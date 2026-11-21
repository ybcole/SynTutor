#!/usr/bin/env python3
"""Single-shot locked evaluation on FROZEN_FINAL_HOLDOUT_V3.csv (n=370)
plus longitudinal tracking on Dev-320, HO-V1-320, HO-V2-370, and the
complete lookup-bypassed Burton-Roberts textbook census (n=216/218 IMG).

Verifies SHA-256 integrity of FROZEN_FINAL_HOLDOUT_V3.csv and zero case-folded
overlap with ALL historical dev, Cycle 1 holdout, and Cycle 2 holdout datasets.
Does NOT overwrite any historical Cycle 0 / Cycle 1 / Cycle 2 artifacts.
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

EXPECTED_V3_SHA256 = "1f4fba4ca45332decbd5bc5236fcde7f73804b097f588646d8ee9bfa5de452a9"


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


def evaluate_corpus(rows: list[dict[str, Any]], schema_val: Any, cam_rt: Any) -> list[dict[str, Any]]:
    import burton_roberts as br
    import cambridge_evaluator
    import detector
    import matrix
    import parse_engine

    sents_all = [r["sentence"] for r in rows]
    cola_all = []
    for s in range(0, len(sents_all), 32):
        cola_all.extend(detector.classify_many(sents_all[s : s + 32]))

    out_rows = []
    for item, det in zip(rows, cola_all):
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
            bsv = (bst == "normalized" and isinstance(bra.get("tree"), dict)
                   and not any(schema_val.iter_errors(bra["tree"])))
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
    return out_rows


def summarize_tree_cov(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    bn = sum(1 for r in rows if r["br_status"] == "normalized")
    bw = sum(1 for r in rows if r["br_status"] != "normalized" and r["br_has_working_tree"])
    bsv = sum(1 for r in rows if r["br_schema_valid"])
    return {
        "n": n,
        "benepar_parse_ok": sum(1 for r in rows if r["parse_ok"]),
        "br_normalized": bn,
        "br_normalized_rate": round(bn / n, 4) if n else 0.0,
        "br_working_tree_fallback": bw,
        "br_unresolved_no_tree": n - bn - bw,
        "br_schema_valid_count": bsv,
    }


def main() -> int:
    t0 = time.perf_counter()
    ho3_path = DIR / "FROZEN_FINAL_HOLDOUT_V3.csv"
    actual_sha = hashlib.sha256(ho3_path.read_bytes()).hexdigest()
    assert actual_sha == EXPECTED_V3_SHA256, f"Holdout V3 SHA mismatch: {actual_sha}"

    with open(ho3_path, encoding="utf-8") as fh:
        holdout3 = list(csv.DictReader(fh))
    assert len(holdout3) == 370

    # Leakage verification against ALL prior dev, Cycle 1 holdout, and Cycle 2 holdout sets
    prior = set()
    for p in (
        DIR / "RAW_PREDICTIONS.csv",
        DIR / "FROZEN_UNTOUCHED_HOLDOUT.csv",
        DIR / "FROZEN_FINAL_HOLDOUT_V2.csv",
        DIR / "baseline_snapshot/RAW_PREDICTIONS.csv",
        DIR / "cycle1_snapshot/RAW_PREDICTIONS.csv",
        DIR / "cycle1_snapshot/FROZEN_UNTOUCHED_HOLDOUT.csv",
    ):
        if p.exists():
            for r in csv.DictReader(open(p, encoding="utf-8")):
                prior.add(r["sentence"].strip().casefold())
    ho3_sents = {r["sentence"].strip().casefold() for r in holdout3}
    assert len(ho3_sents) == 370, "Internal duplicates in Holdout V3!"
    assert not (prior & ho3_sents), f"Leakage detected: {len(prior & ho3_sents)} overlaps!"

    import api
    import burton_roberts as br
    import cambridge_registry
    import detector
    import parse_engine
    from br_tree import load_reference_records
    from jsonschema import Draft202012Validator
    from learner_explanations import compose_learner_explanation
    from run_technical_evaluation import aggregate_parseval, score_parseval_pair

    parse_engine.load_models()
    detector.load_detector()
    cam_rt = cambridge_registry.load_runtime_registry()
    schema_val = Draft202012Validator(
        json.loads((ROOT / "docs/canonical-burton-roberts-tree.schema.json").read_text(encoding="utf-8"))
    )

    # 1. Single-shot untouched Holdout V3 (n=370)
    ho3_rows = evaluate_corpus(holdout3, schema_val, cam_rt)
    with open(DIR / "FINAL_HOLDOUT_V3_PREDICTIONS.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ho3_rows[0].keys()))
        w.writeheader()
        w.writerows(ho3_rows)

    slices = {
        "holdout3_all_370": ho3_rows,
        "holdout3_blimp_all_270": [r for r in ho3_rows if r["dataset"] == "holdout3_blimp"],
        "holdout3_blimp_core_210": [
            r for r in ho3_rows
            if r["dataset"] == "holdout3_blimp" and r["error_family"] not in {"ellipsis", "quantifiers_and_raising"}
        ],
        "holdout3_blimp_hard_60": [
            r for r in ho3_rows
            if r["error_family"] in {"ellipsis", "quantifiers_and_raising"}
        ],
        "holdout3_jfleg_100": [r for r in ho3_rows if r["dataset"] == "holdout3_jfleg"],
    }
    ho3_overall = {}
    for dname, drows in slices.items():
        ho3_overall[dname] = {}
        for mode, vf in [("rules_only", "rules_verdict"), ("hybrid_rules_plus_cola", "hybrid_verdict")]:
            ho3_overall[dname][mode] = {
                op: compute_rich_metrics(drows, vf, op)
                for op in ("strict_ungrammatical", "decisive_only", "non_grammatical_flagged")
            }

    ho3_by_fam = {}
    for fam in sorted({r["error_family"] for r in ho3_rows}):
        sub = [r for r in ho3_rows if r["error_family"] == fam]
        ho3_by_fam[fam] = {
            "n": len(sub),
            "rules_strict": compute_rich_metrics(sub, "rules_verdict", "strict_ungrammatical"),
            "hybrid_decisive": compute_rich_metrics(sub, "hybrid_verdict", "decisive_only"),
            "hybrid_flagged": compute_rich_metrics(sub, "hybrid_verdict", "non_grammatical_flagged"),
            "tree_coverage": summarize_tree_cov(sub),
        }

    ho3_tree_cov = {dname: summarize_tree_cov(drows) for dname, drows in slices.items()}

    # 2. Stratified n=90 full api.build_payload() XAI & Correction audit on Holdout V3
    xai_pool = []
    for fam in sorted({r["error_family"] for r in ho3_rows if r["error_family"] != "l2_learner_writing"}):
        sub = [r for r in ho3_rows if r["error_family"] == fam]
        xai_pool.extend([r for r in sub if r["gold_label"] == "grammatical"][:3])
        xai_pool.extend([r for r in sub if r["gold_label"] == "ungrammatical"][:3])
    j_sub = slices["holdout3_jfleg_100"]
    xai_pool.extend([r for r in j_sub if r["gold_label"] == "ungrammatical"][:18])
    xai_pool.extend([r for r in j_sub if r["gold_label"] == "grammatical"][:18])

    verdict_ok = gating_ok = rule_ok = tok_ok = fg_ok = 0
    err_sents = norm_sents = node_tot = node_ne = 0
    corr_tot = corr_ungram = corr_gram_fp = corr_clean = corr_exact = 0
    corr_samples = []
    t_api = time.perf_counter()
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
            if all(all(t in sl for t in re.findall(r"\w+(?:['’]\w+)*", (d.get("surface") or "").casefold()))
                   for d in errs if d.get("surface")):
                tok_ok += 1
        bra = p["br_analysis"]
        if bra.get("status") == "normalized" and isinstance(bra.get("tree"), dict):
            norm_sents += 1
            tids = set()
            st = [bra["tree"].get("root")]
            while st:
                cur = st.pop()
                if isinstance(cur, dict):
                    if cur.get("id"):
                        tids.add(cur["id"])
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
    api_mean_ms = round(((time.perf_counter() - t_api) / len(xai_pool)) * 1000.0, 1)

    # 3. Complete Burton-Roberts Textbook Census (Lookup Bypassed, with PARSEVAL)
    from br_tree import _atoms, _source_yield
    prof = br.convention_profile()
    recs = [
        r for r in load_reference_records()
        if r.get("status") == "IMG" and r.get("correct") is not False
        and isinstance(r.get("sentence"), str) and isinstance(r.get("tree"), dict)
        and not (r.get("_chapter", 0) > 1 and r["tree"].get("label") == "Sentence")
        and _source_yield(r["tree"]) == _atoms(r["sentence"])
    ]
    tb_all_scored, tb_710_scored = [], []
    tb_norm = tb_rej = tb_crash = tb_schema_err = 0
    ch7_10_tot = ch7_10_norm = 0
    for rec in recs:
        ch = rec.get("_chapter", 0)
        if ch >= 7:
            ch7_10_tot += 1
        try:
            an = parse_engine.analyze(rec["sentence"])
            res = br.normalize_benepar_candidate(an, prof)
        except Exception:
            tb_crash += 1
            continue
        if res["status"] == "normalized":
            tb_norm += 1
            if ch >= 7:
                ch7_10_norm += 1
            if any(schema_val.iter_errors(res["tree"])):
                tb_schema_err += 1
            sc = score_parseval_pair(rec["tree"], res["tree"]["root"], triangle_aware=True)
            sc["status"] = "normalized"
            sc["normalized"] = True
            sc["working_tree"] = False
            tb_all_scored.append(sc)
            if ch >= 7:
                tb_710_scored.append(sc)
        elif res["status"] == "rejected":
            tb_rej += 1
            entry = {"status": "rejected", "normalized": False, "working_tree": False, "yield_match": False}
            tb_all_scored.append(entry)
            if ch >= 7:
                tb_710_scored.append(entry)
        else:
            has_w = bool(res.get("working_tree"))
            st_fb = "working_fallback" if has_w else "unresolved"
            entry = {"status": st_fb, "normalized": False, "working_tree": has_w, "yield_match": False}
            tb_all_scored.append(entry)
            if ch >= 7:
                tb_710_scored.append(entry)

    tb_summary = {
        "n_total": len(recs),
        "normalized": tb_norm,
        "normalization_rate": round(tb_norm / len(recs), 4),
        "crashes": tb_crash,
        "validation_rejected": tb_rej,
        "schema_errors": tb_schema_err,
        "all_parseval": aggregate_parseval(tb_all_scored),
        "ch7_10_total": ch7_10_tot,
        "ch7_10_normalized": ch7_10_norm,
        "ch7_10_normalization_rate": round(ch7_10_norm / ch7_10_tot, 4) if ch7_10_tot else 0.0,
        "ch7_10_parseval": aggregate_parseval(tb_710_scored),
    }

    # 4. Longitudinal tracking on Dev-320, Hist HO1-320, Dev-Diag HO2-370
    dev_rows = [
        r for r in csv.DictReader(open(DIR / "RAW_PREDICTIONS.csv", encoding="utf-8"))
        if r["dataset"] in {"blimp_stratified", "jfleg_stratified"}
    ]
    dev_eval = evaluate_corpus(dev_rows, schema_val, cam_rt)
    ho1_eval = evaluate_corpus(list(csv.DictReader(open(DIR / "FROZEN_UNTOUCHED_HOLDOUT.csv", encoding="utf-8"))), schema_val, cam_rt)
    ho2_eval = evaluate_corpus(list(csv.DictReader(open(DIR / "FROZEN_FINAL_HOLDOUT_V2.csv", encoding="utf-8"))), schema_val, cam_rt)

    longitudinal = {}
    for name, drows in [("dev_320", dev_eval), ("hist_ho1_320", ho1_eval), ("dev_diag_ho2_370", ho2_eval)]:
        longitudinal[name] = {
            "rules_strict": compute_rich_metrics(drows, "rules_verdict", "strict_ungrammatical"),
            "hybrid_decisive": compute_rich_metrics(drows, "hybrid_verdict", "decisive_only"),
            "hybrid_flagged": compute_rich_metrics(drows, "hybrid_verdict", "non_grammatical_flagged"),
            "tree_coverage": summarize_tree_cov(drows),
        }

    # 5. Prepare blank blind human-review worksheet for V3 (0 fabricated scores)
    worksheet_rows = []
    strata = [
        ("TP", [r for r in ho3_rows if r["gold_label"] == "ungrammatical" and r["rules_verdict"] == "ungrammatical"][:14]),
        ("FP", [r for r in ho3_rows if r["gold_label"] == "grammatical" and r["rules_verdict"] == "ungrammatical"][:10]),
        ("UNV_U", [r for r in ho3_rows if r["gold_label"] == "ungrammatical" and r["hybrid_verdict"] == "unverified"][:10]),
        ("UNV_G", [r for r in ho3_rows if r["gold_label"] == "grammatical" and r["hybrid_verdict"] == "unverified"][:8]),
        ("FN", [r for r in ho3_rows if r["gold_label"] == "ungrammatical" and r["hybrid_verdict"] == "grammatical"][:8]),
        ("TN", [r for r in ho3_rows if r["gold_label"] == "grammatical" and r["hybrid_verdict"] == "grammatical"][:10]),
    ]
    for stratum, items in strata:
        for it in items:
            p = api.build_payload(it["sentence"])
            summ = p["summary"]
            worksheet_rows.append({
                "review_id": f"rv3-{len(worksheet_rows)+1:03d}",
                "stratum": stratum,
                "item_id": it["item_id"],
                "error_family": it["error_family"],
                "sentence": it["sentence"],
                "system_verdict": summ["verdict"],
                "constraints_fired": ";".join(summ.get("constraints_fired") or []),
                "corrected_sentence": summ.get("corrected_sentence") or "",
                "br_status": p["br_analysis"].get("status", ""),
                "root_learner_explanation": (p.get("learner_explanation") or {}).get("text", ""),
                # 12 strictly blank blind human reviewer columns
                "r1_verdict_correct": "", "r1_tree_accuracy_1_5": "", "r1_rule_justification_1_5": "",
                "r1_correction_validity_1_5": "", "r1_explanation_clarity_1_5": "", "r1_notes": "",
                "r2_verdict_correct": "", "r2_tree_accuracy_1_5": "", "r2_rule_justification_1_5": "",
                "r2_correction_validity_1_5": "", "r2_explanation_clarity_1_5": "", "r2_notes": "",
            })
    with open(DIR / "HUMAN_REVIEW_WORKSHEET_V3.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(worksheet_rows[0].keys()))
        w.writeheader()
        w.writerows(worksheet_rows)

    fp_cns = Counter(
        c for r in ho3_rows if r["gold_label"] == "grammatical" and r["rules_verdict"] == "ungrammatical"
        for c in (r["constraints_fired"].split(";") if r["constraints_fired"] else ["UNKNOWN"])
    )
    unv_by_fam = Counter(r["error_family"] for r in ho3_rows if r["hybrid_verdict"] == "unverified")
    unv_gold_u = sum(1 for r in ho3_rows if r["hybrid_verdict"] == "unverified" and r["gold_label"] == "ungrammatical")
    unv_tot = sum(1 for r in ho3_rows if r["hybrid_verdict"] == "unverified")

    res = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "holdout_v3_sha256": actual_sha,
        "runtime_seconds": round(time.perf_counter() - t0, 2),
        "holdout_v3_overall": ho3_overall,
        "holdout_v3_by_family": ho3_by_fam,
        "holdout_v3_fp_constraints": dict(fp_cns.most_common(20)),
        "holdout_v3_unverified": {
            "total_hybrid_unverified": unv_tot,
            "gold_ungrammatical": unv_gold_u,
            "gold_grammatical": unv_tot - unv_gold_u,
            "share_truly_ungrammatical": round(unv_gold_u / unv_tot, 4) if unv_tot else 0.0,
            "rule_level_unverified": sum(1 for r in ho3_rows if r["rules_verdict"] == "unverified"),
            "by_family": dict(unv_by_fam.most_common()),
        },
        "holdout_v3_tree_coverage": ho3_tree_cov,
        "holdout_v3_xai_and_corrections_n90": {
            "n": len(xai_pool),
            "mean_api_latency_ms": api_mean_ms,
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
        "textbook_census_lookup_bypassed": tb_summary,
        "longitudinal_dev_and_historical": longitudinal,
        "human_review_worksheet_v3_rows": len(worksheet_rows),
    }
    (DIR / "_final_holdout_v3_results.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"[holdout-v3] COMPLETE in {res['runtime_seconds']}s!", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
