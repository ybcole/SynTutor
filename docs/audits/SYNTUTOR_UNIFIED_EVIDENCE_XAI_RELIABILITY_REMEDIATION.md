# SynTutor evidence and XAI reliability checkpoint

This checkpoint indexes the evidence available at the independent Antigravity handoff review. It records the implementation and its verification boundary. Defect reproductions, current environment, exact commands, browser results, release blockers and benchmark suitability are in the [independent handoff review](SYNTUTOR_INDEPENDENT_AGY_HANDOFF_REVIEW.md). Earlier measurements and the broader risk inventory remain in the [real-world remediation](SYNTUTOR_COMPREHENSIVE_REAL_WORLD_RELIABILITY_REMEDIATION.md), [cross-layer linguistic consistency report](SYNTUTOR_CROSS_LAYER_LINGUISTIC_CONSISTENCY.md) and [final check](SYNTUTOR_SYSTEM_RELIABILITY_FINAL_CHECK.md).

## Execution path and authority

`webapp.py` passes validated, indexed text through `analysis_api.py` to spaCy and Benepar. The parser yields source tokens, morphology, and a candidate constituent tree. FINAL-D1 projects the candidate into a canonical B–R structure when its criteria hold. `matrix.py`, `ruleset.py` and `licensing.py` generate their own findings. Cambridge eligibility and probe evaluation are separate. CoLA contributes advisory evidence. `findings.py` verifies and maps learner findings. The correction layer assembles and checks edits. `learner_explanations.py` and the XAI evidence modules support sentence and node explanations, which share references through the API and frontend. The Builder uses the same evidence API. The latest code fixes preserve those responsibilities.

The committed runtime inventory is represented by [`CONSTRAINT_RULE`](../../server/matrix.py), [`ruleset.py`](../../server/ruleset.py), [`licensing.py`](../../server/licensing.py) and the [Cambridge runtime registry](../../grammar/runtime_registry.json). Some constraints occur only in candidate or otherwise gated paths. The legacy teaching sheet has 112 numbered topics and 175 Stage 4 rows. The 14 newer IDs and the separate `9.15` polarity collision are enumerated in the handoff review. The current structural category inventory is the [canonical schema](../canonical-burton-roberts-tree.schema.json) and its [FINAL-D1 display label registry](../../server/final_d1_labels.py). `xai_facts.py`, `learner_explanations.py` and `node-lessons.js` consume the relevant structural or lexical evidence. A schema label indicates a representation the software supports. Contextual explanation coverage depends on which roles and facts the analysis established.

## Requirements traceability

Verified describes the indicated checks. Partially Verified marks tested subsets or remaining annotation and coverage gaps. The paths in the table are relative to the repository root.

| Requirement | Implementation and verification evidence | Status and limit |
|---|---|---|
| 1 Architecture | Offline backend suite, `scripts/test_runtime_packaging.py`, real Flask `/api/health` and asset identity | Verified for this change set |
| 2 Evidence propagation | `server/findings.py`, `server/test_learner_analysis.py`, live cross-layer XAI | Partially Verified across tested rule families |
| 3 Rule inventory | Runtime registry and matrix mappings, legacy `RULEBOOK`, both tree-sheet build orders and legacy disposition test | Verified for repository inventory boundaries. Linguistic adequacy by family remains partial. |
| 4 Canonical and provisional | `server/final_d1_projection.py`, Generator canvas and real-world browser regressions | Verified distinction for tested cases |
| 5 Word explanations | `server/learner_explanations.py`, morphology and contraction tests, selected `know` in Chromium | Partially Verified. Context varies by available evidence. |
| 6 Phrase explanations | `server/xai_facts.py`, sentence-awareness and cross-layer browser checks | Partially Verified. Attachment and ambiguity require further adjudication. |
| 7 Clause explanations | `server/learner_explanations.py`, independent wh and conditional cases | Partially Verified. Verbless supplement classification remains a risk. |
| 8 Node categories | Canonical schema, `server/test_explanation_coverage.py`, Generator/Builder selections | Partially Verified. Category coverage differs from verified linguistic quality per node. |
| 9 Relations | Learner analysis tests plus live evidence for agreement, auxiliaries, temporal adjuncts and negation | Partially Verified. Legacy ID/constraint teaching join is covered by an API regression. |
| 10 Error association | `server/findings.py`, `web/js/explanation-evidence.js`, interactive XAI browser | Partially Verified. The browser test covers example targets and supporting nodes. |
| 11 Highlight synchronization | Interactive XAI and UI prototype suites | Verified for exercised selection and correction sequences |
| 12 Source alignment | Real-world browser, canonical validation, correction and legacy node map tests | Partially Verified across contractions, Unicode and tested parse spans |
| 13 Selection lifecycle | Generator/Builder and UI refinements browser suites, XAI keyboard controls | Verified for tested transfer, clearing and reload paths |
| 14 Linguistic accuracy | Clause and correction regressions, contextual `ever` controls and API evidence notes | Partially Verified. Independent human ratings remain unmeasured. |
| 15 Grammatical and ungrammatical inputs | `server/test_nlp_reliability_regressions.py`, verb/auxiliary and polarity contrasts | Partially Verified across tested construction families |
| 16 Names and unfamiliar words | Naomi/Unicode browser, proper-name and homograph tests | Partially Verified. New lexical forms remain uncertain where evidence is sparse. |
| 17 Spelling and multiple errors | `server/test_real_world_nlp.py`, interactive and cross-layer browser correction checks | Partially Verified. Learner-intent ambiguity can withhold edits. |
| 18 Meaning preservation and correction | `server/corrections.py`, correction completeness suite, removal of automatic polarity edit, negative controls | Partially Verified. Human meaning judgments remain unmeasured. |
| 19 Incomplete analyses | `They demolished.` and provisional auxiliary/conditional contrast in live browser | Verified for the exercised failure modes |
| 20 Lesson relevance | `test:node-lessons`, live cross-layer routes and Foundations preview | Partially Verified. Scope beyond exercised learner concepts requires curriculum review. |
| 21 Positive and negative controls | Runtime overlay adversarial test, grammar polarity pair, build and API tests | Verified for this change set |
| 22 Invariant and metamorphic tests | `test_nlp_reliability_regressions.py`, API serialization, existing structure and learner checks | Partially Verified. Further construction and interaction generation remain open. |
| 23 Boundary tests | Real HTTP symbol-only input, rare vocabulary and Unicode; transport tests in backend discovery | Partially Verified. Broad fuzz testing remains open. |
| 24 Browser verification | Runtime Chromium suite and three model-free browser suites in the handoff review | Partially Verified. Native account flow requires local or hosted PostgreSQL. |
| 25 Human-review preparation | Preserved blinded V4 and earlier worksheets, 74 integrity checks | Verified for preparation and preservation. Reviewer scores remain unmeasured. |
| 26 Reproducibility | Frozen V4 hash, untouched predictions, commands and local transcripts in handoff review | Verified for reproduced technical results. New independent benchmarks remain unfrozen. |
| 27 JFLEG investigation | Compared three preserved 20-case prediction sets by item ID and frozen label | Verified. One prediction accounts for the historical change. |
| 28 Historical browser failures | Builder/Generator and Quiz V2 passed on the target checkout | Verified for both previously reported scripts |
| 29 Performance and maintainability | Backend suite wall time, cached analysis for UI node selection, live request assertions | Partially Verified. No matched before/after latency or memory study was run. |
| 30 Documentation and release decision | Handoff review, continuous progress and preserved earlier audits | Verified for this checkpoint. Formal curriculum and assessment release gates are blocked. |

Measure any new learner-writing structural agreement against independently adjudicated B–R references, with labeled and unlabeled boundaries reported separately from normalization coverage. Evaluate corrections for error coverage, new errors, meaning and minimality. Treat automated explanation grounding, linguistic accuracy and learner usefulness as separate outcomes. The five resource assessments and corpus-overlap requirements are documented in the handoff review.
