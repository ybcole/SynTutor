import assert from 'node:assert/strict';
import { levelFromXp, levelSpan, xpToReach } from '../web/js/level.js';

assert.deepEqual(Array.from({ length: 6 }, (_, level) => xpToReach(level)),
  [0, 100, 220, 360, 520, 700]);
for (let level = 1; level <= 1000; level += 1) {
  const threshold = xpToReach(level);
  assert.equal(levelFromXp(threshold - 1).level, level - 1);
  assert.deepEqual(levelFromXp(threshold), {
    xp: threshold, level, into: 0, span: levelSpan(level),
    floor: threshold, next: xpToReach(level + 1),
  });
}
for (const invalid of [-1, NaN, Infinity, null, undefined]) {
  assert.equal(levelFromXp(invalid).xp, 0);
}
console.log('PASS: pilot thresholds, 1,000 level boundaries and invalid XP.');
