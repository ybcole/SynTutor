# Source authority matrix — SynTutor

**Decision record:** Milestone 01  
**Effective for the roadmap:** after the Milestone 01 approval gate, under the project owner's standing automatic approval  
**Status:** Adopted target authority boundary; unresolved source mappings remain unresolved. **10 November 2026 update:** B–R Third Edition (2011) identity is verified; the [XAI-PRE source ledger](../grammar/xai_pre/source_audit.json) provides targeted Cambridge/B–R terminology checks without activating runtime rules.

## Authority by responsibility

| Source/system | May determine | Must not determine | Runtime / review condition |
|---|---|---|---|
| Noel Burton-Roberts, *Analysing Sentences: An Introduction to English Syntax* | Target phrase-marker representation; chapter-specific tree labels, hierarchy, features, triangles, gaps, indices, movement conventions, structural method, B-R curriculum progression. | Cambridge-wide grammatical claims where Cambridge uses a different analysis; parser output cannot override book conventions. | Tree conventions and learner-facing structural claims require the correct edition/chapter/page and appropriate source evidence. B–R Third Edition is confirmed by the 2026-11-08 split-source manifest and the supplied complete book; individual phrase-marker claims still require source/scope review. |
| *The Cambridge Grammar of the English Language* | Broader grammatical categories, constructions, constraints, conditions, exceptions, variety/register restrictions, descriptive generalisations, and grammatical explanatory evidence. | B-R target tree shape; a Cambridge record must not be translated to a B-R node/label without a verified crosswalk. Descriptive/classification/stylistic records must not become automatic errors. | Current human-approved records have not undergone the independent second pass described by the extraction protocol; their B-R mappings are unverified. Do not treat them as executable error rules solely because their status says `APPROVED`. |
| Benepar / spaCy | Candidate tokenisation, POS and constituency parse; diagnostic raw parser output and confidence/fallback signals. | Linguistic authority, B-R canonical tree authority, rule correctness, or final learner verdict. Do not merely relabel Penn-style nodes as B-R nodes. | Keep candidate parse separate. Only defensible, tested adapter transformations may enter canonical output; otherwise return unresolved/rejected/alternative. |
| Existing `server/matrix.py`, `server/ruleset.py`, `server/licensing.py` | Existing product behaviour and regression baseline; reusable checks after individual rule/source review. | Independent source authority or automatic truth for every Cambridge/B-R analysis. | Treat as legacy implementation to inventory and compare. Do not silently promote its rule set to the new runtime registry. |
| CoLA acceptability classifier | Optional secondary acceptability signal that can trigger review/unverified status. | Inventing a grammar rule, explaining a violation, or overriding explicit verified linguistic evidence. | Advisory only; keep its signal distinguishable from deterministic structural/rule findings. |
| Explanation templates / optional LLM drafting | Express verified B-R structural evidence or Cambridge rule evidence in readable prose; produce paraphrases and original examples within controlled review. | Decide grammaticality, infer an unrecorded exception, invent a source page, or settle a conflicting analysis. | Only compose from validated analysis facts and approved source references. Missing/uncertain evidence must produce an explicit unresolved or no-source-basis state. |
| Application progress and assessment data | Record versioned learner activity and evidence for progress. | Define linguistic correctness or grant arbitrary client-declared XP as authoritative. | Use stable content/version IDs; later progression work must use protected, idempotent server-side award logic. |

## Cambridge rule-type handling

The existing grammar schema distinguishes these rule types. This matrix preserves their distinct intended uses:

| `rule_type` | Permitted instructional use | Permitted error-detection use |
|---|---|---|
| `constraint` | Explain the stated condition, violation, exceptions, and examples. | Candidate only after independent source review, scope/variety/exception representation, crosswalk status, deterministic implementation, and passing tests. |
| `variety_restricted` | Explain the variety/register explicitly named by the record. | Only when the assessment/request names or otherwise establishes the relevant variety/register and all restrictions are encoded and tested. |
| `descriptive_generalization` | Teach what is typical, frequent, or characteristic, including qualifications. | Never treat the generalisation alone as a prohibition. |
| `classification` | Teach category labels, distinctions, and analyses. | Not an error rule by itself. |
| `stylistic_or_prescriptive` | Explain the stylistic or prescriptive status and distinguish it from grammaticality. | Never convert it into a grammatical error solely on that basis. |

A schema status of `APPROVED` is not equivalent to independent second-pass review, B-R mapping verification, implementation, or test approval. Runtime eligibility is a separate decision.

## Source and evidence lifecycle

A source-derived rule or structural claim must preserve, as applicable:

1. Source identity and edition/bibliographic metadata.
2. Chapter and section.
3. Printed page number(s); PDF page number(s) separately where known.
4. Extracted/paraphrased content and example provenance.
5. Extraction/review/human approval state.
6. B-R mapping relation and its review evidence.
7. Runtime implementation state and the version of the code/rule evaluator.
8. Test/fixture evidence and any limitations or exceptions.

The Cambridge extraction protocol's lifecycle distinguishes extraction, independent second-pass review, and human approval. SynTutor must additionally track cross-framework mapping and runtime eligibility independently. A record may be human-approved while awaiting independent review; it remains non-executable until every required gate is met.

## Unresolved authority and source issues

- The exact B-R edition/page mapping is not confirmed because the source PDFs were not present in the audited repository.
- The exact Cambridge edition/year/ISBN is not present in the inspected extraction metadata.
- All 196 active Cambridge rule records have B-R mappings marked `unverified`.
- Independent second-pass review is outstanding across the supplied Cambridge extraction reports.
- Chapter 2 conflict notes identify several possible terminology/analysis divergences between Cambridge and B-R, but the missing B-R comparison material prevents treating these as verified non-equivalences.
- B-R chapter-specific convention profiles V1–V10 and the V10 + Chapter 7 appendix refinement are documented in `CONVENTIONS.md`; they are the current project convention baseline pending bibliographic confirmation.

