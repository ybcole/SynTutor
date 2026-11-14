# Chapter 9 pilot review · Wh-clauses

Run `python -m http.server 8000 --bind 127.0.0.1 --directory web` from the revision branch and open the [Chapter 9 preview](http://127.0.0.1:8000/?preview=br-09#lesson/br-09/introduction). The nine-page pilot uses device-only progress and XP. Compare the NP and PP gaps, repair the detached object NP, then switch between main and embedded questions and the two relative attachments.

## Source receipt

Noel Burton-Roberts, *Analysing Sentences*, third edition, Pearson, 2011, ISBN 9781408233740. The [storyboard](../planning/syntax-foundations-chapter-9-storyboard.md) maps printed pp. 196–223 (PDF pp. 211–238) and records the figures checked. The pilot uses the book's V9 convention and applies it to authored examples.

| Scope | Printed anchors and analysis |
| --- | --- |
| Main wh-questions | Pp. 196–201, [11b], [13–14] and Discussion 2, p. 213. C2 holds the wh-expression and C1 holds the fronted auxiliary in the examples. The companion contrast distinguishes an NP gap after P from a whole PP gap. The subject question illustrates the book's analysis of overt “is”. |
| Embedded questions | Pp. 201–203, [17–19], [26]. A deeper object gap can occur inside a report. An embedded wh-question has unfilled C1 and keeps “was” inside S. |
| Noun complements and relative variants | Pp. 204–208, [38–39], [44–54]. A noun-complement S′ joins N and contains a complete S. The relative S″ joins NOM and keeps its object gap with “which”, relative “that”, or unfilled C2 in the example. |
| Restrictive and non-restrictive relatives | Pp. 208–211, [59–60]. A restrictive relative narrows the set under NOM. A non-restrictive relative joins the whole NP and adds information about the identified group. The transfer asks learners to recover the object gap in a new restrictive relative. |

The local overlay is version `2.0.0` with five opening and five closing items. The existing canonical inspection tree supplies the Builder target. The 9 min 55 sec estimate still needs a first-time learner trial. Independent instructor review is pending. The reviewed catalog and matching immutable assessment seed belong to release preparation.

## Walkthrough

- The browser test verified NP and PP gap labels, two gaps in the main question, and one gap with unfilled C1 in the embedded question. It also checked that the relative keeps its gap when C2 is unfilled and that both scope answers receive specific feedback.
- The Builder identified the detached NP, checked the repair, and recovered it after Undo and reload. At 390 px the reader fit the question and relative comparisons. Catalog resume reopened the transfer page.
- The opening result was 2/5 with no XP or answer review. A 3/5 closing attempt earned 9 XP, and a 5/5 retake brought the total to 15 XP. The normal Chapter 9 route loaded the published lesson. The preview made no parser requests.

Chapter 8 and all 12 published lesson browser checks passed. Lesson and Builder suites, tree-layout checks, and the filtered static build also passed.

Pilot file hashes:

- `web/content/lessons/br-09-pilot.json` — `74c38651a6aa51165c1462bb6230f7699da88a4632162ef3397e769732fe06a9`
- `web/js/wh-clauses-pilot.js` — `eba0b6a172087ebccd93f35679c10d0788b72be16b8133fb0b24e43a0b443da6`

Gate 4.9 review precedes the Chapter 10 outline.
