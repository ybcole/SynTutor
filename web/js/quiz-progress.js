import { makeAttempt,validateAttempt,canReviewAttempt,gradeAttempt,summaryFor,quizKey,reinforcement,itemsFor } from './quiz-core.js';
import { isResponseProvided } from './quiz-mixed-eval.js';
import { makeV2Attempt, publishedBlueprint } from './quiz-v2.js';
export function createQuizStore(bank,{storage,userId='guest',client=null,timeoutMs=5000}={}) {
  const key=`syntutor:assessments:v1:${userId}`;
  let state={attempts:{},drafts:{}},status='Saved on this device',queue=Promise.resolve();
  const dirty=new Set();
  let retryAfter=0;
  const archived = t => t.retired || !canReviewAttempt(bank, t);
  function read(){
    if(!storage){status='Progress storage unavailable; keep this page open';return;}
    try{const saved=JSON.parse(storage.getItem(key)||'null');if(saved&&saved.attempts&&saved.drafts)state=saved;}catch{status='Progress storage unavailable; keep this page open';}
  }
  function write(){try{storage?.setItem(key,JSON.stringify(state));}catch{status='Progress storage unavailable; keep this page open';}}
  async function bounded(request){let timer;const controller=new AbortController();const job=typeof request.abortSignal==='function'?request.abortSignal(controller.signal):request;
    try{return await Promise.race([job,new Promise((_r,reject)=>{timer=setTimeout(()=>{controller.abort();reject(Error('Account sync timed out; attempts remain saved on this device.'));},timeoutMs);})]);}finally{clearTimeout(timer);}}
  const pendingStatus = 'Account sync unavailable; attempts remain saved on this device. Retry when connected.';
  function serial(run) {
    const locked=()=>globalThis.navigator?.locks?.request?navigator.locks.request(key,run):run();
    queue=queue.catch(()=>{}).then(locked);
    return queue;
  }
  async function sync(readFailed=false){
    if(!client||userId==='guest')return {};
    const awards={};
    for (const t of Object.values(state.attempts)) {
      if (!t.synced) dirty.add(t.attempt_id);
    }
    for (const id of [...dirty]) {
      const attempt = state.attempts[id];
      if (!attempt || attempt.synced || (attempt.practice && !attempt.quiz_v2) || archived(attempt)) dirty.delete(id);
    }
    for(const id of [...dirty].sort((a,b)=>Number(!!state.attempts[a].practice)-Number(!!state.attempts[b].practice)||state.attempts[a].started_at.localeCompare(state.attempts[b].started_at))){
      const t=state.attempts[id];
      try {
        if(t.quiz_v2&&t.practice){
          const {error}=await bounded(client.from('quiz_practice_v2').upsert({user_id:userId,attempt_id:id,payload:t},{onConflict:'user_id,attempt_id'}));
          if(error)throw error;
        } else {
          const keys=t.quiz_v2
            ? ['attempt_id','assessment_id','content_version','spec','title','diagnostic','seed','presented','responses','position']
            : ['attempt_id','assessment_id','content_version','seed','presented','responses','position'];
          const payload=Object.fromEntries(keys.map(k=>[k,t[k]??null]));
          const rpcName=t.quiz_v2?'save_quiz_v2_attempt':'save_quiz_attempt';
          const {data,error}=await bounded(client.rpc(rpcName,{p_attempt:payload,p_submit:Boolean(t.submitted_at)}));
          if (error?.code === '22023' && error.message === 'Unknown published assessment version') {
            t.retired = true;
            dirty.delete(id);
            write();
            continue;
          }
          if(error)throw error;
          if(!data)throw Error(pendingStatus);
          if(t.submitted_at&&data.correct!==gradeAttempt(bank,t).correct){
            status='Server score verification differs; retry account sync before relying on shared XP.';
            continue;
          }
          t.server_awarded=data.earned||0;
          awards[id]=t.server_awarded;
          if(data.submitted_at)t.submitted_at=data.submitted_at;
        }
        t.synced=true;
        dirty.delete(id);
        write();
      } catch (error) {
        status=error?.message?.startsWith('Account sync timed out')?error.message:pendingStatus;
        // A rejected record stays local. Other attempts may still be valid.
        const rejectedAttempt=['22023','23503','23505','23514','P0001'].includes(error?.code);
        const practiceUnavailable=t.practice&&['42501','42P01','PGRST205'].includes(error?.code);
        if (!rejectedAttempt && !practiceUnavailable) {
          retryAfter=Date.now()+30000;
          return awards;
        }
      }
    }
    retryAfter=0;
    status=dirty.size||readFailed?pendingStatus:'Synced to your account';
    return awards;
  }
  async function transact(fn){
    const run=async()=>{read();const result=fn();write();const awards=Date.now()>=retryAfter||Object.hasOwn(result||{},'earned')?await sync():{};
      if (result && Object.hasOwn(awards, result.attempt_id)) result.earned = awards[result.attempt_id];
      if (result && state.attempts[result.attempt_id]?.retired && Object.hasOwn(result, 'earned')) result.earned = 0;
      return result;};
    return serial(run);
  }
  read();for(const t of Object.values(state.attempts))if((!t.practice||t.quiz_v2)&&!t.synced)dirty.add(t.attempt_id);
  return {
    get attempts(){return state.attempts;},get status(){return status;},
    draft(assessment){const t=state.attempts[state.drafts[quizKey(assessment)]];return t&&!t.submitted_at&&!archived(t)?t:null;},
    isArchived: archived,
    summary(assessment){return summaryFor(bank,state.attempts,assessment);},
    load(){return serial(async()=>{
      if(!client||userId==='guest')return;
      read();
      const results=await Promise.allSettled([
        bounded(client.from('quiz_attempts_v1').select('attempt_id,assessment_id,content_version,seed,presented,responses,position,started_at,submitted_at,correct')),
        bounded(client.from('quiz_attempts_v2').select('attempt_id,assessment_id,content_version,spec,title,diagnostic,seed,presented,responses,position,started_at,submitted_at,correct')),
        bounded(client.from('quiz_practice_v2').select('payload')),
      ]);
      const [v1Rows,v2Rows,practiceRows]=results.map(result=>result.value?.data||[]);
      const readFailed=results.some(result=>result.status==='rejected'||result.value?.error);
      const previouslyPending=Object.values(state.attempts).some(t=>t.submitted_at&&!t.synced&&!t.practice&&!t.retired);
         for(const row of v1Rows.sort((a,b)=>a.started_at.localeCompare(b.started_at))){
          const old=state.attempts[row.attempt_id];
          if(!old||row.submitted_at)state.attempts[row.attempt_id]={...row,practice:false,synced:true,...(old?.flagged?.length?{flagged:old.flagged}:{})};
          if (row.submitted_at) dirty.delete(row.attempt_id);
          if (archived(state.attempts[row.attempt_id])) continue;
          const draft=state.attempts[state.drafts[quizKey(row)]];
          if(row.submitted_at&&draft?.attempt_id===row.attempt_id)delete state.drafts[quizKey(row)];
          else if(!row.submitted_at&&(!draft||draft.submitted_at||row.started_at>draft.started_at))state.drafts[quizKey(row)]=row.attempt_id;
         }
         for(const row of v2Rows.sort((a,b)=>a.started_at.localeCompare(b.started_at))){
           const restored={...row,quiz_v2:true,practice:false,xp_policy:'verified-v2',assessment_contract:'quiz-v2-formal-1',includes_unreviewed:false,synced:true};
           if(!canReviewAttempt(bank,restored))continue;
           const old=state.attempts[restored.attempt_id];
           if(!old||old.synced||restored.submitted_at){state.attempts[restored.attempt_id]={...restored,...(old?.flagged?.length?{flagged:old.flagged}:{})};dirty.delete(restored.attempt_id);}
           const t=state.attempts[restored.attempt_id];
           if(t.submitted_at){if(state.drafts[quizKey(t)]===t.attempt_id)delete state.drafts[quizKey(t)];}
           else{
             const draft=state.attempts[state.drafts[quizKey(t)]];
             if(!draft||draft.submitted_at||draft.started_at<t.started_at)state.drafts[quizKey(t)]=t.attempt_id;
           }
         }
         for(const {payload} of practiceRows){
           if(!payload?.quiz_v2||!payload.practice||!canReviewAttempt(bank,payload))continue;
           const old=state.attempts[payload.attempt_id];
           if(!old||old.synced||payload.submitted_at){state.attempts[payload.attempt_id]={...payload,synced:true};dirty.delete(payload.attempt_id);}
           const t=state.attempts[payload.attempt_id];
           if(t.submitted_at){if(state.drafts[quizKey(t)]===t.attempt_id)delete state.drafts[quizKey(t)];}
           else {
             const draft=state.attempts[state.drafts[quizKey(t)]];
             if(!draft||draft.submitted_at||draft.started_at<t.started_at)state.drafts[quizKey(t)]=t.attempt_id;
           }
         }
      write();
      await sync(readFailed);
      return {syncedProgress:previouslyPending && Object.values(state.attempts).some(t=>t.submitted_at&&t.synced&&!t.practice)};
    });},
     start(assessment,seed){return transact(()=>{const t=makeAttempt(bank,assessment,seed);state.attempts[t.attempt_id]=t;state.drafts[quizKey(t)]=t.attempt_id;dirty.add(t.attempt_id);return t;});},
     startV2(curriculum,spec,seed){return transact(()=>{const published=publishedBlueprint(bank,curriculum,spec);const t=published?makeAttempt(bank,published,seed):makeV2Attempt(bank,curriculum,spec,state.attempts,seed);state.attempts[t.attempt_id]=t;state.drafts[quizKey(t)]=t.attempt_id;dirty.add(t.attempt_id);return t;});},
    practice(seed){return transact(()=>{const t=reinforcement(bank,state.attempts,seed);state.attempts[t.attempt_id]=t;return t;});},
    answer(id,itemId,answer){return transact(()=>{const t=state.attempts[id];if(!t||t.submitted_at)throw Error('This attempt is read-only. Start a new attempt to retry.');
      const next={...t,synced:false,responses:{...t.responses,[itemId]:answer}};validateAttempt(bank,next);state.attempts[id]=next;dirty.add(id);return next;});},
    clearAnswer(id,itemId){return transact(()=>{const t=state.attempts[id];if(!t||t.submitted_at)throw Error('This attempt is read-only. Start a new attempt to retry.');
      const responses={...t.responses};delete responses[itemId];const next={...t,synced:false,responses};validateAttempt(bank,next);state.attempts[id]=next;dirty.add(id);return next;});},
    move(id,position){return transact(()=>{const t=state.attempts[id];if(!t||!Number.isInteger(position)||position<0||position>=t.presented.length)throw Error('Invalid question position');t.position=position;if(!t.submitted_at){t.synced=false;dirty.add(id);}return t;});},
    toggleFlag(id,itemId){return transact(()=>{const t=state.attempts[id];if(!t||t.submitted_at)throw Error('This attempt cannot be modified.');if(!t.presented.some(r=>r.item_id===itemId))throw Error('Unknown question.');const current=Array.isArray(t.flagged)?t.flagged:[];const flagged=current.includes(itemId)?current.filter(x=>x!==itemId):[...current,itemId];const next={...t,flagged};state.attempts[id]=next;return next;});},
    submit(id,{requireComplete=false}={}){return transact(()=>{const t=state.attempts[id];if(!t)throw Error('Unknown attempt');
      if(t.submitted_at)return {attempt_id:id,earned:0,grade:gradeAttempt(bank,t)};
      if(requireComplete&&itemsFor(bank,t).some(q=>!isResponseProvided(q,t.responses?.[q.item_id])))throw Error('Answer every question before submitting.');
      const a=bank.assessments.find(a=>quizKey(a)===quizKey(t))||{assessment_id:t.assessment_id,content_version:t.content_version};
      const before=t.practice?0:summaryFor(bank,state.attempts,a).xp_awarded;
      const grade=gradeAttempt(bank,t);if(t.quiz_v2)t.correct=grade.correct;t.submitted_at=new Date().toISOString();t.synced=false;dirty.add(id);delete state.drafts[quizKey(t)];
      return {attempt_id:id,earned:t.practice?0:Math.max(0,grade.target_xp-before),grade};});},
    retry(){return this.load();},
  };
}
