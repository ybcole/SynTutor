"""Offline case evidence for simple active declaratives."""

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from parse_engine import _ordered_leaves


SUBJECT_FORMS = {"me": "I", "him": "he", "her": "she", "us": "we", "them": "they"}
OBJECT_FORMS = {"i": "me", "he": "him", "she": "her", "we": "us", "they": "them"}
# Narrow lexical frames with a single direct object and no predicative complement.
TRANSITIVE_FORMS = {"admire", "admires", "admired", "greet", "greets", "greeted",
                    "thank", "thanks", "thanked", "notice", "notices", "noticed"}


def probe_pronoun_case(sentence, tree, *, variety):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english":
        return result
    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1] or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ):
        return result
    result["status"] = "candidate_only"
    parts = tree.get("children", [])
    if tree["type"] != "S" or [node["type"] for node in parts] != ["NP", "VP", "."]:
        return result
    if parts[-1].get("surface") != ".":
        return result
    predicate = parts[1].get("children", [])
    if len(predicate) != 2:
        return result
    verb, obj = predicate
    if (verb.get("pos") not in {"VBD", "VBP", "VBZ"} or obj["type"] != "NP"
            or verb["surface"].casefold() not in TRANSITIVE_FORMS):
        return result
    for node, role, forms in [(parts[0], "subject", SUBJECT_FORMS), (obj, "direct_object", OBJECT_FORMS)]:
        pronouns = list(_ordered_leaves(node))
        if len(pronouns) != 1 or pronouns[0].get("pos") != "PRP":
            continue
        pronoun = pronouns[0]
        expected = forms.get(pronoun["surface"].casefold())
        if expected is None:
            continue
        span = tokens[pronoun["span"][0]]["char_span"]
        result["candidates"].append({
            "rule_id": "COMP-084", "source_chapter": 4, "source_pages": [237],
            "supporting_sources": [{"rule_id": "PHR-283", "chapter": 5, "pages": [459]}] if role == "subject" else [],
            "relation": {"kind": role, "pronoun_char_span": span,
                         "verb_char_span": tokens[verb["span"][0]]["char_span"]},
            "expected_pronoun": expected, "edit_hint": None,
        })
    return result
