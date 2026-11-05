# Cambridge Chapter 3 — extraction report

## Scope and status

- Source: *The Cambridge Grammar of the English Language*, Chapter 3, “The verb”.
- Processed section: **§1.1 Summary presentation of the categories**.
- Printed pages: **74–75**; supplied chapter-PDF pages: **4–5**.
- Extraction status: **NEEDS_REVIEW**. This is one section only; later sections have not been processed.
- Protocol: `CAMBRIDGE_EXTRACTION_PROMPT.md`, version 1.0.

## Artifacts

- `ch03_s1-1_extraction.json`: full structured extraction, concepts, proposed rules, cross-references, conflict, uncertain item, and coverage report.
- `cross_references.json`: section cross-reference list.
- `conflicts-1.json`: conflict requiring a human decision.
- `grammar/concepts.json`: appended 9 new concepts; no existing concept entries were duplicated.

## Proposed rules

| ID | Domain | Concept | Type | Status |
|---|---|---|---|---|
| MORPH-004 | morphology | Negative forms of lexical verbs | constraint | NEEDS_REVIEW |
| MORPH-005 | morphology | Absence of secondary forms in modal auxiliaries | constraint | NEEDS_REVIEW |
| MORPH-006 | morphology | Invariant present form of modal auxiliaries | constraint | NEEDS_REVIEW |

The approved runtime file `grammar/rules/morphology.json` was deliberately **not** changed: the extraction protocol requires all extraction-pass rules to remain `NEEDS_REVIEW`, and they must not be treated as approved rules by the grammar engine.

## Validation and review flags

- Each of the 3 rule records was checked individually against `grammar/schema.json`; **0 rule-schema errors**.
- New rule IDs continue the existing morphology sequence after `MORPH-003`; no ID collision found.
- Every constraint has at least 2 correct and 2 incorrect examples.
- Example count: 14 AI-authored; 1 short book example (only the brief modal-gerund example, cited to p. 75).
- One conflict is logged: `MORPH-006` (modal forms invariant across subjects) vs. the unqualified present-tense wording in approved `AGR-002`. Do not revise `AGR-002` without human approval.
- One uncertain item: the source says `must` and one or two other modals lack a preterite form, but does not identify the additional item(s) on p. 75. The extraction does not guess.
- Burton-Roberts mappings are `unverified`: the relevant Burton-Roberts materials were not supplied or found in the expected repository source path.
- The supplied PDF pages were visually checked for the paradigm table and page labels.

## Coverage

- Fully covered: printed pp. 74–75, §1.1.
- Not covered in this pass: §1.2 onward (printed pp. 76–208). The protocol requires stopping after each section and awaiting approval.
- No source PDF or extracted chapter text was added to the public repository; only paraphrased rules, original examples, concepts, and page references are stored.

**STOP: awaiting approval for 3/§1.1 Summary presentation of the categories.**
