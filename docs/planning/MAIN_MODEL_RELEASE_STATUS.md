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
- Word-level explanations are specific and non-self-referential. Duplicate
  copy is collapsed only for structural layers; words, triangles, gaps, empty
  positions, and lexical wrappers always keep their own explanation.
- Agreement findings inspect the clause predicate, not verbs inside relative or
  embedded clauses. Past-tense lexical and non-finite predicates are not used
  as number evidence, and correlative subjects project as coordinated NPs.
- Relative pronoun choice is diagnosed from antecedent animacy and the
  subject/object gap (`whom` → `which`, `which` → `who`/`whom`, subject `whom`
  → `who`), with an executable edit. A pronoun inside a relative clause is not
  treated as a prepositional object.

## Exact source-fixture compliance

`scripts/audit_final_d1_exact_fixtures.py` compares complete trees against the
transcribed chapter fixtures:

- 224 sentence-aligned IMG source fixtures;
- 216 complete-tree records after excluding 1 partial fragment, 6 intentionally
  incorrect lesson examples, and 1 legacy-label V2 lesson record;
- 216 normalized;
- **216 exact complete-tree matches (100%)**;
- 0 exact mismatches;
- 0 unresolved source fixtures.

This is source-fixture compliance, not independent free-sentence gold. The
legacy-label V2 lesson record remains a lesson example because a flat
`Sentence` tree cannot be a valid V2 reference (`S → NP VP`).

## Validation

- 65 B-R/gold tests.
- 104 Cambridge/XAI/API tests.
- 895 full backend tests pass (45 skipped).
- Explanation audits: **47 parser-backed sentences** plus **2,368 model-free
  lesson/gold nodes**; 0 self-reference or duplicate problems.
- 0 Penn-label leaks in the catalog audit.
- `artifacts/cambridge-runtime-holdout.json`
- `artifacts/final-d1-exact-fixtures.json`
- `artifacts/syntutor-stress-report.json`
- `artifacts/final-d1-gold-report.json`

## Honest remaining items

1. Author non-adapter free-sentence gold; current `br_final_d1_gold.json` is an
   adapter-derived baseline with owner-waiver provenance.
2. Complete the S/P/U integration workstreams that are not covered by the
   current tests.
3. Independent source/crosswalk QA was explicitly waived by the owner; no
   independent-certification claim may be made.
4. Lessons/quizzes are out of scope for this release.
