# SynTutor Handoff — Combined Generator + Builder

Date: 2026-11-17  
Branch: `feat/combined-builder-generator`  
Base commit: `6ffe63e` (`builder-menu`)  
Working tree: **dirty** — combined-mode and tree-text changes are uncommitted  
Remote: `origin/feat/combined-builder-generator` is at `6ffe63e`; local is ahead with uncommitted work

This handoff accompanies the exported Kilo Code conversation. Treat the repository as the source of truth; inspect `git status`, the current branch, and the diffs before changing anything.

## Provider

Continue using the already configured **Token Harbor** provider in this Kilo Code installation. No provider, credential, or model configuration was changed in this work.

## What this branch is for

Combine the **Syntax Generator** and **Syntax Builder** into one page and one canvas so the learner can:

1. Generate a tree from a sentence.
2. Switch the same canvas into editable Builder mode.
3. Edit the generated tree.
4. Switch back to Generator mode.
5. See the normalized built tree on the generator canvas and as text below the canvas.

Default mode is **Syntax Generator**; the page starts in generator mode.

## Current uncommitted implementation

### Mode toggle

- `#exploreBuilderBtn` is now the mode toggle, inside the canvas at the bottom-right.
- Generator mode label: **“Syntax Builder mode”**.
- Builder mode label: **“Syntax generator mode”**.
- Clicking toggles between `enterCombinedBuilderMode()` and `exitCombinedBuilderMode()`.
- `syncCanvasModeButton()` controls label and visibility.
- The button is visible in the generator/combined page, hidden in lessons/quizzes and in the standalone Builder sidebar view.

Key functions in `web/js/main.js`:

- `enterCombinedBuilderMode()`
- `exitCombinedBuilderMode()`
- `toggleCombinedCanvasMode()`
- `syncCanvasModeButton()`

Implementation detail: while combined Builder mode is active, `workspaceView` is set to `'builder'` so all existing Grammar Tutor input/blur/live-reparse guards skip analysis. The sidebar highlight is then forced back to `'tutor'` with `setActiveNav('tutor')`.

### Tree transfer

Generator to Builder:

- If the canonical tree is on screen, `exploreTreeFor(payload)` supplies its canonical envelope and `openBuilderView({ canonicalTree })` imports it.
- Otherwise the visibly displayed parser tree is imported through `fromDisplayTree(tree.display)`.
- If there is no tree, an empty builder opens.

Builder to Generator:

- `builderDisplayTree()` in `web/js/syntax-builder-ui.js` normalizes layout, exports `toTree(state.model)`, and clears leaf `type` values so the generator does not print the internal `"word"` tag.
- `closeBuilderView()` restores the generator canvas.
- The renderer is set to the built tree with `renderer.setInteractive(false)`; no analysis payload exists for edited structures, so XAI selection is intentionally disabled until the sentence is analyzed again.
- The input value is replaced with the built tree’s leaf surfaces (orphan words excluded).
- `lastBuiltTree` and `combinedTreeSource` preserve builder edits across repeated mode switches.
- `teardownWorkspace()` resets combined state, last built tree, and hides the tree-text panel.

### Orphan handling

- `toTree(model)` exports only the connected root component.
- A node added in Builder but never connected to the chosen root is omitted when switching to Generator.
- Re-entering Builder imports the exported tree, so the orphan is gone from the builder model too.
- If several disconnected candidate roots exist, `toTree`/`guessRoot` picks an `S` root if present, otherwise the first phrase root.

### Input box behavior

- Generator mode: normal generation behavior; after a built tree returns, the input is locked until the user clicks to edit.
- Builder mode: `openBuilderView()` makes the input editable and mirrors it to canvas words. Typing updates the canvas through the existing `onBuilderInput`/`syncInputToCanvas` path.

### Clear button

- Added `<button data-builder-clear>` to `#builderToolbar` after `Fit` in `web/index.html`.
- `wireBuilderToolbar()` now wires `querySelectorAll('[data-builder-clear]')`, so both the toolbar button and the legacy top-left button work.
- In combined Builder mode the top-left Clear (`#builderClearTop`) is hidden; the toolbar Clear is visible.
- In the standalone Builder sidebar view the old behavior remains.

### Instructions

- `setCanvasHint()` is used in both modes.
- `body.combined-modes .builder-hint` moves the hint to the bottom-left (CSS in `web/css/style.css`).
- Generator hint: “Syntax Generator mode — click a node for its explanation, or switch to Syntax Builder mode to edit this tree.”
- Builder hint: “Syntax Builder mode — click the canvas to add words and drag a connector dot to link boxes.”
- Hints are set on init, on mode switches, and when returning to the Tutor workspace.

### Nodes palette

Existing combined-page palette work is on this branch and must be preserved:

- Top-left `#builderPalette`, draggable by its header.
- Search labels; Hide button; reappears when the canvas is clicked.
- Node rows: `[S  Sentence  ?]`.
- `?` shows an immediate custom tooltip “View in lessons”.
- Clicking `?` opens the lessons page for the category’s introduction chapter, e.g. `NP → #lesson/br-02/concepts`.
- Labels without a mapped chapter get a disabled `?`.
- Palette CSS starts at `top: 10px`; Clear has moved out of that corner, so there is no overlap.

### Tree text below the canvas

- Added `#canvasTreeText` and `#canvasTreeTextBody` in `web/index.html`, directly below `.canvas-stage` inside `.canvas-wrap`.
- Open `<details>` panel titled **“View tree as text”**.
- `treeAsText(tree)` in `web/js/main.js` prints indented labels/words, including canonical features and gap/empty markers where present.
- Updates:
  - After generator renders (`syncExploreBuilder`).
  - On Builder mutations through the `syntutor:builder-change` custom event.
  - After node moves on mouse-up.
  - On entering/exiting combined mode.
- Hidden in lessons/quizzes, where lesson tree-text already exists.
- Placeholder is `No tree yet.`

## Files modified in the current working tree

- `web/index.html`
  - mode button label
  - toolbar Clear
  - tree-text panel
- `web/css/style.css`
  - combined-mode hint positioning
  - tree-text panel styling
  - palette/combined-mode refinements from the palette task
- `web/js/main.js`
  - combined mode state/functions
  - transfer and normalization
  - tree-text rendering
  - input/mode synchronization
- `web/js/syntax-builder-ui.js`
  - `builderDisplayTree()`
  - `builderTextTree()`
  - export `showBuilderPalette()`
  - builder-change event dispatch
  - executable Clear wiring for both buttons

Current diff stat at handoff time:

```
web/css/style.css           | 39 +++++++++
web/index.html              |  7 +-
web/js/main.js              | 203 ++++++++++++++++++++++++++++++++++++++++++-----
web/js/syntax-builder-ui.js | 50 ++++++++++++++++++++++++-
4 files changed, 265 insertions(+), 34 deletions(-)
```

## Verification performed

- `node scripts/test_builder_core.js` passes:
  `PASS: 10 canonical lesson round trips; profile palettes, gap/movement/empty nodes, cycle/terminal guards, undo/redo branches, identity recovery, corrupt/unavailable storage and safe import.`
- `node --check` passes for modified JS files.
- `node scripts/build.js` succeeds and rebuilds `dist/`.
- Browser probe using a stubbed generator payload for `The boy walks` confirmed:
  - mode button starts as “Syntax Builder mode”
  - builder canvas opens with the generated `S → NP(The boy), VP(walks)` tree
  - palette is visible; toolbar is `+ − Fit Clear`
  - top-left Clear is hidden
  - input reads `The boy walks`
  - adding an orphan palette node increases the model to 7 nodes
  - returning to generator shows the tree and sentence
  - re-entering builder has 6 nodes; the orphan is gone
  - generator/builder/post-exit tree text all show:
    ```
    S
      NP
        The
        boy
      VP
        walks
    ```
  - mode hints switch and the hint is at the bottom-left
  - no page errors

## Known limitations / risks

1. **No XAI on built trees in generator mode.** Edited trees have no server payload, so the generator canvas is non-interactive until analysis is rerun. Do not claim per-node explanations for a builder-exported tree.
2. **Multiple disconnected components.** Export keeps one connected root component and drops the rest. If the learner expects two separate trees, that is not supported.
3. **Workspace switching.** While combined Builder mode is active, `workspaceView` is `'builder'`; clicking another sidebar destination exits/tears down the combined page. Re-entering via the mode button restores what is still in `lastBuiltTree` only while the combined state survives.
4. **Mode button visibility.** It is intentionally hidden in lessons/quizzes and in the standalone Builder sidebar. If the app is opened directly in a non-Tutor view, the button may stay hidden until the Tutor workspace is shown.
5. **Stale browser tests.** `scripts/test_foundations_preview_browser.py` has a pre-existing stale `1 / 12 lessons` expectation (current course has 31 lessons), and `scripts/test_generator_canvas_browser.py` fails at a non-existent “English variety” control. These are not caused by combined mode; do not “fix” them by weakening assertions without checking the intended UI.
6. **Uncommitted work.** The combined mode and tree-text changes are not committed. Do not overwrite them or switch branches without preserving the diff.

## Recommended next steps

1. Review the uncommitted diff on `feat/combined-builder-generator`.
2. Run the browser probe or add a focused automated test for:
   - default mode and button visibility
   - generator → builder tree transfer
   - builder → generator normalization and orphan removal
   - input-box mode switching
   - Tree text panel updates
3. Commit the combined-mode work with a focused message after verification; push only to `feat/combined-builder-generator`.
4. Optional follow-ups:
   - Keep the combined page alive when sidebar destinations are clicked, or explicitly exit with a confirmation.
   - Preserve canonical ids/display labels through builder edits where possible.
   - Add XAI for edited learner trees by producing a learner envelope and requesting evidence (only if source/validation requirements allow).
   - Add a “fit”/scrollbar layout for very tall trees under the new text panel.
5. Do not merge into `main` without approval.

## Useful commands

```bash
git status -sb
git diff --stat
git diff -- web/js/main.js web/js/syntax-builder-ui.js
node --check web/js/main.js
node --check web/js/syntax-builder-ui.js
node scripts/test_builder_core.js
node scripts/build.js
```

The repository is the authoritative record; this file is only a handoff summary.
