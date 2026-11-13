"""Offline CLS-182 probe for simple affirmative anchors and negative tags."""

if __package__:
    from .cgel_ch03_candidate_probe import MODALS, tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import MODALS, tokens_with_spans
    from parse_engine import _ordered_leaves


DO_FORMS = {"do", "does", "did"}
# These modals keep their full spelling before n't.
MODAL_TAGS = {"could", "should", "would", "might", "must"}


def probe_tag_auxiliary(sentence, tree, *, variety):
    result = {"status": "candidate_only", "production_enabled": False, "candidates": []}
    if variety != "standard_english":
        return {**result, "status": "not_evaluated"}
    parts = tree.get("children", [])
    if (tree["type"] not in {"S", "SQ"} or len(parts) != 6 or parts[0]["type"] != "S"
            or parts[1].get("surface") != "," or parts[-1].get("surface") != "?"):
        return result
    anchor, _, tag, negation, tag_subject, _ = parts
    if negation.get("surface", "").replace("’", "'") != "n't" or tag_subject["type"] != "NP":
        return result
    subject_leaves = list(_ordered_leaves(tag_subject))
    body = anchor.get("children", [])
    if len(body) != 2 or [part["type"] for part in body] != ["NP", "VP"]:
        return result
    anchor_subject = list(_ordered_leaves(body[0]))
    if (len(anchor_subject) != 1 or len(subject_leaves) != 1
            or anchor_subject[0].get("pos") != "PRP" or subject_leaves[0].get("pos") != "PRP"
            or anchor_subject[0]["surface"].casefold() != subject_leaves[0]["surface"].casefold()):
        return result
    vp = body[1].get("children", [])
    if not vp or any(
        leaf["surface"].casefold() in {"not", "n't", "n’t", "never", "hardly", "scarcely", "rarely", "seldom"}
        for leaf in _ordered_leaves(anchor)
    ):
        return result
    head = vp[0]
    word = head.get("surface", "").casefold()
    if head.get("pos") == "MD" and word in MODALS and len(vp) == 2 and vp[1]["type"] == "VP":
        expected = word
    elif (head.get("pos") == "VBD" and word not in {"was", "were", "had", "did"}
          and len(vp) == 2 and vp[1]["type"] == "NP"
          and len(list(_ordered_leaves(vp[1]))) == 1
          and next(_ordered_leaves(vp[1])).get("pos") == "PRP"):
        expected = "did"
    else:
        return result

    observed = tag.get("surface", "").casefold()
    if observed not in DO_FORMS | MODAL_TAGS or observed == expected:
        return result
    tokens = tokens_with_spans(sentence)
    surfaces = [leaf["surface"] for leaf in _ordered_leaves(tree)]
    index = tag["span"][0]
    if surfaces[:index] + ["".join(surfaces[index:index + 2])] + surfaces[index + 2:] != [
        token["text"] for token in tokens
    ]:
        return result
    result["candidates"].append({
        "rule_id": "CLS-182", "source_chapter": 10, "source_pages": [892, 893],
        "relation": {"kind": "tag_auxiliary_matches_anchor",
                     "anchor_char_span": tokens[head["span"][0]]["char_span"],
                     "tag_char_span": tokens[index]["char_span"]},
        "expected_auxiliary": expected, "edit_hint": None,
    })
    return result
