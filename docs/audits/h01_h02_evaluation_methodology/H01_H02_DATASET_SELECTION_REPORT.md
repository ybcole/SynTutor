# H01 and H02 Dataset Selection Report, Power Analysis, and Methodology Justification

**Project:** SynTutor: An Explainable AI-Based Framework for Syntax Tree-Driven Grammar Analysis and Learning Using NLP  
**Date Prepared:** 2026-11-22  
**Companion Dataset:** [H01_H02_PROPOSED_100_SENTENCES.csv](file:///Users/kiyel/Desktop/SynTutor/docs/audits/h01_h02_evaluation_methodology/H01_H02_PROPOSED_100_SENTENCES.csv)  
**Evaluation Status:** Dataset and methodology prepared **blind to SynTutor's outputs**; final evaluation has **not** been executed.

---

## 1. Executive Summary of Dataset Composition

| Dimension | Breakdown | Count |
| :--- | :--- | ---: |
| **Total Proposed Evaluation Sentences** | Balanced grammatical / ungrammatical corpus | **100** |
| **Grammatical Sentences (`G01`–`G50`)** | Eligible for H01 (pending independent gold B–R tree verification) + H02 grammatical controls | **50** |
| — *Simple (`G01`–`G15`)* | Single finite clause, 0 subordinate clauses, all 6 B–R verb complementation classes | 15 |
| — *Moderate (`G16`–`G35`)* | Multi-aux chains, passive, inversion/wh-fronting, phrasal verbs, adverbial layering, coordination, or 1 shallow subordinate clause | 20 |
| — *Complex (`G36`–`G50`)* | Depth $\ge 2$ clausal embedding, long-distance wh-extraction, non-finite raising/control stacks, extraposed subjects, or combined movement + subordination | 15 |
| **Ungrammatical Sentences (`U01`–`U50`)** | Eligible for H02 violation & grounded-explanation evaluation (`H01 eligibility = No`) | **50** |
| — *Verb Form, Auxiliaries & Modals (`U01`–`U10`)* | Preterite/participle, `do`-support, double modal, auxiliary ordering, modal defectiveness | 10 |
| — *Subject–Verb Agreement (`U11`–`U19`)* | Simple, intervening PP, coordinated, disjunctive, distributive, collective, plural-only, singular `-s`, existential `there` | 9 |
| — *Pronoun Case, Genitives & Reflexives (`U20`–`U28`)* | Matrix/embedded subject, direct/prepositional object, `for`-infinitival, `who`/`whom`, dependent `my`, spatial reflexive | 9 |
| — *Determiners, Articles & Count/Non-Count (`U29`–`U35`)* | Bare singular count subject, `every`/`all`/`another` mismatches, fused-head `the`/`every`, `a`/`an` silent-h liaison | 7 |
| — *Complementation, Valency & Word Order (`U36`–`U43`)* | `enjoy` + `to`-inf, `borrow`/`explain` double-object, light-NP shift, verb-object adverb/enough, passive `make`, active-only `befall` | 8 |
| — *Clauses, Polarity, Comparatives, Coordination & Punctuation (`U44`–`U50`)* | Remote conditional modal, NPI `at all`, omitted subject relativiser, `fewer` + non-count, non-parallel coordination, `however` comma splice, `your's` | 7 |
| **Origin Provenance** | Verbatim published textbook originals (`96`) vs. explicitly labeled researcher minimal-pair variants (`4`: `U11`, `U19`, `U35`, `U42`) | **96 / 4** |
| **Direct Minimal Pairs (`P01`–`P19`)** | Exact grammatical (`G`) + ungrammatical (`U`) counterparts (`38` rows total) | **19 pairs** |
| **Repository-Wide Contamination Check** | Case-insensitive substring check across all SynTutor code, book trees, lessons, assessments, rules, and tests | **0 / 100 hits** |

---

## 2. Burton–Roberts-Refined Difficulty Classification Criteria

Sentence difficulty in `H01_H02_PROPOSED_100_SENTENCES.csv` is defined **strictly by Burton–Roberts (2011) syntactic structure**, **never by word count** (a 12-word simple clause with long NPs can be structurally simpler than a 7-word sentence with long-distance wh-extraction or non-finite raising):

| Stratum | Structural Inclusion Criteria (Burton–Roberts Ch. 1–10) | Structural Exclusion Criteria | Examples in Dataset |
| :--- | :--- | :--- | :--- |
| **Simple** | Single finite clause (`S`); `0` subordinate clauses; `0` clause-level coordination; canonical declarative word order; at most one basic auxiliary (`have`/`be`) or basic PP/AP modifier; spans all 6 basic B–R verb complementation types (`[intrans]`, `[trans]`, `[ditrans]`, `[intens]`, `[complex]`, `[prep]`, Ch. 4). | No multi-auxiliary chains, no passive or subject–auxiliary inversion movement, no wh-fronting, no subordinate clauses, no VP/clause coordination. | `G01` (*Hot air rises.*), `G03` (*Richard promised me his spaghetti machine.*), `G06` (*The girl in the palace dyed her hair deep purple.*), `G14` (*The police arrested him on Friday.*) |
| **Moderate** | Single finite clause exhibiting **one or more intermediate Ch. 5–7/9 operations** (multi-auxiliary chains, passive object-to-subject movement, subject–auxiliary inversion to `C`, single-clause wh-fronting, split phrasal-verb particle, layered VP/S-adverbials, possessive/coordinated NPs or VPs) **OR** a **single shallow subordinate clause** (depth `1`: one finite `S'` complement/adverbial, one simple restrictive relative, or one simple control infinitival). | No depth $\ge 2$ recursive clausal embedding; no long-distance wh-extraction across clause boundaries; no stacked non-finite clauses. | `G16` (*Murdstone brought the child up too strictly, in my opinion.*), `G22` (*Could Olaf be being investigated by the Intelligence Agency?*), `G25` (*What shall we feed the cat today?*), `G27` (*Morgan promised Bill to give it a good review.*) |
| **Complex** | **Depth $\ge 2$ clausal embedding** (`2+` subordinate clauses, e.g., `S1 > S2 > S3`), **long-distance wh-extraction** across a subordinate clause boundary, **stacked non-finite raising/control/passive-participial clauses**, **clausal subjects / extraposed subjects with further embedding**, or **combined movement + subordination** (Ch. 8–10). | Any sentence analyzable as a single clause or a single shallow embedded clause without cross-clause extraction. | `G37` (*Why Max didn't answer the accusation that he had cheated is a mystery.*), `G39` (*The Doge of Venice appears to have been eager to join the Crusade.*), `G43` (*What do you think they put in that soup?*), `G45` (*Who did Sarah try to tell what to say?*) |

*(Note: Ungrammatical items `U01`–`U50` also carry a structural complexity tag — `25` Simple, `20` Moderate, `5` Complex — reflecting the underlying clause complexity in which the grammatical error occurs, enabling secondary error-complexity inspection in H02.)*

---

## 3. Sample-Size Justification and A Priori Statistical Power Analysis

> [!WARNING]
> **Methodological Honesty:** A sample size of `100` sentences (`50` grammatical / `50` ungrammatical) is **not universally sufficient for every statistical test**. The exact calculations below specify precisely where `N = 100` is adequately powered and where it is underpowered, so thesis claims stay strictly within statistical evidence.

### 3.1 H01 Estimation Precision (Wilson 95% Confidence Intervals)

Computed via exact Wilson score intervals ($z = 1.96$):

| Sample Size ($n$) | Role in H01 | Wilson 95% CI at $p = 0.80$ (Half-Width) | Wilson 95% CI at $p = 0.50$ (Worst-Case Half-Width) |
| ---: | :--- | :--- | :--- |
| `15` | Simple stratum / Complex stratum | `[0.548, 0.930]` ($\pm 19.1$ pp) | `[0.301, 0.752]` ($\pm 22.5$ pp) |
| `20` | Moderate stratum | `[0.584, 0.919]` ($\pm 16.8$ pp) | `[0.299, 0.701]` ($\pm 20.1$ pp) |
| `30` | Recommended minimum per stratum for high-power binary comparison | `[0.627, 0.905]` ($\pm 13.9$ pp) | `[0.332, 0.668]` ($\pm 16.8$ pp) |
| **`50`** | **Total H01 Grammatical Corpus (`G01`–`G50`)** | **`[0.670, 0.888]` ($\pm 10.9$ pp)** | **`[0.366, 0.634]` ($\pm 13.4$ pp)** |

### 3.2 H01 Between-Stratum Power (Simple vs. Complex Binary Accuracy, $\alpha = 0.05$)

| True Accuracy Gap ($p_{\text{simple}}$ vs. $p_{\text{complex}}$) | Power at $n = 15$ / stratum *(Proposed)* | Power at $n = 30$ / stratum | Power at $n = 50$ / stratum |
| :--- | ---: | ---: | ---: |
| `0.90` vs. `0.50` ($\Delta = 40$ pp) | `0.684` | `0.943` | `0.996` |
| `0.85` vs. `0.50` ($\Delta = 35$ pp) | `0.537` | `0.843` | `0.972` |
| `0.80` vs. `0.50` ($\Delta = 30$ pp) | `0.401` | `0.692` | `0.894` |
| `0.80` vs. `0.60` ($\Delta = 20$ pp) | `0.217` | `0.391` | `0.590` |
| `0.85` vs. `0.70` ($\Delta = 15$ pp) | `0.161` | `0.282` | `0.434` |

**Interpretation for H01:** At `n = 15 / 20 / 15` (`N = 50`), **binary** exact-match comparisons between individual strata are underpowered (`< 0.70` even for a 40 pp gap). Therefore, **continuous per-sentence Labeled Constituent F1 (PARSEVAL)** — which extracts finer-grained structural signal from every constituent in every tree — is designated as the primary inferential metric for stratum comparison (via Kruskal–Wallis + Jonckheere–Terpstra trend test), while binary stratum rates are reported descriptively with Wilson 95% CIs. Expanding to $n = 30$ per stratum ($N = 90$ grammatical trees) is explicitly noted as a future-work recommendation if greater binary between-stratum power is desired.

### 3.3 H02 Exact Two-Sided McNemar Power ($\alpha = 0.05$)

Computed by exact enumeration over all discordant-pair counts $m = n_{10} + n_{01} \sim \text{Binomial}(N, p_{10} + p_{01})$:

| True Paired Effect Scenario ($p_{10}$ Grounded wins, $p_{01}$ Ungrounded wins) | Power at $N = 50$ *(Subgroup only)* | **Power at $N = 100$ *(Proposed Total)*** | Power at $N = 150$ | Power at $N = 200$ |
| :--- | ---: | ---: | ---: | ---: |
| Large (`+20` pp net: $p_{10}=0.25, p_{01}=0.05$) | `0.699` | **`0.961`** | `0.997` | `1.000` |
| Moderate-Large (`+15` pp net: $p_{10}=0.20, p_{01}=0.05$) | `0.478` | **`0.837`** | `0.960` | `0.992` |
| Moderate (`+10` pp net: $p_{10}=0.15, p_{01}=0.05$) | `0.241` | **`0.544`** | `0.746` | `0.875` |
| Small-Moderate (`+8` pp net: $p_{10}=0.12, p_{01}=0.04$) | `0.172` | **`0.436`** | `0.633` | `0.777` |
| Small (`+5` pp net: $p_{10}=0.10, p_{01}=0.05$) | `0.069` | **`0.178`** | `0.276` | `0.373` |

**Interpretation for H02:** At `N = 100`, an exact McNemar test is **well powered (`83.7%`–`96.1%`)** to detect moderate-to-large reductions (`+15` to `+20` pp) in unsupported/incorrect feedback — the magnitude expected when comparing a deterministic rule-grounded pipeline against an ungrounded baseline — while remaining honest that smaller effects (`+5` to `+10` pp) or subgroup-only (`N = 50`) binary comparisons have `< 55%` power and benefit from the companion paired Wilcoxon signed-rank test on the 0–12 ordinal rubric composite.

---

## 4. Inventory of Published Textbook References vs. Unverified Structural Items

Under the finalized **textbook-based evaluation decision** (using published Burton–Roberts and Cambridge answers directly without recruiting additional reviewers and without inventing missing trees):

| Subset | Count | Published Reference Available in Attached PDFs? | Exact Objective Evaluation Scope |
| :--- | ---: | :--- | :--- |
| **H02 Ungrammatical Items (`U01`–`U50`)** | 50 | **Yes (`50/50`)** — `46` verbatim starred (`*`) textbook sentences + `4` rule-verified minimal-pair variants with exact Ch./§/p. locators | **Ready now:** Full 5-metric objective H02 scoring (verdict, span overlap, multi-alternative correction, rule-family match, verifiable evidence integrity) across Arm A vs. Arm B. |
| **H02 Grammatical Controls (`G01`–`G50`)** | 50 | **Yes (`50/50`)** — all `50` verbatim grammatical originals verified in Burton–Roberts (2011) (`31`) and CGEL (2002) (`19`) | **Ready now:** Full 5-metric objective H02 grammatical-control scoring (false-positive & grounding check) across Arm A vs. Arm B. |
| **H01 Unseen Partial-Reference Items** | 16 of 50 (`G01`–`G06`, `G16`–`G17`, `G25`–`G27`, `G36`–`G40`) | **Yes (partial published answers)** — Burton–Roberts' *Discussion of exercises* (pp. 82, 105, 218–220, 249–251) provides explicit functional brackets, verb subcategories, complement-vs.-adjunct attachments, wh/relative derivations, or ACAs | **Ready now:** Track 2 Unseen Published-Reference Agreement (strictly limited to book-established relations) + Track 3 B–R Rule Compliance + Track 4 Conversion Consistency. |
| **H01 Unseen Prompt-Only / CGEL Grammatical Items** | 34 of 50 (`15` B–R Further Exercises + `1` B–R in-text + `18` CGEL grammatical) | **Sentence grammaticality verified; no printed B–R phrase marker in attached PDF** (companion *Answer Book for the Further Exercises* not included) | **Ready now (scoped):** Track 3 B–R Rule Compliance + Track 4 Conversion Consistency **only**; **zero fabricated gold trees**. |
| **H01 Published Full-Tree Reference Diagrams (Historical Book Set)** | `216` active (`web/content/book/`) + `1` (`p. 239 [79b]`) | **Yes (`85` complete zero-triangle + `161` triangle-abbreviated)** — **EXPLICITLY DISCLOSED AS DEVELOPMENT-EXPOSED (`Previous development use = Yes`)** | **Ready now (descriptive track):** Track 1 Full-Tree & Triangle-Aware PARSEVAL F1 with zero-hit book-lookup sentinel. |

---

## 5. Contamination-Check Procedure and Verification Result

To guarantee that none of the 100 proposed evaluation sentences were exposed during SynTutor's engineering, debugging, or prior evaluations, a two-stage automated audit was executed:

1. **Structured Index Check (`dev_exposure.json`):** Extracted `8,219` unique normalized strings across `web/content/book/*.trees.json`, `evaluation/`, `docs/audits/technical_evaluation/`, `docs/lessons/`, `docs/assessments/`, `server/test_*.py`, `scripts/audit_rules.py`, `scripts/test_*.py`, `grammar/rules/*.json`, and `grammar/runtime_registry.json`. Initial draft screening caught `3` hits (`Did she be working?`, `Be not late.`, `He brought in it.`), which were immediately replaced.
2. **Repository-Wide Substring Scan:** Scanned **every** `.py`, `.js`, `.ts`, `.json`, `.jsonl`, `.csv`, `.md`, `.txt`, and `.html` file across the entire SynTutor workspace (excluding `.git`, `.venv`, `node_modules`, `repomix-output.xml`, and this new methodology folder). That deeper scan caught `5` additional overlaps with `web/content/lessons/cambridge-authored/` and `server/test_cgel_word_order_probe.py` (`He has not seen it.`, `A number of spots have appeared.`, `He saw not it.`, `Saw he it?`, `She perused.`), all of which were replaced with fresh verified textbook items.
3. **Final Verified Contamination Count:** **`0 / 100` repository-wide substring hits** and **`0` duplicate sentences**.

---

## 6. Limitations and Bias-Reduction Measures

1. **No Unseen Complete Printed B–R Trees Without the Separate *Answer Book*:** Because all `252` diagrams in `Syntax_Reference_Chapters_1-11-1.pdf` (save the previously probed `[79b]`) are already in `web/content/book/`, H01 separates (a) development-exposed full-tree PARSEVAL (`216+1`), (b) unseen published partial-reference agreement (`16/50`), and (c) unseen B–R rule compliance + conversion consistency (`50/50`), never fabricating gold trees for the `34` prompt-only/CGEL sentences.
2. **Free-Text Explanation Qualities Outside Automated Proof:** Automated H02 scoring evaluates objective verdict, span overlap, multi-alternative correction, rule-family alignment, and structured provenance consistency without exact wording matching, but cannot establish free-text pedagogical clarity or catch subtle semantic flaws in prose carrying a valid rule ID.
3. **Comparable Internal Grounded vs. Ungrounded Scope:** Arm A (rule-grounded SynTutor) vs. Arm B (ungrounded CoLA + perturbation baseline inside SynTutor) uses identical inputs and comparable system components without external LLMs; claims are scoped strictly to structured rule grounding within SynTutor.
4. **Cambridge Governance Status:** SynTutor's `193` runtime-enabled Cambridge rules currently operate under `owner_waiver: true, independent_review: false`, which must be disclosed in Chapter IV.
5. **Blind Selection Guarantee:** SynTutor was **not executed** on any candidate sentence during dataset selection, ensuring zero cherry-picking by system performance.
