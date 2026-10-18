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
//   drag empty space          -> pan      wheel -> zoom

import {
  POS_TYPES, PHRASE_NODE_TYPES, NODE_TYPE_GROUPS, NODE,
  createModel, addWordsFromText, addPhrase, moveNode, setType,
  removeNode, connect, canConnect, disconnect,
  dotOf, dotHit, nodeHit, endpointOf, endpointHit, toTree, compareTrees, leavesOf, leafText,
  seedWords, leavesWithTags, childrenOf,
} from './syntax-builder.js';
import { renderNodeDetail } from './ui.js';

const WORD_FONT = '500 15px Inter, system-ui, sans-serif';
const TAG_FONT = '600 10px Inter, system-ui, sans-serif';
const PHRASE_FONT = '600 16px Inter, system-ui, sans-serif';
const NODE_H = 34;

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
  solved: false,
  root: null,
  canvas: null,
  ctx: null,
  editor: null,
  menu: null,
  dpr: 1,
  frame: 0,
};

export function initSyntaxBuilder({ onStatusChange } = {}) {
  state.onStatus = onStatusChange || (() => {});
}

export function builderModel() {
  return state.model;
}

// ---------------------------------------------------------------------------
// View lifecycle
// ---------------------------------------------------------------------------

export function openBuilderView(opts = {}) {
  const bar = document.getElementById('builderBar');
  const canvas = document.getElementById('builderCanvas');
  const treeCanvas = document.getElementById('treeCanvas');
  if (!bar || !canvas) return;
  ensureWired();
  canvas.hidden = false;
  if (treeCanvas) treeCanvas.hidden = true;
  document.getElementById('emptyTreeState')?.classList.add('hidden');
  // Lessons and quizzes build in place on this canvas; only the standalone
  // Syntax Builder (no challenge) highlights its own sidebar tab, unless the
  // caller asks for a specific tab via `opts.sidebarView`.
  const sidebarView = opts.sidebarView || (opts.challenge ? null : 'builder');
  if (sidebarView) markSidebar(sidebarView);
  state.challenge = opts.challenge || null;
  state.onComplete = opts.onComplete || null;
  state.solved = false;
  if (opts.model) state.model = opts.model;
  if (opts.reset) newModel();
  if (state.challenge) seedForChallenge(state.challenge);

  // A quiz shows no builder chrome at all — the sentence lives in the input box
  // and the tree is checked automatically. Lesson practice keeps a slim hint
  // bar instead: the canvas is the same node editor as the standalone Syntax
  // Builder (right-click to add boxes, drag a dot to connect, grab a link end
  // to re-route or delete), so spell the affordances out where they apply.
  const practice = Boolean(state.challenge) && Boolean(opts.practice);
  bar.hidden = Boolean(state.challenge) && !practice;
  if (!state.challenge) {
    document.getElementById('builderTitle').textContent = 'Syntax Builder';
    document.getElementById('builderHint').textContent =
      'Double-click to type words · Right-click to add a phrase · Drag a dot to connect';
    document.getElementById('builderTarget').hidden = true;
    document.getElementById('builderCheck').hidden = true;
    document.getElementById('builderNext').hidden = true;
    document.getElementById('builderClose').hidden = false;
  } else if (practice) {
    document.getElementById('builderTitle').textContent = 'Lesson practice';
    document.getElementById('builderHint').textContent =
      'Right-click to add a phrase · drag a dot to connect · grab a link end to re-route or delete';
    document.getElementById('builderTarget').hidden = true;
    document.getElementById('builderCheck').hidden = true;
    document.getElementById('builderNext').hidden = true;
    document.getElementById('builderClose').hidden = true;
  }
  hideToast();
  resize();
  canvas.focus();
  explainSelected();
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
  const words = seedWords(state.model, leaves, 60, 360, withTags);
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
  const bar = document.getElementById('builderBar');
  const canvas = document.getElementById('builderCanvas');
  const treeCanvas = document.getElementById('treeCanvas');
  if (!bar) return;
  closeEditor();
  closeMenu();
  bar.hidden = true;
  if (canvas) canvas.hidden = true;
  if (treeCanvas) treeCanvas.hidden = false;
  state.challenge = null;
  state.onComplete = null;
  onBuilderClose();
}

let onBuilderClose = () => {};
export function setBuilderCloseHandler(fn) { onBuilderClose = fn || (() => {}); }

export function isBuilderOpen() {
  const bar = document.getElementById('builderBar');
  return !!bar && !bar.hidden;
}

export function setChallenge(challenge, onComplete) {
  state.challenge = challenge || null;
  state.onComplete = onComplete || null;
  newModel();
  openBuilderView({ challenge, onComplete });
}

export function newModel() {
  state.model = createModel();
  state.selection.clear();
  state.drag = null;
  state.link = null;
  state.marquee = null;
  const target = document.getElementById('builderTarget');
  if (target) target.classList.remove('builder-target-ok');
}

function markSidebar(view) {
  document.querySelectorAll('.sidebar-item[data-view]').forEach((b) => {
    b.classList.toggle('active', b.dataset.view === view);
  });
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
  document.getElementById('builderClear')?.addEventListener('click', () => {
    newModel();
    draw();
  });
  document.getElementById('builderClose')?.addEventListener('click', () => {
    closeBuilderView();
    markSidebar('tutor');
  });
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
  if (e.button === 2) return; // right-click handled elsewhere
  const { sx, sy } = eventPos(e);
  const w = toWorld(sx, sy);

  const dot = dotHit(state.model, w.x, w.y);
  if (dot) {
    state.link = { parentId: dot.id, childId: null, free: 'child', x: w.x, y: w.y };
    closeMenu();
    return;
  }
  // Grab an existing connection at the child's endpoint to re-route or remove
  // it. Detaching straight away means a plain click deletes the connection;
  // dragging it onto another phrase re-attaches it there.
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
  // empty space: shift-drag starts a marquee selection, otherwise pan
  closeMenu();
  if (e.shiftKey) {
    state.marquee = { x0: w.x, y0: w.y, x1: w.x, y1: w.y, base: new Set(state.selection) };
    draw();
    return;
  }
  clearSelection();
  state.pan = { sx, sy, ox: state.view.ox, oy: state.view.oy };
  draw();
  explainSelected();
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
    draw();
    return;
  }
  if (state.pan) {
    state.view.ox = state.pan.ox + (sx - state.pan.sx);
    state.view.oy = state.pan.oy + (sy - state.pan.sy);
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
        // Rejected: the word is not in SynTutor's model, or the link would loop.
        const reason = (tgt.kind === NODE.WORD && tgt.valid === false)
          ? `“${tgt.text}” is not a word SynTutor knows${tgt.suggestion ? ` — did you mean “${tgt.suggestion}”?` : ''}.`
          : 'That connection is not allowed.';
        flashRejected(tgt.id);
        state.onStatus(reason);
      }
    }
    state.link = null;
    state.hoverTarget = null;
    changed();
  }
  if (state.marquee) {
    const { x0, y0, x1, y1, base } = state.marquee;
    const minX = Math.min(x0, x1), maxX = Math.max(x0, x1);
    const minY = Math.min(y0, y1), maxY = Math.max(y0, y1);
    const next = new Set(base || []);
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
  state.drag = null;
  state.pan = null;
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
// marked and cannot be connected (canConnect rejects child.valid === false).
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
  e.preventDefault();
  const { sx, sy } = eventPos(e);
  const w = toWorld(sx, sy);
  const node = nodeHit(state.model, w.x, w.y);
  openMenu(e.clientX, e.clientY, w, node);
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
    state.hoverTarget = null;
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
  if (state.editor) {
    state.editor.remove();
    state.editor = null;
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
  draw();
  if (state.challenge && !state.solved) checkTree();
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
      state.onStatus('Correct — those are exactly SynTutor\'s tokens.');
      state.onComplete?.(true, {});
    } else {
      mark(false);
      state.onStatus(`Not quite. SynTutor splits it as: ${want}`);
      state.onComplete?.(false, {});
    }
    return;
  }

  if (challenge.kind === 'tags') {
    const want = challenge.gold || [];
    const got = wordNodesInOrder();
    if (got.length !== want.length) {
      mark(false);
      state.onStatus(`Add the ${want.length} words first (you have ${got.length}).`);
      state.onComplete?.(false, {});
      return;
    }
    const wrong = [];
    got.forEach((n, i) => {
      if ((n.tag || n.type) !== want[i].tag) wrong.push(`${n.text}→${n.tag || n.type} (want ${want[i].tag})`);
    });
    if (!wrong.length) {
      mark(true);
      state.onStatus('Correct — every word carries its official tag.');
      state.onComplete?.(true, {});
    } else {
      mark(false);
      state.onStatus(`Not quite: ${wrong.join(', ')}. Right-click a word to set its tag.`);
      state.onComplete?.(false, {});
    }
    return;
  }

  // phrases / full: compare the phrase structure against SynTutor's parse.
  const tree = toTree(state.model);
  if (!tree) {
    state.onStatus('Add a phrase box (right-click) and connect everything first.');
    return;
  }
  const gold = challenge.goldTree;
  if (!gold) {
    state.onStatus('Tree built.');
    return;
  }
  const result = compareTrees(tree, gold);
  if (result.correct) {
    mark(true);
    state.onStatus('Correct — your tree matches SynTutor\'s parse.');
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
  mark(false);
  state.onStatus(`Not quite — ${parts.join('; ')}.`);
  state.onComplete?.(false, result);
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
  // canvas transform, so it must happen first.
  const nodes = paintOrder();
  for (const n of nodes) sizeNode(n);

  ctx.save();
  ctx.setTransform(dpr * scale, 0, 0, dpr * scale, dpr * ox, dpr * oy);

  // edges first (straight, thin, like the tutor tree)
  for (const n of nodes) {
    if (!n.parent) continue;
    const parent = state.model.nodes[n.parent];
    if (!parent) continue;
    drawEdge(ctx, { x: parent.x + parent.w / 2, y: parent.y + parent.h },
      { x: n.x + n.w / 2, y: n.y });
  }

  // rubber-band link being dragged
  if (state.link) {
    if (state.link.free === 'parent') {
      const child = state.model.nodes[state.link.childId];
      if (child) drawEdge(ctx, { x: child.x + child.w / 2, y: child.y }, { x: state.link.x, y: state.link.y });
    } else {
      const parent = state.model.nodes[state.link.parentId];
      if (parent) drawEdge(ctx, { x: parent.x + parent.w / 2, y: parent.y + parent.h }, { x: state.link.x, y: state.link.y });
    }
  }

  // nodes
  for (const n of nodes) {
    drawNode(ctx, n);
  }
  ctx.restore();
}

function drawEdge(ctx, a, b) {
  ctx.save();
  ctx.strokeStyle = themeColors().edge;
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
  const invalid = n.kind === NODE.WORD && n.valid === false;

  let color = c.text;
  if (isPhrase) color = c.accent;
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
  // Connector dot (phrase) — drag it to start a new connection.
  if (isPhrase && (hovered || state.link)) {
    const d = { x: cx, y: n.y + n.h + 6 };
    ctx.beginPath();
    ctx.arc(d.x, d.y, 4, 0, Math.PI * 2);
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
