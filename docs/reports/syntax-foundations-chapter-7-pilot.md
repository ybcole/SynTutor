# Chapter 7 pilot review · The structure of Noun Phrases

Run `python -m http.server 8000 --bind 127.0.0.1 --directory web` from the revision branch and open the [Chapter 7 preview](http://127.0.0.1:8000/?preview=br-07#lesson/br-07/introduction). The eight-page pilot uses device-only progress and XP. Compare the empty DET with the plain pronoun tree, try the detached NOM branch, then switch between the two modifier attachments.

## Source receipt

Noel Burton-Roberts, *Analysing Sentences*, third edition, Pearson, 2011, ISBN 9781408233740. The [storyboard](../planning/syntax-foundations-chapter-7-storyboard.md) maps printed pp. 141–170 (PDF pp. 156–185). The examples use the chapter's V7 notation. Printed [32] and the discussion tree on p. 158 were checked during implementation to confirm the compound noun and participle labels.

| Scope | Printed anchors and analysis |
| --- | --- |
| DET, NOM and one-word NPs | Pp. 141–143, [1–7], [10]. “Those lanterns” has DET → DEM and NOM → N. Bare plural “baskets” has a leafless DET. A plain pronoun has one branch under NP. Opening 1 and 5 and closing 1 check these distinctions. |
| Possessives and pre-determiners | Pp. 143–146, [12], [14], [18]. An NP plus genitive *-s* can fill the possessive position. “All” combines with the entire NP “those baskets”, and “those” stays under DET. Opening 2 and closing 2 use pre-determiners. |
| Pre-modifiers | Pp. 146–149, [25–28], [32], [36], plus Discussion 3 on p. 158. “New” joins the smaller NOM “red kite”. The prose introduces QA, PartP and compound N. Opening 3 and closing 3 use the adjective-layering contrast. |
| Post-modifiers and scope | Pp. 150–155, [39a], [A–B], [65–67]. “From Cebu” joins “wooden crates” in the intended kind-plus-origin reading. “For the job” groups first with “applicant” in the other tree. Opening 4 identifies the origin phrase. Closing 4 specifies the intended kind reading and asks for the attachment. |
| Modified indefinite pronoun | Pp. 155–156, [72a–b]. The pronoun and its post-modifying PP are sisters under NP. Closing 5 uses a fresh example. |

The local overlay is version `2.0.0` with five opening and five closing items. It adds pilot source records and uses the catalog’s existing “those lanterns” tree for the editable repair. The two scope examples give a reading before asking learners to place the modifier. Recursive possessives, partitives, and the appendix’s pro-NOM *one* test remain outside this pilot. First-time learner timing and instructor review are pending. The 9 min 35 sec budget is an estimate. The reviewed catalog entry and matching immutable assessment seed belong to release preparation.

## Walkthrough results

- The browser test verified empty DET in the SVG and accessible tree outline, the plain pronoun contrast, and feedback for a detached NOM and one attached to DET. The guide repaired it, Undo restored the incorrect branch, and reload recovered the repaired draft.
- At 390 px the nested NOM and PP comparisons fit the reader. Catalog resume reopened the application page. The normal Chapter 7 route still showed the published lesson, and the preview made no parser requests.
- The opening check showed 2/5 without the answer key or XP. A 3/5 closing attempt earned 9 device XP. A 5/5 retake brought the total to 15 XP.

The Chapter 6 pilot, all 12 published lesson browser checks, lesson and Builder suites, tree-layout checks, and filtered static build passed.

Pilot file hashes:

- `web/content/lessons/br-07-pilot.json` — `874daab84152077a89befa3cbdfec02b25efaa2b903608b5f91d9ff46a68b729`
- `web/js/noun-phrases-pilot.js` — `1fbaf192210dee3e4e0c4fef320d09746b260b3b9b66629a02f9681abaefcb15`

Gate 4.7 review precedes Chapter 8.
