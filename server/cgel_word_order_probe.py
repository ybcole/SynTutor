"""Offline word-order and missing-object candidates for Phase C.

The checks are candidate-only and production-disabled. Reorder edits are scoped
to the diagnostic patterns and are not general-purpose transformations.
"""
from __future__ import annotations

import re
from typing import Any

if __package__:
    from .parse_engine import _ordered_leaves
else:
    from parse_engine import _ordered_leaves


ENOUGH_HEADS = {
    "warm", "cold", "clear", "clearly", "bright", "loud", "loudly", "quick",
    "quickly", "slow", "slowly", "strong", "strongly", "old", "young", "big",
    "small", "tall", "short", "early", "late", "carefully", "easily", "hard",
    "fast", "deep", "deeply", "wide", "widely", "high", "highly",
}
PRETERITE = {
    "leave": "left", "go": "went", "come": "came", "eat": "ate", "see": "saw",
    "take": "took", "make": "made", "write": "wrote", "sing": "sang",
    "run": "ran", "do": "did", "have": "had", "be": "was", "say": "said",
    "give": "gave", "find": "found", "build": "built", "break": "broke",
}
LEAF_SURFACES = {"-LRB-": "(", "-RRB-": ")"}
TIME_NOUNS = {"yesterday", "today", "tomorrow", "afternoon", "morning",
              "evening", "night", "week", "month", "year", "day"}


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
        expected = LEAF_SURFACES.get(leaf.get("surface", ""), leaf.get("surface", ""))
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


def _gerund_from_past(past: str) -> str:
    lower = past.casefold()
    if lower.endswith("ied"):
        return past[:-3] + "ying"
    if lower.endswith("ed"):
        return past[:-2] + "ing"
    return past + "ing"


def probe_such_a(sentence: str) -> list[dict[str, Any]]:
    rows = []
    for match in re.finditer(r"\b(a)\s+(such)\b", sentence, re.IGNORECASE):
        rows.append(_candidate(
            "PHR-247", 5, [435], "predeterminer_after_indefinite_article",
            [match.start(), match.end()], _case(match.group(0), "such a"),
        ))
    for match in re.finditer(r"\b([Aa])\s+what\s+([A-Za-z]+)\b", sentence):
        replacement = _case(match.group(1), "what a") + " " + match.group(2)
        rows.append(_candidate(
            "PHR-247", 5, [435], "exclamative_what_after_article",
            [match.start(), match.end()], replacement,
        ))
    return rows


def probe_before_that(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\bbefore\s+(that)\s+(?=(?:the|a|an|it|they|we|he|she|I|you)\b)",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "PHR-381", 7, [604], "that_before_temporal_clause",
            [match.start(1) - 1, match.end(1)], "",
        ))
    return rows


def probe_ago_order(sentence: str) -> list[dict[str, Any]]:
    rows = []
    duration = (r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
                r"eleven|twelve|twenty|thirty|forty|fifty|sixty|seventy|"
                r"eighty|ninety)\s+(?:day|days|week|weeks|month|months|year|"
                r"years|hour|hours|minute|minutes)")
    pattern = re.compile(rf"\bago\s+({duration})\b", re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "PHR-420", 7, [632], "ago_before_duration",
            [match.start(), match.end()], f"{match.group(1)} ago",
            duration=match.group(1),
        ))
    return rows


def probe_else_order(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\belse\s+(someone|anyone|something|anything|everyone|everything|"
        r"nobody|nothing|somewhere|anywhere)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "PHR-769", 17, [1548], "else_before_indefinite",
            [match.start(), match.end()], f"{match.group(1)} else",
            indefinite=match.group(1),
        ))
    return rows


def probe_particle_pronoun(sentence: str) -> list[dict[str, Any]]:
    rows = []
    verbs = (r"(?:brought|picked|put|took|gave|sent|handed|threw|turned|"
             r"shut|wrote|filled|checked)")
    pattern = re.compile(
        rf"\b({verbs})\s+(in|up|down|out|off|over|back|away|through)\s+"
        r"(it|them|him|her|me|us|you)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        replacement = f"{match.group(1)} {match.group(3)} {match.group(2)}"
        rows.append(_candidate(
            "COMP-085", 4, [247], "weak_pronoun_after_particle",
            [match.start(), match.end()], _case(match.group(0), replacement),
            particle=match.group(2), pronoun=match.group(3),
        ))
    return rows


def probe_explain_double_object(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\bexplained\s+((?:[A-Z][a-z]+)|(?:the\s+[a-z]+s?))\s+"
        r"(the\s+[a-z]+s?)\b")
    for match in pattern.finditer(sentence):
        replacement = f"explained {match.group(2)} to {match.group(1)}"
        rows.append(_candidate(
            "COMP-202", 4, [309], "explain_in_double_object_frame",
            [match.start(), match.end()], replacement,
            recipient=match.group(1), object=match.group(2),
        ))
    return rows


def probe_infinitival_negative(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(r"\bto\s+(don't|do not)\s+([A-Za-z]+)\b", re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "MORPH-056", 3, [89, 90], "imperative_do_support_after_to",
            [match.start(), match.end()], f"not to {match.group(2)}",
            verb=match.group(2),
        ))
    return rows


def probe_enough_order(sentence: str) -> list[dict[str, Any]]:
    rows = []
    heads = "|".join(sorted(ENOUGH_HEADS, key=len, reverse=True))
    pattern = re.compile(rf"\benough\s+({heads})\b", re.IGNORECASE)
    for match in pattern.finditer(sentence):
        rows.append(_candidate(
            "WCAT-046", 6, [534, 535], "degree_enough_before_head",
            [match.start(), match.end()], f"{match.group(1)} enough",
            head=match.group(1),
        ))
    return rows


def probe_multiple_aux_inversion(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b(Where|When|Why|How|What|Who|Which)\s+"
        r"(had|has|have|was|were|is|are|will|would|can|could|should|must|may|might)"
        r"\s+(been|being)\s+(the\s+[a-z]+|[A-Z][a-z]+)\s+([A-Za-z]+)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        replacement = f"{match.group(1)} {match.group(2)} {match.group(4)} {match.group(3)} {match.group(5)}"
        rows.append(_candidate(
            "CLS-114", 3, [97], "more_than_one_prenuclear_auxiliary",
            [match.start(), match.end()], replacement,
            auxiliary=match.group(2),
        ))
    pattern = re.compile(
        r"^(Has|Have|Had|Is|Are|Was|Were)\s+(been|being)\s+"
        r"(the\s+[a-z]+|[A-Z][a-z]+)\s+([A-Za-z]+)\b",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        replacement = f"{match.group(1)} {match.group(3)} {match.group(2)} {match.group(4)}"
        rows.append(_candidate(
            "CLS-114", 3, [97], "more_than_one_prenuclear_auxiliary",
            [match.start(), match.end()], replacement,
            auxiliary=match.group(1),
        ))
    return rows


def probe_fronted_question(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"^([Ww]here|[Ww]hat|[Ww]hen|[Ww]hy|[Hh]ow|[Ww]ho|[Ww]hich)\s+"
        r"([A-Z][a-z]+|(?:[Tt]he)\s+[a-z]+)\s+"
        r"(did|does|do|is|are|was|were|has|have|had|will|would|can|could|should)"
        r"\s+([A-Za-z]+)\b")
    match = pattern.match(sentence)
    if match:
        replacement = f"{match.group(1)} {match.group(3)} {match.group(2)} {match.group(4)}"
        rows.append(_candidate(
            "CLS-128", 10, [856], "no_inversion_after_fronted_phrase",
            [match.start(), match.end()], replacement,
            auxiliary=match.group(3),
        ))
    return rows


def probe_how_come(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"^(How come)\s+"
        r"(is|are|was|were|did|does|do|has|have|had|will|would|can|could|should)"
        r"\s+(the\s+[a-z]+|[A-Z][a-z]+)\s+(.+)$",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if not match:
        return []
    subject = match.group(3)
    rest = match.group(4)
    auxiliary = match.group(2)
    if auxiliary.casefold() == "did":
        verb_match = re.match(r"([A-Za-z]+)(.*)$", rest)
        if verb_match:
            preterite = PRETERITE.get(verb_match.group(1).casefold())
            if preterite:
                replacement = f"How come {subject} {preterite}{verb_match.group(2)}"
            else:
                replacement = f"How come {subject} did {rest}"
        else:
            replacement = f"How come {subject} did {rest}"
    else:
        replacement = f"How come {subject} {auxiliary} {rest}"
    rows.append(_candidate(
        "CLS-213", 10, [909], "inversion_after_how_come",
        [match.start(), match.end()], replacement,
        auxiliary=auxiliary,
    ))
    return rows


def probe_maximal_interrogative(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"^(What size)\s+(did|do|does)\s+(you|they|we|he|she|I)\s+"
        r"([A-Za-z]+)\s+([A-Za-z]+s)\?$",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        replacement = (f"{match.group(1)} {match.group(5)} {match.group(2)} "
                       f"{match.group(3)} {match.group(4)}?")
        rows.append(_candidate(
            "CLS-217", 10, [910, 911], "smaller_interrogative_phrase_fronted",
            [match.start(), match.end()], replacement,
        ))
    pattern = re.compile(
        r"^(How large|How big|How tall|How old)\s+(did|do|does)\s+"
        r"(they|you|we|he|she|I)\s+([A-Za-z]+)\s+a\s+([A-Za-z]+)\?$",
        re.IGNORECASE)
    match = pattern.match(sentence)
    if match:
        replacement = (f"{match.group(1)} a {match.group(5)} {match.group(2)} "
                       f"{match.group(3)} {match.group(4)}?")
        rows.append(_candidate(
            "CLS-217", 10, [910, 911], "smaller_interrogative_phrase_fronted",
            [match.start(), match.end()], replacement,
        ))
    return rows


def probe_perfect_progressive(sentence: str) -> list[dict[str, Any]]:
    rows = []
    pattern = re.compile(
        r"\b(She|He|It|They|We|I|You|[A-Z][a-z]+)\s+(is|are|am)\s+having\s+"
        r"([A-Za-z]+ed)\b",
        re.IGNORECASE)
    for match in pattern.finditer(sentence):
        subject = match.group(1)
        auxiliary = "have" if subject.casefold() in {"they", "we", "i", "you"} else "has"
        gerund = _gerund_from_past(match.group(3))
        replacement = f"{subject} {auxiliary} been {gerund}"
        rows.append(_candidate(
            "CLS-333", 14, [1214, 1215, 1216, 1217, 1218, 1219],
            "progressive_before_perfect", [match.start(), match.end()],
            replacement, participle=match.group(3),
        ))
    return rows


def probe_peruse_object(sentence: str, tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None or tree.get("type") != "S":
        return []
    leaves, spans = aligned
    children = tree.get("children", [])
    if len(children) < 2 or children[1].get("type") != "VP":
        return []
    predicate = children[1]
    first = _first_leaf(predicate)
    if first is None or _leaf_lower(first) != "perused":
        return []
    for child in predicate.get("children", []):
        if child.get("type") != "NP":
            continue
        head = next((leaf for leaf in reversed(list(_ordered_leaves(child)))
                     if leaf.get("pos", "").startswith("NN")), None)
        if head is not None and _leaf_lower(head) not in TIME_NOUNS:
            return []
    span = [spans[predicate["span"][0]][0], spans[predicate["span"][1] - 1][1]]
    return [
        _candidate("COMP-063", 4, [221], "peruse_without_object", span, None,
                   verb="perused"),
        _candidate("COMP-189", 4, [304], "peruse_without_object", span, None,
                   verb="perused"),
    ]


def probe_word_order(sentence: str, tree: dict[str, Any] | None = None, *,
                     variety: str = "standard_english") -> dict[str, Any]:
    result = _result()
    if variety != "standard_english":
        return result
    result["status"] = "candidate_only"
    for checker in (
        probe_such_a,
        probe_before_that,
        probe_ago_order,
        probe_else_order,
        probe_particle_pronoun,
        probe_explain_double_object,
        probe_infinitival_negative,
        probe_enough_order,
        probe_multiple_aux_inversion,
        probe_fronted_question,
        probe_how_come,
        probe_maximal_interrogative,
        probe_perfect_progressive,
    ):
        result["candidates"].extend(checker(sentence))
    if tree is None:
        result["blocked"].append("tree_relations_unavailable")
        return result
    result["candidates"].extend(probe_peruse_object(sentence, tree))
    return result
