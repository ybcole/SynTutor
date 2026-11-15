# Quiz V2 implementation report

## Git
- Base: fetched `origin/main`, starting SHA `115b1dfc1bfda90697344d2a72d5e47ba7828782`.
- Isolated branch/worktree: `feat/quiz-v2`, `SynTutor-quiz-v2`. Original untracked audit files were preserved.
- Implementation commit: `1f2ed724273b279145f71bfd0eee2f874e86bd96`.
- Final commit: the report-only follow-up containing this file; obtain its exact SHA with `git rev-parse feat/quiz-v2` (also supplied in the completion response). A committed file cannot contain its own enclosing commit hash.
- No push, merge, deployment, or remote migration execution.

## Delivered
- Lessons-shared active article registry and chapter overlays; Syntax/Cambridge tabs, native expandable chapters, topic/General entries, separate Personalized/Master modes, scores, explanations, history, and resumable drafts.
- Deterministic distinct-question manifests and answer shuffling. General policy: `max(5, topic count)`; Master water-fill allocation covers every chapter, respects capacity, and randomizes remainder allocation.
- Track-specific, sample-size-adjusted historical/recent performance; concept targeting, unseen-question preference, permanent exclusion of previously missed IDs, diagnostic labeling, and explicit shortages.
- Matching topic scopes reuse existing published blueprints and server-verified XP. Other V2 modes are explicitly **unscored**; they never call the XP-awarding RPC.
- Additive private practice synchronization with Clerk text identities, owner RLS, immutable manifests/completed submissions, and no XP-ledger connection.
- Verified sidebar level/XP/progress uses `level.js` and existing progression RPC; pending local estimates remain separate. Compact public-content caching supports content-service outages after an initial successful load.

## Curriculum and reviewed coverage
| Track | Active chapters | Instructional topic entries | Usable topic quizzes | Published XP-compatible topics |
|---|---:|---:|---:|---:|
| Syntax | 11 | 51 | 11 | 10 |
| Cambridge | 20 | 278 | 1 | 0 |

All chapter IDs, names, and order come from the composed Lessons release; topics come from its active instructional sections, excluding introductions/recaps and generic exercise pages. Existing 120 reviewed questions and 16 published assessments/answer keys are unchanged.

**Content blockers:** no chapter yet has reviewed coverage for every General Quiz topic. Syntax Master supports 11–110 questions; Cambridge Master lacks 19 chapters and is unavailable. Personalized modes work while at least five eligible questions survive exclusions. Ten original questions across two uncovered topics are explicitly unreviewed drafts, never loaded into production. Substantial further authoring and independent review are required.

## Files
- Shared/core/UI: `web/js/{lesson-curriculum,quiz-v2,quiz-core,quiz-progress,quizzes-ui,lessons-ui,main}.js`.
- Presentation: `web/index.html`, `web/css/{quizzes,style}.css`.
- Content: `web/content/quizzes/{bank.schema,v2-review-queue}.json`.
- Persistence: `supabase/migrations/20261116000000_quiz_practice_v2.sql`.
- Tests: `scripts/test_quiz_v2{,_database,_browser}.js`, `package.json`; this report.

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
Core tests cover real curriculum mapping, review gates, 3/5/7-topic General counts, Master balance/capacity, seed/option replay, personalization/improvement/exclusions, grading, persistence, identity isolation, and zero V2 XP. PostgreSQL/PGlite checks cover RLS, immutable practice, forged variable-length submissions, and existing XP/replay regressions. Browser checks cover navigation, keyboard expansion, cached-content draft reload, Master selection/review, personalization, verified sidebar isolation, and 390/1360px light/dark layouts, with no page errors.

## Readiness / limitations
Ready for code review and staging integration, **not a content-complete production launch**. Apply/test the additive migration through the normal authorized deployment process before account practice sync; failures retain device progress. Variable-length/new practice has no verified XP contract by design. Browser auth/progression transport is mocked; SQL authorization is tested separately. Full offline shell installation, live Clerk/Supabase end-to-end operation, and independent linguistic approval were not verified.
