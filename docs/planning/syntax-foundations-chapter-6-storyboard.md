# Chapter 6 proposal · More on verbs — auxiliary VPs

**Status** · Implemented as a [local pilot](../reports/syntax-foundations-chapter-6-pilot.md). Gate 4.6 and learner timing are pending. The implementation adds a brief passive recognition page before negation.

## Source and scope

Noel Burton-Roberts, *Analysing Sentences*, third edition, Pearson, 2011, ISBN 9781408233740. Read printed pp. 111–140 (PDF pp. 126–155) in the reference copy used for the earlier pilots. The chapter draft tree records are already transcribed and source-checked in `web/content/book/ch06.trees.json` (convention `V6`). This outline selects figures and prose from that verified set rather than inventing notation.

Two standing cautions from the source that bound this lesson:

- **Assumption 1 (p.123):** an adverbial placed before a verb modifies the following (higher) VP.
- **Assumption 2 (p.124):** a sentence-final adverbial modifies the lexical VP — **except** certain time adverbials (pp.124–125), which modify a higher tensed auxiliary VP.
- The book calls the interaction of adverbials with auxiliary VPs *“an intricate topic, well beyond the scope of this book”* (p.123). The lesson must present these adverb placements as the book's simplification, not as a general rule.

The current Chapter 4 lesson already introduces the lexical/auxiliary distinction in one sentence and defers auxiliary structure here. Chapter 6 keeps that promise but stays inside the 5–10-minute whole-chapter target, so it teaches the **recursive auxiliary VP** and the **operations that depend on it** (negation, do-support, question fronting) and explicitly defers the passive argument-linking subtleties and the adverbial-assumption exceptions to a documented coverage gap.

| Book section | Teaching decision |
| --- | --- |
| Auxiliaries as heads, tense only on the first verb, pp.111–122, [7–9], [24–25], [29–30], [36–37], [41–42], [52–53b] | Remove the old *Vgrp* idea: each auxiliary heads its own VP and takes a VP complement. Name the four auxiliary types — MOD, PERF, PROG, PASS — from the stored node fragments. Establish the single non-negotiable rule: **the tense feature (pres/past) appears only on the first verb of a sequence**. Use [53b] as the model chain. Defer the participle-form tables ([7], p.120, [26]) to a reference note, not a drill. |
| Recursion and stacking, pp.122–123, [53b], [62] | Show MOD → PERF → V stacking ([53b]) and a two-auxiliary longer chain. Introduce Assumption 1 (adverbial before a verb modifies the following VP) with [62] as the book's own illustration. Label that this is a stated simplification. |
| The lexical VP and sentence-final adverbials, pp.124–125, [66], [69] | Use [66] for Assumption 2 (final adverbial modifies the lexical VP). Use [69] for the documented exception: `last week` modifies the past-tensed PROG VP; `next week` modifies the lexical VP. Keep to one contrast decision; defer full multi-adjunct derivations. |
| Passive VP (recognition only), pp.127–128, [78], [81] | Show PASS as the fourth auxiliary type and that a passive keeps the object's relation via a gap in object position while the verb keeps `[trans]` ([78]). Mention that a `[complex]` passive keeps the object predicative ([81]). **Do not** teach argument-linking rules or the ditransitive-first-object passivisation ([82b]); list them as deferred. |
| Negation, pp.129, [86], [88] | Compare *not/n't* attached to a tensed auxiliary (triangle on the MOD node, [86]) with do-support: an empty `do` under a **TENSE** node carries tense and negation while the lexical V is untensed ([88]). This is the chapter's pivotal operation — give it the worked + practice pages. |
| Question formation, pp.130–132, [91], [93], [103] | Show the tensed auxiliary fronting to C (daughter of S-bar, sister of S) leaving a gap under the auxiliary node ([91]); do-support in a question moves `do` from TENSE to C ([93]); and that *be* always behaves like an auxiliary, so the copula fronts with a gap under V ([103]). One contrast decision per example. |
| Discussion and exercises, pp.133–138 | Reuse the structural comparisons as short original checks. Defer the two-gap question+passives ([94a]/[94b], Disc.6), coordination ([Ex.3(e)]), and the mixed Further Exercises to the documented gap. |

## Outcomes

1. Explain that each auxiliary heads its own VP and takes a VP complement, and name the four auxiliary types (MOD, PERF, PROG, PASS) by their function in the chain.
2. Apply the "tense only on the first verb" rule to a stacked auxiliary sequence.
3. Distinguish negation by *not/n't* on a tensed auxiliary from do-support, and explain how a question fronts the tense-carrying element to C while leaving a gap.

## Page sequence

| Page | Learner task and transition | Budget |
| --- | --- | ---: |
| Introduction and opening check | Revisit “Nora inspected the bridge” from Chapters 4–5. Add “Nora might have inspected the bridge” and ask which word carries the tense. Define auxiliary and the four types (MOD, PERF, PROG, PASS) in prose before the preview bullets; put general key terms below. Show the five-question opening check with a score-only result and no XP. | 1:45 |
| Each auxiliary heads its own VP | Display “You should have written an essay” ([53b]). Switch the read-only tree to show MOD over PERF over the lexical V, and point out that only MOD carries *past*. Ask the learner to click the verb that carries tense. Immediate feedback on the choice. | 1:30 |
| Stack the chain | Trace the numbered levels of [53b], then a longer chain (“You should have been writing that essay”, Disc.2/[56]) to show recursion. One editable repair: reattach a detached higher-VP under the correct auxiliary. | 1:15 |
| Where do the adverbials go? | Compare [62] (adverbial before a verb modifies the following VP) with [66] (final adverbial modifies the lexical VP), and show the [69] time-adverbial exception as a single contrast. Label these as the book's stated simplifications. Unscored short response: which VP does the final phrase modify here? | 1:00 |
| Recognize a passive | Trace the active object, then its passive subject and the gap. Read PASS and the optional agent PP. | 0:35 |
| Negate a clause | Compare “Byron would not dance” ([86]) with “Byron did not dance” ([88]). Define the TENSE node and do-support; show the empty *do* carrying tense and negation. Ask the learner to pick which element carries tense in the second sentence. | 1:00 |
| Ask a question | Compare “Was Byron dancing” ([91]) with “Does Byron dance” ([93]) and “Was Kubla extravagant” ([103]). Trace the fronted element to C and the gap it leaves. One boundary/branch task: mark the fronted auxiliary and its gap. | 1:00 |
| Recap and references | Recap: each auxiliary heads a VP; only the first verb carries tense; negation uses *not/n't* or do-support; questions front the tense-carrier to C and leave a gap. Recall the passive object gap. Defer complex and ditransitive passives and multi-adjunct ordering. Put book/figure anchors in the reference dropdown. | 0:30 |
| Closing check | Five new questions with option-specific feedback, best/last score and incremental XP on improved retakes. | 1:25 |

**Estimated total 10 min, including 35 seconds for passive recognition.** A first-time learner trial is pending. If the trial exceeds ten minutes, make the adverbial-placement page an optional "beyond the core" step and shorten the [62]/[66]/[69] narration, preserving the tense rule, do-support and question fronting as the core sequence. Do not import the passive argument-linking material to save time — it is deferred, not condensed.



## V6 diagram and feedback plan

All trees use the stored `web/content/book/ch06.trees.json` records (convention `V6`). An auxiliary node (MOD/PERF/PROG/PASS) is a display name over a VP whose only child is the auxiliary word; `TENSE` is a display name carrying `do`. The tense feature (`pres`/`past`) appears **only** on the first verb of a sequence. S-bar is printed `S′` in the book and stored as `S-bar`.

| Example | Expected analysis and feedback (source anchor) |
| --- | --- |
| You should have written an essay ([53b], p.122) | MOD (`should`, past) takes a PERF VP (`have` + participle) as complement; the lexical V is `written` with `[trans]` and object NP. Only MOD carries tense. If the learner marks *have* as tensed, direct them to the first verb of the sequence. |
| You should have been writing that essay (Disc.2/[56], p.133) | MOD → PERF → PROG → lexical V. Used to show recursion; each auxiliary heads one VP; still only MOD is tensed. |
| That hippo could easily have killed me ([62], p.123) | Per Assumption 1, the pre-verbal adverbial *easily* modifies the following PERF VP. Present this as the book's stated assumption. |
| They have been complaining for the fun of it ([66], p.124) | Per Assumption 2, the sentence-final adverbial modifies the lexical VP. |
| They were going to India next week last week ([69], p.125) | Documented exception to Assumption 2: `last week` modifies the past-tensed PROG VP (past intentions); `next week` modifies the lexical VP. One contrast decision. |
| Max was fired by the boss ([78], p.127) | PASS VP; the object moved to subject, leaving a gap (blob) in object position; `[trans]` stays on the verb; the *by*-phrase is an adjunct. Recognition only. |
| Otto was driven mad by the noise ([81], p.128) | Passive of a `[complex]` verb: the direct object is the gap and *mad* remains the object predicative, not a subject predicative. |
| Byron would not dance ([86], p.129) | *not/n't* attaches to the tense-carrying MOD (triangle on the MOD node). No separate TENSE node. |
| Byron did not dance ([88], p.129) | do-support: empty *do* under a TENSE node carries tense and negation; the lexical V (`dance`) is untensed. This is the pivotal contrast page. |
| Was Byron dancing ([91], p.130) | The tense-carrying PROG auxiliary fronts to C (daughter of S-bar, sister of S); the gap stays under the PROG node. |
| Does Byron dance ([93], p.131) | do-support in a question: *do* (under TENSE) moves to C. |
| Was Kubla extravagant ([103], p.132) | *be* always behaves like an auxiliary: the lexical (copula) V fronts to C, and the gap sits under the V node. |

For the pilot: reuse the existing numbered trace controls, one editable Builder per page, and a page-specific notation group that explains MOD/PERF/PROG/PASS/TENSE and the pres/past features shown on that page. Feedback must identify the specific node (e.g. "the tense is on the MOD node `should`"). Present the adverbial placements as the book's simplifying assumptions, not as universal rules. The stored `[69]` and `Ex.1(2)` time-adverbial exceptions stay in text/callout form, not as a graded item unless a reviewer signs off.

## Coverage gaps (documented, deferred)

- Passive argument linking, the ditransitive first-object passivisation ([82b], Disc.4), and two-gap question+passives ([94a]/[94b], Disc.6).
- Coordination of lexical VPs ([Ex.3(e)], p.138).
- The full adverbial-ordering "intricate topic" (p.123) beyond the [62]/[66]/[69] contrasts.
- Participle-form tables ([7], p.120, [26]) as reference-only, not drilled.
- Further Exercises (pp.135–138) beyond the reused single contrasts.

## Draft checks

| Item | Prompt | Answer and feedback focus |
| --- | --- | --- |
| Opening 1 | In “You should have written an essay”, which word carries the tense? | **should.** Only the first verb of an auxiliary sequence is tensed; *have* and *written* are not. |
| Opening 2 | How many VPs does “Mina might have finished the report” contain, one per auxiliary plus the verb? | **Three** (MOD *might*, PERF *have*, lexical *finished*). Each auxiliary heads its own VP. |
| Opening 3 | In “Byron did not dance”, which word carries the tense and the negation? | **did.** *do* under the TENSE node carries tense and negation; *dance* is untensed. |
| Opening 4 | In “Is the cat sleeping?”, what has moved to the front, and what did it leave behind? | **The auxiliary *is* moved to the front (C), leaving a gap under its PROG node.** |
| Opening 5 | In “The window was broken by the wind”, what does the *by*-phrase tell you, and is it required to complete the verb? | **It names the agent and is an adjunct, not a required complement.** The verb is passive. |
| Closing 1 | In “You should have been writing that essay”, list the auxiliary types from top to bottom above the lexical verb. | **MOD → PERF → PROG.** Each auxiliary heads a VP; only MOD is tensed. |
| Closing 2 | Which single verb is tensed in “Nia could have been helping us”? | **could.** The tense feature sits only on the first verb of the sequence. |
| Closing 3 | In “Byron would not dance” versus “Byron did not dance”, what structural difference explains where *not* attaches? | **The first has a tensed MOD *would* for *not* to attach to; the second has no auxiliary, so do-support supplies an empty *do* under TENSE to carry tense and negation.** |
| Closing 4 | In “Does Byron dance?” what moved to C, and where did the gap remain? | ***do* moved from the TENSE node to C; the lexical V remains untensed with the gap under the auxiliary position.** |
| Closing 5 | In “Was Kubla extravagant”, why does *was* behave like an auxiliary even though the main verb *be* has no other verb to help? | ***be* always behaves like an auxiliary; the copula fronts to C and leaves a gap under V.** |

Opening items cover outcomes 1, 1, 3, 3 and 1. Closing items cover outcomes 1–2, 2, 3, 3 and 1. During implementation, map each item to its printed anchor above, finish option-specific feedback for every distractor, and confirm each figure reference resolves against `web/content/book/ch06.trees.json`. Verify desktop and mobile navigation, page-specific notation (auxiliary display names and pres/past features), both wrong and correct branch feedback, draft recovery, the score-only opening result, and closing score and incremental-XP retakes. Create the local source receipt before the Gate 4.6 walkthrough. The reviewed release catalog and its immutable assessment seed belong to publication.

## Open questions for owner review (Phase 4 step 2)

1. **Scope trim:** Is it acceptable to teach passive only as a *recognised* auxiliary type (PASS) and defer argument-linking/passivisation details to a documented gap? This keeps the chapter within the time target and matches the book's own "beyond the scope" caveat.
2. **Adverbial assumptions:** Do you accept presenting [62]/[66]/[69] as the book's *stated simplifications* with only the time-adverbial exception called out, rather than a full adverb-order treatment?
3. **do-support emphasis:** Do you agree that the do-support contrast ([86] vs [88]) should get the worked + practice pages, since negation and question formation both depend on it?

**Next step after approval:** implement Chapter 6 as a local pilot (mirroring the Chapter 5 pilot files: `web/content/lessons/br-06-pilot.json`, `web/js/auxiliary-vp-pilot.js`, and a browser test), produce a pilot report, and stop at Gate 4.6. Do **not** begin Chapter 7.
