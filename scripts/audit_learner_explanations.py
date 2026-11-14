#!/usr/bin/env python3
"""Model-free coverage audit of learner-facing concise English grammar prose.

Development/lesson/source structures are NOT an independent human correctness
study. This measures a narrow software acceptance contract only; no judgement
is made about universal English grammaticality.
"""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"server"))
from jsonschema import Draft202012Validator
from learner_explanations import compose_learner_explanation
from xai_facts import build_fact_graph
from burton_roberts import canonicalize_gold_record

BANNED=("b-r structural analysis","book evidence","ch5 p.","rule references",
        "approved runtime","xai-3","benepar","cambridge grammar checks",
        "observed positions:","recorded token interval","source-reviewed")
SELF_REFERENCE_PHRASES=("larger expression","is part of","is a part of",
                        "part of the larger","position in","built around",
                        "beginning with","preposition phrase","verb phrase",
                        "clause ","in “")

def run():
    validator=Draft202012Validator(json.loads(
        (ROOT/"grammar/learner_explanation.schema.json").read_text()))
    families=Counter()
    status=Counter()
    examples=0
    checked=0
    failures=[]
    self_reference_failures=0
    duplicate_parent_failures=0
    def audit(key,analysis):
        nonlocal checked,self_reference_failures,duplicate_parent_failures
        try:
            graph=build_fact_graph(analysis)
            if graph["status"] not in {"observed","provisional"}:return
            nodes=graph["nodes"]
            by_id={node["node_id"]:node for node in nodes}
            texts={node["node_id"]:compose_learner_explanation(
                graph,node_id=node["node_id"]) for node in nodes}
            for node in nodes:
                result=texts[node["node_id"]]
                errors=list(validator.iter_errors(result))
                if errors:
                    failures.append(key+":schema")
                    continue
                text=result["text"]
                if (not text.strip() or "\n" in text or len(text)>750
                        or any(b in text.lower() for b in BANNED)
                        or result["source_claim_ids"] or result["whole_sentence_certified"]):
                    failures.append(key+":student-copy")
                surface=str(node.get("surface") or "").strip()
                if surface and any(f"{phrase}“{surface}”" in text
                                   for phrase in SELF_REFERENCE_PHRASES):
                    self_reference_failures+=1
                    failures.append(key+":"+node["node_id"]+":self-reference")
                parent=by_id.get(node.get("parent_id"))
                if parent is not None and text==texts.get(parent["node_id"]):
                    duplicate_parent_failures+=1
                    failures.append(key+":"+node["node_id"]+":duplicate-parent")
                checked+=1
                status[result["status"]]+=1
                families[node.get("label") or node["kind"]]+=1
        except (ValueError,KeyError,TypeError,RecursionError):
            failures.append(key+":unavailable")
    course=json.loads((ROOT/"web/content/lessons/course.json").read_text())
    for lesson in course["lessons"]:
        t=lesson.get("worked_example",{}).get("tree")
        if isinstance(t,dict):
            examples+=1
            audit("lesson:"+lesson["lesson_id"],{"status":"normalized","tree":t})
    gold=0
    for path in sorted((ROOT/"web/content/book").glob("ch*.trees.json")):
        data=json.loads(path.read_text())
        for row in data.get("trees",[]):
            entry=canonicalize_gold_record(row,data)
            if entry.get("status")=="normalized":
                gold+=1
                audit(path.stem+":"+str(row.get("id")),entry)
    return {
        "schema_version":"learner-audit-1.1.0",
        "language_policy":"ENGLISH_ONLY",
        "lesson_trees":examples,"normalized_gold_trees":gold,
        "examined_nodes":checked,"status_counts":dict(status),
        "observed_label_counts":dict(sorted(families.items())),
        "self_reference_failures":self_reference_failures,
        "duplicate_parent_failures":duplicate_parent_failures,
        "model_network_calls":0,
        "independent_human_accuracy_cases":0,
        "unverified_rule_activations":0,
        "failures":failures,
        "software_gate_passed":not failures and examples>=10 and checked>=100,
        "human_grammar_accuracy_certified":False,
    }

if __name__=="__main__":
    report=run()
    print(json.dumps(report,indent=2))
    if not report["software_gate_passed"]:sys.exit(1)
