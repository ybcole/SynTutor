# SynTutor Technical Evaluation Reproduction Guide

**Repository commit:** `d5aeaf5de98c45abbf2d97f19a6092a24d4ba44c` (`main`)  
**Runtime Environment:** macOS 15.8.2 (`arm64`), Python 3.11.17 (`.venv`), `spacy==3.8.16`, `en_core_web_md==3.8.0`, `benepar_en3`, cached `textattack/roberta-base-CoLA` (`HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`).

---

## 1. Prerequisites

1. Repository root working directory (`/Users/kiyel/Desktop/SynTutor`).
2. Local `.venv` containing `spacy`, `benepar`, `torch`, `transformers`, `jsonschema`, and `en_core_web_md`.
3. Local NLTK data directory containing `benepar_en3` (e.g., `~/nltk_data/models/benepar_en3`) and local HuggingFace cache containing `textattack/roberta-base-CoLA`.
4. No production files in `server/`, `grammar/`, `web/`, or `scripts/` are modified by this evaluation.

---

## 2. Exact Commands Executed

### Step 1 — Verify Model Health & Runtime Speed
```sh
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python -B -c "
import sys; sys.path.insert(0, 'server'); import api
print(api.health_payload())
"
```

### Step 2 — Run Complete Technical Evaluation Harness (Sections 5.1.1–5.1.3)
Runs all 476 stratified external + internal sentences (both Rules-Only and Hybrid Rules+CoLA modes), all 216 published Burton–Roberts textbook IMG trees (lookup-bypassed and lookup-enabled), all 10 AI-reviewed course worked examples, all 20 held-out normalization-coverage sentences, and all 120 full `api.build_payload()` XAI evaluations:

```sh
PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  .venv/bin/python -B docs/audits/technical_evaluation/run_technical_evaluation.py
```

*(Note: During execution, Section 5.1.1 completed all 476 sentences in 47.3s writing `RAW_PREDICTIONS.csv`; after adding fail-closed exception handling for 4 hyphen-alignment `NORMALIZER_FAILURE` edge cases in Section 5.1.2, Sections 5.1.2 and 5.1.3 completed in 69.71s using `--reuse-raw` against the just-written `RAW_PREDICTIONS.csv`. Running without `--reuse-raw` reproduces all outputs end-to-end in ~115s.)*

### Step 3 — Independent Mathematical Verification & Integrity Audit
Recomputes all 66 rows of `METRICS_SUMMARY.csv` directly from `RAW_PREDICTIONS.csv`, verifies all PARSEVAL precision/recall/F1 identities in `_computed_results.json`, and asserts zero fabricated values in all 17 human-rating columns of `HUMAN_REVIEW_WORKSHEET.csv`:

```sh
.venv/bin/python -B docs/audits/technical_evaluation/verify_metrics.py
```
Expected result: `VERIFICATION PASSED: 74 independent metric/integrity checks verified cleanly.`

### Step 4 — Generate All 5 Publication-Quality 300 DPI Thesis Figures
```sh
.venv/bin/python -B docs/audits/technical_evaluation/generate_figures.py
sips -g pixelWidth -g pixelHeight -g dpiWidth -g dpiHeight docs/audits/technical_evaluation/figures/*.png
```

### Step 5 — Verify Existing Model-Free Regression Suites Remain Intact
```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=server .venv/bin/python -B -m unittest \
  server.test_grammar_schema server.test_br_tree_schema server.test_detector \
  server.test_findings server.test_xai_facts server.test_xai_concepts server.test_xai7_unified

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=server .venv/bin/python -B -m unittest \
  server.test_authority server.test_br_native_grammar server.test_cambridge_registry \
  server.test_legacy_disposition server.test_xai_composer server.test_xai6_naturalizer
```
Observed results: `Ran 73 tests in 23.089s / OK` and `Ran 76 tests in 10.290s / OK` (**149/149 passed**).

---

## 3. Generated Artifacts & File Map

| File | Description |
|---|---|
| `docs/audits/SYNTUTOR_TECHNICAL_EVALUATION.md` | Complete thesis-ready academic evaluation report (Sections 5.1.1–5.1.3) |
| `docs/audits/technical_evaluation/GRAMMAR_DETECTION_RESULTS.md` | Detailed Section 5.1.1 metrics, confusion matrices, per-category breakdown, FP/FN taxonomy |
| `docs/audits/technical_evaluation/SYNTAX_TREE_RESULTS.md` | Detailed Section 5.1.2 PARSEVAL results, scoring conventions, lookup audit, mismatch taxonomy |
| `docs/audits/technical_evaluation/EXPLAINABLE_AI_RESULTS.md` | Detailed Section 5.1.3 automated XAI grounding checks, defect audit, human-review protocol |
| `docs/audits/technical_evaluation/EVALUATION_DATASET_INVENTORY.md` | Provenance & contamination audit of all repository and external datasets |
| `docs/audits/technical_evaluation/RAW_PREDICTIONS.csv` | Per-sentence raw predictions across all 476 evaluated sentences |
| `docs/audits/technical_evaluation/METRICS_SUMMARY.csv` | Machine-readable summary of all 66 verified classification metric slices |
| `docs/audits/technical_evaluation/HUMAN_REVIEW_WORKSHEET.csv` | 59 stratified executed SynTutor cases ready for independent dual human review |
| `docs/audits/technical_evaluation/_computed_results.json` | Full structured JSON evidence backing all tables and figures |
| `docs/audits/technical_evaluation/run_technical_evaluation.py` | End-to-end reproducible evaluation script |
| `docs/audits/technical_evaluation/verify_metrics.py` | Independent mathematical & anti-fabrication verifier |
| `docs/audits/technical_evaluation/generate_figures.py` | 300 DPI publication figure generator |
| `docs/audits/technical_evaluation/figures/fig1_confusion_matrix.png` | Figure 1 (2400×1260, 300 DPI) |
| `docs/audits/technical_evaluation/figures/fig2_grammar_detection_performance.png` | Figure 2 (2400×1440, 300 DPI) |
| `docs/audits/technical_evaluation/figures/fig3_per_category_f1.png` | Figure 3 (2400×1560, 300 DPI) |
| `docs/audits/technical_evaluation/figures/fig4_syntax_tree_agreement.png` | Figure 4 (2400×1460, 300 DPI) |
| `docs/audits/technical_evaluation/figures/fig5_explainability_evaluation.png` | Figure 5 (2400×1460, 300 DPI) |
