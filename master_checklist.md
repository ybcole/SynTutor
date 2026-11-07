# SynTutor Master Checklist

Use this as the project sign-off register. Mark a box only when there is evidence (a test result, approved record, reviewed screen, migration, or documented decision). “Code exists” is not sufficient evidence of completion.

## 0. Governance and inventory

- [ ] Confirm exact Noel Burton-Roberts book title, edition, and page numbering represented by the supplied source PDFs.
- [ ] Confirm exact Cambridge edition and the bibliographic metadata used in the extraction files.
- [x] Inventory all B-R chapter JSONs, tree validators, evidence flags, exercise-answer fields, book flags, fragments, and unresolved items.
- [ ] Inventory every Cambridge extraction, merged rule, concept, conflict, cross-reference, and uncertain item.
- [ ] Record which Cambridge sections have been extracted and which remain unprocessed.
- [x] Record the independent-review state separately from human approval.
- [x] Inventory the legacy rule matrix, parser labels, lesson claims, quiz examples, and old progress rows.
- [ ] Approve a migration and rollback strategy before changing live user data.

## 1. Linguistic architecture and source crosswalk

- [x] Approve a canonical B-R tree JSON schema.
- [ ] Approve a convention-profile registry for V1–V10 and the declared final profile.
- [x] Confirm the rule for using chapter-specific convention versions in chapter lessons.
- [x] Define how functions are derived from structural positions rather than encoded as invented nodes.
- [x] Define how gaps, indices, triangles, elided elements, movement metadata, and accepted alternatives are represented.
- [x] Build a B-R ↔ Cambridge terminology/analysis crosswalk.
- [x] Resolve mappings currently marked `unverified` or explicitly retain them as unresolved.
- [x] Create a rule runtime registry separate from extraction approval status.
- [x] Define which rule types can trigger errors and which only inform teaching/description.
- [ ] Document how variety, register, exceptions, ambiguity, and low-confidence analysis affect verdicts.
- [ ] Approve copyright handling for stored examples, book answers, and learner-visible content.

## 2. Syntax Generator

- [x] Preserve raw Benepar parse output for diagnostics.
- [x] Build a B-R normalization adapter.
- [ ] Implement safe mappings/restructuring for supported categories and constructions.
- [x] Add explicit unresolved/alternative-analysis outcomes.
- [x] Add B-R tree structural validation.
- [x] Validate word order and token-span alignment.
- [x] Validate feature legality and chapter convention restrictions.
- [x] Validate gaps, indices, triangles, ellipsis, and accepted alternatives.
- [x] Add gold-tree tests using the B-R chapter JSONs.
- [ ] Add Cambridge minimal-pair and constraint tests.
- [x] Add regression tests for the legacy error corpus.
- [x] Define CoLA's advisory role and prevent it from inventing rule explanations.
- [ ] Implement a shared normalized analysis payload.
- [ ] Verify full sentence and multi-sentence handling.
- [ ] Add performance/error/fallback behavior for parser and normalizer failures.

## 3. Explanation engine

- [ ] Define a standard evidence object for a tree node, rule, and sentence-level verdict.
- [ ] Separate structural explanation, grammatical principle, and error diagnosis.
- [ ] Attach B-R/Cambridge printed-page references to every source-derived explanation.
- [ ] Create reusable explanation templates with sentence-specific slots.
- [ ] Establish AI drafting constraints and human approval workflow.
- [ ] Prevent runtime LLM output from deciding grammatical correctness.
- [ ] Add a `NO_BOOK_BASIS`/unresolved path when source evidence is missing.
- [ ] Test explanation parity between Syntax Generator and Syntax Builder.

## 4. Corrected sentence visualization

- [ ] Preserve original sentence, token spans, and edit operation.
- [ ] Generate corrected sentence and corrected tree independently from original input.
- [ ] Align original tokens to corrected tokens.
- [ ] Support replacement, insertion, deletion, and multi-token edits.
- [ ] Display original incorrect word with strikethrough.
- [ ] Display corrected word directly beneath/adjacent to the original.
- [ ] Ensure only corrected word appears as the actual tree leaf.
- [ ] Preserve full corrected sentence and punctuation.
- [ ] Make original/corrected views reversible.
- [ ] Add accessible text alternatives for correction annotations.
- [ ] Test token alignment when punctuation, contractions, and token counts change.

## 5. Lessons

- [ ] Approve B-R Syntax Foundations curriculum map.
- [ ] Approve Cambridge Grammar & Analysis track map.
- [ ] Map all lesson objectives to source sections, concepts, tree IDs, and rule IDs.
- [ ] Define prerequisites and learning outcomes.
- [ ] Define diagnostic question, concept explanation, worked tree, guided practice, transfer task, and exit check fields.
- [ ] Audit each existing hand-authored lesson against source evidence.
- [ ] Rewrite, replace, move, or remove unsupported legacy claims.
- [ ] Keep chapter-specific B-R convention versions visible and enforceable.
- [ ] Select only relevant Cambridge insight cards for core lessons.
- [ ] Build advanced Cambridge modules separately where needed.
- [ ] Add original lesson examples and accepted tree alternatives.
- [ ] Add source references and review status to every lesson.
- [ ] Persist lesson progress by content version.
- [ ] Award 15 XP once per completed lesson version.
- [ ] Add content review and lesson acceptance tests.

## 6. Quizzes

- [ ] Create a standalone quiz bank separate from lesson examples.
- [ ] Define five-item quiz blueprints and difficulty balance.
- [ ] Support MCQ, tree selection, structure identification, rule application, minimal pairs, error diagnosis, and repair.
- [ ] Include B-R convention version where a tree is involved.
- [ ] Include Cambridge concept/rule IDs and exact page references.
- [ ] Exclude unreviewed/unimplemented constraints from graded grammaticality questions.
- [ ] Write original question stems/distractors; do not copy textbook exercise wording.
- [ ] Store correct answer and distractor rationale.
- [ ] Add per-question feedback from the shared explanation engine.
- [ ] Implement `max(0, 10 - 2 × incorrect)` XP for the five-item assessment.
- [ ] Award only the best-score XP delta per assessment version.
- [ ] Ensure repeating a score cannot mint more XP.
- [ ] Persist attempts, best score, last score, answer-level history, and content version.
- [ ] Add quiz review screen and targeted reinforcement.
- [ ] Test XP calculations for 0/5 through 5/5 and repeated attempts.

## 7. Syntax Builder

- [ ] Replace Penn-style palette with B-R convention-aware labels/features.
- [ ] Use chapter-specific conventions for chapter exercises.
- [ ] Use the declared final convention profile for free-form building.
- [ ] Evaluate the learner's constructed tree, not just the sentence's re-parsed tree.
- [ ] Share the same analysis/evaluation endpoint as Syntax Generator.
- [ ] Share explanation components and evidence structure.
- [ ] Distinguish tree well-formedness, sentence grammaticality, and target comparison.
- [ ] Support accepted alternatives.
- [ ] Keep structural graph errors distinct from grammatical constraints.
- [ ] Add progressive hints and model-tree reveal.
- [ ] Add Builder/Generator explanation-parity tests.

## 8. Gamification and leveling

- [ ] Approve 15 XP lesson reward rules.
- [ ] Approve five-item quiz reward formula and best-score policy.
- [ ] Implement idempotent XP transaction/event ledger.
- [ ] Move authoritative award calculation to trusted server/RPC.
- [ ] Add transaction key per user/activity/content version.
- [ ] Implement proposed `levelSpan(L) = 100 + 20 × L` as a pilot curve (or document a revised curve).
- [ ] Simulate expected progression using estimated lesson/quiz completion rates.
- [ ] Add level progress and next milestone UI.
- [ ] Define optional level unlocks/cosmetics/challenge tiers.
- [ ] Ensure no essential lesson or explanation is locked behind XP.

## 9. Leaderboard

- [ ] Decide opt-in/opt-out default.
- [ ] Add user-chosen public alias.
- [ ] Remove raw Clerk user IDs from public payloads.
- [ ] Add weekly/seasonal ranking model.
- [ ] Retain personal lifetime XP privately.
- [ ] Secure XP updates through trusted server/RPC validation.
- [ ] Add tie-breaker policy.
- [ ] Test RLS/privacy and unauthorized update attempts.

## 10. Achievements

- [ ] Define lesson, quiz, syntax-skill, consistency, and cross-framework categories.
- [ ] Support OR and AND unlock expressions.
- [ ] Define data-driven achievement schema.
- [ ] Derive achievements from trusted activity events.
- [ ] Make unlocks idempotent.
- [ ] Award achievements for improvement and mastery as well as perfection.
- [ ] Add clear progress indicators and optional rewards.
- [ ] Test all achievement unlock conditions.

## 11. UI/UX and accessibility

- [ ] Approve brand promise, tone, design tokens, and icon language.
- [ ] Prototype revised navigation: Syntax Generator, Lessons, Quizzes, Syntax Builder, Leaderboard, Achievements, History/Profile.
- [ ] Build shared explanation/evidence component.
- [ ] Build shared source citation component.
- [ ] Build correction annotation component.
- [ ] Reduce tree spacing modestly and implement adaptive density.
- [ ] Test deep/wide trees and mobile canvas dimensions.
- [ ] Add keyboard and screen-reader equivalent tree representation.
- [ ] Ensure error/success states are not colour-only.
- [ ] Support reduced motion and touch interactions.
- [ ] Conduct usability sessions with learners not involved in implementation.

## 12. Quality, privacy, release

- [ ] Add schema validators and ID/reference integrity checks.
- [ ] Add unit tests for normalizer, structural validator, and rule evaluator.
- [ ] Add B-R gold-tree regression tests.
- [ ] Add Cambridge rule and exception tests.
- [ ] Add explanation source-reference tests.
- [ ] Add browser E2E tests for the principal flows.
- [ ] Add CI to run validators, tests, and build checks.
- [ ] Add database migration tests and backward-compatible progress migration.
- [ ] Add privacy/security review for leaderboard and XP writes.
- [ ] Add rate limiting and backend error handling appropriate to deployment.
- [ ] Add feature flags and staged rollout.
- [ ] Run old/new pipeline comparison on a fixed evaluation corpus.
- [ ] Approve rollback plan.
- [ ] Publish coverage limitations and known ambiguities to users.

---

## Phase sign-off log

| Phase | Reviewer | Evidence / test run | Date | Status |
|---|---|---|---|---|
| 0. Governance and inventory | Implementation audit | docs/repository-inventory.md; source file inventory | 7 Nov 2026 | In progress — source editions and live-data rollback remain open |
| 1. Linguistic architecture | Implementation audit | ADR-001; source-authority matrix; crosswalk; canonical schema proposal | 7 Nov 2026 | In progress — mappings retained unresolved; executable registry remains future work |
| 2. Syntax Generator | Implementation audit | docs/syntax-generator-api.md; 16 focused unit tests; Milestone 02 progress record in execution plan | 7 Nov 2026 | In progress — conservative V2 only; detailed prompt/integration/source evidence outstanding |
| 3. Explanation engine |  |  |  | Not started |
| 4. Lessons |  |  |  | Not started |
| 5. Quizzes |  |  |  | Not started |
| 6. Syntax Builder |  |  |  | Not started |
| 7. Gamification/leaderboard |  |  |  | Not started |
| 8. UI/UX and release |  |  |  | Not started |

---

## Milestone 01 evidence log — 7 November 2026

**Execution branch:** `architecture/milestone-01-source-governance-2026-11-07`

**Verified and checked above**
- B-R tree/validator/evidence inventory.
- Cambridge extraction/rule/concept/conflict/cross-reference/uncertainty inventory.
- Extracted versus unprocessed section coverage.
- Independent-review state separated from human approval.
- Legacy parser/rule/lesson/quiz/progress inventory.
- Canonical B-R schema proposal and V1–V10 convention profile decisions.
- Structural-function, gap/index/triangle/elision/movement/alternative representation decisions.
- B-R/Cambridge crosswalk produced; all unverified mappings explicitly retained as unresolved.
- Rule-type error eligibility and handling of scope, variety, exceptions, ambiguity and confidence documented.
- Copyright handling documented.

**Still unchecked**
- Exact B-R edition/page numbering: source PDFs were not present in the repository or accessible file library search.
- Exact Cambridge edition metadata: year/ISBN not confirmed in the inspected extraction data.
- Detailed production migration/rollback approval: no live data changed; concrete recovery procedure remains required before any live migration.
- Executable runtime rule registry: lifecycle and decision separation are documented in ADR-001, but runtime implementation is not part of Milestone 01.

**Inventory facts**
- 252 B-R tree records (Chapters 1–10), 10 chapter tree validators, and one Chapter 11 text record.
- 273 Cambridge concepts and 196 merged rules.
- 22 raw Cambridge extraction JSONs in 19 chapter folders (Chapters 2–20).
- 33 uncertain-item records and 7 conflict records.
- 196/196 active Cambridge rule records have B-R mapping relation `unverified`.

**No implementation code changed.** No parser, rule evaluator, lesson, quiz, builder, frontend, backend, or database migration was edited during this milestone.


---

## Milestone 02 progress log — 7 November 2026

**Execution branch:** `feature/milestone-02-syntax-generator-2026-11-07`.

The three boxes marked above are supported by code and focused tests: the API retains the raw Benepar diagnostic tree; the canonical adapter exposes unresolved outcomes and validates/preserves accepted alternatives; the structural validator checks exact overt token coverage and ordering alongside spans. All broader Syntax Generator boxes remain unchecked because the complete chapter/profile implementation, full gold-corpus run, source-backed mapping review, UI adoption, and integration tests are not complete.

**Implemented files:** `server/burton_roberts.py`, `server/test_burton_roberts.py`, `server/api.py`, `server/webapp.py`, `server/app.py`, `docs/syntax-generator-api.md`, and the canonical JSON/Markdown schema updates supporting indexed triangles.

**Verification:** `python -m py_compile server/burton_roberts.py` passed. `python -m unittest server.test_burton_roberts -v` passed (16 tests). Tests cover V2 promotion/fallback, FINAL-D1 unresolved handling, profile validation, corrections (substitution/insertion/deletion/punctuation/contraction/multi-token), selected B-R gold structures, source metadata, gaps, indices, movement, controllers, and alternatives.

**Not yet verified:** full 252-record import/validator run, full legacy tests, parser-model API calls, HTTP contract/E2E tests, frontend renderer adoption, and detailed prompt reconciliation. The repository connector could not retrieve `master_prompt_syntax_generator.md` during this run; this progress entry follows the Milestone 02 section of the execution plan rather than asserting compliance with the missing detailed prompt. The exact B-R source edition/PDF remains unconfirmed.

**Milestone 02 remains unchecked and is not approved for downstream use.**


---

## Milestone 02 hardening log — 7 November 2026

**Continuation branch:** `feature/milestone-02-syntax-generator-hardening-2026-11-07`, based on the existing partial Milestone 02 branch.

**Additional implementation work**
- Canonical gold-tree import now preserves node diagram references in `source_refs` and serializes untyped source-only node fields (including symbols, multiword flags, and verb-type labels) into node notes.
- A source-only zero-word Chapter 5 `E` elision marker remains explicitly unresolved. It is not reclassified as a gap or fabricated as a word-bearing terminal.
- Convention profile identity/refinement combinations are checked; triangle labels are checked against chapter-introduction boundaries; invalid falsey feature containers and boolean token-span coordinates are rejected.
- Added focused regression tests and `scripts/audit_burton_roberts_import.py` for read-only reporting across the 252 chapter records.
- Added a visible Syntax Tutor canvas notice that labels the currently rendered Benepar tree as diagnostic-only and reports canonical normalization status; lesson-authored canvas trees clear the notice.

**Verification state for this continuation**
- The new tests, whole-corpus audit runner, and UI changes were committed but could not be executed in this environment. The repository could not be cloned because DNS resolution for `github.com` failed.
- The 16-test PASS entry above is evidence recorded on the parent Milestone 02 branch, not a fresh run of this continuation branch. The hardening changes therefore remain **unverified at runtime** until the focused suite and audit command are run.
- The detailed `master_prompt_syntax_generator.md` was not found at the expected root path or in the accessible branch trees checked during this run. This continuation follows the Milestone 02 execution-plan scope but does not claim detailed-prompt compliance.
- The B-R edition/PDF, full parser/model runtime, canonical frontend renderer adoption, and end-to-end API integration remain outstanding. The new canvas notice is an authority warning, not canonical rendering.

**Milestone 02 remains unchecked and not approved for downstream use.**


## Milestone 02 continuation log — 7 November 2026

**Branch:** `feature/milestone-02-completion-2026-11-07`  
**Pull request:** [#30](https://github.com/ybcole/SynTutor/pull/30), draft and unmerged  
**Status:** Incomplete; M2 remains `[ ]`.

The Generator now calls the shared B-R normalizer and exposes the M1-approved envelope from `docs/canonical-burton-roberts-tree.schema.json` inside `br_analysis.tree`. Exact IMG sentence/profile matches use the read-only importer. Source conflicts, invalid projections, lookup failures, validator failures and unsupported candidate conversions remain explicitly unresolved. The candidate adapter still supports only the narrow V2 `S → NP VP` shell when no exact source tree matches. Sentence-final punctuation is retained in the sentence/raw candidate, not fabricated as a B-R leaf.

Flask, stdlib and hosted routes forward chapter convention, Chapter 7 Appendix D1, selected Cambridge variety, and strict sentence indexes. Invalid or out-of-range indexes are rejected rather than silently clamped. Corrected sentences are parsed and normalized independently using the same selected B-R profile. The frontend authority notice now reads the actual `br_analysis.status`; the tree canvas itself remains on the raw Benepar diagnostic candidate.

A deterministic Cambridge evaluator and machine-readable runtime-check schema have been added. The evaluator only consumes allow-listed rules, restricts the supported token-pattern primitive to sentence scope, handles exceptions per occurrence, blocks non-constraint categories, and requires an explicit matching variety for variety-restricted rules. The repository registry still enables zero rules: the 196 extracted Cambridge records retain unverified B-R crosswalk mappings and have not passed runtime eligibility. Synthetic evaluator tests do not establish Cambridge grammaticality judgments.

The new model-free suite includes API-level M1 schema tests, an API-normalizer corpus audit over sentence-aligned IMG records, Cambridge evaluator/registry/schema tests, normalizer failure-path tests, missing-model transport tests, and variety routing. The separate parser-backed workflow installs spaCy/Benepar and exercises real parsing. Neither workflow has a current-head successful execution record yet.

**Verification boundary:** GitHub Actions run [#35](https://github.com/ybcole/SynTutor/actions/runs/42346333169) passed on an earlier snapshot (46 isolated tests, 24 importer tests, 252 source-record audit, 11 chapter validators, legacy licensing/corrector regressions and schema checks). It predates the current M1 API-envelope integration, Cambridge evaluator, API-normalizer corpus audit, strict-index/variety changes, frontend notice update and parser-backed workflow. Newer Actions runs, including [42349400228](https://github.com/ybcole/SynTutor/actions/runs/42349400228), have failed at startup with no jobs created; retry was rejected. A local clone was blocked because `github.com` could not be resolved. Do not report the current-head tests as passed.

**Remaining unchecked M2 items:** actual current-head tests and schema audit; parser-backed single-/multi-sentence and corrected parsing; latency and deployed-model fallback; source-approved Cambridge rule execution and rule-specific minimal-pair tests (no rules currently eligible); any further source-backed V3–V10 candidate transformations required by the supported Generator scope; and confirmation of exact source edition/page metadata. The M1 canonical API contract is now wired in code, but its current-head API schema tests remain unexecuted. No M3, lesson, quiz, Builder, database or learner-progress work was performed.

The CoLA advisory-role item remains checked based on the earlier passing contract tests. The shared normalized payload item is unchecked until the current M1-envelope API output and its schema tests execute successfully. Milestone 02 itself remains `[ ]` pending successful current-head tests and the approval report.

## M2 continuation — latest verification state

Implementation head: `e51c89c85e17ee8151419ab7739cf1ce03774c5e` on `feature/milestone-02-completion-2026-11-07` and `milestone-02-syntax-generator`.

The canonical M1 API envelope, source-reference importer, V2 fail-closed candidate mapping, Cambridge evaluator boundary, profile/transport contracts, parser-runtime workflow, and associated tests are present. However, the latest Actions attempt [42350898513](https://github.com/ybcole/SynTutor/actions/runs/42350898513) is a pre-job `startup_failure`: workflow metadata `name=""`, `path="BuildFailed"`, `workflow_id=410117115`, zero jobs. The previous green run #35 is historical and does not cover the current API/evaluator/runtime changes. A local clone was blocked by DNS. No new M2 acceptance checkbox is checked on the basis of unexecuted tests. Milestone 02 remains `[ ]`.

The fail-closed conversion boundary remains deliberate: exact eligible source records and the supported V2 shell can normalize; unsupported V3–V10 candidate forms remain unresolved. The Cambridge allow-list remains empty because 196 extracted rules have unverified B-R mappings and have not cleared independent review/runtime gates. Model-backed parsing, correction reparse, latency, and missing-model behavior still need an actual successful parser workflow run.
