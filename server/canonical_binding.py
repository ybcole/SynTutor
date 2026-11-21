"""Bind legacy Benepar node details to canonical B-R nodes.

The legacy detector stores node ids such as `n4`. The canonical envelope uses
ids such as `sg-root-1-0-0`. This module adds `canonical_node_id` and a small
binding record to each detail using token spans and remediation edit positions.
It is a display/evidence bridge, not a Cambridge rule evaluator.
"""
from __future__ import annotations

import re
from typing import Any

_LEAF_TAGS = {
    "CC", "CD", "DT", "EX", "IN", "JJ", "JJR", "JJS", "MD", "NN", "NNS",
    "NNP", "NNPS", "PDT", "PRP", "PRP$", "RB", "RBR", "RBS", "RP", "TO",
    "UH", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ", "WDT", "WP", "WP$", "WRB",
}
_QUOTED = re.compile(r"['\u2018\u2019]([^'\u2018\u2019]{1,60})['\u2018\u2019]")


def _walk(root: dict[str, Any] | None, parent: dict[str, Any] | None = None):
    if not isinstance(root, dict):
        return
    yield root, parent
    for child in root.get("children") or []:
        yield from _walk(child, root)


def _span_length(node: dict[str, Any]) -> int:
    span = node.get("token_span")
    return span[1] - span[0] if isinstance(span, list) and len(span) == 2 else 10**9


def _node_label(node: dict[str, Any], parents: dict[str, dict[str, Any]]) -> str | None:
    label = node.get("label")
    if label:
        return label
    parent = parents.get(node.get("id"))
    while parent:
        if parent.get("label"):
            return parent["label"]
        parent = parents.get(parent.get("id"))
    return None


def bind_details_to_canonical(tree: dict[str, Any] | None,
                              details: dict[str, Any] | None, *,
                              parser_tokens=None, sentence_offset=0) -> dict[str, Any]:
    root = (tree or {}).get("root") if isinstance(tree, dict) else None
    if not isinstance(root, dict) or not isinstance(details, dict):
        return {"status": "unavailable", "mapped": 0, "unmapped": 0}
    nodes = []
    parents: dict[str, dict[str, Any]] = {}
    for node, parent in _walk(root):
        if not isinstance(node.get("id"), str):
            continue
        nodes.append(node)
        if parent is not None:
            parents[node["id"]] = parent

    def smallest_span(start: int, end: int):
        hits = [node for node in nodes
                if isinstance(node.get("token_span"), list)
                and len(node["token_span"]) == 2
                and node["token_span"][0] <= start and end <= node["token_span"][1]]
        return min(hits, key=_span_length) if hits else None

    def smallest_token(index: int):
        hits = [node for node in nodes
                if isinstance(node.get("token_span"), list)
                and len(node["token_span"]) == 2
                and node["token_span"][0] <= index < node["token_span"][1]]
        if not hits:
            return None
        return min(hits, key=lambda node: (
            0 if not node.get("children") else 1,
            _span_length(node),
        ))

    tokens = tree.get("tokens") if isinstance(tree.get("tokens"), list) else []
    source_spans = {(tuple(token['char_span']), token['text']): token['index']
                    for token in tokens if token.get('char_span')}
    index_map = {token['i']: source_spans.get((
        (token['start'] - sentence_offset, token['end'] - sentence_offset), token['t']))
                 for token in parser_tokens or []}

    def source_span(start, end):
        if parser_tokens is None:
            return (start, end)
        matched = [index_map[i] for i in range(start, end) if index_map.get(i) is not None]
        return (min(matched), max(matched) + 1) if matched else None

    mapped = 0
    unmapped = 0
    for detail in details.values():
        if not isinstance(detail, dict):
            continue
        targets = []
        remediation = detail.get("remediation") or {}
        rows = []
        if isinstance(remediation, dict) and isinstance(remediation.get("edit"), dict):
            rows.append(remediation)
        if isinstance(remediation, dict):
            rows.extend(row for row in remediation.get("edits") or [] if isinstance(row, dict))
        for row in rows:
            edit = row.get("edit") if isinstance(row.get("edit"), dict) else row
            start = edit.get("start")
            end = edit.get("end")
            if not isinstance(start, int):
                continue
            mapped_edit = source_span(start, end if isinstance(end, int) and end > start else start + 1)
            if not mapped_edit:
                continue
            first, last = mapped_edit
            node = smallest_span(first, last) if last > first + 1 else smallest_token(first)
            if node is not None:
                targets.append(node)
        # A finding can name one word while its repair edits a different word
        # ("These child" flags the determiner but repairs the noun). Bind the
        # flagged node too so every red word has an explanation.
        span = detail.get("span") if isinstance(detail.get("span"), list) else []
        if len(span) == 2 and all(isinstance(value, int) for value in span):
            start, end = span
            if str(detail.get("type") or "").upper() in _LEAF_TAGS or end - start <= 1:
                extent = source_span(start, min(end, start + 1))
                if extent:
                    node = smallest_token(extent[0])
                    if node is not None:
                        targets.append(node)
        scoped = source_span(*span) if len(span) == 2 and all(isinstance(v, int) for v in span) else None
        if not rows and scoped:
            prose = " ".join(str(remediation.get(key) or "") for key in
                             ("violation", "suggested_fix", "alternative_fix"))
            prose += " " + str(detail.get("text") or "")
            surface_words = set(re.findall(
                r"[A-Za-z0-9][A-Za-z0-9'’-]*", str(detail.get("surface") or "").lower()))
            for word in _QUOTED.findall(prose):
                # Resolve only single-word quotes that actually occur inside
                # the flagged node. Otherwise prose such as "subjects with
                # 'and'" would mark an unrelated conjunction.
                if " " in word.strip() or word.strip().lower() not in surface_words:
                    continue
                matches = [i for i in range(*scoped) if i < len(tokens)
                           and tokens[i]['text'].lower() == word.strip().lower()]
                node = smallest_token(matches[0]) if len(matches) == 1 else None
                if node is not None:
                    targets.append(node)
        if not targets and scoped:
            node = smallest_span(*scoped)
            if node is not None:
                targets.append(node)
        unique = []
        for node in targets:
            if node["id"] not in {item["id"] for item in unique}:
                unique.append(node)
        if not unique:
            unmapped += 1
            detail["canonical_node_id"] = None
            detail["canonical_node_ids"] = []
            detail["canonical_binding"] = {
                "status": "unmapped",
                "reason": "no canonical node covers the legacy span/edit target",
            }
            continue
        mapped += 1
        detail["canonical_node_id"] = unique[0]["id"]
        detail["canonical_node_ids"] = [node["id"] for node in unique]
        detail["canonical_binding"] = {
            "status": "mapped",
            "node_id": unique[0]["id"],
            "node_ids": [node["id"] for node in unique],
            "label": _node_label(unique[0], parents),
            "token_span": unique[0].get("token_span"),
            "token_spans": [node.get("token_span") for node in unique
                            if isinstance(node.get("token_span"), list)],
        }
    return {"status": "mapped", "mapped": mapped, "unmapped": unmapped}
