# Syntax Foundations Phase 5 integration review

The local candidate combines the eleven Burton-Roberts pilots at version `2.0.0`. Start the static app from the revision branch with `python -m http.server 8000 --bind 127.0.0.1 --directory web`, then open the [full Foundations preview](http://127.0.0.1:8000/?preview=foundations#lesson/catalog). The preview has its own device progress and drafts. The separate chapter preview links remain available.

## Verification

| Check | Result |
| --- | --- |
| Catalog schema and assessment coverage | All eleven overlays compose together. All 110 assessment items have in-chapter printed page anchors and the closing checks cover the declared outcomes. The Chapter 6 overlay no longer writes an unused field outside the course schema. |
| Static browser integration | All authored required sections open through their direct routes. Chapters 2, 6 and 11 exercise score feedback and XP increases from 9 to 15. The test covers desktop and 390 px, separate preview drafts, published progress isolation and Cambridge access after revised Chapter 2. |
| Database rehearsal | A disposable PostgreSQL instance applied the actual migrations and seeded all eleven versions twice. All chapters completed out of order with the real answer keys. Opening checks and repeated submissions earned zero extra XP. Cutover retained historical records, Cambridge completion and quiz XP. Rollback restored legacy XP and retained revised attempt history. |
| Existing regression suites | Lessons, assessments, Builder, tree layout and static packaging passed. |

## Publication evidence still needed

- The structural and page-range checks establish that the assessment anchors resolve. The chapter reports carry the detailed source checks. In particular, Chapters 1–3 use existing catalog anchors that are narrower than the ranges recorded for individual questions in their reports. Reconcile those item-level anchors with the cited edition and record independent content, figure and notation review before issuing new publication receipts.
- The unchanged published catalog already differs from its recorded receipts for `br-02`, `br-03`, `br-08` and `cgel-clauses`. The hashes were compared directly. The full Python publication validator also requires `lemminflect`, which is unavailable in this environment. Resolve the receipt differences against their reviewed versions and rerun the gate with the dependency installed. The Cambridge receipt requires its own source review.
- Chapter 6’s pilot tree is adapted from a printed example and carries `IMG` evidence. The legacy publication validator expects instructional trees to carry `TXT`. Review the adaptation and reconcile the tree's evidence classification with the publication rule before merging its overlay into the published catalog.
- First-time learner timings, broader visual and accessibility review, instructor sign-off and hosted account checks are pending. The ten-minute chapter durations are estimates.

## Release and rollback rehearsal

Generate a local candidate and its inactive seed from the same overlays used in the browser.

```sh
node scripts/compose_foundations_preview.js > /tmp/foundations-candidate.json
python scripts/seed_foundations.py --course /tmp/foundations-candidate.json > /tmp/foundations-candidate.sql
python scripts/test_foundations_preview_catalog.py
node scripts/test_foundations_preview_database.js
npm run build
python scripts/test_foundations_preview_browser.py
```

After Gate 5, freeze the reviewed catalog and its matching seed. Record the current deployed catalog, active versions and ledger totals and take restorable database and artifact snapshots. Stage the approved seed as a new migration and verify its eleven rows while inactive. Rehearse the catalog release and version switch together in staging, then coordinate the hosted cutover and verify a fresh account and a returning account. Confirm that the new versions start incomplete with zero revised lesson XP and that Cambridge and quiz history still count.

If a cutover must be reversed, restore the prior static release and call `public.set_foundation_active_version(chapter_id, null)` for each switched chapter in one transaction. Verify that legacy XP returns and that Cambridge and quiz records still count. Keep the revised progress and attempt rows for audit and possible reactivation.
