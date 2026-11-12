"""Measure an unchanged offline candidate on original sentences using the configured parser."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from cgel_passive_make_candidate import probe_passive_make
from parse_engine import analyze


def observe(case, variety):
    sentence = case["sentence"]
    expected = case["expected_sentence"]
    parsed = analyze(sentence)
    result = probe_passive_make(sentence, parsed["root"], variety=variety)
    edits = []
    for candidate in result["candidates"]:
        hint = candidate["edit_hint"]
        start, end = hint["char_span"]
        corrected = sentence[:start] + hint["replacement"] + sentence[end:]
        repaired = analyze(corrected)
        recheck = probe_passive_make(corrected, repaired["root"], variety=variety)
        edits.append({
            "sentence": corrected,
            "recheck_status": recheck["status"],
            "remaining_candidates": len(recheck["candidates"]),
        })
    exact_repair = expected is not None and len(edits) == 1 and edits[0]["sentence"] == expected
    return {
        **case,
        "status": result["status"],
        "reason": result.get("reason"),
        "parse": parsed["parse_string"],
        "candidate_count": len(edits),
        "exact_repair": exact_repair,
        "edits": edits,
    }


def main():
    corpus = json.loads((ROOT / "evaluation/cgel_passive_make_evaluation.json").read_text(encoding="utf-8"))
    cases = corpus["cases"]
    assert len({case["id"] for case in cases}) == len(cases), "Duplicate case IDs"
    assert len({case["sentence"] for case in cases}) == len(cases), "Duplicate inputs"
    observations = [observe(case, corpus["variety"]) for case in cases]
    positives = [row for row in observations if row["expected_sentence"] is not None]
    controls = [row for row in observations if row["expected_sentence"] is None]
    report = {
        "rule_id": corpus["rule_id"],
        "variety": corpus["variety"],
        "summary": {
            "positive_cases": len(positives),
            "positive_cases_with_candidates": sum(row["candidate_count"] > 0 for row in positives),
            "exact_repairs": sum(row["exact_repair"] for row in positives),
            "exact_repairs_without_a_candidate_after_reparse": sum(
                row["exact_repair"] and row["edits"][0]["recheck_status"] == "candidate_only"
                and row["edits"][0]["remaining_candidates"] == 0 for row in positives
            ),
            "valid_controls": len(controls),
            "controls_with_candidates": sum(row["candidate_count"] > 0 for row in controls),
            "controls_not_evaluated": sum(row["status"] == "not_evaluated" for row in controls),
        },
        "observations": observations,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
