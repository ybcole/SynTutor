# H01 and H02 Final Evaluation Readiness Report (Textbook-Based Design)

**Project:** SynTutor: An Explainable AI-Based Framework for Syntax Tree-Driven Grammar Analysis and Learning Using NLP  
**Date Frozen:** 2026-11-22  
**Branch / Code State:** `fix/syntutor-system-reliability-xai` (zero production code, model, or grammar-rule modifications)  
**Evaluation Execution Status:** **FROZEN & READY TO EXECUTE — NOT YET EXECUTED ON THE 100 EVALUATION SENTENCES.** Runner implemented and verified strictly on separate synthetic regression fixtures (`test_run_textbook_h01_h02.py`: **`8/8` passing**).

### Frozen Evaluation Artifact Checksums (SHA-256)
- `docs/audits/h01_h02_evaluation_methodology/H01_H02_PROPOSED_100_SENTENCES.csv`: `ce3020a0cd28796c5ffe71bf0772c66773d3b1154323c823df8ccc3a22e065d6`
- `docs/audits/technical_evaluation/run_textbook_h01_h02.py`: `3815ad1b74647dddaf9dea651a9914b670a375dccc195bd3f2b85f26c3634910`
- `docs/audits/technical_evaluation/test_run_textbook_h01_h02.py`: `0b8f1cbf4c9bfa0cad0cb3d508d8a604071bc8fad2a7a8275ae8852a2c680368`

---

## 1. Which Sentences Are Ready for Evaluation

All **100 sentences** in [H01_H02_PROPOSED_100_SENTENCES.csv](file:///Users/kiyel/Desktop/SynTutor/docs/audits/h01_h02_evaluation_methodology/H01_H02_PROPOSED_100_SENTENCES.csv) (`50` Grammatical + `50` Ungrammatical; `96` verbatim textbook originals + `4` explicitly labeled CGEL minimal-pair variants; `19` direct minimal pairs `P01`–`P19`; **`0 / 100` repository-wide development contamination**) are verified directly against:
- **Burton–Roberts (2011),** *Analysing Sentences* (3rd ed., Pearson/Longman; `Syntax_Reference_Chapters_1-11-1.pdf`, pp. 6–268; SHA-256 `9dee17db3021b45216f9e005eccfdb9f82880ada5fbc852a5fc0945735f22f31`).
- **Huddleston & Pullum (2002),** *The Cambridge Grammar of the English Language* (CGEL; `Cambridge_Grammar_Chapters_1-20-1.pdf`, pp. 1–1764; SHA-256 `0c2fe2c22d881d3684482069c787aea7fd8490b92d211bfd027e02498b555a25`).

| Evaluation Track | Dataset / Sentence IDs | Count | Contamination Status | Reference Basis | Ready? |
| :--- | :--- | ---: | :--- | :--- | :--- |
| **H01 — Track 1: Full-Tree & Triangle-Aware Structural Accuracy** | Published B–R book diagrams in `web/content/book/ch01`–`ch10` (`216` active: `85` complete zero-triangle + triangle-abbreviated) + Ch. 10 p. 239 `[79b]` | `216` (+`1`) | **Development-exposed (`Yes`) — MUST BE DISCLOSED** | Author-published printed B–R phrase markers, run with book-lookup sentinel (`0` hits) | **Yes** *(descriptive full-tree track)* |
| **H01 — Track 2: Unseen Published-Reference Agreement** | `G01`–`G06` (`6` Simple), `G16`–`G17`, `G25`–`G27` (`5` Moderate), `G36`–`G40` (`5` Complex) | **16** | **Unseen (`0/16`)** | Author-published partial structural answers in B–R *Discussion of exercises* (pp. 82, 105, 218–220, 249–251) | **Yes** *(book-established relations only)* |
| **H01 — Tracks 3 & 4: Unseen B–R Rule Compliance & Conversion Consistency** | All `50` grammatical sentences (`G01`–`G50`: `15S`/`20M`/`15C`) | **50** | **Unseen (`0/50`)** | Deterministic B–R canonical schema & Ch. 1–10 structural invariants (never reported as complete tree accuracy) | **Yes** |
| **H02 — Primary Fair Outcome Comparison (Arm A vs. Arm B)** | All `100` sentences (`G01`–`G50` + `U01`–`U50`) | **100** | **Unseen (`0/100`)** | Published CGEL/B–R grammaticality, affected spans, primary corrections, and valid alternatives | **Yes** |
| **H02 — Separate Structured Grounding Diagnostics (`D1`, `D2`)** | All `100` sentences (`G01`–`G50` + `U01`–`U50`) | **100** | **Unseen (`0/100`)** | Published CGEL/B–R rule mappings + SynTutor XAI provenance fields (reported separately for Arm A; never penalizes Arm B) | **Yes** |

---

## 2. Which Measurements Can Be Scored Objectively

### H01 (Four Separated Measurements — Never Conflated)
1. **Track 1 — Full-Tree Structural Accuracy (`216 + 1`, disclosed dev-exposed):** Labeled/Unlabeled PARSEVAL F1, Exact Match, and All-Attempts F1 (unresolved/mismatched items kept as `0` matches), reporting zero-triangle complete trees, full all-attempts F1, and triangle-aware masked F1 side by side under character-offset and strict token alignment.
2. **Track 2 — Unseen Published-Reference Partial Relations (`16` unseen items):** Strictly limited to the exact structural checks implemented in `score_h01_partial()`: subject/predicate/complement spans + V-complement sisterhood (`G01`–`G06`), S-adverbial parent attachment (`G16`), V-complement vs. nested VP-adjunct sisterhood (`G17`), wh/C fronting (`G25`), NP-internal relative containment (`G26`), overt `to`-infinitival boundary (`G27`), and published ACA overt clause spans & nesting (`G36`–`G40`). Every item explicitly records `checked_relations` and `not_checked_relations` (unprinted internal subtrees, covert traces/controllers, lexical subcategory tags) and carries an explicit `scope_disclaimer` preventing misreporting as complete tree accuracy.
3. **Track 3 — Unseen B–R Rule Compliance (`50` unseen items):** Deterministic B–R Ch. 1–10 structural invariants (canonical label set only, zero leaked raw Penn tags, valid `S`/`S'` root, `NP`/`NOM` structure, interrogative `S'`/`C` fronting, non-empty yield).
4. **Track 4 — Unseen Benepar→B–R Conversion Consistency (`50` unseen items):** Canonical resolution rate (`normalized`), JSON schema validity, character-yield preservation, and deterministic repeatability.

### H02 — Fair Outcome-Only Primary Comparison (`N = 100`, Symmetrical Across Arm A & Arm B)
Both Arm A and Arm B are scored on **four outcomes both arms can legitimately achieve** (never using exact prose wording and never penalizing Arm B for lacking `C-*`/`CLS-*` rule IDs):
- **O1 — Correct Grammatical Judgment:** Exact match against textbook grammaticality (`G01`–`G50` = `grammatical`, `U01`–`U50` = `ungrammatical`). **Abstentions (`unverified`/`unresolved`) are strictly excluded from successful error detection** and reported in a dedicated breakdown (`overall_abstention_rate`, `grammatical_abstention_rate`, `ungrammatical_abstention_rate`, `ungrammatical_error_detection_rate`, `grammatical_false_positive_rate`).
- **O2 — Exact Position-Aware Error Localization:** On `U01`–`U50`, emitted `(start, end)` character spans must intersect the exact resolved character span(s) of pre-registered `Affected words` (all `50/50` CSV target spans statically verified). Wrong occurrences of repeated words and overly broad whole-sentence spans (`>65%` of sentence when target `≤45%`) are rejected. On `G01`–`G50`, zero spurious spans.
- **O3 — Valid Correction:** On `U01`–`U50`, normalized emitted correction matches `Expected correction` OR any pre-registered `Valid alternatives`; on `G01`–`G50`, zero erroneous rewrites.
- **O4 — Absence of Demonstrably Incorrect or Unsupported Feedback (Primary H02 Endpoints):** Reported side by side as **`O4_no_incorrect_or_unsupported`** (zero demonstrable falsehoods/contradictions) AND **`O4_decided_clean`** (`O4` AND `not abstained`, preventing abstention-gaming).
- **Primary Paired Composite (`0–4`):** `O1 + O2 + O3 + O4_decided_clean`.

### H02 — Separate Grounding Diagnostics (Reported Independently)
- **D1 — Structured Rule Application Accuracy (Arm A descriptive):** Whether fired rule IDs (`C-*`, `CLS-*`, `COMP-*`, `PHR-*`, `MORPH-*`, `OTH-*`, `WCAT-*`) map to the pre-registered textbook rule family (`U01`–`U50`) and stay silent on `G01`–`G50`.
- **D2 — Structured Evidence & Provenance Integrity (Arm A descriptive):** Valid tree/token anchors, channel-valid B–R/Cambridge provenance, and fail-closed `NO_BOOK_BASIS` integrity.

---

## 3. Which Sentences Lack Sufficient Published Structural Answers

- **H01 (`34 / 50` unseen grammatical items without printed B–R tree/bracket answers):** `15` B–R *Further Exercises* (`G07`–`G08`, `G18`–`G24`, `G41`–`G46`; separate *Answer Book* not in PDF), `1` B–R in-text example (`G28`), and `18` CGEL grammatical originals (`G09`–`G15`, `G29`–`G35`, `G47`–`G50`). **Zero gold trees are invented for these 34 items**; they are scored on H01 Tracks 3–4 (compliance & conversion) and full H02 grammatical-control metrics only.
- **H02 (`0 / 100` lacking reference answers):** All `100` sentences have verified CGEL/B–R grammaticality, span, rule, and correction keys.

---

## 4. Functioning Grounded vs. Ungrounded Comparison System & Statistical Plan

- **Arm A (Rule-Grounded SynTutor):** Unmodified `analysis_api.build_payload(sentence, variety="standard_english")`.
- **Arm B (Ungrounded Neural/Perturbation Baseline — Verified Functioning):** Uses SynTutor's **exact same locally cached neural models** (`textattack/roberta-base-CoLA` via `detector.classify` + `distilbert-base-uncased` via `corrector.sweep`) with **native, unthrottled CoLA classification** (`acceptable == True/False`, avoiding the `0.20` advisory tolerance `_FLAG_TOLERANCE` that applies only when rules are active) and **DistilBERT MLM perturbation localization + correction** whenever CoLA flags a sentence unacceptable.
  - **Smoke-tested offline on separate synthetic fixtures (not in the 100-sentence CSV):** On `"The dog chased the cat."`, Arm B returns `grammatical` (`p = 0.97`, zero errors). On `"The dog chase the cat."`, Arm B returns `ungrammatical` (`p = 0.35`), localizes `'dog'` → `'dogs'`, and generates the valid correction `"The dogs chase the cat."` (`p = 0.96`). Arm B is verified as a genuinely functioning ungrounded system rather than an artificially crippled baseline.
- **Justified Statistical Tests ($\alpha = 0.05$, two-sided):**
  - **H01:** Wilson 95% CIs (binary), 10,000-resample BCa bootstrap 95% CIs (F1), Kruskal–Wallis $H$ + Jonckheere–Terpstra trend test across Simple/Moderate/Complex strata, and Fisher–Freeman–Halton exact test on binary stratum rates.
  - **H02 (`N = 100` paired):** Exact two-sided **McNemar test** on `O4` (primary), `O1`, `O2`, `O3`, and `O1&O2&O3` (`83.7%`–`96.1%` power for `+15` to `+20` pp net improvement), plus **paired Wilcoxon signed-rank test** on the `0–4` Fair Outcome Composite Score (`O1+O2+O3+O4`), with Holm–Bonferroni correction on secondary endpoints and Grammatical / Ungrammatical / Minimal-Pair (`P01`–`P19`) breakdowns.

---

## 5. Remaining Limitations

1. **H01 Unseen Complete Trees:** Without the separate 3rd-edition *Answer Book*, full-tree PARSEVAL (`Track 1`) is dev-exposed (`216+1` book diagrams), while unseen structural ground truth covers `16` partial-reference items (`Track 2`). Partial agreement and conversion consistency must never be reported as unseen full-tree accuracy.
2. **H02 Comparison Scope:** Arm A vs. Arm B proves whether SynTutor's structured linguistic rules improve objective grammaticality, localization, correction, and error-free feedback over SynTutor's own ungrounded neural acceptability/MLM perturbation components; it **does not** prove superiority over external LLMs.
3. **Free-Text Explanation Qualities Requiring Human Judgment:** Automated scoring cannot verify natural-language pedagogical clarity/readability, subtle semantic misstatements inside free-text prose carrying a valid rule ID, or unlisted valid paraphrases (all non-matching correction strings are exported to `non_matching_corrections_audit.csv` for lightweight author/adviser inspection).
4. **Cambridge Governance Waiver:** All `193` runtime-enabled Cambridge rules carry `owner_waiver: true, independent_review: false` and must be disclosed in Chapter IV.
5. **Power Boundaries:** Small H01 binary stratum differences (`n = 15/20/15`, `n = 6/5/5`) and small H02 effects (`≤ 10` pp) are underpowered.

---

## 6. Exact Verified Commands for Final Execution (Do Not Run Until Approved)

Both read-only evaluation scripts are now implemented and verified:

1. **Verify the runner & scoring logic on separate synthetic fixtures (safe to run anytime; does NOT touch the 100 evaluation sentences):**
   ```sh
   export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONDONTWRITEBYTECODE=1
   .venv/bin/python -m unittest -v docs/audits/technical_evaluation/test_run_textbook_h01_h02.py
   ```
2. **Execute H01 Track 1 (Published Full-Tree & Triangle-Aware PARSEVAL on `216` + `[79b]`, zero-lookup sentinel enforced):**
   ```sh
   export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONDONTWRITEBYTECODE=1
   .venv/bin/python docs/audits/technical_evaluation/run_hypothesis_checks.py h01 /tmp/syntutor-final-eval/h01-published-book
   ```
3. **Execute H01 Tracks 2–4 & H02 Arm A vs. Arm B on the 100 Unseen Textbook Sentences (zero-lookup sentinel enforced):**
   ```sh
   export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONDONTWRITEBYTECODE=1
   .venv/bin/python docs/audits/technical_evaluation/run_textbook_h01_h02.py \
     docs/audits/h01_h02_evaluation_methodology/H01_H02_PROPOSED_100_SENTENCES.csv \
     /tmp/syntutor-final-eval/textbook-100
   ```
4. **Record Provenance After Execution:** Archive `git rev-parse HEAD`, environment versions, and `shasum -a 256` of `/tmp/syntutor-final-eval/textbook-100/*` before reporting results in Chapter IV.
