// Matrix Quiz UI controller. Everything renders inside the left sidebar panel
// (#quizPanel): a searchable, scrollable, vertical list of rule quizzes, the
// difficulty setup, the question runner, and the results screen.

import {
  MATRIX_SECTIONS, DIFFICULTY, questionPool, ruleInfo, hasQuiz, INDEX_OPTIONS,
} from './quiz-data.js';

const $ = (sel, root = document) => root.querySelector(sel);

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
}

const state = {
  view: 'list', // list | setup | quiz | results
  ruleId: null,
  difficulty: 'easy',
  questions: [],
  index: 0,
  entries: [],
  search: '',
  body: null,
};

// ---------------------------------------------------------------------------
// Open / close
// ---------------------------------------------------------------------------
export function openQuizView() {
  const panel = $('#quizPanel');
  if (!panel) return;
  panel.hidden = false;
  $('#appSidebar')?.classList.add('quiz-active');
  $('#appSidebarBackdrop')?.classList.add('active');
  $('#sidebarToggleBtn')?.setAttribute('aria-expanded', 'true');
  document.querySelectorAll('.sidebar-item').forEach((b) => {
    b.classList.toggle('active', b.dataset.view === 'quiz');
  });
  goList();
}

export function closeQuizView() {
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

// ---------------------------------------------------------------------------
// Panel shell
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
  shell({ title: 'Matrix Quiz', search: true });
  renderList();
}

function renderList() {
  const body = state.body;
  if (!body) return;
  body.innerHTML = '';
  const query = state.search.trim().toLowerCase();

  let total = 0;
  MATRIX_SECTIONS.forEach((section) => {
    const matches = section.rules.filter((r) => {
      if (!query) return true;
      return r.id.includes(query)
        || r.rule.toLowerCase().includes(query)
        || (r.example || '').toLowerCase().includes(query);
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

  if (!total) body.appendChild(el('p', 'sq-empty', 'No rules match your search.'));
}

function ruleRow(rule) {
  const row = el('button', 'sq-row');
  row.type = 'button';
  row.dataset.rule = rule.id;

  const top = el('div', 'sq-row-top');
  top.appendChild(el('span', 'sq-row-id', rule.id));
  top.appendChild(el('span', 'sq-row-rule', rule.rule));
  const ready = hasQuiz(rule.id);
  top.appendChild(el('span', `sq-dot ${ready ? 'ready' : 'soon'}`, ''));
  row.appendChild(top);

  const foot = el('div', 'sq-row-foot');
  foot.appendChild(el('span', 'sq-bad', rule.example || ''));
  (rule.check || '').split('+').forEach((c) => {
    if (!c) return;
    foot.appendChild(el('span', `sq-check check-${c.toLowerCase()}`, c));
  });
  if (!ready) foot.appendChild(el('span', 'sq-soon', 'soon'));
  row.appendChild(foot);

  row.addEventListener('click', () => goSetup(rule.id));
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
      `Quizzes for \u201c${info ? info.rule : ruleId}\u201d are coming soon. Word Forms is fully playable now.`));
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
    btn.appendChild(el('span', 'sq-diff-count', `${d.count} questions`));
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
// Runner
// ---------------------------------------------------------------------------
function startQuiz() {
  const pool = questionPool(state.ruleId);
  const count = DIFFICULTY[state.difficulty].count;
  state.questions = pool.slice(0, Math.min(count, pool.length));
  state.index = 0;
  state.entries = [];
  state.view = 'quiz';
  renderQuestion();
}

function renderQuestion() {
  const q = state.questions[state.index];
  if (!q) { showResults(); return; }
  const info = ruleInfo(state.ruleId);
  const body = shell({
    title: state.ruleId,
    back: quitConfirm,
    meta: questMeta(info, q),
  });

  body.appendChild(el('p', 'sq-num', `Question ${state.index + 1} of ${state.questions.length}`));
  body.appendChild(el('p', 'sq-prompt', q.prompt));

  const opts = el('div', 'sq-options');
  q.options.forEach((opt, i) => {
    const btn = el('button', 'sq-option');
    btn.type = 'button';
    btn.dataset.index = String(i);
    btn.appendChild(el('span', 'sq-option-key', INDEX_OPTIONS[i] || String(i + 1)));
    btn.appendChild(el('span', 'sq-option-text', opt));
    btn.addEventListener('click', () => chooseOption(i));
    opts.appendChild(btn);
  });
  body.appendChild(opts);

  const fb = el('div', 'sq-feedback');
  fb.id = 'sqFeedback';
  body.appendChild(fb);

  const nav = el('div', 'sq-nav');
  const skip = el('button', 'sq-ghost', 'Skip');
  skip.type = 'button';
  skip.addEventListener('click', skipQuestion);
  nav.appendChild(skip);
  const next = el('button', 'sq-primary', state.index + 1 >= state.questions.length ? 'Finish' : 'Next');
  next.type = 'button';
  next.id = 'sqNextBtn';
  next.disabled = true;
  next.addEventListener('click', advance);
  nav.appendChild(next);
  body.appendChild(nav);
}

function questMeta(info, q) {
  const meta = el('div', 'sq-meta');
  const line = el('div', 'sq-meta-line');
  line.appendChild(el('span', 'sq-meta-rule', info ? info.rule : ''));
  line.appendChild(el('span', 'sq-meta-diff', DIFFICULTY[state.difficulty].label));
  meta.appendChild(line);

  const progress = el('div', 'sq-progress');
  const fill = el('div', 'sq-progress-fill');
  const done = state.entries.filter(Boolean).length;
  fill.style.width = `${Math.round((done / state.questions.length) * 100)}%`;
  progress.appendChild(fill);
  meta.appendChild(progress);

  const sent = el('div', 'sq-sentence');
  sent.appendChild(el('span', 'sq-sentence-label', 'Sentence'));
  sent.appendChild(el('p', null, q.sentence));
  meta.appendChild(sent);
  return meta;
}

function chooseOption(i) {
  const q = state.questions[state.index];
  const entry = state.entries[state.index];
  if (entry && !entry.skipped) return;
  const correct = i === q.answer;
  state.entries[state.index] = { question: q, chosen: i, correct, skipped: false };

  document.querySelectorAll('#quizPanel .sq-option').forEach((btn) => {
    btn.disabled = true;
    const idx = Number(btn.dataset.index);
    if (idx === q.answer) btn.classList.add('correct');
    if (idx === i && !correct) btn.classList.add('wrong');
  });

  const fb = $('#sqFeedback');
  if (fb) {
    fb.classList.add('show', correct ? 'ok' : 'err');
    fb.appendChild(el('strong', null, correct ? 'Correct.' : 'Not quite.'));
    fb.appendChild(el('span', null, ` ${q.explanation}`));
  }
  const next = $('#sqNextBtn');
  if (next) next.disabled = false;
}

function skipQuestion() {
  const q = state.questions[state.index];
  state.entries[state.index] = { question: q, chosen: null, correct: false, skipped: true };
  advance();
}

function advance() {
  if (state.index + 1 >= state.questions.length) { showResults(); return; }
  state.index += 1;
  renderQuestion();
}

// ---------------------------------------------------------------------------
// Results
// ---------------------------------------------------------------------------
function showResults() {
  state.view = 'results';
  const info = ruleInfo(state.ruleId);
  const correct = state.entries.filter((e) => e && e.correct).length;
  const total = state.questions.length;
  const skipped = state.entries.filter((e) => e && e.skipped).length;
  const pct = total ? Math.round((correct / total) * 100) : 0;

  const body = shell({ title: 'Results', back: goList });

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

  const review = el('div', 'sq-review');
  state.entries.forEach((entry, i) => {
    if (!entry) return;
    const q = entry.question;
    const row = el('div', `sq-review-row ${entry.correct ? 'ok' : entry.skipped ? 'skip' : 'err'}`);
    const head = el('div', 'sq-review-head');
    head.appendChild(el('span', 'sq-review-i', `${i + 1}`));
    head.appendChild(el('span', 'sq-review-sent', q.sentence));
    head.appendChild(el('span', 'sq-review-mark', entry.correct ? '\u2713' : entry.skipped ? '\u2013' : '\u2717'));
    row.appendChild(head);
    const ans = el('div', 'sq-review-ans');
    ans.appendChild(el('span', 'sq-review-correct', `Correct: ${q.options[q.answer]}`));
    if (entry.skipped) ans.appendChild(el('span', 'sq-review-yours', 'Skipped'));
    else if (!entry.correct && entry.chosen != null) ans.appendChild(el('span', 'sq-review-yours', `You: ${q.options[entry.chosen]}`));
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
  another.addEventListener('click', goList);
  actions.appendChild(again);
  actions.appendChild(another);
  body.appendChild(actions);
}

// ---------------------------------------------------------------------------
function quitConfirm() {
  if (state.view === 'list') { closeQuizView(); return; }
  if (state.view === 'setup' || state.view === 'results') { goList(); return; }
  if (confirm('Leave this quiz? Your progress will be lost.')) goList();
}

export function initQuiz() {
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    const panel = $('#quizPanel');
    if (panel && !panel.hidden) quitConfirm();
  });
}
