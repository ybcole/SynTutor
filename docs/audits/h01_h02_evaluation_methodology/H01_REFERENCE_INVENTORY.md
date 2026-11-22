# H01 Reference Inventory — Burton–Roberts Syntax-Tree Ground Truth

**Project:** SynTutor: An Explainable AI-Based Framework for Syntax Tree-Driven Grammar Analysis and Learning Using NLP  
**Date Prepared:** 2026-11-22  
**Status:** Pre-evaluation methodology and reference inventory (SynTutor has **not** been run on the proposed evaluation dataset)

---

## 1. Primary Authoritative Reference Verified

| Field | Verified Value |
| :--- | :--- |
| **Author** | Noel Burton-Roberts |
| **Title** | *Analysing Sentences: An Introduction to English Syntax* |
| **Edition** | **3rd edition** (Pearson Education / Longman, 2011; ISBN-13 `9781408233740`) |
| **Inspected File** | `/Users/kiyel/Downloads/Syntax_Reference_Chapters_1-11-1.pdf` |
| **File Size** | `3,146,615` bytes |
| **SHA-256** | `9dee17db3021b45216f9e005eccfdb9f82880ada5fbc852a5fc0945735f22f31` (matches [source_manifest_2026-11-08.json](file:///Users/kiyel/Desktop/SynTutor/sources/burton_roberts/source_manifest_2026-11-08.json)) |
| **Page Coverage** | `263` PDF pages covering **Chapters 1–11**, printed pages **6–268** (PDF page `p` corresponds to printed page `p + 5`) |
| **Companion Volume Missing** | The author-prepared *Answer Book for the Further Exercises* (referenced in the 3rd-edition preface, p. x) is **not included** in the inspected PDF or repository. |

---

## 2. Inventory of Published B–R Diagrams Already Imported into SynTutor (Contaminated for Fresh H01 Testing)

Direct comparison of `Syntax_Reference_Chapters_1-11-1.pdf` against [web/content/book/](file:///Users/kiyel/Desktop/SynTutor/web/content/book/) confirms that **virtually every printed phrase-marker diagram across Chapters 1–10** — including both in-chapter worked figures and end-of-chapter *Discussion of exercises* diagrams — was already transcribed into SynTutor during system development and earlier benchmarking (`252` total records; `216` active in the historical `textbook-parseval` benchmark).

| Chapter | Book Title | Printed Pages Imported | Total Records | `correct=True` | `correct=False` (Rejected Pedagogical Trees) | Records Containing Collapsed Triangles (`triangle: true`) | Complete (`correct=True`, Zero Triangles) |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| `ch01` | Sentence structure: constituents | pp. 7–22 | 15 | 10 | 5 | 2 | 9 |
| `ch02` | Sentence structure: functions | pp. 24–44 | 21 | 19 | 2 | 2 | 17 |
| `ch03` | Sentence structure: categories | pp. 51–65 | 19 | 19 | 0 | 6 | 13 |
| `ch04` | The basic verb phrase | pp. 71–84 | 15 | 15 | 0 | 14 | 1 |
| `ch05` | Adverbials and other matters | pp. 88–109 | 23 | 22 | 1 | 23 | 0 |
| `ch06` | More on verbs: auxiliary VPs | pp. 122–138 | 26 | 26 | 0 | 26 | 0 |
| `ch07` | The structure of noun phrases | pp. 141–170 | 62 | 62 | 0 | 23 | 39 |
| `ch08` | Sentences within sentences | pp. 171–194 | 33 | 33 | 0 | 32 | 1 |
| `ch09` | Wh-clauses | pp. 199–219 | 21 | 21 | 0 | 19 | 2 |
| `ch10` | Non-finite clauses | pp. 226–250 | 17 | 17 | 0 | 14 | 3 |
| **Total** | **Chapters 1–10** | **pp. 7–250** | **252** | **244** | **8** | **161 (63.9%)** | **85 (33.7%)** |

**Provenance statuses in the imported 252 records:** `234` `IMG` (transcribed from printed diagrams), `14` `DERIVED_FROM_INSTRUCTIONS`, and `4` `IMG_ANOMALY`.

### Key Implications of the Imported Diagram Inventory

1. **Development Contamination:** Because SynTutor's `FINAL-D1` projector (`server/burton_roberts.py`), regression tests, and historical evaluation scripts (`docs/audits/technical_evaluation/run_real_world_reliability.py`) were developed and debugged directly against these `252` records, **none of them may be used as unseen confirmatory H01 test data**.
2. **Pervasive Triangle Abbreviation in Higher Chapters:** Burton–Roberts systematically collapses previously taught constituents (especially NPs, PPs, APs, and subordinate clauses) into pedagogical triangles once new syntax topics are introduced. Consequently, **100%** of imported Chapter 5 (`23/23`) and Chapter 6 (`26/26`) diagrams, **97.0%** of Chapter 8 (`32/33`), **90.5%** of Chapter 9 (`19/21`), and **82.4%** of Chapter 10 (`14/17`) diagrams are **abbreviated rather than complete full phrase markers**.
3. **Only One Non-Imported Printed Sentence Diagram Identified in the PDF:** As independently verified during earlier auditing ([H01_H02_VALIDATION_BLOCKER_RESOLUTION.md](file:///Users/kiyel/Desktop/SynTutor/docs/audits/H01_H02_VALIDATION_BLOCKER_RESOLUTION.md)), Chapter 10, **p. 239 `[79a–b]`** (*"He didn't remember kissing Millie."*) was absent from `web/content/book/ch10.trees.json`. However, even `[79b]` (a) collapses two NPs with triangles, (b) contains an empty `C1` and covert co-indexed subject, and (c) was already executed once in `run_hypothesis_checks.py`. Other omitted diagrams in the PDF are fragment-only (`p. 236 [38c]` subject NP only), Abbreviated Clausal Analyses (`pp. 219–220`, `250–251`), or deliberately ill-formed (`p. 266 [12]`). Accordingly, `[79a–b]` is **excluded** from the proposed 100-sentence unseen dataset.

---

## 3. Inventory of Uncontaminated Burton–Roberts 3rd Ed. Sentences Available in the Attached PDF

Direct inspection of *Exercises*, *Discussion of exercises*, and *Further exercises* across Chapters 1–10 in `Syntax_Reference_Chapters_1-11-1.pdf` identified **a substantial pool of authentic Burton–Roberts sentences that were never imported into `web/content/book/` or any SynTutor test, lesson, or evaluation file (`Previous development use = No`)**. These fall into two distinct reference-availability tiers:

### Tier A — Unused Textbook Exercises with Published Partial / Functional / ACA Answers in the PDF

These items have **verified author-published linguistic answers** in Burton–Roberts' *Discussion of exercises*, providing objective ground truth for clause boundaries, major functions (`S`, `V`, `dO`, `iO`, `sP`, `oP`, `PC`, `aA`, `sA`), verb subcategories (`[intrans]`, `[trans]`, `[ditrans]`, `[intens]`, `[complex]`, `[prep]`, `[phrasal]`), question/relative transformations, or covert-constituent controllers — **but do not include a complete uncollapsed phrase-marker tree diagram**:

| Chapter & Section | Printed Pages | Published Answer Type in PDF | Selected Unused Sentences Included in Proposed Dataset (`H01_H02_PROPOSED_100_SENTENCES.csv`) |
| :--- | :--- | :--- | :--- |
| Ch. 4, Exercise 1 | p. 81 (ans. p. 82) | Bracketed major functions (`S`, `V`, `dO`, `iO`, `sP`, `oP`, `PC`) + verb subcategory | `G01`–`G06` (6 Simple sentences covering all 6 B–R verb complementation types) |
| Ch. 5, Exercise 1(g)–(h) | p. 103 (ans. p. 105) | Bracketed functions + `Prt`, `aA`, `sA` + verb subcategory (explicitly excluded from Ex. 2 diagrams) | `G16`–`G17` (2 Moderate sentences) |
| Ch. 9, Exercises 1–2 | pp. 216–217 (ans. p. 218) | Published wh-fronting & restrictive-relative derivations | `G25`–`G26` (2 Moderate sentences) |
| Ch. 9, Exercise 4(a),(b),(d) | p. 217 (ans. pp. 219–220) | Published Abbreviated Clausal Analyses (ACAs) + clause types & functions (`S1`–`S4`) | `G36`–`G38` (3 Complex sentences) |
| Ch. 10, Exercise 1(iii) | p. 247 (ans. p. 249) | Published covert-subject & controller identification (`Morgan` controls covert subject) | `G27` (1 Moderate sentence) |
| Ch. 10, Exercise 3(i),(iii) | p. 248 (ans. pp. 250–251) | Published ACAs + clause forms & functions (`S1`–`S3`, covert constituents) | `G39`–`G40` (2 Complex sentences) |

### Tier B — Unused Textbook Further Exercises & Unimported In-Text Examples (Prompt-Only in PDF)

These items are **authentic Burton–Roberts 3rd ed. sentences** (specifically designed by Burton–Roberts for full phrase-marker drawing in Ch. 4, 7, 8, 9, and 10), verified completely absent from SynTutor's codebase (`0` repo-wide substring hits), but their published trees reside in the separate *Answer Book for the Further Exercises* (not in the attached PDF):

| Chapter & Section | Printed Pages | Syntactic Scope in Burton–Roberts | Selected Unused Sentences Included in Proposed Dataset |
| :--- | :--- | :--- | :--- |
| Ch. 4, Further Ex. 1(1),(5) | p. 85 | Basic intensive & intransitive simple clauses | `G07`–`G08` (2 Simple) |
| Ch. 6, In-text `[96a]` | p. 132 | Closed interrogative with perfect `have` | `G28` (1 Moderate, paired `P08`) |
| Ch. 7, Further Ex. 2(b),(d),(e),(f),(g) | p. 164 | Burton–Roberts' capstone review of complete simple-sentence phrase markers (inversion, genitives, multi-aux passives, NP/VP coordination) | `G18`–`G22` (5 Moderate) |
| Ch. 8, Further Ex. 1(f), 2(d),(g),(h) | p. 195 | Finite subordinate clauses (adverbial, AP-complement, depth-2 embedding) | `G23`–`G24` (2 Moderate), `G41`–`G42` (2 Complex) |
| Ch. 9, Further Ex. 1(8),(12) | pp. 220–221 | Long-distance wh-extraction across finite & extraposed clauses | `G43`–`G44` (2 Complex) |
| Ch. 10, Further Ex. 1(a),(b) | p. 251 | Multiple wh-fronting & stacked non-finite clauses | `G45`–`G46` (2 Complex) |

### Tier C — CGEL (2002) Published Grammatical Counterparts for Minimal-Pair Alignment

The remaining `19` grammatical sentences (`G09`–`G15`, `G29`–`G35`, `G47`–`G50`, plus `G28` from B–R) are verbatim published grammatical originals from Huddleston & Pullum (2002) serving as exact minimal-pair controls (`P01`–`P19`) for H02 while also providing clean, unambiguous single- and multi-clause English structures for H01 once gold B–R trees are annotated.

---

## 4. Finalized Textbook-Based H01 Strategy and Obstacles to Objective Scoring

Because the research design uses **published Burton–Roberts textbook answers as primary references without recruiting additional annotators/reviewers**, no missing full phrase markers are invented for the `34` prompt-only/CGEL sentences. Instead, H01 is partitioned cleanly into **four separated objective measurements**:

1. **Full-Tree Structural Accuracy (Disclosed Development-Exposed Track):** PARSEVAL F1 and Exact Match on the `216` active published diagrams in `web/content/book/` (`85` complete zero-triangle `correct=True` records + triangle-abbreviated records) plus Ch. 10 p. 239 `[79b]`, run with book-tree lookup disabled (`0` hits) and reporting complete-tree, all-attempts, and triangle-aware F1 side by side.
2. **Unseen Published-Reference Agreement (`16 / 50` Unseen Grammatical Items):** Strictly limited to the constituent spans, complement-vs.-adjunct attachments, wh/relative structures, and overt clause boundaries explicitly published in Burton–Roberts' *Discussion of exercises* (`G01`–`G06` p. 82, `G16`–`G17` p. 105, `G25`–`G26` p. 218, `G27` p. 249, `G36`–`G38` pp. 219–220, `G39`–`G40` pp. 250–251).
3. **B–R Rule Compliance (`50 / 50` Unseen Grammatical Items):** Deterministic adherence to Burton–Roberts Ch. 1–10 structural conventions (canonical label set, `S`/`S'`/`C` fronting, X-bar `NP`/`NOM` structure, non-empty yield).
4. **Benepar-to-B–R Conversion Consistency (`50 / 50` Unseen Grammatical Items):** Canonical resolution rate, JSON schema validity, character-yield preservation, and deterministic repeatability across Simple (`15`), Moderate (`20`), and Complex (`15`) strata.

| Obstacle | Description | Mandatory Methodological Handling |
| :--- | :--- | :--- |
| **1. No unseen complete printed B–R trees in the attached PDF** | All `252` published diagrams in Chapters 1–10 (except `[79b]`, already probed) are already in `web/content/book/`, and the *Answer Book for the Further Exercises* is not included. | **Never** present the `216` imported diagrams as unseen holdout data, **never** invent gold trees for the `34` prompt-only/CGEL items, and **never** use Benepar or SynTutor outputs as a gold answer key. Report dev-exposed full-tree accuracy separately from the `16` unseen partial-reference items and the `50` unseen conversion/compliance items. |
| **2. Triangle abbreviation vs. complete trees** | `161/252` textbook diagrams collapse NPs, VPs, PPs, or clauses into triangles. Scoring a full predicted tree against a triangle-abbreviated diagram penalizes valid internal constituents unless triangle-aware masking is applied. | Report **zero-triangle complete diagrams**, **all-attempts full F1**, and **triangle-aware masked F1** side by side so neither penalty distortion nor hidden subtree errors are obscured. |
| **3. Covert nodes, traces, and co-indexing (`•`, `e`, `C1`/`C2`, empty `DET`)** | Burton–Roberts Chapters 6–10 introduce movement gaps (`•`), empty complementisers (`C1`/`C2`), empty `DET`, and controller co-indices (`i`) not emitted by surface Benepar parses. | Score **overt published spans and clause nesting** objectively on the `16` partial-reference items, and log absent covert traces/controllers separately as a documented pipeline limitation rather than inventing gold annotations. |
| **4. Structural ambiguity** | Textbook exercises explicitly flag ambiguous sentences (e.g., Ch. 5 p. 110; Ch. 10 p. 252). | **Ambiguous exercise prompts were deliberately excluded** from `G01`–`G50` so every item has an unambiguous primary syntactic analysis. |
| **5. Contraction and hyphen tokenization** | Tokenization differences (`didn't` vs. `did + n't`, `contact-lenses` vs. `contact - lenses`, `sedan-chair`) caused 15/216 yield mismatches in legacy strict-token PARSEVAL. | Use **character-offset span alignment** (primary, fair to equivalent token splits) alongside strict token-yield alignment, retaining all unresolved or yield-mismatched items in the denominator as `0` matches. |
| **6. Deliberately rejected (`correct=False`) diagrams** | 8 imported records illustrate analyses Burton–Roberts explicitly rejects (e.g., Ch. 5 p. 88 `[11]`). | Excluded from grammatical gold scoring. |
