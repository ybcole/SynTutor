#!/usr/bin/env python3
"""Cycle 8 Locked Evaluation, Blind Generalization (Eval V4), Correction Safety,
Structural PARSEVAL, XAI End-to-End Validation, and Controlled Latency Benchmark.

Methodological discipline:
- Verifies SHA-256 integrity of FROZEN_INDEPENDENT_EVAL_V4.csv (strictly blind,
  frozen BEFORE Cycle 8 code changes) and FROZEN_FINAL_HOLDOUT_V3.csv (diagnostic).
- Never overwrites Cycle 0-7 historical datasets or results.
- Saves raw predictions (CYCLE8_INDEPENDENT_EVAL_V4_PREDICTIONS.csv,
  CYCLE8_HOLDOUT_V3_DIAGNOSTIC_PREDICTIONS.csv), full JSON metrics
  (_cycle8_results.json), blinded human review worksheet
  (HUMAN_REVIEW_WORKSHEET_V4_BLIND.csv, all reviewer columns strictly blank),
  and reproducible SVG/PNG figure (fig14_cycle8_generalization_and_safety).
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import statistics
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
EXPECTED_V4_SHA256 = "1d468942f7e9886039fa1c77df55668609e1cac1b70fcbcda0da8f2c0f0b4fe6"

_INTERNAL_ID_RE = re.compile(
    r"\b(?:C-[A-Z0-9-]{3,}|CLS-\d+|DET-\d+|NP-\d+|VP-\d+|SYN-\d+)\b"
)
_NEG_TOKEN_RE = re.compile(
    r"(?:(?<!\w)(?:not|never|no|none|nothing|nobody|nowhere|neither|nor|"
    r"dont|cant|wont|doesnt|didnt|isnt|arent|wasnt|werent|hasnt|havent|"
    r"hadnt|shouldnt|wouldnt|couldnt|mustnt|aint|nt)(?!\w)|n't(?!\w))",
    re.I,
)
_DUP_PHRASE_RE = re.compile(r"\b([A-Za-z]+\s+[A-Za-z]+)\b(?=.*\b\1\b)", re.I)


def audit_correction_safety(
    orig: str,
    corr: str,
    constraints: list[str],
    ind_fn: Any,
) -> dict[str, Any]:
    """Independent automated safety + meaning-preservation audit of one repair."""
    ind = ind_fn(orig, corr)
    issues = list(ind["issues"])
    # 1. Polarity preservation (unless C-DOUBLE-NEG or C-NPI-LICENSING)
    n_orig = len(_NEG_TOKEN_RE.findall(orig))
    n_corr = len(_NEG_TOKEN_RE.findall(corr))
    polarity_preserved = True
    if n_orig != n_corr and not (set(constraints) & {"C-DOUBLE-NEG", "C-NPI-LICENSING"}):
        polarity_preserved = False
        issues.append(f"polarity_shift:{n_orig}->{n_corr}")
    # 2. Embedded terminal punctuation (? / !) inside sentence interior
    if re.search(r"[?!]\s+[A-Za-z]", corr) and not re.search(r"[?!]\s+[A-Za-z]", orig):
        issues.append("embedded_terminal_punct")
    # 3. Newly duplicated multi-word phrase
    orig_low = orig.lower()
    corr_low = corr.lower()
    for m in _DUP_PHRASE_RE.finditer(corr):
        ph = m.group(1).lower()
        if orig_low.count(ph) < corr_low.count(ph) and ph not in {
            "of the", "in the", "to the", "on the", "at the", "for the",
            "by the", "from the", "with the", "that the", "is a", "in a",
            "to a", "of a", "it is", "he is", "she is", "they are",
        }:
            issues.append(f"dup_phrase:{ph}")
            break
    # 4. Minimal edit ratio (symmetric word-set diff / len(orig_words))
    w_orig = re.findall(r"[A-Za-z0-9']+", orig_low)
    w_corr = re.findall(r"[A-Za-z0-9']+", corr_low)
    c_o, c_c = Counter(w_orig), Counter(w_corr)
    tok_edits = sum((c_o - c_c).values()) + sum((c_c - c_o).values())
    edit_ratio = round(tok_edits / max(1, len(w_orig)), 4)
    return {
        "independent_morph_syntax_clean": len(issues) == 0,
        "polarity_preserved": polarity_preserved,
        "token_edit_distance": tok_edits,
        "edit_ratio": edit_ratio,
        "issues": issues,
    }


def _esc(s: str) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def generate_figure(res: dict[str, Any]) -> None:
    """Render reproducible 3-panel Cycle 8 SVG + PNG figure from _cycle8_results.json."""
    from generate_figures import render_svg_to_png

    W, H = 1520, 560
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<defs><style>',
        'text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }',
        '.title { font-size: 19px; font-weight: 700; fill: #0f172a; }',
        '.sub { font-size: 12px; fill: #475569; }',
        '.ptitle { font-size: 14px; font-weight: 700; fill: #1e293b; }',
        '.axis { font-size: 10.5px; fill: #475569; }',
        '.val { font-size: 10px; font-weight: 700; fill: #0f172a; }',
        '.lbl { font-size: 10px; font-weight: 600; fill: #1e293b; }',
        '.leg { font-size: 10.5px; fill: #334155; }',
        '</style></defs>',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        '<text x="34" y="34" class="title">SynTutor Cycle 8 — Blind Generalization (Eval V4), Structural Accuracy &amp; Correction Safety</text>',
        '<text x="34" y="54" class="sub">Source: _cycle8_results.json | Locked Blind Eval V4 (n=360: 240 BLiMP, 20 JFLEG, 100 CoLA Rules-Only) | Lookup-Bypassed B-R Textbook Census (n=216)</text>',
    ]

    # Panel boxes
    panels = [
        (30, 74, 468, 464, "A. Diagnostic Sets vs Locked Blind Eval V4 (Rules Strict)"),
        (518, 74, 488, 464, "B. Blind Eval V4 Per-Family Strict F1 & Precision (%)"),
        (1026, 74, 464, 464, "C. Structural PARSEVAL & Correction Safety (%)"),
    ]
    for px, py, pw, ph, ptitle in panels:
        svg.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="8" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>')
        svg.append(f'<text x="{px + 16}" y="{py + 26}" class="ptitle">{_esc(ptitle)}</text>')

    # --- Panel A: Grouped bars (Precision vs Recall vs F1) across corpora ---
    v4 = res["blind_eval_v4_overall"]
    ho3 = res["diagnostic_ho3_overall"]["holdout3_all_370"]["rules_only"]["strict_ungrammatical"]
    a_groups = [
        ("HO-V3\n(Diag)", ho3["precision"] * 100, ho3["recall"] * 100, ho3["f1"] * 100),
        ("V4 Ext\n(n=260)", v4["eval4_uncontaminated_260"]["rules_only"]["strict_ungrammatical"]["precision"] * 100,
         v4["eval4_uncontaminated_260"]["rules_only"]["strict_ungrammatical"]["recall"] * 100,
         v4["eval4_uncontaminated_260"]["rules_only"]["strict_ungrammatical"]["f1"] * 100),
        ("V4 BLiMP\n(n=240)", v4["eval4_blimp_240"]["rules_only"]["strict_ungrammatical"]["precision"] * 100,
         v4["eval4_blimp_240"]["rules_only"]["strict_ungrammatical"]["recall"] * 100,
         v4["eval4_blimp_240"]["rules_only"]["strict_ungrammatical"]["f1"] * 100),
        ("V4 JFLEG\n(n=20)", v4["eval4_jfleg_20"]["rules_only"]["strict_ungrammatical"]["precision"] * 100,
         v4["eval4_jfleg_20"]["rules_only"]["strict_ungrammatical"]["recall"] * 100,
         v4["eval4_jfleg_20"]["rules_only"]["strict_ungrammatical"]["f1"] * 100),
        ("V4 CoLA*\n(n=100)", v4["eval4_cola_100"]["rules_only"]["strict_ungrammatical"]["precision"] * 100,
         v4["eval4_cola_100"]["rules_only"]["strict_ungrammatical"]["recall"] * 100,
         v4["eval4_cola_100"]["rules_only"]["strict_ungrammatical"]["f1"] * 100),
    ]
    ax0, ay0, aw, ah = 74, 128, 404, 326
    for pct in (0, 25, 50, 75, 100):
        yy = ay0 + ah - (pct / 100.0) * ah
        svg.append(f'<line x1="{ax0}" y1="{yy:.1f}" x2="{ax0 + aw}" y2="{yy:.1f}" stroke="#e2e8f0" stroke-dasharray="3,3"/>')
        svg.append(f'<text x="{ax0 - 8}" y="{yy + 4:.1f}" text-anchor="end" class="axis">{pct}%</text>')
    gw = aw / len(a_groups)
    colors_a = ("#0ea5e9", "#6366f1", "#0f766e")
    for gi, (lbl, p_v, r_v, f_v) in enumerate(a_groups):
        gx = ax0 + gi * gw + 10
        bw = 18
        for bi, val in enumerate((p_v, r_v, f_v)):
            bh = (val / 100.0) * ah
            bx = gx + bi * (bw + 3)
            by = ay0 + ah - bh
            svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw}" height="{bh:.1f}" rx="2" fill="{colors_a[bi]}"/>')
            svg.append(f'<text x="{bx + bw/2:.1f}" y="{by - 4:.1f}" text-anchor="middle" class="val">{val:.0f}</text>')
        lines = lbl.split("\n")
        cx = gx + 30
        svg.append(f'<text x="{cx:.1f}" y="{ay0 + ah + 16}" text-anchor="middle" class="lbl">{_esc(lines[0])}</text>')
        svg.append(f'<text x="{cx:.1f}" y="{ay0 + ah + 29}" text-anchor="middle" class="axis">{_esc(lines[1])}</text>')
    for li, (col, name) in enumerate(zip(colors_a, ("Precision", "Recall", "Strict F1"))):
        lx = 90 + li * 115
        svg.append(f'<rect x="{lx}" y="505" width="11" height="11" rx="2" fill="{col}"/>')
        svg.append(f'<text x="{lx + 16}" y="514" class="leg">{name}</text>')
    svg.append('<text x="48" y="531" class="axis">*CoLA is strictly independent for Rules-Only (in-distribution for Hybrid RoBERTa-CoLA).</text>')

    # --- Panel B: Horizontal bars for Blind Eval V4 families ---
    fams = res["blind_eval_v4_by_family"]
    fam_order = [
        ("subject_verb_agreement", "Subj-Verb Agree"),
        ("determiner_agreement", "Determiner Agree"),
        ("npi_licensing", "NPI Licensing"),
        ("pronoun_case_and_binding", "Pronoun Binding"),
        ("filler_gap_dependencies", "Filler-Gap"),
        ("island_effects", "Island Effects"),
        ("quantifiers_and_raising", "Quantifiers/Raising"),
        ("argument_structure", "Argument Struct"),
        ("l2_learner_writing", "JFLEG L2 (n=20)"),
        ("cola_general_syntax", "CoLA Rules (n=100)"),
    ]
    bx0, by0, bw_max = 656, 120, 248
    row_h = 37
    for pct in (0, 25, 50, 75, 100):
        xx = bx0 + (pct / 100.0) * bw_max
        svg.append(f'<line x1="{xx:.1f}" y1="{by0 - 6}" x2="{xx:.1f}" y2="{by0 + len(fam_order)*row_h - 6}" stroke="#e2e8f0" stroke-dasharray="3,3"/>')
        svg.append(f'<text x="{xx:.1f}" y="{by0 + len(fam_order)*row_h + 10}" text-anchor="middle" class="axis">{pct}%</text>')
    for idx, (fkey, label) in enumerate(fam_order):
        if fkey not in fams:
            continue
        m = fams[fkey]["rules_strict"]
        f1v = (m["f1"] or 0.0) * 100
        pv = (m["precision"] or 0.0) * 100
        yy = by0 + idx * row_h
        svg.append(f'<text x="{bx0 - 8}" y="{yy + 14}" text-anchor="end" class="lbl">{_esc(label)}</text>')
        w_p = (pv / 100.0) * bw_max
        w_f = (f1v / 100.0) * bw_max
        svg.append(f'<rect x="{bx0}" y="{yy}" width="{w_p:.1f}" height="10" rx="2" fill="#0ea5e9"/>')
        svg.append(f'<rect x="{bx0}" y="{yy + 12}" width="{w_f:.1f}" height="10" rx="2" fill="#0f766e"/>')
        svg.append(f'<text x="{bx0 + max(w_p, w_f) + 5:.1f}" y="{yy + 14}" class="val">P:{pv:.0f} F1:{f1v:.0f}</text>')
    svg.append('<rect x="656" y="510" width="11" height="11" rx="2" fill="#0ea5e9"/>')
    svg.append('<text x="672" y="519" class="leg">Precision (%)</text>')
    svg.append('<rect x="776" y="510" width="11" height="11" rx="2" fill="#0f766e"/>')
    svg.append('<text x="792" y="519" class="leg">Strict F1 (%)</text>')

    # --- Panel C: Structural PARSEVAL & Correction Safety ---
    tb = res["textbook_census_216_lookup_bypassed"]
    ca_v4 = res["correction_safety_audit_eval_v4"]
    ca_v3 = res["correction_safety_audit_ho3"]
    c_items = [
        ("Book Norm\n(216 IMG)", tb["all_triangle_aware"]["normalization_rate"] * 100, "#0f766e"),
        ("Book LF1\n(Ch3-10)", tb["ch3_10_triangle_aware"]["labeled_f1"] * 100, "#0d9488"),
        ("Book LF1\n(All 216)", tb["all_triangle_aware"]["labeled_f1"] * 100, "#14b8a6"),
        ("JFLEG B-R\n(HO3 100)", res["diagnostic_ho3_tree_coverage"]["holdout3_jfleg_100"]["br_normalized_rate"] * 100, "#0284c7"),
        ("JFLEG B-R\n(V4 n=20)", res["blind_eval_v4_tree_coverage"]["eval4_jfleg_20"]["br_normalized_rate"] * 100, "#2563eb"),
        ("Corr Safe\n(HO3+V4)", ((ca_v3["independent_morph_syntax_clean"] + ca_v4["independent_morph_syntax_clean"]) /
                                max(1, ca_v3["total_corrections_generated"] + ca_v4["total_corrections_generated"])) * 100, "#16a34a"),
        ("Polarity OK\n(HO3+V4)", ((ca_v3["polarity_preserved"] + ca_v4["polarity_preserved"]) /
                                  max(1, ca_v3["total_corrections_generated"] + ca_v4["total_corrections_generated"])) * 100, "#15803d"),
    ]
    cx0, cy0, cw, ch = 1070, 128, 404, 326
    for pct in (0, 25, 50, 75, 100):
        yy = cy0 + ch - (pct / 100.0) * ch
        svg.append(f'<line x1="{cx0}" y1="{yy:.1f}" x2="{cx0 + cw}" y2="{yy:.1f}" stroke="#e2e8f0" stroke-dasharray="3,3"/>')
        svg.append(f'<text x="{cx0 - 8}" y="{yy + 4:.1f}" text-anchor="end" class="axis">{pct}%</text>')
    step = cw / len(c_items)
    for i, (lbl, val, col) in enumerate(c_items):
        bx = cx0 + i * step + 10
        bw = step - 20
        bh = (val / 100.0) * ch
        by = cy0 + ch - bh
        svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="3" fill="{col}"/>')
        svg.append(f'<text x="{bx + bw/2:.1f}" y="{by - 5:.1f}" text-anchor="middle" class="val">{val:.1f}%</text>')
        lns = lbl.split("\n")
        svg.append(f'<text x="{bx + bw/2:.1f}" y="{cy0 + ch + 16}" text-anchor="middle" class="lbl">{_esc(lns[0])}</text>')
        svg.append(f'<text x="{bx + bw/2:.1f}" y="{cy0 + ch + 29}" text-anchor="middle" class="axis">{_esc(lns[1])}</text>')
    svg.append('<text x="1044" y="518" class="axis">Note: Automated safety gates != human linguistic certification (human review pending).</text>')
    svg.append("</svg>")

    svg_text = "\n".join(svg)
    svg_path = DIR / "figures" / "fig14_cycle8_generalization_and_safety.svg"
    png_path = DIR / "figures" / "fig14_cycle8_generalization_and_safety.png"
    svg_path.write_text(svg_text, encoding="utf-8")
    render_svg_to_png(svg_text, png_path, W, H)


def run_correction_audit(
    eval_rows: list[dict[str, Any]],
    api: Any,
    detector: Any,
    ind_fn: Any,
) -> dict[str, Any]:
    samples = []
    for item in eval_rows:
        if item["rules_verdict"] != "ungrammatical":
            continue
        p = api.build_payload(item["sentence"])
        summ = p["summary"]
        cs = summ.get("corrected_sentence") or ""
        if not cs:
            continue
        cns = summ.get("constraints_fired") or []
        saf = audit_correction_safety(item["sentence"], cs, cns, ind_fn)
        c_before = float(item["cola_acceptable_prob"]) if item["cola_acceptable_prob"] != "" else None
        det_after = detector.classify(cs)
        c_after = det_after["acceptable_prob"] if det_after else None
        ref = item.get("reference_correction") or ""
        ex = bool(ref and cs.strip().casefold() == ref.strip().casefold())
        samples.append({
            "item_id": item["item_id"],
            "dataset": item["dataset"],
            "gold_label": item["gold_label"],
            "error_family": item["error_family"],
            "sentence": item["sentence"],
            "corrected": cs,
            "reference": ref,
            "exact_match": ex,
            "constraints": ";".join(cns),
            "reparse_clean": bool(((summ.get("correction") or {}).get("impact") or {}).get("whole_sentence_clean")),
            "independent_clean": saf["independent_morph_syntax_clean"],
            "polarity_preserved": saf["polarity_preserved"],
            "token_edit_distance": saf["token_edit_distance"],
            "edit_ratio": saf["edit_ratio"],
            "independent_issues": saf["issues"],
            "cola_before": c_before,
            "cola_after": c_after,
            "cola_improved_or_high": bool(c_after is not None and (c_after >= 0.5 or (c_before is not None and c_after >= c_before))),
        })
    n_tot = len(samples)
    n_ungr_det = sum(1 for r in eval_rows if r["gold_label"] == "ungrammatical" and r["rules_verdict"] == "ungrammatical")
    n_on_u = sum(1 for s in samples if s["gold_label"] == "ungrammatical")
    n_on_g = sum(1 for s in samples if s["gold_label"] == "grammatical")
    return {
        "total_corrections_generated": n_tot,
        "correction_coverage_over_detected_ungrammatical": round(n_on_u / max(1, n_ungr_det), 4),
        "on_gold_ungrammatical": n_on_u,
        "on_gold_grammatical_false_repairs": n_on_g,
        "reparse_clean": sum(1 for s in samples if s["reparse_clean"]),
        "independent_morph_syntax_clean": sum(1 for s in samples if s["independent_clean"]),
        "polarity_preserved": sum(1 for s in samples if s["polarity_preserved"]),
        "cola_improved_or_high": sum(1 for s in samples if s["cola_improved_or_high"]),
        "exact_match_reference": sum(1 for s in samples if s["exact_match"]),
        "mean_token_edit_distance": round(statistics.mean([s["token_edit_distance"] for s in samples]), 2) if samples else 0.0,
        "mean_edit_ratio": round(statistics.mean([s["edit_ratio"] for s in samples]), 4) if samples else 0.0,
        "flagged_issues": [s for s in samples if not s["independent_clean"]],
        "samples": samples,
    }


def main() -> int:
    t0 = time.perf_counter()

    # 1. Integrity checks
    v3_path = DIR / "FROZEN_FINAL_HOLDOUT_V3.csv"
    v4_path = DIR / "FROZEN_INDEPENDENT_EVAL_V4.csv"
    v3_sha = hashlib.sha256(v3_path.read_bytes()).hexdigest()
    v4_sha = hashlib.sha256(v4_path.read_bytes()).hexdigest()
    assert v3_sha == EXPECTED_V3_SHA256, f"V3 SHA mismatch: {v3_sha}"
    assert v4_sha == EXPECTED_V4_SHA256, f"V4 SHA mismatch: {v4_sha}"

    # 2. Controlled Cold-Start Timing Measurement
    t_cold0 = time.perf_counter()
    import analysis_api as api
    import burton_roberts as br
    import cambridge_registry
    import detector
    import matrix
    import parse_engine
    from jsonschema import Draft202012Validator
    from learner_explanations import compose_learner_explanation
    from br_tree import _atoms, _source_yield, load_reference_records
    from run_cycle7_evaluation import (
        evaluate_corpus,
        independent_check_correction,
        summarize_tree_cov,
    )
    from run_final_holdout_v3 import compute_rich_metrics
    from run_technical_evaluation import aggregate_parseval, score_parseval_pair

    schema_val = Draft202012Validator(json.loads((ROOT / "docs/canonical-burton-roberts-tree.schema.json").read_text(encoding="utf-8")))
    cam_rt = cambridge_registry.load_runtime_registry()
    # First cold sentence triggers lazy loading of spaCy + Benepar + RoBERTa-CoLA
    _cold_payload = api.build_payload("The students read books in the library.")
    cold_startup_sec = round(time.perf_counter() - t_cold0, 2)
    print(f"[cycle8] Cold startup + 1st build_payload: {cold_startup_sec}s (flag_tol={detector._FLAG_TOLERANCE})", flush=True)

    # 3. Single-Shot Locked Blind Evaluation on FROZEN_INDEPENDENT_EVAL_V4.csv (n=360)
    print("[cycle8] Running single-shot locked blind evaluation on FROZEN_INDEPENDENT_EVAL_V4.csv (n=360)...", flush=True)
    v4_input = list(csv.DictReader(open(v4_path, encoding="utf-8")))
    v4_rows = evaluate_corpus(v4_input, schema_val, cam_rt)
    v4_pred_path = DIR / "CYCLE8_INDEPENDENT_EVAL_V4_PREDICTIONS.csv"
    with open(v4_pred_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(v4_rows[0].keys()))
        w.writeheader()
        w.writerows(v4_rows)

    v4_slices = {
        "eval4_uncontaminated_260": [r for r in v4_rows if r["provenance_tier"] == "tier1_uncontaminated_external"],
        "eval4_blimp_240": [r for r in v4_rows if r["dataset"] == "eval4_blimp"],
        "eval4_jfleg_20": [r for r in v4_rows if r["dataset"] == "eval4_jfleg"],
        "eval4_cola_100": [r for r in v4_rows if r["dataset"] == "eval4_cola"],
        "eval4_all_360_mixed": v4_rows,
    }
    v4_overall = {}
    for dname, drows in v4_slices.items():
        v4_overall[dname] = {}
        for mode, vf in [("rules_only", "rules_verdict"), ("hybrid_rules_plus_cola", "hybrid_verdict")]:
            v4_overall[dname][mode] = {
                op: compute_rich_metrics(drows, vf, op)
                for op in ("strict_ungrammatical", "decisive_only", "non_grammatical_flagged")
            }
    v4_by_fam = {}
    for fam in sorted({r["error_family"] for r in v4_rows}):
        sub = [r for r in v4_rows if r["error_family"] == fam]
        v4_by_fam[fam] = {
            "n": len(sub),
            "rules_strict": compute_rich_metrics(sub, "rules_verdict", "strict_ungrammatical"),
            "hybrid_decisive": compute_rich_metrics(sub, "hybrid_verdict", "decisive_only"),
            "hybrid_flagged": compute_rich_metrics(sub, "hybrid_verdict", "non_grammatical_flagged"),
            "tree_coverage": summarize_tree_cov(sub),
        }
    v4_tree_cov = {dname: summarize_tree_cov(drows) for dname, drows in v4_slices.items()}
    v4_fp_cns = Counter(
        c for r in v4_rows if r["gold_label"] == "grammatical" and r["rules_verdict"] == "ungrammatical"
        for c in (r["constraints_fired"].split(";") if r["constraints_fired"] else ["UNKNOWN"])
    )
    v4_unv_ext = [r for r in v4_slices["eval4_uncontaminated_260"] if r["hybrid_verdict"] == "unverified"]

    # 4. Diagnostic / Longitudinal Tracking on HO-V3, Dev-320, HO-V1, HO-V2
    print("[cycle8] Running longitudinal & diagnostic tracking (HO-V3, Dev-320, HO-V1, HO-V2)...", flush=True)
    ho3_rows = evaluate_corpus(list(csv.DictReader(open(v3_path, encoding="utf-8"))), schema_val, cam_rt)
    ho3_pred_path = DIR / "CYCLE8_HOLDOUT_V3_DIAGNOSTIC_PREDICTIONS.csv"
    with open(ho3_pred_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ho3_rows[0].keys()))
        w.writeheader()
        w.writerows(ho3_rows)

    ho3_slices = {
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
    ho3_overall = {
        dname: {
            mode: {op: compute_rich_metrics(drows, vf, op)
                   for op in ("strict_ungrammatical", "decisive_only", "non_grammatical_flagged")}
            for mode, vf in [("rules_only", "rules_verdict"), ("hybrid_rules_plus_cola", "hybrid_verdict")]
        }
        for dname, drows in ho3_slices.items()
    }
    ho3_tree_cov = {dname: summarize_tree_cov(drows) for dname, drows in ho3_slices.items()}
    ho3_jfleg_fb = Counter(
        r["br_fallback_reason"] or "UNKNOWN"
        for r in ho3_slices["holdout3_jfleg_100"] if r["br_status"] != "normalized"
    )

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

    # 5. Deep Correction Safety & Meaning-Preservation Audit (both Blind V4 and Diagnostic HO-V3)
    print("[cycle8] Running independent correction safety audit on Blind Eval V4 & HO-V3...", flush=True)
    corr_audit_v4 = run_correction_audit(v4_rows, api, detector, independent_check_correction)
    corr_audit_ho3 = run_correction_audit(ho3_rows, api, detector, independent_check_correction)

    # 6. End-to-End XAI Validation on Blind Eval V4 (n=100 stratified) + Blind Human Review Worksheet (n=60)
    print("[cycle8] Running end-to-end XAI chain validation on Blind Eval V4 (n=100)...", flush=True)
    xai_pool = []
    for fam in sorted({r["error_family"] for r in v4_rows if r["error_family"] not in {"l2_learner_writing", "cola_general_syntax"}}):
        sub = [r for r in v4_rows if r["error_family"] == fam]
        xai_pool.extend([r for r in sub if r["gold_label"] == "grammatical"][:3])
        xai_pool.extend([r for r in sub if r["gold_label"] == "ungrammatical"][:3])
    # All 20 JFLEG items + 32 CoLA (16g + 16u) -> 48 + 20 + 32 = 100
    xai_pool.extend(v4_slices["eval4_jfleg_20"])
    xai_pool.extend([r for r in v4_slices["eval4_cola_100"] if r["gold_label"] == "grammatical"][:16])
    xai_pool.extend([r for r in v4_slices["eval4_cola_100"] if r["gold_label"] == "ungrammatical"][:16])

    verdict_ok = gating_ok = rule_ok = tok_ok = fg_ok = jargon_clean = corr_align_ok = 0
    err_sents = norm_sents = node_tot = node_ne = corr_sents = 0
    human_rows = []
    t_api = time.perf_counter()
    for idx, item in enumerate(xai_pool):
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
        cs = summ.get("corrected_sentence") or ""
        if cs:
            corr_sents += 1
            if v == "ungrammatical" and bool(((summ.get("correction") or {}).get("impact") or {}).get("whole_sentence_clean")):
                corr_align_ok += 1
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

        # Build 60-item blinded human review worksheet (first 60 stratified across BLiMP, JFLEG, CoLA)
        if len(human_rows) < 60 and (idx % 2 == 0 or item["dataset"] == "eval4_jfleg"):
            human_rows.append({
                "review_id": f"HR-V4-{len(human_rows) + 1:03d}",
                "item_id": item["item_id"],
                "dataset": item["dataset"],
                "error_family": item["error_family"],
                "sentence": item["sentence"],
                "syntutor_verdict": v,
                "syntutor_constraints": ";".join(summ.get("constraints_fired") or []),
                "syntutor_br_status": bra.get("status", ""),
                "syntutor_correction": cs,
                "syntutor_primary_explanation": (errs[0].get("text") if errs else summ.get("explanation") or "")[:300],
                # 12 strictly blank dual-reviewer anchored rubric columns (1-5 Likert / Y-N)
                "r1_linguistic_correctness_1_5": "",
                "r1_syntax_tree_accuracy_1_5": "",
                "r1_rule_accuracy_1_5": "",
                "r1_correction_quality_1_5": "",
                "r1_explanation_clarity_1_5": "",
                "r1_educational_usefulness_1_5": "",
                "r2_linguistic_correctness_1_5": "",
                "r2_syntax_tree_accuracy_1_5": "",
                "r2_rule_accuracy_1_5": "",
                "r2_correction_quality_1_5": "",
                "r2_explanation_clarity_1_5": "",
                "r2_educational_usefulness_1_5": "",
                "r1_notes": "",
                "r2_notes": "",
            })
    api_mean_ms = round(((time.perf_counter() - t_api) / len(xai_pool)) * 1000.0, 1)

    hr_path = DIR / "HUMAN_REVIEW_WORKSHEET_V4_BLIND.csv"
    with open(hr_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(human_rows[0].keys()))
        w.writeheader()
        w.writerows(human_rows)

    # 7. Complete Lookup-Bypassed Burton-Roberts Textbook Census (n=216 aligned IMG)
    print("[cycle8] Running complete 216-item lookup-bypassed textbook PARSEVAL census...", flush=True)
    prof = br.convention_profile()
    recs_216 = []
    for r in load_reference_records():
        ch = r.get("_chapter", 0)
        if r.get("status") != "IMG" or not isinstance(r.get("sentence"), str) or not isinstance(r.get("tree"), dict):
            continue
        if r.get("correct") is False:
            continue
        if ch > 1 and r["tree"].get("label") == "Sentence":
            continue
        if _source_yield(r["tree"]) != _atoms(r["sentence"]):
            continue
        recs_216.append(r)

    full_all, tri_all, tri_310, full_710, tri_710 = [], [], [], [], []
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
        if ch >= 3:
            tri_310.append({**meta, **st})
        if ch >= 7:
            full_710.append({**meta, **sf})
            tri_710.append({**meta, **st})

    tb_summary = {
        "n_aligned_img_census": len(recs_216),
        "crashes": tb_crash,
        "schema_errors": tb_schema_err,
        "all_full": aggregate_parseval(full_all),
        "all_triangle_aware": aggregate_parseval(tri_all),
        "all_nontriangle": aggregate_parseval([x for x in full_all if not x.get("has_multiword_triangle")]),
        "ch3_10_triangle_aware": aggregate_parseval(tri_310),
        "ch7_10_full": aggregate_parseval(full_710),
        "ch7_10_triangle_aware": aggregate_parseval(tri_710),
        "by_chapter_triangle_aware": {str(c): aggregate_parseval(by_ch_tri[c]) for c in sorted(by_ch_tri)},
    }

    # 8. Controlled Warm Latency Benchmark (3 repeated passes x 30 stratified sentences)
    print("[cycle8] Running controlled warm latency benchmark (3 passes x 30 sentences)...", flush=True)
    bench_sents = [r["sentence"] for r in ho3_rows[:15]] + [r["sentence"] for r in ho3_slices["holdout3_jfleg_100"][:15]]
    stage_ms: dict[str, list[float]] = defaultdict(list)
    for _pass in range(3):
        for s in bench_sents:
            ta = time.perf_counter()
            an = parse_engine.analyze(s)
            tb_t = time.perf_counter()
            _m = matrix.evaluate(an["root"], text=an["sentence"])
            tc = time.perf_counter()
            _b = br.build_canonical_analysis(an)
            td = time.perf_counter()
            _d = detector.classify(s)
            te = time.perf_counter()
            _p = api.build_payload(s)
            tf = time.perf_counter()
            stage_ms["parse_engine_ms"].append((tb_t - ta) * 1000.0)
            stage_ms["matrix_eval_ms"].append((tc - tb_t) * 1000.0)
            stage_ms["br_canonical_ms"].append((td - tc) * 1000.0)
            stage_ms["cola_detector_ms"].append((te - td) * 1000.0)
            stage_ms["full_build_payload_ms"].append((tf - te) * 1000.0)

    def _lat_stats(vals: list[float]) -> dict[str, float]:
        sv = sorted(vals)
        p95 = sv[min(len(sv) - 1, int(0.95 * len(sv)))]
        return {
            "mean_ms": round(statistics.mean(sv), 2),
            "median_ms": round(statistics.median(sv), 2),
            "p95_ms": round(p95, 2),
            "n_samples": len(sv),
        }

    latency = {
        "cold_startup_plus_first_payload_sec": cold_startup_sec,
        "warm_passes": 3,
        "warm_sentences_per_pass": len(bench_sents),
        "stages": {k: _lat_stats(v) for k, v in stage_ms.items()},
    }

    res = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "holdout_v3_sha256": v3_sha,
        "independent_eval_v4_sha256": v4_sha,
        "detector_flag_tolerance": detector._FLAG_TOLERANCE,
        "runtime_seconds": round(time.perf_counter() - t0, 2),
        "blind_eval_v4_overall": v4_overall,
        "blind_eval_v4_by_family": v4_by_fam,
        "blind_eval_v4_tree_coverage": v4_tree_cov,
        "blind_eval_v4_fp_constraints": dict(v4_fp_cns.most_common()),
        "blind_eval_v4_uncontaminated_unverified": {
            "total": len(v4_unv_ext),
            "gold_ungrammatical": sum(1 for r in v4_unv_ext if r["gold_label"] == "ungrammatical"),
            "gold_grammatical": sum(1 for r in v4_unv_ext if r["gold_label"] == "grammatical"),
        },
        "diagnostic_ho3_overall": ho3_overall,
        "diagnostic_ho3_tree_coverage": ho3_tree_cov,
        "diagnostic_ho3_jfleg_fallback_reasons": dict(ho3_jfleg_fb.most_common()),
        "diagnostic_ho3_unverified": {
            "total": sum(1 for r in ho3_rows if r["hybrid_verdict"] == "unverified"),
            "gold_ungrammatical": sum(1 for r in ho3_rows if r["hybrid_verdict"] == "unverified" and r["gold_label"] == "ungrammatical"),
            "gold_grammatical": sum(1 for r in ho3_rows if r["hybrid_verdict"] == "unverified" and r["gold_label"] == "grammatical"),
        },
        "longitudinal": longitudinal,
        "correction_safety_audit_eval_v4": corr_audit_v4,
        "correction_safety_audit_ho3": corr_audit_ho3,
        "blind_eval_v4_xai_n100": {
            "n": len(xai_pool),
            "mean_api_latency_ms": api_mean_ms,
            "verdict_consistent": verdict_ok,
            "display_gating_ok": gating_ok,
            "err_sents": err_sents,
            "rule_ground_ok": rule_ok,
            "jargon_id_free_ok": jargon_clean,
            "tok_ground_ok": tok_ok,
            "corr_sents": corr_sents,
            "corr_align_ok": corr_align_ok,
            "norm_sents": norm_sents,
            "fg_ground_ok": fg_ok,
            "node_prose_tot": node_tot,
            "node_prose_ne": node_ne,
            "human_review_worksheet": "HUMAN_REVIEW_WORKSHEET_V4_BLIND.csv",
            "human_review_rows": len(human_rows),
            "human_rated_quality": "UNMEASURED / BLOCKED (0 completed human ratings)",
        },
        "textbook_census_216_lookup_bypassed": tb_summary,
        "latency_benchmark": latency,
    }

    out_json = DIR / "_cycle8_results.json"
    out_json.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    generate_figure(res)

    print("\n=== CYCLE 8 SUMMARY ===", flush=True)
    for k in ("eval4_uncontaminated_260", "eval4_blimp_240", "eval4_jfleg_20", "eval4_cola_100"):
        rs = v4_overall[k]["rules_only"]["strict_ungrammatical"]
        hd = v4_overall[k]["hybrid_rules_plus_cola"]["decisive_only"]
        print(f"  BLIND {k:26s}: Rules Acc={rs['accuracy']*100:.2f}% P={rs['precision']*100:.2f}% R={rs['recall']*100:.2f}% F1={rs['f1']*100:.2f}% (FP={rs['fp']}, FN={rs['fn']}) | HybDec={hd['accuracy']*100:.2f}% ({hd['coverage']*100:.1f}% cov)")
    h3rs = ho3_overall["holdout3_all_370"]["rules_only"]["strict_ungrammatical"]
    print(f"  DIAG  holdout3_all_370          : Rules Acc={h3rs['accuracy']*100:.2f}% P={h3rs['precision']*100:.2f}% R={h3rs['recall']*100:.2f}% F1={h3rs['f1']*100:.2f}% (FP={h3rs['fp']}, FN={h3rs['fn']})")
    print(f"  CORR  V4: total={corr_audit_v4['total_corrections_generated']} clean={corr_audit_v4['independent_morph_syntax_clean']} pol={corr_audit_v4['polarity_preserved']} false_rep={corr_audit_v4['on_gold_grammatical_false_repairs']}")
    print(f"  CORR  HO3: total={corr_audit_ho3['total_corrections_generated']} clean={corr_audit_ho3['independent_morph_syntax_clean']} pol={corr_audit_ho3['polarity_preserved']} false_rep={corr_audit_ho3['on_gold_grammatical_false_repairs']}")
    print(f"  TREE  HO3 JFLEG={ho3_tree_cov['holdout3_jfleg_100']['br_normalized']}/100 | V4 JFLEG={v4_tree_cov['eval4_jfleg_20']['br_normalized']}/20 | Book={tb_summary['all_triangle_aware']['n_normalized']}/216 LF1={tb_summary['all_triangle_aware']['labeled_f1']*100:.2f}% (Ch3-10 LF1={tb_summary['ch3_10_triangle_aware']['labeled_f1']*100:.2f}%)")
    print(f"  LAT   cold={cold_startup_sec}s | warm build_payload mean={latency['stages']['full_build_payload_ms']['mean_ms']}ms median={latency['stages']['full_build_payload_ms']['median_ms']}ms p95={latency['stages']['full_build_payload_ms']['p95_ms']}ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
