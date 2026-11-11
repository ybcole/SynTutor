# SynTutor Independent QA Report

Date: November 11, 2026
Reference: main at 5320ecee (PR #82)
Testing environment: Local QA backend, port 8001

## Results

47 targeted checks:
- Passed: 31
- Failed: 16

No changes observed against the previous QA baseline.

## Existing findings

- QA-007: Modal inflection errors missed or misclassified.
- QA-008: Lexical "can" incorrectly treated as a modal.
- QA-009: Modal questions misclassified as run-ons.
- QA-010: Correction and explanation inconsistency.
- XAI: Six explanation-quality requirements not met.

## Diagnostic contract

Three tests fail because the proposed diagnostic_status
field is not yet integrated into the main backend.

The experimental implementation is preserved separately
on fix/friday-verdict-safeguard.

## Interpretation

These are targeted regression checks, not a representative
measurement of overall grammatical accuracy.

The Cambridge extraction workflow was updated in PR #82,
but that does not establish Cambridge detector readiness.

## Next QA priorities

1. Independently verify linguistic expectations.
2. Strengthen the grammar evaluation corpus.
3. Check explanation and correction consistency.
4. Rerun regression tests after integration milestones.
5. Report reproducible failures without changing
   production implementation.
