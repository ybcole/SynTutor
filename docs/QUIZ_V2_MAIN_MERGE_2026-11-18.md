# Main integration into Quiz V2 — 2026-11-18

Repository: `/Users/kiyel/Desktop/SynTutor` (actual workspace; clean before merge).
Target: `feat/quiz-v2`, initially `ab75093729b3a25498e12b1d4ec281a85b40396d` (also fetched `origin/feat/quiz-v2`).
Source: fetched `origin/main`, `a3a8fdd52c4d4d12d82089234ff4ac33336daca5`.
Merge base: `0d879fc534dc834dc5d8fec7b82cdb730e52f8a1`.
Merge was necessary. Used `git merge origin/main --no-ff --no-commit` to verify before committing.

## Six textual conflicts

| File | Resolution |
| --- | --- |
| `web/index.html` | Retain standalone Edit/Construct controls; include main's combined-mode switch and its separate Clear button. |
| `web/js/canvas-view.js` | Retain Quiz V2's hidden-viewport guard and asymmetric control padding; apply main's reduced 1.7 fit scale ceiling. |
| `web/js/main.js` | Combine main's Studio initialization and tree-change listener with Quiz V2's embedded builder injection and lesson/quiz/XP refresh listeners. Retain separate Builder navigation. |
| `web/js/quizzes-ui.js` | Retain the current Quiz V2 rendering, question cleanup, navigation, and review flow; main's change only renamed a legacy exit button no longer present in this implementation. |
| `web/js/syntax-builder-ui.js` | Preserve embedded exercise callbacks, resize observer, undo, placement, and viewport handling. Keep standalone Edit/Construct behavior while main's combined Studio automatically edits. Preserve main's palette lesson links, help, tree transfer, display, and change events. Share anchors between edges, handles and hit testing. |
| `web/js/syntax-builder.js` | Combine Quiz V2's import spacing and safe connector APIs with main's display-tree import, display rows, canonical notation and export changes. Use mode-appropriate anchors. |

## Semantic corrections

- Separate Builder navigation remains active on its own entry; combined Studio retains Syntax as the active destination.
- Combined and standalone editing lifecycles no longer override one another; embedded quiz/lesson builders retain their own lifecycle.
- Standalone palette avoids the toolbar; combined palette is dismissed on workspace teardown. Main's combined Clear remains usable alongside standalone Clear.
- Static upload exclusions now include the dictionary Markdown required by main's new build generator. Backend code still stays outside public output.
- Existing browser tests now wait for queued reconstruction answer persistence, select the visible Clear control, and use current sidebar XP text/chapter-card selectors. Added combined-mode transfer, repeated-switch, palette, Clear, and teardown assertions.
- Question banks, reviewed corrections, scoring/persistence code and migration files were not changed by conflict resolution. No connected database or schema was changed.

## Executed verification

All of these passed (Node scripts under `scripts/`):

- `test_quiz_digest_freshness.js`
- `test_quiz_v2.js`
- `test_quiz_lesson_practice.js`
- `test_quiz_formal.js`
- `test_quiz_v2_database.js`
- `test_quiz_refinements.js`
- `test_tree_quiz.js`
- `test_assessment_core.js`
- `test_assessment_database.js`
- `test_lesson_progress.js`
- `test_lesson_database.js`
- `test_foundation_progress.js`
- `test_builder_core.js`
- `test_account_integration.js`
- `test_level.js`
- `test_legacy_node_map.js`
- `test_tree_layout.js`
- `test_correction.js`
- `test_explanation_evidence.js`
- `test_quiz_v2_browser.js` (all interactive formats, navigation, saved attempts/history, account/XP isolation, 390/768/1360px light/dark layouts)
- `test_gamification_e2e.mjs` (disposable PGlite plus Chromium; all existing migrations, foundation/Quiz V2 verified XP, accounts, achievements, leaderboard, responsive layouts)
- `test_builder_generator_browser.mjs` (standalone Builder, generator input, embedded Lessons exercises, combined Studio checks)
- `audit_linguistic_dictionary.mjs`

Python verification:

- `python3 scripts/test_static_build.py`: passed filtered build in a temporary directory.
- `.venv/bin/python -m unittest discover -s server -p test_false_positive_regressions.py`: 9 passed with real parser/models.
- `PYTHONPATH=/tmp/syntutor-merge-test-deps .venv/bin/python -m unittest discover -s server -p test_builder_evaluation.py`: 7 passed.
- `PYTHONPATH=/tmp/syntutor-merge-test-deps .venv/bin/python -m unittest discover -s server -p test_quiz_evidence.py`: 6 passed.

Browser tests used the existing cached Playwright module, with permission to run local fixture servers/headless Chromium. Missing Python test dependencies were installed only under `/tmp`; sandbox-denied transport checks were rerun with permission and passed. No deployment or production database access was used.

## Known existing failure / limits

`node scripts/test_foundations_preview_database.js` fails at line 40: expected 11 chapters, actual 31. Reproduced the identical failure from a separate `git archive` snapshot of the original target commit in `/tmp/syntutor-premerge-baseline`. Left this obsolete preview expectation unchanged; the active lesson, foundation-progress, assessment, Quiz V2 database and full gamification tests pass.

This is local integration validation, not an exhaustive guarantee of every runtime scenario or an independent linguistic review of question content. Legacy standalone PostgreSQL race tests requiring a provisioned DSN were not run; disposable PostgreSQL suites cover scoring, immutability and account isolation. No push, reset, rebase, deployment, or schema edits were performed.
