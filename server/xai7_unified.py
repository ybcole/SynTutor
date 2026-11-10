"""XAI-7: shared read-only evidence/navigation contract for every learning mode.

This adapter extracts UI focus from server-witnessed XAI-2 tree positions,
separates actual approved XAI-5 violations from *unapproved* raw-token
observations, and preserves the existing B-R/Cambridge evidence channels.

It never licenses linguistic functions, overrides grammar decisions or accepts
client-written source-review metadata. Quiz mode has no fact graph and does not
manufacture one; it shares the same envelope with an explicit unavailable tree.
"""
from __future__ import annotations

from typing import Any

VERSION = "xai7-evidence-1.0.0"


def assemble(evidence: dict[str, Any], *, mode: str = "tree") -> dict[str, Any]:
    if mode not in {"tree", "quiz"} or not isinstance(evidence, dict):
        raise ValueError("XAI-7 requires a server evidence object and known mode")
    graph = evidence.get("fact_graph")
    context = evidence.get("contextual_explanations")
    issue = evidence.get("xai5_localization")
    selected = graph.get("target") if isinstance(graph, dict) else None
    nodes = graph.get("nodes", []) if isinstance(graph, dict) else []
    ids = {row["node_id"] for row in nodes}
    by_id = {row["node_id"]: row for row in nodes}
    if selected and selected["node_id"] not in ids:
        selected = None
    resolved = graph.get("status") if isinstance(graph, dict) else "unavailable"
    if resolved not in {"observed", "provisional"}:
        resolved = "unavailable"
        selected = None

    focus = []
    def add(node_id: str | None, reason: str, *, verified: bool = False):
        if node_id in ids and not any(row["node_id"] == node_id and row["reason"] == reason
                                       for row in focus):
            focus.append({"node_id": node_id, "reason": reason,
                          "relation_authority": ("approved_rule" if verified
                                                 else "witnessed_tree_position")})

    features = []
    issues = []
    if selected:
        add(selected["node_id"], "selected")
        add(selected.get("parent_id"), "parent")
        for sibling in selected.get("sibling_ids", []):
            add(sibling, "sibling")
        features = [
            {"node_id": selected["node_id"], "feature": feature,
             "status": "observed_label_not_a_verified_function"}
            for feature in selected.get("features", [])
        ]
        if isinstance(issue, dict):
            for diagnosis in issue.get("diagnoses", []):
                locs = [diagnosis.get("governor_location") or {},
                        diagnosis.get("target_location") or {}]
                target_id = selected["node_id"]
                if not any(x.get("node_id") == target_id or
                           target_id in x.get("ancestor_node_ids", []) for x in locs):
                    continue
                # XAI-5 'diagnoses' only exist for approved rule violations.
                gov, other = locs
                add(gov.get("node_id"), "approved_governor", verified=True)
                add(other.get("node_id"), "approved_affected", verified=True)
                issues.append({
                    "finding_id": diagnosis["finding_id"],
                    "rule_id": diagnosis["rule_id"],
                    "governor_node_id": gov.get("node_id") if gov.get("node_id") in ids else None,
                    "affected_node_id": other.get("node_id") if other.get("node_id") in ids else None,
                    "affected_char_span": list(diagnosis["char_span"]),
                    "status": "verified_local_violation",
                })

    channels = evidence.get("channels", {})
    if not isinstance(channels, dict):
        channels = {}
    citations = []
    for channel in ("structural", "grammatical", "remediation"):
        for record in channels.get(channel, []):
            for source in record.get("sources", []):
                # These records were filtered by explanations.py's independent
                # source/template review gate. We only carry grounded fields.
                if not isinstance(source, dict) or source.get("printed_page") is None:
                    continue
                entry = {
                    "channel": channel,
                    "source_id": source.get("id"),
                    "book": source.get("book"),
                    "title": source.get("title"),
                    "edition": source.get("edition"),
                    "printed_page": source.get("printed_page"),
                    "node_id": record.get("node_id"),
                }
                if entry not in citations:
                    citations.append(entry)
    return {
        "schema_version": VERSION,
        "language_policy": "ENGLISH_ONLY",
        "mode": mode,
        "analysis_id": graph.get("analysis_id") if isinstance(graph, dict) else None,
        "tree_status": resolved,
        "selected_node_id": selected["node_id"] if selected else None,
        "focus": focus,
        "feature_rows": features,
        "verified_issues": issues,
        "citations": citations,
        "contextual_status": (context.get("status", "unavailable")
                              if isinstance(context, dict) else "unavailable"),
        "book_status": evidence.get("status", "NO_BOOK_BASIS"),
        "claim_boundary": "observations_do_not_create_new_functions_or_grammar_verdicts",
        "whole_sentence_certified": False,
    }
