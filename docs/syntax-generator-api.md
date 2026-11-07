# Syntax Generator API — Milestone 02

**Status:** Implemented on `feature/milestone-02-syntax-generator-2026-11-07`; partial milestone, not release-approved.

## Request

`POST /api/parse` accepts the existing request fields:

| Field | Type | Meaning |
|---|---|---|
| `text` | string, required | Input passage or sentence. |
| `sentence_index` | integer, optional | Zero-based target sentence; defaults to `0`. |
| `chapter` | integer 1–10 or null, optional | B-R chapter convention to request. When omitted, use the declared `FINAL-D1` free-analysis profile. |
| `appendix_nom` | boolean or null, optional | For Chapter 7, `true` explicitly selects the Appendix D1 refinement; omitted or `false` selects V7 core. In free analysis, the FINAL-D1 refinement is fixed and cannot be disabled. |

Examples:

```json
{ "text": "The students laugh", "chapter": 2 }
```

```json
{ "text": "The sad clowns", "chapter": 7, "appendix_nom": true }
```

```json
{ "text": "The students laugh" }
```

The last request uses FINAL-D1. It will currently be unresolved by the live Benepar adapter because the project has not approved a source-backed mapping for the full V10 + D1 profile.

## Response and compatibility

The existing response properties remain available for the current browser renderer:

- `tree`: unchanged legacy Benepar node graph, retained for compatibility. It is **not** an authoritative B-R tree.
- `nodes`, `node_details`, `summary`, `parse`, and `explainers`: existing analysis payload.
- `meta.canonical_schema_version`: canonical envelope version (`1.0.0`).
- `meta.canonical_analysis_status`: result of normalization.
- `meta.displayed_tree_authority`: `benepar_diagnostic_candidate`. The current visual canvas still renders the legacy tree. A visible canvas notice now identifies it as a Benepar diagnostic candidate (or states that a B-R projection is available separately); it does not claim the canonical tree is being rendered.

A separate `canonical_analysis` property is returned:

| Property | Meaning |
|---|---|
| `status` | `normalized`, `unresolved`, or `rejected`. |
| `tree` | Canonical v1.0.0 envelope when normalized; otherwise null. |
| `reasons` | Machine-readable reason codes and human-readable details when normalization is not promoted. |
| `normalization_trace` | Traceable, evidence-labelled transformation steps. |
| `diagnostics` | Parser identity, original parse string, raw candidate graph, and token count. |
| `validation` | Structural validator result when validation was reached. |
| `correction_alignment` | Token/character-aligned edit operations when the existing correction assembler produced a suggestion; otherwise null. |

The canonical envelope carries a convention profile, source metadata, token character spans, B-R root, movement/control metadata, accepted alternatives, and notes. The live Benepar adapter marks parser-derived source provenance as `NEEDS_REVIEW`; it does not claim that the missing B-R source PDF or edition has been verified.

## Current normalization support and limits

The live Benepar-to-B-R projection is intentionally narrow. It currently promotes only a candidate matching the Chapter 2 V2 `S → NP VP` shell where:

1. the root is an `S` with exactly an `NP` followed by a `VP`;
2. the NP and VP can each be represented as source-unanalysed triangles;
3. punctuation does not require a mapping decision;
4. Benepar leaf order and spaCy token order match exactly; and
5. the resulting envelope passes canonical structural validation.

The adapter does not rename arbitrary Penn labels into B-R labels. It returns `unresolved` for other chapter profiles, internally structured NP/VP parses, extra branches, punctuation cases, token mismatches, and unsupported transformations. Those responses retain the raw parse in `diagnostics.raw_candidate_tree`.

Existing B-R chapter records can be projected independently through the read-only `canonicalize_gold_record(record, chapter_data)` importer. It preserves source record identifiers, figure/page/evidence state, tree labels/features, triangles, indexed triangles, gaps, word-bearing elided terminals, accepted alternatives, external controllers, movement descriptions, and chapter-specific answer metadata. Source records are not rewritten.

Node-level diagram references (for example, `ref: "VP1"`) are retained in canonical `source_refs`. Other source-only node fields—including symbols, multiword-terminal flags, verb-type labels, and future unrecognized node metadata—are serialized into node `notes` as JSON-valued `source_node_metadata:<field>=...` entries until an explicitly reviewed typed field is added to the schema. Existing node notes are retained. This avoids silently dropping source annotations or pretending they are canonical structural features.

One source pattern deliberately remains unresolved: Chapter 5 figure [46] uses a zero-word `E` elision marker inside an NP. The approved v1.0.0 node variants represent a gap or an elided terminal with an explicit word, but do not define a zero-word elided-element node. The importer reports this as unresolved and returns the original raw tree; it does not recast `E` as a gap or invent a lexical terminal.

## Correction alignment

When the legacy correction assembler emits a correction, `canonical_analysis.correction_alignment` records both original and corrected tokens and character spans. Changed regions are typed as:

- `substitution`
- `insertion`
- `deletion`
- `punctuation`
- `contraction`
- `multi_token_replacement`

Unchanged regions are also represented. The original correction edit records are retained as `source_edits`. The corrected string is not silently substituted for the original analysis; it remains an aligned candidate for the existing correction preview and later integration work.

## Error states

| HTTP status | Meaning |
|---|---|
| `400` | Invalid `sentence_index`, `chapter`, or `appendix_nom` combination. |
| `422` | Empty input or parser-level parse failure. |
| `503` | Backend/model service unavailable or unexpected analysis failure. |

An HTTP 200 response can still contain `canonical_analysis.status = "unresolved"`; this means the request was parsed but no defensible canonical B-R mapping was available. Consumers must check that status before treating `canonical_analysis.tree` as the target tree.

## Verification command

```bash
python -m unittest server.test_burton_roberts -v
python scripts/audit_burton_roberts_import.py --expected-count 252
```

The focused suite currently covers profile selection, conservative V2 normalization, unsupported-profile and punctuation fallbacks, structural validation, source-authored Chapter 7 and Chapter 10 records, indices/gaps/elision, accepted alternatives, Chapter 9 movement notes, multiple external controllers, and all requested correction edit classes.

## Outstanding before Milestone 02 approval

- Reconcile the detailed `master_prompt_syntax_generator.md` before claiming full prompt compliance. The file was not present in the accessible repository tree/path on the refs checked in this execution; the work recorded here follows the Milestone 02 scope and acceptance criteria in `syntutor_12_prompt_execution_plan.md`.
- Confirm the B-R edition and inspect the source PDFs. Parser-derived mappings must remain source-review pending until then.
- Expand live normalization across V1–V10/FINAL only after source-backed transformation rules and reviewed fixtures exist.
- Run `python scripts/audit_burton_roberts_import.py --expected-count 252` against all 252 B-R records, then reconcile exceptions/unresolved records against the existing chapter validators.
- Add Flask/legacy transport contract tests and full backend/frontend integration tests; implement and test an actual canonical-tree renderer (the current canvas notice only labels the legacy Benepar rendering).
- Compare existing generator behavior against the legacy regression corpus and model-backed parser runtime.
