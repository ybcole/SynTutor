import assert from 'node:assert/strict';
import fs from 'node:fs';
import { validateCourse, STAGES, emptyProgress, reduceProgress, lessonKey, lessonXp, prerequisitesMet } from '../web/js/lesson-core.js';
import { createLessonStore } from '../web/js/lesson-progress.js';
const course=validateCourse(JSON.parse(fs.readFileSync(new URL('../web/content/lessons/course.json',import.meta.url))));
assert.equal(course.lessons.length,12);
function complete(lesson) {
 let p=emptyProgress();
 for(const stage of STAGES){
  if(lesson[stage]) p=reduceProgress(lesson,p,{type:'answer',answer:stage==='predict' ? lesson[stage].options.find(o=>o.id!==lesson[stage].answer).id : lesson[stage].answer});
  p=reduceProgress(lesson,p,{type:'advance'});
 }
 return p;
}
for(const lesson of course.lessons){
 assert.throws(()=>reduceProgress(lesson,emptyProgress(),{type:'navigate',stage:5}),/earlier/);
 assert.throws(()=>reduceProgress(lesson,emptyProgress(),{type:'advance'}),/Answer/);
 const done=complete(lesson);assert.ok(done.completed_at);
 const again=reduceProgress(lesson,done,{type:'advance'});assert.equal(again.completed_at,done.completed_at);
 const partial={...done,completed_at:null,visited:STAGES.filter(s=>s!=='worked')};
 assert.throws(()=>reduceProgress(lesson,partial,{type:'advance'}),/all required/);
 assert.throws(()=>reduceProgress(lesson,{...done,completed_at:null},{type:'advance'},{prerequisites:false}),/prerequisite/);
}
for(const mutate of [c=>{c.sources[0].independent_review=false;},c=>{c.lessons[0].exit.source_ids=[];},c=>{c.lessons[1].prerequisites=[{lesson_id:'missing',content_version:'1.0.0'}];},c=>{c.lessons[0].prerequisites=[{lesson_id:'br-02',content_version:'1.0.0'}];}]){
 const bad=structuredClone(course);mutate(bad);assert.throws(()=>validateCourse(bad));
}
const memory=new Map(),storage={getItem:k=>memory.get(k),setItem:(k,v)=>memory.set(k,v)};
let guest=createLessonStore(course,{storage});
const first=course.lessons[0];
for(const key of STAGES){if(first[key])await guest.act(first,{type:'answer',answer:first[key].answer});await guest.act(first,{type:'advance'});}
assert.equal(lessonXp(guest.records),15);
await Promise.all([guest.act(first,{type:'advance'}),guest.act(first,{type:'advance'})]);
assert.equal(lessonXp(guest.records),15);
const restored=createLessonStore(course,{storage});assert.equal(restored.records[lessonKey(first)].completed_at,guest.records[lessonKey(first)].completed_at);
assert.ok(prerequisitesMet(course.lessons[1],restored.records));
const other=createLessonStore(course,{storage,userId:'user_other'});assert.equal(lessonXp(other.records),0);
const revised=structuredClone(course);revised.lessons[0].content_version='2.0.0';
const revisedStore=createLessonStore(revised,{storage});
assert.ok(revisedStore.records['br-01@1.0.0'].completed_at,'historical completion retained');
assert.equal(revisedStore.records['br-01@2.0.0'],undefined,'new version does not inherit completion');
const broken=createLessonStore(course,{storage:{getItem:()=>{throw Error('blocked');},setItem:()=>{throw Error('blocked');}}});
await broken.act(first,{type:'answer',answer:'a'});await broken.act(first,{type:'advance'});assert.equal(broken.records[lessonKey(first)].stage,1,'memory fallback survives storage failure');
let calls=[];const rpc={rpc:async(name,args)=>{calls.push({name,args});return {error:{message:'offline'}};}};
const offline=createLessonStore(course,{storage,userId:'user_offline',client:rpc});await offline.act(first,{type:'answer',answer:'a'});
assert.match(offline.status,/sync unavailable/i);assert.equal(calls.length,1);assert.equal(calls[0].name,'save_lesson_progress');
assert.deepEqual(Object.keys(calls[0].args).sort(),['p_content_version','p_lesson_id','p_state']);
console.log('PASS: all 12 lessons, stage/answer/review gates, prerequisite/version isolation, persistence, replay/concurrent idempotency and offline account sync.');
// A completion already awarded by another device must not be reported as a new server award.
const synced=createLessonStore(course,{storage,userId:'user_synced',client:{rpc:async(_name,args)=>({data:{...args.p_state,
 completed_at:args.p_state.visited.length===6 ? '2026-11-08T00:00:00Z' : null,earned:0},error:null})}});
let last;
for(const stage of STAGES){if(first[stage])await synced.act(first,{type:'answer',answer:first[stage].answer});last=await synced.act(first,{type:'advance'});}
assert.equal(last.earned,0);assert.ok(last.progress.completed_at);assert.equal(lessonXp(synced.records),15);
console.log('PASS: account server award outcomes are respected when another device completed the version.');
