"""Offline OTH-182 evidence for two temporally bound catenative frames."""

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from parse_engine import _ordered_leaves


def _complement(predicate):
    parts = predicate.get("children", [])
    if len(parts) not in {2, 3} or parts[0].get("pos") not in {"VBD", "VBP", "VBZ"}:
        return None
    governor, *rest = parts
    word = governor["surface"].casefold()
    if word in {"begin", "begins", "began"} and len(rest) == 1 and rest[0]["type"] == "S":
        clause = rest[0].get("children", [])
        if len(clause) == 1 and clause[0]["type"] == "VP":
            infinitival = clause[0].get("children", [])
            if (len(infinitival) == 2 and infinitival[0].get("pos") == "TO"
                    and infinitival[0]["surface"].casefold() == "to" and infinitival[1]["type"] == "VP"):
                return governor, infinitival[1]
    if word in {"make", "makes", "made"}:
        clause = rest[0].get("children", []) if len(rest) == 1 and rest[0]["type"] == "S" else rest
        if [node["type"] for node in clause] == ["NP", "VP"]:
            return governor, clause[1]
    return None


def probe_catenative_perfect(sentence, tree, *, variety, bound_reading_confirmed=False):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english" or bound_reading_confirmed is not True:
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
    if tree["type"] != "S" or [part["type"] for part in parts] != ["NP", "VP", "."]:
        return result
    match = _complement(parts[1])
    if match is None:
        return result
    governor, complement = match
    vp = complement.get("children", [])
    if (len(vp) != 2 or vp[0].get("pos") != "VB" or vp[0]["surface"].casefold() != "have"
            or vp[1]["type"] != "VP"):
        return result
    lower = vp[1].get("children", [])
    if not lower or lower[0].get("pos") != "VBN":
        return result
    result["candidates"].append({
        "rule_id": "OTH-182", "source_chapter": 3, "source_pages": [161],
        "relation": {"kind": "bound_catenative_with_perfect_complement",
                     "governor_char_span": tokens[governor["span"][0]]["char_span"],
                     "auxiliary_char_span": tokens[vp[0]["span"][0]]["char_span"]},
        "edit_hint": None,
    })
    return result


def _objectless_believe(node):
    parts = node.get("children", [])
    if node["type"] == "VP" and len(parts) == 2:
        governor, clause = parts
        if (governor.get("pos") in {"VBD", "VBP", "VBZ"}
                and governor["surface"].casefold() in {"believe", "believes", "believed"}
                and clause["type"] == "S"):
            body = clause.get("children", [])
            if len(body) == 1 and body[0]["type"] == "VP":
                infinitive = body[0].get("children", [])
                if (len(infinitive) == 2 and infinitive[0].get("pos") == "TO"
                        and infinitive[0]["surface"].casefold() == "to" and infinitive[1]["type"] == "VP"):
                    lower = infinitive[1].get("children", [])
                    if lower and lower[0].get("pos") == "VB":
                        return governor, infinitive[0]
    return None


def probe_believe_object(sentence, tree, *, variety, complement_confirmed=False):
    """Check a confirmed infinitival complement of simple active believe."""
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english" or complement_confirmed is not True:
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
    if tree["type"] != "S" or [part["type"] for part in parts] != ["NP", "VP", "."]:
        return result
    match = _objectless_believe(parts[1])
    if match is None:
        return result
    governor, marker = match
    result["candidates"].append({
        "rule_id": "CLS-320", "source_chapter": 14, "source_pages": [1203],
        "relation": {"kind": "active_believe_infinitive_missing_object",
                     "governor_char_span": tokens[governor["span"][0]]["char_span"],
                     "marker_char_span": tokens[marker["span"][0]]["char_span"]},
        "edit_hint": None,
    })
    return result
