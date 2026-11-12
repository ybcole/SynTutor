"""Measure the existing COMP-034 candidate on held-out configured-parser cases."""

import json

from audit_cgel_overlap_probes import observe_modal
from cgel_modal_parser_probe import probe_modal_parser
from parse_engine import analyze


def observe(case):
    report = observe_modal(analyze(case["sentence"]), probe_modal_parser)
    candidates = report["probe"]["candidates"]
    reparse = candidates[0].get("reparse_observation", {}) if len(candidates) == 1 else {}
    expected = case["expected_sentence"]
    exact = expected is not None and reparse.get("sentence") == expected
    return {**case, **report, "exact_repair": exact,
            "exact_repair_clears_candidate": exact and reparse.get("candidate_count") == 0}


def summarize(rows):
    return {
        "cases": len(rows),
        "cases_with_findings": sum(bool(row["probe"]["candidates"]) for row in rows),
        "cases_not_evaluated": sum(row["probe"]["status"] == "not_evaluated" for row in rows),
        "cases_with_canonical_node_links": sum(
            any("canonical_observation" in candidate for candidate in row["probe"]["candidates"])
            for row in rows
        ),
        "exact_repairs": sum(row["exact_repair"] for row in rows),
        "exact_repairs_clearing_candidate": sum(row["exact_repair_clears_candidate"] for row in rows),
    }


def main():
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "evaluation/cgel_modal_complement_heldout.json"
    corpus = json.loads(path.read_text(encoding="utf-8"))
    cases = corpus["cases"]
    if len({case["id"] for case in cases}) != len(cases) or len({case["sentence"] for case in cases}) != len(cases):
        raise ValueError("Duplicate case ID or sentence")
    rows = [observe(case) for case in cases]
    groups = {
        name: summarize([row for row in rows if row["group"] == name])
        for name in dict.fromkeys(row["group"] for row in rows)
    }
    print(json.dumps({"rule_id": corpus["rule_id"], "variety": corpus["variety"],
                      "groups": groups, "observations": rows}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
