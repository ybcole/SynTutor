// Zoom-scope lookup (keyed by constraint id), pair linking, edit application,
// and error re-identification by constraint + surrounding words.

const NOUNISH = new Set(['NN', 'NNS', 'NNP', 'NNPS', 'PRP', 'NML', 'NX']);
const VERBISH = new Set(['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD', 'AUX']);
const POSS = new Set(['my', 'your', 'our', 'their', 'its']);
const lower = (s) => (s || '').toLowerCase();
const leavesOf = (n) => (n.children && n.children.length ? n.children.flatMap(leavesOf) : [n]);

function npHead(np) {
  if (!np) return null;
  const ls = leavesOf(np).filter((l) => NOUNISH.has(l.type) && !POSS.has(lower(l.surface)));
  return ls[ls.length - 1] || null;
}
const firstVerb = (n) => (n ? leavesOf(n).find((l) => VERBISH.has(l.type)) || null : null);
const subjectNP = (s) => (s && s.children ? s.children.find((c) => c.type === 'NP') || null : null);

function followingVerb(parent, aux) {
  if (!parent) return null;
  for (const c of parent.children || []) {
    if (c.id === aux.id) continue;
    const lf = leavesOf(c)[0];
    if (lf && VERBISH.has(lf.type)) return lf;
  }
  return null;
}

// c = { node, parent, grandparent } (the flagged node, its parent and grandparent)
// scope: 'parent' (default) | 'self' | fn(c) -> node       pair: fn(c) -> [leaf|node, ...]
export const SCOPE_TABLE = {
  'C-SUBJECT-AGREEMENT': { label: 'Subject\u2013verb agreement',
    pair: (c) => [npHead(subjectNP(c.parent)), firstVerb(c.node)] },
  'C-DETERMINER-AGREEMENT': { label: 'Determiner\u2013noun agreement',
    pair: (c) => [c.node, npHead(c.parent)] },
  'C-NOUN-FORM': { label: 'Noun form', pair: (c) => [c.node] },
  'C-AUX-FORM': { label: 'Auxiliary verb form',
    pair: (c) => [c.node, followingVerb(c.parent, c.node)] },
  'C-VERB-FORM': { label: 'Verb form',
    pair: (c) => [c.node, followingVerb(c.parent, c.node)] },
  'C-DET-STACK': { label: 'Stacked determiners',
    pair: (c) => (c.parent.children || []).filter((x) => x.type === 'DT' || x.type === 'PRP$').slice(0, 2) },
  'C-MOD-POS': { label: 'Modifier position', pair: (c) => [c.node, npHead(c.parent)] },
  'C-PRONOUN-CASE': { label: 'Pronoun case',
    pair: (c) => {
      if (c.node.type === 'VP') return [npHead(subjectNP(c.parent)), firstVerb(c.node)];
      const gov = c.parent.type === 'PP' ? leavesOf(c.parent)[0] : firstVerb(c.parent);
      return [npHead(c.node), gov];
    } },
  'C-ADJ-ADV': { label: 'Adjective vs. adverb',
    scope: (c) => (c.parent && c.parent.type === 'ADVP' && c.grandparent ? c.grandparent : c.parent),
    pair: (c) => {
      const vp = c.parent && c.parent.type === 'ADVP' ? c.grandparent : c.parent;
      const ls = leavesOf(c.node);
      return [ls[ls.length - 1], firstVerb(vp)];
    } },
  'C-ARTICLE': { label: 'Missing article', pair: (c) => [c.node] },
  'C-ARTICLE-MISMATCH': { label: 'a / an',
    pair: (c) => {
      const ls = leavesOf(c.parent);
      const i = ls.findIndex((l) => l.id === c.node.id);
      return [c.node, ls[i + 1]];
    } },
  'C-CAPITALIZATION': { label: 'Capitalization', scope: 'self', pair: (c) => [leavesOf(c.node)[0]] },
  'C-QUANTIFIER': { label: 'Quantifier\u2013noun agreement', pair: (c) => [c.node, npHead(c.parent)] },
  'C-COMPARATIVE-DOUBLE': { label: 'Double comparative',
    pair: (c) => [c.node, (c.parent.children || []).find((x) => x.type === 'JJR' || x.type === 'JJS')] },
  'C-HEAD-NOUN': { label: 'Missing noun', pair: (c) => [c.node] },
  'C-HEAD-VERB': { label: 'Missing verb', pair: (c) => [c.node] },
  'C-TENSE-FINITE': { label: 'Finite verb required',
    scope: (c) => (c.parent ? c.parent : c.node),
    pair: (c) => (c.node.type === 'VP' ? [firstVerb(c.node)] : []) },
};
const DEFAULT_RULE = { label: 'Grammar error', pair: () => [] };

export function planFocus(payload, id) {
  const details = payload.node_details;
  const detail = details[id];
  const node = payload.nodes[id];
  const parent = detail.parent ? payload.nodes[detail.parent] : null;
  const gpId = parent ? details[parent.id]?.parent : null;
  const grandparent = gpId ? payload.nodes[gpId] : null;
  const rule = SCOPE_TABLE[detail.constraint] || DEFAULT_RULE;
  const c = { node, parent, grandparent };
  let scope;
  if (typeof rule.scope === 'function') scope = rule.scope(c);
  else if (rule.scope === 'self') scope = node;
  else scope = parent;
  if (!scope) scope = node;
  const pair = [...new Set((rule.pair ? rule.pair(c) : []).filter(Boolean).map((n) => n.id))];
  return { nodeId: id, scopeId: scope.id, scopeType: scope.type, label: rule.label, pair };
}

// ---- surrounding-word context (used to re-find the error after an edit) ----
export function contextWords(payload, scopeId, pad = 2) {
  const node = payload.nodes[scopeId];
  const toks = payload.parse.tokens;
  if (!node) return [];
  const lo = Math.max(0, node.span[0] - pad);
  const hi = Math.min(toks.length, node.span[1] + pad);
  return toks.slice(lo, hi).map((t) => lower(t.t)).filter((w) => /\w/.test(w));
}

function overlap(a, b) {
  const A = new Set(a);
  const B = new Set(b);
  if (!A.size || !B.size) return 0;
  let inter = 0;
  A.forEach((w) => { if (B.has(w)) inter += 1; });
  return inter / Math.min(A.size, B.size);
}

// Re-identify the targeted error by constraint id + surrounding words (never node id).
export function findTargetError(payload, focus) {
  let best = null;
  for (const d of Object.values(payload.node_details)) {
    if (d.status !== 'error' || d.constraint !== focus.constraint) continue;
    const plan = planFocus(payload, d.id);
    const score = overlap(contextWords(payload, plan.scopeId), focus.context);
    if (score >= 0.5 && (!best || score > best.score)) best = { detail: d, plan, score };
  }
  return best;
}

// ---- applying a remediation edit to the sentence text (never touches the textbox) ----
export function applyEdit(payload, edit) {
  const sent = payload.parse.sentences[(payload.meta.target_sentence || 1) - 1];
  const toks = payload.parse.tokens;
  const text = payload.parse.text;
  let from;
  let to;
  let repl;
  if (edit.start === edit.end) {
    const t = toks[edit.start];
    from = t ? t.start - sent.start : text.length;
    to = from;
    repl = `${edit.text} `;
  } else {
    from = toks[edit.start].start - sent.start;
    to = toks[edit.end - 1].end - sent.start;
    repl = edit.text;
  }
  return (text.slice(0, from) + repl + text.slice(to))
    .replace(/\s{2,}/g, ' ')
    .replace(/\s+([.,;:!?])/g, '$1')
    .trim();
}

// Words of the scope subtree after the edit, used to find that subtree in the corrected parse.
export function expectedScopeWords(payload, scopeId, edit) {
  const node = payload.nodes[scopeId];
  const toks = payload.parse.tokens;
  if (!node || edit.start < node.span[0] || edit.end > node.span[1]) return null;
  const words = toks.slice(node.span[0], node.span[1]).map((t) => t.t);
  words.splice(edit.start - node.span[0], edit.end - edit.start,
    ...edit.text.split(' ').filter(Boolean));
  return words.join(' ').toLowerCase();
}

export function findScopeNode(payload, scopeType, expected) {
  const hit = Object.values(payload.nodes)
    .find((n) => n.type === scopeType && lower(n.surface) === expected);
  return hit ? hit.id : null;
}