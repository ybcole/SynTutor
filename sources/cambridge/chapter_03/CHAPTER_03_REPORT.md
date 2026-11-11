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


---

## Phase B update — 2026-11-10 (printed pp. 115–122)

Additional original concepts and one narrowly specified diagnostic covering aspectual *used*, tense/aspect/mood, and event classification were added. See `PHASE_B_PP115_122_REPORT.md` for page-by-page sources and contextual restrictions. **Chapter 3: 49 extracted, 3 contents skips, 90 unprocessed** of 142 printed pages. Continue p. 123 without human approval stops. No new active detectors.


---

## Phase B autonomous continuation — 2026-11-10, printed pp. 155–162

Added **35 original, source-cited records** OTH-153–OTH-187: 33 classifications and 2 narrowly specified constraints. See `PHASE_B_PP155_162_REPORT.md` for page-by-page topics, valid contrasts and exceptions. **89 extracted / 142**, **3 contents-only skips**, **50 unprocessed (163–212)**. Full-book extraction remains incomplete. No new production detector activation or measured diagnostic accuracy. Continue at p. 163 automatically, without per-section user approval.


---

## Phase B autonomous extraction — 2026-11-10, printed pp. 163–170

Added 48 original, source-cited records OTH-188–OTH-235, representing 46 classifications, one generalisation and one bounded error specification. The page-based source report and explicit valid exceptions are in `PHASE_B_PP163_170_REPORT.md`. Chapter 3: **97 extracted**, **3 chapter contents-only skips**, **42 unprocessed (171–212)**. Book total: **1,652 unprocessed**. No new production detectors or claims of measured diagnostic accuracy. Continue from printed p. 171 without user approval pauses.


---

## Phase B autonomous continuation — 2026-11-10, printed pp. 171–178

Added **51 independently paraphrased source-cited classifications**, OTH-236–OTH-286, with valid-usage distinctions and specific exceptions. See `PHASE_B_PP171_178_REPORT.md` for per-page coverage. Chapter 3 now has **105 extracted / 142** printed pages, **3 chapter-contents-only skips**, and **34 unprocessed (179–212)**. Book-wide unprocessed pages: **1,644**. No new runtime detector, lesson, quiz or model metric is claimed. Continue at printed p. 179 without manual approval pauses.


---

## Phase B autonomous continuation — 2026-11-11, printed pp. 179–186

Added **57 paraphrased, narrowly cited records**, OTH-287–OTH-343 (42 classifications and 15 descriptive generalizations), with two original English examples apiece and documented scope qualifications. See `PHASE_B_PP179_186_REPORT.md` for an eight-page source and exception audit. Chapter 3 now has **113 extracted / 142** printed pages; **3 justified contents-only skips**, **26 unprocessed (187–212)**. Full-book unprocessed count is **1,636**. No new runtime detectors, active lesson/quiz generation, precision/recall figures, or independent expert approval are claimed. Continue extraction at printed **p. 187** without manual approval stops.


---

## Phase B autonomous continuation — 2026-11-11, printed pp. 187–194

Extracted **70** new, narrowly sourced records OTH-344–OTH-413 (57 classifications, 12 descriptive generalizations, 1 grammatical constraint specification). OTH-377 records the rule that pure future-time temporal adjuncts take simple present rather than futurity *will*; it remains **spec_only** with embedded-interrogative and conditional/volitional guards, and **zero** detectors have been newly enabled. Complete page evidence and exceptions: `PHASE_B_PP187_194_REPORT.md`. Chapter 3: **121 extracted / 142**, **3 justified chapter-contents skips**, **18 unprocessed (195–212)**; book-wide unprocessed **1,628**. The total catalog stands at **699** rules. No measured runtime accuracy or chapter-level completeness claim. Continue with printed pp. **195–202** without a manual approval stop.


---

## Phase B autonomous continuation — 2026-11-11, printed pp. 195–202

Added **70** independently paraphrased, narrowly cited records OTH-414–OTH-483: 54 classifications, 10 descriptive generalizations, 3 grammatical constraint specifications, 2 variety-restricted forms, and 1 rejected shall/will prescriptive pattern. The three new diagnostics (OTH-439, OTH-453, OTH-458) are **spec_only**, with guard examples; no new detectors are enabled or metrics claimed. Exact per-page distinctions, exceptions, PDF provenance and incomplete p. 202 topic continuation: `PHASE_B_PP195_202_REPORT.md`. Chapter 3: **129 extracted / 142**, **3 contents-only skips**, **10 unprocessed (203–212)**. Book-wide unprocessed count: **1,620**; catalog total **769**. Continue from printed **203** without a manual approval stop.


---

## Phase B autonomous continuation — 2026-11-11, printed pp. 203–210

Added **86 original, narrowly source-cited records**, OTH-484–OTH-569: 75 classifications, 7 descriptive generalizations, 2 variety-restricted records, and 2 reports of traditional tense analyses rejected by Cambridge. They distinguish internal versus external modal-perfect scope, modal polarity/negation, modal and lexical interrogatives, dialect-sensitive *have got to*, quasi-modal *be*, and CGEL's treatment of *will/shall* as mood rather than future tense. Full source audit: `PHASE_B_PP203_210_REPORT.md`. Chapter 3 now **137/142 extracted**, 3 justified contents-only skips and **2 unprocessed (211–212)**. Book-wide unprocessed: **1,612**. Total catalog: **855** records. No active detectors, precision/recall figures, or chapter-wide completion claim. Continue at printed **211** without per-range approval.


---

## Phase B final chapter source extraction — 2026-11-11, printed pp. 211–212

Added **32** original paraphrases cited directly to the complete CGEL PDF (OTH-570–OTH-601), concentrating on idiomatic *be going to*, its register, form, present focus, progressive origin, future-in-past actualisation, intention versus refusal, and footnote exceptions. The detailed final-page report is `PHASE_B_PP211_212_REPORT.md`. **The Chapter 3 source-page inventory is now complete:** 139 extracted pages, 3 justified chapter-contents skips (pp. 71–73), 0 unprocessed and 0 unavailable (printed 71–212 inclusive = 142 pages). Book-wide unprocessed pages: **1,610**; total catalog: **887** records (196 earlier + 691 Phase B). **This is source-extraction completeness only.** Independent content validation, B-R comparison, false-positive testing, runtime diagnostics, learner-facing lessons/quizzes and measured precision/recall remain separate pending gates. No newly active detectors or validated performance figures are claimed. Continue the approved autonomous plan without a manual review requirement.


---

## Chapter 3 cross-domain QA follow-up — 2026-11-11

A new executable audit examines all **695** Chapter 3-cited rules across domain files (not only the 601-item `other.json`), while preserving the **139 extracted / 3 contents-only skips / 0 unprocessed** page ledger. Verified 11 targeted high-risk source checkpoints in the complete PDF and corrected four old split-PDF p.5 locators to full-volume p.95 for printed p.75. Cross-linked CLS-119 ↔ OTH-453 and CLS-100 ↔ COMP-030 to prevent separate evidence being counted as two learner errors. The **35** `spec_only` records feed a **277-case original-English candidate corpus**; **four** legacy approved constraints remain without diagnostic specifications and **all 695 B-R mappings are unverified**, so no runtime rule was newly enabled or detection metric measured. Evidence, exception risks, and the numeric family gaps are documented at `CHAPTER_03_AUTOMATED_QA_20261111.md`. The independent linguistic QA and Phase C/D correction gates remain pending; proceed autonomously without requesting user approval.
