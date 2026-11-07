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
