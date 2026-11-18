import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadActiveCourse, quizCurriculum, pilotArticles} from '../web/js/lesson-curriculum.js';
import {makeV2Attempt, selectQuestions, balancedSelection, topicPerformance, questionMetadata, eligibleQuestions, publishedBlueprint, chapterDifficulty, questionDifficulty, specKey, GENERAL_POLICY} from '../web/js/quiz-v2.js';
import {validateBank, gradeAttempt, makeAttempt, rng, validateAttempt, questionForLearner} from '../web/js/quiz-core.js';
import {createQuizStore} from '../web/js/quiz-progress.js';
import {syntaxMixedItems} from '../web/js/quiz-mixed-syntax.js';
import {cambridgeMixedItems} from '../web/js/quiz-mixed-cambridge.js';
import {validateMixedItems, gradeQuestion, REQUIRED_CHAPTER_FORMATS} from '../web/js/quiz-mixed-eval.js';
import {makeLessonPractice} from '../web/js/quiz-lesson-practice.js';
import {makeAssessmentItems} from '../web/js/quiz-assessment-items.js';
import {fromCanonicalEnvelope, moveNode} from '../web/js/syntax-builder.js';
const json = p => JSON.parse(fs.readFileSync(new URL('../'+p, import.meta.url)));
const course = await loadActiveCourse(async p => ({ok:true,json:async()=>json('web'+p)}));
const curriculum = quizCurriculum(course);
const bank = validateBank(json('web/content/quizzes/bank.json'));
assert.deepEqual(curriculum.map(t=>t.id), ['syntax','cambridge']);
assert.deepEqual(curriculum.map(t=>t.chapters.length),[11,20]);
for(const track of curriculum){
  const lessons=course.lessons.filter(l=>l.track===track.lessonTrack);
  assert.deepEqual(track.chapters.map(c=>[c.id,c.title,c.chapter]),lessons.map(l=>[l.lesson_id,l.title,l.chapter]));
  for(const chapter of track.chapters){
    assert.ok(chapter.topics.length);
    assert.ok(chapter.topics.every(t=>!['introduction','recap','closing-check','chapter-review','what-this-course-covers'].includes(t.id)));
    if(pilotArticles[chapter.id])assert.ok(chapter.topics.every(t=>pilotArticles[chapter.id].sections.some(s=>s.id===t.id&&s.title===t.title)));
  }
}
assert.equal(curriculum[0].chapters[2].title,'Sentence structure: categories');
assert.ok(curriculum[0].chapters[2].topics.some(t=>t.id==='prepositions-and-coordination'));
assert.equal(eligibleQuestions(bank,curriculum,'syntax').length,110);
assert.equal(eligibleQuestions(bank,curriculum,'cambridge').length,10);
const spec={track:'syntax',mode:'topic',chapter:'br-03',topic:'worked-example'};
assert.equal(publishedBlueprint(bank,curriculum,spec).assessment_id,'quiz-br-03');
assert.equal(publishedBlueprint(bank,curriculum,{...spec,chapter:'br-11'}),null,'do not broaden the published scope to unrelated topics');
const a=makeV2Attempt(bank,curriculum,spec,{},42,'test-a');
assert.equal(a.presented.length,5);
assert.deepEqual(a.presented,makeV2Attempt(bank,curriculum,spec,{},42,'test-a').presented);
assert.equal(new Set(a.presented.map(q=>q.item_id)).size,5);
assert.ok(new Set(Array.from({length:30},(_,i)=>JSON.stringify(makeV2Attempt(bank,curriculum,spec,{},i*1384921).presented))).size>20);
assert.ok(new Set(Array.from({length:30},(_,i)=>makeV2Attempt(bank,curriculum,spec,{},i*1384921).presented).flat().map(r=>JSON.stringify(r.option_order))).size>1);
assert.throws(()=>selectQuestions(bank,curriculum,{...spec,topic:'concepts'}),/Insufficient approved questions/);
assert.throws(()=>selectQuestions(bank,curriculum,{...spec,mode:'general'}),/Insufficient approved questions/);
assert.throws(()=>selectQuestions(bank,curriculum,{track:'cambridge',mode:'master',count:20}),/Insufficient approved questions|distinct/);
assert.throws(()=>selectQuestions(bank,curriculum,{track:'syntax',mode:'master',count:10}),/at least 11/);
const master=makeV2Attempt(bank,curriculum,{track:'syntax',mode:'master',count:15},{},55);
const counts={};for(const ref of master.presented){const q=bank.items.find(q=>q.item_id===ref.item_id);counts[q.lesson_id]=(counts[q.lesson_id]||0)+1;}
assert.equal(Object.keys(counts).length,11);
assert.deepEqual(Object.values(counts).sort(),[1,1,1,1,1,1,1,2,2,2,2]);
assert.equal(gradeAttempt(bank,master).incorrect,15);
assert.equal(gradeAttempt(bank,master).target_xp,0);
assert.throws(()=>validateAttempt(bank,{...master,xp_policy:'unscored-v2'}),/verified-v2/);
assert.throws(()=>validateAttempt(bank,{...a,presented:a.presented.slice(0,4)}),/five/);
assert.throws(()=>validateAttempt(bank,{...a,presented:[a.presented[0],...a.presented.slice(0,4)]}),/Distinct/);
assert.throws(()=>selectQuestions(bank,curriculum,{track:'syntax',mode:'master',count:51}),/50/);
for(const count of [11,25,50])assert.equal(selectQuestions(bank,curriculum,{track:'syntax',mode:'master',count},{},42).items.length,count);
// Historical Master attempts over 50 remain readable and gradable cleanly without breakage.
const historicalMaster={...master,presented:bank.items.filter(q=>questionMetadata(q,curriculum)?.track_id==='syntax').slice(0,60).map(q=>({item_id:q.item_id,content_version:q.content_version,option_order:q.options.map(o=>o.id)}))};
validateAttempt(bank,historicalMaster);assert.equal(gradeAttempt(bank,historicalMaster).incorrect,60);
for(const groupCount of [3,5,7]){
  const groups=Array.from({length:groupCount},(_,g)=>({id:g,items:Array.from({length:10},(_,i)=>({g,i}))}));
  const selected=balancedSelection(groups,Math.max(GENERAL_POLICY.minimum,groupCount),rng(42));
  const per=groups.map(g=>selected.filter(q=>q.g===g.id).length);
  assert.equal(selected.length,Math.max(5,groupCount));assert.ok(Math.max(...per)-Math.min(...per)<=1);assert.ok(per.every(Boolean));
  const testCurriculum=[{id:'syntax',chapters:[{id:'general-test',topics:groups.map(g=>({id:String(g.id)}))}]}];
  const testBank={...bank,items:groups.flatMap(g=>g.items.map(({i})=>({...bank.items[0],item_id:`general-${g.id}-${i}`,lesson_id:'general-test',subtopic_id:String(g.id)})))};
  const general=makeV2Attempt(testBank,testCurriculum,{track:'syntax',mode:'general',chapter:'general-test'},{},42);
  assert.equal(general.presented.length,Math.max(5,groupCount));
  assert.equal(new Set(general.presented.map(r=>testBank.items.find(q=>q.item_id===r.item_id).subtopic_id)).size,groupCount);
  assert.equal(gradeAttempt(testBank,general).target_xp,0);
}
const remainderWinners=new Set();
for(let seed=0;seed<100;seed++){
  const selected=balancedSelection(Array.from({length:7},(_,g)=>({id:g,items:[`${g}-a`,`${g}-b`]})),8,rng(seed*938327));
  for(let g=0;g<7;g++)if(selected.filter(q=>q.startsWith(`${g}-`)).length===2)remainderWinners.add(g);
}
assert.equal(remainderWinners.size,7,'remainder allocation rotates across seeded attempts');
const capped=balancedSelection([{id:'a',items:['a']},{id:'b',items:['b','c','d','e']}],5,rng(1));
assert.equal(capped.length,5);
// Test-only enriched bank: no new approval claims enter production content.
const fakeCurriculum=[{id:'syntax',chapters:[{id:'test',topics:[{id:'weak'},{id:'strong'},{id:'unseen'}]}]},{id:'cambridge',chapters:[{id:'other',topics:[{id:'weak'}]}]}];
const fakeItems=[];
for(const [chapter,track] of [['test','syntax'],['other','cambridge']])for(const topic of ['weak','strong','unseen'])for(let i=0;i<15;i++){
  fakeItems.push({...bank.items[0],source_ids:track==='syntax'?bank.items[0].source_ids:bank.items.find(q=>q.lesson_id==='cgel-clauses').source_ids,item_id:`${chapter}-${topic}-${i}`,lesson_id:chapter,chapter_id:chapter,track_id:track,subtopic_id:topic,concept_ids:[`${track}-${topic}`]});
}
const fakeBank={...bank,items:fakeItems};
const history={};
for(const [topic,correct] of [['weak',false],['strong',true]]){
  const t=makeV2Attempt(fakeBank,fakeCurriculum,{track:'syntax',mode:'topic',chapter:'test',topic},{},421);
  t.submitted_at='2026-11-01T00:00:00Z';
  for(const r of t.presented)t.responses[r.item_id]=correct?'a':'b';
  history[t.attempt_id]=t;
}
const perf=topicPerformance(fakeBank,fakeCurriculum,history,'syntax');
assert.equal(perf.missed.size,5);assert.equal(perf.topics.get('test/weak').accuracy,2/9);
assert.equal(perf.topics.has('test/unseen'),false);
const personalized=makeV2Attempt(fakeBank,fakeCurriculum,{track:'syntax',mode:'personalized'},history,99);
assert.equal(personalized.diagnostic,false);
assert.equal(personalized.title,'Review your Errors');
const diverseKinds=makeV2Attempt(bank,curriculum,{track:'syntax',mode:'topic',chapter:'br-01',topic:'worked-example'},{},11);
assert.ok(new Set(diverseKinds.presented.map(r=>bank.items.find(q=>q.item_id===r.item_id).kind)).size>=4,'multi-format pool rotates across distinct question kinds');
assert.ok(personalized.presented.every(r=>r.item_id.startsWith('test-weak-')&&!perf.missed.has(r.item_id)&&!perf.seen.has(r.item_id)));
assert.throws(()=>makeV2Attempt(fakeBank,fakeCurriculum,{track:'cambridge',mode:'personalized'},history,99),/missed questions/,'Review your errors is unavailable until errors exist in the track');
assert.equal(chapterDifficulty(curriculum[0].chapters[0]),'easy');
assert.equal(chapterDifficulty(curriculum[0].chapters[5]),'medium');
assert.equal(chapterDifficulty(curriculum[0].chapters[9]),'hard');
assert.equal(specKey({track:'cambridge',mode:'master',count:25,difficulty:'hard',content_tier:'lesson-assessment',format:'formal'}),'quiz-v2:cambridge:master:::25:hard:lesson-assessment:formal-1');
const easyMaster=makeV2Attempt(bank,curriculum,{track:'syntax',mode:'master',count:15,difficulty:'easy'},{},17);
const hardMaster=makeV2Attempt(bank,curriculum,{track:'syntax',mode:'master',count:15,difficulty:'hard'},{},17);
assert.equal(easyMaster.presented.length,15);
assert.equal(hardMaster.presented.length,15);
assert.ok(easyMaster.title.includes('Easy')&&hardMaster.title.includes('Hard'));
const countTier=(attempt,tier)=>attempt.presented.filter(r=>questionDifficulty(bank.items.find(q=>q.item_id===r.item_id),curriculum)===tier).length;
assert.ok(countTier(easyMaster,'easy')>countTier(hardMaster,'easy'),'Easy Master selects more easy questions than Hard Master');
assert.ok(countTier(hardMaster,'hard')>countTier(easyMaster,'hard'),'Hard Master selects more hard questions than Easy Master');
const before=perf.topics.get('test/weak').weakness;
for(let i=0;i<3;i++){
  const t=makeV2Attempt(fakeBank,fakeCurriculum,{track:'syntax',mode:'topic',chapter:'test',topic:'weak'},{},i);
  t.submitted_at=`2026-11-0${i+2}T00:00:00Z`;for(const r of t.presented)t.responses[r.item_id]='a';history[t.attempt_id]=t;
}
const improved=topicPerformance(fakeBank,fakeCurriculum,history,'syntax');
assert.ok(improved.topics.get('test/weak').weakness<before);
assert.equal(improved.missed.size,5,'later success never clears historical exclusion');
const small={...fakeBank,items:fakeItems.filter(q=>q.item_id.startsWith('test-weak-')).slice(0,5)};
assert.throws(()=>makeV2Attempt(small,fakeCurriculum,{track:'syntax',mode:'personalized'},history,0),/excluding every previously missed/);
const blocked={...bank,items:bank.items.map(q=>({...q,review_status:'UNREVIEWED'}))};
assert.equal(eligibleQuestions(blocked,curriculum,'syntax').length,0);
const wrongFramework={...bank,items:bank.items.map(q=>({...q,source_ids:bank.items.find(q=>q.lesson_id==='cgel-clauses').source_ids}))};
assert.equal(eligibleQuestions(wrongFramework,curriculum,'syntax').length,0);
const queued=json('web/content/quizzes/v2-review-queue.json');
assert.equal(queued.items.length,10);
for(const q of queued.items){assert.equal(q.review_status,'UNREVIEWED');assert.equal(q.publication_status,'draft');assert.ok(questionMetadata(q,curriculum));assert.ok(!bank.items.some(i=>i.item_id===q.item_id));assert.ok(q.outcome_ids.every(id=>course.lessons.find(l=>l.lesson_id===q.lesson_id).outcomes.some(o=>o.id===id)));}
// Full persistence, scores, variable navigation, no XP RPC and identity isolation.
const memory=new Map(),storage={getItem:k=>memory.get(k),setItem:(k,v)=>memory.set(k,v)};
let rpcs=0;
const cloud=new Map();
const client={
  rpc:async(name,args)=>{
    if(name!=='save_quiz_v2_attempt')throw Error('Unexpected RPC '+name);
    rpcs++;
    const a=args.p_attempt,score=a.presented.filter(r=>a.responses[r.item_id]===bank.items.find(q=>q.item_id===r.item_id).answer).length;
    const prev=cloud.get(a.attempt_id),submitted_at=args.p_submit?(prev?.submitted_at||'2026-11-16T00:00:00Z'):null;
    const earned=args.p_submit&&!prev?.submitted_at?score*2:0;
    const row={...a,started_at:prev?.started_at||'2026-11-16T00:00:00Z',submitted_at,correct:args.p_submit?score:null};
    cloud.set(a.attempt_id,structuredClone(row));
    return {data:{attempt_id:a.attempt_id,submitted_at,correct:row.correct,earned},error:null};
  },
  from:table=>({
    select:async()=>({data:table==='quiz_attempts_v2'?[...cloud.values()].map(r=>structuredClone(r)):[]}),
    upsert:async()=>{throw Error('Scored V2 must use save_quiz_v2_attempt RPC');},
  }),
};
const store=createQuizStore(bank,{storage,userId:'user_a',client});
const started=await store.startV2(curriculum,{track:'syntax',mode:'master',count:15},71);
await store.move(started.attempt_id,14);
for(const ref of started.presented){const q=bank.items.find(q=>q.item_id===ref.item_id);await store.answer(started.attempt_id,q.item_id,q.answer);}
const reload=createQuizStore(bank,{storage,userId:'user_a',client});
assert.equal(reload.draft(started).position,14);
assert.deepEqual(reload.draft(started).presented,started.presented);
const done=await reload.submit(started.attempt_id);
assert.equal(done.grade.correct,15);assert.equal(done.earned,30);
assert.equal((await reload.submit(started.attempt_id)).earned,0);
assert.ok(rpcs>0);
await assert.rejects(()=>reload.answer(started.attempt_id,started.presented[0].item_id,'a'),/read-only/);
assert.equal(Object.keys(createQuizStore(bank,{storage,userId:'user_b'}).attempts).length,0);
const otherDevice=createQuizStore(bank,{userId:'user_a',client});await otherDevice.load();
assert.equal(otherDevice.attempts[started.attempt_id].submitted_at,reload.attempts[started.attempt_id].submitted_at);
// Existing published history remains visible to personalization.
const legacy=makeAttempt(bank,bank.assessments[0],22);legacy.submitted_at=new Date().toISOString();
assert.equal(topicPerformance(bank,curriculum,{legacy},'syntax').missed.size,5);
// Mixed-format verification across ALL 31 General Quizzes, 327 Subtopic Quizzes, 18 Master configs, and both Track Review your Errors:
const fullPractice=makeLessonPractice(curriculum,json('web/content/quizzes/syntax-practice-source.json'));
const mixedBank={...bank,practice_items:fullPractice,assessment_items:makeAssessmentItems(fullPractice,curriculum),mixed_items:validateMixedItems([...syntaxMixedItems,...cambridgeMixedItems],curriculum)};
for(const t of curriculum){
  const req=REQUIRED_CHAPTER_FORMATS[t.id];
  for(const ch of t.chapters){
    const attempt=makeV2Attempt(mixedBank,curriculum,{track:t.id,mode:'general',chapter:ch.id,content_tier:'lesson-practice',format:'mixed'},{},77);
    assert.equal(attempt.practice,true);assert.equal(attempt.xp_policy,'unscored-v2');
    assert.equal(attempt.presented.length,Math.max(GENERAL_POLICY.minimum,ch.topics.length));
    const kinds=new Set(attempt.presented.map(ref=>mixedBank.mixed_items.find(q=>q.item_id===ref.item_id)?.kind).filter(Boolean));
    for(const fmt of req)assert.ok(kinds.has(fmt),`${ch.id} General Quiz must include ${fmt}`);
    const projected=questionForLearner(mixedBank,attempt,0);
    assert.equal(projected.accepted_answers,undefined);assert.equal(projected.expected_tree,undefined);assert.equal(projected.rationale,undefined);
    for(const tp of ch.topics){
      const topAttempt=makeV2Attempt(mixedBank,curriculum,{track:t.id,mode:'topic',chapter:ch.id,topic:tp.id,content_tier:'lesson-practice',format:'mixed'},{},77);
      assert.equal(topAttempt.presented.length,5);
      const tMixedKinds=new Set(topAttempt.presented.map(ref=>mixedBank.mixed_items.find(q=>q.item_id===ref.item_id)?.kind).filter(Boolean));
      assert.ok(tMixedKinds.size>=2,`${ch.id}/${tp.id} Subtopic Quiz must include >=2 non-MCQ formats`);
    }
  }
  for(const diff of ['easy','medium','hard']){
    for(const count of [t.chapters.length,25,50]){
      const mAtt=makeV2Attempt(mixedBank,curriculum,{track:t.id,mode:'master',count,difficulty:diff,content_tier:'lesson-practice',format:'mixed'},{},88);
      assert.equal(mAtt.presented.length,count);
      const mKinds=new Set(mAtt.presented.map(ref=>mixedBank.mixed_items.find(q=>q.item_id===ref.item_id)?.kind).filter(Boolean));
      for(const fmt of req)assert.ok(mKinds.has(fmt),`${t.id} Master Quiz (${diff}/${count}) must include ${fmt}`);
    }
  }
  const seedMistake=makeV2Attempt(mixedBank,curriculum,{track:t.id,mode:'topic',chapter:t.chapters[0].id,topic:t.chapters[0].topics[0].id,content_tier:'lesson-practice',format:'mixed'},{},19);
  seedMistake.submitted_at='2026-11-16T00:00:00Z';
  const persMixed=makeV2Attempt(mixedBank,curriculum,{track:t.id,mode:'personalized',content_tier:'lesson-practice',format:'mixed'},{[seedMistake.attempt_id]:seedMistake},29);
  const pKinds=new Set(persMixed.presented.map(ref=>mixedBank.mixed_items.find(q=>q.item_id===ref.item_id)?.kind).filter(Boolean));
  assert.ok(pKinds.size>=2,`${t.id} Review your Errors must include >=2 non-MCQ formats`);
}
const capItem=cambridgeMixedItems.find(q=>q.item_id==='mixed:cgel-ch20:capitalisation:grammar_correction:12');
assert.equal(gradeQuestion(capItem,'we visited london last summer.').correct,false,'capitalisation error leaves lowercase rejected');
assert.equal(gradeQuestion(capItem,'We visited London last summer.').correct,true,'capitalised correction accepted');
const sampleFill=syntaxMixedItems.find(q=>q.kind==='fill_blank');
assert.equal(gradeQuestion(sampleFill,'  '+sampleFill.accepted_answers[0].toUpperCase()+'. ').correct,true);
assert.equal(gradeQuestion(sampleFill,'').correct,false);
const sampleGram=cambridgeMixedItems.find(q=>q.kind==='grammar_correction');
assert.equal(gradeQuestion(sampleGram,sampleGram.stimulus.sentence).correct,false,'unchanged erroneous sentence rejected');
assert.equal(gradeQuestion(sampleGram,sampleGram.accepted_answers[0]).correct,true);
const sampleTree=syntaxMixedItems.find(q=>q.kind==='tree_builder');
const built=fromCanonicalEnvelope(sampleTree.expected_tree);
const firstId=Object.keys(built.nodes)[0];
moveNode(built,firstId,built.nodes[firstId].x+180,built.nodes[firstId].y+95);
assert.equal(gradeQuestion(sampleTree,{schema:'builder-tree-1',touched:true,model:built}).correct,true,'tree grading ignores visual coordinates and arbitrary IDs');
assert.equal(gradeQuestion(sampleTree,{schema:'builder-tree-1',touched:true,model:{nodes:{a:{id:'a',kind:'word',type:'word',text:'only',x:0,y:0,parent:null}}}}).correct,false);
console.log(`PASS Quiz V2: ${curriculum.map(t=>`${t.chapters.length} chapters/${t.chapters.reduce((n,c)=>n+c.topics.length,0)} topics`).join(', ')}; mixed-format coverage (${syntaxMixedItems.length}+${cambridgeMixedItems.length} items), selection, balanced counts, review gates, seed replay, personalization/exclusions/improvement, private persistence, variable grading and zero XP.`);
