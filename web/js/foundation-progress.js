// The account endpoint accepts events, never a local score or completion flag.
import { lessonKey } from './lesson-core.js';

export function scoreFoundation(questions, answers) {
  if (Object.keys(answers).length !== questions.length ||
      questions.some(q => !q.options.some(o => o.id === answers[q.id]))) {
    throw new Error('Choose an answer for every question.');
  }
  return questions.filter(q => q.answer === answers[q.id]).length;
}

function project(assessment, record, event) {
  const next = { ...record, updated_at: new Date().toISOString() };
  if (event.kind === 'visit') {
    if (!assessment.required_sections.includes(event.section)) throw new Error('Unknown required section.');
    next.visited = [...new Set([...next.visited, event.section])];
  } else {
    const questions = assessment[event.kind];
    const score = scoreFoundation(questions, event.answers);
    if (event.kind === 'opening') {
      next.opening_correct ??= score;
      next.opening_first_response ??= event.answers[questions[0].id];
    } else {
      next.last_correct = score;
      next.last_answers = event.answers;
      next.best_correct = Math.max(next.best_correct ?? 0, score);
      next.xp = Math.floor(15 * next.best_correct / questions.length);
    }
  }
  if (next.last_correct != null && assessment.required_sections.every(id => next.visited.includes(id))) {
    next.completed_at ??= next.updated_at;
  }
  return next;
}

const empty = () => ({ visited: [], xp: 0, completed_at: null });

export function createFoundationStore(course, { storage, userId, client }) {
  const lessons = course.lessons.filter(lesson => lesson.revised_assessment);
  const key = `syntutor:foundations:v2:${userId}`;
  const account = userId !== 'guest';
  let records = {};
  let queue = Promise.resolve();
  let blocked = false;

  function read() {
    try {
      const saved = JSON.parse(storage?.getItem(key) || 'null');
      if (saved && typeof saved === 'object' && !Array.isArray(saved)) records = saved;
    } catch { /* Keep the current in-memory progress. */ }
  }
  function write() {
    try { storage?.setItem(key, JSON.stringify(records)); }
    catch { /* Keep the current in-memory progress. */ }
  }
  function entry(lesson) {
    const key = lessonKey(lesson);
    const saved = records[key];
    if (Array.isArray(saved?.confirmed?.visited) && Array.isArray(saved.pending)) return saved;
    return records[key] = { confirmed: empty(), pending: [] };
  }
  function progress(lesson) {
    const { confirmed, pending } = entry(lesson);
    const result = pending.reduce((state, event) => project(lesson.revised_assessment, state, event), confirmed);
    return {
      ...result,
      verified_xp: account ? confirmed.xp : result.xp,
      pending: account && pending.length > 0,
    };
  }
  function serial(run) {
    const execute = async () => { read(); return run(); };
    const lock = () => globalThis.navigator?.locks?.request ? navigator.locks.request(key, execute) : execute();
    queue = queue.catch(() => {}).then(lock);
    return queue;
  }
  async function request(query) {
    const signal = AbortSignal.timeout(5000);
    const { data, error } = await query.abortSignal(signal);
    if (error) throw error;
    return data;
  }
  function publicState(row) {
    const { user_id, lesson_id, content_version, earned, ...state } = row;
    return state;
  }
  async function sync(lesson) {
    if (!account || !client || blocked) return 0;
    const item = entry(lesson);
    let earned = 0;
    while (item.pending.length) {
      const data = await request(client.rpc('save_foundation_event', {
        p_lesson_id: lesson.lesson_id, p_content_version: lesson.content_version, p_event: item.pending[0],
      }));
      item.confirmed = publicState(data);
      earned += data.earned;
      item.pending.shift();
      write();
    }
    return earned;
  }
  async function load() {
    if (!account || !client || !lessons.length) return;
    blocked = false;
    try {
      const rows = await request(client.from('foundation_progress').select('*'));
      for (const row of rows) {
        const lesson = lessons.find(l => l.lesson_id === row.lesson_id && l.content_version === row.content_version);
        if (lesson) entry(lesson).confirmed = publicState(row);
      }
      write();
      for (const lesson of lessons) await sync(lesson);
    } catch { blocked = true; }
  }
  read();
  return {
    progress,
    get pending() { return account && lessons.some(lesson => entry(lesson).pending.length > 0); },
    load: () => serial(load),
    act(lesson, event) {
      return serial(async () => {
        const item = entry(lesson);
        const previous = progress(lesson);
        const projected = project(lesson.revised_assessment, previous, event);
        const alreadyRecorded = event.kind === 'visit' && previous.visited.includes(event.section);
        if (!alreadyRecorded) {
          if (account) item.pending.push(event);
          else item.confirmed = projected;
          write();
        }
        let earned = account ? 0 : projected.xp - previous.xp;
        try { earned += await sync(lesson); }
        catch { blocked = true; }
        return { earned, progress: progress(lesson) };
      });
    },
  };
}
