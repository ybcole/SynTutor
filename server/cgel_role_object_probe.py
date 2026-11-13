"""Offline COMP-087 probe for unambiguous bare role objects."""

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from parse_engine import _ordered_leaves


ROLE_NOUNS = {"treasurer", "secretary", "chairperson", "director", "president"}
OBJECT_VERBS = {"question", "questions", "questioned", "dismiss", "dismisses", "dismissed",
                "interview", "interviews", "interviewed", "contact", "contacts", "contacted"}


def _role_objects(node):
    parts = node.get("children", [])
    if node["type"] == "VP" and len(parts) == 2:
        verb, obj = parts
        if verb.get("pos") in {"VB", "VBP", "VBZ", "VBD", "VBN", "VBG"} and (
            verb["surface"].casefold() in OBJECT_VERBS and obj["type"] == "NP"
        ):
            nouns = list(_ordered_leaves(obj))
            if len(nouns) == 1 and nouns[0].get("pos") == "NN" and nouns[0]["surface"] in ROLE_NOUNS:
                yield verb["span"][0], nouns[0]["span"][0]
    for child in parts:
        yield from _role_objects(child)


def probe_role_object(sentence, tree, *, variety):
    result = {"status": "candidate_only", "production_enabled": False, "candidates": [], "blocked": []}
    if variety != "standard_english":
        return {**result, "status": "not_evaluated", "blocked": ["explicit_standard_english_required"]}
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ):
        return {**result, "status": "not_evaluated", "blocked": ["parser_token_alignment_unavailable"]}
    if any(token["text"] in {'"', '“', '”', "'", "‘", "’"} for token in tokens):
        return {**result, "status": "not_evaluated", "blocked": ["quotation_scope_unresolved"]}
    for verb, noun in _role_objects(tree):
        result["candidates"].append({
            "rule_id": "COMP-087", "source_chapter": 4, "source_pages": [253],
            "supporting_sources": [{"rule_id": "PHR-197", "chapter": 5, "pages": [409]}],
            "relation": {
                "kind": "verb_selects_referential_object",
                "governor_char_span": tokens[verb]["char_span"],
                "dependent_char_span": tokens[noun]["char_span"],
            },
            "provisional_explanation": "A singular count noun used as a referential object needs a determiner.",
            "edit_hint": None,
        })
    return result
