// Matrix Quiz UI controller: category browser (scroll + search), difficulty
// setup, the quiz runner, the right-hand "quest" panel, skip, results, quit.

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
  open: false,
  view: 'list', // list | setup | quiz | results
  ruleId: null,
  difficulty: 'easy',
  questions: [],
  index: 0,
  entries: [], // { question, chosen, correct, skipped }
  search: '',
};

// ---------------------------------------------------------------------------
// Open / close the quiz view
// ---------------------------------------------------------------------------
export function openQuizView() {
  const view = $('#quizView');
  if (!view) return;
  state.open = true;
  view.hidden = false;
  view.classList.add('active');
  document.body.classList.add('quiz-open');
  goList();
}

export function closeQuizView() {
  const view = $('#quizView');
  if (!view) return;
  state.open = false;
  view.classList.remove('active');
  view.hidden = true;
  document.body.classList.remove('quiz-open');
  hideQuest();
}

export function isQuizOpen() {
  return state.open;
}

// ---------------------------------------------------------------------------
// View: categories list
// ---------------------------------------------------------------------------
function goList() {
  state.view = 'list';
  hideQuest();
  setToolbar({ title: 'Matrix Quiz', subtitle: 'Pick a rule to practise \u2014 every question is drawn at random.' });
  showSearch(true);
  renderList();
}

function setToolbar({ title, subtitle, back = true }) {
  const t = $('#quizTitle');
  const s = $('#quizSubtitle');
  if (t) t.textContent = title;
  if (s) s.textContent = subtitle || '';
  const backBtn = $('#quizBackBtn');
  if (backBtn) backBtn.hidden = !back;
}

function showSearch(show) {
  const wrap = $('#quizSearchWrap');
  if (wrap) wrap.hidden = !show;
}

function renderList() {
  const body = $('#quizBody');
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

    const group = el('section', 'quiz-group');
    const h = el('div', 'quiz-group-head');
    h.appendChild(el('span', 'quiz-group-id', `${section.id}`));
    h.appendChild(el('h3', 'quiz-group-title', section.title));
    h.appendChild(el('span', 'quiz-group-count', `${matches.length}`));
    group.appendChild(h);

    const grid = el('div', 'quiz-grid');
    matches.forEach((rule) => grid.appendChild(ruleCard(rule)));
    group.appendChild(grid);
    body.appendChild(group);
  });

  if (!total) {
    const empty = el('p', 'quiz-empty', 'No rules match your search.');
    body.appendChild(empty);
  }
}

function ruleCard(rule) {
  const card = el('button', 'quiz-card');
  card.type = 'button';
  card.dataset.rule = rule.id;

  const top = el('div', 'quiz-card-top');
  top.appendChild(el('span', 'quiz-card-id', rule.id));
  const cap = hasQuiz(rule.id);
  const tag = el('span', `quiz-card-tag ${cap ? 'ready' : 'soon'}`, cap ? 'Ready' : 'Soon');
  top.appendChild(tag);
  card.appendChild(top);

  card.appendChild(el('div', 'quiz-card-rule', rule.rule));

  const foot = el('div', 'quiz-card-foot');
  const bad = el('span', 'quiz-bad', rule.example || '');
  foot.appendChild(bad);
  (rule.check || '').split('+').forEach((c) => {
    if (!c) return;
    foot.appendChild(el('span', `quiz-check check-${c.toLowerCase()}`, c));
  });
  card.appendChild(foot);

  card.addEventListener('click', () => goSetup(rule.id));
  return card;
}

// ---------------------------------------------------------------------------
// View: difficulty setup
// ---------------------------------------------------------------------------
function goSetup(ruleId) {
  state.ruleId = ruleId;
  state.view = 'setup';
  hideQuest();
  showSearch(false);
  const info = ruleInfo(ruleId);
  setToolbar({ title: `${ruleId} \u00b7 ${info ? info.rule : 'Quiz'}`, subtitle: 'Choose a difficulty to begin.' });
  renderSetup();
}

function renderSetup() {
  const body = $('#quizBody');
  if (!body) return;
  body.innerHTML = '';
  const info = ruleInfo(state.ruleId);
  const card = el('div', 'quiz-setup');

  if (!hasQuiz(state.ruleId)) {
    const soon = el('div', 'quiz-soon');
    soon.appendChild(el('h3', null, 'Quizzes coming soon'));
    soon.appendChild(el('p', null,
      `We are still writing exercises for \u201c${info ? info.rule : state.ruleId}\u201d. `
      + 'Word Forms is fully playable today \u2014 the rest of the matrix follows the same order.'));
    card.appendChild(soon);
    body.appendChild(card);
    return;
  }

  const meta = el('div', 'quiz-setup-meta');
  if (info) {
    meta.appendChild(el('span', 'quiz-bad', info.example || ''));
    meta.appendChild(el('span', 'quiz-setup-section', info.section));
  }
  card.appendChild(meta);

  card.appendChild(el('h3', 'quiz-setup-head', 'Difficulty'));
  const grid = el('div', 'quiz-diff-grid');
  Object.entries(DIFFICULTY).forEach(([key, d]) => {
    const btn = el('button', `quiz-diff ${state.difficulty === key ? 'selected' : ''}`);
    btn.type = 'button';
    btn.appendChild(el('span', 'quiz-diff-label', d.label));
    btn.appendChild(el('span', 'quiz-diff-count', `${d.count} questions`));
    btn.addEventListener('click', () => {
      state.difficulty = key;
      grid.querySelectorAll('.quiz-diff').forEach((b) => b.classList.remove('selected'));
      btn.classList.add('selected');
    });
    grid.appendChild(btn);
  });
  card.appendChild(grid);

  const start = el('button', 'quiz-start-btn', 'Start Quiz');
  start.type = 'button';
  start.addEventListener('click', startQuiz);
  card.appendChild(start);

  body.appendChild(card);
}

// ---------------------------------------------------------------------------
// View: quiz runner
// ---------------------------------------------------------------------------
function startQuiz() {
  const pool = questionPool(state.ruleId);
  const count = DIFFICULTY[state.difficulty].count;
  state.questions = pool.slice(0, Math.min(count, pool.length));
  state.index = 0;
  state.entries = [];
  state.view = 'quiz';
  showSearch(false);
  renderQuestion();
}

function renderQuestion() {
  const body = $('#quizBody');
  if (!body) return;
  const q = state.questions[state.index];
  if (!q) { showResults(); return; }
  body.innerHTML = '';
  const info = ruleInfo(state.ruleId);
  setToolbar({
    title: `${state.ruleId} \u00b7 ${info ? info.rule : ''}`,
    subtitle: '',
  });

  const wrap = el('div', 'quiz-question');

  const num = el('div', 'quiz-qnum', `Question ${state.index + 1} of ${state.questions.length}`);
  wrap.appendChild(num);

  wrap.appendChild(el('p', 'quiz-prompt', q.prompt));

  const opts = el('div', 'quiz-options');
  q.options.forEach((opt, i) => {
    const btn = el('button', 'quiz-option');
    btn.type = 'button';
    btn.dataset.index = String(i);
    btn.appendChild(el('span', 'quiz-option-key', INDEX_OPTIONS[i] || String(i + 1)));
    btn.appendChild(el('span', 'quiz-option-text', opt));
    btn.addEventListener('click', () => chooseOption(i));
    opts.appendChild(btn);
  });
  wrap.appendChild(opts);

  const feedback = el('div', 'quiz-feedback');
  feedback.id = 'quizFeedback';
  wrap.appendChild(feedback);

  const nav = el('div', 'quiz-nav');
  const skip = el('button', 'quiz-skip-btn', 'Skip');
  skip.type = 'button';
  skip.addEventListener('click', skipQuestion);
  nav.appendChild(skip);
  const next = el('button', 'quiz-next-btn', state.index + 1 >= state.questions.length ? 'Finish' : 'Next');
  next.type = 'button';
  next.id = 'quizNextBtn';
  next.disabled = true;
  next.addEventListener('click', advance);
  nav.appendChild(next);
  wrap.appendChild(nav);

  body.appendChild(wrap);
  renderQuest();
}

function chooseOption(i) {
  const q = state.questions[state.index];
  const entry = state.entries[state.index];
  if (entry && !entry.skipped) return; // already answered
  const correct = i === q.answer;
  state.entries[state.index] = { question: q, chosen: i, correct, skipped: false };

  const opts = document.querySelectorAll('#quizBody .quiz-option');
  opts.forEach((btn) => {
    btn.disabled = true;
    const idx = Number(btn.dataset.index);
    if (idx === q.answer) btn.classList.add('correct');
    if (idx === i && !correct) btn.classList.add('wrong');
  });

  const fb = $('#quizFeedback');
  if (fb) {
    fb.classList.add('show', correct ? 'ok' : 'err');
    fb.appendChild(el('strong', null, correct ? 'Correct.' : 'Not quite.'));
    fb.appendChild(el('span', null, ` ${q.explanation}`));
  }
  const next = $('#quizNextBtn');
  if (next) next.disabled = false;
  renderQuest();
}

function skipQuestion() {
  const q = state.questions[state.index];
  state.entries[state.index] = { question: q, chosen: null, correct: false, skipped: true };
  advance();
}

function advance() {
  if (state.index + 1 >= state.questions.length) {
    showResults();
    return;
  }
  state.index += 1;
  renderQuestion();
}

// ---------------------------------------------------------------------------
// View: results
// ---------------------------------------------------------------------------
function showResults() {
  state.view = 'results';
  const body = $('#quizBody');
  if (!body) return;
  body.innerHTML = '';
  const info = ruleInfo(state.ruleId);

  const correct = state.entries.filter((e) => e && e.correct).length;
  const total = state.questions.length;
  const skipped = state.entries.filter((e) => e && e.skipped).length;
  const pct = total ? Math.round((correct / total) * 100) : 0;

  const card = el('div', 'quiz-results');
  card.appendChild(el('h2', 'quiz-results-score', `${correct} / ${total}`));
  card.appendChild(el('p', 'quiz-results-sub',
    `${info ? info.rule : ''} \u00b7 ${DIFFICULTY[state.difficulty].label}${skipped ? ` \u00b7 ${skipped} skipped` : ''}`));

  const bar = el('div', 'quiz-result-bar');
  const fill = el('div', 'quiz-result-fill');
  fill.style.width = `${pct}%`;
  bar.appendChild(fill);
  card.appendChild(bar);

  const review = el('div', 'quiz-review');
  state.entries.forEach((entry, i) => {
    if (!entry) return;
    const row = el('div', `quiz-review-row ${entry.correct ? 'ok' : entry.skipped ? 'skip' : 'err'}`);
    const q = entry.question;
    const head = el('div', 'quiz-review-head');
    head.appendChild(el('span', 'quiz-review-i', `${i + 1}`));
    head.appendChild(el('span', 'quiz-review-sent', q.sentence));
    head.appendChild(el('span', 'quiz-review-mark', entry.correct ? '\u2713' : entry.skipped ? '\u2013' : '\u2717'));
    row.appendChild(head);
    const answers = el('div', 'quiz-review-answers');
    answers.appendChild(el('span', 'quiz-review-correct', `Correct: ${q.options[q.answer]}`));
    if (!entry.correct && !entry.skipped && entry.chosen != null) {
      answers.appendChild(el('span', 'quiz-review-yours', `You: ${q.options[entry.chosen]}`));
    } else if (entry.skipped) {
      answers.appendChild(el('span', 'quiz-review-yours', 'Skipped'));
    }
    row.appendChild(answers);
    review.appendChild(row);
  });
  card.appendChild(review);

  const actions = el('div', 'quiz-results-actions');
  const again = el('button', 'quiz-start-btn', 'Try again');
  again.type = 'button';
  again.addEventListener('click', startQuiz);
  const another = el('button', 'quiz-ghost-btn', 'Choose another rule');
  another.type = 'button';
  another.addEventListener('click', goList);
  const quit = el('button', 'quiz-ghost-btn', 'Quit');
  quit.type = 'button';
  quit.addEventListener('click', closeQuizView);
  actions.appendChild(again);
  actions.appendChild(another);
  actions.appendChild(quit);
  card.appendChild(actions);

  body.appendChild(card);
  renderResultsQuest(correct, total, skipped);
}

// ---------------------------------------------------------------------------
// Right-hand quest panel
// ---------------------------------------------------------------------------
function hideQuest() {
  const q = $('#quizQuest');
  if (q) { q.hidden = true; q.innerHTML = ''; }
}

function showQuest() {
  const q = $('#quizQuest');
  if (q) q.hidden = false;
  return q;
}

function renderQuest() {
  const panel = showQuest();
  if (!panel) return;
  panel.innerHTML = '';
  const info = ruleInfo(state.ruleId);
  const q = state.questions[state.index];

  const head = el('div', 'quest-head');
  head.appendChild(el('span', 'quest-eyebrow', 'Quest'));
  head.appendChild(el('h3', 'quest-rule', info ? info.rule : ''));
  head.appendChild(el('span', 'quest-id', state.ruleId));
  panel.appendChild(head);

  const meta = el('div', 'quest-meta');
  meta.appendChild(el('span', 'quest-tag', DIFFICULTY[state.difficulty].label));
  meta.appendChild(el('span', 'quest-count', `${state.index + 1} / ${state.questions.length}`));
  panel.appendChild(meta);

  const progress = el('div', 'quest-progress');
  const fill = el('div', 'quest-progress-fill');
  const done = state.entries.filter(Boolean).length;
  fill.style.width = `${Math.round((done / state.questions.length) * 100)}%`;
  progress.appendChild(fill);
  panel.appendChild(progress);

  const sentBox = el('div', 'quest-sentence');
  sentBox.appendChild(el('span', 'quest-sentence-label', 'Sentence'));
  sentBox.appendChild(el('p', null, q.sentence));
  panel.appendChild(sentBox);

  const actions = el('div', 'quest-actions');
  const skip = el('button', 'quest-skip', 'Skip to next');
  skip.type = 'button';
  skip.addEventListener('click', skipQuestion);
  const quit = el('button', 'quest-quit', 'Quit quiz');
  quit.type = 'button';
  quit.addEventListener('click', () => {
    if (confirm('Quit this quiz? Your progress will be lost.')) closeQuizView();
  });
  actions.appendChild(skip);
  actions.appendChild(quit);
  panel.appendChild(actions);
}

function renderResultsQuest(correct, total, skipped) {
  const panel = showQuest();
  if (!panel) return;
  panel.innerHTML = '';
  const info = ruleInfo(state.ruleId);

  const head = el('div', 'quest-head');
  head.appendChild(el('span', 'quest-eyebrow', 'Quest complete'));
  head.appendChild(el('h3', 'quest-rule', info ? info.rule : ''));
  head.appendChild(el('span', 'quest-id', state.ruleId));
  panel.appendChild(head);

  const score = el('div', 'quest-score');
  score.appendChild(el('span', 'quest-score-num', `${correct}/${total}`));
  score.appendChild(el('span', 'quest-score-label', skipped ? `${skipped} skipped` : 'all answered'));
  panel.appendChild(score);

  const actions = el('div', 'quest-actions');
  const again = el('button', 'quest-skip', 'Try again');
  again.type = 'button';
  again.addEventListener('click', startQuiz);
  const quit = el('button', 'quest-quit', 'Quit quiz');
  quit.type = 'button';
  quit.addEventListener('click', closeQuizView);
  actions.appendChild(again);
  actions.appendChild(quit);
  panel.appendChild(actions);
}

// ---------------------------------------------------------------------------
// Wiring
// ---------------------------------------------------------------------------
export function initQuiz() {
  $('#quizSearch')?.addEventListener('input', (e) => {
    state.search = e.target.value;
    if (state.view === 'list') renderList();
  });

  $('#quizBackBtn')?.addEventListener('click', () => {
    if (state.view === 'list') closeQuizView();
    else if (state.view === 'setup') goList();
    else if (state.view === 'quiz') {
      if (confirm('Leave this quiz? Your progress will be lost.')) goList();
    } else goList();
  });

  document.addEventListener('keydown', (e) => {
    if (!state.open || e.key !== 'Escape') return;
    const view = $('#quizView');
    if (view && !view.hidden) {
      if (state.view === 'list') closeQuizView();
      else goList();
    }
  });
}
