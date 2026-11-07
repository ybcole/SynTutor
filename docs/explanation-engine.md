# Shared explanation contract

`server/explanations.py` composes deterministic evidence for both Generator and
Builder. All three HTTP transports expose `POST /api/explain`:

```json
{"tree": "canonical B-R envelope object or null", "node_id": "optional canonical node ID", "variety": "optional selected variety"}
```

The `tree` value is an object, not a JSON-encoded string. The endpoint validates
it against the approved schema and structural invariants. The request may not
supply templates, rule findings or a source registry. Invalid/unknown nodes and
malformed trees return 400; bodies over 250000 bytes return 413. `null` produces
`ANALYSIS_UNRESOLVED`. No parser model is required for this endpoint.

`POST /api/parse` also returns `explanation_evidence`. The browser's Generator
and Builder both call the same `/api/explain` service and use
`web/js/explanation-evidence.js` to render its result. Raw parser node IDs are
not passed off as canonical IDs. Generator selection shows the sentence's
canonical evidence separately from its legacy diagnostic node card.

## Result

- `status`: `EXPLAINED`, `NO_BOOK_BASIS`, `ANALYSIS_UNRESOLVED`, `SOURCE_CONFLICT`.
- `channels.structural`: B-R conventions, with source citations and node facts.
- `channels.grammatical`: reviewed Cambridge teaching descriptions, or explanations of server-evaluated rules. A descriptive/classification template never establishes a grammatical verdict.
- `channels.remediation`: reviewed feedback tied to an actual server-evaluated violation.
- `facts`: observed node IDs, labels and lexical surfaces; these are not claims of grammatical correctness.
- `diagnostics`: withheld/conflicting/missing evidence states.

Schemas: `grammar/explanation_evidence.schema.json` and
`grammar/explanation_templates.schema.json`. The versioned
`grammar/explanation_templates.json` contains repository-owned `sources` and
`templates` arrays. Production now contains the independently reviewed CLS-001 Cambridge teaching
note citing printed pp. 44–45 of the 2002 edition, and a B-R basic S/NP/VP
structural template citing pp.29–30 of the third edition. That template requires
exact immediate NP/VP children. Production grammaticality constraints remain disabled. Other
content remains gated; synthetic records exist only in tests.

## Publication gates

Every teaching template and cited source requires independent-review metadata,
reviewer identity/date and an accepted review state. Sources also require exact
title, edition, positive printed page, IMG/TXT evidence, approved status and a
resolved/compatible crosswalk. Duplicate IDs, missing citations, unreviewed
records and unsupported slots do not produce claims. Conflicting formulations
of the same `claim_key` are withheld. Only literal named slots are accepted;
attribute/index access and arbitrary runtime model prose are not templates.

Structural templates cite B-R only. Grammar/remediation cite Cambridge only.
Grammar constraints require a matching rule ID and actual evaluation outcome
(`when`: passed, violation or exception); remediation additionally requires a
violation. Non-constraint descriptions/classifications are teaching only, using
an explicitly reviewed `claim_type` and node-label match. Server-side runtime
rule eligibility remains governed separately by `grammar/runtime_registry.json`.
Client-supplied source metadata cannot enable a source/template or rule.

## Builder bridge and limits

The existing editor can construct a canonical branch/terminal subset and can
import supported normalized trees from the Generator's “Explore B-R tree in
Builder” action. It retains supported triangles/features/indices, checks graph
connectivity and serializes the actual learner graph. It never reparses the
sentence as a substitute for evaluating the graph. Legacy Penn categories are
not silently renamed; unsupported structures produce an unresolved message.
The bridge refuses movement, accepted-alternative and gap/elision imports that
it cannot preserve. Complete convention-aware editing, recovery and migration
remain M6 work. This bridge provides M3's shared-service integration without
claiming completion of M6.

The legacy diagnostic matrix/inspector remains visible and is separate from
reviewed book evidence. Model-proposed corrections stay advisory and cannot
promote an unverified sentence into an ungrammatical finding.

## Verification

```bash
python -m pip install -r requirements-test.txt
PYTHONPATH=server python -m unittest -v server.test_explanations server.test_explanation_transports
npm run test:evidence
# Requires runtime dependencies, models, Playwright and Chromium:
python scripts/test_explanation_browser.py
python scripts/test_explanation_browser.py --reviewed-fixture
python scripts/audit_source_readiness.py
```

A readiness report cannot independently review a source. It lists the records
and evidence that still need review before milestone 04 can publish lessons.

Legacy matrix verdicts/correction suggestions are diagnostic (`summary.verdict_authority = legacy_diagnostic`, `book_verified = false`). In Generator node cards, legacy linguistic explanation prose is withheld when the shared evidence response exists; reviewed claims are rendered separately under Book evidence. Builder graph/editor diagnostics remain separate. A teaching note never certifies an entire sentence.
