# SynTutor Quiz V2 Requirements Audit Report

## A. Audited Snapshot

- **Repository Root:** `/Users/kiyel/Desktop/SynTutor`
- **Target Branch:** `feat/quiz-v2`
- **Target HEAD SHA:** `28891d77ca3acd9c964f4514171a485adb51727d`
- **Reference Branch:** `origin/main`
- **Reference HEAD SHA:** `0d879fc534dc834dc5d8fec7b82cdb730e52f8a1`
- **Merge Base SHA:** `115b1dfc1bfda90697344d2a72d5e47ba7828782`
- **Ahead / Behind Status:** Ahead 5 commits, behind 11 commits from `origin/main`.
- **Working-Tree State:** Clean working tree (no modified tracked files; one untracked audit directory `docs/audits/` preserved untouched).
- **Audit Mode:** Read-only inspection and local test execution.

---

## B. Requirements Compliance Matrix

| ID | Requirement | Status | Evidence | Missing/Incorrect Behavior |
|---|---|---|---|---|
| **R1** | Two Quiz Tracks (Syntax & Cambridge tabs) | **PASS** | `web/js/quizzes-ui.js` lines 50–55 render track tabs (`Syntax — Burton-Roberts`, `Cambridge — Cambridge Grammar`). `curriculumCatalog()` renders independent tracks, each with its own `Personalized [Track] Quiz`. `topicPerformance()` in `web/js/quiz-v2.js` strictly filters attempt rows by `m?.track_id === trackId`. Verified in `scripts/test_quiz_formal.js` and node execution. | None. Tab switching updates catalog without mutating in-progress attempts. |
| **R2** | Expandable Chapter Blocks & Subtopic Quizzes | **PASS** | `web/js/quizzes-ui.js` renders native `<details class="curriculum-card quiz-chapter">` with `<summary>` per chapter. Chapters match active Lessons in titles and order (11 Syntax chapters, 19 Cambridge chapters). All 317 subtopics correspond 1:1 to instructional sections in `pilotArticles` and `cambridgeChapterData`. Preliminaries (`cgel-ch01`) and non-grammatical orientation (`br-11/concepts`) are excluded in `web/js/quiz-scope.js`. | None. |
| **R3** | Chapter General Quizzes | **PASS** | Every eligible chapter has a General Quiz (11 in Syntax, 19 in Cambridge = 30 total). Verified with `makeV2Attempt` that all 30 General Quizzes cover 100% of their subtopics. Implements `Math.max(5, chapter.topics.length)`: chapters with $\le 5$ topics contain 5 questions; chapters with $> 5$ topics contain one question per subtopic. Selection uses PRNG-seeded `balancedSelection` with no duplicates. | Specification ambiguity resolved via `Math.max(5, topics.length)`. Does not use a flat 5-item count for large chapters, nor $< 5$ for small chapters. |
| **R4** | Randomized Question Bank | **PARTIAL** | Regular topic quizzes contain exactly 5 questions (`validateAttempt` rejects $\ne 5$). PRNG-seeded shuffling randomizes item selection, item order, and option order. Pre-submission projection (`questionForLearner` in `web/js/quiz-core.js`) strips answers, rationales, trees, and feedback; `reviewForLearner` throws before submission. Draft attempts are preserved in `localStorage`. All 317 topics have $\ge 5$ distinct items. | **Review status shortfall:** Only 120 questions in `bank.json` have `INDEPENDENTLY_REVIEWED` status (110 Syntax, 10 Cambridge). The remaining 2,810 assessment items are programmatically derived `assessment_draft` items flagged `UNREVIEWED` (`independent_review: false`). They are playable but XP-exempt, awaiting human linguistic review. |
| **R5** | Master Quiz | **PASS** | Both tracks provide a Master Quiz with interactive numeric input. Minimum count equals chapter count (11 Syntax, 19 Cambridge). Capacity scales up to available pool (max capped at 1,000 via `MAX_QUIZ_ITEMS`). Tested divisible (22, 38) and non-divisible (15, 25, 37, 50) totals: all chapters represented, water-fill allocation ensures spread $\le 1$, ties rotated fairly, variable-length grading verified in `gradeAttempt`. | None. |
| **R6** | Sidebar XP and Level | **PASS** | `web/index.html` (lines 138–142) places `<section id="sidebarProgress">` directly below `#sidebarAuthBtnWrapper`. Display values derive from `supabase.rpc('get_my_progression')` and `levelFromXp` (`web/js/level.js`). Unauthenticated/local states clearly state "Sign in for verified XP" and "Local practice is not verified XP". Expanded vs collapsed sidebar states styled in `web/css/style.css` (collapsed hides subtitle and centers text at 9px). Refreshes on auth changes, window focus, quiz progress, and lesson progress. | None. |
| **R7** | Existing Progression System Reuse | **PASS** | `web/js/level.js` is unchanged and reused directly. Server RPC `get_my_progression` is reused. Additive Supabase migration `20261116000000_quiz_practice_v2.sql` isolates practice attempts to `quiz_practice_v2` with `xp_policy: 'unscored-v2'`. Ledger isolation and forged XP rejection verified in `scripts/test_quiz_v2_database.js`. | None. |
| **R8** | Personalized Syntax Quiz | **PASS** | `topicPerformance` in `web/js/quiz-v2.js` aggregates completed Syntax attempts, computes Bayesian topic weakness and concept error rates, and permanently excludes all previously missed question IDs (`performance.missed`). Unseen questions receive priority. New learners ($< 5$ answers) trigger a balanced 5-chapter diagnostic assessment. Insufficient eligible questions ($< 5$) throw a clear diagnostic error message. Cambridge attempts are strictly excluded. | None. |
| **R9** | Personalized Cambridge Quiz | **PASS** | Evaluated independently for Cambridge track. Cambridge attempts tracked separately from Syntax. Only taught Cambridge grammar concepts are included (Chapters 2–20). Preliminaries (`cgel-ch01`) is strictly excluded from curriculum and question pools. Missed questions permanently excluded. Diagnostic mode and insufficient question handling verified. | None. |

---

## C. Lessons-to-Quiz Coverage

The active Lessons curriculum is composed dynamically from `web/content/lessons/course.json`, Burton-Roberts pilot articles (`pilotArticles`), and Cambridge chapter data (`cambridgeChapterData`).

### 1. Chapter-Level Coverage Summary

| Curriculum Track | Lessons Chapters | Quiz Chapters | Matched | Excluded | Notes |
|---|---|---|---|---|---|
| **Syntax (Burton-Roberts)** | 11 (`br-01` to `br-11`) | 11 | 11 | 0 | 1:1 chapter ID, title, and ordering match. |
| **Cambridge Grammar (CGEL)** | 20 (`cgel-ch01` to `cgel-ch20`) | 19 | 19 | 1 (`cgel-ch01`) | Preliminaries (`cgel-ch01`) intentionally excluded from Quiz assessment scope per policy. |
| **Total** | **31** | **30** | **30** | **1** | **100% of assessable chapters covered.** |

### 2. Subtopic Coverage Summary

- **Syntax Track Topics:** 50 assessable topics across 11 chapters (3 to 6 topics per chapter).
  - *Excluded Topic:* `br-11/concepts` (Languages, sentences, and grammars: language varieties and prescriptivism orientation), excluded in `web/js/quiz-scope.js` as orientation rather than phrase-structure analysis.
- **Cambridge Track Topics:** 267 assessable topics across 19 chapters (11 to 19 topics per chapter).
  - *Excluded Topics:* Section IDs `introduction`, `recap`, `chapter-review`, `closing-check`, and exercise sections (`exercises on...`) are filtered out from assessment catalog.
- **Total Assessable Subtopics:** **317 topics**.
- **General Quizzes:** **30 quizzes** (11 Syntax, 19 Cambridge).
- **Master Quizzes:** **2 quizzes** (Syntax Master, Cambridge Master).
- **Mapping Correctness:** 317 of 317 subtopics map to active instructional sections in `pilotArticles` and `cambridgeChapterData`. Zero invented or orphaned topics.

---

## D. Test Results

### Executed Automated Tests

| Command | Exit Code | Result | Key Evidence |
|---|---|---|---|
| `git rev-parse HEAD && git rev-parse origin/main` | `0` | **PASS** | Target `28891d7...`, Reference `0d879fc...`, Merge Base `115b1df...` |
| `git diff --check 115b1df...HEAD` | `0` | **PASS** | Zero whitespace or formatting errors. |
| `node scripts/test_quiz_v2.js` | `0` | **PASS** | 11 ch / 50 topics, 19 ch / 267 topics; balanced counts, review gates, seed replay, personalization exclusions, variable grading, zero XP. |
| `node scripts/test_quiz_lesson_practice.js` | `0` | **PASS** | 2,930 source-grounded items, 317 topics, 30 General quizzes, both Masters, zero XP, identity isolation. |
| `node scripts/test_quiz_formal.js` | `0` | **PASS** | 317 topics, 30 General, both Masters, Preliminaries excluded, pre-submit projection gates, post-submit scoring. |
| `node scripts/test_quiz_v2_database.js` | `0` | **PASS** | PostgreSQL/PGlite verification: Clerk auth, owner RLS, immutable practice manifests, required unscored policy, forged XP denial. |
| `node scripts/test_assessment_core.js` | `0` | **PASS** | 16 blueprints / 120 variants, deterministic randomization, review gates, draft/submission immutability. |
| `node scripts/test_assessment_database.js` | `0` | **PASS** | Real PostgreSQL seed manifests, score/blueprint verification, RLS, quiz/lesson separation. |
| `node scripts/test_level.js` | `0` | **PASS** | Pilot thresholds, 1,000 level boundaries, invalid XP handling. |
| `node scripts/test_account_integration.js` | `0` | **PASS** | Session-bound token races, JSONB ordering, version archival. |
| `node scripts/test_explanation_evidence.js` | `0` | **PASS** | Shared explanation request/state contract. |
| `node scripts/test_lesson_progress.js` | `0` | **PASS** | All 31 lessons, stage/answer gates, prerequisite isolation, offline account sync. |
| `node scripts/test_lesson_database.js` | `0` | **PASS** | PostgreSQL lesson progress, direct-write/forged-XP denial, RLS isolation. |
| `python3 scripts/test_foundation_fixture.py` | `0` | **PASS** | Foundations lesson curriculum fixtures parsed and validated. |
| `node scripts/test_tree_quiz.js` | `0` | **PASS** | Tree quiz POS tagger, parser, and rule matrix validation. |
| `node scripts/test_tree_layout.js` | `0` | **PASS** | Layout widths, correction shapes, and tree rendering invariants. |
| `node scripts/test_builder_core.js` | `0` | **PASS** | Builder round-trips, profile palettes, undo/redo branches. |

### Blocked / Sandbox-Restricted Tests

| Command | Exit Code | Classification | Failure / Block Evidence |
|---|---|---|---|
| `QUIZ_V2_PLAYWRIGHT_MODULE=... node scripts/test_quiz_v2_browser.js` | `1` | **UNVERIFIED** | `page.goto: net::ERR_ACCESS_DENIED at http://127.0.0.1:63020/`. The standard terminal sandbox isolates loopback sockets, blocking Playwright Chromium from connecting to the internal test server. Headless browser interaction could not be executed end-to-end inside the sandbox. |
| `node scripts/test_foundation_progress.js` | `1` | **UNVERIFIED** (in part) | `spawnSync python3 EPERM` when Node attempts to spawn a subprocess inside the sandbox. (Note: `python3 scripts/test_foundation_fixture.py` succeeds when invoked directly). |

---

## E. Confirmed Issues

### Issue 1: Question Bank Lacks Independent Human Review for 96% of Assessable Topics
- **Severity:** **P1**
- **Exact Behavior:** Only 120 questions across 10 Syntax topics and 1 Cambridge topic have `INDEPENDENTLY_REVIEWED` status in `web/content/quizzes/bank.json`. The remaining 2,810 assessment items across 316 topics are programmatically generated drafts (`bank.assessment_items`) marked `review_status: 'UNREVIEWED'`, `publication_status: 'assessment_draft'`, and `independent_review: false`. While fully playable and scored locally, these items are ineligible for server-verified XP (`xp_policy: 'unscored-v2'`).
- **File and Function:** `web/js/quiz-assessment-items.js` (`makeAssessmentItems`), `web/js/quiz-v2.js` (`eligibleQuestions`).
- **Reproduction Steps:**
  1. Inspect `bank.assessment_items`: observe `review_status === 'UNREVIEWED'`.
  2. Complete any Cambridge topic quiz or non-blueprint Syntax quiz.
  3. Observe that XP awarded is 0 and submission syncs only to `quiz_practice_v2` without updating server progression.
- **Smallest Practical Fix:** Conduct qualified human linguistic review on the drafted question pools in `web/content/quizzes/v2-review-queue.json` and generated assessment items, update their review metadata to `INDEPENDENTLY_REVIEWED`, and publish approved blueprints into `web/content/quizzes/bank.json`.

---

### Issue 2: General Quiz Question Count Diverges Under Strict "5-Items Always" Interpretation
- **Severity:** **P2**
- **Exact Behavior:** Requirement 3 contains a specification ambiguity: "all quizzes contain five items, but also require the General Quiz item count to equal the number of subtopic quizzes." The branch implements `Math.max(5, chapter.topics.length)`. Consequently, Cambridge General Quizzes range from 11 to 19 items (e.g. Chapter 19 General Quiz has 19 items). A user or test expecting all quizzes to be exactly 5 questions will observe variable counts.
- **File and Function:** `web/js/quiz-v2.js` (`GENERAL_POLICY`, `selectQuestions`).
- **Reproduction Steps:**
  1. Start General Quiz for Chapter 2 (`cgel-clauses`).
  2. Observe `presented.length === 16` rather than 5.
- **Smallest Practical Fix:** If product owners require strict 5-item General Quizzes, update `selectQuestions` to select a 5-item sample across subtopics; otherwise, officially adopt `Math.max(5, chapter.topics.length)` in the product specification.

---

### Issue 3: Browser E2E Test Suite Cannot Run in Sandboxed Environment
- **Severity:** **P3**
- **Exact Behavior:** `scripts/test_quiz_v2_browser.js` binds to `http://127.0.0.1:0` and instructs Playwright Chromium to navigate to that URL. In standard sandbox execution, loopback networking is blocked, resulting in `net::ERR_ACCESS_DENIED`.
- **File and Function:** `scripts/test_quiz_v2_browser.js` (lines 20–25, `server.listen`).
- **Reproduction Steps:**
  1. Run `QUIZ_V2_PLAYWRIGHT_MODULE=... node scripts/test_quiz_v2_browser.js` inside standard sandbox.
  2. Observe failure at `page.goto(base)`.
- **Smallest Practical Fix:** Refactor browser test runner or CI environment to execute in a pipeline with local loopback binding permitted, or mock navigation using file-based or memory-based DOM testing.

---

## F. Final Verdict

### Does `feat/quiz-v2` meet ALL original requirements?
# **NO**

### Explanation
The `feat/quiz-v2` branch implements the technical architecture for SynTutor Quiz V2: curriculum alignment with active Lessons, two separated tracks, expandable chapters, randomized question selection, variable Master Quizzes, personalized weakness prioritization with missed-question exclusions, and verified sidebar XP progression. However, it does not yet satisfy **all original requirements** because **Requirement 4 (Randomized Question Bank)** is only partially fulfilled: 2,810 of the 2,930 assessment items remain unreviewed drafts (`review_status: 'UNREVIEWED'`) without independent human linguistic sign-off, forcing all new topics and Cambridge assessments to remain XP-exempt practice rather than fully verified assessments. Furthermore, live headless browser interaction could not be completed within the execution sandbox (`UNVERIFIED`).

### Prioritized Checklist of Remaining Work

1. **[P1] Linguistic Review & Question Promotion:** Submit the 2,810 generated assessment drafts and review-queue items in `web/content/quizzes/v2-review-queue.json` for independent human linguistic verification, promote approved items to `INDEPENDENTLY_REVIEWED`, and publish assessment blueprints for Cambridge and remaining Syntax topics.
2. **[P1] Verified XP Enablement for Quiz V2:** Once blueprints and items achieve reviewed status, create migration and RPC support allowing published V2 assessments to award verified server XP via `save_quiz_attempt`.
3. **[P2] Specification Alignment on General Quiz Length:** Formalize product sign-off on the `Math.max(5, topic_count)` question policy for General Quizzes to resolve the original 5-item specification conflict.
4. **[P2] Automated Browser E2E in CI:** Configure continuous integration outside the restricted sandbox to run `test_quiz_v2_browser.js` against Playwright Chromium for automated visual and DOM regression checks.
5. **[P3] Child Process Subprocess Permissions:** Update `scripts/test_foundation_progress.js` to avoid `spawnSync('python3')` or ensure Python test fixtures are invoked through a standard runner compatible with sandboxed execution.
