#!/usr/bin/env python3
"""XAI-8 source-tree/probe evidence audit and fail-closed release decision.

No parser models or external AI are needed for the model-free engineering
audit. It tests *software contracts*, NOT human-rated grammatical correctness.
No raw user/sentence text enters the output report or telemetry. Existing
XAI-0 development cases remain separate from the 53 held-out safety probes.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))

from jsonschema import Draft202012Validator
from burton_roberts import canonicalize_gold_record
from learner_explanations import compose_learner_explanation
from xai4_partial import evaluate_xai4, load_manifest
from xai_composer import compose_explanations
from xai_facts import build_fact_graph
from xai6_naturalizer import naturalize, load_policy as load_xai6_policy
from xai8_release import load_policy, evaluate_release, QUALITY_METRICS

PROBE_PATH = ROOT / "evaluation/xai8_safety_probes.json"
PROBE_SCHEMA = ROOT / "evaluation/xai8_safety_probes.schema.json"
DEVELOPMENT_PATH = ROOT / "evaluation/xai0_development_cases.json"
LEARNING_PATH = ROOT / "web/content/lessons/course.json"
BANNED_UI = (
    "b-r structural analysis", "book evidence", "cambridge grammar checks",
    "tree rule references", "xai-3", "approved runtime rules",
    "no reviewed book", "source-reviewed", "recorded token interval",
    "observed positions:", "benepar",
)


def _p95(values: list[float]) -> float | None:
    if not values:
        return None
    values = sorted(values)
    i = (len(values) - 1) * .95
    low = int(i)
    high = min(len(values) - 1, low + 1)
    return round(values[low] + (values[high] - values[low]) * (i - low), 3)


def validate_probes(path: Path = PROBE_PATH) -> dict:
    probe = json.loads(path.read_text(encoding="utf-8"))
    schema = json.loads(PROBE_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(probe)
    ids = [r["id"] for r in probe["cases"]]
    texts = [r["text"] for r in probe["cases"]]
    if len(ids) != len(set(ids)) or len(texts) != len(set(texts)):
        raise ValueError("Duplicate probe identifiers or duplicate evaluation inputs")
    if len({r["family"] for r in probe["cases"]}) < 12:
        raise ValueError("XAI-8 needs at least twelve distinct probe families")
    dev = json.loads(DEVELOPMENT_PATH.read_text(encoding="utf-8"))
    if dev["review_status"] != "NOT_HUMAN_ADJUDICATED":
        raise ValueError("Developer set cannot suddenly claim human adjudication")
    overlap = len(set(texts) & {row["text"] for row in dev["cases"]})
    if overlap:
        raise ValueError("XAI-8 probes must be disjoint from existing XAI-0 development input")
    return probe


def benchmark() -> dict:
    data = validate_probes()
    policy = load_policy()
    xai6 = load_xai6_policy()
    manifest, _ = load_manifest()
    fail = Counter()
    signals = Counter()
    intents = Counter(row["family"] for row in data["cases"])
    times: list[float] = []
    total_issues = 0
    globally_certified = 0

    # Safety probes are unadjudicated, so "VIOLATED" is NEVER compared with a
    # made-up correct/incorrect gold label. Only source authorization matters.
    for row in data["cases"]:
        start = time.perf_counter()
        evaluation = evaluate_xai4(row["text"], analysis_status="unresolved")
        times.append((time.perf_counter() - start) * 1000)
        total_issues += len(evaluation["findings"])
        globally_certified += int(evaluation["global_verdict"]["whole_sentence_certified"])
        if evaluation["language_policy"] != "ENGLISH_ONLY":
            fail["language_policy"] += 1
        if evaluation["global_verdict"]["whole_sentence_certified"]:
            fail["global_verdict"] += 1
        if evaluation["findings"]:
            fail["unauthorized_grammar_findings"] += len(evaluation["findings"])
        if evaluation["enabled_rule_ids"]:
            fail["runtime_rule_enabled"] += len(evaluation["enabled_rule_ids"])
        for item in evaluation["evaluations"]:
            signals[item["status"]] += 1

    course = json.loads(LEARNING_PATH.read_text(encoding="utf-8"))
    source_records = [
        ("lesson", {"status": "normalized", "tree": lesson["worked_example"]["tree"]})
        for lesson in course["lessons"]
        if isinstance(lesson.get("worked_example", {}).get("tree"), dict)
    ]
    lesson_count = len(source_records)
    book_count = 0
    # Reuse known source trees only as *structural* fixtures. Their provenance
    # does not independently adjudicate whether every learner explanation is
    # linguistically correct.
    for path in sorted((ROOT / "web/content/book").glob("ch*.trees.json")):
        data_book = json.loads(path.read_text(encoding="utf-8"))
        per_chapter = 0
        for gold in data_book.get("trees", []):
            result = canonicalize_gold_record(gold, data_book)
            if result.get("status") != "normalized":
                continue
            source_records.append(("book_source_structure", result))
            book_count += 1
            per_chapter += 1
            if per_chapter == 3:
                break
    node_count = 0
    nonempty_paragraphs = 0
    proof_atom_records = 0
    proof_atom_matches = 0
    tested_model_requests = 0
    model_calls = 0
    nonempty_learner_quotes = 0
    explanation_times: list[float] = []
    for sample_kind, analysis in source_records:
        try:
            graph = build_fact_graph(analysis)
            if graph["status"] not in {"observed", "provisional"}:
                fail["source_unavailable"] += 1
                continue
            present_atom_ids = {atom["fact_id"] for atom in graph["atoms"]}
            for node in graph["nodes"]:
                start = time.perf_counter()
                ident = node["node_id"]
                content = compose_learner_explanation(graph, node_id=ident)
                proof = compose_explanations(graph, node_id=ident)
                explanation_times.append((time.perf_counter() - start) * 1000)
                node_count += 1
                if (content["status"] in {"observed", "provisional"}
                        and content["text"].strip() and "\n" not in content["text"]
                        and len(content["text"]) <= 750):
                    nonempty_paragraphs += 1
                else:
                    fail["learner_paragraph_unavailable"] += 1
                if (content["whole_sentence_certified"] or content["source_claim_ids"]
                        or any(bad in content["text"].lower() for bad in BANNED_UI)):
                    fail["unsupported_learner_copy"] += 1
                if node["surface"] and "“" in content["text"]:
                    nonempty_learner_quotes += 1
                if not proof["items"] or len(proof["items"]) != 1:
                    fail["fact_proof_missing"] += 1
                for item in proof["items"]:
                    ids = item["evidence_atom_ids"]
                    proof_atom_records += len(ids)
                    proof_atom_matches += sum(x in present_atom_ids for x in ids)
                    if (not ids or set(ids) != {x["fact_id"] for x in item["proof"]}
                            or item["source_ids"] or item["function_status"] != "unknown_unlicensed"):
                        fail["fact_proof_unauthorized"] += 1
            # Validate production XAI-6 gating against actual witnessed tree
            # input; no provider callbacks or external network calls are used.
            first = graph["nodes"][0]["node_id"]
            for_selection = build_fact_graph(analysis, node_id=first)
            context = compose_explanations(for_selection, node_id=first)
            natural = naturalize(for_selection, context, node_id=first)
            tested_model_requests += 1
            model_calls += natural["provider_calls"]
            if natural["status"] != "disabled":
                fail["model_not_disabled"] += 1
        except (ValueError, KeyError, TypeError, RecursionError) as exc:
            # No text or exception string in anonymized report.
            fail["source_contract_exception"] += 1

    # All English accuracy / human-comprehension metrics remain NULL, not 0.
    report = {
        "schema_version": "xai8-evaluation-1.0.0",
        "language_policy": "ENGLISH_ONLY",
        "evaluation_basis": "UNADJUDICATED_DEVELOPER_PROBES_AND_CANONICAL_SOURCE_STRUCTURES",
        "probe_count": len(data["cases"]),
        "probe_family_count": len(intents),
        "probe_family_counts": dict(sorted(intents.items())),
        "xai0_development_case_count": len(json.loads(DEVELOPMENT_PATH.read_text(encoding="utf-8"))["cases"]),
        "xai0_text_overlap_count": 0,
        "probe_candidate_observation_status_counts": dict(sorted(signals.items())),
        "probe_verified_grammar_finding_count": total_issues,
        "runtime_enabled_cambridge_rule_count": len(manifest["runtime_enabled_rule_ids"]),
        "production_ai_model_enabled": xai6["model_enabled"],
        "source_lesson_tree_count": lesson_count,
        "source_book_tree_count": book_count,
        "source_tree_nodes": node_count,
        "source_node_paragraph_coverage": round(nonempty_paragraphs / node_count, 6) if node_count else 0,
        "source_fact_proof_completeness": round(proof_atom_matches / proof_atom_records, 6) if proof_atom_records else 0,
        "source_fact_proof_total": proof_atom_records,
        "source_quoted_span_count": nonempty_learner_quotes,
        "unsupported_book_verified_claim_count": total_issues,
        "whole_sentence_certifications": globally_certified,
        "model_provider_calls": model_calls,
        "model_request_checks": tested_model_requests,
        "raw_text_telemetry_events": 0,
        "evaluation_failures": dict(fail),
        "evaluation_failure_count": sum(fail.values()),
        "independent_expert_cases": 0,
        "independent_linguists": 0,
        "timings_ms": {
            "probe_evaluation_p50": round(statistics.median(times), 3) if times else None,
            "probe_evaluation_p95": _p95(times),
            "node_composition_p50": round(statistics.median(explanation_times), 3) if explanation_times else None,
            "node_composition_p95": _p95(explanation_times),
        },
        **{key: None for key in QUALITY_METRICS},
    }
    report["release"] = evaluate_release(report, policy)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-technical-pass", action="store_true")
    args = parser.parse_args()
    report = benchmark()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                               encoding="utf-8")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.require_technical_pass and (
        report["release"]["technical_acceptance"] != "PASS"
        or report["release"]["release_decision"] != "HOLD"
        or report["release"]["new_diagnostic_rollout_permitted"]
    ):
        sys.exit(1)


if __name__ == "__main__":
    main()
