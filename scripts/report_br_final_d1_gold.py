#!/usr/bin/env python3
"""Compare the FINAL-D1 gold artifact with the current adapter.

This is a drift/regression report. Because the current artifact was generated
from the adapter, a 20/20 match is not independent accuracy evidence.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from parse_engine import analyze  # noqa: E402
from burton_roberts import build_canonical_analysis  # noqa: E402


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, default=ROOT / "evaluation/br_final_d1_gold.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    gold = json.loads(args.gold.read_text(encoding="utf-8"))
    rows = []
    matches = 0
    for entry in gold["entries"]:
        current = build_canonical_analysis(analyze(entry["text"]))
        same = canonical(current.get("tree")) == canonical(entry.get("tree"))
        matches += 1 if same else 0
        rows.append({
            "id": entry["id"],
            "status": current.get("status"),
            "gold_status": entry.get("status"),
            "exact_tree_match": same,
        })
    report = {
        "schema_version": "br-final-d1-gold-report-1.0.0",
        "gold_status": gold.get("status"),
        "provenance": gold.get("provenance"),
        "entries": len(rows),
        "adapter_exact_matches": matches,
        "adapter_exact_match_rate": round(matches / len(rows), 4) if rows else None,
        "caveat": ("Adapter-derived gold baseline; not independent accuracy. "
                   "A match measures drift against the generated artifact."),
        "rows": rows,
    }
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
