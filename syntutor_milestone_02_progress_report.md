# SynTutor — Milestone 02 Progress Report

**Overall status: INCOMPLETE.** Milestone 01 is approved and complete. Milestone 02 has substantial verified implementation but must remain unchecked.

## Repository work

Branch: `milestone-02-syntax-generator`  
Latest implementation commit: `f67e93cbadb267c205868e44ea49ad0726e12eeb`  
CI workflow: [Run 42277343237](https://github.com/ybcole/SynTutor/actions/runs/42277343237)  
Repository progress report: `docs/SYNTUTOR_MILESTONE_02_STATUS.md`

## Verified results

- 35 Python tests passed.
- All 11 existing B-R validators passed.
- 210 of 211 sentence-aligned IMG records normalized and passed structural validation.
- `ch2-2` remains explicitly unresolved because its stored `Sentence` root conflicts with the V2 `S → NP VP` convention.
- Existing licensing regression: 19/19 ungrammatical examples detected; 16/16 grammatical controls not rejected.
- Existing corrector regression passed.
- JSON Schema, Generator API contract, correction alignment and Flask route tests passed.

## Implemented

- Versioned canonical B-R tree schema and structural validator.
- Conservative normalizer using exact IMG-verified references and a narrow V2 S → NP VP mapping.
- Explicit unresolved, ambiguous, and accepted-alternative outcomes.
- Raw Benepar candidate kept separately from `br_analysis`.
- Chapter convention selection V1–V10.
- Cambridge runtime allow-list with no rules enabled by default.
- Correction edit alignment and independent corrected-sentence parse attempt.
- Governance revisions and architecture decision record.

## Why Prompt 02 is not complete

1. General Benepar-to-B-R conversion for V3–V10 constructions is not implemented.
2. The Cambridge registry is not yet a sentence-level Cambridge rule evaluator; no Cambridge rules are enabled.
3. Real spaCy/Benepar-backed end-to-end and multi-sentence tests have not been run.
4. The legacy matrix/CoLA still supplies the existing verdict.
5. The frontend still renders the legacy raw tree; canonical B-R rendering and visual correction annotations are outstanding.
6. Exact B-R/Cambridge edition metadata still needs confirmation against original PDFs.

**Tracker decision:** Milestone 01 `[x]`; Milestone 02 `[ ]`. This follows the rule that a milestone may be checked only when every applicable acceptance criterion is verified.
