import { builderProfile, fromCanonicalEnvelope, paletteFor, toCanonicalEnvelope } from './syntax-builder.js';

export const MIXED_FORMATS = Object.freeze([
  'fill_blank',
  'grammar_correction',
  'syntax_correction',
  'sentence_reconstruction',
  'tree_builder',
]);

export const REQUIRED_CHAPTER_FORMATS = Object.freeze({
  syntax: Object.freeze(['fill_blank', 'syntax_correction', 'sentence_reconstruction', 'tree_builder']),
  cambridge: Object.freeze(['fill_blank', 'grammar_correction', 'sentence_reconstruction']),
});

export const isMixedKind = kind => MIXED_FORMATS.includes(kind);

export function normalizeResponseText(text, { caseSensitive = false, stripTrailingPeriod = false } = {}) {
  let s = String(text ?? '')
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/\s+/g, ' ')
    .trim();
  if (stripTrailingPeriod) {
    s = s.replace(/\.+$/, '').trim();
  }
  s = s.replace(/\s+([,.;:!?])/g, '$1');
  return caseSensitive ? s : s.toLowerCase();
}

export function canonicalTreeShape(node) {
  if (!node || typeof node !== 'object') return null;
  if ('word' in node && node.word !== undefined) {
    return ['W', normalizeResponseText(node.word)];
  }
  if (node.gap || node.empty) {
    return ['S', node.gap ? 'gap' : 'empty', node.label || '', node.index ?? null, Boolean(node.elided)];
  }
  const features = Array.isArray(node.features) ? [...node.features].sort() : [];
  const children = node.triangle
    ? (node.words || []).map(w => ['W', normalizeResponseText(w)])
    : (node.children || []).map(canonicalTreeShape);
  return ['P', node.label || '', features, node.index ?? null, children];
}

function collectNodeLabels(node, out = []) {
  if (!node || typeof node !== 'object') return out;
  if (node.label && !node.gap && !node.empty) out.push(node.label);
  for (const c of node.children || []) collectNodeLabels(c, out);
  return out;
}

export function buildTreeDiffSummary(expectedEnvelope, actualEnvelopeOrError) {
  if (!expectedEnvelope?.root) return '';
  if (!actualEnvelopeOrError || actualEnvelopeOrError.error) {
    return actualEnvelopeOrError?.error || 'Your construction could not be converted into a connected single-root tree.';
  }
  const expRoot = expectedEnvelope.root;
  const actRoot = actualEnvelopeOrError.root;
  if (!actRoot) return 'No root constituent found in your submission.';
  const differences = [];
  if (expRoot.label !== actRoot.label) {
    differences.push(`Top category was "${actRoot.label || 'unlabelled'}" instead of "${expRoot.label}".`);
  }
  const expLabels = collectNodeLabels(expRoot);
  const actLabels = collectNodeLabels(actRoot);
  const expCount = new Map();
  for (const l of expLabels) expCount.set(l, (expCount.get(l) || 0) + 1);
  const actCount = new Map();
  for (const l of actLabels) actCount.set(l, (actCount.get(l) || 0) + 1);
  const missing = [];
  for (const [label, n] of expCount) {
    if ((actCount.get(label) || 0) < n) missing.push(label);
  }
  if (missing.length) {
    differences.push(`Missing or under-nested constituent label(s): ${missing.join(', ')}.`);
  }
  if (!differences.length) {
    differences.push('Constituent attachment, boundaries, or features differ from the reviewed structure.');
  }
  return differences.join(' ');
}

export function isResponseProvided(q, response) {
  if (response === undefined || response === null) return false;
  if (q.kind === 'fill_blank' || q.kind === 'grammar_correction') {
    return typeof response === 'string' && response.trim().length > 0;
  }
  if (q.kind === 'sentence_reconstruction') {
    return Array.isArray(response)
      && Array.isArray(q.tokens)
      && response.length === q.tokens.length
      && new Set(response).size === q.tokens.length
      && response.every(i => Number.isInteger(i) && i >= 0 && i < q.tokens.length);
  }
  if (q.kind === 'tree_builder' || q.kind === 'syntax_correction') {
    if (!response || typeof response !== 'object' || !response.model?.nodes) return false;
    const nodes = Object.values(response.model.nodes);
    if (!nodes.length) return false;
    if (q.kind === 'syntax_correction') return Boolean(response.touched);
    return Boolean(response.touched) || nodes.some(n => n.kind === 'phrase' || n.parent);
  }
  return typeof response === 'string' && response.length > 0;
}

export function formatReconstructionAnswer(q, response) {
  if (!Array.isArray(response) || !Array.isArray(q.tokens)) return '';
  return response
    .filter(i => Number.isInteger(i) && i >= 0 && i < q.tokens.length)
    .map(i => q.tokens[i])
    .join(' ')
    .replace(/\s+([,.;:!?])/g, '$1');
}

export function treeEnvelopeFromResponse(q, response) {
  if (!response || typeof response !== 'object') return { error: 'No tree submitted.' };
  if (response.model?.nodes) {
    try {
      const profile = q.profile || q.expected_tree?.convention_profile || builderProfile();
      const envelope = toCanonicalEnvelope(response.model, profile);
      return { envelope };
    } catch (e) {
      return { error: e.message };
    }
  }
  if (response.envelope?.root) return { envelope: response.envelope };
  return { error: 'Incomplete tree model.' };
}

export function gradeQuestion(q, response) {
  if (!isMixedKind(q.kind)) {
    const chosen = response ?? null;
    return { correct: chosen !== null && chosen === q.answer, response: chosen, answer: q.answer };
  }
  if (!isResponseProvided(q, response)) {
    return {
      correct: false,
      response: null,
      answer: q.display_answer || q.accepted_answers?.[0] || q.expected_summary || '',
      reason: 'No answer submitted.',
    };
  }
  if (q.kind === 'fill_blank') {
    const opts = { caseSensitive: Boolean(q.case_sensitive), stripTrailingPeriod: true };
    const norm = normalizeResponseText(response, opts);
    const accepted = (q.accepted_answers || []).map(a => normalizeResponseText(a, opts));
    const ok = norm.length > 0 && accepted.includes(norm);
    return { correct: ok, response: String(response).trim(), answer: q.display_answer || q.accepted_answers[0] };
  }
  if (q.kind === 'grammar_correction') {
    const opts = { caseSensitive: Boolean(q.case_sensitive), stripTrailingPeriod: !q.punctuation_sensitive };
    const norm = normalizeResponseText(response, opts);
    const originalNorm = normalizeResponseText(q.stimulus?.sentence || '', opts);
    if (originalNorm && norm === originalNorm) {
      return {
        correct: false,
        response: String(response).trim(),
        answer: q.display_answer || q.accepted_answers[0],
        reason: 'Submitted sentence leaves the original error unchanged.',
      };
    }
    const accepted = (q.accepted_answers || []).map(a => normalizeResponseText(a, opts));
    const ok = norm.length > 0 && accepted.includes(norm);
    return { correct: ok, response: String(response).trim(), answer: q.display_answer || q.accepted_answers[0] };
  }
  if (q.kind === 'sentence_reconstruction') {
    const built = formatReconstructionAnswer(q, response);
    const opts = { caseSensitive: false, stripTrailingPeriod: true };
    const norm = normalizeResponseText(built, opts);
    const accepted = (q.accepted_answers || []).map(a => normalizeResponseText(a, opts));
    const ok = norm.length > 0 && accepted.includes(norm);
    return { correct: ok, response: built, answer: q.display_answer || q.accepted_answers[0] };
  }
  if (q.kind === 'tree_builder' || q.kind === 'syntax_correction') {
    const converted = treeEnvelopeFromResponse(q, response);
    if (converted.error) {
      return {
        correct: false,
        response,
        answer: q.expected_summary || q.expected_tree?.sentence || '',
        reason: converted.error,
      };
    }
    const actualShape = JSON.stringify(canonicalTreeShape(converted.envelope.root));
    const expectedList = [q.expected_tree, ...(q.accepted_trees || [])].filter(Boolean);
    const ok = expectedList.some(exp => JSON.stringify(canonicalTreeShape(exp.root)) === actualShape);
    return {
      correct: ok,
      response,
      evaluated_tree: converted.envelope,
      answer: q.expected_summary || q.expected_tree?.sentence || '',
      reason: ok ? '' : buildTreeDiffSummary(q.expected_tree, converted.envelope),
    };
  }
  return { correct: false, response, answer: '' };
}

export function validateMixedItems(items, curriculum) {
  const ids = new Set();
  const prompts = new Set();
  for (const q of items) {
    const chapter = curriculum.find(t => t.id === q.track_id)?.chapters.find(c => c.id === q.chapter_id);
    if (!chapter || !chapter.topics.some(t => t.id === q.subtopic_id)) {
      throw Error(`Mixed quiz item ${q.item_id} has invalid track/chapter/topic mapping.`);
    }
    if (ids.has(q.item_id)) throw Error(`Duplicate mixed quiz item ${q.item_id}.`);
    const promptKey = `${q.chapter_id}/${q.kind}/${q.prompt}/${q.stimulus?.sentence || (q.tokens || []).join('|')}`;
    if (prompts.has(promptKey)) throw Error(`Duplicate mixed quiz prompt ${promptKey}.`);
    if (!isMixedKind(q.kind)) throw Error(`Unsupported mixed quiz kind ${q.kind}.`);
    if (!q.rationale || !q.lesson_reference || q.lesson_id !== q.chapter_id) {
      throw Error(`Incomplete metadata on ${q.item_id}.`);
    }
    if (!['easy', 'medium', 'hard'].includes(q.difficulty)) {
      throw Error(`Missing or invalid difficulty on ${q.item_id}.`);
    }
    if (['fill_blank', 'grammar_correction', 'sentence_reconstruction'].includes(q.kind)) {
      if (!Array.isArray(q.accepted_answers) || !q.accepted_answers.length) {
        throw Error(`Missing accepted_answers on ${q.item_id}.`);
      }
      if (q.kind === 'sentence_reconstruction' && (!Array.isArray(q.tokens) || q.tokens.length < 3)) {
        throw Error(`Invalid reconstruction tokens on ${q.item_id}.`);
      }
      if (q.kind === 'grammar_correction' && !q.stimulus?.sentence) {
        throw Error(`Missing erroneous stimulus sentence on ${q.item_id}.`);
      }
    } else {
      if (!q.expected_tree?.root || !q.expected_tree?.convention_profile) {
        throw Error(`Missing expected_tree on ${q.item_id}.`);
      }
      // Verify both expected_tree and seed_tree (if present) round-trip cleanly through canonical builder validation.
      const profile = q.profile || q.expected_tree.convention_profile;
      const palette = paletteFor(profile);
      const model = fromCanonicalEnvelope(q.expected_tree);
      toCanonicalEnvelope(model, profile);
      const allowed = q.labels || palette.labels;
      for (const lbl of collectNodeLabels(q.expected_tree.root)) {
        if (!allowed.includes(lbl)) {
          throw Error(`Category "${lbl}" on ${q.item_id} is outside chapter ${profile.chapter} palette.`);
        }
      }
      if (q.seed_tree) {
        const seedModel = fromCanonicalEnvelope(q.seed_tree);
        toCanonicalEnvelope(seedModel, profile);
      }
      if (q.kind === 'tree_builder' && !q.seed_tokens) {
        throw Error(`Missing seed_tokens on tree_builder ${q.item_id}.`);
      }
    }
    ids.add(q.item_id);
    prompts.add(promptKey);
  }
  return items;
}
