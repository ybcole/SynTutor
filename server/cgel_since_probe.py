"""Offline OTH-098 evidence for a confirmed present-inclusive state."""

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from parse_engine import _ordered_leaves


def probe_ever_since(sentence, tree, *, variety, present_continuation_confirmed=False):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english" or present_continuation_confirmed is not True:
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
    if len(predicate) < 2 or any(part["type"] in {"CC", "CONJP"} for part in predicate):
        return result
    verb, adjunct = predicate[0], predicate[-1]
    if (verb.get("pos") != "VBD" or verb["surface"].casefold() not in {"was", "were", "knew", "stood"}
            or adjunct["type"] not in {"ADVP", "PP", "SBAR"}):
        return result
    start, end = adjunct["span"]
    if [token["lower"] for token in tokens[start:start + 2]] != ["ever", "since"]:
        return result
    result["candidates"].append({
        "rule_id": "OTH-098", "source_chapter": 3, "source_pages": [141],
        "relation": {"kind": "preterite_with_present_inclusive_ever_since",
                     "verb_char_span": tokens[verb["span"][0]]["char_span"],
                     "adjunct_char_span": [tokens[start]["char_span"][0], tokens[end - 1]["char_span"][1]]},
        "edit_hint": None,
    })
    return result


def probe_completed_past_perfect(sentence, tree, *, variety, single_event_confirmed=False):
    """Recognize selected completed-time adjuncts in a confirmed single-event reading."""
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english" or single_event_confirmed is not True:
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
    predicate = parts[1].get("children", [])
    if len(predicate) not in {2, 3}:
        return result
    auxiliary, perfect, *outer_adjunct = predicate
    if (auxiliary.get("pos") not in {"VBP", "VBZ"}
            or auxiliary["surface"].casefold() not in {"have", "has"} or perfect["type"] != "VP"):
        return result
    lexical = perfect.get("children", [])
    if not lexical or lexical[0].get("pos") != "VBN":
        return result
    adjunct = outer_adjunct[0] if outer_adjunct else lexical[-1]
    if adjunct["type"] not in {"NP", "ADVP"}:
        return result
    # Restrict the whole predicate to a simple verb and an optional NP object.
    arguments = lexical[1:] if outer_adjunct else lexical[1:-1]
    if len(arguments) > 1 or any(node["type"] != "NP" for node in arguments):
        return result
    start, end = adjunct["span"]
    words = tuple(token["lower"] for token in tokens[start:end])
    if words not in {("yesterday",), ("last", "week"), ("two", "minutes", "ago")}:
        return result
    result["candidates"].append({
        "rule_id": "OTH-102", "source_chapter": 3, "source_pages": [143, 144, 146],
        "relation": {"kind": "completed_past_adjunct_with_present_perfect",
                     "auxiliary_char_span": tokens[auxiliary["span"][0]]["char_span"],
                     "adjunct_char_span": [tokens[start]["char_span"][0], tokens[end - 1]["char_span"][1]]},
        "edit_hint": None,
    })
    return result
