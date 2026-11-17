import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadActiveCourse,quizCurriculum} from '../web/js/lesson-curriculum.js';
import {chapterDescriptions,topicDescription} from '../web/js/quiz-catalog-copy.js';
import {cambridgeMixedItems} from '../web/js/quiz-mixed-cambridge.js';
import {revisedMixedIds} from '../web/js/quiz-content-revisions.js';
import {gradeQuestion} from '../web/js/quiz-mixed-eval.js';
import {makeV2Attempt} from '../web/js/quiz-v2.js';
import {itemsFor} from '../web/js/quiz-core.js';
import {makeLessonPractice} from '../web/js/quiz-lesson-practice.js';
import {makeAssessmentItems} from '../web/js/quiz-assessment-items.js';
import {levelFromXp,xpToReach} from '../web/js/level.js';
const read=p=>JSON.parse(fs.readFileSync(new URL('../web'+p,import.meta.url)));
const curriculum=quizCurriculum(await loadActiveCourse(async p=>({ok:true,json:()=>read(p)})));
const descriptions=[];
for(const track of curriculum)for(const chapter of track.chapters){
 assert.ok(chapterDescriptions[chapter.id]?.length>30);
 for(const topic of chapter.topics){const text=topicDescription(chapter,topic);assert.ok(text.length>20&&text.length<130);descriptions.push(text);}
}
assert.equal(descriptions.length,327);
assert.equal(new Set(Object.values(chapterDescriptions)).size,31);
const bank={...read('/content/quizzes/bank.json'),mixed_items:cambridgeMixedItems};
bank.assessment_items=makeAssessmentItems(makeLessonPractice(curriculum,read('/content/quizzes/syntax-practice-source.json')),curriculum);
for(const id of revisedMixedIds){
 const old=cambridgeMixedItems.find(q=>q.item_id===id),replacement=cambridgeMixedItems.find(q=>q.replaces_item_id===id);
 assert.ok(old.retired_from_selection);assert.ok(replacement&&!replacement.retired_from_selection);
 assert.equal(old.content_version,'2.0.0');assert.equal(replacement.content_version,'2.0.1');
 const historical={quiz_v2:true,practice:true,xp_policy:'unscored-v2',spec:{content_tier:'lesson-practice'},presented:[{item_id:id,content_version:'2.0.0'}]};
 assert.equal(itemsFor(bank,historical)[0],old,'historical manifest still resolves original content');
 if(old.kind!=='sentence_reconstruction')assert.equal(gradeQuestion(old,old.accepted_answers[0]).correct,true);
 for(let seed=0;seed<60;seed++){
  const attempt=makeV2Attempt(bank,curriculum,{track:'cambridge',mode:'topic',chapter:old.chapter_id,topic:old.subtopic_id,content_tier:'lesson-practice',format:'mixed'},{},seed);
  assert.ok(!attempt.presented.some(ref=>ref.item_id===id),'new attempts exclude retired content');
 }
 if(replacement.kind==='sentence_reconstruction'){
  const order=[];const available=replacement.tokens.map((t,i)=>({t,i}));
  let rest=replacement.accepted_answers[0];
  while(rest){const found=available.find(x=>rest===x.t||rest.startsWith(x.t+' '));assert.ok(found);order.push(found.i);rest=rest.slice(found.t.length).trim();available.splice(available.indexOf(found),1);}
  assert.equal(gradeQuestion(replacement,order).correct,true);
 }else assert.equal(gradeQuestion(replacement,replacement.accepted_answers[0]).correct,true);
}
const aspect=cambridgeMixedItems.find(q=>q.item_id==='mixed:cgel-ch03:situations-aspect:fill_blank:11:revision-2');
assert.equal(gradeQuestion(aspect,'perfective').correct,false);
assert.equal(gradeQuestion(aspect,'telic').correct,true);
// Preserve the established cumulative curve and reset bar progress at boundaries.
for(let level=0;level<30;level++)for(const xp of [xpToReach(level),xpToReach(level+1)-1]){
 const state=levelFromXp(xp);assert.equal(state.level,level);assert.equal(state.next-state.floor,state.span);
 assert.equal(state.xp,state.floor+state.into);assert.ok(state.into>=0&&state.into<state.span);
}
assert.deepEqual(levelFromXp(250),{xp:250,level:2,into:30,span:140,floor:220,next:360});
console.log('PASS refinements: 31 chapter/327 topic descriptions, versioned content corrections, old manifest/key compatibility, retired-item selection exclusion, reconstruction answers, XP boundaries.');
