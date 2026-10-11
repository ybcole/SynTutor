# SynTutor Feature Status

This document records the current feature set and implementation progress for
SynTutor. It is a status snapshot of the code in this repository, not a
roadmap or a guarantee that every feature is production-ready.

## Progress summary

| Area | Progress | Status |
|---|---:|---|
| Core parsing and syntax-tree generation | 95% | Implemented |
| Deterministic grammar validation | 90% | Implemented; rule coverage can still grow |
| Semantic validation (Stage 11) | 70% | Implemented over closed lexicons; coverage can grow |
| Explanations and learner feedback | 85% | Implemented |
| Interactive browser UI | 90% | Implemented |
| Backend/API and error handling | 85% | Implemented |
| Documentation | 85% | Implemented |
| Automated testing and release infrastructure | 25% | Partial |
| Production readiness | 35% | Prototype/development stage |
| **Overall project completion** | **78%** | Core experience works; operational features remain |

### How the percentages are calculated

The percentages are qualitative engineering estimates based on the current
scope: implemented behavior, integration completeness, error handling,
verification, and production readiness. They are not code-coverage numbers and
should not be interpreted as a percentage of lines completed.

## Implemented features

### User input and sentence selection

- Accepts a sentence or multi-sentence paragraph in the textarea.
- Starts in a locked/read-only state.
- Double-clicking enables editing.
- Clicking away locks the input again.
- Changed input is automatically analyzed after leaving the editor.
- `Ctrl+Enter`/`Cmd+Enter` submits the current text while editing.
- When a paragraph is analyzed, the backend returns sentence character offsets.
- Clicking inside a locked sentence selects and analyzes that sentence.
- The selected sentence is highlighted in the textarea without losing scroll
  position.

### NLP pipeline

- Uses spaCy `en_core_web_md` for tokenization, sentence segmentation, POS
  tagging, dependency metadata, and token heads.
- Uses benepar `benepar_en3` for a neural constituency parse.
- Extracts the selected tree from benepar's `span._.parse_string`.
- Converts the parse string into a serializable nested node graph.
- Produces both a nested `tree` and flat `nodes` map.
- Stores token spans, surface text, POS labels, and punctuation flags.
- Validates that parse leaves align with the spaCy token count.
- Caches loaded models and cached model-load failures within the process.

### Deterministic grammar validation

- Evaluates parent-to-child tree edges through a hand-authored Linguistic
  Constraint Matrix.
- Reports `valid`, `error`, and `unlisted` statuses.
- Checks subject-verb agreement.
- Checks determiner-noun number agreement.
- Checks auxiliary and verb-form selection.
- Distinguishes irregular past tense (`came`) from past participle (`come`) and
  rejects regularized irregular forms such as `becomed`.
- Checks clause finiteness.
- Checks modifier ordering, distinguishing a postnominal numerical identifier
  (`the number seven` → `C-NUM-IDENT`) from a genuine misplaced modifier.
- Checks determiner stacking.
- Checks noun, verb, adjective, adverb, and preposition heads.
- Checks pronoun case.
- Checks article omission and `a`/`an` selection.
- Checks quantifier-noun agreement.
- Checks adjective/adverb confusion and selected flat-adverb cases.
- Checks comparative and superlative stacking.
- Checks infinitival complements and infinitival `to`.
- Checks selected small-clause and adverbial complement structures.
- Checks sentence capitalization and root structure.
- Produces a deterministic summary with counts, verdict, and fired
  constraints.
- Produces deterministic repair suggestions for supported violations.
- Does not use a generative model to create grammar feedback.

### Semantic validation (Stage 11)

- Runs a deterministic, additive semantic layer after the syntax matrix; it
  never changes the syntax verdict.
- Governed prepositions and light-verb collocations (`S-PREPOSITION`,
  `S-COLLOCATION`).
- Per-clause tense–time agreement (`S-TENSE-TIME`): a deictic cue (`yesterday`,
  `ago`, `now`, `tomorrow`, `last/next <noun>`) must match the predicate of the
  *same* clause. Habitual/frequency adverbs no longer blanket-suppress a
  sentence, so `Yesterday I go to school every day.` is reported while
  `The children play in the park every day.` is not.
- Selectional restrictions for a small set of verbs (`S-SELECTIONAL`).
- Subject–predicate compatibility (`S-PREDICATE-COMPAT`), reported as an advisory
  `warning` "under a literal interpretation": **physiological** states (`hungry,
  thirsty, tired, sleepy, exhausted, starving, pregnant, sick`) require an
  animate subject and **life/death** states (`dead, alive`) a living one; at most
  one finding per (clause, subclass).
- Two hedged, **preposition-aware** PP-attachment readings with a non-exhaustive
  scope note — `with` = instrument/accompaniment vs. possession; `in`/`at`/`on`
  = location/setting; `for` = purpose/beneficiary (R11.5).
- Classifies nouns via explicit lexicons plus an **optional local WordNet
  fallback**, a conservative pronoun table and spaCy `PERSON` NER; a lemma no
  evidence classifies stays *unclassified* and is never flagged. WordNet is never
  downloaded at request time and the app degrades to the explicit lexicons when
  it is absent.
- Emits **qualitative** confidence labels (`Direct Rule Match` / `Advisory
  Suggestion` / `Insufficient Evidence`) plus a `provenance` string — never a
  fabricated numeric probability.
- Reports `status`/`available` so a controlled semantic failure is shown as
  "unavailable" and never as a clean "no findings" result.
- Renders advisory findings distinctly from definitive semantic errors, and shows
  **independent Syntax and Semantics status indicators**.

### Explanations and feedback

- Generates plain-English names for common Penn Treebank labels.
- Provides a node explanation for phrase and word nodes.
- Displays grammatical role, constraint, status, surface text, and checks.
- Provides invalid-node remediation when a supported error is detected.
- Provides suggested fixes and optional alternative fixes.
- Provides a basic sentence verdict.
- Provides a deterministic contrastive explanation.
- Keeps node explanations in the frontend session payload, so selecting a node
  does not trigger another parse request.
- Uses distinct visual states for valid, invalid, unlisted, selected, and
  hovered nodes.

### Interactive syntax-tree canvas

- Renders phrase-structure trees in an HTML5 canvas.
- Uses a uniform leaf-slot layout.
- Centers internal nodes over their child spans.
- Draws parent-child edges.
- Colors invalid edges red.
- Highlights the selected tree span.
- Supports mouse selection.
- Supports hover tooltips with plain meanings only, such as
  `Adverb Phrase` rather than `ADVP — Adverb Phrase`.
- Supports drag-to-pan.
- Supports wheel zoom anchored to the cursor.
- Fits the tree to the available canvas area.
- Supports keyboard navigation with arrow keys.
- Supports Enter/Space selection for the focused canvas.
- Handles device-pixel-ratio-aware canvas resizing.
- Shows an empty-state message before a tree is available.

### Backend and HTTP API

- Uses Python's standard-library `http.server`.
- Serves the frontend and API from one process and port.
- Supports configurable `SYNTUTOR_HOST` and `SYNTUTOR_PORT`.
- `GET /` and `GET /index.html` serve the application shell.
- `GET /api/health` reports model availability and installation hints.
- `POST /api/parse` accepts text and an optional zero-based sentence index.
- Returns structured JSON for parse, tree, node, summary, and explanation data.
- Returns clear status codes for invalid JSON, empty input, invalid sentence
  indexes, parse failures, missing models, and unknown paths.
- Normalizes static-file paths and rejects traversal/absolute-path attempts.
- Sends `Cache-Control: no-store` for responses.
- Uses a threaded HTTP server.

### UI diagnostics and developer panel

- Displays the current finite-state-machine state.
- Logs pipeline stages and state transitions.
- Provides a collapsible developer panel.
- Shows the sentence verdict.
- Shows the raw benepar parse string.
- Shows spaCy token metadata.
- Shows the system/state-machine log.
- Displays backend/model errors in the canvas and explanation areas.

### Verification and documentation

- `npm run serve` starts the backend.
- `npm run audit` runs the deterministic gold-corpus rule audit.
- The audit checks expected valid and invalid sentences.
- The audit checks that exercised edge types are covered by matrix rules.
- Current audit target: no gold regressions and no unlisted edge types in the
  corpus.
- `npm run audit:semantics` runs a six-gate semantic-layer audit: matrix
  invariance, false-positive and false-negative guards, R11.5 ambiguity, the
  target sentence, and semantic-failure handling.
- `npm run audit:ui` runs a dependency-free DOM-shim audit of the semantic
  panel (advisory vs. error rendering, the unavailable notice, ambiguity pills).
- Documentation exists for quick start, architecture, grammar rules, and the
  design thesis.

## Current limitations and not implemented

### Intentionally not implemented

These are explicit design choices, not accidental omissions:

- **Automatic correction:** SynTutor shows a violation and suggests a repair;
  it does not rewrite the learner's sentence.
- **Generative/LLM feedback:** `explainers.surprisal`,
  `explainers.perturbation`, and `explainers.llm_note` are reserved fields and
  currently remain `null`.
- **Dependency-tree feedback:** the product is focused on phrase-structure
  constituency trees.
- **Probabilistic grammar verdicts:** the feedback verdict comes from the
  deterministic rule matrix, not an opaque model score.

### Not yet implemented or incomplete

- **Automated unit/integration/browser test suite:** the repository contains the
  audit script but no formal test runner or browser E2E suite.
- **Continuous integration:** no GitHub Actions workflow currently runs the
  audit, linting, or smoke checks on every push.
- **Pinned dependency manifest:** `requirements.txt` documents the backend
  dependencies, including `inflect` for noun-form validation; no lockfile is
  included.
- **Production deployment configuration:** no container, reverse proxy,
  process manager, HTTPS configuration, or deployment manifest is included.
- **Authentication and authorization:** sign-in runs through Clerk (email/password
  with email-code verification and second-factor); Supabase Row-Level Security
  scopes history to the signed-in user. No admin roles, invite flows, or
  fine-grained permissions yet.
- **Persistence:** per-user analysis history is stored in Supabase
  (`analysis_history`) and shown in the history drawer; learner progress,
  settings, and saved texts are not yet stored.
- **Telemetry and analytics:** there is no event tracking, usage analytics, or
  error-reporting service.
- **Internationalization:** labels, explanations, and UI copy are English-only.
- **Accessibility audit:** the canvas has a focus target and ARIA label, but a
  complete screen-reader equivalent of the tree and a formal WCAG audit are
  still needed.
- **Mobile-specific interaction design:** the layout has responsive behavior,
  but touch gestures and small-screen ergonomics have not been fully validated.
- **Rate limiting and request quotas:** the development HTTP server accepts
  requests without rate limiting or abuse controls.
- **Security hardening for deployment:** the server is suitable for local
  development, not an internet-facing deployment without additional
  hardening.
- **Broad linguistic coverage:** the rule matrix covers the audited grammar
  patterns, but English has many constructions and lexical exceptions outside
  the current inventory.
- **Semantic lexicon breadth:** the Stage-11 layer starts from explicit lexicons
  and falls back to a local WordNet corpus; a lemma neither covers is left
  unclassified (no finding), so recall depends on those sources and WordNet's
  sense coverage. WordNet is optional — without it the app runs on the explicit
  lexicons alone.
- **Biological-state predicate coverage:** R11.6 recognises a fixed set of
  physiological states (`hungry, thirsty, tired, sleepy, exhausted, starving,
  pregnant, sick`) and life/death states (`dead, alive`); other predicates are not
  covered, and the check is advisory (it never changes the syntax verdict).
- **Semantic confidence labels:** findings carry qualitative labels
  (`Direct Rule Match` / `Advisory Suggestion` / `Insufficient Evidence`) and a
  provenance string, not a calibrated probability.
- **Responsive layout:** the sidebar collapses below/over the canvas at narrow
  widths; very dense trees may still require scrolling rather than shrinking.
- **Model download automation:** missing models are reported with install hints,
  but the application does not download or manage models automatically.
- **Versioned API contract:** the JSON payload is documented, but there is no
  explicit API versioning or schema validation package.

## Suggested next steps

The highest-value follow-up work is:

1. Add a dependency lock/requirements file and a reproducible setup command.
2. Add Python tests for parse-string conversion, node alignment, matrix rules,
   and API validation.
3. Add browser tests for editing, sentence selection, canvas interaction, and
   error states.
4. Add a CI workflow that runs the audit and test suites.
5. Add a machine-readable API schema and version the endpoint contract.
6. Improve accessibility with a DOM/tree-text alternative to the canvas.
7. Define a deployment target and add the required production configuration.
8. Expand the rule corpus based on learner-facing error patterns.

## Verification snapshot

The latest maintained verification commands are:

```bash
npm run audit
npm run audit:semantics
npm run audit:ui
```

`npm run audit` currently verifies:

- 108 gold-corpus sentences
- 56 expected-valid sentences
- 52 expected-invalid sentences
- 0 gold regressions
- 0 unrated edge types in the exercised corpus (963 edges)

`npm run audit:semantics` runs six gates and verifies:

- the semantic layer never changes the syntax verdict on the gold corpus;
- the semantically-neutral corpus produces zero findings;
- each expectation sentence produces *exactly* the documented finding set
  (rule / constraint / severity / count) — a stray extra finding fails too — and
  every finding carries a qualitative `confidence_label` and a `provenance`;
- R11.5 yields two distinct, span-valid, preposition-aware, hedged readings with
  a two-reading, non-exhaustive scope note;
- `The number seven is hungry.` is syntactically valid with no false
  `C-MOD-POS` and yields the advisory R11.6 warning labelled
  `Advisory Suggestion`;
- a controlled semantic failure preserves the syntax verdict and reports
  `semantics.status = "unavailable"`.

`npm run audit:ui` (dependency-free DOM shim) verifies that findings render the
qualitative labels and never a fabricated decimal, that an advisory card is
visually distinct from a definitive error, that `unavailable` shows the dedicated
notice rather than the empty state, that the independent Syntax/Semantics status
chips cover all four semantic states, and that R11.5 pills render, state the
two-reading scope, and dispatch selection.
