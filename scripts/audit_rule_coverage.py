"""Rule-coverage audit: which detector constraints does the corpus exercise?

Run from the repository root:

    .venv/Scripts/python.exe scripts/audit_rule_coverage.py \
        --corpus artifacts/syntutor-stress-report.json \
        --output artifacts/rule-coverage.json

It reports every constraint known to the matrix that never appeared in any
sentence's node details (valid or error). Uncovered error rules are blind
spots for the stress corpus, not proof that the rule is wrong.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

from api import build_payload  # noqa: E402
import matrix  # noqa: E402


def _constraints(payload):
    found = {}
    for detail in (payload.get("node_details") or {}).values():
        constraint = detail.get("constraint")
        if constraint:
            found.setdefault(constraint, 0)
            found[constraint] += 1
    for row in (payload.get("summary") or {}).get("violations") or []:
        if isinstance(row, dict) and row.get("constraint"):
            found.setdefault(row["constraint"], 0)
            found[row["constraint"]] += 1
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="artifacts/syntutor-stress-report.json")
    parser.add_argument("--output", default="artifacts/rule-coverage.json")
    args = parser.parse_args()
    corpus = json.loads((ROOT / args.corpus).read_text(encoding="utf-8"))
    sentences = [row["sentence"] for row in corpus.get("results", [])]
    known = set(matrix.CHECK_LABELS)
    covered = {}
    errors = {}
    for sentence in sentences:
        payload = build_payload(sentence)
        for constraint, count in _constraints(payload).items():
            covered[constraint] = covered.get(constraint, 0) + count
    for sentence in sentences:
        payload = build_payload(sentence)
        for detail in (payload.get("node_details") or {}).values():
            if detail.get("status") == "error" and detail.get("constraint"):
                errors[detail["constraint"]] = errors.get(detail["constraint"], 0) + 1
    uncovered = sorted(known - set(covered))
    uncovered_errors = sorted(known - set(errors))
    report = {
        "schema_version": "rule-coverage-1.0.0",
        "sentences": len(sentences),
        "known_constraints": len(known),
        "covered_constraints": len(known & set(covered)),
        "constraints_seen_as_errors": len(set(errors)),
        "uncovered": uncovered,
        "uncovered_error_constraints": uncovered_errors,
        "covered": {key: covered[key] for key in sorted(covered)},
        "errors": {key: errors[key] for key in sorted(errors)},
    }
    destination = ROOT / args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "sentences": len(sentences),
        "known_constraints": len(known),
        "covered_constraints": report["covered_constraints"],
        "constraints_seen_as_errors": report["constraints_seen_as_errors"],
        "uncovered": uncovered,
    }, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
