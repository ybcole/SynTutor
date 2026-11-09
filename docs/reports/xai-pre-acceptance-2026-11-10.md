# XAI-PRE Acceptance and Source-Governance Record — 10 November 2026

**Milestone:** XAI-PRE — uploaded-source preflight + correction-dependency contract  
**Status:** **Machine-readable preflight implementation committed. Independent linguistic sign-off is still pending; no grammar rule has been runtime-enabled.**  
**Scope:** **NOT** XAI-0 baseline/50-sentence audit, XAI-1 concept extraction, XAI-4 diagnosis or XAI-5 evolving clickable trees.

## 1. Why XAI-PRE exists

The eventual SynTutor XAI experience must explain what an individual **word, NP, VP, clause or related node does in the *particular* sentence**. If five errors occur, independent and dependent errors cannot be treated as isolated word replacements. An edit may fix one constraint, make a different rule no longer applicable, expose a previously blocked issue, or genuinely introduce a new violation. Every candidate sentence must be separately tokenized and reparsed before its explanation can be considered.

The following deliverables encode the required evidence and record integrity but **do not diagnose or correct English**.

## 2. Primary-book inspection and edition decisions

| Primary source | Inspected in attached original PDF | Consequence | Status |
| --- | --- | --- | --- |
| Noel Burton-Roberts, *Analysing Sentences*, Third Edition (2011), preface **ix–x** | Abandons Vgrp, explicitly treats auxiliary as taking VP complement, revises preposition and node/gap notation | The B–R tree and vocabulary follow the third edition, not second-edition preface passages also included in the full PDF | Primary text inspected; no independent human instructor sign-off |
| Burton-Roberts Ch. 6, **116–118, 122** | Distinguishes lexical and perfect auxiliary *have*; perfect participle after PERF, progressive participle after PROG, each auxiliary heads VP selecting VP complement | Word/error explanations must follow the verb's contextual head/complement relationship, not just spelling | Targeted primary-source check only |
| Cambridge Grammar of the English Language (CGEL), **2002 original edition**, Ch. 3 **p. 76** | Syncretism: *wanted* may be a preterite or past participle despite identical spelling | Don't infer morphological licensing from surface form alone | Targeted primary-source check only |
| Cambridge Ch. 3 **pp. 105–106**, esp. table [44] | Auxiliary ordering and next-verb form: modal→plain, perfect→past participle, progressive→gerund-participle, passive→past participle | Directional feature-selection evidence can in principle support local checks when source/exception/runtime gates pass | Targeted primary-source check only |
| Cambridge Ch. 3 **pp. 143–144** | Past-time adjuncts generally restricted with present perfect, but an explicitly discussed **experiential perfect** admits certain past-time adjuncts with contextual conditions | **Never** enable a blanket present-perfect + yesterday error rule | Targeted primary-source check only |

### Provenance, not overclaiming

- **B–R:** ISBN 9781408233740, 2011 edition confirmed by uploaded title/copyright. The repository split-source manifest holds 11 chapter records; the attached complete volume has 294 PDF pages.
- **CGEL:** ISBN 9780521431460, 2002 original edition. The attached complete volume has 1,862 PDF pages; **the actual physical printing of the uploaded copy is not established**, despite an older plan's unconfirmed mention of a 2016 printing. The repository split-source manifest has 20 chapter records.
- Page references above are **printed book pages**, not PDF page numbers. For these inspected pages, CGEL full-volume PDF page = printed page + 20; B–R Ch. 6 PDF p. 132 = printed 117.
- Existing Cambridge extraction reports cover specific excerpts or sections (for instance, Chapter 3's existing extraction report only covers §1.1 on pp. 74–75). Their reported **owner-approved** state is **not** independent source review for the entire chapter, nor permission to enable XAI-4 constraints.
- The 31-row chapter ledger is a **topic/extraction availability inventory**, not a claim of page-by-page inspection or exhaustive linguistic validation.
- The PRE registry records an **assistant targeted source check**, not independent instructor approval; every proposed new error rule requires a separate exception-aware review and deterministic rule tests.

## 3. Implemented artifacts and strict gates

| Artifact | Purpose | Status |
| --- | --- | --- |
| [source_audit.json](../../grammar/xai_pre/source_audit.json) | Two edition identities, **31 chapter inventory rows**, **13 targeted primary-source claims**, **3 crosswalk decisions**, individual review/activation flags, and open decisions | Added |
| [diagnosis-repair-pre.schema.json](../xai/diagnosis-repair-pre.schema.json) | Versioned partial-rule, issue/dependency graph and evolving candidate tree/token contract | Added |
| [xai_preflight.py](../../server/xai_preflight.py) | Read-only semantic verifier for book-page references, token offsets, stable issue IDs, candidate edit reconstruction, dependency/group integrity, original→candidate finding lineage and source approval boundaries | Added |
| [preflight_fixtures.json](../../grammar/xai_pre/preflight_fixtures.json) | Eleven **synthetic protocol cases** (not gold grammar judgments), including interacted errors, independent repairs, introduced and unmasked findings, temporal exceptions, lexical *have*, syncretism and ambiguous PP attachment | Added |
| [test_xai_preflight.py](../../server/test_xai_preflight.py) | Schema, source guard, rule activation, stale citations, full edit/token provenance, grouping and lineage regression | Added |
| [audit_xai_pre.py](../../scripts/audit_xai_pre.py) | Reproducible summary of technical contract readiness and outstanding source approval | Added |
| [syntax-generator-tests.yml](../../.github/workflows/syntax-generator-tests.yml) | Model-free pipeline runs tests and validates audit/schema/fixtures without downloading NLP models | Updated |
| XAI master plan and implementer prompt | Record concrete preflight artifacts, handoff, and subsequent approval requirements | Updated |

**24 model-free contract tests** now cover chapter and claim provenance, exact token coverage and edit reconstruction, pending-review activation gates, partial outcome lineage, forged citations, and version-specific tree references. These tests do not load spaCy or Benepar.

**Only schema- and semantics-level consistency is checked.** The preflight test fixtures intentionally use `DEMO-*` pseudo-rule identifiers; no fixture can issue a book-certified learner-facing verdict. They cannot establish the accuracy of the actual Benepar/B–R runtime or Cambridge error checks.

## 4. Non-negotiable contract decisions

1. **Original immutable.** Original text, character ranges and token IDs survive every correction; each candidate has a new version ID, text, token map, parser status and a reference to its parent version and (if it exists) its own tree. The current PRE fixture stores no generated trees.
2. **Typed partial evaluations.** `SATISFIED`, `VIOLATED`, `NOT_APPLICABLE`, `BLOCKED`, `AMBIGUOUS`, `UNIMPLEMENTED`. A disabled rule is never silently considered satisfied.
3. **Graph of issue interactions.** Distinguish shared construction, blocked-by, overlapping span, competing interpretation and repair dependencies; independent issues can be explained separately, tightly coupled issues need jointly evaluated candidates.
4. **One finding can highlight several nodes.** A subject–auxiliary relation is a single finding with multiple anchors, not necessarily two independent word errors. Clicking either side points to that same finding.
5. **Counterfactual edit integrity.** The validator applies character-offset edits to the actual parent version; resulting candidate text must match exactly. Edits cannot refer to invented token IDs or reuse version identifiers or repeated sentences in an unbounded loop.
6. **Causal distinction.** `introduced` demands a previously satisfied check and evidence of the edit's effect; `unmasked` demands a previously blocked/ambiguous check. When causality is unknown, say **unknown**.
7. **Candidate outcomes not global certification.** For every original finding, retain `resolved_by_satisfaction`, `no_longer_applicable_after_rewrite`, `persists`, `blocked`, `ambiguous`, etc. A candidate cannot set `whole_sentence_certified: true` in the PRE schema.
8. **Every correction is a new analysis.** XAI-5/7 must later invoke a full parser and eligible rule recheck for each candidate before providing a clickable B–R tree; PRE does not simulate a checked tree by inventing one.
9. **Separate authority.** Burton-Roberts controls B–R tree notation and structure; Cambridge grammatical evidence may explain selection/constraints, but cannot rename the B–R tree via an incomplete terminology crosswalk.
10. **No new runtime rules.** Existing `grammar/runtime_registry.json` remains unchanged, with zero enabled rules. The PRE validator rejects client-supplied enabled rule IDs absent from that registry and pending-review source claims.

## 5. Example: one edit can make a new error

Synthetic scenario: `This boy walk home.`

- The demonstration labels the subject–verb agreement relation as violated.
- It also records an already-satisfied demonstrative→noun-number relation for *this boy*.
- An **experimental** edit to `This boys walk home.` can satisfy the agreement relation while violating the previously satisfied determiner–noun relationship.
- The contract records both a lineage outcome `newly_violated` and a new finding whose origin is `introduced`, with the earlier satisfied proof and a causal edit reference.
- A future live engine must independently support these claims against grammatical rules and interpretive context; these synthetic records are **not actual parser diagnoses**.

The interacting example `She have went to the store yesterday.` also preserves three unresolved/interacting possible findings across `u0`, `u1`, `u2`, and an alternative `u3` branch; deleting the perfect auxiliary makes a formerly applicable constraint **not applicable**, which is not the same as proving it satisfied.

### Additional five-error stress fixture

The simulation `She have went to a stores, and he don't likes it.` now tracks **five candidate findings** across three independent/interacting groups, with five non-overlapping edits and a separate candidate sentence and token map. All "resolved" statuses are synthetic contract data; this is **not** evidence that SynTutor's actual detector or parser can handle such input yet.

The ambiguous PP-attachment example explicitly anchors the **second** occurrence of `the` in `the telescope` (not the earlier `the man`), guarding against duplicate-token misalignment.

## 6. Reproduction and verification

```bash
python -m pip install -r requirements-test.txt
python -m unittest -v server.test_xai_preflight
python scripts/audit_xai_pre.py --require-contracts
python -m json.tool docs/xai/diagnosis-repair-pre.schema.json >/dev/null
python -m json.tool grammar/xai_pre/source_audit.json >/dev/null
python -m json.tool grammar/xai_pre/preflight_fixtures.json >/dev/null
```

A successful run means **technical contracts accepted**, not "the books have been independently approved" or "five simultaneous errors can now be detected". Actual CI links, results and implementation commit are recorded on the XAI-PRE PR.

## 7. Unresolved owner/reviewer decisions, and XAI-0 handoff

- **Source-review authority:** independent human linguistic reviewer/owner needs to approve first-wave extraction/exception/crosswalk records before enabling Cambridge constraints. The current machine inventory is not that approval.
- **Search bounds and meaning:** choose bounded correction beam/depth limits and ask-versus-preserve-context policy using measured XAI-0 data, not a guessed threshold.
- **Structural crosswalk:** explicit comparison of B–R auxiliary VP trees with CGEL clause/VP analysis remains unresolved; the verified form-selection terminology differences do not authorize tree conversion.
- **Variety and register:** define the fallback English variety and what to do when the intended dialect is unknown.
- **XAI-0 baseline:** audit 50+ varied input sentences and record real parser/tree status, explanation coverage, error false positives and XAI-0 fixture baselines. Do not count PRE synthetic data as measured detector performance.
- **XAI-1 and XAI-4:** promote only the source concepts and executable rules whose independent review, scope/exception coverage and tests have passed; no implicit promotion from this document.

**Milestone sign-off:** technical PRE deliverables can be accepted after green CI and owner review of the above decisions. Independent linguistic approval remains an explicit later gate for runtime grammar rules. A branch/PR is a reversible delivery; no Supabase migrations, NLP model reinstalls, or runtime tree changes are required.
