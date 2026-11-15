# Quiz V2 implementation report

## Formal-assessment correction
- The current feature is a scored, independent **quiz**, not a guided practice activity. A question-only presentation projection excludes keys/rationales/answer trees; results are submission-gated. Scores, percentages, correct answers and explanations appear only after submission.
- Current new attempts use **2,810 versioned formal questions** (92 applications, 1,517 grammatical analyses, 1,201 concept completions). Relevance checks cover published and generated pools, excluding lesson-wording recall, chapter/page trivia and textbook-presentation commentary. Two original pronoun-modification questions replace coverage lost through filtering. No published answer key was changed.
- Lessons is the source of taught concepts, **not an automatic quiz catalog**. `web/js/quiz-scope.js` applies assessment relevance independently, including to old offline caches; unimplemented/planned topics remain excluded.
- **Preliminaries is excluded from Cambridge Quiz entirely**, including its generated question pools, General/Personalized/Master selection, and cached catalogs. Its Lessons content and assessments remain untouched. Syntax's language-varieties/description orientation topic is also excluded; its grammatical analysis/recursion topics remain.
- Current scope: **11 Syntax chapters / 50 topics; 19 Cambridge chapters / 267 topics**. All 317 subtopic quizzes, 30 General Quizzes, Personalized modes and both Masters preserve question-count policies, deterministic selection, scoring and persistence. Cambridge Master minimum is now 19.
- Browser verification confirms Preliminaries remains in Lessons but does not appear anywhere in the rendered Cambridge Quiz tab, including stale offline cache, mobile/desktop, light/dark themes. Pre-submit keys/feedback remain hidden and post-submit scores/explanations remain available.
- New question review remains pending; no independent approval or verified XP is fabricated. Numerical quiz scoring is separate from XP. The historical `practice`/`unscored-v2` persistence flags remain XP-exemption fields for compatibility, not the current student-facing activity type.
- Relevant correction files: `web/js/{quiz-scope,lesson-curriculum,quiz-assessment-items,quiz-v2,quizzes-ui}.js`, `scripts/test_quiz_{v2,lesson_practice,formal,v2_browser}.js`, and this report. Historical implementation notes below describe earlier stages, not the current scope or terminology.

## Git
- Base: fetched `origin/main`, starting SHA `115b1dfc1bfda90697344d2a72d5e47ba7828782`.
- Branch: `feat/quiz-v2`, initially developed in isolated `SynTutor-quiz-v2`; moved into the original `SynTutor` worktree at the user's request. Original untracked audit files remain untouched; the extra worktree is detached.
- Initial implementation commit: `1f2ed724273b279145f71bfd0eee2f874e86bd96`; subsequent coverage changes are included at the branch tip.
- Final commit: obtain its exact SHA with `git rev-parse feat/quiz-v2` (also supplied in the completion response). A committed file cannot contain its own enclosing commit hash.
- No push, merge, deployment, or remote migration execution.

## Delivered
- Lessons-shared active article registry and chapter overlays; Syntax/Cambridge tabs, native expandable chapters, topic/General entries, separate Personalized/Master modes, scores, explanations, history, and resumable drafts.
- Deterministic distinct-question manifests and answer shuffling. General policy: `max(5, topic count)`; Master water-fill allocation covers every chapter, respects capacity, and randomizes remainder allocation.
- Track-specific, sample-size-adjusted historical/recent performance; concept targeting, unseen-question preference, permanent exclusion of previously missed IDs, diagnostic labeling, and explicit shortages.
- Matching topic scopes reuse existing published blueprints and server-verified XP. Other V2 modes receive numerical quiz scores but remain **XP-exempt**; they never call the XP-awarding RPC.
- Additive private practice synchronization with Clerk text identities, owner RLS, immutable manifests/completed submissions, and no XP-ledger connection.
- Verified sidebar level/XP/progress uses `level.js` and existing progression RPC; pending local estimates remain separate. Compact public-content caching supports content-service outages after an initial successful load.
- Coverage follow-up: **3,020 explicitly unreviewed, no-XP lesson-practice questions**: 88 original application items, 1,561 lesson-table/example matches, and 1,371 explanation-recall items. They are separate from the published bank. Uncovered cards offer an explicitly labeled lesson-practice action rather than a disabled button; reviewed topic XP routes are unchanged.
- Syntax practice uses a compact snapshot of all 51 actually rendered instructional sections, guarded by lesson versions and teaching-module fingerprints. Cambridge practice derives directly from active chapter data. No approval receipts or textbook exercise attributions were invented. Personalized practice also excludes previously missed underlying examples/families.

## Curriculum and reviewed coverage
| Track | Chapters | Topics playable with lesson practice | Independently reviewed topic coverage | Published XP-compatible topics |
|---|---:|---:|---:|---:|
| Syntax | 11 | 51/51 | 11 | 10 |
| Cambridge | 20 | 278/278 | 1 | 0 |

All chapter IDs, names, and order come from the composed Lessons release; topics come from its active instructional sections, excluding introductions/recaps and generic exercise pages. Existing 120 reviewed questions and 16 published assessments/answer keys are unchanged.

All **329 topics, 31 General Quizzes and both track Masters** now have playable coverage, using explicitly labeled unreviewed lesson practice where necessary. Syntax Master retains its reviewed 11–110-question pool; Cambridge Master offers no-XP lesson practice covering every chapter, with a 1,000-item persistence limit per attempt. Personalized modes require five eligible questions after permanent missed-ID/example exclusions.

**Review distinction:** independently reviewed coverage has not increased. New practice includes reading recall, not just new application assessments, and never awards XP. Ten separately queued original drafts remain unpublished. Independent linguistic review is still required before promoting new content to verified assessments.

## Files
- Shared/core/UI: `web/js/{lesson-curriculum,quiz-v2,quiz-core,quiz-progress,quizzes-ui,lessons-ui,main,quiz-lesson-practice,quiz-practice-examples}.js`.
- Presentation: `web/index.html`, `web/css/{quizzes,style}.css`.
- Content: `web/content/quizzes/{bank.schema,v2-review-queue,syntax-practice-source}.json`; extraction tool `scripts/build_quiz_practice.js`.
- Persistence: `supabase/migrations/20261116000000_quiz_practice_v2.sql`.
- Tests: `scripts/test_quiz_v2{,_database,_browser}.js`, `scripts/test_quiz_lesson_practice.js`, `package.json`; this report.

## Executed verification
After `npm ci`, all final commands passed:
```sh
npm run test:quiz-v2
npm run test:assessments
npm run test:lessons
node scripts/test_account_integration.js
npm run test:evidence
git diff --check
QUIZ_V2_PLAYWRIGHT_MODULE=/private/var/folders/b3/fbp931_n5md4v_6gy949gjjr0000gn/T/opencode/quiz-v2-browser/node_modules/playwright/index.mjs node scripts/test_quiz_v2_browser.js
```
Core tests cover all 329 topic attempts/31 General quizzes/both Masters, real curriculum mapping, review gates, 3/5/7-topic counts, capacity/balance, seed/option replay, personalization/improvement/missed-example exclusions, stale-source rejection, grading, persistence, identities and zero practice XP. PostgreSQL/PGlite checks cover RLS, immutable practice, practice IDs disguised as published submissions, forged variable-length XP, and existing ledger/replay regressions. Browser checks include formerly unavailable topics, explicit unreviewed notices, Cambridge Master, preserved reviewed topic routing, cached-content draft reload, sidebar identity isolation, and 390/1360px light/dark layouts, with no page errors.

## Readiness / limitations
Ready for code review/staging, with complete **lesson-practice availability**, not complete independently reviewed/XP coverage. Apply/test the additive migration through the normal authorized deployment process before account practice sync; failures retain device progress. New practice has no verified XP contract by design. Browser auth/progression transport is mocked; SQL authorization is tested separately. Full offline shell installation, live Clerk/Supabase end-to-end operation, and independent linguistic approval were not verified. Rebuild the Syntax snapshot after changing teaching content; stale snapshots fail closed rather than silently serving outdated recall answers.
