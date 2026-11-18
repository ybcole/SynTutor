import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadActiveCourse,quizCurriculum} from '../web/js/lesson-curriculum.js';
import {chapterDescriptions,topicDescription} from '../web/js/quiz-catalog-copy.js';
import {cambridgeMixedItems} from '../web/js/quiz-mixed-cambridge.js';
import {syntaxMixedItems} from '../web/js/quiz-mixed-syntax.js';
import {revisedMixedIds} from '../web/js/quiz-content-revisions.js';
import {gradeQuestion,normalizeResponseText} from '../web/js/quiz-mixed-eval.js';
import {makeV2Attempt,personalizedReviewSummary,missedTopicsForTrack} from '../web/js/quiz-v2.js';
import {fromCanonicalEnvelope} from '../web/js/syntax-builder.js';
import {itemsFor} from '../web/js/quiz-core.js';
import {makeLessonPractice} from '../web/js/quiz-lesson-practice.js';
import {makeAssessmentItems} from '../web/js/quiz-assessment-items.js';
import {levelFromXp,xpToReach} from '../web/js/level.js';
const read=p=>JSON.parse(fs.readFileSync(new URL('../web'+p,import.meta.url)));
const curriculum=quizCurriculum(await loadActiveCourse(async p=>({ok:true,json:()=>read(p)})));
const descriptions=[];
for(const track of curriculum)for(const chapter of track.chapters){
 assert.ok(chapterDescriptions[chapter.id]?.length>30);
 assert.equal(chapterDescriptions[chapter.id].split('. ').length,2,'chapter copy explains concepts and application in two concise sentences');
 for(const topic of chapter.topics){const text=topicDescription(chapter,topic);assert.ok(text.length>20&&text.length<130);descriptions.push(text);}
}
assert.equal(descriptions.length,327);
assert.equal(new Set(Object.values(chapterDescriptions)).size,31);
const bank={...read('/content/quizzes/bank.json'),mixed_items:[...syntaxMixedItems,...cambridgeMixedItems]};
bank.assessment_items=makeAssessmentItems(makeLessonPractice(curriculum,read('/content/quizzes/syntax-practice-source.json')),curriculum);
for(const id of revisedMixedIds){
 const old=bank.mixed_items.find(q=>q.item_id===id),replacement=bank.mixed_items.find(q=>q.replaces_item_id===id);
 assert.ok(old.retired_from_selection);assert.ok(replacement&&!replacement.retired_from_selection);
 assert.equal(old.content_version,'2.0.0');assert.equal(replacement.content_version,'2.0.1');
 const historical={quiz_v2:true,practice:true,xp_policy:'unscored-v2',spec:{content_tier:'lesson-practice'},presented:[{item_id:id,content_version:'2.0.0'}]};
 assert.equal(itemsFor(bank,historical)[0],old,'historical manifest still resolves original content');
 if(old.accepted_answers&&old.kind!=='sentence_reconstruction')assert.equal(gradeQuestion(old,old.accepted_answers[0]).correct,true);
 for(let seed=0;seed<60;seed++){
  const attempt=makeV2Attempt(bank,curriculum,{track:old.track_id,mode:'topic',chapter:old.chapter_id,topic:old.subtopic_id,content_tier:'lesson-practice',format:'mixed'},{},seed);
  assert.ok(!attempt.presented.some(ref=>ref.item_id===id),'new attempts exclude retired content');
 }
 if(replacement.kind==='sentence_reconstruction'){
  const order=[];const available=replacement.tokens.map((t,i)=>({t,i}));
  let rest=replacement.accepted_answers[0];
  while(rest){const found=available.find(x=>rest===x.t||rest.startsWith(x.t+' '));assert.ok(found);order.push(found.i);rest=rest.slice(found.t.length).trim();available.splice(available.indexOf(found),1);}
  assert.equal(gradeQuestion(replacement,order).correct,true);
 }else if(replacement.accepted_answers){
  for(const answer of replacement.accepted_answers)assert.equal(gradeQuestion(replacement,answer).correct,true);
 }else{
  const response={model:fromCanonicalEnvelope(replacement.expected_tree),touched:true};
  assert.equal(gradeQuestion(replacement,response).correct,true);
  assert.equal(gradeQuestion(old,{model:fromCanonicalEnvelope(old.expected_tree),touched:true}).correct,true,'historical tree key unchanged');
  if(old.chapter_id==='br-04')assert.equal(replacement.subtopic_id,'concepts','transitive repair maps to verb classes, not ditransitives');
  if(old.chapter_id==='br-09'){
   const nodes=[];const visit=n=>{nodes.push(n);for(const child of n.children||[])visit(child);};visit(replacement.expected_tree.root);
   assert.ok(nodes.some(n=>n.label==='C2'&&n.index===1),'wh-expression is in higher C2');
   assert.ok(nodes.some(n=>n.label==='C1'),'lower C1 is explicit');
   assert.ok(nodes.some(n=>n.gap&&n.index===1),'wh-expression has a corresponding gap');
   if(old.subtopic_id!=='embedded-interrogatives')assert.ok(nodes.some(n=>n.gap&&n.index===2),'fronted auxiliary has a separate gap');
  }
 }
}
// Every active reconstruction alternative must use each indivisible token once.
for(const q of bank.mixed_items.filter(q=>q.kind==='sentence_reconstruction'&&!q.retired_from_selection)){
 for(const answer of q.accepted_answers){
  function findOrder(rest,remaining,order=[]){
   if(!remaining.length)return rest===''?order:null;
   for(const i of remaining){
    const token=normalizeResponseText(q.tokens[i]);
    if(rest===token||rest.startsWith(token+' ')){
     const found=findOrder(rest.slice(token.length).trim(),remaining.filter(j=>j!==i),[...order,i]);
     if(found)return found;
    }
   }
   return null;
  }
  const order=findOrder(normalizeResponseText(answer,{stripTrailingPeriod:true}),q.tokens.map((_,i)=>i));
  assert.ok(order,`accepted answer must be buildable: ${q.item_id}: ${answer}`);
  assert.equal(gradeQuestion(q,order).correct,true);
 }
}
const empty=personalizedReviewSummary(bank,curriculum,{},'syntax');
assert.match(empty,/Complete Syntax chapter or subtopic quizzes/);
const missed=bank.mixed_items.find(q=>q.chapter_id==='br-01'&&q.subtopic_id==='concepts'&&q.kind==='fill_blank');
const wrong={attempt_id:'miss',submitted_at:'2026-11-17T00:00:00Z',presented:[{item_id:missed.item_id,content_version:missed.content_version}],responses:{[missed.item_id]:'incorrect'}};
assert.equal(personalizedReviewSummary(bank,curriculum,{draft:{...wrong,submitted_at:null}},'syntax'),empty);
assert.equal(personalizedReviewSummary(bank,curriculum,{unknown:{...wrong,presented:[{item_id:missed.item_id,content_version:'unknown'}]}},'syntax'),empty);
assert.equal(personalizedReviewSummary(bank,curriculum,{correct:{...wrong,responses:{[missed.item_id]:missed.accepted_answers[0]}}},'syntax'),empty);
const summary=personalizedReviewSummary(bank,curriculum,{wrong},'syntax');
assert.ok(summary.includes(topicDescription({id:'br-01'},{id:'concepts'})));
assert.ok(!/weakest|repeated|persistent/i.test(summary),'one mistake is not a persistent diagnosis');
assert.match(personalizedReviewSummary(bank,curriculum,{wrong},'cambridge'),/^Complete Grammar/,'other-track errors never enter guidance');
assert.equal(personalizedReviewSummary(bank,curriculum,{},'syntax'),empty,'an account without attempts has no inherited focus');
assert.equal(missedTopicsForTrack(bank,curriculum,{wrong},'syntax').length,1);
const moreErrors={wrong};
for(const [i,topic] of ['worked-example','application'].entries()){
 const q=bank.mixed_items.find(q=>q.chapter_id==='br-01'&&q.subtopic_id===topic&&q.kind==='fill_blank');
 moreErrors[`other-${i}`]={...wrong,attempt_id:`other-${i}`,presented:[{item_id:q.item_id,content_version:q.content_version}],responses:{[q.item_id]:'incorrect'}};
}
const ranked=missedTopicsForTrack(bank,curriculum,moreErrors,'syntax');
const limited=personalizedReviewSummary(bank,curriculum,moreErrors,'syntax');
assert.ok(ranked.slice(0,2).every(m=>limited.includes(topicDescription({id:m.chapter_id},{id:m.subtopic_id}))));
assert.ok(!limited.includes(topicDescription({id:ranked[2].chapter_id},{id:ranked[2].subtopic_id})),'summary limits focus to two evidenced topics');
const mismatch={...bank,mixed_items:bank.mixed_items.map(q=>q.item_id===missed.item_id?{...q,track_id:'cambridge'}:q)};
assert.equal(personalizedReviewSummary(mismatch,curriculum,{wrong},'syntax'),empty,'conflicting question mappings are ignored');
const aspect=cambridgeMixedItems.find(q=>q.item_id==='mixed:cgel-ch03:situations-aspect:fill_blank:11:revision-2');
assert.equal(gradeQuestion(aspect,'perfective').correct,false);
assert.equal(gradeQuestion(aspect,'telic').correct,true);
// Preserve the established cumulative curve and reset bar progress at boundaries.
for(let level=0;level<30;level++)for(const xp of [xpToReach(level),xpToReach(level+1)-1]){
 const state=levelFromXp(xp);assert.equal(state.level,level);assert.equal(state.next-state.floor,state.span);
 assert.equal(state.xp,state.floor+state.into);assert.ok(state.into>=0&&state.into<state.span);
}
assert.deepEqual(levelFromXp(250),{xp:250,level:2,into:30,span:140,floor:220,next:360});
console.log('PASS refinements: 31 chapter/327 topic descriptions, submitted-error guidance/track isolation/two-topic limit, versioned corrections and historical keys, all active reconstruction alternatives, Chapter 9 C1/C2 and gaps, retired-item exclusion, XP boundaries.');
