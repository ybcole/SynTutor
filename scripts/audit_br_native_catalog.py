#!/usr/bin/env python3
"""Report native B-R signature coverage over the repository's 252 source trees.

This is a *coverage inventory*, never a semantic/grammaticality certification.
Use this as a reproducible baseline while extending the grammar rules.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from server.br_native_grammar import audit_br_constructions

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "web/content/book"


def audit_book_corpus(expected_count: int | None = None) -> dict:
    chapters = []
    all_unknown = Counter()
    statuses = Counter()
    total = 0
    examined = 0
    matched = 0
    hard_leaks = []

    for chapter in range(1, 11):
        path = BOOK / f"ch{chapter:02d}.trees.json"
        records = json.loads(path.read_text(encoding="utf-8"))["trees"]
        chapter_examined = 0
        chapter_matched = 0
        for record in records:
            total += 1
            statuses[record.get("status", "UNSPECIFIED")] += 1
            envelope = {
                "convention_profile": {
                    "chapter": chapter, "version": f"V{chapter}",
                    "profile_id": f"V{chapter}",
                },
                "root": record["tree"],
            }
            result = audit_br_constructions(envelope)
            stats = result["pattern_coverage"]
            chapter_examined += stats["examined"]
            chapter_matched += stats["matched"]
            for unknown in result["uncovered_patterns"]:
                key = unknown["parent"] + " -> " + " ".join(unknown["children"])
                all_unknown[key] += 1
            for leak in result["violations"]:
                hard_leaks.append({"record_id": record.get("id"), **leak})
        examined += chapter_examined
        matched += chapter_matched
        chapters.append({
            "chapter": chapter,
            "tree_records": len(records),
            "matched_branches": chapter_matched,
            "total_branches": chapter_examined,
            "coverage": round(chapter_matched / chapter_examined, 4) if chapter_examined else None,
        })

    if expected_count is not None and total != expected_count:
        raise ValueError(f"Expected {expected_count} source trees, received {total}")
    return {
        "registry_state": "DRAFT_SHAPE_COVERAGE_NOT_LINGUISTIC_CERTIFICATION",
        "source_tree_records": total,
        "tree_record_statuses": dict(statuses),
        "matched_branches": matched,
        "total_branches": examined,
        "overall_coverage": round(matched / examined, 4) if examined else None,
        "chapter_summary": chapters,
        "most_common_uncovered_signatures": all_unknown.most_common(40),
        "parser_label_leaks": hard_leaks,
        "semantic_conditions_checked": False,
        "independently_verified_trees": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-count", type=int, default=252)
    parser.add_argument("--fail-on-penn", action="store_true")
    options = parser.parse_args()
    report = audit_book_corpus(options.expected_count)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if options.fail_on_penn and report["parser_label_leaks"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
