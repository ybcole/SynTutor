# Master Prompt — SynTutor Contextual XAI Engine

**Use with:** [XAI Master Plan](XAI_MASTER_PLAN.md) and [Uploaded-book Source Audit & Multi-Error Protocol](XAI_SOURCE_AUDIT_MULTI_ERROR.md)  
**Status:** Implementation instructions; XAI-PRE contracts, XAI-0 real-parser baseline and **XAI-1 page-checked English-only concept registry** are implemented. Independent human linguistic approval remains outstanding; the XAI-2 structural observation graph is implemented without activating unreviewed functional roles; XAI-3 deterministic, evidence-bound English contextual observations are implemented (technical CI review pending); XAI-4 typed candidate partial evaluation is technically implemented with zero approved/enabled Cambridge diagnostic rules (human source-release gate outstanding). XAI-5–XAI-8 remain subsequent work. No independently unapproved function, complement, head or grammar rule is active. See [XAI-1 acceptance](../reports/xai-1-source-concepts-acceptance-2026-11-10.md).  
**Authority:** Noel Burton-Roberts, *Analysing Sentences*, Third Edition (2011), for tree structure; Huddleston and Pullum et al., *The Cambridge Grammar of the English Language* (2002), for descriptive grammatical knowledge subject to review and source-specific differences.  
**Repository:** `ybcole/SynTutor`

## Role

Act as the senior computational linguist, NLP engineer, XAI designer and code reviewer responsible for SynTutor's book-grounded explanation engine. Your job is to implement **accurate sentence-specific explanations for every relevant Burton-Roberts tree node**, and rule-backed error diagnosis where independently evaluated evidence warrants it.

Work within the existing repository, using its canonical B–R tree, source registry, chapter convention profiles, and shared Generator/Builder evidence contracts. Do not invent book claims, redesign the underlying grammar model without a separate review, or claim human sign-off based on AI review.

## Objective / non-negotiable product behavior

When the learner selects a word, lexical head, phrase, clause, feature row, edge or error, SynTutor should explain **why that element has that category, what it does in the actual sentence, what contextual evidence supports the explanation, and which grammatical rule applies if any**.

The same word can have different syntactic functions in different sentences. The same label `NP` can denote a subject, object or other function. Never return merely "NP means noun phrase" or "had is wrong" absent the relevant constituent, grammatical condition, interpretation and source.

The system must distinguish:

- **Observed tree facts** — directly derivable from the canonical B–R tree.
- **Book-backed structural principles** — source-reviewed B–R construction conditions.
- **Book-backed grammatical constraints** — source-reviewed Cambridge rules with an executable checker, complete prerequisites and exceptions.
- **Provisional observations** — structural tree span without approved interior analysis or semantics.
- **Error findings** — verified relationship-level failures and their localized words/governors.
- **AI paraphrases** — optional natural-language rephrasings of permitted atoms; never independent truth.

## Read first: repository and books

Before any edits, inspect:

1. `docs/planning/XAI_MASTER_PLAN.md` **and** `docs/planning/XAI_SOURCE_AUDIT_MULTI_ERROR.md` in full, plus this prompt. Complete XAI-PRE before implementing XAI-0.
2. `docs/planning/master_plan.md` and `docs/planning/master_checklist.md`, especially the earlier explanation section (foundation only).
3. `CONVENTIONS.md` and `docs/BR_NATIVE_ENGINE_CONSTRUCTION.md`.
4. `server/burton_roberts.py`, `server/final_d1_projection.py`, `server/br_native_grammar.py`, and `grammar/br_native_constructions.json`.
5. `server/explanations.py`, `server/cambridge_evaluator.py`, `server/cambridge_registry.py`, `server/tree_evaluation.py`, `server/api.py`.
6. `grammar/explanation_templates.json`, `grammar/explanation_templates.schema.json`, `grammar/runtime_registry.json`, `grammar/rules/*.json`.
7. `web/js/canonical-view.js`, `web/js/explanation-evidence.js`, `web/js/main.js`, `web/js/lessons-ui.js`, `web/js/ui.js`, and existing correction and Quiz/Builder consumers.
8. The primary book pages relevant to the specific construction being enabled. Use supplied book PDFs / actual provided source evidence when available; do not replace them with inferred facts or a generic web article.

At the start of a milestone report the actual current template/source counts, active Cambridge rule count, current tests, known gaps, and affected compatibility contracts. **Never say an architecture or test suite is complete just because a schema or placeholder was added.**

## Implementation phases

Follow XAI-0 through XAI-8 in the master plan, in order. Implement one coherent vertical slice at a time, with an explicit acceptance gate, runnable tests and a status report.

### Phase PRE — Book coverage and interacting-error protocol (mandatory, no code enablement)

Before running or implementing XAI-0, inspect the **attached original Burton-Roberts third-edition and Cambridge Grammar PDFs** and the source-map audit. The chapters and printed pages identified there are selected verifications, not proof of exhaustive source coverage. Distinguish a chapter-topic inventory from independent page-by-page rule approval.

Concretely verify B–R Ch. 6 pp. 116–118 and Cambridge Ch. 3 pp. 74–77, 106, 143–145 for auxiliary/participle terminology, form-selection rules, syncretism and tense/aspect exceptions. Preserve Cambridge's descriptive variety and symbol distinctions. Source-check each new runtime rule and its exceptions against **its own source pages** before enabling it.

Use the XAI-PRE assets already committed—`grammar/xai_pre/source_audit.json`, `docs/xai/diagnosis-repair-pre.schema.json`, `server/xai_preflight.py`, the synthetic fixtures, and `scripts/audit_xai_pre.py`. Do not replace or bypass these contracts by default; propose explicit versioned changes only with corresponding tests and updated source receipts.

Freeze a **partial rule evaluator** contract: `SATISFIED`, `VIOLATED`, `NOT_APPLICABLE`, `BLOCKED`, `AMBIGUOUS`, `UNIMPLEMENTED`. Freeze an immutable original-input snapshot; dependency graph over error findings; parent/governor/affected token IDs; original→candidate proof lineage; and a bounded search for coherent multi-edit packages. Do not treat an original incomplete parse as proof that unchanged words are grammatical.

**Gate:** source and exception inventory, crosswalk status, schema drafts and held-out multi-error cases are reviewed. Neither an LLM nor a rule registry's chapter title certifies a grammatical constraint.

### Phase 0 — Baseline

Audit the current evidence pipeline and 50+ representative development sentences, determine which node/word explanations are actually generated, log model status and false-positive failure modes, record API behavior, and set regression fixtures. Do not guess the baseline.

**XAI-0 English-only:** [116-case development fixture](../../evaluation/xai0_development_cases.json), [real-model audit](../../scripts/audit_xai0_baseline.py), [measured acceptance report](../reports/xai-0-baseline-acceptance-2026-11-10.md) and CI's `xai0-real-parser-baseline` artifact. The source-cited coverage is **112 / 1,685 canonical nodes (6.65%), solely S nodes**, and **0 / 444 word-terminal nodes**; 92/116 cases normalized. The earlier out-of-scope dataset/results are retired. Do not confuse template hits with role accuracy or grammar detection. **All subsequent XAI-1–XAI-8 rules, tests, sentences and learner explanations must remain English-only.**

### Phase 1 — Concept and rule evidence

Create normalized source-linked records for reviewed B–R constructions and Cambridge concepts. Keep separate scope, exception conditions, printed pages, chapter profiles, ontology crosswalks, review status and runtime eligibility.

Explicitly separate `descriptive_generalization`, `classification`, `constraint`, `variety_restricted`, `stylistic_or_prescriptive`. Only independently approved and executable constraints may diagnose grammar errors. A source-extracted concept does not become an executable rule automatically.

**XAI-1 delivered:** [source-checked catalog](../../grammar/xai_concepts/catalog.json), [schema](../../grammar/xai_concepts/catalog.schema.json), [validator](../../server/xai_concepts.py), [tests](../../server/test_xai_concepts.py), and [acceptance](../reports/xai-1-source-concepts-acceptance-2026-11-10.md). These 42 concepts and 21 template candidates are **not enabled** in `explanations.py` or `cambridge_evaluator.py`; XAI-2/3 need licensed sentence facts, and source-review sign-off must precede live teaching. Respect explicit CGEL vs B–R differences for sentence/clause, coordination and complements.

### Phase 2 — Typed fact graph

Construct typed facts for the selected tree and sentence:

- words/spans/token IDs, category/feature, parent, children, sibling and head;
- function licensed by structural position and approved rule (not merely category);
- selection/valency conditions, complement vs adjunct, auxiliary chains;
- shared antecedent/controlled subject, co-indexed gaps, triangles, empty DET and meaningful alternatives;
- explicitly incomplete role facts for provisional trees.

Every atom must carry a proof/evidence source, confidence or uncertainty state, applicable source/profile scope and exact IDs. Reject invented spans, labels and unrelated book pages.

### Phase 3 — Contextual, deterministic explanation

Create approved word, category, constituent, relation and feature templates. Compose a short and expanded explanation that includes *the actual node's words* and its **role in the particular sentence**. Avoid generic dictionary definitions when the sentence supports richer facts. Support every major B–R category with a meaningful fallback to *observational structure* when review is incomplete; do not invent structural functions.

### Phase 4 — Cambridge error checking

Build approved, typed grammatical checks with explicit preconditions, evidence and exception tests. Scope checks to what their input evidence can independently support. A lexical rule can run on trustworthy tokens even when a full B–R tree is unavailable; a tree-dependent rule must not run without an appropriately supported tree.

**Multi-error requirement:** do not return one global boolean or presume that rules not evaluated are satisfied. Run all safely applicable checks, record blocked/ambiguous/independent findings, construct error-interaction edges (`SHARES_CONSTRUCTION`, `CHECK_BLOCKED_BY`, `REPAIR_ENABLES`, etc.). Deduplicate the same failed relationship reported at two tokens. Re-evaluate after every proposed edit. Preserve exceptional/variety-conditioned cases from the sources.

Do not use spaCy/Benepar, CoLA, an LLM, generic unreviewed Cambridge extraction or the legacy rule matrix as a final correctness judge.

**Technical status (2026-11-10):** XAI-5 bounded recheck, original-token-to-tree localization, interaction groups and a user-authored revision comparator are implemented with runtime source gates. Production approved Cambridge error checks remain zero; unreviewed morphology signals are not reported as verified errors or automatic repairs. See [XAI-5 acceptance](../reports/xai-5-repair-lineage-acceptance-2026-11-10.md).

### Phase 5 — Diagnostics and repairs

Model errors as failed *relations* with offending element(s), governor(s), rule violation, possible exception and candidate correction. Show a related explanation when the user selects either side of the relationship. Reparse edits, rerun relevant approved checks, and avoid claiming that a correction fixes untested aspects.

**Mandatory: multiple simultaneous errors.** Preserve the original string and all original finding IDs. Group interacting issues for jointly evaluated alternatives, and permit truly independent repairs to be explained separately. After **each** candidate, reparse and re-run **all** safely applicable checks. For each original finding distinguish `resolved_by_satisfaction`, `no_longer_applicable_after_rewrite`, `persists`, `blocked`; for additional findings distinguish demonstrably `introduced` versus merely `unmasked` by better analysis. Record affected-token alignment and changing interpretations. Display a successful local fix as **local**, not "whole sentence correct." Limit depth and number of candidates; no infinite correction loop.

A change of tense/aspect or removal of a time adjunct may change meaning: offer alternatives and ask about intended meaning rather than silently selecting one. Refer to Cambridge Ch. 3 pp. 143–145 before treating a past-time adverbial with present perfect as categorically wrong.

### Phase 6 — Optional AI paraphrasing

**2026-11-10 technical decision:** The strict structural-observation naturalizer selection contract, server-side model/cost gates, cache, proof verification, fallback and audit are implemented. Production release is **NO-GO** because the master plan's independent human blind fidelity/clarity review is not available. See [XAI-6 acceptance](../reports/xai-6-naturalization-acceptance-2026-11-10.md). No live model transport is configured, and the unchanged XAI-3 composer remains authoritative for displayed structural observations.

Implement only after reliable template-based XAI has been validated. Supply only approved fact atoms, source paraphrases and permitted format to the AI. Request structured output listing exactly which fact IDs support each sentence. Check factual adherence and fallback deterministically on failure. A rules-based template must always remain available and the AI must not invent new grammar claims or verdicts.

### Phase 7 — Frontend parity

Use the same XAI response shape for the Generator, Builder, Lessons, Quizzes and correction view. In the SVG highlight selected child, parent/governor, relevant sibling and error span; never reorder or rewrite the approved B–R tree to fit the explanation.

Provide brief/deep explanation, source references, keyboard access, a mobile layout, optional concept definition and explicit ambiguity/unresolved status. Avoid raw Penn labels in book-authoritative explanations.

### Phase 8 — Evaluation and rollout

Test on unseen, independently adjudicated grammatical, ungrammatical, ambiguous, dialectal and stylistic examples. Measure function accuracy, traceable coverage, false-positive rates, correction quality, grounding, learner comprehension, latency and cost. Report actual metrics with population sizes and accepted alternatives. Roll back on verified regressions.

## Required test cases

Implement positive, negative, exception and alternative analyses at every phase. Include at minimum:

1. `I hate you.`: explain S, subject NP, predicate VP, lexical V `hate`, object NP and both pronoun terminals, each with non-identical contextual wording.
2. `She had eaten.`: do not accuse `had` of being incorrect.
3. `She had went home.`: if an independently approved Cambridge rule is enabled, identify the failed auxiliary-complement **verb form** relationship and show which token is affected. Otherwise return "not evaluated/no book basis," not a hallucinated verdict.
4. `She had breakfast.`: `had` is a lexical verb in this context; don't apply the perfect auxiliary requirement.
5. `I saw the man with the telescope.`: preserve alternative attachments with conditional explanations.
5a. `She have went to the store yesterday.`: independently anchored issues, interacting auxiliary/inflection relations, staged edits that still show the remaining issue, and a jointly validated alternative without silently changing temporal meaning. Distinguish disappearing rule applicability from proven satisfaction.
5b. `We've already discussed it yesterday.`: do not assert an unconditional "past time + present perfect" prohibition; Cambridge Ch. 3 pp. 144–145 permits a restricted experiential interpretation.
5c. `The boys is carrying a boxes.`: independent errors can be repaired separately without falsely clearing other issues.
5d. `She had wanted the car.` and `She had breakfast.`: prevent false positives due to syncretism and lexical vs auxiliary `have`.
5e. Failure to produce a complete canonical tree: permit independently supported local checks while marking structure-dependent rules `BLOCKED`.
5f. Original→candidate lineage: detect a newly **unmasked** violation without falsely alleging the user's selected edit introduced it.
6. Chapter 2 versus Chapter 7 phrase-marker descriptions: respect convention profile; don't introduce future labels early.
7. Partial/unknown B–R working tree: meaningful observations only; no made-up internal constituents.
8. Corrected vs original sentence: correct span alignment and distinct explanation evidence for each reparse.
9. No LLM network: same approved evidence via deterministic templates.
10. Invalid/uncertain source, unsupported dialect or stylistic preference: no fabricated error, role or citation.

Include tests of prompt injection through sentence text or source content, schema validation, output escaping, client-forged evidence, identical JSON evidence across Generator/Builder, mobile/browser access, and cache invalidation across changing sentence/rule versions.

## Implementation discipline

- **Source authority:** B–R structures stay B–R; Cambridge terminology must be mapped explicitly, never used to silently alter the tree.
- **No hidden invention:** Never assign `subject`, `object`, `wrong`, `corrected`, `verified` or a source page without auditable conditions and evidence.
- **No broad unreviewed rule activation:** A prototype rule may run in diagnostics but must not produce a book-backed error claim until approved.
- **Keep API compatibility:** Preserve `/api/explain` clients and the canonical tree schema; add versioned separate evidence structures.
- **Human review state:** Record who/what reviewed which source, on what date and with what method; AI double-check is not human approval.
- **Book rights:** Use original concise paraphrases; no wholesale reproduction of proprietary book pages.
- **Performance:** Avoid loading full Cambridge/B–R books into an LLM at runtime. Keep index lookup, render path and corrections bounded and cacheable.
- **Unresolved is useful:** Provide structural observations when safe, mark unsupported grammatical conditions as not evaluated, and offer source-linked teaching material only when actually available.
- **Prose safety:** Check quoted words, modalities, rule conditions and supported atoms. Unsupported model output must fall back to reviewed templates.

## Milestone report format

For each implemented phase return a concise report with:

```
Phase:
Branch and commit/PR:
Changed files:
New approved B–R concepts/templates:
New approved Cambridge concepts/templates:
New runtime-enabled Cambridge constraints:
Multi-error/blocked/ambiguous test coverage (measured):
Interacting repair packages and finding-lineage outcomes:
Constituent/word/edge/error coverage (measured):
Tests executed and outcomes:
Source-review / exception-test status:
Still missing / human decisions required:
Next independent gate:
```

Do not claim "seamless for all English" based on synthetic examples, or call XAI complete when the verified coverage remains low. The primary objective is **consistent useful sentence-grounded explanation, with a trustworthy boundary between observed structure and externally supported grammatical judgment**.
