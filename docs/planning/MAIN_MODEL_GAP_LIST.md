# Main Model Gap List

**Status:** not release-complete. This register covers the syntax/grammar model,
not lessons or quizzes (U03 is excluded by owner decision).

## Completed in the current working tree

- Authority manifest attached to `/api/parse`.
- Legacy details bound to canonical B-R nodes (`canonical_node_id`).
- Unified findings with explicit `legacy_matrix` / `cambridge_candidate`
  authority and claim status.
- Exact-node legacy diagnostics in the UI; candidate-only red marks.
- 112 legacy rules inventoried and dispositioned (62 port candidates, 50 keep
  legacy diagnostic).
- PR #169 audit/adapter files, CONVENTIONS update and held-out sentence file
  brought into the working tree.
- FINAL-D1 disposition register: 252 record decisions and 130 instance
  dispositions (126 chapter-only, 4 source anomalies, 0 unresolved). All 41
  construction-triage instances now have a disposition.
- Adapter/catalog rules added for Ch3 coordination, Ch5 adjuncts, Ch6 auxiliary
  gaps, Ch8 clause/scaffold shapes and Ch9 extraposition; passive extraposition
  now normalizes in a parser-backed test.
- AI adapter-derived gold baseline: 20/20 normalized, explicitly not
  independent gold.
- Audit passes: 252 records, 130 instances, 0 Penn label leaks.
- B-R tests: 63 passing. Canonical availability: 283/326 evaluation cases,
  20/20 on the probe set.

Available evidence is availability/schema evidence, not exact B-R accuracy.

## P0 — exact tree correctness

| Gap | Current state | Completion evidence |
|---|---|---|
| Authored FINAL-D1 gold suite | AI draft baseline exists at `evaluation/br_final_d1_gold.json` (20 adapter-derived entries, owner-waiver provenance). It is **not** independent gold and the 20/20 adapter match is circular. | Complete non-adapter-derived ordered trees, accepted alternatives, near negatives, development and frozen held-out splits, authored from fixtures + CONVENTIONS |
| 41 construction instances | Dispositioned: 26 matched by reusable catalog rules, 15 adjudicated chapter-only; 0 unresolved | Figure/path-level proof remains in the disposition register and catalog tests |
| 252 record adjudication | Record decisions currently retain transcriptions and mark review pending | Per-record profile, shape, alternatives, anomalies and exact test |
| Exact accuracy measurement | **184/195 normalized source fixtures exact (94.36%)**; 29 source fixtures unresolved; held-out grammatical corpus 281/281 normalized | Resolve the 29 source-fixture gaps and 11 exact mismatches; author non-adapter free-sentence gold; report false-canonical and ambiguity metrics |

## P0 — adapter completeness

The master list requires S02–S10 and P01–P09. Still missing:

- explicit Benepar-to-B-R transformation table by construction/profile;
- lexical frame evidence for Ch4 complement type, auxiliary role, particles,
  sense ambiguity and Ch10 Type I/II;
- NP → DET/NOM, VP auxiliary/adjunct layers, S-bar/S-dbar, coordination and
  nonfinite structures;
- wh/passive/fronting/gap/empty-C/ellipsis/control/co-index licensing;
- local transformation validation for selection, scope, agreement, attachment;
- accepted alternatives and explicit unresolved outcomes;
- negative integration tests preventing Penn labels, model scores or Cambridge
  claims from becoming B-R proof;
- versioned analysis identity by source/profile/derivation/tokenizer.

## P0 — one contract and product integration

- S05–S10: schema/importer/validator/Builder/renderer agreement for E, empty
  DET/C1, triangles, covert subjects, indices, movement, features, punctuation
  tokenization, ambiguity, provenance and pagination.
- U01 Generator: canonical vs working status, profile, uncertainty and parser
  diagnostics.
- U02 Builder: round-trip every node variant, profile, source, span, index,
  movement link and alternative.
- U04 XAI: structural claims tied to B-R evidence; Cambridge claims tied to
  separately reviewed records and exact governing nodes.
- U05 Corrections: reparse repaired text, preserve offsets, never infer
  whole-sentence correctness from partial checks.
- U06 Transports/storage: audit browser, server, hosted API, old lessons,
  database and exports for old schema/Penn consumers.
- U07 Documentation: reconcile stale Generator/API claims, V2-only statements,
  old Cambridge counts and legacy contracts.

## P1 — production grammar authority

- Cambridge runtime rules enabled: **193 owner-waived pilot rules** (187 primary
  + 6 supporting), not independently reviewed.
- Remaining candidate pilots: **0**; **11 deferred semantic specifications**
  remain outside runtime.
- Missing: independent linguistic review, resolved B-R crosswalk slices,
  held-out detector precision/recall, exception/variety coverage and explicit
  runtime registry entries.
- Legacy matrix remains the only production detector and is still Benepar-based.
- Full canonical detection routing is not complete; unified findings are an
  evidence-layer bridge, not a replacement detector.

### Current runtime measurement

`scripts/audit_cambridge_runtime_holdout.py` reports, with all 193 implemented
rules enabled:

- grammatical held-out sentences: **281/281 normalized**, **0 working trees**,
  **0 sentences with a Cambridge finding**, 0 total findings;
- ungrammatical held-out sentences: **45/45 have a tree** (29 normalized,
  16 working), **0 Cambridge findings**; the corpus is legacy agreement data
  not covered by the Cambridge candidate set, so this is a coverage statement,
  not detector accuracy;
- no held-out sentence is left without a tree.

Working trees retain provisional grouping/triangles and are labelled as working;
they are not counted as normalized Cambridge-evaluation inputs. The zero
false-positive result is after fixing the `CLS-1325` “hands in her pockets”
particle-pronoun false positive.

## P1 — evaluation and release gates

- No held-out detector precision/recall for the 187 candidates.
- No false-canonical rate or ambiguity recall for the Generator.
- No independently adjudicated held-out grammaticality/error diagnoses.
- No release table comparing exact gold accuracy, availability, unsupported
  cases, alternatives and latency.
- The two CI workflows must pass on the final commit, with both FINAL-D1
  coverage artifacts uploaded.

## P2 — independent review

AI source checking can complete implementation work, but it must not be
recorded as independent human certification. Production Cambridge activation
and any “independently verified” claim require a genuinely separate reviewer.

## Definition of done

Per `ABSOLUTE_SYNTAX_MASTER_LIST.md`: every S02–S10, P01–P09 and U01–U07 entry
has a recorded disposition and linked proof; all 252 fixtures and 130 catalog
exceptions have outcomes; the public tree contract round-trips; and frozen gold
suites pass at **100% exact complete-tree agreement across accepted alternatives
for the declared supported constructions**, with zero false canonical claims.

## Next order

1. Author the gold suite for the 20-sentence held-out probe and a small
   development split, starting with simple Ch2/Ch4/Ch7 clauses.
2. Use the completed construction dispositions as the baseline for adapter parity tests.
3. Complete S05–S10 and P01–P05 against those fixtures.
4. Add P06 alternatives, then U01/U02/U04/U05/U06/U07.
5. Run both CI workflows and publish exact accuracy with denominators.
