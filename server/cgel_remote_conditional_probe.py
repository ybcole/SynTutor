"""Offline CLS-119 evidence for a confirmed remote conditional."""

if __package__:
    from .cgel_ch03_candidate_probe import tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import tokens_with_spans
    from parse_engine import _ordered_leaves


def probe_remote_conditional(sentence, tree, *, variety, remote_confirmed=False):
    result = {"status": "not_evaluated", "production_enabled": False, "candidates": []}
    if variety != "standard_english" or remote_confirmed is not True:
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
    if tree["type"] != "S" or [node["type"] for node in parts] != ["SBAR", ",", "NP", "VP", "."]:
        return result
    conditional = parts[0].get("children", [])
    if (len(conditional) != 2 or conditional[0].get("pos") != "IN"
            or conditional[0]["surface"].casefold() != "if" or conditional[1]["type"] != "S"):
        return result
    antecedent = conditional[1].get("children", [])
    if [node["type"] for node in antecedent] != ["NP", "VP"]:
        return result
    condition_vp = antecedent[1].get("children", [])
    consequence_vp = parts[3].get("children", [])
    if not condition_vp or not consequence_vp:
        return result
    antecedent_verb, consequence_verb = condition_vp[0], consequence_vp[0]
    if antecedent_verb.get("pos") != "VBD" or consequence_verb.get("pos") != "VBD":
        return result
    if any(node["type"] in {"CC", "CONJP"} for node in consequence_vp):
        return result
    result["candidates"].append({
        "rule_id": "CLS-119", "source_chapter": 3, "source_pages": [107],
        "relation": {
            "kind": "remote_conditional_consequence_missing_modal",
            "condition_verb_char_span": tokens[antecedent_verb["span"][0]]["char_span"],
            "consequence_verb_char_span": tokens[consequence_verb["span"][0]]["char_span"],
        },
        "edit_hint": None,
    })
    return result
