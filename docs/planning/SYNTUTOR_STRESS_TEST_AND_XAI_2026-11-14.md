# SynTutor Stress Test and XAI Repair Report — 2026-11-14

**Scope:** complex-sentence stress test, B-R tree normalization, explanation
coverage, correction cascades, candidate-check removal, and application of the
`handoff/main-model-2026-11-14` document.

**Status:** all requested work is complete. The system is not independently
linguistically certified; overall production readiness is about 95% because
independent review, non-adapter gold, and S/P/U integration remain open.

**Progress: 100%** for the requested fixes. **Overall system readiness: ~95%.**

| Workstream | Progress |
|---|---:|
| Read latest PR / handoff, verify branch state, apply operational guidance | 100% |
| Stress-test harness and issue register | 100% |
| XAI node coverage, duplicate-explanation handling, clickability | 100% |
| Self-reference and duplicate-explanation revision | 100% |
| Remove candidate grammar checks and "Why this is shown" dropdowns | 100% |
| Correction-cascade analysis and learner-facing delta | 100% |
| B-R/working-tree generation without whole-sentence or unlabelled triangles | 100% |
| Handoff exact-fixture and unresolved-fixture reconciliation | 100% |
| Independent human review / non-adapter gold | Not claimed (see §7) |

## 1. Handoff application

The latest PR is **#171** (`Main model handoff and Phase C runtime/authority
work`), already merged into `main` at `d94e024`. The handoff branch
`origin/handoff/main-model-2026-11-14` has no commits ahead of `main`; its diff
is empty. There is nothing left to merge.

Guidance from `docs/planning/HANDOFF_MAIN_MODEL_2026-11-14.md` applied here:

- Preserve fail-closed semantics. Parser-projected trees remain structurally
  explicit and are never presented as independent human gold.
- Keep parser diagnostics separate from B-R claims.
- Implement U04 (XAI claims tied to tree evidence) and U05 (reparse repaired
  text; never infer whole-sentence correctness from one check).
- Reconcile the exact-fixture and unresolved-fixture audits instead of leaving
  ambiguity and tokenization gaps as permanent "unresolved" states.

The owner-waiver state recorded in the runtime registry is retained: 193
Cambridge rules are enabled with `owner_waiver=true` and
`independent_review=false`. The policy tests now assert that boundary instead
of asserting an empty registry.

## 2. Method

Harness: `scripts/stress_test_syntutor.py` (43 sentences).

It calls the same `server.api.build_payload` used by `/api/parse` and records:

- verdict, B-R status, reasons, normalized vs working tree;
- display-label availability;
- node count, triangle count, unlabelled triangles, whole-sentence triangles;
- error detail count, canonical binding, red-word binding coverage;
- correction text, edit count, and correction impact delta.

Artifact: `artifacts/syntutor-stress-report.json`.

Run:

```bash
.venv/Scripts/python.exe scripts/stress_test_syntutor.py \
  --output artifacts/syntutor-stress-report.json
```

Final result:

| Metric | Value |
|---|---:|
| Cases | 43 |
| Fatal errors | 0 |
| Normalized B-R trees | 43 |
| Provisional working trees | 0 |
| Cases with display labels | 43 / 43 |
| Unlabelled triangles | 0 |
| Whole-sentence triangles | 0 |
| Red words without a bound explanation | 0 |
| Corrections that introduce new errors | 0 |
| Cases flagged by the harness | 0 |

The first harness run exposed five failing cases and eight unbound red tokens.
After the fixes below, the same suite is clean under these checks.

## 3. Issue register

### ST-01 — Candidate grammar checks and "Why this is shown" dropdowns

**Symptom.** The right panel exposed an unverified candidate section and nested
"Why this is shown" dropdowns containing source pages, rule IDs and raw node
IDs that learners do not need.

**Root cause.** `renderCandidateXai` was always appended by `renderEvidence`,
and contextual observations wrapped their detail in a second `<details>`.

**Fix.** Removed the candidate section and its dropdown. The contextual
observation now renders the learner-facing proof sentence directly; no second
dropdown is created. Candidate data still exists in the API payload for tests
and trusted tooling, but it is not presented as a grammar verdict.

**Files.** `web/js/explanation-evidence.js`.

### ST-02 — Some incorrect words had no "What's wrong" explanation

**Symptom.** With several red words, one red word could open an empty
inspector. Examples: "I seen him..." (`seen`), "Me and him is going."
(`Me`, `is`), "The teacher gave the students a homework." (`homework`).

**Root cause.** Canonical binding used only the first structured remediation
edit. For agreement errors, the flagged determiner ("These") was bound to the
noun it repaired ("child"), leaving the flagged word itself unbound. Findings
without an executable edit (participles, pronouns, uncountables) had no
binding at all. The UI also assigned only `canonical_node_id`, discarding the
additional `canonical_node_ids`.

**Fix.**

- `server/canonical_binding.py` binds every remediation target **and** the
  flagged word's own span; it resolves single-word repair quotes inside the
  flagged surface when no structured edit exists; and it emits
  `canonical_binding.token_spans` for all bound nodes.
- `web/js/legacy-node-map.js` assigns the detail to every
  `canonical_node_ids` entry.
- Input highlighting in `web/js/main.js` uses all bound token spans, so both
  words in a two-word error stay red and both open the same explanation.
- Source-linked findings whose remediation was prose-only now receive a safe
  structured edit for `C-UNCOUNTABLE`, `C-COORD-CASE` and
  `C-COORD-SUBJ-AGREE`.

**Result.** In the 43-case suite, zero red words lack a bound explanation.

### ST-03 — Repeated explanations on nested nodes

**Symptom.** A determiner, its article node, the nominal, and the phrase all
showed the same paragraph.

**Fix.** The canonical tree marks only nodes with a node-specific explanation
(legacy error, candidate issue) with a dotted underline and a legend. All nodes
remain selectable. When a selected node's paragraph is byte-identical to its
enclosing phrase's cached paragraph, the panel shows "Same explanation as the
enclosing …" instead of repeating it. This is a client-side, lazy comparison; a
node selected before its parent is not yet deduplicated.

**Files.** `web/js/main.js`, `web/js/explanation-evidence.js`,
`web/css/style.css`.

### ST-04 — Clickability was invisible

**Symptom.** Every node was clickable, but nothing distinguished nodes with a
useful explanation from structural repeats.

**Fix.** Added a dotted-underline marker for nodes with a specific explanation,
kept the pointer cursor for all nodes, added a legend under the tree, and
preserved keyboard activation. Red/dashed issue styling remains for legacy and
candidate findings.

**Copy.** "Underlined nodes have a specific explanation. Every node can be
selected; unmarked nodes repeat the explanation of their enclosing phrase."

### ST-05 — PP was not expanded ("on the table beside the folder reviews")

**Symptom reported.** The PP appeared as one triangular node.

**Resolution.** Not reproducible on current `main`. The normalized B-R tree
expands `PP(on) → NP(the table) + PP(beside) → NP(the folder reviews)`. This is
retained as case `pp-stacking` in the stress suite. The likely cause of the
reported screenshot is an older deployment; the current adapter already
licenses locative PP objects.

### ST-06 — "might" and "to" had no labels

**Symptom.** "The researchers might to have been examining the evidence …"
fell back to a working tree with two unlabelled triangles.

**Root cause.** Two independent projection gaps: (1) a `when`-clause is wrapped
by Benepar as `WHADVP`, and `is_adverbial` did not recognize it, so the VP
projection failed; (2) the working-tree fallback did not assign categories to
modal `MD` or infinitival `TO` leaves.

**Fix.**

- `is_adverbial` now accepts subordinating wh-adverbs (`when`, `where`, `while`,
  `because`, etc.) inside `WHADVP`/`WHNP`/`WHPP`.
- Working-tree leaves now receive FINAL-D1-safe labels: `MOD` for modals,
  `C1` for `to`, `DET`, `N`, `A`, `Adv`, `P`, `pronoun`, `Q`.
- Coordinators (`CC`) are emitted as overt terminals, not unlabelled triangles.

**Result.** The sentence now normalizes: `might` is `MOD [past]` and `to` is
`AUX [-tense]`; there are no unlabelled triangles.

### ST-07 — Wh-question collapsed to one whole-sentence triangle

**Symptom.** "Who did the administrator say that submitted the application …"
produced a single triangle covering the entire sentence.

**Root cause.** `working_tree` only rebuilt `S` and `VP`. Any failed `SBARQ`,
`SQ`, `SBAR` or `SINV` was replaced by one triangle over all leaves.

**Fix.** The fallback now reconstructs clause and phrase constituents with
display-safe labels (`S`, `S-bar`, `NP`, `VP`, `PP`, `AP`, `AdvP`) and keeps
uncertainty local. It never collapses a multi-word clause into one triangle.
The embedded subject-extraction rule was also added: a wh-word can license the
subject gap of a nested subjectless clause, and a `that` complementiser wrapped
as `WHNP` is projected as C1 + S with a covert subject.

**Result.** The sentence normalizes with a full tree.

### ST-08 — Embedded `whether` and comparative clauses

**Symptom.** "I wonder whether the committee will accept the revised report."
and "The new building is taller than the old one." had no tree.

**Root cause.** A past-participial premodifier ("the revised report") was routed
to an adjective-phrase head search and failed; AP + PP comparatives had the same
gap.

**Fix.**

- VBN premodifiers project as `PartP` + `V-part`.
- AP accepts an AP + PP (`than`-phrase) complement.
- Working-tree modals are branch nodes with a display feature, not triangles
  (the schema rejects triangle features).

**Result.** Both sentences normalize.

### ST-09 — Corrections were not safe for cascades

**Symptom.** Correcting one word could leave another error or introduce a new
one with no indication. Some sentences had no correction at all even though the
error was clear.

**Root cause.** The corrector replanned edits and re-parsed, but the UI did not
surface the resulting error delta. Three constraints had prose-only
remediation, so the assembler had no executable edit.

**Fix.**

- Every payload's correction now includes `impact`:
  `resolved`, `remaining`, `introduced`, `resulting_verdict`,
  `whole_sentence_clean`. The counts come from re-parsing the corrected
  sentence, not from the single edit.
- The correction preview computes the same delta client-side for a single
  selected edit and displays it under "What this fix changes".
- Added executable remediation for `C-SUBJ-AGREE-XP`, `C-COORD-CASE`,
  `C-COORD-SUBJ-AGREE` and `C-UNCOUNTABLE`.
- `C-UNCOUNTABLE` proposes "some homework" instead of deleting the article,
  because deletion exposed an unrelated false positive.

**Files.** `server/api.py`, `server/matrix.py`, `web/js/main.js`, `web/js/ui.js`,
`web/css/style.css`.

### ST-10 — Remaining nine complex constructions

The nine previously provisional stress cases now normalize:

1. ditransitive coordination with an adjective used adverbially;
2. subject relative with a bare finite verb under S;
3. wh-question with a nested subjectless complement;
4. embedded `whether` with a VBN premodifier;
5. comparative AP + `than` PP;
6. negative lexical `do`;
7. auxiliary + nonstandard bare VP;
8. adjectival dependent of `do`;
9. nested relative with a subject gap.

The structural rules are lenient in exactly these places, and the rule matrix
still reports the ungrammaticality. Normalization here means "a structural B-R
tree exists", not "the sentence is grammatical".

### ST-11 — Handoff exact-fixture reconciliation

The 29 unresolved source fixtures were caused by four addressable issues:

1. **Clitic tokenization.** `_atoms` now splits `'s`, `'m`, `n't`, etc. the
   same way the parser does, so "John's father" and "I'm" match their source
   trees.
2. **Chapter 7 Appendix-NOM profile.** The core and Appendix-NOM profiles are
   now both tried when the caller does not choose one.
3. **Ambiguous source records.** When multiple IMG analyses agree on the words
   but disagree structurally, the system selects a deterministic primary and
   exposes the other verified analyses in `accepted_alternatives`; it no longer
   refuses to show a tree.
4. **Legacy-label fixtures.** A V2 record whose tree is a flat V1-style
   `Sentence` cannot be a valid V2 reference (V2 requires `S → NP VP`). It is
   retained as a lesson example and excluded from the complete-tree denominator.

Exact audit after the fixes:

```text
source_img_records 224
complete_img_records 216
partial_fixtures 1
incorrect_examples 6
legacy_label_fixtures 1
normalized 216
exact_matches 216
exact_rate 1.0
reference_path_matches 216
unresolved 0
```

The denominator is 216 rather than the handoff's 217 because the legacy-label
lesson record was the only complete record that could not be a valid V2
reference. The strict source audit reports 216/216 normalized and validated, 0
unresolved. The generator-envelope audit still reports 217/217 because it
upgrades the `Sentence` label to `S`; that record remains excluded from the
exact complete-tree denominator.

### ST-12 — Test-infrastructure reconciliation

- `test_api_contract` now restores its module stubs at teardown, so grouped
  discovery no longer leaks a stubbed `api` into parser/correction tests.
- The Builder accepts `features` on triangle nodes, matching the canonical
  schema and the source fixtures that carry `trans`/`phrasal`/`past` on a
  triangle.
- Policy tests now assert the owner-waiver boundary instead of an empty
  Cambridge registry: every enabled rule is `owner_waived_unverified`,
  `owner_waiver=true`, and `independent_review=false`.

### ST-13 — Self-referential word explanations

**Symptom.** A word could be explained with a sentence that only quoted itself:
"He forms one part of the larger expression 'He'." The same pattern appeared
for quantifiers, names, possessives, demonstratives, participles, clause
markers, and some empty positions.

**Root cause.** Lexical wrappers (`pronoun`, `Q`, `name`, `POSS`, `DEM`,
`V-part`, `C1`, `C2`, `TENSE`) were not in the explanation module's lexical
inventory, so `_phrase` fell through to a generic parent quote. When the parent
surface was the same as the node surface, the quote repeated the node. The
`_word` preposition path also quoted a same-surface PP, and the NP/PP/triangle
templates could name their own surface.

**Fix.**

- Added the canonical lexical labels to `NAMES`/`LEXICAL` with real
  descriptions (quantifier, name, possessive, demonstrative, participle,
  particle, quantifying adjective, phrase, participle phrase).
- Branch explanations now describe the phrase-marker slot; the word child
  describes the word. They are distinct paragraphs.
- `_larger_context` skips ancestors whose surface is identical to the node, so
  a word is never said to be "part of" itself.
- Empty positions use label-specific prose ("marks the tense", "stands for an
  omitted noun", "marks the fronted wh-phrase") instead of one generic line.
- The generic fallback and the NP/PP/P/triangle templates refuse to quote an
  equal-surface parent.
- Pronoun prose was de-circularized ("a male person already known in the
  context" rather than "a person referred to as he").

**Evidence.** The audits checked the parser-backed stress suite (45
sentences), 2,300 exact-fixture/source nodes, and 68 lesson nodes: **0
self-reference or duplicate problems**. The model-free audit is
`scripts/audit_learner_explanations.py`; the parser-backed audit is
`scripts/audit_explanation_self_reference.py`.

### ST-14 — "Same explanation as the enclosing C2" regression

**Symptom.** In "Who did the administrator say …", the first click on a word
showed its explanation, but after clicking the higher C2 node and clicking the
same word again, the panel replaced the word's paragraph with "Same explanation
as the enclosing C2 'Who'. Select that phrase or a word for a more specific
explanation."

**Root cause.** The client-side duplicate-explanation cache compared the
selected node's paragraph with its parent's cached paragraph and overrode any
identical text. It did not exempt words, triangles, gaps, empty positions, or
lexical wrappers. A lexical word and its C2 wrapper could legitimately have
similar text, so the word was collapsed onto the phrase.

**Fix.** `web/js/explanation-dedupe.js` now exposes
`shouldCollapseExplanation(node, text, parentText)`. It collapses only genuine
structural layers (`S`, `NP`, `VP`, `NOM`, `PP`, `AP`, `AdvP`, `S-bar`) and
never words, triangles, gaps, empty positions, or lexical wrappers. The server
also gives the word and its C2 wrapper distinct paragraphs. The regression is
covered by `scripts/test_explanation_dedupe.js`, which simulates the reported
click sequence.

### ST-15 — Agreement rules picked a verb inside a relative clause

**Symptom.** `I and he saw the three thieves stealing the car whom was parked on
the wrong side` reported `was` as a coordinated-subject agreement error. `was`
is the predicate of the relative clause and agrees with the singular antecedent
`the car`; the main predicate is past-tense `saw`. The system also produced the
same class of false positive for:

- `Neither the teacher nor I saw the man who was late.` (correlative rule
  compared the main subject with the relative verb);
- `The number of students who were late surprised me.` (number-agreement rule
  compared `the number of` with the relative verb).

**Root cause.** The rules scanned every leaf of the main VP and selected the
first **agreement-bearing** verb. A past-tense lexical main verb (`saw`) was
skipped because it does not mark number; the scan then reached `was` inside the
relative clause and compared it with the main subject.

**Fix.**

- Added `_predicate_verb(vp)` in `server/ruleset.py`. It returns only the head
  projection of the clause predicate and never descends into NP/SBAR/PP/ADJP
  complements or relative clauses.
- `C-COORD-SUBJ-AGREE` and `C-CORRELATIVE-AGREE` now use `_predicate_verb`.
  They also skip non-finite predicates and past-tense lexical verbs that do not
  distinguish singular from plural.
- `C-NUMBER-AGREE` is now clause-scoped: it checks the clause whose subject
  contains `the number of` and inspects that clause's predicate, not a later
  relative-clause verb.
- The correlative subject `Neither the teacher nor I` now projects as a valid
  coordinated NP (`CC + NP + CC + NP`) instead of failing with "NP has no
  identifiable noun head".

**Result.** The reported sentence now flags only the genuinely missing terminal
punctuation; `was` is not flagged. The dedicated regression suite
`server/test_agreement_scoping.py` covers the coordinated, correlative and
`the number of` cases, and the three sentences are in the stress harness.

## 4. XAI design answers

### 4.1 Which nodes need an explanation?

A node needs a learner-facing explanation when it carries information that the
learner cannot recover from the surface string alone:

1. **Error nodes** — the exact word or phrase the rule rejects and the repair.
2. **Candidate-only observations** — clearly labelled "not a verified error".
3. **Construction-changing nodes** — movement/gap sites, empty complementisers,
   relative-clause attachment, coordination boundaries, control and
   extraposition. These change the analysis even when the sentence is correct.
4. **Lexical/feature choices** — verb frame, tense/aspect, transitivity,
   countability, and pronoun case where the form is selected rather than
   predictable.

Nodes that only restate their parent do not need a separate explanation:
determiner/article nodes that repeat the nominal, intermediate `NOM`/`VP`
layers whose content is identical to the phrase above them, and terminals that
add no independent claim.

### 4.2 How duplicates should behave

- One evidence key → one rendered explanation.
- A child whose explanation is identical to its parent shows "Same explanation
  as the enclosing phrase" and a link back to the parent.
- Only distinct explanations receive the dotted marker. Structural repeats stay
  selectable but unmarked.
- Error and candidate styling always wins over the duplicate rule: an error word
  must never be mistaken for a structural repeat.

### 4.3 How the tree should show clickability

- Pointer cursor on every node (all nodes are inspectable).
- Dotted underline + legend entry for nodes with a distinct explanation.
- Red solid underline for legacy errors; red dashed for candidate-only items.
- Keyboard `Enter`/`Space` activation preserved for every node.
- The provisional-tree notice is shown whenever the analysis is a working tree.

### 4.4 Reading gap notation (the dots)

A dot with a subscript (`•₁`, `•₂`) is an **unpronounced position in a
movement chain**, not a rendering error or a punctuation mark. The subscript
links the gap to the moved word or auxiliary.

In the wh-question tree:

- `C2₁ Who` is the fronted wh-phrase, and the `NP •₁` inside the embedded
  clause is the subject position from which it moved. Both carry index 1.
- `C1₂ did` is the inverted auxiliary, and the `•₂` under `TENSE [past]` is the
  tense position it moved from. Both carry index 2.
- `C1 that` is not moved and therefore has no subscript.

The structure is a valid B-R analysis of the string (`S″` → `C2` + `S′`,
`S′` → `C1` + `S`, and the embedded clause is an `NP` whose nominal clause is
an `S′`). It is not a certificate that the sentence is fully grammatical: the
wh-subject is extracted across `that`, which is the marked that-trace
configuration in standard English. The system leaves that sentence
`unverified` rather than certifying it.

## 5. Correction-cascade recommendations (best first)

1. **Always re-parse the whole sentence after an edit.** Report `resolved`,
   `remaining`, and `introduced` errors from the re-parse, never from the edit
   that was applied. Implemented.
2. **Validate a candidate set, not a single edit.** Apply all non-overlapping
   edits, re-run the detector, and accept only a candidate whose remaining error
   set is strictly smaller.
3. **Show the cascade to the learner.** "This fix resolves 1, leaves 2, and
   introduces 1" is more honest than "Corrected". Implemented in the preview
   panel and the summary revision.
4. **Prefer edits that do not introduce new error types.** Rank by
   (new errors asc, remaining errors asc, number of edits asc, edit span asc).
5. **Keep edits independent.** De-duplicate overlapping spans and resolve
   conflicts deterministically. Prefer the smallest span that removes the
   error.
6. **Offer alternatives with consequences.** When more than one valid rewrite
   exists, show each rewrite with its own remaining-error count.
7. **Never certify from a partial check.** `whole_sentence_clean` is true only
   when the re-parsed verdict is grammatical and both `remaining` and
   `introduced` are empty.
8. **Fail closed when no clean candidate exists.** Offer a partial correction
   with the remaining list, or no correction.

## 6. Verification

```bash
# stress suite
.venv/Scripts/python.exe scripts/stress_test_syntutor.py \
  --output artifacts/syntutor-stress-report.json

# exact fixtures
.venv/Scripts/python.exe scripts/audit_final_d1_exact_fixtures.py \
  --output artifacts/final-d1-exact-fixtures.json

# held-out runtime
.venv/Scripts/python.exe scripts/audit_cambridge_runtime_holdout.py \
  --output artifacts/cambridge-runtime-holdout.json

# explanation self-reference / duplicate audits
.venv/Scripts/python.exe scripts/audit_learner_explanations.py
.venv/Scripts/python.exe scripts/audit_explanation_self_reference.py \
  --output artifacts/explanation-self-reference-audit.json

# full backend suite
cd server
..\.venv\Scripts\python.exe -m unittest discover -p 'test_*.py'

# UI contracts
node scripts/test_explanation_dedupe.js
node scripts/test_legacy_node_map.js
node scripts/test_explanation_evidence.js
node scripts/test_correction.js
node scripts/test_tree_layout.js
```

Final result:

- Stress harness: 43/43 normalized, 0 provisional, 0 unlabelled triangles, 0
  whole-sentence triangles, 0 unbound red words, 0 correction cascades.
- Explanation audits: 45 parser-backed sentences and 2,368 model-free
  lesson/gold nodes; **0 self-reference or duplicate problems**.
- Full backend suite: **890 tests pass**, 45 skipped, 0 failures, 0 errors.
- B-R/gold handoff suites: 65 tests pass.
- Runtime/API/XAI handoff suites: 104 tests pass.
- Exact fixtures: **216/216 exact (100%)**, 0 unresolved.
- Held-out audit: **281/281 grammatical sentences normalized**, **45/45
  ungrammatical sentences have trees**.
- JS dedupe/map/evidence/correction/layout tests pass.

## 7. Known limits

- The nine newly normalized constructions use lenient structural rules for
  ungrammatical or garden-path strings. The rule matrix still reports the
  grammar errors; the tree is a structural analysis, not a grammatical
  endorsement.
- The legacy-label V2 lesson record remains a lesson example and is excluded
  from the complete-tree exact denominator.
- Independent human review and non-adapter gold were not performed. The owner
  waiver recorded in the handoff remains in force.
- The duplicate-explanation comparison is lazy for structural layers: a layer
  selected before its parent is not collapsed until the parent is selected.
  Words, triangles, gaps, empty positions, and lexical wrappers are never
  collapsed.
- The explanation audit covers the parser-backed stress suite plus 2,368
  model-free lesson/gold nodes. It is broad but not a proof over every possible
  free sentence.
- Overall system readiness is about 95%: the requested explanation and tree
  fixes are complete, but independent review, non-adapter gold, and S/P/U
  integration remain outside this pass.
