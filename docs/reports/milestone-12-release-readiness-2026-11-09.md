# Milestone 12 — Full validation and release readiness

**Review date:** 9 November 2026 (Asia/Manila)  
**Status:** **INCOMPLETE — production release blocked**. Repository validation is in progress on [draft PR #43](https://github.com/ybcole/SynTutor/pull/43). M9, M10 and M11 changes were merged to `main` through PRs #40–42; merging them does not satisfy their remaining hosted and human approval gates.

## Scope and inspected sources

- Planning: `docs/planning/syntutor_12_prompt_execution_plan.md`, `docs/planning/master_checklist.md`, milestone acceptance reports M1–M11, `docs/ARCHITECTURE.md`, `docs/source-authority-matrix.md`.
- Implementation: `server/api.py`, `server/webapp.py`, `server/app.py`, `server/parse_engine.py`, `server/burton_roberts.py`, `server/explanations.py`, `server/cambridge_evaluator.py`, `web/js/correction.js`, `web/js/auth.js`, `web/js/leaderboard.js`.
- Data: eleven timestamped SQL migrations under `supabase/migrations/`, `grammar/rules/`, approved explanation templates, source manifests, lesson and assessment catalogs.
- Tests: CI workflows, `server/test_burton_roberts.py`, `server/test_webapp_contract.py`, `server/test_stdlib_transport_contract.py`, `server/test_parser_runtime.py`, `scripts/test_*database.py`, browser regression scripts and source validators.

## Changes proposed in M12

1. **Bound all Flask JSON endpoints to 250,000 request bytes.** Previously `/api/parse` and `/api/words` could read an oversized body without an app-wide limit; `/api/evaluate` and `/api/explain` only checked known Content-Length headers. `MAX_CONTENT_LENGTH` and a JSON 413 handler now cover all four. Added request-size tests for each route.
2. **Reject malformed word-lookup payloads safely.** Both Flask and legacy stdlib endpoints now reject non-string word entries; Flask also rejects non-object JSON instead of raising a server error. Added transport regression tests.
3. **Make post-merge validation automatic.** Both GitHub Actions workflows now run on pushes to `main`, in addition to their existing pull-request/legacy triggers, so a merge commit is checked as well as its PR head.
4. **Fixed-corpus pipeline comparison.** `scripts/compare_pipeline_fixed_corpus.py` compares legacy diagnostic verdicts against B-R Chapter V2 and FINAL-D1 output on six original examples using real spaCy/Benepar. It validates any normalized tree against the canonical schema, checks the underlying parser candidate stays identical between profiles, and confirms legacy verdicts are not labelled book-verified. Optional CoLA is disabled for deterministic comparison; this is **not** a grammatical-accuracy benchmark. The parser CI workflow runs it and attaches a machine-readable JSON artifact.

## Verification matrix

| Criterion | Existing evidence / proposed M12 action | Release state |
|---|---|---|
| Test and schema integrity | Model-free CI runs schema JSON, source validators, 252-record importer audit, normalizer/evaluator tests, B-R gold tests and Javascript unit suites | PR #43 CI confirmation pending |
| B-R and Cambridge linguistic checks | Chapter validators, B-R gold normalization; Cambridge registry/evaluator tests and source-readiness audit. Only independently reviewed source material can be authoritative | Tested conservative scope; not whole-book coverage |
| Source-grounded explanation | Generator/Builder parity tests, evidence tests for missing/unreviewed/conflicting sources and `NO_BOOK_BASIS` | Existing regression coverage; real-browser CI pending |
| Parser and browser | Parser-backed CI uses pinned spaCy/Benepar assets, real parser tests, multiline parser, and Generator/Builder/Lessons/Quizzes browser checks | PR #43 CI pending |
| XP, achievements, privacy | Native PostgreSQL tests for M7–M11, multi-session races, RLS, badge replay, opt-in/withdrawal and legacy-row preservation | Local/CI test transport only; real Clerk staging pending |
| Migration and compatibility | Disposable PostgreSQL tests and M11 timestamped migration/rollback guide | No independent hosted migration/back-up check |
| Correction and accessibility | Responsive/keyboard Chromium checks and reviewed screenshots | No independent learners, screen-reader session or owner visual sign-off |
| Backend abuse and error handling | New global 250 KB cap and words validation; existing API error contracts | **Deployment rate limiting and resource exhaustion policy not yet verified** |
| Feature flags and rollback | M9 leaderboard defaults to disabled; M11 rollback guide preserves ledger, XP and badges | Hosted staged rollout and rollback approval outstanding |
| Old/new pipeline comparison | New fixed-corpus script and CI artifact | PR #43 parser-backed execution pending |
| User-facing scope disclosure | Source governance and partial/unsupported-analysis states exist | Confirm that the learner-facing release explicitly explains limited coverage |

**Existing green milestone branches:** M9 [model-free](https://github.com/ybcole/SynTutor/actions/runs/42469371964) / [parser](https://github.com/ybcole/SynTutor/actions/runs/42469372077); M10 [model-free](https://github.com/ybcole/SynTutor/actions/runs/42473094739) / [parser](https://github.com/ybcole/SynTutor/actions/runs/42473094845); final M11 head [model-free](https://github.com/ybcole/SynTutor/actions/runs/42536482257) / [parser](https://github.com/ybcole/SynTutor/actions/runs/42536482247). These validate the PR heads, not deployed systems. Current M12 head checks must be inspected before approval.

## Known limitations and release blockers

1. **Live authentication and database:** No live Clerk JWT/Supabase staging test was performed through this review. Validate account isolation during concurrent requests, real token refresh, guest handling, all migrations, catalogue seed versions, and rollback against representative records. Owner must record database backup and migration ledger.
2. **Leaderboard privacy:** The release flag is off by default. Before enabling it, independently verify real consent, alias disclosure, withdrawal, two-account isolation, and authorization in staging. Public rows must contain only rank, alias and period XP; private XP and badges must never appear.
3. **Independent usability and accessibility:** M10 requires owner review and learner sessions outside the implementation team, including a keyboard or assistive-technology session. Automated screenshots are not equivalent to these.
4. **Parser performance and abuse:** The new 250 KB request cap is only one availability control. A deployment-specific rate limit, CPU/worker concurrency/timeouts, observability and incident handling policy still need implementation and verification. The Flask application's default CORS is `*`; review and set `SYNTUTOR_ALLOW_ORIGIN` to the approved frontend origin in production.
5. **Linguistic scope:** Cambridge runtime grammaticality constraints remain disabled pending case-specific source, exception and crosswalk verification. B-R FINAL-D1 mapping may be unresolved; raw Benepar output remains diagnostic rather than a canonical source-approved B-R tree. Legacy rule-matrix verdicts are *not* source-verified grammaticality judgments; CoLA cannot supply book authority.
6. **Curriculum scope:** The published launch path is eleven B-R lessons and one Cambridge companion, not full coverage of either grammar reference. Seventeen advanced Cambridge topic placeholders are not independently reviewed or published.
7. **Deployment consistency:** GitHub reported successful Vercel status on the M11 merge commit `75ac650`, but a successful build/status does not prove which environment was deployed or whether its SQL schema matches. Never enable release flags on an unverified database.
8. **Approval:** The owner has not accepted the final release-readiness package or the migration/privacy/rollback gates in this report. Do not represent the project as complete or production-ready.

## Staging and release acceptance runbook

1. Freeze a reviewed frontend/backend Git revision and identify the real staging URL, Clerk project, Supabase project and approved CORS origin. Do not put tokens or service-role keys into GitHub comments, public files or the browser.
2. Back up the staging database and capture its migration history. Verify the earlier lesson and quiz schema and seeds; then apply only missing migrations chronologically, through `20261108000007_account_integration.sql`.
3. Run two real Clerk accounts and a signed-out session through Generator, Builder, lesson, quiz, XP, achievements, history and account switching while requests are pending. Confirm versioned replay does not award extra XP and legacy rows survive.
4. Temporarily enable the leaderboard flag **in staging only** to test opt-in and withdrawal. Audit RPC return fields and RLS under both identities. Disable the flag again.
5. Test real desktop/mobile corrections, original restoration and source citation discovery with independent learners; include keyboard/assistive-technology use. Record tasks, outcomes and unresolved accessibility issues.
6. Configure and validate deployment rate limiting, request concurrency limits, privacy-safe error logging and CORS; execute fixed corpus and regression suites on the exact release candidate; compare the emitted machine-readable artifact with the documented source scope.
7. Record recovery drill results. For rollback, disable leaderboard exposure first, restore the last compatible frontend/backend pair, and **retain** the protected migration tables and historical awards unless an explicitly approved data recovery plan says otherwise.
8. Obtain explicit owner approval of the design, privacy, migration and rollback evidence, then update the checklist and milestone tracker. Until then, keep M9–M12 unchecked for final acceptance and label the production release blocked.

## Checklist synchronization and disposition

The M11 merged master checklist began at **131 checked / 19 unchecked** actionable boxes. The M12 report and PR should reconcile the automated test/validator entries only after verifiable CI results. The M9–M11 milestone tracker remains unchecked because the hosted and human acceptance gates are unresolved. Milestone 12 is also unchecked. This is a repository audit and development change, not a user-data migration or release sign-off.

**Approval required:** Owner accepts staging migration/backups, real Clerk and ranking privacy evidence, M10 independent usability/accessibility results, deployment abuse/rollback controls and the final report. Without them, the next action is evidence collection and remediation, not production activation.
