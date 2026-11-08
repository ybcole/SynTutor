# Milestone 07 · Verified XP and progression

Status on 8 November 2026 (Asia/Manila) — repository acceptance complete. The owner authorized proceeding and delegated approval of the existing reward rules, pilot curve, and legacy balance handling. The hosted database has not been changed.

## Baseline

Main at `4df61fa` contains the Milestone 1–6 implementation branches, including the M4 lessons, M5 quizzes, and M6 Builder from PRs #35–37. The remaining unmerged branches cover older correction, sign-in, semantics, and chapter work. The M4/M5 migrations were reported applied by the owner in the M6 handoff. Their hosted deployment status was not independently verified.

## Approved repository reward policy

- A completed lesson earns 15 XP once for its published content version.
- A five-item quiz targets `max(0, 10 - 2 × incorrect)` XP. The RPC pays only the increase over the prior best reward for that assessment version. Unanswered items count as incorrect. A 3/5 followed by a 5/5 earns 6 then 4 XP. A repeated 5/5 earns zero.
- Builder work, reinforcement quizzes, and legacy achievements carry no XP under M7. The level tracker shows a personal milestone every time the learner crosses a threshold. No essential learning material depends on level. Optional future rewards can be cosmetic badges or suggested challenge tiers. Their implementation belongs to later milestones.
- Only recorded M4/M5 awards count toward verified XP. The old client-writable totals are preserved in a restricted administrative snapshot and excluded from progression. An account with no recorded awards starts at zero verified XP. Guest or offline displays can show device estimates while account XP comes from the server.

### Pilot curve comparison

Illustrative scenarios use the shipped catalog of 12 lessons and 16 assessments. The steady and full-catalog scenarios assume a first best score of 3/5 on each attempted assessment. These scenarios are planning estimates.

| Curve | XP at levels 1–5 | Early practice, 4 lessons + 4 quizzes at 2/5 (76 XP) | Steady practice, 8 lessons + 8 quizzes (168 XP) | Full catalog (276 XP) |
|---|---|---:|---:|---:|
| Legacy geometric | 50, 130, 258, 463, 791 | 1 | 2 | 3 |
| Flat 100 XP per level | 100, 200, 300, 400, 500 | 0 | 1 | 2 |
| Proposed pilot, 100 + 20 × current level | 100, 220, 360, 520, 700 | 0 | 1 | 2 |

The pilot keeps early pacing similar to the flat curve and avoids the legacy curve's steep later jumps. The first level takes seven lessons, ten perfect quizzes, or a mix. Completing the entire launch catalog with perfect quizzes yields 340 XP, 20 short of Level 3. Reassess after a pilot using observed completion and best scores.

## Verification

| Criterion | Implementation and evidence |
|---|---|
| Reward formula and level thresholds | Kept M4/M5 reward rules. PostgreSQL verified scores 0–5 and a real account crossing 100 XP. JavaScript checks 1,000 level boundaries. |
| Replay, retry and concurrency | Reused the event keys, version caps, and per-account transaction lock. The native PostgreSQL test observed four blocked second sessions and checked one-time lessons, duplicate quiz attempts, simultaneous lesson and quiz awards, and concurrent quiz improvements. |
| Trusted award and read paths | Direct stats writes denied for both API roles. Invalid payloads and unknown lesson versions rejected. Anonymous and other accounts cannot read private progression or the ledger. Rankings are paused and legacy quiz history is own-only. |
| Versioned evidence and reconciliation | `xp_activity_ledger` projects the existing lesson and quiz events with activity type, content version, event key, result evidence, amount, and timestamp. `get_my_progression()` derives the signed-in account's total and level from these events. Cutover and new-award tests reconcile the compatibility cache with the ledger. |
| UI | Achievements shows verified XP, source breakdown, and XP remaining to the next level. Guest and unavailable states are explicit. Chromium verified the XP breakdown, progress bar, unavailable and signed-out states, and absence of public ranking requests with a stubbed Clerk/Supabase transport. |

Local checks passed: `python scripts/test_progression_database.py` on native PostgreSQL with a disposable database; `node scripts/test_level.js`; npm lesson, assessment, Builder, evidence, correction and legacy quiz checks; M4–M6 contract validators; 134 model-free backend tests; static build, upload filtering and backend runtime packaging. The M7 progression browser test and the M4 lesson, M5 quiz, and M6 Builder browser regressions passed in headless Chromium. GitHub Actions model-free checks passed. The parser-backed job received HTTP 504 downloading the spaCy model before running tests. A retry was requested. Hosted Clerk/Supabase verification remains separate.

The trusted RPCs validate submitted completion and answer data against published catalogs. Learners can still inspect client-delivered practice content and automate valid submissions. The per-version caps limit the reward available through those paths.

## Staging and release

1. Confirm GitHub Actions results and merge the reviewed branch. Repository policy approval is recorded above.
2. Have the database owner confirm that M4/M5 schemas and their catalog seeds are applied, and that the target runs PostgreSQL 15 or newer. Back up the database. Apply `20261108000004_verified_progression.sql` in staging before deploying the M7 frontend. The migration briefly locks the award and stats tables during the snapshot and reconciliation, so schedule the production cutover accordingly.
3. In staging with real Clerk sessions, finish a lesson, improve a quiz score, replay both, and check the Achievements XP display. Use a second account and a signed-out session to check that the ledger and private stats are isolated. Validate reconciliation against the ledger and review accounts affected by excluding legacy balances.
4. After approval and a passing staging check, apply the migration to production and deploy the M7 frontend. Production activation is separate from the local verification.

A migration failure rolls back the transaction. If the frontend must be rolled back after a successful migration, keep database protections and recorded award events in place. The prior frontend can still save lesson and quiz results through the existing RPCs, and the legacy public leaderboard cannot read other users' rows. Roll the progression UI forward after fixing any issue. Keep the historical snapshot for review. Restoring old balances to verified XP would require a separate, explicitly approved policy and audit.
