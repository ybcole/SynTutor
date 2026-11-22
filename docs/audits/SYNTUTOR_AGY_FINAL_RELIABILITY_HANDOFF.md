# SynTutor — Final Reliability Remediation and CI Stabilization Handoff

**Repository:** `ybcole/SynTutor`  
**Working Branch:** `fix/syntutor-system-reliability-xai`  
**Base Commit:** `5451d72752b7919f9d10f4c63c0e0981d7b8a978` (local modifications uncommitted; no commit, push, merge, rebase, or PR performed)  
**Thesis:** *SynTutor: An Explainable AI-Based Framework for Syntax Tree-Driven Grammar Analysis and Learning Using NLP*

---

## 1. Executive Summary & Root Causes Resolved

### A. Model-Free CI — Cambridge Source Governance (`syntax-generator-tests.yml`, failed run `44906130991`)
- **Reported failure:** 10 Cambridge Phase-B source-audit test failures (`<RULE_ID>: freshly extracted rule already in production registry`) in `tools/test_cgel_phase_b*.py`, followed by `tools/cgel_batch_gate.py --all`, `tools/test_cgel_batch_gate.py`, `tools/audit_cgel_ch03.py --check`, and `tools/test_cgel_ch03_qa.py`.
- **Root cause:** Commit `d94e024` (`Main model handoff and Phase C runtime/authority work (#171)`) introduced `grammar/cambridge_runtime_overlay.json` and enabled **193** implemented Phase-C candidate probes in `grammar/runtime_registry.json` under an explicit owner waiver (`owner_waiver: true`, `independent_review: false`, `crosswalk_status: "owner_waived_unverified"`, `test_status: "source_examples_passed"`, `runtime_status: "enabled"`), backed 1-for-1 by overlay entries (`status: "REVIEWED"`, `review_basis: "owner_waived_ai_review"`, `runtime_check: {"kind": "candidate_probe_set", "set": "phase_c"}`) and enforced by `server/test_cambridge_registry.py`. However, the Phase-B audit tools (`tools/cgel_batch_gate.py` and `tools/audit_cgel_ch03.py`) were never updated to recognize this Phase-C owner-waived overlay lifecycle and therefore rejected every overlaid rule as an unauthorized activation of a freshly extracted rule.
- **Fix (strict, fail-closed, zero weakening):** Added `load_owner_waived_overlay()` and `is_owner_waived_phase_c_entry()` in `tools/cgel_batch_gate.py` (reused by `tools/audit_cgel_ch03.py`). A `runtime_registry.json` entry is accepted by Phase-B/Chapter-3 audits **only** when all 7 invariants hold simultaneously:
  1. `owner_waiver is True` and `independent_review is False` (never claiming independent human review);
  2. non-empty `reviewed_by` and `reviewed_on` strings;
  3. `crosswalk_status == "owner_waived_unverified"`;
  4. `test_status == "source_examples_passed"`;
  5. `runtime_status == "enabled"`;
  6. a matching entry in `grammar/cambridge_runtime_overlay.json` with `status == "REVIEWED"`, `review_basis == "owner_waived_ai_review"`, and `runtime_check == {"kind": "candidate_probe_set", "set": "phase_c"}`;
  7. the source rule's `rule_type` is in `{"constraint", "variety_restricted"}` (descriptive, classification, and stylistic rules remain strictly blocked even if added to an overlay).
  Adversarial unit tests were added to `tools/test_cgel_batch_gate.py` proving that unwaived activation, missing overlay records, false `independent_review: True`, and non-constraint rules all still fail closed.

### B. Parser-Backed CI — Unified Generator/Builder & Browser Suite (`syntax-generator-runtime.yml`, failed run `44906130982`)
- **Reported failure:** `scripts/test_explanation_browser.py` timed out at line 98 on `page.wait_for_selector('#openCanonicalBuilder', timeout=60000)`.
- **Root causes:**
  1. **UI transition & selector drift:** Commit `d94e024` removed `#openCanonicalBuilder` from `web/js/main.js`, and commit `a3a8fdd` (`Unify syntax builder and generator UI`) replaced it with the unified `#exploreBuilderBtn` (`"Syntax builder →"` / `"Syntax generator →"`) control, unified zoom/fit button labels (`"Fit syntax tree"`, `"Zoom in on syntax tree"`), `#canvasTreeText` outline, and `#inputClearBtn` session clear.
  2. **Confirmed application regression #1 (Syntax Builder explanation continuity):** When opening a canonical tree from the Syntax Generator via `#exploreBuilderBtn`, `openBuilderView({ combined: true, canonicalTree })` in `web/js/syntax-builder-ui.js` unconditionally called `explainSelected()` with an empty selection, **clearing `#explainNode` blank** instead of invoking `showBuilderEvidence(null)` to display the shared Burton–Roberts `/api/explain` evidence. Additionally, `web/js/syntax-builder-ui.js` still imported `./explanation-evidence.js?v=2026.11.18f` instead of `?v=2026.11.21b`.
  3. **Confirmed application regression #2 (Unified Builder toggle hidden after session reset / account switch):** In `web/js/main.js` (`startNewSession()`), calling `hideExploreBuilder()` without calling `syncCanvasModeButton()` hid `#exploreBuilderBtn` permanently after an account switch or session clear while inside the unified Generator/Builder workspace, leaving the learner unable to toggle back between `"Syntax generator →"` and `"Syntax builder →"`.
- **Fixes:**
  - Fixed `web/js/syntax-builder-ui.js` (`openBuilderView`) to call `showBuilderEvidence(null)` when `opts.canonicalTree` is supplied, and aligned its `explanation-evidence.js` import to `?v=2026.11.21b`.
  - Fixed `web/js/main.js` (`startNewSession`) to call `syncCanvasModeButton()` immediately after `hideExploreBuilder()`, preserving the mode toggle on the unified Syntax Studio while keeping it hidden in Lessons, Quizzes, Leaderboard, and Achievements.
  - Updated `scripts/test_explanation_browser.py` (all 4 modes), `scripts/test_generator_canvas_browser.py`, `scripts/test_xai7_browser.py`, and `.github/workflows/syntax-generator-runtime.yml` so all 11 active Chromium Playwright checks run end-to-end.

### C. Model-Free CI — Downstream Legacy Browser Tests (`syntax-generator-tests.yml:241-244`)
All four browser regression scripts invoked at the end of `syntax-generator-tests.yml` were repaired to validate the actual unified Syntax Studio, Quiz V2, Foundations lessons, and sidebar progression architecture without weakening behavior assertions:
1. **`scripts/test_ui_prototype_browser.py`:** Updated from removed `#toggleParserDiagnostic` / `#generatorTreeOutline` / `"Explore B-R tree in Builder"` / `"Back to Syntax Generator"` to test: (a) fail-closed unresolved B-R authority (`#treeAuthorityNotice`, hidden `#treeCanvas`/`#canonicalTreeView`, absent `#toggleParserDiagnostic`); (b) provisional B-R working tree with flagged node keyboard selection (`Enter`), accessible outline (`#canvasTreeTextBody`), zoom/fit on desktop/tablet-dark/mobile-touch, grounded subject-verb agreement finding + `[data-learner-revision]` + `"Show full sentence analysis"` reset; (c) canonical B-R tree + unified `#exploreBuilderBtn` Generator $\leftrightarrow$ Builder handoff; (d) `renderLessonTree(ADVANCED)` triangle/gap check via live loaded `lessons-ui.js` URL; (e) desktop 503 outage recovery for Lessons and Quizzes (`"Back to Syntax Studio"` + `"Try again"`).
2. **`scripts/test_account_journey_browser.py`:** Updated to apply post-Foundations `20261116*.sql` migrations idempotently when running right after `test_foundation_database.py --after-account-tests`, expanded `SELECTS` and `transport()` to cover `foundation_progress`, `quiz_attempts_v2`, `quiz_practice_v2`, `save_foundation_event`, `save_quiz_v2_attempt`, and `ensure_leaderboard_participation`, and migrated UI flows to: (a) Leaderboard Settings modal alias customization & opt-out; (b) active Foundations `br-01` (`2.0.0`) completion via `save_foundation_event` (`15 / 15 lesson XP verified`); (c) verified `quiz-br-01` completion (`5/5`, `10` verified XP) + fresh-tab PostgreSQL reload into `"Attempt history"`; (d) sidebar verified XP meter (`#sidebarProgressLabel` `25/100 XP`, `#identityChip` `aria-label`) + unlocked badges (`first-lesson`, `first-quiz`, `perfect-five`); (e) private `analysis_history` RLS isolation across `journey-a`, `journey-b`, and signed-out guest; (f) unified Syntax Builder (`#exploreBuilderBtn` $\rightarrow$ `#builderCanvas` + `#inputText`) draft persistence, duplicate-auth retention, and cross-account isolation/restoration (`PrivateB`); (g) stale `/api/parse` race across account switch.
3. **`scripts/test_progression_browser.py`:** Updated from removed `#achievementsProgressLabel` / `#achievementsProgressFill` / `#achievementsCatTrigger` to validate the live sidebar verified-XP meter (`#sidebarProgressLabel`, `#sidebarProgressBar`, `#identityLevelBadge`, `#identityChip`), Leaderboard Settings modal join/leave flow, offline degradation (`"Verified XP unavailable."`, `"Achievements unavailable"`), sign-out state, and direct `#achievementsCatPills` filtering.
4. **`scripts/test_foundations_preview_browser.py`:** Replaced hardcoded `/ 12 lessons completed` counts with dynamic `len(COURSE['lessons'])` (`31` active lessons), checked Cambridge chapter pilot banner dynamically against existing `*-pilot.json` files, and exempted only the known home-page onboarding demo seed (`"The clever boy reads a book."` on bare `base`) while still enforcing **zero** `/api/parse` calls across all lesson views.

---

## 2. Priority 1 Audit — Formal Curriculum Review Blockers (NOT Forged / NOT Weakened)

Both `scripts/validate_lessons.py` and `scripts/validate_assessments.py` in `.github/workflows/syntax-generator-tests.yml` (lines 155 & 157) **genuinely fail** because pre-existing upstream commits on `main` (`69f4390` PR `#173` and `250b232`) modified curriculum and quiz content without executing the required independent source-review receipt workflow. Per strict governance policy, **no approval receipts were regenerated, no reviewer signatures were invented, and no validator checks were weakened.**

### A. `scripts/validate_lessons.py` — Exact Blocker
- **Command error:** `AssertionError: Source metadata changed after review` (`scripts/validate_lessons.py:47`)
- **What is STILL intact (100% matching `2026-11-08` receipts):**
  - All **25** original reviewed sources in `sources/burton_roberts/reviews/2026-11-08-lessons.json` and `sources/cambridge/reviews/2026-11-08-lessons.json` (`0` altered, `0` missing).
  - All **11** Burton–Roberts Foundations lessons (`br-01` through `br-11`, `v1.0.0`): `11/11` SHA-256 digests match `sources/burton_roberts/reviews/2026-11-08-lessons.json` identically.
- **Exact unreviewed modifications requiring formal curriculum review:**
  1. `web/content/lessons/course.json` added **1,713** new unreviewed Cambridge source entries (`course['sources']` expanded from `25` to `1,738`).
  2. `cgel-clauses` was substantively rewritten (`v1.0.0` $\rightarrow$ `v3.1.0`), invalidating its SHA-256 hash in `sources/cambridge/reviews/2026-11-08-lessons.json`.
  3. **19** newly authored Cambridge chapters (`cgel-ch01`, `cgel-ch03` through `cgel-ch20`, `v3.1.0`) were added referencing nonexistent review receipt paths `content/cambridge/cgel-ch01-review.json` .. `content/cambridge/cgel-ch20-review.json`.
- **Required owner action:** Complete an authorized Cambridge curriculum review covering all 20 `3.1.0` chapters (`cgel-ch01`, `cgel-clauses`, `cgel-ch03`..`cgel-ch20`) and the 1,713 added source entries, and record authentic signed review receipts (or explicitly mark unreviewed Cambridge chapters as unreviewed draft/pilot content per repository governance).

### B. `scripts/validate_assessments.py` — Exact Blocker
- **Command error:** `AssertionError: Question/source/blueprint content changed after review` (`scripts/validate_assessments.py:19`)
- **What is STILL intact (100% unchanged since `52f96f7`):**
  - All **110** Burton–Roberts assessment items (`br-01`..`br-11`), all **16** assessment blueprints, and all `bank['sources']`.
- **Exact unreviewed modifications requiring formal assessment review:**
  - Commit `69f4390` (PR `#173`) substantively rewrote all **10** `cgel-clauses` assessment items (`prompt`, `options`, `answer`, and `rationale`) while retaining `"review_status": "INDEPENDENTLY_REVIEWED"` and leaving `sources/assessment_reviews/2026-11-08-bank.json` (`bank_sha256`) pointing to the pre-`69f4390` bank:
    - `cgel-clauses-p1-1`, `cgel-clauses-p1-2`, `cgel-clauses-p2-1`, `cgel-clauses-p2-2`, `cgel-clauses-p3-1`, `cgel-clauses-p3-2`, `cgel-clauses-p4-1`, `cgel-clauses-p4-2`, `cgel-clauses-p5-1`, `cgel-clauses-p5-2`.
- **Required owner action:** Conduct an authorized review of those 10 rewritten `cgel-clauses` items and issue an updated review receipt in `sources/assessment_reviews/` (or revert those 10 items to their reviewed `2026-11-08` wording if unreviewed edits should not ship as `INDEPENDENTLY_REVIEWED`).

---

## 3. Exact Files Modified and Justification

| File | Justification |
|---|---|
| `tools/cgel_batch_gate.py` | Add strict 7-invariant `load_owner_waived_overlay()` / `is_owner_waived_phase_c_entry()` governance predicate so Phase-B audits accept only properly overlaid Phase-C owner-waived candidate rules while failing closed on any unauthorized entry. |
| `tools/audit_cgel_ch03.py` | Reuse `is_owner_waived_phase_c_entry()` / `load_owner_waived_overlay()` in Chapter 3 QA audit. |
| `tools/test_cgel_batch_gate.py` | Add adversarial unit test `test_owner_waived_phase_c_governance_fails_closed_on_unwaived_or_invalid`. |
| `web/js/syntax-builder-ui.js` | Fix real regression where opening a canonical tree via `#exploreBuilderBtn` cleared `#explainNode` blank instead of calling `showBuilderEvidence(null)`; align `explanation-evidence.js` import to `?v=2026.11.21b`. |
| `web/js/main.js` | Fix real regression in `startNewSession()` where `hideExploreBuilder()` left `#exploreBuilderBtn` stuck hidden after account switches or clears on the unified Syntax Studio; call `syncCanvasModeButton()` right after `hideExploreBuilder()`. |
| `scripts/test_explanation_browser.py` | Align all 4 modes to unified `#exploreBuilderBtn` handoff, exact module singleton loading, `/api/parse` response filtering, onboarding dismissal, and `/api/evaluate` == `/api/explain` HTTP parity. |
| `scripts/test_generator_canvas_browser.py` | Align to fail-closed B-R behavior (absent `#toggleParserDiagnostic`, hidden `#treeCanvas`, onboarding dismissal, multi-sentence click selection on desktop/mobile). |
| `scripts/test_xai7_browser.py` | Update zoom/fit button aria-labels (`Zoom in on syntax tree`, `Fit syntax tree`). |
| `scripts/test_ui_prototype_browser.py` | Modernize to validate fail-closed B-R authority, provisional working tree + flagged node keyboard inspection + revision explanation, canonical tree + unified `#exploreBuilderBtn` handoff, outline, zoom, `renderLessonTree(ADVANCED)`, and desktop 503 outage recovery across desktop/tablet-dark/mobile. |
| `scripts/test_account_journey_browser.py` | Modernize for `20261116*.sql` migrations, Leaderboard Settings modal, active Foundations `br-01` (`2.0.0`), verified `quiz-br-01` reload into `"Attempt history"`, sidebar `#sidebarProgressLabel`, private `analysis_history` RLS isolation, unified Syntax Builder draft isolation (`PrivateB`), stale `/api/parse` race, and sign-out. |
| `scripts/test_progression_browser.py` | Modernize for sidebar `#sidebarProgressLabel` / `#sidebarProgressBar` / `#identityChip`, Leaderboard Settings modal join/leave, offline/sign-out states, and `#achievementsCatPills`. |
| `scripts/test_foundations_preview_browser.py` | Replace hardcoded `12`-lesson total with `len(COURSE['lessons'])`, detect Cambridge pilot banner dynamically from `*-pilot.json`, and allow only the bare-home onboarding demo parse while enforcing zero `/api/parse` calls across all lesson routes. |
| `.github/workflows/syntax-generator-runtime.yml` | Wire Node 22 + Playwright and execute all 11 active parser-backed/live-Flask Chromium checks. |

---

## 4. Complete Verification Results (Local vs. Hosted GitHub Actions)

> **Execution Scope Disclosure:** All checks below were executed **locally** on `macOS` (`.venv` Python `3.11.17`, Node `v26.12.0`, Chromium via Python Playwright `1.65.2` and Node Playwright `1.64.1`). Because native `postgres` and `psycopg` are not installed on this macOS host, `scripts/test_account_journey_browser.py` was verified locally end-to-end by running it unmodified against all 20 real `supabase/migrations/*.sql` files inside `@electric-sql/pglite` (PostgreSQL WASM) via a temporary `/tmp` bridge (deleted after verification). **Hosted GitHub Actions execution (including native `postgres:16` + `psycopg` and full CI runner execution) has NOT yet been run** because committing and pushing are outside this step's constraints.

### A. Model-Free Cambridge Governance & Registry Checks (Local — ALL PASS)
- `tools/migrate_diagnostics.py --check`: **PASS** (`3,914` rules, `0` missing diagnostic fields)
- `tools/validate_cgel_rules.py`: **PASS** (`3,914` rules, `0` errors)
- `tools/ledger.py check --allow-unprocessed`: **PASS** (`1,764` pages, `0` errors)
- `unittest tools.test_cgel_infrastructure`: **PASS (6/6)**
- `unittest discover -s tools -p 'test_cgel_phase_b*.py' -t .`: **PASS (123/123)**
- `tools/cgel_batch_gate.py --all`: **PASS (110/110 audits, 1,620 pages, 0 errors)**
- `unittest tools.test_cgel_batch_gate`: **PASS (8/8)**
- `tools/audit_cgel_ch03.py --check`: **PASS (`automated_gate_passed: true`, 0 errors)**
- `unittest tools.test_cgel_ch03_qa`: **PASS (7/7)**

### B. Server Cambridge, Lexical Uncertainty, Correction Completeness, XAI & Metrics (Local — ALL PASS)
- `PYTHONPATH=server .venv/bin/python -m unittest test_cambridge_registry test_cambridge_evaluator test_authority test_canonical_binding test_findings test_legacy_disposition test_cross_layer_consistency test_correction_completeness test_learner_analysis`: **PASS (67/67)**
- `docs/audits/technical_evaluation/verify_metrics.py`: **PASS (74/74 checks; frozen datasets & blank human review worksheet untouched)**

### C. JavaScript, PGlite Database, Static Build & Packaging Checks (Local — ALL PASS)
- `node --check web/js/{main,syntax-builder-ui}.js`: **PASS**
- `npm run test:evidence`, `test:legacy-map`, `test:node-lessons`, `test_explanation_dedupe.js`, `test:correction`, `test:quiz`: **PASS (6/6)**
- `npm run test:quiz-v2` (including `test_quiz_v2_database.js` PGlite), `npm run test:lessons` (including `test_lesson_database.js` PGlite), `npm run test:assessments` (including `test_assessment_database.js` PGlite), `npm run test:builder`: **PASS (4/4)**
- `test_level.js`, `test_tree_layout.js`, `test_xai7_focus.mjs`, `test_learner_explanations.mjs`, `test_account_integration.js`: **PASS (5/5)**
- `node scripts/build.js`, `scripts/test_static_build.py`, `scripts/test_runtime_packaging.py`: **PASS (3/3)**

> **Note on `npm run build` vs `npm run test:quiz` order:** `npm run build` executes `scripts/tree_sheet.py`, which scans `server/matrix.py` and finds 14 newer constraints (`4.9`, `4.10`, `6.21`–`6.24`, `7.9`, `8.8`, `9.16`–`9.21`) added in `af33b9f`/`d3ffb4e` without matching entries in `server/ruleset.py` (`RULEBOOK`) or `web/js/rule-concepts.js`. In `.github/workflows/syntax-generator-tests.yml`, `npm run test:quiz` runs on line 218 *before* `npm run build` on line 232, so CI passes on the tracked `web/content/tree_sheet.json` (`112` rules, `175` constraints). `RULEBOOK` was intentionally left untouched because `server/test_legacy_disposition.py` enforces an exact 1-to-1 match against `grammar/legacy_rule_dispositions.json`.

### D. Complete Chromium Playwright Verification Matrix (Local — 15/15 PASS Post-Final-Edit)
**Parser-Backed CI (`syntax-generator-runtime.yml`, 11/11 PASS):**
1. `.venv/bin/python scripts/test_generator_canvas_browser.py`: **PASS**
2. `HF_HUB_OFFLINE=1 .venv/bin/python scripts/test_explanation_browser.py --reviewed-fixture`: **PASS**
3. `HF_HUB_OFFLINE=1 .venv/bin/python scripts/test_explanation_browser.py`: **PASS**
4. `HF_HUB_OFFLINE=1 .venv/bin/python scripts/test_explanation_browser.py --final-declarative`: **PASS**
5. `HF_HUB_OFFLINE=1 .venv/bin/python scripts/test_explanation_browser.py --working-tree`: **PASS**
6. `node scripts/test_builder_generator_browser.mjs`: **PASS**
7. `node scripts/test_quiz_v2_browser.js`: **PASS**
8. `node scripts/test_cross_layer_xai_browser.mjs` (live Flask `:8769`): **PASS**
9. `node scripts/test_interactive_xai_browser.mjs` (live Flask `:8769`): **PASS**
10. `node scripts/test_ui_ux_refinements_browser.mjs` (live Flask `:8769`): **PASS**
11. `node scripts/test_real_world_nlp_browser.mjs` (live Flask `:8769`): **PASS**

**Model-Free CI (`syntax-generator-tests.yml:241-244`, 4/4 PASS locally):**
12. `.venv/bin/python scripts/test_foundations_preview_browser.py` (against built `dist/`): **PASS** (`100` book topics across 11 pilots)
13. `.venv/bin/python scripts/test_progression_browser.py`: **PASS**
14. `.venv/bin/python scripts/test_ui_prototype_browser.py`: **PASS** (desktop `1440×1000`, tablet dark `800×950`, mobile touch `390×844`)
15. `.venv/bin/python scripts/test_account_journey_browser.py` (verified locally via `@electric-sql/pglite` applying all 20 `supabase/migrations/*.sql` verbatim; native `postgres:16` + `psycopg` run pending hosted CI): **PASS**

### E. Still-Failing Checks (Formal Governance Blockers Only)
- `scripts/validate_lessons.py`: **FAIL** (`AssertionError: Source metadata changed after review`) — blocked by unreviewed `main` commits `69f4390`/`250b232` (see Section 2A).
- `scripts/validate_assessments.py`: **FAIL** (`AssertionError: Question/source/blueprint content changed after review`) — blocked by 10 unreviewed `cgel-clauses` item rewrites from `69f4390` (see Section 2B).

---

## 5. Priority 4 Audit — `repomix-output.xml` Cleanup (No History Rewrite)

- **Audit findings:** Tracked in `5451d72` (`47,341,501 bytes` / `45.1 MiB`, `1,148,013 lines`, `1,198` embedded repository files).
  - **Private secrets (`sk_*`, `ghp_*`, `gho_*`, `github_pat_*`, PEM private keys, `.env`):** `0` found.
  - **Non-secret public client config copied from `web/js/config.js`:** 1 public Supabase `anon` JWT and 5 Clerk test publishable/fixture strings (`pk_test_*`).
  - **Minor local noise:** 2 macOS developer home paths (`/Users/angelo`, `/Users/kiyel`) copied from audit markdown files and 17 fixture emails.
- **Safe to untrack and ignore:** **Yes.** No source file, test, or build script references `repomix-output.xml`.
- **Exact non-history-rewriting remediation commands** (run in a normal follow-up commit when ready to commit):
  ```bash
  git rm repomix-output.xml          # or `git rm --cached repomix-output.xml` to keep a local copy untracked
  printf '\nrepomix-output.xml\n' >> .gitignore
  ```
  This removes the 45 MiB generated bundle from future trees, diffs, and CI checkouts without rewriting Git history.

---

## 6. Hosted CI Readiness & Recommendations for Codex

### Hosted CI Readiness
- **`syntax-generator-runtime.yml` (Parser-backed CI):** **Ready to pass end-to-end on GitHub Actions** once committed and pushed (all 11 Chromium browser suites and all 67 server tests pass locally).
- **`syntax-generator-tests.yml` (Model-free CI):**
  - Cambridge source-governance step (lines 40–52, previously failed run `44906130991`): **Resolved and verified locally.**
  - Browser verification step (lines 235–244, all 4 scripts): **Resolved and verified locally** (`test_account_journey_browser.py` verified locally via PGlite with all 20 SQL migrations; requires hosted `postgres:16` + `psycopg` run to confirm native Postgres execution).
  - **Remaining hosted blocker (lines 153–158):** `scripts/validate_lessons.py` and `scripts/validate_assessments.py` will still fail on GitHub Actions until the formal curriculum/assessment review sign-off for upstream PR `#173` (`69f4390` / `250b232`) is resolved.

### Recommendations for Codex Review
1. **Verify the two real frontend fixes:**
   - `web/js/syntax-builder-ui.js` (`openBuilderView` $\rightarrow$ `showBuilderEvidence(null)` when `opts.canonicalTree` is set)
   - `web/js/main.js` (`startNewSession` $\rightarrow$ `syncCanvasModeButton()` right after `hideExploreBuilder()`)
2. **Audit the 7-invariant Cambridge Phase-C owner-waiver predicate** in `tools/cgel_batch_gate.py` and `tools/audit_cgel_ch03.py` plus its adversarial test in `tools/test_cgel_batch_gate.py`.
3. **Resolve the Priority 1 formal review blocker** (`validate_lessons.py` and `validate_assessments.py`) via an authorized curriculum review pass for the 20 Cambridge `3.1.0` chapters (1,713 added sources) and the 10 rewritten `cgel-clauses` quiz items — never by forging receipts or skipping validators.
4. **Optionally reconcile `tree_sheet.py` vs `server/matrix.py`:** Decide whether the 14 newer `server/matrix.py` constraints (`4.9`, `4.10`, `6.21`–`6.24`, `7.9`, `8.8`, `9.16`–`9.21`) should be excluded from the legacy `RULEBOOK` sheet or documented in a separate mapping so running `npm run build` followed by `npm run test:quiz` locally stays idempotent.
5. **Untrack and ignore `repomix-output.xml`** using the non-history-rewriting commands in Section 5 when committing.
6. **Keep `HUMAN_REVIEW_WORKSHEET.csv` human rating columns blank** until independent human linguistic/pedagogical adjudication is performed.
