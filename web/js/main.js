import { loadClerk, createSupabaseClient } from './auth.js';
import { API_BASE } from './config.js';
import { TreeRenderer } from './renderer.js';
import { getSavedTheme, setTheme } from './theme.js';
import {
  log,
  clearOverlay, clearDiagnostics, showCanvasMessage, renderNodeDetail,
  renderDiagnostic, renderCorrection, applySentenceSelection, plainName, renderCorrectionPanel,
} from './ui.js';
import {
  planFocus, contextWords, applyEdit, expectedScopeWords, findScopeNode, findTargetError,
} from './correction.js';
import {
  openQuizView, closeQuizView, closeSubpanel, initQuiz, quizInputHint, clearActiveLesson,
} from './tree-quiz.js';
import { initSyntaxBuilder, openBuilderView, closeBuilderView, isBuilderOpen, clearBuilder } from './syntax-builder-ui.js';
import { levelFromXp } from './level.js';
import { computeUnlocked } from './achievements.js';

let clerk = null;
let supabase = null;
let isGuest = true;
let activeSessionId = null;

try {
  clerk = await loadClerk();
  if (clerk?.session) {
    isGuest = false;
    activeSessionId = clerk.session.id;
  }
  // Create the Supabase client for every mode: authenticated reads/writes use
  // the Clerk session token, while guests get an anonymous client that can
  // still read the public leaderboard.
  supabase = await createSupabaseClient();
  clerk?.addListener(() => {
    const sessionId = clerk.session?.id ?? null;
    if (sessionId !== activeSessionId) {
      // Identity changed (account switch, sign-in, or sign-out): the
      // in-memory history caches belong to the previous identity, so drop
      // them. History reloads lazily from Supabase on the next drawer open.
      activeSessionId = sessionId;
      recordedTexts.clear();
      cachedHistory = [];
    }
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
let quizMode = false;
const recordedTexts = new Set();
let historySpans = [];

let cachedHistory = [];
let activeHistoryFilter = 'all';

// ---------------------------------------------------------------------------
// Interactive corrective feedback
// ---------------------------------------------------------------------------
// The learner picks a grammar error (a red node in the tree), the canvas zooms
// to the subtree the rule talks about, and the correction panel offers the
// server's suggested repair as a live preview of the re-parsed sentence.
// `focus` holds everything about the error that is currently selected.
let focus = null;                 // active correction target
let correctionMode = 'original';  // 'original' | 'corrected' | 'alternative'
let focusResult = null;           // {kind:'fixed'|'still', message}
let previewLoading = null;        // 'corrected' | 'alternative' | null
let liveReparseTimer = null;      // debounce handle for the live re-parse
let liveReparsePending = false;   // a live re-parse that had to wait

// Live re-parse: while the learner edits the sentence of an open correction,
// the tree follows along, so a fix is confirmed the moment it is typed.
// It only runs while a correction is open — ordinary editing keeps the
// original click-away behaviour.
function scheduleLiveReparse() {
  if (liveReparseTimer) clearTimeout(liveReparseTimer);
  liveReparseTimer = setTimeout(() => {
    liveReparseTimer = null;
    if (!focus || workspaceView !== 'tutor' || quizMode) return;
    const ta = document.querySelector('#inputText');
    if (!ta || ta.readOnly === true || !ta.value.trim()) return;
    if (state === STATES.PROCESSING) { liveReparsePending = true; return; }
    // Keep the sentence the learner is looking at: a passage has one tree per
    // sentence, and the correction belongs to this one.
    const index = session?.sentence_index ?? focus.sentenceIndex ?? 0;
    runPipeline({ isLive: true, index, mergeSpans: true });
  }, 500);
}

function cancelLiveReparse() {
  if (liveReparseTimer) { clearTimeout(liveReparseTimer); liveReparseTimer = null; }
  liveReparsePending = false;
}

const correctionHandlers = {
  onShowCorrected: () => showCorrected('corrected'),
  onShowAlternative: () => showCorrected('alternative'),
  onShowOriginal: () => showOriginal(),
  onClose: () => dismissFocus(),
};

// The preview currently on the canvas, if any. While a preview is showing the
// canvas holds a re-parsed (corrected) sentence, whose node ids differ from
// the original tree's.
function activePreview() {
  if (!focus) return null;
  if (correctionMode === 'corrected') return focus.corrected || null;
  if (correctionMode === 'alternative') return focus.alternativeCorrected || null;
  return null;
}

function refreshCorrectionUi() {
  if (!focus) {
    renderCorrectionPanel(focusResult ? { result: focusResult } : null, correctionHandlers);
    return;
  }
  renderCorrectionPanel({
    label: focus.label,
    mode: correctionMode,
    canCorrect: Boolean(focus.edit),
    alternativeCanCorrect: Boolean(focus.alternativeEdit),
    suggestedFix: focus.suggestedFix || '',
    correctedText: focus.corrected ? focus.corrected.text : '',
    alternativeCorrectedText: focus.alternativeCorrected ? focus.alternativeCorrected.text : '',
    loading: previewLoading,
    result: focusResult,
  }, correctionHandlers);
}

// Leave the correction: the panel closes and the canvas returns to the whole
// tree. This is the explicit way out — clicking empty canvas only drops the
// node selection, so a correction in progress is never thrown away by the
// click that dismisses the keyboard.
function dismissFocus() {
  cancelLiveReparse();
  focus = null;
  correctionMode = 'original';
  focusResult = null;
  renderer.clearFocus();
  refreshCorrectionUi();
}

function resetFocusState() {
  dismissFocus();
}

// Select an error and zoom the canvas to the part of the tree the rule is
// about. Only the original tree can start a correction.
function enterFocus(id, detail) {
  const payload = session?.payload;
  if (!payload || !detail || detail.status !== 'error') return;
  const plan = planFocus(payload, id);
  if (!plan) return;
  const remediation = detail.remediation || {};
  focus = {
    ...plan,
    constraint: detail.constraint,
    sentenceIndex: (payload.meta.target_sentence || 1) - 1,
    context: contextWords(payload, plan.scopeId),
    edit: remediation.edit || null,
    alternativeEdit: remediation.alternative_edit || null,
    suggestedFix: remediation.suggested_fix || '',
    corrected: null,
    alternativeCorrected: null,
  };
  correctionMode = 'original';
  focusResult = null;
  renderer.focusNode(plan.nodeId, plan.scopeId, plan.pair);
  renderer.select(plan.nodeId);
  log(`Zoom: ${detail.constraint} → subtree ${plan.scopeType} (${plan.pair.length} linked node(s))`);
  refreshCorrectionUi();
}

// Rebuild the sentence with the suggested (or alternative) correction and show
// the re-parsed tree. The learner's own text is never touched.
async function showCorrected(variant = 'corrected') {
  if (!focus || !session) return;
  const isAlternative = variant === 'alternative';
  const edit = isAlternative ? focus.alternativeEdit : focus.edit;
  if (!edit) return;

  const target = focus;
  const cacheKey = isAlternative ? 'alternativeCorrected' : 'corrected';
  const modeValue = isAlternative ? 'alternative' : 'corrected';
  const logLabel = isAlternative ? 'Alternative corrected preview' : 'Corrected preview';

  if (!target[cacheKey]) {
    previewLoading = modeValue;
    refreshCorrectionUi();
    const text = applyEdit(session.payload, edit);
    let cp = null;
    try {
      const out = await postParse(text);
      if (!out.error) cp = out.payload;
    } catch (_e) { /* handled below */ }
    previewLoading = null;
    // The learner may have picked another error while the preview was built.
    if (focus !== target) return;
    if (!cp) {
      focusResult = { kind: 'still', message: 'Could not build the preview tree right now.' };
      refreshCorrectionUi();
      return;
    }
    applyStatuses(cp.tree, cp.node_details, cp.summary);
    const expected = expectedScopeWords(session.payload, target.scopeId, edit);
    target[cacheKey] = {
      payload: cp,
      text,
      scopeId: expected ? findScopeNode(cp, target.scopeType, expected) : null,
    };
  }

  correctionMode = modeValue;
  focusResult = null;
  renderer.setTree(target[cacheKey].payload.tree);
  if (target[cacheKey].scopeId) renderer.focusSubtree(target[cacheKey].scopeId, []);
  log(`${logLabel}: showing re-parsed tree (the learner's text is unchanged)`);
  refreshCorrectionUi();
}

function showOriginal() {
  if (!focus || !session) return;
  correctionMode = 'original';
  renderer.setTree(session.payload.tree);
  renderer.focusNode(focus.nodeId, focus.scopeId, focus.pair);
  renderer.select(focus.nodeId);
  refreshCorrectionUi();
}

// Called after a re-parse while a correction target is active: is the error the
// learner was working on still there, or did their own correction fix it?
function recheckFocus(payload) {
  const prev = focus;
  if (!prev) return;
  const hit = findTargetError(payload, prev);
  if (hit) {
    handleNodeSelect(hit.detail.id); // re-zooms on the error's new location
    focusResult = {
      kind: 'still',
      message: 'Still flagged — re-read the explanation and try again.',
    };
    refreshCorrectionUi();
    log(`Re-check: ${prev.constraint} re-identified by constraint + context (score ${hit.score.toFixed(2)})`);
    return;
  }
  const left = (payload.summary.violations || []).length;
  focus = null;
  correctionMode = 'original';
  focusResult = {
    kind: 'fixed',
    message: left
      ? `That error is fixed. ${left} other issue(s) remain — click a red node to continue.`
      : 'That error is fixed — this sentence is clean now.',
  };
  // The inspector described the error that is gone: it steps aside so the
  // correction panel carries the message on its own.
  renderNodeDetail(null, null, null);
  renderer.clearFocus();
  refreshCorrectionUi();
  log(`Re-check: ${prev.constraint} no longer fires — ${left} issue(s) left`);
}

// ---------------------------------------------------------------------------
// Rail navigation — exactly one active destination
// ---------------------------------------------------------------------------
// The rail never highlights two destinations at once, and never highlights
// none: `setActiveNav` is the single painter. The module that owns the
// workspace is remembered separately from the drawer or side panel that may
// be sitting on top of it, so closing an overlay hands the highlight back to
// the module underneath.
const NAV_TARGETS = {
  tutor: '#newSessionBtn',
  history: '#headerHistoryBtn',
  lessons: '.sidebar-item[data-view="lessons"]',
  builder: '.sidebar-item[data-view="builder"]',
  leaderboard: '.sidebar-item[data-view="leaderboard"]',
  achievements: '.sidebar-item[data-view="achievements"]',
  // A standalone quiz session is part of the Lessons module.
  quiz: '.sidebar-item[data-view="lessons"]',
};

// View names that mean the same destination in the rail.
const VIEW_ALIASES = { quiz: 'lessons' };

// The workspace module currently in charge: 'tutor' | 'lessons' | 'builder'.
let workspaceView = 'tutor';
// The drawer / side panel currently on top of the workspace, if any.
let overlayView = null;

function setActiveNav(viewName) {
  const resolve = (name) => {
    const selector = NAV_TARGETS[name]
      || (name ? `.sidebar-item[data-view="${name}"]` : null);
    return selector ? document.querySelector(selector) : null;
  };
  let target = resolve(viewName);
  // The rail always shows exactly one active destination: an unknown view
  // falls back to the module that owns the workspace.
  if (!target) target = resolve(workspaceView);
  document.querySelectorAll('.sidebar-item').forEach((btn) => {
    const on = Boolean(target) && btn === target;
    btn.classList.toggle('active', on);
    if (on) btn.setAttribute('aria-current', 'page');
    else btn.removeAttribute('aria-current');
  });
}

// The module that owns the workspace. It owns the rail highlight unless an
// overlay is on top of it.
function setWorkspaceView(viewName) {
  workspaceView = VIEW_ALIASES[viewName] || viewName;
  if (!overlayView) setActiveNav(workspaceView);
}

// A drawer or side panel takes the highlight while it is open; closing it
// restores the highlight of the workspace underneath.
function setOverlayView(viewName) {
  overlayView = viewName || null;
  setActiveNav(overlayView || workspaceView);
}

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

// Analysis history is an account-only feature: entries live in Supabase, scoped
// to the signed-in user. Guests have no server-side identity, so nothing is
// collected or persisted for them. This one-time cleanup drops entries written
// by older builds that cached guest history in localStorage.
function purgeLegacyGuestHistory() {
  try {
    localStorage.removeItem('syntutor_guest_history');
  } catch {
    // localStorage unavailable — nothing to clean up.
  }
}

export function boot() {
  renderer = new TreeRenderer(document.querySelector('#treeCanvas'), {
    onSelect: (id) => handleNodeSelect(id),
    onHover: () => {},
    describe: plainName,
  });
  wireEvents();
  initThemeAndMenu();
  purgeLegacyGuestHistory();
  initSidebar();
  // The rail starts on the Syntax Generator: exactly one active destination.
  setActiveNav(workspaceView);
  initSyntaxBuilder({ onStatusChange: (msg) => log(msg), setWorkspaceView });
  initQuiz({
    analyze: analyzeForQuiz,
    setQuizMode,
    progress,
    setChatTitle,
    lastChatTitle: () => lastAnalyzedText || '',
    setWorkspaceView,
    setOverlayView,
    showModelTree: showLessonModelTree,
    clearModelTree: clearLessonModelTree,
  });
  initResizers();
  syncInputClearBtn();
  transition(STATES.IDLE, 'system ready');
  log(`SynTutor engine ready \u2014 full-stack pipeline: spaCy + benepar + rule matrix (${isGuest ? 'guest mode' : 'authenticated'})`);
  maybeStartOnboarding();
}

function initThemeAndMenu() {
  applyTheme(getSavedTheme());
  updateAuthState();

  document.querySelector('#themeToggleBtn')?.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    applyTheme(current === 'dark' ? 'light' : 'dark');
  });

  document.querySelector('#identityChip')?.addEventListener('click', () => {
    toggleProfileMenu();
  });

  document.querySelector('#newSessionBtn')?.addEventListener('click', () => {
    enterTutorMode();
  });

  // The subtle × in the upper-right of the input pane: clears the text,
  // resets the highlights, and drops the workspace back to STATES.IDLE with
  // the empty canvas state (startNewSession owns all of that reset).
  // While the Syntax Builder is open the input box mirrors the canvas, so the
  // × clears the canvas instead.
  document.querySelector('#inputClearBtn')?.addEventListener('click', () => {
    if (state === STATES.PROCESSING) return;
    if (isBuilderOpen()) {
      clearBuilder();
      syncInputClearBtn();
      return;
    }
    startNewSession();
    syncInputClearBtn();
  });

  // "Done" leaves the standalone Syntax Builder and lands back in the plain
  // analyzer — put Syntax Generator (and its clear affordance) in charge.
  document.querySelector('#builderDone')?.addEventListener('click', () => {
    setWorkspaceView('tutor');
  });

  document.querySelector('#headerHistoryBtn')?.addEventListener('click', () => {
    openHistoryDrawer();
  });

  initProfileMenu();
}

function initSidebar() {
  const backdrop = document.querySelector('#appSidebarBackdrop');
  const sidebar = document.querySelector('#appSidebar');
  const toggle = document.querySelector('#sidebarToggleBtn');
  const mobileNav = document.querySelector('#mobileNavBtn');

  // Canvases live in the workspace column, so re-fit them once the rail
  // finishes resizing; the fallback timer covers transitions that never run.
  let resizeFallback = 0;
  const dispatchResize = () => {
    window.clearTimeout(resizeFallback);
    window.dispatchEvent(new Event('resize'));
  };
  const scheduleResize = () => {
    window.clearTimeout(resizeFallback);
    resizeFallback = window.setTimeout(dispatchResize, 400);
  };

  const syncRailState = () => {
    const expanded = Boolean(sidebar?.classList.contains('expanded'));
    const label = expanded ? 'Collapse sidebar' : 'Expand sidebar';
    // Only write when needed: this also self-corrects the stale
    // aria-expanded writes tree-quiz.js still makes for the old drawer.
    if (toggle && toggle.getAttribute('aria-expanded') !== String(expanded)) {
      toggle.setAttribute('aria-expanded', String(expanded));
    }
    if (toggle) {
      if (toggle.getAttribute('aria-label') !== label) toggle.setAttribute('aria-label', label);
      if (toggle.title !== label) toggle.title = label;
    }
  };

  const setExpanded = (next) => {
    sidebar?.classList.toggle('expanded', next);
    syncRailState();
    scheduleResize();
  };
  const toggleExpanded = () => setExpanded(!sidebar?.classList.contains('expanded'));

  // The rail expands only via the toggle button (or the brand monogram when
  // collapsed) — never on hover.
  toggle?.addEventListener('click', toggleExpanded);
  const isDesktop = () => window.matchMedia('(min-width: 761px)').matches;
  document.querySelector('#sidebarBrandBtn')?.addEventListener('click', () => {
    if (!isDesktop()) return;
    setExpanded(!sidebar?.classList.contains('expanded'));
  });
  sidebar?.addEventListener('transitionend', (e) => {
    if (e.propertyName === 'width' && e.target === sidebar) dispatchResize();
  });
  let railKey = String(sidebar?.classList.contains('expanded'));
  new MutationObserver(() => {
    const next = String(sidebar?.classList.contains('expanded'));
    if (next === railKey) return;
    railKey = next;
    syncRailState();
    scheduleResize();
  }).observe(sidebar, { attributes: true, attributeFilter: ['class'] });
  syncRailState();

  // Small screens open the rail as a slide-over drawer (tree-quiz.js also
  // toggles the backdrop directly, so mirror its aria state).
  const syncDrawerAria = () => {
    const active = Boolean(backdrop?.classList.contains('active'));
    if (mobileNav && mobileNav.getAttribute('aria-expanded') !== String(active)) {
      mobileNav.setAttribute('aria-expanded', String(active));
    }
  };
  new MutationObserver(syncDrawerAria).observe(backdrop, { attributes: true, attributeFilter: ['class'] });
  const open = () => {
    backdrop?.classList.add('active');
    syncDrawerAria();
  };
  const close = () => {
    backdrop?.classList.remove('active');
    syncDrawerAria();
  };
  syncDrawerAria();

  mobileNav?.addEventListener('click', () => {
    if (backdrop?.classList.contains('active')) close();
    else open();
  });
  document.querySelector('#closeSidebarBtn')?.addEventListener('click', close);
  backdrop?.addEventListener('click', (e) => {
    if (e.target === backdrop) close();
  });

  document.querySelectorAll('.sidebar-item[data-view]').forEach((btn) => {
    btn.addEventListener('click', () => {
      if (btn.id === 'newSessionBtn') return;
      switch (btn.dataset.view) {
        case 'builder':
          enterBuilderMode();
          break;
        case 'lessons':
          enterLessonsMode();
          break;
        case 'leaderboard':
        case 'achievements':
          enterPanelMode(btn.dataset.view);
          break;
        default:
          // Syntax Generator: leave any lesson/quiz/builder session and
          // return to the plain analyzer.
          enterTutorMode();
          close();
      }
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape' || !backdrop?.classList.contains('active')) return;
    const quizPanel = document.querySelector('#quizPanel');
    if (quizPanel && !quizPanel.hidden) return;
    close();
  });
}

// ---------------------------------------------------------------------------
// Mode switching — teardown first, then setup
// ---------------------------------------------------------------------------
// The workspace has three modes: the Grammar Tutor (Syntax Generator), the
// Lessons module, and the standalone Syntax Builder. Every switch starts by
// dismantling the previous mode completely — no lesson panels, no builder
// canvas or floating controls, no canvas overlay, no node diagnostics — so
// nothing from one mode can bleed into the next.

// Close the History drawer and hand the rail highlight back to the module
// underneath it.
function closeHistoryDrawer() {
  document.querySelector('#historyDrawerBackdrop')?.classList.remove('active');
  if (overlayView === 'history') setOverlayView(null);
}

// Tear the workspace down to a clean slate: no module owns anything.
function teardownWorkspace() {
  // Lessons: the picker overlay, the lesson panels, the guide card, the quiz
  // panel in the rail, and the side sub-panel.
  closeQuizView();
  clearActiveLesson();
  // Syntax Builder: the canvas, its floating controls, and the inline editor
  // or context menu it may have opened.
  closeBuilderView();
  // A lesson may have left the valid benepar tree on #treeCanvas; it belongs to
  // the lesson, not to the next workspace mode.
  clearLessonModelTree();
  // The canvas overlay and the node inspector belong to the Grammar Tutor.
  clearDiagnostics();
  // ...and so does the correction panel: a correction never survives a
  // switch to another workspace module.
  resetFocusState();
  // Back to the plain analyzer surfaces.
  const tree = document.querySelector('#treeCanvas');
  const builder = document.querySelector('#builderCanvas');
  const empty = document.querySelector('#emptyTreeState');
  const controls = document.querySelector('#canvasControls');
  if (tree) tree.hidden = false;
  if (builder) builder.hidden = true;
  if (empty) empty.classList.remove('hidden');
  if (controls) controls.hidden = true;
  // The upper-right pane returns to a single-surface input editor: the
  // lesson controls are gone and the editor is locked again.
  document.body.classList.remove('lesson-view');
  const ta = document.querySelector('#inputText');
  const editor = document.querySelector('.input-editor');
  if (ta) {
    ta.readOnly = true;
    ta.classList.remove('editing');
  }
  editor?.classList.remove('editing');
}

// Syntax Generator: the plain analyzer, with a fresh session.
function enterTutorMode() {
  teardownWorkspace();
  setQuizMode(false);
  setWorkspaceView('tutor');
  startNewSession();
  syncInputClearBtn();
  // Dismiss the mobile drawer so the workspace is visible again.
  document.querySelector('#appSidebarBackdrop')?.classList.remove('active');
}

// Lessons: the module picker and its in-place builder. The Grammar Tutor's
// blur/pipeline listeners stay quiet — the lesson owns the input box.
function enterLessonsMode() {
  teardownWorkspace();
  setQuizMode(true);
  setWorkspaceView('lessons');
  openQuizView('lessons');
}

// Syntax Builder: the standalone node editor. No Grammar Tutor pipeline and
// no diagnostics may fire while it owns the canvas.
function enterBuilderMode() {
  teardownWorkspace();
  setQuizMode(false);
  setWorkspaceView('builder');
  openBuilderView();
}

// Leaderboard / Achievements: a side panel next to the rail. The workspace
// underneath keeps its own mode; the panel takes the rail highlight while it
// is open.
function enterPanelMode(viewName) {
  teardownWorkspace();
  setQuizMode(false);
  setWorkspaceView('tutor');
  openQuizView(viewName);
}

// Replaying a past analysis: the workspace returns to the Syntax Generator
// (every other mode is torn down first) and the stored sentence is analyzed
// again.
function replayHistoryEntry(sentence) {
  teardownWorkspace();
  setQuizMode(false);
  setWorkspaceView('tutor');
  setChatTitle(sentence);
  const ta = document.querySelector('#inputText');
  if (ta) ta.value = sentence;
  recordedTexts.add(sentence);
  runPipeline({ isReplay: true });
}

// ---------------------------------------------------------------------------
// Workspace splitters — LeetCode-style gutters between the panes
// ---------------------------------------------------------------------------
// #colResizer splits the canvas column from the right column (.app-main's
// --col-split), #rowResizer splits the input pane from the explain pane
// (.pane-side's --row-split). Both vars are unitless fractions (0..1) of the
// grid content box, written inline by the drag handler; the handles sit in the
// 8px gap between panels. Double-click restores the 0.58 default. Canvas
// redraws ride a rAF-throttled resize event.
function initResizers() {
  const main = document.querySelector('.app-main');
  const sidePane = document.querySelector('.pane-side');
  let frame = 0;
  const dispatchResize = () => {
    window.cancelAnimationFrame(frame);
    frame = window.requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));
  };

  const wire = (sel, container, prop, axis, min, max) => {
    const gutter = document.querySelector(sel);
    if (!gutter || !container) return;
    gutter.addEventListener('pointerdown', (e) => {
      if (e.pointerType === 'mouse' && e.button !== 0) return;
      e.preventDefault();
      // Synthetic pointer events (tests) have no active pointer, so capture
      // is best-effort: real drags still get it, and the listeners below
      // keep the drag working either way.
      try { gutter.setPointerCapture(e.pointerId); } catch { /* no active pointer */ }
      gutter.classList.add('dragging');
      document.body.classList.add('is-resizing');
      const rect = container.getBoundingClientRect();
      // Percentage grid tracks resolve against the content box, so the drag
      // math strips .app-main's padding (8px per side) off the measurement.
      const cs = window.getComputedStyle(container);
      const padA = parseFloat(axis === 'x' ? cs.paddingLeft : cs.paddingTop) || 0;
      const padB = parseFloat(axis === 'x' ? cs.paddingRight : cs.paddingBottom) || 0;
      const total = (axis === 'x' ? rect.width : rect.height) - padA - padB;
      const origin = (axis === 'x' ? rect.left : rect.top) + padA;
      if (!total) return;
      const move = (ev) => {
        const pos = (axis === 'x' ? ev.clientX : ev.clientY) - origin;
        const pct = Math.min(max, Math.max(min, (pos / total) * 100));
        container.style.setProperty(prop, (pct / 100).toFixed(4));
        dispatchResize();
      };
      const up = (ev) => {
        if (gutter.hasPointerCapture?.(ev.pointerId)) gutter.releasePointerCapture(ev.pointerId);
        gutter.classList.remove('dragging');
        document.body.classList.remove('is-resizing');
        gutter.removeEventListener('pointermove', move);
        gutter.removeEventListener('pointerup', up);
        gutter.removeEventListener('pointercancel', up);
        dispatchResize();
      };
      gutter.addEventListener('pointermove', move);
      gutter.addEventListener('pointerup', up);
      gutter.addEventListener('pointercancel', up);
      move(e);
    });
    gutter.addEventListener('dblclick', () => {
      container.style.removeProperty(prop);
      dispatchResize();
    });
  };

  wire('#colResizer', main, '--col-split', 'x', 35, 75);
  wire('#rowResizer', sidePane, '--row-split', 'y', 22, 78);

  // Any layout change inside the workspace — a resizer drag, the rail
  // expanding/collapsing, or a sub-panel sliding open — reflows the canvases
  // and textareas in real time. ResizeObserver fires synchronously with the
  // layout, and the rAF-throttled dispatch coalesces bursts.
  if (typeof ResizeObserver !== 'undefined') {
    const ro = new ResizeObserver(() => dispatchResize());
    for (const node of [main, sidePane, document.querySelector('.canvas-wrap'), document.querySelector('.pane-side')]) {
      if (node) ro.observe(node);
    }
  }

  // A left sub-panel opening/closing shifts the workspace grid on desktop;
  // re-fit the canvases once its slide transition ends.
  for (const sel of ['#subpanelPlaceholder', '#historyDrawerBackdrop']) {
    document.querySelector(sel)?.addEventListener('transitionend', (e) => {
      if (e.propertyName === 'width') dispatchResize();
    });
  }
}

function setChatTitle(title) {
  const el = document.querySelector('#chatTitle');
  if (!el) return;
  el.textContent = title && title.trim() ? title : 'Untitled chat...';
  el.title = title && title.trim() ? title : '';
}

function openHistoryDrawer() {
  if (isGuest) return; // history is an account-only feature
  // History and the tree-quiz sub-panel share the same slide-out slot —
  // opening one dismisses the other.
  closeSubpanel();
  document.querySelector('#historyDrawerBackdrop')?.classList.add('active');
  // The drawer owns the rail highlight while it is open; closing it hands
  // the highlight back to the module underneath.
  setOverlayView('history');
  loadAndRenderHistory();
}

function openAuthModal(mode = 'signin') {
  const backdrop = document.querySelector('#authModalBackdrop');
  if (!backdrop) return;
  // The add-account flow runs while already signed in, so offering
  // "Continue as guest" there is meaningless — hide that row.
  const guestRow = backdrop.querySelector('.modal-close-row');
  if (guestRow) guestRow.hidden = mode === 'add-account';
  backdrop.classList.add('active');
  const email = document.querySelector('#authEmail');
  if (email) setTimeout(() => email.focus(), 0);
}

function closeAuthModal() {
  const backdrop = document.querySelector('#authModalBackdrop');
  backdrop?.classList.remove('active');
  // Restore the guest row so the next open starts from the default state.
  const guestRow = backdrop?.querySelector('.modal-close-row');
  if (guestRow) guestRow.hidden = false;
}

function applyTheme(theme) {
  setTheme(theme, document.querySelector('#themeIcon'));
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
    chip.title = 'Account menu';
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
    cachedHistory = [];
    closeHistoryDrawer();
  }
  renderProfileMenu();
  refreshProfileStats();
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
  if (open) {
    showProfileMenuMain();
    refreshProfileStats();
  }
  if (open) focusFirstMenuItem();
}

function refreshProfileStats() {
  const box = document.querySelector('#profileStats');
  if (!box) return;
  if (!isGuest && clerk?.session && supabase) {
    box.innerHTML = '<span>Loading progress\u2026</span>';
    loadPlayerProgress().then((p) => {
      if (!box) return;
      const stats = p || { xp: 0, level: 0 };
      const level = levelFromXp(stats.xp);
      box.innerHTML = '';
      const row = document.createElement('div');
      row.className = 'profile-stats-stats';
      const lvl = document.createElement('span');
      lvl.className = 'profile-stats-level';
      lvl.textContent = `Level ${stats.level}`;
      const xp = document.createElement('span');
      xp.className = 'profile-stats-xp';
      xp.textContent = `${stats.xp} XP`;
      row.appendChild(lvl);
      row.appendChild(xp);
      box.appendChild(row);
      const bar = document.createElement('div');
      bar.className = 'profile-stats-bar';
      const fill = document.createElement('div');
      fill.className = 'profile-stats-fill';
      fill.style.width = `${level.span ? Math.min(100, Math.round((level.into / level.span) * 100)) : 0}%`;
      bar.appendChild(fill);
      box.appendChild(bar);
      const note = document.createElement('span');
      note.textContent = `${level.into} / ${level.span} XP to Level ${stats.level + 1}`;
      box.appendChild(note);
    }).catch(() => {
      if (box) box.textContent = 'Progress unavailable right now.';
    });
  } else {
    box.textContent = 'Guest mode \u2014 sign in to earn XP and achievements.';
  }
}

function visibleMenuItems() {
  const menu = document.querySelector('#profileMenu');
  if (!menu) return [];
  // offsetParent excludes items inside the currently-hidden view, so arrow
  // keys never jump into the view that isn't showing.
  return [...menu.querySelectorAll('.profile-menu-item, .profile-account-item')]
    .filter((el) => !el.hidden && el.offsetParent !== null);
}

function focusFirstMenuItem() {
  visibleMenuItems()[0]?.focus();
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
    openAuthModal('add-account');
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
    openAuthModal('signin');
  });
  document.addEventListener('click', (e) => {
    if (profileMenuOpen && !e.target.closest('.profile-anchor')) setProfileMenu(false);
  });
  document.querySelector('#profileMenu')?.addEventListener('keydown', (e) => {
    const items = visibleMenuItems();
    if (!items.length) return;
    const idx = items.indexOf(document.activeElement);
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      (items[idx + 1] ?? items[0]).focus();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      (items[idx - 1] ?? items[items.length - 1]).focus();
    } else if (e.key === 'Home') {
      e.preventDefault();
      items[0].focus();
    } else if (e.key === 'End') {
      e.preventDefault();
      items[items.length - 1].focus();
    } else if (e.key === 'Escape') {
      setProfileMenu(false);
      document.querySelector('#identityChip')?.focus();
    }
  });
}

function wireEvents() {
  const ta = document.querySelector('#inputText');
  // Single-click editing (empty input / single sentence / active sentence /
  // blank space): this listener is registered before activateSentenceAtCaret,
  // so once readOnly flips false the sentence-nav click short-circuits.
  ta.addEventListener('click', () => enterEditMode());
  ta.addEventListener('scroll', syncHighlightScroll);
  ta.addEventListener('input', () => {
    historySpans = [];
    renderInputHighlights(ta.value);
    syncInputClearBtn();
    // A correction is open: re-parse as the learner types so the tree (and
    // the re-check of the error) follow the edit.
    if (focus) scheduleLiveReparse();
  });
  // Locked passages (session.sentences.length > 1) render one interactive
  // span per sentence in the highlight overlay. Inspecting a different
  // sentence reruns the pipeline for it WITHOUT unlocking the textarea;
  // clicking the active sentence — or double-clicking a span — edits.
  // The action runs on mousedown + preventDefault: that keeps focus where it
  // is, so the blur → highlight re-render never swaps the span out from under
  // the click.
  const layer = document.querySelector('#inputHighlights');
  layer?.addEventListener('mousedown', (e) => {
    if (ta.readOnly !== true) return;
    const span = e.target.closest?.('.sentence-span');
    if (!span) return;
    e.preventDefault();
    if (state === STATES.PROCESSING) return;
    const idx = Number(span.dataset.sentIdx);
    if (!Number.isInteger(idx)) return;
    if (idx === (session?.sentence_index ?? -1)) { enterEditMode(); return; }
    if (workspaceView === 'builder') return;   // the builder owns the canvas
    if (quizMode) { analyzeForQuiz(ta.value, idx); return; }
    // Inspect: flip the target sentence immediately (so the highlight moves
    // as soon as the payload lands) and rebuild the canvas for it.
    if (session) session.sentence_index = idx;
    runPipeline({ index: idx, isSentenceNav: true });
  });
  layer?.addEventListener('dblclick', (e) => {
    if (ta.readOnly === true && e.target.closest?.('.sentence-span')) enterEditMode();
  });
  ta.addEventListener('blur', () => {
    // The Syntax Builder owns the workspace: no Grammar Tutor pipeline and
    // no diagnostics may run while it is open.
    if (workspaceView === 'builder') return;
    if (quizMode) {
      returnToLocked();
      setQuizHintText();
      const currentIndex = (session?.payload?.meta?.target_sentence || 1) - 1;
      analyzeForQuiz(ta.value, currentIndex);
      return;
    }
    const changed = ta.value !== lastAnalyzedText;
    returnToLocked();
    // With a correction open the re-analysis has to look at the same sentence
    // the correction belongs to, otherwise the error could not be re-checked.
    if (changed) runPipeline(focus ? { index: focus.sentenceIndex } : {});
  });
  ta.addEventListener('click', activateSentenceAtCaret);
  ta.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && ta.readOnly === false) {
      // Exit edit mode: blur re-locks the textarea and the blur handler
      // reruns the pipeline only when the text actually changed.
      e.preventDefault();
      ta.blur();
      return;
    }
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      if (workspaceView !== 'builder') runPipeline();
      return;
    }
    if (e.key === 'Enter' && ta.readOnly) {
      e.preventDefault();
      activateSentenceAtCaret();
    }
  });

  const drawer = document.querySelector('#historyDrawerBackdrop');
  document.querySelector('#closeDrawerBtn')?.addEventListener('click', () => {
    closeHistoryDrawer();
  });
  drawer?.addEventListener('click', (e) => {
    if (e.target === drawer) closeHistoryDrawer();
  });

  // Escape closes an open left sub-panel first (the tree-quiz panel, then
  // History); stopImmediatePropagation keeps the sidebar's own Escape from
  // also dismissing the mobile drawer in the same keypress. Either way the
  // rail highlight goes back to the module underneath.
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    const sub = document.querySelector('#subpanelPlaceholder');
    if (sub?.classList.contains('active')) {
      closeSubpanel();
      e.stopImmediatePropagation();
      return;
    }
    if (drawer?.classList.contains('active')) {
      closeHistoryDrawer();
      e.stopImmediatePropagation();
    }
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
    if (isGuest || !supabase || !clerk?.user?.id || !cachedHistory.length) return;
    if (!confirm('Clear all analysis history? This action cannot be undone.')) return;

    const { error } = await supabase
      .from('analysis_history')
      .delete()
      .eq('user_id', clerk.user.id);

    if (error) {
      alert('Failed to clear history: ' + error.message);
      return;
    }
    cachedHistory = [];
    renderHistoryItems();
  });
}

const DEFAULT_INPUT_HINT = 'Click the panel to write a sentence. SynTutor builds its syntax tree and analysis automatically.';

function setHint(editing) {
  // The input panel's prompt lives on the textarea itself: the highlight
  // overlay never renders text of its own, so the two can never overlap.
  // The Syntax Builder owns the panel while it is open \u2014 its prompt stays
  // until the builder closes.
  if (!editing && isBuilderOpen()) return;
  const ta = document.querySelector('#inputText');
  if (ta) {
    ta.placeholder = editing
      ? 'Editing \u2014 click away to lock and analyze. (Type above)'
      : DEFAULT_INPUT_HINT;
  }
}

function setQuizHintText() {
  const ta = document.querySelector('#inputText');
  if (ta) ta.placeholder = quizInputHint();
}

// The session doubles as the source for locked-mode sentence navigation:
// `sentences` holds the passage's sentence boundaries and `sentence_index`
// is the sentence currently rendered on the canvas.
function buildSession(payload) {
  return {
    payload,
    sentences: payload.parse.sentences || [],
    sentence_index: (payload.meta.target_sentence || 1) - 1,
  };
}

// The × in the upper-right of the input pane only shows while there is
// something to clear (CSS additionally scopes it to the Syntax Generator tab).
function syncInputClearBtn() {
  const btn = document.querySelector('#inputClearBtn');
  const ta = document.querySelector('#inputText');
  if (!btn || !ta) return;
  btn.hidden = !ta.value.trim();
}

// Locked -> edit: unlock the textarea and hide the highlight overlay (the
// .editing class on .input-editor drops it from the layout) so typing goes
// straight into the textarea.
function enterEditMode() {
  const ta = document.querySelector('#inputText');
  const editor = document.querySelector('.input-editor');
  if (!ta) return;
  // The Syntax Builder owns the input box: it mirrors the words on the
  // canvas, so it stays locked (and the canvas stays the only place to type).
  if (isBuilderOpen()) return;
  if (ta.readOnly === false) { ta.focus(); return; }
  editor?.classList.add('editing');
  ta.readOnly = false;
  ta.classList.add('editing');
  setHint(true);
  ta.focus();
}

function returnToLocked(payload = null) {
  const ta = document.querySelector('#inputText');
  const editor = document.querySelector('.input-editor');
  ta.readOnly = true;
  ta.classList.remove('editing');
  editor?.classList.remove('editing');
  setHint(false);
  renderInputHighlights(ta.value, payload);
}

function startNewSession() {
  if (state === STATES.PROCESSING) return;

  clearActiveLesson();
  recordedTexts.clear();
  session = null;
  lastAnalyzedText = null;
  historySpans = [];
  setChatTitle('');

  const ta = document.querySelector('#inputText');
  const editor = document.querySelector('.input-editor');
  ta.value = '';
  ta.readOnly = true;
  ta.classList.remove('editing');
  editor?.classList.remove('editing');
  setHint(false);
  renderInputHighlights('');
  syncInputClearBtn();
  syncHighlightScroll();

  renderer.select(null);
  renderer.clear();
  clearOverlay();
  renderNodeDetail(null, null, null);
  resetFocusState();

  document.querySelector('#emptyTreeState')?.classList.remove('hidden');

  transition(STATES.IDLE, 'new session started');
  log('New session \u2014 canvas, input, and analysis cleared.');
}

function activateSentenceAtCaret() {
  const ta = document.querySelector('#inputText');
  if (!session || ta.readOnly !== true) return;
  if (workspaceView === 'builder') return;   // the builder owns the canvas
  if (ta.selectionStart !== ta.selectionEnd) return;
  const sents = session.payload.parse.sentences || [];
  const caret = ta.selectionStart;
  const hit = sents.find((s) => caret >= s.start && caret < s.end);
  if (!hit) return;
  const alreadyTarget = hit.ordinal - 1 === (session.payload.meta.target_sentence || 1) - 1;
  if (quizMode) {
    if (!alreadyTarget) analyzeForQuiz(ta.value, hit.ordinal - 1);
    return;
  }
  if (!alreadyTarget) runPipeline({ index: hit.ordinal - 1, isSentenceNav: true });
}

function failPipeline(title, lines) {
  showCanvasMessage('error', title, lines);
  renderDiagnostic(title, lines);
  transition(STATES.VIEWING, 'request failed -> diagnostic shown');
  log(`Request failed: ${title} \u2014${lines[0] || ''}`);
}

async function postParse(text, index = null) {
  const body = { text };
  if (index !== undefined && index !== null) body.sentence_index = index;
  const res = await fetch(`${API_BASE}/api/parse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    return { error: { status: res.status, error: data.error, hint: data.hint } };
  }
  return { payload: await res.json() };
}

function setQuizMode(active) {
  quizMode = active;
  if (renderer) renderer.setInteractive(!active);
}

// ---------------------------------------------------------------------------
// Lessons: the read-only model tree
// ---------------------------------------------------------------------------
// True while #treeCanvas holds a lesson model tree. The tree can outlive the
// Model state (Practice hides the canvas but the renderer keeps the tree), so
// teardown uses this flag to clear a lesson tree without wiping the Grammar
// Tutor's own analysis when an unrelated panel opens.
let lessonModelActive = false;
// Module lessons render a read-only parsed tree on #treeCanvas. Legacy
// single-unit lessons may still hand #builderCanvas to the builder; this is the
// counterpart that hands the shared canvas back to the static renderer without
// touching the lesson panels or the tutor's history/session state. Callers
// decide whether to paint a tree or clear it.
function prepareLessonModelCanvas() {
  const treeCanvas = document.querySelector('#treeCanvas');
  const builderCanvas = document.querySelector('#builderCanvas');
  const controls = document.querySelector('#canvasControls');
  const hint = document.querySelector('#builderHint');
  const target = document.querySelector('#builderTarget');
  const empty = document.querySelector('#emptyTreeState');
  if (builderCanvas) builderCanvas.hidden = true;
  if (treeCanvas) {
    treeCanvas.hidden = false;
    treeCanvas.setAttribute('aria-label', 'Parsed syntax tree (read-only)');
  }
  if (controls) controls.hidden = true;
  if (hint) hint.hidden = true;
  if (target) target.hidden = true;
  if (empty) empty.classList.add('hidden');
  document.querySelector('.builder-toast')?.classList.remove('show');
  document.querySelector('#loadingIndicator')?.classList.remove('visible');
  document.body.classList.remove('builder-active');
  document.body.classList.add('lesson-model');
  clearOverlay();
  if (renderer) renderer.setInteractive(false);
}

function showLessonModelTree(payload, focusId = null) {
  if (!payload || !payload.tree || !renderer) return;
  prepareLessonModelCanvas();
  lessonModelActive = true;
  applyStatuses(payload.tree, payload.node_details || {}, payload.summary || {});
  renderer.setTree(payload.tree);
  if (focusId) renderer.select(focusId);
  // The canvas was hidden while the builder owned it; refit once the browser
  // has had a chance to lay the visible canvas out.
  requestAnimationFrame(() => window.dispatchEvent(new Event('resize')));
}

// Drop the lesson model tree. Used when switching examples/sections and when
// the lesson view is torn down, so no ghost tree survives either swap. Returns
// true when a tree was actually cleared. `force` also clears the Grammar
// Tutor's tree when a lesson is opening over it; teardown omits it so opening
// a side panel does not wipe an analysis the tutor should keep.
function clearLessonModelTree({ force = false } = {}) {
  if (!renderer) return false;
  if (!force && !lessonModelActive) return false;
  prepareLessonModelCanvas();
  renderer.clear();
  renderer.setInteractive(!quizMode);
  document.body.classList.remove('lesson-model');
  lessonModelActive = false;
  const treeCanvas = document.querySelector('#treeCanvas');
  if (treeCanvas) {
    treeCanvas.setAttribute('aria-label',
      'Interactive syntax tree; click a node, or use arrow keys and Enter');
  }
  return true;
}

// ---------------------------------------------------------------------------
// Gamification: XP, levels, and the permanent leaderboard.
// XP is only banked for signed-in users (guests see the UI but nothing saves).
// ---------------------------------------------------------------------------
function progressAvailable() {
  return !isGuest && !!clerk?.user?.id && !!supabase;
}

function playerDisplayName() {
  const user = clerk?.user;
  return user?.firstName
    || user?.username
    || user?.primaryEmailAddress?.emailAddress?.split('@')[0]
    || 'Learner';
}

async function loadPlayerProgress() {
  if (!progressAvailable()) return null;
  const { data, error } = await supabase
    .from('player_stats')
    .select('xp, level')
    .eq('user_id', clerk.user.id)
    .maybeSingle();
  if (error) {
    console.warn('Failed to load player progress:', error.message);
    return null;
  }
  return data || { xp: 0, level: 0 };
}

async function awardPlayerXp(amount) {
  if (!progressAvailable() || !Number.isFinite(amount) || amount <= 0) return null;
  const current = await loadPlayerProgress();
  const xp = (current?.xp || 0) + amount;
  const { level } = levelFromXp(xp);
  const { error } = await supabase.from('player_stats').upsert({
    user_id: clerk.user.id,
    display_name: playerDisplayName(),
    xp,
    level,
    updated_at: new Date().toISOString(),
  }, { onConflict: 'user_id' });
  if (error) {
    console.warn('Failed to save XP:', error.message);
    return null;
  }
  return { xp, ...levelFromXp(xp), earned: amount };
}

async function loadLeaderboard(limit = 25) {
  if (!supabase) return null;
  const { data, error } = await supabase
    .from('player_stats')
    .select('user_id, display_name, xp, level')
    .order('level', { ascending: false })
    .order('xp', { ascending: false })
    .limit(limit);
  if (error) {
    console.warn('Failed to load the leaderboard:', error.message);
    return null;
  }
  return data;
}

async function loadQuizProgress() {
  if (!supabase || !clerk?.user?.id) return [];
  const { data, error } = await supabase
    .from('quiz_progress')
    .select('rule_id, completed_count, perfect_count')
    .eq('user_id', clerk.user.id);
  if (error) {
    console.warn('Failed to load quiz progress:', error.message);
    return [];
  }
  return data || [];
}

// Records a finished quiz run (upserts a completion for the rule) and returns
// the achievement ids that this run newly unlocked.
async function trackQuizCompletion({ ruleId, perfect }) {
  if (!progressAvailable()) return { newlyUnlocked: [], ran: false };
  const before = computeUnlocked(await loadQuizProgress());
  const existing = await supabase
    .from('quiz_progress')
    .select('completed_count, perfect_count')
    .eq('user_id', clerk.user.id)
    .eq('rule_id', ruleId)
    .maybeSingle();
  const prev = existing?.error ? {} : (existing?.data || {});
  const { error } = await supabase.from('quiz_progress').upsert({
    user_id: clerk.user.id,
    rule_id: ruleId,
    completed_count: (prev.completed_count || 0) + 1,
    perfect_count: (prev.perfect_count || 0) + (perfect ? 1 : 0),
    last_completed_at: new Date().toISOString(),
  }, { onConflict: 'user_id,rule_id' });
  if (error) {
    console.warn('Failed to record quiz completion:', error.message);
    return { newlyUnlocked: [], ran: false };
  }
  const after = computeUnlocked(await loadQuizProgress());
  return {
    newlyUnlocked: [...after].filter((id) => !before.has(id)),
    ran: true,
  };
}

const progress = {
  isAvailable: progressAvailable,
  myId: () => (clerk?.user?.id ? clerk.user.id : null),
  load: loadPlayerProgress,
  award: awardPlayerXp,
  leaderboard: loadLeaderboard,
  getQuizProgress: loadQuizProgress,
  trackCompletion: trackQuizCompletion,
};

// Quiz-only analysis: parses the sentence, renders its tree, and returns the
// payload WITHOUT touching history, highlights, or the locked/editable state.
async function analyzeForQuiz(text, index = null) {
  if (!text || !text.trim()) return null;
  const clean = text.trim();
  clearOverlay();
  renderer.select(null);
  renderNodeDetail(null, null, null);
  resetFocusState();
  let payload;
  try {
    const out = await postParse(clean, index);
    if (out.error) {
      showCanvasMessage('error', 'Unable to analyze', [out.error.error || 'The backend rejected the request.']);
      return null;
    }
    payload = out.payload;
  } catch (_e) {
    showCanvasMessage('error', 'Backend unreachable', [
      'The SynTutor NLP server is not responding.',
      'Start it with:  python3 server/app.py',
    ]);
    return null;
  }
  applyStatuses(payload.tree, payload.node_details, payload.summary);
  session = buildSession(payload);
  lastAnalyzedText = clean;
  historySpans = [];
  const input = document.querySelector('#inputText');
  if (input?.value.trim() === clean) renderInputHighlights(clean);
  document.querySelector('#emptyTreeState')?.classList.add('hidden');
  renderer.setTree(payload.tree);
  transition(STATES.VIEWING, 'quiz sentence analyzed');
  return payload;
}

async function runPipeline(opts = {}) {
  if (state === STATES.PROCESSING) {
    // A live re-parse that landed while the previous run was still in flight
    // is re-queued instead of dropped, so the tree always catches up.
    if (opts.isLive) liveReparsePending = true;
    return;
  }
  // Only the Grammar Tutor runs the analysis pipeline: the Lessons module
  // and the Syntax Builder own the workspace in their own way.
  if (workspaceView !== 'tutor') return;
  transition(STATES.PROCESSING, 'user submits text');
  setLoadingIndicator(true);
  try {
    await executePipeline(opts);
  } finally {
    setLoadingIndicator(false);
    if (liveReparsePending) {
      liveReparsePending = false;
      scheduleLiveReparse();
    }
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

  // A fresh analysis replaces whatever correction was on screen: sentence
  // navigation and a replay start from a clean slate. A live re-parse keeps
  // the correction target — that is the one run whose whole point is to
  // re-check it.
  if (opts.isSentenceNav || opts.isReplay) resetFocusState();
  else if (!focus) refreshCorrectionUi();

  const text = document.querySelector('#inputText').value.trim();
  if (!text) {
    showCanvasMessage('error', 'No analyzable sentence', ['Enter some English text first, then submit it.']);
    renderDiagnostic('No analyzable sentence', ['Enter some English text first, then submit it.']);
    transition(STATES.IDLE, 'empty input -> back to idle');
    return;
  }
  log(`Stage 1: user input captured \u2014 ${JSON.stringify(text)}`);

  const target = opts.index !== undefined && opts.index !== null ? `sentence #${opts.index + 1}` : 'first sentence';
  log(`Stage 2: POST ${API_BASE}/api/parse (target: ${target})`);
  let payload;
  try {
    const out = await postParse(text, opts.index);
    if (out.error) {
      const { status, error, hint } = out.error;
      const title = status === 503
        ? 'NLP models unavailable'
        : status === 422 ? 'Unable to produce a parse' : `Backend error (HTTP ${status})`;
      failPipeline(title, [error || 'The backend rejected the request.', hint || ''].filter(Boolean));
      return;
    }
    payload = out.payload;
  } catch (_e) {
    failPipeline('Backend unreachable', [
      'The SynTutor NLP server is not responding.',
      'Start it with:  python3 server/app.py',
    ]);
    return;
  }
  log(`Stage 2: payload received (${Object.keys(payload.nodes).length} nodes) \u00b7${payload.meta.backend}`);

  const tokens = payload.parse.tokens;
  const posInfo = tokens.map((t) => `${t.t}/${t.pos}`).join(' ');
  log(`Stage 3: spaCy tokenization + POS \u2014 ${posInfo}`);
  if (payload.meta.sentence_count > 1) {
    log(`Stage 3: ${payload.meta.sentence_count} sentence(s) detected \u2014 analyzing sentence${payload.meta.target_sentence} (deterministic policy)`);
  }

  log(`Stage 4: benepar parse string \u2014 ${payload.parse.parse_string}`);

  applyStatuses(payload.tree, payload.node_details, payload.summary);
  const s = payload.summary;
  log(`Stage 5: rule-matrix validation \u2014 ${s.valid_edges} valid / ${s.violated_edges} violated / ${s.unrated_edges} unrated \u00b7 fired${JSON.stringify(s.constraints_fired)}`);

  log(`Stage 6: explanations generated \u2014 basic + ${payload.explainers.contrastive ? 'contrastive' : '(none)'}`);

  session = buildSession(payload);
  lastAnalyzedText = text;
  setChatTitle(text);

  // If the learner jumped back into edit mode while the request was in
  // flight, don't yank the textarea back to locked or overwrite their
  // typing — the highlights re-render from historySpans on the next blur.
  const input = document.querySelector('#inputText');
  const editingMidFlight = input != null && input.readOnly === false;
  if (!editingMidFlight && input) {
    input.value = text;
    syncInputClearBtn();
  }
  const spans = buildHighlightSpans(text, payload);
  if (opts.isSentenceNav || opts.mergeSpans) {
    historySpans = mergeHighlightSpans(historySpans, spans);
  } else {
    historySpans = spans;
  }
  if (!editingMidFlight) {
    returnToLocked(payload);
    applySentenceSelection(payload);
  }

  document.querySelector('#emptyTreeState')?.classList.add('hidden');
  renderer.setTree(payload.tree);
  if (!quizMode) renderCorrection(payload.summary);
  transition(STATES.VIEWING, 'output ready -> viewing');
  log('Stage 7: syntax tree rendered \u2014 Interaction Loop active (node details cached in session)');

  // The correction target (if any) is re-checked against the new analysis:
  // the learner may have fixed the error with their own edit. A re-parse
  // invalidates the preview too — the canvas shows the learner's own
  // sentence again.
  if (focus) {
    correctionMode = 'original';
    focus.corrected = null;
    focus.alternativeCorrected = null;
    recheckFocus(payload);
  }

  const isNavigation = Boolean(opts.isSentenceNav || opts.isReplay || opts.isLive);
  // History is account-only: guests are never recorded.
  if (!isNavigation && !isGuest && supabase && clerk?.user?.id && !recordedTexts.has(text)) {
    try {
      const { error: insertError } = await supabase.from('analysis_history').insert({
        user_id: clerk.user.id,
        sentence: text,
        is_valid: payload.summary.verdict === 'grammatical',
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
  const sentenceClean = payload.summary?.verdict === 'grammatical';
  return tokenRanges.map((token) => {
    let status = sentenceClean ? 'valid' : 'neutral';
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
  const ta = document.querySelector('#inputText');
  if (!layer) return;
  layer.textContent = '';
  if (!text) return;
  const spans = payload ? mergeHighlightSpans(historySpans, buildHighlightSpans(text, payload)) : historySpans;
  const target = payload?.parse?.sentences?.[(payload.meta.target_sentence || 1) - 1];
  let sentenceStart = target?.start ?? -1;
  let sentenceEnd = target?.end ?? -1;
  const off = (n) => Math.max(0, Math.min(n, text.length));
  const boundaries = new Set([0, text.length]);
  spans.forEach((span) => {
    boundaries.add(off(span.start));
    boundaries.add(off(span.end));
  });
  if (sentenceStart >= 0) {
    boundaries.add(sentenceStart);
    boundaries.add(sentenceEnd);
  }
  const sents = session?.sentences || [];
  const activeIdx = session?.sentence_index ?? ((payload?.meta?.target_sentence || 1) - 1);

  // One styled <mark> for the [start, end) slice, or null when it carries
  // no highlighting.
  const segment = (start, end) => {
    const wordSpan = spans.find((span) => span.start <= start && end <= span.end);
    const selected = sentenceStart >= 0 && start >= sentenceStart && end <= sentenceEnd;
    const classes = [];
    if (selected) classes.push('sentence-selected');
    if (wordSpan && HIGHLIGHT_STATUSES.has(wordSpan.status) && HIGHLIGHT_CLASSES[wordSpan.status]) {
      classes.push(HIGHLIGHT_CLASSES[wordSpan.status]);
    }
    if (!classes.length) return null;
    const mark = document.createElement('span');
    mark.className = classes.join(' ');
    mark.textContent = text.slice(start, end);
    return mark;
  };

  const multi = ta?.readOnly === true && sents.length > 1;
  if (multi) {
    // Locked multi-sentence passage: every sentence becomes an interactive
    // span (see the click delegation in wireEvents) — clicking a non-active
    // one inspects that sentence, clicking the active one edits.
    const active = sents[activeIdx];
    if (active) { sentenceStart = active.start; sentenceEnd = active.end; }
    const points = [...boundaries].sort((a, b) => a - b);
    let cursor = 0;
    const appendRange = (from, to, parent) => {
      let pos = from;
      for (const p of [...points.filter((b) => b > from && b < to), to]) {
        if (p <= pos) continue;
        parent.appendChild(segment(pos, p) || document.createTextNode(text.slice(pos, p)));
        pos = p;
      }
    };
    sents.forEach((s, i) => {
      const start = off(s.start);
      const end = Math.max(start, off(s.end));
      if (start > cursor) layer.appendChild(document.createTextNode(text.slice(cursor, start)));
      const span = document.createElement('span');
      span.className = 'sentence-span' + (i === activeIdx ? ' is-active' : '');
      span.dataset.sentIdx = String(i);
      appendRange(start, end, span);
      layer.appendChild(span);
      cursor = Math.max(cursor, end);
    });
    if (cursor < text.length) layer.appendChild(document.createTextNode(text.slice(cursor)));
    syncHighlightScroll();
    return;
  }

  const points = [...boundaries].sort((a, b) => a - b);
  for (let index = 0; index < points.length - 1; index += 1) {
    const start = points[index];
    const end = points[index + 1];
    if (start === end) continue;
    const mark = segment(start, end);
    layer.appendChild(mark || document.createTextNode(text.slice(start, end)));
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

function applyStatuses(tree, details, summary) {
  const fallback = summary?.verdict === 'grammatical' ? 'valid' : 'neutral';
  const walk = (node) => {
    const d = details[node.id];
    const raw = d?.display_status || d?.status || fallback;
    node.edgeResult = { status: raw === 'error' ? 'error' : raw === 'valid' ? 'valid' : 'neutral' };
    for (const c of node.children || []) walk(c);
  };
  walk(tree);
  const ungrammatical = summary?.valid === false || summary?.verdict === 'ungrammatical';
  if (ungrammatical
      && !Object.values(details).some((detail) => detail?.status === 'error')) {
    tree.edgeResult = { status: 'error' };
  }
  return tree;
}

function handleNodeSelect(id) {
  if (quizMode) return;
  if (workspaceView !== 'tutor') return;
  if (!id || !session) {
    if (session) {
      // Empty canvas: the node selection goes, the open correction stays —
      // the learner may still be typing the fix for it.
      renderer.select(null);
      renderNodeDetail(null, null, null);
      transition(STATES.VIEWING, 'selection cleared');
    }
    return;
  }
  // While a correction preview is on the canvas the tree belongs to the
  // re-parsed sentence, so the node is looked up in that payload.
  const preview = activePreview();
  const payload = preview ? preview.payload : session.payload;
  const detail = payload.node_details[id];
  const node = payload.nodes[id];
  if (!node || !detail) return;
  renderNodeDetail(session, detail, node);
  // Keep the fresh detail card visible in the bottom-right explain pane
  // without yanking the rest of the workspace.
  document.querySelector('#explainNode')
    ?.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  renderer.select(id);
  // An error node is the entry point of the corrective feedback: it zooms the
  // canvas to the rule's scope and opens the correction panel. A preview tree
  // never starts a new correction — the original error stays the target.
  if (!preview && detail.status === 'error') enterFocus(id, detail);
  if (state !== STATES.PROCESSING) {
    transition(STATES.EXPLORING, 'user selects syntax node (cache hit \u2014 no HTTP request)');
    log(`Exploring: cached XAI for node ${node.type} \u2014 ${detail.constraint} (${detail.status})`);
  }
}

async function loadAndRenderHistory() {
  const container = document.querySelector('#historyList');
  if (!container) return;
  container.innerHTML = '<p class="history-empty">Loading past analyses...</p>';

  if (!isGuest && supabase) {
    const { data, error } = await supabase
      .from('analysis_history')
      .select('id, sentence, is_valid, constraints_fired, created_at')
      .order('created_at', { ascending: false })
      .limit(50);

    if (error) {
      container.textContent = '';
      const err = document.createElement('p');
      err.className = 'history-empty';
      err.style.color = 'var(--err)';
      err.textContent = `Error loading history: ${error.message}`;
      container.appendChild(err);
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
    container.textContent = '';
    const note = document.createElement('p');
    note.className = 'history-empty';
    note.textContent = cachedHistory.length
      ? 'No matching analyses found.'
      : 'No history yet — analyses you run will appear here.';
    container.appendChild(note);
    return;
  }

  container.innerHTML = '';
  filtered.forEach((entry) => {
    const isError = !entry.is_valid;

    const card = document.createElement('div');
    card.className = `history-item ${isError ? 'is-invalid' : 'is-valid'}`;
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');
    card.title = entry.sentence;
    card.setAttribute('aria-label', `${entry.sentence} — ${entry.is_valid ? 'Valid' : 'Invalid'}`);

    const titleP = document.createElement('p');
    // `hist-sentence` carries the single-line ellipsis truncation: a long
    // sentence never widens the card or the drawer.
    titleP.className = 'hist-title hist-sentence';
    titleP.textContent = entry.sentence;

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

    card.appendChild(titleP);
    card.appendChild(delBtn);

    const openEntry = () => {
      closeHistoryDrawer();
      replayHistoryEntry(entry.sentence);
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
      if (isGuest || !supabase || !clerk?.user?.id) return;
      delBtn.disabled = true;

      const { error } = await supabase
        .from('analysis_history')
        .delete()
        .eq('id', entry.id);

      if (error) {
        alert('Failed to delete item: ' + error.message);
        delBtn.disabled = false;
        return;
      }

      cachedHistory = cachedHistory.filter((item) => item.id !== entry.id);
      renderHistoryItems();
    });

    container.appendChild(card);
  });
}

// ---------------------------------------------------------------------------
// First-visit onboarding — a step-by-step spotlight tour of the workspace
// ---------------------------------------------------------------------------
// Runs once per browser. It preloads a friendly example sentence so the tree,
// the analysis, and every zone the tour points at are populated, then walks
// four steps: input panel, canvas/tree, bottom-right analysis, and the sidebar
// (Lessons / Syntax Builder). Skip / Next / Back / Got it are all supported.
const ONBOARDING_KEY = 'syntutor_onboarding_seen';
const ONBOARDING_SENTENCE = 'The clever boy reads a book.';
const ONBOARDING_STEPS = [
  {
    sel: '.pane-input',
    title: 'Write a sentence',
    text: 'Click the panel, type any English sentence, then click away. SynTutor parses it and highlights anything ungrammatical.',
  },
  {
    sel: '.canvas-stage',
    title: 'Explore the syntax tree',
    text: 'Each word and phrase becomes a node. Click a node to see its role — the tree is the explanation.',
  },
  {
    sel: '.pane-explain',
    title: 'Read the analysis',
    text: 'This pane explains the node you selected, and flags grammar issues with hints on how to fix them.',
  },
  {
    sel: '#appSidebar',
    title: 'Learn and build',
    text: 'Open Lessons for guided practice, or Syntax Builder to construct phrase-structure trees by hand.',
  },
];

let onboardingStep = 0;
let onboardingEls = null;

function maybeStartOnboarding() {
  let seen = false;
  try { seen = localStorage.getItem(ONBOARDING_KEY) === '1'; } catch { seen = false; }
  if (seen) return;
  // First visit: seed the example sentence so the canvas and analysis are
  // populated for the tour. isReplay keeps it out of the analysis history.
  const ta = document.querySelector('#inputText');
  if (ta) ta.value = ONBOARDING_SENTENCE;
  syncInputClearBtn();
  Promise.resolve()
    .then(() => runPipeline({ isReplay: true }))
    .catch(() => {})
    .finally(() => window.setTimeout(showOnboarding, 400));
}

function ensureOnboarding() {
  if (onboardingEls) return onboardingEls;
  const root = document.createElement('div');
  root.className = 'onboarding';
  root.id = 'onboarding';
  root.hidden = true;
  const ring = document.createElement('div');
  ring.className = 'onboarding-ring';
  ring.setAttribute('aria-hidden', 'true');
  const card = document.createElement('div');
  card.className = 'onboarding-card';
  card.setAttribute('role', 'dialog');
  card.setAttribute('aria-label', 'Welcome to SynTutor');
  card.innerHTML =
    '<span class="onboarding-kicker"></span>'
    + '<h3 class="onboarding-title"></h3>'
    + '<p class="onboarding-text"></p>'
    + '<div class="onboarding-dots"></div>'
    + '<div class="onboarding-nav">'
    + '<button type="button" class="onboarding-skip">Skip</button>'
    + '<button type="button" class="sq-ghost onboarding-back">Back</button>'
    + '<button type="button" class="sq-primary onboarding-next">Next \u2192</button>'
    + '</div>';
  root.appendChild(ring);
  root.appendChild(card);
  document.body.appendChild(root);
  card.querySelector('.onboarding-skip').addEventListener('click', finishOnboarding);
  card.querySelector('.onboarding-back').addEventListener('click', () => onboardingGo(-1));
  card.querySelector('.onboarding-next').addEventListener('click', () => onboardingGo(1));
  onboardingEls = { root, ring, card };
  return onboardingEls;
}

function renderOnboarding() {
  const { card } = ensureOnboarding();
  const step = ONBOARDING_STEPS[onboardingStep];
  card.querySelector('.onboarding-kicker').textContent =
    `Step ${onboardingStep + 1} of ${ONBOARDING_STEPS.length}`;
  card.querySelector('.onboarding-title').textContent = step.title;
  card.querySelector('.onboarding-text').textContent = step.text;
  const dots = card.querySelector('.onboarding-dots');
  dots.textContent = '';
  ONBOARDING_STEPS.forEach((_, i) => {
    const dot = document.createElement('span');
    dot.className = i === onboardingStep ? 'onboarding-dot is-active' : 'onboarding-dot';
    dots.appendChild(dot);
  });
  card.querySelector('.onboarding-back').disabled = onboardingStep === 0;
  card.querySelector('.onboarding-next').textContent =
    onboardingStep === ONBOARDING_STEPS.length - 1 ? 'Got it \u2713' : 'Next \u2192';
  window.requestAnimationFrame(positionOnboarding);
}

function positionOnboarding() {
  if (!onboardingEls) return;
  const { ring, card } = onboardingEls;
  const vw = window.innerWidth;
  const vh = window.innerHeight;
  const pad = 8;
  const target = document.querySelector(ONBOARDING_STEPS[onboardingStep].sel);
  let rect = target ? target.getBoundingClientRect() : null;
  // Ignore targets that are hidden or off-screen (e.g. the mobile drawer).
  if (rect && (!rect.width || !rect.height || rect.right < 4 || rect.left > vw - 4)) rect = null;
  if (rect) {
    ring.style.display = '';
    ring.style.left = `${Math.round(rect.left - pad)}px`;
    ring.style.top = `${Math.round(rect.top - pad)}px`;
    ring.style.width = `${Math.round(rect.width + pad * 2)}px`;
    ring.style.height = `${Math.round(rect.height + pad * 2)}px`;
  } else {
    ring.style.display = 'none';
  }
  const cw = card.offsetWidth;
  const ch = card.offsetHeight;
  let left;
  let top;
  if (rect) {
    left = rect.right + 16;
    if (left + cw > vw - 12) left = rect.left - cw - 16;
    if (left < 12) left = Math.max(12, Math.min(rect.left, vw - cw - 12));
    top = Math.max(12, Math.min(rect.top, vh - ch - 12));
  } else {
    left = Math.round((vw - cw) / 2);
    top = Math.round((vh - ch) / 2);
  }
  card.style.left = `${left}px`;
  card.style.top = `${top}px`;
}

function onboardingGo(d) {
  const next = onboardingStep + d;
  if (next < 0) return;
  if (next >= ONBOARDING_STEPS.length) {
    finishOnboarding();
    return;
  }
  onboardingStep = next;
  renderOnboarding();
}

function showOnboarding() {
  const { root } = ensureOnboarding();
  onboardingStep = 0;
  root.hidden = false;
  renderOnboarding();
  document.addEventListener('keydown', onOnboardingKeydown);
  window.addEventListener('resize', positionOnboarding);
  window.addEventListener('scroll', positionOnboarding, true);
}

function finishOnboarding() {
  try { localStorage.setItem(ONBOARDING_KEY, '1'); } catch { /* storage unavailable */ }
  if (onboardingEls) onboardingEls.root.hidden = true;
  document.removeEventListener('keydown', onOnboardingKeydown);
  window.removeEventListener('resize', positionOnboarding);
  window.removeEventListener('scroll', positionOnboarding, true);
}

function onOnboardingKeydown(e) {
  if (e.key === 'Escape') finishOnboarding();
  else if (e.key === 'ArrowRight') onboardingGo(1);
  else if (e.key === 'ArrowLeft') onboardingGo(-1);
}

if (typeof window !== 'undefined') {
  if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', () => boot());
  } else {
    boot();
  }
}