# Cambridge Lessons Master

This file contains the editable teaching text and assessments for the 16 Cambridge
grammar lessons in SynTutor. The lessons use original examples grounded in
*The Cambridge Grammar of the English Language* (Huddleston and Pullum, 2002).
Source references use the book’s printed page numbers.

The chapter number identifies the main source chapter. Each lesson teaches a
selected set of constructions from that chapter. The article supplies the reading
sequence. Stage checks work through individual steps, and the assessment or quiz
bank provides further practice. Rule and source identifiers give SynTutor the
references it needs to apply an editorial update to the corresponding lesson.

- schema_version: 1.0.0
- course_version: 2026.11.15
- title: Syntax Foundations and Grammar Analysis
- lessons: 16

## Tracks

- foundations: Syntax Foundations — Ten lessons in the B-R tree convention, followed by a written synthesis.
- grammar: Grammar and Analysis — Cambridge-based articles, worked examples and practice.

---

# Lesson: cgel-clauses — Sentences and embedded clauses

- lesson_id: cgel-clauses
- title: Sentences and embedded clauses
- track: grammar
- chapter: 2
- content_version: 1.1.0
- difficulty: intermediate
- estimated_minutes: 7
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: CLS-001
- source_ids: CGEL-2002-CH02-P0044, CGEL-2002-CH02-P0045
- concept_ids: cgel-sentence-clause
- tree_ids: ch2-33

## Outcomes
- o1: Identify the boundaries of a written sentence and explain how a clause can be embedded within it or coordinated with another clause.

## Key terms
- **written sentence** — A unit of text. In ordinary prose, an initial capital and a terminal mark usually help identify its boundaries.
- **clause** — A grammatical unit organised around a predicate. A typical finite clause has its own subject and predicate.
- **embedded clause** — A clause that serves as part of a larger construction, for example as the complement of a verb.
- **coordination** — The joining of units at the same structural level, often with a word such as and or but.

## Rules
- CLS-001

## Sources
- CGEL-2002-CH02-P0044 (p.44)
- CGEL-2002-CH02-P0045 (p.45)

## Chapter article

### Introduction
“The back door was open.” In a caretaker’s log, that can stand as a complete entry. Now imagine the caretaker writes, “I noticed that the back door was open.” The observation now sits inside the account of what the caretaker noticed. There is still just one line in the log. How many clauses does that line contain?

### Topics
- Finding the written boundary
- Finding a clause inside a clause
- Telling embedding from coordination

### Example
- context: The caretaker records an observation at the end of a shift.
- sentence: I noticed [that the back door was open].
- explanation: The brackets enclose the content of the observation. The sentence runs from “I” to the full stop.

### Preview
- Read the entry as a sentence, then identify its two layers of clause structure.

### Concept: What did the caretaker notice?
Read from the first capital to the full stop. There is one written sentence. Its main clause has *I* as subject and *noticed that the back door was open* as predicate. If you ask what the caretaker noticed, the answer is the whole clause *that the back door was open*. Inside it, *the back door* is subject and *was open* is predicate. The second subject–predicate pair has a job inside the first.

The caretaker has used *that* to introduce the observation. In *I noticed the back door was open*, the same clause is embedded even though the marker is absent. Ask what was noticed and the structure comes into view again.

### Concept: Two clauses can also sit side by side
Suppose the next entry reads, “The back door was open, but the gate was locked.” Here there is still one written sentence, with two clauses joined by *but*. The gate clause does not give the content of a verb in the door clause. Each part makes its own assertion. The connection is coordination, and it accounts for the two clauses without putting either one inside the other.

### Contrast: Where the second clause belongs
- *I noticed [that the back door was open].* The bracketed clause fills the content slot opened by *noticed*.
- *[The back door was open], but [the gate was locked].* Both bracketed clauses belong to the coordination.

### Application
- example: Mara discovered that the spare key was missing. The caretaker called the office, but nobody answered.
- **Analyse the first entry** — Find its embedded clause and identify that clause’s subject and predicate.
- **Analyse the second entry** — Explain what but connects.

### Reveal: Check your analysis
There are two written sentences. In the first, *that the spare key was missing* gives the content of Mara’s discovery. Its subject is *the spare key* and its predicate is *was missing*. In the second, *but* joins two clauses, *the caretaker called the office* and *nobody answered*.

### Recap
Counting written sentences tells you where one entry ends and another begins. Drawing the clause boundaries tells you what is inside each entry. The caretaker’s log can have one sentence with a clause inside another, or one sentence with clauses side by side.

### Self-check
- In “The caretaker thought the door was locked”, what words make up the embedded clause?
- “The door was locked” supplies the content of the thought. “The door” is its subject and “was locked” its predicate.

## Teaching blocks
### Teaching block 1
Start with the full span of the written sentence, then ask which words answer “What did the person notice, say or think?” In these examples the answer gives the bounds of the embedded content clause.

### Teaching block 2
In the tree-convention track, use the established B-R labels. “Written sentence” describes the unit in the text, while “embedded clause” describes the role of a construction inside it.

## Worked example
- sentence: The caretaker thought the lock was broken.
- origin: Original SynTutor example.
- step: Find the matrix subject, “the caretaker”.
- step: Take “the lock was broken” as the content complement of “thought”.
- step: Within that complement, divide “the lock” from its predicate “was broken”.

## Stage checks

#### predict
- prompt: Which stretch is the embedded clause in “Sol realised that the clock had stopped”?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH02-P0044
- hint: First find the complete stretch that tells you what Sol realised.
- options:
  - id: a
    text: the clock
    feedback: “The clock” names only the subject. Include what happened to it.
  - id: b
    text: Sol realised that
    feedback: “Sol realised” belongs to the main clause. The embedded clause begins at that.
  - id: c
    text: that the clock had stopped
    feedback: The content clause includes its marker, subject and predicate.

#### guided
- prompt: In “I believe the caretaker has gone”, why is there an embedded clause even though that is absent?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH02-P0044
- hint: Read “the caretaker has gone” by itself. Which verb gives it a job in the longer sentence?
- options:
  - id: a
    text: The caretaker has gone still gives the content of believe.
    feedback: The clause has its own subject and predicate and functions as the complement of believe.
  - id: b
    text: The word I sets off a separate sentence.
    feedback: Has is a verb within the clause. Include the caretaker and the rest of the predicate.
  - id: c
    text: The word has is itself an embedded clause.
    feedback: I is the main subject. The whole report is still one written sentence.

#### transfer
- prompt: In “Mina noticed the kettle was boiling. She switched it off”, how many written sentences and clauses are there?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH02-P0044
- hint: Count the written boundaries first. Then look for a clause inside the first sentence.
- options:
  - id: a
    text: Two sentences and two clauses
    feedback: The second sentence has one clause, but the first has both the noticing and the observation.
  - id: b
    text: Three sentences and three clauses
    feedback: A clause nested inside a sentence does not have its own written boundary.
  - id: c
    text: Two sentences and three clauses
    feedback: The first sentence contains a main clause and an embedded clause. The second contains one clause.

#### exit
- prompt: Which analysis fits “Mira knew the gate was stuck, but Jo tried the handle”?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH02-P0044
- hint: Underline what but joins, then see whether either side contains a clause of its own.
- options:
  - id: a
    text: Two sentences with no embedding
    feedback: But links ideas inside the one written sentence.
  - id: b
    text: One sentence with two coordinated clauses, one containing an embedded clause
    feedback: But coordinates Mira knew the gate was stuck with Jo tried the handle. The gate was stuck is embedded inside the first coordinate.
  - id: c
    text: One sentence whose three clauses are all coordinates
    feedback: The gate was stuck gives the content of knew, so it sits inside the first coordinate.

## Lesson quizzes (bank)

### cgel-clauses-p1-1
- kind: mcq
- prompt: Read “Jo waited. Mira noticed that the gate was open.” How many written sentences are there?
- answer: b
- rationale: The full stop after waited closes the first sentence. The second contains two clauses within its written boundary.
- options:
  - id: a
    text: Three
  - id: b
    text: Two
  - id: c
    text: One

### cgel-clauses-p2-1
- kind: minimal_pair
- prompt: “The buses stopped.” Now read “I saw that the buses stopped.” What has changed?
- answer: c
- rationale: The buses and stopped still supply a subject and predicate inside the longer sentence.
- options:
  - id: a
    text: The observation is a separate sentence in both cases.
  - id: b
    text: The words have lost their subject and predicate.
  - id: c
    text: The observation is embedded in a larger clause.

### cgel-clauses-p3-1
- kind: structure
- prompt: In “I noticed that the back door was open”, what is the subject of the embedded clause?
- answer: a
- rationale: I is the main subject. Inside the observation, the back door is the subject of was open.
- options:
  - id: a
    text: the back door
  - id: b
    text: I
  - id: c
    text: the back door was open

### cgel-clauses-p4-1
- kind: rule_application
- prompt: How are the clauses related in “The latch clicked, but the door stayed shut”?
- answer: b
- rationale: But joins two complete clauses at the same level. The written sentence includes both.
- options:
  - id: a
    text: The second clause is the object of clicked.
  - id: b
    text: They are coordinates in one sentence.
  - id: c
    text: The first clause is embedded in the second.

### cgel-clauses-p5-1
- kind: repair
- prompt: Which line contains two clauses within one written sentence?
- answer: c
- rationale: In the first line, Ren thinks takes the embedded clause the job is finished.
- options:
  - id: a
    text: Ren finished the job.
  - id: b
    text: Ren checked the tools and the locks.
  - id: c
    text: Ren thinks the job is finished.

### cgel-clauses-p1-2
- kind: mcq
- prompt: In “The log says that the lift failed”, what is the main-clause subject?
- answer: a
- rationale: The log is what says something. The lift is the subject inside what the log says.
- options:
  - id: a
    text: the log
  - id: b
    text: the lift
  - id: c
    text: that the lift failed

### cgel-clauses-p2-2
- kind: minimal_pair
- prompt: In “I heard that the lift had stopped”, which words form the predicate inside the embedded clause?
- answer: a
- rationale: The lift is the embedded subject. Had stopped is what the clause says about it.
- options:
  - id: a
    text: had stopped
  - id: b
    text: the lift had stopped
  - id: c
    text: heard

### cgel-clauses-p3-2
- kind: structure
- prompt: In “Rae knew the road was blocked”, which words express what Rae knew?
- answer: c
- rationale: The entire embedded clause supplies the content of the knowledge, even without that.
- options:
  - id: a
    text: was blocked
  - id: b
    text: Rae knew
  - id: c
    text: the road was blocked

### cgel-clauses-p4-2
- kind: rule_application
- prompt: What does but connect in “Mina phoned, but the line was busy”?
- answer: b
- rationale: Mina phoned and the line was busy each have a subject and a predicate.
- options:
  - id: a
    text: Two subjects of phoned
  - id: b
    text: Two clauses
  - id: c
    text: A verb and its object

### cgel-clauses-p5-2
- kind: repair
- prompt: Which wording puts the delivery report into the content of someone’s speech?
- answer: b
- rationale: The clause the crate had arrived fills the content slot after said.
- options:
  - id: a
    text: The crate arrived. Rae called.
  - id: b
    text: Rae said the crate had arrived.
  - id: c
    text: The crate had arrived, and Rae smiled.

---

# Lesson: cgel-ch01 — Contractions with coordinated subjects

- lesson_id: cgel-ch01
- title: Contractions with coordinated subjects
- track: grammar
- chapter: 1
- content_version: 2.1.0
- difficulty: introductory
- estimated_minutes: 8
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: OTH-615
- source_ids: CGEL-2002-CH01-P0009, CGEL-2002-CH01-P0010
- concept_ids: cgel-ch01-concept
- tree_ids:

## Outcomes
- o1: Find the full subject before deciding whether to contract a form of be.
- o2: Distinguish coordinated noun phrases from coordinated clauses.
- o3: Explain why contractions are possible in some sentences that contain and.

## Key terms
- **contraction** — A reduced form written with an apostrophe, as in you’re for you are.
- **coordinated subject** — One subject made up of coordinated expressions, as in Maya and you.
- **auxiliary reduction** — The shortening of a form such as are to ’re and its attachment to the preceding word.

## Rules
- OTH-615

## Sources
- CGEL-2002-CH01-P0009 (p.9)
- CGEL-2002-CH01-P0010 (p.10)

## Chapter article

### Introduction
“You’re on the list,” the usher tells you. Then the usher checks a second name and adds, “Maya and you are on the list.” Try saying the second line with the same *you’re* that sounded so natural in the first. Something changes when *you* becomes part of the longer subject. To see why, read each line up to the point where the usher tells you what’s true.

### Topics
- Which words make up the subject?
- What does and join?

### Example
- context: At rehearsal, the usher confirms two names together.
- sentence: Maya and you are on the list.
- explanation: Maya and you is the entire subject of are on the list.

### Preview
- Compare a pair of people sharing one predicate with two clauses that each have their own predicate.

### Concept: One predicate for both names
In *You’re on the list*, *you* is the whole subject, and *are* can reduce to *’re*. In *Maya and you are on the list*, the subject is *Maya and you*. The full *are* follows that coordination and begins the predicate shared by both names. The contraction in *Maya and you’re on the list* cannot do that job in this construction. Even if you know the usher means both people, you still need the full form for that wording.

### Concept: When and joins two statements
Now let the usher say, “Maya is on the list, and you’re on the list too.” The first clause already has a predicate of its own. After *and*, *you* is the whole subject of the second clause, so *you’re* works as it did in the opening line. This is why spotting *and* in the vicinity of a contraction tells you very little by itself. Read far enough to see what it joins.

### Contrast: One shared predicate or two separate predicates?
- *Maya and you are on the list.* One coordinated subject, one predicate.
- *Maya is on the list, and you’re on the list too.* Two clauses, each with its own subject and predicate.

### Application
- example: The usher wrote, “Lea and you’re standing by the entrance.” The message is meant to give one instruction to both people.
- **Find the intended subject** — Underline the complete group of people meant by the message.
- **Revise the wording** — Keep one subject and one predicate, then write a version with two clauses.

### Reveal: Check your analysis
*Lea and you are standing by the entrance* keeps the shared predicate. *Lea is standing by the entrance, and you’re standing there too* gives each person a clause of their own. The reduction returns because *you* is once again a whole subject.

### Recap
When you reach *you’re*, try expanding it and finding the subject of *are*. If the subject in this pattern is a coordination ending in *you*, leave *are* in full. If *you* heads a separate clause, the ordinary reduction is available.

### Self-check
- Why is “I’m by the door, and you’re by the window” well formed?
- And joins two clauses. In the second, “you” is the whole subject.

## Teaching blocks
### Teaching block 1
Read “You are on the list” and “Maya and you are on the list” aloud. Ask the learner to bracket the subject before trying the reduction.

### Teaching block 2
Keep the target to contraction with a coordinated subject ending in a pronoun. Contractions with other kinds of subject are a separate question.

## Worked example
- sentence: I’m at the desk, and you’re at the door.
- origin: Original SynTutor example.
- step: Expand the contractions to expose “I am” and “you are”.
- step: Locate the two predicates, “am at the desk” and “are at the door”.
- step: Each pronoun is the whole subject of its own clause, so both reductions work.

## Stage checks

#### predict
- prompt: In “Rae and you are waiting”, which words tell us who is waiting?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH01-P0010
- hint: Find the complete answer to “Who is waiting?”
- options:
  - id: a
    text: you are
    feedback: “You are” includes are, which starts the predicate. Start earlier and stop just before are.
  - id: b
    text: Rae only
    feedback: Rae is one member of the subject. The waiting applies to both Rae and you.
  - id: c
    text: Rae and you
    feedback: Both names belong to the one subject of are waiting.

#### guided
- prompt: The intended subject is “I and you”. Choose the ordinary form for the single shared predicate.
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH01-P0010
- hint: Expand ’re and read the subject and verb separately.
- options:
  - id: a
    text: I and you are on the rota.
    feedback: The coordinated subject takes the full form are in this wording.
  - id: b
    text: I and you is on the rota.
    feedback: Is would fit a single third-person subject. The coordinated subject here uses are.
  - id: c
    text: I and you’re on the rota.
    feedback: You is only one member of that subject. Give the whole pair the full form are.

#### transfer
- prompt: Choose a two-clause version of “Mira and you are on the early shift”.
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH01-P0010
- hint: Give Mira a predicate of her own before and.
- options:
  - id: a
    text: Mira is on the early shift, and you’re on it too.
    feedback: The first version gives Mira and you separate predicates, so you’re is available.
  - id: b
    text: Mira and you’re on the early shift.
    feedback: This still tries to contract the verb after one coordinated subject. Give Mira a complete clause.
  - id: c
    text: Mira and you are both on the early shift.
    feedback: The wording is grammatical, but Mira and you still share a single predicate.

#### exit
- prompt: Why is “At eight, you’re needed” natural but “At eight, Jo and you’re needed” unsuitable for one shared predicate?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH01-P0010
- hint: Compare how much of the line counts as the subject in each case.
- options:
  - id: a
    text: Needed must always follow the full are.
    feedback: Needed can follow ’re when “you” is the whole subject, as the first line shows.
  - id: b
    text: The time phrase blocks all contraction.
    feedback: At eight is present in both lines. The difference is the boundary around the subject.
  - id: c
    text: In the first, you is the whole subject. In the second it is a coordinate within the subject.
    feedback: The contrast comes from the subject boundary. The time phrase and the participle are present in both.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: Which words form the subject in “Maya and you are on the list”?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH01-P0010
- options:
  - id: a
    text: you
    feedback: The one predicate applies to the entire coordinated subject.
  - id: b
    text: you are
    feedback: The one predicate applies to the entire coordinated subject.
  - id: c
    text: Maya and you
    feedback: The one predicate applies to the entire coordinated subject.

#### opening-2
- prompt: What does and join in “I’m at the desk, and you’re at the door”?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH01-P0010
- options:
  - id: a
    text: Two predicates with the same subject
    feedback: Each side has a subject and its own predicate.
  - id: b
    text: Two clauses
    feedback: Each side has a subject and its own predicate.
  - id: c
    text: Two pronouns in one subject
    feedback: Each side has a subject and its own predicate.

#### opening-3
- prompt: In which line can you reduce “you are” to “you’re” without reorganising the clause?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH01-P0010
- options:
  - id: a
    text: After the break, you are next.
    feedback: You is the full subject only in the first wording. In the other two it is part of Jo and you.
  - id: b
    text: Jo and you are next.
    feedback: You is the full subject only in the first wording. In the other two it is part of Jo and you.
  - id: c
    text: I think Jo and you are next.
    feedback: You is the full subject only in the first wording. In the other two it is part of Jo and you.

#### opening-4
- prompt: Which version keeps one shared predicate for Sam and the listener?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH01-P0010
- options:
  - id: a
    text: Sam waved, and you were near the exit.
    feedback: Sam and you is a coordinated subject of the single predicate were near the exit.
  - id: b
    text: Sam was near the exit, and you were there too.
    feedback: Sam and you is a coordinated subject of the single predicate were near the exit.
  - id: c
    text: Sam and you were near the exit.
    feedback: Sam and you is a coordinated subject of the single predicate were near the exit.

#### opening-5
- prompt: In “Lea is ready, and you’re ready too”, where does the second clause begin?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH01-P0010
- options:
  - id: a
    text: at ready after Lea
    feedback: Lea is ready is already a complete clause. The second clause starts with its own subject, you.
  - id: b
    text: at too
    feedback: Lea is ready is already a complete clause. The second clause starts with its own subject, you.
  - id: c
    text: at you’re
    feedback: Lea is ready is already a complete clause. The second clause starts with its own subject, you.

### Closing questions

#### closing-1
- prompt: A volunteer writes “Tess and you’re on duty”, meaning Tess and the reader have the same assignment. Which repair keeps a single clause?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH01-P0010
- options:
  - id: a
    text: Tess and you’re both on duty.
    feedback: The full are can follow Tess and you and begin the shared predicate.
  - id: b
    text: Tess and you are on duty.
    feedback: The full are can follow Tess and you and begin the shared predicate.
  - id: c
    text: Tess is on duty, and you’re on duty.
    feedback: The full are can follow Tess and you and begin the shared predicate.

#### closing-2
- prompt: In “The usher says that I and you are on the list”, what controls are?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH01-P0010
- options:
  - id: a
    text: the usher
    feedback: The relevant subject is inside the clause after that, and it includes both pronouns.
  - id: b
    text: I and you
    feedback: The relevant subject is inside the clause after that, and it includes both pronouns.
  - id: c
    text: you alone
    feedback: The relevant subject is inside the clause after that, and it includes both pronouns.

#### closing-3
- prompt: Which example has a valid contraction after and because a new clause starts there?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH01-P0010
- options:
  - id: a
    text: The list names Jo and you’re.
    feedback: In the first example, Jo checked the door already has a predicate. You is the full subject after and.
  - id: b
    text: Jo and you’re checking the window.
    feedback: In the first example, Jo checked the door already has a predicate. You is the full subject after and.
  - id: c
    text: Jo checked the door, and you’re checking the window.
    feedback: In the first example, Jo checked the door already has a predicate. You is the full subject after and.

#### closing-4
- prompt: Which explanation fits “She and we are ready”?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH01-P0010
- options:
  - id: a
    text: Are is chosen only because we is the nearest word.
    feedback: One shared predicate tells us something about both parts of the subject.
  - id: b
    text: Are follows the coordinated subject she and we.
    feedback: One shared predicate tells us something about both parts of the subject.
  - id: c
    text: We are the only people described as ready.
    feedback: One shared predicate tells us something about both parts of the subject.

#### closing-5
- prompt: How do “Kim and you are leaving” and “Kim is staying, and you’re leaving” differ?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH01-P0010
- options:
  - id: a
    text: The second coordinates two subjects of leaving.
    feedback: In the second example Kim has the predicate is staying, while you has are leaving.
  - id: b
    text: The first coordinates noun phrases and the second coordinates clauses.
    feedback: In the second example Kim has the predicate is staying, while you has are leaving.
  - id: c
    text: Both coordinate clauses.
    feedback: In the second example Kim has the predicate is staying, while you has are leaving.

---

# Lesson: cgel-ch03 — Verb forms and auxiliaries

- lesson_id: cgel-ch03
- title: Verb forms and auxiliaries
- track: grammar
- chapter: 3
- content_version: 2.1.0
- difficulty: introductory
- estimated_minutes: 18
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: CLS-099, CLS-100, CLS-102, CLS-103, CLS-104, CLS-106, CLS-107, CLS-108, CLS-114, CLS-117, CLS-119, CLS-120, COMP-030, COMP-031, COMP-033, COMP-034, COMP-035, COMP-036, COMP-040, COMP-041, COMP-042, MORPH-025, MORPH-026, MORPH-035, MORPH-041, MORPH-056, OTH-098, OTH-102, OTH-158, OTH-182, OTH-216, OTH-377, OTH-439, OTH-453, OTH-458
- source_ids: CGEL-2002-CH03-P0076, CGEL-2002-CH03-P0077, CGEL-2002-CH03-P0079, CGEL-2002-CH03-P0081, CGEL-2002-CH03-P0082, CGEL-2002-CH03-P0089, CGEL-2002-CH03-P0090, CGEL-2002-CH03-P0093, CGEL-2002-CH03-P0094, CGEL-2002-CH03-P0095, CGEL-2002-CH03-P0096, CGEL-2002-CH03-P0097, CGEL-2002-CH03-P0102, CGEL-2002-CH03-P0105, CGEL-2002-CH03-P0106, CGEL-2002-CH03-P0107, CGEL-2002-CH03-P0111, CGEL-2002-CH03-P0112, CGEL-2002-CH03-P0113, CGEL-2002-CH03-P0115, CGEL-2002-CH03-P0141, CGEL-2002-CH03-P0143, CGEL-2002-CH03-P0144, CGEL-2002-CH03-P0146, CGEL-2002-CH03-P0156, CGEL-2002-CH03-P0161, CGEL-2002-CH03-P0167, CGEL-2002-CH03-P0168, CGEL-2002-CH03-P0191, CGEL-2002-CH03-P0197, CGEL-2002-CH03-P0199, CGEL-2002-CH03-P0200
- concept_ids: cgel-ch03-concept
- tree_ids:

## Outcomes
- o1: Choose an auxiliary for an ordinary negative or question, including when do is needed.
- o2: Build an auxiliary chain in order and select the verb form required at each step.
- o3: Explain selected differences in tense, aspect and modal interpretation in context.

## Key terms
- **auxiliary** — A verb that can fill special grammatical roles, such as carrying negation or appearing before the subject in a question.
- **do-support** — The use of auxiliary do when a construction needs an auxiliary and the clause lacks a suitable one.
- **plain form** — The uninflected verb form used after modal auxiliaries and supportive do, as in check.
- **participle** — A verb form used in constructions such as has checked, was checked or is checking.
- **backshift** — A tense choice in an embedded report that takes the original occasion of speaking as a reference point.

## Rules
- CLS-099
- CLS-100
- CLS-102
- CLS-103
- CLS-104
- CLS-106
- CLS-107
- CLS-108
- CLS-114
- CLS-117
- CLS-119
- CLS-120
- COMP-030
- COMP-031
- COMP-033
- COMP-034
- COMP-035
- COMP-036
- COMP-040
- COMP-041
- COMP-042
- MORPH-025
- MORPH-026
- MORPH-035
- MORPH-041
- MORPH-056
- OTH-098
- OTH-102
- OTH-158
- OTH-182
- OTH-216
- OTH-377
- OTH-439
- OTH-453
- OTH-458

## Sources
- CGEL-2002-CH03-P0076 (p.76)
- CGEL-2002-CH03-P0077 (p.77)
- CGEL-2002-CH03-P0079 (p.79)
- CGEL-2002-CH03-P0081 (p.81)
- CGEL-2002-CH03-P0082 (p.82)
- CGEL-2002-CH03-P0089 (p.89)
- CGEL-2002-CH03-P0090 (p.90)
- CGEL-2002-CH03-P0093 (p.93)
- CGEL-2002-CH03-P0094 (p.94)
- CGEL-2002-CH03-P0095 (p.95)
- CGEL-2002-CH03-P0096 (p.96)
- CGEL-2002-CH03-P0097 (p.97)
- CGEL-2002-CH03-P0102 (p.102)
- CGEL-2002-CH03-P0105 (p.105)
- CGEL-2002-CH03-P0106 (p.106)
- CGEL-2002-CH03-P0107 (p.107)
- CGEL-2002-CH03-P0111 (p.111)
- CGEL-2002-CH03-P0112 (p.112)
- CGEL-2002-CH03-P0113 (p.113)
- CGEL-2002-CH03-P0115 (p.115)
- CGEL-2002-CH03-P0141 (p.141)
- CGEL-2002-CH03-P0143 (p.143)
- CGEL-2002-CH03-P0144 (p.144)
- CGEL-2002-CH03-P0146 (p.146)
- CGEL-2002-CH03-P0156 (p.156)
- CGEL-2002-CH03-P0161 (p.161)
- CGEL-2002-CH03-P0167 (p.167)
- CGEL-2002-CH03-P0168 (p.168)
- CGEL-2002-CH03-P0191 (p.191)
- CGEL-2002-CH03-P0197 (p.197)
- CGEL-2002-CH03-P0199 (p.199)
- CGEL-2002-CH03-P0200 (p.200)

## Chapter article

### Introduction
The early shift left one line in the maintenance log: “Nina checked the seal.” On the radio, the supervisor asks, “Did Nina check it?” and hears, “She hasn’t checked it yet.” Those replies turn a short log entry into a useful experiment. Which verb carries the tense? Which one is ready to move in a question? Once you can answer that, a longer line such as *The seal may have been checked* becomes much easier to read.

### Topics
- Finding the auxiliary that can move
- Reading a chain one verb at a time
- Matching tense and aspect to the log

### Example
- context: The supervisor asks about a completed check.
- sentence: Did Nina check the seal?
- explanation: Did carries past tense and precedes the subject. Check stays plain.

### Preview
- Start with the question on the radio, then work out how its logic extends to longer verb groups.

### Concept: The first auxiliary does the visible work
In *Nina checked it*, the ordinary lexical verb *checked* carries past tense. To make the usual negative or yes–no question, English supplies *did*. You get *Nina did not check it* and *Did Nina check it?* Once *did* carries the tense, the following verb is plain *check*. When a suitable auxiliary is already there, use it. *Nina has checked it* gives *Nina has not checked it* and *Has Nina checked it?* In *Might Nina have checked it?*, only *might* goes before Nina.

The same idea explains *What did Nina check?* Here *what* asks for the object, so the auxiliary precedes Nina. In *Who checked it?*, *who* fills the subject position and the ordinary affirmative question needs no *did*. You also hear inversion after *never* and clause-scoped *only*: *Never did Nina miss a check* and *Only then did Nina see the crack*. Compare *Only Nina saw the crack*, where *only* applies to the subject. The same order turns up in formal result patterns with fronted *so* or *such*. Someone writing up the incident might say, *So loud was the alarm that we heard it outside*. Frequency adverbs have their own ordinary positions: *Nina often checks the seal*, *Nina is often late* and *Nina has often checked it*.

### Concept: Each verb hands a form to the next
Read *The seal may have been checked* from left to right. The modal *may* selects plain *have*. Perfect *have* selects the past participle *been*. Here *been* is passive *be*, which selects the past participle *checked*. Compare *Nina may have been checking the seal*. The first two links make the same choices, but this *been* is progressive *be* and selects *checking*. If all four auxiliaries occur, their order is modal, perfect, progressive, passive, as in the possible but cumbersome *The seal might have been being checked*. In the core Standard English pattern a single chain has one central modal. Some dialects have double modals.

The plain form also follows fixed *had better*, as in *We had better check again*. For a negative instruction use *Don’t check it yet*, or even *Don’t be late*. An embedded negative infinitival has a different shape, as in *They told us not to check it yet*. Ordinary dynamic *have* also takes *do* in *Did you have lunch?*, while possessive *have got* gives *Have you got the keys?* When someone says, “I used to check by hand,” *I did too* and *I used to* are two possible replies. Both leave the repeated action understood.

### Concept: The same forms tell different stories about time
Compare *Nina checked the seal at nine yesterday* with *Nina has checked the seal twice since nine*. The first places the check at a definite, finished past time. The present perfect in the second counts events in a period reaching the present. A simple past in the main clause would read differently from *She has worked here ever since*. The progressive also depends on what the verb means. *The tank consists of two chambers* describes a fixed composition. *The tank is leaking* presents an event in progress. An *-ing* ending can appear elsewhere, and the surroundings help tell verb from noun: *carefully checking the gauge* has a verb with an object, while *the careful checking of the gauge* has a noun. Some forms can also be adjectival, as in *very worried*.

When one person reports another’s words, tense can track the original situation. Nina says, “I’m leaving before the next shift arrives.” A later report can be *Nina said she was leaving before the next shift arrived*. If it still applies, the reporter can retain the present in one or both embedded clauses. Within this reading, once the report switches to the reporter’s present standpoint at a higher level, a lower past cannot be explained as a return to backshift. A past with its own independent past-time interpretation is a different matter. The verb also affects whether you can put a perfect in an infinitival. *She seems to have left* places the departure before the apparent evidence. With *begin*, the lower activity starts at the very point of beginning. That gives you *She began to leave*, without room for the earlier departure that *began to have left* would suggest.

### Concept: What the modal leaves open
If the team is planning, *We’ll call when the seal arrives* uses ordinary present tense inside the time adjunct. If it is asking about a delivery time, *We know when the seal will arrive* has an embedded question instead. Compare the open possibility *If the seal leaks, we’ll stop the test* with the remote *If the seal leaked, we would stop the test*. In *I wish we had a spare*, the past form presents the wish as unreal in the current situation. And *Nina could lift the hatch when she was younger* describes a past ability. To report one particular successful lift, *Nina managed to lift the hatch* makes the success explicit. An affirmative *could* has other uses, including possibility and some single-event contexts, so the point is about how to report a past achievement.

### Contrast: What kind of be is this?
- *Nina has been checking the seal.* Progressive be takes checking. Nina is doing the work.
- *The seal has been checked.* Passive be takes checked. The seal undergoes the check.

### Application
- example: The supervisor asks for a report that leaves open whether the seal was checked before lunch.
- **Start with a statement** — Build a clause with might, perfect have and passive be.
- **Turn it into a question** — Move the one auxiliary that belongs before the subject.

### Reveal: Check your analysis
*The seal might have been checked before lunch* keeps the possibility open. The question is *Might the seal have been checked before lunch?* The rest of the chain keeps its order and forms when *might* moves.

### Recap
In the maintenance log, the first auxiliary carries the work of ordinary negation or inversion. Inside a chain, each auxiliary determines the form of the next verb. After those forms are in place, the time expressions and the situation tell you which reading the clause can naturally carry.

### Self-check
- Why does “Has Nina checked it?” have checked while “Did Nina check it?” has check?
- Perfect have selects the past participle checked. Supportive do selects the plain form check.

## Teaching blocks
### Teaching block 1
Ask which verb would move if the sentence became a question. A lexical verb such as “checks” cannot fill that slot on its own in the ordinary construction, so “does” enters and “check” loses the tense ending.

### Teaching block 2
Work from left to right through long verb chains. When two links have the same spelling, use the form they select to decide what job each link is doing.

### Teaching block 3
Ask learners to supply the situation for a tense answer. A finished time, a period continuing to now and a past reporting viewpoint give different reasons for the same visible verb forms.

## Worked example
- sentence: Has the new valve been tested?
- origin: Original SynTutor example.
- step: Put the subject first to recover “The new valve has been tested”.
- step: Identify “has” as the perfect auxiliary and “been” as its past-participle complement.
- step: Identify “been” as passive be because it selects “tested”. In the question only “has” precedes the subject.

## Stage checks

#### predict
- prompt: Change “Nina has checked the seal” to a straightforward negative.
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH03-P0093, CGEL-2002-CH03-P0095
- hint: Look for a verb already capable of carrying not.
- options:
  - id: a
    text: Nina not has checked the seal.
    feedback: Not follows the finite auxiliary in this ordinary clause.
  - id: b
    text: Nina has not checked the seal.
    feedback: The auxiliary has is present and can carry not without do-support.
  - id: c
    text: Nina does not have checked the seal.
    feedback: Have in the affirmative is already an auxiliary here. Keep it in the negative.

#### guided
- prompt: What is the role of be in “The seal was being checked”?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH03-P0105, CGEL-2002-CH03-P0106
- hint: Look at what each form of be selects next.
- options:
  - id: a
    text: Was is passive, and being is perfect.
    feedback: Was is followed by an -ing form, the signature of the progressive. Perfect have is absent.
  - id: b
    text: Both forms of be are progressive.
    feedback: Being selects checked, a past participle. That is the passive link.
  - id: c
    text: Was is progressive, and being is passive.
    feedback: Progressive was selects being. Passive being selects checked and makes the affected seal the subject.

#### transfer
- prompt: Which best presents a response to a hypothetical leak in the remote construction taught here?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH03-P0199, CGEL-2002-CH03-P0200
- hint: Read the condition and the consequence as one hypothetical pair.
- options:
  - id: a
    text: If the valve will leak, we stopped the test.
    feedback: The clause is about a hypothetical response. The two tenses here do not express that reading together.
  - id: b
    text: If the valve leaked, we would stop the test.
    feedback: The preterite presents the condition as remote, and would marks the consequence in this construction.
  - id: c
    text: If the valve leaked, we stop the test.
    feedback: The present stop does not express the ordinary remote consequence. Use the modal that matches the remote condition.

#### exit
- prompt: Which wording explicitly says Rae succeeded once in her attempt to lift the hatch?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH03-P0197
- hint: Distinguish having an ability from using it successfully on one occasion.
- options:
  - id: a
    text: Rae managed to lift the hatch.
    feedback: Managed to reports an achievement. The other examples express past ability and future possibility.
  - id: b
    text: Rae could lift the hatch as a child.
    feedback: This says Rae had the ability, and leaves open whether she used it on a particular occasion.
  - id: c
    text: Rae might lift the hatch tomorrow.
    feedback: This is about a future possibility. It gives no report of a completed lift.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: Which question asks whether Nina tested the valve?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH03-P0095
- options:
  - id: a
    text: Did Nina test the valve?
    feedback: Did carries past tense, so test takes the plain form.
  - id: b
    text: Tested Nina the valve?
    feedback: Did carries past tense, so test takes the plain form.
  - id: c
    text: Did Nina tested the valve?
    feedback: Did carries past tense, so test takes the plain form.

#### opening-2
- prompt: What follows perfect have in “The crew might have ___”?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH03-P0105, CGEL-2002-CH03-P0106
- options:
  - id: a
    text: leave
    feedback: Perfect have selects a past participle. Left is the past participle of leave.
  - id: b
    text: leaving
    feedback: Perfect have selects a past participle. Left is the past participle of leave.
  - id: c
    text: left
    feedback: Perfect have selects a past participle. Left is the past participle of leave.

#### opening-3
- prompt: Which line places an event at a definite finished past time?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH03-P0143, CGEL-2002-CH03-P0144
- options:
  - id: a
    text: Nina has inspected it twice since nine.
    feedback: The simple past fits the dated event. Since nine can instead open a period continuing to the present.
  - id: b
    text: Nina inspected it at nine yesterday.
    feedback: The simple past fits the dated event. Since nine can instead open a period continuing to the present.
  - id: c
    text: Nina has inspected it at nine yesterday.
    feedback: The simple past fits the dated event. Since nine can instead open a period continuing to the present.

#### opening-4
- prompt: Which one is an ordinary question about the subject?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH03-P0095
- options:
  - id: a
    text: Who checked the lock?
    feedback: Who fills the subject slot. What and when ask about other parts.
  - id: b
    text: What did Nina check?
    feedback: Who fills the subject slot. What and when ask about other parts.
  - id: c
    text: When did Nina check the lock?
    feedback: Who fills the subject slot. What and when ask about other parts.

#### opening-5
- prompt: Which wording has both perfect and progressive aspect?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH03-P0105, CGEL-2002-CH03-P0106
- options:
  - id: a
    text: The crew was testing it.
    feedback: Has selects been for the perfect. Progressive been then selects testing.
  - id: b
    text: The crew had tested it.
    feedback: Has selects been for the perfect. Progressive been then selects testing.
  - id: c
    text: The crew has been testing it.
    feedback: Has selects been for the perfect. Progressive been then selects testing.

### Closing questions

#### closing-1
- prompt: How do you ask about a definite possibility in “The alarm might have sounded”?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH03-P0095, CGEL-2002-CH03-P0096
- options:
  - id: a
    text: Might have the alarm sounded?
    feedback: Only the first auxiliary moves before the subject.
  - id: b
    text: Might the alarm have sounded?
    feedback: Only the first auxiliary moves before the subject.
  - id: c
    text: Did the alarm might have sounded?
    feedback: Only the first auxiliary moves before the subject.

#### closing-2
- prompt: Which report combines a modal with a perfect passive?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH03-P0105, CGEL-2002-CH03-P0106
- options:
  - id: a
    text: The key may have been copying.
    feedback: May takes plain have, have takes been, and passive been takes copied.
  - id: b
    text: The key may have been copied.
    feedback: May takes plain have, have takes been, and passive been takes copied.
  - id: c
    text: The key may has been copied.
    feedback: May takes plain have, have takes been, and passive been takes copied.

#### closing-3
- prompt: Lea said, “I’m leaving before Jo returns.” Which report backshifts both embedded present tenses?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH03-P0156
- options:
  - id: a
    text: Lea said she is leaving before Jo returns.
    feedback: Was and returned both shift to the past viewpoint of the original utterance.
  - id: b
    text: Lea said she was leaving before Jo returns.
    feedback: Was and returned both shift to the past viewpoint of the original utterance.
  - id: c
    text: Lea said she was leaving before Jo returned.
    feedback: Was and returned both shift to the past viewpoint of the original utterance.

#### closing-4
- prompt: Which is an ordinary direct negative instruction?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH03-P0089
- options:
  - id: a
    text: Don’t be late.
    feedback: The negative imperative uses plain supportive do, even with be.
  - id: b
    text: Doesn’t be late.
    feedback: The negative imperative uses plain supportive do, even with be.
  - id: c
    text: Not to be late.
    feedback: The negative imperative uses plain supportive do, even with be.

#### closing-5
- prompt: Which wording presents an activity in progress?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH03-P0167, CGEL-2002-CH03-P0168
- options:
  - id: a
    text: The tank is leaking.
    feedback: The progressive presents the leaking as ongoing. The composition statements describe stable states.
  - id: b
    text: The tank consists of two chambers.
    feedback: The progressive presents the leaking as ongoing. The composition statements describe stable states.
  - id: c
    text: The tank has two chambers.
    feedback: The progressive presents the leaking as ongoing. The composition statements describe stable states.

---

# Lesson: cgel-ch04 — Complementation and valency

- lesson_id: cgel-ch04
- title: Complementation and valency
- track: grammar
- chapter: 4
- content_version: 2.1.0
- difficulty: introductory
- estimated_minutes: 12
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: COMP-060, COMP-061, COMP-062, COMP-063, COMP-084, COMP-085, COMP-087, COMP-116, COMP-128, COMP-138, COMP-189, COMP-194, COMP-202
- source_ids: CGEL-2002-CH04-P0220, CGEL-2002-CH04-P0221, CGEL-2002-CH04-P0237, CGEL-2002-CH04-P0247, CGEL-2002-CH04-P0253, CGEL-2002-CH04-P0270, CGEL-2002-CH04-P0275, CGEL-2002-CH04-P0280, CGEL-2002-CH04-P0304, CGEL-2002-CH04-P0306, CGEL-2002-CH04-P0309
- concept_ids: cgel-ch04-concept
- tree_ids:

## Outcomes
- o1: Identify the complement a particular verb and sense allow.
- o2: Distinguish an object, a prepositional complement and an optional adjunct.
- o3: Preserve the correct verb frame when adding recipients, particles or pronouns.

## Key terms
- **valency** — The set of complement patterns available to a word in a particular sense.
- **complement** — A dependent whose type or presence is licensed by the head of its construction.
- **adjunct** — An added dependent specifying circumstances such as time, place or manner.
- **particle** — A short word such as back or off that forms a construction with a verb and may alternate in position with a noun-phrase object.

## Rules
- COMP-060
- COMP-061
- COMP-062
- COMP-063
- COMP-084
- COMP-085
- COMP-087
- COMP-116
- COMP-128
- COMP-138
- COMP-189
- COMP-194
- COMP-202

## Sources
- CGEL-2002-CH04-P0220 (p.220)
- CGEL-2002-CH04-P0221 (p.221)
- CGEL-2002-CH04-P0237 (p.237)
- CGEL-2002-CH04-P0247 (p.247)
- CGEL-2002-CH04-P0253 (p.253)
- CGEL-2002-CH04-P0270 (p.270)
- CGEL-2002-CH04-P0275 (p.275)
- CGEL-2002-CH04-P0280 (p.280)
- CGEL-2002-CH04-P0304 (p.304)
- CGEL-2002-CH04-P0306 (p.306)
- CGEL-2002-CH04-P0309 (p.309)

## Chapter article

### Introduction
At a repair café, one volunteer *gives a visitor a form* and another *explains the form to the visitor*. Both verbs involve something passing from one person to another. Try putting *explains* into the first sentence, though, and the result is *explains a visitor a form*. The meaning you wanted is easy to guess. The sentence still needs the second pattern. This lesson is about how to hear the difference between an idea and the particular grammatical frame a verb gives it.

### Topics
- The complements a verb opens up
- How objects behave when they are short
- Which frame fits a given sense

### Example
- context: The volunteer walks a visitor through the repair steps.
- sentence: The volunteer explained the procedure to the visitor.
- explanation: Explain takes the thing explained as its object. The recipient goes in the to phrase.

### Preview
- Compare explain with give, then look at clauses, objects and particles with the same licensing question in mind.

### Concept: Which complement can follow the verb?
*Give the visitor a form* and *give a form to the visitor* are both available. With *explain*, use *explain the procedure to the visitor*. The choice can be just as specific when the only complement is a preposition phrase. A circuit *consists of* components, while a repair *depends on* the available parts. A verb can also select a clause of a particular shape. A latch *tends to stick*, and a volunteer *enjoys fixing latches*. The fact that both are about an activity gives you no reason to exchange the infinitival and the *-ing* clause.

Complements can be optional. *Sam read while the kettle boiled* leaves what Sam read unstated. In ordinary use, *Sam perused the manual* calls for an object. *While the kettle boiled* can attach to either account as an adjunct. Adding circumstances cannot supply the missing object of *perused*.

### Concept: Where an object belongs
In *She called him*, nominative *she* is the subject and accusative *him* is the object. Keep the object form when a particle is involved: *She switched it off*. A short noun phrase can usually appear in either order with that particle, as in *switched the lamp off* and *switched off the lamp*. A word of literal direction can follow a light noun phrase in a different pattern, as *upstairs* does in *carry the box upstairs*. Follow the construction that the particular verb and dependent allow.

A preposition in an idiomatic frame can also have restrictions of its own. In *the guide we came across*, *across* stays with *came* in the sense “found by chance”. Moving it in *the guide across which we came* disrupts that idiomatic reading. And an ordinary singular count object needs the usual noun-phrase structure. The café can *hire a technician*. The bare role in *elect her chair* is licensed in a different function, where *chair* describes her resulting role.

### Concept: Check the whole frame when you revise
A door can *open* or be *opened*, but an ordinary inanimate subject does not make *construct* or *destroy* inchoative in the same way. *The café constructed a ramp* can become *A ramp was constructed*. The passive supplies a frame for talking about the ramp as subject. *The ramp constructed* will not express the same event.

Rephrasing can also preserve a choice already present in the larger clause. *What the volunteer is doing is checking the latch* makes the ongoing activity explicit in the specifying clause. *What the volunteer did was check the latch* names an action in the plain form. The *do* construction provides more than a blank into which any verb form fits.

### Contrast: Two ways to talk about a recipient
- *She gave the visitor the guide.* Give licenses a recipient before the direct object.
- *She explained the guide to the visitor.* Explain licenses the recipient with to in this use.

### Application
- example: The draft says, “I explained Kim the instructions, and she switched off it.”
- **Repair the recipient frame** — Keep Kim as the recipient of the explanation.
- **Repair the particle frame** — Keep the pronoun it and the particle off.

### Reveal: Check your analysis
*I explained the instructions to Kim, and she switched it off.* The first repair uses the recipient frame available to *explain*. The second puts the unstressed pronoun before the particle.

### Recap
Keep a verb’s sense, its complement types and any optional additions in view together. That is how you can explain why *depends on*, *tends to stick* and *enjoys fixing* each need a different continuation.

### Self-check
- In “We inspected the lamp after lunch”, which dependent is an adjunct?
- “After lunch” supplies the time. “The lamp” is the object of inspected.

## Teaching blocks
### Teaching block 1
Use a single meaning across several verbs, such as informing a visitor. Have the learner test “tell the visitor the result”, “explain the result to the visitor” and “say what happened”.

### Teaching block 2
Optionality is a clue about a dependent, but a verb can license a complement without requiring it on every occasion. Also check whether the verb keeps its sense when the words are removed.

## Worked example
- sentence: We sent her the checklist, then switched the lamp off.
- origin: Original SynTutor example.
- step: Identify “her” as the recipient and “the checklist” as the thing sent.
- step: Use “sent the checklist to her” as another frame available to send.
- step: Replace “the lamp” with “it” and place the pronoun before off.

## Stage checks

#### predict
- prompt: What can complete “The repair depends ___ the parts available”?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH04-P0220
- hint: Keep the verb depend and look for the preposition it selects.
- options:
  - id: a
    text: of
    feedback: Consist uses of. Depend selects a different preposition.
  - id: b
    text: on
    feedback: Depend selects on in this frame.
  - id: c
    text: the
    feedback: Depend does not take the available parts as a bare object in this sense.

#### guided
- prompt: Which sentence uses the ordinary activity complement for enjoy?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH04-P0220, CGEL-2002-CH04-P0221
- hint: Compare the complement endings in tends to fix and enjoys fixing.
- options:
  - id: a
    text: They enjoy that fixing old lamps.
    feedback: That could introduce a finite clause, but the words after it do not form one here.
  - id: b
    text: They enjoy to fix old lamps.
    feedback: A to-infinitival is available after tend. Enjoy selects a different activity complement.
  - id: c
    text: They enjoy fixing old lamps.
    feedback: Enjoy can take the gerund-participial clause fixing old lamps.

#### transfer
- prompt: Choose the edit for “Her handed him the lamp and then switched off it.”
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH04-P0237, CGEL-2002-CH04-P0247, CGEL-2002-CH04-P0253
- hint: Check the subject and recipient first. Then put the small object pronoun beside the particle verb.
- options:
  - id: a
    text: She handed he the lamp and then switched off it.
    feedback: He is nominative and cannot fill the recipient slot here. The unstressed it also needs to precede off.
  - id: b
    text: Her handed him the lamp and then switched it off.
    feedback: The particle frame has been fixed. The finite subject still needs nominative she.
  - id: c
    text: She handed him the lamp and then switched it off.
    feedback: The finite subject is nominative she, him is the object, and unstressed it precedes off.

#### exit
- prompt: What distinguishes a licensed complement from a time adjunct in these examples?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH04-P0220, CGEL-2002-CH04-P0221
- hint: Ask which dependent the verb specifically makes room for.
- options:
  - id: a
    text: A complement always appears before the verb.
    feedback: Complement position varies. Look at what the verb licenses in the relevant sense.
  - id: b
    text: The complement is permitted by the particular verb and sense. The time adjunct adds a circumstance.
    feedback: A verb may license an optional complement, so its licensing is a better first clue than whether you can omit it.
  - id: c
    text: Every complement is obligatory, and every adjunct is a clause.
    feedback: Some complements can be left out, such as the object of read. The licensing test covers both optional and obligatory cases.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: Which wording expresses the material that makes up a mixture?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH04-P0220
- options:
  - id: a
    text: The mixture consists with milk and flour.
    feedback: In this sense consist selects an of phrase.
  - id: b
    text: The mixture consists of milk and flour.
    feedback: In this sense consist selects an of phrase.
  - id: c
    text: The mixture consists milk and flour.
    feedback: In this sense consist selects an of phrase.

#### opening-2
- prompt: In “We perused the manual after lunch”, what is the adjunct?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH04-P0221
- options:
  - id: a
    text: after lunch
    feedback: After lunch specifies time. The manual answers what was perused and is the object.
  - id: b
    text: perused the manual
    feedback: After lunch specifies time. The manual answers what was perused and is the object.
  - id: c
    text: the manual
    feedback: After lunch specifies time. The manual answers what was perused and is the object.

#### opening-3
- prompt: Which version gives the recipient in the ordinary frame for explain?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH04-P0309
- options:
  - id: a
    text: Explain Jo the result.
    feedback: Explain takes the result as direct object and licenses a recipient to phrase.
  - id: b
    text: Explain to Jo to the result.
    feedback: Explain takes the result as direct object and licenses a recipient to phrase.
  - id: c
    text: Explain the result to Jo.
    feedback: Explain takes the result as direct object and licenses a recipient to phrase.

#### opening-4
- prompt: Which sentence describes the latch’s tendency?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH04-P0220, CGEL-2002-CH04-P0221
- options:
  - id: a
    text: The latch tends that it sticks.
    feedback: Tend selects a to-infinitival in this construction.
  - id: b
    text: The latch tends to stick.
    feedback: Tend selects a to-infinitival in this construction.
  - id: c
    text: The latch tends sticking.
    feedback: Tend selects a to-infinitival in this construction.

#### opening-5
- prompt: In “She called him”, what makes him the right form?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH04-P0237
- options:
  - id: a
    text: It is the finite subject.
    feedback: Him is accusative, as expected for an ordinary personal-pronoun object.
  - id: b
    text: It is the object of called.
    feedback: Him is accusative, as expected for an ordinary personal-pronoun object.
  - id: c
    text: It is the person who placed the call.
    feedback: Him is accusative, as expected for an ordinary personal-pronoun object.

### Closing questions

#### closing-1
- prompt: How would you replace “the lamp” with “it” in “She switched off the lamp”?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH04-P0247, CGEL-2002-CH04-P0253
- options:
  - id: a
    text: She switched it off.
    feedback: An ordinary unstressed personal pronoun precedes the particle in this construction.
  - id: b
    text: She switched off they.
    feedback: An ordinary unstressed personal pronoun precedes the particle in this construction.
  - id: c
    text: She switched off it.
    feedback: An ordinary unstressed personal pronoun precedes the particle in this construction.

#### closing-2
- prompt: Which ordinary sentence says that a ramp came into existence through the café’s work?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH04-P0221, CGEL-2002-CH04-P0304, CGEL-2002-CH04-P0306
- options:
  - id: a
    text: A ramp was constructed at the café.
    feedback: Construct does not have the relevant inchoative use. The passive makes a ramp the subject of a complete clause.
  - id: b
    text: A ramp constructed at the café.
    feedback: Construct does not have the relevant inchoative use. The passive makes a ramp the subject of a complete clause.
  - id: c
    text: A ramp destroyed at the café.
    feedback: Construct does not have the relevant inchoative use. The passive makes a ramp the subject of a complete clause.

#### closing-3
- prompt: Why doesn’t “after lunch” provide what perused needs in “We perused after lunch”?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH04-P0221
- options:
  - id: a
    text: It changes perused into a preposition.
    feedback: A time adjunct and the verb’s object perform different jobs.
  - id: b
    text: It says when, while perused normally calls for what was examined.
    feedback: A time adjunct and the verb’s object perform different jobs.
  - id: c
    text: It supplies an object naming the thing examined.
    feedback: A time adjunct and the verb’s object perform different jobs.

#### closing-4
- prompt: Which wording preserves the idiomatic sense “found by chance”?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH04-P0275, CGEL-2002-CH04-P0280
- options:
  - id: a
    text: the manual we came across
    feedback: The idiomatic combination came across resists fronting across with a relative phrase.
  - id: b
    text: the manual across which we came
    feedback: The idiomatic combination came across resists fronting across with a relative phrase.
  - id: c
    text: the manual we came from
    feedback: The idiomatic combination came across resists fronting across with a relative phrase.

#### closing-5
- prompt: Why can you say “We gave Jo a copy” but normally “We explained the result to Jo”?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH04-P0309
- options:
  - id: a
    text: Give licenses the double-object frame. Explain uses a to phrase for the recipient in this sense.
    feedback: The available complement frames are properties of individual verbs and senses.
  - id: b
    text: Jo must always follow the direct object, regardless of verb.
    feedback: The available complement frames are properties of individual verbs and senses.
  - id: c
    text: Explain takes the recipient in the same frame as give.
    feedback: The available complement frames are properties of individual verbs and senses.

---

# Lesson: cgel-ch05 — Nouns and determiners

- lesson_id: cgel-ch05
- title: Nouns and determiners
- track: grammar
- chapter: 5
- content_version: 2.1.0
- difficulty: introductory
- estimated_minutes: 18
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: PHR-028, PHR-043, PHR-044, PHR-054, PHR-062, PHR-065, PHR-079, PHR-080, PHR-083, PHR-084, PHR-087, PHR-088, PHR-110, PHR-126, PHR-128, PHR-133, PHR-140, PHR-157, PHR-161, PHR-164, PHR-197, PHR-220, PHR-240, PHR-247, PHR-258, PHR-283, PHR-289, PHR-290, PHR-295, PHR-305, PHR-321, PHR-334, PHR-343, PHR-347
- source_ids: CGEL-2002-CH05-P0329, CGEL-2002-CH05-P0339, CGEL-2002-CH05-P0343, CGEL-2002-CH05-P0345, CGEL-2002-CH05-P0346, CGEL-2002-CH05-P0349, CGEL-2002-CH05-P0350, CGEL-2002-CH05-P0351, CGEL-2002-CH05-P0352, CGEL-2002-CH05-P0353, CGEL-2002-CH05-P0361, CGEL-2002-CH05-P0371, CGEL-2002-CH05-P0372, CGEL-2002-CH05-P0373, CGEL-2002-CH05-P0375, CGEL-2002-CH05-P0379, CGEL-2002-CH05-P0387, CGEL-2002-CH05-P0388, CGEL-2002-CH05-P0390, CGEL-2002-CH05-P0391, CGEL-2002-CH05-P0409, CGEL-2002-CH05-P0423, CGEL-2002-CH05-P0432, CGEL-2002-CH05-P0435, CGEL-2002-CH05-P0441, CGEL-2002-CH05-P0459, CGEL-2002-CH05-P0461, CGEL-2002-CH05-P0464, CGEL-2002-CH05-P0465, CGEL-2002-CH05-P0470, CGEL-2002-CH05-P0471, CGEL-2002-CH05-P0483, CGEL-2002-CH05-P0493, CGEL-2002-CH05-P0494, CGEL-2002-CH05-P0500, CGEL-2002-CH05-P0501, CGEL-2002-CH05-P0504
- concept_ids: cgel-ch05-concept
- tree_ids:

## Outcomes
- o1: Build noun phrases with determiners suited to the meaning and number of the noun.
- o2: Recognise when a determiner or modifier can do the work of a missing head.
- o3: Find the relevant noun phrase when choosing pronoun case or verb agreement.

## Key terms
- **head** — The central word around which a phrase is built, such as lantern in the old lantern near the door.
- **determiner** — A function in a noun phrase. A determiner can indicate which things are meant or how many there are.
- **count and mass uses** — Count uses treat things as individual units. Mass uses present material or a collection without counting units directly.
- **fused head** — A construction in which one expression does the work of the head as well as another function, as each does in each was labelled.
- **agreement** — The relation that gives us forms such as the box is and the boxes are.

## Rules
- PHR-028
- PHR-043
- PHR-044
- PHR-054
- PHR-062
- PHR-065
- PHR-079
- PHR-080
- PHR-083
- PHR-084
- PHR-087
- PHR-088
- PHR-110
- PHR-126
- PHR-128
- PHR-133
- PHR-140
- PHR-157
- PHR-161
- PHR-164
- PHR-197
- PHR-220
- PHR-240
- PHR-247
- PHR-258
- PHR-283
- PHR-289
- PHR-290
- PHR-295
- PHR-305
- PHR-321
- PHR-334
- PHR-343
- PHR-347

## Sources
- CGEL-2002-CH05-P0329 (p.329)
- CGEL-2002-CH05-P0339 (p.339)
- CGEL-2002-CH05-P0343 (p.343)
- CGEL-2002-CH05-P0345 (p.345)
- CGEL-2002-CH05-P0346 (p.346)
- CGEL-2002-CH05-P0349 (p.349)
- CGEL-2002-CH05-P0350 (p.350)
- CGEL-2002-CH05-P0351 (p.351)
- CGEL-2002-CH05-P0352 (p.352)
- CGEL-2002-CH05-P0353 (p.353)
- CGEL-2002-CH05-P0361 (p.361)
- CGEL-2002-CH05-P0371 (p.371)
- CGEL-2002-CH05-P0372 (p.372)
- CGEL-2002-CH05-P0373 (p.373)
- CGEL-2002-CH05-P0375 (p.375)
- CGEL-2002-CH05-P0379 (p.379)
- CGEL-2002-CH05-P0387 (p.387)
- CGEL-2002-CH05-P0388 (p.388)
- CGEL-2002-CH05-P0390 (p.390)
- CGEL-2002-CH05-P0391 (p.391)
- CGEL-2002-CH05-P0409 (p.409)
- CGEL-2002-CH05-P0423 (p.423)
- CGEL-2002-CH05-P0432 (p.432)
- CGEL-2002-CH05-P0435 (p.435)
- CGEL-2002-CH05-P0441 (p.441)
- CGEL-2002-CH05-P0459 (p.459)
- CGEL-2002-CH05-P0461 (p.461)
- CGEL-2002-CH05-P0464 (p.464)
- CGEL-2002-CH05-P0465 (p.465)
- CGEL-2002-CH05-P0470 (p.470)
- CGEL-2002-CH05-P0471 (p.471)
- CGEL-2002-CH05-P0483 (p.483)
- CGEL-2002-CH05-P0493 (p.493)
- CGEL-2002-CH05-P0494 (p.494)
- CGEL-2002-CH05-P0500 (p.500)
- CGEL-2002-CH05-P0501 (p.501)
- CGEL-2002-CH05-P0504 (p.504)

## Chapter article

### Introduction
After a storm, a crew takes stock of what is in the community hall. Their inventory lists *a lantern*, *two blankets* and *some equipment*. All three entries refer to things you could point to, yet the words that go in front of them behave differently. Now turn an entry into a sentence: “The box of lanterns is by the gate.” Why does *is* go with a line that mentions several lanterns? The answer starts with the same question we need for the inventory: which word is the head of the phrase?

### Topics
- Counting units and choosing determiners
- Knowing what can stand on its own
- Finding the head for agreement and the role for case

### Example
- context: The crew needs a work light, then checks its stock.
- sentence: Each lantern was tested. Each was labelled.
- explanation: In the first sentence, each determines lantern. In the second each does both jobs, and the context supplies lantern as the intended kind of thing.

### Preview
- Start with the inventory names, build phrases around them, then see how those phrases behave in complete clauses.

### Concept: Decide what the inventory is counting
In ordinary prose write *A lantern was missing* or *The old lantern was missing*. A singular count noun in this kind of subject needs a determiner. A checklist heading can simply say *Lantern*, and a bare role can occur in *We elected her chair*. These are different environments from *We hired a technician*, where the noun phrase is an ordinary singular count object.

*Two blankets* counts separate units. *Much equipment* and *a little tape* measure amounts. If the inventory needs to count equipment, say *two pieces of equipment*. Clothing works likewise: *one item of clothing*, or simply *one garment*. Plural *clothes* works in *three items from the pile of clothes*, where *from* introduces a separate selection. Count and mass uses can also belong to the same word: the crew may have *some glass* to clear away and *two glasses* in the kitchen.

### Concept: Read the quantity word and the noun together
*These blankets* and *three blankets* take a plural head. *This blanket*, *one more blanket* and *more than one blanket* have a singular head. *Each lantern*, *every lantern* and *either lantern* also take a singular count noun. *Both lanterns* refers to two, and the coordinating marker in *both the lantern and the torch* introduces a pair of coordinates.

An exact quantity is *three hundred blankets*. An approximate plural quantity can be *hundreds of blankets* or *a great deal of equipment* for a mass amount. The *a* in *a hundred or so blankets* is part of the numeral. With an outer determiner you can keep *one*, as in *the one hundred or so blankets*, or in some cases omit the multiplier, as in *the hundred blankets*. *All* can precede a definite article in *all the blankets*. For one indefinite item in its entirety, ordinary wording is *a whole blanket*. *Such a mess!* and *What a mess!* put the special modifier before *a*.

### Concept: Which words can carry the noun phrase alone?
The inventory keeper can say *Each was labelled* once the lanterns are known. With *every*, the equivalent is *Every one was labelled*. The article *the* also needs a following head or a modifier that can share that job, as in *the largest*. Compare *no lanterns* with *none were left*, and *another lantern* with *bring another*. *Another* is written as a single word in this ordinary use. We will return to *one* and this kind of omission in the lesson on pronouns and pro-forms.

In compounds like *nothing*, a restrictor follows: *nothing useful*. To include several independent descriptions, an ordinary noun phrase such as *no useful new equipment* has room for them in front of the noun. There can be structure inside that pre-head space too. In *an ambitious tax reform proposal*, *tax reform* specifies what the proposal concerns and stays next to *proposal*. The more general description *ambitious* goes outside that pairing.

### Concept: Case and agreement answer different questions
In *She handed him the lantern*, case tells you that *she* is the finite subject and *him* the object. *We arranged for him to bring the lantern* also has *him*, this time as the subject of a *for*-infinitival. In *Who did you say had the lantern?*, *who* is subject of *had* inside the embedded clause. It is equally natural in *Who do you think the new caretaker is?*, where it corresponds to the predicative phrase after *is*. Genitives have their own contrast: *her lantern* and *the lantern is hers*. In *she brought her own*, *own* supplies the understood head together with its modifying role.

For agreement, start with *The box of lanterns is by the gate*. The head is *box*. The nearby *lanterns* can draw you toward *are* by mistake. Actual grammatical patterns sometimes work differently. *The number of lanterns is rising* treats the number as a total, while *A number of lanterns are missing* gives a plural quantifying reading. *The police are outside* and *The cattle are in the far field* have plural agreement. *The news is encouraging* and *Shingles is painful* use singular agreement. A mass aggregate like *furniture* also takes singular agreement. With singular *they*, the verb keeps the forms used with *they*: *Someone brought their own lantern. They are waiting outside*.

### Contrast: The phrase that controls agreement
- *The number of lanterns is falling.* The subject refers to the total.
- *A number of lanterns are missing.* The subject refers to several lanterns.

### Application
- example: The inventory says, “The box of spare batteries are missing. Every were logged yesterday.” Assume the batteries were logged, and one box is missing.
- **Find what is missing** — Identify the head of the first subject and choose the verb form accordingly.
- **Recover the understood noun** — Give every the support it needs and check agreement in the second sentence.

### Reveal: Check your analysis
*The box of spare batteries is missing. Every one was logged yesterday.* The missing thing is the box. *Every one* has a singular head and refers to the batteries one at a time.

### Recap
In the inventory, choosing a determiner starts with how the head is being used. If the head is understood, check which expressions can carry the phrase on their own. Back in a full clause, head and construction explain agreement, while pronoun case depends on the pronoun’s local function.

### Self-check
- Why is “The tray of glasses is full” singular, and why is “The glasses are full” plural?
- The first subject has tray as its head. The second has glasses as its head.

## Teaching blocks
### Teaching block 1
Contrast a number as a total with a number of as a quantifying construction. Let the learner explain what the sentence is about before choosing between is and are.

### Teaching block 2
Start a determiner exercise with a pair the learner can hold fixed, such as each lantern and every lantern. Then remove lantern and ask what has to return to the phrase.

## Worked example
- sentence: The number of lamps is falling, but a number of lanterns are still available.
- origin: Original SynTutor example.
- step: In the first clause, “the number” refers to a total, so choose singular “is”.
- step: In the second clause, “a number of lanterns” means several lanterns, so choose plural “are”.
- step: Check the reading of each noun phrase before looking at the noun immediately beside the verb.

## Stage checks

#### predict
- prompt: Which pair combines ordinary agreements?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH05-P0345, CGEL-2002-CH05-P0346
- hint: Treat police and news as two separate tests of head number.
- options:
  - id: a
    text: The police are here. The news is good.
    feedback: Police has plural agreement, while news has singular agreement despite its ending.
  - id: b
    text: The police are here. The news are good.
    feedback: The police half is right. News takes singular agreement despite its ending.
  - id: c
    text: The police is here. The news are good.
    feedback: Police uses plural agreement in the ordinary collective reference, while news is singular.

#### guided
- prompt: Finish the remark about three labelled lanterns. “I inspected every lantern. Every ___ was safe.”
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH05-P0379
- hint: Try saying “every lantern” and then replacing lantern with a general count word.
- options:
  - id: a
    text: were
    feedback: Were supplies a verb, but the gap needs a noun-like head to go with every.
  - id: b
    text: one
    feedback: Every cannot carry the head function alone in this construction. One supplies the head.
  - id: c
    text: them
    feedback: Them cannot be the head immediately after every. Compare “every one of them”.

#### transfer
- prompt: Which pair distinguishes an exact count from an approximate large quantity?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH05-P0351, CGEL-2002-CH05-P0352, CGEL-2002-CH05-P0353
- hint: Check whether the number phrase states a precise count or describes a broad quantity.
- options:
  - id: a
    text: three hundred blankets / hundreds of blankets
    feedback: The exact numeral uses uninflected hundred. The approximate plural noun takes an of phrase.
  - id: b
    text: three hundred of blankets / hundreds blankets
    feedback: Remove of from the exact numeral and include it after plural hundreds in the approximate phrase.
  - id: c
    text: three hundreds blankets / hundred of blankets
    feedback: An exact count keeps hundred uninflected, while an approximate plural uses hundreds of.

#### exit
- prompt: Which version keeps the cases and agreement in “___ gave ___ the box of keys. The box of keys ___ heavy.”?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH05-P0470, CGEL-2002-CH05-P0471, CGEL-2002-CH05-P0500
- hint: Find the giver, the recipient and the head of the second subject.
- options:
  - id: a
    text: Her / he / are
    feedback: Her and he reverse the expected cases, and “keys” is inside the of phrase, leaving box as the head that controls agreement.
  - id: b
    text: She / he / are
    feedback: She works as subject. The recipient needs him, and the second verb agrees with box.
  - id: c
    text: She / him / is
    feedback: She is the subject, him the recipient object, and the head box controls singular agreement.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: Which inventory item is expressed as an ordinary singular count subject?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH05-P0329, CGEL-2002-CH05-P0339
- options:
  - id: a
    text: Much blanket was missing.
    feedback: A blanket treats one item as countable and supplies the determiner required in this use.
  - id: b
    text: Blanket was missing.
    feedback: A blanket treats one item as countable and supplies the determiner required in this use.
  - id: c
    text: A blanket was missing.
    feedback: A blanket treats one item as countable and supplies the determiner required in this use.

#### opening-2
- prompt: The lanterns were considered one by one. Which continuation can stand after the noun is understood?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH05-P0379, CGEL-2002-CH05-P0409
- options:
  - id: a
    text: Every was labelled.
    feedback: Each can do the work of determiner and head. Every would need one, and the needs something to follow it.
  - id: b
    text: Each was labelled.
    feedback: Each can do the work of determiner and head. Every would need one, and the needs something to follow it.
  - id: c
    text: The was labelled.
    feedback: Each can do the work of determiner and head. Every would need one, and the needs something to follow it.

#### opening-3
- prompt: Choose the ordinary agreement in “The box of matches ___ empty.”
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH05-P0500
- options:
  - id: a
    text: is
    feedback: Box heads the singular subject. Matches is inside the of phrase.
  - id: b
    text: were
    feedback: Box heads the singular subject. Matches is inside the of phrase.
  - id: c
    text: are
    feedback: Box heads the singular subject. Matches is inside the of phrase.

#### opening-4
- prompt: Which wording counts two units without treating equipment itself as a count noun?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH05-P0343, CGEL-2002-CH05-P0345
- options:
  - id: a
    text: two equipments
    feedback: Pieces supplies the countable head. Equipment retains its ordinary mass use.
  - id: b
    text: each equipment
    feedback: Pieces supplies the countable head. Equipment retains its ordinary mass use.
  - id: c
    text: two pieces of equipment
    feedback: Pieces supplies the countable head. Equipment retains its ordinary mass use.

#### opening-5
- prompt: Which phrase has the ordinary structure for a new useful item when the writer uses something?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH05-P0409, CGEL-2002-CH05-P0423
- options:
  - id: a
    text: something useful new
    feedback: Something comes before its post-head restrictor. For several independent modifiers, use a full noun phrase.
  - id: b
    text: something useful
    feedback: Something comes before its post-head restrictor. For several independent modifiers, use a full noun phrase.
  - id: c
    text: useful something
    feedback: Something comes before its post-head restrictor. For several independent modifiers, use a full noun phrase.

### Closing questions

#### closing-1
- prompt: A person left their name. Choose the standard continuation with singular they.
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH05-P0493
- options:
  - id: a
    text: They are on the list.
    feedback: They retains its ordinary verb forms even when it refers to one person.
  - id: b
    text: They is on the list.
    feedback: They retains its ordinary verb forms even when it refers to one person.
  - id: c
    text: They am on the list.
    feedback: They retains its ordinary verb forms even when it refers to one person.

#### closing-2
- prompt: Which phrase means either one of two lanterns in the ordinary construction?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH05-P0387, CGEL-2002-CH05-P0388
- options:
  - id: a
    text: either lantern
    feedback: Either selects a singular count head here. Both lanterns would mean the two together.
  - id: b
    text: both lantern
    feedback: Either selects a singular count head here. Both lanterns would mean the two together.
  - id: c
    text: either lanterns
    feedback: Either selects a singular count head here. Both lanterns would mean the two together.

#### closing-3
- prompt: Which report refers to the total as a figure that is rising?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH05-P0350, CGEL-2002-CH05-P0351
- options:
  - id: a
    text: A number of repairs are finished.
    feedback: The number of repairs names the total. A number of repairs gives a different, quantifying reading.
  - id: b
    text: The number of repairs is rising.
    feedback: The number of repairs names the total. A number of repairs gives a different, quantifying reading.
  - id: c
    text: The number of repairs are rising.
    feedback: The number of repairs names the total. A number of repairs gives a different, quantifying reading.

#### closing-4
- prompt: There are no matches left. Which short answer can stand in for “no matches”?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH05-P0390, CGEL-2002-CH05-P0391
- options:
  - id: a
    text: the
    feedback: None carries the independent negative reading. No introduces a following noun in no matches.
  - id: b
    text: no
    feedback: None carries the independent negative reading. No introduces a following noun in no matches.
  - id: c
    text: none
    feedback: None carries the independent negative reading. No introduces a following noun in no matches.

#### closing-5
- prompt: In “Who did you say had the key?”, what is the local function of who?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH05-P0464, CGEL-2002-CH05-P0465
- options:
  - id: a
    text: Object of say
    feedback: Who belongs with had in the embedded clause. You is the subject of the main clause.
  - id: b
    text: Subject of did you say
    feedback: Who belongs with had in the embedded clause. You is the subject of the main clause.
  - id: c
    text: Subject of had the key
    feedback: Who belongs with had in the embedded clause. You is the subject of the main clause.

---

# Lesson: cgel-ch06 — Enough, and accustomed to

- lesson_id: cgel-ch06
- title: Enough, and accustomed to
- track: grammar
- chapter: 6
- content_version: 2.1.0
- difficulty: intermediate
- estimated_minutes: 9
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: WCAT-046, WCAT-059
- source_ids: CGEL-2002-CH06-P0534, CGEL-2002-CH06-P0535, CGEL-2002-CH06-P0545
- concept_ids: cgel-ch06-concept
- tree_ids:

## Outcomes
- o1: Place enough according to the expression it modifies.
- o2: Recognise prepositional to after accustomed and contrast it with infinitival to.
- o3: Explain the choices in a sentence that contains both constructions.

## Key terms
- **degree** — How far a quality or activity reaches, as in bright enough.
- **prepositional to** — The to in accustomed to the schedule or accustomed to working late.
- **infinitival marker** — The to before a plain verb in an infinitival clause, as in to work late.

## Rules
- WCAT-046
- WCAT-059

## Sources
- CGEL-2002-CH06-P0534 (p.534)
- CGEL-2002-CH06-P0535 (p.535)
- CGEL-2002-CH06-P0545 (p.545)

## Chapter article

### Introduction
At the end of a rehearsal a singer asks, “Was I loud enough?” The sound engineer asks, “Did we have enough time?” Both are asking whether something reached a threshold. Yet *enough* sits on a different side of the word it goes with. A little later the engineer says, “I’m accustomed to working late.” Here, too, a familiar little word gets its behaviour from its surroundings. The way to read both expressions is to look at what they belong to.

### Topics
- Enough with a quality, action or amount
- The two uses of to

### Example
- context: The sound engineer checks the recording.
- sentence: Did we speak clearly enough for the recording?
- explanation: Enough follows clearly because the question is about the degree of clarity.

### Preview
- Keep one rehearsal in mind as you compare the positions of enough and the complements after to.

### Concept: Enough follows a quality or activity
*Loud enough* asks about volume and *clearly enough* asks how clearly people spoke. *We practised enough* asks about the extent of the practice. When a short direct object is present, keep it beside the verb: *We practised the ending enough*. With some verbs and prepositional complements, more than one order works, as in *They didn’t care enough about the delay* and *They didn’t care about the delay enough*.

When you are talking about an amount of a thing, the usual order is *enough time*, *enough chairs* or *enough practice*. You may also see *time enough to rehearse*, especially with more words after *enough*. So *enough practice to finish the piece* measures the amount of practice, and *practised enough to finish the piece* measures the activity. The position changes because the expression that *enough* goes with changes.

### Concept: Let a noun phrase show you which to you have
The sound engineer is *accustomed to the late finish*. Replace *the late finish* with a clause for the activity and you get *accustomed to finishing late*. In both, *to* is a preposition. Compare *The engineer planned to finish late*. The verb *planned* introduces an infinitival clause here, and the form after its *to* is plain *finish*. You can see the two structures together in *The engineer is accustomed to working late to finish the mix*. The first phrase tells you what has become familiar. The second gives a purpose.

### Contrast: Where enough gets its place
- *The room was quiet enough.* Enough modifies quiet, an adjective.
- *We had enough quiet to finish the recording.* Enough specifies an amount of quiet.

### Application
- example: The note says, “We are accustomed to record at night, but we haven’t tested enough the microphone.”
- **Keep the familiar routine** — Choose the form appropriate after accustomed to.
- **Keep microphone as the direct object** — Place enough where it measures the testing.

### Reveal: Check your analysis
*We are accustomed to recording at night, but we haven’t tested the microphone enough.* In the first half, *recording at night* follows the preposition *to*. In the second, *the microphone* stays beside its verb and *enough* follows the object.

### Recap
When *enough* is about a quality, manner or action, find that expression before placing it. When you see *to*, try working out what licenses it. *Accustomed to the routine* gives you the pattern for *accustomed to working late*.

### Self-check
- How can you tell that the first to in “She is accustomed to staying late to edit” is a preposition?
- “Accustomed to the late nights” takes a noun phrase in the same slot. The second to introduces an infinitival purpose.

## Teaching blocks
### Teaching block 1
Try “enough light” beside “bright enough” before introducing category names. Ask what would need to increase for each statement to become true.

### Teaching block 2
Keep “accustomed to the schedule” on screen as the learner changes schedule to an activity. The preposition remains in place.

## Worked example
- sentence: The crew checked the wiring enough to trust it.
- origin: Original SynTutor example.
- step: Find the extent being measured, namely the checking.
- step: Keep “the wiring” immediately after its verb and let “enough” follow the short object.
- step: Read “to trust it” as the threshold reached by the amount of checking.

## Stage checks

#### predict
- prompt: Choose the natural comparison that contains an adjective phrase followed by enough.
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH06-P0534
- hint: Decide whether the example measures an amount or grades a quality.
- options:
  - id: a
    text: bright enough
    feedback: Bright names a quality and is graded by a following enough. The other examples measure amounts.
  - id: b
    text: enough light
    feedback: Here enough specifies a quantity of light. The exercise asks for a quality graded by enough.
  - id: c
    text: enough lamps
    feedback: Lamps are counted or quantified. Look for a word describing how bright something is.

#### guided
- prompt: Choose the complement that fits “They grew accustomed to ___ the first flight.”
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH06-P0545
- hint: Try “accustomed to the journey” to identify the kind of to.
- options:
  - id: a
    text: they take
    feedback: A finite clause with they take does not fit right after that preposition.
  - id: b
    text: taking
    feedback: To is a preposition after accustomed, and taking introduces its activity complement.
  - id: c
    text: take
    feedback: Take is a plain form. Prepositional to after accustomed takes an activity form in -ing.

#### transfer
- prompt: Revise “We’re accustomed to play outside but haven’t practised enough the ending.”
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH06-P0534, CGEL-2002-CH06-P0535, CGEL-2002-CH06-P0545
- hint: Work on the part after accustomed separately from the part after practised.
- options:
  - id: a
    text: We’re accustomed to play outside but haven’t practised the ending enough.
    feedback: The position of enough is right. The activity after accustomed to needs playing.
  - id: b
    text: We’re accustomed to playing outside but haven’t practised the ending enough.
    feedback: Use playing after prepositional to. Put enough after the direct object.
  - id: c
    text: We’re accustomed to playing outside but haven’t enough practised the ending.
    feedback: Playing fits after accustomed to. For extent, put enough after the short object the ending.

#### exit
- prompt: Which sentence uses two different kinds of to?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH06-P0534, CGEL-2002-CH06-P0545
- hint: Look at the word immediately after each to and at what introduced it.
- options:
  - id: a
    text: Jo is accustomed to staying late to finish the mix.
    feedback: The first to in the correct line heads a preposition phrase. The second introduces an infinitival of purpose.
  - id: b
    text: Jo is accustomed to the late shift and to the noise.
    feedback: Both instances are prepositions before noun phrases. Look for one serving another job.
  - id: c
    text: Jo plans to stay late to finish the mix.
    feedback: Both instances introduce infinitivals here, as the plain verbs stay and finish show.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: Finish “The room was quiet ___ to record in.”
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH06-P0534
- options:
  - id: a
    text: enough
    feedback: Degree enough follows the adjective quiet.
  - id: b
    text: with enough
    feedback: Degree enough follows the adjective quiet.
  - id: c
    text: of enough
    feedback: Degree enough follows the adjective quiet.

#### opening-2
- prompt: Which phrase says that late work is already familiar to Jo?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH06-P0545
- options:
  - id: a
    text: Jo plans to work late.
    feedback: Accustomed takes prepositional to with a gerund-participial complement. Plans to expresses an intention.
  - id: b
    text: Jo is accustomed to work late.
    feedback: Accustomed takes prepositional to with a gerund-participial complement. Plans to expresses an intention.
  - id: c
    text: Jo is accustomed to working late.
    feedback: Accustomed takes prepositional to with a gerund-participial complement. Plans to expresses an intention.

#### opening-3
- prompt: Why do “warm enough” and “accustomed to working” call for different form choices?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH06-P0534, CGEL-2002-CH06-P0545
- options:
  - id: a
    text: Both are infinitival constructions.
    feedback: The first choice is about modifier position. The second depends on which kind of to is present.
  - id: b
    text: Enough follows the adjective it grades. To after accustomed licenses the -ing clause.
    feedback: The first choice is about modifier position. The second depends on which kind of to is present.
  - id: c
    text: Both need a plain verb after to.
    feedback: The first choice is about modifier position. The second depends on which kind of to is present.

#### opening-4
- prompt: Complete “We had ___ chairs for everyone.”
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH06-P0534
- options:
  - id: a
    text: enough
    feedback: The blank is before chairs, the ordinary position for enough when it specifies the amount.
  - id: b
    text: chairs were enough
    feedback: The blank is before chairs, the ordinary position for enough when it specifies the amount.
  - id: c
    text: chairs enough
    feedback: The blank is before chairs, the ordinary position for enough when it specifies the amount.

#### opening-5
- prompt: Which phrase lets you replace the activity with “the new schedule” without changing the frame?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH06-P0545
- options:
  - id: a
    text: accustomed to following the schedule
    feedback: Accustomed to the new schedule preserves the prepositional frame.
  - id: b
    text: planning to follow the schedule
    feedback: Accustomed to the new schedule preserves the prepositional frame.
  - id: c
    text: hoping to follow the schedule
    feedback: Accustomed to the new schedule preserves the prepositional frame.

### Closing questions

#### closing-1
- prompt: Keep the direct object in “We tested the microphone” and add enough.
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH06-P0535
- options:
  - id: a
    text: We enough tested the microphone.
    feedback: The short direct object stays next to tested, with enough after it.
  - id: b
    text: We tested enough the microphone.
    feedback: The short direct object stays next to tested, with enough after it.
  - id: c
    text: We tested the microphone enough.
    feedback: The short direct object stays next to tested, with enough after it.

#### closing-2
- prompt: What is enough about in “We practised the song enough”?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH06-P0534
- options:
  - id: a
    text: The number of songs
    feedback: Enough measures the action. The song identifies what was practised.
  - id: b
    text: The quality of the song itself
    feedback: Enough measures the action. The song identifies what was practised.
  - id: c
    text: The extent of the practice
    feedback: Enough measures the action. The song identifies what was practised.

#### closing-3
- prompt: Which expression contains infinitival to?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH06-P0545
- options:
  - id: a
    text: planned to stay late
    feedback: The infinitival marker is followed by the plain verb stay. The other uses take a prepositional complement.
  - id: b
    text: accustomed to the late shift
    feedback: The infinitival marker is followed by the plain verb stay. The other uses take a prepositional complement.
  - id: c
    text: accustomed to staying late
    feedback: The infinitival marker is followed by the plain verb stay. The other uses take a prepositional complement.

#### closing-4
- prompt: In “We’re accustomed to staying late, but we don’t have enough time”, why does enough go first in its phrase?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH06-P0534, CGEL-2002-CH06-P0545
- options:
  - id: a
    text: It belongs to accustomed.
    feedback: Enough and time form a noun phrase that measures an amount.
  - id: b
    text: It modifies the adjective late.
    feedback: Enough and time form a noun phrase that measures an amount.
  - id: c
    text: It specifies the amount of time.
    feedback: Enough and time form a noun phrase that measures an amount.

#### closing-5
- prompt: Which pair shows two possible positions with a prepositional complement of care?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH06-P0535
- options:
  - id: a
    text: care about enough it / care about it enough
    feedback: With care, enough can precede or follow the whole about phrase.
  - id: b
    text: enough care about it / care about enough it
    feedback: With care, enough can precede or follow the whole about phrase.
  - id: c
    text: care enough about it / care about it enough
    feedback: With care, enough can precede or follow the whole about phrase.

---

# Lesson: cgel-ch07 — Time words and connecting words

- lesson_id: cgel-ch07
- title: Time words and connecting words
- track: grammar
- chapter: 7
- content_version: 2.1.0
- difficulty: intermediate
- estimated_minutes: 8
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: PHR-381, PHR-420
- source_ids: CGEL-2002-CH07-P0604, CGEL-2002-CH07-P0632
- concept_ids: cgel-ch07-concept
- tree_ids:

## Outcomes
- o1: Identify what can follow before and related prepositions introducing clauses.
- o2: Put ago and elapsed-time on after the duration phrase.
- o3: Distinguish backward counting from the present from forward counting from an earlier event.

## Key terms
- **preposition** — A word that heads a preposition phrase. In the Cambridge analysis it can take a noun phrase or clause as complement, among other possibilities.
- **content clause** — A clause such as the siren rang, which can serve as a complement inside a larger construction.
- **reference point** — The time from which an expression counts backward or forward.

## Rules
- PHR-381
- PHR-420

## Sources
- CGEL-2002-CH07-P0604 (p.604)
- CGEL-2002-CH07-P0632 (p.632)

## Chapter article

### Introduction
An archivist reads two accounts of the same storm. One was written during the cleanup: “We moved the boats before the siren rang.” The other opens with “Ten years on, the old slipway was still there.” The first line puts one event before another. The second measures forward from an earlier event. To make sense of either line, you need to find where the time expression begins, which side its dependent goes on and what point in time it uses.

### Topics
- Before with a noun phrase or a clause
- Counting back with ago and forward with on

### Example
- context: An archivist dates the evacuation relative to the alarm.
- sentence: They moved the boats before the siren rang.
- explanation: The siren rang is the clause that completes the before phrase.

### Preview
- Compare before the siren with before the siren rang, then switch to expressions that put the duration first.

### Concept: A whole clause can follow before
Someone might write *before lunch* or *before the siren rang*. In the first, *lunch* is a noun phrase. In the second, *the siren rang* has its own subject and verb. In the Cambridge analysis, *before* heads the preposition phrase in both. Try fitting *that* immediately after *before* in the second example and the construction breaks down.

Now compare *We know the siren rang* and *We know that the siren rang*. The verb *know* allows the marker. The preposition *provided* can allow it too, as in *They can stay provided (that) the water recedes*. That comparison matters when you edit. Look at the particular word and the complement it allows before deciding whether to add *that*.

### Concept: A duration can come first
Imagine the archivist is writing in 2026. *The flood happened ten years ago* counts back ten years from the time of writing. The duration comes first: *ten years ago*. Now imagine the account has already established the flood as its starting point. *Ten years on, the landing was still closed* counts ten years forward from the flood. This use of *on* likewise follows the duration. Cambridge analyses both as exceptional prepositions with the complement in front of the head.

### Contrast: Find the reference point
- *The landing closed ten years ago.* Count back from the writer’s present.
- *Ten years on, the landing was still closed.* Count forward from an earlier point supplied by the account.

### Application
- example: A report dated 2026 says, “The volunteers left before that the roads flooded. That was ago ten years. Two years on, the new road opened.”
- **Restore the clause after before** — Keep the event that sets the time of the departure.
- **Correct the word order and date the opening** — Use the writer’s present for ago and the earlier event for on.

### Reveal: Check your analysis
*The volunteers left before the roads flooded. That was ten years ago. Two years on, the new road opened.* The earlier event is placed in 2016, so two years on puts the opening in 2018.

### Recap
A time expression can take a clause, as *before the siren rang* does. Some take a duration on the left, as *ten years ago* and *ten years on* do. Read the whole phrase before deciding what time it identifies.

### Self-check
- In a letter dated 2026, “The station closed five years ago. Three years on, it reopened.” In which year did it reopen?
- It closed in 2021 and reopened in 2024. Three years on counts from the closure.

## Teaching blocks
### Teaching block 1
Treat “before the alarm” and “before the alarm sounded” as a pair. Ask what comes after before in each and have the learner test the effect of inserting that in the clause.

### Teaching block 2
Write the date of the telling above the date of the event. Draw the two offsets in words before asking a learner to turn them into an ago or on phrase.

## Worked example
- sentence: They checked the tide before the team left. Three weeks on, they checked it again.
- origin: Original SynTutor example.
- step: Find “the team left”, the clause licensed by “before”.
- step: Read “three weeks on” as a forward step from the earlier occasion in the account.
- step: Keep the duration “three weeks” before “on”.

## Stage checks

#### predict
- prompt: Which version leaves the events in the same order and repairs “We moved before that the siren rang”?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH07-P0604
- hint: Hold the order of the events fixed. Change only the string after before.
- options:
  - id: a
    text: We moved before did the siren ring.
    feedback: The clause after before keeps subject–verb order. It is not phrased as a direct question.
  - id: b
    text: We moved after the siren rang.
    feedback: After reverses the time relation given in the original line.
  - id: c
    text: We moved before the siren rang.
    feedback: Removing that preserves both the events and their time relation.

#### guided
- prompt: Which pair puts the duration on the correct side in both constructions?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH07-P0632
- hint: Read the duration as a single phrase before looking at the head.
- options:
  - id: a
    text: three days ago / three days on
    feedback: Both ago and elapsed-time on follow their duration complement.
  - id: b
    text: ago three days / three days on
    feedback: The first expression puts ago on the wrong side of the duration.
  - id: c
    text: three days ago / on three days
    feedback: The ago phrase works. Use the same duration-first order with elapsed-time on.

#### transfer
- prompt: Written in 2026: “The hall closed six years ago. One year on, the work began.” When did the work begin?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH07-P0632
- hint: Use the date of the report for ago and the closure for on.
- options:
  - id: a
    text: 2027
    feedback: The report date is used for ago. On measures from the event it just established.
  - id: b
    text: 2019
    feedback: That would be one year before the 2020 closure. On counts forward.
  - id: c
    text: 2021
    feedback: Ago places the closure in 2020. On measures forward one year from the closure.

#### exit
- prompt: Which explanation distinguishes “before the siren rang” from “five years ago”?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH07-P0604, CGEL-2002-CH07-P0632
- hint: Identify the type and position of the dependent in each phrase.
- options:
  - id: a
    text: Both heads must come before the dependent.
    feedback: Ago shows that a head can follow its dependent in these expressions.
  - id: b
    text: Before precedes its clause. Ago follows its duration and counts back from the present.
    feedback: Before and ago head time phrases with different complement types and different orders.
  - id: c
    text: Ago introduces a clause just as before does.
    feedback: Before takes a clause here. Ago goes with the duration phrase five years.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: Which part of “We left before the bell rang” is a clause inside the before phrase?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH07-P0604
- options:
  - id: a
    text: before the bell
    feedback: The bell is the subject and rang is its predicate. Together they form the complement of before.
  - id: b
    text: the bell rang
    feedback: The bell is the subject and rang is its predicate. Together they form the complement of before.
  - id: c
    text: the bell
    feedback: The bell is the subject and rang is its predicate. Together they form the complement of before.

#### opening-2
- prompt: Choose the usual wording for a memory from three weeks earlier.
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH07-P0632
- options:
  - id: a
    text: I saw it three weeks ago.
    feedback: Ago follows the complete duration phrase.
  - id: b
    text: I saw it ago three weeks.
    feedback: Ago follows the complete duration phrase.
  - id: c
    text: I saw it three ago weeks.
    feedback: Ago follows the complete duration phrase.

#### opening-3
- prompt: In “The bridge closed in 2018. Two years on, it reopened”, when did it reopen?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH07-P0632
- options:
  - id: a
    text: Two years after the reader sees the text
    feedback: On counts forward from the closure mentioned in the first sentence.
  - id: b
    text: 2016
    feedback: On counts forward from the closure mentioned in the first sentence.
  - id: c
    text: 2020
    feedback: On counts forward from the closure mentioned in the first sentence.

#### opening-4
- prompt: Choose the ordinary clause after before.
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH07-P0604
- options:
  - id: a
    text: before that the rain started
    feedback: Before permits the content clause without that and with ordinary subject–verb order.
  - id: b
    text: before the rain started
    feedback: Before permits the content clause without that and with ordinary subject–verb order.
  - id: c
    text: before did the rain start
    feedback: Before permits the content clause without that and with ordinary subject–verb order.

#### opening-5
- prompt: What is the default reference point in “The bridge reopened two years ago”?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH07-P0632
- options:
  - id: a
    text: The time of speaking or writing
    feedback: Ago ordinarily counts backward from the speaker or writer’s present.
  - id: b
    text: Any date mentioned in an earlier sentence
    feedback: Ago ordinarily counts backward from the speaker or writer’s present.
  - id: c
    text: The time when the bridge first closed
    feedback: Ago ordinarily counts backward from the speaker or writer’s present.

### Closing questions

#### closing-1
- prompt: Which pair permits the same clause with or without that?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH07-P0604
- options:
  - id: a
    text: We waited before (that) the gate shut.
    feedback: Know permits either form. The time prepositions in the other examples do not take the extra marker in those uses.
  - id: b
    text: We left after (that) the bells rang.
    feedback: Know permits either form. The time prepositions in the other examples do not take the extra marker in those uses.
  - id: c
    text: We know (that) the gate is shut.
    feedback: Know permits either form. The time prepositions in the other examples do not take the extra marker in those uses.

#### closing-2
- prompt: Which expression can mean “five years later”?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH07-P0632
- options:
  - id: a
    text: five years ago
    feedback: Elapsed-time on follows the duration and measures forward from a reference point.
  - id: b
    text: on five years
    feedback: Elapsed-time on follows the duration and measures forward from a reference point.
  - id: c
    text: five years on
    feedback: Elapsed-time on follows the duration and measures forward from a reference point.

#### closing-3
- prompt: A diary written in 2026 reads, “The store closed four years ago.” What year does the writer mean?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH07-P0632
- options:
  - id: a
    text: 2022
    feedback: Four years before 2026 is 2022.
  - id: b
    text: 2030
    feedback: Four years before 2026 is 2022.
  - id: c
    text: 2024
    feedback: Four years before 2026 is 2022.

#### closing-4
- prompt: Which line shows a preposition that can take a that-clause in the construction given?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH07-P0604
- options:
  - id: a
    text: We left after that the roads flooded.
    feedback: Provided allows the marker. Before and after in these time-clause constructions do not.
  - id: b
    text: You can come provided that the roads are clear.
    feedback: Provided allows the marker. Before and after in these time-clause constructions do not.
  - id: c
    text: We left before that the roads flooded.
    feedback: Provided allows the marker. Before and after in these time-clause constructions do not.

#### closing-5
- prompt: In “Ten years on, the harbour was still empty”, which words supply the duration?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH07-P0632
- options:
  - id: a
    text: on
    feedback: Ten years is the duration phrase placed before elapsed-time on.
  - id: b
    text: ten years
    feedback: Ten years is the duration phrase placed before elapsed-time on.
  - id: c
    text: still empty
    feedback: Ten years is the duration phrase placed before elapsed-time on.

---

# Lesson: cgel-ch10 — Clause types and questions

- lesson_id: cgel-ch10
- title: Clause types and questions
- track: grammar
- chapter: 10
- content_version: 2.1.0
- difficulty: intermediate
- estimated_minutes: 13
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: CLS-126, CLS-128, CLS-130, CLS-131, CLS-156, CLS-171, CLS-182, CLS-183, CLS-201, CLS-213, CLS-217, CLS-229, CLS-268, CLS-270
- source_ids: CGEL-2002-CH10-P0856, CGEL-2002-CH10-P0857, CGEL-2002-CH10-P0874, CGEL-2002-CH10-P0885, CGEL-2002-CH10-P0892, CGEL-2002-CH10-P0893, CGEL-2002-CH10-P0903, CGEL-2002-CH10-P0909, CGEL-2002-CH10-P0910, CGEL-2002-CH10-P0911, CGEL-2002-CH10-P0919, CGEL-2002-CH10-P0920, CGEL-2002-CH10-P0934, CGEL-2002-CH10-P0935, CGEL-2002-CH10-P0943, CGEL-2002-CH10-P0944
- concept_ids: cgel-ch10-concept
- tree_ids:

## Outcomes
- o1: Choose clause order for an ordinary direct question or its embedded counterpart.
- o2: Recognise special question patterns and form response-seeking tags.
- o3: Distinguish a command, an exclamation and a question by their grammar.

## Key terms
- **closed interrogative** — A question clause with a limited set of answers, typically yes or no.
- **open interrogative** — A question clause that asks for missing information, commonly with who, what, where or how.
- **question tag** — A short auxiliary-and-pronoun question attached to a clause, as in aren’t they?
- **imperative** — A clause type commonly used for instructions, with a plain-form verb and often an understood subject.

## Rules
- CLS-126
- CLS-128
- CLS-130
- CLS-131
- CLS-156
- CLS-171
- CLS-182
- CLS-183
- CLS-201
- CLS-213
- CLS-217
- CLS-229
- CLS-268
- CLS-270

## Sources
- CGEL-2002-CH10-P0856 (p.856)
- CGEL-2002-CH10-P0857 (p.857)
- CGEL-2002-CH10-P0874 (p.874)
- CGEL-2002-CH10-P0885 (p.885)
- CGEL-2002-CH10-P0892 (p.892)
- CGEL-2002-CH10-P0893 (p.893)
- CGEL-2002-CH10-P0903 (p.903)
- CGEL-2002-CH10-P0909 (p.909)
- CGEL-2002-CH10-P0910 (p.910)
- CGEL-2002-CH10-P0911 (p.911)
- CGEL-2002-CH10-P0919 (p.919)
- CGEL-2002-CH10-P0920 (p.920)
- CGEL-2002-CH10-P0934 (p.934)
- CGEL-2002-CH10-P0935 (p.935)
- CGEL-2002-CH10-P0943 (p.943)
- CGEL-2002-CH10-P0944 (p.944)

## Chapter article

### Introduction
At a school rehearsal, the director has four things to say: “Where did you put the keys?” “I wonder where you put them.” “Everybody check your pockets.” “What a relief!” Each line has a different shape, even though all four belong to the same little exchange. The first two are particularly revealing. Both concern the location of the keys, but only one puts *did* before its subject.

### Topics
- Direct and embedded questions
- Questions in conversation
- Instructions and exclamations

### Example
- context: A cast member asks about a missing prop.
- sentence: Where did you put the keys?
- explanation: Where asks for a location. Did comes before you, and put has its plain form.

### Preview
- Follow the questions about the missing keys, then see how the director turns the same situation into a tag, an instruction and an exclamation.

### Concept: What exactly are you asking for?
In *Did Rowan leave?*, *did* marks past tense, so *leave* stays plain. In *Where did Rowan leave the keys?*, the question word asks for a location and the clause keeps the same inversion. *Who left the keys here?* asks for the subject. Its starting *who* takes that slot, and the ordinary active question needs no *did*. If the question goes inside *Do you know where Rowan left the keys?*, the inversion belongs to the outer *Do you know …?* Inside, *Rowan left* has ordinary subject–verb order.

A question can begin with an entire phrase: *Which of the two cupboards did you check?* and *How many spare keys did you find?* Move the whole phrase that asks for the information. With two pieces of information, *Who left what where?* shows how some question words can stay in place. In *When and where did you leave it?*, the two question words form one coordinated phrase at the front. Fixed questions deserve their own reading too. The ordinary fixed form is *Which of you …?*, while *How come Rowan left early?* has subject–verb order after *how come*.

### Concept: When the wording itself invites an answer
“You found the keys?” can be a question in conversation even though its word order is declarative. Compare neutral *Did you find any keys?* with the declarative confirmation *You found some keys?* An ordinary positive declarative confirmation uses *some* here. The inverted question licenses *any* in the sense “any at all”.

If the director wants confirmation, they might say, “The spare keys are in the drawer, aren’t they?” The short tag uses *are* to match the main clause and *they* for the keys. In *Rowan left, didn’t she?*, the past tense is carried by *did* in the tag. In a familiar reversed-polarity tag, a positive clause goes with a negative tag and a negative clause with a positive tag. Other tag patterns can have different effects in conversation.

### Concept: The same scene can call for an instruction or an exclamation
*Everybody check your pockets* is an imperative with an overt subject. The verb remains plain *check*. The negative is *Don’t be late*, even with *be*. A report can turn that directive into *The director told us not to be late*. In that embedded infinitival, *not* goes before *to*. An inclusive suggestion takes the special form *Let’s check the cupboard*. The suggestion already includes the speaker and the person addressed. Start it with *Let’s* and follow with the plain verb *check*.

Once the keys turn up, *What a relief!* combines exclamative *what* with *a* before the singular count head. A full exclamative can do the same: *What a mess we’ve made!* It presents the extent of the mess, whereas *What mess have we made?* asks for information.

### Contrast: One scene, two clause structures
- *Where did Rowan leave the keys?* The question stands on its own and uses inversion.
- *I wonder where Rowan left the keys.* The question is embedded and has ordinary subject–verb order.

### Application
- example: The director wrote, “I wonder where did Rowan leave the keys. Everybody checks your pockets. The case is empty, didn’t it?”
- **Make the question embedded and the command direct** — Revise the first two sentences.
- **Match the tag to its clause** — Use the auxiliary and pronoun appropriate to the case.

### Reveal: Check your analysis
*I wonder where Rowan left the keys. Everybody check your pockets. The case is empty, isn’t it?* The first utterance is a statement with an embedded question. The second has an imperative plain form. In the third, *isn’t it?* picks up *is* and *the case*.

### Recap
Before choosing word order or a verb form, decide which clause you are editing. A direct open question, an embedded question, a tag and an imperative each put the relevant verb in a different place.

### Self-check
- Why does “Everybody bring a pencil” use bring even with everybody as subject?
- It is a directive in the imperative form. The imperative takes a plain verb even when its subject is overt.

## Teaching blocks
### Teaching block 1
Use quoted dialogue to distinguish what a speaker is doing from the form they choose. A declarative “You’re leaving?” can request confirmation even with unchanged word order.

### Teaching block 2
In long examples, draw the boundary of the embedded question before deciding where inversion belongs. The edge of the written sentence is too broad a guide.

## Worked example
- sentence: Do you know which of the drawers Rowan checked?
- origin: Original SynTutor example.
- step: Identify “Do you know …?” as the main closed interrogative.
- step: Keep “which of the drawers” together as one interrogative phrase inside it.
- step: Read “Rowan checked” in ordinary order within the subordinate question.

## Stage checks

#### predict
- prompt: What is the whole fronted question phrase in “How many spare keys did you find?”
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH10-P0874, CGEL-2002-CH10-P0910
- hint: Read the full phrase that could be answered with “three spare keys”.
- options:
  - id: a
    text: how many
    feedback: “How many” gives the quantity expression, but the fronted group includes the things counted.
  - id: b
    text: how
    feedback: How by itself does not express the question that “three spare keys” would answer.
  - id: c
    text: how many spare keys
    feedback: The full phrase, including spare keys, asks for the quantity and functions as the object of find.

#### guided
- prompt: In “Do you know where the bus stops?”, where is the ordinary question inversion?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH10-P0874
- hint: Find the question that is being asked directly.
- options:
  - id: a
    text: In do you know
    feedback: The main clause inverts do and you. The embedded question retains subject–verb order.
  - id: b
    text: In both clauses
    feedback: Only the first clause is a direct question. Look at you and know in the larger clause.
  - id: c
    text: In where the bus stops
    feedback: Where the bus stops preserves subject–verb order.

#### transfer
- prompt: Which question asks neutrally whether there were keys, using polarity-sensitive any?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH10-P0885
- hint: Compare a neutral question with a request to confirm an assumption.
- options:
  - id: a
    text: Did you find any keys?
    feedback: The closed interrogative licenses this use of any. The positive declarative with some normally asks for confirmation.
  - id: b
    text: You found any keys?
    feedback: This is a declarative confirmation pattern, which lacks the ordinary licensing for this use of any.
  - id: c
    text: You found some keys?
    feedback: Some is ordinary in this declarative confirmation. The task asks for the neutral question with any.

#### exit
- prompt: How does “Don’t open it” become an infinitival report after “Jo told us”?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH10-P0943, CGEL-2002-CH10-P0944
- hint: Check where not goes in a reported infinitival.
- options:
  - id: a
    text: Jo told us not open it.
    feedback: Not belongs before the entire to-infinitival. Keep the marker to.
  - id: b
    text: Jo told us to don’t open it.
    feedback: Supportive do belongs in the direct imperative. The report uses an infinitival with not.
  - id: c
    text: Jo told us not to open it.
    feedback: The infinitival puts not before to. Do-support belongs to the direct negative imperative.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: Which is an ordinary direct question about whether Nora took the keys?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH10-P0856, CGEL-2002-CH10-P0857
- options:
  - id: a
    text: Did Nora took the keys?
    feedback: Did carries the past tense. Take follows in the plain form.
  - id: b
    text: Nora did took the keys?
    feedback: Did carries the past tense. Take follows in the plain form.
  - id: c
    text: Did Nora take the keys?
    feedback: Did carries the past tense. Take follows in the plain form.

#### opening-2
- prompt: Which tag fits “The cases are empty, ___?”
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH10-P0892, CGEL-2002-CH10-P0893
- options:
  - id: a
    text: didn’t they
    feedback: Are and the plural subject the cases give aren’t they in the ordinary reversed-polarity tag.
  - id: b
    text: aren’t they
    feedback: Are and the plural subject the cases give aren’t they in the ordinary reversed-polarity tag.
  - id: c
    text: isn’t it
    feedback: Are and the plural subject the cases give aren’t they in the ordinary reversed-polarity tag.

#### opening-3
- prompt: Which wording gives a direct instruction to everyone in the group?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH10-P0934
- options:
  - id: a
    text: Everybody bring a pencil.
    feedback: The imperative uses the plain verb even with an overt subject.
  - id: b
    text: Everybody brings a pencil.
    feedback: The imperative uses the plain verb even with an overt subject.
  - id: c
    text: Everybody brought a pencil.
    feedback: The imperative uses the plain verb even with an overt subject.

#### opening-4
- prompt: Which question asks for the subject of “Someone moved the chair”?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH10-P0874
- options:
  - id: a
    text: Where did someone move the chair?
    feedback: Who replaces someone in the subject slot. In the others, the fronted phrase asks about a different part.
  - id: b
    text: What did Jo move?
    feedback: Who replaces someone in the subject slot. In the others, the fronted phrase asks about a different part.
  - id: c
    text: Who moved the chair?
    feedback: Who replaces someone in the subject slot. In the others, the fronted phrase asks about a different part.

#### opening-5
- prompt: Which order fits after the fixed question expression how come?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH10-P0909
- options:
  - id: a
    text: How come did Jo leave early?
    feedback: The clause after how come retains ordinary subject–verb order.
  - id: b
    text: How come left Jo early?
    feedback: The clause after how come retains ordinary subject–verb order.
  - id: c
    text: How come Jo left early?
    feedback: The clause after how come retains ordinary subject–verb order.

### Closing questions

#### closing-1
- prompt: Choose the ordinary embedded question after “I wonder”.
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH10-P0874
- options:
  - id: a
    text: where left Rowan the key
    feedback: The embedded question keeps subject–verb order and has no supportive did here.
  - id: b
    text: where Rowan left the key
    feedback: The embedded question keeps subject–verb order and has no supportive did here.
  - id: c
    text: where did Rowan leave the key
    feedback: The embedded question keeps subject–verb order and has no supportive did here.

#### closing-2
- prompt: Which exclamation contains an ordinary singular count phrase after what?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH10-P0919, CGEL-2002-CH10-P0920
- options:
  - id: a
    text: What mess we made!
    feedback: Exclamative what goes before a in this singular count phrase.
  - id: b
    text: What a mess we made!
    feedback: Exclamative what goes before a in this singular count phrase.
  - id: c
    text: What an mess we made!
    feedback: Exclamative what goes before a in this singular count phrase.

#### closing-3
- prompt: Which tag completes “Jo called, ___?”
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH10-P0892, CGEL-2002-CH10-P0893
- options:
  - id: a
    text: isn’t it
    feedback: The lexical past called corresponds to did in the tag, and she refers to Jo in this context.
  - id: b
    text: hasn’t she
    feedback: The lexical past called corresponds to did in the tag, and she refers to Jo in this context.
  - id: c
    text: didn’t she
    feedback: The lexical past called corresponds to did in the tag, and she refers to Jo in this context.

#### closing-4
- prompt: Which imperative is an ordinary negative warning?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH10-P0935, CGEL-2002-CH10-P0943, CGEL-2002-CH10-P0944
- options:
  - id: a
    text: Not to be late.
    feedback: Negative imperatives use plain do. Not to be late fits inside a reported directive.
  - id: b
    text: Don’t be late.
    feedback: Negative imperatives use plain do. Not to be late fits inside a reported directive.
  - id: c
    text: Doesn’t be late.
    feedback: Negative imperatives use plain do. Not to be late fits inside a reported directive.

#### closing-5
- prompt: Which is a standard inclusive suggestion using let’s?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH10-P0934, CGEL-2002-CH10-P0935
- options:
  - id: a
    text: Let’s checks the cupboard.
    feedback: The inclusive let’s construction uses the plain verb and has no overt matrix subject we.
  - id: b
    text: Let’s check the cupboard.
    feedback: The inclusive let’s construction uses the plain verb and has no overt matrix subject we.
  - id: c
    text: We let’s check the cupboard.
    feedback: The inclusive let’s construction uses the plain verb and has no overt matrix subject we.

---

# Lesson: cgel-ch13 — Comparatives

- lesson_id: cgel-ch13
- title: Comparatives
- track: grammar
- chapter: 13
- content_version: 2.1.0
- difficulty: advanced
- estimated_minutes: 13
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: CLS-1119, CLS-1129, CLS-1159, CLS-1166, CLS-1188, CLS-1197, CLS-1218, CLS-1222, CLS-1239, CLS-1244, CLS-1259, CLS-1274, CLS-1276
- source_ids: CGEL-2002-CH13-P1108, CGEL-2002-CH13-P1113, CGEL-2002-CH13-P1127, CGEL-2002-CH13-P1129, CGEL-2002-CH13-P1130, CGEL-2002-CH13-P1138, CGEL-2002-CH13-P1141, CGEL-2002-CH13-P1145, CGEL-2002-CH13-P1148, CGEL-2002-CH13-P1154, CGEL-2002-CH13-P1156, CGEL-2002-CH13-P1162, CGEL-2002-CH13-P1168, CGEL-2002-CH13-P1169
- concept_ids: cgel-ch13-concept
- tree_ids:

## Outcomes
- o1: Recover the missing counterpart in a comparative clause and decide when a subject is needed.
- o2: Select the expression and complement that convey the intended comparison.
- o3: Distinguish a ranking in a noun phrase from a free superlative.

## Key terms
- **comparative clause** — The clause in a comparison such as than it was or as it is wide, with part of its interpretation supplied by the larger construction.
- **comparison set** — The group of things or occasions a ranking is made over.
- **superlative** — A form such as deepest or most efficiently, used to locate the extreme of a scale within a set.

## Rules
- CLS-1119
- CLS-1129
- CLS-1159
- CLS-1166
- CLS-1188
- CLS-1197
- CLS-1218
- CLS-1222
- CLS-1239
- CLS-1244
- CLS-1259
- CLS-1274
- CLS-1276

## Sources
- CGEL-2002-CH13-P1108 (p.1108)
- CGEL-2002-CH13-P1113 (p.1113)
- CGEL-2002-CH13-P1127 (p.1127)
- CGEL-2002-CH13-P1129 (p.1129)
- CGEL-2002-CH13-P1130 (p.1130)
- CGEL-2002-CH13-P1138 (p.1138)
- CGEL-2002-CH13-P1141 (p.1141)
- CGEL-2002-CH13-P1145 (p.1145)
- CGEL-2002-CH13-P1148 (p.1148)
- CGEL-2002-CH13-P1154 (p.1154)
- CGEL-2002-CH13-P1156 (p.1156)
- CGEL-2002-CH13-P1162 (p.1162)
- CGEL-2002-CH13-P1168 (p.1168)
- CGEL-2002-CH13-P1169 (p.1169)

## Chapter article

### Introduction
A carpenter measuring a display case writes, “The lower shelf is as deep as it is wide.” There are two dimensions in the sentence, but only one degree comparison. You can feel it if you try to insert *very* before *wide*: the sentence had already left a place for the degree of width. The next notes use *less*, *the same* and *the widest*. They give us a chance to see what changes when the comparison shifts from a measurement to a match, then to a ranking.

### Topics
- What a comparative clause leaves understood
- Matching the comparison word to its complement
- What is being ranked?

### Example
- context: The carpenter measures two dimensions of the shelf.
- sentence: The lower shelf is as deep as it is wide.
- explanation: As much depth as it has width is the intended reading. The second clause leaves the degree of width unexpressed.

### Preview
- Follow the measurements first, then read the rest of the notes for equality, difference and rank.

### Concept: Leave room for the comparison
*The shelf is as deep as it is wide* compares depth with width. A degree word such as *very* in the second clause would occupy the position interpreted through the comparison. With a single property, you may see less repeated: *This shelf is deeper than the old one was*. When you keep *was*, keep *the old one* too. *This shelf is deeper than the old one* also works. There are cases where the subject itself is the missing counterpart: *More brackets arrived than were ordered*. In *more than seemed necessary*, the omission has yet another structure, with an understood embedded subject.

### Concept: Check what is being matched or separated
A shopper needs *fewer brackets* when counting individual pieces and *less hardware* when specifying an amount. *Less* also appears with measurements such as *less than two metres* and in wider usage, so the count contrast is a guide to ordinary choices, especially in edited prose.

The carpenter used *the same screws as last time* and bought *hardware similar to ours*. An ordinary attributive *same* uses a definite noun phrase, commonly with *the*. *Similar*, *superior* and *inferior* commonly use *to* for the standard they compare against. *We used no fasteners other than screws* sets apart *screws*, a noun phrase. To refer to the fasteners in a clause, use a phrase like *those that the store supplied*. A supplementary reporting phrase has its own omission: *The shelf was uneven, as the carpenter had warned*. What the carpenter warned about is recovered from the main clause.

### Concept: Resemblance, role and rank
*Rae spoke like a designer* compares Rae’s manner with a designer’s. *Rae spoke as a designer* gives the capacity in which Rae spoke. In *like her* or *like him*, the personal pronoun complement takes the ordinary accusative form. You can still use *as* for an equality comparison with degrees, as in the opening measurement.

For two shelves, *the deeper of the two* is the conventional comparative wording. Superlatives with two members also occur in ordinary use. In a larger set, *the deepest shelf in the case* has an incorporated superlative inside a definite noun phrase. *This is our deepest shelf* uses a possessive determiner. Look now at *The lake is the lowest it has been all year*. Here *lowest* describes the lake’s level and heads a free superlative. The integrated clause *it has been all year* gives the span of comparison in a construction with *the*. You cannot substitute *which it has been all year* with the same grammar there.

### Contrast: Two jobs for a ranking expression
- *We measured the widest shelf.* Widest modifies a noun and ranks the shelves.
- *The gap is the widest it has ever been.* Widest describes the gap and ranks its width across occasions.

### Application
- example: The draft reads, “The case is as tall as it is very wide. We need fewer equipment than we did last time.”
- **Recover the first comparison** — Leave the degree of width for the comparison to supply.
- **Decide what the second sentence measures** — Keep equipment and choose the quantity word that fits.

### Reveal: Check your analysis
*The case is as tall as it is wide. We need less equipment than we did last time.* The first comparison supplies both degrees. The second measures an amount, and *we* remains the subject of the retained *did*.

### Recap
In a comparative clause, work out what the first part already supplies. Then check the words that remain, including any subject and the marker introducing the standard. For a ranking, ask whether you are identifying a thing in a set or comparing how it has been on different occasions.

### Self-check
- What does “than were requested” leave understood in “More chairs arrived than were requested”?
- The subject is the counterpart of “more chairs”. The comparison sets the number that arrived against the number requested.

## Teaching blocks
### Teaching block 1
Ask learners to name the two properties or quantities before filling a comparative blank. They can then see why “very” competes for the degree the construction supplies.

### Teaching block 2
For superlatives, identify whether there is a head noun and state the comparison set aloud. That distinguishes “the lowest price” from “the lowest it has been”.

## Worked example
- sentence: The new drawer opens more quietly than the old one did.
- origin: Original SynTutor example.
- step: Name the property being compared, the quietness of the opening.
- step: In the comparative clause, “did” stands for the opening and “the old one” is its subject.
- step: Try the shorter “than the old one” and observe that this time there is no retained verb.

## Stage checks

#### predict
- prompt: Which edit keeps the same subject and the comparative verb in “Mira works harder than did last year”?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH13-P1108, CGEL-2002-CH13-P1113
- hint: Keep did and ask who was working last year.
- options:
  - id: a
    text: Mira works harder than she worked hard last year.
    feedback: This repeats the degree description and drops did. Keep did with a subject.
  - id: b
    text: Mira works harder than she did last year.
    feedback: The instruction calls for keeping did, so insert she. The version without did is also grammatical but uses a shorter construction.
  - id: c
    text: Mira works harder than last year.
    feedback: This is grammatical but removes did, which the question asks you to retain.

#### guided
- prompt: Which pair distinguishes a count of parts from an amount of material?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH13-P1127, CGEL-2002-CH13-P1129
- hint: Decide which noun names individual items and which names an amount.
- options:
  - id: a
    text: less brackets / fewer hardware
    feedback: The ordinary quantity word with mass hardware is less.
  - id: b
    text: fewer brackets / fewer hardware
    feedback: Brackets works with fewer. Hardware is a mass noun in this use.
  - id: c
    text: fewer brackets / less hardware
    feedback: Fewer is the ordinary choice here for individual brackets. Less measures the amount of hardware.

#### transfer
- prompt: Which version compares the present noise level with all earlier ones?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH13-P1168, CGEL-2002-CH13-P1169
- hint: Compare different rooms with different occasions in the same room.
- options:
  - id: a
    text: The quietest room is upstairs.
    feedback: This identifies a room by how it ranks among rooms. Nothing tracks its earlier noise levels.
  - id: b
    text: The room is the quietest it has ever been.
    feedback: The free superlative and integrated clause set the comparison across occasions in the same room.
  - id: c
    text: This is the quietest room here.
    feedback: This ranks rooms against each other. The question asks about occasions in the same room.

#### exit
- prompt: What would very occupy in “as deep as it is very wide”?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH13-P1108
- hint: Try asking “to what degree wide?”
- options:
  - id: a
    text: The degree position that the comparison already supplies
    feedback: The clause needs to leave the degree of width for the construction to interpret.
  - id: b
    text: The subject of is wide
    feedback: It supplies the subject of the second clause. Very goes with wide instead.
  - id: c
    text: The position of the adjective wide itself
    feedback: Wide names the property under comparison. Very would specify its degree independently.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: Which comparison leaves the degree of width available for as to supply?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH13-P1108
- options:
  - id: a
    text: The shelf is as deep as it is wide.
    feedback: The second clause retains wide but leaves its degree unexpressed.
  - id: b
    text: The shelf is as deep as it is quite wide.
    feedback: The second clause retains wide but leaves its degree unexpressed.
  - id: c
    text: The shelf is as deep as it is very wide.
    feedback: The second clause retains wide but leaves its degree unexpressed.

#### opening-2
- prompt: Which wording measures an amount of equipment?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH13-P1127, CGEL-2002-CH13-P1129
- options:
  - id: a
    text: fewer equipment
    feedback: Equipment has its ordinary mass reading. Fewer ordinarily counts separate items.
  - id: b
    text: few equipment
    feedback: Equipment has its ordinary mass reading. Fewer ordinarily counts separate items.
  - id: c
    text: less equipment
    feedback: Equipment has its ordinary mass reading. Fewer ordinarily counts separate items.

#### opening-3
- prompt: What is ranked in “the deepest shelf in the case”?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH13-P1168, CGEL-2002-CH13-P1169
- options:
  - id: a
    text: The possible meanings of shelf
    feedback: The incorporated superlative modifies shelf and ranks it against other shelves.
  - id: b
    text: The shelves in the case
    feedback: The incorporated superlative modifies shelf and ranks it against other shelves.
  - id: c
    text: One shelf across several occasions
    feedback: The incorporated superlative modifies shelf and ranks it against other shelves.

#### opening-4
- prompt: Which wording keeps a subject for the retained did?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH13-P1113
- options:
  - id: a
    text: Lea works faster than she did last year.
    feedback: She supplies the subject of did, which stands for the earlier working.
  - id: b
    text: Lea works faster than did last year.
    feedback: She supplies the subject of did, which stands for the earlier working.
  - id: c
    text: Lea works faster than did she last year.
    feedback: She supplies the subject of did, which stands for the earlier working.

#### opening-5
- prompt: Choose the ordinary phrase naming matching screws.
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH13-P1138, CGEL-2002-CH13-P1141
- options:
  - id: a
    text: same screws as last time
    feedback: This use of same occurs in a definite noun phrase with the.
  - id: b
    text: some same screws as last time
    feedback: This use of same occurs in a definite noun phrase with the.
  - id: c
    text: the same screws as last time
    feedback: This use of same occurs in a definite noun phrase with the.

### Closing questions

#### closing-1
- prompt: Why is the subject absent in “More brackets arrived than were ordered”?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH13-P1113
- options:
  - id: a
    text: Every comparative clause lacks a subject.
    feedback: The missing position represents the number of brackets ordered.
  - id: b
    text: The missing subject is the comparative counterpart of more brackets.
    feedback: The missing position represents the number of brackets ordered.
  - id: c
    text: Were ordered is the main predicate of more brackets arrived.
    feedback: The missing position represents the number of brackets ordered.

#### closing-2
- prompt: Rae really is a guide and spoke in that capacity. Which wording explicitly presents the role?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH13-P1148, CGEL-2002-CH13-P1154, CGEL-2002-CH13-P1156
- options:
  - id: a
    text: Rae spoke like she.
    feedback: As a guide describes the capacity. Like a guide describes resemblance.
  - id: b
    text: Rae spoke as a guide.
    feedback: As a guide describes the capacity. Like a guide describes resemblance.
  - id: c
    text: Rae spoke like a guide.
    feedback: As a guide describes the capacity. Like a guide describes resemblance.

#### closing-3
- prompt: Which sentence has a free superlative with an integrated relative?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH13-P1168, CGEL-2002-CH13-P1169
- options:
  - id: a
    text: The lowest lake is on the left.
    feedback: Lowest describes the lake’s level. The clause compares it with its level on other occasions.
  - id: b
    text: The lake is low, which surprises us.
    feedback: Lowest describes the lake’s level. The clause compares it with its level on other occasions.
  - id: c
    text: The lake is the lowest it has been all year.
    feedback: Lowest describes the lake’s level. The clause compares it with its level on other occasions.

#### closing-4
- prompt: Which pair gives ordinary complements in both phrases?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH13-P1130, CGEL-2002-CH13-P1141
- options:
  - id: a
    text: superior to the original / similar to the original
    feedback: Both adjectives can use to to introduce their standard of comparison.
  - id: b
    text: superior of the original / similar than the original
    feedback: Both adjectives can use to to introduce their standard of comparison.
  - id: c
    text: superior than the original / similar the original
    feedback: Both adjectives can use to to introduce their standard of comparison.

#### closing-5
- prompt: Which continuation supplies a noun phrase after postpositive other than?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH13-P1145
- options:
  - id: a
    text: We used no fasteners other than screws.
    feedback: Screws is a noun phrase. Those that the store sold is another possible noun phrase.
  - id: b
    text: We used no fasteners other than the store sold.
    feedback: Screws is a noun phrase. Those that the store sold is another possible noun phrase.
  - id: c
    text: We used no fasteners other than were delivered.
    feedback: Screws is a noun phrase. Those that the store sold is another possible noun phrase.

---

# Lesson: cgel-ch14 — Non-finite clauses

- lesson_id: cgel-ch14
- title: Non-finite clauses
- track: grammar
- chapter: 14
- content_version: 2.1.0
- difficulty: advanced
- estimated_minutes: 11
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: CLS-285, CLS-286, CLS-320, CLS-333, CLS-357, CLS-407, CLS-408
- source_ids: CGEL-2002-CH14-P1182, CGEL-2002-CH14-P1183, CGEL-2002-CH14-P1203, CGEL-2002-CH14-P1214, CGEL-2002-CH14-P1215, CGEL-2002-CH14-P1216, CGEL-2002-CH14-P1217, CGEL-2002-CH14-P1218, CGEL-2002-CH14-P1219, CGEL-2002-CH14-P1234, CGEL-2002-CH14-P1264, CGEL-2002-CH14-P1265
- concept_ids: cgel-ch14-concept
- tree_ids:

## Outcomes
- o1: Identify the expressed or understood subject of a non-finite clause.
- o2: Choose the form of the infinitival in active, passive and interrogative constructions.
- o3: Apply auxiliary order and recognise a participial modifier without adding a relative marker.

## Key terms
- **non-finite clause** — A clause whose verb is an infinitival or participial form, as in to check the gauge or checking the gauge.
- **bare infinitival** — An infinitival with a plain-form verb and without the marker to.
- **expressed subject** — A subject present as words in the clause, as him is in for him to speak.

## Rules
- CLS-285
- CLS-286
- CLS-320
- CLS-333
- CLS-357
- CLS-407
- CLS-408

## Sources
- CGEL-2002-CH14-P1182 (p.1182)
- CGEL-2002-CH14-P1183 (p.1183)
- CGEL-2002-CH14-P1203 (p.1203)
- CGEL-2002-CH14-P1214 (p.1214)
- CGEL-2002-CH14-P1215 (p.1215)
- CGEL-2002-CH14-P1216 (p.1216)
- CGEL-2002-CH14-P1217 (p.1217)
- CGEL-2002-CH14-P1218 (p.1218)
- CGEL-2002-CH14-P1219 (p.1219)
- CGEL-2002-CH14-P1234 (p.1234)
- CGEL-2002-CH14-P1264 (p.1264)
- CGEL-2002-CH14-P1265 (p.1265)

## Chapter article

### Introduction
On a training day, a supervisor *arranged for him to check the gauge*, *made him check it twice*, and later wrote that *he was made to check it twice*. The same trainee does the checking all three times. Even so, his role in the wording keeps changing. We will follow him through those three sentences, then see what happens when the person doing the action can be left understood.

### Topics
- Finding who does the action
- Choosing bare or to-infinitival forms
- Recognising questions and modifiers built without tense

### Example
- context: The supervisor assigns the next reading to a trainee.
- sentence: We arranged for him to check the gauge.
- explanation: The infinitival starts with for, followed by its subject him and the to-infinitival predicate.

### Preview
- Track the trainee across an arrangement, an instruction and a report about the same work.

### Concept: A subject can be expressed inside the infinitival
*We arranged for him to check the gauge* gives the checking clause a subject of its own. Read its parts in order: *for*, *him*, *to check the gauge*. In this use English takes the accusative form, even though *him* is subject of the infinitival. The same arrangement is visible in *It’s essential for you to check the gauge*, where the case contrast is invisible because both forms of *you* look alike.

Other verbs give a following noun phrase a job in the higher clause too. In *Nina believed herself to be ready*, *herself* is the object of *believed* in the construction and is understood as the one who is ready. With the finite alternative, *Nina believed she was ready*, the embedded finite clause supplies its own subject.

### Concept: Switching to the passive can change the infinitival
*The supervisor made him check the gauge* uses a bare infinitival. In *He was made to check the gauge*, *to* appears in the passive construction. Changing only the subject and the form of *make* would leave the repair unfinished. A longer chain then follows the usual order from the verb lesson. In *He seems to have been checking the gauge*, perfect *have* takes *been*, and progressive *been* takes *checking*.

### Concept: When the subject is left to the context
*The trainee asked what to check* leaves the checker understood. An interrogative infinitival of this kind has no expressed subject, so if the trainee wants to ask what someone else should do, a finite question such as *The trainee asked what Mara should check* makes that explicit. Compare *They asked who to call*, where *who* is understood as the object of *call*, with *They asked who should call*, where it is subject of the finite clause.

In *the trainee checking the gauge*, readers understand that the trainee is checking it. The participial clause modifies the noun. The finite version is *the trainee who is checking the gauge*. Once you choose the participial modifier, it can stand directly after the noun.

### Contrast: Two forms with causative make
- *The supervisor made him check the gauge.* The active frame takes a bare infinitival.
- *He was made to check the gauge.* The passive frame takes a to-infinitival.

### Application
- example: The report says, “We arranged for she to test the spare. Later she was made test it again. We asked what for her to record.”
- **Fix the first two infinitivals** — Use the case licensed by for and the form licensed by passive make.
- **Preserve the person who records** — Use a finite embedded question if that subject must be stated.

### Reveal: Check your analysis
*We arranged for her to test the spare. Later she was made to test it again. We asked what she should record.* The report now expresses the test and recording assignments in the constructions that allow them.

### Recap
Find the non-finite clause’s front edge and ask where its subject comes from. Then look to the construction around it for the required verb form. This is how *for him to check*, *made him check* and *was made to check* can refer to the same activity.

### Self-check
- Why is “who” possible in “They asked who to call”?
- Who is understood as the person to be called. The subject of call remains unexpressed.

## Teaching blocks
### Teaching block 1
Ask learners to name the person doing the lower action separately from the grammatical position of that person’s expression. The answers need not use the same label.

### Teaching block 2
When comparing an active and passive with make, keep the lower activity fixed. The appearance of to is easier to see when the rest stays familiar.

## Worked example
- sentence: The engineer asked which valve to open.
- origin: Original SynTutor example.
- step: Keep “which valve” together as the interrogative phrase.
- step: Interpret it as the object of “open”. The subject is understood from context.
- step: To make the intended actor explicit, choose a finite question such as “which valve the trainee should open”.

## Stage checks

#### predict
- prompt: After “We waited for ___ to answer”, which pronoun names the one person expected to answer?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH14-P1182, CGEL-2002-CH14-P1183
- hint: Find the subject inside the infinitival, then test its case.
- options:
  - id: a
    text: he
    feedback: He is nominative. In this infinitival with for, the subject takes the accusative form.
  - id: b
    text: him
    feedback: The subject of the for-infinitival is accusative him.
  - id: c
    text: his
    feedback: His is genitive. The for-infinitival in this exercise requires him.

#### guided
- prompt: Make the lower event accurate in “The trainees were made ___ again.”
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH14-P1234
- hint: Begin with the active “They made the trainees start”, and change the higher verb to passive.
- options:
  - id: a
    text: started
    feedback: The lower verb belongs in an infinitival. The past marking is already carried by were.
  - id: b
    text: start
    feedback: Start would fit the active causative. The passive requires a different form.
  - id: c
    text: to start
    feedback: The passive construction changes the bare infinitival of the active into a to-infinitival.

#### transfer
- prompt: In “We asked which door to open”, what is left understood?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH14-P1264
- hint: Which door already identifies what is opened.
- options:
  - id: a
    text: Which object open takes
    feedback: Which door supplies the object. The action is to open that door.
  - id: b
    text: Whether the words form a question
    feedback: Which door makes the subordinate clause interrogative. What the clause leaves out is the person doing the opening.
  - id: c
    text: Who will open it
    feedback: Which door supplies the object. The actor is left to context.

#### exit
- prompt: How does “the guest waiting outside” differ from “the guest who is waiting outside”?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH14-P1264, CGEL-2002-CH14-P1265
- hint: Compare the versions for a finite auxiliary and a relative marker.
- options:
  - id: a
    text: The first needs who before waiting.
    feedback: Holding or waiting can directly modify a noun. Use who when you choose a finite relative such as who is waiting.
  - id: b
    text: The first has a participial modifier. The second has a finite relative.
    feedback: Waiting outside has no tense-bearing auxiliary. Who is waiting outside is finite.
  - id: c
    text: Both have expressed subjects inside their modifiers.
    feedback: The subject is understood in the participial modifier. The relative marker represents it in the finite version.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: Who is understood to speak in “They arranged for him to speak first”?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH14-P1182, CGEL-2002-CH14-P1183
- options:
  - id: a
    text: they
    feedback: Him is the expressed subject of the infinitival after for.
  - id: b
    text: him
    feedback: Him is the expressed subject of the infinitival after for.
  - id: c
    text: an unexpressed third person
    feedback: Him is the expressed subject of the infinitival after for.

#### opening-2
- prompt: Which is the ordinary passive counterpart of “They made us wait”?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH14-P1234
- options:
  - id: a
    text: We were made to wait.
    feedback: Passive causative make selects a to-infinitival.
  - id: b
    text: We were made waited.
    feedback: Passive causative make selects a to-infinitival.
  - id: c
    text: We were made wait.
    feedback: Passive causative make selects a to-infinitival.

#### opening-3
- prompt: Choose a non-finite modifier for “the technician ___ the meter”.
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH14-P1264, CGEL-2002-CH14-P1265
- options:
  - id: a
    text: who checking
    feedback: Checking heads a participial modifier. That is checking would be a finite relative.
  - id: b
    text: that is checking
    feedback: Checking heads a participial modifier. That is checking would be a finite relative.
  - id: c
    text: checking
    feedback: Checking heads a participial modifier. That is checking would be a finite relative.

#### opening-4
- prompt: Which order fits the infinitival after essential?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH14-P1182, CGEL-2002-CH14-P1183
- options:
  - id: a
    text: It’s essential for she to check the reading.
    feedback: The order is for, accusative subject her, then the to-infinitival predicate.
  - id: b
    text: It’s essential for her to check the reading.
    feedback: The order is for, accusative subject her, then the to-infinitival predicate.
  - id: c
    text: It’s essential for the reading her to check.
    feedback: The order is for, accusative subject her, then the to-infinitival predicate.

#### opening-5
- prompt: What role does who have in “They asked who to call”?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH14-P1264
- options:
  - id: a
    text: Expressed subject of call
    feedback: The caller is understood. Who asks which person should receive the call.
  - id: b
    text: Understood object of call
    feedback: The caller is understood. Who asks which person should receive the call.
  - id: c
    text: Subject of asked
    feedback: The caller is understood. Who asks which person should receive the call.

### Closing questions

#### closing-1
- prompt: Choose the ordinary active infinitival construction with believe to describe Nina’s view of herself.
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH14-P1203
- options:
  - id: a
    text: Nina believed herself to be ready.
    feedback: Believe takes the overt object herself in this frame, and she is used in the finite alternative she was ready.
  - id: b
    text: Nina believed she to be ready.
    feedback: Believe takes the overt object herself in this frame, and she is used in the finite alternative she was ready.
  - id: c
    text: Nina believed to be ready.
    feedback: Believe takes the overt object herself in this frame, and she is used in the finite alternative she was ready.

#### closing-2
- prompt: In “The supervisor made Jen check again”, which words form the lower predicate?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH14-P1234
- options:
  - id: a
    text: check again
    feedback: The active causative takes a bare infinitival. The to form appears in the passive counterpart.
  - id: b
    text: to check again
    feedback: The active causative takes a bare infinitival. The to form appears in the passive counterpart.
  - id: c
    text: made Jen
    feedback: The active causative takes a bare infinitival. The to form appears in the passive counterpart.

#### closing-3
- prompt: Which order puts perfect have before progressive be?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH14-P1214, CGEL-2002-CH14-P1219
- options:
  - id: a
    text: to has been checking
    feedback: In the infinitival, plain have selects been, and progressive been selects checking.
  - id: b
    text: to have been checking
    feedback: In the infinitival, plain have selects been, and progressive been selects checking.
  - id: c
    text: to be having checked
    feedback: In the infinitival, plain have selects been, and progressive been selects checking.

#### closing-4
- prompt: Choose the finite wording if Mara must be named as the person who checks something.
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH14-P1264
- options:
  - id: a
    text: They asked what Mara should check.
    feedback: The finite question can express Mara as subject. The third option is grammatical but leaves the subject understood.
  - id: b
    text: They asked what for Mara to check.
    feedback: The finite question can express Mara as subject. The third option is grammatical but leaves the subject understood.
  - id: c
    text: They asked what to check.
    feedback: The finite question can express Mara as subject. The third option is grammatical but leaves the subject understood.

#### closing-5
- prompt: Which version directly modifies the noun with a non-finite clause?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH14-P1264, CGEL-2002-CH14-P1265
- options:
  - id: a
    text: the worker holding the spare meter
    feedback: Holding the spare meter is participial and can modify worker without a relative marker.
  - id: b
    text: the worker who holding the spare meter
    feedback: Holding the spare meter is participial and can modify worker without a relative marker.
  - id: c
    text: the worker who is holding the spare meter
    feedback: Holding the spare meter is participial and can modify worker without a relative marker.

---

# Lesson: cgel-ch15 — Coordination and supplementary clauses

- lesson_id: cgel-ch15
- title: Coordination and supplementary clauses
- track: grammar
- chapter: 15
- content_version: 2.1.0
- difficulty: advanced
- estimated_minutes: 10
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: CLS-1034, CLS-1035, CLS-1036, CLS-1095
- source_ids: CGEL-2002-CH15-P1323, CGEL-2002-CH15-P1324, CGEL-2002-CH15-P1334, CGEL-2002-CH15-P1335, CGEL-2002-CH15-P1353
- concept_ids: cgel-ch15-concept
- tree_ids:

## Outcomes
- o1: Test whether two proposed coordinates can serve the same function in context.
- o2: Recognise restrictions on coordinating clause forms and nouns under one determiner.
- o3: Trace a supplementary relative clause to its anchor.

## Key terms
- **coordinate** — One member of a pair or series joined at the same structural level.
- **supplement** — An expression set apart from the main structure that adds information about an anchor.
- **anchor** — The expression, person, thing or situation a supplement comments on.

## Rules
- CLS-1034
- CLS-1035
- CLS-1036
- CLS-1095

## Sources
- CGEL-2002-CH15-P1323 (p.1323)
- CGEL-2002-CH15-P1324 (p.1324)
- CGEL-2002-CH15-P1334 (p.1334)
- CGEL-2002-CH15-P1335 (p.1335)
- CGEL-2002-CH15-P1353 (p.1353)

## Chapter article

### Introduction
An exhibition coordinator writes, “The crates arrived yesterday and without warning.” One part tells us when and the other tells us about the circumstances. Both fit the report independently: *The crates arrived yesterday* and *The crates arrived without warning*. Then the coordinator adds, “The largest crate, which came from Manila, was opened first.” That middle clause adds information too, yet *which came from Manila* needs something in the surrounding sentence to latch onto. These are two different ways of putting more than one idea in a sentence.

### Topics
- Finding the job shared by coordinates
- When the forms must match
- Attaching a supplementary relative

### Example
- context: A coordinator notes the circumstances of delivery.
- sentence: The crates arrived yesterday and without warning.
- explanation: Both coordinates are adjuncts to arrived. One is an adverb phrase, and the other is a preposition phrase.

### Preview
- Test the delivery report one coordinate at a time, then try the same test on a supplementary relative.

### Concept: Test each coordinate in the same slot
Take the first report apart. *Yesterday* and *without warning* are different phrase types, but each works as an adjunct with *arrived*. Now try *The crates arrived yesterday and the loading bay*. The second expression names a location, but it cannot fill the slot on its own in that form. *At the loading bay* restores the connection. In the lesson on contractions, *Maya and you* had a shared job as a subject. This time the coordination shares the adjunct job.

### Concept: Some constructions ask more than a shared job
*To label each crate would help* and *photographing each crate would help* each provide a subject. The infinitival and the gerund-participial do not make an ordinary coordinate pair in that subject position. Choose *To label the crates or to photograph them would help*, or *Labelling the crates or photographing them would help*.

Inside a noun phrase, count the structure as well as the objects. In *this cup and saucer*, a single *this* can introduce the closely associated pair. Two separate singular phrases, *this cup and that saucer*, are also possible. The plural determiner in *these cup and saucer* cannot treat the coordination of singular nouns as a plural head in this construction. Use full phrases or a plural head such as *these cups and saucers* if that is what you mean.

### Concept: A supplementary relative needs somewhere to attach
In *The largest crate, which came from Manila, was opened first*, *the largest crate* already identifies the crate. The commas set off a supplementary relative that adds its origin. Compare *The crate which came from Manila was opened first*. Here the relative can be part of the identification. An anchor can also be a whole situation, as in *The crate arrived undamaged, which was a relief*. A line such as *Which came from Manila, was opened first* has lost the noun phrase that serves as the anchor and the subject of *was opened*.

### Contrast: Two ways to add information
- *The crate was large and unusually heavy.* Both parts serve as descriptions after was.
- *The crate, which was unusually heavy, blocked the aisle.* The relative adds a comment anchored to the crate.

### Application
- example: A report says, “These cup and saucer arrived yesterday and the lobby. Which had been wrapped separately, came first.”
- **Build the coordination** — Assume the report describes one cup and one saucer and a delivery to the lobby.
- **Anchor the relative** — Build a full sentence that identifies the cup as the first to arrive.

### Reveal: Check your analysis
*This cup and that saucer arrived at the lobby yesterday* uses two full subject noun phrases and two adjuncts. The location and time can also be coordinated, as in *They arrived yesterday and at the lobby*, though the uncoordinated order is smoother here. *The cup, which had been wrapped separately, arrived first* sets the wrapping detail inside a complete sentence anchored to *the cup*.

### Recap
With coordination, ask what each member does in the shared context and whether the slot places any extra restrictions on form. With supplementation, name the thing or situation the comment is about and check that it is available as an anchor.

### Self-check
- In “The delivery was late, which upset the curator”, what upset the curator?
- The fact that the delivery was late. The whole preceding clause supplies the anchor.

## Teaching blocks
### Teaching block 1
Give learners two expressions that each work alone as subject, then invite them to coordinate them. This surfaces why functional equivalence is only the first check.

### Teaching block 2
When removing a supplementary relative for comparison, keep its anchor in the sentence. Read the remaining clause aloud and then restore the comment.

## Worked example
- sentence: The crate was sturdy and in good condition, which reassured the curator.
- origin: Original SynTutor example.
- step: Check that “sturdy” and “in good condition” each work after “was”.
- step: Read the relative as a comment on the preceding state of affairs.
- step: Keep the comma to distinguish the supplement from the coordinated descriptions.

## Stage checks

#### predict
- prompt: What small grammatical change repairs “They arrived yesterday and the lobby”?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH15-P1323, CGEL-2002-CH15-P1324
- hint: Give the location a form that can follow arrived by itself.
- options:
  - id: a
    text: They arrived yesterday and in the lobby.
    feedback: In the lobby can fill the location-adjunct slot. The bare noun phrase cannot do so here.
  - id: b
    text: The lobby and they arrived yesterday.
    feedback: Making the lobby a subject changes the meaning. Keep it in the location phrase.
  - id: c
    text: They arrived yesterday but the lobby.
    feedback: But no longer joins equivalent adjuncts if “the lobby” stays bare.

#### guided
- prompt: Which revision keeps both proposed activities in infinitival form?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH15-P1324
- hint: Keep the subject coordination but check both verb forms.
- options:
  - id: a
    text: To label the crates or photographing them would help.
    feedback: This mixes an infinitival and an -ing clause in one coordination.
  - id: b
    text: To label the crates or to photograph them would help.
    feedback: Both coordinates in the first option have to-infinitival form. The last option works grammatically but switches both forms.
  - id: c
    text: Labelling the crates or photographing them would help.
    feedback: Both clauses here are gerund-participial. The task asks for the pair with to-infinitivals.

#### transfer
- prompt: Repair “Which had been wrapped, came first” while keeping the wrapping detail supplementary.
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH15-P1353
- hint: The sentence needs something that was first. Give it a subject.
- options:
  - id: a
    text: The cup, which had been wrapped, came first.
    feedback: The cup supplies the anchor and the main subject. Paired commas mark the additional comment.
  - id: b
    text: The cup which had been wrapped came first.
    feedback: Without commas, the relative can identify which cup. The exercise asks for an added comment.
  - id: c
    text: Which had been wrapped came first.
    feedback: That would need a different construction for which. Give came first its own subject.

#### exit
- prompt: In “The crate was large and heavy, which worried us”, what do and and which do?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH15-P1323, CGEL-2002-CH15-P1324, CGEL-2002-CH15-P1353
- hint: Try “The crate was large” and “The crate was heavy” separately, then ask what worried us.
- options:
  - id: a
    text: And joins two clauses. Which is a third coordinate.
    feedback: Large and heavy are two predicative descriptions after was. Neither has a separate clause here.
  - id: b
    text: And introduces an object. Which modifies only the word heavy.
    feedback: Which points to the whole description of the crate. Its size and weight together caused the worry.
  - id: c
    text: And joins two predicative descriptions. Which adds a comment anchored to the state of affairs.
    feedback: Large and heavy share a predicative function. The source of the worry is the crate’s being large and heavy.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: In “The crates arrived yesterday and without warning”, what job do the coordinates share?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH15-P1323, CGEL-2002-CH15-P1324
- options:
  - id: a
    text: Both are subjects of arrived.
    feedback: Each expression can supply a circumstance of the arrival.
  - id: b
    text: Both are objects of arrived.
    feedback: Each expression can supply a circumstance of the arrival.
  - id: c
    text: They are adjuncts to arrived.
    feedback: Each expression can supply a circumstance of the arrival.

#### opening-2
- prompt: Which pair makes an ordinary coordination in subject position?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH15-P1324
- options:
  - id: a
    text: Labelling or to photograph the crates would help.
    feedback: The two clauses in this subject coordination have the same form.
  - id: b
    text: Labelling or photographing the crates would help.
    feedback: The two clauses in this subject coordination have the same form.
  - id: c
    text: To label or photographing the crates would help.
    feedback: The two clauses in this subject coordination have the same form.

#### opening-3
- prompt: What is the anchor of the supplement in “The large crate, which came from Manila, was heavy”?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH15-P1353
- options:
  - id: a
    text: the large crate
    feedback: The relative adds an origin detail about the crate.
  - id: b
    text: Manila
    feedback: The relative adds an origin detail about the crate.
  - id: c
    text: was heavy
    feedback: The relative adds an origin detail about the crate.

#### opening-4
- prompt: Which second coordinate fits “She spoke softly and ___” as another manner adjunct?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH15-P1323, CGEL-2002-CH15-P1324
- options:
  - id: a
    text: the corridor
    feedback: Without hesitation can modify spoke independently, just as softly can.
  - id: b
    text: her voice
    feedback: Without hesitation can modify spoke independently, just as softly can.
  - id: c
    text: without hesitation
    feedback: Without hesitation can modify spoke independently, just as softly can.

#### opening-5
- prompt: Which version names one cup and one saucer with two separate noun phrases?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH15-P1334, CGEL-2002-CH15-P1335
- options:
  - id: a
    text: these cups and saucers
    feedback: Repeating the singular determiner creates two full phrases. The last option describes plurals.
  - id: b
    text: this cup and that saucer
    feedback: Repeating the singular determiner creates two full phrases. The last option describes plurals.
  - id: c
    text: these cup and saucer
    feedback: Repeating the singular determiner creates two full phrases. The last option describes plurals.

### Closing questions

#### closing-1
- prompt: Which pair can both serve after “The parcel was ___”?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH15-P1323, CGEL-2002-CH15-P1324
- options:
  - id: a
    text: sturdy and in good condition
    feedback: An adjective phrase and a preposition phrase can each describe the parcel after was in the first option.
  - id: b
    text: sturdy and the lobby
    feedback: An adjective phrase and a preposition phrase can each describe the parcel after was in the first option.
  - id: c
    text: at the depot and yesterday morning arrived
    feedback: An adjective phrase and a preposition phrase can each describe the parcel after was in the first option.

#### closing-2
- prompt: Which sentence has a supplementary relative about the whole reported situation?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH15-P1353
- options:
  - id: a
    text: The parcel arrived undamaged, which was a relief.
    feedback: The relief comes from the safe arrival, so the preceding clause provides the anchor.
  - id: b
    text: The parcel which arrived undamaged went upstairs.
    feedback: The relief comes from the safe arrival, so the preceding clause provides the anchor.
  - id: c
    text: The parcel, which arrived undamaged, went upstairs.
    feedback: The relief comes from the safe arrival, so the preceding clause provides the anchor.

#### closing-3
- prompt: Why does “these cup and saucer” fail in the shared-determiner construction?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH15-P1334, CGEL-2002-CH15-P1335
- options:
  - id: a
    text: These can select only singular nouns.
    feedback: The number condition applies to the grammatical head. There can be two objects in the real world and still be two singular nouns in the coordination.
  - id: b
    text: The two singular nouns do not make a plural head that these can select.
    feedback: The number condition applies to the grammatical head. There can be two objects in the real world and still be two singular nouns in the coordination.
  - id: c
    text: The problem is a missing relative clause.
    feedback: The number condition applies to the grammatical head. There can be two objects in the real world and still be two singular nouns in the coordination.

#### closing-4
- prompt: Which wording treats “which had been relabelled” as an added comment about an already identified crate?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH15-P1353
- options:
  - id: a
    text: Which had been relabelled, arrived first.
    feedback: The supplement is set off after its anchor. The integrated alternative can help identify which crate.
  - id: b
    text: The crate which had been relabelled arrived first.
    feedback: The supplement is set off after its anchor. The integrated alternative can help identify which crate.
  - id: c
    text: The blue crate, which had been relabelled, arrived first.
    feedback: The supplement is set off after its anchor. The integrated alternative can help identify which crate.

#### closing-5
- prompt: What should you try first when testing “yesterday and at the station” after arrived?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH15-P1323, CGEL-2002-CH15-P1324
- options:
  - id: a
    text: Check that both phrases have the same spelling pattern.
    feedback: The independent readings show that both can serve as adjuncts.
  - id: b
    text: Look for a separate subject in each part.
    feedback: The independent readings show that both can serve as adjuncts.
  - id: c
    text: Read each part after arrived on its own.
    feedback: The independent readings show that both can serve as adjuncts.

---

# Lesson: cgel-ch16 — Information packaging

- lesson_id: cgel-ch16
- title: Information packaging
- track: grammar
- chapter: 16
- content_version: 2.1.0
- difficulty: advanced
- estimated_minutes: 12
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: CLS-1325, CLS-1329, CLS-1379, CLS-1415, CLS-1425, CLS-1451, CLS-1479
- source_ids: CGEL-2002-CH16-P1383, CGEL-2002-CH16-P1384, CGEL-2002-CH16-P1406, CGEL-2002-CH16-P1407, CGEL-2002-CH16-P1419, CGEL-2002-CH16-P1422, CGEL-2002-CH16-P1423, CGEL-2002-CH16-P1432, CGEL-2002-CH16-P1442, CGEL-2002-CH16-P1443
- concept_ids: cgel-ch16-concept
- tree_ids:

## Outcomes
- o1: Choose an available word order for particles, recipients and extraposed subjects.
- o2: Use a cleft to highlight the information a reader is looking for.
- o3: Identify which clause becomes passive and choose the required complement form.

## Key terms
- **extraposition** — A construction with it in the usual subject position and a clause later, as in It would help to close the valve.
- **it-cleft** — A construction such as It was Maya who closed the valve, which singles out a value for a role.
- **pseudo-cleft** — A specifying construction such as What helped was closing the valve, with a fused relative as one part.
- **passive** — A construction that can make the affected participant the subject, as in The valve was closed by Maya.

## Rules
- CLS-1325
- CLS-1329
- CLS-1379
- CLS-1415
- CLS-1425
- CLS-1451
- CLS-1479

## Sources
- CGEL-2002-CH16-P1383 (p.1383)
- CGEL-2002-CH16-P1384 (p.1384)
- CGEL-2002-CH16-P1406 (p.1406)
- CGEL-2002-CH16-P1407 (p.1407)
- CGEL-2002-CH16-P1419 (p.1419)
- CGEL-2002-CH16-P1422 (p.1422)
- CGEL-2002-CH16-P1423 (p.1423)
- CGEL-2002-CH16-P1432 (p.1432)
- CGEL-2002-CH16-P1442 (p.1442)
- CGEL-2002-CH16-P1443 (p.1443)

## Chapter article

### Introduction
“Who closed the valve?” the incident reviewer asks. “It was Maya who closed it.” The second speaker could have said, “Maya closed it.” The cleft makes the answer to *who?* easy to hear. Once the reviewer changes the question to “What helped?”, a different wording fits: “What helped was closing the valve.” This lesson follows those choices in a short incident report, including the places where a useful change of emphasis runs up against a fixed word order.

### Topics
- Local word order in the report
- Moving a long clause and highlighting an answer
- Choosing where the passive belongs

### Example
- context: A reviewer corrects a mistaken account of the incident.
- sentence: It was Maya who closed the valve.
- explanation: Maya is the value singled out by the cleft. The relative supplies the role the reviewer is asking about.

### Preview
- Start with short objects and recipients, then see what happens when the report gives structure to longer material.

### Concept: Choose among the orders the frame gives you
*We sent the crew a reminder* puts the recipient before the direct object. To put the reminder first, use *We sent a reminder to the crew*. Dropping *to* after the direct object leaves an order the ordinary double-object frame does not supply. With particles, *Maya brought back the tools* and *Maya brought the tools back* both work. Replacing *the tools* with an unstressed *them* makes *Maya brought them back* the regular order. A reader may care about what is new or heavy, but those preferences operate inside the choices the grammar permits.

### Concept: Shift a clause or single out a value
*To close the valve would help* places the whole infinitival clause first. When the reviewer asks a question, *Would it help to close the valve?* is the natural wording. *It* occupies the subject slot after the inverted auxiliary and the longer clause follows later. This is the same subject–auxiliary order you saw in the question lesson, with a different kind of subject construction.

An it-cleft answers a focused question: *It was Maya who closed the valve*. After a verb like *believe*, the raised-object construction needs *be*: *I believe it to be Maya who closed the valve*. A related way to specify the answer is *What helped was closing the valve*. Here *what helped* means roughly “the thing that helped”. For a person, ordinary Standard English uses *The one who closed it was Maya*. Bare *who* does not do the same fused-relative job in *Who closed it was Maya*, although *who closed it* is fine as an embedded question in *I know who closed it*.

### Concept: Ask which event is passive
*We saw Maya close the valve* reports a perception. Make *see* passive and you get *Maya was seen to close the valve*, with *to* in the lower clause. The same sort of change happened earlier in the course with *made him check* and *was made to check*.

Now leave *we saw* active and describe an event that happened to Maya: *We saw Maya get splashed* or *We saw Maya splashed by a burst of water*. Here it is the lower event that is passive. This bare-perception frame has *get* or a bare passive, while inserting *be* before *splashed* is excluded in the frame described here. The question “Which event is passive?” keeps the two patterns straight.

### Contrast: Put the focus where it answers the question
- *It was Maya who closed the valve.* This specifies a person in an it-cleft.
- *What helped was closing the valve.* This specifies an action in a pseudo-cleft.

### Application
- example: The notes read, “Would to close the second valve help? Who closed the first one was Maya. Maya was seen close it.”
- **Make the question natural** — Give the longer infinitival clause a position after the predicate.
- **Preserve the focus and the observation** — Use a specifying clause for the person and the appropriate infinitival in the passive.

### Reveal: Check your analysis
*Would it help to close the second valve? The one who closed the first one was Maya. Maya was seen to close it.* Each sentence now preserves the writer’s intended emphasis using an available frame.

### Recap
Ask what the reader needs first, then check the available grammar. A recipient can move into a *to* phrase, an infinitival subject can be expressed later with *it* in its place, and a cleft can put the value of a piece of information in focus.

### Self-check
- Which event is passive in “We saw Maya get splashed”?
- The splashing. “We saw” stays active.

## Teaching blocks
### Teaching block 1
Try a short three-turn report: a neutral statement, a question identifying one missing detail and a cleft supplying the answer. This gives the cleft a reason to be there.

### Teaching block 2
In perception examples, have learners underline the matrix verb and circle the lower event. Convert one at a time so that the complement changes are visible.

## Worked example
- sentence: It would help to close the second valve.
- origin: Original SynTutor example.
- step: Identify the infinitival clause, “to close the second valve”.
- step: Recognise “it” as the extraposition subject and “would” as the finite auxiliary.
- step: Invert “would” and “it” to ask “Would it help to close the second valve?”

## Stage checks

#### predict
- prompt: Turn “It might help to turn the handle” into a direct question.
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH16-P1406, CGEL-2002-CH16-P1407
- hint: Keep the infinitival at the end and find the short word in the subject slot.
- options:
  - id: a
    text: Might it help to turn the handle?
    feedback: Might inverts with the extraposition subject it. The infinitival stays after help.
  - id: b
    text: Might to turn the handle help?
    feedback: The task starts with extraposition, so keep it in the subject slot and leave the infinitival after help.
  - id: c
    text: Did it might help to turn the handle?
    feedback: Might is already an auxiliary. It can move before the subject on its own.

#### guided
- prompt: A reviewer asks “Which person reset the alarm?” Which cleft makes that person the focus?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH16-P1419, CGEL-2002-CH16-P1422, CGEL-2002-CH16-P1423
- hint: Look immediately after “It was” in each it-cleft.
- options:
  - id: a
    text: It was the alarm that Jo reset.
    feedback: This cleft foregrounds the alarm. Choose the cleft that puts the person after it was.
  - id: b
    text: It was Jo who reset the alarm.
    feedback: The first cleft foregrounds Jo. The other two foreground the thing reset.
  - id: c
    text: What Jo reset was the alarm.
    feedback: This focuses the thing Jo reset.

#### transfer
- prompt: Which edit makes the act of seeing passive, keeping the act of closing active?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH16-P1432, CGEL-2002-CH16-P1442, CGEL-2002-CH16-P1443
- hint: Identify the two events and ask which one the observer is the subject of.
- options:
  - id: a
    text: We saw Maya get splashed.
    feedback: Saw remains active. Get splashed makes the lower event passive.
  - id: b
    text: Maya was seen to close the valve.
    feedback: Was seen marks the higher passive. Close remains active in the lower infinitival.
  - id: c
    text: We saw the valve closed.
    feedback: Saw is active and the valve undergoes the closing. The task asks you to passivise see.

#### exit
- prompt: Why does “I know who called” work while the course uses “The one who called was Jo” to specify the caller?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH16-P1422, CGEL-2002-CH16-P1423
- hint: Ask whether “who called” stands for a question or whether who modifies the one.
- options:
  - id: a
    text: The former contains a question. The latter uses an overt head with a relative.
    feedback: An interrogative who clause and a fused relative need not license the same words.
  - id: b
    text: Called requires a to-infinitival in a specifying clause.
    feedback: The difference is between an embedded question and a headed relative. Both examples use the same finite verb called.
  - id: c
    text: Who is a free-standing fused-relative subject in both.
    feedback: Who starts an embedded interrogative after know. In the other sentence, the one supplies the head of the subject noun phrase.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: Choose the ordinary particle order when the direct object is unstressed them.
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH16-P1383, CGEL-2002-CH16-P1384
- options:
  - id: a
    text: Maya brought them back.
    feedback: The unstressed object pronoun comes before the particle.
  - id: b
    text: Maya brought back them.
    feedback: The unstressed object pronoun comes before the particle.
  - id: c
    text: Maya them brought back.
    feedback: The unstressed object pronoun comes before the particle.

#### opening-2
- prompt: Which line specifically answers “Who closed the valve?” with an it-cleft?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH16-P1419
- options:
  - id: a
    text: Maya closed the valve.
    feedback: The cleft places Maya in the identifying slot before the relative.
  - id: b
    text: What helped was closing the valve.
    feedback: The cleft places Maya in the identifying slot before the relative.
  - id: c
    text: It was Maya who closed the valve.
    feedback: The cleft places Maya in the identifying slot before the relative.

#### opening-3
- prompt: Which clause is passive in “We saw Maya get splashed”?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH16-P1442, CGEL-2002-CH16-P1443
- options:
  - id: a
    text: The clause headed by saw
    feedback: We saw is active. Maya undergoes the splashing in the lower clause.
  - id: b
    text: The lower splashing clause
    feedback: We saw is active. Maya undergoes the splashing in the lower clause.
  - id: c
    text: Both clauses
    feedback: We saw is active. Maya undergoes the splashing in the lower clause.

#### opening-4
- prompt: Which question uses extraposition?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH16-P1406, CGEL-2002-CH16-P1407
- options:
  - id: a
    text: Would it help to close the valve?
    feedback: It goes in the subject position and the infinitival comes later.
  - id: b
    text: Would the valve close?
    feedback: It goes in the subject position and the infinitival comes later.
  - id: c
    text: Would to close the valve help?
    feedback: It goes in the subject position and the infinitival comes later.

#### opening-5
- prompt: Which pseudo-cleft names the action that helped?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH16-P1422, CGEL-2002-CH16-P1423
- options:
  - id: a
    text: What helped was closing the valve.
    feedback: What helped sets up a value, and closing the valve specifies it.
  - id: b
    text: It was Maya who closed the valve.
    feedback: What helped sets up a value, and closing the valve specifies it.
  - id: c
    text: Closing the valve helped.
    feedback: What helped sets up a value, and closing the valve specifies it.

### Closing questions

#### closing-1
- prompt: Reword “We sent Jo a reminder” so that the reminder comes before Jo.
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH16-P1383, CGEL-2002-CH16-P1384
- options:
  - id: a
    text: We sent to Jo a reminder.
    feedback: The direct-object-first wording uses a recipient to phrase.
  - id: b
    text: We sent a reminder Jo.
    feedback: The direct-object-first wording uses a recipient to phrase.
  - id: c
    text: We sent a reminder to Jo.
    feedback: The direct-object-first wording uses a recipient to phrase.

#### closing-2
- prompt: Which wording keeps the raised it-cleft after “I believe”?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH16-P1419
- options:
  - id: a
    text: I believe it Maya who closed the valve.
    feedback: The raised-object cleft construction uses be. I believe that it was Maya would use a different frame.
  - id: b
    text: I believe Maya who closed the valve.
    feedback: The raised-object cleft construction uses be. I believe that it was Maya would use a different frame.
  - id: c
    text: I believe it to be Maya who closed the valve.
    feedback: The raised-object cleft construction uses be. I believe that it was Maya would use a different frame.

#### closing-3
- prompt: Make see passive in “They saw Maya close the valve”.
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH16-P1432
- options:
  - id: a
    text: Maya was seen to close the valve.
    feedback: When see is passive in this frame, to appears before close.
  - id: b
    text: They saw Maya get splashed.
    feedback: When see is passive in this frame, to appears before close.
  - id: c
    text: Maya was seen close the valve.
    feedback: When see is passive in this frame, to appears before close.

#### closing-4
- prompt: Which sentence specifies the identity of the person, using a subject noun phrase with an integrated relative?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH16-P1422, CGEL-2002-CH16-P1423
- options:
  - id: a
    text: Who called was Jo.
    feedback: The one provides an overt head for the relative. The last line uses an embedded question instead.
  - id: b
    text: I know who called.
    feedback: The one provides an overt head for the relative. The last line uses an embedded question instead.
  - id: c
    text: The one who called was Jo.
    feedback: The one provides an overt head for the relative. The last line uses an embedded question instead.

#### closing-5
- prompt: Which pair keeps see active but makes the lower event passive?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH16-P1442, CGEL-2002-CH16-P1443
- options:
  - id: a
    text: We saw Maya splash water. / We saw Maya run.
    feedback: Get splashed and the bare splashed by a wave both present Maya as undergoing the event.
  - id: b
    text: Maya was seen to splash water. / We saw Maya splash water.
    feedback: Get splashed and the bare splashed by a wave both present Maya as undergoing the event.
  - id: c
    text: We saw Maya get splashed. / We saw Maya splashed by a wave.
    feedback: Get splashed and the bare splashed by a wave both present Maya as undergoing the event.

---

# Lesson: cgel-ch17 — Pronouns and pro-forms

- lesson_id: cgel-ch17
- title: Pronouns and pro-forms
- track: grammar
- chapter: 17
- content_version: 2.1.0
- difficulty: advanced
- estimated_minutes: 18
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: CLS-1101, CLS-1103, PHR-580, PHR-582, PHR-590, PHR-593, PHR-600, PHR-601, PHR-602, PHR-606, PHR-612, PHR-620, PHR-629, PHR-632, PHR-644, PHR-645, PHR-653, PHR-654, PHR-655, PHR-656, PHR-666, PHR-673, PHR-684, PHR-696, PHR-704, PHR-705, PHR-706, PHR-737, PHR-748, PHR-769
- source_ids: CGEL-2002-CH17-P1457, CGEL-2002-CH17-P1488, CGEL-2002-CH17-P1497, CGEL-2002-CH17-P1499, CGEL-2002-CH17-P1500, CGEL-2002-CH17-P1501, CGEL-2002-CH17-P1502, CGEL-2002-CH17-P1503, CGEL-2002-CH17-P1505, CGEL-2002-CH17-P1508, CGEL-2002-CH17-P1509, CGEL-2002-CH17-P1512, CGEL-2002-CH17-P1515, CGEL-2002-CH17-P1516, CGEL-2002-CH17-P1518, CGEL-2002-CH17-P1520, CGEL-2002-CH17-P1524, CGEL-2002-CH17-P1528, CGEL-2002-CH17-P1530, CGEL-2002-CH17-P1539, CGEL-2002-CH17-P1541, CGEL-2002-CH17-P1548
- concept_ids: cgel-ch17-concept
- tree_ids:

## Outcomes
- o1: Trace reflexives and reciprocals to the expressions that license them.
- o2: Choose between repeating a noun and using one, a fused head or a demonstrative.
- o3: Explain what is recoverable when a verb phrase or other material is left out.

## Key terms
- **antecedent** — An expression that supplies the interpretation for another expression, as doors supplies the noun understood in the red one.
- **reflexive** — A form such as herself or themselves. It can point back to a local antecedent or add emphasis in a separate use.
- **reciprocal** — A form such as each other that represents a relation holding in both directions or among members of a group.
- **ellipsis** — A construction where material is unexpressed but can be recovered from the context.

## Rules
- CLS-1101
- CLS-1103
- PHR-580
- PHR-582
- PHR-590
- PHR-593
- PHR-600
- PHR-601
- PHR-602
- PHR-606
- PHR-612
- PHR-620
- PHR-629
- PHR-632
- PHR-644
- PHR-645
- PHR-653
- PHR-654
- PHR-655
- PHR-656
- PHR-666
- PHR-673
- PHR-684
- PHR-696
- PHR-704
- PHR-705
- PHR-706
- PHR-737
- PHR-748
- PHR-769

## Sources
- CGEL-2002-CH17-P1457 (p.1457)
- CGEL-2002-CH17-P1488 (p.1488)
- CGEL-2002-CH17-P1497 (p.1497)
- CGEL-2002-CH17-P1499 (p.1499)
- CGEL-2002-CH17-P1500 (p.1500)
- CGEL-2002-CH17-P1501 (p.1501)
- CGEL-2002-CH17-P1502 (p.1502)
- CGEL-2002-CH17-P1503 (p.1503)
- CGEL-2002-CH17-P1505 (p.1505)
- CGEL-2002-CH17-P1508 (p.1508)
- CGEL-2002-CH17-P1509 (p.1509)
- CGEL-2002-CH17-P1512 (p.1512)
- CGEL-2002-CH17-P1515 (p.1515)
- CGEL-2002-CH17-P1516 (p.1516)
- CGEL-2002-CH17-P1518 (p.1518)
- CGEL-2002-CH17-P1520 (p.1520)
- CGEL-2002-CH17-P1524 (p.1524)
- CGEL-2002-CH17-P1528 (p.1528)
- CGEL-2002-CH17-P1530 (p.1530)
- CGEL-2002-CH17-P1539 (p.1539)
- CGEL-2002-CH17-P1541 (p.1541)
- CGEL-2002-CH17-P1548 (p.1548)

## Chapter article

### Introduction
Two volunteers are sorting a box of lanterns. “I’ve checked the red one,” says Mira. “So have I,” says Jo. “Did they come with any batteries?” “The red one did.” Nobody repeats *lantern* or *checked the red one* every time. A reader can still recover both pieces of information because the conversation makes them available. The same attention to context will help with *herself* and *each other*, though those forms require a closer look at the structure around them.

### Topics
- Finding the right antecedent
- Replacing or leaving out a noun
- Recovering missing actions and complements

### Example
- context: The volunteers choose a lantern from the box.
- sentence: The red lantern is cracked. I’ll take the blue one.
- explanation: One stands for lantern. Blue tells us which lantern is meant.

### Preview
- Follow one reference at a time, from the people doing the work to the lanterns and then to the work itself.

### Concept: Who can a reflexive or reciprocal refer to?
In *Mira reminded herself to bring batteries*, the object *herself* refers to Mira. Move it into *Mira said that Jo had reminded herself* and the ordinary local antecedent is Jo, even if the account is still about Mira. In *If she injures herself, Mira will stop*, *she* supplies the local antecedent. Its interpretation can in turn come from Mira. The lexical construction *Mira prides herself on her patience* also requires a reflexive object tied to the subject.

Sometimes a reflexive emphasises an existing participant. *Mira herself checked the lantern* singles Mira out. *Mira checked the lantern herself* can emphasise that she did it personally. In the latter position it points back to the subject. Put the emphatic expression inside a noun phrase and the local attachment changes: *the assistant of the manager herself* puts the emphasis with *the manager*. If you need the genitive, use *the manager’s assistant* and put the emphasis elsewhere. *The manager herself’s assistant* does not work in the ordinary construction.

*Mira and Jo helped each other* gives the reciprocal a local plural subject. Being mentioned in the preceding sentence is insufficient to fill that role. Some speakers also allow *Everyone knows each other*. *Everyone* is singular in form but can supply the whole group for this reading. With an ordinary noun phrase such as *every volunteer*, use *All the volunteers know each other* or *Every volunteer knows the others*. The split *Mira and Jo each checked the other’s lantern* has *each* associated with the subject and *the other’s lantern* as the object. In a split construction with *one*, it can follow the verb before a preposition phrase, as in *The lanterns stood one beside the other*. To use *the other* as direct object here, the split construction would instead use *each*, as in *They each checked the other*. For emphasis alone, *Mira and Jo themselves checked the lanterns* uses a reflexive. The reciprocal *each other* has no equivalent emphatic use. In *Mira and Jo found photos of each other*, the main subject supplies the antecedent. If the names are merely possessors, as in *Mira and Jo’s photos were found by each other*, that genitive cannot supply the antecedent in this mixed verb–noun construction.

### Concept: Which parts of the noun phrase can you recover?
*This red lantern* and *these red lanterns* distinguish number. In *this lantern here* and *that lantern there*, the pointing expressions fit the intended spatial reading. A formal comparison such as *The output of this lantern exceeds that of the older model* uses *that* without pointing. Here *that* performs the determiner and head jobs, with *output* recoverable from the first part. It can recover a mass noun in *the equipment at this site and that at the other site*. Substitution with *one* needs a count interpretation: *the red lantern and the blue one* works, while *new equipment and old one* does not express the corresponding mass comparison.

*Which one?* and *Which?* can ask the same question when the choice is clear. *Every one* needs the expressed *one*. *We need three* and *We found none* have fused heads, while *three spare ones* and *no working ones* allow *ones* after a modifier. *An excellent one* keeps the head overt. One can also carry ordinary descriptions, as in *the damaged ones from the shed*. It does not freely inherit all the complements a noun licenses. Keep the noun in *the claim that the lantern is safe* or *the owner of the lantern*. Some *of* complements remain possible with a different kind of noun. After *a recording of the morning session*, you could ask for *the one of the afternoon session*. If the group is contrasting two usable items, *the other red lantern* puts *other* before the attributive adjective. With an indefinite or interrogative expression, the counterpart can follow the head: *something else* or *what else?*

### Concept: What is missing from the reply?
*Mira has checked the lantern, and Jo has too* keeps the auxiliary *has*. The missing material is recovered as *checked the lantern*. After *Mira checked the lantern*, completion with *Jo did too* uses supportive *did* to stand with the omitted verb phrase. With certain lexical verbs, a reply can leave the whole selected complement understood. In *I asked whether the lantern worked, but Jo didn’t say*, what Jo did not say is recoverable. In *Mira tried to fix the first lantern, and Jo will try*, the understood complement of the second *try* is *to fix the first lantern*. To change the object, restore the clause: *Jo will try to fix the second one*.

*Mira cleaned the lens, and Jo did so too* uses *do so* for the action. It ordinarily draws on a lexical verb phrase, while *has* itself is not what *do so* stands for. If the lens is replaced by the handle as the contrasting direct object, *Jo cleaned the handle* makes the contrast explicit. Some later phrases can specify different circumstances, as in *Jo did so after lunch*, but a comparative such as *Jo cleaned the lens more carefully than Mira did* uses ellipsis. In this construction, *did so* does not supply the counterpart required by the comparison. Ellipsis after an auxiliary sometimes does leave a contrasting complement, as in *I can’t check the first lantern, but I can the others*. The choice is restricted. For instance, in *Mira had seemed confident, but Jo had seemed worried*, leaving just *had worried* changes the reading. Keeping the lower verb preserves the contrast intended.

Back in the opening exchange, “So have I” adds a matching positive statement with inversion. For *Mira hasn’t checked it*, use *Neither have I* or *Nor have I*. If Mira says, “Someone took the batteries,” Jo can ask “Who?” “Which batteries?” keeps the interrogative phrase together. “Which ones?” and simply “Which?” can also recover the batteries. A fragment can strand a preposition in “Who for?” With a determiner and its noun, Cambridge gives the preposition-first pattern for this kind of fragment. Compare “In which van?” with the full question “Which van are they travelling in?”

### Contrast: Two ways to avoid repeating a noun
- *I’ll take the blue one.* One stands for the count noun lantern.
- *I’ll take the cheaper.* In a suitable two-item comparison, cheaper can carry the head function with the article.

### Application
- example: Jo wrote, “Mira said that Jo had reminded herself to bring the lanterns. Mira hasn’t checked the red one, and so haven’t I.”
- **Trace herself** — Identify the local antecedent in the first sentence.
- **Repair the reply and recover one** — Keep the negative meaning and say what one refers to.

### Reveal: Check your analysis
*Herself* refers to Jo, the local subject of *had reminded*. The reply is *Mira hasn’t checked the red one, and neither have I*. *One* refers to a lantern, and the reply leaves *checked the red one* understood.

### Recap
When a familiar expression saves words, try putting back what the reader recovers. Then examine the structure that licenses it. A reflexive needs a suitable antecedent, a pro-nominal *one* needs a count reading, and *Neither have I* recovers a negative proposition with its own particular word order.

### Self-check
- Why can you say “We need three spare ones” but normally “We need three” when there is no “spare”?
- Three can carry the head job alone. The adjective in “three spare ones” makes a different phrase possible, with ones as the overt head.

## Teaching blocks
### Teaching block 1
For a reflexive, have the learner point to the subject of the clause containing it before looking at any other name. Then distinguish a reflexive object from an added emphatic reflexive.

### Teaching block 2
Let learners answer the same request in three ways, such as “the red lantern”, “the red one” and “the cheaper”. Ask precisely which word carries the nominal work in each response.

### Teaching block 3
Close by reconstructing a reply word for word. The context supplies a meaning, but a reply such as “neither have I” still needs the auxiliary and polarity required by its own construction.

## Worked example
- sentence: Jo can check the blue lantern, and so can Mira.
- origin: Original SynTutor example.
- step: Recover “check the blue lantern” after the second “can”.
- step: Find “Mira” as the new subject. The addition is positive, so choose “so”.
- step: Invert the auxiliary and subject in the additive clause.

## Stage checks

#### predict
- prompt: In “If she hurts herself, Mira will stop”, which expression is the immediate antecedent of herself?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH17-P1488
- hint: Start with the subject of hurts. Follow the reference to Mira only after that.
- options:
  - id: a
    text: the whole if clause
    feedback: The clause contains the reflexive. Look inside it for the subject, which supplies the antecedent.
  - id: b
    text: Mira directly
    feedback: Mira supplies the reference for she. The local antecedent of the reflexive is the pronoun she.
  - id: c
    text: she
    feedback: She is local to the reflexive. Context can then identify she as Mira.

#### guided
- prompt: After “All the lanterns were tested”, which short subject fits “___ was safe” and expresses every?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH17-P1512
- hint: Recall what can stand alone in “Each was safe”.
- options:
  - id: a
    text: Every one
    feedback: Every requires one in this construction. Each could stand alone.
  - id: b
    text: Every
    feedback: Every needs an expressed head in this construction. Add the count form one.
  - id: c
    text: Every them
    feedback: Them cannot fill the position after every. In a partitive use “every one of them”.

#### transfer
- prompt: Which continuation adds Jo to “Mira can lift the crate”?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH17-P1539
- hint: Use the same polarity as the first clause and match the auxiliary.
- options:
  - id: a
    text: and neither can Jo
    feedback: Neither adds a matching negative statement. The first clause is positive here.
  - id: b
    text: and so Jo can’t
    feedback: The reply adds a different subject affirmatively. Keep can positive and put it before Jo.
  - id: c
    text: and so can Jo
    feedback: The first clause is positive. So adds a positive counterpart with auxiliary–subject order.

#### exit
- prompt: What is missing in “I asked whether it worked, but she didn’t say”?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH17-P1528
- hint: Ask what question she could have answered.
- options:
  - id: a
    text: The subject of didn’t say
    feedback: She is already the subject. Read back to the question that was put to her.
  - id: b
    text: The content of what she could have said, whether it worked
    feedback: The lexical verb say can leave its complement understood here. She is the overt subject.
  - id: c
    text: A mandatory direct object after did so
    feedback: There is no do so here. Didn’t supports the negative, and lexical say can leave its complement understood.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: Who does herself ordinarily refer to in “Mira said Jo had reminded herself”?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH17-P1488
- options:
  - id: a
    text: Either person equally
    feedback: Jo is the subject of the clause containing the reflexive object.
  - id: b
    text: Jo
    feedback: Jo is the subject of the clause containing the reflexive object.
  - id: c
    text: Mira
    feedback: Jo is the subject of the clause containing the reflexive object.

#### opening-2
- prompt: The intended antecedent is the count noun lantern. Which phrase avoids repeating it?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH17-P1512, CGEL-2002-CH17-P1515
- options:
  - id: a
    text: the blue one
    feedback: One supplies the nominal head and blue identifies the lantern.
  - id: b
    text: the blue equipment
    feedback: One supplies the nominal head and blue identifies the lantern.
  - id: c
    text: the one blue
    feedback: One supplies the nominal head and blue identifies the lantern.

#### opening-3
- prompt: Respond to “I haven’t checked the lens” by adding the same negative statement about yourself.
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH17-P1539
- options:
  - id: a
    text: So haven’t I.
    feedback: Neither introduces the ordinary negative additive reply. The auxiliary precedes the subject.
  - id: b
    text: So have I.
    feedback: Neither introduces the ordinary negative additive reply. The auxiliary precedes the subject.
  - id: c
    text: Neither have I.
    feedback: Neither introduces the ordinary negative additive reply. The auxiliary precedes the subject.

#### opening-4
- prompt: What does herself do in “Mira herself checked the lens”?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH17-P1497, CGEL-2002-CH17-P1499
- options:
  - id: a
    text: It is the object Mira checked.
    feedback: The lens is the object. The reflexive emphasises that Mira did the checking.
  - id: b
    text: It emphasises Mira.
    feedback: The lens is the object. The reflexive emphasises that Mira did the checking.
  - id: c
    text: It names a second person.
    feedback: The lens is the object. The reflexive emphasises that Mira did the checking.

#### opening-5
- prompt: Which short phrase works after “We have two lanterns but we need ___”?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH17-P1512
- options:
  - id: a
    text: three
    feedback: The numeral can carry the head function alone. Three spare ones has a different structure with an intervening modifier.
  - id: b
    text: three lantern
    feedback: The numeral can carry the head function alone. Three spare ones has a different structure with an intervening modifier.
  - id: c
    text: three ones
    feedback: The numeral can carry the head function alone. Three spare ones has a different structure with an intervening modifier.

### Closing questions

#### closing-1
- prompt: Who helps whom in “Mira and Jo helped each other”?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH17-P1502, CGEL-2002-CH17-P1503, CGEL-2002-CH17-P1505
- options:
  - id: a
    text: Mira and Jo each helped themselves.
    feedback: The reciprocal links members of the subject and makes the helping mutual.
  - id: b
    text: Only Mira helped Jo.
    feedback: The reciprocal links members of the subject and makes the helping mutual.
  - id: c
    text: Mira helped Jo, and Jo helped Mira.
    feedback: The reciprocal links members of the subject and makes the helping mutual.

#### closing-2
- prompt: Which phrase can recover the mass noun equipment in “the equipment on this floor and ___ on the next”?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH17-P1509, CGEL-2002-CH17-P1512, CGEL-2002-CH17-P1515
- options:
  - id: a
    text: the ones
    feedback: Nonpointing that can refer back to equipment in this formal construction. One ordinarily needs a count reading.
  - id: b
    text: the one
    feedback: Nonpointing that can refer back to equipment in this formal construction. One ordinarily needs a count reading.
  - id: c
    text: that
    feedback: Nonpointing that can refer back to equipment in this formal construction. One ordinarily needs a count reading.

#### closing-3
- prompt: What is recovered after the final has in “Mira has cleaned the lens, and Jo has too”?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH17-P1524, CGEL-2002-CH17-P1528
- options:
  - id: a
    text: cleaned the lens
    feedback: The auxiliary stays overt, and its complement is recovered from the first clause.
  - id: b
    text: Jo has
    feedback: The auxiliary stays overt, and its complement is recovered from the first clause.
  - id: c
    text: the lens by itself
    feedback: The auxiliary stays overt, and its complement is recovered from the first clause.

#### closing-4
- prompt: Why can “Jo did so too” follow “Mira cleaned the lens” in the same-action reading?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH17-P1530
- options:
  - id: a
    text: Did so always requires a new direct object.
    feedback: The do so construction recovers the verb and its complement together.
  - id: b
    text: Do so picks up cleaned the lens as a whole.
    feedback: The do so construction recovers the verb and its complement together.
  - id: c
    text: So stands for lens alone.
    feedback: The do so construction recovers the verb and its complement together.

#### closing-5
- prompt: Which phrase uses else in its ordinary position?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH17-P1548
- options:
  - id: a
    text: else something
    feedback: Else follows its head in something else. In a comparable count noun phrase use another lantern or the other lantern.
  - id: b
    text: something else
    feedback: Else follows its head in something else. In a comparable count noun phrase use another lantern or the other lantern.
  - id: c
    text: else lantern
    feedback: Else follows its head in something else. In a comparable count noun phrase use another lantern or the other lantern.

---

# Lesson: cgel-ch18 — Morphology and spelling

- lesson_id: cgel-ch18
- title: Morphology and spelling
- track: grammar
- chapter: 18
- content_version: 2.1.0
- difficulty: advanced
- estimated_minutes: 11
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: MORPH-078, MORPH-080, MORPH-083, MORPH-092, MORPH-104, MORPH-105, MORPH-109, MORPH-114, MORPH-130, MORPH-141
- source_ids: CGEL-2002-CH18-P1575, CGEL-2002-CH18-P1576, CGEL-2002-CH18-P1577, CGEL-2002-CH18-P1579, CGEL-2002-CH18-P1585, CGEL-2002-CH18-P1595, CGEL-2002-CH18-P1596, CGEL-2002-CH18-P1598, CGEL-2002-CH18-P1603, CGEL-2002-CH18-P1612, CGEL-2002-CH18-P1618
- concept_ids: cgel-ch18-concept
- tree_ids:

## Outcomes
- o1: Apply common spelling changes when adding an inflectional suffix.
- o2: Distinguish ordinary noun plurals, surname plurals and genitives.
- o3: Use sound or clause position to choose between forms such as a and an or am not and aren’t.

## Key terms
- **inflection** — A form change that marks a grammatical distinction such as past tense or plural.
- **base** — The form to which a suffix is attached, such as fit in fitted.
- **genitive** — A form that marks a relation such as possession, as in the guests’ coats.

## Rules
- MORPH-078
- MORPH-080
- MORPH-083
- MORPH-092
- MORPH-104
- MORPH-105
- MORPH-109
- MORPH-114
- MORPH-130
- MORPH-141

## Sources
- CGEL-2002-CH18-P1575 (p.1575)
- CGEL-2002-CH18-P1576 (p.1576)
- CGEL-2002-CH18-P1577 (p.1577)
- CGEL-2002-CH18-P1579 (p.1579)
- CGEL-2002-CH18-P1585 (p.1585)
- CGEL-2002-CH18-P1595 (p.1595)
- CGEL-2002-CH18-P1596 (p.1596)
- CGEL-2002-CH18-P1598 (p.1598)
- CGEL-2002-CH18-P1603 (p.1603)
- CGEL-2002-CH18-P1612 (p.1612)
- CGEL-2002-CH18-P1618 (p.1618)

## Chapter article

### Introduction
A stage manager’s checklist says, “We fitted the latch, tied the cable and labelled the boxes.” None of the jobs is difficult to picture. Spelling the verbs is a different matter: *fit* doubles its final letter, *tie* drops part of its ending before *-ing*, and *label* has two accepted spelling patterns. Follow the checklist through a few changes of tense and number, then compare what happens when the choice depends on sound or clause type instead.

### Topics
- What changes when a suffix is added
- Plurals and names
- Choosing forms by sound or construction

### Example
- context: The manager updates a job from in progress to complete.
- sentence: The crew fitted a new latch.
- explanation: Fit ends in a single consonant letter after a single vowel letter. Before -ed, double the t.

### Preview
- Compare similar-looking verbs, then apply the same attention to endings in a list of guests and labels.

### Concept: Look at the end of the base, then listen for stress
*Fit* gives *fitted* and *fitting*. *Visit* gives *visited* and *visiting* because the stress is earlier, even though its last letters look like those of *fit*. *Wait* gives *waited* and *waiting*, with a two-letter vowel spelling. For the general doubling pattern, look for a single final consonant letter after a single vowel letter in the stressed final syllable, before a vowel-initial suffix. British and American conventions differ for some final *l* spellings, as in *labelled* and *labeled*.

*Hope* gives *hoping* by dropping final silent *e*, while *hop* gives *hopping* by doubling *p*. In the ongoing version of the checklist, *tie* gives *tying* and *lie* gives *lying*. Some bases ending in *c* add *k* before these endings, as in *panic*, *panicked* and *panicking*. Irregular verbs can change their vowels instead of taking the ordinary past suffix. *Sing*, *sang*, *sung* shows the plain form, past tense and past participle across three different vowels.

### Concept: The guest list needs two different kinds of ending
An ordinary noun like *city* gives *cities*, while *day* gives *days*. The family name *Brady* ordinarily gives *the Bradys*. If a notice is about their seats, write *the Bradys’ seats*. For the surname *Jones*, use *the Joneses* as the plural. The apostrophe signals the genitive after the plural ending in *the Joneses’ seats*.

Try the same distinction with *guest*. Write *the guest’s seat* for one and *the guests’ seats* for more than one. Plurals like *children*, which lack the regular *-s* ending, take *’s* in *the children’s seats*.

### Concept: Listen to the next sound and read the next slot
The manager puts the latch in *an envelope* and checks it with *a unit* from the tool kit. *Unit* begins with a consonant sound, so the spelling of the initial letter tells you too little. *An hour* illustrates the reverse: the written *h* is silent. Say the phrase aloud if the article is in doubt.

When the manager asks “Aren’t I on the rota?”, that inverted form is widespread. In a statement the corresponding wording is *I’m not on the rota* or *I am not on the rota*. Some dialects use *amn’t*. The place where a form is available can be part of knowing its grammar, just as the previous chapter’s questions showed.

### Contrast: Three nearly identical bases
- *hop → hopping* adds the doubled p before the suffix.
- *hope → hoping* drops the final silent e.
- *tie → tying* uses y before the ending.

### Application
- example: The draft says, “The Bradies left a hour ago. I aren’t sure who was tieing the cable.”
- **Fix the family name and article** — Keep the family surname Brady and say hour aloud.
- **Fix the verb forms** — Use ordinary negative statement order and the participle of tie.

### Reveal: Check your analysis
*The Bradys left an hour ago. I’m not sure who was tying the cable.* The name keeps its *y*, *hour* begins with a vowel sound, and the verb choices follow their own spelling and clause patterns.

### Recap
The end of a word is easier to spell once you know what you are adding. Test the base and the suffix when you inflect a word, and test the sound or clause position when choosing *a*, *an*, *am not* or *aren’t I*.

### Self-check
- Why do “hopping” and “hoping” have different spellings even though both end in -ing?
- Hopping comes from hop, which doubles p. Hoping comes from hope, which drops its final e.

## Teaching blocks
### Teaching block 1
Show the bases before presenting their inflections. Contrast “fit” with “visit” so the learner has to use stress as well as letter shape.

### Teaching block 2
Have learners name the number first in a surname example, then add possession as a second operation. The plain plural can stay visible while they choose where the apostrophe goes.

## Worked example
- sentence: The stage manager has tied the cables, and the Bradys are taking their seats.
- origin: Original SynTutor example.
- step: Recognise “tied” as the past participle selected by “has”. The -ing form would be “tying”.
- step: Read “the Bradys” as the plain plural of the surname.
- step: If the seats belong to the family, write “the Bradys’ seats”.

## Stage checks

#### predict
- prompt: Which form of fit completes “The crew is ___ the latch”?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH18-P1575, CGEL-2002-CH18-P1576
- hint: Start from the base fit and check the last two letters.
- options:
  - id: a
    text: fittting
    feedback: Doubling adds one t to fit. This spelling adds two.
  - id: b
    text: fiting
    feedback: The stressed one-syllable base fit doubles its final consonant before -ing.
  - id: c
    text: fitting
    feedback: Fit keeps its short stressed vowel and doubles its t before -ing.

#### guided
- prompt: Write the genitive for the seats assigned to the Brady family as a group.
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH18-P1595, CGEL-2002-CH18-P1596
- hint: Write the family’s plain plural first.
- options:
  - id: a
    text: the Bradys’ seats
    feedback: Form the plural Bradys first, then mark the genitive after the plural s.
  - id: b
    text: the Brady’s seats
    feedback: Brady’s is singular genitive. Add the plural first to refer to the family.
  - id: c
    text: the Bradies’ seats
    feedback: The plural of the family name is Bradys. Keep y before the ending.

#### transfer
- prompt: Which forms complete “I ___ yesterday. I’ve ___ today” for sing?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH18-P1603
- hint: The blank after have needs a participle.
- options:
  - id: a
    text: sang / sung
    feedback: Sang is the past tense, and perfect have selects the past participle sung.
  - id: b
    text: sung / sang
    feedback: Sung is the participle, so it belongs after have. Begin with the past sang.
  - id: c
    text: singed / sang
    feedback: Sing uses irregular past and participial forms, sang and sung.

#### exit
- prompt: Choose the ordinary statement and article in “I ___ sure we have ___ hour to wait.”
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH18-P1612, CGEL-2002-CH18-P1618
- hint: Say hour aloud and compare the negative question with the negative statement.
- options:
  - id: a
    text: am not / a
    feedback: Am not fits. Hour begins with a vowel sound, so change the article.
  - id: b
    text: aren’t / a
    feedback: Aren’t I is ordinary in the inverted question, but I aren’t is not the corresponding standard statement. Hour needs an.
  - id: c
    text: am not / an
    feedback: The uninverted statement uses am not, and hour starts with a vowel sound.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: What is the ordinary past-tense spelling of fit in “They ___ a new latch”?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH18-P1575
- options:
  - id: a
    text: fited
    feedback: Fit meets the conditions for doubling t before -ed.
  - id: b
    text: fittted
    feedback: Fit meets the conditions for doubling t before -ed.
  - id: c
    text: fitted
    feedback: Fit meets the conditions for doubling t before -ed.

#### opening-2
- prompt: Which phrase names the Brady family in the plural without showing possession?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH18-P1585, CGEL-2002-CH18-P1595
- options:
  - id: a
    text: the Brady’s
    feedback: Surname Brady retains y in its ordinary plural. An apostrophe would signal a different construction.
  - id: b
    text: the Bradys
    feedback: Surname Brady retains y in its ordinary plural. An apostrophe would signal a different construction.
  - id: c
    text: the Bradies
    feedback: Surname Brady retains y in its ordinary plural. An apostrophe would signal a different construction.

#### opening-3
- prompt: Which article fits “___ unit” in ordinary pronunciation?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH18-P1618
- options:
  - id: a
    text: a
    feedback: Unit begins with a consonant sound even though its first written letter is a vowel.
  - id: b
    text: an
    feedback: Unit begins with a consonant sound even though its first written letter is a vowel.
  - id: c
    text: both equally in the same pronunciation
    feedback: Unit begins with a consonant sound even though its first written letter is a vowel.

#### opening-4
- prompt: Which pair correctly distinguishes hop from hope in the -ing forms?
- answer: c
- outcome_ids: o1
- source_ids: CGEL-2002-CH18-P1575, CGEL-2002-CH18-P1576
- options:
  - id: a
    text: hopping / hopeing
    feedback: Hop doubles p. Hope drops silent e.
  - id: b
    text: hoping / hopping
    feedback: Hop doubles p. Hope drops silent e.
  - id: c
    text: hopping / hoping
    feedback: Hop doubles p. Hope drops silent e.

#### opening-5
- prompt: Which form refers to seats belonging to several guests?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH18-P1595, CGEL-2002-CH18-P1596
- options:
  - id: a
    text: the guest’s seats
    feedback: The regular plural guests has an apostrophe after its s in the genitive.
  - id: b
    text: the guests seats
    feedback: The regular plural guests has an apostrophe after its s in the genitive.
  - id: c
    text: the guests’ seats
    feedback: The regular plural guests has an apostrophe after its s in the genitive.

### Closing questions

#### closing-1
- prompt: Choose the ordinary inverted tag after “I’m on the list”.
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH18-P1612
- options:
  - id: a
    text: isn’t I
    feedback: Aren’t I is widely established in inversion. A statement instead uses I’m not or I am not.
  - id: b
    text: aren’t I
    feedback: Aren’t I is widely established in inversion. A statement instead uses I’m not or I am not.
  - id: c
    text: I aren’t
    feedback: Aren’t I is widely established in inversion. A statement instead uses I’m not or I am not.

#### closing-2
- prompt: Which form fits “She’s ___ the cable” if the base is tie?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH18-P1577, CGEL-2002-CH18-P1579
- options:
  - id: a
    text: tieing
    feedback: A base ending in ie changes to y before -ing in this pattern.
  - id: b
    text: tying
    feedback: A base ending in ie changes to y before -ing in this pattern.
  - id: c
    text: tiing
    feedback: A base ending in ie changes to y before -ing in this pattern.

#### closing-3
- prompt: Which plural preserves the ending of the surname Jones?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH18-P1595
- options:
  - id: a
    text: the Jones
    feedback: The plural adds -es. A genitive apostrophe is a separate matter.
  - id: b
    text: the Jones’s
    feedback: The plural adds -es. A genitive apostrophe is a separate matter.
  - id: c
    text: the Joneses
    feedback: The plural adds -es. A genitive apostrophe is a separate matter.

#### closing-4
- prompt: Why is it “visited” but “fitted”?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH18-P1575
- options:
  - id: a
    text: Visit cannot take -ed.
    feedback: The general doubling pattern depends on final stress as well as letters.
  - id: b
    text: Visit has earlier stress, while the single syllable in fit is stressed.
    feedback: The general doubling pattern depends on final stress as well as letters.
  - id: c
    text: Fit ends in a silent e.
    feedback: The general doubling pattern depends on final stress as well as letters.

#### closing-5
- prompt: Which pair follows the sound rule in both places?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH18-P1618
- options:
  - id: a
    text: an hour / an one-off event
    feedback: Hour starts with a vowel sound. One starts with a consonant sound.
  - id: b
    text: an hour / a one-off event
    feedback: Hour starts with a vowel sound. One starts with a consonant sound.
  - id: c
    text: a hour / an one-off event
    feedback: Hour starts with a vowel sound. One starts with a consonant sound.

---

# Lesson: cgel-ch19 — Word formation and inflection

- lesson_id: cgel-ch19
- title: Word formation and inflection
- track: grammar
- chapter: 19
- content_version: 2.1.0
- difficulty: advanced
- estimated_minutes: 12
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: MORPH-237, MORPH-258, MORPH-309, MORPH-311, MORPH-313, MORPH-316, MORPH-357, MORPH-385, MORPH-391, MORPH-445, MORPH-477, MORPH-480, MORPH-481, MORPH-482, MORPH-483
- source_ids: CGEL-2002-CH19-P1655, CGEL-2002-CH19-P1660, CGEL-2002-CH19-P1675, CGEL-2002-CH19-P1676, CGEL-2002-CH19-P1677, CGEL-2002-CH19-P1687, CGEL-2002-CH19-P1694, CGEL-2002-CH19-P1695, CGEL-2002-CH19-P1696, CGEL-2002-CH19-P1709, CGEL-2002-CH19-P1717, CGEL-2002-CH19-P1718, CGEL-2002-CH19-P1719
- concept_ids: cgel-ch19-concept
- tree_ids:

## Outcomes
- o1: Distinguish a new word built from a base from an inflected form of an existing word.
- o2: Build and spell familiar compounds, derivatives and inhabitant names.
- o3: Read a composite numeral or fraction from the inside out.

## Key terms
- **derivation** — Word formation that creates a new word from a base, as in drive and driver.
- **compound** — A word formed from two or more bases, as in passer-by.
- **multiplier** — The part giving the number of hundreds, thousands or other powers in a composite numeral.

## Rules
- MORPH-237
- MORPH-258
- MORPH-309
- MORPH-311
- MORPH-313
- MORPH-316
- MORPH-357
- MORPH-385
- MORPH-391
- MORPH-445
- MORPH-477
- MORPH-480
- MORPH-481
- MORPH-482
- MORPH-483

## Sources
- CGEL-2002-CH19-P1655 (p.1655)
- CGEL-2002-CH19-P1660 (p.1660)
- CGEL-2002-CH19-P1675 (p.1675)
- CGEL-2002-CH19-P1676 (p.1676)
- CGEL-2002-CH19-P1677 (p.1677)
- CGEL-2002-CH19-P1687 (p.1687)
- CGEL-2002-CH19-P1694 (p.1694)
- CGEL-2002-CH19-P1695 (p.1695)
- CGEL-2002-CH19-P1696 (p.1696)
- CGEL-2002-CH19-P1709 (p.1709)
- CGEL-2002-CH19-P1717 (p.1717)
- CGEL-2002-CH19-P1718 (p.1718)
- CGEL-2002-CH19-P1719 (p.1719)

## Chapter article

### Introduction
A travel article mentions a *four-night stay*, two *passers-by* and a crowd of *five hundred and three*. The writer is counting several things each time. Yet *night* stays singular, *passer* takes the plural, and *hundred* stays as it is. Last lesson, the base gave us most of what we needed for the spelling. Here we also need to look at the structure built around it. The differences in these three phrases give us a place to start.

### Topics
- Where a compound carries number
- What spelling preserves in a derived word
- How numerals group their parts

### Example
- context: A reporter counts the people who stopped to help.
- sentence: Two passers-by stopped to help.
- explanation: The established plural attaches to passer, the first part of passer-by.

### Preview
- Start with the travel article, then test the patterns on new compounds, words and numbers.

### Concept: Put the number on the right part
*We stayed four nights* counts nights directly. In *a four-night stay*, the measure expression modifies *stay*, and *night* stays singular inside the compound. In *a two-bedroomed flat* the plural meaning is already supplied by *two*. The possessive *-ed* formation means “with two bedrooms”. A count of people in *two passers-by* behaves differently. The established plural inflects *passer*. It is worth learning the plural of particular compounds because the recipes for established compounds vary.

### Concept: Forming a word can change its spelling
The agent noun *driver* comes from *drive* plus *-er*. The final silent *e* of the base drops before the suffix. Compare *commit* and *committal*, where the stressed final syllable favours doubling, or *propel* and *propellant*. The broader spelling patterns introduced in the previous lesson also appear in derivation, with some word-specific and dialectal variants.

Sometimes retaining *e* helps preserve a soft consonant. *Noticeable* keeps it after *c*, and *changeable* after *g*. The *y* in *happy* changes in *happiness*, while *babyhood* keeps its *y*. Even prefixes have forms suited to the base. Negative *in-* appears as *im-* in *impossible*, *il-* in *illegal* and *ir-* in *irregular*. Established forms are a better guide here than joining letter strings mechanically.

### Concept: A place name does not predict every related word
An article can say *the Australian team* and *two Australians*. The inhabitant noun changes number. *Two Swiss competitors* uses *Swiss* unchanged as an adjective, and in noun use *Swiss* can also remain unchanged in the plural. Some writers prefer *a Swiss person* in the singular. *A Swedish runner* and *two Swedes* show that the inhabitant noun can differ from the adjective. Some place names lack a widely established derived adjective. A phrase like *a visitor from the island* can say exactly what is needed without inventing an ending.

### Concept: Work from the number’s internal structure
*Five hundred and three* means five times a hundred plus three. Inside that number, *hundred* has no plural ending. *Hundreds of visitors* gives a different, approximate quantity. *A hundred* and *one hundred* are both available at the beginning of many numeral expressions. In *two thousand one hundred and three*, *one hundred* is the natural choice for that internal addition. Some choices about *and* vary with region and style.

In *twenty-first* or *one hundred and first*, the final cardinal part takes the ordinal form. A fraction has another structure: a numerator and a denominator. In *one fifth*, the denominator is singular, and in *three fifths*, that denominator takes the plural. The visible ending belongs to the head of the fraction expression, just as *passers-by* placed its ending on the part that carries number in that compound.

### Contrast: Quantity outside and inside a compound
- *We stayed four nights.* Nights heads an ordinary plural phrase.
- *We booked a four-night stay.* Night is inside the measure compound modifying stay.

### Application
- example: A draft says, “Two passer-bys told us about a three-nights stay. About four hundreds visitors booked it.” Assume the writer wants the numeral 400 after about.
- **Find the head in each phrase** — Use the established plural for passer-by and the singular measure form inside the compound.
- **Read the number** — Keep the exact numeral form even though about makes the estimate approximate.

### Reveal: Check your analysis
*Two passers-by told us about a three-night stay. About four hundred visitors booked it.* The modifier *about* qualifies the number. The numeral still has uninflected *hundred*.

### Recap
Before adding an ending, ask what expression you are building and which part controls its form. A compound, a derived word and a numeral each have their own internal structure.

### Self-check
- Why do “hundreds of visitors” and “four hundred visitors” use different forms of hundred?
- Hundreds of is an approximate plural quantity expression. In four hundred, hundred is a fixed numeral head with the multiplier four.

## Teaching blocks
### Teaching block 1
Keep a number constant across phrases, such as “four nights” and “a four-night stay”. Ask where the count is expressed in each.

### Teaching block 2
Build a composite numeral in stages. Read the multiplier with its power word, then say what is added. That makes the uninflected power word visible.

## Worked example
- sentence: Around three fifths of the visitors chose the two-day tour.
- origin: Original SynTutor example.
- step: Read “three fifths” as a numerator followed by the plural denominator.
- step: Keep “day” singular inside the measure modifier “two-day”.
- step: Compare “the tour lasts two days”, where “days” heads the measure phrase itself.

## Stage checks

#### predict
- prompt: Which pair uses singular nouns inside both measure or descriptive formations?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH19-P1660, CGEL-2002-CH19-P1709
- hint: In both modifiers, the number already tells you how many.
- options:
  - id: a
    text: a two-days tour / a two-bedroomed flat
    feedback: The descriptive compound is right. Keep day singular inside the measure modifier.
  - id: b
    text: a two-day tour / a two-bedroomed flat
    feedback: Day stays singular in the measure compound. The -ed formation is built with the uninflected noun bedroom.
  - id: c
    text: a two-days tour / a two-bedroomsed flat
    feedback: Remove the plural forms from day and bedroom in these formations.

#### guided
- prompt: Which pair shows the ordinary spelling of both derivatives?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH19-P1675, CGEL-2002-CH19-P1676
- hint: Check the stress of commit and the silent e in drive.
- options:
  - id: a
    text: commital / driveer
    feedback: The verb commit has final stress. Double t in committal. The driver spelling is right.
  - id: b
    text: committal / driveer
    feedback: Committal works. Before -er, drive drops the final e.
  - id: c
    text: committal / driver
    feedback: Commit doubles t before the suffix in committal. Drive drops silent e before -er.

#### transfer
- prompt: Which is the ordinary composite numeral for 2,103 in the style that says and before the final three?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH19-P1717, CGEL-2002-CH19-P1718
- hint: Read the thousands portion, then the hundreds portion, then the addition.
- options:
  - id: a
    text: two thousands one hundred and three
    feedback: Thousand stays uninflected after its multiplier, two.
  - id: b
    text: two thousand one hundred and three
    feedback: Both power words remain uninflected. One hundred supplies the hundreds portion.
  - id: c
    text: two thousand one hundreds and three
    feedback: The hundreds portion of the numeral uses singular-looking hundred.

#### exit
- prompt: Why is fifths plural in “three fifths” but not in “one fifth”?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH19-P1719
- hint: In a fraction, ask which word is being counted.
- options:
  - id: a
    text: Fifths is the fraction’s head, counted by the numerator.
    feedback: The denominator is the noun-like head. Its number depends on the numerator.
  - id: b
    text: Three always makes the following word an ordinal.
    feedback: Three is the numerator. It counts the denominator, whose spelling shows the ordinal and plural.
  - id: c
    text: Only the numerator can show number.
    feedback: Number shows on the denominator here. The numerator supplies the count.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: Which phrase uses a measure compound to describe a stay?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH19-P1655, CGEL-2002-CH19-P1660
- options:
  - id: a
    text: a four-night stay
    feedback: Four-night is a pre-head modifier built with singular night.
  - id: b
    text: a stay of four nights
    feedback: Four-night is a pre-head modifier built with singular night.
  - id: c
    text: the stay lasted four nights
    feedback: Four-night is a pre-head modifier built with singular night.

#### opening-2
- prompt: Which plural is established for passer-by?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH19-P1655
- options:
  - id: a
    text: passer-bys
    feedback: The plural ending goes on passer in this established compound.
  - id: b
    text: passer’s-by
    feedback: The plural ending goes on passer in this established compound.
  - id: c
    text: passers-by
    feedback: The plural ending goes on passer in this established compound.

#### opening-3
- prompt: What is the role of five in “five hundred and three”?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH19-P1717, CGEL-2002-CH19-P1718
- options:
  - id: a
    text: The denominator
    feedback: Five tells how many hundreds there are. Three is added afterward.
  - id: b
    text: The multiplier of hundred
    feedback: Five tells how many hundreds there are. Three is added afterward.
  - id: c
    text: The addition after hundred
    feedback: Five tells how many hundreds there are. Three is added afterward.

#### opening-4
- prompt: Which pair shows a new word followed by an inflected form of drive?
- answer: a
- outcome_ids: o1
- source_ids: CGEL-2002-CH19-P1675, CGEL-2002-CH19-P1676
- options:
  - id: a
    text: driver / drove
    feedback: Driver is a derived noun. Drove is the past tense of the verb.
  - id: b
    text: drove / driver
    feedback: Driver is a derived noun. Drove is the past tense of the verb.
  - id: c
    text: drives / drove
    feedback: Driver is a derived noun. Drove is the past tense of the verb.

#### opening-5
- prompt: Which spelling keeps the e that helps preserve a soft g before a suffix?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH19-P1676, CGEL-2002-CH19-P1677
- options:
  - id: a
    text: changeible
    feedback: Change keeps e in changeable before -able.
  - id: b
    text: changable
    feedback: Change keeps e in changeable before -able.
  - id: c
    text: changeable
    feedback: Change keeps e in changeable before -able.

### Closing questions

#### closing-1
- prompt: Which line distinguishes an exact numeral from an approximate quantity?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH19-P1717
- options:
  - id: a
    text: four hundreds / hundred of people
    feedback: Hundred is uninflected within the numeral. Hundreds takes of in the quantity phrase.
  - id: b
    text: four hundred / hundreds of people
    feedback: Hundred is uninflected within the numeral. Hundreds takes of in the quantity phrase.
  - id: c
    text: four hundred of people / hundreds people
    feedback: Hundred is uninflected within the numeral. Hundreds takes of in the quantity phrase.

#### closing-2
- prompt: Which adjective contains the negative form im-?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH19-P1687
- options:
  - id: a
    text: illegal
    feedback: Im- is the spelling of the negative prefix in impossible. The others show other established forms.
  - id: b
    text: impossible
    feedback: Im- is the spelling of the negative prefix in impossible. The others show other established forms.
  - id: c
    text: irregular
    feedback: Im- is the spelling of the negative prefix in impossible. The others show other established forms.

#### closing-3
- prompt: Which pair uses an adjective and a distinct inhabitant noun?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH19-P1694, CGEL-2002-CH19-P1695
- options:
  - id: a
    text: Australian / Australian
    feedback: Swedish modifies a noun. Swede names an inhabitant.
  - id: b
    text: Swiss / Swiss
    feedback: Swedish modifies a noun. Swede names an inhabitant.
  - id: c
    text: Swedish / Swede
    feedback: Swedish modifies a noun. Swede names an inhabitant.

#### closing-4
- prompt: Which is the ordinary ordinal for 21?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH19-P1718, CGEL-2002-CH19-P1719
- options:
  - id: a
    text: twenty-first
    feedback: The final cardinal element one takes the ordinal form first.
  - id: b
    text: twenty-oneth
    feedback: The final cardinal element one takes the ordinal form first.
  - id: c
    text: twentieth-one
    feedback: The final cardinal element one takes the ordinal form first.

#### closing-5
- prompt: Which wording expresses a numerator of three and a denominator of five?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH19-P1719
- options:
  - id: a
    text: three fifths
    feedback: Three is the numerator and the denominator takes the plural form fifths.
  - id: b
    text: third fives
    feedback: Three is the numerator and the denominator takes the plural form fifths.
  - id: c
    text: three fifth
    feedback: Three is the numerator and the denominator takes the plural form fifths.

---

# Lesson: cgel-ch20 — Punctuation

- lesson_id: cgel-ch20
- title: Punctuation
- track: grammar
- chapter: 20
- content_version: 2.1.0
- difficulty: advanced
- estimated_minutes: 13
- publication_status: published
- reviewed_by: Codex (editorial and Cambridge source check)
- reviewed_on: 2026-11-15
- rule_ids: OTH-671, OTH-688, OTH-698, OTH-699, OTH-701, OTH-708, OTH-712, OTH-715, OTH-717, OTH-726, OTH-730, OTH-737, OTH-740, OTH-743, OTH-756, OTH-761, OTH-764
- source_ids: CGEL-2002-CH20-P1725, CGEL-2002-CH20-P1733, CGEL-2002-CH20-P1737, CGEL-2002-CH20-P1738, CGEL-2002-CH20-P1739, CGEL-2002-CH20-P1741, CGEL-2002-CH20-P1742, CGEL-2002-CH20-P1743, CGEL-2002-CH20-P1744, CGEL-2002-CH20-P1745, CGEL-2002-CH20-P1748, CGEL-2002-CH20-P1750, CGEL-2002-CH20-P1753, CGEL-2002-CH20-P1754, CGEL-2002-CH20-P1755, CGEL-2002-CH20-P1761, CGEL-2002-CH20-P1763, CGEL-2002-CH20-P1764
- concept_ids: cgel-ch20-concept
- tree_ids:

## Outcomes
- o1: Choose punctuation from the structure of the whole written sentence.
- o2: Set off supplements, parenthetical material and direct speech using a consistent style.
- o3: Handle apostrophes, hyphens and terminal punctuation in common editing cases.

## Key terms
- **sentence terminal** — A mark such as a full stop, question mark or exclamation mark that can end a written sentence.
- **vocative** — An expression naming the person being addressed, as in Jo, close the door.
- **connective adjunct** — An expression such as however that links a clause’s meaning to surrounding text.
- **matrix sentence** — The larger sentence containing an embedded question, quotation or other construction.

## Rules
- OTH-671
- OTH-688
- OTH-698
- OTH-699
- OTH-701
- OTH-708
- OTH-712
- OTH-715
- OTH-717
- OTH-726
- OTH-730
- OTH-737
- OTH-740
- OTH-743
- OTH-756
- OTH-761
- OTH-764

## Sources
- CGEL-2002-CH20-P1725 (p.1725)
- CGEL-2002-CH20-P1733 (p.1733)
- CGEL-2002-CH20-P1737 (p.1737)
- CGEL-2002-CH20-P1738 (p.1738)
- CGEL-2002-CH20-P1739 (p.1739)
- CGEL-2002-CH20-P1741 (p.1741)
- CGEL-2002-CH20-P1742 (p.1742)
- CGEL-2002-CH20-P1743 (p.1743)
- CGEL-2002-CH20-P1744 (p.1744)
- CGEL-2002-CH20-P1745 (p.1745)
- CGEL-2002-CH20-P1748 (p.1748)
- CGEL-2002-CH20-P1750 (p.1750)
- CGEL-2002-CH20-P1753 (p.1753)
- CGEL-2002-CH20-P1754 (p.1754)
- CGEL-2002-CH20-P1755 (p.1755)
- CGEL-2002-CH20-P1761 (p.1761)
- CGEL-2002-CH20-P1763 (p.1763)
- CGEL-2002-CH20-P1764 (p.1764)

## Chapter article

### Introduction
The house editor receives a reporter’s line: “Mara asked whether the hall was open?” There is a question in it, but the reporter is telling us what Mara asked. A few lines down, the draft quotes Mara directly: “Is the hall open?” The two lines are about the same question. Their punctuation differs because the question sits at a different level. That distinction will also help when the draft has extra comments, quotations inside quotations and a stray comma that appears to separate a subject from its verb.

### Topics
- Endings and boundaries between clauses
- Commas and brackets around added material
- Quotation and punctuation within words

### Example
- context: A reporter gives an indirect account of Mara’s question.
- sentence: Mara asked whether the hall was open.
- explanation: The matrix clause is a statement even though it contains an embedded question. The full stop closes the matrix sentence.

### Preview
- Mark the outside of the sentence first. Then work inward to clauses, comments, quotations and words.

### Concept: Punctuate the whole clause before its smaller parts
Compare *Mara asked what time the hall opened* with *Did Mara ask what time the hall opened?* The inner question stays the same. The terminal reflects the larger sentence. This is the written counterpart of the distinction between direct and embedded questions earlier in the course.

Inside the sentence, look at the relation between clauses. *The hall was closed: the caretaker had gone home* uses a colon to introduce an explanation. In a series of clauses on equal terms, an editor could use semicolons or separate sentences. Multiple colons can leave the reader guessing which level the next piece attaches to. In ordinary edited prose, *The hall was closed. However, the courtyard was open* gives the two main clauses clear boundaries. A semicolon can also work before *however*. A comma alone generally will not carry the boundary in that example. Short balanced sequences such as *Some stayed, some left* belong to a different punctuation pattern.

### Concept: Set off additions while keeping the main structure intact
*Mara, please check the side entrance* has a vocative. *The side entrance, as you may recall, was locked* has a parenthetical comment with an opening and a closing comma. A left dislocation can also be set off, as in *That old door, it never closes properly*. Now try *The side entrance near the hall, was locked*. There is no added comment to delimit. The comma interrupts the ordinary subject–predicate connection.

If you use parentheses for a modifier, say the words inside them aloud too. Write *an (unusually detailed) manual*, because *unusually* begins with a vowel sound, and *a (brief) interruption*, because *brief* begins with a consonant sound. Article choice is an exception to the ordinary independence of parenthesised material. In *Mara (and Jo) was informed*, the verb agrees with *Mara*. If both names are to control agreement, write *Mara and Jo were informed*.

### Concept: Give each quotation mark and terminal a job
In the article’s direct speech, *Mara asked, “Is the hall open?”* uses a comma after the reporting phrase in this conventional frame. The quoted question mark can serve at the end without an extra full stop. When a quote is a statement and the report continues, its terminal full stop is ordinarily dropped. In *Mara said, “The hall is closed” and locked the gate*, the sentence ends at *gate*. An internal question mark can survive in the corresponding question quote. For nested speech, use the complementary quotation marks inside, following the publication’s order for outer and inner marks.

A line ending *The venue is in Washington, D.C.* uses the abbreviation’s last full stop as the visible sentence ending. If the whole line asks a question, *Is the venue in Washington, D.C.?* keeps both the abbreviation and the question mark. With directional typography the apostrophe marking a missing letter has the same shape as a closing single quote, as in *rock ’n’ roll*. That apostrophe has a different purpose from a genitive apostrophe. *The hall’s door* has one, whereas possessive *its* does not. Hyphens also reflect internal word structure. You can see the compounds from the previous lesson in *twenty-one* and *a two-day closure*. The house may also use a hyphen in a fraction like *two-thirds*.

### Contrast: The same question at different levels
- *Mara asked whether the hall was open.* The whole sentence reports her question.
- *Mara asked, “Is the hall open?”* The question mark belongs to her quoted words.

### Application
- example: The copy reads, “Mara asked if the gate was open? The gate beside the hall, was shut, however, the courtyard was open.”
- **Choose the first terminal** — Decide whether the whole sentence asks or reports.
- **Mark the main-clause boundaries** — Keep the uninterrupted subject together and make the contrast easy to follow.

### Reveal: Check your analysis
*Mara asked if the gate was open. The gate beside the hall was shut. However, the courtyard was open.* A semicolon before *however* is another way to set the boundary between the last two clauses.

### Recap
Read the sentence outside in. Give the whole sentence its terminal, mark the boundaries between clauses, and then give each supplement or quotation the marks that belong to it. Finally check the marks that form part of individual words.

### Self-check
- In “Who asked whether the gate was open?”, why is the question mark appropriate?
- The main clause asks who did the asking. The embedded whether clause lies inside that larger question.

## Teaching blocks
### Teaching block 1
Have the learner read the matrix clause with the quotation temporarily replaced by “this”. Then look inside the quote to determine which terminal belongs to its own sentence.

### Teaching block 2
When commas surround added material, try removing the entire span. The surrounding clause should retain its expected subject and predicate.

## Worked example
- sentence: “Mara,” Jo asked, “is the hall open?”
- origin: Original SynTutor example.
- step: Read the quoted speech as the single question “Mara, is the hall open?”
- step: Keep the comma marking the vocative and set off the reporting interruption according to the quotation style.
- step: Put the question mark at the end of the quoted question, which also ends the matrix sentence.

## Stage checks

#### predict
- prompt: Which main sentence is a question even though both contain “what time the doors open”?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH20-P1733
- hint: Read the outer clause on its own before looking at the embedded question.
- options:
  - id: a
    text: Mara asked what time the doors open.
    feedback: Asked appears in ordinary declarative order here. The embedded question cannot turn the whole line into a direct question.
  - id: b
    text: Did Mara ask what time the doors open?
    feedback: The main clause did Mara ask is interrogative. The embedded question stays the same.
  - id: c
    text: Neither main sentence is a question.
    feedback: The version starting “Did Mara ask” has direct-question inversion in its outer clause.

#### guided
- prompt: Which edit gives two clear independent clauses in ordinary edited prose?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH20-P1742, CGEL-2002-CH20-P1743
- hint: Check whether however joins two complete statements.
- options:
  - id: a
    text: The hall, was shut. However the courtyard, was open.
    feedback: The hall is the subject of was shut and takes no delimiting comma there. Set off however in the second sentence.
  - id: b
    text: The hall was shut, however, the courtyard was open.
    feedback: However does not give a comma extra force. Put a full stop or semicolon at the main clause boundary.
  - id: c
    text: The hall was shut. However, the courtyard was open.
    feedback: Use a sentence boundary before the connective. The comma after however separates it from its clause.

#### transfer
- prompt: Where are the commas needed in “The side gate as you know was locked”?
- answer: c
- outcome_ids: o2
- source_ids: CGEL-2002-CH20-P1744, CGEL-2002-CH20-P1745
- hint: Try removing the whole interposed comment, then put it back.
- options:
  - id: a
    text: Only after gate
    feedback: A lone opening comma would leave the end of the interruption unmarked.
  - id: b
    text: Only before was
    feedback: A lone closing comma would leave the start of the interruption unmarked.
  - id: c
    text: Around as you know
    feedback: The added comment is enclosed on both sides. The base clause is The side gate was locked.

#### exit
- prompt: Complete the direct question “Did she say the venue was in Washington, ___”
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH20-P1754, CGEL-2002-CH20-P1755, CGEL-2002-CH20-P1764
- hint: The city abbreviation has its own punctuation. What is the whole sentence doing?
- options:
  - id: a
    text: D.C.
    feedback: That is enough for a statement about the city. The larger question still needs its question mark.
  - id: b
    text: D.C.?
    feedback: The abbreviation retains its stop, and the whole question has its own question mark.
  - id: c
    text: D.C..
    feedback: The whole line asks a question. Use a question mark after the abbreviation’s stop.

## Revised assessment
- required_sections: introduction, concepts, worked-example, application, recap

### Opening questions

#### opening-1
- prompt: Choose the ending for the report “Mara asked whether the hall was open___”
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH20-P1733
- options:
  - id: a
    text: a question mark
    feedback: The main clause reports a question. The sentence as a whole is a statement.
  - id: b
    text: a full stop
    feedback: The main clause reports a question. The sentence as a whole is a statement.
  - id: c
    text: a semicolon
    feedback: The main clause reports a question. The sentence as a whole is a statement.

#### opening-2
- prompt: Which line uses a comma for direct address?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH20-P1745
- options:
  - id: a
    text: Mara, check the side gate.
    feedback: Mara is the person addressed in the command. The other commas interrupt ordinary connections.
  - id: b
    text: Mara checked, the gate.
    feedback: Mara is the person addressed in the command. The other commas interrupt ordinary connections.
  - id: c
    text: The gate near Mara, is closed.
    feedback: Mara is the person addressed in the command. The other commas interrupt ordinary connections.

#### opening-3
- prompt: How many consecutive full stops follow the final C in the statement “The office is in Washington, D.C.”?
- answer: c
- outcome_ids: o3
- source_ids: CGEL-2002-CH20-P1763, CGEL-2002-CH20-P1764
- options:
  - id: a
    text: Two
    feedback: The abbreviation’s final full stop also supplies the visible end of the statement.
  - id: b
    text: Zero
    feedback: The abbreviation’s final full stop also supplies the visible end of the statement.
  - id: c
    text: One
    feedback: The abbreviation’s final full stop also supplies the visible end of the statement.

#### opening-4
- prompt: Which line uses a colon to introduce an explanation?
- answer: b
- outcome_ids: o1
- source_ids: CGEL-2002-CH20-P1737, CGEL-2002-CH20-P1738, CGEL-2002-CH20-P1739
- options:
  - id: a
    text: The hall: by the old entrance was closed.
    feedback: The second clause explains the closure. A coordinate list of clauses needs a different boundary pattern.
  - id: b
    text: The hall was closed: the caretaker had gone home.
    feedback: The second clause explains the closure. A coordinate list of clauses needs a different boundary pattern.
  - id: c
    text: The hall opened at nine: the clinic opened at ten: the store opened at eleven.
    feedback: The second clause explains the closure. A coordinate list of clauses needs a different boundary pattern.

#### opening-5
- prompt: Which sentence sets off the interruption while keeping the subject with its predicate?
- answer: b
- outcome_ids: o2
- source_ids: CGEL-2002-CH20-P1744, CGEL-2002-CH20-P1745
- options:
  - id: a
    text: The gate, as you may recall was locked.
    feedback: Paired commas enclose the parenthetical material. A long subject alone needs no comma before was.
  - id: b
    text: The gate, as you may recall, was locked.
    feedback: Paired commas enclose the parenthetical material. A long subject alone needs no comma before was.
  - id: c
    text: The gate near the hall, was locked.
    feedback: Paired commas enclose the parenthetical material. A long subject alone needs no comma before was.

### Closing questions

#### closing-1
- prompt: Which directional apostrophe indicates the missing letters before n in rock ’n’ roll?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH20-P1725
- options:
  - id: a
    text: ’
    feedback: The omission mark has the shape of a closing single quotation mark.
  - id: b
    text: “
    feedback: The omission mark has the shape of a closing single quotation mark.
  - id: c
    text: ‘
    feedback: The omission mark has the shape of a closing single quotation mark.

#### closing-2
- prompt: Which article fits before “(unusually detailed) manual” when the whole phrase is read aloud?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH20-P1748
- options:
  - id: a
    text: an
    feedback: Read the parenthesised words too. Unusually immediately follows the article in speech and begins with a vowel sound.
  - id: b
    text: a
    feedback: Read the parenthesised words too. Unusually immediately follows the article in speech and begins with a vowel sound.
  - id: c
    text: No article is possible.
    feedback: Read the parenthesised words too. Unusually immediately follows the article in speech and begins with a vowel sound.

#### closing-3
- prompt: Which version avoids a quoted full stop inside a continuing sentence?
- answer: b
- outcome_ids: o3
- source_ids: CGEL-2002-CH20-P1753, CGEL-2002-CH20-P1754, CGEL-2002-CH20-P1755
- options:
  - id: a
    text: Mara said, “The hall is closed.” And turned the key.
    feedback: The matrix sentence continues after the quotation, so the quoted full stop is dropped there.
  - id: b
    text: Mara said, “The hall is closed” and turned the key.
    feedback: The matrix sentence continues after the quotation, so the quoted full stop is dropped there.
  - id: c
    text: Mara said, “The hall is closed.” and turned the key.
    feedback: The matrix sentence continues after the quotation, so the quoted full stop is dropped there.

#### closing-4
- prompt: A quoted question ends the report “Mara asked, ‘Is the hall open?’” What follows the closing quotation mark?
- answer: a
- outcome_ids: o2
- source_ids: CGEL-2002-CH20-P1753, CGEL-2002-CH20-P1754, CGEL-2002-CH20-P1755
- options:
  - id: a
    text: Nothing more
    feedback: The internal question mark is retained and the external full stop is suppressed.
  - id: b
    text: An additional full stop
    feedback: The internal question mark is retained and the external full stop is suppressed.
  - id: c
    text: A second question mark
    feedback: The internal question mark is retained and the external full stop is suppressed.

#### closing-5
- prompt: Which pair uses the usual word punctuation in both phrases?
- answer: a
- outcome_ids: o3
- source_ids: CGEL-2002-CH20-P1761, CGEL-2002-CH20-P1763
- options:
  - id: a
    text: the hall’s door / a two-day closure
    feedback: The genitive takes an apostrophe and the pre-head measure compound takes a hyphen with singular day.
  - id: b
    text: the hall’s door / a two-days closure
    feedback: The genitive takes an apostrophe and the pre-head measure compound takes a hyphen with singular day.
  - id: c
    text: the halls door / a two day closure
    feedback: The genitive takes an apostrophe and the pre-head measure compound takes a hyphen with singular day.
