"""Fail-closed allow-list for Cambridge rules eligible for runtime execution."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any


def load_runtime_registry(root: Path | None = None) -> dict[str, Any]:
    root = root or Path(__file__).resolve().parents[1]
    try:
        registry = json.loads((root / "grammar" / "runtime_registry.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"registry_version": None, "active_rules": [],
                "diagnostics": [{"code": "REGISTRY_UNAVAILABLE", "message": str(exc)}]}

    by_id: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "grammar" / "rules").glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rows = payload if isinstance(payload, list) else payload.get("rules", [])
        for row in rows:
            if isinstance(row, dict) and row.get("id"):
                by_id[str(row["id"])] = row

    active, diagnostics, seen = [], [], set()
    entries = registry.get("enabled_rules", [])
    if not isinstance(entries, list):
        entries = []
        diagnostics.append({"code": "INVALID_ALLOW_LIST", "message": "enabled_rules must be an array."})
    for entry in entries:
        if not isinstance(entry, dict) or not entry.get("rule_id"):
            diagnostics.append({"code": "INVALID_ALLOW_LIST_ENTRY", "message": "Allow-list entry lacks rule_id."})
            continue
        rule_id = str(entry["rule_id"])
        if rule_id in seen:
            diagnostics.append({"code": "DUPLICATE_ALLOW_LIST_ENTRY", "message": rule_id})
            continue
        seen.add(rule_id)
        rule = by_id.get(rule_id)
        reasons = []
        if rule is None:
            reasons.append("source rule not found")
        else:
            if rule.get("status") not in {"APPROVED", "REVIEWED"}:
                reasons.append("source extraction is not reviewed/approved")
            if rule.get("rule_type") not in {"constraint", "variety_restricted"}:
                reasons.append("rule type is not executable")
            if not any(source.get("pages") for source in rule.get("sources", []) if isinstance(source, dict)):
                reasons.append("source page evidence is missing")
        if entry.get("independent_review") is not True:
            reasons.append("independent_review must be true")
        if entry.get("crosswalk_status") not in {"compatible", "resolved"}:
            reasons.append("B-R/Cambridge crosswalk is unresolved")
        if entry.get("test_status") != "passed":
            reasons.append("positive/negative/exception tests have not passed")
        if entry.get("runtime_status") != "enabled":
            reasons.append("runtime_status is not enabled")
        if reasons:
            diagnostics.append({"code": "RULE_NOT_RUNTIME_ELIGIBLE",
                                "message": f"{rule_id}: " + "; ".join(reasons)})
            continue
        active.append({
            "rule_id": rule_id, "rule_type": rule["rule_type"],
            "concept": rule.get("concept"), "sources": rule.get("sources", []),
            "variety": rule.get("variety"),
        })
    return {
        "registry_version": registry.get("registry_version"),
        "active_rules": active,
        "active_rule_ids": [row["rule_id"] for row in active],
        "diagnostics": diagnostics,
    }
