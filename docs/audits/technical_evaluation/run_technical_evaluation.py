#!/usr/bin/env python3
"""Fast-Track Reproducible Technical Evaluation Harness for SynTutor (Sections 5.1.1-5.1.3).

Single-process execution with 1-time model loading (avoids macOS OpenMP
oversubscription) and deterministic stratified external sampling + full census
of all 216 published Burton-Roberts textbook IMG trees.

Produces under docs/audits/technical_evaluation/:
  - RAW_PREDICTIONS.csv
  - METRICS_SUMMARY.csv
  - HUMAN_REVIEW_WORKSHEET.csv
  - _computed_results.json
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = Path(__file__).resolve().parent
SERVER_DIR = ROOT / "server"
sys.path.insert(0, str(SERVER_DIR))

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

BLIMP_FAMILY_MAP = {
    "regular_plural_subject_verb_agreement_1": "subject_verb_agreement",
    "regular_plural_subject_verb_agreement_2": "subject_verb_agreement",
    "irregular_plural_subject_verb_agreement_1": "subject_verb_agreement",
    "irregular_plural_subject_verb_agreement_2": "subject_verb_agreement",
    "distractor_agreement_relational_noun": "subject_verb_agreement",
    "distractor_agreement_relative_clause": "subject_verb_agreement",
    "determiner_noun_agreement_1": "determiner_agreement",
    "determiner_noun_agreement_2": "determiner_agreement",
    "determiner_noun_agreement_irregular_1": "determiner_agreement",
    "determiner_noun_agreement_irregular_2": "determiner_agreement",
    "determiner_noun_agreement_with_adjective_1": "determiner_agreement",
    "determiner_noun_agreement_with_adj_2": "determiner_agreement",
    "determiner_noun_agreement_with_adj_irregular_1": "determiner_agreement",
    "determiner_noun_agreement_with_adj_irregular_2": "determiner_agreement",
    "irregular_past_participle_verbs": "verb_forms",
    "irregular_past_participle_adjectives": "verb_forms",
    "principle_A_case_1": "pronoun_case_and_binding",
    "principle_A_case_2": "pronoun_case_and_binding",
    "anaphor_gender_agreement": "pronoun_case_and_binding",
    "anaphor_number_agreement": "pronoun_case_and_binding",
    "principle_A_c_command": "pronoun_case_and_binding",
    "principle_A_domain_1": "pronoun_case_and_binding",
    "principle_A_domain_2": "pronoun_case_and_binding",
    "principle_A_domain_3": "pronoun_case_and_binding",
    "principle_A_reconstruction": "pronoun_case_and_binding",
    "animate_subject_passive": "argument_structure",
    "animate_subject_trans": "argument_structure",
    "causative": "argument_structure",
    "drop_argument": "argument_structure",
    "inchoative": "argument_structure",
    "intransitive": "argument_structure",
    "passive_1": "argument_structure",
    "passive_2": "argument_structure",
    "transitive": "argument_structure",
    "wh_questions_object_gap": "filler_gap_dependencies",
    "wh_questions_subject_gap": "filler_gap_dependencies",
    "wh_questions_subject_gap_long_distance": "filler_gap_dependencies",
    "wh_vs_that_no_gap": "filler_gap_dependencies",
    "wh_vs_that_no_gap_long_distance": "filler_gap_dependencies",
    "wh_vs_that_with_gap": "filler_gap_dependencies",
    "wh_vs_that_with_gap_long_distance": "filler_gap_dependencies",
    "adjunct_island": "island_effects",
    "complex_NP_island": "island_effects",
    "coordinate_structure_constraint_complex_left_branch": "island_effects",
    "coordinate_structure_constraint_object_extraction": "island_effects",
    "left_branch_island_echo_question": "island_effects",
    "left_branch_island_simple_question": "island_effects",
    "sentential_subject_island": "island_effects",
    "wh_island": "island_effects",
    "matrix_question_npi_licensor_present": "npi_licensing",
    "npi_present_1": "npi_licensing",
    "npi_present_2": "npi_licensing",
    "only_npi_licensor_present": "npi_licensing",
    "only_npi_scope": "npi_licensing",
    "sentential_negation_npi_licensor_present": "npi_licensing",
    "sentential_negation_npi_scope": "npi_licensing",
    "existential_there_quantifiers_1": "quantifiers_and_raising",
    "existential_there_quantifiers_2": "quantifiers_and_raising",
    "existential_there_object_raising": "quantifiers_and_raising",
    "existential_there_subject_raising": "quantifiers_and_raising",
    "expletive_it_object_raising": "quantifiers_and_raising",
    "superlative_quantifiers_1": "quantifiers_and_raising",
    "superlative_quantifiers_2": "quantifiers_and_raising",
    "tough_vs_raising_1": "quantifiers_and_raising",
    "tough_vs_raising_2": "quantifiers_and_raising",
    "ellipsis_n_bar_1": "ellipsis",
    "ellipsis_n_bar_2": "ellipsis",
}

RAPID_AUDIT_SENTENCES = [
    ("Intransitive", "The birds sing.", "grammatical"),
    ("Transitive", "Nora inspected the bridge.", "grammatical"),
    ("AP/degree", "The children seemed very cheerful.", "grammatical"),
    ("Adjunct", "Nora inspected the bridge yesterday.", "grammatical"),
    ("Double object", "They gave me the key.", "grammatical"),
    ("PP complement", "They gave the key to me.", "grammatical"),
    ("Perfect/progressive", "The researchers have been examining the evidence.", "grammatical"),
    ("Passive", "The letter was read by Mara.", "grammatical"),
    ("Modal", "She can go.", "grammatical"),
    ("Extra infinitival marker", "She can to go.", "ungrammatical"),
    ("Agreement error", "The boy go to school.", "ungrammatical"),
    ("Perfect form error", "She has went home.", "ungrammatical"),
    ("Wh-question", "What did Jon buy?", "grammatical"),
    ("Yes/no question", "Did Jon buy the book?", "grammatical"),
    ("Relative", "The book that she wrote is popular.", "grammatical"),
    ("Embedded content", "She said that Jon left.", "grammatical"),
    ("Nonfinite control", "She persuaded Mara to leave.", "grammatical"),
    ("VP coordination", "She sings and dances.", "grammatical"),
    ("Comparative", "She is taller than he is.", "grammatical"),
    ("Clausal PP complement", "I saw him before he left.", "grammatical"),
    ("Informal predicative case", "It’s me.", "grammatical"),
    ("Notional agreement", "Three eggs is plenty.", "grammatical"),
    ("Negation", "She did not leave.", "grammatical"),
    ("Imperative", "Close the door.", "grammatical"),
]

JARGON_TERMS = (
    "b-r", "canonical", "constraint", "xai", "matrix", "phrase marker",
    "constituent", "projection", "rule id", "parsed", "token",
    "node", "benepar", "spacy", "cgel", "cambridge grammar checks",
)
ACTION_VERBS = (
    "write", "change", "remove", "use", "add", "move", "drop", "replace",
    "delete", "correct", "say", "put", "insert", "capitalize", "hyphenate",
)
INTERNAL_ID_RE = re.compile(r"\b(sg-root|n\d+:|C-[A-Z][A-Z-]{2,})\b")
_PUNCT_RE = re.compile(r"^[^\w]+$")


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z'’-]*", text or "")


def _syllables(word: str) -> int:
    groups = re.findall(r"[aeiouy]+", word.lower())
    count = len(groups)
    if word.lower().endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def _flesch(text: str) -> float | None:
    ws = _words(text)
    if not ws:
        return None
    sents = max(1, len(re.findall(r"[.!?]", text or "")))
    syl = sum(_syllables(w) for w in ws)
    return round(206.835 - 1.015 * (len(ws) / sents) - 84.6 * (syl / len(ws)), 1)


def _hygiene_flags(text: str, status: str | None = None) -> list[str]:
    low = (text or "").lower()
    flags = []
    if not low.strip():
        return ["empty"]
    if any(t in low for t in JARGON_TERMS):
        flags.append("jargon")
    if len(_words(text)) > 55:
        flags.append("too-long")
    if status in {"error", "suggestion"} and not any(v in low for v in ACTION_VERBS):
        flags.append("not-actionable")
    if INTERNAL_ID_RE.search(text or ""):
        flags.append("internal-id")
    return flags


def load_stratified_datasets() -> list[dict[str, Any]]:
    """Load deterministic stratified external subsets (n=400) + internal diagnostics (n=76)."""
    records: list[dict[str, Any]] = []

    # 1. BLiMP stratified subset: 8 core grammatical families x 15 pairs = 240 sentences (from 2,010)
    blimp_pairs_by_fam: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    with open(ROOT / "benchmarks/blimp.tsv", encoding="utf-8") as fh:
        r = csv.reader(fh, delimiter="\t")
        next(r)
        rows = [row for row in r if len(row) >= 3 and not row[0].startswith("#")]
    i = 0
    while i + 1 < len(rows):
        c1, l1, s1 = rows[i][0].strip(), rows[i][1].strip(), rows[i][2].strip()
        c2, l2, s2 = rows[i + 1][0].strip(), rows[i + 1][1].strip(), rows[i + 1][2].strip()
        if c1 == c2 and {l1, l2} == {"good", "bad"}:
            good_s = s1 if l1 == "good" else s2
            bad_s = s2 if l1 == "good" else s1
            fam = BLIMP_FAMILY_MAP.get(c1, "other_blimp")
            blimp_pairs_by_fam[fam].append((c1, good_s, bad_s))
            i += 2
        else:
            i += 1

    target_families = [
        "subject_verb_agreement",
        "determiner_agreement",
        "verb_forms",
        "pronoun_case_and_binding",
        "argument_structure",
        "filler_gap_dependencies",
        "island_effects",
        "npi_licensing",
    ]
    b_idx = 0
    for fam in target_families:
        pool = blimp_pairs_by_fam[fam]
        # Deterministic strided selection of 15 pairs (30 sentences) spanning all sub-paradigms
        n_pick = 15
        picked = [pool[int(k * len(pool) / n_pick)] for k in range(n_pick)]
        for cat, good_s, bad_s in picked:
            b_idx += 1
            records.append({
                "item_id": f"blimp-{b_idx:03d}-g",
                "dataset": "blimp_stratified",
                "split_type": "external_independent_stratified_subset",
                "category": cat,
                "error_family": fam,
                "gold_label": "grammatical",
                "sentence": good_s,
                "reference_correction": "",
                "provenance": "nyu-mll/blimp (Warstadt et al., 2020); stratified 240/2010 subset",
            })
            records.append({
                "item_id": f"blimp-{b_idx:03d}-u",
                "dataset": "blimp_stratified",
                "split_type": "external_independent_stratified_subset",
                "category": cat,
                "error_family": fam,
                "gold_label": "ungrammatical",
                "sentence": bad_s,
                "reference_correction": good_s,
                "provenance": "nyu-mll/blimp (Warstadt et al., 2020); stratified 240/2010 subset",
            })

    # 2. JFLEG stratified subset: 40 pairs = 80 sentences (40 L2 bad / 40 human-corrected good; from 400)
    with open(ROOT / "benchmarks/jfleg.tsv", encoding="utf-8") as fh:
        r = csv.reader(fh, delimiter="\t")
        next(r)
        jrows = [row for row in r if len(row) >= 3 and not row[0].startswith("#")]
    jpairs = []
    for k in range(0, len(jrows) - 1, 2):
        if jrows[k][1].strip() == "bad" and jrows[k + 1][1].strip() == "good":
            jpairs.append((jrows[k][2].strip(), jrows[k + 1][2].strip()))
    for idx in range(40):
        bad_s, good_s = jpairs[int(idx * len(jpairs) / 40)]
        records.append({
            "item_id": f"jfleg-{idx + 1:03d}-u",
            "dataset": "jfleg_stratified",
            "split_type": "external_independent_stratified_subset",
            "category": "jfleg_l2_learner",
            "error_family": "l2_learner_writing",
            "gold_label": "ungrammatical",
            "sentence": bad_s,
            "reference_correction": good_s,
            "provenance": "jhu-clsp/jfleg validation (Napoles et al., 2017); stratified 80/400 subset",
        })
        records.append({
            "item_id": f"jfleg-{idx + 1:03d}-g",
            "dataset": "jfleg_stratified",
            "split_type": "external_independent_stratified_subset",
            "category": "jfleg_l2_learner",
            "error_family": "l2_learner_writing",
            "gold_label": "grammatical",
            "sentence": good_s,
            "reference_correction": "",
            "provenance": "jhu-clsp/jfleg validation (Napoles et al., 2017); stratified 80/400 subset",
        })

    # 3. CoLA stratified subset: 40 good + 40 bad = 80 sentences (from 400; flagged for hybrid overlap!)
    with open(ROOT / "benchmarks/cola.tsv", encoding="utf-8") as fh:
        r = csv.reader(fh, delimiter="\t")
        next(r)
        crows = [row for row in r if len(row) >= 3 and not row[0].startswith("#")]
    c_good = [row[2].strip() for row in crows if row[1].strip() == "good"]
    c_bad = [row[2].strip() for row in crows if row[1].strip() == "bad"]
    for idx in range(40):
        records.append({
            "item_id": f"cola-{idx + 1:03d}-g",
            "dataset": "cola_stratified",
            "split_type": "external_independent_cola_overlap_caveat",
            "category": "cola_acceptability",
            "error_family": "cola_general_acceptability",
            "gold_label": "grammatical",
            "sentence": c_good[int(idx * len(c_good) / 40)],
            "reference_correction": "",
            "provenance": "nyu-mll/glue cola validation (Warstadt et al., 2019); stratified 80/400 subset; hybrid CoLA caveat",
        })
        records.append({
            "item_id": f"cola-{idx + 1:03d}-u",
            "dataset": "cola_stratified",
            "split_type": "external_independent_cola_overlap_caveat",
            "category": "cola_acceptability",
            "error_family": "cola_general_acceptability",
            "gold_label": "ungrammatical",
            "sentence": c_bad[int(idx * len(c_bad) / 40)],
            "reference_correction": "",
            "provenance": "nyu-mll/glue cola validation (Warstadt et al., 2019); stratified 80/400 subset; hybrid CoLA caveat",
        })

    # 4. Internal minimal pairs: ALL 26 pairs = 52 items (evaluation/minimal_pairs.json)
    mp = json.loads((ROOT / "evaluation/minimal_pairs.json").read_text(encoding="utf-8"))
    for idx, p in enumerate(mp, 1):
        records.append({
            "item_id": f"int-mp-{idx:03d}-g",
            "dataset": "internal_minimal_pairs",
            "split_type": "internal_repository_ai_authored",
            "category": p.get("rule_id", ""),
            "error_family": p.get("domain", "other"),
            "gold_label": "grammatical",
            "sentence": p["grammatical"],
            "reference_correction": "",
            "provenance": "evaluation/minimal_pairs.json (full census 52/52; repository ai_authored)",
        })
        records.append({
            "item_id": f"int-mp-{idx:03d}-u",
            "dataset": "internal_minimal_pairs",
            "split_type": "internal_repository_ai_authored",
            "category": p.get("rule_id", ""),
            "error_family": p.get("domain", "other"),
            "gold_label": "ungrammatical",
            "sentence": p["ungrammatical"],
            "reference_correction": p["grammatical"],
            "provenance": "evaluation/minimal_pairs.json (full census 52/52; repository ai_authored)",
        })

    # 5. Internal rapid consistency audit: ALL 24 representative & Cambridge lesson sentences
    for idx, (cat, sent, gold) in enumerate(RAPID_AUDIT_SENTENCES, 1):
        records.append({
            "item_id": f"audit24-{idx:02d}",
            "dataset": "internal_rapid_audit_24",
            "split_type": "internal_regression_audit",
            "category": cat,
            "error_family": cat.lower().replace(" ", "_").replace("/", "_"),
            "gold_label": gold,
            "sentence": sent,
            "reference_correction": "",
            "provenance": "docs/audits/RAPID_CROSS_COMPONENT_CONSISTENCY_AUDIT.md (full census 24/24)",
        })

    return records


def compute_binary_metrics(rows: list[dict[str, Any]], vfield: str, op: str) -> dict[str, Any]:
    n_total = len(rows)
    n_err = n_unv_p = n_unv_n = n_gp = n_gn = 0
    tp = tn = fp = fn = 0
    for r in rows:
        gp = (r["gold_label"] == "ungrammatical")
        if gp:
            n_gp += 1
        else:
            n_gn += 1
        v = r[vfield]
        if v == "execution_error" or r["execution_status"] != "ok":
            n_err += 1
            continue
        if v == "unverified":
            if gp:
                n_unv_p += 1
            else:
                n_unv_n += 1
            if op == "decisive_only":
                continue
        if op in {"decisive_only", "strict_ungrammatical"}:
            pp = (v == "ungrammatical")
        elif op == "non_grammatical_flagged":
            pp = (v in {"ungrammatical", "unverified"})
        else:
            raise ValueError(op)
        if gp and pp:
            tp += 1
        elif (not gp) and (not pp):
            tn += 1
        elif (not gp) and pp:
            fp += 1
        else:
            fn += 1

    ev = tp + tn + fp + fn
    cov = ev / n_total if n_total else 0.0
    acc = (tp + tn) / ev if ev else None
    prec = tp / (tp + fp) if (tp + fp) else None
    rec = tp / (tp + fn) if (tp + fn) else None
    f1 = (2 * prec * rec / (prec + rec)) if (prec is not None and rec is not None and (prec + rec) > 0) else (0.0 if ev else None)
    spec = tn / (tn + fp) if (tn + fp) else None

    def _r(x):
        return round(x, 4) if x is not None else None

    return {
        "n_total": n_total,
        "n_gold_ungrammatical": n_gp,
        "n_gold_grammatical": n_gn,
        "n_evaluated": ev,
        "n_unverified_total": n_unv_p + n_unv_n,
        "n_unverified_gold_ungrammatical": n_unv_p,
        "n_unverified_gold_grammatical": n_unv_n,
        "n_execution_error": n_err,
        "coverage": _r(cov),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": _r(acc),
        "precision": _r(prec),
        "recall": _r(rec),
        "f1": _r(f1),
        "specificity": _r(spec),
    }


# --- PARSEVAL scorer (Section 5.1.2) ---
PRETERM_LABELS = {
    "N", "V", "V(I)", "V(II)", "A", "Adv", "P", "ART", "DEM", "Q", "POSS",
    "PRE-DET", "DEG", "Prt", "C", "C1", "C2", "MOD", "PERF", "PROG", "PASS",
    "TENSE", "AUX", "V-part", "QA", "name", "pronoun", "DET",
}


def _norm_label(n: dict[str, Any]) -> str:
    lbl = str(n.get("label") or "")
    if lbl == "Sentence":
        lbl = "S"
    vt = n.get("verb_type")
    if lbl == "V" and vt in {"I", "II"}:
        lbl = f"V({vt})"
    return lbl


def _extract_spans(root: dict[str, Any]) -> tuple[list[str], list[tuple[int, int, str]], list[tuple[int, int]]]:
    words: list[str] = []
    spans: list[tuple[int, int, str]] = []
    mw_tris: list[tuple[int, int]] = []

    def is_empty(n: dict[str, Any]) -> bool:
        if n.get("empty") or n.get("elided") or n.get("gap") or n.get("symbol") == "E":
            return True
        return not n.get("children") and "word" not in n and "words" not in n

    def walk(n: dict[str, Any]) -> tuple[int, int]:
        if not isinstance(n, dict) or is_empty(n):
            p = len(words)
            return p, p
        if "word" in n and not n.get("children") and not n.get("label"):
            w = str(n["word"]).strip()
            if w and not _PUNCT_RE.match(w):
                s = len(words)
                words.append(w.casefold())
                return s, len(words)
            p = len(words)
            return p, p
        if n.get("triangle") or ("words" in n and not n.get("children")):
            raw_ws = n.get("words") or ([n["word"]] if "word" in n else [])
            s = len(words)
            for rw in raw_ws:
                for tok in re.findall(r"\w+(?:['’]\w+)*", str(rw)):
                    words.append(tok.casefold())
            e = len(words)
            lbl = _norm_label(n)
            if e > s and lbl:
                spans.append((s, e, lbl))
                if e - s >= 2:
                    mw_tris.append((s, e))
            return s, e
        if "word" in n and not n.get("children") and n.get("label"):
            s = len(words)
            for tok in re.findall(r"\w+(?:['’]\w+)*", str(n["word"])):
                words.append(tok.casefold())
            e = len(words)
            lbl = _norm_label(n)
            if e > s and lbl and lbl not in PRETERM_LABELS:
                spans.append((s, e, lbl))
            return s, e
        children = n.get("children") or []
        ranges = [walk(c) for c in children]
        non_empty = [(s, e) for s, e in ranges if e > s]
        if not non_empty:
            p = len(words)
            return p, p
        s, e = non_empty[0][0], non_empty[-1][1]
        lbl = _norm_label(n)
        is_direct_preterm = (
            lbl in PRETERM_LABELS
            and all(isinstance(c, dict) and ("word" in c) and not c.get("children") and not c.get("label") for c in children)
        )
        if lbl and not is_direct_preterm:
            spans.append((s, e, lbl))
        return s, e

    walk(root)
    return words, spans, mw_tris


def _mask_inside_triangles(spans: list[tuple[int, int, str]], tris: list[tuple[int, int]]) -> list[tuple[int, int, str]]:
    if not tris:
        return list(spans)
    return [
        (s, e, lbl) for s, e, lbl in spans
        if not any((ts <= s and e <= te) and not (s == ts and e == te) for ts, te in tris)
    ]


def score_parseval_pair(gold_root: dict[str, Any], pred_root: dict[str, Any], triangle_aware: bool = False) -> dict[str, Any]:
    gw, gs, gtris = _extract_spans(gold_root)
    pw, ps, _ = _extract_spans(pred_root)
    if gw != pw:
        return {
            "yield_match": False, "gold_count": len(gs), "pred_count": len(ps),
            "labeled_match": 0, "unlabeled_match": 0, "exact_match": False,
            "has_multiword_triangle": bool(gtris), "label_errors": 0,
            "boundary_only_pred": 0, "boundary_only_gold": 0, "extra_nom_or_bar": 0,
        }
    pe = _mask_inside_triangles(ps, gtris) if triangle_aware else ps
    gc, pc = Counter(gs), Counter(pe)
    lm = sum((gc & pc).values())
    gu, pu = Counter((s, e) for s, e, _ in gs), Counter((s, e) for s, e, _ in pe)
    um = sum((gu & pu).values())
    gs_set, ps_set = set(gu.keys()), set(pu.keys())
    return {
        "yield_match": True,
        "gold_count": sum(gc.values()),
        "pred_count": sum(pc.values()),
        "labeled_match": lm,
        "unlabeled_match": um,
        "exact_match": (gc == pc),
        "has_multiword_triangle": bool(gtris),
        "label_errors": max(0, um - lm),
        "boundary_only_pred": sum(c for (s, e), c in pu.items() if (s, e) not in gs_set),
        "boundary_only_gold": sum(c for (s, e), c in gu.items() if (s, e) not in ps_set),
        "extra_nom_or_bar": sum(c for (_, _, lbl), c in (pc - gc).items() if lbl in {"NOM", "S-bar", "S-dbar"}),
        "gold_only_spans": list((gc - pc).elements())[:8],
        "pred_only_spans": list((pc - gc).elements())[:8],
    }


def aggregate_parseval(scored: list[dict[str, Any]]) -> dict[str, Any]:
    n_tot = len(scored)
    aligned = [x for x in scored if x.get("normalized") and x.get("yield_match")]
    n_norm = sum(1 for x in scored if x.get("normalized"))
    n_work = sum(1 for x in scored if (not x.get("normalized")) and x.get("working_tree"))
    n_unres = n_tot - n_norm
    n_al = len(aligned)
    gt = sum(x["gold_count"] for x in aligned)
    pt = sum(x["pred_count"] for x in aligned)
    lm = sum(x["labeled_match"] for x in aligned)
    um = sum(x["unlabeled_match"] for x in aligned)
    ex = sum(1 for x in aligned if x["exact_match"])
    lp = lm / pt if pt else None
    lr = lm / gt if gt else None
    lf1 = (2 * lp * lr / (lp + lr)) if (lp and lr and (lp + lr) > 0) else (0.0 if n_al else None)
    up = um / pt if pt else None
    ur = um / gt if gt else None
    uf1 = (2 * up * ur / (up + ur)) if (up and ur and (up + ur) > 0) else (0.0 if n_al else None)
    _r = lambda v: round(v, 4) if v is not None else None
    return {
        "n_total": n_tot,
        "n_normalized": n_norm,
        "normalization_rate": _r(n_norm / n_tot if n_tot else None),
        "n_working_fallback": n_work,
        "n_unresolved": n_unres,
        "n_yield_aligned": n_al,
        "gold_constituents": gt,
        "pred_constituents": pt,
        "labeled_matches": lm,
        "unlabeled_matches": um,
        "labeled_precision": _r(lp),
        "labeled_recall": _r(lr),
        "labeled_f1": _r(lf1),
        "unlabeled_precision": _r(up),
        "unlabeled_recall": _r(ur),
        "unlabeled_f1": _r(uf1),
        "exact_matches": ex,
        "exact_rate_over_aligned": _r(ex / n_al if n_al else None),
        "exact_rate_over_total": _r(ex / n_tot if n_tot else None),
        "total_label_errors": sum(x.get("label_errors", 0) for x in aligned),
        "total_boundary_only_pred": sum(x.get("boundary_only_pred", 0) for x in aligned),
        "total_boundary_only_gold": sum(x.get("boundary_only_gold", 0) for x in aligned),
        "total_extra_nom_or_bar": sum(x.get("extra_nom_or_bar", 0) for x in aligned),
    }


def main() -> int:
    t0 = time.perf_counter()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    import parse_engine
    import matrix
    import detector
    import burton_roberts as br
    import cambridge_registry
    import cambridge_evaluator
    import api
    from br_tree import _atoms, _source_yield
    from learner_explanations import compose_learner_explanation
    from jsonschema import Draft202012Validator

    print("[eval] Loading spaCy + Benepar + RoBERTa-CoLA once...", flush=True)
    parse_engine.load_models()
    detector.load_detector()
    cam_rt = cambridge_registry.load_runtime_registry()
    schema_val = Draft202012Validator(
        json.loads((ROOT / "docs/canonical-burton-roberts-tree.schema.json").read_text(encoding="utf-8"))
    )
    print(f"[eval] Models loaded in {time.perf_counter() - t0:.2f}s", flush=True)

    # =========================================================================
    # SECTION 5.1.1 — Grammar Error Detection (476 stratified + internal items)
    # =========================================================================
    records = load_stratified_datasets()
    reuse_raw = "--reuse-raw" in sys.argv and (OUT_DIR / "RAW_PREDICTIONS.csv").exists()
    if reuse_raw:
        print("[5.1.1] Reusing completed RAW_PREDICTIONS.csv (476 rows)...", flush=True)
        det_results = []
        with open(OUT_DIR / "RAW_PREDICTIONS.csv", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                r["parse_ok"] = r["parse_ok"] == "True"
                r["hybrid_flagged"] = r["hybrid_flagged"] == "True"
                r["cola_available"] = r["cola_available"] == "True"
                r["br_has_working_tree"] = r["br_has_working_tree"] == "True"
                r["br_schema_valid"] = r["br_schema_valid"] == "True"
                r["token_count"] = int(r["token_count"] or 0)
                r["error_count"] = int(r["error_count"] or 0)
                r["cambridge_findings_count"] = int(r["cambridge_findings_count"] or 0)
                det_results.append(r)
        assert len(det_results) == len(records), f"Row count mismatch: {len(det_results)} vs {len(records)}"
    else:
        print(f"[5.1.1] Running {len(records)} sentences (400 external stratified + 76 internal)...", flush=True)
        t1 = time.perf_counter()

        # Batch CoLA detector calls for huge speedup (32 sentences/batch)
        sentences_all = [r["sentence"] for r in records]
        cola_all: list[dict[str, Any] | None] = []
        for start in range(0, len(sentences_all), 32):
            batch = sentences_all[start : start + 32]
            cola_all.extend(detector.classify_many(batch))
        print(f"[5.1.1] Batched RoBERTa-CoLA complete in {time.perf_counter() - t1:.1f}s", flush=True)

        det_results = []
        for idx, (item, det) in enumerate(zip(records, cola_all), 1):
            ts = time.perf_counter()
            row = dict(item)
            try:
                analysis = parse_engine.analyze(item["sentence"])
                mat = matrix.evaluate(analysis["root"], text=analysis["sentence"])
                summary = mat["summary"]
                details = mat["details"]
                rules_verdict = summary.get("verdict", "unverified")
                err_constraints = sorted({
                    str(d.get("constraint") or d.get("rule_id") or "")
                    for d in details.values()
                    if isinstance(d, dict) and d.get("status") == "error"
                    and (d.get("constraint") or d.get("rule_id"))
                })
                err_count = sum(1 for d in details.values() if isinstance(d, dict) and d.get("status") == "error")

                if det is not None:
                    comb = detector.combine(summary, det)
                    hybrid_verdict = comb.get("verdict", rules_verdict)
                    hybrid_flagged = bool(comb.get("flagged", hybrid_verdict != "grammatical"))
                    cola_avail = bool(det.get("available"))
                    cola_lbl = det.get("label", "")
                    cola_prob = det.get("acceptable_prob", "")
                else:
                    hybrid_verdict = rules_verdict
                    hybrid_flagged = rules_verdict != "grammatical"
                    cola_avail = False
                    cola_lbl = ""
                    cola_prob = ""

                br_an = br.build_canonical_analysis(analysis)
                br_st = br_an.get("status", "unresolved")
                br_work = bool(br_an.get("working_tree"))
                br_sv = (br_st == "normalized" and isinstance(br_an.get("tree"), dict) and not any(schema_val.iter_errors(br_an["tree"])))
                cam = cambridge_evaluator.evaluate_cambridge(br_an, cam_rt, variety="standard_english")
                cam_f = cam.get("findings") or []

                row.update({
                    "execution_status": "ok",
                    "error_message": "",
                    "parse_ok": True,
                    "token_count": len(analysis.get("tokens") or []),
                    "rules_verdict": rules_verdict,
                    "hybrid_verdict": hybrid_verdict,
                    "hybrid_flagged": hybrid_flagged,
                    "cola_available": cola_avail,
                    "cola_label": cola_lbl,
                    "cola_acceptable_prob": cola_prob,
                    "error_count": err_count,
                    "constraints_fired": ";".join(err_constraints),
                    "cambridge_findings_count": len(cam_f),
                    "cambridge_rule_ids": ";".join(sorted({str(f.get("rule_id", "")) for f in cam_f if f.get("rule_id")})),
                    "br_status": br_st,
                    "br_has_working_tree": br_work,
                    "br_schema_valid": br_sv,
                    "elapsed_ms": round((time.perf_counter() - ts) * 1000.0, 2),
                })
            except Exception as exc:
                row.update({
                    "execution_status": "parse_error",
                    "error_message": f"{type(exc).__name__}: {exc}",
                    "parse_ok": False,
                    "token_count": 0,
                    "rules_verdict": "execution_error",
                    "hybrid_verdict": "execution_error",
                    "hybrid_flagged": False,
                    "cola_available": False,
                    "cola_label": "",
                    "cola_acceptable_prob": "",
                    "error_count": 0,
                    "constraints_fired": "",
                    "cambridge_findings_count": 0,
                    "cambridge_rule_ids": "",
                    "br_status": "execution_error",
                    "br_has_working_tree": False,
                    "br_schema_valid": False,
                    "elapsed_ms": round((time.perf_counter() - ts) * 1000.0, 2),
                })
            det_results.append(row)
            if idx % 100 == 0 or idx == len(records):
                print(f"[5.1.1] {idx}/{len(records)} ({time.perf_counter() - t1:.1f}s)", flush=True)

        # Save RAW_PREDICTIONS.csv
        raw_fields = [
            "item_id", "dataset", "split_type", "category", "error_family", "gold_label",
            "sentence", "reference_correction", "provenance", "execution_status",
            "error_message", "parse_ok", "token_count", "rules_verdict", "hybrid_verdict",
            "hybrid_flagged", "cola_available", "cola_label", "cola_acceptable_prob",
            "error_count", "constraints_fired", "cambridge_findings_count",
            "cambridge_rule_ids", "br_status", "br_has_working_tree", "br_schema_valid",
            "elapsed_ms",
        ]
        with open(OUT_DIR / "RAW_PREDICTIONS.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=raw_fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(det_results)

    slices = {
        "external_all_400": [r for r in det_results if r["dataset"] in {"blimp_stratified", "jfleg_stratified", "cola_stratified"}],
        "external_strict_uncontaminated_320": [r for r in det_results if r["dataset"] in {"blimp_stratified", "jfleg_stratified"}],
        "blimp_stratified": [r for r in det_results if r["dataset"] == "blimp_stratified"],
        "jfleg_stratified": [r for r in det_results if r["dataset"] == "jfleg_stratified"],
        "cola_stratified": [r for r in det_results if r["dataset"] == "cola_stratified"],
        "internal_minimal_pairs": [r for r in det_results if r["dataset"] == "internal_minimal_pairs"],
        "internal_rapid_audit_24": [r for r in det_results if r["dataset"] == "internal_rapid_audit_24"],
    }

    detection_metrics: dict[str, Any] = {}
    metrics_csv_rows: list[dict[str, Any]] = []
    for dname, drows in slices.items():
        detection_metrics[dname] = {}
        for mode_label, vfield in [("rules_only", "rules_verdict"), ("hybrid_rules_plus_cola", "hybrid_verdict")]:
            detection_metrics[dname][mode_label] = {}
            for op in ("strict_ungrammatical", "decisive_only", "non_grammatical_flagged"):
                m = compute_binary_metrics(drows, vfield, op)
                detection_metrics[dname][mode_label][op] = m
                metrics_csv_rows.append({
                    "section": "5.1.1", "dataset": dname, "mode": mode_label,
                    "operating_point": op, "category": "ALL", **m,
                })

    blimp_by_family: dict[str, Any] = {}
    for fam in sorted({r["error_family"] for r in slices["blimp_stratified"]}):
        sub = [r for r in slices["blimp_stratified"] if r["error_family"] == fam]
        blimp_by_family[fam] = {
            "rules_strict": compute_binary_metrics(sub, "rules_verdict", "strict_ungrammatical"),
            "rules_decisive": compute_binary_metrics(sub, "rules_verdict", "decisive_only"),
            "hybrid_strict": compute_binary_metrics(sub, "hybrid_verdict", "strict_ungrammatical"),
            "hybrid_decisive": compute_binary_metrics(sub, "hybrid_verdict", "decisive_only"),
            "hybrid_flagged": compute_binary_metrics(sub, "hybrid_verdict", "non_grammatical_flagged"),
        }
        for mode_label, key, op_name in [
            ("rules_only", "rules_strict", "strict_ungrammatical"),
            ("hybrid_rules_plus_cola", "hybrid_decisive", "decisive_only"),
            ("hybrid_rules_plus_cola", "hybrid_flagged", "non_grammatical_flagged"),
        ]:
            metrics_csv_rows.append({
                "section": "5.1.1", "dataset": "blimp_stratified", "mode": mode_label,
                "operating_point": op_name, "category": fam, **blimp_by_family[fam][key],
            })

    fp_constraints_ext = Counter()
    fp_examples_ext = []
    fn_by_family_rules = Counter()
    fn_examples_ext = []
    unverified_by_family_hybrid = Counter()
    for r in slices["external_all_400"]:
        if r["execution_status"] != "ok":
            continue
        if r["gold_label"] == "grammatical" and r["rules_verdict"] == "ungrammatical":
            for c in (r["constraints_fired"].split(";") if r["constraints_fired"] else ["UNKNOWN"]):
                fp_constraints_ext[c] += 1
            if len(fp_examples_ext) < 30:
                fp_examples_ext.append({
                    "item_id": r["item_id"], "dataset": r["dataset"], "category": r["category"],
                    "sentence": r["sentence"], "constraints": r["constraints_fired"], "cola_label": r["cola_label"],
                })
        if r["gold_label"] == "ungrammatical" and r["rules_verdict"] != "ungrammatical":
            fn_by_family_rules[f"{r['dataset']}:{r['error_family']}"] += 1
            if len(fn_examples_ext) < 30 and r["hybrid_verdict"] == "grammatical":
                fn_examples_ext.append({
                    "item_id": r["item_id"], "dataset": r["dataset"], "category": r["category"],
                    "error_family": r["error_family"], "sentence": r["sentence"],
                    "rules_verdict": r["rules_verdict"], "hybrid_verdict": r["hybrid_verdict"],
                    "cola_prob": r["cola_acceptable_prob"],
                })
        if r["gold_label"] == "ungrammatical" and r["hybrid_verdict"] == "unverified":
            unverified_by_family_hybrid[f"{r['dataset']}:{r['error_family']}"] += 1

    ext_tree_cov = {}
    for dname in ("external_all_400", "blimp_stratified", "jfleg_stratified", "cola_stratified", "internal_minimal_pairs"):
        drows = slices[dname]
        n = len(drows)
        pok = sum(1 for r in drows if r["parse_ok"])
        bn = sum(1 for r in drows if r["br_status"] == "normalized")
        bw = sum(1 for r in drows if r["br_status"] != "normalized" and r["br_has_working_tree"])
        bu = n - bn - bw
        bsv = sum(1 for r in drows if r["br_schema_valid"])
        ext_tree_cov[dname] = {
            "n": n, "benepar_parse_ok": pok, "benepar_parse_rate": round(pok / n, 4) if n else 0.0,
            "br_normalized": bn, "br_normalized_rate": round(bn / n, 4) if n else 0.0,
            "br_working_tree_fallback": bw, "br_unresolved_no_tree": bu,
            "br_schema_valid_count": bsv, "br_schema_valid_rate_of_normalized": round(bsv / bn, 4) if bn else None,
        }

    # =========================================================================
    # SECTION 5.1.2 — Syntax Tree Generation (FULL 216 Burton-Roberts IMG trees)
    # =========================================================================
    print("[5.1.2] Running PARSEVAL on all 216 published Burton-Roberts IMG trees...", flush=True)
    t2 = time.perf_counter()
    final_profile = br.convention_profile()
    book_full, book_tri, v2_ch2 = [], [], []
    by_ch_full: dict[int, list[dict[str, Any]]] = defaultdict(list)
    by_ch_tri: dict[int, list[dict[str, Any]]] = defaultdict(list)
    prod_norm = prod_ref = prod_exact = 0
    excl = Counter()
    mismatches = []

    for ch in range(1, 11):
        recs = json.loads((ROOT / "web/content/book" / f"ch{ch:02d}.trees.json").read_text(encoding="utf-8"))["trees"]
        for rec in recs:
            if rec.get("status") != "IMG" or not rec.get("sentence") or not rec.get("tree"):
                excl["non_img_or_missing"] += 1
                continue
            if rec.get("correct") is False:
                excl["incorrect_contrast_example"] += 1
                continue
            if ch > 1 and rec["tree"].get("label") == "Sentence":
                excl["legacy_v1_sentence_label"] += 1
                continue
            if _source_yield(rec["tree"]) != _atoms(rec["sentence"]):
                excl["partial_subtree_fixture"] += 1
                continue
            sent = rec["sentence"]
            an = parse_engine.analyze(sent)
            # Path A: Production lookup-enabled
            pr = br.build_canonical_analysis(an, chapter=ch)
            if pr.get("status") == "normalized" and pr.get("tree"):
                prod_norm += 1
                if "EXACT_IMG_GOLD_REFERENCE" in [x.get("rule_id") for x in (pr.get("normalization_trace") or [])]:
                    prod_ref += 1
                env = pr["tree"]
                cands = [env["root"]] + [a["root"] for a in (env.get("accepted_alternatives") or []) if isinstance(a, dict) and a.get("root")]
                if any(score_parseval_pair(rec["tree"], c, False)["exact_match"] for c in cands):
                    prod_exact += 1
            # Path B: True parser-projection path (lookup bypassed, fail-closed matching build_canonical_analysis)
            try:
                pj = br.normalize_benepar_candidate(an, final_profile)
            except Exception as exc:
                pj = {"status": "unresolved", "tree": None, "reasons": [{"code": "NORMALIZER_FAILURE", "detail": str(exc)}]}
            is_n = pj.get("status") == "normalized" and isinstance(pj.get("tree"), dict)
            has_w = bool(pj.get("working_tree"))
            sf = score_parseval_pair(rec["tree"], pj["tree"]["root"], False) if is_n else {"yield_match": False, "has_multiword_triangle": False}
            st = score_parseval_pair(rec["tree"], pj["tree"]["root"], True) if is_n else {"yield_match": False, "has_multiword_triangle": False}
            meta = {"record_id": rec["id"], "chapter": ch, "sentence": sent, "normalized": is_n, "working_tree": has_w,
                    "reasons": [x.get("code") for x in (pj.get("reasons") or [])]}
            rf, rt = {**meta, **sf}, {**meta, **st}
            book_full.append(rf)
            book_tri.append(rt)
            by_ch_full[ch].append(rf)
            by_ch_tri[ch].append(rt)
            if is_n and st.get("yield_match") and not st.get("exact_match") and len(mismatches) < 25:
                mismatches.append({
                    "record_id": rec["id"], "chapter": ch, "sentence": sent,
                    "has_multiword_triangle": st["has_multiword_triangle"],
                    "label_errors": st["label_errors"],
                    "boundary_only_pred": st["boundary_only_pred"],
                    "boundary_only_gold": st["boundary_only_gold"],
                    "gold_only_spans": st["gold_only_spans"][:5],
                    "pred_only_spans": st["pred_only_spans"][:5],
                })
            if ch == 2:
                try:
                    v2r = br.normalize_benepar_candidate(an, br.convention_profile(chapter=2))
                except Exception as exc:
                    v2r = {"status": "unresolved", "tree": None, "reasons": [{"code": "NORMALIZER_FAILURE", "detail": str(exc)}]}
                v2n = v2r.get("status") == "normalized" and isinstance(v2r.get("tree"), dict)
                sv2 = score_parseval_pair(rec["tree"], v2r["tree"]["root"], False) if v2n else {"yield_match": False}
                v2_ch2.append({**meta, "normalized": v2n, "working_tree": bool(v2r.get("working_tree")), **sv2})

    # Course worked examples (10 AI-source-reviewed examples)
    course = json.loads((ROOT / "web/content/lessons/course.json").read_text(encoding="utf-8"))
    course_rows = []
    for l in course["lessons"]:
        we = l.get("worked_example") or {}
        if not we.get("tree"):
            continue
        t = we["tree"]
        an = parse_engine.analyze(t["sentence"])
        try:
            pj = br.normalize_benepar_candidate(an, final_profile)
        except Exception as exc:
            pj = {"status": "unresolved", "tree": None, "reasons": [{"code": "NORMALIZER_FAILURE", "detail": str(exc)}]}
        is_n = pj.get("status") == "normalized" and isinstance(pj.get("tree"), dict)
        course_rows.append({
            "lesson_id": l["lesson_id"], "chapter": l.get("chapter"), "sentence": t["sentence"],
            "normalized": is_n, "working_tree": bool(pj.get("working_tree")),
            "full": score_parseval_pair(t["root"], pj["tree"]["root"], False) if is_n else {"yield_match": False},
            "tri": score_parseval_pair(t["root"], pj["tree"]["root"], True) if is_n else {"yield_match": False},
        })

    # Held-out 20 sentences (coverage only — br_final_d1_gold.json disqualified)
    heldout = json.loads((ROOT / "evaluation/final_d1_heldout_sentences.json").read_text(encoding="utf-8"))
    ho_norm = ho_work = ho_unres = 0
    for h in heldout:
        try:
            r = br.normalize_benepar_candidate(parse_engine.analyze(h["text"]), final_profile)
        except Exception:
            r = {"status": "unresolved"}
        if r.get("status") == "normalized":
            ho_norm += 1
        elif r.get("working_tree"):
            ho_work += 1
        else:
            ho_unres += 1

    tree_eval = {
        "book_excluded_counts": dict(excl),
        "book_production_lookup": {
            "n_complete_img": len(book_full), "n_normalized": prod_norm,
            "reference_path_matches": prod_ref, "exact_parseval_matches": prod_exact,
        },
        "book_final_d1_bypass_full": aggregate_parseval(book_full),
        "book_final_d1_bypass_triangle_aware": aggregate_parseval(book_tri),
        "book_final_d1_bypass_nontriangle_subset": aggregate_parseval([x for x in book_full if not x.get("has_multiword_triangle")]),
        "book_ch7_to_ch10_full": aggregate_parseval([x for x in book_full if x["chapter"] >= 7]),
        "book_ch7_to_ch10_triangle_aware": aggregate_parseval([x for x in book_tri if x["chapter"] >= 7]),
        "book_ch7_to_ch10_nontriangle": aggregate_parseval([x for x in book_full if x["chapter"] >= 7 and not x.get("has_multiword_triangle")]),
        "book_ch2_v2_shell_bypass": aggregate_parseval(v2_ch2),
        "by_chapter_full": {str(c): aggregate_parseval(by_ch_full[c]) for c in range(1, 11)},
        "by_chapter_triangle_aware": {str(c): aggregate_parseval(by_ch_tri[c]) for c in range(1, 11)},
        "unresolved_reasons": dict(Counter(r for x in book_full if not x["normalized"] for r in (x.get("reasons") or ["UNKNOWN"]))),
        "mismatch_examples": mismatches,
        "course_worked_examples": {
            "provenance": "Codex — scoped AI source review; not human instructor sign-off",
            "n": len(course_rows),
            "full": aggregate_parseval([{"normalized": r["normalized"], "working_tree": r["working_tree"], **r["full"]} for r in course_rows]),
            "triangle_aware": aggregate_parseval([{"normalized": r["normalized"], "working_tree": r["working_tree"], **r["tri"]} for r in course_rows]),
            "rows": [{"lesson_id": r["lesson_id"], "chapter": r["chapter"], "sentence": r["sentence"],
                      "normalized": r["normalized"], "exact_full": r["full"].get("exact_match", False),
                      "exact_tri": r["tri"].get("exact_match", False)} for r in course_rows],
        },
        "heldout_20_coverage_only": {
            "n": len(heldout), "normalized": ho_norm, "working_tree": ho_work, "unresolved": ho_unres,
            "gold_status": "DISQUALIFIED_AS_INDEPENDENT_GOLD (AI_DRAFT_OWNER_WAIVER; adapter-derived)",
        },
        "external_tree_coverage": ext_tree_cov,
    }
    print(f"[5.1.2] Complete in {time.perf_counter() - t2:.1f}s (216 book trees + 10 course + 20 heldout)", flush=True)

    # =========================================================================
    # SECTION 5.1.3 — Full-Payload Explainable AI Evaluation (120 stratified)
    # =========================================================================
    xai_pool: list[dict[str, Any]] = []
    # 36 BLiMP (6 families x 3 pairs = 36)
    blimp_fams_xai = ["subject_verb_agreement", "determiner_agreement", "verb_forms",
                      "pronoun_case_and_binding", "argument_structure", "filler_gap_dependencies"]
    for fam in blimp_fams_xai:
        sub = [r for r in slices["blimp_stratified"] if r["error_family"] == fam]
        gs = [r for r in sub if r["gold_label"] == "grammatical"][:3]
        bs = [r for r in sub if r["gold_label"] == "ungrammatical"][:3]
        for x in gs + bs:
            xai_pool.append({**x, "xai_source": "external_blimp"})
    # 12 JFLEG (6 bad + 6 good)
    j_bad = [r for r in slices["jfleg_stratified"] if r["gold_label"] == "ungrammatical"][:6]
    j_good = [r for r in slices["jfleg_stratified"] if r["gold_label"] == "grammatical"][:6]
    for x in j_bad + j_good:
        xai_pool.append({**x, "xai_source": "external_jfleg"})
    # 12 CoLA (6 bad + 6 good)
    c_b = [r for r in slices["cola_stratified"] if r["gold_label"] == "ungrammatical"][:6]
    c_g = [r for r in slices["cola_stratified"] if r["gold_label"] == "grammatical"][:6]
    for x in c_b + c_g:
        xai_pool.append({**x, "xai_source": "external_cola"})
    # 36 Internal minimal pairs (first 18 pairs)
    for x in slices["internal_minimal_pairs"][:36]:
        xai_pool.append({**x, "xai_source": "internal_minimal_pairs"})
    # All 24 Rapid Cross-Component Audit sentences
    for x in slices["internal_rapid_audit_24"]:
        xai_pool.append({**x, "xai_source": "internal_rapid_audit_24"})

    print(f"[5.1.3] Running full api.build_payload() XAI checks on {len(xai_pool)} sentences...", flush=True)
    t3 = time.perf_counter()
    xai_rows = []
    for idx, item in enumerate(xai_pool, 1):
        sent = item["sentence"]
        ts = time.perf_counter()
        try:
            payload = api.build_payload(sent)
        except Exception as exc:
            xai_rows.append({**item, "execution_status": "error", "error_message": f"{type(exc).__name__}: {exc}"})
            continue
        summary = payload.get("summary") or {}
        details = payload.get("node_details") or {}
        br_an = payload.get("br_analysis") or {}
        fg = (payload.get("explanation_evidence") or {}).get("fact_graph") or {}
        cam_eval = payload.get("cambridge_evaluation") or {}
        xai7 = payload.get("xai7_unified") or {}
        correction = summary.get("correction")
        verdict = summary.get("verdict", "unknown")
        err_details = [(did, d) for did, d in details.items() if isinstance(d, dict) and d.get("status") == "error"]

        verdict_consistent = (len(err_details) >= 1) if verdict == "ungrammatical" else (len(err_details) == 0 if verdict in {"grammatical", "unverified"} else False)
        display_gating_ok = True if verdict == "grammatical" else not any(isinstance(d, dict) and d.get("display_status") == "valid" for d in details.values())

        sent_low = sent.casefold()
        err_texts, err_constraints, err_flesch, err_wc, err_hflags = [], [], [], [], []
        rule_grounded_all = surface_grounded_all = True
        for _, d in err_details:
            cn = d.get("constraint") or d.get("rule_id") or ""
            tx = (d.get("text") or "").strip()
            fx = ((d.get("remediation") or {}).get("suggested_fix") or "").strip()
            comb = (tx + (" " + fx if fx else "")).strip()
            sf = (d.get("surface") or "").strip()
            err_constraints.append(cn)
            err_texts.append(comb)
            if not cn or not tx:
                rule_grounded_all = False
            if sf:
                toks = re.findall(r"\w+(?:['’]\w+)*", sf.casefold())
                if toks and not all(tok in sent_low for tok in toks):
                    surface_grounded_all = False
            err_hflags.extend(_hygiene_flags(comb, "error"))
            fe = _flesch(comb)
            if fe is not None:
                err_flesch.append(fe)
            err_wc.append(len(_words(comb)))

        br_st = br_an.get("status", "unresolved")
        br_tree = br_an.get("tree")
        br_sv = False
        tree_ids: set[str] = set()
        if br_st == "normalized" and isinstance(br_tree, dict):
            br_sv = not any(schema_val.iter_errors(br_tree))
            st_nodes = [br_tree.get("root")]
            while st_nodes:
                cur = st_nodes.pop()
                if isinstance(cur, dict):
                    if cur.get("id"):
                        tree_ids.add(cur["id"])
                    st_nodes.extend(cur.get("children") or [])
        fg_nodes = fg.get("nodes") or []
        fg_ids = {n.get("node_id") for n in fg_nodes if isinstance(n, dict) and n.get("node_id")}
        fg_grounded = fg_ids.issubset(tree_ids) if (br_st == "normalized" and fg_nodes) else (br_st != "normalized")

        lp_cnt = lp_ne = lp_dup = 0
        lp_flags = []
        root_prose = ""
        if fg_nodes:
            seen_p = Counter()
            for j, n in enumerate(fg_nodes):
                pt = (compose_learner_explanation(fg, node_id=n["node_id"]).get("text") or "").strip()
                if j == 0:
                    root_prose = pt
                lp_cnt += 1
                if pt:
                    lp_ne += 1
                    seen_p[pt] += 1
                    lp_flags.extend(_hygiene_flags(pt, "neutral"))
            lp_dup = sum(c - 1 for c in seen_p.values() if c > 1)

        has_corr = bool(summary.get("corrected_sentence"))
        corr_s = summary.get("corrected_sentence") or ""
        imp = (correction or {}).get("impact") or {}
        ref_c = item.get("reference_correction") or ""
        xai_rows.append({
            **item,
            "execution_status": "ok",
            "elapsed_ms": round((time.perf_counter() - ts) * 1000.0, 2),
            "verdict": verdict,
            "summary_explanation": (summary.get("explanation") or "").strip(),
            "detector_label": (summary.get("detector") or {}).get("label", ""),
            "error_count": len(err_details),
            "error_constraints": ";".join(sorted(set(err_constraints))),
            "error_texts_joined": " | ".join(err_texts),
            "cambridge_rule_ids": ";".join(sorted({str(f.get("rule_id", "")) for f in (cam_eval.get("findings") or []) if f.get("rule_id")})),
            "verdict_consistent": verdict_consistent,
            "display_gating_ok": display_gating_ok,
            "rule_grounded_all": rule_grounded_all,
            "surface_grounded_all": surface_grounded_all,
            "br_status": br_st,
            "br_schema_valid": br_sv,
            "fg_node_count": len(fg_nodes),
            "fg_grounded_in_tree": fg_grounded,
            "learner_prose_count": lp_cnt,
            "learner_prose_nonempty": lp_ne,
            "learner_prose_dup_within": lp_dup,
            "root_learner_prose": root_prose,
            "root_q_subordinate_bug": bool(sent.strip().endswith("?") and "subordinate clause" in root_prose.lower()),
            "error_hygiene_flags": ";".join(sorted(set(err_hflags))),
            "learner_hygiene_flags": ";".join(sorted(set(lp_flags))),
            "error_flesch_list": err_flesch,
            "error_word_counts": err_wc,
            "has_correction": has_corr,
            "corrected_sentence": corr_s,
            "correction_differs": bool(has_corr and corr_s.strip() != sent.strip()),
            "corr_resolved": imp.get("resolved_count"),
            "corr_remaining": imp.get("remaining_count"),
            "corr_introduced": imp.get("introduced_count"),
            "corr_whole_clean": imp.get("whole_sentence_clean"),
            "corr_resulting_verdict": imp.get("resulting_verdict"),
            "corr_exact_match_ref": bool(has_corr and ref_c and corr_s.strip().casefold() == ref_c.strip().casefold()),
            "xai7_status": xai7.get("status", ""),
            "parse_string": (payload.get("parse") or {}).get("parse_string", ""),
        })
        if idx % 30 == 0 or idx == len(xai_pool):
            print(f"[5.1.3] {idx}/{len(xai_pool)} ({time.perf_counter() - t3:.1f}s)", flush=True)

    raw_by_id = {r["item_id"]: r for r in det_results}
    xai_ok = [x for x in xai_rows if x["execution_status"] == "ok"]
    vp_chk = sum(1 for x in xai_ok if x["item_id"] in raw_by_id)
    vp_mat = sum(1 for x in xai_ok if x["item_id"] in raw_by_id and x["verdict"] == raw_by_id[x["item_id"]]["hybrid_verdict"])

    n_xai = len(xai_ok)
    xai_err = [x for x in xai_ok if x["error_count"] > 0]
    xai_corr = [x for x in xai_ok if x["has_correction"]]
    xai_corr_ref = [x for x in xai_corr if x.get("reference_correction")]
    xai_norm = [x for x in xai_ok if x["br_status"] == "normalized"]
    xai_q = [x for x in xai_ok if x["sentence"].strip().endswith("?")]
    all_ef = [v for x in xai_err for v in x["error_flesch_list"]]
    all_ew = [v for x in xai_err for v in x["error_word_counts"]]

    xai_summary = {
        "n_total": len(xai_rows),
        "n_ok": n_xai,
        "n_exec_error": len(xai_rows) - n_xai,
        "verdict_distribution": dict(Counter(x["verdict"] for x in xai_ok)),
        "verdict_parity_with_511": {"checked": vp_chk, "matched": vp_mat, "rate": round(vp_mat / vp_chk, 4) if vp_chk else None},
        "verdict_evidence_consistent": sum(1 for x in xai_ok if x["verdict_consistent"]),
        "verdict_evidence_consistent_rate": round(sum(1 for x in xai_ok if x["verdict_consistent"]) / n_xai, 4) if n_xai else None,
        "display_status_truth_gating_ok": sum(1 for x in xai_ok if x["display_gating_ok"]),
        "display_status_truth_gating_rate": round(sum(1 for x in xai_ok if x["display_gating_ok"]) / n_xai, 4) if n_xai else None,
        "sentences_with_error_explanations": len(xai_err),
        "rule_grounded_all_count": sum(1 for x in xai_err if x["rule_grounded_all"]),
        "rule_grounded_rate": round(sum(1 for x in xai_err if x["rule_grounded_all"]) / len(xai_err), 4) if xai_err else None,
        "surface_token_grounded_count": sum(1 for x in xai_err if x["surface_grounded_all"]),
        "surface_token_grounded_rate": round(sum(1 for x in xai_err if x["surface_grounded_all"]) / len(xai_err), 4) if xai_err else None,
        "br_normalized_count": len(xai_norm),
        "br_schema_valid_count": sum(1 for x in xai_norm if x["br_schema_valid"]),
        "fact_graph_tree_grounded_count": sum(1 for x in xai_norm if x["fg_grounded_in_tree"]),
        "fact_graph_tree_grounded_rate": round(sum(1 for x in xai_norm if x["fg_grounded_in_tree"]) / len(xai_norm), 4) if xai_norm else None,
        "total_node_explanations_generated": sum(x["learner_prose_count"] for x in xai_ok),
        "total_node_explanations_nonempty": sum(x["learner_prose_nonempty"] for x in xai_ok),
        "total_duplicate_prose_within_sentence": sum(x["learner_prose_dup_within"] for x in xai_ok),
        "root_question_count": len(xai_q),
        "root_question_called_subordinate_count": sum(1 for x in xai_q if x["root_q_subordinate_bug"]),
        "corrections_generated": len(xai_corr),
        "corrections_differ_from_input": sum(1 for x in xai_corr if x["correction_differs"]),
        "corrections_reparse_whole_clean": sum(1 for x in xai_corr if x["corr_whole_clean"] is True),
        "corrections_reparse_whole_clean_rate": round(sum(1 for x in xai_corr if x["corr_whole_clean"] is True) / len(xai_corr), 4) if xai_corr else None,
        "corrections_reparse_resolved_gt0": sum(1 for x in xai_corr if (x["corr_resolved"] or 0) > 0),
        "corrections_reparse_introduced_new_error": sum(1 for x in xai_corr if (x["corr_introduced"] or 0) > 0),
        "corrections_with_reference_count": len(xai_corr_ref),
        "corrections_exact_match_reference": sum(1 for x in xai_corr_ref if x["corr_exact_match_ref"]),
        "error_explanation_flesch_mean": round(sum(all_ef) / len(all_ef), 1) if all_ef else None,
        "error_explanation_flesch_median": sorted(all_ef)[len(all_ef) // 2] if all_ef else None,
        "error_explanation_words_mean": round(sum(all_ew) / len(all_ew), 1) if all_ew else None,
        "error_hygiene_flag_counts": dict(Counter(fl for x in xai_err for fl in (x["error_hygiene_flags"].split(";") if x["error_hygiene_flags"] else []))),
        "learner_node_hygiene_flag_counts": dict(Counter(fl for x in xai_ok for fl in (x["learner_hygiene_flags"].split(";") if x["learner_hygiene_flags"] else []))),
        "human_review_status": "UNMEASURED_BLOCKED_NO_COMPLETED_HUMAN_RATINGS",
    }

    # Build HUMAN_REVIEW_WORKSHEET.csv (60 stratified executed cases, blank human columns)
    buckets = {
        "TP_rules_flagged": [x for x in xai_ok if x["gold_label"] == "ungrammatical" and x["verdict"] == "ungrammatical"],
        "FP_rules_flagged": [x for x in xai_ok if x["gold_label"] == "grammatical" and x["verdict"] == "ungrammatical"],
        "UNVERIFIED_gold_ungram": [x for x in xai_ok if x["gold_label"] == "ungrammatical" and x["verdict"] == "unverified"],
        "UNVERIFIED_gold_gram": [x for x in xai_ok if x["gold_label"] == "grammatical" and x["verdict"] == "unverified"],
        "FN_missed_ungram": [x for x in xai_ok if x["gold_label"] == "ungrammatical" and x["verdict"] == "grammatical"],
        "TN_clean_gram": [x for x in xai_ok if x["gold_label"] == "grammatical" and x["verdict"] == "grammatical"],
    }
    ws_rows = []
    seen_ws = set()
    for bname, q in [("TP_rules_flagged", 16), ("FP_rules_flagged", 10), ("UNVERIFIED_gold_ungram", 12),
                     ("UNVERIFIED_gold_gram", 6), ("FN_missed_ungram", 8), ("TN_clean_gram", 8)]:
        pool = [x for x in buckets[bname] if x["xai_source"].startswith("external")] + [x for x in buckets[bname] if not x["xai_source"].startswith("external")]
        for x in pool:
            if x["item_id"] in seen_ws:
                continue
            seen_ws.add(x["item_id"])
            ws_rows.append({
                "review_id": f"HR-{len(ws_rows) + 1:03d}",
                "stratum": bname,
                "item_id": x["item_id"],
                "dataset": x["dataset"],
                "error_family": x["error_family"],
                "sentence": x["sentence"],
                "gold_label": x["gold_label"],
                "reference_correction": x.get("reference_correction", ""),
                "syntutor_verdict": x["verdict"],
                "detector_label": x["detector_label"],
                "triggered_constraints": x["error_constraints"],
                "cambridge_rule_ids": x["cambridge_rule_ids"],
                "br_normalization_status": x["br_status"],
                "benepar_parse_string": x["parse_string"],
                "generated_correction": x["corrected_sentence"],
                "summary_explanation": x["summary_explanation"],
                "error_explanation_text": x["error_texts_joined"],
                "root_learner_tree_explanation": x["root_learner_prose"],
                "r1_linguistic_accuracy_1_5": "",
                "r1_verdict_explanation_consistency_1_5": "",
                "r1_rule_grounding_1_5": "",
                "r1_tree_evidence_grounding_1_5": "",
                "r1_correction_validity_1_5": "",
                "r1_pedagogical_clarity_1_5": "",
                "r1_defect_category": "",
                "r1_notes": "",
                "r2_linguistic_accuracy_1_5": "",
                "r2_verdict_explanation_consistency_1_5": "",
                "r2_rule_grounding_1_5": "",
                "r2_tree_evidence_grounding_1_5": "",
                "r2_correction_validity_1_5": "",
                "r2_pedagogical_clarity_1_5": "",
                "r2_defect_category": "",
                "r2_notes": "",
                "adjudicated_consensus_score": "",
            })
            if sum(1 for r in ws_rows if r["stratum"] == bname) >= q:
                break

    with open(OUT_DIR / "HUMAN_REVIEW_WORKSHEET.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ws_rows[0].keys()))
        w.writeheader()
        w.writerows(ws_rows)

    with open(OUT_DIR / "METRICS_SUMMARY.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(metrics_csv_rows[0].keys()))
        w.writeheader()
        w.writerows(metrics_csv_rows)

    computed = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_runtime_seconds": round(time.perf_counter() - t0, 2),
        "evaluation_design": "Fast-track stratified external subset (n=400: 240 BLiMP + 80 JFLEG + 80 CoLA) + full internal minimal pairs (n=52) + rapid audit (n=24) + FULL census 216 Burton-Roberts textbook IMG trees + 120 full-payload XAI checks",
        "section_511": {
            "overall": detection_metrics,
            "blimp_by_family": blimp_by_family,
            "fp_constraints_external": dict(fp_constraints_ext.most_common(30)),
            "fn_by_family_rules_external": dict(fn_by_family_rules.most_common(30)),
            "unverified_by_family_hybrid_external": dict(unverified_by_family_hybrid.most_common(30)),
            "fp_examples_external": fp_examples_ext,
            "fn_examples_external": fn_examples_ext,
        },
        "section_512": tree_eval,
        "section_513": {
            "summary": xai_summary,
            "rapid_audit_24_results": [
                {
                    "item_id": x["item_id"], "category": x["category"], "sentence": x["sentence"],
                    "gold_label": x["gold_label"], "verdict": x["verdict"], "constraints": x["error_constraints"],
                    "corrected_sentence": x["corrected_sentence"], "root_q_subordinate_bug": x["root_q_subordinate_bug"],
                    "verdict_consistent": x["verdict_consistent"], "br_status": x["br_status"],
                }
                for x in xai_ok if x["dataset"] == "internal_rapid_audit_24"
            ],
            "correction_failures": [
                {
                    "item_id": x["item_id"], "dataset": x["dataset"], "sentence": x["sentence"],
                    "corrected_sentence": x["corrected_sentence"], "corr_resolved": x["corr_resolved"],
                    "corr_remaining": x["corr_remaining"], "corr_introduced": x["corr_introduced"],
                    "corr_resulting_verdict": x["corr_resulting_verdict"],
                }
                for x in xai_corr if not x["corr_whole_clean"]
            ][:20],
            "worksheet_strata_counts": dict(Counter(r["stratum"] for r in ws_rows)),
        },
    }
    (OUT_DIR / "_computed_results.json").write_text(json.dumps(computed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[eval] ALL DONE in {computed['total_runtime_seconds']}s!", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
