"""Measure the offline candidate on original sentences using the configured parser."""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
from burton_roberts import build_canonical_analysis
from cgel_passive_make_candidate import probe_passive_make
from parse_engine import analyze
from xai_facts import build_fact_graph


def observe_clause_link(nodes, auxiliary, governor, dependent):
    """Observe a sister clause and co-indexed gaps in the normalized tree."""
    predicate = nodes.get(governor["parent_id"])
    if (not predicate or predicate["label"] != "VP" or auxiliary["label"] != "PASS"
            or auxiliary["parent_id"] not in predicate["ancestor_ids"]):
        return None
    children = [nodes[node_id] for node_id in predicate["child_ids"]]
    clause = next((node for node in children if node["label"] == "S-bar"
                   and node["node_id"] in dependent["ancestor_ids"]), None)
    if clause is None:
        return None
    lower_s = next((nodes[node_id] for node_id in clause["child_ids"]
                    if nodes[node_id]["label"] == "S"), None)
    if lower_s is None or not lower_s["child_ids"]:
        return None
    lower_subject = nodes[lower_s["child_ids"][0]]
    if lower_subject["label"] != "NP":
        return None
    object_gaps = [nodes[node_id] for node in children if node["label"] == "NP"
                   for node_id in node["child_ids"] if nodes[node_id]["kind"] == "gap"]
    subject_gaps = [nodes[node_id] for node_id in lower_subject["child_ids"]
                    if nodes[node_id]["kind"] == "gap"]
    for obj in object_gaps:
        for subj in subject_gaps:
            if obj["index"] is not None and obj["index"] == subj["index"]:
                return {"passive_node_id": auxiliary["node_id"], "predicate_node_id": predicate["node_id"],
                        "clause_node_id": clause["node_id"],
                        "object_gap_node_id": obj["node_id"], "subject_gap_node_id": subj["node_id"],
                        "shared_index": obj["index"]}
    return None


def observe_canonical(parsed, candidates=()):
    """Record canonical availability and overt node alignment without licensing a rule."""
    result = build_canonical_analysis(parsed)
    report = {
        "status": result["status"],
        "reason_codes": [reason["code"] for reason in result["reasons"]],
        "working_tree_available": bool(result.get("working_tree")),
        "candidate_nodes": [],
    }
    if result["status"] != "normalized" or not candidates:
        return report

    graph = build_fact_graph(result)
    if graph["status"] != "observed":
        return report
    nodes_by_id = {node["node_id"]: node for node in graph["nodes"]}
    tokens_by_span = {tuple(token["char_span"]): token for token in graph["token_index"]}
    for candidate in candidates:
        relation = candidate["relation"]
        evidence = {}
        auxiliary = parsed["tokens"][relation["passive_auxiliary_token_index"]]
        spans = {
            "auxiliary": (auxiliary["start"], auxiliary["end"]),
            "governor": tuple(relation["governor_char_span"]),
            "dependent": tuple(relation["dependent_char_span"]),
        }
        for role, span in spans.items():
            token = tokens_by_span.get(span)
            if token and not token["opaque"]:
                if role == "auxiliary":
                    lexical = next((nodes_by_id[node_id] for node_id in token["node_ids_innermost_first"]
                                    if nodes_by_id[node_id]["label"] == "PASS"), None)
                else:
                    lexical = nodes_by_id.get(token["lexical_ancestor_id"])
                if lexical:
                    evidence[role] = {"node_id": lexical["node_id"], "label": lexical["label"]}
        if spans.keys() <= evidence.keys():
            link = observe_clause_link(nodes_by_id, nodes_by_id[evidence["auxiliary"]["node_id"]],
                                       nodes_by_id[evidence["governor"]["node_id"]],
                                       nodes_by_id[evidence["dependent"]["node_id"]])
            if link:
                evidence["observed_clause_link"] = link
        report["candidate_nodes"].append(evidence)
    return report


def observe(case, variety):
    sentence = case["sentence"]
    expected = case["expected_sentence"]
    parsed = analyze(sentence)
    result = probe_passive_make(sentence, parsed["root"], variety=variety)
    canonical = observe_canonical(parsed, result["candidates"])
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
            "canonical": observe_canonical(repaired),
        })
    exact_repair = expected is not None and len(edits) == 1 and edits[0]["sentence"] == expected
    return {
        **case,
        "status": result["status"],
        "reason": result.get("reason"),
        "parse": parsed["parse_string"],
        "candidate_count": len(edits),
        "canonical": canonical,
        "exact_repair": exact_repair,
        "edits": edits,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", type=Path, nargs="?",
                        default=ROOT / "evaluation/cgel_passive_make_evaluation.json")
    args = parser.parse_args()
    corpus = json.loads(args.corpus.read_text(encoding="utf-8"))
    cases = corpus["cases"]
    assert len({case["id"] for case in cases}) == len(cases), "Duplicate case IDs"
    assert len({case["sentence"] for case in cases}) == len(cases), "Duplicate inputs"
    observations = [observe(case, corpus["variety"]) for case in cases]
    positives = [row for row in observations if row["expected_sentence"] is not None]
    controls = [row for row in observations if row["expected_sentence"] is None]
    report = {
        "corpus": args.corpus.name,
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
            "positive_cases_with_normalized_canonical_tree": sum(
                row["canonical"]["status"] == "normalized" for row in positives
            ),
            "positive_cases_with_both_candidate_nodes": sum(
                any({"governor", "dependent"} <= evidence.keys()
                    for evidence in row["canonical"]["candidate_nodes"])
                for row in positives
            ),
            "positive_cases_with_observed_clause_link": sum(
                any("observed_clause_link" in evidence for evidence in row["canonical"]["candidate_nodes"])
                for row in positives
            ),
            "exact_repairs_with_normalized_canonical_tree": sum(
                row["exact_repair"] and row["edits"][0]["canonical"]["status"] == "normalized"
                for row in positives
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
