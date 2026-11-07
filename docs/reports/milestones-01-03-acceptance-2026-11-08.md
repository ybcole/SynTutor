# Milestones 01–03 acceptance and Milestone 04 handoff

Date: 8 November 2026 (Asia/Manila). This is the current status; earlier audit,
remediation and progress reports remain historical evidence.

## Decision

Milestones **01, 02 and 03 are complete for their approved scope**. Milestone 04
lesson/curriculum work may proceed. Milestone 04 itself has not been implemented
or accepted. No source gate or roadmap acceptance criterion has been removed.
The owner's standing approval and instruction to repair the blockers authorize
this source review and implementation sign-off; independent AI review is not
recorded as human approval.

M2 explicitly requires mapping only defensible analyses and permits unresolved
output. Completion therefore does not mean arbitrary V3–V10 Benepar conversion.
M3 requires reviewed claims and safe missing-evidence behavior, not enabling an
unreviewed constraint. The starter structural and grammatical teaching templates
now have actual source evidence. Runtime grammaticality coverage remains a
separate measurement, currently zero enabled Cambridge constraints.

## Blockers resolved

- Confirmed the supplied B-R chapters as *Analysing Sentences*, third edition,
  Pearson Education, copyright 2011, ISBN 9781408233740, printed pp.6–268. The
  chapter starts distinguish this edition from the fourth. Cambridge's 2002
  title/edition/ISBN and relevant pages were confirmed in the preceding review.
  Manifests record original filenames, hashes, page ranges and exceptions.
- Inspected selected B-R page images to resolve zero-word DET/C1 positions,
  the E elision marker, the introductory Sentence display, and unlabelled wh
  triangles. Schema 1.1.0 preserves those source distinctions; 1.0.0 remains
  supported for its original subset. No word or NP label is invented.
- Preserved the printed Chapter 9 tense anomaly as IMG_ANOMALY. Added the p.213
  PP alternative as TXT licensed by the discussion, distinct from a printed
  diagram. No broad corpus review status was silently upgraded.
- Independently checked the earlier basic S/NP/VP paraphrase against B-R
  pp.29–30 and published its narrowly matched structural template. The Cambridge
  CLS-001 teaching template remains a separate grammatical classification note.
  Each has concise/deeper text, page-level sources and sentence/node facts.
- Kept legacy matrix findings diagnostic. API summaries explicitly declare
  `book_verified: false`; Generator node cards with shared evidence withhold
  unreviewed matrix explanation prose. Diagnostic correction suggestions are
  labelled accordingly. Reviewed book claims are shown in the separate shared
  evidence panel. Unsupported Builder imports fail before clearing the analysis.
- Earlier integration repairs resolved the API contract conflict, parser test
  isolation, model-advisory verdict mutation, Vercel build exclusions, and Docker
  runtime COPY dependencies. Repository organization remains in the documented
  `web/`, `server/`, `grammar/`, `sources/`, `docs/planning/`, `docs/reports/` and
  `docs/research/` layout. No user-data migration is needed for these changes.

## Acceptance evidence

| Milestone criterion | Evidence |
|---|---|
| M1 inventory, architecture, authority, crosswalk and migration design | Existing inventory, ADR-001, authority matrix, compatibility plan and canonical schema; source manifests close bibliography gaps. Unverified raw crosswalks remain explicitly unresolved. |
| M2 canonical output and traceable mappings | `server/burton_roberts.py`, canonical JSON Schema, source receipts, exact source lookup plus conservative V2 transformation; raw candidate kept separately. |
| M2 gold validation and alternatives/unresolved output | All 211 sentence-aligned IMG records pass the approved envelope and JSON Schema. Full 252-record importer: 250 valid envelopes, two generic schematics explicitly unresolved. Source-anomaly and TXT alternative metadata retained. |
| M2 API/error and existing behavior regressions | Flask, stdlib and hosted contracts; parser-backed sentence selection, corrections, failure handling and LF/CRLF; legacy licensing/corrector and JavaScript regressions. |
| M3 shared service and consistent rendering | Generator and Builder use `/api/explain` and the shared evidence renderer; real Chromium compares identical rendered evidence for production templates and a separate synthetic fixture. |
| M3 substantive claims traced and authorities separated | B-R pp.29–30 structural template; CGEL pp.44–45 classification template; separate structural/grammatical/remediation channels. Client provenance cannot bypass server-owned registries. |
| M3 sentence/node specificity and concise/deep content | Exact S child-shape match, observed node ID/label/surface slots, deeper details; browser and unit checks. Raw parser IDs are not substituted for canonical node IDs. |
| M3 missing/conflicting/unverified/unresolved cases | Review/title/edition/page/crosswalk gates, conflict and forgery tests, `NO_BOOK_BASIS`, `SOURCE_CONFLICT`, `ANALYSIS_UNRESOLVED`; no unrestricted runtime LLM explanation source. |

Local checks: 121 combined model-free tests, 34 canonical gold tests, six real
parser tests, LF/CRLF regression, all eleven chapter validators, legacy
licensing/corrector regressions, three JavaScript suites, static build, Vercel
upload-filter reproduction, runtime packaging fixture, and both Chromium evidence
parity modes. CI runs the corresponding suites on the publishing PR before merge.
Browser tests isolate third-party authentication requests and advisory CoLA;
these checks do not certify production auth or deployment security. Runtime
packaging is a COPY/import fixture, not an actual Docker image build.

The older `server/br_tree.py` compatibility projection still reports 210/211,
with p.24's introductory Sentence display unresolved under its stricter V2
policy. It is not the Generator's approved-envelope normalizer; the approved
path reports 211/211. Its conservative rejection is retained rather than
silently changing the printed display.

## M4 entry and publication rules

`python scripts/audit_source_readiness.py --require-ready` passes: one reviewed
B-R structural starter template, one reviewed Cambridge grammatical teaching
starter template, and both bibliographic manifests. Missing/unreviewed starter
sources still fail the gate in tests. `runtime_constraint_coverage_ready` remains
false. This separates instructional prerequisites from executable constraint
coverage; it does not certify all extracted records or complete the curriculum.

For M4, author the curriculum map, objectives/prerequisites, source-linked lesson
records, worked examples and accepted alternatives; review each lesson and each
additional template before publication. Implement versioned progress and the
specified lesson reward behavior under the roadmap. Do not treat an inventory
or structural validation run as independent linguistic review of every fixture.

Residual coverage limits are explicit and do not block this scoped handoff:

- The other 195 Cambridge merged records are not independently re-certified.
  CLS-002 needs narrowing; PHR-011 needs full scope/exception review. They and
  their raw unresolved crosswalks stay outside production runtime eligibility.
- Generic ch1-ex1/ch2-35 schematics are not canonical linguistic analyses.
- Free-form unsupported constructions stay unresolved; a structural teaching
  note is not a full grammaticality verdict. The canvas is labelled as the raw
  diagnostic candidate; canonical data is in the response and supported Builder
  view. Full chapter-aware editing/migration is M6.
- Full linguistic recertification of every corpus record, live database/auth
  security, production latency and release certification remain later work.

Rollback: revert this PR for the source/schema/template extension, retaining the
prior merged API contract. No database/content-progress rewrite or PDF upload is
committed. The schema's legacy acceptance and refusal of unsupported editor
imports protect existing serialized structures.

Source review receipts: `sources/burton_roberts/reviews/2026-11-08-conventions.json`
and `sources/cambridge/reviews/2026-11-08-cls-001.json`. No source PDF, page image
or full chapter prose is committed to the repository.
