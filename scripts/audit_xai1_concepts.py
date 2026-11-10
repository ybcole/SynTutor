#!/usr/bin/env python3
"""XAI-1 source-checked knowledge-base audit (does not diagnose English).

python scripts/audit_xai1_concepts.py --require-valid --output artifacts/xai1-concepts.json
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server.xai_concepts import load_catalog, validate_catalog  # noqa: E402

XAI0_UNCITED_PRIORITY = {
    "VP": 191, "NP": 184, "V": 110, "NOM": 97, "DET": 84,
    "N": 83, "pronoun": 66, "ART": 58,
}
XAI2_REQUIRED = {
    "S", "NP", "VP", "NOM", "PP", "AP", "AdvP", "V", "N", "P", "A",
    "DET", "ART", "pronoun", "name",
}


def report() -> dict:
    catalog = load_catalog()
    counts = validate_catalog(catalog)
    labels = Counter()
    for c in catalog["concepts"]:
        labels.update(c["scope"]["target_labels"])
    templates = Counter(t["target_label"] for t in catalog["template_candidates"])
    absent = sorted(XAI2_REQUIRED - set(labels))
    if absent:
        raise ValueError("Missing priority B-R concepts: " + ", ".join(absent))
    return {
        "milestone": "XAI-1",
        "status": "SOURCE_CHECKED_CANDIDATES_TECHNICALLY_VALID_HUMAN_SIGNOFF_PENDING",
        "language_scope": catalog["language_policy"],
        "counts": counts,
        "priority_label_source_coverage": {x: labels[x] for x in sorted(XAI2_REQUIRED)},
        "priority_label_template_candidates": {
            x: templates[x] for x in sorted(XAI2_REQUIRED)},
        "priority_label_missing": absent,
        "xai0_uncited_node_counts_for_priority": XAI0_UNCITED_PRIORITY,
        "source_review": {
            "method": "assistant-reviewed selected pages of uploaded original editions",
            "independently_human_approved": 0,
            "full_book_review_claimed": False,
            "crosswalk_disagreements": [
                {"id": x["id"], "relation": x["relation"], "issue": x["issue"]}
                for x in catalog["crosswalks"]
                if x["relation"] in {"analysis_differs", "unresolved", "not_covered"}
            ],
        },
        "safety": {
            "production_explanation_registry_unchanged": True,
            "cambridge_runtime_constraints_enabled_by_xai1": 0,
            "corrector_or_canonicalizer_changed_by_xai1": False,
            "templates_are_non_runtime_candidates": True,
        },
        "next": {
            "XAI-2": "license node/category/head/sibling/role facts with original tree proof",
            "XAI-3": "approve and render sentence-dependent templates using trusted fact graph",
            "XAI-4": "independent rule review, exception handling, runtime grammar tests",
            "XAI-5": "counterfactual grouped repairs and versioned clickable B-R trees",
        },
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--require-valid", action="store_true")
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        data = report()
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                                   encoding="utf-8")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({"milestone": "XAI-1", "error": str(exc)}, indent=2))
        if args.require_valid:
            raise SystemExit(1)
