"""Offline CLS-099 check for confirmed ordinary primary negation."""

from lemminflect import getInflection, getLemma

if __package__:
    from .cgel_ch03_candidate_probe import MODALS, SUPPORT_DO, tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import MODALS, SUPPORT_DO, tokens_with_spans
    from parse_engine import _ordered_leaves


def probe_primary_negation(sentence, tree, *, variety, primary_confirmed=False):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": [], "blocked": []}
    if variety != "standard_english" or primary_confirmed is not True:
        return {**result, "blocked": ["ordinary_primary_negation_context_required"]}
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
    children = tree.get("children", [])
    if tree["type"] != "S" or [node["type"] for node in children] != ["NP", "VP", "."]:
        return result
    if children[2].get("surface") != ".":
        return result
    predicate = children[1].get("children", [])
    if len(predicate) != 2:
        return result
    verb, negation = predicate
    negative_leaves = list(_ordered_leaves(negation))
    if negation["type"] not in {"RB", "ADVP"} or len(negative_leaves) != 1:
        return result
    if negative_leaves[0]["surface"] != "not":
        return result
    index = verb["span"][0]
    word = verb.get("surface", "")
    tag = verb.get("pos")
    auxiliary = {"am", "is", "are", "was", "were", "be", "has", "have", "had"}
    if (tag not in {"VBP", "VBZ", "VBD"} or not word.islower()
            or word in auxiliary | MODALS | SUPPORT_DO or negative_leaves[0]["span"][0] != index + 1):
        return result
    lemmas = getLemma(word, upos="VERB", lemmatize_oov=False)
    if len(lemmas) != 1 or word not in getInflection(lemmas[0], tag=tag, inflect_oov=False):
        return result
    auxiliary_form = {"VBP": "do", "VBZ": "does", "VBD": "did"}[tag]
    start = tokens[index]["char_span"][0]
    end = tokens[index + 1]["char_span"][1]
    result["candidates"].append({
        "rule_id": "CLS-099", "source_chapter": 3, "source_pages": [93, 94],
        "relation": {"kind": "finite_lexical_verb_followed_by_primary_not",
                     "verb_char_span": tokens[index]["char_span"],
                     "negation_char_span": tokens[index + 1]["char_span"]},
        "edit_hint": {"char_span": [start, end], "replacement": f"{auxiliary_form} not {lemmas[0]}",
                      "requires_reparse": True, "safe_to_apply_automatically": False},
    })
    return result
