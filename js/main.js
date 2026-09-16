import { supabase } from './auth.js';
import { TreeRenderer } from './renderer.js';
import {
  log,
  clearOverlay, showCanvasMessage, renderSentenceVerdict, renderNodeDetail,
  renderDiagnostic, fillDevPanel, applySentenceSelection, plainName,
} from './ui.js';

// Route guard: require session before loading syntax tree workbench
const { data: { session: authSession } } = await supabase.auth.getSession();
if (!authSession) {
  window.location.href = '/login.html';
}

supabase.auth.onAuthStateChange((event, currentSession) => {
  if (event === 'SIGNED_OUT' || !currentSession) {
    window.location.href = '/login.html';
  }
});

const STATES = { IDLE: 'IDLE', PROCESSING: 'PROCESSING', VIEWING: 'VIEWING', EXPLORING: 'EXPLORING', END: 'END' };

let state = STATES.IDLE;
let session = null;
let renderer = null;
let lastAnalyzedText = null;
let lastRecordedText = null;

let cachedHistory = [];
let activeHistoryFilter = 'all';

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

  // History Drawer Controls
  const drawer = document.querySelector('#historyDrawerBackdrop');
  document.querySelector('#historyBtn')?.addEventListener('click', () => {
    drawer?.classList.add('active');
    loadAndRenderHistory();
  });
  document.querySelector('#closeDrawerBtn')?.addEventListener('click', () => {
    drawer?.classList.remove('active');
  });
  drawer?.addEventListener('click', (e) => {
    if (e.target === drawer) drawer.classList.remove('active');
  });

  // Filter pills
  document.querySelectorAll('#historyFilters .filter-pill').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#historyFilters .filter-pill').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      activeHistoryFilter = btn.dataset.filter;
      renderHistoryItems();
    });
  });

  // Clear all history
  document.querySelector('#clearHistoryBtn')?.addEventListener('click', async () => {
    if (!cachedHistory.length) return;
    if (confirm('Clear all analysis history? This action cannot be undone.')) {
      const { error } = await supabase
        .from('analysis_history')
        .delete()
        .eq('user_id', authSession.user.id);

      if (error) {
        alert('Failed to clear history: ' + error.message);
      } else {
        cachedHistory = [];
        renderHistoryItems();
      }
    }
  });

  // Auth Controls
  document.querySelector('#logoutBtn')?.addEventListener('click', async () => {
    await supabase.auth.signOut();
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
    // Navigating between sentences in the same text must not create history records
    runPipeline({ index: hit.ordinal - 1, isSentenceNav: true });
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

  // Persist to history only when user submits a new text (never on sentence clicks or replays)
  const isNavigation = Boolean(opts.isSentenceNav || opts.isReplay);
  if (authSession?.user?.id && !isNavigation && text !== lastRecordedText) {
    lastRecordedText = text;
    supabase.from('analysis_history').insert({
      user_id: authSession.user.id,
      sentence: text,
      is_valid: payload.summary.valid,
      constraints_fired: payload.summary.constraints_fired,
    }).then(({ error }) => {
      if (error) console.error('Failed to log history:', error.message);
    });
  }

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

async function loadAndRenderHistory() {
  const container = document.querySelector('#historyList');
  if (!container) return;
  container.innerHTML = '<p class="muted">Loading past analyses...</p>';

  const { data, error } = await supabase
    .from('analysis_history')
    .select('id, sentence, is_valid, constraints_fired, created_at')
    .order('created_at', { ascending: false })
    .limit(50);

  if (error) {
    container.innerHTML = `<p class="muted" style="color: var(--err);">Error loading history: ${error.message}</p>`;
    return;
  }

  cachedHistory = data || [];
  renderHistoryItems();
}

function renderHistoryItems() {
  const container = document.querySelector('#historyList');
  if (!container) return;

  const filtered = cachedHistory.filter((entry) => {
    if (activeHistoryFilter === 'error') return !entry.is_valid;
    if (activeHistoryFilter === 'valid') return entry.is_valid;
    return true;
  });

  if (!filtered.length) {
    container.innerHTML = '<p class="muted">No matching analyses found.</p>';
    return;
  }

  container.innerHTML = '';
  filtered.forEach((entry) => {
    const card = document.createElement('div');
    card.className = 'history-item';

    const date = new Date(entry.created_at).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    });

    const statusClass = entry.is_valid ? 'ok' : 'err';
    const statusText = entry.is_valid ? 'VALID' : 'INVALID';

    card.innerHTML = `
      <div class="hist-top">
        <span class="hist-status">
          <span class="nc-dot ${statusClass}"></span>
          <span style="color: var(--${statusClass});">${statusText}</span>
        </span>
        <div class="hist-actions">
          <span class="hist-time">${date}</span>
          <button class="hist-delete-btn" title="Delete entry" data-id="${entry.id}">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
        </div>
      </div>
      <p class="hist-sentence">${entry.sentence}</p>
      <div class="hist-chips">
        ${(entry.constraints_fired || []).map((c) => `<span class="nc-chip ${entry.is_valid ? '' : 'err'}">${c}</span>`).join('')}
      </div>
    `;

    // Replay from history without re-logging
    card.addEventListener('click', () => {
      document.querySelector('#historyDrawerBackdrop')?.classList.remove('active');
      const ta = document.querySelector('#inputText');
      ta.value = entry.sentence;
      lastRecordedText = entry.sentence;
      runPipeline({ isReplay: true });
    });

    // Delete single item
    const delBtn = card.querySelector('.hist-delete-btn');
    delBtn.addEventListener('click', async (e) => {
      e.stopPropagation();
      delBtn.disabled = true;

      const { error } = await supabase
        .from('analysis_history')
        .delete()
        .eq('id', entry.id);

      if (error) {
        alert('Failed to delete item: ' + error.message);
        delBtn.disabled = false;
      } else {
        cachedHistory = cachedHistory.filter((item) => item.id !== entry.id);
        renderHistoryItems();
      }
    });

    container.appendChild(card);
  });
}

if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', () => boot());
}