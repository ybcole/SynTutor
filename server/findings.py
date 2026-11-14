"""Unified finding model for legacy and Cambridge candidate channels.

The purpose is coherence, not promotion: every item carries its authority and
claim status. Legacy findings remain legacy diagnostics; candidate findings
remain candidate-only.
"""
from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "unified-findings-1.0.0"


def build_unified_findings(details: dict[str, Any] | None,
                           candidate_xai: dict[str, Any] | None = None) -> dict[str, Any]:
    items = []
    for node_id, detail in (details or {}).items():
        if not isinstance(detail, dict) or detail.get("status") != "error":
            continue
        remediation = detail.get("remediation") or {}
        items.append({
            "finding_id": f"legacy:{node_id}",
            "authority": "legacy_matrix",
            "claim_status": "legacy_diagnostic_not_book_verified",
            "production_path": True,
            "book_verified": False,
            "rule_id": detail.get("constraint"),
            "legacy_node_id": node_id,
            "canonical_node_id": detail.get("canonical_node_id"),
            "canonical_binding": detail.get("canonical_binding"),
            "span": detail.get("span"),
            "surface": detail.get("surface"),
            "violation": remediation.get("violation") or detail.get("text"),
            "suggested_fix": remediation.get("suggested_fix"),
            "alternative_fix": remediation.get("alternative_fix"),
            "remediation": remediation,
        })
    for index, item in enumerate((candidate_xai or {}).get("items") or [], start=1):
        if not isinstance(item, dict):
            continue
        binding = item.get("tree_binding") or {}
        explanation = item.get("explanation") or {}
        items.append({
            "finding_id": f"candidate:{item.get('rule_id')}:{item.get('finding_id') or index}",
            "authority": "cambridge_candidate",
            "claim_status": "candidate_observation_not_verified_error",
            "production_path": False,
            "book_verified": False,
            "rule_id": item.get("rule_id"),
            "canonical_node_id": binding.get("affected_node_id"),
            "canonical_binding": binding,
            "source_chapter": item.get("source_chapter"),
            "source_pages": item.get("source_pages") or [],
            "explanation": explanation,
        })
    by_authority: dict[str, int] = {}
    by_claim: dict[str, int] = {}
    for item in items:
        by_authority[item["authority"]] = by_authority.get(item["authority"], 0) + 1
        by_claim[item["claim_status"]] = by_claim.get(item["claim_status"], 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "production_enabled": False,
        "whole_sentence_certified": False,
        "findings": items,
        "counts": {
            "total": len(items),
            "by_authority": by_authority,
            "by_claim_status": by_claim,
            "legacy": by_authority.get("legacy_matrix", 0),
            "candidate": by_authority.get("cambridge_candidate", 0),
        },
        "caveat": ("Legacy findings are diagnostic and not book-verified. "
                   "Candidate findings are not verified errors. No item here "
                   "authorizes a Cambridge runtime rule."),
    }
