// Interactive corrective feedback — zoom scope lookup (keyed by constraint id),
// pair linking, edit application, and error re-identification by constraint +
// surrounding words.
//
// The module is deliberately free of DOM code: it only reasons about the parse
// payload the server returns, so the tutor page can drive it without the
// renderer or the UI layer knowing about each other.

const NOUNISH = new Set(['NN', 'NNS', 'NNP', 'NNPS', 'PRP', 'NML', 'NX']);
const VERBISH = new Set(['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD', 'AUX']);
const POSS = new Set(['my', 'your', 'our', 'their', 'its']);
const lower = (s) => (s || '').toLowerCase();
const leavesOf = (n) => (n.children && n.children.length ? n.children.flatMap(leavesOf) : [n]);

// The API sends Unicode code-point offsets. Textarea and DOM ranges use UTF-16.
export function domTextOffsets(text) {
  const offsets = [0];
  for (const char of text) offsets.push(offsets.at(-1) + char.length);
  return offsets;
}

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
  'C-SUBJECT-AGREEMENT': { label: 'Subject–verb agreement',
    pair: (c) => [npHead(subjectNP(c.parent)), firstVerb(c.node)] },
  'C-DETERMINER-AGREEMENT': { label: 'Determiner–noun agreement',
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
  'C-QUANTIFIER': { label: 'Quantifier–noun agreement', pair: (c) => [c.node, npHead(c.parent)] },
  'C-COMPARATIVE-DOUBLE': { label: 'Double comparative',
    pair: (c) => [c.node, (c.parent.children || []).find((x) => x.type === 'JJR' || x.type === 'JJS')] },
  'C-HEAD-NOUN': { label: 'Missing noun', pair: (c) => [c.node] },
  'C-HEAD-VERB': { label: 'Missing verb', pair: (c) => [c.node] },
  'C-TENSE-FINITE': { label: 'Finite verb required',
    scope: (c) => (c.parent ? c.parent : c.node),
    pair: (c) => (c.node.type === 'VP' ? [firstVerb(c.node)] : []) },
  'C-SUBJ-AGREE-XP': { label: 'Subject–verb agreement',
    pair: (c) => [npHead(subjectNP(c.parent)), firstVerb(c.node)] },
};
const DEFAULT_RULE = { label: 'Grammar error', pair: () => [] };

export function planFocus(payload, id) {
  const details = payload.node_details || {};
  const nodes = payload.nodes || {};
  const detail = details[id];
  if (!detail) return null;
  const node = nodes[id];
  if (!node) return null;
  const parent = detail.parent ? nodes[detail.parent] : null;
  const gpId = parent ? details[parent.id]?.parent : null;
  const grandparent = gpId ? nodes[gpId] : null;
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
  const node = (payload.nodes || {})[scopeId];
  const toks = (payload.parse && payload.parse.tokens) || [];
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
  if (!payload || !focus) return null;
  const ctx = focus.context || [];
  let best = null;
  for (const d of Object.values(payload.node_details || {})) {
    if (d.status !== 'error' || d.constraint !== focus.constraint) continue;
    const plan = planFocus(payload, d.id);
    if (!plan) continue;
    if (!ctx.length) {
      // No surrounding words to match on (the scope had none): the constraint
      // alone identifies the error.
      return { detail: d, plan, score: 1 };
    }
    const score = overlap(contextWords(payload, plan.scopeId), ctx);
    if (score >= 0.5 && (!best || score > best.score)) best = { detail: d, plan, score };
  }
  return best;
}

// ---- applying a remediation edit to the sentence text (never touches the textbox) ----
export function correctionPreview(payload, edit, inputText) {
  const sent = payload.parse.sentences[(payload.meta.target_sentence || 1) - 1];
  const tokens = payload.parse.tokens;
  // Offsets refer to the original request even when parse.text has normalized
  // whitespace. Take the target sentence from that request when available.
  const chars = typeof inputText === 'string'
    ? Array.from(inputText).slice(sent.start, sent.end)
    : Array.from(payload.parse.text);
  const insertion = edit.start === edit.end;
  const from = tokens[edit.start]?.start ?? sent.start + chars.length;
  const to = insertion ? from : tokens[edit.end - 1].end;
  const before = chars.slice(0, from - sent.start).join('');
  const removed = chars.slice(from - sent.start, to - sent.start).join('');
  const after = chars.slice(to - sent.start).join('');
  const added = edit.text;
  const punctuation = /^[.,;:!?]/.test(added);
  const left = punctuation ? before.trimEnd() : before;
  const insertSpace = insertion && left && !/\s$/.test(left) && !punctuation ? ' ' : '';
  const tailSpace = insertion && after && !/^[\s.,;:!?]/.test(after) ? ' ' : '';
  const text = (left + insertSpace + added + tailSpace + after)
    .replace(/\s+/g, ' ')
    .replace(/\s+([.,;:!?])/g, '$1')
    .trim();
  return { text, removed, added };
}

// The parser can encode brackets and quotes in Penn notation. Everything else
// must match the target sentence's tokens and ordered leaf spans exactly.
const PENN_PUNCTUATION = new Map([
  ['-LRB-', '('], ['-RRB-', ')'], ['-LSB-', '['], ['-RSB-', ']'],
  ['-LCB-', '{'], ['-RCB-', '}'], ['``', '"'], ["''", '"'],
]);
export function matchesPreviewTokens(payload, text) {
  if (!payload?.tree || payload.parse?.text !== text) return false;
  const tokens = payload.parse.tokens;
  const sentence = payload.parse.sentences?.[(payload.meta?.target_sentence || 1) - 1];
  if (!sentence || !Array.isArray(tokens) || !tokens.length) return false;
  const chars = Array.from(text);
  const leaves = leavesOf(payload.tree);
  if (leaves.length !== tokens.length) return false;
  let end = 0;
  for (const [index, token] of tokens.entries()) {
    const start = token.start - sentence.start;
    const finish = token.end - sentence.start;
    const leaf = leaves[index];
    if (!Number.isInteger(start) || !Number.isInteger(finish)
        || start < end || finish <= start || finish > chars.length
        || chars.slice(end, start).join('').trim()
        || chars.slice(start, finish).join('') !== token.t
        || leaf.span?.[0] !== index || leaf.span?.[1] !== index + 1
        || (leaf.surface !== token.t && PENN_PUNCTUATION.get(leaf.surface) !== token.t)) {
      return false;
    }
    end = finish;
  }
  return !chars.slice(end).join('').trim();
}

export function applyEdit(payload, edit) {
  return correctionPreview(payload, edit).text;
}

// Words of the scope subtree after the edit, used to find that subtree in the corrected parse.
export function expectedScopeWords(payload, scopeId, edit) {
  const node = (payload.nodes || {})[scopeId];
  const toks = (payload.parse && payload.parse.tokens) || [];
  if (!node || edit.start < node.span[0] || edit.end > node.span[1]) return null;
  const words = toks.slice(node.span[0], node.span[1]).map((t) => t.t);
  // Replace exactly the tokens the edit covers (the range is relative to the
  // scope, the length is the number of tokens the edit removes).
  words.splice(edit.start - node.span[0], edit.end - edit.start,
    ...edit.text.split(' ').filter(Boolean));
  return words.join(' ').toLowerCase();
}

export function findScopeNode(payload, scopeType, expected) {
  const hit = Object.values(payload.nodes || {})
    .find((n) => n.type === scopeType && lower(n.surface) === expected);
  return hit ? hit.id : null;
}

// ---- correction preview impact & honest completeness reporting -------------
function errorRowsOf(payload) {
  return Object.values(payload?.node_details || {})
    .filter((detail) => detail && detail.status === 'error')
    .map((detail) => ({
      detail_id: detail.id,
      constraint: detail.constraint,
      type: detail.type,
      surface: detail.surface,
      violation: detail.remediation?.violation || detail.text || '',
      suggested_fix: detail.remediation?.suggested_fix || '',
    }));
}

function mergeUnresolvedTokens(...lists) {
  const out = [];
  const seen = new Set();
  for (const list of lists) {
    if (!Array.isArray(list)) continue;
    for (const item of list) {
      if (!item || !item.surface) continue;
      const key = `${item.token_id ?? ''}|${item.surface}`;
      if (seen.has(key)) continue;
      seen.add(key);
      out.push({ token_id: item.token_id, surface: item.surface });
    }
  }
  return out;
}

export function computePreviewImpact(originalPayload, previewPayload) {
  if (!originalPayload || !previewPayload) return null;
  const before = errorRowsOf(originalPayload);
  const after = errorRowsOf(previewPayload);
  const key = (row) => `${row.constraint || ''}|${row.type || ''}`;
  const beforeKeys = new Set(before.map(key));
  const afterKeys = new Set(after.map(key));
  const resolved = before.filter((row) => !afterKeys.has(key(row)));
  const remaining = after.filter((row) => beforeKeys.has(key(row)));
  const introduced = after.filter((row) => !beforeKeys.has(key(row)));
  const verdict = previewPayload.summary?.verdict;
  const origCorr = originalPayload.summary?.correction;
  const matchesServerCorr = Boolean(
    origCorr?.corrected_sentence
    && previewPayload.parse?.text
    && origCorr.corrected_sentence.trim() === previewPayload.parse.text.trim(),
  );
  const unresolvedTokens = mergeUnresolvedTokens(
    previewPayload.summary?.unresolved_tokens,
    matchesServerCorr ? origCorr?.impact?.unresolved_tokens : null,
  );
  const serverMarkedPartial = matchesServerCorr && origCorr?.impact?.whole_sentence_clean === false;
  const treeUnresolved = Boolean(
    previewPayload.br_analysis && previewPayload.br_analysis.status !== 'normalized',
  );
  const wholeClean = verdict === 'grammatical'
    && !remaining.length
    && !introduced.length
    && !unresolvedTokens.length
    && !treeUnresolved
    && !serverMarkedPartial;
  return {
    resolved_count: resolved.length,
    remaining_count: remaining.length,
    introduced_count: introduced.length,
    resolved,
    remaining,
    introduced,
    resulting_verdict: verdict,
    unresolved_tokens: unresolvedTokens,
    tree_unresolved: treeUnresolved,
    whole_sentence_clean: wholeClean,
    completeness: wholeClean ? 'complete' : 'partial',
  };
}

export function formatImpactSummary(impact, { panel = false } = {}) {
  if (!impact) return '';
  if (impact.whole_sentence_clean) {
    return panel
      ? 'Re-parsing finds no remaining rule-level error. The whole sentence is clean.'
      : 'Re-parsing finds no remaining rule-level error.';
  }
  const parts = [];
  if (impact.resolved_count) {
    parts.push(`${impact.resolved_count} ${panel ? (impact.resolved_count === 1 ? 'issue resolved' : 'issues resolved') : 'resolved'}`);
  }
  if (impact.remaining_count) parts.push(`${impact.remaining_count} still present`);
  if (impact.introduced_count) parts.push(`${impact.introduced_count} newly introduced`);
  const prefix = panel ? 'Re-parsing after this edit' : 'Re-parsing after the revision';
  const base = parts.length
    ? `${prefix}: ${parts.join(', ')}.`
    : `${prefix}: no change in the rule-level error set.`;
  const extras = [];
  if (Array.isArray(impact.unresolved_tokens) && impact.unresolved_tokens.length) {
    const quoted = impact.unresolved_tokens.map((t) => `\u201c${t.surface}\u201d`).join(', ');
    extras.push(`The spelling of ${quoted} remains uncertain.`);
  }
  if (impact.tree_unresolved || (impact.resulting_verdict && impact.resulting_verdict !== 'grammatical')) {
    extras.push('Full grammaticality could not be verified for the rest of the sentence.');
  }
  return extras.length ? `${base} ${extras.join(' ')}` : base;
}

export function formatRecheckOutcome(payload) {
  const left = (payload?.summary?.violations || []).length;
  if (left > 0) {
    return {
      kind: 'fixed',
      complete: false,
      message: `That error is fixed. ${left} other issue(s) remain \u2014 click a red node to continue.`,
    };
  }
  const unresolved = payload?.summary?.unresolved_tokens || [];
  if (unresolved.length) {
    const quoted = unresolved.map((t) => `\u201c${t.surface}\u201d`).join(', ');
    return {
      kind: 'fixed',
      complete: false,
      message: `That error is fixed, but the spelling of ${quoted} remains uncertain.`,
    };
  }
  const verdict = payload?.summary?.verdict;
  const treeUnresolved = Boolean(
    payload?.br_analysis && payload.br_analysis.status !== 'normalized',
  );
  if ((verdict && verdict !== 'grammatical') || treeUnresolved) {
    return {
      kind: 'fixed',
      complete: false,
      message: 'That error is fixed, though the rest of the sentence could not be verified as fully grammatical.',
    };
  }
  return {
    kind: 'fixed',
    complete: true,
    message: 'That error is fixed \u2014 this sentence is clean now.',
  };
}
