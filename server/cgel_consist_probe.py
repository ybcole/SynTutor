"""Offline COMP-060 probe for explicitly confirmed composition readings."""

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from parse_engine import _ordered_leaves


def probe_consist(sentence, tree, *, variety, composition_confirmed=False):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english" or composition_confirmed is not True:
        return result
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ) or any(token["text"] in {'"', '“', '”', "'", '‘', '’'} for token in tokens):
        return result
    result["status"] = "candidate_only"
    parts = tree.get("children", [])
    if tree["type"] != "S" or [part["type"] for part in parts] != ["NP", "VP", "."]:
        return result
    predicate = parts[1].get("children", [])
    if len(predicate) != 2:
        return result
    verb, phrase = predicate
    if (verb.get("pos") not in {"VBP", "VBZ", "VBD"}
            or verb.get("surface", "").casefold() not in {"consist", "consists", "consisted"}
            or phrase["type"] != "PP"):
        return result
    pp = phrase.get("children", [])
    if len(pp) != 2 or pp[1]["type"] != "NP":
        return result
    marker = pp[0]
    if marker.get("pos") != "IN" or marker.get("surface", "").casefold() not in {"with", "on"}:
        return result
    if marker["span"][0] != verb["span"][1]:
        return result
    span = tokens[marker["span"][0]]["char_span"]
    result["candidates"].append({
        "rule_id": "COMP-060", "source_chapter": 4, "source_pages": [220],
        "relation": {"kind": "composition_preposition",
                     "verb_char_span": tokens[verb["span"][0]]["char_span"],
                     "preposition_char_span": span},
        "edit_hint": {"char_span": span, "replacement": "of",
                      "requires_reparse": True, "safe_to_apply_automatically": False},
    })
    return result
