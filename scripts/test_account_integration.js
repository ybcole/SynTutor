import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { accountUserId, bindSessionToken } from '../web/js/session-scope.js';
import { makeAttempt, validateAttempt } from '../web/js/quiz-core.js';
import { createQuizStore } from '../web/js/quiz-progress.js';

const clerk = { user: { id: 'user_a' }, session: { id: 'session_a', getToken: async () => 'a' } };
const accessA = bindSessionToken(clerk);
assert.equal(await accessA(), 'a');
let finishToken;
clerk.session.getToken = () => new Promise(resolve => { finishToken = resolve; });
const pending = accessA();
clerk.user = { id: 'user_b' };
clerk.session = { id: 'session_b', getToken: async () => 'b' };
finishToken('a');
await assert.rejects(pending, /session changed/);
await assert.rejects(accessA(), /session changed/);
assert.equal(await bindSessionToken(clerk)(), 'b');
clerk.session.is_anonymous = true;
const guest = bindSessionToken(clerk);
assert.equal(accountUserId(clerk), null);
clerk.session.is_anonymous = false;
assert.equal(await guest(), null);
const b = bindSessionToken(clerk);
clerk.session.getToken = async () => null;
await assert.rejects(b(), /unavailable/);

const bank = JSON.parse(readFileSync(new URL('../web/content/quizzes/bank.json', import.meta.url)));
const [a, other] = bank.assessments;
const draft = makeAttempt(bank, a, 310, crypto.randomUUID());
// jsonb object order is independent of JavaScript insertion order.
draft.presented = draft.presented.map(({ option_order, content_version, item_id }) =>
  ({ item_id, option_order, content_version }));
assert.doesNotThrow(() => validateAttempt(bank, draft));
const reordered = structuredClone(draft);
reordered.presented[0].option_order.reverse();
assert.throws(() => validateAttempt(bank, reordered), /manifest/);
const stale = { ...draft, attempt_id: crypto.randomUUID(), content_version: '0.9.0', submitted_at: draft.started_at, correct: 3 };
let saved = JSON.stringify({ attempts: { [stale.attempt_id]: stale }, drafts: {} });
const calls = [];
const store = createQuizStore(bank, {
  userId: 'user_a',
  storage: { getItem: () => saved, setItem: (_key, value) => { saved = value; } },
  client: {
    from: () => ({ select: async () => ({ data: [draft] }) }),
    rpc: async (_name, { p_attempt: attempt }) => {
      calls.push(attempt.content_version);
      return attempt.assessment_id === a.assessment_id
        ? { error: { code: '22023', message: 'Unknown published assessment version' } }
        : { data: { earned: 0 } };
    },
  },
});
await store.load();
assert.equal(store.draft(a).attempt_id, draft.attempt_id);
assert.equal(store.isArchived(stale), true);
assert.doesNotThrow(() => store.summary(a));
await store.move(draft.attempt_id, 1);
assert.equal(store.draft(a), null);
assert.equal(store.isArchived(store.attempts[draft.attempt_id]), true);
const fresh = await store.start(other, 321);
assert.equal(store.draft(other).attempt_id, fresh.attempt_id);
assert.deepEqual(calls, ['1.0.0', '1.0.0']);
assert(JSON.parse(saved).attempts[stale.attempt_id]);
console.log('PASS: session-bound token races, jsonb ordering, version archival and unblocked new attempts.');
