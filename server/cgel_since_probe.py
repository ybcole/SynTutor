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


def probe_nested_backshift(sentence, tree, *, variety, shared_report_time_confirmed=False):
    """Check a present progressive report with a backshifted before-clause."""
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english" or shared_report_time_confirmed is not True:
        return result
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ) or any(token["text"] in {'"', '“', '”', "'", '‘', '’'} for token in tokens):
        return result
    result["status"] = "candidate_only"
    root = tree.get("children", [])
    if tree["type"] != "S" or [part["type"] for part in root] != ["NP", "VP", "."]:
        return result
    reporting = root[1].get("children", [])
    if (len(reporting) != 2 or reporting[0].get("pos") != "VBD"
            or reporting[0]["surface"].casefold() != "said" or reporting[1]["type"] != "SBAR"):
        return result
    complement = reporting[1].get("children", [])
    if (len(complement) != 2 or complement[0].get("surface", "").casefold() != "that"
            or complement[1]["type"] != "S"):
        return result
    clause = complement[1].get("children", [])
    if [part["type"] for part in clause] != ["NP", "VP"]:
        return result
    predicate = clause[1].get("children", [])
    if len(predicate) not in {2, 3}:
        return result
    auxiliary, progressive, *outer_adjunct = predicate
    if (auxiliary.get("pos") not in {"VBP", "VBZ"}
            or auxiliary["surface"].casefold() not in {"am", "is", "are"} or progressive["type"] != "VP"):
        return result
    progressive_parts = progressive.get("children", [])
    if not progressive_parts or progressive_parts[0].get("pos") != "VBG":
        return result
    temporal = outer_adjunct[0] if outer_adjunct else progressive_parts[-1]
    temporal_parts = temporal.get("children", [])
    if (temporal["type"] != "SBAR" or len(temporal_parts) != 2
            or temporal_parts[0].get("surface", "").casefold() != "before" or temporal_parts[1]["type"] != "S"):
        return result
    embedded = temporal_parts[1].get("children", [])
    if [part["type"] for part in embedded] != ["NP", "VP"]:
        return result
    lower = embedded[1].get("children", [])
    if len(lower) != 1 or lower[0].get("pos") != "VBD":
        return result
    result["candidates"].append({
        "rule_id": "OTH-158", "source_chapter": 3, "source_pages": [156],
        "relation": {"kind": "backshift_below_unshifted_report",
                     "higher_verb_char_span": tokens[auxiliary["span"][0]]["char_span"],
                     "lower_verb_char_span": tokens[lower[0]["span"][0]]["char_span"]},
        "edit_hint": None,
    })
    return result
