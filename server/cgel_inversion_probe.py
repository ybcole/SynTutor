"""Offline main-clause question inversion evidence for CLS-103 and CLS-104."""

if __package__:
    from .cgel_ch03_candidate_probe import MODALS, tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import MODALS, tokens_with_spans
    from parse_engine import _ordered_leaves


def _uninverted_clause(tree, question_kind):
    parts = tree.get("children", [])
    if not parts or parts[-1].get("surface") != "?":
        return None
    if question_kind == "polar" and tree["type"] == "S":
        body = parts[:-1]
    elif question_kind == "non_subject_wh" and tree["type"] in {"SBARQ", "SBAR"}:
        if len(parts) != 3 or parts[0]["type"] not in {"WHNP", "WHADVP", "WHPP"} or parts[1]["type"] != "S":
            return None
        body = parts[1].get("children", [])
    else:
        return None
    if [node["type"] for node in body] != ["NP", "VP"]:
        return None
    subject, predicate = body
    vp = predicate.get("children", [])
    if not vp or any(node["type"] in {"CC", "CONJP"} for node in vp):
        return None
    verb = vp[0]
    if verb.get("pos") not in {"VBD", "VBP", "VBZ"} and not (
        verb.get("pos") == "MD" and verb["surface"].casefold() in MODALS
    ):
        return None
    return subject, verb


def probe_inversion(sentence, tree, *, variety, question_kind=None):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": [], "blocked": []}
    if variety != "standard_english" or question_kind not in {"polar", "non_subject_wh"}:
        return {**result, "blocked": ["canonical_direct_question_context_required"]}
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ):
        return {**result, "blocked": ["parser_token_alignment_unavailable"]}
    if any(token["text"] in {'"', '“', '”', "'", "‘", "’"} for token in tokens):
        return {**result, "blocked": ["quotation_scope_unresolved"]}
    result["status"] = "candidate_only"
    match = _uninverted_clause(tree, question_kind)
    if match is not None:
        subject, verb = match
        start, end = subject["span"]
        index = verb["span"][0]
        polar = question_kind == "polar"
        result["candidates"].append({
            "rule_id": "CLS-103" if polar else "CLS-104",
            "source_chapter": 3, "source_pages": [94, 95] if polar else [95],
            "relation": {
                "kind": "subject_precedes_finite_verb_in_direct_question",
                "subject_char_span": [tokens[start]["char_span"][0], tokens[end - 1]["char_span"][1]],
                "verb_char_span": tokens[index]["char_span"],
            },
            "edit_hint": None,
        })
    return result
