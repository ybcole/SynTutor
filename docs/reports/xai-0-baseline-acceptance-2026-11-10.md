# XAI-0 — Empirical Baseline, Node-Explanation Coverage and Contract Freeze

**Milestone:** XAI-0 (following [XAI-PRE](xai-pre-acceptance-2026-11-10.md))  
**Status:** Repeatable baseline instrumentation + tests implemented. **Real-parser figures must be read from CI artifact and recorded here only after that workflow finishes**.  
**Date:** 10 November 2026  
**Implementation branch:** `feature/xai-0-measured-baseline-2026-11-10`  
**Scope:** Inspection and measurement. No new Cambridge constraints, edits to B–R grammar, new explanations or correction algorithms.

## 1. Baseline inventory — verified in the current repository

| Module or asset | Current state | XAI gap |
| --- | --- | --- |
| `grammar/explanation_templates.json` | **2** independently reviewed teaching templates, **4** source rows. One B–R structural S → NP VP teaching template; one Cambridge sentence/clause classification template. | Does not supply tailored word/NP/VP/head/complement explanation for arbitrary sentences. |
| `grammar/runtime_registry.json` | **0** Cambridge runtime-enabled constraints. | Grammar and remediation claims cannot be independently certified from Cambridge until XAI-4. |
| `server/explanations.py` | Server-owned, source-gated composer for channels structural, grammatical and remediation. Matches primarily `node_label`, optionally immediate child-label patterns. Returns `facts[]` with node category and surface; `NO_BOOK_BASIS` if no eligible template. | No typed sentence fact graph; no independently licensed subject/object relations or per-node targeted grammatical diagnosis. Observational facts are **not the same as contextual book explanations**. |
| `server/parse_engine.py` | spaCy `en_core_web_md` and Benepar `benepar_en3` candidate parsing. | A candidate parse is not a grammar verdict or B–R source. |
| `server/burton_roberts.py` + FINAL-D1 | Attempts canonical B–R normalization and exposes unresolved/working status for unsupported cases. | Not every input produces a canonical tree; available working trees must not be treated as source-verified. |
| `server/cambridge_evaluator.py` | Fail-closed runtime registry with currently disabled Cambridge constraints. | No Cambridge-backed live error findings available for XAI explanations. |
| `server/api.py` | `build_payload` carries raw candidate and B–R analyses, `explanation_evidence`, Cambridge evaluation, legacy matrix and correction proposal separately. | Legacy candidate verdicts and corrections are **not book-backed XAI**. `POST /api/explain` accepts canonical tree, optional node ID and variety; no client-supplied source registry. |
| `web/js/canonical-view.js` | Deterministic selected-node observations (category, surface, daughters, features). | No source-linked proof of grammatical function or argument structure. |
| `web/js/explanation-evidence.js` | Shared Generator/Builder request/rendering contract, reviewed citation displayed where available. | Most word and constituent nodes have no eligible template; click can show an observation but not a tailored book-grounded explanation. |
| `web/js/main.js` and `web/js/correction.js` | Existing *legacy* node focus and candidate correction/reparse flow; selected-node inspection and corrected view exist in the prior prototype. | Not yet the XAI-PRE multi-error proof/lineage contract, interacting-repair search or independently validated evolving B–R syntax trees. |

### Provenance and status rules frozen for later phases

1. **B–R source of tree structure:** only the canonical `br_analysis.tree` where status and schema permit; never relabel raw Benepar/Penn output as book authority.
2. **Book evidence:** only server-owned reviewed source/template records with exact edition, printed page, approved framework mapping, and the correct channel; no externally supplied client citations.
3. **Node explanation:** observed label/words/children are **structural observations**; a cited `EXPLAINED` item is an **eligible template hit**; a separately approved role and proof would be needed to claim **contextual syntactic-function accuracy**. These must be tracked as different coverage metrics.
4. **Grammar and errors:** Cambridge evaluation is the only potential new book-backed runtime constraint path; `legacy_matrix` and any acceptability signal remain **diagnostic**, not a proof. There are zero eligible Cambridge rules today.
5. **Ambiguity/unresolved:** preserve uncertain/working tree statuses; no invented deep child phrases or categorical function labels where source/parser evidence is unavailable.
6. **Correction ancestry:** preserve `XAI-PRE` immutable original, per-version candidates and typed finding lineage. Existing UI reparse does not automatically satisfy that stronger contract.
7. **Cross-client parity:** Generator and Builder share `POST /api/explain`; versioned additions may be made later, but changing those existing fields requires regression tests.
8. **UI language:** “Observed structure,” “Reviewed book evidence,” “Legacy diagnostic, not verified,” “Ambiguous,” and “Analysis unavailable” are separate concepts. No unqualified green “sentence correct” conclusion from a structural tree.
9. **No uncontrolled runtime AI:** XAI-0 audits existing deterministic server evidence; any optional LLM naturalizer remains off until XAI-6 grounding tests.

## 2. Development set and measurement method

**File:** [evaluation/xai0_development_cases.json](../../evaluation/xai0_development_cases.json)

**Count:** 116 distinct case IDs in 12 construction/usage families (plus a second-sentence selection probe). All records are `NOT_ADJUDICATED`, and this is a **development set, not a held-out gold benchmark**.

The corpus includes ordinary clauses, transitives/ditransitives, nested auxiliaries, passives, questions, negation, nonfinite/embedded clauses, coordination, attachments, ambiguous word class, two-or-more errors, five simultaneous proposed problems, style/dialect-dependent English, temporal exceptions from Cambridge, Taglish/mixed language, quoted/marked-up text and punctuation/multi-sentence inputs.

**Report generator:** [scripts/audit_xai0_baseline.py](../../scripts/audit_xai0_baseline.py)

- Uses **actual installed spaCy/Benepar**, `build_canonical_analysis`, `evaluate_cambridge`, `explain_analysis`, and a scoped existing `explain_request` on real canonical roots; no mock tree is substituted.
- Records model availability and model identity, raw parser success/errors, B–R normalization/working/unresolved status and reasons, explanation status, observed node/terminal counts, reviewed source-cited template hits, category gaps, API root-target parity, legacy matrix observations, timing percentiles and individual outcomes.
- Separate denominators: **parser cases**, **normalized cases**, **nodes in normalized trees**, **terminal word nodes**, **eligible cited nodes**. An unresolved case is not quietly dropped from the corpus; no invalid rate uses a zero denominator.
- The “grammatical_control” and “malformed_probe” tags are **provisional development hypotheses**. Any mismatch with the legacy matrix is a **triage flag**, not measured false-positive or false-negative accuracy. Formal human adjudication belongs to XAI-8.
- The pipeline does **not** call CoLA acceptability or the legacy candidate corrector in bulk. This narrower audit intentionally isolates real parser+B–R+reviewed explanation coverage; classifier/correction red flags remain separately documented by existing API/browser tests.
- `--require-models` fails clearly if models are missing. The model-free input validator can run without models but **does not fabricate** parser metrics.

### Local and CI commands

```bash
python scripts/audit_xai0_baseline.py --validate-input-only --expected-count 116
python -m unittest -v server.test_xai0_baseline
python scripts/audit_xai0_baseline.py --require-models --expected-count 116 --output artifacts/xai0-baseline.json
```

The first two run in the model-free workflow. The third runs in the pinned-model parser-backed workflow, which uploads `xai0-real-parser-baseline` as a versioned JSON artifact. Do not confuse passing model-free tests with measuring real parser coverage.

## 3. Empirical outcomes — to populate from completed pinned-model CI

Record exactly the resulting PR head SHA/workflow artifact and the printed summary, with no invented statistics:

| Metric | Current value |
| --- | --- |
| Cases actually attempted | **Pending parser-backed CI** |
| spaCy/Benepar model availability | **Pending parser-backed CI** |
| Canonical normalized / unresolved / failures | **Pending parser-backed CI** |
| Eligible source-cited explanations by canonical node | **Pending parser-backed CI** |
| Eligible source-cited explanations by overt terminal node | **Pending parser-backed CI** |
| Most commonly unsupported B–R node labels | **Pending parser-backed CI** |
| Observed legacy matrix disagreements on provisional controls | **Pending parser-backed CI — do not call these verified false positives** |
| Root `/api/explain` contract parity mismatches | **Pending parser-backed CI** |
| p50/p95 observed runtimes | **Pending parser-backed CI (CI environment only)** |

## 4. First priority gaps for XAI-1 through XAI-3

- **Syntactic relation coverage:** identify a selected NP as actual subject/object only where a reviewed B–R parent/child construction licenses it. Current two-template system cannot cover general contextual roles.
- **Node-level coverage:** account for V, N, DET, NOM, pronoun/name, PP, P, AdvP, AP, wh gaps, auxiliaries, whole phrase spans and collapsed triangles. Explain missing source basis rather than pretending a category definition is contextual evidence.
- **Morphology and Cambridge scope:** preserve lexical `had` vs perfect auxiliary `had`, tense/participle syncretism, modal+plain selection, Cambridge temporal adjunct exceptions, and variety conditions.
- **Unresolved and alternative analyses:** provide honest structural observations for noncanonical/working parses, with explicit scope and no fabricated inside-the-triangle grammar; later use reviewed alternatives to explain attachment differences.
- **Multi-error correction:** do not upgrade legacy one-error edits to a 5-error proof. Build XAI-PRE relation graph and candidate re-evaluation separately in XAI-4/5, preserve branch history and new tree for each applied edit when available.
- **Security and learner safety:** selected node text and Markdown must be escaped; script-like sentence content cannot become executable markup or source instructions. Use source-controlled templates and no client-supplied citations.

## 5. XAI-0 acceptance and remaining human work

**Machine acceptance:** corpus and measurement tests pass; real parser executes on the declared 116 inputs; full JSON per-case report is produced/uploaded; source/rule inventory and observed node coverage denominators are documented; existing model-free and parser-backed/browser regressions remain green.

**Outside XAI-0:** independently adjudicating grammar errors, approving new source claims, adding the full per-node fact graph, writing new Cambridge rules, naturalizer generation, or implementing five-error correction plans. No database migration or configuration change is needed.

**Next:** XAI-1 — independently reviewed, page-linked B–R/Cambridge concept ledger and template candidates; only then begin detailed relationship facts and actual corrected-node XAI where approved.
