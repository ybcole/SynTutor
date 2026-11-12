# CGEL accelerated Phase B runbook — source fidelity first

**Binding authority:** `docs/planning/CAMBRIDGE_FULL_COVERAGE_MASTER_PLAN.md` §0, §§3–9.  
**Scope:** all 20 Cambridge chapters; **no changes** to B-R syntax-tree authority, XAI proof policy, user English-only policy, source citation quality, independent approval, detector eligibility, or measured performance requirements.

## Current execution checkpoint — 2026-11-12

Chapter 15 is source-extracted through printed p. 1362: **88 substantive pages, 2 documented contents-only skips, no unprocessed pages**. The next Phase B priority is **Chapter 17, printed pp. 1449–1564**, beginning with its contents pages and the first substantive text. Earlier Chapter 4 through Chapter 15 quick-starts below are historical scaffolding only; do not restart their completed source extraction. Follow the master plan §0 adaptive source-audit requirements, preserve all QA gates, and use the current coverage ledger rather than snapshot counts.

---

## Historical Chapter 4 quick-start (completed)

**Next chapter:** Chapter 4, *The clause: complements*, **printed pp. 213–322**. Chapter 3 printed pp. 71–212 are already fully accounted for as **139 extracted + three contents-only skips**, while **1,610 full-book pages remain unprocessed**. Do not redo Chapter 3 extraction or postpone Chapter 4 for additional speculative Phase C prototypes.

For Chapter 4, start with **pp. 213–252** as a **tentative** 40-page batch. If tables, diagrams, complex footnotes, unclear text or exceptions make this too dense, split into shorter consecutive sections without skipping any pages. Subsequent tentative ranges are 253–292 and 293–322; adjust boundaries to actual section limits. The chapter's final printed p. 322 is already justified as textless in the split/full-source ledger; **confirm source status** and preserve the skip, not an invented rule.

Prefer one feature branch and a single fully CI-tested PR for the completed chapter; create internal verified commits per batch. **Both existing GitHub Actions workflows must pass on the final PR head before merging**.

### One-time scaffold command per batch

```bash
python tools/cgel_batch_gate.py --scaffold \
  --chapter 4 --start 213 --end 252 \
  --report sources/cambridge/chapter_04/PP213_252_REPORT.md \
  --output sources/cambridge/chapter_04/PP213_252_AUDIT.json
```

The generated file **deliberately fails validation** until actual page reading is documented. An example completed manifest shape:

```json
{
  "manifest_version": 1,
  "chapter": 4,
  "printed_start": 213,
  "printed_end": 213,
  "report": "sources/cambridge/chapter_04/PP213_213_REPORT.md",
  "source_pdf_page_offset": 20,
  "source_anchor": {"printed_page": 213, "pdf_page": 233},
  "added_rule_ids": ["COMP-123"],
  "page_checks": [{
    "page": 213,
    "status": "extracted",
    "section": "ACTUAL printed section heading; do not guess",
    "summary": "SOURCE-CHECKED paraphrase of this page, written after reading it",
    "source_checked": true,
    "nonprose_present": true,
    "layout_checked": true,
    "exceptions_checked": true,
    "unresolved_items": []
  }]
}
```

**The JSON above is a FORMAT ILLUSTRATION, not an extracted rule or source claim.** The example invented rule ID and example heading must NEVER be committed as evidence. The source full-volume mapping **printed p + 20 = one-based PDF page** was used for Chapter 3; verify actual first/last PDF labels and edition for Chapter 4 before retaining offset 20. Use one full contiguous range in the real audit and list **every** printed page, including documented skips.

### What to do for each actual page

1. Read the page text and visually inspect tables/figures/footnotes and any extraction anomalies. Record actual section, a short substantive content summary, whether there is nonprose content, and whether its layout was checked.
2. Capture grammatical categories, genuinely error-capable constraints, correct and incorrect contrast sets, rare exceptions and dialect/register distinctions as separate atomic English records. Keep their scope precise and exceptions cited. Do **not** convert an adjective of frequency, Cambridge's rejected traditional analyses, a stylistic tendency, or a legitimate dialect into a universal error rule.
3. Every new constraint has ≥2 original correct cases, ≥2 original incorrect cases, repaired minimal pairs, documented false-positive guards, a diagnostic **`spec_only`** and strict variety scope. Descriptive records need ≥2 original valid/contrast examples but **must not invent incorrect cases or enable a detector**.
4. A page is `extracted` only when all source content needed for the goal has been handled; report genuine uncertainty and **leave that page unprocessed** until resolved. Never mark a future page or an unavailable/textless page extracted. A status of `skipped_with_reason` is for genuinely non-expository or textless content after checking, not to speed up work.
5. Update `grammar/coverage/cgel_ledger.json` so each extracted page has its batch `report` as evidence, then populate the audit manifest, `added_rule_ids`, verified source page offset and anchor. The agent's `source_checked` field records work done; it does not establish independent linguistic approval.

### Fast batch verification (no quality reduction)

```bash
python tools/cgel_batch_gate.py --manifest sources/cambridge/chapter_04/PP213_252_AUDIT.json
python tools/validate_cgel_rules.py
python tools/ledger.py check --allow-unprocessed
python -m unittest discover -v -s tools -p 'test_cgel_phase_b*.py' -t .
python -m unittest -v tools.test_cgel_batch_gate
```

Check every message, not merely process exit code; repair any failure before the next batch. The range script verifies exact ledger page statuses, existing report paths, first-page anchor and per-rule printed/PDF citations, source-check and layout assertions, unresolved content, stable unique rule IDs, source-bound correct/incorrect examples, false-positive guards, unverified crosswalks and nonactivation. **Mechanical validation cannot certify grammatical truth**; rereread all high-risk source claims independently.

### Fast chapter PR verification

```bash
python tools/cgel_batch_gate.py --all
python tools/validate_cgel_rules.py
python tools/ledger.py check --allow-unprocessed
python tools/ledger.py check --chapter 4
```

The first command **auto-discovers** `sources/cambridge/chapter_*/PP*_AUDIT.json` and fails if any newly extracted non-Chapter-3 page lacks a manifest. The existing Chapter 3 extraction predates this structured manifest format and retains its original per-page source reports and regression suites. The chapter check must have **zero unprocessed pages** before claiming Chapter 4 source extraction complete.

When the source pages and ledger are complete, open a chapter PR and require success from **both**:

- `Syntax Generator model-free checks`: all legacy and new Cambridge tests (via automatic discovery), source/ledger/schema, B-R, XAI, corrections, database and Chromium browser checks.
- `Syntax Generator parser-backed runtime checks`: full real-parser, baseline, B-R/XAI and browser regressions.

Do not remove or downgrade existing CI checks to accelerate a PR. Instead, **reduce the number of PRs**, write one concise chapter report and let the batch gate handle repetitive evidence accounting.

## Distinguish four completion levels

| Status | What can truthfully be claimed |
|---|---|
| Source-extracted | Every printed page accounted for with grounded source records and exceptions |
| Structurally QA-checked | Schema, cross-domain source inventory, per-page audit, no missing references, standard negative guards |
| Detector-ready | Independently verified grammar constraints and source-to-B-R crosswalk, real typed relations, adversarial and held-out tests, registered and enabled per safe registry gate |
| End-to-end XAI-ready | Actual selected tree spans, source-linked learner explanations, grouped errors, bounded edits, repeated reparsing, corrected-paragraph output and no whole-sentence certification from partial coverage |

**No amount of batch automation substitutes for linguistic evidence or for the last two production gates.**

## Work cadence and stopping rules

Process the entire current batch and its gate autonomously, fix failures, commit it and continue through the chapter. No review/approval prompts to the user. If source information is inaccessible or unsafe to infer, record the exact page/figure and blocker; never manufacture extraction. In each user turn, complete the most work actually possible and disclose any remaining blocker or incomplete PR. Future work does not run while the chat is closed.


## Rolling checkpoint 2026-11-11

The dense opening of Chapter 4 was split to 213–232; source audit and 19 inactive grammar records are in `sources/cambridge/chapter_04/PP213_232_AUDIT.json` and `sources/cambridge/chapter_04/PP213_232_REPORT.md`. Complete pp.233–252 next, then continue through p.322 before final chapter PR/CI merge. Do not treat source review as independent reviewer approval.


## Chapter 4 second checkpoint (2026-11-11)

Printed pp.233–252 audited consecutively; all are substantive pages. 22 additional inactive records and crosschecks in `sources/cambridge/chapter_04/PP233_252_REPORT.md` and `sources/cambridge/chapter_04/PP233_252_AUDIT.json`. Chapter 4 now has 38 extracted pages and two contents-only skips, leaving 69 unprocessed and one preexisting textless skip. Continue at p.253; do not merge until the rest of Chapter 4 is validated and both full CI workflows are green.


## Chapter 4 checkpoint 253–272 (2026-11-11)

Source checked all 20 printed pages in sources/cambridge/chapter_04/PP253_272_REPORT.md with machine audit sources/cambridge/chapter_04/PP253_272_AUDIT.json; 37 new inert Chapter 4 records. Continue printed 273–292 on the same PR before chapter-close QA.


## Rolling Chapter 4 checkpoint — 2026-11-11

Completed internal audited batch printed pp.273–292; report sources/cambridge/chapter_04/PP273_292_REPORT.md, audit sources/cambridge/chapter_04/PP273_292_AUDIT.json, 41 newly documented inactive grammar principles. Continue printed p.293, then close Chapter 4 only after complete page and exception coverage and both full CI workflows passing.


## Ch4 checkpoint — pp.293–307 (2026-11-11)

Source-audited 15 consecutive pages on the chapter branch. Report sources/cambridge/chapter_04/PP293_307_REPORT.md and machine-audit sources/cambridge/chapter_04/PP293_307_AUDIT.json; 35 new English-only inert records. Remaining 308–321 and textless p.322; review gate and chapter CI required before merging.


## Chapter 4 source extraction closed, 2026-11-11

Printed 213–321 and blank 322 accounted for. Chapter 4 107 extracted substantive pages, 3 justified skips, zero unprocessed. This last batch source audit: sources/cambridge/chapter_04/PP308_321_REPORT.md, manifest: sources/cambridge/chapter_04/PP308_321_AUDIT.json, 39 new records. Close the draft PR only after both GitHub CI workflows and batch/ledger/schema gates pass. New rules stay NEEDS_REVIEW and runtime activation remains blocked. Next extraction priority: chapters with remaining unprocessed pages.


## Chapter 5 first checkpoint — 2026-11-11

Chapter 5 pp.323–340 inspected (contents-only 323–325, expository 326–340), with 28 inert grammar records. Report sources/cambridge/chapter_05/PP323_340_REPORT.md; audit sources/cambridge/chapter_05/PP323_340_AUDIT.json. The next checkpoint covers printed pp.341–348. Independent linguistic QA remains separate from Phase B.


## Chapter 5 second checkpoint (2026-11-11)

Printed pp.341–348 checked against text and page layouts. The batch adds 24 records (`PHR-048`–`PHR-071`) for plural-only nouns, invariant count forms, and sense-dependent agreement. The next checkpoint covers printed pp.349–358. The chapter remains on its rolling draft PR.


## Chapter 5 third checkpoint (2026-11-11)

Printed pp.349–358 checked in text and rendered layout. The 32 original-example records (`PHR-072`–`PHR-103`) cover number transparency, number selection and agreement, the determiner function, and the introduction to quantification. The next checkpoint covers printed pp.359–382.


## Chapter 5 fourth checkpoint (2026-11-11)

Printed pp.359–382 checked against text and rendered pages as a 24-page accelerated batch. Added 43 original-example records (`PHR-104`–`PHR-146`). The next checkpoint covers printed pp.383–406.


## Chapter 5 fifth checkpoint (2026-11-11)

Printed pp.383–406 checked against text and rendered pages as a 24-page batch. Added 44 original-example records (`PHR-147`–`PHR-190`). The next checkpoint covers printed pp.407–430.


## Chapter 5 sixth checkpoint (2026-11-11)

Printed pp.407–430 checked against text and rendered pages as a 24-page batch. Added 44 original-example records (`PHR-191`–`PHR-234`). The next checkpoint covers printed pp.431–454.


## Chapter 5 seventh checkpoint (2026-11-11)

Printed pp.431–454 checked against text and rendered pages as a 24-page batch. Added 43 original-example records (`PHR-235`–`PHR-277`). The next checkpoint covers printed pp.455–478.


## Chapter 5 eighth checkpoint (2026-11-11)

Printed pp.455–478 checked against text and rendered pages as a 24-page batch. Added 38 original-example records (`PHR-278`–`PHR-315`). The next checkpoint covers printed pp.479–502.


## Chapter 5 ninth checkpoint (2026-11-11)

Printed pp.479–502 checked in text and rendered layout. Added 30 original-example records (`PHR-316`–`PHR-345`). The final checkpoint covers pp.503–524.


## Chapter 5 source extraction complete (2026-11-11)

The final batch adds 26 records (`PHR-346`–`PHR-371`) for pp.503–523 and confirms that full-volume PDF p.544, corresponding to printed p.524, is blank. Chapter 5 has 198 substantive pages extracted, three contents-only skips, one verified split-source exclusion, and zero unprocessed pages. Phase B next proceeds to Chapter 7 under the priority sequence in the master plan.


## Chapter 7 first checkpoint (2026-11-11)

Printed pp.597–617 checked in text and rendered layout. Page 597 contains the chapter title and contents only. The 20 substantive pages yielded 28 records (`PHR-372`–`PHR-399`). Continue at p.618 with idiomatic and fossilised expressions.


## Chapter 7 second checkpoint (2026-11-11)

Printed pp.618–634 yielded 24 records (`PHR-400`–`PHR-423`). Continue at p.635 with the end of PP preposing and the start of PP complementation.

## Chapter 7 source extraction complete (2026-11-11)

The final accelerated batch covers 27 substantive pages, printed pp.635–661, and verifies that p.662 is blank. It adds 35 records (`PHR-424`–`PHR-458`). Chapter 7 closes with 64 substantive pages, two justified skips and zero unprocessed pages. Chapter 10 is next in the master plan priority order.

## Chapter 10 first checkpoint (2026-11-11)

Printed pp. 851–878 account for 26 substantive pages and two contents pages. The 41 records (`CLS-121`–`CLS-161`) include five inactive constraint specifications. Continue at p. 879 with the final discussion of direction questions and the start of biased questions.

## Chapter 10 second checkpoint (2026-11-11)

Printed pp. 879–902 yielded 39 records (`CLS-162`–`CLS-200`), including three inactive constraint specifications. Chapter 10 has 50 substantive pages extracted and 43 pages unprocessed. Continue at p. 903 with interrogative words and phrases.

## Chapter 10 third checkpoint (2026-11-11)

Printed pp. 903–924 yielded 36 records (`CLS-201`–`CLS-236`), including four inactive constraint specifications. Chapter 10 has 72 substantive pages extracted and 21 pages unprocessed. Continue at p. 925 with the detailed imperative analysis.

## Chapter 10 source extraction complete (2026-11-11)

The final batch covers 21 substantive pages, printed pp. 925–945, and verifies blank p. 946. The 34 records (`CLS-237`–`CLS-270`) include two inactive constraint specifications. Chapter 10 closes with 93 substantive pages, three justified skips and zero unprocessed pages. Chapter 14 is next in the master plan priority order.

## Chapter 14 first checkpoint (2026-11-11)

Printed pp. 1171–1193 account for two contents pages and 21 substantive pages and yield 27 records (`CLS-271`–`CLS-297`), including two inactive constraint specifications. Continue at p. 1194 with simple catenative constructions.

## Chapter 14 second checkpoint (2026-11-11)

Printed pp. 1194–1209 yielded 23 records (`CLS-298`–`CLS-320`), including one inactive constraint specification. This shorter batch groups the dense raising and complementation diagnostics. Continue at p. 1210 with competing analyses of auxiliaries.

## Chapter 14 third checkpoint (2026-11-11)

Printed pp. 1210–1226 yielded 24 records (`CLS-321`–`CLS-344`), including one inactive constraint specification. The batch groups the competing auxiliary analyses and the framework for catenative classification. Continue at p. 1227 with the omissions note and Class 1 verbs.

## Chapter 14 fourth checkpoint (2026-11-11)

Printed pp. 1227–1245 yielded 29 records (`CLS-345`–`CLS-373`), including one inactive constraint specification. Continue at p. 1246 with the distribution of hollow clauses.

## Chapter 14 source extraction complete (2026-11-11)

Printed pp. 1246–1271 yielded 36 records (`CLS-374`–`CLS-409`), including two inactive constraint specifications. The final batch verifies that p. 1272 is blank. Chapter 14 closes with 99 substantive pages, three justified skips and zero unprocessed pages. Chapter 18 is next in the master plan priority order.

## Chapter 2 first checkpoint (2026-11-12)

Printed pp. 43–56 account for one contents page and 13 substantive pages. The batch adds 19 records (`CLS-410`–`CLS-428`). Continue at p. 57 with countability and adjective and adverb phrases.

## Chapter 2 source extraction complete (2026-11-12)

Printed pp. 57–69 yielded 21 records (`CLS-429`–`CLS-449`). The matching full-volume page for p. 70 is blank. Chapter 2 closes with 26 substantive pages and zero unprocessed pages. Chapter 6 is next in the master plan priority order.

## Chapter 6 first checkpoint (2026-11-12)

Printed pp. 525–542 yielded 21 records (`WCAT-036`–`WCAT-056`), including one inactive constraint specification. Continue at p. 543 with adjective complementation.

## Chapter 6 second checkpoint (2026-11-12)

Printed pp. 543–562 yielded 24 records (`WCAT-057`–`WCAT-080`), including one inactive constraint specification. Continue at p. 563 with the distribution of adverb modifiers.

## Chapter 6 third checkpoint (2026-11-12)

Printed pp. 563–582 yielded 22 records (`WCAT-081`–`WCAT-102`). Continue at p. 583 with adverbial modification of adjectives and adverbs.

## Chapter 6 source extraction complete (2026-11-12)

Printed pp. 583–595 yielded 18 records (`WCAT-103`–`WCAT-120`). Printed p. 596 is blank. Chapter 6 closes with 70 substantive pages and zero unprocessed pages. Chapter 8 is next in the master plan priority order.

## Chapter 8 first checkpoint

Printed pp. 663–683 yielded 29 classification records (`CLS-450`–`CLS-478`). Continue at p. 684 with locative realization and change of location.

## Chapter 8 second checkpoint

Printed pp. 684–702 yielded 32 classification records (`CLS-479`–`CLS-510`). Continue at p. 703 with bounding and non-bounding duration.

## Chapter 8 third checkpoint

Printed pp. 703–724 yielded 34 classification records (`CLS-511`–`CLS-544`). Continue at p. 725 with degree under negation and then cause and result.

## Chapter 8 fourth checkpoint

Printed pp. 725–738 yielded 24 classification records (`CLS-545`–`CLS-568`). Continue at p. 739 with open conditional constructions.

## Chapter 8 fifth checkpoint

Printed pp. 739–760 yielded 29 classification records (`CLS-569`–`CLS-597`). Continue at p. 761 with exhaustive conditionals.

## Chapter 8 source extraction complete

Printed pp. 761–784 yielded 29 classification records (`CLS-598`–`CLS-626`). Chapter 8 closes source extraction with 120 substantive pages, two contents-only skips and zero unprocessed pages. The next chapter in the priority order is Chapter 9.

## Chapter 9 first checkpoint

Printed pp. 785–805 yielded 29 classification records (`CLS-627`–`CLS-655`) across 20 substantive pages and one contents page. Continue at p. 806 with secondary and non-verbal negation.

## Chapter 9 second checkpoint

Printed pp. 806–821 yielded 29 classification records (`CLS-656`–`CLS-684`). Continue at p. 822 with polarity-sensitive items.

## Chapter 9 third checkpoint

Printed pp. 822–838 yielded 25 classification records (`CLS-685`–`CLS-709`). Continue at p. 839 with increased specificity of negation.

## Chapter 9 source extraction complete

Printed pp. 839–849 yielded 16 records (`CLS-710`–`CLS-725`). Printed p. 850 is blank. Chapter 9 closes with 64 substantive pages and zero unprocessed pages. The next chapter in the priority order is Chapter 11.

## Chapter 11 first checkpoint

Printed pp. 947–966 yielded 30 classification records (`CLS-726`–`CLS-755`). Continue at p. 967.

## Chapter 11 second checkpoint

Printed pp. 967–980 yielded 25 classification records (`CLS-756`–`CLS-780`). Continue at p. 981 with question- and answer-oriented interrogatives.

## Chapter 11 third checkpoint

Printed pp. 981–994 yielded 18 classification records (`CLS-781`–`CLS-798`). Continue at p. 995 with mandatives.

## Chapter 11 fourth checkpoint

Printed pp. 995–1010 yielded 21 classification records (`CLS-799`–`CLS-819`). Continue at p. 1011 with syntactic analysis and reported speech.

## Chapter 11 source extraction complete

Printed pp. 1011–1030 yielded 26 classification records (`CLS-820`–`CLS-845`). Chapter 11 closes source extraction with 82 substantive pages and two contents pages. Chapter 12 is next.

## Chapter 12 first checkpoint

Printed pp. 1031–1047 yielded 22 classification records (`CLS-846`–`CLS-867`). Continue at p. 1048 with who and which.

## Chapter 12 second checkpoint

Printed pp. 1048–1066 yielded 23 classification records (`CLS-868`–`CLS-890`). Continue at p. 1067 with infinitival relatives.

## Chapter 12 third checkpoint

Printed pp. 1067–1078 yielded 19 classification records (`CLS-891`–`CLS-909`). Continue at p. 1079 with unbounded dependencies.

## Chapter 12 source extraction complete

Printed pp. 1079–1096 yielded 21 classification records (`CLS-910`–`CLS-930`). Chapter 12 closes source extraction with 64 substantive pages and two contents pages. Chapter 15 is next in the priority order.

## Chapter 15 first checkpoint

Printed pp. 1273–1288 yielded 21 classification records (`CLS-931`–`CLS-951`). Continue at p. 1289 with coordinators and related linking items.

## Chapter 15 second checkpoint

Printed pp. 1289–1304 yielded 21 classification records (`CLS-952`–`CLS-972`). Continue at p. 1305 with both and either.

## Chapter 15 third checkpoint

Printed pp. 1305–1322 yielded 23 classification records (`CLS-973`–`CLS-995`). Continue at p. 1323 with conditions on coordination.

## Chapter 15 fourth checkpoint

Printed pp. 1323–1342 audited consecutively in text and rendered layout, including genitive comparison tables, footnote exceptions and the nonce-constituent tree. Added 41 inert English-only records (`CLS-996`–`CLS-1036`); 3 are spec-only constraints, not enabled. Continue at p. 1343; only 20 printed pages remain in Chapter 15. Independent linguistic review and chapter-wide CI remain outstanding.

## Chapter 15 Phase B source closure

Printed pp. 1343–1362 were checked against text, all rendered page layouts and the two syntax-tree diagrams; the batch adds 59 inert records (`CLS-1037`–`CLS-1095`). Chapter 15 printed pp. 1273–1362 are fully accounted for (88 substantive and 2 contents-only skips; zero unprocessed). The Chapter 15 draft PR remains subject to complete local/CI gates and independent source QA, with no newly enabled runtime rules. Next chapter in priority order: Chapter 17.

## Chapter 17 first checkpoint — 2026-11-12

Printed pp. 1449–1472 checked consecutively in uploaded full-volume PDF text and page layout. Two contents-only pages (1449–1450) are properly skipped. The 22 substantive pages (1451–1472) yield 62 inert, source-attributed original-example records (PHR-459–PHR-514 and CLS-1096–CLS-1101), one narrow spec-only reflexive constraint with explicit guards. Next begins at p. 1473. No runtime enablement, fabricated B-R crosswalk or independent source approval.
