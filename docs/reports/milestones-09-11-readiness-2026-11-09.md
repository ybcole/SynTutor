# Milestones 9–11: integration and merge-readiness review

Review date: 9 November 2026 (Asia/Manila). This report records review of repository code and existing CI evidence. It does **not** record a live Clerk/Supabase test, a human learner session, a production deployment, or project-owner acceptance.

## Repository evidence

| Milestone | PR | Current repository evidence | Outstanding gate |
| --- | --- | --- | --- |
| 9 — Consent-gated leaderboards | [#40](https://github.com/ybcole/SynTutor/pull/40) | Default-off database release flag, private preferences and server-computed weekly/quarterly ranking; aliases and rank-only public projection. Native PostgreSQL tests and head CI pass. | Review actual privacy and access controls using two real Clerk accounts on staging; do not enable rankings until approved. |
| 10 — Adaptive trees and corrections | [#41](https://github.com/ybcole/SynTutor/pull/41) | Responsive measured layout, correct-token guard for an independently reparsed correction, reversible preview, semantic deletion/insertion annotations and keyboard/text alternatives. Browser tests and head CI pass. | Owner design sign-off; independent learner usability sessions, including keyboard/assistive-technology review. |
| 11 — Account integration | [#42](https://github.com/ybcole/SynTutor/pull/42) | Combined M9 + M10 functionality, account-session-bound Supabase token handling, stale account-response suppression, private history and old-version preservation, migration tests and integrated browser checks. Head CI passes. | Confirm real Clerk JWT/Supabase third-party authentication and staged database migration, then owner sign-off. |

Verified PR-head checks before the correction-checklist documentation update:

- M9 commit `8363bc4`: [model-free](https://github.com/ybcole/SynTutor/actions/runs/42469371964) and [parser-backed](https://github.com/ybcole/SynTutor/actions/runs/42469372077) succeeded.
- M10 commit `f3c19e3`: [model-free](https://github.com/ybcole/SynTutor/actions/runs/42473094739) and [parser-backed](https://github.com/ybcole/SynTutor/actions/runs/42473094845) succeeded.
- M11 commit `95b084d`: [model-free](https://github.com/ybcole/SynTutor/actions/runs/42475063897) and [parser-backed](https://github.com/ybcole/SynTutor/actions/runs/42475064006) succeeded.

A later documentation-only commit checks the eleven implemented correction-visualization items in the M11 master checklist. **Check new-head CI again before merging**; the successful runs above predate that change. The milestone tracker itself remains correctly unchecked for M9–M11.

## Correction checklist reconciliation

The eleven checkboxes in **section 4, Corrected sentence visualization**, were left empty even though the M10 prototype documents the implementation and the current M11 branch carries it. They are now checked against the following repository artifacts:

- `web/js/correction.js`: offset-aware construction for replacement, insertion, deletion, punctuation, contractions and multi-token edits; corrected tree/token/leaf ordering verification.
- `web/js/main.js`: retains the original sentence, fetches the corrected parse from the parser separately, rejects stale/mismatched trees, shows the preview, and restores the original.
- `web/js/ui.js`: full corrected sentence, `<del>` / `<ins>` annotations, and labeled corrected B-R or diagnostic tree.
- `scripts/test_tree_layout.js`, `scripts/test_ui_prototype_browser.py`, and the parser-backed real-response correction tests: existing automated verification and screenshots.

These checks **do not** satisfy the separate M10 owner/independent-learner acceptance gates. Do not treat a green automated workflow as a screen-reader accessibility audit.

The integration-branch master checklist now contains **131 checked / 19 unchecked** actionable checkboxes. Major remaining groups: approval of the migration/rollback strategy, optional advanced Cambridge modules, independent UI review, real Clerk/Supabase integrated rollout, and the fourteen M12 quality/release-readiness items. Some M12 implementation tasks already have automated coverage, but the final release milestone must independently reconcile and sign off its scope instead of automatically marking them done.

## Safe release sequence

1. Review the standing privacy rules: aliases are voluntary, public ranking fields are rank/alias/period XP, private lifetime XP and badges are never listed. Confirm opt-out and the default-disabled release flag. Do not enable the production ranking flag.
2. Confirm the deployment path: determine whether merging to `main` automatically deploys Vercel. A merge is **not** a substitute for applying database migrations. Avoid deploying the new frontend against an old database.
3. Back up the staging database and record its applied migrations. Apply only missing migrations in timestamp order, including `20261108000004_verified_progression.sql`, `20261108000005_achievements.sql`, `20261108000006_private_leaderboard.sql`, and `20261108000007_account_integration.sql`. Confirm the earlier M4/M5 schema and catalog seed migrations first.
4. Verify the real integration using two actual Clerk accounts plus a signed-out session. Test account switching during a pending request, private history isolation, lesson completion, quiz score improvement and replay, verified XP/badges, leaderboard consent/withdrawal, and legacy row preservation. Test both database policies and browser behavior.
5. Complete M10 manual review: screenshots and interaction sign-off; independent learner correction, return-to-original, and explanation tasks; keyboard-only or assistive-technology check.
6. Confirm all PR heads pass CI after final changes. Review M9 then M10, followed by M11. Because #42 is stacked on #41 and already includes #40, re-check the resulting `main` diff after each merge to avoid duplicate or conflicting content.
7. Record the real staging results, final privacy approval, and owner acceptance in the corresponding reports and roadmap; only then mark the milestones complete. Proceed with M12 validation before any production release.

## Explicit limitations

The GitHub connector can inspect commits, code, pull requests, CI, and repository files. It does not provide a configured staging Clerk/Supabase environment or participants for independent human usability testing. Those gates cannot be truthfully completed from the repository alone. No live migration, GitHub PR merge, leaderboard activation, or production deployment is claimed by this report.
