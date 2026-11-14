# Chapter 1 pilot review

**Status:** Implemented and browser-tested. Gate 3 acceptance and first-time learner timing are pending.

## Open the pilot

From the root of the revision branch, start the static app:

```sh
python -m http.server 8000 --bind 127.0.0.1 --directory web
```

Open [Chapter 1 pilot](http://127.0.0.1:8000/?preview=br-01#lesson/br-01/introduction). The preview uses device-only progress in a separate namespace. Open the same route without the query parameter to see the published Chapter 1. The source and assessment changes in this branch are available for local review. The published course catalog, existing answer-key migrations, and hosted database were left intact.

## Walkthrough

The catalog and chapter header use the book’s title, **Sentence structure: constituents**. The six pages follow the reasoning in the [source map and storyboard](../planning/syntax-foundations-chapter-1-storyboard.md). The same sentence carries the learner from nested brackets to omission, replacement and question tests. The learner then compares flat and nested phrase markers and repairs a flat tree. Two partial V1 diagrams show alternative attachments, followed by a written transfer response with a hint and an authored comparison. The recap gives the analysis procedure and printed-page references.

The opening and closing checks each have five items. The opening displays the score without answers and earns zero XP. The closing displays last and best scores, feedback and correct answers. The browser walkthrough confirmed that a first 3/5 earns 9 device XP and an improved 5/5 reaches 15 XP. The sidebar distinguishes a visited teaching section from a finished assessment. The timing estimate is 9 min 45 sec. The automated interaction test excludes reading and reasoning, so actual first-time learner timing remains open.

## Source receipt

Noel Burton-Roberts, *Analysing Sentences*, third edition, Pearson, 2011, ISBN 9781408233740. Reviewed printed pages 6–23, PDF pages 21–38. Reference PDF SHA-256 is `4d6fe351bac7702c3e60bcc38ae0c98d99592c914d7f8a32f83601ac8154e4ac`. The separate AI source pass inspected the book text and relevant diagrams. It does not establish independent linguistic review or owner acceptance.

| Reviewed element | Printed anchors | Decision |
| --- | --- | --- |
| Opening substitution, location answer and omission | 10–15 | The clock span, lake location and bench location each answer the requested test. The opening check keeps its answer key out of the result screen. |
| Opening brackets and closing landmark and direct branches | 13–17, [25a–c], [34–35] | Inner brackets include the whole landmark. The two immediate elements under the outer node are the first word and the inner node. |
| Closing optional phrase and longer landmark | 10–12, 15–17 | The time phrase may be omitted in the supplied sentence. The bus-identifying clause belongs to the longer landmark under the stipulated reading. |
| Opening and closing ambiguity, teaching diagrams and written transfer | 15–18, [36] | Both attachment readings are represented when context permits them. The final item fixes the reporter-identifying interpretation. Accept either wording or order in the transfer if both interpretations and attachment groups are identified. |
| Tree repair and comparison | 13–17, [25a–c], [34–35] | Use Chapter 1 lettered nodes. The flat contrast deliberately omits the inner constituent. The partial ambiguity diagrams omit the subject and later category labels. |

Pilot source hashes:

- `web/content/lessons/br-01-pilot.json` — `f6bb26ade9c4c3edd5f3f06db1dcd026271e143b93c64cb1cbb55ab66feb1aff`
- `web/js/constituents-pilot.js` — `d3554765ca4ebb73ea5830d5e9f8112f25c0ddd200286aef7884660a3351cc0d`
- Reused `web/js/constituent-tree-builder.js` — `459eeaada0538c9d0ae68311acaebe0fcc9417290d9ce1a1ce6a730752642f51`

The diagrams in the pilot are authored teaching views and are kept outside the shared FINAL-D1 contract. For publication, promote the approved Chapter 1 content into the versioned course catalog, add the new source receipt and immutable assessment seed, run publication validation, and coordinate activation with the Phase 2 migration plan. Preserve the historic v1 receipt. The known pre-existing Chapter 2 receipt drift remains separate from the pilot and must be addressed for the full catalog validator to pass.

## Verification

- `python scripts/test_chapter_one_pilot_browser.py` exercised the real preview in Chromium. It checked keyboard tree controls, visible captions, guided repair and reload, mobile transfer and response recovery, source disclosure, opening and closing scores, a retake, and isolation from the published lesson. The walkthrough called no parser endpoint.
- `npm run test:lessons`, `npm run test:builder`, and `npm run test:assessments` passed.
- The browser regression for all 12 published lessons and the Phase 2 assessment browser fixture passed. The static build passed.
