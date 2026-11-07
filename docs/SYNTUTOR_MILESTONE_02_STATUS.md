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


---

## Milestone 02 continuation report — 7 November 2026

**Status: INCOMPLETE. M2 remains unchecked.**  
**Continuation branch:** `feature/milestone-02-completion-2026-11-07`  
**Draft pull request:** [#30](https://github.com/ybcole/SynTutor/pull/30)  
**Latest successful verification:** [GitHub Actions run #35](https://github.com/ybcole/SynTutor/actions/runs/42346333169)  
**Verified head:** `408ed2fab5abec634177bb462f0f48605e546d9e`

### 1. Files inspected

The root execution plan, detailed `master_prompt_syntax_generator.md`, master checklist, M1 architecture/source-governance ADRs, canonical schema documents, the runtime `grammar/br_tree.schema.json`, B-R chapter tree JSONs and validators, Cambridge rule registry, API and parser modules, correction modules, existing tests, and the Syntax Generator CI workflow.

### 2. Files changed on this continuation

- `server/api.py` — one active `br_analysis` result, chapter/profile validation, profile metadata, corrected-analysis profile propagation, and CoLA advisory declaration.
- `server/br_tree.py` — Chapter 7 core/Appendix D1 source-reference separation.
- `server/webapp.py`, `server/app.py`, `server/hf_space.py` — consistent chapter/profile routing and validation across transports.
- `server/test_api_contract.py`, `server/test_webapp_contract.py`, `server/test_br_tree.py` — profile routing, mismatch rejection, D1 separation, and selected-sentence API contracts.
- `server/test_detector.py` — CoLA advisory-only contract tests.
- `server/test_br_tree_fixtures.py`, `server/test_burton_roberts.py` — source-refinement fixture handling and metadata assertion.
- `.github/workflows/syntax-generator-tests.yml` — run the additional CoLA suite, importer suite, and full source-record audit.
- `docs/syntax-generator-api.md` — current request/response boundary, unresolved behavior, and explicit schema compatibility issue.
- `master_checklist.md`, `syntutor_12_prompt_execution_plan.md` — synchronized progress/evidence records. M2 remains unchecked.

### 3. Acceptance review

| Criterion | Result | Evidence / remaining gap |
|---|---|---|
| Generator output conforms to the approved canonical schema | **Not verified** | Runtime `br_analysis` uses `grammar/br_tree.schema.json`, whereas M1 ADR D3 approves `docs/canonical-burton-roberts-tree.schema.json`. The source importer validates its projection against the M1 envelope, but the API does not currently return that envelope. These formats need reconciliation and an API-level schema test. |
| Traceable normalization; unsupported mappings not silently relabelled | **Partially verified** | Exact IMG source references and the narrow V2 `S → NP VP` mapping are guarded; unsupported analyses return unresolved diagnostics. General V3–V10 candidate transformations remain unsupported. |
| Known B-R gold examples pass structural validation | **Verified for eligible fixture subset; not universal** | 210/211 sentence-aligned IMG records passed the runtime candidate-normalizer fixture test. `ch2-2` remains unresolved. The separate read-only importer audit processed 252 source records: 203 normalized, 49 unresolved, with the expected-count check passing. |
| Unresolved and alternative analyses handled explicitly | **Verified at unit-test level** | Runtime normalizer and importer tests cover unresolved, ambiguous, accepted-alternative, and source-only metadata cases. |
| API contracts and error states documented and tested | **Partially verified** | Flask contract tests and shared-payload tests pass. Chapter routing is forwarded in Flask, stdlib, and hosted transports; direct integration tests for every deployment transport remain limited. |
| Existing required Generator behavior covered by regression tests | **Partially verified** | Model-free legacy licensing/matrix and correction regressions pass. Actual spaCy/Benepar-backed end-to-end parsing is not included in this model-free CI run. |

### 4. Tests and checks run

All were run by GitHub Actions on 7 November 2026:

- `python -m unittest -v test_br_tree test_cambridge_registry test_br_tree_fixtures test_br_tree_schema test_api_contract test_webapp_contract test_detector` — **46 passed**.
- `python -m unittest -v server.test_burton_roberts` — **24 passed**.
- `python scripts/audit_burton_roberts_import.py --expected-count 252` — **passed**; 252 source records across 10 chapters; 203 normalized and 49 unresolved.
- All 11 chapter validators — **passed**.
- Legacy licensing regression — **19/19** invalid examples detected; **16/16** grammatical controls not rejected.
- Corrector regression — **passed**.
- New backend module compile step — **passed**.
- `python -m json.tool grammar/br_tree.schema.json` — **passed**.

The separate IMG fixture regression printed **210/211** normalized and validated, with `ch2-2` explicitly unresolved because its stored `Sentence` root conflicts with V2's `S → NP VP` convention.

### 5. Known limitations and unresolved issues

1. The runtime API schema and M1-approved canonical tree envelope are not yet reconciled; API output conformance is not verified.
2. General source-grounded Benepar transformations for V3–V10 are not implemented. The adapter supports exact eligible B-R source references and a narrow non-reference V2 top-level mapping; all other unsupported shapes remain unresolved.
3. `grammar/runtime_registry.json` enables zero Cambridge rules. `server/cambridge_registry.py` is an eligibility gate, not a sentence-level Cambridge evaluator. No Cambridge positive/negative/exception minimal-pair suite is available.
4. The CI workflow does not install `en_core_web_md` or `benepar_en3`. Live parser output, multi-sentence runtime behavior, correction parsing with the real models, latency, and missing-model fallback remain unverified.
5. The current frontend retains the raw candidate tree for compatibility. It has an authority notice, but it has not been migrated to render the runtime canonical representation as the primary tree. The detailed prompt's stop condition keeps a full UI redesign/Builder migration out of this workstream.
6. Exact B-R/Cambridge edition and page metadata still require confirmation against original source PDFs.
7. The full importer audit's 49 unresolved records are not failures hidden by the audit; many correspond to convention restrictions, unsupported zero-word elision, source fragments/metadata shapes, or other cases that must stay unresolved until reviewed.

### 6. Data, schema, and migration implications

The API now forwards `chapter`, `convention_version`, and `appendix_nom` across supported transports and reports selected-profile metadata. Chapter/version mismatches are rejected. No database schema, live user progress, lesson content, quiz content, or Builder data was migrated. Beneath the API, the two schema representations remain separate and must be reconciled before downstream consumption.

### 7. Checklist updates

- The CoLA advisory-role checkbox is now checked based on passing focused tests.
- The normalizer, unresolved/alternative, validator, token-order/span, profile/feature, tree-feature, gold-fixture, legacy regression, and shared-payload boxes retain the evidence-based states in `master_checklist.md`.
- Cambridge minimal-pair/evaluator, general safe V3–V10 mapping, parser-backed full/multi-sentence runtime, and performance/fallback boxes remain unchecked.
- Milestone 02 itself remains `[ ]`; no later milestone was marked.

### 8. Approval gate and dependency

The PR is a **draft**, remains unmerged, and targets `main`. The final CI run passed, but the M2 approval gate is not satisfied because the approved-schema integration, Cambridge evaluator boundary, and real parser-backed runtime checks remain open. Automatic approval of roadmap gates does not turn unverified acceptance criteria into completed work. Milestone 03 is not started.
