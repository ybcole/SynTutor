# Syntax Foundations lesson implementation plan

Use the current Chapter 1 and Chapter 2 on `explore/foundations-lesson-rollout-plan`
as the reference for revising one chapter at a time. Chapter 1 shows how to
introduce a concept through an example and a short exercise. Chapter 2 shows
how to carry that approach through a longer explanation, a worked comparison,
a guided build, and an independent application.

## Read before writing

| Source | What to check |
| --- | --- |
| [Master plan](master_plan.md#recommended-lesson-sequence), [Prompt 04](syntutor_12_prompt_execution_plan.md#04--lessons-and-curriculum), [M4 brief](master_prompt_lessons.md), [M4 launch curriculum](../curriculum/README.md), and [M4 acceptance](../reports/milestone-04-acceptance-2026-11-08.md) | Find the reviewed outcome, prerequisites, scope, teaching sequence, and completion contract for the target chapter. |
| [B-R edition manifest](../../sources/burton_roberts/source_manifest_2026-11-08.json), [source review receipt](../../sources/burton_roberts/reviews/2026-11-08-lessons.json), [conventions](../../CONVENTIONS.md), and [book tree records](../../web/content/book/) | Identify the edition, printed pages, source figures, and chapter-specific labels. Read the relevant sections of [Analysing Sentences, 3rd ed.](https://lmsspada.kemdiktisaintek.go.id/pluginfile.php/1032828/mod_resource/content/2/Introduction%20to%20English%20Syntax.pdf) by printed page. |
| [Course JSON](../../web/content/lessons/course.json), [course schema](../../web/content/lessons/course.schema.json), and [progress contract](../curriculum/progress-and-deployment.md) | Locate the published lesson, canonical example, assessment answers, references, saved stages, and XP. |
| [Chapter 1 presentation](../../web/js/constituents-lesson.js), [Chapter 2 presentation](../../web/js/subject-predicate-lesson.js), [shared lesson UI](../../web/js/lessons-ui.js), and [lesson CSS](../../web/css/lessons.css) | Walk both chapters at the branch tip. Check their typography, reading order, navigation, worked diagrams, and knowledge checks. |
| [Embedded tree exercise](../../web/js/lesson-tree-exercise.js), [Chapter 2 Builder exercises](../../web/js/subject-predicate-builder.js), [Builder UI](../../web/js/syntax-builder-ui.js), [notation guide](../../web/js/lesson-notation.js), and [M6 acceptance](../reports/milestone-06-acceptance-2026-11-08.md) | Find the chapter's approved target and reuse the editor lifecycle, profile, guide, and feedback. |
| [Source authority matrix](../source-authority-matrix.md) | Use Burton-Roberts for the tree analysis and notation. Use Cambridge for cited grammatical context that answers a question raised by the lesson. |

Before editing, map each topic to a printed page or figure, the M4 outcome
it supports, a learner decision, an original example, and the feedback that
will help after a common error. Use the book's teaching sequence and write
the examples and explanations in SynTutor's own words. If a source page
cannot be checked, report that gap and use the reviewed evidence for the
affected section.

## Six-page lesson template

| Page | What the learner does | What the page needs |
| --- | --- | --- |
| 1. Introduction and opening check | Recall an idea from the previous chapter. Make a prediction about one short example and reveal the explanation. | A brief **What this chapter covers**, one example that introduces the concept, and a compact **What you’ll see in this chapter** preview that also serves as the learning outcomes. Save longer contrasts and explanations for the teaching pages. End with three unscored questions shown one at a time, with the reviewed prediction as the saved first response. |
| 2. Core concepts | Work through the book's reasoning using the chapter's example and a contrasting example. Try a diagnostic or decide between two analyses. | Several descriptive subheadings. Under each, explain one idea in short paragraphs, show which words or branches provide evidence, and give feedback on a likely misunderstanding. Keep the essential explanation visible and use disclosures for answers and extra detail. |
| 3. Worked analysis and guided construction | Read a tree from a meaningful starting node. Trace the words and compare the same relationship in another example. Build or edit the part that demonstrates the concept. | An authored canvas, a nearby notation guide, and short captions explaining the relation. For tree construction, place the editable canvas with **Guide me** and **Check construction** in the lesson. Match the scope of the construction task to the chapter's outcome. |
| 4. Apply the concept | Compare a pair of sentences or analyse a new one. Explain which evidence supports the decision, then practise the relationship again. | A new example that requires the same reasoning, feedback that explains the result, and a worked reveal. If the application asks learners to build, provide a second guided editor on this page with its own draft. |
| 5. Recap and self-check | Use a short procedure to analyse a fresh example, then check the answer. | A reusable procedure, a short explanation of what learners commonly confuse, an example with a reveal, and references. A Cambridge note may go here or beside a relevant example. Pair it with the chapter's own analysis when it helps answer a question. |
| 6. Closing knowledge check | Complete the reviewed questions one at a time, then read the full answers overview. | An optional unscored warm-up where it helps, followed by the existing graded contract. Include question count, feedback, and active question navigation. Completed review shows all answers, and a practice retake uses temporary responses. |

Write for English learners. Use familiar examples, short sentences, and
explicit referents such as “the NP under S” and “the words near the gate”.
Define abbreviations on first use. Introduce a concept in words before
using its tree label as an answer choice. Give each main topic page enough
visible explanation for a learner to follow the reasoning before interacting.
A useful section moves from a question to an example, then explains what
the example shows and gives the learner a decision to make. Use diagrams,
sentence pairs, brackets, and short practice prompts to break up reading.
A terminology note alone is too little for a topic page. Cambridge can
clarify a distinction within a page that already teaches the B-R concept.
Before each worked figure, name the sentence, connect the figure to the
preceding explanation, and tell learners which words or branches to trace.
Explain unfamiliar symbols before asking learners to use the diagram.

Use at most two multiple-choice questions across the teaching pages. Reserve
them for choices where each plausible answer reveals a different misunderstanding.
For other practice, let learners select a word boundary, trace a branch,
edit a tree, or say or write an analysis and reveal the explanation. Give
feedback that points to the relevant words or branches. This limit applies
to practice inside the content. The opening and closing knowledge checks
use their existing question flow.

## Chapter 2 reference implementation

Chapter 2 covers the immediate NP and VP under S in the basic V2 pattern.
Burton-Roberts introduces the subject–predicate split on printed pp. 24–28,
then noun and verb phrases, category versus function, and triangles on
pp. 29–31. Figure [33] (stored as `ch2-33`) supports the shape of the authored
catalog tree. The reviewed M4 outcome `br-02/o1` assesses the top-level split.
The launch curriculum lists pp. 29–30 as the reviewed evidence for that
outcome. The surrounding pages can inform examples and explanations, while
broader objectives such as head and dependent relationships belong to the
later coverage already mapped in the curriculum.

| Page | Implemented teaching sequence |
| --- | --- |
| Introduction | Bridge from word groups to their jobs. Use *The robins sing* to introduce subject and predicate, then preview finding, reading, and building the two groups. |
| Finding the subject and predicate | Show how *every morning* extends the predicate. Then select the last word of the subject in *The robins near the gate are singing softly*. Use a yes/no question and pronoun replacement to check the full subject. Explain NP and VP, and show a predicate that describes a state. |
| Reading and building the NP/VP tree | Compare the two trees and trace the span of a branch. Explain sister nodes and the purpose of the triangles. Build the short example in the lesson and use the longer canvas for a branch-selection check. |
| Applying the split | Use the lesson’s one multiple-choice item to compare *The robins sing* with *Maya watched the robins*. Open a close-up to see the NP within the VP. Build *The gate by our house is open* in a second embedded editor, using a separate draft. |
| Chapter recap | Use a short procedure and a fresh example, *The lights in the hall were bright*. Apply the Cambridge sentence–clause distinction to two examples as a cited note. |
| Closing check | Offer a short open-response warm-up with a reveal, followed by the three reviewed M4 questions. |

Chapter 2 uses the yes/no question as a way to find the group in the
corresponding statement. The tree task stays on the statement. Later
relationships such as dependency and the full analysis of heads, modifiers,
and complements can be introduced at the curriculum points that teach them.
The Cambridge note uses CGEL pp. 44–45 as terminology context and retains
the catalog references for `cgel-sentence-clause`.

## In-lesson tree construction

1. Reuse the existing Syntax Builder canvas through `addEmbeddedTreeExercise`
   and `mountEmbeddedBuilder`. Keep the compact lesson controls and the
   existing keyboard and touch editing. Place the task, canvas, and feedback
   together on the same page, so the learner can continue reading and move
   between lesson pages with the normal navigation.
2. Offer **Guide me** above the canvas. Reveal the clickable steps together.
   Each step should describe what the learner will see and apply that edit.
   A typical sequence is add the nodes, connect the main branches, attach
   the words, and check the required notation. Let learners edit freely
   before or after using the guide. Explain missing prerequisites or
   conflicting manual edits in the feedback.
3. Check the structure against the intended chapter profile and task. For
   V2 this includes the root, order of the NP and VP, complete word spans,
   and triangles. Keep construction unscored when it is lesson practice.
   Teach the intended relation in the feedback, including how to repair
   a misplaced branch.
4. The embedded editor shares one canvas with the standalone Builder.
   Mount one editable exercise per lesson page. Use different exercise IDs
   for different targets, and keep existing IDs stable when preserving
   drafts. Verify that moving between the worked and application pages
   restores each draft and that normal standalone use retains its own draft.
5. Use the read-only authored diagram for tracing and inspection. Reuse the
   word highlighting, keyboard selection, accessible outline, and neutral
   branch styling. Keep feedback and notation beside the diagram. For a
   text-only outcome, such as Chapter 11's use of rules, use an application
   activity that fits that objective.

## Catalog and progress boundaries

Keep the reviewed outcome, published examples, source IDs, question IDs,
answers, prerequisites, and progress contract in the course catalog.
Chapter-specific presentation can add source-linked explanations, original
supplemental examples, and ungraded interactions, following Chapters 1 and 2.
Keep book tree records as source evidence and use the reviewed catalog target
for scored work. A change to reviewed catalog content needs the source
review, receipt, and seed workflow. Changing a published answer key requires
a new content version with historical version support.

Keep the saved opening prediction compatible with the existing options and
the single server response. Keep the graded `guided → transfer → exit` flow,
guided-label masking, resume, answers overview, and one-time XP. Verify that
new practice and draft edits leave assessment progress intact.

## Verification and handoff

- Run `python3 scripts/validate_lessons.py`, `npm run test:lessons`,
  `npm run test:builder`, `python3 scripts/test_lessons_browser.py`, and
  `python3 scripts/test_builder_browser.py`. Run
  `python3 scripts/validate_builder_contracts.py` if the target contract changes.
- Walk the target chapter on desktop and mobile. Check that learners can
  follow every explanation, distinguish examples from prompts, operate the
  canvas with keyboard or touch, and repair an incorrect attempt. Check
  the in-lesson draft on revisiting the page and exercise in light and dark.
- Resume each assessment, complete the chapter, inspect the answers overview,
  and try a practice retake. Check that older saved responses and XP carry
  forward and that hidden labels stay masked in the visual and accessible
  tree. Check shared behavior in Chapters 1 and 2 and the standalone Builder.
- Report what changed, which source pages were consulted, the commit and
  verification results, and what requires learner, hosted, or signed-in review.

## Prompt to paste for the next chapter

> On `explore/foundations-lesson-rollout-plan`, revise Syntax Foundations
> Chapter [number] using `docs/planning/syntax_foundations_lesson_rollout.md`.
> Walk the latest Chapters 1 and 2, then read the linked M4 plan, catalog,
> conventions, and the relevant printed pages and figures in Burton-Roberts.
> Write a six-page lesson with multiple readable teaching sections, a
> sustained example, at least one contrast that exposes a likely error, a
> worked analysis, fresh application, recap, and the existing closing check.
> Keep the introduction to one example and a short learning preview. Use at
> most two multiple-choice questions inside the teaching content, and use
> direct interaction or short open-response practice for the other activities.
> Place any tree-building activity directly in the lesson using the existing
> editable canvas with an optional clickable guide. Keep Cambridge as cited
> context within the teaching. Preserve the reviewed assessment and progress
> contract. Run the verification checks and report the commit, source pages,
> and specific items for me to try.

## Owner review

Review one chapter at a time. First read it as a learner and try the new
example before opening any answer or guide. Then complete the construction
both manually and with the guide, and try the closing check and a retake.
Send the page heading, example or instruction that needs revision, and a
screenshot when the issue is visual. Start with Chapter 3 after reviewing
the expanded Chapter 2 experience.
