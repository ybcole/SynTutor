# Chapter 8 proposal · Sentences within sentences

**Status** · Implemented as a [local pilot](../reports/syntax-foundations-chapter-8-pilot.md). Gate 4.8 review is pending. First-time learner timing remains pending.

## Source and scope

Noel Burton-Roberts, *Analysing Sentences*, third edition, Pearson, 2011, ISBN 9781408233740. Reviewed printed pp. 171–195 (PDF pp. 186–210). Visually checked [11a–b], [15], [23], [36], [54], [61], [67c] and [71]. The current lesson teaches an overt “that” clause and already has a repair for C beside S under S′. Keep that repair, then teach where the completed group attaches.

| Book section | Teaching decision |
| --- | --- |
| Clausal recursion and abbreviated clausal analysis, pp. 171–174, [1–4], [9–10] | Contrast a clause embedded inside another with two clauses joined by “and”. Trace one three-clause example with labelled brackets. Defer the full phrase markers for multiply embedded sentences. |
| Complementisers, pp. 174–176, [11a–b], [14–17] | Compare overt “that”, unfilled C, and “whether” introducing an embedded yes/no question. Connect the contrast to Chapter 6’s fronted auxiliary. Use a reporting verb that permits omission of “that”. Defer distribution of interrogative “if”. |
| Clausal subject and extraposition, pp. 176–178, [20–24] | Compare a subject NP containing S′ with its extraposed counterpart, where dummy “it” fills the subject slot and S′ attaches directly under the main S. Defer verbs that only permit the extraposed pattern. |
| Complement of V, pp. 179–181, [32–41] | Show NP above S′ for a clausal direct object in the selected reporting example. Contrast that with S′ directly under the predicate VP in a copular subject-predicative example. Defer verb-by-verb selection and passive diagnostics. |
| Complements of A and N, pp. 181–184, [43–49], [53–54] | Show S′ beside A inside AP and beside N inside NOM. Choose contexts that keep the noun-complement reading distinct from extraposition. |
| Complement of P and adverbial clauses, pp. 184–187, [60–71], [76–84] | Compare P + S′ with “whether”, P + S with temporal “after”, and a reason clause headed by C “because”. Attach the reason clause beside the basic VP in a clear event reading. Mention whole-sentence adverbials as a scope extension. Defer the temporal/causal ambiguity of “since” and phrasal complementisers. |
| Discussion and exercises, pp. 188–195 | Use a short transfer on nested clause spans and new assessment examples. Defer mixed full-tree derivations. |

## Outcomes and learner flow

1. Find the main clause and the complete spans of its embedded clauses. Distinguish nesting from coordination.
2. Read C and S under S′ with overt “that”, unfilled C or interrogative “whether”.
3. Use the host and the role of the clause to choose its attachment, including the contrast between clausal subjects, complements and adverbials.

| Page | Learner action | Budget |
| --- | --- | ---: |
| Introduction and opening check | Define main clause and embedded clause around “Leo says [that Nora is inspecting the bridge]”. Place the general key terms after the preview bullets, then give five diagnostic items. | 1:45 |
| Find the clause within the clause | Compare “Leo says that Nora is inspecting the bridge” with “Leo spoke and Nora inspected the bridge”. Trace the three lexical verbs in “Maya thinks [Leo said [Nora closed the gate]]”, with each embedded span centred and introduced before it is analysed. | 1:00 |
| Read C and S | Reuse the existing C branch repair for Leo’s report. Compare “Leo says Nora is inspecting the bridge” and “Leo asked whether Nora was inspecting the bridge”. Locate the unfilled C and compare embedded subject-before-auxiliary order with “Was Nora inspecting the bridge?” | 1:30 |
| Follow the clause as subject or object | Switch between “That the latch jammed surprised Mina” and “It surprised Mina that the latch jammed”. Then locate the object NP containing S′ in “Mina noticed that the latch jammed”. Use one cue per tree. | 1:10 |
| Find the head the clause completes | Compare “certain that the latch jammed”, “the claim that the latch jammed”, and “about whether the latch jammed”. Trace A, N and P beside their complements. Give one short copular example in prose. | 0:55 |
| Distinguish two ways to add a clause | Compare “Mina waited after the gate closed” with “Mina waited because the gate jammed”. Use a two-choice attachment exercise and feedback. Trace the PP in the first and the adverbial S′ in the second. | 1:05 |
| Transfer | In “Ria heard that Ivo wondered whether the hall was open”, choose where both embedded spans start before revealing the complete bracketed answer. | 0:45 |
| Recap and references | Find the clause boundary, then check the introductory word and the host. Revisit one contrast where the same clause changes role. Put book and figure references in the recap dropdown. | 0:25 |
| Closing check | Five new items with option-specific feedback, last and best scores, and retakes. | 1:20 |

**Estimated total 9 min 55 sec.** If a learner trial exceeds ten minutes, shorten the full subject and extraposition traces and move the copular example to a short disclosure. Keep the C contrast, subject and object distinction, and PP versus adverbial comparison in the core lesson.

## Expected V8 analyses and implementation checks

- In “Leo says that Nora is inspecting the bridge”, the inner S starts at “Nora”. S′ includes C “that” and S. The local repair operates on this fragment. A whole-sentence object tree adds NP over S′ under VP, following [36].
- In “Leo says Nora is inspecting the bridge”, display a leafless C beside S, as in [15]. It contributes no word and differs from the movement gap in Chapter 6. Verify both the SVG and accessible outline. Add a concise caption to the empty branch.
- “Whether Nora was inspecting the bridge” has overt C and embedded S with subject-before-auxiliary order. The contrasting standalone question uses the fronted-auxiliary pattern introduced in Chapter 6.
- “That the latch jammed surprised Mina” has subject NP over S′. In the extraposed version, the subject NP contains dummy “it”, and extraposed S′ is a daughter of main S beside subject NP and VP. Keep the entire S′ in that third branch, following [24].
- In “certain that the latch jammed”, S′ is a sister of A within AP. In “the claim that the latch jammed”, S′ is a sister of N within NOM. In “about whether the latch jammed”, S′ is a sister of P within PP. A copular subject predicative such as “whether the latch jammed” in “The question is whether the latch jammed” can be S′ directly, following [41].
- Temporal “after” takes a bare S under PP in this analysis, following [67c]. In the reason example, C “because” and its S form an adverbial S′, which joins the basic VP under a higher VP, following [71] and Discussion 7.
- Reuse the existing fragment and Builder checker for C beside S. The inner S is collapsed to a triangle in that draft, so test a detached C and a valid attachment. Use authored read-only trees for extraposition and the P/S contrast. Verify numbered buttons visibly change the tree or focus, and confirm that direct routes, resume, and the published lesson still work.

## Draft checks

| Item | Prompt | Answer and feedback focus |
| --- | --- | --- |
| Opening 1 | In “Mina says that the gate jammed”, which group gives the content of her report? | **that the gate jammed.** Include the word that introduces the report. |
| Opening 2 | In “Ari wondered whether the hall was open”, what introduces the embedded question? | **whether.** The subject inside the embedded clause is “the hall”. |
| Opening 3 | In “That the lights went out surprised Ren”, what surprised Ren? | **That the lights went out.** The whole clause supplies the subject. |
| Opening 4 | What does “that the ferry was late” supply in “the claim that the ferry was late”? | **The content of the claim.** It completes the noun “claim”. |
| Opening 5 | In “The crew stopped because the rope snapped”, which group gives the reason for stopping? | **because the rope snapped.** The group explains the whole stopping event. |
| Closing 1 | In “Ren thinks Ivo knows the bell rang”, which is the most deeply embedded clause? | **the bell rang.** It is inside what Ivo knows, which is inside what Ren thinks. |
| Closing 2 | In “Ria heard the ferry had left”, what appears under C in the embedded clause tree? | **No word.** C is unfilled, and the inner S begins at “the ferry”. |
| Closing 3 | In “Ivo asked whether the door was locked”, what order belongs inside the embedded S? | **the door was locked.** “Whether” already occupies C. |
| Closing 4 | In “It bothered Nia that the lamp flickered”, where does the extraposed S′ attach in this analysis? | **Directly under the main S.** Dummy “it” fills the subject slot. |
| Closing 5 | In “Ren stayed after the rain stopped”, what does temporal “after” take as its complement? | **The S “the rain stopped”.** The preposition and bare S form a PP. |

Opening items map to outcomes 1, 2, 3, 3 and 3. Closing items map to 1, 2, 2, 3 and 3. Finalize distractors with a cited answer key and verify the opening score, closing feedback, draft recovery and retake XP at Gate 4.8. Create the matching immutable seed during release preparation.
