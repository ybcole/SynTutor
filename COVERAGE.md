# CGEL printed-page coverage

**Phase B extraction status: 2026-11-10.** Pages are counted as extracted when a page-specific source audit report is recorded. This is not a claim of full-chapter audit, new live diagnostic detection, or completion of the 20-chapter reference.

| Chapter | Printed pages | Extracted | Unprocessed | Skipped | Absent from split | Status |
|---|---:|---:|---:|---:|---:|---|
| 1. Preliminaries | 42 | 0 | 41 | 1 | 0 | Incomplete |
| 2. Syntactic overview | 28 | 0 | 27 | 0 | 1 | Incomplete |
| 3. The verb | 142 | 97 | 42 | 3 | 0 | Incomplete |
| 4. The clause: complements | 110 | 0 | 109 | 1 | 0 | Incomplete |
| 5. Nouns and noun phrases | 202 | 0 | 201 | 0 | 1 | Incomplete |
| 6. Adjectives and adverbs | 72 | 0 | 71 | 1 | 0 | Incomplete |
| 7. Prepositions and preposition phrases | 66 | 0 | 65 | 1 | 0 | Incomplete |
| 8. The clause: adjuncts | 122 | 0 | 122 | 0 | 0 | Incomplete |
| 9. Negation | 66 | 0 | 65 | 1 | 0 | Incomplete |
| 10. Clause type and illocutionary force | 96 | 0 | 95 | 1 | 0 | Incomplete |
| 11. Content clauses and reported speech | 84 | 0 | 84 | 0 | 0 | Incomplete |
| 12. Relative constructions | 66 | 0 | 66 | 0 | 0 | Incomplete |
| 13. Comparative constructions | 74 | 0 | 74 | 0 | 0 | Incomplete |
| 14. Non-finite and verbless clauses | 102 | 0 | 101 | 1 | 0 | Incomplete |
| 15. Coordination and supplementation | 90 | 0 | 90 | 0 | 0 | Incomplete |
| 16. Information packaging | 86 | 0 | 85 | 1 | 0 | Incomplete |
| 17. Deixis and anaphora | 116 | 0 | 116 | 0 | 0 | Incomplete |
| 18. Inflectional morphology | 56 | 0 | 55 | 1 | 0 | Incomplete |
| 19. Lexical word-formation | 102 | 0 | 101 | 1 | 0 | Incomplete |
| 20. Punctuation | 42 | 0 | 42 | 0 | 0 | Incomplete |

**Totals:** 1764 printed pages; **97 extracted**, 1652 unprocessed, 13 justified skips and 2 absent from the split sources.

## Chapter 3 implementation

**Catalog:** 196 earlier approved records + 35 rules from pp. 76–90 + 70 rules from pp. 91–114 + 31 from pp. 115–122 + 20 from pp. 123–130 + 21 from pp. 131–138 + 30 from pp. 139–146 + 35 from pp. 147–154 + 35 from pp. 155–162 + 48 from pp. 163–170 = **521 rules**. The error-capable records added during Phase B remain specifications rather than newly integrated runtime detectors; **implemented new detectors: zero**. No new detection precision/recall claim is made.

Chapter 3 is at **97 extracted pages of 142**, plus 3 chapter-contents-only skips and **42 unprocessed (pp. 171–212)**. Source notes: `sources/cambridge/chapter_03/PHASE_B_PP76_90_REPORT.md`, `PHASE_B_PP91_114_REPORT.md`, `PHASE_B_PP115_122_REPORT.md`, and `PHASE_B_PP123_130_REPORT.md`; the later sequential source audit reports through `PHASE_B_PP163_170_REPORT.md` are also in the chapter folder. Continue from printed page **171**. Full-chapter completion gates remain inactive until source coverage is complete; no user sign-off is required for continued extraction.

## Chapter 3 printed pp. 123–130 (2026-11-10)

Added 20 Cambridge-supported explanatory classifications (OTH-047–OTH-066). Coverage now includes the serial/iterative/repeated distinction, perfective versus imperfective viewpoint, temporal reference/orientation/deixis, and special simple-present uses. This batch does not introduce new error detectors. The source audit is `sources/cambridge/chapter_03/PHASE_B_PP123_130_REPORT.md`. The next unprocessed page is 131.

## Chapter 3 printed pp. 131–138 (2026-11-10)

Added 21 source-cited explanatory records (OTH-067–OTH-087). Covered the future-present usage of main-clause futurates versus subordinate clauses, scheduling and prediction, modal *will*, time of orientation, the preterite in past-state interpretations, polite requests and past futurates. No newly active detectors or accuracy claims. Page-level provenance: `sources/cambridge/chapter_03/PHASE_B_PP131_138_REPORT.md`. Next unprocessed printed page: 139.

## Chapter 3 printed pp. 139–146 (2026-11-10)

Added 30 source-cited tense/perfect records (OTH-088–OTH-117), covering compound anteriority, continuative/existential/resultative/recent-past perfects, definite-past adjunct constraints with source exceptions, and dialectal variation. Source audit: `sources/cambridge/chapter_03/PHASE_B_PP139_146_REPORT.md`. Next unprocessed printed page: 147.

## Chapter 3 printed pp. 147–154 (2026-11-10)

Added 35 source-cited classification, descriptive, and usage records (OTH-118–OTH-152) covering perfect omissibility/scope, modal-remoteness contrasts, standard and nonstandard conditional variants, and preterite backshift. Original examples and source exceptions: `sources/cambridge/chapter_03/PHASE_B_PP147_154_REPORT.md`. No active detectors added. Next unprocessed printed page: 155.

## Chapter 3 printed pp. 155–162 (2026-11-10)

Extracted and paraphrased 35 new records (OTH-153–OTH-187), including two tightly bounded diagnostic specifications. The source-based audit covers optional and obligatory backshift, the four original-tense patterns, catenative temporal selection, and tenseless non-finite modifiers: `sources/cambridge/chapter_03/PHASE_B_PP155_162_REPORT.md`. No new detector implementations or performance metrics. Next unprocessed printed page: **163**.

## Chapter 3 printed pp. 163–170 (2026-11-10)

Added 48 source-checked explanatory and diagnostic records (OTH-188–OTH-235) covering progressive aspectuality, cancellable mid-interval/temporary implications, aspectual coercion, stative-versus-dynamic construals, sensation and cognition verb classes. One narrowly guarded error specification, no new active detectors. Full page-by-page exception audit: `sources/cambridge/chapter_03/PHASE_B_PP163_170_REPORT.md`. Next unprocessed printed page is **171**, continuing stance verbs and progressive aspect.
