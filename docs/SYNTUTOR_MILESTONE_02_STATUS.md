# SynTutor Milestone 02 — Progress and Verification Report

**Milestone:** 02 — Syntax Generator and B-R tree normalization  
**Status:** **INCOMPLETE — MUST REMAIN UNCHECKED**  
**Branch:** milestone-02-syntax-generator  
**Latest verified implementation commit:** f67e93cbadb267c205868e44ea49ad0726e12eeb  
**Verification run:** GitHub Actions run 42277179854 — success (7 November 2026, Asia/Manila)

## Summary

Milestone 02 now has a versioned B-R canonical-analysis schema, a fail-closed normalizer/validator, a narrow supported Benepar mapping for V2, explicit unresolved/ambiguous outcomes, a guarded Cambridge runtime-rule registry, API contracts, correction alignment metadata, and regression coverage.

This is a real implementation increment, not a completed general-purpose B-R parser. Most arbitrary Benepar parses—especially V7–V10 structures requiring NP/NOM recursion, auxiliary-headed VP layers, clause layers, wh-movement, indices, and non-finite analysis—remain unresolved unless an exact verified B-R source reference is available. No unverified structural transformation is fabricated.

## Implemented

- server/br_tree.py: canonical B-R node conversion from exact verified source fixtures, V2 S → NP VP mapping, chapter-aware validation, token yield/spans/order checks, feature legality, gaps, indices, triangles, ellipsis/elision, accepted alternatives, movement and controller metadata, and structured unresolved diagnostics.
- grammar/br_tree.schema.json: JSON Schema 2020-12 for normalized and unresolved analysis payloads.
- server/api.py: preserves the raw Benepar candidate as tree / candidate_tree; adds canonical br_analysis, convention metadata, and Cambridge registry result.
- server/webapp.py and server/app.py: accept and validate convention_version V1–V10.
- Correction payload: original/corrected token alignment, edit ranges, affected original terminal IDs, and a separate parse plus B-R normalization attempt for the corrected sentence.
- grammar/runtime_registry.json and server/cambridge_registry.py: explicit fail-closed rule allow-list; no Cambridge rules are enabled by default.
- server/test_*.py: model-free normalizer, schema, Cambridge registry, API, HTTP, correction, and source-fixture tests.
- .github/workflows/syntax-generator-tests.yml: executes the new tests, existing B-R validators, and legacy licensing/correction regression scripts.
- docs/SYNTAX_GENERATOR_B_R.md: request/response and normalization contract.
- docs/adr/0001-linguistic-authority-and-syntax-generator.md: architecture decisions and source crosswalk.
- MASTER_PROMPT.md and CONVENTIONS.md: reconciled B-R structural authority with independently reviewed Cambridge evidence for broader grammatical claims.

## Verification evidence

GitHub Actions run: https://github.com/ybcole/SynTutor/actions/runs/42277179854

- **35 Python tests passed.**
- **All 11 existing B-R chapter validators passed** (validate_ch01.py through validate_ch11.py).
  - Chapters 7–11 report: 447/447, 347/347, 252/252, 215/215, and 143/143 checks passed respectively.
- B-R source-fixture audit: **211 sentence-aligned IMG records; 210 normalized and structurally validated; 1 explicitly unresolved**.
- The remaining record is ch2-2 (V2). Its stored root label is Sentence, which conflicts with the V2 S → NP VP convention. The adapter emits REFERENCE_VALIDATION_FAILED; it does not silently relabel the tree.
- Existing licensing regression: **19/19 ungrammatical examples detected; 16/16 grammatical controls not rejected** (the OOV smartphone example remains unverified rather than being falsely rejected).
- Existing corrector regression: passed.
- JSON Schema validation and Flask request/error contract checks: passed.
- Correction alignment coverage includes replacement, insertion, deletion, multi-token replacement, punctuation changes, contraction expansion, and original-document character offsets.

## Milestone 02 acceptance review

| Acceptance criterion | Status | Evidence / gap |
|---|---|---|
| Canonical schema and br_analysis output | Verified for supported normalized/unresolved payloads | JSON Schema and API contract tests pass; raw tree remains for legacy compatibility |
| Traceable normalization decisions; no silent relabelling | Verified | Exact B-R source provenance and structured diagnostic paths |
| Known B-R gold/source examples validate | Verified for eligible fixtures | 210/211 sentence-aligned IMG records pass; ch2-2 remains explicitly unresolved |
| Unresolved and alternative analyses | Verified | Unit tests cover unresolved, ambiguous reference, and accepted alternatives |
| API/error contract documented and tested | Verified at contract level | SYNTAX_GENERATOR_B_R.md; stubbed API tests and Flask route tests |
| Existing required Generator behavior remains covered | Partially verified | Existing licensing/matrix and corrector regression tests pass; actual Benepar/spaCy-backed end-to-end parsing was not run in CI |

## Remaining blockers before Milestone 02 can be checked

1. **General Benepar-to-B-R normalization:** current non-reference mapping is deliberately narrow (V2 top-level S → NP VP). Implement and test source-backed transformations for the B-R constructions the Generator is expected to support, particularly V3–V10. Unsupported cases must continue to fail safely.
2. **Cambridge rule evaluation:** the runtime registry is only an eligibility gate. It currently enables zero rules; no deterministic Cambridge sentence-level evaluator or Cambridge minimal-pair/exception suite is implemented.
3. **Parser-backed integration:** the CI environment does not install/download en_core_web_md and benepar_en3. Run model-backed smoke tests on the configured runtime and verify real parse output, full/multi-sentence input, corrections, performance, and failure fallback.
4. **Legacy authority boundary:** the legacy matrix/CoLA verdict still runs. It is not a Cambridge verdict and must remain clearly labelled until a reviewed Cambridge evaluator replaces it.
5. **Frontend consumption:** the current frontend still renders the legacy raw tree. Later UI/integration work must render br_analysis and provide visible unresolved/alternative states. The requested strikethrough correction presentation is not implemented in this milestone.
6. **Edition metadata:** confirm the exact B-R and Cambridge editions/page numbering against the original supplied PDFs.

## Data and migration impact

No database schema or user-progress migration was performed. The raw Benepar tree and legacy verdict remain available for backward compatibility. The new canonical analysis is an additional API field. The Cambridge allow-list is empty. No feature has been activated for downstream Lessons, Quizzes, or Builder workflows.

## Sign-off

Milestone 02 remains unchecked in the 12-Prompt Execution Plan. This is intentional: passing the new adapter tests and source validators does not satisfy the unfinished general normalization, Cambridge evaluator, and actual parser-integration requirements.

Do not start Milestone 03 or downstream work that depends on complete canonical Generator behavior until the owner reviews the sample outputs and the remaining criteria are completed.
