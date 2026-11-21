#!/usr/bin/env python3
"""Generate publication-quality 300 DPI thesis figures from verified SynTutor results.

Reads docs/audits/technical_evaluation/_computed_results.json and renders clean
vector SVGs into 300 DPI PNGs under docs/audits/technical_evaluation/figures/
using macOS QuickLook (qlmanage) plus exact PNG pHYs 300 DPI metadata tagging.

Zero fabricated numbers: every value comes directly from _computed_results.json.
Human explanation clarity distribution is intentionally NOT plotted because zero
completed human reviewer assessments exist.
"""
from __future__ import annotations

import html
import json
import struct
import subprocess
import zlib
from pathlib import Path
from typing import Any

DIR = Path(__file__).resolve().parent
FIG_DIR = DIR / "figures"

# Academic colorblind-safe palette
NAVY = "#1B365D"
TEAL = "#2A9D8F"
AMBER = "#E9A03B"
CORAL = "#C8553D"
SLATE = "#5C6B73"
LIGHT_BG = "#FFFFFF"
GRID = "#E2E8F0"
BORDER = "#CBD5E1"
TEXT = "#0F172A"
MUTED = "#475569"
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"


def _esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def _set_png_dpi_and_crop(png_path: Path, target_w: int, target_h: int, dpi: int = 300) -> None:
    """Crop qlmanage square padding to exact aspect ratio and embed 300 DPI pHYs chunk."""
    # Use sips to crop centered to exact target_w x target_h if qlmanage padded height/width
    subprocess.run(
        ["sips", "--cropToHeightWidth", str(target_h), str(target_w), str(png_path)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    # Inject exact pHYs chunk (pixels per meter = round(dpi / 0.0254))
    data = png_path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "Not a PNG"
    ppm = round(dpi / 0.0254)
    phys_payload = struct.pack(">IIB", ppm, ppm, 1)
    phys_crc = zlib.crc32(b"pHYs" + phys_payload) & 0xFFFFFFFF
    phys_chunk = struct.pack(">I", len(phys_payload)) + b"pHYs" + phys_payload + struct.pack(">I", phys_crc)

    out = bytearray(data[:8])
    pos = 8
    inserted = False
    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        ctype = data[pos + 4 : pos + 8]
        chunk_end = pos + 12 + length
        if ctype == b"pHYs":
            pos = chunk_end
            continue
        out.extend(data[pos:chunk_end])
        if ctype == b"IHDR" and not inserted:
            out.extend(phys_chunk)
            inserted = True
        pos = chunk_end
    png_path.write_bytes(bytes(out))


def render_svg_to_png(svg_text: str, out_png: Path, width: int, height: int) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    # Write clean aspect-correct standalone SVG as archival vector source
    svg_path = out_png.with_suffix(".svg")
    svg_path.write_text(svg_text, encoding="utf-8")
    # Wrap inside a square SxS viewport so macOS qlmanage renders at exact 1:1 scale
    # without cropping/zooming, then center-crop to exact width x height at 300 DPI.
    size = max(width, height)
    dx = (size - width) // 2
    dy = (size - height) // 2
    inner = svg_text.split(">", 1)[1].rsplit("</svg>", 1)[0]
    sq_svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'<rect width="{size}" height="{size}" fill="{LIGHT_BG}"/>'
        f'<g transform="translate({dx},{dy})">{inner}</g></svg>'
    )
    tmp_svg = FIG_DIR / f"_tmp_{out_png.stem}.svg"
    tmp_svg.write_text(sq_svg, encoding="utf-8")
    try:
        subprocess.run(
            ["qlmanage", "-t", "-s", str(size), "-o", str(FIG_DIR), str(tmp_svg)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        ql_png = FIG_DIR / f"{tmp_svg.name}.png"
        ql_png.replace(out_png)
        _set_png_dpi_and_crop(out_png, width, height, dpi=300)
    finally:
        if tmp_svg.exists():
            tmp_svg.unlink()


# =============================================================================
# FIGURE 1: Grammar Detection Confusion Matrices (Side-by-Side, n=320 External)
# =============================================================================
def make_fig1_confusion_matrix(comp: dict[str, Any]) -> None:
    W, H = 2400, 1260
    s320 = comp["section_511"]["overall"]["external_strict_uncontaminated_320"]
    m_rules = s320["rules_only"]["strict_ungrammatical"]
    m_hyb = s320["hybrid_rules_plus_cola"]["non_grammatical_flagged"]

    def draw_matrix(x0: int, y0: int, m: dict[str, Any], title: str, subtitle: str) -> str:
        tp, fn, fp, tn = m["tp"], m["fn"], m["fp"], m["tn"]
        gpos = tp + fn
        gneg = fp + tn
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
            # Column headers
            f'<text x="{x0 + cw // 2}" y="{y0 - 12}" text-anchor="middle" font-family="{FONT}" font-size="28" font-weight="600" fill="{TEXT}">Pred: Ungrammatical (+)</text>',
            f'<text x="{x0 + cw + cw // 2}" y="{y0 - 12}" text-anchor="middle" font-family="{FONT}" font-size="28" font-weight="600" fill="{TEXT}">Pred: Grammatical (−)</text>',
            # Row headers
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
        # Footer metrics summary
        acc = (m["accuracy"] or 0) * 100
        prec = (m["precision"] or 0) * 100
        rec = (m["recall"] or 0) * 100
        f1 = (m["f1"] or 0) * 100
        parts.append(
            f'<text x="{x0 + cw}" y="{y0 + 2 * ch + 60}" text-anchor="middle" font-family="{FONT}" font-size="27" font-weight="600" fill="{NAVY}">'
            f'Acc: {acc:.1f}%  |  Prec: {prec:.1f}%  |  Rec: {rec:.1f}%  |  F1: {f1:.1f}%</text>'
        )
        return "\n".join(parts)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="{LIGHT_BG}"/>
<text x="{W // 2}" y="76" text-anchor="middle" font-family="{FONT}" font-size="48" font-weight="800" fill="{NAVY}">Figure 1. SynTutor Grammar Error Detection Confusion Matrices</text>
<text x="{W // 2}" y="126" text-anchor="middle" font-family="{FONT}" font-size="29" fill="{MUTED}">Uncontaminated External Stratified Benchmark (BLiMP n = 240 + JFLEG n = 80; Total n = 320, Positive Class = Ungrammatical)</text>
<line x1="120" y1="156" x2="{W - 120}" y2="156" stroke="{BORDER}" stroke-width="2"/>
{draw_matrix(310, 340, m_rules, "A. Deterministic Rules-Only", "Strict rule-backed verdict (ungrammatical vs. other)")}
{draw_matrix(1460, 340, m_hyb, "B. Hybrid (Rules + RoBERTa-CoLA)", "Non-acceptance operating point (ungrammatical or unverified)")}
<text x="{W // 2}" y="{H - 46}" text-anchor="middle" font-family="{FONT}" font-size="24" fill="{MUTED}">Note: CoLA validation subset (n = 80) is excluded here to prevent overlap with the RoBERTa-CoLA hybrid detector and is reported separately.</text>
</svg>'''
    render_svg_to_png(svg, FIG_DIR / "fig1_confusion_matrix.png", W, H)


# =============================================================================
# FIGURE 2: Grammar Detection Performance (Grouped Bar Chart)
# =============================================================================
def make_fig2_detection_performance(comp: dict[str, Any]) -> None:
    W, H = 2400, 1440
    ov = comp["section_511"]["overall"]
    s320 = ov["external_strict_uncontaminated_320"]
    s_mp = ov["internal_minimal_pairs"]

    cov_dec = (s320["hybrid_rules_plus_cola"]["decisive_only"]["coverage"] or 0) * 100
    series = [
        ("External Uncontam. (n=320) — Rules-Only (Strict)", s320["rules_only"]["strict_ungrammatical"], NAVY),
        ("External Uncontam. (n=320) — Hybrid (Flagged)", s320["hybrid_rules_plus_cola"]["non_grammatical_flagged"], TEAL),
        (f"External Uncontam. (n=320) — Hybrid (Decisive, cov={cov_dec:.1f}%)", s320["hybrid_rules_plus_cola"]["decisive_only"], AMBER),
        ("Internal Minimal Pairs (n=52, AI-authored) — Rules-Only", s_mp["rules_only"]["strict_ungrammatical"], CORAL),
    ]
    metrics = [("accuracy", "Accuracy"), ("precision", "Precision"), ("recall", "Recall"), ("f1", "F1-Score"), ("specificity", "Specificity")]

    x0, y0, pw, ph = 200, 290, 2060, 820
    parts = []
    # Gridlines 0..100%
    for pct in range(0, 101, 20):
        gy = y0 + ph - int(ph * pct / 100)
        parts.append(f'<line x1="{x0}" y1="{gy}" x2="{x0 + pw}" y2="{gy}" stroke="{GRID}" stroke-width="2"/>')
        parts.append(f'<text x="{x0 - 22}" y="{gy + 10}" text-anchor="end" font-family="{FONT}" font-size="28" fill="{MUTED}">{pct}%</text>')
    parts.append(f'<line x1="{x0}" y1="{y0 + ph}" x2="{x0 + pw}" y2="{y0 + ph}" stroke="{TEXT}" stroke-width="3"/>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + ph}" stroke="{TEXT}" stroke-width="3"/>')

    gw = pw / len(metrics)
    bw = 74
    gap = 12
    total_bw = len(series) * bw + (len(series) - 1) * gap

    for gi, (mkey, mlabel) in enumerate(metrics):
        gx_center = x0 + gw * gi + gw / 2
        bx_start = gx_center - total_bw / 2
        parts.append(f'<text x="{gx_center:.1f}" y="{y0 + ph + 52}" text-anchor="middle" font-family="{FONT}" font-size="32" font-weight="700" fill="{TEXT}">{mlabel}</text>')
        for si, (_, mdict, col) in enumerate(series):
            val = (mdict.get(mkey) or 0.0) * 100.0
            bh = int(round(ph * val / 100.0))
            bx = bx_start + si * (bw + gap)
            by = y0 + ph - bh
            parts.append(f'<rect x="{bx:.1f}" y="{by}" width="{bw}" height="{bh}" rx="6" fill="{col}"/>')
            parts.append(f'<text x="{bx + bw / 2:.1f}" y="{by - 12}" text-anchor="middle" font-family="{FONT}" font-size="22" font-weight="700" fill="{TEXT}">{val:.1f}%</text>')

    # Legend (2x2)
    ly = y0 + ph + 115
    for si, (lbl, _, col) in enumerate(series):
        lx = x0 + (si % 2) * 1030
        ry = ly + (si // 2) * 52
        parts.append(f'<rect x="{lx}" y="{ry - 22}" width="32" height="28" rx="5" fill="{col}"/>')
        parts.append(f'<text x="{lx + 46}" y="{ry}" font-family="{FONT}" font-size="26" fill="{TEXT}">{_esc(lbl)}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="{LIGHT_BG}"/>
<text x="{W // 2}" y="76" text-anchor="middle" font-family="{FONT}" font-size="48" font-weight="800" fill="{NAVY}">Figure 2. Grammar Error Detection Performance Across Operating Modes</text>
<text x="{W // 2}" y="128" text-anchor="middle" font-family="{FONT}" font-size="29" fill="{MUTED}">Positive Class = Ungrammatical | External Stratified Subset (BLiMP n = 240 + JFLEG n = 80) vs. Internal Minimal Pairs (n = 52)</text>
<text x="64" y="{y0 + ph // 2}" text-anchor="middle" font-family="{FONT}" font-size="30" font-weight="700" fill="{TEXT}" transform="rotate(-90 64 {y0 + ph // 2})">Score (%)</text>
{"".join(parts)}
<text x="{W // 2}" y="{H - 36}" text-anchor="middle" font-family="{FONT}" font-size="23" fill="{MUTED}">Note: Internal minimal pairs are AI-authored diagnostic checks and are plotted separately from unseen external benchmarks.</text>
</svg>'''
    render_svg_to_png(svg, FIG_DIR / "fig2_grammar_detection_performance.png", W, H)


# =============================================================================
# FIGURE 3: Per-Category Detection F1 (Horizontal Grouped Bar Chart)
# =============================================================================
def make_fig3_per_category_f1(comp: dict[str, Any]) -> None:
    W, H = 2400, 1560
    bf = comp["section_511"]["blimp_by_family"]
    ov = comp["section_511"]["overall"]

    label_map = {
        "subject_verb_agreement": "Subject–Verb Agreement (BLiMP, n=30)",
        "determiner_agreement": "Determiner–Noun Agreement (BLiMP, n=30)",
        "verb_forms": "Irregular Verb Forms (BLiMP, n=30)",
        "pronoun_case_and_binding": "Pronoun Case & Binding (BLiMP, n=30)",
        "argument_structure": "Argument Structure (BLiMP, n=30)",
        "filler_gap_dependencies": "Filler–Gap Dependencies (BLiMP, n=30)",
        "island_effects": "Syntactic Island Effects (BLiMP, n=30)",
        "npi_licensing": "NPI Licensing (BLiMP, n=30)",
    }
    rows = []
    for k, lbl in label_map.items():
        if k in bf:
            rows.append((lbl, (bf[k]["rules_strict"]["f1"] or 0) * 100, (bf[k]["hybrid_flagged"]["f1"] or 0) * 100))
    rows.append((
        "JFLEG L2 Learner Writing (n=80)",
        (ov["jfleg_stratified"]["rules_only"]["strict_ungrammatical"]["f1"] or 0) * 100,
        (ov["jfleg_stratified"]["hybrid_rules_plus_cola"]["non_grammatical_flagged"]["f1"] or 0) * 100,
    ))
    rows.append((
        "CoLA Acceptability* (n=80, hybrid in-dist.)",
        (ov["cola_stratified"]["rules_only"]["strict_ungrammatical"]["f1"] or 0) * 100,
        (ov["cola_stratified"]["hybrid_rules_plus_cola"]["non_grammatical_flagged"]["f1"] or 0) * 100,
    ))

    x0, y0, pw, ph = 720, 230, 1500, 1080
    parts = []
    for pct in range(0, 101, 20):
        gx = x0 + int(pw * pct / 100)
        parts.append(f'<line x1="{gx}" y1="{y0}" x2="{gx}" y2="{y0 + ph}" stroke="{GRID}" stroke-width="2"/>')
        parts.append(f'<text x="{gx}" y="{y0 + ph + 42}" text-anchor="middle" font-family="{FONT}" font-size="27" fill="{MUTED}">{pct}%</text>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + ph}" stroke="{TEXT}" stroke-width="3"/>')
    parts.append(f'<line x1="{x0}" y1="{y0 + ph}" x2="{x0 + pw}" y2="{y0 + ph}" stroke="{TEXT}" stroke-width="3"/>')

    rh = ph / len(rows)
    bh = 32
    for i, (lbl, r_f1, h_f1) in enumerate(rows):
        yc = y0 + i * rh + rh / 2
        parts.append(f'<text x="{x0 - 24}" y="{yc + 9}" text-anchor="end" font-family="{FONT}" font-size="27" font-weight="600" fill="{TEXT}">{_esc(lbl)}</text>')
        rw = max(4, int(round(pw * r_f1 / 100)))
        hw = max(4, int(round(pw * h_f1 / 100)))
        parts.append(f'<rect x="{x0}" y="{yc - bh - 3:.1f}" width="{rw}" height="{bh}" rx="5" fill="{NAVY}"/>')
        parts.append(f'<text x="{x0 + rw + 14}" y="{yc - 9:.1f}" font-family="{FONT}" font-size="24" font-weight="700" fill="{NAVY}">{r_f1:.1f}%</text>')
        parts.append(f'<rect x="{x0}" y="{yc + 3:.1f}" width="{hw}" height="{bh}" rx="5" fill="{TEAL}"/>')
        parts.append(f'<text x="{x0 + hw + 14}" y="{yc + bh - 4:.1f}" font-family="{FONT}" font-size="24" font-weight="700" fill="{TEAL}">{h_f1:.1f}%</text>')

    # Legend
    ly = y0 + ph + 135
    parts.append(f'<rect x="720" y="{ly - 22}" width="34" height="28" rx="5" fill="{NAVY}"/>')
    parts.append(f'<text x="768" y="{ly}" font-family="{FONT}" font-size="27" font-weight="600" fill="{TEXT}">Deterministic Rules-Only F1 (Strict Rule-Flagged)</text>')
    parts.append(f'<rect x="1480" y="{ly - 22}" width="34" height="28" rx="5" fill="{TEAL}"/>')
    parts.append(f'<text x="1528" y="{ly}" font-family="{FONT}" font-size="27" font-weight="600" fill="{TEXT}">Hybrid Rules + CoLA F1 (Flagged)</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="{LIGHT_BG}"/>
<text x="{W // 2}" y="76" text-anchor="middle" font-family="{FONT}" font-size="48" font-weight="800" fill="{NAVY}">Figure 3. Per-Category Grammar Detection F1-Score</text>
<text x="{W // 2}" y="128" text-anchor="middle" font-family="{FONT}" font-size="28" fill="{MUTED}">Stratified External Benchmarks (BLiMP 8 Families n = 240, JFLEG n = 80, CoLA n = 80; Positive Class = Ungrammatical)</text>
<text x="{x0 + pw // 2}" y="{y0 + ph + 78}" text-anchor="middle" font-family="{FONT}" font-size="28" font-weight="700" fill="{TEXT}">F1-Score (%)</text>
{"".join(parts)}
<text x="{W // 2}" y="{H - 36}" text-anchor="middle" font-family="{FONT}" font-size="23" fill="{MUTED}">*CoLA validation sentences share domain/label distribution with textattack/roberta-base-CoLA; interpret hybrid CoLA F1 with caution.</text>
</svg>'''
    render_svg_to_png(svg, FIG_DIR / "fig3_per_category_f1.png", W, H)


# =============================================================================
# FIGURE 4: Syntax Tree Agreement (PARSEVAL on Published Burton-Roberts Trees)
# =============================================================================
def make_fig4_syntax_tree_agreement(comp: dict[str, Any]) -> None:
    W, H = 2400, 1460
    s512 = comp["section_512"]

    groups = [
        (f"All Ch1–Ch10\nFull PARSEVAL\n(n={s512['book_final_d1_bypass_full']['n_total']})", s512["book_final_d1_bypass_full"]),
        (f"All Ch1–Ch10\nTriangle-Aware\n(n={s512['book_final_d1_bypass_triangle_aware']['n_total']})", s512["book_final_d1_bypass_triangle_aware"]),
        (f"Non-Triangle\nFully Expanded\n(n={s512['book_final_d1_bypass_nontriangle_subset']['n_total']})", s512["book_final_d1_bypass_nontriangle_subset"]),
        (f"Late Ch7–Ch10\nTriangle-Aware\n(n={s512['book_ch7_to_ch10_triangle_aware']['n_total']})", s512["book_ch7_to_ch10_triangle_aware"]),
        (f"Ch2 V2-Shell\nLookup-Bypass\n(n={s512['book_ch2_v2_shell_bypass']['n_total']})", s512["book_ch2_v2_shell_bypass"]),
    ]
    bars = [
        ("labeled_f1", "Labeled Constituent F1", NAVY),
        ("unlabeled_f1", "Unlabeled Constituent F1", TEAL),
        ("exact_rate_over_aligned", "Exact-Tree Match (of Aligned)", AMBER),
        ("normalization_rate", "B-R Normalization Success Rate", SLATE),
    ]

    x0, y0, pw, ph = 200, 270, 2060, 800
    parts = []
    for pct in range(0, 101, 20):
        gy = y0 + ph - int(ph * pct / 100)
        parts.append(f'<line x1="{x0}" y1="{gy}" x2="{x0 + pw}" y2="{gy}" stroke="{GRID}" stroke-width="2"/>')
        parts.append(f'<text x="{x0 - 22}" y="{gy + 10}" text-anchor="end" font-family="{FONT}" font-size="28" fill="{MUTED}">{pct}%</text>')
    parts.append(f'<line x1="{x0}" y1="{y0 + ph}" x2="{x0 + pw}" y2="{y0 + ph}" stroke="{TEXT}" stroke-width="3"/>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + ph}" stroke="{TEXT}" stroke-width="3"/>')

    gw = pw / len(groups)
    bw = 70
    gap = 10
    tot_bw = len(bars) * bw + (len(bars) - 1) * gap

    for gi, (glabel, d) in enumerate(groups):
        xc = x0 + gi * gw + gw / 2
        bstart = xc - tot_bw / 2
        for li, line in enumerate(glabel.split("\n")):
            parts.append(f'<text x="{xc:.1f}" y="{y0 + ph + 44 + li * 34}" text-anchor="middle" font-family="{FONT}" font-size="26" font-weight="{"700" if li == 0 else "400"}" fill="{TEXT if li == 0 else MUTED}">{_esc(line)}</text>')
        for bi, (key, _, col) in enumerate(bars):
            val = (d.get(key) or 0.0) * 100.0
            bh = int(round(ph * val / 100.0))
            bx = bstart + bi * (bw + gap)
            by = y0 + ph - bh
            parts.append(f'<rect x="{bx:.1f}" y="{by}" width="{bw}" height="{bh}" rx="5" fill="{col}"/>')
            parts.append(f'<text x="{bx + bw / 2:.1f}" y="{by - 10}" text-anchor="middle" font-family="{FONT}" font-size="21" font-weight="700" fill="{TEXT}">{val:.1f}%</text>')

    ly = y0 + ph + 175
    for bi, (_, lbl, col) in enumerate(bars):
        lx = x0 + (bi % 2) * 1030
        ry = ly + (bi // 2) * 48
        parts.append(f'<rect x="{lx}" y="{ry - 22}" width="32" height="26" rx="5" fill="{col}"/>')
        parts.append(f'<text x="{lx + 46}" y="{ry}" font-family="{FONT}" font-size="27" fill="{TEXT}">{_esc(lbl)}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="{LIGHT_BG}"/>
<text x="{W // 2}" y="76" text-anchor="middle" font-family="{FONT}" font-size="48" font-weight="800" fill="{NAVY}">Figure 4. Syntax Tree Structural Agreement (Lookup-Bypassed PARSEVAL)</text>
<text x="{W // 2}" y="128" text-anchor="middle" font-family="{FONT}" font-size="28" fill="{MUTED}">SynTutor Benepar → B-R FINAL-D1 Projection Evaluated Against Published Burton–Roberts Textbook Trees (n = 216 Complete IMG Figures)</text>
<text x="64" y="{y0 + ph // 2}" text-anchor="middle" font-family="{FONT}" font-size="30" font-weight="700" fill="{TEXT}" transform="rotate(-90 64 {y0 + ph // 2})">Agreement / Rate (%)</text>
{"".join(parts)}
<text x="{W // 2}" y="{H - 36}" text-anchor="middle" font-family="{FONT}" font-size="23" fill="{MUTED}">Note: Exact-IMG lookup (EXACT_IMG_GOLD_REFERENCE) was bypassed for true generalization. External Penn Treebank gold is not installed locally (unmeasured).</text>
</svg>'''
    render_svg_to_png(svg, FIG_DIR / "fig4_syntax_tree_agreement.png", W, H)


# =============================================================================
# FIGURE 5: Explainability Automated Consistency & Grounding Evaluation
# =============================================================================
def make_fig5_explainability(comp: dict[str, Any]) -> None:
    W, H = 2400, 1460
    xs = comp["section_513"]["summary"]
    n_ok = xs["n_ok"]
    n_err = xs["sentences_with_error_explanations"]
    n_norm = xs["br_normalized_count"]
    n_corr = xs["corrections_generated"]
    n_nodes = xs["total_node_explanations_generated"]
    n_q = xs["root_question_count"]
    q_ok = n_q - xs["root_question_called_subordinate_count"]

    items = [
        ("Verdict ↔ Error-Detail Consistency", xs["verdict_evidence_consistent"], n_ok, NAVY),
        ("Display-Status Truth Gating", xs["display_status_truth_gating_ok"], n_ok, NAVY),
        ("Error Rule-ID & Text Grounding", xs["rule_grounded_all_count"], n_err, TEAL),
        ("Error Surface-Token Grounding", xs["surface_token_grounded_count"], n_err, TEAL),
        ("B-R Canonical Tree Schema Validity", xs["br_schema_valid_count"], n_norm, TEAL),
        ("Fact-Graph ↔ Tree Node Grounding", xs["fact_graph_tree_grounded_count"], n_norm, TEAL),
        ("Non-Empty Learner Node Prose", xs["total_node_explanations_nonempty"], n_nodes, TEAL),
        ("Correction Re-Parse Whole-Sentence Clean", xs["corrections_reparse_whole_clean"], n_corr, AMBER),
        ("Root Question Semantic Prose (No Subord. Bug)", q_ok, n_q, CORAL),
    ]

    x0, y0, pw, ph = 840, 240, 1210, 860
    parts = []
    for pct in range(0, 101, 20):
        gx = x0 + int(pw * pct / 100)
        parts.append(f'<line x1="{gx}" y1="{y0}" x2="{gx}" y2="{y0 + ph}" stroke="{GRID}" stroke-width="2"/>')
        parts.append(f'<text x="{gx}" y="{y0 + ph + 42}" text-anchor="middle" font-family="{FONT}" font-size="27" fill="{MUTED}">{pct}%</text>')
    parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + ph}" stroke="{TEXT}" stroke-width="3"/>')
    parts.append(f'<line x1="{x0}" y1="{y0 + ph}" x2="{x0 + pw}" y2="{y0 + ph}" stroke="{TEXT}" stroke-width="3"/>')

    rh = ph / len(items)
    bh = 48
    for i, (lbl, num, den, col) in enumerate(items):
        yc = y0 + i * rh + rh / 2
        pct = (num / den * 100.0) if den else 0.0
        bw = max(4, int(round(pw * pct / 100.0)))
        parts.append(f'<text x="{x0 - 24}" y="{yc + 9}" text-anchor="end" font-family="{FONT}" font-size="27" font-weight="600" fill="{TEXT}">{_esc(lbl)}</text>')
        parts.append(f'<rect x="{x0}" y="{yc - bh / 2:.1f}" width="{bw}" height="{bh}" rx="6" fill="{col}"/>')
        parts.append(f'<text x="{x0 + bw + 16}" y="{yc + 9}" font-family="{FONT}" font-size="25" font-weight="700" fill="{TEXT}">{pct:.1f}% ({num}/{den})</text>')

    # Transparent Callout Box: Human Evaluation NOT PLOTTED
    by = y0 + ph + 86
    parts.append(f'<rect x="160" y="{by}" width="{W - 320}" height="150" rx="12" fill="#FFF7ED" stroke="#F59E0B" stroke-width="3"/>')
    parts.append(f'<text x="200" y="{by + 48}" font-family="{FONT}" font-size="29" font-weight="800" fill="#92400E">Human-Rated Explanation Quality &amp; Clarity Distribution — NOT PLOTTED (UNMEASURED)</text>')
    parts.append(f'<text x="200" y="{by + 92}" font-family="{FONT}" font-size="25" fill="#78350F">Zero completed independent human reviewer assessments exist in the repository. Automated consistency checks verify</text>')
    parts.append(f'<text x="200" y="{by + 126}" font-family="{FONT}" font-size="25" fill="#78350F">structural and rule-grounding fidelity only; a 59-case HUMAN_REVIEW_WORKSHEET.csv has been generated for dual-rater scoring.</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="{LIGHT_BG}"/>
<text x="{W // 2}" y="76" text-anchor="middle" font-family="{FONT}" font-size="48" font-weight="800" fill="{NAVY}">Figure 5. Automated Explainability &amp; Evidence-Grounding Consistency</text>
<text x="{W // 2}" y="128" text-anchor="middle" font-family="{FONT}" font-size="28" fill="{MUTED}">Full api.build_payload() Execution Audit (n = {n_ok} Stratified Sentences: 60 External + 36 Internal Minimal Pairs + 24 Audit Cases)</text>
{"".join(parts)}
</svg>'''
    render_svg_to_png(svg, FIG_DIR / "fig5_explainability_evaluation.png", W, H)


def main() -> int:
    comp = json.loads((DIR / "_computed_results.json").read_text(encoding="utf-8"))
    make_fig1_confusion_matrix(comp)
    make_fig2_detection_performance(comp)
    make_fig3_per_category_f1(comp)
    make_fig4_syntax_tree_agreement(comp)
    make_fig5_explainability(comp)
    print(f"Generated 5 publication-quality 300 DPI PNG figures in {FIG_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
