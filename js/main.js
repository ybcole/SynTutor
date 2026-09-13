import { TreeRenderer } from './renderer.js';
import {
  log,
  clearOverlay, showCanvasMessage, renderSentenceVerdict, renderNodeDetail,
  renderDiagnostic, fillDevPanel, applySentenceSelection, plainName,
} from './ui.js';
const STATES = { IDLE: 'IDLE', PROCESSING: 'PROCESSING', VIEWING: 'VIEWING', EXPLORING: 'EXPLORING', END: 'END' };

let state = STATES.IDLE;
let session = null;
let renderer = null;
let lastAnalyzedText = null;

function transition(next, event) {
  const from = state;
  state = next;
  log(`FSM: ${from} \u2192 ${next} (${event})`);
}

export function boot() {
  renderer = new TreeRenderer(document.querySelector('#treeCanvas'), {
    onSelect: (id) => handleNodeSelect(id),
    onHover: () => {},
    describe: plainName,
  });
  wireEvents();
  transition(STATES.IDLE, 'system ready');
  log('SynTutor engine ready \u2014 full-stack pipeline: spaCy + benepar + rule matrix');
}

function wireEvents() {
  const ta = document.querySelector('#inputText');
  ta.addEventListener('dblclick', () => {
    ta.readOnly = false;
    ta.classList.add('editing');
    setEditHint(true);
    ta.focus();
  });
  ta.addEventListener('blur', () => {
    const changed = ta.value !== lastAnalyzedText;
    returnToLocked();
    if (changed) runPipeline();
  });
  ta.addEventListener('click', activateSentenceAtCaret);
  ta.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      runPipeline();
      return;
    }
    if (e.key === 'Enter' && ta.readOnly) {
      e.preventDefault();
      activateSentenceAtCaret();
    }
  });
}

function setEditHint(editing) {
  const hint = document.querySelector('#inputHint');
  hint.textContent = editing
    ? 'Editing \u2014 click away to lock and analyze.'
    : 'Locked \u2014 click any sentence to view its syntax tree. Double-click to edit.';
}

function returnToLocked() {
  const ta = document.querySelector('#inputText');
  ta.readOnly = true;
  ta.classList.remove('editing');
  setEditHint(false);
}

function activateSentenceAtCaret() {
  const ta = document.querySelector('#inputText');
  if (!session || ta.readOnly !== true) return;
  if (ta.selectionStart !== ta.selectionEnd) return;
  const sents = session.payload.parse.sentences || [];
  const caret = ta.selectionStart;
  const hit = sents.find((s) => caret >= s.start && caret < s.end);
  if (hit && hit.ordinal - 1 !== (session.payload.meta.target_sentence || 1) - 1) {
    runPipeline({ index: hit.ordinal - 1 });
  }
}

function failPipeline(title, lines) {
  showCanvasMessage('error', title, lines);
  renderSentenceVerdict([`\u{26D4} ${title}`, ...lines], true);
  renderDiagnostic(title, lines);
  transition(STATES.VIEWING, 'request failed -> diagnostic shown');
  log(`Request failed: ${title} \u2014 ${lines[0] || ''}`);
}

async function runPipeline(opts = {}) {
  if (state === STATES.PROCESSING) return;
  transition(STATES.PROCESSING, 'user submits text');
  await executePipeline(opts);
}

async function executePipeline(opts = {}) {
  clearOverlay();
  renderer.select(null);
  renderNodeDetail(null, null, null);

  const text = document.querySelector('#inputText').value.trim();
  if (!text) {
    showCanvasMessage('error', 'No analyzable sentence', ['Enter some English text first, then submit it.']);
    renderSentenceVerdict(['\u26D4 No analyzable sentence', 'Enter some English text first, then submit it.'], true);
    renderDiagnostic('No analyzable sentence', ['Enter some English text first, then submit it.']);
    transition(STATES.IDLE, 'empty input -> back to idle');
    return;
  }
  log(`Stage 1: user input captured \u2014 ${JSON.stringify(text)}`);

  const body = { text };
  if (opts.index !== undefined && opts.index !== null) body.sentence_index = opts.index;
  const target = opts.index !== undefined && opts.index !== null ? `sentence #${opts.index + 1}` : 'first sentence';
  log(`Stage 2: POST /api/parse (target: ${target})`);
  let res;
  try {
    res = await fetch('/api/parse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  } catch (_e) {
    failPipeline('Backend unreachable', [
      'The SynTutor NLP server is not responding.',
      'Start it with:  python3 server/app.py',
    ]);
    return;
  }
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const title = res.status === 503
      ? 'NLP models unavailable'
      : res.status === 422 ? 'Unable to produce a parse' : `Backend error (HTTP ${res.status})`;
    const lines = [data.error || 'The backend rejected the request.', data.hint || ''].filter(Boolean);
    failPipeline(title, lines);
    return;
  }
  const payload = await res.json();
  fillDevPanel(payload);
  log(`Stage 2: payload received (${Object.keys(payload.nodes).length} nodes) \u00b7 ${payload.meta.backend}`);

  const tokens = payload.parse.tokens;
  const posInfo = tokens.map((t) => `${t.t}/${t.pos}`).join(' ');
  log(`Stage 3: spaCy tokenization + POS \u2014 ${posInfo}`);
  if (payload.meta.sentence_count > 1) {
    log(`Stage 3: ${payload.meta.sentence_count} sentence(s) detected \u2014 analyzing sentence ${payload.meta.target_sentence} (deterministic policy)`);
  }

  log(`Stage 4: benepar parse string \u2014 ${payload.parse.parse_string}`);

  applyStatuses(payload.tree, payload.node_details);
  const s = payload.summary;
  log(`Stage 5: rule-matrix validation \u2014 ${s.valid_edges} valid / ${s.violated_edges} violated / ${s.unrated_edges} unrated \u00b7 fired ${JSON.stringify(s.constraints_fired)}`);

  renderSentenceVerdict(payload.explainers.basic.split('\n'), !payload.summary.valid);
  log(`Stage 6: explanations generated \u2014 basic + ${payload.explainers.contrastive ? 'contrastive' : '(none)'}`);

  session = { payload };
  lastAnalyzedText = text;
  document.querySelector('#inputText').value = text;
  lockInput();
  applySentenceSelection(payload);
  renderer.setTree(payload.tree);
  transition(STATES.VIEWING, 'output ready -> viewing');
  log('Stage 7: syntax tree rendered \u2014 Interaction Loop active (node details cached in session)');
}

function lockInput() {
  const ta = document.querySelector('#inputText');
  ta.readOnly = true;
  ta.classList.remove('editing');
  setEditHint(false);
  ta.blur();
}

function applyStatuses(tree, details) {
  const walk = (node) => {
    const d = details[node.id];
    node.edgeResult = { status: d ? d.status : 'valid' };
    for (const c of node.children || []) walk(c);
  };
  walk(tree);
  return tree;
}

function handleNodeSelect(id) {
  if (!id || !session) {
    if (session) {
      renderer.select(null);
      transition(STATES.VIEWING, 'selection cleared');
    }
    return;
  }
  const detail = session.payload.node_details[id];
  const node = session.payload.nodes[id];
  if (!node || !detail) return;
  renderNodeDetail(session, detail, node);
  renderer.select(id);
  if (state !== STATES.PROCESSING) {
    transition(STATES.EXPLORING, 'user selects syntax node (cache hit \u2014 no HTTP request)');
    log(`Exploring: cached XAI for node ${node.type} \u2014 ${detail.constraint} (${detail.status})`);
  }
}

if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', () => boot());
}