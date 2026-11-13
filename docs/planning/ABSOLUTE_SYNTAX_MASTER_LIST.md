# SynTutor absolute syntax master list

**Audit dated 13 November 2026.** This is the implementation register for Burton-Roberts tree fidelity and SynTutor's versioned tree contract. The source is Noel Burton-Roberts, *Analysing Sentences: An Introduction to English Syntax*, third edition (2011), including the attached complete PDF. The cited printed pages refer to the book, not PDF offsets. This document records findings and required work. It does not certify universal parser accuracy.

**Product decision:** Benepar remains the general English parser. SynTutor translates its proposed analyses into the B-R teaching convention and validates those translations. The goal is broad practical coverage comparable to Benepar's, with correct B-R labels and structures for supported inputs. Building a second unrestricted native parser is optional research, not a prerequisite. A source-tree corpus is a test and teaching resource, not the only set of sentences the adapter may handle.

## The meaning of one-to-one

For a specified interpretation and convention profile, a supported analysis must serialize into one lossless, ordered SynTutor tree with exact token alignment. Decoding that tree must recover its nodes, labels, features, spans, dependencies, profile, and source. A sentence can have several legitimate analyses. Chapter teaching versions can represent the same words differently. SynTutor must retain accepted alternatives or return unresolved when an interpretation cannot be chosen. A single sentence cannot always have one objectively unique tree.

## Audit verdict and authority

The chapter-aware convention is coherent as a design, but it is **not yet complete or fully coherent across runtime contracts and documentation**. The main convention is [CONVENTIONS.md](../../CONVENTIONS.md), with versions V1–V10 and free-analysis FINAL-D1. The public envelope is [canonical-burton-roberts-tree.schema.json](../canonical-burton-roberts-tree.schema.json). The actual importer and Benepar adapter are in [burton_roberts.py](../../server/burton_roberts.py) and [final_d1_projection.py](../../server/final_d1_projection.py). An older [br_tree.py](../../server/br_tree.py) and [br_tree.schema.json](../../grammar/br_tree.schema.json) use a different internal shape. The [construction catalog](../../grammar/br_native_constructions.json) checks shapes, while [br_native_chart.py](../../server/br_native_chart.py) generates limited diagnostic candidates. None of these alone proves the analysis of novel unrestricted English.

| Evidence | Current result | Meaning |
|---|---:|---|
| Source corpus, Chapters 1–10 | 252 trees | 234 IMG, 14 derived from instructions, 4 image anomalies. |
| Catalog branch recognition | 1,382 / 1,558, or 88.7% | 176 branch instances need triage. Shape recognition does not check semantic conditions. |
| Independently verified trees in catalog audit | 0 | The selected-page AI recheck of 8 November is not corpus-wide independent linguistic certification. |
| Cambridge production rules | 0 | Cambridge explanations and diagnostics have separate licensing. |

Reproduce the catalog numbers with **python scripts/audit_br_native_catalog.py --expected-count 252 --fail-on-penn**. Its semantic_conditions_checked value is false. Do not boost that percentage with indiscriminate shape rules.

Burton-Roberts third edition governs canonical tree structure. A reviewed source diagram governs its particular exercise, including visible anomalies. The chapter prose governs constructions beyond those figures after the reading is adjudicated. Benepar supplies general sentence analyses and likely attachments; the adapter may reuse these as evidence while building B-R structures. B-R conventions determine what is shown and taught. Cambridge supplies independently attributed grammar constraints, not B-R edges. A schema-valid tree, a catalog-recognized shape, a source-image transcription, and an independently verified linguistic interpretation are different claims.

## Complete profile inventory

| Profile | Book location | Defining obligations |
|---|---|---|
| V1 | Ch1, printed pp. 6–23 | Sentence, schematic phrases, dominance, constituents, triangles; preserve original letters. |
| V2 | Ch2, pp. 24–45 | S with NP subject and VP predicate after category introduction; the earlier introductory Sentence display stays as printed. Functions are derived. |
| V3 | Ch3, pp. 46–66 | Lexical/phrasal categories; name/pronoun NP; PP, AP, AdvP; coordination; NP internals still use schematic placeholders. |
| V4 | Ch4, pp. 67–86 | Lexical V and six complement frames: intrans, trans, ditrans, intens, complex, prep. |
| V5 | Ch5, pp. 87–110 | Nested VP for adjuncts, higher S for sentence adverbials, particles, ellipsis E and stated simplifications. |
| V6 | Ch6, pp. 111–140 | MOD, PERF, PROG, PASS, TENSE, recursive auxiliary VPs, tense, fronting C and licensed gaps. |
| V7 | Ch7, pp. 141–170 | DET/NOM, recursive modification, possessives, PRE-DET, empty DET, PartP, separate Appendix NOM refinement. |
| V8 | Ch8, pp. 171–195 | S-bar/C/S, clausal arguments and adjuncts, selected S versus S-bar, extraposition, ACA. |
| V9 | Ch9, pp. 196–223 | S-dbar/C2/S-bar/C1, empty C1, wh movement, relative attachment and category-sensitive gaps. |
| V10 | Ch10, pp. 224–253 | Nonfinite clauses, negative tense feature, controlled subjects, indices, Type I/II verb patterns. |
| FINAL-D1 | Free analysis | Cumulative through Ch10 with the Ch7 Appendix NOM refinement; this is a SynTutor profile. |
| Ch11 | pp. 254–268 | Theory without a new phrase-marker version. |

The examples, source citations, inventories, tests and chapter-specific simplifications in CONVENTIONS.md §§2–9 remain the detailed specification. A chapter exercise must use its chapter profile. A free sentence must declare FINAL-D1. Each construction rule needs its introduction chapter and exact permitted profiles.

## Canonical serialization requirements

1. The public result is the versioned **br_analysis.tree** envelope. Its sentence, selected profile, source, stable analysis ID, ordered root, lexical tokens, half-open character and token spans, movement/control records, alternatives and notes must survive a save/load round trip. API top-level tree and candidate_tree are parser diagnostics until all consumers migrate.
2. Every overt token occurs exactly once, in order. Define reversible alignment for punctuation omitted from book phrase markers, apostrophes, contractions, hyphens, compounds, whitespace, Unicode and multi-sentence selection. A lexical-yield match alone must not transfer a tree across meaning-changing punctuation.
3. Allow only the source-supported node variants: labelled branches, terminals, triangles, gaps, covert positions and typed empty positions. E is ellipsis, not a movement gap. An unlabelled wh triangle is allowed only in its licensed C2 context. No fabricated overt word or unsupported zero-width node.
4. Store S-bar and S-dbar for displayed S′ and S″. Preserve AP and AdvP rather than Penn labels. The infinitival to is AUX with the negative tense feature. Grammatical functions are overlays inferred from licensed structure; subject, dO, adjunct and similar functions are not phrase-marker nodes.
5. An accepted alternative has its own analysis ID, root, profile, source and meaning or acceptance state. Keep multiple source-authorized readings. Parser hypotheses remain separate from accepted alternatives.
6. Check schema and token coverage, profile legality, constructive shape, lexical selection, attachment, feature agreement, movement/control dependencies, interpretation and provenance as separate validation levels. A pass at a lower level never implies a higher one.

## Source and contract work

| ID | Work to complete | Proof of completion |
|---|---|---|
| S01 | Resolved: FINAL-D1 uses the Appendix NOM distinction; V7 core figures and Appendix exercises retain distinct profiles. | CONVENTIONS.md §9 now states the choice, supported by the book's pp. 167–168 contrast. Runtime already selects these profiles. |
| S02 | Adjudicate all 252 source records against PDF images and prose, including 14 derived and 4 anomalies. | Per-record figure/page, reviewer, outcome, alternatives and disputed readings. |
| S03 | Triage all 176 unmatched branch instances. Early PHRASE and S scaffolds may be pedagogical rather than productive grammar. | Figure-level disposition for each unmatched signature, without a global catch-all. |
| S04 | Examine later missing signatures: C2 to unknown, VP to VP NP, PP/AP/AdvP gaps, NOM to N AP or PartP N, VP to V S-bar, NP to NP S-dbar. | Exact source examples, narrow construction rules or explicit unsupported status. |
| S05 | Make the schema, importer, validator, Builder and renderer agree on E, empty DET/C1, unlabelled C2 triangles, covert subjects, indices and movement. | Lossless round trip and source-fixture tests for every variant. |
| S06 | Set feature identity and order. The tree evaluator currently sorts features for comparison, while FINAL-D1 has a displayed order. | Explicit display and equality policy with permutation tests. |
| S07 | Specify punctuation and tokenization for source lookup and arbitrary input. | Offset round trips and adversarial punctuation/contraction cases. |
| S08 | Define ambiguity, chapter simplification, source alternatives, interpretation and target grading. | Gold alternative sets and graded examples that depend on meaning. |
| S09 | Separate IMG transcription, AI source pass, independent linguistic review, anomaly and release approval. | Enforced provenance fields and review trail, without bulk self-approval. |
| S10 | Reconcile PDF pagination and edition manifests. The attached volume has 297 PDF pages; the older 294-page claim is corrected. | Confirm page offsets and edition for every source fixture before marking the full corpus reviewed. |

## Benepar adapter and validation work

| ID | Work to complete | Acceptance evidence |
|---|---|---|
| P01 | Build an explicit Benepar-to-B-R transformation table by construction and chapter profile. Reuse reliable token spans and phrase attachments, and reconstruct B-R-specific layers. | Positive, negative, exception and ambiguity cases for each transformation. |
| P02 | Add lexical frame evidence where Benepar's categories cannot decide Ch4 complement type, auxiliary role, particles, prepositions, sense ambiguity or Ch10 Type I/II. | Unseen verb/sense contrasts and explicit unresolved unknowns. |
| P03 | Transform parsed NP into DET/NOM, VP into B-R auxiliary and adjunct layers, and clauses into S-bar/S-dbar, covering coordination and nonfinite structures. | Source and held-out complete-tree matches under the correct profile, with comparable general-input coverage measured. |
| P04 | License wh, passive, fronted auxiliary, gap, empty C, ellipsis, controlled subject and co-index. | Every non-overt position has a tested controller or dependency and adversarial negatives. |
| P05 | Validate the adapter's local transformations, lexical selection, scope, agreement and attachments. | Reject deliberately wrong but schema-valid trees with precise failed obligations. |
| P06 | Preserve and evaluate alternatives when Benepar or the B-R mapping is ambiguous. Add a second candidate only where evidence supports one. A native chart is optional research. | Held-out parser-disagreement cases, ambiguity recall and explicit unresolved outcomes. |
| P07 | Keep Penn POS, model scores and Cambridge claims from becoming B-R proof. | Negative integration tests across normalizer, API, and frontend. |
| P08 | Separate structural validation, grammaticality findings, corrections and explanation evidence. | Distinct statuses and rule IDs, including a structurally valid tree for an unacceptable sentence. |
| P09 | Version analysis identity by source/profile, derivation and tokenizer. | Stable reload and invalidation after rule/profile changes. |

The existing FINAL-D1 projection is the starting point. Expand its construction mappings and measured coverage before investing in an independent full parser. The small hard-coded chart can remain a diagnostic or supply alternate hypotheses where it helps. Successful projection still needs rule-specific checks. The catalog's shape conditions are descriptions and are not currently executable checks.

## Product, removal and migration list

| ID | Surface | Required outcome |
|---|---|---|
| U01 | Generator | Show canonical and explicitly working analyses with correct status, profile and uncertainty; identify parser diagnostics. |
| U02 | Builder | Edit and round-trip every node variant, profile, source, span, index, movement link and alternative. |
| U03 | Lessons/quizzes | Version answer keys by source, chapter, accepted readings and simplifications. Grade hierarchy, order, features and dependencies. |
| U04 | XAI | Tie each structural explanation to B-R evidence and each Cambridge constraint to its separately reviewed record and exact governing nodes. |
| U05 | Corrections | Reparse repaired text, preserve original/revised offsets and do not infer whole-sentence correctness from partial checks. |
| U06 | Transports/storage | Audit browser, server, hosted API, old lessons, database and exports for old schema consumers and Penn renderers. Migrate with old-workspace fixtures. |
| U07 | Documentation | Update stale syntax-generator-api.md statements about V2-only support, the 196-rule Cambridge snapshot and unrun parser CI; reconcile D1 and legacy contracts. |

Retain source records, anomalies, raw diagnostics and accepted alternatives. Remove obsolete authority paths after migration: implicit Penn relabelling, unqualified canonical claims for working trees, source-review claims based on shape matching and duplicate public schema claims. Deprecate the older internal schema only after caller inventory and backward-compatibility checks.

## Completion gates and sequence

1. **Source fidelity:** adjudicate all source records and alternatives; dispose of every unmatched branch and ambiguous transcription.
2. **One contract:** make public schema, importer, validator, Builder and display agree; round-trip all representable source records and old saved workspaces.
3. **Broad Benepar adapter:** transform its analyses under the selected B-R profile, checking lexical selection, attachments and dependencies with explicit unknown outcomes.
4. **Independent measurement:** use separate development and held-out source/new-sentence sets. Report exact complete-tree agreement against alternatives, verified coverage, false certification rate, ambiguity recall, calibration, latency and unsupported cases with denominators and uncertainty. No finite zero-failure suite guarantees every English sentence.
5. **Integration:** test Generator, Builder, lessons, quizzes, XAI, corrections, API transports, browser and parser-backed CI through their normal entry points.
6. **Release:** activate only reviewed, measured construction families and publish their supported coverage and limitations.

**Current gate state:** the D1 profile decision and the known PDF-page-count mismatch are resolved in the convention documents. Source fidelity across all records remains incomplete; contract, adapter and product integration are partial; broad B-R presentation at Benepar's coverage has not yet been measured. Start with the P01 construction map and representative held-out sentences alongside S02–S04 and the source fixtures, expand P02–P05 by construction, then evaluate P06 and U01–U07. Finish the source review and contract tasks before claiming independently certified fidelity. Cambridge Phase C diagnostic pilots have a separate registry and review path.
