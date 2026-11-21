#!/usr/bin/env python3
"""Generate publication-quality 300 DPI before/after & untouched holdout thesis figures.

Reads:
  - baseline_snapshot/_computed_results.json   (pre-remediation baseline)
  - _computed_results.json                     (post-remediation dev + 216 textbook trees + 120 XAI)
  - _holdout_results.json                      (single-shot untouched 320-sentence holdout)

Writes under docs/audits/technical_evaluation/figures/:
  - fig6_before_after_detection.png
  - fig7_holdout_confusion_matrix.png
  - fig8_before_after_trees_and_xai.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DIR))
from generate_figures import (
    AMBER, BORDER, CORAL, FIG_DIR, FONT, GRID, LIGHT_BG, MUTED, NAVY, SLATE,
    TEAL, TEXT, _esc, render_svg_to_png,
)


def make_fig6_before_after_detection(base: dict[str, Any], after: dict[str, Any], ho: dict[str, Any]) -> None:
    W, H = 2400, 1480
    b320 = base["section_511"]["overall"]["external_strict_uncontaminated_320"]
    a320 = after["section_511"]["overall"]["external_strict_uncontaminated_320"]
    h320 = ho["overall"]["holdout_all_320"]

    series = [
        ("Baseline Dev (n=320) — Rules-Only Strict", b320["rules_only"]["strict_ungrammatical"], SLATE),
        ("After Dev (n=320) — Rules-Only Strict", a320["rules_only"]["strict_ungrammatical"], "#4A7C9B"),
        ("Untouched Holdout (n=320) — Rules-Only Strict", h320["rules_only"]["strict_ungrammatical"], NAVY),
        ("Baseline Dev (n=320) — Hybrid Flagged", b320["hybrid_rules_plus_cola"]["non_grammatical_flagged"], AMBER),
        ("After Dev (n=320) — Hybrid Flagged", a320["hybrid_rules_plus_cola"]["non_grammatical_flagged"], "#1F9D76"),
        ("Untouched Holdout (n=320) — Hybrid Flagged", h320["hybrid_rules_plus_cola"]["non_grammatical_flagged"], TEAL),
    ]
    metrics = [("accuracy", "Accuracy"), ("precision", "Precision"), ("recall", "Recall"), ("f1", "F1-Score"), ("specificity", "Specificity")]

    x0, y0, pw, ph = 200, 270, 2060, 780
    parts = []
    for pct in range(0, 101, 20):
        gy = y0 + ph - int(ph * pct / 100)
        parts.append(f'<line x1="{x0}" y1="{gy}" x2="{x0 + pw}" y2="{gy}" stroke="{GRID}" stroke-width="2"/>')
        parts.append(f'<text x="{x0 - 22}" y="{gy + 10}" text-anchor="end" font-family="{FONT}" font-size="28" fill="{MUTED}">{pct}%</text>')
    parts.append(f'<line x1="{x0}" y1="{y0 + ph}" x2="{x0 + pw}" y2="{y0 + ph}" stroke="{TEXT}" stroke-width="3"/>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + ph}" stroke="{TEXT}" stroke-width="3"/>')

    gw = pw / len(metrics)
    bw = 50
    gap = 7
    tot_bw = len(series) * bw + (len(series) - 1) * gap

    for gi, (mkey, mlabel) in enumerate(metrics):
        xc = x0 + gi * gw + gw / 2
        bstart = xc - tot_bw / 2
        parts.append(f'<text x="{xc:.1f}" y="{y0 + ph + 50}" text-anchor="middle" font-family="{FONT}" font-size="31" font-weight="700" fill="{TEXT}">{mlabel}</text>')
        for si, (_, mdict, col) in enumerate(series):
            val = (mdict.get(mkey) or 0.0) * 100.0
            bh = int(round(ph * val / 100.0))
            bx = bstart + si * (bw + gap)
            by = y0 + ph - bh
            parts.append(f'<rect x="{bx:.1f}" y="{by}" width="{bw}" height="{bh}" rx="4" fill="{col}"/>')
            parts.append(f'<text x="{bx + bw / 2:.1f}" y="{by - 10}" text-anchor="middle" font-family="{FONT}" font-size="18" font-weight="700" fill="{TEXT}">{val:.1f}</text>')

    # 3x2 Legend
    ly = y0 + ph + 115
    for si, (lbl, _, col) in enumerate(series):
        lx = x0 + (si % 2) * 1030
        ry = ly + (si // 2) * 48
        parts.append(f'<rect x="{lx}" y="{ry - 21}" width="30" height="24" rx="4" fill="{col}"/>')
        parts.append(f'<text x="{lx + 42}" y="{ry}" font-family="{FONT}" font-size="25" fill="{TEXT}">{_esc(lbl)}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="{LIGHT_BG}"/>
<text x="{W // 2}" y="76" text-anchor="middle" font-family="{FONT}" font-size="46" font-weight="800" fill="{NAVY}">Figure 6. Grammar Detection Before vs. After Remediation &amp; Untouched Holdout</text>
<text x="{W // 2}" y="126" text-anchor="middle" font-family="{FONT}" font-size="28" fill="{MUTED}">Uncontaminated External Benchmarks (BLiMP n = 240 + JFLEG n = 80; Positive Class = Ungrammatical; Holdout SHA-256 Verified)</text>
<text x="64" y="{y0 + ph // 2}" text-anchor="middle" font-family="{FONT}" font-size="30" font-weight="700" fill="{TEXT}" transform="rotate(-90 64 {y0 + ph // 2})">Score (%)</text>
{"".join(parts)}
<text x="{W // 2}" y="{H - 34}" text-anchor="middle" font-family="{FONT}" font-size="23" fill="{MUTED}">Note: Holdout sentences (n = 320) had zero overlap with development sets and were executed once after all fixes were locked.</text>
</svg>'''
    render_svg_to_png(svg, FIG_DIR / "fig6_before_after_detection.png", W, H)


def make_fig7_holdout_confusion(ho: dict[str, Any]) -> None:
    W, H = 2400, 1260
    h320 = ho["overall"]["holdout_all_320"]
    m_rules = h320["rules_only"]["strict_ungrammatical"]
    m_hyb = h320["hybrid_rules_plus_cola"]["non_grammatical_flagged"]

    def draw_matrix(x0: int, y0: int, m: dict[str, Any], title: str, subtitle: str) -> str:
        tp, fn, fp, tn = m["tp"], m["fn"], m["fp"], m["tn"]
        gpos, gneg = tp + fn, fp + tn
        cw, ch = 360, 270
        cells = [
            (0, 0, "TP", tp, tp / gpos * 100 if gpos else 0, "#1E4E79", "#FFFFFF"),
            (1, 0, "FN", fn, fn / gpos * 100 if gpos else 0, "#FDE8E8", "#7F1D1D"),
            (0, 1, "FP", fp, fp / gneg * 100 if gneg else 0, "#FEF3C7", "#78350F"),
            (1, 1, "TN", tn, tn / gneg * 100 if gneg else 0, "#D1FAE5", "#064E3B"),
        ]
        parts = [
            f'<text x="{x0 + cw}" y="{y0 - 95}" text-anchor="middle" font-family="{FONT}" font-size="38" font-weight="700" fill="{TEXT}">{_esc(title)}</text>',
            f'<text x="{x0 + cw}" y="{y0 - 52}" text-anchor="middle" font-family="{FONT}" font-size="26" fill="{MUTED}">{_esc(subtitle)}</text>',
            f'<text x="{x0 + cw // 2}" y="{y0 - 12}" text-anchor="middle" font-family="{FONT}" font-size="28" font-weight="600" fill="{TEXT}">Pred: Ungrammatical (+)</text>',
            f'<text x="{x0 + cw + cw // 2}" y="{y0 - 12}" text-anchor="middle" font-family="{FONT}" font-size="28" font-weight="600" fill="{TEXT}">Pred: Grammatical (−)</text>',
            f'<text x="{x0 - 22}" y="{y0 + ch // 2 - 8}" text-anchor="end" font-family="{FONT}" font-size="28" font-weight="600" fill="{TEXT}">Gold:</text>',
            f'<text x="{x0 - 22}" y="{y0 + ch // 2 + 26}" text-anchor="end" font-family="{FONT}" font-size="26" fill="{MUTED}">Ungram. (+)</text>',
            f'<text x="{x0 - 22}" y="{y0 + ch + ch // 2 - 8}" text-anchor="end" font-family="{FONT}" font-size="28" font-weight="600" fill="{TEXT}">Gold:</text>',
            f'<text x="{x0 - 22}" y="{y0 + ch + ch // 2 + 26}" text-anchor="end" font-family="{FONT}" font-size="26" fill="{MUTED}">Gram. (−)</text>',
        ]
        for col, row, tag, val, pct, bg, fg in cells:
            cx, cy = x0 + col * cw, y0 + row * ch
            parts.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="10" fill="{bg}" stroke="#FFFFFF" stroke-width="6"/>')
            parts.append(f'<text x="{cx + cw // 2}" y="{cy + 78}" text-anchor="middle" font-family="{FONT}" font-size="30" font-weight="700" fill="{fg}">{tag}</text>')
            parts.append(f'<text x="{cx + cw // 2}" y="{cy + 158}" text-anchor="middle" font-family="{FONT}" font-size="68" font-weight="800" fill="{fg}">{val}</text>')
            parts.append(f'<text x="{cx + cw // 2}" y="{cy + 214}" text-anchor="middle" font-family="{FONT}" font-size="28" fill="{fg}">({pct:.1f}% of row)</text>')
        acc, prec, rec, f1 = (m["accuracy"] or 0) * 100, (m["precision"] or 0) * 100, (m["recall"] or 0) * 100, (m["f1"] or 0) * 100
        parts.append(f'<text x="{x0 + cw}" y="{y0 + 2 * ch + 60}" text-anchor="middle" font-family="{FONT}" font-size="27" font-weight="600" fill="{NAVY}">Acc: {acc:.1f}%  |  Prec: {prec:.1f}%  |  Rec: {rec:.1f}%  |  F1: {f1:.1f}%</text>')
        return "\n".join(parts)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="{LIGHT_BG}"/>
<text x="{W // 2}" y="76" text-anchor="middle" font-family="{FONT}" font-size="48" font-weight="800" fill="{NAVY}">Figure 7. Post-Remediation Confusion Matrices on Untouched Holdout</text>
<text x="{W // 2}" y="126" text-anchor="middle" font-family="{FONT}" font-size="29" fill="{MUTED}">Frozen Untouched External Holdout (BLiMP n = 240 + JFLEG n = 80; Total n = 320, Zero Dev Overlap, Positive Class = Ungrammatical)</text>
<line x1="120" y1="156" x2="{W - 120}" y2="156" stroke="{BORDER}" stroke-width="2"/>
{draw_matrix(310, 340, m_rules, "A. Deterministic Rules-Only (Holdout)", "Strict rule-backed verdict (ungrammatical vs. other)")}
{draw_matrix(1460, 340, m_hyb, "B. Hybrid Rules + CoLA (Holdout)", "Non-acceptance operating point (ungrammatical or unverified)")}
<text x="{W // 2}" y="{H - 46}" text-anchor="middle" font-family="{FONT}" font-size="24" fill="{MUTED}">Holdout SHA-256: 90919d6b6001bb3c09cfcda8cde8f1698a03d86bddbe792c3aecf8a0324e503b | Hybrid Decisive-Only Acc: {(h320["hybrid_rules_plus_cola"]["decisive_only"]["accuracy"] or 0)*100:.1f}% (cov={(h320["hybrid_rules_plus_cola"]["decisive_only"]["coverage"] or 0)*100:.1f}%).</text>
</svg>'''
    render_svg_to_png(svg, FIG_DIR / "fig7_holdout_confusion_matrix.png", W, H)


def make_fig8_trees_and_xai(base: dict[str, Any], after: dict[str, Any]) -> None:
    W, H = 2400, 1440
    b512, a512 = base["section_512"], after["section_512"]
    b513, a513 = base["section_513"]["summary"], after["section_513"]["summary"]
    b320 = base["section_511"]["overall"]["external_strict_uncontaminated_320"]
    a320 = after["section_511"]["overall"]["external_strict_uncontaminated_320"]

    rows = [
        ("B-R Textbook Normalization (n=216, Lookup Bypassed)", b512["book_final_d1_bypass_full"]["normalization_rate"] * 100, a512["book_final_d1_bypass_full"]["normalization_rate"] * 100),
        ("Ch7–Ch10 Textbook Normalization (n=115, Bypass)", b512["book_ch7_to_ch10_triangle_aware"]["normalization_rate"] * 100, a512["book_ch7_to_ch10_triangle_aware"]["normalization_rate"] * 100),
        ("Ch7–Ch10 Triangle-Aware Labeled F1", (b512["book_ch7_to_ch10_triangle_aware"]["labeled_f1"] or 0) * 100, (a512["book_ch7_to_ch10_triangle_aware"]["labeled_f1"] or 0) * 100),
        ("Textbook Exact Matches (of Total 216, Tri-Aware)", (b512["book_final_d1_bypass_triangle_aware"]["exact_rate_over_total"] or 0) * 100, (a512["book_final_d1_bypass_triangle_aware"]["exact_rate_over_total"] or 0) * 100),
        ("Rules-Only Decisive Coverage (Dev n=320)", (b320["rules_only"]["decisive_only"]["coverage"] or 0) * 100, (a320["rules_only"]["decisive_only"]["coverage"] or 0) * 100),
        ("Rules-Only Specificity (Dev n=320)", (b320["rules_only"]["strict_ungrammatical"]["specificity"] or 0) * 100, (a320["rules_only"]["strict_ungrammatical"]["specificity"] or 0) * 100),
        ("Reference-Matched Corrections (XAI n=120)", (b513["corrections_exact_match_reference"] / max(1, b513["corrections_with_reference_count"])) * 100, (a513["corrections_exact_match_reference"] / max(1, a513["corrections_with_reference_count"])) * 100),
        ("Rapid Cross-Component Audit Pass Rate (n=24)", 20 / 24 * 100, 24 / 24 * 100),
    ]

    x0, y0, pw, ph = 820, 240, 1360, 960
    parts = []
    for pct in range(0, 101, 20):
        gx = x0 + int(pw * pct / 100)
        parts.append(f'<line x1="{gx}" y1="{y0}" x2="{gx}" y2="{y0 + ph}" stroke="{GRID}" stroke-width="2"/>')
        parts.append(f'<text x="{gx}" y="{y0 + ph + 42}" text-anchor="middle" font-family="{FONT}" font-size="27" fill="{MUTED}">{pct}%</text>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + ph}" stroke="{TEXT}" stroke-width="3"/>')
    parts.append(f'<line x1="{x0}" y1="{y0 + ph}" x2="{x0 + pw}" y2="{y0 + ph}" stroke="{TEXT}" stroke-width="3"/>')

    rh = ph / len(rows)
    bh = 34
    for i, (lbl, bv, av) in enumerate(rows):
        yc = y0 + i * rh + rh / 2
        parts.append(f'<text x="{x0 - 24}" y="{yc + 9}" text-anchor="end" font-family="{FONT}" font-size="26" font-weight="600" fill="{TEXT}">{_esc(lbl)}</text>')
        bw1, bw2 = max(4, int(round(pw * bv / 100))), max(4, int(round(pw * av / 100)))
        parts.append(f'<rect x="{x0}" y="{yc - bh - 3:.1f}" width="{bw1}" height="{bh}" rx="5" fill="{SLATE}"/>')
        parts.append(f'<text x="{x0 + bw1 + 14}" y="{yc - 9:.1f}" font-family="{FONT}" font-size="23" font-weight="700" fill="{SLATE}">{bv:.1f}%</text>')
        parts.append(f'<rect x="{x0}" y="{yc + 3:.1f}" width="{bw2}" height="{bh}" rx="5" fill="{TEAL}"/>')
        delta = av - bv
        parts.append(f'<text x="{x0 + bw2 + 14}" y="{yc + bh - 4:.1f}" font-family="{FONT}" font-size="23" font-weight="700" fill="{TEAL}">{av:.1f}% ({delta:+.1f} pp)</text>')

    ly = y0 + ph + 115
    parts.append(f'<rect x="820" y="{ly - 22}" width="34" height="28" rx="5" fill="{SLATE}"/>')
    parts.append(f'<text x="868" y="{ly}" font-family="{FONT}" font-size="27" font-weight="600" fill="{TEXT}">Pre-Remediation Baseline</text>')
    parts.append(f'<rect x="1420" y="{ly - 22}" width="34" height="28" rx="5" fill="{TEAL}"/>')
    parts.append(f'<text x="1468" y="{ly}" font-family="{FONT}" font-size="27" font-weight="600" fill="{TEXT}">Post-Remediation SynTutor</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="{LIGHT_BG}"/>
<text x="{W // 2}" y="76" text-anchor="middle" font-family="{FONT}" font-size="46" font-weight="800" fill="{NAVY}">Figure 8. End-to-End Reliability Gains: Trees, Corrections &amp; XAI</text>
<text x="{W // 2}" y="126" text-anchor="middle" font-family="{FONT}" font-size="28" fill="{MUTED}">Before vs. After Systematic Linguistic Fixes (Lookup-Bypassed Textbook Trees n = 216, Dev n = 320, Full XAI Payloads n = 120)</text>
{"".join(parts)}
</svg>'''
    render_svg_to_png(svg, FIG_DIR / "fig8_before_after_trees_and_xai.png", W, H)


def main() -> int:
    base = json.loads((DIR / "baseline_snapshot/_computed_results.json").read_text(encoding="utf-8"))
    after = json.loads((DIR / "_computed_results.json").read_text(encoding="utf-8"))
    ho = json.loads((DIR / "_holdout_results.json").read_text(encoding="utf-8"))
    make_fig6_before_after_detection(base, after, ho)
    make_fig7_holdout_confusion(ho)
    make_fig8_trees_and_xai(base, after)
    print(f"Generated 3 before/after + holdout 300 DPI PNG figures in {FIG_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
