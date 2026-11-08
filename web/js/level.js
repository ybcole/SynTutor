// Pilot curve shared with lesson_level_for_xp in the M7 migration.
export function levelSpan(level) {
  return 100 + 20 * level;
}

export function xpToReach(level) {
  return 10 * level ** 2 + 90 * level;
}

export function levelFromXp(xp) {
  const safeXp = Number.isSafeInteger(xp) && xp >= 0 ? xp : 0;
  const level = Math.floor((Math.sqrt(8100 + 40 * safeXp) - 90) / 20);
  const floor = xpToReach(level);
  return {
    xp: safeXp,
    level,
    into: safeXp - floor,
    span: levelSpan(level),
    floor,
    next: xpToReach(level + 1),
  };
}
