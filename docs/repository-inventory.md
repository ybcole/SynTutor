# SynTutor repository inventory — Milestone 01

**Audit baseline:** `main`  
**Baseline commit:** `b8b9a244e099eefff5675c7754b4fc3345397177`  
**Audit date:** 7 November 2026  
**Purpose:** Record the implementation and source/data state observed for Milestone 01. This is an inventory, not a claim that the existing implementation satisfies the target architecture.

## Repository and deployment topology

- Repository: `ybcole/SynTutor`; public; default branch `main`; not archived.
- The repository tree was fetched recursively from GitHub. GitHub reported `truncated: false`.
- Browser application: `web/index.html`, `web/css/`, and `web/js/`.
- Primary backend: Flask application in `server/webapp.py`, importing transport-independent logic from `server/api.py`.
- Legacy HTTP server: `server/app.py`.
- Hugging Face Spaces entry point: `server/hf_space.py` (Gradio).
- Static build: `scripts/build.js`; package build command runs `python3 scripts/tree_sheet.py && node scripts/build.js`. Vercel configuration is in `vercel.json`.
- Frontend API origin is configured through `web/js/config.js`; `web/js/config.example.js` is the template. `web/js/config.js` is intentionally ignored by Git.
- README setup identifies spaCy `en_core_web_md` and Benepar `benepar_en3` as runtime model dependencies. External Clerk and Supabase configuration is also required for signed-in persistence.

## Active request and analysis path

1. The browser application boots through `web/js/main.js`.
2. `main.js` sends analysis requests to the configured API origin.
3. `server/webapp.py` serves the frontend and exposes:
   - `GET /api/health`
   - `POST /api/parse`
   - `POST /api/words`
   - API fallback handling for unknown `/api/*` routes.
4. `server/api.py` owns `build_payload` and coordinates:
   - `server/parse_engine.py`: spaCy tokenisation/POS and Benepar constituency candidate.
   - `server/matrix.py`: deterministic legacy tree-relationship/rule matrix and node findings.
   - `server/ruleset.py` and `server/licensing.py`: legacy rule, lexical, licensing, and context checks.
   - `server/detector.py`: optional CoLA acceptability signal.
   - `server/corrector.py` and `server/corrections.py`: candidate correction search, edit assembly, and validation.
   - `server/plain.py`: plain-language payload support.
5. The browser renders the returned tree and evidence through `web/js/renderer.js`, `web/js/ui.js`, and `web/js/main.js`.

**Observed boundary:** the existing `/api/parse` response is a parser/matrix-oriented payload. The repository does not yet contain a canonical Burton-Roberts (B-R) tree normalizer or a B-R structural validator. Benepar output is currently central to the presented tree.

## Frontend feature ownership

| Area | Current files | Observed implementation |
|---|---|---|
| Main workspace and navigation | `web/js/main.js`, `web/index.html` | Coordinates Syntax Generator, Lessons, Builder, history, theme, authentication, and progress. |
| Syntax Generator | `web/js/main.js`, `web/js/renderer.js`, `web/js/ui.js` | Requests `/api/parse`, renders the server tree and diagnostics. |
| Lessons and quiz-like practice | `web/js/tree-quiz.js` | Lesson definitions and content are hard-coded in the module; practice fetches live parser output. It is not a separate, source-versioned assessment bank. |
| Syntax Builder model | `web/js/syntax-builder.js` | DOM-free graph model, node operations, tree conversion, phrase-span comparison. |
| Syntax Builder UI | `web/js/syntax-builder-ui.js` | Canvas interactions, palette, graph checks, word validation and sentence-level parse request. The learner's own graph is not yet evaluated by the same canonical B-R evaluator. |
| Leveling | `web/js/level.js` | Legacy geometric XP thresholds; 5 XP per correct answer plus 5 XP bonus for a flawless run. |
| Achievements | `web/js/achievements.js`, `web/js/tree-quiz.js` | Catalog and deterministic unlock helper exist; dedicated view remains a placeholder. The stored lesson progress identifier does not match the numeric stage identifier expected by the achievement helper. |
| Leaderboard | `web/js/main.js`, `web/js/tree-quiz.js` | Data-reading helper exists; dedicated view remains a placeholder. Public payload currently selects raw user ID. |
| Authentication/persistence | `web/js/auth.js`, `web/js/config.js` | Clerk session and Supabase client integration. External provider configuration cannot be verified from repository source alone. |
| Correction presentation | `web/js/main.js`, `web/js/correction.js`, `server/corrections.py` | Candidate corrections and re-parsed preview exist; the target canonical correction annotation contract is not yet implemented. |

## Linguistic data and source inventory

### Burton-Roberts material

- `CONVENTIONS.md` describes the chapter-specific B-R tree-drawing convention profiles V1–V10 and a final free-analysis profile based on V10 plus the Chapter 7 appendix refinement (D1).
- `web/content/book/ch01.trees.json` through `ch10.trees.json` contain **252 tree records** in total:

| Chapter | Convention | Tree records |
|---:|---|---:|
| 1 | V1 | 15 |
| 2 | V2 | 21 |
| 3 | V3 | 19 |
| 4 | V4 | 15 |
| 5 | V5 | 23 |
| 6 | V6 | 26 |
| 7 | V7 | 62 |
| 8 | V8 | 33 |
| 9 | V9 | 21 |
| 10 | V10 | 17 |
| **Total** | **V1–V10** | **252** |

- Each of Chapters 1–10 has a corresponding `validate_chNN.py` file: **10 tree chapter validators**.
- Chapter 11 is represented by `web/content/book/ch11.json`, a text-oriented chapter record (14 concepts, 6 lesson steps, 7 examples, 9 glossary entries in the inspected file), not another tree bank. It also has `validate_ch11.py`.
- Chapters 7–10 carry additional source-answer metadata such as node fragments, book flags, discussion answers, abbreviated clausal analyses, exercise-answer records, and review notes. Chapter 1–6 also carry chapter-specific answer/diagram metadata.
- Evidence and review markers include `IMG`, `DERIVED_FROM_INSTRUCTIONS`, and `IMG_ANOMALY` in the chapter data. These distinctions must not be discarded by a future import.
- `CONVENTIONS.md` explicitly says the exact B-R edition needs confirmation: its source note refers to the supplied PDFs and a Second Edition preface. No B-R source PDF or separate B-R source directory was present in the audited Git tree. Accordingly, the precise edition and page-image basis have **not** been independently confirmed in this audit.

### Cambridge material

- Cambridge source records are organised under `sources/cambridge/chapter_02/` through `chapter_20/`: **19 chapter folders**.
- The repository contains **22 raw extraction JSON files** (four Chapter 2 batches and one in each Chapter 3–20 folder), **19 chapter extraction reports**, chapter cross-reference records, and chapter conflict records.
- The merged concepts file `grammar/concepts.json` contains **273 entries**.
- The merged runtime-domain rule files contain **196 records**:

| Domain file | Records |
|---|---:|
| `agreement.json` | 2 |
| `clauses.json` | 98 |
| `complementation.json` | 19 |
| `morphology.json` | 23 |
| `other.json` | 18 |
| `phrases.json` | 19 |
| `word_categories.json` | 17 |
| **Total** | **196** |

- The inspected 196 active records are marked `APPROVED`. Their aggregate rule types are 141 classifications, 22 constraints, 32 descriptive generalisations, and 1 stylistic/prescriptive record. No `variety_restricted` record was present in this active set.
- All **196/196** active rule records have B-R mapping entries whose relation is `unverified`. There are no verified cross-framework mappings in the inspected active rule registry.
- Across the 22 raw extractions, **32 uncertain-item records** were present.
- Across 19 chapter conflict files, **7 conflict records** were present: three in Chapter 2 and one each in Chapters 3, 13, 16, and 17. Chapter reports describe four as resolved within the Cambridge rule set (Chapters 3, 13, 16, 17); the three Chapter 2 cross-framework differences remain unresolved pending B-R comparison.
- Coverage is section/subsection based, not whole-chapter completion. Chapter 2 reports cover printed pages 43–69 in four batches; Chapters 3–20 generally cover only the first named section/subsection in each report. The detailed list and limitations are in `docs/burton-roberts-cambridge-crosswalk.md`.
- The Cambridge reports repeatedly state that independent second-pass review has not been performed and B-R mappings remain unverified. Therefore `APPROVED` is recorded as human approval, **not** as evidence of independent review or automatic runtime eligibility.
- The exact Cambridge edition/year/ISBN metadata was not present in the inspected repository records. The title is named as *The Cambridge Grammar of the English Language*, but its edition metadata remains to be supplied/confirmed.
- Cambridge PDFs and long source extracts are not committed to the public repository; reports state that copyrighted source files were not added.

## Rule, evaluation, and generated data

- `grammar/schema.json` defines the Cambridge rule-record shape, required source/page data, framework mapping, exceptions, examples, confidence, and status fields.
- `grammar/rules/*.json` is organised by grammatical domain, not by Cambridge chapter.
- `web/content/master.json` is the legacy 11-section, 111-question rule/error corpus used for model regression, not a standalone modern quiz bank.
- `evaluation/grammatical_sentences.json`, `evaluation/ungrammatical_sentences.json`, and `evaluation/minimal_pairs.json` are evaluation seed sets.
- `web/content/tree_sheet.json` and `docs/tree_sheet.*` are generated instructional/metadata sheets.
- The 252 chapter tree records are the principal existing B-R structural reference fixtures, subject to their individual evidence/review notes.

## Persistence, identity, and migration dependencies

Three SQL migrations were found:

| Migration | Table(s) | Relevant behaviour |
|---|---|---|
| `20260916000000_analysis_history.sql` | `analysis_history` | Clerk subject stored as text; RLS compares JWT `sub`. Migration comments state UUID-era rows remain as UUID text and are not migrated to Clerk identities. |
| `20261013000000_player_stats.sql` | `player_stats` | XP/level/display name table; public SELECT policy; owner-scoped insert/update policies. |
| `20261013000001_quiz_progress.sql` | `quiz_progress` | Per-user/per-rule completion counts; public SELECT policy; owner-scoped insert/update policies. |

Observed risks/dependencies for later milestones:

- `player_stats` XP/level writes are currently performed by browser code using an upsert. The database policy checks row ownership but does not establish a trusted award calculation or idempotent transaction ledger.
- Public leaderboard reads select `user_id`, `display_name`, `xp`, and `level`; raw Clerk subject identifiers are consequently exposed by the current client query.
- `quiz_progress` also has public SELECT in its migration; its privacy suitability must be reconsidered with leaderboard/achievement requirements.
- The current progress records use a `rule_id` value supplied from the lesson phrase type; the achievement helper expects numeric stage IDs.
- Clerk as a Supabase third-party auth provider is an external configuration dependency. Its production setup and live RLS behaviour cannot be confirmed from the repository tree.
- Existing migration comments document a prior auth-provider transition in which old UUID-keyed history is not backfilled. No live database or user rows were accessed in this audit.

## Existing tests, scripts, and CI

Package scripts in `package.json` include:

- `npm run build`
- `npm run test:quiz`
- `npm run test:correction`
- `npm run test:rules`
- `npm run audit`
- `npm run sheet`, `npm run tree:sheet`, `npm run explanation-sheet`, and remediation/master-sheet generators.

Python tests include `server/test_corrector.py`, `server/test_licensing.py`, `server/test_matrix_remediation.py`, `server/test_multiline_parse.py`, and `server/test_licensing.py` (listed once in the repository). Chapter validators are under `web/content/book/`.

No GitHub Actions workflow or browser E2E test configuration was present in the inspected main tree. Test scripts are inventoried here; runtime test execution was not possible from this audit environment because a repository clone could not be established (DNS resolution for `github.com` failed). No test result is claimed.

## Governance files absent from the repository baseline

The audited `main` tree did not contain:
- `master_plan.md`
- `master_checklist.md`
- `syntutor_12_prompt_execution_plan.md`

The project owner supplied these governing documents in the working conversation. Milestone 01 adds the checklist and authoritative execution plan to the repository so subsequent milestones can update their sign-off records in place. The Master Plan is treated as contextual reference and is not copied or used as a separate implementation roadmap.

## Milestone 01 audit boundary

This audit and its deliverables are documentation/decision records only. No parser, rules, lesson, quiz, builder, frontend, backend, database migration, or source-content implementation code was modified.
