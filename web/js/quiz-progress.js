import { makeAttempt,validateAttempt,gradeAttempt,summaryFor,quizKey,reinforcement } from './quiz-core.js';
export function createQuizStore(bank,{storage,userId='guest',client=null,timeoutMs=5000}={}) {
  const key=`syntutor:assessments:v1:${userId}`;
  let state={attempts:{},drafts:{}},status='Saved on this device',blocked=false,queue=Promise.resolve();
  const dirty=new Set();
  function read(){
    if(!storage){status='Progress storage unavailable; keep this page open';return;}
    try{const saved=JSON.parse(storage.getItem(key)||'null');if(saved&&saved.attempts&&saved.drafts)state=saved;}catch{status='Progress storage unavailable; keep this page open';}
  }
  function write(){try{storage?.setItem(key,JSON.stringify(state));}catch{status='Progress storage unavailable; keep this page open';}}
  async function bounded(request){let timer;const controller=new AbortController();const job=typeof request.abortSignal==='function'?request.abortSignal(controller.signal):request;
    try{return await Promise.race([job,new Promise((_r,reject)=>{timer=setTimeout(()=>{controller.abort();reject(Error('Account sync timed out; attempts remain saved on this device.'));},timeoutMs);})]);}finally{clearTimeout(timer);}}
  async function sync(){
    if(!client||userId==='guest')return {};
    const awards={};
    for(const id of [...dirty].sort((a,b)=>state.attempts[a].started_at.localeCompare(state.attempts[b].started_at))){
      const t=state.attempts[id];if(t.practice){dirty.delete(id);continue;}
      const payload=Object.fromEntries(['attempt_id','assessment_id','content_version','seed','presented','responses','position'].map(k=>[k,t[k]]));
      const {data,error}=await bounded(client.rpc('save_quiz_attempt',{p_attempt:payload,p_submit:Boolean(t.submitted_at)}));
      if(error)throw Error('Account sync unavailable; attempts remain saved on this device. Retry when connected.');
      if(data){
        if(t.submitted_at&&data.correct!==gradeAttempt(bank,t).correct)throw Error('Server score verification differs; retry account sync before relying on shared XP.');
        t.synced=true;t.server_awarded=data.earned||0;awards[id]=data.earned||0;
        if(data.submitted_at)t.submitted_at=data.submitted_at;
      }
      dirty.delete(id);
    }
    write();status='Synced to your account';return awards;
  }
  async function transact(fn){
    const run=async()=>{read();const result=fn();write();let awards={};try{if(!blocked)awards=await sync();}catch(e){blocked=true;status=e.message;}
      if(result&&Object.hasOwn(awards,result.attempt_id))result.earned=awards[result.attempt_id];return result;};
    const locked=()=>globalThis.navigator?.locks?.request?navigator.locks.request(key,run):run();queue=queue.catch(()=>{}).then(locked);return queue;
  }
  read();for(const t of Object.values(state.attempts))if(!t.practice&&!t.synced)dirty.add(t.attempt_id);
  return {
    get attempts(){return state.attempts;},get status(){return status;},
    draft(assessment){const t=state.attempts[state.drafts[quizKey(assessment)]];return t&&!t.submitted_at?t:null;},
    summary(assessment){return summaryFor(bank,state.attempts,assessment);},
    async load(){
      if(!client||userId==='guest')return;
      try{
        const {data,error}=await bounded(client.from('quiz_attempts_v1').select('attempt_id,assessment_id,content_version,seed,presented,responses,position,started_at,submitted_at'));
        if(error)throw error;
        for(const row of (data||[]).sort((a,b)=>a.started_at.localeCompare(b.started_at))){try{validateAttempt(bank,{...row,practice:false});}catch{continue;}
          const old=state.attempts[row.attempt_id];if(!old||row.submitted_at)state.attempts[row.attempt_id]={...row,practice:false,synced:true};
          const draft=state.attempts[state.drafts[quizKey(row)]];
          if(row.submitted_at&&draft?.attempt_id===row.attempt_id)delete state.drafts[quizKey(row)];
          else if(!row.submitted_at&&(!draft||draft.submitted_at||row.started_at>draft.started_at))state.drafts[quizKey(row)]=row.attempt_id;
        }
        write();await sync();
      }catch{blocked=true;status='Account sync unavailable; attempts remain saved on this device';}
    },
    start(assessment,seed){return transact(()=>{const t=makeAttempt(bank,assessment,seed);state.attempts[t.attempt_id]=t;state.drafts[quizKey(t)]=t.attempt_id;dirty.add(t.attempt_id);return t;});},
    practice(seed){return transact(()=>{const t=reinforcement(bank,state.attempts,seed);state.attempts[t.attempt_id]=t;return t;});},
    answer(id,itemId,answer){return transact(()=>{const t=state.attempts[id];if(!t||t.submitted_at)throw Error('This attempt is read-only. Start a new attempt to retry.');
      const next={...t,synced:false,responses:{...t.responses,[itemId]:answer}};validateAttempt(bank,next);state.attempts[id]=next;dirty.add(id);return next;});},
    move(id,position){return transact(()=>{const t=state.attempts[id];if(!t||!Number.isInteger(position)||position<0||position>4)throw Error('Invalid question position');t.position=position;if(!t.submitted_at){t.synced=false;dirty.add(id);}return t;});},
    submit(id){return transact(()=>{const t=state.attempts[id];if(!t)throw Error('Unknown attempt');
      if(t.submitted_at)return {attempt_id:id,earned:0,grade:gradeAttempt(bank,t)};
      const a=bank.assessments.find(a=>quizKey(a)===quizKey(t));const before=t.practice?0:summaryFor(bank,state.attempts,a).xp_awarded;
      const grade=gradeAttempt(bank,t);t.submitted_at=new Date().toISOString();t.synced=false;dirty.add(id);delete state.drafts[quizKey(t)];
      return {attempt_id:id,earned:t.practice?0:Math.max(0,grade.target_xp-before),grade};});},
    async retry(){blocked=false;await this.load();},
  };
}
