"""Offline determiner-selection candidates for Chapter 5.

The checks are candidate-only and production-disabled. They use a deliberately
small countability lexicon and do not claim to classify every English noun.
"""
from __future__ import annotations

import re
from typing import Any

if __package__:
    from .parse_engine import _ordered_leaves
else:
    from parse_engine import _ordered_leaves


COUNT_SINGULAR = {
    "technician", "administrator", "assistant", "engineer", "bicycle", "chair",
    "volunteer", "mechanic", "route", "parcel", "lamp", "bolt", "pumpkin",
    "cyclist", "wall", "week", "bulb", "student", "teacher", "doctor", "nurse",
    "driver", "worker", "manager", "visitor", "officer", "clerk", "builder",
    "farmer", "singer", "player", "writer", "reader", "speaker", "helper",
}
MASS = {
    "furniture", "equipment", "information", "advice", "luggage", "baggage",
    "news", "money", "water", "milk", "grit", "repetition", "condensation",
    "stationery", "homework", "research", "traffic", "weather", "bread",
    "cheese", "rice", "sand", "salt", "sugar", "coffee", "tea", "music",
    "art", "work", "evidence", "knowledge", "progress", "software",
    "hardware", "clothing", "machinery", "scenery", "electricity", "air",
    "oxygen", "paper", "glass", "wood", "metal", "cotton", "wool",
}
COUNTABLE_SHIFTS = {
    "chocolate", "discipline", "cheese", "coffee", "tea", "paper", "glass",
    "business", "difficulty", "experience", "language", "light", "room",
}
NON_PLURAL_S = {
    "gas", "series", "species", "news", "chaos", "analysis", "basis",
    "crisis", "thesis", "bus", "class", "glass", "process", "access",
    "success", "business", "status", "corpus", "campus",
}
IRREGULAR_PLURAL = {"people", "children", "men", "women", "feet", "teeth",
                    "mice", "geese"}
def _result() -> dict[str, Any]:
    return {"status": "not_evaluated", "production_enabled": False,
            "candidates": [], "blocked": []}


def _edit(span: list[int], replacement: str) -> dict[str, Any]:
    return {"char_span": list(span), "replacement": replacement,
            "requires_reparse": True, "safe_to_apply_automatically": False}


def _candidate(rule_id: str, pages: list[int], kind: str, span: list[int],
               replacement: str | None, **relation: Any) -> dict[str, Any]:
    edit = _edit(span, replacement) if replacement is not None else None
    return {"rule_id": rule_id, "source_chapter": 5, "source_pages": pages,
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


def _is_plural(word: str) -> bool:
    lower = word.casefold()
    if lower in IRREGULAR_PLURAL:
        return True
    if lower in NON_PLURAL_S or lower in MASS:
        return False
    return lower.endswith("s") and not lower.endswith(("ss", "us", "is"))


def _singularize(word: str) -> str:
    lower = word.casefold()
    if lower == "people":
        return "person"
    if lower == "children":
        return "child"
    if lower == "men":
        return "man"
    if lower == "women":
        return "woman"
    if lower == "feet":
        return "foot"
    if lower == "teeth":
        return "tooth"
    if lower == "mice":
        return "mouse"
    if lower == "geese":
        return "goose"
    if lower.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if lower.endswith(("ches", "shes", "xes", "zes", "ses")):
        return word[:-2]
    if lower.endswith("s"):
        return word[:-1]
    return word


def _pluralize(word: str) -> str:
    lower = word.casefold()
    if lower.endswith(("s", "x", "z", "ch", "sh")):
        return word + "es"
    if re.search(r"[^aeiou]y$", lower):
        return word[:-1] + "ies"
    return word + "s"


def _article_for(word: str) -> str:
    return "an" if word[:1].casefold() in "aeiou" else "a"


def _case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


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



def _pos_at(sentence: str, tree: dict[str, Any] | None, char_index: int) -> str | None:
    if tree is None:
        return None
    aligned = _align(sentence, tree)
    if aligned is None:
        return None
    leaves, spans = aligned
    for leaf, span in zip(leaves, spans):
        if span[0] <= char_index < span[1]:
            return leaf.get("pos")
    return None


def probe_bare_singular_subject(sentence: str, tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None or tree.get("type") != "S":
        return []
    leaves, spans = aligned
    children = tree.get("children", [])
    if len(children) < 2 or children[0].get("type") != "NP":
        return []
    subject = children[0]
    subject_leaves = list(_ordered_leaves(subject))
    if any(leaf.get("pos") in {"DT", "PRP", "PRP$", "NNP", "NNPS", "NNS", "CD"}
           for leaf in subject_leaves):
        return []
    head = next((leaf for leaf in reversed(subject_leaves)
                 if leaf.get("pos") == "NN"), None)
    if head is None or _leaf_lower(head) not in COUNT_SINGULAR:
        return []
    start = spans[subject["span"][0]][0]
    return [_candidate(
        "PHR-028", [329], "bare_singular_count_subject",
        [start, start], "The ",
        subject_char_span=[start, spans[subject["span"][1] - 1][1]],
    )]


def probe_much_count(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\bmuch\s+([A-Za-z]+)\b", sentence, re.IGNORECASE):
        noun = match.group(1)
        if noun.casefold() not in COUNT_SINGULAR:
            continue
        article = _article_for(noun)
        rows.append(_candidate(
            "PHR-043", [339], "much_with_count_singular",
            [match.start(), match.start() + 4], _case(match.group(0), article),
            noun=noun,
        ))
    return rows


def probe_each_mass(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\b(each|every)\s+([A-Za-z]+)\b", sentence, re.IGNORECASE):
        noun = match.group(2)
        lower = noun.casefold()
        if lower not in MASS or lower in COUNTABLE_SHIFTS:
            continue
        insertion = match.start(2)
        rows.append(_candidate(
            "PHR-044", [339], "distributive_with_mass_nominal",
            [insertion, insertion], "piece of ",
            noun=noun,
        ))
    return rows


def probe_deal_plural(sentence: str, tree: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(r"\b(a (?:great|good) deal of)\s+([A-Za-z]+)\b", re.IGNORECASE)
    for match in pattern.finditer(sentence):
        noun = match.group(2)
        if not _is_plural(noun) or noun.casefold() in MASS:
            continue
        if tree is not None and _pos_at(sentence, tree, match.start(2)) not in {"NN", "NNS", "NNP", "NNPS"}:
            continue
        rows.append(_candidate(
            "PHR-080", [349, 350], "plural_complement_with_quantificational_deal",
            [match.start(2), match.end(2)], None,
            complement=noun,
        ))
    return rows


def probe_approximate_number_mass(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b(dozens|hundreds|thousands|millions)\s+of\s+([A-Za-z]+)(?:\s+([A-Za-z]+))?",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        noun = match.group(2)
        following = match.group(3)
        if noun.casefold() not in MASS or noun.casefold() in COUNTABLE_SHIFTS:
            continue
        if following and _is_plural(following):
            continue
        rows.append(_candidate(
            "PHR-084", [351], "mass_complement_after_plural_approximate_number",
            [match.start(2), match.end(2)], None,
            complement=noun, following=following,
        ))
    return rows


def probe_cardinal_number(sentence: str, tree: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\bone\s+([A-Za-z]+)\b", sentence, re.IGNORECASE):
        noun = match.group(1)
        if not _is_plural(noun):
            continue
        if noun.casefold() in MASS:
            continue
        if tree is not None and _pos_at(sentence, tree, match.start(1)) not in {"NN", "NNS", "NNP", "NNPS"}:
            continue
        rows.append(_candidate(
            "PHR-088", [352, 353], "singular_cardinal_with_plural_head",
            [match.start(1), match.end(1)], _case(noun, _singularize(noun)),
            numeral="one",
        ))
    for match in re.finditer(r"\bone and a half\s+([A-Za-z]+)\b", sentence, re.IGNORECASE):
        noun = match.group(1)
        if _is_plural(noun) or noun.casefold() in MASS:
            continue
        rows.append(_candidate(
            "PHR-088", [352, 353], "noninteger_cardinal_with_singular_head",
            [match.start(1), match.end(1)], _case(noun, _pluralize(noun)),
            numeral="one and a half",
        ))
    return rows


def probe_the_fused_head(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pronoun = re.compile(r"\bthe\s+(you|I|we|they|he|she|it)\s+([A-Za-z]+ed)\b",
                         re.IGNORECASE)
    for match in pronoun.finditer(sentence):
        rows.append(_candidate(
            "PHR-126", [371], "the_as_fused_determiner_head",
            [match.start(), match.start() + 3], "the one",
            following=match.group(2),
        ))
    for match in re.finditer(r"\bthe\s+(from|of|in|on|at|to)\b", sentence, re.IGNORECASE):
        rows.append(_candidate(
            "PHR-126", [371], "the_as_fused_determiner_head",
            [match.start(), match.start() + 3], "that",
            following=match.group(1),
        ))
    return rows


def probe_initial_a_numeral(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b(these|those|this|that)\s+(a)\s+(hundred|thousand|million|billion|dozen)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "PHR-128", [372, 373], "initial_a_after_determiner",
            [match.start(2), match.end(2) + 1], "",
            numeral=match.group(3),
        ))
    return rows


def probe_all_indefinite(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(r"\ball\s+a\s+([A-Za-z]+)\b", re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "PHR-133", [375], "all_before_indefinite_article",
            [match.start(), match.end() - len(match.group(1)) - 1], "a whole",
            noun=match.group(1),
        ))
    return rows


def probe_every_of(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\b(Every)\s+of\b", sentence):
        rows.append(_candidate(
            "PHR-140", [379], "every_as_fused_head",
            [match.start(1), match.end(1)], "Each",
        ))
    return rows


def probe_either_plural(sentence: str, tree: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\beither\s+([A-Za-z]+)\b", sentence, re.IGNORECASE):
        noun = match.group(1)
        if not _is_plural(noun) or noun.casefold() in MASS:
            continue
        if tree is not None and _pos_at(sentence, tree, match.start(1)) not in {"NN", "NNS", "NNP", "NNPS"}:
            continue
        rows.append(_candidate(
            "PHR-157", [387, 388], "either_with_plural_head",
            [match.start(1), match.end(1)], _case(noun, _singularize(noun)),
        ))
    return rows


def probe_no_none(sentence: str, tree: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\b(No)\s+of\b", sentence):
        rows.append(_candidate(
            "PHR-161", [390], "no_used_as_fused_head",
            [match.start(1), match.end(1)], "None",
        ))
    for match in re.finditer(r"\b(None)\s+([A-Za-z]+)\b", sentence, re.IGNORECASE):
        noun = match.group(2)
        if noun.casefold() in {"other", "the"} or not _is_plural(noun):
            continue
        if tree is not None and _pos_at(sentence, tree, match.start(2)) not in {"NN", "NNS", "NNP", "NNPS"}:
            continue
        rows.append(_candidate(
            "PHR-161", [390], "none_used_before_nominal",
            [match.start(1), match.end(1)], "No",
            noun=noun,
        ))
    return rows


def probe_determiner(sentence: str, tree: dict[str, Any] | None = None, *,
                     variety: str = "standard_english") -> dict[str, Any]:
    result = _result()
    if variety != "standard_english":
        return result
    result["status"] = "candidate_only"
    for checker in (
        probe_much_count,
        probe_each_mass,
        probe_approximate_number_mass,
        probe_the_fused_head,
        probe_initial_a_numeral,
        probe_all_indefinite,
        probe_every_of,
    ):
        result["candidates"].extend(checker(sentence))
    for checker in (probe_deal_plural, probe_cardinal_number,
                    probe_either_plural, probe_no_none):
        result["candidates"].extend(checker(sentence, tree))
    if tree is None:
        result["blocked"].append("tree_relations_unavailable")
        return result
    result["candidates"].extend(probe_bare_singular_subject(sentence, tree))
    return result
