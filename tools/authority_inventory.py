#!/usr/bin/env python3
"""Emit the current runtime authority inventory as JSON.

Run from the repository root:

    python tools/authority_inventory.py
    python tools/authority_inventory.py --write docs/planning/authority_inventory.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

from authority import build_authority_manifest  # noqa: E402
from ruleset import RULEBOOK, method_of  # noqa: E402


def inventory() -> dict:
    manifest = build_authority_manifest(br_status="normalized")
    legacy = []
    for rule_id, row in sorted(RULEBOOK.items(), key=lambda item: tuple(
            int(part) if part.isdigit() else part for part in item[0].split("."))):
        name, example, method = row
        legacy.append({
            "rule_id": rule_id,
            "name": name,
            "example_error": example,
            "method": method,
            "disposition": "legacy_diagnostic_until_ported_or_retired",
        })
    return {
        "schema_version": "authority-inventory-1.0.0",
        "authority": manifest,
        "legacy_rulebook": {
            "source": "server/ruleset.py",
            "count": len(legacy),
            "methods": dict(Counter(row["method"] for row in legacy)),
            "rules": legacy,
        },
        "migration_policy": {
            "structural_authority": "burton_roberts_canonical",
            "grammar_authority": "cambridge_runtime_registry",
            "legacy_authority": "diagnostic_only",
            "delete_policy": "port_or_retire_after_parity_tests",
            "production_without_independent_review": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    data = inventory()
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
