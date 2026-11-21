# SynTutor System Reliability Final Check

**Date:** 2026-11-21  
**Branch:** `fix/syntutor-system-reliability-xai`  
**Base Checkpoint Commit:** `f96a68dee220b8ac6b65f3b2fc43d8968648c7f7` (working tree dirty with verified remediation changes; no commit, push, merge, rebase, reset, or discard performed)  
**New Timestamped Archive:** `docs/audits/technical_evaluation/remediation_run_2026-11-21/`  
**Historical Baseline (Untouched):** `docs/audits/technical_evaluation/real_world_reliability/`

---

## 1. Executive Summary

This remediation pass addressed four reliability priorities on `fix/syntutor-system-reliability-xai` while preserving all earlier UI/UX refinements, cross-layer linguistic consistency fixes, model weights, canonical schema (`docs/canonical-burton-roberts-tree.schema.json`), API contracts, and historical evaluation artifacts:

1. **Correction Completeness vs. Safety (Priority A):**
   - Reproduced `Ths cat sleepps.` $\rightarrow$ `Ths cat sleeps.`. Confirmed that leaving sentence-initial 3-letter `Ths` unedited is **intended conservative safety behavior** because `Ths` is genuinely ambiguous between `This` and `The` and overlaps the protected capitalized-name/short-token envelope.
   - Fixed three genuine defects exposed during the investigation:
     1. **Latent lexicon bug (`server/spellcheck.py`):** `_morph_variants()` stripped `-s` from 3-letter words (`len(w) > 2`), reducing `ths` $\rightarrow$ `th` (which exists in macOS `/usr/share/dict/words`), causing `known_word('Ths')` to falsely return `True`. Tightened `-s` stripping to `len(w) > 3` and added an exact high-frequency SymSpell dictionary lookup ($\text{count} \ge 1{,}000{,}000$) in `known_word()` so common inflected short words missing from Webster's 1934 `/usr/share/dict/words` (`has`, `was`, `his`, `its`, `cafes`) remain known without admitting nonsense (`ths`, `teh`, `sleepps`).
     2. **Incomplete partial-revision detection (`server/spellcheck.py`, `server/analysis_api.py`):** Expanded `uncertain_function_words()` to detect transposed determiners (`teh`, `hte`, `tihs`, `taht`, `tey`) in determiner/pre-nominal positions, added `unresolved_spelling_tokens()` combining uncertain closed-class words with unedited lowercase OOV typos (while preserving capitalized proper names and split contraction stems such as `does` + `n't`), and exposed `correction.impact.completeness` (`"complete"` vs. `"partial"`).
     3. **Audit metric conflation (`docs/audits/technical_evaluation/run_cycle8_evaluation.py`, `run_real_world_reliability.py`):** Updated `audit_correction_safety()` to explicitly distinguish `independent_morph_syntax_clean` (which checks newly introduced defects only and skips unchanged original words) from `spelling_complete`, `correction_completeness` (`"complete"` vs. `"partial_review_required"`), `remaining_uncertain_tokens`, and an explicit `completeness_note`.
2. **Modernization of Stale Browser Suites + Live CSS Bug Caught (Priority B):**
   - Modernized `scripts/test_quiz_v2_browser.js` and `scripts/test_builder_generator_browser.mjs` from obsolete `.sidebar-item[data-view="builder"]` / `history` / `#builderPalette` expectations (removed when the UI unified Syntax Generator and Builder in commit `a3a8fdd`) to the current 5-item sidebar (`tutor`, `lessons`, `quizzes`, `leaderboard`, `achievements`), `#exploreBuilderBtn` combined Syntax Builder mode, and right-click `.builder-menu` node insertion, preserving all substantive functional assertions.
   - Running the modernized Builder browser suite uncovered a **genuine CSS specificity regression** in `web/css/style.css`: `#builderToolbar.canonical-zoom button { display: inline-flex; }` overrode `[hidden]` on `[data-builder-construct]` and `#combinedBuilderClear`. Fixed by adding explicit `[hidden] { display: none; }` rules at matching specificity.
3. **Timestamped Benchmark Archive & Reconciliation (Priority C):**
   - Re-ran `docs/audits/technical_evaluation/run_real_world_reliability.py` into a brand-new directory `docs/audits/technical_evaluation/remediation_run_2026-11-21/` with full environment/model/Git/SHA-256 provenance in `provenance.json`.
   - Every single metric delta vs. the untouched historical snapshot (`docs/audits/technical_evaluation/real_world_reliability/`) is reconciled down to individual sentence IDs (`eval4-jfleg-003-u`, `eval4-blimp-043-g`, and 5 textbook PARSEVAL records).
4. **Full Post-Edit Verification (Priority D):**
   - **976/976** Python server tests PASS under `CGEL_REQUIRE_PARSER=1` (`0` failures, `0` errors, `0` skipped).
   - **9/9** `server/test_corrector.py` regression checks PASS.
   - **74/74** `docs/audits/technical_evaluation/verify_metrics.py` integrity checks PASS (`HUMAN_REVIEW_WORKSHEET.csv` confirmed 100% blank / unfabricated).
   - **23/23** non-browser frontend JS unit, PostgreSQL DB, and account integration suites PASS.
   - **6/6** live Chromium Playwright browser suites PASS (`0` page/console errors).

---

## 2. Changed Files Inventory (Current Working Tree vs. `f96a68d`)

### Priority A — Correction Completeness & Safety
- `server/spellcheck.py`: Tightened `-s` morphological stripping (`len(w) > 3`), added high-frequency SymSpell fallback in `known_word()`, expanded `uncertain_function_words()` for transposed determiners, added `unresolved_spelling_tokens()` with contraction-stem preservation.
- `server/analysis_api.py`: Switched post-repair uncertainty check to `unresolved_spelling_tokens()` and added explicit `correction['impact']['completeness']` (`'complete'` | `'partial'`).
- `server/test_correction_completeness.py` *(new)*: Regression suite covering `Ths cat sleepps.`, `The cat sleepps.`, already-correct controls, capitalized proper names (`Ana`, `Lee`, `Kim`, `Kiyel`, `Brang`, `Tsh`), `Teh cat sleepps.`, repaired contractions (`Naomi doesnt know the answer.`, `They didnt arrive.`), multi-error inputs, and `audit_correction_safety()` completeness metadata.
- `docs/audits/technical_evaluation/run_cycle8_evaluation.py`: Extended `audit_correction_safety()` with `spelling_complete`, `correction_completeness`, `remaining_uncertain_tokens`, `completeness_note`, and apostrophe-aware word tokenization (`[A-Za-z]+(?:['’][A-Za-z]+)?`).
- `docs/audits/technical_evaluation/run_real_world_reliability.py`: Propagated `correction.impact.whole_sentence_clean` and `unresolved_tokens` into `correction-audit.json`.

### Priority B — Browser Test Modernization & CSS Fix
- `web/css/style.css`: Fixed `[hidden]` display override on `#builderToolbar.canonical-zoom button[hidden]`, `.builder-top-left button[hidden]`, `.builder-nodes-toggle[hidden]`, `.explore-builder-btn[hidden]`.
- `scripts/test_quiz_v2_browser.js`: Updated sidebar inventory and mobile drawer navigation checks to current 5-item navigation (`tutor`, `lessons`, `quizzes`, `leaderboard`, `achievements`) + `#exploreBuilderBtn` integrated Builder mode + immediate onboarding dismissal.
- `scripts/test_builder_generator_browser.mjs`: Updated Builder section and combined-studio checks to `#exploreBuilderBtn`, right-click `.builder-menu`, inline canvas word editor (`.builder-inline-input`), versioned `syntax-builder-ui.js?v=2026.11.18f` module import, and generator-notation `parentAnchorOf()` dot alignment while preserving all generator, Fit, connector-drag, wide-Fit, mobile dark, and Lessons `br-01/02/07/08` assertions.

### Previously Completed on Branch (Preserved & Re-Verified)
- `server/ruleset.py`, `server/findings.py`, `server/final_d1_projection.py`, `server/learner_explanations.py`, `server/test_learner_analysis.py`, `server/test_cross_layer_consistency.py`
- `web/js/canvas-view.js`, `web/js/explanation-evidence.js`, `web/js/main.js`, `web/index.html`
- `scripts/test_ui_ux_refinements_browser.mjs`, `scripts/test_cross_layer_xai_browser.mjs`
- `docs/audits/SYNTUTOR_ANTIGRAVITY_CONTINUATION_REPORT.md`, `docs/audits/SYNTUTOR_CROSS_LAYER_LINGUISTIC_CONSISTENCY.md`, `docs/audits/SYNTUTOR_CONTINUOUS_RELIABILITY_PROGRESS.md`

---

## 3. Before / After Behavioral Examples

| Input Sentence | Historical / Before | Current Verified Output | Safety / Completeness Classification |
|---|---|---|---|
| `Ths cat sleepps.` | `known_word('Ths') == True` (via `ths -> th`); `correction-audit.json` reported `independent_morph_syntax_clean: true` with no completeness field | `corrected_sentence: "Ths cat sleeps."`; `whole_sentence_clean: false`; `completeness: "partial"`; `unresolved_tokens: [{"token_id": 0, "surface": "Ths"}]`; audit: `independent_morph_syntax_clean: true`, `spelling_complete: false`, `correction_completeness: "partial_review_required"`, `remaining_uncertain_tokens: ["Ths"]` | Conservative non-edit preserved; partial repair explicitly disclosed to learners and audit |
| `The cat sleepps.` | `The cat sleeps.` | `corrected_sentence: "The cat sleeps."`; `whole_sentence_clean: true`; `completeness: "complete"`; `unresolved_tokens: []` | Complete safe repair |
| `Teh cat sleepps.` | Transposed `Teh` missed by `uncertain_function_words` | Flagged as partial (`whole_sentence_clean: false`, `completeness: "partial"`, `unresolved_tokens` includes `Teh`) whenever repaired partially | No false completeness claim |
| `Naomi doesnt know the answer.` | Audit regex split `doesn't` $\rightarrow$ `doesn`, falsely flagging partial | `corrected_sentence: "Naomi doesn't know the answer."`; `whole_sentence_clean: true`; `completeness: "complete"`; audit: `spelling_complete: true`, `remaining_uncertain_tokens: []` | Complete safe contraction repair |
| `The cat sleeps.` / `Ana sleeps.` / `Kiyel arrived yesterday.` / `Tsh arrived yesterday.` | Protected | `corrected_sentence: null`, `findings: []` | Already-correct sentences and capitalized proper names never rewritten |
| `I am scares tomorrow.` | Fabricated `PP -> P[E]` on `tomorrow`; category/function contradiction on `scares` | `tomorrow` projected as bare temporal NP; Rule `6.25` (`C-COPULA`) flags copula + bare plural noun conflict; consistent local explanation and lesson routing | Cross-layer linguistic consistency preserved |

---

## 4. Benchmark Reconciliation & Provenance (Historical Snapshot vs. New Archive)

All figures below were read directly from JSON/CSV outputs in:
- **Historical Snapshot (untouched):** `docs/audits/technical_evaluation/real_world_reliability/`
- **New Timestamped Archive:** `docs/audits/technical_evaluation/remediation_run_2026-11-21/`

### 4.1 Real-World Diagnostic Probes (`diagnostic_cases.json`)
> **Important Methodological Distinction:** `diagnostic_cases.json` contains **73 total probes**: **62 gold-labeled scored cases** (28 ungrammatical, 34 grammatical), **2 rejected unsupported inputs** (`unsupported_input`), and **9 unlabeled exploratory/edge cases**. All diagnostic probes informed development and are reported strictly as diagnostic checks, not blind generalization.

| Metric | Historical Snapshot (`real_world_reliability/`) | New Archive (`remediation_run_2026-11-21/`) | Notes |
|---|---:|---:|---|
| Total probes / Gold-labeled scored | 73 / 62 (28U, 34G) | 73 / 62 (28U, 34G) | Identical frozen probe set |
| Strict Rules (`n_evaluated` / Accuracy / F1) | 62 / 100.00% / 100.00% (`3` unverified G treated non-error) | 62 / 100.00% / 100.00% (`3` unverified G treated non-error) | 0 FP, 0 FN |
| Hybrid Decisive (`n_evaluated` / `n_unverified` / Coverage / Acc / F1) | 58 / 4 / 93.55% / 100.00% / 100.00% | 58 / 4 / 93.55% / 100.00% / 100.00% | 4 grammatical controls abstained (`unverified`), not scored as errors |
| Tree status (`normalized` / `unresolved` / `unsupported_input`) | 42 / 29 (27 working trees) / 2 | 42 / 29 (27 working trees) / 2 | 0 schema failures, 0 misaligned offsets |
| Exposed repairs / Repairs on labeled grammatical controls | 16 / 0 | 16 / 0 | Zero false rewrites on grammatical controls |
| Automated repair audit: `independent_morph_syntax_clean` | 16 / 16 (completeness not tracked) | 16 / 16 | Checks newly introduced defects only |
| Automated repair audit: `spelling_complete` vs. `partial_review_required` | Not tracked | **15 / 16 complete**, **1 / 16 partial** (`Ths cat sleepps.` $\rightarrow$ `Ths cat sleeps.`, unresolved: `['Ths']`) | Honest completeness disclosure |
| Warm probe latency (median / p95) | 188.03 ms / 384.12 ms | 146.99 ms / 393.66 ms | Local Apple Silicon CPU run |

### 4.2 Frozen Eval V4 (`FROZEN_INDEPENDENT_EVAL_V4.csv`, $n=360$)
> **Important Methodological Distinction:** In `rules` strict evaluation, `unverified` is counted as non-ungrammatical (`coverage = 100%`). In `hybrid` decisive evaluation, `unverified` items are **abstentions** excluded from accuracy/F1 and reported explicitly alongside decisive coverage (`n_evaluated / n_total`).

| Split | Mode | Historical Snapshot (`real_world_reliability/`) | New Archive (`remediation_run_2026-11-21/`) | Exact Cause of Delta |
|---|---|---:|---:|---|
| **Primary (`n=260`: BLiMP + JFLEG)** | Rules strict | Acc `85.00%`, P `94.17%`, R `74.62%`, F1 `83.26%` (TP 97, FP 6, FN 33, TN 124) | Acc **`85.38%`**, P **`94.23%`**, R **`75.38%`**, F1 **`83.76%`** (TP 98, FP 6, FN 32, TN 124) | `eval4-jfleg-003-u` (`brang`) recovered (`unverified -> ungrammatical`, `C-VERB-FORM`) |
| **Primary (`n=260`)** | Hybrid decisive | Eval `239` (`21` unver, cov `91.92%`), Acc `89.12%`, F1 `88.18%` (TP 97, FP 6, FN 20, TN 116) | Eval **`241`** (**`19`** unver, cov **`92.69%`**), Acc **`89.21%`**, F1 **`88.29%`** (TP 98, FP 6, FN 20, TN 117) | `eval4-jfleg-003-u` (+1 TP, -1 unver) + `eval4-blimp-043-g` (+1 TN, -1 unver) |
| **BLiMP (`n=240`)** | Rules strict | Acc `85.42%`, P `95.70%`, R `74.17%`, F1 `83.57%` (TP 89, FP 4, FN 31, TN 116) | Acc `85.42%`, P `95.70%`, R `74.17%`, F1 `83.57%` (TP 89, FP 4, FN 31, TN 116) | Unchanged |
| **BLiMP (`n=240`)** | Hybrid decisive | Eval `221` (`19` unver, cov `92.08%`), Acc `89.59%`, F1 `88.56%` (TP 89, FP 4, FN 19, TN 109) | Eval **`222`** (**`18`** unver, cov **`92.50%`**), Acc **`89.64%`**, F1 `88.56%` (TP 89, FP 4, FN 19, TN 110) | `eval4-blimp-043-g` (*"Carmen finds out that the customers have run around many cafes."*) no longer falsely OOV-abstained once `known_word('cafes')` consulted SymSpell |
| **JFLEG (`n=20`)** | Rules strict | Acc `80.00%`, P `80.00%`, R `80.00%`, F1 `80.00%` (TP 8, FP 2, FN 2, TN 8) | Acc **`85.00%`**, P **`81.82%`**, R **`90.00%`**, F1 **`85.71%`** (TP 9, FP 2, FN 1, TN 8) | `eval4-jfleg-003-u` (*"...why he always brang bad marks at home ."*) recovered by `C-VERB-FORM` |
| **JFLEG (`n=20`)** | Hybrid decisive | Eval `18` (`2` unver, cov `90.00%`), Acc `83.33%`, F1 `84.21%` (TP 8, FP 2, FN 1, TN 7) | Eval **`19`** (**`1`** unver, cov **`95.00%`**), Acc **`84.21%`**, F1 **`85.71%`** (TP 9, FP 2, FN 1, TN 7) | Same (`eval4-jfleg-003-u`) |
| **CoLA (`n=100`, rules-only sensitivity)** | Rules strict | Acc `61.00%`, P `86.67%`, R `26.00%`, F1 `40.00%` (TP 13, FP 2, FN 37, TN 48) | Acc `61.00%`, P `86.67%`, R `26.00%`, F1 `40.00%` (TP 13, FP 2, FN 37, TN 48) | Unchanged (expected low recall on non-pedagogical CoLA phenomena) |
| **CoLA (`n=100`)** | Hybrid decisive | Eval `88` (`12` unver, cov `88.00%`), Acc `68.18%`, F1 `48.15%` | Eval `88` (`12` unver, cov `88.00%`), Acc `68.18%`, F1 `48.15%` | Unchanged |
| **Tree Normalization (`primary`, `n=260`)** | `FINAL-D1` | `209/260` (`80.38%`), working fallback `51`, schema valid `209/209` | `209/260` (`80.38%`), working fallback `51`, schema valid `209/209` | Normalization rate ≠ tree correctness |

### 4.3 Textbook Structural PARSEVAL (Burton–Roberts IMG Corpus, $n=216$, Lookup-Bypassed)
> **Important Methodological Distinction:** Normalization rate (`200/216 = 92.59%`) measures schema-valid `FINAL-D1` projection coverage; **structural tree correctness** is measured by PARSEVAL over the `185` yield-aligned normalized trees (`16` working fallbacks, `15` yield-misaligned).

| Metric | Historical Snapshot (`real_world_reliability/`) | New Archive (`remediation_run_2026-11-21/`) | Exact Cause of Delta |
|---|---:|---:|---|
| Normalized / Working Fallback / Yield-Aligned | `200/216` (`92.59%`) / `16` / `185` | `200/216` (`92.59%`) / `16` / `185` | Same coverage |
| **Full PARSEVAL:** Labeled P / R / F1 | `55.16%` / `88.67%` / `68.01%` | **`55.27%`** / `88.57%` / **`68.07%`** | Removing fabricated `PP -> P[E]` on bare temporal NPs removed 5 spurious `PP` nodes across `ch5-d3`, `ch5-ex2c`, `ch6-69`, `ch6-ex3a`, `ch8-ex2-d` (`pred_constituents` `1617 -> 1612`; note `ch6-69` gold had a `PP` span `[7,9]`, shifting `labeled_matches` `892 -> 891`) |
| **Full PARSEVAL:** Unlabeled P / R / F1 | `58.57%` / `94.14%` / `72.21%` | **`58.75%`** / `94.14%` / **`72.35%`** | +0.14 pp UF1 |
| **Triangle-Aware PARSEVAL:** Labeled P / R / F1 | `79.43%` / `88.67%` / `83.80%` | **`79.70%`** / `88.57%` / **`83.90%`** | +0.10 pp LF1 |
| **Triangle-Aware PARSEVAL:** Unlabeled P / R / F1 | `84.33%` / `94.14%` / `88.96%` | **`84.70%`** / `94.14%` / **`89.17%`** | +0.21 pp UF1 |
| **Triangle-Aware Exact Matches** | `98 / 185` (`52.97%` aligned; `45.37%` of 216) | **`99 / 185`** (**`53.51%`** aligned; **`45.83%`** of 216) | +1 exact textbook match |

### 4.4 Environment, Model Versions & Provenance (`provenance.json`)
Full SHA-256 hashes of all 20 modified/new source files, 3 frozen input files, and 6 archive outputs are archived in `docs/audits/technical_evaluation/remediation_run_2026-11-21/provenance.json`:
- **Python:** `3.11.17` on `macOS-15.8.2-arm64-arm-64bit`
- **Node.js:** `v26.12.0`
- **Core NLP & Runtime Packages:** `spacy 3.8.16`, `en-core-web-md 3.8.0`, `benepar 0.2.0` (`benepar_en3`), `transformers 4.46.3`, `torch 2.15.0`, `torch-struct 0.5`, `symspellpy 6.10.2`, `flask 3.1.3`, `fastapi 0.165.0`, `jsonschema 4.26.0`
- **Frozen Input SHA-256 Digests:**
  - `FROZEN_INDEPENDENT_EVAL_V4.csv`: `1d468942f7e9886039fa1c77df55668609e1cac1b70fcbcda0da8f2c0f0b4fe6`
  - `real_world_reliability/diagnostic_cases.json`: `395506c0cf19044a0f041f8caf3fab0d85ed8f11e04386019f7d53af3ab3d3b3`
  - `docs/canonical-burton-roberts-tree.schema.json`: `e42b7e27f123541a39b055b26d43a1f54a67238d926cbeaf9f658c74a0a33e0e`

---

## 5. Post-Edit Regression Verification Matrix

All checks below were executed **after the final code edit**:

| Suite / Command | Result | Details |
|---|---|---|
| `PYTHONPATH=server HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false CGEL_REQUIRE_PARSER=1 .venv/bin/python -m unittest discover -s server -p "test_*.py"` | **PASS** | **976/976** tests OK in `239.47s` (`0` failures, `0` errors, `0` skipped) |
| `PYTHONPATH=server HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false CGEL_REQUIRE_PARSER=1 .venv/bin/python server/test_corrector.py` | **PASS** | `9/9` corrector assertions passed |
| `.venv/bin/python docs/audits/technical_evaluation/verify_metrics.py` | **PASS** | `74/74` metric & integrity checks verified (`HUMAN_REVIEW_WORKSHEET.csv`: 56 rows, all 17 human rating columns blank/unfabricated) |
| 19 non-browser frontend JS/MJS unit suites (`test_assessment_core`, `test_builder_core`, `test_correction`, `test_explanation_dedupe`, `test_explanation_evidence`, `test_foundation_progress`, `test_learner_explanations`, `test_legacy_node_map`, `test_lesson_progress`, `test_level`, `test_node_lesson_map`, `test_quiz_digest_freshness`, `test_quiz_formal`, `test_quiz_lesson_practice`, `test_quiz_refinements`, `test_quiz_v2`, `test_tree_layout`, `test_tree_quiz`, `test_xai7_focus`) | **PASS** | **19/19** passed |
| PostgreSQL (PGlite) DB & Account Integration suites (`test_account_integration.js`, `test_assessment_database.js`, `test_lesson_database.js`, `test_quiz_v2_database.js`) | **PASS** | **4/4** passed |
| `QUIZ_V2_PLAYWRIGHT_MODULE=... node scripts/test_quiz_v2_browser.js` | **PASS** | All 11 Syntax + 20 Cambridge chapters, quizzes, drafts, reviews, account isolation, 390/768/1360px light/dark, mobile drawer + integrated Builder; `0` errors |
| `QUIZ_V2_PLAYWRIGHT_MODULE=... node scripts/test_builder_generator_browser.mjs` | **PASS** | Generator Enter/Shift+Enter/blank guard, unified Builder toolbar + right-click `.builder-menu`/search/help + Fit + connector alignment + drag + wide Fit + mobile dark, Lessons `br-01/02/07/08`, combined Studio transfer/switches/Clear/teardown; `0` errors |
| `QUIZ_V2_PLAYWRIGHT_MODULE=... node scripts/test_ui_ux_refinements_browser.mjs http://127.0.0.1:8769` | **PASS** | Node deselection, lesson/reload state preservation, immediate tutorial, button consistency (desktop + mobile) |
| `QUIZ_V2_PLAYWRIGHT_MODULE=... node scripts/test_cross_layer_xai_browser.mjs http://127.0.0.1:8769` | **PASS** | Live Flask + Chromium cross-layer consistency, empty-node licensing, explanations, corrections, lesson routing |
| `QUIZ_V2_PLAYWRIGHT_MODULE=... node scripts/test_interactive_xai_browser.mjs http://127.0.0.1:8769` | **PASS** | Live Chromium interactive XAI, evidence propagation, highlighting, partial revisions, state reset |
| `QUIZ_V2_PLAYWRIGHT_MODULE=... node scripts/test_real_world_nlp_browser.mjs http://127.0.0.1:8769` | **PASS** | Live Flask browser parity, Unicode selection, rejected input, rapid submissions |

---

## 6. Open Risks, Unresolved Items & Honest Disclosures

1. **Human Linguistic & Pedagogical Validation Not Yet Performed:** All automated checks (`independent_morph_syntax_clean`, `spelling_complete`, PARSEVAL, rule/hybrid accuracy) are algorithmic checks only. `docs/audits/technical_evaluation/HUMAN_REVIEW_WORKSHEET.csv` retains all 17 human adjudication columns blank; no human expert or learner study claims may be made until real human adjudication is completed.
2. **CoLA Recall Ceiling (`26.00%` rules-only):** SynTutor's pedagogical rule matrix targets classroom-documented English grammar constraints and does not attempt general linguistic acceptability modeling for arbitrary theoretical CoLA phenomena (e.g., island/binding/semantic-pragmatic edge cases).
3. **Textbook Structural PARSEVAL Gap (`68.07%` full LF1 / `83.90%` triangle-aware LF1):** Over-segmentation into intermediate `NOM`/`VP` projections relative to textbook flat/abbreviated diagrams accounts for most precision loss (`total_extra_nom_or_bar = 261` full / `90` triangle-aware); `16/216` textbook sentences still fall back to working trees rather than full `FINAL-D1` normalization.
4. **Ambiguous Short/Capitalized Typos Remain Conservatively Unedited:** Tokens such as sentence-initial `Ths` (`This` vs. `The`) are intentionally left unedited to avoid rewriting proper names (`Tsh`, `Ana`, `Lee`, `Kim`, `Brang`) or guessing intent. They are now explicitly marked as partial (`completeness: "partial"` / `partial_review_required`) rather than silently treated as complete.
5. **Pre-Existing Out-of-Scope Legacy Scripts:**
   - `scripts/test_foundations_preview_database.js` fails on a pre-existing stale count assertion (`31 !== 11`) from before the 20 Cambridge chapters were added to `foundation_assessments`.
   - `scripts/test_gamification_e2e.mjs` imports `'playwright'` directly rather than honoring `QUIZ_V2_PLAYWRIGHT_MODULE`, so it requires a local `node_modules/playwright` installation to run.
   - Untracked `repomix-output.xml` remains untouched in the working tree as requested.
