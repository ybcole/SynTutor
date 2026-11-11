# Syntax Foundations lesson rollout master plan

## Goal and reference implementation

Bring Chapters 3–11 in **Lessons → Syntax Foundations** into the lesson flow and
visual system already used in Chapters 1 and 2. Make the existing material easier
to read, follow, and practice. The rollout covers presentation and learning
sequence. Content expansion belongs in a later revision.

Use Chapter 1 as the visual and interaction reference. Use Chapter 2 as the
scope reference for a conversion that carries over the original teaching
paragraph, worked example, source note, and questions with minimal new prose.

Read these before editing:

1. The [M4 launch curriculum](../curriculum/README.md) gives the reviewed outcome,
   source pages, comparison tree, and coverage limits for each chapter.
2. The [original master plan](master_plan.md#lessons),
   [M4 execution plan](syntutor_12_prompt_execution_plan.md#04--lessons-and-curriculum),
   [M4 implementation brief](master_prompt_lessons.md), and
   [M4 acceptance report](../reports/milestone-04-acceptance-2026-11-08.md)
   define the course and its acceptance criteria.
3. [The lesson catalog](../../web/content/lessons/course.json) contains the
   actual reviewed teaching text, authored tree, worked steps, source IDs,
   questions, answers, feedback, and prerequisites.
4. [The shared lesson renderer](../../web/js/lessons-ui.js),
   [lesson styles](../../web/css/lessons.css),
   [Chapter 1 presentation](../../web/js/constituents-lesson.js), and
   [Chapter 2 presentation](../../web/js/subject-predicate-lesson.js) show the
   current interface. Follow the running implementation when old planning
   screenshots or descriptions show a different layout.

## Content and implementation boundaries

- Treat Noel Burton-Roberts' *Analysing Sentences*, third edition, as the
  foundation for the chapter sequence and notation. The M4 source records and
  [review receipt](../../sources/burton_roberts/reviews/2026-11-08-lessons.json)
  identify the checked printed pages. The repository has reviewed records and
  comparison trees. The full source PDF is outside the repository. Use the
  existing material when the source pages are unavailable, and describe the
  scope of any verification accurately.
- Preserve the catalog, source receipts, reviewed explanations, examples,
  worked steps, tree envelopes, assessment wording, answer keys, feedback,
  lesson IDs and versions, prerequisite links, completion rules, and XP.
  Brief introductions, descriptive headings, navigation cues, and recaps may
  restate the reviewed outcome or teaching text. Keep any substantive new claim,
  replacement example, new question, or broader objective for a separate
  source-reviewed content revision.
- Use each chapter's M4 convention. The canonical worked example from the
  lesson record drives the diagram and graded activity. The comparison tree
  ID identifies a source reference. Keep authored trees independent of live
  parser predictions. Reuse the existing evidence service for node explanations
  where available.
- Scope the rollout to `br-03` through `br-11`. Use Chapters 1 and 2 as
  regression checks for shared UI. Keep the Cambridge companion track, M5
  standalone quizzes, Builder, Generator, account contracts, and deployment
  outside this rollout. Retain Chapter 8's existing Cambridge insight as context.

## Learner flow

Use the same six reading pages and navigation pattern as Chapter 2. Each page
has a descriptive heading and a clear reading or practice goal.

| Page | Learner experience | What to reuse |
| --- | --- | --- |
| 1. Introduction | A short opening explains what to look for in the chapter. The existing unscored pre-test appears below the introduction in a rounded panel. Any response unlocks Next. Once submitted, show **Response recorded.** on return. | The M4 outcome and existing prediction prompt and choices. |
| 2. Core idea | Read the reviewed explanation before opening the worked example. Use the chapter's terminology in the heading. | Existing teaching blocks in their reviewed wording. |
| 3. Worked example | Follow the authored steps in place. Selecting a step highlights its relevant node and shows the existing caption. Zoom and text view stay with the diagram. | Canonical tree and `worked_example.steps`. For Chapter 11, use the same sequence as a text walkthrough. |
| 4. Read the structure in context | Explain what the key branch, feature, gap, or combination in the example shows. Use a brief cue and the relevant reviewed detail. If a point fits better here than on page 3, move it here so students only read it once. Keep Chapter 8's existing Cambridge insight available here. | Existing teaching or worked material. This is an application of the example before the assessment. |
| 5. Chapter recap | Review a few points tied to the objective. Open **References and source review** below the recap. Use **Start post-test** when ready. | A concise restatement of the reviewed material and the existing source records. |
| 6. Post-test | Answer the existing guided, transfer, and exit questions in order. Present the prompt, relevant tree, options, and feedback together in a rounded panel. Learners can revisit the recap with Previous. After completion, they can review their answers or retake for practice. | Existing scoring, hints, feedback, and guided label or feature target. |

Keep the site font, compact headings, single reading column, purple controls,
and rounded assessment panels. Use the same canvas and control placement when
switching between views. Show a tree where it helps with the example or question.
Keep the text view available and explanations below the canvas. Use Previous
and Next at the bottom and retain the current heading focus on page transitions.

## Chapter map

Source pages and comparison IDs below follow the M4 map. The example column is
the authored SynTutor example used in the lesson.

| Chapter | M4 focus | B-R pages and comparison ID | Existing example and presentation detail |
| --- | --- | --- | --- |
| 3. Heads and adjective phrases | Distinguish the adjective head from the degree word. | 55, 62 · `ch3-text-a` | *very cheerful*. Follow **A** and **DEG** under **AP**. |
| 4. The basic transitive VP | Attach transitive **V** and direct-object **NP** as sisters. | 70–71 · `ch4-21` | *Nora inspected the bridge*. Keep the guided **[trans]** feature activity. |
| 5. Adjuncts and two levels of VP | Distinguish adjunct attachment from complement attachment. | 89–90 · `ch5-12` | *Nora inspected the bridge in June*. Show which VP the adjunct PP joins. |
| 6. Auxiliaries head their own VPs | Identify the progressive auxiliary's VP complement. | 121–122 · `ch6-52` | *Nora is inspecting the bridge*. Follow the existing **PROG** and lexical VP steps. |
| 7. DET and NOM inside NP | Build the core Chapter 7 NP using **DET** and **NOM**. | 141–142 · `ch7-5` | *those lanterns*. Keep V7-CORE and its reviewed labels. Appendix D1 is later coverage. |
| 8. Complementisers and subordinate clauses | Expand an overt *that*-clause into **C** and **S**. | 174 · `ch8-11a` | *that Nora is inspecting the bridge*. Keep the **S′** display, stored S-bar label, and reviewed Cambridge context. |
| 9. Wh-fronting and typed gaps | Distinguish **C2** and **C1** and preserve the **NP** object gap. | 198–200 · `ch9-11b` | *What is Nora inspecting*. Preserve typed gaps, including the authored PROG gap, and their placement. |
| 10. The non-finite to-infinitive VP | Represent untensed *to* and its lexical VP complement. | 226 · `ch10-11` | *to inspect the bridge*. Preserve the source-aligned feature-only **[-tense]** display and its feature question. |
| 11. From sentence lists to grammars | Explain how finite rules can produce unbounded combinations. | 260, 263, 265–266 · text-only | *Iris rests. / Leo waits. / Iris rests and Leo waits.* Use the authored combination steps and text questions. |

## Execution order for the next AI

1. **Audit the baseline.** Confirm the planning branch descends from
   `explore/constituents-lesson` at `d85147e` or later. Walk Chapter 2 from
   introduction through post-test, then compare Chapters 3–11 against their
   catalog entries. Identify which guided tasks use labels, features, or text.
2. **Convert Chapter 3 through the shared path.** Reuse the article renderer
   and current CSS. Read the canonical worked steps from the catalog. Keep the
   existing questions and make the label-fill activity work in the new panel.
   Use Chapter 3 to verify the shared pattern before applying it to the rest.
3. **Convert Chapters 4–7.** Keep per-chapter presentation data small. Confirm
   that the shared diagram and assessment paths support a missing feature in
   Chapter 4 as well as the label activities in Chapters 5–7.
4. **Convert Chapters 8–10.** Verify the Cambridge insight placement, subordinate
   clause labels, typed gap display, and feature-only infinitival node in both
   instruction and assessment. Check the guided prompt, visible tree, and
   accepted answer against each other.
5. **Convert Chapter 11.** Use the same article and assessment components.
   Render the authored examples, worked steps, and guided question as text.
   Make canvas and build targets conditional so the shared page works without
   a tree.
6. **Check saved progress.** Follow the current
   [progress contract](../curriculum/progress-and-deployment.md). Existing
   `predict`, `understand`, and `worked` records resume at their corresponding
   article pages. Existing `guided`, `transfer`, and `exit` records resume at
   the corresponding post-test question. Preserve responses, prior completion,
   prerequisites, and one-time 15 XP. Previous changes the reading location,
   while practice retakes stay separate from saved assessment answers. The
   worked and remaining reading pages share the current worked checkpoint, as
   in Chapter 2.
7. **Verify and report.** Run `python scripts/validate_lessons.py`,
   `npm run test:lessons`, and `python scripts/test_lessons_browser.py`.
   Update the existing browser regression for the shared flow. Complete all
   12 lessons through the UI and verify one-time awards. Check desktop and
   mobile layouts, keyboard navigation, answer feedback, reload and review.
   Inspect Chapter 4 or 10 for a feature blank, Chapter 9 for gaps, and
   Chapter 11 for text-only completion. Verify that a lesson never requests a
   parser prediction. Report the commit, migrated chapters, observed checks,
   and any missing source or hosted verification.

## Prompt for the next AI

> On `explore/foundations-lesson-rollout-plan`, read this master plan and the
> linked M4 curriculum and implementation. Apply the shared Chapter 1–2 article
> flow to Chapters 3–11 in Syntax Foundations. Use Chapter 2 as the model for
> how much content to change. Preserve the reviewed M4 explanations, examples,
> trees, questions, and learner records. Follow the chapter map, run the
> acceptance checks, and report what you verified on the branch.
