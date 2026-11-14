#!/usr/bin/env python3
"""Build the FINAL-D1 disposition register required by the syntax handoff.

Inputs are repository fixtures and the catalog audit. No PDF is read.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_br_native_catalog import audit_book_corpus  # noqa: E402

BOOK = ROOT / "web/content/book"
OUT = ROOT / "docs/planning/br_final_d1_dispositions.json"

DISPOSITION = {
    "PEDAGOGICAL_SCHEMATIC_PROFILE": "chapter_only",
    "ACA_SOURCE_SPECIFIC_SCAFFOLD": "chapter_only",
    "PRINTED_ANOMALY_REQUIRES_ADJUDICATION": "source_anomaly",
    "CONSTRUCTION_REQUIRES_SOURCE_REVIEW": "unresolved",
}
REASON = {
    "PEDAGOGICAL_SCHEMATIC_PROFILE": (
        "Introductory teaching schematic or PHRASE placeholder. Keep the chapter "
        "profile; do not invent a FINAL-D1 lexical analysis."
    ),
    "ACA_SOURCE_SPECIFIC_SCAFFOLD": (
        "Chapter 8 abbreviated clause scaffold. Preserve it for the chapter lesson; "
        "do not generalize a unary scaffold as a universal production."
    ),
    "PRINTED_ANOMALY_REQUIRES_ADJUDICATION": (
        "Printed source anomaly. Retain the transcribed source form and record the "
        "anomaly; do not silently normalize it."
    ),
    "CONSTRUCTION_REQUIRES_SOURCE_REVIEW": (
        "Construction-specific unmatched branch. Requires figure/path adjudication "
        "before deciding whether a reusable FINAL-D1 rule is missing."
    ),
}
CHAPTER_ONLY_OVERRIDES = {
    ("ch3-7", "root"): "Chapter 3 introductory NP schematic with PHRASE-b; not a free-analysis sentence.",
    ("ch7-25", "root/children/1/children/0"): "Chapter 7 AP fragment used to teach DEG + quantifying adjective; not a free sentence.",
    ("ch7-32", "root/children/1/children/1"): "Chapter 7 compound-N teaching fragment.",
    ("ch7-72a", "root"): "Chapter 7 indefinite-pronoun NP fragment with AP postmodifier.",
    ("ch7-72b", "root"): "Chapter 7 indefinite-pronoun NP fragment with PP postmodifier.",
    ("ch7-disc3", "root/children/1"): "Chapter 7 PartP teaching fragment, not a free sentence.",
    ("ch7-disc3", "root/children/1/children/0"): "Chapter 7 PartP teaching fragment, not a free sentence.",
    ("ch7-disc4", "root/children/1/children/1/children/1"): "Chapter 7 nested compound-N teaching fragment.",
    ("ch7-ex1-d", "root/children/0/children/0/children/0/children/1"): "Chapter 7 exercise fragment with a partitive NOM.",
    ("ch7-ex1-d", "root/children/0/children/0/children/0/children/1/children/0"): "Chapter 7 exercise fragment with a PartP.",
    ("ch7-ex1-f", "root/children/1/children/1"): "Chapter 7 exercise fragment; hyphen/compound tokenization is a source-notation case.",
    ("ch7-app-19b", "root/children/1"): "Chapter 7 Appendix pro-NOM fragment with PP.",
    ("ch7-app-20b", "root/children/1"): "Chapter 7 Appendix pro-NOM fragment.",
    ("ch8-23", "root/children/1"): "Chapter 8 printed unary-VP scaffold; preserve it as chapter-specific rather than a universal production.",
    ("ch8-ex2-d", "root/children/3"): "Chapter 8 exercise C/S scaffold; chapter-specific, not a free-analysis rule.",
}
CHAPTER_ONLY_REASON = "Reviewed chapter-specific teaching shape; no reusable FINAL-D1 rule is claimed."


RECORD_DISPOSITION = {
    "IMG": "retain_source_transcription",
    "DERIVED_FROM_INSTRUCTIONS": "retain_derived_source",
    "IMG_ANOMALY": "retain_source_anomaly",
}


def record_decisions() -> list[dict]:
    rows = []
    for chapter in range(1, 11):
        path = BOOK / f"ch{chapter:02d}.trees.json"
        records = json.loads(path.read_text(encoding="utf-8"))["trees"]
        for record in records:
            status = record.get("status", "UNSPECIFIED")
            rows.append({
                "record_id": record.get("id"),
                "chapter": chapter,
                "printed_page": record.get("page"),
                "figure": record.get("fig"),
                "source_status": status,
                "sentence": record.get("sentence", ""),
                "profile_id": f"V{chapter}",
                "disposition": RECORD_DISPOSITION.get(status, "pending_source_adjudication"),
                "reason": (
                    "Repository transcription retained; source-image verification is "
                    "recorded separately and is not claimed here."
                ),
                "verification_level": "transcribed_not_independently_verified",
            })
    return rows


def build() -> dict:
    audit = audit_book_corpus(252)
    rows = []
    for row in audit["uncovered_instances"]:
        triage = row["triage_group"]
        override = CHAPTER_ONLY_OVERRIDES.get((row["record_id"], row["path"]))
        disposition = "chapter_only" if override else DISPOSITION.get(triage, "unresolved")
        reason = override or REASON.get(triage, REASON["CONSTRUCTION_REQUIRES_SOURCE_REVIEW"])
        test_id = (f"audit:{row['record_id']}:{row['path']}"
                   if disposition in {"chapter_only", "source_anomaly"} else None)
        rows.append({
            "record_id": row["record_id"],
            "chapter": row["chapter"],
            "printed_page": row["printed_page"],
            "figure": row["figure"],
            "source_status": row["source_status"],
            "profile_id": f"V{row['chapter']}",
            "path": row["path"],
            "signature": row["signature"],
            "triage_group": triage,
            "disposition": disposition,
            "reason": reason,
            "runtime_rule": None,
            "test_id": test_id,
            "test_status": ("covered_by_catalog_audit"
                            if test_id else "requires_figure_specific_adjudication"),
            "verification_level": "transcribed_not_independently_verified",
            "independently_verified": False,
        })
    records = record_decisions()
    return {
        "schema_version": "br-final-d1-dispositions-1.0.0",
        "source": "web/content/book/ch01.trees.json..ch10.trees.json + catalog audit",
        "pdf_required": False,
        "policy": {
            "source_fixture_is_teaching_evidence_not_free_analysis_gold": True,
            "do_not_invent_source_figures": True,
            "do_not_claim_independent_review": True,
            "unsupported_must_remain_unresolved": True,
        },
        "counts": {
            "source_records": len(records),
            "uncovered_instances": len(rows),
            "dispositions": dict(Counter(row["disposition"] for row in rows)),
            "triage": dict(Counter(row["triage_group"] for row in rows)),
        },
        "record_decisions": records,
        "uncovered_instances": rows,
    }


def main() -> int:
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    print(json.dumps(data["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
