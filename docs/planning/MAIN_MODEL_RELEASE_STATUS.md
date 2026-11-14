# Main Model Release Status

**Status:** ready for testing. Not a claim of independent linguistic certification.

## What works

- **193/193 implemented pilot rules** are enabled in the Cambridge runtime
  through an allow-listed Phase-C candidate set. They are owner-waived and
  AI-checked, not independently human-certified.
- **281/281 grammatical held-out sentences normalize** to a B-R tree.
- **0 false positives** on the 281 normalized grammatical held-out sentences.
- **45/45 ungrammatical held-out sentences have a tree**: 29 normalized,
  16 explicit working trees.
- Canonical tree, legacy diagnostics, candidate findings and unified findings
  all expose explicit authority/claim labels.
- Candidate XAI is node-mapped, correction is local, and production remains
  deterministic and fail-closed for non-enabled rules.

## Exact source-fixture compliance

`scripts/audit_final_d1_exact_fixtures.py` compares complete trees against the
transcribed chapter fixtures:

- 224 sentence-aligned IMG source fixtures;
- 195 normalized;
- **184 exact complete-tree matches (94.36%)**;
- 11 exact mismatches;
- 29 unresolved source fixtures.

This is source-fixture compliance, not independent free-sentence gold. The
11 mismatches and 29 unresolved fixtures remain explicit work.

## Validation

- 65 B-R/gold tests.
- 78 Cambridge/XAI/API tests.
- 0 Penn-label leaks in the catalog audit.
- `artifacts/cambridge-runtime-holdout.json`
- `artifacts/final-d1-exact-fixtures.json`
- `artifacts/final-d1-gold-report.json`

## Honest remaining items

1. Resolve the 29 unresolved source fixtures and 11 exact mismatches.
2. Author non-adapter free-sentence gold; current `br_final_d1_gold.json` is an
   adapter-derived baseline with owner-waiver provenance.
3. Complete the S/P/U integration workstreams that are not covered by the
   current tests.
4. Independent source/crosswalk QA was explicitly waived by the owner; no
   independent-certification claim may be made.
5. Lessons/quizzes are out of scope for this release.
