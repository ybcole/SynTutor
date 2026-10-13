// Matrix Quiz UI controller.
//
// The sidebar panel (#quizPanel) still hosts the searchable rule catalog and
// the difficulty setup. Once a run starts, the quiz moves onto the main canvas:
// the learner repairs the incorrect sentence in the top textarea and the syntax
// tree is rendered below, while a collapsible quest panel on the right shows the
// category, progress, score, and Skip / Submit controls. Wrong answers surface
// the same rule-matrix remediation used by the tutor.

import {
  MATRIX_SECTIONS, DIFFICULTY, questionPool, ruleInfo, ruleDifficulty, hasQuiz,
} from './quiz-data.js';
import {
  isParagraphQuizAnswerCorrect, isQuizAnswerCorrect, hasSyntaxError,
} from './quiz/answer.js';
import { XP_PER_CORRECT, PERFECT_QUIZ_BONUS, levelFromXp } from './quiz/level.js';
import { achievementCatalog, computeUnlocked } from './quiz/achievements.js';
import { renderNodeDetail } from './ui.js';

const $ = (sel, root = document) => root.querySelector(sel);

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
}

const state = {
  view: 'list', // list | setup | quiz | results | leaderboard | achievements
  ruleId: null,
  difficulty: 'easy',
  difficultyFilter: null, // null = all rules
  questions: [],
  index: 0,
  entries: [],
  search: '',
  body: null,
  active: false,
  answered: false,
  collapsed: false,
  controller: null,
  awarded: false,
  xpEarned: 0,
  xpPerfect: false,
  xpResult: null,
  unlockedNow: [],
  progress: null,
  progressAvailable: false,
};

// ---------------------------------------------------------------------------
// Open / close
// ---------------------------------------------------------------------------
export function openQuizView(view = 'list') {
  const panel = $('#quizPanel');
  if (!panel) return;
  if (state.active) endQuiz();
  panel.hidden = false;
  $('#appSidebar')?.classList.add('quiz-active');
  $('#appSidebarBackdrop')?.classList.add('active');
  $('#sidebarToggleBtn')?.setAttribute('aria-expanded', 'true');
  const activeView = { quiz: 'quiz', leaderboard: 'leaderboard', achievements: 'achievements' }[view] || 'quiz';
  document.querySelectorAll('.sidebar-item').forEach((b) => {
    b.classList.toggle('active', b.dataset.view === activeView);
  });
  if (view === 'leaderboard') goLeaderboard();
  else if (view === 'achievements') goAchievements();
  else goList();
}

export function closeQuizView() {
  if (state.active) endQuiz();
  const panel = $('#quizPanel');
  if (panel) { panel.hidden = true; panel.innerHTML = ''; }
  $('#appSidebar')?.classList.remove('quiz-active');
  document.querySelectorAll('.sidebar-item').forEach((b) => {
    b.classList.toggle('active', b.dataset.view === 'tutor');
  });
}

export function isQuizOpen() {
  return Boolean($('#quizPanel') && !$('#quizPanel').hidden);
}

function hideSidebar() {
  const panel = $('#quizPanel');
  if (panel) panel.hidden = true;
  $('#appSidebar')?.classList.remove('quiz-active');
  $('#appSidebarBackdrop')?.classList.remove('active');
  $('#sidebarToggleBtn')?.setAttribute('aria-expanded', 'false');
}

// ---------------------------------------------------------------------------
// Sidebar shell
// ---------------------------------------------------------------------------
function shell({ title, back, search, meta }) {
  const panel = $('#quizPanel');
  panel.innerHTML = '';

  const head = el('div', 'sq-head');
  if (back) {
    const backBtn = el('button', 'sq-back');
    backBtn.type = 'button';
    backBtn.setAttribute('aria-label', 'Back');
    backBtn.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>';
    backBtn.addEventListener('click', back);
    head.appendChild(backBtn);
  }
  head.appendChild(el('h2', 'sq-title', title));
  panel.appendChild(head);

  if (search) {
    const box = el('div', 'sq-searchbox');
    const input = el('input', 'sq-search');
    input.type = 'search';
    input.placeholder = 'Search rules, ids, examples\u2026';
    input.value = state.search;
    input.addEventListener('input', (e) => {
      state.search = e.target.value;
      if (state.view === 'list') renderList();
    });
    box.appendChild(input);
    panel.appendChild(box);
  }

  if (meta) panel.appendChild(meta);

  const body = el('div', 'sq-body');
  panel.appendChild(body);
  state.body = body;
  return body;
}

// ---------------------------------------------------------------------------
// List
// ---------------------------------------------------------------------------
function goList() {
  state.view = 'list';
  const filter = el('div', 'sq-filter');
  const options = [['', 'All'], ...Object.entries(DIFFICULTY).map(([key, d]) => [key, d.label])];
  for (const [key, label] of options) {
    const chip = el('button', `sq-filter-chip${state.difficultyFilter === key ? ' selected' : ''}`, label);
    chip.type = 'button';
    chip.addEventListener('click', () => {
      state.difficultyFilter = key || null;
      goList();
    });
    filter.appendChild(chip);
  }
  shell({ title: 'Matrix Quiz', search: true, meta: filter });
  renderList();
  refreshProgress();
}

function refreshProgress() {
  const progress = state.controller?.progress;
  state.progressAvailable = Boolean(progress?.isAvailable?.());
  if (!state.progressAvailable) {
    state.progress = null;
    if (state.view === 'list') renderList();
    return;
  }
  progress.load?.().then((data) => {
    state.progress = data
      ? { xp: data.xp, level: data.level, ...levelFromXp(data.xp) }
      : null;
    if (state.view === 'list') renderList();
  }).catch(() => {
    state.progress = null;
    if (state.view === 'list') renderList();
  });
}

function progressStrip() {
  const wrap = el('div', 'sq-progress-card');

  const head = el('div', 'sq-progress-head');
  head.appendChild(el('span', 'sq-level',
    state.progress ? `Level ${state.progress.level}` : 'Progress'));
  const links = el('div', 'sq-progress-links');
  const board = el('button', 'sq-link', 'Leaderboard');
  board.type = 'button';
  board.addEventListener('click', goLeaderboard);
  const ach = el('button', 'sq-link', 'Achievements');
  ach.type = 'button';
  ach.addEventListener('click', goAchievements);
  links.appendChild(board);
  links.appendChild(ach);
  head.appendChild(links);
  wrap.appendChild(head);

  if (!state.progressAvailable) {
    wrap.appendChild(el('p', 'sq-progress-note',
      'Sign in to earn XP and join the leaderboard.'));
    return wrap;
  }
  if (!state.progress) {
    wrap.appendChild(el('p', 'sq-progress-note', 'Loading progress\u2026'));
    return wrap;
  }

  const { into, span, level } = state.progress;
  const bar = el('div', 'sq-xp-bar');
  const fill = el('div', 'sq-xp-fill');
  fill.style.width = `${span ? Math.min(100, Math.round((into / span) * 100)) : 0}%`;
  bar.appendChild(fill);
  wrap.appendChild(bar);
  wrap.appendChild(el('p', 'sq-progress-note',
    `${state.progress.xp} XP \u00b7 ${into} / ${span} to Level ${level + 1}`));
  return wrap;
}

function goLeaderboard() {
  state.view = 'leaderboard';
  shell({ title: 'Leaderboard', back: goList });
  renderLeaderboard();
}

async function renderLeaderboard() {
  const body = state.body;
  if (!body) return;
  body.innerHTML = '';
  const progress = state.controller?.progress;
  if (!progress) {
    body.appendChild(el('p', 'sq-empty', 'The leaderboard is unavailable.'));
    return;
  }
  body.appendChild(el('p', 'sq-empty', 'Loading leaderboard\u2026'));
  let rows;
  try {
    rows = await progress.leaderboard?.();
  } catch {
    rows = null;
  }
  body.innerHTML = '';
  if (!rows || !rows.length) {
    body.appendChild(el('p', 'sq-empty',
      'No rankings yet \u2014 finish a quiz signed in to earn your first XP!'));
    return;
  }
  const myId = progress.myId ? progress.myId() : null;
  const list = el('ol', 'sq-board');
  rows.forEach((player, index) => {
    const item = el('li', `sq-board-row${player.user_id === myId ? ' me' : ''}`);
    const rank = el('span', 'sq-board-rank', `${index + 1}`);
    const meta = el('span', 'sq-board-meta');
    meta.appendChild(el('span', 'sq-board-name', player.display_name || 'Learner'));
    meta.appendChild(el('span', 'sq-board-xp', `${player.xp} XP`));
    item.appendChild(rank);
    item.appendChild(meta);
    const levelBadge = el('span', 'sq-board-level', `Lv ${player.level}`);
    item.appendChild(levelBadge);
    if (player.user_id === myId) item.setAttribute('aria-label', 'Your ranking');
    list.appendChild(item);
  });
  body.appendChild(list);
  body.appendChild(el('p', 'sq-board-note',
    'Rankings are permanent and ordered by level (XP breaks ties).'));
}

function goAchievements() {
  state.view = 'achievements';
  shell({ title: 'Achievements', back: goList });
  renderAchievements();
}

async function renderAchievements() {
  const body = state.body;
  if (!body) return;
  body.innerHTML = '';
  const progress = state.controller?.progress;
  let rows = [];
  if (progress?.getQuizProgress) {
    try {
      rows = await progress.getQuizProgress();
    } catch {
      rows = [];
    }
  }
  const catalog = achievementCatalog();
  const unlocked = computeUnlocked(rows);
  const unlockedCount = catalog.filter((ach) => unlocked.has(ach.id)).length;

  const summary = el('div', 'sq-achievement-summary');
  summary.appendChild(el('span', 'sq-achievement-count',
    `${unlockedCount} / ${catalog.length} unlocked`));
  if (!progress?.isAvailable?.()) {
    summary.appendChild(el('p', 'sq-progress-note',
      'Sign in to earn achievements \u2014 your progress counts once you are signed in.'));
  }
  body.appendChild(summary);

  const grid = el('div', 'sq-ach-grid');
  for (const ach of catalog) {
    const tile = el('div', `sq-ach${unlocked.has(ach.id) ? ' unlocked' : ''}`);
    tile.appendChild(el('span', 'sq-ach-icon', ach.icon));
    const t = el('span', 'sq-ach-title', ach.title);
    const d = el('span', 'sq-ach-desc', ach.description);
    const s = el('span', 'sq-ach-state', unlocked.has(ach.id) ? 'Unlocked' : 'Locked');
    tile.appendChild(t);
    tile.appendChild(d);
    tile.appendChild(s);
    grid.appendChild(tile);
  }
  body.appendChild(grid);
  if (!progress?.isAvailable?.()) {
    body.appendChild(el('p', 'sq-board-note',
      'Achievements: complete a quiz in every section to become a Grammar Grandmaster.'));
  } else {
    const done = MATRIX_SECTIONS.filter((section) => unlocked.has(`section_${section.id}`)).length;
    body.appendChild(el('p', 'sq-board-note', `${done} / ${MATRIX_SECTIONS.length} sections explored.`));
  }
}

function renderList() {
  const body = state.body;
  if (!body) return;
  body.innerHTML = '';
  body.appendChild(progressStrip());
  const query = state.search.trim().toLowerCase();
  const diffFilter = state.difficultyFilter;
  const hint = diffFilter
    ? `Showing ${DIFFICULTY[diffFilter].label} rules \u2014 click a rule to start that quiz.`
    : 'Click a rule to choose a difficulty, or pick one from the filter to start instantly.';

  let total = 0;
  MATRIX_SECTIONS.forEach((section) => {
    const matches = section.rules.filter((r) => {
      if (query) {
        const haystack = `${r.id} ${r.rule} ${r.example || ''}`.toLowerCase();
        if (!haystack.includes(query)) return false;
      }
      if (diffFilter && ruleDifficulty(r) !== diffFilter) return false;
      return true;
    });
    if (!matches.length) return;
    total += matches.length;

    const group = el('div', 'sq-group');
    const h = el('div', 'sq-group-head');
    h.appendChild(el('span', 'sq-group-id', `${section.id}`));
    h.appendChild(el('span', 'sq-group-title', section.title));
    h.appendChild(el('span', 'sq-group-count', `${matches.length}`));
    group.appendChild(h);

    matches.forEach((rule) => group.appendChild(ruleRow(rule)));
    body.appendChild(group);
  });

  body.appendChild(el('p', 'sq-filter-hint', hint));
  if (!total) body.appendChild(el('p', 'sq-empty', 'No rules match your search or filter.'));
}

function ruleRow(rule) {
  const row = el('button', 'sq-row');
  row.type = 'button';
  row.dataset.rule = rule.id;

  const top = el('div', 'sq-row-top');
  top.appendChild(el('span', 'sq-row-id', rule.id));
  top.appendChild(el('span', 'sq-row-rule', rule.rule));
  const meta = el('span', 'sq-row-meta');
  const diff = ruleDifficulty(rule);
  meta.appendChild(el('span', `sq-diff-badge ${diff}`, DIFFICULTY[diff].label));
  const ready = hasQuiz(rule.id);
  meta.appendChild(el('span', `sq-dot ${ready ? 'ready' : 'soon'}`, ''));
  top.appendChild(meta);
  row.appendChild(top);

  const foot = el('div', 'sq-row-foot');
  foot.appendChild(el('span', 'sq-bad', rule.example || ''));
  if (!ready) foot.appendChild(el('span', 'sq-soon', 'soon'));
  row.appendChild(foot);

  row.addEventListener('click', () => {
    if (state.difficultyFilter) {
      state.ruleId = rule.id;
      state.difficulty = state.difficultyFilter;
      startQuiz();
    } else {
      goSetup(rule.id);
    }
  });
  return row;
}

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------
function goSetup(ruleId) {
  state.ruleId = ruleId;
  state.view = 'setup';
  const info = ruleInfo(ruleId);
  const body = shell({ title: ruleId, back: goList });
  state.body = body;

  if (!hasQuiz(ruleId)) {
    const soon = el('div', 'sq-soon-box');
    soon.appendChild(el('p', 'sq-soon-text',
      `Quizzes for \u201c${info ? info.rule : ruleId}\u201d are coming soon.`));
    body.appendChild(soon);
    return;
  }

  const intro = el('div', 'sq-intro');
  intro.appendChild(el('span', 'sq-intro-id', ruleId));
  intro.appendChild(el('span', 'sq-intro-rule', info ? info.rule : ''));
  if (info) intro.appendChild(el('span', 'sq-bad', info.example || ''));
  body.appendChild(intro);

  body.appendChild(el('div', 'sq-label', 'Difficulty'));
  const grid = el('div', 'sq-diff-grid');
  Object.entries(DIFFICULTY).forEach(([key, d]) => {
    const btn = el('button', `sq-diff ${state.difficulty === key ? 'selected' : ''}`);
    btn.type = 'button';
    btn.appendChild(el('span', 'sq-diff-label', d.label));
    btn.addEventListener('click', () => {
      state.difficulty = key;
      grid.querySelectorAll('.sq-diff').forEach((b) => b.classList.remove('selected'));
      btn.classList.add('selected');
    });
    grid.appendChild(btn);
  });
  body.appendChild(grid);

  const start = el('button', 'sq-primary', 'Start Quiz');
  start.type = 'button';
  start.addEventListener('click', startQuiz);
  body.appendChild(start);
}

// ---------------------------------------------------------------------------
// Quest panel (right-hand side, on the canvas)
// ---------------------------------------------------------------------------
function questHost() {
  let host = $('#quizQuestHost');
  if (!host) {
    const right = document.querySelector('.right-panel');
    if (!right) return null;
    host = document.createElement('div');
    host.id = 'quizQuestHost';
    right.insertBefore(host, right.firstChild);
  }
  return host;
}

function clearQuestPanel() {
  const host = questHost();
  if (host) host.innerHTML = '';
}

function setQuizLoading(show) {
  $('#loadingIndicator')?.classList.toggle('visible', show);
}

function renderQuest() {
  const host = questHost();
  if (!host) return;
  host.innerHTML = '';

  const card = el('section', 'card quiz-quest');
  const head = el('div', 'qq-head');
  head.setAttribute('role', 'button');
  head.setAttribute('tabindex', '0');
  const headMain = el('div', 'qq-head-main');
  const info = ruleInfo(state.ruleId);
  headMain.appendChild(el('span', 'qq-cat',
    `${state.ruleId}${info ? ` \u00b7 ${info.rule}` : ''}`));
  if (state.view === 'quiz') headMain.appendChild(el('span', 'qq-diff', DIFFICULTY[state.difficulty].label));
  head.appendChild(headMain);
  const caret = el('button', 'qq-collapse');
  caret.type = 'button';
  caret.setAttribute('aria-label', state.collapsed ? 'Expand' : 'Collapse');
  caret.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="${state.collapsed ? '9 18 15 12 9 6' : '6 9 12 15 18 9'}"></polyline></svg>`;
  head.appendChild(caret);
  const toggle = () => {
    state.collapsed = !state.collapsed;
    renderQuest();
  };
  caret.addEventListener('click', (e) => { e.stopPropagation(); toggle(); });
  head.addEventListener('click', toggle);
  head.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
  });
  card.appendChild(head);

  if (!state.collapsed) {
    const body = el('div', 'qq-body');
    if (state.view === 'results') renderResultsInto(body);
    else renderQuestionInto(body);
    card.appendChild(body);
  }

  host.appendChild(card);
}

function renderQuestionInto(body) {
  const q = state.questions[state.index];
  if (!q) { showResults(); return; }
  const paragraphQuestion = isRegularPluralParagraph(q);
  const done = state.entries.filter(Boolean).length;
  const total = state.questions.length;

  const progress = el('div', 'qq-progress');
  const fill = el('div', 'qq-progress-fill');
  fill.style.width = `${Math.round((done / total) * 100)}%`;
  progress.appendChild(fill);
  body.appendChild(progress);

  const meta = el('div', 'qq-meta-row');
  meta.appendChild(el('span', 'qq-num', `Question ${state.index + 1} of ${total}`));
  const score = state.entries.filter((e) => e && e.correct).length;
  meta.appendChild(el('span', 'qq-score', `Score ${score}`));
  if (state.progressAvailable) {
    meta.appendChild(el('span', 'qq-xp', `+${score * XP_PER_CORRECT} XP`));
  }
  body.appendChild(meta);

  const target = el('div', 'qq-target');
  target.appendChild(el('span', 'qq-label', paragraphQuestion
    ? 'Correct plural errors in this paragraph. Some sentences are already correct.'
    : 'Correct this sentence'));
  target.appendChild(el('p', 'qq-sentence', q.bad));
  body.appendChild(target);

  const answer = el('div', 'qq-answer');
  answer.appendChild(el('span', 'qq-label', paragraphQuestion
    ? 'Corrected paragraph'
    : 'Correct answer'));
  answer.appendChild(el('p', 'qq-good', q.good));
  answer.hidden = !state.answered;
  body.appendChild(answer);

  const nav = el('div', 'qq-nav');
  if (state.answered) {
    const next = el('button', 'sq-primary qq-next',
      state.index + 1 >= total ? 'Finish' : paragraphQuestion ? 'Next paragraph' : 'Next sentence');
    next.type = 'button';
    next.addEventListener('click', advance);
    nav.appendChild(next);
  } else {
    const skip = el('button', 'sq-ghost qq-skip', 'Skip');
    skip.type = 'button';
    skip.addEventListener('click', skipQuestion);
    nav.appendChild(skip);
    const submit = el('button', 'sq-primary qq-submit', 'Submit');
    submit.type = 'button';
    submit.addEventListener('click', submitAnswer);
    nav.appendChild(submit);
  }
  body.appendChild(nav);

  const quit = el('button', 'qq-quit', 'Quit quiz');
  quit.type = 'button';
  quit.addEventListener('click', quitConfirm);
  body.appendChild(quit);
}

function isRegularPluralParagraph(question) {
  return state.ruleId === '1.1'
    && state.difficulty === 'hard'
    && Array.isArray(question.sentences);
}

function renderResultsInto(body) {
  const info = ruleInfo(state.ruleId);
  const correct = state.entries.filter((e) => e && e.correct).length;
  const total = state.questions.length;
  const skipped = state.entries.filter((e) => e && e.skipped).length;
  const pct = total ? Math.round((correct / total) * 100) : 0;

  const score = el('div', 'sq-score');
  score.appendChild(el('span', 'sq-score-num', `${correct} / ${total}`));
  score.appendChild(el('span', 'sq-score-sub',
    `${info ? info.rule : ''} \u00b7 ${DIFFICULTY[state.difficulty].label}${skipped ? ` \u00b7 ${skipped} skipped` : ''}`));
  body.appendChild(score);

  const bar = el('div', 'sq-progress');
  const fill = el('div', 'sq-progress-fill');
  fill.style.width = `${pct}%`;
  bar.appendChild(fill);
  body.appendChild(bar);

  const xp = el('div',
    `qq-xp-earned${state.xpPerfect ? ' perfect' : ''}${state.xpResult ? ' awarded' : ''}`);
  if (state.progressAvailable) {
    xp.appendChild(el('span', 'qq-xp-amount', `+${state.xpEarned} XP earned`));
    if (state.xpPerfect) xp.appendChild(el('span', 'qq-xp-bonus', `Flawless run +${PERFECT_QUIZ_BONUS} bonus`));
    if (state.xpResult) {
      xp.appendChild(el('span', 'qq-xp-total',
        `${state.xpResult.xp} XP total \u00b7 Level ${state.xpResult.level}`));
      if (state.xpResult.leveledUp) {
        xp.appendChild(el('span', 'qq-xp-up', `\u2b06 Level ${state.xpResult.level}!`));
      }
    }
  } else {
    xp.appendChild(el('span', 'qq-xp-amount',
      `+${state.xpEarned} XP earned \u00b7 sign in to keep it`));
  }
  body.appendChild(xp);

  if (state.unlockedNow.length) {
    const catalog = achievementCatalog();
    const names = state.unlockedNow
      .map((id) => catalog.find((ach) => ach.id === id)?.title || id)
      .join('\n');
    const ach = el('div', 'qq-ach-unlocked');
    ach.appendChild(el('span', 'qq-ach-icon', '\u{1F3C6}'));
    const note = el('span', 'qq-ach-note', `Achievement unlocked: ${names}`);
    ach.appendChild(note);
    body.appendChild(ach);
  }

  const review = el('div', 'sq-review');
  state.entries.forEach((entry, i) => {
    if (!entry) return;
    const q = entry.question;
    const row = el('div', `sq-review-row ${entry.correct ? 'ok' : entry.skipped ? 'skip' : 'err'}`);
    const rowHead = el('div', 'sq-review-head');
    rowHead.appendChild(el('span', 'sq-review-i', `${i + 1}`));
    rowHead.appendChild(el('span', 'sq-review-sent', q.bad));
    rowHead.appendChild(el('span', 'sq-review-mark', entry.correct ? '\u2713' : entry.skipped ? '\u2013' : '\u2717'));
    row.appendChild(rowHead);
    const ans = el('div', 'sq-review-ans');
    ans.appendChild(el('span', 'sq-review-correct', `Correct: ${q.good}`));
    if (entry.skipped) ans.appendChild(el('span', 'sq-review-yours', 'Skipped'));
    else if (!entry.correct && entry.answer) ans.appendChild(el('span', 'sq-review-yours', `You: ${entry.answer}`));
    row.appendChild(ans);
    review.appendChild(row);
  });
  body.appendChild(review);

  const actions = el('div', 'sq-actions');
  const again = el('button', 'sq-primary', 'Try again');
  again.type = 'button';
  again.addEventListener('click', startQuiz);
  const another = el('button', 'sq-ghost', 'Choose another');
  another.type = 'button';
  another.addEventListener('click', exitQuiz);
  actions.appendChild(again);
  actions.appendChild(another);
  body.appendChild(actions);
}

// ---------------------------------------------------------------------------
// Runner
// ---------------------------------------------------------------------------
function startQuiz() {
  if (!state.ruleId || !hasQuiz(state.ruleId)) return;
  const count = DIFFICULTY[state.difficulty].count;
  let pool;
  try {
    pool = questionPool(state.ruleId, state.difficulty);
  } catch (error) {
    console.error(`Failed to build the ${state.ruleId} quiz question pool.`, error);
    state.body?.appendChild(el('p', 'sq-empty',
      'This quiz could not be started because its question bank failed to load.'));
    return;
  }
  if (pool.length < count) {
    console.error(`The ${state.ruleId} quiz has ${pool.length} questions; ${count} are required.`);
    state.body?.appendChild(el('p', 'sq-empty',
      `This quiz needs ${count} questions to start, but only ${pool.length} are available.`));
    return;
  }
  state.questions = pool.slice(0, count);
  state.index = 0;
  state.entries = [];
  state.answered = false;
  state.collapsed = false;
  state.active = true;
  state.view = 'quiz';
  state.awarded = false;
  state.xpEarned = 0;
  state.xpPerfect = false;
  state.xpResult = null;
  state.unlockedNow = [];
  state.progressAvailable = Boolean(state.controller?.progress?.isAvailable?.());
  setQuizMode(true);
  hideSidebar();
  loadQuestion();
}

async function loadQuestion() {
  const q = state.questions[state.index];
  if (!q) { showResults(); return; }
  state.answered = false;

  const ta = $('#inputText');
  const editor = document.querySelector('.input-editor');
  if (ta) {
    ta.value = q.bad;
    ta.readOnly = true;
    ta.classList.remove('editing');
  }
  editor?.classList.remove('editing');
  const overlay = $('#inputHighlights');
  if (overlay) overlay.dataset.hint = quizInputHint();

  renderQuest();
  renderNodeDetail(null, null, null);
  setQuizLoading(true);
  await state.controller?.analyze(q.bad, 0);
  setQuizLoading(false);
}

export function quizInputHint() {
  const q = state.questions[state.index];
  const paragraph = q && isRegularPluralParagraph(q);
  return paragraph
    ? 'Click any sentence to view its tree; double-click to edit the paragraph, then press Submit.'
    : 'Click to view the tree; double-click to edit the sentence, then press Submit.';
}

async function submitAnswer() {
  if (state.answered) return;
  const q = state.questions[state.index];
  const ta = $('#inputText');
  const text = (ta?.value || '').trim();
  if (!text) return;

  state.answered = true;
  setQuizLoading(true);
  const paragraphQuestion = isRegularPluralParagraph(q);
  let payload;
  let correct;
  if (paragraphQuestion) {
    const first = await state.controller?.analyze(text, 0);
    const sentences = (first?.parse?.sentences || []).map((sentence) => sentence.text);
    const payloads = [first];
    for (let index = 1; index < sentences.length; index += 1) {
      payloads.push(await state.controller?.analyze(text, index));
    }
    payload = payloads.find((item) => item && hasSyntaxError(item)) || first;
    correct = isParagraphQuizAnswerCorrect(
      sentences,
      q.sentences.map((sentence) => sentence.good),
      payloads,
    );
  } else {
    payload = await state.controller?.analyze(text);
    correct = isQuizAnswerCorrect(text, q.good, payload);
  }
  setQuizLoading(false);

  state.entries[state.index] = { question: q, answer: text, correct, skipped: false };
  applyFeedback(q, correct, payload);
  renderQuest();
}

function skipQuestion() {
  const q = state.questions[state.index];
  state.answered = true;
  state.entries[state.index] = { question: q, answer: '', correct: false, skipped: true };
  renderSkipped();
  renderQuest();
}

function advance() {
  if (state.index + 1 >= state.questions.length) { showResults(); return; }
  state.index += 1;
  loadQuestion();
}

// ---------------------------------------------------------------------------
// Feedback (reuses the tutor's node/remediation explainer)
// ---------------------------------------------------------------------------
function firstError(payload) {
  if (!payload) return null;
  const details = payload.node_details || {};
  for (const [id, d] of Object.entries(details)) {
    if (d && d.status === 'error') return { id, detail: d, node: payload.nodes?.[id] };
  }
  return null;
}

function showFeedbackBox() {
  const empty = $('#emptyExplainState');
  if (empty) empty.classList.add('hidden');
  return $('#explainNode');
}

function renderSuccess(q, payload) {
  const box = showFeedbackBox();
  if (!box) return;
  box.innerHTML = '';
  const card = el('div', 'node-card');
  const head = el('div', 'nc-head');
  head.appendChild(el('span', 'nc-dot ok', ''));
  head.appendChild(el('span', 'nc-name', 'Correct'));
  card.appendChild(head);
  const verdict = payload?.summary?.verdict;
  card.appendChild(el('p', 'ex-text',
    verdict === 'grammatical'
      ? 'Nice work \u2014 your sentence is well-formed. The tree below shows the corrected structure.'
      : verdict === 'unverified'
        ? 'Your correction matches the expected answer, but the syntax checker could not fully verify the sentence.'
        : 'Your correction matches the expected answer, but the syntax check is unavailable.'));

  const rem = el('div', 'nc-rem');
  if (q && q.good) {
    rem.appendChild(el('div', 'nc-label', 'Corrected sentence'));
    rem.appendChild(el('p', 'ex-text nc-fix', q.good));
  }
  if (q && q.explanation) {
    rem.appendChild(el('div', 'nc-label', 'Why this is correct'));
    rem.appendChild(el('p', 'ex-text', q.explanation));
  }
  const verdictText = payload && payload.summary && payload.summary.explanation;
  if (verdictText) {
    rem.appendChild(el('div', 'nc-label', 'Syntax tree check'));
    rem.appendChild(el('p', 'ex-text', verdictText));
  }
  card.appendChild(rem);
  box.appendChild(card);
}

function renderSkipped() {
  const box = showFeedbackBox();
  if (!box) return;
  box.innerHTML = '';
  const card = el('div', 'node-card');
  const head = el('div', 'nc-head');
  head.appendChild(el('span', 'nc-dot un', ''));
  head.appendChild(el('span', 'nc-name', 'Skipped'));
  card.appendChild(head);
  card.appendChild(el('p', 'ex-text', 'No answer submitted. The correct sentence is shown in the quiz panel.'));
  box.appendChild(card);
}

function renderFallbackWrong(q, payload) {
  const box = showFeedbackBox();
  if (!box) return;
  box.innerHTML = '';
  const card = el('div', 'node-card');
  const head = el('div', 'nc-head');
  head.appendChild(el('span', 'nc-dot err', ''));
  head.appendChild(el('span', 'nc-name', 'Not quite'));
  card.appendChild(head);
  const verdict = payload?.summary?.verdict;
  const message = verdict === 'ungrammatical'
    ? payload.summary.explanation
    : verdict === 'grammatical'
      ? `The syntax checker found no structural violation, but your answer does not match the expected correction: ${q.good}`
      : verdict === 'unverified'
        ? `Your answer does not match the expected correction, and the syntax checker could not verify its structure: ${q.good}`
        : q.explanation || 'Your sentence does not match the expected correction.';
  card.appendChild(el('p', 'ex-text', message));
  box.appendChild(card);
}

function applyFeedback(q, correct, payload) {
  if (correct) { renderSuccess(q, payload); return; }
  const err = firstError(payload);
  if (err && err.detail && err.node) {
    renderNodeDetail(null, err.detail, err.node);
  } else {
    renderFallbackWrong(q, payload);
  }
}

// ---------------------------------------------------------------------------
// Results / teardown
// ---------------------------------------------------------------------------
function showResults() {
  state.view = 'results';
  state.answered = false;
  if (!state.awarded) {
    state.awarded = true;
    awardQuizXp();
  }
  renderQuest();
}

function quizXpEarned() {
  const entries = state.entries.filter(Boolean);
  const total = state.questions.length;
  const correct = entries.filter((entry) => entry.correct).length;
  const perfect = entries.length === total && entries.every((entry) => entry && entry.correct);
  return {
    correct,
    total,
    perfect,
    earned: correct * XP_PER_CORRECT + (perfect ? PERFECT_QUIZ_BONUS : 0),
  };
}

async function awardQuizXp() {
  const outcome = quizXpEarned();
  state.xpEarned = outcome.earned;
  state.xpPerfect = outcome.perfect;
  const progress = state.controller?.progress;
  const beforeLevel = state.progress?.level ?? 0;
  state.unlockedNow = [];
  let result = null;
  try {
    const tracked = await progress?.trackCompletion?.({
      ruleId: state.ruleId,
      difficulty: state.difficulty,
      perfect: outcome.perfect,
    });
    state.unlockedNow = tracked?.newlyUnlocked || [];
    if (progress?.isAvailable?.()) {
      result = await progress.award?.(outcome.earned);
    }
  } catch {
    result = null;
  }
  if (result) {
    state.xpResult = { ...result, leveledUp: result.level > beforeLevel };
    state.progress = { xp: result.xp, level: result.level, ...levelFromXp(result.xp) };
  } else {
    state.xpResult = null;
  }
  renderQuest();
}

function setQuizMode(active) {
  state.controller?.setQuizMode(active);
}

function endQuiz() {
  state.active = false;
  state.answered = false;
  setQuizMode(false);
  clearQuestPanel();
  const overlay = $('#inputHighlights');
  if (overlay) {
    overlay.dataset.hint = 'Double-click the panel to edit. When locked, click any sentence to view its syntax tree.';
  }
}

function exitQuiz() {
  endQuiz();
  openQuizView();
}

function quitConfirm() {
  if (!state.active) return;
  if (confirm('Leave this quiz? Your progress will be lost.')) exitQuiz();
}

// ---------------------------------------------------------------------------
export function initQuiz(controller) {
  state.controller = controller || null;
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    if (state.active) { quitConfirm(); return; }
    const panel = $('#quizPanel');
    if (panel && !panel.hidden && state.view !== 'list') goList();
  });
}
