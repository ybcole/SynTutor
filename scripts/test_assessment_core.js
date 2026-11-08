import assert from 'node:assert/strict';import fs from 'node:fs';
import {validateBank,makeAttempt,gradeAttempt,summaryFor,targetXp,reinforcement,quizKey} from '../web/js/quiz-core.js';
import {createQuizStore} from '../web/js/quiz-progress.js';
import {composeQuizEvidence} from '../web/js/explanation-evidence.js';
const bank=validateBank(JSON.parse(fs.readFileSync(new URL('../web/content/quizzes/bank.json',import.meta.url))));
assert.equal(bank.items.length,120);assert.equal(bank.assessments.length,16);
function answers(t,score){t.responses={};for(const [i,ref] of t.presented.entries()){const q=bank.items.find(q=>q.item_id===ref.item_id);t.responses[q.item_id]=i<score?q.answer:q.options.find(o=>o.id!==q.answer).id;}return t;}
for(const a of bank.assessments)for(let score=0;score<=5;score++){
 const t=answers(makeAttempt(bank,a,414),score);assert.equal(gradeAttempt(bank,t).correct,score);assert.equal(gradeAttempt(bank,t).target_xp,2*score);
 const repeat=makeAttempt(bank,a,414,t.attempt_id);assert.deepEqual(t.presented,repeat.presented);
 assert.equal(new Set(t.presented.map(r=>r.item_id)).size,5);
}
for(const bad of [-1,6,1.5,NaN])assert.throws(()=>targetXp(bad));
const a=bank.assessments[0],history={};
for(const [i,score] of [3,5,5,2].entries()){const t=answers(makeAttempt(bank,a,100+i),score);t.submitted_at=new Date(1000*i).toISOString();history[t.attempt_id]=t;}
const sum=summaryFor(bank,history,a);assert.equal(sum.best_score,5);assert.equal(sum.last_score,2);assert.equal(sum.xp_awarded,10);assert.equal(sum.attempt_count,4);
const practice=reinforcement(bank,history,42);assert.equal(practice.practice,true);assert.equal(gradeAttempt(bank,practice).target_xp,0);
const lastByPool=new Map();for(const t of Object.values(history))for(const ref of t.presented)lastByPool.set(bank.items.find(q=>q.item_id===ref.item_id).pool_id,ref.item_id);
for(const ref of practice.presented){const q=bank.items.find(q=>q.item_id===ref.item_id);assert.notEqual(ref.item_id,lastByPool.get(q.pool_id),'reinforcement rotates the example');}
const variants=new Set();for(let i=0;i<100;i++)variants.add(JSON.stringify(makeAttempt(bank,a,Math.imul(i+1,348739)).presented));assert.ok(variants.size>20);
for(const q of bank.items)for(const answer of [q.answer,q.options.find(o=>o.id!==q.answer).id,null])assert.equal(composeQuizEvidence(q,answer,bank).status,'EXPLAINED');
const forged=structuredClone(bank);forged.sources[0].independent_review=false;assert.throws(()=>validateBank(forged));
const q=bank.items.find(q=>q.source_ids.includes(forged.sources[0].id));assert.equal(composeQuizEvidence(q,q.answer,forged).status,'NO_BOOK_BASIS');
const memory=new Map(),storage={getItem:k=>memory.get(k),setItem:(k,v)=>memory.set(k,v)};
const store=createQuizStore(bank,{storage});
async function finish(score){const t=await store.start(a,210+score);for(const [i,ref] of t.presented.entries()){const q=bank.items.find(q=>q.item_id===ref.item_id);await store.answer(t.attempt_id,q.item_id,i<score?q.answer:q.options.find(o=>o.id!==q.answer).id);}return [t,await store.submit(t.attempt_id)];}
const [first,r1]=await finish(3);assert.equal(r1.earned,6);const [second,r2]=await finish(5);assert.equal(r2.earned,4);const [,r3]=await finish(5);assert.equal(r3.earned,0);
assert.equal((await store.submit(first.attempt_id)).earned,0);await assert.rejects(()=>store.answer(first.attempt_id,first.presented[0].item_id,'a'),/read-only/);
const restored=createQuizStore(bank,{storage});assert.equal(restored.summary(a).xp_awarded,10);
assert.equal(createQuizStore(bank,{storage,userId:'user_other'}).summary(a).xp_awarded,0);
assert.ok(![...memory.keys()].some(k=>k.includes(':lessons:')),'quiz attempts never mutate lesson progress');
const revised={...a,content_version:'2.0.0'};assert.equal(summaryFor(bank,store.attempts,revised).attempt_count,0);
const draft=await store.start(a,27);await store.answer(draft.attempt_id,draft.presented[0].item_id,'a');await store.move(draft.attempt_id,2);const reload=createQuizStore(bank,{storage});assert.equal(reload.draft(a).position,2);
let calls=0,offline=false;const client={rpc:async(_n,args)=>{calls++;return offline?{error:{message:'offline'}}:{data:{correct:null,earned:0}};},from:()=>({select:async()=>({data:[],error:null})})};
const account=createQuizStore(bank,{storage,userId:'user_account',client});const synced=await account.start(a,84);offline=true;await account.answer(synced.attempt_id,synced.presented[0].item_id,'b');assert.match(account.status,/sync unavailable/);
const accountReload=createQuizStore(bank,{storage,userId:'user_account',client});offline=false;const before=calls;await accountReload.retry();assert.ok(calls>before,'unsynced edits survive reload and retry');
const broken=createQuizStore(bank,{storage:{getItem:()=>{throw Error('blocked');},setItem:()=>{throw Error('blocked');}}});const b=await broken.start(a,42);await broken.move(b.attempt_id,1);assert.equal(broken.attempts[b.attempt_id].position,1);
let hangs=0;const hung=createQuizStore(bank,{storage,userId:'user_hung',timeoutMs:5,client:{rpc:()=>{hangs++;return new Promise(()=>{});}}});const ht=await hung.start(a,42);await hung.move(ht.attempt_id,1);assert.equal(hangs,1);assert.match(hung.status,/timed out/);
console.log('PASS: 16 blueprints/120 variants, all scores and XP deltas, deterministic randomization, review gates, immutable submissions, reinforcement rotation, independent identities/versions/drafts and bounded offline persistence.');
