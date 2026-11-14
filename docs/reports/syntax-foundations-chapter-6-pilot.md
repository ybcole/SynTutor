# Chapter 6 pilot review · More on verbs: auxiliary VPs

Start the static lesson player with `python -m http.server 8000 --bind 127.0.0.1 --directory web`, then open the [Chapter 6 preview](http://127.0.0.1:8000/?preview=br-06#lesson/br-06/introduction). The nine-page preview uses device-only progress and XP. Trace the modal and perfect VPs, repair the detached VP, compare the passive and active object positions, then inspect the three yes/no question trees.

## Source receipt

Noel Burton-Roberts, *Analysing Sentences*, third edition, Pearson, 2011, ISBN 9781408233740. The [storyboard](../planning/syntax-foundations-chapter-6-storyboard.md) covers printed pp. 111–140 (PDF pp. 126–155). This pass checked the key teaching figures and reviewed the answer choices against their cited structures.

| Scope | Printed anchors and review |
| --- | --- |
| Progressive and stacked VPs | Pp. 121–122, [52–53b]. Each auxiliary heads a VP with a VP complement. The tense feature sits on the first verb. The worked chain adapts the printed example [53b], which the pilot metadata now credits. |
| Adverbial scope | Pp. 123–125, [62], [66], [69]. The lesson presents the two attachment patterns as assumptions for the examples and notes a time-phrase exception. |
| Passive | Pp. 125–128, [71], [78]. The original curator/statue contrast shows PASS, the direct-object gap and the optional agent PP outside the basic lexical VP. The lexical verb keeps [trans]. Complex and ditransitive passive derivations remain deferred. |
| Negation and do-support | P. 129, [86], [88]. The shared parent of TENSE and the lexical VP is the predicate VP. The tensed modal or TENSE bears the feature and groups the verb form with “not”. |
| Question fronting | Pp. 130–132, [91], [93], [103]. The fronted word is under C and the gap is under the original PROG, TENSE or lexical V node. Tense remains visible on that node in these diagrams. |

The assessed pilot version is `2.0.0`. Opening and closing checks use five items each. The revised closing examples test transfer from the taught examples. The preview overlay and the locally authored diagrams are isolated from the published catalog. Publication requires the reviewed catalog entry and matching immutable assessment seed. First-time learner timing and independent instructor review remain pending. The estimated budget is 10 minutes, including 35 seconds for passive recognition.

## Walkthrough

The browser test covered the opening score of 2/5 without answer review or XP, feedback on the tense-carrier choice, branch repair and undo, the saved branch after reload, mobile navigation and tree fit, passive recognition, negation and question trees, and the closing check. The 3/5 closing attempt earned 9 XP, and the 5/5 retake raised the total to 15 XP. The normal Chapter 6 route still loaded the published lesson. The test recorded no parser calls.

Chapter 5 and all 12 published lesson browser checks, lesson and Builder suites, the tree layout checks and Vercel-filtered static build passed. The pilot overlay passed catalog validation, and its worked tree passed the canonical JSON schema. The Python course validator stopped during import because `lemminflect` is unavailable in this environment.

Pilot hashes:

- `web/content/lessons/br-06-pilot.json` — `6f73dc7c59c7c38c77dc3055eb0d82588f476dfe829ffc06fc30edad7c13d383`
- `web/js/auxiliaries-pilot.js` — `244afba4b4f9f25d545c3ac0230a333b53ae2146e79a75cd9e1045bd832208a1`
