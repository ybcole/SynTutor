# SYNTUTOR — MASTER IMPLEMENTATION PROMPT
## Syntax Foundations lesson revision (Burton-Roberts Chapters 1–11)

**Status:** Chapter 1 pilot implemented for Gate 3 review. The first-time learner timing trial and owner acceptance are pending.
**Target branch:** `feat/lessons/revision-plan`, based on `origin/explore/foundations-lesson-rollout-plan` at `7df6b1e6775760b67a445f1cfa995d33b922ca2a`.
**Implementation:** Codex. **Acceptance:** project owner.
**Phase 0 audit:** `docs/planning/syntax_foundations_revision_phase_0.md` on the revision branch.
**Reference date:** 2026-11-13. **Authority:** This document supersedes outdated lesson planning guidance where stated. Existing security, data-integrity and source-evidence requirements apply.

---

# A. Agent operating instructions

You are the implementation agent for SynTutor's revised Syntax Foundations lessons. Deliver a coherent, source-reviewed, tested learning experience, rather than superficial text expansion or isolated UI changes. Work **one phase and one approved chapter at a time**; do not automatically advance past a gate. Confirm the repository, worktree, checked-out branch, clean/dirty state, and actual file inventory first. Do not assume branch files match old documents. Never overwrite unrelated work. Never merge or push to `main` unless the owner explicitly requests it in the current implementation task and the applicable checks and approvals are complete.

At each approved unit of work: (1) inspect existing implementation and source evidence; (2) write a concrete implementation plan; (3) change the minimum necessary files; (4) execute focused and cross-cutting tests; (5) capture a source and test receipt; (6) show the owner the proposed UI/content and behavioral differences; (7) obtain approval before the next phase or chapter. Mark progress `not started`, `in progress`, `blocked`, `verified`, or `owner approved`; never label pending work complete. An AI assertion that a page is correct is not evidence of browser, database, or source verification.

## Confirmed owner decisions (binding)

1. Revise **the entire Lessons area** and **Burton-Roberts 3rd-edition Chapters 1–11**, maintaining the actual book chapter order. Keep **lesson 12 as the separate Cambridge companion**, without revising or incorporating its content in this workstream.
2. Teach **the most important foundational concepts and relationships** from each chapter, while omitting more specialized discussions as necessary for a concise introductory course. The objective is meaningful comprehension, not exhaustive chapter transcription.
3. Target **approximately 5–10 minutes for each entire chapter, including reading and activities**. This is an instructional design target rather than a guarantee. Propose explicit trade-offs where essential topics cannot be taught accurately within the time budget; never silently remove an indispensable concept. Prioritize comprehension over the time estimate when they conflict and request owner approval.
4. Retain the current recognizable Lessons page aesthetics and article-style presentation, chapter navigation, progress bar, resume/reload, XP, versioned progress, and reusable tree/Builder components. Add a **left-hand chapter section/page sidebar**, analogous to an LMS module contents panel. Responsive/mobile presentation is required.
5. Keep the familiar progression **introduction → core concepts → worked example/analysis → application or guided practice → recap → closing check**, but allow variable numbers of concise pages and appropriate activity variation. Avoid a rigid six-page count. Do not create a long scrolling textbook chapter by stacking every possible subsection.
6. Explain terminology and notation clearly before using it. Use an accessible tone for learners with functional English proficiency but little formal syntax knowledge. Each instructional page should teach a relationship with reasoning and an appropriate example, not merely offer dictionary-style definitions.
7. Use a mix of read-only authored tree tracing, word/boundary selection, contrastive analysis, short open responses, and **unscored embedded Builder exercises** wherever pedagogically appropriate. Avoid multiple-choice questions inside the teaching sequence; multiple choice is allowed in the opening and closing checks.
8. Opening check: **at least five questions per chapter**, diagnostic only, show numerical score, **do not show the answer key**, and preserve the first-response synced marker where supported. No XP from this check.
9. Closing check: **at least five questions per chapter** covering taught concepts; display score, post-attempt feedback and the full answers overview. Reattempts are permitted, including after answer review. Only an improved **best verified score** grants additional XP; equal or lower results grant **zero** XP. No parser-generated answer keys.
10. XP: **15 XP maximum per chapter for this newly reset curriculum**, calculated from the best verified closing-check score. For a five-question equal-weight exam, award 3 XP per correct answer (0/3/6/9/12/15 total). A better later attempt awards **only the difference** between the prior cumulative award and the new eligible award. Replays, identical scores, worse scores, duplicate submissions, and concurrent retries never duplicate XP. For more than five questions, use a tested, deterministic integer proportional formula capped at 15. An answer key may be shown after submission; retakes remain eligible for improvement-based XP under the owner's explicit preference. Acknowledge that this allows learners to study or copy reviewed answers; never misrepresent this as an anti-cheating assessment.
11. Every chapter is freely browsable. Do **not** implement a mastery rating, mastery threshold or pass/fail gate. Track **chapter completed: yes/no** as a simple status. A chapter is complete once its required lesson stages have been visited/finished and its closing check has been submitted at least once, **regardless of score**. Prerequisites may inform recommended sequence but must not block navigation or completion. Chapter completion is independent of whether 15 XP has been earned.
12. **Owner-authorized fresh start:** revised Syntax Foundations Chapters 1–11 start with **zero active chapter progress, zero chapter XP, and not completed**, with no carryover of the previous lesson-version's progress or awards. The new curriculum is treated as a new scoring baseline, not as an additional 15-XP opportunity on top of the old version. Legacy lesson state is excluded from the active curriculum and may be archived as code/audit evidence. Since the owner does not require preservation of existing lesson progress, a lesson-specific reset or migration is authorized **in principle**, but the implementer must first inventory actual stored data, scope it strictly to obsolete lesson progress/awards, document rollback, and obtain deployment approval before any destructive database operation. Never wipe accounts, unrelated global XP, M5 standalone quiz data or other application records. If old lesson XP was folded into a shared total, produce a reconciliation plan rather than blindly subtracting or zeroing unrelated XP.
13. Rewrite/restructure chapter teaching material in the third-edition book's pedagogical sequence; reuse existing source-verified content and components when applicable. Examples should be original; a running example may appear across pages in one chapter, but use new transfer examples and avoid repeating the same example across every chapter.
14. Chapter 11 should use useful diagrams, rule applications and active exercises where justified by the chapter's actual source content. Do not force a syntax-tree Builder into a chapter when it would teach the wrong abstraction.
15. Place concise **source/page references and inspired-figure attribution** in the current summary-page References dropdown, backed by internal source IDs/receipts for substantive claims. The UI need not print a citation after every sentence.
16. Require **AI-generated source-verification receipts AND owner chapter-by-chapter acceptance**. Include the commit, files changed, page/figure anchors, verified limitations, tests and concrete learner questions in each handoff.
17. Preserve old lesson source, content and source receipts by Git commit and assessment version. Keep historical seed migrations immutable. Old learner lesson progress need not remain active or queryable after the explicitly scoped reset. Do not present retired unreviewed material as current instructional authority.

## Non-negotiable integrity rules retained from the implementation architecture

- Do not use live Benepar/spaCy parses to determine lesson correctness, answer keys, or canonical tree truth. Authored, validated, source-reviewed lesson analyses are authoritative.
- Do not silently promote Cambridge catalog specifications to B-R notation or active grammar errors; Cambridge companion revision is outside scope.
- Do not invent Burton-Roberts pages, quoted claims, figures, labels, source receipts, schema validation, learner outcomes, or UI test results. Distinguish a source-extracted statement from a proposal.
- Preserve identity isolation, account security, row-level security, server-validated scoring and progress, local/offline behavior, retry, idempotency, and existing unrelated functionality.
- A change to a published graded question or answer key requires a **new content version** and matching reviewed seed. Preserve accepted alternatives and evidence. Do not modify a published answer key in place.
- Keep the existing `guided → transfer → exit` conceptual progression where technically necessary; use the owner-approved binary chapter completion rule, independent of XP. Reuse the approved UI and tests wherever feasible.
- Do not deploy destructive migrations or claim a hosted migration, authenticated end-to-end result, or production deployment without observing it.
- Keep M5 standalone assessments, M6 full free-form Builder, Cambridge source extraction and other active engineering branches separate. Only modify shared interfaces when needed and regression tested.

---

# B. Evidence and source inventory

## Established from the repository materials examined

- `sources/burton_roberts/source_manifest_2026-11-08.json` identifies **Noel Burton-Roberts, _Analysing Sentences: An Introduction to English Syntax_, 3rd ed.**, copyright 2011; ISBN 9781408233740. It records 11 chapter files and page-range hashes. It **does not, by itself, prove every chapter topic or figure has been independently checked**.
- The confirmed chapter labels and **printed page ranges from that manifest** are:

| Chapter | Manifest title / chapter topic | Printed pages |
|---|---|---|
| 1 | Sentence structure — constituents | 6–23 |
| 2 | Sentence structure — functions | 24–45 |
| 3 | Sentence structure — categories | 46–66 |
| 4 | The basic Verb Phrase | 67–86 |
| 5 | Adverbials and other matters | 87–110 |
| 6 | More on verbs — auxiliary VPs | 111–140 |
| 7 | The structure of Noun Phrases | 141–170 |
| 8 | Sentences within sentences | 171–195 |
| 9 | Wh-clauses | 196–223 |
| 10 | Non-finite clauses | 224–253 |
| 11 | Languages, sentences and grammars | 254–268 |

- `docs/planning/syntax_foundations_lesson_structure.md` contains a **previous, selective launch curriculum**; it is a historical baseline and UI/exercise reference, **not authoritative coverage** for this revised curriculum.
- `docs/planning/syntax_foundations_lesson_rollout.md` and `syntax_foundations_lesson_polishing_plan.md` describe previous chapter activities and reusable presentation conventions. Their suggestions are not proof of source coverage.
- `docs/planning/master_prompt_lessons.md` and `docs/reports/milestone-04-acceptance-2026-11-08.md` document the original versioned lesson, reviewed answer, XP and validation contract. The original completion-based **15-XP-once** mechanism is **not compatible by default** with partial incremental XP and must be deliberately redesigned.
- `docs/curriculum/progress-and-deployment.md` describes version-specific storage, an identity-bound protected RPC, a server-owned lesson catalog, unique award events, and idempotent account progress. It also contains different statements about production deployment status; **confirm the live environment independently** rather than assuming either assertion is current.
- `docs/source-authority-matrix.md` defines the authority boundary: B-R is authoritative for canonical syntax lesson structures; parser outputs are candidates, not teaching truth.

## Inspect in the actual target worktree before implementation

- `web/content/lessons/course.json`, its JSON schema, review receipts, generated seed and migrations.
- `web/content/book/chXX.trees.json`, `CONVENTIONS.md`, `sources/burton_roberts/**`, and any book extraction artifacts actually present locally. Check chapter-by-chapter availability and reliability; **the source manifest may reference PDFs not committed to GitHub**. If the source pages/figures are unavailable or ambiguous, flag and request them—do not reverse-engineer a book from the older curriculum map alone.
- `web/js/lessons-ui.js`, `lesson-core.js`, `lesson-progress.js`, chapter presentation modules, `lesson-tree-exercise.js`, `lesson-notation.js`, `lesson-key-terms.js`, `lesson-presentation.js`, `web/css/lessons.css`, and the actual router and data interfaces.
- `scripts/validate_lessons.py`, `scripts/test_lessons_browser.py`, `scripts/seed_lessons.py`, `npm run test:lessons`, `npm run test:builder`, CI and relevant authenticated/offline tests.

**Deliverable:** a status table with each chapter's actual source text/pages, content outline, existing implemented scope, new proposed scope, figure support, missing evidence and estimated learner time. Identify real file paths and commit SHAs. Never treat a planned feature as existing code.

---

# C. Instructional design specification

## C1. Coverage and timing

The 5–10 minute **whole-chapter** target and **majority-of-core-concepts** goal create a genuine trade-off. Treat 5–10 minutes as a target for the typical learner with the requisite prior knowledge, **including two tests of at least five questions each**. Do not claim that a chapter can be delivered within this target without testing reading and interaction time. Use the following order:

1. Select only indispensable foundational concepts and their dependency relationships using the book's actual chapter outline.
2. Ensure an example and a short evidence-based explanation for each selected concept.
3. Cover the highest-value structural operation or distinction with one genuine learner action and brief feedback.
4. Condense repetition and specialized exceptions; put omitted material in a documented coverage gap, not as hidden unsupported advice.
5. Budget time realistically: if the two five-question checks alone consume most of the allotment, present a measured estimate and request permission to exceed 10 minutes rather than silently omitting content or speeding up assessments.

A recommended **starting** time allocation, to validate in pilot trials: 1 minute introduction; 2–3 minutes teaching; 1–2 minutes worked/active practice; 1 minute recap; 2–3 minutes combined tests. This totals roughly 7–10 minutes, often optimistic for the more advanced chapters. Estimates must be revised using actual pilot completion times. Do not force unrelated specialist material into a lesson simply to maximize topic count.

## C2. Page sequence and learner experience

Provide a variable-page chapter with named sections shown in the new left sidebar. A compact typical sequence:

1. **Introduction + opening check (five or more questions):** state the key idea, prerequisite vocabulary, one contextual example, and what learners can do by the end. The diagnostic reports `x / n` only and grants zero XP; hide correct answers. Keep existing first-response marker semantics if valid for the new model.
2. **Core concept(s) (one or more pages):** short readable explanation, defined notation, sourced relationship, original example and a small understanding action. Avoid MC in the teaching content.
3. **Worked analysis + optional guided construction:** source-validated authored tree or diagram, numbered trace controls, visible corresponding explanation/callout; appropriately scoped interactive canvas where the book calls for construction.
4. **Transfer:** new example, unscored response/branch/boundary choice, feedback, hints and an optional answer reveal after an attempt. Persist editable practice drafts in the correct lesson/version/identity scope.
5. **Recap + references:** 3–5 key insights, common confusion, repeatable analysis procedure, and existing References dropdown with genuine B-R printed page/figure references.
6. **Closing knowledge check (five or more questions):** fair coverage of taught outcomes, appropriate accepted alternatives, trusted score/feedback/answer overview and retake/incremental XP logic.

Do not mechanically create six pages if fewer are clearer or more are necessary. **Never pad with trivial text or duplicate the same exercise.** Every page should answer a specific learner question. Do not enforce a perfect 5–10-minute target at the expense of actual comprehension.

## C3. Sidebar and navigation

- Left sidebar contains section titles for the selected chapter and reflects current location, visited state, saved practice and evaluated completion; indicate clearly what is merely visited versus completed.
- Chapters 1–12 remain in the main chapter navigator. Learners can open any chapter immediately; prerequisites are advisory only; do not block completion or browsing.
- Preserve forward/backward and resume/reload behavior; deep links and browser history must not silently reset work. Navigate back to the exact chapter section if a valid section ID survives revision; otherwise fall back safely.
- On narrow/mobile screens the sidebar should collapse into an accessible table-of-contents drawer/selector. Keep chapter text and canvas readable without horizontal overflow, with keyboard/touch focus management and accessible labels.
- Sidebar metadata and progress keys must remain stable within a version. Version changes must not reinterpret old section indexes as unrelated new content.

## C4. Exercises, feedback and examples

- All midpoint practice and embedded Builder construction are **unscored**, retryable, and independent of the closing-check XP total. Avoid coercing open text into parser-derived correctness: where robust automatic validation is impossible, use self-check with a reviewed model analysis.
- Prefer a combination of word-span or boundary selection, guided tree tracing, branch reattachment, compare-two-structures, short constructed responses and toy rule construction in Chapter 11. Exercises must match the chapter's **reviewed** tree/notation profile; no invented triangles, gap indices or placeholder labels.
- Keep the exercise prompt visible; explain expected controls, reveal feedback without requiring the learner to infer it from color; give hints and specific corrective guidance. Distinguish **wrong attempt** from **incomplete attempt**.
- Reuse an example in subsequent concept sections where it adds continuity, but use a different example for the transfer. Avoid copying source-book wording or diagrams verbatim; make original examples and review their grammatical claims.
- No automatic learner-facing instructor mode in this release.

## C5. Assessment, binary completion and XP — owner decisions APPROVED; technical implementation audited at Gate 0

**Baseline to change:** existing server-controlled, versioned lesson progress and 15-XP completion award, with stage/prerequisite mastery gating. The new contract replaces mastery with binary completion and replaces the all-or-nothing award with best-score-based incremental XP. These are approved product decisions, **not** a claim that implementation or database migration is complete.

- **New curriculum boundary:** Initialize active progress/completion and lesson XP at zero for each of Chapters 1–11. Do not carry forward any prior lesson-version score, award or completion. Maintain separate lesson data keys/catalog versions and reconcile any shared/global XP total safely. Chapter 12's content and score behavior remain out of scope unless the owner separately authorizes its reset.
- **Completion:** `chapter_completed = true` when required instructional stages and a first valid closing-check submission are recorded; score can be 0 to total. Never add a mastery threshold, pass percentage or requirement to achieve 15 XP. Completion remains true following later retries.
- **XP cap:** For `lesson_id` in the new curriculum, `MAX_XP=15` cumulatively. Use an exact trusted `best_correct/best_total`, with a deterministic formula, e.g. `eligible_xp=floor(15*best_correct/best_total)`. For exactly five equally weighted questions, the amounts are 0/3/6/9/12/15. If total counts differ across tests, do not assume raw correct counts are comparable: record a normalized best eligible-XP amount, and apply an explicitly tested policy.
- **Increment:** `delta_xp=max(0,new_eligible_xp - already_awarded_lesson_xp)` under a serializable/idempotent server-controlled operation. Score equal or worse => `delta_xp=0`. Better score => award only positive delta, never exceed total 15, regardless of number of attempts or repeats. First attempt is eligible even if score is below perfect.
- **Answer review and retake:** Show the answer overview after the closing check, as requested. Retakes remain eligible to improve the best score and recover missing XP **even after the answer key has been seen**. Do not present these scores as invigilated/proctored competence measures; the learner can look up answers. If the existing frontend treats retakes as temporary practice-only, revise the verified-scoring contract accordingly and differentiate any unofficial preview from an actual submitted retry.
- **Security and storage:** Determine correctness and XP in a trusted backend/RPC against versioned reviewed answers; never trust client XP, score, identity or completion flags. Preserve identity isolation/RLS, concurrency protection, replay resistance and offline sync reconciliation. Record last score, best verified score, cumulative earned chapter XP, binary completion and attempt history as appropriate. A failed sync does not imply a confirmed server award.
- **Reset implementation:** The owner authorizes starting anew for revised lessons, including clearing obsolete **lesson-specific** progress/awards if technically warranted. Prefer an additive version cutover. Exclude retired Foundations awards from active shared totals, prevent obsolete clients from re-awarding them, and reconcile the compatibility cache with the trusted ledger. Retain historical rows for rollback. Before executing destructive cleanup, inspect contributions to shared XP, leaderboards and achievements. Provide an explicit affected-table/row/identity inventory, dependency analysis, backups or recovery plan, and migration rehearsal. Perform no production mutation without separate owner deployment authorization. Never destructively delete unrelated identity, quiz, Builder, assessment or source-review records.
- **Tests:** first/worse/same/better/perfect submissions; repeated perfect retries; post-reveal improvement; out-of-order/concurrent requests; changed content version; offline reconnection; account isolation; stale cache; forgery; completion with 0/5; read-ahead navigation; and lesson-specific reset with no contamination of other features.

**Example progression:** First closing check 3/5 => 9 cumulative XP, chapter completed. Second 3/5 => +0 XP. Third 4/5 => +3 XP (12 cumulative). Fourth 5/5 => +3 XP (15 cumulative). Further 5/5 or lower => +0 XP. A first score of 0/5 still completes the chapter with 0 XP.

---

# D. Chapter-specific design cards

These are **proposed lesson outcomes and activities**, derived from the historical rollout map and chapter titles. **Phase 0 verified the table of contents and representative pages in a complete third-edition reference copy.** Review each chapter’s specific teaching claims, original examples, answer keys and figures during its implementation pass. Do not treat this table as a complete table of contents or as proof that a subtopic belongs to a given page. For each chapter, prepare a detailed source-to-outcome map before authoring.

| Ch. | Source range | Proposed indispensable learning goal | Original activity concept | Special caution |
|---|---|---|---|---|
| **1** Constituents | 6–23 | Explain nested grouping and how constituency evidence/ambiguity motivates tree structure | Highlight exactly the words spanned by a group; contrast two candidate groupings | Use `PHRASE-a/b` placeholders only if justified for the selected introductory representation |
| **2** Functions | 24–45 | Distinguish subject/predicate **function** from phrase **category**; identify appropriate NP–VP split | Select subject boundary and trace parents of NPs | Verify chapter-specific treatment of labels and whether a top-split triangle is warranted |
| **3** Categories | 46–66 | Introduce phrase categories and head-related distinctions at the book's actual level | Identify the head and phrase span in a compact authored tree | Do not reduce the chapter automatically to adjective phrases; first check the full chapter outline |
| **4** Basic VP | 67–86 | Explain verb–object relation and the basic internal VP hierarchy | Construct a reviewed transitive VP and distinguish subject vs object NP | Avoid presenting one VP shape as universal |
| **5** Adverbials etc. | 87–110 | Distinguish the important adverbial/adjunct attachments from complements | Compare an example with and without a temporal modifier | Check actual B-R attachments and conceptual coverage; do not overgeneralize tests |
| **6** Auxiliary VPs | 111–140 | Identify key auxiliary and embedded VP relationships in the book's progression | Trace a higher and lower VP in one source-validated example | Earlier rollout focused on progressive; audit whether other essential auxiliary patterns must be retained |
| **7** NP structure | 141–170 | Show nominal head, determiner and major NP-internal relationships | Assemble a reviewed NP from words and trace N → NOM → NP if source-authorized | Verify exact node/category notation; avoid importing Penn labels |
| **8** Sentences within sentences | 171–195 | Recognize a clause embedded in another construction and its structural boundaries | Mark outer and inner clause spans in an original example | Confirm whether `S′`, `C`, and alternatives apply to each example |
| **9** Wh-clauses | 196–223 | Explain core wh-clause fronting and source-appropriate gap relations | Trace fronted item to reviewed source-position gap(s) | Do not reduce the chapter automatically to object wh-questions; audit essential variations |
| **10** Non-finite clauses | 224–253 | Distinguish basic finite/non-finite clause analyses and source-approved infinitival structure | Select appropriate non-finite unit and trace a validated complement | Existing plan overfocuses on `to`; inspect chapter scope and feature-only notation |
| **11** Languages, sentences and grammars | 254–268 | Understand elementary rules of formation/recursion and their explanatory role | Step-by-step toy grammar derivation and repeated combination | A generic Builder is not obligatory; use source-matched rules and diagrams rather than invented B-R tree doctrine |
| **12** Cambridge | Separate source | **Out of scope** | No new activity | Do not change contents, answers, completion/scoring contract or Cambridge source mapping except unavoidable shared regression repairs |

For each revised chapter, output the following before coding:

1. Actual B-R subsection list, verified chapter/printed page anchors, and figure/representation inventory.
2. Selected **3–5 highest-priority takeaways**, each linked to book evidence. For longer source chapters, explain what is omitted and why.
3. Exact chapter timing estimate and the budget for introduction, teaching, activities and two five-question checks. If it exceeds 10 minutes, show the trade-off and request owner approval.
4. Page-by-page teaching storyboard with specific learner decisions, notation definitions, authored diagram requirements and feedback.
5. Original sentence examples, reviewed tree/alternative analysis and accepted answers.
6. Opening ≥5 and closing ≥5 **different** items, mapped to taught objectives. The two sets may test similar skills, but avoid copying identical questions as a default.
7. Source-verification receipt, known ambiguities, existing content reused/retired and rationale.

---

# E. Phased execution plan and gates

## Phase 0 — Baseline audit and approved-policy implementation design (NO application edits)

- Confirm actual worktree/branch and compare it with `main`/the parent branch. Inspect all relevant source, curriculum, code, persistence, test and deployment files.
- Verify the book manifest, locate actual full chapter PDFs or equivalent reliable page evidence, and build a precise 11-chapter source coverage inventory, not relying on the old simplified curriculum map.
- Record current lesson navigation, exercises, scoring, historical XP, versioning, migrations and authenticated/local/offline behavior.
- Provide a technical change-impact design for the sidebar, variable pages, opening-check expansion, partial XP, fresh chapter completion/progress, history and security.
- Document how to implement the **three already-approved policies**: (i) reset old lesson XP/progress for a fresh 15-XP maximum on the revised curriculum; (ii) award only positive XP differences on higher verified retake scores, including after answer review; and (iii) use completed/not-completed chapter status without mastery thresholds. Audit shared XP totals before planning any lesson-only reset; do not reopen policy decisions.

**Gate 0:** Owner approves source/baseline evidence, prioritized coverage, migration/reset execution plan, implementation impact and security checks. The three product policies are already approved. No code edits or schema changes before approval.

## Phase 1 — Shared chapter player and navigation

- Preserve existing layout/branding but add the accessible chapter-section sidebar, variable-length section definitions, deep-link/resume, progress states and mobile behavior.
- Refactor only where necessary to support data-driven chapter sections and current chapter component lifecycle. Keep all existing 12 published lessons functional with their present content.
- Tests: chapter navigation, reload, back/forward, dark/light mode, desktop/mobile, keyboard/touch focus, screen reader labels, browser history, draft recovery and historical version isolation.

**Gate 1:** Owner reviews desktop/mobile screenshots and navigation behavior; all existing lessons and builder regressions pass.

## Phase 2 — Exercise, quiz and XP infrastructure

- Reuse or extend unscored read/trace/select/build exercises and hints without coupling lesson grading to parser predictions.
- Add the five-question no-XP opening check with a numerical score and five-plus-question scored closing check, with answer visibility rules and separate best/last attempt summaries.
- Introduce the **approved** server-backed incremental XP and binary chapter-completion policy through additive versioned schema/seed/RPC changes, preserving historical data and trusted identity boundaries. Do not run a destructive or hosted reset until its specific migration plan and deployment have been approved.
- Update validators and tests in lockstep, using fresh content versions and source receipts when assessment items change.
- Test idempotent awards, concurrency, better/worse/equal score, advisory prerequisites, post-reveal improvement, guest/offline behavior, hostile client input, RLS and rollback. Verify that the Cambridge companion can still use the existing Chapter 2 prerequisite when old Foundations versions are retired. Keep its assessment and scoring path intact.

Phase 2 implementation and local walkthrough are recorded in [the Phase 2 review](../reports/syntax-foundations-revision-phase-2.md).

**Gate 2:** Owner approves actual examples of XP progression and review states; local SQL tests and browser regressions pass. Hosted migration remains separately approval-gated.

## Phase 3 — Chapter 1 pilot: content, interaction and evaluation

- Perform source-mapped storyboard, original examples, concise concept teaching, tree diagrams and guided exercises for **Chapter 1 only**. Follow the complete chapter process in Section D.
- Verify actual 5–10-minute feasibility by timed user pilot; if unrealistic, present a concrete scope/time trade-off.
- Confirm the exact source-review and publication/version process before proceeding to later chapters.

The [Chapter 1 pilot review](../reports/syntax-foundations-chapter-1-pilot.md) records the source check, local preview and verification results.

**Gate 3:** Owner personally walks Chapter 1, accepts linguistic accuracy, readability, activity quality, approximate completion time, and sources. Only then generalize the pattern.

## Phase 4 — Chapters 2–11, sequentially with per-chapter owner gates

Order: 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11. For **each** chapter:

1. Inspect source pages and relevant current implementation; list indispensable and omitted topics.
2. Submit an outline, time estimate, examples, reviewed answer key plan and UI activities for owner approval **before implementation**.
3. Implement only that chapter plus necessary well-tested shared fixes.
4. Run targeted and project-level tests, create source receipt, version bump and matching seed where applicable.
5. Present desktop/mobile chapter walkthrough, one correct and one incorrect attempt, feedback, resume and XP behavior.
6. Provide commit SHA(s), changed files, page anchors, limitations and open questions. **Stop at the owner gate**; do not auto-advance.

**Gates 4.2–4.11:** Separate owner approval for each completed chapter. Rejected or unresolved chapters remain unapproved and must not be treated as complete. Keep lesson 12 unchanged.

## Phase 5 — Full-course integration and release readiness

- Run all content/figure source provenance and notation validation, 11-chapter coverage, per-version schema/seed checks, navigation/resume, builder and exercise regressions, responsive accessibility, identity and progress isolation, XP/award replay controls, account/offline and database checks, and app packaging/static build.
- Verify revised Chapters 1–11 start with fresh progress, zero lesson XP and incomplete statuses, with old lesson states excluded and unrelated account/global data preserved; Chapter 12 still behaves as intended.
- Validate selected early/middle/advanced chapters visually on desktop and mobile. Run a small real-user timing and clarity review where possible. Document what cannot be verified locally.
- Prepare migration/deployment/rollback documentation and the final owner acceptance report. Do not claim production verification without production evidence.

**Gate 5:** Owner reviews course-wide release candidate; only then publish/merge/deploy as separately instructed.

---

# F. Objective acceptance checklist

A chapter is **not completed** unless all applicable items are verified:

- [ ] Third-edition source identity, chapter/subsection scope and printed page/figure anchors are verified; unsupported content is removed or explicitly marked unresolved.
- [ ] Learning outcomes cover the prioritized core of the actual chapter, with specialized omissions documented.
- [ ] Expected **whole-chapter** completion duration is reported, with evidence or a clearly labeled untested estimate.
- [ ] UI contains a recognizable intro, concise concept explanation(s), one worked analysis, relevant unscored practice, recap/references and valid closing check.
- [ ] Opening check has ≥5 versioned items, displays score but no answer key and gives no XP.
- [ ] Closing check has ≥5 independently reviewed items, gives score/feedback/review and follows approved trusted retake policy.
- [ ] XP and binary completion are separately tracked; max award, positive-only increments, post-reveal retakes, security, replay handling and advisory prerequisites pass relevant tests.
- [ ] Every chapter is browsable and completable regardless of prerequisites or score; old version data cannot count toward revised completion or XP.
- [ ] Any tree/diagram is valid under the correct B-R chapter representation and not treated as parser-derived truth.
- [ ] Key terms and notation are defined before assessment; exercise feedback identifies the relevant words/branches/rules.
- [ ] Original examples and independently reviewed answers do not silently contradict the source or use unjustified parser outputs.
- [ ] Sidebar/forward/back/resume and draft persistence work on desktop and mobile; light/dark mode, keyboard, touch and buttons behave correctly.
- [ ] Reviewed content version, receipt, migrations and generated seed are synchronized; prior records and unrelated M5/M6 behaviors remain intact.
- [ ] Executed tests and real observations are reported accurately; failures and unrun checks remain visible.
- [ ] Owner approves the chapter's presented learner walkthrough, source verification and implementation report.

## Suggested commands (verify scripts exist on actual branch)

```bash
python scripts/validate_lessons.py
npm run test:lessons
npm run test:builder
python scripts/test_lessons_browser.py
```

Also run related Builder, static build, browser, SQL/RLS/authentication and CI suites **if present and relevant**, recording exact commands and outcomes. No success claims from merely reading an old test report.

---

# G. Mandatory per-phase / per-chapter handoff template

```
Phase / chapter:
Branch and base SHA:
Current HEAD and commit(s):
Status: in progress | blocked | verified | owner approved
Book edition / chapter / printed pages actually inspected:
Source receipts (IDs, hashes and checks):
Core concepts taught and why selected:
Specialized topics omitted / deferred:
Learning outcomes and page-by-page storyboard:
Estimated or observed total chapter time (including checks):
New original examples and validated tree/diagram representations:
Files changed and rationale:
Changes to existing learner-facing behavior:
Opening check / closing check item counts and review status:
Progress, binary completion, XP and versioning effects:
Test commands, pass/fail counts, screenshots and untested areas:
Desktop/mobile/keyboard/touch/light/dark observations:
Known limitations, source ambiguities and regressions:
Owner walkthrough steps and concrete questions:
Next proposed change (NOT started before owner approval):
```

At the end of a handoff, **stop** and ask for a specific approval or needed source clarification. Do not automatically merge into `main` or begin the next phase.

---

# H. Resume at the current gate

Phase 0 has an audit handoff on the revision branch. Review its chapter coverage, timing trade-offs, existing receipt drift, proposed XP cutover and Chapter 12 compatibility. Once Gate 0 is approved, implement Phase 1 and present the sidebar and navigation walkthrough for Gate 1.

For later chapters, use one handoff document or pull-request summary per unit. Carry shared baseline and migration decisions forward by reference. Update only the chapter's new evidence, examples, outcomes, test results and open decisions. The chapter's outline and completed walkthrough still require the approval in Phase 4. Keep commits on the revision branch until the owner authorizes integration.

---

# I. Provenance / verification boundaries for this master prompt

**Owner-provided decisions:** The uploaded `master_prompt_lesson_revision_plan.md` and follow-up confirmations (scope, timing, XP, chapter access, fresh reset, opening and closing assessments), plus final owner approvals on 2026-11-13: no old lesson data carryover; no XP on unchanged/worse attempts; binary completed/not-completed status rather than mastery.
**Repository-confirmed planning/context (read from GitHub parent branch):** B-R source manifest, earlier foundations structure/rollout/polishing plans, M4 implementation brief, source authority matrix, M4 acceptance and progress/deployment contract.
**Proposed, not source-verified yet:** Detailed subtopic coverage, sample exercise designs, 5–10-minute feasibility, new scoring formula implementation, real hosted DB status, current local-branch implementation, latest working-code validation and Chapter 11 visualization details.

**Interpretation rule:** Where a previous roadmap document conflicts with the owner-confirmed curriculum and assessment changes, make the conflict explicit and propose a versioned migration. Where a proposed educational activity conflicts with primary B-R evidence, the verified primary source wins. Where owner intent conflicts with data integrity, security or unreviewed grammatical certainty, stop and propose a safe equivalent instead of silently weakening protections.
