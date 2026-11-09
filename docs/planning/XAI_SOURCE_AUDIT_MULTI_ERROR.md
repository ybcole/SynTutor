# SynTutor XAI — Uploaded-Book Source Audit and Multi-Error Repair Protocol

**Date:** 10 November 2026  
**Status:** Design and targeted source verification, **not a full independent audit of both books and not implemented code**.  
**Applies before:** XAI-0 baseline and all XAI milestones.  
**Authorities:** Noel Burton-Roberts, *Analysing Sentences: An Introduction to English Syntax*, **third edition**, Pearson 2011; Huddleston & Pullum et al., *The Cambridge Grammar of the English Language* (**CGEL**), CUP 2002, uploaded 2016 printing.

See [XAI_MASTER_PLAN.md](XAI_MASTER_PLAN.md), [MASTER_PROMPT_XAI.md](MASTER_PROMPT_XAI.md), [CONVENTIONS.md](../../CONVENTIONS.md).

> **Core decision:** an error belongs to a **failed grammatical relation or construction**, not necessarily to an intrinsically "wrong word"; a repair is a **conditional transformation of a candidate analysis**, not proof that the remainder of the original sentence is grammatical. Multi-error sentences require immutable original evidence, simultaneous problem discovery where possible, explicit error dependencies, grouped or separately validated repairs, and a full reassessment after any edit.

## 1. Exact supplied editions and citation policy

- Burton-Roberts: 294 PDF pages; title/copyright identify **third edition** (2011). Cite **printed** pages, not PDF indices. The third-edition preface on printed pp. ix–x contains important changes compared with the older-edition prefaces bundled in the PDF. Never treat older prefaces as an instruction to retain `Vgrp`.
- Cambridge: 1,862 PDF pages, **2002** content (2016 printing). Printed page numbering differs from PDF physical pages; cite **printed** pages. It contains **20 substantive chapters**; reviewing only the first 10 or 11 chapters is insufficient.
- These attached source volumes are research/reference material. Do **not** publish long passages or reproduce the book as generated runtime answers. Create independently checked, original paraphrases with edition and printed-page provenance.
- This document verifies *selected* passages directly against the attached books. It **does not** certify source review of every one of the 20 CGEL or 11 B–R chapters, existing extracted rule JSONs, or 252 B–R reference trees. Those audits remain mandatory.

## 2. Important book-grounded findings before any runtime error rules are enabled

| Source and printed page | Directly supported point | Specific XAI consequence | Current review scope |
| --- | --- | --- | --- |
| B–R third-edition preface **ix–x** | Third edition removes `Vgrp`; each auxiliary is analyzed as the **head of a VP taking another VP complement**. Category changes include specified temporal words as prepositions and notation `name`, `pronoun`, `C1/C2`, `S′/S″`, indexed VPs and gap bullet | Explanation engine must traverse nested auxiliary VPs, preserve genuine B–R hierarchy; don't simply rename a Penn auxiliary node | Book passage verified; runtime details **not certified** |
| B–R Ch. 1 **pp. 10–17** | Constituent identity and boundaries depend on the whole sentence/interpretation; the same adjacent string need not be a constituent in another sentence. Structural ambiguity is real | Node explanations must cite full-sentence span and selected analysis, not just an isolated word string. Competing attachments cannot be merged into one categorical fact | Book passage verified; examples not exhaustive |
| B–R Ch. 2 **pp. 31–38** | Functions arise from structural dependency: subject–predicate, modifier–head, head–complement. Category is not identical to function | XAI must explain an NP **as a subject or object in this configuration**, never label every NP "subject" | Scoped to summary and surrounding source, deeper pass pending |
| B–R Ch. 6 **pp. 115–118**, **121–122** | Distinguishes lexical `have` from perfect auxiliary `PERF`; modals have special form requirements; perfect `have` selects a **perfect participle** (e.g., `went` vs `gone`); auxiliaries head VP complements and can be stacked | Contextualize the *auxiliary → selected verb form* relation and its actual lexical paradigm before assigning blame. Lexical `had` in "had breakfast" must not trigger a perfect-participle requirement | Selected passages verified |
| CGEL notational conventions **pp. xi–xii** | Distinct annotations: `*` ungrammatical, `#` semantic/pragmatic anomaly, `%` dialect restricted, `?` doubtful grammaticality, `!` non-standard; B–R's marker conventions are not interchangeable with CGEL's | Preserve **different status types** instead of collapsing every unusual form into "incorrect"; record interpretation and selected variety | Verified |
| CGEL Ch. 1 **pp. 2, 5–10** | Descriptive grammar of *present-day Standard English*, not universal writing advice; style, dialect, variation and grammaticality differ. Some non-standard forms are grammatical in non-standard dialects | Separate grammar violations from stylistic recommendations, non-standard/dialectal use, semantic oddity, punctuation and unsupported variety | Verified |
| CGEL Ch. 3 **pp. 74–77** | Distinguishes **preterite**, **plain form**, **gerund-participle**, and **past participle**; form identity/syncretism is common. The same orthographic form may realize different grammatical forms in different constructions | Surface string alone does not prove tense or participial features. Need typed inflectional analysis, not regex-only "went/had/was" labels | Verified |
| CGEL Ch. 3 **p. 106**, table [44] | Modal → plain form; perfect → past participle; progressive → gerund-participle; passive → past participle | Implement a **directional selection constraint** on a lexical/auxiliary chain. Local diagnosis can operate with enough lexical evidence even if another independent part is malformed | Verified, implementation pending |
| CGEL Ch. 3 **pp. 142–145** | Present perfect normally disallows adjuncts explicitly locating an event wholly in the past, **but has contextual exceptions**, e.g., an experiential perfect in the presence of `already` with `yesterday` | **Do not create a categorical "present perfect + yesterday = ungrammatical" rule.** Model discourse/tense/aspect, exclusions, exceptions and uncertainty; do not auto-delete `yesterday` | Verified; high-priority adversarial test |
| CGEL Ch. 3 **p. 146**, note 38 | Some recent-past uses show AmE/BrE variation (`just`, `already`, `yet`) | Variety/register parameters must affect suggestions, not global grammar verdicts | Verified |
| CGEL Ch. 18 **pp. 1596–1610** | Inflectional morphology, irregular preterite/past participle paradigms and variation | Lexical form validation needs paradigms and genuine exceptions; do not "correct" acceptable syncretic or dialectal forms | Chapter targeted, complete tables **not yet independently audited** |

### Cross-framework terminology guardrails

- B–R calls the form after perfect `have` a **perfect participle** (Ch. 6 p. 117); CGEL's corresponding inflectional category is the **past participle** (Ch. 3 pp. 74, 76–77, 106). This is a **crosswalk**, not a claim that one book is mistaken or permission to relabel B–R tree nodes.
- B–R calls the `-ing` verb selected by progressive `be` the **progressive participle** (Ch. 6 p. 118). CGEL uses **gerund-participle** for the common `-ing` inflectional form (Ch. 3 pp. 74, 80, 106). The selection constraint can correspond even when the full category frameworks differ.
- B–R lexical `have` + NP and `PERF` + VP are different structures. CGEL also distinguishes perfect `have` from lexical `have` (Ch. 3 §§2–3); never infer from spelling.
- B–R third-edition categorization of `now/then/when/here/there/where` and some temporal conjunction/preposition boundaries must be checked against CGEL's own distributional categories, **not blindly equated**. Mark any unverified crosswalk pending.
- B–R constituent/function analysis and CGEL grammatical function/constituent classifications can overlap but need explicit feature-by-feature mapping; no silent replacement of B–R tree notation.

### Cambridge 20-chapter coverage inventory — **audit checklist**, not "all chapters read"

| CGEL chapters, printed first page | Domains to index for XAI | Risk if ignored |
| --- | --- | --- |
| 1 Preliminaries, **1** | Descriptive scope; grammaticality vs semantics, usage, dialect, lexical vs syntactic claims | Overcorrection and false certainty |
| 2 Syntactic overview, **43** | Structural categories, functions, hierarchy, ambiguity | Wrong parent/head/role explanations |
| 3 The verb, **71** | Auxiliary chains, inflection, agreement, aspect/tense, irregular verbs, lexical vs auxiliary | False verb-form corrections and interacting errors |
| 4 The clause: complements, **213** | Subject and object, predicative complements, licensing and valency | Misidentifying what the verb requires |
| 5 Nouns and noun phrases, **323** | Determinatives, pronouns, number, case, possession and NP structure | Fake article errors, misidentified NP roles |
| 6 Adjectives and adverbs, **525** | Modification and distribution | Adjunct/compliment category confusion |
| 7 Prepositions and PP, **597** | P category, selected complements, adjuncts | Contradictory P/Adv classifications across books |
| 8 The clause: adjuncts, **663** | Scope, timing, time adjuncts, adverbial positions | Unlicensed "yesterday" or placement corrections |
| 9 Negation, **785** | Scope, negation, polarity, dialectal negative concord | Treating nonstandard varieties as globally ungrammatical |
| 10 Clause type and illocutionary force, **851** | Questions, imperatives, exclamatives, inversion | Incorrectly forcing declarative word order |
| 11 Content clauses and reported speech, **947** | Embedded complements, interrogatives, finite vs nonfinite embedding | Incorrect verb-form constraints in subclauses |
| 12 Relative constructions/unbounded dependencies, **1031** | Gaps, extraction, wh/relative chains | Invented missing words or misattached gaps |
| 13 Comparative constructions, **1097** | Comparison and degree | Invalid modifier/case expectations |
| 14 Non-finite and verbless clauses, **1171** | Nonfinite licensing, control, understood subjects | Invented subject or false infinitive error |
| 15 Coordination and supplementation, **1273** | Head/number and coordinated phrase structure, supplements | Bad agreement and scope diagnosis |
| 16 Information packaging, **1363** | Focus, topicalization, clefts, noncanonical order | Overcorrecting legitimate word order |
| 17 Deixis and anaphora, **1449** | Reference, antecedents, context and discourse | False pronoun errors and unwarranted anaphora assertions |
| 18 Inflectional morphology, **1565** | Surface forms, irregular paradigms, syncretism | Wrong repair to irregular forms |
| 19 Lexical word-formation, **1621** | Morphological derivation/word class | Wrong derivational claims; scope limits |
| 20 Punctuation, **1723** | Sentence writing conventions, punctuation boundaries | Mixing orthography into B–R syntax and error scores |

### Burton-Roberts all-chapter coverage inventory — **audit checklist**

| B–R chapters | Primary XAI role |
| --- | --- |
| 1 Constituents | Span boundaries, constituency tests, structural ambiguity |
| 2 Functions | Subject/predicate, head/modifier/complement relationships |
| 3 Categories | Lexical/phrase categories, P/PP and coordination |
| 4 Basic VP | Lexical complements, transitive/intransitive and related frames |
| 5 Adverbials | VP levels, adjunct placement, ellipsis and S-adverbials |
| 6 Auxiliary VPs | MOD/PERF/PROG/PASS, form selection, question/negation, nested VPs |
| 7 NP structure | DET, NOM, pre/post modifiers, NP complements and ellipsis |
| 8 Embedded sentences | S′, C, subordinate functions, complement clauses |
| 9 Wh-clauses | Higher C positions, movement, relative clauses, gaps |
| 10 Non-finite clauses | Verb forms, C1/C2, control and nonfinite complements |
| 11 Language and grammars | Scope/limitations of an analysis and formal grammar |

**Mandatory pre-implementation work:** complete a reproducible source-to-claim inventory across all chapters, prioritize constructions actually encountered in the intended product, identify conflicting analyses, build exceptions and minimal pairs, and distinguish source-checked from runtime-tested. The tables above are a chapter-wide coverage **plan** rather than proof of reading every page.

## 3. Multiple errors: define the problem correctly

An original user string may have:

1. **Independent violations**: changing one has no relevant effect on conditions for another.
2. **Interacting violations**: two or more constraints share a construction or head/feature, so one "repair" can change the applicability of the others.
3. **Masked violations**: the original analysis lacks information needed for a check, which becomes evaluable after a different repair.
4. **Competing diagnoses**: alternative parses or intentions explain the same surface sequence differently.
5. **False positives or dialectal/style differences**: not errors at all under some licensed interpretation/variety.
6. **Cross-sentence dependencies**: anaphora, tense sequence, ellipsis, quoted and reported contexts may require more context than the selected sentence.

An unchecked parse of an ungrammatical sentence is **not** a complete fact base. Some checks can run on reliable local tokens/inflectional evidence; others need sufficiently licensed constituent structure or reference context.

### Fundamental rule

**Evaluate an edit against its own proven rule obligations, not against a fiction that the original remainder is correct.** The original string remains immutable; a proposed correction is a new sentence candidate with new parsed evidence and its own verdicts.

## 4. Correct formal model

Let `U0` be the original input, `H0` a set of plausible parse/lexical hypotheses (not necessarily one tree), `R` the eligible, versioned rules, and `E(U,H,R)` a partial evaluator. Each rule outcome is one of:

- `SATISFIED` — applicable and proven satisfied;
- `VIOLATED` — applicable and proven failed, with exact evidence;
- `NOT_APPLICABLE` — precondition does not hold;
- `BLOCKED` — insufficient/contradictory structural evidence;
- `AMBIGUOUS` — hypotheses or varieties lead to different outcomes;
- `UNIMPLEMENTED` — the rule itself is not enabled, **not** a pass.

Use a dedicated `error_finding` record with:

`finding_id, original_input_id, rule_id/version, anchor_token_ids, span, governing_node_ids, required_relation, observed_relation, proof_atoms, counterevidence, preconditions, interpretation_id, variety, confidence_scope, status, source_pages`.

A finding may affect a **pair or set of nodes** (e.g., subject ↔ finite verb, auxiliary ↔ participle), not a single character span.

### Error interaction graph

Build a graph over `VIOLATED`, `AMBIGUOUS` and `BLOCKED` findings. Typed edges include:

- `SHARES_GOVERNOR`, `SHARES_CONSTRUCTION`, `OVERLAPS_SPAN`;
- `CHECK_DEPENDS_ON` and `CHECK_BLOCKED_BY`;
- `REPAIRS_CONFLICT`, `REPAIR_ENABLES`, `REPAIR_MASKS`;
- `ALTERNATIVE_INTERPRETATION` (mutually exclusive parse hypotheses).

Do **not** assume overlapping token ranges mean two separate errors; deduplicate equivalent rule findings with one underlying cause. Likewise, two different tokens can fail a **single** relational requirement.

Treat independent connected components separately when proven safe. Evaluate tightly interacting components as a **joint repair group**. If a broken subtree blocks an adjacent rule, report it as `BLOCKED`, not "valid."

## 5. Candidate generation and counterfactual verification

Algorithm outline (architecture recommendation; **not a rule prescribed by either book**):

1. **Snapshot:** freeze `U0`, token offsets, all available hypotheses and initial findings. The user must always be able to inspect their original words.
2. **Detect first:** run every enabled independent rule whose preconditions are actually met. Build the original finding set, including blocked/ambiguous statuses.
3. **Group interactions:** construct dependency graph; determine independent vs. jointly constrained findings.
4. **Propose evidence-licensed edits:** minimal local word-form changes, missing complements/DET, insert/delete/move proposals only if justified by an approved rule and explicit meaning constraints. Record each proposed edit's **intended issue IDs** and prerequisites.
5. **Evaluate counterfactuals:** build `U1 = apply(U0, edits)` as a separate candidate. Token alignment is immutable across the original, but remapped to new IDs in each candidate. **Rerun candidate parsing and all applicable enabled rules**—not just the one targeted check.
6. **Reconcile every original finding:** separate `resolved_by_satisfaction`, `no_longer_applicable_after_rewrite`, `persists`, `still_blocked`, `changed_interpretation`. A disappearing diagnostic is not necessarily "fixed"; deleting the governing structure can make a rule **inapplicable** instead.
7. **Track newly observable outcomes:** `new_violation`, `unmasked_violation`, or `ambiguous_new`. Do not blame an edit for a newly visible error unless evidence establishes **causality**, not just chronology.
8. **Compare minimal coherent repair packages:** prioritize evidence coverage, preservation of intended meaning, number/severity of justified edits, source and variety compatibility. Do not universally optimize Levenshtein distance at the cost of meaning.
9. **Stop safely:** bound repair depth, candidate count, inference latency, repeated states and loop detection; return unresolved or ask about meaning/variety if no safe package is available. Never run an unbounded "auto-fix until the sentence is clean" loop.
10. **Explain per original finding and per candidate:** report what each edit addresses, what remains, any reinterpretation, and why an entire corrected sentence is **not automatically certified**.

Don't use a model's grammaticality score as proof of successful repair. Optional learned correction systems may propose candidate edits but cannot approve them.

### Concrete example: interacting errors + temporal context

Original: **She have went to the store yesterday.**

- `F1`: In an ordinary finite present perfect construction, third-person singular **she** is incompatible with finite **have**. This is a possible agreement violation when that interpretation is secure.
- `F2`: Perfect auxiliary **have** selects a **past participle**; **went** is the preterite of **go**, while **gone** is its past participle (B–R Ch. 6 p. 117; CGEL Ch. 3 pp. 76, 106).
- `F3`: In a **present-perfect** interpretation, the temporal adjunct **yesterday** ordinarily excludes the present-perfect reading, but CGEL Ch. 3 pp. 143–145 explicitly documents **exceptions**. Therefore treat as **context-sensitive** and never an unconditional third violation.

Potential counterfactuals:

| Candidate | What changed | What it proves and does NOT prove |
| --- | --- | --- |
| She **has** went to the store yesterday. | `have → has` | Addresses F1 only; F2 remains; temporal interpretation may still require review. **Not a globally corrected sentence.** |
| She have **gone** to the store yesterday. | `went → gone` | Addresses F2's form requirement; F1 remains; tense–time context unresolved. |
| She **went** to the store yesterday. | Remove auxiliary `have`; keep `went` | A **different preterite construction** can express a definite past event, but F1/F2 become *not applicable after a reanalysis*, not separately proven "fixed." Preserve intended meaning and confirm context. |
| She **has gone** to the store. | `have → has`, `went → gone`, remove explicit definite past adjunct | A present-perfect alternative. It changes time/aspect information; must not be silently substituted for the author's intended definite past account. |

**UI principle:** for a selected `have` or `went`, explain the shared construction and show both issues as interacting. Offer "Address this issue only (other issues remain)" **or** a jointly evaluated sentence alternative, never a claim that the isolated word fix makes the sentence grammatical.

This is exactly why using *one error's XAI explanation in an otherwise erroneous sentence* is feasible **only if its rule preconditions are locally established** and the explanation states its scope.

### Independent-error example

**The boys is carrying a boxes.** Assuming standard-English declarative interpretation:

- Finite agreement `boys ↔ is`: possible `is → are`.
- NP determiner/number `a ↔ boxes`: possible remove `a` / replace phrase according to intended meaning.
- They occur in separate constructions; a locally certified fix for one can be explained while the other remains. Reparse and rescan after both edits. Do not conflate these into a single grammatical error.

### Blocked-by-parse example

An unlicensed verb form may make the parser misattach a dependent clause. If a proposed attachment-sensitive diagnostic depends on that part of the tree, output **BLOCKED_BY_UNRESOLVED_STRUCTURE**, not "correct". A safe local inflectional check can still run if it has independently sufficient lexical evidence.

## 6. Suggested versioned schema (proposal, no existing implementation)

```json
{
  "schema_version": "xai-multierror-1.0-draft",
  "original": {"input_id": "u0", "text": "She have went to the store yesterday.", "immutable": true},
  "hypotheses": [{"id": "h0", "status": "candidate_parse_not_canonical_proof"}],
  "findings": [
    {
      "id": "f1",
      "rule_id": "REVIEWED_AGREEMENT_RULE_ID_HERE",
      "status": "VIOLATED",
      "governor_ids": ["subject_np", "aux_head"],
      "affected_token_ids": ["she", "have"],
      "interpretation_id": "h0",
      "source_review": "NOT_YET_APPROVED_FOR_RUNTIME"
    },
    {
      "id": "f2",
      "rule_id": "REVIEWED_PERFECT_SELECTION_RULE_ID_HERE",
      "status": "VIOLATED",
      "governor_ids": ["perf_head", "lexical_verb"],
      "affected_token_ids": ["have", "went"],
      "interpretation_id": "h0",
      "source_review": "NOT_YET_APPROVED_FOR_RUNTIME"
    }
  ],
  "dependencies": [{"from": "f1", "to": "f2", "kind": "SHARES_CONSTRUCTION"}],
  "candidates": [
    {
      "candidate_id": "u1",
      "text": "She has went to the store yesterday.",
      "edits": [{"op": "replace", "original_token_id": "have", "new_text": "has"}],
      "targeted_finding_ids": ["f1"],
      "finding_lineage": [
        {"finding_id": "f1", "after": "resolved_by_satisfaction"},
        {"finding_id": "f2", "after": "persists"}
      ],
      "new_findings": [],
      "whole_sentence_certified": false
    }
  ],
  "analysis_status": "DRAFT_ILLUSTRATION_NOT_RUNTIME_EVIDENCE"
}
```

The example is a **shape/protocol illustration**: placeholder rule IDs and `VIOLATED` records are **not** a claim that the repository currently has enabled Cambridge detectors. Actual runtime must enforce provenance/allow-lists, stable UUID/token IDs, compatible variety/interpretation, deterministic diff and schema validation.

## 7. Acceptance gates and tests that must precede learner-facing correction

1. **Two independent errors:** single edit helps one; other remains visible and its original anchors remain stable.
2. **Two interacting errors:** grouping and joint repair planning work; isolated fixes show "other issues remain."
3. **Single broken relation, two flagged tokens:** deduplicated into one core finding with multiple affected spans, not double-counted.
4. **Reanalysis:** deleting/changing an auxiliary can make a participle-selection constraint **not applicable**, which is distinct from proving it satisfied.
5. **Unmasking:** a new finding after editing is labelled "newly evaluable" unless independently shown to have been introduced.
6. **Repair cycle:** repeated edit candidates terminate with a bounded search and no infinite alternation.
7. **Preservation:** original text, order, punctuation, provenance, stable spans and original B–R tree remain inspectable.
8. **Word/constituent parity:** clicking both `had` and its VP exposes the same underlying problem and consistent correction status.
9. **Cambridge exception:** do **not** categorically reject *We've already discussed it yesterday* (CGEL Ch. 3 pp. 144–145); avoid a simplistic `perfect + yesterday` blacklist.
10. **Lexical–auxiliary disambiguation:** *She had breakfast* must not inherit a `PERF` complement constraint; *She had eaten* must.
11. **Syncretism:** *She had wanted the car* uses the surface past participle form; do not reject solely because it looks identical to the preterite (CGEL Ch. 3 p. 76).
12. **Dialect, quotations, ellipsis, special registers:** no universal correction claims from unsupported assumptions.
13. **Meaning and temporality:** choose between *She went yesterday* and *She has gone* only with defensible context or user confirmation; don't silently remove `yesterday`.
14. **Partial tree:** a reliable local morphology finding may be explained, while blocked tree-dependent checks stay blocked.
15. **Source gating:** no original-book-looking runtime "citation" supplied by an LLM, client, stale source record or unapproved rule.
16. **Cross-client parity:** Generator, Builder and corrected/original tree views reuse the **same finding IDs**, issue groups and explanation provenance.
17. **Corpus evaluation:** pre-register a **held-out multi-error gold set** with independent judgments about issue count, overlapping causes, minimal repair sets, conditional interpretations and allowable alternatives. Measure precision, cause attribution, correction interaction handling and false positives separately from generic grammaticality accuracy.

## 8. Changes to XAI milestones: prerequisite and implementation order

### XAI-PRE — Mandatory uploaded-source review + interaction contract **BEFORE XAI-0 implementation**

- Confirm source editions and printed page anchors; inspect the 20 CGEL and 11 B–R chapter coverage inventory; source-check relevant passages for each first-wave construction.
- Resolve key terminology crosswalks; list source exceptions (especially tense/aspect, auxiliary selection, dialect/usage) before writing executable grammar checks.
- Approve the **partial evaluator states**, error interaction/dependency graph and versioned candidate/lineage API.
- Establish multi-error and dialect/temporal minimal-pair fixtures as part of baseline.
- **Gate:** sign off the contracts and narrow initial source review; unresolved chapter sections remain explicitly "not yet checked".

### XAI-0 / XAI-1

- Extend baseline inventory with multi-error cases, blocked analyses and exception catalog.
- Do not mark all-source coverage complete from a 20-row table; attach per-claim printed-page checks and independent review records.

### XAI-2 / XAI-3

- Fact graph must permit partial/contradictory analysis and track stable provenance, original token spans, governing relationships and proof scope.
- Word and constituent explanations may be structural observations even when no global grammaticality judgment exists.

### XAI-4

- Implement **partial evaluation** and dependency tracking simultaneously with each approved Cambridge constraint. Don't return a boolean "grammatical" field that hides blocked rules.
- Have actual morphological and lexical checks independent of global canonicalization where safe. Rule exception/variety tests required.

### XAI-5

- Implement grouped repairs, counterfactual reparse/recheck, original-to-candidate finding lineage, minimal coherent alternatives and issue-specific explanations.
- Per-issue "fixed" state is subordinate to the new candidate's proof, and whole-sentence "all clear" is not available unless a declared, sufficiently broad approved rule set actually covers its relevant constructions.

### XAI-6 / XAI-7 / XAI-8

- LLM naturalizer receives an issue group and allowed repair proof; it **cannot** independently resolve dependencies or decide a global verdict.
- UI displays **resolved / remaining / newly apparent / uncertain** groups, plus original vs alternative tree and reversible edits.
- Human-adjudicated held-out tests must include multiple simultaneous errors and ambiguous alternatives, not only one-error minimal pairs.

## 9. Decisions and explicit unresolved items

**Decided:** no piecemeal declaration of "fully corrected" from a partially broken sentence; do not overwrite the original; separate local proof from global validity; process interacting errors together; distinguish repair-induced vs newly unmasked findings; preserve human choice when tense/meaning changes; citations governed by specific edition and printed pages.

**Still to be done:** full independent audit of all relevant chapters and tables, complete B–R↔CGEL category crosswalk, grammar/lexicon implementations, rule approver sign-off, empirically calibrated repair ranking and latency budget, exact approved API schema, parser-backed multi-error test suite. **No runtime code changes are made in this documentation increment.**

**Source-note example of why we need exceptions:** CGEL Ch. 3 pp. 143–145 explicitly moves from the usual past-adjunct restriction on the present perfect to a restricted experiential case where the marker `already` changes the interpretation. A rule constructed from just p. 143 would be overgeneralized. This is not speculative: it is the kind of nuance the Cambridge volume itself supplies, and a concrete reason to review source sections **including exceptions** before enabling automatic correction.
