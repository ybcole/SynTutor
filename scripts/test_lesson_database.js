// Executes the actual PostgreSQL migrations/RLS/RPC in an isolated WASM Postgres.
// This does not connect to or alter the user's Supabase deployment.
import { PGlite } from '@electric-sql/pglite';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const db=new PGlite();
const root=new URL('../',import.meta.url);
const file=path=>fs.readFileSync(new URL(path,root),'utf8');
const course=JSON.parse(file('web/content/lessons/course.json'));
await db.exec(`create role anon; create role authenticated; create schema auth;
 create function auth.jwt() returns jsonb language sql stable as $$select coalesce(nullif(current_setting('request.jwt.claims',true),'')::jsonb,'{}'::jsonb)$$;
 grant usage on schema auth to anon, authenticated; grant execute on function auth.jwt() to anon, authenticated;`);
await db.exec(file('supabase/migrations/20261013000000_player_stats.sql'));
await db.exec(file('supabase/migrations/20261108000000_versioned_lessons.sql'));
await db.exec(file('supabase/migrations/20261108000001_lesson_catalog.sql'));
await db.exec(file('supabase/migrations/20261108000001_lesson_catalog.sql'));
const identity=async(id,role='anon')=>{await db.exec('reset role');await db.query("select set_config('request.jwt.claims',$1,false)",[JSON.stringify(id ? {sub:id} : {})]);await db.exec(`set role ${role}`);};
function state(lesson) {return {responses:Object.fromEntries(['predict','guided','transfer','exit'].map(k=>[k,lesson[k].answer])),visited:['predict','understand','worked','guided','transfer','exit'],stage:5};}
async function save(l,s=state(l)) {const r=await db.query('select public.save_lesson_progress($1,$2,$3::jsonb) as data',[l.lesson_id,l.content_version,JSON.stringify(s)]);return r.rows[0].data;}
const first=course.lessons[0],second=course.lessons[1];
await identity(null);await assert.rejects(()=>save(first),/Sign in/);
await identity('user_a');
await assert.rejects(()=>db.exec("insert into public.lesson_progress (user_id,lesson_id,content_version) values ('user_a','br-01','1.0.0')"),/permission denied/);
await assert.rejects(()=>save(first,{...state(first),xp:10000}),/Invalid lesson progress/);
await assert.rejects(()=>save({...first,content_version:'99.0.0'}),/Unknown or unpublished/);
const beforePrereq=await save(second);assert.equal(beforePrereq.completed_at,null);assert.equal(beforePrereq.earned,0);
const wrong=state(first);wrong.responses.exit=first.exit.options.find(o=>o.id!==first.exit.answer).id;
assert.equal((await save(first,wrong)).earned,0);
const partial=state(first);partial.visited=['predict'];
// A different user has no prior stages to merge.
await identity('user_partial');assert.equal((await save(first,partial)).completed_at,null);
await identity('user_a');
const result=await save(first);assert.equal(result.earned,15);assert.ok(result.completed_at);
const back=await save(first,{...state(first),stage:0});assert.equal(back.stage,0,'account navigation can go backwards');assert.equal(back.earned,0);
for(const replay of await Promise.all(Array.from({length:8},()=>save(first))))assert.equal(replay.earned,0);
assert.equal((await save(first,wrong)).completed_at,result.completed_at,'stale/wrong replay cannot undo completion');
assert.equal((await save(second)).earned,15);
let total=await db.query('select count(*)::int as n,sum(xp)::int as xp from public.lesson_xp_events');assert.equal(total.rows[0].n,2);assert.equal(total.rows[0].xp,30);
await identity('user_b','authenticated');assert.equal((await db.query('select * from public.lesson_progress')).rows.length,0,'other account cannot read progress');
assert.equal((await db.query('select * from public.lesson_xp_events')).rows.length,0,'other account cannot read awards');
await assert.rejects(()=>db.exec('update public.lesson_progress set completed_at=now()'),/permission denied/);
await assert.rejects(()=>db.exec("insert into public.lesson_xp_events values ('user_b','forged',15,now())"),/permission denied/);
assert.equal((await save(first)).earned,15,'accounts earn independently');
await db.exec('reset role');
const score=await db.query("select xp from public.player_stats where user_id='user_a'");assert.equal(score.rows[0].xp,30);
// New content versions are distinct, while old version data remains intact.
await db.query("insert into public.lesson_catalog select lesson_id,'2.0.0',prerequisites,answer_key,true from public.lesson_catalog where lesson_id='br-01'");
await identity('user_a');assert.equal((await save({...first,content_version:'2.0.0'})).earned,15);
assert.equal((await db.query("select count(*)::int as n from public.lesson_progress where lesson_id='br-01' and completed_at is not null")).rows[0].n,2);
await db.exec('reset role');
assert.equal((await db.query("select public.lesson_level_for_xp(50) as l")).rows[0].l,1);
await db.close();
console.log('PASS: actual PostgreSQL migrations/seed, no-sub/direct-write/forged-XP denial, prerequisites, wrong/missing work, repeated submissions, RLS account isolation and versioned one-time awards.');
