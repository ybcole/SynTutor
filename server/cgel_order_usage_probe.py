"""Offline complement-selection and inversion candidates for Phase C.

The checks are candidate-only and production-disabled. Reorder and rewrite
edits are scoped to the diagnostic pairs and are not general transformations.
"""
from __future__ import annotations

import re
from typing import Any


SIMPLE_PAST_TO_BASE = {
    "had": "have", "caused": "cause", "made": "make", "took": "take",
    "gave": "give", "sent": "send", "wrote": "write", "saw": "see",
    "found": "find", "left": "leave", "came": "come", "went": "go",
    "did": "do", "said": "say", "built": "build", "broke": "break",
}
LEXICAL_VERBS = {
    "visits", "visit", "travels", "travel", "reads", "read", "writes",
    "write", "sees", "see", "makes", "make", "takes", "take", "plays",
    "play", "works", "work", "calls", "call", "checks", "check",
}
ADVERBS = {"always", "probably", "often", "usually", "sometimes", "never",
           "rarely", "seldom"}
DIRECTION_ADVERBS = {"downstairs", "upstairs", "inside", "outside", "indoors",
                     "outdoors"}


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


def probe_superior_than(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\b(superior|inferior)\s+than\b", sentence, re.IGNORECASE):
        rows.append(_candidate(
            "CLS-1166", 13, [1129, 1130], "than_with_superior_or_inferior",
            [match.start(), match.end()], _case(match.group(0), f"{match.group(1)} to"),
            adjective=match.group(1),
        ))
    return rows


def probe_similar_as(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\bsimilar\s+as\b", sentence, re.IGNORECASE):
        rows.append(_candidate(
            "CLS-1197", 13, [1141], "as_with_similar",
            [match.start(), match.end()], _case(match.group(0), "similar to"),
        ))
    return rows


def probe_other_than_clause(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\bother than\s+((?:the|his|her|their|our|my|your)\s+[a-z]+s?\s+"
        r"([a-z]+ed|offered|sent|said|expected|did|does|is|was|were|can|could|will|would))\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "CLS-1218", 13, [1145], "bare_clause_after_other_than",
            [match.start(1), match.start(1)], "what ",
            subject=match.group(1),
        ))
    return rows


def probe_got_seen(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(r"\bgot\s+seen\s+to\s+([A-Za-z]+)\b", re.IGNORECASE)
    for match in pattern.finditer(sentence):
        before = sentence[:match.start()].rstrip()
        word = re.search(r"([A-Za-z]+)\s*$", before)
        plural = bool(word and (word.group(1).casefold() in {"two", "three", "they", "we", "you"}
                                or word.group(1).casefold().endswith("s")))
        replacement = "were" if plural else "was"
        rows.append(_candidate(
            "CLS-1479", 16, [1442, 1443], "get_passive_of_perception_verb",
            [match.start(), match.start() + 3], replacement,
            participle="seen",
        ))
    return rows


def probe_inversion_clausal_subject(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"^(Would|Will|Can|Could|Should|Does|Do|Did|Is|Are|Was|Were|Has|Have|Had)"
        r"\s+to\s+([A-Za-z]+)\s+(the\s+[a-z]+)\s+([A-Za-z]+)(\?)?$",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        replacement = (f"{match.group(1)} it {match.group(4)} to "
                       f"{match.group(2)} {match.group(3)}{match.group(5) or ''}")
        rows.append(_candidate(
            "CLS-1379", 16, [1406, 1407], "infinitival_subject_after_auxiliary",
            [match.start(), match.end()], replacement,
        ))
    pattern = re.compile(
        r"^(Is|Was|Are|Were|Does|Do|Did|Has|Have|Had)\s+that\s+"
        r"(the\s+[a-z]+)\s+([A-Za-z]+ed)\s+([A-Za-z]+)\?$",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        replacement = (f"{match.group(1)} it {match.group(4)} that "
                       f"{match.group(2)} {match.group(3)}?")
        rows.append(_candidate(
            "CLS-1379", 16, [1406, 1407], "declarative_subject_after_auxiliary",
            [match.start(), match.end()], replacement,
        ))
    return rows


def probe_fronted_so_such(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"^(So\s+(?:little|much|few|many)\s+[a-z]+)\s+"
        r"(we|they|I|you|he|she|the\s+[a-z]+)\s+([A-Za-z]+)\s+that\b",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        base = SIMPLE_PAST_TO_BASE.get(match.group(3).casefold(), match.group(3))
        replacement = f"{match.group(1)} did {match.group(2)} {base} that"
        rows.append(_candidate(
            "CLS-108", 3, [96], "fronted_so_result_without_inversion",
            [match.start(), match.end()], replacement,
            fronted=match.group(1),
        ))
    pattern = re.compile(
        r"^(Such a [a-z]+)\s+(the\s+[a-z]+|[A-Z][a-z]+)\s+"
        r"([A-Za-z]+ed)\s+that\b",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        base = SIMPLE_PAST_TO_BASE.get(match.group(3).casefold())
        if base is None:
            base = match.group(3)[:-2]
        replacement = f"{match.group(1)} did {match.group(2)} {base} that"
        rows.append(_candidate(
            "CLS-108", 3, [96], "fronted_such_result_without_inversion",
            [match.start(), match.end()], replacement,
            fronted=match.group(1),
        ))
    return rows


def probe_adverb_placement(sentence: str) -> list[dict[str, Any]]:
    rows = []
    verbs = "|".join(sorted(LEXICAL_VERBS, key=len, reverse=True))
    adverbs = "|".join(sorted(ADVERBS, key=len, reverse=True))
    pattern = re.compile(rf"\b({verbs})\s+({adverbs})\b", re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "CLS-117", 3, [102], "adverb_between_lexical_verb_and_complement",
            [match.start(), match.end()], f"{match.group(2)} {match.group(1)}",
            adverb=match.group(2),
        ))
    return rows


def probe_single_fronting(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"^(What|Who|Which)\s+(to\s+whom|to\s+what)\s+"
        r"(did|does|do|will|would|can|could|should)\s+"
        r"(she|he|they|we|I|you)\s+([A-Za-z]+)\?$",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        replacement = (f"{match.group(1)} {match.group(3)} {match.group(4)} "
                       f"{match.group(5)} {match.group(2)}?")
        rows.append(_candidate(
            "CLS-156", 10, [874], "two_fronted_interrogative_phrases",
            [match.start(), match.end()], replacement,
        ))
    pattern = re.compile(
        r"^(Where|When|Why|How)\s+(which\s+[a-z]+s?)\s+"
        r"(did|does|do|will|would|can|could|should)\s+"
        r"(they|she|he|we|I|you)\s+([A-Za-z]+)\?$",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        replacement = (f"{match.group(1)} {match.group(3)} {match.group(4)} "
                       f"{match.group(5)} {match.group(2)}?")
        rows.append(_candidate(
            "CLS-156", 10, [874], "two_fronted_interrogative_phrases",
            [match.start(), match.end()], replacement,
        ))
    return rows


def probe_for_subject_order(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\bfor\s+(the\s+[a-z]+)\s+(you|them|us|him|her|me|it)\s+to\s+([A-Za-z]+)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        replacement = f"for {match.group(2)} to {match.group(3)} {match.group(1)}"
        rows.append(_candidate(
            "CLS-286", 14, [1182, 1183], "object_between_for_and_subject",
            [match.start(), match.end()], replacement,
            subject=match.group(2), object=match.group(1),
        ))
    return rows


def probe_fragment_stranding(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b([Ww])hich\s+([a-z]+)\s+(in|on|at|to|from|with|by|for)\?")
    for match in pattern.finditer(sentence):
        replacement = f"{match.group(3).capitalize()} which {match.group(2)}?"
        rows.append(_candidate(
            "PHR-748", 17, [1541], "stranded_preposition_after_which_np",
            [match.start(), match.end()], replacement,
            preposition=match.group(2),
        ))
    return rows


def probe_direction_adverb(sentence: str) -> list[dict[str, Any]]:
    rows = []
    verbs = r"(?:brought|carried|took|sent|put|threw|handed|pulled|pushed)"
    pattern = re.compile(
        rf"\b({verbs})\s+(downstairs|upstairs|inside|outside|indoors|outdoors)\s+"
        r"(the\s+[a-z]+(?: [a-z]+){0,2})",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        following = sentence[match.end():].lstrip()
        if re.match(r"(that|which|who)\b", following, re.IGNORECASE):
            continue
        if len(match.group(3).split()) > 3:
            continue
        replacement = f"{match.group(1)} {match.group(3)} {match.group(2)}"
        rows.append(_candidate(
            "COMP-138", 4, [280], "direction_adverb_before_light_np",
            [match.start(), match.end()], replacement,
            direction=match.group(2), object=match.group(3),
        ))
    return rows


def probe_aux_order(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\bhad\s+(could|might|must|should|would|can|may)\s+be\s+([A-Za-z]+ed)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        replacement = f"{match.group(1)} have been {match.group(2)}"
        rows.append(_candidate(
            "COMP-033", 3, [105, 106], "modal_after_perfect",
            [match.start(), match.end()], replacement,
            modal=match.group(1),
        ))
    pattern = re.compile(
        r"\b(is|are|was|were)\s+having\s+been\s+([A-Za-z]+ed)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        auxiliary = "has" if match.group(1).casefold() in {"is", "was"} else "have"
        replacement = f"{auxiliary} been {match.group(2)}"
        rows.append(_candidate(
            "COMP-033", 3, [105, 106], "progressive_before_perfect",
            [match.start(), match.end()], replacement,
            auxiliary=auxiliary,
        ))
    return rows


def probe_dynamic_have(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"^Had\s+(they|we|you|he|she|I)\s+(a|an|the)\s+"
        r"([a-z]+(?:\s+[a-z]+)?)\?$",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        replacement = f"Did {match.group(1)} have {match.group(2)} {match.group(3)}?"
        rows.append(_candidate(
            "COMP-040", 3, [111], "dynamic_have_without_do_support",
            [match.start(), match.end()], replacement,
            subject=match.group(1),
        ))
    pattern = re.compile(
        r"^(She|He|They|We|I|You|The\s+[a-z]+)\s+hadn't\s+"
        r"(the\s+[a-z]+)\s+([A-Za-z]+ed)\b",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        replacement = f"{match.group(1)} did not have {match.group(2)} {match.group(3)}"
        rows.append(_candidate(
            "COMP-040", 3, [111], "dynamic_have_without_do_support",
            [match.start(), match.end()], replacement,
            subject=match.group(1),
        ))
    return rows


def probe_order_usage(sentence: str, *, variety: str = "standard_english") -> dict[str, Any]:
    result = _result()
    if variety != "standard_english":
        return result
    result["status"] = "candidate_only"
    for checker in (
        probe_superior_than,
        probe_similar_as,
        probe_other_than_clause,
        probe_got_seen,
        probe_inversion_clausal_subject,
        probe_fronted_so_such,
        probe_adverb_placement,
        probe_single_fronting,
        probe_for_subject_order,
        probe_fragment_stranding,
        probe_direction_adverb,
        probe_aux_order,
        probe_dynamic_have,
    ):
        result["candidates"].extend(checker(sentence))
    return result
