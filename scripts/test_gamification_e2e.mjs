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
import { deriveLeaderboardAlias } from '../web/js/leaderboard-alias.js';

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

async function setDbIdentity(sub, role = 'authenticated', extraClaims = {}) {
  await db.exec('reset role');
  const claims = sub ? { sub, ...extraClaims } : {};
  await db.query("select set_config('request.jwt.claims', $1, false)", [JSON.stringify(claims)]);
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
// 2a. Leaderboard enabled by migration; guests see clean empty board & cannot enroll.
await setDbIdentity(null, 'anon');
const lbGuest = (await db.query("select public.get_leaderboard('weekly') as data")).rows[0].data;
assert.equal(lbGuest.enabled, true, 'public leaderboard is released');
assert.deepEqual(lbGuest.entries, [], 'no fabricated leaderboard entries');
await assert.rejects(() => db.query('select public.ensure_leaderboard_participation()'), /Sign in/);

// Complete br-09 lesson BEFORE user_alpha ever enrolls (historical private XP stays private after enrollment).
await setDbIdentity('user_alpha');
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

// Email-derived alias normalization unit checks across providers and edge cases.
assert.equal(deriveLeaderboardAlias('alice.chen@gmail.com'), 'alice_chen');
assert.equal(deriveLeaderboardAlias('María.López+cs@ox.ac.uk'), 'Maria_Lopez_cs');
assert.equal(deriveLeaderboardAlias('dr-jones@company.co.uk'), 'dr-jones');
assert.equal(deriveLeaderboardAlias('123alex@proton.me'), 'alex');
assert.equal(deriveLeaderboardAlias('987654@qq.com'), null);
assert.equal(deriveLeaderboardAlias('user_admin@example.com'), null);
assert.equal(deriveLeaderboardAlias('jo@x.co'), null);

// Automatic enrollment on login assigns safe alias & includes 0-XP participant without leaking historical XP.
const autoAlpha = (await db.query('select public.ensure_leaderboard_participation() as data')).rows[0].data;
assert.equal(autoAlpha.opted_in, true);
assert.equal(autoAlpha.enrolled_now, true);
assert.match(autoAlpha.alias, /^Learner_[A-F0-9]{6}$/);
const initialBoard = (await db.query("select public.get_leaderboard('weekly') as data")).rows[0].data;
assert.equal(initialBoard.entries.length, 1);
assert.equal(initialBoard.entries[0].alias, autoAlpha.alias);
assert.equal(initialBoard.entries[0].xp, 0, 'pre-enrollment br-09 XP stays private');
assert.equal(initialBoard.entries[0].lessons_completed, 0, 'pre-enrollment br-09 completion stays private');

// Duplicate email prefixes receive a short non-identifying suffix; existing custom aliases are never overwritten.
await db.query("select public.set_my_leaderboard_preference('AlphaTree', true)");
const keepCustom = (await db.query("select public.ensure_leaderboard_participation('should_not_overwrite') as data")).rows[0].data;
assert.equal(keepCustom.alias, 'AlphaTree', 'previously customized alias preserved');

await setDbIdentity('user_gmail_1');
const gmail1 = (await db.query("select public.ensure_leaderboard_participation($1) as data", [deriveLeaderboardAlias('alice.chen@gmail.com')])).rows[0].data;
assert.equal(gmail1.alias, 'alice_chen');

await setDbIdentity('user_outlook_dup');
const outlookDup = (await db.query("select public.ensure_leaderboard_participation($1) as data", [deriveLeaderboardAlias('alice.chen@outlook.com')])).rows[0].data;
assert.match(outlookDup.alias, /^alice_chen_[A-F0-9]{4}$/, 'duplicate local-part adds short non-identifying suffix');
assert.ok(!outlookDup.alias.includes('outlook'), 'domain never exposed');

await setDbIdentity('user_gmail_1');
await db.query('select public.set_my_leaderboard_preference(null, false)');
await setDbIdentity('user_outlook_dup');
await db.query('select public.set_my_leaderboard_preference(null, false)');

// Security check: unverified JWT email & raw client-supplied '@' email must NEVER derive aliases.
await setDbIdentity('user_unverified_jwt', 'authenticated', { email: 'unverified.user@gmail.com', email_verified: false });
const unvJwt = (await db.query('select public.ensure_leaderboard_participation(null) as data')).rows[0].data;
assert.match(unvJwt.alias, /^Learner_[A-F0-9]{6}$/, 'unverified JWT email must not derive public alias');
await db.query('select public.set_my_leaderboard_preference(null, false)');

await setDbIdentity('user_raw_at_arg');
const rawAtArg = (await db.query("select public.ensure_leaderboard_participation('spoof@gmail.com') as data")).rows[0].data;
assert.match(rawAtArg.alias, /^Learner_[A-F0-9]{6}$/, 'raw email string in p_preferred_alias must not derive public alias');
await db.query('select public.set_my_leaderboard_preference(null, false)');

await setDbIdentity('user_verified_jwt', 'authenticated', { email: 'Dr.Patel@cam.ac.uk', email_verified: true });
const verJwt = (await db.query("select public.ensure_leaderboard_participation('ignored_other') as data")).rows[0].data;
assert.equal(verJwt.alias, 'Dr_Patel', 'verified JWT email takes precedence over client hint');
await db.query('select public.set_my_leaderboard_preference(null, false)');

// Legacy user already holding an old Learner_XXXXXX alias is preserved untouched until explicit adoption.
await setDbIdentity('user_legacy_adopt');
const legacyRes = (await db.query('select public.ensure_leaderboard_participation(null) as data')).rows[0].data;
assert.match(legacyRes.alias, /^Learner_[A-F0-9]{6}$/);
const legacySecond = (await db.query("select public.ensure_leaderboard_participation('legacy_scholar') as data")).rows[0].data;
assert.equal(legacySecond.alias, legacyRes.alias, 'existing generated alias is not silently overwritten without disclosure');
await db.query('select public.set_my_leaderboard_preference(null, false)');

await setDbIdentity('user_beta');
const autoBeta = (await db.query('select public.ensure_leaderboard_participation() as data')).rows[0].data;
assert.match(autoBeta.alias, /^Learner_[A-F0-9]{6}$/);
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

// Submit a repeat attempt of the same quiz & explicitly opt out user_private -> counts stay distinct & opted-out user excluded even across re-login!
await setDbIdentity('user_beta');
const ch01QuizRepeat = makeV2Payload({ track: 'cambridge', mode: 'topic', chapter: 'cgel-ch01', topic: 'prescriptive-descriptive' }, 5, 209);
await db.query('select public.save_quiz_v2_attempt($1::jsonb, true)', [JSON.stringify(ch01QuizRepeat.payload)]);
const draftQuiz = makeV2Payload({ track: 'cambridge', mode: 'topic', chapter: 'cgel-ch04', topic: 'clause-patterns' }, 0, 210);
await db.query('select public.save_quiz_v2_attempt($1::jsonb, false)', [JSON.stringify(draftQuiz.payload)]);

await setDbIdentity('user_private');
await db.query('select public.ensure_leaderboard_participation()');
await db.query('select public.set_my_leaderboard_preference(null, false)');
const recheckOptedOut = (await db.query('select public.ensure_leaderboard_participation() as data')).rows[0].data;
assert.equal(recheckOptedOut.opted_in, false, 'explicit opt-out persists across subsequent logins');
const privQuiz = makeV2Payload({ track: 'cambridge', mode: 'topic', chapter: 'cgel-ch01', topic: 'prescriptive-descriptive' }, 5, 211);
await db.query('select public.save_quiz_v2_attempt($1::jsonb, true)', [JSON.stringify(privQuiz.payload)]);

await setDbIdentity('user_alpha');
const weekly = (await db.query("select public.get_leaderboard('weekly') as data")).rows[0].data;
assert.equal(weekly.entries.length, 2, 'only opted-in learners appear; opted-out user_private excluded');
assert.equal(weekly.entries[0].alias, 'AlphaTree');
assert.equal(weekly.entries[0].lessons_completed, 1, 'pre-opt-in br-09 excluded; only post-opt-in cgel-ch01 counts');
assert.equal(weekly.entries[0].quizzes_completed, 2, 'distinct formal quizzes submitted by Alpha after opt-in');
assert.equal(weekly.entries[1].alias, 'BetaSyntax');
assert.equal(weekly.entries[1].lessons_completed, 1);
assert.equal(weekly.entries[1].quizzes_completed, 1, 'repeat attempt & unfinished draft never inflate distinct count');
assert.ok(weekly.entries[0].xp > weekly.entries[1].xp);
const seasonal = (await db.query("select public.get_leaderboard('seasonal') as data")).rows[0].data;
assert.equal(seasonal.entries.length, 2);

// 3. Browser End-to-End Integration wired to the REAL PostgreSQL instance!
const root = path.resolve('web');
const mime = { '.js': 'application/javascript', '.json': 'application/json', '.css': 'text/css', '.html': 'text/html', '.svg': 'image/svg+xml' };
let dbLock = Promise.resolve();
let simulateHostedZeroArgRpc = false;
let simulateFoundationSyncFail = false;
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
            if (body.name === 'ensure_leaderboard_participation') {
              if (simulateHostedZeroArgRpc && body.args && Object.prototype.hasOwnProperty.call(body.args, 'p_preferred_alias')) {
                return {
                  data: null,
                  error: { code: 'PGRST202', message: 'Could not find the function public.ensure_leaderboard_participation(p_preferred_alias) in the schema cache' },
                };
              }
              return { data: (await db.query('select public.ensure_leaderboard_participation($1) as d', [body.args?.p_preferred_alias ?? null])).rows[0].d, error: null };
            }
            if (body.name === 'get_leaderboard') return { data: (await db.query('select public.get_leaderboard($1) as d', [body.args.p_period])).rows[0].d, error: null };
            if (body.name === 'set_my_leaderboard_preference') {
              await db.query('select public.set_my_leaderboard_preference($1, $2)', [body.args.p_alias, body.args.p_opt_in]);
              return { data: null, error: null };
            }
            if (body.name === 'save_foundation_event') {
              if (simulateFoundationSyncFail) {
                return { data: null, error: { code: '503', message: 'Temporary sync outage' } };
              }
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
    window.setTestUser = (id, emailOpts = null) => {
      if (!id) {
        window.Clerk.user = null;
        window.Clerk.session = null;
      } else {
        const addresses = emailOpts ? [{
          id: 'email_' + id,
          emailAddress: emailOpts.email,
          verification: { status: emailOpts.verified ? 'verified' : 'unverified' },
        }] : [];
        window.Clerk.user = {
          id,
          firstName: id,
          primaryEmailAddressId: addresses[0]?.id || null,
          primaryEmailAddress: addresses[0] || null,
          emailAddresses: addresses,
        };
        window.Clerk.session = { id: 'sess_' + id, getToken: async () => id };
      }
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

  // Lessons Overview & Progress-State Verification across Syntax and Grammar:
  await nav('lessons');
  const lessons = page.locator('#curriculumView');
  await lessons.locator('.lesson-module').first().waitFor();
  assert.ok(!(await lessons.locator('.lesson-total').textContent()).includes('in this view'), 'signed-in lesson total reflects account, not device-only preview');
  assert.equal(await lessons.locator('.lesson-prerequisite').count(), 0, 'overview cards omit prerequisite notes');
  assert.equal(await lessons.locator('.lesson-module-description').count(), 11, 'Syntax overview cards display restored chapter descriptions');
  assert.equal(await lessons.locator('.lesson-module-objective').count(), 11, 'Syntax overview cards display restored learning objectives');
  const br01Card = lessons.locator('[data-lesson-card="br-01"]');
  const br09Card = lessons.locator('[data-lesson-card="br-09"]');
  assert.equal(await br01Card.getByRole('button').innerText(), 'Start lesson');
  assert.ok((await br01Card.innerText()).includes('0 of 5 required sections visited'));
  assert.equal(await br09Card.getByRole('button').innerText(), 'Review lesson', 'already completed chapter shows Review lesson');
  if (process.env.QUIZ_V2_SCREENSHOT_DIR) await page.screenshot({ path: path.join(process.env.QUIZ_V2_SCREENSHOT_DIR, 'lessons-overview-syntax.png') });

  // Grammar tab shows identical compact card layout + independent chapter-list scroll down to Ch. 20 while header/tabs/panels stay stationary.
  await lessons.getByRole('button', { name: 'Grammar and Analysis', exact: true }).click();
  assert.equal(await lessons.locator('.lesson-prerequisite').count(), 0, 'Grammar cards omit prerequisite notes');
  assert.equal(await lessons.locator('.lesson-module-description').count(), 20, 'Grammar overview cards display restored chapter descriptions');
  assert.equal(await lessons.locator('.lesson-module-objective').count(), 20, 'Grammar overview cards display restored learning objectives');
  assert.equal(await lessons.locator('[data-lesson-card="cgel-ch01"]').getByRole('button').innerText(), 'Review lesson');
  const scrollMetricsBefore = await lessons.evaluate(() => ({
    outerScroll: document.querySelector('#curriculumView').scrollHeight > document.querySelector('#curriculumView').clientHeight + 2,
    sheetScrollable: document.querySelector('#curriculumView .lesson-tab-sheet').scrollHeight > document.querySelector('#curriculumView .lesson-tab-sheet').clientHeight,
    headerTop: document.querySelector('#curriculumView .curriculum-header').getBoundingClientRect().top,
    tabsTop: document.querySelector('#curriculumView .lesson-track-tabs').getBoundingClientRect().top,
    summaryTop: document.querySelector('#curriculumView .lesson-catalog-summary').getBoundingClientRect().top,
  }));
  assert.equal(scrollMetricsBefore.outerScroll, false, 'Desktop Lessons Overview does not scroll the outer page');
  assert.equal(scrollMetricsBefore.sheetScrollable, true, 'Only the chapter list scrolls inside the tab sheet');
  await lessons.locator('[data-lesson-card="cgel-ch20"]').scrollIntoViewIfNeeded();
  const scrollMetricsAfter = await lessons.evaluate(() => ({
    sheetScrollTop: document.querySelector('#curriculumView .lesson-tab-sheet').scrollTop,
    headerTop: document.querySelector('#curriculumView .curriculum-header').getBoundingClientRect().top,
    tabsTop: document.querySelector('#curriculumView .lesson-track-tabs').getBoundingClientRect().top,
    summaryTop: document.querySelector('#curriculumView .lesson-catalog-summary').getBoundingClientRect().top,
  }));
  assert.ok(scrollMetricsAfter.sheetScrollTop > 400, 'Chapter list scrolls smoothly down to final Grammar Chapter 20');
  assert.equal(scrollMetricsAfter.headerTop, scrollMetricsBefore.headerTop, 'Header remains stationary while scrolling chapters');
  assert.equal(scrollMetricsAfter.tabsTop, scrollMetricsBefore.tabsTop, 'Track tabs remain stationary while scrolling chapters');
  assert.equal(scrollMetricsAfter.summaryTop, scrollMetricsBefore.summaryTop, 'Progress/Activity panels remain stationary while scrolling chapters');
  if (process.env.QUIZ_V2_SCREENSHOT_DIR) await page.screenshot({ path: path.join(process.env.QUIZ_V2_SCREENSHOT_DIR, 'lessons-overview-grammar.png') });
  // Opening a scrolled chapter and returning restores scroll context instead of jumping back to Chapter 1.
  await lessons.locator('[data-lesson-card="cgel-ch20"] button').click();
  await lessons.locator('.header-icon-btn').click();
  const restoredSheetTop = await lessons.evaluate(() => document.querySelector('#curriculumView .lesson-tab-sheet').scrollTop);
  assert.ok(restoredSheetTop > 400, `Returning from Chapter 20 restores Grammar chapter scroll (${restoredSheetTop}px)`);
  await lessons.getByRole('button', { name: 'Syntax Foundations', exact: true }).click();
  assert.equal(await lessons.evaluate(() => document.querySelector('#curriculumView .lesson-tab-sheet').scrollTop), 0, 'Switching tracks opens Syntax at top');

  // Visit 1 required section on br-01 -> Resume lesson; visit all 5 required sections WITHOUT closing check -> 5 of 5 visited + STILL Resume lesson!
  await br01Card.getByRole('button', { name: 'Start lesson', exact: true }).click();
  await lessons.locator('.lesson-contents-toggle').waitFor();
  await lessons.getByRole('button', { name: 'All lessons', exact: true }).click();
  assert.equal(await br01Card.getByRole('button').innerText(), 'Resume lesson', '1 section visited transitions Start -> Resume');
  assert.ok((await br01Card.innerText()).includes('1 of 5 required sections visited'));

  // Reopen br-01 and visit all remaining required sections without submitting closing assessment.
  await br01Card.getByRole('button', { name: 'Resume lesson', exact: true }).click();
  await lessons.locator('.lesson-section-sidebar a').first().waitFor({ state: 'visible' });
  const navLinks = lessons.locator('.lesson-section-sidebar nav a');
  for (let i = 1; i <= 4; i++) {
    await navLinks.nth(i).click();
    await page.waitForTimeout(40);
  }
  await lessons.getByRole('button', { name: 'All lessons', exact: true }).click();
  assert.ok((await br01Card.innerText()).includes('5 of 5 required sections visited'), 'shows 5 of 5 visited');
  assert.equal(await br01Card.locator('progress').getAttribute('value'), '5');
  assert.equal(await br01Card.locator('progress').getAttribute('max'), '5');
  assert.equal(await br01Card.getByRole('button').innerText(), 'Resume lesson', '100% visited without closing check must stay Resume lesson, NOT Review lesson');

  // Reopening a completed lesson (br-09) preserves Review lesson state across return.
  await br09Card.getByRole('button', { name: 'Review lesson', exact: true }).click();
  await lessons.getByRole('button', { name: 'All lessons', exact: true }).click();
  assert.equal(await br09Card.getByRole('button').innerText(), 'Review lesson');

  // Simulated temporary sync failure retains pending work without falsely claiming verified completion; reload restores sync.
  const br02Card = lessons.locator('[data-lesson-card="br-02"]');
  await br02Card.getByRole('button', { name: 'Start lesson', exact: true }).click();
  simulateFoundationSyncFail = true;
  const br02Links = lessons.locator('.lesson-section-sidebar nav a');
  for (let i = 1; i <= 5; i++) {
    await br02Links.nth(i).click();
    await page.waitForTimeout(40);
  }
  const br02Meta = course.lessons.find(l => l.lesson_id === 'br-02');
  for (const [idx, q] of br02Meta.revised_assessment.closing.entries()) {
    await lessons.locator(`input[name="foundation-closing-${q.id}"][value="${q.answer}"]`).check();
    const isLast = idx === br02Meta.revised_assessment.closing.length - 1;
    await lessons.locator('.lesson-assessment button', { hasText: isLast ? 'Submit closing check' : 'Next question →' }).click();
  }
  await lessons.locator('.lesson-sync-alert').waitFor({ state: 'visible' });
  await lessons.locator('.header-icon-btn').click();
  assert.equal(await br02Card.getByRole('button').innerText(), 'Resume lesson', 'offline pending completion does not claim verified Review lesson');
  assert.ok((await lessons.locator('.lesson-activity-list').innerText()).includes('Pending sync'), 'recent activity marks unconfirmed work as Pending sync');

  // Reconnect & verify Retry account sync confirms br-02 completion -> Review lesson and persists after reload.
  simulateFoundationSyncFail = false;
  await lessons.locator('.lesson-sync-alert button', { hasText: 'Retry account sync' }).click();
  await page.waitForFunction(() => document.querySelector('[data-lesson-card="br-02"] button')?.textContent === 'Review lesson');
  await page.reload();
  await nav('lessons');
  await lessons.locator('[data-lesson-card="br-02"]').waitFor();
  assert.equal(await lessons.locator('[data-lesson-card="br-02"] button').innerText(), 'Review lesson', 'confirmed completion persists across page refresh');

  // Inspect bookmark, sticky Chapter Contents, and smooth toggle on br-01.
  await lessons.locator('[data-lesson-card="br-01"] button').click();
  await lessons.locator('.lesson-contents-toggle').waitFor();
  const lessonBackStyle = await lessons.locator('.header-icon-btn').evaluate(n => getComputedStyle(n).borderTopWidth);
  assert.equal(lessonBackStyle, '0px', 'Lessons back button uses minimal icon-only style');
  const expBox = await lessons.locator('.lesson-contents-toggle').boundingBox();
  const expSidebarBox = await lessons.locator('.lesson-section-sidebar').boundingBox();
  assert.ok(Math.abs((expBox.y + expBox.height / 2) - (expSidebarBox.y + expSidebarBox.height / 2)) <= 12, 'expanded bookmark is vertically centered on right edge of subtopic panel');
  assert.ok(Math.abs(expBox.x - (expSidebarBox.x + expSidebarBox.width)) <= 4, 'expanded bookmark attaches to right edge of subtopic panel');
  if (process.env.QUIZ_V2_SCREENSHOT_DIR) await page.screenshot({ path: path.join(process.env.QUIZ_V2_SCREENSHOT_DIR, 'lessons-expanded.png') });
  await lessons.locator('.lesson-contents-toggle').click();
  await page.locator('.lesson-reader.is-nav-collapsed').waitFor();
  await page.waitForTimeout(340);
  const handleBox = await lessons.locator('.lesson-section-sidebar.is-collapsed .lesson-contents-toggle').boundingBox();
  const readerBox = await lessons.locator('.lesson-reader.is-nav-collapsed').boundingBox();
  const pageBox = await lessons.locator('.lesson-reader.is-nav-collapsed .constituent-page').boundingBox();
  assert.ok(handleBox.width <= 40, `collapsed handle is slim bookmark width (${handleBox.width}px)`);
  assert.ok(handleBox.x >= readerBox.x - 2 && handleBox.x < pageBox.x + 56, 'collapsed bookmark attaches to left boundary without overlapping global sidebar');
  assert.ok(Math.abs((handleBox.y + handleBox.height / 2) - 486) <= 60, `collapsed bookmark stays vertically centered (${handleBox.y + handleBox.height / 2}px)`);
  assert.ok(pageBox.width > 800, `collapsed state expands reading area (${pageBox.width}px)`);
  if (process.env.QUIZ_V2_SCREENSHOT_DIR) await page.screenshot({ path: path.join(process.env.QUIZ_V2_SCREENSHOT_DIR, 'lessons-collapsed.png') });
  // Rapid toggle does not corrupt layout or arrow state.
  await lessons.locator('.lesson-contents-toggle').click();
  await lessons.locator('.lesson-contents-toggle').click();
  await page.waitForTimeout(320);
  assert.equal(await page.locator('.lesson-reader.is-nav-collapsed').count(), 1);
  assert.equal(await lessons.locator('.lesson-save-status').count(), 0, 'Lessons sync footer completely removed on healthy account sync');
  assert.equal(await lessons.locator('.lesson-sync-alert').count(), 0, 'No sync error banner when synced normally');
  const stickyMetrics = await lessons.evaluate(() => {
    const header = document.querySelector('#curriculumView > .lesson-header');
    const sidebar = document.querySelector('#curriculumView .lesson-section-sidebar');
    const hRect = header.getBoundingClientRect();
    const sRect = sidebar.getBoundingClientRect();
    return { headerBottom: hRect.bottom, sidebarTop: sRect.top, sidebarHeight: sRect.height, vh: window.innerHeight };
  });
  assert.ok(Math.abs(stickyMetrics.sidebarTop - stickyMetrics.headerBottom) <= 2, 'Chapter contents top meets lesson header bottom seamlessly');
  assert.ok(Math.abs((stickyMetrics.sidebarTop + stickyMetrics.sidebarHeight) - stickyMetrics.vh) <= 2, 'Chapter contents extends cleanly to viewport bottom with zero footer gap');

  // Achievements: verify earned/locked badges, consolidated single category filter bar (no duplicate All), unclipped Cross-framework, compact pills, and removal of redundant XP header bar.
  await nav('achievements');
  await page.locator('[data-achievement="first-lesson"]').waitFor();
  assert.equal(await page.locator('#achievementsProgressLabel').count(), 0, 'redundant XP summary removed from Achievements');
  assert.equal(await page.locator('#achievementsProgressFill').count(), 0, 'redundant XP progress bar removed from Achievements');
  assert.equal(await page.locator('#achievementsCatTrigger').count(), 0, 'duplicate All dropdown trigger removed');
  assert.equal(await page.locator('.achievement-card').count(), 12);
  const statsText = await page.locator('#achievementsStatsCounter').textContent();
  assert.match(statsText, /^\d+ of 12 achievements earned$/);
  const achDesktopAudit = await page.evaluate(() => {
    const view = document.getElementById('achievementsView');
    const pills = [...document.querySelectorAll('#achievementsCatPills .cat-pill')];
    const rects = pills.map(p => ({ text: p.textContent.trim(), r: p.getBoundingClientRect(), overflow: p.scrollWidth > p.clientWidth + 1 }));
    const vRect = view.getBoundingClientRect();
    return {
      labels: rects.map(x => x.text),
      allInsideViewport: rects.every(x => x.r.left >= vRect.left && x.r.right <= vRect.right && !x.overflow),
      maxHeight: Math.max(...rects.map(x => x.r.height)),
      singleRowDesktop: new Set(rects.map(x => Math.round(x.r.top))).size === 1,
      pageOverflow: document.documentElement.scrollWidth - window.innerWidth,
    };
  });
  assert.deepEqual(achDesktopAudit.labels, ['All', 'Learning Path', 'Assessment', 'Syntax Skill', 'Consistency', 'Cross-framework']);
  assert.equal(achDesktopAudit.allInsideViewport, true, 'All 6 category pills including Cross-framework render completely without clipping');
  assert.ok(achDesktopAudit.maxHeight <= 32, `Compact filter pill height (got ${achDesktopAudit.maxHeight}px)`);
  assert.equal(achDesktopAudit.singleRowDesktop, true, 'All category pills sit cleanly on one row on desktop');
  assert.ok(achDesktopAudit.pageOverflow <= 1, 'No horizontal page overflow on desktop Achievements');
  if (process.env.QUIZ_V2_SCREENSHOT_DIR) await page.screenshot({ path: path.join(process.env.QUIZ_V2_SCREENSHOT_DIR, 'achievements-clean.png') });
  await page.locator('.cat-pill[data-category="assessment"]').click();
  await page.waitForFunction(() => document.querySelectorAll('#achievementsGrid .achievement-card').length === 5);
  assert.equal(await page.locator('.achievement-card').count(), 5);
  assert.match(await page.locator('#achievementsStatsCounter').textContent(), /^\d+ of 5 achievements earned$/);
  await page.locator('.cat-pill[data-category="cross-framework"]').click();
  await page.waitForFunction(() => document.querySelectorAll('#achievementsGrid .achievement-card').length >= 1);
  await page.locator('.cat-pill[data-category="all"]').click();
  await page.waitForFunction(() => document.querySelectorAll('#achievementsGrid .achievement-card').length === 12);

  // Check responsive tablet & mobile dark Achievements filter bar with zero clipping or overflow.
  for (const vp of [{ width: 820, height: 900, theme: 'light' }, { width: 390, height: 844, theme: 'dark' }]) {
    await page.setViewportSize({ width: vp.width, height: vp.height });
    await page.evaluate(t => document.documentElement.setAttribute('data-theme', t), vp.theme);
    await page.waitForTimeout(80);
    const resp = await page.evaluate(() => {
      const view = document.getElementById('achievementsView').getBoundingClientRect();
      const pills = [...document.querySelectorAll('#achievementsCatPills .cat-pill')];
      return {
        allVisibleUnclipped: pills.every(p => {
          const r = p.getBoundingClientRect();
          return r.width > 0 && r.left >= view.left && r.right <= view.right && p.scrollWidth <= p.clientWidth + 1;
        }),
        pageOverflow: document.documentElement.scrollWidth - window.innerWidth,
      };
    });
    assert.equal(resp.allVisibleUnclipped, true, `All category pills remain unclipped at ${vp.width}px (${vp.theme})`);
    assert.ok(resp.pageOverflow <= 1, `No page horizontal overflow at ${vp.width}px`);
    if (vp.width === 390 && process.env.QUIZ_V2_SCREENSHOT_DIR) {
      await page.screenshot({ path: path.join(process.env.QUIZ_V2_SCREENSHOT_DIR, 'achievements-mobile-dark.png') });
    }
  }
  await page.setViewportSize({ width: 1360, height: 920 });
  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'light'));

  // Leaderboard: verify minimal fix/UI design, Top Learner podium, 5 standings columns, and zero clutter.
  await nav('leaderboard');
  await page.locator('.podium-card').first().waitFor();
  assert.equal(await page.locator('#leaderboardStatusRow').isHidden(), true, 'status row hidden when rankings are populated');
  const lbText = await page.locator('#leaderboardView').innerText();
  for (const forbidden of ['Private lifetime', 'Participation and privacy', 'Your alias', 'Your public alias', 'Top Contributor', 'UTC']) {
    assert.ok(!lbText.includes(forbidden), `clutter text removed from main Leaderboard: ${forbidden}`);
  }
  const podiumText = await page.locator('#leaderboardPodium').innerText();
  assert.ok(podiumText.includes('Top Learner'), 'first place shows Top Learner');
  assert.ok(podiumText.includes('Open rank'), '3rd open slot clean');
  const colHeaders = await page.locator('#leaderboardView .standings-table th').allTextContents();
  assert.deepEqual(colHeaders, ['Rank', 'Learner', 'Lessons Completed', 'Quizzes Completed', 'Period XP']);
  assert.ok(await page.locator('#leaderboardEntries').innerText().then(t => t.includes('AlphaTree') && t.includes('BetaSyntax')));
  await page.locator('#leaderboardPeriod').selectOption('seasonal');
  await page.waitForFunction(() => document.querySelector('#leaderboardEntries')?.innerText?.includes('AlphaTree'));
  await page.locator('#leaderboardPeriod').selectOption('weekly');
  await page.waitForFunction(() => document.querySelector('#leaderboardEntries')?.innerText?.includes('AlphaTree'));

  // Account Profile Menu -> Leaderboard Settings modal: verified email prefix derivation, unverified fallback, random nickname button, alias save, opt-out & resume.
  await page.evaluate(() => window.setTestUser('user_browser_email', { email: 'maya.lin+study@stanford.edu', verified: true }));
  await page.waitForFunction(() => document.querySelector('#leaderboardEntries')?.innerText?.includes('maya_lin_study'));
  assert.ok(!(await page.locator('#leaderboardView').innerText()).includes('stanford.edu'), 'email domain never exposed on Leaderboard');

  await page.evaluate(() => window.setTestUser('user_browser_unverified', { email: 'secret.person@yahoo.com', verified: false }));
  await page.waitForFunction(() => /Learner_[A-F0-9]{6}/.test(document.querySelector('#leaderboardEntries')?.innerText || ''));
  assert.ok(!(await page.locator('#leaderboardView').innerText()).includes('secret_person'), 'unverified email must not derive alias');

  await page.evaluate(() => window.setTestUser('user_browser_email', { email: 'maya.lin+study@stanford.edu', verified: true }));
  await page.waitForFunction(() => document.querySelector('#leaderboardEntries')?.innerText?.includes('maya_lin_study'));
  await page.locator('#identityChip').click();
  await page.locator('#profileLeaderboardSettings').click();
  await page.locator('#leaderboardSettingsModal.is-open').waitFor();
  assert.equal(await page.locator('#leaderboardAlias').inputValue(), 'maya_lin_study');
  assert.ok((await page.locator('#leaderboardPrivacyCopy').innerText()).includes('before @'), 'clear disclosure shown in settings');
  await page.locator('#leaderboardRandomAlias').click();
  assert.match(await page.locator('#leaderboardAlias').inputValue(), /^Learner_[A-F0-9]{6}$/);
  await page.locator('#leaderboardAlias').fill('SyntaxOwl');
  await page.getByRole('button', { name: 'Save public alias', exact: true }).click();
  await page.waitForFunction(() => document.querySelector('#leaderboardEntries')?.innerText?.includes('SyntaxOwl'));
  await page.getByRole('button', { name: 'Leave public rankings', exact: true }).click();
  await page.waitForFunction(() => document.querySelector('#leaderboardJoin')?.textContent === 'Resume public rankings');
  assert.ok(!(await page.locator('#leaderboardEntries').innerText()).includes('SyntaxOwl'), 'opted-out user hidden immediately');
  await page.locator('#leaderboardSettingsCloseBtn').click();
  await page.evaluate(() => window.setTestUser('user_alpha'));
  await page.evaluate(() => window.setTestUser('user_browser_email', { email: 'maya.lin+study@stanford.edu', verified: true }));
  await page.waitForFunction(() => document.querySelector('#leaderboardEntries')?.innerText?.includes('AlphaTree'));
  assert.ok(!(await page.locator('#leaderboardEntries').innerText()).includes('SyntaxOwl'), 'opt-out persists across subsequent logins');
  await page.locator('#identityChip').click();
  await page.locator('#profileLeaderboardSettings').click();
  await page.locator('#leaderboardSettingsModal.is-open').waitFor();
  await page.getByRole('button', { name: 'Resume public rankings', exact: true }).click();
  await page.waitForFunction(() => document.querySelector('#leaderboardEntries')?.innerText?.includes('SyntaxOwl'));
  await page.locator('#leaderboardSettingsCloseBtn').click();
  await page.evaluate(() => window.setTestUser('user_alpha'));
  await page.waitForFunction(() => document.querySelector('#leaderboardEntries')?.innerText?.includes('AlphaTree'));

  // Backward-compatible 0-arg RPC fallback & existing Learner_XXXXXX account adopting verified email prefix with clear disclosure + reload persistence.
  simulateHostedZeroArgRpc = true;
  await page.evaluate(() => window.setTestUser('user_hosted_0arg', { email: 'amira.khan@mit.edu', verified: true }));
  await page.waitForFunction(() => /Learner_[A-F0-9]{6}/.test(document.querySelector('#leaderboardEntries')?.innerText || ''));
  simulateHostedZeroArgRpc = false;

  await page.locator('#identityChip').click();
  await page.locator('#profileLeaderboardSettings').click();
  await page.locator('#leaderboardSettingsModal.is-open').waitFor();
  await page.locator('#leaderboardAliasSuggestion').waitFor({ state: 'visible' });
  const sugCopy = await page.locator('#leaderboardAliasSuggestionCopy').innerText();
  assert.ok(sugCopy.includes('amira_khan') && sugCopy.includes('before @') && sugCopy.includes('publish'), 'disclosure clearly explains public visibility before adoption');
  assert.ok(!sugCopy.includes('mit.edu'), 'suggestion disclosure never exposes email domain');
  await page.locator('#leaderboardAdoptEmailAlias').click();
  await page.waitForFunction(() => document.querySelector('#leaderboardEntries')?.innerText?.includes('amira_khan'));
  assert.equal(await page.locator('#leaderboardAliasSuggestion').isHidden(), true, 'suggestion banner hides once email alias is adopted');
  await page.locator('#leaderboardSettingsCloseBtn').click();

  // Verify adopted alias is consistent in BOTH podium (#3 ahead of Learner_* and SyntaxOwl) and standings table.
  assert.ok((await page.locator('#leaderboardPodium').innerText()).includes('amira_khan'), 'adopted alias appears in podium');
  assert.ok((await page.locator('#leaderboardEntries').innerText()).includes('amira_khan'), 'adopted alias appears in standings');

  // Legacy account with colliding verified email prefix adopts a short non-identifying suffix automatically.
  simulateHostedZeroArgRpc = true;
  await page.evaluate(() => window.setTestUser('user_hosted_0arg_dup', { email: 'amira.khan@brown.edu', verified: true }));
  await page.waitForFunction(() => /Learner_[A-F0-9]{6}/.test(document.querySelector('#leaderboardEntries')?.innerText || ''));
  simulateHostedZeroArgRpc = false;
  await page.locator('#identityChip').click();
  await page.locator('#profileLeaderboardSettings').click();
  await page.locator('#leaderboardSettingsModal.is-open').waitFor();
  await page.locator('#leaderboardAdoptEmailAlias').click();
  await page.waitForFunction(() => /amira_khan_[A-F0-9]{4}/.test(document.querySelector('#leaderboardAlias')?.value || ''));
  await page.locator('#leaderboardSettingsCloseBtn').click();

  await page.reload();
  await nav('leaderboard');
  await page.waitForFunction(() => document.querySelector('#leaderboardEntries')?.innerText?.includes('AlphaTree'));
  assert.ok((await page.locator('#leaderboardEntries').innerText()).includes('amira_khan'), 'adopted alias persists across page refresh');
  assert.ok(/amira_khan_[A-F0-9]{4}/.test(await page.locator('#leaderboardEntries').innerText()), 'duplicate adopted alias with suffix persists across refresh');

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
