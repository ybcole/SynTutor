// Syntax-Tree Quiz — a textbook for building syntax trees.
//
// There are no "stages". The lesson list is the inventory of phrase
// constructions SynTutor's parser knows, ordered from simple building blocks
// (noun/adjective/adverb/prepositional/verb phrases) through wh-phrases and
// quantifiers to whole clauses, questions and special phrases. Each lesson
// explains, in words, how that phrase is built, then gives real examples.
//
// Two entry points:
//   * Quiz (sidebar)    — starts a quiz straight away and walks every
//                         construction in order, advancing automatically each
//                         time the learner's tree matches SynTutor's parse.
//   * Lessons (sidebar) — the same textbook, read at your own pace; every
//                         lesson ends with its own quiz.
//
// Each example is done *in the Syntax Builder*: the sentence is shown in the
// input box with its words already laid out, the learner builds the phrase
// structure by adding phrase boxes and connecting them, and the tree is checked
// against SynTutor's own parse — fetched live from /api/parse, so the gold tree
// can never drift from the model.
//
// Exports the surface main.js imports:
//   openQuizView, closeQuizView, isQuizOpen, initQuiz, quizInputHint

import { openBuilderView, closeBuilderView } from './syntax-builder-ui.js';
import { leavesWithTags } from './syntax-builder.js';

const $ = (sel, root = document) => root.querySelector(sel);

const state = {
  view: 'lessons',    // lessons | lesson
  lessonIndex: null,
  controller: null,
  cache: new Map(),   // sentence -> gold
  done: new Set(),    // `${type}:${example}`
  session: null,      // { seq: [{lesson, example}], pos }
};

// The textbook, in order. `type` is the official parser label; `rule` is the
// "how to build it" explanation shown before the examples.
const LESSONS = [
  {
    type: 'NP', title: 'Noun phrase', group: 'Phrases',
    rule: 'A noun phrase is built around a noun head. Put a determiner in front, then any adjectives, then the noun: DT → ADJP → N. So "the", "big", "cat" combine into a single NP.',
    examples: ['the big cat', 'a student of physics', 'my older sister'],
  },
  {
    type: 'ADJP', title: 'Adjective phrase', group: 'Phrases',
    rule: 'An adjective phrase is built around an adjective. An adverb may go before it and a prepositional phrase may follow: (RB) → ADJ → (PP).',
    examples: ['very happy', 'fond of music', 'extremely proud of her'],
  },
  {
    type: 'ADVP', title: 'Adverb phrase', group: 'Phrases',
    rule: 'An adverb phrase is built around an adverb. A degree adverb may modify it: (RB) → ADV.',
    examples: ['very quickly', 'quite well'],
  },
  {
    type: 'VP', title: 'Verb phrase', group: 'Phrases',
    rule: 'A verb phrase is built around a verb, together with its object or complement: V → (NP) → (PP).',
    examples: ['is running', 'has eaten the cake'],
  },
  {
    type: 'PP', title: 'Prepositional phrase', group: 'Phrases',
    rule: 'A prepositional phrase is a preposition followed by a noun phrase: IN → NP.',
    examples: ['in the garden', 'of physics', 'on the small table'],
  },
  {
    type: 'QP', title: 'Quantifier phrase', group: 'Phrases',
    rule: 'A quantifier phrase expresses an amount, often with a comparative and "than": (JJR) → (IN) → CD.',
    examples: ['More than five people came.'],
  },
  {
    type: 'S', title: 'Clause (sentence)', group: 'Clauses',
    rule: 'A clause joins a subject noun phrase to a predicate verb phrase: NP → VP. This is the top of a normal sentence.',
    examples: ['The cat sat.', 'The dog chased the ball.', 'Birds sing.'],
  },
  {
    type: 'SQ', title: 'Yes/no question', group: 'Clauses',
    rule: 'A yes/no question inverts the auxiliary and the subject: AUX → NP → VP.',
    examples: ['Is it raining?', 'Did she leave?', 'Can you swim?'],
  },
  {
    type: 'SBARQ', title: 'Wh-question', group: 'Clauses',
    rule: 'A wh-question puts a wh-phrase first, then inverts the auxiliary with the subject: WH-phrase → AUX → NP.',
    examples: ['What did you say?', 'Who ate the cake?', 'Where is the cat?'],
  },
  {
    type: 'SBAR', title: 'Subordinate clause', group: 'Clauses',
    rule: 'A subordinate clause is introduced by a complementizer (or a relative pronoun) followed by a clause: IN → S.',
    examples: ['because he left', 'that she knows', 'which I saw'],
  },
  {
    type: 'SINV', title: 'Inverted clause', group: 'Clauses',
    rule: 'An inverted clause fronts a negative or restrictive phrase and inverts the auxiliary with the subject: ADVP → AUX → NP.',
    examples: ['Never have I seen such a thing.', 'Rarely does he complain.'],
  },
  {
    type: 'WHNP', title: 'Wh-noun phrase', group: 'Wh-phrases',
    rule: 'A wh-noun phrase begins with a wh-determiner or wh-pronoun and then the noun that belongs to it: WDT → N.',
    examples: ['which book', 'what color'],
  },
  {
    type: 'WHADJP', title: 'Wh-adjective phrase', group: 'Wh-phrases',
    rule: 'A wh-adjective phrase asks "how …?" about an adjective: how → ADJ.',
    examples: ['how old'],
  },
  {
    type: 'WHADVP', title: 'Wh-adverb phrase', group: 'Wh-phrases',
    rule: 'A wh-adverb phrase is a single wh-adverb standing in for when/where/how/why: WRB.',
    examples: ['where', 'when', 'how'],
  },
  {
    type: 'WHPP', title: 'Wh-prepositional phrase', group: 'Wh-phrases',
    rule: 'A wh-prepositional phrase is a preposition with a wh-noun phrase: IN → WHNP.',
    examples: ['to whom', 'for what'],
  },
  {
    type: 'CONJP', title: 'Conjunction phrase', group: 'Special phrases',
    rule: 'A conjunction phrase links two items using a multi-word conjunction: CC → X.',
    examples: ['as well as'],
  },
  {
    type: 'UCP', title: 'Unlike-coordinated phrase', group: 'Special phrases',
    rule: 'An unlike-coordinated phrase coordinates two items of different categories: X → CC → Y.',
    examples: ['first, second'],
  },
  {
    type: 'PRT', title: 'Particle', group: 'Special phrases',
    rule: 'A particle is a small adverb-like word that completes a phrasal verb. It hangs directly off the verb phrase: VB → PRT.',
    examples: ['Throw it away.', 'Give up the fight.'],
  },
  {
    type: 'FRAG', title: 'Fragment', group: 'Special phrases',
    rule: 'A fragment is a phrase standing alone as an utterance, without a subject and predicate.',
    examples: ['Hello there.'],
  },
  {
    type: 'INTJ', title: 'Interjection', group: 'Special phrases',
    rule: 'An interjection is a word that expresses emotion on its own: Wow! Hey!',
    examples: ['Wow!', 'Hey!'],
  },
];

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

// `view` may be 'quiz' (start a quiz now), 'lessons' (open the textbook), or
// 'leaderboard'/'achievements' (not built yet — show a placeholder).
export function openQuizView(view = 'quiz') {
  if (view === 'leaderboard' || view === 'achievements') {
    return showPlaceholder(view);
  }
  if (view === 'lessons') {
    openPanel('lessons');
    state.view = 'lessons';
    render();
    return;
  }
  // 'quiz' (or default): start immediately — the learner doesn't pick a
  // sentence, the quiz serves them in order.
  closeQuizView();
  startSession(flatExamples());
}

function showPlaceholder(view) {
  const panel = $('#quizPanel');
  if (!panel) return;
  closeBuilderView();
  panel.hidden = false;
  $('#appSidebar')?.classList.add('quiz-active');
  $('#appSidebarBackdrop')?.classList.add('active');
  document.querySelectorAll('.sidebar-item').forEach((b) => {
    b.classList.toggle('active', b.dataset.view === view);
  });
  panel.innerHTML = '';
  const body = shell({ title: view === 'leaderboard' ? 'Leaderboard' : 'Achievements' });
  body.appendChild(el('p', 'sq-intro', 'Coming soon.'));
}

function openPanel(view) {
  const panel = $('#quizPanel');
  if (!panel) return;
  closeBuilderView();
  panel.hidden = false;
  $('#appSidebar')?.classList.add('quiz-active');
  $('#appSidebarBackdrop')?.classList.add('active');
  $('#sidebarToggleBtn')?.setAttribute('aria-expanded', 'true');
  document.querySelectorAll('.sidebar-item').forEach((b) => {
    b.classList.toggle('active', b.dataset.view === view);
  });
}

export function closeQuizView() {
  const panel = $('#quizPanel');
  if (panel) { panel.hidden = true; panel.innerHTML = ''; }
  $('#appSidebar')?.classList.remove('quiz-active');
}

export function isQuizOpen() {
  return Boolean($('#quizPanel') && !$('#quizPanel').hidden);
}

export function quizInputHint() {
  return 'Build the tree on the canvas — it checks itself as you go.';
}

export function initQuiz(controller) {
  state.controller = controller || null;
}

// ---------------------------------------------------------------------------
// Quiz session: walk a sequence of examples, advancing when each is solved
// ---------------------------------------------------------------------------
function flatExamples() {
  const seq = [];
  for (const lesson of LESSONS) {
    for (const example of lesson.examples) seq.push({ lesson, example });
  }
  return seq;
}

function startSession(seq, pos = 0) {
  state.session = { seq, pos };
  advance();
}

async function advance() {
  const s = state.session;
  if (!s) return;
  if (s.pos >= s.seq.length) return finishSession();
  const { lesson, example } = s.seq[s.pos];
  await startChallenge(lesson, example, (ok) => {
    if (!ok) return;
    const solvedPos = s.pos;
    setTimeout(() => {
      if (state.session !== s || s.pos !== solvedPos) return;
      s.pos += 1;
      advance();
    }, 1200);
  });
}

function finishSession() {
  state.session = null;
  closeBuilderView();
  const panel = $('#quizPanel');
  if (!panel) return;
  panel.hidden = false;
  $('#appSidebar')?.classList.add('quiz-active');
  $('#appSidebarBackdrop')?.classList.add('active');
  document.querySelectorAll('.sidebar-item').forEach((b) => {
    b.classList.toggle('active', b.dataset.view === 'quiz');
  });
  panel.innerHTML = '';
  const body = shell({ title: "You've built every tree!" });
  body.appendChild(el('p', 'sq-intro', 'Nice work — you constructed every phrase type SynTutor knows.'));
  const again = el('button', 'sq-stage sq-stage-alt');
  again.type = 'button';
  again.appendChild(el('span', 'sq-stage-title', 'Start again'));
  again.addEventListener('click', () => { closeQuizView(); startSession(flatExamples()); });
  body.appendChild(again);
}

// ---------------------------------------------------------------------------
// Shell + lesson views
// ---------------------------------------------------------------------------
function shell({ title, back }) {
  const panel = $('#quizPanel');
  panel.innerHTML = '';
  const head = el('div', 'sq-head');
  if (back) {
    const b = el('button', 'sq-back');
    b.type = 'button';
    b.setAttribute('aria-label', 'Back');
    b.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>';
    b.addEventListener('click', back);
    head.appendChild(b);
  }
  head.appendChild(el('h2', 'sq-title', title));
  panel.appendChild(head);
  const body = el('div', 'sq-body');
  panel.appendChild(body);
  return body;
}

function render() {
  if (state.view === 'lesson') return renderLesson();
  return renderLessons();
}

// ---------------------------------------------------------------------------
// Lessons: the textbook table of contents
// ---------------------------------------------------------------------------
function renderLessons() {
  const body = shell({ title: 'How to build syntax trees' });
  body.appendChild(el('p', 'sq-intro',
    'A textbook of phrase constructions, simplest first. Read how each one is built, then take its quiz in the Syntax Builder.'));

  let lastGroup = null;
  for (const lesson of LESSONS) {
    if (lesson.group !== lastGroup) {
      lastGroup = lesson.group;
      body.appendChild(el('div', 'sq-group', lesson.group));
    }
    const card = el('button', 'sq-stage');
    card.type = 'button';
    card.appendChild(el('span', 'sq-stage-num', lesson.type));
    card.appendChild(el('span', 'sq-stage-title', lesson.title));
    card.appendChild(el('span', 'sq-stage-blurb', lesson.rule));
    const done = lesson.examples.filter((e) => state.done.has(`${lesson.type}:${e}`)).length;
    card.appendChild(el('span', 'sq-stage-count', `${done}/${lesson.examples.length}`));
    card.addEventListener('click', () => { state.lessonIndex = lesson.type; state.view = 'lesson'; render(); });
    body.appendChild(card);
  }

  const practice = el('button', 'sq-stage sq-stage-alt');
  practice.type = 'button';
  practice.appendChild(el('span', 'sq-stage-num', 'Free'));
  practice.appendChild(el('span', 'sq-stage-title', 'Syntax Builder'));
  practice.appendChild(el('span', 'sq-stage-blurb', 'Open a blank canvas and build any tree by hand.'));
  practice.addEventListener('click', () => {
    closeQuizView();
    $('#appSidebarBackdrop')?.classList.remove('active');
    openBuilderView();
  });
  body.appendChild(practice);
}

// ---------------------------------------------------------------------------
// Lesson: one construction + its examples + its quiz
// ---------------------------------------------------------------------------
function renderLesson() {
  const lesson = LESSONS.find((l) => l.type === state.lessonIndex);
  const body = shell({
    title: `${lesson.type} · ${lesson.title}`,
    back: () => { state.view = 'lessons'; render(); },
  });

  const rule = el('div', 'sq-rule');
  rule.appendChild(el('span', 'sq-rule-tag', lesson.type));
  rule.appendChild(el('p', 'sq-rule-text', lesson.rule));
  body.appendChild(rule);

  body.appendChild(el('div', 'sq-group', 'Build these'));
  for (const example of lesson.examples) {
    const row = el('button', 'sq-challenge');
    row.type = 'button';
    const isDone = state.done.has(`${lesson.type}:${example}`);
    if (isDone) row.classList.add('is-done');
    row.appendChild(el('span', 'sq-challenge-mark', isDone ? '✓' : '▸'));
    row.appendChild(el('span', 'sq-challenge-sentence', example));
    row.addEventListener('click', () => startChallenge(lesson, example));
    body.appendChild(row);
  }

  const quiz = el('button', 'sq-stage sq-stage-alt');
  quiz.type = 'button';
  quiz.appendChild(el('span', 'sq-stage-num', 'Quiz'));
  quiz.appendChild(el('span', 'sq-stage-title', `Quiz: ${lesson.title}`));
  quiz.appendChild(el('span', 'sq-stage-blurb', 'Build every example in this lesson, in order.'));
  quiz.addEventListener('click', () => {
    closeQuizView();
    $('#appSidebarBackdrop')?.classList.remove('active');
    startSession(lesson.examples.map((example) => ({ lesson, example })));
  });
  body.appendChild(quiz);
}

// ---------------------------------------------------------------------------
// Start an example: show the sentence, load gold, open the builder
// ---------------------------------------------------------------------------
async function startChallenge(lesson, example, onDone) {
  const input = $('#inputText');
  if (input) input.value = example;
  const highlights = $('#inputHighlights');
  if (highlights) highlights.innerHTML = '';

  closeQuizView();
  $('#appSidebarBackdrop')?.classList.remove('active');

  let gold = state.cache.get(example);
  if (!gold) {
    openBuilderView({ challenge: { kind: 'full', target: example, hint: lesson.rule, gold: [], goldTree: null } });
    try {
      gold = await loadGold(example);
    } catch (err) {
      setBuilderHint(`Could not reach SynTutor's model: ${err.message}`);
      return;
    }
    state.cache.set(example, gold);
  }

  openBuilderView({
    challenge: {
      kind: 'full',
      target: example,
      hint: lesson.rule,
      gold: gold.leaves,
      goldTree: gold.tree,
    },
    onComplete: (ok) => {
      record(lesson, example, ok);
      onDone?.(ok);
    },
  });
}

function record(lesson, example, ok) {
  if (!ok) return;
  state.done.add(`${lesson.type}:${example}`);
  const progress = state.controller?.progress;
  if (progress && typeof progress.trackCompletion === 'function') {
    try { progress.trackCompletion({ ruleId: lesson.type, perfect: true }); } catch { /* ignore */ }
  }
}

// ---------------------------------------------------------------------------
// Gold data straight from SynTutor's own parser
// ---------------------------------------------------------------------------
async function loadGold(sentence) {
  const res = await fetch('/api/parse', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: sentence }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const payload = await res.json();
  const tree = apiTree(payload.tree);
  return { tree, leaves: leavesWithTags(tree) };
}

// Reduce /api/parse's node tree to the {type, children|leaf, surface} shape the
// comparison + leaf helpers expect.
function apiTree(node) {
  if (!node) return null;
  const kids = node.children;
  if (!kids || kids.length === 0) {
    return { type: node.type, leaf: true, surface: node.surface ?? '' };
  }
  return { type: node.type, children: kids.map(apiTree) };
}

function setBuilderHint(msg) {
  const hint = $('#builderHint');
  if (hint) hint.textContent = msg;
}
