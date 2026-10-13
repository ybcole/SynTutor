// Achievements catalog + unlock rules for the Matrix Quiz.
//
// Achievements are derived deterministically from the learner's signed-in
// quiz_progress rows (a completion per rule+difficulty), so nothing extra has
// to be persisted: the earned set is recomputed on demand and stored progress
// only lives in the quiz_progress table.

import { MATRIX_SECTIONS, ruleInfo } from '../quiz-data.js';

export function achievementCatalog() {
  const catalog = [];
  for (const section of MATRIX_SECTIONS) {
    catalog.push({
      id: `section_${section.id}`,
      icon: '\u{1F393}',
      title: `${section.title} Scholar`,
      description: `Complete a quiz in \u201c${section.title}\u201d.`,
      sectionId: section.id,
    });
  }
  catalog.push({
    id: 'first_quiz',
    icon: '\u{1F3AF}',
    title: 'First Steps',
    description: 'Complete your first Matrix Quiz.',
  });
  catalog.push({
    id: 'flawless',
    icon: '\u{1F48E}',
    title: 'Flawless Run',
    description: 'Finish a quiz with every answer correct.',
  });
  catalog.push({
    id: 'all_sections',
    icon: '\u{1F3C6}',
    title: 'Grammar Grandmaster',
    description: 'Complete a quiz in every section.',
  });
  return catalog;
}

// rows: quiz_progress entries shaped like { rule_id, perfect_count }.
// Returns a Set of achievement ids earned from the given rows.
export function computeUnlocked(rows, catalog = achievementCatalog()) {
  const list = rows || [];
  const completedSections = new Set();
  for (const row of list) {
    const info = ruleInfo(row.rule_id);
    if (info) completedSections.add(info.sectionId);
  }
  const unlocked = new Set();
  if (list.length > 0) unlocked.add('first_quiz');
  if (list.some((row) => row.perfect_count > 0)) unlocked.add('flawless');
  for (const ach of catalog) {
    if (ach.sectionId && completedSections.has(ach.sectionId)) unlocked.add(ach.id);
  }
  if (MATRIX_SECTIONS.every((section) => completedSections.has(section.id))) {
    unlocked.add('all_sections');
  }
  return unlocked;
}