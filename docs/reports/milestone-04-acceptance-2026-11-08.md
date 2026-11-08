# Milestone 04 — Lessons and curriculum acceptance

Date: 8 November 2026 (Asia/Manila).

## Result

M4's launch curriculum and implementation are complete and locally verified.
The active Lessons entry point now serves 11 chapter-ordered B-R lessons and one
Cambridge companion. Seventeen further Cambridge topics are explicitly planned,
not published. This is a scoped launch course, not full coverage of either book.
M5 standalone assessments and M6 free-form chapter-aware Builder remain separate.

**Deployment follow-up:** the two prepared Supabase migrations have not been
applied to production. Device-local progress works for guests and accounts;
account cloud synchronization and trusted shared player XP need those migrations.
The UI reports sync unavailability/pending state. No production database save or
live migration is claimed. See [progress/deployment](../curriculum/progress-and-deployment.md).

The named `master_prompt_lessons.md` was absent. Its implementation brief was
restored from the unchanged execution-plan acceptance criteria and master-plan
Lessons section. The owner's instruction to proceed and standing milestone
authorization cover the implementation/review gate. No human instructor sign-off
is manufactured: content records/receipts explicitly identify the AI review.

## Acceptance criteria

| Existing M4 criterion | Implementation and verification |
|---|---|
| Every published lesson has outcomes, prerequisites, worked examples, practice and exit check | Versioned course schema; 12 lessons each with an assessed outcome, prerequisite/version, prediction, explanation, three worked steps, guided/transfer/exit activities and exact answer feedback. All rendered/completed in Chromium. |
| Analyses use stage-appropriate B-R conventions | Ten authored canonical trees validated by the approved JSON Schema and structural validator; stored profile matches the lesson. V7-CORE explicitly excludes Appendix refinement. V8 uses C/S-bar; V9 uses C1/C2 and typed gaps; V10 displays the source's feature-only untensed auxiliary node; Ch11 has no tree/profile. |
| Cambridge selection is accurate, cited and does not override B-R | One companion and two aligned insight cards reuse the reviewed CLS-001 classification scope, printed pp.44–45. No new runtime constraint or raw crosswalk mapping is enabled. B-R labels remain unchanged. |
| No unsupported/unreviewed extraction is authoritative instruction | All blocks/questions have reviewed page source IDs; lesson/source hashes bind the review receipts. Missing/unreviewed source or content drift fails validation. Twenty old parser topics are audited/archived outside the static app; planned modules are visibly unpublished. |
| Progress/completion/version are consistent | Pure stage/answer/prerequisite rules; per-identity/per-version stores; resumable stages; 15 XP once after all required activities/exit; no replay increment. Old version records remain historical. Account sync is a server-validated idempotent RPC, with explicit local/offline fallback. |
| Navigation/rendering/feedback/persistence are tested | Full Chromium course completion, wrong exit feedback/blocked completion, reload/resume, 180 XP once/replay, track navigation, planned status, mode teardown and no lesson parser request. Separate JS and real PostgreSQL tests exercise version/identity isolation, prerequisites and reward/write boundaries. |

## Source and representative review

The early/middle/advanced samples were br-01, br-06 and br-10. Their original
content/answer shapes were checked against the supplied source pages before
publishing the full launch catalog. Desktop and 390-pixel mobile screenshots
were inspected. The source review then covered each published unit's limited
claims/answers, preserving a distinction between inspected image anchors and
text-checked page prose. The receipts record the exact content/source hashes.

The same assistant performed a separate verification pass after drafting; this
is not represented as a different human instructor or a different model. The
review found and repaired two exit-task alignment issues: br-10 now directly
tests the untensed-auxiliary/VP representation, and the Cambridge exit directly
classifies an embedded clause. It also preserved the p.226 feature-only display
rather than presenting the internal canonical `AUX` tag as a printed book label.

No source PDF, extracted chapter text or source page image is committed. New
examples and question wording are original. A local scan found no 13-word source
run in the new B-R teaching prose/steps. Comparison fixture IDs do not promote
the whole gold corpus into independently reviewed lesson material.

## Observed checks

- `python scripts/validate_lessons.py`: 12 reviewed lessons, 25 printed-page
  sources, ten canonical trees, concept/reference/answer/outcome/receipt and
  SQL seed integrity passed.
- `npm run test:lessons`: stage/review/prerequisite gates, wrong prediction
  tolerance, version/history isolation, reload storage, unavailable storage,
  offline account sync, repeated/concurrent submissions and server award outcome
  handling passed. Actual PGlite PostgreSQL executes the migrations/seed/RLS/RPC;
  anonymous/direct writes, forged XP, unknown versions and wrong/missing work
  are denied or receive no reward; account reads remain isolated.
- `python scripts/test_lessons_browser.py`: all 12 lessons completed through
  rendered controls; representative desktop/mobile trees, wrong-answer feedback,
  resume/reload, exactly 180 lesson XP, replay protection, planned modules and
  workspace return passed without a lesson parse request.
- Existing 121 model-free backend tests passed. Generator/Builder real
  parser/HTTP/browser evidence parity passed with both production sources and
  the isolated synthetic fixture.
- JavaScript evidence/correction/legacy content regressions, static build,
  Vercel upload-filter reproduction and runtime packaging fixture passed.
  Existing full parser/gold/chapter suites remain in CI for the publishing PR.

Browser tests isolate external authentication; PostgreSQL tests mock verified
request claims in an isolated engine. These are not claims of hosted Clerk/
Supabase configuration or production load verification. The SQL test's concurrent
requests share a serialized WASM engine; multi-connection hosted load is not
claimed. Existing global legacy leaderboard/XP policies remain later M7/M9 work.

## Migration, rollback and handoff

No legacy quiz/history/player row or guest XP record is rewritten. The old
20-topic module is archived for audit; it no longer supplies public lesson
content or its old completion/reward path. The new content, source receipts,
curriculum map, lesson schema and progress contract are the M5/M6 handoff.

For cloud account rollout, deploy the two additive prepared migrations through
the normal project process. Their unique activity ledger/RPC supplies the new
lesson award path without accepting caller-supplied XP or identity. A frontend
revert restores the prior module if required; database rollback should retain
award history and disable execution rather than blindly deleting earned XP.

References: [curriculum map](../curriculum/README.md),
[legacy audit](../curriculum/legacy-lesson-audit.md),
[progress and deployment](../curriculum/progress-and-deployment.md).
