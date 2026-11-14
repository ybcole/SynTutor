#!/usr/bin/env python3
"""Measure the enabled Cambridge runtime on repository held-out sentence sets.

This is candidate-runtime measurement, not independent grammaticality gold.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from parse_engine import analyze  # noqa: E402
from burton_roberts import build_canonical_analysis  # noqa: E402
from cambridge_registry import load_runtime_registry  # noqa: E402
from cambridge_evaluator import evaluate_cambridge  # noqa: E402


def run(path: Path, registry, limit: int | None = None) -> dict:
    rows = [row for row in json.loads(path.read_text(encoding="utf-8"))
            if isinstance(row, dict) and row.get("unit") == "sentence"]
    if limit:
        rows = rows[:limit]
    findings = []
    skipped = 0
    evaluated = 0
    working = 0
    for row in rows:
        text = row["text"]
        try:
            analysis = build_canonical_analysis(analyze(text))
            analysis["sentence"] = text
        except Exception:
            skipped += 1
            continue
        if analysis.get("status") != "normalized":
            if analysis.get("working_tree"):
                working += 1
            else:
                skipped += 1
            continue
        evaluated += 1
        result = evaluate_cambridge(analysis, registry, variety="standard_english")
        for finding in result.get("findings", []):
            findings.append({
                "rule_id": finding.get("rule_id"),
                "text": text,
                "matched": finding.get("candidate_matches")
                or finding.get("matched_sequences")
                or finding.get("structural_matches"),
            })
    return {
        "path": str(path.relative_to(ROOT)),
        "sentences": len(rows),
        "evaluated": evaluated,
        "working_tree_available": working,
        "tree_available": evaluated + working,
        "skipped_unresolved": skipped,
        "sentences_with_findings": len({row["text"] for row in findings}),
        "finding_count": len(findings),
        "by_rule": dict(Counter(row["rule_id"] for row in findings)),
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    registry = load_runtime_registry()
    report = {
        "schema_version": "cambridge-runtime-holdout-1.0.0",
        "enabled_rules": len(registry["active_rule_ids"]),
        "claim": "Owner-waived candidate runtime measurement; not independent gold.",
        "grammatical": run(ROOT / "evaluation/grammatical_sentences.json", registry, args.limit),
        "ungrammatical": run(ROOT / "evaluation/ungrammatical_sentences.json", registry, args.limit),
    }
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text)
    for split in ("grammatical", "ungrammatical"):
        row = report[split]
        print(f"{split}: sentences={row['sentences']} evaluated={row['evaluated']} "
              f"working={row['working_tree_available']} tree_available={row['tree_available']} "
              f"skipped={row['skipped_unresolved']} with_findings={row['sentences_with_findings']} "
              f"findings={row['finding_count']} top={sorted(row['by_rule'].items(), key=lambda x: -x[1])[:5]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
