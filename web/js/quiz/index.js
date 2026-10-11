// Aggregate every section's rule builders into one lookup keyed by rule id.
// Each value is (difficulty: 'easy'|'medium'|'hard') => item[] where an item is
// { bad, good, explanation }. Every builder returns 40 unique items per tier.
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

// Returns a shuffled pool of up to `limit` (default 40) items for a
// rule + difficulty. Cached per rule+difficulty so a run does not rebuild the
// whole bank, but re-shuffled on every request for variety.
export function questionPool(ruleId, difficulty = 'easy', limit = QUESTION_COUNT) {
  const build = BUILDERS[ruleId];
  if (typeof build !== 'function') return [];
  const key = `${ruleId}:${difficulty}`;
  if (!cache.has(key)) {
    let pool = [];
    try { pool = build(difficulty) || []; } catch { pool = []; }
    cache.set(key, pool);
  }
  return shuffle(cache.get(key)).slice(0, limit);
}

export function shuffle(arr) {
  const out = [...arr];
  for (let i = out.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}
