# SynTutor — Complete Architecture Reference

Every module, function, data field, constant, and state rule in the running
implementation. This is the **implementation** document (what the code actually
does); `THESIS.md` is the **design specification**; `RULES.md` is the
**linguistic rule inventory**. A spec-vs-implementation compliance map is in
§14 at the end.

---

## 1. System overview

SynTutor is a deterministic, explainable, intelligent tutoring system for
English phrase-structure syntax. It:

1. Tokenizes + POS-tags with spaCy (`en_core_web_md`),
2. Produces a single best **constituency parse tree** via benepar (`benepar_en3`),
3. Validates **every parent→child edge** against a hand-authored **Linguistic
   Constraint Matrix** (no ML in the feedback path),
4. Renders an interactive canvas tree and explains each node from a
   precomputed payload (no re-parse on click).

Hard guarantees:

- **Determinism** — identical input ⇒ identical verdict, always.
- **No auto-correction** — the system shows a violation + a deterministic
  correction *suggestion*; the learner edits the text themselves (dual-loop).
- **Phrase-structure only** — no dependency-parse trees are used for feedback.

| | |
|---|---|
| Frontend | Vanilla ES modules, HTML5 `<canvas>`, no frameworks, no transpilation; build = `scripts/build.js` copy `web/` → `dist/` (Vercel) |
| Backend | Local: Python 3.10+ stdlib `http.server` (`server/app.py`); production: the same `build_payload`/`analyze` logic mounted on Gradio/FastAPI (`server/hf_space.py`) on the HF Space |
| NLP | spaCy `en_core_web_md` + benepar `benepar_en3` + `transformers==4.46.3` pin |
| Parsing output | single MAP constituent tree drawn from `span._.parse_string` |
| Verification | `python3 scripts/audit_rules.py` (gold corpus, fails loud) |
| Deployment | Vercel static frontend (`syntutor.vercel.app`) + HF Space API (`ybcole-syntutor.hf.space`); push to `main` redeploys both |

---

## 2. Repository layout & module inventory

```
SynTutor/
  server/hf_space.py      HF Space entrypoint: minimal Gradio app (ZeroGPU) + mounted /api routes
  web/index.html          UI shell (all 16 wired element IDs, §3)
  web/login.html          Clerk sign-in / sign-up shell
  package.json            {build, serve, audit} npm scripts
  README.md               quick start + spec-level overview
  docs/                   ARCHITECTURE.md (this file) + docs/matrix.md (rule inventory)
  web/css/style.css       design system (§4)
  web/js/main.js          FSM + pipeline orchestration, highlighting, auth, and history
  web/js/renderer.js      canvas layout/draw/hitbox/zoom/keyboard
  web/js/ui.js            DOM views, explainer, semantic panel + segmented tabs, dev panel, logs
  server/app.py           HTTP server + payload assembly (local full-stack)
  server/parse_engine.py  NLP load, parse-string -> node graph (+ spaCy NER token metadata)
  server/matrix.py        rule matrix + XAI + remediation
  server/detector.py      CoLA acceptability classifier wrapper
  server/corrector.py     MLM-based correction search
  server/basic_errors.py  basic error detectors (spelling, morphology, punctuation)
  server/licensing.py     licensing layer for rule corrections
  server/ruleset.py       full rule-matrix rulebook (111 rules)
  server/semantics.py     Stage-11 semantic layer (R11.2-R11.6)
  server/lexicon.py       noun classification: explicit lexicons + optional WordNet, pronouns, NER
  scripts/build.js        Vercel frontend build (copies web/ -> dist/)
  scripts/audit_rules.py  gold-corpus coverage audit (exit-code gate)
  scripts/audit_semantics.py  six-gate semantic-layer audit
  scripts/audit_ui.mjs    dependency-free DOM-shim semantic-panel audit
```

### The seven pipeline stages (as implemented)

| # | Stage | Producer | Consumer | UI feedback |
|---|-------|----------|----------|-------------|
| 1 | User Input | textarea `#inputText` | `main.js executePipeline` | session label "Processing…" |
| 2 | Request `/api/parse` | `fetch` POST JSON (API base = `web/js/config.js` `API_BASE`) | `build_payload` (local `server/app.py`; HF `server/hf_space.py` mounts the identical handler) | FSM badge PROCESSING |
| 3 | Tokenize + POS | spaCy `nlp(text)` | `parse_engine.token_metadata` | token stream |
| 4 | Parse tree | benepar `span._.parse_string` | `parse_parse_string` → `NodeBuilder` | parse string |
| 5 | Validate Ψ matrix | `matrix.evaluate(root)` | `MatrixEvaluator` | node colors |
| 6 | Generate explanations | `build_payload` (`basic`, `contrastive`) | `renderSentenceVerdict` | verdict card |
| 7 | Canvas + feedback loop | `TreeRenderer.setTree` | cache in `session` memory | Explorer |

The seven steps are **not shown as UI chips anymore** — progress is visible
only via the FSM badge, the session label, and the dev-panel log (each stage
logs a `Stage N:` line).

---

## 3. Frontend — `web/index.html`

Layout is a three-column shell; `<body>` is `flex column; overflow:hidden`
(no page scroll — the canvas and panels scroll internally).

Element registry (all are read or written by the JS, exact ids):

| Element | Kind | Role |
|---|---|---|
| `#stateBadge` | span | FSM state pill (data-state colors: IDLE/PROCESSING/VIEWING/EXPLORING) |
| `#sessionLabel` | span | "Idle" / "Processing…" |
| `.input-editor` | div | positions the textarea and read-only highlight overlay |
| `#inputText` | textarea | paragraph-capable input; starts `readOnly`. Double-click enters edit mode with native text and caret; blur re-locks and auto-re-analyzes changed text; locked clicks activate the sentence at the caret |
| `#inputHighlights` | div | safe text-node overlay showing red invalid words and the selected-sentence background while locked |
| `#inputHint` | p | `.input-hint` — live instruction line (editing ↔ locked) |
| `#treeCanvas` | canvas | `tabindex=0`, keyboard navigable, aria-label |
| `#canvasOverlay` | div | `.canvas-overlay`, `pointer-events:none` (see §4) |
| `#explainNode` | div | primary plain-English explainer container (no header/clear button — filled by `renderNodeDetail`/`renderDiagnostic`) |
| `#statusStrip` | div | `.status-strip` row of the two independent status chips (hidden until an analysis completes) |
| `#syntaxStatus` | span | `.status-chip` — Syntax state from the matrix (`Valid` / `Issues Found`) |
| `#semanticsStatus` | span | `.status-chip` — Semantics state from the semantic layer (`No Findings` / `Suggestions Available` / `Issues Found` / `Analysis Unavailable`) |
| `#semanticsSection` | section | Stage-11 semantic findings / ambiguity panel |
| `#ambiguityScope` | p | `.ambiguity-scope` two-reading, non-exhaustive scope note for R11.5 |
| `#devPanel` | `<details>` | collapsible developer panel |
| `#sentenceVerdict` | div | auto-generated pedagogical summary |
| `#parseString` | `<pre>` | raw benepar parse string |
| `#tokenStream` | `<pre>` | spaCy token table (i, t, pos, tag) |
| `#logPanel` | div | prepend-most-recent system/FSM log |

Module graph (`<script type=module src=js/main.js>`):

```
main.js ──> auth.js       (Supabase client and session)
   ├─────> renderer.js    (TreeRenderer, createLayout, COLORS)
   └─────> ui.js          (FSM badge, logs, views, fillDevPanel)
```

---

## 4. Frontend — stylesheet `web/css/style.css`

Design tokens (`:root`):

```css
--bg #f4f3fb  --panel #ffffff  --ink #2b2440  --muted #77708f
--accent #6d5ae6  --accent-soft #efeafc  --ok #2e8b57  --err #d64545
--warn #c98f00  --border #e3e0f2  --radius 12px
```

Key layout facts:

- `.app-main`: `grid-template-columns: minmax(0,1fr) minmax(300px,380px)`; gap
  14px; padding `10px 14px 6px`. The flexible tracks let the canvas shrink and
  the sidebar grow within bounds so neither ever overflows its column.
- `.app-header`: fixed 60px; `.state-badge` data-state palettes; PROCESSING pulses.
- `.canvas-wrap`: `position:relative; flex:1; overflow:hidden`.
- **`.canvas-overlay`**: `position:absolute; inset:0; pointer-events:none` —
  this is the fix that made node clicks reach the canvas again (an earlier
  `pointer-events:auto` version swallowed every mouse event). When `:empty`
  the background is fully transparent.
- `.dev-panel[open]`: `max-height:46vh; overflow:auto`. `.dev-grid`:
  `repeat(4, 1fr)` — verdict / parse string / token stream / log.
- `.primary-explainer` + `.node-explainer`: column flex, inner scroll;
  `flex: 0 1 auto` so they shrink within the sidebar instead of forcing it wider.
- `.status-strip` / `.status-chip`: the two independent Syntax / Semantics
  indicators; advisory and error chips adopt the `--warn` / `--err` accents.
  `.ambiguity-scope`: muted note under the R11.5 reading pills.
- Explainer sections: `.ex-sec .ex-label .ex-identity .ex-badge(.root)
  .ex-role .ex-plain(mark) .ex-rule .ex-text .ex-checks(.ck.ok/.no)`.
- Remediation (Case B): `.remediation` (red top border), `.rem-title`,
  `.rem-body`, `.rem-row`, `.rem-key`, `.rem-value`, `.rem-outcome`.
- Canvas focus: `#treeCanvas:focus { outline: 2px solid var(--accent) }`.
- Responsive `@media (max-width: 1100px)`: `.app-main` stacks to one column
  (canvas above the sidebar, no overlap/clipping), the right panel becomes a
  2-col grid, `.log-card` spans both; the status strip wraps.

---

## 5. Frontend — `web/js/ui.js` (views, logs, dev panel)

Exports: `plainName, confidenceLabel, log, clearOverlay, showCanvasMessage,
renderNodeDetail, renderDiagnostic, renderSentenceVerdict, renderSemantics,
fillDevPanel, applySentenceSelection, renderStatusStrip`.

- `PLAIN_NAME` — canonical Penn-label → plain-English dictionary (~45 entries)
  used by `plainName(type)`; unknown labels fall back to the raw type.
- `confidenceLabel(finding)` — maps a finding to a **qualitative** confidence
  label (`Direct Rule Match` / `Advisory Suggestion` / `Insufficient Evidence`),
  preferring the backend `confidence_label` and falling back to a constraint →
  label table. No numeric probability is ever produced.
- `renderSemantics(semantics, {onSelectReading, activeIndex})` — fills
  `#semanticsSection`: an `unavailable` payload shows `#semanticsUnavailable`
  (never the empty state); otherwise findings render as `.sem-card` (advisory vs.
  error) with the qualitative badge + `provenance` title, and an R11.5 ambiguity
  renders reading pills plus the `#ambiguityScope` two-reading note.
- `renderStatusStrip({syntaxValid, semantics})` — paints the independent
  `#syntaxStatus` / `#semanticsStatus` chips from the internal `semanticsStatus()`
  helper; called with no argument it hides `#statusStrip`.
- `log(entry)` — prepends a timestamped `<div class=log-entry>` to `#logPanel`
  (HH:MM:SS, 24h, en-GB).
- `showCanvasMessage(kind, title, lines)` — overlay card (`.overlay-card error`).
- `renderNodeDetail(_session, detail, node)` — builds 5 sections + Case B:
  1. **Node Identity** — badge `detail.type` (+`.root`), plain name (adds
     `(fragment)` if NP & role == fragment root), `Grammatical role:` line.
  2. **Text Span** — `<mark>` surface + `Token n` / `Tokens n–m` (1-based).
  3. **Structural Rule** — `<pre class=ex-rule>` with `detail.rule`.
  4. **Plain-English Explanation** — `detail.text`.
  5. **Constraint Matrix Checks** — `<ul class=ex-checks>` of `detail.checks`
     with ✓/✗ icons.
  Then, if `status === 'error'` **and** `remediation` exists, the **Case B
  block**: title `Case B: Invalid Node [STATUS: INVALID / VIOLATION · C-*]`,
  then *Violation Breakdown* (`rm.violation`), then *Actionable Correction
  Guide* with `Suggested Fix`, `Alternative Structural Fix` (if present), and
  `Targeted Outcome` (as `<pre class=rem-outcome>`).
- `renderDiagnostic(title, lines)` — fills `#explainNode` with an error card
  (used by `failPipeline`).
- `renderSentenceVerdict(markupLines, isError)` — fills `#sentenceVerdict`
  with `data-verdict=valid|error` and `.is-error` toggling.
- `fillDevPanel(payload)` — parse string → `#parseString`; token stream →
  `#tokenStream` (tab-separated `i  t  pos  tag`).

---

## 6. Frontend — `web/js/main.js` (FSM + orchestration)

State machine (exact states/events):

```
IDLE ──user submits text──────────► PROCESSING ──output ready──► VIEWING
   ▲                                 │   │                        │  ▲
   │empty input / system ready       │   └─request failed──► (VIEWING, diagnostic)
   └─────────────────────────────────┘   (empty input ──► IDLE)  │  │
                                                    user selects node   │
                                                    ▼                    │
                                                  EXPLORING ─back to tree┘
USER interaction loop: VIEWING ⇄ EXPLORING   (node explanations from memory)
RE-ENTRY loop:          any state → PROCESSING on resubmit
```

- Module state: `let state, session, renderer`.
- `transition(next, event)` — sets state, badge, appends `FSM: from → next
  (event)` to the log.
- `boot()` — constructs `TreeRenderer(#treeCanvas, { onSelect:
  handleNodeSelect, onHover: noop, describe: plainName })`, wires events, → IDLE.
- `wireEvents()` — no submit buttons. Textarea **double-click** → edit mode
  (`readOnly=false`, `.editing` accent ring); **blur** → re-lock and, only if
  the text changed since the last analysis, auto-`runPipeline()`; textarea
  click while locked → `activateSentenceAtCaret()` (reads `selectionStart`,
  finds the containing sentence span, re-runs `runPipeline({index})` for that
  sentence — so **clicking any sentence in the paragraph swaps its syntax
  tree in**); keydown (Ctrl/Cmd+Enter → full re-analyze; plain Enter while
  locked → re-analyze the sentence at the caret).
  Deselection happens by clicking empty canvas space (no Clear-selection
  button).
- `returnToLocked()` — after analysis or blur, restores `readOnly = true`,
  hides the native textarea text behind the overlay, and renders the selected
  sentence/error highlights while preserving scroll offsets.
- `buildHighlightSpans()` / `renderInputHighlights()` — map parser token ranges
  and error node spans to safe DOM text nodes. These spans are local UI state
  and are never written to Supabase history.
  `lastAnalyzedText` guards the blur path so unchanged text never re-parses.
- `failPipeline(title, lines)` — canvas overlay error, verdict error lines,
  diagnostic, → VIEWING, logs.
- `runPipeline()` — guards against re-entry while PROCESSING; sets busy;
  `executePipeline` in try/finally (always un-busy).
- `executePipeline()` — the 7-stage walk (progress visible only in the dev-panel
  log, `Stage N:` lines — no UI chips):
  - clears overlay/selection/explainer; takes `#inputText` trimmed;
  - **empty input** → overlay + verdict + diagnostic, → IDLE;
  - `POST /api/parse` JSON `{text, sentence_index?}`; on network failure →
    failPipeline("Backend unreachable", [server start hint]); on `!res.ok`
    pick title by code (503 models / 422 no parse / `Backend error (HTTP n)`)
    and body lines `[error, hint]`;
  - stores `payload.parse.tokens`; logs stage 3 POS stream; if
    `meta.sentence_count > 1` logs the selected-sentence policy; stage 4 logs
    `parse.parse_string`;
  - stage 5: `applyStatuses(tree, node_details)` (annotates each node with its
    own `edgeResult` for edge coloring) and logs the summary counters + fired
    constraint set;
  - stage 6: `renderSentenceVerdict(payload.explainers.basic.split('\n'),
    !payload.summary.valid)` and `renderSemantics(payload.semantics, {…})`;
    `renderStatusStrip({syntaxValid: payload.summary.valid, semantics:
    payload.semantics})` paints the two independent status chips (cleared on
    reset / empty input / failure);
  - **`session = { payload }`** ← the in-memory cache that powers the
    Interaction Loop; input is locked and the highlight overlay renders the
    analyzed sentence/error spans, then stage 7:
    `renderer.setTree(payload.tree)` → VIEWING.
  - Renders the tree and highlights before starting the background history save.
    New submissions are inserted into `analysis_history`; sentence navigation
    and history replay do not create duplicate rows. The recorded-text guard is
    updated only after a successful insert.
- `loadAndRenderHistory()` / `renderHistoryItems()` — load the authenticated
  user's recent history, filter valid/invalid entries, and create safe DOM
  nodes for sentence text and constraint chips.
- `replayHistory()` / `clearHistory()` — replay an entry without inserting a
  duplicate and delete only the authenticated user's selected history rows.
- `applyStatuses(tree, details)` — DFS; `node.edgeResult = {status}` (default
  'valid' if missing) — the renderer reads this per child edge.
- `handleNodeSelect(id)` — no-op if no session; `renderNodeDetail(session,
  detail, node)` from `session.payload.node_details`/`nodes`; `renderer.select
  (id)`; → EXPLORING (unless PROCESSING) with log `Exploring: cached XAI for
  node …`.

Error-handling matrix (frontend):

| Failure | UI path |
|---|---|
| Empty input | overlay, verdict, → IDLE |
| Network unreachable | failPipeline(Backend unreachable) |
| 503 | failPipeline(NLP models unavailable) |
| 422 | failPipeline(Unable to produce a parse) |
| other status | failPipeline(Backend error (HTTP n)) |

---

## 7. Frontend — `web/js/renderer.js` (canvas layout, drawing, interaction)

### Layout algorithm (`createLayout`)

Constants: `BOX_H=34, MIN_BOX_W=54, H_PAD=14, GAP=26, V_GAP=40, TOP_PAD=24,
SIDE_PAD=24`.

The layout is a **uniform-slot grid**: every leaf occupies the same-width slot,
so columns are perfectly aligned and every internal node is dead-centered over
its leaf span — no stair-stepping, no off-center parents.

1. `collectNodes` — DFS pre-order list.
2. Assign `nodeDepth` (root=0) and `maxDepth`.
3. `SLOT = max over leaves(measuredLabel + 2·H_PAD) + GAP` — one shared slot
   width. Leaf `i` sits at `x = SLOT·i + SLOT/2` (evenly spaced columns).
4. `span` map: each node = `[firstLeafIndex, lastLeafIndex]` (recursive min/max).
5. Internal node x = midpoint of its span `=(lo+hi+1)·SLOT/2` (hence exactly
   centered over its children), `w = (hi−lo+1)·SLOT`; y =
   `TOP_PAD + depth·(34+40) + 17` for every node at that depth → rows align.
6. `totalW = max(leafCount·SLOT + 48, 320)`;
   `totalH = max(TOP_PAD + maxDepth·74 + BOX_H + SIDE_PAD·2, 160)` (bottom room
   reserved for leaf POS tags).

`nodeLabel`: phrase → `node.type`; leaf → `node.surface`.

`COLORS`: nodeStroke `#6d5ae6`, text `#2b2440`, edge `#000000`, edgeValid
`#000000` (default line color), edgeError `#d64545`, edgeText `#77708f`,
selectedStroke `#c98f00`.

### `TreeRenderer` (canvas, opts {onSelect, onHover, describe})

- `describe(label)` (from `ui.plainName`) turns a Penn tag into its
  plain-English meaning for the hover tooltip.
- `view = {scale, tx, ty}`; events: mousedown/move/up/leave, wheel (passive:
  false), keydown, window resize.
- **Viewport math**: `_toScreen`/`_toWorld` linear transforms; `_fitView`
  scale = `min((w−80)/totalW, (h−80)/totalH, 1.4)` floored at 0.2, centered;
  wheel zoom clamps 0.15…3 anchored at the cursor; drag pans (3px threshold
  before it counts as a drag); DPR-aware resize (`devicePixelRatio`).
- **Hit-testing**: candidates = layout boxes inflated +8px each side; ties
  broken toward the **largest y** (front-most); returns node id or null.
- **Interaction loop**: mousedown records start + base pan; mouseup without
  movement = click → `onSelect(hitId)`; mousemove (not dragging) → hover
  (`pointer` cursor) + repaint (cursor tracked for tooltip anchoring);
  mouseleave clears hover.
- **Keyboard nav** (`_onKey`, canvas focused): ArrowLeft/Up = prev, ArrowRight/
  Down = next, in **DFS order** (`dfsOrder` + `indexById`), clamped; Enter/Space
  = select the currently selected node.
- `draw()`: clear → "No syntax tree yet" hint if empty → translate+scale →
  optional selection **span-band** (translucent `rgba(255,217,77,0.16)` from
  the selected node's top down to the tree bottom, covering its leaf span) →
  edges colored by child `edgeResult.status` (error red / valid green /
  unlisted base) → node labels → restores transform → `_drawTooltip()`.
- `_drawTooltip()`: when hovering a node whose `describe(node.type)` returns a
  real meaning, draws a dark rounded pill near the cursor
  `NNP — Proper noun (singular)` (clamped to the canvas; skipped when the
  meaning equals the bare label, i.e. unknown tags).
- `_drawNode`: minimalist **text-only** rendering — no boxes or outlines.
  Label color: error node → red, root/hover → purple, selected → amber
  (`#c98f00`) with a heavier weight, else ink. Leaves draw their POS type in
  small 10px muted text **above** the word (word sits slightly below the row
  center; the incoming edge terminates **well above the tag** — ~11px of clear
  gap — so the annotation never touches the line).
  Hitboxes/layout still use the (now invisible) box geometry from
  `createLayout`. Selection highlight comes from the translucent span-band
  rather than a box fill.

---

## 8. Backend — `server/app.py` (HTTP + payload)

This is the canonical full-stack/local server (stdlib `http.server` + static
files from `web/` + `/api/*`). In production the same logic runs behind
`server/hf_space.py` (HF Space): Gradio is launched on port 7860 to satisfy the
ZeroGPU startup scan, then the identical `/api/health` and `/api/parse` handlers
are mounted on the FastAPI app Gradio returns. `server/app.py` is only ever used
directly for local development / the container image.

- `ROOT` = project dir (parent of `server/`); `PORT = env SYNTUTOR_PORT|8000`;
  host `127.0.0.1` / `SYNTUTOR_HOST`.
- `ThreadingHTTPServer` + `Handler` (server_version `SynTutor/2.0`).
- `MIME` map for `.html .js .css .json .svg .png .ico .md`.
- `_model_status()` — cached lazily; tries `load_models()` and reports
  `{ready, spacy version, benepar: 'benepar_en3', pipeline pipe names}`;
  on failure captures the exception text.

### Endpoints

| Method&Path | Behavior |
|---|---|
| `GET /` (or `/index.html`) | serves `index.html` |
| `GET /file…` | path-normalized read from `ROOT`; `..`/absolute → 403; missing → 404; `Cache-Control: no-store` |
| `GET /api/health` | 200 + model JSON when ready, else 503 + `install_hint` |
| `POST /api/parse` | see below |

### `POST /api/parse`

- Bad JSON body → 400. Empty/missing `text` → 422 `{error, hint}`.
  `sentence_index` (optional, 0-based integer) → 400 on non-integer/negative.
- `build_payload(text, sentence_index=0)`:
  1. `analyze(text, sentence_index)` (parse_engine) → analysis,
  2. `evaluate(analysis['root'])` (matrix) → details + summary,
  3. emits the JSON contract (§10).
- `ParseFailure` → 422 `{error, input}`.
- Any other exception (model missing) → 503 `{error, hint}` where hint comes
  from `_model_status().error` or the canonical install command
  (`pip install spacy benepar transformers==4.46.3` + model downloads).

`_contrastive(summary, details)` — deterministic contrastive text:
valid & no root error → "No grammatical alternative is observed…";
otherwise take the **first** error detail and phrase the repair from a break
map (`C-SUBJECT-AGREEMENT`, `C-DETERMINER-AGREEMENT`, `C-DET-STACK`,
`C-MOD-POS`, `C-AUX-FORM`, `C-TENSE-FINITE`), falling back to a generic
"after satisfying C-*".

`explainers` also reserves `surprisal: null`, `perturbation: null`,
`llm_note: null` — intentionally absent by design (see §15).

---

## 9. Backend — `server/parse_engine.py` (stages 3–4)

- Constants: `PARSER_BUNDLE='en_core_web_md'`, `PARSER_MODEL='benepar_en3'`.
- `load_models()` — module-level singleton `_nlp`; caches failures in
  `_load_error` and re-raises; builds `spacy.load(bundle)` + 
  `nlp.add_pipe('benepar', config={'model': model})`.
- `ParseFailure(Exception)` — the payload's 422 path.
- `parse_parse_string(tree_text)` — hand-rolled recursive-descent parser over
  the benepar `( ... )` string. Tokenizes with
  `re.findall(r'\(|\)|[^\s()]+', text)`. Returns nested tuples
  `('S', [('NP', [...]), ('VP', [...]), ('.', '.')])`. A node with exactly one
  child collapses to that child; raises on trailing tokens or bad structure.
- `NodeBuilder`:
  - ids: `n0, n1, …` (pre-order counter).
  - Builds for each leaf `{id, type(=pos), pos, span:[i,i+1), surface, punct}`
    where `punct` ⇔ tag ∈ `{., ,, :, ;, ?, !, \`\`, '', -RRB-, -LRB-}`,
  - for each internal node `{id, type(=phrase label or 'ROOT'/'PHRASE'),
    span:[first,last), surface (space-joined leaves), children:[…]}`,
  - **alignment guard**: after building, the number of consumed leaves must
    equal `leaf_count` (spaCy sentence token count) else `ParseFailure`.
- `token_metadata(nlp, doc, target)` — per token:
  `{i (0-based within sentence), t, pos, tag, dep, head(text)}`.
- `analyze(text, sentence_index=0)`:
  1. `nlp = load_models()`; `doc = nlp(text)`,
  2. segments `doc.sents`; **clamps** `sentence_index` into range; the target
     sentence is `sents[idx]` (multi-sentence policy: exactly one sentence
     analyzed per request, deterministically selectable),
  3. `parse_string = target._.parse_string`,
  4. `parse_parse_string` → `NodeBuilder.build(tagged, len(target))`,
  5. includes the full segmentation `sentences = [{ordinal, start, end,
     text}]` where `start`/`end` are **character offsets into the exact
     `text` string passed** (used by the frontend to map textarea carets to
     sentences),
  7. returns `{sentence, sentence_index, sentence_count, sentences, tokens,
     parse_string, root, nodes}`.

---

## 10. Backend — `server/matrix.py` (Stage 5 XAI, full detail)

### 10.1 Classification sets & feature tables

```
SENTENCE_CLASSES  = {S, SINV, SQ, SBARQ, FRAG, ROOT}
NOUN_CLASS        = {NN, NNS, NNP, NNPS, PRP, NML, NX}
VERB_CLASS        = {VB, VBD, VBG, VBN, VBP, VBZ, MD, AUX}
ADJ_CLASS         = {JJ, JJR, JJS}   ADV_CLASS = {RB, RBR, RBS}
DET_CLASS         = {DT}             PREP_CLASS = {IN, TO, POS, RP}
NOUN_PLURAL       = {NNS, NNPS}      NOUN_SINGULAR = {NN, NNP, NML, NX}
NONFINITE         = {VB, VBG, VBN}
```

Language tables (deterministic, hard-coded):

- `PRP_KEY` — pronoun features: `I→(1,sg) we→(1,pl) you→(2,None) he/she/it→
  (3,sg) they→(3,pl)`.
- `DET_NUMREQ` — determiner number requirement: `a an one this that each every
  another much → sg`; `these those both many several → pl`.
- `MODALS = will would shall should can could may might must`.
- `BE_FORM = am is are was were be been being`; `HAVE_FORM = have has had
  having`; `DO_FORM = do does did doing done`.
- `VERB_FORM_LABEL` — Penn verb tag → human form name.
- `IRREGULAR_PLURAL` — θ→θ shapes (child→children … sheep→sheep, fish→fish…).
- `inflect` — deterministic lexical/productive noun morphology used by
  `C-NOUN-FORM`; accepts legitimate alternatives (`cacti`/`cactuses`,
  `people`/`persons`) and rejects malformed plurals (`foots`, `childs`).
- `IRREGULAR_VBN` — 70+ irregular past-participles (be→been, eat→eaten…).
- `IRREGULAR_PAST` — irregular past-tense forms used to distinguish `VBD`
  (`came`) from `VBN` (`come`).

### 10.2 Morphological helpers

- `_preserve_case(source, word)` — mirrors leading capitalization.
- `_base_form(leaf)` — derives a best-effort base form from the observed
  surface and POS tag; no lemma is included in the payload.
- `_noun_form_issue(leaf)` — compares a parser-tagged plural with `inflect`'s
  accepted singular/plural relation; returns the canonical singular and
  expected plural for malformed forms, else `None`.
- `_plural_noun(word)` — irregular table → `s/x/z/ch/sh`→`+es` →
  consonant+y→`+ies` → `+s`.
- `_singular_noun(leaf)` — derives a singular noun form from the observed
  surface, including the maintained irregular-noun table.
- `_third_present(base)` — 3sg present: `be→is have→has do→does go→goes`,
  `s/x/z/ch/sh/o→+es`, consonant+y→`+ies`, else `+s`.
- `_nonthird_present(base)` — `be→are`, else base.
- `_vbn_form(base)` — irregular → VBN; `+e→+d`, else `+ed`.
- `_vbg_form(base)` — `be→being`, `lie/die/tie→ying`, `+e→-e+ing`, else `+ing`.
- `_replace_subject_head(subj, head, newword)` — rewrites the subject surface,
  swapping the trailing head for the replacement (capitalization preserved).

### 10.3 Feature functions

- `num_of(leaf)` — pl/sg from tag; PRP via `PRP_KEY`; else None.
- `person_of(leaf)` — NN*→'3'; PRP via key; else None.
- `subject_key(leaf)` — `(person, num)` or None.
- `verb_key(leaf)` — `MD/VBD → None` (person-neutral); `VBZ → ('3','sg')`;
  `VBP → ('*','non3sg')`; be/have/do special-cased by surface
  (`is/was→('3','sg')`, `am→('1','sg')`, `has/does→('3','sg')`, else
  `('*','non3sg')`).
- `agree(subject_leaf, verb_leaf)` — True if the verb is neutral, the subject
  is unmarked, or when the strict equality (with `('*','non3sg')` and
  `('2',None)` special cases) holds.
- `_is_valid_verb_form(leaf)` — rejects regularized irregular forms such as
  `becomed` and past-tense forms such as `came` when benepar places them in a
  `VBN` context.
- `phrase_head(node)` — deterministic head pick by phrase label:
  NP/NML/NX → **last** noun; VP → **first** verb; PP → **first** prep;
  ADJP → **last** adjective; ADVP → **first** adverb; S-clauses → **first**
  verb; else None.
- `clause_subject_and_verb(s_node)` — first NP child (subject), first VP child.
- `is_coordinated(node)` — True if the node has a `CC`/`CONJP`/`UCP` child;
  **a coordinated subject is always plural** (the "Jaisen and Kielle" fix).
- `_agreement_ok(skey, vkey)` — same logic as `agree` but on precomputed keys.

### 10.4 The edge evaluator (`MatrixEvaluator`)

`evaluate(root)`:
1. `_walk` fills `self.details[child_id] = _edge(parent, child)` for every non-root node,
2. `_root_level(root)`,
3. for each detail: build `checks`; if status error, attach `remediation` via `_remediate` (may be None),
4. returns `{details, summary}`.

`_edge(parent, child)`:
- punctuation child → valid `C-PUNCT` immediately (no matrix row),
- else `_classify(parent, child)` → `(status, constraint, text)` → `_detail(...)`
  with role from `_role_for(constraint)`.

#### `_classify` — the rule table (parent type → child type → verdict)

**`S`** (the heart):
- `NP` → `_s_subject`: valid `C-SUBJECT-ROLE` (agreement checked on predicate edge).
- `ADJP` → valid `C-SMALL-CLAUSE-PREDICATE` (small-clause predicate complement).
- `VP` → `_s_predicate`:
  - no verb head → error `C-TENSE-FINITE` ("no finite predicate verb"),
  - head is `NONFINITE` (VB/VBG/VBN): if the VP begins with the infinitival
    marker `TO` → valid `C-INFINITIVAL-COMPLEMENT` (`want to go`); else error
    `C-TENSE-FINITE`,
  - **pronoun case (subject)**: subject head is a `PRP` in `PRON_OBJ_PLAIN`
    (`me/us/him/her/them`) → error `C-PRONOUN-CASE` (use nominative),
  - else compute `subj_head`, `coordinated = is_coordinated(subj)`,
    `skey = ('3','pl') if coordinated else subject_key(subj_head)`,
    `vkey = verb_key(vp_head)`; if `_agreement_ok` → valid `C-PREDICATE`
    naming subject label + verb form; else **error `C-SUBJECT-AGREEMENT`**.
- `ADVP`/`PP` → valid `C-CLAUSAL-ADVERBIAL`; `SBAR` → valid `C-CLAUSAL-COMPLEMENT`.

**`NP`** → `_np_rule(parent, child, grandparent)`:
- determinative child (`DT`, `PRP$`, or a bare `PRP` surfacing as one of
  `my/your/our/their/its`): if **two determinatives** → error `C-DET-STACK`;
  DT → `_det_num`; else possessive → valid `C-DETERMINER`. If the NP has
  **no nominal head** after a determiner → error **`C-HEAD-NOUN`** (head
  licensing: `I hate your.`), unless the determiner is a standalone
  demonstrative/quantifier (`this/that/these/those/each/some/one/all/...`)
  which may head an NP.
- noun head: valid `C-HEAD-NOUN` (with number); **and** if the head is a bare
  singular common `NN` in an argument position (grandparent `S`/`VP`), with no
  determinative and not exempt (mass/gerund/institutional nouns) → error
  **`C-ARTICLE`** (`Dog is barking.`); other noun → `C-NOUN-ADJUNCT`.
- `JJ/JJR/JJS/ADJP` or `CD/PDT/QP` → `_modifier_pos` (head must precede it);
  quantifier adjectives `less/fewer/much/many/little/few` → `_quantifier_check`
  (error `C-QUANTIFIER` on number mismatch, `less cookies`→`fewer`).
- `PP` → `C-NP-POSTMODIFIER`; `VP` → `C-NP-REDUCED-RELATIVE`;
  `SBAR`/`S` → `C-NP-RELATIVE`; `CC` → `C-COORDINATOR`;
  `NP/NML/NX` → `C-NP-COMPOUND`; else `_unlisted`.

`phrase_head` → `_np_head` for NPs: noun candidates **exclude** possessive
determiner surfaces (`my/your/our/their/its`); with a determinative present and
no noun, a trailing adjective may serve as a nominalized head (`my favorite`).

`_det_num` — `numreq = DET_NUMREQ[lower(det)]`, `num = num_of(head)`; mismatch
→ error `C-DETERMINER-AGREEMENT`; match → valid `C-DETERMINER` (number stated);
no info → `C-DETERMINER` (number-neutral). For `a/an_` additionally runs the
phonetic article check (silent-h `an hour`; vowel-letter-with-consonant-sound
`a university`) → error `C-ARTICLE-MISMATCH`.

`_modifier_pos` — if modifier span starts after head span start → error
`C-MOD-POS` (modifier after head); else valid (precedes head).

`_is_postnominal_numeral` — a `CD` child whose singular noun head is in the
closed `POSTNOMINAL_NUMERAL_HEADS` set (numbered/labelled entities: *the number
seven*, *the year 2020*, *page three*), appears immediately after that head, and
is the final leaf of the `NP` → valid `C-NUM-IDENT` (postnominal numerical
identifier). A cardinal after any other head, or anywhere else in the `NP`,
falls through to `_modifier_pos` and stays a genuine `C-MOD-POS` violation
(e.g. *the honesty seven*), so the change refines — never disables — the CD
modifier-position check.

**`VP`** → `_vp_rule`:
- verb-class child → `_aux_class` ? classify aux → see `_aux_check` : head:
  `_verb_head` (finite/non-finite role text, `C-HEAD-VERB`).
- noun child → error **`C-HEAD-VERB`** (VP headed by a noun, e.g.
  `I am agree.`); `VP` → `C-AUX-COMPLEMENT`; `NP` → `C-DIRECT-OBJECT`, but a
  nominative pronoun head (`I/we/he/she/they`) after an action verb → error
  **`C-PRONOUN-CASE`** (`call she` → `call her`); `PP` → `C-ADJUNCT`;
  `ADJP` → `C-PREDICATE-ADJECTIVE`, but after a non-linking verb with no
  preceding object NP → error **`C-ADJ-ADV`** (`sings beautiful`);
  `ADVP` → `C-ADVERBIAL`, but flat-adjective-head adverbs
  (`quick/slow/good/real/...`) → error **`C-ADJ-ADV`** (`runs quick`);
  `SBAR` → `C-CLAUSAL-COMPLEMENT`; `S` → `C-SMALL-CLAUSE`;
  `TO` → `C-INFINITIVAL-MARKER`; `RP` → `C-PARTICLE`; else unlisted.

`_aux_class(child)` — type MD/AUX or surface ∈ MODALS/BE/HAVE/DO.

`_aux_check` — class modal/be/have/do; find `_following_verb` (first verb leaf in
the sibling VP) and require forms:
- modal & do → `{VB}` (base), have → `{VBN}` (past participle),
  be → `{VBG, VBN}` (participle).
- match → valid `C-AUXILIARY`; mismatch → **error `C-AUX-FORM`**.
- missing following verb → falls back to `_verb_head` (valid).

**`PP`**: prep child → `C-HEAD-PREPOSITION`; `NP` → `C-PREP-OBJECT`, but a
nominative pronoun object → error **`C-PRONOUN-CASE`** (`to she` → `to her`).

**`ADJP`**: `ADJ_CLASS` → `C-HEAD-ADJECTIVE`;
`RBR`/`RBS` (`more`/`most`): a `JJR`/`JJS` sibling → error **`C-COMPARATIVE-DOUBLE`**
(`more smarter`), else `C-INTENSIFIER`; RB → `C-INTENSIFIER`; VBN/VBG →
`C-PARTICIPLE-MODIFIER`.

**`ADVP`**: `ADJ_CLASS` → error **`C-ADJ-ADV`**; `NP` → `C-ADVERBIAL-COMPLEMENT`
(`an hour ago`); RB/RBR/RBS/ADVP → `C-HEAD-ADVERBIAL`; `CC` → `C-COORDINATOR`.

**`SBAR`**: `S` → `C-RELATIVE-CLAUSE`; `IN` → `C-COMPLEMENTIZER`;
`WHNP/WHPP/WHADVP/WADVP/WPP` → `C-RELATIVE-HEAD`.

**`WHNP`**: `WP/WDT/WP$` → `C-RELATIVE-PRONOUN`; `NOUN_CLASS` → `C-RELATIVE-NOUN`.

**`WHPP/WHADVP/WADVP/WPP`**: → `C-RELATIVE-HEAD`.

**Sentence classes (SINV/SQ/SBARQ/FRAG/ROOT)**: `NP` → `C-CLAUSE-SUBJECT`;
`VP` → `C-CLAUSE-PREDICATE`.

**Any unmatched pair** → `_unlisted` → `('unlisted','C-UNLISTED', …)` — the
audit's sentinel; must stay at 0 for the corpus.

### 10.5 Root-level check

`_root_level(root)` — root type ∈ `SENTENCE_CLASSES`: first token begins with a
**lowercase** letter → error **`C-CAPITALIZATION`** (needs a capital); else
valid `C-ROOT`. Root not in `SENTENCE_CLASSES` → **error `C-TENSE-FINITE`** with
role `'fragment root'` (fragment input, e.g. "The boy running.").

### 10.6 Node detail schema + checks

`_detail(...)` emits:
```
{ id, type, pos, surface, span, parent, rule, children_ids,
  children: [{id,type,surface}], role, constraint, status, text }
```
`_rule_for` → `"NP → DT + JJ + NN"` or `"NN → 'boy'"`.
`_checks_for` — deduped checklist: the node's named check (`CHECK_LABELS`),
a "Rule membership (C-*)" row (or "Matrix coverage (unrated · valid-by-default)"),
plus named checks of each child (grouped by shared label).

### 10.7 Case-B remediation dispatcher (`_remediate`)

Constraint → method:

| constraint | method | produces |
|---|---|---|
| `C-SUBJECT-AGREEMENT` | `_rem_agreement` | violation; `suggested_fix` re-conjugates verb to the correct form; `alternative_fix` via `_subject_fix_alternative`; outcome `Subject NP + VBZ/VBP` |
| `C-DETERMINER-AGREEMENT` | `_rem_det` | change noun (pl/sg) or swap determiner; outcome `DT + NNS` / `DT + NN` |
| `C-AUX-FORM` | `_rem_aux` | modal/do→base (`VB`), have→VBN, be→VBG/VBN; alternative for modal ("drop modal, use finite verb") and do (rephrase) |
| `C-DET-STACK` | `_rem_det_stack` | remove extra determiners, keep first |
| `C-MOD-POS` | `_rem_mod_pos` | move modifier before head |
| `C-HEAD-NOUN` | `_rem_head_noun` | add a noun after the bare determiner (`your` → `your idea`) |
| `C-PRONOUN-CASE` | `_rem_pronoun_case` | swap nominative↔objective from `SENTENCE_CLASSES`/`VP`/`PP` parent position |
| `C-ADJ-ADV` | `_rem_adj_adv` | `-ly` adverb form via `_adverbial_form` (`quick`→`quickly`, `good`→`well`) |
| `C-ARTICLE` | `_rem_article` | insert `_indefinite_article(head)` before the noun |
| `C-ARTICLE-MISMATCH` | `_rem_article_mismatch` | swap `a`↔`an` to the phonetic match |
| `C-CAPITALIZATION` | `_rem_capitalization` | capitalize the first letter |
| `C-QUANTIFIER` | `_rem_quantifier` | `less`↔`fewer`, `much`↔`many`, `little`↔`few` |
| `C-HEAD-VERB` | `_rem_vp_head_noun` | give the VP a real verb head (auxiliary + participle) |
| `C-COMPARATIVE-DOUBLE` | `_rem_double_comparative` | keep the morphological `JJR`/`JJS` only |
| `C-TENSE-FINITE` (root fragment) | `_rem_fragment` | restructure as `S → NP + VP`, e.g. "'… runs.'" |
| `C-TENSE-FINITE` (non-finite predicate) | `_rem_finite_verb` | add `is` before VBG or finite VBZ; outcomes per VBG/VBN/VB |
| any other | `_rem_generic` | generic: "satisfy the {check}" |

Every remediation is `{violation, suggested_fix, alternative_fix,
targeted_outcome}` (alternative/outcome may be None).

`_subject_fix_alternative` details:
- coordinated subject → "drop the conjunction and use just '{head}'"; uses
  `she/he` as a neutral singular placeholder for non-3rd-person heads (avoids
  mispaired pronouns like "I is").
- non-coordinated: match the verb's (3,sg) vs plural side, incl. pronoun swaps
  (`they→he or she`, `we→I`, `he→he or she`).

### 10.8 Summary

`_summarize(root)`:
- edges = all details except root; `valid/violated/unrated` counts;
- `violations` = error edges (+ root detail if root error);
- `valid` = no violations;
- `explanation` priority: root-error text → first error text → "All N validated
  edge(s) are licensed … grammatical.";
- `constraints_fired` = sorted unique constraint ids across violations;
- `root_error` bool.

---

## 11. REST payload contract (`build_payload` output)

```jsonc
{
  "meta": {
    "deterministic": true, "k": 1,
    "parser": "benepar_en3", "spacy": "en_core_web_md",
    "backend": "spaCy + benepar (neural constituency) + rule matrix (XAI)",
    "sentence_count": <int>, "target_sentence": <1-based index analyzed>
  },
  "parse": {
    "text": "<target sentence>", "sentence_count": <int>,
    "sentences": [ { "ordinal", "start", "end", "text" } ],  // char offsets into input
    "tokens": [ { "i", "t", "pos", "tag", "dep", "head" } ],
    "parse_string": "(S (NP ...) (VP ...) (. .))"
  },
  "tree":   <nested {id,type,span,surface,children?}>,
  "nodes":  { "n0": <node>, ... },
  "node_details": { "n0": { id,type,pos,surface,span,parent,rule,children_ids,
                            children[], role, constraint, status, text, checks[],
                            remediation? } },
  "summary": { valid, valid_edges, violated_edges, violations[],
               unrated_edges, constraints_fired[], root_error, explanation },
  "explainers": {
    "basic": "<multi-line text>", "contrastive": "<text>",
    "surprisal": null, "perturbation": null, "llm_note": null
  },
  "semantics": {
    "status": "ok",              // 'ok' | 'unavailable'
    "available": true,           // false on a controlled semantic-layer failure
    "findings": [ { rule, constraint, status,   // status: 'error' | 'warning'
                    category, text, evidence, suggestion,
                    confidence_label,           // qualitative: 'Direct Rule Match'
                                                // | 'Advisory Suggestion'
                    provenance } ],             // e.g. "deterministic rule R11.6 (...)"
    "ambiguous": false,
    "ambiguity": { "ambiguous": false, "readings": [ ... ],
                   "preposition": "with", "scope": "<two-reading, non-exhaustive>" } | null,
    "tree_variants": [ { attachment, root, pp, np } ],
    "summary": { status, available, valid, findings, errors, warnings,
                 constraints_fired[], ambiguous_attachments[],
                 tree_variants, explanation }
  }
}
```

`explainers.basic` (line-by-line): Input · benepar parse string · token stream ·
matrix counts (`N validated · M violated · K unrated`) · `Verdict: VALID/INVALID`
· explanation · determinism note.
`node_details[].status` ∈ `valid|error|unlisted`; `constraint` is a `C-*` id.
The additive `semantics` block (Stage 11, §17) never changes the syntax result.
Findings always carry a **qualitative** `confidence_label` and a `provenance`
string — no numeric probability is ever emitted. When the semantic layer raises,
the server logs the traceback and returns `semantics.status = 'unavailable'`,
`available: false`, `findings: []` — a failure is never presented as an ordinary
"no findings" result.

---

## 12. Coverage audit — `scripts/audit_rules.py`

- `GOLD`: **99 sentences** (51 expected-valid / 48 expected-invalid) tagged with
  a `why` note — including the regression cases that previously slipped through:
  coordinated-subject agreement ("Jaisen and Kielle is…"), determiner stacking
  ("The my book…", "His the car…"), NP head-licensing ("I hate your.",
  "Their is a problem."), pronoun case ("Me likes music.", "to she"),
  adjective–adverb confusion ("runs quick.", "sings beautiful"), missing/mismatched
  articles ("Dog is barking.", "a elephant", "an hour" happy path), capitalization
  ("he runs fast."), quantifier agreement ("less cookies", "many apple"),
  double comparatives ("more smarter"), and the clause-level structures added
  during this session ("In the park, they run fast.", "That he left is true.",
  relative clauses, to-infinitive complements, small clauses).
- `edge_iter(details)` — yields `(parent_type, child_type, constraint, status)`
  for every non-root detail (parent type recovered from the details map).
- `run_corpus()` — drives the **real** `parse_engine.analyze` + `matrix.evaluate`
  (imports via `sys.path` root insert); collects per-sentence verdict match,
  edge-type counter, status counter, and the set of `unlisted` edge types.
- `report()` — prints the verdict summary, regressions (with `fired`),
  edge totals, the edge-coverage matrix (`[NP] -> DT x38`, …), unlisted-edge
  list, and a `SUMMARY: gold regressions=N  unrated_edge_types=N  edges=N` line.
- `npm run audit` = `python3 scripts/audit_rules.py`. The semantic layer has its
  own six-gate audit, `npm run audit:semantics` =
  `python3 scripts/audit_semantics.py` (see §17). The syntax corpus (`GOLD`) is
  kept semantically neutral so syntax-correctness tests and semantic-expectation
  tests stay separate.
- `main()` returns **exit 1 if any regression or any unrated edge type**, else 0.
  Run via `python3 scripts/audit_rules.py` or `npm run audit`.
  Current green state: 99 sentences, 888 edges, 0 distinct+unrated, 0
  regressions, 0 unrated.

---

## 13. Runtime configuration & verification

**Local (full-stack):** `python3 server/app.py` (or `npm run serve`); port 8000
(override `SYNTUTOR_PORT`), host 127.0.0.1 (override `SYNTUTOR_HOST`).
- Health: `curl -s http://127.0.0.1:8000/api/health`.
- Parse: `curl -s -X POST http://127.0.0.1:8000/api/parse -H 'Content-Type:
  application/json' -d '{"text":"The boys runs."}'`.

**Production (HF Space):** `server/hf_space.py` launches Gradio on port 7860 (the
platform's `PORT`/`GRADIO_SERVER_PORT`) and mounts `/api/health` + `/api/parse`
on it; the frontend on Vercel calls the API cross-origin via `API_BASE` in
`web/js/config.js` (currently `https://ybcole-syntutor.hf.space`). CORS headers
are emitted by the API handlers; `GRADIO_SSR_MODE=false` is set so the mounted
routes are served reliably. `@spaces.GPU` on `_zerogpu_noop` satisfies ZeroGPU's
startup scan but is never invoked (CPU-only backend, so no GPU quota is consumed).

- Local static assets are read from disk **per request** (served with
  `no-store`), so JS/CSS/index edits show up on a hard refresh; **Python
  changes require a server restart**.
- Model pin: `transformers==4.46.3` (benepar's retokenizer relies on
  `T5Tokenizer.build_inputs_with_special_tokens`, which newer transformers
  removed). On the Space, `torch.cuda.is_available()` is forced to `False`
  while models load so benepar stays on CPU under ZeroGPU's CUDA emulation.
- Determinism premise: benepar + spaCy with identical serialized input produce
  the same tree/tags; the matrix has zero randomness; multi-sentence input is
  pinned to **sentence 1** (`sents[0]`).

---

## 14. Compliance with `THESIS.md` (the design spec)

| Spec section | Status | Where |
|---|---|---|
| 7-stage IPO pipeline | ✅ Implemented | §2 table, `main.js` |
| PCFG 5-tuple `G=(N,Σ,R,S,P)` | ⚠️ **Diverged** | replaced by trained neural parser (§15) |
| CYK + Viterbi `π(i,j,A)`, CNF, backpointers, `O(n³·\|G\|)` | ❌ Not implemented | see §15 |
| MAP tree `argmax P(T)`, S-rooted phrase structure | ✅ Output contract met | benepar `parse_string` |
| XAI `E(v_d,v_p)` vs `𝒞`, `f_valid`/`f_error` | ✅ Implemented | §10.4 |
| Deterministic non-generative feedback | ✅ Implemented | whole matrix |
| FSM `IDLE→PROCESSING→VIEWING⇄EXPLORING→END` | ✅ Implemented (`END` defined, no transition wires it) | §6 |
| Interaction Loop (memory, no re-parse) | ✅ Implemented | `session.payload`, `handleNodeSelect` |
| Re-Entry Loop, **no auto-correction** | ✅ Implemented | suggestion-only remediation |
| Phrase-structure only; dependency parsing excluded | ✅ | benepar is constituency-based; dep tags only appear in `parse.tokens` metadata diagnostics |
| English-only scope | ✅ | spaCy/benepar English models |

### 15. The one intentional divergence — the parser engine

The spec's stages 1–2 (PCFG+CYK+Viterbi, CNF binarization, `π(i,j,A)` table,
backpointer serialization) were **not reimplemented**; the tree is instead
produced by benepar, a trained neural constituency parser. Rationale from the
project decision:

- The spec's mathematical parser — hand-authored grammar, `O(n³·|G|)` — is a
  textbook construction; a manually authored grammar cannot cover the range of
  real learner sentences. benepar reproduces the **same output contract**
  (single best S-rooted constituent tree consumed deterministically by the
  matrix) with far better coverage.
- Every downstream guarantee the spec cares about — XAI integrity (100%
  deterministic, no hallucination), explainer grounding in the tree, dual-loop
  feedback — is independent of which parser produced the tree.

This remains an open design decision; the current implementation makes no
representations that it runs CYK. `README.md` and `RULES.md` describe the
implementation as-built; `THESIS.md` remains the specification.

---

## 16. Known design notes

- `END` is declared in `STATES` but never reached by a transition event (the
  app keeps the session alive in VIEWING/EXPLORING).
- `explainers.surprisal/perturbation/llm_note` are always `null` — reserved
  slots that are intentionally not implemented (generative paths are excluded).
- `build_payload` computes a local `error_ids` list that the contrastive
  builder does not consume (it re-derives errors) — harmless.
- Sentence verdict summary text is deterministic and re-stated verbatim in
  `explainers.basic`; node detail text is generated once at parse time and
  served from memory thereafter.
- The semantic layer emits **qualitative** confidence labels
  (`Direct Rule Match` / `Advisory Suggestion` / `Insufficient Evidence`) and a
  human-readable `provenance` string. There are no numeric confidence values —
  the feedback path contains no trained/probabilistic model (`audit_ui.mjs`
  fails if a fabricated decimal reappears).
- The semantic lexicons are open-world at the edges: explicit project lexicons
  are consulted first, then an **optional local WordNet (NLTK) fallback**; a noun
  that neither establishes is left *unclassified* and is never turned into a
  finding, so false positives are favoured against at the cost of some recall.
  WordNet is never downloaded at request time and the app degrades to the
  explicit lexicons when it is absent.
- R11.6's biological-state class is organised into a **physiological** subclass
  (`hungry, thirsty, tired, sleepy, exhausted, starving, pregnant, sick`) and a
  **life/death** subclass (`dead, alive`); at most one finding is emitted per
  (clause, subclass), so `hungry and starving` is not reported twice.
- R11.3 is evaluated **per clause**: a deictic anchor and the predicate it
  clashes with must share a clause. The earlier blanket "any habitual marker
  anywhere suppresses the sentence" rule was removed — genericity is signalled
  structurally by the absence of a deictic anchor, so `The children play in the
  park every day.` still never fires while `Yesterday I go to school every day.`
  correctly does.
- The UI shows **two independent status indicators** — Syntax (`Valid` /
  `Issues Found`, from the matrix) and Semantics (`No Findings` / `Suggestions
  Available` / `Issues Found` / `Analysis Unavailable`, from the semantic layer) —
  so an unavailable analysis can never be mistaken for a clean syntax verdict.
- `C-NUM-IDENT` licenses a postnominal cardinal only after a head noun in the
  closed `POSTNOMINAL_NUMERAL_HEADS` list; any other head keeps `C-MOD-POS`.
- A `warning` finding is advisory only and never affects the syntax
  `summary.valid` / `constraints_fired`.

---

## 17. Semantic layer (Stage 11, spec R11)

`server/semantics.py` is a **deterministic, additive** layer that runs after the
matrix (in `app.build_payload`). It never mutates the analysis or the matrix
result, so the syntax verdict is preserved bit-for-bit (audit Gate 1). There is
no ML/HF/cloud dependency in the meaning checks: its inputs are the token stream
and the benepar tree. Classification starts from explicit project lexicons and
optionally falls back to a local, offline WordNet corpus exposed by
`server/lexicon.py`. The layer is *additive*: it never changes
`summary.valid` / `constraints_fired`, and a failure is isolated.

### 17.1 Findings

| rule | constraint | status | check |
|---|---|---|---|
| R11.2 / R8.1 | `S-PREPOSITION` | `error` | governed preposition (`depend in` → `on`) |
| R11.2 / R8.1 | `S-COLLOCATION` | `error` | light-verb collocation (`do a decision` → `make`) |
| R11.3 | `S-TENSE-TIME` | `error` | deictic past/future/present cue clashing with the predicate of the *same clause* (`Yesterday I go`); no deictic anchor ⇒ no finding |
| R11.4 | `S-SELECTIONAL` | `error` | animate subject / classed object (`The book eats the boy`) |
| R11.6 | `S-PREDICATE-COMPAT` | **`warning`** | copular biological-state predicate on an unsupported subject (`The number seven is hungry.`) |
| R11.5 | — | (ambiguity) | PP-attachment candidate readings |

The R11.3 check is clause-scoped: a habitual/frequency adverb no longer
blanket-suppresses the sentence, so a genuine mismatch in the main clause is
reported even when a subordinate clause is generic (and vice-versa).

Each finding exposes `rule`, `constraint`, `status`, `category`, `text`,
`evidence`, `suggestion`, plus a qualitative `confidence_label`
(`Direct Rule Match` for definitive rules, `Advisory Suggestion` for the hedged
R11.6 warning) and a `provenance` string. No numeric confidence is emitted.

R11.5 does not assert a single "correct" attachment: it presents **two primary,
hedged candidate readings** — a verb-phrase (adjunct) reading and a noun-phrase
(modifier) reading — whose wording is **preposition-aware** (`with` =
instrument/accompaniment vs. possession/attribute; `in`/`at`/`on` =
location/setting; `for` = purpose/beneficiary), plus a `scope` note stating the
comparison is not exhaustive. Unmodelled prepositions fall back to neutral
candidate wording.

### 17.2 Entity taxonomy and uncertainty

The layer classifies a common-noun lemma into one of four coarse classes plus an
explicit *unclassified* result:

| class | source / example |
|---|---|
| `animate` | explicit `ANIMATE_NOUNS`, WordNet `animal/person` hypernyms (`dog`), a personal pronoun (`I/we/you/he/she`), or a spaCy `PERSON` named entity |
| `living` | WordNet `living_thing.n.01` without an animate sense (`bacterium`) |
| `inanimate` | explicit `INANIMATE_OBJECTS` / edible / drinkable sets, or WordNet `artifact` (`car`, `telescope`) |
| `abstract` | explicit `ABSTRACT_NOUNS`, or WordNet `abstraction` (`number`, `algorithm`) |
| `None` | no evidence — an unknown word (`zorblax`) or a genuinely ambiguous/polysemous one (`bank`) |

Precedence is explicit project lexicon → optional WordNet fallback → pronoun /
NER → `None`. `ABSTRACT_NOUNS` is deliberately *not* a reuse of the object
lexicon: a number is not a physical object merely because both are non-animate.
An `None` class is **not** collapsed into "inanimate", so an unknown noun never
supports a finding. WordNet classification requires a **strict majority** of a
noun's synsets to agree (deterministic tie-break by class name); a split noun
stays `None`. `server/lexicon.py` loads WordNet lazily, caches results
in-process, never downloads at request time, and degrades to the explicit
lexicons when NLTK/the corpus is absent.

R11.6 matches the subject's class against the predicate's subclass:
**physiological** states (`hungry, thirsty, tired, sleepy, exhausted, starving,
pregnant, sick`) require an animate subject (abstract/inanimate flagged; a mere
*living* organism is not); **life/death** states (`dead, alive`) require a living
subject (only abstract subjects are flagged — a "dead battery" is idiomatic). At
most one finding is emitted per (clause, subclass), so `hungry and starving` is
reported once. The message frames the result as an anomaly *"under a literal
interpretation"* that invites a figurative or personified reading; it never
claims the sentence is objectively meaningless or ungrammatical.

### 17.3 Output contract and failure handling

`analyze_semantics` returns `{status, available, findings, ambiguous, ambiguity,
tree_variants, summary}` (see §11). On an unexpected exception, `app.py` logs the
full traceback server-side and substitutes a schema-consistent payload with
`status='unavailable'`, `available=false`, `findings=[]`. `js/ui.js` then shows a
distinct "Semantic analysis unavailable" notice — never the ordinary
"No semantic anomalies detected" state — while the syntax verdict stays visible.

The UI surfaces two **independent** status chips (`renderStatusStrip` in
`js/ui.js`): **Syntax** (`Valid` / `Issues Found`, from `summary.valid`) and
**Semantics** (`No Findings` / `Suggestions Available` / `Issues Found` /
`Analysis Unavailable`, derived from the semantic payload). They never overwrite
one another, so an unavailable semantic analysis can never be read as a clean
syntax verdict.

### 17.4 Audit

`npm run audit:semantics` (`scripts/audit_semantics.py`) runs six gates:

1. **matrix invariance** — `summary.valid` + `constraints_fired` are identical
   before and after `analyze_semantics` for every gold sentence;
2. **false-positive guard** — the semantically-neutral corpus (gold + extras,
   including unclassified nouns) produces zero findings;
3. **finding-set guard** — each expectation sentence produces *exactly* the
   documented finding multiset (rule / constraint / severity / count): a stray
   extra finding fails as loudly as a missing one, and every finding must carry
   a qualitative `confidence_label` and a `provenance` string;
4. **R11.5 + §6** — `The boy saw the man with a telescope.` yields two
   structurally distinct, span-valid, hedged readings with distinct paraphrase /
   node_details, the `scope` note states the two-reading, non-exhaustive scope,
   and the candidate wording is preposition-aware (`with` / `on` / `for` cases);
5. **target** — `The number seven is hungry.` is syntactically valid with no
   false `C-MOD-POS` on `seven` and yields the advisory literal-interpretation
   warning (labelled `Advisory Suggestion`);
6. **failure handling** — a simulated `analyze_semantics` failure preserves the
   syntax verdict and reports `semantics.status='unavailable'`.

The syntax gold corpus is kept semantically neutral, so syntax-correctness tests
and semantic-expectation tests (`SEMANTIC_CASES` / `SEMANTIC_NEUTRAL_EXTRA`) are
separated cleanly.

The semantic panel itself is covered by a dependency-free DOM-shim audit,
`npm run audit:ui` (`scripts/audit_ui.mjs`): it asserts that findings carry the
qualitative labels (`Direct Rule Match` / `Advisory Suggestion` / `Insufficient
Evidence`) and never a fabricated decimal, that an advisory (`warning`) card is
rendered distinctly from a definitive error, that an `unavailable` payload shows
the dedicated notice rather than the empty "no findings" state, that the
independent Syntax/Semantics status indicators cover all four documented states,
and that R11.5 pills render, state the two-reading scope, and dispatch the
selection callback.