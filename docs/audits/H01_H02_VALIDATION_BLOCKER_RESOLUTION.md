# H01 and H02 validation blocker resolution

22 November 2026. The focused runs used branch `fix/syntutor-system-reliability-xai`, commit `e1d887d67d1f5e95d5b038b9d662f007c20229d1`, with spaCy 3.8.16, `en_core_web_md` 3.8.0, Benepar 0.2.0 with `benepar_en3`, Torch 2.15.0 and Transformers 4.46.3. The sole executable change is the [offline evaluation runner](technical_evaluation/run_hypothesis_checks.py). Production, the four hypotheses, the manuscript and existing results were preserved.

## H01 — Complete Benepar → Burton–Roberts pipeline

**Resolved and executed.** The runner called spaCy/Benepar and the production FINAL-D1 projector directly. It installed a lookup sentinel for the duration of the test and verified zero calls. The unchanged legacy run reproduced the Phase 3 `textbook-parseval.json` byte for byte. The additional scorer reports what happens when the 30 unaligned or unresolved inputs remain in the denominator. [Reference loader](../../server/br_tree.py), [FINAL-D1 projector and lookup](../../server/burton_roberts.py), [historical scorer](technical_evaluation/run_real_world_reliability.py)

| Measure | Reproduced result |
| --- | ---: |
| Canonical and schema-valid | 201/216 |
| Yield-aligned canonical | 186/216 |
| Unresolved, all with working trees | 15/216 |
| Canonical with mismatched yield | 15/216 |
| Full labeled F1, aligned cases | 68.46% |
| Triangle-aware labeled F1, aligned cases | 84.31% |
| Full exposed-span exact, all inputs | 32/216 |
| Triangle-aware exposed-span exact, all inputs | 101/216 |
| Full labeled F1, all attempts | **59.53%** |

All-attempt F1 is `2 × 903 / (1,195 + 1,839)`. An unresolved item contributes all its reference spans and zero canonical predictions. A yield mismatch contributes reference and predicted spans with zero matches. The 216 include fragments and partially expanded diagrams. Among 106 references rooted in `S` or `Sentence`, 88 align, two match exactly and all-attempt F1 is 55.97%. With zero, one, and two or more explicit `S` nodes, all-attempt F1 is 61.09% (83 inputs), 64.12% (90), and 51.76% (43). These are source-side complexity proxies. Collapsed constituents can hide clauses and the same sentence can have several diagrams. The exposed textbook sample cannot establish a significance claim or accuracy on unfamiliar English across complexity levels. No success threshold was introduced. [Published-record provenance and limitations](H01_H02_EVIDENCE_VALIDITY_AUDIT.md), [reference JSON](../../web/content/book)

**Verified one additional author diagram.** All 11 supplied chapter PDFs matched the stored SHA-256 records. The 263-page combined copy covers printed pp. 6–268 and has SHA-256 `9dee17db3021b45216f9e005eccfdb9f82880ada5fbc852a5fc0945735f22f31`. I inventoried pages for diagram graphics and visually checked likely omitted examples. Chapter 10, p. **239**, sentence **[79a]** and diagram **[79b]**, give the phrase marker for “He didn’t remember kissing Millie.” It was absent from the imported trees, searched fixtures and saved prediction records. I transcribed the visible diagram without expanding the two NP triangles or inventing a realization of C1. The diagram shows a `TENSE [past]` node, an embedded `S′` with empty C1, and the covert subject coindexed with the matrix subject. This is a source transcription checked against the printed figure. A second reader has yet to verify it.

The full pipeline returned a canonical tree for [79b]. The unchanged scorer rejected the leaf split `did` + `n’t` versus printed `didn’t`. The separate lexical-character comparison required identical overt characters apart from apostrophe typography and obtained **8/8 exposed labeled spans**. It detected a deliberately changed lexical yield as unequal. This check does not certify metadata or expand the author's triangles. The source case stays outside the historical 216. On p. 236, [38c] supplies a subject NP only. Pages 248 and 251 contain abbreviated clausal analyses. Page 266, [12], is deliberately introduced as a tree for an unacceptable string. None supplies an additional full affirmative sentence key for FINAL-D1. [Burton–Roberts third-edition record](https://eprints.ncl.ac.uk/157385), [chapter source manifest](../../sources/burton_roberts/source_manifest_2026-11-08.json), [transcription and alignment check](technical_evaluation/run_hypothesis_checks.py)

**Final readiness.** The complete-pipeline benchmark is reproducible and ready for descriptive reporting. Fresh independent FINAL-D1 testing is still blocked. One newly found textbook diagram cannot supply independent complexity strata. The preface, p. x, directs teaching staff to the author-prepared *Answer Book for the Further Exercises*. The materials inspected contain prompts on pp. 220–221 and 251–253. Access to their answer diagrams and their convention compatibility remain unconfirmed. The immediate action is for an authorized instructor or librarian to obtain the third-edition answer book, have two readers verify eligible full diagrams, and seal a complexity-stratified, deduplicated case list before testing. The Penn reference plan cannot answer the canonical H01 question. [Third-edition preface copy](https://muugumuugu.github.io/bOOkshelF/languagesNcodes/Analysing%20sentences.pdf)

## H02 — Paired feedback from the real SynTutor pipeline

**Resolved and executed a component comparison.** The matrix generates diagnostics, licensing supplements them, and `supported_findings` corroborates and localizes learner-facing findings. Corrections are assembled and rechecked from actual diagnostics. Cambridge independently evaluates applicable normalized analyses through its registry. The grounded ON arm uses the unchanged API. OFF suppresses only `check_lexicon` and `check_relatives` in the evaluation process for the source input and any correction reanalysis. It preserves the matrix, other deterministic rules, Cambridge, Benepar, the CoLA advisory channel, evidence routing and the same correction and explanation renderers. No unrelated model was used. This isolates the incremental effect of the two positive-evidence licensing checks. Disabling all matrix and evidence sources would deprive the existing correction and grammar explanation channels of their inputs and would not give an active baseline for the broader hypothesis. [Matrix](../../server/matrix.py), [licensing](../../server/licensing.py), [Cambridge evaluator](../../server/cambridge_evaluator.py), [finding validation](../../server/findings.py), [production analysis and corrections](../../server/analysis_api.py), [learner explanations](../../server/learner_explanations.py)

All **405 identical inputs** ran in both arms. The raw parses, Cambridge results, tree status and advisory outputs agreed across arms. Cambridge evaluated 194 selected sentences and returned four findings. The pipeline raised no request exceptions. Eleven segmented or incomplete whole-item selections were retained as failures by the relevant scoring adapters. Forty-five saved feedback packets differed. Both arms produced 405 sentence text fields and 400 node-prose packets, including qualified or provisional messages. The learner findings channel contained findings in 133 OFF versus 142 ON packets. Availability and agreement are delivery checks.

| Published reference and outcome | Licensing OFF | Licensing ON |
| --- | ---: | ---: |
| BLiMP exact verdicts, abstentions counted as nonmatches | 85/116 | 85/116 |
| BLiMP unverified, false ungrammatical on grammatical, missed ungrammatical labeled grammatical | 15, 8, 8 | 16, 8, 7 |
| BLiMP learner finding presence on ungrammatical / grammatical inputs | 39/58 / 4/58 | 39/58 / 4/58 |
| W&I+LOCNESS API correction TP/FP/FN and ERRANT F0.5 | 4/7/189, 0.0844 | 5/6/188, 0.1055 |
| W&I+LOCNESS learner-visible correction TP/FP/FN and F0.5 | 1/4/192, 0.0235 | 2/3/191, 0.0469 |
| EXPECT target overlap and source evidence TP/FP/FN | 14/169, 6/4/199 | 16/169, 6/4/199 |

BLiMP had 58 minimal pairs and two exact-verdict wins in each arm. W&I had 120 inputs with 193 scored edits, two whole-item failures and five learner-visible revisions per arm. EXPECT had 169 annotations with 205 source evidence tokens and nine whole-item failures. Its two extra anchors, **91** and **922**, had no source witnesses after projection, so evidence F1 stayed **0.0558**. ON's historical W&I API hypothesis file and EXPECT prediction file matched Phase 3 byte for byte. W&I matches an annotated edit and may miss valid alternatives. EXPECT compares localized evidence and has no prose answer key. All three samples informed previous development and remain diagnostics. [BLiMP](https://aclanthology.org/2020.tacl-1.25/), [W&I+LOCNESS and ERRANT](https://aclanthology.org/W19-4406/), [EXPECT](https://aclanthology.org/2023.acl-long.413/), [frozen source hashes and scoring configuration](SYNTUTOR_CODEX_PHASE3_BENCHMARK_RELIABILITY.md)

**Independently checkable feedback examples.** On W&I `B.dev:605`, ON exposed the published spelling repair `experinces` → `experiences` and a corresponding explanation. Two other annotated edits were still absent. On `A.dev:123`, **both** arms explained that `new stuff` needed an article because `stuff` was countable. The standard sense here is uncountable. OFF also proposed `a new stuff` in the API correction field, but that correction was withheld by both learner-facing payloads. The correction gate prevented display of that rewrite and the incorrect prose persisted. These examples verify specific claims and cannot establish an error rate for sentence or node explanations. [Cambridge English Grammar Today, *Thing and stuff*](https://dictionary.cambridge.org/grammar/british-grammar/stuff)

**Final readiness.** The scoped licensing comparison is executable and has preserved learner packets. The original H02 remains untested. The benchmarks give no independent full correctness labels for grammar or node prose, and the ablation leaves the core matrix and its grounding in both arms. Before another inference run, use the saved changed cases and neutral controls to calibrate the existing [blinded worksheet](technical_evaluation/H02_BLINDED_REVIEW_WORKSHEET.csv) with qualified reviewers. For a confirmatory whole-system comparison, agree the active baseline and whether the claim is causal or a system comparison before freezing untouched author/essay groups. Measure paired material-error and adequate-feedback rates with abstentions retained. A component result cannot be substituted for the original hypothesis.

## Reproduction

Run from the repository root. The Phase 3 report lists the original source URLs and pins. The Phase 2 external manifest SHA-256 is `0a0322368b646873a1b42f77571d27259a2e664a1c20b09aa831afd98d1b4672`. Its three relevant source hashes and the unchanged scoring adapter hash are enforced by the runner. ERRANT 3.0.0 is in the existing Phase 2 scoring dependency directory.

```sh
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false PYTHONDONTWRITEBYTECODE=1
runner=docs/audits/technical_evaluation/run_hypothesis_checks.py
out="$(mktemp -d /tmp/syntutor-hypotheses-repro.XXXXXX)"
.venv/bin/python "$runner" h01 "$out/h01"
PYTHONPATH=/tmp/syntutor-phase2/scoring-deps .venv/bin/python "$runner" h02 \
  /tmp/syntutor-phase2 /tmp/syntutor-phase2/external-manifest.json "$out/h02"
```

Raw artifacts are under `/tmp/syntutor-hypothesis-check/{h01-final,h02}/` with checksums in `/tmp/syntutor-hypothesis-check/ARTIFACTS.sha256`. This includes each attempt, the separate [79b] source comparison, both arms’ feedback packets, exact-edit M2 and EXPECT records, failures and the paired-difference list. Keep the licensed learner text in the local research workspace.
