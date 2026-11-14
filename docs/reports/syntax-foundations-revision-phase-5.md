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
- The full Python publication validator runs without loading the parser lemmatizer. It reports existing receipt drift in `br-02`, `br-03`, `br-08` and `cgel-clauses`; the other eight published records pass individually. Commit `7df6b1e` introduced the differences. The affected changes are the Cambridge insight in Chapters 2 and 8, assessment hints and feedback in Chapter 3, and the Cambridge companion's teaching and example-origin wording. The historical catalog and receipts on `main` retain the reviewed wording. Use that wording for the Cambridge companion in the eventual integration and explicitly include revised Foundations wording in the new review receipts.
- Chapter 6 now uses an original instructional tree for the modal–perfect sequence. It retains the printed anchor for the structure it illustrates. The candidate passes the canonical schema, structural rules and guided-target checks. The new tree's independent review remains pending.
- The reference copy used in the pilot receipts was unavailable for a fresh page-level check. First-time learner timings, instructor sign-off and hosted account checks remain pending. The ten-minute catalog durations are estimates.

## Owner walkthrough and timing

In a fresh browser profile, work through Chapter 1's constituent tests and tree repair, Chapter 6's auxiliary chain and branch repair, and Chapter 11's recursive derivation. Repeat the desktop sidebar links with the keyboard or use the Chapter contents dropdown on a phone. The browser test exercised those interactions in desktop light mode and mobile dark mode and checked that the tree pages fit at 390 px. Start each timed run at the introduction and stop when the first closing score appears. Record elapsed time, any pauses and the first point where an instruction, label or example needed rereading. Keep automated interaction times out of the learner timing record.

## Integration with main

A read-only merge simulation against `main` at `c72744c` found seven Git conflicts. Six concern Cambridge coverage, planning, probes or probe tests. The seventh is in `web/js/main.js`. Main's Lessons initialization also lacks the embedded Builder callback used by legacy guided practice. Prepare integration on a branch based on current main, carry over the lesson changes and embedded Builder wiring, and preserve the Generator and Cambridge changes already on main. Rerun the full preview and Builder checks on that integrated tree before preparing any release.

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

## Results on the integration branch

The review branch `feat/lessons/revision-integration` integrates `main` at `c72744c` with the revision branch at `a88db1c`. The six Cambridge conflicts use main's files. The app entry point retains main's Generator workspace setting and adds the lesson route cleanup and embedded Builder callback. The catalog keeps main's reviewed individual lesson records and adds only the Foundations card descriptions. The legacy publication validator now passes all 12 lessons and their existing receipts, and the separate candidate validator passes all 11 revised overlays. No receipts were rewritten. The Builder regression now checks that an exported triangle retains its features, in line with main's canonical tree contract.

The static build, combined preview, published Lessons browser, Builder browser and core, assessments, source validators, tree layout, correction and database cutover/rollback tests passed. The Generator canvas test fails on main and on the integration branch because the English variety control is missing from main's HTML. The server-backed XAI browser test requires Werkzeug, which was unavailable in this environment. Independent source review, first-time learner timing, owner acceptance and hosted checks are still pending.
