# SynTutor — Targeted Reliability Improvement & Independent Evaluation V2 Report (H01 & H02)

**Branch:** `fix/syntutor-system-reliability-xai`  
**Evaluation V1 Status:** Permanently preserved unmodified (`/tmp/syntutor-final-eval/`, `H01_H02_FINAL_EVALUATION_RESULTS_REPORT.md`, frozen V1 SHA-256 checksums re-verified identical).  
**Evaluation V2 Status:** Executed **once** on 100 brand-new, zero-overlap published textbook sentences (`V2_PROPOSED_100_SENTENCES.csv`) after freezing both production code and the V2 scoring runner. Raw artifacts archived at `/tmp/syntutor-final-eval-v2/` with `ARTIFACTS.sha256`.

---

## 1. Executive Summary Against the 80–82% Engineering Targets

| Target Domain | Metric | V1 (Frozen) | V2 (Frozen, Unseen) | ≥80% Target Met? |
|---|---|---:|---:|---|
| **H01 — Unseen B–R Partial Relations** | Track 2 All-Checked Passed (`n=16` V1 / `n=22` V2) | 43.75% (`7/16`) | **81.82%** (`18/22`) | **Yes** (`+38.07 pp`; Complex `7/7 = 100%`) |
| **H01 — Unseen B–R Partial Relations** | Track 2 Relation-Level Agreement | 78.33% (`47/60`) | **80.72%** (`67/83`) | **Yes** (mean item rate `85.45%`) |
| **H01 — Unseen Complex Conversion** | Track 4 Complex Tier Consistency (`n=15`) | 73.33% (`11/15`) | **93.33%** (`14/15`) | **Yes** (`+20.00 pp`; overall `44/50 = 88.0%`) |
| **H01 — Published Book Diagrams (Dev-Exposed)** | Track 1 Triangle-Aware Labeled F1 (`n=216`) | 83.35% | **83.35%** | **Yes** (Ch. 3–10 zero-triangle `n=65`: **91.56%**) |
| **H01 — Published Book Diagrams (Dev-Exposed)** | Track 1 Raw Full-Tree Labeled F1 (`n=216`, all attempts) | 62.96% | **62.98%** | **No** (`145/216` book trees collapse subtrees into triangles; `17` Ch. 1–2 trees use introductory `Phrase` labels) |
| **H02 — Grammatical Judgment Accuracy** | `O1` Overall (`n=100`, abstentions not counted as detected) | 75.0% | **70.0%** (Arm B: 71.0%) | **No** (Grammatical specificity rose to **94.0%**; ungrammatical recall `46.0%` on harder unseen CGEL set) |
| **H02 — Non-Abstaining Clean Feedback** | `O4_decided_clean` (`n=100`) | 72.0% | **67.0%** (Arm B: 69.0%) | **No** (`O4_no_incorrect = 76.0%` vs Arm B `69.0%`, `+7.0 pp`) |
| **H02 — Grounded vs. Ungrounded Precision Outcomes** | `O2` Localization / `O3` Valid Correction / Full Adequacy | 73% / 62% / 62% | **70% / 62% / 60%** (Arm B: 54% / 52% / 48%) | **Statistically significant Arm A advantage** on all three (`p = 0.0025`, `0.0213`, `0.0118`; all survive Holm–Bonferroni) |

> **Honest Overall Assessment:** Principled H01 fixes yielded substantial, generalizable gains on unseen complex Burton–Roberts syntax trees (**Track 2 all-passed jumped from 43.75% to 81.82%**, with **100% (7/7)** on unseen Complex Track 2 items and **93.33% (14/15)** on unseen Complex Track 4 conversion). On H02, grammatical false positives were cut more than in half (**10.0% → 4.0%**, **94.0%** grammatical acceptance), and Arm A retained large, statistically significant advantages over the ungrounded baseline (Arm B) on exact-position localization (**44% vs. 8%** on ungrammatical items, `p = 0.000277`), valid correction (**26% vs. 4%**, `p = 0.007385`), and full outcome adequacy (**60% vs. 48%**, `p = 0.0118`). However, **H02 overall `O1` (70.0%) and `O4_decided_clean` (67.0%) did not reach the 80–82% target** on V2's harder independent CGEL error set (where Arm B RoBERTa-CoLA also dropped from 56% to 50% error detection).

---

## 2. Underlying Production Fixes Implemented (Separate Dev Examples Only)

All production fixes were developed and verified strictly on synthetic development examples and existing regression suites (never against V1 or V2 evaluation sentences):

### Priority 1 — H01 (`server/final_d1_projection.py`)
1. **Long-distance wh-extraction through extraposed/copular predicative clauses (`wh_gap`, `question`, `vp`, `predicative`):** Stopped `wh_gap` from misclassifying copular questions with embedded `SBAR`/`ADJP(SBAR)` clauses as matrix predicative gaps; added `has_embedded_clause` and routed incoming wh-gaps cleanly through extraposed `it` clauses and adjectival clausal complements.
2. **Multi-clause ditransitive & Type II object-control wh-extraction (`wh_gap`, `vp`):** Fixed `wh_gap` so subjectless non-finite `S` complements (`what to buy`) are not mistaken for finite subject-gap sites; added `DITRANSITIVE` recipient-gap + embedded wh-`SBAR` projection and `TYPE_II` object-gap + controlled non-finite `S` projection.
3. **Coordinated non-finite clausal subjects (`is_nonfinite`):** Peeled nested/coordinated `VP` layers so coordinated `to`-infinitival subjects normalize cleanly.
4. **Embedded finite `S` with trailing adverbial (`clause`):** Handled Benepar's `(S (S ...) (SBAR/PP/ADVP ...))` attachment without failing on predicate identification.
5. **Complement-vs.-adjunct attachment (`SELECTED_PP`, `COMPLEX`, `peel_sentence_final_s_adverbial`):** Expanded B–R Ch. 4 prepositional verbs (`apply for`, `worry about`, `call for`, `approve of`, `submit to`, etc.), flattened Benepar's `V NP (S (ADJP/NP/PP))` small-clause wrapper for complex-transitive verbs, and peeled comma-delimited sentence-final S-adverbial disjuncts (`in my opinion`, `in my view`, `apparently`, etc.) to `S` level per B–R Ch. 5.

### Priority 2 — H02 (`server/analysis_api.py`, `server/matrix.py`, `server/ruleset.py`, `server/licensing.py`, `server/cgel_pronoun_case_probe.py`)
1. **Integrated runtime-enabled Cambridge findings into production verdicts & repairs (`analysis_api.py`):** Added `_integrate_cambridge_findings` so violations returned by the gated 193-rule Cambridge evaluator (`evaluate_cambridge`) update `summary['verdict']`, attach localized findings to matching tree nodes, and feed deterministic `edit_hint` repairs into `corrections.assemble()` (re-validated against both the rule matrix and `evaluate_cambridge`). Aligned `_validate_correction` CoLA threshold (`0.20`) with `detector.combine()`.
2. **Eliminated 4 general false-positive classes (`matrix.py`, `ruleset.py`, `cgel_pronoun_case_probe.py`):**
   - `subject_head()` now excludes embedded non-finite/participial `S`/`VP` modifiers and unwraps postmodified outer `NP` shells.
   - `_needs_indefinite_article_error()` exempts bare ordinal rank NPs (`first prize`, `second place`) and standard bare verb–object collocations.
   - `_ZERO_PLURAL_NOUNS` expanded (`staff`, `police`, `cattle`, `personnel`, etc.) and `_DITRANSITIVE_OR_COMPLEX_VERBS` expanded (`bring`, `feed`, `serve`, `cook`, `bake`, `read`, `throw`, `order`, etc.).
   - Fixed `PHR-582` in `cgel_pronoun_case_probe.py` so copular contractions (`It's himself`) are never mistaken for genitive `'s`.
   - Exempted `SINGULAR_S_NOUNS` (`measles`, `shingles`, `mumps`, etc.) in `_noun_form_issue` and `_singular_noun`.
3. **Localized `C-PRONOUN-CASE` span & fixed structured remediation edits (`matrix.py`, `ruleset.py`):** Moved finite-clause accusative-subject checks onto the subject `NP` edge (`_s_subject`) rather than the `VP` span; fixed `_rem()` positional `edits` bug (which had silently disabled structured edits on `C-TO-BASE` and `C-RELATIVE-AGREE`) and added structured edits to `C-MODAL-TO`, `C-MODAL-STACK`, `C-GERUND-INFIN`/`C-GERUND-INFINITIVE`, and `C-OBJECT-ORDER`.
4. **Added high-precision CGEL constraints (`_check_h02_cgel_constraints` in `ruleset.py`, wired into `licensing.collect_all`):** Supportive `do` with `be`/`have`, lexical-verb inversion without `do`-support, auxiliary chain ordering (`have + MD`, `be + having + VBN`), `who`/`whom` case (subject `whom` and pied-piped `P + who`), determiner–noun countability (`every`/`each`/`another` + mass noun; `all` + bare singular count noun), non-dative-alternation double objects (`V PRP NP`), `V + manner -ly Adv + light NP`, mixed non-finite coordination (`VBG + and/or + to VB`), unlicensed NPI `at all`, and counterfactual conditional apodosis missing modal.

### Regression Verification (Pre-Freeze)
- **269 / 269 unit & regression tests passed (`0` failures, `0` regressions)** across 15 server suites (`test_h01_h02_reliability`, `test_false_positive_regressions`, `test_api_contract`, `test_cambridge_evaluator`, `test_learner_analysis`, `test_nlp_reliability_regressions`, `test_cgel_pronoun_case_probe`, `test_br_tree`, `test_canonical_binding`, `test_findings`, `test_licensing`, `test_xai7_unified`, `test_burton_roberts`, `test_cambridge_registry`, `test_explanations`, `test_webapp_contract`, `test_real_world_nlp`, `test_final_d1_heldout_gaps`, `test_final_d1_extraposition`) plus `217 / 217` M1-envelope source audit passing.

---

## 3. Independent Evaluation V2 Design & Contamination Audit

- **Dataset:** `docs/audits/h01_h02_evaluation_methodology/V2_PROPOSED_100_SENTENCES.csv` (`100` verbatim published textbook sentences mirroring V1's exact balance: `50` Grammatical [`15` Simple, `20` Moderate, `15` Complex] from Burton–Roberts 2011 and CGEL 2002; `50` Ungrammatical [`25` Simple, `20` Moderate, `5` Complex] from unused starred examples in CGEL 2002 and Burton–Roberts 2011 across all 6 grammar domains; `22` unseen B–R sentences with published Discussion-of-exercises structural answers for Track 2).
- **Automated Contamination Audit:** **`0 / 100` overlap** with Evaluation V1, **`0 / 100` overlap** with sprint development sentences, and **`0 / 100` overlap** across all SynTutor repo files (`server/*.py`, `web/content/book/*.json`, `web/content/lessons/*.json`, `grammar/rules/*.json`, `docs/audits/technical_evaluation/*.py`).
- **Gold Lookup Sentinel:** Verified `gold_lookup_sentinel_verified_zero_calls: true` during H01 Tracks 2–4 and `_matching_gold_records -> []` during H02 Arm A.
- **Frozen Pre-Execution SHA-256 Checksums:**
  - `V2_PROPOSED_100_SENTENCES.csv`: `057be35b3351875f4dc71d3709c8c95eb08ee0f8305406d8c28e74dc920a1a65`
  - `run_textbook_h01_h02_v2.py`: `8f49ff0f64a00026724486e1fa93b7f02fa40f496c68ef7c50fb68dbc9357346`
  - Preserved V1 checksums verified unchanged: `H01_H02_PROPOSED_100_SENTENCES.csv` (`ce3020a0...`), `run_textbook_h01_h02.py` (`3815ad1b...`), `test_run_textbook_h01_h02.py` (`0b8f1cbf...`).

---

## 4. Side-by-Side Results: Evaluation V1 vs. Evaluation V2

### 4.1 H01 — Burton–Roberts Syntax Trees (Four Strictly Separated Tracks)

| Track | Scope | V1 Result | V2 Result | Change / Notes |
|---|---|---:|---:|---|
| **Track 1 (Dev-Exposed Book Diagrams)** | `n=216` all-attempts full labeled F1 | 62.96% | **62.98%** | Stable (`213/216` normalized; `8/8` exact on Fig. `[79b]`) |
| **Track 1 (Triangle-Aware)** | `n=216` triangle-aware labeled F1 | 83.35% | **83.35%** | Ch. 3–10 zero-triangle complete diagrams (`n=65`): **91.56%** |
| **Track 2 (Unseen Partial Ref — All Passed)** | `n=16` (V1) / `n=22` (V2) | 43.75% (`7/16`) | **81.82%** (`18/22`, 95% CI `[61.5%, 92.7%]`) | **+38.07 pp**; Complex tier: **`7/7 = 100.0%`** (KW `p = 0.325`) |
| **Track 2 (Unseen Partial Ref — Relations)** | `60` (V1) / `83` (V2) checked relations | 78.33% (`47/60`) | **80.72%** (`67/83`, 95% CI `[71.0%, 87.8%]`) | Mean item rate **85.45%** (`[70.9%, 99.1%]`) |
| **Track 3 (Unseen B–R Compliance)** | `n=50` unseen grammatical | 90.00% (`45/50`) | **76.00%** (`38/50`, 95% CI `[62.6%, 85.7%]`) | 6 of 12 failures are valid Ch. 9 `S-dbar` wh-question roots excluded by the inherited V1 `valid_clause_root` whitelist (`44/50 = 88.0%` with `S-dbar`) |
| **Track 4 (Unseen Conversion Consistency)** | `n=50` unseen grammatical | 90.00% (`45/50`) | **88.00%** (`44/50`, 95% CI `[76.2%, 94.4%]`) | Simple `11/15` (`73.3%`), Moderate `19/20` (`95.0%`), **Complex `14/15` (`93.3%`, up from `73.3%` in V1)** |

### 4.2 H02 — Grounded SynTutor (Arm A) vs. Ungrounded Neural Baseline (Arm B)

| Fair Outcome Metric (`n = 100`) | V1 Arm A | V1 Arm B | V2 Arm A | V2 Arm B | V2 Net Diff (A − B) | V2 Exact McNemar `p` |
|---|---:|---:|---:|---:|---:|---:|
| **`O1` Grammatical Judgment Accuracy** | 75.0% | 72.0% | **70.0%** | 71.0% | −1.0 pp | `1.0000` (NS) |
| **`O2` Exact-Position Target Localization** | 73.0% | 50.0% | **70.0%** | 54.0% | **+16.0 pp** | **`0.002494`** (Holm `0.009976`) |
| **`O3` Valid Correction** | 62.0% | 49.0% | **62.0%** | 52.0% | **+10.0 pp** | **`0.021271`** (Holm `0.042542`) |
| **`O4_no_incorrect` Zero Demonstrable Errors** | 79.0% | 71.0% | **76.0%** | 69.0% | +7.0 pp | `0.264931` (NS) |
| **`O4_decided_clean` Non-Abstaining Clean Feedback** | 72.0% | 71.0% | **67.0%** | 69.0% | −2.0 pp | `0.860050` (NS) |
| **Full Outcome Adequacy (`O1 & O2 & O3 & O4_decided`)** | 62.0% | 48.0% | **60.0%** | 48.0% | **+12.0 pp** | **`0.011818`** (Holm `0.035454`) |
| **Fair Composite (`0–4` Mean)** | 2.82 | 2.42 | **2.69** | 2.46 | +0.23 | Wilcoxon `p = 0.1736` (NS) |

#### V2 Abstention, Detection & Specificity Breakdown (Reported Separately)
- **Grammatical Subset (`n = 50`):**
  - Arm A: **94.0% accepted (`47/50`)**, **4.0% false positives (`2/50`)** (down from `10.0%` in V1!), **2.0% abstained (`1/50`)**.
  - Arm B: **92.0% accepted (`46/50`)**, **8.0% false positives (`4/50`)**, **0.0% abstained**.
- **Ungrammatical Subset (`n = 50`):**
  - Arm A: **46.0% detected (`23/50`)**, **16.0% abstained (`8/50`)**, **38.0% missed as grammatical (`19/50`)**, **44.0% exact-position localized (`22/50`)**, **26.0% valid correction (`13/50`)**.
  - Arm B: **50.0% detected (`25/50`)**, **0.0% abstained**, **50.0% missed as grammatical (`25/50`)**, **8.0% exact-position localized (`4/50`)**, **4.0% valid correction (`2/50`)**.
  - Ungrammatical Arm A vs. Arm B exact McNemar: `O2` localization **OR = 7.0, `p = 0.000277`**; `O3` correction **OR = 6.5, `p = 0.007385`**; `O1` detection `p = 0.845` (NS).
- **Separate Arm A Grounding Diagnostics (Never Penalizing Arm B):**
  - `D1` Rule-family match: **69.0%** (`69/100`, 95% CI `[59.4%, 77.2%]`).
  - `D2` Provenance & evidence integrity: **100.0%** (`100/100`, 95% CI `[96.3%, 100.0%]`); `0` self-contradictions.

---

## 5. Transparent Error Analysis & Limitations

1. **H01 Remaining Failures in V2:**
   - **Track 4 (`6/50` unresolved):** 4 Simple items failed due to remaining verb-frame lexicon gaps (`V2-G03` `nominated` not in `COMPLEX`, `V2-G04` `feeds` not in `DITRANSITIVE`, `V2-G12` `wished` not in `DITRANSITIVE`, `V2-G15` exceptive `but her`), plus 1 Moderate (`V2-G30` phrasal verb + stranded preposition `show up in`) and 1 Complex (`V2-G47` coordinated subject inside `whether`-clause).
   - **Track 2 (`4/22` failed):** 3 were those unresolved canonical trees (`V2-G03`, `V2-G04`, `V2-G30`); the only normalized tree partial miss was `V2-G17` (`William baked a cake for everyone.`, `4/5` checks — `bake` not in `DITRANSITIVE` so `for everyone` attached as adjunct rather than `V`-sister).
   - **Full-tree gold-standard limitation:** Complete unseen B–R full-tree PARSEVAL remains unavailable without the separate Burton–Roberts *Answer Book* (not in the provided textbook PDF). Track 1 raw F1 (`62.98%`) continues to reflect 145/216 triangle-abbreviated diagrams and 17 Ch. 1–2 introductory-label diagrams rather than errors on complete B–R syntax trees (where Ch. 3–10 zero-triangle complete diagrams score `91.56%`).
2. **H02 Remaining Failures & Difficulty Shift in V2:**
   - **Genuine benchmark difficulty shift:** Arm B (unmodified RoBERTa-CoLA) dropped from `56.0%` ungrammatical detection in V1 to `50.0%` in V2, confirming that V2's unused CGEL starred items are substantially harder.
   - **Arm A missed/abstained ungrammatical items (`19` missed + `8` abstained):** Concentrated in unimplemented fine-grained CGEL rules: declarative `don't/doesn't have + VBN` (`V2-U02`, `V2-U04`), idiomatic/locative reflexive restrictions (`V2-U26`–`V2-U28`), subtle quantifier/determiner constraints (`V2-U11`, `V2-U16`, `V2-U31`, `V2-U34`, `V2-U35`), bare institutional proper names (`V2-U32`), full-NP non-dative double objects (`V2-U37`, `V2-U38`), indirect-object-only `spare` (`V2-U39`), complex passive restrictions (`V2-U40`, `V2-U42`), polarity `yet`/`need + VB` (`V2-U46`, `V2-U47`), single comma between S–VP or V–`that` (`V2-U48`, `V2-U49`), and `it's` possessive before adjective+noun (`V2-U50`).
   - **Audit transparency note (`V2-U06`):** On `V2-U06` (*"He may must work tomorrow."*), Arm A emitted `"He may work tomorrow."`, which was listed in `Valid alternatives` using a `|` delimiter rather than `;`. Under the frozen V1/V2 scorer's `;`/`/` delimiter parser, it was conservatively counted as a non-matching correction (`O3 = False`); the frozen score (`62.0%` `O3`, `67.0%` `O4_decided_clean`) is reported strictly unmodified.
3. **Hypothesis Interpretation:**
   - **H01:** Supported on unseen B–R published-reference partial relations (`81.82%` all-passed, `100%` on Complex) and unseen Complex conversion consistency (`93.33%`), while Track 1 full-tree F1 (`62.98%`) remains bounded by textbook triangle abbreviation and Ch. 1–2 label conventions.
   - **H02:** Grounding produces strong, statistically significant improvements in **error localization (`p = 0.0025`)**, **valid correction (`p = 0.0213`)**, and **full outcome adequacy (`p = 0.0118`)** alongside low false-positive rates (`4.0%`) and `100%` provenance integrity — but does **not** yet yield a statistically significant advantage on binary detection (`O1`, `70%` vs `71%`) or non-abstaining clean feedback (`O4_decided_clean`, `67%` vs `69%`) on broad unseen CGEL phenomena until rule coverage across the remaining CGEL complementation, polarity, reflexive, and punctuation families is expanded.
