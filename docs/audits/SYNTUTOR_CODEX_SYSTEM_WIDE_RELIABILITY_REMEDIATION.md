# SynTutor Phase 2 linguistic reliability and external evaluation

The Phase 2 baseline used `fix/syntutor-system-reliability-xai` at `5451d72752b7919f9d10f4c63c0e0981d7b8a978` with 26 tracked changes and three untracked audit files from the handoff. The starting working diff SHA-256 was `aac7fcc40624be71603a0c99821887508d58220461e8500f0c840d518cdc8f4d`. Earlier fixes, published content, source receipts, frozen datasets, and historical predictions were preserved. See the [handoff review](SYNTUTOR_INDEPENDENT_AGY_HANDOFF_REVIEW.md) and [XAI traceability matrix](SYNTUTOR_UNIFIED_EVIDENCE_XAI_RELIABILITY_REMEDIATION.md).

## Baseline and evaluation design

I ran the existing V4 diagnostic, real-world probes, and lookup-bypassed B–R census before changing production code. I also froze and scored a separate external sample before implementation. I used the existing diagnostics and independently constructed controls to investigate failures. The external samples were used for aggregate comparisons. The same frozen manifest and scoring code were used after the fixes.

| Resource | Provenance and use |
|---|---|
| BLiMP | The new external sample contains 58 source pairs, one per eligible non-semantics paradigm, from `3e56b06fcabca9b30822fc66435fca6b1aa40bb1`. Deterministic SHA-256 ranking selected pairs after normalized exact exclusion from known repository samples and a 0.85 token-set Jaccard prior-overlap check. The test measures SynTutor's sentence-level judgments against the official labels. BLiMP's original language-model benchmark uses pairwise preferences. Some retained paradigms involve syntax–semantics interactions. [Official BLiMP repository](https://github.com/alexwarstadt/blimp) |
| JFLEG | The V4 slice contains 10 learner originals and 10 selected corrected sentences. It is a previously exposed binary diagnostic derived from JFLEG, whose original task uses multiple holistic fluency revisions. The source archive at `ee06ff806a208aba815ac45313f4e750a48330a5` was checked directly for the historical disagreement. The noncommercial corpus and the selected corrected variants do not establish an independent grammaticality benchmark. [Official JFLEG repository](https://github.com/keisks/jfleg), [JFLEG paper](https://aclanthology.org/E17-2037/) |
| W&I+LOCNESS | The public v2.1 archive provides development gold M2. I froze 40 items per W&I level A, B and C, with source tokenization compatibility checked before evaluation. Native LOCNESS items were reserved for the EXPECT run. The released M2 edits derive from human revisions and automated error typing. I used ERRANT 3.0.0 span-and-replacement scoring on app corrections. The official test references are held by the shared-task service. These results are for a local development-set sample. [Official BEA shared task](https://www.cl.cam.ac.uk/research/nl/bea2019st/), [ERRANT 3.0.0](https://github.com/chrisjbryant/errant/tree/v3.0.0) |
| Burton–Roberts | The 216 transcribed, sentence-yield-matched `IMG` references exercised the compositional FINAL-D1 projector without reference lookup. Full and triangle-aware scores use the repository's PARSEVAL implementation, which scores canonical outputs with aligned word yield. The material has informed development and includes conventions and categories of particular book figures. [Reference records](../../web/content/book), [existing scorer](technical_evaluation/run_technical_evaluation.py) |
| GUM | I scored the `const_gold` Penn trees from Peng and Zeldes's hand-corrected 2018 research release at `09ec5f66b92722368fbb13b10513e25c3429d08d`. I used seven documents and excluded the redacted Reddit document. I stripped function suffixes and ignored wrappers, punctuation, empty nodes, and preterminals. Lexical-character offsets permit equivalent token splits only when the normalized lexical yields agree. This measures Benepar candidate bracketing, with coverage reported separately. It uses Penn labels and has no FINAL-D1 reference annotations. The broader GUM constituent layer is largely parser-produced. [Gold release](https://github.com/gucorpling/GUM_UD_LAW2018), [corpus annotation documentation](https://gucorpling.org/gum/annotations.html) |
| EXPECT | From the published test annotation at `6e44b68f6e4c199dd3b235cacb604a856bd3d133`, I used the native `N` origin portion to keep it separate from W&I A/B/C. I mapped the paper's joint target/source indices to source word offsets and used source-side non-placeholder edit anchors. A verified finding must overlap the referenced edit anchor before its related evidence words are scored. Missing findings count against recall. Target-side words and insertion-only anchors are outside this source-only comparison. The 15-class error inventory does not map one-to-one to SynTutor's IDs. The measured result is evidence-token grounding with the published types retained for case analysis. [EXPECT paper](https://aclanthology.org/2023.acl-long.413/), [data and format](https://github.com/lorafei/Explainable_GEC) |
| GMEG-EXP | Its coverage, informativeness and correctness rubric is suitable for blinded explanation review. Human and generated explanations and grammar versus fluency would need separate judgments. The author repository documents an access request for the Yahoo portion. No GMEG-EXP score was collected. [Paper](https://aclanthology.org/2024.lrec-main.688/), [release repository](https://github.com/grammarly/gmeg-exp) |
| EXCGEC | The publicly described edit-wise tasks can inform review design. Its Chinese data is outside the English evaluation scope. [EXCGEC paper](https://arxiv.org/abs/2407.00924) |

The external exclusions cover known repository texts, including the earlier benchmarks, V4 and textbook records. Unknown pretraining overlap remains possible for pretrained models. EXPECT uses W&I+LOCNESS development essays and the two evaluation slices remain in the same corpus family despite their distinct origin strata. W&I and EXPECT results use the available source formats and exclude duplicates against known prior texts rather than implying comprehensive document-level deduplication of all material. No pooled performance score combines protocols or corpora.

### JFLEG prediction investigation

The V4 item `eval4-jfleg-003-u` matches row 34 in the published JFLEG `dev.src`. All four references change the disputed `brang`, but they disagree on tense or construction. One leaves a bare `bringing` without a finite auxiliary. One uses `brought`, retaining simple past in the embedded clause. The original context supplies an overt subject and a finite lexical-verb slot. Detecting the nonstandard form in that slot is therefore supported for standard written English. Matching one particular fluency rewrite would overstate the annotation evidence. [Original JFLEG data revision](https://github.com/keisks/jfleg/tree/ee06ff806a208aba815ac45313f4e750a48330a5/dev)

The stored Cycle 8 result found `C-SPELLING`, the next diagnostic abstained, and the subsequent run detected `C-VERB-FORM`. The actual Phase 2 baseline reproduced `C-VERB-FORM`. The 85% → 80% → 85% movement reflects one prediction under the same binary scoring convention. The interim abstention reduced recall, and the later recovery supplies more precise grammatical evidence. The binary score counts a grammatical abstention as non-positive. Exact verdict matching is 16 → 15 → 16 out of 20. The frozen reference remains as received.

## Confirmed defects and fixes

| Finding | Root cause and implementation | Controls |
|---|---|---|
| Wrong canonical labels on contracted auxiliaries | FINAL-D1 selected the perfect/passive path for `'s` before checking its complement, sometimes accepting a misleading spaCy `auxpass` tag. It also assumed any `MD` label on `'d` meant *would*. The projector and matrix now share a supported interpretation of `'s` and `'d`. Progressive `-ing`, perfect *been*, a supported direct object, an overt attached passive agent, and distinct base/participle forms supply evidence. Potentially retained passive objects and shared forms keep the full contraction provisional. | “She's leaving,” “She's eaten the apple,” “She's eaten by the monster,” “She's been studying,” “I'd leave,” “I'd left,” “She's given a prize,” and “I'd put the keys away.” Both straight and curly apostrophes were tested. |
| Malformed input displayed canonical auxiliary labels | The projector treated almost any verb shape after `be` as progressive or passive and accepted a past-only form under perfect `have` if the parser mislabeled it as `VBN`. The new form check withholds canonical authority. Corroborated grammar findings and validated revisions can still pass through the existing local evidence path. | “She is eat dinner” becomes provisional with the plain-form issue and an available revision. “They have went home” becomes provisional and retains the `gone` repair. Lexical `have` with an NP and copular `be` retain their existing interpretation. |
| An unsafe correction changed *had left* to *would leave* | The matrix tested `'d` only as a modal and sent the resulting false verb-form finding to correction assembly. The shared contraction handling removes the false trigger. The ambiguity branch leaves `put`-type shared forms without a repair. | “I'd left by noon” stays grammatical with the word `left` and no revision. “I'd leave tomorrow” still selects a plain form. |
| Passive participial adjunct had an adjective-phrase boundary and a spurious manner correction finding | A postverbal `VBN` and its *by*-agent could come from Benepar inside an ADJP-like wrapper. The matrix treated it as an adjective describing a manner. A matching past-participial tag, dependency on the matrix verb as `advcl`, and an agent PP linked to the participle now justify the B–R non-finite clause. The existing gap machinery links the matrix subject, covert subordinate subject and passive object. This follows Chapter 10 Discussion 5, [55b]. | The reference “We returned disappointed by our evening” and variants headed by *surrounded* and *accompanied* use the clause structure with lookup bypassed. The adjective complement after *seems* remains an AP. “She waltzed gentle” retains the existing adjective/adverb finding. [Chapter 10 reference](../../web/content/book/ch10.trees.json) |
| Auxiliary explanation named the wrong selected verb in chains | Dependency annotation often points every auxiliary to the lexical head, so the explanation could pair progressive `'s` with *watched*. The source-bound node text now follows the auxiliary's selected VP layer. Generator and Builder use the same canonical relationship. Word and constituent explanations retain their distinct descriptions. | “He's being watched” explains *being* under the progressive auxiliary. “She's been studying” explains *been* under the perfect. Browser keyboard selection and Builder evidence transport exercise these presentation paths. |
| Detached nominal supplement triggered a missing-copula finding and a polarity finding | The missing-copula rule previously counted any NP and modifier in the same candidate `S`, independent of order. The evidence must now show a subject before a predicate. The polarity rule recognizes a narrow initial detached `ever` plus determined NP with an overt following subject and finite predicate. No new canonical supplement label was introduced. | “Ever the optimist, she tried again” and “Ever a gentleman, he offered his seat” lose both false findings. “She very happy” and genuinely unlicensed `ever` retain their findings. |

## Comparable before and after results

Grammar F1 uses `ungrammatical` as the positive class. Strict rules score every record and treat abstentions as non-positive. The separate hybrid column gives F1 and MCC on decisive items and reports the denominator. Coverage is the share of answers that were decisive. All rows below had zero execution errors for grammar scoring.

| Input cohort | Rules F1 | Rules MCC | Rules decisive coverage | Hybrid decisive F1 | Hybrid MCC | Hybrid coverage |
|---|---:|---:|---:|---:|---:|---:|
| Frozen external BLiMP sample, 116 | 0.7778 → 0.7778 | 0.5919 → 0.5919 | 114/116 → 114/116 | 0.8485 → 0.8485 | 0.7001 → 0.7001 | 100/116 → 100/116 |
| V4 BLiMP, 240 previously exposed | 0.8357 → 0.8357 | 0.7270 → 0.7270 | 240/240 → 240/240 | 0.8856 → 0.8856 | 0.7993 → 0.7993 | 222/240 → 222/240 |
| V4 JFLEG, 20 previously exposed | 0.8571 → 0.8571 | 0.7035 → 0.7035 | 19/20 → 19/20 | 0.8571 → 0.8571 | 0.6854 → 0.6854 | 19/20 → 19/20 |
| V4 BLiMP + JFLEG, 260 previously exposed | 0.8376 → 0.8376 | 0.7223 → 0.7223 | 259/260 → 259/260 | 0.8829 → 0.8829 | 0.7890 → 0.7890 | 241/260 → 241/260 |

The V4 CoLA subset remains a separate contamination-sensitive diagnostic because the advisory model was trained on CoLA. Rules F1 and MCC stayed at 0.4000 and 0.3081. The only changed V4 prediction field was a structural fallback reason for `eval4-blimp-056-u`. Its tree and judgment stayed unresolved in the same ways. The local real-world probe run exposed 16 repairs in both passes. These safety probes do not supply independent meaning-preservation ratings.

| Task | Before → after | Coverage and interpretation |
|---|---|---|
| Lookup-bypassed B–R full | Labeled F1 **0.6807 → 0.6832**, unlabeled F1 0.7235 → 0.7244 | 200/216 canonical and 185/216 yield-aligned in both runs. Full exact matches stayed at 32. |
| Lookup-bypassed B–R triangle-aware | Labeled F1 **0.8390 → 0.8420**, unlabeled F1 0.8917 → 0.8928 | 99 → 100 exact on the same 185 aligned outputs. The change is entirely `ch10-d5-55b`, where the corrected clause added four matched labeled spans. This is a measured textbook diagnostic improvement. |
| GUM gold Penn constituency | Precision 0.8781 → 0.8781, recall 0.8728 → 0.8728, labeled F1 0.8754 → 0.8754 | 360/387 scoreable in both runs. Thirteen were split across application sentence boundaries and 14 had incompatible normalized yields. There was no upstream candidate parser change. |
| W&I development edit correction | Precision 0.2778 → 0.2778, recall 0.0259 → 0.0259, F0.5 0.0943 → 0.0943 | 14/120 API revisions and 5 TP, 13 FP, 188 FN edits in both runs. Two non-single-sentence inputs contributed unchanged hypotheses. Low recall is the main measured gap. |
| EXPECT source evidence words | Precision **0.5000 → 0.5556**, recall **0.0195 → 0.0244**, F1 **0.0376 → 0.0467** | 14 → 15 of 169 edit anchors detected. One additional correct evidence word, with matched counts 4/4/201 → 5/4/200 (TP/FP/FN). Nine non-single-sentence items contributed empty predictions. This small change is evidence-token coverage, with no claim about quality of natural-language explanations. |

## Release and research readiness

The grammar/tree separation and correction behavior are ready for further local development. SynTutor retains the same parser, canonical B–R authority, Cambridge registry, rule matrix, advisory detector and public endpoints. The lesson and assessment publication validators still fail on their respective metadata and bank digests. Independent approval remains required for 20 Cambridge chapters, 1,713 cited records and 10 rewritten assessment items. No reviewer receipts, curriculum, assessment items, or production data were changed.

| Verification | Final result |
|---|---|
| Backend discovery with offline model caches and local transports | **986 passed**, zero reported failures or skips, in 223.676 seconds. Includes the new controls, Flask/FastAPI/stdlib contracts, projection, Cambridge evaluation and correction safety. |
| Focused linguistic and explanation run | **26 passed**. The first explanation run exposed a regression in the existing tense wording and word-versus-branch distinction. The final shared description retains them, and the earlier assertions pass. |
| Cambridge source governance | **15 passed** in combined batch/Chapter 3 tests. **110 batch audits** and **1,620 pages** passed. The Chapter 3 CLI returned zero errors. Existing owner waivers retain their status. |
| Chromium on the local application | Real Flask on port 8771 passed the strengthened Syntax Generator suite, including selected progressive `being`, the unaltered contracted perfect, provisional grammar and correction, and the passive participial clause. The Generator-to-Builder HTTP/rendering parity test and XAI-7 lesson/quiz evidence test also passed. |
| Model-free frontend and packaging | `test:quiz`, `test:evidence`, `test:builder`, `test:node-lessons`, `test:correction`, `test:lessons`, `test:assessments`, `test:quiz-v2`, Vercel-filtered static build and Docker copy contract passed. These checks are local integration results. |
| Historical integrity | **74 passed**. No tracked frozen input, prediction, review worksheet, source extraction, or receipt changed. |
| Formal validators | `validate_lessons.py` failed with `Source metadata changed after review`. `validate_assessments.py` failed with `Question/source/blueprint content changed after review`. Hosted CI and the native account-browser flow were outside this local run. |

The canonical pathway still depends on usable upstream shape and attachment evidence. Unmarked result-state readings such as “She's gone,” shared perfect/modal contraction forms, and cases without a corroborated passive agent can remain provisional. GUM scoreable coverage and errors quantify part of the upstream boundary gap. Official BEA test scores, human explanation evaluations, and independent learner-writing B–R references remain unavailable in this evaluation. The W&I and EXPECT recalls indicate that broad correction and explanation coverage remain open research problems.

An independent review should blind reviewers to implementation version and model provenance, retain alternative readings where defensible, and record agreement and adjudication. Separate (1) canonical B–R boundaries and labels, (2) correction necessity and meaning preservation, and (3) explanation correctness, informativeness and coverage. Record dialect and register separately from grammar errors. The preserved human-review worksheets contain no new ratings.

## Environment and reproduction

The production configuration was unchanged between runs. Darwin arm64, Python `3.11.17`, spaCy `3.8.16`, `en_core_web_md 3.8.0`, Benepar `0.2.0`, Torch `2.15.0`, Transformers `4.46.3`, SentencePiece `0.2.3`, Flask `3.1.3`, NLTK `3.10.4` and JSON Schema `4.26.0`. The optional scoring environment pinned ERRANT `3.0.0` and RapidFuzz `3.14.3` in a temporary directory. The ERRANT tagging and edit extraction run used the existing `en_core_web_md` package in both passes.

| Item | Version or SHA-256 |
|---|---|
| Benepar `benepar_en3` model weights | `fc465e820f8a62ffc6c23cb7d2ceed61f41d29d1930d471df301f17d3dbb4822` |
| Advisory RoBERTa-CoLA | revision `3ccf3a400f2fa75ff257eac171047603ffbe84f1`, weights `7111036783d87c0f01df1b28c4625fcceb1272f8cc6037aed818cb26698fe7cc` |
| Optional correction MLM DistilBERT | revision `12040accade4e8a0f71eabdb258fecc2e7e948be`, weights `5e3f1108e3cb34ee048634875d8482665b65ac713291a7e32396fb18f6ff0063` |
| V4 frozen CSV | `1d468942f7e9886039fa1c77df55668609e1cac1b70fcbcda0da8f2c0f0b4fe6` |
| BLiMP tar.gz | `cbada5cc59b41798f0f0a6b2525166c7a1d82c4a40ed726c78810b898e1979f6` |
| W&I+LOCNESS v2.1 tar.gz | `d5cbf68cda3da0c3af69dd672614d07287bfe996b87da0c75051d5349d76c666` |
| EXPECT test JSONL | `b969451d22a918cdbed5642dcb008e8ded2badbcec127aba099af8daca7073f5` |
| GUM gold tar.gz | `ce1765b215321bec95fa083f9ec70754c98ac5421de51d31a73f9c5f5425011f` |
| JFLEG tar.gz | `fbf9e18d3f89043498bfe0fd48ec9333f968817884e5ff79547987e33ef03467` |
| Frozen external manifest | `0a0322368b646873a1b42f77571d27259a2e664a1c20b09aa831afd98d1b4672` |
| External scorer | `48cdbba34e775d984544d95b1ca78df45a76676056ad068c5e7f33b5a74ee962` |
| Local diagnostic and textbook runner | `cf34571dcf0c06353c96e799b58e3f7d9a0f2625722b2642c3a4de08be218b69` |

The [external runner](technical_evaluation/run_phase2_external.py) uses `blimp.tar.gz`, `wi-locness-v2.1.tar.gz`, `expect-test.json` and `gum-gold.tar.gz` under the supplied source path. The archive URLs were the pinned GitHub codeload tarballs for BLiMP and GUM, [EXPECT test JSONL](https://raw.githubusercontent.com/lorafei/Explainable_GEC/6e44b68f6e4c199dd3b235cacb604a856bd3d133/data/json/test.json), and the [Cambridge v2.1 archive](https://www.cl.cam.ac.uk/research/nl/bea2019st/data/wi%2Blocness_v2.1.bea19.tar.gz). Only the temporary evaluation directory contains downloaded data and per-case predictions. The commands below re-create the measurements using the same model configuration in both states.

```sh
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false CGEL_REQUIRE_PARSER=1
export PYTHONPATH=/tmp/syntutor-phase2/scoring-deps
eval_dir=/tmp/syntutor-phase2
eval_code=docs/audits/technical_evaluation
# Freeze once, before production edits. The runner verifies corpus and scorer hashes.
.venv/bin/python "$eval_code/run_phase2_external.py" "$eval_dir" "$eval_dir/external-manifest.json"
.venv/bin/python "$eval_code/run_phase2_external.py" "$eval_dir" "$eval_dir/external-manifest.json" --output "$eval_dir/external-before"
.venv/bin/python "$eval_code/run_real_world_reliability.py" "$eval_dir/before"
# Repeat from the final working tree against that manifest.
.venv/bin/python "$eval_code/run_phase2_external.py" "$eval_dir" "$eval_dir/external-manifest.json" --output "$eval_dir/external-after-final"
.venv/bin/python "$eval_code/run_real_world_reliability.py" "$eval_dir/after-final"
PYTHONPATH=server .venv/bin/python -m unittest discover -s server -p 'test_*.py'
.venv/bin/python "$eval_code/verify_metrics.py"
```

The baseline working diff, final comparison metrics, raw predictions, diagnostic API payloads and Chromium logs are under `/tmp/syntutor-phase2`. The external runner writes raw M2 hypothesis/reference blocks, overlap-screened sample IDs, and per-case measures. The test command needs permission to bind local HTTP transports. No hosted system was used.
