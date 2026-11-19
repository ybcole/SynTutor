# Syntax Pretest/Posttest Evaluation Plan

## Goal

Evaluate whether SynTutor’s interactive syntax-tree analysis improves BSCS students’ ability to judge grammaticality and construct phrase-structure trees, and whether that learning transfers to new sentences with the same structures.

## Recommended Design

- **Participants**: 50 BSCS students, randomly assigned to:
  - **Treatment (n=25)**: SynTutor Syntax Studio + B-R Lessons 1–10
  - **Control (n=25)**: same lesson content and practice time without Syntax Studio
- **If a control group is impossible**: use a one-group pretest/posttest design with a delayed posttest and state that causal claims are limited.
- **Pretest**: 16 items, 45 minutes.
- **Intervention**: 60–90 minutes.
- **Posttest 1**: 32 items, 45–60 minutes, immediately after intervention.
- **Posttest 2 (optional, recommended)**: 16 transfer items only, 1 week later.

## Test Sections

### Section A — Grammaticality Judgment

Students mark each sentence as **Grammatical (G)** or **Ungrammatical (*)**.

Pretest validity items:

1. `The lantern glowed.` — G
2. `The child was asleep.` — G
3. `She gave me the key.` — G
4. `The dog barked loudly in the garden.` — G
5. `The report was leaked.` — G
6. `She said that he left.` — G
7. `Kim has been waiting.` — G
8. `The students who passed were congratulated.` — G
9. `*The lantern glowed the room.` — U
10. `*She gave the key Pat.` — U
11. `*The child was asleep quickly.` — U
12. `*She wants to to leave.` — U
13. `*The students passed were congratulated.` — U
14. `*The report was leaked by.` — U
15. `*He slept the baby.` — U
16. `*She found the book very interestingly.` — U

Recommended pretest use: 8 items (4 G, 4 U) to keep total time manageable. Full bank above can be used if the session allows 90 minutes.

### Section B — Syntax Tree Construction

Students build the tree in SynTutor notation. Expected structures:

1. `very cheerful` → `AP → DEG A`
2. `the lantern` → `NP → DET NOM → N`
3. `She gave me the key.` → `S → NP VP`; `VP → V NP NP`
4. `The dog barked loudly.` → `S → NP VP`; `VP → V AdvP`
5. `Kim has been waiting.` → `S → NP VP`; `VP → AUX VP` with PERF/PROG features
6. `She said that he left.` → `S → NP VP`; `VP → V S-bar`; `S-bar → C S`
7. `What did she see?` → `S-dbar → C2 C1 S`; object gap in VP
8. `She wants to leave.` → `S → NP VP`; `VP → V VP` with non-finite `-tense`

### Section C — Transfer Items

Posttest transfer items use the same structures with different lexical content:

Validity:
1. `The lamp shone.` — G
2. `The boy was asleep.` — G
3. `Pat gave Kim the book.` — G
4. `The cat slept quietly.` — G
5. `The report was published.` — G
6. `She thinks that he stayed.` — G
7. `They have been reading.` — G
8. `The students who passed were praised.` — G
9. `*The lamp shone the room.` — U
10. `*Pat gave the book Kim.` — U
11. `*The boy was asleep quickly.` — U
12. `*She wants to to go.` — U
13. `*The students passed were praised.` — U
14. `*The report was published by.` — U
15. `*He slept the child.` — U
16. `*She found the book very interestingly.` — U

Tree construction:
1. `quite happy` → `AP → DEG A`
2. `a lantern` → `NP → DET NOM → N`
3. `Pat gave Kim the book.` → `S → NP VP`; `VP → V NP NP`
4. `The cat slept quietly.` → `S → NP VP`; `VP → V AdvP`
5. `They have been reading.` → `S → NP VP`; `VP → AUX VP` with PERF/PROG features
6. `She thinks that he stayed.` → `S → NP VP`; `VP → V S-bar`; `S-bar → C S`
7. `Who did he see?` → `S-dbar → C2 C1 S`; object gap in VP
8. `He forced Pat to go.` → `S → NP VP`; `VP → V NP VP` with non-finite `-tense`

## Posttest Structure

- **Posttest A (repeated)**: exact pretest items, to measure direct learning from the same sentences.
- **Posttest B (transfer)**: same structures with different lexical items, to measure whether the learner can apply the analysis to new input.
- Recommended order counterbalancing:
  - Group 1: repeated items first, transfer items second.
  - Group 2: transfer items first, repeated items second.

## Intervention Protocol for 50 Students

1. **Pretest (45 min)**: Section A + Section B.
2. **Intervention (60–90 min)**:
   - Treatment: guided Syntax Studio tasks on B-R Lessons 1–10.
   - Control: same lessons and practice time without Syntax Studio, or delayed waitlist if all students must receive the intervention.
   - Include a guided phase where students analyze the pretest sentences in Syntax Studio, then complete lesson-aligned tree tasks.
3. **Posttest 1 (45–60 min)**: repeated pretest items + transfer items.
4. **Optional Posttest 2 (20 min)**: transfer items only, 1 week later.
5. **SUS survey**: 10 items, 5-point Likert.

## Scoring

- Section A: 1 point per correct G/U judgment.
- Section B: 2 points per item:
  - 1 point for correct top-level structure
  - 1 point for correct labels/features
- Section C: same scoring as Section B.
- Report separately:
  - raw pretest score
  - repeated-item gain
  - transfer-item gain
  - per-lesson/per-structure gain

## Handling and Controls

- Use anonymized participant codes.
- Randomly assign participants to treatment/control if possible.
- Counterbalance item order across groups.
- Administer in a controlled lab with one device per student.
- Record item-level responses, time, and (if available) node-selection/panel interaction logs.
- Exclude incomplete pretests from gain analysis.
- Report attrition separately.

## Analysis

- Paired t-test or Wilcoxon Signed-Rank for pre/post gains.
- Independent t-test or Mann-Whitney for treatment vs control.
- Cohen’s d or rank-biserial effect size.
- Separate analysis for repeated vs transfer items.
- Item difficulty and discrimination analysis.
- SUS composite score and qualitative usability comments.

## Risks and Mitigations

- **Practice effect**: mitigate with control group and delayed posttest.
- **Item memory**: include transfer items; do not treat repeated-item gain alone as learning.
- **Ceiling/floor effects**: pilot the instrument before full administration.
- **Parser mismatch**: every test sentence must be checked against the SynTutor parser before deployment.
- **Control-group limitation**: if all 50 students must use SynTutor, the causal claim is limited to within-subject gain; the transfer items then become the main evidence for generalization.
- **Ethics**: informed consent, voluntary participation, no grade penalty, anonymized data, secure storage.

## Open Question

The design above assumes a control condition is possible. If institutional constraints require all 50 students to receive SynTutor, the plan should use the one-group pretest/posttest fallback and emphasize transfer gain plus delayed posttest rather than treatment-vs-control causality.