# Cambridge Chapter 5 — extraction report

## Scope and approval

- Source: *The Cambridge Grammar of the English Language*, Chapter 5, “Nouns and noun phrases”.
- Processed section: **§1 Distinctive properties of nouns and NPs**.
- Printed pages: **326–328**; supplied PDF pages: **4–6**.
- Page 328 is partially included: the final bare-role-NP discussion closes §1; §2 begins later on the same page.
- Human approval: **APPROVED on 2026-11-05**, following the repository owner's explicit instruction to approve all items requiring approval.
- Protocol: `CAMBRIDGE_EXTRACTION_PROMPT.md`, version 1.0.

## Artifacts

- `ch05_s1_extraction.json`: complete structured extraction, concepts, rules, cross-references, and coverage report.
- `cross_references.json`: 13 links to existing SynTutor rules and the expressly cited Cambridge Ch. 4 §3.2.2.
- `conflicts-1.json`: empty; no conflict requiring reconciliation was identified.
- `grammar/concepts.json`: 7 new concepts appended without duplicate terms.
- `grammar/rules/morphology.json`: MORPH-007 added.
- `grammar/rules/word_categories.json`: WCAT-014 and WCAT-015 added.
- `grammar/rules/phrases.json`: PHR-016 through PHR-018 added and existing PHR-011 refined with the bare-role-NP exception.

## Approved rules

| ID | Concept | Type | Status |
|---|---|---|---|
| MORPH-007 | Inflectional paradigm of prototypical nouns | descriptive_generalization | APPROVED |
| WCAT-014 | Noun-specific dependents | descriptive_generalization | APPROVED |
| WCAT-015 | Nouns do not take objects | constraint | APPROVED |
| PHR-016 | Functions of NPs beyond clause complements | classification | APPROVED |
| PHR-017 | Dummy there as an NP | classification | APPROVED |
| PHR-018 | Bare role NPs | classification | APPROVED |

Existing WCAT-004 (pronouns as a noun subcategory), PHR-005 (NP structure), PHR-009 (fused heads), and PHR-010 (subject-determiner) were retained and cross-referenced, not re-extracted. Existing PHR-011 was refined to make explicit the source's bare-role-NP exception: singular bare role NPs may occur as predicative complements, but not as subject or object without a determiner. Six new examples were added to PHR-011; these are separate from the 27 examples in the six new rules.

## Validation and review notes

- All 6 new rule records and the refined PHR-011 were checked against `grammar/schema.json`: **0 schema errors**. PHR-016's modifier-only NP exception has a dedicated contrast example.
- IDs continue the existing domain sequences; no ID collisions.
- WCAT-015, the constraint, has 4 correct and 2 incorrect examples.
- Non-constraint records use contrast examples, not invented ungrammatical examples.
- Burton-Roberts mappings remain `unverified` because no relevant material was supplied or found in the expected source directory.
- No independent second-pass AI review was run; the approval status reflects the owner's explicit authorization.
- The source PDF and extracted chapter text were not added to the public repository.

## Coverage

- Fully covered: printed pp. 326–327, §1.
- Partially covered: printed p. 328, the closing bare-role-NP discussion only.
- Not covered: §2 onward (remaining Chapter 5 material).
- Skipped by design: §2 “Overview of noun classes and NP structure” and all later sections; the protocol requires one section per pass.

**APPROVED: 5/§1 Distinctive properties of nouns and NPs.**
