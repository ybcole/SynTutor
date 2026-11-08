function collectNodes(root) {
  const out = [];
  const walk = (n) => {
    out.push(n);
    for (const c of n.children || []) walk(c);
  };
  walk(root);
  return out;
}

const BOX_H = 34;
const MIN_BOX_W = 54;
const H_PAD = 14;
const TOP_PAD = 24;
const SIDE_PAD = 24;
const LABEL_GAP = 20;

function getThemeColors() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  return {
    nodeStroke: isDark ? '#a78bfa' : '#6d5ae6',
    text: isDark ? '#f1f5f9' : '#2b2440',
    edge: isDark ? '#94a3b8' : '#000000',
    edgeValid: isDark ? '#94a3b8' : '#000000',
    edgeError: '#d64545',
    edgeText: isDark ? '#94a3b8' : '#77708f',
    selectedStroke: '#eab308',
  };
}

const ch = (nd) => nd.children || [];

export function createLayout(root, measure, viewportWidth = 800) {
  const nodes = collectNodes(root);
  const leaves = nodes.filter(node => ch(node).length === 0);
  const layout = new Map();
  const widths = new Map();
  const labels = new Map();
  const bounds = new Map();
  const gap = viewportWidth < 600 || leaves.length >= 8 ? 16 : 18;
  const row = BOX_H + (leaves.length >= 8 ? 28 : 30);
  let maxDepth = 0;

  function size(node) {
    const label = Math.max(MIN_BOX_W, measure(nodeLabel(node)) + H_PAD * 2,
      ch(node).length ? 0 : measure(node.type) + H_PAD);
    labels.set(node.id, label);
    const children = ch(node).map(size);
    const childrenWidth = children.reduce((sum, width) => sum + width, 0)
      + Math.max(0, children.length - 1) * gap;
    const width = Math.max(label, childrenWidth);
    widths.set(node.id, { width, childrenWidth });
    return width;
  }

  function place(node, left, depth) {
    const { width, childrenWidth } = widths.get(node.id);
    maxDepth = Math.max(maxDepth, depth);
    const y = TOP_PAD + depth * row + BOX_H / 2;
    const x = left + width / 2;
    layout.set(node.id, {
      id: node.id, node, x, y, w: labels.get(node.id), h: BOX_H, leaf: !ch(node).length,
    });
    bounds.set(node.id, { left, right: left + width });
    let childLeft = x - childrenWidth / 2;
    for (const child of ch(node)) {
      place(child, childLeft, depth + 1);
      childLeft += widths.get(child.id).width + gap;
    }
  }
  const totalW = Math.max(size(root) + SIDE_PAD * 2, 320);
  place(root, (totalW - widths.get(root.id).width) / 2, 0);
  const totalH = Math.max(TOP_PAD + maxDepth * row + BOX_H + SIDE_PAD * 2, 160);
  return { layout, bounds, totalW, totalH, maxDepth, nodes, leaves, root };
}

function nodeLabel(node) {
  if (ch(node).length === 0) return node.surface || node.type;
  return node.type;
}

export class TreeRenderer {
  constructor(canvas, opts = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.onSelect = opts.onSelect || (() => {});
    this.onHover = opts.onHover || (() => {});
    this.outline = opts.outline;
    this.outline?.querySelector('[data-zoom="in"]')?.addEventListener('click', () => this.zoom(1.2));
    this.outline?.querySelector('[data-zoom="out"]')?.addEventListener('click', () => this.zoom(1 / 1.2));
    this.outline?.querySelector('[data-zoom="fit"]')?.addEventListener('click', () => this.clearFocus());
    this.describe = opts.describe || (() => null);
    this.tree = null;
    this.layoutData = null;
    this.view = { scale: 1, tx: 0, ty: 0 };
    this.selectedId = null;
    this.hoverId = null;
    this.hoverX = 0;
    this.hoverY = 0;
    this.interactive = true;
    this._drag = null;
    this.dfsOrder = [];
    this.indexById = new Map();
    // True when the last fit attempt found no room to draw (the canvas was
    // hidden or zero-sized). The tree is re-fitted as soon as the canvas has
    // a size again — otherwise it would come back squished into a corner.
    this.needsFit = false;
    // Interactive corrective feedback: the subtree the current error lives in
    // (and the pair of nodes the rule links together).
    this.focus = null;
    this._raf = null;
    this._setup();
    this._resize();
  }

  _setup() {
    this.canvas.addEventListener('pointerdown', e => {
      if (!e.isPrimary || e.button !== 0) return;
      this.canvas.setPointerCapture(e.pointerId);
      this._onDown(e);
    });
    this.canvas.addEventListener('pointermove', e => { if (e.isPrimary) this._onMove(e); });
    this.canvas.addEventListener('pointerup', e => { if (e.isPrimary) this._onUp(); });
    this.canvas.addEventListener('pointercancel', () => { this._drag = null; });
    this.canvas.addEventListener('lostpointercapture', () => { this._drag = null; });
    this.canvas.addEventListener('pointerleave', () => this._onLeave());
    this.canvas.addEventListener('wheel', (e) => this._onWheel(e), { passive: false });
    this.canvas.addEventListener('keydown', (e) => this._onKey(e));
    window.addEventListener('resize', () => this._resize());
  }

  _onKey(e) {
    if (!this.tree || !this.interactive) return;
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      e.preventDefault();
      const dir = (e.key === 'ArrowLeft' || e.key === 'ArrowUp') ? -1 : 1;
      const cur = this.selectedId && this.indexById.has(this.selectedId)
        ? this.indexById.get(this.selectedId)
        : -1;
      const next = this.dfsOrder[Math.min(Math.max(cur + dir, 0), this.dfsOrder.length - 1)];
      if (next) this.onSelect(next);
      return;
    }
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (this.selectedId) this.onSelect(this.selectedId);
    }
  }

  _measure(label) {
    this.ctx.font = '600 16px Inter, system-ui, sans-serif';
    return this.ctx.measureText(label).width;
  }

  setTree(root) {
    this.focus = null;
    this.tree = root;
    cancelAnimationFrame(this._raf);
    this._layoutTree(this.canvas.clientWidth);
    this.dfsOrder = collectNodes(root).map((n) => n.id);
    this.indexById = new Map(this.dfsOrder.map((id, i) => [id, i]));
    this.selectedId = null;
    this._fitView();
    this._renderOutline();
    this.draw();
  }

  select(id) {
    this.selectedId = id;
    this.outline?.querySelectorAll('[data-node]').forEach(button => {
      if (button.dataset.node === id) button.setAttribute('aria-current', 'true');
      else button.removeAttribute('aria-current');
    });
    this.draw();
  }

  _renderOutline() {
    if (!this.outline) return;
    this.outline.hidden = !this.tree;
    const body = this.outline.querySelector('.tree-outline-body');
    body.replaceChildren();
    if (!this.tree) {
      this.outline.open = false;
      return;
    }
    const list = nodes => {
      const ul = document.createElement('ul');
      for (const node of nodes) {
        const item = document.createElement('li');
        const button = document.createElement('button');
        button.type = 'button';
        button.dataset.node = node.id;
        const label = nodeLabel(node);
        const category = !ch(node).length && label !== node.type ? ` (${node.type})` : '';
        button.textContent = label + category
          + (node.edgeResult?.status === 'error' ? ' · flagged for review' : '');
        button.addEventListener('click', () => this.onSelect(node.id));
        item.append(button);
        if (ch(node).length) item.append(list(ch(node)));
        ul.append(item);
      }
      return ul;
    };
    body.append(list([this.tree]));
  }

  setInteractive(flag) {
    this.interactive = flag !== false;
    if (!this.interactive) {
      this.hoverId = null;
      this.canvas.style.cursor = 'default';
      this.draw();
    }
  }

  clear() {
    this.tree = null;
    this.layoutData = null;
    this.dfsOrder = [];
    this.indexById = new Map();
    this.selectedId = null;
    this.hoverId = null;
    this.focus = null;
    this.view = { scale: 1, tx: 0, ty: 0 };
    this._renderOutline();
    this.draw();
  }

  _fitTarget() {
    const w = this.canvas.clientWidth || this.canvas.width;
    const h = this.canvas.clientHeight || this.canvas.height;
    // No room to draw (the canvas is hidden or has no size yet): don't
    // squeeze the tree into a corner — fit it again when there is space.
    if (!w || !h) {
      this.needsFit = true;
      return;
    }
    const pad = Math.min(24, w / 8, h / 8);
    const raw = Math.min((w - pad * 2) / this.layoutData.totalW, (h - pad * 2) / this.layoutData.totalH, 1.7);
    const scale = Math.max(Math.min(raw, 1.7), 0.2);
    return {
      scale,
      tx: (w - this.layoutData.totalW * scale) / 2,
      ty: (h - this.layoutData.totalH * scale) / 2,
    };
  }

  _fitView() {
    const target = this._fitTarget();
    if (!target) return;
    this.view = target;
    this.needsFit = false;
  }

  _layoutTree(width) {
    this.compact = width < 600;
    this.layoutData = createLayout(this.tree, label => this._measure(label), width);
  }

  _resize() {
    const dpr = window.devicePixelRatio || 1;
    const w = this.canvas.clientWidth;
    const h = this.canvas.clientHeight;
    if (!w || !h) {
      // The canvas has no size (it is hidden): keep the backing store and
      // remember that the tree still has to be fitted.
      this.needsFit = true;
      return;
    }
    this.canvas.width = Math.round(w * dpr);
    this.canvas.height = Math.round(h * dpr);
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (this.tree) {
      // A canvas that had no size could not be fitted: fit it now that it is
      // back, so the tree is centred instead of squished.
      const relayout = !this.focus && this.compact !== (w < 600);
      if (relayout) this._layoutTree(w);
      if (this.needsFit || relayout) this._fitView();
      this.draw();
    }
  }

  _toWorld(p) {
    return { x: (p.x - this.view.tx) / this.view.scale, y: (p.y - this.view.ty) / this.view.scale };
  }

  hitTest(mx, my) {
    return this.layoutData ? this._hitTest(mx, my) : null;
  }

  _hitTest(mx, my) {
    const w = this._toWorld({ x: mx, y: my });
    let best = null;
    for (const l of this.layoutData.layout.values()) {
      const halfW = (l.w + 8) / 2;
      const halfH = (l.h + 8) / 2;
      if (Math.abs(w.x - l.x) <= halfW && Math.abs(w.y - l.y) <= halfH) {
        if (!best || l.y > best.y) best = l;
      }
    }
    return best ? best.id : null;
  }

  _onDown(e) {
    const rect = this.canvas.getBoundingClientRect();
    this._drag = {
      startX: e.clientX,
      startY: e.clientY,
      baseTx: this.view.tx,
      baseTy: this.view.ty,
      moved: false,
      mouseX: e.clientX - rect.left,
      mouseY: e.clientY - rect.top,
    };
  }

  _onMove(e) {
    const rect = this.canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    if (this._drag) {
      const dx = e.clientX - this._drag.startX;
      const dy = e.clientY - this._drag.startY;
      if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
        this._drag.moved = true;
        this.view.tx = this._drag.baseTx + dx;
        this.view.ty = this._drag.baseTy + dy;
        this.draw();
      }
    } else if (this.interactive) {
      const id = this.layoutData ? this._hitTest(mx, my) : null;
      this.hoverX = mx;
      this.hoverY = my;
      if (id !== this.hoverId) {
        this.hoverId = id;
        this.canvas.style.cursor = id ? 'pointer' : 'default';
        this.onHover(id);
        this.draw();
      } else {
        this.draw();
      }
    }
  }

  _onUp() {
    if (this._drag && !this._drag.moved && this.layoutData && this.interactive) {
      const id = this._hitTest(this._drag.mouseX, this._drag.mouseY);
      this.onSelect(id);
    }
    this._drag = null;
  }

  _onLeave() {
    this.hoverId = null;
    this.draw();
  }

  zoom(factor) {
    if (!this.tree) return;
    const x = this.canvas.clientWidth / 2;
    const y = this.canvas.clientHeight / 2;
    const point = this._toWorld({ x, y });
    const scale = Math.min(5, Math.max(0.2, this.view.scale * factor));
    this._animateTo({ scale, tx: x - point.x * scale, ty: y - point.y * scale }, 180);
  }

  _onWheel(e) {
    e.preventDefault();
    const rect = this.canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const factor = e.deltaY > 0 ? 0.9 : 1.1;
    const world = this._toWorld({ x: mx, y: my });
    const newScale = Math.min(Math.max(this.view.scale * factor, 0.15), 3);
    this.view.scale = newScale;
    this.view.tx = mx - world.x * this.view.scale;
    this.view.ty = my - world.y * this.view.scale;
    this.draw();
  }

  draw() {
    const ctx = this.ctx;
    const w = this.canvas.clientWidth || this.canvas.width;
    const h = this.canvas.clientHeight || this.canvas.height;
    ctx.clearRect(0, 0, w, h);
    if (!this.layoutData) {
      return;
    }
    ctx.save();
    ctx.translate(this.view.tx, this.view.ty);
    ctx.scale(this.view.scale, this.view.scale);

    if (this.selectedId) {
      const selected = this.layoutData.layout.get(this.selectedId);
      const range = this.layoutData.bounds.get(this.selectedId);
      if (selected && range) {
        const yTop = selected.y - BOX_H / 2 - 8;
        ctx.fillStyle = 'rgba(255, 217, 77, 0.16)';
        ctx.fillRect(range.left - 8, yTop, range.right - range.left + 16, this.layoutData.totalH - yTop + 8);
      }
    }

    for (const l of this.layoutData.layout.values()) {
      for (const c of ch(l.node)) {
        const cl = this.layoutData.layout.get(c.id);
        const status = c.edgeResult ? c.edgeResult.status : 'neutral';
        const gap = cl.leaf ? 23 : LABEL_GAP;
        // While a correction is focused, everything outside the error's scope
        // fades back so the rule and its linked nodes stand out.
        const dimEdge = this.focus
          && !(this.focus.inScope.has(c.id) && this.focus.inScope.has(l.node.id));
        ctx.globalAlpha = dimEdge ? 0.12 : 1;
        ctx.strokeStyle = this._edgeColor(status);
        ctx.lineWidth = 1.5;
        ctx.setLineDash(status === 'error' ? [5, 4] : []);
        ctx.beginPath();
        ctx.moveTo(l.x, l.y + LABEL_GAP);
        ctx.lineTo(cl.x, cl.y - gap);
        ctx.stroke();
      }
    }
    ctx.globalAlpha = 1;
    ctx.setLineDash([]);

    for (const l of this.layoutData.layout.values()) {
      this._drawNode(l);
    }

    ctx.restore();
    this._drawTooltip();
  }

  _drawTooltip() {
    if (!this.hoverId || !this.layoutData) return;
    const l = this.layoutData.layout.get(this.hoverId);
    if (!l) return;
    const meaning = this.describe(l.node.type);
    if (!meaning || meaning === l.node.type) return;
    const label = meaning;
    const ctx = this.ctx;
    const w = this.canvas.clientWidth || this.canvas.width;
    const h = this.canvas.clientHeight || this.canvas.height;
    ctx.font = '600 12px system-ui, sans-serif';
    const tw = ctx.measureText(label).width;
    const padX = 10;
    const padY = 7;
    const bw = tw + padX * 2;
    const bh = 26;
    let bx = this.hoverX + 14;
    let by = this.hoverY + 16;
    bx = Math.min(Math.max(bx, 6), w - bw - 6);
    by = Math.min(Math.max(by, 6), h - bh - 6);
    ctx.save();
    ctx.fillStyle = 'rgba(22, 17, 43, 0.93)';
    ctx.beginPath();
    ctx.roundRect(bx, by, bw, bh, 8);
    ctx.fill();
    ctx.fillStyle = '#f2efff';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(label, bx + padX, by + bh / 2);
    ctx.restore();
  }

  _edgeColor(status) {
    const colors = getThemeColors();
    if (status === 'error') return colors.edgeError;
    if (status === 'valid') return colors.edgeValid;
    return colors.edge;
  }

  _drawNode(l) {
    const ctx = this.ctx;
    const n = l.node;
    const colors = getThemeColors();
    const isRoot = this.layoutData.root === n;
    const isSel = n.id === this.selectedId;
    const isHov = n.id === this.hoverId;
    const err = n.edgeResult && n.edgeResult.status === 'error';
    // Nodes outside the focused scope fade back; the pair the rule links
    // together is painted in the error colour.
    const dim = this.focus && !this.focus.inScope.has(n.id);
    const paired = this.focus && this.focus.pair.includes(n.id);

    ctx.save();
    if (dim) ctx.globalAlpha = 0.18;

    let color = err ? colors.edgeError : colors.text;
    if (isRoot) color = colors.nodeStroke;
    if (isHov) color = colors.nodeStroke;
    if (paired) color = colors.edgeError;
    if (isSel) color = colors.selectedStroke;

    ctx.fillStyle = color;
    if (ch(n).length === 0) {
      ctx.font = paired ? '700 15px Inter, system-ui, sans-serif' : '500 15px Inter, system-ui, sans-serif';
    } else {
      ctx.font = (isSel || paired) ? '700 16px Inter, system-ui, sans-serif' : '600 16px Inter, system-ui, sans-serif';
    }
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(nodeLabel(n), l.x, l.y + 3);

    if (ch(n).length === 0) {
      ctx.fillStyle = colors.edgeText;
      ctx.font = '600 10px Inter, system-ui, sans-serif';
      ctx.fillText(n.type, l.x, l.y - 14);
    }
    ctx.restore();
  }

  _animateTo(target, ms = 380) {
    cancelAnimationFrame(this._raf);
    if (!target) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      this.view = target;
      this.draw();
      return;
    }
    const from = { ...this.view };
    const t0 = performance.now();
    const step = (now) => {
      const k = Math.min(1, (now - t0) / ms);
      const e = 1 - (1 - k) ** 3;
      this.view.scale = from.scale + (target.scale - from.scale) * e;
      this.view.tx = from.tx + (target.tx - from.tx) * e;
      this.view.ty = from.ty + (target.ty - from.ty) * e;
      this.draw();
      if (k < 1) this._raf = requestAnimationFrame(step);
    };
    this._raf = requestAnimationFrame(step);
  }

  /** Zoom to the subtree rooted at scopeId; pairIds are linked with a dashed red curve. */
  focusSubtree(scopeId, pairIds = []) {
    const L = this.layoutData;
    const sl = L && L.layout.get(scopeId);
    if (!sl) return false;
    const inScope = new Set();
    let maxY = sl.y;
    const walk = (n) => {
      inScope.add(n.id);
      const l = L.layout.get(n.id);
      if (l) maxY = Math.max(maxY, l.y);
      for (const c of ch(n)) walk(c);
    };
    walk(sl.node);
    const { left: x0, right: x1 } = L.bounds.get(scopeId);
    const y0 = sl.y - BOX_H / 2 - 12;
    const y1 = maxY + 80; // word + POS tag + room for the pair link
    const w = this.canvas.clientWidth || this.canvas.width;
    const h = this.canvas.clientHeight || this.canvas.height;
    const pad = 40;
    const scale = Math.max(Math.min((w - pad * 2) / (x1 - x0), (h - pad * 2) / (y1 - y0), 2), 0.2);
    this.focus = { scopeId, inScope, pair: pairIds.filter((id) => L.layout.has(id)) };
    this._animateTo({
      scale,
      tx: w / 2 - ((x0 + x1) / 2) * scale,
      ty: h / 2 - ((y0 + y1) / 2) * scale,
    });
    return true;
  }

  /** Center and emphasize an error node without reducing the current zoom. */
  focusNode(nodeId, scopeId, pairIds = []) {
    const L = this.layoutData;
    const target = L && L.layout.get(nodeId);
    if (!target) return false;
    const inScope = new Set();
    const scopeNode = scopeId && L.layout.get(scopeId) ? L.layout.get(scopeId).node : null;
    const walk = (n) => {
      inScope.add(n.id);
      for (const c of n.children || []) walk(c);
    };
    if (scopeNode) walk(scopeNode);
    else inScope.add(nodeId);
    const w = this.canvas.clientWidth || this.canvas.width;
    const h = this.canvas.clientHeight || this.canvas.height;

    // The error and the node(s) the rule links it to must stay on screen —
    // that link is the whole point of the zoom — so the view is fitted to
    // their range instead of to the whole tree.
    const wanted = [nodeId, ...pairIds].filter((id) => L.layout.has(id));
    let lo = Infinity;
    let hi = -Infinity;
    let top = Infinity;
    let bottom = -Infinity;
    for (const id of wanted) {
      const range = L.bounds.get(id);
      const l = L.layout.get(id);
      if (range) { lo = Math.min(lo, range.left); hi = Math.max(hi, range.right); }
      if (l) { top = Math.min(top, l.y); bottom = Math.max(bottom, l.y); }
    }
    if (!Number.isFinite(lo)) { lo = 0; hi = 0; }
    if (!Number.isFinite(top)) { top = target.y; bottom = target.y; }
    const pad = 64;
    const x0 = lo - pad;
    const x1 = hi + pad;
    const y0 = top - BOX_H / 2 - pad / 2;
    const y1 = bottom + BOX_H / 2 + pad / 2;
    const scale = Math.max(Math.min((w - 24) / (x1 - x0), (h - 24) / (y1 - y0), 2.6), 0.35);
    this.focus = { scopeId: scopeId || nodeId, inScope, pair: pairIds.filter((id) => L.layout.has(id)) };
    this._animateTo({
      scale,
      tx: w / 2 - ((x0 + x1) / 2) * scale,
      ty: h / 2 - ((y0 + y1) / 2) * scale,
    });
    return true;
  }

  clearFocus() {
    this.focus = null;
    if (this.layoutData) this._animateTo(this._fitTarget());
  }
}