# Cambridge Chapter 3 — extraction report

## Scope and approval

- Source: *The Cambridge Grammar of the English Language*, Chapter 3, “The verb”.
- Processed section: **§1.1 Summary presentation of the categories**.
- Printed pages: **74–75**; supplied chapter-PDF pages: **4–5**.
- Human approval: **APPROVED on 2026-11-05**, following the repository owner's explicit instruction to approve all pending items.
- Protocol: `CAMBRIDGE_EXTRACTION_PROMPT.md`, version 1.0.

## Artifacts

- `ch03_s1-1_extraction.json`: structured extraction, concepts, approved rules, cross-references, resolved conflict, uncertain item, and coverage report.
- `cross_references.json`: section cross-reference list.
- `conflicts-1.json`: retained audit record of the AGR-002 conflict, marked resolved.
- `grammar/concepts.json`: 9 new concepts appended without duplicating existing entries.
- `grammar/rules/morphology.json`: 3 approved rules added.
- `grammar/rules/agreement.json`: approved AGR-002 refined to exclude invariant modal auxiliaries from present-tense agreement.

## Approved rules

| ID | Domain | Concept | Type | Status |
|---|---|---|---|---|
| MORPH-004 | morphology | Negative forms of lexical verbs | constraint | APPROVED |
| MORPH-005 | morphology | Absence of secondary forms in modal auxiliaries | constraint | APPROVED |
| MORPH-006 | morphology | Invariant present form of modal auxiliaries | constraint | APPROVED |

## Agreement conflict resolution

The prior broad wording of AGR-002 did not explicitly exclude modal auxiliaries, although Cambridge §1.1 states that modal auxiliaries use one present-tense form with all subjects. With explicit human approval, AGR-002 has been narrowed to present-tense non-modal verbs and `be` in the preterite. It now contains a modal-auxiliary exception, two original examples testing that exception, and a Chapter 3 source citation. The conflict record is retained for traceability and marked `needs_human: false`.

## Validation and review flags

- All 3 new rule records were checked against the required fields and constraints in `grammar/schema.json`; no required-field omissions or ID collisions found.
- Every new constraint has at least 2 correct and 2 incorrect examples.
- Example count: 14 AI-authored; 1 short book example (the brief modal-gerund illustration, p. 75).
- AGR-002 retains its earlier notional-number exception and now also records modal invariance.
- Burton-Roberts mappings remain `unverified`; no corresponding material was provided.
- One source uncertainty remains: the text says `must` and one or two other modal auxiliaries lack a preterite form but does not identify the additional item(s). This is not guessed or treated as an approved rule.
- The source pages were visually checked for the inflectional paradigms and printed page labels.
- No separate second-pass AI review was run; the rule statuses reflect the explicit human approval, not an independent second-pass review.
- The Cambridge PDF and extracted chapter text were not added to the public repository.

## Coverage

- Fully covered: printed pp. 74–75, §1.1.
- Not covered: §1.2 onward (printed pp. 76–208). Those sections remain outside this approved batch; protocol §10 requires a separate approval gate for each section.

**APPROVED: 3/§1.1 Summary presentation of the categories.**


---

## Phase B addendum — 2026-11-10

New protocol-1.1 extraction of printed pp. 76–90 added **35 NEEDS_REVIEW rules** (MORPH-024–MORPH-058), including 5 constraints with diagnostic specifications. Each new constraint remains `spec_only` pending Phase C. The 76–90 source/exception audit is in `PHASE_B_PP76_90_REPORT.md`. Printed pp. 71–73 contain the chapter contents only and are explicitly skipped. Previously approved §1.1 pp. 74–75 remains intact. **Chapter coverage: 17 extracted pages, 3 justified skips, 122 unprocessed (of 142 printed pages).** Not independently reviewed or detector-integrated; chapter is incomplete.


---

## Phase B update — 2026-11-10 (printed pp. 91–114)

An additional **70 original source-cited records** are staged for grammar knowledge and learner-content generation, with page-by-page source and exception notes in `PHASE_B_PP91_114_REPORT.md`. The Chapter 3 ledger contains **41 extracted, 3 contents-only skips, 98 unprocessed** pages. Detector activation and full-chapter gates remain separate work. Continue from p. 115 without user approval pauses.
