# H01 and H02 Frozen Final Evaluation Results Report

**Project:** SynTutor: An Explainable AI-Based Framework for Syntax Tree-Driven Grammar Analysis and Learning Using NLP  
**Execution Date:** 2026-11-22  
**Branch / Evaluated Commit:** `fix/syntutor-system-reliability-xai` (`65ba545` + frozen evaluation harness; **zero modifications to SynTutor production code, models, grammar rules, or thesis manuscript**)  
**Execution Mode:** Single frozen offline run (`HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`), zero tuning against the 100 evaluation sentences, **gold-tree lookup sentinel verified `0` calls** in H01 Tracks 1–4 and `[]` in H02 Arm A.

---

## 1. Pre-Execution Integrity Verification

All three frozen SHA-256 checksums matched byte-for-byte before execution:

| Artifact | Verified SHA-256 |
| :--- | :--- |
| `docs/audits/h01_h02_evaluation_methodology/H01_H02_PROPOSED_100_SENTENCES.csv` | `ce3020a0cd28796c5ffe71bf0772c66773d3b1154323c823df8ccc3a22e065d6` |
| `docs/audits/technical_evaluation/run_textbook_h01_h02.py` | `3815ad1b74647dddaf9dea651a9914b670a375dccc195bd3f2b85f26c3634910` |
| `docs/audits/technical_evaluation/test_run_textbook_h01_h02.py` | `0b8f1cbf4c9bfa0cad0cb3d508d8a604071bc8fad2a7a8275ae8852a2c680368` |

Preserved raw evaluation artifacts and checksums (also archived in `/tmp/syntutor-final-eval/ARTIFACTS.sha256`):

| Raw Output Artifact | SHA-256 |
| :--- | :--- |
| `/tmp/syntutor-final-eval/h01-published-book/h01.json` | `8c3dc0088ee8b92338a150f4d1919f2e04027491a34fc6b0386628cb83ed45e6` |
| `/tmp/syntutor-final-eval/h01-published-book/h01-source-figure-79b.json` | `aeed26450f0acc6ae505f1165b5376a00aaf4aa7443b693637272afae3d5c0db` |
| `/tmp/syntutor-final-eval/textbook-100/summary.json` | `e8da46eed614caae246900655884f00b7b345a4d484e11bc06dd2fb05b4db2ec` |
| `/tmp/syntutor-final-eval/textbook-100/h01_details.json` | `c988517c9915bbbcb0844b995ea34e078a2c41d96016120d055cb31e627e15d8` |
| `/tmp/syntutor-final-eval/textbook-100/h02_details.json` | `440d72a0bdb0ba8ff20e73c19f3318b5e77018487301c74fbd560a25ef2eef21` |
| `/tmp/syntutor-final-eval/textbook-100/non_matching_corrections_audit.csv` | `65b1674ed58f11c475c77aab558a686d43da95ae382da9e28ce00a26c05d8310` |
| `/tmp/syntutor-final-eval/textbook-100/complete_statistical_analysis.json` | *(generated post-run from the above frozen JSONs)* |

---

## 2. H01 Results — Burton–Roberts Syntax-Tree Pipeline (Four Separated Tracks)

### 2.1 Track 1 — Published Full-Tree & Triangle-Aware PARSEVAL (`216 + 1`, Disclosed Dev-Exposed)

| Subset / View | `n` | Normalized | Yield-Aligned | Exact Match (Wilson 95% CI) | Micro All-Attempts F1 | Macro All-Attempts F1 (10k Boot 95% CI) |
| :--- | ---: | ---: | ---: | :--- | ---: | :--- |
| **Overall (`216` active book diagrams)** | 216 | 213 (`98.61%`) | 204 (`94.44%`) | `37/216 = 17.13%` (`[12.69%, 22.72%]`) | **`62.96%`** | `65.56%` (`[61.07%, 70.03%]`, med `76.92%`) |
| — Aligned Full Labeled / Unlabeled F1 | 204 | 204 | 204 | `37/204 = 18.14%` | `67.00%` / `71.53%` | — |
| — **Triangle-Aware Masked (Aligned)** | 204 | 204 | 204 | `112/216 = 51.85%` (`54.90%` aligned) | **`83.35%`** (`88.98%` unlab.) | — |
| — **Zero-Triangle Complete Diagrams Only** | 71 | 71 (`100%`) | 71 (`100%`) | `29/71 = 40.85%` (`[30.17%, 52.46%]`) | `69.04%` | `68.97%` (`[59.39%, 77.94%]`, med `91.67%`) |
| — Triangle-Abbreviated Diagrams Only | 145 | 142 (`97.93%`) | 133 (`91.72%`) | `8/145 = 5.52%` (`[2.82%, 10.51%]`) | `61.30%` | `63.89%` (`[59.07%, 68.44%]`, med `72.73%`) |
| — Sentence-Rooted Only (`S`/`Sentence`) | 106 | 104 (`98.11%`) | 99 (`93.40%`) | `3/106 = 2.83%` | `58.48%` | — |
| **Non-Imported Figure `[79b]` (Ch. 10 p. 239)** | 1 | 1 (`normalized`) | `8/8` lex-char | `1/1` (`100%` exposed spans) | `100.0%` *(exposed)* | — |

**Track 1 Complexity Breakdown (by Explicit Clause Count in Published Gold Tree):**
- `0` clauses (`n=83`): micro F1 **`64.83%`**, macro F1 `65.80%` (`[57.72%, 74.00%]`), exact `26/83 = 31.33%`.
- `1` clause (`n=90`): micro F1 **`68.81%`**, macro F1 `70.10%` (`[64.60%, 75.40%]`), exact `10/90 = 11.11%`.
- `2+` clauses (`n=43`): micro F1 **`53.31%`**, macro F1 `55.60%` (`[44.78%, 65.71%]`), exact `1/43 = 2.33%`.
- **Inferential tests across complexity:** Kruskal–Wallis `H = 4.9281, df = 2, p = 0.0851`; **Jonckheere–Terpstra `z = -2.1541, p = 0.0312`** (statistically significant monotonic F1 decrease with complexity); **Fisher–Freeman–Halton exact match `p = 0.000022`**.

### 2.2 Tracks 2–4 — Unseen 50 Grammatical Textbook Sentences (`G01`–`G50`, `0/50` Dev-Exposed)

| Track (Scope Strictly Limited as Labeled) | Overall (`n`) | Simple | Moderate | Complex | Complexity Tests |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Track 2 — Unseen Published Partial Relations** *(NOT complete-tree accuracy)* | **Relations:** `47/60 = 78.33%` (`[66.38%, 86.88%]`)<br>**All-passed items:** `7/16 = 43.75%` (`[23.10%, 66.82%]`)<br>**Mean item rate:** `77.71%` (`[63.12%, 89.90%]`) | `n=6`: all-passed `4/6` (`66.67%`), mean `93.06%` (`[84.72%, 100%]`) | `n=5`: all-passed `1/5` (`20.00%`), mean `65.33%` (`[32.00%, 89.33%]`) | `n=5`: all-passed `2/5` (`40.00%`), mean `71.67%` (`[48.33%, 95.00%]`) | KW `H=3.149, p=0.2071`<br>JT `z=-1.512, p=0.1306`<br>FFH `p=0.3881` |
| **Track 3 — Unseen B–R Rule Compliance** *(NOT gold-tree accuracy)* | **`45/50 = 90.00%`** (`[78.64%, 95.65%]`) | `15/15` (`100.0%`, `[79.61%, 100%]`) | `19/20` (`95.0%`, `[76.39%, 99.11%]`) | `11/15` (`73.33%`, `[48.05%, 89.10%]`) | **KW `H=6.715, p=0.0348`**<br>**JT `z=-2.410, p=0.0160`**<br>FFH `p=0.0552` |
| **Track 4 — Unseen Benepar→B–R Conversion Consistency** *(NOT gold-tree accuracy)* | **`45/50 = 90.00%`** (`[78.64%, 95.65%]`) | `15/15` (`100.0%`, `[79.61%, 100%]`) | `19/20` (`95.0%`, `[76.39%, 99.11%]`) | `11/15` (`73.33%`, `[48.05%, 89.10%]`) | FFH `p=0.0552` |

- **Unresolved items in Tracks 3–4 (`5/50`):** `G25` (Moderate wh-question), `G43`–`G45` (Complex long-distance wh-extraction), and `G50` (Complex coordinated infinitival subject). Every normalized tree (`45/45`) passed 100% of deterministic B–R compliance checks with zero leaked Penn tags.
- **Specific Track 2 partial-relation failures (`9/16` items):** `G05` (`v_sister:applied+for a gun licence`), `G06` (`v_sister:dyed+deep purple`), `G16` (`parent:in my opinion` not attached to `S`), `G17` (`v_sister:worry+about exams`), `G25` (unresolved canonical tree), `G26` (`relative_clause` span/label), `G36` (`s2_wh_interrog`), `G37` (`s2_subject_clause`, `s3_noun_comp`), `G38` (`s2_nonrestr_rel`). Full-pass items (`7/16`): `G01`–`G04`, `G27`, `G39`, `G40`.

---

## 3. H02 Results — Fair Outcome-Based Comparison (`N = 100` Unseen Textbook Sentences)

### 3.1 Primary Symmetrical Comparison: Arm A (Rule-Grounded SynTutor) vs. Arm B (Ungrounded CoLA + DistilBERT MLM)

| Outcome Metric (`N = 100` paired) | Arm A (Rule-Grounded) | Arm B (Ungrounded Neural) | Net Diff (A − B) | Discordant Wins (A : B) | Odds Ratio | Exact Two-Sided McNemar `p` | Holm–Bonferroni `p` |
| :--- | ---: | ---: | ---: | :---: | ---: | ---: | ---: |
| **`O4_no_incorrect_or_unsupported` (Primary)** | **`79.0%`** (`79/100`) | `71.0%` (`71/100`) | `+8.0` pp | `17 : 9` | `1.89` | `0.168638` | *(primary)* |
| **`O4_decided_clean` (Non-Abstaining Primary)** | **`72.0%`** (`72/100`) | `71.0%` (`71/100`) | `+1.0` pp | `16 : 15` | `1.07` | `1.000000` | *(co-primary)* |
| **`O1` — Correct Grammatical Judgment** | `75.0%` (`75/100`) | `72.0%` (`72/100`) | `+3.0` pp | `15 : 12` | `1.25` | `0.701108` | `0.701108` |
| **`O2` — Exact-Position Target Localization** | **`73.0%`** (`73/100`) | `50.0%` (`50/100`) | **`+23.0` pp** | **`28 : 5`** | **`5.60`** | **`0.000066`** | **`0.000264`** |
| **`O3` — Valid Correction** | **`62.0%`** (`62/100`) | `49.0%` (`49/100`) | **`+13.0` pp** | **`16 : 3`** | **`5.33`** | **`0.004425`** | **`0.013275`** |
| **Full Outcome Adequacy (`O1 & O2 & O3 & O4`)** | `58.0%` (`58/100`) | `49.0%` (`49/100`) | `+9.0` pp | `14 : 5` | `2.80` | `0.063568` | `0.127136` |
| **Fair Outcome Composite (`0–4`, Paired Wilcoxon)** | Mean **`2.82`** (`[2.49, 3.14]`), Med `4.0` | Mean `2.42` (`[2.08, 2.74]`), Med `2.0` | **`+0.40`** | `W+ = 653, W- = 293` (`43` nonzero) | `r = 0.3805` | **`p = 0.028595`** | *(ordinal primary)* |

### 3.2 Abstention vs. Error Detection & Subgroup Breakdown (Reported Separately)

| Subgroup / Diagnostic Rate | Arm A (Rule-Grounded) | Arm B (Ungrounded Neural) | Exact McNemar `p` |
| :--- | :--- | :--- | ---: |
| **Overall Abstention Rate (`N = 100`)** | **`7.0%`** (`7/100`, `[3.43%, 13.75%]`) | **`0.0%`** (`0/100`, `[0.0%, 3.70%]`) | — |
| **Grammatical (`n = 50`): Acceptance (`O1`)** | `90.0%` (`45/50`, `[78.64%, 95.65%]`) | `96.0%` (`48/50`, `[86.54%, 98.90%]`) | `0.3750` |
| **Grammatical (`n = 50`): False-Positive Rate** | `8.0%` (`4/50`, `[3.15%, 18.84%]`) | `4.0%` (`2/50`, `[1.10%, 13.46%]`) | `0.6875` *(O4)* |
| **Grammatical (`n = 50`): Abstention Rate** | `2.0%` (`1/50`) | `0.0%` (`0/50`) | — |
| **Ungrammatical (`n = 50`): Error Detection (`O1`, excl. abstentions)** | `60.0%` (`30/50`, `[46.18%, 72.39%]`) | `48.0%` (`24/50`, `[34.80%, 61.49%]`) | `0.2863` |
| **Ungrammatical (`n = 50`): Abstention Rate** | `12.0%` (`6/50`, `[5.62%, 23.80%]`) | `0.0%` (`0/50`) | — |
| **Ungrammatical (`n = 50`): Missed as Grammatical** | `28.0%` (`14/50`) | `52.0%` (`26/50`) | — |
| **Ungrammatical (`n = 50`): Target Localization (`O2`)** | **`54.0%`** (`27/50`, `[40.40%, 67.03%]`) | `4.0%` (`2/50`, `[1.10%, 13.46%]`) | **`< 0.000001`** (`26:1`, OR `26.0`) |
| **Ungrammatical (`n = 50`): Valid Correction (`O3`)** | **`28.0%`** (`14/50`, `[17.47%, 41.67%]`) | `2.0%` (`1/50`, `[0.35%, 10.50%]`) | **`0.000977`** (`14:1`, OR `14.0`) |
| **Ungrammatical (`n = 50`): Clean `O4` (No Incorrect Feedback)** | **`66.0%`** (`33/50`) | `46.0%` (`23/50`) | **`0.041389`** (`15:5`, OR `3.0`) |
| **Minimal Pairs (`19` pairs `P01`–`P19`): Both `O1` Correct** | `52.63%` (`10/19`) | `57.89%` (`11/19`) | `1.0000` (`3:4`) |

- **Failure Modes (`N = 100`):** Arm A had `0` self-contradictions, `0` overly broad spans, `4` grammatical FPs, `14` ungrammatical misses, `7` wrong-target localizations, and `2` invalid rewrites (`0` uncatalogued non-matching corrections). Arm B had `0` self-contradictions, `2` grammatical FPs, `26` ungrammatical misses, `2` wrong-target localizations, and `3` invalid rewrites (`1` non-matching correction on `U46`: *"This is the letter drawing our attention to the problem."* — participle rewrite rather than relative-clause restoration).

### 3.3 Separate Arm A Grounding Diagnostics (Reported Independently; Never Penalized Arm B)
- **`D1` — Structured Rule-Family Match (`N = 100`):** `69/100 = 69.00%` (`[59.37%, 77.22%]`).
- **`D2` — Structured Evidence & Provenance Integrity (`N = 100`):** `100/100 = 100.0%` (`[96.30%, 100.0%]`).

---

## 4. Synthesis: What Supports H01/H02 vs. What Does Not

### H01 Verdict Summary
- **Supports H01:** High canonical conversion (`98.61%` on book diagrams, `90.0%` on unseen sentences, `100%` on unseen Simple), strong triangle-aware labeled F1 (`83.35%`) and unlabeled F1 (`88.98%`) on published book diagrams, `8/8` exact exposed spans on Figure `[79b]`, `78.33%` (`47/60`) unseen published partial-relation satisfaction (`93.06%` on unseen Simple), and `100%` deterministic B–R compliance on all `45/45` normalized unseen trees.
- **Does NOT Support H01:** Full-tree all-attempts labeled F1 on Track 1 is `62.96%` (`17.13%` strict exact match), and **accuracy degrades significantly as syntactic complexity increases** — Track 1 Jonckheere–Terpstra `p = 0.0312` (`68.81%` → `53.31%`), Track 1 exact match FFH `p = 0.000022`, and Track 3 unseen compliance KW `p = 0.0348` / JT `p = 0.0160` (`100%` Simple → `73.33%` Complex, with all `5` unresolved canonical trees occurring in wh-extraction and coordinated non-finite subjects). Only `7/16` (`43.75%`) unseen partial-reference items passed every checked relation.

### H02 Verdict Summary
- **Supports H02:** Rule-grounded SynTutor (Arm A) achieves **statistically significant, large gains** over the functioning ungrounded neural/perturbation baseline (Arm B) on **exact-position error localization** (`73%` vs. `50%` overall, Holm `p = 0.000264`; `54%` vs. `4%` on ungrammatical items, `p < 0.000001`), **valid corrections** (`62%` vs. `49%` overall, Holm `p = 0.013275`; `28%` vs. `2%` on ungrammatical items, `p = 0.000977`), **overall fair outcome composite score** (`2.82` vs. `2.42`, paired Wilcoxon `p = 0.0286`, `r = 0.38`), and **ungrammatical clean-feedback rate `O4`** (`66%` vs. `46%`, `p = 0.0414`), while maintaining `100%` structured provenance integrity (`D2`) and `0` contradictions.
- **Does NOT Support H02:** On the **overall `N = 100` primary binary McNemar endpoints**, neither `O4_no_incorrect_or_unsupported` (`79%` vs. `71%`, `p = 0.1686`) nor `O4_decided_clean` (`72%` vs. `71%`, `p = 1.000`) nor binary judgment `O1` (`75%` vs. `72%`, `p = 0.7011`) reached statistical significance at $\alpha = 0.05$. Arm A traded slightly higher grammatical false positives (`8%` vs. `4%`) and `7%` abstentions for much stronger localization and repair, yet still missed `28%` (`14/50`) of unseen ungrammatical CGEL sentences as grammatical and produced valid corrections on only `28%` (`14/50`).

---

## 5. Limitations

1. **No Unseen Complete Printed B–R Trees:** Full-tree PARSEVAL (`Track 1`) is dev-exposed (`216+1`), while unseen structural verification covers `16` partial-reference items (`Track 2`, explicitly limited to checked relations) and `34` items have no published tree (evaluated on compliance/conversion only).
2. **Comparison Scope:** Arm A vs. Arm B isolates SynTutor's structured linguistic rules against SynTutor's own ungrounded RoBERTa-CoLA + DistilBERT MLM components; it does not benchmark external instruction-tuned LLMs.
3. **Free-Text Prose Quality:** Automated scoring does not verify human-perceived pedagogical clarity, learner readability, or subtle prose misstatements inside explanations that carry valid rule IDs.
4. **Governance & Statistical Power:** SynTutor's `193` runtime Cambridge rules operate under `owner_waiver: true, independent_review: false`; `N = 100` was underpowered for the observed `+8` pp overall `O4` difference (`p = 0.1686`), and Track 2 (`n = 16`) was underpowered for between-stratum differences.
