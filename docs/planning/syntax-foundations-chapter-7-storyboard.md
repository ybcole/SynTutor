# Chapter 7 proposal · The structure of Noun Phrases

**Status** · Outline for owner review. Chapter 6 walkthrough and Chapter 7 outline approval precede Chapter 7 implementation.

## Source and scope

Noel Burton-Roberts, *Analysing Sentences*, third edition, Pearson, 2011, ISBN 9781408233740. Reviewed printed pp. 141–170 (PDF pp. 156–185). Visually checked [1–7], [10], [18], [36], [39a], [A–B] and [72a–b]. The current lesson shows a demonstrative and a noun. Keep that example and use it to explain what changes when the phrase gains a determiner, modifier or larger nominal.

| Book section | Teaching decision |
| --- | --- |
| Basic NP, pp. 141–142, [1–4] | Compare a one-word name or pronoun with an NP that divides into DET and NOM. Define NOM as the layer between NP and the noun, containing the noun and its modifiers. |
| Determiners, pp. 142–144, [5–7], [10], [12], [14] | Compare articles, demonstratives, simple quantifiers and possessives in the same slot. Show empty DET with a bare plural or mass noun. Mention that an NP plus genitive *-s* can fill the possessive slot. Defer recursive possessives. |
| Pre-determiners, pp. 145–146, [15–20] | Use “all those baskets” to show that PRE-DET joins a whole NP. Its coexistence with “those” shows that it occupies a separate position. |
| Pre-modifiers, pp. 146–149, [25–28], [32], [36] | Trace successive APs under successive NOM layers. Give short recognition examples of a numeral under QA, a participle phrase, and a noun compound under N. Defer their finer diagnostics. |
| Post-modifiers, pp. 150–155, [39a–b], [A–B], [65–67] | Show a PP after the noun and compare attachments when a phrase also contains a pre-modifier. Mention an AP with its own complement as a post-modifier. Defer ambiguous PP stacks and the detailed treatment of complements in NOM. |
| Modification of pronouns, pp. 155–156, [72–75] | Compare a plain pronoun NP with “someone from the village”. Show pronoun and PP as sisters under NP for that indefinite pronoun. Defer the elliptical-head analysis of partitives. |
| Exercises and appendix, pp. 157–170 | Use a fresh modifier-scope comparison. Defer the appendix’s pro-NOM *one* test and its optional refinement of the main chapter’s analysis. |

## Outcomes and learner flow

1. Build the basic DET–NOM split and distinguish overt DET, empty DET, and an NP headed by a plain name or pronoun.
2. Locate a pre-determiner and trace where pre- and post-modifiers attach.
3. Explain how a modifier’s interpretation determines its attachment, and recognize the separate pattern for a modified indefinite pronoun.

| Page | Learner task | Budget |
| --- | --- | ---: |
| Introduction and opening check | Introduce the example “[those] [baskets]” and define DET, NOM and noun head in prose. Use the preview bullets, general key terms and five diagnostic questions. | 1:45 |
| Find DET and NOM | Compare “those baskets”, “the baskets”, and “baskets”. Trace “those” as DEM under DET and “baskets” as N under NOM. Compare bare “baskets” with “they”. | 1:15 |
| Build the basic NP | Reuse the existing “those baskets” tree repair. Give feedback if NOM is attached below DET. After the repair, trace “all those baskets” to see PRE-DET beside the inner NP. | 1:15 |
| Add modifiers inside NOM | Use “a new red kite” to trace “red kite” before adding “new”. Briefly compare “those two kites”, “the sleeping child” and “the paper kite” for QA, PartP and compound N. | 1:05 |
| Compare modifier attachments | Display “the wooden crates from Cebu”. Read “wooden crates” as a kind of crate, then attach the origin PP to that NOM. Compare “the eager applicant for the job”, where “applicant for the job” is the smaller NOM in the intended reading. Add one short example of an AP with its own complement, “the pilot ready for departure”. | 1:10 |
| Apply the distinction | In “those ceramic bowls from Vigan”, ask what the PP modifies. Give an authored self-check. Compare “someone from Vigan”, where the PP joins the indefinite pronoun under NP. | 1:00 |
| Recap and references | Recap how to find the head, identify the determiner and trace the smallest meaningful nominal first. Put book and figure anchors in the reference dropdown. | 0:35 |
| Closing check | Five new questions, with option-specific feedback, numerical scores, and retakes. | 1:30 |

**Estimated total 9 min 35 sec.** First-time learner timing is pending. Move the QA, participle and compound examples into an optional comparison if timing exceeds ten minutes. Keep both NOM attachment patterns and the empty DET distinction in the core sequence.

## V7 analyses to verify in the pilot

- “Those baskets” is NP with DET → DEM and NOM → N. Bare plural “baskets” still has a DET node with no word. “They” has NP → pronoun. Do not render an empty DET as a movement gap.
- “All those baskets” has NP → PRE-DET + NP. The inner NP retains DET and NOM. The editable example keeps a single target and leaves PRE-DET to the read-only comparison.
- “A new red kite” has NOM → AP + NOM, with the inner NOM → AP + N. “Those two kites” uses AP → QA for “two”. “The sleeping child” uses PartP → V-part for “sleeping”. “Paper kite” is shown as a compound N in its material reading. Before publishing, confirm the precise compound and participle labels against the figures.
- In the intended kind-plus-origin reading of “the wooden crates from Cebu”, the larger NOM branches to NOM “wooden crates” and PP. In the intended reading of “the eager applicant for the job”, the larger NOM branches to AP “eager” and NOM “applicant for the job”. Use context to select the reading and accept a coherent explanation of the chosen attachment.
- “Someone from Vigan” has NP → pronoun + PP, following [72b]. The illustration of a modified indefinite pronoun needs its own tree and caption.

Reuse the versioned Builder draft, numbered traces and page-specific notation. During implementation, verify the leafless DET in the SVG and text outline, and test one wrong attachment, recovery, resume, and both assessment paths.

## Draft checks

| Item | Prompt | Answer and feedback focus |
| --- | --- | --- |
| Opening 1 | Which word names what is being referred to in “those baskets”? | **baskets.** “Those” points out which baskets. |
| Opening 2 | Which phrase puts a word before the determiner “the”? | **both the lanterns.** “Both” can occur before the article. |
| Opening 3 | What does “red” describe in “a new red kite”? | **kite.** It specifies the colour of the kite. |
| Opening 4 | In “the wooden crates from Cebu”, which phrase gives the origin? | **from Cebu.** It supplies the origin of the crates. |
| Opening 5 | Which complete group does “someone” form in “Someone waved”? | **An NP.** The pronoun fills the subject position on its own. |
| Closing 1 | What does the DET branch contain in “lanterns” in “Lanterns glowed”? | **No word.** The bare plural has empty DET and overt NOM. |
| Closing 2 | In “both these notebooks”, what is the sister of PRE-DET? | **The whole NP “these notebooks”.** “These” stays in DET inside that NP. |
| Closing 3 | In “a small blue lantern”, which group forms the inner NOM in the colour-first reading? | **blue lantern.** “Small” modifies that smaller group. |
| Closing 4 | In “the metal boxes from Iloilo”, assuming that “metal boxes” names the kind of box, what does the PP attach beside? | **The NOM “metal boxes”.** The PP adds origin to the kind. |
| Closing 5 | How is “anyone near the entrance” structured in this analysis? | **Pronoun and PP are sisters under NP.** The PP modifies the indefinite pronoun. |

Opening items map to outcomes 1, 2, 2, 3 and 1. Closing items map to 1, 2, 2, 3 and 3. Record the final distractor review, local source receipt and browser evidence at Gate 4.7. The immutable assessment seed belongs to publication.
