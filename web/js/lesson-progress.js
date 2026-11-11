import { lessonKey, cleanProgress, reduceProgress, prerequisitesMet, completedCriteria } from './lesson-core.js';

export function createLessonStore(course, { storage, userId = 'guest', client = null, syncTimeoutMs = 5000 } = {}) {
  const key = `syntutor:lessons:v1:${userId}`;
  let records = {}, status = userId === 'guest' ? 'Saved on this device' : 'Saved on this device; account sync pending';
  let queue = Promise.resolve();
  const remoteAwards = new Map();
  let syncBlocked = false;
  async function bounded(request) {
    let timer;
    const controller = new AbortController();
    const job = typeof request.abortSignal === 'function' ? request.abortSignal(controller.signal) : request;
    try {
      return await Promise.race([job,new Promise((_resolve,reject) => { timer=setTimeout(() => { controller.abort();reject(new Error('Account sync timed out; progress is saved on this device. Retry when connected.')); },syncTimeoutMs); })]);
    } finally { clearTimeout(timer); }
  }
  function read() {
    if (!storage) { status = 'Progress storage unavailable; keep this page open'; return; }
    try {
      const saved = JSON.parse(storage?.getItem(key) || '{}');
      records = Object.fromEntries(Object.entries(saved).filter(([k,v]) => v && typeof v === 'object' && course.lessons.some(l => k.startsWith(l.lesson_id + '@')) && /^[a-z0-9-]+@\d+\.\d+\.\d+$/.test(k)).map(([k,v]) => {
        const l = course.lessons.find(l => lessonKey(l) === k);
        if (!l) return [k,v]; // Preserve historical versions; never import them into a new version.
        const cleaned = cleanProgress(l,v);
        if (cleaned.completed_at && !completedCriteria(l,cleaned)) cleaned.completed_at = null;
        return [k,cleaned];
      }));
    } catch { status = 'Progress storage unavailable; keep this page open'; }
  }
  function write() {
    try { storage?.setItem(key,JSON.stringify(records)); }
    catch { status = 'Progress storage unavailable; keep this page open'; }
  }
  async function sync() {
    if (!client || userId === 'guest') return;
    // The course is topologically ordered, so offline prerequisites sync first.
    for (const lesson of course.lessons) {
      const record = records[lessonKey(lesson)]; if (!record || !dirty.has(lessonKey(lesson))) continue;
      const { data, error } = await bounded(client.rpc('save_lesson_progress', { p_lesson_id: lesson.lesson_id,
        p_content_version: lesson.content_version, p_state: { responses: record.responses, visited: record.visited, stage: record.stage } }));
      if (error) throw new Error('Account sync unavailable. Your lesson progress is saved on this device; retry sync when connected.');
      if (data) {
        records[lessonKey(lesson)] = cleanProgress(lesson, { ...data, updated_at: record.updated_at });
        remoteAwards.set(lessonKey(lesson), data.earned || 0);
      }
      dirty.delete(lessonKey(lesson));
    }
    write(); status = 'Synced to your account';
  }
  read();
  const dirty = new Set(Object.keys(records));
  return {
    get records() { return records; }, get status() { return status; },
    async load() {
      if (!client || userId === 'guest') return;
      try {
        const { data, error } = await bounded(client.from('lesson_progress').select('lesson_id,content_version,responses,visited,stage,completed_at,updated_at'));
        if (error) throw error;
        for (const row of data || []) {
          const lesson = course.lessons.find(l => l.lesson_id === row.lesson_id && l.content_version === row.content_version);
          if (!lesson) continue;
          const local = records[lessonKey(lesson)];
          if (!local || row.completed_at) records[lessonKey(lesson)] = cleanProgress(lesson,row);
        }
        await sync();
      } catch { syncBlocked=true;status = 'Account sync unavailable; progress is saved on this device'; }
    },
    async act(lesson, event) {
      const run = async () => {
        // Refresh in case another tab saved the same version. XP is still derived once per key.
        read();
        const previous = records[lessonKey(lesson)];
        const next = reduceProgress(lesson, previous, event, { prerequisites: prerequisitesMet(lesson,records) });
        next.updated_at = new Date().toISOString();
        records[lessonKey(lesson)] = next; dirty.add(lessonKey(lesson)); write();
        remoteAwards.delete(lessonKey(lesson));
        try { if(!syncBlocked)await sync(); } catch (error) { syncBlocked=true;status = error.message; }
        const earned = remoteAwards.has(lessonKey(lesson)) ? remoteAwards.get(lessonKey(lesson)) : !previous?.completed_at && next.completed_at ? 15 : 0;
        return { progress: records[lessonKey(lesson)], earned };
      };
      const execute = () => globalThis.navigator?.locks?.request ? navigator.locks.request(key,run) : run();
      queue = queue.catch(() => {}).then(execute); return queue;
    },
    async retry() { try { await sync();syncBlocked=false; } catch(error) { syncBlocked=true;status = error.message; } },
  };
}
