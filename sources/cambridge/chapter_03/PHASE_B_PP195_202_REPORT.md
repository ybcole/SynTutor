# Cambridge Grammar — Chapter 3, printed pages 195–202

## Source, fidelity, and scope

Source: the complete user-provided *The Cambridge Grammar of the English Language* (Huddleston & Pullum et al., 2002), Chapter 3, **printed pp. 195–202**. One-based full-PDF page numbers **215–222** (zero-based **214–221**). The eight pages were read consecutively from the actual PDF, including source footnotes. Rendered images were inspected for pp. 195 and 200 to check the original typographical contrasts, prescriptive shall/will table, and tentative-modal table. The rule catalog contains **only paraphrased analytical claims and new English examples**, not the source's table or lengthy book prose.

## Printed-page coverage

| Printed page | Added rule IDs | Verified source distinctions |
|---|---|---|
| 195 | OTH-414–OTH-423 | Direction-seeking shall questions; first-person shall in futurity, conditional consequence and volition; rejection of the prescriptive person-based shall/will table; BrE/formality and AmE frequency; second/third-person guarantee shall; rare second-person interrogative shall; archaic legal protasis shall |
| 196 | OTH-424–OTH-432 | First-person shall as volition; §9.7 had better subjective deontic necessity, strong semantics/softer pragmatics, present orientation and internal negation; dynamic dare as courage, negative external scope; §9.8 modal preterite asymmetry; very rare past-time might and absence of ordinary past-time should |
| 197 | OTH-433–OTH-442 | Past could: permission, reasonable expectation, circumstances, existential traits, potential ability, ongoing perception; restriction on affirmative single-event perfective actualisation; past would in volition, habitual propensity and narrative futurity |
| 198 | OTH-443–OTH-450 | Stressed emotive would in one annoying event versus habitual stressed will; future-in-past would in narrative with expected actualisation; §9.8.2 backshift of could/might/would/should; ambiguity between backshifted open and remote conditionals, *were to* as remoteness cue |
| 199 | OTH-451–OTH-457 | §9.8.3 modal remoteness with implicit conditions; epistemic might versus permission could; remote apodosis needs a modal auxiliary; analysis that remote would retains the modal sense of open will rather than serving merely as a counterfactual marker; semantic differences between open and counterfactual worlds |
| 200 | OTH-458–OTH-465 | Wish finite-complement preterite requirement; comparison with remote conditionals; tentative would in estimates, could in requests, may/might speaker differences, affirmative epistemic could, and tentative permission questions |
| 201 | OTH-466–OTH-473 | Elaborate polite permission formula; would in indirect performatives and requests; would/should like as a tentative one-time future preference; indirect thanks; would appear/seem double hedging; would inside an open if-clause; special unrealised past possibility and as-if present readings of might/could |
| 202 | OTH-474–OTH-483 | Might/could as reproach; stronger present-time might criticism; §9.8.4 preterite status of should via backshift and remoteness, idiomatic meaning of should; dialect-sensitive may/might relationship, Dialect A versus Dialect B in remote/backshift and perfect environments; possible influence of modal must/ought without preterites |

**Boundary:** printed p. 202 ends *mid-explanation* of factors behind the Dialect B reanalysis. The discussion continues at p. 203, so the remainder is explicitly outside this batch. No claims are invented about that continuation.

## Source exception and false-positive audit

1. **Shall versus will (p. 195):** The traditional table prescribing which person takes shall or will is explicitly rejected by the source and recorded as **stylistic_or_prescriptive**, never as an error. First-person will is normal and more frequent than shall. The frequency of shall depends on register and dialect; a small set of archaic legal and interrogative forms must be allowed rather than generalized.
2. **Had better/dare (p. 196):** Had better is semantically stronger than should yet generally less imposing as an interpersonal act than must. Its modal evaluation is present-oriented. The ordinary negative has internal scope, with two attested positions of not. Auxiliary dare describes the courage of the participant, and negative declarative dare normally involves external negation. Lexical dare must not be confused with auxiliary dare.
3. **Past actualisation (p. 197):** Could is valid for past deontic permission, ability, circumstances, habitual states and ongoing perception. **OTH-439** specifies the narrow excluded case: a *positive, one-off, perfectively completed achievement* asserted using past-time could. The detector must distinguish that meaning before flagging; it remains **spec_only**. Past volitional would exhibits a related limitation but is retained as descriptive rather than as an active error. Negatives and habitual/ongoing contexts are explicit guards.
4. **Emotive and narrative would (p. 198):** Stressed WOULD can refer to a singular irritating completed occurrence, unlike stressed propensity will, which is habitual. Narrative future-in-past would ordinarily implies later occurrence; other uses of would may be modal-remote or backshifted without actualisation. Backshift collapses the surface contrast between some open and remote conditionals, while were to may disambiguate.
5. **Remote conditional (p. 199):** A modal-remote consequent normally needs a modal auxiliary (**OTH-453**); open conditionals do not. Simply finding the preterite after if does **not** establish remote status: backshift, ordinary past conditionals, and valid open if-clauses must be guarded. CGEL treats would as retaining the semantic contribution of will rather than as a purely empty counterfactual marker.
6. **Wish and tentative modals (p. 200):** A finite wish complement for an unreal desired state selects the preterite (**OTH-458**, **spec_only**), but hope, wish to, and alternative complements are not targeted. Could you and might I are pragmatic politeness variants, not corrections to grammatical can you or may I. Speaker differences in may versus might likelihood cannot be forced into universal grammar constraints.
7. **Would and special might/could (p. 201):** I would suggest can perform the act immediately, despite its preterite modal. Would like with prospective infinitival complements can express one individual future wish; bare like often denotes recurrent preference. Would seem/appear contains two hedges, not a doubled-error sequence. Open if-clauses can contain independent remote would. Might/could have presents unrealised risks, not just a tentative inference.
8. **Dialect/idiomaticity (p. 202):** Some speakers allow may in remote and backshift contexts; the source explicitly distinguishes Dialect A (may rejected) from Dialect B (may accepted and distinct from might). **OTH-479** and **OTH-482** are variety-restricted and must **never** support cross-variety false positives. Should is preterite by structural evidence from backshift and conditional constructions but its advice/probability senses are idiomatic, not mechanically derived from shall. The source's factor explanation is incomplete at this batch boundary.

## Rule and engineering accounting

- **70** new atomic rule records: **OTH-414–OTH-483**, comprising **54 classifications**, **10 descriptive generalizations**, **3 constraints**, **2 variety-restricted statements**, and **1 stylistic/prescriptive report**.
- **140 initial original correct sentences**, plus **6 additional guarded/exception correct sentences** for the constraints, and **6 original incorrect sentences** (two for each constraint); **6 narrowly paired corrections**. No book examples copied into the catalog.
- **3** diagnostic specifications only: OTH-439 (affirmative single-event perfective past *could*), OTH-453 (missing auxiliary in a real remote apodosis), OTH-458 (non-remote finite wish complement). All three remain **spec_only** and contain negative tests for valid variants.
- New runtime detectors: **0**. New measured error detection precision/recall: **none**. No new end-user lesson/quiz activation claimed.
- Burton-Roberts mapping stays explicitly **unverified**; no invented crosswalk.
- **Chapter 3:** 129 extracted of 142 pages; 3 justified contents-only skips and **10 unprocessed (203–212)**.
- **Book-wide:** **129 extracted**, **1,620 unprocessed**, 13 justified skips, 2 absent from source split; total printed pages 1,764.
- **Total catalog:** **769 rules**.
- **Next batch:** Chapter 3 printed **203–210** (complete §9.8.4 continuation and subsequent sections).

## Validation method

Incremental tests enforce contiguous unique IDs, valid JSON Schema records, correct printed/PDF-page provenance, ledger-to-report evidence, original example origin, three diagnostic blocks with minimal pairs and false-positive guards, and honest incomplete-coverage counters. The GitHub CI workflow also runs the existing SynTutor server, XAI contract, browser and parser suites. Chapter-wide mandatory completion gates are not asserted while pp. 203–212 remain unprocessed.
