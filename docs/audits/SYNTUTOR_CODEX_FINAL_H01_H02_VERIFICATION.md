# SynTutor H01 and H02 verification

## A. Git and implementation state

Verified on 22 November 2026 in `/Users/kiyel/Desktop/SynTutor`, branch `fix/syntutor-system-reliability-xai`, starting HEAD `1af399bf2017154edc7af620620fda053db1307f`. The checkout started clean. Recent predecessors were `f9470d4`, `73c555c`, `e1d887d` and `5451d72`. The production and evaluation patches in this report are local. The tracked patch digest is `a0c156852361945ce6d8301da6ff6e3613099d95674bf0701d6608c40bdab4b4`. The parser, projector, Matrix, Cambridge evaluation, licensing, corrections, XAI and API retain their existing responsibilities and contracts. The manuscript, hypotheses, benchmark data, historical outputs and curriculum records were left intact.

| Implementation defect | Change and verification |
| --- | --- |
| A finite postposed adjunct could be nested inside an untensed VP under an auxiliary. | FINAL-D1 now attaches it beside the tensed VP when an overt subordinator and spaCy's `mark` and `advcl` dependencies independently corroborate that boundary. The fix follows a simple auxiliary chain and preserves selected complements, negation, fronting and incoming gaps. The two changed textbook cases are `ch8-71` and `ch8-disc7`. [Projector](../../server/final_d1_projection.py), [Chapter 8, p. 186 [71] and p. 190 Discussion 7](../../web/content/book/ch08.trees.json) |
| Bare-noun feedback inferred countability from generic adjectives. The lexical rules also treated inflecting verbs as having a single valency. | The noun check requires evidence of a count reading for flexible nouns such as *change* and *manipulation*. An overt ordinal within the argument NP is sufficient on the tested path. *Major change* and *careful manipulation* can be mass readings. The simple obligatory-object list no longer claims that *take* and *cure* always require an object. The *talk* addressee check requires a witnessed personal addressee and excludes shapes with further VP dependents, protecting topic uses and *talk someone into* constructions. Controls retain genuinely missing articles, *resemble* without an object and a witnessed bare addressee. [Matrix](../../server/matrix.py), [Rules](../../server/ruleset.py), [Oxford count and mass senses of change](https://www.oxfordlearnersdictionaries.com/us/definition/english/change_2), [Cambridge transitivity](https://dictionary.cambridge.org/uk/grammar/british-grammar/intransitive-and-transitive-verbs), [Cambridge topic use of talk](https://dictionary.cambridge.org/dictionary/english/talk-business-politics-etc), [Cambridge talk someone into](https://dictionary.cambridge.org/dictionary/english/talk-into), [Merriam-Webster take](https://scrabble.m-w.com/dictionary/take), [Collins cure](https://www.collinsdictionary.com/dictionary/english/cure) |
| Agreement prose mislabeled the base form as plural and linked relative-clause agreement to a determiner. A valid article edit could be lost when it inserted before a modifier. | Indefinite-subject prose states singular agreement. Relative-subject feedback cites the actual number witness and relative pronoun, with the finite verb as the error target. Number-ambiguous coordination and first/second-person pronouns with insufficient person evidence are guarded. Verified NP-initial insertion anchors now travel as related evidence while the noun remains the article target. The API regression verifies `We bought a red bicycle.` and preserves the original meaning and boundary. [Licensing](../../server/licensing.py), [Findings](../../server/findings.py), [Regression controls](../../server/test_h01_h02_reliability.py) |
| An indefinite pronoun could be linked to a bare `be` after `may` or to a verb in another clause. Both parsers also labeled the bare form in `Everybody stand up!` as present indicative. | The indefinite rule checks its clause's own subject and tensed predicate. *None* no longer supplies fixed singular number. The Matrix, deterministic rule and learner evidence withhold an agreement violation for a witnessed plausible root command with overt *everybody/everyone*. A late diagnostic also confirmed that *delay* can be mass. The existing context-sensitive check now protects *further delay* and still flags omission before an ordinal count reading. [Cambridge on modals](https://dictionary.cambridge.org/grammar/british-grammar/modality-), [Everyone subjects in directives](https://dictionary.cambridge.org/us/grammar/british-grammar/everyone), [None-number alternation](https://dictionary.cambridge.org/us/grammar/british-grammar/no-none-), [Cambridge delay](https://dictionary.cambridge.org/us/dictionary/english/delay) |

Evaluation changes are in the [offline neural comparator](technical_evaluation/run_h02_grounding_comparator.py), [separate structural scorer](technical_evaluation/run_reference_specified.py) and [eight method tests](technical_evaluation/test_hypothesis_methods.py). The original H01 runner and frozen span, ERRANT and EXPECT scorers are unchanged.

## B. H01 baseline and final results

Both runs used the same 216 third-edition textbook records with lookup prohibited. The measured pipeline is spaCy → Benepar → production FINAL-D1. A missing projection contributes all gold spans and no prediction. Yield mismatch contributes both span totals and zero matches. Neither contributes an exact match. The full-span extractor measures labeled overt constituent boundaries and does not score every tree label, lexical feature or gap/coindexation relation. [Original scorer and results protocol](H01_H02_VALIDATION_BLOCKER_RESOLUTION.md), [Third-edition source](https://eprints.ncl.ac.uk/157385), [PDF source hashes](../../sources/burton_roberts/source_manifest_2026-11-08.json)

| Metric | Baseline | Final |
| --- | ---: | ---: |
| Normalized and schema-valid | 213/216 (98.61%) | 213/216 (98.61%) |
| Yield-aligned | 204/216 (94.44%) | 204/216 (94.44%) |
| Full labeled F1, all attempts | 62.83% | **62.96%** |
| Full precision / recall / F1, 204 aligned | 53.93% / 87.99% / 66.87% | 54.03% / 88.17% / 67.00% |
| Triangle-aware precision / recall / F1, 204 aligned | 78.87% / 87.99% / 83.18% | 79.03% / 88.17% / 83.35% |
| Full exact disclosed spans, all attempts | 37/216 (17.13%) | 37/216 (17.13%) |
| Triangle-aware exact disclosed spans, all attempts | 112/216 (51.85%) | 112/216 (51.85%) |
| Reference-specified structural agreement, all attempts | 77.02% | 77.18% |
| Complex/embedded all-attempt full F1, 44 cases, 40 aligned | 52.69% | **53.09%** |
| Complex/embedded reference-specified agreement, 44 cases | 70.87% | 71.41% |
| Simple full F1, 62 cases, 59 aligned | 64.19% | 64.19% |
| Phrase/fragment full F1, 110 cases, 105 aligned | 70.22% | 70.22% |

The final full score is `2 × 991 / (1,195 + 1,953)`, up from 989 matched spans. All-attempt precision and recall are 50.74% and 82.93%. Only the two identified adjunct cases changed scored agreement. Nine normalized records failed yield alignment and three had working trees only (`ch4-52b`, `ch8-67c`, `ch8-ex2-f`). The complexity proxy uses root `S`/`Sentence` and an embedded `S`, `S-bar` or `S-dbar` visible in the source. Collapsed clauses can hide complexity. In `ch8-9a` the parser attaches *at every opportunity* to the embedded predicate, where the author shows a matrix reading. Remapping the `S` outline labels would not resolve that attachment difference. In `ch8-4a`, the outline compresses explicitly embedded complement boundaries. Contrasting source analyses for ambiguities such as `ch9-59/60` and `ch10-ex2a/b` need explicit reading-sensitive adjudication. The extra third-edition figure [79b], ch. 10 p. 239, again matched 8/8 exposed spans by the separate overt-character alignment. It remains one exposed, single-reader transcription outside the 216. [Chapter 8 source](../../web/content/book/ch08.trees.json), [Historical provenance and author figure](H01_H02_VALIDATION_BLOCKER_RESOLUTION.md)

The historical trace at `f9470d4` contains 561/826 aligned unmatched predictions strictly inside collapsed triangles. The reproduced current baseline has 580/845. The 52 placeholder count is reproducible when `PHRASE` includes the suffixed variants. The three named outline records (`ch8-4a`, `ch8-10a`, `ch8-ex1-a`) have 13 unmatched gold `S` spans in total, compared with 50 across all 204 aligned baseline records. The earlier attribution of roughly 47 to those three is unsupported. An upper bound of `2G/(2G+T)` describes a hypothetical parser matching all `G` gold spans and retaining exactly `T` specified extras. For `G=1,195, T=561` it is 80.99%. Neither the extras nor their number are fixed for all valid expanded parsers, so this cannot establish a structural ceiling.

The supplemental score removes only unmatched predicted spans strictly inside explicit gold triangles. It records each ignored span and the enclosing triangle. Tests require a wrong outer label and a crossing attachment to remain errors. Placeholder labels, outlines and gaps receive no speculative equivalence or extra credit. The denominator remains 216, including all failures. [Supplemental scorer](technical_evaluation/run_reference_specified.py), [Historical ceiling claim](SYNTUTOR_H01_H02_FINAL_IMPROVEMENT_AND_VALIDATION.md)

## C. H02 baseline and final results

Baseline and final grounded runs use the original manifest and scoring calls. BLiMP counts an abstention as incorrect for exact verdict accuracy. W&I and EXPECT keep failed whole-item analyses in their annotation denominators. Separate learner-visible correction scoring selects the text exposed by the learner feedback surface.

| Measure | Baseline | Final |
| --- | ---: | ---: |
| BLiMP exact verdict, all items | 102/116 (87.93%) | 100/116 (86.21%) |
| BLiMP decisive coverage | 108/116 (93.10%) | 106/116 (91.38%) |
| BLiMP false error judgments on grammatical items | 2/58 | 2/58 |
| BLiMP missed error judgments, including abstentions | 5/58 (4 grammatical, 1 abstention) | 7/58 (4 grammatical, 3 abstentions) |
| W&I API exact edits, precision / recall / F0.5 | 6 TP, 7 FP, 187 FN / 46.15%, 3.11%, 12.24% | Same (11 proposed revisions on 120 inputs) |
| W&I learner exact edits, precision / recall / F0.5 | 2 TP, 4 FP, 191 FN / 33.33%, 1.04%, 4.61% | Same (6 displayed revisions on 120 inputs) |
| EXPECT annotated edit target overlapped | 20/169 | 19/169 |
| EXPECT source evidence, precision / recall / F1 | 12 TP, 4 FP, 193 FN / 75.00%, 5.85%, 10.86% | 11 TP, 5 FP, 194 FN / 68.75%, 5.37%, 9.95% |
| Learner output packets with rule findings / sentence prose / node prose | 140 / 405 / 400 (of 405) | 139 / 405 / 400 (of 405) |
| Independently assessed conceptual correctness or correction validity | Unmeasured | Unmeasured |

The two BLiMP losses after replacing the unconditional obligatory-object entries were `inchoative:528:ungrammatical` and `wh_vs_that_with_gap:43:ungrammatical`. A verb that supports both frames cannot by itself prove an object is missing. The second item additionally needs a defensible clause or extraction diagnosis. Both remain misses against the original labels. The regression controls protect intransitive *the graft took* and *the resin cured* as well as a genuinely obligatory object with *resemble*. None of these corrections attributes the BLiMP list labels to phrase-level accuracy or to explanation quality. [BLiMP](https://aclanthology.org/2020.tacl-1.25/)

The W&I adapter keeps 120 sentences and 193 scored gold edits. Two whole-item segmentation failures contribute eight missed edits. Punctuation, broad lexical substitutions, vocabulary choice and larger rewrites are only selectively covered. In the Phase 3 `R:VERB:SVA` proxy slice, both versions match 2/3 gold edits at the API and 1/3 in learner output, with five and four unmatched predictions tagged SVA respectively. The fixed EXPECT `Participle` slice has four annotations and ten projected gold witnesses. Both versions locate two anchors and match 2/10 evidence words with no extra witness. Corpus-wide supported-scope performance needs a rule-to-annotation crosswalk checked before looking at outcomes. W&I's official span-based ERRANT comparison measures exact edit agreement. Alternative validity, unnecessary edit judgments and actual introduced-error rates require independent adjudication. [BEA-2019 W&I+LOCNESS](https://aclanthology.org/W19-4406/), [ERRANT](https://github.com/chrisjbryant/errant), [Phase 3 slice definitions](SYNTUTOR_CODEX_PHASE3_BENCHMARK_RELIABILITY.md)

EXPECT annotation 1781 pairs a number edit with two source witnesses. The baseline received credit for one overlapping witness while flagging a missing article in *further delay*, a valid mass use. Withdrawing that unrelated article finding loses the overlap. Annotation 2394 has no projected gold witness, so adding the independently identifiable relative subject *who* counts as one extra token. The same packet now omits the false claim about the bare *be* governed by *may* and retains the actual relative agreement diagnosis. These are the only two changes to the EXPECT prediction records. The remaining misses include 141 analyzable annotations without a detected anchor and 19 missed gold witnesses from nine rejected items. Ninety-five annotations project to zero source gold witnesses. Prose counts include partial-input packets and measure availability only. [EXPECT](https://aclanthology.org/2023.acl-long.413/), [Cambridge delay](https://dictionary.cambridge.org/us/dictionary/english/delay)

## D. Comparator validity

The full condition uses the production analysis and published learner output. The neural-only condition shares inputs, parse eligibility and the existing CoLA score. It selects revisions through the existing MLM search and renders a short acceptability or correction message. The Matrix checks, deterministic rules, Cambridge findings, licensing, finding selection, correction constraints and structural explanation generation differ. The comparison measures the difference between available feedback systems on this sample. It cannot attribute that difference to the Matrix alone or test like-for-like node explanations. No labels inform predictions. The harness verifies the source hashes, source order, unique inputs and 58 genuine BLiMP good/bad pair IDs. It preserves whole-input processing failures for both arms and treats a missing neural score as an abstention. [Comparator](technical_evaluation/run_h02_grounding_comparator.py)

The existing same-system ON/OFF experiment removes only `check_lexicon` and `check_relatives` during evaluation and correction verification. It preserves the Matrix, Cambridge, the correction engine and the explanation renderers. The final replay changed 44/405 feedback packets with zero disagreements in the shared parse, tree status, Cambridge and detector fields. BLiMP exact verdicts were 100/116 ON and 98/116 OFF. W&I matched six versus four API edits and two versus one displayed edits of 193. EXPECT overlapped 19 versus 16 targets, with both arms matching 11/205 source witnesses and producing five versus three extras. The intervention establishes the incremental behavior of those two licensing checks. Turning the whole Matrix off would remove part of the input to the existing grammar findings, correction and explanation channels. A future causal claim needs a prespecified intervention with a shared explanation path and comparable opportunity to produce feedback. [Lexical and relative intervention](technical_evaluation/run_hypothesis_checks.py), [Existing protocol](H01_H02_VALIDATION_BLOCKER_RESOLUTION.md)

The old workbook did contain 405 differing pairs and 405 key entries. Eleven inputs that failed the whole-sentence benchmark check were eligible to appear as first-sentence feedback in that workbook. The corrected workbook keeps all 405 intake rows, records availability, randomizes the row order and condition-to-X/Y assignment independently, and stores the key separately with mode `0600`. The earlier key had mode `0644` inside the private scratch directory. Every rating and notes field remains blank. Current row counts and integrity are listed in the artifact inventory. Screening only differing pairs would estimate quality conditional on pair disagreement and distort an overall feedback-quality estimate. System style or availability can still give reviewers clues even when identities are hidden. [Worksheet writer](technical_evaluation/run_h02_grounding_comparator.py)

## E. Scientific evidence

The recorded baseline comparator reproduced 102/116 versus 95/116 exact verdicts, 46/58 versus 37/58 complete correct BLiMP pairs, and 2/58 versus 13/58 false ungrammatical judgments. Its two-sided exact McNemar values were `0.09228516` for item verdicts (discordance 10:3), `0.01171875` for both items within a minimal pair (10:1), `0.00341797` for false-error judgments on grammatical items (12:1), and `1.00000000` for W&I per-sentence unmatched edit presence (2:2). The matched denominator counts the opposing condition's missed feedback separately from a false claimed error. Exact tests use the two-sided binomial tail on discordant observations, (\min(1,2P[\mathrm{Binom}(b+c, 0.5)\le\min(b,c)])\). [McNemar method](https://itl.nist.gov/div898/software/dataplot/refman1/auxillar/mcnemar.htm)

| Final grounded versus neural-only outcome | Grounded | Neural-only | Discordance (grounded better : neural better) | Exact two-sided p | Holm-adjusted p |
| --- | ---: | ---: | ---: | ---: | ---: |
| BLiMP exact verdicts | 100/116 | 95/116 | 10 : 5 | 0.30175781 | 0.60351562 |
| BLiMP both verdicts correct within pair | 44/58 | 37/58 | 10 : 3 | 0.09228516 | 0.27685548 |
| BLiMP false error judgments on grammatical items | 2/58 | 13/58 | 12 : 1 | 0.00341797 | 0.01367188 |
| W&I sentences with at least one unmatched edit | 6/120 | 6/120 | 2 : 2 | 1.00000000 | 1.00000000 |

The false-error difference is 11/58 or **18.97 percentage points**, with a descriptive 95% percentile interval of 8.62–31.03 points from 10,000 resamples of minimal-pair IDs. An abstention avoids a positive error claim and fails exact correctness. Grounded and neural-only exact-accuracy Wilson intervals are 78.76–91.33% and 73.90–87.84%. These marginal intervals assume independent items and do not account for minimal-pair coupling. The pair-level analysis is preferable for exact accuracy. Treat the Holm adjustment across the four tests as exploratory. For W&I the neural-only outputs match 1/193 gold edits with six unmatched predicted edits (14.29% precision, 0.52% recall, 2.26% F0.5). It overlaps one EXPECT target and produces zero related witnesses by design, giving no positive evidence predictions on which to estimate precision. The adapter reports a zero convention for that empty denominator. These results describe the two tested subsystems and a lower false-error count, with limited coverage and no causal isolation of grounding.

The H01 diagrams informed application development. Lookup was blocked during evaluation, which removes direct answer retrieval. A deterministic overlap check (Unicode NFKC, casefold, alphanumeric tokenization) found 200 unique strings among 216 diagrams across 12 duplicate groups, 168 among 169 EXPECT items and no cross-source exact normalized matches among the four samples. This check leaves paraphrases, template overlap, author alternatives and unpublished model training data unverified. BLiMP has correlated minimal pairs and W&I sentences may share prompts or source documents. All samples informed development. Treat the exploratory comparisons as descriptive under these conditions.

No qualified human ratings were collected. For sentence and node explanations, two qualified reviewers should grade independently with condition identity held apart, then record disagreements for third-reader adjudication. Rate the grammatical principle, application, word/relationship evidence, structural support and absence of unsupported claims separately. Use `1`, `0`, `U` (unverifiable) and `NA` (inapplicable), with coverage and unavailable cases reported as their own counts. Require conceptual equivalence and falsifiable evidence for corrections and explanations. Include identical and unavailable packets. If review is sampled, freeze strata and inclusion weights, report per-stratum coverage and retain the paired analysis. Report pre-adjudication agreement and clustered uncertainty across sentences/documents, with node judgments nested within sentences. Node prose can be rated on its own merits with this interface. The neural control has no equivalent node prose for a paired causal inference.

## F. Target assessment

| Engineering target | Status | Evidence |
| --- | --- | --- |
| H01 full structural agreement >80% | NOT ACHIEVED | 62.96% full F1 across 216 attempts. The separately reported aligned triangle-aware result is 83.35% on 204 cases. |
| H01 complex structural agreement >80% | NOT ACHIEVED | 53.09% full F1 across 44 attempts. |
| H01 >80% normalization and alignment | ACHIEVED | 213/216 and 204/216. |
| H01 substantial exact-agreement improvement | NOT ACHIEVED | 37/216 full and 112/216 triangle-aware, both unchanged. |
| H02 exact grammaticality verdict >80% | ACHIEVED | 100/116 (86.21%) on exposed BLiMP. |
| H02 independently verified conceptual accuracy >80% | NOT MEASURED | No ratings. |
| H02 >80% supported-scope evidence correctness | NOT MEASURED | Full EXPECT precision 11/16 (68.75%). Fixed participle proxy has 2/2 precision and 2/10 recall at very low coverage. |
| H02 independently assessed correction validity >80% | NOT MEASURED | Official exact-edit precision is 6/13 (46.15%) at the API and 2/6 (33.33%) in learner output. |
| H02 substantially improved supported-scope detection recall | NOT ACHIEVED | Phase 3 proxy counts unchanged. Full EXPECT target overlap fell to 19/169. |
| H02 fewer incorrect conceptual claims without loss of legitimate feedback | NOT MEASURED | API regressions confirm the specific corrected claims. Broad independent assessment remains pending. |

## G. Remaining limitations

| Classification | Concrete remaining work or boundary |
| --- | --- |
| Fixable implementation defects | Some projections still produce same-boundary category disagreements or miss constituent boundaries outside triangles. Parser evidence for an embedded complement or extraction must be checked before modifying attachment. A nested argument NP can lose the applicable article scope, as in `The editor proposed third manipulation of the image.` The fixed simple-NP path correctly flags `third manipulation` in its object use without that PP. |
| Reference representation or evaluation mismatch | Triangle expansions, pedagogical labels, clause outlines, tokenization and competing author readings contribute genuine scorer disagreements. EXPECT's source-side projection and W&I's exact edits omit valid contextual alternatives. |
| Unsupported scope | Broad lexical choice, intended register and discourse ellipsis, plus ambiguous alternations without enough source evidence, cannot all receive an independently supported correction. Some learner inputs contain more than one sentence and are rejected by the frozen single-sentence evaluation path. |
| Architecture limitation | FINAL-D1 can repair some recurring candidate shapes. Where the required competing analysis is absent from the available candidate and source dependencies cannot distinguish readings, the same pipeline cannot verify an intended choice. Grammar and node prose consume structured facts by design, so physically deleting those facts does not yield a comparable explanation channel. |
| Independent validation blocker | No unused, independently checked compatible FINAL-D1 set was found in the reviewed assets. Penn and GUM constituency cannot substitute for Burton–Roberts without a separately validated convention crosswalk. Independent correction and conceptual explanation judgments remain blank. |

## H. Original hypothesis decisions

| Hypothesis | Decision | Reason |
| --- | --- | --- |
| H01 | **NOT STATISTICALLY DETERMINED** | No confirmatory evaluation with independently checked, development-disjoint FINAL-D1 references across complexity levels and a prespecified accuracy estimand and inferential criterion. |
| H02 | **NOT STATISTICALLY DETERMINED** | The neural comparison changes multiple components and measures benchmark verdicts/edits. The narrow licensing intervention does not answer the full claim about unsound feedback. Neither supplies independent judgments of conceptual correctness. |

## I. Reproduction and the next validation actions

Re-run these commands from the repository root with an empty output directory per run and the intended code state active. The baseline artifacts record the original HEAD. Python 3.11.17, spaCy 3.8.16/`en_core_web_md` 3.8.0, Benepar 0.2.0/`benepar_en3`, torch 2.15.0, Transformers 4.46.3 and ERRANT 3.0.0 were used offline. The Benepar checkpoint SHA-256 is `fc465e820f8a62ffc6c23cb7d2ceed61f41d29d1930d471df301f17d3dbb4822`. The cached revisions were `textattack/roberta-base-CoLA@3ccf3a400f2fa75ff257eac171047603ffbe84f1` and `distilbert-base-uncased@12040accade4e8a0f71eabdb258fecc2e7e948be`. The external manifest SHA-256 is `0a0322368b646873a1b42f77571d27259a2e664a1c20b09aa831afd98d1b4672`, external scorer SHA-256 `48cdbba34e775d984544d95b1ca78df45a76676056ad068c5e7f33b5a74ee962`, and digest of the textbook chapter file hashes `768183fc43e25078644b6e6a3d73996f8a7b280af41e9e8ded4b03f30cbb81d0`. [Published source pins and data hashes](SYNTUTOR_CODEX_PHASE3_BENCHMARK_RELIABILITY.md#reproduction-and-artifact-inventory)

```sh
export CGEL_REQUIRE_PARSER=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
export PYTHONDONTWRITEBYTECODE=1
out="$(mktemp -d /tmp/syntutor-h01h02.XXXXXX)"
src=/tmp/syntutor-phase2
audit=docs/audits/technical_evaluation
.venv/bin/python "$audit/run_hypothesis_checks.py" h01 "$out/h01"
.venv/bin/python "$audit/run_reference_specified.py" "$out/br-traces.json" "$out/reference-specified.json" --capture-from "$out/h01/h01.json"
PYTHONPATH="$src/scoring-deps" .venv/bin/python "$audit/run_hypothesis_checks.py" h02 "$src" "$src/external-manifest.json" "$out/h02"
PYTHONPATH="$src/scoring-deps" .venv/bin/python "$audit/run_h02_grounding_comparator.py" "$src" "$src/external-manifest.json" "$out/comparator"
.venv/bin/python -m unittest discover -s "$audit" -p test_hypothesis_methods.py
.venv/bin/python "$audit/verify_metrics.py"
PYTHONPATH=server .venv/bin/python -m unittest \
  test_h01_h02_reliability test_burton_roberts test_br_final_d1_gold \
  test_br_final_d1_dispositions test_br_tree test_canonical_binding test_xai_facts \
  test_findings test_licensing test_corrector test_cross_layer_consistency \
  test_correction_completeness test_learner_analysis test_detection_scoping \
  test_nlp_reliability_regressions test_relative_pronoun test_cambridge_registry \
  test_cambridge_evaluator test_authority test_api_contract
```

At the clean baseline 208 required backend tests passed in 336.398 s. At the final state **227 tests passed**, including the 19 requested modules and API contracts, in 222.233 s with zero failures or skips. The **8** offline scorer and comparator tests passed separately. The historical verifier passed **74 checks** covering 476 raw predictions, 66 metric rows and 56 human worksheet rows with 17 blank rating columns. Early regression probes exposed the directive ambiguity and a test's assumption that an optional revision field was always present. The final checks exercise both the protected directive and the unchanged response contract. Timing varied with CPU contention during inference.

Raw artifacts are in `/tmp/syntutor-codex-final.HU6agF`. Use `baseline-h01/` and `after-h01/` for the original H01 scorer, `baseline-br-traces.json` and `final-br-traces.json` for all per-case structures, `baseline-reference-specified.json` and `final-reference-specified.json` for masks, and `baseline-h02/on/` and `complete-h02/` for grounded and licensing benchmark predictions. `baseline-comp/` and `complete-comp/` contain the neural comparisons. The final worksheet retains 394 paired feedback records and 11 identical unavailable records, all with unique IDs matching the key and all 4,050 rating cells blank. The exact BLiMP discordances and workbook integrity were recomputed from saved records by `verify_comparator.py` at that location. `ARTIFACTS.sha256` records checksums. Keep learner text and the condition key in the private research workspace.

The immediate H01 action is to acquire unseen source sentences across prespecified complexity strata and commission two independent FINAL-D1 annotations, resolve or record defensible alternatives, then freeze the manifest before predictions. H02 first needs a prespecified comparison with comparable feedback opportunities, untouched document-disjoint inputs, and two qualified blinded reviewers. Determine sample sizes from a prespecified acceptable uncertainty or a minimum relevant effect and expected discordant-pair rate, using separate pilot evidence and allowing for document/phenomenon clustering. Fix one primary endpoint per intended claim before testing. No amount of rerunning an exposed benchmark resolves either evidence gap.
