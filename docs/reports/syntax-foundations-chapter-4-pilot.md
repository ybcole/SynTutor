# Chapter 4 pilot review · The basic Verb Phrase

From the revision branch, run `python -m http.server 8000 --bind 127.0.0.1 --directory web` and open the [Chapter 4 preview](http://127.0.0.1:8000/?preview=br-04#lesson/br-04/introduction). The eight pages use device-only progress and XP. Try the direct-object exercise before using its guide. On the next three pages, switch the tree steps and compare the highlighted constituents and the features on V.

## Source receipt

The [storyboard](../planning/syntax-foundations-chapter-4-storyboard.md) maps printed pp. 67–86 (PDF pp. 82–101) of Noel Burton-Roberts, *Analysing Sentences*, 3rd ed., Pearson, 2011, ISBN 9781408233740. Text was checked across the chapter and diagrams were visually checked on printed pp. 71–73 and 76–78. The worked examples and assessment sentences are original.

| Scope | Printed anchors and review |
| --- | --- |
| Lexical head and basic VP | Pp. 67–70. The introduction connects the earlier subject–predicate split to the lexical verb and its complements. Auxiliary structure and modifier attachment are deferred to Chapters 6 and 5 respectively. |
| Transitive and intransitive | Pp. 70–72, [21–22]. “The bridge” is an NP sister of V [trans]. In “Nora waited”, V [intrans] is the only immediate part of VP. The window examples show how the same lexical verb can appear in different patterns. Opening 1–2 and closing 1 use these distinctions. |
| Ditransitive | Pp. 72–74, [26], [32]. In “handed Leo a map” and “handed a map to Leo”, “a map” is the direct object. The recipient is expressed by an NP or a corresponding PP. Both complements attach directly under VP. Opening 3 and closing 2 apply this distinction. |
| Intensive and complex transitive | Pp. 74–78, [46a–b], [51]. The NP “a coach” identifies Mina with “became” and is a direct object with “met”. The AP “slippery” describes the object “the steps” and attaches beside V [complex] and the object NP. Opening 4 and closing 3–4 check the described participant. |
| Prepositional complement and optional location | Pp. 78–79, [56] and summary. The PP “on her notes” is selected by “relied”; “in the studio” is a subject predicative with “was” and an optional location with “waited”. Opening 5 uses the optional location contrast. Closing 5 uses a separate verb that selects an “of” phrase. |

The local overlay supplies source IDs for the five newly cited pages. Published catalog records are isolated from these additions. The pilot uses a separate content version, `2.0.0`. When preparing the release, transfer reviewed source metadata and generate the matching immutable assessment seed from the release catalog. No hosted migration or activation was run. Independent instructor review and first-time learner timing remain pending. The 9 min 50 sec storyboard budget is an estimate.

## Walkthrough results

- The Chapter 4 browser test exercises eight-page navigation, keyboard activation of the intransitive trace, the accessible tree outline, page-specific verb features, and a 390 px viewport in dark mode.
- The tree check gives feedback on the detached branch. The guide connects it, Check my tree confirms the repair, Undo detaches it, and reload restores the repaired draft. The transfer response survives catalog resume and reload.
- The opening check reports 2/5 without answers or XP. The closing check reports 3/5 and 9 XP, then 5/5 and 15 total XP after a retake. The published Chapter 4 still opens through its normal route. The walkthrough sends no parser requests.

Regression checks passed for the Chapter 3 pilot and all 12 published lessons. `npm run test:lessons`, `npm run test:builder`, and `node scripts/build.js` also passed.

Pilot file hashes:

- `web/content/lessons/br-04-pilot.json` — `cdf2ef9ce11eb5363b74aea3f672916b812ffb7804a4cf9495c0a6ea9f879c80`
- `web/js/basic-vp-pilot.js` — `13f5dd6706c616a808bc59ecbb0c55edf4c4d43abe3613d6d71f564048d4012c`

Gate 4.4 review precedes Chapter 5.
