"""Offline usage candidates for a mixed Phase C surface batch.

The checks are candidate-only and production-disabled. Each function is scoped
to the diagnostic construction and does not certify the reading of the sentence.
"""
from __future__ import annotations

import re
from typing import Any

if __package__:
    from .parse_engine import _ordered_leaves
else:
    from parse_engine import _ordered_leaves


MASS = {
    "equipment", "furniture", "information", "advice", "luggage", "baggage",
    "news", "money", "water", "milk", "flour", "grit", "repetition",
    "condensation", "stationery", "homework", "research", "traffic", "weather",
    "bread", "cheese", "rice", "sand", "salt", "sugar", "coffee", "tea",
    "music", "art", "work", "evidence", "knowledge", "progress", "software",
    "hardware", "clothing", "machinery", "scenery", "electricity", "air",
    "oxygen",
}
PERSON_NOUNS = {
    "cousin", "cousins", "curator", "curators", "teacher", "teachers",
    "student", "students", "artist", "artists", "manager", "managers",
    "doctor", "doctors", "nurse", "nurses", "driver", "drivers", "worker",
    "workers", "visitor", "visitors", "officer", "officers", "clerk", "clerks",
    "builder", "builders", "farmer", "farmers", "singer", "singers",
    "player", "players", "writer", "writers", "reader", "readers",
    "speaker", "speakers", "helper", "helpers", "technician", "technicians",
    "administrator", "administrators", "assistant", "assistants", "engineer",
    "engineers", "mechanic", "mechanics", "cyclist", "cyclists", "volunteer",
    "volunteers", "person", "people", "woman", "women", "man", "men",
    "child", "children", "reviewer", "reviewers",
}
TENS_TO_THOUSAND = {
    "ten": "one", "twenty": "two", "thirty": "three", "forty": "four",
    "fifty": "five", "sixty": "six", "seventy": "seven", "eighty": "eight",
    "ninety": "nine",
}
CONTRACTIONS = {
    "i'm": "I am", "you're": "you are", "he's": "he is", "she's": "she is",
    "it's": "it is", "we're": "we are", "they're": "they are",
}


def _result() -> dict[str, Any]:
    return {"status": "not_evaluated", "production_enabled": False,
            "candidates": [], "blocked": []}


def _edit(span: list[int], replacement: str) -> dict[str, Any]:
    return {"char_span": list(span), "replacement": replacement,
            "requires_reparse": True, "safe_to_apply_automatically": False}


def _candidate(rule_id: str, chapter: int, pages: list[int], kind: str,
               span: list[int], replacement: str | None,
               **relation: Any) -> dict[str, Any]:
    edit = _edit(span, replacement) if replacement is not None else None
    return {"rule_id": rule_id, "source_chapter": chapter, "source_pages": pages,
            "relation": {"kind": kind, "mark_char_span": list(span), **relation},
            "edit_hint": edit}


def _walk(node: dict[str, Any]):
    yield node
    for child in node.get("children", []):
        yield from _walk(child)


def _first_leaf(node: dict[str, Any]) -> dict[str, Any] | None:
    for leaf in _ordered_leaves(node):
        return leaf
    return None


def _leaf_lower(leaf: dict[str, Any] | None) -> str:
    return (leaf or {}).get("surface", "").casefold()


def _align(sentence: str, tree: dict[str, Any]):
    leaves = list(_ordered_leaves(tree))
    spans: list[list[int]] = []
    cursor = 0
    for leaf in leaves:
        while cursor < len(sentence) and sentence[cursor].isspace():
            cursor += 1
        expected = leaf.get("surface", "")
        if not expected:
            return None
        if sentence.startswith(expected, cursor):
            spans.append([cursor, cursor + len(expected)])
            cursor += len(expected)
            continue
        if expected in {"'", "’"} and cursor < len(sentence) and sentence[cursor] in {"'", "’"}:
            spans.append([cursor, cursor + 1])
            cursor += 1
            continue
        return None
    if sentence[cursor:].strip():
        return None
    return leaves, spans


def _case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def _singularize(word: str) -> str:
    lower = word.casefold()
    if lower.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if lower.endswith(("ches", "shes", "xes", "zes", "ses")):
        return word[:-2]
    if lower.endswith("s"):
        return word[:-1]
    return word


def probe_of_approximate(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(r"\b(dozens|hundreds|thousands|millions)\s+([A-Za-z]+s)\b",
                         re.IGNORECASE)
    for match in pattern.finditer(sentence):
        noun = match.group(2)
        insertion = match.start(2)
        rows.append(_candidate(
            "PHR-083", 5, [351], "missing_of_after_plural_approximate_number",
            [insertion, insertion], "of ",
            complement=noun,
        ))
    return rows


def probe_both_coordination(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\bboth\s+([A-Za-z]+),\s*([A-Za-z]+),\s*(?:and\s+)?([A-Za-z]+)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "PHR-110", 5, [361], "both_with_more_than_two_coordinates",
            [match.start(), match.end()], None,
            coordinates=[match.group(1), match.group(2), match.group(3)],
        ))
    return rows


def probe_more_than_one(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for pattern, kind in (
        (re.compile(r"\bmore than one\s+([A-Za-z]+s)\b", re.IGNORECASE), "more_than_one"),
        (re.compile(r"\bone more\s+([A-Za-z]+s)\b", re.IGNORECASE), "one_more"),
    ):
        for match in pattern.finditer(sentence):
            noun = match.group(1)
            rows.append(_candidate(
                "PHR-240", 5, [432], "plural_head_with_singular_selector",
                [match.start(1), match.end(1)], _case(noun, _singularize(noun)),
                selector=kind,
            ))
    return rows


def probe_coordinated_contraction(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\band\s+(I'm|you're|he's|she's|it's|we're|they're)\b", re.IGNORECASE)
    for match in pattern.finditer(sentence):
        contraction = match.group(1)
        expanded = CONTRACTIONS.get(contraction.casefold())
        if expanded is None:
            continue
        rows.append(_candidate(
            "OTH-615", 1, [9, 10], "contraction_on_final_coordinate_subject",
            [match.start(1), match.end(1)], expanded,
            contraction=contraction,
        ))
    return rows


def probe_have_got_do(sentence: str) -> list[dict[str, Any]]:
    rows = []
    question = re.compile(r"\b(Do|Does|Did)\s+(I|you|he|she|it|we|they)\s+have got\b",
                          re.IGNORECASE)
    for match in question.finditer(sentence):
        auxiliary = {"do": "Have", "does": "Has", "did": "Had"}[match.group(1).casefold()]
        rows.append(_candidate(
            "COMP-041", 3, [112], "supportive_do_with_have_got",
            [match.start(), match.end()], f"{auxiliary} {match.group(2)} got",
            subject=match.group(2),
        ))
    negative = re.compile(
        r"\b(I|you|he|she|it|we|they)\s+(don't|doesn't|didn't)\s+have got\b",
        re.IGNORECASE)
    for match in negative.finditer(sentence):
        subject = match.group(1)
        contraction = {"don't": "haven't", "doesn't": "hasn't", "didn't": "hadn't"}[
            match.group(2).casefold()]
        rows.append(_candidate(
            "COMP-041", 3, [112], "supportive_do_with_have_got",
            [match.start(), match.end()], f"{subject} {contraction} got",
            subject=subject,
        ))
    return rows


def probe_sung_sang(sentence: str) -> list[dict[str, Any]]:
    rows = []
    preterite = re.compile(
        r"\b(I|you|he|she|we|they|[A-Z][a-z]+)\s+sung\b")
    for match in preterite.finditer(sentence):
        start = match.start(0) + len(match.group(1)) + 1
        rows.append(_candidate(
            "MORPH-114", 18, [1603], "participle_used_as_preterite",
            [start, match.end()], "sang",
            subject=match.group(1),
        ))
    perfect = re.compile(r"\b(has|have|had)\s+sang\b", re.IGNORECASE)
    for match in perfect.finditer(sentence):
        start = match.start(0) + len(match.group(1)) + 1
        rows.append(_candidate(
            "MORPH-114", 18, [1603], "preterite_used_as_participle",
            [start, match.end()], "sung",
            auxiliary=match.group(1),
        ))
    return rows


def probe_i_arent(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\bI\s+aren['’]t\b", sentence):
        rows.append(_candidate(
            "MORPH-130", 18, [1612], "first_person_negative_am_contraction",
            [match.start(), match.end()], "I am not",
        ))
    return rows


def probe_new_zealand_predicate(sentence: str, tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None or tree.get("type") != "S":
        return []
    leaves, spans = aligned
    children = tree.get("children", [])
    if len(children) < 3 or children[0].get("type") != "NP" or children[1].get("type") != "VP":
        return []
    subject = children[0]
    subject_leaves = list(_ordered_leaves(subject))
    subject_words = {_leaf_lower(leaf) for leaf in subject_leaves}
    if not subject_words & PERSON_NOUNS:
        return []
    predicate = children[1]
    predicate_leaves = list(_ordered_leaves(predicate))
    if not predicate_leaves or _leaf_lower(predicate_leaves[0]) not in {"is", "are", "was", "were"}:
        return []
    if any(_leaf_lower(leaf) == "from" for leaf in predicate_leaves):
        return []
    complement = next((child for child in predicate.get("children", [])
                       if child.get("type") == "NP"), None)
    if complement is None:
        return []
    text = " ".join(leaf.get("surface", "") for leaf in _ordered_leaves(complement))
    if text.casefold() != "new zealand":
        return []
    plural = _leaf_lower(predicate_leaves[0]) in {"are", "were"}
    replacement = "New Zealanders" if plural else "from New Zealand"
    span = [spans[complement["span"][0]][0], spans[complement["span"][1] - 1][1]]
    return [_candidate(
        "MORPH-391", 19, [1696], "place_name_as_nationality_predicate",
        span, replacement,
        subject_char_span=[spans[subject["span"][0]][0],
                           spans[subject["span"][1] - 1][1]],
    )]


def probe_ten_hundred(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b(ten|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)\s+hundred\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        replacement = f"{TENS_TO_THOUSAND[match.group(1).casefold()]} thousand"
        rows.append(_candidate(
            "MORPH-480", 19, [1717, 1718], "ten_multiplier_of_hundred",
            [match.start(), match.end()], _case(match.group(0), replacement),
        ))
    return rows


def probe_a_in_composite_numeral(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
        r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
        r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)\s+"
        r"(thousand|million|billion)\s+(a)\s+hundred\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "MORPH-481", 19, [1718], "a_after_earlier_numeral",
            [match.start(3), match.end(3)], "one",
        ))
    return rows


def probe_used_to_ellipsis(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\bused to\b[^.;!?]*\band\s+([A-Za-z]+)\s+used\s+(too|as well)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        ending = match.group(2).casefold()
        replacement = "did too" if ending == "too" else "used to as well"
        start = match.start(0) + match.group(0).casefold().rfind("used")
        rows.append(_candidate(
            "CLS-120", 3, [115], "stranded_aspectual_used",
            [start, match.end()], replacement,
            subject=match.group(1),
        ))
    return rows


def probe_fewer_mass(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\bfewer\s+([A-Za-z]+)\b", sentence, re.IGNORECASE):
        noun = match.group(1)
        if noun.casefold() not in MASS:
            continue
        rows.append(_candidate(
            "CLS-1159", 13, [1127], "fewer_with_mass_nominal",
            [match.start(), match.start() + 5], _case(match.group(0), "less"),
            noun=noun,
        ))
    return rows


def probe_a_same(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\b(a)\s+(same)\b", sentence, re.IGNORECASE):
        rows.append(_candidate(
            "CLS-1188", 13, [1138], "indefinite_article_with_attributive_same",
            [match.start(), match.end()], _case(match.group(0), "the same"),
        ))
    return rows


def probe_as_like(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(
            r"\b(is|are|was|were)\s+(as)\s+(her|his|my|your|our|their|its)\b",
            sentence, re.IGNORECASE):
        rows.append(_candidate(
            "CLS-1239", 13, [1154], "as_for_resemblance",
            [match.start(2), match.end(2)], _case(match.group(2), "like"),
        ))
    initial = re.compile(r"^As\s+([A-Z][a-z]+)\s*,", re.IGNORECASE)
    match = initial.match(sentence)
    if match:
        rows.append(_candidate(
            "CLS-1239", 13, [1154], "as_for_resemblance",
            [match.start(), match.start() + 2], "Like",
            name=match.group(1),
        ))
    return rows


def probe_cleft_it_be(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b([Cc]onsider|[Bb]elieve)\s+it\s+((?:the\s+[a-z][A-Za-z'-]*)|(?:[A-Z][a-z]+))"
        r"\s+(who|that)\b")
    for match in pattern.finditer(sentence):
        insertion = match.start(2)
        rows.append(_candidate(
            "CLS-1415", 16, [1419], "raised_cleft_it_without_be",
            [insertion, insertion], "to be ",
            cleft_head=match.group(2),
        ))
    return rows


def probe_bare_who_pseudocleft(sentence: str) -> list[dict[str, Any]]:
    match = re.match(r"^Who\s+[A-Za-z]+\s+[^.;!?]*\b(was|were)\b", sentence)
    if not match:
        return []
    return [_candidate(
        "CLS-1425", 16, [1422, 1423], "bare_who_fused_relative_head",
        [0, 4], "The one who ",
        main_verb=match.group(1),
    )]


def probe_particle_pronoun(sentence: str) -> list[dict[str, Any]]:
    rows = []
    verbs = (r"(?:brought|bring|picked|pick|put|took|take|gave|give|sent|send|"
             r"handed|hand|threw|throw|turned|turn|shut|wrote|write|filled|fill|"
             r"checked|check|called|call|showed|show|taught|teach|told|tell|"
             r"left|leave|paid|pay|read|sold|sell)")
    pattern = re.compile(
        rf"\b({verbs})\s+(back|away|up|down|out|in|off|over|through)\s+"
        r"(them|him|her|it|me|us|you)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        replacement = f"{match.group(1)} {match.group(3)} {match.group(2)}"
        rows.append(_candidate(
            "CLS-1325", 16, [1383], "weak_pronoun_after_particle",
            [match.start(), match.end()], _case(match.group(0), replacement),
            particle=match.group(2), pronoun=match.group(3),
        ))
    return rows


def probe_usage(sentence: str, tree: dict[str, Any] | None = None, *,
                variety: str = "standard_english") -> dict[str, Any]:
    result = _result()
    if variety != "standard_english":
        return result
    result["status"] = "candidate_only"
    for checker in (
        probe_of_approximate,
        probe_both_coordination,
        probe_more_than_one,
        probe_coordinated_contraction,
        probe_have_got_do,
        probe_sung_sang,
        probe_i_arent,
        probe_ten_hundred,
        probe_a_in_composite_numeral,
        probe_used_to_ellipsis,
        probe_fewer_mass,
        probe_a_same,
        probe_as_like,
        probe_cleft_it_be,
        probe_bare_who_pseudocleft,
        probe_particle_pronoun,
    ):
        result["candidates"].extend(checker(sentence))
    if tree is None:
        result["blocked"].append("tree_relations_unavailable")
        return result
    result["candidates"].extend(probe_new_zealand_predicate(sentence, tree))
    return result
