# SynTutor — XAI Master Plan: Sentence-Grounded Explanations for Every Tree Level

**Status:** XAI-PRE contracts, English-only **XAI-0 baseline**, and **XAI-1 source-linked concept registry implemented**. **XAI-2 structural fact graph is implemented with tests**, pending CI verification and human review for functional-role licensing. XAI-3 deterministic contextual composer is technically implemented (pending CI and linguistic sign-off); XAI-4–XAI-8 remain unimplemented. See [XAI-PRE](../reports/xai-pre-acceptance-2026-11-10.md), [XAI-0](../reports/xai-0-baseline-acceptance-2026-11-10.md), and [XAI-1 source acceptance](../reports/xai-1-source-concepts-acceptance-2026-11-10.md).  
**Date:** 10 November 2026  
**Repository:** `ybcole/SynTutor`  
**Companion implementer prompt:** [MASTER_PROMPT_XAI.md](MASTER_PROMPT_XAI.md)  
**Mandatory pre-milestone evidence and correction specification:** [XAI_SOURCE_AUDIT_MULTI_ERROR.md](XAI_SOURCE_AUDIT_MULTI_ERROR.md)  
**Related:** [Existing master plan](master_plan.md), [B–R construction specification](../BR_NATIVE_ENGINE_CONSTRUCTION.md), [source conventions](../../CONVENTIONS.md)

> **Product decision: Explain words, lexical heads, all meaningful constituents (NP, VP, PP, AP, AdvP, NOM, S/S′/S″), structural edges/functions, detected violations, and repairs.** Every explanation must reference the actual sentence and, when relevant, the surrounding constituent structure. Never reduce this to an isolated POS-tag dictionary. Do not confuse interpreting a tree with judging whether the sentence is grammatical.

## Non-negotiable scope: English only

**SynTutor analyzes and explains English syntax and English grammar only.** All XAI milestones, examples, regression corpora, book-derived concept registries, tests, corrections and learner-facing generated prose must remain in English. **Do not add code-mixed or non-English sentence inputs** as development probes, supported-language claims, training examples, rule constraints or advertised product scope without a separate, explicit change requested by the project owner. English dialect/register differences are considered as English-language phenomena; this does not authorize other languages. The XAI-0 development corpus is versioned with `language_policy: ENGLISH_ONLY` and each row declares `language: en`; this metadata is an audit safeguard, not an automatic language detector.

## 0. Baseline reality: what exists versus what remains

Repository code inspected on 10 November 2026:

| Component | Current behavior | Gap for the proposed XAI |
| --- | --- | --- |
| `server/parse_engine.py` | spaCy + Benepar candidate analysis | Candidate evidence is not a grammaticality proof or B–R source |
| `server/burton_roberts.py`, `server/final_d1_projection.py` | Canonical/working B–R hierarchy with chapter profiles and uncertainty | Unresolved analyses, alternative attachments, and confidence must constrain explanations |
| `server/br_native_grammar.py`, `grammar/br_native_constructions.json` | 100 draft structural signatures + 10 obligations, unreviewed conditions | Shape signatures alone cannot justify natural-language semantic or error claims |
| `server/explanations.py` | Validates canonical envelope; three channels (structural, grammatical, remediation); source/review gates; simple templating | Small set of highly generic templates; no full per-node relational fact graph, evidence-level error attribution, or comprehensive contextual prose |
| `grammar/explanation_templates.json` | **2 templates**, **4 source records**, with documented independent AI source passes but no human-instructor sign-off | Need chapter-by-chapter concept and construction coverage; current scope is much narrower than the books |
| `grammar/runtime_registry.json` | **0 enabled Cambridge runtime constraints** | Must implement and independently validate actual grammatical/lexical checks before producing "wrong because…" verdicts |
| `server/cambridge_evaluator.py` | Fail-closed, narrow sentence-scope forbidden-sequence runtime primitive | Add linguistically grounded typed feature/role/selection checks with exception and variety handling; never infer universality from token patterns |
| `web/js/canonical-view.js` | Deterministic node facts: label, surface, daughters, a few features | Needs head, function, sibling, parent, licensed construction, evidence, dependencies, and explicit unknowns |
| `web/js/explanation-evidence.js` | Shared evidence rendering for Generator/Builder | Progressive depth, node-specific contextual language, correction explanation links, status labels and accessibility |
| `server/tree_evaluation.py` | Shares evidence and comparison contracts | Expand to shared node/edge/diagnostic explanation records while preserving separate well-formedness and grammaticality |
| Legacy `matrix.py`, `ruleset.py`, `detector.py`, `corrector.py` | Candidate/legacy heuristics and corrections | Their output is **not automatically book-backed**, and must not be laundered into cited teaching claims |

The old `master_checklist.md` marks its **basic explanation-engine foundation** complete. That does **not** mean this deeper, relational, sentence-adaptive XAI system has already been delivered. This is a **new workstream**, with new gates below.

## 0A. Mandatory pre-milestone source review and multi-error contract

**XAI-PRE is a hard prerequisite to implementation of XAI-0 through XAI-8.** Read and apply the [uploaded-book source audit and multi-error protocol](XAI_SOURCE_AUDIT_MULTI_ERROR.md). The uploaded B–R third edition (2011) and Cambridge Grammar (2002) have been checked in **selected relevant passages**; this is **not** an exhaustive page-by-page audit. The source audit inventories all 11 B–R and 20 Cambridge chapters and tracks independently reviewed vs pending constructions.

Specific book findings that affect implementation:

- B–R Ch. 6 pp. 116–118, 121–122 and Cambridge Ch. 3 p. 106 both encode auxiliary → selected verb-form relationships, but **B–R “perfect participle” versus Cambridge “past participle”** and **B–R “progressive participle” versus Cambridge “gerund-participle”** need explicit crosswalk records. Cambridge p. 76 treats overtly identical preterite/participle forms as syntactically distinct.
- Cambridge Ch. 3 pp. 143–145 describes the usual restriction of past-time adjuncts with present perfect **and exceptions** (e.g. an experiential perfect containing “already … yesterday”). Never enable a simple `present perfect + yesterday → error` predicate.
- Cambridge Ch. 1 pp. 2, 5–10 and its notational conventions separate Standard English, informal/nonstandard varieties, semantics/pragmatics, uncertain grammaticality, and actual ungrammaticality. Keep corresponding diagnostic types distinct.
- B–R third-edition preface pp. ix–x discontinues older `Vgrp` analyses; nested auxiliary VPs must be preserved.

**Architectural change:** a sentence can contain several interacting issues. Each detected issue requires an original-input evidence scope, governing relationship, rule precondition, independent validity state and exact token anchors. Maintain a dependency graph of independent/overlapping/blocked/cascaded diagnoses; propose **joint repair packages** for interacting constraints. Every candidate edit produces a new candidate analysis and **full re-evaluation**. Distinguish an issue `resolved_by_satisfaction` from one `no_longer_applicable_after_rewrite`, and a newly **unmasked** issue from a genuinely **introduced** issue. Never label a whole sentence grammatical based on fixing a single issue.

**Pre-milestone gate:** edition-verified source map, pending crosswalks, documented Cambridge exceptions, multi-error status/lineage API contract, a controlled held-out/adversarial fixture list, and written distinction between confirmed local findings and unresolved global grammaticality. **Implementation evidence:** [source claims and chapter ledger](../../grammar/xai_pre/source_audit.json), [correction schema](../xai/diagnosis-repair-pre.schema.json), [semantic validator](../../server/xai_preflight.py), [11 synthetic fixtures](../../grammar/xai_pre/preflight_fixtures.json), [acceptance report](../reports/xai-pre-acceptance-2026-11-10.md). No XAI-specific source claim is independently human-approved or eligible to issue a runtime grammar verdict.

## 1. Definitive architecture decisions

### D1 — All meaningful tree nodes are explainable; avoid generic filler

A learner may click *any* canonical tree node, including root S, intermediate NP/VP/NOM/PP, lexical heads (V/N/P/A), overt terminal words, feature rows, or gaps/empty positions. Not all require equal depth.

For each node, produce these **separate** sections where supported:

1. **What this part is (structural observation):** the actual node category, exact span, head, daughters and source-approved structure.
2. **What it does *here* (relational function):** subject, predicate, object, complement, modifier, head, clause role, etc. Functions are inferred from licensed parent/sister configurations, not invented as B–R phrase-marker nodes.
3. **Why it is analyzed this way (book-grounded explanation):** matching reviewed B–R construction IDs, conditions, alternatives, and printed-page evidence.
4. **Grammatical principle (Cambridge where eligible):** a source-approved concept or executable rule applied to the actual words/features and their syntactic context, **not** just a definition.
5. **Issue and repair (only if independently detected):** violated rule, evidence, triggering context, localization, exceptions, alternative interpretations, correction, and why the repair satisfies that rule.
6. **Depth controls:** default brief explanation; optional expanded explanation, "show the evidence", and worked comparison.

A terminal's contextual role can depend on several ancestors; give it meaningful parent/edge context without asserting that word-level POS alone establishes its function. A constituent explanation must summarize its **actual** immediate daughters and relationship to its parent, not "NP is a noun phrase" repeated everywhere.

### D2 — Two books, two distinct authorities

- **Noel Burton-Roberts, *Analysing Sentences*, Third Edition (2011):** phrase markers, categories, node hierarchy, features, subcategorization patterns, functions derived from his representation, chapter versions V1–V10, FINAL-D1, triangles, gaps, indices, and controlled subjects.
- **Huddleston & Pullum et al., *The Cambridge Grammar of the English Language* (2002):** descriptive grammatical principles, category/lexical distinctions, contextual constraints, exceptions, usage/variety/register, and independent error checks when review and implementation permit.
- **Explicit B–R↔Cambridge crosswalk required:** `compatible`, `terminology_differs`, `analysis_differs`, `not_covered`, `unresolved`; never silently substitute one framework's nodes or labels for the other.
- Rule *source reference* means real printed-page grounding; `draft`, `extracted`, `AI-reviewed`, `human-approved`, and `runtime-enabled` are different states. Do not equate an AI second pass to human instructor approval.

### D3 — Derive facts first, compose language second

**The LLM cannot be the detector or grammatical authority.** The supported production chain is:

```text
INPUT / ORIGINAL SENTENCE (token IDs, spans, variety/profile)
             |
      Candidate parser evidence
             |
     Validated B–R canonical tree OR provisional working tree
             |
     Relationship resolver: parent / siblings / head / valency /
     complement vs adjunct / grammatical function / features /
     antecedent / gap links / attachment alternatives
             |
  Source-linked construction matcher + approved Cambridge evaluator
             |
  EXPLANATION FACT GRAPH (atom IDs, proof, uncertainty, provenance)
             |
    Explanation planner (target node + learner level + intent)
             |
   Approved sentence-specific templates (reliable baseline)
            optional ↓
    AI paraphrase of allowed facts ONLY, schema-constrained
             |
  Output verifier: atom coverage, citations, spans, category/role
  consistency, disallowed claim and contradiction checks
             |
   Rendered explainable node / edge / diagnostic / corrected view
```

Never send a whole textbook or the full 2,000-page PDF to the runtime LLM per sentence. Build reviewed concept/rule records **offline**, indexed by exact construction/lexical condition. At runtime fetch only *applicable, approved* evidence. Retrieval alone is never proof that the rule is triggered.

### D4 — Correctness is not node identity and cannot be inferred from one token

An unacceptable sentence may still receive a useful constituency parse. Conversely, a source-valid B–R tree is not evidence that every agreement/tense/selection condition is satisfied. Keep independent outcomes:

- `tree_structure`: recognized / provisional / invalid / ambiguous / unresolved;
- `grammatical_evaluation`: verified_violation / no_approved_violation_found / insufficient_evidence / not_evaluated;
- `correction`: proposed / validated_against_applicable_rules / ambiguous / not_available;
- `explanation`: source_backed / structural_observation_only / provisional / no_book_basis / source_conflict.

**"No detected errors" is not "perfectly grammatical".** Never claim "wrong" because a heuristic disliked a sentence. A rule must prove a specific condition and exceptions.

### D5 — Interpret errors as *failed relationships*, then highlight the relevant words

Use at least three anchors: (1) culprit token/span or missing slot, (2) governing node/head, (3) violated relation. For example, in **"She had went home"** the candidate error is the verb form *went* after perfect auxiliary *had*, **not** necessarily *had* itself. The relevant grammatical relationship is perfect auxiliary → required participial form. The corrected candidate **"She had gone home"** must be checked by a rule with exceptions and context, then reparsed; a correction is not proven merely because it looks natural.

The exact claim is **illustrative, not a currently enabled Cambridge rule**. It cannot be presented as book-verified remediation until its Cambridge record is independently checked and runtime tests pass.

If a user clicks `had`, the explanation should state *had*'s role in the diagnosed construction and point to the problematic complement form; if they click `went`, explain its form relative to *had*. Wrongness is contextual and may span multiple tokens, not a property of the isolated word.

### D6 — No external LLM required for baseline usability

A good XAI engine must work offline with approved deterministic templates, even if the LLM service is down, expensive or unavailable. Runtime AI paraphrasing is an optional *quality layer*, not a dependency of source validation, grammar detection, tutoring, or correction.

## 2. Four supported explanation target types

| Target | Example | Required sentence-grounded facts |
| --- | --- | --- |
| **Word/lexical head** | `V` "hate" in "I hate you" | Surface, lemma/inflection when evidenced, B–R V features, parent VP, selected/complement NP "you", clause subject "I", governing construction, source status |
| **Constituent/phrase** | `VP` "hate you" | Head "hate", immediate daughters `V NP`, function as predicate of "I" for this unmarked S, object/complement status of "you", hierarchy justification |
| **Relationship/edge** | `S → NP VP` | `NP` "I" subject vs `VP` "hate you" predicate; distinction between daughter category and syntactic function |
| **Diagnostic/correction** | "She had went home" | Rule ID, `had` as context, *went* as affected form, eligible source evidence, alternative `gone`, exception/variety checks, reparse and alignment |

Other targets: clause/S′/S″, NOM recursion, AP/AdvP/PP attachments, coordination, gap/co-indexation, empty determiner, and feature lines. Punctuation can receive a structural/orthographic note only where a reviewed rule supports it.

**Example pedagogical narrative — "I hate you"** (illustrative; not claimed as already source-approved templates):

- Click S: "In **I hate you**, the subject NP **I** combines with the predicate VP **hate you**."
- Click NP "I": "This NP functions as the clause's subject. It is headed by a pronoun and is directly dominated by S."
- Click VP "hate you": "This is the predicate VP. The verb **hate** takes the NP **you** as its complement in this construction."
- Click V "hate": "The lexical head is **hate**, analyzed with the source-authorized transitive feature; **you** fills its NP complement slot."
- Click NP "you": "This NP is the verb's object in the VP. Its syntactic function comes from its place as complement to **hate**, not merely from the word being a pronoun."
- Click a word "you": "The pronoun **you** realizes the object NP in this sentence; its grammatical function is determined by that NP's relationship to the verb."

Never label all pronouns as subjects or all NPs as objects. Avoid repeating definitions when the user changes nodes: make every explanation refer to the selected node's distinct relationship.

## 3. Typed evidence / proof model (recommended new schema)

Do not replace the approved canonical tree schema. Attach explanation evidence in a **separate** versioned object with stable references to that tree.

```json
{
  "schema_version": "xai-2.0-draft",
  "sentence": "I hate you.",
  "analysis_id": "computed-from-input-and-parser-version",
  "profile": "FINAL-D1",
  "analysis_status": "normalized",
  "target": {
    "kind": "constituent",
    "node_id": "node-vp-id",
    "surface": "hate you",
    "token_span": [1, 3]
  },
  "atoms": [
    {
      "fact_id": "f1",
      "predicate": "head_of",
      "subject_node_id": "node-v-id",
      "object_node_id": "node-vp-id",
      "value": "hate",
      "evidence_kind": "validated_tree_observation",
      "source_rule_ids": [],
      "uncertainty": "none",
      "provenance": ["canonical_tree"]
    },
    {
      "fact_id": "f2",
      "predicate": "object_complement_of",
      "subject_node_id": "node-object-np-id",
      "object_node_id": "node-v-id",
      "value": "you",
      "evidence_kind": "book_rule_application",
      "source_rule_ids": ["BR04-VP-TRANSITIVE"],
      "uncertainty": "source_rule_not_independently_verified",
      "provenance": ["br_construction_registry"]
    }
  ],
  "applicable_rules": [],
  "diagnostics": [],
  "alternatives": [],
  "explanation": {
    "status": "provisional",
    "short": "The VP 'hate you' contains the verb 'hate' and the NP 'you'.",
    "expanded": null,
    "supported_fact_ids": ["f1"],
    "source_refs": [],
    "rendering": "approved_template"
  }
}
```

*Illustrative schema only.* The example's second atom is deliberately marked **unreviewed**; it must **not** be treated as accepted book-backed evidence. For actual code, supply strict JSON Schema (`additionalProperties:false`), sentence/node/span/feature/sentence-text validators, and provenance checks that prevent a model or client from declaring its own review status.

### Evidence atom categories and gates

1. `validated_tree_observation`: directly observed node label, span, children and explicitly recorded features; safe to render as **observed structure**, not source-certified grammar.
2. `source_backed_structure`: B–R rule applied with reviewed source and matched construction-specific conditions.
3. `source_backed_grammatical_constraint`: Cambridge rule applied by a tested detector with all exceptions and variety checks.
4. `source_backed_diagnostic`: violated constraint with concrete affected spans, repair rationale and checking record.
5. `hypothesis`: candidate interpretation/attachment that is not approved; disclosed as provisional and never the only explanation where source evidence is absent.

Each atom has stable IDs, exact token spans, relevant nodes/relations, original evidence references, rule ID + version, source printed pages, reason trace, applicable variety, antecedents/alternatives, and explicit `unknown` values where evidence is missing. Do not invent a head, role, or source simply because a user clicked a node.

## 4. Book-to-rule extraction workflow (offline)

### B–R construction explanations

Walk the current B–R construction catalog and 252 reference trees, chapter by chapter, **without presuming the catalog is fully approved**. Each source-authorized construction gets:

`concept_id`, `construction_rule_id`, `profiles`, `tree_signature`, `matching_conditions`, `head_selection`, `functions`, `allowed_features`, `possible_alternatives`, `exceptions`, `source_pages`, `source_example_id`, `review_status`, `approved_template_ids`.

Where chapter notation differs, retain separate versions. For example, don't explain a Chapter 2 tree using Chapter 7 NOM conventions. Distinguish instruction-level triangular analyses from mature FINAL-D1 phrase markers.

### Cambridge concept and rule records

Use the existing extracted `grammar/rules/*.json` as **candidate material**. Revisit relevant supplied Cambridge chapter material in reviewable batches, with printed page IDs, linguistic tests, exceptions and variants. Each output is one of:

- `classification` / `descriptive_generalization`: can teach; **cannot alone detect errors**.
- `constraint`: can diagnose only after independent review + executable rule + minimal-pair/exception coverage.
- `variety_restricted`: requires an explicit eligible variety/register and conditional wording.
- `stylistic_or_prescriptive`: distinguish preference/style from ungrammaticality.

Map the rule to B–R tree nodes **without assuming Cambridge uses the same syntax categories**. One record must list `terminology_differs`/`analysis_differs` explicitly when applicable, with adapted explanation wording.

### AI conversion step — offline authoring

AI may help draft original pedagogical paraphrases from **small, verified source notes and rule facts**. For each concept it produces:

- short explanation for word/head, constituent, relation;
- deep explanation including head, siblings, original sentence and contrastive minimal pairs;
- positive, negative, exception and ambiguous examples;
- common confusions / likely misapplications;
- potentially helpful question-answer hints.

But reviewers approve *source claims and test cases* before enabling templates. Do not upload full proprietary book passages to unrelated AI services without permission, and do not publish long quotations or reconstituted textbook content. Use original paraphrases and concise bibliographic references.

### Review gates

`EXTRACTED → SOURCE_CHECKED → TESTED → APPROVED_FOR_TEACHING → ENABLED_FOR_RUNTIME`. Human-instructor review is a stronger optional gate with its own flag and identity; never misreport an AI source check as human approval. Any rejected/conflicting evidence remains visible in reports but disabled in learner-facing claims.

## 5. Context engine — determining what the selected node does

Build a **sentence fact graph** before producing any prose. On validated tree data, derive only licensed facts, including:

- token and character span → smallest lexical, phrase and clause ancestors;
- parent ↔ child edge with positions, head and siblings;
- constituent span text and exact token order (including contractions and punctuation policy);
- subject NP vs predicate VP when S-structure supports it;
- selected NP/PP/S′ complements vs adjunct PP/AdvP/clauses, contingent on reviewed verb valency and construction rule;
- head-category and modification scope for NOM/AP/PP/AdvP;
- auxiliary chain (MOD/PERF/PROG/PASS/TENSE), tense/form labels and complement VP dependencies;
- clause embedding, wh displacement, indexed gap ↔ antecedent, relative clause function;
- source-specific triangles, deliberate underanalysis, ellipsis and empty determiners;
- ambiguity forest: represent different legitimate attachments with separate facts and conditional explanations.

Do not silently invent object, head or modifier relationships from a flat set of labels. If the rule is not licensed, state only the observed daughters and mark the function as unknown. For provisional/working B–R trees, expose observable spans; do not fabricate an internally resolved analysis.

## 6. Grammar checks and the error-to-explanation path

Begin with high-value phenomena selected by **reviewed Cambridge coverage**, not guessed from popularity:

- finite subject–verb agreement (including inverted clauses, existential constructions, coordinated subjects, collective nouns, atypical dialects);
- auxiliary + verb-form licensing (perfect, progressive, modal, passive, negation, do-support);
- transitive/intransitive/ditransitive and prepositional complement selection;
- pronoun case and determiner/number constraints where descriptive evidence supports them;
- clause finiteness, complementiser/wh dependencies, relative clauses;
- adjective/adverb positioning, agreement exceptions, comparative constructions, and multiword phrase attachment.

Each *runtime-enabled* rule must have a specification of:
`preconditions`, `positive_evidence`, `violation_condition`, `exceptions`, `variety`, `affected_nodes`, `affected_span`, `governing_nodes`, `alternatives`, `repair_transform`, `verification_test`, `sources`.

A rule must be able to return: `matched_valid`, `violation`, `not_applicable`, `ambiguous`, `insufficient_evidence`. A rule not implemented is **not equivalent** to a passed rule.

**Important architecture change:** the source-valid canonicalizer may decline to produce a full tree for an ungrammatical input. Let independently validated **lexical/morphological checks** run on token/dependency evidence when their own preconditions suffice, instead of requiring a fully normalized canonical tree for every error check. Structural checks that need verified B–R hierarchy must still refuse evaluation if that hierarchy is unresolved. Never infer B–R correctness from a token-only check.

### Diagnosing a word "had" in context

| Sentence | Required reasoning | What SynTutor must avoid |
| --- | --- | --- |
| *She had eaten.* | Perfect auxiliary construction; check form of its complement | Saying "had is wrong" because it appears in past tense |
| *She had went home.* | Proposed violation is *went* as complement form after *had*, subject to a reviewed Cambridge rule and correct interpretation | Blaming *had* instead of locating the failed relation |
| *She had breakfast.* | Here *had* is a lexical verb with an object in an ordinary transitive construction | Treating all occurrences of *had* as perfect auxiliaries |

These are product examples for future rule validation, **not currently executable, source-certified Cambridge diagnoses**.

### Correction verification

Record exact original → candidate edit operations, token alignment, affected tree nodes, deterministic rule rerun, and separately parsed corrected tree. A correction may be a **suggestion** without claiming the whole corrected sentence is verified grammatical. If multiple acceptable alternatives exist, describe each and do not make arbitrary changes to meaning, tense, dialect, or emphasis. Do not assert that a change "fixes everything" when other untested conditions remain.

## 7. Explanation planner + natural-language composer

### Template-first baseline (recommended to implement first)

Use context slots much richer than today's `{label}` and `{surface}`:

`sentence`, `target_surface`, `target_category`, `parent_surface`, `parent_label`, `head_surface`, `governor_surface`, `sibling_surface`, `function`, `daughter_surfaces`, `construction_id`, `feature_readings`, `rule_condition`, `error_span`, `correction_span`, `reason`, `evidence_status`.

Do **not** permit arbitrary placeholders not validated by the sentence fact graph. Use typed claim templates whose grammatical content is approved separately from variable span values. Example family:

- **Category:** "The word `{word}` realizes `{category}` in this sentence."
- **Constituent:** "The `{label}` spanning `{phrase}` contains `{child1}` and `{child2}`."
- **Function:** "Here, `{phrase}` functions as `{function}` of `{governor}` because `{approved_condition}`."
- **Remediation:** "In `{context}`, `{rule}` requires `{required_form}`; `{observed_form}` does not satisfy it. One supported repair is `{repair}`."

### Optional LLM naturalizer (after baseline works)

Send the AI **only** the approved fact atoms, allowed source paraphrases, selected target, user reading level, and permitted explanation goals. The LLM may reorder, shorten, and clarify but **cannot** introduce new grammar facts, verdicts, alternatives, source pages, or corrections.

Use schema-constrained structured output:
`paragraphs[]: {text, supported_fact_ids[], source_ids[], level}`.
Reject unsupported fact IDs, unapproved source references, wrong target, invented quoted sentence spans, changes of certainty/modality ("may"→"must"), contradictions, harmful or irrelevant content, and sentence-text mismatches. Automated checks cannot guarantee perfect semantic entailment; use conservative approved templates whenever a robust proof is unavailable. Log accepted/rejected versions. Avoid retries that could become costly/unbounded. Cache by canonical tree hash, selected node, enabled rule-set version, source/template version, variety and reading level.

A naturalizer can improve style; **it must never silently override the fact graph**.

## 8. UX interaction: explain on click, not a wall of text

When the learner selects a node, use the same contextual explanation surface for Generator, Builder, Lessons and Quizzes:

1. **One-line contextual answer** as the default, e.g. "The NP *you* is the object of *hate* within the VP *hate you*."
2. **Why?** Show immediate parent/sisters, a highlighted edge in the existing B–R tree, and eligible source-linked rule.
3. **Grammar insight** (if an approved Cambridge rule is applicable), clearly separated from B–R structure.
4. **Issue/repair** if a verified violation involves this node, including governing word and highlighted affected span.
5. **Read more / examples**: contrastive examples, exceptions, and chapter link, not generic repeated dictionary definitions.
6. **Uncertainty:** provisional/ambiguous/no-book-basis labels, not a green "verified" badge just because an LLM wrote confidently.

Feature rows such as `[trans]` and `[pres]` should be independently selectable or exposed within the V node panel. Tree highlights should show the selected node and its governing/related constituents without changing the approved SVG phrase marker. Link cited printed pages and related lessons; do not expose entire copyrighted passages.

## 9. Proposed software contracts and files

**Do not edit the canonical grammar tree schema to inject unreviewed prose.** Proposed additive components:

| File / subsystem | Responsibility |
| --- | --- |
| `docs/planning/XAI_MASTER_PLAN.md` | This overarching plan, fixed architecture decisions, acceptance criteria |
| `docs/planning/MASTER_PROMPT_XAI.md` | Controlled implementer prompt for successive implementation phases |
| `docs/xai/evidence-v2.schema.json` (future) | Typed node, relation, rule application, diagnostic and prose evidence |
| `server/xai_facts.py` (future) | Canonical tree to sentence-specific atomic observations and approved relations |
| `server/xai_relationships.py` (future) | B–R construction conditions, subject/predicate, complement/adjunct, head and gap/antecedent |
| `server/xai_constraints.py` (future) | New typed Cambridge checks; separate admissibility gates from detection |
| `server/xai_diagnostics.py` (future) | Grounded problem anchors, counterevidence, localization and repairs |
| `server/xai_planner.py` (future) | Select minimal relevant facts per clicked node and learning level |
| `server/xai_composer.py` (future) | Template-first sentence-specific prose; no unsourced claims |
| `server/xai_naturalizer.py` (optional) | Safely constrained LLM paraphrasing with deterministic fallback |
| `grammar/xai_concepts/` (future) | Source-reviewed B–R and Cambridge concept rules, original paraphrases |
| `grammar/xai_templates/` (future) | Approved contextual word, constituent, relation, error templates |
| `scripts/audit_xai_coverage.py` (future) | Node-category, construction, error, chapter and source-coverage reports |
| Existing `server/explanations.py` | Compatibility adapter into XAI v2, keeping `/api/explain` clients alive |
| Existing `web/js/explanation-evidence.js` and `canonical-view.js` | Sentence-aware UI and structural observation when book evidence missing |

Suggested API:

- `POST /api/xai/explain` with `{tree_or_analysis_id, node_id, target_type, depth, variety, reading_level}`; server obtains immutable trusted source/rule metadata and the original sentence.
- `POST /api/xai/evaluate` for a controlled diagnostic result with separate structural and grammatical statuses.
- Keep `POST /api/explain` as compatibility contract until all Generator/Builder/Lessons/Quiz callers migrate. Do not allow client-supplied citations, rule statuses or "human approved" claims.

Avoid round-tripping large full trees to AI services. For any remote AI usage obtain appropriate user/organizational consent and avoid including identifiers or private data not necessary for the task. Source-book text rights must be respected.

## 10. Milestones / acceptance gates

**Each stage is independently shippable. Do not mark complete merely because a file exists or a synthetic test passes.**

### XAI-PRE — Book check + multi-error protocol, before any implementation

- Apply the dedicated [uploaded-book source audit and dependency-aware correction specification](XAI_SOURCE_AUDIT_MULTI_ERROR.md); verify both editions and printed-page citations.
- Audit all 20 CGEL and 11 B–R chapter **topics** for relevant construction coverage; source-check the selected actual passages before activating each rule. The topic inventory is **not** equivalent to reading and approving the complete books.
- Define separate tree, rule, variety, usage, and semantic status enums; define evidence provenance and partial evaluation (`SATISFIED`, `VIOLATED`, `NOT_APPLICABLE`, `BLOCKED`, `AMBIGUOUS`, `UNIMPLEMENTED`).
- Freeze original-input spans, issue/dependency graph, scoped repair candidate and original→candidate finding lineage contracts. Require exception-rich multi-error tests and human-approved source gates.

**Gate:** technically validated schema, source evidence inventory and exceptions; independent linguistic/owner approval remains pending before enabling any runtime constraint. No runtime rule or corrector is enabled merely because these artifacts exist.

### XAI-0 — Baseline audit and contract freeze

- Inventory existing templates, all book-source status, Cambridge enabled rules, current node inspection and correction outputs.
- Collect at least 50 representative sentences for initial **development** smoke (English-only: grammatical controls, malformed probes, ambiguity, nonfinite clauses, wh, coordination, auxiliaries, punctuation, and difficult English constructions) and record parser status without inventing "gold".
- Record the currently missing node types, source coverage and false-positive diagnoses.
- Agree source metadata + data contracts and UI labels before changing production outputs.
- Include original-vs-candidate multi-error diagnosis and Cambridge contextual exceptions in baseline fixtures; record blocked/ambiguous findings explicitly.

**Gate:** written inventory, reproducible test set and initial metrics. **English-only XAI-0 baseline measured on 116 real parser cases:** 92 normalized B–R trees, 24 unresolved, 1,685 canonical nodes, 112 S-level source-cited template hits (6.65%), **0 of 444** word-terminal nodes source-cited. The old out-of-scope audit is superseded. Static inventory: 2 templates, 4 source records, 0 enabled Cambridge constraints. See [measured English-only acceptance](../reports/xai-0-baseline-acceptance-2026-11-10.md). These are not correctness scores or independently verified error judgments.

### XAI-1 — Source concept registry / claim provenance

- Generate candidate B–R teaching rule records from the 3rd-edition chapter conventions and corpus; Cambridge candidate records by chapter/grammar domain.
- Independently check each against source pages, interpretations, conditions, examples, and alternatives. Track conflicts/review states.
- Separate instructional descriptive rules from executable constraints.
- Build original pedagogical paraphrases, not textbook quotations.

**Gate:** representative page-checked concepts per priority construction, with positive/contrast/exception examples, exact printed pages and crosswalk status. **XAI-1 technical delivery:** [42 English-only concepts and 21 non-runtime contextual template candidates](../../grammar/xai_concepts/catalog.json), [strict schema](../../grammar/xai_concepts/catalog.schema.json), [audit and approval gates](../reports/xai-1-source-concepts-acceptance-2026-11-10.md). Of eight crosswalks, some explicitly differ or remain unresolved. **Human/instructor linguistic sign-off is still pending; none of these candidates is live.**

### XAI-2 — Node and relationship fact engine

- Implement root/phrase/lexical/word/edge/feature/span/cross-clause fact graph.
- Only license functional roles if a matched reviewed construction and all preconditions apply.
- Preserve chapter profiles and ambiguity, correctly handle unlabelled triangles and gaps.

**Gate:** every canonical/working node produces at least accurate basic structural observation; unsupported roles remain unknown. Held-out node-function gold tests, no invented children or words.

### XAI-3 — Contextual template composer

**Implementation:** `server/xai_planner.py` and `server/xai_composer.py` emit English-only per-node short/deep observations from XAI-2 atoms, exposed in `/api/explain` and `/api/evaluate` and displayed by the shared Generator/Builder evidence panel. This is structural observation only; XAI-1 unapproved head/function rules remain disabled. See [XAI-3 acceptance](../reports/xai-3-contextual-composer-acceptance-2026-11-10.md). CI and independent linguistic review are tracked separately.


- Produce short/deep original phrasing from only permitted facts.
- Explain **S, NP, VP, NOM, PP, AP, AdvP, V, N, P, A, pronoun/name and word terminals**.
- Provide reason-specific differences between selected child vs parent; include actual words and relations.
- Teach conceptual distinction between category, phrase, function and part of speech.

**Gate:** all tested supported nodes receive useful sentence-specific prose, no generic filler-only outputs, no unsourced source claims. Evaluate separately on unseen sentences.

### XAI-4 — Real Cambridge runtime constraints

**XAI-4 technical slice (10 Nov 2026):** Four English-only, source-audited typed candidate checks are implemented with token-span evidence and blocked/ambiguous/unknown outcomes. See [XAI-4 technical acceptance](../reports/xai-4-cambridge-partial-acceptance-2026-11-10.md). **Release gate remains blocked: 0 independently human-approved Cambridge diagnostic constraints are enabled; no new verified error verdicts are issued.** Positive/negative/exception unit fixtures cannot substitute for human-adjudicated false-positive checks.

- Start with a small batch of high-frequency *reviewed* contrastive constraints.
- Treat checks as **partial evaluators**, not universal grammar verdicts; expose `BLOCKED`, `AMBIGUOUS`, and `NOT_APPLICABLE` separately.
- Attach cause/dependency edges across simultaneous violations before enabling learner-facing diagnosis.
- Implement typed detectors with preconditions, exceptions, variety and disagreement policy; enable only after tests.
- Support basic token-only constraints even if full B–R tree is not normalized, without promoting parser evidence to authoritative B–R relationships.

**Gate:** rule-by-rule positive/negative/exception/minimal-pair tests and human-adjudicated false positives; counts of enabled rules published. At launch, no unverified "error" claim may be issued.

### XAI-5 — Error-to-tree localization and correction rationale

**XAI-5 technical implementation (10 Nov 2026):** Deterministic source-safe location mapping, immutable original and bounded staged revisions, fresh full rule reevaluation, token and tree version tracking and an accessible manual revision-comparison UI are implemented. See [acceptance report](../reports/xai-5-repair-lineage-acceptance-2026-11-10.md). **Human-adjudicated diagnostic release remains gated by XAI-4: zero real approved Cambridge error rules, no verified automatic corrections.** Synthetic approved-rule tests demonstrate mechanics but do not constitute real source authorization.

- A failing check identifies exact affected span **and** governor/ancestor relation, plus possible alternatives.
- Support multiple simultaneous errors with stable original finding IDs and independent vs interacting **repair groups**.
- Reparse and re-evaluate every candidate edit; distinguish resolved/satisfied, inapplicable after structural change, persisting, newly unmasked and genuinely introduced findings. Never declare an isolated fix globally correct.
- Attach diagnosis to both clicked word and related constituent/feature row.
- Reparse correction; evaluate applicable rule set; preserve unverified conditions, multiple corrections and meaning.

**Gate:** tested "had", auxiliary, agreement, pronoun and valency families; each proposed repair states exactly which violation it addresses. No "had is wrong" without a specific actual violated relationship.

### XAI-6 — AI naturalization (OPTIONAL)

**XAI-6 technical acceptance (10 Nov 2026):** Optional evidence-constrained model-selection path, input/output schemas, adversarial checks, bounded cache, cost/latency contracts and deterministic XAI-3 fallback implemented. [Acceptance and no-go decision](../reports/xai-6-naturalization-acceptance-2026-11-10.md). **AI naturalizer remains disabled in production:** independent human blind fidelity/readability comparison has not occurred; no AI prose is presented as independently approved. XAI-7 can proceed with the deterministic baseline.

- Compare quality and factual adherence of approved template baseline to constrained model paraphrasing.
- Add strict contracts, provenance/atom verification, cost and latency ceilings, caching and deterministic fallback.
- Record which statements can be attributed to the rule facts. Disallow any unsupported source or invented correction.

**Gate:** on a human-reviewed blind set, naturalized prose is at least as factually faithful and clearly more readable, with no materially increased false claims. Otherwise leave AI disabled.

### XAI-7 — Unified frontend and learning modes

**XAI-7 implementation (10 Nov 2026):** Shared English-only XAI-2/3/4/5/6 plus quiz evidence now uses one typed UI contract, node/feature selection, observed parent/sibling and independently approved error-relative focus, brief/deep and mobile zoom. See [acceptance report](../reports/xai-7-unified-frontend-acceptance-2026-11-10.md). **Source limitations remain explicit:** printed citations do not imply an accessible PDF deep link, and 0 new Cambridge diagnostic rules are enabled. The full gate requires passing model-free and real browser CI.

- Generator, Builder, Lessons, Quizzes and correction views consume identical evidence and contextual explanation records.
- Highlight selected node + governor/other side of the relation.
- Support keyboard/screen-reader traversal and verbosity controls, responsive panel, mobile zoom, cited page links.

**Gate:** browser parity tests across all modes; no raw Benepar label leaks into claimed B–R explanation.

### XAI-8 — Independent evaluation and safe rollout

- Expert/adjudicated test set with grammatical, ungrammatical, ambiguous, dialectal, stylistic and false-positive traps.
- Include multiple-error and interference cases, partial parses, contradictory recommendations, context-sensitive perfect+temporal adjunct cases, and alternative valid correction sets.
- Measure node explanation coverage, role accuracy, grounding/traceability, error precision/recall, repair validity, learner comprehension and latency independently.
- Blind-rated comparison to current UI; monitor real usage with anonymized logs and opt-in collection.

**Gate:** thresholds agreed before evaluation; no known unsupported "book-verified" or categorical error claims in signed-off test suite; report observed limitations. Ship progressively, hold rollback path and never conflate test-suite success with universal linguistic correctness.

### Non-negotiable acceptance scenarios

1. *I hate you*: S, both NP nodes, VP, V, two pronouns and each relation get distinct context-specific language.
2. *She had eaten*: correct auxiliary and complement explanation, no false alarm.
3. *She had went home*: where an approved, tested detector exists, contextualize affected verb form and governor correctly; otherwise no book-backed diagnosis.
3a. *She have went to the store yesterday*: expose the interacting agreement and auxiliary-form issues; isolate or group repairs and recheck all findings. Do not silently remove the definite-time adjunct or assume the first repair makes the sentence correct.
3b. *We’ve already discussed it yesterday*: retain Cambridge Ch. 3 pp. 144–145's contextual exception; don't treat a simple past-time-adjunct blacklist as book-certified.
4. *She had breakfast*: recognize lexical-verb use and do not apply perfect-auxiliary rule.
5. *The student saw the man with a telescope*: attachment alternatives remain explicit.
6. Unsupported chapter/structure: retain plain observational explanation without fabricated function or evidence.
7. Invalid learner-built structure: structural feedback differs from grammaticality verdict.
8. Source conflict: withhold categorical teaching claim, preserve the conflict record.
9. No LLM/network: same legitimate evidence/diagnostic availability via templates.
10. Changing a noun, verb or pronoun in a minimal pair updates the contextual statement and exact spans; no stale cached explanation.
11. Counterexample/dialect/quotation/ellipsis: do not overcorrect without eligible evidence.
12. Backwards compatibility: existing `/api/explain` contract and M4–M11 flows continue to pass.

## 11. Research and UX evaluation plan

Evaluate separately:

- **Fact grounding:** fraction of factual claims mapped to matching evidence atoms and reviewed source records; judge by independent annotation, not only string matching.
- **Constituent/function accuracy:** correct subject/predicate/head/complement/adjunct assignments on held-out B–R trees (multiple legitimate interpretations allowed).
- **Explanation specificity:** does the text name the actual sentence constituent and distinguish sibling/parent roles?
- **Error precision and recall:** calibrated against linguistically adjudicated judgments; include false-positive rate for grammatical sentences and dialect/variety cases.
- **Repair quality:** whether a proposed change fixes the cited condition while preserving reasonable intended meaning and registering unresolved issues.
- **Ambiguity honesty:** frequency of unsupported certainty vs. explicit alternatives.
- **User learning:** pre/post gain and independent comprehension questions, readability, usefulness and navigability of node vs constituent explanations.
- **Operational:** p50/p95 latency, cache hits, rule/evidence version drift, model cost, availability and accessibility.

No fabricated metric targets; set defensible numerical gates after baseline and annotated sample design. Every report must state population, adjudicator, convention version, rules enabled, and uncertainty.

## 12. Delivery order and stopping rules

**Recommended dependency order:** XAI-0 → XAI-1 → XAI-2 → XAI-3 → XAI-4 → XAI-5 → XAI-7 → XAI-8, with XAI-6 optional after a mature deterministic baseline.

At the end of each milestone:

- update this plan/checklist and record exact changed files and tests;
- report **implemented vs. prototype vs. source-review pending vs. untested**;
- surface any new linguistic disagreements rather than writing an invented crosswalk;
- retain a working reviewed-template fallback while adding features;
- do not automatically proceed past an unreviewed rule-certification gate.

**Core product promise to target:** selecting any B–R constituent reveals what it is and what it does **in this sentence**, and any explanation of "why wrong" names a verified failing grammatical relationship, the evidence in context, and the limited corrective action. It is better to give a precise structural observation than a confident but ungrounded error verdict.
