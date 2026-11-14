# Chapter 10 proposal · Non-finite clauses

**Status** · Outline ready for owner review. Chapter 10 implementation follows outline approval.

## Source and scope

Noel Burton-Roberts, *Analysing Sentences*, third edition, Pearson, 2011, ISBN 9781408233740. Read printed pp. 224–253 (PDF pp. 239–268). Visually checked [6], [11–12], [17], [14a], [21–22], [101b–102b], and Discussions 1–2. The published lesson works through a to-infinitive VP fragment. Keep that repair and place it within the book’s broader account of non-finite clauses.

| Book section | Teaching decision |
| --- | --- |
| Overt, free and controlled subjects, pp. 224–225, [1–3] | Distinguish an overt subject from a silent one. Show a free silent subject with no specific controller and a controlled silent subject with a matching index. |
| Four forms, pp. 225–229, [4–25] | Compare bare infinitive, to-infinitive, passive participle, and -ing participle. Trace where [-tense] appears. Use a stative -ing example to distinguish the form from a finite progressive. Defer stacked auxiliary passives and their multiple gaps. |
| Complementisers, pp. 229–232, [26–39] | Compare overt “for” with “whether” and “what” in infinitival clauses. Reuse C1 and C2 from Chapter 9. Point out that an overt infinitival subject can occur with unfilled C1. Defer the full infinitival-relative derivation. |
| Clause functions, pp. 232–236, [40–65] | Contrast a clause as subject, a complement to a preposition, and an adverbial of purpose. Give brief examples of complements to A and N and a participial modifier in NP. Defer detailed extraposition restrictions and mixed NP structures. |
| Complement of V, pp. 236–243, [66–102] | Compare “expected” and “persuaded” with the same following words. Find the overt lower subject in Type I and the higher object controlling a silent lower subject in Type II. Use expletive “there” as an optional check. Mention subject control with “promise” in a short note. Defer disputed verb classifications and the full list of complement patterns. |
| Discussion and exercises, pp. 244–253 | Use Discussions 1–2 for the overt and free subject analyses. Use one transfer comparing Type I and II. Defer the long mixed derivations. |

## Outcomes and learner flow

1. Distinguish the four non-finite forms and locate the tense feature in each example.
2. Locate overt and covert subjects, identify a controller when present, and read the relevant C position.
3. Recognize the function of an embedded non-finite clause and distinguish the Type I and Type II structures.

| Page | Learner action | Budget |
| --- | --- | ---: |
| Introduction and opening check | Compare “Nora plans [to inspect the bridge]” and “Nora planned [to inspect the bridge]”. Define finite and non-finite in prose, then show the preview bullets, key terms and five diagnostic items. | 1:40 |
| Identify the four forms | Compare “The crew made Ivo wait”, “Nora planned to inspect the bridge”, “With the lamps packed, the crew left” and “Knowing the route helps”. Use short bracketed examples, with the tense marker shown on the relevant verb or auxiliary. | 1:10 |
| Trace and repair the infinitival VP | Reuse the canonical “to inspect the bridge” fragment. Trace “to” and its lexical VP, then attach the detached VP under the higher VP. Contrast infinitival “to” with “to the bridge”. | 1:15 |
| Find the subject and its controller | Compare “Knowing the route helps”, “Nia enjoys checking the maps”, and “Nia enjoys Ivo checking the maps”. Trace the free subject, matched controller and overt subject. Use “For Ivo to wait outside seemed unfair”, “Nia wondered whether to wait”, and “Nia knew what to pack” to locate C1 and C2. | 1:25 |
| Ask what job the clause does | Compare “[Checking the ropes] takes time”, “Nia insisted on [checking the ropes]” and “Nia paused [to check the ropes]”. Identify subject, complement of P and purpose adverbial. Briefly show “eager to help”, “a request to speak”, and “the crates stacked by the door”. | 1:00 |
| Compare Type I and Type II | Switch between “They expected Ivo to wait” and “They persuaded Ivo to wait”. Ask which clause contains the overt NP, give targeted feedback, and trace the silent subject and controller in Type II. | 1:15 |
| Transfer | Use “Nia expected Ren to leave” and “Nia advised Ren to leave”. Ask who leaves and which clause contains the overt NP. Reveal both structures in brackets. | 0:35 |
| Recap and references | Find the untensed form, locate its subject, then identify the clause’s function. Keep the book and figure references in the recap dropdown. | 0:25 |
| Closing check | Five fresh items with option-specific feedback, last and best scores, and retake XP. | 1:10 |

**Estimated total 9 min 55 sec.** The first-time learner trial is pending. If it exceeds ten minutes, move the optional expletive test and secondary host examples into disclosures. Keep all four forms and the Type I and II comparison in the core sequence.

## V10 analyses and implementation checks

- Figures [6], [11], [17] and [21–22] place [-tense] on the bare infinitival V, the feature-only branch over infinitival “to”, the passive participle V, and the initial -ing verb respectively. The last can be lexical or auxiliary. In the “with” example, “packed” is the passive participle. For a passive gap demonstration, use the verified pattern [14a] and show where the object would be in the corresponding active clause.
- In the worked fragment, “to” and the lexical VP share the higher VP. Keep the stored AUX category for Builder checks and show only [-tense] on that branch in the learner diagram. The fragment is a VP within the larger clause.
- For “Nia enjoys checking the maps”, match the index on the overt NP “Nia” and the dot under the embedded subject NP. In “Knowing the route helps”, the silent subject is free and the dot has no matching index. “Ivo” occupies the embedded subject position in the third example. Explain that the dot can represent an understood subject as well as the position left by movement.
- Use “for” and “whether” under C1. In “what to pack”, “what” is under C2, C1 is unfilled, and S includes a silent subject and an object gap. A clause following the preposition “on” sits directly under PP as S, using the chapter’s preposition exception.
- Type I [101b] has V(I) beside a single S′ complement. The overt NP “Ivo” is inside the lower S. Type II [102b] has V(II) beside the object NP and S′. The object NP and the silent lower subject share an index. The number itself is arbitrary. Learners need to see it at both positions in the canvas and accessible outline.
- Reuse the existing fragment repair and separate preview drafts from published progress. Check a detached branch and repaired branch, the feature-only auxiliary label, both ends of the index, and mobile fit of the deep Type II tree.

## Draft checks

| Item | Prompt | Answer and feedback focus |
| --- | --- | --- |
| Opening 1 | Which verb carries past tense in “Nora planned to inspect the bridge”? | **planned.** The infinitival group stays the same in the present-tense counterpart. |
| Opening 2 | In “The crew made Ivo wait”, what form is “wait”? | **Bare infinitive.** It has the stem form without “to”. |
| Opening 3 | Who is understood to check the maps in “Nia enjoys checking the maps”? | **Nia.** The main subject controls the silent lower subject. |
| Opening 4 | In “For Ivo to wait outside seemed unfair”, who is the overt subject of “to wait”? | **Ivo.** “For” introduces the clause and the NP supplies its subject. |
| Opening 5 | Why did Nia pause in “Nia paused to check the ropes”? | **To check the ropes.** The clause gives the purpose of pausing. |
| Closing 1 | In “All Ren did was tighten the bolts”, where does [-tense] appear in the bare infinitival VP? | **On V “tighten”.** There is no infinitival “to” branch. |
| Closing 2 | In “Mina agreed to count the crates”, where does [-tense] appear in the infinitival VP? | **On the branch above “to”.** “Count the crates” is its VP complement. |
| Closing 3 | In “Reading maps takes practice”, what does the silent subject of “reading” refer to? | **People in general.** No overt constituent in the main clause controls it. |
| Closing 4 | Compare “They expected Lea to sing” and “They persuaded Lea to sing”. In which example is “Lea” the overt subject inside the infinitival clause? | **The first.** In the second, “Lea” is the higher object and controls the silent lower subject. |
| Closing 5 | In “Mina insisted on locking the gate”, what is the function of “locking the gate”? | **Complement of “on” inside PP.** The -ing clause is the group selected by the preposition. |

Opening items map to outcomes 1, 1, 2, 2 and 3. Closing items map to 1, 1, 2, 3 and 3. Finalize distractor feedback with the printed anchors. Record the assessment, draft recovery, and retake evidence at Gate 4.10. The immutable assessment seed belongs to release preparation.
