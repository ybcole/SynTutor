import { loadClerk, createSupabaseClient } from './auth.js';
import { TreeRenderer } from './renderer.js';
import {
  log,
  clearOverlay, showCanvasMessage, renderSentenceVerdict, renderNodeDetail,
  renderDiagnostic, fillDevPanel, applySentenceSelection, plainName,
} from './ui.js';

let clerk = null;
let supabase = null;
let isGuest = true;

try {
  clerk = await loadClerk();
  if (clerk?.session) {
    isGuest = false;
    supabase = await createSupabaseClient();
  }
  clerk?.addListener(() => {
    isGuest = !clerk.session;
    updateAuthState();
  });
} catch (err) {
  console.warn('Authentication skipped or failed; running in guest mode:', err);
  isGuest = true;
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
  syncCanvasEmptyState();
}

function syncCanvasEmptyState() {
  const empty = document.querySelector('#emptyTreeState');
  if (!empty) return;
  empty.classList.toggle('hidden', state !== STATES.IDLE);
}

function getGuestHistory() {
  try {
    return JSON.parse(localStorage.getItem('syntutor_guest_history') || '[]');
  } catch {
    return [];
  }
}

function deleteGuestHistory(id) {
  const items = getGuestHistory().filter((item) => item.id !== id);
  localStorage.setItem('syntutor_guest_history', JSON.stringify(items));
}

function clearGuestHistory() {
  localStorage.removeItem('syntutor_guest_history');
}

export function boot() {
  renderer = new TreeRenderer(document.querySelector('#treeCanvas'), {
    onSelect: (id) => handleNodeSelect(id),
    onHover: () => {},
    describe: plainName,
  });
  wireEvents();
  initThemeAndMenu();
  transition(STATES.IDLE, 'system ready');
  log(`SynTutor engine ready \u2014 full-stack pipeline: spaCy + benepar + rule matrix (${isGuest ? 'guest mode' : 'authenticated'})`);
}

function initThemeAndMenu() {
  const savedTheme = localStorage.getItem('syntutor_theme') || 'light';
  applyTheme(savedTheme);
  updateAuthState();

  document.querySelector('#themeToggleBtn')?.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    applyTheme(current === 'dark' ? 'light' : 'dark');
  });

  document.querySelector('#identityChip')?.addEventListener('click', () => {
    toggleProfileMenu();
  });

  document.querySelector('#newSessionBtn')?.addEventListener('click', () => {
    startNewSession();
  });

  document.querySelector('#headerHistoryBtn')?.addEventListener('click', () => {
    openHistoryDrawer();
  });

  initDevPanel();
  initProfileMenu();
}

function openHistoryDrawer() {
  if (isGuest) return;
  document.querySelector('#historyDrawerBackdrop')?.classList.add('active');
  loadAndRenderHistory();
}

function openAuthModal() {
  const backdrop = document.querySelector('#authModalBackdrop');
  if (!backdrop) return;
  backdrop.classList.add('active');
  const email = document.querySelector('#authEmail');
  if (email) setTimeout(() => email.focus(), 0);
}

function closeAuthModal() {
  document.querySelector('#authModalBackdrop')?.classList.remove('active');
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('syntutor_theme', theme);
  const icon = document.querySelector('#themeIcon');
  if (icon) {
    icon.innerHTML = theme === 'dark'
      ? `
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="5"></circle>
          <line x1="12" y1="1" x2="12" y2="3"></line>
          <line x1="12" y1="21" x2="12" y2="23"></line>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
          <line x1="1" y1="12" x2="3" y2="12"></line>
          <line x1="21" y1="12" x2="23" y2="12"></line>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        </svg>
      `
      : `
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
      `;
  }
  if (renderer && renderer.tree) {
    renderer.draw();
  }
}

function updateAuthState() {
  const chip = document.querySelector('#identityChip');
  const label = document.querySelector('#identityLabel');
  const avatar = document.querySelector('#identityAvatar');
  const historyBtn = document.querySelector('#headerHistoryBtn');
  if (!chip || !label || !avatar) return;

  if (!isGuest && clerk?.session) {
    const user = clerk.user;
    const name = user?.firstName || user?.username || user?.primaryEmailAddress?.emailAddress?.split('@')[0] || 'User';
    label.textContent = name;
    avatar.classList.remove('guest');
    avatar.textContent = name.charAt(0).toUpperCase();
    chip.title = 'Sign out';
    if (historyBtn) historyBtn.hidden = false;
  } else {
    label.textContent = 'Guest';
    avatar.classList.add('guest');
    avatar.innerHTML = `
      <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
    `;
    chip.title = 'Log In / Sign Up';
    if (historyBtn) historyBtn.hidden = true;
    document.querySelector('#historyDrawerBackdrop')?.classList.remove('active');
  }
  renderProfileMenu();
}

let devPanelOpen = false;

function setDevPanelOpen(open) {
  devPanelOpen = open;
  const overlay = document.querySelector('#devPanelOverlay');
  const toggle = document.querySelector('#devPanelToggle');
  overlay?.classList.toggle('open', open);
  toggle?.classList.toggle('open', open);
  toggle?.setAttribute('aria-expanded', String(open));
  overlay?.setAttribute('aria-hidden', String(!open));
}

function initDevPanel() {
  document.querySelector('#devPanelToggle')?.addEventListener('click', () => {
    setDevPanelOpen(!devPanelOpen);
  });
}

let profileMenuOpen = false;

function renderProfileMenu() {
  const auth = !isGuest && !!(clerk?.session);
  const setHidden = (id, hidden) => {
    const el = document.querySelector(id);
    if (el) el.hidden = hidden;
  };
  setHidden('#profileAddAccount', !auth);
  setHidden('#profileSwitchAccount', !auth);
  setHidden('#profileMenuDivider', !auth);
  setHidden('#profileLogout', !auth);
  setHidden('#profileSignIn', auth);
}

function setProfileMenu(open) {
  profileMenuOpen = open;
  const menu = document.querySelector('#profileMenu');
  const chip = document.querySelector('#identityChip');
  if (menu) {
    menu.classList.toggle('open', open);
    menu.setAttribute('aria-hidden', String(!open));
  }
  chip?.setAttribute('aria-expanded', String(open));
  if (open) showProfileMenuMain();
}

function toggleProfileMenu() {
  setProfileMenu(!profileMenuOpen);
}

function showProfileMenuMain() {
  const main = document.querySelector('#profileMenuMain');
  const accounts = document.querySelector('#profileAccounts');
  if (main) main.hidden = false;
  if (accounts) accounts.hidden = true;
}

function profileAccountName(session) {
  const u = session.user || {};
  if (u.firstName) return u.firstName;
  if (u.username) return u.username;
  if (u.primaryEmailAddress?.emailAddress) return u.primaryEmailAddress.emailAddress.split('@')[0];
  return 'Account';
}

async function openProfileAccounts() {
  const main = document.querySelector('#profileMenuMain');
  const accounts = document.querySelector('#profileAccounts');
  if (main) main.hidden = true;
  if (accounts) accounts.hidden = false;
  const list = document.querySelector('#profileAccountsList');
  if (!list) return;
  list.innerHTML = '';
  let sessions = [];
  try {
    sessions = (clerk?.client?.sessions || []).filter((s) => s.status === 'active');
  } catch {
    sessions = [];
  }
  if (!sessions.length) {
    const none = document.createElement('p');
    none.className = 'profile-menu-note';
    none.textContent = 'No other accounts found.';
    list.appendChild(none);
    return;
  }
  for (const s of sessions) {
    const active = clerk?.session?.id === s.id;
    const name = profileAccountName(s);
    const email = s.user?.primaryEmailAddress?.emailAddress || name;
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = `profile-account-item${active ? ' active' : ''}`;
    if (active) btn.setAttribute('aria-current', 'true');
    const av = document.createElement('span');
    av.className = 'profile-account-avatar';
    av.textContent = name.charAt(0).toUpperCase();
    const meta = document.createElement('span');
    meta.className = 'profile-account-meta';
    const nm = document.createElement('span');
    nm.className = 'profile-account-name';
    nm.textContent = name;
    const em = document.createElement('span');
    em.className = 'profile-account-email';
    em.textContent = email;
    meta.appendChild(nm);
    meta.appendChild(em);
    btn.appendChild(av);
    btn.appendChild(meta);
    list.appendChild(btn);
    if (active) continue;
    btn.addEventListener('click', async () => {
      try {
        await clerk.setActive({ session: s.id });
      } catch (err) {
        console.warn('Account switch failed:', err);
      }
      setProfileMenu(false);
    });
  }
}

function initProfileMenu() {
  document.querySelector('#profileAddAccount')?.addEventListener('click', () => {
    setProfileMenu(false);
    openAuthModal();
  });
  document.querySelector('#profileSwitchAccount')?.addEventListener('click', () => {
    openProfileAccounts();
  });
  document.querySelector('#profileLogout')?.addEventListener('click', () => {
    if (clerk) {
      clerk.signOut().then(() => window.location.reload());
    } else {
      setProfileMenu(false);
    }
  });
  document.querySelector('#profileSignIn')?.addEventListener('click', () => {
    setProfileMenu(false);
    openAuthModal();
  });
  document.addEventListener('click', (e) => {
    if (profileMenuOpen && !e.target.closest('.profile-anchor')) setProfileMenu(false);
  });
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

  const drawer = document.querySelector('#historyDrawerBackdrop');
  document.querySelector('#closeDrawerBtn')?.addEventListener('click', () => {
    drawer?.classList.remove('active');
  });
  drawer?.addEventListener('click', (e) => {
    if (e.target === drawer) drawer.classList.remove('active');
  });

  const authModal = document.querySelector('#authModalBackdrop');
  document.querySelector('#authContinueGuestBtn')?.addEventListener('click', closeAuthModal);
  authModal?.addEventListener('click', (e) => {
    if (e.target === authModal) closeAuthModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    if (authModal?.classList.contains('active')) {
      closeAuthModal();
      return;
    }
    if (profileMenuOpen) {
      setProfileMenu(false);
      return;
    }
    if (devPanelOpen) setDevPanelOpen(false);
  });

  document.querySelectorAll('#historyFilters .filter-pill').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#historyFilters .filter-pill').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      activeHistoryFilter = btn.dataset.filter;
      renderHistoryItems();
    });
  });

  document.querySelector('#clearHistoryBtn')?.addEventListener('click', async () => {
    if (!cachedHistory.length) return;
    if (confirm('Clear all analysis history? This action cannot be undone.')) {
      if (!isGuest && supabase && clerk?.user?.id) {
        const { error } = await supabase
          .from('analysis_history')
          .delete()
          .eq('user_id', clerk.user.id);

        if (error) {
          alert('Failed to clear history: ' + error.message);
          return;
        }
      } else {
        clearGuestHistory();
      }
      cachedHistory = [];
      renderHistoryItems();
    }
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

function startNewSession() {
  if (state === STATES.PROCESSING) return;

  recordedTexts.clear();
  session = null;
  lastAnalyzedText = null;
  historySpans = [];

  const ta = document.querySelector('#inputText');
  const editor = document.querySelector('.input-editor');
  ta.value = '';
  ta.readOnly = true;
  ta.classList.remove('editing');
  editor?.classList.remove('editing');
  setEditHint(false);
  renderInputHighlights('');
  syncHighlightScroll();

  renderer.select(null);
  renderer.clear();
  clearOverlay();
  renderNodeDetail(null, null, null);
  renderSentenceVerdict(['Submit a sentence to see the auto-generated pedagogical summary.'], false);

  const parseStr = document.querySelector('#parseString');
  const tokStream = document.querySelector('#tokenStream');
  if (parseStr) parseStr.textContent = '\u2014';
  if (tokStream) tokStream.textContent = '\u2014';

  document.querySelector('#emptyTreeState')?.classList.remove('hidden');

  transition(STATES.IDLE, 'new session started');
  log('New session \u2014 canvas, input, and analysis cleared.');
}

function activateSentenceAtCaret() {
  const ta = document.querySelector('#inputText');
  if (!session || ta.readOnly !== true) return;
  if (ta.selectionStart !== ta.selectionEnd) return;
  const sents = session.payload.parse.sentences || [];
  const caret = ta.selectionStart;
  const hit = sents.find((s) => caret >= s.start && caret < s.end);
  if (hit && hit.ordinal - 1 !== (session.payload.meta.target_sentence || 1) - 1) {
    runPipeline({ index: hit.ordinal - 1, isSentenceNav: true });
  }
}

function failPipeline(title, lines) {
  showCanvasMessage('error', title, lines);
  renderSentenceVerdict([`\u{26D4} ${title}`, ...lines], true);
  renderDiagnostic(title, lines);
  transition(STATES.VIEWING, 'request failed -> diagnostic shown');
  log(`Request failed: ${title} \u2014${lines[0] || ''}`);
}

async function runPipeline(opts = {}) {
  if (state === STATES.PROCESSING) return;
  transition(STATES.PROCESSING, 'user submits text');
  setLoadingIndicator(true);
  try {
    await executePipeline(opts);
  } finally {
    setLoadingIndicator(false);
  }
}

function setLoadingIndicator(show) {
  const pill = document.querySelector('#loadingIndicator');
  if (pill) pill.classList.toggle('visible', show);
  syncCanvasEmptyState();
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
  log(`Stage 2: payload received (${Object.keys(payload.nodes).length} nodes) \u00b7${payload.meta.backend}`);

  const tokens = payload.parse.tokens;
  const posInfo = tokens.map((t) => `${t.t}/${t.pos}`).join(' ');
  log(`Stage 3: spaCy tokenization + POS \u2014 ${posInfo}`);
  if (payload.meta.sentence_count > 1) {
    log(`Stage 3: ${payload.meta.sentence_count} sentence(s) detected \u2014 analyzing sentence${payload.meta.target_sentence} (deterministic policy)`);
  }

  log(`Stage 4: benepar parse string \u2014 ${payload.parse.parse_string}`);

  applyStatuses(payload.tree, payload.node_details);
  const s = payload.summary;
  log(`Stage 5: rule-matrix validation \u2014 ${s.valid_edges} valid / ${s.violated_edges} violated / ${s.unrated_edges} unrated \u00b7 fired${JSON.stringify(s.constraints_fired)}`);

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

  document.querySelector('#emptyTreeState')?.classList.add('hidden');
  renderer.setTree(payload.tree);
  transition(STATES.VIEWING, 'output ready -> viewing');
  log('Stage 7: syntax tree rendered \u2014 Interaction Loop active (node details cached in session)');

  const isNavigation = Boolean(opts.isSentenceNav || opts.isReplay);
  if (!isNavigation && !recordedTexts.has(text)) {
    if (!isGuest && supabase && clerk?.user?.id) {
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
    } else {
      recordedTexts.add(text);
      log('Stage 6b: analysis history skipped (guest session)');
    }
  }
}

function buildHighlightSpans(text, payload) {
  const target = payload.parse.sentences[payload.meta.target_sentence - 1];
  if (!target) return [];
  const tokens = payload.parse.tokens || [];
  const tokenRanges = [];
  const hasCharOffsets = tokens.length > 0 && tokens.every(
    (t) => typeof t.start === 'number' && typeof t.end === 'number' && t.end > t.start,
  );
  if (hasCharOffsets) {
    for (const token of tokens) {
      if (token.start < target.start || token.end > target.end) continue;
      tokenRanges.push({ start: token.start, end: token.end, index: token.i });
    }
  } else {
    let cursor = target.start;
    for (const token of tokens) {
      const start = text.indexOf(token.t, cursor);
      if (start < 0 || start >= target.end) continue;
      tokenRanges.push({ start, end: start + token.t.length, index: token.i });
      cursor = start + token.t.length;
    }
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
      renderNodeDetail(null, null, null);
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
  if (isGuest) return;
  container.innerHTML = '<p class="history-empty">Loading past analyses...</p>';

  if (supabase) {
    const { data, error } = await supabase
      .from('analysis_history')
      .select('id, sentence, is_valid, constraints_fired, created_at')
      .order('created_at', { ascending: false })
      .limit(50);

    if (error) {
      container.innerHTML = `<p class="history-empty" style="color: var(--err);">Error loading history: ${error.message}</p>`;
      return;
    }
    cachedHistory = data || [];
  } else {
    cachedHistory = [];
  }

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
    container.innerHTML = '<p class="history-empty">No matching analyses found.</p>';
    return;
  }

  container.innerHTML = '';
  filtered.forEach((entry) => {
    const card = document.createElement('div');
    card.className = 'history-item';
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');
    card.title = 'Open this analysis';

    const date = new Date(entry.created_at).toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    });

    const isError = !entry.is_valid;

    const head = document.createElement('div');
    head.className = 'hist-head';

    const badge = document.createElement('span');
    badge.className = `hist-badge ${isError ? 'err' : 'ok'}`;
    badge.textContent = entry.is_valid ? 'Valid' : 'Invalid';

    const timeSpan = document.createElement('span');
    timeSpan.className = 'hist-time';
    timeSpan.textContent = date;

    const delBtn = document.createElement('button');
    delBtn.type = 'button';
    delBtn.title = 'Delete entry';
    delBtn.className = 'hist-delete-btn';
    delBtn.innerHTML = `
      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="3 6 5 6 21 6"></polyline>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
      </svg>
    `;

    const openSvg = document.createElement('span');
    openSvg.className = 'hist-open';
    openSvg.setAttribute('aria-hidden', 'true');
    openSvg.innerHTML = `
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="9 18 15 12 9 6"></polyline>
      </svg>
    `;

    head.appendChild(badge);
    head.appendChild(timeSpan);
    head.appendChild(delBtn);
    head.appendChild(openSvg);

    const sentenceP = document.createElement('p');
    sentenceP.className = 'hist-sentence';
    sentenceP.textContent = entry.sentence;
    sentenceP.title = entry.sentence;

    const chipsDiv = document.createElement('div');
    chipsDiv.className = 'hist-chips';
    (entry.constraints_fired || []).forEach((constraint) => {
      const chip = document.createElement('span');
      chip.className = `hist-chip ${isError ? 'err' : ''}`;
      chip.textContent = constraint;
      chipsDiv.appendChild(chip);
    });

    card.appendChild(head);
    card.appendChild(sentenceP);
    if (entry.constraints_fired?.length) card.appendChild(chipsDiv);

    const openEntry = () => {
      document.querySelector('#historyDrawerBackdrop')?.classList.remove('active');
      const ta = document.querySelector('#inputText');
      ta.value = entry.sentence;
      recordedTexts.add(entry.sentence);
      runPipeline({ isReplay: true });
    };

    card.addEventListener('click', openEntry);
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openEntry();
      }
    });

    delBtn.addEventListener('click', async (e) => {
      e.stopPropagation();
      delBtn.disabled = true;

      if (!isGuest && supabase) {
        const { error } = await supabase
          .from('analysis_history')
          .delete()
          .eq('id', entry.id);

        if (error) {
          alert('Failed to delete item: ' + error.message);
          delBtn.disabled = false;
          return;
        }
      } else {
        deleteGuestHistory(entry.id);
      }

      cachedHistory = cachedHistory.filter((item) => item.id !== entry.id);
      renderHistoryItems();
    });

    container.appendChild(card);
  });
}

if (typeof window !== 'undefined') {
  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', () => boot());
  } else {
    boot();
  }
}