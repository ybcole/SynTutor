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


def probe_fronted_inversion(sentence, tree, *, variety, clause_scope_confirmed=False):
    """Check a narrow root pattern after clause-wide scope has been established."""
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": [], "blocked": []}
    if variety != "standard_english" or clause_scope_confirmed is not True:
        return {**result, "blocked": ["explicit_clause_scope_required"]}
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
    parts = tree.get("children", [])
    if tree["type"] != "S" or len(parts) != 4:
        return result
    adjunct, subject, predicate, punctuation = parts
    if (adjunct["type"] != "ADVP" or subject["type"] != "NP" or predicate["type"] != "VP"
            or punctuation.get("surface") not in {".", "!"}):
        return result
    start, end = adjunct["span"]
    trigger = tuple(token["lower"] for token in tokens[start:end])
    if trigger not in {("never",), ("nowhere",), ("not", "once"), ("only", "once"), ("only", "then")}:
        return result
    vp = predicate.get("children", [])
    if (not vp or vp[0].get("pos") not in {"VBD", "VBP", "VBZ", "MD"}
            or any(part["type"] in {"CC", "CONJP"} for part in vp)):
        return result
    only = trigger[0] == "only"
    result["candidates"].append({
        "rule_id": "CLS-107" if only else "CLS-106",
        "source_chapter": 3, "source_pages": [95, 96],
        "relation": {
            "kind": "subject_precedes_finite_verb_after_fronted_adjunct",
            "adjunct_char_span": [tokens[start]["char_span"][0], tokens[end - 1]["char_span"][1]],
            "subject_char_span": [tokens[subject["span"][0]]["char_span"][0],
                                  tokens[subject["span"][1] - 1]["char_span"][1]],
            "verb_char_span": tokens[vp[0]["span"][0]]["char_span"],
        },
        "edit_hint": None,
    })
    return result


def probe_declarative_polarity(sentence, tree, *, variety, simple_positive_question_confirmed=False):
    """Check temporal ever in a confirmed simple positive declarative question."""
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": [], "blocked": []}
    if variety != "standard_english" or simple_positive_question_confirmed is not True:
        return result
    parts = tree.get("children", [])
    if (tree["type"] != "S" or [p["type"] for p in parts] != ["NP", "VP", "."]
            or parts[-1].get("surface") != "?"):
        return result
    subject = list(_ordered_leaves(parts[0]))
    if len(subject) != 1 or subject[0].get("pos") != "PRP":
        return result
    tokens = tokens_with_spans(sentence)
    words = [token["lower"] for token in tokens]
    leaves = list(_ordered_leaves(tree))
    surfaces = [leaf["surface"].casefold().replace("’", "'") for leaf in leaves]
    if len(surfaces) > 2 and surfaces[1] in {"'ve", "'s"}:
        surfaces[:2] = ["".join(surfaces[:2])]
    if surfaces != words or not words or any(
        word in {"'", '"', "“", "”", "‘", "’"} for word in words
    ):
        return result
    result["status"] = "candidate_only"
    # Require an attested perfect head, and an immediate preverbal temporal ever.
    predicate = list(_ordered_leaves(parts[1]))
    if (len(predicate) < 3 or predicate[0].get("pos") not in {"VBP", "VBZ", "VBD"}
            or predicate[0]["surface"].casefold().replace("’", "'") not in {"have", "has", "had", "'ve", "'s"}
            or predicate[1].get("pos") != "RB" or predicate[1]["surface"].casefold() != "ever"
            or predicate[2].get("pos") != "VBN"):
        return result
    if any(leaf.get("pos") in {"CC", "JJS", "RBS"} or leaf["surface"].casefold() in
           {"not", "only", "never", "first", "last", "few", "hardly"} for leaf in predicate[2:]):
        return result
    item = tokens[words.index("ever")]
    result["candidates"].append({
        "rule_id": "CLS-171", "source_chapter": 10, "source_pages": [885],
        "relation": {"kind": "temporal_ever_in_positive_declarative_question",
                     "item_char_span": item["char_span"]},
        "edit_hint": None,
    })
    return result


def _indefinite_partitives(node):
    parts = node.get("children", [])
    if node["type"] == "WHNP" and len(parts) in {2, 3}:
        lead = list(_ordered_leaves(parts[0]))
        phrase = parts[-1]
        if (len(lead) == 1 and lead[0].get("pos") == "WDT"
                and lead[0]["surface"].casefold() == "which"
                and (len(parts) == 2 or parts[1].get("pos") == "CD")
                and phrase["type"] == "PP"):
            pp = phrase.get("children", [])
            if (len(pp) == 2 and pp[0].get("pos") == "IN"
                    and pp[0]["surface"].casefold() == "of" and pp[1]["type"] == "NP"):
                nominal = pp[1].get("children", [])
                if (len(nominal) == 2 and nominal[0].get("pos") == "DT"
                        and nominal[0]["surface"].casefold() in {"some", "any"}
                        and nominal[1].get("pos") in {"NN", "NNS"}):
                    yield lead[0], pp[1]
    for part in parts:
        yield from _indefinite_partitives(part)


def probe_which_partitive(sentence, tree, *, variety):
    """Find explicitly indefinite set complements inside a direct which-question."""
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english":
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
    if (tree["type"] != "SBARQ" or [part["type"] for part in parts] != ["WHNP", "SQ", "."]
            or parts[-1].get("surface") != "?"):
        return result
    for marker, nominal in _indefinite_partitives(parts[0]):
        start, end = nominal["span"]
        result["candidates"].append({
            "rule_id": "CLS-201", "source_chapter": 10, "source_pages": [903],
            "relation": {"kind": "indefinite_set_in_which_partitive",
                         "which_char_span": tokens[marker["span"][0]]["char_span"],
                         "set_char_span": [tokens[start]["char_span"][0], tokens[end - 1]["char_span"][1]]},
            "edit_hint": None,
        })
    return result
