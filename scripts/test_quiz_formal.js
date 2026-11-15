import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadActiveCourse,quizCurriculum} from '../web/js/lesson-curriculum.js';
import {makeLessonPractice} from '../web/js/quiz-lesson-practice.js';
import {makeAssessmentItems,validateAssessmentItems} from '../web/js/quiz-assessment-items.js';
import {makeV2Attempt,eligibleQuestions,questionMetadata,topicPerformance} from '../web/js/quiz-v2.js';
import {validateBank,itemsFor,questionForLearner,reviewForLearner,gradeAttempt,validateAttempt} from '../web/js/quiz-core.js';
import {createQuizStore} from '../web/js/quiz-progress.js';
import {applyQuizScope,isRelevantAssessmentQuestion} from '../web/js/quiz-scope.js';
const json=p=>JSON.parse(fs.readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const course=await loadActiveCourse(async p=>({ok:true,json:async()=>json('web'+p)}));
const curriculum=quizCurriculum(course),bank=validateBank(json('web/content/quizzes/bank.json'));
bank.practice_items=makeLessonPractice(curriculum,json('web/content/quizzes/syntax-practice-source.json'));
bank.assessment_items=validateAssessmentItems(makeAssessmentItems(bank.practice_items),curriculum);
// Taught content is not automatically assessable: keep Lessons unchanged.
const prelim=course.lessons.find(l=>l.lesson_id==='cgel-ch01');
assert.equal(prelim.title,'Preliminaries');
assert.ok(prelim.revised_assessment.opening.length&&prelim.revised_assessment.closing.length);
assert.equal(curriculum[1].chapters.some(c=>c.id==='cgel-ch01'),false);
assert.deepEqual(curriculum.map(t=>t.chapters.length),[11,19]);
assert.equal(curriculum[0].chapters.find(c=>c.id==='br-11').topics.some(t=>t.id==='concepts'),false);
assert.equal(bank.practice_items.some(q=>q.lesson_id==='cgel-ch01'),false);
assert.equal(bank.assessment_items.some(q=>q.lesson_id==='cgel-ch01'),false);
assert.ok(bank.items.every(isRelevantAssessmentQuestion),'screen the immutable published bank as well as generated questions');
assert.ok(bank.assessment_items.every(isRelevantAssessmentQuestion));
assert.equal(isRelevantAssessmentQuestion({kind:'mcq',prompt:'Which page introduces the passive?'}),false);
assert.equal(isRelevantAssessmentQuestion({kind:'concept_completion',prompt:'The book treats the second type as ____'}),false);
assert.equal(isRelevantAssessmentQuestion({kind:'analysis',prompt:'Choose the Chapter 3 B-R diagram for quite gentle.'}),true);
for(const track of curriculum)assert.deepEqual(track.chapters.map(c=>[c.id,c.title]),course.lessons.filter(l=>l.track===track.lessonTrack&&l.lesson_id!=='cgel-ch01').map(l=>[l.lesson_id,l.title]));
const stale=structuredClone(curriculum);
stale[1].chapters.unshift({id:'cgel-ch01',title:'Preliminaries',topics:[{id:'overview',title:'Course overview'}]});
assert.equal(applyQuizScope(stale)[1].chapters.some(c=>c.id==='cgel-ch01'),false,'scope also filters old offline catalogs');
assert.ok(course.lessons.some(l=>l.lesson_id==='cgel-ch01'),'the course was not mutated');
// Book-only / planned / unimplemented additions cannot create a quiz.
const phantom={...prelim,lesson_id:'cgel-book-only',title:'Unsupported preliminary chapter'};
const extra=quizCurriculum({...course,lessons:[...course.lessons,phantom],planned_modules:[...course.planned_modules,phantom]});
assert.equal(extra[1].chapters.some(c=>c.id===phantom.lesson_id),false);
const removed=quizCurriculum({...course,lessons:course.lessons.filter(l=>l.lesson_id!=='cgel-ch01')});
assert.equal(removed[1].chapters.some(c=>c.id==='cgel-ch01'),false);
assert.equal(makeAssessmentItems(makeLessonPractice(removed,json('web/content/quizzes/syntax-practice-source.json'))).some(q=>q.chapter_id==='cgel-ch01'),false);
assert.equal(eligibleQuestions(bank,curriculum,'cambridge').length,10,'review/XP gates are not relaxed');
assert.ok(bank.assessment_items.length>2500);
assert.ok(bank.assessment_items.every(q=>!['lesson_match','lesson_recall'].includes(q.kind)));
let topics=0;
for(const track of curriculum){
  for(const chapter of track.chapters){
    for(const topic of chapter.topics){
      const spec={track:track.id,chapter:chapter.id,topic:topic.id,mode:'topic',content_tier:'lesson-assessment',format:'formal'};
      const t=makeV2Attempt(bank,curriculum,spec,{},782);
      assert.equal(t.assessment_contract,'quiz-v2-formal-1');assert.equal(t.presented.length,5);
      assert.throws(()=>reviewForLearner(bank,t),/Submit the quiz/);
      assert.ok(itemsFor(bank,t).every(q=>questionMetadata(q,curriculum).subtopic_id===topic.id));
      for(const [index,q] of itemsFor(bank,t).entries()){
        const presented=questionForLearner(bank,t,index);
        assert.equal(presented.answer,undefined);assert.equal(presented.rationale,undefined);
        assert.equal(presented.answer_tree,undefined);assert.equal(presented.source_metadata,undefined);
        assert.ok(presented.options.every(o=>!Object.hasOwn(o,'rationale')&&!Object.hasOwn(o,'correct')));
        t.responses[q.item_id]=q.answer;
      }
      t.submitted_at=new Date().toISOString();
      assert.equal(reviewForLearner(bank,t).correct,5);assert.equal(gradeAttempt(bank,t).target_xp,0);
      assert.deepEqual(t.presented,makeV2Attempt(bank,curriculum,spec,{},782,t.attempt_id).presented);
      topics++;
    }
    const general=makeV2Attempt(bank,curriculum,{track:track.id,chapter:chapter.id,mode:'general',content_tier:'lesson-assessment',format:'formal'},{},61);
    assert.equal(general.presented.length,Math.max(5,chapter.topics.length));
    assert.equal(new Set(itemsFor(bank,general).map(q=>questionMetadata(q,curriculum).subtopic_id)).size,chapter.topics.length);
  }
  const master=makeV2Attempt(bank,curriculum,{track:track.id,mode:'master',count:track.chapters.length+4,content_tier:'lesson-assessment',format:'formal'},{},17);
  assert.equal(new Set(itemsFor(bank,master).map(q=>q.lesson_id)).size,track.chapters.length);
}
assert.equal(topics,317);
const missedLegacy=makeV2Attempt(bank,curriculum,{track:'syntax',chapter:'br-03',topic:'concepts',mode:'topic',content_tier:'lesson-practice'},{},21);
missedLegacy.submitted_at=new Date().toISOString();
const performance=topicPerformance(bank,curriculum,{missedLegacy},'syntax');
const personalized=makeV2Attempt(bank,curriculum,{track:'syntax',mode:'personalized',content_tier:'lesson-assessment',format:'formal'},{missedLegacy},81);
assert.ok(itemsFor(bank,personalized).every(q=>!performance.missed.has(q.item_id)
  &&!performance.missedFamilies.has(q.practice_family)
  &&!(q.practice_example_ids||[]).some(id=>performance.missedExamples.has(id))));
assert.ok(itemsFor(bank,personalized).every(q=>questionMetadata(q,curriculum).track_id==='syntax'));
const spec={track:'cambridge',chapter:'cgel-ch06',topic:'modifier-style',mode:'topic',content_tier:'lesson-assessment',format:'formal'};
const attempt=makeV2Attempt(bank,curriculum,spec,{},19);
assert.throws(()=>validateAttempt(bank,{...attempt,practice:false}),/unscored/);
assert.throws(()=>validateAttempt(bank,{...attempt,assessment_contract:undefined}),/unavailable/);
const memory=new Map(),storage={getItem:k=>memory.get(k),setItem:(k,v)=>memory.set(k,v)};
const store=createQuizStore(bank,{storage});
const saved=await store.startV2(curriculum,spec,19);
const first=itemsFor(bank,saved)[0];
await store.answer(saved.attempt_id,first.item_id,first.answer);
assert.throws(()=>reviewForLearner(bank,store.attempts[saved.attempt_id]),/Submit/);
const reload=createQuizStore(bank,{storage});
assert.deepEqual(reload.draft(saved).presented,saved.presented);
const result=await reload.submit(saved.attempt_id);
assert.equal(result.grade.correct,1);assert.equal(result.grade.incorrect,4);assert.equal(result.earned,0);
assert.equal(reviewForLearner(bank,reload.attempts[saved.attempt_id]).correct,1);
assert.equal((await reload.submit(saved.attempt_id)).earned,0);
console.log(`PASS formal quizzes: ${topics} assessable lesson-aligned topics, 30 chapter quizzes/both Masters, Preliminaries excluded without changing Lessons, published/generated relevance gates, stale-cache filtering, question-only projection, submission-gated results, scoring/reload and unchanged XP gates.`);
