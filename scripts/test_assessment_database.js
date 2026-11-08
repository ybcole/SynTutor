import {PGlite} from '@electric-sql/pglite';import fs from 'node:fs';import assert from 'node:assert/strict';
import {makeAttempt} from '../web/js/quiz-core.js';
const file=p=>fs.readFileSync(new URL('../'+p,import.meta.url),'utf8');const bank=JSON.parse(file('web/content/quizzes/bank.json'));
const db=new PGlite();
await db.exec(`create role anon;create role authenticated;create schema auth;create function auth.jwt() returns jsonb language sql stable as $$select coalesce(nullif(current_setting('request.jwt.claims',true),'')::jsonb,'{}'::jsonb)$$;grant usage on schema auth to anon,authenticated;grant execute on function auth.jwt() to anon,authenticated;`);
for(const p of ['20261013000000_player_stats.sql','20261108000000_versioned_lessons.sql','20261108000001_lesson_catalog.sql','20261108000002_independent_quizzes.sql','20261108000003_quiz_catalog.sql'])await db.exec(file('supabase/migrations/'+p));
await db.exec(file('supabase/migrations/20261108000003_quiz_catalog.sql'));
async function identity(id,role='anon'){await db.exec('reset role');await db.query("select set_config('request.jwt.claims',$1,false)",[JSON.stringify(id?{sub:id}:{})]);await db.exec(`set role ${role}`);}
function payload(a,score,seed=310){const t=makeAttempt(bank,a,seed);t.responses={};for(const [i,ref] of t.presented.entries()){const q=bank.items.find(q=>q.item_id===ref.item_id);t.responses[q.item_id]=i<score?q.answer:q.options.find(o=>o.id!==q.answer).id;}return Object.fromEntries(['attempt_id','assessment_id','content_version','seed','presented','responses','position'].map(k=>[k,t[k]]));}
async function save(t,submit=true){return (await db.query('select public.save_quiz_attempt($1::jsonb,$2) as data',[JSON.stringify(t),submit])).rows[0].data;}
const a=bank.assessments[0];await identity(null);await assert.rejects(()=>save(payload(a,5)),/Sign in/);
for(let score=0;score<=5;score++){await identity('user_score_'+score);const result=await save(payload(a,score,100+score));assert.equal(result.correct,score);assert.equal(result.earned,2*score);}
// Validate deterministic pool selection for every blueprint, including mixed topics.
for(const [i,a] of bank.assessments.entries()){await identity('user_blueprint_'+i);const r=await save(payload(a,5,1292381+i*98234));assert.equal(r.correct,5);assert.equal(r.earned,10);}
await identity('user_a');const low=payload(a,3);const draft=await save(low,false);assert.equal(draft.correct,null);assert.equal(draft.submitted_at,null);assert.equal(draft.earned,0);
const first=await save(low);assert.equal(first.earned,6);
for(const r of await Promise.all(Array.from({length:5},()=>save(low))))assert.equal(r.earned,0);
const high=payload(a,5,822);assert.equal((await save(high)).earned,4);assert.equal((await save(payload(a,5,823))).earned,0);assert.equal((await save(payload(a,1,824))).earned,0);
const best=(await db.query('select * from public.quiz_best_scores_v1')).rows[0];assert.equal(best.best_score,5);assert.equal(best.last_score,1);assert.equal(best.attempt_count,4);assert.equal(best.xp_awarded,10);
assert.equal((await db.query('select sum(xp)::int as xp from public.quiz_xp_events_v1')).rows[0].xp,10);
const edited=structuredClone(low);edited.responses[edited.presented[4].item_id]='a';if(edited.responses[edited.presented[4].item_id]===low.responses[edited.presented[4].item_id])edited.responses[edited.presented[4].item_id]='b';
await assert.rejects(()=>save(edited),/immutable/);
for(const change of [t=>{t.xp=10000;},t=>{t.user_id='user_b';},t=>{t.responses.forged='a';},t=>{t.content_version='99.0.0';},t=>{t.presented[1]=t.presented[0];},t=>{t.seed=4294967296;},t=>{t.presented[0].option_order=['a','a','a'];}]){
 const t=payload(a,5);change(t);await assert.rejects(()=>save(t));
}
await assert.rejects(()=>db.exec("update public.quiz_best_scores_v1 set xp_awarded=10"),/permission denied/);
assert.equal((await db.query('select * from public.lesson_progress')).rows.length,0,'quiz submission does not create lesson completion');
await identity('user_b','authenticated');assert.equal((await db.query('select * from public.quiz_attempts_v1')).rows.length,0);assert.equal((await db.query('select * from public.quiz_xp_events_v1')).rows.length,0);
await assert.rejects(()=>db.exec("insert into public.quiz_xp_events_v1 values ('user_b','00000000-0000-0000-0000-000000000000','x','1.0.0',10,now())"),/permission denied/);
await db.exec('reset role');await db.query("insert into public.quiz_catalog_v1 select assessment_id,'2.0.0',item_version,pool_ids,true from public.quiz_catalog_v1 where assessment_id=$1",[a.assessment_id]);
await identity('user_a');assert.equal((await save(payload({...a,content_version:'2.0.0'},5))).earned,10);
await db.exec('reset role');assert.equal((await db.query("select xp from public.player_stats where user_id='user_a'")).rows[0].xp,20);
assert.equal((await db.query('select count(*)::int as n from public.lesson_progress')).rows[0].n,0);
await db.close();console.log('PASS: real PostgreSQL seed manifests, every score/blueprint, draft/submission immutability, best-score deltas, replay/version caps, RLS and quiz/lesson separation.');
