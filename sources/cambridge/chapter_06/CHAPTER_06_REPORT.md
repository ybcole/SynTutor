# Cambridge Chapter 6 — extraction report

## Scope and approval

- Source: *The Cambridge Grammar of the English Language*, Chapter 6, “Adjectives and adverbs”.
- Processed section: **§1 Preliminaries**.
- Printed pages: **526–527**; supplied PDF pages: **2–3**.
- Page 527 is partially included: the remaining paragraphs closing §1 are covered; §2 begins later on the same page.
- Owner approval: **applied on 2026-11-05** under the user's instruction to approve everything requiring approval.
- Protocol: `CAMBRIDGE_EXTRACTION_PROMPT.md`, version 1.0.

## Extraction outcome

No standalone rule was added because the grammatical distinctions introduced in §1 were already represented in SynTutor's approved rule base. Instead, six existing approved rules received source-backed refinements, and five concepts were added to the shared concept index.

## Existing rule updates

| Rule ID | Domain | Change |
|---|---|---|
| WCAT-007 | word_categories | Clarified the predicative adjective's semantic role in be + AdjP; added pp. 526–527 sources and two examples. |
| WCAT-009 | word_categories | Added p. 527 source support for the absence of adverb predicative function; kept the narrower engine condition. |
| WCAT-010 | word_categories | Added prepositions and determinatives to the categories modified by adverbs. |
| WCAT-011 | word_categories | Added p. 527 source support for -ly derivation. |
| PHR-012 | phrases | Clarified the single AdjP level and recorded rare transitive adjectives worth and like as exceptions to the usual absence of direct NP complements. |
| PHR-013 | phrases | Clarified the single AdvP level and the qualified generalization that AdvP expansion is broadly a subset of AdjP expansion. |

All six rules were already `APPROVED`; their updated records retain that status. Five original examples were added to the existing rule files: two under WCAT-007 and three under PHR-012. The PHR-012 examples include the exceptional NP-complement uses and the ordinary PP-mediated pattern.

## New concepts

- **adjective phrase (AdjP):** The single higher-level syntactic unit headed by an adjective; the phrase may contain modifiers and, where licensed, complements.
- **adverb phrase (AdvP):** The single higher-level syntactic unit headed by an adverb; its possible internal expansions are broadly a subset of those available to AdjPs.
- **predicative function of adjectives:** An adjective phrase can function as a clause complement while the adjective supplies the main semantic predicate and be carries tense and subject agreement.
- **stative and dynamic situations:** Adjectives almost always denote states, while verbs are commonly used for dynamic situations, although many verbs also denote states.
- **transitive adjective:** A rare adjective that takes an NP complement directly; the section names worth and like as examples.

No duplicate concept terms were added.

## Validation and flags

- All 6 updated rule records were checked against `grammar/schema.json`: **0 schema errors**.
- No new rule IDs were allocated; no duplicate IDs were introduced.
- All affected rules were already approved and remain `APPROVED`.
- Existing rule cross-references are recorded and verified.
- Burton-Roberts mappings were not changed; the corresponding source material was not provided.
- No conflict requiring reconciliation was identified.
- No independent second-pass AI review was run; the source-backed updates are covered by the user's explicit approval.
- The source PDF and extracted chapter text were not added to the repository.

## Coverage

- Fully covered: printed p. 526, §1.
- Partially covered: printed p. 527, remainder of §1 only.
- Not covered: §2 onward.
- Skipped by design: **§2 Criterial properties of adjectives** and all later sections, each of which requires a separate extraction and approval gate.

**APPROVED: 6/§1 Preliminaries.**
