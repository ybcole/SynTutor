"""Offline pro-form and ellipsis candidates for Chapter 17 and related rules.

The checks are candidate-only and production-disabled. Each pattern is scoped
to the diagnostic pair and does not replace a full antecedent analysis.
"""
from __future__ import annotations

import re
from typing import Any


MASS = {
    "equipment", "furniture", "information", "advice", "luggage", "baggage",
    "news", "money", "water", "milk", "flour", "grit", "repetition",
    "condensation", "stationery", "homework", "research", "traffic", "weather",
    "bread", "cheese", "rice", "sand", "salt", "sugar", "coffee", "tea",
    "music", "art", "work", "evidence", "knowledge", "progress", "software",
    "hardware", "clothing", "machinery", "scenery", "electricity", "air",
    "oxygen",
}
SIZE_COLOR = {
    "blue", "red", "green", "black", "white", "brown", "grey", "gray",
    "yellow", "orange", "pink", "purple", "small", "large", "big", "tiny",
    "young", "old", "new", "long", "short", "wide", "narrow", "thick", "thin",
}
NEGATED_AUX = {
    "can't": "can", "won't": "will", "doesn't": "does", "didn't": "did",
    "isn't": "is", "aren't": "are", "wasn't": "was", "weren't": "were",
    "hasn't": "has", "haven't": "have", "hadn't": "had", "don't": "do",
}
PROFORM_VERBS = {"stock", "have", "had", "need", "want", "buy", "sell",
                 "find", "make", "take", "get"}


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


def _case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def probe_fused_that(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\b(this|these)\s+of\b", sentence, re.IGNORECASE):
        replacement = "that" if match.group(1).casefold() == "this" else "those"
        rows.append(_candidate(
            "PHR-629", 17, [1508], "proximal_demonstrative_as_fused_head",
            [match.start(1), match.end(1)], _case(match.group(1), replacement),
        ))
    return rows


def probe_mass_one(sentence: str) -> list[dict[str, Any]]:
    lower = sentence.casefold()
    if not any(re.search(rf"\b{re.escape(noun)}\b", lower) for noun in MASS):
        return []
    rows = []
    pattern = re.compile(
        r"\bthe one\b(?=\s+(?:in|from|of|on|at|with|beside|near)\b|\s*[.,;!?]|$)",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "PHR-632", 17, [1508, 1509], "pro_one_for_mass_antecedent",
            [match.start(), match.end()], _case(match.group(0), "that"),
        ))
    return rows


def probe_bare_ones(sentence: str) -> list[dict[str, Any]]:
    rows = []
    cardinals = (r"(?:\d+|two|three|four|five|six|seven|eight|nine|ten|"
                 r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
                 r"seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|"
                 r"sixty|seventy|eighty|ninety)")
    for match in re.finditer(rf"\b({cardinals})\s+(ones)\b", sentence, re.IGNORECASE):
        rows.append(_candidate(
            "PHR-644", 17, [1512], "cardinal_before_bare_ones",
            [match.start(), match.end()], _case(match.group(0), match.group(1)),
            cardinal=match.group(1),
        ))
    for match in re.finditer(r"\bno\s+(ones)\b", sentence, re.IGNORECASE):
        rows.append(_candidate(
            "PHR-644", 17, [1512], "no_before_bare_ones",
            [match.start(), match.end()], _case(match.group(0), "none"),
        ))
    return rows


def probe_every_fused(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b(every)\s+(was|is|were|are|lit|looked|seemed|had|did|does)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "PHR-645", 17, [1512], "every_as_fused_head",
            [match.start(1), match.end(1)], _case(match.group(1), "every one"),
            following=match.group(2),
        ))
    return rows


def probe_bare_ones_object(sentence: str) -> list[dict[str, Any]]:
    rows = []
    verbs = "|".join(sorted(PROFORM_VERBS, key=len, reverse=True))
    pattern = re.compile(
        rf"\b({verbs})\s+(ones)\b(?=\s*(?:[?.,;!?]|too\b|as well\b|$))",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        following = sentence[match.end():].lstrip().casefold()
        replacement = "some" if following.startswith(("too", "as well")) else "them"
        rows.append(_candidate(
            "PHR-654", 17, [1515], "bare_ones_without_dependent",
            [match.start(2), match.end(2)], replacement,
            verb=match.group(1),
        ))
    return rows


def probe_other_order(sentence: str) -> list[dict[str, Any]]:
    rows = []
    adjectives = "|".join(sorted(SIZE_COLOR, key=len, reverse=True))
    pattern = re.compile(rf"\bthe\s+({adjectives})\s+others\b", re.IGNORECASE)
    for match in pattern.finditer(sentence):
        replacement = f"the other {match.group(1)} ones"
        rows.append(_candidate(
            "PHR-666", 17, [1518], "adjective_before_pro_nominal_other",
            [match.start(), match.end()], _case(match.group(0), replacement),
            adjective=match.group(1),
        ))
    return rows


def probe_aux_reduction_do(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b(will|has|have|had|is|are|was|were|can|could|should|would|may|might|must)"
        r"\s+(be|been|[A-Za-z]+ed|[A-Za-z]+ing)\b[^.;!?]{0,80}\band\s+"
        r"([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+does\s+too\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        start = match.end() - len("does too")
        rows.append(_candidate(
            "PHR-684", 17, [1524], "reduction_do_for_auxiliary_headed_vp",
            [start, match.end()], f"{match.group(1)} too",
            auxiliary=match.group(1),
        ))
    return rows


def probe_be_did_so(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\bto be\b[^.;!?]{0,100}\band\s+(?:eventually\s+)?"
        r"(I|you|he|she|we|they|[A-Z][a-z]+)\s+did so\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        subject = match.group(1)
        replacement = "were" if subject.casefold() in {"we", "you", "they"} else "was"
        start = match.end() - len("did so")
        rows.append(_candidate(
            "PHR-704", 17, [1530], "do_so_recovering_predicative_be",
            [start, match.end()], replacement,
            subject=subject,
        ))
    return rows


def probe_do_so_object(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b(did|do|does|doing)\s+so\s+"
        r"((?:the\s+[a-z][A-Za-z'-]*)|(?:[A-Z][a-z]+))\b")
    for match in pattern.finditer(sentence):
        start = match.start(1) + len(match.group(1))
        rows.append(_candidate(
            "PHR-705", 17, [1530], "do_so_with_retained_object",
            [start, match.start(2)], " ",
            object=match.group(2),
        ))
    return rows


def probe_do_so_comparison(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b(than|as)\s+(I|you|he|she|we|they|[A-Z][a-z]+)\s+"
        r"(do|does|did)\s+so\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        before = sentence[:match.start()].rstrip()
        if not before or before.endswith((".", "?", "!")):
            continue
        start = match.end(3)
        rows.append(_candidate(
            "PHR-706", 17, [1530], "do_so_in_comparative_complement",
            [start, match.end()], "",
            comparative=match.group(1),
        ))
    return rows


def probe_additive_so(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\band\s+so\s+(can't|won't|doesn't|didn't|isn't|aren't|wasn't|weren't|"
        r"hasn't|haven't|hadn't|don't)\s+([A-Z][a-z]+)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        auxiliary = NEGATED_AUX[match.group(1).casefold()]
        rows.append(_candidate(
            "PHR-737", 17, [1539], "negative_polarity_with_additive_so",
            [match.start(), match.end()], f"and neither {auxiliary} {match.group(2)}",
            auxiliary=auxiliary,
        ))
    return rows


def probe_proform(sentence: str, *, variety: str = "standard_english") -> dict[str, Any]:
    result = _result()
    if variety != "standard_english":
        return result
    result["status"] = "candidate_only"
    for checker in (
        probe_fused_that,
        probe_mass_one,
        probe_bare_ones,
        probe_every_fused,
        probe_bare_ones_object,
        probe_other_order,
        probe_aux_reduction_do,
        probe_be_did_so,
        probe_do_so_object,
        probe_do_so_comparison,
        probe_additive_so,
    ):
        result["candidates"].extend(checker(sentence))
    return result
