"""Offline imperative candidates requiring independently supplied directive intent."""

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .cgel_modal_parser_probe import _plain_form_for_mistagged_3sg
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from cgel_modal_parser_probe import _plain_form_for_mistagged_3sg
    from parse_engine import _ordered_leaves


def _directive_context(sentence, tree, variety, directive_confirmed):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": [], "blocked": []}
    if variety != "standard_english" or directive_confirmed is not True:
        return {**result, "blocked": ["standard_english_and_directive_intent_required"]}, None
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ):
        return {**result, "blocked": ["parser_token_alignment_unavailable"]}, None
    if any(token["text"] in {'"', '“', '”', "'", "‘", "’"} for token in tokens):
        return {**result, "blocked": ["quotation_scope_unresolved"]}, None

    return result, tokens


def probe_imperative(sentence, tree, *, variety, directive_confirmed=False):
    result, tokens = _directive_context(sentence, tree, variety, directive_confirmed)
    if tokens is None:
        return result

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

def probe_negative_imperative(sentence, tree, *, variety, ordinary_verbal_directive_confirmed=False):
    """Check subjectless ordinary be imperatives with integrated verbal not."""
    result, tokens = _directive_context(sentence, tree, variety, ordinary_verbal_directive_confirmed)
    if tokens is None:
        return result
    children = tree.get("children", [])
    if tree["type"] != "S" or len(children) != 2 or children[-1].get("surface") not in {".", "!"}:
        return result
    predicate = children[0]
    if predicate["type"] != "VP":
        return result
    result["status"] = "candidate_only"
    parts = predicate.get("children", [])
    if len(parts) < 2 or any(part["type"] in {"CC", "CONJP"} for part in parts):
        return result
    first, second = parts[:2]
    # In pre-verbal order the parser may group be and its complement in a VP.
    first_is_not = first.get("pos") == "RB" and first["surface"].casefold() == "not"
    verb, negation = (second, first) if first_is_not else (first, second)
    if first_is_not and verb["type"] == "VP":
        lower = verb.get("children", [])
        if not lower:
            return result
        verb = lower[0]
    if (verb.get("pos") != "VB" or verb["surface"].casefold() != "be"
            or negation.get("pos") != "RB" or negation["surface"].casefold() != "not"):
        return result
    verb_index, negation_index = verb["span"][0], negation["span"][0]
    start, end = sorted((verb_index, negation_index))
    if start != 0 or end != 1:
        return result
    # The supplied directive context must exclude literary Be not and constituent negation.
    result["candidates"].append({
        "rule_id": "CLS-102", "supporting_rule_ids": ["CLS-131"],
        "source_chapter": 3, "source_pages": [94],
        "supporting_sources": [{"rule_id": "CLS-131", "chapter": 10, "pages": [857]}],
        "relation": {"kind": "negative_imperative_missing_do",
                     "verb_char_span": tokens[verb_index]["char_span"],
                     "negation_char_span": tokens[negation_index]["char_span"]},
        "edit_hint": {"char_span": [tokens[start]["char_span"][0], tokens[end]["char_span"][1]],
                      "replacement": "Do not be" if tokens[start]["text"][0].isupper() else "do not be",
                      "requires_reparse": True, "safe_to_apply_automatically": False},
    })
    return result
