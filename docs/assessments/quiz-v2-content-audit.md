# Focused Quiz V2 content audit and correction pass

Base: `origin/feat/quiz-v2` at `c79341c702e0f3f51ac30b275c05dc47be0c9bc3`, fetched again on 2026-11-17. The preserved workspace history and existing refinement changes remain intact on `refine/quiz-v2`.

## Method and limits

Compared question prompts, displayed stimuli and reconstruction answers with their corresponding instructional sections: Cambridge's `cambridge-chapter-data.js` and Syntax's digest-checked `syntax-practice-source.json`. Read the relevant lesson explanations and examples for the findings below; checked the proposed answers and what learner work the format actually requires. Functional coverage tests are separate evidence about software behavior, not evidence that an item teaches or assesses well.

The reproducible screening command is `node scripts/audit_quiz_content.mjs /workspace/quiz-v2-content-audit.json`. It inventories 120 immutable legacy questions, 1,774 formal questions, and 835 mixed items (828 original, seven replacements). It finds 1,263 overlap candidates including retired originals, 1,261 among active items. A candidate has a quoted stimulus or reconstruction answer of at least four words occurring in the same lesson section after punctuation/spacing normalization. These counts are **not confirmed-defect counts**: common diagnostic sentences, quoted objects of analysis and scaffolded practice can legitimately overlap. Conversely, this scan cannot prove novelty or detect all superficial paraphrases. The detailed candidate file is an editorial review queue.

This is a targeted editorial comparison plus whole-bank automated screening, not independent human review or a semantic certification of every item. The bank still contains substantial lesson-derived material; it should not be described as wholly original, transfer-only assessment content. The seven confirmed local defects below were corrected; remaining overlap candidates were not rewritten en masse without individual evidence.

## Confirmed findings and changes

All IDs below have prefix `mixed:`. Replacements append `:revision-2` and use content version `2.0.1`.

| Original ID | Lesson evidence and defect | Replacement |
| --- | --- | --- |
| `cgel-ch03:situations-aspect:fill_blank:11` | The lesson separates telic accomplishments from perfective viewpoint. The item called *wrote a novel* “telic / _____” but keyed **perfective**, conflating distinct dimensions. | New bicycle-repair contrast asks about an inherent endpoint; key **telic**. Perfective is rejected. |
| `cgel-ch05:pronouns:grammar_correction:12` | The lesson contrasts dependent **her** with independent **hers**. The stimulus incorrectly has *hers car*, but the prompt claims **her** is wrongly used independently: the direction of the error is reversed. | Prompt asks to change only the erroneous genitive before *car*; **her car** is accepted. |
| `cgel-ch20:comma-uses:sentence_reconstruction:5` | One accepted answer omits the comma although the fixed token is **rained,**. That alternative is unbuildable; arbitrary order changes cannot remove punctuation. | Explicit initial subordinate-clause task with one buildable comma-preserving answer. |
| `cgel-ch01:defining-concepts:fill_blank:11` | The lesson explicitly demonstrates **They bottled the jam** to reject classification by notional meaning. The assessment repeats it while requesting the abstract slogan “grammatical _____”: copying plus memorization emphasis. | A new **pocketed the receipt** example asks for the category supported by tense marking and an object. |
| `cgel-ch01:defining-concepts:sentence_reconstruction:12` | Reconstructs the exact **They bottled the jam** demonstration, a superficial repeat rather than a new application. | New converted-verb example; instructions identify the head and object roles the learner must construct. It remains a scaffolded reconstruction, not evidence of unprompted category mastery. |
| `cgel-ch01:truth-entailment:fill_blank:4` | Merely recites the definition “If A cannot be true without B ... A _____ B”. Correct terminology, but definition retrieval alone fails the requested application emphasis. | Classify the truth relation between a shattering event and a breaking event, with an explanation distinguishing entailment from a defeasible expectation. |
| `cgel-ch01:truth-entailment:sentence_reconstruction:11` | “Arrange ... some students passed” supplies no premise or inference task. Its rationale mentions entailment, but the learner only orders words: an inappropriate use of reconstruction for this concept. | A new sculptures scenario requires the scope **not all**, preserving reconstruction while requiring the specified truth-conditional relation. |

## Retained examples and format findings

- Syntax `br-01/concepts` includes the familiar *Rae set up camp beside the pond* example. The lesson actually demonstrates its movement test. A question asking which movement is evidence is scaffolded recognition, not an original transfer item. It is flagged by the overlap scan and retained as an editorial candidate; it is not counted here as proof that the bank meets a transfer-only requirement. The immutable formal/XP catalog is not silently rewritten in this pass.
- The separate original application item *The ranger photographed the hiker with a drone* correctly keys VP attachment as the means of photographing. The lesson teaches PP attachment and structural ambiguity. Reusing that structural problem with another scenario is legitimate application; superficial lexical novelty alone would not establish quality, but the attachment-to-interpretation reasoning is the target here. No confirmed answer defect was found in this inspected item.
- Every chapter retains the mandated format set: Syntax blanks, reconstruction, tree construction and syntax-tree repair; Grammar blanks, reconstruction and grammatical correction. This is **availability**, not proof that every format is suitable for every semantic topic. The entailment reconstruction above is a concrete mismatch corrected on substantive grounds.
- The corrected punctuation prompt narrows the intended construction instead of rejecting another grammatical order arbitrarily. Exact-answer grammar correction still depends on an authored answer list; these edits do not claim unrestricted natural-language evaluation.

## Historical compatibility and scoring

Original questions remain in `cambridgeMixedItems` with their original IDs, version `2.0.0`, stimuli and answer keys. A selection-only flag excludes seven originals from new mixed attempts. Historical `itemsFor` lookups do not apply this flag, so existing manifests, drafts and submitted reviews resolve the original content. Replacements have separate IDs and version `2.0.1`; no old keys or score calculations change. The targeted regression checks historical resolution/grading and retired-item exclusion across 60 selection seeds per corrected item. No database schema, published XP catalog, server award formula or student records were modified.

## Catalog, layout and XP

31 chapter summaries and 327 topic summaries are newly authored assessment descriptions keyed by stable lesson/topic IDs, rather than sentences extracted from Lessons. The General Chapter Quiz button is in a right-aligned footer **after** the subtopic disclosure, preserving its original spec, draft lookup and start handler. Native disclosure keyboard behavior remains; shared `.quiz-published > summary` and `.quiz-history > summary` styling and open-state spacing are restored.

The XP curve is unchanged: `xpToReach(L) = 10L² + 90L`. The label shows cumulative current/next-threshold XP. The bar shows `(XP − current-level floor)/(next threshold − floor)`. At 250 XP: level 2 starts at 220; next threshold is 360; label `250/360 XP`; bar `30/140`. Hover text explains both quantities, and is cleared during identity refresh to avoid retaining another account's XP. Boundary tests cover levels 0–29.

## Verification result

Passed `npm run test:quiz-v2` (including the new targeted regressions), `npm run test:assessments`, and the complete Playwright browser suite with no page errors. Browser geometry checks cover footer order/right alignment and bottom spacing at 390px and 1360px, light and dark themes, expanded and collapsed subtopics. History open/close styling, mixed inputs, draft reload/resume, account isolation and the XP label/bar values are exercised. Screenshots `quiz-chapter-footer-desktop.png` and `quiz-mobile-dark.png` in `/tmp/syntutor-builder-browser` were visually inspected.

The final combined refinement patch is `/workspace/quiz-v2-refinement.patch`; it was checked against `origin/feat/quiz-v2` with an isolated Git index. No Supabase files changed. No push, merge, deployment or database write was performed. Codex Cloud review-target controls remain unavailable: any later PR must explicitly target **feat/quiz-v2**, not main.
