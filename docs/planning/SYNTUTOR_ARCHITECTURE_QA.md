# SynTutor Architecture Q&A

**Purpose:** one place to answer the recurring “what is canonical?”, “which
detector is real?”, “how do two books coexist?” and “what is missing?” questions.

The active migration plan is
[`ARCHITECTURE_AUTHORITY_MIGRATION.md`](ARCHITECTURE_AUTHORITY_MIGRATION.md).
The main-model release gaps are in
[`MAIN_MODEL_GAP_LIST.md`](MAIN_MODEL_GAP_LIST.md).
The machine-readable inventory is
[`authority_inventory.json`](authority_inventory.json).

This document describes the code as implemented, not the intended end state.
The intended end state is in
[`CAMBRIDGE_FULL_COVERAGE_MASTER_PLAN.md`](CAMBRIDGE_FULL_COVERAGE_MASTER_PLAN.md)
and
[`BR_NATIVE_ENGINE_CONSTRUCTION.md`](../BR_NATIVE_ENGINE_CONSTRUCTION.md).

## The short version

- **Burton-Roberts (B-R)** is the structural and syntax-tree authority.
- **Cambridge (CGEL)** is the grammar-constraint, exception and explanation
  authority.
- **Benepar/spaCy** are candidate parser evidence. They are not an authority.
- The **legacy detector** is the deterministic matrix + licensing, plus an
  optional CoLA acceptability classifier. It runs on the Benepar tree.
- **Phase C Cambridge detectors** are candidate-only. The backlog currently has
  **187 primary pilots, 6 supporting pilots, 11 deferred, 0 production-enabled**.
- The **B-R canonical tree** is a book-convention envelope, not a complete
  arbitrary-sentence B-R parser. It is produced by exact gold records, a narrow
  adapter, and a FINAL-D1 projection; unsupported structures stay
  `unresolved`/`working`.
- The app today has **three structural layers**: raw Benepar, B-R canonical, and
  candidate findings mapped onto whichever tree is available. They are not
  merged into one parser.

## 1. Trees and the word “canonical”

### Q1. What does “canonical” mean in `br_analysis`?

It means “represented in the approved B-R envelope and convention profile”, not
“the one true parse” and not “verified grammatical”.

A canonical result can be:

- `normalized` — the B-R envelope passed validation for the declared profile;
- `working` — a provisional B-R-shaped view with triangles for unresolved
  spans;
- `unresolved` — no safe B-R tree was produced.

`normalized` still does not mean the tree was independently verified against
the book or that the sentence is grammatical.

### Q2. Is the canonical tree just Benepar with B-R labels?

No. The adapter refuses to relabel Penn-style categories wholesale. The current
paths are:

1. Exact sentence match to an IMG-verified B-R source record.
2. A narrow V2 lesson shell (`S → NP VP` with internal triangles).
3. The FINAL-D0 construction projection, built from explicit construction
   rules, with triangles and unresolved spans when it cannot complete.
4. A bounded experimental native chart, exposed only as a diagnostic candidate,
   never as the canonical tree.

Unsupported structures return `unresolved`; they do not get silently renamed.

### Q3. If B-R can describe any sentence, why can’t the canonical tree parse any sentence?

Because B-R is a **convention and grammatical framework**, while SynTutor’s
current implementation is a **Benepar-to-B-R adapter/projector**, not a complete
constructive grammar.

The final product decision in
[`ABSOLUTE_SYNTAX_MASTER_LIST.md`](ABSOLUTE_SYNTAX_MASTER_LIST.md) is that
Benepar remains the general English parser and SynTutor translates its proposed
analyses into B-R. Building a second unrestricted native parser is optional
research, not a prerequisite.

What the adapter still needs is construction-specific work:

- an explicit Benepar-to-B-R transformation table for S02–S10 and P01–P09;
- individual dispositions for the 130 catalog instances;
- complete gold trees for the supported constructions;
- one contract across API, Builder, renderer and storage;
- held-out exact-tree evaluation, including ambiguity and unsupported inputs.

When the adapter cannot justify a B-R analysis, the result must remain
`unresolved`/working. A schema-valid tree is not proof of B-R correctness.

### Q4. Does the app combine Benepar and B-R trees?

Yes, but in **separate lanes**:

| Layer | What it is | What uses it |
|---|---|---|
| Benepar/spaCy tree | Raw candidate phrase structure | Legacy matrix, candidate probes, parser fallback, node IDs `n0…` |
| B-R canonical envelope | Book-convention tree, source/profile-specific | Canonical tree view, Builder, lesson/quiz structure, structural XAI |
| Candidate XAI mapping | Finding spans mapped to canonical nodes when available, otherwise Benepar nodes | Candidate explanations and red candidate marks |

The legacy detector does **not** run on the B-R canonical tree. It runs on the
Benepar tree. That is one of the main architectural gaps.

### Q5. Why does the UI sometimes show the B-R tree and sometimes the parser tree?

When canonicalization is normalized/working, the B-R tree is the primary
structural display. When it is unresolved, the raw Benepar diagnostic is hidden
behind an opt-in toggle. The raw parser is retained for compatibility and
debugging, never presented as the B-R authority.

## 2. Detectors and correctors

### Q5b. Why did the summary say “ungrammatical” while the canonical tree showed no red node?

Because the legacy agreement error is stored on the **Benepar** nodes (`n4`,
`n5`), while the displayed canonical tree uses ids such as
`sg-root-1-0-0`. The two id spaces are different, and the canonical renderer
originally knew only about candidate findings.

The UI now bridges them (`web/js/legacy-node-map.js`): legacy remediation edit
positions are mapped to the exact canonical target word, so the canonical node
for “reads” is marked red and the inspector shows a
“Legacy diagnostic — not book-verified” section with the suggested fix. The
detail is not attached to every word in the phrase. When a finding has no
remediation target, the smallest covering canonical node is used instead. This
is a display bridge, not a promotion of the legacy rule into Cambridge.

### Q6. Is there an existing grammar error detector model?

There are two detection channels today:

1. **Deterministic constraint matrix / rulebook / licensing**
   (`server/matrix.py`, `server/ruleset.py`, `server/licensing.py`).
   Hand-written Python over the Benepar tree. It has 112 legacy rules, marks
   nodes, and provides remediation for some findings. It does **not** read
   `grammar/rules/*.json`.
2. **CoLA acceptability classifier** (`server/detector.py`,
   `textattack/roberta-base-CoLA` by default). It is advisory. If the matrix is
   clean and CoLA rejects the sentence, the verdict becomes `unverified`, not
   “ungrammatical”, because the rules cannot explain why.

Cambridge is a third, newer channel. It is not the existing production
detector.

### Q7. Is Cambridge the only grammar error corrector?

No. There are three correction paths:

1. **Matrix remediation** — rule-specific “replace X with Y” findings when the
   matrix knows the repair.
2. **Text-space MLM corrector** (`server/corrector.py`) — used only for
   `unverified` CoLA rejections; masks a token, proposes lemma-compatible
   replacements, batch-classifies them, re-parses and re-runs the matrix.
3. **Phase D Cambridge candidate correction** (`server/cgel_phase_d.py`) —
   applies explicit candidate edits, reparses, reruns candidate probes and
   reports local lineage. It is candidate-only and production-disabled.

### Q8. Which detector is “the truth”?

For the current production verdict: the **legacy matrix plus the optional CoLA
signal**. That verdict is explicitly labelled legacy/diagnostic
(`verdict_authority = legacy_diagnostic`, `book_verified = false`).

Cambridge is not production truth: the independently gated
`grammar/runtime_registry.json` enables **zero** Cambridge rules. Candidate
findings, including the red node marks, are local observations.

### Q9. Why are there so many different detectors?

They answer different questions:

- matrix: “which deterministic structural rule is violated?”;
- CoLA: “does a learned acceptability model reject this?”;
- Cambridge candidate probes: “does a source-grounded pattern apply?”.

They are not yet fused into one calibrated detector. That fusion is missing
work, not an existing feature.

## 3. The two books

### Q10. What does each book control?

| Source | Authority |
|---|---|
| Burton-Roberts, *Analysing Sentences* | Phrase-marker hierarchy, labels, features, triangles, gaps, indices, movement, chapter conventions V1–V10 and FINAL-D1 |
| Cambridge Grammar (CGEL, 2002) | Grammar constraints, exceptions, categories, constructions, variety/register restrictions, descriptive generalisations, grammatical explanations and lesson/quiz content |
| Benepar/spaCy | Candidate tokens, POS, constituency and diagnostic alternatives only |

Cambridge must not dictate the B-R tree shape. B-R must not be used to invent a
Cambridge rule. A crosswalk is supposed to connect them, but almost all of it is
still unverified.

### Q11. How do explanations work when there are two books?

`server/explanations.py` defines separate channels:

- **structural** — B-R conventions and tree facts; structural templates cite
  B-R only;
- **grammatical** — reviewed Cambridge teaching descriptions or server-evaluated
  Cambridge rules; grammar claims cite Cambridge only;
- **remediation** — Cambridge feedback tied to an actual evaluated violation.

Conflicting claims with the same `claim_key` are withheld. Source conflicts
produce `SOURCE_CONFLICT`, not a guess. The node inspector’s structural
paragraph is B-R-based; a Cambridge rule paragraph is a separate grammatical
channel.

Candidate XAI is a special case: it combines the Cambridge rule’s
`learner_explanation` with observed tree context, but marks the result
`CANDIDATE_OBSERVATION_NOT_VERIFIED_ERROR`.

### Q12. Are the B-R ↔ Cambridge mappings verified?

No. The crosswalk document records that all active Cambridge records remain
`unverified`. There are candidate comparison areas and known tensions
(auxiliary-as-head, determinatives, pronoun-as-noun, copular *be*, tense/time,
“object”, preposition scope, relative clauses). None is a verified equivalence
or a licence to overwrite B-R labels.

### Q13. What happens when the books disagree?

They remain separate framework-specific analyses. The explanation contract can
withhold conflicting claims, and the canonical tree remains B-R. Cambridge
cannot silently override it; B-R cannot silently settle a Cambridge constraint.

## 4. XAI explanations

### Q14. What XAI already exists?

- Rule-level `learner_explanation` for the 204 diagnostic specifications.
- Structural node XAI from `xai_facts` + `xai_composer` +
  `learner_explanations`: the short paragraph when a syntax node is clicked.
- XAI-4 partial evaluator for independently approved Cambridge rules.
  All 193 implemented pilot rules (187 primary + 6 supporting) are enabled as
  owner-waived, AI-checked candidate rules. They are not independently
  human-certified; the 11 deferred semantic specifications remain outside
  runtime.
- XAI-5 localization/repair, XAI-6 naturalization and XAI-7 unified assembly.
- Candidate XAI tree mapping (`server/cgel_candidate_xai.py`): maps candidate
  findings to canonical/Benepar nodes and composes short/deep candidate
  paragraphs. This is the **Phase C finding → XAI/tree mapping** layer; the
  selected-sentence repair pipeline is **Phase D**.

### Q15. Is the node-click paragraph a Cambridge explanation?

Usually no. The node-click learner paragraph is **structural**: it describes
the observed B-R node, its function and its local tree context. It is not a
Cambridge grammar verdict.

Candidate XAI adds a separate section that can quote a Cambridge rule
explanation, but it is explicitly candidate-only.

### Q16. Does every candidate finding have a tree explanation?

Every candidate finding with a character span gets a tree binding. The mapping
prefers the canonical B-R fact graph and falls back to the labelled Benepar
tree. Findings without spans are returned as `unmapped` with a reason. The 11
deferred semantic specifications are not included.

## 5. The current state

| Area | Status |
|---|---|
| Source extraction | All 20 chapters accounted for: 1,716 extracted, 0 unprocessed, 46 justified skips, 2 absent from split sources |
| Source QA | Independent linguistic QA and crosswalk review still pending |
| Legacy detector | Active; 112 legacy rules; Benepar-based |
| CoLA | Optional/advisory; can only move a clean matrix to `unverified` |
| Cambridge catalog | 3,914 records; 204 diagnostic specifications |
| Cambridge implementation | 187 primary pilots, 6 supporting, 11 deferred, **0 production-enabled** |
| B-R canonical tree | Exact gold records + Benepar adapter + FINAL-D1 projection; native parser optional |
| B-R ↔ Cambridge crosswalk | Unverified |
| Candidate XAI | Node-mapped, context-aware, red candidate marks, production-disabled |
| Phase D correction | Candidate-only selected-sentence repair; not production |
| Lessons/quizzes | Legacy content works; Cambridge-derived generation/validation still pending |

## 6. What is missing?

### Q17. What prevents SynTutor from becoming what it is intended to be?

The main blockers, in dependency order:

1. **Complete B-R adapter coverage and gold evaluation.** Benepar remains the
   general parser. The current FINAL-D1 adapter has partial construction
   coverage and no exact held-out tree benchmark. This—not a second parser—is the
   main structural blocker. A native parser is optional research.
2. **Production Cambridge licensing.** 187 candidate pilots are not production.
   Each production rule needs independent review, a resolved crosswalk, exact
   exceptions/variety, executable tests, held-out evaluation and an explicit
   runtime registry entry.
3. **One detector authority.** The legacy matrix, CoLA and Cambridge candidates
   are separate channels. There is no calibrated fusion, no shared B-R tree
   basis, and no unified confidence/conflict policy.
4. **Verified two-book crosswalk.** The structural book and the grammar book
   still lack verified mappings. Explanations can be produced in separate
   channels, but production claims need resolved crosswalks.
5. **Production correction.** Phase D is candidate-only; the production MLM
   corrector is a fallback; interacting errors and ambiguity are not fully
   solved.
6. **Evaluation.** Source examples and guards test implementation behaviour, not
   broad held-out detector accuracy. A cross-family corpus and measured
   precision/recall are still needed.
7. **Cambridge-derived lessons/quizzes.** Existing lessons/quizzes are legacy;
   generation from approved Cambridge rule IDs and printed-page references is
   not complete.
8. **UI truthfulness.** Candidate red marks now exist, but the product must keep
   candidate, legacy-diagnostic and independently verified claims clearly
   distinct.

### Q18. What should I expect today if I type a sentence?

- Benepar parses it; the legacy matrix and optional CoLA produce a diagnostic
  verdict.
- The B-R tree appears when the canonical adapter can produce one; otherwise it
  is unresolved/working and the raw parser is opt-in.
- Implemented candidate rules can mark nodes/tokens red and show a candidate
  explanation with a proposed edit.
- Candidate red is **not** an approved error, and no Cambridge rule is
  production-enabled.
- Phase D can return a local corrected sentence through its API, but the normal
  UI does not auto-apply it.

### Q19. What is the shortest correct path forward?

1. Finish the B-R adapter construction table, the 252-record/130-instance
   dispositions, and the gold suites so the canonical tree is a tested
   adaptation, not an unmeasured projection.
2. License one small, high-confidence Cambridge family into production with
   held-out tests and a verified crosswalk slice.
3. Run matrix, Cambridge and XAI on that same canonical tree; keep CoLA as an
   advisory signal only.
4. Produce correction and lesson/quiz content from the same approved rule IDs.
5. Expand family by family, preserving fail-closed behaviour.

## 7. Vocabulary

| Term | Meaning |
|---|---|
| Benepar tree | Raw candidate constituency parse; node ids `n0…` |
| B-R tree | Burton-Roberts convention envelope; `br_analysis.tree` |
| Canonical | B-R-convention-valid envelope for a profile; not a grammaticality verdict |
| Normalized | Canonical envelope passed structural validation |
| Working | Provisional B-R view with unresolved triangles |
| Unresolved | No safe B-R tree; raw parser is diagnostic only |
| Legacy detector | Deterministic matrix/ruleset/licensing + optional CoLA |
| Candidate | Source-linked check that is not production-enabled |
| Production-enabled | Explicitly licensed in `grammar/runtime_registry.json` |
| XAI | Deterministic explanation composed from tree facts or rule evidence |
| Crosswalk | Source-reviewed mapping between B-R and Cambridge concepts |
