#!/usr/bin/env python3
"""XAI-PRE read-only audit: contract integrity is NOT runtime grammar readiness.

Commands:
  python scripts/audit_xai_pre.py
  python scripts/audit_xai_pre.py --require-contracts
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.xai_preflight import (  # noqa: E402
    AUDIT_PATH, FIXTURE_PATH, load_json,
    validate_source_audit, validate_diagnosis_repair_case,
)


def audit() -> dict:
    source = load_json(AUDIT_PATH)
    counts = validate_source_audit(source)
    fixtures = load_json(FIXTURE_PATH)
    if fixtures.get("review_state") != "NOT_HUMAN_ADJUDICATED":
        raise ValueError("Synthetic preflight fixtures must not claim expert gold status")
    results = []
    for case in fixtures.get("cases", []):
        stats = validate_diagnosis_repair_case(case["envelope"])
        expected = case.get("expected", {})
        for field in ("original_findings", "issue_groups", "candidates"):
            if stats[field] != expected.get(field):
                raise ValueError(f"{case.get('id')}: count mismatch for {field}")
        results.append({"id": case["id"], **stats})
    if len({row["id"] for row in results}) != len(results):
        raise ValueError("Duplicate fixture identifiers")

    registry = json.loads((ROOT / "grammar/runtime_registry.json").read_text(encoding="utf-8"))
    active = registry.get("enabled_rules", [])
    return {
        "milestone": "XAI-PRE",
        "status": "CONTRACTS_VALIDATED_SOURCE_APPROVAL_PENDING",
        "scope": "Source-inventory and mock-record validation, NOT English error detection",
        "source_inventory": counts,
        "cambridge_runtime_rule_count": len(active),
        "synthetic_cases_validated": len(results),
        "synthetic_case_results": results,
        "approved_xai_pre_claim_count": 0,
        "full_book_independent_audit_complete": False,
        "reliable_sentence_corrections_implemented": False,
        "evolving_B_R_trees_implemented_by_this_milestone": False,
        "next": [
            "Independent source and exception review for first actual Cambridge constraints",
            "Owner confirmation of remaining XAI-PRE source-governance decisions",
            "XAI-0 audit of existing node explanations, parser status and 50+ representative sentences",
            "XAI-2/3 contextual relationships and explanations; XAI-4/5 actual diagnostics and repair engines",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-contracts", action="store_true",
                        help="Exit nonzero unless the source and mock contracts validate")
    options = parser.parse_args()
    try:
        outcome = audit()
        print(json.dumps(outcome, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"milestone": "XAI-PRE", "error": str(exc)}, indent=2))
        if options.require_contracts:
            raise SystemExit(1)
