"""Offline verb-form candidates for selected Chapter 3, 4 and 6 rules.

The checks are candidate-only and production-disabled. Parser-grounded checks
use the canonical tree only for the narrow constructions named by each spec.
"""
from __future__ import annotations

import re
from typing import Any

if __package__:
    from .parse_engine import _ordered_leaves
else:
    from parse_engine import _ordered_leaves


PAST_TO_PRETERITE = {
    "broken": "broke", "chosen": "chose", "spoken": "spoke", "taken": "took",
    "given": "gave", "written": "wrote", "driven": "drove", "eaten": "ate",
    "fallen": "fell", "forgotten": "forgot", "gotten": "got", "known": "knew",
    "seen": "saw", "done": "did", "gone": "went", "begun": "began",
    "drunk": "drank", "sung": "sang", "swum": "swam", "thrown": "threw",
    "flown": "flew", "grown": "grew", "shown": "showed", "torn": "tore",
    "worn": "wore", "ridden": "rode", "risen": "rose", "stolen": "stole",
}
GERUND_TO_BASE = {
    "sticking": "stick", "arriving": "arrive", "making": "make",
    "taking": "take", "coming": "come", "writing": "write", "running": "run",
    "sitting": "sit", "getting": "get", "putting": "put", "beginning": "begin",
    "happening": "happen", "trying": "try", "studying": "study",
    "carrying": "carry", "playing": "play", "working": "work",
    "living": "live", "giving": "give", "moving": "move",
    "choosing": "choose", "watering": "water", "reading": "read",
    "speaking": "speak", "repairing": "repair", "rewriting": "rewrite",
}
BASE_TO_GERUND = {
    "work": "working", "take": "taking", "leave": "leaving",
    "arrive": "arriving", "stick": "sticking", "open": "opening",
    "repair": "repairing", "rewrite": "rewriting", "water": "watering",
    "read": "reading", "make": "making", "come": "coming",
    "write": "writing", "run": "running", "sit": "sitting",
    "get": "getting", "put": "putting", "begin": "beginning",
    "happen": "happening", "try": "trying", "study": "studying",
    "carry": "carrying", "play": "playing", "live": "living",
    "give": "giving", "move": "moving", "choose": "choosing",
}
TIME_NOUNS = {"day", "days", "week", "weeks", "month", "months", "year",
              "years", "morning", "afternoon", "evening", "night", "nights"}


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


def _base_from_gerund(word: str) -> str:
    lower = word.casefold()
    if lower in GERUND_TO_BASE:
        return GERUND_TO_BASE[lower]
    if lower.endswith("ying") and len(word) > 4:
        return word[:-4] + "ie"
    if lower.endswith("ing") and len(word) > 3:
        stem = word[:-3]
        if len(stem) > 2 and stem[-1] == stem[-2] and stem[-1] not in "lsz":
            return stem[:-1]
        return stem
    return word


def _gerund_from_base(word: str) -> str:
    lower = word.casefold()
    if lower in BASE_TO_GERUND:
        return BASE_TO_GERUND[lower]
    if lower.endswith("ie"):
        return word[:-2] + "ying"
    if lower.endswith("e") and not lower.endswith(("ee", "ye", "oe")):
        return word[:-1] + "ing"
    return word + "ing"


def _case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def probe_had_better_to(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(r"\b(had|'d)\s+(better|best)\s+(to)\s+([A-Za-z]+)\b",
                         re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "COMP-042", 3, [113], "to_after_had_better",
            [match.start(3), match.end(3) + 1], "",
            complement=match.group(4),
        ))
    return rows


def probe_tend_gerund(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(r"\b(tend|tends|tended|tending)\s+([A-Za-z]+ing)\b",
                         re.IGNORECASE)
    for match in pattern.finditer(sentence):
        gerund = match.group(2)
        base = _base_from_gerund(gerund)
        replacement = "to " + _case(gerund, base)
        rows.append(_candidate(
            "COMP-061", 4, [220], "gerund_complement_of_tend",
            [match.start(2), match.end(2)], replacement,
            verb=match.group(1),
        ))
    return rows


def probe_do_pseudocleft(sentence: str) -> list[dict[str, Any]]:
    rows = []
    first = re.compile(r"\bWhat\s+(?:the\s+)?([A-Za-z]+)\s+did\s+was\s+([A-Za-z]+ing)\b",
                       re.IGNORECASE)
    for match in first.finditer(sentence):
        gerund = match.group(2)
        rows.append(_candidate(
            "COMP-116", 4, [270], "progressive_value_after_nonprogressive_do",
            [match.start(2), match.end(2)], _case(gerund, _base_from_gerund(gerund)),
            subject=match.group(1),
        ))
    second = re.compile(r"\bWhat\s+(?:the\s+)?([A-Za-z]+)\s+was\s+doing\s+was\s+([A-Za-z]+)\b",
                        re.IGNORECASE)
    for match in second.finditer(sentence):
        base = match.group(2)
        if base.casefold().endswith(("ing", "ed")):
            continue
        rows.append(_candidate(
            "COMP-116", 4, [270], "nonprogressive_value_after_progressive_do",
            [match.start(2), match.end(2)], _case(base, _gerund_from_base(base)),
            subject=match.group(1),
        ))
    return rows


def probe_inchoative(sentence: str, tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None or tree.get("type") != "S":
        return []
    leaves, spans = aligned
    children = tree.get("children", [])
    if len(children) < 2 or children[1].get("type") != "VP":
        return []
    predicate = children[1]
    first = _first_leaf(predicate)
    if first is None or _leaf_lower(first) not in {"destroyed", "constructed"}:
        return []
    for child in predicate.get("children", []):
        if child.get("type") != "NP":
            continue
        head = next((leaf for leaf in reversed(list(_ordered_leaves(child)))
                     if leaf.get("pos", "").startswith("NN")), None)
        if head is not None and _leaf_lower(head) not in TIME_NOUNS:
            return []
    span = [spans[predicate["span"][0]][0], spans[predicate["span"][1] - 1][1]]
    return [_candidate(
        "COMP-194", 4, [306], "bare_inchoative_with_causative_verb",
        span, None,
        subject_char_span=[spans[children[0]["span"][0]][0],
                           spans[children[0]["span"][1] - 1][1]],
    )]


def probe_bare_participle(sentence: str, tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None or tree.get("type") != "S":
        return []
    leaves, spans = aligned
    children = tree.get("children", [])
    if len(children) < 2 or children[1].get("type") != "VP":
        return []
    predicate = children[1]
    first = _first_leaf(predicate)
    if first is None:
        return []
    surface = _leaf_lower(first)
    if surface not in PAST_TO_PRETERITE:
        return []
    span = spans[first["span"][0]]
    return [_candidate(
        "MORPH-025", 3, [76, 77], "bare_past_participle_as_finite_verb",
        span, _case(first.get("surface", ""), PAST_TO_PRETERITE[surface]),
        subject_char_span=[spans[children[0]["span"][0]][0],
                           spans[children[0]["span"][1] - 1][1]],
    )]


def probe_degree_participle(sentence: str, tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None:
        return []
    leaves, spans = aligned
    rows = []
    for node in _walk(tree):
        if node.get("type") != "VP":
            continue
        children = node.get("children", [])
        for index in range(1, len(children)):
            adverb = children[index - 1]
            following = children[index]
            if adverb.get("type") != "ADVP" or following.get("type") != "VP":
                continue
            degree = _leaf_lower(_first_leaf(adverb))
            if degree not in {"very", "too"}:
                continue
            first = _first_leaf(following)
            if first is None:
                continue
            if degree == "very" and first.get("pos") == "VBG":
                if not any(child.get("type") == "NP" for child in following.get("children", [])):
                    continue
                span = [spans[adverb["span"][0]][0], spans[adverb["span"][1] - 1][1]]
                rows.append(_candidate(
                    "MORPH-035", 3, [79, 81], "degree_adverb_with_verbal_participle",
                    span, "carefully",
                    participle=first.get("surface"),
                ))
            if degree == "too" and first.get("pos") == "VBN":
                if not any(child.get("type") == "PP" and _leaf_lower(_first_leaf(child)) == "by"
                           for child in following.get("children", [])):
                    continue
                start = spans[adverb["span"][0]][0]
                end = spans[first["span"][0]][1]
                rows.append(_candidate(
                    "MORPH-035", 3, [79, 81], "degree_adverb_with_verbal_participle",
                    [start, end], first.get("surface", "") + " thoroughly",
                    participle=first.get("surface"),
                ))
    return rows


def probe_accustomed_to(sentence: str, tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None or "accustomed" not in sentence.casefold():
        return []
    leaves, spans = aligned
    rows = []
    for node in _walk(tree):
        if node.get("type") != "PP":
            continue
        children = node.get("children", [])
        if len(children) < 2 or _leaf_lower(_first_leaf(node)) != "to":
            continue
        complement = children[1]
        if complement.get("type") != "S":
            continue
        predicate = next((child for child in complement.get("children", [])
                          if child.get("type") == "VP"), None)
        if predicate is None:
            continue
        first = _first_leaf(predicate)
        if first is None or first.get("pos") != "VB":
            continue
        span = spans[first["span"][0]]
        rows.append(_candidate(
            "WCAT-059", 6, [545], "base_verb_after_prepositional_to",
            span, _case(first.get("surface", ""), _gerund_from_base(first.get("surface", ""))),
            adjective="accustomed",
        ))
    if not rows:
        for match in re.finditer(r"\baccustomed\s+to\s+([A-Za-z]+)\b", sentence, re.IGNORECASE):
            word = match.group(1)
            if word.casefold() not in BASE_TO_GERUND:
                continue
            after = sentence[match.end():].lstrip()
            if re.match(r"(that|which|who|whose|whom)\b", after, re.IGNORECASE):
                continue
            span = [match.start(1), match.end(1)]
            rows.append(_candidate(
                "WCAT-059", 6, [545], "base_verb_after_prepositional_to",
                span, _case(word, _gerund_from_base(word)),
                adjective="accustomed",
            ))
    return rows


def probe_verb_form(sentence: str, tree: dict[str, Any] | None = None, *,
                    variety: str = "standard_english") -> dict[str, Any]:
    result = _result()
    if variety != "standard_english":
        return result
    result["status"] = "candidate_only"
    for checker in (probe_had_better_to, probe_tend_gerund, probe_do_pseudocleft):
        result["candidates"].extend(checker(sentence))
    if tree is None:
        result["blocked"].append("tree_relations_unavailable")
        return result
    for checker in (probe_inchoative, probe_bare_participle,
                    probe_degree_participle, probe_accustomed_to):
        result["candidates"].extend(checker(sentence, tree))
    return result
