# XAI-4 — Cambridge partial checks: technical delivery and blocked source gate

**Date:** 10 November 2026
**Language:** English only
**Technical delivery:** implementation complete, CI verification separately tracked.
**Source-authorized grammaticality release:** NOT COMPLETE — **zero enabled Cambridge diagnostic rules**.

## Baseline and independent review

The production Cambridge allow-list initially had zero active diagnostic rules. The independently reviewed Cambridge teaching template in the existing explanation registry is descriptive, not an error constraint. XAI-PRE documents 13 targeted source claims checked by an assistant, **not independent human linguistic reviewers**. The B-R/Cambridge morphology crosswalks remain pending approval and the auxiliary-head crosswalk is unresolved. The checks below are candidates, not promoted source-backed error diagnoses.

## XAI-4 delivery

- grammar/xai4_candidates.json and its schema: four English-only, disabled rule candidates with typed families, source-claim IDs, preconditions, crosswalks, variety and exception notes and explicit human/test gate fields.
- server/xai4_partial.py: deterministic sentence-token observations including exact original character spans. Source-approval predicates fail closed and reject unchecked crosswalks, review status, exceptions and testing.
- grammar/xai4_partial.schema.json: typed result, no whole-sentence pass; explicit BLOCKED, AMBIGUOUS, NOT_APPLICABLE, UNIMPLEMENTED and independently eligible SATISFIED/VIOLATED states. Token references are not fabricated B-R dependencies.
- Source-audited families: perfect-have participle selection, modal plain form, progressive-be gerund-participle, and present-perfect temporal-adjunct interpretation.
- server/explanations.py, server/tree_evaluation.py, server/api.py: XAI-4 sidecar on explanation, evaluation and parser flows. Raw-token checks remain available if B-R normalization fails.
- web/js/explanation-evidence.js: accessible pending-approval status separate from reviewed book teaching. No blocked candidate is displayed as a verified error.
- server/test_xai4_partial.py: 17 targeted positive/negative/exception, source-gate, API parity and synthetic approved-fixture dependency tests; integrated into mandatory CI.
- Existing XAI-0, XAI-1, XAI-2, XAI-3, Builder and parser-backed baselines remain unchanged.

## What this milestone does not assert

Candidate findings for “She had went home,” “She can goes,” or “She is sing” are **not** activated as Cambridge-certified errors. The engine correctly preserves the lexical use in “She had breakfast,” the copular/passive alternative in “The door is closed,” and the documented experiential ambiguity in “We've already discussed it yesterday.” The synthetic multi-error tests are explicitly **not real human adjudication**.

Production **enabled rule count = 0**. Production approved diagnostic findings = 0. No user-facing verified corrections are newly activated, no migrations are required, and no sentence is certified wholly grammatical merely because no rule fired. The candidate output exposes structural token evidence or BLOCKED/AMBIGUOUS statuses, never an unapproved grammaticality verdict.

## Independent source-release gate outstanding

Human/instructor linguistic sign-off is still required for the actual Cambridge printed-page passages (Ch. 3 pp. 76, 105–106, 143–144), full relevant exceptions, dialect/register policy, explicit B-R comparisons, and held-out false-positive assessment. Only then may a reviewer update the versioned XAI-PRE source audit, rule catalog, and allow-list to enable individual runtime checks after new CI and browser tests. This source-release gate is not completed and cannot legitimately be marked complete by software tests alone. XAI-5 correction lineage and error-to-tree localization remain separate work.
