import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadActiveCourse,quizCurriculum} from '../web/js/lesson-curriculum.js';
import {makeLessonPractice,validateLessonPractice} from '../web/js/quiz-lesson-practice.js';
import {eligibleQuestions,makeV2Attempt,questionMetadata,publishedBlueprint,topicPerformance,selectQuestions} from '../web/js/quiz-v2.js';
import {validateBank,gradeAttempt,validateAttempt,makeAttempt,itemsFor} from '../web/js/quiz-core.js';
import {createQuizStore} from '../web/js/quiz-progress.js';
const json=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const course=await loadActiveCourse(async p=>({ok:true,json:async()=>json('web'+p)})),curriculum=quizCurriculum(course);
const bank=validateBank(json('web/content/quizzes/bank.json'));
const syntax=json('web/content/quizzes/syntax-practice-source.json');
assert.equal(syntax.sections.length,51);
bank.practice_items=validateLessonPractice(makeLessonPractice(curriculum,syntax),curriculum);
assert.ok(bank.practice_items.length>2500);
assert.deepEqual(bank.practice_items,makeLessonPractice(curriculum,syntax),'stable source-derived IDs, keys, explanations and choices');
const stale=structuredClone(syntax);
for(const section of stale.sections.filter(s=>s.lesson_id==='br-03'))section.article_digest='stale';
assert.equal(makeLessonPractice(curriculum,stale).filter(q=>q.chapter_id==='br-03').length,0,'stale Syntax capture is unavailable, never silently used');
assert.equal(bank.items.length,120,'published content is never replaced or mixed with practice');
assert.throws(()=>validateBank({...bank,items:[...bank.items,bank.practice_items[0]]}),/Unreviewed/);
assert.throws(()=>validateLessonPractice([{...bank.practice_items[0],independent_review:true}],curriculum),/Invalid lesson practice/);
assert.equal(eligibleQuestions(bank,curriculum,'syntax').length,110);
assert.equal(eligibleQuestions(bank,curriculum,'cambridge').length,10);
for(const q of bank.practice_items){
  assert.equal(q.review_status,'UNREVIEWED');assert.equal(q.independent_review,false);
  assert.equal(q.publication_status,'practice');assert.ok(questionMetadata(q,curriculum));
  assert.ok(q.rationale.length>15);assert.ok(q.options.every(o=>o.rationale));
}
let topics=0,generals=0;
for(const track of curriculum){
  for(const chapter of track.chapters){
    for(const topic of chapter.topics){
      const spec={track:track.id,chapter:chapter.id,topic:topic.id,mode:'topic',content_tier:'lesson-practice'};
      const t=makeV2Attempt(bank,curriculum,spec,{},515);
      assert.equal(t.presented.length,5);assert.equal(new Set(t.presented.map(r=>r.item_id)).size,5);
      assert.equal(publishedBlueprint(bank,curriculum,spec),null);
      assert.ok(itemsFor(bank,t).every(q=>questionMetadata(q,curriculum).subtopic_id===topic.id));
      for(const q of itemsFor(bank,t))t.responses[q.item_id]=q.answer;
      assert.equal(gradeAttempt(bank,t).correct,5);assert.equal(gradeAttempt(bank,t).target_xp,0);
      assert.deepEqual(t.presented,makeV2Attempt(bank,curriculum,spec,{},515,t.attempt_id).presented);
      const notOptedIn={...t,spec:{...spec,content_tier:undefined}};
      if(t.presented.some(r=>r.item_id.startsWith('lesson-practice:')))assert.throws(()=>validateAttempt(bank,notOptedIn),/unavailable/);
      topics++;
    }
    const general=makeV2Attempt(bank,curriculum,{track:track.id,chapter:chapter.id,mode:'general',content_tier:'lesson-practice'},{},17);
    assert.equal(general.presented.length,Math.max(5,chapter.topics.length));
    const covered=new Set(itemsFor(bank,general).map(q=>q.subtopic_id||questionMetadata(q,curriculum).subtopic_id));
    assert.equal(covered.size,chapter.topics.length);assert.equal(gradeAttempt(bank,general).target_xp,0);generals++;
  }
  const master=makeV2Attempt(bank,curriculum,{track:track.id,mode:'master',count:track.chapters.length+7,content_tier:'lesson-practice'},{},52);
  const counts=track.chapters.map(c=>itemsFor(bank,master).filter(q=>q.lesson_id===c.id).length);
  assert.ok(counts.every(Boolean));assert.ok(Math.max(...counts)-Math.min(...counts)<=1);
}
assert.equal(topics,329);assert.equal(generals,31);
// Missing content is never padded with duplicate or synthetic approval records.
const none={...bank,items:[],practice_items:[]};
assert.throws(()=>selectQuestions(none,curriculum,{track:'syntax',chapter:'br-03',topic:'concepts',mode:'topic',content_tier:'lesson-practice'},{},1),/0\/5/);
const prior=makeV2Attempt(bank,curriculum,{track:'syntax',chapter:'br-03',topic:'concepts',mode:'topic',content_tier:'lesson-practice'},{},21);
prior.submitted_at=new Date().toISOString();
const performance=topicPerformance(bank,curriculum,{prior},'syntax');
assert.equal(performance.missed.size,5);
const personalized=makeV2Attempt(bank,curriculum,{track:'syntax',mode:'personalized',content_tier:'lesson-practice'},{prior},32);
assert.ok(itemsFor(bank,personalized).every(q=>!performance.missed.has(q.item_id)&&!performance.missedFamilies.has(q.practice_family)));
assert.ok(itemsFor(bank,personalized).every(q=>!(q.practice_example_ids||[]).some(id=>performance.missedExamples.has(id))),'do not recycle a missed example through a differently worded question');
assert.ok(itemsFor(bank,personalized).every(q=>questionMetadata(q,curriculum).track_id==='syntax'));
assert.equal(topicPerformance(bank,curriculum,{prior},'cambridge').missed.size,0);
// Practice cannot enter a published five-question contract, even with a valid ID/seed.
const forged=makeAttempt(bank,bank.assessments[0],21);
forged.presented=prior.presented;assert.throws(()=>validateAttempt(bank,forged));
let xpCalls=0;
const memory=new Map(),storage={getItem:k=>memory.get(k),setItem:(k,v)=>memory.set(k,v)};
const client={from:()=>({upsert:async()=>({error:null}),select:async()=>({data:[]})}),rpc:async()=>{xpCalls++;throw Error('No XP path permitted');}};
const store=createQuizStore(bank,{storage,userId:'practice-user',client});
const started=await store.startV2(curriculum,{track:'cambridge',mode:'topic',chapter:'cgel-ch07',topic:'preposition-style',content_tier:'lesson-practice'},76);
await store.answer(started.attempt_id,started.presented[0].item_id,started.presented[0].option_order[0]);
const reloaded=createQuizStore(bank,{storage,userId:'practice-user',client});
assert.deepEqual(reloaded.draft(started).presented,started.presented);
assert.equal((await reloaded.submit(started.attempt_id)).earned,0);
assert.equal((await reloaded.submit(started.attempt_id)).earned,0);assert.equal(xpCalls,0);
assert.ok(Number.isInteger(reloaded.attempts[started.attempt_id].correct),'practice score survives a later content archive');
assert.equal(Object.keys(createQuizStore(bank,{storage,userId:'other-user'}).attempts).length,0);
console.log(`PASS lesson practice: ${bank.practice_items.length} explicitly unreviewed source-grounded questions, all ${topics} topics/31 General quizzes/both Masters, deterministic reload, track-specific personalized exclusions, review opt-in, zero XP and identity isolation.`);
