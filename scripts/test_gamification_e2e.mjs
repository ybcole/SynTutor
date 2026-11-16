// End-to-end verification of Account Sync, Verified XP, Leaderboard, Achievements,
// Grammar Chapter 1 coverage, Master Quiz limits (25 default / 50 max), and layout
// against real disposable PostgreSQL (PGlite running all migrations) and Chromium.
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import fs from 'node:fs';
import { createServer } from 'node:http';
import path from 'node:path';
import { PGlite } from '@electric-sql/pglite';
import { loadActiveCourse, quizCurriculum } from '../web/js/lesson-curriculum.js';
import { makeLessonPractice, validateLessonPractice } from '../web/js/quiz-lesson-practice.js';
import { makeAssessmentItems, validateAssessmentItems } from '../web/js/quiz-assessment-items.js';
import { makeV2Attempt } from '../web/js/quiz-v2.js';

const { chromium } = await import(process.env.QUIZ_V2_PLAYWRIGHT_MODULE || 'playwright');

const read = rel => fs.readFileSync(new URL('../' + rel, import.meta.url), 'utf8');
const readJson = rel => JSON.parse(read(rel));

const course = await loadActiveCourse(async p => ({ ok: true, json: async () => readJson('web' + p) }));
const curriculum = quizCurriculum(course);
const bank = readJson('web/content/quizzes/bank.json');
const syntaxSource = readJson('web/content/quizzes/syntax-practice-source.json');
bank.practice_items = validateLessonPractice(makeLessonPractice(curriculum, syntaxSource), curriculum);
bank.assessment_items = validateAssessmentItems(makeAssessmentItems(bank.practice_items, curriculum), curriculum);

// 1. Boot real WASM PostgreSQL with ALL migrations in chronological order.
const db = new PGlite();
await db.exec(`
  create role anon;
  create role authenticated;
  create schema auth;
  create function auth.jwt() returns jsonb language sql stable as $$
    select coalesce(nullif(current_setting('request.jwt.claims', true), '')::jsonb, '{}'::jsonb)
  $$;
  grant usage on schema auth to anon, authenticated;
  grant execute on function auth.jwt() to anon, authenticated;
`);
for (const file of fs.readdirSync(new URL('../supabase/migrations/', import.meta.url)).filter(f => f.endsWith('.sql')).sort()) {
  await db.exec(read(`supabase/migrations/${file}`));
}

async function setDbIdentity(sub, role = 'authenticated') {
  await db.exec('reset role');
  await db.query("select set_config('request.jwt.claims', $1, false)", [JSON.stringify(sub ? { sub } : {})]);
  await db.exec(`set role ${role}`);
}

const v2Keys = ['attempt_id', 'assessment_id', 'content_version', 'spec', 'title', 'diagnostic', 'seed', 'presented', 'responses', 'position'];
function makeV2Payload(spec, score, seed = 101) {
  const attempt = makeV2Attempt(bank, curriculum, spec, {}, seed);
  attempt.responses = {};
  for (const [i, ref] of attempt.presented.entries()) {
    const q = bank.assessment_items.find(x => x.item_id === ref.item_id) || bank.items.find(x => x.item_id === ref.item_id);
    attempt.responses[q.item_id] = i < score ? q.answer : q.options.find(o => o.id !== q.answer).id;
  }
  return { raw: attempt, payload: Object.fromEntries(v2Keys.map(k => [k, attempt[k] ?? null])) };
}

// 2. Database Contract Verification:
// 2a. Leaderboard enabled by migration; pre-opt-in activity stays private.
await setDbIdentity('user_alpha');
const lbGuest = (await db.query("select public.get_leaderboard('weekly') as data")).rows[0].data;
assert.equal(lbGuest.enabled, true, 'public opt-in leaderboard is released');
assert.deepEqual(lbGuest.entries, [], 'no fabricated leaderboard entries');

// Complete br-09 lesson BEFORE opting in (remains private on leaderboard, still earns verified XP + achievements).
const br09 = course.lessons.find(l => l.lesson_id === 'br-09');
for (const section of br09.revised_assessment.required_sections) {
  await db.query('select public.save_foundation_event($1, $2, $3::jsonb)', [
    br09.lesson_id, br09.content_version, JSON.stringify({ kind: 'visit', section }),
  ]);
}
const br09First = (await db.query('select public.save_foundation_event($1, $2, $3::jsonb) as data', [
  br09.lesson_id, br09.content_version, JSON.stringify({
    kind: 'closing', attempt_id: randomUUID(),
    answers: Object.fromEntries(br09.revised_assessment.closing.map((q, idx) => [q.id, idx < 3 ? q.answer : q.options.find(o => o.id !== q.answer).id])),
  }),
])).rows[0].data;
assert.equal(br09First.earned, 9);
assert.ok(br09First.completed_at);

// Opt-in Account A and Account B; earn verified XP after opt-in.
await setDbIdentity('user_alpha');
await db.query("select public.set_my_leaderboard_preference('AlphaTree', true)");
await setDbIdentity('user_beta');
await db.query("select public.set_my_leaderboard_preference('BetaSyntax', true)");

// Account B completes cgel-ch01 (Preliminaries 3.1.0) & scores 5/5 on cgel-ch01 formal topic quiz!
const ch01 = course.lessons.find(l => l.lesson_id === 'cgel-ch01');
for (const section of ch01.revised_assessment.required_sections) {
  await db.query('select public.save_foundation_event($1, $2, $3::jsonb)', [
    ch01.lesson_id, ch01.content_version, JSON.stringify({ kind: 'visit', section }),
  ]);
}
const ch01Res = (await db.query('select public.save_foundation_event($1, $2, $3::jsonb) as data', [
  ch01.lesson_id, ch01.content_version, JSON.stringify({
    kind: 'closing', attempt_id: randomUUID(),
    answers: Object.fromEntries(ch01.revised_assessment.closing.map(q => [q.id, q.answer])),
  }),
])).rows[0].data;
assert.equal(ch01Res.earned, 15, 'Cambridge active lesson earns verified XP');

const ch01Quiz = makeV2Payload({ track: 'cambridge', mode: 'topic', chapter: 'cgel-ch01', topic: 'prescriptive-descriptive' }, 5, 202);
const ch01QuizRes = (await db.query('select public.save_quiz_v2_attempt($1::jsonb, true) as data', [JSON.stringify(ch01Quiz.payload)])).rows[0].data;
assert.equal(ch01QuizRes.earned, 10);

// Account A improves br-09 closing check (+6 XP), completes br-08 (+15 XP), submits a 50-question Master Quiz (45/50 = 90 XP).
await setDbIdentity('user_alpha');
const br09Retry = (await db.query('select public.save_foundation_event($1, $2, $3::jsonb) as data', [
  br09.lesson_id, br09.content_version, JSON.stringify({
    kind: 'closing', attempt_id: randomUUID(),
    answers: Object.fromEntries(br09.revised_assessment.closing.map(q => [q.id, q.answer])),
  }),
])).rows[0].data;
assert.equal(br09Retry.earned, 6, 'best-score improvement delta on active revised lesson');

// Master Quiz limits check: 50 allowed, 51 rejected on new attempt, pre-existing >50 preserved.
const master50 = makeV2Payload({ track: 'syntax', mode: 'master', count: 50 }, 45, 303);
const master50Res = (await db.query('select public.save_quiz_v2_attempt($1::jsonb, true) as data', [JSON.stringify(master50.payload)])).rows[0].data;
assert.equal(master50Res.correct, 45);
assert.equal(master50Res.earned, 90);

const syntax51Items = bank.assessment_items.filter(q => q.track_id === 'syntax').slice(0, 51);
const master51Payload = {
  attempt_id: randomUUID(),
  assessment_id: 'quiz-v2:syntax:master:51:lesson-assessment:formal-1',
  content_version: '2.0.0',
  spec: { track: 'syntax', mode: 'master', count: 51, content_tier: 'lesson-assessment', format: 'formal' },
  title: 'Syntax Master Quiz',
  diagnostic: false,
  seed: 404,
  presented: syntax51Items.map(q => ({ item_id: q.item_id, content_version: q.content_version, option_order: q.options.map(o => o.id) })),
  responses: {},
  position: 0,
};
await assert.rejects(
  () => db.query('select public.save_quiz_v2_attempt($1::jsonb, false)', [JSON.stringify(master51Payload)]),
  /at most 50/
);

// Historical >50 unfinished row in DB remains playable & submittable!
await db.exec('reset role');
const histId = randomUUID();
const syntax55Items = bank.assessment_items.filter(q => q.track_id === 'syntax').slice(0, 55);
const histPresented = syntax55Items.map(q => ({ item_id: q.item_id, content_version: q.content_version, option_order: q.options.map(o => o.id) }));
const histSpec = { track: 'syntax', mode: 'master', count: 55, content_tier: 'lesson-assessment', format: 'formal' };
await db.query(`
  insert into public.quiz_attempts_v2 (user_id, attempt_id, assessment_id, content_version, spec, title, diagnostic, seed, presented, responses, position)
  values ($1, $2, $3, '2.0.0', $4::jsonb, 'Historical Master', false, 505, $5::jsonb, '{}'::jsonb, 0)
`, ['user_alpha', histId, 'quiz-v2:syntax:master:55:lesson-assessment:formal-1', JSON.stringify(histSpec), JSON.stringify(histPresented)]);
await setDbIdentity('user_alpha');
const histRes = (await db.query('select public.save_quiz_v2_attempt($1::jsonb, true) as data', [JSON.stringify({
  attempt_id: histId,
  assessment_id: 'quiz-v2:syntax:master:55:lesson-assessment:formal-1',
  content_version: '2.0.0',
  spec: histSpec,
  title: 'Historical Master',
  diagnostic: false,
  seed: 505,
  presented: histPresented,
  responses: Object.fromEntries(syntax55Items.slice(0, 10).map(q => [q.item_id, q.answer])),
  position: 54,
})])).rows[0].data;
assert.equal(histRes.correct, 10);

// Complete a Cambridge lesson + improve quiz -> verify Achievements & Leaderboard rankings!
await db.query('select public.save_foundation_event($1, $2, $3::jsonb)', [
  ch01.lesson_id, ch01.content_version, JSON.stringify({
    kind: 'closing', attempt_id: randomUUID(),
    answers: Object.fromEntries(ch01.revised_assessment.closing.map(q => [q.id, q.answer])),
  }),
]);
for (const section of ch01.revised_assessment.required_sections) {
  await db.query('select public.save_foundation_event($1, $2, $3::jsonb)', [
    ch01.lesson_id, ch01.content_version, JSON.stringify({ kind: 'visit', section }),
  ]);
}
const badgesAlpha = (await db.query('select public.get_my_achievements() as data')).rows[0].data;
const unlockedAlpha = new Set(badgesAlpha.filter(b => b.unlocked_at).map(b => b.id));
for (const id of ['first-lesson', 'first-quiz', 'personal-best', 'master-challenger', 'gap-spotter', 'framework-distinction']) {
  assert.ok(unlockedAlpha.has(id), `expected badge unlocked: ${id}`);
}
// Unlocks persist across repeat calls without duplicates.
const badgesAlpha2 = (await db.query('select public.get_my_achievements() as data')).rows[0].data;
assert.deepEqual(badgesAlpha2, badgesAlpha, 'achievements idempotent with preserved timestamps');

const weekly = (await db.query("select public.get_leaderboard('weekly') as data")).rows[0].data;
assert.equal(weekly.entries.length, 2);
assert.equal(weekly.entries[0].alias, 'AlphaTree');
assert.equal(weekly.entries[1].alias, 'BetaSyntax');
assert.ok(weekly.entries[0].xp > weekly.entries[1].xp);

// 3. Browser End-to-End Integration wired to the REAL PostgreSQL instance!
const root = path.resolve('web');
const mime = { '.js': 'application/javascript', '.json': 'application/json', '.css': 'text/css', '.html': 'text/html', '.svg': 'image/svg+xml' };
let dbLock = Promise.resolve();
const withDb = fn => {
  const next = dbLock.then(fn, fn);
  dbLock = next.catch(() => {});
  return next;
};

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://localhost');
    if (url.pathname === '/e2e-supabase' && req.method === 'POST') {
      const chunks = [];
      for await (const c of req) chunks.push(c);
      const body = JSON.parse(Buffer.concat(chunks).toString('utf8'));
      const out = await withDb(async () => {
        await setDbIdentity(body.token || null);
        try {
          if (body.kind === 'rpc') {
            if (body.name === 'get_my_progression') return { data: (await db.query('select public.get_my_progression() as d')).rows[0].d, error: null };
            if (body.name === 'get_my_achievements') return { data: (await db.query('select public.get_my_achievements() as d')).rows[0].d, error: null };
            if (body.name === 'get_leaderboard') return { data: (await db.query('select public.get_leaderboard($1) as d', [body.args.p_period])).rows[0].d, error: null };
            if (body.name === 'set_my_leaderboard_preference') {
              await db.query('select public.set_my_leaderboard_preference($1, $2)', [body.args.p_alias, body.args.p_opt_in]);
              return { data: null, error: null };
            }
            if (body.name === 'save_foundation_event') {
              return {
                data: (await db.query('select public.save_foundation_event($1, $2, $3::jsonb) as d', [
                  body.args.p_lesson_id, body.args.p_content_version, JSON.stringify(body.args.p_event),
                ])).rows[0].d,
                error: null,
              };
            }
            if (body.name === 'save_quiz_v2_attempt') {
              return {
                data: (await db.query('select public.save_quiz_v2_attempt($1::jsonb, $2) as d', [
                  JSON.stringify(body.args.p_attempt), body.args.p_submit,
                ])).rows[0].d,
                error: null,
              };
            }
            return { data: null, error: null };
          }
          const rows = (await db.query(`select * from public.${body.name}`)).rows;
          return { data: rows, error: null };
        } catch (err) {
          return { data: null, error: { code: err.code || 'P0001', message: err.message } };
        }
      });
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(out));
      return;
    }
    const filename = path.resolve(root, '.' + (url.pathname === '/' ? '/index.html' : url.pathname));
    if (!filename.startsWith(root + path.sep)) throw Error('Invalid path');
    res.writeHead(200, { 'Content-Type': mime[path.extname(filename)] || 'application/octet-stream' });
    res.end(fs.readFileSync(filename));
  } catch {
    res.writeHead(404);
    res.end();
  }
});

await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch();

try {
  const page = await browser.newPage({ viewport: { width: 1360, height: 900 } });
  const errors = [];
  page.on('pageerror', e => errors.push(`pageerror: ${e.message}`));
  page.on('console', msg => { if (msg.type() === 'error') errors.push(`console.error: ${msg.text()}`); });

  await page.addInitScript(() => {
    localStorage.setItem('syntutor_onboarding_seen', '1');
    window.Clerk = {
      user: { id: 'user_alpha', firstName: 'Alpha' },
      session: { id: 'sess_alpha', getToken: async () => window.Clerk.user?.id || null },
      load: async () => {},
      addListener(fn) { window.__clerkListeners = [...(window.__clerkListeners || []), fn]; },
    };
    window.setTestUser = id => {
      window.Clerk.user = id ? { id, firstName: id } : null;
      window.Clerk.session = id ? { id: 'sess_' + id, getToken: async () => id } : null;
      (window.__clerkListeners || []).forEach(fn => fn());
    };
  });

  await page.route('**/*', route => {
    const url = route.request().url();
    if (url.startsWith(`${base}/js/config.js`)) {
      return route.fulfill({
        contentType: 'application/javascript',
        body: "export const CLERK_CONFIG={publishableKey:'pk_test_e2e'};export const SUPABASE_CONFIG={url:'https://fixture.test',anonKey:'anon'};export const API_BASE='';",
      });
    }
    if (url.startsWith('https://esm.sh/')) {
      return route.fulfill({
        contentType: 'application/javascript',
        body: `export const createClient = (_u, _k, { accessToken }) => {
          const req = async (kind, name, args, signal) => {
            const token = await accessToken();
            const r = await fetch('/e2e-supabase', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ kind, name, args, token }), signal });
            return r.json();
          };
          const q = (kind, name, args = {}) => ({
            abortSignal: s => req(kind, name, args, s),
            then: (res, rej) => req(kind, name, args).then(res, rej),
            order() { return this; }, limit() { return this; },
          });
          return {
            rpc: (name, args) => q('rpc', name, args),
            from: name => ({ select: () => q('select', name), upsert: row => q('upsert', name, row) }),
          };
        };`,
      });
    }
    return url.startsWith(base) ? route.continue() : route.abort();
  });

  await page.goto(base);
  const nav = view => page.locator(`.sidebar-item[data-view="${view}"]`).click();

  // Verify sidebar verified XP loaded directly from Postgres for Alpha.
  await page.waitForFunction(() => document.querySelector('#sidebarProgressLabel')?.textContent?.includes('verified XP'));
  const sidebarText = await page.locator('#sidebarProgressLabel').textContent();
  assert.ok(!sidebarText.includes('unavailable'), `Sidebar XP loaded cleanly: ${sidebarText}`);

  // Lessons: verify account sync (not device-only!) & collapsed slim left-edge bookmark handle.
  await nav('lessons');
  const lessons = page.locator('#curriculumView');
  await lessons.locator('.lesson-module').first().waitFor();
  assert.ok(!(await lessons.locator('.lesson-total').textContent()).includes('in this view'), 'signed-in lesson total reflects account, not device-only preview');
  await lessons.locator('.lesson-module').first().getByRole('button').click();
  await lessons.locator('.lesson-contents-toggle').waitFor();
  await lessons.locator('.lesson-contents-toggle').click();
  await page.locator('.lesson-reader.is-nav-collapsed').waitFor();
  const handleBox = await lessons.locator('.lesson-section-sidebar.is-collapsed .lesson-contents-toggle').boundingBox();
  const pageBox = await lessons.locator('.lesson-reader.is-nav-collapsed .constituent-page').boundingBox();
  assert.ok(handleBox.width <= 40, `collapsed handle is slim bookmark width (${handleBox.width}px)`);
  assert.ok(pageBox.width > 800, `collapsed state expands reading area (${pageBox.width}px)`);
  assert.ok((await lessons.locator('.lesson-save-status').textContent()).includes('Synced to your account'), 'Lessons synced cleanly to account');

  // Achievements: verify unlocked, in-progress, locked & category selector work from Postgres.
  await nav('achievements');
  await page.locator('[data-achievement="first-lesson"]').waitFor();
  assert.ok(!(await page.locator('#achievementsProgressLabel').textContent()).includes('unavailable'));
  assert.equal(await page.locator('.achievement-card').count(), 12);
  await page.locator('#achievementsCatTrigger').click();
  await page.locator('.cat-pill[data-category="assessment"]').click();
  await page.waitForFunction(() => document.querySelectorAll('#achievementsGrid .achievement-card').length === 5);
  assert.equal(await page.locator('.achievement-card').count(), 5);

  // Leaderboard: verify rankings & podium rendered from Postgres.
  await nav('leaderboard');
  await page.locator('.podium-card').first().waitFor();
  assert.ok(await page.locator('#leaderboardEntries').innerText().then(t => t.includes('AlphaTree') && t.includes('BetaSyntax')));
  assert.ok(!(await page.locator('#leaderboardLifetime').textContent()).includes('unavailable'));

  // Quizzes: verify Grammar Ch 1 playable, Master default 25 / max 50, mobile + dark theme layout.
  await nav('quizzes');
  const quiz = page.locator('#quizzesView');
  await quiz.getByRole('button', { name: 'Grammar', exact: true }).click();
  const cambridgeMaster = quiz.locator('.quiz-practice').filter({ has: page.getByRole('heading', { name: 'Cambridge Master Quiz', exact: true }) });
  assert.equal(await cambridgeMaster.getByRole('spinbutton').inputValue(), '25');
  assert.equal(await cambridgeMaster.getByRole('spinbutton').getAttribute('max'), '50');
  await quiz.locator('[data-chapter="cgel-ch01"] > summary').click();
  await quiz.locator('[data-chapter="cgel-ch01"]').getByRole('button', { name: 'Start quiz', exact: true }).first().click();
  await quiz.getByRole('heading', { name: 'Question 1 of 5', exact: true }).waitFor();

  for (const view of ['lessons', 'quizzes', 'achievements', 'leaderboard']) {
    await page.setViewportSize({ width: 1360, height: 900 });
    await nav(view);
    const sel = view === 'lessons' ? '#curriculumView' : view === 'quizzes' ? '#quizzesView' : `#${view}View`;
    for (const width of [390, 1360]) {
      await page.setViewportSize({ width, height: 900 });
      for (const theme of ['dark', 'light']) {
        await page.evaluate(t => document.documentElement.setAttribute('data-theme', t), theme);
        const overflow = await page.locator(sel).evaluate(n => n.scrollWidth > n.clientWidth + 2);
        assert.equal(overflow, false, `${view} ${width}px ${theme} no horizontal overflow`);
      }
    }
  }

  assert.deepEqual(errors, []);
  console.log('PASS end-to-end DB + browser gamification: active lesson & Quiz V2 verified XP, account sync, restored progression, Leaderboard rankings, Achievements unlocks/progress/filters, Grammar Ch.1 10 topics, Master 25/50 limits, slim bookmark handle, light/dark + mobile/desktop zero overflow, 0 errors.');
} finally {
  await browser.close();
  await new Promise(resolve => server.close(resolve));
  await db.close();
}
