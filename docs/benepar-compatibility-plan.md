# Benepar compatibility and normalization plan — Milestone 01

**Decision:** Retain spaCy/Benepar as a candidate parse provider during the transition. Do not remove or replace the parser in this milestone. Do not present its raw Penn-style analysis as the authoritative Burton-Roberts tree.

## 1. Current observed role

The active backend path is:

`POST /api/parse` → `server/webapp.py` → `server/api.py::build_payload` → `server/parse_engine.py::analyze` → spaCy + Benepar candidate tree → legacy matrix, licensing and detector evaluation → response consumed by the browser.

Benepar's current tree labels/structure are closely tied to the existing parser-oriented UI and rule matrix. They are useful as candidate structural data and for maintaining the old Parser view while the new linguistic contract is introduced.

## 2. Required authority boundary

- **spaCy/Benepar:** candidate tokenisation, POS tags and constituency parse, plus diagnostics.
- **B-R normalizer:** the only service allowed to construct the canonical B-R tree from candidate data, and only where a mapping is justified by conventions and gold evidence.
- **B-R structural validator:** decides whether a proposed canonical tree satisfies the selected chapter convention, tree schema, word order, token spans, features, gaps, indices, triangles and alternative-analysis rules.
- **Cambridge evaluator:** evaluates only reviewed, in-scope grammatical knowledge against an accepted analysis and the sentence.
- **Explanation composer:** renders only validated structural/rule evidence and source references.
- **CoLA acceptability classifier:** optional secondary signal. It may flag for review/unverified status; it cannot create a grammatical explanation or overrule a verified deterministic constraint.

## 3. Why a label-renaming adapter is insufficient

The existing `CONVENTIONS.md` §11 already documents these incompatibilities:

| B-R convention | Current PTB/Benepar output | Compatibility decision |
|---|---|---|
| `AP`, `AdvP` | `ADJP`, `ADVP` | A label alias may be possible in a narrowly verified context, but must be tested against the chapter's tree shape and evidence. Never apply a global string replacement without validation. |
| `S-bar`, `S-dbar`, `C1`, `C2` | `SBAR`, `SBARQ`, `WH*` | No clean one-to-one mapping. Requires explicit structural analysis; otherwise unresolved. |
| Chapter 7 `NP → DET NOM` with recursive `NOM` | Often flat `NP` with modifier sisters | Not reproducible automatically from the flat parse. Use book-authored/gold structures or mark unresolved. |
| Chapter 5 higher VP for adjuncts | Adjuncts may be flat within VP | Requires attachment decisions not supplied by the label. Do not infer a higher VP without evidence. |
| Auxiliary heads with VP complements | Benepar may nest some auxiliaries but flatten others | Partial correspondence only. Validate auxiliary class, order and complement structure separately. |
| `MOD PERF PROG PASS TENSE` and B-R verb features | Penn POS tags such as `MD`, `VBZ`, `VBP`, `VBD` | POS tags can be evidence about form, not a direct substitute for structural labels/features. |
| Gaps `•`, indices/control, `[-tense]`, `PartP`, `PRE-DET`, `NOM` | Not emitted as B-R structures by Benepar | Cannot be recovered by relabelling. Requires source-backed reconstruction from context or an unresolved/alternative result. |

The repository convention file concludes that lesson gold trees should be authored from the book and the parser can only provide a rough candidate tree to be corrected by hand. This is the governing compatibility constraint.

## 4. Normalization outcomes

Every candidate analysis should end in one of these explicit states:

### A. Normalized and validated

Use when every structural transformation is supported by a documented convention rule and one or more B-R reference fixtures, token alignment passes, and the canonical validator passes.

Record:
- raw candidate tree and parser/version metadata;
- normalized B-R tree and schema version;
- convention profile;
- transformation identifiers and their evidence;
- structural validation results;
- confidence and source references.

### B. Accepted alternatives

Use when the B-R source permits more than one analysis for the sentence or exercise. Preserve each accepted tree with its own identifier, source basis, meaning/condition where relevant, and grading status. Do not select one arbitrary Benepar parse as the sole correct answer.

### C. Unresolved

Use when a required structural choice cannot be inferred defensibly from the candidate parse, sentence, convention profile or available source evidence. Return the candidate tree for diagnostics, explain which transformation is unresolved, and avoid presenting a guessed B-R tree as authoritative.

### D. Rejected / invalid candidate

Use when the candidate data violates basic invariants such as malformed tree structure, invalid token spans, changed word order without a correction record, missing required terminal coverage, or an illegal label/feature for the selected convention. Record validation errors and do not promote the candidate.

A failed or unavailable parser must remain distinguishable from a linguistically unresolved analysis. Unknown constructions must fail safely, not be silently coerced.

## 5. Normalization pipeline proposal

1. Preserve the original input and sentence segmentation.
2. Tokenize once for the request and establish a stable token index and character-offset map.
3. Run the configured candidate parser and retain its raw output.
4. Choose the requested convention profile:
   - chapter-specific V1–V10 for chapter lessons/assessments;
   - the declared final free-analysis profile (V10 plus the Chapter 7 appendix refinement, with the existing D1 option recorded where the course requires core Chapter 7 treatment).
5. Produce candidate B-R mappings using a versioned transformation registry. Every transformation declares preconditions, output shape, evidence, unsupported cases and confidence.
6. Normalize only the structures supported by source conventions and reviewed gold fixtures.
7. Run canonical schema and structural validation.
8. Attach accepted alternatives or explicit unresolved/rejected states.
9. Evaluate only Cambridge rules independently eligible for runtime use.
10. Build one analysis payload and explanations from validated facts.
11. Compare candidate/new results with the legacy pipeline before any production feature-flag promotion.

## 6. Gold data and test strategy

Use `web/content/book/ch01.trees.json` through `ch10.trees.json` as the existing 252 B-R tree records, respecting their individual status/evidence flags. Preserve Chapter 11 as a text-only content record, not a tree fixture. Do not treat `IMG_ANOMALY`, `TXT`, `NEEDS_REVIEW`, or unresolved fragments as pristine gold examples without their documented review.

For each transformation:
- add hand-reviewed fixtures covering positive, negative, ambiguity and unsupported cases;
- validate tree shape, label/feature legality, token coverage/order, gaps/indices, triangle semantics and convention restrictions;
- verify accepted alternatives and book simplifications;
- test long/deep recursive structures and complete sentence alignment;
- run legacy regression inputs to measure unintended changes.

A tree count or a successful parser call is not a quality score. Record results per chapter, construction and transformation.

## 7. Compatibility and rollout

- Keep the existing parser/matrix response and UI path functioning while the new schema/adapter is introduced.
- Do not destructively rewrite the current 252 tree JSONs or the legacy parser payload as part of Milestone 01.
- Introduce a versioned canonical analysis object in parallel with the legacy response during Milestone 02.
- Keep raw parser diagnostics available to reviewers, but label them distinctly from the B-R view in the product.
- Use a feature flag or explicit mode selection until the benchmark/regression acceptance threshold has been met.
- Promote the normalized B-R path only after its gold fixtures, structural validators, error states and API regression tests pass.
- Retain a rollback path to the existing parser view and response contract until cross-feature integration is verified.

## 8. Dependencies and decisions

- Confirm the B-R edition and inspect the actual source pages for each transformation.
- Complete/record independent review and B-R crosswalk decisions before activating Cambridge constraints.
- Approve the canonical schema proposal and transformation registry.
- Establish tokenisation ownership so parser token spans and correction edits cannot drift.
- Determine whether the legacy Parser view remains a user-visible diagnostic mode after the new B-R generator is stable.
- Define numeric thresholds for normalization confidence and benchmark acceptance in Milestone 02; this milestone does not invent thresholds.
