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
const GAP = 26;
const V_GAP = 40;
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

export function createLayout(root, measure) {
  const nodes = collectNodes(root);
  const leafNodes = [];
  const nodeDepth = new Map();
  let maxDepth = 0;

  const walk = (nd, depth) => {
    maxDepth = Math.max(maxDepth, depth);
    nodeDepth.set(nd.id, depth);
    if (ch(nd).length === 0) {
      leafNodes.push(nd);
    }
    for (const c of ch(nd)) walk(c, depth + 1);
  };
  walk(root, 0);

  const leafIndex = new Map();
  leafNodes.forEach((lf, i) => leafIndex.set(lf.id, i));

  let maxLeafW = MIN_BOX_W;
  for (const lf of leafNodes) {
    maxLeafW = Math.max(maxLeafW, measure(nodeLabel(lf)) + H_PAD * 2);
  }
  const SLOT = maxLeafW + GAP;

  const span = new Map();
  const collectSpan = (nd) => {
    if (span.has(nd.id)) return span.get(nd.id);
    if (ch(nd).length === 0) {
      const i = leafIndex.get(nd.id);
      const s = [i, i];
      span.set(nd.id, s);
      return s;
    }
    let lo = Infinity;
    let hi = -Infinity;
    for (const c of ch(nd)) {
      const cs = collectSpan(c);
      lo = Math.min(lo, cs[0]);
      hi = Math.max(hi, cs[1]);
    }
    const s = [lo, hi];
    span.set(nd.id, s);
    return s;
  };
  collectSpan(root);

  const layout = new Map();
  for (const n of nodes) {
    const depth = nodeDepth.get(n.id) || 0;
    const y = TOP_PAD + depth * (BOX_H + V_GAP) + BOX_H / 2;
    if (ch(n).length === 0) {
      const i = leafIndex.get(n.id);
      layout.set(n.id, {
        id: n.id,
        node: n,
        x: SLOT * i + SLOT / 2,
        y,
        w: SLOT,
        h: BOX_H,
        leaf: true,
      });
    } else {
      const s = span.get(n.id);
      const x = ((s[0] + s[1]) / 2 + 0.5) * SLOT;
      const w = (s[1] - s[0] + 1) * SLOT;
      layout.set(n.id, {
        id: n.id,
        node: n,
        x,
        y,
        w,
        h: BOX_H,
        leaf: false,
      });
    }
  }

  const totalW = Math.max(leafNodes.length * SLOT + SIDE_PAD * 2, 320);
  const totalH = Math.max(TOP_PAD + maxDepth * (BOX_H + V_GAP) + BOX_H + SIDE_PAD * 2, 160);

  return {
    layout,
    totalW,
    totalH,
    maxDepth,
    nodes,
    leaves: leafNodes,
    root,
    span,
    slot: SLOT,
  };
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
    this.describe = opts.describe || (() => null);
    this.tree = null;
    this.layoutData = null;
    this.view = { scale: 1, tx: 0, ty: 0 };
    this.selectedId = null;
    this.hoverId = null;
    this.hoverX = 0;
    this.hoverY = 0;
    this._drag = null;
    this.dfsOrder = [];
    this.indexById = new Map();
    this._setup();
    this._resize();
  }

  _setup() {
    this.canvas.addEventListener('mousedown', (e) => this._onDown(e));
    this.canvas.addEventListener('mousemove', (e) => this._onMove(e));
    this.canvas.addEventListener('mouseup', () => this._onUp());
    this.canvas.addEventListener('mouseleave', () => this._onLeave());
    this.canvas.addEventListener('wheel', (e) => this._onWheel(e), { passive: false });
    this.canvas.addEventListener('keydown', (e) => this._onKey(e));
    window.addEventListener('resize', () => this._resize());
  }

  _onKey(e) {
    if (!this.tree) return;
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
    this.tree = root;
    this.layoutData = createLayout(root, (label) => this._measure(label));
    this.dfsOrder = collectNodes(root).map((n) => n.id);
    this.indexById = new Map(this.dfsOrder.map((id, i) => [id, i]));
    this.selectedId = null;
    this._fitView();
    this.draw();
  }

  select(id) {
    this.selectedId = id;
    this.draw();
  }

  clear() {
    this.tree = null;
    this.layoutData = null;
    this.dfsOrder = [];
    this.indexById = new Map();
    this.selectedId = null;
    this.hoverId = null;
    this.view = { scale: 1, tx: 0, ty: 0 };
    this.draw();
  }

  _fitView() {
    const w = this.canvas.clientWidth || this.canvas.width;
    const h = this.canvas.clientHeight || this.canvas.height;
    const pad = 30;
    const scale = Math.min((w - pad * 2) / this.layoutData.totalW, (h - pad * 2) / this.layoutData.totalH, 1.7) * 1.25;
    this.view.scale = Math.max(Math.min(scale, 1.7), 0.2);
    this.view.tx = (w - this.layoutData.totalW * this.view.scale) / 2;
    this.view.ty = (h - this.layoutData.totalH * this.view.scale) / 2;
  }

  _resize() {
    const dpr = window.devicePixelRatio || 1;
    const w = this.canvas.clientWidth;
    const h = this.canvas.clientHeight;
    if (!w || !h) return;
    this.canvas.width = Math.round(w * dpr);
    this.canvas.height = Math.round(h * dpr);
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    if (this.tree) this.draw();
  }

  _toWorld(p) {
    return { x: (p.x - this.view.tx) / this.view.scale, y: (p.y - this.view.ty) / this.view.scale };
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
    } else {
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
    if (this._drag && !this._drag.moved && this.layoutData) {
      const id = this._hitTest(this._drag.mouseX, this._drag.mouseY);
      this.onSelect(id);
    }
    this._drag = null;
  }

  _onLeave() {
    this.hoverId = null;
    this.draw();
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
      const selSpan = this.layoutData.span.get(this.selectedId);
      if (selSpan) {
        const lo = this.layoutData.leaves[selSpan[0]];
        const hi = this.layoutData.leaves[selSpan[1]];
        const ll = this.layoutData.layout.get(lo.id);
        const hl = this.layoutData.layout.get(hi.id);
        if (ll && hl) {
          const x0 = ll.x - ll.w / 2 - 8;
          const x1 = hl.x + hl.w / 2 + 8;
          const yTop = (this.layoutData.layout.get(this.selectedId) || { y: TOP_PAD }).y - BOX_H / 2 - 8;
          ctx.fillStyle = 'rgba(255, 217, 77, 0.16)';
          ctx.fillRect(x0, yTop, x1 - x0, this.layoutData.totalH - yTop + 8);
        }
      }
    }

    for (const l of this.layoutData.layout.values()) {
      for (const c of ch(l.node)) {
        const cl = this.layoutData.layout.get(c.id);
        const status = c.edgeResult ? c.edgeResult.status : 'valid';
        const gap = cl.leaf ? 36 : LABEL_GAP;
        ctx.strokeStyle = this._edgeColor(status);
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(l.x, l.y + LABEL_GAP);
        ctx.lineTo(cl.x, cl.y - gap);
        ctx.stroke();
      }
    }

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

    let color = err ? colors.edgeError : colors.text;
    if (isRoot) color = colors.nodeStroke;
    if (isHov) color = colors.nodeStroke;
    if (isSel) color = colors.selectedStroke;

    ctx.fillStyle = color;
    if (ch(n).length === 0) {
      ctx.font = '500 15px Inter, system-ui, sans-serif';
    } else {
      ctx.font = isSel ? '700 16px Inter, system-ui, sans-serif' : '600 16px Inter, system-ui, sans-serif';
    }
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(nodeLabel(n), l.x, l.y + 3);

    if (ch(n).length === 0) {
      ctx.fillStyle = colors.edgeText;
      ctx.font = '600 10px Inter, system-ui, sans-serif';
      ctx.fillText(n.type, l.x, l.y - 14);
    }
  }
}