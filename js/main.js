import { supabase } from './auth.js';
import { TreeRenderer } from './renderer.js';
import {
  log, clearOverlay, showCanvasMessage, renderSentenceVerdict, renderNodeDetail,
  renderDiagnostic, fillDevPanel, applySentenceSelection, plainName,
} from './ui.js';

const STATES = { IDLE: 'IDLE', PROCESSING: 'PROCESSING', VIEWING: 'VIEWING', EXPLORING: 'EXPLORING' };
const HIGHLIGHT_STATUSES = new Set(['valid', 'error']);
const HIGHLIGHT_CLASSES = { valid: 'word-valid', error: 'word-invalid' };

let state = STATES.IDLE;
let session = null;
let renderer = null;
let lastAnalyzedText = null;
let lastRecordedText = null;
let historySpans = [];
let cachedHistory = [];
let activeHistoryFilter = 'all';

const { data: { session: authSession } } = await supabase.auth.getSession();
if (!authSession) window.location.href = '/login.html';

supabase.auth.onAuthStateChange((event, currentSession) => {
  if (event === 'SIGNED_OUT' || !currentSession) window.location.href = '/login.html';
});

function transition(next, event) {
  const from = state;
  state = next;
  log(`FSM: ${from} -> ${next} (${event})`);
}

export function boot() {
  renderer = new TreeRenderer(document.querySelector('#treeCanvas'), {
    onSelect: handleNodeSelect, onHover: () => {}, describe: plainName,
  });
  wireEvents();
  transition(STATES.IDLE, 'system ready');
  log('SynTutor engine ready - full-stack pipeline: spaCy + benepar + rule matrix');
}

function wireEvents() {
  const ta = document.querySelector('#inputText');
  const editor = document.querySelector('.input-editor');
  ta.addEventListener('dblclick', () => {
    editor.classList.add('editing');
    ta.readOnly = false;
    ta.classList.add('editing');
    setEditHint(true);
    renderInputHighlights(ta.value);
    ta.focus();
  });
  ta.addEventListener('scroll', syncHighlightScroll);
  ta.addEventListener('input', () => {
    historySpans = [];
    renderInputHighlights(ta.value);
  });
  ta.addEventListener('blur', () => {
    const changed = ta.value !== lastAnalyzedText;
    returnToLocked();
    if (changed) {
      runPipeline();
    } else {
      renderInputHighlights(ta.value);
    }
  });
  ta.addEventListener('click', activateSentenceAtCaret);
  ta.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && (event.metaKey || event.ctrlKey)) {
      event.preventDefault();
      runPipeline();
    } else if (event.key === 'Enter' && ta.readOnly) {
      event.preventDefault();
      activateSentenceAtCaret();
    }
  });

  document.querySelector('#historyBtn')?.addEventListener('click', () => {
    document.querySelector('#historyDrawerBackdrop')?.classList.add('active');
    loadAndRenderHistory();
  });
  document.querySelector('#closeDrawerBtn')?.addEventListener('click', closeHistory);
  document.querySelector('#historyDrawerBackdrop')?.addEventListener('click', (event) => {
    if (event.target.id === 'historyDrawerBackdrop') closeHistory();
  });
  document.querySelectorAll('#historyFilters .filter-pill').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelectorAll('#historyFilters .filter-pill').forEach((item) => item.classList.remove('active'));
      button.classList.add('active');
      activeHistoryFilter = button.dataset.filter;
      renderHistoryItems();
    });
  });
  document.querySelector('#clearHistoryBtn')?.addEventListener('click', clearHistory);
  document.querySelector('#logoutBtn')?.addEventListener('click', () => supabase.auth.signOut());
}

function closeHistory() {
  document.querySelector('#historyDrawerBackdrop')?.classList.remove('active');
}

function setEditHint(editing) {
  document.querySelector('#inputHint').textContent = editing
    ? 'Editing - click away to lock and analyze.'
    : 'Locked - click any sentence to view its syntax tree. Double-click to edit.';
}

function returnToLocked() {
  const ta = document.querySelector('#inputText');
  ta.readOnly = true;
  ta.classList.remove('editing');
  document.querySelector('.input-editor').classList.remove('editing');
  setEditHint(false);
  renderInputHighlights(ta.value);
}

function activateSentenceAtCaret() {
  const ta = document.querySelector('#inputText');
  if (!session || !ta.readOnly || ta.selectionStart !== ta.selectionEnd) return;
  const hit = (session.payload.parse.sentences || []).find(
    (sentence) => ta.selectionStart >= sentence.start && ta.selectionStart < sentence.end,
  );
  const current = (session.payload.meta.target_sentence || 1) - 1;
  if (hit && hit.ordinal - 1 !== current) runPipeline({ index: hit.ordinal - 1, isSentenceNav: true });
}

async function runPipeline(options = {}) {
  if (state === STATES.PROCESSING) return;
  transition(STATES.PROCESSING, 'user submits text');
  await executePipeline(options);
}

async function executePipeline(options = {}) {
  clearOverlay();
  renderer.select(null);
  renderNodeDetail(null, null, null);
  const text = document.querySelector('#inputText').value.trim();
  if (!text) {
    renderInputHighlights('');
    showCanvasMessage('error', 'No analyzable sentence', ['Enter some English text first, then submit it.']);
    renderSentenceVerdict(['No analyzable sentence', 'Enter some English text first, then submit it.'], true);
    renderDiagnostic('No analyzable sentence', ['Enter some English text first, then submit it.']);
    transition(STATES.IDLE, 'empty input -> back to idle');
    return;
  }
  // Keep the source text visible through the asynchronous parse request.
  renderInputHighlights(text);

  let response;
  try {
    response = await fetch('/api/parse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, ...(options.index === undefined ? {} : { sentence_index: options.index }) }),
    });
  } catch (_error) {
    failPipeline('Backend unreachable', ['Start it with: python3 server/app.py']);
    return;
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    failPipeline(response.status === 503 ? 'NLP models unavailable' : 'Unable to produce a parse',
      [data.error || 'The backend rejected the request.', data.hint || ''].filter(Boolean));
    return;
  }

  const payload = await response.json();
  fillDevPanel(payload);
  applyStatuses(payload.tree, payload.node_details);
  renderSentenceVerdict(payload.explainers.basic.split('\n'), !payload.summary.valid);
  session = { payload };
  lastAnalyzedText = text;

  const spans = buildHighlightSpans(text, payload);
  if (options.isSentenceNav) {
    historySpans = mergeHighlightSpans(historySpans, spans);
  } else {
    historySpans = spans;
  }
  if (!options.isReplay && !options.isSentenceNav && text !== lastRecordedText) {
    const saved = await saveHistoryEntry(text, payload);
    if (saved) lastRecordedText = text;
  }

  document.querySelector('#inputText').value = text;
  returnToLocked();
  renderInputHighlights(text, payload);
  applySentenceSelection(payload);
  renderer.setTree(payload.tree);
  transition(STATES.VIEWING, 'output ready -> viewing');
}

async function saveHistoryEntry(text, payload) {
  const { data: { session: currentSession }, error: sessionError } = await supabase.auth.getSession();
  if (sessionError) {
    log(`History unavailable: ${sessionError.message}`);
    return null;
  }
  if (!currentSession?.user?.id) {
    log('History not saved: no authenticated user session.');
    return null;
  }

  const { error } = await supabase.from('analysis_history').insert({
    user_id: currentSession.user.id,
    sentence: text,
    is_valid: payload.summary.valid,
    constraints_fired: payload.summary.constraints_fired,
  });
  if (error) {
    log(`History save failed: ${error.message}`);
    return null;
  }
  log('Analysis history saved.');
  return true;
}

function failPipeline(title, lines) {
  showCanvasMessage('error', title, lines);
  renderSentenceVerdict([title, ...lines], true);
  renderDiagnostic(title, lines);
  transition(STATES.VIEWING, 'request failed -> diagnostic shown');
}

function applyStatuses(tree, details) {
  const detail = details[tree.id];
  tree.edgeResult = { status: detail?.status || 'valid' };
  for (const child of tree.children || []) applyStatuses(child, details);
}

function buildHighlightSpans(text, payload) {
  const target = payload.parse.sentences[payload.meta.target_sentence - 1];
  if (!target) return [];
  const tokens = payload.parse.tokens || [];
  const tokenRanges = [];
  let cursor = target.start;
  for (const token of tokens) {
    const start = text.indexOf(token.t, cursor);
    if (start < 0 || start >= target.end) continue;
    tokenRanges.push({ start, end: start + token.t.length, index: token.i });
    cursor = start + token.t.length;
  }
  const statuses = tokenRanges.map((token) => {
    let status = 'valid';
    for (const detail of Object.values(payload.node_details)) {
      if (detail.status === 'error' && detail.span[0] <= token.index && token.index < detail.span[1]) {
        if (detail.constraint === 'C-CAPITALIZATION' && token.index !== 0) continue;
        status = 'error';
        break;
      }
    }
    return { start: token.start, end: token.end, status };
  });
  return statuses;
}

function mergeHighlightSpans(existing, additions) {
  const merged = new Map(existing.map((span) => [`${span.start}:${span.end}`, span]));
  additions.forEach((span) => merged.set(`${span.start}:${span.end}`, span));
  return [...merged.values()].sort((a, b) => a.start - b.start);
}

function renderInputHighlights(text, payload = null) {
  const layer = document.querySelector('#inputHighlights');
  if (!layer) return;
  layer.textContent = '';
  if (!text) return;
  const spans = payload ? mergeHighlightSpans(historySpans, buildHighlightSpans(text, payload)) : historySpans;
  let cursor = 0;
  for (const span of spans) {
    if (span.start < cursor || span.start >= text.length) continue;
    layer.appendChild(document.createTextNode(text.slice(cursor, span.start)));
    const mark = document.createElement('span');
    mark.className = HIGHLIGHT_STATUSES.has(span.status) ? HIGHLIGHT_CLASSES[span.status] : '';
    mark.textContent = text.slice(span.start, Math.min(span.end, text.length));
    layer.appendChild(mark);
    cursor = Math.min(span.end, text.length);
  }
  layer.appendChild(document.createTextNode(text.slice(cursor)));
  syncHighlightScroll();
}

function syncHighlightScroll() {
  const ta = document.querySelector('#inputText');
  const layer = document.querySelector('#inputHighlights');
  if (ta && layer) {
    layer.scrollTop = ta.scrollTop;
    layer.scrollLeft = ta.scrollLeft;
  }
}

async function loadAndRenderHistory() {
  const container = document.querySelector('#historyList');
  if (!container) return;
  container.textContent = 'Loading past analyses...';
  const { data, error } = await supabase.from('analysis_history')
    .select('id, sentence, is_valid, constraints_fired, created_at')
    .order('created_at', { ascending: false }).limit(50);
  if (error) {
    container.textContent = `Error loading history: ${error.message}`;
    return;
  }
  cachedHistory = data || [];
  renderHistoryItems();
}

function renderHistoryItems() {
  const container = document.querySelector('#historyList');
  container.textContent = '';
  const entries = cachedHistory.filter((entry) => activeHistoryFilter === 'all'
    || (activeHistoryFilter === 'valid' ? entry.is_valid : !entry.is_valid));
  if (!entries.length) {
    container.textContent = 'No matching analyses found.';
    return;
  }
  entries.forEach((entry) => {
    const card = document.createElement('button');
    card.className = 'history-item';
    card.type = 'button';
    const status = document.createElement('strong');
    status.className = entry.is_valid ? 'legend-valid' : 'legend-invalid';
    status.textContent = entry.is_valid ? 'VALID' : 'INVALID';
    const sentence = document.createElement('span');
    sentence.textContent = entry.sentence;
    card.append(status, sentence);
    card.addEventListener('click', () => replayHistory(entry));
    container.appendChild(card);
  });
}

async function replayHistory(entry) {
  closeHistory();
  const ta = document.querySelector('#inputText');
  ta.value = entry.sentence;
  lastAnalyzedText = entry.sentence;
  await runPipeline({ isReplay: true });
}

async function clearHistory() {
  if (!authSession?.user?.id || !confirm('Clear all analysis history?')) return;
  const { error } = await supabase.from('analysis_history').delete().eq('user_id', authSession.user.id);
  if (error) console.error('Failed to clear history:', error.message);
  else {
    cachedHistory = [];
    historySpans = [];
    renderHistoryItems();
  }
}

function handleNodeSelect(id) {
  if (!id || !session) return;
  const detail = session.payload.node_details[id];
  const node = session.payload.nodes[id];
  if (!node || !detail) return;
  renderNodeDetail(session, detail, node);
  renderer.select(id);
  transition(STATES.EXPLORING, `selected syntax node ${node.type}`);
}

if (typeof window !== 'undefined') window.addEventListener('DOMContentLoaded', boot);
