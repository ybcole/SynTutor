#!/usr/bin/env python3
"""Repeat validation evaluation against FROZEN_UNTOUCHED_HOLDOUT.csv (n=320).

Verifies SHA-256 integrity and zero sentence overlap with all development data,
executes actual SynTutor runtime pipelines, computes all classification metrics,
per-category F1, unverified breakdown, B-R canonical normalization coverage,
correction accuracy vs independent references, and automated XAI consistency.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "server"))
sys.path.insert(0, str(DIR))

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

EXPECTED_SHA256 = "90919d6b6001bb3c09cfcda8cde8f1698a03d86bddbe792c3aecf8a0324e503b"


def main() -> int:
    t0 = time.perf_counter()
    ho_path = DIR / "FROZEN_UNTOUCHED_HOLDOUT.csv"
    actual_sha = hashlib.sha256(ho_path.read_bytes()).hexdigest()
    assert actual_sha == EXPECTED_SHA256, f"Holdout SHA mismatch: {actual_sha} != {EXPECTED_SHA256}"

    with open(ho_path, encoding="utf-8") as fh:
        holdout = list(csv.DictReader(fh))
    assert len(holdout) == 320

    # Verify sentence disjointness; this does not prove historical untouched status
    dev_sents = {
        r["sentence"].strip().casefold()
        for r in csv.DictReader(open(DIR / "baseline_snapshot/RAW_PREDICTIONS.csv", encoding="utf-8"))
    }
    ho_sents = {r["sentence"].strip().casefold() for r in holdout}
    assert not (dev_sents & ho_sents), "Leakage detected between dev and holdout!"

    import api
    import burton_roberts as br
    import cambridge_evaluator
    import cambridge_registry
    import detector
    import matrix
    import parse_engine
    from jsonschema import Draft202012Validator
    from learner_explanations import compose_learner_explanation
    from run_technical_evaluation import compute_binary_metrics

    parse_engine.load_models()
    assert detector.load_detector() is not None, "Required hybrid model unavailable"
    cam_rt = cambridge_registry.load_runtime_registry()
    schema_val = Draft202012Validator(
        json.loads((ROOT / "docs/canonical-burton-roberts-tree.schema.json").read_text(encoding="utf-8"))
    )

    # Batch RoBERTa-CoLA
    sents_all = [r["sentence"] for r in holdout]
    cola_all = []
    for s in range(0, len(sents_all), 32):
        cola_all.extend(detector.classify_many(sents_all[s : s + 32]))

    out_rows = []
    for item, det in zip(holdout, cola_all):
        row = dict(item)
        try:
            an = parse_engine.analyze(item["sentence"])
            mat = matrix.evaluate(an["root"], text=an["sentence"])
            summary = mat["summary"]
            details = mat["details"]
            rules_v = summary.get("verdict", "unverified")
            cns = sorted({
                str(d.get("constraint") or d.get("rule_id") or "")
                for d in details.values()
                if isinstance(d, dict) and d.get("status") == "error"
                and (d.get("constraint") or d.get("rule_id"))
            })
            comb = detector.combine(summary, det) if det is not None else summary
            hyb_v = comb.get("verdict", rules_v)
            br_an = br.build_canonical_analysis(an)
            br_st = br_an.get("status", "unresolved")
            br_w = bool(br_an.get("working_tree"))
            br_sv = (br_st == "normalized" and isinstance(br_an.get("tree"), dict) and not any(schema_val.iter_errors(br_an["tree"])))
            cam = cambridge_evaluator.evaluate_cambridge(br_an, cam_rt, variety="standard_english")
            row.update({
                "execution_status": "ok",
                "parse_ok": True,
                "rules_verdict": rules_v,
                "hybrid_verdict": hyb_v,
                "cola_label": det.get("label", "") if det else "",
                "cola_acceptable_prob": det.get("acceptable_prob", "") if det else "",
                "constraints_fired": ";".join(cns),
                "cambridge_findings_count": len(cam.get("findings") or []),
                "br_status": br_st,
                "br_has_working_tree": br_w,
                "br_schema_valid": br_sv,
            })
        except Exception as exc:
            row.update({
                "execution_status": "parse_error",
                "error_message": f"{type(exc).__name__}: {exc}",
                "parse_ok": False,
                "rules_verdict": "execution_error",
                "hybrid_verdict": "execution_error",
                "cola_label": "",
                "cola_acceptable_prob": "",
                "constraints_fired": "",
                "cambridge_findings_count": 0,
                "br_status": "execution_error",
                "br_has_working_tree": False,
                "br_schema_valid": False,
            })
        out_rows.append(row)

    with open(DIR / "HOLDOUT_PREDICTIONS.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    slices = {
        "holdout_all_320": out_rows,
        "holdout_blimp_240": [r for r in out_rows if r["dataset"] == "holdout_blimp"],
        "holdout_jfleg_80": [r for r in out_rows if r["dataset"] == "holdout_jfleg"],
    }
    overall = {}
    for dname, drows in slices.items():
        overall[dname] = {}
        for mode, vf in [("rules_only", "rules_verdict"), ("hybrid_rules_plus_cola", "hybrid_verdict")]:
            overall[dname][mode] = {
                op: compute_binary_metrics(drows, vf, op)
                for op in ("strict_ungrammatical", "decisive_only", "non_grammatical_flagged")
            }

    by_fam = {}
    for fam in sorted({r["error_family"] for r in slices["holdout_blimp_240"]}):
        sub = [r for r in slices["holdout_blimp_240"] if r["error_family"] == fam]
        by_fam[fam] = {
            "rules_strict": compute_binary_metrics(sub, "rules_verdict", "strict_ungrammatical"),
            "hybrid_decisive": compute_binary_metrics(sub, "hybrid_verdict", "decisive_only"),
            "hybrid_flagged": compute_binary_metrics(sub, "hybrid_verdict", "non_grammatical_flagged"),
        }

    # Tree coverage on untouched holdout
    tree_cov = {}
    for dname, drows in slices.items():
        n = len(drows)
        bn = sum(1 for r in drows if r["br_status"] == "normalized")
        bw = sum(1 for r in drows if r["br_status"] != "normalized" and r["br_has_working_tree"])
        bsv = sum(1 for r in drows if r["br_schema_valid"])
        tree_cov[dname] = {
            "n": n,
            "benepar_parse_ok": sum(1 for r in drows if r["parse_ok"]),
            "br_normalized": bn,
            "br_normalized_rate": round(bn / n, 4),
            "br_working_tree_fallback": bw,
            "br_unresolved_no_tree": n - bn - bw,
            "br_schema_valid_count": bsv,
        }

    # Full api.build_payload XAI + Correction audit on stratified 60-sentence holdout slice
    # (3 pairs x 8 BLiMP families = 48? Let's take 2 pairs x 8 BLiMP = 32 + 14 JFLEG pairs = 28 => 60)
    ho_xai_pool = []
    for fam in sorted({r["error_family"] for r in slices["holdout_blimp_240"]}):
        sub = [r for r in slices["holdout_blimp_240"] if r["error_family"] == fam]
        ho_xai_pool.extend([r for r in sub if r["gold_label"] == "grammatical"][:2])
        ho_xai_pool.extend([r for r in sub if r["gold_label"] == "ungrammatical"][:2])
    ho_xai_pool.extend([r for r in slices["holdout_jfleg_80"] if r["gold_label"] == "ungrammatical"][:14])
    ho_xai_pool.extend([r for r in slices["holdout_jfleg_80"] if r["gold_label"] == "grammatical"][:14])

    corr_total = corr_on_ungram = corr_on_gram = corr_reparse_clean = corr_exact_ref = 0
    verdict_ok = gating_ok = rule_ground_ok = tok_ground_ok = fg_ok = 0
    err_sents = norm_sents = node_prose_tot = node_prose_ne = 0
    corr_samples = []
    for item in ho_xai_pool:
        p = api.build_payload(item["sentence"])
        summ = p["summary"]
        dets = p["node_details"]
        verdict = summ["verdict"]
        errs = [d for d in dets.values() if isinstance(d, dict) and d.get("status") == "error"]
        if (verdict == "ungrammatical" and errs) or (verdict in {"grammatical", "unverified"} and not errs):
            verdict_ok += 1
        if verdict == "grammatical" or not any(isinstance(d, dict) and d.get("display_status") == "valid" for d in dets.values()):
            gating_ok += 1
        if errs:
            err_sents += 1
            if all((d.get("constraint") or d.get("rule_id")) and (d.get("text") or "").strip() for d in errs):
                rule_ground_ok += 1
            sl = item["sentence"].casefold()
            if all(all(t in sl for t in re.findall(r"\w+(?:['’]\w+)*", (d.get("surface") or "").casefold())) for d in errs if d.get("surface")):
                tok_ground_ok += 1
        bran = p["br_analysis"]
        if bran.get("status") == "normalized" and isinstance(bran.get("tree"), dict):
            norm_sents += 1
            tids = set()
            st = [bran["tree"].get("root")]
            while st:
                cur = st.pop()
                if isinstance(cur, dict):
                    if cur.get("id"): tids.add(cur["id"])
                    st.extend(cur.get("children") or [])
            fg = (p.get("explanation_evidence") or {}).get("fact_graph") or {}
            fgn = fg.get("nodes") or []
            if {n.get("node_id") for n in fgn if n.get("node_id")}.issubset(tids):
                fg_ok += 1
            for n in fgn:
                node_prose_tot += 1
                if (compose_learner_explanation(fg, node_id=n["node_id"]).get("text") or "").strip():
                    node_prose_ne += 1
        cs = summ.get("corrected_sentence") or ""
        if cs:
            corr_total += 1
            if item["gold_label"] == "ungrammatical":
                corr_on_ungram += 1
            else:
                corr_on_gram += 1
            imp = (summ.get("correction") or {}).get("impact") or {}
            if imp.get("whole_sentence_clean") is True:
                corr_reparse_clean += 1
            ref = item.get("reference_correction") or ""
            ex = bool(ref and cs.strip().casefold() == ref.strip().casefold())
            if ex:
                corr_exact_ref += 1
            corr_samples.append({
                "item_id": item["item_id"], "gold_label": item["gold_label"],
                "sentence": item["sentence"], "corrected": cs,
                "reference": ref, "exact_match": ex,
                "constraints": ";".join(summ.get("constraints_fired") or []),
            })

    fp_cns = Counter(
        c for r in out_rows if r["gold_label"] == "grammatical" and r["rules_verdict"] == "ungrammatical"
        for c in (r["constraints_fired"].split(";") if r["constraints_fired"] else ["UNKNOWN"])
    )

    res = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "holdout_sha256": actual_sha,
        "sample_role": "Previously examined sentence-disjoint validation set; rerun for source reproducibility, not a new untouched test",
        "runtime_seconds": round(time.perf_counter() - t0, 2),
        "overall": overall,
        "blimp_by_family": by_fam,
        "fp_constraints": dict(fp_cns.most_common(20)),
        "tree_coverage": tree_cov,
        "xai_and_corrections_n60": {
            "n": len(ho_xai_pool),
            "verdict_consistent": verdict_ok,
            "display_gating_ok": gating_ok,
            "err_sents": err_sents,
            "rule_ground_ok": rule_ground_ok,
            "tok_ground_ok": tok_ground_ok,
            "norm_sents": norm_sents,
            "fg_ground_ok": fg_ok,
            "node_prose_tot": node_prose_tot,
            "node_prose_ne": node_prose_ne,
            "corrections_generated": corr_total,
            "corrections_on_ungrammatical": corr_on_ungram,
            "corrections_on_grammatical_false_repairs": corr_on_gram,
            "corrections_reparse_clean": corr_reparse_clean,
            "corrections_exact_match_ref": corr_exact_ref,
            "correction_samples": corr_samples,
        },
    }
    (DIR / "_holdout_results.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[holdout] COMPLETE in {res['runtime_seconds']}s!", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
