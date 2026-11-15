# SynTutor Next Steps and Gap Register — 2026-11-14

This document records what the latest verification run found, where the
remaining gaps are, and the best order to close them. It is a software
acceptance view, not an independent linguistic certification.

## 1. What was verified

| Gate | Result |
|---|---:|
| Full backend suite | **908 tests pass**, 45 skipped |
| Stress suite | **183 cases: 165 normalized, 18 labelled working trees, 0 flagged** |
| Exact fixtures | **216/216 exact**, 0 unresolved |
| Held-out grammatical | **281/281 normalized** |
| Held-out ungrammatical | **45/45 with trees** |
| Explanation audits | 185 parser-backed sentences; 0 self-reference, over-context or word-level duplicate problems |
| Rule-probe corpus | **71/83 implemented error rules exercised directly** |
| Learner XAI quality | mean Flesch reading ease **89.5**; 0 jargon, id-leak, over-length or non-actionable flags |

New audit tooling added this session:

- `scripts/audit_rule_coverage.py` — which matrix constraints the corpus hits.
- `scripts/rule_probe_corpus.py` + `scripts/audit_rule_probes.py` — one probe
  per implemented error rule.
- `scripts/audit_learner_xai_quality.py` — readability, jargon, actionability
  and repetition screen.
- `server/test_detection_scoping.py`,
  `server/test_explanation_sentence_awareness.py`.

## 2. Detection coverage

Of 124 registered constraints, the 183-sentence corpus exercises 39 directly.
The rule-probe corpus covers 71 of the 83 implemented error rules directly.
The remaining 12 are grouped:

**Fires a related constraint (probe needs a more specific trigger)**
- `C-DUMMY-IT` (fires `C-MISSING-SUBJECT`)
- `C-L1-INTERFERENCE` (fires `C-MOD-POS`)
- `C-PROPER-NOUN` (fires `C-ARTICLE`)
- `C-QUOTATION` (fires `C-PROPER-NOUN`)
- `C-RELATIVE-POSSESSIVE` (fires `C-ARTICLE`)
- `C-WORD-ORDER` (fires `C-TENSE-FINITE`)

**Trigger-specific / dormant**
- `C-NUMERAL-FORMAT` (needs a matching numeric format such as `12,00`)
- `C-PARTICIPIAL` (needs a specific participial fragment shape)
- `C-REGISTER` (depends on a register word list; `gonna` is split by the
  tokenizer)

**Resource-dependent (likely dormant until a lexicon is wired)**
- `C-LEXICON-MALFORMED`, `C-LEXICON-TAG-MISMATCH`, `C-LEXICON-UNKNOWN`

**Declared but has no producer**
- `C-MLM-ANOMALY` (only appears in the label registry)

## 3. Tree coverage

18 constructions still use **labelled provisional working trees** (reason-coded,
not triangles):

- `since` temporal/causal ambiguity (intentional fail-closed).
- `Who among the candidates is best qualified?` (inversion subject with PP).
- `The more you practice, the better you become.` (correlative comparative).
- `He earns less than his colleague.` (comparative `less than`).
- `Having finished the report, she went home.` (perfect participial).
- `The children were seen playing in the yard.` (perception passive control).
- `We heard the door close.` (bare-infinitive small clause).
- Negative / only / locative / so inversion (4).
- Gapping (`They reviewed the first draft and we the second.`).
- VP ellipsis (`She can play the piano and he can too.`).
- Topicalization with comma (`This problem, we can solve together.`).
- Appositive (`The plan, a bold one, was approved.`).
- Infinitival relative (`much work to do before Friday`).
- Stranded-preposition question (`Who did you give the keys to?`).
- Nested relative with a subject gap (`deep-relative-3`).

## 4. Learner XAI quality

- Error/suggestion copy: 52 findings across 183 sentences; every one is
  actionable and free of internal ids or jargon.
- Mean reading ease 89.5 (very easy); the shortest copy is still above 56.
- 210 repeated node paragraphs come from structural layers (`VP`/`NP`/`S′`)
  and are collapsed by the UI (`explanation-dedupe.js`); words and lexical
  wrappers never repeat their parent.
- Remaining learner-experience opportunity: explain grammatical terms inline
  (for example a glossary tooltip for "subject", "object", "clause",
  "prepositional phrase") and, optionally, add a `Full B-R` / `Learner view`
  toggle for `C1`/`C2` and movement subscripts.

## 5. Best approach next (ranked)

1. **Make the rule registry honest.** For the 12 uncovered probes: either add a
   correct trigger test so the rule is exercised, or move truly dormant rules
   (lexicon-resource rules, `C-MLM-ANOMALY`) out of the enabled registry so the
   inventory matches what production can actually detect.
2. **Close the highest-frequency provisional constructions.** In order of
   learner value: `less/more than` comparatives, appositives, participial
   adjuncts, and the inversion family. Each needs one narrow licensed rule and
   one stress case.
3. **Reduce structural repetition at the source.** `VP`/`NP`/`S′` layers that
   repeat their parent could return a one-line "same as the enclosing phrase"
   payload directly, instead of relying on the client cache, so any consumer
   (builder, API) behaves the same.
4. **Add a learner glossary + optional simplified view.** Keep the canonical
   tree; present `C1`/`C2` and movement subscripts behind a toggle, and link
   grammatical terms to short definitions.
5. **Add a browser/visual pass.** Run the Playwright lesson/foundation tests
   and capture tree screenshots for the reported sentences.
6. **Author independent review or non-adapter gold.** The current gold is
   adapter-derived; the owner waiver for the 193 runtime rules remains in
   force and must not be described as certification.

## 6. Verification commands

```bash
# full backend
cd server && ..\.venv\Scripts\python.exe -m unittest discover -p 'test_*.py'

# stress + audits
.venv/Scripts/python.exe scripts/stress_test_syntutor.py
.venv/Scripts/python.exe scripts/audit_rule_coverage.py
.venv/Scripts/python.exe scripts/audit_rule_probes.py
.venv/Scripts/python.exe scripts/audit_explanation_self_reference.py
.venv/Scripts/python.exe scripts/audit_learner_xai_quality.py

# UI contracts
node scripts/test_explanation_dedupe.js
node scripts/test_legacy_node_map.js
node scripts/test_correction.js
node scripts/test_tree_layout.js
```
