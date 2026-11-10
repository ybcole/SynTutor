# Cambridge Full-Coverage Master Plan

**Goal:** an AI agent extracts *The Cambridge Grammar of the English Language* (CGEL, 2002), all 20 chapters and about 1,760 printed pages, into SynTutor's knowledge base. That knowledge base is the single source for (1) lessons, (2) quizzes, and (3) the XAI explanation shown when the detector finds a mistake.

**Operating mode:** autonomous. The agent works through whole chapters with **no per-section or per-chapter human approval stops**. Quality is enforced by automated gates (section 8), not by waiting. This supersedes the "stop and wait" rules in section 10 of `CAMBRIDGE_EXTRACTION_PROMPT.md`. All other rules in that file (copyright, no guessing, schema, ID policy) still apply.

---

## 1. Why this plan exists (current state, measured)

- Extraction so far covers about **2-4 pages per chapter** (the first section only), for **196 rules**. Chapter 3 ("The verb") has only pp. 74-75; Chapter 13's report says §§1.2-6.3 were not processed.
- The detector (`server/ruleset.py`, `server/matrix.py`) is **hand-written Python**. It does **not** read `grammar/rules/*.json`. Extracting a rule does not make a mistake detectable. **Phase C below is mandatory.**
- Four XAI-4 Cambridge rules are enabled by `grammar/owner_approvals.json` (owner-approved, provisional). Everything else needs new rules.

---

## 2. Definition of done

1. **Page ledger complete:** every printed page of every chapter is `extracted`, `skipped_with_reason`, or `absent_from_source` in `grammar/coverage/cgel_ledger.json`. Zero `unprocessed`.
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
4. Write `tools/bulk_owner_approve.py`: promotes `NEEDS_REVIEW` rules to `APPROVED` with `approved_by: "owner_bulk"` and today's date, only when all mechanical gates in section 8 pass. This is the single owner sign-off (run once per chapter, no per-rule review).
5. Add the ledger check and schema validation to CI.

### Phase B: extraction loop (per chapter)
For each chapter in priority order:
1. Read the chapter PDF **from its first printed page to its last**, in consecutive ranges of about 6-8 pages. Do not stop between ranges.
2. Extract **everything error-relevant and everything lesson-relevant**: definitions, category tables, paradigms, constraints, exceptions, contrast tables, diagrams, and the book's own "this is often said but is not a rule" discussions.
3. One atomic rule per principle, with printed-page citations, 2+ correct and 2+ incorrect original examples, a minimal pair, and every exception the book states. Never merge a rule with its exception.
4. Fill the `diagnostic` block for every `constraint`.
5. Update the ledger for every page in the range as you go.
6. Run the mechanical gates (section 8) after each range. Fix failures before moving on.
7. Write `sources/cambridge/chapter_NN/CHAPTER_NN_REPORT.md`: pages processed, rules added by ID, skipped items with page numbers, uncertain items, **honest coverage percentage**.

### Phase C: wire rules into detection and XAI (per chapter, right after B)
This is what actually makes mistakes get flagged and explained.
1. For each new `constraint` with `detector: spec_only`, implement a detector (in `server/ruleset.py` or a new `server/cgel_detectors.py` loaded by the matrix), keyed by the rule ID so findings carry `rule_id`.
2. Each finding must return: `rule_id`, token/char span, the governing relation (both tokens when two are involved), `learner_explanation` from the rule, source pages, and any `variety_scope`.
3. Add `false_positive_guards` as negative tests. A detector is not done until its guards pass.
4. Register enabled rules so the XAI layer (`server/xai4_partial.py` and `explanations.py`) can show them. Use the owner-approval registry for provisional status; add each new rule ID to `grammar/owner_approvals.json` when its tests pass.
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

A range or chapter may not advance unless all pass:
1. JSON validates against `grammar/schema.json`; IDs unique and never renumbered.
2. Every cited printed page falls inside the chapter and is not textless.
3. Every constraint has 2+ correct and 2+ incorrect examples and a `diagnostic` block.
4. Ledger shows no `unprocessed` pages for the chapter (or lists exact skipped pages with reasons).
5. `server` test suite passes; new detectors pass their false-positive guards.
6. `python scripts/audit_xai_pre.py --require-contracts` still passes (the source audit file must not be edited to claim review that did not happen).
7. Each extracted rule is checked against its own source page text for the stated exception list (agent self-check, recorded in the chapter report).

---

## 9. Required reporting (honest coverage)

Each chapter report and a root `COVERAGE.md` must state: pages processed / total, rules added, detectors implemented / spec-only, error families caught per the corpus, known gaps. Never write "complete" for a chapter whose ledger has gaps.

---

## 10. Agent prompt (paste this)

```
Read docs/planning/CAMBRIDGE_FULL_COVERAGE_MASTER_PLAN.md and
CAMBRIDGE_EXTRACTION_PROMPT.md. The master plan overrides the stop-and-wait
rules: work autonomously with no approval stops. Do Phase A once, then for each
chapter in priority order run Phase B, then Phase C and D for that chapter,
then commit. Attached PDF: Chapter <N>, printed start page <X>. Process every
page. Update the ledger and COVERAGE.md. Run the gates in section 8 and fix
failures. Report only what you actually ran and measured.
```
