# Cambridge Chapter 4 — extraction report

## Scope and status

- Source: *The Cambridge Grammar of the English Language*, Chapter 4, “The clause: complements”.
- Processed section: **§1.1 Types of complement and canonical clause structures**.
- Printed pages: **216–219**; supplied chapter-PDF pages: **4–7**.
- Page 219 is only partially included: the valency discussion finishes there, immediately before §1.2 begins.
- Extraction status: **NEEDS_REVIEW**. No rules in this batch have been human-approved.
- Protocol: `CAMBRIDGE_EXTRACTION_PROMPT.md`, version 1.0.

## Artifacts

- `ch04_s1-1_extraction.json`: complete structured extraction.
- `cross_references.json`: 14 links to existing SynTutor rules and named Cambridge chapter material.
- `conflicts-1.json`: empty; no Cambridge-internal or existing-rule conflict identified in this section.
- `grammar/concepts.json`: 14 new concepts appended. Existing concepts were not duplicated.

## Proposed rules

| ID | Concept | Type | Status |
|---|---|---|---|
| COMP-011 | transitivity of verb uses and dual-transitivity verbs | classification | NEEDS_REVIEW |
| COMP-012 | core and non-core complements | descriptive_generalization | NEEDS_REVIEW |
| COMP-013 | oblique | classification | NEEDS_REVIEW |
| COMP-014 | predicand | classification | NEEDS_REVIEW |
| COMP-015 | orientation of predicative complements | descriptive_generalization | NEEDS_REVIEW |
| COMP-016 | predicative complement construction versus finite clause complement construction | classification | NEEDS_REVIEW |
| COMP-017 | copular clause | classification | NEEDS_REVIEW |
| COMP-018 | valency | classification | NEEDS_REVIEW |

The approved runtime file `grammar/rules/complementation.json` was deliberately **not** changed. Existing rules COMP-002, COMP-003, COMP-004, COMP-005, COMP-006 and COMP-007 already cover baseline object selection, external subjects, transitivity classes, PP complements, predicative complements, and be clauses; the proposed records add only distinctions not already represented there.

## Validation and self-flags

- All 8 proposed rule records were checked against `grammar/schema.json`: **0 schema errors**.
- New rule IDs continue after COMP-010; no collision with the existing complementation rules.
- Non-constraint records use contrast examples rather than invented ungrammatical examples.
- Example count: 24 AI-authored contrasts; 0 book examples.
- Burton-Roberts mappings remain `unverified` because no corresponding materials were supplied or found in the expected source directory.
- Valency is used in the chapter's local sense (number of syntactic complements); footnote 7's alternative uses (number plus type of complements, or number of semantic arguments/adicity) are noted rather than conflated.
- The source PDF pages 216–219 were visually inspected, including the transition from the valency discussion into §1.2.
- No source PDF or extracted chapter text was added to the public repository.

## Coverage

- Fully covered: printed pp. 216–218, §1.1.
- Partially covered: printed p. 219, only the valency continuation and its footnote belonging to §1.1.
- Not covered: §1.2 onward (the rest of Chapter 4).
- Skipped by design: §1.2 “Complements vs adjuncts” and later sections, because the extraction protocol requires stopping after each section.

**STOP: awaiting approval for 4/§1.1 Types of complement and canonical clause structures.**
