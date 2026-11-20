#!/usr/bin/env python3
"""Reproducible Chapter 5 *development-corpus* diagnostic metrics.

IMPORTANT: scripts.audit_rules.GOLD is a repository-maintained regression
corpus, not a locked independent hold-out or expert-adjudicated sample.
The resulting precision/recall/F1 must NOT be described as independent
accuracy or evidence that every reported XAI explanation is correct.
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.audit_rules import GOLD, run_corpus

def ratio(num, den):
    return num / den if den else None

def calculate(records):
    expected = len(GOLD)
    if len(records) != expected:
        raise ValueError(f"Expected {expected} predictions; received {len(records)}")
    confusion = Counter()
    cases = []
    for row in records:
        truth = not bool(row["expected"])  # positive class: ungrammatical
        actual = row.get("actual")
        if actual not in ("grammatical", "ungrammatical"):
            label = "unscored"
        else:
            pred = actual == "ungrammatical"
            label = ("TP" if truth else "FP") if pred else ("FN" if truth else "TN")
        confusion[label] += 1
        cases.append({
            "text": row["text"], "expected_ungrammatical": truth,
            "actual_verdict": actual, "classification": label,
            "checker_errors": row.get("checker_errors", []),
        })
    tp, fp, fn, tn = (confusion[k] for k in ("TP", "FP", "FN", "TN"))
    scored = tp + fp + fn + tn
    precision, recall = ratio(tp, tp+fp), ratio(tp, tp+fn)
    return {
        "corpus": "repository-maintained GOLD in scripts/audit_rules.py",
        "validation_status": "DEVELOPMENT_REGRESSION_NOT_INDEPENDENT",
        "positive_class": "ungrammatical",
        "n_total": len(records),
        "n_scored": scored,
        "n_unscored": confusion["unscored"],
        "n_expected_grammatical": sum(bool(r["expected"]) for r in records),
        "n_expected_ungrammatical": sum(not bool(r["expected"]) for r in records),
        "confusion_matrix": {"TP": tp, "FP": fp, "FN": fn, "TN": tn},
        "accuracy": ratio(tp+tn, scored),
        "precision": precision,
        "recall": recall,
        "f1": ratio(2*tp, 2*tp+fp+fn),
        "specificity": ratio(tn, tn+fp),
        "cases": cases,
        "interpretation": (
            "Development regression measurements only; not independent "
            "generalization accuracy. The source corpus may have been "
            "used to tune rules. Tree constituent F1 and semantic XAI "
            "correctness require separate adjudicated reference data."
        ),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/ch5-technical-development.json")
    parser.add_argument("--strict", action="store_true",
                        help="Fail if a classification disagrees with a development expectation")
    args = parser.parse_args()
    records, *_ = run_corpus()  # real spaCy/Benepar and live matrix
    result = calculate(records)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps({key:value for key,value in result.items() if key != "cases"}, indent=2))
    cm = result["confusion_matrix"]
    if args.strict and (cm["FP"] or cm["FN"] or result["n_unscored"]):
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
