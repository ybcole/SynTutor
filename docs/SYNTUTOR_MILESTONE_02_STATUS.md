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

## Milestone 02 continuation report — current branch state, 7 November 2026

**Milestone:** 02 — Syntax Generator and B-R tree normalization  
**Status:** **INCOMPLETE — MUST REMAIN UNCHECKED**  
**Continuation branch:** `feature/milestone-02-completion-2026-11-07`  
**Draft PR:** [#30](https://github.com/ybcole/SynTutor/pull/30), targeting `main`, unmerged  
**Most recent successful CI baseline:** [run #35](https://github.com/ybcole/SynTutor/actions/runs/42346333169), from earlier implementation commit `408ed2fab5abec634177bb462f0f48605e546d9e`  
**Current branch head at this report update:** `2b0e73caef146de1f78cc4b4e30165bed241e05d`. **Current verification state:** no successful test execution on the newer current branch head.

### 1. Files inspected

- `master_prompt_syntax_generator.md`, `syntutor_12_prompt_execution_plan.md`, `master_checklist.md`, `master_plan.md`.
- M1 governance ADRs, source-authority/crosswalk decisions, `CONVENTIONS.md`, the approved canonical B-R schema and schema documentation.
- B-R chapter JSONs, validators, source import/normalizer/validator modules.
- Cambridge extraction schema, all rule collections, runtime allow-list and registry.
- `server/parse_engine.py`, `server/api.py`, Flask/stdlib/hosted API transports, correction, legacy matrix, CoLA detector, frontend tree notice/renderer paths.
- Existing normalizer, importer, schema, registry, API, HTTP, licensing, correction and multi-line tests; existing and newly added CI workflows.

### 2. Files changed on this continuation branch

**Implementation and contracts**
- `server/burton_roberts.py` — API canonical-envelope assembly from exact eligible IMG source references, conflict handling, importer/validator failure handling, raw parser diagnostic retention, default NOT_REVIEWED provenance when source review is not explicit, and exact request-sentence/token-offset rebasing.
- `server/api.py` — one canonical M1 `br_analysis.tree` output, chapter/free-profile enforcement, selected Cambridge variety, separate Cambridge evaluator output, corrected analysis through the same normalizer.
- `server/br_tree.py` — Chapter 7 core/Appendix D1 source-reference separation and punctuation alignment.
- `server/parse_engine.py` — strict sentence-index range checking; it no longer silently clamps an out-of-range index.
- `server/webapp.py`, `server/app.py`, `server/hf_space.py` — chapter, Appendix D1, variety, strict integer sentence-index forwarding/validation.
- `server/cambridge_evaluator.py` — new fail-closed evaluator primitive, sentence-scope restriction, occurrence-specific exception matching, variety restriction and non-constraint blocking.
- `server/cambridge_registry.py` — require explicit resolved crosswalk and deterministic runtime check, including variety metadata for variety-restricted rules.
- `grammar/schema.json` — machine-readable `runtime_check` schema.
- `grammar/br_tree.schema.json` — marked as a deprecated internal projection schema rather than the public canonical API contract.
- `web/js/main.js` — authority notice now reads `br_analysis.status` and labels the displayed raw Benepar canvas as diagnostic-only.

**Tests and workflows**
- Updated `server/test_api_contract.py`, `server/test_webapp_contract.py`, `server/test_stdlib_transport_contract.py`, `server/test_br_tree.py`, `server/test_br_tree_fixtures.py`, `server/test_burton_roberts.py`, `server/test_cambridge_registry.py`.
- Added `server/test_cambridge_evaluator.py`, `server/test_grammar_schema.py`, `server/test_parser_runtime.py`, and `server/test_detector.py`.
- Updated `.github/workflows/syntax-generator-tests.yml`; added `.github/workflows/syntax-generator-runtime.yml`.

**Documentation**
- Updated `docs/syntax-generator-api.md`, `master_checklist.md`, and `syntutor_12_prompt_execution_plan.md`.

### 3. Acceptance criteria review

| M2 acceptance criterion | Current status | Evidence / remaining gap |
|---|---|---|
| Generator output conforms to the approved canonical schema | **Implemented; current-head verification pending** | The shared API calls `build_canonical_analysis`; normalized `br_analysis.tree` is constructed in the M1 envelope. API-level JSON Schema tests and a corpus-through-API audit have been added, but have not run successfully on the current head. |
| Normalization decisions are traceable; unsupported mappings are not silently relabelled | **Partially verified** | Exact IMG reference path and narrow V2 `S → NP VP` mapping preserve provenance/trace. Unsupported mappings and import/normalizer failures produce unresolved results. General V3–V10 transformations remain unsupported rather than guessed. Current-head tests are pending. |
| Known B-R gold examples pass structural validation | **Historical baseline verified; current API path pending** | Earlier CI audited 252 records (203 normalized, 49 unresolved) and 210/211 sentence-aligned IMG examples; `ch2-2` remains unresolved. The new test that exercises the *actual API normalizer* against the M1 schema across all aligned IMG records has not run. |
| Unresolved and alternative analyses are handled explicitly | **Implemented; current-head verification pending** | Existing importer/normalizer tests cover unresolved, ambiguous and accepted-alternative states. New failure-path tests ensure source lookup/normalizer exceptions do not promote a tree. |
| API contracts and error states are documented and tested | **Partially verified** | Flask/API contract coverage exists for chapter, Appendix D1, variety, bad indexes, out-of-range indexes and 400/422/503 responses. Tests for the new signatures have not run on current head; stdlib/hosted transports still need live integration verification. |
| Existing Generator behavior that remains required is covered by regressions | **Historical baseline only** | Earlier CI passed legacy licensing regression (19/19 invalid examples detected; 16/16 controls not rejected) and corrector regression. Current-head regression rerun is blocked by Actions startup failures. |

### 4. Test and CI evidence

**Earlier successful baseline, not the current head:** GitHub Actions run #35 executed:
- 46 model-free Syntax Generator/API/HTTP/schema/Cambridge-registry/CoLA contract tests.
- 24 B-R importer tests.
- 252-record read-only source import audit (203 normalized, 49 unresolved).
- All 11 B-R validators.
- Legacy licensing regression (19/19 invalid examples detected; 16/16 grammatical controls not rejected).
- Corrector regression and JSON schema validation.

That successful run predates the current M1 API-envelope routing, Cambridge evaluator additions/hardening, new API-normalizer gold-corpus audit, strict sentence-index and variety routing, frontend notice correction, and parser-backed workflow. It must not be described as verification of these later changes.

**Current branch:** Recent GitHub Actions attempts including [42349400228](https://github.com/ybcole/SynTutor/actions/runs/42349400228) have returned `startup_failure` / `BuildFailed` with zero jobs created; the latest two attempts each report zero jobs. GitHub refused a retry for a startup-failed run. A local checkout/clone was also blocked because DNS could not resolve `github.com`. As a result, current-head `compileall`, the expanded model-free suite, the new M1 API corpus audit, and the parser-backed workflow have **not been executed successfully**.

### 5. Linguistic/runtime boundaries and outstanding limitations

1. **V3–V10 Benepar candidate conversion:** broad, source-grounded Benepar restructuring is not implemented. The adapter currently prefers exact, convention-matched IMG source trees and has a narrow non-reference V2 top-level mapping; other candidates return unresolved. Do not treat this as a general V1–V10 transformer.
2. **Cambridge rules:** `server/cambridge_evaluator.py` implements a constrained sentence-scope token-pattern primitive with exception handling, but the production registry enables **zero** Cambridge rules. The 196 extracted rules retain unverified B-R crosswalk mappings and have not passed the independent review/runtime gates. Synthetic primitive tests are not Cambridge rule judgments; rule-specific minimal-pair/exception tests remain unavailable until rules are approved for execution.
3. **Parser runtime:** a model-backed workflow is present to install spaCy/Benepar and exercise real single-/multi-sentence parsing and API output, but no successful workflow run exists for the current head. Runtime latency and deployed-model fallback remain unverified.
4. **Frontend:** the canvas continues to display the raw Benepar candidate for compatibility, but the notice now accurately reads `br_analysis.status` and labels the canvas as diagnostic-only. Primary interactive rendering of the M1 envelope and Builder migration remain outside this prompt's stop condition.
5. **Edit/correction behavior:** the API carries correction alignment and reparses corrected text independently with the selected profile. The updated path requires current-head runtime verification, especially for punctuation/contractions/multi-token correction scenarios using actual parser models.
6. **Source editions:** exact Burton-Roberts/Cambridge edition and printed-page metadata still need confirmation against the original source PDFs.

### 6. Data, schema, API and migration implications

- Normalized API output now uses the M1-approved B-R envelope in `br_analysis.tree`; the prior `grammar/br_tree.schema.json` is retained only for compatibility tests of the older internal projection.
- Raw Benepar graph and legacy matrix verdict remain available separately for current-renderer/backward compatibility. Cambridge evaluation is a distinct response field and is not represented as the legacy matrix verdict.
- Chapter, Appendix D1 and optional variety are forwarded through the three HTTP entry points. Sentence selection rejects non-integer, negative and out-of-range indexes.
- No database schema, learner progress, lessons, quizzes or Builder state was migrated.

### 7. Checklist and roadmap updates

- CoLA advisory-only role remains checked based on its earlier focused passing test run.
- Generalized V3–V10 mapping, Cambridge rule-specific minimal-pair tests, current-head multi-sentence/runtime evidence, performance/fallback verification and exact source edition metadata remain unchecked.
- The approved-schema API wiring is implemented, but current-head schema/corpus tests remain unexecuted; do not mark that checklist task complete on the basis of code alone.
- Milestone 02 remains `[ ]`. Milestone 03 and all later milestones remain untouched.

### 8. Approval gate

The owner authorized automatic approvals, so no additional decision is requested. That permission does not waive the plan's evidence requirements. PR #30 remains draft and unmerged. M2 is **not complete** because current-head tests have not run, real parser-backed behavior has not been verified, runtime Cambridge rules are not available, and broader source-supported normalization requirements remain unresolved. Do not start Milestone 03 until those conditions are addressed and an evidence-backed M2 acceptance report can be produced.
