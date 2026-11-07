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
- [ ] Define CoLA's advisory role and prevent it from inventing rule explanations.
- [x] Implement a shared normalized analysis payload.
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

- [x] Preserve original sentence, token spans, and edit operation.
- [x] Generate corrected sentence and corrected tree independently from original input.
- [x] Align original tokens to corrected tokens.
- [x] Support replacement, insertion, deletion, and multi-token edits.
- [ ] Display original incorrect word with strikethrough.
- [ ] Display corrected word directly beneath/adjacent to the original.
- [x] Ensure only corrected word appears as the actual tree leaf.
- [x] Preserve full corrected sentence and punctuation.
- [ ] Make original/corrected views reversible.
- [ ] Add accessible text alternatives for correction annotations.
- [x] Test token alignment when punctuation, contractions, and token counts change.

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
| 0. Governance and inventory | AI + project owner | Milestone 01 inventory/ADR complete; exact editions and Cambridge coverage remain documented follow-ups | 7 Nov 2026 | Complete for M1 scope |
| 1. Linguistic architecture | Project owner approved | ADR-0001, source-authority matrix, B-R/Cambridge crosswalk, Benepar compatibility plan, canonical schema and migration map | 7 Nov 2026 | Approved (Milestone 01 complete) |
| 2. Syntax Generator | AI | CI run 42277343237: 35 tests, 11 B-R validators; 210/211 fixtures normalize | 7 Nov 2026 | In progress — not signed off |
| 3. Explanation engine |  |  |  | Not started |
| 4. Lessons |  |  |  | Not started |
| 5. Quizzes |  |  |  | Not started |
| 6. Syntax Builder |  |  |  | Not started |
| 7. Gamification/leaderboard |  |  |  | Not started |
| 8. UI/UX and release |  |  |  | Not started |


## Milestone 02 implementation note — 7 November 2026

The checkboxes above reflect only the verified sub-tasks. **Milestone 02 as a whole
is not complete and must remain unchecked in the 12-Prompt Execution Plan.**
General Benepar-to-B-R normalization beyond exact verified source references and
the narrow V2 top-level mapping is outstanding; the Cambridge registry currently
enables no rules and is not a sentence-level evaluator; parser-backed spaCy/Benepar
end-to-end tests and multi-sentence runtime checks remain outstanding; the frontend
still renders the legacy raw candidate tree.

Verification evidence:
- GitHub Actions: https://github.com/ybcole/SynTutor/actions/runs/42277343237
- 35 Python tests passed.
- All 11 B-R validators passed.
- 210/211 sentence-aligned IMG source records normalized and validated; ch2-2 is
  explicitly unresolved due to its Sentence root/V2 convention conflict.
- Legacy licensing regression: 19/19 bad examples detected and 16/16 good controls
  not rejected; correction regression passed.
