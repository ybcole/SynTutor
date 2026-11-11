# LREF-ISSUE-003: False Run-on Attribution in Auxiliary Questions

Status: Reproduced — unresolved
Priority: High
Tested commit: 0e1100fc9a657fb63ad619b5dfae84b1c4909677
Reference status: Provisional linguistic expectations

## Problem

SynTutor incorrectly reports C-RUNON for malformed
subject-auxiliary inversion constructions.

## Reproducing examples

1. Can she sings?
   Observed: C-RUNON
   Expected: Modal-complement form violation;
             no run-on violation.

2. Does she runs?
   Observed: C-RUNON
   Expected: Auxiliary-complement form violation;
             no run-on violation.

## Controls

3. Can she sing?
   Observed: No C-RUNON
   Expected: No C-RUNON

4. She sings he dances.
   Observed: C-RUNON
   Expected: Fused-sentence violation

5. She sings and he dances.
   Observed: No C-RUNON
   Expected: No C-RUNON

## Root cause

The run-on heuristic in server/ruleset.py examines
sequences containing two finite-tagged tokens with
an intervening pronoun or noun.

This pattern is insufficient to establish the existence
of two independent clauses.

A malformed auxiliary question can satisfy the heuristic
without containing a fused-sentence construction.

## Required improvement

Distinguish independent clause boundaries from
subject-auxiliary inversion.

Validate auxiliary-complement forms independently.

Avoid treating parser POS tags alone as sufficient
evidence of a run-on construction.

## Acceptance criteria

- No false C-RUNON in the two auxiliary-question cases.
- Correct auxiliary-form errors are identified.
- Actual fused-sentence errors remain detectable.
- Valid coordination remains accepted.
- Diagnostics include appropriate structural evidence.
- Findings generalize to additional contrastive examples.
- Tests pass on the eventual integration commit.

## Reproduction test

evaluation/linguistic_reference/test_runon_contrasts.py

Current result: 3 passed, 2 failed.

## Research implications

Relevant to grammatical attribution, diagnostic precision,
structural evidence, and explanation faithfulness.

These are targeted regression results, not a representative
population-level accuracy estimate.

## Integration boundary

No production code is modified by this finding.


## Positive diagnostic-attribution regression

Additional test:
evaluation/linguistic_reference/
test_auxiliary_inversion_positive.py

Observed on commit:
0e1100fc9a657fb63ad619b5dfae84b1c4909677

Results:
- Can she sings?: FAIL; only C-RUNON reported.
- Does she runs?: FAIL; only C-RUNON reported.

Both failures reproduce the absence of an appropriate
auxiliary-form diagnosis.

The positive tests are implementation-specific and use
the existing C-AUX-FORM and C-MODAL-VERB-FORM identifiers.

A future unified diagnostic contract should additionally
verify the affected verb span, grammatical relationship,
source evidence, explanation, and correction.

## Proposed architectural direction

1. Extract auxiliary-complement relationships across
   declarative and inverted clause structures.
2. Reuse grammatical form checks across both structures.
3. Require independent-clause evidence before reporting
   a fused-sentence violation.
4. Preserve genuine run-on detection and valid questions.
5. Handle lexical ambiguity and unsupported structures
   without inventing grammatical diagnoses.
6. Validate corrections separately from diagnostics.

The proposal requires code review and independent
linguistic evaluation before implementation is accepted.
