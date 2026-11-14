"""Offline tense/aspect candidates for OTH-377, OTH-439 and OTH-458.

The checks are candidate-only and production-disabled. They do not certify a
modal reading, replace the source's semantic conditions, or enable a registry
rule.
"""
from __future__ import annotations

import re
from typing import Any

if __package__:
    from .parse_engine import _ordered_leaves
else:
    from parse_engine import _ordered_leaves


REPORTING_MENTAL = {
    "tell", "told", "ask", "asked", "know", "knew", "predict", "predicts",
    "predicted", "say", "said", "wonder", "wondered", "decide", "decided",
    "remember", "remembered", "forget", "forgot", "explain", "explained",
    "determine", "determined", "know", "guess", "guessed", "estimate",
}
PERCEPTION = {"hear", "see", "smell", "feel", "taste", "watch", "notice"}
ACHIEVEMENT = {
    "open", "find", "finish", "solve", "reach", "catch", "win", "pass",
    "lift", "move", "fix", "get", "unlock", "close", "complete", "obtain",
    "locate", "rescue", "persuade", "convince", "remember", "understand",
}
PRESENT_TO_REMOTE = {
    "is": "were", "are": "were", "am": "were", "can": "could",
    "will": "would", "have": "had", "has": "had", "do": "did", "does": "did",
}
LEAF_SURFACES = {"-LRB-": "(", "-RRB-": ")"}


def _result() -> dict[str, Any]:
    return {"status": "not_evaluated", "production_enabled": False,
            "candidates": [], "blocked": []}


def _edit(span: list[int], replacement: str) -> dict[str, Any]:
    return {"char_span": list(span), "replacement": replacement,
            "requires_reparse": True, "safe_to_apply_automatically": False}


def _candidate(rule_id: str, pages: list[int], kind: str, span: list[int],
               replacement: str | None, **relation: Any) -> dict[str, Any]:
    edit = _edit(span, replacement) if replacement is not None else None
    return {"rule_id": rule_id, "source_chapter": 3, "source_pages": pages,
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


def _last_leaf(node: dict[str, Any]) -> dict[str, Any] | None:
    last = None
    for leaf in _ordered_leaves(node):
        last = leaf
    return last


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


def _third_person(verb: str) -> str:
    lower = verb.casefold()
    if lower == "have":
        return "has"
    if lower == "do":
        return "does"
    if lower == "go":
        return "goes"
    if re.search(r"(?:s|x|z|ch|sh|o)$", lower):
        return verb + "es"
    if re.search(r"[^aeiou]y$", lower):
        return verb[:-1] + "ies"
    return verb + "s"


def _subject_is_plural(subject: dict[str, Any]) -> bool:
    leaves = list(_ordered_leaves(subject))
    if any(leaf.get("pos") == "PRP" and _leaf_lower(leaf) in {"we", "they", "you"}
           for leaf in leaves):
        return True
    if any(leaf.get("pos") in {"NNS", "NNPS"} for leaf in leaves):
        return True
    if any(leaf.get("surface") in {"and", ","} for leaf in leaves):
        return True
    return False


def _subject_of_clause(sbar: dict[str, Any]) -> dict[str, Any] | None:
    for child in sbar.get("children", []):
        if child.get("type") == "S":
            for part in child.get("children", []):
                if part.get("type") in {"NP", "SBAR", "PRP"}:
                    return part
    return None


def _temporal_sbar(sentence: str, sbar: dict[str, Any], spans: list[list[int]],
                   parent: dict[str, Any] | None) -> bool:
    first = _first_leaf(sbar)
    if first is None:
        return False
    surface = _leaf_lower(first)
    if surface == "as":
        start = spans[sbar["span"][0]][0]
        context = sentence[max(0, start - 12):start + 3].casefold()
        return "as soon" in context
    if surface not in {"when", "before", "after"}:
        return False
    if surface == "when" and parent is not None:
        parent_children = parent.get("children", [])
        position = next((i for i, child in enumerate(parent_children)
                         if child["id"] == sbar["id"]), None)
        if position is not None:
            head = None
            for child in reversed(parent_children[:position]):
                leaf = _first_leaf(child)
                if leaf is not None and leaf.get("pos", "").startswith("VB"):
                    head = _leaf_lower(leaf)
                    break
            if head in REPORTING_MENTAL:
                return False
    return True


def probe_temporal_will(sentence: str, tree: dict[str, Any]) -> list[dict[str, Any]]:
    aligned = _align(sentence, tree)
    if aligned is None:
        return []
    leaves, spans = aligned
    parents = {}
    for node in _walk(tree):
        for child in node.get("children", []):
            parents[child["id"]] = node
    rows = []
    for sbar in _walk(tree):
        if sbar.get("type") != "SBAR":
            continue
        if not _temporal_sbar(sentence, sbar, spans, parents.get(sbar["id"])):
            continue
        clause = next((child for child in sbar.get("children", [])
                       if child.get("type") == "S"), None)
        if clause is None:
            continue
        clause_leaves = list(_ordered_leaves(clause))
        will_index = next((i for i, leaf in enumerate(clause_leaves)
                           if _leaf_lower(leaf) in {"will", "'ll"}), None)
        if will_index is None:
            continue
        verb_index = next((i for i in range(will_index + 1, len(clause_leaves))
                           if clause_leaves[i].get("pos", "").startswith("VB")), None)
        if verb_index is None:
            continue
        between = clause_leaves[will_index + 1:verb_index]
        subject = _subject_of_clause(sbar)
        plural = _subject_is_plural(subject) if subject is not None else False
        verb = clause_leaves[verb_index]
        if _leaf_lower(verb) == "be":
            replacement = "are" if plural else ("am" if subject is not None
                                                 and _leaf_lower(_first_leaf(subject)) == "i" else "is")
        else:
            replacement = verb.get("surface", "") if plural else _third_person(verb.get("surface", ""))
        if between:
            if len(between) == 1 and _leaf_lower(between[0]) == "not":
                replacement = replacement + " not"
            else:
                replacement = None
        start = spans[clause["span"][0] + will_index][0]
        end = spans[clause["span"][0] + verb_index][1]
        rows.append(_candidate(
            "OTH-377", [191], "futurity_will_in_temporal_adjunct",
            [start, end], replacement,
            sbar_char_span=[spans[sbar["span"][0]][0], spans[sbar["span"][1] - 1][1]],
            temporal_head=_first_leaf(sbar).get("surface") if _first_leaf(sbar) else None,
        ))
    return rows


def probe_past_could_achievement(sentence: str) -> list[dict[str, Any]]:
    attempt = (r"(?:tried|searched|attempted|worked|struggled|looked|waited|"
               r"asked|hunted|reached|tested)")
    achieve = "|".join(sorted(ACHIEVEMENT, key=len, reverse=True))
    pattern = re.compile(
        rf"\b({attempt})\b[^.;!?]{{0,120}}?\band\s+(could)\s+({achieve})\b",
        re.IGNORECASE)
    rows = []
    for match in pattern.finditer(sentence):
        prefix = sentence[:match.start(1)].casefold()
        if re.search(r"\b(when i was|when we were|in those days|as a child|used to)\b", prefix):
            continue
        if re.search(r"\b(hear|see|smell|feel|taste|watch|notice)\b",
                     match.group(3), re.IGNORECASE):
            continue
        before = sentence[:match.start(1)]
        pronouns = re.findall(r"\b(I|we|you|he|she|it|they)\b", before, re.IGNORECASE)
        if pronouns:
            plural = pronouns[-1].casefold() in {"we", "you", "they"}
        else:
            word = re.search(r"([A-Za-z]+)\s*$", before)
            plural = bool(word and word.group(1).casefold().endswith("s")
                          and not word.group(1).casefold().endswith("ss"))
        replacement = "were able to" if plural else "was able to"
        span = [match.start(2), match.end(2)]
        rows.append(_candidate(
            "OTH-439", [197], "affirmative_past_could_single_event",
            span, replacement,
            achievement=match.group(3),
        ))
    return rows


def probe_wish_complement(sentence: str) -> list[dict[str, Any]]:
    subject = (r"(?:I|we|you|he|she|it|they|"
               r"(?:the|a|an)\s+(?:[A-Za-z-]+\s+){0,3}[A-Za-z-]+|"
               r"[A-Z][a-z]+)")
    pattern = re.compile(
        rf"\b(wish|wishes|wished)\s+(?:that\s+)?({subject})\s+"
        r"(is|are|am|can|will|have|has|do|does)\b",
        re.IGNORECASE)
    rows = []
    for match in pattern.finditer(sentence):
        verb = match.group(3)
        replacement = PRESENT_TO_REMOTE.get(verb.casefold())
        if replacement is None:
            continue
        span = [match.start(3), match.end(3)]
        rows.append(_candidate(
            "OTH-458", [200], "nonremote_present_in_wish_complement",
            span, replacement,
            wish_form=match.group(1), subject=match.group(2),
        ))
    return rows


def probe_tense_aspect(sentence: str, tree: dict[str, Any] | None = None, *,
                       variety: str = "standard_english") -> dict[str, Any]:
    result = _result()
    if variety != "standard_english":
        return result
    result["status"] = "candidate_only"
    result["candidates"].extend(probe_past_could_achievement(sentence))
    result["candidates"].extend(probe_wish_complement(sentence))
    if tree is None:
        result["blocked"].append("tree_relations_unavailable")
        return result
    result["candidates"].extend(probe_temporal_will(sentence, tree))
    return result
