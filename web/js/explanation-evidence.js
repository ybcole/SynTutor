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

// XAI-3 observations have fact-atom proofs, not new book authority.
// All text, including user-supplied words, is inserted as text (never HTML).
function renderContextualObservations(evidence, panel) {
  const context = evidence?.contextual_explanations;
  if (!context || !Array.isArray(context.items) || context.status === 'unavailable') return;
  const section = document.createElement('section');
  section.dataset.xaiContext = '';
  const heading = document.createElement('h3');
  heading.textContent = 'In this sentence';
  section.append(heading);
  if (context.items.length !== 1) {
    const message = document.createElement('p');
    message.textContent = context.items.length
      ? context.items.length + ' tree positions have contextual observations. Select a node or word to inspect its own evidence.'
      : 'No tree position was available for a contextual explanation.';
    section.append(message);
  } else {
    const item = context.items[0];
    const status = document.createElement('p');
    status.dataset.xaiStatus = '';
    status.textContent = item.uncertainty === 'provisional'
      ? 'Provisional tree observation — this analysis is not yet resolved.'
      : 'Structural observation — not a grammaticality judgment.';
    const short = document.createElement('p');
    short.dataset.xaiShort = '';
    short.textContent = item.short;
    section.append(status, short);
    const more = document.createElement('details');
    more.dataset.xaiDetails = '';
    const summary = document.createElement('summary');
    summary.textContent = 'Why this is shown';
    const deep = document.createElement('p');
    deep.dataset.xaiDeep = '';
    deep.textContent = item.deep;
    more.append(summary, deep);
    if (Array.isArray(item.proof) && item.proof.length) {
      const proof = document.createElement('p');
      proof.textContent = 'Observed tree evidence: '
        + item.proof.map(fact => fact.predicate + ' (' + fact.fact_id + ', ' + fact.proof_path + ')').join('; ') + '.';
      more.append(proof);
    }
    section.append(more);
  }
  panel.append(section);
}

// XAI-4 reports authorization status, never unchecked "incorrect" labels.
// Candidate matched words are not displayed as error diagnoses.
function renderCambridgePartial(evidence, panel) {
  const xai = evidence?.xai4_partial_evaluation;
  if (!xai || !Array.isArray(xai.evaluations)) return;
  const area = document.createElement('details');
  area.dataset.xai4Partial = '';
  const title = document.createElement('summary');
  title.textContent = 'Cambridge grammar checks: '
    + xai.enabled_rule_ids.length + ' approved runtime rules';
  area.append(title);
  const scope = document.createElement('p');
  scope.textContent = 'This is a partial check, not a sentence grammaticality verdict. '
    + 'Blocked candidates cannot issue verified errors; unmatched conditions are not grammar passes.';
  area.append(scope);
  if (!xai.enabled_rule_ids.length) {
    const message = document.createElement('p');
    message.textContent = 'Independent source, exception, crosswalk and linguistic review is still required. '
      + 'No new Cambridge error diagnosis is asserted.';
    area.append(message);
  }
  for (const check of xai.evaluations) {
    if (check.status === 'NOT_APPLICABLE') continue;
    const row = document.createElement('p');
    row.textContent = check.rule_id + ': ' + check.status + '. '
      + (check.status === 'BLOCKED'
        ? 'Potential construction observed, but it is not approved as an error check.'
        : check.status === 'AMBIGUOUS'
          ? 'Interpretation or exception requires further evidence.'
          : check.reason);
    area.append(row);
  }
  panel.append(area);
}

// XAI-5: compare learner-authored revisions without automatic correction.
function renderRepairRecheck(evidence, panel) {
  const data = evidence?.xai5_localization;
  if (!data || typeof data.original_sentence !== 'string' || !data.original_sentence.trim()) return;
  const section = document.createElement('details');
  section.dataset.xai5Repair = '';
  const heading = document.createElement('summary');
  heading.textContent = 'Compare a revised sentence';
  section.append(heading);
  const warning = document.createElement('p');
  warning.textContent = 'Comparisons reparse your edit and rerun available checks. '
    + 'No change is automatically applied or certified as fully grammatical.';
  section.append(warning);
  const count = document.createElement('p');
  count.dataset.xai5Count = '';
  count.textContent = data.diagnoses.length + ' approved original findings; '
    + data.observations.filter(item => item.authority === 'UNAPPROVED_CANDIDATE').length
    + ' unapproved token observations.';
  section.append(count);
  const chosen = evidence?.fact_graph?.target?.node_id;
  const related = (data.observations || []).filter(item => {
    const at = [item.governor_location, item.target_location];
    return !chosen || at.some(row => row?.node_id === chosen || row?.ancestor_node_ids?.includes(chosen));
  }).slice(0, 4);
  for (const item of related) {
    const note = document.createElement('p');
    note.textContent = item.authority === 'APPROVED_CHECK'
      ? item.rule_id + ': ' + item.governor_text + ' → ' + item.target_text + ' (' + item.status + '). Local reviewed check.'
      : 'Possible ' + item.governor_text + ' → ' + item.target_text + ': ' + item.status
        + '. Unapproved observation; not a diagnosed error.';
    section.append(note);
  }
  const label = document.createElement('label');
  label.textContent = 'Your revised sentence';
  const field = document.createElement('textarea');
  field.rows = 2;
  field.maxLength = 1200;
  field.value = data.original_sentence;
  field.setAttribute('aria-label', 'Your revised sentence');
  label.append(field);
  section.append(label);
  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = 'Reparse and compare this revision';
  const output = document.createElement('div');
  output.dataset.xai5Result = '';
  output.setAttribute('role', 'status');
  button.addEventListener('click', async () => {
    if (button.disabled) return;
    const revised = field.value;
    if (!revised.trim() || revised === data.original_sentence) {
      output.textContent = 'Enter a different nonempty sentence to compare.';
      return;
    }
    button.disabled = true;
    output.textContent = 'Rechecking the revised sentence…';
    try {
      const response = await fetch('/api/repair-check', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          text: data.original_sentence,
          candidates: [{text: revised}],
        }),
      });
      const checked = await response.json();
      if (!response.ok) throw new Error(checked.error || 'Revision recheck unavailable');
      if (!section.isConnected) return;
      output.replaceChildren();
      const revision = checked.revisions[0];
      const summary = document.createElement('p');
      summary.textContent = 'Revision ' + revision.version_id + ': '
        + revision.snapshot.analysis_status + ' tree analysis; '
        + revision.original_finding_lineage.length + ' reviewed original findings rechecked. '
        + 'This does not certify the whole sentence.';
      output.append(summary);
      for (const row of revision.original_finding_lineage) {
        const item = document.createElement('p');
        item.textContent = row.original_finding_id + ' (' + row.rule_id + '): ' + row.outcome + '.';
        output.append(item);
      }
      if (!checked.diagnostic_rule_count) {
        const note = document.createElement('p');
        note.textContent = 'No independently approved Cambridge diagnostic rules are enabled. '
          + 'This comparison cannot verify that a grammar error was fixed.';
        output.append(note);
      }
      for (const finding of revision.new_findings) {
        const item = document.createElement('p');
        const origin = finding.origin === 'introduced' ? 'locally introduced by the aligned edit'
          : finding.origin === 'unmasked' ? 'newly visible after an ambiguity was removed'
          : 'origin not established';
        item.textContent = 'Additional narrow check ' + finding.rule_id + ': '
          + origin + '. No whole-sentence correction claim.';
        output.append(item);
      }
      // A candidate tree is *newly parsed*, not a re-labelled original.
      // Users can inspect its actual constituent nodes and rerun the same
      // evidence composer on the selected revised-tree node.
      const revisedTree = revision.snapshot.canonical_tree;
      if (revisedTree) {
        const treeDetails = document.createElement('details');
        treeDetails.dataset.xai5RevisedTree = '';
        const heading = document.createElement('summary');
        heading.textContent = 'Inspect revised B-R tree';
        treeDetails.append(heading);
        const { renderLessonTree } = await import('./lessons-ui.js');
        if (!section.isConnected) return;
        const treeView = renderLessonTree(revisedTree, {interactive: true});
        treeView.addEventListener('click', async (event) => {
          const target = event.target.closest?.('button[data-node-id]');
          if (!target || !treeView.contains(target)) return;
          const nodeId = target.dataset.nodeId;
          const details = document.createElement('section');
          details.dataset.xai5RevisedNode = '';
          details.textContent = 'Checking the selected revised-tree node…';
          treeDetails.querySelector('[data-xai5-revised-node]')?.remove();
          treeDetails.append(details);
          try {
            const selected = await requestEvidence(revisedTree, nodeId);
            if (details.isConnected) renderEvidence(selected, details);
          } catch (error) {
            if (details.isConnected) details.textContent = error.message || 'Node evidence unavailable.';
          }
        });
        treeDetails.append(treeView);
        output.append(treeDetails);
      } else {
        const missing = document.createElement('p');
        missing.textContent = 'No complete canonical B-R tree was established for this revised sentence; the original tree is not reused.';
        output.append(missing);
      }
    } catch (error) {
      if (section.isConnected) output.textContent = error.message || 'Revision recheck unavailable.';
    } finally {
      button.disabled = false;
    }
  });
  section.append(button, output);
  panel.append(section);
}

export function renderEvidence(evidence, host = document.querySelector('#explainNode')) {
  if (!host) return;
  host.querySelector('[data-shared-evidence]')?.remove();
  const panel = document.createElement('section');
  panel.dataset.sharedEvidence = '';
  panel.setAttribute('aria-live', 'polite');
  const title = document.createElement('h3');
  title.textContent = 'Book evidence';
  renderContextualObservations(evidence, panel);
  renderCambridgePartial(evidence, panel);
  renderRepairRecheck(evidence, panel);
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
