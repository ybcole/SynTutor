#!/usr/bin/env python3
"""Generate the legacy-rule disposition map.

This is a proposed migration inventory, not independent approval. Every legacy
rule is accounted for and assigned a next action; no legacy code is deleted.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from ruleset import RULEBOOK, method_of  # noqa: E402

FAMILIES = {
    "1": "Word forms",
    "2": "Agreement",
    "3": "Articles and determiners",
    "4": "Nouns",
    "5": "Pronouns",
    "6": "Verbs",
    "7": "Adjectives and adverbs",
    "8": "Prepositions",
    "9": "Sentence structure",
    "10": "Punctuation and orthography",
    "11": "Meaning and usage",
}
RELATED = {
    "1.13": ["MORPH-480", "MORPH-481"],
    "3.1": ["OTH-726"],
    "4.2": ["MORPH-258"],
    "6.9": ["COMP-061", "WCAT-059"],
    "6.10": ["MORPH-056"],
    "6.11": ["COMP-085", "CLS-1325"],
    "6.12": ["COMP-042", "MORPH-056"],
    "6.13": ["CLS-128", "CLS-213", "CLS-156"],
    "6.16": ["OTH-453"],
    "6.17": ["OTH-458"],
    "7.5": ["WCAT-046"],
    "7.6": ["CLS-1259"],
    "8.6": ["WCAT-059"],
    "9.13": ["OTH-688"],
    "10.4": ["OTH-671", "OTH-688", "OTH-698", "OTH-699", "OTH-701", "OTH-708",
             "OTH-712", "OTH-715", "OTH-717", "OTH-730", "OTH-737", "OTH-740",
             "OTH-743"],
    "10.5": ["OTH-671"],
    "10.8": ["OTH-698", "OTH-699"],
}


def disposition(rule_id: str, method: str) -> tuple[str, str, str]:
    if method == "T":
        return (
            "port_candidate",
            "1-tree",
            "Port to a canonical-tree check or a candidate detector; keep the legacy "
            "path as a diagnostic until parity tests pass.",
        )
    if method == "L":
        return (
            "keep_legacy_diagnostic",
            "2-lexical",
            "Lexical list/morphology check. Keep as a legacy diagnostic until a "
            "source-reviewed Cambridge implementation exists.",
        )
    return (
        "keep_legacy_diagnostic",
        "3-semantic",
        "Context/meaning check. Keep diagnostic-only; do not promote to a "
        "production error without source review and a deterministic guard.",
    )


def build() -> dict:
    rows = []
    for rule_id, row in sorted(RULEBOOK.items(), key=lambda item: tuple(
            int(part) if part.isdigit() else part for part in item[0].split("."))):
        name, example, method = row
        family_id = rule_id.split(".")[0]
        action, priority, rationale = disposition(rule_id, method)
        related = RELATED.get(rule_id, [])
        rows.append({
            "rule_id": rule_id,
            "name": name,
            "example_error": example,
            "method": method,
            "family": FAMILIES.get(family_id, "Other"),
            "proposed_disposition": action,
            "priority": priority,
            "rationale": rationale,
            "related_cambridge_specs": related,
            "mapping_status": "unverified_related_only" if related else "unmapped",
            "status": "proposed_needs_review",
        })
    return {
        "schema_version": "legacy-disposition-1.0.0",
        "source": "server/ruleset.py",
        "policy": {
            "delete_without_parity": False,
            "production_without_review": False,
            "legacy_claim": "legacy_diagnostic_not_book_verified",
        },
        "counts": {
            "total": len(rows),
            "port_candidate": sum(1 for row in rows if row["proposed_disposition"] == "port_candidate"),
            "keep_legacy_diagnostic": sum(
                1 for row in rows if row["proposed_disposition"] == "keep_legacy_diagnostic"),
        },
        "rules": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    data = build()
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(text, encoding="utf-8")
        print(f"wrote {args.write}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
