# Chapter 8 pilot review · Sentences within sentences

Run `python -m http.server 8000 --bind 127.0.0.1 --directory web` from the revision branch and open the [Chapter 8 preview](http://127.0.0.1:8000/?preview=br-08#lesson/br-08/introduction). The nine pages use device-only progress and XP. Compare overt and unfilled C, repair the detached C branch, then trace the clausal subject, object, and adverbial structures.

## Source receipt

Noel Burton-Roberts, *Analysing Sentences*, third edition, Pearson, 2011, ISBN 9781408233740. The [storyboard](../planning/syntax-foundations-chapter-8-storyboard.md) maps printed pp. 171–195 (PDF pp. 186–210) and records the figures checked. The pilot applies their structural analyses to SynTutor examples.

| Scope | Printed anchors and analysis |
| --- | --- |
| Embedding and coordination | Pp. 171–174, [1–4], [9–10]. The deepest clause in the bracketed example supplies what Leo said. That report is part of what Maya thinks. The transfer asks learners to locate the two S′ starts before revealing both complete spans. |
| Complementisers | Pp. 174–176, [11a–b], [15–17]. Overt “that” and “whether” fill C. In the reporting example without “that”, a leafless C sits beside S. The embedded interrogative keeps the subject before the auxiliary. |
| Subjects and objects | Pp. 176–181, [23–24], [36], [40–41]. NP dominates S′ in the subject and direct-object examples. In the extraposed version, dummy “it” fills the subject NP and the final S′ joins the main S directly. The copular example introduces S′ as a subject predicative. |
| A, N and P complements | Pp. 181–185, [47], [54], [61]. The S′ sits beside A within AP, beside N within NOM, or beside P within PP in the illustrated cases. |
| Time and reason | Pp. 185–187, [67c], [71], and Discussion 7 on p. 190. Temporal “after” is P with a bare S complement. “Because” fills C in an adverbial S′. Both larger groups in the comparison modify the basic VP. |

The version `2.0.0` overlay adds source records for the five opening and five closing items. It reuses the reviewed overt-C fragment for Builder repair. The 9 min 55 sec budget is an estimate. First-time learner timing and independent instructor review are pending. The reviewed catalog and immutable assessment seed belong to release preparation.

## Walkthrough

- The browser test verified empty C in the SVG and accessible outline, subject-before-auxiliary order with “whether”, and three immediate branches under the main S in the extraposed example.
- The Builder check identified the detached C, confirmed the guided repair, and verified Undo and draft recovery after reload. At 390 px, the new clause comparisons fit the reader and catalog resume returned to the transfer page.
- Both unscored activities gave feedback on incorrect and correct choices. The opening check displayed 2/5 with no answer review or XP. A 3/5 closing attempt earned 9 XP, and a 5/5 retake brought the total to 15 XP.
- The normal Chapter 8 route loaded its published lesson. The walkthrough made no parser requests.

Chapter 7 and all 12 published lesson browser checks passed, along with the lesson and Builder suites, the tree-layout checks, and the filtered static build.

Pilot file hashes:

- `web/content/lessons/br-08-pilot.json` — `9750e447e66a793977dd9fa09115129c8b08e5d784ab3f7e60423884cbcc3574`
- `web/js/embedded-clauses-pilot.js` — `e51658f4c6e297c46253e73a3811cbf39721fb7c4c1913bcb8309cf2bac55389`

Gate 4.8 review precedes the Chapter 9 outline.
