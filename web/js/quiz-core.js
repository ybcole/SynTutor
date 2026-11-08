// Deterministic assessment manifests and grading; independent of lesson progress.
export const quizKey = q => `${q.assessment_id}@${q.content_version}`;
export const itemKey = q => `${q.item_id}@${q.content_version}`;
export const targetXp = correct => {
  if (!Number.isInteger(correct) || correct < 0 || correct > 5) throw new Error('Score must be an integer from 0 to 5.');
  return Math.max(0,10-2*(5-correct));
};
export function rng(seed) { let x=seed>>>0;return ()=>{x=(1664525*x+1013904223)%4294967296;return x/4294967296;}; }
export function shuffled(values,random) {const a=[...values];for(let i=a.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
export function randomSeed() { return crypto.getRandomValues(new Uint32Array(1))[0]; }
export function reviewed(row) { return row?.review_status==='INDEPENDENTLY_REVIEWED' && row.independent_review===true && Boolean(row.reviewed_by && row.reviewed_on); }
export function validateBank(bank) {
  if(bank?.schema_version!=='1.0.0'||!bank.items?.length||!bank.assessments?.length)throw new Error('Invalid assessment bank.');
  const sources=new Map(bank.sources.map(s=>[s.id,s]));
  if(sources.size!==bank.sources.length)throw new Error('Duplicate quiz sources.');
  const ids=new Set(),assessments=new Set();
  for(const q of bank.items){
    if(ids.has(itemKey(q))||!reviewed(q)||q.publication_status!=='published')throw new Error('Unreviewed/duplicate quiz item.');ids.add(itemKey(q));
    if(!q.source_ids?.length||q.source_ids.some(id=>{const s=sources.get(id);return !s||!reviewed(s)||s.status!=='approved'||!s.title||!s.edition||!Number.isInteger(s.printed_page)||s.printed_page<1||!['resolved','compatible'].includes(s.crosswalk_status);}))throw new Error('Missing reviewed quiz source.');
    if(q.claim_scope==='grammaticality_constraint')throw new Error('No production grammaticality constraint is enabled for these assessments.');
    if(!q.rationale||!q.outcome_ids?.length||!q.concept_ids?.length||q.options.length<2||new Set(q.options.map(o=>o.id)).size!==q.options.length||!q.options.every(o=>o.text&&o.rationale)||!q.options.some(o=>o.id===q.answer))throw new Error('Incomplete quiz answer contract.');
  }
  for(const a of bank.assessments){
    if(assessments.has(quizKey(a))||!reviewed(a)||a.pool_ids.length!==5||new Set(a.pool_ids).size!==5)throw new Error('Invalid five-item blueprint.');assessments.add(quizKey(a));
    for(const pool of a.pool_ids){const items=bank.items.filter(i=>i.pool_id===pool&&i.content_version===a.item_version);if(items.length<2)throw new Error('Missing equivalent question variants.');}
  }
  return bank;
}
export function makeAttempt(bank,assessment,seed=randomSeed(),id=crypto.randomUUID()) {
  if(!Number.isInteger(seed)||seed<0||seed>4294967295)throw new Error('Invalid seed.');
  const random=rng(seed);
  const selection=assessment.pool_ids.map(pool=>{const variants=bank.items.filter(i=>i.pool_id===pool&&i.content_version===assessment.item_version).sort((a,b)=>a.item_id.localeCompare(b.item_id));return variants[Math.floor(random()*variants.length)];});
  return {attempt_id:id,assessment_id:assessment.assessment_id,content_version:assessment.content_version,seed,
    presented:shuffled(selection,random).map(q=>({item_id:q.item_id,content_version:q.content_version,option_order:shuffled(q.options.map(o=>o.id),random)})),
    responses:{},position:0,started_at:new Date().toISOString(),submitted_at:null,practice:false};
}
export function itemsFor(bank,attempt) {
  return attempt.presented.map(ref=>{const q=bank.items.find(q=>q.item_id===ref.item_id&&q.content_version===ref.content_version);if(!q)throw new Error('Assessment content version is unavailable.');return q;});
}
export function validateAttempt(bank,attempt) {
  if(!attempt||!Array.isArray(attempt.presented)||attempt.presented.length!==5||new Set(attempt.presented.map(r=>r.item_id)).size!==5)throw new Error('Exactly five distinct question versions are required.');
  const items=itemsFor(bank,attempt);
  if(!attempt.practice){
    const a=bank.assessments.find(a=>quizKey(a)===quizKey(attempt));if(!a)throw new Error('Unknown assessment version.');
    const expected=makeAttempt(bank,a,attempt.seed,attempt.attempt_id).presented;
    // The full deterministic order is preserved for review and reload.
    if (expected.some((ref, index) => {
      const actual = attempt.presented[index];
      return itemKey(ref) !== itemKey(actual)
        || JSON.stringify(ref.option_order) !== JSON.stringify(actual.option_order);
    })) throw new Error('Assessment manifest does not match its seed/blueprint.');
  }
  for(let i=0;i<items.length;i++){
    const order=attempt.presented[i].option_order;
    if(!Array.isArray(order)||new Set(order).size!==order.length||order.length!==items[i].options.length||order.some(id=>!items[i].options.some(o=>o.id===id)))throw new Error('Invalid option ordering.');
  }
  if(!attempt.responses||typeof attempt.responses!=='object'||Array.isArray(attempt.responses)||Object.keys(attempt.responses).some(id=>!items.some(q=>q.item_id===id)))throw new Error('Unexpected answer IDs.');
  for(const q of items)if(attempt.responses[q.item_id]!=null&&!q.options.some(o=>o.id===attempt.responses[q.item_id]))throw new Error('Unknown answer.');
  if(!Number.isInteger(attempt.position)||attempt.position<0||attempt.position>4)throw new Error('Invalid question position.');
  return items;
}
export function canReviewAttempt(bank, attempt) {
  try {
    validateAttempt(bank, attempt);
    return true;
  } catch {
    return false;
  }
}
export function gradeAttempt(bank,attempt) {
  const items=validateAttempt(bank,attempt);
  const results=items.map(q=>({item_id:q.item_id,content_version:q.content_version,pool_id:q.pool_id,lesson_id:q.lesson_id,concept_ids:q.concept_ids,outcome_ids:q.outcome_ids,
    response:attempt.responses[q.item_id]??null,answer:q.answer,correct:attempt.responses[q.item_id]===q.answer}));
  const correct=results.filter(r=>r.correct).length;
  return {correct,incorrect:5-correct,target_xp:attempt.practice?0:targetXp(correct),results};
}
export function summaryFor(bank,attempts,assessment) {
  const rows=Object.values(attempts).filter(t=>!t.practice&&!t.retired&&t.submitted_at&&quizKey(t)===quizKey(assessment)&&canReviewAttempt(bank,t));
  const graded=rows.map(t=>({t,g:gradeAttempt(bank,t)})).sort((a,b)=>a.t.submitted_at.localeCompare(b.t.submitted_at)||a.t.attempt_id.localeCompare(b.t.attempt_id));
  return {attempt_count:rows.length,best_score:Math.max(0,...graded.map(r=>r.g.correct)),last_score:graded.at(-1)?.g.correct??null,last_completed_at:graded.at(-1)?.t.submitted_at??null,
    xp_awarded:Math.max(0,...graded.map(r=>r.g.target_xp))};
}
export function reinforcement(bank,attempts,seed=randomSeed()) {
  const mistakes=new Map();
  for(const t of Object.values(attempts).filter(t=>!t.retired&&t.submitted_at&&canReviewAttempt(bank,t)).sort((a,b)=>a.submitted_at.localeCompare(b.submitted_at)))for(const r of gradeAttempt(bank,t).results){
    const old=mistakes.get(r.pool_id)||{count:0,last:null};old.count+=r.correct?0:1;old.last=r.item_id;mistakes.set(r.pool_id,old);
  }
  const pools=[...mistakes].filter(([,v])=>v.count).sort((a,b)=>b[1].count-a[1].count).map(([id])=>id);
  for(const q of bank.items)if(!pools.includes(q.pool_id))pools.push(q.pool_id);
  const pseudo={assessment_id:'reinforcement',content_version:'1.0.0',item_version:'1.0.0',pool_ids:pools.slice(0,5)};
  const t=makeAttempt(bank,pseudo,seed);t.practice=true;
  t.presented=t.presented.map(ref=>{const variants=bank.items.filter(q=>q.pool_id===bank.items.find(q=>q.item_id===ref.item_id).pool_id);const other=variants.find(q=>q.item_id!==mistakes.get(q.pool_id)?.last);return other?{...ref,item_id:other.item_id}:ref;});
  return t;
}
