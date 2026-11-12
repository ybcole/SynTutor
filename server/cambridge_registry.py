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
    if not isinstance(registry, dict):
        return {"registry_version": None, "active_rules": [],
                "diagnostics": [{
                    "code": "INVALID_REGISTRY",
                    "message": "The Cambridge runtime registry root must be a JSON object.",
                }]}

    by_id: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "grammar" / "rules").glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, list):
            rows = payload
        elif isinstance(payload, dict):
            rows = payload.get("rules", [])
        else:
            continue
        if not isinstance(rows, list):
            continue
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
            if rule.get("rule_type") == "variety_restricted" and (
                not isinstance(rule.get("variety"), str) or not rule["variety"].strip()
            ):
                reasons.append("variety-restricted rule must declare its variety")
            sources = rule.get("sources")
            if not isinstance(sources, list) or not any(
                isinstance(source, dict)
                and isinstance(source.get("pages"), list)
                and any(isinstance(page, int) and not isinstance(page, bool) and page > 0
                        for page in source["pages"])
                for source in sources
            ):
                reasons.append("source page evidence is missing or malformed")
            mappings = rule.get("burton_roberts_mapping", [])
            allowed_relations = {
                "same", "terminology_differs", "analysis_differs", "not_covered",
            }
            if not isinstance(mappings, list) or not mappings:
                reasons.append("source record has no explicit B-R crosswalk")
            elif any(
                not isinstance(mapping, dict)
                or mapping.get("relation") not in allowed_relations
                for mapping in mappings
            ):
                reasons.append("source record still contains an unresolved or invalid B-R crosswalk")
            check = rule.get("runtime_check")
            if not isinstance(check, dict):
                reasons.append("deterministic runtime_check is missing")
            elif check.get("kind") == "passive_make_missing_to":
                if rule_id != "CLS-357" or set(check) != {"kind"} or rule.get("scope") != "clause":
                    reasons.append("passive_make_missing_to requires the clause-scoped CLS-357 source")
            elif check.get("kind") != "forbidden_token_sequences":
                reasons.append("runtime_check kind is not supported by the deterministic evaluator")
            else:
                forbidden = check.get("forbidden_sequences")
                exceptions = check.get("exception_sequences", [])
                def valid_sequence(sequence: Any) -> bool:
                    return (isinstance(sequence, list) and bool(sequence)
                            and all(isinstance(token, str) and token.strip()
                                    for token in sequence))
                if not isinstance(forbidden, list) or not forbidden or not all(
                    valid_sequence(sequence) for sequence in forbidden
                ):
                    reasons.append("runtime_check forbidden_sequences are malformed")
                if not isinstance(exceptions, list) or not all(
                    valid_sequence(sequence) for sequence in exceptions
                ):
                    reasons.append("runtime_check exception_sequences are malformed")
        if entry.get("independent_review") is not True:
            reasons.append("independent_review must be true")
        if not isinstance(entry.get("reviewed_by"), str) or not entry["reviewed_by"].strip():
            reasons.append("reviewer identity is missing or malformed")
        if not isinstance(entry.get("reviewed_on"), str) or not entry["reviewed_on"].strip():
            reasons.append("review date is missing or malformed")
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
            "scope": rule.get("scope"),
            "violation": rule.get("violation"),
            "runtime_check": rule.get("runtime_check"),
        })
    return {
        "registry_version": registry.get("registry_version"),
        "active_rules": active,
        "active_rule_ids": [row["rule_id"] for row in active],
        "diagnostics": diagnostics,
    }
