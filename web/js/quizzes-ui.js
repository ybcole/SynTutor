import { showCurriculumState } from './curriculum-state.js';
import {validateBank,quizKey,itemsFor,gradeAttempt,questionForLearner,reviewForLearner,MAX_QUIZ_ITEMS} from './quiz-core.js';
import {createQuizStore} from './quiz-progress.js';
import {composeQuizEvidence,requestQuizEvidence,requestEvidence,renderEvidence} from './explanation-evidence.js';
import {renderLessonTree} from './lessons-ui.js';
import {subscribeAuthState} from './auth.js';
import {loadActiveCourse,quizCurriculum} from './lesson-curriculum.js';
import {selectQuestions,specKey,eligibleQuestions,publishedBlueprint,questionMetadata} from './quiz-v2.js';
import {makeLessonPractice,validateLessonPractice} from './quiz-lesson-practice.js';
import {makeAssessmentItems,validateAssessmentItems} from './quiz-assessment-items.js';
let host,config={},bank,store,curriculum,current=null,trackId='syntax',busy=false,message='',generation=0;
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const button=(text,fn,cls='')=>{const b=el('button',text,cls);b.type='button';b.addEventListener('click',fn);return b;};
const labels={mcq:'Concept question',tree_choice:'Tree selection',structure:'Structure identification',minimal_pair:'Compare analyses',rule_application:'Apply a convention',diagnosis:'Tree diagnosis',repair:'Structure repair',analysis:'Grammatical analysis',concept_completion:'Grammatical concept'};
function assessmentFor(t){return bank.assessments.find(a=>quizKey(a)===quizKey(t));}
async function action(fn){
 if(busy)return;const token=generation,focusName=document.activeElement?.name,focusValue=document.activeElement?.value;busy=true;host.setAttribute('aria-busy','true');host.querySelectorAll('button,input').forEach(n=>{n.disabled=true;});
 try{const result=await fn();if(token!==generation)return;
  if(result?.attempt_id)current=result.attempt_id;
  if(result&&Object.hasOwn(result,'earned'))window.dispatchEvent(new Event('syntutor:quiz-progress'));
   message=result&&Object.hasOwn(result,'earned')?(store.attempts[result.attempt_id]?.practice?`Quiz submitted. Score: ${result.grade.correct}/${result.grade.results.length}. XP is not enabled for this quiz.`:`${result.earned} new quiz XP for this assessment version.${store.status === 'Synced to your account' ? '' : ' Device estimate until verified by account sync.'}`):'';
 }catch(e){if(token===generation)message=e.message;}
 finally{if(token===generation){busy=false;host.setAttribute('aria-busy','false');render();if(focusName)host.querySelector(`input[name="${CSS.escape(focusName)}"][value="${focusValue}"]`)?.focus();}}
}
function footer(){const f=el('footer',undefined,'lesson-save-status');f.setAttribute('aria-live','polite');if(message)f.append(el('p',message));f.append(el('p',store.status));if(config.userId?.())f.append(button('Retry account sync',()=>action(()=>store.retry())));host.append(f);}
function v2Card(parent,title,spec){
 spec={...spec,format:'formal',...(spec.mode==='personalized'?{content_tier:'lesson-assessment'}:{})};
 const card=el('article',undefined,'curriculum-card quiz-topic-card');
 card.append(el('h3',title));
 let reason='',selection;
 try{selection=selectQuestions(bank,curriculum,spec,store.attempts,0);}catch(e){reason=e.message;}
 if(reason&&spec.content_tier!=='lesson-assessment'){
  const expandedSpec={...spec,content_tier:'lesson-assessment'};
  try{selection=selectQuestions(bank,curriculum,expandedSpec,store.attempts,0);spec=expandedSpec;reason='';}catch{}
 }
 const provisional=spec.content_tier==='lesson-assessment';
 const published=publishedBlueprint(bank,curriculum,spec),assessment=published||{assessment_id:specKey(spec),content_version:'2.0.0'},draft=store.draft(assessment);
 const previous=Object.values(store.attempts).filter(t=>quizKey(t)===quizKey(assessment)&&t.submitted_at&&!store.isArchived(t)).sort((a,b)=>a.submitted_at.localeCompare(b.submitted_at));
 if(previous.length){const last=previous.at(-1),best=Math.max(...previous.map(t=>gradeAttempt(bank,t).correct/t.presented.length));card.append(el('p',`Best ${Math.round(best*100)}% · Last ${gradeAttempt(bank,last).correct}/${last.presented.length} · ${previous.length} attempts`));}
 card.append(el('p',reason||`${selection.items.length} questions · ${provisional?'Scored quiz · question review pending · XP not enabled':published?'Published assessment · verified account XP eligible':selection.diagnostic?'Diagnostic quiz (insufficient history) · XP not enabled':'Scored quiz · XP not enabled'}`,'lesson-status'));
 if(published)card.append(el('p',`${store.summary(published).xp_awarded}/10 device XP estimate; account verification required.`));
 const start=button(draft?'Resume quiz':reason?'Questions Under Review':'Start quiz',()=>action(()=>draft||store.startV2(curriculum,spec)),'lesson-primary');
 start.disabled=!!reason&&!draft;card.append(start);parent.append(card);
}
function curriculumCatalog(){
 const header=el('header',undefined,'curriculum-header');header.append(el('p','QUIZ V2','lesson-eyebrow'),el('h1','Assess your understanding.'),el('p','Answer independently. Scores, correct answers and explanations are available only after submission. Quizzes follow the implemented Lessons curriculum. Question review and XP eligibility are shown separately.','lesson-lead'));host.append(header);
 const nav=el('div',undefined,'lesson-track-tabs');nav.setAttribute('aria-label','Quiz learning tracks');
 for(const track of curriculum){const b=button(`${track.title} — ${track.subtitle}`,()=>{trackId=track.id;render();});b.setAttribute('aria-pressed',String(trackId===track.id));nav.append(b);}host.append(nav);
 const track=curriculum.find(t=>t.id===trackId),special=el('div',undefined,'curriculum-grid');
 v2Card(special,`Personalized ${track.title} Quiz`,{track:trackId,mode:'personalized'});host.append(special);
 for(const chapter of track.chapters){
  const details=el('details',undefined,'curriculum-card quiz-chapter');details.dataset.chapter=chapter.id;
  const key=`${trackId}:${chapter.id}`;details.open=expanded.has(key);
  details.addEventListener('toggle',()=>{if(details.open)expanded.add(key);else expanded.delete(key);});
  details.append(el('summary',`Chapter ${chapter.chapter}: ${chapter.title}`));
  const grid=el('div',undefined,'curriculum-grid');
  for(const topic of chapter.topics)v2Card(grid,topic.title,{track:trackId,mode:'topic',chapter:chapter.id,topic:topic.id});
  v2Card(grid,'General Quiz',{track:trackId,mode:'general',chapter:chapter.id});details.append(grid);host.append(details);
 }
 const master=el('section',undefined,'quiz-practice');master.append(el('h2',`${track.title} Master Quiz`));
 const min=track.chapters.length;
 let masterTier='reviewed';
 try{selectQuestions(bank,curriculum,{track:trackId,mode:'master',count:min},store.attempts,0);}catch{masterTier='lesson-assessment';}
 const available=new Set(eligibleQuestions(bank,curriculum,trackId,masterTier).map(q=>q.item_id)).size,max=Math.min(MAX_QUIZ_ITEMS,available);
 const label=el('label','Number of questions '),input=el('input');input.type='number';input.min=String(min);input.max=String(max);input.step='1';input.value=String(masterCounts[trackId]||min);input.disabled=max<min;input.setAttribute('aria-label',`${track.title} Master Quiz question count`);label.append(input);master.append(label);
 master.append(el('p',`Minimum ${min} (one per chapter); ${available} distinct ${masterTier==='reviewed'?'reviewed':'eligible assessment'} questions. All chapters must be represented.${available>MAX_QUIZ_ITEMS?` Maximum ${MAX_QUIZ_ITEMS.toLocaleString()} per attempt.`:''}`));
 const target=el('div');target.setAttribute('aria-live','polite');const update=()=>{masterCounts[trackId]=Number(input.value);target.replaceChildren();if(max<min)target.append(el('p',`Questions Under Review: Master Quiz requires at least ${min} questions and coverage of all ${min} chapters; only ${max} eligible questions are available.`));else if(!input.validity.valid)target.append(el('p','Choose a whole number within the available range.'));else v2Card(target,'Master Quiz',{track:trackId,mode:'master',count:Number(input.value),...(masterTier==='lesson-assessment'?{content_tier:masterTier}:{})});};input.addEventListener('input',update);update();master.append(target);host.append(master);
}
const expanded=new Set(),masterCounts={};
async function loadContent(){
 if(bank&&curriculum)return '';
 const cacheKey='syntutor:quiz-v2:public-content:2';
 try{
   const [nextBank,course,syntaxSource]=await Promise.all([
   fetch('/content/quizzes/bank.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('Bank unavailable');return r.json();}).then(validateBank),
    loadActiveCourse(),
    fetch('/content/quizzes/syntax-practice-source.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('Practice source unavailable');return r.json();}).catch(()=>null),
  ]);
  bank=nextBank;curriculum=quizCurriculum(course);
  // Only public, compact curriculum metadata is cached, never the 12MB course.
   try{localStorage.setItem(cacheKey,JSON.stringify({bank,curriculum,syntaxSource}));}catch{}
    bank.practice_items=validateLessonPractice(makeLessonPractice(curriculum,syntaxSource),curriculum);
    bank.assessment_items=validateAssessmentItems(makeAssessmentItems(bank.practice_items),curriculum);
  return '';
 }catch(error){
  try{
   const cached=JSON.parse(localStorage.getItem(cacheKey));
   const nextBank=validateBank(cached.bank);
   if(cached.curriculum?.length!==2||!cached.curriculum.every(t=>t.chapters?.length&&t.chapters.every(c=>c.topics?.length)))throw error;
    bank=nextBank;curriculum=cached.curriculum;
     bank.practice_items=validateLessonPractice(makeLessonPractice(curriculum,cached.syntaxSource),curriculum);
     bank.assessment_items=validateAssessmentItems(makeAssessmentItems(bank.practice_items),curriculum);
     return 'Offline content: using the last successfully downloaded curriculum and question sources. Quiz scores are saved locally; account XP requires server verification.';
  }catch{throw error;}
 }
}
function catalog(){
 curriculumCatalog();
 const published=el('details',undefined,'quiz-published');published.append(el('summary','Published assessments · existing XP and history'),el('p','These original five-item assessments retain their published scope, versions and verified account XP contract. Local XP is pending until account verification.'));
 const grid=el('div',undefined,'curriculum-grid');
 for(const a of bank.assessments.filter(a=>a.pool_ids.every(pool=>{
  const items=bank.items.filter(q=>q.pool_id===pool&&q.content_version===a.item_version);
  return items.length&&items.every(q=>questionMetadata(q,curriculum)?.track_id===trackId);
 }))){
  const card=el('article',undefined,'curriculum-card');card.dataset.assessment=a.assessment_id;const summary=store.summary(a),draft=store.draft(a);
  card.append(el('p',`${a.mode} · 5 questions · v${a.content_version}`,'lesson-eyebrow'),el('h2',a.title),el('p',`Best ${summary.best_score}/5 · Last ${summary.last_score===null?'—':summary.last_score+'/5'} · ${summary.attempt_count} attempts`));
  card.append(el('p',`${summary.xp_awarded}/10 device XP estimate · account verification required`,'lesson-status'));
  card.append(button(draft?'Resume assessment':'Start assessment',()=>action(async()=>{if(draft)return draft;return store.start(a);}), 'lesson-primary'));grid.append(card);
 }
 published.append(grid);host.append(published);
 const unfinished=Object.values(store.attempts).filter(t=>!t.submitted_at&&!store.isArchived(t)).sort((a,b)=>b.started_at.localeCompare(a.started_at));
 if(unfinished.length){
  const section=el('section',undefined,'quiz-practice');section.append(el('h2','Resume unfinished quizzes'));
  const drafts=el('ul');
  for(const t of unfinished){const row=el('li');row.append(button(`Resume ${t.title||assessmentFor(t)?.title||'Reinforcement'} · ${t.presented.length} questions · at ${t.position+1}`,()=>{current=t.attempt_id;message='';render();}));drafts.append(row);}
  section.append(drafts);host.append(section);
 }
 const history=el('details');history.append(el('summary','Your attempt history'));const list=el('ul');
 for(const t of Object.values(store.attempts).filter(t=>t.submitted_at || store.isArchived(t)).sort((a,b)=>(b.submitted_at||b.started_at).localeCompare(a.submitted_at||a.started_at))){
  if (store.isArchived(t)) {
     const score = Number.isInteger(t.correct) ? ` · ${t.correct}/${t.presented?.length||5} recorded${t.practice?' (XP not enabled)':''}` : '';
   list.append(el('li', `${t.assessment_id} · v${t.content_version} · archived${score}`));
   continue;
  }
  const grade=gradeAttempt(bank,t);
  const row=el('li');row.append(button(`${t.title||(t.practice?'Reinforcement':assessmentFor(t)?.title||t.assessment_id)} · ${grade.correct}/${t.presented.length} · v${t.content_version}`,()=>{current=t.attempt_id;message='';render();}));list.append(row);
 }
 history.append(list);host.append(history);
}
function review(t){
 const grade=reviewForLearner(bank,t),a=assessmentFor(t);host.append(el('p','QUIZ RESULTS','lesson-eyebrow'),el('h1',t.title||a?.title||'Quiz'),el('p',`${grade.correct}/${t.presented.length} correct (${Math.round(100*grade.correct/t.presented.length)}%) · ${grade.incorrect} incorrect or unanswered`,'quiz-score'));
 if(t.includes_unreviewed)host.append(el('p','Question review pending: this quiz has not been independently reviewed. Your score is recorded, but this quiz does not award verified account XP.','lesson-status'));
 if(!t.practice){const s=store.summary(a);host.append(el('p',`Best ${s.best_score}/5 · last ${s.last_score}/5 · ${s.xp_awarded}/10 device XP estimate for this version. Verified account totals appear in the sidebar.`));}
 host.append(el('p','Review your submitted answers below. A short quiz does not establish mastery.','lesson-lead'));
 const strengths=grade.results.filter(r=>r.correct),needs=grade.results.filter(r=>!r.correct);
 const next=el('section',undefined,'quiz-next');next.append(el('h2','Based on this attempt'),el('p',`${strengths.length} responses matched the answer key; ${needs.length} need another look.`));
 const topicTitle=lid=>bank.assessments.find(a=>a.assessment_id===`quiz-${lid}`)?.title||lid;
 if(strengths.length)next.append(el('p',`Responses that matched: ${[...new Set(strengths.map(r=>r.lesson_id))].map(topicTitle).join('; ')}.`));
 for(const lid of [...new Set(needs.map(r=>r.lesson_id))])next.append(button(`Revisit: ${topicTitle(lid)}`,()=>config.onLesson?.(lid)));host.append(next);
 for(const [index,q] of itemsFor(bank,t).entries()){
  const response=t.responses[q.item_id]??null,correct=response===q.answer,card=el('article',undefined,'quiz-review-card');card.dataset.reviewItem=q.item_id;
  card.append(el('h2',`${index+1}. ${q.prompt}`),el('p',response===null?'Unanswered':correct?'Correct on this attempt':'Review this response',correct?'lesson-feedback correct':'lesson-feedback retry'));
  card.append(el('p',`Your answer: ${q.options.find(o=>o.id===response)?.text||'No answer'}`));
    if(['practice','assessment_draft'].includes(q.publication_status)){
     card.append(el('p',`Correct answer: ${q.options.find(o=>o.id===q.answer).text}`),el('p',q.rationale),el('p','Basis: the corresponding implemented SynTutor lesson section. Independent question review is pending.','lesson-status'));
    const link=el('a','Read the lesson section');link.href=q.lesson_reference;card.append(link);
   }else renderEvidence(composeQuizEvidence(q,response,bank),card);
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
    if(['practice','assessment_draft'].includes(q.publication_status)){host.append(card);continue;}
   const token=generation,controller=new AbortController(),timer=setTimeout(()=>controller.abort(),5000);
  requestQuizEvidence(q,response,{signal:controller.signal}).then(evidence=>{if(token===generation&&card.isConnected)renderEvidence(evidence,card);}).catch(()=>{}).finally(()=>clearTimeout(timer));
  host.append(card);
 }
 if(!t.practice)host.append(button('Try a new attempt',()=>action(()=>store.start(a)),'lesson-primary'));
 if(t.quiz_v2)host.append(button('Try a new attempt',()=>action(()=>store.startV2(curriculum,t.spec)),'lesson-primary'));
  host.append(button('Back to quiz selection',()=>{current=null;render();}));
}
function attemptScreen(t){
 const a=assessmentFor(t),q=questionForLearner(bank,t),ref=t.presented[t.position],count=t.presented.length;
  host.append(el('p',`${t.title||a?.title||'Quiz'} · v${t.content_version}`,'lesson-eyebrow'),el('h1',`Question ${t.position+1} of ${count}`),el('p',labels[q.kind]||'Quiz question','lesson-status'));
 const panel=el('section',undefined,'quiz-question');panel.dataset.quizItem=q.item_id;
 if(q.stimulus)panel.append(el('p',q.stimulus.sentence,'lesson-example-sentence'));
 const field=el('fieldset');field.append(el('legend',q.prompt));const choices=el('div',undefined,q.kind==='tree_choice'?'quiz-tree-options':'quiz-options');
 for(const id of ref.option_order){const option=q.options.find(o=>o.id===id),label=el('label',undefined,'lesson-option'),radio=el('input');radio.type='radio';radio.name=q.item_id;radio.value=id;radio.checked=t.responses[q.item_id]===id;
  radio.addEventListener('change',()=>action(()=>store.answer(t.attempt_id,q.item_id,id)));label.append(radio,el('span',option.text));
  const group=el('div',undefined,'quiz-choice');group.append(label);if(option.diagram){const diagram=renderLessonTree(option.diagram);diagram.classList.add('quiz-candidate');diagram.querySelector('svg')?.setAttribute('aria-label',`Candidate ${id}: ${option.text}`);group.append(diagram);}choices.append(group);
 }
 field.append(choices);panel.append(field);host.append(panel);
 const nav=el('nav',undefined,'lesson-step-controls');nav.setAttribute('aria-label','Question navigation');
 const back=button('Previous question',()=>action(()=>store.move(t.attempt_id,t.position-1)));back.disabled=t.position===0;
 const next=button('Next question',()=>action(()=>store.move(t.attempt_id,t.position+1)));next.disabled=t.position===count-1;nav.append(back,next);host.append(nav);
 host.append(el('p','Answers and source-based explanations appear after submission. You can change your choices before submitting.'));
 const unanswered=t.presented.filter(q=>!t.responses[q.item_id]).length;
 host.append(button(`Submit assessment${unanswered?` · ${unanswered} unanswered`:''}`,()=>action(()=>store.submit(t.attempt_id)),'lesson-primary'));
}
function render(){
 if(!host||host.hidden||!store||!bank)return;const scroll=host.scrollTop;host.replaceChildren(button('Back to Syntax Generator',()=>config.onExit?.()));
 if(current){host.append(button('← All quizzes',()=>{current=null;message='';render();}));const t=store.attempts[current];if(!t){current=null;catalog();}else if(store.isArchived(t)){current=null;message='This assessment version is archived. Your attempt was retained.';catalog();}else if(t.submitted_at)review(t);else attemptScreen(t);}else catalog();
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
export function closeQuizzes(){generation++;busy=false;current=null;if(host){host.hidden=true;host.replaceChildren();}document.body.classList.remove('quizzes-open','curriculum-open');}
