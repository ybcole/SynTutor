# SynTutor Quiz V2 Final Readiness Report

- **Repository:** `/Users/kiyel/Desktop/SynTutor`
- **Branch:** `feat/quiz-v2` (`28891d77ca3acd9c964f4514171a485adb51727d`)
- **Reference:** `origin/main` (`0d879fc534dc834dc5d8fec7b82cdb730e52f8a1`), merge base `115b1dfc1bfda90697344d2a72d5e47ba7828782`
- **Audit Scope:** Read-only browser verification, 40-question linguistic audit against Lessons content, and `origin/main` integration check. No implementation code or Git state was modified.

---

## Final Verdict: **NOT READY**

The Quiz V2 UI, routing, scoping, randomization, personalization, local/DB isolation, and sidebar XP/Level integration work end-to-end in headless Chromium. However, the branch is **NOT READY** for production release or direct merge to `main` due to:
1. **Systemic template-level linguistic defects** across the 2,810 unreviewed generated items (`96.7%` of generated items come from three flawed templates exhibiting ungrammatical distractors, missing-context stems, lexical giveaways, and broken prompt phrasing).
2. **Unreviewed status** of all 2,810 generated items (`UNREVIEWED`, XP-ineligible; only 120 items in `web/content/quizzes/bank.json` are `INDEPENDENTLY_REVIEWED`).
3. **Silent merge breakage with `origin/main`:** `origin/main` edited `teach` prose in 10 of 11 Syntax pilot files, which invalidates `article_digest` in `web/content/quizzes/syntax-practice-source.json` and will silently drop generated Syntax items for 10/11 chapters unless regenerated.

---

## 1. Browser Testing Results (Priority 1)

- **Environmental restriction (sandboxed mode):** Running `scripts/test_quiz_v2_browser.js` inside the standard sandbox fails at `page.goto` with `net::ERR_ACCESS_DENIED at http://127.0.0.1:<port>/` because sandbox isolation blocks loopback socket connections from Playwright Chromium. This is an environment restriction, not an application defect.
- **Unsandboxed local Playwright run (`chromium` via `/Users/kiyel/.npm/_npx/e41f203b7505f1fb/node_modules/playwright/index.mjs`):**
  1. `node scripts/test_quiz_v2_browser.js` — **PASS (exit code 0, 0 page errors)**:
     - Verified `Syntax — Burton-Roberts` (11 chapters) and `Cambridge — Cambridge Grammar` (19 chapters, `Preliminaries` excluded even with poisoned offline cache).
     - Verified expandable chapters (`br-03`), Syntax topic quizzes (unreviewed and published `quiz-br-03`), draft persistence across reload, pre-submit isolation (no scores/answers/explanations), post-submit review, Syntax & Cambridge Master Quizzes (`min=19`, `25` items, `15` items, navigation, submission), and Personalized Syntax Quiz (excludes missed items).
     - Verified sidebar XP/Level updates on sign-in (`Level 2 · 250 verified XP`, `110 to next level`, `value="30"`) and sign-out (`Sign in for verified XP.`), plus `390px` and `1360px` `dark`/`light` themes with no horizontal overflow.
  2. **Supplemental browser check (General Quizzes, Cambridge Topic & Personalized Cambridge)** — **PASS (exit code 0, 0 page errors)**:
     - Verified Syntax General Quiz (`br-01`, 5 questions, answer selection + submission).
     - Verified Cambridge General Quiz (`cgel-clauses`, 16 questions + submission).
     - Verified Cambridge topic quiz (`cgel-ch04`, 5 questions + submission).
     - Verified Personalized Cambridge Quiz (5 questions + submission).

---

## 2. Linguistic Accuracy Audit (Priority 2)

### Pool Overview (`makeAssessmentItems` in `web/js/quiz-assessment-items.js`)
- **Total generated assessment items:** `2,810` (all `publication_status: 'assessment_draft'`, `review_status: 'UNREVIEWED'`, `independent_review: false`):
  - `syntax:concept_completion` (`explanation-*`): `255`
  - `syntax:rule_application` (`original-application-*` / `coordination-*` / `formal-application-*`): `69`
  - `cambridge:analysis` (`example-*`): `872`
  - `cambridge:analysis` (`table-*`): `645`
  - `cambridge:concept_completion` (`explanation-*`): `946`
  - `cambridge:rule_application` (`original-application-*` / `formal-application-*`): `23`
- Note: Only the 40 sampled questions below were audited; unreviewed questions remain unapproved.

### Shared-Template Defects Observed (with Full-Pool Measurements)

1. **`explanation-*` (`concept_completion`: 1,201 / 2,810 = 42.7% of generated items)**
   - *Source:* `sentenceFacts()` and `sectionQuestions()` in `web/js/quiz-lesson-practice.js`, rewritten in `web/js/quiz-assessment-items.js`.
   - *Mechanism:* Splits lesson prose at the first verb from a fixed list and borrows tails from other sentences in the same section as distractors.
   - *Confirmed defects:*
     - **Ungrammatical / syntactically mismatched distractors:** Because stems end with arbitrary verbs/modals (`is`, `can`, `does`, `takes`, `describes`) while distractors come from sentences split at different words, distractors frequently fail basic English grammar (seen in **12/15** sampled `concept_completion` items: `#1`, `#2`, `#3`, `#4`, `#5`, `#6`, `#8`, `#32`, `#33`, `#34`, `#36`, `#38`). Full pool includes `76` items with punctuation-leading options (e.g., `, so context matters.`).
     - **Missing context / unresolved anaphora:** Sentences extracted without preceding examples leave stems referring to absent text (`the same verb`, `“Three”`, `Vic`, `the same way`, `What licenses it`, `such things`; **7/15** sampled `concept_completion` items; `84` items in full pool begin with overt anaphoric/pronoun stems).
     - **Verbatim prose recall instead of grammatical understanding:** e.g., `#34` (`She didn’t have ____` → `lunch with my old man: she had lunch with my father.`).

2. **`example-*` (`analysis`: 872 / 2,810 = 31.0% of generated items)**
   - *Source:* `examples` block pairing in `web/js/quiz-lesson-practice.js` (lines 67–76).
   - *Confirmed defects:*
     - **Lexical giveaway distractors:** Distractors come from other examples' notes and often reference words not present in the prompt example (e.g., `#18` `speaking`/`rude` vs `Foolishly, he answered two questions`; `#20` `What a liar`/`How difficult` vs `what a mess ... told`; `#23` `Now`/`Soon` vs `a week ago`; `#15` `than`; `#16` passive when prompt is active). Seen in **6/10** sampled `example-*` items.
     - **Ambiguous / partially true distractors:** `#17` (`Elizabeth, your taxi is here.`) marks `Strong proper name with no determiner.` wrong, even though `Elizabeth` is in fact a strong proper name with no determiner.

3. **`table-*` (`analysis`: 645 / 2,810 = 23.0% of generated items)**
   - *Source:* `table` block pairing in `web/js/quiz-lesson-practice.js` + `web/js/quiz-assessment-items.js` (line 23).
   - *Confirmed defects:*
     - **Broken prompt interpolation:** Raw column names produce ungrammatical questions (`which what changes correctly fits` in `#25`, `which indirect object correctly fits` in `#26`; `38` items in the full pool match `which (what|how|why|when|where|whether)`).
     - **Binary 2-option items:** Tables with two distinct column values yield 50/50 guesses (`#30`; `51` items in the full pool have only 2 options).

4. **`rule_application` (`original-application-*`, `coordination-*`, `formal-application-*`: 92 / 2,810 = 3.3% of generated items)**
   - **8/8** sampled items (`#9`–`#14`, `#39`–`#40`) are linguistically accurate, self-contained, and aligned with their lessons (minor note: `#14` uses obviously incomplete fragments as distractors, tied to the coordination rule exercise).

### Sampled 40 Questions

| # | Track / Type | Item ID (Chapter / Subtopic) | Verdict | Key Finding vs Lessons Content |
|---|---|---|---|---|
| 1 | Syntax `concept_completion` | `lesson-assessment:br-02:application:explanation-27a04f9c:a7d0f47b:formal-1` | **DEFECT** | Distractors `b` (`an object...`) and `c` (`leave out...`) are ungrammatical after `the head ____`; prose recall. |
| 2 | Syntax `concept_completion` | `lesson-assessment:br-04:concepts:explanation-624b10c1:9ba24f34:formal-1` | **DEFECT** | Missing context (`the same verb`); plural distractors mismatch singular `is ____`. |
| 3 | Syntax `concept_completion` | `lesson-assessment:br-05:particles:explanation-9df22724:26996ffb:formal-1` | **DEFECT** | Answer starts with `, so context matters.`; distractors ungrammatical after `use ____`. |
| 4 | Syntax `concept_completion` | `lesson-assessment:br-06:chain:explanation-19a86151:12337b0d:formal-1` | **DEFECT** | Answer accurate, but distractor `c` (`a speaker connect...`) is ungrammatical after `is ____`. |
| 5 | Syntax `concept_completion` | `lesson-assessment:br-07:pre-modifiers:explanation-89182220:304d2aaa:formal-1` | **DEFECT** | Missing example (`“Three”`/`“glowing”`); ungrammatical distractor `b`; lesson meta-text in `c`. |
| 6 | Syntax `concept_completion` | `lesson-assessment:br-08:concepts:explanation-f19d3f52:15730852:formal-1` | **DEFECT** | Answer accurate, but both distractors are ungrammatical NP/fragment completions after modal `can ____`. |
| 7 | Syntax `concept_completion` | `lesson-assessment:br-10:concepts:explanation-c040e206:43c988ce:formal-1` | **MINOR** | Accurate against `br-10/concepts`, though `[them open the gate]` lacks its matrix clause (`Rae made...`). |
| 8 | Syntax `concept_completion` | `lesson-assessment:br-10:verb-complements:explanation-494340ee:7aefefa6:formal-1` | **DEFECT** | Unresolved reference to `Vic` (not in prompt); distractor `c` ungrammatical after `takes ____`. |
| 9 | Syntax `rule_application` | `lesson-assessment:br-02:worked-example:original-application-2:d7ff57f9:formal-1` | **PASS** | Accurate, self-contained, tests structural sisterhood under `S`. |
| 10 | Syntax `rule_application` | `lesson-assessment:br-05:ellipsis:original-application-0:1783a62f:formal-1` | **PASS** | Accurate, tests understood-recipient ellipsis with novel context. |
| 11 | Syntax `rule_application` | `lesson-assessment:br-08:worked-example:original-application-1:79f46596:formal-1` | **PASS** | Accurate, tests `S′` dominating `C` and `S`. |
| 12 | Syntax `rule_application` | `lesson-assessment:br-09:worked-example:original-application-0:8fe31ebf:formal-1` | **PASS** | Accurate, tests B-R `C2` under `S″` vs `C1` under `S′`. |
| 13 | Syntax `rule_application` | `lesson-assessment:br-09:relative-scope:original-application-1:4e5bf896:formal-1` | **PASS** | Accurate, tests non-restrictive relative attachment to full `NP`. |
| 14 | Syntax `rule_application` | `lesson-assessment:br-11:apply-the-rule:coordination-4:ea081f36:formal-1` | **PASS** | Accurate; distractors are incomplete fragments matching the lesson's rule test. |
| 15 | Cambridge `analysis:example` | `lesson-assessment:cgel-clauses:subordinate-clauses:example-9-1:6c13362a:formal-1` | **DEFECT** | Answer accurate, but distractor `c` mentions `than` (absent from `"the note she wrote"`). |
| 16 | Cambridge `analysis:example` | `lesson-assessment:cgel-ch04:objects:example-5-1:6f42d747:formal-1` | **MINOR** | Accurate; `b` is a strong distractor, while `c` (`passive subject`) does not match active prompt. |
| 17 | Cambridge `analysis:example` | `lesson-assessment:cgel-ch05:proper-names:example-4-3:a23cb155:formal-1` | **DEFECT** | Ambiguous distractor: `Elizabeth` in `"Elizabeth, your taxi is here."` is *also* a strong proper name with no determiner (`b`). |
| 18 | Cambridge `analysis:example` | `lesson-assessment:cgel-ch08:act-related:example-3-2:82b0f7cb:formal-1` | **DEFECT** | Lexical giveaway: prompt has `Foolishly`/`answered`; distractors talk about `rude`/`speaking to the husband`. |
| 19 | Cambridge `analysis:example` | `lesson-assessment:cgel-ch10:form-force:example-4-1:1ef55af6:formal-1` | **PASS** | Accurate with clean grammatical form/force contrast distractors. |
| 20 | Cambridge `analysis:example` | `lesson-assessment:cgel-ch11:exclamative-content:example-3-2:42b5f6cf:formal-1` | **DEFECT** | Lexical giveaway: distractors quote `"What a liar"` and `"How difficult"`, neither in prompt. |
| 21 | Cambridge `analysis:example` | `lesson-assessment:cgel-ch14:form-types:example-4-1:a6d8a470:formal-1` | **PASS** | Accurate minimal contrast (bare vs `to`-infinitival vs gerund-participial). |
| 22 | Cambridge `analysis:example` | `lesson-assessment:cgel-ch16:preposing:example-3-2:66260bfd:formal-1` | **PASS** | Accurate minimal contrast across preposing types. |
| 23 | Cambridge `analysis:example` | `lesson-assessment:cgel-ch17:temporal-deixis:example-3-3:ade8cc41:formal-1` | **DEFECT** | Lexical giveaway: distractors discuss `Now` and `Soon`, while prompt only has `ago`. |
| 24 | Cambridge `analysis:example` | `lesson-assessment:cgel-ch19:numerals:example-3-3:6aa10554:formal-1` | **PASS** | Accurate classification (numerical compound vs cardinal/ordinal), minor `year` cue. |
| 25 | Cambridge `analysis:table` | `lesson-assessment:cgel-clauses:information-packaging:table-4-0:b93eea96:formal-1` | **DEFECT** | Broken prompt phrasing: `which what changes correctly fits`. Content accurate. |
| 26 | Cambridge `analysis:table` | `lesson-assessment:cgel-ch04:objects:table-4-1:4a032f02:formal-1` | **DEFECT** | Awkward prompt phrasing (`which indirect object correctly fits` when asking its core status). |
| 27 | Cambridge `analysis:table` | `lesson-assessment:cgel-ch06:criterial-properties:table-3-2:06574e2a:formal-1` | **PASS** | Accurate and tests postpositive vs attributive/predicative function. |
| 28 | Cambridge `analysis:table` | `lesson-assessment:cgel-ch08:space:table-4-2:e3bf993e:formal-1` | **PASS** | Accurate spatial semantic role classification (`Endpoint` vs static/starting). |
| 29 | Cambridge `analysis:table` | `lesson-assessment:cgel-ch10:imperatives-directives:table-5-2:cbe69b4e:formal-1` | **PASS** | Accurate contrast in the section's form/use table (minor superordinate overlap between `Prohibition`/`Directive`). |
| 30 | Cambridge `analysis:table` | `lesson-assessment:cgel-ch14:finite-nonfinite:table-3-1:beecf18d:formal-1` | **MINOR** | Linguistically valid (subjunctive is finite), but only 2 options (`Finite` / `Non-finite`). |
| 31 | Cambridge `analysis:table` | `lesson-assessment:cgel-ch18:alternation-syncretism:table-4-3:d4b81544:formal-1` | **PASS** | Accurate, tests conceptual distinction for syncretism. |
| 32 | Cambridge `concept_completion` | `lesson-assessment:cgel-ch03:auxiliaries:explanation-adf9500e:a356b58c:formal-1` | **DEFECT** | Unresolved anaphora (`the same way`); both distractors ungrammatical after `Auxiliary have ____`. |
| 33 | Cambridge `concept_completion` | `lesson-assessment:cgel-ch06:adjp-complementation:explanation-04759b4a:79c50732:formal-1` | **DEFECT** | Unresolved `it`; `b` starts mid-idiom (`part, glad...`); `c` ungrammatical after `is ____`. |
| 34 | Cambridge `concept_completion` | `lesson-assessment:cgel-ch09:metalinguistic:explanation-8b07de83:e1d80e19:formal-1` | **DEFECT** | Verbatim example completion (`She didn't have ____`); nonsensical/ungrammatical distractors. |
| 35 | Cambridge `concept_completion` | `lesson-assessment:cgel-ch12:relativisation-gaps:explanation-23a9efc9:99029501:formal-1` | **MINOR** | Answer accurate, though `that element` is anaphoric and `b`/`c` are weak distractors. |
| 36 | Cambridge `concept_completion` | `lesson-assessment:cgel-ch15:coordination-overview:explanation-274f4963:386c9546:formal-1` | **DEFECT** | Unresolved `such things`; distractor `c` (`see you...`) ungrammatical after `is ____`. |
| 37 | Cambridge `concept_completion` | `lesson-assessment:cgel-ch17:special-it:explanation-bf15e3da:062bffe1:formal-1` | **DEFECT** | Distractor `c` (`the extraposed subject...`) is ungrammatical after `does ____`. |
| 38 | Cambridge `concept_completion` | `lesson-assessment:cgel-ch19:negatives:explanation-6932b944:22563187:formal-1` | **DEFECT** | Answer accurate, but both distractors are ungrammatical after modal `can ____`. |
| 39 | Cambridge `rule_application` | `lesson-assessment:cgel-ch07:preposition-style:original-application-3:2eff0fa6:formal-1` | **PASS** | Accurate, self-contained, tests non-compositional prepositional idioms. |
| 40 | Cambridge `rule_application` | `lesson-assessment:cgel-ch19:affixation:original-application-0:759e24e8:formal-1` | **PASS** | Accurate, self-contained, tests derivational category change. |

---

## 3. Integration Readiness (`feat/quiz-v2` vs `origin/main`) (Priority 3)

### Overlapping Modified Files (Both branches touched since merge base `115b1df`)
- `web/index.html`: Disjoint hunks (`feat/quiz-v2` adds `#sidebarProgress`; `origin/main` adds `#builderTopLeft` and removes `#generatorTreeOutline`). Should merge cleanly.
- `web/css/style.css`: Disjoint hunks (`feat/quiz-v2` adds `.sidebar-progress`; `origin/main` updates `.builder-top-left`/`.canonical-tree-view`). Should merge cleanly.
- `web/js/main.js`: Disjoint hunks (`feat/quiz-v2` adds `refreshSidebarProgress` and listeners; `origin/main` edits `showCanonicalTree`). Should merge cleanly.
- `web/js/lessons-ui.js`: Likely minor text conflict in the top `import` block (`feat/quiz-v2` removes pilot imports in favor of `./lesson-curriculum.js`; `origin/main` adds `./lesson-dictionary.js` nearby). Function edits (`onProgress` / `loadActiveCourse` vs dictionary wiring) are disjoint.

### Behavioral Impact from Newer `origin/main` Changes
- **CRITICAL — Syntax Practice Digest Invalidation:** `origin/main` edited `teach` content in **10 of 11** Syntax pilot files (`constituents-pilot.js`, `functions-pilot.js`, `categories-pilot.js`, `basic-vp-pilot.js`, `adverbials-pilot.js`, `noun-phrases-pilot.js`, `embedded-clauses-pilot.js`, `wh-clauses-pilot.js`, `non-finite-pilot.js`, `grammar-pilot.js` — all except `auxiliaries-pilot.js`). Because `web/js/quiz-lesson-practice.js` skips any Syntax chapter whose `article_digest !== syntaxPracticeDigest(chapter.id)`, merging with `origin/main` **without regenerating `web/content/quizzes/syntax-practice-source.json` via `scripts/build_quiz_practice.js` will silently drop generated questions for 10 of 11 Syntax chapters**, breaking Syntax topic quizzes, General Quizzes, Master Quiz, and Personalized Syntax Quiz.
- **No impact from `web/js/cambridge-chapter-lessons.js`:** `origin/main` changed `renderCheck` prose formatting in `cambridge-chapter-lessons.js`, which does not affect Quiz V2 because `quiz-lesson-practice.js` reads `web/js/cambridge-chapter-data.js` (unchanged on `origin/main`).

---

## 4. Prioritized Required Fixes

1. **[P0 — Integration Blocker] Regenerate `syntax-practice-source.json` upon merging/rebasing `origin/main`:** Rebase/merge `origin/main`, resolve the `web/js/lessons-ui.js` import block, and run `scripts/build_quiz_practice.js` so `article_digest` matches the updated Syntax `teach` prose for all 11 chapters.
2. **[P1 — Quality Blocker] Replace or overhaul automated question generation templates (`quiz-lesson-practice.js` & `quiz-assessment-items.js`):**
   - Retire or strictly gate the `sentenceFacts()` verb-splitting `concept_completion` generator (1,201 items) which creates ungrammatical distractors, punctuation fragments, unresolved anaphora, and prose-memory tasks.
   - Fix `example-*` distractors (872 items) to share grammatical category/vocabulary constraints rather than cross-example lexical giveaways or simultaneously true labels.
   - Fix `table-*` prompt formatting (645 items) so column headers never interpolate as `"which what changes..."`, and filter or expand 2-option tables.
3. **[P1 — Requirement Blocker] Complete human linguistic review & verified XP promotion:** Review and approve items (moving beyond the 120 `INDEPENDENTLY_REVIEWED` items in `web/content/quizzes/bank.json` to cover all 317 topics), then enable verified server XP once reviewed blueprints are published.
4. **[P2] Extend `scripts/test_quiz_v2_browser.js`:** Add explicit assertions for Syntax/Cambridge General Quizzes, Cambridge topic quizzes, and Personalized Cambridge Quiz, and run the Playwright suite in CI outside loopback-restricted sandboxes.
