# Assessment progress and deployment

Device storage is separate from lessons: `syntutor:assessments:v1:<identity>`. Attempts preserve the assessment/item versions, seed, displayed item/option manifest, responses, position and timestamps. Submitted responses are immutable; a retry creates a new attempt. Best score, last score, attempt count and answer history remain available. Guest/offline caches are learning aids, not trusted leaderboard scores.

Five items earn `max(0,10-2*incorrect)` (two XP per correct response). Unanswered items count as incorrect. Award only the difference above the prior best target for the assessment/version. Scores 3→5→5→1 award 6→4→0→0; the version cap is 10. Targeted reinforcement selects frequently missed pools and rotates examples where available, carries no XP, and is separate from assessment records. It is not a calendar-based spaced repetition scheduler.

Account synchronization has a five-second request bound, device fallback and explicit retry. Offline edits survive reload; auth changes discard the active view and late responses cannot replace another account's store. Storage failure retains memory and reports the limitation. Submitted server records win over stale device records.

## Prepared migration order

First apply M4's `20261108000000_versioned_lessons.sql` and `20261108000001_lesson_catalog.sql`. M5 adds:

1. `20261108000002_independent_quizzes.sql`: private attempt/best-score/XP-event tables, server-owned catalogs and the `save_quiz_attempt` RPC.
2. `20261108000003_quiz_catalog.sql`: immutable reviewed bank/blueprint seed, generated read-only by `scripts/seed_quizzes.py`.

The RPC derives identity from the verified JWT, recomputes the deterministic manifest from the private catalog, validates answers and ignores no forged claims: unknown keys, identity or XP fields are rejected. Direct writes are revoked; own-only RLS reads preserve privacy. Per-user transaction locking serializes lesson/quiz awards. SQL computes scores and best-score deltas, stores a unique positive reward event and updates shared player XP atomically. Repeated submission returns zero without inflating attempt count. Lessons and legacy quiz rows are untouched.

**Hosted status:** no production Supabase migration has been applied. Cloud synchronization/trusted shared XP require all four additive M4/M5 migrations through the normal project deployment process, with the existing Clerk JWT setup. Device-local quizzes work before that step. No production credentials or hosted database connection were available. Actual SQL, permissions and RLS were verified in isolated PGlite with mocked verified JWT claims; its serialized WASM connection is not a hosted multi-connection load test.

Retain published items/blueprints in both browser bank and server catalog forever while their history is supported. Append new version keys rather than rewriting answers in place; a new assessment version has a separate reward cap. The public practice bank is not a high-stakes anti-cheating exam. Existing global legacy XP write/leaderboard policies remain later M7/M9 work; this new isolated path does not certify them.

Rollback the frontend if needed. Preserve earned-event/history tables; disable RPC execution rather than dropping data or blindly subtracting XP. No legacy data rewrite/backfill is required.
