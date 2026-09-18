import { loadClerk, createSupabaseClient } from './auth.js';
import { TreeRenderer } from './renderer.js';
import {
  log,
  clearOverlay, showCanvasMessage, renderSentenceVerdict, renderNodeDetail,
  renderDiagnostic, fillDevPanel, applySentenceSelection, plainName,
} from './ui.js';

// Route guard: require a Clerk session before loading the syntax tree workbench.
// The supabase client, listener, and boot sequence are all gated on the session
// so an unauthenticated visitor only triggers the redirect — nothing else runs.
const clerk = await loadClerk();
const supabase = clerk.session ? await createSupabaseClient() : null;

if (!clerk.session) {
  window.location.href = '/login.html';
} else {
  // Supabase client bound to the active Clerk session token (see auth.js);
  // RLS authorizes reads/writes via the Clerk `sub` claim in the JWT.
  clerk.addListener(() => {
    if (!clerk.session) {
      window.location.href = '/login.html';
    }
  });
}

const STATES = { IDLE: 'IDLE', PROCESSING: 'PROCESSING', VIEWING: 'VIEWING', EXPLORING: 'EXPLORING', END: 'END' };
const HIGHLIGHT_STATUSES = new Set(['valid', 'error']);
const HIGHLIGHT_CLASSES = { valid: '', error: 'word-invalid' };

let state = STATES.IDLE;
let session = null;
let renderer = null;
let lastAnalyzedText = null;
const recordedTexts = new Set();
let historySpans = [];

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
  const editor = document.querySelector('.input-editor');
  ta.addEventListener('dblclick', () => {
    editor?.classList.add('editing');
    ta.readOnly = false;
    ta.classList.add('editing');
    setEditHint(true);
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
        .eq('user_id', clerk.user.id);

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
    await clerk.signOut();
    window.location.href = '/login.html';
  });
}

function setEditHint(editing) {
  const hint = document.querySelector('#inputHint');
  hint.textContent = editing
    ? 'Editing \u2014 click away to lock and analyze.'
    : 'Locked \u2014 click any sentence to view its syntax tree. Double-click to edit.';
}

function returnToLocked(payload = null) {
  const ta = document.querySelector('#inputText');
  const editor = document.querySelector('.input-editor');
  ta.readOnly = true;
  ta.classList.remove('editing');
  editor?.classList.remove('editing');
  setEditHint(false);
  renderInputHighlights(ta.value, payload);
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

  document.querySelector('#inputText').value = text;
  const spans = buildHighlightSpans(text, payload);
  if (opts.isSentenceNav) {
    historySpans = mergeHighlightSpans(historySpans, spans);
  } else {
    historySpans = spans;
  }
  returnToLocked(payload);
  applySentenceSelection(payload);
  renderer.setTree(payload.tree);
  transition(STATES.VIEWING, 'output ready -> viewing');
  log('Stage 7: syntax tree rendered \u2014 Interaction Loop active (node details cached in session)');

  // Persist to history only when user submits a new text (never on sentence clicks or replays).
  // Save in the background so a slow/unavailable Supabase never blocks rendering the verdict,
  // and only mark the text as recorded once the insert has actually succeeded.
  const isNavigation = Boolean(opts.isSentenceNav || opts.isReplay);
  if (clerk.user?.id && !isNavigation && !recordedTexts.has(text)) {
    try {
      const { error: insertError } = await supabase.from('analysis_history').insert({
        user_id: clerk.user.id,
        sentence: text,
        is_valid: payload.summary.valid,
        constraints_fired: payload.summary.constraints_fired,
      });

      if (insertError) {
        console.warn('Failed to log history to Supabase:', insertError.message);
        log(`Warning: Failed to save analysis history \u2014 ${insertError.message}`);
      } else {
        recordedTexts.add(text);
        log('Stage 6b: analysis history recorded in Supabase');
      }
    } catch (dbErr) {
      console.warn('Network error logging history:', dbErr);
      log('Warning: Network error saving history');
    }
  }
}

function lockInput() {
  const ta = document.querySelector('#inputText');
  ta.readOnly = true;
  ta.classList.remove('editing');
  setEditHint(false);
  ta.blur();
}

function buildHighlightSpans(text, payload) {
  const target = payload.parse.sentences[payload.meta.target_sentence - 1];
  if (!target) return [];
  const tokenRanges = [];
  let cursor = target.start;
  for (const token of payload.parse.tokens || []) {
    const start = text.indexOf(token.t, cursor);
    if (start < 0 || start >= target.end) continue;
    tokenRanges.push({ start, end: start + token.t.length, index: token.i });
    cursor = start + token.t.length;
  }
  return tokenRanges.map((token) => {
    let status = 'valid';
    const isSentenceInitialToken = token.index === tokenRanges[0]?.index;
    for (const detail of Object.values(payload.node_details)) {
      if (detail.status === 'error' && detail.span[0] <= token.index && token.index < detail.span[1]) {
        if (detail.constraint === 'C-CAPITALIZATION' && !isSentenceInitialToken) continue;
        status = 'error';
        break;
      }
    }
    return { start: token.start, end: token.end, status };
  });
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
  const target = payload?.parse?.sentences?.[(payload.meta.target_sentence || 1) - 1];
  const sentenceStart = target?.start ?? -1;
  const sentenceEnd = target?.end ?? -1;
  const boundaries = new Set([0, text.length]);
  spans.forEach((span) => {
    boundaries.add(Math.max(0, Math.min(span.start, text.length)));
    boundaries.add(Math.max(0, Math.min(span.end, text.length)));
  });
  if (sentenceStart >= 0) {
    boundaries.add(sentenceStart);
    boundaries.add(sentenceEnd);
  }
  const points = [...boundaries].sort((a, b) => a - b);
  for (let index = 0; index < points.length - 1; index += 1) {
    const start = points[index];
    const end = points[index + 1];
    if (start === end) continue;
    const wordSpan = spans.find((span) => span.start <= start && end <= span.end);
    const selected = sentenceStart >= 0 && start >= sentenceStart && end <= sentenceEnd;
    const classes = [];
    if (selected) classes.push('sentence-selected');
    if (wordSpan && HIGHLIGHT_STATUSES.has(wordSpan.status) && HIGHLIGHT_CLASSES[wordSpan.status]) {
      classes.push(HIGHLIGHT_CLASSES[wordSpan.status]);
    }
    if (classes.length) {
      const mark = document.createElement('span');
      mark.className = classes.join(' ');
      mark.textContent = text.slice(start, end);
      layer.appendChild(mark);
    } else {
      layer.appendChild(document.createTextNode(text.slice(start, end)));
    }
  }
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

    // 1. Header row
    const topRow = document.createElement('div');
    topRow.className = 'hist-top';

    const statusSpan = document.createElement('span');
    statusSpan.className = 'hist-status';

    const dot = document.createElement('span');
    dot.className = `nc-dot ${statusClass}`;

    const statusLabel = document.createElement('span');
    statusLabel.style.color = `var(--${statusClass})`;
    statusLabel.textContent = statusText;

    statusSpan.appendChild(dot);
    statusSpan.appendChild(statusLabel);

    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'hist-actions';

    const timeSpan = document.createElement('span');
    timeSpan.className = 'hist-time';
    timeSpan.textContent = date;

    const delBtn = document.createElement('button');
    delBtn.className = 'hist-delete-btn';
    delBtn.title = 'Delete entry';
    delBtn.setAttribute('aria-label', 'Delete entry');
    delBtn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="3 6 5 6 21 6"></polyline>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
      </svg>
    `;

    actionsDiv.appendChild(timeSpan);
    actionsDiv.appendChild(delBtn);

    topRow.appendChild(statusSpan);
    topRow.appendChild(actionsDiv);

    // 2. Sentence paragraph (safe textContent prevents XSS)
    const sentenceP = document.createElement('p');
    sentenceP.className = 'hist-sentence';
    sentenceP.textContent = entry.sentence;

    // 3. Chips container (safe textContent for constraints)
    const chipsDiv = document.createElement('div');
    chipsDiv.className = 'hist-chips';
    (entry.constraints_fired || []).forEach((constraint) => {
      const chip = document.createElement('span');
      chip.className = `nc-chip ${entry.is_valid ? '' : 'err'}`;
      chip.textContent = constraint;
      chipsDiv.appendChild(chip);
    });

    card.appendChild(topRow);
    card.appendChild(sentenceP);
    card.appendChild(chipsDiv);

    // Replay interaction
    card.addEventListener('click', () => {
      document.querySelector('#historyDrawerBackdrop')?.classList.remove('active');
      const ta = document.querySelector('#inputText');
      ta.value = entry.sentence;
      recordedTexts.add(entry.sentence);
      runPipeline({ isReplay: true });
    });

    // Delete interaction
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
  // auth.js loads with `defer` and main.js with `type=module`, so the DOM may
  // already be interactive by the time this module runs — guard both cases.
  // boot() depends on the gated supabase client, so it only runs with a session.
  if (clerk.session && document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', () => boot());
  } else if (clerk.session) {
    boot();
  }
}