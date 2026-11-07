// Syntax Builder view: a free-form canvas node editor for assembling syntax
// trees by hand. It is shown as a sidebar destination (like Achievements) and
// also drives the Matrix Quiz's "rebuild the tree" questions.
//
// Controls:
//   double-click empty canvas -> bare inline text box; type words, Enter drops
//     them as movable word boxes (no popup, no chrome)
//   right-click empty canvas  -> compact menu of phrase labels; pick one to drop
//     a phrase box (NP, VP, S, ...)
//   drag a phrase's connector dot -> a rubber-band link; release on a word or
//     another phrase to attach it as a child
//   drag a box body           -> move it
//   double-click a box        -> edit its word text / relabel the phrase
//   Delete/Backspace          -> remove the selected box
//   drag empty space          -> pan the canvas   wheel -> zoom
//   right-click (click)       -> add a node menu
//   right-click (hold) + drag -> marquee-select multiple nodes

import {
  POS_TYPES, PHRASE_NODE_TYPES, NODE_TYPE_GROUPS, NODE,
  createModel, addWordsFromText, addPhrase, moveNode, setType,
  removeNode, connect, canConnect, disconnect,
  dotOf, dotHit, nodeHit, endpointOf, endpointHit, toTree, compareTrees, leavesOf, leafText,
  seedWords, leavesWithTags, childrenOf, getSentenceFromLeaves as sentenceFromLeaves,
} from './syntax-builder.js';
import { renderNodeDetail, renderDiagnostic, clearOverlay } from './ui.js';

const WORD_FONT = '500 15px Inter, system-ui, sans-serif';
const TAG_FONT = '600 10px Inter, system-ui, sans-serif';
const PHRASE_FONT = '600 16px Inter, system-ui, sans-serif';
const NODE_H = 34;

// The upper-right input box shows one of two prompts: the Grammar Tutor's
// while the workspace analyses text, and the builder's while the canvas owns
// the words.
const TUTOR_PLACEHOLDER = 'Click the panel to write a sentence. SynTutor builds its syntax tree and analysis automatically.';
const BUILDER_PLACEHOLDER = 'Words typed on the canvas will appear here...';

// The affordance hints that float in the upper-left of the canvas. The
// practice stage invites the learner to build; the quiz stage asks for a
// tree that matches SynTutor's parse.
const PRACTICE_HINT = 'Right-click to add a phrase · drag a dot to connect · grab a link end to re-route or delete';
const QUIZ_HINT = 'Build the tree, then check it against SynTutor’s parse';

// The canvas hint (top-left): a static line telling the learner what the
// stage expects, replaced by the live validation message while a check runs.
// Exported so the lesson can drive it per stage.
export function setCanvasHint(msg, kind) {
  const hint = document.getElementById('builderHint');
  if (!hint) return;
  if (!msg) {
    hint.textContent = '';
    hint.hidden = true;
    return;
  }
  hint.textContent = msg;
  const cls = ['builder-hint'];
  if (kind) cls.push(`builder-hint-${kind}`);
  if (hint.classList.contains('with-actions')) cls.push('with-actions');
  hint.className = cls.join(' ');
  hint.hidden = false;
}

// Whether the hint sits below the floating action cluster (Clear / Build
// tree) instead of on top of it.
export function setHintBelowActions(visible) {
  const hint = document.getElementById('builderHint');
  if (!hint) return;
  hint.classList.toggle('with-actions', Boolean(visible));
}


// Colours mirror the grammar-tutor tree renderer so the builder looks identical.
function themeColors() {
  const dark = document.documentElement.getAttribute('data-theme') === 'dark';
  return {
    text: dark ? '#f1f5f9' : '#2b2440',
    accent: dark ? '#a78bfa' : '#6d5ae6',
    edge: dark ? '#94a3b8' : '#000000',
    tag: dark ? '#94a3b8' : '#77708f',
    selected: '#eab308',
    error: '#d64545',
  };
}

const state = {
  model: createModel(),
  view: { ox: 60, oy: 60, scale: 1 },
  drag: null,
  pan: null,
  link: null,
  marquee: null,
  hover: null,
  hoverTarget: null,
  hoverEndpoint: null,
  selection: new Set(),
  reject: null,
  challenge: null,
  onStatus: () => {},
  onComplete: null,
  setWorkspaceView: null,
  solved: false,
  treeCorrect: false,
  snapped: false,
  snappedLayout: null,
  // The static hint of the current stage; a live check message replaces it
  // for a few seconds and then gives it back.
  hintBase: '',
  hintTimer: 0,
  // Per-node validation errors produced by the last Build tree check:
  // id -> detail record (same shape as the tutor's payload.node_details[id]).
  nodeErrors: new Map(),
  root: null,
  canvas: null,
  ctx: null,
  editor: null,
  menu: null,
  dpr: 1,
  frame: 0,
  rightHoldTimer: null,
  holdingRight: false,
  rightDownStart: null,
};

export function initSyntaxBuilder({ onStatusChange, setWorkspaceView } = {}) {
  state.onStatus = onStatusChange || (() => {});
  state.setWorkspaceView = setWorkspaceView || null;
}

export function builderModel() {
  return state.model;
}

// ---------------------------------------------------------------------------
// Canvas ↔ input panel
// ---------------------------------------------------------------------------
// The builder canvas and the upper-right input box are one surface: the words
// the learner places on the canvas ARE the sentence in the input panel. The
// panel is a mirror, not a second editing surface — it stays locked and is
// refreshed from the canvas on every word mutation.

// The sentence the canvas currently spells out.
export function getSentenceFromLeaves() {
  return sentenceFromLeaves(state.model);
}

// Mirror the canvas into the input panel. The update is programmatic, so it
// must never start the Grammar Tutor's analysis pipeline: the 'input' event
// only refreshes the highlight overlay and the × affordance (main.js's
// listener never runs the pipeline — the blur handler does, and it is
// disabled while the builder owns the workspace).
function syncCanvasToInput() {
  const sentence = getSentenceFromLeaves();
  const input = document.getElementById('inputText');
  if (!input) return sentence;
  if (input.value === sentence) return sentence;
  input.value = sentence;
  const highlights = document.getElementById('inputHighlights');
  if (highlights) highlights.textContent = sentence;
  input.dispatchEvent(new Event('input', { bubbles: true }));
  return sentence;
}

// The input panel's prompt follows the active mode. It lives on the
// textarea only — the highlight overlay never renders a prompt of its own.
function setInputPlaceholder(text) {
  const input = document.getElementById('inputText');
  if (input) input.placeholder = text;
}

// Empty the canvas — and with it the sentence in the input panel.
export function clearBuilder() {
  newModel();
  draw();
  syncCanvasToInput();
}

// ---------------------------------------------------------------------------
// View lifecycle
// ---------------------------------------------------------------------------

export function openBuilderView(opts = {}) {
  const bar = document.getElementById('canvasControls');
  const canvas = document.getElementById('builderCanvas');
  const treeCanvas = document.getElementById('treeCanvas');
  if (!bar || !canvas) return;
  ensureWired();
  canvas.hidden = false;
  if (treeCanvas) treeCanvas.hidden = true;
  document.getElementById('emptyTreeState')?.classList.add('hidden');
  // The shared canvas overlay (e.g. "No analyzable sentence" from the parser)
  // belongs to the main tree view, not the builder — clear it so it never
  // bleeds into this page.
  clearOverlay();
  // Lessons and quizzes build in place on this canvas; only the standalone
  // Syntax Builder (no challenge) highlights its own sidebar tab, unless the
  // caller asks for a specific tab via `opts.sidebarView`.
  const sidebarView = opts.sidebarView || (opts.challenge ? null : 'builder');
  if (sidebarView) markSidebar(sidebarView);
  state.challenge = opts.challenge || null;
  state.onComplete = opts.onComplete || null;
  state.solved = false;
  if (opts.reset) newModel();
  if (opts.model) {
    // A caller may supply a fully seeded model (e.g. a deliberately broken
    // tree for a repair task). Reset every transient editor state so nothing
    // from the previous exercise survives the swap.
    state.model = opts.model;
    resetTransientState();
  }
  if (state.challenge && !opts.model) seedForChallenge(state.challenge);
  // A fresh exercise starts from a known viewport; a previous pan/zoom must
  // not leave the new word row off-screen.
  if (opts.reset || opts.model) state.view = { ox: 60, oy: 60, scale: 1 };

    // Two builder stages live inside a lesson: the practice stage (Step 2) and
    // the quiz stage (Step 3). The lesson's right panel owns the actions in
    // both, so the canvas carries no second way to submit a check.
    const practice = Boolean(state.challenge) && Boolean(opts.practice);
    const quiz = Boolean(state.challenge) && Boolean(opts.quiz);
    const interactive = practice || quiz;
    bar.hidden = Boolean(state.challenge) && !interactive;
    // The "Show model tree" escape hatch only exists for lesson practice; it is
    // wired by tree-quiz.js and must never appear in the standalone builder.
    const modelBtn = document.getElementById('builderModel');
    if (modelBtn) modelBtn.hidden = !practice;
  // The builder owns the input panel now: it mirrors the canvas, so it gets
  // the builder's prompt and stays read-only.
  document.body.classList.add('builder-active');
  document.body.classList.remove('lesson-model');
  setInputPlaceholder(BUILDER_PLACEHOLDER);
  const target = document.getElementById('builderTarget');
  const clear = document.getElementById('builderClear');
  const snap = document.getElementById('builderSnap');
  const check = document.getElementById('builderCheck');
  const next = document.getElementById('builderNext');
  const done = document.getElementById('builderDone');
  if (!state.challenge) {
    // Standalone Syntax Builder: only the action buttons (Clear / Build tree /
    // Done) float over the canvas — no instructions, no target sentence.
    if (target) target.hidden = true;
    if (check) check.hidden = true;
    if (next) next.hidden = true;
    if (done) done.hidden = false;
    state.hintBase = '';
    setCanvasHint('');
  } else if (interactive) {
    // Lesson practice and the lesson quiz keep the affordance hint, but the
    // actions live in the lesson's right panel: the canvas never offers a
    // second way to submit a check.
    state.hintBase = opts.hint || (practice ? PRACTICE_HINT : QUIZ_HINT);
    setCanvasHint(state.hintBase);
    if (target) target.hidden = true;
    if (check) check.hidden = true;
    if (next) next.hidden = true;
    if (done) done.hidden = true;
    if (practice) {
      // Guided practice is a walkthrough: the canvas stays clean, and the
      // step pager in the right panel drives it.
      bar.hidden = true;
    } else {
      // The quiz keeps the two harmless canvas actions — clear the canvas,
      // reset the layout — and nothing else.
      bar.hidden = false;
      if (clear) clear.hidden = false;
      if (snap) snap.hidden = false;
    }
  } else {
    // A standalone quiz shows no builder chrome at all: the action buttons
    // and the practice hint both stay off the canvas.
    state.hintBase = '';
    setCanvasHint('');
  }
  hideToast();
  // The hint steps below the action cluster whenever that cluster is up.
  setHintBelowActions(!bar.hidden);
  resize();
  if (opts.model) {
    const words = Object.values(state.model.nodes)
      .filter((n) => n.kind === NODE.WORD)
      .sort((a, b) => a.x - b.x);
    if (words.length) measureWords(words);
    applyTreeLayout({ fit: true });
    syncCanvasToInput();
  }
  canvas.focus();
  explainSelected();
  state.treeCorrect = treeIsComplete();
  draw();
}

const HINTS = {
  tokens: 'Double-click the canvas and type the sentence. SynTutor must split it into exactly these words.',
  tags: 'Right-click each word to give it the part-of-speech tag SynTutor would assign.',
  phrases: 'Words and tags are given. Add phrase boxes (right-click) and drag their dots to connect the words.',
  full: 'Build the whole tree: type the words, then add and connect the phrase boxes.',
};

// Pre-place the sentence's word boxes so the learner focuses on building the
// phrase structure — the sentence is given in the input box; the tree is the
// exercise.
function seedForChallenge(challenge) {
  const leaves = challenge.gold || [];
  if (!leaves.length) return;
  if (challenge.kind === 'tokens') return;
  const withTags = challenge.kind !== 'tags';
  // Keep the seeded word row on screen on short (mobile) canvases instead of
  // parking it below the fold at the desktop height.
  const canvasH = state.canvas?.parentElement?.clientHeight || 480;
  const rowY = Math.max(140, Math.min(360, canvasH - 120));
  const words = seedWords(state.model, leaves, 60, rowY, withTags);
  measureWords(words);
}

function measureWords(nodes) {
  for (const n of nodes) n.w = measureWord(n.text);
  // Re-lay them out now that widths are known.
  let cursor = 60;
  for (const n of nodes) {
    n.x = cursor;
    cursor += n.w + 12;
  }
}

export function closeBuilderView() {
  const bar = document.getElementById('canvasControls');
  const canvas = document.getElementById('builderCanvas');
  const treeCanvas = document.getElementById('treeCanvas');
  if (!bar) return;
  closeEditor();
  closeMenu();
  bar.hidden = true;
  // The practice hint floats on its own (outside the action cluster), so it
  // has to be dismissed with the cluster.
  const hint = document.getElementById('builderHint');
  if (hint) hint.hidden = true;
  state.hintBase = '';
  window.clearTimeout(state.hintTimer);
  state.hintTimer = 0;
  if (canvas) canvas.hidden = true;
  if (treeCanvas) treeCanvas.hidden = false;
  // The Grammar Tutor takes the input panel back, with its own prompt.
  document.body.classList.remove('builder-active');
  setInputPlaceholder(TUTOR_PLACEHOLDER);
  state.challenge = null;
  state.onComplete = null;
  onBuilderClose();
}

let onBuilderClose = () => {};
export function setBuilderCloseHandler(fn) { onBuilderClose = fn || (() => {}); }

export function isBuilderOpen() {
  const bar = document.getElementById('canvasControls');
  return !!bar && !bar.hidden;
}

export function setChallenge(challenge, onComplete) {
  state.challenge = challenge || null;
  state.onComplete = onComplete || null;
  newModel();
  openBuilderView({ challenge, onComplete });
}

// Drop every transient interaction (selection, drag/link/marquee, hover, a
// rejected-connection flash, an open menu/editor) so a new model or a supplied
// repair model starts clean.
function resetTransientState() {
  state.selection.clear();
  state.drag = null;
  state.pan = null;
  state.link = null;
  state.marquee = null;
  state.hover = null;
  state.hoverTarget = null;
  state.hoverEndpoint = null;
  state.reject = null;
  state.snapped = false;
  state.snappedLayout = null;
  state.nodeErrors = new Map();
  if (state.rightHoldTimer) { clearTimeout(state.rightHoldTimer); state.rightHoldTimer = null; }
  state.holdingRight = false;
  state.rightDownStart = null;
  closeMenu();
  closeEditor();
  const target = document.getElementById('builderTarget');
  if (target) target.classList.remove('builder-target-ok');
}

export function newModel() {
  state.model = createModel();
  resetTransientState();
}

// The rail highlight is owned by main.js (setActiveNav): the builder only
// reports which module it is showing for, so exactly one destination stays
// active.
function markSidebar(view) {
  if (view) state.setWorkspaceView?.(view);
}

// ---------------------------------------------------------------------------
// Wiring (once)
// ---------------------------------------------------------------------------
let wired = false;
function ensureWired() {
  if (wired) return;
  wired = true;
  state.canvas = document.getElementById('builderCanvas');
  state.ctx = state.canvas.getContext('2d');
  document.getElementById('builderClear')?.addEventListener('click', clearBuilder);
  document.getElementById('builderSnap')?.addEventListener('click', buildTree);
  document.getElementById('builderDone')?.addEventListener('click', () => closeBuilderView());
  document.getElementById('builderCheck')?.addEventListener('click', checkTree);
  document.getElementById('builderNext')?.addEventListener('click', () => {
    const cb = state.challenge && state.challenge.onNext;
    if (typeof cb === 'function') cb();
  });
  wireCanvas(state.canvas);
  window.addEventListener('resize', () => {
    if (isBuilderOpen()) {
      resize();
      draw();
    }
  });
}

function resize() {
  const canvas = state.canvas;
  const wrap = canvas.parentElement;
  const dpr = window.devicePixelRatio || 1;
  state.dpr = dpr;
  const w = wrap.clientWidth;
  const h = wrap.clientHeight;
  canvas.width = Math.round(w * dpr);
  canvas.height = Math.round(h * dpr);
  canvas.style.width = `${w}px`;
  canvas.style.height = `${h}px`;
}

// ---------------------------------------------------------------------------
// Coordinate mapping
// ---------------------------------------------------------------------------

function toWorld(sx, sy) {
  const { ox, oy, scale } = state.view;
  return { x: (sx - ox) / scale, y: (sy - oy) / scale };
}
function toScreen(wx, wy) {
  const { ox, oy, scale } = state.view;
  return { x: wx * scale + ox, y: wy * scale + oy };
}
function eventPos(e) {
  const rect = state.canvas.getBoundingClientRect();
  return { sx: e.clientX - rect.left, sy: e.clientY - rect.top };
}

// ---------------------------------------------------------------------------
// Input wiring
// ---------------------------------------------------------------------------

function wireCanvas(canvas) {
  canvas.addEventListener('mousedown', onMouseDown);
  canvas.addEventListener('mousemove', onMouseMove);
  window.addEventListener('mouseup', onMouseUp);
  canvas.addEventListener('dblclick', onDoubleClick);
  canvas.addEventListener('contextmenu', onContextMenu);
  canvas.addEventListener('wheel', onWheel, { passive: false });
  canvas.addEventListener('keydown', onKeyDown);
}

function onMouseDown(e) {
  const { sx, sy } = eventPos(e);
  const w = toWorld(sx, sy);

  // Right-click: short click opens the add-node menu; hold starts multi-selection.
  if (e.button === 2) {
    if (state.rightHoldTimer) clearTimeout(state.rightHoldTimer);
    state.rightDownStart = { sx, sy, clientX: e.clientX, clientY: e.clientY };
    state.holdingRight = false;
    state.rightHoldTimer = setTimeout(() => {
      state.holdingRight = true;
      // On hold, start marquee selection from this point (treat like left-drag marquee)
      closeMenu();
      state.marquee = { x0: w.x, y0: w.y, x1: w.x, y1: w.y, base: new Set() };
      draw();
    }, 200); // 200ms hold threshold
    return;
  }

  if (e.button === 0) {
    const dot = dotHit(state.model, w.x, w.y);
    if (dot) {
      state.link = { parentId: dot.id, childId: null, free: 'child', x: w.x, y: w.y };
      closeMenu();
      return;
    }
    const endpoint = endpointHit(state.model, w.x, w.y);
    if (endpoint) {
      const oldParent = endpoint.parent;
      endpoint.parent = null;
      state.link = {
        parentId: null, childId: endpoint.id, free: 'parent',
        originalParent: oldParent, x: w.x, y: w.y,
      };
      selectOnly(endpoint.id);
      closeMenu();
      draw();
      explainSelected();
      return;
    }
    const node = nodeHit(state.model, w.x, w.y);
    if (node) {
      const additive = e.shiftKey || e.metaKey || e.ctrlKey;
      if (additive) {
        toggleSelect(node.id);
        draw();
        explainSelected();
        return;
      }
      if (!state.selection.has(node.id)) selectOnly(node.id);
      // Drag every selected box together.
      const ids = [...state.selection];
      const origins = {};
      for (const id of ids) {
        const n = state.model.nodes[id];
        if (n) origins[id] = { x: n.x, y: n.y };
      }
      state.drag = { ids, origins, start: { x: w.x, y: w.y }, moved: false };
      canvas_focus();
      draw();
      explainSelected();
      return;
    }
    // Empty space: hold left-click and drag to move within the canvas (pan).
    closeMenu();
    clearSelection();
    state.pan = { sx, sy, ox: state.view.ox, oy: state.view.oy };
    state.canvas.style.cursor = 'grabbing';
    draw();
    explainSelected();
  }
}

function isSelected(id) {
  return state.selection.has(id);
}
function selectOnly(id) {
  state.selection.clear();
  if (id != null) state.selection.add(id);
}
function toggleSelect(id) {
  if (state.selection.has(id)) state.selection.delete(id);
  else state.selection.add(id);
}
function clearSelection() {
  state.selection.clear();
}
function selectedNodes() {
  return [...state.selection]
    .map((id) => state.model.nodes[id])
    .filter(Boolean);
}
function primarySelected() {
  const ids = [...state.selection];
  return ids.length ? state.model.nodes[ids[ids.length - 1]] : null;
}

function canvas_focus() {
  state.canvas?.focus?.();
}

function onMouseMove(e) {
  const { sx, sy } = eventPos(e);
  const w = toWorld(sx, sy);

  if (state.drag) {
    const dx = w.x - state.drag.start.x;
    const dy = w.y - state.drag.start.y;
    if (dx || dy) state.drag.moved = true;
    for (const id of state.drag.ids) {
      const o = state.drag.origins[id];
      if (o) moveNode(state.model, id, o.x + dx, o.y + dy);
    }
    draw();
    return;
  }
  if (state.marquee) {
    state.marquee.x1 = w.x;
    state.marquee.y1 = w.y;
    state.canvas.style.cursor = 'crosshair';
    draw();
    return;
  }
  if (state.pan) {
    state.view.ox = state.pan.ox + (sx - state.pan.sx);
    state.view.oy = state.pan.oy + (sy - state.pan.sy);
    state.canvas.style.cursor = 'grabbing';
    draw();
    return;
  }
  if (state.link) {
    state.link.x = w.x;
    state.link.y = w.y;
    if (state.link.free === 'parent') {
      const hit = nodeHit(state.model, w.x, w.y);
      state.hoverTarget = (hit && canConnect(state.model, hit.id, state.link.childId)) ? hit.id : null;
    } else {
      const tgt = nodeHit(state.model, w.x, w.y);
      state.hoverTarget = (tgt && canConnect(state.model, state.link.parentId, tgt.id)) ? tgt.id : null;
    }
    draw();
    return;
  }
  // hover feedback
  const node = nodeHit(state.model, w.x, w.y);
  const id = node ? node.id : null;
  const epNode = endpointHit(state.model, w.x, w.y);
  const epId = epNode ? epNode.id : (node && node.parent ? node.id : null);
  if (id !== state.hover || epId !== state.hoverEndpoint) {
    state.hover = id;
    state.hoverEndpoint = epId;
    state.canvas.style.cursor = epNode ? 'grab'
      : node ? (node.kind === NODE.PHRASE ? 'grab' : 'pointer') : 'default';
    draw();
  }
}

function onMouseUp(e) {
  if (e.button === 2) {
    if (state.rightHoldTimer) {
      clearTimeout(state.rightHoldTimer);
      state.rightHoldTimer = null;
    }
    const start = state.rightDownStart;
    state.rightDownStart = null;
    if (state.holdingRight) {
      const m = state.marquee;
      const moved = m && (Math.abs(m.x1 - m.x0) > 3 || Math.abs(m.y1 - m.y0) > 3);
      if (moved) {
        const { x0, y0, x1, y1 } = m;
        const minX = Math.min(x0, x1), maxX = Math.max(x0, x1);
        const minY = Math.min(y0, y1), maxY = Math.max(y0, y1);
        const next = new Set();
        for (const n of Object.values(state.model.nodes)) {
          const cx = n.x + n.w / 2;
          const cy = n.y + n.h / 2;
          if (cx >= minX && cx <= maxX && cy >= minY && cy <= maxY) next.add(n.id);
        }
        state.selection = next;
        explainSelected();
      } else {
        // Held but never dragged: treat as a normal right-click on empty space.
        state.marquee = null;
        const { sx, sy } = eventPos(e);
        const w = toWorld(sx, sy);
        const node = nodeHit(state.model, w.x, w.y);
        openMenu(start ? start.clientX : e.clientX, start ? start.clientY : e.clientY, w, node);
      }
      state.marquee = null;
      state.holdingRight = false;
      state.canvas.style.cursor = '';
      draw();
      return;
    }
    // Quick right-click: open the add-node menu ourselves (contextmenu is
    // suppressed) so the menu only appears for a genuine click.
    const { sx, sy } = eventPos(e);
    const w = toWorld(sx, sy);
    const node = nodeHit(state.model, w.x, w.y);
    openMenu(start ? start.clientX : e.clientX, start ? start.clientY : e.clientY, w, node);
    return;
  }

  const { sx, sy } = eventPos(e);
  const w = toWorld(sx, sy);
  if (state.link) {
    if (state.link.free === 'parent') {
      const hit = nodeHit(state.model, w.x, w.y);
      if (hit && canConnect(state.model, hit.id, state.link.childId)) {
        connect(state.model, hit.id, state.link.childId);
        state.onStatus?.(`Connected “${nodeLabel(hit)}” → “${nodeLabel(state.model.nodes[state.link.childId])}”.`);
      } else {
        // Dropped on empty space (or an invalid target): the connection was
        // already detached on mouse-down, so it stays removed.
        state.onStatus?.('Connection removed.');
      }
    } else {
      const tgt = nodeHit(state.model, w.x, w.y);
      if (tgt && canConnect(state.model, state.link.parentId, tgt.id)) {
        connect(state.model, state.link.parentId, tgt.id);
      } else if (tgt) {
        // Rejected: a self-link or a cycle would break the tree.
        flashRejected(tgt.id);
        state.onStatus('That connection is not allowed.');
      }
    }
    state.link = null;
    state.hoverTarget = null;
    changed();
  }
  if (state.marquee) {
    const { x0, y0, x1, y1 } = state.marquee;
    const minX = Math.min(x0, x1), maxX = Math.max(x0, x1);
    const minY = Math.min(y0, y1), maxY = Math.max(y0, y1);
    const next = new Set();
    for (const n of Object.values(state.model.nodes)) {
      const cx = n.x + n.w / 2;
      const cy = n.y + n.h / 2;
      if (cx >= minX && cx <= maxX && cy >= minY && cy <= maxY) next.add(n.id);
    }
    state.selection = next;
    state.marquee = null;
    draw();
    explainSelected();
  }
  // A word dragged sideways can change the reading order, so the input panel
  // follows once the drag ends.
  const dragged = state.drag;
  state.drag = null;
  state.pan = null;
  state.canvas.style.cursor = '';
  if (dragged?.moved) syncCanvasToInput();
}

function nodeLabel(node) {
  if (!node) return '?';
  return node.kind === NODE.PHRASE ? node.type : (node.text || '…');
}

function flashRejected(id) {
  state.reject = { id, until: Date.now() + 900 };
  draw();
  setTimeout(() => {
    if (state.reject && state.reject.id === id && Date.now() >= state.reject.until) {
      state.reject = null;
      draw();
    }
  }, 950);
}

function onDoubleClick(e) {
  const { sx, sy } = eventPos(e);
  const w = toWorld(sx, sy);
  const node = nodeHit(state.model, w.x, w.y);
  if (node) {
    editNode(node, e.clientX, e.clientY);
  } else {
    openInlineEditor(w, e.clientX, e.clientY, '', (text) => {
      if (!text.trim()) return;
      const made = addWordsFromText(state.model, text, w.x, w.y);
      validateWords(made);
      changed();
    });
  }
}

// Ask SynTutor's own model which of these words are real. Invalid words are
// Words SynTutor doesn't recognise are still flagged visually, but they can
// now be connected like any other node.
async function validateWords(nodes) {
  const words = nodes.map((n) => n.text);
  let results = null;
  try {
    const res = await fetch('/api/words', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ words }),
    });
    if (res.ok) {
      const data = await res.json();
      results = data.results;
    }
  } catch {
    results = null;
  }
  if (!results) return;
  nodes.forEach((node, i) => {
    const info = results[i];
    if (!info) return;
    node.valid = info.valid !== false;
    node.suggestion = info.suggestion || null;
    node.tag = info.tag || null;
  });
  const bad = nodes.filter((n) => n.valid === false).map((n) => n.text);
  if (bad.length) {
    state.onStatus(`Not in SynTutor's model: ${bad.join(', ')} — fix or delete to connect them.`);
  }
  draw();
}

function onContextMenu(e) {
  // The builder owns the right-click interaction (click = add-node menu,
  // hold + drag = multi-select), so never show the browser's native menu.
  e.preventDefault();
}

function onWheel(e) {
  e.preventDefault();
  const { sx, sy } = eventPos(e);
  const before = toWorld(sx, sy);
  const factor = e.deltaY < 0 ? 1.12 : 1 / 1.12;
  state.view.scale = Math.min(2.5, Math.max(0.3, state.view.scale * factor));
  // keep the point under the cursor fixed
  const after = toWorld(sx, sy);
  state.view.ox += (after.x - before.x) * state.view.scale;
  state.view.oy += (after.y - before.y) * state.view.scale;
  draw();
}

function onKeyDown(e) {
  if (e.key === 'Escape') {
    closeMenu();
    closeEditor();
    // Cancel a re-route: put the connection back where it was.
    if (state.link && state.link.free === 'parent' && state.link.originalParent) {
      const child = state.model.nodes[state.link.childId];
      if (child) child.parent = state.link.originalParent;
    }
    state.link = null;
    state.drag = null;
    state.pan = null;
    state.marquee = null;
    if (state.rightHoldTimer) { clearTimeout(state.rightHoldTimer); state.rightHoldTimer = null; }
    state.holdingRight = false;
    state.rightDownStart = null;
    state.hoverTarget = null;
    state.canvas.style.cursor = '';
    draw();
    return;
  }
  if ((e.key === 'Delete' || e.key === 'Backspace') && state.selection.size > 0) {
    e.preventDefault();
    for (const id of [...state.selection]) removeNode(state.model, id);
    state.selection.clear();
    changed();
    explainSelected();
  }
}

// ---------------------------------------------------------------------------
// Inline (chrome-less) text editor
// ---------------------------------------------------------------------------

function openInlineEditor(world, clientX, clientY, initial, onCommit) {
  closeEditor();
  const input = document.createElement('input');
  input.className = 'builder-inline-input';
  input.value = initial || '';
  input.placeholder = 'type words…';
  input.style.left = `${clientX}px`;
  input.style.top = `${clientY}px`;
  document.body.appendChild(input);
  state.editor = input;
  const w = world;
  input.focus();
  input.select();
  input.addEventListener('keydown', (ev) => {
    if (ev.key === 'Enter') {
      ev.preventDefault();
      const text = input.value;
      closeEditor();
      onCommit(text, w);
    } else if (ev.key === 'Escape') {
      closeEditor();
    }
  });
  input.addEventListener('blur', () => closeEditor());
}

function editNode(node, clientX, clientY) {
  const world = { x: node.x, y: node.y };
  if (node.kind === NODE.WORD) {
    openInlineEditor(world, clientX, clientY, node.text, (text) => {
      node.text = text.trim();
      node.w = measureWord(node.text);
      validateWords([node]);
      changed();
      explainSelected();
    });
  } else {
    openInlineEditor(world, clientX, clientY, node.type, (text) => {
      const t = text.trim().toUpperCase();
      if (t) setType(state.model, node.id, t);
      changed();
      explainSelected();
    });
  }
}

function closeEditor() {
  const editor = state.editor;
  if (!editor) return;
  // Null first so a re-entrant `blur` handler can't remove the same node twice.
  state.editor = null;
  try {
    editor.remove();
  } catch {
    // The editor may already be detached from the DOM.
  }
}

// ---------------------------------------------------------------------------
// Right-click menu
// ---------------------------------------------------------------------------

function openMenu(clientX, clientY, world, node) {
  closeMenu();
  const menu = document.createElement('div');
  menu.className = 'builder-menu';

  const title = document.createElement('div');
  title.className = 'builder-menu-title';
  title.textContent = node
    ? (node.kind === NODE.PHRASE ? `Change “${node.type}” node` : `Change “${node.text}” tag`)
    : 'Add a node';
  menu.appendChild(title);

  const search = document.createElement('input');
  search.className = 'builder-menu-search';
  search.type = 'text';
  search.placeholder = 'Search labels…';
  menu.appendChild(search);

  const body = document.createElement('div');
  body.className = 'builder-menu-scroll';
  menu.appendChild(body);

  const phraseTypes = NODE_TYPE_GROUPS.flatMap((g) => g.types);
  const sections = (node && node.kind === NODE.WORD)
    ? [{ name: 'Word tags (POS)', types: POS_TYPES }]
    : [{ name: 'Phrases', types: phraseTypes }];

  const render = (filter = '') => {
    body.innerHTML = '';
    const f = filter.trim().toLowerCase();
    let shown = 0;
    for (const section of sections) {
      const types = section.types.filter((t) => t.toLowerCase().includes(f));
      if (!types.length) continue;
      const head = document.createElement('div');
      head.className = 'builder-menu-head';
      head.textContent = section.name;
      body.appendChild(head);
      const grid = document.createElement('div');
      grid.className = 'builder-menu-grid';
      for (const t of types) {
        grid.appendChild(menuItem(t, node, world));
        shown += 1;
      }
      body.appendChild(grid);
    }
    if (!shown) {
      const empty = document.createElement('div');
      empty.className = 'builder-menu-empty';
      empty.textContent = 'No matching label';
      body.appendChild(empty);
    }
  };
  render();
  search.addEventListener('input', () => render(search.value));

  if (node) {
    const del = document.createElement('button');
    del.type = 'button';
    del.className = 'builder-menu-delete';
    const selCount = state.selection.size;
    del.textContent = selCount > 1 && state.selection.has(node.id) ? `Delete ${selCount} nodes` : 'Delete node';
    del.addEventListener('click', (ev) => {
      ev.stopPropagation();
      if (selCount > 1 && state.selection.has(node.id)) {
        for (const id of [...state.selection]) removeNode(state.model, id);
        state.selection.clear();
      } else {
        removeNode(state.model, node.id);
        state.selection.delete(node.id);
      }
      closeMenu();
      changed();
      explainSelected();
    });
    menu.appendChild(del);
  }

  document.body.appendChild(menu);
  // Clamp inside the viewport.
  const rect = menu.getBoundingClientRect();
  const left = Math.min(clientX, window.innerWidth - rect.width - 8);
  const top = Math.min(clientY, window.innerHeight - rect.height - 8);
  menu.style.left = `${Math.max(8, left)}px`;
  menu.style.top = `${Math.max(8, top)}px`;

  state.menu = menu;
  search.focus();
  setTimeout(() => {
    document.addEventListener('mousedown', closeMenuOnOutside, { once: true });
  }, 0);
}

function menuItem(label, node, world) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'builder-menu-item';
  const isPhrase = PHRASE_NODE_TYPES.includes(label);
  if (isPhrase) btn.classList.add('is-phrase');
  btn.textContent = label;
  if (node && node.type === label) btn.classList.add('is-current');
  btn.addEventListener('click', (ev) => {
    ev.stopPropagation();
    if (node) {
      setType(state.model, node.id, label);
      if (node.kind === NODE.WORD) {
        node.tag = POS_TYPES.includes(label) ? label : node.tag;
      }
    } else if (isPhrase) {
      addPhrase(state.model, label, world.x - 28, world.y - 16);
    }
    closeMenu();
    changed();
    explainSelected();
  });
  return btn;
}

function closeMenuOnOutside(e) {
  if (state.menu && !state.menu.contains(e.target)) closeMenu();
}
function closeMenu() {
  if (state.menu) {
    state.menu.remove();
    state.menu = null;
  }
}

// ---------------------------------------------------------------------------
// XAI explanation panel — same card the Grammar Tutor shows for a tree node
// ---------------------------------------------------------------------------
// The tutor explains a sentence by rendering a card for the node you select.
// The builder shows the identical card for the selected box: what the phrase or
// tag is and how it reads. Content is read from the same tree_sheet.json the
// tutor and the tree quiz use, so the wording agrees everywhere.
const INFO = { phrase: null, pos: null };
let infoPromise = null;

function loadInfo() {
  if (infoPromise) return infoPromise;
  INFO.phrase = new Map();
  INFO.pos = new Map();
  infoPromise = fetch('/content/tree_sheet.json')
    .then((r) => (r.ok ? r.json() : null))
    .then((sheet) => {
      for (const stage of (sheet?.stages || [])) {
        if (stage.id === 2) for (const it of stage.items || []) INFO.pos.set(it.tag, it);
        if (stage.id === 3) for (const it of stage.items || []) INFO.phrase.set(it.tag, it);
      }
    })
    .catch(() => {});
  return infoPromise;
}

// Leaf surface text of a model node's subtree (the phrase's words).
function nodeLeafText(id) {
  const out = [];
  const walk = (nid) => {
    const children = childrenOf(state.model, nid);
    if (!children.length) {
      const n = state.model.nodes[nid];
      if (n) out.push(n.text);
      return;
    }
    for (const c of children) walk(c.id);
  };
  walk(id);
  return out.join(' ');
}

// Build a node-detail record shaped like the tutor's payload.node_details[id].
function describeNode(node) {
  // A Build-tree validation error takes priority so selecting a red node shows
  // the exact problem in the right-hand panel.
  const flagged = state.nodeErrors.get(node.id);
  if (flagged) return flagged;
  if (node.kind === NODE.PHRASE) {
    const info = INFO.phrase?.get(node.type);
    return {
      type: node.type,
      surface: nodeLeafText(node.id),
      status: 'valid',
      role: 'Phrase node',
      text: info ? `${info.name} — e.g. ${info.example}` : `A ${node.type} phrase.`,
    };
  }
  const tag = node.tag || null;
  if (node.valid === false) {
    return {
      type: tag || 'WORD',
      surface: node.text,
      status: 'error',
      role: 'Word',
      text: `\u201c${node.text}\u201d is not a word SynTutor's model knows.`,
      remediation: {
        violation: `\u201c${node.text}\u201d is not in SynTutor's vocabulary, so no tree can license it.`,
        suggested_fix: node.suggestion
          ? `Replace it with \u201c${node.suggestion}\u201d.`
          : 'Correct the spelling or delete the box.',
        alternative_fix: null,
      },
    };
  }
  const info = tag ? INFO.pos?.get(tag) : null;
  return {
    type: tag || 'WORD',
    surface: node.text,
    status: 'valid',
    role: 'Word',
    text: info ? `${info.name} — e.g. ${info.example}` : 'A word in the tree.',
  };
}

// Re-render the node inspector for the current selection, and nudge the
// bottom-right explain pane so the fresh detail card is visible without
// yanking the rest of the workspace (block: 'nearest' only scrolls if needed).
function explainSelected() {
  const ids = [...state.selection];
  const node = ids.length ? state.model.nodes[ids[ids.length - 1]] : null;
  if (!node) {
    renderNodeDetail(null, null, null);
    return;
  }
  loadInfo().then(() => {
    renderNodeDetail(null, describeNode(node), node);
    document.getElementById('explainNode')
      ?.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  });
}

// ---------------------------------------------------------------------------
// Quiz check
// ---------------------------------------------------------------------------

// Called after every structural change: redraw, and (when a quiz is running)
// re-check the tree automatically so there is no "Check" button.
function changed() {
  // Any structural edit after a snap leaves the snapped layout, so the builder
  // falls back to measuring boxes from their content.
  state.snapped = false;
  state.snappedLayout = null;
  // The user edited the tree, so stale Build-tree validation errors no longer
  // apply — clear them and let the words fall back to their lexical colouring.
  state.nodeErrors = new Map();
  draw();
  state.treeCorrect = treeIsComplete();
  // Words were added, edited, re-ordered, or removed: the input panel mirrors
  // the canvas again.
  syncCanvasToInput();
  if (state.challenge && !state.solved) checkTree();
  // Structural feedback is independent of the gold comparison: a detached
  // branch or an empty phrase box turns red as soon as the edit lands. The
  // standalone builder keeps its existing Build-tree validation instead.
  if (state.challenge) flagStructuralIssues();
}

// Paint disconnected nodes and empty phrase boxes. Skipped while the model is
// still only a word row (task 1 starts that way; every word is parentless by
// design until the learner adds the first phrase box).
function flagStructuralIssues() {
  const nodes = Object.values(state.model.nodes);
  if (!nodes.some((n) => n.kind === NODE.PHRASE)) return;
  const reach = (start) => {
    const seen = new Set();
    const stack = [start];
    while (stack.length) {
      const n = stack.pop();
      if (!n || seen.has(n.id)) continue;
      seen.add(n.id);
      for (const child of childrenOf(state.model, n.id)) stack.push(child);
    }
    return seen;
  };
  const roots = nodes.filter((n) => !n.parent);
  let main = null;
  let best = -1;
  for (const root of roots) {
    const size = reach(root).size;
    if (size > best) {
      best = size;
      main = root;
    }
  }
  const seen = main ? reach(main) : new Set();
  for (const n of nodes) {
    // Bare words are expected to sit unconnected while the learner is still
    // assembling the tree; a detached *phrase*, however, is a real orphan.
    if (n.kind === NODE.PHRASE && !seen.has(n.id) && !state.nodeErrors.has(n.id)) {
      state.nodeErrors.set(n.id, disconnectedDetail(n));
    }
  }
  for (const n of nodes) {
    if (n.kind === NODE.PHRASE
        && childrenOf(state.model, n.id).length === 0
        && !state.nodeErrors.has(n.id)) {
      state.nodeErrors.set(n.id, emptyPhraseDetail(n));
    }
  }
  draw();
}

// True when every node is connected under a single root — i.e. the tree is
// structurally complete (no orphan boxes, no cycles).
function treeIsComplete() {
  const nodes = Object.values(state.model.nodes);
  if (!nodes.length) return false;
  const roots = nodes.filter((n) => !n.parent);
  if (roots.length !== 1) return false;
  const root = roots[0];
  const visited = new Set();
  const walk = (id) => {
    visited.add(id);
    for (const c of childrenOf(state.model, id)) walk(c.id);
  };
  walk(root.id);
  return visited.size === nodes.length;
}

function showToast(msg, ok) {
  const stage = document.querySelector('.canvas-stage');
  if (!stage) return;
  let t = stage.querySelector('.builder-toast');
  if (!t) {
    t = document.createElement('div');
    t.className = 'builder-toast';
    stage.appendChild(t);
  }
  t.textContent = msg;
  t.classList.toggle('builder-toast-ok', ok === true);
  t.classList.toggle('builder-toast-no', ok === false);
  t.classList.add('show');
}

function hideToast() {
  document.querySelector('.builder-toast')?.classList.remove('show');
}

// A listener for the live check result, so the lesson's quiz panel can show
// the validation status next to the question.
let checkResultHandler = null;
export function setCheckResultHandler(fn) { checkResultHandler = fn || null; }

// A listener for every change to the built tree, so the lesson's diagnostics
// can follow the learner while they build.
let modelChangeHandler = null;
export function setModelChangeHandler(fn) { modelChangeHandler = fn || null; }

// Run a check on the current tree — the lesson's quiz stage asks for it.
export function checkBuilderTree() {
  if (!state.challenge) return false;
  checkTree();
  return true;
}

// The result of a check goes to the app log and — while a lesson stage is
// running — to the canvas hint, where the learner is actually looking. The
// stage's own hint comes back after a few seconds.
function reportCheck(message, kind) {
  state.onStatus?.(message);
  checkResultHandler?.(message, kind);
  if (!state.hintBase) return;
  setCanvasHint(message, kind);
  window.clearTimeout(state.hintTimer);
  state.hintTimer = window.setTimeout(() => {
    state.hintTimer = 0;
    setCanvasHint(state.hintBase);
  }, 6000);
}

function checkTree() {
  const challenge = state.challenge || {};
  const target = document.getElementById('builderTarget');
  const nextBtn = document.getElementById('builderNext');
  const mark = (ok) => {
    target?.classList.toggle('builder-target-ok', ok);
    if (nextBtn) {
      nextBtn.hidden = !(ok && state.challenge && typeof state.challenge.onNext === 'function');
    }
    if (ok && !state.solved) {
      state.solved = true;
      showToast('Correct!', true);
    }
  };

  if (challenge.kind === 'tokens') {
    const got = wordsInOrder().join(' ');
    const want = (challenge.gold || []).map((l) => l.surface).join(' ');
    if (got === want) {
      mark(true);
      reportCheck('Correct — those are exactly SynTutor\'s tokens.', 'ok');
      state.onComplete?.(true, {});
    } else {
      mark(false);
      reportCheck(`Not quite. SynTutor splits it as: ${want}`, 'no');
      state.onComplete?.(false, {});
    }
    return;
  }

  if (challenge.kind === 'tags') {
    const want = challenge.gold || [];
    const got = wordNodesInOrder();
    if (got.length !== want.length) {
      mark(false);
      reportCheck(`Add the ${want.length} words first (you have ${got.length}).`, 'no');
      state.onComplete?.(false, {});
      return;
    }
    const wrong = [];
    got.forEach((n, i) => {
      if ((n.tag || n.type) !== want[i].tag) wrong.push(`${n.text}→${n.tag || n.type} (want ${want[i].tag})`);
    });
    if (!wrong.length) {
      mark(true);
      reportCheck('Correct — every word carries its official tag.', 'ok');
      state.onComplete?.(true, {});
    } else {
      mark(false);
      reportCheck(`Not quite: ${wrong.join(', ')}. Right-click a word to set its tag.`, 'no');
      state.onComplete?.(false, {});
    }
    return;
  }

  // phrases / full: compare the phrase structure against SynTutor's parse.
  // A full-tree task is only done when every box belongs to one connected
  // tree; otherwise stray words could be ignored by the comparison.
  if (challenge.kind === 'full' && !treeIsComplete()) {
    state.onStatus('Connect every word and phrase into one tree first.');
    // The lesson's diagnostics panel shows the same verdict.
    reportCheck('Connect every word and phrase into one tree first.', 'no');
    return;
  }
  const tree = toTree(state.model);
  if (!tree) {
    // The tree is not connected yet: report it, but do not call the
    // completion callback — the learner is still building, not failing.
    reportCheck('Add a phrase box (right-click) and connect everything first.', 'no');
    return;
  }
  const gold = challenge.goldTree;
  if (!gold) {
    reportCheck('Tree built.', 'ok');
    return;
  }
  const result = compareTrees(tree, gold);
  if (result.correct) {
    mark(true);
    reportCheck('Correct — your tree matches SynTutor\'s parse.', 'ok');
    state.onComplete?.(true, result);
    return;
  }
  const parts = [];
  if (result.missing.length) {
    parts.push(`missing ${result.missing.map((s) => `${s.type} (${s.start}-${s.end})`).join(', ')}`);
  }
  if (result.extra.length) {
    parts.push(`extra ${result.extra.map((s) => `${s.type} (${s.start}-${s.end})`).join(', ')}`);
  }
  const message = `Not quite — ${parts.join('; ')}.`;
  mark(false);
  flagMismatchedBranches(result);
  // A wrong branch gets an immediate on-canvas toast; a tree that is merely
  // unfinished (missing constituents, no extras) only updates the status line
    reportCheck(message, 'no');
  // so the hint does not nag after every added box.
  if (result.extra.length) showToast(message, false);
  state.onStatus(message);
  state.onComplete?.(false, result);
}

// Paint the phrase boxes that the learner drew but SynTutor's parse does not
// contain. Missing constituents can only be described (there is no box to
// paint), but an extra branch gets an immediate red mark on the canvas.
function flagMismatchedBranches(result) {
  if (!result || !result.extra?.length) return;
  const bySpan = new Map();
  const root = Object.values(state.model.nodes)
    .find((n) => !n.parent && n.kind === NODE.PHRASE);
  if (!root) return;
  let cursor = 0;
  const walk = (node) => {
    const kids = childrenOf(state.model, node.id);
    if (!kids.length) {
      const start = cursor;
      cursor += 1;
      return;
    }
    const start = cursor;
    for (const kid of kids) walk(kid);
    bySpan.set(`${node.type}[${start}-${cursor}]`, node);
  };
  walk(root);
  for (const span of result.extra) {
    const node = bySpan.get(`${span.type}[${span.start}-${span.end}]`);
    if (!node || state.nodeErrors.has(node.id)) continue;
    state.nodeErrors.set(node.id, {
      type: node.type,
      surface: nodeLeafText(node.id),
      status: 'error',
      role: 'Not in SynTutor’s parse',
      text: `This ${node.type} covers “${nodeLeafText(node.id)}”, but SynTutor’s parse does not group those words that way.`,
      remediation: {
        violation: `The ${node.type} branch adds a constituent the parser does not license here.`,
        suggested_fix: 'Re-attach its children to the constituent that actually dominates them, or remove the extra phrase box.',
        alternative_fix: null,
      },
    });
  }
  draw();
}

// Word boxes ordered left-to-right by x (their reading order).
function wordNodesInOrder() {
  return Object.values(state.model.nodes)
    .filter((n) => n.kind === NODE.WORD)
    .sort((a, b) => a.x - b.x);
}
function wordsInOrder() {
  return wordNodesInOrder().map((n) => n.text);
}

// ---------------------------------------------------------------------------
// Snap to syntax-tree structure (hierarchical layout like the tutor canvas)
// ---------------------------------------------------------------------------

// Compute a hierarchical layout for the current builder model that mirrors the
// generator (renderer.js createLayout): leaves spread evenly left-to-right in
// uniform slots, each phrase centred over its children, depth-based rows.
// Returns {layout, ...} keyed by node id with centre coordinates, or null when
// there is no connected tree to lay out.
function computeTreeLayout() {
  const nodes = Object.values(state.model.nodes);
  if (!nodes.length || !state.ctx) return null;

  // Children map over every node, sorted by current x for a stable reading order.
  const kidsOf = new Map();
  for (const n of nodes) kidsOf.set(n.id, []);
  for (const n of nodes) {
    if (n.parent && state.model.nodes[n.parent]) kidsOf.get(n.parent).push(n);
  }

  // Count how many nodes are reachable from a given root (cycle-safe).
  const reachableFrom = (start) => {
    const seen = new Set();
    const stack = [start];
    while (stack.length) {
      const n = stack.pop();
      if (!n || seen.has(n.id)) continue;
      seen.add(n.id);
      for (const c of kidsOf.get(n.id) || []) stack.push(c);
    }
    return seen;
  };

  // Pick the parentless node that reaches the most nodes; prefer a phrase root.
  const parentless = nodes.filter((n) => !n.parent);
  const candidates = parentless.length ? parentless : nodes;
  let root = null;
  let best = -1;
  for (const n of candidates) {
    const size = reachableFrom(n).size + (n.kind === NODE.PHRASE ? 0.5 : 0);
    if (size > best) {
      best = size;
      root = n;
    }
  }
  if (!root) return null;

  // Depth + leaf order (DFS from the chosen root only).
  const depth = new Map();
  const leafIds = [];
  let maxDepth = 0;
  const visited = new Set();
  const walk = (n, d) => {
    if (!n || visited.has(n.id)) return;
    visited.add(n.id);
    maxDepth = Math.max(maxDepth, d);
    depth.set(n.id, d);
    const kids = (kidsOf.get(n.id) || []).slice().sort((a, b) => a.x - b.x);
    if (!kids.length) leafIds.push(n.id);
    for (const c of kids) walk(c, d + 1);
  };
  walk(root, 0);

  const leafIndex = new Map();
  leafIds.forEach((id, i) => leafIndex.set(id, i));

  const BOX_H = 34;
  const MIN_BOX_W = 54;
  const H_PAD = 14;
  const GAP = 26;
  const V_GAP = 40;
  const TOP_PAD = 24;

  // Uniform leaf slot sized from the widest leaf label (matches the generator).
  let maxLeafW = MIN_BOX_W;
  state.ctx.save();
  state.ctx.setTransform(1, 0, 0, 1, 0, 0);
  state.ctx.font = WORD_FONT;
  for (const id of leafIds) {
    const n = state.model.nodes[id];
    if (!n) continue;
    maxLeafW = Math.max(maxLeafW, state.ctx.measureText(n.text || n.type || '').width + H_PAD * 2);
  }
  state.ctx.restore();
  const SLOT = maxLeafW + GAP;

  // Bottom-up span (leaf range each node covers).
  const span = new Map();
  const collectSpan = (id) => {
    if (span.has(id)) return span.get(id);
    const kids = kidsOf.get(id) || [];
    if (!kids.length) {
      const s = [leafIndex.get(id), leafIndex.get(id)];
      span.set(id, s);
      return s;
    }
    let lo = Infinity, hi = -Infinity;
    for (const c of kids) {
      const cs = collectSpan(c.id);
      lo = Math.min(lo, cs[0]);
      hi = Math.max(hi, cs[1]);
    }
    const s = [lo, hi];
    span.set(id, s);
    return s;
  };
  collectSpan(root.id);

  // Lay out every node reachable from the root only; leave orphans untouched.
  const layout = new Map();
  for (const n of nodes) {
    if (!visited.has(n.id)) continue;
    const d = depth.get(n.id) || 0;
    const y = TOP_PAD + d * (BOX_H + V_GAP) + BOX_H / 2;
    const kids = kidsOf.get(n.id) || [];
    if (!kids.length) {
      const i = leafIndex.get(n.id);
      layout.set(n.id, { x: SLOT * i + SLOT / 2, y, w: SLOT, h: BOX_H });
    } else {
      const s = span.get(n.id);
      const x = ((s[0] + s[1]) / 2 + 0.5) * SLOT;
      const w = (s[1] - s[0] + 1) * SLOT;
      layout.set(n.id, { x, y, w, h: BOX_H });
    }
  }
  if (!layout.size) return null;
  return { layout, SLOT, maxDepth, TOP_PAD, BOX_H, V_GAP };
}

// Re-arrange every node into the hierarchical syntax-tree layout so it matches
// the tree SynTutor's generator produces. Returns the layout map (or null when
// there is no connected tree). `fit` controls whether the viewport is refitted.
function applyTreeLayout({ fit = true } = {}) {
  const result = computeTreeLayout();
  if (!result) return null;
  const { layout } = result;
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const [id, pos] of layout) {
    const n = state.model.nodes[id];
    if (!n) continue;
    n.x = pos.x - pos.w / 2;
    n.y = pos.y - pos.h / 2;
    n.w = pos.w;
    n.h = pos.h;
    minX = Math.min(minX, n.x);
    minY = Math.min(minY, n.y);
    maxX = Math.max(maxX, n.x + n.w);
    maxY = Math.max(maxY, n.y + n.h);
  }
  if (!fit) return layout;
  const cw = state.canvas.clientWidth;
  const ch = state.canvas.clientHeight;
  const totalW = Math.max(maxX - minX, 1);
  const totalH = Math.max(maxY - minY, 1);
  if (cw && ch) {
    const pad = 30;
    let scale = Math.min((cw - pad * 2) / totalW, (ch - pad * 2) / totalH, 1.7) * 1.25;
    scale = Math.max(Math.min(scale, 1.7), 0.2);
    state.view.scale = scale;
    state.view.ox = (cw - totalW * scale) / 2 - minX * scale;
    state.view.oy = (ch - totalH * scale) / 2 - minY * scale;
  }
  return layout;
}

async function buildTree() {
  const layout = applyTreeLayout({ fit: true });
  if (!layout) {
    state.onStatus('Build a connected tree first — drag connector dots to link nodes.');
    return;
  }
  changed();
  state.snapped = true;
  state.snappedLayout = layout;
  draw();
  // Re-validate every word against SynTutor's model so that recognised words
  // lose their red styling once the tree is structurally complete.
  const wordNodes = Object.values(state.model.nodes).filter((n) => n.kind === NODE.WORD);
  if (wordNodes.length) {
    await validateWords(wordNodes);
  }
  state.treeCorrect = treeIsComplete();
  draw();
  // Surface the constructed sentence in the tutor's top input box so the page
  // reads like a normal analysis of that sentence — the input panel always
  // mirrors the canvas, and building the tree only re-orders it.
  syncCanvasToInput();
  // Check the node connections and the overall structure, mark anything invalid
  // red, and report the findings in the right-hand explain panel.
  await validateBuiltTree();
}

// ---------------------------------------------------------------------------
// Build-tree validation
// ---------------------------------------------------------------------------

// Structural + lexical check run after Build tree. Invalid nodes are recorded
// in state.nodeErrors (id -> detail shaped like the tutor's
// payload.node_details[id]), painted red on the canvas, and the first problem
// is surfaced in the right-hand explain panel — the same way the tutor
// reports errors.
async function validateBuiltTree() {
  const errors = state.nodeErrors;
  const nodes = Object.values(state.model.nodes);
  if (!nodes.length) return;

  // --- 1. Structural checks (client-side) ----------------------------
  const roots = nodes.filter((n) => !n.parent);

  // More than one root: everything after the first is a stray tree.
  if (roots.length > 1) {
    for (const r of roots.slice(1)) {
      if (!errors.has(r.id)) errors.set(r.id, disconnectedDetail(r));
    }
  }

  // Orphans: nodes unreachable from the primary root.
  if (roots.length >= 1) {
    const seen = new Set();
    const walk = (id) => { seen.add(id); for (const c of childrenOf(state.model, id)) walk(c.id); };
    walk(roots[0].id);
    for (const n of nodes) {
      if (!seen.has(n.id) && !errors.has(n.id)) errors.set(n.id, disconnectedDetail(n));
    }
  }

  // Phrase nodes must dominate something.
  for (const n of nodes) {
    if (n.kind === NODE.PHRASE && childrenOf(state.model, n.id).length === 0 && !errors.has(n.id)) {
      errors.set(n.id, emptyPhraseDetail(n));
    }
  }

  // Words SynTutor doesn't recognise.
  for (const n of nodes) {
    if (n.kind === NODE.WORD && n.valid === false && !errors.has(n.id)) {
      errors.set(n.id, describeNode(n));
    }
  }

  // --- 2. Grammaticality of the constructed sentence (best-effort) ---
  const sentence = wordsInOrder().join(' ');
  let verdictLine = null;
  if (sentence.trim()) {
    try {
      const res = await fetch('/api/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: sentence }),
      });
      if (res.ok) {
        const payload = await res.json();
        const summary = payload.summary || {};
        if (summary.valid === false) {
          verdictLine = summary.explanation
            || `SynTutor reads “${sentence}” as ungrammatical.`;
        }
      }
    } catch {
      // Backend unreachable — the structural checks above still apply.
    }
  }

  // --- 3. Report ----------------------------------------------------
  state.treeCorrect = errors.size === 0 && treeIsComplete();
  draw();
  reportBuildResult(sentence, errors, verdictLine);
}

function disconnectedDetail(n) {
  return {
    type: n.kind === NODE.PHRASE ? n.type : (n.tag || 'WORD'),
    surface: n.kind === NODE.PHRASE ? nodeLeafText(n.id) : n.text,
    status: 'error',
    role: 'Disconnected',
    text: `“${nodeLabel(n)}” is not connected to the tree — every node must hang under a single root.`,
    remediation: {
      violation: `“${nodeLabel(n)}” forms its own tree, so the builder holds more than one root.`,
      suggested_fix: 'Drag its connector dot onto the main tree to attach it as a child.',
      alternative_fix: null,
    },
  };
}

function emptyPhraseDetail(n) {
  return {
    type: n.type,
    surface: '',
    status: 'error',
    role: 'Empty phrase',
    text: `The ${n.type} phrase has nothing under it.`,
    remediation: {
      violation: `A ${n.type} phrase must dominate at least one word or sub-phrase.`,
      suggested_fix: 'Drag a word or another phrase’s dot onto this phrase to fill it.',
      alternative_fix: null,
    },
  };
}

// Surface the first error in the right-hand panel (mirroring the tutor's
// node detail), or a summary when the tree is clean.
function reportBuildResult(sentence, errors, verdictLine) {
  if (errors.size) {
    const firstId = [...errors.keys()][0];
    const node = state.model.nodes[firstId];
    if (node) {
      selectOnly(firstId);
      renderNodeDetail(null, errors.get(firstId), node);
      draw();
    }
    const n = errors.size;
    state.onStatus(`Tree built — ${n} problem${n === 1 ? '' : 's'} found (see panel).`);
    return;
  }
  if (verdictLine) {
    renderDiagnostic('Sentence may be ungrammatical', [verdictLine]);
    state.onStatus('Tree built — but SynTutor flags the sentence itself (see panel).');
    return;
  }
  // Clean: show a green summary card in the panel.
  const root = Object.values(state.model.nodes).find((x) => !x.parent);
  renderNodeDetail(null, {
    type: root && root.kind === NODE.PHRASE ? root.type : 'S',
    surface: sentence,
    status: 'valid',
    role: 'Sentence',
    text: `“${sentence}” is connected and every node is structurally valid.`,
  }, root || { id: '__summary__' });
  state.onStatus('Tree built — the sentence and its structure are valid.');
}

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

function measureWord(text) {
  state.ctx.setTransform(1, 0, 0, 1, 0, 0);
  state.ctx.font = WORD_FONT;
  return Math.max(30, state.ctx.measureText(text || '').width + 16);
}

function measurePhrase(type) {
  state.ctx.setTransform(1, 0, 0, 1, 0, 0);
  state.ctx.font = PHRASE_FONT;
  return Math.max(30, state.ctx.measureText(type || '').width + 16);
}

// Keep each box's measured size in sync with its label (used for hit-testing).
function sizeNode(n) {
  n.h = NODE_H;
  n.w = n.kind === NODE.PHRASE ? measurePhrase(n.type) : measureWord(n.text);
}

// Order nodes so parents are painted after children (roots last) — matches the
// tutor renderer, where the root is emphasised.
function paintOrder() {
  return Object.values(state.model.nodes);
}

function draw() {
  if (!state.ctx) return;
  cancelAnimationFrame(state.frame);
  state.frame = requestAnimationFrame(render);
  // The tree changed: whoever watches it (the lesson's diagnostics) follows.
  modelChangeHandler?.();
}

function render() {
  const ctx = state.ctx;
  const canvas = state.canvas;
  if (!ctx || !canvas) return;
  const dpr = state.dpr;
  const { ox, oy, scale } = state.view;

  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr); // clear background

  // Measure boxes before applying the view transform — measuring resets the
  // canvas transform, so it must happen first. When the tree has been snapped
  // into the generator layout, keep the snapped slot sizes instead.
  const nodes = paintOrder();
  if (!state.snapped) {
    for (const n of nodes) sizeNode(n);
  }

  ctx.save();
  ctx.setTransform(dpr * scale, 0, 0, dpr * scale, dpr * ox, dpr * oy);

  const c = themeColors();
  // edges first (straight, thin). Anchors hug the rendered labels so the line
  // reads as directly connected to each node.
  for (const n of nodes) {
    if (!n.parent) continue;
    const parent = state.model.nodes[n.parent];
    if (!parent) continue;
    const childIsLeaf = childrenOf(state.model, n.id).length === 0;
    // Stop just above a leaf's POS tag when it has one, otherwise hug the word.
    const childGap = childIsLeaf && n.tag ? 24 : 12;
    // An edge into a node that failed validation is drawn red, like the tutor.
    const bad = state.nodeErrors.has(n.id);
    drawEdge(ctx,
      { x: parent.x + parent.w / 2, y: parent.y + parent.h / 2 + 12 },
      { x: n.x + n.w / 2, y: n.y + n.h / 2 - childGap },
      bad ? c.error : undefined);
  }

  // rubber-band link being dragged
  if (state.link) {
    if (state.link.free === 'parent') {
      const child = state.model.nodes[state.link.childId];
      if (child) {
        const childIsLeaf = childrenOf(state.model, child.id).length === 0;
        const childGap = childIsLeaf && child.tag ? 24 : 12;
        drawEdge(ctx, { x: child.x + child.w / 2, y: child.y + child.h / 2 - childGap }, { x: state.link.x, y: state.link.y });
      }
    } else {
      const parent = state.model.nodes[state.link.parentId];
      if (parent) drawEdge(ctx, { x: parent.x + parent.w / 2, y: parent.y + parent.h / 2 + 12 }, { x: state.link.x, y: state.link.y });
    }
  }

  // nodes
  for (const n of nodes) {
    drawNode(ctx, n);
  }

  // marquee selection rectangle (drawn in world space, on top of nodes)
  if (state.marquee) {
    const { x0, y0, x1, y1 } = state.marquee;
    const minX = Math.min(x0, x1), maxX = Math.max(x0, x1);
    const minY = Math.min(y0, y1), maxY = Math.max(y0, y1);
    ctx.strokeStyle = c.accent;
    ctx.lineWidth = 1;
    ctx.setLineDash([6, 4]);
    ctx.strokeRect(minX, minY, maxX - minX, maxY - minY);
    ctx.setLineDash([]);
    ctx.fillStyle = c.accent + '20';
    ctx.fillRect(minX, minY, maxX - minX, maxY - minY);
  }
  ctx.restore();
}

function drawEdge(ctx, a, b, color) {
  ctx.save();
  ctx.strokeStyle = color || themeColors().edge;
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(a.x, a.y);
  ctx.lineTo(b.x, b.y);
  ctx.stroke();
  ctx.restore();
}

function drawNode(ctx, n) {
  const c = themeColors();
  const selected = isSelected(n.id);
  const hovered = state.hover === n.id || state.hoverTarget === n.id || state.hoverEndpoint === n.id;
  const rejected = state.reject && state.reject.id === n.id;
  const isPhrase = n.kind === NODE.PHRASE;
  // A node is red when Build tree flagged it (state.nodeErrors), or when it is
  // an unknown word and the tree is not yet structurally complete.
  const invalid = state.nodeErrors.has(n.id)
    || (n.kind === NODE.WORD && n.valid === false && !state.treeCorrect);

  let color = c.text;
  if (invalid || rejected) color = c.error;
  if (hovered) color = c.accent;
  if (selected) color = c.selected;

  const cx = n.x + n.w / 2;
  const cy = n.y + n.h / 2;

  ctx.save();
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  if (isPhrase) {
    ctx.fillStyle = color;
    ctx.font = '600 16px Inter, system-ui, sans-serif';
    ctx.fillText(n.type, cx, cy + 3);
  } else {
    ctx.fillStyle = color;
    ctx.font = WORD_FONT;
    ctx.fillText(n.text || '…', cx, cy + 3);
    if (n.tag) {
      ctx.fillStyle = invalid ? c.error : c.tag;
      ctx.font = TAG_FONT;
      ctx.fillText(n.tag, cx, cy - 14);
    }
    if (invalid && n.suggestion) {
      ctx.fillStyle = c.tag;
      ctx.font = '500 11px Inter, system-ui, sans-serif';
      ctx.fillText(`→ ${n.suggestion}`, cx, n.y + n.h + 12);
    }
  }

  // Endpoint handle (connected child) — revealed on hover so the clean tree
  // look matches the grammar tutor.
  if (n.parent && hovered) {
    const ep = { x: cx, y: n.y };
    ctx.beginPath();
    ctx.arc(ep.x, ep.y, 4, 0, Math.PI * 2);
    ctx.fillStyle = c.accent;
    ctx.fill();
  }
  // Connector dot (phrase) — drag it to start a new connection. Always shown so
  // the connect target is easy to find and click.
  if (isPhrase) {
    const d = { x: cx, y: n.y + n.h + 6 };
    ctx.beginPath();
    ctx.arc(d.x, d.y, 5, 0, Math.PI * 2);
    ctx.fillStyle = c.accent;
    ctx.fill();
  }
  ctx.restore();
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function getCss(name, fallback) {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || fallback;
}

// Re-export a couple of helpers the quiz reuses.
export { toTree, compareTrees, leavesOf };

// ---------------------------------------------------------------------------
// Step-guide spotlight — client-space boxes for the lesson's interactive guide
// ---------------------------------------------------------------------------

// Client-pixel rectangle the lesson step guide should spotlight. `target` is
// one of:
//   { kind: 'words' }          the pre-placed word boxes (with their tags)
//   { kind: 'phrase', type }   an existing phrase box, e.g. { type: 'NP' }
//   { kind: 'dot', type }      that box's connector dot
//   { kind: 'spot' }           the empty region where the next box gets added
//   { kind: 'canvas' }         the whole canvas
// Returns { left, top, width, height } in client coordinates, or null when
// the canvas is hidden or the target does not exist (yet).
export function canvasGuideBox(target = {}) {
  const canvas = state.canvas;
  if (!canvas || canvas.hidden || !state.ctx) return null;
  const rect = canvas.getBoundingClientRect();
  if (!rect.width || !rect.height) return null;
  const pad = 12; // world units of breathing room around nodes
  const toClient = (wx, wy) => {
    const p = toScreen(wx, wy);
    return { x: rect.left + p.x, y: rect.top + p.y };
  };
  const boxOf = (x0, y0, x1, y1) => {
    const a = toClient(x0, y0);
    const b = toClient(x1, y1);
    return { left: a.x, top: a.y, width: b.x - a.x, height: b.y - a.y };
  };
  const nodes = Object.values(state.model.nodes);
  const phraseOf = (type) => nodes.find((n) => n.kind === NODE.PHRASE && n.type === type) || null;
  const bbox = (list) => {
    if (!list.length) return null;
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const n of list) {
      sizeNode(n);
      x0 = Math.min(x0, n.x);
      y0 = Math.min(y0, n.y);
      x1 = Math.max(x1, n.x + n.w);
      y1 = Math.max(y1, n.y + n.h);
    }
    return { x0, y0, x1, y1 };
  };

  switch (target.kind) {
    case 'words': {
      // Word boxes are drawn with their POS tag above, so pad a little higher.
      const b = bbox(nodes.filter((n) => n.kind === NODE.WORD));
      if (!b) return null;
      return boxOf(b.x0 - pad, b.y0 - pad - 4, b.x1 + pad, b.y1 + pad);
    }
    case 'phrase': {
      const n = phraseOf(target.type);
      if (!n) return null;
      sizeNode(n);
      return boxOf(n.x - pad, n.y - pad, n.x + n.w + pad, n.y + n.h + pad);
    }
    case 'dot': {
      const n = phraseOf(target.type);
      if (!n) return null;
      sizeNode(n);
      const cx = n.x + n.w / 2;
      const cy = n.y + n.h + 6;
      return boxOf(cx - 14, cy - 14, cx + 14, cy + 14);
    }
    case 'spot': {
      // An empty patch just above the word row (or the view's centre) — where
      // the learner is about to drop the next box.
      const b = bbox(nodes.filter((n) => n.kind === NODE.WORD));
      let cx;
      let y1;
      if (b) {
        cx = (b.x0 + b.x1) / 2;
        y1 = b.y0 - 40;
      } else {
        const w0 = toWorld(0, 0);
        const w1 = toWorld(rect.width, rect.height);
        cx = (w0.x + w1.x) / 2;
        y1 = (w0.y + w1.y) / 2 + 40;
      }
      const cl = boxOf(cx - 150, y1 - 120, cx + 150, y1);
      // Keep the spotlight inside the canvas when there is room.
      const m = 14;
      return {
        left: Math.max(rect.left + m, Math.min(cl.left, rect.right - cl.width - m)),
        top: Math.max(rect.top + m, Math.min(cl.top, rect.bottom - cl.height - m)),
        width: cl.width,
        height: cl.height,
      };
    }
    default:
      return { left: rect.left + 10, top: rect.top + 10, width: rect.width - 20, height: rect.height - 20 };
  }
}
