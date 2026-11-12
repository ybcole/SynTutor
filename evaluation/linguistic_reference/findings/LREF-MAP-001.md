# LREF-MAP-001: SVA-001 to FINAL-D1 alignment

Status: OBSERVED ALIGNMENT — NOT LINGUISTIC CERTIFICATION

## Case

ID: SVA-001
Sentence: The boy runs.

LREF notation: LREF_MINIMAL_DRAFT_V0
Canonical profile: FINAL-D1
Canonical normalization: normalized
HTTP response: 200

Endpoint used:
http://127.0.0.1:8001/api/parse

The exact running server revision has not yet
been independently attested.

## Observed surface alignment

| Linguistic element | LREF | FINAL-D1 | Character span |
| --- | --- | --- | --- |
| Subject phrase | NP | NP | [0, 7] |
| Predicate phrase | VP | VP | [8, 12] |
| Article surface | Determiner | ART | [0, 3] |
| Noun surface | NounHead | N | [4, 7] |
| Verb surface | VerbHead | V | [8, 12] |

Five of five selected spans aligned.

This is a selected-case observation, not an
estimate of general syntactic accuracy.

## Representation differences

LREF:
Sentence > Clause > NP / VP

FINAL-D1:
S > NP / VP

LREF uses:
Determiner, NounHead, VerbHead

FINAL-D1 uses:
DET > ART
NOM > N
V with features [intrans, pres]

LREF includes a punctuation leaf for the period.

The observed FINAL-D1 canonical tokens omit
the final period.

## Mapping policy

Matching character spans establish surface
correspondence only.

They do not establish grammatical equivalence
between the corresponding labels.

No exact-tree accuracy score is authorized
by this comparison.

The representation mapping remains provisional
until its category and function correspondences
are independently justified.

## Source evidence

See:
- LREF-SOURCE-001.md
- LREF-SOURCE-002.md

These support selected grammatical relationships,
not the complete FINAL-D1 representation.

## Unresolved requirements

1. Independently justify category correspondences.
2. Separate grammatical categories from functions.
3. Define punctuation-alignment policy.
4. Verify the running server and model provenance.
5. Test representative positive and negative cases.
6. Establish independently reviewed tree references.

SVA-001 retains draft review status.
