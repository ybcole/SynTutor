// Aggregate every section's rule builders into one lookup keyed by rule id.
// Each value is (difficulty: 'easy'|'medium'|'hard') => item[] where an item is
// { bad, good, explanation }. Builders provide at least 5 and up to 40 items.
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

// Returns a shuffled pool of up to `limit` (default 40) items for a
// rule + difficulty. Cached per rule+difficulty so a run does not rebuild the
// whole bank, but re-shuffled and selected for contextual variety on every run.
export function questionPool(ruleId, difficulty = 'easy', limit = QUESTION_COUNT) {
  const build = BUILDERS[ruleId];
  if (typeof build !== 'function') return [];
  const key = `${ruleId}:${difficulty}`;
  if (!cache.has(key)) {
    const pool = build(difficulty);
    if (!Array.isArray(pool)) {
      throw new TypeError(`Question builder for ${ruleId} (${difficulty}) did not return an array.`);
    }
    cache.set(key, pool);
  }
  return diverseSample(shuffle(cache.get(key)), Math.max(0, limit));
}

export function shuffle(arr) {
  const out = [...arr];
  for (let i = out.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}
