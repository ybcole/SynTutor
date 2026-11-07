# Canonical Burton-Roberts tree schema proposal — Milestone 01

**Status:** Implemented, approved versioned contract; current output 1.1.0, legacy 1.0.0 accepted.
**Compatibility:** Wrap and normalize the existing book tree records; do not rewrite their source data during Milestone 01.

## 1. Design goals

The canonical representation must preserve the information used by B-R chapter conventions without inheriting Penn Treebank labels or adding function-labelled nodes that the book does not use.

It must represent:
- stable node identity and canonical label;
- chapter/convention profile;
- B-R features and indices;
- ordered hierarchical children and lexical terminals;
- triangles as intentionally unanalyzed constituents;
- gaps/covert elements and co-indexing;
- elided elements;
- movement/control metadata separately from phrase-marker structure where the book treats it as explanatory;
- token spans and stable surface alignment;
- source figure/page/evidence status;
- accepted alternative analyses and uncertainty.

## 2. Envelope

A tree record is wrapped in the following envelope:

| Field | Type | Purpose |
|---|---|---|
| `schema_version` | string | Version of this canonical contract (`1.1.0`; legacy `1.0.0` accepted). |
| `tree_id` | string | Stable identifier for this analysis/fixture. |
| `sentence` | string | Full input surface, including punctuation where present. |
| `tokens` | array | Ordered token records with zero-based token index and character offsets. |
| `convention_profile` | object | `chapter`, `version` (V1–V10 or approved final profile), and optional `appendix_nom` refinement flag. |
| `source` | object | Source/book/chapter/printed page/figure and evidence/review metadata. |
| `root` | node | Canonical root node. |
| `movement` | array | Separate explanatory movement links when applicable; never insert arrows as phrase-marker nodes. |
| `accepted_alternatives` | array | Other source-accepted analyses, each with its own root and reason/source metadata. |
| `notes` | array | Source-preserving editorial/interpretive notes; not a substitute for structured status. |

Token spans are **zero-based, half-open** `[start, end)` indices into the `tokens` array. Character offsets are zero-based, half-open offsets into the original sentence. This convention must be implemented consistently and tested before use.

## 3. Node variants

All nodes may have an optional stable `id` and `token_span`. Child order is the source phrase-marker order, not visual canvas order.

### 3.1 Branching or non-branching labelled node

`{ "label": "VP", "features": [], "index": null, "children": [...] }`

- `label` is a canonical B-R label, such as `S`, `NP`, `VP`, `NOM`, `DET`, `N`, `A`, `AP`, `Adv`, `AdvP`, `P`, `PP`, `MOD`, `PERF`, `PROG`, `PASS`, `TENSE`, `C`, `C1`, `C2`, `S-bar`, `S-dbar`, `PRE-DET`, `PartP`, or another label introduced by the appropriate chapter convention.
- `features` is an ordered array of source-supported feature strings (for example `trans`, `past`, `-tense`).
- `index` is a co-index value when the book's analysis requires it.
- `children` is ordered and contains node variants.
- Grammatical functions (subject, dO, iO, adjunct, etc.) are derived from structural position or shown as explanatory overlays; they are not invented phrase-marker nodes.

### 3.2 Lexical terminal

`{ "word": "spotted" }`

A terminal contains the lexical surface form. Optional `pos` is parser/source diagnostic metadata, not a B-R category label. Optional `elided: true` records a source-approved elided item. Its token span is empty or source-defined when the element is not overt.

### 3.3 Triangle

`{ "label": "NP", "triangle": true, "words": ["those", "wildcats"], "index": 1 }`

A triangle carries the category label and the unanalyzed words. In 1.1.0, a source-permitted wh triangle under C2 from V9 may instead omit `label` and carry `unlabelled: true`. This does not license arbitrary unlabelled constituents. It must not also contain `children`. It still contributes the overt words to token coverage and order. The optional non-negative `index` preserves Chapter 10 co-indexing when the source indexes an unanalyzed constituent.

### 3.4 Gap or covert element

`{ "gap": true, "index": 1 }`

A gap does not contribute an overt token. It may carry an index and other source-approved metadata. Its licensing and controller/co-reference information must be recorded in the enclosing analysis or movement/control metadata where appropriate.

### 3.5 Separate movement/control metadata

Movement arrows/dotted lines that the book treats as explanatory rather than phrase-marker structure belong in the `movement` collection. A movement record may identify a source node/gap, target position, index, and source reference. Control relations and external controllers can be represented there or in a distinct `control` field; they must not be fabricated as overt constituents.

## 4. Convention and provenance data

Every canonical tree must declare a convention profile. Chapter lessons use the relevant chapter version; free analysis uses the declared final profile. Later conventions must never leak into earlier chapter trees.

Source metadata must distinguish:
- source title and confirmed edition;
- chapter and printed page number;
- figure/exercise/tree ID;
- page-image evidence status (`IMG`, `TXT`, `DERIVED_FROM_INSTRUCTIONS`, `IMG_ANOMALY`, or source-specific equivalent);
- review state and reviewer record;
- copyright-safe paraphrase/notes.

Do not infer missing page numbers or upgrade `TXT`/anomaly records to image-verified status.

## 5. Alternatives and confidence

The envelope's `accepted_alternatives` stores all source-accepted parses that are relevant to the exercise/sentence. Each alternative has:
- stable `analysis_id`;
- its own canonical root;
- source and convention profile;
- rationale/meaning distinction or source note;
- grading/acceptance state.

A single canonical tree may also have an uncertainty state from its normalization process. A parser's top-ranked result is not automatically the only acceptable analysis.

## 6. Structural invariants

The future validator must check:

1. The selected chapter/convention profile is valid for the task.
2. Every overt token is covered exactly once by the tree terminals/triangles, in sentence order.
3. No gaps/elided elements count as overt tokens.
4. Every node label and feature is permitted by the selected chapter profile.
5. Child order and hierarchy obey the applicable B-R convention.
6. Triangles contain words but not nested analyzed children.
7. Gaps and co-indices are licensed and co-refer correctly where required.
8. Movement/control metadata references valid nodes/indices and remains outside the phrase marker unless the source explicitly says otherwise.
9. Function labels are not inserted as nodes.
10. Alternatives and book simplifications are represented explicitly and are not lost in serialization.

## 7. Migration from existing data

- Existing `web/content/book/chNN.trees.json` records remain the source fixtures and retain their current wrapper fields and evidence values.
- A read-only importer/adapter maps their existing `tree`/node forms into the envelope for validation and downstream consumption.
- Preserve existing `fig`, `page`, `sentence`, `status`, `note`, `accepted_alternatives`, `book_simplification`, `external_controller`, `movement`, `clause_id`, and chapter-specific metadata during import.
- Do not bulk-edit or discard the source records.
- Preserve node-level diagram references in `source_refs`; preserve source-only fields without approved typed schema counterparts in `notes` as explicit source metadata. Do not silently discard them or promote them to structural labels/features.
- A zero-word elided-element symbol (for example, source marker `E` with no lexical word) is not interchangeable with a gap or a word-bearing elided terminal. Until the schema has an approved node variant for that source structure, keep the source record unresolved and retain its raw form.
- Add stable IDs and spans in the canonical projection; do not fabricate missing source metadata.
- Record unmappable fields or structural choices as unresolved rather than dropping them.
- Only after the importer and validator pass all relevant chapter fixtures should later milestones consider a persisted canonical data migration.

## 8. Illustrative envelope (abridged)

```json
{
  "schema_version": "1.0.0",
  "tree_id": "ch7-3",
  "sentence": "the clowns",
  "tokens": [
    {"index": 0, "text": "the", "char_span": [0, 3]},
    {"index": 1, "text": "clowns", "char_span": [4, 10]}
  ],
  "convention_profile": {"chapter": 7, "version": "V7", "appendix_nom": false},
  "source": {
    "book": "Burton-Roberts",
    "chapter": 7,
    "printed_page": 141,
    "figure_id": "[3]",
    "evidence_status": "IMG"
  },
  "root": {
    "label": "NP",
    "token_span": [0, 2],
    "children": [
      {"label": "DET", "token_span": [0, 1], "children": [
        {"label": "ART", "token_span": [0, 1], "children": [
          {"word": "the", "token_span": [0, 1]}
        ]}
      ]},
      {"label": "NOM", "token_span": [1, 2], "children": [
        {"label": "N", "token_span": [1, 2], "children": [
          {"word": "clowns", "token_span": [1, 2]}
        ]}
      ]}
    ]
  },
  "movement": [],
  "accepted_alternatives": [],
  "notes": []
}
```

This example is a schema illustration based on the repository's Ch7 [3] gold record, not a new claim about the B-R source edition. The production schema may refine optional fields after the source/fixture review in Milestone 02; it must not silently change the principles above.

## 1.1.0 source-backed extension and compatibility

`{"empty":true,"label":"DET","empty_role":"determiner","token_span":[0,0]}` represents a zero-word source position. The only permitted pairs are DET/determiner (V7+), C1/complementiser (V9+) and E/ellipsis (V5+). These nodes never carry lexical words or movement-gap status. Their spans are in range and zero-width. Parent overt spans exclude them.

The source receipt `sources/burton_roberts/reviews/2026-11-08-conventions.json` explains the printed figures. Unlabelled wh triangles also require 1.1.0. The JSON Schema recursively restricts 1.0.0 envelopes to the original node variants; the Python validator enforces the same version boundary. No stored user data migration occurs. Builder editing currently rejects the new variants before replacing the current workspace, pending M6 support.
