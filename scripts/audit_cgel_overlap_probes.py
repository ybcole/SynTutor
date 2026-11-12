"""Observe legacy and matrix findings on Cambridge overlap probes."""

import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
from parse_engine import NodeBuilder, analyze, parse_parse_string
from ruleset import collect

# These small development probes are not a gold corpus.
CASES = [
("modal form", "She can goes.", "(S (NP (PRP She)) (VP (MD can) (VP (VBZ goes))) (. .))"),
("modal to", "She can to go.", "(S (NP (PRP She)) (VP (MD can) (S (VP (TO to) (VP (VB go))))) (. .))"),
("modal control", "She can go.", "(S (NP (PRP She)) (VP (MD can) (VP (VB go))) (. .))"),
("ought control", "She ought to leave.", "(S (NP (PRP She)) (VP (MD ought) (S (VP (TO to) (VP (VB leave))))) (. .))"),
("active causative", "She made him to wait.", "(S (NP (PRP She)) (VP (VBD made) (NP (PRP him)) (S (VP (TO to) (VP (VB wait))))) (. .))"),
("active causative control", "She made him wait.", "(S (NP (PRP She)) (VP (VBD made) (NP (PRP him)) (S (VP (VB wait)))) (. .))"),
("passive causative", "We were made wait outside.", "(S (NP (PRP We)) (VP (VBD were) (VP (VBN made) (S (VP (VB wait) (ADVP (RB outside)))))) (. .))"),
("passive causative control", "We were made to wait outside.", "(S (NP (PRP We)) (VP (VBD were) (VP (VBN made) (S (VP (TO to) (VP (VB wait) (ADVP (RB outside))))))) (. .))"),
("enjoy action", "She enjoys to run.", "(S (NP (PRP She)) (VP (VBZ enjoys) (S (VP (TO to) (VP (VB run))))) (. .))"),
("enjoy noun control", "She enjoys the music.", "(S (NP (PRP She)) (VP (VBZ enjoys) (NP (DT the) (NN music))) (. .))"),
("modal coordination control", "She may or may not finish.", "(S (NP (PRP She)) (VP (MD may) (CC or) (MD may) (RB not) (VP (VB finish))) (. .))"),
]


def summarize_matrix(evaluation):
    summary = evaluation["summary"]
    node_errors = []
    attached_errors = []
    for node_id, detail in evaluation["details"].items():
        if detail["status"] == "error":
            node_errors.append({
                "node_id": node_id,
                "rule_id": detail.get("rule_id"),
                "constraint": detail.get("constraint"),
                "surface": detail.get("surface"),
                "suggested_fix": (detail.get("remediation") or {}).get("suggested_fix"),
            })
        for finding in detail.get("findings", []):
            if finding["status"] == "error":
                attached_errors.append({
                    "attached_to": node_id,
                    "node_id": finding.get("node_id"),
                    "rule_id": finding.get("rule_id"),
                    "constraint": finding.get("constraint"),
                })
    return {
        "verdict": summary["verdict"],
        "checker_errors": summary["checker_errors"],
        "node_errors": node_errors,
        "attached_errors": attached_errors,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", action="store_true",
                        help="Use hand-authored trees instead of the configured parser")
    parser.add_argument("--matrix", action="store_true",
                        help="Also observe matrix verdicts, node errors, and attached findings")
    args = parser.parse_args()
    if args.matrix:
        from matrix import evaluate
    observations = []
    for label, sentence, fixture in CASES:
        if args.fixtures:
            leaf_count = len(re.findall(r"\([^()]+\)", fixture))
            tree = NodeBuilder().build(parse_parse_string(fixture), leaf_count=leaf_count)
        else:
            tree = analyze(sentence)["root"]
        errors = [
            {key: finding.get(key) for key in ("rule_id", "constraint", "node_id")}
            for finding in collect(sentence, tree)
            if finding["status"] == "error"
        ]
        observation = {"probe": label, "sentence": sentence, "errors": errors}
        if args.matrix:
            observation["matrix"] = summarize_matrix(evaluate(tree, text=sentence))
        observations.append(observation)
    print(json.dumps({
        "input": "hand_authored_trees" if args.fixtures else "configured_parser",
        "checker": "ruleset.collect",
        "matrix_included": args.matrix,
        "observations": observations,
    }, indent=2))


if __name__ == "__main__":
    main()
