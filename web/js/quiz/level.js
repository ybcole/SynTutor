// Gamification: XP and exponential leveling.
//
// Every correct answer is worth XP_PER_CORRECT; a flawless run (no wrong or
// skipped answers) adds PERFECT_QUIZ_BONUS on top. The amount of XP needed to
// advance from one level to the next grows geometrically, so each level is
// progressively harder to reach than the last (level 4 -> 5 costs far more than
// level 0 -> 1).

export const XP_PER_CORRECT = 5;
export const PERFECT_QUIZ_BONUS = 5;

const BASE_SPAN = 50;
const SPAN_GROWTH = 1.6;

// Cumulative XP thresholds. To reach level L a learner must bank the geometric
// sum BASE_SPAN * (1 + g + g^2 + ... + g^(L-1)): 50, 80, 128, 205, 328, ...
export function levelSpan(level) {
  return Math.round(BASE_SPAN * SPAN_GROWTH ** level);
}

export function xpToReach(level) {
  let total = 0;
  for (let i = 0; i < level; i += 1) total += levelSpan(i);
  return total;
}

// Decompose total XP into the current level plus progress toward the next one.
export function levelFromXp(xp) {
  const safeXp = Math.max(0, Math.floor(Number(xp) || 0));
  let level = 0;
  let floor = 0;
  let span = levelSpan(0);
  while (safeXp >= floor + span) {
    floor += span;
    level += 1;
    span = levelSpan(level);
  }
  return {
    xp: safeXp,
    level,
    into: safeXp - floor,
    span,
    floor,
    next: floor + span,
  };
}
