# Syntax Foundations lesson implementation plan

## Next implementation: Chapter 2

Polish **Lessons → Syntax Foundations → Subject, predicate and category**
(`br-02`) on `explore/foundations-lesson-rollout-plan`. Use the live Chapter 1
experience as the template for reading, interaction, and assessment. Write
Chapter 2 around its own example and learning outcome. The earlier Chapters
3–11 presentation rollout is complete ([`f2e7720`](https://github.com/ybcole/SynTutor/commit/f2e7720a5ec939c42b828be052466f7b93bf8621)).
This pass targets Chapter 2. Use Chapter 1 and the rest of the course to check
shared behavior. The Chapter 1 reference reviewed for this plan is
[`dafb179`](https://github.com/ybcole/SynTutor/commit/dafb17961e32ee898324b167a0a3d9d48d27ea9e).
Since Chapter 1 is still being polished, walk both chapters on the branch tip
when starting implementation and use the latest Chapter 1 interaction details.

### Read in this order

| Source | What it governs |
| --- | --- |
| [Original master plan](master_plan.md#recommended-lesson-sequence), [Prompt 04](syntutor_12_prompt_execution_plan.md#04--lessons-and-curriculum), [M4 brief](master_prompt_lessons.md), [M4 launch curriculum](../curriculum/README.md), and [M4 acceptance](../reports/milestone-04-acceptance-2026-11-08.md) | Keep the sequence of diagnostic, instruction, worked analysis, guided practice, transfer, and exit check. Keep one assessed outcome, source-backed examples, and versioned completion. |
| [B-R edition manifest](../../sources/burton_roberts/source_manifest_2026-11-08.json), [M4 B-R receipt](../../sources/burton_roberts/reviews/2026-11-08-lessons.json), [conventions](../../CONVENTIONS.md#ch2--functions-v2), and [Chapter 2 book tree records](../../web/content/book/ch02.trees.json) | Verify the edition, printed pages, comparison figure, and labels. The book tree data is structured source evidence. |
| [Course JSON](../../web/content/lessons/course.json), [course schema](../../web/content/lessons/course.schema.json), and [progress contract](../curriculum/progress-and-deployment.md) | Find the published lesson, reviewed text, example, assessed questions, prerequisites, citations, and progress contract. |
| [Chapter 1 presentation](../../web/js/constituents-lesson.js), [Chapter 1 Builder exercise](../../web/js/constituent-tree-builder.js), [Chapter 2 presentation](../../web/js/subject-predicate-lesson.js), [shared lesson UI](../../web/js/lessons-ui.js), and [lesson CSS](../../web/css/lessons.css) | Compare the rendered pages and find reusable components. Chapter 2 currently has a single opening prediction and a Builder link that leaves the lesson. |
| [Worked example](../../web/js/foundations-lesson.js), [notation guide](../../web/js/lesson-notation.js), [Builder UI](../../web/js/syntax-builder-ui.js), and [M6 acceptance](../reports/milestone-06-acceptance-2026-11-08.md) | Reuse the existing canvas, notation, Builder lifecycle, and reviewed Chapter 2 construction target. |

## What Chapter 2 teaches

Use Noel Burton-Roberts, *Analysing Sentences*, 3rd ed. (Pearson, 2011,
ISBN 9781408233740). Chapter 2, **Sentence structure: functions**, spans printed
pp. 24–45. Its opening builds on Chapter 1 by moving from identifying groups
to asking what kind of group each is and what job it does. Read the
[third-edition reference copy](https://lmsspada.kemdiktisaintek.go.id/pluginfile.php/1032828/mod_resource/content/2/Introduction%20to%20English%20Syntax.pdf)
by printed page. Subject and predicate begin on p. 24, NP and VP on p. 29,
and dependency on p. 31. The reviewed launch scope is the basic split from
pp. 29–30. Use the chapter opening as a teaching model and leave dependency,
head–modifier and head–complement relations, and subject diagnostics for a
separately reviewed expansion. If the book is unavailable during implementation,
work from the existing reviewed evidence and report which claims and pages
were actually checked.

- The single assessed outcome, `o1`, is to identify subject and predicate from
  the immediate NP/VP split under S. Begin with a familiar sentence, ask learners
  to find the groups, then introduce **function** as the job a group does in this
  structure and **category** as the kind of group it is. Use short sentences and
  explain abbreviations on first use. Say “in this basic pattern” when drawing a
  generalization. Use position in the tree to explain the answer.
- Carry **The robins sing** from the introduction through instruction, worked
  diagram, and build. In V2, **S** covers the sentence. Its two direct children
  are **NP** over *The robins* and **VP** over *sing*. These sisters function as
  subject and predicate in this pattern. Put function names in captions or
  explanatory annotations. Keep the NP and VP triangles in the canonical model
  and explain that a triangle leaves the phrase's internal branches out of view.
  A phrase can contain one word here. Keep later category and feature labels
  out of the Chapter 2 teaching and construction palette.
- Use the source comparison `ch2-33` (p. 30, fig. [33]) to check the V2 shape.
  The book's example and function annotations are source evidence. SynTutor's
  original example is `lesson-br-02-worked` in the catalog and drives the lesson
  and its assessment. Use original teaching and question wording.
- Keep the reviewed **Cambridge insight** short and cited to CGEL pp. 44–45.
  It distinguishes the sentence as a unit of text from the clause as a unit
  of syntax and notes that clauses can be embedded. Keep `cgel-sentence-clause`
  and the existing source IDs. Use the insight as terminology context under
  [source governance](../source-authority-matrix.md). B-R governs the tree
  shape and labels. Keep the Cambridge companion lesson and runtime rules
  outside this implementation.

## Six pages for the learner

The headings below describe the proposed sequence. Use Chapter 1's compact
typography, single reading column, bottom Previous/Next navigation, and focus
behavior. The six reading pages map onto the existing M4 saved stages. The
construction and application pages can share the worked checkpoint.

| Page | Teaching and interaction | Reuse and boundaries |
| --- | --- | --- |
| 1. Introduction to subject and predicate | Bridge from finding groups in Chapter 1 to identifying their jobs. In **What this chapter covers**, ask learners to read *The robins sing* and find its two parts. Preview reading and building the top split. End with **Check what you know**. | Three unscored items in one rounded panel, one at a time. Use the reviewed `predict` as item 1 and add two original low-stakes prompts about grouping and what the predicate tells us. Any choice can advance each item. |
| 2. Finding the subject and predicate | Start with *The robins* and *sing*, then show a bracketed split or simple selectable sentence strip. Ask which words each group contains and what each group does. Introduce category versus function with the same example. | Render the ideas from the reviewed `teaching` paragraph in short, source-linked blocks while keeping the catalog record intact. Teach the distinction before asking the learner to build. |
| 3. Reading and building the NP/VP tree | Follow **Whole sentence → Subject → Predicate** in the authored tree. Ask learners to select each branch and trace which words it covers. Beneath it, build the same sentence in an editable canvas using optional guidance. | Reuse the three authored steps and focus IDs, the canonical tree, the Chapter 1 canvas treatment, and the reviewed M6 target. Place the small **Tree notation** guide near the diagram. Introduce S, NP, VP, and the triangle there. |
| 4. Applying the split | Give learners one short, ungraded practice sentence with a multiword predicate, for example *The lanterns glow at night*. Ask them to identify the whole VP and explain why the immediate NP is the subject in the model. Reveal the explanation after the attempt. Put the brief **Sentence and clause** Cambridge insight here as supporting context. | Use an original, source-aligned example checked against V2 and `o1`. If shown as a tree, use authored NP and VP triangles. Keep the stored transfer and exit examples for the closing check. |
| 5. Chapter recap | Summarize how to find the direct NP and VP under S, explain category and function, and read a triangle. Give a short procedure learners can use on a new sentence. Include **References and source review**, then **Check what you learned**. | Use the catalog citation resolver. Identify what the B-R and Cambridge references support. |
| 6. Check what you learned | Present the existing guided, transfer, and exit questions one at a time in a single rounded panel. Show question count and feedback. **Next question** advances within the panel. After completion, **Answers overview** shows all three answers and their feedback. | Keep the published scoring and guided tree blank. Match Chapter 1's larger radio buttons and alternating option rows. Keep question navigation inside active checks and practice retakes. Offer **Try the questions again** and **Finish review** from the completed overview. |

Use the site font, neutral thin branches, and covered-word highlighting in the
worked diagram. Put selected words above the short authored caption. The
expandable **Explanation** can use the existing shared evidence service with
the canonical tree and focused node. Keep the authored caption readable when
evidence is unavailable. Place step controls immediately above the diagram on
mobile and keep zoom in the existing location. Follow Chapter 1's visible
controls and keep the accessible tree outline and keyboard selection available.

### Embedded construction on page 3

1. Use `mountEmbeddedBuilder` and the existing Syntax Builder canvas, with
   **Guide me** and **Check construction** above it. Seed *The*, *robins*, and
   *sing* in order. Let learners add and edit nodes and branches directly. Keep
   the embedded view compact, with the canvas's existing edit affordances and
   keyboard/touch support.
2. Reuse the inline guide pattern from Chapter 1. Reveal all four numbered,
   clickable rows at once, with neutral text and visible hover/focus. Suggested
   actions are **Add S, NP and VP**, **Attach NP and VP under S**, **Attach the
   words to their phrases**, and **Collapse both phrases and check**. Support
   missing or ambiguous prerequisites with concrete feedback. Guide actions
   should be repeatable and preserve unrelated manual work. Use the existing
   Builder model operations for manual and guided edits.
3. Check against the authored `br-02` target using the existing target comparison
   where applicable. Inspect how the embedded and standalone paths validate
   before wiring it. Use the reviewed canonical target and existing comparison
   rules as the source of truth. Check the root, ordered sister branches, phrase
   spans, and expected V2 triangle representation. Explain which part needs
   attention. Keep the exercise ungraded and skippable. Keep grading of the
   separate M4 label-fill question in the closing check.
4. Keep **Try in Syntax Builder** after the inline exercise as an optional
   full-workspace link. Verify **Return to lesson** takes the learner
   to the worked page. Navigation, remount, and workspace switching should clean
   up the embedded canvas and keep its state isolated from Chapter 1 and the
   learner's standalone draft. Record the embedded exercise's draft behavior.

## Implementation sequence and data boundaries

1. **Audit the branch and baseline.** Open both chapters in the browser. Trace
   `articleLessons`, the article renderer, the existing knowledge-check code,
   and the Builder entry points. Check the current browser tests for Chapter 2's
   old labels and handoff before updating their expectations.
2. **Map the data before writing copy.** In `course.json`, locate `br-02`,
   `o1`, the V2 convention, `tree_ids`, `teaching`, `worked_example`,
   `cambridge_insights`, `predict`, `guided`, `transfer`, `exit`, and
   `completion`. Resolve the B-R source IDs `BR-3E-P29` and `BR-3E-P30`
   and Cambridge IDs `CGEL-2002-CH02-P0044` and `CGEL-2002-CH02-P0045`
   through the course's source registry. Keep the canonical envelope's tokens,
   IDs, spans, triangles, step focus IDs, source metadata, and accepted
   alternatives. `ch02.trees.json` is the book comparison inventory.
   `course.json` is the published lesson and answer contract.
3. **Build the reading pages.** Keep the reviewed catalog as the primary data
   source. Put page headings, short bridging copy, supplemental ungraded prompts,
   and canvas controls in the Chapter 2 presentation layer, following the
   existing Chapter 1 pattern. Reuse shared components where both chapters need
   them. Keep the lesson ID, version, `br-01` prerequisite, published question
   IDs, and answer contract stable for this presentation pass. A future change
   to reviewed catalog content requires checking the source review/hash and
   versioned seed workflow. A changed published answer key requires a new
   content version with a reviewed server seed and historical version support.
4. **Wire the Builder and assessments.** Use the in-lesson canvas and guide.
   Reuse the Chapter 1 question flow with Chapter 2-specific instructions.
   Keep the first opening answer compatible with the saved `predict` choices
   and the single server prediction response. Extra opening responses are
   presentation-only. Match Chapter 1's identity- and version-scoped draft
   behavior and recognize an already saved prediction as a completed opening
   check. Preserve the `guided → transfer → exit` answer requirements,
   focus on question changes, masking of the guided answer, saved response
   feedback, and practice-only state.
5. **Check progress and scope.** Existing records at prediction, instruction,
   worked example, or any closing question must still resume at the applicable
   page or question. Preserve completed answers, prerequisite enforcement,
   local/account isolation, and one-time 15 XP. Keep reading available under the
   current access rules. Use authored trees for instruction and assessment.
   Keep independent quizzes, the Generator, and production migrations outside
   this pass.

## Verification and handoff

- Run `python3 scripts/validate_lessons.py`, `npm run test:lessons`,
  `npm run test:builder`, `python3 scripts/test_lessons_browser.py`, and
  `python3 scripts/test_builder_browser.py`. Update the existing browser
  regression for the new Chapter 2 sequence and use the existing suites to
  check shared paths. Run `python3 scripts/validate_builder_contracts.py`
  if the target integration changes.
- On desktop and mobile, check all six pages, keyboard focus, tree selection,
  notation, feedback, and light/dark contrast. Build manually and with the guide.
  Try incorrect branch placement and missing nodes, then correct them. Check
  that the canvas fits on mobile and that controls stay close to it.
- Reload partway through the opening check and each closing stage. Verify a
  pre-revision saved prediction and a saved closing response still carry over.
  Complete the lesson, confirm the overview shows three saved answers with no
  question-navigation control, then take a practice retake and check that the
  saved answers and XP remain intact. Confirm the guided blank is masked in
  both the visual and accessible tree until the correct response.
- Walk Chapter 1 and representative shared paths in the remaining course,
  including a feature blank, typed gap, and the Chapter 11 text-only lesson.
  Confirm the standalone Builder still works and retains its draft.
- Report the commit, changed files, source pages actually consulted, checks
  run and their results, and any differences from this plan. Distinguish local
  verification from hosted or signed-in verification.

## Prompt to paste next

> On `explore/foundations-lesson-rollout-plan`, read
> `docs/planning/syntax_foundations_lesson_rollout.md` and its linked M4 and
> source records. Implement the Chapter 2 revision only. Walk the latest
> Chapter 1 first and match its six-page reading flow, compact canvas and
> clickable guide, recap, and one-question-at-a-time knowledge checks. Teach
> from the reviewed Chapter 2 V2 outcome and authored *The robins sing* tree.
> Keep the Cambridge note as cited context and preserve existing assessments,
> progress, and XP. Run the verification checks and report the commit and
> anything that needs my review.

## Owner review after implementation

1. Try Chapter 2 as a new learner on desktop and mobile. Check that the opening
   example carries naturally into the tree and that you can explain why **NP**
   names a category and **subject** names its job in that tree.
2. Build *The robins sing* once by hand and once with **Guide me**. Try a wrong
   attachment to see whether the feedback helps you fix it. Check that the
   triangles make sense after you have attached the words.
3. Complete the closing check, reopen the lesson, and try a practice retake.
   Check the answers overview, completion badge, and XP. If an account preview
   is available, test signed-in resume there as well.
4. Send the next revision prompt the branch or commit, page heading, exact
   wording or interaction you want changed, and a screenshot when layout is the
   issue. Once you have reviewed Chapters 1 and 2 together, decide which polish
   patterns to carry into Chapters 3–11. Use a separate source-reviewed pass if
   you want to expand Chapter 2 into dependency or head relationships.
