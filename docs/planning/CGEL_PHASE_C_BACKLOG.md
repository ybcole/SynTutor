# Cambridge Phase C backlog

Snapshot through the Chapter 20 punctuation, spelling-inflection, tense-aspect, determiner, verb-form, usage, pronoun-case, pro-form, word-order, complement-selection and final-surface batches. The 11 outside-pilot specifications are deferred semantic review, not detector targets. The [master plan](CAMBRIDGE_FULL_COVERAGE_MASTER_PLAN.md) defines the exit criteria. The [cross-domain QA](CGEL_CROSS_DOMAIN_QA.md) explains the pilot scope decisions.

| Diagnostic specifications | Primary pilot | Supporting pilot | Outside pilot | Production-enabled |
|---:|---:|---:|---:|---:|
| 204 | 187 | 6 | 11 (deferred) | 0 |

## Next implementation batch

**No further recognizable-pattern detector batch is queued.** The remaining 11 outside-pilot constraints are deferred semantic review: agreement attraction, remote conditionals, supplementary relatives, reciprocal binding, fused-head `one` and ellipsis. They are not SynTutor detector targets for this phase because the triggers depend on semantic interpretation, binding or ellipsis resolution rather than a stable surface relation. A few are pattern-detectable in principle, so they are not recorded as `none_possible`; they need a dedicated source review before any final disposition. Production remains at zero.

The next practical step is review and integration of the 187 candidate-only pilots, not more surface detectors. The Phase D selected-sentence pipeline (`server/cgel_phase_d.py`) and candidate XAI tree mapping (`server/cgel_candidate_xai.py`) are implemented. Phase D applies explicit edit hints, reparses and reruns the checks, and reports local lineage; the XAI mapping binds findings to syntax-tree nodes and composes context-aware candidate paragraphs. Both remain production-disabled.

The remaining work before lessons/quizzes is review, UI verification of the candidate-only sections, and independent source review. The 11 deferred semantic specifications are a separate future review queue, not a blocker for this phase.

## Chapter 20 punctuation batch (2026-11-13)

Implemented all 15 remaining primary Chapter 20 punctuation specifications plus the supporting `OTH-726` article check in `server/cgel_punctuation_probe.py`. The probe is offline and candidate-only: `production_enabled` remains false, every Cambridge registry rule stays disabled, and the source records remain `spec_only`.

The batch covers `OTH-671`, `OTH-688`, `OTH-698`, `OTH-699`, `OTH-701`, `OTH-708`, `OTH-712`, `OTH-715`, `OTH-717`, `OTH-726`, `OTH-730`, `OTH-737`, `OTH-740`, `OTH-743`, `OTH-756` and `OTH-764`. `server/test_cgel_punctuation_probe.py` checks every incorrect source example, every correct example, every source false-positive guard, held-out punctuation variants and exact edit spans. Source pages are pp. 1725, 1733, 1737–1739, 1741–1745, 1748, 1750, 1753–1755, 1761 and 1764.

Known scope limits: `OTH-698` detects structural nesting and a narrow semicolon-elaboration pattern; `OTH-717` covers vocatives but not the full dislocation inventory; `OTH-730` covers agreement and pronoun dependence on a parenthesised coordinate; `OTH-740` and `OTH-743` use surface quotation spans rather than canonical quotation relations. These limits are candidates for independent review, not claims of detector accuracy.

## Spelling inflection batch (2026-11-13)

Implemented the 14 queued spelling-inflection specifications in `server/cgel_spelling_probe.py`: `PHR-164`, `MORPH-109`, `MORPH-237`, `MORPH-258`, `MORPH-309`, `MORPH-311`, `MORPH-313`, `MORPH-316`, `MORPH-357`, `MORPH-385`, `MORPH-445`, `MORPH-477`, `MORPH-482` and `MORPH-483`. The probe is offline and candidate-only; production remains disabled and the registry detector state remains `spec_only`.

`server/test_cgel_spelling_probe.py` checks every incorrect source example, every correct example, every source false-positive guard, held-out spelling variants and exact edit spans. Sources are Ch. 5 p. 391; Ch. 18 p. 1598; and Ch. 19 pp. 1655, 1660, 1675–1677, 1687, 1694–1695, 1709 and 1717–1719.

The implemented checks are deliberately lexeme-scoped where the source pattern is lexically established. `MORPH-309`, `MORPH-311`, `MORPH-313` and `MORPH-316` cover the diagnostic lexemes and a few transparent variants, not the full productive English spelling rule; `MORPH-258`, `MORPH-445`, `MORPH-477`, `MORPH-482` and `MORPH-483` use surface numeral, measure and fraction patterns; `MORPH-385` is restricted to the listed invariant inhabitant bases. These scope limits need independent review before any production claim.

## Tense and aspect batch (2026-11-13)

Implemented `OTH-377`, `OTH-439` and `OTH-458` in `server/cgel_tense_aspect_probe.py`. The probe is offline and candidate-only; production remains disabled and the registry detector state remains `spec_only`.

`server/test_cgel_tense_aspect_probe.py` checks every incorrect source example, every correct example, every source false-positive guard, held-out variants and exact edit spans. Sources are Ch. 3 p. 191 for `OTH-377`, p. 197 for `OTH-439` and p. 200 for `OTH-458`.

Scope limits: `OTH-377` recognises temporal `when`, `before`, `after` and `as soon as` adjuncts and simple present-tense repairs; it deliberately leaves complex auxiliation and ambiguous volitional readings unevaluated. `OTH-439` is limited to an explicit past attempt or search followed by affirmative `and could` plus an achievement verb, so capacity and habitual uses are left alone. `OTH-458` targets finite `wish` complements with present auxiliaries; lexical present verbs and more remote constructions need separate coverage. These are candidate scopes, not production claims.

## Article determiner batch (2026-11-13)

Implemented the 12 queued Chapter 5 determiner specifications in `server/cgel_determiner_probe.py`: `PHR-028`, `PHR-043`, `PHR-044`, `PHR-080`, `PHR-084`, `PHR-088`, `PHR-126`, `PHR-128`, `PHR-133`, `PHR-140`, `PHR-157` and `PHR-161`. The probe is offline and candidate-only; production remains disabled and the registry detector state remains `spec_only`.

`server/test_cgel_determiner_probe.py` checks every incorrect source example, every correct example, every source false-positive guard, held-out variants, POS-filtered nominal heads and exact edit spans. Sources are Ch. 5 pp. 329, 339, 349–353, 371–373, 375, 379, 387–388 and 390.

The countability classification is deliberately small and lexeme-based. `PHR-028`, `PHR-043` and `PHR-044` use explicit noun sets; `PHR-080`, `PHR-084`, `PHR-088`, `PHR-157` and `PHR-161` combine surface patterns with parser POS checks where a tree is available; `PHR-080` and `PHR-084` emit findings without an automatic rewrite because the source repair is lexical. `PHR-126` covers the two fused-head shapes in the diagnostic, not the full range of fused-head environments. These scopes need independent review before any production claim.

## Verb form batch (2026-11-13)

Implemented the seven queued verb-form specifications in `server/cgel_verb_form_probe.py`: `MORPH-025`, `MORPH-035`, `COMP-042`, `COMP-061`, `COMP-116`, `COMP-194` and `WCAT-059`. The probe is offline and candidate-only; production remains disabled and the registry detector state remains `spec_only`.

`server/test_cgel_verb_form_probe.py` checks every incorrect source example, every correct example, every source false-positive guard, held-out variants and exact edit spans. Sources are Ch. 3 pp. 76–77, 79, 81 and 113; Ch. 4 pp. 220, 270 and 306; and Ch. 6 p. 545.

Scope limits: `MORPH-025` recognises a fixed list of irregular past participles used as the sole finite verb; regular syncretic forms are left alone as the source requires. `MORPH-035` uses parser structure to distinguish verbal participles from participial adjectives. `COMP-194` recognises the two named causative verbs with no ordinary object. `COMP-061` and `COMP-116` use surface patterns and a gerund/base lexicon. `WCAT-059` prefers parser structure and falls back to a lexical base-verb check. These are candidate scopes, not production claims.

## Usage batch (2026-11-13)

Implemented 17 queued constraints in `server/cgel_usage_probe.py`: `PHR-083`, `PHR-110`, `PHR-240`, `OTH-615`, `COMP-041`, `MORPH-114`, `MORPH-130`, `MORPH-391`, `MORPH-480`, `MORPH-481`, `CLS-120`, `CLS-1159`, `CLS-1188`, `CLS-1239`, `CLS-1415`, `CLS-1425` and `CLS-1325`. The probe is offline and candidate-only; production remains disabled and the registry detector state remains `spec_only`.

`server/test_cgel_usage_probe.py` checks every incorrect source example, every correct example, every source false-positive guard, held-out variants and exact edit spans. Sources are Ch. 1 pp. 9–10; Ch. 3 pp. 112, 115; Ch. 5 pp. 351, 361, 432; Ch. 13 pp. 1127, 1138, 1154; Ch. 16 pp. 1383, 1419, 1422–1423; Ch. 18 pp. 1603, 1612; and Ch. 19 pp. 1696, 1717–1718.

Scope limits: `MORPH-391` uses parser structure plus a person-noun set and only the New Zealand example. `PHR-110` reports the over-coordinated `both` construction without an automatic rewrite. `CLS-1159` uses a mass-noun set. `OTH-615` recognises contracted final coordinates but does not distinguish every clause-coordination context. `CLS-1239` covers the diagnostic resemblance shapes, not the full `as`/`like` inventory. These are candidate scopes, not production claims.

## Pronoun case batch (2026-11-13)

Implemented the seven queued pronoun-case specifications in `server/cgel_pronoun_case_probe.py`: `PHR-289`, `PHR-290`, `PHR-295`, `PHR-305`, `PHR-321`, `PHR-580` and `PHR-582`. The probe is offline and candidate-only; production remains disabled and the registry detector state remains `spec_only`.

`server/test_cgel_pronoun_case_probe.py` checks every incorrect source example, every correct example, every source false-positive guard, held-out variants and exact edit spans. Sources are Ch. 5 pp. 461, 464–465, 470–471, 483 and Ch. 17 p. 1497.

Scope limits: `PHR-289` uses a verb list and a small accusative map; `PHR-295` uses a finite-past verb list and deliberately leaves auxiliaries and embedded subjects alone; `PHR-305` and `PHR-321` use genitive maps and punctuation boundaries; `PHR-580` reorders the diagnostic double-object shape; `PHR-582` reports the `herself's` shape without an automatic rewrite and removes the genitive in the `Clara's herself` shape. These are candidate scopes, not production claims.

## Pro-form and ellipsis batch (2026-11-13)

Implemented 11 queued constraints in `server/cgel_proform_probe.py`: `PHR-629`, `PHR-632`, `PHR-644`, `PHR-645`, `PHR-654`, `PHR-666`, `PHR-684`, `PHR-704`, `PHR-705`, `PHR-706` and `PHR-737`. The probe is offline and candidate-only; production remains disabled and the registry detector state remains `spec_only`.

`server/test_cgel_proform_probe.py` checks every incorrect source example, every correct example, every source false-positive guard, held-out variants and exact edit spans. Sources are Ch. 17 pp. 1508–1509, 1512, 1515, 1518, 1524, 1530 and 1539.

Scope limits: `PHR-632` uses a mass-noun set and a small set of following prepositions; `PHR-644` and `PHR-654` use surface cardinal/verb patterns; `PHR-684`, `PHR-704`, `PHR-705` and `PHR-706` use bounded clause windows; `PHR-737` handles the listed negated auxiliaries. These are candidate scopes, not production claims.

## Word-order batch (2026-11-13)

Implemented 15 queued constraints in `server/cgel_word_order_probe.py`: `PHR-247`, `PHR-381`, `PHR-420`, `PHR-769`, `COMP-085`, `COMP-202`, `MORPH-056`, `WCAT-046`, `CLS-114`, `CLS-128`, `CLS-213`, `CLS-217`, `CLS-333`, `COMP-063` and `COMP-189`. The probe is offline and candidate-only; production remains disabled and the registry detector state remains `spec_only`.

`server/test_cgel_word_order_probe.py` checks every incorrect source example, every correct example, every source false-positive guard, held-out variants and exact edit spans. Sources are Ch. 3 pp. 89–90, 97; Ch. 4 pp. 247, 309; Ch. 5 p. 435; Ch. 6 pp. 534–535; Ch. 7 pp. 604, 632; Ch. 10 pp. 856, 909–911; Ch. 14 pp. 1214–1219; Ch. 17 p. 1548; and Ch. 4 pp. 221, 304.

Scope limits: the reorder rules are pattern-scoped and not general transformations. `CLS-128` deliberately requires a capitalized or definite subject to avoid fronted-phrase false positives. `CLS-213` uses a small preterite map. `COMP-063` and `COMP-189` use parser structure and treat time NPs as adjuncts. `COMP-202`, `COMP-085` and the question reorderings emit candidate edits for review, not automatic rewrites. These are candidate scopes, not production claims.

## Complement-selection and inversion batch (2026-11-13)

Implemented 13 queued constraints in `server/cgel_order_usage_probe.py`: `CLS-1166`, `CLS-1197`, `CLS-1218`, `CLS-1479`, `CLS-1379`, `CLS-108`, `CLS-117`, `CLS-156`, `CLS-286`, `PHR-748`, `COMP-138`, `COMP-033` and `COMP-040`. The probe is offline and candidate-only; production remains disabled and the registry detector state remains `spec_only`.

`server/test_cgel_order_usage_probe.py` checks every incorrect source example, every correct example, every source false-positive guard, held-out variants and exact edit spans. Sources are Ch. 3 pp. 96, 102, 105–106, 111; Ch. 4 p. 280; Ch. 10 p. 874; Ch. 13 pp. 1129–1130, 1141, 1145; Ch. 14 pp. 1182–1183; Ch. 16 pp. 1406–1407, 1442–1443; and Ch. 17 p. 1541.

Scope limits: the reorder rules are pattern-scoped. `CLS-108` uses a small past-to-base map. `CLS-117` uses an adverb and lexical-verb set. `CLS-156`, `CLS-286` and `PHR-748` handle the diagnostic orders only. `COMP-138` skips heavy objects. `COMP-033` and `COMP-040` handle the listed auxiliary/have patterns. These are candidate scopes, not production claims.

## Final surface batch (2026-11-13)

Implemented 12 queued constraints in `server/cgel_final_surface_probe.py`: `PHR-220`, `PHR-258`, `PHR-590`, `PHR-593`, `PHR-600`, `PHR-602`, `PHR-653`, `CLS-1222`, `CLS-1259`, `CLS-1274`, `CLS-1276` and `CLS-1329`. The probe is offline and candidate-only; production remains disabled and the registry detector state remains `spec_only`.

`server/test_cgel_final_surface_probe.py` checks every incorrect source example, every correct example, every source false-positive guard, held-out variants and exact edit spans. Sources are Ch. 5 pp. 423, 441; Ch. 13 pp. 1148, 1162, 1168–1169; Ch. 16 p. 1384; and Ch. 17 pp. 1499–1502, 1515.

Scope limits: `PHR-220` and `PHR-258` use adjective sets and surface order. `PHR-600` and `PHR-602` use a small plural/reflexive rewrite. `PHR-653` uses a mass-noun set. `CLS-1259` uses a comparative-to-superlative mapping. `CLS-1274` and `CLS-1276` handle the diagnostic definiteness shapes. `CLS-1329` reorders the named double-object verbs. These are candidate scopes, not production claims.

## Deferred semantic review (2026-11-13)

The following 11 specifications are outside the pilot but are **not** queued detector work and are **not** claimed as `none_possible`:

`PHR-343` (agreement attraction versus grammatical overrides), `OTH-453` (remote conditional apodosis), `CLS-1095` (supplementary relative antecedent), `PHR-054` (partitive selection with aggregate plurals), `PHR-601` (compound reciprocals across a finite clause), `PHR-606` (subject restriction on verb-domain reciprocals), `PHR-612` (genitive antecedent exclusion), `PHR-655` (content-clause complement of pro-nominal `one`), `PHR-656` (relational PP complement of pro-nominal `one`), `PHR-673` (contrasting complements after auxiliary stranding) and `PHR-696` (full-complement omission with lexical verbs).

These are deliberately not detector targets for the current recognizable-pattern phase. Their triggers depend on notional agreement, conditional mood, antecedent/binding relations, lexical recovery or ellipsis resolution. Several could support a narrow candidate check, but a pattern detector would not meet the source's semantic scope or false-positive guards. They require a dedicated semantic review before any future detector, `none_possible` disposition or production claim. The registry remains fail-closed and production-enabled Cambridge rules remain at zero.

## Phase D selected-sentence pipeline (2026-11-13)

Implemented `server/cgel_phase_d.py` and `server/test_cgel_phase_d.py`. The pipeline is candidate-only and production-disabled. It collects the candidate probes, groups explicit edit hints, applies one or more non-overlapping edits, reparses the candidate sentence, reruns the probes and reports per-finding lineage. It enforces a candidate cap, rejects candidates that introduce a new rule ID, and leaves findings without edit hints unresolved. A clean candidate is a local check result, not a whole-sentence grammaticality verdict.

The pipeline is documented in [CGEL_PHASE_D_SELECTED_SENTENCE.md](CGEL_PHASE_D_SELECTED_SENTENCE.md). Deferred semantic specifications are not included. The production registry remains untouched and all Cambridge rules remain disabled.

## Candidate XAI tree mapping (2026-11-13)

Implemented `server/cgel_candidate_xai.py` and `server/test_cgel_candidate_xai.py`. Candidate findings are now mapped onto syntax-tree nodes: mark spans, relation spans, punctuation boundaries, clause and phrase context. Phase D findings carry `tree_binding` and `candidate_explanation`. `/api/explain` exposes the same mapping when `include_candidate_xai` is requested, and the node inspector renders it as “Candidate grammar checks — not verified errors.” `/api/parse` accepts the flag too; candidate nodes are marked red on both the canonical B-R tree and the legacy parser tree, with the red mark explicitly labelled as a candidate check rather than a verified error.

This closes the gap between rule-level `learner_explanation`, structural node XAI and the 187 candidate checks. It does not approve a rule, license a grammatical function or certify a sentence. The canonical B-R fact graph is preferred; the labelled Benepar fallback is used when canonicalization fails. See [CGEL_CANDIDATE_XAI_MAPPING.md](CGEL_CANDIDATE_XAI_MAPPING.md).

## Pilot groups

| Construction | Primary specs | Supporting specs | Merged evidence | Next action |
|---|---|---|---|---|
| Modal complement form | COMP-034 | — | [#105](https://github.com/ybcole/SynTutor/pull/105) | Validate canonical selection and test fresh cases. |
| Modal stacking | COMP-031 | — | [#107](https://github.com/ybcole/SynTutor/pull/107) | Test variety and ambiguous lexical readings. |
| Supportive do | CLS-100, CLS-126 | COMP-030 | [#108](https://github.com/ybcole/SynTutor/pull/108), [#109](https://github.com/ybcole/SynTutor/pull/109) | Validate question relations and separate auxiliary compatibility from lexical inflection. |
| Perfect, progressive and passive selection | MORPH-026, COMP-035, COMP-036 | — | [#110](https://github.com/ybcole/SynTutor/pull/110), [#111](https://github.com/ybcole/SynTutor/pull/111) | Validate auxiliary roles and test ambiguous simple be controls. |
| Passive causative make | CLS-357 | CLS-1451 | [Review handoff](CGEL_CROSS_DOMAIN_QA.md#cls-357-independent-review-handoff) | Complete independent review of the canonical mapping and learner explanation. |
| Action complement of enjoy | COMP-062 | — | [#106](https://github.com/ybcole/SynTutor/pull/106) | Resolve copular tree grounding and test fresh controls. |
| Determiners on role objects | COMP-087 | PHR-197 | [#114](https://github.com/ybcole/SynTutor/pull/114) | Validate referential object function and broaden role and title controls. |
| Article pronunciation | MORPH-141 | OTH-726 | [#112](https://github.com/ybcole/SynTutor/pull/112) | Validate pronunciation evidence and the read-aloud condition. |
| Main-clause question inversion | CLS-103, CLS-104 | — | [#117](https://github.com/ybcole/SynTutor/pull/117) | Validate question context and canonical grounding. |
| Fronted negative and only inversion | CLS-106, CLS-107 | — | This batch | Validate scope independently and broaden parser coverage, including subordinate clauses. |
| Primary finite negation | CLS-099 | — | This batch | Validate the source of primary scope and extend coverage beyond clause-final not. |
| Negative imperative be | CLS-102 | CLS-131 | This batch | Validate ordinary verbal directive context and broaden parser coverage. |
| Inclusive let’s | CLS-268 | — | This batch | Verify broader subject and parser coverage, including vocatives. |
| Reported negative directives | CLS-270 | — | This batch | Broaden reporting-verb and parser coverage. |
| Auxiliary choice in canonical tags | CLS-182 | — | This batch | Broaden anchor and tag shapes and validate canonical grounding. |
| Question-tag agreement | CLS-183 | — | This batch | Broaden coverage of tag shapes and validate canonical grounding. |
| Canonical pronoun case | COMP-084 | PHR-283 | This batch | Validate canonical relations and broaden finite clause coverage. |
| Infinitival pronoun case | CLS-285 | — | This batch | Validate canonical subject grounding and broaden parser coverage. |
| Local reflexive antecedents | CLS-1101 | — | This batch | Validate conditional-clause grounding and assess additional argument frames. |
| Reflexive objects of pride | CLS-1103 | — | This batch | Validate the self-esteem construction and canonical object grounding. |
| Comparative like pronoun case | CLS-1244 | — | This batch | Validate detached initial and final adjuncts and retain medial and finite-clause controls. |
| Preposition selection with consist | COMP-060 | — | This batch | Validate composition sense and broaden complement coverage. |
| Fronting with come across | COMP-128 | — | This batch | Validate lexical sense and extend beyond direct questions to relatives and clefts. |
| Lexical number agreement | PHR-062, PHR-065 | — | This batch | Validate canonical subject heads and extend beyond the simple finite forms. |
| Demonstrative number agreement | PHR-087 | — | This batch | Broaden lexical and NP coverage while preserving number exceptions. |
| Agreement with the number as a total | PHR-079 | — | This batch | Broaden finite verb coverage and validate canonical subject-head grounding. |
| Finite agreement with singular they | PHR-334 | — | This batch | Validate antecedent grounding and extend beyond simple main-clause be/have. |
| Mass aggregate agreement | PHR-347 | — | This batch | Validate additional subject shapes and preserve count collective readings. |
| Spatial demonstrative agreement | PHR-620 | — | This batch | Validate locative attachment and shared deictic context before any rewrite. |
| Basic coordination | CLS-1034, CLS-1035 | — | This batch | Broaden evidence for shared function and nonfinite subject coordination. |
| Plural determiners and noun coordination | CLS-1036 | — | This batch | Validate word-level scope and preserve full NP coordination. |
| Comparative degree gaps | CLS-1119 | — | This batch | Validate scalar comparative attachment and extend to other degree modifiers. |
| Comparative subject omission | CLS-1129 | — | This batch | Broaden retained-verb coverage and validate comparative attachment. |
| Polarity in declarative questions | CLS-171 | — | This batch | Validate question context and other licensors of temporal ever. |
| Remote conditional auxiliary selection | CLS-119 | — | This batch | Validate remoteness and expand beyond fronted if-clauses and preterite consequences. |
| Present-inclusive ever since | OTH-098 | — | This batch | Validate continuation context and extend beyond the narrow lexical and adjunct patterns. |
| Present perfect with completed-past adjuncts | OTH-102 | — | This batch | Validate single-event context and adjunct attachment. |
| Nested backshift | OTH-158 | — | This batch | Establish shared time reference and broaden reporting constructions. |
| Progressive aspect and fixed composition | OTH-216 | — | This batch | Validate static versus dynamic readings before considering a repair. |
| Perfect auxiliaries under catenatives | OTH-182 | — | This batch | Validate the temporally bound reading and additional complement shapes. |
| Overt object with active believe | CLS-320 | — | This batch | Validate complement attachment and broaden active frame coverage. |
| Overt subjects in wh-infinitivals | CLS-407 | — | This batch | Validate interrogative attachment and assess wh-subject cases separately. |
| Participial NP modifiers | CLS-408 | — | This batch | Validate NP attachment and preserve finite relatives. |
| Set expressions in which partitives | CLS-201 | — | This batch | Validate partitive attachment and extend beyond explicit some and any. |
| Exclamative what and articles | CLS-229 | — | This batch | Validate exclamative context and broaden count-head coverage. |
| Determiners before object-taking participles | MORPH-041 | — | This batch | Validate verbal object attachment and preserve nominal and genitive constructions. |
| Omitted consonant doubling | MORPH-078 | — | This batch | Extend beyond selected verb bases and validate ambiguous real-word spellings. |
| Mute e before ing | MORPH-080 | — | This batch | Broaden established verb coverage and preserve retention variants. |
| Final ie before ing | MORPH-083 | — | This batch | Validate tagging and preserve distinct bases such as dye. |
| Regular final-y plurals | MORPH-092 | — | This batch | Broaden common-noun coverage and preserve lexical variants. |
| Personal name plurals | MORPH-104 | — | This batch | Validate name identity and expand beyond the source examples. |
| Bare and marked genitives | MORPH-105 | — | This batch | Validate dependent plural genitives, parser segmentation, and legitimate apostrophe variants. |
| Apostrophes in possessive pronouns | OTH-761 | — | This batch | Validate ambiguous contractions and broaden possessive contexts. |
| Chapter 20 punctuation batch | OTH-671, OTH-688, OTH-698, OTH-699, OTH-701, OTH-708, OTH-712, OTH-715, OTH-717, OTH-730, OTH-737, OTH-740, OTH-743, OTH-756, OTH-764 | OTH-726 | This batch | Run held-out punctuation evaluation, deduplicate overlapping quotation findings, and validate the scoped `OTH-698`/`OTH-717`/`OTH-730` relations. |
| Spelling inflection batch | PHR-164, MORPH-109, MORPH-237, MORPH-258, MORPH-309, MORPH-311, MORPH-313, MORPH-316, MORPH-357, MORPH-385, MORPH-445, MORPH-477, MORPH-482, MORPH-483 | — | This batch | Validate the lexeme-scoped rules against held-out text and decide which broader spelling patterns need separate specs. |
| Tense and aspect batch | OTH-377, OTH-439, OTH-458 | — | This batch | Validate semantic scope, especially capacity readings for `OTH-439` and non-temporal `will` for `OTH-377`. |
| Article determiner batch | PHR-028, PHR-043, PHR-044, PHR-080, PHR-084, PHR-088, PHR-126, PHR-128, PHR-133, PHR-140, PHR-157, PHR-161 | — | This batch | Validate countability sets, POS filtering and the lexeme-scoped fused-head checks. |
| Verb form batch | MORPH-025, MORPH-035, COMP-042, COMP-061, COMP-116, COMP-194, WCAT-059 | — | This batch | Validate participle/adjective boundaries, the fixed participle list and the surface gerund conversions. |
| Usage batch | PHR-083, PHR-110, PHR-240, OTH-615, COMP-041, MORPH-114, MORPH-130, MORPH-391, MORPH-480, MORPH-481, CLS-120, CLS-1159, CLS-1188, CLS-1239, CLS-1415, CLS-1425, CLS-1325 | — | This batch | Validate clause-coordination boundaries for `OTH-615`, the person-noun set for `MORPH-391`, and the reorder edits. |
| Pronoun case batch | PHR-289, PHR-290, PHR-295, PHR-305, PHR-321, PHR-580, PHR-582 | — | This batch | Validate the finite-verb lists, genitive boundaries and emphatic-adjunct reorder. |
| Pro-form and ellipsis batch | PHR-629, PHR-632, PHR-644, PHR-645, PHR-654, PHR-666, PHR-684, PHR-704, PHR-705, PHR-706, PHR-737 | — | This batch | Validate antecedent recovery, the mass-noun set and the bounded ellipsis windows. |
| Word-order batch | PHR-247, PHR-381, PHR-420, PHR-769, COMP-085, COMP-202, MORPH-056, WCAT-046, CLS-114, CLS-128, CLS-213, CLS-217, CLS-333, COMP-063, COMP-189 | — | This batch | Validate the reorder edits, fronted-phrase guards and the peruse time-NP distinction. |
| Complement-selection and inversion batch | CLS-1166, CLS-1197, CLS-1218, CLS-1479, CLS-1379, CLS-108, CLS-117, CLS-156, CLS-286, PHR-748, COMP-138, COMP-033, COMP-040 | — | This batch | Validate complement selection, heavy-NP guards and the auxiliary-order rewrites. |
| Final surface batch | PHR-220, PHR-258, PHR-590, PHR-593, PHR-600, PHR-602, PHR-653, CLS-1222, CLS-1259, CLS-1274, CLS-1276, CLS-1329 | — | This batch | Validate reciprocal rewrites, comparative grading and double-object reordering. |
| Imperative verb form | CLS-130 | — | [#115](https://github.com/ybcole/SynTutor/pull/115) | Establish the source of directive intent and validate the resulting finding. |

## Rule-by-rule inventory

**Pilot** means a primary offline implementation exists. **Support** means the entry corroborates a pilot. **Next** identifies the next batch. **Queued** means source and overlap triage is pending in this tracker.

When a batch lands, update the rows and link its evidence. Record canonical grounding, held-out results, independent review, learner explanations and registry activation separately from prototype status.

### Agreement (9)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `PHR-062` | Plural agreement with cattle and police | Ch. 5, pp. 345 | Pilot |
| `PHR-065` | Singular agreement with news and shingles | Ch. 5, pp. 346 | Pilot |
| `PHR-079` | Agreement with the number as a total | Ch. 5, pp. 350 | Pilot |
| `PHR-087` | Demonstrative number agreement | Ch. 5, pp. 352, 353 | Pilot |
| `PHR-240` | Singular selection with more than one and one more | Ch. 5, pp. 432 | Pilot |
| `PHR-334` | Singular they and finite agreement | Ch. 5, pp. 493, 494 | Pilot |
| `PHR-343` | Agreement attraction versus grammatical overrides | Ch. 5, pp. 500, 501 | Deferred |
| `PHR-347` | Mass aggregates and agreement | Ch. 5, pp. 504 | Pilot |
| `CLS-183` | Agreement with the pronoun in canonical tags | Ch. 10, pp. 893 | Pilot |

### Article determiner (19)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `MORPH-041` | Determiners cannot directly govern gerund-participial verbs | Ch. 3, pp. 81, 82 | Pilot |
| `COMP-087` | Bare role NP requires determiner in ordinary object position | Ch. 4, pp. 253 | Pilot |
| `PHR-028` | Bare nominal cannot occupy ordinary singular count subject | Ch. 5, pp. 329 | Pilot |
| `PHR-043` | Noncount selectors much and a little | Ch. 5, pp. 339 | Pilot |
| `PHR-044` | Distributive each and every select count singular | Ch. 5, pp. 339 | Pilot |
| `PHR-080` | Singular complement with a great deal of | Ch. 5, pp. 349, 350 | Pilot |
| `PHR-084` | Number selection by plural quantity nouns | Ch. 5, pp. 351 | Pilot |
| `PHR-088` | Number selection by cardinal determiners | Ch. 5, pp. 352, 353 | Pilot |
| `PHR-126` | The cannot serve as a fused determiner-head | Ch. 5, pp. 371 | Pilot |
| `PHR-128` | Initial a in embedded numeral modifiers | Ch. 5, pp. 372, 373 | Pilot |
| `PHR-133` | All before an indefinite article | Ch. 5, pp. 375 | Pilot |
| `PHR-140` | Each as fused head and every as dependent | Ch. 5, pp. 379 | Pilot |
| `PHR-157` | Either selects a singular count nominal | Ch. 5, pp. 387, 388 | Pilot |
| `PHR-161` | No and none in dependent and fused-head functions | Ch. 5, pp. 390 | Pilot |
| `PHR-197` | Bare role nouns in ordinary object position | Ch. 5, pp. 409 | Support |
| `CLS-201` | Set expressions in which partitives | Ch. 10, pp. 903 | Pilot |
| `CLS-229` | Exclamative what and singular count NPs | Ch. 10, pp. 919, 920 | Pilot |
| `CLS-1036` | Singular-noun coordination cannot satisfy a plural determinative | Ch. 15, pp. 1334, 1335 | Pilot |
| `MORPH-141` | Liaison and article choice by sound | Ch. 18, pp. 1618 | Pilot |

### Extra word (7)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `CLS-100` | Supportive do excluded when a lexical clause already has an auxiliary | Ch. 3, pp. 93, 94 | Pilot |
| `COMP-030` | Supportive do is incompatible with other auxiliaries in one chain | Ch. 3, pp. 105 | Support |
| `COMP-041` | Supportive do excluded in idiomatic have got | Ch. 3, pp. 112 | Pilot |
| `PHR-381` | Non-expandable declarative complements | Ch. 7, pp. 604 | Pilot |
| `CLS-268` | No overt matrix subject before inclusive let's | Ch. 10, pp. 934, 935 | Pilot |
| `CLS-270` | Negating a to-infinitival report of a directive | Ch. 10, pp. 943, 944 | Pilot |
| `CLS-407` | No overt subject in infinitival interrogative complements | Ch. 14, pp. 1264 | Pilot |

### Missing word (10)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `CLS-102` | Negative imperatives use supportive do | Ch. 3, pp. 94 | Pilot |
| `CLS-120` | Aspectual used to requires do or to under code ellipsis | Ch. 3, pp. 115 | Pilot |
| `OTH-453` | Remote conditional apodosis requires a modal auxiliary | Ch. 3, pp. 199 | Deferred |
| `COMP-063` | Peruse normally requires an object | Ch. 4, pp. 221 | Pilot |
| `COMP-189` | Unlicensed implicit object for peruse | Ch. 4, pp. 304 | Pilot |
| `PHR-083` | Of with plural approximate number nouns | Ch. 5, pp. 351 | Pilot |
| `CLS-131` | Supportive do with be in ordinary negative imperatives | Ch. 10, pp. 857 | Support |
| `CLS-320` | Overt object with active believe plus an infinitival | Ch. 14, pp. 1203 | Pilot |
| `CLS-408` | Participial NP modifiers without relative markers | Ch. 14, pp. 1265 | Pilot |
| `CLS-1095` | Supplementary relative clause requires an antecedent anchor | Ch. 15, pp. 1353 | Deferred |

### Other (51)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `OTH-615` | Contraction with coordinated subjects | Ch. 1, pp. 9, 10 | Pilot |
| `PHR-054` | Partitive selection with aggregate plurals | Ch. 5, pp. 343 | Deferred |
| `PHR-110` | Both as a binary coordination marker | Ch. 5, pp. 361 | Pilot |
| `CLS-171` | Negative polarity items in simple positive declarative questions | Ch. 10, pp. 885 | Pilot |
| `CLS-1119` | Obligatory gap for the comparative governor counterpart | Ch. 13, pp. 1108 | Pilot |
| `CLS-1129` | Subject omission with a retained comparative verb | Ch. 13, pp. 1113 | Pilot |
| `CLS-1159` | Fewer with ordinary non-count singulars | Ch. 13, pp. 1127 | Pilot |
| `CLS-1166` | To complements of superior and inferior | Ch. 13, pp. 1129, 1130 | Pilot |
| `CLS-1188` | Definiteness with attributive same | Ch. 13, pp. 1138 | Pilot |
| `CLS-1197` | Complement selection with similar | Ch. 13, pp. 1141 | Pilot |
| `CLS-1218` | Nominal complement in the postpositive other than pattern | Ch. 13, pp. 1145 | Pilot |
| `CLS-1222` | Anaphoric gap in supplementary reporting as | Ch. 13, pp. 1148 | Pilot |
| `CLS-1239` | Like with NP for resemblance and as for capacity | Ch. 13, pp. 1154 | Pilot |
| `CLS-1244` | Personal pronoun case after comparative like | Ch. 13, pp. 1156 | Pilot |
| `CLS-1259` | Comparative grade in two-member set comparisons | Ch. 13, pp. 1162 | Pilot |
| `CLS-1274` | Definiteness in incorporated ranking superlatives | Ch. 13, pp. 1168, 1169 | Pilot |
| `CLS-1276` | Integrated relatives after free superlatives | Ch. 13, pp. 1169 | Pilot |
| `CLS-1034` | Basic coordination requires equivalent syntactic functions | Ch. 15, pp. 1323 | Pilot |
| `CLS-1035` | Infinitival and gerund-participial clause coordination restriction | Ch. 15, pp. 1324 | Pilot |
| `CLS-1325` | Unstressed personal pronoun before a verbal particle | Ch. 16, pp. 1383 | Pilot |
| `CLS-1329` | Indirect object cannot follow direct object in the double-object alternant | Ch. 16, pp. 1384 | Pilot |
| `CLS-1379` | Subject–auxiliary inversion with clausal subjects | Ch. 16, pp. 1406, 1407 | Pilot |
| `CLS-1415` | Raised it in clefts and the need for be | Ch. 16, pp. 1419 | Pilot |
| `CLS-1425` | Bare who unavailable as a fused-relative pseudo-cleft head | Ch. 16, pp. 1422, 1423 | Pilot |
| `CLS-1451` | To in passive counterparts of bare-infinitival actives | Ch. 16, pp. 1432 | Support |
| `CLS-1479` | Be and get in the two perception-verb frames | Ch. 16, pp. 1442, 1443 | Pilot |
| `PHR-600` | Every plus singular noun as a reciprocal antecedent | Ch. 17, pp. 1501 | Pilot |
| `PHR-601` | Local structural licensing of compound reciprocals | Ch. 17, pp. 1502 | Deferred |
| `PHR-602` | Compound reciprocals lack an emphatic adjunct use | Ch. 17, pp. 1502 | Pilot |
| `PHR-606` | Subject restriction on verb-domain reciprocals | Ch. 17, pp. 1503 | Deferred |
| `PHR-612` | Genitive antecedent exclusion in the mixed verb–noun reciprocal domain | Ch. 17, pp. 1503 | Deferred |
| `PHR-620` | Spatial agreement inside a demonstrative NP | Ch. 17, pp. 1505 | Pilot |
| `PHR-629` | Nondeictic that as a fused definite determiner-head | Ch. 17, pp. 1508 | Pilot |
| `PHR-632` | Countability in fused that and pro-nominal one | Ch. 17, pp. 1508, 1509 | Pilot |
| `PHR-644` | Immediate cardinal or no before bare pro-nominal ones | Ch. 17, pp. 1512 | Pilot |
| `PHR-645` | Determiners requiring pro-nominal one in the immediate construction | Ch. 17, pp. 1512 | Pilot |
| `PHR-653` | Count antecedent restriction on pro-nominal one | Ch. 17, pp. 1515 | Pilot |
| `PHR-654` | Dependents of plural pro-nominal ones | Ch. 17, pp. 1515 | Pilot |
| `PHR-655` | Content-clause complements of pro-nominal one | Ch. 17, pp. 1515, 1516 | Deferred |
| `PHR-656` | Relational PP complements of pro-nominal one | Ch. 17, pp. 1515, 1516 | Deferred |
| `PHR-666` | Position of other relative to attributive adjectives | Ch. 17, pp. 1518 | Pilot |
| `PHR-673` | Limits on contrasting complements after auxiliary stranding | Ch. 17, pp. 1520 | Deferred |
| `PHR-684` | Antecedent head restriction on reduction-driven do | Ch. 17, pp. 1524 | Pilot |
| `PHR-696` | Full-complement omission with lexical verbs | Ch. 17, pp. 1528 | Deferred |
| `PHR-704` | Auxiliary-headed antecedent exclusion for do so | Ch. 17, pp. 1530 | Pilot |
| `PHR-705` | Contrastive objects and do so | Ch. 17, pp. 1530 | Pilot |
| `PHR-706` | Do so in comparisons | Ch. 17, pp. 1530 | Pilot |
| `PHR-737` | Polarity of additive inverted so | Ch. 17, pp. 1539 | Pilot |
| `MORPH-391` | Place names without derived nationality adjectives | Ch. 19, pp. 1696 | Pilot |
| `MORPH-480` | Multipliers of hundred | Ch. 19, pp. 1717, 1718 | Pilot |
| `MORPH-481` | A and one in composite numerals | Ch. 19, pp. 1718 | Pilot |

### Preposition (2)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `COMP-060` | Consist selects of | Ch. 4, pp. 220 | Pilot |
| `COMP-128` | Fixed come across cannot undergo ordinary PP-fronting | Ch. 4, pp. 275 | Pilot |

### Pronoun case (12)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `COMP-084` | Canonical pronominal subject and object case | Ch. 4, pp. 237 | Pilot |
| `PHR-283` | Finite clause subjects and nominative case | Ch. 5, pp. 459 | Support |
| `PHR-289` | Accusative in ordinary noncoordinate object positions | Ch. 5, pp. 461 | Pilot |
| `PHR-290` | Accusative subject of a for-infinitival | Ch. 5, pp. 461 | Pilot |
| `PHR-295` | Who as local subject or subjective predicative | Ch. 5, pp. 464, 465 | Pilot |
| `PHR-305` | Dependent and independent genitive pronouns | Ch. 5, pp. 470, 471 | Pilot |
| `PHR-321` | Own as fused modifier-head | Ch. 5, pp. 483 | Pilot |
| `CLS-285` | Accusative pronouns after infinitival for | Ch. 14, pp. 1182 | Pilot |
| `CLS-1101` | Reflexive anaphor requires the appropriate local antecedent in a chain | Ch. 17, pp. 1457 | Pilot |
| `CLS-1103` | Pride lexically requires the subject-bound reflexive object | Ch. 17, pp. 1488 | Pilot |
| `PHR-580` | Subject antecedent of an emphatic clause adjunct | Ch. 17, pp. 1497 | Pilot |
| `PHR-582` | Genitive exclusion with NP-internal emphatic reflexives | Ch. 17, pp. 1497 | Pilot |

### Punctuation (17)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `OTH-671` | Apostrophe shape in directional typography | Ch. 20, pp. 1725 | Pilot |
| `OTH-688` | Main-clause and subordinate embedded questions | Ch. 20, pp. 1733 | Pilot |
| `OTH-698` | Single-level constraint for repeated colons and semicolons | Ch. 20, pp. 1737, 1738 | Pilot |
| `OTH-699` | Colons and coordinate series | Ch. 20, pp. 1738 | Pilot |
| `OTH-701` | Boundary before non-initial bare coordinates | Ch. 20, pp. 1739 | Pilot |
| `OTH-708` | Boundary before connective adjuncts joining main clauses | Ch. 20, pp. 1741, 1742 | Pilot |
| `OTH-712` | Boundary before direct reported speech complements | Ch. 20, pp. 1743 | Pilot |
| `OTH-715` | Comma at the subject–verb boundary | Ch. 20, pp. 1744 | Pilot |
| `OTH-717` | Delimitation of vocatives parentheticals and dislocations | Ch. 20, pp. 1745 | Pilot |
| `OTH-726` | Article choice before a parenthesised element | Ch. 20, pp. 1748 | Support |
| `OTH-730` | Insulation of parenthesised content | Ch. 20, pp. 1750 | Pilot |
| `OTH-737` | Alternation of nested quotation marks | Ch. 20, pp. 1753 | Pilot |
| `OTH-740` | Quoted terminal full stop inside a continuing matrix sentence | Ch. 20, pp. 1754 | Pilot |
| `OTH-743` | Terminal suppression at the end of a quotation | Ch. 20, pp. 1755 | Pilot |
| `OTH-756` | Hyphens in numerals fractions and established formations | Ch. 20, pp. 1761 | Pilot |
| `OTH-761` | Genitive apostrophes and personal pronouns | Ch. 20, pp. 1763 | Pilot |
| `OTH-764` | Sentence-final abbreviation full stop | Ch. 20, pp. 1764 | Pilot |

### Spelling inflection (20)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `PHR-164` | Single-word another in ordinary indefinite noun phrases | Ch. 5, pp. 391 | Pilot |
| `MORPH-078` | Consonant doubling before vowel-initial suffixes | Ch. 18, pp. 1575, 1576 | Pilot |
| `MORPH-080` | Mute e deletion before ing | Ch. 18, pp. 1576, 1577 | Pilot |
| `MORPH-083` | Ie bases and ing spelling | Ch. 18, pp. 1579 | Pilot |
| `MORPH-092` | Regular noun plurals with final y | Ch. 18, pp. 1585 | Pilot |
| `MORPH-104` | Plural spelling of personal names | Ch. 18, pp. 1595 | Pilot |
| `MORPH-105` | Bare and marked genitives | Ch. 18, pp. 1595, 1596 | Pilot |
| `MORPH-109` | Adding k after final c | Ch. 18, pp. 1598 | Pilot |
| `MORPH-237` | Plural marking in established er plus preposition compounds | Ch. 19, pp. 1655 | Pilot |
| `MORPH-258` | Singular measure bases in attributive compounds | Ch. 19, pp. 1660 | Pilot |
| `MORPH-309` | Consonant doubling in lexical derivation | Ch. 19, pp. 1675 | Pilot |
| `MORPH-311` | Mute e deletion before a vowel-initial suffix | Ch. 19, pp. 1675 | Pilot |
| `MORPH-313` | Mute e retention after soft c and g | Ch. 19, pp. 1676 | Pilot |
| `MORPH-316` | Y replacement before suffixes | Ch. 19, pp. 1676, 1677 | Pilot |
| `MORPH-357` | Negative in alternants in spelling and speech | Ch. 19, pp. 1687 | Pilot |
| `MORPH-385` | Invariant inhabitant nouns in Class 1a | Ch. 19, pp. 1694, 1695 | Pilot |
| `MORPH-445` | Possessive ed and plural nominal inputs | Ch. 19, pp. 1709 | Pilot |
| `MORPH-477` | Uninflected power heads inside numerals | Ch. 19, pp. 1717 | Pilot |
| `MORPH-482` | Ordinal formation from the final cardinal base | Ch. 19, pp. 1718, 1719 | Pilot |
| `MORPH-483` | Numerator and denominator in fractions | Ch. 19, pp. 1719 | Pilot |

### Tense aspect (8)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `CLS-119` | Remote conditional apodosis requires modal auxiliary | Ch. 3, pp. 107 | Pilot |
| `OTH-098` | Bare preterite incompatible with present-inclusive ever since | Ch. 3, pp. 141 | Pilot |
| `OTH-102` | Definite completed-past adjunct with present perfect | Ch. 3, pp. 143, 144, 146 | Pilot |
| `OTH-158` | Backshift choices form a prefix through embedded clauses | Ch. 3, pp. 156 | Pilot |
| `OTH-216` | Fixed-composition state rejects ordinary progressive | Ch. 3, pp. 167, 168 | Pilot |
| `OTH-377` | Temporal adjuncts disallow ordinary futurity will | Ch. 3, pp. 191 | Pilot |
| `OTH-439` | Affirmative could and single-event perfective restriction | Ch. 3, pp. 197 | Pilot |
| `OTH-458` | Finite wish complements require preterite for unreal situation | Ch. 3, pp. 200 | Pilot |

### Verb form (20)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `MORPH-025` | Preterite licensing in a canonical finite clause | Ch. 3, pp. 76, 77 | Pilot |
| `MORPH-026` | Past participle complement of perfect auxiliary have | Ch. 3, pp. 76, 77 | Pilot |
| `MORPH-035` | Degree modification of participial verbs | Ch. 3, pp. 79, 81 | Pilot |
| `COMP-031` | Mutual exclusion of core modal auxiliaries in Standard English | Ch. 3, pp. 105, 107 | Pilot |
| `COMP-034` | Central modal selection of the following plain form | Ch. 3, pp. 106 | Pilot |
| `COMP-035` | Progressive be selects a gerund-participle | Ch. 3, pp. 106 | Pilot |
| `COMP-036` | Passive be selects a past participle | Ch. 3, pp. 106 | Pilot |
| `COMP-042` | Bare infinitival complement of had better | Ch. 3, pp. 113 | Pilot |
| `OTH-182` | Perfect auxiliaries are not selectable by all catenatives | Ch. 3, pp. 161 | Pilot |
| `COMP-061` | Tend selects a to-infinitival action clause | Ch. 4, pp. 220 | Pilot |
| `COMP-062` | Enjoy excludes a to-infinitival action complement | Ch. 4, pp. 221 | Pilot |
| `COMP-116` | Do pseudocleft aspect connectedness | Ch. 4, pp. 270 | Pilot |
| `COMP-194` | Construct and destroy lack ordinary inchoative uses | Ch. 4, pp. 306 | Pilot |
| `WCAT-059` | Prepositional to after adjectives | Ch. 6, pp. 545 | Pilot |
| `CLS-126` | Plain form after supportive do in questions | Ch. 10, pp. 856 | Pilot |
| `CLS-130` | Plain form in ordinary imperatives | Ch. 10, pp. 857 | Pilot |
| `CLS-182` | Auxiliary choice and tense in canonical tags | Ch. 10, pp. 892, 893 | Pilot |
| `CLS-357` | Infinitival marker in passive causative make | Ch. 14, pp. 1234 | Pilot |
| `MORPH-114` | Three-way vowel alternation | Ch. 18, pp. 1603 | Pilot |
| `MORPH-130` | Negative am and inversion | Ch. 18, pp. 1612 | Pilot |

### Word order (29)

| Rule | Construction | Cambridge source | Status |
|---|---|---|---|
| `MORPH-056` | Negative imperative differs from negative infinitival | Ch. 3, pp. 89, 90 | Pilot |
| `CLS-099` | Do-support in primary finite negation | Ch. 3, pp. 93, 94 | Pilot |
| `CLS-103` | Inversion of auxiliary and subject in closed interrogatives | Ch. 3, pp. 94, 95 | Pilot |
| `CLS-104` | Main-clause non-subject wh-inversion | Ch. 3, pp. 95 | Pilot |
| `CLS-106` | Clause-scoped initial negative triggering inversion | Ch. 3, pp. 95, 96 | Pilot |
| `CLS-107` | Initial only with clause scope triggering inversion | Ch. 3, pp. 95, 96 | Pilot |
| `CLS-108` | Fronted so and such in result constructions | Ch. 3, pp. 96 | Pilot |
| `CLS-114` | One prenuclear auxiliary in subject–auxiliary inversion | Ch. 3, pp. 97 | Pilot |
| `CLS-117` | Integrated frequency and modal adverbs after lexical verbs | Ch. 3, pp. 102 | Pilot |
| `COMP-033` | Ordering of modal, perfect, progressive and passive auxiliaries | Ch. 3, pp. 105, 106 | Pilot |
| `COMP-040` | Dynamic lexical have takes do-support | Ch. 3, pp. 111 | Pilot |
| `COMP-085` | Weak object pronoun before verb particle | Ch. 4, pp. 247 | Pilot |
| `COMP-138` | Direction adverb versus particle before light NP | Ch. 4, pp. 280 | Pilot |
| `COMP-202` | Explain does not license canonical double-object frame | Ch. 4, pp. 309 | Pilot |
| `PHR-220` | Post-head restrictor order in compound determinatives | Ch. 5, pp. 423 | Pilot |
| `PHR-247` | Such and exclamative what before a | Ch. 5, pp. 435 | Pilot |
| `PHR-258` | Pre-head complements adjacent to the noun | Ch. 5, pp. 441 | Pilot |
| `WCAT-046` | Placement of degree enough | Ch. 6, pp. 534, 535 | Pilot |
| `PHR-420` | Ago and elapsed-time on | Ch. 7, pp. 632 | Pilot |
| `CLS-128` | Inversion with a fronted non-subject question phrase | Ch. 10, pp. 856 | Pilot |
| `CLS-156` | Single fronting of uncoordinated interrogative phrases | Ch. 10, pp. 874 | Pilot |
| `CLS-213` | Clause order after idiomatic how come | Ch. 10, pp. 909 | Pilot |
| `CLS-217` | Maximal interrogative phrases | Ch. 10, pp. 910, 911 | Pilot |
| `CLS-286` | Position of for and its infinitival subject | Ch. 14, pp. 1182, 1183 | Pilot |
| `CLS-333` | Perfect have precedes progressive be | Ch. 14, pp. 1214, 1215, 1216, 1217, 1218, 1219 | Pilot |
| `PHR-590` | Distribution of each in split reciprocals | Ch. 17, pp. 1499 | Pilot |
| `PHR-593` | Adjunct one and direct-object other | Ch. 17, pp. 1500 | Pilot |
| `PHR-748` | Stranding restriction in interrogative fragments with determiners | Ch. 17, pp. 1541 | Pilot |
| `PHR-769` | Post-head else and implicit comparison | Ch. 17, pp. 1548 | Pilot |
