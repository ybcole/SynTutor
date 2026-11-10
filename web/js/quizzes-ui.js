import { showCurriculumState } from './curriculum-state.js';
import {validateBank,quizKey,itemsFor,gradeAttempt} from './quiz-core.js';
import {createQuizStore} from './quiz-progress.js';
import {composeQuizEvidence,requestQuizEvidence,requestEvidence,renderEvidence} from './explanation-evidence.js';
import {renderLessonTree} from './lessons-ui.js';
import {subscribeAuthState} from './auth.js';
let host,config={},bank,store,current=null,mode='all',busy=false,message='',generation=0;
const el=(tag,text,cls)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(cls)n.className=cls;return n;};
const button=(text,fn,cls='')=>{const b=el('button',text,cls);b.type='button';b.addEventListener('click',fn);return b;};
const labels={mcq:'Concept check',tree_choice:'Tree selection',structure:'Structure identification',minimal_pair:'Compare analyses',rule_application:'Apply a convention',diagnosis:'Tree diagnosis',repair:'Structure repair'};
function assessmentFor(t){return bank.assessments.find(a=>quizKey(a)===quizKey(t));}
async function action(fn){
 if(busy)return;const token=generation,focusName=document.activeElement?.name,focusValue=document.activeElement?.value;busy=true;host.setAttribute('aria-busy','true');host.querySelectorAll('button,input').forEach(n=>{n.disabled=true;});
 try{const result=await fn();if(token!==generation)return;
  if(result?.attempt_id)current=result.attempt_id;
  message=result&&Object.hasOwn(result,'earned')?`${result.earned} new quiz XP for this assessment version.${store.status === 'Synced to your account' ? '' : ' Device estimate until verified by account sync.'}`:'';
 }catch(e){if(token===generation)message=e.message;}
 finally{if(token===generation){busy=false;host.setAttribute('aria-busy','false');render();if(focusName)host.querySelector(`input[name="${CSS.escape(focusName)}"][value="${focusValue}"]`)?.focus();}}
}
function footer(){const f=el('footer',undefined,'lesson-save-status');f.setAttribute('aria-live','polite');if(message)f.append(el('p',message));f.append(el('p',store.status));if(config.userId?.())f.append(button('Retry account sync',()=>action(()=>store.retry())));host.append(f);}
function catalog(){
 const header=el('header',undefined,'curriculum-header');header.append(el('p','INDEPENDENT ASSESSMENTS','lesson-eyebrow'),el('h1','Test what you can apply.'),el('p','Five questions. New examples. Review your reasoning after you submit. Lessons remain available whenever you want to revisit an idea.','lesson-lead'));
 const total=bank.assessments.reduce((sum,a)=>sum+store.summary(a).xp_awarded,0);header.append(el('p',`${total} quiz XP across assessment versions`,'lesson-total'));host.append(header);
 const nav=el('div',undefined,'lesson-track-tabs');nav.setAttribute('aria-label','Assessment modes');
 for(const m of ['all','topic','chapter','cumulative','diagnostic','challenge']){const b=button(m[0].toUpperCase()+m.slice(1),()=>{mode=m;render();});b.setAttribute('aria-pressed',String(mode===m));nav.append(b);}host.append(nav);
 const grid=el('div',undefined,'curriculum-grid');
 for(const a of bank.assessments.filter(a=>mode==='all'||a.mode===mode||(mode==='topic'&&a.mode==='chapter'))){
  const card=el('article',undefined,'curriculum-card');card.dataset.assessment=a.assessment_id;const summary=store.summary(a),draft=store.draft(a);
  card.append(el('p',`${a.mode} · 5 questions · v${a.content_version}`,'lesson-eyebrow'),el('h2',a.title),el('p',`Best ${summary.best_score}/5 · Last ${summary.last_score===null?'—':summary.last_score+'/5'} · ${summary.attempt_count} attempts`));
  card.append(el('p',`${summary.xp_awarded}/10 XP earned · lessons are recommended, not required`,'lesson-status'));
  card.append(button(draft?'Resume assessment':'Start assessment',()=>action(async()=>{if(draft)return draft;return store.start(a);}), 'lesson-primary'));grid.append(card);
 }
 host.append(grid);
 const practice=el('section',undefined,'quiz-practice');practice.append(el('h2','Reinforce what you missed'),el('p','Practise five questions selected from your mistakes, with another example where available. Reinforcement has no XP reward.'),button('Start reinforcement',()=>action(()=>store.practice())));host.append(practice);
 const history=el('details');history.append(el('summary','Your attempt history'));const list=el('ul');
 for(const t of Object.values(store.attempts).filter(t=>t.submitted_at || store.isArchived(t)).sort((a,b)=>(b.submitted_at||b.started_at).localeCompare(a.submitted_at||a.started_at))){
  if (store.isArchived(t)) {
   const score = Number.isInteger(t.correct) ? ` · ${t.correct}/5 recorded` : '';
   list.append(el('li', `${t.assessment_id} · v${t.content_version} · archived${score}`));
   continue;
  }
  const grade=gradeAttempt(bank,t);
  const row=el('li');row.append(button(`${t.practice?'Reinforcement':assessmentFor(t)?.title||t.assessment_id} · ${grade.correct}/5 · v${t.content_version}`,()=>{current=t.attempt_id;message='';render();}));list.append(row);
 }
 history.append(list);host.append(history);
}
function review(t){
 const grade=gradeAttempt(bank,t),a=assessmentFor(t);host.append(el('p',t.practice?'UNSCORED REINFORCEMENT':'ASSESSMENT REVIEW','lesson-eyebrow'),el('h1',a?.title||'Reinforcement'),el('p',`${grade.correct}/5 correct · ${grade.incorrect} incorrect or unanswered`,'quiz-score'));
 if(!t.practice){const s=store.summary(a);host.append(el('p',`Best ${s.best_score}/5 · last ${s.last_score}/5 · ${s.xp_awarded}/10 quiz XP recorded for this version.`));}
 host.append(el('p','Use this attempt to choose your next practice. A short assessment does not establish mastery.','lesson-lead'));
 const strengths=grade.results.filter(r=>r.correct),needs=grade.results.filter(r=>!r.correct);
 const next=el('section',undefined,'quiz-next');next.append(el('h2','Based on this attempt'),el('p',`${strengths.length} responses matched the reviewed answer; ${needs.length} need another look.`));
 const topicTitle=lid=>bank.assessments.find(a=>a.assessment_id===`quiz-${lid}`)?.title||lid;
 if(strengths.length)next.append(el('p',`Responses that matched: ${[...new Set(strengths.map(r=>r.lesson_id))].map(topicTitle).join('; ')}.`));
 for(const lid of [...new Set(needs.map(r=>r.lesson_id))])next.append(button(`Revisit: ${topicTitle(lid)}`,()=>config.onLesson?.(lid)));host.append(next);
 for(const [index,q] of itemsFor(bank,t).entries()){
  const response=t.responses[q.item_id]??null,correct=response===q.answer,card=el('article',undefined,'quiz-review-card');card.dataset.reviewItem=q.item_id;
  card.append(el('h2',`${index+1}. ${q.prompt}`),el('p',response===null?'Unanswered':correct?'Correct on this attempt':'Review this response',correct?'lesson-feedback correct':'lesson-feedback retry'));
  card.append(el('p',`Your answer: ${q.options.find(o=>o.id===response)?.text||'No answer'}`));
  renderEvidence(composeQuizEvidence(q,response,bank),card);
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
      inspector.replaceChildren(el('p','Loading selected tree evidence…'));
      try{
        const evidence=await requestEvidence(q.answer_tree,nodeId);
        if(requestId!==version||token!==generation||!card.isConnected)return;
        renderEvidence(evidence,inspector,{treeRoot:treeView});
        if(feature) {
          const note=el('p','Selected recorded feature '+feature+'. The printed feature is not itself a grammar-error verdict.');
          note.dataset.xai7FeatureSelected='';
          inspector.prepend(note);
        }
      }catch{
        if(requestId===version&&card.isConnected)
          inspector.replaceChildren(el('p','Selected tree evidence is unavailable. Reviewed quiz feedback remains visible.'));
      }
    };
    treeView=renderLessonTree(q.answer_tree,{interactive:true,zoomControls:true,stackFeatures:true,onSelectNode:choose});
    details.append(el('summary','See the reviewed answer tree'),treeView,inspector);
    card.append(details);
  }
  const token=generation,controller=new AbortController(),timer=setTimeout(()=>controller.abort(),5000);
  requestQuizEvidence(q,response,{signal:controller.signal}).then(evidence=>{if(token===generation&&card.isConnected)renderEvidence(evidence,card);}).catch(()=>{}).finally(()=>clearTimeout(timer));
  host.append(card);
 }
 if(!t.practice)host.append(button('Try a new attempt',()=>action(()=>store.start(a)),'lesson-primary'));
 host.append(button('Practise missed concepts · no XP',()=>action(()=>store.practice())));
}
function attemptScreen(t){
 const a=assessmentFor(t),items=itemsFor(bank,t),q=items[t.position],ref=t.presented[t.position];
 host.append(el('p',`${t.practice?'Reinforcement · no XP':a.title} · v${t.content_version}`,'lesson-eyebrow'),el('h1',`Question ${t.position+1} of 5`),el('p',labels[q.kind],'lesson-status'));
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
 const next=button('Next question',()=>action(()=>store.move(t.attempt_id,t.position+1)));next.disabled=t.position===4;nav.append(back,next);host.append(nav);
 host.append(el('p','Answers and source-based explanations appear after submission. You can change your choices before submitting.'));
 const unanswered=items.filter(q=>!t.responses[q.item_id]).length;
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
 showCurriculumState(host, { message: 'Loading reviewed assessments…' });
 try{
  bank ||= validateBank(await(await fetch('/content/quizzes/bank.json',{cache:'no-cache'})).json());
  if(!store){let storage;try{storage=localStorage;}catch{storage=null;}const next=createQuizStore(bank,{storage,userId:config.userId?.()||'guest',client:config.client?.()});await next.load();if(token!==generation)return;store=next;}
  if(token!==generation)return;current=null;message='';busy=false;
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
