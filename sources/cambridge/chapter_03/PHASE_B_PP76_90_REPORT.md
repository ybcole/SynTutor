# Chapter 3 Phase B — audited extraction, printed pp. 76–90

**Status:** PARTIAL CHAPTER COVERAGE; 2026-11-10. Source: the user-supplied 1,862-page CGEL full PDF (printed page n corresponds to PDF viewer page n+20). No book text, tables or scan images are committed.

## Page-by-page source audit

Two consecutive ranges were read: 76–82 and 83–90. The finiteness table on printed page 89 was additionally inspected visually to confirm the braces that group imperative and subjunctive as finite, infinitival as non-finite. All generated examples are original. Every row below lists rules sourced to that printed page; some principles intentionally cite more than one page.

| Printed page | Newly recorded rule IDs | Examined topics and restrictions |
|---|---|---|
| 76 | MORPH-024, MORPH-025, MORPH-026, MORPH-027 | syncretism; preterite versus perfect participle; stable morphological contrast |
| 77 | MORPH-025, MORPH-026, MORPH-027, MORPH-028, MORPH-029, MORPH-030, MORPH-031 | agreement restricted to preterite be; no distinct imperative/subjunctive inflection; perfect and passive participles |
| 78 | MORPH-030, MORPH-032, MORPH-033 | postnominal participial clause versus attributive VP; participle versus adjective |
| 79 | MORPH-033, MORPH-034, MORPH-035, MORPH-036 | event versus state; seem-complement test; very/too is a one-way adjective diagnostic |
| 80 | MORPH-037, MORPH-038, MORPH-039 | -ing progressive and modifying uses; relative time; verbal versus adjectival interpretation |
| 81 | MORPH-034, MORPH-035, MORPH-036, MORPH-039, MORPH-040, MORPH-041 | participle/adjective distribution; traditional gerund; verbal -ing versus gerundial nouns |
| 82 | MORPH-037, MORPH-040, MORPH-041, MORPH-042, MORPH-043 | nominal determiners, plural and of-complements; adjective/adverb diagnostics; ambiguity and genitive exception |
| 83 | MORPH-037, MORPH-040, MORPH-044 | three -ing categories and unified verb inflection; imperative/subjunctive/infinitive plain form |
| 84 | MORPH-045, MORPH-046, MORPH-047, MORPH-048 | infinitival to is a separate word; plain present versus plain form; be distinction |
| 85 | MORPH-046, MORPH-047, MORPH-048, MORPH-049 | plain present agreement; non-tensed plain form; modal defective paradigms; preterite uses |
| 86 | MORPH-049, MORPH-050, MORPH-051 | preterite past/remoteness/backshift; irrealis were and informal was |
| 87 | MORPH-050, MORPH-052, MORPH-053 | variant extended uses of were; irrealis distinct from subjunctive; no forced correction |
| 88 | MORPH-050, MORPH-052, MORPH-054, MORPH-055 | irrealis only with singular be; primary and secondary form definitions; clause finiteness |
| 89 | MORPH-055, MORPH-056, MORPH-057 | visually checked finiteness table; subordinate non-finite forms; finite imperatives and subjunctives |
| 90 | MORPH-056, MORPH-057, MORPH-058 | negative imperative versus infinitival; subjunctive alternants; for + accusative in overt-subject infinitives |

## Rules and implementation status

- New rules: **35** (27 classifications, 5 constraints, 2 descriptive generalisations, 1 style/prescriptive record).
- All new constraints have a protocol 1.1 diagnostic specification, two or more original correct examples, two original incorrect examples, two original minimal pairs and explicit false-positive guards. Each detector is **spec_only**. No detector behavior, source-based XAI explanation runtime, or precision/recall is claimed.
- New rule status: `NEEDS_REVIEW`. Crosswalk mappings to Burton-Roberts: `unverified`. No independent second-pass audit or owner bulk approval was conducted, and no rule was added to the runtime allow-list.

## Explicit exceptions and review cautions

- Printed pp. 76–77: a regular preterite and participle may be syncretic; spelling alone must not cause an error.
- Printed pp. 79, 81: modifying a participial adjective with very/too can be grammatical, and some adjectives are not gradable. Never classify an ungradable item automatically as a verb.
- Printed pp. 81–83: gerundial nouns are not the gerund-participle verb form. Bare -ing words may remain ambiguous, and genitive dependents occur with both categories.
- Printed pp. 84–85: split infinitives are not grammatical errors; modal auxiliaries and be do not follow ordinary agreement patterns.
- Printed pp. 86–88: informal *was* can express remoteness; *were* has varied uses across speakers, but inversion and the idiom *as it were* restrict this alternation. Avoid universally mandatory were rules.
- Printed pp. 89–90: classification of finiteness depends on construction, not the plain word form. Imperative do-support differs from infinitival negation.

## Honest limits

Chapter 3 printed pages 71–73 are the chapter-level contents and were skipped with a reason. Pages 74–75 are supported by the earlier approved §1.1 report, which remains unchanged. Pages 76–90 have been newly reviewed and extracted. **Pages 91–212 have not yet been processed**; Chapter 3 is **not complete**. More specialised discussion later in the chapter may require exceptions or revisions to these candidates. No full chapter independent review or detector activation has occurred.
