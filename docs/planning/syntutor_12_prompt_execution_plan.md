# SynTutor — 12-Prompt Execution Plan

**Purpose:** This document is the authoritative implementation roadmap for completing the SynTutor master plan. It defines the order, scope, dependencies, approval gates, and completion criteria for the 12 implementation milestones.

**Repository:** `https://github.com/ybcole/SynTutor/tree/main`

**Related project documents:**
- `master_plan.md` — complete product, linguistic, technical, and UX plan.
- `master_checklist.md` — detailed task checklist and acceptance criteria.
- `master_prompt_*.md` — detailed instructions for individual areas.
- `syntutor_initial_ai_prompt.md` — initial instructions to the AI implementing this roadmap.

---

## Mandatory completion and reporting rules

1. **Never mark a milestone complete merely because code was written, a pull request was opened, or an implementation was attempted.**
2. Mark milestone `N` as `[x]` **if and only if** every applicable acceptance criterion for milestone `N` has been implemented and verified with relevant tests or other concrete evidence.
3. If any required criterion is incomplete, unverified, blocked, or only partially implemented, leave that milestone as `[ ]`. Do not use `[x]` to mean “mostly done.”
4. A milestone may be marked `[x]` only after the AI reports:
   - what changed;
   - which acceptance criteria were verified;
   - the exact tests/checks run and their results;
   - any known limitations that do not invalidate completion.
5. If a test cannot be run, explain why and leave the milestone unchecked unless the master plan explicitly allows an alternative verification method and that alternative is completed.
6. Do not mark a later milestone complete when a required dependency remains incomplete. A milestone may be started only when its listed dependencies and approval gates are satisfied.
7. Keep this file and `master_checklist.md` synchronized. Update both after each milestone. Never silently change an acceptance criterion; propose the change and obtain approval first.
8. Record partial work, blockers, deferred scope, and follow-up tasks in a clearly labelled section. Do not hide them by checking the milestone.
9. Preserve the existing application until the replacement behavior is verified. Avoid destructive rewrites and remove old implementations only after their replacements pass the relevant regression tests.
10. Use small, reviewable commits where repository write access permits. Do not claim a commit, push, deployment, or test run that did not actually occur.

## Milestone tracker

Current acceptance: [8 November M1–M3 report](../reports/milestones-01-03-acceptance-2026-11-08.md). Earlier dated continuation entries below are historical. M4 launch implementation is now complete; see the [M4 acceptance report](../reports/milestone-04-acceptance-2026-11-08.md), including the unapplied account-cloud migration follow-up. Earlier dated findings remain historical.

- [x] **01 — Architecture, repository audit, and source governance**
- [x] **02 — Syntax Generator and B-R tree normalization**
- [x] **03 — Shared, source-grounded explanation engine**
- [x] **04 — Lessons and curriculum**
- [x] **05 — Independent quiz system and question bank** — scoped launch verified; see [M5 acceptance](../reports/milestone-05-acceptance-2026-11-08.md); hosted migrations pending.
- [ ] **06 — Syntax Builder integration**
- [ ] **07 — XP, levels, and progression rules**
- [ ] **08 — Achievements and mastery milestones**
- [ ] **09 — Leaderboard and player privacy**
- [ ] **10 — UI/UX, tree layout, and correction presentation**
- [ ] **11 — Cross-feature integration and migration**
- [ ] **12 — Full validation, regression testing, and release readiness**

---

## 01 — Architecture, repository audit, and source governance

**Purpose:** Establish an agreed technical and linguistic foundation before changing application behavior.

**Use these prompts:**
- `master_prompt_thoughts.md`
- `master_prompt_concerns_matters_to_be_addressed.md`
- This execution plan and `master_plan.md`

**Primary materials:** `CONVENTIONS.md`, `MASTER_PROMPT.md`, `CAMBRIDGE_EXTRACTION_PROMPT.md`, `grammar/schema.json`, `grammar/concepts.json`, `grammar/rules/`, `sources/cambridge/`, `web/content/book/`, `docs/ARCHITECTURE.md`, current backend and frontend files, and the existing tests/validators.

**Scope:**
- Audit the repository and identify the active runtime paths, obsolete paths, data sources, existing tests, and migration risks.
- Reconcile the existing B-R-only governance language with the intended combined use of B-R and Cambridge.
- Define the authority boundary: B-R governs the target syntactic representation and chapter progression; Cambridge supplies broader grammatical descriptions, classifications, constraints, conditions, exceptions, and explanatory evidence where applicable.
- Establish source/edition/page citation requirements and distinguish extraction approval, independent review, human sign-off, and runtime eligibility.
- Define a source crosswalk without forcing false equivalence between B-R and Cambridge terminology.
- Decide how Benepar is retained as a candidate parser and how a normalization/validation layer will handle incompatible analyses and unresolved cases.
- Propose the canonical B-R tree schema, data lifecycle, API boundaries, and migration sequence.
- Identify unresolved linguistic questions and decisions requiring the project owner's approval.

**Acceptance criteria:**
- A repository inventory identifies the real active code paths and important data dependencies.
- An architecture decision record (ADR) documents parser, canonical tree, explanation, lesson, quiz, and data-governance decisions.
- A source-authority matrix explains what each source may and may not determine.
- A B-R/Cambridge crosswalk records verified mappings, non-equivalences, and unresolved mappings.
- A Benepar compatibility plan explicitly covers normalization, rejection, alternative analyses, and unresolved output.
- A canonical tree-schema proposal and migration map are documented.
- Critical uncertainties, missing source evidence, security risks, and approval decisions are listed.
- No implementation code is changed during this milestone unless the project owner explicitly approves a narrowly scoped exception.

**Approval gate:** Stop after presenting the deliverables. Obtain approval of the architecture and source-governance decisions before Milestone 02.

---

## 02 — Syntax Generator and B-R tree normalization

**Purpose:** Make the Syntax Generator produce, validate, and correct trees according to the approved B-R representation rather than exposing raw Benepar conventions as canonical output.

**Use this prompt:** `master_prompt_syntax_generator.md`.

**Dependencies:** Milestone 01 approved; canonical schema and parser-normalization design agreed.

**Scope:**
- Implement the approved B-R canonical tree model and normalization/validation layer.
- Keep raw parser output available for diagnostics where useful, but do not present it as the authoritative B-R tree.
- Map only analyses that can be mapped with defensible evidence; return an unresolved state or supported alternatives when they cannot.
- Respect chapter-specific B-R conventions and the approved free-analysis profile.
- Preserve token alignment and correction metadata for substitutions, insertions, deletions, punctuation, contractions, and multi-token corrections.
- Add regression fixtures based on existing B-R tree data and validators.

**Acceptance criteria:**
- Generator output conforms to the approved canonical schema.
- Normalization decisions are traceable and invalid or unsupported mappings are not silently relabelled.
- Known B-R gold examples pass the relevant structural validation tests.
- Unresolved and alternative analyses are handled explicitly.
- API contracts and error states are documented and tested.
- Existing generator behavior that is still required remains covered by regression tests.

**Milestone 02 continuation — 7 November 2026**

**Status: INCOMPLETE — keep `[ ]`.** The root `master_prompt_syntax_generator.md` was retrieved and reconciled. Implementation remains isolated on `feature/milestone-02-completion-2026-11-07`, draft PR [#30](https://github.com/ybcole/SynTutor/pull/30), targeting `main`.

**Implementation added after the previous M2 report**
- The live Generator now calls `build_canonical_analysis` and returns the M1-approved envelope from `docs/canonical-burton-roberts-tree.schema.json` in `br_analysis.tree`. `grammar/br_tree.schema.json` is now identified as a deprecated internal projection schema, not the public API contract.
- Exact sentence- and convention-matched IMG B-R gold records are projected through the read-only importer. Conflicting records, invalid imports, validator exceptions, and unsupported parser analyses remain explicitly unresolved. Chapter 7 core/Appendix D1 records are separated.
- The non-reference Benepar mapping remains V2 `S → NP VP` with NP/VP triangles. Sentence punctuation remains in the sentence and raw parser diagnostic but is not fabricated as a phrase-marker leaf.
- Chapter/profile selection, Chapter 7 Appendix D1, strict integer sentence-index validation, out-of-range rejection, corrected-sentence profile propagation, and optional Cambridge variety selection are routed through Flask, stdlib and hosted APIs.
- A fail-closed Cambridge execution service consumes only allow-listed rules. It supports a typed sentence-scope token-pattern primitive with occurrence-specific exceptions; blocks non-constraint types and unsupported scopes; requires explicit crosswalk/runtime-check eligibility; and requires an explicit matching selected variety for variety-restricted rules. The repository allow-list still enables zero rules because the 196 extracted Cambridge mappings remain unverified.
- Added API-level M1 schema tests, an IMG corpus audit through the API normalizer, Cambridge evaluator/registry/schema tests (including M1-envelope, malformed-registry, exception-occurrence, scope and variety paths), parser and normalizer exception tests, Flask/stdlib model-failure and JSON transport tests, and parser-backed single-/multi-sentence/corrected-sentence tests.
- The frontend authority notice now reads `br_analysis.status`, but the canvas still renders the raw Benepar candidate as a diagnostic/compatibility tree.
- Added `.github/workflows/syntax-generator-runtime.yml` to install spaCy/Benepar models and run live parser/API tests. The model-free workflow now compiles all server code/test files and includes the new tests.

**Verification state — implementation head e51c89c85e17ee8151419ab7739cf1ce03774c5e; PR documentation head 59d0aebaaf8e2b9915541c120c5469d85c7dd0c3**

The latest attempt on the PR documentation head [42351010687](https://github.com/ybcole/SynTutor/actions/runs/42351010687), and the latest attempt on the implementation head [42350898513](https://github.com/ybcole/SynTutor/actions/runs/42350898513), were both push events. Both are attributed to an empty `BuildFailed` workflow registration (workflow ID `410117115`), concluded `startup_failure`, and created zero jobs. The prior push attempt [42350764338](https://github.com/ybcole/SynTutor/actions/runs/42350764338) showed the same signature. No test steps or parser model installation ran. The previous green [run #35](https://github.com/ybcole/SynTutor/actions/runs/42346333169) predates the current API M1-envelope integration and Cambridge evaluator; it is historical baseline evidence only.

A local checkout also failed because DNS could not resolve `github.com`. The repository workflow files are present and include both model-free and parser-backed test jobs. The current startup failures occur before job creation, so they are not test failures and cannot be fixed by changing Syntax Generator tests. The run metadata and the same publicly reported `BuildFailed` signature are recorded in `docs/SYNTUTOR_MILESTONE_02_STATUS.md`; the repository owner must ask GitHub Support to inspect/reindex workflow registration `410117115`.

**Remaining limitations**
1. General candidate restructuring for arbitrary V3–V10 Benepar analyses remains unsupported. The implemented design uses exact eligible B-R source records and the narrow V2 shell; other shapes return unresolved rather than being falsely relabelled. This is a deliberate safe limit, but representative supported transformations beyond V2 still need to be established if required for the Generator's target scope.
2. The Cambridge evaluator primitive and its synthetic contract tests exist, but no actual Cambridge grammar rule is eligible or enabled. Rule-specific positive/negative/exception tests cannot be claimed until source review, crosswalk, deterministic implementation, and allow-list gates pass.
3. The frontend continues to render the raw candidate, clearly labelled diagnostic-only; it does not yet render the M1 B-R envelope as its primary interactive tree. Full UI redesign and Builder migration remain outside this prompt's stop condition.
4. Exact B-R/Cambridge edition and printed-page metadata still require the original source PDFs.
5. Current-head compilation/test workflows have not executed due GitHub Actions startup failures. The previous green run cannot certify current code.

No lesson, quiz, Builder, database or learner-progress migration was performed. Milestone 03 has not been started. Automatic approval does not waive the execution plan's requirement for current, passing evidence; Milestone 02 remains unchecked until the current model-free and parser-backed workflows complete and the acceptance report is verified.
---

## 03 — Shared, source-grounded explanation engine

**Purpose:** Give the Syntax Generator and Syntax Builder one consistent explanation system backed by approved B-R and Cambridge source records.

**Use this prompt:** Start from `master_prompt_others.md` and the explanation requirements in `master_plan.md`; create a narrowly scoped implementation prompt from those requirements if needed.

**Dependencies:** Milestone 01 approved; canonical schema from Milestone 01 and stable tree output from Milestone 02.

**Scope:**
- Separate structural explanations (B-R), broader grammatical explanations (Cambridge), and learner remediation/feedback.
- Build a reusable explanation service used by both Generator and Builder.
- Ground explanations in approved concept/rule/source IDs, page references, and sentence-specific analysis facts.
- Use controlled templates or reviewed content records for learner-facing explanations; do not permit unrestricted runtime model invention from whole-book context.
- Support concise default explanations and optional deeper explanations.
- Provide explicit “not enough evidence” or “analysis unresolved” states instead of fabricating a rule.

**Acceptance criteria:**
- Generator and Builder call the same explanation service and render materially consistent explanations for the same analysis.
- Each substantive grammatical claim can be traced to an approved source record.
- Explanations distinguish B-R tree conventions from Cambridge grammatical claims.
- Sentence-specific explanations accurately reference the relevant node, function, feature, or rule.
- Unverified, conflicting, or missing source records are not presented as settled facts.
- Tests cover correct explanations, missing sources, conflicting sources, and unresolved parses.

**Approval gate:** Review sample explanations across both interfaces before expanding lesson and assessment content around them.

---

## 04 — Lessons and curriculum

**Purpose:** Replace or revise the current hard-coded lessons with a coherent, source-grounded learning path.

**Use this prompt:** `master_prompt_lessons.md`.

**Dependencies:** Milestone 01 approved; Milestones 02 and 03 sufficiently stable for lesson trees and explanations.

**Scope:**
- Use B-R as the structural curriculum spine and chapter progression.
- Integrate selected Cambridge insights where they clarify grammatical distinctions, classifications, constraints, conditions, and exceptions.
- Avoid turning the core course into a full Cambridge reference-book reproduction; reserve advanced/optional material for appropriate modules.
- Design a consistent sequence: brief engagement or diagnostic question, learning objective, concise explanation, worked B-R example, relevant Cambridge insight, guided practice, transfer/application activity, and exit check.
- Retain lessons as instruction and guided practice; do not collapse the curriculum into quizzes.
- Version lesson content and preserve source metadata.

**Acceptance criteria:**
- Every published lesson has explicit learning outcomes, prerequisites, worked examples, practice, and an exit check.
- Lesson analyses follow the approved B-R conventions for their stage.
- Cambridge content is selected, accurately paraphrased, and cited; it does not silently override B-R tree conventions.
- No unsupported or unreviewed extraction is exposed as authoritative instructional content.
- Lesson progression, completion state, and content version are represented consistently.
- Lesson content is tested for navigation, rendering, answer feedback, and progress persistence.

**Approval gate:** Review representative early, middle, and advanced lessons before migrating the entire curriculum.

---

## 05 — Independent quiz system and question bank

**Purpose:** Create a genuine assessment system separate from lesson scaffolding and practice.

**Use this prompt:** `master_prompt_quizzes.md`.

**Dependencies:** Milestone 01 approved; content/explanation conventions from Milestone 03; lesson outcomes and curriculum map from Milestone 04.

**Scope:**
- Separate lesson practice from standalone quizzes and assessment records.
- Create original questions mapped to learning outcomes, B-R conventions, and approved Cambridge rules/concepts.
- Treat book-derived answer trees and exercise metadata as source material, not as a ready-to-publish question bank. Do not reproduce copyrighted exercise wording.
- Support appropriate question types, answer feedback, difficulty, randomization, and equivalent question variants.
- Keep scoring and completion independent from lesson completion.
- Version question content and define how attempts and best scores are stored.

**Acceptance criteria:**
- Quizzes can be taken independently of lesson completion where the progression design allows it.
- Every question has a correct answer, explanation, difficulty, outcome/concept mapping, source metadata, and version.
- Questions are original and do not reproduce copyrighted textbook exercise wording.
- Assessment state is not accidentally recorded as lesson completion or vice versa.
- Scoring, retries, randomization, and persistence have automated tests.
- Quiz results identify strengths and remediation targets without falsely claiming mastery from one attempt.

**Approval gate:** Review a sample question set and scoring behavior before bulk question-bank authoring.

---

## 06 — Syntax Builder integration

**Purpose:** Bring the Syntax Builder into alignment with the canonical B-R tree model and shared explanation service.

**Use this prompt:** `master_prompt_syntax_builder.md`.

**Dependencies:** Milestone 02 canonical tree implementation and Milestone 03 shared explanation engine.

**Scope:**
- Make the Builder create and edit the same canonical tree structures used by the Generator.
- Reuse the shared explanation service so Generator and Builder do not diverge.
- Validate tree-building actions and feedback against chapter-specific B-R conventions.
- Support accepted alternatives and clear unresolved/unsupported states.
- Preserve learner work, undo/redo or equivalent editing behavior, and accessible interaction patterns.

**Acceptance criteria:**
- Builder output serializes to the same canonical schema as Generator output.
- The same tree receives consistent structural and grammatical explanations in both interfaces.
- Validation feedback is accurate, source-grounded, and does not enforce unapproved conventions.
- Core editing, saving, loading, and recovery paths pass tests.
- Existing Builder functionality that remains in scope is not regressed.

**Approval gate:** Demonstrate matching Generator and Builder treatment of a shared set of benchmark sentences.

---

## 07 — XP, levels, and progression rules

**Purpose:** Implement a fair, understandable, and abuse-resistant progression system.

**Use this prompt:** `master_prompt_others.md`, together with the gamification decisions in `master_plan.md`.

**Dependencies:** Lesson and quiz completion/version semantics from Milestones 04 and 05; player data and security architecture approved in Milestone 01.

**Scope:**
- Implement the planned XP sources: lesson completion and quiz performance.
- Use the agreed quiz formula for a five-item quiz: `max(0, 10 - 2 × incorrect_answers)`, unless the project owner approves a different interpretation before implementation.
- Award lesson completion XP once per lesson version, and prevent repeated attempts from minting unlimited XP.
- Define level thresholds, progression display, and reward cadence. Simulate candidate curves before choosing one; avoid an unexplained or excessively steep curve.
- Make award events idempotent and authoritative on a trusted server-side function/RPC or equivalent protected path.
- Record an auditable activity/award ledger and handle retries, replay, and concurrency.

**Acceptance criteria:**
- XP values and level thresholds match the approved product rules.
- Repeated requests, retries, or replayed events cannot duplicate awards.
- Client-side manipulation cannot directly grant arbitrary XP.
- Lesson and quiz awards are correctly distinguished and version-aware.
- XP totals and level values reconcile with the award ledger.
- Tests cover perfect, partial, zero-score, repeated, concurrent, and invalid award events.

**Approval gate:** Approve the XP formula, level curve, and reward policy before production activation.

---

## 08 — Achievements and mastery milestones

**Purpose:** Reward learning progress and mastery across both lessons and quizzes.

**Use this prompt:** `master_prompt_achievements.md`.

**Dependencies:** Reliable lesson/quiz progress and award semantics from Milestones 04, 05, and 07.

**Scope:**
- Support achievements for first steps, lesson/chapter completion, quiz participation, accuracy, consistency, and concept mastery.
- Include meaningful progress-based achievements, not only perfect-score awards.
- Avoid awarding achievements from duplicated or untrusted events.
- Provide clear unlock criteria, progress state, timestamps, and user-facing descriptions.

**Acceptance criteria:**
- Achievement definitions have deterministic, documented unlock conditions.
- Lesson and quiz achievements are independently supported where appropriate.
- Duplicate events do not duplicate unlocks or corrupt progress.
- Achievement state persists and renders accurately.
- Tests cover unlock, partial progress, retries, and invalid events.

**Approval gate:** Review the achievement set for educational value and exploit resistance before release.

---

## 09 — Leaderboard and player privacy

**Purpose:** Deliver a working leaderboard without exposing unnecessary identity information or trusting client-supplied scores.

**Use this prompt:** `master_prompt_leaderboard.md`.

**Dependencies:** Secure XP/level authority and privacy design from Milestone 07; player identity and consent decisions from Milestone 01.

**Scope:**
- Implement an opt-in or otherwise clearly consented leaderboard.
- Use user-chosen display names or pseudonyms rather than exposing raw authentication/provider identifiers.
- Decide and implement lifetime and/or time-bounded rankings as approved.
- Restrict public data to the minimum needed for ranking.
- Ensure rankings use trusted server-side totals and appropriate database access controls.
- Provide empty, loading, error, and privacy states.

**Acceptance criteria:**
- Leaderboard data is based on authoritative XP/level records.
- Raw authentication IDs and unnecessary personal data are not publicly exposed.
- Consent/visibility preferences are enforced by backend policies, not only hidden in the UI.
- Ranking order and ties are deterministic and tested.
- Unauthorized reads/writes and score manipulation are blocked by tests or documented security verification.

**Approval gate:** Review privacy behavior and database access policies before enabling public rankings.

---

## 10 — UI/UX, tree layout, and correction presentation

**Purpose:** Improve visual clarity and interaction consistency without compromising linguistic information or accessibility.

**Use this prompt:** `master_prompt_ui_ux_design.md`.

**Dependencies:** The relevant data contracts and interaction behaviors from Milestones 02–09 must be stable for the screens being revised.

**Scope:**
- Tighten syntax-tree spacing moderately and responsively, accounting for tree width, depth, zoom, and mobile layouts.
- Preserve readable labels, branch relationships, node hit areas, and accessibility.
- On syntax-tree correction, show the full corrected sentence and clearly display incorrect words with strikethrough and the corrected word below or adjacent, as designed.
- Keep the actual tree aligned to the corrected sentence and preserve insertion/deletion/punctuation behavior.
- Improve navigation and visual consistency across Generator, Builder, Lessons, Quizzes, Achievements, and Leaderboard.

**Acceptance criteria:**
- Tree layout remains readable on representative shallow, deep, and wide trees and on supported screen sizes.
- Node labels and connectors do not overlap or become inaccessible.
- Correction display correctly handles substitutions, insertions, deletions, punctuation, contractions, and multi-token corrections.
- The displayed corrected sentence matches the tree's token sequence.
- Major interfaces have consistent loading, empty, error, success, and responsive states.
- Accessibility and interaction regression checks pass.

**Approval gate:** Review screenshots or live UI demonstrations for representative desktop and mobile cases.

---

## 11 — Cross-feature integration and migration

**Purpose:** Ensure the individual systems operate as one coherent application and safely transition existing user/content data.

**Use these prompts:** Relevant sections from `master_prompt_others.md`, `master_prompt_concerns_matters_to_be_addressed.md`, and `master_plan.md`.

**Dependencies:** Milestones 02–10 sufficiently complete for the features being integrated; any unresolved blockers documented.

**Scope:**
- Wire shared contracts and services across Generator, Builder, Lessons, Quizzes, XP, Achievements, and Leaderboard.
- Remove duplicate or conflicting logic only after replacement behavior is verified.
- Implement database migrations and safe compatibility or backfill paths for existing user progress where appropriate.
- Define content/schema version compatibility and behavior for stale attempts or old lesson/question versions.
- Validate authentication, authorization, privacy, error handling, observability, and application navigation end to end.
- Update documentation, environment configuration, and operational instructions.

**Acceptance criteria:**
- End-to-end user journeys work across all implemented features.
- Shared tree, explanation, content, and progress contracts are consistent.
- Migrations are tested against representative existing data and have a documented recovery/rollback plan.
- Old behavior is removed only when no longer referenced and replacement tests pass.
- No critical integration, authentication, authorization, or data-consistency defects remain open.
- Architecture and user/developer documentation reflect the actual implementation.

**Approval gate:** Review the integrated application and migration results before final acceptance testing.

---

## 12 — Full validation, regression testing, and release readiness

**Purpose:** Verify that the completed SynTutor system is linguistically defensible, technically stable, secure, and usable.

**Use these prompts:** `master_prompt_concerns_matters_to_be_addressed.md` and the relevant acceptance criteria in `master_plan.md` and `master_checklist.md`.

**Dependencies:** Milestone 11 integration complete; all critical fixes from prior milestones resolved.

**Scope:**
- Run the full automated test suite, validators, schema checks, and build/lint checks available in the repository.
- Run B-R benchmark/gold-tree validation and Cambridge source/rule validation.
- Test explanation provenance and consistency between Generator and Builder.
- Test lesson and quiz progression, XP integrity, achievements, leaderboard privacy, and migration behavior.
- Perform responsive UI and accessibility checks.
- Review security controls, database policies, secrets/configuration handling, and abuse cases.
- Document known limitations, unsupported constructions, and release/rollback steps.

**Acceptance criteria:**
- All required automated tests and validators pass, or any approved exception is documented with evidence and owner approval.
- No known critical or high-severity defect remains unresolved.
- Linguistic benchmark results and known parser limitations are documented; unsupported cases fail safely.
- User-facing claims and explanations are traceable to approved source material.
- Security, privacy, and XP integrity checks pass.
- Release instructions, migration/rollback instructions, and final documentation are complete.
- The final checklist accurately reflects what was and was not verified.

**Final approval gate:** Present a release-readiness report. Do not claim the project is complete or production-ready until the project owner accepts the evidence and any explicitly required deployment checks have passed.

---

## Standard report required after every milestone

The AI must provide this report before asking to proceed:

1. **Milestone number and title**
2. **Status:** Complete / Incomplete / Blocked (only Complete may be checked `[x]`)
3. **Files inspected**
4. **Files created or changed**
5. **Acceptance criteria:** each criterion marked verified or not verified, with evidence
6. **Tests/checks run:** exact commands or procedures and outcomes
7. **Known limitations and unresolved issues**
8. **Data/schema/API changes and migration implications**
9. **Checklist updates:** identify exactly which boxes were changed and why
10. **Approval needed:** state the specific decision required, or state that the next milestone is unblocked

## Definition of project completion

The 12-prompt plan is complete only when all 12 milestone boxes are `[x]`, every applicable acceptance criterion has evidence, all required approval gates have been satisfied, and the project owner has accepted the final release-readiness report. An unchecked milestone means the work is not yet verified as complete.

---

## Milestone 01 completion record — 7 November 2026

**Status:** Complete. Standing approval from the project owner satisfied the Milestone 01 approval gate. No implementation code was changed.

### Files inspected

- `CONVENTIONS.md`, `MASTER_PROMPT.md`, `CAMBRIDGE_EXTRACTION_PROMPT.md`
- `grammar/schema.json`, `grammar/concepts.json`, all seven `grammar/rules/*.json` files
- `sources/cambridge/chapter_02/` through `chapter_20/` extraction records, reports, conflict and cross-reference files
- `web/content/book/ch01.trees.json` through `ch11.json` and chapter validators
- `docs/ARCHITECTURE.md`, `docs/README.md`, `README.md`, `package.json`, `requirements.txt`
- Active backend, frontend, authentication/progress, and Supabase migration files identified in `docs/repository-inventory.md`

### Deliverables added on this branch

- `docs/repository-inventory.md`
- `docs/source-authority-matrix.md`
- `docs/burton-roberts-cambridge-crosswalk.md`
- `docs/benepar-compatibility-plan.md`
- `docs/canonical-burton-roberts-tree-schema.md`
- `docs/canonical-burton-roberts-tree.schema.json`
- `docs/ADR-001-architecture-and-source-governance.md`
- `master_checklist.md` (synchronized copy of the owner-supplied checklist)
- `syntutor_12_prompt_execution_plan.md` (synchronized copy of the owner-supplied authoritative roadmap)

### Acceptance criteria

1. Repository inventory identifies active code paths and important dependencies — **Verified**, documented in `docs/repository-inventory.md`.
2. ADR covers parser, canonical tree, explanation, lesson, quiz, and data-governance decisions — **Verified**, `docs/ADR-001-architecture-and-source-governance.md`.
3. Source-authority matrix defines what each source/system may and may not determine — **Verified**, `docs/source-authority-matrix.md`.
4. Crosswalk records the status of verified, non-equivalent and unresolved relationships — **Verified as an evidence-status inventory**. No B-R/Cambridge mapping or non-equivalence could be independently verified because the B-R source PDFs were not present. The crosswalk records all 196 active Cambridge rule mappings as `unverified`, enumerates candidate tension areas, and identifies the evidence needed to resolve them. It does not misrepresent candidates as proven non-equivalences.
5. Benepar compatibility plan covers normalization, rejection, alternatives and unresolved output — **Verified**, `docs/benepar-compatibility-plan.md`.
6. Canonical tree-schema proposal and migration map documented — **Verified**, Markdown proposal and JSON Schema at the paths listed above.
7. Critical uncertainties, source gaps, security risks and approval decisions listed — **Verified**, ADR, crosswalk, inventory and checklist.
8. No implementation code changed — **Verified by branch comparison**; only documentation/governance files were added or updated.

### Checks and results

- GitHub recursive repository tree inspection — **Completed**, `truncated: false`.
- Source-data inventory — **Completed**: 252 B-R tree records across Chapters 1–10; 10 corresponding chapter validators; Chapter 11 text record; 273 Cambridge concepts; 196 merged Cambridge rule records; 33 uncertain-item records across 22 raw extraction files; 7 conflict records.
- Cambridge mapping status inspection — **Completed**: 196/196 active rule records have B-R mapping relation `unverified`.
- Branch comparison against `main` — **Documentation-only changes**; no application code or database migration changed.
- Repository clone/test execution — **Not run**. A local clone attempt failed because this execution environment could not resolve `github.com`. Milestone 01 is an architecture/governance documentation milestone and did not modify runtime code. No application test is claimed as passed.

### Known limitations and outstanding matters

- Exact B-R edition and source-page image basis still require confirmation against the underlying book/source PDFs.
- Exact Cambridge bibliographic edition/year/ISBN still requires confirmation.
- All current Cambridge-to-B-R rule mappings remain unverified; three Chapter 2 conflict entries remain unresolved.
- Independent second-pass review of the Cambridge extractions remains outstanding as stated by the extraction reports.
- The runtime rule registry, canonical adapter and validator are design deliverables only; implementation belongs to later milestones.
- Live Supabase/Clerk configuration and production database policies were not accessed or tested.

### Data/schema/API and migration impact

No application API, runtime schema, database table, migration, or user data was changed. The canonical B-R schema is a documented proposal for Milestone 02. Existing `POST /api/parse` behavior is to remain compatible during later implementation.

### Checklist synchronization

The matching checklist records verified inventory and architecture tasks, while leaving exact edition confirmation, live-data rollback approval and the executable runtime registry unchecked where not yet evidenced.

### Approval

The project owner granted standing automatic approval for all milestone gates. Milestone 01 is therefore unblocked for Milestone 02 under the documented dependencies.

---

## Milestone 02 progress record — 7 November 2026

**Status:** In progress; do not mark Milestone 02 complete. The implementation covers a conservative subset of the approved scope and is awaiting the approval gate.

**Execution branch:** `feature/milestone-02-syntax-generator-2026-11-07` (based on the Milestone 01 branch).

### Prompt availability

The execution plan names `master_prompt_syntax_generator.md`. During this run, the connected repository tool returned 404 for that exact path on the default branch, Milestone 01 branch, and the newly created feature branch; repository search did not return the file. The code work recorded here therefore follows the Milestone 02 scope and acceptance criteria in this execution plan, but has **not** been checked against the contents of that detailed prompt. Reconcile it against that prompt before approval.

### Files inspected

- `CONVENTIONS.md` and the approved Milestone 01 architecture, compatibility plan, and canonical schema.
- `server/parse_engine.py`, `server/api.py`, `server/webapp.py`, and `server/app.py`.
- `server/corrections.py` and the existing correction metadata contract.
- Chapter tree records and selected validators, including actual Chapter 7, Chapter 9, and Chapter 10 records.
- `web/js/main.js`, `web/js/renderer.js`, and existing payload/rendering call sites.
- The Milestone 02 section of this plan and `master_checklist.md`.

### Files created or changed

- `server/burton_roberts.py`: canonical envelope construction, convention profiles, conservative live Benepar projection, read-only gold-record importer, correction alignment, and structural validator.
- `server/test_burton_roberts.py`: focused unit/regression suite (16 tests).
- `server/api.py`: adds a separate `canonical_analysis` response while retaining the existing raw `tree` for compatibility and marking its diagnostic authority in metadata.
- `server/webapp.py` and `server/app.py`: accepts and validates optional chapter and Appendix D1 profile selection.
- `docs/canonical-burton-roberts-tree.schema.json` and `docs/canonical-burton-roberts-tree-schema.md`: support the indexed triangles present in Chapter 10 fixtures.
- `docs/syntax-generator-api.md`: API contract, status meanings, current coverage, and outstanding integration work.

No database migration or live data change was made. No frontend renderer replacement was made.

### Acceptance evidence

1. Canonical model/validator exists — **Partially verified**. A v1.0.0 envelope and manual structural validator are implemented; complete linguistic validation across every chapter convention is not.
2. Traceable decisions/no silent relabelling — **Verified for the implemented scope**. Live projection records transformation IDs/reasons and leaves unsupported or ambiguous output unresolved.
3. Known B-R gold examples and validators — **Partially verified**. Focused source-shaped fixtures cover Ch7 core, Ch9 movement, Ch10 gaps/features/controllers, and alternatives. The complete set of 252 tree records and all 10 chapter validators have not been run through an integrated import.
4. Unresolved and accepted alternatives — **Verified for the implemented scope**. Unmappable alternatives are retained in partial-tree notes and make the import unresolved; alternative trees are validated.
5. API contract and errors — **Partially verified**. Both transports accept profile controls and the contract is documented; HTTP transport tests and end-to-end contract tests remain outstanding.
6. Existing generator behavior — **Not yet verified**. The legacy `tree` response is kept unchanged, but the full old regression corpus and browser flows were not executed.

### Tests and checks

- `python -m py_compile server/burton_roberts.py` — **PASS**.
- `python -m unittest server.test_burton_roberts -v` — **PASS**, 16 tests.
- Verified that the exact Git blob SHAs for `server/burton_roberts.py` and `server/test_burton_roberts.py` match the locally tested files.
- Confirmed the JSON Schema remains valid JSON and includes optional `index` on triangle nodes.
- Full repository test scripts, parser/model-backed API calls, browser tests, and whole-repository build were **not run**. The environment could not establish a repository clone because DNS resolution for `github.com` failed; the NLP model/runtime environment was not available for an integrated parse run.

### Important limitations

- The live Benepar adapter currently promotes only a narrow V2 `S → NP VP` shell with unanalyzed NP/VP triangles, no punctuation mapping, and exact token alignment. Other profiles—including default FINAL-D1—return unresolved rather than receiving guessed Penn-to-B-R relabelling.
- Even the supported parser-derived tree carries `source.evidence_status = NEEDS_REVIEW`; the B-R source PDF and exact edition remain unconfirmed.
- The existing frontend still renders the legacy Benepar `payload.tree`; it is labelled in response metadata as a diagnostic candidate. Canonical renderer adoption and learner-facing state handling are not complete.
- Chapter-specific source metadata without typed schema fields is retained in notes. Empty source nodes and movement descriptions lacking stable node references remain unresolved or descriptive; no node identifiers are fabricated.
- The detailed `master_prompt_syntax_generator.md` was not visible through the repository connector during execution and still requires reconciliation.
- No Cambridge evaluator, lesson, quiz, builder, XP, leaderboard, auth, or database implementation was included in this milestone.

### Checklist synchronization

Only individually evidenced items are checked in `master_checklist.md`. Milestone 02 itself remains unchecked because the full acceptance criteria and approval gate are not yet met.

### Approval gate

**Not ready for sign-off.** Review representative normalized V2 output, unresolved FINAL/unsupported constructions, gold import results, test evidence, prompt reconciliation, and remaining integration/source-evidence gaps before using canonical output downstream.


---

## Milestone 02 hardening continuation — 7 November 2026

**Branch:** `feature/milestone-02-syntax-generator-hardening-2026-11-07` (based on `feature/milestone-02-syntax-generator-2026-11-07`).

Additional work:
- Fixed node-level source-metadata loss in the gold-record importer. Diagram references are represented as `source_refs`; source-only symbols, multiword markers, verb-type labels, and other untyped metadata are preserved in node notes as JSON-valued source metadata.
- Explicitly leaves a zero-word `E` elision marker unresolved because the current canonical schema has no matching node type. It is not conflated with a gap or a lexical elided terminal.
- Tightened exact profile/refinement validation, chapter-introduction checks for triangle labels, feature-container validation, and token-span integer validation.
- Added seven focused tests for these cases and a read-only full-corpus audit script: `python scripts/audit_burton_roberts_import.py --expected-count 252`.
- Updated the API/schema documentation with the importer's preservation and unresolved-state behavior.
- Added a visible canvas notice that distinguishes the rendered Benepar diagnostic graph from the canonical B-R response; lesson-authored trees clear this notice. This is not canonical renderer adoption.

**Verification and limitations:** The new test suite and 252-record audit runner have not been run in this environment because a local repository clone was blocked by DNS resolution failure for `github.com`. The 16 focused tests previously recorded as passing belong to the parent branch and have not been rerun against this continuation. The detailed `master_prompt_syntax_generator.md` still was not visible at the expected path or in the accessible branch trees checked during this execution; the work follows the execution plan's Milestone 02 scope, without claiming detailed-prompt compliance. The exact B-R edition/PDF and parser/model-backed E2E path remain unverified. The live frontend now visibly labels the displayed Benepar tree as diagnostic-only, but it still renders that diagnostic tree rather than the canonical projection.

**Milestone 02 remains unchecked.** The approval gate is not met; do not rely on the canonical output downstream until the detailed prompt is reconciled and the focused tests, corpus audit, transport contract tests, frontend integration, and source-evidence review are completed.


## M2–M3 remediation continuation — 7 November 2026

Implementation defects and branch/layout conflicts have been repaired. See
`docs/reports/milestones-02-03-remediation.md` for fresh model-free, real-parser,
HTTP and browser results. The shared explanation service is now integrated in
Generator and Builder. Exact source editions, independent review/crosswalk
resolution, reviewed production templates and supported source coverage remain
open. **M2 and M3 stay unchecked; source-backed M4 publication is not certified.**
No prior checkbox or acceptance criterion was weakened.


## Cambridge starter review — 8 November 2026

See `docs/reports/cambridge-source-review-2026-11-08.md` for the source manifest,
Cambridge 2002 bibliographic evidence, and independent review of the existing
CLS-001 teaching paraphrase. Generator and Builder can now render one real
cited Cambridge classification note. Original B-R mappings, production
constraints, and M2/M3 milestone boxes remain unchanged.

## Milestones 02–03 acceptance — 8 November 2026

The [current acceptance report](../reports/milestones-01-03-acceptance-2026-11-08.md) maps every applicable M2/M3 criterion to implementation and executed evidence. Source edition checks, scoped independent template review, schema 1.1.0 source-preservation changes, real parser/browser tests and fail-closed source gates resolve the earlier blockers. Both milestones are checked for their existing conservative supported/unresolved scope. No criterion was rewritten. Human sign-off is not inferred from AI review; the owner's recorded standing approval applies. M4 lesson/curriculum work can begin, with each new content record still requiring its source and publication review.

## Milestone 04 acceptance — 8 November 2026

The [M4 report](../reports/milestone-04-acceptance-2026-11-08.md) maps all six existing criteria to the 12-lesson launch course and executed schema/source/tree, stage/answer, PostgreSQL and real browser evidence. Representative early/middle/advanced content and desktop/mobile screens were reviewed under the owner's standing authorization; no human instructor sign-off is claimed. The active legacy lesson module is archived and its learner records remain unchanged. The two additive Supabase migrations are prepared/tested but not applied to production: device-local progress works, while account cloud sync/shared XP requires that deployment step. M4 is checked for this explicit implementation scope; neither a live database rollout nor exhaustive textbook coverage is claimed.
