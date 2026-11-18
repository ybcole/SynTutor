# Rapid Cross-Component Consistency Audit

## Snapshot and verdict

| Item | Result |
|---|---|
| Branch / commit | `main` / `250b232df2c551f8cfeb6317d4faccf16f54f7bb` |
| Audit date | 2026-11-15 UTC; final evidence timestamp `2026-11-15T13:23:23Z` |
| Environment | Local macOS 15.8.2, arm64; Python 3.11.17 in `.venv` |
| Installed parser | spaCy model `en_core_web_md` 3.8.0; `benepar_en3`; health `ready=True` |
| Scope | 24 representative sentences, free-analysis FINAL-D1; canonical trees, legacy diagnostics, Cambridge findings, learner node explanations |
| Confirmed inconsistencies | **4 distinct defects**, affecting **4 sentence cases** |
| Highest severity | **P1** |
| Overall verdict | **Not consistently aligned.** Common structures work in this sample, but exact Cambridge lesson examples receive false rejection/correction advice, and independent questions receive misleading explanations. |

Severity: P0 = critical systemic failure; P1 = teaches/recommends an incorrect grammatical change; P2 = misleading structural explanation; P3 = minor presentation issue. No P0 established.

## Execution and exact results

| Execution | Executed | Passed | Failed | Blocked |
|---|---:|---:|---:|---:|
| Representative sentence consistency cases | 24 | 20 | 4 | 0 |
| Existing unittest methods | 20 | 20 | 0 | 0 |
| **Total completed cases/methods** | **44** | **40** | **4** | **0** |

“Passed” for sentence cases means no contradiction identified in the bounded checks below, **not proof of linguistic correctness**. Failures are audit judgments against repository lesson claims and returned explanations, not failures of the existing unittest suite.

Commands run from repository root:

```sh
pwd && git status --short && git branch --show-current && git rev-parse HEAD
.venv/bin/python -B -c "import sys,platform; sys.path.insert(0,'server'); import api; print(sys.version); print(platform.platform()); print(api.health_payload())"
PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python -B - <<'PY'
# Inline batch: api.build_payload for each sentence in the coverage table;
# patch api.classify to return None; compose_learner_explanation for every
# fact_graph node; collect node_details, summary and Cambridge findings.
PY
PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONPATH=server .venv/bin/python -B -m unittest server.test_learner_explanations server.test_explanation_sentence_awareness server.test_modal_category_runtime
```

The batch listing above abbreviates the executed inline Python, not its results; a standalone reproducer follows below.

* Corrected batch: `CASES 24 EXCEPTIONS 0`; all 24 analyses `normalized`, all explanation statuses `EXPLAINED`; **417 node explanations** generated and inspected.
* Independent schema/sentence check on saved batch payloads: `24/24 schema and sentence checks passed; prose nodes: 417`. Used `Draft202012Validator` with `docs/canonical-burton-roberts-tree.schema.json`; checked `tree["sentence"] == input`.
* Existing tests: **`Ran 20 tests in 16.597s` / `OK`**, exit 0. These tests did not catch the four defects below.
* Parser health: `status='ok'`, `ready=True`, pipeline `tok2vec, tagger, parser, attribute_ruler, lemmatizer, ner, benepar`.
* Initial batch reporting mistakenly accessed `payload["details"]` instead of `payload["node_details"]`: 24 reporting `KeyError('details')` exceptions after analysis. All 24 were rerun successfully with the correct key. Those incomplete harness attempts are excluded from completed-case totals; they are **not product defects**.
* Model/tokenizer deprecation warnings and cached CoLA checkpoint unused-pooler warnings appeared; no test failure resulted. No dependencies or models were installed/downloaded.

Batch payloads/prose were retained outside the repository at `/private/var/folders/b3/fbp931_n5md4v_6gy949gjjr0000gn/T/opencode/rapid-consistency-results.json` for local inspection, not as a committed fixture.

## Confirmed findings

| ID / severity | Reproducible contradiction | Affected files and recommended fix |
|---|---|---|
| **F1 / P1** | **Clausal subject treated as preposition object.** Cambridge lesson explicitly uses **“I saw him before he left.”** and teaches that prepositions can take clauses. Generator returns `PP(P before, S(NP he, VP left))`, and learner prose correctly identifies `he` as the subject of `he left`. Nevertheless legacy verdict is `ungrammatical`, with `C-PREP-PRON-CASE`: **“After the preposition 'before', the pronoun must be 'him', not 'he'.”** This advice contradicts both the lesson and the generated clause structure. No assembled correction was returned. | Lesson: `web/js/cambridge-chapter-data.js:728,776–784`. Diagnostic: `server/ruleset.py:3386–3401` scans adjacent leaves without checking whether the pronoun is a clausal subject. Require a direct NP/pronoun complement relation; do not apply object-case rules across a clause boundary. Add this exact lesson example and an actual PP-object error as regression controls. |
| **F2 / P1** | **Notional agreement example rejected and “repaired.”** Lesson explicitly presents **“Three eggs is plenty”** as agreement following meaning as well as form. Input **“Three eggs is plenty.”** returns `ungrammatical`, `C-SUBJECT-AGREEMENT`: **“The subject 'Three eggs' and the verb 'is' do not match. Use 'are' with this subject.”** Returned `corrected_sentence` is **“Three eggs are plenty.”** The lesson's amount interpretation is not acknowledged. This finding does not assert that plural agreement is impossible in every other context. | Lesson: `web/js/cambridge-chapter-data.js:611`. Agreement fallback: `server/matrix.py:2095–2121`; API correction assembly: `server/api.py:239–286`. Support amount/measure predicates and notional agreement, or withhold categorical rejection and correction when that reading is unresolved. Preserve the lesson example unchanged in a regression. |
| **F3 / P1** | **Unsupported count-noun claim about “plenty.”** Independently of F2, the same input produces `C-ARTICLE`: **“'plenty' is a singular noun that names one countable thing, so it needs a little word like 'a' or 'the' before it. Add 'a' (or 'the'/'this').”** Canonical projection places `plenty` under `NP → NOM → N`; learner prose calls it a noun phrase naming a person/thing/group/idea. The lesson licenses this exact bare predicate. The compulsory-article claim is therefore contradicted by repository teaching, regardless of whether a different framework categorizes `plenty` differently. | `server/matrix.py:1377–1419,2229–2237`; parser/projection boundary in `server/parse_engine.py` and `server/final_d1_projection.py`; lesson `web/js/cambridge-chapter-data.js:611`. Do not infer countability or obligatory articles solely from parser `NN`. Handle this predicative use, and mark uncertain lexical analyses instead of teaching “one countable thing.” Test article diagnostics separately from agreement. |
| **F4 / P2** | **Independent questions called subordinate clauses.** **“What did Jon buy?”** gets root `S-dbar`, whose learner explanation is **“‘What did Jon buy’ is a subordinate clause layer; ‘What’ introduces it and the following clause supplies the rest.”** **“Did Jon buy the book?”** gets root `S-bar` and the same subordinate-clause claim with `Did` as introducer. B-R foundations explicitly use S′/S″, C1/C2 and gaps for questions, not only embedding. The tree notation is legitimate; equating it with subordination is the defect. | `server/learner_explanations.py:282–291`; comparison `web/js/advanced-foundations-lessons.js:146–171`. Determine root/embedded status and question structure from graph context; describe C1 as the fronted auxiliary position where appropriate. Do not infer subordination from a bar-level label. Add root yes/no and wh-question explanation assertions. |

F2 and F3 share a sentence but are distinct emitted constraints and independently incorrect teaching claims.

## Sentence coverage

All rows produced schema-valid canonical trees and node prose. Diagnostics below are observed legacy verdicts; “G/U” means `grammatical/ungrammatical`, not independent certification.

| # | Construction / exact input | Verdict | Consistency result |
|---:|---|:---:|---|
| 1 | Intransitive: The birds sing. | G | Pass |
| 2 | Transitive: Nora inspected the bridge. | G | Pass |
| 3 | AP/degree: The children seemed very cheerful. | G | Pass |
| 4 | Adjunct: Nora inspected the bridge yesterday. | G | Pass |
| 5 | Double object: They gave me the key. | G | Pass |
| 6 | PP complement: They gave the key to me. | G | Pass |
| 7 | Perfect/progressive: The researchers have been examining the evidence. | G | Pass |
| 8 | Passive: The letter was read by Mara. | G | Pass |
| 9 | Modal: She can go. | G | Pass |
| 10 | Extra infinitival marker: She can to go. | U | Pass: `C-MODAL-TO`, correction “She can go.” |
| 11 | Agreement error: The boy go to school. | U | Pass: `C-SUBJECT-AGREEMENT` |
| 12 | Perfect form error: She has went home. | U | Pass: `C-VERB-FORM`, correction “She has gone home.” |
| 13 | Wh-question: What did Jon buy? | G | **Fail F4** |
| 14 | Yes/no question: Did Jon buy the book? | G | **Fail F4** |
| 15 | Relative: The book that she wrote is popular. | G | Pass |
| 16 | Embedded content: She said that Jon left. | G | Pass; NP wrapper not treated as cross-framework defect |
| 17 | Nonfinite control: She persuaded Mara to leave. | G | Pass |
| 18 | VP coordination: She sings and dances. | G | Pass |
| 19 | Comparative: She is taller than he is. | G | Pass |
| 20 | Clausal PP complement: I saw him before he left. | U | **Fail F1** |
| 21 | Informal predicative case: It’s me. | G | Pass |
| 22 | Notional agreement: Three eggs is plenty. | U | **Fail F2, F3** |
| 23 | Negation: She did not leave. | G | Pass |
| 24 | Imperative: Close the door. | G | Pass |

Positive structural checks included AP with DEG/A, transitive V/object sisters, layered adjunct VP, ordered PERF/PROG, PASS/by phrase, question C1/C2 and gaps, coordination, and embedded/nonfinite clause layers. The three deliberate error cases received relevant diagnostics; Cambridge findings also identified `COMP-034` for modal selection and `MORPH-026` for perfect form selection.

## Components inspected

| Component | Files |
|---|---|
| Lesson presentation/content | `web/js/phrase-structure-lessons.js`, `web/js/advanced-foundations-lessons.js`, `web/js/cambridge-chapter-lessons.js`, targeted passages in `web/js/cambridge-chapter-data.js` |
| Runtime orchestration/contracts | `server/api.py`; `server/test_api_contract.py`; `server/test_parser_runtime.py` |
| Diagnostics and learner explanations | `server/matrix.py`, `server/ruleset.py`, `server/learner_explanations.py`, `server/test_explanation_sentence_awareness.py` |
| Reused tests/schema and harness reference | Three unittest modules listed above; `docs/canonical-burton-roberts-tree.schema.json`; `scripts/stress_test_syntutor.py`; `package.json` |

The running API also exercised canonical projection, Cambridge evaluation, evidence/fact-graph generation and correction assembly. This is not a claim of line-by-line review of all their implementations.

## Minimal reproduction

Uses installed models offline, with the advisory CoLA channel disabled exactly as in the representative batch. No parser/tree or diagnostic mocks are used.

```sh
PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 .venv/bin/python -B - <<'PY'
import sys
from unittest.mock import patch
sys.path.insert(0, "server")
import api
from learner_explanations import compose_learner_explanation
with patch.object(api, "classify", return_value=None):
    for sentence in (
        "I saw him before he left.", "Three eggs is plenty.",
        "What did Jon buy?", "Did Jon buy the book?",
    ):
        p = api.build_payload(sentence)
        print(sentence, p["summary"]["verdict"],
              p["summary"].get("corrected_sentence"))
        for d in p["node_details"].values():
            if isinstance(d, dict) and d.get("status") == "error":
                print(d.get("constraint"), d.get("text"))
        g = p["explanation_evidence"]["fact_graph"]
        root = g["nodes"][0]
        print(compose_learner_explanation(g, node_id=root["node_id"])["text"])
PY
```

## Framework distinctions, limitations and unresolved questions

* **Not counted as defects:** B-R versus Cambridge category/function differences, NOM/DET conventions, B-R content-clause NP wrappers, and S′/S″ notation itself. Neutral descriptions of malformed input do not certify it as grammatical: `normalized`/`EXPLAINED` are not grammaticality verdicts.
* **Authority caveat:** API sets `verdict_authority="legacy_diagnostic"` and `book_verified=False` (`server/api.py:288–289`). Nevertheless clean summaries assert “is grammatical: every word is used in an allowed way.” This is broader than the bounded checks establish. Treat as a follow-up certainty/presentation risk, not an additional counted contradiction here.
* Representative batch disabled advisory CoLA to avoid correction-search variability and unnecessary model work. Existing unittest execution used normal runtime behavior where invoked. Full hybrid reproduction of each finding was not separately tested; deterministic findings themselves were executed.
* No browser/UI session, hosted API, database lesson versions, or built `dist` content was checked. User-visible selection/routing of canonical versus legacy explanations remains unverified.
* Only free-analysis FINAL-D1 was sampled; chapter-specific V1–V10 profiles, appendix toggles, multiple sentences, unsupported/unresolved input, dialect variation, ambiguous attachments and exhaustive grammatical coverage remain untested.
* Lesson claims were checked against repository content, not independently against original book pages. No claim of comprehensive Burton-Roberts or Cambridge fidelity is made.
* Schema validity establishes data shape, not linguistic validity. Generic prose and minor stylistic differences were not exhaustively assessed.
* Initial repository status was clean. Production code, existing tests and fixtures were left unchanged; this report is the only intended repository change.

**Recommended order:** fix clause-boundary case checking and notional/countability false corrections first; then fix question/subordination prose and add cross-component regressions using the exact lesson examples above.
