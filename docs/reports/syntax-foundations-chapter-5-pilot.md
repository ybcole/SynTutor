# Chapter 5 pilot review · Adverbials and other matters

From the revision branch, run `python -m http.server 8000 --bind 127.0.0.1 --directory web` and open the [Chapter 5 preview](http://127.0.0.1:8000/?preview=br-05#lesson/br-05/introduction). The nine pages use device-only progress and XP. Compare the two uses of “in the shed”, then try attaching “in June” to the outer VP. On later pages, switch each tree to compare position, particle use, an understood recipient and sentence-level scope.

## Source receipt

The [storyboard](../planning/syntax-foundations-chapter-5-storyboard.md) maps Noel Burton-Roberts, *Analysing Sentences*, 3rd ed., Pearson, 2011, ISBN 9781408233740, printed pp. 87–110 (PDF pp. 102–125). The chapter text and the figures below were checked against the same reference copy as Chapter 4. SynTutor’s authored sentences apply the source structures to fresh examples.

| Scope | Printed anchors and review |
| --- | --- |
| Adjunct versus complement | Pp. 87–91, [12], [15–16], [17–20]. In the inspection and repair examples, the PP is a sister of the basic VP. With “put”, the locative object predicative is a sister of V. “Did so” with a different time recovers the activity and its object. Opening 1–2 and closing 1–2 test those distinctions. |
| Mobility | Pp. 92–93, [32]. “Quietly” attaches beside VP in both orders. “Last night” shows an NP with an adverbial function. Displaced and interposed cases are left to the book’s discussion. |
| Particles | Pp. 93–95, [35], [39], [40a–b]. In “Lea turned it off”, V [trans] [phrasal], object NP and Prt are sisters. The preposition “off” heads “off the bus” with the NP inside PP. Opening 3 and closing 3 use the pronoun order in clear transitive patterns. |
| Ellipsis | Pp. 96–98, [46]. The giving context identifies Ren. An NP over E represents the understood recipient and supplies no spoken word. The direct object remains overt. Opening 4 and closing 4 explicitly supply the recipient context. |
| Sentence adverbials | Pp. 98–101, [55a–b], [58]. The manner use of “honestly” is beside VP. The sentence comment is beside S. “Therefore” illustrates the conjunct’s link to preceding discourse. Opening 5 and closing 5 use whole-statement evaluations. |

The local overlay uses version `2.0.0` and supplies assessment citations for the additional printed pages. Read-only diagrams display VP₁ and VP₂ using display references. The embedded repair uses the existing canonical tree and comparison so the learner is checked on the attachment. The repair draft is scoped to the pilot version and its worked page.

Independent instructor review and first-time learner timing are pending. The 9 min 55 sec storyboard budget is an estimate. Publication requires the reviewed catalog entries and a matching immutable assessment seed. This preview uses local progress and has no hosted migration or activation.

## Walkthrough results

- Desktop and 390 px browser checks exercised the two PP readings, the accessible numbered notation, both adjunct positions, the particle and preposition contrast, the E branch, and sentence-level scope. The PP attachment question gave distinct feedback for each answer.
- The Builder check identified both a detached PP and a PP attached directly to S. The guide repaired the branch, Undo restored the wrong attachment, and reload recovered the repaired draft. The catalog resumed on the scope page.
- The opening check displayed 2/5 with no answer key or XP. A 3/5 closing score earned 9 XP and a 5/5 retake raised the total to 15 XP. The published lesson loaded through its standard route, and the walkthrough made no parser requests.

The Chapter 4 pilot and all 12 published lesson browser checks passed. `npm run test:lessons`, `npm run test:builder` and `node scripts/build.js` also passed.

Pilot file hashes:

- `web/content/lessons/br-05-pilot.json` — `ef7fb425724963030812748a959428cb1bc3b48c4a069f1e64a9019dbe286091`
- `web/js/adverbials-pilot.js` — `ddbdea09d55ab9db79feb47617bfd83dc3255587604c93679811c188d0eef637`

Gate 4.5 review precedes Chapter 6.
