# Chapter 2 pilot review · Sentence structure: functions

Run `python -m http.server 8000 --bind 127.0.0.1 --directory web` from the revision branch, then open the [Chapter 2 pilot](http://127.0.0.1:8000/?preview=br-02#lesson/br-02/introduction). Preview progress and XP are device-only. Chapter 1 is available through its existing `preview=br-01` link, now with the book's title in the catalog and header.

## Source and teaching sequence

The pilot follows the [Chapter 2 storyboard](../planning/syntax-foundations-chapter-2-storyboard.md). The AI source check used Burton-Roberts, *Analysing Sentences*, third edition, printed pp. 24–45 (PDF pp. 39–60), in the same copy recorded in the Chapter 1 receipt.

| Learner task | Printed anchors and source check |
| --- | --- |
| Find a complete subject and predicate | Pp. 24–28. The yes/no question keeps the entire lantern NP together. Its auxiliary moves in front of the subject. The original declarative establishes the predicate span. |
| Trace category and function | Pp. 29–32, [33–35]. The first diagram is the early top split with NP and VP triangles. The Mira example expands the VP to reveal a second NP. Both groups have category NP, and only the one directly under S is the subject in this tree. |
| Repair one branch | Pp. 30–31, [33–34]. The unscored V2 repair accepts the lantern NP under VP with the subject directly under S. The preview uses an authored target. |
| Explain dependencies | Pp. 31–38, [35], [43], [46], [48]. Compare sisters within the relevant phrase. Test omission within the same reading. The full location can be optional even though the intended use of “beside” needs its landmark. |
| Transfer and assess | Pp. 24–38. The written response accepts equivalent explanations via self-check. The two five-item checks use distinct original sentences. The closing check covers all three outcomes. |

The source figures informed the scope and notation. The pilot diagrams and examples are original teaching material. Independent linguistic review and Gate 4.2 acceptance are pending. The 9 min 50 sec estimate is a design estimate. A first-time learner has yet to time the chapter.

## Verification and release boundary

- The Chromium walkthrough checks exact catalog and header titles in both pilots, wrong and correct subject boundaries, visible trace feedback, incomplete and repaired trees, draft reload, the 390 px transfer view, score-only opening feedback, and source disclosure.
- A closing result of 0/5 completes the chapter after the required visits and earns zero XP. A later 5/5 earns 15 device XP. The walkthrough made no parser requests.
- The pilots are separate from the published catalog and hosted account scoring. The Chapter 2 preview includes no Cambridge curriculum changes. Release requires a new reviewed catalog entry and assessment seed, the active-version prerequisite compatibility check, and the existing migration gate. The previously documented legacy receipt mismatches still block full publication validation.
- The Chapter 1 pilot and all 12 published Lessons browser regressions passed. The Lessons and Builder test suites and static build passed.

Pilot source hashes:

- `web/content/lessons/br-02-pilot.json` — `f5f037e59bdc42329cbb10a1cea60fb0c7576388308668e84f8067cb815da998`
- `web/js/functions-pilot.js` — `2d11efc13c69f3c6a4e18f88b20b6ae0fb56a13d8b007b3c70bf38125c07beca`
