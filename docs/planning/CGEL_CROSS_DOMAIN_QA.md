# Cambridge cross-domain QA

## First pass

The Phase B baseline contains 3,914 records and 204 diagnostic specifications. The initial scan grouped titles by case-folded word tokens and grouped incorrect diagnostic examples by trimmed text with straight and curly apostrophes treated alike. Three title groups cross catalog domains. One incorrect example occurs in multiple specifications, and both prescribe the same correction. These exact-match scans are a starting point for review. Overlap can also occur between records with different wording or examples.

| Records | Scope decision | Phase C and lesson handling |
|---|---|---|
| CLS-357 and CLS-1451 | Chapter 14 describes the active and passive causative make pattern. Chapter 16 provides a second source specifically for the verbal passive. Both repair the shared example by inserting to. | Use CLS-357 as the primary specification for this construction, with CLS-1451 as corroboration for the passive. A missing-to event on the same governing make–infinitival relation gets one finding. Keep active bare infinitivals as a guard. |
| OTH-007 and PHR-464 | Both cover the contribution of contextual gestures to deixis. OTH-007 gives broader indexing examples, while PHR-464 highlights dependence on the immediate situation. | Combine the material in a lesson and retain both sources. A written sentence alone may not supply the deictic referent. |
| CLS-425 and PHR-095 | Both distinguish determiner function from determinative category. Chapter 2 provides the overview, and Chapter 5 details the phrase types that can fill the function. | Teach CLS-425 as the introductory distinction and use PHR-095 for the fuller classification. |
| CLS-1367 and PHR-636 | Both describe informal discourse-new this. The existential treatment is construction-specific, and the deixis treatment gives wider use and speaker variation. | Teach these as related uses and retain both source scopes. Treat discourse-new this as a guard against an automatic familiarity error. |

The linked records retain their IDs, source citations, original examples and review states. Detector selection in this table is a Phase C design decision and confers no runtime license. A later pass needs to compare paraphrased diagnostics by trigger, governing relation, correction and counterexamples, including potential overlaps with the current parser-backed rules.
