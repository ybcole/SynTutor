// Syntax Builder core: a free-form node-graph model for building syntax trees
// by hand. Unlike SynTutor's read-only tree, here the learner arranges nodes on
// a canvas: word boxes they type, and phrase boxes (NP, VP, S, ...) they create
// from a right-click menu. Phrase nodes expose a small connector dot; dragging
// from a dot draws a link that attaches a word or another phrase as a child.
//
// The model is DOM-free so it can be unit-tested and reused by the Matrix Quiz
// (which asks the learner to rebuild SynTutor's tree for a target sentence and
// then compares the result against the gold parse).

// Every phrase label benepar can emit, grouped for the palette.
export const PHRASE_NODE_TYPES = [
  'S', 'NP', 'VP', 'PP', 'ADJP', 'ADVP',
  'SBAR', 'SBARQ', 'SINV', 'SQ', 'FRAG',
  'NML', 'WHNP', 'WHADVP', 'WHADJP', 'WHPP',
  'QP', 'NX', 'CONJP', 'UCP', 'LST', 'X',
  'INTJ', 'PRT',
];

// Lexical (part-of-speech) tags, usable as leaf labels.
export const POS_TYPES = [
  'CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD',
  'NN', 'NNS', 'NNP', 'NNPS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR',
  'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP',
  'VBZ', 'WDT', 'WP', 'WP$', 'WRB', '#', '$', '.', ',', ':', ';', '(',
  ')', '"', "'", '-NONE-', 'HYPH',
];

export const NODE_TYPE_GROUPS = [
  { name: 'Clauses', types: ['S', 'SBAR', 'SQ', 'SINV', 'SBARQ', 'FRAG'] },
  { name: 'Arguments', types: ['NP', 'VP'] },
  { name: 'Modifiers', types: ['PP', 'ADVP', 'ADJP'] },
  { name: 'Wh-words', types: ['WHNP', 'WHADVP', 'WHADJP', 'WHPP'] },
  { name: 'Coordination & misc', types: ['NML', 'QP', 'NX', 'CONJP', 'UCP', 'LST', 'INTJ', 'PRT', 'X'] },
];

export const NODE = { WORD: 'word', PHRASE: 'phrase' };

let counter = 0;
export function nextId() {
  counter += 1;
  return `n${counter}`;
}
export function resetIds() {
  counter = 0;
}

// Default box sizes; the UI overrides with real text measurement.
const WORD_W = 84;
const PHRASE_W = 58;
const NODE_H = 32;
const DOT_R = 5;

export function createModel() {
  return { nodes: {}, counter: 0 };
}

function put(model, node) {
  model.nodes[node.id] = node;
  return node;
}

export function addWord(model, text, x, y) {
  const t = String(text || '').trim();
  return put(model, {
    id: nextId(), kind: NODE.WORD, type: 'word', text: t,
    x, y, w: WORD_W, h: NODE_H, parent: null,
    valid: true, suggestion: null, tag: null,
  });
}

export function addPhrase(model, type, x, y) {
  return put(model, {
    id: nextId(), kind: NODE.PHRASE, type: type || 'NP', text: '',
    x, y, w: PHRASE_W, h: NODE_H, parent: null,
  });
}

// Split free text into tokens the way SynTutor's tokenizer would (words,
// numbers, and single punctuation marks kept separate).
export function tokenise(text) {
  return (String(text || '').match(/[A-Za-z]+(?:'[A-Za-z]+)?|[0-9]+(?:[.,][0-9]+)*|[^\sA-Za-z0-9]/g)) || [];
}

// Create one word node per token, laid out in a row starting at (x, y).
export function addWordsFromText(model, text, x, y, gap = 12) {
  const toks = tokenise(text);
  const made = [];
  let cursor = x;
  for (const tok of toks) {
    const n = addWord(model, tok, cursor, y);
    made.push(n);
    cursor += n.w + gap;
  }
  return made;
}

export function moveNode(model, id, x, y) {
  const n = model.nodes[id];
  if (!n) return null;
  n.x = x;
  n.y = y;
  return n;
}

export function setType(model, id, type) {
  const n = model.nodes[id];
  if (!n) return null;
  n.type = type;
  return n;
}

export function removeNode(model, id) {
  const n = model.nodes[id];
  if (!n) return false;
  // Detach children (they become roots again).
  for (const other of Object.values(model.nodes)) {
    if (other.parent === id) other.parent = null;
  }
  delete model.nodes[id];
  return true;
}

export function childrenOf(model, id) {
  return Object.values(model.nodes)
    .filter((n) => n.parent === id)
    .sort((a, b) => a.x - b.x);
}

export function roots(model) {
  return Object.values(model.nodes).filter((n) => !n.parent);
}

// Would attaching child under parent create a cycle? (parent is a descendant
// of child.) Also rejects self-links.
//
// The builder is intentionally permissive: any node may connect to any other
// node, even if the combination is not a valid constituency. A word like NNP
// can be a parent, and a word SynTutor doesn't recognise can be a child — the
// tree still gets built so the builder stays functional.
export function canConnect(model, parentId, childId) {
  if (parentId === childId) return false;
  const parent = model.nodes[parentId];
  const child = model.nodes[childId];
  if (!parent || !child) return false;
  let cur = parent;
  while (cur) {
    if (cur.id === childId) return false;
    cur = cur.parent ? model.nodes[cur.parent] : null;
  }
  return true;
}

export function connect(model, parentId, childId) {
  if (!canConnect(model, parentId, childId)) return false;
  model.nodes[childId].parent = parentId;
  return true;
}

export function disconnect(model, childId) {
  const n = model.nodes[childId];
  if (!n || !n.parent) return false;
  n.parent = null;
  return true;
}

// Connector dot: bottom-centre of a phrase box (drag it to start a new link).
export function dotOf(node) {
  return { x: node.x + node.w / 2, y: node.y + node.h + DOT_R + 1, r: DOT_R };
}

export function dotHit(model, x, y) {
  for (const n of Object.values(model.nodes)) {
    if (n.kind !== NODE.PHRASE) continue;
    const d = dotOf(n);
    // Generous hit area so clicking just below a phrase box starts a link
    // instead of dragging the box.
    if (Math.hypot(x - d.x, y - d.y) <= d.r + 12) return n;
  }
  return null;
}

// Endpoint: top-centre of a box, where an existing parent edge meets it. Drag
// it to re-attach the connection to a different parent, or drop it on empty
// space (or click it) to remove the connection.
export function endpointOf(node) {
  return { x: node.x + node.w / 2, y: node.y, r: DOT_R };
}

export function endpointHit(model, x, y) {
  const list = Object.values(model.nodes);
  for (let i = list.length - 1; i >= 0; i -= 1) {
    const n = list[i];
    if (!n.parent) continue;
    const p = endpointOf(n);
    if (Math.hypot(x - p.x, y - p.y) <= p.r + 4) return n;
  }
  return null;
}

export function nodeHit(model, x, y) {
  const list = Object.values(model.nodes);
  for (let i = list.length - 1; i >= 0; i -= 1) {
    const n = list[i];
    if (x >= n.x && x <= n.x + n.w && y >= n.y && y <= n.y + n.h) return n;
  }
  return null;
}

// Flatten a nested tree into its leaves with their surface word and POS tag.
export function leavesWithTags(tree) {
  const out = [];
  const walk = (n) => {
    if (!n) return;
    if (n.leaf || !n.children || n.children.length === 0) {
      out.push({ surface: n.surface ?? '', tag: n.type });
      return;
    }
    n.children.forEach(walk);
  };
  walk(tree);
  return out;
}

// Seed the model with one word box per gold leaf, laid out in a row. When
// ``withTags`` is set the official POS tag is attached to each word (used by
// the phrase/full-tree lessons where tagging is already taught).
export function seedWords(model, leaves, x, y, withTags = false, gap = 12) {
  const made = [];
  let cursor = x;
  for (const leaf of leaves) {
    const node = addWord(model, leaf.surface, cursor, y);
    if (withTags && leaf.tag) node.tag = leaf.tag;
    node.valid = true;
    made.push(node);
    cursor += node.w + gap;
  }
  return made;
}

// Turn the graph into a nested tree rooted at `rootId` (or the best guess when
// omitted): leaves ordered left-to-right by x. Returns null when `rootId` is a
// word or missing.
export function toTree(model, rootId) {
  let root = rootId ? model.nodes[rootId] : guessRoot(model);
  if (!root || root.kind !== NODE.PHRASE) return null;
  const build = (node) => {
    const kids = childrenOf(model, node.id);
    if (node.kind === NODE.WORD || kids.length === 0) {
      return { type: node.kind === NODE.WORD ? node.type : node.type, surface: node.text, leaf: true, x: node.x };
    }
    const children = kids.map(build);
    const ordered = [...children].sort((a, b) => a.x - b.x);
    return { type: node.type, children: ordered.map(clean), x: node.x };
  };
  const clean = (n) => {
    const out = { type: n.type };
    if (n.leaf) {
      out.surface = n.surface;
      out.leaf = true;
    } else {
      out.children = n.children;
    }
    return out;
  };
  return clean(build(root));
}

function guessRoot(model) {
  const rs = roots(model).filter((n) => n.kind === NODE.PHRASE);
  if (!rs.length) return null;
  const s = rs.find((n) => /^(S|SBAR|SQ|SINV|SBARQ)$/.test(n.type));
  return s || rs[0];
}

// Leaf text order for a tree, left-to-right.
export function leavesOf(tree) {
  if (!tree) return [];
  if (tree.leaf || !tree.children) return [tree.surface ?? ''];
  return tree.children.flatMap(leavesOf);
}

// Structural comparison against a gold tree (SynTutor's parse, already reduced
// to {type, children:[...]} / {type, leaf, surface} form). Returns matched /
// missing / extra phrase spans so the quiz can give precise feedback.
export function compareTrees(userTree, goldTree) {
  const gold = phraseSpans(goldTree);
  const user = phraseSpans(userTree);
  const key = (s) => `${s.type}[${s.start}-${s.end}]`;
  const gset = new Map(gold.map((s) => [key(s), s]));
  const uset = new Map(user.map((s) => [key(s), s]));
  const matched = [];
  const missing = [];
  const extra = [];
  for (const [k, s] of gset) (uset.has(k) ? matched : missing).push(s);
  for (const [k, s] of uset) if (!gset.has(k)) extra.push(s);
  return {
    correct: missing.length === 0 && extra.length === 0,
    matched, missing, extra,
  };
}

// Every phrase node's {type, start, end} span in leaf order. Leaf nodes are the
// unit of width; spans are computed in one recursive pass.
export function phraseSpans(tree) {
  const out = [];
  let cursor = 0;
  const walk = (node) => {
    if (!node || node.leaf || !node.children || node.children.length === 0) {
      const start = cursor;
      cursor += 1;
      return { start, end: cursor };
    }
    const start = cursor;
    for (const child of node.children) walk(child);
    out.push({ type: node.type, start, end: cursor });
    return { start, end: cursor };
  };
  if (tree) walk(tree);
  return out;
}

// Compare the leaf text sequence so the quiz can flag a wrong sentence.
export function leafText(tree) {
  return leavesOf(tree).join(' ');
}
