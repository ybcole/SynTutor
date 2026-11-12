# LREF Linguistic Annotation Specification v1

Status: DRAFT — methodological proposal
Research branch: research/lref
Gold-standard status: NOT ESTABLISHED

## 1. Purpose

LREF provides independent linguistic reference annotations
for evaluating SynTutor.

Its purpose is to measure linguistic reliability, not merely
conformance with SynTutor's internal implementation.

Reference annotations must not be generated from SynTutor's
predictions and then treated as independent ground truth.

## 2. Evaluation Dimensions

Evaluate these dimensions separately:

1. Sentence acceptability
2. Constituency and grammatical structure
3. Grammatical relationships
4. Error detection and category attribution
5. Error localization
6. Explanation correctness and faithfulness
7. Correction appropriateness and meaning preservation
8. Uncertainty and abstention

A successful result in one dimension does not establish
correctness in the others.

## 3. Grammatical Frameworks

FINAL-D1:
SynTutor's declared canonical tree representation.
Evaluate formal compliance separately from accuracy.

Penn Treebank:
Evaluate Benepar candidate constituency structures
using representation-appropriate reference analyses.

Linguistic source references:
Use verified grammatical descriptions to justify
constructions, categories, and relationships.

LREF:
Record independently reviewed linguistic facts and
explicit mappings to relevant tree representations.

Do not assume these frameworks use identical structures.

## 4. Reference Case Requirements

Each reference case must record:

- Unique case ID and original sentence
- Linguistic phenomenon
- Language variety or unspecified variety
- Acceptability and any required context
- Relevant diagnostic claims
- Structural analysis or unresolved status
- Permitted alternative analyses
- Acceptable repairs where applicable
- Explanation requirements
- Source provenance and review status

Absent information must remain absent or explicitly
undetermined; it must not be fabricated.

## 5. Source Text and Alignment

Character spans use zero-based half-open intervals:
[start, end).

Token spans use the same interval convention but
refer to token indices, not character offsets.

Every mapping between these coordinates must specify
the tokenization used.

Surface words must be traceable to the input.

Gaps and empty categories require separate handling
and must not be treated as ordinary nonempty tokens.

## 6. Tree Annotation Policy

A reference tree must declare its notation and status.

The current LREF_MINIMAL_DRAFT_V0 representation is
provisional and is not a verified CGEL or Penn Treebank tree.

Do not compare trees by exact structure unless their
representations and relevant conventions are compatible.

A structurally valid annotation is not automatically
a linguistically correct annotation.

## 7. Grammatical Relationships

Record independently justified relationships such as:

- Subject and finite predicate
- Subject-verb agreement
- Auxiliary and selected verb phrase
- Head and dependent
- Clause boundaries
- Movement and relevant dependencies

Relationship endpoints must refer to valid annotated
structures or explicitly identified surface spans.

A correct word correction does not prove that the
grammatical relationship was diagnosed correctly.

## 8. Unacceptable Sentences

Retain the original erroneous sentence.

Separate observed forms from proposed corrected forms.

Record local violations even when a complete tree
cannot be independently established.

Do not silently substitute a repaired sentence's tree
for the analysis of the original input.

Allow unresolved or partial analyses with documented
reasons and limitations.

## 9. Ambiguity and Alternative Analyses

Record context-dependent interpretations explicitly.

Alternative structures require their own rationale
and review evidence.

Treat unresolved alternatives as unresolved.

Do not automatically promote an internally labeled
ACCEPTED or PREFERRED alternative to gold status.

## 10. Diagnostic Evidence

For each supported violation, record:

- Grammatical category
- Affected span
- Relevant grammatical relationships
- Observed form
- Expected constraint or form
- Supporting source evidence
- Uncertainty where applicable

Diagnostic category, localization, and correction
must be evaluated independently.

## 11. Independent Review

Use the existing review states:

draft
source_reviewed
expert_adjudicated

Draft:
Provisional annotation, not validated ground truth.

Source reviewed:
Relevant source claims have been independently checked.

Expert adjudicated:
Required independent approvals and adjudication evidence
have been documented and verified.

Metadata alone does not authenticate reviewer identity.

Only appropriately reviewed dimensions may contribute
to claims of gold-standard evaluation.

## 12. Structural Validation

Automated validation should check:

- Required fields and allowed data types
- Span bounds and parent-child containment
- Surface-text alignment
- Relation endpoint integrity
- Supported representation versions
- Alternative-analysis integrity
- Review-state consistency

Additional tests are required before claiming complete
coverage of these invariants.

Structural validation does not replace linguistic review.

## 13. Evaluation Reporting

Report separately:

- Formal tree validity
- Tree accuracy against reviewed references
- Grammatical error detection
- Error-category attribution
- Span localization
- Correction validity and meaning preservation
- Explanation faithfulness
- Abstention and selective coverage

Specify denominators, exclusions, uncertain cases,
and the reviewed dimensions used in each measurement.

Known-failure regression tests are not representative
population-level accuracy estimates.

## 14. Reproducibility

Record:

- Tested repository commit
- Server and model provenance
- Dataset revision
- Annotation specification version
- Review status
- Evaluation configuration
- Test results and failures

Do not claim improvement without comparable before-
and-after measurements.

## 15. Current Limitations

The existing pilot contains 11 draft cases.

Only SVA-001 currently has a provisional reference tree.

There are no independently adjudicated gold cases.

The current tree validator supports only
LREF_MINIMAL_DRAFT_V0.

The annotation standard and representation mappings
require further review before formal adoption.
