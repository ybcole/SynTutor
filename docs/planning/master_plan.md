# SynTutor — Master Product, Linguistic, and Engineering Plan

**Repository:** [ybcole/SynTutor](https://github.com/ybcole/SynTutor)  
**Reviewed branch:** `main`  
**Plan date:** 6 November 2026  
**Status:** Planning only — no repository code or content has been changed as part of this plan.

---

## Companion execution plans

The detailed, sentence-specific explanation and error-diagnosis workstream is now defined in [XAI Master Plan](XAI_MASTER_PLAN.md), with a separate [XAI implementation master prompt](MASTER_PROMPT_XAI.md). Before beginning milestones, apply the [uploaded-book source audit and multi-error dependency/repair contract](XAI_SOURCE_AUDIT_MULTI_ERROR.md), which adds the mandatory XAI-PRE gate. The XAI-PRE technical artifact inventory and open reviewer decisions are recorded in [its acceptance report](../reports/xai-pre-acceptance-2026-11-10.md). **The XAI-0 empirical baseline is implemented and recorded in the [116-case measured acceptance report](../reports/xai-0-baseline-acceptance-2026-11-10.md)**; it shows 0/417 word-terminal nodes with source-cited explanations, not a completed contextual XAI engine. These documents supersede *only* the minimal XAI foundation assumptions for this dedicated workstream; they do not retroactively declare the advanced explanation engine implemented.

## Executive direction

SynTutor should become a source-grounded English syntax tutor built around two complementary authorities:

1. **Noel Burton-Roberts, *Analysing Sentences: An Introduction to English Syntax*** — the primary authority for constituent structure, phrase-marker construction, tree labels, chapter-specific conventions, and the method taught in the Syntax Builder.
2. **The Cambridge Grammar of the English Language (Cambridge)** — the primary knowledge source for a broader and more detailed account of English grammatical categories, constructions, constraints, exceptions, and linguistic distinctions, and for the grammatical reasoning used in explanations and assessments.

These sources must not be flattened into one undifferentiated grammar. Where their terminology or analyses differ, SynTutor must preserve the distinction, record the evidence, and avoid pretending that one framework automatically translates into the other.

**Recommended architecture:** Benepar remains a candidate parser initially; a new B-R normalization and validation layer converts only well-supported analyses into the canonical B-R tree representation. Cambridge knowledge is then evaluated against the normalized structure and the sentence. A shared evidence-based explanation service serves the Syntax Generator, Syntax Builder, Lessons, and Quizzes.

Do not replace Benepar merely because the linguistic authority is changing. Replace the old *representational, rule, teaching, and explanation layers* first. Replacing the parser itself is a separate research decision that requires substantially more book-aligned training/evaluation data.

## Decisions at a glance

| Question | Recommendation | Reason |
|---|---|---|
| Which book governs syntax-tree form? | Burton-Roberts | The repository already has explicit, chapter-specific tree conventions and 252 chapter trees. |
| Which book governs grammatical knowledge? | Cambridge, with B-R cross-references | Cambridge provides a broad grammatical analysis; B-R also remains authoritative for the structural method being taught. |
| Is Cambridge the sole basis for every explanation? | No | Structural explanations should be sourced to B-R; Cambridge should support grammatical concepts, conditions, exceptions, and rule application. |
| Should an LLM write explanations? | Use it as a controlled drafting/paraphrasing aid, not as the grammar judge | Deterministic evidence must decide what rule applies; generated prose must not invent linguistic claims. |
| Should Benepar be removed now? | No | Keep it as a candidate parser behind a B-R adapter until measured results justify replacement. |
| Should all lessons be replaced with Cambridge? | No | Use B-R as the ordered syntax curriculum and integrate selected Cambridge material as aligned explanation cards and advanced modules. |
| Should Lessons be removed in favour of Quizzes? | No | Lessons teach; quizzes test independent retrieval and transfer. They have different jobs and should be separate destinations. |
| Should book exercises be copied into a quiz bank? | No | Current JSONs mostly contain answer data/tree references, not complete question banks; respect copyright and author original parallel items. |
| Should achievements be lesson-only? | No | Make them earnable through lessons, quizzes, syntax analysis, and builder mastery. |
| Level curve | Gently accelerating, not steep exponential | The proposed 15/10 XP rewards need a predictable early and middle game. |

---

# Thoughts

## A. Response to the proposed direction and concerns

### 1. Replacing the existing model with Cambridge + Noel Burton-Roberts

This is the right strategic direction, with one refinement: **separate linguistic authority from parsing technology**.

The old system has at least four things that are currently bundled together:

- A parser's output labels and structure.
- The linguistic conventions used to decide what a correct tree should look like.
- The grammar rules used to identify a grammatical or ungrammatical construction.
- The prose used to explain the analysis to a learner.

Those are not the same responsibility. The target state should make them separate services with explicit contracts.

B-R should govern how SynTutor teaches constituent structure and constructs/grades its phrase markers. Cambridge should contribute the broader grammatical analysis and the principles used to explain why a structure or construction behaves as it does. The existing rule matrix and manually authored lessons should be treated as legacy material to audit and migrate, not as unquestioned sources of truth.

### 2. Should Cambridge be the ONLY basis for explanations?

**Cambridge should be the primary grammatical authority, but not the only source for every kind of explanation.**

Use each source where it has the right job:

| Explanation type | Primary source | What it should tell the learner |
|---|---|---|
| Tree construction | Burton-Roberts | Why this label, constituent boundary, hierarchy, feature, gap, or convention is used. |
| Grammatical concept | Cambridge, cross-referenced to B-R where appropriate | What the concept means, when it applies, and how it differs from nearby concepts. |
| Error diagnosis | Cambridge constraint plus validated structural evidence | Which condition is not satisfied, which words/nodes demonstrate it, what exception or variety limit matters, and a repair. |
| Lesson sequencing | B-R chapter progression plus instructional design | What the learner should know before this concept and what they should learn next. |

Do not ask an AI to read a general paragraph from Cambridge and independently decide how it applies to a sentence. Instead:

1. A deterministic parser/normalizer creates a B-R-compatible analysis.
2. A deterministic evaluator identifies the relevant rule IDs and evidence (nodes, spans, token forms, conditions, exceptions).
3. An explanation composer receives only those verified facts and source references.
4. Approved templates or tightly constrained AI-drafted prose express the result in natural language and anchor it to the actual sentence.
5. The final explanation records its source pages and content version.

The AI can help turn a source-backed rule into readable prose such as: “In *Maya has finished*, *has* is the auxiliary head. In this analysis it heads its own VP and takes the VP containing *finished* as its complement.” But the AI must not invent the structure, decide whether the construction is wrong, or infer an exception that is absent from the source record.

Use reusable explanation templates with slots for the learner's words and rule evidence. Human-review and approve the templates. Runtime LLM generation should be optional, constrained, and never authoritative for correctness.

### 3. What information is in the B-R and Cambridge JSONs?

The B-R `ch01.trees.json`–`ch10.trees.json` files are primarily **tree and exercise-answer repositories**. Depending on the chapter, they hold:

- Figure IDs, printed pages, sentences, and nested tree nodes.
- Labels, features, triangles, gaps, and occasionally movement or control metadata.
- Chapter-specific convention versions and interpretive notes.
- Node fragments where a full tree is not given.
- Book flags, discussion answers, abbreviated clausal analyses (ACAs), and other supporting lists.
- `exercise_answers_from_book` with extracted answers, classifications, function labels, and/or IDs of corresponding trees.

They do not consistently contain the full prompt wording of each book exercise. Treat them as answer keys and gold/reference data, not as ready-made quiz question text. The current Chapter 11 file is a text-oriented lesson record containing concepts, steps, examples, glossary, questions raised, and a statement that no book exercise section is present.

The Cambridge raw extraction files have `meta`, `concepts`, `rules`, `cross_references`, `conflicts`, `uncertain_items`, and `coverage_report`. The merged `grammar/rules/*.json` files group rules by grammatical domain rather than by Cambridge chapter. A rule can contain its type, scope, statement, condition, violation, exceptions, correct/incorrect/contrast examples, printed-page sources, B-R mapping, confidence, and review status.

Importantly, the Cambridge rule types have different uses:

- `constraint`: can support error detection once independently validated and implemented.
- `variety_restricted`: can support conditional evaluation only in its stated variety/register.
- `descriptive_generalization`: teaches a tendency or pattern; it is not an automatic prohibition.
- `classification`: identifies or defines a category; it is not by itself an error rule.
- `stylistic_or_prescriptive`: must not be turned into a grammatical error merely because a traditional prescription exists.

The raw extraction status `APPROVED` is not proof of independent second-pass verification. Many reports explicitly state that an independent second pass was not performed and that B-R mappings remain `unverified` because the corresponding B-R source/concept index was not supplied to those extraction jobs.

### 4. Should the current lessons all be replaced with B-R and Cambridge?

Replace the **content and the unsupported explanations**, but do not make every lesson a full Cambridge chapter lecture.

B-R already provides a natural learning progression: identify constituents, introduce categories, build phrases, add verb features and complements, analyse adjuncts, auxiliaries, subordinate clauses, wh-structures, and non-finite clauses. Its conventions evolve across chapters, and the curriculum should teach those changes when the source introduces them.

Cambridge is much larger and more detailed. Forcing every Cambridge distinction into the beginner syntax course would make lessons long and cognitively dense. Instead, use three levels:

1. **Core B-R lesson:** the chapter's learning objective and the correct chapter-specific phrase-marker method.
2. **Cambridge insight card:** a short, sourced explanation of a directly relevant grammatical concept, condition, exception, or difference in terminology.
3. **Advanced Cambridge module:** a separate deeper topic for material that is too extensive or not a prerequisite for the B-R tree lesson.

The learner should be able to move from a B-R structural lesson to its Cambridge grammatical context without being forced to study the entire Cambridge chapter at once.

### 5. Can B-R and Benepar coexist?

Yes, but not by simply relabelling Benepar nodes. Benepar should propose a constituency analysis. A B-R normalizer must translate or restructure it into the B-R representation, check whether the transformation is justified, and flag cases it cannot confidently resolve.

Some differences are theoretical, not cosmetic: auxiliary-headed VP recursion, `DET`/`NOM`, the chapter-specific `S′`/`S″` layers, gaps and indices, verb subcategorisation features, and the function of a constituent can require structural decisions that a Penn-style parse does not directly encode.

Keep the raw Benepar parse for diagnostics. Show and grade the normalized B-R tree. If the adapter cannot justify a result, present an unresolved/alternative analysis rather than silently claiming that the parser produced the book's analysis.

### 6. Should lessons begin with a multiple-choice question?

Yes, as a short **prediction/diagnostic prompt**, not as a graded quiz that punishes the learner before teaching them.

Recommended flow:

1. A low-stakes prediction question: “Which structure do you expect?” or “Which word is the head?”
2. A brief concept explanation with B-R page citation and the relevant Cambridge insight, if one applies.
3. A worked phrase marker, revealed progressively.
4. Guided construction/practice using the B-R convention for that chapter.
5. An application task that changes the example or context so the learner must transfer the concept.
6. A concise exit check; passing it completes the lesson.

The user's suggested multiple-choice → tree explanation → application sequence is sound. Add a worked example and guided practice between explanation and independent application. That reduces the risk of asking learners to perform a difficult tree construction after only reading a paragraph.

### 7. Should Lessons and Quizzes be separate?

Yes. A lesson can include checks and an exit ticket, but the independent quiz experience should be a separate product area.

- **Lessons teach:** introduce an objective, explain it, model it, guide practice, and check application.
- **Quizzes assess:** retrieve knowledge without the full lesson scaffold, test transfer, mix item types, and diagnose weak concepts.

Do not reuse the same exact worked examples as the sole quiz questions. Use book-derived answer structures as internal reference, then create original parallel examples and controlled distractors.

### 8. How should Cambridge content be selected for quizzes?

Do not extract every sentence or every concept into a quiz. Curate a question blueprint from learning objectives and verified rule records.

- Classifications: ask learners to identify or distinguish categories.
- Descriptive generalizations: ask what is typical, possible, or less typical; do not mark a possible alternative wrong.
- Constraints: use minimally different grammatical/ungrammatical examples, including exceptions.
- Variety-restricted rules: name the target variety/register in the item.
- Stylistic/prescriptive records: assess whether the learner understands the distinction between style advice and grammar, not whether they obey a false prohibition.

The five-question quiz can draw from a small balanced sample; the bank behind it should be much larger and tagged by source, concept, difficulty, chapter, convention version, and question type.

### 9. Should achievements be limited to lessons?

No. Achievements should reward several forms of meaningful progress: completing lessons, passing quizzes, improving a personal best, building a valid B-R tree, recognizing a difficult construction, and applying both frameworks together.

Use both “OR” conditions (a skill can be demonstrated in either a lesson or a quiz) and “AND” conditions for deeper mastery (complete the lesson and pass the independent assessment). Do not make every achievement depend on a perfect score; that discourages beginners.

### 10. How do we incentivize XP and levels?

XP should visibly represent progress, but it should not be the only reason to study. Give learners immediate feedback, visible mastery, unlockable optional cosmetics, new challenge tiers, personal bests, and short weekly goals. Essential content and useful explanations should never be hidden behind grinding.

The proposed awards are reasonable:

- Lesson completion: **15 XP**, awarded once per lesson content version after the lesson's required activities and exit check are complete.
- Five-item quiz: **10 XP maximum**, reduced by **2 XP per incorrect answer**. For five questions, `earned XP = max(0, 10 - 2 × incorrect answers)`. This is equivalent to two XP per correct answer.

Do not subtract XP from a learner's accumulated balance when they answer incorrectly. A wrong answer lowers the reward for that attempt; it does not create a debt.

Prevent farming by making XP idempotent. Recommended policy: award XP for the best score achieved on a quiz assessment version, not every replay. A learner who first scores 3/5 earns 6 XP; improving to 5/5 later can grant the remaining 4 XP, but the same assessment version can never pay more than 10 XP in total. Lesson XP is similarly one-time per lesson version.

### 11. What leveling curve?

Use a **gently accelerating curve**: not a flat number forever, but not the current steep exponential growth either. The current `level.js` uses a geometric span of approximately 50, 80, 128, 205, 328... XP (growth factor 1.6). That curve should be retuned for the new award schedule.

A simple starting formula is:

`XP needed to advance from level L = 100 + 20 × L`, where the first level-up starts at L = 0.

| Level reached | Cumulative XP threshold | XP needed for that level |
|---:|---:|---:|
| 1 | 100 | 100 |
| 2 | 220 | 120 |
| 3 | 360 | 140 |
| 4 | 520 | 160 |
| 5 | 700 | 180 |
| 6 | 900 | 200 |

This is a linearly increasing per-level cost and therefore a quadratic cumulative curve. It gives early milestones without making later levels trivial. Recalibrate using observed lesson/quiz completion rates after a pilot.

### 12. Should syntax tree components be closer together?

Yes, modestly. The current renderer uses `GAP = 26` and `V_GAP = 40` (along with fixed node dimensions). Reducing whitespace can make constituent relations easier to follow, but a global reduction can cause overlap in long sentences and deep recursive trees.

Use adaptive spacing:

- Reduce the ordinary horizontal gap and vertical level gap in a small, testable step (e.g. horizontal 26 → 16–18 and vertical 40 → 26–30 as a first experiment).
- Calculate width from actual label/leaf measurements; do not force a narrow fixed width.
- Add density modes or scale-aware spacing for very large trees.
- Preserve clear connector paths, selected/error highlights, readable labels, and touch targets.
- Test Chapter 7–10 deep structures, long coordination, gaps, triangles, and mobile canvas dimensions before approving the change.

---

## B. Additional product and technical thoughts

1. **Build one canonical analysis contract.** The Syntax Generator and Syntax Builder must not maintain separate rule logic or explanation formats.
2. **Separate source truth from runtime implementation.** An approved extracted record is not automatically executable. Track source-review state, framework crosswalk state, runtime implementation state, and test state separately.
3. **Keep evidence with every claim.** Every visible book-derived explanation should carry chapter and printed-page references; internal records should also keep PDF pages where useful.
4. **Treat convention versions as first-class data.** Chapter lessons use the chapter's convention. Free-form full analyses use the repository's declared final profile (currently V10 plus the Chapter 7 appendix refinement in `CONVENTIONS.md`).
5. **Preserve alternatives and uncertainty.** Some sentences have multiple possible analyses. The UI and grader need accepted alternatives, uncertainty states, and “not enough evidence” outcomes.
6. **Make content versioned.** When a source extraction, rule, lesson, or assessment changes, progress and XP should know which content version was completed.
7. **Do not use an LLM to decide grammar.** It can help draft explanations and distractors from structured, reviewed facts; deterministic code and reviewed data decide correctness.
8. **Add tests before expanding features.** This project changes the core linguistic contract. A parser change without gold tests can silently break every downstream feature.
9. **Treat copyright as a product requirement.** Store paraphrases, short references, original examples, and internal answer structures; do not expose copied exercise prompts or lengthy source prose.

---

# Syntax Generator

## Thoughts

The Syntax Generator (the current Grammar Tutor workspace) should be the authoritative end-to-end analysis experience. It should answer four separate questions without conflating them:

1. What words/tokens are present?
2. What is the B-R-compatible constituent structure?
3. Which Cambridge grammatical principles apply to the sentence and structure?
4. What evidence supports the explanation or correction?

The old system's Benepar parse, legacy matrix rules, CoLA detector, and correction suggestions currently coexist. The new system must explicitly define their authority:

- Benepar: candidate structure provider, not linguistic authority.
- B-R normalizer/validator: authoritative tree representation.
- Cambridge evaluator: source-grounded grammatical constraints and descriptive/classification insights.
- CoLA acceptability model: optional secondary signal only. It may flag a sentence for review, but must not invent a rule explanation or override an explicit verified constraint.
- Explanation composer: renders verified evidence, not free-form guesswork.

### Corrected sentence display

The requested correction presentation is desirable. The corrected tree should still represent the **corrected sentence**, while the learner can see which original token was wrong. Show the original incorrect word struck through and the replacement immediately beneath or beside it at the corresponding leaf position. The tree's node and spans must remain aligned to the corrected tokenization.

For example, if the original is “She can goes home” and the repair is “She can go home”, the `go` leaf in the corrected tree is annotated with a struck-through `goes` and the corrected `go`. Do not put both forms into the grammatical tree as if both were spoken words.

Handle replacement, insertion, deletion, and multi-token edits. Preserve the full sentence, punctuation, and token alignment. Provide a clear toggle back to the original sentence/tree.

## Plan

### SG-1. Define the canonical tree schema

Create a versioned schema that captures B-R information explicitly:

- Node ID, canonical label, features, index/co-index, children, lexical word, gap/elision/triangle markers, token span, source/convention version.
- Separate movement metadata from the phrase marker when the book treats movement arrows/lines as explanatory rather than structural.
- Derive grammatical functions from the relevant tree positions; do not add subject/direct-object/adjunct nodes just because a function exists.
- Store `S-bar`/`S-dbar` internally according to `CONVENTIONS.md`, with rendering of primes handled by the presentation layer.
- Preserve accepted alternatives and analysis confidence.

Keep the raw Benepar parse as a separate diagnostic field. Do not overwrite it with the normalized result.

### SG-2. Implement the B-R normalization layer

Create a parser adapter that maps or restructures candidate nodes only where the mapping is supported by B-R conventions and gold examples. It must handle the known chapter developments: lexical/phrasal categories, verb subcategorisation features, auxiliary-headed VP layers, DET/NOM, clause layers, wh-gaps, and non-finite structures.

For any transformation that cannot be inferred confidently, return an explicit unresolved item or alternative. Never silently guess a B-R analysis.

### SG-3. Define the convention profile

- Chapter lessons must parse/build/grade using that chapter's `convention_version`.
- The free-form Syntax Generator should use the final convention profile declared by the team (currently V10 plus the Chapter 7 appendix refinement, subject to confirming the edition and decision record).
- UI labels may be rendered in book typography, but internal labels must remain canonical and machine-stable.

### SG-4. Build a structural validator

Validate schema, token coverage, word order, category/feature legality, node hierarchy, gaps/indices, triangles, accepted alternatives, and convention-version rules. Reuse the 252 B-R trees as gold fixtures; add tests for every transformation.

### SG-5. Integrate Cambridge rule evaluation

Create a rule registry/runtime adapter. An extracted rule becomes executable only when:

- Source content has been independently reviewed.
- B-R mapping/cross-framework status is resolved or explicitly marked compatible.
- The rule type and scope are understood.
- Conditions/exceptions/variety are represented in executable form.
- Unit tests and regression fixtures pass.

Initially implement only the strongest validated constraints. Keep classification and descriptive records available for lessons and explanations, but do not use them as error flags.

### SG-6. Create a shared analysis payload

Return one contract with: sentence/token spans, raw candidate parse, normalized B-R tree, convention version, structural validation, Cambridge rule results, acceptability signal (if enabled), per-node evidence, corrections, alternatives, confidence, and source references.

### SG-7. Implement correction annotation

Use the machine-applicable edit plus token alignment to produce a corrected analysis and an annotation map. Render the corrected sentence as the true leaf sequence, with original erroneous form struck through and the corrected form visually associated with that position. Keep original and corrected text/tree states reversible.

### SG-8. Regression and acceptance

Run all B-R chapter validators, gold-tree comparisons, Cambridge minimal pairs, legacy error corpus, correction tests, and sentence/token alignment tests. Do not switch the new pipeline on by default until key fixtures meet the agreed acceptance threshold and unknown cases fail safely.

---

# Lessons

## Thoughts

Do not remove Lessons. The repository's present lessons are hard-coded in `web/js/tree-quiz.js` with manually authored summaries, rules, details, steps, sections, and examples. They are useful as a prototype but are not yet a durable source-backed curriculum. Replace the lesson content model, not the learning function.

Use **B-R for the core syntax curriculum** because it teaches the method of constructing phrase markers in a deliberate progression. Use Cambridge as a companion source for relevant grammatical ideas, distinctions, conditions, and exceptions. Advanced Cambridge material should be an optional track or deeper module rather than dumped into every introductory lesson.

### Recommended curriculum structure

**Track A — Syntax Foundations (B-R):** teach Chapters 1–10 in order, respecting each convention version; use Chapter 11 as a closing/theoretical synthesis. The learner should see why the book's tree notation changes as their knowledge develops.

**Track B — Grammar and Analysis (Cambridge):** provide curated topic modules such as verb forms and auxiliaries, complementation/valency, nouns and NPs, adjective/adverb categories, prepositions, adjuncts, negation, clause types, subordinate clauses, relatives, comparatives, non-finite clauses, coordination, information packaging, morphology, word formation, and punctuation.

**Integrated lessons:** when a Cambridge concept directly clarifies the B-R chapter being taught, include a short “Cambridge insight” panel with the relevant concept/rule IDs and source pages. Do not force unrelated content into the lesson.

### Recommended lesson sequence

1. **Predict (diagnostic MCQ):** one low-stakes question before teaching; reveal why after the learner answers. No XP is lost for an incorrect prediction.
2. **Understand:** a short learning objective, B-R definition/convention, and a Cambridge insight where useful.
3. **See it:** a worked B-R tree with progressive highlighting of the head, dependents, complements, features, or other current concept.
4. **Build it:** guided construction in the Syntax Builder, with hints that progressively fade.
5. **Apply it:** an original transfer example or a different sentence requiring the learner to use the concept independently.
6. **Exit check:** a short independent task; successful completion awards the lesson's 15 XP once per content version.

A lesson is completed when all required stages and its exit check are done—not simply when the learner opens the page.

## Plan

### L-1. Create a data-driven lesson schema

Each lesson should define:

- `lesson_id`, title, track, chapter/section, content version, difficulty, estimated effort.
- Prerequisites and learning objectives.
- B-R `convention_version` and references to relevant `tree_ids`.
- Cambridge `concept_ids` and `rule_ids` (only relevant ones).
- Prediction prompt, teaching explanation blocks, worked examples, guided steps, transfer task, exit check.
- Accepted tree alternatives, source references, review state, and completion criteria.

Keep lesson text out of `tree-quiz.js`; it should render lesson data, not be the database of linguistic truth.

### L-2. Design the curriculum map

Map every B-R chapter objective and each selected Cambridge module to prerequisites, difficulty, source pages, and related tree IDs/rule IDs. Track which content is:

- Core / prerequisite.
- Supporting insight.
- Advanced / optional.
- Not yet covered by source extraction.

Do not mark an unextracted Cambridge section as taught or covered.

### L-3. Migrate existing lesson content

Audit every current hard-coded lesson. For each item, classify as:

- Source-supported and reusable after rewriting.
- Needs correction/reframing under B-R.
- Duplicated by another lesson.
- Unsupported and to be removed.
- Advanced topic to move to Cambridge track.

Do not bulk-copy existing Penn-style labels or explanations into the new B-R course without verification.

### L-4. Build lesson UI components

Separate reusable components for diagnostic prompt, concept card, source citation, annotated tree, step guide, guided builder activity, Cambridge insight, and exit ticket. Make lesson stages resumable and persist progress by lesson content version.

### L-5. Award lesson XP safely

Award 15 XP once after lesson completion criteria pass. Record a unique activity key such as `lesson:<lesson_id>:<content_version>` so replaying the lesson cannot repeatedly mint XP.

### L-6. Validate learning

Every lesson must have an objective-to-assessment alignment: a learner who passes the exit task should have demonstrated the stated objective. Add instructor/reviewer sign-off for content and answer structures before publication.

---

# Quizzes

## Thoughts

Quizzes should be a separate, independent assessment area. Lessons can contain formative checks, but the standalone quiz should not be the same “build every worked example again” sequence that the current `tree-quiz.js` uses.

A five-item quiz is a sensible short session. It should mix question types and not consist entirely of full-tree construction. Full trees are valuable but expensive and cognitively heavy; use them selectively for the learning objective being assessed.

### Cambridge extraction strategy

Cambridge is too large to turn wholesale into quiz questions. Build a curated question bank from reviewed learning objectives and rule types. Do not treat a 196-record knowledge base as 196 error rules or assume every record should have a multiple-choice question.

Potential quiz item types:

- Multiple choice: identify the correct category, distinction, or analysis.
- Tree selection: choose the B-R tree that matches a sentence/construction.
- Label/function identification: identify the head, complement, modifier, or function read from a position.
- Error diagnosis: locate a violation of an implemented Cambridge constraint.
- Minimal-pair judgement: distinguish the two examples and explain what changes.
- Ordering/assembly: put constituents in the correct hierarchy.
- Repair: select or build the corrected form/tree.
- Exception/variety question: choose the valid interpretation under a stated exception or language variety.

Every question needs a source link, concept/rule IDs, convention version if a tree is involved, correct answer, distractor rationale, difficulty, and version.

### XP policy

For a five-question quiz:

`earned XP = max(0, 10 - 2 × incorrect answers)`

A perfect 5/5 earns 10 XP; 4/5 earns 8; 3/5 earns 6; 2/5 earns 4; 1/5 earns 2; 0/5 earns 0. Do not subtract from accumulated XP.

Award the best-score difference only, per quiz assessment version. Example: a first 3/5 attempt earns 6 XP; a later 5/5 attempt earns a further 4 XP. Repeating the same score does not mint more XP. A revised/new assessment version can earn a new reward.

## Plan

### Q-1. Create a standalone assessment bank

Store items independently of lesson examples. Include item ID, assessment ID/version, item type, concept/rule IDs, B-R tree IDs or expected structure, Cambridge sources, difficulty, distractors, answer, rationale, and review status.

### Q-2. Build five-item assessment blueprints

Each quiz should sample a balanced selection of items for one topic or a cumulative level. Balance recall, interpretation, structural application, and error diagnosis. Avoid asking about a Cambridge rule that is not yet reviewed or not taught.

### Q-3. Make answer explanations evidence-based

After a response, show why the correct option fits and why the chosen distractor fails, using the shared explanation composer and the same source-backed rule/tree data as the Syntax Generator.

### Q-4. Support multiple quiz modes

Provide topic quizzes, chapter quizzes, cumulative quizzes, diagnostic quizzes, and optional challenge quizzes. Keep the five-item standard reward format consistent; longer practice modes can use separate reward rules or no XP.

### Q-5. Persist assessment progress

Store attempts, best score, last score, completion time, assessment version, response-level mistakes, and XP already awarded. Avoid storing only one `perfect_count` because it cannot represent learning improvement or idempotent reward calculations.

### Q-6. Award quiz XP

Compute a target reward of two XP per correct answer, max ten, and award only the difference between the new best-score reward and XP already granted for that assessment version. Log the XP transaction with a unique idempotency key.

### Q-7. Add spaced reinforcement

Use question history to bring back concepts the learner missed. Do not use repeated identical questions as the only reinforcement; rotate original examples while retaining the same source-backed objective.

---

# Syntax Builder

## Thoughts

The Syntax Builder should become the learner's workspace for constructing and testing **B-R phrase markers**, not a separate Penn-style tree game.

The current builder is permissive and lets a learner connect arbitrary word/phrase boxes. That is useful for exploration, but its target label inventory and validation currently follow Benepar/Penn-style labels. Its build validation performs client-side graph checks and then sends the sentence text to `/api/parse`; it does not yet evaluate the learner's own constructed graph with exactly the same per-node Cambridge/B-R evidence and explanations as the Syntax Generator.

The requested shared explanations are the right design. There should be one explanation service, one rule registry, and one evidence format. The builder should send its constructed tree to the same evaluator used for the generated tree, rather than simply asking the parser to analyse the sentence again and returning a sentence-level verdict.

Also distinguish three outcomes:

1. **Tree well-formedness:** does the submitted graph satisfy the selected B-R convention and hierarchy?
2. **Sentence grammaticality:** does the sentence satisfy the active, implemented Cambridge constraints and other verified evidence?
3. **Target comparison:** does the learner's tree match one of the accepted analyses for this exercise?

These must not be collapsed into one “wrong” label. A different but accepted analysis should not be marked wrong just because it differs from one parser output.

## Plan

### SB-1. Replace the node palette with B-R convention-aware labels

Load available labels/features from the selected chapter convention. Do not show labels before the source introduces them. The free-form builder uses the final convention profile; a chapter exercise uses its chapter profile.

### SB-2. Share the analysis/evaluation contract

Create a backend endpoint/service that accepts the learner's constructed normalized tree and sentence, then returns the same `node_details`, rule results, explanation evidence, source refs, and structural diagnostics used by the Syntax Generator.

### SB-3. Build a shared explanation component

Use the same explanation card/pane for a selected node in both the Syntax Generator and Builder. The card should have consistent sections: structural role, relevant rule/evidence, source reference, problem/validity state, and suggested next step.

### SB-4. Compare against accepted alternatives

Exercise grading must compare against all accepted alternatives or a canonical equivalence representation. It must not depend solely on exact tree identity from Benepar. Preserve triangles, gaps, indices, and chapter-specific conventions.

### SB-5. Add progressive assistance

Allow hints, highlighted target nodes, step-by-step instructions, and a “show model tree” action, but make hints fade in independent practice. Give feedback at the node/relationship that the rule actually concerns.

### SB-6. Test shared explanations

For the same sentence/node/rule, the Syntax Generator and Builder should produce matching explanation evidence and equivalent prose. Only the interaction context should differ.

---

# Leaderboard

## Thoughts

A leaderboard can encourage practice, but a single public, all-time XP ranking tends to favour early adopters and people who can grind the most attempts. It may also expose more identity information than necessary.

The current database stores `user_id`, `display_name`, `xp`, and `level`, and the client reads a public ranking ordered by level and XP. The current public query also includes the account's user ID. The SQL policies permit a user to update their own XP row, so client-side XP calculations alone are not a trustworthy competitive record.

Make leaderboard participation opt-in, show a chosen display alias rather than raw Clerk identifiers, and consider weekly/seasonal boards alongside a personal lifetime record. XP awards must be verified and idempotent on a trusted backend/RPC path before they are used for competitive ranking.

## Plan

### LB-1. Define leaderboard modes

- Weekly leaderboard: XP earned in the current week.
- Seasonal leaderboard: XP earned during a defined competition period.
- Personal lifetime progress: the learner's own total XP, level, and mastery; this need not expose their identity publicly.

### LB-2. Add privacy settings

Give learners an opt-in control, a public alias, and the ability to hide from rankings while retaining personal XP. Never expose email addresses or raw authentication IDs in the public leaderboard payload.

### LB-3. Secure XP transactions

Move award validation to a trusted server function or database RPC. Accept an activity ID, content version, result evidence, and idempotency key. The server calculates/validates the award; clients cannot arbitrarily write XP totals.

### LB-4. Define fair ranking

Rank by seasonal XP earned, with an explicit tie-breaker such as most recent qualifying activity or mastery score. Do not use lifetime level alone as the competitive ranking metric.

### LB-5. Provide useful personal context

Show the learner's rank, progress to next tier, recent XP, and personal bests without requiring them to publish their profile.

---

# Achievements

## Thoughts

Achievements should be available through lessons **and** quizzes, and selected achievements should also come from Syntax Generator/Syntax Builder mastery. A learner can demonstrate knowledge in more than one way.

Avoid an achievement system in which nearly everything requires perfection. Reward completion, persistence, improvement, accurate analysis, and difficult concept mastery as well as perfect performance.

Use explicit unlock logic:

- **OR criteria** for alternate demonstrations (e.g. pass the chapter quiz OR complete the builder mastery task).
- **AND criteria** for deeper mastery (e.g. complete the lesson AND pass the assessment).

Achievements should be durable, version-aware, and derived from auditable activity events rather than hard-coded around the current four pipeline stages.

## Plan

### A-1. Create achievement categories

- Learning path: complete a B-R chapter or Cambridge topic module.
- Assessment: first quiz, perfect quiz, cumulative assessment passed, improvement milestone.
- Syntax skill: construct a valid tree, correctly use a convention feature, analyse a deep/complex construction.
- Consistency: complete a weekly goal or return to a previously weak concept (optional; avoid punitive streaks).
- Cross-framework mastery: use a Cambridge concept to explain a B-R tree or resolve a framework distinction.

### A-2. Build a data-driven achievement catalog

Each achievement should define ID, name, description, icon, category, reward, unlock expression, source/content versions, hidden/visible status, and repeatability.

### A-3. Derive unlocks from activity events

Use a stable activity ledger for lessons, quizzes, tree builds, and challenges. Calculate newly unlocked achievements after the event and persist them idempotently. Do not keep achievements dependent only on the current `tree-catalog.js` four-stage model.

### A-4. Reward without distorting learning

Use optional cosmetic rewards, titles, profile frames, tree themes, and challenge access. Do not gate essential course material, explanations, or accessibility features behind achievements.

### A-5. Show clear progress

For locked achievements, show the criterion and the learner's progress when appropriate. For secret achievements, reveal only the hint intended by the product.

---

# UI/UX Design

## System Branding

Retain the name **SynTutor** and position it as a rigorous but approachable learning environment for English syntax and grammatical analysis.

Suggested brand direction:

- **Core promise:** “Understand structure. Explain grammar.”
- **Visual metaphor:** connected constituents, branches, nodes, and a readable phrase marker.
- **Tone:** precise, encouraging, intellectually curious; not childish or overly gamified.
- **Visual language:** clean editorial typography, restrained accent colour, clear hierarchy, consistent tree/node visuals, and source citations that look like scholarly references rather than legal footnotes.
- Keep the existing light/dark theme support. Revisit the current purple accent only if a full brand pass is planned; avoid changing the brand palette piecemeal.

## Thoughts on specific UIs across the system

### Syntax Generator

Make the result view communicate: sentence, B-R tree, grammatical verdict, specific rule evidence, explanation, and source references. Put the correction annotation directly on the corrected leaf without obscuring the full corrected sentence. Keep raw parser output in a developer/diagnostics view.

### Lessons

The lesson catalog should expose two tracks, prerequisites, progress, difficulty, and “continue learning.” A lesson screen should make its current stage clear and maintain a consistent right-side explanation area. Show source-page links close to each book-derived explanation.

### Quizzes

Use a distinct assessment area with quiz mode (topic, chapter, cumulative), five-item progress, clear response feedback, final score, XP calculation, and review of missed concepts. Avoid overwhelming the learner with long source prose.

### Syntax Builder

Reuse the Syntax Generator's explanation panel and evidence language. Visually separate free construction from the sentence input/target; make the B-R label inventory context-aware and expose chapter conventions in a subtle “Convention Vx” indicator.

### Leaderboard

Keep it calm and privacy-conscious: seasonal rank, display alias, current tier, weekly XP, and personal progress. Do not turn the entire app into a competitive scoreboard.

### Achievements

Use grouped badges/cards with clear criteria and progress. Show which activity types can unlock each achievement. Celebrate meaningful progress without aggressive popups or interrupting practice.

### Syntax tree density / spacing

The current renderer uses fixed spacing (`GAP = 26`, `V_GAP = 40`). Reduce it modestly and make it adaptive. The tree should look compact, but each node/edge must remain unambiguous. Test long sentences, deep embeddings, coordinated phrases, triangles, gaps, selected/error states, and mobile canvas sizes. Do not reduce the font or hit target to create the appearance of compactness.

### Corrected word visual treatment

Use a two-line terminal annotation: original form struck through, corrected form below, with the corrected form styled as the actual tree leaf. Add an accessible text alternative such as “Original: goes. Corrected: go.” Preserve the surrounding full sentence and punctuation.

## Plan

### UI-1. Establish design tokens and shared components

Define spacing, type scale, surfaces, semantic colours, states, motion, and responsive breakpoints. Create shared components for source citation, rule evidence, correction annotation, quiz item, lesson stage, progress display, and achievement card.

### UI-2. Prototype the revised information architecture

Design the main navigation around Syntax Generator, Lessons, Quizzes, Syntax Builder, Leaderboard, Achievements, and History/Profile. Test whether “Syntax Generator” is a clearer name for the current Grammar Tutor workspace; maintain familiar labels if renaming causes confusion.

### UI-3. Improve tree layout adaptively

Test horizontal gap 16–18 and vertical gap 26–30 as an initial design experiment. Implement measured widths, depth-aware spacing, responsive scale, and collision checks. Approve only after dense-tree visual regression.

### UI-4. Accessibility and responsive review

Provide a textual tree outline, semantic node descriptions, keyboard controls, colour-independent error signals, reduced motion, and touch-friendly selection. Test at desktop, tablet, and mobile widths.

### UI-5. Usability validation

Test with learners who have not authored the system. Observe whether they understand the difference between grammaticality, structural correctness, parser uncertainty, and an accepted alternative analysis.

---

# Others

## Thoughts

The work also needs a content-governance, data, testing, and release plan. These are not secondary details: without them, a theoretically correct grammar system can still show unsupported explanations, lose a learner's progress, award XP twice, or silently regress tree conventions.

The repository currently has a useful base—chapter tree data, validators, Cambridge rule JSONs, player stats, and quiz progress—but the product status document describes automated integration/E2E testing and production readiness as incomplete. The master plan must include those engineering requirements before broad release.

## Plan

### O-1. Create a source and framework registry

For every source, store bibliographic edition, chapter, section, printed pages, PDF pages, evidence type, extraction version, review state, copyright handling, and related source artifact. Confirm the precise B-R edition represented by the supplied PDFs before treating page conventions as universal.

### O-2. Build the framework crosswalk

Create a maintained crosswalk for B-R terms/structures and Cambridge concepts/rules. Each mapping should record relationship (`same`, `terminology differs`, `analysis differs`, `not covered`, `unverified`), explanation, scope, source references, reviewer, and status. Unresolved differences must not be silently merged.

### O-3. Separate source approval from implementation approval

Track at least four statuses independently:

1. Extraction/source review.
2. Framework crosswalk review.
3. Runtime implementation status.
4. Automated test status.

An `APPROVED` extracted record does not automatically become an enabled runtime constraint.

### O-4. Add content and event versioning

Version lessons, quiz assessments, B-R convention profiles, Cambridge rules, and explanation templates. Tie progress/XP to content versions so revised content does not duplicate rewards or corrupt mastery data.

### O-5. Establish a trusted activity ledger

Record event type, user, activity/content version, evidence, score, calculated XP, idempotency key, and timestamp. Award XP through a trusted server/RPC path. Keep progress events auditable.

### O-6. Copyright and source handling

Keep the public repository limited to paraphrased rules, original examples, citations, and compact structural data as permitted. Do not commit full copyrighted chapter text, PDFs, or copied exercise prompts. Separate private source material from public derivative data where necessary.

### O-7. Testing and CI

Add tests for schema validation, ID/cross-reference uniqueness, tree convention compliance, gold tree matching, parser normalization, rule applicability, exception handling, explanation references, XP idempotency, achievement conditions, leaderboard privacy, and browser flows. Run the chapter validators and regression corpora on every content/parser change.

### O-8. Observability and feedback

Track unresolved parses, false positives/negatives, corrections accepted/rejected, quiz item discrimination, learner exits, and content with repeated confusion. Collect minimal, privacy-conscious telemetry and make it possible to report a problematic explanation.

### O-9. Release strategy

Use feature flags and a staged rollout: internal evaluation, controlled learner pilot, compare old/new pipeline on the same test corpus, review disagreements, then switch the default. Keep a rollback path until the new B-R layer has stable regression results.

---

# Concerns / Matters That Must Be Addressed

## Critical

1. **B-R source availability and edition:** the repo contains B-R structural extraction data and conventions but not a complete B-R chapter-text/concept corpus. Confirm the edition and make the underlying source/reference materials available for proper cross-framework verification.
2. **Unverified Cambridge/B-R mappings:** many Cambridge records explicitly say `burton_roberts_mapping` is `unverified`. Do not claim the frameworks have been reconciled until this is addressed.
3. **No independent second-pass review for many Cambridge records:** human approval and independent verification are different. Review before enabling constraints in the runtime engine.
4. **Selected-section coverage only:** current Cambridge files cover selected sections, not complete chapters. The app must communicate its coverage honestly and avoid presenting unextracted content as fully modelled.
5. **Benepar/B-R representational mismatch:** direct label substitution is insufficient. The normalizer needs explicit transformation rules, gold tests, and an unresolved path.
6. **Legacy mixed conventions:** the existing lesson/rule system uses Penn-style labels and manually authored claims. Audit it before reusing any content.
7. **Correctness must be explainable:** runtime grammar verdicts must arise from deterministic, source-backed rules and structural evidence; an LLM/CoLA score cannot invent reasons.
8. **Accepted alternatives and ambiguity:** exact tree equality with one Benepar parse is not a valid universal grading criterion.
9. **XP integrity:** client-side XP writes can be manipulated. Use trusted, idempotent award transactions before leaderboards are competitive.
10. **Privacy:** do not expose Clerk user IDs or email-derived names as public leaderboard identities by default.
11. **Copyright:** no copied textbook exercise wording or substantial source prose in the public quiz/lesson bank.
12. **Migration and rollback:** preserve existing accounts/progress and support rolling back the new parser/explanation/content model.

## Non-critical (but should be planned)

1. Cosmetic rewards, themes, titles, and seasonal visuals.
2. Streaks and daily/weekly goals (avoid punishing missed days).
3. More quiz item types beyond the first assessment set.
4. Adaptive difficulty and personalized spaced practice.
5. A richer public explanation library for advanced Cambridge topics.
6. Fine-grained analytics and instructor dashboards.
7. Additional parser providers or a custom parser after sufficient B-R annotation data exists.
8. More elaborate tree animation, transitions, and density presets.
9. Social/classroom competitions, only after privacy and integrity safeguards.

---

# Recommended implementation order

The order below is dependency-driven. UI refinements and content authoring can be prototyped in parallel, but production integration should follow these gates.

| Phase | Main outcome | Exit gate |
|---|---|---|
| 0. Governance and inventory | Confirm source editions, coverage, legacy assets, and status meanings | Source register and migration inventory approved |
| 1. Linguistic architecture | Canonical B-R tree schema, chapter profiles, Cambridge/B-R crosswalk, rule runtime registry | Representative structures and conflicts documented; unresolved items can be flagged |
| 2. Syntax Generator foundation | Benepar candidate + B-R normalizer/validator + gold evaluation | Chapter validators and parser regression suite pass; uncertainty is explicit |
| 3. Shared explanation engine | One evidence payload and explanation composer | Same node/rule yields same evidence in Generator and Builder |
| 4. Lessons | Versioned B-R core curriculum + selected Cambridge insight modules | Source citations and learning-objective checks pass |
| 5. Quizzes | Separate assessment bank, five-item format, review flow | Answer keys, distractors, item sources, and XP calculations validated |
| 6. Syntax Builder | B-R label palette + same evaluator/explanations + alternative-aware grading | Builder and Generator explanation parity tests pass |
| 7. Gamification and leaderboard | Secure XP ledger, leveling, achievements, privacy-safe ranks | Idempotency/security tests pass; opt-in leaderboard works |
| 8. UI/UX and release hardening | Tree density, corrected-word annotation, responsive design, accessibility | Visual/browser E2E, accessibility, and rollback checks pass |

### Critical dependency rule

Do not author a large new lesson or quiz bank before the B-R tree contract and source crosswalk are stable. Do not ship the Builder explanation refactor before the shared analysis/evaluation contract exists. Do not enable competitive leaderboards before XP is server-verified.

---

# Master acceptance checklist

The separate [master checklist](master_checklist.md) is the working sign-off list for all phases. No phase is complete because files were merely created; it is complete only when the specified evidence, reviews, tests, and approvals exist.

## Repository reference points inspected

- [`CONVENTIONS.md`](https://github.com/ybcole/SynTutor/blob/main/CONVENTIONS.md) — B-R tree conventions and source authority.
- [`MASTER_PROMPT.md`](https://github.com/ybcole/SynTutor/blob/main/MASTER_PROMPT.md) — existing B-R content workflow (must be revised for the new architecture).
- [`CAMBRIDGE_EXTRACTION_PROMPT.md`](https://github.com/ybcole/SynTutor/blob/main/CAMBRIDGE_EXTRACTION_PROMPT.md) — Cambridge extraction protocol.
- [`grammar/schema.json`](https://github.com/ybcole/SynTutor/blob/main/grammar/schema.json) and [`grammar/rules/`](https://github.com/ybcole/SynTutor/tree/main/grammar/rules) — structured Cambridge rule data.
- [`web/content/book/`](https://github.com/ybcole/SynTutor/tree/main/web/content/book) — B-R chapter tree/answer data.
- [`server/parse_engine.py`](https://github.com/ybcole/SynTutor/blob/main/server/parse_engine.py), [`server/matrix.py`](https://github.com/ybcole/SynTutor/blob/main/server/matrix.py), [`server/ruleset.py`](https://github.com/ybcole/SynTutor/blob/main/server/ruleset.py) — current parsing and rule engine.
- [`web/js/tree-quiz.js`](https://github.com/ybcole/SynTutor/blob/main/web/js/tree-quiz.js), [`web/js/syntax-builder.js`](https://github.com/ybcole/SynTutor/blob/main/web/js/syntax-builder.js), [`web/js/syntax-builder-ui.js`](https://github.com/ybcole/SynTutor/blob/main/web/js/syntax-builder-ui.js) — current lesson/quiz/builder implementation.
- [`web/js/level.js`](https://github.com/ybcole/SynTutor/blob/main/web/js/level.js), [`web/js/achievements.js`](https://github.com/ybcole/SynTutor/blob/main/web/js/achievements.js), and [`supabase/migrations/`](https://github.com/ybcole/SynTutor/tree/main/supabase/migrations) — existing gamification storage/logic.

---

## Operating instruction for future implementation sessions

Use the matching `master_prompt_*.md` file for the workstream. Before editing, inspect the current main branch and any intervening changes; do not assume this plan describes code added after 6 November 2026. Implement only the assigned phase, preserve existing user data, add tests, report files changed and tests actually run, and stop at the phase's stated approval gate. Do not silently change linguistic conventions or source-derived claims.
