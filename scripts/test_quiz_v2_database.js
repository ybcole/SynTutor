import {PGlite} from '@electric-sql/pglite';
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {makeV2Attempt} from '../web/js/quiz-v2.js';
import {loadActiveCourse,quizCurriculum} from '../web/js/lesson-curriculum.js';
import {makeLessonPractice,validateLessonPractice} from '../web/js/quiz-lesson-practice.js';
import {makeAssessmentItems} from '../web/js/quiz-assessment-items.js';
const file=p=>fs.readFileSync(new URL('../'+p,import.meta.url),'utf8');
const bank=JSON.parse(file('web/content/quizzes/bank.json'));
const curriculum=quizCurriculum(await loadActiveCourse(async p=>({ok:true,json:async()=>JSON.parse(file('web'+p))})));
bank.practice_items=validateLessonPractice(makeLessonPractice(curriculum,JSON.parse(file('web/content/quizzes/syntax-practice-source.json'))),curriculum);
bank.assessment_items=makeAssessmentItems(bank.practice_items,curriculum);
const db=new PGlite();
await db.exec(`create role anon;create role authenticated;create schema auth;
create function auth.jwt() returns jsonb language sql stable as $$select coalesce(nullif(current_setting('request.jwt.claims',true),'')::jsonb,'{}'::jsonb)$$;
grant usage on schema auth to anon,authenticated;grant execute on function auth.jwt() to anon,authenticated;`);
for (const name of fs.readdirSync(new URL('../supabase/migrations/', import.meta.url)).filter(name=>name.endsWith('.sql')).sort()) {
  await db.exec(file('supabase/migrations/'+name));
}
async function identity(id,role='authenticated'){
  await db.exec('reset role');await db.query("select set_config('request.jwt.claims',$1,false)",[JSON.stringify(id?{sub:id}:{})]);await db.exec(`set role ${role}`);
}
const t=makeV2Attempt(bank,curriculum,{track:'syntax',mode:'master',count:15,content_tier:'lesson-practice'},{},42);
const insert=(user,payload=t)=>db.query('insert into public.quiz_practice_v2(user_id,attempt_id,payload) values($1,$2,$3::jsonb)',[user,payload.attempt_id,JSON.stringify(payload)]);
const update=payload=>db.query('update public.quiz_practice_v2 set payload=$1::jsonb where attempt_id=$2',[JSON.stringify(payload),t.attempt_id]);
await identity(null,'anon');await assert.rejects(()=>insert('user_clerk_a'),/row-level security/);
await identity('user_clerk_a');await assert.rejects(()=>insert('user_clerk_b'),/row-level security/);
await insert('user_clerk_a');
assert.equal((await db.query('select payload from public.quiz_practice_v2')).rows.length,1);
await identity('user_clerk_b');assert.equal((await db.query('select * from public.quiz_practice_v2')).rows.length,0);
await assert.rejects(()=>insert('user_clerk_a'),/row-level security/);
await identity('user_clerk_a');
await assert.rejects(()=>update({...t,presented:[...t.presented].reverse()}),/immutable/);
const submitted={...t,submitted_at:new Date().toISOString()};
await update(submitted);
await assert.rejects(()=>update({...submitted,responses:{forged:'a'}}),/immutable/);
const invalid=makeV2Attempt(bank,curriculum,{track:'syntax',mode:'master',count:15,content_tier:'lesson-practice'},{},43);
delete invalid.practice;await assert.rejects(()=>insert('user_clerk_a',invalid),/check constraint/);
// A forged client score can never enter a verified assessment or ledger.
const forged={...makeV2Attempt(bank,curriculum,{track:'syntax',mode:'master',count:15,content_tier:'lesson-practice'},{},44),practice:true,correct:15,xp:999999};
await insert('user_clerk_a',forged);
await assert.rejects(()=>db.query('select public.save_quiz_attempt($1::jsonb,true)',[JSON.stringify(forged)]),/Invalid assessment payload/);
const lessonPractice=makeV2Attempt(bank,curriculum,{track:'cambridge',mode:'topic',chapter:'cgel-ch07',topic:'preposition-style',content_tier:'lesson-practice'},{},46);
await insert('user_clerk_a',lessonPractice);
// Try to disguise practice item IDs as an otherwise valid published contract.
const disguised=Object.fromEntries(['attempt_id','assessment_id','content_version','seed','presented','responses','position'].map(k=>[k,lessonPractice[k]]));
disguised.assessment_id=bank.assessments[0].assessment_id;disguised.content_version=bank.assessments[0].content_version;
await assert.rejects(()=>db.query('select public.save_quiz_attempt($1::jsonb,true)',[JSON.stringify(disguised)]));
const v2Keys=['attempt_id','assessment_id','content_version','spec','title','diagnostic','seed','presented','responses','position'];
function v2Payload(spec,score,seed=49){
  const t=makeV2Attempt(bank,curriculum,spec,{},seed);
  t.responses={};
  for(const [i,ref] of t.presented.entries()){
    const q=bank.assessment_items.find(x=>x.item_id===ref.item_id)||bank.items.find(x=>x.item_id===ref.item_id);
    t.responses[q.item_id]=i<score?q.answer:q.options.find(o=>o.id!==q.answer).id;
  }
  return Object.fromEntries(v2Keys.map(k=>[k,t[k]??null]));
}
async function saveV2(t,submit=true){return (await db.query('select public.save_quiz_v2_attempt($1::jsonb,$2) as data',[JSON.stringify(t),submit])).rows[0].data;}

const formal=v2Payload({track:'cambridge',mode:'topic',chapter:'cgel-ch04',topic:'clause-patterns'},3,49);
await identity(null);
await assert.rejects(()=>saveV2(formal),/Sign in/);

await identity('user_clerk_v2');
await db.query("select public.ensure_leaderboard_participation('RankedLearner')");
const draftV2=await saveV2(formal,false);
assert.equal(draftV2.correct,null);assert.equal(draftV2.submitted_at,null);assert.equal(draftV2.earned,0);
const sub3=await saveV2(formal,true);
assert.equal(sub3.correct,3);assert.equal(sub3.earned,6);
assert.equal((await saveV2(formal,true)).earned,0);

const editedV2=structuredClone(formal);
editedV2.responses[editedV2.presented[4].item_id]=editedV2.presented[4].option_order.find(id=>id!==editedV2.responses[editedV2.presented[4].item_id]);
await assert.rejects(()=>saveV2(editedV2,true),/immutable/);

const sub5=await saveV2(v2Payload({track:'cambridge',mode:'topic',chapter:'cgel-ch04',topic:'clause-patterns'},5,50),true);
assert.equal(sub5.correct,5);assert.equal(sub5.earned,4);
const sub2=await saveV2(v2Payload({track:'cambridge',mode:'topic',chapter:'cgel-ch04',topic:'clause-patterns'},2,51),true);
assert.equal(sub2.correct,2);assert.equal(sub2.earned,0);

const generalSpec={track:'syntax',mode:'general',chapter:'br-02'};
const generalAttempt=v2Payload(generalSpec,5,52);
assert.equal(generalAttempt.presented.length,5);
const generalV2=await saveV2(generalAttempt,true);
assert.equal(generalV2.correct,5);assert.equal(generalV2.earned,10);

const masterV2=await saveV2(v2Payload({track:'syntax',mode:'master',count:15},15,54),true);
assert.equal(masterV2.correct,15);assert.equal(masterV2.earned,30);

const prog=(await db.query('select public.get_my_progression() as data')).rows[0].data;
assert.equal(prog.quiz_xp,50);assert.equal(prog.xp,50);
const board=(await db.query("select public.get_leaderboard('weekly') as data")).rows[0].data;
assert.deepEqual(board.entries.find(row=>row.alias==='RankedLearner'), {
  alias:'RankedLearner',rank:1,xp:50,lessons_completed:0,quizzes_completed:3,
});

for(const bad of [
  t=>{t.xp=999999;},
  t=>{t.correct=5;},
  t=>{t.spec.content_tier='lesson-practice';},
  t=>{t.presented[0].item_id='practice-nonexistent-item';},
  t=>{t.presented[1]=t.presented[0];},
]){
  const badP=v2Payload({track:'cambridge',mode:'topic',chapter:'cgel-ch04',topic:'clause-patterns'},5,53);
  bad(badP);
  await assert.rejects(()=>saveV2(badP,true));
}

await assert.rejects(()=>db.exec("insert into public.quiz_xp_events_v2 values ('user_clerk_v2','00000000-0000-0000-0000-000000000002','x','2.0.0',99,now())"),/permission denied/);
await assert.rejects(()=>db.exec("update public.quiz_best_scores_v2 set xp_awarded=999"),/permission denied/);
await identity('user_clerk_b','authenticated');
assert.equal((await db.query('select count(*)::int as n from public.quiz_attempts_v2')).rows[0].n,0);
assert.equal((await db.query('select count(*)::int as n from public.quiz_xp_events_v1')).rows[0].n,0);
await assert.rejects(()=>db.exec("insert into public.quiz_xp_events_v1 values ('user_clerk_a','00000000-0000-0000-0000-000000000001','x','1.0.0',10,now())"),/permission denied/);
await identity('user_clerk_legacy','anon');const legacyRole=makeV2Attempt(bank,curriculum,{track:'syntax',mode:'master',count:15,content_tier:'lesson-practice'},{},45);await insert('user_clerk_legacy',legacyRole);
assert.equal((await db.query('select count(*)::int as n from public.quiz_practice_v2')).rows[0].n,1);
await db.close();
console.log('PASS Quiz V2 PostgreSQL: Clerk text identities, guest denial, owner RLS, private manifest sync, immutable manifests/submissions, required unscored policy, forged variable-length XP rejection and ledger isolation.');
