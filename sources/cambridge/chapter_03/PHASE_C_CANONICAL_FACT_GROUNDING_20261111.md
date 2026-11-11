# Chapter 3 Phase C — canonical-tree evidence grounding

**Date:** 11 November 2026  
**Source basis:** Cambridge, *The Cambridge Grammar of the English Language*, Chapter 3, printed **pp. 93–94, 105–107**, from source-linked records `CLS-100`, `COMP-030`, `COMP-031`, and `COMP-034`.  
**Status:** Verified technical *tree grounding*, **not** independent linguistic role verification, production activation, or completion of Chapter 3 Phase C.

## Implemented

Added `server/cgel_ch03_fact_bridge.py` with the function `probe_ch03_on_canonical(analysis, typed_facts, *, variety)`. This binds the prior candidate-only auxiliary checker to the existing `server/burton_roberts.py` canonical-tree validator and `server/xai_facts.py` XAI-2 fact graph.

For a candidate to be examined, all of these must be true:

1. The supplied analysis is **normalized** and the canonical B-R envelope passes validation. The tree has an exact sentence value, and the canonical tokens and character offsets match the unmodified sentence and the candidate probe tokenizer. Unresolved and provisional facts fail closed.
2. There is no unresolved alternate analysis or evidence-status uncertainty. Source and review annotations on a caller-supplied tree are **not** used to authorise grammar rules.
3. The candidate envelope binds to the **computed analysis ID**, actual tree ID and identical sentence, rather than a caller-supplied, unverified graph snapshot.
4. Each proposed auxiliary relation refers to two **overt terminal node IDs** occupying the exact proposed governor and dependent token positions. Opaque triangles cannot provide lexical head evidence.
5. The validated tree must visibly contain the appropriate B-R **category labels** for each stated candidate role: e.g. MOD for a proposed core modal, V for its overt lexical complement, AUX for supportive *do*, and PERF/PROG/PASS for typed aspectual auxiliary candidates. These are **observed categories only**, not independent certification of semantic role.
6. The two tokens must share an **overt VP constituent** and the same immediate clause ancestor. A B-R structural shape, direct-child relationship, or lexical category is never promoted by itself into an approved *direct selection* claim.
7. The existing candidate checker must still accept the typed relation and a **selected Standard English variety**. It continues to block a genuine lexical *have*, legitimate central-modal/plain-form combinations, nonstandard double-modal dialects, coordinated modals and negative/emphatic imperatives.

Outputs remain `candidate_only`, `production_enabled: false`, `whole_sentence_certified: false`, with `role_licensing: unverified`. A candidate has `status: tree_bound_relation_unverified`; its grounding contains computed `analysis_id`, observed token-terminal node IDs, labels, VP and clause IDs, and `head_and_selection_licensed: false`. Existing candidate-only edit hints remain non-applied and explicitly demand reparsing.

## Source and overlap policy

This milestone does not change Cambridge's grammatical distinctions or turn contextual tendencies into grammatical errors. The three provisional primary checks are:

| Primary source rule | Page(s) | Construction |
| --- | --- | --- |
| `COMP-034` | 106 | The plain-form requirement after a central modal in a core auxiliary chain; exclude special *ought to* and lexical-verb constructions |
| `COMP-031` | 105, 107 | Standard English core central-double-modal restriction; do **not** apply as an error verdict to dialects permitting ordered double modals |
| `CLS-100` with `COMP-030` cross-reference | 93–94, 105 | No redundant supportive *do* with an already available finite auxiliary, except special imperative and lexical-have readings |

`CLS-100` and `COMP-030` describe the same relevant supportive-`do` principle; the candidate checker emits **one primary finding with one supporting source ID**, not duplicated errors.

## Regression evidence

Added `server/test_cgel_ch03_fact_bridge.py`, registered in model-free GitHub Actions. Synthetic validated canonical-tree fixtures check exact source offsets, overt MOD/V/AUX/PROG categories, common clause/VP paths, wrong/fake terminal IDs, stale analysis/tree IDs, malformed role metadata, multiple varieties, normal auxiliary chains, provisional trees, unresolved alternatives, source-review flag forgery, and a **real existing course tree** whose opaque triangles must never be silently expanded into a lexical role.

Passing a canonical-tree validator **only proves the representation meets its structural contract**; the fixture builder is synthetic and intentionally does not represent an independently adjudicated grammar analysis of a malformed sentence. Tests are engineering invariants, not measured precision/recall or human review of grammar interpretations.

## Explicitly remaining

- A parser-backed, independent source-checked **head/function/selection** evidence extractor is still missing. The XAI-2 graph explicitly records `head_status: unknown_unlicensed` and `function_status: unknown_unlicensed`; this bridge **does not override them**.
- Many valid parser analyses contain opaque triangles, unresolved alternatives, or tokenisations that do not match the candidate tokenizer. These are deliberately **not evaluated**. This avoids false claims but limits candidate coverage.
- All Chapter 3 rule B-R crosswalks remain unverified, and all new Phase B constraints remain `spec_only`. The independent review and crosswalk gate must pass before putting any rule into the **empty** `grammar/runtime_registry.json` production allow-list.
- A true Phase C implementation must derive and validate grammatical relations from the real parser, test all source exceptions and varieties, publish adjudicated held-out precision/recall, and connect source-linked findings to XAI. Phase D still requires bounded, re-parsed **corrected paragraphs**; no whole-sentence grammar certification is claimed.

**Progress:** An analysis-ID-bound technical adapter and adversarial tests; **zero newly enabled Cambridge detectors**, **no new rules or pages extracted**, **Chapter 3 Phase C remains incomplete**.
