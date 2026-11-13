"""Offline lexical-number agreement evidence for simple subject–predicate frames."""

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from parse_engine import _ordered_leaves


LEXICAL_NUMBER = {
    "cattle": ("PHR-062", 345, False),
    "police": ("PHR-062", 345, False),
    "news": ("PHR-065", 346, True),
    "shingles": ("PHR-065", 346, True),
    **{noun: ("PHR-347", 504, True) for noun in ("crockery", "furniture", "luggage", "equipment")},
}
FORMS = {"is": ("is", "are"), "are": ("is", "are"),
         "was": ("was", "were"), "were": ("was", "were"),
         "has": ("has", "have"), "have": ("has", "have")}


def probe_lexical_number(sentence, tree, *, variety, disease_confirmed=False):
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
    children = tree.get("children", [])
    if tree["type"] != "S" or [child["type"] for child in children] != ["NP", "VP", "."]:
        return result
    subject = list(_ordered_leaves(children[0]))
    predicate = children[1].get("children", [])
    if len(subject) == 2 and subject[0].get("pos") == "DT" and subject[0]["surface"].casefold() == "the":
        subject = subject[1:]
    if len(subject) != 1 or subject[0].get("pos") not in {"NN", "NNS"} or not predicate:
        return result
    noun, verb = subject[0], predicate[0]
    word = noun["surface"].casefold()
    if word not in LEXICAL_NUMBER or (word == "shingles" and disease_confirmed is not True):
        return result
    if verb.get("pos") not in {"VBZ", "VBP", "VBD"}:
        return result
    form = verb["surface"].casefold()
    if form not in FORMS:
        return result
    rule, page, singular = LEXICAL_NUMBER[word]
    expected = FORMS[form][0 if singular else 1]
    if form != expected:
        result["candidates"].append({
            "rule_id": rule, "source_chapter": 5, "source_pages": [page],
            "relation": {"kind": "lexical_subject_number_agreement",
                         "subject_char_span": tokens[noun["span"][0]]["char_span"],
                         "verb_char_span": tokens[verb["span"][0]]["char_span"]},
            "expected_verb": expected, "edit_hint": None,
        })
    return result


# Restrict the pilot to ordinary count nouns with distinct number forms.
COUNT_NUMBER = {
    "book": True, "books": False, "folder": True, "folders": False,
    "chair": True, "chairs": False, "bottle": True, "bottles": False,
    "child": True, "children": False,
}
DEMONSTRATIVE_NUMBER = {"this": True, "that": True, "these": False, "those": False}


def _demonstrative_pairs(node):
    children = node.get("children", [])
    if node["type"] == "NP" and len(children) == 2:
        determiner, noun = children
        if determiner.get("pos") == "DT" and noun.get("pos") in {"NN", "NNS"}:
            yield determiner, noun
    for child in children:
        yield from _demonstrative_pairs(child)


def probe_demonstrative_number(sentence, tree, *, variety):
    """Report an NP-internal mismatch without assuming the intended number."""
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
    for determiner, noun in _demonstrative_pairs(tree):
        det_number = DEMONSTRATIVE_NUMBER.get(determiner["surface"].casefold())
        noun_number = COUNT_NUMBER.get(noun["surface"].casefold())
        if det_number is None or noun_number is None or det_number == noun_number:
            continue
        result["candidates"].append({
            "rule_id": "PHR-087", "source_chapter": 5, "source_pages": [352, 353],
            "relation": {
                "kind": "demonstrative_head_number_mismatch",
                "determiner_char_span": tokens[determiner["span"][0]]["char_span"],
                "head_char_span": tokens[noun["span"][0]]["char_span"],
            },
            "edit_hint": None,
        })
    return result


def probe_total_number(sentence, tree, *, variety):
    """Check finite agreement with a simple subject headed by the number."""
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
    children = tree.get("children", [])
    if tree["type"] != "S" or [node["type"] for node in children] != ["NP", "VP", "."]:
        return result
    parts = children[0].get("children", [])
    if len(parts) == 2 and parts[0]["type"] == "NP":
        parts = [*parts[0].get("children", []), parts[1]]
    if len(parts) != 3:
        return result
    det, noun, phrase = parts
    if (det.get("pos") != "DT" or det["surface"].casefold() != "the"
            or noun.get("pos") != "NN" or noun["surface"].casefold() != "number"
            or phrase["type"] != "PP"):
        return result
    pp = phrase.get("children", [])
    if (len(pp) != 2 or pp[0].get("pos") != "IN" or pp[0]["surface"].casefold() != "of"
            or pp[1]["type"] != "NP"):
        return result
    vp = children[1].get("children", [])
    if not vp or vp[0].get("pos") not in {"VBP", "VBZ", "VBD"}:
        return result
    verb = vp[0]
    form = verb["surface"].casefold()
    if form in {"are", "were", "have"}:
        result["candidates"].append({
            "rule_id": "PHR-079", "source_chapter": 5, "source_pages": [350],
            "relation": {"kind": "total_number_subject_agreement",
                         "subject_head_char_span": tokens[noun["span"][0]]["char_span"],
                         "verb_char_span": tokens[verb["span"][0]]["char_span"]},
            "expected_verb": FORMS[form][0], "edit_hint": None,
        })
    return result


def probe_singular_they_agreement(sentence, tree, *, variety, singular_reference_confirmed=False):
    """Check finite be/have forms where singular reference is supplied externally."""
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english" or singular_reference_confirmed is not True:
        return result
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ) or any(token["text"] in {'"', '“', '”', "'", '‘', '’'} for token in tokens):
        return result
    result["status"] = "candidate_only"
    children = tree.get("children", [])
    if tree["type"] != "S" or [node["type"] for node in children] != ["NP", "VP", "."]:
        return result
    subject = list(_ordered_leaves(children[0]))
    predicate = children[1].get("children", [])
    if (len(subject) != 1 or subject[0].get("pos") != "PRP"
            or subject[0]["surface"].casefold() != "they" or not predicate):
        return result
    verb = predicate[0]
    form = verb.get("surface", "").casefold()
    if verb.get("pos") not in {"VBD", "VBP", "VBZ"} or form not in {"is", "was", "has"}:
        return result
    result["candidates"].append({
        "rule_id": "PHR-334", "source_chapter": 5, "source_pages": [493, 494],
        "relation": {"kind": "finite_agreement_with_singular_they",
                     "subject_char_span": tokens[subject[0]["span"][0]]["char_span"],
                     "verb_char_span": tokens[verb["span"][0]]["char_span"]},
        "expected_verb": FORMS[form][1], "edit_hint": None,
    })
    return result
