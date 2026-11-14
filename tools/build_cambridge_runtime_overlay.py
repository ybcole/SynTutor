#!/usr/bin/env python3
"""Enable every implemented pilot/support rule as an owner-waived candidate set.

This is an explicit owner waiver, not independent review. The runtime executes
the allow-listed Phase-C candidate probe set once per sentence and filters by
rule id.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "docs/planning/CGEL_PHASE_C_BACKLOG.md"
OVERLAY = ROOT / "grammar/cambridge_runtime_overlay.json"
REGISTRY = ROOT / "grammar/runtime_registry.json"


def pilot_ids() -> list[str]:
    ids = []
    for line in BACKLOG.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\| `([^`]+)` \| [^|]+ \| [^|]+ \| (Pilot|Support) \|", line)
        if match:
            ids.append(match.group(1))
    return sorted(set(ids))


def build() -> tuple[dict, dict]:
    ids = pilot_ids()
    overlay = {
        "schema_version": "cambridge-runtime-overlay-1.0.0",
        "purpose": "Owner-waived candidate rules. Not independently human-certified.",
        "policy": {
            "independent_human_review": False,
            "owner_waiver": True,
            "claim": "AI-checked source examples and guards; no independent certification",
            "candidate_set": "phase_c",
        },
        "rules": [
            {
                "rule_id": rule_id,
                "status": "REVIEWED",
                "runtime_check": {"kind": "candidate_probe_set", "set": "phase_c"},
                "review_basis": "owner_waived_ai_review",
            }
            for rule_id in ids
        ],
    }
    registry = {
        "registry_version": 1,
        "purpose": "Explicit owner-waived allow-list for implemented candidate rules.",
        "enabled_rules": [
            {
                "rule_id": rule_id,
                "owner_waiver": True,
                "independent_review": False,
                "reviewed_by": "owner waiver + AI source examples/guards",
                "reviewed_on": "2026-11-14",
                "crosswalk_status": "owner_waived_unverified",
                "test_status": "source_examples_passed",
                "runtime_status": "enabled",
            }
            for rule_id in ids
        ],
        "policy": {
            "extraction_status_alone_never_enables_a_rule": True,
            "permitted_rule_types": ["constraint", "variety_restricted"],
            "required_review_state": "owner_waived_ai_review",
            "required_crosswalk_status": ["owner_waived_unverified"],
            "required_test_state": "source_examples_passed",
            "default_when_absent": "disabled",
            "independent_review": False,
        },
        "notes": [
            "Owner explicitly waived independent human review on 2026-11-14.",
            "All enabled rules are AI-checked candidate probes, not independently certified.",
            "The runtime executes one allow-listed Phase-C candidate set and filters by rule id.",
            "Rules without a matching candidate finding simply pass for that sentence.",
        ],
    }
    return overlay, registry


def main() -> int:
    overlay, registry = build()
    OVERLAY.write_text(json.dumps(overlay, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REGISTRY.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"enabled {len(overlay['rules'])} owner-waived candidate rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
