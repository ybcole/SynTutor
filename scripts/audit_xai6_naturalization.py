#!/usr/bin/env python3
"""XAI-6 offline baseline/proof audit; no API calls, no external model.

This is NOT the independent human blind readability comparison required to
enable the AI style layer. It verifies deterministic structural grounding and
the production off-switch across reviewed source trees.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

from jsonschema import Draft202012Validator
from xai6_naturalizer import load_policy, naturalize, promotion_eligible
from xai_facts import build_fact_graph
from xai_composer import compose_explanations
from burton_roberts import canonicalize_gold_record

def measure():
    records=[]
    course=json.loads((ROOT/"web/content/lessons/course.json").read_text())
    for lesson in course["lessons"]:
        t=lesson.get("worked_example",{}).get("tree")
        if isinstance(t,dict):
            records.append(("lesson:"+lesson["lesson_id"],{"status":"normalized","tree":t}))
    source_trees=0
    for path in sorted((ROOT/"web/content/book").glob("ch*.trees.json")):
        data=json.loads(path.read_text())
        valid=0
        for source in data.get("trees",[]):
            entry=canonicalize_gold_record(source,data)
            if entry.get("status")!="normalized":
                continue
            records.append((path.stem+":"+str(source.get("id")),entry))
            valid+=1
            source_trees+=1
            if valid>=4:
                break
    tested=0
    fail=[]
    schema=Draft202012Validator(json.loads((ROOT/"grammar/xai6_result.schema.json").read_text()))
    policy=load_policy()
    for name,analysis in records:
        graph=build_fact_graph(analysis)
        if graph["status"] not in {"observed","provisional"}:
            fail.append(name+": no factual graph")
            continue
        for node in graph["nodes"]:
            short=compose_explanations(graph,node_id=node["node_id"])
            out=naturalize(graph,short,node_id=node["node_id"])
            problems=list(schema.iter_errors(out))
            if problems:
                fail.append(name+":"+node["node_id"]+": schema "+problems[0].message)
                continue
            if (out["status"]!="disabled" or out["provider_calls"]!=0
                    or out["paragraphs"][0]["text"]!=short["items"][0]["short"]
                    or out["paragraphs"][1]["text"]!=short["items"][0]["deep"]
                    or out["source_ids"] or out["whole_sentence_certified"]):
                fail.append(name+":"+node["node_id"]+": baseline/proof/policy diverged")
            tested+=1
    report={
        "schema_version":"xai6-audit-1.0.0",
        "language_policy":"ENGLISH_ONLY",
        "lesson_source_trees":len(records)-source_trees,
        "gold_source_trees":source_trees,
        "tested_tree_nodes":tested,
        "baseline_identity_count":tested-len(fail),
        "default_model_calls":0,
        "default_model_enabled":policy["model_enabled"],
        "promotion_eligible":promotion_eligible(policy),
        "independent_blind_human_sample_size":0,
        "naturalizer_readability_gain_proven":False,
        "naturalizer_source_fidelity_superiority_proven":False,
        "auto_enabled_in_production":False,
        "failures":fail,
        "release_decision":"RETAIN_DETERMINISTIC_XAI3_FALLBACK",
    }
    return report

if __name__=="__main__":
    report=measure()
    print(json.dumps(report,indent=2))
    if report["failures"] or report["tested_tree_nodes"]<100 or report["default_model_enabled"]:
        sys.exit(1)
