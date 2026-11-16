import { showCurriculumState } from './curriculum-state.js';
import {validateBank,quizKey,itemsFor,gradeAttempt,questionForLearner,reviewForLearner,MAX_QUIZ_ITEMS} from './quiz-core.js';
import {createQuizStore} from './quiz-progress.js';
import {composeQuizEvidence,requestQuizEvidence,requestEvidence,renderEvidence} from './explanation-evidence.js';
import {renderLessonTree} from './lessons-ui.js';
import {subscribeAuthState} from './auth.js';
import {loadActiveCourse,quizCurriculum} from './lesson-curriculum.js';
import {selectQuestions,specKey,eligibleQuestions,publishedBlueprint,questionMetadata,topicPerformance,MAX_MASTER_QUIZ_ITEMS,DEFAULT_MASTER_QUIZ_ITEMS} from './quiz-v2.js';
import {makeLessonPractice,validateLessonPractice} from './quiz-lesson-practice.js';
import {makeAssessmentItems,validateAssessmentItems} from './quiz-assessment-items.js';
import {applyQuizScope} from './quiz-scope.js';
let host,config={},bank,store,curriculum,current=null,trackId='syntax',busy=false,message='',generation=0,pendingConfirmAttempt=null;
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const button=(text,fn,cls='')=>{const b=el('button',text,cls);b.type='button';b.addEventListener('click',fn);return b;};
function iconButton(label,svg,fn,cls='header-icon-btn'){
 const b=button('',fn,cls);
 b.setAttribute('aria-label',label);
 b.title=label;
 b.innerHTML=svg;
 return b;
}
const BACK_ARROW_SVG='<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5"/><path d="m12 19-7-7 7-7"/></svg>';
const PREV_ARROW_SVG='<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>';
const NEXT_ARROW_SVG='<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>';
const FLAG_SVG='<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/></svg>';
const shortDate=new Intl.DateTimeFormat(undefined,{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'});
const shortDateSeconds=new Intl.DateTimeFormat(undefined,{month:'short',day:'numeric',hour:'numeric',minute:'2-digit',second:'2-digit'});
const plural=(n,word)=>`${n} ${n===1?word:word+'s'}`;
const answeredCount=t=>t.presented.filter(q=>t.responses?.[q.item_id]!==undefined&&t.responses?.[q.item_id]!==null).length;
const trackTabLabel=track=>track.id==='cambridge'?'Grammar':track.title;
function assessmentFor(t){return bank.assessments.find(a=>quizKey(a)===quizKey(t));}
async function action(fn){
 if(busy)return;const token=generation,focusName=document.activeElement?.name,focusValue=document.activeElement?.value;busy=true;pendingConfirmAttempt=null;host.setAttribute('aria-busy','true');host.querySelectorAll('button,input').forEach(n=>{n.disabled=true;});
 try{const result=await fn();if(token!==generation)return;
  if(result?.attempt_id)current=result.attempt_id;
  if(result&&Object.hasOwn(result,'earned'))window.dispatchEvent(new Event('syntutor:quiz-progress'));
  message=result&&Object.hasOwn(result,'earned')?(store.attempts[result.attempt_id]?.practice?`Quiz submitted. Score: ${result.grade.correct}/${result.grade.results.length}.`:`${result.earned} new quiz XP earned.`):'';
 }catch(e){if(token===generation)message=e.message;}
 finally{if(token===generation){busy=false;host.setAttribute('aria-busy','false');render();if(focusName)host.querySelector(`input[name="${CSS.escape(focusName)}"][value="${focusValue}"]`)?.focus();}}
}
function footer(){
 const signedIn=Boolean(config.userId?.());
 const syncFailed=signedIn&&store.status!=='Synced to your account';
 if(!message&&!signedIn)return;
 const f=el('footer',undefined,'lesson-save-status');
 f.setAttribute('aria-live','polite');
 if(message)f.append(el('p',message));
 if(signedIn&&(!message||syncFailed)){
  f.append(el('p',store.status));
 }
 if(syncFailed)f.append(button('Retry account sync',()=>action(()=>store.retry())));
 host.append(f);
}
function attemptHistorySummary(assessment){
 const previous=Object.values(store.attempts).filter(t=>quizKey(t)===quizKey(assessment)&&t.submitted_at&&!store.isArchived(t)).sort((a,b)=>a.submitted_at.localeCompare(b.submitted_at));
 if(!previous.length)return null;
 const last=previous.at(-1),best=Math.max(...previous.map(t=>gradeAttempt(bank,t).correct/t.presented.length));
 return `Best ${Math.round(best*100)}% · Last ${gradeAttempt(bank,last).correct}/${last.presented.length} · ${plural(previous.length,'attempt')}`;
}
function xpMeter(awarded,maxXp){
 if(!awarded||awarded<=0||!maxXp)return null;
 const wrap=el('div',undefined,'quiz-xp-meter');
 const bar=el('progress');bar.value=Math.min(awarded,maxXp);bar.max=maxXp;bar.setAttribute('aria-label',`${awarded} of ${maxXp} XP earned`);
 wrap.append(bar,el('span',`${awarded}/${maxXp} XP`,'quiz-xp-label'));
 return wrap;
}
function v2Card(parent,title,spec,opts={}){
 const published=publishedBlueprint(bank,curriculum,spec);
 const activeSpec=published?spec:{...spec,content_tier:'lesson-assessment',format:'formal'};
 const isPersonalized=spec.mode==='personalized';
 const isGeneral=spec.mode==='general';
 const card=el('article',undefined,`curriculum-card quiz-topic-card${opts.featured?' quiz-featured-card':''}${isGeneral?' is-general':''}`);
 let reason='',selection;
 try{selection=selectQuestions(bank,curriculum,activeSpec,store.attempts,0);}catch(e){reason=e.message;}
 const assessment=published||{assessment_id:specKey(activeSpec),content_version:'2.0.0'},draft=store.draft(assessment);
 const headRow=el('div',undefined,'quiz-card-head');
 headRow.append(el('h3',title));
 if(!reason)headRow.append(el('span',`${selection.items.length} questions`,'quiz-card-count'));
 card.append(headRow);
 if(isPersonalized&&!reason){
  const perf=topicPerformance(bank,curriculum,store.attempts,spec.track);
  const desc=selection.diagnostic
   ?'Builds a short baseline across chapters. Complete 5 questions in this track so future quizzes can target weaker concepts.'
   :perf.missed.size>0
    ?'Prioritizes weaker grammatical concepts from your previous results and excludes questions you missed.'
    :'Adapts to your completed quiz history and selects unseen questions across topics.';
  card.append(el('p',desc,'quiz-card-desc'));
 }
 const statusText=reason
  ?reason
  :draft
   ?`In progress · ${answeredCount(draft)} of ${draft.presented.length} answered`
   :(attemptHistorySummary(assessment)||'Not started');
 card.append(el('p',statusText,reason?'quiz-card-error':'quiz-card-status'));
 const cardFoot=el('div',undefined,'quiz-card-footer');
 if(!reason){
  const meter=xpMeter(store.summary(assessment).xp_awarded,2*selection.items.length);
  if(meter)cardFoot.append(meter);
 }
 const start=button(draft?'Resume quiz':reason?'Quiz unavailable':'Start quiz',()=>action(()=>draft||store.startV2(curriculum,activeSpec)),'lesson-primary');
 start.disabled=!!reason&&!draft;
 cardFoot.append(start);
 card.append(cardFoot);
 parent.append(card);
}
function unfinishedSection(body){
 const unfinished=Object.values(store.attempts).filter(t=>!t.submitted_at&&!store.isArchived(t)).sort((a,b)=>b.started_at.localeCompare(a.started_at));
 if(!unfinished.length)return;
 const details=el('details',undefined,'quiz-unfinished-details');
 details.open=true;
 details.append(el('summary',`Resume unfinished quizzes (${unfinished.length})`));
 const minuteKeys=new Map();
 for(const t of unfinished){
  const title=t.title||assessmentFor(t)?.title||'Quiz';
  const minKey=`${title}:${t.started_at?shortDate.format(new Date(t.started_at)):''}`;
  minuteKeys.set(minKey,(minuteKeys.get(minKey)||0)+1);
 }
 const list=el('div',undefined,'quiz-unfinished-list');
 for(const t of unfinished){
  const title=t.title||assessmentFor(t)?.title||'Quiz';
  const total=t.presented.length,answered=answeredCount(t),pos=Math.min(total,(t.position||0)+1);
  const minKey=`${title}:${t.started_at?shortDate.format(new Date(t.started_at)):''}`;
  const fmt=minuteKeys.get(minKey)>1?shortDateSeconds:shortDate;
  const startedLabel=t.started_at?fmt.format(new Date(t.started_at)):'';
  const row=el('div',undefined,'quiz-unfinished-row');
  const info=el('div',undefined,'quiz-unfinished-info');
  info.append(el('strong',title));
  info.append(el('span',`${answered} of ${total} answered · Question ${pos} of ${total}${startedLabel?` · Started ${startedLabel}`:''}`,'quiz-unfinished-meta'));
  const resumeBtn=button('Resume',()=>{current=t.attempt_id;message='';render();},'lesson-primary');
  resumeBtn.setAttribute('aria-label',`Resume ${title} (${answered} of ${total} answered, Question ${pos} of ${total})`);
  row.append(info,resumeBtn);
  list.append(row);
 }
 details.append(list);
 body.append(details);
}
function masterQuizCard(parent,track){
 const master=el('section',undefined,'curriculum-card quiz-practice quiz-featured-card');
 const min=track.chapters.length,masterTier='lesson-assessment';
 const available=new Set(eligibleQuestions(bank,curriculum,trackId,masterTier).map(q=>q.item_id)).size,max=Math.min(MAX_MASTER_QUIZ_ITEMS,available);
 const defaultCount=max>=min?Math.min(Math.max(DEFAULT_MASTER_QUIZ_ITEMS,min),max):min;
 const initialCount=masterCounts[trackId]>=min&&masterCounts[trackId]<=max?masterCounts[trackId]:defaultCount;
 const headRow=el('div',undefined,'quiz-card-head');
 headRow.append(el('h2',`${track.title} Master Quiz`),el('span',max>=min?`${min}–${max} questions`:'Unavailable','quiz-card-count'));
 master.append(headRow);
 master.append(el('p',`Covers every chapter in ${track.title} with at least one question per chapter.`,'quiz-card-desc'));
 const controlRow=el('div',undefined,'quiz-master-control');
 const label=el('label','Questions ');
 const input=el('input');
 input.type='number';input.min=String(min);input.max=String(max);input.step='1';
 input.value=String(initialCount);input.disabled=max<min;
 input.setAttribute('aria-label',`${track.title} Master Quiz question count`);
 label.append(input);
 controlRow.append(label,el('span',`Minimum ${min} · Maximum ${max}`,'quiz-master-hint'));
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
  const spec={track:trackId,mode:'master',count:Number(input.value),content_tier:masterTier};
  const assessment={assessment_id:specKey(spec),content_version:'2.0.0'},draft=store.draft(assessment);
  const statusLine=draft?`In progress · ${answeredCount(draft)} of ${draft.presented.length} answered`:(attemptHistorySummary(assessment)||'Ready');
  target.append(el('p',statusLine,'quiz-card-status'));
  const foot=el('div',undefined,'quiz-card-footer');
  const meter=xpMeter(store.summary(assessment).xp_awarded,2*Number(input.value));
  if(meter)foot.append(meter);
  foot.append(button(draft?'Resume quiz':'Start quiz',()=>action(()=>draft||store.startV2(curriculum,spec)),'lesson-primary'));
  target.append(foot);
 };
 input.addEventListener('input',update);update();
 master.append(target);
 parent.append(master);
}
function curriculumCatalog(){
 const header=el('header',undefined,'view-header curriculum-header');
 header.append(el('h1','Assess your understanding.','view-title'));
 host.append(header);

 const body=el('div',undefined,'quiz-catalog-body');
 const folder=el('div',undefined,'quiz-folder-panel');
 const nav=el('div',undefined,'lesson-track-tabs');nav.setAttribute('role','group');nav.setAttribute('aria-label','Quiz learning tracks');
 for(const track of curriculum){const b=button(trackTabLabel(track),()=>{trackId=track.id;render();});b.setAttribute('aria-pressed',String(trackId===track.id));nav.append(b);}
 const sheet=el('div',undefined,'quiz-tab-sheet');
 const signedIn=Boolean(config.userId?.());
 const introText=signedIn
  ?'Scores and explanations unlock after submission.'
  :'Scores and explanations unlock after submission. Sign in to save verified account XP.';
 sheet.append(el('p',introText,'lesson-lead quiz-xp-notice'));

 unfinishedSection(sheet);

 const track=curriculum.find(t=>t.id===trackId);
 const featured=el('div',undefined,'quiz-featured-grid');
 v2Card(featured,`Personalized ${track.title} Quiz`,{track:trackId,mode:'personalized'},{featured:true});
 masterQuizCard(featured,track);
 sheet.append(featured);

 const chaptersGroup=el('div',undefined,'quiz-chapters-group');
 for(const chapter of track.chapters){
  const details=el('details',undefined,'curriculum-card quiz-chapter');details.dataset.chapter=chapter.id;
  const key=`${trackId}:${chapter.id}`;details.open=expanded.has(key);
  details.addEventListener('toggle',()=>{if(details.open)expanded.add(key);else expanded.delete(key);});
  details.append(el('summary',`Chapter ${chapter.chapter}: ${chapter.title}`));
  const grid=el('div',undefined,'curriculum-grid quiz-topic-grid');
  for(const topic of chapter.topics)v2Card(grid,topic.title,{track:trackId,mode:'topic',chapter:chapter.id,topic:topic.id});
  v2Card(grid,'General Quiz',{track:trackId,mode:'general',chapter:chapter.id});details.append(grid);chaptersGroup.append(details);
 }
 sheet.append(chaptersGroup);
 folder.append(nav,sheet);
 body.append(folder);
 host.append(body);
}
const expanded=new Set(),masterCounts={};
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
  return staleWarning;
 }catch(error){
  try{
   const cached=JSON.parse(localStorage.getItem(cacheKey));
   const nextBank=validateBank(cached.bank);
   if(cached.curriculum?.length!==2||!cached.curriculum.every(t=>t.chapters?.length&&t.chapters.every(c=>c.topics?.length)))throw error;
     bank=nextBank;curriculum=applyQuizScope(cached.curriculum);
     bank.practice_items=validateLessonPractice(makeLessonPractice(curriculum,cached.syntaxSource,{onStale:recordStale,allowMissingSyntax:true}),curriculum);
     bank.assessment_items=validateAssessmentItems(makeAssessmentItems(bank.practice_items,curriculum),curriculum);
     return [staleWarning,'Offline content: using the last successfully downloaded curriculum and question sources.'].filter(Boolean).join(' ');
  }catch{throw error;}
 }
}
function catalog(){
 curriculumCatalog();
 const sheet=host.querySelector('.quiz-tab-sheet')||host;
 const published=el('details',undefined,'quiz-published');published.append(el('summary','Original 5-question quizzes · prior scores & XP'),el('p','These original five-question chapter quizzes retain their existing scores and verified XP progress.'));
 const grid=el('div',undefined,'curriculum-grid quiz-topic-grid');
 for(const a of bank.assessments.filter(a=>a.pool_ids.every(pool=>{
  const items=bank.items.filter(q=>q.pool_id===pool&&q.content_version===a.item_version);
  return items.length&&items.every(q=>questionMetadata(q,curriculum)?.track_id===trackId);
 }))){
  const card=el('article',undefined,'curriculum-card quiz-topic-card');card.dataset.assessment=a.assessment_id;const summary=store.summary(a),draft=store.draft(a);
  const headRow=el('div',undefined,'quiz-card-head');
  headRow.append(el('h2',a.title),el('span','5 questions','quiz-card-count'));
  card.append(headRow,el('p',`Best ${summary.best_score}/5 · Last ${summary.last_score===null?'—':summary.last_score+'/5'} · ${plural(summary.attempt_count,'attempt')}`,'quiz-card-status'));
  const foot=el('div',undefined,'quiz-card-footer');
  const meter=xpMeter(summary.xp_awarded,10);
  if(meter)foot.append(meter);
  foot.append(button(draft?'Resume assessment':'Start assessment',()=>action(async()=>{if(draft)return draft;return store.start(a);}), 'lesson-primary'));
  card.append(foot);grid.append(card);
 }
 published.append(grid);sheet.append(published);
 const history=el('details',undefined,'quiz-history');history.append(el('summary','Your attempt history'));const list=el('div',undefined,'quiz-history-list');
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
 const grade=reviewForLearner(bank,t),a=assessmentFor(t);
 const header=el('header',undefined,'view-header curriculum-header');
 const titleGroup=el('div',undefined,'view-header-title-group');
 titleGroup.append(iconButton('All quizzes',BACK_ARROW_SVG,()=>{current=null;message='';render();}));
 const titleRow=el('div',undefined,'quiz-header-side-by-side');
 titleRow.append(el('h1',t.title||a?.title||'Quiz','view-title'));
 titleGroup.append(titleRow);
 header.append(titleGroup);
 host.append(header);

 const body=el('div',undefined,'quiz-review-body');
 const shell=el('div',undefined,'quiz-review-shell');
 const summaryCard=el('section',undefined,'quiz-results-summary');
 const summaryMain=el('div',undefined,'quiz-results-main');
 summaryMain.append(
  el('p','QUIZ RESULTS','lesson-eyebrow quiz-results-eyebrow'),
  el('p',`${grade.correct}/${t.presented.length} correct (${Math.round(100*grade.correct/t.presented.length)}%)`,'quiz-score')
 );
 summaryCard.append(summaryMain);
 const summaryMeta=el('div',undefined,'quiz-results-meta');
 if(t.includes_unreviewed&&t.practice)summaryMeta.append(el('p','Unscored practice attempt','quiz-card-status'));
 if(!t.practice){
  const summaryTarget=a||{assessment_id:t.assessment_id,content_version:t.content_version};
  const s=store.summary(summaryTarget),total=t.presented.length;
  summaryMeta.append(
   el('p',`Best ${s.best_score}/${total} · Last ${s.last_score}/${total} · ${s.xp_awarded}/${2*total} XP`,'quiz-results-stats'),
   el('p','Verified account totals appear in the sidebar.','quiz-card-status')
  );
 }
 if(summaryMeta.childElementCount)summaryCard.append(summaryMeta);
 shell.append(summaryCard);
 const strengths=grade.results.filter(r=>r.correct),needs=grade.results.filter(r=>!r.correct);
 const next=el('section',undefined,'quiz-next');next.append(el('h2','Based on this attempt'),el('p',`${strengths.length} ${strengths.length===1?'response':'responses'} matched the answer key; ${needs.length} ${needs.length===1?'needs':'need'} another look.`));
 const topicTitle=lid=>bank.assessments.find(a=>a.assessment_id===`quiz-${lid}`)?.title||lid;
 if(strengths.length)next.append(el('p',`Matched topics: ${[...new Set(strengths.map(r=>r.lesson_id))].map(topicTitle).join('; ')}.`));
 if(needs.length){
  const revisitRow=el('div',undefined,'quiz-revisit-row');
  for(const lid of [...new Set(needs.map(r=>r.lesson_id))])revisitRow.append(button(`Revisit: ${topicTitle(lid)}`,()=>config.onLesson?.(lid)));
  next.append(revisitRow);
 }
 shell.append(next);
 for(const [index,q] of itemsFor(bank,t).entries()){
  const response=t.responses[q.item_id]??null,correct=response===q.answer,card=el('article',undefined,'quiz-review-card');card.dataset.reviewItem=q.item_id;
  const cardHead=el('div',undefined,'quiz-review-head');
  cardHead.append(el('h2',`${index+1}. ${q.prompt}`),el('span',response===null?'Unanswered':correct?'Correct on this attempt':'Review this response',correct?'lesson-feedback correct':'lesson-feedback retry'));
  card.append(cardHead);
  const answerGrid=el('div',undefined,'quiz-review-answers');
  answerGrid.append(el('p',`Your answer: ${q.options.find(o=>o.id===response)?.text||'No answer'}`),el('p',`Correct answer: ${q.options.find(o=>o.id===q.answer).text}`));
  if(q.review_status!=='INDEPENDENTLY_REVIEWED'){
   card.append(answerGrid,el('p',q.rationale,'quiz-review-rationale'));
   const link=el('a','Read the lesson section');link.href=q.lesson_reference;card.append(link);
  }else{
   card.append(el('p',`Your answer: ${q.options.find(o=>o.id===response)?.text||'No answer'}`));
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
 const a=assessmentFor(t),q=questionForLearner(bank,t),ref=t.presented[t.position],count=t.presented.length;
 const flaggedSet=new Set(Array.isArray(t.flagged)?t.flagged:[]);
 const isFlagged=flaggedSet.has(q.item_id);
 const header=el('header',undefined,'view-header curriculum-header');
 const titleGroup=el('div',undefined,'view-header-title-group');
 titleGroup.append(iconButton('All quizzes',BACK_ARROW_SVG,()=>{current=null;pendingConfirmAttempt=null;message='';render();}));
 const titleRow=el('div',undefined,'quiz-header-side-by-side');
 titleRow.append(
  el('span',t.title||a?.title||'Quiz','quiz-header-name'),
  el('h1',`Question ${t.position+1} of ${count}`,'view-title')
 );
 titleGroup.append(titleRow);
 header.append(titleGroup);
 host.append(header);

 const body=el('div',undefined,'quiz-attempt-body');
 const layout=el('div',undefined,'quiz-attempt-layout');
 const main=el('div',undefined,'quiz-attempt-main');
 const answered=answeredCount(t),allAnswered=answered===count;

 const panel=el('section',undefined,'quiz-question');panel.dataset.quizItem=q.item_id;
 const panelBar=el('div',undefined,'quiz-question-bar');
 const hasAnswer=t.responses?.[q.item_id]!==undefined&&t.responses?.[q.item_id]!==null;
 if(hasAnswer){
  panelBar.append(button('Clear choice',()=>action(()=>store.clearAnswer(t.attempt_id,q.item_id)),'quiz-clear-btn'));
 }
 const flagBtn=button('',()=>action(()=>store.toggleFlag(t.attempt_id,q.item_id)),`quiz-flag-btn${isFlagged?' is-flagged':''}`);
 flagBtn.setAttribute('aria-pressed',String(isFlagged));
 flagBtn.setAttribute('aria-label',isFlagged?'Remove flag from this question':'Flag this question for review');
 flagBtn.innerHTML=FLAG_SVG;
 flagBtn.append(el('span',isFlagged?'Flagged':'Flag'));
 panelBar.append(flagBtn);
 panel.append(panelBar);

 if(q.stimulus)panel.append(el('p',q.stimulus.sentence,'lesson-example-sentence'));
 const field=el('fieldset');field.append(el('legend',q.prompt));const choices=el('div',undefined,q.kind==='tree_choice'?'quiz-tree-options':'quiz-options');
 for(const id of ref.option_order){const option=q.options.find(o=>o.id===id),label=el('label',undefined,'lesson-option'),radio=el('input');radio.type='radio';radio.name=q.item_id;radio.value=id;radio.checked=t.responses[q.item_id]===id;
  radio.addEventListener('change',()=>action(()=>store.answer(t.attempt_id,q.item_id,id)));label.append(radio,el('span',option.text));
  const group=el('div',undefined,'quiz-choice');group.append(label);if(option.diagram){const diagram=renderLessonTree(option.diagram);diagram.classList.add('quiz-candidate');diagram.querySelector('svg')?.setAttribute('aria-label',`Candidate ${id}: ${option.text}`);group.append(diagram);}choices.append(group);
 }
 field.append(choices);panel.append(field);main.append(panel);

 const controls=el('div',undefined,'quiz-attempt-controls');
 const nav=el('nav',undefined,'lesson-step-controls');nav.setAttribute('aria-label','Question navigation');
 const back=iconButton('Previous question',PREV_ARROW_SVG,()=>action(()=>store.move(t.attempt_id,t.position-1)),'quiz-step-btn');back.disabled=t.position===0;
 const next=iconButton('Next question',NEXT_ARROW_SVG,()=>action(()=>store.move(t.attempt_id,t.position+1)),'quiz-step-btn');next.disabled=t.position===count-1;
 nav.append(back,next);
 controls.append(nav);
 if(allAnswered){
  const submitBtn=button('Submit',()=>{
   const live=store.attempts[t.attempt_id];
   if(!live||live.presented.some(item=>live.responses?.[item.item_id]===undefined||live.responses?.[item.item_id]===null)){
    render();
    return;
   }
   action(()=>store.submit(t.attempt_id,{requireComplete:true}));
  },'lesson-primary');
  controls.append(submitBtn);
 }
 main.append(controls);

 const navigator=el('aside',undefined,'quiz-navigator');
 navigator.setAttribute('aria-label','Question navigator');
 const navHead=el('div',undefined,'quiz-nav-head');
 navHead.append(el('h2','Questions'),el('span',`${answered}/${count} answered`,'quiz-nav-summary'));
 navigator.append(navHead);
 const numGrid=el('div',undefined,'quiz-nav-grid');
 for(let i=0;i<count;i++){
  const itemRef=t.presented[i];
  const isCurrent=i===t.position;
  const isAnswered=t.responses?.[itemRef.item_id]!==undefined&&t.responses?.[itemRef.item_id]!==null;
  const isItemFlagged=flaggedSet.has(itemRef.item_id);
  const numBtn=button(String(i+1),()=>action(()=>store.move(t.attempt_id,i)),`quiz-nav-num${isCurrent?' is-current':''}${isAnswered?' is-answered':''}${isItemFlagged?' is-flagged':''}`);
  if(isCurrent)numBtn.setAttribute('aria-current','step');
  const states=[isCurrent?'current':null,isAnswered?'answered':'unanswered',isItemFlagged?'flagged for review':null].filter(Boolean);
  numBtn.setAttribute('aria-label',`Question ${i+1}, ${states.join(', ')}`);
  numGrid.append(numBtn);
 }
 navigator.append(numGrid);
 const legend=el('div',undefined,'quiz-nav-legend');
 const addLegend=(cls,text)=>{const item=el('span',undefined,'quiz-nav-legend-item');item.append(el('span',undefined,`quiz-nav-dot ${cls}`),el('span',text));legend.append(item);};
 addLegend('is-current','Current');
 addLegend('is-answered','Answered');
 addLegend('is-flagged','Flagged');
 navigator.append(legend);

 layout.append(main,navigator);
 body.append(layout);
 host.append(body);
}
function render(){
 if(!host||host.hidden||!store||!bank)return;const scroll=host.scrollTop;
 host.replaceChildren();
 if(current){
  const t=store.attempts[current];
  if(!t){current=null;catalog();}
  else if(store.isArchived(t)){current=null;message='This assessment version is archived. Your attempt was retained.';catalog();}
  else if(t.submitted_at)review(t);
  else attemptScreen(t);
 }else catalog();
 footer();host.scrollTop=scroll;
}
export function initQuizzes(options={}){
 config=options;host=el('section',undefined,'curriculum-view quiz-view');host.id='quizzesView';host.hidden=true;host.setAttribute('aria-label','Independent quizzes');document.body.append(host);
 subscribeAuthState(()=>{generation++;store=null;current=null;busy=false;if(!host.hidden)openQuizzes();});
 const route=()=>{const match=/^#quiz\/([a-z0-9-]+)$/.exec(location.hash);if(match)config.onNavigate?.(match[1]);};window.addEventListener('hashchange',route);if(/^#quiz\//.test(location.hash))queueMicrotask(route);
}
export async function openQuizzes(id=null){
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
export function closeQuizzes(){generation++;busy=false;current=null;pendingConfirmAttempt=null;if(host){host.hidden=true;host.replaceChildren();}document.body.classList.remove('quizzes-open','curriculum-open');}
