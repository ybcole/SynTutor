// Test the generated candidate and actual migration functions in disposable PostgreSQL.
import { PGlite } from '@electric-sql/pglite';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { makeAttempt } from '../web/js/quiz-core.js';

const root = new URL('../', import.meta.url);
const cwd = fileURLToPath(root);
const read = path => readFileSync(new URL(path, root), 'utf8');
const candidate = execFileSync(process.execPath, ['scripts/compose_foundations_preview.js'], { cwd });
const renderSeed = input => execFileSync('python3', ['scripts/seed_foundations.py', '--course', '-'],
  { input, cwd, encoding: 'utf8' });
const seed = renderSeed(candidate);
const course = JSON.parse(candidate);
const published = JSON.parse(read('web/content/lessons/course.json'));
const chapters = course.lessons.filter(lesson => lesson.revised_assessment);
const cambridge = published.lessons.find(lesson => lesson.lesson_id === 'cgel-clauses');
assert.deepEqual(course.lessons.find(lesson => lesson.lesson_id === cambridge.lesson_id), cambridge);
assert.equal(chapters.length, 11);

const db = new PGlite();
try {
  const scalar = async (sql, params) => Object.values((await db.query(sql, params)).rows[0])[0];
  await db.exec(`
    create role anon; create role authenticated; create schema auth;
    create function auth.jwt() returns jsonb language sql stable as $$
      select coalesce(nullif(current_setting('request.jwt.claims', true), '')::jsonb, '{}'::jsonb)
    $$;
    grant usage on schema auth to anon, authenticated;
    grant execute on function auth.jwt() to anon, authenticated;
  `);
  for (const migration of readdirSync(new URL('supabase/migrations/', root)).sort()) {
    if (migration.endsWith('.sql')) await db.exec(read(`supabase/migrations/${migration}`));
  }
  await db.exec(seed);
  await db.exec(seed);
  assert.equal(await scalar('select count(*)::int from public.foundation_assessments'), 11);
  assert.equal(await scalar('select count(*)::int from public.foundation_active'), 0);
  const edited = structuredClone(course);
  const question = edited.lessons[0].revised_assessment.closing[0];
  question.answer = question.options.find(option => option.id !== question.answer).id;
  edited.lessons[1].content_version = '2.0.1';
  await assert.rejects(() => db.exec(renderSeed(JSON.stringify(edited))),
    /Foundations seed differs from stored versions: br-01@2\.0\.0/);
  await db.exec('rollback');
  assert.equal(await scalar('select count(*)::int from public.foundation_assessments'), 11,
    'a mismatched key rolls back other additions in the same seed');

  async function identity(userId) {
    await db.exec('reset role');
    await db.query("select set_config('request.jwt.claims',$1,false)", [JSON.stringify({ sub: userId })]);
    await db.exec('set role authenticated');
  }
  function legacy(lesson) {
    const keys = ['predict', 'guided', 'transfer', 'exit'];
    return scalar('select public.save_lesson_progress($1,$2,$3::jsonb)', [
      lesson.lesson_id, lesson.content_version,
      JSON.stringify({
        responses: Object.fromEntries(keys.map(key => [key, lesson[key].answer])),
        visited: lesson.completion.required_stages, stage: 5,
      }),
    ]);
  }
  function event(lesson, payload) {
    return scalar('select public.save_foundation_event($1,$2,$3::jsonb)',
      [lesson.lesson_id, lesson.content_version, JSON.stringify(payload)]);
  }
  function attempt(lesson, kind, correct) {
    return {
      kind, attempt_id: randomUUID(),
      answers: Object.fromEntries(lesson.revised_assessment[kind].map((question, index) => [
        question.id, index < correct ? question.answer :
          question.options.find(option => option.id !== question.answer).id,
      ])),
    };
  }
  async function switchVersions(active) {
    await db.exec('reset role');
    await db.transaction(async tx => {
      for (const lesson of chapters) {
        await tx.query('select public.set_foundation_active_version($1,$2)',
          [lesson.lesson_id, active ? lesson.content_version : null]);
      }
    });
  }
  const xp = id => scalar('select xp from public.player_stats where user_id=$1', [id]);
  const count = table => scalar(`select count(*)::int from public.${table}`);

  await identity('returning');
  for (const chapter of published.lessons) assert.equal((await legacy(chapter)).earned, 15);
  const bank = JSON.parse(read('web/content/quizzes/bank.json'));
  const quiz = makeAttempt(bank, bank.assessments[0], 310);
  quiz.responses = Object.fromEntries(quiz.presented.map(({ item_id }) =>
    [item_id, bank.items.find(item => item.item_id === item_id).answer]));
  const payload = Object.fromEntries(['attempt_id', 'assessment_id', 'content_version', 'seed', 'presented', 'responses', 'position']
    .map(key => [key, quiz[key]]));
  assert.equal((await scalar('select public.save_quiz_attempt($1::jsonb,true)', [JSON.stringify(payload)])).earned, 10);
  assert.equal(await xp('returning'), 190);

  await switchVersions(true);
  assert.equal(await count('foundation_active'), 11);
  assert.equal(await xp('returning'), 25, 'Cambridge and quiz XP survive the cutover');
  await identity('returning');
  assert.equal(await count('foundation_progress'), 0, 'legacy completion does not count as revised progress');
  assert.equal(await count('lesson_progress'), 12, 'legacy history is preserved');

  await identity('new-reader');
  assert.equal((await legacy(cambridge)).completed_at, null);
  for (const chapter of [...chapters].reverse()) {
    const opening = await event(chapter, attempt(chapter, 'opening', 2));
    assert.equal(opening.opening_correct, 2);
    assert.equal(opening.earned, 0);
    for (const section of chapter.revised_assessment.required_sections) {
      await event(chapter, { kind: 'visit', section });
    }
    const closing = attempt(chapter, 'closing', 3);
    const first = await event(chapter, closing);
    assert.ok(first.completed_at, chapter.lesson_id);
    assert.equal(first.earned, 9);
    assert.equal((await event(chapter, closing)).earned, 0);
  }
  assert.equal((await legacy(cambridge)).earned, 15, 'revised Chapter 2 satisfies the Cambridge prerequisite');
  assert.equal(await xp('new-reader'), 114);

  await switchVersions(false);
  assert.equal(await count('foundation_active'), 0);
  assert.equal(await xp('returning'), 190);
  assert.equal(await xp('new-reader'), 15, 'Cambridge completion survives rollback');
  assert.equal(await count('foundation_progress'), 11, 'revised history survives rollback');
} finally {
  await db.close();
}
console.log('PASS: actual seed, immutable-key mismatch rollback, eleven-version cutover, account isolation, revised scoring/replay, Cambridge and quiz XP, and rollback.');
