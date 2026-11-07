# Milestone 04 — Lessons implementation brief

This restores the missing named workstream prompt from the existing execution
plan and `master_plan.md` Lessons section. It does not replace their acceptance
criteria. The owner authorized proceeding with M4 after the M1–M3 handoff.

Implement a versioned, source-reviewed course with B-R chapter progression and
selected Cambridge companions. Each published lesson requires outcomes,
prerequisites, prediction, explanation, worked example, guided practice,
transfer and exit check. Chapter 11 remains text-only. Preserve B-R profiles,
source/citation/review metadata and accepted-alternative fields. Teach only the
reviewed scope; planned modules must not appear as published instruction.

Review representative early, middle and advanced content before publishing the
full launch catalog. Use original example/question wording and source-checked
answer structures. The lesson renderer must not grade against live Benepar
predictions. The shared M3 evidence service may supply additional reviewed
notes; missing templates must not invent claims.

Replace the active legacy lesson entry point; preserve its source and historical
learner records separately. Audit every legacy topic and record replacement,
reframing, removal or planned coverage. Keep standalone assessments for M5 and
the full chapter-aware free-form Builder for M6. Guided lesson label/feature
completion can operate directly on an authored canonical tree.

Persist stage, answers and completion by identity, lesson ID and content version.
Completion requires all stages, correct guided/transfer/exit answers and the
versioned prerequisite. A prediction can be wrong without losing XP. Award 15
lesson XP once per content version. Repeated submissions must be idempotent.
Keep local progress available during network failure, isolate accounts, and
make account sync state visible. Do not import old unversioned quiz counts as
source-reviewed lesson mastery. Prepare and test any new database migration;
never claim a hosted migration or deployment that has not occurred.

Verify schema/provenance/answer/tree integrity, navigation/rendering/feedback,
resume/reload, content-version isolation, reward idempotency, and account write
boundaries. Review early/middle/advanced desktop/mobile screens. Run applicable
existing regressions and CI before merging. Synchronize the tracker, checklist,
source receipts and acceptance report with observed results.
