# SynTutor — Burton-Roberts Native Engine: Construction Specification

**Revision:** 9 November 2026. **Implementation branch:** feature/br-native-grammar-2026-11-09.  
**Book authority:** Noel Burton-Roberts, *Analysing Sentences: An Introduction to English Syntax*, Third Edition, Pearson Education, copyright 2011, ISBN 9781408233740.  
**Source:** attached complete 297-page third-edition PDF; existing CONVENTIONS.md; source manifest and Chapter 1–10 tree records. Printed page numbers differ from PDF page indices.

> **Audit status:** This is the source-grounded construction specification and first runtime increment, NOT certification of full native B-R parsing on unrestricted English. All generated labels, edges, features, empty positions and movement relationships must be justified. Ambiguity may require multiple analyses or an unresolved response.

## 1. Invariants and division of authority

1. Burton-Roberts Third Edition determines target *phrase-marker hierarchy, lexical/phrase labels, chapter versions, features, triangles, gaps, indices, control, and ellipsis*. Its syntax cannot be obtained simply by renaming a Penn Treebank tree.
2. Benepar/spaCy contribute *candidate evidence*—tokens, POS, dependencies, proposed spans and attachments—not final B-R labels.
3. Cambridge provides broader grammatical constraints or explanations, independently attributed; it never silently overrides a B-R tree.
4. Chapter exercises use V1–V10 as the book introduces them. Free-form generation uses FINAL-D1, cumulative through Chapter 10 with Chapter 7 Appendix NOM.
5. Syntactic *functions* (subject, predicate, complement, adjunct, head, direct object) are derived from tree relationships, not separate invented phrase-marker nodes.
6. The raw Benepar diagnostic remains available only in an explicitly labelled, opt-in view. Never silently fall back to it when a B-R tree is unavailable.
7. A syntactically well-formed tree shape is not necessarily the correct interpretation or a grammaticality verdict. Validation, semantic licensing, and human evidence are distinct.
8. Unresolved attachments, unsupported constructions, lexical-frame uncertainty and ambiguity must remain visible. Never fabricate covert subjects, gaps, overt words, or source citations.
9. Retain exact token order, character spans, source profiles, accepted alternatives and independent source-review status.
10. Only an independent linguistic audit plus passed held-out testing may authorize claims of externally verified accuracy; no finite program can be literally error-proof on all English.

## 2. Third Edition conventions we must honor

| Printed pages | Requirement |
| --- | --- |
| Preface ix–x | Vgrp removed; every auxiliary heads its own VP and takes a VP complement. Name/pronoun labels introduced; C/C1/C2; S′/S″; gap •; lowest numbered VP is VP1. |
| Chapter 1, 6–23 | Constituents are hierarchical and word spans must have defensible grouping; triangles denote unanalyzed constituents. |
| Chapter 2, 24–45 | S can comprise subject NP + predicate VP; distinguish head, modifier, complement and sisterhood without extra function nodes. |
| Chapter 3, 46–66 | NP, AP, AdvP, PP and lexical categories; names and pronouns can be complete NPs. In relevant uses now/then/when and here/there/where are prepositions; PP can consist of P alone. Coordinate constituents must be category-compatible. |
| Chapter 4, 67–86 | Lexical V frames: trans, intrans, ditrans, intens, complex, prep. A child's position alone does not determine the verb's lexical licensing. |
| Chapter 5, 87–110 | VP1 nested inside a larger VP with adjunct PP/AdvP; verb particles, ellipsis E, VP-adverbials versus S-adverbials. |
| Chapter 6, 111–140 | MOD/PERF/PROG/PASS/TENSE recursive VP structure; tense and negation; do-support, question auxiliary fronting and gap. |
| Chapter 7, 141–170 | DET, NOM recursion, empty DET, pre-determiners, possessives, quantifying modifiers, adjective complementation, Appendix NOM refinement. |
| Chapter 8, 171–195 | S′/C/S for complements and clauses; PP with temporal prepositions taking S; since also has a causal C reading that requires disambiguation. |
| Chapter 9, 196–223 | S″/C2/S′/C1, wh-fronting, relative clauses, gaps and alternatives; do not rename SBARQ without rebuilding hierarchy. |
| Chapter 10, 224–253 | Nonfinite S and [-tense], covert controlled NP subjects, indices, Type I vs Type II V complement patterns. |
| Chapter 11, 254–268 | Methodological explanations rather than a new phrase-marker convention file. |

## 3. Intended complete runtime architecture

~~~text
Input and sentence/token offsets
      |
Candidate evidence: spaCy, Benepar, optional independent parser
      |
Book-backed lexicon, construction patterns, lexical frames,
feature-unification rules and reviewed exceptions
      |
NATIVE B-R CANDIDATE GENERATOR
  chart/agenda parser with packed alternative subtrees;
  NP/NOM and auxiliary/VP recursion; wh movement/gaps;
  controlled nonfinite subjects; ambiguity hypotheses
      |
Independent rule licensing and canonical structure checker
      |
Lexical selection, semantic frame and interpretation review
      |
Canonical B-R tree + derivation trace / accepted alternatives
      OR working/unresolved analysis
      |
Generator, Builder, Lessons, Quizzes and explanations
~~~

The existing FINAL-D1 projection is a **first construction adapter**. The new experimental bounded native chart constructs **a narrow subset of finite clauses** independently of Benepar tree shape; it has no full lexical frame system, movement/wh/control analysis, or grammaticality authority. On an unresolved free-form analysis, the Generator API can expose candidates in a separate `br_analysis.native_chart_candidates` diagnostic field, never as the canonical `tree` or a verified grammaticality verdict. Neither module is the complete chart/unification parser pictured above. We preserve both while validating independent layers. A new parser should be evaluated on unseen sentences where Benepar's top-ranked attachment is wrong, rather than trained solely to copy Penn trees.

## 4. Current implementation increment and files

| File | Change |
| --- | --- |
| grammar/br_native_constructions.json | Added **100 explicit structural signatures** across the chapter sequence and **10 semantic/notation obligations**. Each contains stable ID, book pages, chapter gate, and independent-review-pending status. |
| server/br_native_grammar.py | Added registry loading, source metadata checks, profile-based branch recognition, Penn-only label leak detection, transparent rule IDs, and unknown-coverage reporting. |
| server/br_native_chart.py | Added a **bounded experimental native chart candidate generator** composing simple new S/NP/VP/PP/AdvP structures from tagged tokens without copying Benepar's constituency tree. It deliberately returns candidate or unresolved, not verified/canonical. |
| server/burton_roberts.py | Attaches a separate br_rule_verification report to generated canonical/working trees. Raw diagnostics stay separate. An explicitly illegal Penn label blocks normalized promotion. |
| server/final_d1_projection.py | Projects now/then as P-only temporal PP where applicable, considers when as a PP wh-gap, and conservatively marks subordinate since unresolved until temporal-P vs causal-C interpretation can be resolved. |
| web/js/main.js | Raw Benepar renderer is hidden by default when B-R analysis fails; diagnostic toggle remains available. |
| web/js/syntax-builder.js | Early pedagogical Sentence/Phrase/PHRASE placeholders are excluded from later profile palettes. |
| scripts/audit_br_native_catalog.py | Added a reproducible book-corpus branch-coverage report over 252 source records. |
| web/js/canvas-view.js | Restored the missing canonical B-R tree viewport module, enabling pan, zoom and retained node interactions. |
| server/test_br_native_grammar.py | Added model-free tests for the registry, chapter gates, recognized triangles, unresolved shapes, source-review state and raw Penn category leakage. |
| server/test_br_native_chart.py | Added tests for simple productive finite clauses, lexical valency, empty DET, VP adjunct recursion, temporal P-only PP, and fail-closed unknown verbs. |

**These changes do not rewrite the 252 existing source records, migrate Supabase data, replace Benepar, integrate an unrestricted chart parser, or claim linguistic completeness.** The new bounded chart is a demonstrator only.

## 5. Construction catalog format and interpretation

The new JSON catalog has a version, explicit rule list, and separate semantic obligations. Each structural record has:

- id: stable source-linked identifier (example BR05-VP-PP-ADJUNCT);
- chapter_introduced: first license version, not a claim that every later sentence fits;
- parent and ordered children: a *shape* signature, including @word lexical leaf symbol (never a Penn POS tag);
- source.printed_pages, evidence type and review status;
- condition: limitations which **are not evaluated by a pure shape match**.

For example:

~~~json
{
  "id": "BR05-VP-PP-ADJUNCT",
  "chapter_introduced": 5,
  "parent": "VP",
  "children": ["VP", "PP"],
  "condition": "Higher VP contains basic VP and optional PP adjunct."
}
~~~

The above can identify a branch, but cannot prove the PP is an adjunct rather than a selected complement. A correct later compiler will additionally require lexical verb frames and attachment constraints.

The catalog is deliberately labelled DRAFT and each rule is marked NEEDS_INDEPENDENT_EXAMPLE_AUDIT. It is **not** falsely presented as 100 exhaustively human-reviewed construction rules. A source-matched chapter diagram is not by itself a statistically valid generalization.

## 6. Rule verification output semantics

The model-independent audit returns:

- source_matched_unreviewed: exact IMG-reference match, still awaiting full independent source-tree certification;
- shape_covered_semantics_unverified: all examined branches have a matching catalog signature, semantic licensing not independently checked;
- partially_covered: some branches are not in the current rule list; lack of catalog coverage is not proof of ungrammaticality;
- invalid_label: forbidden Benepar/Penn-only category leaked into purported canonical tree;
- audit_unavailable: audit failed; never treat as source-certified.

All results retain matched/examined counts, source rule IDs/pages, uncovered patterns and explicit fields semantic_conditions_checked=false, independent_linguistic_review=false, may_certify_grammaticality=false. A structurally normalized tree must **not** be advertised as independently book-verified solely because it has no uncovered patterns.

## 6A. Initial catalog recognition baseline (9 November 2026)

A read-only comparison of the **100 draft signatures** against all 252 stored chapter-tree records identified **1,382 of 1,558 existing branch shapes (88.7%)** using chapter introduction gates. This is a match of local parent/child label signatures only: **it is not 88.7% grammar accuracy, full B-R compatibility, or successful on-the-fly parsing**.

**13 November 2026 audit update:** the catalog now recognizes the raw book's unlabelled C2 wh triangle, NP-over-E ellipsis, and Chapter 10 V(I)/V(II) encoding without confusing these with other nodes. It matches 1,390 of 1,558 branch instances (89.2%). The audit lists all 168 remaining instances with their source record and provisional triage group. No semantic condition or independent source adjudication was inferred from that increase.

**14 November source-image batch:** printed pp. 155, 210–212 support narrowly described postmodifying AP, non-restrictive relative, and PP/AdvP/AP wh-gap shapes. Six catalog signatures now cover 12 additional stored branch instances. Shape coverage is 1,402 of 1,558 (90.0%). The other 156 instances remain individually reported, and movement/attachment conditions are still unchecked.

| Chapter | Matched / examined branch shapes | Recognition |
| --- | ---: | ---: |
| 1 | 0 / 38 | 0.0% |
| 2 | 2 / 53 | 3.8% |
| 3 | 70 / 82 | 85.4% |
| 4 | 49 / 49 | 100.0% |
| 5 | 77 / 83 | 92.8% |
| 6 | 181 / 186 | 97.3% |
| 7 | 495 / 510 | 97.1% |
| 8 | 157 / 184 | 85.3% |
| 9 | 201 / 219 | 91.8% |
| 10 | 150 / 154 | 97.4% |

Chapters 1–2 use pedagogical placeholders and schematic trees intentionally not represented by mature structural rules. Some later omissions involve source-specific coordination, gap-only nodes, and special phrase-marker scaffolding. The reproducible audit script reports exact missing signatures; these must be reviewed rather than filled by arbitrary global label substitutions.

**Proof obligation remaining:** every candidate needs correct lexical selection, attachment, role interpretation and source convention; a branch-shape recognition statistic supplies none of those.

## 7. Remaining native-generation phases (not yet implemented)

### Phase B — Turn catalog into an executable B-R grammar

Convert rule descriptions into typed constructive rules and constraints. Implement lexical valency/selection conditions; recursive NOM, VP and auxiliary structure; coordination; null categories, word-aligned elision, controlled indices; and book-specific exceptions. Use immutable IDs and Third Edition citations. Require positive, negative, exception and ambiguous gold tests before enabling each rule for automated certification.

**Acceptance:** every enabled rule has a reviewed derivation, known profiles, a strict executable condition, and a tested failure path. A shape-only match is not an admissible proof.

### Phase C — Native B-R candidate parser

Build a bounded chart/agenda parser with a packed parse forest. Seed hypotheses with Benepar/spaCy evidence but independently create alternative B-R attachments and hierarchical arrangements. Use explicit feature unification for lexical frames, tense, control, movement, empty positions and coordination.

**Acceptance:** recovers correct held-out B-R analyses *even when Benepar's first hypothesis is wrong*, without inserting unexplained structure.

### Phase D — Separate proof checker, review and evaluation

Check full derivation proof, not merely valid JSON. Independently adjudicate the 252 source records including IMG_ANOMALY/derived/alternative status, and build a separate held-out annotation set with multiple expert-accepted interpretations.

Measure:
1. Exact complete-tree agreement **including legal alternatives**.
2. Incorrect-analysis verification rate (principal safety metric).
3. Verified coverage of unfamiliar sentences.
4. Ambiguity recall, unknown/open-set handling and calibration.
5. Runtime/latency, memory and adversarial input behavior.

**Acceptance:** no *known* false verified tree in the approved reference/adversarial suite; empirical rates documented with version, size and confidence intervals. Zero errors on a finite suite is not a universal no-error guarantee.

### Phase E — Optional learned B-R-specific parser

Only after sufficient independently adjudicated examples exist, compare a fine-tuned B-R tree predictor with the hybrid engine. Use model scores for candidate ranking, not authoritative certification.

### Phase F — All applications on one canonical contract

Generator, Builder, Lesson, Quiz, corrections and evidence must render book-style labels, chapter profile and gap/ellipsis notation from the same trusted canonical envelope. Audit remaining Penn renderer routes and remove or clearly segregate any diagnostic-only path. Preserve browser tests, a reversible rollout and source-versioned assessment answer keys.

## 8. Commands / reproduction / rollout

~~~bash
python -m unittest server.test_br_native_grammar server.test_br_native_chart -v
python scripts/audit_br_native_catalog.py --expected-count 252 --fail-on-penn
python -m unittest server.test_burton_roberts -v
python scripts/audit_burton_roberts_import.py --expected-count 252
python -m compileall -q server
npm run test:builder
node --check web/js/main.js
~~~

The GitHub branch is the rollback boundary. No database changes or migrations are necessary for this increment. Do not merge without model-free tests, runtime model tests where available, and browser review of canonical, unresolved, quiz, lesson and correction paths.

## 9. Known outstanding issues and source decisions

- The Chapter 5 source-attested VP1/VP2 references are now rendered as VP₁/VP₂ by the FINAL-D1 master resolver and lesson SVG fallback when the references survive import. Browser parity across all source diagrams is still unverified.
- The Third Edition's *since* distinction requires contextual disambiguation; the new adapter intentionally refuses an unsupported guess.
- A full lexicon for all six verb classes and Type I/II nonfinite uses remains to be developed.
- Arbitrary noun-internal attachments, recursive wh-clauses, passive argument linking, coordination, idioms, ellipsis and noncanonical word orders are not fully verified.
- The current registry recognizes *shapes*; additional proof rules must validate each source-specific attachment and semantic relationship.
- Legacy quiz/lesson/correction routes still need a complete UI parity audit; hiding the tutor's default diagnostic does not prove every route is B-R-only.
- The 8 November source review explicitly did not certify independent comparison of every one of the 252 corpus records. Preserve that outstanding gate.

## 10. Decision record

**Chosen:** Keep Benepar as neural candidate evidence, formalize Burton-Roberts as the structural authority, add a rule compiler and a native B-R chart parser after the source-driven rule-review gates, and require separate structural, lexical and semantic verification. Avoid promising universal certainty.

**Rejected:** globally substituting Penn tag names; trusting a single Benepar tree as the book's own analysis; letting an unrestricted LLM invent verified syntax; self-certifying all existing figures; hiding unhandled constructions behind fabricated analyses.

**9 November 2026 implementation result:** 100-shape source-linked construction registry, separate conservative coverage auditor, backend audit integration, default-hidden Penn diagnostic, Builder palette correction, focused Third Edition temporal fixes and registry unit tests. **Phases B–F remain open.**
