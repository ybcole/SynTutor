# Chapter III — Proposed Research Methodology Draft (Textbook-Based H01 and H02 Evaluation)

> [!IMPORTANT]
> **Alignment Notice for Thesis Adviser / Panel Review (Do Not Silently Overwrite Approved Chapter III):**  
> This draft preserves the original hypotheses in [CHAPTER1_REVISED.md](file:///Users/kiyel/Desktop/SynTutor/docs/research/CHAPTER1_REVISED.md) while updating the technical evaluation procedure in [CHAPTER3_REVISED.md](file:///Users/kiyel/Desktop/SynTutor/docs/research/CHAPTER3_REVISED.md) and [CHAPTER4_REVISED.md](file:///Users/kiyel/Desktop/SynTutor/docs/research/CHAPTER4_REVISED.md) to use **directly verified published textbook answers from Burton–Roberts (2011) and Huddleston & Pullum (2002)** as primary objective references, without requiring recruitment of additional reviewers. Methodological updates flagged for adviser/panel approval:
> 1. Replacing the development-exposed 104-sentence legacy zero-regression check with a **contamination-audited (`0/100`) unseen 100-sentence textbook corpus** (`50` grammatical stratified by Burton–Roberts complexity + `50` ungrammatical verified in CGEL/B–R).
> 2. Separating H01 into **four objective textbook-grounded tracks** (dev-exposed published full-tree PARSEVAL on `216+1` book diagrams; unseen published-reference agreement on `16` items with B–R *Discussion of exercises* answers; and unseen B–R rule compliance + Benepar→B–R conversion consistency across all `50` grammatical items) rather than inventing missing gold trees.
> 3. Evaluating H02 via a **fair outcome-based primary comparison** (`O1` Grammatical Judgment, `O2` Error Localization, `O3` Valid Correction, `O4` Absence of Demonstrably Incorrect/Unsupported Feedback) achievable by both rule-grounded SynTutor (Arm A) and a verified functioning ungrounded neural/perturbation baseline using SynTutor's own RoBERTa-CoLA + DistilBERT MLM components (Arm B), while reporting structured rule application (`D1`) and evidence provenance integrity (`D2`) separately so Arm A never receives an automatic advantage merely for containing grounding components.
>
> All procedures describe **planned evaluation work**; no final evaluation runs, accuracy rates, or p-values have been executed or fabricated.

---

## 3.1 Research Design

This study uses a **quantitative, criterion-referenced, and paired quasi-experimental technical evaluation design** to test SynTutor's syntax-tree accuracy (H01) and rule-grounded grammatical feedback reliability (H02), complementing the thesis's classroom learning and usability study (H03–H04). Both H01 and H02 rely directly on **published authoritative textbook answers** rather than recruiting additional external reviewers, and all datasets, reference keys, scoring rules, and statistical tests are frozen **prior** to executing SynTutor on the evaluation corpus.

---

## 3.2 System Under Evaluation

SynTutor is an Explainable AI (XAI)-based web framework for English syntax analysis and grammar learning (`server/analysis_api.py`):
1. **Syntactic Parsing:** `spaCy` (`en_core_web_md`) and Berkeley Neural Parser (`Benepar`, `benepar_en3`).
2. **Burton–Roberts Canonical Tree Projection (`FINAL-D1`):** Deterministic conversion (`server/burton_roberts.py`) into schema-validated canonical Burton–Roberts trees (`docs/canonical-burton-roberts-tree.schema.json`).
3. **Structured Linguistic Rule Evaluation:** Deterministic **Linguistic Constraint Matrix** (`server/matrix.py`, `server/ruleset.py`, `server/licensing.py`; `170` `C-*` rules across `11` domains) and **Cambridge Grammar Evaluator** (`server/cambridge_evaluator.py`, `server/cgel_phase_d.py`; `193` runtime-enabled CGEL rules operating under documented owner waiver).
4. **Advisory Neural Acceptability & Fail-Closed XAI Layer:** CoLA neural acceptability classifier and text-space perturbation corrector (`server/detector.py`, `server/corrector.py`), paired with provenance-gated explanation assembly (`server/explanations.py`, `server/learner_explanations.py`) that emits explicit unresolved/no-basis diagnostics (`ANALYSIS_UNRESOLVED`, `NO_BOOK_BASIS`) rather than fabricating textbook citations.

No production code, models, or grammar rules will be modified in response to the evaluation items.

---

## 3.3 Evaluation Hypotheses

Consistent with Chapter I ([CHAPTER1_REVISED.md](file:///Users/kiyel/Desktop/SynTutor/docs/research/CHAPTER1_REVISED.md)), the original hypotheses are preserved without redefinition:

- **H01:** Evaluates the structural accuracy of SynTutor's final Burton–Roberts syntax trees across different levels of English sentence complexity (*Simple*, *Moderate*, and *Complex*). Because only published textbook answers are used without fabricating missing gold trees, H01 evidence is reported transparently across four separated measurements (dev-exposed full-tree accuracy, unseen partial-reference agreement, unseen B–R rule compliance, and unseen Benepar→B–R conversion consistency), without claiming that conversion consistency or partial agreement proves complete unseen full-tree accuracy.
- **H02:** Evaluates whether grounding SynTutor's grammatical explanations and feedback on structured linguistic rules reduces incorrect or unsupported feedback compared to an ungrounded baseline on identical inputs. Automated textbook-based scoring tests objective verdict, localization, multi-alternative correction, rule-family application, and structured evidence integrity, while explicitly noting that free-text pedagogical clarity remains outside automated proof.

---

## 3.4 Dataset Construction, Classification, and Verification

### 3.4.1 Verified Authoritative Sources
1. **Noel Burton-Roberts (2011),** *Analysing Sentences: An Introduction to English Syntax*, **3rd ed.** (Pearson Education / Longman; inspected PDF covering Chapters 1–11, printed pp. 6–268; SHA-256 verified).
2. **Rodney Huddleston & Geoffrey K. Pullum (2002),** *The Cambridge Grammar of the English Language* (**CGEL**, Cambridge University Press; inspected PDF covering Chapters 1–20, printed pp. 1–1764; SHA-256 verified).

### 3.4.2 Why 100 Sentences Were Selected
The corpus ([H01_H02_PROPOSED_100_SENTENCES.csv](file:///Users/kiyel/Desktop/SynTutor/docs/audits/h01_h02_evaluation_methodology/H01_H02_PROPOSED_100_SENTENCES.csv)) contains **`N = 100` unseen English sentences** (`50` grammatical + `50` ungrammatical) to balance grammatical-control false-positive testing against ungrammatical violation coverage across all six core implemented SynTutor grammar domains while achieving **`83.7%`–`96.1%` exact McNemar power** for moderate-to-large (`+15` to `+20` pp) paired H02 grounding effects and `±10.9` pp Wilson 95% CI precision (at `p = 0.80`) on the `50`-sentence grammatical set:
- **50 Grammatical (`G01`–`G50`):** `15` Simple, `20` Moderate, `15` Complex (`31` from Burton–Roberts unused Exercises/Further Exercises/in-text examples + `19` from CGEL grammatical originals).
- **50 Ungrammatical (`U01`–`U50`):** `46` verbatim published `*` ungrammatical textbook originals + `4` explicitly labeled CGEL minimal-pair variants (`U11`, `U19`, `U35`, `U42`), including `19` exact minimal pairs (`P01`–`P19`) across Verb Form/Auxiliaries/Modals (`10`), Subject–Verb Agreement (`9`), Pronoun Case/Genitives/Reflexives (`9`), Determiners/Articles/Count-Mass (`7`), Complementation/Valency/Word Order (`8`), and Clauses/Polarity/Comparatives/Coordination/Punctuation (`7`).

### 3.4.3 Structural Difficulty Classification
Difficulty is classified **strictly by Burton–Roberts syntactic structure**, not word count:
- **Simple (`15`):** Single finite clause `S`, zero subordinate clauses, zero clause coordination, covering all six basic B–R verb complementation types (`Ch. 4`).
- **Moderate (`20`):** Single finite clause with multi-auxiliary chains, passive movement, subject–auxiliary inversion, wh-fronting, split phrasal verbs, layered VP/S-adverbials, or coordination; OR one shallow subordinate clause (`Ch. 5–9`).
- **Complex (`15`):** Depth $\ge 2$ clausal embedding (`2+` subordinate clauses), long-distance wh-extraction, stacked non-finite raising/control/participial clauses, or extraposed clausal subjects (`Ch. 8–10`).

### 3.4.4 Reference Verification and Contamination Screening
Every sentence, chapter, section, printed page, and expected answer was verified directly against the two PDFs. Two-stage automated contamination screening (structured index of `8,219` strings + full repository-wide substring audit across code, book trees, lessons, assessments, rules, and tests) confirmed **`0 / 100` prior development exposure** (8 overlapping draft candidates were replaced before freezing). Structurally ambiguous prompts, CGEL `%` style/dialect-divided constructions, prescriptive myths rejected by CGEL, and pragmatic `#` oddities were excluded.

---

## 3.5 Reference Tiers and Scoring Procedure

### 3.5.1 H01 — Four Separated Objective Tracks
1. **Full-Tree Structural Accuracy (Disclosed Dev-Exposed Track):** PARSEVAL Labeled/Unlabeled F1 and Exact Match on the `216` active published B–R diagrams in `web/content/book/` (`85` zero-triangle complete + triangle-abbreviated) plus Ch. 10 p. 239 `[79b]`, run with book-tree lookup disabled (`0` hits) and reporting complete-tree, all-attempts, and triangle-aware F1 side by side under both character-offset and strict token alignment.
2. **Unseen Published-Reference Agreement (`16 / 50` Unseen Grammatical Items):** Scored strictly on constituent spans, complement-vs.-adjunct attachments, wh/relative structures, and overt ACA clause boundaries explicitly published in Burton–Roberts *Discussion of exercises* (`G01`–`G06` p. 82, `G16`–`G17` p. 105, `G25`–`G26` p. 218, `G27` p. 249, `G36`–`G40` pp. 219–220, 250–251).
3. **B–R Rule Compliance (`50 / 50` Unseen):** Deterministic verification of Burton–Roberts Ch. 1–10 structural invariants (canonical label set, X-bar `NP`/`NOM`, `S'`/`C` fronting, yield integrity).
4. **Benepar→B–R Conversion Consistency (`50 / 50` Unseen):** Canonical resolution rate, JSON schema validity, character-yield preservation, and deterministic repeatability.

No gold trees are fabricated for the `34` unseen sentences lacking published B–R diagrams (`15` *Further Exercises* whose separate *Answer Book* is absent, `1` B–R in-text example, `18` CGEL grammatical originals).

### 3.5.2 H02 — Fair Outcome-Based Comparison and Separate Grounding Diagnostics
To ensure Arm B is not penalized merely for having structured rule engines disabled, the **primary Arm A vs. Arm B comparison** evaluates four outcomes that **both arms can legitimately achieve** (never using exact prose-wording matching):
- **O1 — Correct Grammatical Judgment:** Match against published CGEL/B–R grammaticality (`G01`–`G50` = grammatical, `U01`–`U50` = ungrammatical; abstentions logged separately).
- **O2 — Correct Error Localization:** Token/character span overlap with pre-registered `Affected words` on `U01`–`U50`; zero spurious error spans on `G01`–`G50`.
- **O3 — Valid Correction:** Normalized match against `Expected correction` or any pre-registered `Valid alternatives` on `U01`–`U50`; zero erroneous rewrites on `G01`–`G50`.
- **O4 — Absence of Demonstrably Incorrect or Unsupported Feedback (Primary Endpoint):** Zero false-positive flags/rewrites on `G01`–`G50`, zero false-negative `grammatical` certifications on `U01`–`U50`, zero wrong-target localizations on `U01`–`U50`, zero invalid/corrupting rewrites, and zero internal self-contradictions. Absence of `C-*`/`CLS-*` rule IDs is never counted as an error for Arm B.

Structured rule-family accuracy (**D1**) and structured tree/source provenance integrity (**D2**) are reported **separately** as Arm A grounding diagnostics.

**Comparable Paired Arms (`N = 100` identical inputs):**
- **Arm A (Rule-Grounded SynTutor):** Unmodified production `analysis_api.build_payload(sentence, variety="standard_english")`.
- **Arm B (Ungrounded Neural/Perturbation Baseline):** Uses SynTutor's own locally cached `textattack/roberta-base-CoLA` classifier (`detector.classify`, native unthrottled binary judgment) and `distilbert-base-uncased` masked-language-model perturbation corrector (`corrector.sweep`) for localization and repair, without SynTutor's Linguistic Constraint Matrix or Cambridge rule registry.

---

## 3.6 Statistical Analysis Plan

All tests are two-sided ($\alpha = 0.05$, Holm–Bonferroni correction on secondary endpoints):
- **H01:** Wilson 95% CIs (binary metrics), 10,000-resample BCa bootstrap 95% CIs (PARSEVAL F1), **Kruskal–Wallis $H$ + Jonckheere–Terpstra trend test** across Simple/Moderate/Complex strata on continuous structural scores, and **Fisher–Freeman–Halton exact test** on binary stratum rates.
- **H02 (`N = 100` paired):** **Exact two-sided McNemar test** on paired discordant outcomes (`n10` vs. `n01`) for `O4` (primary incorrect/unsupported feedback rate) and secondary outcome endpoints (`O1`, `O2`, `O3`, `O1&O2&O3`), plus **paired Wilcoxon signed-rank test** on the symmetrical `0–4` Fair Outcome Composite Score (`O1+O2+O3+O4`, reporting median difference and rank-biserial $r$), alongside Grammatical (`n = 50`), Ungrammatical (`n = 50`), and Minimal-Pair (`P01`–`P19`) breakdowns.

---

## 3.7 Scope of Evidence, Remaining Limitations, and Ethics

- **What Results Can Support H01 and H02:** For H01, the four separated tracks transparently report dev-exposed full-tree fidelity (`216+1`), unseen partial-reference agreement (`16`), and unseen compliance/conversion (`50`) without misrepresenting partial agreement or conversion consistency as complete unseen tree accuracy. For H02, statistically significant Arm A vs. Arm B gains on `O1`–`O4` directly establish whether structured linguistic rules reduce demonstrably incorrect/unsupported feedback relative to SynTutor's ungrounded neural acceptability/perturbation components on 100 unseen textbook sentences.
- **Remaining Limitations:** (a) No unseen complete printed B–R trees exist in the attached PDF without the separate *Answer Book*; (b) automated scoring cannot establish free-text pedagogical clarity, learner readability, or subtle semantic misstatements inside prose carrying a valid rule ID; (c) Arm A vs. Arm B isolates rule grounding inside SynTutor rather than benchmarking external LLMs; (d) `193` runtime Cambridge rules operate under `owner_waiver: true, independent_review: false`; and (e) small binary H01 stratum gaps (`n = 15/20/15`, `n = 6/5/5`) and small H02 effects (`≤ 10` pp) are underpowered.
- **Copyright and Reproducibility:** Only bibliographic locators, structural metadata, and short isolated textbook examples are stored. Git commit hashes, PDF/CSV SHA-256 digests, and read-only offline evaluation scripts (`run_textbook_h01_h02.py`, `test_run_textbook_h01_h02.py`) are archived for exact reproducibility.
