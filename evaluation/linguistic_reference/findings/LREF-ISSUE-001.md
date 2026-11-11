# LREF-ISSUE-001: Contradictory Diagnostic Authority

Status: Reproduced — unresolved
Priority: High
Tested commit: 0e1100fc9a657fb63ad619b5dfae84b1c4909677
Test environment: Local Flask API, port 8001
Reference status: Draft, not expert-adjudicated

## Reproduction

Input: They can the peaches.

Observed:
- Legacy rule violations: none
- CoLA p(acceptable): 0.1413
- Final verdict: unverified
- Primary explanation: sentence "is grammatical"
- B-R analysis: unresolved

The original sentence permits a grammatical interpretation
in which "can" means to preserve food in cans.

## Root cause

server/matrix.py generates a categorical grammatical
explanation when no violation is found.

server/detector.py combine() changes the verdict to
unverified when the acceptability model rejects the input,
but retains the earlier grammatical explanation.

server/api.py subsequently presents the combined summary.

## Required correction

1. Distinguish no-supported-error from verified grammaticality.
2. Reconcile diagnostic evidence before producing final feedback.
3. Do not present acceptability-model disagreement as a
   verified grammatical error.
4. Keep canonical-analysis uncertainty distinct from
   local diagnostic evidence.
5. Preserve the original findings and authority information.

## Acceptance criteria

- Verdict and explanation must not contradict each other.
- Unverified results must not assert grammatical certainty.
- Supported local errors remain reportable with their evidence.
- Unsupported constructions must not be certified.
- A model rejection alone must not invent a grammatical rule.
- Contrasting lexical/modal "can" constructions are tested.
- Tests pass on the actual integration commit.

## Existing reproduction

evaluation/linguistic_reference/test_runtime_authority.py

Expected failing test on this commit:
test_unverified_verdict_not_certified

## Research implications

Relevant to diagnostic reliability, explanation faithfulness,
linguistic coverage, and Chapter III methodology.

This is a confirmed runtime inconsistency, not a measured
population-level grammatical error rate.

## Integration boundary

No production changes made by LREF.
A separately reviewed fix is required.
