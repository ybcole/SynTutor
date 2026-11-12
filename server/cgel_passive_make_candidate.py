"""Offline Phase C probe for the missing infinitival marker after passive make."""

import json

if __package__:
    from .cgel_ch03_candidate_probe import ROOT, tokens_with_spans
    from .parse_engine import _ordered_leaves
else:
    from cgel_ch03_candidate_probe import ROOT, tokens_with_spans
    from parse_engine import _ordered_leaves


RULE_ID = "CLS-357"
SUPPORT_ID = "CLS-1451"
BE_FORMS = frozenset({"am", "is", "are", "was", "were", "be", "being", "been"})


def _passive_modifiers(middle, tail):
    """Permit only explicit negation and an attached by-phrase."""
    match middle:
        case []:
            pass
        case [{"pos": "RB", "surface": word}] if word.casefold() == "not":
            pass
        case [{"type": "ADVP", "children": [{"pos": "RB", "surface": word}]}] if word.casefold() == "not":
            pass
        case _:
            return False
    match tail:
        case []:
            return True
        case [{"type": "PP", "children": [{"pos": "IN", "surface": word}, {"type": "NP"}]}] if word.casefold() == "by":
            return True
        case _:
            return False


def _passive_relations(node):
    """Recognize a be-passive and its immediately selected bare VP."""
    children = node.get("children", [])
    match node:
        case {
            "type": "VP",
            "children": [
                {"pos": "VB" | "VBD" | "VBG" | "VBN" | "VBP" | "VBZ", "surface": be} as auxiliary,
                *middle,
                {"type": "VP", "children": [{"pos": "VBN", "surface": made} as make, complement, *tail]},
            ],
        } if (
            be.casefold() in BE_FORMS and made.casefold() == "made"
            and _passive_modifiers(middle, tail)
        ):
            if complement["type"] == "S" and len(complement.get("children", [])) == 1:
                complement = complement["children"][0]
            match complement:
                case {"type": "VP", "children": [{"pos": "VB"} as head, *rest]}:
                    if all(part["type"] not in {"CC", "CONJP"} for part in rest):
                        yield auxiliary, make, head
    for child in children:
        yield from _passive_relations(child)


def probe_passive_make(sentence, tree, *, variety):
    """Return candidate evidence and an unapplied edit, with exact source spans."""
    result = {"status": "candidate_only", "production_enabled": False, "candidates": []}
    if variety != "standard_english":
        return {**result, "status": "not_evaluated", "reason": "explicit_standard_variety_required"}

    tokens = tokens_with_spans(sentence)
    leaves = list(_ordered_leaves(tree))
    if len(tokens) != len(leaves) or any(
        leaf["span"] != [token["index"], token["index"] + 1]
        or leaf["surface"] != token["text"]
        for leaf, token in zip(leaves, tokens)
    ):
        return {**result, "status": "not_evaluated", "reason": "parser_token_alignment_unavailable"}

    # A narrow first pass leaves quoted and metalinguistic readings for later.
    if any(token["text"] in {'"', '“', '”', "'", "‘", "’"} for token in tokens):
        return {**result, "status": "not_evaluated", "reason": "quotation_scope_unresolved"}

    seen = set()
    for auxiliary, make, verb in _passive_relations(tree):
        auxiliary_i, make_i, verb_i = (leaf["span"][0] for leaf in (auxiliary, make, verb))
        if verb_i != make_i + 1 or (make_i, verb_i) in seen:
            continue
        seen.add((make_i, verb_i))
        make_span = tokens[make_i]["char_span"]
        verb_span = tokens[verb_i]["char_span"]
        start = verb_span[0]
        result["candidates"].append({
            "rule_id": RULE_ID,
            "supporting_rule_ids": [SUPPORT_ID],
            "relation": {
                "kind": "passive_causative_make_selects",
                "passive_auxiliary_token_index": auxiliary_i,
                "passive_auxiliary_char_span": tokens[auxiliary_i]["char_span"],
                "governor_token_index": make_i,
                "dependent_token_index": verb_i,
                "governor_char_span": make_span,
                "dependent_char_span": verb_span,
            },
            "token_span": [make_i, verb_i + 1],
            "char_span": [make_span[0], verb_span[1]],
            "edit_hint": {
                "char_span": [start, start],
                "replacement": "to ",
                "requires_reparse": True,
                "safe_to_apply_automatically": False,
            },
        })

    if result["candidates"]:
        records = json.loads((ROOT / "grammar/rules/clauses.json").read_text(encoding="utf-8"))
        rules = {rule["id"]: rule for rule in records if rule["id"] in {RULE_ID, SUPPORT_ID}}
        primary = rules[RULE_ID]
        sources = primary["sources"] + rules[SUPPORT_ID]["sources"]
        for candidate in result["candidates"]:
            candidate["sources"] = sources
            candidate["variety_scope"] = primary["diagnostic"]["variety_scope"]
            candidate["provisional_explanation"] = primary["diagnostic"]["learner_explanation"]
    return result
