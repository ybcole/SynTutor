# SynTutor — Linguistic Reliability Engineering Handoff

Status: Research baseline; production fixes pending
Research commit: 721dfdfc
Branch: research/lref

## Executive Summary

Independent testing reproduced failures involving:

1. Contradictory diagnostic verdicts and explanations.
2. Incorrect attribution of malformed modal constructions.
3. False run-on diagnoses in auxiliary questions.

These findings indicate limitations in diagnostic authority,
grammatical relationship recognition, and clause analysis.

## Priority A — Diagnostic Authority (P0)

Finding: findings/LREF-ISSUE-001.md

Example:
They can the peaches.

Observed:
Verdict is unverified, but explanation asserts grammaticality.

Required:
Reconcile evidence and verdict before producing learner-facing
explanations. Do not certify unsupported constructions.

## Priority B — Auxiliary Relationships (P1)

Examples:
- She cans sing.
- They cans sing.
- Can she sings?
- Does she runs?

Observed:
Missing or incorrect auxiliary-form attribution.

Required:
Recognize auxiliary-complement relationships across declarative
and interrogative structures. Distinguish modal auxiliaries from
legitimate lexical uses of can and cans.

## Priority C — Run-on Detection (P1)

Finding: findings/LREF-ISSUE-003.md

Observed:
Auxiliary questions can be misclassified as fused sentences.

Required:
Establish independent clause boundaries before reporting C-RUNON.
Preserve genuine run-on detection and valid coordination.

## Verification

Run the Flask application using the research checkout and its
required dependencies on localhost port 8001.

Run reference validator tests:

python -m unittest -v \
  evaluation.linguistic_reference.test_validate

Run runtime regression tests:

python -m unittest -v \
  evaluation.linguistic_reference.test_runtime_authority \
  evaluation.linguistic_reference.test_runon_contrasts \
  evaluation.linguistic_reference.test_auxiliary_inversion_positive

Recorded research baseline:
- Reference validation: 11 pass, 0 fail.
- Runtime regression: 4 pass, 7 fail.

The runtime failures are expected on the investigated baseline.

## Evaluation Requirements

Verify improvements using both positive and negative controls.

Measure separately:
- Error detection
- Grammatical attribution
- Span localization
- Structural evidence
- Explanation faithfulness
- Correction safety
- Appropriate abstention

Do not treat these selected tests as population-level accuracy.
All linguistic reference annotations remain provisional.

## Reproducibility Limitations

The research worktree's parent commit was recorded as:
0e1100fc9a657fb63ad619b5dfae84b1c4909677

The running API server's exact commit was not independently
verified. Confirm server provenance before formal comparison.

Model versions and independent reference adjudication
must also be documented before publication-quality evaluation.

## Integration

No production implementation changes are included.

Review proposals against the current integration branch.
Apply fixes through the appropriate development workflow.
Run the LREF tests before and after each change.

See IMPLEMENTATION_PROPOSAL.md for detailed acceptance criteria.
