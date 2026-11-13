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


def probe_inclusive_lets(sentence, tree, *, variety):
    """Require a parsed matrix pronoun before the contracted inclusive marker."""
    result = {"status": "candidate_only", "production_enabled": False, "candidates": [], "blocked": []}
    if variety != "standard_english":
        return {**result, "status": "not_evaluated", "blocked": ["explicit_standard_english_required"]}
    tokens = tokens_with_spans(sentence)
    if any(token["text"] in {'"', '“', '”', "'", "‘", "’"} for token in tokens):
        return {**result, "status": "not_evaluated", "blocked": ["quotation_scope_unresolved"]}
    if len(tokens) < 4 or tokens[0]["lower"] not in {"you", "we"} or tokens[1]["lower"] != "let's":
        return result
    parts = tree.get("children", [])
    if tree["type"] != "S" or [part["type"] for part in parts[:2]] != ["NP", "VP"]:
        return result
    subject = list(_ordered_leaves(parts[0]))
    predicate = list(_ordered_leaves(parts[1]))
    if (len(subject) != 1 or subject[0].get("pos") != "PRP"
            or subject[0]["surface"] != tokens[0]["text"] or subject[0]["span"] != [0, 1]
            or not predicate):
        return result
    if predicate[0]["surface"] == tokens[1]["text"]:
        marker_size = 1
    elif len(predicate) >= 2 and predicate[0]["surface"] + predicate[1]["surface"] == tokens[1]["text"]:
        marker_size = 2
    else:
        return result
    if len(predicate) <= marker_size or predicate[marker_size].get("pos") != "VB":
        return result
    # The contraction may occupy one source token and two parser leaves.
    expected = [token["text"] for token in tokens]
    surfaces = [leaf["surface"] for leaf in _ordered_leaves(tree)]
    if surfaces[:1] + ["".join(surfaces[1:1 + marker_size])] + surfaces[1 + marker_size:] != expected:
        return result
    result["candidates"].append({
        "rule_id": "CLS-268", "source_chapter": 10, "source_pages": [934, 935],
        "relation": {"kind": "overt_subject_before_inclusive_lets",
                     "subject_char_span": tokens[0]["char_span"],
                     "marker_char_span": tokens[1]["char_span"]},
        "edit_hint": None,
    })
    return result


def probe_reported_negative_directive(sentence, tree, *, variety):
    """Check a direct reported directive with an attested auxiliary-do shape."""
    result, tokens = _directive_context(sentence, tree, variety, True)
    if tokens is None:
        return result
    result["status"] = "candidate_only"
    root = tree.get("children", [])
    if tree["type"] != "S" or [part["type"] for part in root] != ["NP", "VP", "."]:
        return result
    parts = root[1].get("children", [])
    if len(parts) != 3:
        return result
    reporting, addressee, clause = parts
    if (reporting.get("pos") not in {"VB", "VBP", "VBZ", "VBD", "VBN"}
            or reporting["surface"].casefold() not in {"told", "asked", "ordered", "advised"}
            or addressee["type"] != "NP" or clause["type"] != "S"):
        return result
    embedded = clause.get("children", [])
    if len(embedded) != 1 or embedded[0]["type"] != "VP":
        return result
    leaves = list(_ordered_leaves(embedded[0]))
    if len(leaves) < 4:
        return result
    marker, auxiliary, negative = leaves[:3]
    if ([leaf["surface"].casefold() for leaf in leaves[:3]] != ["to", "do", "not"]
            or [leaf.get("pos") for leaf in leaves[:4]] != ["TO", "VB", "RB", "VB"]):
        return result
    start, end = marker["span"][0], negative["span"][0]
    result["candidates"].append({
        "rule_id": "CLS-270", "source_chapter": 10, "source_pages": [943, 944],
        "relation": {"kind": "reported_directive_with_imperative_do",
                     "reporting_verb_char_span": tokens[reporting["span"][0]]["char_span"],
                     "auxiliary_char_span": tokens[auxiliary["span"][0]]["char_span"]},
        "edit_hint": {"char_span": [tokens[start]["char_span"][0], tokens[end]["char_span"][1]],
                      "replacement": "not to", "requires_reparse": True,
                      "safe_to_apply_automatically": False},
    })
    return result
