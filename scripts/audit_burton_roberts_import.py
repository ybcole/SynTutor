#!/usr/bin/env python3
"""Audit read-only projection of all existing Burton-Roberts chapter trees.

Run from the repository root:
    python scripts/audit_burton_roberts_import.py

Unresolved source records are reported, not treated as failures. A failure
means an importer exception or a projection marked normalized that fails the
canonical validator.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from server.burton_roberts import canonicalize_gold_record, validate_canonical_tree


def audit_chapter(path: Path, expected_chapter: int) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    chapter = data.get("chapter")
    if chapter != expected_chapter:
        raise ValueError(f"{path}: chapter field is {chapter!r}, expected {expected_chapter}")
    records = data.get("trees")
    if not isinstance(records, list):
        raise ValueError(f"{path}: 'trees' must be an array")

    statuses: Counter[str] = Counter()
    evidence: Counter[str] = Counter()
    unresolved: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    normalized = 0

    for record in records:
        record_id = str(record.get("id", "<missing-id>"))
        evidence[str(record.get("status", "<missing-status>"))] += 1
        try:
            result = canonicalize_gold_record(record, data)
        except Exception as exc:  # report all malformed source rows in one run
            statuses["exception"] += 1
            failures.append({"id": record_id, "error": f"{type(exc).__name__}: {exc}"})
            continue

        status = str(result.get("status", "<missing-status>"))
        statuses[status] += 1
        if status == "normalized":
            normalized += 1
            validation = validate_canonical_tree(result.get("tree"))
            if not validation.get("valid"):
                failures.append({
                    "id": record_id,
                    "error": "normalized projection failed validation",
                    "validation_errors": validation.get("errors", []),
                })
        elif status in {"unresolved", "rejected"}:
            unresolved.append({
                "id": record_id,
                "status": status,
                "reasons": result.get("errors", []),
            })
        else:
            failures.append({"id": record_id, "error": f"unexpected status {status!r}"})

    return {
        "chapter": expected_chapter,
        "source_file": str(path.relative_to(ROOT)),
        "source_records": len(records),
        "statuses": dict(sorted(statuses.items())),
        "evidence_statuses": dict(sorted(evidence.items())),
        "normalized_and_revalidated": normalized,
        "unresolved_or_rejected": unresolved,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-count", type=int, default=None,
                        help="optionally require an exact total source-record count")
    args = parser.parse_args()

    chapters = []
    for chapter in range(1, 11):
        path = ROOT / "web" / "content" / "book" / f"ch{chapter:02d}.trees.json"
        if not path.is_file():
            print(f"Missing chapter fixture: {path}", file=sys.stderr)
            return 2
        chapters.append(audit_chapter(path, chapter))

    total_records = sum(row["source_records"] for row in chapters)
    totals: Counter[str] = Counter()
    evidence_totals: Counter[str] = Counter()
    unresolved_rows = []
    failures = []
    for row in chapters:
        totals.update(row["statuses"])
        evidence_totals.update(row["evidence_statuses"])
        unresolved_rows.extend(
            {"chapter": row["chapter"], **item}
            for item in row["unresolved_or_rejected"]
        )
        failures.extend(
            {"chapter": row["chapter"], **item}
            for item in row["failures"]
        )

    report = {
        "audit": "Burton-Roberts canonical fixture projection",
        "read_only": True,
        "chapter_count": len(chapters),
        "source_record_count": total_records,
        "expected_count_check": (
            None if args.expected_count is None
            else {"expected": args.expected_count, "passed": total_records == args.expected_count}
        ),
        "status_totals": dict(sorted(totals.items())),
        "evidence_status_totals": dict(sorted(evidence_totals.items())),
        "chapters": chapters,
        "unresolved_records": unresolved_rows,
        "failures": failures,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        return 1
    if args.expected_count is not None and total_records != args.expected_count:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
