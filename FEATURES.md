# SynTutor Feature Status

This document records the current feature set and implementation progress for
SynTutor. It is a status snapshot of the code in this repository, not a
roadmap or a guarantee that every feature is production-ready.

## Progress summary

| Area | Progress | Status |
|---|---:|---|
| Core parsing and syntax-tree generation | 95% | Implemented |
| Deterministic grammar validation | 90% | Implemented; rule coverage can still grow |
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
- Checks clause finiteness.
- Checks modifier ordering.
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
- **Pinned dependency manifest:** dependencies are documented in the quick
  start, but there is no `requirements.txt` or lockfile in the repository.
- **Production deployment configuration:** no container, reverse proxy,
  process manager, HTTPS configuration, or deployment manifest is included.
- **Authentication and authorization:** the local server has no users,
  accounts, roles, or access control.
- **Persistence:** analyses, learner history, progress, and settings are not
  stored in a database or browser storage.
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

The latest maintained verification command is:

```bash
npm run audit
```

The audit currently verifies:

- 99 gold-corpus sentences
- 51 expected-valid sentences
- 48 expected-invalid sentences
- 0 gold regressions
- 0 unlisted edge types in the exercised corpus
