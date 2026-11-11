# Chapter 3 — Phase B source-page completion audit

**Audit date:** 2026-11-11  
**Book:** *The Cambridge Grammar of the English Language*, Chapter 3, "The verb"  
**Printed chapter span:** 71–212 inclusive (142 pages)  
**Status:** **Source-page inventory complete; independent linguistic QA and Phase C/D implementation remain pending.**

## Mechanically verified source inventory

| Status | Printed pages | Count |
|---|---|---:|
| Extracted | 74–212 | **139** |
| Skipped with explicit reason | 71–73 (chapter table of contents only) | **3** |
| Unprocessed | None | **0** |
| Unavailable from source | None for Chapter 3 | **0** |
| **Total** | **71–212** | **142** |

This is not the same as claiming that every possible grammatical distinction in the book has been independently re-audited, crosswalked with Burton-Roberts, or connected to live detection.

The source ledger `grammar/coverage/cgel_ledger.json` identifies a Markdown evidence path for **all 142** Chapter 3 pages. Source reports cover the initial p. 74–75 entry plus consecutive ranges **76–90, 91–114, 115–122, 123–130, 131–138, 139–146, 147–154, 155–162, 163–170, 171–178, 179–186, 187–194, 195–202, 203–210, and 211–212**. The first three pages are explicitly marked contents-only.

The initial source inventory starts at p. 74 because printed pp. 71–73 contain only the chapter opening contents. A reporting discrepancy between the printed book and split sources is not being silently filled with inferred rules.

## Rule catalog

Total catalog **887** records: **196 pre-Phase-B records** plus **691 records added during Chapter 3 Phase B**. The last source batch adds **32** records, OTH-570–OTH-601, each with explicit printed-page and PDF page provenance.

The last batch preserves distinctions that cannot safely be treated as automatic errors: formal versus colloquial reductions of *be going to*; present-evidence focus versus pure futurity *will*; distant intention versus immediate futurity; past *was going to* versus narrative *would* actualisation; and willingness/refusal versus intention. Examples are original English sentences, not copies from CGEL.

## Gates and remaining engineering work

**Source extraction gate (Phase B):** page inventory fully accounted for. The repository's existing schema, source citation and ledger gates and new chapter regression must pass in CI before merging.

**Independent linguistic QA:** still to be performed at the chapter level, including accuracy of exceptions, cross-reference completeness and suspected overly broad constraints. Existing `NEEDS_REVIEW` record status is a provenance lifecycle state, not a request for manual approval from the user. Subsequent work should be autonomous.

**Burton-Roberts crosswalk:** entries recorded as `unverified` where no direct crosswalk was established. Do not silently claim equivalence.

**Phase C:** existing `spec_only` constraints need source-specific deterministic/parsing implementations plus positive, negative and exception tests. No newly active detectors or measured precision/recall are claimed by Phase B extraction.

**Phase D:** corrected-paragraph output, interactive multi-error re-evaluation and explanation lineage must be verified separately.

**Phase E:** lessons and quizzes must be grounded in source-linked rule IDs and original examples.

**Next work under the master plan:** automated Chapter 3 independent QA and Phase C/D detection/XAI integration, **not** a claim that the 20-chapter reference is complete. Whole-book ledger remains **139 extracted, 1,610 unprocessed, 13 skips, 2 unavailable**.
