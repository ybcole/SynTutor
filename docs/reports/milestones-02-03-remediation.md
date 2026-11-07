# Milestones 02–03 remediation

Date: 7 November 2026 (Asia/Manila). This report supersedes the software-blocker
findings in `milestones-01-03-audit.md`; that audit remains historical evidence.

## Result and remaining gate

The M2 implementation branch and repository organization are integrated, with
source/API/transport/test defects repaired. M3 now has a shared composer,
versioned evidence/template schemas, all three transports, canonical Builder
bridge, one browser evidence component, and unit/HTTP/browser coverage.

**Do not mark M2 or M3 fully complete or claim milestone 04 is unconditionally
unblocked.** The original sources' exact edition/page metadata and independent
review/crosswalk decisions are not established by fixing code. The production
Cambridge runtime registry enables zero rules; the production explanation
registry has zero reviewed sources/templates. The system therefore withholds
unsupported claims instead of inventing book evidence. Publishing source-backed
lessons still requires the selected actual records/templates to pass those gates.

Existing source-shaped E markers and ambiguous/unsupported mappings remain
explicitly unresolved; no source record, gold answer, review status or approval
criterion was rewritten to make tests green. General arbitrary V3–V10 Benepar
conversion is not claimed. The approved conservative adapter handles supported
structures and otherwise fails safely.

## Software fixes

- Integrated PR #30's canonical-envelope/transport/evaluator improvements with
  PR #31's organized layout. Resolved the API-documentation merge conflict by
  retaining the newer M2 contract; relocated planning files preserve M2 edits.
- Replaced the broken main API path with the consolidated M2 contract: chapter,
  Appendix D1 and variety are validated; `br_analysis` is the canonical envelope.
  The old undefined `chapter` call and discarded second envelope are gone.
- Fixed two invalid continuation sequences in the gold test module, updated a
  stale diagnostics assertion to the documented `parser_diagnostics` field, and
  implemented narrowly scoped sentence-final punctuation handling. Medial
  punctuation remains unresolved rather than being silently discarded.
- Isolated API test stubs so they do not replace real parser/matrix modules for
  subsequent tests. Model-backed tests execute in a separate process.
- Removed promotion of model-proposed edits into grammatical rule violations;
  the advisory helper cannot mutate verdict/findings, verified by a regression.
- Added `POST /api/explain` to Flask, stdlib and hosted ASGI. It validates bounded
  canonical requests, rejects client registries, and uses repository-owned
  reviewed templates/sources. Grammatical rule claims use server evaluations;
  reviewed classifications are teaching only.
- Added structural/grammatical/remediation channels, citations, concise/deeper
  text, conflict/missing-source/unresolved states, and matching schemas.
- Wired Generator and Builder to one endpoint and renderer. Builder serializes
  the learner graph; the supported canonical import path retains triangles and
  the selected chapter. A real browser caught and verified the fix for a
  chapter/source-metadata mismatch in the new exporter.
- Improved malformed-input handling, source-readiness reporting and CI coverage;
  corrected the advertised Benepar installer command. Parser CI installs CPU
  PyTorch before resolving requirements to avoid unnecessary CUDA packages.

## Verified checks

Local environment: Python 3.12, spaCy 3.8.16, Benepar 0.2.0, transformers 4.46.3,
PyTorch 2.15.0; en_core_web_md 3.8.0 and benepar_en3 loaded and parsed real input.

| Check | Result |
|---|---|
| Backend `compileall` | Passed |
| Combined model-free normalizer/schema/API/transport/evaluator/detector/explanation tests | 106 passed |
| Canonical gold unit suite | 34 passed |
| Parser-backed runtime suite | 6 passed, including actual multi-sentence and independently corrected parses |
| Existing LF/CRLF parser regression | Passed |
| All 11 B-R chapter validators | Passed |
| Read-only 252-record importer audit | 203 normalized, 49 explicit unresolved, no invalid outputs |
| Approved-envelope API path over 211 aligned IMG records | 177 normalized/schema-valid, 34 explicit unresolved; separate from the older projection's 210/211 count |
| Legacy licensing corpus | 19/19 bad detected; 16/16 good not rejected |
| Existing corrector regression | Passed |
| JavaScript correction, quiz-content and evidence bridge checks | Passed |
| Static build and modified JavaScript syntax checks | Passed |
| Chromium Generator → Builder real HTTP/rendered-evidence parity | Passed with production empty-registry state |
| Chromium parity with synthetic reviewed test fixture | Passed; fixture is never written to production registry |
| Browser HTML injection / deeper-details rendering | Passed |

Browser tests use real parsing, canonical serialization, HTTP endpoints and
rendering. Third-party auth requests and advisory CoLA are isolated in the test;
this is not a production authentication/deployment certification. The six real
parser tests likewise isolate advisory classification so model outputs do not
decide the canonical contract. The runtime unit run took under 10 seconds locally;
this is a smoke result, not a production latency SLA.

Relevant commands are in the CI workflows and `docs/explanation-engine.md`.
Source readiness can be inspected with `python scripts/audit_source_readiness.py`;
`--require-ready` exits nonzero while the content gate remains unsatisfied.

## Acceptance review

| Area | Verified | Open |
|---|---|---|
| M2 schema/normalization/errors | Canonical supported output, unsupported/unresolved paths, token/correction metadata, transport contracts, actual parser regressions | Broader source-supported construction coverage and source anomalies remain explicitly unresolved |
| M2 source/rule boundary | CoLA advisory, fail-closed runtime registry/evaluator, synthetic primitive and exception tests | No independently reviewed production Cambridge rule enabled |
| M3 shared use/parity | Generator and Builder endpoint/component, canonical graph bridge, real browser parity in both tested registry states | Full editing/migration beyond bridge remains M6 |
| M3 claims/provenance | Reviewed citation gates, source separation, specific node facts, conflict and forgery tests | Actual production-reviewed templates and reviewed real-source sample explanations |
| M3 safe failures | Missing/invalid/conflicting/unresolved states, three transport checks, request bounds | Original book edition/independent-review evidence cannot be manufactured in code |

## Data, rollout and tracker impact

No database/user-progress migration is performed. Runtime rule allow-list and
teaching templates remain empty by design. The new service is additive; the
legacy diagnostic payload remains available. Install runtime requirements to
include JSON Schema validation; hosted Gradio already supplies Starlette.

M1 remains complete for its approved documentation scope. M2 and M3 remain
unchecked while the source/coverage acceptance issues above are unresolved.
M4 curriculum planning can be prepared, but do not publish unreviewed lessons
or claim its dependency gate has been met. No approval question is needed for
the completed software fixes; actual source evidence/review is still required.

## Vercel build blocker repaired

The first integration preview failed. A checkout filtered by the original
`.vercelignore` reproduced `FileNotFoundError: server/ruleset.py` because the
configured static content build reads three backend source modules as text.
The ignore file now includes only those three build inputs while excluding the
rest of the backend. `scripts/test_static_build.py` reproduces the upload filter
and verifies the build and absence of backend files from public `dist/`. This
check is also in model-free CI. No backend source is copied into the public app.

Before this deployment fix, both integration GitHub Actions workflows passed
on commit `75e22fcf89097dc20baf505c3dda43c93a953dcd`:
[model-free/build run](https://github.com/ybcole/SynTutor/actions/runs/42388090996)
and [parser/browser run](https://github.com/ybcole/SynTutor/actions/runs/42388090924).
The final PR checks cover the deployment fix as well.
