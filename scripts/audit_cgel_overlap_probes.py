"""Observe legacy and matrix findings on Cambridge overlap probes."""

import argparse
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
from cgel_passive_make_candidate import probe_passive_make
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


# Freeze these expectations before running the configured parser.
MODAL_EVALUATION_CASES = [
    ("third-person form", "The courier might arrives before noon.", "The courier might arrive before noon."),
    ("third-person form", "Our guide will brings a spare lantern.", "Our guide will bring a spare lantern."),
    ("third-person form", "The committee should approves the request.", "The committee should approve the request."),
    ("extra to", "The caretaker must to lock the side gate.", "The caretaker must lock the side gate."),
    ("extra to", "A volunteer could to move the cabinet.", "A volunteer could move the cabinet."),
    ("extra to", "The hikers may to cross the bridge.", "The hikers may cross the bridge."),
    ("stress: negation", "The courier might not arrives before noon.", "The courier might not arrive before noon."),
    ("stress: inversion", "Could the courier arrives before noon?", "Could the courier arrive before noon?"),
    ("stress: intervening adjunct", "The courier might soon arrives.", "The courier might soon arrive."),
    ("control: plain", "The courier might arrive before noon.", None),
    ("control: perfect", "The courier might have arrived already.", None),
    ("control: passive", "The side gate must be locked.", None),
    ("control: noncentral modal", "The caretaker ought to lock the gate.", None),
    ("control: lexical need", "The guide needs to bring a spare lantern.", None),
    ("control: coordination", "The hikers may or may not cross the bridge.", None),
    ("control: lexical can", "The crew cans peaches in August.", None),
    ("control: infinitival purpose", "The caretaker will wait to lock the gate.", None),
    ("control: quotation", "The sign read, “You may cross the bridge.”", None),
]


def evaluate_modal_cases(probe_modal_parser):
    rows = []
    for group, sentence, expected in MODAL_EVALUATION_CASES:
        observation = observe_modal(analyze(sentence), probe_modal_parser)
        candidates = observation["probe"]["candidates"]
        exact_reparse = len(candidates) == 1 and (
            candidates[0].get("reparse_observation", {}).get("sentence") == expected
            and candidates[0].get("reparse_observation", {}).get("candidate_count") == 0
        )
        rows.append({
            "group": group,
            "sentence": sentence,
            "expected_repair": expected,
            "exact_reparse": exact_reparse,
            **observation,
        })
    return rows


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


def observe_modal(analysis, probe_modal_parser):
    from burton_roberts import build_canonical_analysis
    from xai_facts import build_fact_graph

    sentence = analysis["sentence"]
    probe = probe_modal_parser(sentence, analysis["root"], variety="standard_english")
    canonical = build_canonical_analysis(analysis)
    report = {"parse": analysis["parse_string"], "probe": probe,
              "canonical_status": canonical["status"],
              "canonical_reason_codes": [row["code"] for row in canonical["reasons"]]}
    if not probe["candidates"]:
        return report
    graph = build_fact_graph(canonical) if canonical["status"] == "normalized" else {}
    by_id = {node["node_id"]: node for node in graph.get("nodes", []) if graph["status"] == "observed"}
    by_span = {tuple(token["char_span"]): token for token in graph.get("token_index", [])
               if graph["status"] == "observed"}
    for candidate in probe["candidates"]:
        relation = candidate["relation"]
        labels = {"governor": {"MOD"}, "dependent": {"V", "AUX"}}
        nodes = {}
        for role, expected in labels.items():
            token = by_span.get(tuple(relation[f"{role}_char_span"]))
            if token and not token["opaque"]:
                node = next((by_id[node_id] for node_id in token["node_ids_innermost_first"]
                             if by_id[node_id]["label"] in expected), None)
                if node:
                    nodes[role] = node
        if len(nodes) == 2:
            common = set(nodes["governor"]["ancestor_ids"]) & set(nodes["dependent"]["ancestor_ids"])
            vp = next((node_id for node_id in nodes["governor"]["ancestor_ids"]
                       if node_id in common and by_id[node_id]["label"] == "VP"), None)
            if vp:
                candidate["canonical_observation"] = {
                    "modal_node_id": nodes["governor"]["node_id"],
                    "dependent_node_id": nodes["dependent"]["node_id"],
                    "shared_vp_node_id": vp,
                }
        hint = candidate.get("edit_hint")
        if hint:
            start, end = hint["char_span"]
            corrected = sentence[:start] + hint["replacement"] + sentence[end:]
            reparsed = analyze(corrected)
            candidate["reparse_observation"] = {
                "sentence": corrected,
                "candidate_count": len(probe_modal_parser(
                    corrected, reparsed["root"], variety="standard_english")["candidates"]),
            }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", action="store_true",
                        help="Use hand-authored trees instead of the configured parser")
    parser.add_argument("--matrix", action="store_true",
                        help="Also observe matrix verdicts, node errors, and attached findings")
    parser.add_argument("--passive-candidate", action="store_true",
                        help="Also observe the inactive passive causative candidate")
    parser.add_argument("--modal-candidate", action="store_true",
                        help="Observe parser-backed central modal candidates and canonical node alignment")
    parser.add_argument("--modal-evaluation", action="store_true",
                        help="Run the separate modal evaluation on configured parser output")
    args = parser.parse_args()
    if args.modal_evaluation:
        if args.fixtures or args.matrix or args.passive_candidate or args.modal_candidate:
            parser.error("--modal-evaluation runs separately on configured parser output")
        from cgel_modal_parser_probe import probe_modal_parser

        print(json.dumps({"input": "configured_parser",
                          "modal_evaluation": evaluate_modal_cases(probe_modal_parser)}, indent=2))
        return
    if args.modal_candidate and args.fixtures:
        parser.error("--modal-candidate requires configured parser output")
    if args.modal_candidate:
        from cgel_modal_parser_probe import probe_modal_parser
    if args.matrix:
        from matrix import evaluate
    observations = []
    for label, sentence, fixture in CASES:
        if args.fixtures:
            leaf_count = len(re.findall(r"\([^()]+\)", fixture))
            tree = NodeBuilder().build(parse_parse_string(fixture), leaf_count=leaf_count)
        else:
            analysis = analyze(sentence)
            tree = analysis["root"]
        errors = [
            {key: finding.get(key) for key in ("rule_id", "constraint", "node_id")}
            for finding in collect(sentence, tree)
            if finding["status"] == "error"
        ]
        observation = {"probe": label, "sentence": sentence, "errors": errors}
        if args.matrix:
            observation["matrix"] = summarize_matrix(evaluate(tree, text=sentence))
        if args.passive_candidate:
            probe = probe_passive_make(sentence, tree, variety="standard_english")
            observation["passive_make_candidate"] = probe
            if label == "passive causative":
                observation["passive_make_parse"] = fixture if args.fixtures else analysis["parse_string"]
            if not args.fixtures:
                for candidate in probe["candidates"]:
                    edit = candidate["edit_hint"]
                    start, end = edit["char_span"]
                    corrected = sentence[:start] + edit["replacement"] + sentence[end:]
                    corrected_tree = analyze(corrected)["root"]
                    recheck = probe_passive_make(corrected, corrected_tree, variety="standard_english")
                    candidate["reparse_observation"] = {
                        "sentence": corrected,
                        "candidate_count": len(recheck["candidates"]),
                        "candidate_status": recheck["status"],
                    }
                    if args.matrix:
                        candidate["reparse_observation"]["matrix_verdict"] = evaluate(
                            corrected_tree, text=corrected)["summary"]["verdict"]
        if args.modal_candidate:
            observation["modal_candidate"] = observe_modal(analysis, probe_modal_parser)
        observations.append(observation)
    print(json.dumps({
        "input": "hand_authored_trees" if args.fixtures else "configured_parser",
        "checker": "ruleset.collect",
        "matrix_included": args.matrix,
        "observations": observations,
    }, indent=2))


if __name__ == "__main__":
    main()
