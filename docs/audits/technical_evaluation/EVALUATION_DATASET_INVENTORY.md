# SynTutor Evaluation Dataset Inventory & Provenance Audit

**Repository commit:** `d5aeaf5de98c45abbf2d97f19a6092a24d4ba44c` (branch `main`)  
**Audit date:** 2026-11-20  
**Scope:** Complete inventory of all external benchmark corpora, internal repository evaluation corpora, textbook syntax-tree fixtures, and development/regression datasets present in the SynTutor repository.

---

## 1. Classification of Dataset Authority

To maintain strict scientific validity across Sections 5.1.1–5.1.3, every dataset in the repository is classified into one of four provenance tiers:

| Tier | Classification | Permitted Academic Role |
|---|---|---|
| **Tier 1** | **Independent External Annotated Benchmarks** | Primary empirical evaluation for Section 5.1.1 (with explicit CoLA in-distribution disclosure for the hybrid neural detector). |
| **Tier 2** | **Independently Published Textbook Reference Trees** | Primary structural reference for Section 5.1.2 **only when SynTutor's exact-IMG lookup table is bypassed**; lookup-enabled runs are reported strictly as source-fixture compliance. |
| **Tier 3** | **Internal Repository / AI-Authored Corpora** | Secondary diagnostic and coverage measurement; explicitly distinguished from unseen independent test data. |
| **Tier 4** | **Disqualified / Non-Independent / Development Artifacts** | Excluded from independent accuracy claims (e.g., adapter-generated drafts, development probes, unreviewed candidates). |

---

## 2. Section 5.1.1 — Grammar Error Detection Datasets

### 2.1 Tier 1: Independent External NLP Benchmarks (`benchmarks/`)

Fetched via [`scripts/fetch_benchmarks.py`](../../../scripts/fetch_benchmarks.py) from public HuggingFace benchmarks and stored as normalized tab-separated files (`category`, `label`, `sentence`):

| File | Total Items | Grammatical (`good`) | Ungrammatical (`bad`) | Categories / Paradigms | External Source & Citation | Contamination / Independence Audit |
|---|---:|---:|---:|---:|---|---|
| [`benchmarks/blimp.tsv`](../../../benchmarks/blimp.tsv) | **2,010** | 1,005 | 1,005 | 67 paradigms (15 pairs each; grouped into 10 families) | `nyu-mll/blimp` — Warstadt et al. (2020), *BLiMP: The Benchmark of Linguistic Minimal Pairs for English* | **Uncontaminated independent test set.** Neither SynTutor's deterministic rules nor `textattack/roberta-base-CoLA` was trained on BLiMP. |
| [`benchmarks/jfleg.tsv`](../../../benchmarks/jfleg.tsv) | **400** | 200 | 200 | 1 (`jfleg` L2 learner writing + 1st human reference correction) | `jhu-clsp/jfleg` validation split — Napoles et al. (2017), *JFLEG: A Fluency Corpus and Benchmark for Grammatical Error Correction* | **Uncontaminated independent L2 learner test set.** Natural non-native English errors (spelling, agreement, articles, verb forms, syntax, fluency). |
| [`benchmarks/cola.tsv`](../../../benchmarks/cola.tsv) | **400** | 274 | 126 | 1 (`cola` linguistic acceptability) | `nyu-mll/glue` (`cola` validation split) — Warstadt et al. (2019), *Neural Network Acceptability Judgments* | **Mixed caveat:** Independent for **Rules-Only** mode. **In-distribution for Hybrid mode** because `server/detector.py` uses `textattack/roberta-base-CoLA` (fine-tuned on CoLA). Reported separately from the strict uncontaminated 2,410-sentence external slice (`blimp` + `jfleg`). |
| **Combined External Total** | **2,810** | **1,479** | **1,331** | **69** | BLiMP + JFLEG + CoLA | Reported both as **Strict Uncontaminated External (n = 2,410: BLiMP + JFLEG)** and **All External (n = 2,810)**. |

### 2.2 Tier 3: Internal Repository Grammar Corpora (`evaluation/`)

These files were authored within the SynTutor project during Cambridge CGEL rule extraction and development. They **must not** be presented as unseen external test benchmarks:

| File | Total Records | Sentence-Level | Phrase-Level | Authorship / Provenance | Overlap & Evaluation Role |
|---|---:|---:|---:|---|---|
| [`evaluation/grammatical_sentences.json`](../../../evaluation/grammatical_sentences.json) | 337 | 281 | 56 | `origin: ai_authored` (337/337), keyed to Cambridge CGEL rule IDs across 7 domains | Internal diagnostic corpus (`internal_sentences`, sentence-level subset n = 281). |
| [`evaluation/ungrammatical_sentences.json`](../../../evaluation/ungrammatical_sentences.json) | 56 | 45 | 11 | `origin: ai_authored` (54), `origin: book` (2), keyed to Cambridge CGEL constraint IDs | Internal diagnostic corpus (`internal_sentences`, sentence-level subset n = 45; combined sentence-level n = 326). |
| [`evaluation/minimal_pairs.json`](../../../evaluation/minimal_pairs.json) | 26 pairs (52 items) | mixed | mixed | Derived subset of the two files above: **26/26** grammatical and **26/26** ungrammatical items appear in `grammatical_sentences.json` / `ungrammatical_sentences.json` | Internal contrastive diagnostic set (`internal_minimal_pairs`, n = 52). Evaluated separately; never merged into external totals. |

### 2.3 Tier 4: Candidate / Single-Construction / Development Corpora (Not Used as General Benchmark Gold)

| File | Records | Provenance & Status | Reason Excluded from Primary General Metrics |
|---|---:|---|---|
| [`evaluation/cgel_ch03_candidate_corpus.json`](../../../evaluation/cgel_ch03_candidate_corpus.json) | 277 | `authority: SOURCE_EXTRACTED_CANDIDATES_NOT_GOLD_ADJUDICATED`, `runtime_status: not_enabled` | Unadjudicated candidate probes for disabled Chapter 3 rules. |
| [`evaluation/cgel_passive_make_evaluation.json`](../../../evaluation/cgel_passive_make_evaluation.json) | 28 | Frozen single-construction (`CLS-357`) probe set | Narrow single-rule development benchmark. |
| [`evaluation/cgel_passive_make_modifiers_heldout.json`](../../../evaluation/cgel_passive_make_modifiers_heldout.json) | 22 | Frozen single-construction (`CLS-357`) modifier probe set | Narrow single-rule development benchmark. |
| [`evaluation/xai0_development_cases.json`](../../../evaluation/xai0_development_cases.json) | 116 | `review_status: NOT_HUMAN_ADJUDICATED`, `purpose: development probes` | Explicitly marked development probes, not gold data. |
| [`artifacts/syntutor-stress-report.json`](../../../artifacts/syntutor-stress-report.json) | 183 | Development stress-test report (`scripts/stress_test_syntutor.py`) | Development regression/stress corpus, not independent test data. |

---

## 3. Section 5.1.2 — Syntax Tree Reference Datasets

| Source | Total Records | Complete Evaluable Trees | Provenance & Verification Status | Role in Section 5.1.2 |
|---|---:|---:|---|---|
| [`web/content/book/ch01.trees.json`](../../../web/content/book/ch01.trees.json) – [`ch10.trees.json`](../../../web/content/book/ch10.trees.json) | 252 records (224 `IMG` with sentence + tree) | **216** complete grammatical sentence-aligned `IMG` trees (excluding 6 intentionally incorrect contrast examples, 1 legacy V1 `Sentence` label in Ch2+, and 1 partial subtree fixture) | **Tier 2 (Published Textbook Authority):** Transcribed from printed page figures of Noel Burton-Roberts, *Analysing Sentences* (3rd ed., Pearson, 2011; ISBN 9781408233740). | **Primary Structural PARSEVAL Reference** under **lookup-bypassed** `normalize_benepar_candidate()` (FINAL-D1 and Ch2 V2). Lookup-enabled `build_canonical_analysis()` is reported separately strictly as memorized fixture compliance (`EXACT_IMG_GOLD_REFERENCE`). |
| [`web/content/lessons/course.json`](../../../web/content/lessons/course.json) | 31 lessons | **10** worked-example trees (`br-01` – `br-10`) | **Tier 3 (AI Source-Reviewed Curriculum):** Metadata states `reviewed_by: "Codex — scoped AI source review; not human instructor sign-off"`. | Secondary diagnostic PARSEVAL check; explicitly labeled as AI-reviewed curriculum worked examples, **not** human-certified gold. |
| [`evaluation/br_final_d1_gold.json`](../../../evaluation/br_final_d1_gold.json) & [`evaluation/final_d1_heldout_sentences.json`](../../../evaluation/final_d1_heldout_sentences.json) | 20 entries | 0 independent gold trees (20 raw sentences) | **Tier 4 (DISQUALIFIED AS GOLD):** File header states `status: "AI_DRAFT_OWNER_WAIVER"`, `independently_verified: false`, `provenance: "Generated from repository held-out sentences and the current FINAL-D1 adapter. Owner waived human review on 2026-11-14. This is not independent gold and must not be cited as independent certification."` | **Disqualified from PARSEVAL accuracy.** Used only to verify non-crash normalization coverage on the 20 raw sentences. |
| External Penn Treebank (`nltk.corpus.treebank` / WSJ) | **0 (Not installed)** | **0** | Checked local NLTK search paths: `Resource 'treebank' not found`. | **Blocked / Unmeasured.** Raw Benepar-vs-PTB PARSEVAL cannot be measured locally without installing an external PTB gold corpus; SynTutor's own Benepar output is **never** substituted as reference gold. |
| External Benchmark Coverage Corpus (`benchmarks/*.tsv`) | 2,810 sentences | 2,810 unparsed input sentences (no gold trees) | BLiMP + JFLEG + CoLA | Used strictly for **Tree Generation & B-R Canonical Normalization Success Rate** and JSON-schema validity coverage (not PARSEVAL accuracy). |

### Breakdown of Burton-Roberts Textbook Records (`web/content/book/ch01..ch10.trees.json`)

| Chapter | Total Records in JSON | `IMG` with Sentence & Tree | Complete Grammatical Aligned Trees Used |
|---|---:|---:|---:|
| Ch 1 (`V1`) | 15 | 10 | 7 |
| Ch 2 (`V2`) | 21 | 16 | 15 |
| Ch 3 (`V3`) | 19 | 19 | 19 |
| Ch 4 (`V4`) | 15 | 15 | 15 |
| Ch 5 (`V5`) | 23 | 23 | 23 |
| Ch 6 (`V6`) | 26 | 26 | 26 |
| Ch 7 (`V7`) | 62 | 46 | 46 |
| Ch 8 (`V8`) | 33 | 33 | 29 |
| Ch 9 (`V9`) | 21 | 20 | 20 |
| Ch 10 (`V10`) | 17 | 16 | 16 |
| **Total** | **252** | **224** | **216** |

*(Exact per-chapter complete IMG counts verified during execution: Ch1 = 6, Ch2 = 13, Ch3 = 19, Ch4 = 15, Ch5 = 22, Ch6 = 26, Ch7 = 46, Ch8 = 33, Ch9 = 20, Ch10 = 16; total = 216; excluded = 28 non-IMG/missing + 6 intentionally incorrect contrast examples + 1 partial subtree + 1 legacy V1 Sentence label = 36.)*

---

## 4. Executed Fast-Track Stratified Evaluation Sample Sizes

To obtain reproducible, verified measurements without confusing subset metrics with full-dataset claims, the executed evaluation harness ([`run_technical_evaluation.py`](./run_technical_evaluation.py)) evaluated the following exact slices:

### 4.1 Section 5.1.1 — Grammar Error Detection (`RAW_PREDICTIONS.csv`, n = 476 Executed)

| Executed Slice | Executed n | Source Full Corpus Size | Provenance Tier | Selection Method |
|---|---:|---:|---|---|
| `blimp_stratified` | **240** (120 good / 120 bad) | 2,010 | Tier 1 (External Independent) | Deterministic strided sampling: 8 core grammatical families × 15 minimal pairs |
| `jfleg_stratified` | **80** (40 bad / 40 good) | 400 | Tier 1 (External Independent) | Deterministic strided sampling: 40 of 200 L2 learner/reference pairs |
| **Strict Uncontaminated External** | **320** | **2,410** | **Tier 1 (Zero CoLA overlap)** | **`blimp_stratified` + `jfleg_stratified`** |
| `cola_stratified` | **80** (40 good / 40 bad) | 400 | Tier 1 (Hybrid CoLA caveat) | Deterministic strided sampling; reported separately from strict uncontaminated slice |
| **All External Combined** | **400** | **2,810** | **Tier 1** | **Stratified subset across all 3 external benchmarks** |
| `internal_minimal_pairs` | **52** (26 pairs) | 52 | Tier 3 (Internal AI-authored) | Full census (`evaluation/minimal_pairs.json`) |
| `internal_rapid_audit_24` | **24** | 24 | Tier 3 (Internal audit/lesson) | Full census (`RAPID_CROSS_COMPONENT_CONSISTENCY_AUDIT.md`) |

### 4.2 Section 5.1.3 — Explainable AI (`n = 120` Full `api.build_payload()` Executions)

| Stratum | Count | Provenance Tier | Selection Method |
|---|---:|---|---|
| External BLiMP (6 families: SVA, determiner agreement, verb forms, pronoun case/binding, argument structure, filler-gap) | 36 | Tier 1 (External Independent) | First 3 pairs (6 sentences) per family from `blimp_stratified` |
| External JFLEG (L2 learner + human correction pairs) | 12 | Tier 1 (External Independent) | First 6 pairs (6 ungrammatical / 6 grammatical) from `jfleg_stratified` |
| External CoLA (general linguistic acceptability) | 12 | Tier 1 (External; CoLA hybrid caveat) | First 6 grammatical + 6 ungrammatical from `cola_stratified` |
| Internal Minimal Pairs (`evaluation/minimal_pairs.json`) | 36 | Tier 3 (Internal AI-authored) | First 18 minimal pairs |
| Rapid Cross-Component Consistency Audit cases (`docs/audits/RAPID_CROSS_COMPONENT_CONSISTENCY_AUDIT.md`) | 24 | Tier 3 (Internal audit/lesson cases) | Complete census (all 24 representative & Cambridge lesson sentences) |
| **Total Full-Payload XAI Audit Corpus** | **120** | **60 External + 60 Internal** | **All 120 executed through unmodified `api.build_payload()`** |

### 4.3 Human-Rated Explanation Assessments

| Artifact | Completed Human Ratings | Independent Raters | Inter-Rater Agreement | Status |
|---|---:|---:|---|---|
| Repository prior audits (`docs/reports/*`, `sources/cambridge/reviews/*`) | **0** | **0** | Not applicable | Confirmed zero completed human XAI evaluations exist in repository. |
| [`HUMAN_REVIEW_WORKSHEET.csv`](./HUMAN_REVIEW_WORKSHEET.csv) | **0 completed** (59 stratified executed cases pre-populated with actual SynTutor outputs and 17 blank dual-reviewer rubric columns) | Pending (designed for ≥2 independent linguistics/TESOL raters) | **UNMEASURED / BLOCKED** | Ready for immediate human annotation; zero fabricated scores. |
