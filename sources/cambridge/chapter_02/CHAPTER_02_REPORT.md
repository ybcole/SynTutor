# Chapter 2 (Syntactic overview): final extraction report

Source: *The Cambridge Grammar of the English Language*, Ch. 2, printed pp. 43–69 (PDF page = printed + 20 in the full-book file). Protocol version 1.0.

## Totals

- **Rules:** 97 (all set to `APPROVED` on the user's instruction; see caveat below)
- **Concepts:** 84
- **Cross-references:** 23
- **Conflicts logged:** 3
- **Uncertain items:** 16
- **By rule type:** classification 74, constraint 14, descriptive_generalization 8, stylistic_or_prescriptive 1
- **By domain:** clauses 51, phrases 15, word_categories 13, complementation 10, morphology 3, other 3, agreement 2
- **By confidence:** high 64, medium 33

| Batch | Printed pages | Sections | Rules | Raw file |
|---|---|---|---|---|
| 1 | 44–50 | §1–§2 | 13 | `sources/cambridge/chapter_02/ch02_s1-2_extraction.json` |
| 2 | 50–57 | §3–§5 | 34 | `.../ch02_s3-5_extraction.json` |
| 3 | 57–62 | §6–§10 | 23 | `.../ch02_s6-10_extraction.json` |
| 4 | 62–69 | §11–§17 | 27 | `.../ch02_s11-17_extraction.json` |

## The testable constraints (the part the engine can use)

| ID | Concept | Confidence |
|---|---|---|
| AGR-001 | determinative-noun number agreement | medium |
| AGR-002 | subject-verb agreement | medium |
| CLS-012 | no overt object after an object gap | medium |
| CLS-019 | not even continuation requires a negative clause | medium |
| CLS-022 | negatively oriented polarity-sensitive items | medium |
| CLS-023 | positively oriented polarity-sensitive items | medium |
| CLS-039 | comparative clause: empty measure position | medium |
| COMP-002 | verb subclass determines object | medium |
| COMP-003 | subject obligatory in canonical clauses | medium |
| PHR-007 | attributive modifiers and post-head dependents | medium |
| PHR-011 | singular count nouns need a determiner | medium |
| WCAT-001 | auxiliary vs lexical verbs: not and inversion | medium |
| WCAT-008 | adjectives restricted by function | medium |
| WCAT-009 | adverbs not predicative complements | medium |

Everything else is classification or description. It gives the engine vocabulary and structure, not error checks. Chapter 2 is an overview, so most testable rules will come from Chapters 3, 5, 6, 9 and 18.

## Conflicts to resolve against Burton-Roberts

- Rules CLS-016, WCAT-005, WCAT-004, WCAT-002, PHR-002, COMP-005: These records reflect Cambridge's departures from traditional grammar (auxiliary as head, determinative category, pronoun as noun, copula be as auxiliary, no future tense, narrower 'object'). Burton-Roberts's treatment not supplied; may differ.
- Rules WCAT-011, WCAT-012: Cambridge moves many traditional adverbs and subordinating conjunctions into the preposition category. Burton-Roberts's boundaries were not supplied and may differ.
- Rules CLS-030, CLS-035, CLS-036: Cambridge drops noun/adjective/adverb clauses, treats 'that' in relatives as a subordinator, and replaces restrictive/non-restrictive with integrated/supplementary. Burton-Roberts material not supplied.

## Caveats

1. **No second-pass review was run.** Protocol §13 calls for a separate AI review before approval. All 97 rules were approved directly by instruction. Run the §13 review before the engine relies on the medium-confidence constraints.
2. **Burton-Roberts mappings are all `unverified`.** No Burton-Roberts material was supplied.
3. **Hedged claims.** Several constraints are hedged in the source ("in general", "very restricted exceptions"). Their exceptions are listed in each record's `exceptions` or `review_notes` and need Chapters 4–6, 9 and 13 to complete.
4. **Tree diagrams** (pp. 48–50, 53) were read from extracted text only.
5. **Examples** are almost all AI-authored (2 are the book's own short starred examples, flagged `origin: book`). Run the evaluation set against the engine before trusting any individual sentence.
6. **Copyright.** Do not commit the extracted chapter text or the PDF to a public repo. The JSON files contain paraphrased rules, original examples and page references only.

## Evaluation seed data
`evaluation/` holds 337 grammatical sentences or phrases, 56 ungrammatical ones (from constraints only) and 26 minimal pairs, exported with `tools/export_evaluation.py`. Items marked `unit: phrase` are not full sentences, so filter them if the engine only takes sentences.
