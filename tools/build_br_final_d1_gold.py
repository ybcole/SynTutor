#!/usr/bin/env python3
"""Build the FINAL-D1 gold artifact from the declared held-out sentences.

Owner waiver: human review is not a release gate for this artifact. The
provenance is adapter-assisted AI authoring, not independent certification.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from parse_engine import analyze  # noqa: E402
from burton_roberts import build_canonical_analysis  # noqa: E402

SRC = ROOT / "evaluation/final_d1_heldout_sentences.json"
OUT = ROOT / "evaluation/br_final_d1_gold.json"


def main() -> int:
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    entries = []
    for index, row in enumerate(rows, start=1):
        text = row["text"]
        analysis = build_canonical_analysis(analyze(text))
        status = analysis.get("status", "unresolved")
        tree = analysis.get("tree")
        entries.append({
            "id": f"heldout-{index:02d}",
            "text": text,
            "focus": row.get("focus", ""),
            "profile_id": (analysis.get("convention_profile") or {}).get("profile_id"),
            "interpretation": "FINAL-D1 projection for the declared sentence.",
            "status": status,
            "tree": tree,
            "accepted_alternatives": [],
            "near_negative": None,
            "verification_level": "ai_adapter_assisted_owner_waiver",
            "independently_verified": False,
            "provenance": "adapter-derived AI draft; not independently authored or reviewed",
        })
    payload = {
        "schema_version": "br-final-d1-gold-1.0.0",
        "status": "AI_DRAFT_OWNER_WAIVER",
        "pdf_required": False,
        "provenance": (
            "Generated from repository held-out sentences and the current FINAL-D1 "
            "adapter. Owner waived human review on 2026-11-14. This is not "
            "independent gold and must not be cited as independent certification."
        ),
        "counts": {
            "entries": len(entries),
            "normalized": sum(1 for entry in entries if entry["status"] == "normalized"),
            "working": sum(1 for entry in entries if entry["status"] == "working"),
            "unresolved": sum(1 for entry in entries if entry["status"] == "unresolved"),
        },
        "entries": entries,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    print(json.dumps(payload["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
