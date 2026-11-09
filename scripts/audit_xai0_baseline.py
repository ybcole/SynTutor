#!/usr/bin/env python3
"""XAI-0 empirical baseline: source-cited node coverage on real parser outputs.

This is an observation/report tool, NOT a grammaticality evaluator.
The development corpus is NOT a reviewed gold set. Positive-control and
malformed-probe labels are experimental buckets, not truth labels.

Parser mode (real pinned spaCy/Benepar required):
  python scripts/audit_xai0_baseline.py --output artifacts/xai0-baseline.json \
    --require-models --expected-count 116

Model-free structural contract smoke:
  python scripts/audit_xai0_baseline.py --validate-input-only
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "server"))
DATA_PATH = ROOT / "evaluation/xai0_development_cases.json"
VALID_INTENTS = {
    "grammatical_control", "ambiguous", "malformed_probe", "multi_error_probe",
    "variety_sensitive", "context_sensitive", "unsupported_or_mixed_language",
    "formatting_probe",
}
MINIMUM_FAMILIES = 10


def load_cases(path=DATA_PATH):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != "xai-0-development-1.0":
        raise ValueError("Unrecognized XAI-0 corpus schema version")
    if data.get("review_status") != "NOT_HUMAN_ADJUDICATED":
        raise ValueError("Development inputs cannot silently become adjudicated gold")
    if data.get("source_authority") != "none":
        raise ValueError("Development labels cannot claim primary-book source authority")
    rows = data.get("cases")
    if not isinstance(rows, list) or len(rows) < 50:
        raise ValueError("XAI-0 requires at least 50 development sentences")
    found = set()
    families = set()
    for row in rows:
        ident = row.get("id")
        if not isinstance(ident, str) or not ident or ident in found:
            raise ValueError("Missing/duplicate corpus case ID")
        found.add(ident)
        text = row.get("text")
        if not isinstance(text, str) or not text.strip() or len(text) > 650:
            raise ValueError(f"{ident}: invalid or excessive sentence length")
        if row.get("intent") not in VALID_INTENTS:
            raise ValueError(f"{ident}: invalid intent category")
        if row.get("expected_status") != "NOT_ADJUDICATED":
            raise ValueError(f"{ident}: unsupported grammaticality truth claim")
        index = row.get("selected_sentence_index")
        if type(index) is not int or index < 0:
            raise ValueError(f"{ident}: invalid selected_sentence_index")
        if not isinstance(row.get("family"), str) or not row["family"]:
            raise ValueError(f"{ident}: missing sentence family")
        families.add(row["family"])
    if len(families) < MINIMUM_FAMILIES:
        raise ValueError("Insufficient different syntactic/variety sentence families")
    return data


def percentile(samples, percentile_rank):
    """Observed runtime timing; never turn time into a claim of accuracy."""
    if not samples:
        return None
    values = sorted(samples)
    position = (len(values) - 1) * percentile_rank / 100
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    return round(values[lower] + (values[upper] - values[lower]) *
                 (position - lower), 2)


def walk_nodes(root):
    if not isinstance(root, dict):
        return
    stack = [root]
    while stack:
        node = stack.pop()
        if not isinstance(node, dict):
            continue
        yield node
        stack.extend(reversed(node.get("children", [])))


def status_counters(records):
    """All rates are denominated in actual observed cases, not unsupported guesses."""
    n = len(records)
    parsed = [row for row in records if row["parser_status"] == "parsed"]
    normalized = [row for row in parsed if row["br_status"] == "normalized"]
    node_total = sum(row["all_nodes"] for row in normalized)
    source_cited_nodes = sum(row["source_cited_nodes"] for row in normalized)
    terminal_total = sum(row["terminal_nodes"] for row in normalized)
    terminal_cited = sum(row["source_cited_terminal_nodes"] for row in normalized)
    parser_statuses = Counter(r["parser_status"] for r in records)
    br_statuses = Counter(r["br_status"] for r in parsed)
    xai_statuses = Counter(r["explanation_status"] for r in parsed)
    reason_codes = Counter(
        reason for row in parsed for reason in row.get("br_reason_codes", [])
    )
    labels_missing = Counter()
    labels_all = Counter()
    for row in normalized:
        labels_missing.update(row["labels_without_cited_explanation"])
        labels_all.update(row["all_labels"])
    suspicious = [r for r in parsed if r["control_vs_legacy_disagreement"]]
    probe_missed = [r for r in parsed if r["malformed_probe_vs_legacy_no_flag"]]
    times = [r["timing_ms"]["total"] for r in records if "timing_ms" in r]
    root_endpoint = [r for r in normalized if r.get("root_endpoint_checked")]
    by_family = {}
    for family in sorted({r["family"] for r in records}):
        family_rows = [r for r in records if r["family"] == family]
        family_normalized = [r for r in family_rows if r["br_status"] == "normalized"]
        by_family[family] = {
            "total": len(family_rows),
            "parsed": sum(r["parser_status"] == "parsed" for r in family_rows),
            "br_normalized": len(family_normalized),
            "br_unresolved": sum(r["br_status"] == "unresolved" for r in family_rows),
            "source_cited_nodes": sum(r["source_cited_nodes"]
                                      for r in family_normalized),
            "canonical_nodes": sum(r["all_nodes"] for r in family_normalized),
        }
    cited_labels = labels_all - labels_missing
    return {
        "cases_total": n,
        "parser_cases_parsed": len(parsed),
        "parser_status_counts": dict(sorted(parser_statuses.items())),
        "br_status_counts": dict(sorted(br_statuses.items())),
        "explanation_status_counts": dict(sorted(xai_statuses.items())),
        "br_normalized": len(normalized),
        "br_working_tree_observed": sum(r["working_tree_observed"] for r in parsed),
        "br_reason_counts": dict(reason_codes.most_common()),
        "canonical_nodes_total": node_total,
        "source_cited_nodes": source_cited_nodes,
        "source_cited_node_coverage_percent": round(
            source_cited_nodes * 100 / node_total, 2) if node_total else None,
        "canonical_terminal_nodes_total": terminal_total,
        "source_cited_terminal_nodes": terminal_cited,
        "source_cited_terminal_coverage_percent": round(
            terminal_cited * 100 / terminal_total, 2) if terminal_total else None,
        "canonical_node_labels": dict(labels_all.most_common()),
        "source_cited_node_labels": dict(cited_labels.most_common()),
        "labels_without_cited_explanation": dict(labels_missing.most_common()),
        "by_family": by_family,
        "root_endpoint_compatibility_checked": len(root_endpoint),
        "root_endpoint_mismatches": sum(not r["root_endpoint_matches"] for r in root_endpoint),
        "control_legacy_disagreements": len(suspicious),
        "control_legacy_disagreement_case_ids": [r["id"] for r in suspicious],
        "malformed_probe_legacy_no_flag_count": len(probe_missed),
        "malformed_probe_legacy_no_flag_ids": [r["id"] for r in probe_missed],
        "latency_ms_observed": {
            "p50_total": percentile(times, 50),
            "p95_total": percentile(times, 95),
            "max_total": round(max(times), 2) if times else None,
        },
        "notes": [
            "Source-cited node rate measures existing reviewed template *hits*, not factual/linguistic correctness, personalized wording or teaching quality.",
            "A normalized tree is not a claim the English sentence is grammatical.",
            "Legacy matrix disagreements are *triage candidates* only; corpus is not expert-adjudicated gold. No false-positive/false-negative rates can be certified.",
            "Model-free mode produces no parser-coverage results. Missing NLP models produce an explicit unavailable report or error, never simulated metrics.",
        ],
    }


def static_inventory(root=ROOT):
    from cambridge_registry import load_runtime_registry
    from explanations import load_registry
    templates = load_registry()
    runtime = load_runtime_registry()
    channels = Counter(row.get("channel") for row in templates.get("templates", []))
    return {
        "reviewed_template_rows": len(templates.get("templates", [])),
        "template_channels": dict(channels),
        "source_records": len(templates.get("sources", [])),
        "runtime_enabled_cambridge_rules": len(runtime.get("active_rules", [])),
        "runtime_diagnostic_codes": [
            x.get("code") for x in runtime.get("diagnostics", [])
        ],
        "correction_lineage": "PRE schema only, not wired to parser-backed API",
        "generator_builder": "Existing /api/explain shares normalized tree contract; root parity is sampled below",
        "source_review_scope": "Repository-approved templates and source records; no invented new book claims",
    }


def inspect_case(item, *, runtime=None):
    """Invoke the actual installed Benepar parser and existing B–R/XAI functions.

    No mocks, no synthetic tree substitution, no CoLA model or auto-repair run.
    The legacy rule matrix is measured as an advisory candidate diagnostic.
    """
    from parse_engine import analyze
    from burton_roberts import build_canonical_analysis
    from explanations import explain_analysis, explain_request, nodes_of
    from cambridge_registry import load_runtime_registry
    from cambridge_evaluator import evaluate_cambridge

    t0 = time.perf_counter()
    row = {
        "id": item["id"], "family": item["family"], "intent": item["intent"],
        "text": item["text"], "sentence_index": item["selected_sentence_index"],
        "parser_status": "unavailable", "br_status": "not_evaluated",
        "explanation_status": "NOT_EVALUATED",
        "working_tree_observed": False,
        "br_reason_codes": [],
        "all_nodes": 0, "terminal_nodes": 0, "source_cited_nodes": 0,
        "source_cited_terminal_nodes": 0,
        "all_labels": {}, "labels_without_cited_explanation": {},
        "control_vs_legacy_disagreement": False,
        "malformed_probe_vs_legacy_no_flag": False,
        "root_endpoint_checked": False,
        "root_endpoint_matches": None,
        "legacy_matrix": {"status": "not_run"},
        "cambridge": {"status": "not_run", "enabled_count": 0},
        "timing_ms": {},
    }
    try:
        analysis = analyze(item["text"], sentence_index=item["selected_sentence_index"])
    except Exception as exc:  # real parse failures must remain visible
        row["parser_status"] = "parse_error"
        row["parser_error"] = {"type": type(exc).__name__, "message": str(exc)[:300]}
        row["timing_ms"]["total"] = round((time.perf_counter() - t0) * 1000, 2)
        return row
    t_parse = time.perf_counter()
    row["parser_status"] = "parsed"
    row["selected_text"] = analysis["sentence"]
    row["sentence_count"] = analysis["sentence_count"]
    row["candidate_root_type"] = analysis["root"].get("type")
    row["candidate_node_count"] = len(analysis.get("nodes") or [])
    row["input_token_count"] = len(analysis["tokens"])
    row["timing_ms"]["parse"] = round((t_parse - t0) * 1000, 2)
    try:
        br = build_canonical_analysis(analysis)
    except Exception as exc:
        row["br_status"] = "audit_error"
        row["br_exception"] = {"type": type(exc).__name__, "message": str(exc)[:300]}
        row["timing_ms"]["total"] = round((time.perf_counter() - t0) * 1000, 2)
        return row
    row["br_status"] = br.get("status", "missing_status")
    row["br_reason_codes"] = sorted(set(
        r.get("code", "UNKNOWN") for r in br.get("reasons", [])
        if isinstance(r, dict)
    ))
    row["working_tree_observed"] = isinstance(br.get("working_tree"), dict)
    row["br_rule_verification_status"] = (
        br.get("br_rule_verification", {}).get("status")
        if isinstance(br.get("br_rule_verification"), dict) else None
    )
    t_br = time.perf_counter()
    row["timing_ms"]["br"] = round((t_br - t_parse) * 1000, 2)
    registry = runtime or load_runtime_registry()
    try:
        evaluation = evaluate_cambridge(br, registry)
        row["cambridge"] = {
            "status": evaluation.get("status"),
            "evaluated_ids": evaluation.get("evaluated_rule_ids", []),
            "finding_count": len(evaluation.get("findings", [])),
            "enabled_count": len(registry.get("active_rules", [])),
        }
    except Exception as exc:
        row["cambridge"] = {"status": "audit_error", "error": str(exc)[:200]}
    try:
        xai = explain_analysis(br, runtime_registry=registry)
    except Exception as exc:
        row["explanation_status"] = "audit_error"
        row["explanation_exception"] = {"type": type(exc).__name__,
                                        "message": str(exc)[:300]}
        row["timing_ms"]["total"] = round((time.perf_counter() - t0) * 1000, 2)
        return row
    row["explanation_status"] = xai.get("status", "missing_status")
    row["explanation_channels"] = {
        c: len(items) for c, items in xai.get("channels", {}).items()
    }
    row["observational_fact_count"] = len(xai.get("facts", []))
    row["explanation_diagnostic_codes"] = sorted({
        d.get("code", "UNKNOWN") for d in xai.get("diagnostics", [])
    })
    tree = br.get("tree")
    if row["br_status"] == "normalized" and isinstance(tree, dict):
        nodes = list(nodes_of(tree))
        labels = Counter(str(n.get("label", "(unlabelled)")) for _, n in nodes)
        cited = {a.get("node_id") for entries in xai.get("channels", {}).values()
                 for a in entries if a.get("sources")}
        ids = {ident for ident, _ in nodes}
        cited &= ids
        terminal = {ident for ident, n in nodes if isinstance(n.get("word"), str)}
        row["all_nodes"] = len(nodes)
        row["terminal_nodes"] = len(terminal)
        row["source_cited_nodes"] = len(cited)
        row["source_cited_terminal_nodes"] = len(terminal & cited)
        row["all_labels"] = dict(labels)
        row["labels_without_cited_explanation"] = dict(
            Counter(str(n.get("label", "(unlabelled)"))
                    for ident, n in nodes if ident not in cited)
        )
        row["triangle_collapsed_word_count"] = sum(
            len(n.get("words", [])) for _, n in nodes if n.get("triangle"))
        # This is a *real* request through the existing /api/explain contract
        # adapter but without HTTP transport; separate transport tests cover
        # Flask + stdlib behavior. It may be NO_BOOK_BASIS.
        try:
            root_id = nodes[0][0]
            target = explain_request({"tree": tree, "node_id": root_id})
            root_items = {
                c: [r for r in items if r.get("node_id") == root_id]
                for c, items in xai.get("channels", {}).items()
            }
            row["root_endpoint_checked"] = True
            row["root_endpoint_matches"] = (
                target["status"] ==
                ("EXPLAINED" if any(root_items.values()) else "NO_BOOK_BASIS")
                and target.get("channels", {}) == root_items
            )
        except Exception as exc:
            row["root_endpoint_checked"] = True
            row["root_endpoint_matches"] = False
            row["root_endpoint_exception"] = str(exc)[:200]
    t_explain = time.perf_counter()
    row["timing_ms"]["xai_and_cambridge"] = round((t_explain - t_br) * 1000, 2)

    try:
        from matrix import evaluate
        legacy = evaluate(analysis["root"], text=analysis["sentence"])
        summary = legacy.get("summary", {})
        verdict = summary.get("verdict")
        row["legacy_matrix"] = {
            "status": "evaluated", "verdict": verdict,
            "violated_edges": summary.get("violated_edges"),
            "unrated_edges": summary.get("unrated_edges"),
            "verdict_authority": "legacy_candidate_only",
        }
        row["control_vs_legacy_disagreement"] = (
            item["intent"] == "grammatical_control"
            and verdict == "ungrammatical"
        )
        row["malformed_probe_vs_legacy_no_flag"] = (
            item["intent"] in {"malformed_probe", "multi_error_probe"}
            and verdict == "grammatical"
        )
    except Exception as exc:
        row["legacy_matrix"] = {"status": "audit_error", "error": str(exc)[:240]}
    row["timing_ms"]["total"] = round((time.perf_counter() - t0) * 1000, 2)
    return row


def audit_dataset(items, *, require_models=False):
    model = {
        "ready": False, "parser_bundle": "en_core_web_md",
        "parser_model": "benepar_en3", "error": None,
    }
    try:
        from parse_engine import load_models
        pipeline = load_models()
        model.update({"ready": True, "pipeline": list(pipeline.pipe_names),
                      "spacy_model_version": (pipeline.meta or {}).get("version")})
    except Exception as exc:
        model["error"] = f"{type(exc).__name__}: {exc}"[:400]
        if require_models:
            raise RuntimeError("XAI-0 parser-backed baseline requires real NLP models: " +
                               model["error"]) from exc
    inventory = static_inventory()
    cases = []
    if model["ready"]:
        from cambridge_registry import load_runtime_registry
        registry = load_runtime_registry()
        for item in items:
            cases.append(inspect_case(item, runtime=registry))
    else:
        for item in items:
            cases.append({
                "id": item["id"], "family": item["family"],
                "intent": item["intent"], "text": item["text"],
                "parser_status": "models_unavailable", "br_status": "not_evaluated",
                "explanation_status": "NOT_EVALUATED",
                "all_nodes": 0, "terminal_nodes": 0, "source_cited_nodes": 0,
                "source_cited_terminal_nodes": 0,
                "all_labels": {}, "labels_without_cited_explanation": {},
                "working_tree_observed": False, "br_reason_codes": [],
                "control_vs_legacy_disagreement": False,
                "malformed_probe_vs_legacy_no_flag": False,
            })
    return {
        "schema_version": "xai-0-measurement-1.0",
        "milestone": "XAI-0",
        "corpus_kind": "development_not_gold",
        "cases_total": len(items),
        "model_status": model,
        "inventory": inventory,
        "summary": status_counters(cases),
        "cases": cases,
        "provenance": {
            "github_sha": os.environ.get("GITHUB_SHA"),
            "ci_run_id": os.environ.get("GITHUB_RUN_ID"),
            "corpus_path": str(DATA_PATH.relative_to(ROOT)),
            "review_status": "NOT_HUMAN_ADJUDICATED",
            "measurement_status": ("real_parser_evaluated" if model["ready"]
                                   else "models_unavailable_no_parser_metrics"),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-input-only", action="store_true")
    parser.add_argument("--require-models", action="store_true")
    parser.add_argument("--expected-count", type=int, default=116)
    parser.add_argument("--max-cases", type=int, default=None,
                        help="Local smoke only; this limits measured sentences")
    args = parser.parse_args()
    corpus = load_cases()
    if len(corpus["cases"]) != args.expected_count:
        raise SystemExit(
            f"Expected {args.expected_count} development cases, found {len(corpus['cases'])}"
        )
    if args.validate_input_only:
        print(json.dumps({
            "validated": True, "cases": len(corpus["cases"]),
            "families": dict(Counter(x["family"] for x in corpus["cases"])),
            "adjudicated_gold": False,
        }, indent=2))
        return
    if args.max_cases is not None and args.max_cases < 1:
        raise SystemExit("--max-cases must be positive")
    items = corpus["cases"] if args.max_cases is None else corpus["cases"][:args.max_cases]
    report = audit_dataset(items, require_models=args.require_models)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                               encoding="utf-8")
    print(json.dumps({
        "milestone": report["milestone"],
        "model_status": report["model_status"],
        "inventory": report["inventory"],
        "summary": report["summary"],
        "report_path": str(args.output) if args.output else None,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
