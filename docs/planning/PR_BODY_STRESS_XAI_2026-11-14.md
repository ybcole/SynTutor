# Repair B-R coverage, XAI explanations, and agreement scoping

## Summary

This PR closes the stress-test/XAI repair pass and the agreement false-positive
reported for `I and he saw the three thieves stealing the car whom was parked on
the wrong side`.

- B-R normalization now covers the remaining complex constructions and the
  former 29 unresolved source fixtures.
- Explanation coverage binds every error word, removes self-referential copy,
  and prevents words from being collapsed onto an enclosing C2.
- Corrections expose a re-parsed impact delta instead of claiming whole-sentence
  correctness from a single edit.
- Agreement rules inspect the clause predicate, not verbs inside relative or
  embedded clauses.
- Candidate grammar checks and "Why this is shown" dropdowns are removed from
  the learner panel.
- Test/CI policy now matches the owner-waiver runtime.

## Verification

| Gate | Result |
|---|---:|
| Full backend suite | **890 tests pass**, 45 skipped |
| Stress suite | **43/43 normalized**, 0 issues |
| Exact fixtures | **216/216 exact**, 0 unresolved |
| Held-out grammatical | **281/281 normalized** |
| Held-out ungrammatical | **45/45 with trees** |
| Explanation audits | 0 self-reference/duplicate failures |

Commands:

```bash
cd server
..\.venv\Scripts\python.exe -m unittest discover -p 'test_*.py'
cd ..
.venv/Scripts/python.exe scripts/stress_test_syntutor.py \
  --output artifacts/syntutor-stress-report.json
.venv/Scripts/python.exe scripts/audit_final_d1_exact_fixtures.py \
  --output artifacts/final-d1-exact-fixtures.json
.venv/Scripts/python.exe scripts/audit_learner_explanations.py
.venv/Scripts/python.exe scripts/audit_explanation_self_reference.py
node scripts/test_explanation_dedupe.js
node scripts/test_legacy_node_map.js
node scripts/test_explanation_evidence.js
node scripts/test_correction.js
node scripts/test_tree_layout.js
```

## Key changes

- `server/ruleset.py`: `_predicate_verb` scopes agreement to the clause
  predicate; coordinated/correlative/number rules no longer read relative-clause
  verbs.
- `server/final_d1_projection.py`: wh/relative/comparative/correlative
  projections and punctuation handling.
- `server/burton_roberts.py`, `server/br_tree.py`: clitic-aware source matching,
  Appendix-NOM profile fallback, ambiguity alternatives.
- `server/learner_explanations.py`: lexical wrappers, empty positions, and
  equal-surface context handling; branch and word explanations distinct.
- `web/js/explanation-dedupe.js`: structural-only duplicate collapse.
- `web/js/main.js`, `web/js/explanation-evidence.js`, `web/js/ui.js`: legend,
  correction impact, candidate-section removal.
- Tests: `server/test_agreement_scoping.py`, `server/test_explanation_coverage.py`,
  `scripts/test_explanation_dedupe.js`.

## Known limits

- No independent human review or non-adapter free-sentence gold.
- `whom` → `which` for inanimate antecedents is still not diagnosed; the
  agreement false positive on `was` is fixed.
- Some ungrammatical/garden-path strings are structurally normalized; the rule
  matrix still reports their grammar errors.
- No browser visual pass.

## Documentation

- `docs/planning/SYNTUTOR_STRESS_TEST_AND_XAI_2026-11-14.md`
- `docs/planning/HANDOFF_AI_CONTINUATION_2026-11-14.md`
- `docs/planning/MAIN_MODEL_RELEASE_STATUS.md`
- `docs/planning/MAIN_MODEL_GAP_LIST.md`
