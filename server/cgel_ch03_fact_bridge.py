"""Ground Phase-C candidate auxiliaries in an observed canonical B-R fact graph.

This is an offline, non-authoritative adapter. It witnesses lexical token IDs,
constituent spans and overt category labels, but does NOT infer or license
governor/dependent grammatical functions. The explicit typed relations remain
unreviewed candidates, never student-visible grammar errors or applied edits.

Do not call this from the production Cambridge evaluator without separately
satisfying source review, B-R crosswalk, parser relation licensing, all guards,
and the existing runtime allow-list.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from .burton_roberts import validate_canonical_tree
    from .xai_facts import build_fact_graph
    from .cgel_ch03_candidate_probe import probe_ch03, tokens_with_spans
except ImportError:
    from burton_roberts import validate_canonical_tree
    from xai_facts import build_fact_graph
    from cgel_ch03_candidate_probe import probe_ch03, tokens_with_spans


# These are *observed B-R tree labels*, not a source-approved licensing table.
_ROLE_LABELS = {
    "central_modal": frozenset({"MOD"}),
    "lexical_verb": frozenset({"V", "V(I)", "V(II)"}),
    "supportive_do": frozenset({"AUX"}),
    "perfect_have": frozenset({"PERF"}),
    "progressive_be": frozenset({"PROG"}),
    "passive_be": frozenset({"PASS"}),
    "copular_be": frozenset({"V", "V(I)", "V(II)"}),
}
_ALLOWED_KINDS = {"modal_selects", "supportive_do_selects"}


def _base(blocked: list[Any], *, status: str = "not_evaluated") -> dict[str, Any]:
    return {
        "status": status,
        "authority": "CANONICAL_TOKEN_AND_LABEL_SHAPE_ONLY_ROLE_UNVERIFIED",
        "production_enabled": False,
        "whole_sentence_certified": False,
        "candidates": [],
        "blocked": blocked,
        "evidence_level": "observed_canonical_tree_not_grammatical_licensing",
        "role_licensing": "unverified",
    }


def _overt_label(node_id: Any, token_id: int, graph: dict[str, Any],
                 by_id: dict[str, dict[str, Any]], role: Any) -> str | None:
    """Require a real overt terminal below a visible B-R category for the role."""
    if not isinstance(role, str) or role not in _ROLE_LABELS:
        return None
    token = graph["token_index"][token_id]
    if token["opaque"] or not isinstance(node_id, str):
        return None
    if node_id != token["smallest_node_id"]:
        return None
    terminal = by_id.get(node_id)
    if not terminal or terminal["kind"] != "word" or terminal["token_span"] != [token_id, token_id + 1]:
        return None
    observed = [by_id[x]["label"] for x in token["node_ids_innermost_first"]
                if x in by_id and by_id[x]["kind"] == "branch"]
    return next((label for label in observed if label in _ROLE_LABELS[role]), None)


def _shared_vp(graph: dict[str, Any], by_id: dict[str, dict[str, Any]],
               governor: int, dependent: int) -> str | None:
    a = graph["token_index"][governor]
    b = graph["token_index"][dependent]
    if not a["clause_ancestor_id"] or a["clause_ancestor_id"] != b["clause_ancestor_id"]:
        return None
    common = set(a["node_ids_innermost_first"]) & set(b["node_ids_innermost_first"])
    candidates = [
        by_id[x] for x in common if x in by_id
        and by_id[x]["label"] == "VP" and by_id[x]["kind"] == "branch"
        and by_id[x]["token_span"] is not None
    ]
    if not candidates:
        return None
    # Innermost overt VP covering both tokens is the strongest shape evidence.
    candidates.sort(key=lambda node: (node["token_span"][1] - node["token_span"][0],
                                       node["path"]))
    return candidates[0]["node_id"]


def probe_ch03_on_canonical(analysis: Any, typed_facts: Any, *,
                            variety: str | None, root: Path | None = None) -> dict[str, Any]:
    """Ground typed candidate relations in an actually validated canonical tree.

    The typed envelope MUST bind to this exact tree_id and computed analysis_id;
    each relation MUST bind to both overt terminal node IDs. Category labels,
    spans and shared overt VP are checked independently against the graph.
    Selection semantics are **not** licensed by these shape checks.
    """
    if not isinstance(analysis, dict) or analysis.get("status") != "normalized":
        return _base(["normalized_canonical_analysis_required"])
    tree = analysis.get("tree")
    validated = validate_canonical_tree(tree)
    if not validated.get("valid"):
        return _base(["invalid_canonical_tree"])
    if not isinstance(tree, dict) or not isinstance(tree.get("sentence"), str):
        return _base(["canonical_sentence_required"])
    sentence = tree["sentence"]
    if not sentence.strip():
        return _base(["canonical_sentence_required"])
    if tree.get("accepted_alternatives"):
        return _base(["alternative_analysis_unresolved"])
    graph = build_fact_graph(analysis)
    if graph["status"] != "observed":
        return _base(["canonical_facts_provisional"])
    if not isinstance(typed_facts, dict) or typed_facts.get("status") != "typed_candidate":
        return _base(["typed_candidate_facts_required"])
    if (typed_facts.get("tree_id") != graph["tree_id"]
            or typed_facts.get("analysis_id") != graph["analysis_id"]
            or typed_facts.get("sentence") != sentence
            or not isinstance(typed_facts.get("relations"), list)):
        return _base(["candidate_provenance_mismatch"])
    canonical = tree["tokens"]
    visible = tokens_with_spans(sentence)
    if (len(canonical) != len(visible)
            or len(graph["token_index"]) != len(visible)
            or any(
                canonical[i].get("index") != i
                or canonical[i].get("text") != local["text"]
                or canonical[i].get("char_span") != local["char_span"]
                or graph["token_index"][i]["char_span"] != local["char_span"]
                for i, local in enumerate(visible)
            )):
        return _base(["canonical_tokenization_or_span_mismatch"])

    by_id = {node["node_id"]: node for node in graph["nodes"]}
    selected: list[dict[str, Any]] = []
    proof_by_pair: dict[tuple[int, int, str], dict[str, Any]] = {}
    blocked: list[dict[str, Any]] = []
    for i, rel in enumerate(typed_facts["relations"]):
        if not isinstance(rel, dict):
            blocked.append({"relation_index": i, "reason": "unusable_relation"})
            continue
        a, b = rel.get("governor"), rel.get("dependent")
        if (type(a) is not int or type(b) is not int
                or a < 0 or b < 0 or a >= len(visible) or b >= len(visible) or a == b
                or not isinstance(rel.get("kind"), str)
                or rel["kind"] not in _ALLOWED_KINDS
                or not isinstance(rel.get("clause_kind"), str)):
            blocked.append({"relation_index": i, "reason": "unusable_relation"})
            continue
        glabel = _overt_label(rel.get("governor_node_id"), a, graph, by_id,
                             rel.get("governor_role"))
        dlabel = _overt_label(rel.get("dependent_node_id"), b, graph, by_id,
                             rel.get("dependent_role"))
        if glabel is None or dlabel is None:
            blocked.append({"relation_index": i, "reason": "opaque_or_unmatched_lexical_category"})
            continue
        vp = _shared_vp(graph, by_id, a, b)
        if vp is None:
            blocked.append({"relation_index": i, "reason": "no_shared_overt_vp_in_same_clause"})
            continue
        # Rely on the existing candidate-checker for semantic fallbacks.
        # Do not attempt to infer selection from token adjacency or a VP label.
        key = (a, b, rel["kind"])
        proof_by_pair[key] = {
            "analysis_id": graph["analysis_id"],
            "tree_id": graph["tree_id"],
            "governor_node_id": rel["governor_node_id"],
            "dependent_node_id": rel["dependent_node_id"],
            "governor_observed_label": glabel,
            "dependent_observed_label": dlabel,
            "shared_vp_node_id": vp,
            "shared_clause_node_id": graph["token_index"][a]["clause_ancestor_id"],
            "head_and_selection_licensed": False,
            "proof_level": "visible_canonical_token_and_constituent_shape",
        }
        selected.append(rel)

    unverified = probe_ch03(
        sentence,
        {"status": "typed_candidate", "sentence": sentence, "relations": selected},
        variety=variety, root=root,
    )
    if unverified["status"] == "not_evaluated":
        return {**_base(blocked + unverified["blocked"]),
                "status": "not_evaluated",
                "analysis_id": graph["analysis_id"],
                "tree_id": graph["tree_id"]}
    candidates = []
    for candidate in unverified["candidates"]:
        relation = candidate["relation"]
        key = (relation["governor_token_index"],
               relation["dependent_token_index"], relation["kind"])
        proof = proof_by_pair.get(key)
        if proof is None:
            continue
        candidates.append({
            **candidate,
            "grounding": proof,
            "status": "tree_bound_relation_unverified",
        })
    return {
        **_base(blocked + unverified["blocked"], status="candidate_only"),
        "analysis_id": graph["analysis_id"],
        "tree_id": graph["tree_id"],
        "candidates": candidates,
    }
