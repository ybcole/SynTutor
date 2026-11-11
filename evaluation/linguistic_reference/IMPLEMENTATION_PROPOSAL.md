# SynTutor: Linguistic Reliability Improvement Proposal

Status: Proposed — not implemented
Research baseline: 0e1100fc9a657fb63ad619b5dfae84b1c4909677
Reference status: Draft; independent linguistic review pending

## Objective

Improve grammatical error attribution, structural evidence,
uncertainty handling, and learner-facing explanations without
introducing sentence-specific patches.

## Workstream A: Diagnostic Authority (P0)

Evidence: LREF-ISSUE-001

Problem:
The rule matrix can assert grammaticality before the
acceptability-model verdict is reconciled.

Recommendation:
Produce a unified diagnostic outcome from all available
evidence before generating learner-facing explanations.

Acceptance:
- No categorical grammatical claim for unverified input.
- Model disagreement does not invent a grammatical error.
- Supported local violations remain reportable.
- Canonical-tree status is kept distinct from grammaticality.
- Each diagnostic records its source and authority.

## Workstream B: Auxiliary Relationships (P1)

Evidence: Modal regressions and LREF-ISSUE-003

Problem:
Existing auxiliary-form checks do not reliably cover
subject-auxiliary inversion or malformed intended modals.

Recommendation:
Introduce a shared representation of auxiliary-complement
relationships, including links across SQ and VP structures.

Acceptance:
- Recognize valid modal and do-support questions.
- Identify incorrect complement forms in inverted questions.
- Do not misattribute malformed modals to agreement alone.
- Preserve legitimate lexical uses of can and cans.
- Identify affected spans and structural evidence.
- Abstain where the intended construction is unsupported.

## Workstream C: Clause Boundaries (P1)

Evidence: LREF-ISSUE-003

Problem:
Finite-verb sequences can trigger a false run-on diagnosis
without establishing two independent clauses.

Recommendation:
Base fused-sentence detection on justified clause-boundary
relationships rather than finite-token counts alone.

Acceptance:
- Preserve genuine fused-sentence detection.
- Preserve valid coordination.
- Do not classify auxiliary inversion as a run-on.
- Include evidence identifying both proposed clause units.

## Evaluation Requirements

Use independent reference annotations for:
- Grammatical construction and error category
- Affected token and character spans
- Expected structural relationships
- Explanation requirements
- Acceptable corrections
- Uncertainty and abstention

Report separate results for:
- Error detection
- Error-category attribution
- Span localization
- Tree and relationship accuracy
- Explanation faithfulness
- Correction safety
- Abstention behavior

Do not equate a successful correction, normalized tree,
or absence of detected violations with verified correctness.

## Integration Conditions

- No direct modifications to teammates' active worktrees.
- Review proposals against the latest integration commit.
- Obtain independent linguistic review of reference cases.
- Run LREF regressions before and after implementation.
- Add new contrastive cases to check generalization.
- Record model versions, commit, dataset revision, and results.
- Do not report performance gains without comparative evidence.

## Existing Regressions

- test_runtime_authority.py
- test_runon_contrasts.py
- test_auxiliary_inversion_positive.py

These are provisional tests against the local research baseline.

## Scope of LREF

LREF provides independent reference data, regression tests,
failure analysis, and evaluation methodology.

Production implementation and final integration require
separate review and coordination.
