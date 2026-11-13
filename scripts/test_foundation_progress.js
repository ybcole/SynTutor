import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { validateCourse } from '../web/js/lesson-core.js';
import { createFoundationStore } from '../web/js/foundation-progress.js';

const course = validateCourse(JSON.parse(execFileSync('python3', ['scripts/test_foundation_fixture.py'])));
const chapter = course.lessons.find(l => l.revised_assessment);
const { closing, required_sections: sections } = chapter.revised_assessment;
const attempt = (id, correct) => ({
  kind: 'closing', attempt_id: id,
  answers: Object.fromEntries(closing.map((q, i) => [q.id, i < correct ? 'a' : 'b'])),
});
const values = new Map();
const storage = { getItem: key => values.get(key), setItem: (key, value) => values.set(key, value) };
const guest = createFoundationStore(course, { storage, userId: 'guest' });
for (const section of sections) await guest.act(chapter, { kind: 'visit', section });
assert.equal((await guest.act(chapter, attempt('guest-1', 0))).earned, 0);
assert.ok(guest.progress(chapter).completed_at);
assert.equal((await guest.act(chapter, attempt('guest-2', 3))).earned, 7);

let reachable = false;
const confirmed = {
  visited: [], xp: 7, completed_at: null, last_correct: 3, best_correct: 3,
  last_answers: attempt('account-1', 3).answers,
};
const received = [];
const request = data => ({ abortSignal: async () => reachable ? { data } : { error: new Error('Offline') } });
const client = {
  from: () => ({ select: () => request([]) }),
  rpc: (_name, payload) => {
    received.push(payload);
    return request({ ...confirmed, earned: 0 });
  },
};
const config = { storage, userId: 'a', client };
let account = createFoundationStore(course, config);
assert.equal(account.progress(chapter).xp, 0, 'Guest progress does not transfer to an account');
const saved = await account.act(chapter, attempt('account-1', 3));
assert.equal(saved.earned, 0);
assert.equal(saved.progress.verified_xp, 0);
assert.equal(saved.progress.pending, true);
assert.equal(saved.progress.last_correct, 3);
account = createFoundationStore(course, config);
assert.equal(account.progress(chapter).pending, true);
reachable = true;
await account.load();
assert.equal(account.progress(chapter).verified_xp, 7);
assert.equal(account.progress(chapter).pending, false);
assert.deepEqual(received[0], received[1], 'Retry must send the same immutable event');
assert.deepEqual(Object.keys(received[1]).sort(), ['p_content_version', 'p_event', 'p_lesson_id']);
assert.equal(createFoundationStore(course, { ...config, userId: 'b' }).progress(chapter).xp, 0);
assert.equal(account.progress({ ...chapter, content_version: '3.0.0' }).xp, 0);
const invalid = structuredClone(course);
const item = invalid.lessons.find(l => l.revised_assessment).revised_assessment;
item.closing[0].prompt = item.opening[0].prompt;
assert.throws(() => validateCourse(invalid), /Invalid revised assessment question/);
console.log('PASS: revised assessment validation, guest zero-score completion, offline retry, verified XP, account and version isolation.');
