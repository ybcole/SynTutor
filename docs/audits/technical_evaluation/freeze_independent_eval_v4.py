#!/usr/bin/env python3
"""Deterministically construct, verify, and freeze FROZEN_INDEPENDENT_EVAL_V4.csv.

Strict blind evaluation discipline (Cycle 8 Priority One):
- Excludes ALL sentences (case-folded exact match) appearing in:
  * RAW_PREDICTIONS.csv (Dev-320 + CoLA-80 + internal)
  * FROZEN_UNTOUCHED_HOLDOUT.csv (HO-V1)
  * FROZEN_FINAL_HOLDOUT_V2.csv (HO-V2)
  * FROZEN_FINAL_HOLDOUT_V3.csv (HO-V3)
  * evaluation/*.json
  * web/content/book/ch*.trees.json
- Audits near-duplicate lexical overlap (token Jaccard >= 0.85) against prior sets
  and excludes near-duplicates from CoLA and JFLEG (and reports BLiMP template
  similarity transparently).
- Never prints sentence contents so the dataset stays strictly blind until
  Cycle 8 code and configuration are locked.
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DIR = Path(__file__).resolve().parent
SEED = 20261121

BLIMP_FAMILY_MAP = {
    # Argument structure
    "animate_subject_passive": "argument_structure",
    "animate_subject_trans": "argument_structure",
    "causative": "argument_structure",
    "drop_argument": "argument_structure",
    "inchoative": "argument_structure",
    "intransitive": "argument_structure",
    "passive_1": "argument_structure",
    "passive_2": "argument_structure",
    "transitive": "argument_structure",
    # Determiner-noun agreement
    "determiner_noun_agreement_1": "determiner_agreement",
    "determiner_noun_agreement_2": "determiner_agreement",
    "determiner_noun_agreement_irregular_1": "determiner_agreement",
    "determiner_noun_agreement_irregular_2": "determiner_agreement",
    "determiner_noun_agreement_with_adj_2": "determiner_agreement",
    "determiner_noun_agreement_with_adj_irregular_1": "determiner_agreement",
    "determiner_noun_agreement_with_adj_irregular_2": "determiner_agreement",
    "determiner_noun_agreement_with_adjective_1": "determiner_agreement",
    # Ellipsis
    "ellipsis_n_bar_1": "ellipsis",
    "ellipsis_n_bar_2": "ellipsis",
    # Filler-gap dependencies
    "wh_questions_object_gap": "filler_gap_dependencies",
    "wh_questions_subject_gap": "filler_gap_dependencies",
    "wh_questions_subject_gap_long_distance": "filler_gap_dependencies",
    "wh_vs_that_no_gap": "filler_gap_dependencies",
    "wh_vs_that_no_gap_long_distance": "filler_gap_dependencies",
    "wh_vs_that_with_gap": "filler_gap_dependencies",
    "wh_vs_that_with_gap_long_distance": "filler_gap_dependencies",
    # Island effects
    "adjunct_island": "island_effects",
    "complex_NP_island": "island_effects",
    "coordinate_structure_constraint_complex_left_branch": "island_effects",
    "coordinate_structure_constraint_object_extraction": "island_effects",
    "left_branch_island_echo_question": "island_effects",
    "left_branch_island_simple_question": "island_effects",
    "sentential_subject_island": "island_effects",
    "wh_island": "island_effects",
    # NPI licensing
    "matrix_question_npi_licensor_present": "npi_licensing",
    "npi_present_1": "npi_licensing",
    "npi_present_2": "npi_licensing",
    "only_npi_licensor_present": "npi_licensing",
    "only_npi_scope": "npi_licensing",
    "sentential_negation_npi_licensor_present": "npi_licensing",
    "sentential_negation_npi_scope": "npi_licensing",
    # Pronoun case & binding
    "anaphor_gender_agreement": "pronoun_case_and_binding",
    "anaphor_number_agreement": "pronoun_case_and_binding",
    "principle_A_c_command": "pronoun_case_and_binding",
    "principle_A_case_1": "pronoun_case_and_binding",
    "principle_A_case_2": "pronoun_case_and_binding",
    "principle_A_domain_1": "pronoun_case_and_binding",
    "principle_A_domain_2": "pronoun_case_and_binding",
    "principle_A_domain_3": "pronoun_case_and_binding",
    "principle_A_reconstruction": "pronoun_case_and_binding",
    # Quantifiers & raising
    "existential_there_object_raising": "quantifiers_and_raising",
    "existential_there_quantifiers_1": "quantifiers_and_raising",
    "existential_there_quantifiers_2": "quantifiers_and_raising",
    "existential_there_subject_raising": "quantifiers_and_raising",
    "expletive_it_object_raising": "quantifiers_and_raising",
    "superlative_quantifiers_1": "quantifiers_and_raising",
    "superlative_quantifiers_2": "quantifiers_and_raising",
    "tough_vs_raising_1": "quantifiers_and_raising",
    "tough_vs_raising_2": "quantifiers_and_raising",
    # Subject-verb agreement
    "distractor_agreement_relational_noun": "subject_verb_agreement",
    "distractor_agreement_relative_clause": "subject_verb_agreement",
    "irregular_plural_subject_verb_agreement_1": "subject_verb_agreement",
    "irregular_plural_subject_verb_agreement_2": "subject_verb_agreement",
    "regular_plural_subject_verb_agreement_1": "subject_verb_agreement",
    "regular_plural_subject_verb_agreement_2": "subject_verb_agreement",
    # Verb forms / irregulars
    "irregular_past_participle_adjectives": "verb_forms",
    "irregular_past_participle_verbs": "verb_forms",
}


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip()).casefold()


def _toks(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", _norm(s)))


def _max_jaccard(s: str, prior_tok_sets: list[set[str]]) -> float:
    ts = _toks(s)
    if not ts:
        return 0.0
    best = 0.0
    for pts in prior_tok_sets:
        if not pts:
            continue
        inter = len(ts & pts)
        if inter == 0:
            continue
        j = inter / len(ts | pts)
        if j > best:
            best = j
    return best


def collect_prior_sentences() -> tuple[set[str], list[set[str]]]:
    prior: set[str] = set()
    for fn in (
        "RAW_PREDICTIONS.csv",
        "FROZEN_UNTOUCHED_HOLDOUT.csv",
        "FROZEN_FINAL_HOLDOUT_V2.csv",
        "FROZEN_FINAL_HOLDOUT_V3.csv",
    ):
        p = DIR / fn
        if p.exists():
            for r in csv.DictReader(open(p, encoding="utf-8")):
                if r.get("sentence"):
                    prior.add(_norm(r["sentence"]))
                if r.get("reference_correction"):
                    prior.add(_norm(r["reference_correction"]))
    # Also exclude internal evaluation JSONs and textbook sentences
    for jp in (ROOT / "evaluation").glob("*.json"):
        try:
            data = json.loads(jp.read_text(encoding="utf-8"))
        except Exception:
            continue
        def _walk(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in ("sentence", "grammatical", "ungrammatical", "text") and isinstance(v, str):
                        prior.add(_norm(v))
                    else:
                        _walk(v)
            elif isinstance(obj, list):
                for x in obj:
                    _walk(x)
        _walk(data)
    for bp in (ROOT / "web/content/book").glob("ch*.trees.json"):
        try:
            data = json.loads(bp.read_text(encoding="utf-8"))
            for rec in (data.get("records") if isinstance(data, dict) else data):
                if isinstance(rec, dict) and isinstance(rec.get("sentence"), str):
                    prior.add(_norm(rec["sentence"]))
        except Exception:
            continue
    return prior, [_toks(s) for s in prior]


def main() -> int:
    rng = random.Random(SEED)
    prior_norm, prior_toks = collect_prior_sentences()
    out_rows: list[dict[str, str]] = []

    # 1. Untouched BLiMP: stratified across all 9 families with unused pairs
    # Target: 130 pairs = 260 items, covering all 63 untouched paradigms.
    blimp_raw = list(csv.DictReader(open(ROOT / "benchmarks/blimp.tsv", encoding="utf-8"), delimiter="\t"))
    by_fam_cat: dict[str, dict[str, list[tuple[dict, dict]]]] = defaultdict(lambda: defaultdict(list))
    for i in range(0, len(blimp_raw), 2):
        if i + 1 >= len(blimp_raw):
            break
        a, b = blimp_raw[i], blimp_raw[i + 1]
        if a["category"] != b["category"]:
            continue
        good, bad = (a, b) if a["label"] == "good" else (b, a)
        if _norm(good["sentence"]) in prior_norm or _norm(bad["sentence"]) in prior_norm:
            continue
        fam = BLIMP_FAMILY_MAP[good["category"]]
        by_fam_cat[fam][good["category"]].append((good, bad))

    # Quota per family (sums to 130 pairs = 260 items)
    fam_quotas = {
        "argument_structure": 18,
        "determiner_agreement": 14,
        "ellipsis": 10,
        "filler_gap_dependencies": 14,
        "island_effects": 16,
        "npi_licensing": 14,
        "pronoun_case_and_binding": 16,
        "quantifiers_and_raising": 16,
        "subject_verb_agreement": 12,
    }
    chosen_blimp: list[tuple[str, str, dict, dict]] = []
    seen_v4: set[str] = set()
    for fam, quota in sorted(fam_quotas.items()):
        cats = sorted(by_fam_cat[fam].keys())
        # Shuffle within each paradigm deterministically, then round-robin across paradigms
        pools = {}
        for c in cats:
            lst = list(by_fam_cat[fam][c])
            rng.shuffle(lst)
            pools[c] = lst
        picked = 0
        idx = 0
        while picked < quota and any(pools.values()):
            c = cats[idx % len(cats)]
            if pools[c]:
                good, bad = pools[c].pop()
                ng, nb = _norm(good["sentence"]), _norm(bad["sentence"])
                if ng != nb and ng not in seen_v4 and nb not in seen_v4:
                    seen_v4.add(ng)
                    seen_v4.add(nb)
                    chosen_blimp.append((fam, c, good, bad))
                    picked += 1
            idx += 1

    for pidx, (fam, cat, good, bad) in enumerate(chosen_blimp, 1):
        out_rows.append({
            "item_id": f"eval4-blimp-{pidx:03d}-g",
            "dataset": "eval4_blimp",
            "provenance_tier": "tier1_uncontaminated_external",
            "source_benchmark": "nyu-mll/blimp",
            "source_category": cat,
            "error_family": fam,
            "gold_label": "grammatical",
            "sentence": good["sentence"].strip(),
            "reference_correction": "",
        })
        out_rows.append({
            "item_id": f"eval4-blimp-{pidx:03d}-u",
            "dataset": "eval4_blimp",
            "provenance_tier": "tier1_uncontaminated_external",
            "source_benchmark": "nyu-mll/blimp",
            "source_category": cat,
            "error_family": fam,
            "gold_label": "ungrammatical",
            "sentence": bad["sentence"].strip(),
            "reference_correction": good["sentence"].strip(),
        })

    # 2. Untouched JFLEG: ALL remaining completely untouched pairs (up to 20 pairs = 40 items)
    jfleg_raw = list(csv.DictReader(open(ROOT / "benchmarks/jfleg.tsv", encoding="utf-8"), delimiter="\t"))
    jfleg_pairs = []
    for i in range(0, len(jfleg_raw), 2):
        if i + 1 >= len(jfleg_raw):
            break
        a, b = jfleg_raw[i], jfleg_raw[i + 1]
        bad, good = (a, b) if a["label"] == "bad" else (b, a)
        if _norm(bad["sentence"]) in prior_norm or _norm(good["sentence"]) in prior_norm:
            continue
        nb, ng = _norm(bad["sentence"]), _norm(good["sentence"])
        if nb == ng or nb in seen_v4 or ng in seen_v4:
            continue
        if _max_jaccard(bad["sentence"], prior_toks) >= 0.85 or _max_jaccard(good["sentence"], prior_toks) >= 0.85:
            continue
        seen_v4.add(nb)
        seen_v4.add(ng)
        jfleg_pairs.append((bad, good))
    for pidx, (bad, good) in enumerate(jfleg_pairs, 1):
        out_rows.append({
            "item_id": f"eval4-jfleg-{pidx:03d}-u",
            "dataset": "eval4_jfleg",
            "provenance_tier": "tier1_uncontaminated_external",
            "source_benchmark": "jhu-clsp/jfleg",
            "source_category": "jfleg",
            "error_family": "l2_learner_writing",
            "gold_label": "ungrammatical",
            "sentence": bad["sentence"].strip(),
            "reference_correction": good["sentence"].strip(),
        })
        out_rows.append({
            "item_id": f"eval4-jfleg-{pidx:03d}-g",
            "dataset": "eval4_jfleg",
            "provenance_tier": "tier1_uncontaminated_external",
            "source_benchmark": "jhu-clsp/jfleg",
            "source_category": "jfleg",
            "error_family": "l2_learner_writing",
            "gold_label": "grammatical",
            "sentence": good["sentence"].strip(),
            "reference_correction": "",
        })

    # 3. Untouched CoLA: 50 good + 50 bad = 100 items
    # Explicitly tagged as tier1_cola_rules_independent_hybrid_indist
    cola_raw = list(csv.DictReader(open(ROOT / "benchmarks/cola.tsv", encoding="utf-8"), delimiter="\t"))
    cola_good = []
    cola_bad = []
    seen_cola = set()
    for r in cola_raw:
        ns = _norm(r["sentence"])
        if ns in prior_norm or ns in seen_cola or ns in seen_v4:
            continue
        if _max_jaccard(r["sentence"], prior_toks) >= 0.85:
            continue
        seen_cola.add(ns)
        if r["label"] == "good":
            cola_good.append(r)
        else:
            cola_bad.append(r)
    rng.shuffle(cola_good)
    rng.shuffle(cola_bad)
    for idx, r in enumerate(cola_good[:50], 1):
        out_rows.append({
            "item_id": f"eval4-cola-{idx:03d}-g",
            "dataset": "eval4_cola",
            "provenance_tier": "tier1_cola_rules_independent_hybrid_indist",
            "source_benchmark": "nyu-mll/glue:cola",
            "source_category": "cola",
            "error_family": "cola_general_syntax",
            "gold_label": "grammatical",
            "sentence": r["sentence"].strip(),
            "reference_correction": "",
        })
    for idx, r in enumerate(cola_bad[:50], 1):
        out_rows.append({
            "item_id": f"eval4-cola-{idx:03d}-u",
            "dataset": "eval4_cola",
            "provenance_tier": "tier1_cola_rules_independent_hybrid_indist",
            "source_benchmark": "nyu-mll/glue:cola",
            "source_category": "cola",
            "error_family": "cola_general_syntax",
            "gold_label": "ungrammatical",
            "sentence": r["sentence"].strip(),
            "reference_correction": "",
        })

    # Verify zero exact overlap & zero internal duplicates
    out_norms = [_norm(r["sentence"]) for r in out_rows]
    assert len(out_norms) == len(set(out_norms)), "Internal duplicate in V4!"
    assert not (set(out_norms) & prior_norm), "Exact overlap with prior datasets!"

    # Measure near-duplicate Jaccard distribution transparently (without printing sentences)
    jacc_high_by_ds = Counter()
    for r in out_rows:
        mj = _max_jaccard(r["sentence"], prior_toks)
        if mj >= 0.85:
            jacc_high_by_ds[r["dataset"]] += 1

    out_path = DIR / "FROZEN_INDEPENDENT_EVAL_V4.csv"
    fields = [
        "item_id", "dataset", "provenance_tier", "source_benchmark",
        "source_category", "error_family", "gold_label", "sentence", "reference_correction",
    ]
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    sha = hashlib.sha256(out_path.read_bytes()).hexdigest()
    meta = {
        "file": str(out_path.name),
        "sha256": sha,
        "seed": SEED,
        "n_total": len(out_rows),
        "by_dataset": dict(Counter(r["dataset"] for r in out_rows)),
        "by_provenance_tier": dict(Counter(r["provenance_tier"] for r in out_rows)),
        "by_gold_label": dict(Counter(r["gold_label"] for r in out_rows)),
        "by_error_family": dict(Counter(r["error_family"] for r in out_rows)),
        "blimp_distinct_paradigms": len({r["source_category"] for r in out_rows if r["dataset"] == "eval4_blimp"}),
        "exact_overlap_with_all_prior_and_internal": 0,
        "near_dup_jaccard_ge_085_by_dataset": dict(jacc_high_by_ds),
        "blind_status": "FROZEN_BLIND_PRE_CYCLE8_CODE_CHANGES",
    }
    meta_path = DIR / "FROZEN_INDEPENDENT_EVAL_V4_MANIFEST.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
