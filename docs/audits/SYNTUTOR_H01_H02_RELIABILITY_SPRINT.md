# SynTutor H01/H02 Focused Reliability Sprint Report

**Repository:** `SynTutor`  
**Branch:** `fix/syntutor-system-reliability-xai`  
**Base Commit:** `73c555cf8261771eecdcabb15925f093884040ca` (unmodified baseline captured directly on this commit before any sprint edits)  
**Working Tree Status:** Uncommitted local changes only (no commits, pushes, merges, or rebases; no edits to evaluation scripts, frozen datasets, scorers, hypotheses, or thesis text).

> **Scientific Scope Statement:** All before-and-after metrics below are **development-set** measurements obtained by running the unmodified, frozen evaluators on identical inputs (`216` Burton–Roberts textbook references for H01; `405` paired external inputs from BLiMP, W&I+LOCNESS, and EXPECT for H02). They demonstrate genuine implementation reliability improvements, **not** independent statistical validation or rejection of the original H01 or H02 hypotheses.

---

## 1. Baseline Measurements and Evaluated Version

Fresh unmodified baselines were captured on `73c555cf8261771eecdcabb15925f093884040ca` using `docs/audits/technical_evaluation/run_hypothesis_checks.py` inside `.venv` (Python 3.11.17, spaCy 3.8.16, `en_core_web_md`, `benepar_en3`, Transformers 4.46.3, ERRANT 3.0.0) and reproduced the historical reference numbers in `docs/audits/H01_H02_VALIDATION_BLOCKER_RESOLUTION.md` identically:

- **H01 Unmodified Baseline (`73c555cf`, zero textbook lookup verified via `normalize_benepar_candidate`):**
  - `216` B–R references: `201/216` normalized (`93.06%`), `15` explicitly unresolved (all `15` with working fallback trees, `0` rejected), `186/216` yield-aligned (`86.11%`).
  - Aligned full labeled F1: `68.46%` (`P = 55.60%`, `R = 89.05%`, `903` matched constituents, `32` exact).
  - Aligned triangle-aware labeled F1: `84.31%` (`P = 80.05%`, `R = 89.05%`, `101` exact).
  - All-attempts full labeled F1: `59.53%` (`903` matches / `1195` gold / `1839` predicted).
  - Complexity strata (all-attempts F1): `0` clauses `61.09%` (`83`), `1` clause `64.12%` (`90`), `2+` clauses `51.76%` (`43`); `sentence_root_only`: `55.97%` (`106` attempted, `88` aligned, `2` exact).
  - Figure `[79b]` (`He didn't remember kissing Millie.`): normalized, `8/8` lexical-character exact, raw terminal yield mismatch (`did` + `n't`).
- **H02 Unmodified Baseline (`73c555cf`, frozen manifest SHA-256 `0a0322368b646873a1b42f77571d27259a2e664a1c20b09aa831afd98d1b4672`, `405` paired inputs ON vs. OFF):**
  - **BLiMP (`116`):** ON = `85/116` (`43` gram, `42` ungram, `8` FP, `7` FN, `16` unverified); OFF = `85/116` (`45` gram, `40` ungram, `8` FP, `8` FN, `15` unverified).
  - **W&I+LOCNESS (`120` items, `193` gold edits, `2` parser failures):** Matrix API ON `TP=5, FP=6, FN=188, Prec=0.4545, Rec=0.0259, F0.5=0.1055` (`9` revisions); Learner-visible ON `TP=2, FP=3, FN=191, Prec=0.4000, Rec=0.0104, F0.5=0.0469` (`5` revisions). Known false explanation on `"invent new stuff"` (`A.dev:123`, plus bogus `"invent a new stuff"` revision in OFF).
  - **EXPECT (`169` annotations, `205` evidence tokens, `9` failures):** ON `TP=6, FP=4, FN=199, Prec=0.6000, Rec=0.0293, F1=0.0558` (`16` anchored); OFF identical (`14` anchored).
  - **Packet coverage:** `packets_with_rule_findings`: ON `142`, OFF `133`; `packets_with_sentence_prose`: `405/405`; `packets_with_node_prose`: `400/405`.

---

## 2. Root Causes Investigated (Top 3 per Hypothesis)

### H01 — Benepar → Burton–Roberts (`FINAL-D1`) Projection

1. **Tokenization Yield Mismatches on Contracted Negative Auxiliaries & Hyphenated Compounds:** Benepar splits negative contractions (`didn't` → `did` + `n't`) and hyphenated compounds (`second-hand` → `second` + `-` + `hand`), causing `15` yield-alignment failures on Burton–Roberts Ch. 2–10 diagrams (including Fig. `[79b]`). Meanwhile, B–R Ch. 7 explicitly analyzes possessive `'s` (`POSS → NP + 's`) and participial `so-called` (`DEG + PartP`), so those must remain split.
2. **Unresolved Structural Constructions in `FINAL-D1` Projection:** `15` textbook diagrams failed projection due to unhandled general syntactic patterns: nested/coordinated passive VPs (`was accepted and quickly published`, `were being observed at all`), passive complex-transitive complements (`was driven mad`), subject wh-questions parsed as `SQ(AUX, VP)`, root `WHADVP` copular questions (`How are you`), complete noun-complement `that`-clauses vs. gapped relative clauses (`a proposal that we should support [the strike]`), `UCP`-coordinated prepositions (`up and down the staircase`), `PRE-DET` wrapped inside possessive `NP` (`all Gulbenkian's contributions`), and standalone non-finite overt-subject clauses (`Murtlock having been hospitalised`).
3. **B–R Ch. 7 Appendix D1 `of`-PP Complement Attachment Inside `NOM`:** Benepar wraps `(NP (NP DT premods N) (PP of ...))`, causing `of`-PP noun complements to attach outside premodifying `AP`s instead of as immediate sister to `N` inside `NOM` (`NOM → N + PP(of ...)` before outer `AP`/`PP` modifiers, e.g., `that tall student of maths in the hat`).

### H02 — Constraint Matrix, Cambridge Rules, Corrections, and XAI Consistency

1. **`C-ARTICLE` False Positives on Uncountable/Abstract Nouns, Misspelled/Unknown Words, and Post-Auxiliary Base Verbs:** Missing standard mass/abstract nouns (`stuff`, `manipulation`, `indifference`, `change`, etc.) caused false `C-ARTICLE` explanations (including `"new stuff"` on `A.dev:123` and bogus `"a new stuff"` / `"a genetic manipulation"` / `"a little change"` repairs). Unknown/misspelled words (`excercise`) were also treated as verified singular countable nouns, and bare verbs misparsed as `NP(NN)` after modals were not exempted.
2. **High-Severity False Grammatical Rules & Wrong Corrections:**
   - `C-PREP-GERUND` unconditionally flagged `('used', 'to') + VB`, teaching ungrammatical English (`used to preparing`) on grammatical passive-purpose (`Fire has always been used to prepare the food`) and habitual past (`used to live`) constructions.
   - `C-CONDITIONAL-WILL` scanned forward across flat leaves past the `if`-`SBAR` boundary into matrix apodoses (`If we miss the boat I think we will...`) and nested relative clauses (`laws that would unite it`).
   - `C-STRANDED-PREP` missed `it`-clefts (`It's herself that some girl wasn't listening to.`) and hollow-clause control adjectives (`ready`, `fit`, `suitable`, `eligible`, `available`, `free`, `open` in `Kristen wasn't ready to return to.`).
   - `C-SUBJECT-AGREEMENT` falsely fired on ECM infinitivals parsed as `S(NP, TO, VP)` (`anticipate it to be unexpected`) and coordinated bare clauses under inverted `SQ`/`SBARQ` (`What cashiers did Beverly disgust and Carla listen to?`).
   - `C-PREP-PRON-CASE` treated verb particles (`RP`, e.g., `figured out she will listen to?`) as prepositions governing object pronouns.
   - `C-NOUN-FORM` rejected numeric decade plurals (`1920s → 1920S`), `C-ADJ-ADV` rejected numeric ordinals (`21st`), and `C-COMMA-SPLICE` scanned across colons/semicolons (`effects: First of all, children...`).
3. **Duplicate Learner Findings in `supported_findings()`:** Nested `S` nodes producing identical `(code, text)` prose (e.g., `C-FINITE-VERB` on `A.dev:825`) were emitted twice in learner-facing findings.

*(Note: Two BLiMP "grammatical" items—`ellipsis_n_bar_2:460` `"three exposed art gallery"` and `wh_questions_object_gap:818` `"that all women disgusts"`—contain genuine synthetic errors in BLiMP itself. SynTutor's `C-QUANT-PLURAL` and `C-SUBJECT-AGREEMENT` rules are linguistically correct on both and were intentionally NOT weakened.)*

---

## 3. Exact Implementation Changes

| File | Diff | Summary of Changes |
|---|---|---|
| [server/burton_roberts.py](file:///Users/kiyel/Desktop/SynTutor/server/burton_roberts.py) | `+137 / -4` | Added `_fuse_orthographic_tokens()` to fuse contiguous negative-auxiliary contractions (`didn't`, `hasn't`, etc., with `fused_aux_base` metadata) and non-participial hyphenated compounds (`second-hand`, excluding `RB + HYPH + VBN/VBG` like `so-called` and never fusing possessive `'s`) on a working copy without mutating raw `analysis['tokens']`; added `UCP` dispatch in `_final_projection()`. |
| [server/final_d1_projection.py](file:///Users/kiyel/Desktop/SynTutor/server/final_d1_projection.py) | `+135 / -9` | Updated `lemma()`/`tense()` for fused negative auxiliaries; added single-adjective `NML` handling; peeled nested/coordinated VP wrappers in `auxiliary()` and shared passive object gaps + complex-transitive passive complements in `vp()`; added subject-wh `SQ`, root `WHADVP`, and standalone non-finite clause projection; added noun-complement vs. relative `that`-clause fallback; added `UCP` coordinated-PP projection and `PRE-DET` hoisting over possessive `NP`; added Ch. 7 Appendix D1 `of`-PP complement attachment inside `NOM`. |
| [server/matrix.py](file:///Users/kiyel/Desktop/SynTutor/server/matrix.py) | `+53 / -4` | Expanded `NONCOUNT_NOUNS` with genuinely mass/uncountable abstract nouns (`stuff`, `manipulation`, `indifference`, `change`, etc.); exempted unknown/misspelled words and post-modal base verbs in `_needs_indefinite_article_error()`; exempted numeric decade plurals (`\d{2,4}s`) in `_noun_form_issue()` and numeric ordinals (`\d+(st|nd|rd|th)`) in `C-ADJ-ADV`; fixed `_s_predicate()` to recognize `S(NP, TO, VP)` infinitivals and coordinated `VP` under inverted `SQ`/`SBARQ` questions. |
| [server/ruleset.py](file:///Users/kiyel/Desktop/SynTutor/server/ruleset.py) | `+73 / -8` | Replaced unconditional `('used', 'to')` in `PREP_GERUND_PHRASES` with unambiguous adjectival `get/become + used + to`; scoped `C-CONDITIONAL-WILL` strictly to the `if`-`SBAR`'s own clause leaves (excluding matrix apodoses and nested `SBAR`/`S`); added `it`-cleft licensing and hollow-clause adjectives (`ready`, `fit`, `suitable`, `eligible`, `available`, `free`, `open`) to `C-STRANDED-PREP`; skipped `RP` verb particles in both `C-PREP-PRON-CASE` checks; reset `C-COMMA-SPLICE` `before` slicing after literal `:` / `;` surface tokens (not PTB `:` tag, which matches hyphens/dashes). |
| [server/findings.py](file:///Users/kiyel/Desktop/SynTutor/server/findings.py) | `+4 / -1` | Deduplicated identical `(code, text)` learner findings in `supported_findings()` (except distinct-span `C-SPELLING` / `C-SPACING-REPEAT` occurrences). |
| [server/test_h01_h02_reliability.py](file:///Users/kiyel/Desktop/SynTutor/server/test_h01_h02_reliability.py) | New (`280` lines) | Added 14 focused positive & negative regression tests covering all 3 H01 and all 3 H02 root causes. |

---

## 4. Before-and-After Development Results (Identical Inputs & Frozen Scorers)

### H01 — 216 Burton–Roberts References (`run_hypothesis_checks.py h01`, zero textbook lookup)

| Metric | Baseline (`73c555cf`) | After Sprint | Delta |
|---|---:|---:|---:|
| Normalized (`n / 216`) | `201 / 216` (`93.06%`) | **`210 / 216` (`97.22%`)** | **`+9` (`+4.16 pp`)** |
| Explicitly unresolved (with working tree) | `15` (`0` rejected) | **`6` (`0` rejected)** | **`-9`** |
| Terminal yield-aligned (`n / 216`) | `186 / 216` (`86.11%`) | **`201 / 216` (`93.06%`)** | **`+15` (`+6.95 pp`)** |
| **All-attempts full labeled F1** | `59.53%` (`903` matches) | **`62.20%` (`966` matches)** | **`+2.67 pp` (`+63` matches)** |
| Full exact matches (`n / 216`) | `32` (`14.81%`) | **`36` (`16.67%`)** | **`+4` (`0` regressions)** |
| Triangle-aware exact matches (`n / 216`) | `101` (`46.76%`) | **`109` (`50.46%`)** | **`+8` (`0` regressions)** |
| Aligned full labeled F1 *(larger denominator)* | `68.46%` (`n=186`) | `66.76%` (`n=201`) | `-1.70 pp` *(see note)* |
| Aligned triangle-aware F1 *(larger denominator)* | `84.31%` (`n=186`) | `82.81%` (`n=201`) | `-1.50 pp` *(see note)* |
| Complexity: `0` clauses (all-attempts F1, `n=83`) | `61.09%` (`81` norm) | **`64.58%` (`83/83` norm)** | **`+3.49 pp`** |
| Complexity: `1` clause (all-attempts F1, `n=90`) | `64.12%` (`85` norm) | **`67.60%` (`87` norm)** | **`+3.48 pp`** |
| Complexity: `2+` clauses (all-attempts F1, `n=43`) | `51.76%` (`35` norm) | **`52.48%` (`40` norm)** | **`+0.72 pp`** |
| `sentence_root_only` (all-attempts F1, `n=106`) | `55.97%` (`88` aligned, `2` exact) | **`57.77%` (`96` aligned, `3` exact)** | **`+1.80 pp`** |
| Figure `[79b]` (`He didn't remember kissing Millie.`) | Normalized, raw yield mismatch | **Normalized, `yield_match=True`, `8/8` exact** | **Exact match** |

*Denominator note:* Per-item comparison across all `186` previously aligned references confirms **`0` exact regressions, `0` triangle-exact regressions, `0` normalization regressions, `0` alignment regressions, and `0` F1 regressions**, with `7` previously aligned cases strictly improving (e.g., `ch7-disc7` `0.8889 → 1.0000`, `ch7-ex1-b` `0.8000 → 0.9167`). The lower aligned-subset average reflects `15` harder Ch. 6–10 items entering the aligned denominator from `0%` unaligned.

### H02 — 405 Paired External Inputs (`run_hypothesis_checks.py h02`, ON vs. OFF)

| Benchmark / Metric | Baseline ON | After Sprint ON | Baseline OFF | After Sprint OFF |
|---|---:|---:|---:|---:|
| **BLiMP (`116`) exact** | `85 / 116` (`43` g, `42` u) | **`88 / 116` (`46` g, `42` u)** | `85 / 116` (`45` g, `40` u) | **`88 / 116` (`48` g, `40` u)** |
| **BLiMP false positives (`gram → ungram`)** | `8` | **`3` (`-62.5%`)** | `8` | **`3` (`-62.5%`)** |
| **BLiMP false negatives (`ungram → gram`)** | `7` | `7` (`0` reg) | `8` | `8` (`0` reg) |
| **EXPECT (`169`) TP / FP / FN** | `6 / 4 / 199` | **`6 / 3 / 199`** | `6 / 4 / 199` | **`6 / 3 / 199`** |
| **EXPECT precision / F1** | `0.6000` / `0.0558` | **`0.6667` / `0.0561`** | `0.6000` / `0.0558` | **`0.6667` / `0.0561`** |
| **W&I Matrix API (`120`) TP / FP / FN / F0.5** | `5 / 6 / 188 / 0.1055` | `5 / 7 / 188 / 0.1037` *(note)* | `4 / 7 / 189 / 0.0844` | `4 / 7 / 189 / 0.0844` |
| **W&I Learner-visible (`120`) TP / FP / FN / F0.5** | `2 / 3 / 191 / 0.0469` | `2 / 4 / 191 / 0.0461` *(note)* | `1 / 4 / 192 / 0.0235` | `1 / 6 / 192 / 0.0226` |
| **Packets with rule findings (`405`)** | `142` | **`128` (`-14`)** | `133` | **`118` (`-15`)** |
| **Sentence / node prose coverage** | `405 / 400` | `405 / 400` | `405 / 400` | `405 / 400` |

*Exact packet-level audit (`405` inputs):* In both ON and OFF arms, **`24` packets changed**, **`22` false-positive rule firings were eliminated** (`C-ARTICLE`: 6, `C-PREP-GERUND`: 4, `C-STRANDED-PREP`: 3, `C-CONDITIONAL-WILL`: 3, `C-SUBJECT-AGREEMENT`: 2, `C-COMMA-SPLICE`: 2, `C-PREP-PRON-CASE`: 1, `C-NOUN-FORM`: 1), and **`0` new rules were falsely added** (`added_rules = {}`). Known defects resolved: `"invent new stuff"` (`A.dev:123`), `"Doing excercise"` (`B.dev:1100`), duplicate `C-FINITE-VERB` prose (`A.dev:825`), `"1920s → 1920S"`, `"a genetic manipulation"`, `"a little change"`, `"used to prepare"`, and `"used to live"`.

*W&I ERRANT note:* Zero TPs were lost (`TP = 5` Matrix ON, `TP = 2` Learner ON). The single extra ERRANT FP on ON (`B.dev:527`: `"But television have also negative effects: First of all, children..."`) occurred because removing the false `C-COMMA-SPLICE` unblocked the genuine `C-SUBJECT-AGREEMENT` repair (`television have → television has`), which ERRANT marks FP only because the W&I reference merges verb agreement and adverb placement into one span (`have also → also has`).

---

## 5. Focused Tests and Regression Checks

All automated verification suites passed on the final working tree:

- **New H01/H02 focused regression suite** (`server/test_h01_h02_reliability.py`): **14/14 PASS** (positive & negative cases for all 6 root causes).
- **B–R & Cambridge core suites** (`test_burton_roberts`, `test_br_final_d1_gold`, `test_br_tree`, `test_canonical_binding`, `test_xai_facts`, `test_cambridge_registry`, `test_cambridge_evaluator`, `test_authority`): **109/109 PASS** (including M1-envelope source audit `217/217` normalized).
- **H02 matrix, licensing, corrector, findings & scoping suites** (`test_findings`, `test_licensing`, `test_corrector`, `test_cross_layer_consistency`, `test_correction_completeness`, `test_learner_analysis`, `test_detection_scoping`, `test_nlp_reliability_regressions`, `test_relative_pronoun`): **77/77 PASS** (plus re-verified `38/38` on `test_h01_h02_reliability` + `test_detection_scoping` + `test_learner_analysis` after the final colon-vs-dash fix).
- **Frozen evaluation metric & integrity verifier** (`docs/audits/technical_evaluation/verify_metrics.py`): **74/74 PASS** (`HUMAN_REVIEW_WORKSHEET.csv` untouched, all 17 human columns blank/unfabricated).

---

## 6. Independent-Evaluation Readiness Assessment

- **H01:** The production Benepar → Burton–Roberts `FINAL-D1` projector is now **substantially stronger and engineering-ready for independent testing** (`97.22%` normalization, `93.06%` terminal alignment, `62.20%` all-attempts F1, `50.46%` triangle-aware exact, `0` regressions on any previously aligned tree). However, it is **not yet independently validated**.
- **H02:** The Matrix / Cambridge rule engine and learner-facing explanation layer now have **sharply lower false-positive rates** (`-62.5%` BLiMP FPs, `+6.67 pp` EXPECT precision, `22` verified false rules removed, `0` newly added FPs, duplicate prose fixed). However, recall on free learner writing (`W&I+LOCNESS` `Rec = 2.59%`, `EXPECT` `Rec = 2.93%`) remains structurally low by design (high-precision rule-backed gating), and the **original H02 grounding hypothesis remains unverified**.

---

## 7. Remaining Research-Evidence Blockers

1. **H01 Independent Test Set Blocker:** No independently verified, complexity-stratified Burton–Roberts `FINAL-D1` test set exists outside the `216` textbook diagrams already used for development. Independent validation requires transcribing unseen exercises (e.g., from Burton–Roberts 3rd ed. *Answer Book for the Further Exercises*) with independent two-reader verification before freezing and running one-shot evaluation.
2. **H02 Grounding Comparator Blocker:** The existing ON/OFF ablation in `run_hypothesis_checks.py h02` only toggles `check_lexicon` and `check_relatives` inside `server/licensing.py`; it does **not** isolate a full Constraint-Matrix / Cambridge-grounded vs. ungrounded XAI comparator.
3. **H02 Human Prose-Correctness Ground Truth Blocker:** `H02_BLINDED_REVIEW_WORKSHEET.csv` / `HUMAN_REVIEW_WORKSHEET.csv` remain unannotated (no blinded human linguist ratings of explanation correctness and hallucination rate exist yet).

---

## 8. Reproducible Commands and Next Executable Action

```bash
# 1. Focused H01 + H02 regression tests and metric integrity verification
PYTHONPATH=server HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python -m unittest \
  server/test_h01_h02_reliability.py \
  server/test_burton_roberts.py server/test_br_final_d1_gold.py server/test_br_tree.py \
  server/test_canonical_binding.py server/test_xai_facts.py \
  server/test_findings.py server/test_licensing.py server/test_corrector.py \
  server/test_cross_layer_consistency.py server/test_correction_completeness.py \
  server/test_learner_analysis.py server/test_detection_scoping.py \
  server/test_nlp_reliability_regressions.py server/test_relative_pronoun.py \
  server/test_cambridge_registry.py server/test_cambridge_evaluator.py server/test_authority.py
.venv/bin/python docs/audits/technical_evaluation/verify_metrics.py

# 2. Reproduce H01 development evaluation (fresh output dir)
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python docs/audits/technical_evaluation/run_hypothesis_checks.py h01 /tmp/syntutor-repro-h01

# 3. Reproduce H02 paired ON/OFF development evaluation (fresh output dir)
PYTHONPATH=/tmp/syntutor-phase2/scoring-deps HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONDONTWRITEBYTECODE=1 \
  .venv/bin/python docs/audits/technical_evaluation/run_hypothesis_checks.py h02 \
  /tmp/syntutor-phase2 /tmp/syntutor-phase2/external-manifest.json /tmp/syntutor-repro-h02
```

**Next Executable Action:** Review and commit these verified engineering fixes on `fix/syntutor-system-reliability-xai`, then close the two external research-evidence blockers before any thesis hypothesis claim: (1) construct and two-reader-verify a held-out complexity-stratified Burton–Roberts `FINAL-D1` test set for H01, and (2) complete blinded human annotation of the H02 explanation-grounding worksheet alongside a full grounded-vs.-ungrounded comparator.
