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
| Frontend | Vanilla ES modules, HTML5 `<canvas>`, no frameworks, no build step |
| Backend | Python 3.10+ stdlib `http.server`, no Django/Flask |
| NLP | spaCy `en_core_web_md` + benepar `benepar_en3` + `transformers<4.47` pin |
| Parsing output | single MAP constituent tree drawn from `span._.parse_string` |
| Verification | `python3 scripts/audit_rules.py` (gold corpus, fails loud) |

---

## 2. Repository layout & module inventory

```
SynTutor/
  index.html              UI shell (all 16 wired element IDs, §3)
  package.json            {serve, audit} npm scripts
  README.md               quick start + spec-level overview
  RULES.md                full rule-matrix inventory (sibling doc)
  THESIS.md               original design specification (input document)
  ARCHITECTURE.md         this file
  css/style.css           394-line design system (§4)
  js/main.js              200 lines: FSM + pipeline orchestration
  js/renderer.js          387 lines: canvas layout/draw/hitbox/zoom/keyboard
  js/ui.js                291 lines: DOM views, explainer, dev panel, logs
  server/app.py           240 lines: HTTP server + payload assembly
  server/parse_engine.py  202 lines: NLP load, parse-string -> node graph
  server/matrix.py        1615 lines: rule matrix + XAI + remediation
  scripts/audit_rules.py  238 lines: gold-corpus coverage audit (exit-code gate)
```

### The seven pipeline stages (as implemented)

| # | Stage | Producer | Consumer | UI feedback |
|---|-------|----------|----------|-------------|
| 1 | User Input | textarea `#inputText` | `main.js executePipeline` | session label "Processing…" |
| 2 | Request `/api/parse` | `fetch` POST JSON | `server/app.py build_payload` | FSM badge PROCESSING |
| 3 | Tokenize + POS | spaCy `nlp(text)` | `parse_engine.token_metadata` | token stream |
| 4 | Parse tree | benepar `span._.parse_string` | `parse_parse_string` → `NodeBuilder` | parse string |
| 5 | Validate Ψ matrix | `matrix.evaluate(root)` | `MatrixEvaluator` | node colors |
| 6 | Generate explanations | `build_payload` (`basic`, `contrastive`) | `renderSentenceVerdict` | verdict card |
| 7 | Canvas + feedback loop | `TreeRenderer.setTree` | cache in `session` memory | Explorer |

The seven steps are **not shown as UI chips anymore** — progress is visible
only via the FSM badge, the session label, and the dev-panel log (each stage
logs a `Stage N:` line).

---

## 3. Frontend — `index.html`

Layout is a three-column shell; `<body>` is `flex column; overflow:hidden`
(no page scroll — the canvas and panels scroll internally).

Element registry (all are read or written by the JS, exact ids):

| Element | Kind | Role |
|---|---|---|
| `#stateBadge` | span | FSM state pill (data-state colors: IDLE/PROCESSING/VIEWING/EXPLORING) |
| `#sessionLabel` | span | "Idle" / "Processing…" |
| `#inputText` | textarea | paragraph-capable input; starts `readOnly`. Double-click enters edit mode; blur re-locks and auto-re-analyzes on changed text; when locked, clicking positions a caret so sentence activation works |
| `#inputHint` | p | `.input-hint` — live instruction line (editing ↔ locked) |
| `#treeCanvas` | canvas | `tabindex=0`, keyboard navigable, aria-label |
| `#canvasOverlay` | div | `.canvas-overlay`, `pointer-events:none` (see §4) |
| `#explainNode` | div | primary plain-English explainer container (no header/clear button — filled by `renderNodeDetail`/`renderDiagnostic`) |
| `#devPanel` | `<details>` | collapsible developer panel |
| `#sentenceVerdict` | div | auto-generated pedagogical summary |
| `#parseString` | `<pre>` | raw benepar parse string |
| `#tokenStream` | `<pre>` | spaCy token table (i, t, pos, tag, lemma) |
| `#logPanel` | div | prepend-most-recent system/FSM log |

Module graph (`<script type=module src=js/main.js>`):

```
main.js ──> renderer.js   (TreeRenderer, createLayout, COLORS)
   └─────> ui.js        (FSM badge, logs, views, fillDevPanel)
```

---

## 4. Frontend — stylesheet `css/style.css`

Design tokens (`:root`):

```css
--bg #f4f3fb  --panel #ffffff  --ink #2b2440  --muted #77708f
--accent #6d5ae6  --accent-soft #efeafc  --ok #2e8b57  --err #d64545
--warn #c98f00  --border #e3e0f2  --radius 12px
```

Key layout facts:

- `.app-main`: `grid-template-columns: 1fr 340px`; gap 14px; padding `10px 14px 6px`.
- `.app-header`: fixed 60px; `.state-badge` data-state palettes; PROCESSING pulses.
- `.canvas-wrap`: `position:relative; flex:1; overflow:hidden`.
- **`.canvas-overlay`**: `position:absolute; inset:0; pointer-events:none` —
  this is the fix that made node clicks reach the canvas again (an earlier
  `pointer-events:auto` version swallowed every mouse event). When `:empty`
  the background is fully transparent.
- `.dev-panel[open]`: `max-height:46vh; overflow:auto`. `.dev-grid`:
  `repeat(4, 1fr)` — verdict / parse string / token stream / log.
- `.primary-explainer` + `.node-explainer`: column flex, inner scroll.
- Explainer sections: `.ex-sec .ex-label .ex-identity .ex-badge(.root)
  .ex-role .ex-plain(mark) .ex-rule .ex-text .ex-checks(.ck.ok/.no)`.
- Remediation (Case B): `.remediation` (red top border), `.rem-title`,
  `.rem-body`, `.rem-row`, `.rem-key`, `.rem-value`, `.rem-outcome`.
- Canvas focus: `#treeCanvas:focus { outline: 2px solid var(--accent) }`.
- Responsive `@media (max-width: 1100px)`: `.app-main` stacks to one column,
  the right panel becomes a 2-col grid, `.log-card` spans both.

---

## 5. Frontend — `js/ui.js` (views, logs, dev panel)

Exports: `setStateBadge, log, clearOverlay, showCanvasMessage,
renderSentenceVerdict, renderNodeDetail, renderDiagnostic, fillDevPanel,
applySentenceSelection, setProcessBusy`.

- `PLAIN_NAME` — canonical Penn-label → plain-English dictionary (~45 entries)
  used by `plainName(type)`; unknown labels fall back to the raw type.
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
  `#tokenStream` (tab-separated `i  t  pos  tag  lemma:x`).

---

## 6. Frontend — `js/main.js` (FSM + orchestration)

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
- `lockInput()` — after a successful payload the textarea is normalized to
  the trimmed text, `readOnly = true`, hint switched to "click any sentence",
  the textarea blurred, and `ui.applySentenceSelection(payload)` highlights the
  analyzed sentence span (native text-selection, scroll preserved).
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
    !payload.summary.valid)`;
  - **`session = { payload }`** ← the in-memory cache that powers the
    Interaction Loop; input normalized + locked (`lockInput`),
    `applySentenceSelection(payload)` highlights the analyzed sentence, then
    stage 7: `renderer.setTree(payload.tree)` → VIEWING.
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

## 7. Frontend — `js/renderer.js` (canvas layout, drawing, interaction)

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
  (`pip install spacy benepar "transformers<4.47"` + model downloads).

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
  `{i (0-based within sentence), t, lemma, pos, tag, dep, head(text)}`.
- `analyze(text, sentence_index=0)`:
  1. `nlp = load_models()`; `doc = nlp(text)`,
  2. segments `doc.sents`; **clamps** `sentence_index` into range; the target
     sentence is `sents[idx]` (multi-sentence policy: exactly one sentence
     analyzed per request, deterministically selectable),
  3. `parse_string = target._.parse_string`,
  4. `parse_parse_string` → `NodeBuilder.build(tagged, len(target))`,
  5. attaches `lemma` to every leaf from the token metadata,
  6. includes the full segmentation `sentences = [{ordinal, start, end,
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
- `IRREGULAR_VBN` — 70+ irregular past-participles (be→been, eat→eaten…).

### 10.2 Morphological helpers

- `_preserve_case(source, word)` — mirrors leading capitalization.
- `_base_form(leaf)` — `lemma` (or surface) lower-cased.
- `_plural_noun(word)` — irregular table → `s/x/z/ch/sh`→`+es` →
  consonant+y→`+ies` → `+s`.
- `_singular_noun(leaf)` — spaCy lemma (already the citation form).
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
    "tokens": [ { "i", "t", "lemma", "pos", "tag", "dep", "head" } ],
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
  }
}
```

`explainers.basic` (line-by-line): Input · benepar parse string · token stream ·
matrix counts (`N validated · M violated · K unrated`) · `Verdict: VALID/INVALID`
· explanation · determinism note.
`status` ∈ `valid|error|unlisted`; `constraint` is a `C-*` id.

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
- `main()` returns **exit 1 if any regression or any unrated edge type**, else 0.
  Run via `python3 scripts/audit_rules.py` or `npm run audit`.
  Current green state: 99 sentences, 888 edges, 0 distinct+unrated, 0
  regressions, 0 unrated.

---

## 13. Runtime configuration & verification

- Server: `python3 server/app.py` (or `npm run serve`); port 8000
  (override `SYNTUTOR_PORT`), host 127.0.0.1 (override `SYNTUTOR_HOST`).
- Health: `curl -s http://127.0.0.1:8000/api/health`.
- Parse: `curl -s -X POST http://127.0.0.1:8000/api/parse -H 'Content-Type:
  application/json' -d '{"text":"The boys runs."}'`.
- Static assets are read from disk **per request** (served with `no-store`), so
  JS/CSS/index edits show up on a hard refresh; **Python changes require a
  server restart**.
- Model pin: `transformers<4.47` (benepar's retokenizer relies on
  `T5Tokenizer.build_inputs_with_special_tokens`).
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