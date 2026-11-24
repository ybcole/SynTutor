# SynTutor: 26-sentence alignment remediation

**Result: 0 full / 14 partial / 12 fail → 0 full / 26 partial / 0 fail.** The remediated system gives useful, qualified results on all 26 cases. No case earns a full pass under the original audit’s requirement for a verified, error-specific explanation grounded in a defensible canonical tree.

## What changed

- **Detection and repairs:** Replaced determiner deletion with order-sensitive rules that retain quantifiers. Embedded questions prefer neutral tense inflection; polar questions invert an existing modal without do-support. The rules distinguish passive participles, placement complements, active causatives, repeated relative objects, distributive agreement, and degree-adverb placement. Names do not determine a person’s pronouns, and ambiguous inputs do not receive invented repairs.
- **Tree authority and feedback:** The B–R normalizer now withholds projection where a candidate implies a conflicting verb frame, a filled relative gap, an unconfirmed embedded gap, or misleading modifier attachment. Legacy findings distinguish error targets from supporting words and can mark a single word in a provisional tree without certifying the tree. Unverified verdicts no longer retain a claim of grammaticality. The Cambridge/XAI approval gates are unchanged.
- **Revision checks:** Safer, construction-specific edits preserve the relevant words or grammatical features. Emitted revisions are reparsed and checked for remaining and introduced diagnostics. Passing those checks is not independent proof of meaning preservation. Duplicate case/gerund diagnoses no longer inflate the revision impact in #3/#18.

## Exact production rerun

Branch `fix/syntutor-system-reliability-xai`; changes are uncommitted on baseline `05dfdf0f9d731d8ad783b5d6b50e55cbbb08f30f`. Baseline: [original 26-sentence audit](SYNTUTOR_26_SENTENCE_END_TO_END_ALIGNMENT.md). The exact 26 strings were run in one final `analysis_api.build_payload` batch with models initialized once, `FINAL-D1`, default variety, and browser-style candidate XAI enabled. The local spaCy `en_core_web_md` and Benepar `benepar_en3` pipeline and advisory CoLA were available. Raw candidate trees, canonical/working trees, verdicts, findings, spans, learner markers, and revised analyses were inspected. All 26 returned payloads.

**N** = normalized canonical tree; **W** = unresolved canonical analysis with a provisional working tree. **V** = emitted and mechanically validated revision, including a reparse with no remaining or introduced diagnostic; the corrected tree was normalized unless noted. The four component columns are after remediation. The overall column compares the original audit with this rerun.

| Case | Tree | Detection | XAI | Correction | End-to-End | Observed result / remaining issue |
|---|---|---|---|---|---|---|
| 1. The dogs barks loudly. | PASS (N) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | `C-SUBJECT-AGREEMENT`: *barks* marked, *dogs* supports the diagnosis. V: “The dogs bark loudly.” Local, not verified. |
| 2. The boy run fast. | PASS (N) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | Same rule: *run* marked, *boy* supports singular agreement. V: “The boy runs fast.” Local, not verified. |
| 3. Me went home. | PASS (N) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | `C-PRONOUN-CASE` marks subject *Me*, relates *went*, and reports one resolved error. V: “I went home.” |
| 4. Himself left early. | PASS (N) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | `C-REFLEXIVE-SUBJECT` explains no local antecedent; it marks *Himself* and relates *left*. No unique pronoun chosen without context. |
| 5. Mary likes himself. | PASS (N) | PASS | PARTIAL | PASS | FAIL → PARTIAL | `unverified`, no categorical mismatch based on the name. Conditional explanation distinguishes a coreferential reflexive from a different referent’s object pronoun. No automatic revision or mark. |
| 6. The all students passed. | PARTIAL (W) | PASS | PARTIAL | PASS | FAIL → PARTIAL | `C-DET-ORDER` marks *all*, relates *The*, and preserves both. V: “All the students passed.” No canonical tree for the erroneous order. |
| 7. I saw very tall a man. | PARTIAL (W) | PASS | PARTIAL | PASS | FAIL → PARTIAL | `C-ARTICLE-ORDER` marks *a* on the working tree and relates *very tall* and *man*. V: “I saw a very tall man.” |
| 8. She asked me where did he go. | PASS (N) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | `C-INDIRECT-Q-ORDER` marks *did*, relates *he* and *go*. V: “She asked me where he went.” Retaining *did* is explained as emphatic, not offered as the default. |
| 9. Did she can swim? | PARTIAL (W) | PASS | PARTIAL | PASS | FAIL → PARTIAL | `C-DO-MODAL`, no run-on finding. Marks *Did* and relates *can* and *she*. V: “Can she swim?” *Could* is conditional on past ability; `CLS-100` remains candidate-only. |
| 10. He can sings. | PARTIAL (W) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | Benepar still tags *sings* `NNS`; working tree leaves its category open. `C-MODAL-VERB-FORM` marks the word and relates *can*. V: “He can sing.” |
| 11. She didn’t went home. | PASS (N) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | `C-AUX-FORM` learner mark is on *went*, with *did* as a witness. V: “She didn’t go home.” |
| 12. The book was wrote by him. | PARTIAL (W) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | `C-BE-PAST` marks *wrote* rather than *was*; *was* and *by* support the passive diagnosis. V: “The book was written by him.” |
| 13. I put the book. | PARTIAL (W) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | `C-PLACEMENT-COMPLEMENT` explains that placement *put* needs a location or destination in addition to *book*. Advises supplying it, but does not invent one. |
| 14. He sleeps the bed. | PARTIAL (W) | PASS | PARTIAL | PARTIAL | FAIL → PARTIAL | No canonical transitive *sleeps*. `C-INTRANSITIVE-OBJECT` marks *sleeps* and relates *bed*. Gives *in*/*on* conditionally; no single spatial reading is selected. |
| 15. She explained me the problem. | PARTIAL (W) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | `C-TRANSITIVITY` marks *me*, with *explained* and the object NP as evidence. V: “She explained the problem to me.” |
| 16. He suggested me to go. | PARTIAL (W) | PASS | PARTIAL | PASS | FAIL → PARTIAL | `C-VERB-CLAUSE-PATTERN` marks *to* with *suggested/me/go* as witnesses. No independent nominative instruction in the existing infinitival frame. V: “He suggested that I go.” |
| 17. She made him to cry. | PARTIAL (W) | PASS | PARTIAL | PARTIAL | FAIL → PARTIAL | `C-CAUSATIVE-TO` marks *to*, relates *made/him/cry*, and preserves *him*. V: “She made him cry.” Reparse passed the grammar checks but the corrected B–R analysis remains unresolved. |
| 18. She enjoys to read. | PARTIAL (W) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | One `C-GERUND-INFIN` finding marks *to* and relates *enjoys/read*. V: “She enjoys reading.” `COMP-062` is an agreeing raw-tree observation, not a verified finding. |
| 19. I look forward to see you. | PARTIAL (W) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | `C-PREP-GERUND` marks *see* and explicitly explains prepositional *to*. V: “I look forward to seeing you.” |
| 20. The book that I bought it was expensive. | PARTIAL (W) | PASS | PARTIAL | PASS | FAIL → PARTIAL | No canonical occupied-slot-plus-gap claim. `C-RESUMPTIVE-RELATIVE` marks *it* with *that/bought* as witnesses. V: “The book that I bought was expensive.” |
| 21. What did you wonder whether John bought? | PARTIAL (W) | PARTIAL | PARTIAL | PASS | FAIL → PARTIAL | `unverified`; no invented matrix gap. Explains the possible embedded dependency and degraded extraction across a question marker. No change into a non-equivalent yes/no question. |
| 22. Who do you think that will win? | PARTIAL (W) | PARTIAL | PARTIAL | PASS | FAIL → PARTIAL | `unverified`; no canonical object-gap claim. Explains demonstrative versus complementizer and conditionally notes omission before an embedded subject gap in many varieties. No forced revision. |
| 23. There is many reasons. | PARTIAL (N) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | `C-EXISTENTIAL` marks *is*, relates *reasons*, and qualifies formal usage. Explanation identifies dummy *there*; tree still uses a generic pronoun label. V: “There are many reasons.” |
| 24. Each of the students have a book. | PASS (N) | PASS | PARTIAL | PASS | FAIL → PARTIAL | `C-SUBJ-AGREE-XP` marks *have* and identifies *Each* as the singular controller, not *students*. No subject-replacement alternative. V: “Each of the students has a book.” |
| 25. The man which I met was kind. | PASS (N) | PASS | PARTIAL | PASS | PARTIAL → PARTIAL | `C-RELATIVE-PRONOUN` marks *which* and relates *man*. Standard written usage is qualified; formal object *whom* is valid, not the only valid option. V: “The man whom I met was kind.” |
| 26. She speaks English fluently very. | PARTIAL (W) | PASS | PARTIAL | PASS | FAIL → PARTIAL | `C-DEGREE-ORDER` marks *very*, relates *fluently*, and explains the degree relationship. No canonical tree with two independent adjuncts. V: “She speaks English very fluently.” |

The pipeline returned 23 `ungrammatical` and 3 `unverified` outcomes. It emitted 20 revisions versus 12 in the baseline. Nineteen corrected trees normalized; #17 did not. Original-tree outputs changed from 16 normalized / 9 working / 1 raw-only to 10 normalized / 16 working / 0 raw-only. The lower normalized count reflects withholding unsupported analyses, not replacing them with new canonical labels. There were no verified Cambridge runtime grammar findings or XAI7 verified issues in the final set; `CLS-100` and `COMP-062` remained candidate-only.

## Verification and presentation

The regression controls exercise nearby examples, including *both her friends*, *so tall a woman*, valid emphatic embedded *did*, passive *was made to*, and valid quantifier agreement. The `so tall a` control requires no rule rejection or rewrite, while allowing an advisory model abstention.

- **Backend regression:** 14 targeted tests passed on the final backend, including the new variant/positive controls, passive and gerund regressions, relative-pronoun checks, and canonical binding. A broader 64-test run passed before the final localization and wording adjustments, also covering real-world NLP, agreement scoping, modals, learner explanations, and correction safety. The full repository suite was not run.
- **Frontend regression:** `test:evidence`, `test:legacy-map`, and `test:correction` passed. In headless Chromium, the latest available `origin/main` (`5f582552`) frontend and the reliability frontend used the same live backend to isolate presentation. Both rendered 22 SVG nodes for the shared agreement example and passed keyboard inspection, zoom/fit, highlighting, corrected-text reanalysis, mobile-width, and saved-onboarding checks. The branch additionally passed error versus supporting-node marking and revision-card checks for an embedded question, and displayed an error mark and revision on a provisional determiner-order tree.
- **Presentation change:** Restored `main`’s persisted onboarding dismissal without replacing the branch’s newer session behavior. No layout, renderer, CSS, lesson, or quiz changes.

## Remaining limitations

- Verified error XAI still requires approved rules with source-linked evidence for these constructions. Working-tree markings identify source words, not canonical syntactic relationships.
- Ambiguous embedded gaps (#21–22), full canonical treatment of several malformed constructions, and canonical projection of the corrected causative (#17) remain unresolved. Resolving them requires additional linguistic evidence, not weaker certification.
- No unrestricted correctness or semantic-equivalence claim is made. The audit is a challenge set, not a corpus estimate. The thesis and its reported evaluation metrics were not changed.
