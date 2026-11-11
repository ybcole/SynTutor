# Cambridge Chapter 3 — Phase C typed-evidence candidate probe

**Date:** 11 November 2026  
**Status:** Technical candidate checker and regression fixtures, **not a production grammar detector**.  
**Source:** *The Cambridge Grammar of the English Language*, Chapter 3, printed pp. 93–94, 105–107. Original English examples and exceptions are in the cited source-linked rule records.

## Implemented technical slice

`server/cgel_ch03_candidate_probe.py` introduces `probe_ch03(sentence, typed_facts, variety=...)`, a deliberately limited checker that consumes **explicitly typed auxiliary-selection candidates**, not a raw sentence as sufficient grammatical evidence.

| Primary candidate ID | Printed pages | Tested construction | Important guards |
|---|---|---|---|
| `COMP-034` | 106 | Central modal selecting an inflected 3sg present verb or an unlicensed infinitival *to* | Plain-form complements; *ought to* and lexical *need*; uncertain part-of-speech or inflection; unreliable selection evidence |
| `COMP-031` | 105, 107 | Two central modals directly selecting one another in an uncoordinated standard-English auxiliary chain | Double-modal English dialects; coordinated modals; lexical *can* as in *may can peaches*; opaque/non-direct dependencies |
| `CLS-100` with `COMP-030` as linked support | 93–94; 105 | Supportive *do* selecting another auxiliary in an ordinary finite clause | Lexical *have*, negative and emphatic imperatives, wrong clause or argument structure |

`CLS-100` and `COMP-030` concern an overlapping *do*-support restriction, and are **one candidate finding**, not two independent errors. More complex contextual semantic constraints, such as `OTH-102` and modal-remote `CLS-119/OTH-453`, are not turned into heuristics by this slice.

Each candidate is keyed to the source rule ID, with source-printed pages, a rule-derived **provisional** learner explanation, governor and dependent token positions, exact character spans, and optional **non-applicable edit hints** for an isolated modal-selection form. Both `requires_reparse` and `safe_to_apply_automatically: false` are explicit on edit hints. No edited paragraph is produced.

## Fail-closed conditions

- A raw sentence by itself **cannot** trigger a candidate. The caller must supply structured, explicitly typed relationships (`direct_selection=true`, `same_clause=true`, `coordinated=false`) with specified categories and forms.
- Nonstandard or unselected varieties are **not evaluated** by this Standard English probe. Unclear/invalid relations, out-of-range token indices, wrong sentence bindings and mismatched clause structures do not produce a candidate.
- The typed relations are not themselves *verified syntactic evidence*. The real canonical Burton-Roberts and XAI-2 facts currently do not independently license every necessary lexical head, auxiliary function or direct-selection relation. Arbitrary callers cannot use these candidate results as proof of a grammatical error.
- Results are explicitly marked `candidate_only`, `production_enabled=false`, `whole_sentence_certified=false`, and each candidate `needs_linguistic_validation`.
- The existing `server/cambridge_registry.py` and its `grammar/runtime_registry.json` remain unchanged: **zero Cambridge runtime rules enabled**. The source `diagnostic.detector` fields remain `spec_only`; no forged independent review, owner signature or Burton-Roberts crosswalk. No new API response, XAI error verdict, UI behavior or student-facing correction is claimed.

## Test evidence

`server/test_cgel_ch03_candidate_probe.py` is wired into `.github/workflows/syntax-generator-tests.yml` to exercise:

1. Synthetically typed positive cases for modal + nonplain form, double modals, and redundant supportive do.
2. True negative cases for ordinary modal selection, lexical *have*, lexical *can*, *ought to*, negative/emphatic imperatives and coordinated structures.
3. Explicit English variety restriction for a dialectal double-modal construction.
4. Duplicate relationship suppression (`CLS-100` / `COMP-030`), exact spans and nonautomatic edit hints.
5. Malformed/unsupported relations, unselected variety, missing evidence and mismatched sentence fail-closed behavior.
6. Multiple independent candidates with an explicitly **uncertified** whole sentence.
7. The production Cambridge runtime allow-list remains empty.

These are synthetic engineering probes, **not a held-out accuracy evaluation**. The prior 277-case Chapter 3 candidate corpus remains development-only; no precision/recall score is attributed to this change.

## Outstanding Phase C/D gates

1. Build a validated, parser- and source-grounded typed auxiliary-relation extractor. The current XAI-2 fact graph can observe constituency, but its head/function labels remain unlicensed and must not be silently promoted.
2. Independently verify each Cambridge rule against its page and resolve its explicit Burton-Roberts crosswalk. Do not equate automated schema QA with source or runtime approval.
3. Complete positive, negative, exception, dialect and adversarial tests on actually generated parser facts. Extend the held-out corpus to its specified per-family minimum and adjudicate the labels.
4. Only then connect enabled, checked constraints to the runtime registry, XAI finding lineage, bounded correction and full-paragraph reparsing with overlap/dependency handling.
5. Complete the remaining Chapter 3 constraint implementations before calling its Phase C complete. Continue the remaining 19 CGEL chapters under the master plan.

**Milestone conclusion:** A *provisional, typed-evidence* engine for three primary Chapter 3 auxiliary constraints exists and is regression-tested. **Zero live detectors are activated and Phase C is still incomplete.**
