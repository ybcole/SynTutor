# Milestone 09 · Opt-in verified XP rankings

Repository implementation and privacy verification on 8 November 2026 (Asia/Manila). Public release is off by default and requires separate review and an explicit database-owner action. The hosted database has not been changed.

## Participation and ranking

| Decision | Behavior |
|---|---|
| Consent | Private by default, including all existing accounts. A signed-in learner explicitly joins with a chosen alias. |
| Alias | 3–24 ASCII letters, digits, underscores or hyphens, starting with a letter. Active aliases are case-insensitively unique. The server rejects email-shaped strings, reserved provider ID prefixes and the caller's own subject. The UI asks learners to use a nickname. |
| Public fields | Rank, alias and period XP only, for the top 100. No authentication subject, email field, timestamps, level, activity records, or lifetime totals. A separate caller-only field provides personal rank even outside the top 100. |
| Weekly period | Monday 00:00 UTC through the next Monday, end exclusive. |
| Seasonal period | Calendar quarter in UTC, end exclusive. |
| Eligibility | Positive award events from the M7 ledger at or after both the period start and the current opt-in timestamp. Existing private XP stays private. Renaming retains the consent timestamp. |
| Tie-breakers | Period XP descending, then earliest last qualifying award, then case-insensitive alias ascending under the C collation. |
| Withdrawal | Opt-out removes the alias and score from subsequent public responses. A later opt-in starts a new eligibility window. Private XP, level and badges are retained. Previously viewed public entries may have been copied. |

## Authority and storage

The M7 award RPCs and private event ledger remain authoritative. M9 creates a private preferences table and an administrator-only release flag. The write RPC uses the verified Clerk subject and accepts only alias and opt-in state. The read RPC validates the period and projects only public fields from consenting accounts when the release flag is enabled. There is no public table read or direct client write. The frontend displays private lifetime progression separately and handles paused, guest, loading, empty and error states.

## Verification

Native PostgreSQL tests covered default pause, unauthorized settings/flag/XP writes, alias validation and collision, public field minimization, exclusion of pre-consent XP, withdrawal and rejoining, retention of private XP/badges, both UTC periods, deterministic ties, and a private rank outside the public cap. Chromium exercised paused and empty states, period switching, alias opt-in, opt-out, and the private lifetime display against stubbed account transport. No hosted or production flag was changed.

## Release and rollback

1. Review consent copy, alias limitations, tie-breakers, and database access. Apply M7, M8 and M9 migrations in order in staging before deploying the matching frontend.
2. Keep the M9 release flag disabled by default. Verify with a guest and two real Clerk accounts that joining shows only eligible period XP, public rows contain only the three documented fields, withdrawal removes the row from new reads, and direct writes remain denied. Temporarily enable the flag in staging for this test, then disable it.
3. Enable the production flag only after approving the privacy behavior and database access. To roll back public exposure, disable the flag. Keep preferences, achievements and XP records in place. Opt-out is available while paused. Re-enabling preserves existing consent timestamps. New eligibility begins only if the learner opts in again after withdrawing.
