# SynTutor — Regression Prevention, CI Reliability, and Root-Cause Audit

**Date:** 2026-11-21  
**Repository:** `ybcole/SynTutor`  
**Working Branch:** `fix/syntutor-system-reliability-xai`  
**Base Commit:** `af33b9fd32334f76a4dc4383fe902ad6b6994045` (uncommitted local changes; `main` untouched; no commit/push/PR performed)

---

## 1. Issue Classification Matrix

| # | Investigated Area / Issue | Classification | Resolution / Status |
|---|---|---|---|
| 1 | Invalid YAML indentation in `.github/workflows/syntax-generator-tests.yml` (lines 208–211 at 8 spaces instead of 10 inside `run: \|`) | **Confirmed defect — fixed** | Fixed indentation; validated via `yaml.safe_load()`. |
| 2 | CI workflows not triggering on `main`, `fix/syntutor-system-reliability-xai`, or `fix/*` / `feature/*` branches | **Confirmed defect — fixed** | Updated `on.push.branches` and `on.pull_request.branches` in both workflows (`main`, `milestone-02-syntax-generator`, `fix/*`, `feature/*`). |
| 3 | 10 parser-backed server regression suites missing from CI (`test_cross_layer_consistency`, `test_correction_completeness`, `test_learner_analysis`, `test_nlp_reliability_regressions`, `test_real_world_nlp`, `test_false_positive_regressions`, `test_matrix_remediation`, and 3 CGEL parser probes) | **Confirmed defect — fixed** | Replaced stale manual test list in `syntax-generator-runtime.yml` with automatic discovery (`PYTHONPATH=server CGEL_REQUIRE_PARSER=1 python -m unittest discover -v -s server -p 'test_*.py'`) + `test_corrector.py` + `test_multiline_parse.py`, and installed `requirements-test.txt`. |
| 4 | Frontend JS CI missing `npm run test:quiz-v2`, `npm run test:node-lessons`, and `node --check` on `canvas-view.js`, `explanation-evidence.js`, `ui.js`, `correction.js` | **Confirmed defect — fixed** | Added to `syntax-generator-tests.yml` and verified locally (`23/23` suites pass). |
| 5 | Interactive correction preview (`web/js/main.js`, `web/js/ui.js`) & `recheckFocus()` falsely reporting `"The whole sentence is clean."` / `"this sentence is clean now."` on partial repairs like `Ths cat sleepps.` $\rightarrow$ `Ths cat sleeps.` | **Confirmed defect — fixed** | Added backend `summary['unresolved_tokens']` in `server/analysis_api.py`; consolidated preview impact, impact prose, and recheck messaging into pure shared helpers (`computePreviewImpact`, `formatImpactSummary`, `formatRecheckOutcome`) in `web/js/correction.js`, wired into `web/js/main.js` and `web/js/ui.js`. |
| 6 | Duplicate `C-COPULA` finding emitted in `learner_analysis['findings']` on `I am scares tomorrow.` (`local-1` + `local-2`) | **Confirmed defect — fixed** | Deduplicated by `(code, tuple(targets))` in `server/findings.py` `supported_findings()` so `stored` (with full `related_token_ids=[0, 1]`) is kept once without a duplicate row. |
| 7 | `Ths boys walks.` $\rightarrow$ `Ths boys walk.` falsely marked `whole_sentence_clean: True` because spaCy tagged `Ths` as `PROPN/PERSON` while Benepar tagged it `PRP$` | **Confirmed defect — fixed** | Refined `uncertain_function_words()` in `server/spellcheck.py` so determiner vowel-elisions tagged `DT`/`PRP$` before `NN`/`NNS`/`JJ` (`not known_word`) are flagged even when spaCy guesses `PROPN/PERSON`, while preserving proper-name safety (`Tsh arrived yesterday.`, `Ana`, `Lee`, `Kim`, `Kiyel`, `Brang`). |
| 8 | `Teh cat sleepps.` and `Teh cat sleeps.` triggered `C-ARTICLE`, fabricating nonsensical `"A Teh cat sleeps."` | **Confirmed defect — fixed** | Guarded `_needs_indefinite_article_error()` in `server/matrix.py` against inserting an article before a misspelled/transposed determiner (`teh`, `hte`, `tihs`, `taht`, `tey`, `ths`, `tht`). |
| 9 | Core sentence-level partial revision banner in `web/js/explanation-evidence.js` (`Partial revision — “Ths cat sleeps.” The spelling of “Ths” remains uncertain.`) | **False alarm — no change necessary** | Already correctly implemented prior to this task; preserved untouched. |
| 10 | Core Burton–Roberts bare temporal NP adjunct projection (`tomorrow`), copular Rule `6.25`, empty-node licensing, UI node deselection, lesson/reload state preservation, immediate tutorial, Builder toolbar CSS `[hidden]` fix | **Already resolved before this task** | Verified intact on `af33b9f` and preserved without modification. |
| 11 | `scripts/validate_lessons.py` and `scripts/validate_assessments.py` fail with `Source metadata changed after review` / `Question/source/blueprint content changed after review` | **Outdated test or infrastructure issue** | Pre-existing upstream manifest drift from commit `250b232` on `main` (unrelated to this branch). Assertions kept intact in CI; requires an authorized curriculum review sign-off pass rather than loosening checks. |
| 12 | Legacy Python Playwright scripts `scripts/test_builder_browser.py` and `scripts/test_account_journey_browser.py` reference `#builderTools` / `.sidebar-item[data-view="builder"]` removed in commit `a3a8fdd` | **Outdated test or infrastructure issue** | Pre-existing stale legacy browser tests from before unified Builder/Generator UI (`a3a8fdd`). Active Node Playwright suites (`test_builder_generator_browser.mjs`, `test_quiz_v2_browser.js`, `test_ui_ux_refinements_browser.mjs`, `test_cross_layer_xai_browser.mjs`, `test_interactive_xai_browser.mjs`, `test_real_world_nlp_browser.mjs`) all pass `6/6`. |
| 13 | `scripts/test_foundations_preview_database.js` asserts `11` rows instead of `31`; `scripts/test_gamification_e2e.mjs` imports `'playwright'` directly | **Outdated test or infrastructure issue** | Pre-existing stale test expectations outside this remediation scope. |
| 14 | Human linguistic/pedagogical validation (`HUMAN_REVIEW_WORKSHEET.csv`), CoLA non-pedagogical recall ceiling (`26.00%`), textbook PARSEVAL intermediate `NOM`/`VP` granularity (`68.07%` full / `83.90%` triangle-aware) | **Existing limitation — documented** | Documented transparently; no human adjudication fabricated; no benchmark files altered. |

---

## 2. Confirmed Root Causes & Minimal Fixes

### 2.1 GitHub Actions CI Failures (`.github/workflows/syntax-generator-tests.yml`, `.github/workflows/syntax-generator-runtime.yml`)
- **Root cause:**
  1. `syntax-generator-tests.yml` lines 208–211 were unindented from the `run: |` block (column 9 instead of column 11), causing a hard YAML parse failure (`could not find expected ':'`) before GitHub Actions could schedule any job.
  2. Both workflows listened only to legacy branch names (`milestone-02-syntax-generator`, `feature/milestone-*`), so commits on `main` and `fix/syntutor-system-reliability-xai` never triggered CI automatically.
  3. `syntax-generator-runtime.yml` enumerated a fixed list of 28 test modules, silently omitting 10 newer parser-backed regression suites (including `test_cross_layer_consistency.py`, `test_correction_completeness.py`, `test_learner_analysis.py`, `test_nlp_reliability_regressions.py`, and `test_real_world_nlp.py`), and did not install `requirements-test.txt` (`fastapi`, `httpx`).
- **Fix:**
  - Fixed YAML indentation and added `npm run test:quiz-v2`, `npm run test:node-lessons`, and `node --check` on modified frontend modules in `.github/workflows/syntax-generator-tests.yml`.
  - Enabled `push` and `pull_request` triggers for `main`, `milestone-02-syntax-generator`, `fix/*`, and `feature/*` in both workflows.
  - Replaced the manual server test list in `.github/workflows/syntax-generator-runtime.yml` with automatic discovery (`PYTHONPATH=server CGEL_REQUIRE_PARSER=1 python -m unittest discover -v -s server -p 'test_*.py'`) plus `server/test_corrector.py` and `server/test_multiline_parse.py`, installing `-r requirements.txt -r requirements-test.txt`.

### 2.2 Correction-Preview Consistency (`server/analysis_api.py`, `web/js/correction.js`, `web/js/main.js`, `web/js/ui.js`)
- **Root cause:** Three separate places re-implemented "is the sentence clean?" using inconsistent signals:
  1. `server/analysis_api.py` attached `unresolved_tokens` only to `summary['correction']['impact']`, NOT to `summary` on standalone `/api/parse` calls. When the interactive correction preview called `postParse('Ths cat sleeps.')`, the response had `verdict='grammatical'` and zero rule violations, with no unresolved-spelling signal.
  2. `web/js/main.js` `previewImpact()` computed `whole_sentence_clean = verdict === 'grammatical' && !remaining.length && !introduced.length`, ignoring both unresolved spelling tokens and unresolved syntax trees (`br_analysis.status !== 'normalized'`).
  3. `web/js/main.js` `recheckFocus()` checked only `(payload.summary.violations || []).length === 0` before printing `'That error is fixed — this sentence is clean now.'`.
  4. `web/js/ui.js` `renderCorrection()` and `renderCorrectionPanel()` duplicated impact-summary formatting and omitted `unresolved_tokens` / unverified status when `whole_sentence_clean` was `false`.
- **Fix:**
  - `server/analysis_api.py`: Added additive `summary['unresolved_tokens']` when `unresolved_spelling_tokens(analysis)` is non-empty (omitted when empty; zero breaking contract change).
  - `web/js/correction.js`: Added shared pure functions `computePreviewImpact(originalPayload, previewPayload)`, `formatImpactSummary(impact, { panel })`, and `formatRecheckOutcome(payload)` enforcing a single cross-layer definition of completeness (`verdict === 'grammatical' && !remaining.length && !introduced.length && !unresolvedTokens.length && !treeUnresolved`).
  - `web/js/main.js` & `web/js/ui.js`: Delegated preview impact, recheck messaging, and correction card/panel summaries to those shared functions; `renderCorrection()` now labels partial revisions `'Partial revision'` instead of `'Suggested revision'`.

### 2.3 Duplicate `C-COPULA` Finding (`server/findings.py`)
- **Root cause:** `supported_findings()` iterated `[*stored, detail]` and keyed deduplication on `(lesson or code, tuple(targets), tuple(participants))`. On `I am scares tomorrow.`, `stored[0]` had `participants=(0, 1)` while the promoted `detail` had a different participant tuple, causing `learner_analysis['findings']` to contain two identical `C-COPULA` findings on token `[2]`.
- **Fix:** Added `(code, tuple(targets))` to the `seen` deduplication set in `server/findings.py` so `stored` (carrying full `related_token_ids`) is retained once and duplicate entries are suppressed.

### 2.4 Uncertain Determiner & `C-ARTICLE` Interaction (`server/spellcheck.py`, `server/matrix.py`)
- **Root cause:**
  1. On `Ths boys walk.`, Benepar tagged `Ths` as `PRP$` (closed-class determiner), while spaCy tagged `fpos='PROPN', fentity='PERSON'`. `uncertain_function_words()` checked `not has_name_evidence(node)` unconditionally, missing `Ths` and marking `Ths boys walks.` $\rightarrow$ `Ths boys walk.` as `whole_sentence_clean: True`.
  2. On `Teh cat sleepps.` and `Teh cat sleeps.`, `_needs_indefinite_article_error()` in `server/matrix.py` saw `(NP (NNP Teh) (NN cat))` without a `DT` and fired `C-ARTICLE`, causing the corrector to fabricate `"A Teh cat sleeps."`.
- **Fix:**
  - `server/spellcheck.py`: Allowed determiner vowel-elisions tagged `DT`/`PRP$` (`not known_word`) immediately before `NN`/`NNS`/`JJ` to be reported by `uncertain_function_words()` even if spaCy guesses `PROPN/PERSON` (real proper names like `Tsh arrived yesterday.`, `Ana`, `Lee`, `Kim`, `Kiyel`, `Brang` remain unaffected).
  - `server/matrix.py`: Exempted multi-word NPs whose leading token is a misspelled/transposed determiner (`teh`, `hte`, `tihs`, `taht`, `tey`, `ths`, `tht`) from `C-ARTICLE` article insertion.

---

## 3. Files Modified

| File | Justification |
|---|---|
| `.github/workflows/syntax-generator-tests.yml` | Fix YAML syntax error (lines 208–211), add branch triggers, include `test:quiz-v2`, `test:node-lessons`, and JS syntax checks. |
| `.github/workflows/syntax-generator-runtime.yml` | Add branch triggers, install `requirements-test.txt`, switch to automatic `unittest discover` for all `server/test_*.py` suites + `test_corrector.py` + `test_multiline_parse.py`. |
| `server/analysis_api.py` | Expose additive `summary['unresolved_tokens']` so standalone parses and interactive previews share the same uncertainty signal. |
| `server/findings.py` | Deduplicate findings by `(code, tuple(targets))` to eliminate duplicate `C-COPULA` entries. |
| `server/spellcheck.py` | Detect determiner vowel-elisions tagged `DT`/`PRP$` before nouns (`Ths boys walk.`) while protecting proper names. |
| `server/matrix.py` | Prevent `C-ARTICLE` from inserting `'A '` before misspelled/transposed determiners (`Teh cat sleepps.`). |
| `web/js/correction.js` | Add single-source-of-truth `computePreviewImpact()`, `formatImpactSummary()`, and `formatRecheckOutcome()`. |
| `web/js/main.js` | Use shared `computePreviewImpact()` and `formatRecheckOutcome()` (bumping module cache query string to `?v=2026.11.21b`). |
| `web/js/ui.js` | Use shared `formatImpactSummary()` in both `renderCorrection()` and `renderCorrectionPanel()`; distinguish `'Partial revision'` from `'Suggested revision'`. |
| `scripts/test_correction.js` | Add model-free unit regression tests for complete, partial (`Ths`), unverified/unresolved-tree, and multi-error correction previews and rechecks. |
| `server/test_correction_completeness.py` | Add parser-backed regression tests for `Ths boys walks.`, `Teh cat sleepps.` / `Teh cat sleeps.`, standalone `summary['unresolved_tokens']`, and non-duplicated `C-COPULA` on `I am scares tomorrow.`. |
| `scripts/test_interactive_xai_browser.mjs` | Add live Chromium assertions verifying `Ths cat sleepps.` never claims `"clean"`, standalone `Ths cat sleeps.` exposes `unresolved_tokens`, and `Teh cat sleepps.` never fabricates `"A Teh cat sleeps."`. |

---

## 4. Verification Execution Results (Local vs. GitHub Actions)

> **Execution Scope Disclosure:** All checks below were executed **locally** on `macOS-15.8.2-arm64` (Python `3.11.17`, Node `v26.12.0`). **GitHub-hosted Actions execution has NOT been verified yet** because pushing to GitHub is prohibited during this task; once changes are reviewed and pushed, GitHub Actions will automatically trigger on `fix/syntutor-system-reliability-xai`.

| Check / Command | Environment | Result | Details |
|---|---|---|---|
| `yaml.safe_load()` on `.github/workflows/syntax-generator-tests.yml` and `syntax-generator-runtime.yml` | Local | **PASS** | Both workflow files parse as valid YAML. |
| `node --check web/js/{main,ui,correction,canvas-view,explanation-evidence}.js` | Local | **PASS** | Zero JS syntax errors. |
| `npm run test:evidence && npm run test:legacy-map && npm run test:node-lessons && node scripts/test_explanation_dedupe.js && npm run test:correction && npm run test:quiz && npm run test:quiz-v2 && npm run test:lessons && npm run test:assessments && npm run test:builder && node scripts/test_level.js && node scripts/test_tree_layout.js && node scripts/test_xai7_focus.mjs && node scripts/test_learner_explanations.mjs && node scripts/test_account_integration.js` | Local | **PASS** | **23/23** frontend JS, PostgreSQL (PGlite), and account integration suites passed (exact expanded CI command). |
| `PYTHONPATH=server HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false CGEL_REQUIRE_PARSER=1 .venv/bin/python -m unittest discover -s server -p 'test_*.py'` | Local | **PASS** | **978/978** tests passed in `192.73s` (`0` failures, `0` errors, `0` skipped — exact auto-discovered CI command). |
| `server/test_corrector.py` & `server/test_multiline_parse.py` | Local | **PASS** | All `9/9` corrector checks and LF/CRLF multiline parser regression passed. |
| `.venv/bin/python docs/audits/technical_evaluation/verify_metrics.py` | Local | **PASS** | **74/74** metric and integrity checks passed (`HUMAN_REVIEW_WORKSHEET.csv`: 56 rows, all 17 human rating columns blank/unfabricated). |
| All 6 Chromium Playwright suites (`test_ui_ux_refinements_browser.mjs`, `test_cross_layer_xai_browser.mjs`, `test_interactive_xai_browser.mjs`, `test_real_world_nlp_browser.mjs`, `test_builder_generator_browser.mjs`, `test_quiz_v2_browser.js`) | Local (live Flask `:8769` + Chromium) | **PASS** | **6/6** browser suites passed with `0` page errors. |
| Model-free CI scripts spot-check (`tools/migrate_diagnostics.py`, `tools/validate_cgel_rules.py`, `tools/ledger.py`, `test_foundations_preview_catalog.py`, `validate_builder_contracts.py`, `test_static_build.py`, `test_runtime_packaging.py`, `audit_burton_roberts_import.py`, `audit_br_native_catalog.py`, `audit_learner_explanations.py`, `server/test_licensing.py`) | Local | **11/11 PASS** | Two pre-existing upstream scripts (`scripts/validate_lessons.py`, `scripts/validate_assessments.py`) fail on manifest drift from `main` commit `250b232` (not altered here). |
| GitHub-hosted Actions runners (`ubuntu-latest` with `postgres:16`) | GitHub Actions | **NOT YET EXECUTED** | Requires pushing branch changes after review; cannot be verified locally without pushing. |

---

## 5. Benchmark Impact Assessment

- **Historical benchmark files (`RAW_PREDICTIONS.csv`, `METRICS_SUMMARY.csv`, `FROZEN_INDEPENDENT_EVAL_V4.csv`, `docs/audits/technical_evaluation/real_world_reliability/`, `remediation_run_2026-11-21/`):** Untouched (`verify_metrics.py`: `74/74` PASS).
- **Behavioral scope of code changes:** The 4 targeted runtime changes (`summary['unresolved_tokens']`, `supported_findings` `(code, targets)` dedupe, `uncertain_function_words` `DT`/`PRP$` pre-nominal guard, and `_needs_indefinite_article_error` transposed-determiner guard) affect only misspelled/transposed determiners (`Ths`, `Teh`) and duplicate `C-COPULA` suppression; they do not alter rule verdicts on standard grammatical/ungrammatical BLiMP/JFLEG/CoLA controls or Burton–Roberts canonical tree projection.

---

## 6. Remaining Unresolved Issues & Recommendations for Preventing Recurrence

1. **Upstream Review-Manifest Drift (`scripts/validate_lessons.py`, `scripts/validate_assessments.py`):** Both fail on `main` (`250b232`) because lesson/assessment content was edited after the review hash was recorded. When `syntax-generator-tests.yml` runs on GitHub Actions (now that its YAML syntax error is fixed!), these two checks will surface loudly as expected rather than being silently hidden by broken YAML. Resolution requires an authorized instructor/owner curriculum review re-sign-off, NOT weakening the validators.
2. **Legacy Python Playwright Scripts (`scripts/test_builder_browser.py`, `scripts/test_account_journey_browser.py`):** Both reference `#builderTools` / `.sidebar-item[data-view="builder"]` removed in commit `a3a8fdd`. They should either be modernized to the unified `#exploreBuilderBtn` + `.builder-menu` UI or retired once the 6 passing Node Playwright suites are wired into CI.
3. **Single Source of Truth for Cross-Layer Contracts:** Keep grammatical/spelling completeness logic centralized (backend `unresolved_spelling_tokens` $\rightarrow$ `summary['unresolved_tokens']` & `correction.impact` $\rightarrow$ frontend `web/js/correction.js` helpers) so UI components never re-derive `"clean"` status independently.
4. **Automatic Test Discovery as Default:** Maintaining `unittest discover -s server -p 'test_*.py'` in `syntax-generator-runtime.yml` guarantees every newly added backend regression file automatically executes in CI without manual YAML list updates.
5. **Human Validation Remains Open:** Automated tests verify structural, rule, and contract invariants only; real human linguistic and pedagogical adjudication on `HUMAN_REVIEW_WORKSHEET.csv` remains required before making human-validated educational claims.
