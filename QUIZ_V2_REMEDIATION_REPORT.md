# SynTutor Quiz V2 Remediation Report

- **Repository:** `/Users/kiyel/Desktop/SynTutor`
- **Branch:** `feat/quiz-v2` (isolated from `main`; not merged, rebased, reset, or pushed)
- **Integration Target Tested:** `feat/quiz-v2` + `origin/main` (`0d879fc534dc834dc5d8fec7b82cdb730e52f8a1`) in temporary clone `/tmp/quiz-v2-main-integration` (cleaned up after verification)

---

## 1. Confirmed Problems Fixed

### Priority 0 — Lesson-to-Quiz Integration & Stale Digest Handling
1. **Stopped silent discarding of Syntax questions on digest mismatch:** `makeLessonPractice()` in `web/js/quiz-lesson-practice.js` previously executed `continue` silently when `source.article_digest !== syntaxPracticeDigest(chapter.id)` or `source.lesson_version !== chapter.content_version`. Added `findStaleSyntaxSources()` and `validateSyntaxPracticeSource()`: `makeLessonPractice()` now throws loudly by default when any Syntax chapter digest/version is stale, and `web/js/quizzes-ui.js` passes `{ onStale }` to surface an explicit warning banner in the UI rather than silently hiding chapters.
2. **Validated `scripts/build_quiz_practice.js` & regenerated `syntax-practice-source.json`:**
   - Verified `scripts/build_quiz_practice.js` against both `feat/quiz-v2` and a temporary merged `feat/quiz-v2` + `origin/main` integration tree.
   - Before regeneration on the merged `origin/main` tree, `test_quiz_digest_freshness.js` detected `digest_mismatch` across **9 Syntax chapters / 40 topics** (`br-01`, `br-02`, `br-03`, `br-05`, `br-07`, `br-08`, `br-09`, `br-10`, `br-11`) due to `origin/main` edits to `teach` prose.
   - Regenerated `web/content/quizzes/syntax-practice-source.json` via `scripts/build_quiz_practice.js` (`50` active Syntax sections, removing the stale `br-11/concepts` leftover from pre-scope-exclusion capture).
3. **Added automated stale-digest test:** Created `scripts/test_quiz_digest_freshness.js` and wired it into `npm run test:quiz-v2` in `package.json`.

### Priority 1 — Defective Question Generation Templates
1. **A. Concept completion (`explanation-*`):**
   - Retired `sentenceFacts()` arbitrary verb-splitting in `web/js/quiz-lesson-practice.js` and excluded `lesson_recall` in `web/js/quiz-assessment-items.js`.
   - Eliminated all `1,201` incomplete-sentence verb-split items, punctuation-leading fragments (`76` items), unresolved anaphoric stems (`84+` items), and verbatim prose-recall items.
   - Fixed `additions` in `web/js/quiz-assessment-items.js` to fall back to a chapter-level metadata basis so valid hand-authored `rule_application` items (`cgel-ch06/modifier-style`, `br-07/application`) are not lost when `sentenceFacts()` is removed.
2. **B. Example analysis (`example-*`):**
   - Rejected `mark !== 'ok'` items, `selfLeak` items (where the correct note leaks lexical words unique to its own example, such as `"Elizabeth"` in `cgel-ch05/proper-names`), and distractors citing foreign lexical words, `*...*`/`“...”` phrases, or sentence-initial capitalized tokens/phrases from other examples in the block (e.g., `"To me is a PP complement"`, `"What a liar"`, `"How difficult"`, `"speaking only to the husband"`, `"Now"`, `"Soon"`).
   - Required `>= 2` clean, compatible distractors (`>= 3` total options).
3. **C. Table analysis (`table-*`):**
   - Added `formatTablePrompt()` to eliminate raw `which what changes` / `which anchored to` / `which temporal` / `which tensed` interpolation bugs and preserve uppercase `NP`.
   - Rejected tables with empty column headers, `< 3` distinct target values (eliminating all `51` 2-option binary questions), and excluded comparison-matrix / lexeme-paradigm target columns (`take`, `want`, `hit`, `Direct object`, `Indirect object`, `Auxiliary`, `Lexical verb`, etc.).
   - Rejected rows with bare single-word proper-name `Example` answers (`Kim`, `Pat`), rows duplicating a context cell, and rows with lexical leakage between context and options.
4. **Accurate unavailable state & validation gates:**
   - Updated `web/js/quiz-v2.js` and `web/js/quizzes-ui.js` (`v2Card` catch block) so topics with `< 5` validated assessment questions accurately display `Questions Under Review: X/5 distinct validated assessment questions available.` with a disabled button rather than `0/5` or manufacturing replacement items.
   - Added strict invariants to `validateLessonPractice()` and `validateAssessmentItems()` (`>= 3` options, no punctuation-leading options, no `____` completions, no `which what/how/why/...` prompts, only `analysis` and `rule_application` kinds for generated assessment items).

---

## 2. Files Changed

- [package.json](file:///Users/kiyel/Desktop/SynTutor/package.json) — Added `scripts/test_quiz_digest_freshness.js` to `test:quiz-v2`.
- [web/js/quiz-lesson-practice.js](file:///Users/kiyel/Desktop/SynTutor/web/js/quiz-lesson-practice.js) — Added stale-digest detection/validation, retired `sentenceFacts()`, added `formatTablePrompt()`, and added strict example & table filtering.
- [web/js/quiz-assessment-items.js](file:///Users/kiyel/Desktop/SynTutor/web/js/quiz-assessment-items.js) — Excluded `lesson_recall`, wired `formatTablePrompt()`, fixed chapter fallback for `additions`, and tightened `validateAssessmentItems()`.
- [web/js/quiz-v2.js](file:///Users/kiyel/Desktop/SynTutor/web/js/quiz-v2.js) — Clarified `< 5` topic error label (`validated assessment` vs `reviewed`).
- [web/js/quizzes-ui.js](file:///Users/kiyel/Desktop/SynTutor/web/js/quizzes-ui.js) — Fixed `v2Card` `catch(e2)` reason propagation and surfaced stale-source warnings via `onStale`.
- [web/content/quizzes/syntax-practice-source.json](file:///Users/kiyel/Desktop/SynTutor/web/content/quizzes/syntax-practice-source.json) — Regenerated (`50` active Syntax sections matching active Lessons).
- [scripts/test_quiz_digest_freshness.js](file:///Users/kiyel/Desktop/SynTutor/scripts/test_quiz_digest_freshness.js) — New automated test failing on stale Syntax digests or version mismatches.
- [scripts/test_quiz_lesson_practice.js](file:///Users/kiyel/Desktop/SynTutor/scripts/test_quiz_lesson_practice.js) — Updated section count check (`50`), stale-digest failure assertions, and `< 5` / General unavailable-state assertions.
- [scripts/test_quiz_formal.js](file:///Users/kiyel/Desktop/SynTutor/scripts/test_quiz_formal.js) — Added regression assertions rejecting every confirmed defective item ID/template from `QUIZ_V2_FINAL_READINESS.md` and verifying accurate unavailable states.
- [scripts/test_quiz_v2_database.js](file:///Users/kiyel/Desktop/SynTutor/scripts/test_quiz_v2_database.js) — Switched formal Cambridge topic fixture from `cgel-ch06/modifier-style` (`2/5` available) to `cgel-ch04/clause-patterns` (`>= 5` available).
- [scripts/test_quiz_v2_browser.js](file:///Users/kiyel/Desktop/SynTutor/scripts/test_quiz_v2_browser.js) — Verified unavailable state for `br-03/concepts` (`0/5`), playable non-blueprint Syntax topic (`br-02/worked-example`), Cambridge General Quiz (`cgel-ch04`, 13 items), and Personalized Cambridge Quiz.

---

## 3. Question-Template Changes

| Template / Family | Before | After |
|---|---|---|
| `explanation-*` (`concept_completion`) | Split lesson sentences at first verb (`sentenceFacts`), swapped tails across sentences | **Retired** (`0` generated items; incomplete verb-split stems rejected by `validateAssessmentItems`) |
| `example-*` (`analysis`) | Paired `example.text` with any other `example.note` in block | **Filtered** (`mark: 'ok'`, no `selfLeak`, no foreign lexical citations/capitalized phrases, `>= 3` options) |
| `table-*` (`analysis`) | Picked rightmost `>= 2`-value column, interpolated `which ${col}` | **Repaired & Filtered** (`formatTablePrompt`, `>= 3` distinct values, no empty headers, no comparison-matrix target columns, no context/answer overlap or bare proper-name answers) |
| `rule_application` (`original-application-*`, `coordination-*`, `formal-application-*`) | Hand-authored items (`92` total; `4` dropped if topic lacked `lessonItems`) | **Retained (`92/92`)** with chapter-level metadata fallback for `additions` |

---

## 4. Question Counts: Retained, Rejected, and Unreviewed

- **Published independently reviewed bank (`web/content/quizzes/bank.json`):** `120` items (`110` Syntax, `10` Cambridge) — **100% retained**, `INDEPENDENTLY_REVIEWED`, XP-eligible.
- **Generated `assessment_items` (`makeAssessmentItems`):**
  - **Before remediation:** `2,810` items
  - **Retained after remediation:** **`1,077`** items (`69` Syntax `rule_application`, `985` Cambridge `analysis` [`512` `example-*` + `473` `table-*`], `23` Cambridge `rule_application`; `0` duplicates)
  - **Rejected:** **`1,733`** items (`1,201` `concept_completion` + `360` `example-*` + `172` `table-*`)
  - **Still unreviewed:** All **`1,077`** generated `assessment_items` (and `1,071` `practice_items`) remain `review_status: 'UNREVIEWED'`, `independent_review: false`, `xp_policy: 'unscored-v2'` (no verified XP awarded).

---

## 5. Lessons-to-Quiz Coverage After Integration

- **Syntax (`syntax`):** `11` chapters, `50` assessable subtopics (`br-11/concepts` excluded per scope):
  - Topic Quizzes playable (`>= 5` validated items): `16 / 50` (`10` via `bank.json`, `6` via `rule_application`)
  - Partial (`1..4` items, accurately unavailable for 5-item Topic Quiz): `9 / 50`
  - Empty (`0` items, accurately unavailable): `25 / 50`
  - General Quizzes playable (`100%` subtopic coverage): `1 / 11` (`br-11`)
  - Master Quiz (`min = 11`, all 11 chapters covered) & Personalized Syntax Quiz: **Available**
- **Cambridge (`cambridge`):** `19` chapters (`cgel-ch01` Preliminaries excluded), `267` assessable subtopics:
  - Topic Quizzes playable (`>= 5` validated items): `84 / 267`
  - Partial (`1..4` items, accurately unavailable for 5-item Topic Quiz): `133 / 267`
  - Empty (`0` items, accurately unavailable): `50 / 267`
  - General Quizzes playable (`100%` subtopic coverage): `5 / 19` (`cgel-ch03`, `cgel-ch04`, `cgel-ch10`, `cgel-ch18`, `cgel-ch20`)
  - Master Quiz (`min = 19`, all 19 chapters covered) & Personalized Cambridge Quiz: **Available**
- **Integration with `origin/main`:** Verified in temporary merged clone `/tmp/quiz-v2-main-integration` that regenerating `syntax-practice-source.json` restores all `11` Syntax chapters / `50` topics with `0` Git merge conflicts across `web/index.html`, `web/css/style.css`, `web/js/main.js`, and `web/js/lessons-ui.js`.

---

## 6. Exact Test Commands and Results

All commands below were executed after the final code edit:

| Target | Command | Result |
|---|---|---|
| `feat/quiz-v2` | `npm run test:quiz-v2` (`test_quiz_digest_freshness.js`, `test_quiz_v2.js`, `test_quiz_lesson_practice.js`, `test_quiz_formal.js`, `test_quiz_v2_database.js`) | **PASS (exit 0)** — `1,077` validated assessment items, `100/317` playable topics (`217` accurately unavailable), `6` General quizzes, both Masters, all defective-template regression gates passed, PostgreSQL/PGlite RLS & forged-XP rejection passed |
| `feat/quiz-v2` | `node scripts/test_assessment_core.js && node scripts/test_level.js` | **PASS (exit 0)** — `16` blueprints/`120` variants, `1,000` level boundaries |
| `feat/quiz-v2` | `QUIZ_V2_PLAYWRIGHT_MODULE=/Users/kiyel/.npm/_npx/e41f203b7505f1fb/node_modules/playwright/index.mjs node scripts/test_quiz_v2_browser.js` (unsandboxed) | **PASS (exit 0, 0 page errors)** — Syntax/Cambridge tabs, Preliminaries exclusion, `br-03/concepts` disabled unavailable state, `br-02/worked-example` & `br-03/worked-example`, `cgel-ch04` General Quiz (`13` items), Syntax/Cambridge Master Quizzes, Personalized Syntax & Cambridge Quizzes, sidebar XP/Level, mobile/desktop dark/light |
| Merged `feat/quiz-v2` + `origin/main` (pre-regen) | `node /tmp/quiz-v2-main-integration/scripts/test_quiz_digest_freshness.js` | **FAIL (expected)** — caught `digest_mismatch` across `9` Syntax chapters / `40` topics |
| Merged `feat/quiz-v2` + `origin/main` (post-regen) | `npm run test:quiz-v2` + `node scripts/test_quiz_v2_browser.js` (unsandboxed, after `scripts/build_quiz_practice.js`) | **PASS (exit 0, 0 page errors)** — `50` Syntax sections captured against `origin/main` Lessons; all `5` Node/DB suites and Chromium E2E passed |
| `feat/quiz-v2` | `git diff --check` | **PASS (exit 0)** — no whitespace errors |

---

## 7. Remaining Blockers

1. **Human linguistic review & verified XP promotion (`P1`):** `1,077` generated assessment items remain `UNREVIEWED` (`xp_policy: 'unscored-v2'`), and `217 / 317` subtopics plus `24 / 30` chapter General Quizzes lack 5-item / full-subtopic coverage until qualified human-authored or independently reviewed questions are added (intentionally not padded).
2. **Post-merge regeneration workflow (`P0` operational step):** When `feat/quiz-v2` and `main` are eventually merged, `scripts/build_quiz_practice.js` must be run and `web/content/quizzes/syntax-practice-source.json` committed as part of the merge (now automatically enforced by `scripts/test_quiz_digest_freshness.js`).

---

## 8. Final Readiness Assessment

- **Technical / Template & Integration Remediation:** **COMPLETE** on `feat/quiz-v2`. Defective verb-splitting, leaky example distractors, broken table prompts, and silent stale-digest failures are eliminated, and `origin/main` integration compatibility is verified end-to-end.
- **Full Production Release Verdict:** **READY WITH RESTRICTIONS** (safe for unscored practice/assessment on the `100` playable topics, `6` General Quizzes, both Master Quizzes, and Personalized Quizzes, with `217` under-populated topics accurately gated as `Questions Under Review`; full 317-topic verified-XP launch still requires human linguistic authoring/review).
