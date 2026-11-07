# Syntax Generator: B-R Analysis Contract

**Status:** Milestone 02 implementation contract  
**Canonical authority:** Noel Burton-Roberts, Analysing Sentences: An Introduction to English Syntax (edition must still be confirmed against the supplied source PDFs)  
**Candidate parser:** spaCy and Benepar  
**Canonical schema:** grammar/br_tree.schema.json

## 1. Purpose and authority boundary

The Syntax Generator now exposes two distinct structural representations:

- **Benepar candidate parse:** a raw parser proposal retained for diagnostics and compatibility with the existing renderer.
- **B-R canonical analysis:** the book-convention representation in the br_analysis field. This is the only field intended to be treated as the canonical B-R phrase marker.

Benepar labels are not renamed wholesale into B-R labels. A normalization is emitted only when the available evidence supports the conversion. Unsupported structures return status "unresolved"; they are not silently relabelled.

The legacy rule matrix and CoLA signal still exist in the current Generator pipeline. They are not the new Cambridge rule evaluator. The API makes active Cambridge rule IDs explicit under cambridge_runtime; the default allow-list is empty.

## 2. Request contract

POST /api/parse

    {
      "text": "The birds sing.",
      "sentence_index": 0,
      "convention_version": "V10"
    }

- text is required and must contain non-whitespace text.
- sentence_index is optional, zero-based, and defaults to 0.
- convention_version is optional and defaults to V10; accepted values are V1 through V10.
- Chapter lessons must send their chapter convention. Free analysis defaults to the current declared final profile: V10 plus the Chapter 7 appendix refinement decision (D1). The D1 refinement is preserved from verified source references; the adapter does not invent additional NOM nodes.

## 3. Canonical analysis response

The complete canonical analysis is returned in br_analysis:

    {
      "schema_version": "1.0.0",
      "status": "normalized",
      "convention_version": "V10",
      "profile": "free_analysis_v10_plus_ch7_d1",
      "source": {
        "book": "Burton-Roberts",
        "chapter": 10,
        "page": 226,
        "figure": "[11]",
        "tree_id": "ch10-11",
        "evidence": "IMG",
        "method": "exact_verified_reference"
      },
      "tree": {},
      "accepted_alternatives": [],
      "movement": [],
      "external_controller": null,
      "diagnostics": []
    }

The example is illustrative. Real node objects are validated by grammar/br_tree.schema.json.

### Node representation

- Constituent: id, label, features, index, triangle, span, surface, and either children or words.
- Terminal: id, word, span, surface, with optional elided, ellipsis, or starred.
- Elision symbol: the source's symbolic E is represented as an explicit zero-width symbol terminal.
- Gap: id, gap=true, zero-width span, and optional positive index.
- V9 wh triangle: an unlabelled triangle is permitted only as a child of C2, where the chapter convention allows its category to be omitted.
- Span coordinates are zero-based, half-open parser-token indices. Punctuation remains in the parse token stream; a phrase marker covers the lexical words represented by its nodes.

Grammatical functions are not invented as tree nodes. They remain positional interpretations, consistent with CONVENTIONS.md.

## 4. Normalization policy

The current adapter has deliberately narrow safe paths:

1. An exact sentence match to a B-R reference record with status IMG, a matching convention version, and a source tree that passes the canonical structural validator may be normalized directly. The reference's page, figure, tree ID, movement metadata, external controller, and accepted alternatives are retained.
2. V2 supports one conservative Benepar structural mapping only: an S node whose immediate non-punctuation children are exactly NP then VP. The NP and VP internals remain triangles. This is a partial analysis, not a full phrase analysis.
3. Other Benepar candidates remain unresolved until an evidence-backed transformation is implemented and tested.

A matching source record that fails validation produces REFERENCE_VALIDATION_FAILED with rejected tree IDs and precise validation reasons. Distinct valid B-R analyses for the same sentence produce AMBIGUOUS_REFERENCE. An unsupported candidate produces NO_SAFE_B_R_MAPPING.

### Current source-fixture audit

The automated audit checked 211 sentence-aligned, IMG-marked records from Chapters 1–10:

- **210** normalized and passed the canonical structural validator.
- **1** remains explicitly unresolved: ch2-2. Its stored tree is rooted in Sentence, while V2 requires the S → NP VP convention. It must not be silently upgraded or relabelled.

The audit does not treat TXT-only, derived, anomaly, fragment, or answer-key metadata as automatic gold trees. IMG means the tree shape was checked against the image; it does not mean every stored record is necessarily valid under its declared convention.

## 5. Cambridge runtime eligibility

grammar/runtime_registry.json is an explicit allow-list. It is empty by default.

An extracted record's APPROVED status is insufficient to enable it. Runtime eligibility requires:

- an approved/reviewed source record and printed page evidence;
- independent review, reviewer identity, and review date;
- a resolved or compatible B-R crosswalk (an unverified mapping blocks activation);
- an executable rule type (constraint or variety_restricted);
- passing positive, negative, and exception tests;
- an explicit runtime_status=enabled entry.

Classification, descriptive-generalization, and stylistic/prescriptive records do not become automatic error rules. No Cambridge rules are currently enabled. The current module loads eligibility metadata; a complete Cambridge sentence evaluator is still pending and is not claimed by this API contract.

## 6. Correction payload

When the existing correction engine proposes a correction, the API now adds:

- corrected_sentence: the complete repaired sentence;
- alignment: original and corrected token lists, edit opcodes, token/character ranges, and the affected original parser terminal IDs where available;
- corrected_candidate_parse: a separate parse of the corrected sentence, not a splice into the original parse;
- corrected_br_analysis: the corrected sentence's canonical B-R analysis, or an explicit unresolved result if the corrected parse cannot be obtained or normalized.

The corrected parse is generated from the corrected sentence, so it cannot contain the original erroneous token as an actual corrected leaf. The strikethrough/adjacent display of original and replacement forms is a frontend responsibility and is not implemented in this milestone.

## 7. Backward compatibility

The top-level response fields tree and candidate_tree continue to expose the raw Benepar candidate for the existing frontend. meta.tree_authority explicitly warns that the canonical B-R result is in br_analysis. This compatibility bridge is temporary; a later UI milestone must consume the canonical field and present unresolved states clearly before the old tree field can be retired.

The existing rule-matrix verdict remains a legacy verdict. It should not be described as a Cambridge-evaluated result.

## 8. Error and fallback behavior

- 400: invalid request or invalid convention_version.
- 422: empty input or parser-level invalid/no-sentence input.
- 503: parser model or backend unavailable.
- Successful parser request with unsupported B-R structure: HTTP success with br_analysis.status=unresolved and a diagnostic code. This is not a parser failure.

A normalization failure must not erase the raw candidate parse or crash the legacy response.

## 9. Verification

The CI workflow .github/workflows/syntax-generator-tests.yml compiles the new modules and runs:

- B-R normalizer and validator unit tests;
- Cambridge runtime-registry eligibility tests;
- the Chapter 1–10 IMG source-reference audit;
- canonical JSON Schema validation tests.

The existing parser/model pipeline, old grammar verdict, and end-to-end UI rendering still require separate regression coverage on a machine with the configured spaCy/Benepar model environment. Those are listed as remaining Milestone 02 work, not implied complete by the model-free CI run.
