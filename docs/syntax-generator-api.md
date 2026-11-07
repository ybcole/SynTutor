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

The last request selects the declared free-analysis profile (FINAL-D1, represented by V10 in the candidate normalizer). Chapter selection and the Chapter 7 Appendix D1 refinement are forwarded through the Flask, stdlib, and hosted API entry points to the shared analysis function.

## Response and authority

- `tree` and `candidate_tree` retain the raw Benepar candidate for diagnostics and existing-client compatibility. They are not the canonical B-R tree.
- `br_analysis` is the single runtime normalizer result used by the current Generator API. Its `status` is `normalized` or `unresolved`; the raw parse remains separate.
- The runtime payload currently follows `grammar/br_tree.schema.json`. This is the API's active wrapper contract, but it is **not shape-identical** to the M1-approved tree-envelope schema in `docs/canonical-burton-roberts-tree.schema.json`. See the compatibility note below.
- `meta.tree_authority` identifies the split. `meta.br_profile_id`, `meta.br_convention_version`, `meta.br_chapter`, and `meta.br_appendix_nom` report the selected profile.
- `parse.sentences` and `meta.sentence_count` preserve passage segmentation; `sentence_index` determines the selected sentence and `meta.target_sentence` reports its one-based position.
- `cambridge_runtime` reports only allow-listed Cambridge rule eligibility. It is not itself a sentence-level grammaticality verdict.

The normalized `br_analysis` preserves the B-R convention version, profile/refinement, source provenance, canonical tree, accepted alternatives, movement/controller metadata where present, and diagnostics. Source fixture provenance is retained; an IMG marker is evidence of transcription from an image, not by itself independent review or human approval.

## Canonical schema compatibility — open M2 issue

The approved M1 ADR (D3) names `docs/canonical-burton-roberts-tree.schema.json` as the canonical B-R tree envelope. That contract uses fields such as `tokens`, `convention_profile`, `root`, and `token_span`.

The live Generator's `br_analysis` instead follows `grammar/br_tree.schema.json`, with `convention_version`, `profile`, `tree`, and node `span`/`surface` fields. The read-only source importer in `server/burton_roberts.py` projects source records into the M1 envelope, but that projection is not currently the object returned as the API's `br_analysis`. The two formats are not interchangeable.

CI validates the runtime payload against `grammar/br_tree.schema.json` and separately tests the gold importer against the M1 envelope validator. It does **not** establish that the live API payload conforms to the approved M1 envelope. This conflict must be reconciled and covered by an API-level schema test before Milestone 02 can pass its canonical-output acceptance criterion or be used downstream. The M1-approved contract is not silently amended by this implementation note.

## Safe normalization boundary

The live Benepar-to-B-R mapping remains deliberately conservative:

1. Exact sentence-aligned B-R gold references are used only when the reference has IMG evidence, is not marked incorrect, matches the selected convention version, and passes structural validation.
2. If distinct matching gold references produce different structures, the result is unresolved rather than arbitrarily selecting one.
3. The non-reference live mapping is the narrowly supported V2 `S → NP VP` shell. It leaves NP and VP internal structure as triangles; it does not rename arbitrary Penn labels into B-R categories.
4. Chapter 7 Appendix D1 references are filtered separately from V7 core references.
5. Other Benepar structures, unsupported profiles, token-yield mismatches, or unsupported punctuation/mapping cases remain unresolved with diagnostics and the raw candidate preserved.

This is not a general V1–V10 Benepar transformer. In particular, arbitrary V3–V10 internal structures are not mapped without reviewed source conventions and gold fixtures.

The read-only B-R fixture projection also records source-only metadata and accepted alternatives. A source-only zero-word elision marker that has no corresponding canonical node shape remains unresolved; it is not reinterpreted as a gap or fabricated lexical terminal.

## Cambridge rule boundary

`grammar/runtime_registry.json` is a fail-closed allow-list. Extraction status alone never enables a rule. An entry must meet the independent-review, source-page, crosswalk, test, reviewer, and runtime-state gates. Only `constraint` and `variety_restricted` rules are eligible to trigger grammatical errors; descriptive generalizations, classifications, and stylistic/prescriptive material cannot be treated as prohibitions.

**Current state:** the allow-list enables zero Cambridge rules. The registry reports eligibility but a deterministic Cambridge sentence-level evaluator and positive/negative/exception minimal-pair suite are not yet implemented. The legacy rule matrix is separate; it must not be represented as a Cambridge verdict.

## CoLA / acceptability-model role

The CoLA acceptability model is secondary. If the deterministic rule matrix identifies a rule-level violation, CoLA cannot cancel it. If the matrix is clean but CoLA rejects the sentence, the verdict is downgraded to `UNVERIFIED`, not `UNGRAMMATICAL`. The model does not create a rule ID, a structural claim, or a grammatical explanation. If it is unavailable, the existing rules-only path remains available.

## Corrected sentence data

When the correction assembler returns a suggestion, the response retains the original sentence and separately supplies the corrected sentence, token/character alignment, edit operations, affected original terminal IDs, and a fresh parse/normalization attempt for the corrected text. Supported edit kinds include replacement, insertion, deletion, punctuation, contractions, and multi-token changes. The corrected candidate tree is independently generated from the corrected sentence; the original parse is not silently rewritten. Unsupported corrected analyses stay unresolved.

## Error states

| HTTP status | Meaning |
|---|---|
| `400` | Invalid sentence index, chapter/profile combination, or convention version. |
| `422` | Empty input or parser-level parse failure. |
| `503` | Backend/model service unavailable or unexpected analysis failure. |

An HTTP 200 response may contain `br_analysis.status = "unresolved"`. This means parsing completed, but a defensible B-R mapping was not available. Consumers must check this status before treating a canonical tree as present.

## Verification

The model-free CI workflow runs the normalizer/API/HTTP contracts, B-R chapter validators, and legacy licensing/correction regressions. It now also runs the CoLA advisory contract tests, the read-only `burton_roberts` importer tests, and the full B-R source-record audit.

The following checks still require a configured spaCy/Benepar runtime and have not been established by model-free CI: actual parser-backed smoke tests, live full/multi-sentence parsing, deployed-model fallback/performance behavior, and end-to-end browser consumption of canonical B-R trees.

## Outstanding before Milestone 02 approval

- General source-grounded Benepar-to-B-R mappings for supported V3–V10 constructions remain incomplete.
- No Cambridge rules are runtime-enabled; no deterministic Cambridge sentence-level evaluator or minimal-pair/exception suite is active.
- Real spaCy/Benepar-backed end-to-end parsing, multi-sentence behavior, latency, and missing-model fallback need runtime verification.
- The legacy matrix remains the grammaticality verdict source; it is not a Cambridge evaluator.
- The frontend still renders the legacy raw candidate tree. This milestone preserves the authority distinction in the API; it does not redesign the UI or migrate the Builder.
- Exact B-R and Cambridge edition/page metadata still needs confirmation against original source PDFs.
