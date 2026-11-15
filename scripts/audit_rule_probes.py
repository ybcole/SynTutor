"""Run the rule-probe corpus and report which expected rules fired.

    .venv/Scripts/python.exe scripts/audit_rule_probes.py \
        --output artifacts/rule-probe-report.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(ROOT / "scripts"))

from api import build_payload  # noqa: E402
from rule_probe_corpus import PROBES  # noqa: E402
import matrix  # noqa: E402

RULE_TO_CONSTRAINT = {
    rule_id: constraint
    for constraint, (rule_id, _method) in matrix.CONSTRAINT_RULE.items()
    if isinstance(rule_id, str)
}

# Registry aliases: the rule fires under one constraint id but the coverage
# inventory also lists the equivalent id.
ALIASES = {
    "C-ADVERB-FORM": {"C-ADJ-ADV"},
    "C-APOSTROPHE": {"C-HOMOPHONE"},
    "C-CLAUSE-LINKING": {"C-CONJUNCTION-PAIR"},
    "C-CORRELATIVE-AGREE": {"C-SUBJECT-AGREEMENT", "C-COORD-SUBJ-AGREE"},
    "C-DET-NOUN-AGREE": {"C-DETERMINER-AGREEMENT", "C-DETERMINER"},
    "C-INDEFINITE-AGREE": {"C-INDEF-AGREE"},
    "C-NUMERAL": {"C-QUANT-PLURAL", "C-QUANTIFIER"},
    "C-PASSIVE": {"C-VERB-FORM"},
    "C-PLURAL-FORM": {"C-NOUN-FORM"},
    "C-PLURAL-ONLY": {"C-UNCOUNTABLE"},
    "C-REFLEXIVE-ANTECEDENT": {"C-REFLEXIVE-SUBJECT"},
    "C-SELECTIONAL": {"C-VERB-CLAUSE-PATTERN"},
    "C-WRONG-PREPOSITION": {"C-ADJ-PREP", "C-PREP-CASE", "C-PREP-OBJECT"},
    "C-FIRST-MENTION": {"C-ARTICLE"},
    "C-FRAGMENT": {"C-TENSE-FINITE", "C-MISSING-SUBJECT"},
    "C-HOMOPHONE": {"C-TO_TOO"},
    "C-EXTRA-WORD": {"C-SPACING-REPEAT"},
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/rule-probe-report.json")
    args = parser.parse_args()
    results = []
    passed = 0
    for probe_id, sentence, expected in PROBES:
        try:
            payload = build_payload(sentence)
        except Exception as exc:  # noqa: BLE001
            results.append({"probe": probe_id, "sentence": sentence,
                            "expected": expected, "fatal": f"{type(exc).__name__}: {exc}",
                            "fired": [], "pass": False})
            continue
        seen = {
            detail.get("constraint")
            for detail in (payload.get("node_details") or {}).values()
            if detail.get("constraint")
        }
        for entry in (payload.get("summary") or {}).get("suggestions") or []:
            rule_id = str(entry).rsplit(":", 1)[-1]
            constraint = RULE_TO_CONSTRAINT.get(rule_id)
            if constraint:
                seen.add(constraint)
        seen = sorted(seen)
        fired = sorted({
            detail.get("constraint")
            for detail in (payload.get("node_details") or {}).values()
            if detail.get("status") in {"error", "suggestion"}
            and detail.get("constraint")
        })
        ok = (expected in seen or bool(ALIASES.get(expected, set()) & set(seen)))
        passed += 1 if ok else 0
        results.append({
            "probe": probe_id, "sentence": sentence, "expected": expected,
            "fired": fired, "pass": ok,
            "as_error": expected in {
                detail.get("constraint")
                for detail in (payload.get("node_details") or {}).values()
                if detail.get("status") == "error"
            },
            "verdict": (payload.get("summary") or {}).get("verdict"),
        })
    report = {
        "schema_version": "rule-probe-report-1.0.0",
        "probes": len(PROBES),
        "passed": passed,
        "failed": len(PROBES) - passed,
        "results": results,
    }
    destination = ROOT / args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({"probes": len(PROBES), "passed": passed,
                      "failed": len(PROBES) - passed}, ensure_ascii=True))
    for row in results:
        if not row["pass"]:
            print(f"FAIL {row['probe']}: expected {row['expected']} fired={row.get('fired')} "
                  f"fatal={row.get('fatal')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
