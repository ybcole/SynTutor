# Syntax Foundations lesson implementation plan

Use Chapters 1–5 on `explore/foundations-lesson-rollout-plan` as the reference
for revising the remaining chapters. Chapters 1 and 2 establish the flow.
Chapters 3–5 show how to use the same flow to teach a specific attachment
with a partially built tree.

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

Use the printed Burton-Roberts text for the linguistic explanation. Use
`web/content/book/chXX.trees.json` to check the selected source analyses
and figure notation. Use `course.json` for the reviewed SynTutor example,
assessment, and provenance. The supplemental prose, examples, and practice
are authored for SynTutor and should be checked against those sources and
the chapter profile. Use the existing lessons and owner feedback to guide
the teaching format. Use Cambridge only for relevant, cited grammatical
context.

## Six-page lesson template

| Page | What the learner does | What the page needs |
| --- | --- | --- |
| 1. Introduction and opening check | Recall an idea from the previous chapter and read one short worked example. | A brief **What this chapter covers**, one visible example with its explanation, and a compact **What you’ll see in this chapter** preview. Save longer contrasts for the teaching pages. End with three unscored questions shown one at a time, with the reviewed prediction as the saved first response. |
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
Show worked examples and explanations directly in the lesson. Use a single
optional reveal for a practice answer when seeing it early would give away
the task. Keep the prompt visible.

Use at most two multiple-choice questions across the teaching pages. Reserve
them for choices where each plausible answer reveals a different misunderstanding.
For other practice, let learners select a word boundary, trace a branch,
edit a tree, or say or write an analysis and reveal the explanation. Give
feedback that points to the relevant words or branches. This limit applies
to practice inside the content. The opening and closing knowledge checks
use their existing question flow.

## Chapter 1 reference implementation

The launch outcome `br-01/o1` asks learners to trace all and only the words
of a constituent. The reviewed catalog cites printed pp. 16–17. The teaching
pages draw on the chapter’s wider treatment of grouping, evidence and ambiguity.

| Page | Implemented teaching sequence |
| --- | --- |
| Introduction | Use the bicycle analogy and *We met near the quiet garden* to introduce groups within groups. Preview replacement, questions, tree reading, and ambiguity before the opening check. |
| Identifying constituents | Keep the garden sentence for a successful replacement, an incomplete replacement, and two questions that pick out different-sized groups. Show the same groups with brackets and selectable highlighting. |
| Comparing flat and nested trees | Use the same four words in both drawings. Ask whether one node covers exactly *the quiet garden*. Then build the inner group in *beside the red gate* in the embedded canvas. |
| Structural ambiguity | Switch between two attachments of *with a telescope*. Ask who had the telescope and connect the answer to the highlighted group. |
| Recap and closing check | Recap the evidence and the all-and-only test. Use the reviewed check and offer optional open-response practice during review. |

The Chapter 1 builder starts with the words attached to the outer phrase.
Learners add one inner grouping and see which words it reaches. The
`PHRASE-a` and `PHRASE-b` guide labels are local placeholders. This exercise
checks grouping and word order, so the same grouping can succeed with
different placeholder labels. Chapter 2 introduces the V2 categories and
checks those labels as part of its own tasks.

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
| Introduction | Introduce subject and predicate as jobs in a simple statement and use *The robins sing* to distinguish those jobs from the noun phrase and verb phrase categories. Preview finding, reading, and building the two groups. |
| Finding the subject and predicate | Preview the ways to check the split. Show how *every morning* extends the predicate, then let learners mark the last word of the subject in the longer sentence. Present the yes/no question, pronoun replacement, and return to the original statement as a bulleted worked procedure. |
| Reading and building the NP/VP tree | Explain sister nodes and triangles, then demonstrate tracing on the short tree. **Try the longer sentence** switches the same read-only canvas to a predicate check, with the prompt beside the diagram and feedback after a node selection. Build the short example in the editor below. |
| Applying the split | Use the lesson’s one multiple-choice item to compare *The robins sing* with *Maya watched the robins*. Trace the highlighted NP within the VP in the visible figure. Build *The gate by our house is open* in a second embedded editor, using a separate draft. |
| Chapter recap | Reuse the subject–predicate procedure on a fresh example, *The lights in the hall were bright*. |
| Closing check | Offer a short open-response warm-up with a reveal, followed by the three reviewed M4 questions. |

Chapter 2 uses the yes/no question as a way to find the group in the
corresponding statement. The tree task stays on the statement. Later
relationships such as dependency and the full analysis of heads, modifiers,
and complements can be introduced at the curriculum points that teach them.
The Cambridge sentence–clause distinction is covered by the companion
lesson `cgel-clauses`. The Chapter 2 recap focuses on the split learners
will use in the closing check. The reviewed catalog retains its source links.

## Polishing decisions from Chapters 1 and 2

| Decision | What to carry forward | Scope and limitations |
| --- | --- | --- |
| Teach one relationship at a time | Keep the opening brief. Carry the same example through the explanation, figure, and immediate practice. Introduce the new words or labels before asking learners to use them. Group short diagnostic steps into a worked list and use a fresh example for transfer. | Keep supplemental content within the reviewed outcome and chapter convention. Chapter 1 uses grouping placeholders. Chapter 2 studies the top-level NP and VP. Include terminology notes where they help learners perform the task at hand. |
| Show essential content inline | Place the explanation before the diagram and the prompt beside the controls it refers to. Keep worked examples visible. Use a reveal for an answer the learner should try first or for optional reference detail. | A worked diagram can teach a relationship while leaving other branches out of the analysis. Chapter 1 shows individual branches for tracing. Chapter 2 uses triangles to show the span of phrases at the top split. |
| Separate reading from construction | First let learners trace words in a worked tree. Put a quick check beside that figure, then give the construction task its own heading and canvas. Label controls with what the learner will do. | The longer Chapter 2 comparison is a read-only branch check and leads into the short build. The longer editable example is the fresh sentence on the application page. Keep one mounted editor per page. |
| Keep diagrams readable and accessible | Use thin neutral branches, highlight selected words, and keep the caption close to the figure. Allow keyboard selection and preserve a screen-reader outline. Check light and dark mode as well as mobile fit. | The lesson diagrams use an accessible outline in place of a visible tree-text disclosure. Check that blank assessment labels are masked in the outline too. |
| Guide without taking over | Keep **Guide me** and **Check construction** above the canvas. Show the compact numbered guide rows together. Each row applies a concrete edit, and learners can continue editing directly. | A guide step can require earlier nodes or branches. Explain how to recover from a conflicting edit. Keep drafts separate and use the chapter’s feedback and grading boundaries. |
| Keep checks short and progress predictable | Use word selection, tree interaction, and open-response prompts for practice. Show formal questions one at a time, then present all completed answers together. | Only the first opening answer is the saved diagnostic response. Ungraded practice and retakes use separate state. Preserve scored answers, feedback, and one-time XP. |

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

## Chapters 3–5 reference implementation

These three chapters use the same six pages and reviewed closing checks as
the earlier chapters. The opening check keeps the catalog prediction first
and adds two unscored questions. The worked page uses the reviewed tree as a
model, then detaches one branch in a separate editable draft. The learner
can reconnect it manually or use the two-step guide. The application page
uses an original example and a short written analysis to reveal.

| Chapter | Source and teaching focus | Build and transfer |
| --- | --- | --- |
| 3 · Heads and adjective phrases | V3, printed pp. 55 and 62. Distinguish the adjective head from a degree word in an AP. Use the basic DEG + A example before covering wider category systems in later units. | Connect A under AP in *very cheerful*. Compare *quite bright* with the one-word AP *bright*. |
| 4 · The basic transitive VP | V4, printed pp. 70–71. Separate the subject NP from the direct-object NP and read the `[trans]` feature for the use of the verb in this sentence. | Attach the object NP beside V under VP in *Nora inspected the bridge*. Locate the whole object in *The children carried a heavy box*. |
| 5 · Adjuncts and two levels of VP | V5, printed pp. 89–90 and Fig. 12. Distinguish the object beside V from the final time PP beside the inner VP. Printed p. 91 supports the supplemental *do so* example. | Attach *in June* beside the inner VP. In a fresh sentence, find the verb and object that group first and show where *before lunch* attaches. |

These are the launch outcomes. Broader adjective categories, other verb
frames, and moved adverbials need their own source and scope review when
they are taught. A branch exercise checks the intended shape for its
particular sentence. It gives local construction feedback and leaves
formal grading to the reviewed knowledge check.

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
> Place read-only practice beside the figure it uses and before the build
> it prepares learners for. Apply the polishing decisions above.
> Place any tree-building activity directly in the lesson using the existing
> editable canvas with an optional clickable guide. Keep Cambridge as cited
> context within the teaching. Preserve the reviewed assessment and progress
> contract. Run the verification checks and report the commit, source pages,
> and specific items for me to try.

## Owner review

Review one chapter at a time. First read it as a learner and try the new
example before opening any answer or guide. Then try one plausible wrong
branch, complete the construction manually and with the guide, and try the
closing check and a retake. Check that the explanation, diagram, and feedback
use the same words and notation. Send the chapter and page heading, the
expected learner action, what happened, and a screenshot for layout issues.
Use feedback from Chapters 3–5 to settle the shared pattern before starting
Chapter 6. For each remaining batch, agree on the target outcome and one
fresh example per chapter, then review a worked page and closing check
before carrying the pattern forward.
