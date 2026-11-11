# Cambridge Full-Coverage Master Plan

**Goal:** autonomously extract and source-check all **20 chapters / 1,764 printed pages** of *The Cambridge Grammar of the English Language* (CGEL, 2002) as SynTutor's **primary grammatical reference** for error constraints, exceptions, grammatical explanations, and English-only lesson/quiz content. **Burton-Roberts remains the independent structural and syntax-tree authority**, and an explicitly validated crosswalk connects the two. An extracted rule does not become a live detector.

**Operating mode:** autonomous, quality-gated, English-only. No per-section or per-chapter **user approval stops**. Automated gates and direct checks of the supplied book replace *workflow waiting*, **not** independent linguistic/source review or the safety gates required for production activation. This supersedes only the stop-and-wait wording in `CAMBRIDGE_EXTRACTION_PROMPT.md`; its copyright, no-guessing, schema, exception, and ID policies remain binding.

---

## 0. Binding accelerated execution protocol — 2026-11-11

**Optimization target:** eliminate repeated setup, boilerplate reports, fragile historical test registration and redundant CI runs, **without relaxing any page-level, linguistic, exception, schema, runtime, or XAI quality standard**.

1. **Phase B first across all remaining chapters.** Finish source extraction, page audits and rule specifications for Chapters **4, 5, 7, 10, 14, 18**, then **2, 6, 8, 9, 11, 12, 15, 17**, then **1, 13, 16, 19, 20** (priority 1/2/3 as in §3), before returning to large-scale Phase C/D implementation. Chapter 3 remains source-extracted; keep and test its existing Phase C prototype, but **do not make finishing Chapter 3 detectors a prerequisite to processing Chapter 4**. No chapter will be silently dropped.
2. **Adaptive verified source batches, default 24–48 consecutive printed pages**, not the old 6–8. Use ~48–64 only for clear, low-complexity passages and ~8–24 for dense diagrams, tables, footnotes, nested exceptions, ambiguous source text or high-risk constraints. **Batch size is reduced whenever needed for accuracy**; volume never overrides comprehension. Verify text **and rendered layout** on every table/diagram/complex page, and check page labels before extraction. Never skip an unreadable item, guess or claim a page extracted while relevant evidence remains unresolved.
3. **Batch source audit, not repetitive essay documentation.** A single compact **machine-checkable per-page audit manifest** and its concise human-readable source report replace repetitive per-eight-page milestone prose. Run `python tools/cgel_batch_gate.py --manifest <batch.json>` after each batch, alongside rule schema and ledger checks. The gate checks each printed page's ledger/evidence, rule IDs, citations, constraints and false-positive guards, original English examples, all layout exceptions and unresolved items. **A manifest's `source_checked` field is an auditable agent claim, not proof of linguistic truth**. Exception interpretations still require direct source rereading.
4. **One branch and normally one pull request per chapter**, with source-audited commits per internal batch. A huge/difficult chapter may require two PRs if clearer to validate. Do not open a PR per eight pages; keep a rolling chapter summary and automatically generated coverage totals. Keep old Chapter 3 audits and tests intact.
5. **Two-tier verification with no lost gate.** After each internal batch, run deterministic local/branch checks (the batch gate, full cross-domain schema validator, ledger integrity, relevant unit/exception tests). At the **chapter PR** run **both full existing GitHub workflows, including parser-backed, XAI, database and browser regressions**; fix all failures before merge. No skipped branch protections, no fake green status, and do not merge a failing PR. Historical Phase B unit tests continue to run via **automatic discovery**; adding the next range must not require another workflow YAML edit.
6. **Only generate what the evidence supports.** Descriptive, dialectal, stylistic and prescriptive distinctions never become errors by default. Constraints must have 2+ original correct examples, 2+ original incorrect/minimal-pair examples, source-checked exceptions and valid counterexamples; other record types get 2+ valid/contrast examples without fictitious incorrect cases. Full source citations, append-only stable IDs, source variety and the **unverified** B-R crosswalk state remain intact. No source PDF or copied textbook paragraphs enter GitHub.
7. **No approval fabrication or dangerous auto-enablement.** `NEEDS_REVIEW` is not a prompt for the owner to sign off; proceed autonomously with QA. But an LLM, bulk script or passing schema test must **never** impersonate independent reviewer approval, switch crosswalks to verified, or activate a runtime detector. The existing fail-closed Cambridge registry remains authoritative; future Phase C implementation uses real validated grammatical relations, exceptions and measured held-out tests.
8. **Use stable totals and tests, not fixed interim snapshots.** Every coverage report computes counts from the ledger and catalog. Regression tests for a previous range must remain valid when other chapters add rules/pages; avoid asserting that a specific future chapter is always unprocessed or hardcoding a temporary full-book total. Keep an explicit list of known deferred blockers and do not conflate source extraction, linguistic QA, implementation, or measured correctness.
9. **No asynchronous promise.** Each user-triggered execution performs actual work and leaves a verified commit/PR or a clear blocker. `NEXT!` resumes from the current ledger; it does not mean the agent works while the chat is closed.

**Acceptance rule:** any speed optimization that reduces source coverage, exception fidelity, per-rule attribution, English-only content, independent licensing, adversarial regression coverage, or production safety is **rejected**, even if faster. The objective is less duplicate work, not lower standards. Practical task order is **Phase B across 20 chapters → cross-domain QA and overlap resolution → Phase C source-licensed detectors and measurable gold tests → Phase D interacting-error corrections → Phase E lessons/quizzes**. Independent source QA can run continuously alongside Phase B but cannot be skipped.

---

## 1. Why this plan exists (current state, measured)

- **As of 2026-11-11:** Chapter 3 has **139 of 142 printed pages extracted**, with 3 contents-only skips and no unprocessed pages. Book-wide ledger: **139 extracted, 1,610 unprocessed, 13 justified skips and 2 absent from split sources** out of **1,764** printed pages. Grammar catalog: **887 records**, including 196 pre-Phase-B records. Chapter 3 still has pending independent linguistic QA and source-to-detector licensing. Other chapters remain incomplete; do not confuse preliminary records with page-level extraction.
- The detector (`server/ruleset.py`, `server/matrix.py`) is **hand-written Python**. It does **not** read `grammar/rules/*.json`. Extracting a rule does not make a mistake detectable. **Phase C below is mandatory.**
- Earlier XAI-4/owner-approval materials do not constitute the **Cambridge production registry**. The independently gated `grammar/runtime_registry.json` currently enables **zero** Cambridge rules. Chapter 3's Phase C prototype is **candidate-only**.

---

## 2. Definition of done

1. **Source page ledger complete for all 20 chapters:** every printed page is `extracted`, `skipped_with_reason`, or `absent_from_source` in `grammar/coverage/cgel_ledger.json`, backed by direct page/figure/exception auditing. Zero `unprocessed`. Source extraction is only one gate, not proof of runtime correctness.
2. **Every error-capable rule** (`rule_type: constraint`) has a `diagnostic` block (section 4) and a detector implementation or an explicit `detector: "none_possible"` with reason.
3. **Every detector finding** produces an XAI explanation sourced from its rule ID, and a corrected sentence **plus a corrected paragraph**.
4. `scripts/basic_errors.py` and the new coverage corpus (section 7) are run in CI; the coverage table (section 9) is published.
5. Lessons and quizzes can be generated from rules by rule ID (section 6).

---

## 3. Chapter inventory (printed pages from the CGEL contents)

Page counts are approximate (next chapter start minus start). Pp. 70 and 524 are absent from the supplied split files; ten pages are textless. Record them in the ledger as `absent_from_source` / `textless`, never as blank.

| Ch | Title | Start | ~Pages | Priority | Main error areas it feeds |
|---|---|---|---|---|---|
| 1 | Preliminaries | 1 | 42 | 3 | grammaticality vs style vs dialect (override policy) |
| 2 | Syntactic overview | 43 | 28 | 2 | constituents, functions |
| 3 | The verb | 71 | 142 | **1** | agreement, tense, aspect, irregular forms, auxiliaries |
| 4 | Clause: complements | 213 | 110 | **1** | missing/extra complements, valency |
| 5 | Nouns and NPs | 323 | 202 | **1** | number, determiners, pronoun case, countability |
| 6 | Adjectives and adverbs | 525 | 72 | 2 | adj/adv confusion, comparatives, modifier order |
| 7 | Prepositions and PPs | 597 | 66 | **1** | preposition choice, stranding |
| 8 | Clause: adjuncts | 663 | 122 | 2 | adverbial placement, time adjuncts |
| 9 | Negation | 785 | 66 | 2 | double negatives, polarity |
| 10 | Clause type | 851 | 96 | **1** | questions, imperatives, inversion, word order |
| 11 | Content clauses / reported speech | 947 | 84 | 2 | embedded clauses, sequence of tenses |
| 12 | Relative constructions | 1031 | 66 | 2 | relatives, gaps, wh-words |
| 13 | Comparative constructions | 1097 | 74 | 3 | comparatives, degree |
| 14 | Non-finite / verbless clauses | 1171 | 102 | **1** | infinitive vs gerund, dangling participles |
| 15 | Coordination | 1273 | 90 | 2 | parallelism, coordinated-subject agreement |
| 16 | Information packaging | 1363 | 86 | 3 | word order variants (avoid false positives) |
| 17 | Deixis and anaphora | 1449 | 116 | 2 | pronoun reference, reflexives |
| 18 | Inflectional morphology | 1565 | 56 | **1** | irregular paradigms, spelling of inflections |
| 19 | Lexical word-formation | 1621 | 102 | 3 | derivation, word class |
| 20 | Punctuation | 1723 | ~40 | 3 | punctuation (kept separate from syntax) |

Process in priority order (1, then 2, then 3). Within a priority, go by chapter number.

---

## 4. Rule record additions (extends `grammar/schema.json`)

Every `constraint` rule gets a `diagnostic` block (add it to the schema first; this is Phase A):

```json
"diagnostic": {
  "error_family": "agreement | verb_form | tense_aspect | article_determiner | pronoun_case | preposition | word_order | missing_word | extra_word | punctuation | spelling_inflection | other",
  "error_pattern": "plain description of the mistake pattern",
  "detector": "implemented:<function or constraint id> | spec_only | none_possible",
  "detector_reason_if_none": "",
  "minimal_pairs": ["wrong sentence ||| corrected sentence"],
  "learner_explanation": "ONE paragraph, plain language, no jargon beyond Cambridge terms, says what is wrong, why, and the fix",
  "corrected_paragraph_template": "how the corrected sentence and a one-line reason are phrased",
  "variety_scope": "standard_english | variety_restricted: <which>",
  "false_positive_guards": ["valid sentences that must NOT be flagged"],
  "lesson_tags": [],
  "quiz_seeds": ["identify | correct | explain"]
}
```

Rules about prescriptive advice, dialect or style use `rule_type: stylistic_or_prescriptive` and produce **suggestions, never errors**.

---

## 5. Phases

### Phase A: infrastructure (do first, once)
1. Extend `grammar/schema.json` with the `diagnostic` block; keep backward compatibility with the 196 existing rules (migration script adds `diagnostic: null`).
2. Create `grammar/coverage/cgel_ledger.json` with one row per printed page (1 to end), state `unprocessed`, plus the absent/textless pages from the source manifest.
3. Write `tools/ledger.py`: `mark`, `report`, `check` (fails if any page is `unprocessed` or any cited page is outside a chapter).
4. Preserve `tools/bulk_owner_approve.py` only as legacy tooling; **do not use it to fabricate an owner sign-off or independent review**. Runtime activation continues to require the independently checked `grammar/runtime_registry.json` source, B-R crosswalk, implementation, tests and approval gates. The user's instruction to proceed autonomously is **not** evidence of linguistic approval.
5. Add the ledger check and schema validation to CI.

### Phase B: accelerated source extraction (all remaining chapters, before broad Phase C)
For every remaining chapter in §3 priority order, without waiting for phase C of the previous chapter:
1. Verify the **actual supplied source**, PDF edition, printed-to-PDF page mapping, first/last page labels, and chapter boundaries. Read **every printed page consecutively**, by default in **24–48 page internal batches**. Adaptive size and nonprose rendering requirements in §0 are binding; source complexity overrides batch size.
2. Extract **all error-relevant and lesson-relevant evidence**: definitions, classifications, paradigms, constraints, exceptions, variation, diagram/table content, footnotes, contrasts and warnings against prescriptive misconceptions. Independently inspect page image/layout where the text extractor is unreliable.
3. Use **atomic source-grounded records**, immutable IDs, print/PDF page citations, the exact semantic scope, original **English-only** examples, explicit exceptions and cautious B-R mappings. **Constraints** require 2+ correct and 2+ incorrect examples and matched minimal pairs and guards; **nonconstraints** require 2+ positive or contrast examples and must not invent mistakes.
4. Specify the `diagnostic` for every new error-capable constraint (or record an explicit source-grounded no-detector rationale); keep it `spec_only` until Phase C licensing. Nonconstraints have no diagnostic. Never treat advice, style or dialect variation as a universal error.
5. After each internal batch, update the ledger and append a compact **per-page source-audit manifest** plus concise report. Run `python tools/cgel_batch_gate.py --manifest <batch.json>` and the schema/ledger/relevant tests. All source-audit fields must reflect pages actually read; unresolved items block completion.
6. Collect consecutive checked batches on **one feature branch per chapter** whenever practical. Generate the chapter audit and truthful `COVERAGE.md` ledger statistics once per chapter PR rather than rewriting repeated milestone prose. Full GitHub CI, including all previous regressions, **still must pass on the final PR SHA before merge**. Never declare chapter source-complete with unprocessed pages.
7. The first remaining chapter is **Chapter 4 (printed pp. 213–322)**, followed by the §3 priority order. No need to restart Chapter 3 extraction or redo its passing test suite manually.

### Phase C: wire source-licensed rules into detection and XAI (after broad Phase B)
Do this **after all 20 chapters have source extraction** (except for minimal shared infrastructure or urgent correctness fixes). Chapter 3's existing candidate prototype is preserved. This is what actually makes source-grounded mistakes detectable, rather than merely catalogued.
1. For each new `constraint` with `detector: spec_only`, implement a detector (in `server/ruleset.py` or a new `server/cgel_detectors.py` loaded by the matrix), keyed by the rule ID so findings carry `rule_id`.
2. Each finding must return: `rule_id`, token/char span, the governing relation (both tokens when two are involved), `learner_explanation` from the rule, source pages, and any `variety_scope`.
3. Add `false_positive_guards` as negative tests. A detector is not done until its guards pass.
4. Register enabled rules through the **fail-closed `grammar/runtime_registry.json` after independent source review, resolved B-R crosswalk, implementation and adversarial/held-out tests**. Passing unit tests or owner-consented autonomous execution does **not** authorise setting an unreviewed rule to `APPROVED`. Keep XAI-4 (`server/xai4_partial.py`, `explanations.py`) subordinate to the registry and actual validated syntactic evidence.
5. Implement multi-error handling per `docs/planning/XAI_SOURCE_AUDIT_MULTI_ERROR.md`: group interacting findings, re-evaluate each candidate fix, never certify a whole sentence from a partial rule set.

### Phase D: corrected paragraph output
- For any input text, return: (a) per-error findings, (b) a **corrected paragraph** (the full text with all accepted fixes applied) with a short change list, (c) which findings could not be fixed safely and why.
- Fixes follow the bounded search in the multi-error doc: generate candidates, re-run all detectors on each, reject candidates that introduce new errors, cap depth and candidates, detect loops, preserve meaning.

### Phase E: lessons and quizzes
- Generate lesson skeletons and quiz seeds from rules by `lesson_tags` and `quiz_seeds`. Quizzes use original sentences only. No textbook exercise text.
- Every lesson/quiz item stores the rule ID(s) and printed pages it came from.

---

## 6. Content rules (kept from the repo protocol)

- Paraphrase only. No paragraphs, long quotes or full tables from the book; at most one fragment under 15 words per rule, only when the exact wording matters.
- Examples are AI-authored; book examples only if a single short clause, flagged.
- Use Cambridge's terms exactly (`preterite`, `past participle`, `gerund-participle`, `determinative`). Record traditional terms in `traditional_terms`.
- Burton-Roberts mappings: `unverified` unless B-R text is supplied. Never invent one.
- Do not commit PDFs or extracted prose. Commit rules, ledger, reports, code.
- Never guess. If a table or diagram is unreadable, list it under `uncertain_items` with its page.

---

## 7. Coverage corpus

Create `evaluation/cgel_coverage_corpus.json`: for every `error_family`, at least 10 wrong sentences with the expected rule ID and corrected sentence, and at least 10 valid sentences (including each rule's exceptions and dialect cases). Seed it from `scripts/basic_errors.py`. Report precision (valid sentences wrongly flagged) and recall (errors caught) per family.

---

## 8. Automated gates (these replace human approval stops)

A **source batch** may advance within Phase B only after the **batch checks** below pass; the chapter PR must additionally pass the full integration workflows. Phase C/D release needs its *own* strict licensing/accuracy gates. These are not interchangeable:
1. JSON validates against `grammar/schema.json`; IDs unique and never renumbered.
2. Every cited printed page falls inside the chapter and is not textless.
3. Every constraint has 2+ correct and 2+ incorrect examples and a `diagnostic` block.
4. Each **completed batch** has no unprocessed printed pages within its audited range and references existing source evidence and per-page audit entries; a **chapter cannot be called source-complete** until its entire chapter ledger contains no unprocessed pages and all skips have reasons.
5. A batch runs the cross-domain schema, coverage/manifest and relevant rule/exception tests. **Full `server`, database, parser-backed, XAI and browser CI still runs on every chapter PR and must pass before merge**; new detectors separately pass positive, negative, false-positive, dialect and adversarial tests before activation.
6. `python scripts/audit_xai_pre.py --require-contracts` still passes (the source audit file must not be edited to claim review that did not happen).
7. Each extracted rule is checked against the **actual printed page and relevant footnotes/tables/diagrams** for the claimed exception list; record page-specific evidence and uncertainties. The mechanical manifest alone **cannot certify** source truth. No fabricated claim of independent review or runtime reliability.

---

## 9. Required reporting (honest coverage)

Each chapter report and a root `COVERAGE.md` must state: pages processed / total, rules added, detectors implemented / spec-only, error families caught per the corpus, known gaps. Never write "complete" for a chapter whose ledger has gaps.

---

## 10. Agent prompt (paste this)

```
Read docs/planning/CAMBRIDGE_FULL_COVERAGE_MASTER_PLAN.md and
CAMBRIDGE_EXTRACTION_PROMPT.md. The master plan overrides the stop-and-wait
rules: work autonomously with no approval stops. Phase A is complete. Use the binding acceleration protocol in section 0:
complete Phase B source extraction for ALL remaining chapters in priority
order before broad Phase C/D. Next: Chapter 4, printed pp. 213–322.
Use adaptive 24–48-page source-verified internal batches (smaller whenever
the text/tables/diagrams are dense); process every page and exception.
For each batch write a compact per-page JSON audit manifest and source
report; update ledger and original-English rules; run
python tools/cgel_batch_gate.py --manifest <batch.json> plus schema/ledger
checks. Normally one feature branch/PR per chapter, not per 8 pages.
Run BOTH full existing GitHub workflows on the final PR SHA, fix all
failures, then merge. Do not auto-approve source rules, invent crosswalks,
enable unverified detectors or claim measured accuracy.
Preserve XAI node/group/reparse/corrected-paragraph gates for later phases.
Report only work actually executed and validated; no approval stops.
```
