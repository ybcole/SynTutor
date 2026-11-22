# H01 and H02 Evaluation Rubric and Scoring Protocol (Finalized Textbook-Based Design)

**Project:** SynTutor: An Explainable AI-Based Framework for Syntax Tree-Driven Grammar Analysis and Learning Using NLP  
**Date Frozen:** 2026-11-22  
**Status:** **FROZEN PRE-EVALUATION SPECIFICATION** — verified on separate synthetic regression fixtures (`test_run_textbook_h01_h02.py`, `8/8` passing); SynTutor has **not** been executed on the 100-sentence dataset.
- Dataset SHA-256 (`H01_H02_PROPOSED_100_SENTENCES.csv`): `ce3020a0cd28796c5ffe71bf0772c66773d3b1154323c823df8ccc3a22e065d6`
- Frozen Runner SHA-256 (`run_textbook_h01_h02.py`): `3815ad1b74647dddaf9dea651a9914b670a375dccc195bd3f2b85f26c3634910`
- Regression Suite SHA-256 (`test_run_textbook_h01_h02.py`): `0b8f1cbf4c9bfa0cad0cb3d508d8a604071bc8fad2a7a8275ae8852a2c680368`

---

## 1. H01 — Burton–Roberts Syntax-Tree Evaluation Rubric (Four Separated Tracks)

### 1.1 Non-Circularity and No-Fabrication Rules

1. **Neither Benepar nor SynTutor may ever serve as its own answer key.**
2. **No missing textbook tree may be invented.** Only published Burton–Roberts diagrams and published partial answers are used as structural ground truth.
3. **Never conflate partial-reference agreement or conversion consistency with complete syntax-tree accuracy.** All four tracks are reported separately.

### 1.2 Four Separated H01 Measurements

| Track | Measurement | Dataset Scope | Contamination Status | Objective Metrics | Fair Handling of Triangles & Alternatives |
| :-: | :--- | :--- | :--- | :--- | :--- |
| **1** | **Full-Tree Structural Accuracy** | `216` active published B–R diagrams (`web/content/book/ch01`–`ch10`) + Ch. 10 p. 239 `[79b]` | **Development-exposed (explicitly disclosed)** | Labeled & Unlabeled PARSEVAL Precision/Recall/F1, Exact Tree Match, All-Attempts F1 (unresolved & yield-mismatched items retained as `0` matches); zero-hit book-lookup sentinel enforced (`AssertionError` if invoked). | Report (a) `85` zero-triangle complete diagrams only, (b) all-attempts full F1, and (c) triangle-aware masked F1 side by side; use both character-offset and strict token-yield alignment. |
| **2** | **Unseen Published-Reference Partial Relations** | `16` unseen grammatical items (`G01`–`G06`, `G16`–`G17`, `G25`–`G27`, `G36`–`G40`: `6` Simple, `5` Moderate, `5` Complex) | **Unseen (`0/16`)** | Scored **exclusively** on the specific relations genuinely verified by `score_h01_partial()` against B–R *Discussion of exercises* (pp. 82, 105, 218–220, 249–251): subject/predicate/complement spans + V-complement sisterhood (`G01`–`G06`), S-adverbial parent attachment (`G16`), V-complement vs. nested VP-adjunct sisterhood (`G17`), wh/C fronting (`G25`), NP-internal relative containment (`G26`), overt `to`-infinitival span (`G27`), and published ACA overt clause spans & nesting (`G36`–`G40`). Every item explicitly logs `checked_relations` and `not_checked_relations` (unprinted internal NP/PP subtrees, covert traces/controllers `•`, lexical subcategory feature tags). **Never reported as complete syntax-tree accuracy.** | Character-offset span comparison fairly accommodates equivalent contraction/hyphen splits (`didn't`, `contact-lenses`, `sedan-chair`). |
| **3** | **B–R Rule Compliance** | All `50` unseen grammatical items (`G01`–`G50`: `15S`/`20M`/`15C`) | **Unseen (`0/50`)** | Deterministic Burton–Roberts Ch. 1–10 structural invariants: canonical B–R label inventory only (zero leaked raw Penn tags), valid `S`/`S'` root, `NP`/`NOM` structural well-formedness, `S'`/`C` fronting in interrogatives, and non-empty terminal yield. | Evaluates rule compliance objectively without fabricating gold trees for the `34` prompt-only/CGEL sentences. |
| **4** | **Benepar→B–R Conversion Consistency** | All `50` unseen grammatical items (`G01`–`G50`: `15S`/`20M`/`15C`) | **Unseen (`0/50`)** | Canonical resolution rate (`status == "normalized"`), JSON schema validity (`docs/canonical-burton-roberts-tree.schema.json`), character-yield preservation rate, and deterministic repeatability. | All `50` items remain in the denominator (`15/20/15`). |

---

## 2. H02 — Fair Outcome-Based Primary Comparison (`N = 100`, Arm A vs. Arm B)

To avoid rigging the comparison in Arm A's favor, **the primary H02 comparison measures ONLY outcomes that both Arm A and Arm B can legitimately achieve** without exact prose-wording matching and **without penalizing Arm B merely for lacking internal `C-*`/`CLS-*` rule IDs or Cambridge source templates**:

| # | Primary Fair Outcome Metric | Pass (`1`) — Identical Rule for Arm A & Arm B | Fail (`0`) |
| :-: | :--- | :--- | :--- |
| **O1** | **Correct Grammatical Judgment** | `G01`–`G50`: verdict is `grammatical`.<br>`U01`–`U50`: verdict is `ungrammatical`. | Misclassification (`grammatical` ↔ `ungrammatical`), or abstention (`unverified`/`unresolved`) on strict judgment accuracy *(abstentions logged separately)*. |
| **O2** | **Exact Position-Aware Error Localization** | `U01`–`U50`: at least one emitted localized `(start, end)` character span (Arm A: `unified_findings`/`node_details`/`cambridge_evaluation` exact token/char offsets; Arm B: `corrector.sweep` exact word-position span) intersects the exact resolved character span(s) of pre-registered `Affected words`. Wrong occurrences of repeated words and overly broad whole-sentence spans (`>65%` of sentence length when target is `≤45%`) are strictly rejected.<br>`G01`–`G50`: zero spurious error spans emitted. | Missed target span, wrong occurrence of a repeated word, overly broad unlocalized span, or spurious error span on `G01`–`G50`. |
| **O3** | **Valid Correction** | `U01`–`U50`: emitted correction matches `Expected correction` **OR any pre-registered `Valid alternatives`** after case, whitespace, and contraction/apostrophe normalization (for Arm A, learner-visible `learner_analysis.revision.text` and API `summary.corrected_sentence` are both logged, with primary correction compared fairly alongside Arm B's `corrector.sweep` `corrected_text`).<br>`G01`–`G50`: no erroneous rewrite emitted. | Missing correction or invalid/ungrammatical rewrite on `U01`–`U50`; spurious rewrite altering a grammatical sentence on `G01`–`G50`. |
| **O4** | **Absence of Demonstrably Incorrect or Unsupported Feedback (Primary H02 Endpoint)** | Pass (`1` = Clean) iff **ZERO** demonstrable errors occur:<br>1. No false-positive error verdict, error span, or rewrite on grammatical `G01`–`G50`;<br>2. No false-negative `grammatical` certification on ungrammatical `U01`–`U50`;<br>3. No wrong-target or overly broad unlocalized span on `U01`–`U50`;<br>4. No invalid/corrupting rewrite string; and<br>5. No internal self-contradiction (e.g., `grammatical` verdict alongside active error spans/rewrites, or citing nonexistent tokens/nodes). | Fail (`0` = Demonstrably Incorrect / Unsupported Feedback) if **any** of conditions 1–5 is violated.<br>**Fairness & Anti-Gaming Rules:** Absence of `C-*`/`CLS-*` rule IDs is **never** counted as an O4 error. Principled abstention (`unverified` with no false claim) is reported **separately** (overall, Grammatical `n=50`, Ungrammatical `n=50`) and **strictly excluded** from both successful error detection (`O1`) and `O4_decided_clean` (`O4 & ~abstained`), ensuring an arm cannot game scores by abstaining. |

### Primary Paired Endpoints (Symmetrical Across Both Arms)
- **Primary Binary Endpoints (Exact McNemar):** **Demonstrably Incorrect / Unsupported Feedback Rate (`1 - O4`)** reported side by side with **Decided Clean Feedback Rate (`O4_decided_clean` = `O4 & ~abstained`)** and **Separate Abstention & Error-Detection Breakdown** (overall abstention, grammatical false-positive vs. abstention, ungrammatical detection recall vs. abstention vs. missed-as-grammatical).
- **Secondary Binary Endpoints (Exact McNemar):** `O1` (Judgment), `O2` (Exact-Position Localization), `O3` (Valid Correction), and `O1 & O2 & O3 & O4` (Full Outcome Adequacy).
- **Primary Ordinal Endpoint (Paired Wilcoxon Signed-Rank):** **Fair Outcome Composite Score (`0–4`)** = `O1 + O2 + O3 + O4_decided_clean`.

---

## 3. Separate Structured Grounding Diagnostics (Reported Independently — Never Used to Penalize Arm B)

These diagnostics evaluate SynTutor's internal rule-grounding machinery **separately** from the primary Arm A vs. Arm B comparison:

| # | Separate Diagnostic | Evaluated On | What It Measures |
| :-: | :--- | :--- | :--- |
| **D1** | **Structured Rule Application Accuracy** | Arm A (descriptive) | On `U01`–`U50`: whether at least one fired constraint/Cambridge rule ID (`C-*`, `CLS-*`, `COMP-*`, `PHR-*`, `MORPH-*`, `OTH-*`, `WCAT-*`) matches the pre-registered grammatical rule family (`SynTutor rule mapping`). On `G01`–`G50`: zero spurious violation rules fired. |
| **D2** | **Structured Evidence & Provenance Integrity** | Arm A (descriptive) | Whether (a) every referenced token/node ID exists in the sentence and canonical/working tree, (b) cited source records obey channel provenance (`B-R` for `structural`, `Cambridge` for `grammatical`/`remediation`), and (c) fail-closed provenance gating (`NO_BOOK_BASIS` / `ANALYSIS_UNRESOLVED`) prevents unreviewed claims from being labeled textbook-verified. |

---

## 4. Functioning Grounded vs. Ungrounded Comparison System (Verified)

Both arms execute over the **exact same 100 unseen textbook sentences (`G01`–`G50`, `U01`–`U50`)** using SynTutor's own locally cached models (`spaCy en_core_web_md`, `benepar_en3`, `textattack/roberta-base-CoLA`, `distilbert-base-uncased`):

- **Arm A — Rule-Grounded SynTutor (Production):** Unmodified `analysis_api.build_payload(sentence, variety="standard_english")`: `spaCy/Benepar` → `FINAL-D1` B–R tree → Linguistic Constraint Matrix (`matrix.py` + `ruleset.py` + `licensing.py`) + `193`-rule Cambridge Evaluator (`cambridge_evaluator.py`) + CoLA/DistilBERT fallback + fail-closed provenance-gated XAI.
- **Arm B — Ungrounded Neural/Perturbation Baseline (Verified Functioning Control):** Uses SynTutor's **exact same** neural acceptability classifier (`detector.classify`, `textattack/roberta-base-CoLA`) and masked-language-model perturbation corrector (`corrector.sweep`, `distilbert-base-uncased`) **WITHOUT** artificial rule-matrix throttling:
  - Native unthrottled CoLA classification (`acceptable == True` → `grammatical`; `acceptable == False` → `ungrammatical`) — **not** artificially suppressed by the `0.20` advisory tolerance (`_FLAG_TOLERANCE`) used only when rules are active!
  - Whenever CoLA classifies a sentence as `unacceptable`, `corrector.sweep(sentence, detector.classify_many)` runs to localize the error word (`bad`, token span) and generate a grammaticality-restoring correction (`corrected_text`).
  - Verified on separate non-evaluation smoke fixtures (`"The dog chased the cat."` → `grammatical`, `p=0.97`; `"The dog chase the cat."` → `ungrammatical`, `p=0.35`, localized `'dog' → 'dogs'`, corrected `"The dogs chase the cat."`, `p=0.96`) — confirming Arm B is a **genuinely functioning ungrounded grammar-analysis system**, not an artificially broken stub.

### Explicit Scope of What This Comparison Can and Cannot Prove About H02
- **Can prove:** Whether adding SynTutor's structured linguistic rules (Linguistic Constraint Matrix + Cambridge rules + fail-closed provenance checks) on top of SynTutor's neural acceptability/perturbation components measurably reduces demonstrably incorrect/unsupported feedback (`O4`) and improves grammatical judgment (`O1`), error localization (`O2`), and valid correction (`O3`) on 100 unseen textbook sentences.
- **Cannot prove:** (a) Superiority over external instruction-tuned LLMs, (b) human-perceived pedagogical clarity/readability of free-text prose explanations, or (c) absence of subtle semantic inaccuracies inside free-text prose that accompanies a valid rule ID.

---

## 5. Free-Text Explanation Qualities Outside Automated Scoring

Automated textbook-based scoring **cannot** reliably establish:
1. Natural-language pedagogical clarity, tone, or learner comprehension (evaluated separately by the thesis's H03/H04 learner study).
2. Subtle semantic/factual misstatements inside free-text prose whose verdict and rule ID happen to be correct.
3. Unexpected valid Standard English repairs outside the pre-registered `Valid alternatives` list (mitigated by exporting all non-matching correction strings for lightweight author/adviser inspection before Chapter IV tabulation).

---

## 6. Justified Statistical Tests ($\alpha = 0.05$, Two-Sided)

- **H01:** Wilson 95% CIs (binary metrics), 10,000-resample BCa bootstrap 95% CIs (PARSEVAL F1), **Kruskal–Wallis $H$ + Jonckheere–Terpstra trend test** across Simple/Moderate/Complex strata on continuous scores, and **Fisher–Freeman–Halton exact test** on binary stratum rates.
- **H02 (`N = 100` paired Arm A vs. Arm B):** **Exact two-sided McNemar test** on paired discordant outcomes (`n10` vs. `n01`) for `O4` (primary), `O1`, `O2`, `O3`, and `O1&O2&O3`, plus **paired Wilcoxon signed-rank test** on the `0–4` Fair Outcome Composite Score (`O1+O2+O3+O4`), Holm–Bonferroni correction across secondary endpoints, and Grammatical (`n = 50`) / Ungrammatical (`n = 50`) / Minimal-Pair (`P01`–`P19`) breakdowns.
