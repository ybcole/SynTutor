"""Explicit runtime authority manifest.

This is descriptive metadata for coherence and UI labelling. It does not
enable a rule or grant a source claim.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    from . import ruleset
    from .cambridge_registry import load_runtime_registry
except ImportError:  # pragma: no cover - script execution from server/
    import ruleset
    from cambridge_registry import load_runtime_registry

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "authority-manifest-1.0.0"


@lru_cache(maxsize=1)
def _catalog_counts() -> dict[str, int]:
    total = 0
    diagnostics = 0
    constraints = 0
    for path in sorted((ROOT / "grammar" / "rules").glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rows = payload.get("rules", []) if isinstance(payload, dict) else payload
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict) or not row.get("id"):
                continue
            total += 1
            if isinstance(row.get("diagnostic"), dict):
                diagnostics += 1
                if row.get("rule_type") == "constraint":
                    constraints += 1
    return {"records": total, "diagnostic_specs": diagnostics,
            "constraint_specs": constraints}


def build_authority_manifest(*, br_status: str | None = None,
                             runtime_registry: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = runtime_registry if isinstance(runtime_registry, dict) else load_runtime_registry()
    enabled = registry.get("active_rules") if isinstance(registry, dict) else []
    enabled_count = len(enabled) if isinstance(enabled, list) else 0
    counts = _catalog_counts()
    legacy_rulebook = getattr(ruleset, "RULEBOOK", {})
    return {
        "schema_version": SCHEMA_VERSION,
        "coherence_policy": "one structural authority, one approved grammar authority, labeled legacy channels",
        "structure": {
            "authority": "burton_roberts",
            "label": "B-R canonical tree" if br_status in {"normalized", "working"} else "B-R unavailable / parser diagnostic",
            "status": br_status or "unavailable",
            "derived": True,
            "book_verified": False,
        },
        "detection": {
            "authority": "legacy_matrix",
            "label": "Legacy matrix diagnostic + advisory CoLA",
            "production_verdict": True,
            "book_verified": False,
            "legacy_rulebook_rules": len(legacy_rulebook) if isinstance(legacy_rulebook, dict) else 0,
        },
        "cambridge": {
            "authority": "cambridge",
            "label": f"{enabled_count} runtime-enabled Cambridge rules",
            "runtime_enabled": enabled_count,
            "catalog_records": counts["records"],
            "diagnostic_specs": counts["diagnostic_specs"],
            "constraint_specs": counts["constraint_specs"],
            "candidate_only": enabled_count == 0,
        },
        "candidate": {
            "label": "Candidate grammar checks — not verified errors",
            "production_enabled": False,
        },
        "explanations": {
            "structural": "B-R only",
            "grammatical": "Cambridge only",
            "remediation": "Cambridge only",
            "legacy_prose": "withheld when shared evidence exists",
        },
        "correction": {
            "production": "legacy remediation + optional MLM fallback",
            "candidate": "Phase D selected-sentence candidate correction",
        },
        "lessons_quizzes": {
            "current": "legacy rulebook content",
            "cambridge_generation": "pending",
        },
    }
