# SynTutor AI Continuation Handoff — 2026-11-14

**Purpose:** this document lets another AI (or engineer) continue SynTutor
without re-discovering the architecture, the recent fixes, the verification
commands, or the known gaps.

**Read this first:** the system is functionally working and fully tested, but it
is **not independently linguistically certified**. The owner waiver in the
runtime registry remains in force. Do not claim human-review certification.

## 1. Current state

- Repository: `https://github.com/ybcole/SynTutor`
- Base branch: `main`
- Base commit at handoff: `d94e024` (`Main model handoff and Phase C runtime/authority work (#171)`).
- This work is on a feature branch created from `d94e024`; merge it through a
  pull request before continuing on `main`.
- Worktree: clean only after the handoff commit; check `git status` first.

The branch completes the stress-test/XAI repair pass:

- B-R projection and fixture reconciliation.
- Explanation coverage, self-reference repair, and duplicate-explanation fix.
- Correction-impact reporting.
- Agreement-rule scoping repair.
- UI removal of candidate grammar checks and "Why this is shown" dropdowns.
- Test/CI reconciliation with the owner-waiver runtime.

## 2. Architecture at a glance

### Request flow

`web/js/main.js`
→ `POST /api/parse` (`server/api.py`)
→ `server/parse_engine.py` (spaCy + Benepar)
→ `server/matrix.py` + `server/ruleset.py` + `server/licensing.py`
→ `server/burton_roberts.py` / `server/final_d1_projection.py` / `server/br_tree.py`
→ `server/explanations.py` → `server/learner_explanations.py`
→ `server/corrections.py` → payload
→ browser renderers in `web/js/`.

### Main files

| Area | File | Role |
|---|---|---|
| API payload | `server/api.py` | `build_payload`, correction impact, transport payload |
| Parsing | `server/parse_engine.py` | spaCy + Benepar candidate tree |
| B-R canonicalization | `server/burton_roberts.py` | exact IMG gold lookup, normalization, validation |
| B-R projection | `server/final_d1_projection.py` | FINAL-D1 construction projection and working trees |
| B-R schema/helpers | `server/br_tree.py` | source records, tokens, validation, clitics |
| Grammar rules | `server/matrix.py`, `server/ruleset.py`, `server/licensing.py` | findings, agreement, licensing |
| Corrections | `server/corrections.py` | edit assembly, re-parse validation |
| Explanation evidence | `server/explanations.py` | fact graph, channels, XAI payload |
| Learner prose | `server/learner_explanations.py` | one plain-English paragraph per node |
| Canonical binding | `server/canonical_binding.py` | legacy findings → canonical node IDs |
| UI shell | `web/js/main.js` | tree rendering, selection, explanation dedupe |
| Evidence UI | `web/js/explanation-evidence.js` | paragraph + legacy diagnostic |
| Dedupe | `web/js/explanation-dedupe.js` | structural-only duplicate collapse |
| Legacy map | `web/js/legacy-node-map.js` | legacy detail → canonical node |
| Correction UI | `web/js/ui.js` | correction panel, impact delta |
| Builder | `web/js/syntax-builder.js` | editor round-trip; triangles may carry features |

### Data

- `web/content/book/ch01.trees.json` … `ch10.trees.json`: IMG-verified source
  trees used by the exact-gold lookup.
- `web/content/lessons/course.json`: lesson trees.
- `grammar/runtime_registry.json`: **193 owner-waived Cambridge rules**
  (`owner_waiver=true`, `independent_review=false`).
- `grammar/explanation_templates.json`: reviewed explanation templates.
- `evaluation/grammatical_sentences.json`: 281 held-out grammatical sentences.
- `evaluation/ungrammatical_sentences.json`: 45 held-out ungrammatical sentences.

## 3. Invariants and authority model

1. **Do not promote unverified material.** A B-R tree is normalized only from
   a validated source record or a licensed projection. Parser-only fallbacks are
   labelled provisional/working.
2. **The rule matrix and Cambridge candidates are separate authorities.** A
   candidate-only observation is never a grammar verdict.
3. **Every error word must have a node binding.** `canonical_binding.py` binds
   the flagged word and every remediation target; the UI assigns every
   `canonical_node_ids` entry.
4. **Corrections are re-parsed.** Never infer whole-sentence correctness from a
   single edit. `summary.correction.impact` reports resolved/remaining/
   introduced counts.
5. **Explanation dedupe is structural only.** Words, triangles, gaps, empty
   positions, and lexical wrappers always keep their own explanation. Only
   `S`, `NP`, `VP`, `NOM`, `PP`, `AP`, `AdvP`, `S-bar` layers may collapse onto
   an identical parent paragraph.
6. **Agreement rules inspect the clause predicate.** Past-tense lexical verbs
   and non-finite predicates are not number evidence; relative-clause verbs are
   never compared with the main subject.
7. **One paragraph per node.** `learner_explanations.py` must not emit
   self-referential copy ("X is part of the larger expression X"). Run the
   self-reference audit after changes.
8. **No UI candidate dropdown.** Candidate checks and "Why this is shown"
   dropdowns were removed from the learner panel. Keep candidate data in the
   payload for tooling, not as a verdict.

## 4. What this branch changed

### 4.1 B-R normalization and fixtures

- Clitic-aware `_atoms` (`John's`, `I'm`, `n't`) in `br_tree.py`.
- Chapter 7 Appendix-NOM profile fallback.
- Ambiguous exact-gold records select a deterministic primary and expose the
  other verified analyses in `accepted_alternatives` instead of returning
  `unresolved`.
- Legacy-label V2 `Sentence` records are lesson examples, not V2 references.
- Projection coverage added for: wh subject extraction, `that` relatives,
  subjectless SBAR gaps, bare finite verbs under `S`, VBN `PartP`, AP + `than`
  PP, negative lexical `do`, auxiliary + bare VP, adjectival `do` complements,
  correlative subjects (`Neither X nor I`), and final punctuation filtering.

Result: exact fixture audit **216/216 exact (100%)**, 0 unresolved. Held-out
audit: **281/281 grammatical normalized**, **45/45 ungrammatical have trees**.

### 4.2 Explanation coverage and dedupe

- `canonical_binding.py` binds all remediation targets and the flagged word.
- `legacy-node-map.js` assigns all `canonical_node_ids`.
- `main.js` highlights all bound token spans.
- `explanation-evidence.js` removed the candidate section and flattened the
  "Why this is shown" detail.
- `explanation-dedupe.js` collapses only structural layers. The reported
  "Same explanation as the enclosing C2 'Who'" regression is covered by
  `scripts/test_explanation_dedupe.js`.
- `learner_explanations.py` handles lexical wrappers, empty positions, and
  equal-surface contexts; branch and word explanations are distinct.

Audits:

- `scripts/audit_learner_explanations.py`: model-free, 2,368 lesson/gold nodes,
  0 self-reference or duplicate failures.
- `scripts/audit_explanation_self_reference.py`: parser-backed, 45 sentences,
  0 problems.

### 4.3 Correction impact

- `api.py` adds `summary.correction.impact` with re-parsed counts.
- `ui.js` shows "What this fix changes" in the preview and summary revision.
- Structured remediation added for `C-SUBJ-AGREE-XP`, `C-COORD-CASE`,
  `C-COORD-SUBJ-AGREE`, and `C-UNCOUNTABLE` (some via `matrix.py`).

### 4.4 Agreement scoping

- `ruleset.py::_predicate_verb(vp)` returns only the clause predicate head.
- `C-COORD-SUBJ-AGREE`, `C-CORRELATIVE-AGREE`, and `C-NUMBER-AGREE` use it.
- Past-tense lexical and non-finite predicates are skipped.
- `Neither the teacher nor I` now projects as a coordinated NP.

Regression: `server/test_agreement_scoping.py`.

### 4.5 Test/CI reconciliation

- `test_api_contract` restores module stubs at teardown.
- Builder accepts `features` on triangles.
- Policy tests assert the owner-waiver boundary rather than an empty registry.
- CI isolated job includes `test_explanation_coverage`,
  `test_agreement_scoping`, `test_relative_pronoun`, and
  `node scripts/test_explanation_dedupe.js`.

### 4.6 Relative pronoun choice and pronoun-case scoping

- `licensing.py::check_relatives` now chooses `who`/`whom`/`which` from the
  antecedent's animacy and the relative clause's subject/object gap, with an
  executable replacement edit.
- `HUMAN_ANTECEDENTS` / `NONHUMAN_ANTECEDENTS` were expanded; collective nouns
  (`committee`, `government`) stay unverified rather than being forced into one
  class.
- `matrix.py::_has_clause` prevents the preposition + object-pronoun rule from
  reading a pronoun inside a relative clause
  (`The students from several departments whom I met` is no longer flagged).
- Regression: `server/test_relative_pronoun.py`.

## 5. Verification

Run from the repository root unless noted.

```bash
# Full backend suite
cd server
..\.venv\Scripts\python.exe -m unittest discover -p 'test_*.py'

# Stress suite
.venv/Scripts/python.exe scripts/stress_test_syntutor.py \
  --output artifacts/syntutor-stress-report.json

# Exact fixtures
.venv/Scripts/python.exe scripts/audit_final_d1_exact_fixtures.py \
  --output artifacts/final-d1-exact-fixtures.json

# Held-out runtime
.venv/Scripts/python.exe scripts/audit_cambridge_runtime_holdout.py \
  --output artifacts/cambridge-runtime-holdout.json

# Explanation audits
.venv/Scripts/python.exe scripts/audit_learner_explanations.py
.venv/Scripts/python.exe scripts/audit_explanation_self_reference.py \
  --output artifacts/explanation-self-reference-audit.json

# UI contracts
node scripts/test_explanation_dedupe.js
node scripts/test_legacy_node_map.js
node scripts/test_explanation_evidence.js
node scripts/test_correction.js
node scripts/test_tree_layout.js
```

Current expected results:

| Gate | Result |
|---|---:|
| Full backend suite | **895 tests pass**, 45 skipped |
| Stress suite | **45/45 normalized**, 0 issues |
| Exact fixtures | **216/216 exact**, 0 unresolved |
| Held-out grammatical | **281/281 normalized** |
| Held-out ungrammatical | **45/45 with trees** |
| Explanation audits | 0 self-reference/duplicate failures |
| B-R/gold suites | 65 tests pass |
| Runtime/API/XAI suites | 104 tests pass |

## 6. Known gaps and next priorities

1. **No independent human review or non-adapter free-sentence gold.** The owner
   waiver covers the 193 runtime rules. Do not claim certification.
2. **Animacy knowledge is finite.** `check_relatives` now selects
   `who`/`whom`/`which` from the antecedent's animacy and the subject/object
   gap, so `the car whom was parked` is diagnosed as `which` with an executable
   edit. Unknown common nouns are deliberately left unverified rather than
   guessed; extend `HUMAN_ANTECEDENTS` / `NONHUMAN_ANTECEDENTS` when a
   domain-specific noun needs coverage.
3. **Lenient structural rules.** Nine garden-path/ungrammatical constructions
   were normalized with structural rules; the rule matrix still reports their
   grammar errors. Do not treat normalization as a grammaticality certificate.
4. **Explanation dedupe is lazy for structural layers.** A layer selected
   before its parent is not collapsed until the parent is selected. Words and
   lexical wrappers are never collapsed.
5. **No browser visual pass.** A Playwright/visual pass is still recommended.
6. **S/P/U integration workstreams** from the prior handoff remain open.
7. **Optional UX:** a `Full B-R` / `Learner view` toggle for `C1`/`C2` nodes
   and movement subscripts is recommended for beginners. Keep the canonical
   tree and API unchanged; hide only in presentation.

## 7. Environment notes

- Python: use `.venv\Scripts\python.exe` on Windows.
- spaCy/Benepar models are installed in the venv. First load prints T5/RoBERTa
  warnings; they are expected.
- `fastapi` is in `requirements-test.txt`; install it if ASGI transport tests
  error with `ModuleNotFoundError`.
- PowerShell may display curly quotes/subscripts as `?`; this is console
  encoding, not payload corruption. Use `PYTHONUTF8=1` when needed.
- The Builder/`dist` directory is generated by `node scripts/build.js`; `dist`
  is git-ignored.
- `git diff --check` must be clean before committing.

## 8. Where to start on common tasks

- **A false positive in a rule:** reproduce with `build_payload`, inspect
  `node_details` and the raw tree, then find the rule in `matrix.py`,
  `ruleset.py`, or `licensing.py`. Scope it to the clause/phrase it owns; do not
  scan across embedded clauses. Add a case to `server/test_agreement_scoping.py`
  or a focused test.
- **A missing B-R tree:** reproduce with `build_canonical_analysis(analyze(s))`,
  read `reasons`, inspect `final_d1_projection.py`, and add the narrowest
  licensed rule. Add the sentence to the stress suite.
- **A self-referential explanation:** check `learner_explanations.py` label
  coverage and `_larger_context`; run
  `scripts/audit_explanation_self_reference.py`.
- **A wrong/duplicated explanation in the browser:** check
  `explanation-dedupe.js` and `main.js` `select()`; add a case to
  `scripts/test_explanation_dedupe.js`.
- **A correction that breaks the sentence:** inspect
  `summary.correction.impact`; fix the remediation in `matrix.py` and add a
  test to `test_correction_offsets.py` or `test_agreement_scoping.py`.

## 9. PR / merge procedure

```bash
git checkout -b repair/stress-xai-final-2026-11-14
git add <intended files>
git commit -m "Repair B-R coverage, XAI explanations, and agreement scoping"
git push -u origin HEAD
gh pr create --base main --head repair/stress-xai-final-2026-11-14 \
  --title "Repair B-R coverage, XAI explanations, and agreement scoping" \
  --body-file docs/planning/PR_BODY_STRESS_XAI_2026-11-14.md
gh pr merge --merge --delete-branch
```

If `gh` is unavailable, install it (`winget install --id GitHub.cli`) or use the
GitHub REST API with a `GITHUB_TOKEN` that has `repo` scope.

## 10. Ownership and non-certification

- Owner waiver: the 193 enabled Cambridge rules are
  `owner_waived_unverified`; `independent_review=false`.
- The system is a **software acceptance** implementation, not an independent
  human accuracy study.
- `br_final_d1_gold.json` is adapter-derived baseline gold, not non-adapter
  free-sentence gold.
- Do not describe the system as independently certified or as a universal
  English grammar judge.

## 11. Files changed in this branch

See `git diff --stat` for the full list. The central files are:

- `server/api.py`, `server/canonical_binding.py`, `server/ruleset.py`,
  `server/matrix.py`, `server/final_d1_projection.py`,
  `server/burton_roberts.py`, `server/br_tree.py`, `server/learner_explanations.py`
- `web/js/main.js`, `web/js/explanation-evidence.js`,
  `web/js/explanation-dedupe.js`, `web/js/legacy-node-map.js`, `web/js/ui.js`,
  `web/js/syntax-builder.js`, `web/css/style.css`
- `scripts/stress_test_syntutor.py`, `scripts/audit_learner_explanations.py`,
  `scripts/audit_explanation_self_reference.py`,
  `scripts/audit_final_d1_exact_fixtures.py`,
  `scripts/test_explanation_dedupe.js`
- `server/test_explanation_coverage.py`, `server/test_agreement_scoping.py`,
  `server/test_relative_pronoun.py`
- `docs/planning/SYNTUTOR_STRESS_TEST_AND_XAI_2026-11-14.md`
