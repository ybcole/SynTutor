# Lesson Refinement Master Plan

**Status:** active. Lessons only; quizzes inherit the refined lesson checks later.

## 1. Goal

Turn every lesson chapter into a self-contained, chapter-aware teaching text
that a motivated fifth grader can follow without losing the linguistic terms
they genuinely need.

## 2. Requirements

1. **Every chapter has unique content.** No chapter may reuse another chapter’s
   prose, examples, or recap. Chapter identity is the patterns it teaches.
2. **Comprehensive and chapter-aware.** Each chapter covers every pattern
   assigned to it, in a deliberate order, with examples and contrasts.
3. **Fifth-grader readable.** Short sentences, concrete examples, active voice,
   second person. Keep necessary jargon, but define it the first time it
   appears and use it consistently afterwards.
4. **All key terms indicated.** Every chapter declares its key terms in
   `key_terms`, and each term is defined in one or two natural sentences.
5. **No generic filler.** Generic descriptions are forbidden unless a term
   definition truly requires one. Everything else must be a specific,
   natural-English explanation tied to this chapter’s patterns.
6. **Self-review to perfection.** Every chapter passes the review checklist and
   automated checks before it is marked complete.

## 3. Editorial rules

### 3.1 Voice and readability

- Address the learner directly: “you”, “notice”, “try”, “compare”.
- Keep most sentences under 20 words. Break long ideas into steps.
- Prefer “the verb needs a direct object” over “an object is selected by the
  verb”.
- Explain every technical term the first time it appears, then use it.
- Never write a sentence whose only job is to announce the chapter.

### 3.2 Anti-generic test

A sentence is generic filler if it could be moved to another chapter unchanged.
Generic sentences are removed or replaced with a chapter-specific statement,
example, or instruction.

Allowed exception: a key-term definition may be general when the term itself is
general, e.g. “A **direct object** names the person or thing affected by the
verb.” Each chapter may use at most one such general definition per term.

### 3.3 Examples

- Every concept paragraph contains at least one concrete example.
- Prefer two short examples that contrast: one that works, one that does not.
- Use the chapter’s own examples; do not borrow another chapter’s sentences.
- Keep examples in ordinary, modern English.

### 3.4 Chapter flow

Each chapter follows the same arc:

1. **Introduction** — a real situation or question, then what the learner will
   be able to do by the end.
2. **Key ideas** — two to four subsections, each with an explanation, examples,
   and a contrast.
3. **Worked example** — one sentence or short passage, annotated step by step.
4. **In your own writing** — a short, practical procedure for checking drafts.
5. **Recap** — a compact summary of the chapter’s own patterns and terms.
6. **Checks** — opening and closing questions drawn only from this chapter.

## 4. Key-term policy

- Key terms live in the lesson under `key_terms: [{term, definition}]`.
- Each chapter declares 4–10 terms.
- A term is defined in plain English, then reused in the chapter.
- Key terms must not duplicate a term already defined in a prerequisite
  chapter unless the earlier definition is explicitly recalled.
- The lesson renderer shows the terms in the chapter sidebar.

## 5. Chapter inventory

| Lesson | Track | Rules | Current title | Content state |
|---|---|---:|---|---|
| cgel-ch01 | grammar | 1 | Using words and forms accurately | **done: specific prose, key terms, checks** |
| cgel-ch03 | grammar | 35 | Verb forms and auxiliaries | **done: specific prose, key terms, checks** |
| cgel-ch04 | grammar | 13 | Complementation and valency | **done: specific prose, key terms, checks** |
| cgel-ch05 | grammar | 34 | Nouns and determiners | **done: specific prose, key terms, checks** |
| cgel-ch06 | grammar | 2 | Adjectives and adverbs | **done: specific prose, key terms, checks** |
| cgel-ch07 | grammar | 2 | Prepositions and particles | **done: specific prose, key terms, checks** |
| cgel-ch10 | grammar | 14 | Clause types and questions | **done: specific prose, key terms, checks** |
| cgel-ch13 | grammar | 13 | Comparatives | **done: specific prose, key terms, checks** |
| cgel-ch14 | grammar | 7 | Non-finite clauses | **done: specific prose, key terms, checks** |
| cgel-ch15 | grammar | 4 | Coordination | **done: specific prose, key terms, checks** |
| cgel-ch16 | grammar | 7 | Information packaging | **done: specific prose, key terms, checks** |
| cgel-ch17 | grammar | 30 | Pronouns and pro-forms | **done: specific prose, key terms, checks** |
| cgel-ch18 | grammar | 10 | Morphology and spelling | **done: specific prose, key terms, checks** |
| cgel-ch19 | grammar | 15 | Word formation and inflection | **done: specific prose, key terms, checks** |
| cgel-ch20 | grammar | 17 | Punctuation | **done: specific prose, key terms, checks** |
| br-01 … br-11 | foundations | — | revised foundations lessons | review against this plan |

## 6. Per-chapter content brief

Each chapter refinement records:

- chapter id and title;
- rules covered, in teaching order;
- key terms with definitions;
- section-by-section prose;
- worked example and contrast pair;
- chapter-specific checks;
- self-review notes.

The brief is stored in chapter source and mirrored into the generated pilot.

## 7. Validation

Automated checks must confirm:

- schema validity for `key_terms` and revised assessments;
- every rule id appears in the lesson and in at least one check;
- every key term has a non-empty definition;
- no banned phrasing: “Cambridge”, “book”, “source”, “as mentioned earlier”,
  “this chapter covers”, “in this lesson we will”;
- no generic sentence from the shared filler list;
- sentence length and paragraph length within the readability limits;
- chapter prose is unique across chapters (no duplicate paragraphs);
- chapter checks do not duplicate prompts across chapters;
- all existing lesson and quiz tests still pass.

## 8. Rollout order

1. `cgel-ch04` — pilot refinement and checklist calibration.
2. `cgel-ch01`, `cgel-ch06`, `cgel-ch07`, `cgel-ch14`, `cgel-ch15` — small
   chapters.
3. `cgel-ch10`, `cgel-ch13`, `cgel-ch16`, `cgel-ch18`, `cgel-ch19`,
   `cgel-ch20` — medium chapters.
4. `cgel-ch03`, `cgel-ch05`, `cgel-ch17` — large chapters.
5. Review the `br-01`–`br-11` revised lessons against the same checklist.

## 9. Definition of done

A chapter is done when it passes the schema, rule-coverage, key-term,
uniqueness, readability, banned-phrasing and self-review checks; has been read
end to end by the author; and includes no generic filler outside permitted
term definitions.

## 10. Self-review checklist

- [ ] The introduction names a real situation and an outcome.
- [ ] Every rule in the chapter appears in teaching order.
- [ ] Every key term is defined once and reused.
- [ ] Every concept paragraph has an example or contrast.
- [ ] No sentence could be moved to another chapter unchanged.
- [ ] The worked example is annotated step by step.
- [ ] The recap uses this chapter’s own words.
- [ ] Checks sample this chapter’s patterns only.
- [ ] No banned phrasing.
- [ ] Reads aloud naturally.
