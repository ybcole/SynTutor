"""Offline evidence for overt degree modifiers in scalar comparative clauses."""

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from parse_engine import _ordered_leaves


def _degree_conflict(node):
    if node["type"] != "ADJP":
        return None
    parts = node.get("children", [])
    if len(parts) == 2 and parts[0]["type"] == "ADJP":
        parts = [*parts[0].get("children", []), parts[1]]
    if len(parts) == 3 and parts[0].get("surface", "").casefold() == "as" and parts[1].get("pos") == "JJ":
        governor, _, comparison = parts
        marker = "as"
    elif len(parts) == 2 and parts[0].get("pos") == "JJR":
        governor, comparison = parts
        marker = "than"
    else:
        return None
    tail = comparison.get("children", [])
    if comparison["type"] not in {"PP", "SBAR"} or len(tail) != 2:
        return None
    if tail[0].get("surface", "").casefold() != marker or tail[1]["type"] != "S":
        return None
    body = tail[1].get("children", [])
    if [part["type"] for part in body] != ["NP", "VP"]:
        return None
    predicate = body[1].get("children", [])
    if len(predicate) != 2 or predicate[0].get("surface", "").casefold() not in {"is", "are", "was", "were"}:
        return None
    adjective = predicate[1]
    if adjective["type"] != "ADJP":
        return None
    words = adjective.get("children", [])
    if len(words) != 2 or words[1].get("pos") != "JJ" or words[0]["type"] not in {"RB", "ADVP"}:
        return None
    modifier = list(_ordered_leaves(words[0]))
    if len(modifier) == 1 and modifier[0]["surface"].casefold() in {"very", "quite"}:
        return governor, modifier[0]
    return None


def _conflicts(node):
    match = _degree_conflict(node)
    if match:
        yield match
    for child in node.get("children", []):
        yield from _conflicts(child)


def probe_comparative_gap(sentence, tree, *, variety):
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
    for governor, modifier in _conflicts(tree):
        result["candidates"].append({
            "rule_id": "CLS-1119", "source_chapter": 13, "source_pages": [1108],
            "relation": {"kind": "overt_modifier_in_comparative_degree_gap",
                         "governor_char_span": tokens[governor["span"][0]]["char_span"],
                         "modifier_char_span": tokens[modifier["span"][0]]["char_span"]},
            "edit_hint": None,
        })
    return result


def _subjectless_did_comparisons(node):
    parts = node.get("children", [])
    if node["type"] == "ADVP" and len(parts) == 2:
        governor, comparison = parts
        if governor["type"] == "ADVP" and len(governor.get("children", [])) == 1:
            governor = governor["children"][0]
        tail = comparison.get("children", [])
        if (governor.get("pos") == "RBR" and comparison["type"] in {"SBAR", "PP"}
                and len(tail) == 2 and tail[0].get("pos") == "IN"
                and tail[0]["surface"].casefold() == "than" and tail[1]["type"] == "S"):
            body = tail[1].get("children", [])
            if len(body) == 1 and body[0]["type"] == "VP":
                predicate = body[0].get("children", [])
                if len(predicate) == 2:
                    verb, time = predicate
                    if (verb.get("pos") == "VBD" and verb["surface"].casefold() == "did"
                            and time["type"] in {"NP", "ADVP"}
                            and tuple(leaf["surface"].casefold() for leaf in _ordered_leaves(time))
                            in {("last", "year"), ("last", "summer"), ("yesterday",)}):
                        yield tail[0], verb
    for child in parts:
        yield from _subjectless_did_comparisons(child)


def probe_comparative_subject(sentence, tree, *, variety):
    """Check retained did in narrow subjectless adverbial comparisons."""
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
    for marker, verb in _subjectless_did_comparisons(tree):
        result["candidates"].append({
            "rule_id": "CLS-1129", "source_chapter": 13, "source_pages": [1113],
            "relation": {"kind": "retained_verb_without_comparative_subject",
                         "marker_char_span": tokens[marker["span"][0]]["char_span"],
                         "verb_char_span": tokens[verb["span"][0]]["char_span"]},
            "edit_hint": None,
        })
    return result
