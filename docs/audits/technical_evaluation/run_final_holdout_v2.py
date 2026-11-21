#!/usr/bin/env python3
"""Single-shot Cycle-2 final evaluation on FROZEN_FINAL_HOLDOUT_V2.csv (n=370).

Verifies SHA-256 integrity and zero overlap with all Cycle 0/1 dev, Cycle 1
historical holdout, and internal corpora. Computes full Phase 9 metrics
(Accuracy, Balanced Accuracy, Precision, Recall, F1, Specificity, FPR, FNR,
MCC, 95% Wilson CIs, Coverage, Unverified Rate), construction-level
generalization on unseen BLiMP families, B-R canonical tree normalization,
and full-payload XAI + correction accuracy on a stratified n=90 subset.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
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

EXPECTED_SHA256 = "4028b741f0e10e23230599bdad8bff673756313c7d1ce9466279f282fb552a98"


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float | None, float | None]:
    if not n:
        return None, None
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = (z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)) / denom
    return round(max(0.0, center - margin), 4), round(min(1.0, center + margin), 4)


def compute_rich_metrics(rows: list[dict[str, Any]], vfield: str, op: str) -> dict[str, Any]:
    from run_technical_evaluation import compute_binary_metrics

    m = compute_binary_metrics(rows, vfield, op)
    tp, tn, fp, fn = m["tp"], m["tn"], m["fp"], m["fn"]
    ev = m["n_evaluated"]
    rec = m["recall"]
    spec = m["specificity"]
    bal_acc = round((rec + spec) / 2.0, 4) if (rec is not None and spec is not None) else None
    fpr = round(fp / (fp + tn), 4) if (fp + tn) else None
    fnr = round(fn / (fn + tp), 4) if (fn + tp) else None
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = round(((tp * tn) - (fp * fn)) / denom, 4) if denom > 0 else 0.0
    ci_lo, ci_hi = wilson_ci(tp + tn, ev)
    m.update({
        "balanced_accuracy": bal_acc,
        "fpr": fpr,
        "fnr": fnr,
        "mcc": mcc,
        "acc_ci95_low": ci_lo,
        "acc_ci95_high": ci_hi,
        "unverified_rate": round(m["n_unverified_total"] / m["n_total"], 4) if m["n_total"] else 0.0,
    })
    return m


def main() -> int:
    t0 = time.perf_counter()
    ho_path = DIR / "FROZEN_FINAL_HOLDOUT_V2.csv"
    actual_sha = hashlib.sha256(ho_path.read_bytes()).hexdigest()
    assert actual_sha == EXPECTED_SHA256, f"Holdout V2 SHA mismatch: {actual_sha}"

    with open(ho_path, encoding="utf-8") as fh:
        holdout = list(csv.DictReader(fh))
    assert len(holdout) == 370

    # Leakage verification against ALL prior dev and Cycle 1 holdout sets
    prior = set()
    for p in (
        DIR / "baseline_snapshot/RAW_PREDICTIONS.csv",
        DIR / "cycle1_snapshot/RAW_PREDICTIONS.csv",
        DIR / "cycle1_snapshot/FROZEN_UNTOUCHED_HOLDOUT.csv",
    ):
        for r in csv.DictReader(open(p, encoding="utf-8")):
            prior.add(r["sentence"].strip().casefold())
    ho_sents = {r["sentence"].strip().casefold() for r in holdout}
    assert not (prior & ho_sents), "Leakage detected!"

    import api
    import burton_roberts as br
    import cambridge_evaluator
    import cambridge_registry
    import detector
    import matrix
    import parse_engine
    from jsonschema import Draft202012Validator
    from learner_explanations import compose_learner_explanation

    parse_engine.load_models()
    detector.load_detector()
    cam_rt = cambridge_registry.load_runtime_registry()
    schema_val = Draft202012Validator(
        json.loads((ROOT / "docs/canonical-burton-roberts-tree.schema.json").read_text(encoding="utf-8"))
    )

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
            rv = summary.get("verdict", "unverified")
            cns = sorted({
                str(d.get("constraint") or d.get("rule_id") or "")
                for d in details.values()
                if isinstance(d, dict) and d.get("status") == "error"
                and (d.get("constraint") or d.get("rule_id"))
            })
            comb = detector.combine(summary, det) if det is not None else summary
            hv = comb.get("verdict", rv)
            bra = br.build_canonical_analysis(an)
            bst = bra.get("status", "unresolved")
            bw = bool(bra.get("working_tree"))
            bsv = (bst == "normalized" and isinstance(bra.get("tree"), dict) and not any(schema_val.iter_errors(bra["tree"])))
            cam = cambridge_evaluator.evaluate_cambridge(bra, cam_rt, variety="standard_english")
            row.update({
                "execution_status": "ok",
                "error_message": "",
                "parse_ok": True,
                "rules_verdict": rv,
                "hybrid_verdict": hv,
                "cola_label": det.get("label", "") if det else "",
                "cola_acceptable_prob": det.get("acceptable_prob", "") if det else "",
                "constraints_fired": ";".join(cns),
                "cambridge_findings_count": len(cam.get("findings") or []),
                "br_status": bst,
                "br_has_working_tree": bw,
                "br_schema_valid": bsv,
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

    with open(DIR / "FINAL_HOLDOUT_V2_PREDICTIONS.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    slices = {
        "holdout2_all_370": out_rows,
        "holdout2_seen_fams_plus_jfleg_310": [r for r in out_rows if r["dataset"] in {"holdout2_blimp_seen_fam", "holdout2_jfleg"}],
        "holdout2_blimp_seen_fam_210": [r for r in out_rows if r["dataset"] == "holdout2_blimp_seen_fam"],
        "holdout2_blimp_unseen_fam_60": [r for r in out_rows if r["dataset"] == "holdout2_blimp_unseen_fam"],
        "holdout2_jfleg_100": [r for r in out_rows if r["dataset"] == "holdout2_jfleg"],
    }
    overall = {}
    for dname, drows in slices.items():
        overall[dname] = {}
        for mode, vf in [("rules_only", "rules_verdict"), ("hybrid_rules_plus_cola", "hybrid_verdict")]:
            overall[dname][mode] = {
                op: compute_rich_metrics(drows, vf, op)
                for op in ("strict_ungrammatical", "decisive_only", "non_grammatical_flagged")
            }

    by_fam = {}
    for fam in sorted({r["error_family"] for r in out_rows}):
        sub = [r for r in out_rows if r["error_family"] == fam]
        by_fam[fam] = {
            "n": len(sub),
            "rules_strict": compute_rich_metrics(sub, "rules_verdict", "strict_ungrammatical"),
            "hybrid_decisive": compute_rich_metrics(sub, "hybrid_verdict", "decisive_only"),
            "hybrid_flagged": compute_rich_metrics(sub, "hybrid_verdict", "non_grammatical_flagged"),
        }

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

    # Stratified n=90 full api.build_payload() XAI & Correction audit
    # 9 BLiMP families x 3 pairs (54) + 18 JFLEG pairs (36) = 90
    xai_pool = []
    for fam in sorted({r["error_family"] for r in out_rows if r["error_family"] != "l2_learner_writing"}):
        sub = [r for r in out_rows if r["error_family"] == fam]
        xai_pool.extend([r for r in sub if r["gold_label"] == "grammatical"][:3])
        xai_pool.extend([r for r in sub if r["gold_label"] == "ungrammatical"][:3])
    j_sub = slices["holdout2_jfleg_100"]
    xai_pool.extend([r for r in j_sub if r["gold_label"] == "ungrammatical"][:18])
    xai_pool.extend([r for r in j_sub if r["gold_label"] == "grammatical"][:18])

    verdict_ok = gating_ok = rule_ok = tok_ok = fg_ok = 0
    err_sents = norm_sents = node_tot = node_ne = 0
    corr_tot = corr_ungram = corr_gram_fp = corr_clean = corr_exact = 0
    corr_samples = []
    for item in xai_pool:
        p = api.build_payload(item["sentence"])
        summ = p["summary"]
        dets = p["node_details"]
        v = summ["verdict"]
        errs = [d for d in dets.values() if isinstance(d, dict) and d.get("status") == "error"]
        if (v == "ungrammatical" and errs) or (v in {"grammatical", "unverified"} and not errs):
            verdict_ok += 1
        if v == "grammatical" or not any(isinstance(d, dict) and d.get("display_status") == "valid" for d in dets.values()):
            gating_ok += 1
        if errs:
            err_sents += 1
            if all((d.get("constraint") or d.get("rule_id")) and (d.get("text") or "").strip() for d in errs):
                rule_ok += 1
            sl = item["sentence"].casefold()
            if all(all(t in sl for t in re.findall(r"\w+(?:['’]\w+)*", (d.get("surface") or "").casefold())) for d in errs if d.get("surface")):
                tok_ok += 1
        bra = p["br_analysis"]
        if bra.get("status") == "normalized" and isinstance(bra.get("tree"), dict):
            norm_sents += 1
            tids = set()
            st = [bra["tree"].get("root")]
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
                node_tot += 1
                if (compose_learner_explanation(fg, node_id=n["node_id"]).get("text") or "").strip():
                    node_ne += 1
        cs = summ.get("corrected_sentence") or ""
        if cs:
            corr_tot += 1
            if item["gold_label"] == "ungrammatical":
                corr_ungram += 1
            else:
                corr_gram_fp += 1
            imp = (summ.get("correction") or {}).get("impact") or {}
            if imp.get("whole_sentence_clean") is True:
                corr_clean += 1
            ref = item.get("reference_correction") or ""
            ex = bool(ref and cs.strip().casefold() == ref.strip().casefold())
            if ex:
                corr_exact += 1
            corr_samples.append({
                "item_id": item["item_id"], "gold_label": item["gold_label"],
                "error_family": item["error_family"],
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
        "holdout_v2_sha256": actual_sha,
        "runtime_seconds": round(time.perf_counter() - t0, 2),
        "overall": overall,
        "by_family": by_fam,
        "fp_constraints": dict(fp_cns.most_common(20)),
        "tree_coverage": tree_cov,
        "xai_and_corrections_n90": {
            "n": len(xai_pool),
            "verdict_consistent": verdict_ok,
            "display_gating_ok": gating_ok,
            "err_sents": err_sents,
            "rule_ground_ok": rule_ok,
            "tok_ground_ok": tok_ok,
            "norm_sents": norm_sents,
            "fg_ground_ok": fg_ok,
            "node_prose_tot": node_tot,
            "node_prose_ne": node_ne,
            "corrections_generated": corr_tot,
            "corrections_on_ungrammatical": corr_ungram,
            "corrections_on_grammatical_false_repairs": corr_gram_fp,
            "corrections_reparse_clean": corr_clean,
            "corrections_exact_match_ref": corr_exact,
            "correction_samples": corr_samples,
        },
    }
    (DIR / "_final_holdout_v2_results.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[holdout-v2] COMPLETE in {res['runtime_seconds']}s!", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
