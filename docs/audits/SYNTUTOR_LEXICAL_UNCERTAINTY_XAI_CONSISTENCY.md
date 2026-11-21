# SynTutor — Lexical Uncertainty, Syntax Tree, and XAI Consistency Remediation

**Repository:** `ybcole/SynTutor`  
**Branch:** `fix/syntutor-system-reliability-xai`  
**Reference Commit:** `d3ffb4e` (`d3ffb4e2268fb93651d1ece5f847a88d7ff69710`)  
**Thesis:** *SynTutor: An Explainable AI-Based Framework for Syntax Tree-Driven Grammar Analysis and Learning Using NLP*

---

## 1. Executive Summary

An investigation of `Ths cat sleeps.` in the Syntax Generator confirmed a reproducible cross-layer linguistic consistency defect on the current `fix/syntutor-system-reliability-xai` branch (`HEAD d3ffb4e`):

1. **Unverified Possessive Promotion in Canonical Burton–Roberts Projection:**  
   When analyzing `Ths cat sleeps.` (or `Ths boys walk.`), spaCy + Benepar assigned `tag = "PRP$"` to the orthographically uncertain token `Ths` (`(S (NP (PRP$ Ths) (NN cat)) (VP (VBZ sleeps)) (. .))`). Unlike articles (`ART`), demonstratives (`DEM`), and quantifiers (`Q`)—which required closed-class lexical membership in `DETERMINERS`—`server/final_d1_projection.py` accepted **any** token tagged `PRP$` as a verified Burton–Roberts possessive determiner (`DET → POSS → Ths`), returning `br_analysis.status = "normalized"`. Similarly, for `Teh cat sleeps.`, Benepar tagged `Teh` as `NNP`, promoting it into a canonical compound noun `N → [N(Teh), N(cat)]` with an empty `DET[]`.
2. **Concealed Lexical Uncertainty in Learner Explanations and UI Verdict:**  
   Even though `server/spellcheck.py:uncertain_function_words` and `summary["unresolved_tokens"]` already identified `[{'token_id': 0, 'surface': 'Ths'}]`, `server/learner_explanations.py` and `web/js/explanation-evidence.js` did not consult `unresolved_tokens` when generating node descriptions, full-sentence overviews, or the sentence-level verdict badge. Consequently:
   - The full-sentence explanation panel displayed `"The checks found no clear grammatical issue."` without mentioning that `"Ths"` is orthographically uncertain.
   - Selecting the `POSS` or `Ths` node told the learner `"The possessive position in “Ths cat” is filled by “Ths”."` and `"“Ths” is a possessive word showing who something belongs to."`

We implemented a generalized, minimal root-cause fix across the projection, explanation, and frontend evidence layers so that:
- Closed-class possessive determiner projection (`DET → POSS`) requires verified lexical membership in `POSSESSIVE_DETERMINERS`, and any token flagged by `uncertain_function_words(analysis)` prevents false canonical promotion (`br_analysis.status = "unresolved"`, rendering an unlabelled provisional triangle in `working_tree` without fabricating `POSS` or `DET`).
- Valid local grammatical relationships (such as singular subject–verb agreement between `"cat"` and `"sleeps"` or plural agreement between `"boys"` and `"walk"`) are preserved and explicitly qualified alongside the lexical uncertainty.
- Both full-sentence and node-level learner explanations clearly communicate that `"Ths"` is orthographically uncertain and present context-compatible determiner readings (`“The”` or `“This”` before singular `"cat"`; `“The”`, `“These”`, or `“Those”` before plural `"boys"`) as possibilities rather than confirmed corrections.

---

## 2. Verified Runtime Reproduction

Before modifying code, `build_payload("Ths cat sleeps.")` was executed on `fix/syntutor-system-reliability-xai` at commit `d3ffb4e`:

- **Parser candidate (`parse_string`):** `(S (NP (PRP$ Ths) (NN cat)) (VP (VBZ sleeps)) (. .))`
- **Token record for `Ths`:** `pos = "ADJ"`, `tag = "PRP$"`, `dep = "amod"`
- **`summary.verdict`:** `"grammatical"`
- **`summary.unresolved_tokens`:** `[{'token_id': 0, 'surface': 'Ths'}]`
- **`br_analysis.status` (Before Fix):** `"normalized"`
- **Canonical tree rendered (Before Fix):** `S → NP(DET(POSS(Ths)), NOM(N(cat))) + VP(V[intrans, pres](sleeps))`
- **Displayed explanations (Before Fix):**
  - Full-sentence overview: `"“Ths cat” is the subject of this clause, and “sleeps” is its predicate."`
  - Verdict badge: `"The checks found no clear grammatical issue."`
  - Node `POSS` (`sg-root-0-0-0`): `"The possessive position in “Ths cat” is filled by “Ths”."`
  - Node `Ths` (`sg-root-0-0-0-0`): `"“Ths” is a possessive word showing who something belongs to."`

Thus, the screenshot reflected actual current-branch behavior at `d3ffb4e`, not stale browser state or an older branch.

---

## 3. Root-Cause Analysis

Tracing the pipeline across all six stages revealed three interacting root causes:

1. **Unchecked `PRP$` Promotion in `server/final_d1_projection.py` and `server/burton_roberts.py`:**
   - In `server/final_d1_projection.py` (`Projection.np`), determiner projection checked:
     `if leaf(first) and (tag(first) == "PRP$" or word(first) in DETERMINERS):`
     Because `tag(first) == "PRP$"` did not verify whether `word(first)` belonged to the closed class of English possessive determiners (`my`, `your`, `his`, `her`, `its`, `our`, `their`, `whose`, `thy`, `one's`), any OOV or misspelled token tagged `PRP$` by spaCy/Benepar was promoted into a verified canonical `DET → POSS` node.
   - Similarly, in `Projection.working_leaf`, `WORKING_LEAF_LABEL` mapped `"PRP$": "DET"` and `"DT": "DET"` unconditionally, and `server/burton_roberts.py:_final_projection` did not check `spellcheck.uncertain_function_words(analysis)` before canonical projection.
2. **Missing Lexical-Uncertainty Guard in `server/learner_explanations.py`:**
   - `_runtime_description()` checked `_has_category_conflict(leaf)` only for `{'N', 'V', 'A', 'Adv', 'P', 'pronoun', 'name'}` and did not consult `summary['unresolved_tokens']`. When explaining `Ths` (or `Teh`), it fell back to `_word()` / `_phrase()`, which trustingly narrated the tree label (`"possessive word showing who something belongs to"` or `"noun that names someone, something, or an idea"`).
   - `build_learner_analysis()` only updated `result['sentence_text']` when `resolved` (`br_analysis.status == 'normalized'`) was true, and defined `sentence_not_clean = verdict != 'grammatical' or bool(findings)` without checking `unresolved_tokens`.
3. **Unconditional Clean Verdict Badge in `web/js/explanation-evidence.js` and `web/js/main.js`:**
   - `localEvidenceOptions()` in `web/js/main.js` did not pass `unresolvedTokens` into `renderEvidence()`.
   - In `web/js/explanation-evidence.js`, `renderEvidence()` either displayed `'The checks found no clear grammatical issue.'` (when `treeUnresolved` was false and `verdict === 'grammatical'`) or replaced the entire overview with `'Analysis incomplete. The syntax remains uncertain and the grammatical result is inconclusive.'` (when `treeUnresolved` was true and `findings` was empty), hiding both the specific lexical uncertainty and the valid local subject–verb agreement.

---

## 4. Files Modified and Why

| File | Responsibility & Modification |
|---|---|
| `server/spellcheck.py` | Added `uncertain_function_word_candidates(word, next_type=None)` using general orthographic edit patterns (vowel deletion, adjacent transposition, same-prefix substitution, and consonant-skeleton match) filtered by number compatibility with the following nominal head (`NN`/`NNP` vs `NNS`/`NNPS`). |
| `server/final_d1_projection.py` | Added closed-class `POSSESSIVE_DETERMINERS`; guarded `Projection.np` against `uncertain_token` leaves and unverified `PRP$`/`DT`/`PDT` tokens; updated `Projection.working_leaf` so uncertain tokens project as unlabelled provisional triangles rather than unverified `POSS` or `DET` categories. |
| `server/burton_roberts.py` | In `_final_projection`, marked leaves matching `uncertain_function_words(analysis)` with `uncertain_token = True` and routed clauses containing orthographically uncertain function words to the provisional `working_tree` (`br_analysis.status = "unresolved"`). |
| `server/learner_explanations.py` | Updated `_runtime_description` and `build_learner_analysis` to explain single-token and phrase/clause-level lexical uncertainty with plausible determiner readings, preserve and qualify valid local subject–verb agreement, and link uncertain determiner-slot tokens to `#lesson/br-07/concepts` (*Determiners and pre-determiners*). |
| `web/js/explanation-evidence.js` | Updated `renderEvidence` to handle `options.unresolvedTokens`: displays the uncertainty-qualified overview and `'Lexical uncertainty — provisional analysis'` verdict badge instead of `'The checks found no clear grammatical issue.'` or a generic inconclusive fallback. |
| `web/js/main.js` | Passed `unresolvedTokens` from `payload.summary.unresolved_tokens` / `payload.learner_analysis.unresolved_tokens` into `localEvidenceOptions()`. |
| `web/js/lessons-ui.js` | Added `'pointer-events': 'all'` on rendered SVG triangle `<polygon>` elements in `renderLessonTree()` so clicks anywhere inside an unlabelled provisional triangle select the node rather than falling through to `<svg>`. |
| `server/test_cross_layer_consistency.py` | Added `test_lexical_uncertainty_and_determiner_controls` covering all 8 required control and target sentences (`The cat sleeps.`, `This cat sleeps.`, `His cat sleeps.`, `Ths cat sleeps.`, `Ths boys walk.`, `Teh cat sleeps.`, `Tsh arrived yesterday.`, `Ana sleeps.`). |
| `scripts/test_cross_layer_xai_browser.mjs` | Extended live Flask + Chromium E2E assertions for `His cat sleeps.`, `Ths cat sleeps.`, `Ths boys walk.`, and `Ana sleeps.` and switched SVG label assertions from `allInnerTexts()` to `allTextContents()`. |

---

## 5. Before / After Behavior for Key Sentences

| Sentence | Before Fix (`d3ffb4e`) | After Fix |
|---|---|---|
| `The cat sleeps.` | `status="normalized"`, `S → NP(DET(ART(The)), NOM(N(cat))) + VP(V(sleeps))`, clean grammatical verdict. | **Unchanged** (`status="normalized"`, `DET → ART → The`, clean grammatical verdict). |
| `This cat sleeps.` | `status="normalized"`, `S → NP(DET(DEM(This)), NOM(N(cat))) + VP(V(sleeps))`, clean grammatical verdict. | **Unchanged** (`status="normalized"`, `DET → DEM → This`, clean grammatical verdict). |
| `His cat sleeps.` | `status="normalized"`, `S → NP(DET(POSS(His)), NOM(N(cat))) + VP(V(sleeps))`, clean grammatical verdict. | **Unchanged** (`status="normalized"`, `DET → POSS → His`, clean grammatical verdict). |
| `Ths cat sleeps.` | `status="normalized"`, `DET → POSS → Ths`; badge: `"The checks found no clear grammatical issue."`; node: `"“Ths” is a possessive word showing who something belongs to."` | `status="unresolved"` (`working_tree` with unlabelled provisional triangle for `Ths`, **no `POSS` or `DET`**); badge: `"Lexical uncertainty — provisional analysis"`; overview preserves valid `"cat"` + `"sleeps"` agreement while stating `"Ths"` (plausibly `"The"` or `"This"`) is uncertain; node explanation states `"Ths"` is an orthographically uncertain token. |
| `Ths boys walk.` | `status="normalized"`, `DET → POSS → Ths`; badge: `"The checks found no clear grammatical issue."` | `status="unresolved"` (`working_tree`, **no `POSS` or `DET`**); badge: `"Lexical uncertainty — provisional analysis"`; overview preserves valid plural `"boys"` + `"walk"` agreement while stating `"Ths"` (plausibly `"The"`, `"These"`, or `"Those"`) is uncertain. |
| `Teh cat sleeps.` | `status="normalized"`, canonical compound `NOM → N → [N(Teh), N(cat)]` with empty `DET[]`; clicking `Teh` said `"“Teh” is a noun..."` | `status="unresolved"` (`working_tree` with unlabelled provisional triangle for `Teh`); `C-SPELLING` finding (`"Check the spelling of “Teh” (for example, “the”)."`); clicking `Teh` explains its orthographic uncertainty rather than calling it a noun. |
| `Tsh arrived yesterday.` | `status="normalized"`, `NP → name → Tsh`, zero findings, no rewrite. | **Unchanged** (`status="normalized"`, `NP → name → Tsh`, zero findings, `unresolved_tokens = None`). |
| `Ana sleeps.` | `status="normalized"`, `NP → name → Ana`, zero findings, no rewrite. | **Unchanged** (`status="normalized"`, `NP → name → Ana`, zero findings, `unresolved_tokens = None`). |

---

## 6. Regression Tests Added

1. **Python Cross-Layer Integration Test (`server/test_cross_layer_consistency.py` — `test_lexical_uncertainty_and_determiner_controls`):**
   - Verifies canonical `ART`, `DEM`, and `POSS` projection on `The cat sleeps.`, `This cat sleeps.`, and `His cat sleeps.`.
   - Verifies that `Ths cat sleeps.` and `Ths boys walk.` return `br_analysis.status == "unresolved"`, `tree is None`, `working_tree` without `POSS` or `DET`, `unresolved_tokens == [{'token_id': 0, 'surface': 'Ths'}]`, preserved and qualified `subject_verb_agreement`, context-appropriate candidate readings (`“The”`/`“This”` vs `“The”`/`“These”`/`“Those”`), zero `"possessive"` claims on any node, and `#lesson/br-07/concepts` routing on the `Ths` node.
   - Verifies that `Teh cat sleeps.` returns `br_analysis.status == "unresolved"`, `C-SPELLING` with `“the”`, and no `"“Teh” is a noun"` node explanation.
   - Verifies that proper-name controls `Tsh arrived yesterday.` and `Ana sleeps.` remain `status == "normalized"` with `name` nodes and zero findings.
2. **Chromium End-to-End Browser Test (`scripts/test_cross_layer_xai_browser.mjs`):**
   - Submits `His cat sleeps.`, `Ths cat sleeps.`, `Ths boys walk.`, and `Ana sleeps.` through the live `#inputText` UI against the Flask backend.
   - Asserts SVG node labels, `#treeAuthorityNotice` provisional banner, `#explainNode` full-sentence overview and verdict badge, interactive node click on `Ths`, and `#lesson/br-07/concepts` lesson link.

---

## 7. Commands Executed and Verification Results

1. **Environment / Parser Loading Resolution:**
   - **Cause of earlier `load_models()` failure in sandboxed runs:** `benepar_en3` was installed only in `/Users/kiyel/nltk_data/models/benepar_en3` (outside the workspace sandbox boundary) and not in `/Users/kiyel/Desktop/SynTutor/.venv/nltk_data/models/benepar_en3` (which is on NLTK's default `.venv` search path inside the workspace). When `load_models()` in `server/parse_engine.py` ran inside the sandbox, `nltk.data.find('models/benepar_en3')` raised `LookupError`, which `parse_engine.py` cached in `_load_error` for subsequent tests in the same process.
   - **Resolution:** Installed `benepar_en3` into `/Users/kiyel/Desktop/SynTutor/.venv/nltk_data/models/benepar_en3` (inside the gitignored `.venv/`).
   - **Focused parser verification:**
     `PYTHONPATH=server .venv/bin/python -c "import parse_engine; nlp = parse_engine.load_models(); res = parse_engine.analyze('Ths cat sleeps.'); ..."` — **PASSED** (`Loaded pipes: ['tok2vec', 'tagger', 'parser', 'attribute_ruler', 'lemmatizer', 'ner', 'benepar']`).
2. **Targeted & Full Python Unit / Integration Tests:**
   - `PYTHONPATH=server .venv/bin/python -m unittest test_cross_layer_consistency.CrossLayerLinguisticConsistencyTest.test_lexical_uncertainty_and_determiner_controls` — **PASSED (1/1)**
   - `PYTHONPATH=server .venv/bin/python -m unittest test_cross_layer_consistency` — **PASSED (7/7)**
   - `HF_HUB_OFFLINE=1 .venv/bin/python -m unittest discover -s server -p 'test_*.py'` — **979 tests discovered (`0` failures; the 14 sandbox socket errors and 45 `CGEL_REQUIRE_PARSER=1` skips were verified directly in the two commands immediately below)**
   - `HF_HUB_OFFLINE=1 PYTHONPATH=server .venv/bin/python -m unittest test_builder_evaluation test_explanation_transports test_quiz_evidence test_stdlib_transport_contract` — **PASSED (24/24)**
   - `HF_HUB_OFFLINE=1 CGEL_REQUIRE_PARSER=1 .venv/bin/python -m unittest discover -s server -p 'test_cgel_*.py'` — **PASSED (413/413, `0` skipped)**
   - `HF_HUB_OFFLINE=1 PYTHONPATH=server .venv/bin/python server/test_corrector.py` — **PASSED (9/9)**
3. **Frontend JS, Database, Dictionary & Evaluation Integrity Suites:**
   - `node --check web/js/lessons-ui.js web/js/explanation-evidence.js web/js/main.js` — **PASSED**
   - 21 Node/PGlite unit & database suites (`test_account_integration.js`, `test_assessment_core.js`, `test_assessment_database.js`, `test_builder_core.js`, `test_correction.js`, `test_explanation_dedupe.js`, `test_explanation_evidence.js`, `test_foundation_progress.js`, `test_legacy_node_map.js`, `test_lesson_database.js`, `test_lesson_progress.js`, `test_level.js`, `test_node_lesson_map.js`, `test_quiz_digest_freshness.js`, `test_quiz_formal.js`, `test_quiz_lesson_practice.js`, `test_quiz_refinements.js`, `test_quiz_v2_database.js`, `test_quiz_v2.js`, `test_tree_layout.js`, `test_tree_quiz.js`) — **PASSED (21/21)**
   - `npm run dictionary:audit` — **PASSED (852/852 terms)**
   - `python3 docs/audits/technical_evaluation/verify_metrics.py` — **PASSED (74/74 checks)**
4. **Live Flask + Chromium Playwright Browser Suites (`SYNTUTOR_PORT=8769`):**
   - `scripts/test_cross_layer_xai_browser.mjs` — **PASSED**
   - `scripts/test_interactive_xai_browser.mjs` — **PASSED**
   - `scripts/test_ui_ux_refinements_browser.mjs` — **PASSED**
   - `scripts/test_real_world_nlp_browser.mjs` — **PASSED**

---

## 8. Remaining Risks or Explicitly Deferred Limitations

1. **Sentence-Initial Ambiguity Between Rare Proper Names and Unusual Typos:**  
   In accordance with SynTutor's conservative non-fabrication policy, sentence-initial capitalized tokens that are not near-miss closed-class determiners (`uncertain_function_words`) and that receive proper-noun parses (`NNP`, e.g., `Ana sleeps.` or `Tsh arrived yesterday.`) continue to be analyzed as proper names rather than flagged as spelling errors.
2. **Open-Class Real-Word Malapropisms:**  
   When a typo accidentally produces a valid English word with a compatible syntactic category in the same slot (e.g., `"The car sleeps."` for `"The cat sleeps."`), syntactic and orthographic checks treat the sentence as structurally grammatical.
