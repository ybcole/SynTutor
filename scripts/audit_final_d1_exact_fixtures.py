#!/usr/bin/env python3
"""Measure exact complete-tree agreement against transcribed chapter fixtures.

This is source-fixture compliance, not independent free-sentence gold.
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


def signature(node):
    if not isinstance(node, dict):
        return None
    return (
        node.get("label"), node.get("word"), node.get("triangle"),
        node.get("gap"), node.get("elided"),
        tuple(sorted(node.get("features") or [])),
        tuple(signature(child) for child in node.get("children") or []),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = []
    exact = normalized = unresolved = reference = 0
    mismatches = []
    for chapter in range(1, 11):
        path = ROOT / "web/content/book" / f"ch{chapter:02d}.trees.json"
        for record in json.loads(path.read_text(encoding="utf-8"))["trees"]:
            if record.get("status") != "IMG" or not record.get("sentence") or not record.get("tree"):
                continue
            result = build_canonical_analysis(analyze(record["sentence"]), chapter=chapter)
            if result.get("status") != "normalized" or not result.get("tree"):
                unresolved += 1
                rows.append({"record_id": record["id"], "chapter": chapter,
                             "status": "unresolved", "exact": False})
                continue
            normalized += 1
            trace = [item.get("rule_id") for item in result.get("normalization_trace", [])]
            if "EXACT_IMG_GOLD_REFERENCE" in trace:
                reference += 1
            same = signature(result["tree"]["root"]) == signature(record["tree"])
            exact += 1 if same else 0
            if not same:
                mismatches.append({"record_id": record["id"], "chapter": chapter,
                                   "sentence": record["sentence"]})
            rows.append({"record_id": record["id"], "chapter": chapter,
                         "status": "normalized", "exact": same})
    report = {
        "schema_version": "final-d1-exact-fixtures-1.0.0",
        "source": "web/content/book/ch01.trees.json..ch10.trees.json (IMG sentence-aligned)",
        "claim": "Exact complete-tree agreement against transcribed chapter fixtures; not independent free-sentence gold.",
        "source_img_records": normalized + unresolved,
        "normalized": normalized,
        "exact_matches": exact,
        "exact_rate": round(exact / normalized, 4) if normalized else None,
        "reference_path_matches": reference,
        "unresolved": unresolved,
        "mismatches": mismatches,
        "rows": rows,
    }
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text)
    print({key: report[key] for key in (
        "source_img_records", "normalized", "exact_matches", "exact_rate",
        "reference_path_matches", "unresolved")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
