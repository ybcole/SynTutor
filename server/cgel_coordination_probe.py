"""Offline evidence for two narrow basic-coordination constructions."""

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from parse_engine import _ordered_leaves


def _nonfinite_subject_kind(node):
    if node["type"] == "S":
        parts = node.get("children", [])
        if len(parts) != 1:
            return None
        node = parts[0]
    if node["type"] != "VP":
        return None
    parts = node.get("children", [])
    if parts and parts[0].get("pos") == "VBG":
        return "gerund_participial"
    if (len(parts) == 2 and parts[0].get("pos") == "TO"
            and parts[0]["surface"].casefold() == "to" and parts[1]["type"] == "VP"):
        lower = parts[1].get("children", [])
        if lower and lower[0].get("pos") == "VB":
            return "infinitival"
    return None


def _pair(node):
    parts = node.get("children", [])
    if len(parts) == 3 and parts[1].get("pos") == "CC" and parts[1]["surface"].casefold() in {"and", "or"}:
        return parts[0], parts[2]
    return None


def _arrival_pair(predicate):
    parts = predicate.get("children", [])
    if (len(parts) != 2 or parts[0].get("pos") not in {"VBD", "VBP", "VBZ"}
            or parts[0]["surface"].casefold() not in {"arrive", "arrives", "arrived"}):
        return None
    pair = _pair(parts[1])
    if pair is None:
        return None
    left, right = pair
    left_words = [leaf["surface"].casefold() for leaf in _ordered_leaves(left)]
    right_parts = right.get("children", [])
    if (left["type"] in {"NP", "ADVP", "RB"} and left_words in (["yesterday"], ["today"], ["tomorrow"])
            and right["type"] == "NP" and len(right_parts) == 2
            and right_parts[0].get("pos") == "DT" and right_parts[0]["surface"].casefold() == "the"
            and right_parts[1].get("pos") == "NN"
            and right_parts[1]["surface"].casefold() in {"station", "airport", "terminal"}):
        return pair
    return None


def probe_coordination(sentence, tree, *, variety):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english":
        return result
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ) or any(token["text"] in {'"', '“', '”', "'", "‘", "’"} for token in tokens):
        return result
    result["status"] = "candidate_only"
    parts = tree.get("children", [])
    if tree["type"] != "S" or len(parts) != 3 or [part["type"] for part in parts[1:]] != ["VP", "."]:
        return result
    subject, predicate, _ = parts
    pair = _pair(subject) if subject["type"] in {"S", "NP", "UCP"} else None
    if pair and {_nonfinite_subject_kind(node) for node in pair} == {"infinitival", "gerund_participial"}:
        rule, page, kind = "CLS-1035", 1324, "mixed_nonfinite_subject_coordinates"
    elif subject["type"] == "NP" and (pair := _arrival_pair(predicate)):
        rule, page, kind = "CLS-1034", 1323, "arrival_time_and_unlicensed_bare_location"
    else:
        return result
    result["candidates"].append({
        "rule_id": rule, "source_chapter": 15, "source_pages": [page],
        "relation": {"kind": kind, "coordinate_char_spans": [
            [tokens[start]["char_span"][0], tokens[end - 1]["char_span"][1]]
            for start, end in (node["span"] for node in pair)
        ]},
        "edit_hint": None,
    })
    return result
