# Milestone 05 — Independent quizzes acceptance

Date: 8 November 2026 (Asia/Manila).

M5's scoped launch implementation is complete and locally verified: 120 original variants, 60 question pools, 16 independent five-item blueprints and 20 canonical positive answer trees. Coverage follows the 12 reviewed M4 outcomes; unreviewed Cambridge constraints remain disabled. No human instructor approval or whole-book coverage is claimed.

| Criterion | Evidence |
|---|---|
| Independent assessments | Separate Quizzes navigation, device namespace, attempt/history tables and no lesson completion dependency/write |
| Original questions and source alignment | Strict bank schema, source/page/profile/outcome links, digest-bound AI review receipt, no lesson prompt reuse, retained M4 source records |
| Mixed five-item blueprints | Seven question kinds, at least three kinds per blueprint, relative difficulty balance, two equivalent lexical variants per pool |
| Fair attempts and feedback | Seeded variants/question/option ordering, immutable submitted responses, resumable drafts, post-submit shared M3 source evidence and targeted lesson links |
| Rewards and persistence | All scores 0–5, best-score delta only, 6→4→0 retry flow, independent versions/accounts, SQL-derived scoring, private RLS and duplicate submission protection |
| Reinforcement and review | Private history, last/best scores, rotated missed-concept practice without XP, explicit short-attempt limits |
| User-facing integration | Actual Chromium navigation, reload, feedback boundary, retries, reinforcement, responsive tree/text alternatives, teardown and zero quiz parser calls |

Observed local checks: 127 model-free backend tests; bank/schema/source/receipt/20-tree/seed validator; JavaScript core/storage tests; actual PostgreSQL migration/seed/RPC/RLS tests; independent browser flow. Existing lesson/browser, legacy evidence/correction/quiz, static build/upload-filter and runtime packaging regressions also run before publication. CI retains full parser/gold/chapter regressions. This report does not claim hosted database or authentication integration testing.

The sample chapter-2 set and scoring policy were checked before bulk authoring under standing owner authorization. The same assistant performed the separate source-constrained verification pass, recorded explicitly in `sources/assessment_reviews/2026-11-08-bank.json`. Existing reviewed M4 source scopes support the new original examples; no raw crosswalk/rule becomes production authority.

The missing detailed quiz prompt was restored as an implementation brief from the unchanged authoritative plan. A shared tree renderer null-guard was corrected so deliberately noncanonical candidate diagrams render without canonical IDs.

**Deployment follow-up:** the two additive M5 migrations and the two M4 prerequisites remain unapplied to production. Device-local progress works; cloud saves and trusted shared XP need deployment. No legacy rows were migrated. Preserve history/award tables on rollback. Existing global gamification/privacy work and broader Cambridge modules remain later milestones, not M5 blockers within this scope.

References: [bank and coverage](../assessments/README.md), [progress/deployment](../assessments/progress-and-deployment.md).
