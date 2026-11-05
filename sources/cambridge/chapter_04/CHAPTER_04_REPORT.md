# Cambridge Chapter 4 — extraction report

## Scope and approval

- Source: *The Cambridge Grammar of the English Language*, Chapter 4, “The clause: complements”.
- Processed section: **§1.1 Types of complement and canonical clause structures**.
- Printed pages: **216–219**; supplied chapter-PDF pages: **4–7**.
- Page 219 is only partially included: the valency discussion and its footnote close §1.1; §1.2 begins later on that page.
- Human approval: **APPROVED on 2026-11-05**, following the repository owner's explicit instruction to approve all pending items.
- Protocol: `CAMBRIDGE_EXTRACTION_PROMPT.md`, version 1.0.

## Artifacts

- `ch04_s1-1_extraction.json`: complete structured extraction, concepts, approved rules, cross-references, and coverage report.
- `cross_references.json`: 14 links to existing SynTutor rules and named Cambridge chapter material.
- `conflicts-1.json`: empty; this pass identified no conflict requiring reconciliation.
- `grammar/concepts.json`: 14 new concepts appended without duplicating existing entries.
- `grammar/rules/complementation.json`: 8 approved rules added, continuing the COMP sequence.

## Approved rules

| ID | Concept | Type | Status |
|---|---|---|---|
| COMP-011 | transitivity of verb uses and dual-transitivity verbs | classification | APPROVED |
| COMP-012 | core and non-core complements | descriptive_generalization | APPROVED |
| COMP-013 | oblique | classification | APPROVED |
| COMP-014 | predicand | classification | APPROVED |
| COMP-015 | orientation of predicative complements | descriptive_generalization | APPROVED |
| COMP-016 | predicative complement construction versus finite clause complement construction | classification | APPROVED |
| COMP-017 | copular clause | classification | APPROVED |
| COMP-018 | valency | classification | APPROVED |

Existing rules COMP-001 through COMP-010 were preserved. The new rules add distinctions not separately represented in the active rule file: dual-transitivity uses, core/non-core complement prototypes, obliques, predicands, predicative-complement orientation, predicative vs finite-clause constructions, the chapter's narrower use of copular clause, and its definition of valency.

## Validation and review notes

- All 8 new rule records were checked against `grammar/schema.json`; no schema errors.
- New IDs continue after COMP-010; no ID collisions.
- All 8 proposed records have been moved into the active complementation rule file with status `APPROVED`.
- Non-constraint records use contrast examples rather than invented ungrammatical examples.
- Example count: 24 AI-authored contrasts; 0 book examples.
- Burton-Roberts mappings remain `unverified` because no corresponding materials were supplied or found in the expected source directory.
- Valency is used in the chapter's local sense (number of syntactic complements); footnote 7's alternative uses (number plus type of complements, or number of semantic arguments/adicity) are noted rather than conflated.
- No separate independent second-pass AI review was run; approval status reflects the explicit human authorization.
- The source PDF and extracted chapter text were not added to the public repository.

## Coverage

- Fully covered: printed pp. 216–218, §1.1.
- Partially covered: printed p. 219, only the valency continuation and its footnote belonging to §1.1.
- Not covered: §1.2 onward (the rest of Chapter 4).
- Later sections remain subject to their own section-by-section approval gates.

**APPROVED: 4/§1.1 Types of complement and canonical clause structures.**
