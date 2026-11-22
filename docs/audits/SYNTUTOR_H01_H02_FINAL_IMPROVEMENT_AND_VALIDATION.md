# SynTutor — Comprehensive H01/H02 Accuracy, Reliability, and Validation Report

## 1. Branch, Commit, and Working-Tree Identity

- **Repository:** `SynTutor`
- **Branch:** `fix/syntutor-system-reliability-xai`
- **Current `HEAD` commit:** `f9470d4e359efda1b85d0988157163230fb91a1e` (previous H01/H02 sprint commit on top of `73c555cf8261771eecdcabb15925f093884040ca`)
- **Working-tree state:** Uncommitted local changes only (`6` tracked files modified: `+461 / -64`; `1` new standalone comparator script `docs/audits/technical_evaluation/run_h02_grounding_comparator.py`; `1` new report file). No commits, pushes, merges, rebases, or manuscript edits were performed. All frozen evaluation scripts (`run_hypothesis_checks.py`, `run_phase2_external.py`, `run_real_world_reliability.py`, `run_technical_evaluation.py`), frozen manifests (SHA-256 `0a0322368b646873a1b42f77571d27259a2e664a1c20b09aa831afd98d1b4672`), and blank human worksheets remain unmodified.
- **Runtime environment:** `.venv` (Python 3.11.17, spaCy 3.8.16, `en_core_web_md` 3.8.0, Benepar `benepar_en3`, Transformers 4.46.3, `textattack/roberta-base-CoLA`, offline MLM corrector, ERRANT 3.0.0).

---

## 2. Verified Baseline Measurements

Both the pre-sprint baseline (`73c555cf`) and the prior-sprint `HEAD` baseline (`f9470d4e`) were verified using the unmodified `docs/audits/technical_evaluation/run_hypothesis_checks.py` runner on identical inputs:

- **H01 (`216` Burton–Roberts textbook references, zero textbook lookup verified via lookup sentinel):**
  - `73c555cf`: `201/216` (`93.06%`) normalized, `186/216` (`86.11%`) terminal-aligned, `59.53%` all-attempt full labeled F1 (`903` matches), `68.46%` aligned full labeled F1, `84.31%` aligned triangle-aware F1, `32/216` full exact, `101/216` triangle-aware exact, `51.76%` all-attempt F1 on `2+` explicit clauses.
  - `f9470d4e`: `210/216` (`97.22%`) normalized, `201/216` (`93.06%`) terminal-aligned, `62.20%` all-attempt full labeled F1 (`966` matches), `66.76%` aligned full labeled F1, `82.81%` aligned triangle-aware F1, `36/216` full exact, `109/216` triangle-aware exact, `52.48%` all-attempt F1 on `2+` explicit clauses; Figure `[79b]` normalized and `8/8` exact.
- **H02 (`405` paired external inputs: BLiMP `116`, W&I+LOCNESS `120` [`193` edits], EXPECT `169` [`205` evidence tokens]):**
  - `73c555cf`: BLiMP ON `85/116` (`73.28%`, `8` FP, `7` FN), OFF `85/116` (`8` FP, `8` FN); W&I Matrix ON `TP=5, FP=6, FN=188, Prec=0.4545, Rec=0.0259, F0.5=0.1055`; EXPECT ON `TP=6, FP=4, FN=199, Prec=0.6000, Rec=0.0293, F1=0.0558` (`16` anchored).
  - `f9470d4e`: BLiMP ON `88/116` (`75.86%`, `3` FP, `7` FN), OFF `88/116` (`3` FP, `8` FN); W&I Matrix ON `TP=5, FP=7, FN=188, Prec=0.4167, Rec=0.0259, F0.5=0.1037`; EXPECT ON `TP=6, FP=3, FN=199, Prec=0.6667, Rec=0.0293, F1=0.0561` (`15` anchored); `"invent new stuff"` false explanation resolved.

---

## 3. Prioritized Root Causes and Linguistic References

### H01 — Complete Benepar → Burton–Roberts (`FINAL-D1`) Pipeline

1. **Restrictive Relative Clause Attachment & `that`-Relative `C2` Position (Burton–Roberts, *Analysing Sentences*, 3rd ed., Ch. 9 `[39]`, `[53a]`, `[59]`):** A premature `(NP (NP ...) (SBAR ...))` short-circuit in `final_d1_projection.py` attached restrictive relative clauses at `NP` level (`NP → NP + S-dbar`, which is reserved for comma-delimited non-restrictive relatives) instead of inside `NOM` (`NP → DET + NOM(NOM + S-dbar)`), and placed `that` in `C1` rather than `C2` (`S-dbar → C2(that) + S-bar(C1[], S)`) on gapped `that`-relatives.
2. **Non-Finite `wh`-Infinitive Gap Binding & `to` Position (B–R Ch. 10 `[37]`):** In `wh_gap()` / `wh_clause()`, `how many guests to expect` misclassified the infinitival `S(VP(TO to, VP))` as a subject-gap finite clause and inverted `to` into `C1`, whereas B–R keeps `to` as `AUX[-tense]` inside `VP` with covert subject `PRO` and binds the fronted `WHNP` to the object gap.
3. **Remaining Unresolved Unambiguous Constructions (B–R Ch. 8–9):** Three unambiguous textbook patterns remained unresolved (`ch8-disc2` expletive `it` zero-`that` extraposition parsed as `VP(VP, NP, VP)`, `ch8-ex2-b` wrapped zero-`that` `SBAR(S)` + adverbial `SBAR(because ...)`, and `ch9-11a` echo wh-in-situ `taking (SBAR (WHNP what) (PP to Athens))`), alongside a `SQ(VP)` subject-gap regression on `"Whose is this?"`. Three genuinely ambiguous B–R 3rd ed. cases (`ch4-52b` `find NP NP` ditransitive vs. object-predicative; `ch8-67c` & `ch8-ex2-f` temporal-`P` vs. causal-`C` `since`) were intentionally preserved as unresolved.
4. **Structural Ceiling on Full-Tree F1 Over the 216 Textbook Diagrams (Quantified):** Of `826` unmatched predicted constituents in the `f9470d4e` baseline, **`561` (`67.9%`) sit strictly inside textbook collapsed triangles** (`ch1`–`ch10`), `~52` gold spans use Ch. 1–2 pedagogical placeholder labels (`PHRASE`/`Phrase`), and `47` gold-only `S` spans come from Ch. 8 abbreviated clause-outline triangle diagrams (`ch8-4a`, `ch8-10a`, `ch8-ex1-a`). Even a 100% exact expanded `FINAL-D1` parser cannot exceed `~81%` full F1 without collapsing triangles or replacing `NP`/`NOM` with `PHRASE`—neither of which is linguistically valid.

### H02 — Linguistic Constraint Matrix, Cambridge Rules, Corrections, and XAI Grounding

1. **False `unverified` Downgrades in Lexical Licensing & Fragment Misparses:** `licensing.py` downgraded grammatical sentences with `p(CoLA) > 0.74` to `unverified` on nominalized adjectives after `the` (`in the open`) and Benepar `VBD`-mistagged present verbs after long relative clauses (`those skirts that annoyed Kayla stun Dan`). `matrix.py` falsely condemned Benepar-misparsed plural subject + intransitive verb (`A lot of pants fray.`) as `C-TENSE-FINITE`.
2. **High-Impact Missing / Incomplete General Syntactic Rules (Cambridge CGEL / Binding Theory / Island & Valency Constraints):**
   - **Binding Principle A finite-clause domain (`C-REFLEXIVE-ANTECEDENT`):** Missing male names (`Jesus`, etc.) and inanimate local-subject mismatch (`some screen ... himself`).
   - **NPI `ever` Licensing (`C-NPI-LICENSING`):** Proportional quantifier `most` (upward-entailing, unlike definite superlative `the most`) was listed in `_NPI_DIRECT_LICENSORS`, failing to flag `*Most legislatures that only some spotlights stun might ever collaborate.`
   - **Verb Valency & Passive Small Clauses:** `talk` missing from `_STRICTLY_INTRANSITIVE_VERBS` (fixing both `C-INTRANSITIVE-OBJECT` on `*talked Brenda` and `C-FILLED-GAP` on `*who those museums talk about waiters`); `take`/`cure` missing from `_OBLIGATORILY_TRANSITIVE_VERBS` (`*These icicles took.`, `*investigating that that boy had cured.`); passive `VBN` + direct NP object in reflexive small clauses (`*imagine themselves referenced a lot of teachers`).
   - **Island & Tough-Movement Constraints:** `C-LEFT-BRANCH-ISLAND` skipped bare singular NP objects under ditransitive-listed verbs (`*Which is Samuel passing high school?`); `C-COORD-ISLAND` missed Benepar's `VP(VB, NP(... CC ...), VP(stranded PP))` parse (`*What did Beverly disgust cashiers and Carla listen to?`); `C-TOUGH-COMPLEMENT` missed sibling `S` under `VP` and stacked infinitives (`*Some library was enjoyable to order this student to escape.`).
3. **Learner Correction, Localization, and Context-Sensitive Article Accuracy:**
   - **Context-sensitive `C-ARTICLE`:** Removed `'change'` and `'manipulation'` from unconditional `NONCOUNT_NOUNS` into context-evaluated `DUAL_COUNT_MASS_NOUNS` (exempting bare generic, mass-quantified, and domain-classified uses like `"little change"` / `"genetic manipulation"`, while flagging countable uses like `"This is big change."`).
   - **Coordinated VP SVA remediation (`_rem_agreement`):** Fixed no-op edit targeting the first agreeing verb (`owns → owns`) instead of the disagreeing conjunct (`use → uses`).
   - **Infinitival `to` + irregular past/participle (`C-TO-BASE`), relative SVA (`C-RELATIVE-AGREE`), missing possessive apostrophe (`C-POSSESSIVE-S`), and `C-DETERMINER-AGREEMENT` target alignment:** Added irregular non-base morphology + repair edits (`to lent → to lend`), added `C-RELATIVE-AGREE` remediation edits (`want → wants`), extended `C-POSSESSIVE-S` to singular determiner + `-s` noun + noun (`a persons heritage`, `that nights news`) with evidence links, and aligned `a/an + plural` `target_token_ids` to the edited plural noun (`tubes` with `a` as related evidence).

---

## 4. Implementation Modifications

| File | Diff (vs. `f9470d4e`) | Purpose |
|---|---|---|
| [server/final_d1_projection.py](file:///Users/kiyel/Desktop/SynTutor/server/final_d1_projection.py) | `+62 / -14` | Restrictive relative attachment in `NOM`; `that`-relative `C2` placement; non-finite `wh`-infinitive `to` in `VP` + object-gap binding; `ch8-disc2`/`ch8-ex2-b`/`ch9-11a` projections; `SQ(VP)` guard for `"Whose is this?"`. |
| [server/licensing.py](file:///Users/kiyel/Desktop/SynTutor/server/licensing.py) | `+14 / -1` | Licensed nominalized adjectives after `the` and `VBD`-mistagged valid `VBP`/`VB` verbs; added remediation edits to `C-RELATIVE-AGREE`. |
| [server/matrix.py](file:///Users/kiyel/Desktop/SynTutor/server/matrix.py) | `+64 / -2` | Context-sensitive `DUAL_COUNT_MASS_NOUNS` (`change`, `manipulation`); coordinated-VP disagreeing-conjunct repair in `_rem_agreement`; plural-NP + intransitive-`VBP` mistag guard in `_root_level`. |
| [server/ruleset.py](file:///Users/kiyel/Desktop/SynTutor/server/ruleset.py) | `+244 / -22` | Binding Principle A inanimate/name coverage; `C-TO-BASE` irregular past/participle + edits; `most` removed from `_NPI_DIRECT_LICENSORS`; `talk`/`take`/`cure` valency; `C-COORD-ISLAND` Pattern 2; `C-LEFT-BRANCH-ISLAND` bare singular NP; `C-TOUGH-COMPLEMENT` sibling `S` & stacked infinitives; `C-PASSIVE` reflexive small clause `VBN + NP`; `C-POSSESSIVE-S` singular-det missing apostrophe + edits. |
| [server/findings.py](file:///Users/kiyel/Desktop/SynTutor/server/findings.py) | `+12 / -7` | Corroborated irregular `C-TO-BASE`; aligned `a/an + plural` `determiner_noun_agreement` target to the edited plural noun and added `'determiner_noun_agreement'` to participant-span matching. |
| [server/test_h01_h02_reliability.py](file:///Users/kiyel/Desktop/SynTutor/server/test_h01_h02_reliability.py) | `+79 / -4` | Expanded to 17 focused positive & negative regression test methods covering every H01 and H02 fix. |
| [docs/audits/technical_evaluation/run_h02_grounding_comparator.py](file:///Users/kiyel/Desktop/SynTutor/docs/audits/technical_evaluation/run_h02_grounding_comparator.py) | New (`290` lines) | Standalone whole-system Grounded vs. Ungrounded Neural comparator on the frozen 405-item manifest with exact paired McNemar tests, Wilson CIs, ERRANT, EXPECT, and blank blinded human worksheet generation. |

---

## 5. Focused Regression Results

- **Full 20-module unit & regression test suite:** **220/220 PASS** (`test_parser_runtime`, `test_burton_roberts` [including M1-envelope `217/217`], `test_br_final_d1_gold`, `test_br_final_d1_dispositions`, `test_br_tree`, `test_canonical_binding`, `test_xai_facts`, `test_findings`, `test_licensing`, `test_corrector`, `test_cross_layer_consistency`, `test_correction_completeness`, `test_learner_analysis`, `test_detection_scoping`, `test_nlp_reliability_regressions` [29/29], `test_relative_pronoun`, `test_cambridge_registry`, `test_cambridge_evaluator`, `test_authority`, and `test_h01_h02_reliability` [17/17]).
- **Frozen metric & integrity verifier (`verify_metrics.py`):** **74/74 PASS** (`HUMAN_REVIEW_WORKSHEET.csv` intact, all 17 human rating columns blank/unfabricated).

---

## 6. Before-and-After H01 Development Measurements (`216` B–R References, Zero Lookup)

| Metric | Original (`73c555cf`) | Sprint-1 (`f9470d4e`) | Final (This Sprint) | Net Delta vs. `73c555cf` |
|---|---:|---:|---:|---:|
| Normalization rate (`n / 216`) | `201 / 216` (`93.06%`) | `210 / 216` (`97.22%`) | **`213 / 216` (`98.61%`)** `[96.00%, 99.53%]` | **`+12` (`+5.55 pp`)** |
| Unresolved (with working tree) / Rejected | `15 / 0` | `6 / 0` | **`3 / 0`** *(only 3 ambiguous B–R cases)* | **`-12`** |
| Terminal yield-aligned (`n / 216`) | `186 / 216` (`86.11%`) | `201 / 216` (`93.06%`) | **`204 / 216` (`94.44%`)** `[90.54%, 96.79%]` | **`+18` (`+8.33 pp`)** |
| **All-attempt full labeled F1** | `59.53%` (`903` matches) | `62.20%` (`966` matches) | **`62.83%` (`989` matches)** | **`+3.30 pp` (`+86` matches)** |
| Aligned full labeled P / R / F1 | `55.60 / 89.05 / 68.46%` | `53.91 / 87.66 / 66.76%` | `53.93 / 87.99 / 66.87%` *(n=204)* | `+18` harder trees aligned |
| **Aligned triangle-aware P / R / F1** | `80.05 / 89.05 / 84.31%` | `78.47 / 87.66 / 82.81%` | **`78.87 / 87.99 / 83.18%`** *(unlabeled `88.81%`)* | `+18` harder trees aligned |
| Full exact agreement (`n / 216`) | `32` (`14.81%`) | `36` (`16.67%`) | **`37` (`17.13%`)** | **`+5` (`0` exact regressions)** |
| Triangle-aware exact (`n / 216`) | `101` (`46.76%`) | `109` (`50.46%`) | **`112` (`51.85%`, `54.90%` aligned)** | **`+11`** |
| Explicit-clause proxy: `0` / `1` / `2+` (all-attempt F1) | `61.09 / 64.12 / 51.76%` | `64.58 / 67.60 / 52.48%` | **`64.83 / 68.81 / 52.90%`** | **`+3.74 / +4.69 / +1.14 pp`** |
| `sentence_root_only` (`n=106`, all-attempt F1) | `55.97%` (`88` aligned) | `57.77%` (`96` aligned) | **`58.27%` (`99` aligned, `3` exact)** | **`+2.30 pp`** |
| Figure `[79b]` (separate author diagram) | Normalized, yield mismatch | Normalized, `8/8` exact | **Normalized, `yield_match=True`, `8/8` exact** | **Exact match** |

**True Syntactic Complexity Stratification (Final, distinguishing real clause structure from visible `S` counts):**
- **Phrase / fragment (`n=110`, non-`S` root):** `109/110` (`99.09%`) normalized, `105` aligned, `34` full exact, `70.22%` all-attempt F1, `74.30%` aligned F1.
- **Simple sentence (`n=62`, `S` root, 1 clause, no `S-bar`/`S-dbar`):** `61/62` (`98.39%`) normalized, `59` aligned, `2` full exact, `64.19%` all-attempt F1, `67.33%` aligned F1.
- **Complex / embedded sentence (`n=44`, `S` root with `S-bar`/`S-dbar` or `2+` clauses):** `43/44` (`97.73%`) normalized, `40` aligned, `1` full exact, `52.69%` all-attempt F1, `57.27%` aligned F1.

*Per-item regression check vs. `f9470d4e`:* `0` exact regressions, `0` normalization regressions, `0` alignment regressions; `5` previously aligned Ch. 9/10 items improved (`ch9-d6-53a` `0.8000 → 1.0000`, `ch10-37` `0.6154 → 0.9231`, `ch9-39` `0.5714 → 0.7143`, `ch9-59` `0.5333 → 0.6667`, `ch9-d5` `0.8148 → 0.8889`). The sole F1 decrease was `ch9-60` (`0.6667 → 0.5333`), which shares the exact punctuation-less string `"the dogs which have rabies"` with restrictive `ch9-59` (`+0.1334`).

---

## 7. Before-and-After H02 Development Measurements (`405` Frozen External Inputs)

### A. Component Licensing Ablation (`run_hypothesis_checks.py h02`, ON vs. OFF)

| Benchmark / Metric | `73c555cf` ON | `f9470d4e` ON | **Final ON** | **Final OFF** |
|---|---:|---:|---:|---:|
| **BLiMP (`116`) exact verdicts** | `85/116` (`73.28%`) | `88/116` (`75.86%`) | **`102/116` (`87.93%`)** | `100/116` (`86.21%`) |
| BLiMP `gram → gram` / `FP` / `unverified` (`n=58`) | `43 / 8 / 7` | `46 / 3 / 9` | **`49 / 2* / 7`** | `49 / 2* / 7` |
| BLiMP `ungram → ungram` / `FN` / `unverified` (`n=58`) | `42 / 7 / 9` | `42 / 7 / 9` | **`53 / 4 / 1`** | `51 / 5 / 2` |
| BLiMP ungrammatical P / R / F1 *(over decisive verdicts)* | `84.0 / 85.7 / 84.8%` | `93.3 / 85.7 / 89.4%` | **`96.4 / 93.0 / 94.6%`** | `96.2 / 91.1 / 93.6%` |
| **W&I+LOCNESS Matrix API (`120`, `193` edits) TP / FP / FN** | `5 / 6 / 188` | `5 / 7 / 188` | **`6 / 7 / 187`** (`11` rev) | `4 / 7 / 189` (`11` rev) |
| W&I Matrix API Prec / Rec / F0.5 | `0.4545 / 0.0259 / 0.1055` | `0.4167 / 0.0259 / 0.1037` | **`0.4615 / 0.0311 / 0.1224`** | `0.3636 / 0.0207 / 0.0844` |
| W&I Learner-visible TP / FP / FN / F0.5 | `2 / 3 / 191 / 0.0469` | `2 / 4 / 191 / 0.0461` | `2 / 4 / 191 / 0.0461` (`6` rev) | `1 / 6 / 192 / 0.0226` (`7` rev) |
| **EXPECT (`169`, `205` evidence tokens) TP / FP / FN** | `6 / 4 / 199` | `6 / 3 / 199` | **`12 / 4 / 193`** | `12 / 4 / 193` |
| EXPECT Prec / Rec / F1 (`anchored / 169`) | `0.6000 / 0.0293 / 0.0558` (`16`) | `0.6667 / 0.0293 / 0.0561` (`15`) | **`0.7500 / 0.0585 / 0.1086` (`20`)** | `0.7500 / 0.0585 / 0.1086` (`18`) |
| Packets with rule findings / sentence prose / node prose (`405`) | `142 / 405 / 400` | `128 / 405 / 400` | `140 / 405 / 400` | `130 / 405 / 400` |

*\*Disputed published-label note:* The `2` remaining BLiMP grammatical→ungrammatical items are `ellipsis_n_bar_2:460` (`"...three exposed art gallery."`, `C-QUANT-PLURAL`) and `wh_questions_object_gap:818` (`"...that all women disgusts."`, `C-SUBJECT-AGREEMENT`), both genuine synthetic agreement errors in BLiMP's reference strings. Original BLiMP scores are preserved unchanged (`2` FP); on the `56` genuinely grammatical BLiMP sentences, false positives are `0/56`.

### B. Whole-System Grounding Comparison (`run_h02_grounding_comparator.py`, Same 405 Inputs)

| Published Benchmark & Outcome | Condition A: Grounded SynTutor | Condition B: Ungrounded Neural SynTutor (CoLA + MLM Perturbation) | Paired Statistical Test (Exact Two-Sided McNemar) |
|---|---:|---:|---|
| **BLiMP exact verdicts (`n=116`)** | **`102/116` (`87.93%`)** `CI95 [80.76%, 92.67%]` | `95/116` (`81.90%`) `CI95 [73.90%, 87.84%]` | `b = 10, c = 3, p = 0.0923` *(n.s. at α=0.05)* |
| **BLiMP minimal pairs both exact (`n=58` pairs)** | **`46/58` (`79.31%`)** | `37/58` (`63.79%`) | **`b = 10, c = 1, p = 0.0117`** *(significant)* |
| **BLiMP false-positive ungrammatical feedback on grammatical sentences (`n=58`)** | **`2/58` (`3.45%`)** | **`13/58` (`22.41%`)** | **`b = 12, c = 1, p = 0.0034`** *(significant; -84.6% FPs)* |
| BLiMP abstention (`unverified`) rate (`n=116`) | `8/116` (`6.90%`) | `0/116` (`0.00%`) | Reported explicitly (abstentions counted as non-matches) |
| **W&I+LOCNESS ERRANT TP / FP / FN / Prec / F0.5 (`120` items)** | **`6 / 7 / 187 / 0.4615 / 0.1224`** (`11` rev) | `1 / 6 / 192 / 0.1429 / 0.0226` (`7` rev) | Per-sentence FP presence: `6` vs `6` (`b=2, c=2, p=1.0000`); Grounded `5.4×` F0.5, `6×` TP |
| **EXPECT evidence TP / FP / FN / Prec / F1 (`169` items)** | **`12 / 4 / 193 / 0.7500 / 0.1086`** (`20` anchored) | `0 / 0 / 205 / 0.0000 / 0.0000` (`1` anchored) | Ungrounded single-token perturbation supplies zero relational evidence |

---

## 8. Achievement Status of `>80%` Engineering Targets

| Target | Achieved? | Measured Value & Exact Denominator |
|---|---|---|
| **H01:** Normalization & terminal alignment coverage | **YES** | **`98.61%`** (`213/216`) normalized; **`94.44%`** (`204/216`) yield-aligned. |
| **H01:** Triangle-aware labeled F1 `>80%` | **YES** | **`83.18%`** (`n=204` aligned; unlabeled **`88.81%`**; recall **`87.99%`**). |
| **H01:** All-attempt full labeled F1 `>80%` | **NO** | **`62.83%`** (`n=216`). Structural ceiling due to `561` triangle-internal nodes, `~52` Ch. 1–2 `Phrase` placeholders, and `47` Ch. 8 clause-outline triangles. |
| **H01:** Complex-sentence full labeled F1 `>80%` | **NO** | **`52.69%`** all-attempt / **`57.27%`** aligned (`n=44` complex/embedded sentences). |
| **H01:** Full exact tree agreement `>80%` (stretch) | **NO** | **`17.13%`** full exact (`37/216`); **`51.85%`** triangle-aware exact (`112/216`). |
| **H02:** Grammaticality judgment accuracy `>80%` | **YES** *(dev benchmark)* | **`87.93%`** (`102/116`, 95% CI `[80.76%, 92.67%]`) on BLiMP with abstentions counted as errors (`94.6%` ungrammatical F1 on decisive verdicts; `3.45%` FP rate). |
| **H02:** Conceptually correct explanations `>80%` (independent set) | **NOT MEASURED** | Blocked: blinded human annotation of prose explanations has not been performed yet. |
| **H02:** Evidence localization `>80%` within supported scope | **NO** | EXPECT precision reached **`75.00%`** (`12/16` emitted evidence tokens), but overall recall is **`5.85%`** (`12/205`) because most EXPECT categories (`Others`, `Collocation`, `Preposition`, `Possessive` proper names) fall outside deterministic rule coverage. |
| **H02:** Valid corrections `>80%` with adequate coverage | **NO** | W&I+LOCNESS ERRANT exact-edit precision **`46.15%`** (`6/13`), recall **`3.11%`** (`6/193`), F0.5 **`0.1224`** (`11/120` sentences revised). |

---

## 9. Conceptual Correctness Evaluation and Evidence Limits

Per the 5-criterion conceptual rubric (1. correct grammatical principle, 2. correct application to sentence, 3. correct target words/relationships, 4. correct tree-node/evidence association, 5. no unsupported/false claims):
- Automated benchmarks verify **necessary components**—verdict accuracy (BLiMP), exact-edit alignment (W&I+LOCNESS ERRANT), and token-evidence overlap (EXPECT)—and programmatic regression tests verify specific known failure fixes (e.g., `"invent new stuff"`, `"This is big change."`, `"Every citizen owns a car and use it"`, `"Bodies can start their days in a test tubes."`).
- Automated benchmarks **do not independently verify free-text conceptual explanation correctness**, and AI-judged or embedding-similarity labels were intentionally NOT used.
- A ready-to-annotate, randomly anonymized blinded human-review worksheet (`405` differing Condition A vs. Condition B pairs, `System X` vs. `System Y`, all 12 human rubric columns blank and unfabricated) was exported to `/tmp/syntutor-comp-final/h02-grounding-v2/BLINDED_GROUNDED_VS_UNGROUNDED_WORKSHEET.csv` with sealed key `/tmp/syntutor-comp-final/h02-grounding-v2/BLINDED_KEY_SEALED.json`.

---

## 10. Independent Validation Readiness and Results Obtained

- **H01:** The production `FINAL-D1` projector is engineering-ready and frozen-testable (`98.61%` normalization, zero lookup, zero exact regressions). An audit of all repository assets confirmed **no unused, independently verified B–R `FINAL-D1` reference set exists** beyond the `216` development textbook diagrams and Figure `[79b]` (which is single-reader transcribed and already exposed). Penn/GUM trees cannot substitute for `FINAL-D1`.
- **H02:** The whole-system Grounded vs. Ungrounded comparator is executable, deterministic, and reproducible on identical inputs (`run_h02_grounding_comparator.py`). However, the `405` frozen external items were used during development diagnostics, and human prose grading remains pending—so these results are **paired development/diagnostic evidence**, not confirmatory independent validation.

---

## 11. Statistical Test Results (Validly Executed on Published External Ground Truth)

All statistical tests below were executed on published external ground-truth labels (zero AI-invented labels, zero post-hoc cutoffs) on the `405`-item paired Grounded vs. Ungrounded comparator:
- **BLiMP false-positive ungrammatical feedback reduction (`n=58` grammatical items):** Grounded `2/58` (`3.45%`) vs. Ungrounded `13/58` (`22.41%`); exact two-sided paired McNemar `b = 12, c = 1, p = 0.0034`.
- **BLiMP minimal-pair exact accuracy (`n=58` pairs, accounting for pair clustering):** Grounded `46/58` (`79.31%`) vs. Ungrounded `37/58` (`63.79%`); exact two-sided paired McNemar `b = 10, c = 1, p = 0.0117`.
- **BLiMP item-level exact accuracy (`n=116`, abstentions counted as non-matches):** Grounded `102/116` (`87.93%`, 95% Wilson CI `[80.76%, 92.67%]`) vs. Ungrounded `95/116` (`81.90%`, 95% Wilson CI `[73.90%, 87.84%]`); exact two-sided paired McNemar `b = 10, c = 3, p = 0.0923`.
- **W&I+LOCNESS per-sentence ERRANT FP presence (`n=120`):** `6` vs. `6` (`b = 2, c = 2, p = 1.0000`), while Grounded achieved `6` TP vs. `1` TP (`F0.5 = 0.1224` vs. `0.0226`).

*Caveat:* Because BLiMP/W&I/EXPECT were inspected during development, these p-values are **paired diagnostic/ablation evidence** and must be replicated on a fresh, untouched held-out sample with blinded human ratings for confirmatory inference.

---

## 12. Explicit Original H01 and H02 Hypothesis Decisions

- **Original H01:** **`NOT STATISTICALLY DETERMINED`** — Development structural accuracy improved substantially (`98.61%` normalization, `94.44%` alignment, `62.83%` all-attempt F1, `83.18%` triangle-aware F1), but no untouched, independently two-reader-verified, complexity-stratified Burton–Roberts `FINAL-D1` test set exists yet to perform a valid confirmatory test.
- **Original H02:** **`NOT STATISTICALLY DETERMINED`** — The new whole-system paired grounding comparator provides strong diagnostic evidence that Matrix/Cambridge grounding significantly reduces false-positive ungrammatical feedback (`13 → 2`, McNemar `p = 0.0034`), improves minimal-pair accuracy (`p = 0.0117`), yields `5.4×` higher correction F0.5 on W&I+LOCNESS, and enables relational evidence localization (`TP = 12` vs. `0` on EXPECT). However, confirmatory rejection of the full original H02 still requires blinded human linguist scoring of conceptual prose correctness on an untouched held-out sample.

---

## 13. Remaining Methodological Blockers

1. **H01 Untouched Reference Set:** Obtain Burton–Roberts (3rd ed.) *Answer Book for the Further Exercises*, transcribe eligible full diagrams (no collapsed-triangle ambiguity) with independent two-reader verification, stratify by true syntactic complexity, and freeze before running one-shot evaluation.
2. **H02 Blinded Human Prose Review on Untouched Data:** Freeze an untouched multi-source test set (unseen BLiMP/W&I/EXPECT items), run `run_h02_grounding_comparator.py` once, and have two qualified human linguists independently score the anonymized `BLINDED_GROUNDED_VS_UNGROUNDED_WORKSHEET.csv` on the 5-criterion conceptual rubric with inter-rater reliability (Cohen's κ / Krippendorff's α) before running confirmatory paired McNemar / Wilcoxon tests.
3. **H02 Free-Writing Recall Ceiling:** Deterministic rule-backed gating achieves high precision (`96.4%` BLiMP ungrammatical precision, `75.0%` EXPECT evidence precision) at low free-essay recall (`3.11%` W&I, `5.85%` EXPECT) because open-class lexical choice, collocations, punctuation style, and discourse rewrites lie outside deterministic syntactic rules.

---

## 14. Reproducible Commands and Artifact Paths

```bash
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONDONTWRITEBYTECODE=1

# 1. Full 20-module regression suite (220 tests) + 74 metric integrity checks
PYTHONPATH=server .venv/bin/python -m unittest \
  server/test_parser_runtime.py server/test_burton_roberts.py server/test_br_final_d1_gold.py \
  server/test_br_final_d1_dispositions.py server/test_br_tree.py server/test_canonical_binding.py \
  server/test_xai_facts.py server/test_findings.py server/test_licensing.py server/test_corrector.py \
  server/test_cross_layer_consistency.py server/test_correction_completeness.py \
  server/test_learner_analysis.py server/test_detection_scoping.py \
  server/test_nlp_reliability_regressions.py server/test_relative_pronoun.py \
  server/test_cambridge_registry.py server/test_cambridge_evaluator.py server/test_authority.py \
  server/test_h01_h02_reliability.py
.venv/bin/python docs/audits/technical_evaluation/verify_metrics.py

# 2. H01 complete-pipeline development evaluation (fresh output dir)
.venv/bin/python docs/audits/technical_evaluation/run_hypothesis_checks.py h01 /tmp/syntutor-repro-h01

# 3. H02 component licensing ablation (ON vs OFF, fresh output dir)
PYTHONPATH=/tmp/syntutor-phase2/scoring-deps .venv/bin/python \
  docs/audits/technical_evaluation/run_hypothesis_checks.py h02 \
  /tmp/syntutor-phase2 /tmp/syntutor-phase2/external-manifest.json /tmp/syntutor-repro-h02

# 4. H02 whole-system Grounded vs Ungrounded Neural comparator (fresh output dir)
PYTHONPATH=/tmp/syntutor-phase2/scoring-deps .venv/bin/python \
  docs/audits/technical_evaluation/run_h02_grounding_comparator.py \
  /tmp/syntutor-phase2 /tmp/syntutor-phase2/external-manifest.json /tmp/syntutor-repro-h02-grounding
```

**Saved Verification Artifacts:**
- H01 final run: `/tmp/syntutor-comp-h01-v2/{h01.json,h01-source-figure-79b.json}`
- H02 ON/OFF final run: `/tmp/syntutor-comp-final/h02-v2/{on,off,paired.json}`
- H02 Grounded vs. Ungrounded comparator & blank blinded worksheet: `/tmp/syntutor-comp-final/h02-grounding-v2/{summary.json,BLINDED_GROUNDED_VS_UNGROUNDED_WORKSHEET.csv,BLINDED_KEY_SEALED.json}`

---

## 15. Evidence-Supported Recommendations for Chapter V

1. **Report H01 honestly with full denominator transparency:** Present `98.61%` normalization (`213/216`), `94.44%` yield alignment (`204/216`), `62.83%` all-attempt full labeled F1, and `83.18%` triangle-aware labeled F1 alongside the true complexity strata (`70.22%` phrase/fragment, `64.19%` simple sentence, `52.69%` complex/embedded sentence) and explain the textbook triangle/placeholder structural ceiling (`561` triangle-internal nodes). Do **not** claim confirmatory rejection of H01 until an untouched, two-reader-verified `FINAL-D1` test set is evaluated.
2. **Report H02 using both the component ablation and the new whole-system Grounded vs. Ungrounded comparator:** Highlight that grounding achieved `87.93%` BLiMP accuracy (`95% CI [80.76%, 92.67%]`), cut false-positive ungrammatical feedback from `22.41%` to `3.45%` (paired McNemar `p = 0.0034`), improved minimal-pair accuracy (`p = 0.0117`), raised W&I+LOCNESS ERRANT F0.5 `5.4×` (`0.1224` vs. `0.0226`), and raised EXPECT evidence precision to `75.00%` (`TP = 12` vs. `0`), while explicitly stating that low free-essay recall (`3.11%` W&I, `5.85%` EXPECT) reflects precision-first rule gating and that confirmatory H02 rejection awaits blinded human grading of conceptual prose correctness on untouched data.
3. **Preserve exact hypothesis status wording:** Classify both original H01 and original H02 as **`NOT STATISTICALLY DETERMINED`** pending the two remaining external human/reference validation protocols above, rather than overclaiming rejection or misusing "failed to reject" for unexecuted confirmatory tests.
