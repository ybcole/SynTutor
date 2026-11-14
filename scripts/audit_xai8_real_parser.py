#!/usr/bin/env python3
"""XAI-8 parser-backed, privacy-preserving structural/safety measurement.

Requires real pinned spaCy/Benepar runtime. Independently parses one new
unadjudicated safety probe in each English category. No sentence strings,
user identifiers, external LLM output or human truth labels are reported.
Revision checks are real re-parses, but do NOT validate semantic preservation.
"""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"server"))
from xai5_repair import recheck_revisions
from audit_xai0_baseline import inspect_case

def run():
    source=json.loads((ROOT/"evaluation/xai8_safety_probes.json").read_text())
    first={}
    for row in source["cases"]:
        first.setdefault(row["family"],row)
    stats=Counter()
    timing=[]
    failures=Counter()
    enabled=0
    for family,row in sorted(first.items()):
        result=inspect_case({
            "id":row["id"],"family":family,"intent":"context_sensitive",
            "text":row["text"],"selected_sentence_index":0
        })
        stats["examined"]+=1
        stats["parsed"]+=result["parser_status"]=="parsed"
        stats["normalized"]+=result["br_status"]=="normalized"
        stats["unresolved"]+=result["br_status"]=="unresolved"
        stats["working_tree"]+=bool(result.get("working_tree_observed"))
        if result.get("root_endpoint_checked"):
            stats["root_endpoint_checked"]+=1
            if not result["root_endpoint_matches"]:
                failures["root_evidence_mismatch"]+=1
        enabled+=result.get("cambridge",{}).get("enabled_count",0)
        if result["parser_status"]=="parse_error":
            failures["parser_exception"]+=1
        if result["br_status"]=="audit_error":
            failures["normalizer_exception"]+=1
        if result["explanation_status"]=="audit_error":
            failures["explanation_exception"]+=1
        if result["timing_ms"].get("total") is not None:
            timing.append(result["timing_ms"]["total"])
    # Two independent multiple-error snapshots, with real parser,
    # source-gated re-evaluation and immutable learner edits.
    revision_groups=[
        ("She have went to the store yesterday.",[
            {"text":"She has went to the store yesterday."},
            {"text":"She has gone to the store yesterday.","parent_version_id":"v1"}]),
        ("The boys is carrying a boxes.",[
            {"text":"The boys are carrying a boxes."},
            {"text":"The boys are carrying boxes.","parent_version_id":"v1"}]),
    ]
    for text,edits in revision_groups:
        result=recheck_revisions({"text":text,"candidates":edits})
        stats["revision_groups"]+=1
        stats["independently_reparsed_revisions"]+=len(result["revisions"])
        if result["whole_sentence_certified"] or any(
                c["whole_sentence_certified"] or c["meaning_status"]!="not_assessed"
                for c in result["revisions"]):
            failures["unsupported_revision_claim"]+=1
        if any(c["snapshot"]["text"] != e["text"]
               for c,e in zip(result["revisions"],edits)):
            failures["revision_source_mismatch"]+=1
        if any(c["parent_version_id"] != e.get("parent_version_id","u0")
               for c,e in zip(result["revisions"],edits)):
            failures["revision_parent_mismatch"]+=1
    return {
        "schema_version":"xai8-real-parser-smoke-1.0.0",
        "language_policy":"ENGLISH_ONLY",
        "evaluation_basis":"UNADJUDICATED_NEW_PROBES_WITH_REAL_PINNED_PARSER",
        "case_counts":dict(sorted(stats.items())),
        "source_enabled_runtime_rule_observations":enabled,
        "latency_ms_median":round(statistics.median(timing),3) if timing else None,
        "latency_ms_max":round(max(timing),3) if timing else None,
        "independent_human_accuracy_cases":0,
        "independent_expert_review":False,
        "grammar_error_precision":None,
        "grammar_error_recall":None,
        "repair_meaning_preservation":None,
        "new_verified_diagnostic_rollout_enabled":False,
        "raw_sentence_or_user_text_recorded":False,
        "failures":dict(failures),
        "technical_smoke_pass":not failures and stats["parsed"]>=9
             and stats["revision_groups"]==2 and stats["independently_reparsed_revisions"]==4,
    }

if __name__=="__main__":
    target=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/"artifacts/xai8-real-parser-smoke.json"
    report=run()
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    if not report["technical_smoke_pass"]:sys.exit(1)
