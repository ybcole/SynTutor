# Milestones 01–03 verification

Audit date: 8 November 2026 (Asia/Manila). Repository read on 7 November UTC.

## Decision

| Milestone | Verified disposition | Reason |
|---|---|---|
| 01 Architecture/source governance | Complete for its approved documentation scope | Inventory, ADR, authority matrix, crosswalk inventory, Benepar compatibility plan, canonical schema and migration documentation are present; the plan records owner approval. Source verification follow-ups remain explicitly open. |
| 02 Syntax Generator | Incomplete; blocked | Main has a reproducible API NameError. PR #30 has substantial additional code and 83 passing model-free tests, but is draft/unmerged, its gold test file does not compile, and model-backed acceptance is unverified. |
| 03 Shared explanation engine | Not integrated; incomplete and dependency-blocked | Neither main nor the named M3 branch contains the shared service/schemas/templates described by the attachments. Generator/Builder shared-service parity is absent and M2 is incomplete. |

Do not check milestones 02 or 03. The cleanup does not repair parser code or merge implementation PRs.

## Revisions and references inspected

- Main: `b51d045ff9a0048c4be9cf20f8318307d322a058`.
- M2 PR #30 head: `d70443c77a53194d83399d5b0d2ae9b9153a6fed`, `feature/milestone-02-completion-2026-11-07`.
- `feature/milestone-03-shared-explanations-2026-11-07` resolves to the same commit as M2; its diff against M2 is empty. A branch name is not implementation evidence.
- User attachments: `TEST_RESULTS.md` and `README (1)(1).md`. These describe an isolated patch, 16 composer tests, no complete-checkout integration and no UI parity. They contain no actual service, installer or patch to apply.
- Reviewed the authoritative plan/checklist, detailed Generator/other prompts, M1 governance deliverables, M2 progress reports, API/transports/normalizers/registry, frontend tree call sites, schemas, fixtures, tests, build/deployment configuration, open PR metadata and latest workflow metadata.

## Acceptance review

### Milestone 01

All eight documentation deliverables are present: inventory; ADR; authority matrix; crosswalk evidence-status inventory; normalization/rejection/alternatives plan; canonical schema/migration proposal; risk/source-gap list; documentation-only M1 change record. The owner approval record is in the authoritative execution plan. This recheck verifies the documents exist and accurately retain uncertainty; it does not independently confirm the missing original source PDFs or bibliographic editions. All crosswalk mappings being unverified is a documented limitation of the approved inventory, not verified linguistic equivalence.

### Milestone 02

| Criterion | Main / current branch evidence |
|---|---|
| Approved canonical schema in Generator output | Main computes a new envelope using undefined variables and does not expose it; M2 branch has API/schema tests that pass, but remains unmerged. |
| Traceable, defensible normalization | Conservative exact-source and narrow V2 projection exists; unsupported mappings remain unresolved. No general V3–V10 transformer is demonstrated. |
| Gold examples and structural checks | Main focused suite exercises the 211 aligned IMG records: 210 normalize, `ch2-2` remains unresolved. M2 read-only 252-record audit: 203 normalized/49 unresolved, no invalid imported outputs. These are different populations/contracts, not contradictory counts. M2 gold unit suite cannot import due to SyntaxError. |
| Unresolved and alternative analyses | Covered in passing model-free tests for supported scope; unresolved records are not proof of broad parser coverage. |
| API contracts and errors | Main suite fails with four NameErrors. M2's 83-test run includes API, Flask, stdlib, registry/evaluator, schema, corpus and detector tests. Model-backed transport behavior remains unverified. |
| Required Generator regressions | Legacy licensing/corrector and JavaScript checks pass on main. Real models are unavailable here; six runtime tests error before proving behavior. Full-suite acceptance cannot be claimed. |

### Milestone 03

| Criterion | Disposition |
|---|---|
| Generator and Builder call the same service / consistent rendering | Not met; no shared service integrated. Attachment explicitly defers Builder wiring to M6, conflicting with M3's own acceptance criterion. |
| Source-traceable substantive claims | Not demonstrated in repository; empty production allow-list and outstanding source/review gates prevent reviewed production examples. |
| Separate B-R structural vs Cambridge grammatical explanations | Proposed by isolated package; not integrated/verified. Existing deterministic matrix explanations are not this M3 service. |
| Sentence/node/function/feature-specific evidence | No integrated M3 evidence contract or service to verify. |
| Missing/conflicting/unverified sources fail safely | The registry has fail-closed checks, but these do not substitute for M3 composer coverage. |
| Correct/missing/conflicting/unresolved explanation tests | Attached 16-test claim belongs to a separate patch workspace; no corresponding `server/test_explanations.py` exists on inspected branches. |

## Concrete conflicts and blockers

1. **Main API runtime failure** — `server/api.py:188` passes `chapter` and `appendix_nom`, neither defined in `build_payload`. Four API tests raise `NameError: name 'chapter' is not defined`. The computed `canonical_analysis` is also absent from the returned payload, while `web/js/main.js` checks that field; API metadata instead refers to `br_analysis`. This is an incomplete/conflicting contract integration.
2. **M2 test SyntaxError** — at PR #30 head, `server/test_burton_roberts.py:667` ends a context-manager line with two backslashes. Both `compileall` and `python -m unittest -v server.test_burton_roberts` fail to import the file. Passing the separate 83-test group cannot certify this suite.
3. **Parser/model evidence missing** — torch, spaCy, Benepar and configured models are absent in this audit runtime. Six `test_parser_runtime` tests error with missing `torch`. These are environment-blocked checks, not demonstrated linguistic failures. Model installation/performance, real correction reparsing and multi-sentence parsing remain unverified.
4. **Actions fails before tests** — latest inspected run [42377374184](https://github.com/ybcole/SynTutor/actions/runs/42377374184), M3 branch at the same M2 SHA, reports `startup_failure`, `path=BuildFailed`, and zero jobs. The preceding four inspected runs also report startup failure. No job output exists to establish the root cause; a GitHub platform registration diagnosis remains a hypothesis, not a proven cause.
5. **Source gates** — zero production Cambridge rules are enabled; exact editions/pages and independent review/crosswalk evidence remain open. PR #30 adds a restricted evaluator primitive, but it does not provide reviewed runtime grammatical coverage. `ch2-2`'s stored `Sentence` root still conflicts with V2 conventions.
6. **Roadmap/package scope conflict** — M3 requires both interfaces to consume one service; the attachment defers Builder integration. The attachment says `master_prompt_others.md` was missing in its workspace, but it exists in this checkout (now `docs/planning/`). Reconcile actual current prompts before applying a version-sensitive installer. Only the README/test-results attachments were supplied, not the installer or implementation patch.
7. **Branch/document divergence** — M2 improvements are not merged into main. Existing progress files mix earlier successful checks and later unexecuted changes; this audit identifies exact tested revisions. Historical `_updated` copies are now archived to reduce competing sources of status.
8. **Cleanup integration risk** — PR #30 was reported mergeable, draft, and `mergeable_state=unstable` before cleanup. It updates the plan/checklist/report files moved here. Future merge may require carrying those edits to the relocated files; no textual merge conflict is claimed without a merge attempt.

The canvas still renders `payload.tree` (raw diagnostic tree). This limits current user-facing canonical behavior. Full renderer/Builder migration also has later milestones; do not silently redefine M3's explicit shared-service criterion as solely M6 work.

## Checks actually executed

Local Python 3.12, lightweight JSON Schema/Flask/morphology dependencies installed. Tests used separate main and M2 worktrees.

| Revision | Exact command / procedure | Result |
|---|---|---|
| Main | From `server/`: `python -m unittest -v test_burton_roberts test_br_tree test_cambridge_registry test_br_tree_fixtures test_br_tree_schema test_api_contract test_webapp_contract` | 36 tests, 4 errors (NameError); other 32 passed. Embedded aligned IMG audit: 210/211 normalized. |
| M2 head | From `server/`: `python -m unittest -v test_br_tree test_cambridge_registry test_cambridge_evaluator test_grammar_schema test_br_tree_fixtures test_br_tree_schema test_api_contract test_webapp_contract test_stdlib_transport_contract test_detector` | 83 tests passed. |
| M2 head | `python -m compileall -q server` | Failed: SyntaxError at gold test line 667. |
| M2 head | `python -m unittest -v server.test_burton_roberts` | Failed to import: same SyntaxError. |
| M2 head | `python scripts/audit_burton_roberts_import.py --expected-count 252` | Passed: 252 records; 203 normalized/49 unresolved; no failures. |
| M2 head | From `server/`: `python -m unittest -v test_parser_runtime` | 6 errors, missing torch; no real model-backed success claimed. |
| Main | Run each `validate_ch01.py` through `validate_ch11.py` in `web/content/book/`; check exit and failure markers | All 11 passed. |
| Main | From `server/`: `python test_licensing.py` | 19/19 bad detected; 16/16 good not rejected. |
| Main | From `server/`: `python test_corrector.py` | Passed. |
| Main | `npm run test:correction` | Passed. |
| Main | `npm run test:quiz` | Passed. |
| M2 head and organized main | `npm run build` | Passed. Generated sheet changes were discarded, preserving checked-in content. |
| Organized main | `git diff --check`; compare tracked runtime blobs and built assets to original main | Passed; no runtime source/content change from organization. |

No full-suite, browser, deployed-host, source-PDF verification or successful current-head Actions run is claimed.

## Organization and migration

Moved planning files to `docs/planning`, research drafts to `docs/research`, progress report to `docs/reports`, historical snapshots to `docs/archive`, and obsolete root browser files to `archive/legacy-web`. Rebased Markdown links, added navigation/layout documentation and corrected stale documentation claiming tests were excluded. Governance and deployment entry points remain at root. See [relocation table](../repository-layout.md).

No runtime API/schema, database, learner data or linguistic source record changed. No milestone boxes changed: existing M1 complete / M2–M3 incomplete tracker state is retained. Pending implementation PRs require ordinary review and integration; no additional user approval is needed to keep auditing or prepare fixes within the requested scope.
