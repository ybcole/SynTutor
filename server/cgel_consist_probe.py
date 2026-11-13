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


def probe_come_across(sentence, tree, *, variety, encounter_confirmed=False):
    """Check fronted across in a simple direct question with confirmed encounter sense."""
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english" or encounter_confirmed is not True:
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
    if (tree["type"] != "SBARQ" or [part["type"] for part in parts] != ["WHPP", "SQ", "."]
            or parts[-1].get("surface") != "?"):
        return result
    fronted, question, _ = parts
    pp = fronted.get("children", [])
    if (len(pp) != 2 or pp[0].get("pos") != "IN"
            or pp[0]["surface"].casefold() != "across" or pp[1]["type"] != "WHNP"):
        return result
    body = question.get("children", [])
    if (len(body) != 3 or body[0].get("pos") not in {"VBD", "VBP", "VBZ", "MD"}
            or body[0]["surface"].casefold() not in {"did", "do", "does", "can", "could", "will", "would"}
            or [part["type"] for part in body[1:]] != ["NP", "VP"]):
        return result
    predicate = body[-1].get("children", [])
    if (len(predicate) != 1 or predicate[0].get("pos") != "VB"
            or predicate[0]["surface"].casefold() != "come"):
        return result
    result["candidates"].append({
        "rule_id": "COMP-128", "source_chapter": 4, "source_pages": [275],
        "relation": {"kind": "fronted_preposition_in_encounter_construction",
                     "preposition_char_span": tokens[pp[0]["span"][0]]["char_span"],
                     "verb_char_span": tokens[predicate[0]["span"][0]]["char_span"]},
        "edit_hint": None,
    })
    return result
