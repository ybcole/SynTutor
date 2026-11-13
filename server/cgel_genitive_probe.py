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


def _align_leaves(sentence, tree):
    if any(mark in sentence for mark in '"“”‘'):
        return None
    normalized = sentence.translate(APOSTROPHES)
    if re.search(r"(?<!\w)'", normalized):
        return None
    leaves = list(_ordered_leaves(tree))
    spans = []
    cursor = 0
    for index, leaf in enumerate(leaves):
        while cursor < len(sentence) and sentence[cursor].isspace():
            cursor += 1
        surface = leaf["surface"].translate(APOSTROPHES)
        if not surface or leaf["span"] != [index, index + 1] or not normalized.startswith(surface, cursor):
            return None
        spans.append((cursor, cursor + len(surface)))
        cursor += len(surface)
    if sentence[cursor:].strip():
        return None
    return normalized, leaves, spans


def probe_plural_genitives(sentence, tree, *, variety):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    aligned = _align_leaves(sentence, tree) if variety == "standard_english" else None
    if aligned is None:
        return result
    normalized, leaves, spans = aligned
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


PERSONAL_GENITIVES = re.compile(r"\b(it|your)'s(?![\w'])", re.IGNORECASE)
COPULAS = {"am", "is", "are", "was", "were", "be", "been"}


def _copular_complement(node, first, after):
    children = node.get("children", [])
    if node["type"] == "VP":
        for verb, complement in zip(children, children[1:]):
            if (verb.get("pos", "").startswith("VB") and verb["surface"].lower() in COPULAS
                    and complement["type"] == "NP" and complement["span"] == [first, after]):
                return True
    return any(_copular_complement(child, first, after) for child in children)


def probe_personal_genitives(sentence, tree, *, variety):
    """Evaluate apostrophes only in the two possessive contexts covered by the pilot."""
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    aligned = _align_leaves(sentence, tree) if variety == "standard_english" else None
    if aligned is None:
        return result
    normalized, leaves, spans = aligned
    result["status"] = "candidate_only"
    starts = {start: index for index, (start, _) in enumerate(spans)}
    ends = {end: index + 1 for index, (_, end) in enumerate(spans)}
    for match in PERSONAL_GENITIVES.finditer(normalized):
        first, after = starts.get(match.start()), ends.get(match.end())
        if first is None or after is None:
            continue
        if match[1].lower() == "it":
            # A bare noun immediately after the spelling must be in the same
            # nominal constituent, without a verbal analysis of the clitic.
            if (after == len(leaves) or leaves[after].get("pos") not in {"NN", "NNS"}
                    or any(leaf.get("pos", "").startswith("VB") for leaf in leaves[first:after])
                    or not any(phrase["span"] == [first, after + 1]
                               for phrase in _noun_phrases(tree))):
                continue
            kind = "dependent_possessive"
        elif _copular_complement(tree, first, after):
            kind = "independent_possessive"
        else:
            continue
        span = list(match.span())
        result["candidates"].append({
            "rule_id": "OTH-761", "source_chapter": 20, "source_pages": [1763],
            "relation": {"kind": kind, "word_char_span": span},
            "edit_hint": {"char_span": span, "replacement": sentence[span[0]:span[1]].replace(
                "'", "").replace("’", ""), "requires_reparse": True, "safe_to_apply_automatically": False},
        })
    return result
