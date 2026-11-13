"""Offline evidence for selected plural genitive spellings."""

import re

if __package__:
    from .parse_engine import _ordered_leaves
else:
    from parse_engine import _ordered_leaves


REPLACEMENTS = {"teachers's": "teachers'", "students's": "students'",
                "childrens'": "children's", "womens'": "women's"}
APOSTROPHES = str.maketrans({"’": "'"})
SPELLINGS = re.compile(r"\b(?:" + "|".join(map(re.escape, REPLACEMENTS)) + r")(?![\w'])")


def _noun_phrases(node):
    if node["type"] == "NP":
        yield node
    for child in node.get("children", []):
        yield from _noun_phrases(child)


def probe_plural_genitives(sentence, tree, *, variety):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english" or any(mark in sentence for mark in '"“”‘'):
        return result

    normalized = sentence.translate(APOSTROPHES)
    if re.search(r"(?<!\w)'", normalized):
        return result
    leaves = list(_ordered_leaves(tree))
    spans = []
    cursor = 0
    for index, leaf in enumerate(leaves):
        while cursor < len(sentence) and sentence[cursor].isspace():
            cursor += 1
        surface = leaf["surface"].translate(APOSTROPHES)
        if not surface or leaf["span"] != [index, index + 1] or not normalized.startswith(surface, cursor):
            return result
        spans.append((cursor, cursor + len(surface)))
        cursor += len(surface)
    if sentence[cursor:].strip():
        return result
    result["status"] = "candidate_only"

    starts = {start: index for index, (start, _) in enumerate(spans)}
    ends = {end: index + 1 for index, (_, end) in enumerate(spans)}
    noun_phrases = list(_noun_phrases(tree))
    for match in SPELLINGS.finditer(normalized):
        first = starts.get(match.start())
        after = ends.get(match.end())
        if first is None or after is None or leaves[first].get("pos") not in {"NN", "NNS"}:
            continue
        # Require a following common noun in the same NP. This pilot leaves
        # independent genitives and NP-internal modifiers to separate checks.
        if after == len(leaves) or leaves[after].get("pos") not in {"NN", "NNS"}:
            continue
        if not any(start <= first and end == after + 1
                   for start, end in (phrase["span"] for phrase in noun_phrases)):
            continue
        replacement = REPLACEMENTS[match.group()]
        if "’" in sentence[match.start():match.end()]:
            replacement = replacement.replace("'", "’")
        span = list(match.span())
        result["candidates"].append({
            "rule_id": "MORPH-105", "source_chapter": 18, "source_pages": [1595, 1596],
            "relation": {"kind": "plural_genitive_spelling", "word_char_span": span},
            "edit_hint": {"char_span": span, "replacement": replacement,
                          "requires_reparse": True, "safe_to_apply_automatically": False},
        })
    return result
