// Aggregate every section's rule builders into one lookup keyed by rule id.
// Each value is (tier: 'easy'|'medium'|'hard') => item[] where an item is
// { bad, good, explanation }. Builders provide at least 5 and up to 40 items.
//
// The tiers only vary sentence *structure*; the error a learner must fix is the
// same in every tier. Quizzes have no difficulty setting, so a rule's pool is
// the union of all tiers (deduped) -- more variety, one uniform run length.
import s1 from './s1.js';
import s2 from './s2.js';
import s3 from './s3.js';
import s4 from './s4.js';
import s5 from './s5.js';
import s6 from './s6.js';
import s7 from './s7.js';
import s8 from './s8.js';
import s9 from './s9.js';
import s10 from './s10.js';
import s11 from './s11.js';
import { PARAGRAPHS } from './paragraphs.js';

export const BUILDERS = {
  ...s1, ...s2, ...s3, ...s4, ...s5, ...s6,
  ...s7, ...s8, ...s9, ...s10, ...s11,
};

export const QUESTION_COUNT = 40;

export function hasQuiz(ruleId) {
  return typeof BUILDERS[ruleId] === 'function';
}

const cache = new Map();

function questionFeatures(question) {
  const tokens = question.bad.toLowerCase().match(/[a-z0-9']+/g) || [];
  const features = new Map();
  const addNgrams = (words, prefix = '') => {
    for (let size = 2; size <= 4; size += 1) {
      for (let i = 0; i <= words.length - size; i += 1) {
        const key = `${prefix}${words.slice(i, i + size).join(' ')}`;
        features.set(key, prefix ? 3 : 1);
      }
    }
  };
  addNgrams(tokens);
  const comma = question.bad.indexOf(',');
  if (comma >= 0) {
    addNgrams(question.bad.slice(comma + 1).toLowerCase().match(/[a-z0-9']+/g) || [], 'tail:');
  }
  return features;
}

function contextKey(question) {
  const comma = question.bad.search(/[,;]/);
  const context = comma < 0 ? question.bad : question.bad.slice(comma + 1);
  return context.toLowerCase().replace(/[^a-z0-9']+/g, ' ').trim();
}

function similarity(left, right) {
  let shared = 0;
  let total = 0;
  for (const [feature, weight] of left) {
    total += weight;
    if (right.has(feature)) shared += weight;
  }
  for (const [feature, weight] of right) {
    if (!left.has(feature)) total += weight;
  }
  return total ? shared / total : 0;
}

function diverseSample(pool, limit) {
  const remaining = pool.map((question) => ({
    question,
    features: questionFeatures(question),
    context: contextKey(question),
  }));
  const selected = [];
  while (remaining.length && selected.length < limit) {
    const slotsLeft = limit - selected.length;
    const usedContexts = new Set(selected.map((item) => item.context));
    const fresh = remaining.filter((item) => !usedContexts.has(item.context));
    const candidates = new Set(fresh.map((item) => item.context)).size >= slotsLeft
      ? fresh
      : remaining;
    let best = 0;
    let bestDistance = -1;
    for (let i = 0; i < candidates.length; i += 1) {
      const distances = selected.map((item) =>
        1 - similarity(candidates[i].features, item.features));
      const distance = distances.length ? Math.min(...distances) : 1;
      if (distance > bestDistance) {
        best = i;
        bestDistance = distance;
      }
    }
    const choice = candidates[best];
    remaining.splice(remaining.indexOf(choice), 1);
    selected.push(choice);
  }
  return selected.map(({ question }) => question);
}

const tiers = ['easy', 'medium', 'hard'];

// Rule 1.1 is the one exception: its 'hard' tier holds the multi-sentence
// paragraph task, which *is* its quiz, so it does not merge with the
// single-sentence tiers.
const SINGLE_TIER_RULES = { '1.1': 'hard' };

function dedupeById(items) {
  const seen = new Set();
  const out = [];
  for (const item of items) {
    if (!item || seen.has(item.bad)) continue;
    seen.add(item.bad);
    out.push(item);
  }
  return out;
}

// Returns the fully materialized, deduped pool for a rule (every tier combined).
// This is what scripts/build_master.js freezes into web/content/master.json.
// Rules with hand-authored paragraphs (./paragraphs.js) use those directly; the
// rest fall back to the tier-merged single-sentence generators.
export function materializePool(ruleId) {
  const authored = PARAGRAPHS[ruleId];
  if (Array.isArray(authored) && authored.length) return dedupeById(authored);
  const build = BUILDERS[ruleId];
  if (typeof build !== 'function') return [];
  const list = SINGLE_TIER_RULES[ruleId] ? [SINGLE_TIER_RULES[ruleId]] : tiers;
  const pool = [];
  for (const tier of list) {
    const items = build(tier);
    if (!Array.isArray(items)) {
      throw new TypeError(`Question builder for ${ruleId} (${tier}) did not return an array.`);
    }
    pool.push(...items);
  }
  return dedupeById(pool);
}

// Returns a shuffled pool of up to `limit` (default 40) items for a rule,
// drawn from every tier and selected for contextual variety. Cached per rule so
// a run does not rebuild the whole bank, but re-shuffled and re-sampled on
// every run.
export function questionPool(ruleId, limit = QUESTION_COUNT) {
  if (!cache.has(ruleId)) cache.set(ruleId, materializePool(ruleId));
  return diverseSample(shuffle(cache.get(ruleId)), Math.max(0, limit));
}

export function shuffle(arr) {
  const out = [...arr];
  for (let i = out.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

export { diverseSample };
