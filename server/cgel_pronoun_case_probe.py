"""Offline pronoun-case candidates for Chapter 5 and Chapter 17.

The checks are candidate-only and production-disabled. Surface patterns are
scoped to the diagnostic pairs and do not replace a full case analysis.
"""
from __future__ import annotations

import re
from typing import Any


ACCUSATIVE = {"he": "him", "she": "her", "they": "them", "we": "us", "i": "me"}
DEPENDENT = {"mine": "my", "yours": "your", "hers": "her", "ours": "our",
             "theirs": "their"}
INDEPENDENT = {"my": "mine", "your": "yours", "her": "hers", "our": "ours",
               "their": "theirs"}
DOUBLE_OBJECT_VERBS = {"sent", "handed", "gave", "offered", "showed", "brought", "told"}
FINITE_VERBS = {
    "opened", "led", "sang", "wrote", "made", "took", "gave", "found",
    "built", "ran", "won", "lost", "left", "came", "went", "spoke",
    "broke", "chose", "drove", "ate", "saw", "knew", "thought", "said",
    "called", "asked", "helped", "met", "paid", "put", "read", "sent",
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


def _case(original: str, replacement: str) -> str:
    if original.isupper():
        return replacement.upper()
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def probe_accusative_object(sentence: str) -> list[dict[str, Any]]:
    rows = []
    verbs = "|".join(sorted({
        "thanked", "handed", "sent", "gave", "showed", "told", "helped",
        "met", "called", "asked", "invited", "saw", "heard", "found",
        "brought", "took", "put", "paid", "offered",
    }, key=len, reverse=True))
    pattern = re.compile(rf"\b({verbs})\s+(he|she|they|we|I)\b", re.IGNORECASE)
    for match in pattern.finditer(sentence):
        pronoun = match.group(2)
        correct = ACCUSATIVE.get(pronoun.casefold())
        if correct is None:
            continue
        rows.append(_candidate(
            "PHR-289", 5, [461], "nominative_pronoun_in_object_position",
            [match.start(2), match.end(2)], _case(pronoun, correct),
            verb=match.group(1),
        ))
    return rows


def probe_for_infinitival(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\b([Ff]or)\s+(he|she|they|we|I)\s+to\b", sentence):
        pronoun = match.group(2)
        rows.append(_candidate(
            "PHR-290", 5, [461], "nominative_subject_of_for_infinitival",
            [match.start(2), match.end(2)], _case(pronoun, ACCUSATIVE[pronoun.casefold()]),
        ))
    return rows


def probe_who_subject(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(r"\b([Ww]hom)\s+([A-Za-z]+)\b")
    for match in pattern.finditer(sentence):
        following = match.group(2)
        lower = following.casefold()
        if lower in {"did", "does", "do", "will", "would", "can", "could",
                     "should", "is", "are", "was", "were", "has", "have",
                     "had", "we", "they", "he", "she", "i", "you"}:
            continue
        if not (lower in FINITE_VERBS or lower.endswith("ed")):
            continue
        rows.append(_candidate(
            "PHR-295", 5, [464, 465], "objective_whom_as_local_subject",
            [match.start(1), match.end(1)], _case(match.group(1), "who"),
            verb=following,
        ))
    return rows


def probe_genitive_pronoun(sentence: str) -> list[dict[str, Any]]:
    rows = []
    dependent = "|".join(sorted(DEPENDENT, key=len, reverse=True))
    pattern = re.compile(rf"\b({dependent})\s+([A-Za-z]+)\b", re.IGNORECASE)
    for match in pattern.finditer(sentence):
        pronoun = match.group(1)
        rows.append(_candidate(
            "PHR-305", 5, [470, 471], "independent_genitive_before_nominal",
            [match.start(1), match.end(1)], _case(pronoun, DEPENDENT[pronoun.casefold()]),
            following=match.group(2),
        ))
    independent = "|".join(sorted(INDEPENDENT, key=len, reverse=True))
    pattern = re.compile(
        rf"\b(is|are|was|were|seems?|became)\s+({independent})\b(?=\s*[.,;!?]|$)",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        pronoun = match.group(2)
        rows.append(_candidate(
            "PHR-305", 5, [470, 471], "dependent_genitive_as_independent_head",
            [match.start(2), match.end(2)], _case(pronoun, INDEPENDENT[pronoun.casefold()]),
        ))
    return rows


def probe_own(sentence: str) -> list[dict[str, Any]]:
    rows = []
    independent = "|".join(sorted(DEPENDENT, key=len, reverse=True))
    pattern = re.compile(rf"\b({independent})\s+own\b", re.IGNORECASE)
    for match in pattern.finditer(sentence):
        pronoun = match.group(1)
        rows.append(_candidate(
            "PHR-321", 5, [483], "independent_genitive_before_own",
            [match.start(1), match.end(1)], _case(pronoun, DEPENDENT[pronoun.casefold()]),
        ))
    return rows


def probe_emphatic_clause_adjunct(sentence: str) -> list[dict[str, Any]]:
    rows = []
    verbs = "|".join(sorted(DOUBLE_OBJECT_VERBS, key=len, reverse=True))
    pattern = re.compile(
        rf"\b({verbs})\s+([A-Z][a-z]+)\s+(the\s+[a-z][A-Za-z'-]*)\s+"
        r"(herself|himself|themselves|ourselves|myself|yourself)\b")
    for match in pattern.finditer(sentence):
        replacement = f"{match.group(1)} {match.group(2)} {match.group(4)} {match.group(3)}"
        rows.append(_candidate(
            "PHR-580", 17, [1497], "emphatic_adjunct_linked_to_nonsubject",
            [match.start(), match.end()], replacement,
            recipient=match.group(2), object=match.group(3),
        ))
    return rows


def probe_genitive_reflexive(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b((?:[Tt]he\s+[a-z][A-Za-z'-]*)|(?:[A-Z][a-z]+))\s+"
        r"(herself|himself|themselves|ourselves|myself|yourself)\s*['’]s\b")
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "PHR-582", 17, [1497], "genitive_with_np_internal_reflexive",
            [match.start(), match.end()], None,
            reflexive=match.group(2),
        ))
    pattern = re.compile(
        r"\b([A-Z][a-z]+)['’]s\s+(herself|himself|themselves|ourselves|myself|yourself)\b")
    for match in pattern.finditer(sentence):
        replacement = f"{match.group(1)} {match.group(2)}"
        rows.append(_candidate(
            "PHR-582", 17, [1497], "genitive_with_np_internal_reflexive",
            [match.start(), match.end()], replacement,
            reflexive=match.group(2),
        ))
    return rows


def probe_pronoun_case(sentence: str, *, variety: str = "standard_english") -> dict[str, Any]:
    result = _result()
    if variety != "standard_english":
        return result
    result["status"] = "candidate_only"
    for checker in (
        probe_accusative_object,
        probe_for_infinitival,
        probe_who_subject,
        probe_genitive_pronoun,
        probe_own,
        probe_emphatic_clause_adjunct,
        probe_genitive_reflexive,
    ):
        result["candidates"].extend(checker(sentence))
    return result
