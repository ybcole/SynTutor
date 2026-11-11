// Pure lesson/progress rules. No parser, model, account or DOM dependencies.
export const STAGES = ['predict', 'understand', 'worked', 'guided', 'transfer', 'exit'];
export const STAGE_TITLES = ['Predict', 'Understand', 'See it', 'Build it', 'Apply it', 'Exit check'];
export const lessonKey = lesson => `${lesson.lesson_id}@${lesson.content_version}`;
export const activityKey = lesson => `lesson:${lesson.lesson_id}:${lesson.content_version}`;
export function isReviewed(record) {
  return record?.review_status === 'INDEPENDENTLY_REVIEWED' && record.independent_review === true
    && Boolean(record.reviewed_by && record.reviewed_on);
}
export function validateCourse(course) {
  if (course?.schema_version !== '1.0.0' || !Array.isArray(course.lessons) || !course.lessons.length) throw new Error('Invalid lesson catalog.');
  const sources = new Map((course.sources || []).map(s => [s.id, s]));
  if (sources.size !== course.sources.length) throw new Error('Duplicate lesson source IDs.');
  const ids = new Set();
  const concepts = new Set((course.concepts || []).map(c => c.id));
  if (concepts.size !== course.concepts?.length) throw new Error('Invalid lesson concepts.');
  function cited(ids) {
    if (!Array.isArray(ids) || !ids.length || ids.some(id => {
      const s = sources.get(id);
      return !s || !['B-R','Cambridge'].includes(s.book) || !Number.isInteger(s.chapter) || s.chapter < 1 || !isReviewed(s) || s.status !== 'approved' || !s.edition || !s.title
        || !Number.isInteger(s.printed_page) || s.printed_page < 1 || !['IMG', 'TXT'].includes(s.evidence_status);
    })) throw new Error('Lesson evidence is missing or unreviewed.');
  }
  for (const concept of course.concepts) cited(concept.source_ids);
  for (const lesson of course.lessons) {
    if (lesson.concept_ids.some(id => !concepts.has(id)) || lesson.cambridge_insights.some(b => b.concept_ids.some(id => !concepts.has(id)))) throw new Error('Unknown lesson concept.');
    if (ids.has(lesson.lesson_id) || lesson.publication_status !== 'published' || !isReviewed(lesson)) throw new Error('Invalid lesson publication/review state.');
    ids.add(lesson.lesson_id); cited(lesson.source_ids);
    if (!/^\d+\.\d+\.\d+$/.test(lesson.content_version) || !lesson.outcomes?.length || !Array.isArray(lesson.prerequisites)) throw new Error('Incomplete lesson contract.');
    if (JSON.stringify(lesson.completion?.required_stages) !== JSON.stringify(STAGES) || lesson.completion.reward_xp !== 15) throw new Error('Invalid completion contract.');
    for (const block of [...lesson.teaching, ...lesson.worked_example.steps, ...lesson.cambridge_insights]) { if (!block.text) throw new Error('Empty teaching block.'); cited(block.source_ids); }
    cited(lesson.worked_example.source_ids);
    for (const key of ['predict', 'guided', 'transfer', 'exit']) {
      const q = lesson[key]; cited(q?.source_ids);
      if (q?.id !== key || !q.prompt || !q.hint || q.options?.length < 2 || !q.options.every(o => o.text && o.feedback)
          || new Set(q.options.map(o => o.id)).size !== q.options.length || !q.options.some(o => o.id === q.answer)
          || !q.outcome_ids?.length || q.outcome_ids.some(id => !lesson.outcomes.some(o => o.id === id))) throw new Error('Invalid lesson question.');
    }
    if (lesson.worked_example.tree && !lesson.convention_profile) throw new Error('Tree without convention profile.');
  }
  for (const lesson of course.lessons) for (const p of lesson.prerequisites) {
    if (!course.lessons.some(l => l.lesson_id === p.lesson_id && l.content_version === p.content_version)) throw new Error('Unknown prerequisite/version.');
  }
  const visiting = new Set(), done = new Set();
  function visit(id) {
    if (visiting.has(id)) throw new Error('Curriculum prerequisite cycle.');
    if (done.has(id)) return;
    visiting.add(id); for (const p of course.lessons.find(l => l.lesson_id === id).prerequisites) visit(p.lesson_id);
    visiting.delete(id); done.add(id);
  }
  for (const lesson of course.lessons) visit(lesson.lesson_id);
  return course;
}
export function emptyProgress() { return { responses: {}, visited: [], stage: 0, completed_at: null }; }
export function cleanProgress(lesson, raw = {}) {
  const responses = {};
  for (const key of ['predict', 'guided', 'transfer', 'exit']) {
    if (lesson[key].options.some(o => o.id === raw.responses?.[key])) responses[key] = raw.responses[key];
  }
  return { responses, visited: STAGES.filter(s => raw.visited?.includes(s)),
    stage: Number.isInteger(raw.stage) && raw.stage >= 0 && raw.stage < STAGES.length ? raw.stage : 0,
    completed_at: typeof raw.completed_at === 'string' && Number.isFinite(Date.parse(raw.completed_at)) ? raw.completed_at : null,
    updated_at: typeof raw.updated_at === 'string' && Number.isFinite(Date.parse(raw.updated_at)) ? raw.updated_at : null };
}
export function prerequisitesMet(lesson, records) {
  return lesson.prerequisites.every(p => Boolean(records[`${p.lesson_id}@${p.content_version}`]?.completed_at));
}
export function canAdvance(lesson, progress) {
  const key = STAGES[progress.stage];
  return !lesson[key] || (key === 'predict' ? Boolean(progress.responses[key]) : progress.responses[key] === lesson[key].answer);
}
export function completedCriteria(lesson, progress) {
  return STAGES.every(s => progress.visited.includes(s)) && Boolean(progress.responses.predict)
    && ['guided', 'transfer', 'exit'].every(key => progress.responses[key] === lesson[key].answer);
}
export function reduceProgress(lesson, raw, event, { prerequisites = true, now = () => new Date().toISOString() } = {}) {
  const next = cleanProgress(lesson, raw);
  if (event.type === 'answer') {
    const key = STAGES[next.stage];
    if (lesson[key]?.options.some(o => o.id === event.answer)) next.responses[key] = event.answer;
    else throw new Error('Answer does not belong to this lesson stage.');
  } else if (event.type === 'navigate') {
    const furthest = Math.min(5, STAGES.findIndex(s => !next.visited.includes(s)) < 0 ? 5 : STAGES.findIndex(s => !next.visited.includes(s)));
    if (!Number.isInteger(event.stage) || event.stage < 0 || event.stage > furthest) throw new Error('Finish the earlier stage first.');
    next.stage = event.stage;
  } else if (event.type === 'advance') {
    if (!canAdvance(lesson, next)) throw new Error('Answer this stage before continuing.');
    const key = STAGES[next.stage];
    if (!next.visited.includes(key)) next.visited.push(key);
    if (next.stage < 5) next.stage += 1;
    else {
      if (!completedCriteria(lesson, next)) throw new Error('Complete all required activities first.');
      if (!prerequisites) throw new Error('Complete the prerequisite lesson first. Your work is saved.');
      next.completed_at ||= now();
    }
  } else throw new Error('Unknown lesson action.');
  return next;
}
export function lessonXp(records) {
  // Derived from unique version keys, never incremented by a replay click.
  return Object.values(records).filter(row => row.completed_at).length * 15;
}
