# CGEL accelerated Phase B runbook — source fidelity first

**Binding authority:** `docs/planning/CAMBRIDGE_FULL_COVERAGE_MASTER_PLAN.md` §0, §§3–9.  
**Scope:** all 20 Cambridge chapters; **no changes** to B-R syntax-tree authority, XAI proof policy, user English-only policy, source citation quality, independent approval, detector eligibility, or measured performance requirements.

## Quick-start for the next execution

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

Printed pp.359–382 checked against text and rendered pages as a 24-page accelerated batch. Added 43 original-example records (`PHR-104`–`PHR-146`). Continue with §7.5 at printed p.383 on the same draft PR.
