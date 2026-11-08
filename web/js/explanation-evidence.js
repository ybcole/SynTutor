// One request contract and one evidence renderer for Generator and Builder.
import { API_BASE } from './config.js';

export async function requestEvidence(tree, nodeId = null, options = {}) {
  const body = { tree: tree || null };
  if (nodeId !== null) body.node_id = nodeId;
  if (options.variety) body.variety = options.variety;
  const response = await (options.fetch || fetch)(`${API_BASE}/api/explain`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body), signal: options.signal,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Explanation unavailable');
  return data;
}

export function evidenceLines(evidence) {
  if (!evidence) return ['Explanation unavailable.'];
  const messages = {
    NO_BOOK_BASIS: 'No reviewed book evidence is available for this analysis.',
    ANALYSIS_UNRESOLVED: 'The analysis is unresolved. No grammatical explanation is asserted.',
    SOURCE_CONFLICT: 'The sources conflict. Conflicting claims are withheld.',
    EXPLAINED: 'Explanation from reviewed book evidence.',
  };
  return [messages[evidence.status] || 'Explanation unavailable.',
    ...(evidence.diagnostics || []).map(row => row.message)];
}

export function renderEvidence(evidence, host = document.querySelector('#explainNode')) {
  if (!host) return;
  host.querySelector('[data-shared-evidence]')?.remove();
  const panel = document.createElement('section');
  panel.dataset.sharedEvidence = '';
  panel.setAttribute('aria-live', 'polite');
  const title = document.createElement('h3');
  title.textContent = 'Book evidence';
  panel.append(title);
  for (const line of evidenceLines(evidence)) {
    const p = document.createElement('p'); p.textContent = line; panel.append(p);
  }
  for (const [channel, items] of Object.entries(evidence?.channels || {})) {
    if (!items.length) continue;
    const h = document.createElement('h4');
    h.textContent = ({ structural: 'B-R structure', grammatical: 'Cambridge grammar', remediation: 'Feedback' })[channel] || channel;
    panel.append(h);
    for (const item of items) {
      const p = document.createElement('p'); p.textContent = item.text; panel.append(p);
      for (const source of item.sources || []) {
        const cite = document.createElement('small');
        cite.textContent = `${source.title}, ${source.edition}, p. ${source.printed_page} [${source.id}]`;
        panel.append(cite);
      }
      if (item.deep_text) {
        const more = document.createElement('details');
        const summary = document.createElement('summary'); summary.textContent = 'More detail';
        const deep = document.createElement('p'); deep.textContent = item.deep_text;
        more.append(summary, deep); panel.append(more);
      }
    }
  }
  host.append(panel);
}

const QUIZ_SOURCE_FIELDS = ['id','book','title','edition','printed_page','evidence_status','status','crosswalk_status','review_status','independent_review','reviewed_by','reviewed_on'];
// Controlled feedback for the reviewed standalone bank. This same response
// shape and source boundary is used by the server composer and M3 renderer.
export function composeQuizEvidence(item, answer, bank) {
  const output={schema_version:'1.0.0',status:'NO_BOOK_BASIS',analysis_status:'quiz_feedback',channels:{structural:[],grammatical:[],remediation:[]},facts:[],diagnostics:[]};
  const reviewed=r=>r?.review_status==='INDEPENDENTLY_REVIEWED'&&r.independent_review===true&&Boolean(r.reviewed_by)&&/^\d{4}-\d{2}-\d{2}$/.test(r.reviewed_on);
  const sources=(item.source_ids||[]).map(id=>bank.sources.find(s=>s.id===id));
  const required=item.claim_scope==='br_structure'?'B-R':item.claim_scope==='cambridge_classification'?'Cambridge':null;
  if(!required||!reviewed(item)||!sources.length||new Set(bank.sources.map(s=>s.id)).size!==bank.sources.length||sources.some(s=>!s||!reviewed(s)||s.book!==required||s.status!=='approved'||!s.title||!s.edition||!Number.isInteger(s.printed_page)||s.printed_page<1||!['IMG','TXT'].includes(s.evidence_status)||!['resolved','compatible'].includes(s.crosswalk_status))){output.diagnostics.push({code:'NO_BOOK_BASIS',message:'This question lacks eligible reviewed evidence.'});return output;}
  const chosen=item.options.find(o=>o.id===answer),correct=item.options.find(o=>o.id===item.answer);
  if(answer!==null&&answer!==undefined&&!chosen)throw new Error('Unknown quiz answer.');
  if(!correct||!item.rationale||!item.options.every(o=>o.rationale))return output;
  const facts={item_id:item.item_id,item_version:item.content_version,answer_id:answer??null,correct_answer_id:item.answer,response_status:answer===item.answer?'correct':chosen?'incorrect':'unanswered',claim_scope:item.claim_scope};
  const channel=required==='B-R'?'structural':'grammatical';
  output.channels[channel].push({template_id:`quiz:${item.item_id}@${item.content_version}`,node_id:`quiz:${item.item_id}`,
    text:`Correct answer: ${correct.text}. ${item.rationale}`,deep_text:chosen?`Your selected option: ${chosen.rationale}`:'No answer was submitted; it counts as incorrect.',
    sources:sources.map(s=>Object.fromEntries(QUIZ_SOURCE_FIELDS.map(k=>[k,s[k]]))),facts});
  output.facts=[facts];output.status='EXPLAINED';return output;
}
export async function requestQuizEvidence(item,answer,options={}) {
  const response=await (options.fetch||fetch)(`${API_BASE}/api/explain`,{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({quiz_item_id:item.item_id,quiz_item_version:item.content_version,answer_id:answer??null}),signal:options.signal});
  const data=await response.json();if(!response.ok)throw new Error(data.error||'Quiz evidence unavailable');return data;
}
