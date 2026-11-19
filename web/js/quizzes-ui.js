import {chapterDescriptions,topicDescription} from './quiz-catalog-copy.js';
import { showCurriculumState } from './curriculum-state.js';
import {validateBank,quizKey,itemsFor,gradeAttempt,questionForLearner,reviewForLearner,MAX_QUIZ_ITEMS} from './quiz-core.js';
import {createQuizStore} from './quiz-progress.js';
import {composeQuizEvidence,requestQuizEvidence,requestEvidence,renderEvidence} from './explanation-evidence.js?v=2026.11.18f';
import {renderLessonTree} from './lessons-ui.js';
import {subscribeAuthState} from './auth.js';
import {loadActiveCourse,quizCurriculum} from './lesson-curriculum.js';
import {selectQuestions,specKey,eligibleQuestions,questionMetadata,topicPerformance,personalizedReviewSummary,DIFFICULTIES,MAX_MASTER_QUIZ_ITEMS,DEFAULT_MASTER_QUIZ_ITEMS} from './quiz-v2.js';
import {makeLessonPractice,validateLessonPractice} from './quiz-lesson-practice.js';
import {makeAssessmentItems,validateAssessmentItems} from './quiz-assessment-items.js';
import {applyQuizScope} from './quiz-scope.js';
import {syntaxMixedItems} from './quiz-mixed-syntax.js';
import {cambridgeMixedItems} from './quiz-mixed-cambridge.js';
import {validateMixedItems,isResponseProvided,formatReconstructionAnswer,isMixedKind} from './quiz-mixed-eval.js';
import {addWordsFromText,createModel,fromCanonicalEnvelope} from './syntax-builder.js';
let host,config={},bank,store,curriculum,current=null,trackId='syntax',busy=false,message='',generation=0,pendingConfirmAttempt=null,lastEarned=null,quizBuilderCleanup=null,flushTextDraft=null;
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const button=(text,fn,cls='')=>{const b=el('button',text,cls);b.type='button';b.addEventListener('click',fn);return b;};
function iconButton(label,svg,fn,cls='header-icon-btn'){
 const b=button('',fn,cls);
 b.setAttribute('aria-label',label);
 b.title=label;
 b.innerHTML=svg;
 return b;
}
const BACK_ARROW_SVG='<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5"/><path d="m12 19-7-7 7-7"/></svg>';
const PREV_ARROW_SVG='<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>';
const NEXT_ARROW_SVG='<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>';
const formatDiff=d=>d?d[0].toUpperCase()+d.slice(1):'';
const plural=(n,word)=>`${n} ${n===1?word:word+'s'}`;
const KIND_LABELS={
 fill_blank:'Fill in the blanks',
 grammar_correction:'Grammar error correction',
 syntax_correction:'Syntax error correction',
 sentence_reconstruction:'Sentence reconstruction',
 tree_builder:'Syntax tree builder',
};
const trackTabLabel=track=>track.id==='cambridge'?'Grammar':track.title;
const lessonTitle=lid=>curriculum?.flatMap(t=>t.chapters).find(c=>c.id===lid)?.title||bank?.assessments?.find(a=>a.assessment_id===`quiz-${lid}`)?.title||lid;
const parseLessonRef=ref=>{const m=/^#lesson\/([^/]+)(?:\/([^/]+))?/.exec(ref||'');return m?{lessonId:m[1],section:m[2]||null}:null;};
const subtopicTitle=(lid,sid)=>sid?curriculum?.flatMap(t=>t.chapters).find(c=>c.id===lid)?.topics?.find(x=>x.id===sid)?.title||null:null;
function assessmentFor(t){return bank.assessments.find(a=>quizKey(a)===quizKey(t));}
function cleanupActiveQuestion(){
 flushTextDraft?.();flushTextDraft=null;
 quizBuilderCleanup?.();quizBuilderCleanup=null;
}
async function action(fn){
 if(busy)return;flushTextDraft?.();const token=generation,focusName=document.activeElement?.name,focusValue=document.activeElement?.value;busy=true;pendingConfirmAttempt=null;host.setAttribute('aria-busy','true');host.querySelectorAll('button,input,textarea').forEach(n=>{n.disabled=true;});
 try{const result=await fn();if(token!==generation)return;
  if(result?.attempt_id)current=result.attempt_id;
  if(result&&Object.hasOwn(result,'earned')){
   lastEarned={attempt_id:result.attempt_id,earned:result.earned};
   window.dispatchEvent(new Event('syntutor:quiz-progress'));
  }
  message='';
 }catch(e){if(token===generation)message=e.message;}
 finally{if(token===generation){busy=false;host.setAttribute('aria-busy','false');render();if(focusName)host.querySelector(`input[name="${CSS.escape(focusName)}"][value="${focusValue}"]`)?.focus();}}
}
function inlineNotice(parent){
 const signedIn=Boolean(config.userId?.());
 const syncFailed=signedIn&&store.status!=='Synced to your account';
 const text=message||(syncFailed?store.status:'');
 if(!text&&!syncFailed)return;
 const bar=el('div',undefined,'quiz-notice');
 bar.setAttribute('role','status');
 if(text)bar.append(el('p',text));
 if(syncFailed)bar.append(button('Retry sync',()=>action(()=>store.retry())));
 (parent||host).append(bar);
}
function attemptHistorySummary(assessment){
 const previous=Object.values(store.attempts).filter(t=>quizKey(t)===quizKey(assessment)&&t.submitted_at&&!store.isArchived(t)).sort((a,b)=>a.submitted_at.localeCompare(b.submitted_at));
 if(!previous.length)return null;
 const last=previous.at(-1),best=Math.max(...previous.map(t=>gradeAttempt(bank,t).correct/t.presented.length));
 return `Best ${Math.round(best*100)}% · Last ${gradeAttempt(bank,last).correct}/${last.presented.length} · ${plural(previous.length,'attempt')}`;
}
function v2Card(parent,title,spec,opts={}){
 const isPersonalized=spec.mode==='personalized';
 const isGeneral=spec.mode==='general';
 const isSubtopic=spec.mode==='topic';
 const activeSpec={...spec,content_tier:'lesson-practice',format:'mixed'};
 const card=el('article',undefined,`curriculum-card quiz-topic-card${opts.featured?' quiz-featured-card':''}${isPersonalized?' is-review':''}${isGeneral?' is-general':''}${isSubtopic?' is-subtopic':''}`);
 let reason='';
 try{selectQuestions(bank,curriculum,activeSpec,store.attempts,0);}catch(e){reason=e.message;}
 const assessment={assessment_id:specKey(activeSpec),content_version:'2.0.0'},draft=store.draft(assessment);
 if(opts.featured){
  const headRow=el('div',undefined,'quiz-card-head');
  const titleWrap=el('div',undefined,'quiz-card-title-wrap');
  titleWrap.append(el(opts.headingTag||'h3',title));
  if(!isPersonalized&&opts.trackLabel)titleWrap.append(el('span',opts.trackLabel,'quiz-track-tag'));
  headRow.append(titleWrap);
  card.append(headRow);
  if(isPersonalized){
   const desc=personalizedReviewSummary(bank,curriculum,store.attempts,spec.track);
   card.append(el('p',desc,'quiz-card-desc'));
   if(reason&&topicPerformance(bank,curriculum,store.attempts,spec.track).missed.size)card.append(el('p',reason,'quiz-card-error'));
  }
  const statusText=reason&&!isPersonalized
   ?reason
   :draft
    ?null
    :attemptHistorySummary(assessment);
  if(statusText)card.append(el('p',statusText,reason&&!isPersonalized?'quiz-card-error':'quiz-card-status'));
  const cardFoot=el('div',undefined,'quiz-card-footer');
  const start=button(draft?'Resume quiz':reason?'Unavailable':'Start quiz',()=>action(()=>draft||store.startV2(curriculum,activeSpec)),'lesson-primary');
  start.disabled=!!reason&&!draft;
  cardFoot.append(start);
  card.append(cardFoot);
  parent.append(card);
  return;
 }
 const mainCol=el('div',undefined,'quiz-row-main');
 const titleWrap=el('div',undefined,'quiz-card-title-wrap');
 titleWrap.append(el(opts.headingTag||'h3',title));
 mainCol.append(titleWrap);
 const descText=opts.description||(isGeneral?'Covers every assessable subtopic in this chapter.':'');
 if(descText)mainCol.append(el('p',descText,'quiz-card-desc'));
 const statusText=reason
  ?reason
  :draft
   ?null
   :attemptHistorySummary(assessment);
 if(statusText)mainCol.append(el('p',statusText,reason?'quiz-card-error':'quiz-card-status'));
 const sideCol=el('div',undefined,'quiz-row-side');
 const start=button(draft?'Resume quiz':reason?'Unavailable':'Start quiz',()=>action(()=>draft||store.startV2(curriculum,activeSpec)),'lesson-primary');
 start.disabled=!!reason&&!draft;
 sideCol.append(start);
 card.append(mainCol,sideCol);
 parent.append(card);
}
function masterQuizCard(parent,track){
 const master=el('section',undefined,'curriculum-card quiz-practice quiz-featured-card is-master');
 const min=track.chapters.length,masterTier='lesson-practice';
 const available=new Set([
  ...eligibleQuestions(bank,curriculum,trackId,'lesson-assessment'),
  ...(bank.mixed_items||[]).filter(q=>questionMetadata(q,curriculum)?.track_id===trackId),
 ].map(q=>q.item_id)).size,max=Math.min(MAX_MASTER_QUIZ_ITEMS,available);
 const defaultCount=max>=min?Math.min(Math.max(DEFAULT_MASTER_QUIZ_ITEMS,min),max):min;
 const initialCount=masterCounts[trackId]>=min&&masterCounts[trackId]<=max?masterCounts[trackId]:defaultCount;
 const headRow=el('div',undefined,'quiz-card-head');
 headRow.append(el('h2',`${track.title} Master Quiz`),el('span',max>=min?`${min}–${max} questions`:'Unavailable','quiz-card-count'));
 master.append(headRow);
 master.append(el('p','Comprehensive assessment across every chapter.','quiz-card-desc'));
 const controlRow=el('div',undefined,'quiz-master-controls');
 const label=el('label','Questions ');
 const input=el('input');
 input.type='number';input.min=String(min);input.max=String(max);input.step='1';
 input.value=String(initialCount);input.disabled=max<min;
 input.setAttribute('aria-label',`${track.title} Master Quiz question count`);
 label.append(input);
 const diffGroup=el('div',undefined,'quiz-master-difficulty');
 diffGroup.setAttribute('role','group');
 diffGroup.setAttribute('aria-label',`${track.title} Master Quiz difficulty`);
 const activeDiff=DIFFICULTIES.includes(masterDifficulties[trackId])?masterDifficulties[trackId]:'medium';
 masterDifficulties[trackId]=activeDiff;
 const diffButtons=[];
 for(const diff of DIFFICULTIES){
  const btn=button(formatDiff(diff),()=>{
   masterDifficulties[trackId]=diff;
   for(const b of diffButtons)b.setAttribute('aria-pressed',String(b.dataset.difficulty===diff));
   update();
  },'quiz-diff-btn');
  btn.dataset.difficulty=diff;
  btn.setAttribute('aria-pressed',String(activeDiff===diff));
  diffButtons.push(btn);
  diffGroup.append(btn);
 }
 controlRow.append(label,diffGroup);
 master.append(controlRow);
 const target=el('div',undefined,'quiz-master-footer');target.setAttribute('aria-live','polite');
 const update=()=>{
  masterCounts[trackId]=Number(input.value);
  target.replaceChildren();
  if(max<min){
   target.append(el('p',`Needs at least ${min} questions to cover all chapters.`,'quiz-card-error'));
   return;
  }
  if(!input.validity.valid){
   target.append(el('p',`Enter a whole number between ${min} and ${max}.`,'quiz-card-error'));
   return;
  }
  const spec={track:trackId,mode:'master',count:Number(input.value),difficulty:masterDifficulties[trackId],content_tier:masterTier,format:'mixed'};
  const assessment={assessment_id:specKey(spec),content_version:'2.0.0'},draft=store.draft(assessment);
  const statusLine=draft?null:attemptHistorySummary(assessment);
  if(statusLine)target.append(el('p',statusLine,'quiz-card-status'));
  const foot=el('div',undefined,'quiz-card-footer');
  foot.append(button(draft?'Resume quiz':'Start quiz',()=>action(()=>draft||store.startV2(curriculum,spec)),'lesson-primary'));
  target.append(foot);
 };
 input.addEventListener('input',update);update();
 master.append(target);
 parent.append(master);
}
function curriculumCatalog(){
 const header=el('header',undefined,'view-header curriculum-header');
 header.append(el('h1','Quizzes','view-title'));
 host.append(header);

 const body=el('div',undefined,'quiz-catalog-body');
 inlineNotice(body);

 const track=curriculum.find(t=>t.id===trackId);
 const reviewSec=el('section',undefined,'quiz-special-section is-review');
 reviewSec.setAttribute('aria-label','Review your Errors');
 v2Card(reviewSec,'Review your Errors',{track:trackId,mode:'personalized'},{featured:true,headingTag:'h2',trackLabel:trackTabLabel(track)});
 body.append(reviewSec);

 const folder=el('div',undefined,'quiz-folder-panel');
 const nav=el('div',undefined,'lesson-track-tabs');nav.setAttribute('role','group');nav.setAttribute('aria-label','Quiz learning tracks');
 for(const trackItem of curriculum){const b=button(trackTabLabel(trackItem),()=>{trackId=trackItem.id;render();});b.setAttribute('aria-pressed',String(trackId===trackItem.id));nav.append(b);}
 const sheet=el('div',undefined,'quiz-tab-sheet');

 const masterSec=el('section',undefined,'quiz-special-section is-master');
 masterQuizCard(masterSec,track);
 sheet.append(masterSec);

 const chaptersSec=el('section',undefined,'quiz-chapters-section');
 chaptersSec.append(el('h2','Chapter Quizzes','quiz-section-label'));
 const chaptersGroup=el('div',undefined,'quiz-chapters-group');
 for(const chapter of track.chapters){
  const card=el('article',undefined,'curriculum-card lesson-module quiz-chapter');card.dataset.chapter=chapter.id;
  const head=el('div',undefined,'quiz-chapter-header');
  head.append(el('p',`Chapter ${chapter.chapter}`,'lesson-eyebrow'),el('h2',chapter.title,'quiz-chapter-title'));
  head.append(el('p',chapterDescriptions[chapter.id],'quiz-card-desc'));
  const spec={track:trackId,mode:'general',chapter:chapter.id,content_tier:'lesson-practice',format:'mixed'};
  const assessment={assessment_id:specKey(spec),content_version:'2.0.0'},draft=store.draft(assessment);
  let reason='';
  try{selectQuestions(bank,curriculum,spec,store.attempts,0);}catch(e){reason=e.message;}
  const status=draft?null:attemptHistorySummary(assessment);
  if(reason||status)head.append(el('p',reason||status,reason?'quiz-card-error':'quiz-card-status'));
  const start=button('General Quiz',()=>action(()=>draft||store.startV2(curriculum,spec)),'lesson-primary');
  start.setAttribute('aria-label',`General Quiz: ${chapter.title} — ${draft?'Resume':'Start'} General Chapter Quiz`);
  start.disabled=!!reason&&!draft;
  card.append(head);
  const details=el('details',undefined,'quiz-subtopics');
  const key=`${trackId}:${chapter.id}`;details.open=expanded.has(key);
  details.addEventListener('toggle',()=>{if(details.open)expanded.add(key);else expanded.delete(key);});
  details.append(el('summary','Subtopic quizzes'));
  const list=el('div',undefined,'quiz-topic-list');
  for(const [topicIndex,topic] of chapter.topics.entries()){
   v2Card(list,`Quiz ${topicIndex+1}: ${topic.title}`,{track:trackId,mode:'topic',chapter:chapter.id,topic:topic.id},{description:topicDescription(chapter,topic)});
  }
  const footer=el('footer',undefined,'quiz-card-footer quiz-chapter-footer');
  details.append(list);footer.append(details,start);card.append(footer);chaptersGroup.append(card);
 }
 chaptersSec.append(chaptersGroup);
 sheet.append(chaptersSec);
 folder.append(nav,sheet);
 body.append(folder);
 host.append(body);
}
const expanded=new Set(),masterCounts={},masterDifficulties={};
async function loadContent(){
 if(bank&&curriculum)return '';
 const cacheKey='syntutor:quiz-v2:public-content:2';
  let staleWarning='';
  const recordStale=stale=>{
   const chapters=[...new Set(stale.map(s=>s.chapter_id))].join(', ');
   staleWarning=`Syntax practice source is out of date for ${chapters}. Regenerate syntax-practice-source.json before assessing those chapters.`;
  };
  try{
   const [nextBank,course,syntaxSource]=await Promise.all([
   fetch('/content/quizzes/bank.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('Bank unavailable');return r.json();}).then(validateBank),
    loadActiveCourse(),
    fetch('/content/quizzes/syntax-practice-source.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('Practice source unavailable');return r.json();}).catch(()=>null),
  ]);
  bank=nextBank;curriculum=quizCurriculum(course);
  // Only public, compact curriculum metadata is cached, never the 12MB course.
   try{localStorage.setItem(cacheKey,JSON.stringify({bank,curriculum,syntaxSource}));}catch{}
    bank.practice_items=validateLessonPractice(makeLessonPractice(curriculum,syntaxSource,{onStale:recordStale,allowMissingSyntax:true}),curriculum);
    bank.assessment_items=validateAssessmentItems(makeAssessmentItems(bank.practice_items,curriculum),curriculum);
    bank.mixed_items=validateMixedItems([...syntaxMixedItems,...cambridgeMixedItems],curriculum);
  return staleWarning;
 }catch(error){
  try{
   const cached=JSON.parse(localStorage.getItem(cacheKey));
   const nextBank=validateBank(cached.bank);
   if(cached.curriculum?.length!==2||!cached.curriculum.every(t=>t.chapters?.length&&t.chapters.every(c=>c.topics?.length)))throw error;
     bank=nextBank;curriculum=applyQuizScope(cached.curriculum);
     bank.practice_items=validateLessonPractice(makeLessonPractice(curriculum,cached.syntaxSource,{onStale:recordStale,allowMissingSyntax:true}),curriculum);
     bank.assessment_items=validateAssessmentItems(makeAssessmentItems(bank.practice_items,curriculum),curriculum);
     bank.mixed_items=validateMixedItems([...syntaxMixedItems,...cambridgeMixedItems],curriculum);
     return [staleWarning,'Offline content: using the last successfully downloaded curriculum and question sources.'].filter(Boolean).join(' ');
  }catch{throw error;}
 }
}
function catalog(){
 curriculumCatalog();
 const sheet=host.querySelector('.quiz-tab-sheet')||host;
 const history=el('details',undefined,'quiz-history');history.append(el('summary','Attempt history'));const list=el('div',undefined,'quiz-history-list');
 for(const t of Object.values(store.attempts).filter(t=>t.submitted_at || store.isArchived(t)).sort((a,b)=>(b.submitted_at||b.started_at).localeCompare(a.submitted_at||a.started_at))){
  if (store.isArchived(t)) {
   const score = Number.isInteger(t.correct) ? ` · ${t.correct}/${t.presented?.length||5} recorded` : '';
   list.append(el('p', `${t.assessment_id} · archived${score}`,'quiz-history-archived'));
   continue;
  }
  const grade=gradeAttempt(bank,t);
  const row=el('div',undefined,'quiz-history-row');
  const title=t.title||(t.practice?'Reinforcement':assessmentFor(t)?.title||t.assessment_id);
  row.append(button(`${title} · ${grade.correct}/${t.presented.length} (${Math.round(100*grade.correct/t.presented.length)}%)`,()=>{current=t.attempt_id;message='';render();}));
  list.append(row);
 }
 if(!list.childElementCount)list.append(el('p','No completed quiz attempts yet.','quiz-card-status'));
 history.append(list);sheet.append(history);
}
function review(t){
 const grade=reviewForLearner(bank,t),a=assessmentFor(t),total=t.presented.length,pct=Math.round(100*grade.correct/total);
 const header=el('header',undefined,'view-header curriculum-header');
 const titleGroup=el('div',undefined,'view-header-title-group');
 titleGroup.append(iconButton('All quizzes',BACK_ARROW_SVG,()=>{current=null;message='';render();}));
 const titleRow=el('div',undefined,'quiz-header-side-by-side');
 titleRow.append(el('h1',t.title||a?.title||'Quiz','view-title'));
 titleGroup.append(titleRow);
 header.append(titleGroup);
 host.append(header);

 const body=el('div',undefined,'quiz-review-body');
 inlineNotice(body);
 const shell=el('div',undefined,'quiz-review-shell');
 const summaryCard=el('section',undefined,'quiz-results-summary');
 summaryCard.append(el('p',`${grade.correct}/${total} correct (${pct}%)`,'quiz-score'));
 const metaParts=[];
 if(t.spec?.format==='mixed'){
  metaParts.push('Interactive mixed-format · 0 verified XP (server XP verifies MCQ items only)');
 }else if(t.includes_unreviewed&&t.practice){
  metaParts.push('Practice attempt');
 }else if(!t.practice){
  const summaryTarget=a||{assessment_id:t.assessment_id,content_version:t.content_version};
  const s=store.summary(summaryTarget);
  const signedIn=Boolean(config.userId?.());
  const attemptXp=Number.isFinite(t.server_awarded)?t.server_awarded:(lastEarned?.attempt_id===t.attempt_id?lastEarned.earned:null);
  if(s.attempt_count>1&&s.best_score>grade.correct)metaParts.push(`Best ${s.best_score}/${total}`);
  if(attemptXp!==null){
   metaParts.push(`${attemptXp>0?`+${attemptXp}`:'0'} ${signedIn&&t.synced?'verified XP':signedIn?'XP (pending sync)':'XP earned (local)'}`);
  }else{
   metaParts.push(`${s.xp_awarded}/${2*total} ${signedIn&&t.synced?'verified XP':'XP (local)'}`);
  }
 }
 if(metaParts.length)summaryCard.append(el('p',metaParts.join(' · '),'quiz-results-stats'));
 shell.append(summaryCard);

 const reviewItems=itemsFor(bank,t);
 const needs=grade.results.filter(r=>!r.correct);
 const missedSectionsByLesson=new Map();
 for(const [idx,item] of reviewItems.entries()){
  if(grade.results[idx]?.correct||!item.lesson_id)continue;
  const parsed=parseLessonRef(item.lesson_reference);
  const sec=parsed?.section||null;
  const set=missedSectionsByLesson.get(item.lesson_id)||new Set();
  if(sec)set.add(sec);
  missedSectionsByLesson.set(item.lesson_id,set);
 }
 const missedLessons=[...missedSectionsByLesson.keys()];
 const consolidatedLessons=new Set();
 if(needs.length&&missedLessons.length){
  const next=el('section',undefined,'quiz-next');
  const openTarget=lid=>{
   const secs=[...(missedSectionsByLesson.get(lid)||[])];
   config.onLesson?.(lid,secs.length===1?{section:secs[0]}:undefined);
  };
  if(missedLessons.length===1){
   const lid=missedLessons[0];
   if((missedSectionsByLesson.get(lid)?.size||0)<=1)consolidatedLessons.add(lid);
   next.append(el('strong',`Review: ${lessonTitle(lid)}`,'quiz-next-title'));
   const revisitRow=el('div',undefined,'quiz-revisit-row');
   revisitRow.append(button('Open lesson',()=>openTarget(lid)));
   next.append(revisitRow);
  }else{
   next.append(el('strong','Review lessons','quiz-next-title'));
   const revisitRow=el('div',undefined,'quiz-revisit-row');
   for(const lid of missedLessons.slice(0,4)){
    if((missedSectionsByLesson.get(lid)?.size||0)<=1)consolidatedLessons.add(lid);
    revisitRow.append(button(lessonTitle(lid),()=>openTarget(lid)));
   }
   if(missedLessons.length>4)revisitRow.append(el('span',`+${missedLessons.length-4} more`,'quiz-card-status'));
   next.append(revisitRow);
  }
  shell.append(next);
 }

 const seenCardRefs=new Set();
 for(const [index,q] of reviewItems.entries()){
  const res=grade.results[index],response=t.responses[q.item_id]??null,correct=Boolean(res?.correct);
  const card=el('article',undefined,`quiz-review-card ${correct?'is-correct':'is-incorrect'}`);
  card.dataset.reviewItem=q.item_id;
  const titleRow=el('div',undefined,'quiz-review-title-row');
  const mark=el('span',correct?'✓':'✕',`quiz-status-mark ${correct?'is-correct':'is-incorrect'}`);
  mark.setAttribute('aria-hidden','true');
  const qHeading=el('h2',`${index+1}. ${q.prompt}`,'quiz-review-question');
  const srStatus=el('span',correct?' (Correct)':!isResponseProvided(q,response)?' (Unanswered)':' (Incorrect)','sr-only');
  qHeading.append(srStatus);
  titleRow.append(mark,qHeading);
  card.append(titleRow);
  if(q.stimulus?.sentence)card.append(el('p',q.stimulus.sentence,'lesson-example-sentence'));
  if(q.kind==='fill_blank'||q.kind==='grammar_correction'||q.kind==='sentence_reconstruction'){
   const answerLines=el('div',undefined,'quiz-review-answer-lines');
   const submittedText=q.kind==='sentence_reconstruction'
    ?(formatReconstructionAnswer(q,response)||'No answer')
    :(typeof response==='string'&&response.trim()?response.trim():'No answer');
   const verdictLine=el('p',undefined,'quiz-review-verdict');
   verdictLine.append(document.createTextNode(q.kind==='grammar_correction'?'Your correction: ':'Your answer: '),el('span',submittedText,correct?'quiz-answer-selected':'quiz-answer-wrong'));
   answerLines.append(verdictLine);
   if(!correct){
    const primary=q.display_answer||q.accepted_answers?.[0]||'';
    const alts=[...new Set((q.accepted_answers||[]).filter(a=>a&&a!==primary))];
    const corrLine=el('p',undefined,'quiz-review-correct');
    corrLine.append(document.createTextNode(q.kind==='grammar_correction'?'Accepted correction: ':'Accepted answer: '),el('span',primary,'quiz-answer-right'));
    if(alts.length)corrLine.append(document.createTextNode(` (also accepted: ${alts.join(' / ')})`));
    answerLines.append(corrLine);
   }
   card.append(answerLines);
   if(res?.reason)card.append(el('p',res.reason,'quiz-review-diff-note'));
  }else if(q.kind==='tree_builder'||q.kind==='syntax_correction'){
   const treeCols=el('div',undefined,'quiz-review-trees');
   const subCol=el('div',undefined,'quiz-review-tree-col');
   subCol.append(el('strong','Your submitted structure'));
   if(res?.evaluated_tree?.root){
    subCol.append(renderLessonTree(res.evaluated_tree,{zoomControls:false,stackFeatures:true}));
   }else{
    subCol.append(el('p',res?.reason||'No connected tree submitted.','quiz-review-diff-note'));
   }
   treeCols.append(subCol);
   if(!correct&&q.expected_tree?.root){
    const expCol=el('div',undefined,'quiz-review-tree-col');
    expCol.append(el('strong','Expected structure'));
    expCol.append(renderLessonTree(q.expected_tree,{zoomControls:false,stackFeatures:true}));
    treeCols.append(expCol);
   }
   card.append(treeCols);
   if(res?.reason&&res?.evaluated_tree?.root)card.append(el('p',res.reason,'quiz-review-diff-note'));
  }else{
   const selectedText=q.options.find(o=>o.id===response)?.text||'No answer';
   const correctText=q.options.find(o=>o.id===q.answer)?.text||'';
   const answerLines=el('div',undefined,'quiz-review-answer-lines');
   const verdictLine=el('p',undefined,'quiz-review-verdict');
   const ansSpan=el('span',selectedText,correct?'quiz-answer-selected':'quiz-answer-wrong');
   verdictLine.append(document.createTextNode('Your answer: '),ansSpan);
   answerLines.append(verdictLine);
   if(!correct&&correctText){
    const corrLine=el('p',undefined,'quiz-review-correct');
    corrLine.append(document.createTextNode('Correct answer: '),el('span',correctText,'quiz-answer-right'));
    answerLines.append(corrLine);
   }
   card.append(answerLines);
  }
  if(q.review_status!=='INDEPENDENTLY_REVIEWED'){
   card.append(el('p',q.rationale,'quiz-review-rationale'));
   if(!correct&&q.lesson_reference&&!consolidatedLessons.has(q.lesson_id)&&!seenCardRefs.has(q.lesson_reference)){
    seenCardRefs.add(q.lesson_reference);
    const parsed=parseLessonRef(q.lesson_reference);
    const label=subtopicTitle(parsed?.lessonId||q.lesson_id,parsed?.section);
    const link=el('a',label?`Lesson: ${label}`:'Lesson section','quiz-lesson-link');
    link.href=q.lesson_reference;
    link.addEventListener('click',e=>{
     if(e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;
     e.preventDefault();
     config.onLesson?.(parsed?.lessonId||q.lesson_id,parsed?.section?{section:parsed.section}:undefined);
    });
    card.append(link);
   }
  }else{
   renderEvidence(composeQuizEvidence(q,response,bank),card);
  }
  if(q.answer_tree){
    const details=el('details');
    details.dataset.xai7QuizTree = '';
    const inspector=el('div',undefined,'quiz-tree-inspector');
    inspector.dataset.xai7QuizInspector = '';
    let version=0;
    let treeView;
    const choose=async (nodeId, feature=null)=>{
      details.open=true;
      const requestId=++version;
      inspector.replaceChildren(el('p','Explaining this word or phrase…'));
      try{
        const evidence=await requestEvidence(q.answer_tree,nodeId);
        if(requestId!==version||token!==generation||!card.isConnected)return;
        renderEvidence(evidence,inspector,{treeRoot:treeView,feature});
      }catch{
        if(requestId===version&&card.isConnected)
          inspector.replaceChildren(el('p','An explanation is not available for this part of the sentence.'));
      }
    };
    treeView=renderLessonTree(q.answer_tree,{interactive:true,zoomControls:true,stackFeatures:true,onSelectNode:choose});
    details.append(el('summary','Explore the answer tree'),treeView,inspector);
    card.append(details);
  }
    if(q.review_status!=='INDEPENDENTLY_REVIEWED'){shell.append(card);continue;}
   const token=generation,controller=new AbortController(),timer=setTimeout(()=>controller.abort(),5000);
  requestQuizEvidence(q,response,{signal:controller.signal}).then(evidence=>{if(token===generation&&card.isConnected)renderEvidence(evidence,card);}).catch(()=>{}).finally(()=>clearTimeout(timer));
  shell.append(card);
 }
 const reviewActions=el('div',undefined,'quiz-review-actions');
 if(t.quiz_v2)reviewActions.append(button('Try a new attempt',()=>action(()=>store.startV2(curriculum,t.spec)),'lesson-primary'));
 else if(!t.practice)reviewActions.append(button('Try a new attempt',()=>action(()=>store.start(a)),'lesson-primary'));
 reviewActions.append(button('Back to quiz selection',()=>{current=null;render();}));
 shell.append(reviewActions);
 body.append(shell);
 host.append(body);
}
function attemptScreen(t){
 const a=assessmentFor(t),allItems=itemsFor(bank,t),q=questionForLearner(bank,t),fullQ=allItems[t.position],ref=t.presented[t.position],count=t.presented.length;
 const header=el('header',undefined,'view-header curriculum-header');
 const titleGroup=el('div',undefined,'view-header-title-group');
 titleGroup.append(iconButton('All quizzes',BACK_ARROW_SVG,()=>{current=null;pendingConfirmAttempt=null;message='';render();}));
 titleGroup.append(el('h1',t.title||a?.title||'Quiz','view-title'));
 header.append(titleGroup);
 host.append(header);

 const body=el('div',undefined,'quiz-attempt-body');
 inlineNotice(body);
 const layout=el('div',undefined,'quiz-attempt-layout');
 const main=el('div',undefined,'quiz-attempt-main');
 const isBuilderQ=q.kind==='tree_builder'||q.kind==='syntax_correction';
 const panel=el('section',undefined,`quiz-question${isBuilderQ?' is-builder-question':''}`);
 panel.dataset.quizItem=q.item_id;
 panel.dataset.quizKind=q.kind||'mcq';
 const panelBar=el('div',undefined,'quiz-question-bar');
 const numWrap=el('div',undefined,'quiz-question-title-wrap');
 numWrap.append(el('h2',`Question ${t.position+1} of ${count}`,'quiz-question-number'));
 if(KIND_LABELS[q.kind])numWrap.append(el('span',KIND_LABELS[q.kind],'quiz-format-badge'));
 panelBar.append(numWrap);
 const panelActions=el('div',undefined,'quiz-question-actions');
 panelBar.append(panelActions);
 panel.append(panelBar);

 const qContent=el('div',undefined,'quiz-question-content');
 if(q.stimulus)qContent.append(el('p',q.stimulus.sentence,'lesson-example-sentence'));

 const controls=el('div',undefined,'quiz-attempt-controls');
 const nav=el('nav',undefined,'lesson-step-controls');nav.setAttribute('aria-label','Question navigation');
 const back=iconButton('Previous question',PREV_ARROW_SVG,()=>action(()=>store.move(t.attempt_id,t.position-1)),'quiz-step-btn');back.disabled=t.position===0;
 const next=iconButton('Next question',NEXT_ARROW_SVG,()=>action(()=>store.move(t.attempt_id,t.position+1)),'quiz-step-btn');next.disabled=t.position===count-1;
 nav.append(back,next);
 controls.append(nav);

 const navigator=el('aside',undefined,'quiz-navigator');
 navigator.setAttribute('aria-label','Question navigator');
 const navHead=el('div',undefined,'quiz-nav-head');
 navHead.append(el('h2','Questions'));
 navigator.append(navHead);
 const questionList=el('ol',undefined,'quiz-nav-list');
 const navButtons=[];
 for(let i=0;i<count;i++){
  const row=el('li');
  const numBtn=button('',()=>action(()=>store.move(t.attempt_id,i)).then(()=>{
   host.querySelector('.quiz-nav-row[aria-current="step"]')?.focus();
  }),'quiz-nav-row');
  numBtn.append(el('span',String(i+1),'quiz-nav-number'),el('span','','quiz-nav-state'));
  if(i===t.position)numBtn.setAttribute('aria-current','step');
  row.append(numBtn);questionList.append(row);
  navButtons.push(numBtn);
 }
 navigator.append(questionList);

 let onClearCurrent=()=>action(()=>store.clearAnswer(t.attempt_id,q.item_id)),mountBuilderNow=null;
 let submitBtn=null;
 let draftResponses={...(store.attempts[t.attempt_id]?.responses||t.responses||{})};
 const syncChrome=()=>{
  const live=store.attempts[t.attempt_id]||t;
  const responses={...(live.responses||{}),...draftResponses};
  let answered=0;
  for(let i=0;i<count;i++){
   const item=allItems[i];
   const ok=isResponseProvided(item,responses[item.item_id]);
   if(ok)answered++;
   const btn=navButtons[i];
   const isCurrent=i===t.position;
   btn.className=`quiz-nav-row${isCurrent?' is-current':''}${ok?' is-answered':''}`;
   btn.querySelector('.quiz-nav-state').textContent=[isCurrent?'Current':null,ok?'Answered':!isCurrent?'Unanswered':null].filter(Boolean).join(' · ');
   btn.setAttribute('aria-label',`Question ${i+1}, ${[isCurrent?'current':null,ok?'answered':'unanswered'].filter(Boolean).join(', ')}`);
  }
  const curVal=responses[q.item_id];
  const hasCurrent=curVal!==undefined&&curVal!==null&&(typeof curVal!=='string'||curVal.trim().length>0)&&(!Array.isArray(curVal)||curVal.length>0);
  panelActions.replaceChildren();
  if(hasCurrent){
   panelActions.append(button(isMixedKind(q.kind)?'Clear answer':'Clear choice',()=>onClearCurrent(),'quiz-clear-btn'));
  }
  const allDone=answered===count;
  if(allDone&&!submitBtn){
   submitBtn=button('Submit',()=>{
    flushTextDraft?.();
    const fresh=store.attempts[t.attempt_id];
    if(!fresh||allItems.some(item=>!isResponseProvided(item,fresh.responses?.[item.item_id]))){
     draftResponses={...(fresh?.responses||draftResponses)};
     syncChrome();return;
    }
    action(()=>store.submit(t.attempt_id,{requireComplete:true}));
   },'lesson-primary');
   controls.append(submitBtn);
  }else if(!allDone&&submitBtn){
   submitBtn.remove();
   submitBtn=null;
  }
 };

 let saveTimer=null;
 const setDraftResponse=value=>{
  draftResponses={...draftResponses,[q.item_id]:value};
  t.responses=draftResponses;
 };
 const quietSave=(value)=>{
  setDraftResponse(value);
  clearTimeout(saveTimer);
  const persist=()=>{
   clearTimeout(saveTimer);saveTimer=null;
   flushTextDraft=null;
   if(value===null||value===undefined||(typeof value==='string'&&value==='')){
    store.clearAnswer(t.attempt_id,q.item_id).catch(()=>{});
   }else{
    store.answer(t.attempt_id,q.item_id,value).catch(()=>{});
   }
  };
  flushTextDraft=persist;
  saveTimer=setTimeout(persist,150);
  syncChrome();
 };

 if(q.kind==='fill_blank'){
  qContent.append(el('p',q.prompt,'quiz-prompt-text'));
  const wrap=el('div',undefined,'quiz-text-wrap');
  const lbl=el('label','Your answer','quiz-text-label');
  const inp=document.createElement('input');
  inp.type='text';inp.className='quiz-text-input';
  inp.placeholder='Type the missing word or phrase…';
  inp.autocomplete='off';inp.spellcheck=false;
  inp.value=typeof t.responses[q.item_id]==='string'?t.responses[q.item_id]:'';
  inp.addEventListener('input',()=>quietSave(inp.value));
  inp.addEventListener('blur',()=>flushTextDraft?.());
  lbl.append(inp);
  wrap.append(lbl);
  qContent.append(wrap);
  onClearCurrent=()=>{inp.value='';flushTextDraft=null;clearTimeout(saveTimer);setDraftResponse(null);syncChrome();action(()=>store.clearAnswer(t.attempt_id,q.item_id));};
 }else if(q.kind==='grammar_correction'){
  qContent.append(el('p',q.prompt,'quiz-prompt-text'));
  const wrap=el('div',undefined,'quiz-text-wrap');
  const lbl=el('label','Corrected sentence','quiz-text-label');
  const area=document.createElement('textarea');
  area.className='quiz-textarea';area.rows=3;
  area.placeholder='Write the corrected sentence…';
  area.spellcheck=false;
  area.value=typeof t.responses[q.item_id]==='string'?t.responses[q.item_id]:'';
  area.addEventListener('input',()=>quietSave(area.value));
  area.addEventListener('blur',()=>flushTextDraft?.());
  lbl.append(area);
  wrap.append(lbl);
  qContent.append(wrap);
  onClearCurrent=()=>{area.value='';flushTextDraft=null;clearTimeout(saveTimer);setDraftResponse(null);syncChrome();action(()=>store.clearAnswer(t.attempt_id,q.item_id));};
 }else if(q.kind==='sentence_reconstruction'){
  qContent.append(el('p',q.prompt,'quiz-prompt-text'));
  const reconBox=el('div',undefined,'quiz-recon-section');
  let order=Array.isArray(t.responses[q.item_id])?[...t.responses[q.item_id]]:[];
  let dragPos=null;
  const updateRecon=nextOrder=>{
   order=nextOrder;
   setDraftResponse(order.length?[...order]:null);
   renderRecon();
   syncChrome();
   if(order.length)store.answer(t.attempt_id,q.item_id,order).catch(()=>{});
   else store.clearAnswer(t.attempt_id,q.item_id).catch(()=>{});
  };
  const renderRecon=()=>{
   reconBox.replaceChildren();
   const trayLabel=el('p','Your reconstructed sentence','quiz-recon-label');
   const tray=el('div',undefined,'quiz-recon-tray');
   tray.setAttribute('role','region');tray.setAttribute('aria-label','Your reconstructed sentence');
   if(!order.length){
    tray.append(el('span','Select or drag components below in order…','quiz-recon-placeholder'));
   }else{
    for(const [pos,tokIdx] of order.entries()){
     const chip=el('div',undefined,'quiz-recon-chip');
     chip.draggable=true;
     chip.dataset.tokenIdx=String(tokIdx);
     chip.addEventListener('dragstart',()=>{dragPos=pos;chip.classList.add('is-dragging');});
     chip.addEventListener('dragend',()=>{dragPos=null;chip.classList.remove('is-dragging');});
     chip.addEventListener('dragover',e=>e.preventDefault());
     chip.addEventListener('drop',e=>{
      e.preventDefault();
      if(dragPos===null||dragPos===pos)return;
      const nextOrd=[...order];
      const [moved]=nextOrd.splice(dragPos,1);
      nextOrd.splice(pos,0,moved);
      updateRecon(nextOrd);
     });
     chip.append(el('span',q.tokens[tokIdx],'quiz-recon-token'));
     const actRow=el('span',undefined,'quiz-recon-chip-actions');
     if(pos>0){
      const leftB=button('←',()=>{const n=[...order];[n[pos-1],n[pos]]=[n[pos],n[pos-1]];updateRecon(n);},'quiz-recon-move');
      leftB.setAttribute('aria-label',`Move “${q.tokens[tokIdx]}” left`);
      actRow.append(leftB);
     }
     if(pos<order.length-1){
      const rightB=button('→',()=>{const n=[...order];[n[pos+1],n[pos]]=[n[pos],n[pos+1]];updateRecon(n);},'quiz-recon-move');
      rightB.setAttribute('aria-label',`Move “${q.tokens[tokIdx]}” right`);
      actRow.append(rightB);
     }
     const remB=button('×',()=>updateRecon(order.filter((_,i)=>i!==pos)),'quiz-recon-remove');
     remB.setAttribute('aria-label',`Remove “${q.tokens[tokIdx]}”`);
     actRow.append(remB);
     chip.append(actRow);
     tray.append(chip);
    }
   }
   const poolLabel=el('p','Available words / constituents','quiz-recon-label');
   const pool=el('div',undefined,'quiz-recon-pool');
   pool.setAttribute('role','group');pool.setAttribute('aria-label','Available words or constituents');
   const remaining=(q.token_order||q.tokens.map((_,i)=>i)).filter(idx=>!order.includes(idx));
   if(!remaining.length){
    pool.append(el('span','All components placed.','quiz-recon-placeholder'));
   }else{
    for(const tokIdx of remaining){
     const btn=button(q.tokens[tokIdx],()=>updateRecon([...order,tokIdx]),'quiz-recon-avail');
     btn.dataset.tokenIdx=String(tokIdx);
     pool.append(btn);
    }
   }
   reconBox.append(trayLabel,tray,poolLabel,pool);
  };
  renderRecon();
  qContent.append(reconBox);
  onClearCurrent=()=>updateRecon([]);
 }else if(isBuilderQ){
  qContent.append(el('p',q.prompt,'quiz-prompt-text'));
  if(typeof config.mountBuilder==='function'){
   const wrap=el('div',undefined,'quiz-builder-wrap');
   const toolbar=el('div',undefined,'first-tree-toolbar quiz-builder-toolbar');
   const ws=el('div',undefined,'first-tree-workspace quiz-builder-workspace');
   const stage=el('div',undefined,'first-tree-stage');
   const palette=el('aside',undefined,'first-tree-palette');
   palette.setAttribute('aria-label','Add a node');
   const paletteHead=el('div',undefined,'first-tree-palette-head');
   paletteHead.append(el('h4','Add a node'));
   const paletteList=el('div',undefined,'first-tree-palette-list');
   let editor=null;
   const paletteToggle=button('Hide',()=>{
    const collapsed=palette.classList.toggle('is-collapsed');
    paletteList.hidden=collapsed;
    paletteToggle.textContent=collapsed?'Show':'Hide';
    paletteToggle.setAttribute('aria-expanded',String(!collapsed));
    ws.classList.toggle('is-palette-collapsed',collapsed);
    editor?.fit?.();
   },'first-tree-palette-toggle');
   paletteToggle.setAttribute('aria-expanded','true');
   paletteHead.append(paletteToggle);
   palette.append(paletteHead,paletteList);
   ws.append(stage,palette);
   const leftGrp=el('div',undefined,'first-tree-help');
   const resetBtn=button('Reset starting tree',()=>{
    editor?.restart?.();
    flushTextDraft=null;clearTimeout(saveTimer);
    setDraftResponse(null);
    syncChrome();
    store.clearAnswer(t.attempt_id,q.item_id).catch(()=>{});
   });
   leftGrp.append(resetBtn);
   const ctrlGrp=el('div',undefined,'first-tree-controls');
   ctrlGrp.append(
    button('↶',()=>editor?.undo?.(),'first-tree-undo'),
    button('−',()=>editor?.zoom?.(0.8),'first-tree-zoom-btn'),
    button('+',()=>editor?.zoom?.(1.25),'first-tree-zoom-btn'),
    button('Fit',()=>editor?.fit?.(),'first-tree-fit-btn'),
   );
   toolbar.append(leftGrp,ctrlGrp);
   wrap.append(toolbar,ws);
   qContent.append(wrap);
   const exercise={
    id:`quiz:${t.attempt_id}:${q.item_id}`,
    profile:q.profile,
    labels:q.labels,
    seed:()=>{
     const saved=t.responses?.[q.item_id];
     if(saved?.model?.nodes)return JSON.parse(JSON.stringify(saved.model));
     if(q.seed_tree)return fromCanonicalEnvelope(q.seed_tree);
     const m=createModel();
     addWordsFromText(m,q.seed_tokens||'',24,210);
     return m;
    },
    onChange:model=>{
     quietSave({schema:'builder-tree-1',touched:true,model:JSON.parse(JSON.stringify(model))});
    },
   };
   mountBuilderNow=()=>{
    editor=config.mountBuilder(stage,exercise);
    for(const nodeLabel of (q.labels||editor.labels?.()||[])){
     const addBtn=button(nodeLabel,()=>editor.addNode?.(nodeLabel),'first-tree-node-btn');
     addBtn.dataset.nodeLabel=nodeLabel;
     addBtn.setAttribute('aria-label',`Add ${nodeLabel} node`);
     paletteList.append(addBtn);
    }
    if(typeof window!=='undefined'&&window.innerWidth<=760){
     palette.classList.add('is-collapsed');paletteList.hidden=true;paletteToggle.textContent='Show';paletteToggle.setAttribute('aria-expanded','false');ws.classList.add('is-palette-collapsed');
    }
    editor?.fit?.();
    quizBuilderCleanup=()=>{try{editor?.destroy?.();}catch{}quizBuilderCleanup=null;};
   };
   onClearCurrent=()=>resetBtn.click();
  }else{
   qContent.append(el('p','Interactive tree builder is unavailable in this environment.','quiz-card-error'));
  }
 }else{
  const field=el('fieldset');field.append(el('legend',q.prompt));const choices=el('div',undefined,q.kind==='tree_choice'?'quiz-tree-options':'quiz-options');
  for(const id of ref.option_order){const option=q.options.find(o=>o.id===id),label=el('label',undefined,'lesson-option'),radio=el('input');radio.type='radio';radio.name=q.item_id;radio.value=id;radio.checked=t.responses[q.item_id]===id;
   radio.addEventListener('change',()=>action(()=>store.answer(t.attempt_id,q.item_id,id)));label.append(radio,el('span',option.text));
   const group=el('div',undefined,'quiz-choice');group.append(label);if(option.diagram){const diagram=renderLessonTree(option.diagram);diagram.classList.add('quiz-candidate');diagram.querySelector('svg')?.setAttribute('aria-label',`Candidate ${id}: ${option.text}`);group.append(diagram);}choices.append(group);
  }
  field.append(choices);qContent.append(field);
 }

 panel.append(qContent);
 syncChrome();
 panel.append(controls);
 main.append(panel);

 layout.append(main,navigator);
 body.append(layout);
 host.append(body);
 // Keep the active entry visible after Previous/Next or draft restoration without
 // scrolling the assessment page down to the navigator on small screens.
 const activeBounds=navButtons[t.position].getBoundingClientRect(),listBounds=questionList.getBoundingClientRect();
 if(activeBounds.bottom>listBounds.bottom)questionList.scrollTop+=activeBounds.bottom-listBounds.bottom+3;
 mountBuilderNow?.();
}
function render(){
 if(!host||host.hidden||!store||!bank)return;const scroll=host.scrollTop;
 cleanupActiveQuestion();
 host.replaceChildren();
 if(current){
  const t=store.attempts[current];
  if(!t){current=null;catalog();}
  else if(store.isArchived(t)){current=null;message='This assessment version is archived. Your attempt was retained.';catalog();}
  else if(t.submitted_at)review(t);
  else attemptScreen(t);
 }else catalog();
 host.scrollTop=scroll;
}
export function initQuizzes(options={}){
 config=options;host=el('section',undefined,'curriculum-view quiz-view');host.id='quizzesView';host.hidden=true;host.setAttribute('aria-label','Independent quizzes');document.body.append(host);
 subscribeAuthState(()=>{generation++;store=null;current=null;busy=false;if(!host.hidden)openQuizzes();});
 const route=()=>{const match=/^#quiz\/([a-z0-9-]+)$/.exec(location.hash);if(match)config.onNavigate?.(match[1]);};window.addEventListener('hashchange',route);if(/^#quiz\//.test(location.hash))queueMicrotask(route);
}
export async function openQuizzes(id=null){
 cleanupActiveQuestion();
 host.hidden=false;host.setAttribute('aria-busy','false');document.body.classList.add('curriculum-open','quizzes-open');const token=++generation;
  showCurriculumState(host, { message: 'Loading quizzes…' });
 try{
   const contentNotice=await loadContent();
  if(!store){let storage;try{storage=localStorage;}catch{storage=null;}const next=createQuizStore(bank,{storage,userId:config.userId?.()||'guest',client:config.client?.()});await next.load();if(token!==generation)return;store=next;}
   if(token!==generation)return;current=null;message=contentNotice;busy=false;
  host.setAttribute('aria-busy','false');render();
  const heading = host.querySelector('h1');
  if (heading) {
    heading.tabIndex = -1;
    heading.focus({ preventScroll: true });
  }
  if(id){const a=bank.assessments.find(a=>a.assessment_id===id);if(a)await action(()=>store.draft(a)||store.start(a));}
  host.scrollTop=0;document.querySelector('#appSidebarBackdrop')?.classList.remove('active');
 } catch {
   if (token === generation) showCurriculumState(host, {
     title: 'Assessments unavailable',
     message: 'The bank could not be loaded or its source review is incomplete.',
     retry: () => openQuizzes(id), back: config.onExit,
   });
 }
}
export function closeQuizzes(){cleanupActiveQuestion();generation++;busy=false;current=null;pendingConfirmAttempt=null;if(host){host.hidden=true;host.replaceChildren();}document.body.classList.remove('quizzes-open','curriculum-open');}
