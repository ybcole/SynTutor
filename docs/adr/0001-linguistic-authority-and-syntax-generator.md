# ADR-0001: Linguistic authority, candidate parsing, and canonical B-R analysis

- **Status:** Accepted by project owner for implementation on 7 November 2026
- **Scope:** SynTutor's syntax-analysis architecture and source governance
- **Supersedes:** The interpretation that the B-R book is the only permitted source for every kind of grammatical explanation
- **Does not supersede:** B-R chapter-specific phrase-marker conventions, source transcription checks, or the prohibition against using Penn/Benepar output as canonical B-R structure

## Context

SynTutor previously treated the Benepar constituency output, a hand-authored rule matrix, and B-R book-derived trees/lessons as one coupled system. The book-derived tree data is chapter-sensitive; the Cambridge Grammar supplies a broader account of grammatical categories, constructions, conditions, and exceptions. These sources do not always use identical terms or structural analyses.

A direct label substitution from Penn Treebank/Benepar to B-R is unsafe. The repository's own convention notes identify non-cosmetic differences, including NP-internal structure, recursive NOM, auxiliary-headed VP layers, clause layers, wh-fronting, gaps, indices, features, and triangles.

## Decision 1 — Separate linguistic authorities by domain

| Source | Authoritative for | Must not determine |
|---|---|---|
| Noel Burton-Roberts, *Analysing Sentences* | B-R phrase-marker shape, constituent hierarchy, labels/features, chapter-specific convention progression, B-R tree-building method, and the source-derived structural explanation | General grammar claims not supported by the book; silently overriding Cambridge findings outside the book's stated scope |
| The Cambridge Grammar of the English Language | Broader grammatical categories, constructions, constraints, conditions, exceptions, variety/register qualifications, and explanations of those grammatical principles | Rewriting a B-R phrase marker or silently replacing a chapter-specific B-R convention |
| Benepar | Candidate constituency analysis and diagnostic parser output | Canonical B-R tree, correctness verdict, or independent grammatical explanation |
| Existing matrix/CoLA/legacy corpus | Existing compatibility behavior during migration and comparison | Cambridge authority or B-R structural authority |
| LLM | Controlled drafting/paraphrasing of reviewed source facts and explanation templates | Grammar adjudication, unsupported inference, source conflict resolution, or invention of a B-R tree |

When sources differ, retain source-specific terminology and evidence. Record the crosswalk status as compatible, non-equivalent, conflicting, or unresolved. Do not force a mapping.

## Decision 2 — Preserve Benepar as a candidate parser behind an adapter

Keep spaCy/Benepar during the first migration stage. Preserve its raw parse for diagnostics and backward compatibility. Convert it into a B-R canonical tree only when a transformation is explicitly supported by the B-R convention and gold/reference evidence.

If a mapping cannot be justified, return a structured unresolved result with a diagnostic. If multiple distinct analyses are supported, return ambiguity or explicit accepted alternatives. Do not silently relabel a PTB node.

Replacing Benepar with a new B-R-trained parser is a separate research decision requiring a representative B-R training/evaluation corpus and comparative results.

## Decision 3 — Canonical analysis schema

The versioned contract is grammar/br_tree.schema.json (schema version 1.0.0). A canonical analysis contains:

- schema and convention versions;
- normalized/unresolved state and analysis profile;
- source provenance (chapter, printed page, figure, record ID, evidence status, and method);
- canonical tree and accepted alternatives;
- movement metadata separate from the phrase marker;
- external controller metadata when the B-R source supplies it;
- diagnostic records.

Nodes preserve canonical IDs, labels, features, indices, token spans, word terminals, triangles, gaps, elision symbols, and empty/elided material. Functions are not invented as labels; they are interpreted from positions.

Chapter lessons select the chapter's convention version. Free analysis uses the team's declared V10 profile plus the Chapter 7 appendix D1 refinement decision. No D1 structure is inferred merely because a candidate parse looks similar.

## Decision 4 — Fail-closed normalization

The current adapter in server/br_tree.py has these safe paths:

1. Exact sentence and convention match to an IMG-marked B-R source tree that passes canonical validation.
2. One conservative V2 mapping where the immediate non-punctuation children of S are exactly NP then VP. NP and VP internals remain triangles, so this is explicitly partial.
3. All other candidates return unresolved until additional mappings have been independently specified and tested.

A source status is not by itself proof that a tree is runtime-grade. A source record may be image-transcribed and still conflict with the convention version stored in its chapter file.

## Decision 5 — Cambridge runtime governance

Extracted Cambridge records are not executable merely because an extraction status says APPROVED. grammar/runtime_registry.json is an explicit allow-list, empty by default.

Eligibility requires source-page evidence, independent reviewer and date, a resolved/compatible crosswalk, an executable record type, positive/negative/exception tests, and an explicit enabled status. Classification and descriptive records support teaching; they do not become automatic error rules. Stylistic/prescriptive statements are not automatically grammaticality constraints.

The current server/cambridge_registry.py enforces this gate. A complete sentence-level Cambridge evaluator has not yet been implemented.

## Decision 6 — Shared API and backward compatibility

server/api.py returns:

- tree and candidate_tree: the raw Benepar candidate, retained temporarily for the existing renderer;
- br_analysis: the B-R canonical analysis or explicit unresolved result;
- cambridge_runtime: the allow-listed runtime rule IDs and registry diagnostics;
- correction alignment and a separate candidate/B-R analysis of the corrected sentence when the correction engine returns a correction.

meta.tree_authority identifies br_analysis as canonical. The old matrix verdict remains a legacy verdict, not a Cambridge verdict. The existing frontend must be migrated to render br_analysis in a later approved UI/integration milestone before raw tree compatibility fields are retired.

## Source-authority and crosswalk matrix

| Area | B-R representation | Cambridge contribution | Benepar relationship | Current status |
|---|---|---|---|---|
| S → NP VP | Direct V2 convention | May explain subject/predicate grammar where sourced | Narrow top-level mapping possible when exact immediate children are NP and VP | Supported, partial |
| NP internal structure | Chapter progression; V7 NP → DET NOM, recursive NOM | Broader noun/NP description and constraints | PTB NP is often flat; not equivalent to DET/NOM recursion | Non-equivalent unless specifically normalized |
| AP / ADJP, AdvP / ADVP | B-R labels AP and AdvP | Category definitions and relevant distinctions | Penn label names and analyses are not automatic B-R equivalents | Unverified; no blind rename |
| Verb features/complementation | B-R V features and position-based complements | Cambridge valency/complementation and constraints | Benepar does not supply all B-R subcategorisation or feature evidence | Requires deterministic analysis and tests |
| Auxiliaries and VP recursion | B-R auxiliary heads take VP complements; staged convention V6+ | Cambridge explains auxiliary forms and grammatical behaviour | PTB chains do not directly encode B-R's head/VP layers | Requires restructuring evidence |
| Clause layers | B-R S-bar, S-dbar, C/C1/C2 by chapter | Cambridge clause/construction definitions | SBAR/CP structures are not a direct equivalent | Unverified |
| Wh-fronting/relative clauses | B-R C2/C1 positions, gaps, accepted forms | Cambridge may describe wh/relative constructions and conditions | Benepar movement/gap metadata is insufficient as-is | Explicit unresolved/alternatives until mapped |
| Gaps, indices, triangles, ellipsis | Preserved as B-R nodes/metadata | Cambridge may explain construction/interpretation, not replace B-R notation | Usually not present in candidate tree in B-R form | Preserved from B-R reference; parser mapping not general |
| Grammatical functions | Read from structural positions; not tree nodes | Cambridge may discuss grammatical functions/relations | PTB labels do not substitute for B-R positional interpretation | Distinct layers |

## Repository inventory and active paths (reviewed branch main)

| Responsibility | Existing path(s) | Migration decision |
|---|---|---|
| Candidate parser | server/parse_engine.py | Keep candidate parser; add adapter after parse |
| Legacy rule matrix | server/matrix.py, server/ruleset.py, server/licensing.py | Keep as legacy until Cambridge rules are independently implemented and compared |
| Request/payload orchestration | server/api.py, server/webapp.py, server/app.py | Return both candidate and B-R analysis; accept convention_version |
| Corrections | server/corrections.py, server/corrector.py | Preserve original and corrected text; attach edit alignment and separate corrected parse |
| B-R source fixtures | web/content/book/ch01.trees.json through ch10.trees.json; validate_chNN.py | Use only convention-matching, structurally validated records as gold/reference fixtures |
| Cambridge source data | grammar/schema.json, grammar/concepts.json, grammar/rules/*.json, sources/cambridge/ | Keep extraction/review status separate from runtime enablement |
| Frontend | web/js/main.js, renderer.js, correction.js, syntax-builder*.js, tree-quiz.js | Current renderer remains on legacy tree field; later integration/UI milestone must consume br_analysis |
| Existing tests | server/test_*.py and web/content/book/validate_chNN.py | Retain and add regression coverage; do not claim unrun model tests passed |
| CI | .github/workflows/ | Add model-free B-R and schema tests; model-backed integration remains separate |

## Migration map

1. Preserve the existing parser output and legacy verdict. Do not delete either as part of the adapter introduction.
2. Introduce the canonical B-R schema and a fail-closed normalizer.
3. Validate exact B-R source records and add tests for chapter conventions, alternative analyses, ellipsis, triangles, gaps, indices, movement metadata, and token alignment.
4. Build and independently validate Cambridge runtime records. Keep the default allow-list empty until then.
5. Move the Generator's consumer/UI to br_analysis after the frontend can render normalized, ambiguous, and unresolved states.
6. Integrate the same canonical structure/evidence with the Syntax Builder and shared explanation service in their own milestones.
7. Retire legacy paths only after side-by-side comparison, regression tests, data migration, and rollback planning.

## Evidence and open matters

- The repository's Chapter 1–10 source files contain 252 tree records. A CI audit currently checks 211 sentence-aligned IMG records: 210 normalize and pass canonical validation; ch2-2 remains unresolved because its stored root label Sentence conflicts with V2's later S → NP VP convention. This unresolved source record is visible in diagnostics; it is not silently relabelled.
- IMG_ANOMALY, TXT-only, derived records, node fragments, and ACA material must be assessed by type before promotion to a runtime gold fixture.
- The exact B-R edition and the Cambridge edition/page-offset metadata must be confirmed against the supplied original PDFs. The repository currently records an edition uncertainty for B-R.
- Many Cambridge extraction records have no independent second pass and B-R mappings marked unverified. No such record is enabled by default.
- The current API still exposes the old tree for frontend compatibility and still runs the legacy matrix. The frontend has not yet been switched to B-R canonical rendering.
- A full Cambridge evaluator, general Benepar-to-B-R structural conversions, broad legacy error-corpus regression, parser-model integration tests, multi-sentence correction verification, and end-to-end UI verification remain outstanding.

## Approval record

The project owner instructed the assistant to "approve everything" and authorized proceeding with the planned architecture and Milestone 02 implementation on 7 November 2026. That approval does not waive source evidence, validation, test, security, or milestone completion requirements. Each milestone remains unchecked unless its own acceptance criteria are verified.
