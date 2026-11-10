# CGEL full coverage

Phase A infrastructure baseline (2026-11-10). This report does not certify extraction or new detector/XAI implementation. Earlier partial section extractions remain preserved but are not counted as verified full-page coverage.

| Chapter | Total printed pages | Extracted | Unprocessed | Textless | Absent from splits | Completion |
|---|---:|---:|---:|---:|---:|---|
| 1. Preliminaries | 42 | 0 | 41 | 1 | 0 | Incomplete |
| 2. Syntactic overview | 28 | 0 | 27 | 0 | 1 | Incomplete |
| 3. The verb | 142 | 17 | 122 | 3 | 0 | Incomplete — §§1.1–1.8 partial chapter |
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

Totals: 1764 printed pages; 17 extracted pages; 1732 unprocessed; 13 justified textless/contents skips; 2 absent in split files. The 12 exceptional pages were independently checked as textless in the uploaded full PDF. Rules: 231 in catalog (196 previously approved plus 35 NEEDS_REVIEW Chapter 3 candidates). The 35 include 5 spec-only constraints. New implemented detectors: 0. Measured precision/recall by family: not available until Phase C coverage corpus exists.

To verify integrity without asserting completion: python tools/ledger.py check --allow-unprocessed. The strict command python tools/ledger.py check fails until pages are accounted for.

## Phase B incremental extraction (2026-11-10)

Chapter 3 printed pp. 76–90 are recorded with rule IDs and exception notes in `sources/cambridge/chapter_03/PHASE_B_PP76_90_REPORT.md`. Pages 74–75 retain prior approved §1.1 evidence. Pages 71–73 are contents only, not counted as grammar extraction. No chapter is yet complete. Chapter 3 covers 17/142 extracted pages (11.97%); 3 further pages are justified contents-only skips. Prioritised phase-B work must continue with p. 91, and any later source contradictions must trigger revision rather than guesswork.
