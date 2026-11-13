"""Offline CLS-130 candidate requiring independently supplied directive intent."""

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .cgel_modal_parser_probe import _plain_form_for_mistagged_3sg
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from cgel_modal_parser_probe import _plain_form_for_mistagged_3sg
    from parse_engine import _ordered_leaves


def probe_imperative(sentence, tree, *, variety, directive_confirmed=False):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": [], "blocked": []}
    if variety != "standard_english" or directive_confirmed is not True:
        return {**result, "blocked": ["standard_english_and_directive_intent_required"]}
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ):
        return {**result, "blocked": ["parser_token_alignment_unavailable"]}
    if any(token["text"] in {'"', '“', '”', "'", "‘", "’"} for token in tokens):
        return {**result, "blocked": ["quotation_scope_unresolved"]}

    children = tree.get("children", [])
    if (tree["type"] != "S" or len(children) != 3 or children[0]["type"] != "NP"
            or children[1]["type"] != "VP" or children[2].get("surface") not in {".", "!"}):
        return {**result, "blocked": ["simple_overt_subject_directive_required"]}
    parts = children[1].get("children", [])
    result["status"] = "candidate_only"
    if not parts or any(part["type"] in {"CC", "CONJP"} for part in parts):
        return result
    head = parts[0]
    if head.get("pos") not in {"VB", "VBZ"}:
        return result
    word = head["surface"]
    plain = _plain_form_for_mistagged_3sg(word.casefold())
    if plain and word.islower():
        index = head["span"][0]
        span = tokens[index]["char_span"]
        result["candidates"].append({
            "rule_id": "CLS-130", "source_chapter": 10, "source_pages": [857],
            "relation": {"kind": "directive_predicate", "dependent_token_index": index,
                         "dependent_char_span": span},
            "edit_hint": {"char_span": span, "replacement": plain,
                          "requires_reparse": True, "safe_to_apply_automatically": False},
        })
    return result
