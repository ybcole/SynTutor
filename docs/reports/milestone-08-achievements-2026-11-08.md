# Milestone 08 · Achievements and mastery

Implementation verified in the repository on 8 November 2026 (Asia/Manila). The educational and exploit-resistance release review is open. No hosted migration has been applied.

## Badge set for review

| Badge | Evidence required |
|---|---|
| First Lesson | One completed lesson |
| Learning Path | Four distinct completed lessons |
| First Assessment | One submitted assessment, including 0/5 |
| Quiz Explorer | Three distinct submitted assessments |
| Personal Best | A higher score than an earlier submitted attempt on the same assessment version |
| Perfect Five | One submitted 5/5 |
| Gap Spotter | Complete the wh-fronting lesson **or** score at least 4/5 on the matching quiz |
| Syntax Checkpoint | Complete the complementisers lesson **and** score at least 4/5 on the advanced checkpoint |
| Steady Practice | Three UTC dates with the first completion or submission of distinct activities. The dates can be nonconsecutive. |
| Framework Distinction | Complete the Cambridge companion lesson **and** score at least 4/5 on its clauses assessment |

The launch catalog is visible and one-time per badge. Its optional reward is the displayed badge itself. Badges grant zero XP and do not gate course content, feedback, or accessibility. Perfection is required for one of the ten badges. The syntax and framework badges represent their specified evidence, with no claim of general mastery.

## Evidence and persistence

- Lesson completion comes from `lesson_progress.completed_at`. Quiz participation, accuracy, and improvement come from submitted `quiz_attempts_v1` rows. A zero-XP submission still counts for participation.
- Catalog rows identify the badge and display properties. Each criterion identifies its activity scope, content version, threshold, and learner-facing label. Criteria in an option are AND conditions. Options are OR alternatives. Launch criteria explicitly reference content version 1.0.0. Publish an explicit criterion revision when new content versions become eligible.
- `get_my_achievements()` reconciles the caller's badges from those records when they open Achievements. It persists one unlock per account and badge. The unlock timestamp is the earliest qualifying evidence time, with a successful AND group using the time its last condition was met. Reopening or simultaneous reads cannot create another unlock. Guests can view criteria with zero personal progress.
- The Generator and Builder currently send evaluation requests without durable, account-bound mastery records. M8 maps their skills to the existing trusted lesson and assessment paths where applicable. Generator or Builder submissions, guest drafts, local estimates, legacy parser-stage counters, and unscored reinforcement do not unlock badges. Direct badges for Generator or Builder need a verified account-bound event path and separate reviewed criteria.
- Remaining abuse tradeoff for review: learners can inspect answers delivered with practice content and submit valid responses. The RPC checks against server-owned catalogs and caps what replays can count toward. Personal Best can be earned after a deliberately low first attempt. It is a single cosmetic badge with no XP incentive.

## Verification and release

Native PostgreSQL tests covered all ten badges, both OR paths, partial and complete AND progress, 0/5, score improvement, replay, two-session reconciliation, durable dates, legacy/draft/version rejection, guest/other-account privacy, and denial of client writes. Chromium checked the badge criteria, timestamps, category filtering, verified XP, account sign-out, and unavailable states with stubbed account/database transport. Lesson, quiz, Builder, level and packaging regressions passed locally.

1. Review the ten badges, the version scope, and the abuse tradeoffs. Check CI before merging. The prior M7 parser CI stopped during the external spaCy download. Model-free checks cover the M7 and M8 account features independently.
2. On staging, confirm the M4/M5 schemas and catalog seeds. Apply M7's `20261108000004_verified_progression.sql`, then M8's `20261108000005_achievements.sql`, before deploying their matching frontend. Run the M7 award, replay and isolation checks with real Clerk accounts.
3. In Achievements, verify an existing account's badges, a new partial then completed condition, replay, and a second account and signed-out session. Check that badge unlocks leave verified XP unchanged. If the M8 frontend must be rolled back, retain the database tables and their unlock rows.
4. For Milestone 9, the plan requires secure XP/level authority and privacy design from M7 plus M1 identity and consent decisions. Review opt-in aliases, ranking exposure, and database access before enabling public rankings. M8's badge review is required before releasing the badges.
