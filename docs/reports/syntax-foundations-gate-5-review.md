# Syntax Foundations release review

Review the candidate on `feat/lessons/revision-integration`. The [Phase 5 report](syntax-foundations-revision-phase-5.md) records integration, regression and rollback results.

## Source and assessment review

Use Noel Burton-Roberts, *Analysing Sentences*, third edition, ISBN 9781408233740. The reference copy recorded for the pilots uses printed page + 15 as the PDF page. Verify pagination against the copy in use before checking a figure.

From the repository root, generate the internal answer packet into a file outside the public web directory.

```sh
python scripts/foundations_review_packet.py > foundations-review.md
```

The packet lists all 110 items, options, expected answers, feedback, outcomes and current printed page anchors. For each chapter, use the packet alongside its linked source notes. Record the reviewed commit, version, item or figure ID, exact printed page, and the reviewer's decision. If a prompt admits another defensible answer, record the alternative and fix the prompt or key before signing. Review the actual tree, including its labels, branch attachment, and any gap or controller. Confirm that the figure reference explains the structure demonstrated.

Chapters 1–3 need particular attention because their current assessment anchors reuse a small set of legacy source records. Use these review ranges to locate evidence for each item before changing its catalog anchors.

| Chapter | Where to verify the item references |
| --- | --- |
| 1 · Constituents | Omission, replacement and question tests on pp. 10–15. Nested brackets and immediate branches on pp. 13–17. Attachment readings on pp. 15–18, including [36]. |
| 2 · Functions | Subject boundaries, predicate and yes/no questions on pp. 24–28. Category and function on pp. 29–32, including [33–35]. Sisterhood, modification and the P–NP dependency on pp. 31–38. |
| 3 · Categories | Nouns, names and NP substitution on pp. 47–53. Degree, adverbs and AdvP on pp. 54–56 and 62. Locative PP on pp. 56–57 and coordination on pp. 57–62. |

## First-time learner walkthrough

Start the local static server and open the [combined catalog](http://127.0.0.1:8000/?preview=foundations#lesson/catalog).

```sh
python -m http.server 8000 --bind 127.0.0.1 --directory web
```

Use a fresh browser profile for each first attempt. Ask learners to work through Chapter 1's constituent tests, Chapter 6's auxiliary chain or Chapter 11's derivation. Time each run from the introduction through the first closing result. Record interruptions separately. Ask the learner to explain what one branch or bracket means and record which instruction they had to reread. Check on desktop and on a phone where possible.

| Chapter | Device | Elapsed time | Reading or interaction difficulty | Learner's explanation |
| --- | --- | --- | --- | --- |
| 1 | | | | |
| 6 | | | | |
| 11 | | | | |

## Owner decision

Record the reviewed commit, reviewer and date, chapter decisions, learner timing evidence and any changes required before approval. Once approved, use the deployment and rollback checklist in the integration report. The generated seed can be rehearsed without activating any chapter. A stored assessment version with different keys or sections must fail the seed transaction and receive a new version through the reviewed release process.
