"""Offline COMP-062 probe for a direct to-infinitival complement of enjoy."""

import re

from lemminflect import getAllInflections, getInflection

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from parse_engine import _ordered_leaves


def _direct_complement(node):
    children = node.get("children", [])
    if node["type"] != "VP" or len(children) != 2:
        return None
    governor, clause = children
    if governor.get("pos") not in {"VB", "VBP", "VBZ", "VBD", "VBN", "VBG"}:
        return None
    if governor["surface"].casefold() not in {"enjoy", "enjoys", "enjoyed", "enjoying"}:
        return None
    parts = clause.get("children", [])
    if clause["type"] != "S" or len(parts) != 1 or parts[0]["type"] != "VP":
        return None
    infinitival = parts[0].get("children", [])
    if len(infinitival) != 2:
        return None
    marker, vp = infinitival
    if marker.get("pos") != "TO" or vp["type"] != "VP":
        return None
    lexical = vp.get("children", [])
    if not lexical or lexical[0].get("pos") != "VB" or any(
        part["type"] in {"CC", "CONJP"} for part in lexical
    ):
        return None
    return governor["span"][0], marker["span"][0], lexical[0]["span"][0]


def _relations(node):
    relation = _direct_complement(node)
    if relation is not None:
        yield relation
    for child in node.get("children", []):
        yield from _relations(child)


def probe_enjoy_parser(sentence, tree, *, variety):
    result = {"status": "candidate_only", "production_enabled": False, "candidates": [], "blocked": []}
    if variety != "standard_english":
        return result
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ):
        return {**result, "status": "not_evaluated", "blocked": ["parser_token_alignment_unavailable"]}
    if any(token["text"] in {'"', '“', '”', "'", "‘", "’"} for token in tokens):
        return {**result, "status": "not_evaluated", "blocked": ["quotation_scope_unresolved"]}
    for governor, marker, verb in _relations(tree):
        if (marker, verb) != (governor + 1, governor + 2):
            continue
        start = tokens[marker]["char_span"][0]
        verb_start, end = tokens[verb]["char_span"]
        base = tokens[verb]["text"]
        if not re.fullmatch(r"to[ \t]+", sentence[start:verb_start], re.IGNORECASE):
            continue
        forms = getInflection(base.casefold(), tag="VBG", inflect_oov=False)
        if len(forms) != 1 or base.casefold() not in getAllInflections(base.casefold(), upos="VERB").get("VB", ()):
            continue
        result["candidates"].append({
            "rule_id": "COMP-062",
            "source_chapter": 4,
            "source_pages": [221],
            "relation": {
                "kind": "enjoy_selects",
                "governor_token_index": governor,
                "dependent_token_index": verb,
                "governor_char_span": tokens[governor]["char_span"],
                "dependent_char_span": tokens[verb]["char_span"],
            },
            "edit_hint": {
                "char_span": [start, end], "replacement": forms[0],
                "requires_reparse": True, "safe_to_apply_automatically": False,
            },
        })
    return result
