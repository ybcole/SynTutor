
# SynTutor — Friday Prototype Fix Priorities

## P0 — Must address before demonstration

- [ ] Remove unsupported claims of verified grammatical correctness.
- [ ] Fix or safely suppress misleading run-on diagnostics in modal questions (QA-009).
- [ ] Coordinate individual grammar explanations with selected corrections (QA-010).

## P1 — High-priority linguistic quality

- [ ] Correct inconsistent central-modal inflection diagnostics (QA-007).
- [ ] Improve contextual, educationally useful XAI explanations.
- [ ] Investigate lexical/modal ambiguity in syntax-tree normalization (QA-008).

## Validation requirements

- Reproduce each defect before modifying implementation.
- Keep acceptable contrastive sentences working.
- Rerun all relevant regression and quality checks.
- Distinguish independently verified behavior from legacy heuristic results.
- Do not claim book verification without appropriate evidence.

## Current QA baseline

- Automated checks: 27 passed, 13 failed.
- Legacy error-detection F1: 88.9% on 11 selected examples.
- Correct detection and attribution: 3/5 labeled error cases.
- Normalized structural coverage: 5/6 acceptable examples.
- Cambridge runtime verification: not established for tested cases.

All metrics are preliminary and based on a small draft-labeled corpus.

## QA-009 — Modal questions incorrectly diagnosed as run-ons

**Priority:** P0
**Primary implementation:** server/ruleset.py

### Required changes

1. Make C-RUNON distinguish improperly joined clauses
   from a single interrogative clause with auxiliary inversion.

2. Extend C-MODAL-VERB-FORM to inspect the lexical VP
   selected by a modal in SQ structures.

3. Generate the correction "Can she swim?" for
   "Can she swims?".

### Acceptance criteria

- test_question_modal.py: 4/4 passing
- test_runon_controls.py: 3/3 passing
- Existing grammar and structural regression tests remain passing
- No contradictory run-on diagnostic for the corrected question

### Implementation constraints

- Do not use sentence-specific exceptions.
- Do not disable all run-on detection in questions.
- Preserve uncertainty and diagnostic provenance.
- Keep the independent QA branch separate from implementation.
