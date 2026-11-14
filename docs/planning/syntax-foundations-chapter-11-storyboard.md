# Chapter 11 proposal · Languages, sentences and grammars

**Status** · Implemented as a [local pilot](../reports/syntax-foundations-chapter-11-pilot.md). Gate 4.11 review and first-time learner timing are pending.

## Source and scope

Noel Burton-Roberts, *Analysing Sentences*, third edition, Pearson, 2011, ISBN 9781408233740. Read printed pp. 254–268 (PDF pp. 269–283). Visually checked the coordination diagrams on p. 260 and phrase marker [12] on p. 266. Keep the current “Iris rests” and “Leo waits” examples and extend the activity to connect the rules with structural descriptions.

| Book section | Teaching decision |
| --- | --- |
| Languages, pp. 254–257 | Present a set of sentences as one way to study a language. Acknowledge that speakers’ patterns can vary across English varieties. Defer historical examples and dialect classification. |
| Describing languages, pp. 257–259 | Show how a complete list can specify a deliberately tiny language. Add a repeatable operation so learners can see why a longer list cannot exhaust the expanded system. Distinguish possible sentences from the finite set someone has actually heard. |
| Describing infinite languages, pp. 259–262, p. 260 diagrams | Use a short base list and a rule that joins two S units with “and”. Reuse a result as one input. Show its grouping at each application. The book also illustrates flat coordination of more than two inputs. This activity isolates the binary recursive case. Defer the historical comparison of theories of language. |
| Grammars, pp. 262–265 | Define a grammar as a system of rules specifying which sequences count as sentences and assigning them structural descriptions. Introduce implicit knowledge through a novel example that learners can judge. Defer an account of mental grammar and acquisition. |
| Grammars and sentence analysis, pp. 265–268, [11–12] | Contrast drawing a phrase marker for a sequence with giving a rule that licenses its order. Use a small NP–VP rule set to explain one permitted sequence and one reversed sequence. Explain “generative grammar” in this sense. Defer competing formal systems and any claim that the exercise describes the whole of English. |

## Outcomes and learner flow

1. Explain how a finite base and recursive rule can describe an unbounded set of sentences.
2. Apply the toy rule to new inputs, recover the resulting grouping, and explain why an unfinished input fails.
3. Distinguish describing a sentence’s structure from specifying rules that license it, and explain the two jobs a grammar performs.

| Page | Learner action | Budget |
| --- | --- | ---: |
| Introduction and opening check | Start with the bracketed combination “[Iris rests] and [Leo waits]”. Define grammar and preview what the rule can explain. Put general key terms below the preview bullets and give five diagnostic items. | 1:45 |
| Compare a list with a rule | Limit a toy language to “Iris rests”, “Leo waits”, and “Mina waves”. Ask whether the combined example belongs to that list. Add a rule that combines two sentences into a sentence, then explain why the result can be combined again. | 1:10 |
| Trace two applications | Show S above the two input S units and “and”, first for “Iris rests and Leo waits”, then for “Iris rests and Leo waits and Mina waves”. Trace the earlier result as a constituent of the larger derivation. | 1:15 |
| Apply the rule | Reuse the two-input activity. Try a complete pair and the unfinished “Iris rests and”. Reuse the first result and preserve its labelled grouping. Give feedback explaining which input fails and what the learner can change. | 1:20 |
| Explain what the rules license | Compare “The dog waits” with “Waits the dog” as candidate neutral statements in the toy grammar. Use S → NP VP, NP → DET N, VP → V and a tiny lexicon. Point out which derivation fails and explain why the ability to draw a diagram does not establish membership. | 1:15 |
| Transfer | Ask whether “Mina waves and Leo waits” can be derived even though it is absent from the base list. Reveal the two inputs, rule, and grouping. Relate the judgement to speakers’ ability to interpret a new sentence. | 0:50 |
| Recap and references | Separate list membership, rule application and structural description. Use one sentence to define what a generative grammar does. Keep book and figure references in the recap dropdown. | 0:35 |
| Closing check | Five fresh items with option-specific feedback, last and best scores, and retake XP. | 1:20 |

**Estimated total 9 min 30 sec.** First-time learner timing is pending. If it exceeds ten minutes, shorten the list-membership comparison and keep the recursive step and the explanation of the failed derivation.

## Activity and notation plan

- Declare the coordination rule as `S → S and S`, with the three listed base sentences also licensed as S. Give the result the category S. For the selected derivation, show `[S [S [S Iris rests] and [S Leo waits]] and [S Mina waves]]`. Explain that the brackets record this derivation, and that the same words can be grouped in other ways. Treat this as an authored diagram of a toy grammar.
- The existing input activity supports one reuse and provides the appropriate two-step interaction. During implementation, verify that the accepted result can be reused, that its grouping stays visible, and that missing and unfinished inputs give distinct feedback. Keep structural labels on the worked trace. Use the existing activity or extend it narrowly if needed. A standalone Builder is unnecessary.
- In the word-order example, use a separate toy grammar with lexicon `DET → the`, `N → dog`, and `V → waits`. The whole order follows from S → NP VP. Make clear that the rule set licenses this neutral statement pattern and gives no verdict about English constructions outside the exercise.
- Preserve the normal six section IDs and give the added rule and syntax pages their own IDs. Test keyboard input, visible feedback, 390 px fit, stable routes, resume, score-only opening results, closing review and positive-only XP on an improved retake.

## Draft checks

| Item | Prompt | Answer and feedback focus |
| --- | --- | --- |
| Opening 1 | If the complete list is “Iris rests” and “Leo waits”, does “Iris rests and Leo waits” belong to it? | **No.** It is absent from the complete list. |
| Opening 2 | If “and” joins two complete inputs, which input is unfinished: “Mina waves” or “Iris rests and”? | **Iris rests and.** The second sentence after “and” is missing. |
| Opening 3 | What can the output of a sentence-combination rule become? | **An input to the same rule.** The output is itself a sentence. |
| Opening 4 | In “[Iris rests and Leo waits] and [Mina waves]”, what is the first input to the last step? | **Iris rests and Leo waits.** The brackets group the earlier result. |
| Opening 5 | What does a labelled tree tell the reader? | **How a sequence is grouped.** Branches describe the parts and their relationships. |
| Closing 1 | A toy grammar lists “Ren reads” and “Ivo sings” and permits S → S and S. What licenses “Ren reads and Ivo sings and Ren reads”? | **Apply the rule to two base sentences, then join the result with another base sentence.** The result remains S at each step. |
| Closing 2 | Why does the same toy rule fail for the input “Ivo sings and”? | **It lacks a complete second sentence.** The rule needs two S inputs. |
| Closing 3 | Which grouping records combining “Ren reads” with “Ivo sings and Nia listens” as the two final inputs? | **[Ren reads] and [Ivo sings and Nia listens].** The second input preserves the earlier combination. |
| Closing 4 | The toy grammar uses S → NP VP and licenses “The bird sings”. Why does the same rule fail for “Sings the bird”? | **The VP comes before the NP.** The rule specifies their order as well as their categories. |
| Closing 5 | What must the toy grammar supply in addition to a decision about whether it licenses a sequence? | **A structural description of a licensed sequence.** The rules state which combinations are permitted and how they are grouped. |

Opening items map to outcomes 1, 2, 1, 2 and 3. Closing items map to 1, 2, 2, 3 and 3. Finalize distractors with cited feedback. Record the walkthrough and source receipt at Gate 4.11. The immutable seed and whole-course release checks belong to Phase 5.
