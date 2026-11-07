# ADR-001 — Architecture, parser authority, and linguistic source governance

- **Status:** Adopted for the SynTutor roadmap baseline (Milestone 01).
- **Date:** 7 November 2026.
- **Decision owners:** Project owner (standing automatic approval for roadmap gates); implementation evidence recorded by the AI agent.
- **Scope:** Architecture and data-governance decisions only. No runtime code or database schema changed in this milestone.

## Context

SynTutor currently combines four responsibilities in its parser pipeline: candidate constituency analysis, target tree conventions, grammatical rule evaluation, and learner-facing explanation. The active application uses spaCy/Benepar and a legacy Penn-style rule matrix, while the repository also contains B-R chapter gold trees/conventions and Cambridge grammatical extraction records.

The B-R data provides chapter-specific phrase-marker conventions. Cambridge provides a broader grammatical knowledge source with different categories of rule/evidence. Some Cambridge-to-B-R mappings remain explicitly unverified. A runtime that silently equates frameworks or treats every extracted record as an error rule would be unsafe.

## Decisions

### D1. Linguistic authority

- Burton-Roberts governs the target syntactic representation and the ordered structural curriculum, subject to confirming the exact edition represented by the source PDFs.
- Cambridge supplies broader grammatical categories, construction descriptions, constraints, conditions, exceptions, variety/register restrictions and explanations where applicable.
- The two frameworks remain separately represented when terminology or analysis differs.
- No framework mapping is considered verified from label similarity alone.

### D2. Parser technology

- Retain spaCy/Benepar as a candidate parser during the transition.
- Preserve its raw output for diagnostics.
- Never expose raw Penn-style output as canonical B-R output.
- Build a B-R normalizer and structural validator; normalize only transformations supported by B-R conventions and gold fixtures.
- Return unresolved, rejected or accepted-alternative states where mapping is not justified. Do not invent a preferred analysis.

### D3. Canonical tree and convention profiles

- Establish a versioned B-R canonical tree schema as proposed in `docs/canonical-burton-roberts-tree.schema.json` and described in `docs/canonical-burton-roberts-tree-schema.md`.
- Preserve B-R canonical labels, features, indices, terminal order, triangles, gaps, elision, movement/control metadata, source evidence and accepted alternatives.
- Chapter lessons/building/grading use that chapter's convention V1–V10.
- Free analysis uses the declared final convention profile in `CONVENTIONS.md` (V10 plus the Chapter 7 appendix refinement), preserving the recorded Chapter 7 core/appendix option.
- Derive functions from structure; do not invent function-labelled phrase-marker nodes.
- Existing source tree JSON remains unchanged; import through a read-only adapter before any persistent migration.

### D4. Explanation authority and service boundary

- A shared analysis/evidence contract supplies both Syntax Generator and Syntax Builder.
- Structural explanations must cite B-R convention/source evidence.
- Broader grammatical principles and constraints must cite Cambridge evidence where relevant.
- Error diagnoses require validated structure plus an independently reviewed, runtime-eligible rule with encoded scope, conditions, exceptions and variety limits.
- Explanations are composed from deterministic facts and reviewed templates. Optional language-model drafting may paraphrase approved facts but may not determine grammaticality or invent evidence.
- Missing/conflicting/unresolved source evidence produces an explicit unresolved or no-source-basis result, not a fabricated explanation.

### D5. Rule registry and lifecycle

A source extraction record is not automatically an executable rule. Track these states independently:

1. extraction state and protocol version;
2. independent-review state;
3. human approval state;
4. B-R crosswalk state;
5. runtime implementation/eligibility state;
6. validation/test state;
7. active content/rule version.

Only a record that meets its applicable source-review, crosswalk, rule-type, scope, exception/variety, deterministic implementation and test requirements may trigger a grammar-error finding. Classification and descriptive generalisation records remain instructional evidence; stylistic/prescriptive records never become grammatical prohibitions by default.

### D6. Lessons and quizzes

- Lessons remain instructional, guided, chapter-sequenced learning experiences.
- Standalone quizzes are separate assessments with independent question/attempt/version data.
- B-R supplies the structural curriculum spine; Cambridge insights are selected and cited rather than forced into every core lesson.
- Book answer/tree repositories are reference data, not a ready-to-publish copy of book exercise wording.
- Content and progress are versioned so updates do not rewrite the meaning of earlier learner activity.

### D7. API boundaries

The current `POST /api/parse` contract remains in place during Milestone 01 and must not be broken by documentation work.

Target logical services:

1. **Parsing adapter:** receives sentence text, tokenises and produces raw candidate parse plus metadata.
2. **B-R normalization/validation:** receives raw candidate parse, sentence/tokens and convention profile; returns canonical tree, validation findings and uncertainty/alternatives.
3. **Cambridge rule registry/evaluator:** receives the canonical analysis and sentence; evaluates only runtime-eligible records.
4. **Evidence/explanation composer:** receives validated structural/rule evidence and source refs; returns explanations/remediation tied to node spans and source IDs.
5. **Shared analysis service:** composes the above into one versioned payload for Generator and Builder.
6. **Client modules:** Generator displays sentence analysis; Builder submits the learner's constructed tree to the same validator/evaluator rather than reparsing only the sentence.

A future implementation may retain `POST /api/parse` as a compatibility facade returning the legacy fields plus a versioned `analysis` object. The precise endpoint/payload will be frozen in the relevant implementation milestone after inspection and tests; this ADR does not add endpoints now.

### D8. Migration strategy

- Keep the old parser/rule matrix and UI behaviour available while the canonical path is introduced in parallel.
- Do not destructively rewrite B-R trees, Cambridge extractions, lesson data, or learner progress before importers/validators/tests exist.
- Use stable content/schema versions and explicit compatibility rules for old activity rows.
- Design database migrations to be additive where possible, tested against representative old data, and accompanied by backup/rollback instructions.
- Move authoritative XP calculation to a trusted backend/RPC in its own milestone; the current browser upsert path is not an acceptable final authority.
- Review public leaderboard and quiz-progress reads for data minimisation and opt-in privacy before public launch.
- Gate new behaviour by feature flag until old/new corpus comparisons and end-to-end regression checks pass.

## Consequences

Positive:
- The parser technology is replaceable without redefining linguistic authority.
- B-R trees remain faithful to chapter progression.
- Cambridge records can provide broader grammatical context without silently controlling tree shape.
- The same structural/rule evidence can serve Generator, Builder, lessons, and quizzes.
- Unknown cases can fail safely.

Costs/risks:
- A source crosswalk and review process are needed before many Cambridge rules can execute.
- The Benepar adapter cannot solve every structure automatically; some lesson gold trees require book-authored data.
- Versioned payloads, content migration, and review metadata add implementation work.
- A subset of the current UI and progress model will need compatibility handling.

## Open uncertainties and risks

- Exact B-R edition/source PDF and printed-page alignment are not confirmed.
- Exact Cambridge edition/year/ISBN metadata is not confirmed in repository extraction files.
- All 196 active Cambridge rule records have B-R mapping `unverified`.
- Independent second-pass review remains outstanding according to extraction reports.
- Three Cambridge Chapter 2 conflict entries identify candidate B-R disagreements; none can be resolved from current source inputs.
- Benepar structural errors can propagate misleading explanations if the old matrix is applied without validation.
- Legacy rule-matrix coverage is not complete; its unlisted checks and known evaluation false positives remain a regression risk.
- Supabase third-party Clerk auth configuration is external and was not tested.
- Existing public policies expose leaderboard and quiz-progress records; raw Clerk subject is selected in the current leaderboard query.
- Current XP writes are client-calculated/upserted and have no authoritative idempotency ledger.
- Existing user history keyed to the previous UUID identity is not migrated by the current Clerk migration.
- No live database, secrets, production environment or user rows were accessed during this audit.

## Approval / implementation sequence

The project owner has granted standing automatic approval for roadmap gates. This ADR and the associated Milestone 01 deliverables are therefore treated as accepted for proceeding to Milestone 02 once all Milestone 01 acceptance criteria and documentation checks are verified.

No parser, rule, frontend, lesson, quiz, builder, database migration or user-data code is changed in this ADR.
