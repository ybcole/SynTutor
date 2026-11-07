# Syntax Generator API — Milestone 02

**Status:** In progress. The API exposes a canonical B-R analysis separately from the raw Benepar candidate. Unsupported mappings remain unresolved; the current live candidate adapter is intentionally narrow.

## Request

`POST /api/parse` accepts:

| Field | Type | Meaning |
|---|---|---|
| `text` | string, required | Input sentence or passage. |
| `sentence_index` | integer, optional | Zero-based sentence to analyze; defaults to `0`. |
| `chapter` | integer 1–10 or null, optional | Selects the chapter convention profile V1–V10. |
| `convention_version` | string V1–V10, optional | Compatibility override. If `chapter` is also supplied, it must match `V{chapter}`. |
| `appendix_nom` | boolean or null, optional | For Chapter 7, selects V7 core (`false`) or Appendix D1 (`true`). With no chapter, free analysis uses the declared FINAL-D1 profile and cannot disable the refinement. |
| `variety` | non-empty string or null, optional | Selects the variety/register required by a `variety_restricted` Cambridge rule. No variety-restricted finding is produced unless the selected value matches the reviewed rule. |

Examples:

```json
{ "text": "The students laugh", "chapter": 2 }
```

```json
{ "text": "The students laugh", "chapter": 7, "appendix_nom": true }
```

```json
{ "text": "The students laugh" }
```

The last request selects the declared free-analysis profile FINAL-D1. Chapter selection, the Chapter 7 Appendix D1 refinement, and optional variety selection are forwarded through the Flask, stdlib, and hosted API entry points to the shared analysis function. Unchaptered free analysis accepts only the omitted convention or the legacy `V10` spelling; pass `chapter` to select a lesson profile.

## Response and authority

- `tree` and `candidate_tree` retain the raw Benepar candidate and metadata for diagnostics and compatibility. They are not the canonical B-R tree.
- `br_analysis` is the single shared normalization result. Its `status` is `normalized` or `unresolved`. When normalized, `br_analysis.tree` is the canonical M1 envelope defined by `docs/canonical-burton-roberts-tree.schema.json`; it is not a Penn/Benepar tree.
- The M1 envelope contains `schema_version`, `tree_id`, `sentence`, lexical `tokens` with character offsets, `convention_profile`, source provenance, `root`, `movement`, `accepted_alternatives`, and notes.
- `br_analysis.parser_diagnostics` retains the raw parse string/candidate tree separately. `br_analysis.normalization_trace` explains the mapping path; `br_analysis.diagnostics` explains unresolved/rejected cases.
- `meta.tree_authority` identifies the split. `meta.br_profile_id`, `meta.br_convention_version`, `meta.br_chapter`, and `meta.br_appendix_nom` report the selected profile.
- `parse.sentences` and `meta.sentence_count` preserve passage segmentation; `sentence_index` selects a sentence and `meta.target_sentence` reports its one-based position. Invalid and out-of-range indexes return HTTP 400; the parser no longer silently clamps to the last sentence.
- `cambridge_runtime` reports the fail-closed rule allow-list; `cambridge_evaluation` reports what was actually evaluated. Neither field re-labels the legacy matrix verdict as a Cambridge verdict.

Source fixture provenance is retained. An IMG marker is evidence of transcription from an image, not by itself independent review or human approval.

## Canonical schema compatibility — resolved in this continuation

The API normalizer now uses `build_canonical_analysis` from `server/burton_roberts.py`. Exact sentence/profile-matched IMG source records are imported through the read-only gold importer and validated against the M1 envelope validator before being returned. Conflicting source records and source records that fail projection stay unresolved. The narrow V2 candidate mapping also constructs and validates an M1 envelope.

The API contract tests validate the actual `br_analysis.tree` response against `docs/canonical-burton-roberts-tree.schema.json`. `grammar/br_tree.schema.json` is retained only as a deprecated internal projection schema for the legacy `server/br_tree.py` module and its focused tests; it is not the public Generator canonical-output contract.

## Safe normalization boundary

The live Benepar-to-B-R mapping remains deliberately conservative:

1. Exact sentence-aligned B-R gold references are used only when the reference has IMG evidence, is not marked incorrect, matches the selected convention version, and passes structural validation.
2. If distinct matching gold references produce different structures, the result is unresolved rather than arbitrarily selecting one.
3. The non-reference live mapping is the narrowly supported V2 `S → NP VP` shell. It leaves NP and VP internal structure as triangles; it does not rename arbitrary Penn labels into B-R categories. Terminal punctuation is retained in the full sentence and raw candidate diagnostics but is not fabricated as a phrase-marker leaf; punctuation inside a phrase that prevents safe alignment remains unresolved.
4. Chapter 7 Appendix D1 references are filtered separately from V7 core references.
5. Other Benepar structures, unsupported profiles, token-yield mismatches, or unsupported punctuation/mapping cases remain unresolved with diagnostics and the raw candidate preserved.

This is not a general V1–V10 Benepar transformer. In particular, arbitrary V3–V10 internal structures are not mapped without reviewed source conventions and gold fixtures.

The read-only B-R fixture projection also records source-only metadata and accepted alternatives. A source-only zero-word elision marker that has no corresponding canonical node shape remains unresolved; it is not reinterpreted as a gap or fabricated lexical terminal.

## Cambridge rule boundary

`grammar/runtime_registry.json` is a fail-closed allow-list. Extraction status alone never enables a rule. An entry must meet the independent-review, source-page, crosswalk, test, reviewer, and runtime-state gates. Only `constraint` and `variety_restricted` rules can trigger grammatical findings; descriptive generalizations, classifications, and stylistic/prescriptive material cannot be treated as prohibitions.

`server/cambridge_evaluator.py` now provides a deterministic execution boundary for explicitly typed `runtime_check` records. The first supported primitive is `forbidden_token_sequences` with occurrence-specific exception sequences. It is restricted to sentence-scope checks, validates token-sequence types, and returns a violation only for non-exempt matching occurrences. Variety-restricted rules require a non-empty declared variety and an explicit matching `variety` request value. Rules without a supported machine-readable check are skipped. The rule schema, registry, API payload, and evaluator tests cover allow-list, unresolved-analysis, positive, negative, exception, non-constraint, unsupported-scope, and variety-selection paths.

**Current source state:** the allow-list enables zero Cambridge rules. All 196 extracted rule records retain unverified B-R mappings, and they have not cleared the independent-review/crosswalk/runtime gates. Therefore no Cambridge grammatical rule is currently evaluated and the API returns `cambridge_evaluation.status = "no_runtime_rules"` for a normalized parse, or `not_evaluated` when B-R normalization is unresolved. The test cases for the generic primitive are synthetic evaluator-contract tests, not claims about Cambridge judgments. The legacy rule matrix remains separate and is not a Cambridge verdict.

## CoLA / acceptability-model role

The CoLA acceptability model is secondary. If the deterministic rule matrix identifies a rule-level violation, CoLA cannot cancel it. If the matrix is clean but CoLA rejects the sentence, the verdict is downgraded to `UNVERIFIED`, not `UNGRAMMATICAL`. The model does not create a rule ID, a structural claim, or a grammatical explanation. If it is unavailable, the existing rules-only path remains available.

## Corrected sentence data

When the correction assembler returns a suggestion, the response retains the original sentence and separately supplies the corrected sentence, token/character alignment, edit operations, affected original terminal IDs, and a fresh parse/normalization attempt for the corrected text. Supported edit kinds include replacement, insertion, deletion, punctuation, contractions, and multi-token changes. The corrected candidate tree is independently generated from the corrected sentence; the original parse is not silently rewritten. Unsupported corrected analyses stay unresolved.

## Error states

| HTTP status | Meaning |
|---|---|
| `400` | Non-integer, negative, or out-of-range sentence index; invalid chapter/profile combination; unsupported convention version; or invalid/empty `variety`. |
| `422` | Empty input or parser-level parse failure. |
| `503` | Backend/model service unavailable or unexpected analysis failure. |

An HTTP 200 response may contain `br_analysis.status = "unresolved"`. This means parsing completed, but a defensible B-R mapping was not available. Consumers must check this status before treating a canonical tree as present.

## Verification

The model-free CI workflow runs normalizer/API/HTTP contracts, M1 schema validation of actual API output, importer tests, Cambridge registry/evaluator/schema tests, B-R chapter validators, CoLA advisory contracts, and legacy licensing/correction regressions. It also runs the 252-record read-only B-R importer audit.

A separate `.github/workflows/syntax-generator-runtime.yml` installs the pinned spaCy/Benepar dependencies and models, verifies model load, and runs parser-backed single-sentence, multi-sentence, out-of-range-index, and actual Generator API tests. This workflow is the evidence source for the model-backed requirements; a model-free pass is not a substitute. Runtime performance/latency and deployed-host fallback still require separate measurement and deployment checks.

## Outstanding before Milestone 02 approval

- The current candidate normalizer does not generally restructure Benepar analyses into V3–V10 B-R trees. Exact eligible IMG source references and the narrow V2 shell are supported; other candidate shapes remain unresolved unless a separately reviewed source mapping is added.
- No Cambridge rule is runtime-enabled because the 196 extracted rule records retain unverified B-R mappings and have not cleared the independent-review/runtime gates. The generic evaluator primitive is tested synthetically; rule-specific positive/negative/exception tests remain pending until a rule is eligible.
- The parser-backed workflow has been added but has not yet produced a successful run in this environment. Its actual spaCy/Benepar parse, multi-sentence, and API tests remain unverified; GitHub Actions has returned startup failures before creating jobs on recent branch commits.
- An unexpected exact-gold lookup, importer, canonical validator, or Benepar adapter exception is converted to an explicit unresolved result. The raw candidate parse is retained in `parser_diagnostics`; it is never promoted after a failure.
- Runtime latency/performance and deployed-model missing-model fallback still need evidence. HTTP 400/422/503 error contracts are covered by model-free route tests, but that does not verify the deployed model service.
- The current frontend retains the Benepar candidate as a diagnostic/compatibility tree and its authority notice now reads `br_analysis.status`; it has not been migrated to render the new M1 envelope as its primary interactive tree. This is not a UI redesign or Builder migration.
- Exact B-R and Cambridge edition/page metadata still needs confirmation against original source PDFs.
