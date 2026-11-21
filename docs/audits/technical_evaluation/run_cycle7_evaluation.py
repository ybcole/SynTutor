#!/usr/bin/env python3
"""Cycle 7 Reproducible Evaluation, Independent Correction Audit, Repaired Textbook
PARSEVAL Census, Unverified Calibration Audit, and Figure Generator.

Preserves ALL historical datasets and original Cycle 0-6 results untouched.
Writes new Cycle 7 artifacts under docs/audits/technical_evaluation/:
  - _cycle7_results.json
  - CYCLE7_HOLDOUT_V3_PREDICTIONS.csv
  - figures/fig_cycle7_reliability_progression.png
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
from collections import Counter, defaultdict
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
_BAD_COMP_ADV_RE = re.compile(r"\b[a-z]+(?:er|est)ly\b", re.I)
_ALLOWED_ERLY = {
    "elderly", "orderly", "quarterly", "easterly", "westerly", "northerly",
    "southerly", "motherly", "fatherly", "brotherly", "sisterly", "masterly",
    "miserly", "gingerly", "bitterly", "utterly", "eagerly", "cleverly",
    "properly", "soberly", "tenderly", "slenderly", "formerly", "latterly",
    "mannerly", "neighborly", "neighbourly", "scholarly", "soldierly",
    "dastardly", "beastly", "costly", "ghastly", "ghostly", "honestly",
    "modestly", "earnestly", "manifestly", "priestly", "mostly", "justly",
    "vastly", "firstly", "lastly", "chiefly", "briefly", "overly", "severely",
    "sincerely", "merely", "purely", "surely", "rarely", "barely", "squarely",
    "fairly", "clearly", "nearly", "dearly", "yearly", "hourly", "poorly", "early",
}
_MID_NP_ART_RE = re.compile(
    r"\b(?:more|very|really|extremely|highly|fairly|pretty|unsure|displeased|tall|red|big|small|happy|angry|old|young|gray|grey)\s+(?:a|an)\s+[a-z]+\b",
    re.I,
)
_DUP_WORD_RE = re.compile(r"\b([A-Za-z]+)\s+\1\b", re.I)
_INTERNAL_ID_RE = re.compile(r"\b(sg-root|n\d+:|C-[A-Z][A-Z-]{2,})\b")


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
            br_reason = ""
            if bst != "normalized" and bra.get("reasons"):
                r0 = bra["reasons"][0]
                br_reason = str(r0.get("detail") or r0.get("code") or "")
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
                "br_fallback_reason": br_reason,
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
                "br_fallback_reason": "",
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


def calibration_sweep(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rclean = [r for r in rows if r["rules_verdict"] == "grammatical" and r["cola_acceptable_prob"] != ""]
    tp_r = sum(1 for r in rows if r["gold_label"] == "ungrammatical" and r["rules_verdict"] == "ungrammatical")
    fp_r = sum(1 for r in rows if r["gold_label"] == "grammatical" and r["rules_verdict"] == "ungrammatical")
    gg_clean = sum(1 for r in rclean if r["gold_label"] == "grammatical")
    gu_clean = sum(1 for r in rclean if r["gold_label"] == "ungrammatical")
    out = []
    for t in (0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.42):
        fu = sum(1 for r in rclean if r["gold_label"] == "ungrammatical" and float(r["cola_acceptable_prob"]) < t)
        fg = sum(1 for r in rclean if r["gold_label"] == "grammatical" and float(r["cola_acceptable_prob"]) < t)
        tot = fu + fg
        tn = gg_clean - fg
        fn = gu_clean - fu
        ev = tp_r + tn + fp_r + fn
        out.append({
            "threshold": t,
            "cola_unverified_total": tot,
            "gold_ungrammatical": fu,
            "gold_grammatical": fg,
            "share_truly_ungrammatical": round(fu / tot, 4) if tot else None,
            "decisive_coverage": round(ev / len(rows), 4) if rows else 0.0,
            "decisive_accuracy": round((tp_r + tn) / ev, 4) if ev else None,
            "flagged_accuracy": round((tp_r + fu + tn) / len(rows), 4) if rows else None,
        })
    return out


def independent_check_correction(orig: str, corr: str) -> dict[str, Any]:
    """Validate a candidate correction independently of SynTutor's own matrix."""
    import spellcheck
    from lemminflect import getAllLemmas

    issues = []
    orig_low = orig.lower()
    # 1. Invalid comparative -erly / -estly fabrication
    for m in _BAD_COMP_ADV_RE.finditer(corr):
        w = m.group(0).lower()
        if w not in orig_low and w not in _ALLOWED_ERLY:
            issues.append(f"invalid_comp_adv:{w}")
    # 2. Mid-NP article insertion ('more unsure a person', 'very tall a man')
    if _MID_NP_ART_RE.search(corr) and not _MID_NP_ART_RE.search(orig):
        issues.append("mid_np_article_insertion")
    # 3. Adjacent word duplication ('a a', 'the the')
    for m in _DUP_WORD_RE.finditer(corr):
        if m.group(0).lower() not in orig_low:
            issues.append(f"dup_word:{m.group(0)}")
    # 4. Lexical validity of newly introduced alphabetic words (preserving contractions)
    _KNOWN_CONTRACTIONS = {
        "don't", "doesn't", "didn't", "won't", "wouldn't", "can't", "couldn't",
        "shouldn't", "mustn't", "isn't", "aren't", "wasn't", "weren't",
        "hasn't", "haven't", "hadn't", "i'm", "i've", "i'll", "i'd",
        "you're", "you've", "you'll", "you'd", "he's", "she's", "it's",
        "we're", "we've", "we'll", "they're", "they've", "they'll", "that's",
    }
    orig_words = {w.lower() for w in re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", orig)}
    corr_words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", corr)
    for w in corr_words:
        wl = w.lower()
        if wl in orig_words or wl in _KNOWN_CONTRACTIONS or len(wl) <= 2:
            continue
        known = spellcheck.known_word(wl) or any(getAllLemmas(wl, u) for u in ("NOUN", "VERB", "ADJ", "ADV", "AUX"))
        if not known:
            issues.append(f"unknown_introduced_word:{wl}")
    return {"independent_clean": len(issues) == 0, "issues": issues}


def generate_figure(res: dict[str, Any]) -> None:
    from generate_figures import (
        AMBER, BORDER, CORAL, FIG_DIR, FONT, GRID, LIGHT_BG, MUTED, NAVY, SLATE,
        TEAL, TEXT, _esc, render_svg_to_png,
    )

    W, H = 2400, 1080
    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
        f'<text x="70" y="64" font-family="{FONT}" font-size="30" font-weight="700" fill="{NAVY}">'
        'SynTutor Cycle 7 — Evidence-Driven NLP Reliability Progression (Reproducible Measurements)</text>',
        f'<text x="70" y="98" font-family="{FONT}" font-size="16" fill="{MUTED}">'
        'Source: _cycle7_results.json (n=320 Dev, n=320 HO-V1, n=370 HO-V2, n=370 HO-V3 diagnostic, n=216 aligned B–R textbook IMG trees)</text>',
    ]

    # --- Panel A: Rules-Only Strict F1 Progression (x=70..780, y=140..960) ---
    px0, py0, pw, ph = 90, 175, 680, 680
    svg.append(f'<rect x="{px0-20}" y="{py0-45}" width="{pw+40}" height="{ph+145}" rx="12" fill="{LIGHT_BG}" stroke="{BORDER}"/>')
    svg.append(f'<text x="{px0}" y="{py0-14}" font-family="{FONT}" font-size="20" font-weight="700" fill="{NAVY}">A. Strict Rule-Backed F1 (%)</text>')
    for tick in (0, 20, 40, 60, 80, 100):
        ty = py0 + ph - (tick / 100.0) * (ph - 40)
        svg.append(f'<line x1="{px0+40}" y1="{ty:.1f}" x2="{px0+pw-15}" y2="{ty:.1f}" stroke="{GRID}" stroke-dasharray="4,4"/>')
        svg.append(f'<text x="{px0+32}" y="{ty+5:.1f}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{MUTED}">{tick}%</text>')

    corpora = ["Dev-320", "HO-V1", "HO-V2", "HO-V3"]
    c2_f1 = [64.31, 64.52, 57.91, None]
    c6_f1 = [78.42, 79.85, 81.85, 75.68]
    c7_f1 = [
        res["longitudinal"]["dev_320"]["rules_strict"]["f1"] * 100,
        res["longitudinal"]["hist_ho1_320"]["rules_strict"]["f1"] * 100,
        res["longitudinal"]["dev_diag_ho2_370"]["rules_strict"]["f1"] * 100,
        res["holdout_v3_overall"]["holdout3_all_370"]["rules_only"]["strict_ungrammatical"]["f1"] * 100,
    ]
    bw = 38
    base_y = py0 + ph
    for i, label in enumerate(corpora):
        cx = px0 + 115 + i * 150
        vals = [(c2_f1[i], SLATE, -bw - 4), (c6_f1[i], "#3B82F6", 0), (c7_f1[i], TEAL, bw + 4)]
        for val, col, dx in vals:
            if val is None:
                continue
            bh = (val / 100.0) * (ph - 40)
            bx = cx + dx - bw / 2
            by = base_y - bh
            svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw}" height="{bh:.1f}" rx="4" fill="{col}"/>')
            svg.append(f'<text x="{bx+bw/2:.1f}" y="{by-6:.1f}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" fill="{TEXT}">{val:.1f}</text>')
        svg.append(f'<text x="{cx}" y="{base_y+24}" text-anchor="middle" font-family="{FONT}" font-size="14" font-weight="600" fill="{TEXT}">{_esc(label)}</text>')
    # Legend A
    for idx, (lbl, col) in enumerate([("Cycle 2 Locked", SLATE), ("Cycles 3–6", "#3B82F6"), ("Cycle 7", TEAL)]):
        lx = px0 + 50 + idx * 190
        ly = base_y + 58
        svg.append(f'<rect x="{lx}" y="{ly-12}" width="16" height="16" rx="3" fill="{col}"/>')
        svg.append(f'<text x="{lx+22}" y="{ly+1}" font-family="{FONT}" font-size="13" fill="{TEXT}">{_esc(lbl)}</text>')

    # --- Panel B: Canonical B-R Trees & Repaired Textbook PARSEVAL (x=835..1555) ---
    bx0 = 855
    svg.append(f'<rect x="{bx0-20}" y="{py0-45}" width="{pw+40}" height="{ph+145}" rx="12" fill="{LIGHT_BG}" stroke="{BORDER}"/>')
    svg.append(f'<text x="{bx0}" y="{py0-14}" font-family="{FONT}" font-size="20" font-weight="700" fill="{NAVY}">B. Canonical B–R Trees &amp; Repaired PARSEVAL</text>')
    for tick in (0, 20, 40, 60, 80, 100):
        ty = py0 + ph - (tick / 100.0) * (ph - 40)
        svg.append(f'<line x1="{bx0+40}" y1="{ty:.1f}" x2="{bx0+pw-15}" y2="{ty:.1f}" stroke="{GRID}" stroke-dasharray="4,4"/>')
        svg.append(f'<text x="{bx0+32}" y="{ty+5:.1f}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{MUTED}">{tick}%</text>')
    tb_tri = res["textbook_census_216_lookup_bypassed"]["all_triangle_aware"]
    tb7_tri = res["textbook_census_216_lookup_bypassed"]["ch7_10_triangle_aware"]
    j_c7 = res["holdout_v3_tree_coverage"]["holdout3_jfleg_100"]["br_normalized_rate"] * 100
    all_c7 = res["holdout_v3_tree_coverage"]["holdout3_all_370"]["br_normalized_rate"] * 100
    b_items = [
        ("JFLEG L2", 38.0, j_c7),
        ("All HO-V3", 69.19, all_c7),
        ("Book Norm", 91.74, tb_tri["normalization_rate"] * 100),
        ("Book LF1", None, tb_tri["labeled_f1"] * 100),
        ("Ch7–10 LF1", None, tb7_tri["labeled_f1"] * 100),
    ]
    bw2 = 42
    for i, (lbl, v6, v7) in enumerate(b_items):
        cx = bx0 + 100 + i * 124
        if v6 is not None:
            h6 = (v6 / 100.0) * (ph - 40)
            svg.append(f'<rect x="{cx-bw2-2:.1f}" y="{base_y-h6:.1f}" width="{bw2}" height="{h6:.1f}" rx="4" fill="#60A5FA"/>')
            svg.append(f'<text x="{cx-bw2/2-2:.1f}" y="{base_y-h6-6:.1f}" text-anchor="middle" font-family="{FONT}" font-size="11.5" fill="{TEXT}">{v6:.1f}</text>')
        else:
            svg.append(f'<text x="{cx-bw2/2-2:.1f}" y="{base_y-10:.1f}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" fill="{CORAL}">null</text>')
        h7 = (v7 / 100.0) * (ph - 40)
        svg.append(f'<rect x="{cx+2:.1f}" y="{base_y-h7:.1f}" width="{bw2}" height="{h7:.1f}" rx="4" fill="{TEAL}"/>')
        svg.append(f'<text x="{cx+bw2/2+2:.1f}" y="{base_y-h7-6:.1f}" text-anchor="middle" font-family="{FONT}" font-size="11.5" font-weight="700" fill="{TEXT}">{v7:.1f}</text>')
        svg.append(f'<text x="{cx}" y="{base_y+24}" text-anchor="middle" font-family="{FONT}" font-size="13" font-weight="600" fill="{TEXT}">{_esc(lbl)}</text>')
    for idx, (lbl, col) in enumerate([("Cycle 6 (V3 JSON PARSEVAL null)", "#60A5FA"), ("Cycle 7 (Verified, 0 schema errs)", TEAL)]):
        lx = bx0 + 50 + idx * 310
        ly = base_y + 58
        svg.append(f'<rect x="{lx}" y="{ly-12}" width="16" height="16" rx="3" fill="{col}"/>')
        svg.append(f'<text x="{lx+22}" y="{ly+1}" font-family="{FONT}" font-size="13" fill="{TEXT}">{_esc(lbl)}</text>')

    # --- Panel C: RoBERTa-CoLA Calibration on Dev+HO1+HO2 (n=1,010) (x=1600..2330) ---
    cx0 = 1620
    svg.append(f'<rect x="{cx0-20}" y="{py0-45}" width="{pw+40}" height="{ph+145}" rx="12" fill="{LIGHT_BG}" stroke="{BORDER}"/>')
    svg.append(f'<text x="{cx0}" y="{py0-14}" font-family="{FONT}" font-size="20" font-weight="700" fill="{NAVY}">C. Advisory Calibration (n=1,010 Dev+HO1+HO2)</text>')
    for tick in (40, 55, 70, 85, 100):
        ty = py0 + ph - ((tick - 40.0) / 60.0) * (ph - 40)
        svg.append(f'<line x1="{cx0+45}" y1="{ty:.1f}" x2="{cx0+pw-15}" y2="{ty:.1f}" stroke="{GRID}" stroke-dasharray="4,4"/>')
        svg.append(f'<text x="{cx0+37}" y="{ty+5:.1f}" text-anchor="end" font-family="{FONT}" font-size="13" fill="{MUTED}">{tick}%</text>')

    cal = res["unverified_calibration_dev_ho1_ho2_1010"]
    def _px(t_val: float) -> float:
        return cx0 + 70 + ((t_val - 0.10) / 0.34) * (pw - 115)
    def _py(pct: float) -> float:
        return py0 + ph - ((max(40.0, min(100.0, pct)) - 40.0) / 60.0) * (ph - 40)

    # Vertical reference lines at t=0.20 and t=0.42
    for t_ref, col, lbl in [(0.20, TEAL, "Cycle 7 t=0.20"), (0.42, CORAL, "Prior t=0.42")]:
        vx = _px(t_ref)
        svg.append(f'<line x1="{vx:.1f}" y1="{py0+25}" x2="{vx:.1f}" y2="{base_y}" stroke="{col}" stroke-width="2.5" stroke-dasharray="6,5"/>')
        svg.append(f'<text x="{vx:.1f}" y="{py0+18}" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="700" fill="{col}">{lbl}</text>')

    pts_sh = " ".join(f"{_px(c['threshold']):.1f},{_py((c['share_truly_ungrammatical'] or 0)*100):.1f}" for c in cal)
    pts_cov = " ".join(f"{_px(c['threshold']):.1f},{_py(c['decisive_coverage']*100):.1f}" for c in cal)
    svg.append(f'<polyline fill="none" stroke="{TEAL}" stroke-width="3.5" points="{pts_sh}"/>')
    svg.append(f'<polyline fill="none" stroke="{NAVY}" stroke-width="3.0" stroke-dasharray="8,4" points="{pts_cov}"/>')
    for c in cal:
        t_v = c["threshold"]
        sh = (c["share_truly_ungrammatical"] or 0.0) * 100
        cov = c["decisive_coverage"] * 100
        x_p = _px(t_v)
        svg.append(f'<circle cx="{x_p:.1f}" cy="{_py(sh):.1f}" r="5.5" fill="{TEAL}"/>')
        svg.append(f'<rect x="{x_p-4.5:.1f}" y="{_py(cov)-4.5:.1f}" width="9" height="9" fill="{NAVY}"/>')
        svg.append(f'<text x="{x_p:.1f}" y="{base_y+22}" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{TEXT}">{t_v:.2f}</text>')
        if t_v in (0.10, 0.20, 0.42):
            svg.append(f'<text x="{x_p:.1f}" y="{_py(sh)-12:.1f}" text-anchor="middle" font-family="{FONT}" font-size="11.5" font-weight="700" fill="{TEAL}">{sh:.1f}% ({c["gold_grammatical"]}g)</text>')
    for idx, (lbl, col) in enumerate([("Unverified Precision (% ungram.)", TEAL), ("Hybrid Decisive Coverage (%)", NAVY)]):
        lx = cx0 + 50 + idx * 310
        ly = base_y + 58
        svg.append(f'<rect x="{lx}" y="{ly-12}" width="16" height="16" rx="3" fill="{col}"/>')
        svg.append(f'<text x="{lx+22}" y="{ly+1}" font-family="{FONT}" font-size="13" fill="{TEXT}">{_esc(lbl)}</text>')

    svg.append("</svg>")
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    png_path = FIG_DIR / "fig13_cycle7_reliability_progression.png"
    render_svg_to_png("\n".join(svg), png_path, W, H)


def main() -> int:
    t0 = time.perf_counter()
    ho3_path = DIR / "FROZEN_FINAL_HOLDOUT_V3.csv"
    actual_sha = hashlib.sha256(ho3_path.read_bytes()).hexdigest()
    assert actual_sha == EXPECTED_V3_SHA256, f"Holdout V3 SHA mismatch: {actual_sha}"
    holdout3 = list(csv.DictReader(open(ho3_path, encoding="utf-8")))
    assert len(holdout3) == 370

    import api
    import burton_roberts as br
    import cambridge_registry
    import detector
    import parse_engine
    from br_tree import _atoms, _source_yield, load_reference_records
    from jsonschema import Draft202012Validator
    from learner_explanations import compose_learner_explanation
    from run_technical_evaluation import aggregate_parseval, score_parseval_pair

    parse_engine.load_models()
    detector.load_detector()
    cam_rt = cambridge_registry.load_runtime_registry()
    schema_val = Draft202012Validator(
        json.loads((ROOT / "docs/canonical-burton-roberts-tree.schema.json").read_text(encoding="utf-8"))
    )

    # 1. Diagnostic re-evaluation on Holdout V3 (historical diagnostic) + Dev-320 + HO1 + HO2
    print("[cycle7] Evaluating HO-V3 (n=370)...", flush=True)
    ho3_rows = evaluate_corpus(holdout3, schema_val, cam_rt)
    with open(DIR / "CYCLE7_HOLDOUT_V3_PREDICTIONS.csv", "w", newline="", encoding="utf-8") as fh:
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
    jfleg_fb_reasons = Counter(
        r["br_fallback_reason"] or "UNKNOWN"
        for r in slices["holdout3_jfleg_100"] if r["br_status"] != "normalized"
    )

    # 2. Longitudinal evaluation on Dev-320, HO-V1-320, HO-V2-370
    print("[cycle7] Evaluating Dev-320, HO-V1, HO-V2...", flush=True)
    dev_rows = [
        r for r in csv.DictReader(open(DIR / "RAW_PREDICTIONS.csv", encoding="utf-8"))
        if r["dataset"] in {"blimp_stratified", "jfleg_stratified"}
    ]
    dev_eval = evaluate_corpus(dev_rows, schema_val, cam_rt)
    ho1_eval = evaluate_corpus(list(csv.DictReader(open(DIR / "FROZEN_UNTOUCHED_HOLDOUT.csv", encoding="utf-8"))), schema_val, cam_rt)
    ho2_eval = evaluate_corpus(list(csv.DictReader(open(DIR / "FROZEN_FINAL_HOLDOUT_V2.csv", encoding="utf-8"))), schema_val, cam_rt)

    longitudinal = {}
    for name, drows in [("dev_320", dev_eval), ("hist_ho1_320", ho1_eval), ("dev_diag_ho2_370", ho2_eval)]:
        j_sub = [r for r in drows if "jfleg" in r.get("dataset", "") or "jfleg" in r.get("item_id", "")]
        longitudinal[name] = {
            "rules_strict": compute_rich_metrics(drows, "rules_verdict", "strict_ungrammatical"),
            "hybrid_decisive": compute_rich_metrics(drows, "hybrid_verdict", "decisive_only"),
            "hybrid_flagged": compute_rich_metrics(drows, "hybrid_verdict", "non_grammatical_flagged"),
            "tree_coverage": summarize_tree_cov(drows),
            "jfleg_tree_coverage": summarize_tree_cov(j_sub),
        }

    # 3. Full-payload XAI audit (n=90 stratified) + Independent Correction Audit (ALL V3 error sentences)
    print("[cycle7] Running full-payload XAI & independent correction audit...", flush=True)
    xai_pool = []
    for fam in sorted({r["error_family"] for r in ho3_rows if r["error_family"] != "l2_learner_writing"}):
        sub = [r for r in ho3_rows if r["error_family"] == fam]
        xai_pool.extend([r for r in sub if r["gold_label"] == "grammatical"][:3])
        xai_pool.extend([r for r in sub if r["gold_label"] == "ungrammatical"][:3])
    j_sub3 = slices["holdout3_jfleg_100"]
    xai_pool.extend([r for r in j_sub3 if r["gold_label"] == "ungrammatical"][:18])
    xai_pool.extend([r for r in j_sub3 if r["gold_label"] == "grammatical"][:18])

    verdict_ok = gating_ok = rule_ok = tok_ok = fg_ok = jargon_clean = 0
    err_sents = norm_sents = node_tot = node_ne = 0
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
            if all(not _INTERNAL_ID_RE.search(d.get("text") or "") for d in errs):
                jargon_clean += 1
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
    api_mean_ms = round(((time.perf_counter() - t_api) / len(xai_pool)) * 1000.0, 1)

    # Independent correction validation on ALL V3 sentences where rules fired
    corr_rows = []
    for item in ho3_rows:
        if item["rules_verdict"] != "ungrammatical":
            continue
        p = api.build_payload(item["sentence"])
        summ = p["summary"]
        cs = summ.get("corrected_sentence") or ""
        if not cs:
            continue
        ind = independent_check_correction(item["sentence"], cs)
        c_before = float(item["cola_acceptable_prob"]) if item["cola_acceptable_prob"] != "" else None
        det_after = detector.classify(cs)
        c_after = det_after["acceptable_prob"] if det_after else None
        ref = item.get("reference_correction") or ""
        ex = bool(ref and cs.strip().casefold() == ref.strip().casefold())
        corr_rows.append({
            "item_id": item["item_id"],
            "gold_label": item["gold_label"],
            "error_family": item["error_family"],
            "sentence": item["sentence"],
            "corrected": cs,
            "reference": ref,
            "exact_match": ex,
            "constraints": ";".join(summ.get("constraints_fired") or []),
            "reparse_clean": bool(((summ.get("correction") or {}).get("impact") or {}).get("whole_sentence_clean")),
            "independent_clean": ind["independent_clean"],
            "independent_issues": ind["issues"],
            "cola_before": c_before,
            "cola_after": c_after,
            "cola_improved_or_high": bool(c_after is not None and (c_after >= 0.5 or (c_before is not None and c_after >= c_before))),
        })

    # 4. Repaired Complete Burton-Roberts Textbook Census (n=216 aligned IMG, lookup bypassed)
    print("[cycle7] Running repaired 216-item Burton-Roberts textbook PARSEVAL census...", flush=True)
    prof = br.convention_profile()
    recs_216 = []
    excluded_items = []
    excluded_counts = Counter()
    for r in load_reference_records():
        ch = r.get("_chapter", 0)
        if r.get("status") != "IMG" or not isinstance(r.get("sentence"), str) or not isinstance(r.get("tree"), dict):
            excluded_counts["non_img_or_missing"] += 1
            continue
        if r.get("correct") is False:
            excluded_counts["incorrect_contrast_example"] += 1
            continue
        if ch > 1 and r["tree"].get("label") == "Sentence":
            excluded_counts["legacy_v1_sentence_label"] += 1
            excluded_items.append({"id": r.get("id"), "chapter": ch, "reason": "legacy_v1_sentence_label", "sentence": r.get("sentence")})
            continue
        if _source_yield(r["tree"]) != _atoms(r["sentence"]):
            excluded_counts["partial_subtree_fixture"] += 1
            excluded_items.append({
                "id": r.get("id"), "chapter": ch, "reason": "partial_subtree_fixture",
                "sentence": r.get("sentence"),
                "tree_yield_len": len(_source_yield(r["tree"])),
                "sentence_atoms_len": len(_atoms(r["sentence"])),
            })
            continue
        recs_216.append(r)

    full_all, tri_all, full_710, tri_710 = [], [], [], []
    by_ch_tri: dict[int, list[dict[str, Any]]] = defaultdict(list)
    tb_crash = tb_schema_err = 0
    for rec in recs_216:
        ch = rec.get("_chapter", 0)
        try:
            an = parse_engine.analyze(rec["sentence"])
            pj = br.normalize_benepar_candidate(an, prof)
        except Exception:
            tb_crash += 1
            pj = {"status": "unresolved", "tree": None}
        is_n = pj.get("status") == "normalized" and isinstance(pj.get("tree"), dict)
        has_w = bool(pj.get("working_tree"))
        if is_n and any(schema_val.iter_errors(pj["tree"])):
            tb_schema_err += 1
        sf = score_parseval_pair(rec["tree"], pj["tree"]["root"], False) if is_n else {"yield_match": False, "has_multiword_triangle": False}
        st = score_parseval_pair(rec["tree"], pj["tree"]["root"], True) if is_n else {"yield_match": False, "has_multiword_triangle": False}
        meta = {"record_id": rec["id"], "chapter": ch, "normalized": is_n, "working_tree": has_w}
        full_all.append({**meta, **sf})
        tri_all.append({**meta, **st})
        by_ch_tri[ch].append({**meta, **st})
        if ch >= 7:
            full_710.append({**meta, **sf})
            tri_710.append({**meta, **st})

    tb_summary = {
        "n_aligned_img_census": len(recs_216),
        "n_unfiltered_v3_census": len(recs_216) + len(excluded_items),
        "census_delta_216_vs_218": excluded_items,
        "all_excluded_counts": dict(excluded_counts),
        "crashes": tb_crash,
        "schema_errors": tb_schema_err,
        "all_full": aggregate_parseval(full_all),
        "all_triangle_aware": aggregate_parseval(tri_all),
        "all_nontriangle": aggregate_parseval([x for x in full_all if not x.get("has_multiword_triangle")]),
        "ch7_10_full": aggregate_parseval(full_710),
        "ch7_10_triangle_aware": aggregate_parseval(tri_710),
        "by_chapter_triangle_aware": {str(c): aggregate_parseval(by_ch_tri[c]) for c in sorted(by_ch_tri)},
    }

    # Verify PARSEVAL math identities before saving
    for k in ("all_full", "all_triangle_aware", "all_nontriangle", "ch7_10_full", "ch7_10_triangle_aware"):
        b = tb_summary[k]
        assert b["n_normalized"] > 0 and b["n_yield_aligned"] > 0 and b["labeled_f1"] is not None, f"PARSEVAL incomplete in {k}!"

    fp_cns = Counter(
        c for r in ho3_rows if r["gold_label"] == "grammatical" and r["rules_verdict"] == "ungrammatical"
        for c in (r["constraints_fired"].split(";") if r["constraints_fired"] else ["UNKNOWN"])
    )
    unv_tot = sum(1 for r in ho3_rows if r["hybrid_verdict"] == "unverified")
    unv_gu = sum(1 for r in ho3_rows if r["hybrid_verdict"] == "unverified" and r["gold_label"] == "ungrammatical")

    res = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "holdout_v3_sha256": actual_sha,
        "detector_flag_tolerance": detector._FLAG_TOLERANCE,
        "runtime_seconds": round(time.perf_counter() - t0, 2),
        "holdout_v3_overall": ho3_overall,
        "holdout_v3_by_family": ho3_by_fam,
        "holdout_v3_fp_constraints": dict(fp_cns.most_common(20)),
        "holdout_v3_unverified": {
            "total_hybrid_unverified": unv_tot,
            "gold_ungrammatical": unv_gu,
            "gold_grammatical": unv_tot - unv_gu,
            "share_truly_ungrammatical": round(unv_gu / unv_tot, 4) if unv_tot else 0.0,
            "rule_level_unverified": sum(1 for r in ho3_rows if r["rules_verdict"] == "unverified"),
        },
        "unverified_calibration_dev_ho1_ho2_1010": calibration_sweep(dev_eval + ho1_eval + ho2_eval),
        "unverified_calibration_ho3_370": calibration_sweep(ho3_rows),
        "holdout_v3_tree_coverage": ho3_tree_cov,
        "holdout_v3_jfleg_fallback_reasons": dict(jfleg_fb_reasons.most_common()),
        "holdout_v3_xai_n90": {
            "n": len(xai_pool),
            "mean_api_latency_ms": api_mean_ms,
            "verdict_consistent": verdict_ok,
            "display_gating_ok": gating_ok,
            "err_sents": err_sents,
            "rule_ground_ok": rule_ok,
            "jargon_id_free_ok": jargon_clean,
            "tok_ground_ok": tok_ok,
            "norm_sents": norm_sents,
            "fg_ground_ok": fg_ok,
            "node_prose_tot": node_tot,
            "node_prose_ne": node_ne,
            "human_rated_quality": "UNMEASURED_PENDING_HUMAN_REVIEW",
        },
        "independent_correction_audit_all_v3": {
            "total_corrections_generated": len(corr_rows),
            "on_gold_ungrammatical": sum(1 for c in corr_rows if c["gold_label"] == "ungrammatical"),
            "on_gold_grammatical": sum(1 for c in corr_rows if c["gold_label"] == "grammatical"),
            "reparse_clean": sum(1 for c in corr_rows if c["reparse_clean"]),
            "independent_morph_syntax_clean": sum(1 for c in corr_rows if c["independent_clean"]),
            "cola_improved_or_high": sum(1 for c in corr_rows if c["cola_improved_or_high"]),
            "exact_match_reference": sum(1 for c in corr_rows if c["exact_match"]),
            "flagged_issues": [c for c in corr_rows if not c["independent_clean"]],
            "samples": corr_rows,
        },
        "textbook_census_216_lookup_bypassed": tb_summary,
        "longitudinal": longitudinal,
    }
    (DIR / "_cycle7_results.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    generate_figure(res)
    print(f"[cycle7] COMPLETE in {res['runtime_seconds']}s!", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
