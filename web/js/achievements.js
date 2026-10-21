// Achievements catalog + unlock rules for SynTutor.
//
// Achievements are derived deterministically from the learner's signed-in
// quiz_progress rows (one completion per stage id, "1".."4"), so nothing extra
// has to be persisted: the earned set is recomputed on demand and stored
// progress only lives in the quiz_progress table.
//
// Every achievement carries a category (the toolbar filter), a metric (how the
// goal is measured), a target and an XP reward, so the catalog can drive the
// progress banner, the tier bars and the reward pills of the modal.

import { TREE_SECTIONS, stageInfo } from './tree-catalog.js';

// The categories the catalog is grouped by.
export const achievementCategories = [
  { id: 'all', label: 'All' },
  { id: 'basics', label: 'Syntax Basics' },
  { id: 'speed', label: 'Speed & Accuracy' },
  { id: 'streaks', label: 'Streaks' },
  { id: 'mastery', label: 'Mastery' },
];

// The category the achievements grid is currently showing.
let activeCategory = 'all';
// Whoever re-renders the grid when the category changes.
let filterListener = null;
let filterDelegateBound = false;

export function activeAchievementCategory() {
  return activeCategory;
}

export function achievementCategoryLabel(id) {
  return achievementCategories.find((category) => category.id === id)?.label || 'All';
}

// The inline, horizontally expanding category selector: a trigger pill that
// unfurls into the full row of categories. Picking a category re-filters the
// grid, relabels the trigger and folds the row away again; a click outside
// folds it away too.
//
// The listeners live on the document, not on the buttons: the achievements
// view is re-rendered often, and a re-render must never leave the selector
// dead.
export function initAchievementCategorySelector(onChange) {
  filterListener = typeof onChange === 'function' ? onChange : null;
  if (filterDelegateBound) return;
  filterDelegateBound = true;

  document.addEventListener('click', (e) => {
    // 1. The trigger toggles the row.
    const trigger = e.target.closest('#achievementsCatTrigger');
    if (trigger) {
      e.stopPropagation();
      const wrapper = trigger.closest('#achievementsCatExpander');
      if (wrapper) {
        const isOpen = wrapper.classList.toggle('is-open');
        trigger.setAttribute('aria-expanded', String(isOpen));
      }
      return;
    }

    // 2. A category pill selects and filters.
    const pill = e.target.closest('.cat-pill[data-category]');
    if (pill && pill.closest('#achievementsCatExpander')) {
      const category = pill.getAttribute('data-category');
      const wrapper = pill.closest('#achievementsCatExpander');
      const label = wrapper.querySelector('#achievementsCatTrigger .cat-trigger-label');
      if (label) label.textContent = pill.textContent.trim();
      wrapper.querySelectorAll('.cat-pill').forEach((other) => other.classList.remove('active'));
      pill.classList.add('active');
      activeCategory = category;
      // Fold the row away again.
      wrapper.classList.remove('is-open');
      const triggerBtn = wrapper.querySelector('#achievementsCatTrigger');
      if (triggerBtn) triggerBtn.setAttribute('aria-expanded', 'false');
      filterListener?.(category);
      return;
    }

    // 3. A click anywhere else folds the row away.
    if (!e.target.closest('#achievementsCatExpander')) {
      const openWrapper = document.querySelector('#achievementsCatExpander.is-open');
      if (openWrapper) {
        openWrapper.classList.remove('is-open');
        const triggerBtn = openWrapper.querySelector('#achievementsCatTrigger');
        if (triggerBtn) triggerBtn.setAttribute('aria-expanded', 'false');
      }
    }
  });
}

// The badge icons, as inline SVG paths (24×24, stroke based).
export const achievementIcons = {
  tree: '<circle cx="12" cy="5" r="2.4"/><circle cx="6" cy="18" r="2.4"/><circle cx="18" cy="18" r="2.4"/><path d="M12 7.4v3.2M10.6 10.6 7.6 16M13.4 10.6l3 5.4"/>',
  target: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="1"/>',
  flame: '<path d="M12 3c3 3.6 5 5.9 5 8.8A5 5 0 0 1 7 12c0-1.7.8-3 2-4.2.3 1.3 1 2 2 2.4C10.4 7.6 11 5.4 12 3Z"/>',
  trophy: '<path d="M8 4h8v5a4 4 0 0 1-8 0V4Z"/><path d="M8 6H5.5A2.5 2.5 0 0 0 8 10.5M16 6h2.5A2.5 2.5 0 0 1 16 10.5"/><path d="M10 13h4l.5 4h-5l.5-4Z"/><path d="M8 19h8"/>',
  gem: '<path d="M6 3h12l3 6-9 12L3 9l3-6Z"/><path d="M3 9h18M9 3l-3 6 6 12 6-12-3-6"/>',
  book: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5V5.5Z"/><path d="M4 20.5A2.5 2.5 0 0 1 6.5 18H20v3H6.5A2.5 2.5 0 0 1 4 20.5Z"/>',
  bolt: '<path d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z"/>',
  mountain: '<path d="m3 19 6-11 4 6 2-3 6 8H3Z"/>',
  sprout: '<path d="M12 21v-7"/><path d="M12 14C12 10 9 8 5 8c0 4 3 6 7 6Z"/><path d="M12 14c0-3 2.5-5 7-5 0 3.5-2.8 5-7 5Z"/>',
  medal: '<circle cx="12" cy="15" r="5"/><path d="m8.5 10.5-2-7h4l1.5 4 1.5-4h4l-2 7"/>',
  sparkle: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>',
  stack: '<path d="M12 3 3 8l9 5 9-5-9-5Z"/><path d="m3 13 9 5 9-5"/>',
};

// metric: how the goal is measured against the learner's progress.
//   quizzes  — quiz completions in total
//   perfect  — perfect runs (every answer right)
//   accuracy — perfect runs per completion, in percent
//   sections — pipeline stages completed
//   streak   — consecutive days with a completion
export function achievementCatalog() {
  const catalog = [];
  TREE_SECTIONS.forEach((section, i) => {
    catalog.push({
      id: `stage_${section.id}`,
      icon: 'tree',
      title: `${section.title} Scholar`,
      description: `Complete the quiz for “${section.title}”.`,
      category: 'basics',
      metric: 'sections', unit: 'Stages Cleared',
      goal: section.id,
      target: section.id,
      xp: 30 + i * 20,
      sectionId: section.id,
    });
  });
  catalog.push(
    {
      id: 'first_quiz', icon: 'target', title: 'First Steps',
      description: 'Complete your first Syntax-Tree Quiz.',
      category: 'basics', metric: 'quizzes', unit: 'Quizzes Built', goal: 1, target: 1, xp: 25,
    },
    {
      id: 'quiz_10', icon: 'sprout', title: 'Getting the Hang of It',
      description: 'Complete 10 quizzes.',
      category: 'basics', metric: 'quizzes', unit: 'Quizzes Built', goal: 10, target: 10, xp: 60,
    },
    {
      id: 'quiz_50', icon: 'mountain', title: 'Sentence Mountain',
      description: 'Complete 50 quizzes.',
      category: 'basics', metric: 'quizzes', unit: 'Quizzes Built', goal: 50, target: 50, xp: 180,
    },
    {
      id: 'flawless', icon: 'gem', title: 'Flawless Run',
      description: 'Finish a quiz with every answer correct.',
      category: 'speed', metric: 'perfect', unit: 'Perfect Runs', goal: 1, target: 1, xp: 40,
    },
    {
      id: 'flawless_10', icon: 'sparkle', title: 'Diamond Hands',
      description: 'Finish 10 quizzes with every answer correct.',
      category: 'speed', metric: 'perfect', unit: 'Perfect Runs', goal: 10, target: 10, xp: 130,
    },
    {
      id: 'accuracy_75', icon: 'target', title: 'Steady Hand',
      description: 'Reach 75% accuracy across at least 10 quizzes.',
      category: 'speed', metric: 'accuracy', unit: 'Accuracy', goal: 75, target: 75, xp: 90, requires: 10,
    },
    {
      id: 'accuracy_90', icon: 'gem', title: 'Sharp Eye',
      description: 'Reach 90% accuracy across at least 10 quizzes.',
      category: 'speed', metric: 'accuracy', unit: 'Accuracy', goal: 90, target: 90, xp: 160, requires: 10,
    },
    {
      id: 'streak_3', icon: 'flame', title: 'Warming Up',
      description: 'Practise three days in a row.',
      category: 'streaks', metric: 'streak', unit: 'Day Streak', goal: 3, target: 3, xp: 60,
    },
    {
      id: 'streak_7', icon: 'bolt', title: 'Week Warrior',
      description: 'Practise seven days in a row.',
      category: 'streaks', metric: 'streak', unit: 'Day Streak', goal: 7, target: 7, xp: 140,
    },
    {
      id: 'streak_30', icon: 'trophy', title: 'Month of Trees',
      description: 'Practise thirty days in a row.',
      category: 'streaks', metric: 'streak', unit: 'Day Streak', goal: 30, target: 30, xp: 320,
    },
    {
      id: 'all_sections', icon: 'trophy', title: 'Tree Grandmaster',
      description: 'Complete a quiz in every pipeline stage.',
      category: 'mastery', metric: 'sections', unit: 'Stages Cleared', goal: 4, target: 4, xp: 220,
    },
    {
      id: 'scholar', icon: 'book', title: 'Syntax Scholar',
      description: 'Complete 25 quizzes.',
      category: 'mastery', metric: 'quizzes', unit: 'Quizzes Built', goal: 25, target: 25, xp: 160,
    },
    {
      id: 'perfect_50', icon: 'medal', title: 'Perfectionist',
      description: 'Finish 50 quizzes with every answer correct.',
      category: 'mastery', metric: 'perfect', unit: 'Perfect Runs', goal: 50, target: 50, xp: 260,
    },
    {
      id: 'quiz_100', icon: 'stack', title: 'Century Club',
      description: 'Complete 100 quizzes.',
      category: 'mastery', metric: 'quizzes', unit: 'Quizzes Built', goal: 100, target: 100, xp: 400,
    },
  );
  return catalog;
}

// The local day a timestamp falls on (the learner's own day boundary).
function dayKey(date) {
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
}

// The streak: consecutive days with a completion, ending today (or yesterday
// when the learner has not practised yet today).
export function computeStreak(rows) {
  const days = new Set();
  for (const row of rows || []) {
    if (!row?.last_completed_at) continue;
    const when = new Date(row.last_completed_at);
    if (Number.isNaN(when.getTime())) continue;
    days.add(dayKey(when));
  }
  if (!days.size) return 0;
  const cursor = new Date();
  cursor.setHours(0, 0, 0, 0);
  if (!days.has(dayKey(cursor))) {
    cursor.setDate(cursor.getDate() - 1);
    if (!days.has(dayKey(cursor))) return 0;
  }
  let streak = 0;
  while (days.has(dayKey(cursor))) {
    streak += 1;
    cursor.setDate(cursor.getDate() - 1);
  }
  return streak;
}

// Everything the catalog measures, derived from the learner's rows.
export function achievementMetrics(rows) {
  const list = rows || [];
  const quizzes = list.reduce((sum, row) => sum + (row.completed_count || 0), 0);
  const perfect = list.reduce((sum, row) => sum + (row.perfect_count || 0), 0);
  const sections = new Set();
  for (const row of list) {
    const info = stageInfo(row.rule_id);
    if (info && (row.completed_count || 0) > 0) sections.add(info.id);
  }
  const accuracy = quizzes > 0 ? Math.round((perfect / quizzes) * 100) : 0;
  return { quizzes, perfect, sections: sections.size, accuracy, streak: computeStreak(list) };
}

// The measured value of one achievement.
function metricValue(achievement, metrics) {
  switch (achievement.metric) {
    case 'quizzes': return metrics.quizzes;
    case 'perfect': return metrics.perfect;
    case 'accuracy': return metrics.accuracy;
    case 'sections': return metrics.sections;
    case 'streak': return metrics.streak;
    default: return 0;
  }
}

// Has the learner earned this achievement?
function isUnlocked(achievement, metrics) {
  if (achievement.requires && metrics.quizzes < achievement.requires) return false;
  if (achievement.metric === 'accuracy' && metrics.quizzes <= 0) return false;
  return metricValue(achievement, metrics) >= achievement.goal;
}

// rows: quiz_progress entries shaped like { rule_id, completed_count }.
// Returns a Set of achievement ids earned from the given rows.
export function computeUnlocked(rows, catalog = achievementCatalog()) {
  const metrics = achievementMetrics(rows);
  const unlocked = new Set();
  for (const achievement of catalog) {
    if (isUnlocked(achievement, metrics)) unlocked.add(achievement.id);
  }
  return unlocked;
}

// The full catalog with each achievement's live progress: {progress, target,
// pct, unlocked}. The modal renders one card per entry.
export function achievementProgress(rows, catalog = achievementCatalog()) {
  const metrics = achievementMetrics(rows);
  return catalog.map((achievement) => {
    const progress = metricValue(achievement, metrics);
    const target = achievement.target ?? achievement.goal;
    const pct = target > 0 ? Math.min(100, Math.round((progress / target) * 100)) : 0;
    return { ...achievement, progress, target, pct, unlocked: isUnlocked(achievement, metrics) };
  });
}
