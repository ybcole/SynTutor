// Syntax-Tree Quiz — a textbook for building syntax trees.
//
// There are no "stages". The lesson list is the inventory of phrase
// constructions SynTutor's parser knows, ordered from simple building blocks
// (noun/adjective/adverb/prepositional/verb phrases) through wh-phrases and
// quantifiers to whole clauses, questions and special phrases. Each lesson
// gives an in-depth explanation, a numbered step-by-step tree-building guide
// for each example, and its own quiz.
//
// Two entry points:
//   * Quiz (sidebar)    — starts a quiz straight away and walks every
//                         construction in order, advancing automatically each
//                         time the learner's tree matches SynTutor's parse.
//   * Lessons (sidebar) — a frosted-glass overlay of module cards with
//                         per-lesson progress: pick a category and a topic,
//                         then step through its Concept → Steps → Practice
//                         pages; the module's comprehensive quiz appears
//                         exclusively at the very end, on page 4.
//
// Each example is done *in the Syntax Builder*: the sentence is shown in the
// input box with its words already laid out, the learner builds the phrase
// structure by hand — right-clicking to add phrase boxes and dragging
// connector dots to connect them, re-route, or delete — and the tree is
// checked against SynTutor's own parse — fetched live from /api/parse, so the
// gold tree can never drift from the model. The Steps page can hand the
// learner an interactive spotlight guide that points at the exact canvas
// region, word row, or box each step talks about.
//
// Exports the surface main.js imports:
//   openQuizView, closeQuizView, isQuizOpen, initQuiz, quizInputHint,
//   clearActiveLesson

import { openBuilderView, closeBuilderView, setBuilderCloseHandler, builderModel, canvasGuideBox } from './syntax-builder-ui.js';
import { leavesWithTags, NODE, PHRASE_NODE_TYPES } from './syntax-builder.js';

const $ = (sel, root = document) => root.querySelector(sel);

const state = {
  view: 'lessons',    // lessons | lesson
  lessonIndex: null,
  exampleIndex: 0,    // active example inside the open lesson
  lessonPage: 1,      // lesson sub-view: 1 concept | 2 steps | 3 practice | 4 quiz
  lessonsTab: 0,      // active category page in the lessons overlay
  controller: null,
  cache: new Map(),   // sentence -> gold
  done: new Set(),    // `${type}:${example}`
  session: null,      // { seq: [{lesson, example}], pos }
};

// The textbook, in order. `type` is the official parser label; `rule` is the
// one-line "how to build it" summary used as the in-canvas hint; `detail` is
// the in-depth explanation (role, head, modifiers/complements, recognition);
// `steps` is the numbered guide for assembling the example's tree on canvas.
const LESSONS = [
  {
    type: 'NP', title: 'Noun phrase', group: 'Phrases',
    rule: 'A noun phrase is built around a noun head. Put a determiner in front, then any adjectives, then the noun: DT → ADJP → N. So "the", "big", "cat" combine into a single NP.',
    detail: 'A noun phrase names a person, thing, or idea. Its head is a noun (NN, NNS, NNP) or a pronoun (PRP), and the phrase is the unit that serves as the subject or object of a clause. Modifiers sit in front of the head - a determiner (DT), a possessive (PRP$), or one or more adjectives grouped into an adjective phrase (ADJP) - while complements such as a prepositional phrase (PP) or a relative clause (SBAR) follow it. To recognize a noun phrase, ask "who or what?" about the clause verb: the answer is typically an NP, and its head noun is the last major word of the phrase.',
    steps: [
      'Read the pre-placed leaves and their POS tags: the determiner (DT), any adjectives (JJ/JJR/JJS), the noun head (NN/NNS/NNP), and any prepositional-phrase words (IN ... ).',
      'If the phrase has adjectives, right-click an empty spot on the canvas and add an ADJP box; drag its connector dot onto the adjective word(s).',
      'Right-click again and add the NP box; drag its connector dot onto its children in reading order - determiner, ADJP (if any), then the noun head.',
      'If a prepositional phrase completes the noun, add a PP box, connect it to the NP after the head, and attach the preposition and its own noun-phrase object beneath it.',
      'Check that the NP leaves read left to right exactly like the example sentence - the canvas checks the tree automatically as you connect boxes.',
    ],
    examples: ['the big cat', 'a student of physics', 'my older sister'],
  },
  {
    type: 'ADJP', title: 'Adjective phrase', group: 'Phrases',
    rule: 'An adjective phrase is built around an adjective. An adverb may go before it and a prepositional phrase may follow: (RB) → ADJ → (PP).',
    detail: 'An adjective phrase describes a quality and is headed by an adjective (JJ, JJR, JJS). It works either attributively, inside a noun phrase ("the very happy child"), or predicatively, as the complement of a linking verb ("she is very happy"). A degree adverb (RB) may modify the head in front of it, and a prepositional phrase (PP) or infinitive clause may complete it from behind. Recognize it by asking "what kind?" or "how ...?" about a noun: the answer is an ADJP whose head is the last adjective in the phrase.',
    steps: [
      'Find the head adjective (JJ) and everything attached to it: a degree adverb (RB) before the head and/or a prepositional phrase (PP) after it.',
      'Right-click the canvas and add the ADJP box; drag its connector dot onto the degree adverb and the adjective head, in reading order.',
      'If a prepositional phrase complements the adjective, add a PP box, connect it to the ADJP after the head, and attach the preposition and its noun-phrase object underneath.',
      'Check that the leaves match the example phrase exactly - the canvas checks the tree automatically.',
    ],
    examples: ['very happy', 'fond of music', 'extremely proud of her'],
  },
  {
    type: 'ADVP', title: 'Adverb phrase', group: 'Phrases',
    rule: 'An adverb phrase is built around an adverb. A degree adverb may modify it: (RB) → ADV.',
    detail: 'An adverb phrase tells how, when, where, or to what degree, and its head is an adverb (RB, RBR, RBS). Adverb phrases modify verbs, adjectives, or other adverbs ("runs very quickly"), and some act as clausal adjuncts ("rarely does he complain"). A degree adverb (RB) can stand in front of the head, which is normally the last adverb of the phrase. To recognize one, ask "how?", "when?", or "where?" about the verb or adjective it attaches to.',
    steps: [
      'Spot the adverb head (RB/RBR/RBS) and any degree adverb (RB) that modifies it.',
      'Right-click the canvas and add the ADVP box; connect it to the degree adverb first, then to the adverb head.',
      'If the adverb has no modifiers, connect the ADVP straight to the single adverb.',
      'Check that the leaves match the example phrase - the canvas checks the tree automatically.',
    ],
    examples: ['very quickly', 'quite well'],
  },
  {
    type: 'VP', title: 'Verb phrase', group: 'Phrases',
    rule: 'A verb phrase is built around a verb, together with its object or complement: V → (NP) → (PP).',
    detail: 'A verb phrase is headed by a verb (VB, VBZ, VBD, VBG, VBN, VBP, MD) and carries the clause predicate: it says what the subject does or is. Auxiliaries and modals come first, then the main verb, followed by its complements - a direct-object noun phrase (NP) or a prepositional phrase (PP). Recognize a VP because it contains the finite verb together with everything that belongs with it, and it agrees with the subject ("the dog chased the ball").',
    steps: [
      'Identify the verb leaves: any auxiliary or modal, the main verb, and the object or complement that follows.',
      'Right-click the canvas and add the VP box; drag its connector dot onto the verb word(s) in reading order.',
      'If there is a direct object, add an NP box, connect it to the VP after the verb, and attach its determiner and noun underneath.',
      'If a prepositional phrase follows the verb, add a PP box and connect the preposition and its noun-phrase object beneath it.',
      'Check that the VP leaves match the example - the canvas checks the tree automatically.',
    ],
    examples: ['is running', 'has eaten the cake'],
  },
  {
    type: 'PP', title: 'Prepositional phrase', group: 'Phrases',
    rule: 'A prepositional phrase is a preposition followed by a noun phrase: IN → NP.',
    detail: 'A prepositional phrase is headed by a preposition (IN) and always takes a noun-phrase object (NP). It usually expresses place, time, manner, or possession ("in the garden", "of physics") and attaches to the word it modifies - a noun, verb, or adjective. The preposition is the head and comes first; everything after it forms the object NP. Recognize it by the leading preposition: a phrase that begins with in, on, of, to, or with is almost certainly a PP with the pattern IN → NP.',
    steps: [
      'Identify the preposition (IN) and the noun-phrase object that follows it (determiner + noun, or a pronoun).',
      'Right-click the canvas and add the PP box; drag its connector dot onto the preposition.',
      'Add an NP box for the object and connect it to the PP after the preposition; attach the object determiner and noun beneath the NP.',
      'Check that the PP leaves read like the example phrase - the canvas checks the tree automatically.',
    ],
    examples: ['in the garden', 'of physics', 'on the small table'],
  },
  {
    type: 'QP', title: 'Quantifier phrase', group: 'Phrases',
    rule: 'A quantifier phrase expresses an amount, often with a comparative and "than": (JJR) → (IN) → CD.',
    detail: 'A quantifier phrase expresses an amount or quantity. Its head is a cardinal number (CD), often modified by a comparative (JJR, e.g. "more") and linked by a comparative preposition (IN, e.g. "than"). Quantifier phrases sit inside noun phrases ("more than five people") or act as measure expressions in their own right. Recognize one when the phrase answers "how many?" or "how much?" and ends in a number.',
    steps: [
      'Pick out the quantity leaves: the comparative (JJR) if there is one, the linking word than (IN), and the cardinal number (CD) head.',
      'Right-click the canvas and add the QP box; drag its connector dot onto each leaf in reading order - comparative, than, number.',
      'If the phrase has no comparative, connect the QP straight to the number.',
      'Check that the quantifier leaves match the example - the canvas checks the tree automatically.',
    ],
    examples: ['More than five people came.'],
  },
  {
    type: 'S', title: 'Clause (sentence)', group: 'Clauses',
    rule: 'A clause joins a subject noun phrase to a predicate verb phrase: NP → VP. This is the top of a normal sentence.',
    detail: 'A clause (S) is the complete sentence-level unit: it pairs a subject noun phrase with a predicate verb phrase (NP → VP), optionally with an adverb or prepositional phrase on the edge. The subject is what the sentence is about; the VP says something about it, and the verb inside the VP determines which complements are needed. Recognize a full clause by that subject-predicate pairing - unlike a fragment, it can stand alone as a grammatical sentence.',
    steps: [
      'Split the sentence into its two biggest pieces: the subject NP (who or what the sentence is about) and the predicate VP (what is said about it).',
      'Right-click the canvas and add the S box first; drag its connector dot onto the subject NP and the predicate VP.',
      'Build the subject NP beneath: determiner, any adjectives, then the noun head.',
      'Build the predicate VP: auxiliary or modal, the main verb, then any object NP or PP beneath it.',
      'Check that the S spans every word of the sentence - the canvas checks the tree automatically.',
    ],
    examples: ['The cat sat.', 'The dog chased the ball.', 'Birds sing.'],
  },
  {
    type: 'SQ', title: 'Yes/no question', group: 'Clauses',
    rule: 'A yes/no question inverts the auxiliary and the subject: AUX → NP → VP.',
    detail: 'A yes/no question (SQ) is a clause whose auxiliary has moved in front of the subject ("Is it raining?", "Did she leave?"). It expects a yes or no answer, so no wh-phrase is involved; the pattern is AUX → NP → VP with the auxiliary or modal at the very front and the subject directly after it. Recognize one by that inverted order - verb before subject - usually ending in a question mark.',
    steps: [
      'Find the fronted auxiliary or modal and the subject NP that follows it.',
      'Right-click the canvas and add the SQ box; drag its connector dot onto the auxiliary first, then the subject NP.',
      'Add the VP for the predicate and connect it to the SQ after the subject; attach the main verb and its complements beneath.',
      'Check that the leaves read exactly like the question - the canvas checks the tree automatically.',
    ],
    examples: ['Is it raining?', 'Did she leave?', 'Can you swim?'],
  },
  {
    type: 'SBARQ', title: 'Wh-question', group: 'Clauses',
    rule: 'A wh-question puts a wh-phrase first, then inverts the auxiliary with the subject: WH-phrase → AUX → NP.',
    detail: 'A wh-question (SBARQ) begins with a wh-phrase - a wh-noun phrase (WHNP), wh-adjective phrase, wh-adverb phrase (WHADVP), or wh-prepositional phrase (WHPP) - followed by an inverted clause (SQ) whose auxiliary has moved past the subject. Wh-questions ask for missing information ("What did you say?"), and the wh-word is normally the first word. Recognize one by the fronted wh-word plus subject-auxiliary inversion, with a question mark at the end.',
    steps: [
      'Identify the wh-phrase at the front (what/which → WHNP, where/how → WHADVP, whom → WHPP) and the inverted clause that follows.',
      'Right-click the canvas and add the SBARQ box; connect it to the wh-phrase first.',
      'Build the wh-phrase subtree beneath its own box (wh-word and noun, if present).',
      'Right-click again and add the SQ box for the inverted clause; connect the auxiliary, the subject NP, and the VP under it.',
      'Check that the leaves match the question - the canvas checks the tree automatically.',
    ],
    examples: ['What did you say?', 'Who ate the cake?', 'Where is the cat?'],
  },
  {
    type: 'SBAR', title: 'Subordinate clause', group: 'Clauses',
    rule: 'A subordinate clause is introduced by a complementizer (or a relative pronoun) followed by a clause: IN → S.',
    detail: 'A subordinate clause (SBAR) is a clause introduced by a complementizer or relative pronoun (IN/WDT/WP, e.g. "because", "that", "which") with a full clause beneath it. It does not stand alone; it fills a role inside a larger sentence - the complement of a verb ("I think that she knows") or a modifier of a noun ("the book which I saw"). Recognize it by the leading subordinator followed by its own subject-predicate clause.',
    steps: [
      'Find the introducing complementizer or relative word and the clause (S) that follows it.',
      'Right-click the canvas and add the SBAR box; connect it to the introducer first.',
      'Add an S box beneath for the embedded clause and build its subject NP and predicate VP.',
      'Check that the SBAR leaves match the example phrase - the canvas checks the tree automatically.',
    ],
    examples: ['because he left', 'that she knows', 'which I saw'],
  },
  {
    type: 'SINV', title: 'Inverted clause', group: 'Clauses',
    rule: 'An inverted clause fronts a negative or restrictive phrase and inverts the auxiliary with the subject: ADVP → AUX → NP.',
    detail: 'An inverted declarative clause (SINV) fronts a negative or restrictive phrase ("never", "rarely", "only then") and then inverts the auxiliary with the subject ("Never have I seen such a thing."). It is a stylistic declarative, not a question, so no wh-word is involved; the giveaway is the adverb or prepositional phrase before the inverted auxiliary. The pattern is ADVP/PP → AUX → NP → VP.',
    steps: [
      'Spot the fronted negative or restrictive phrase and the inverted auxiliary after it.',
      'Right-click the canvas and add the SINV box; connect the fronted phrase first, then the auxiliary.',
      'Add the subject NP and the predicate VP, and connect both beneath, building their own subtrees.',
      'Check that the leaves match the example sentence - the canvas checks the tree automatically.',
    ],
    examples: ['Never have I seen such a thing.', 'Rarely does he complain.'],
  },
  {
    type: 'WHNP', title: 'Wh-noun phrase', group: 'Wh-phrases',
    rule: 'A wh-noun phrase begins with a wh-determiner or wh-pronoun and then the noun that belongs to it: WDT → N.',
    detail: 'A wh-noun phrase (WHNP) is a noun phrase built on a wh-word: a wh-determiner (WDT, "which/what") or wh-pronoun (WP, "who/whom") plus the noun it determines. It names the unknown person or thing a question asks about ("which book", "what color") and usually serves as the fronted phrase of a wh-question or the object of a preposition. Recognize it by the wh-word at its left edge directly followed by (or standing in for) a noun.',
    steps: [
      'Find the wh-word (WDT/WP) and the noun it belongs with.',
      'Right-click the canvas and add the WHNP box; drag its connector dot onto the wh-word and the noun in reading order.',
      'If the wh-pronoun stands alone, connect the WHNP directly to it.',
      'Check that the leaves match the example phrase - the canvas checks the tree automatically.',
    ],
    examples: ['which book', 'what color'],
  },
  {
    type: 'WHADJP', title: 'Wh-adjective phrase', group: 'Wh-phrases',
    rule: 'A wh-adjective phrase asks "how …?" about an adjective: how → ADJ.',
    detail: 'A wh-adjective phrase (WHADJP) asks "how ...?" about a quality and is headed by how plus an adjective ("how old", "how tall"). It typically fronts a question or appears as the complement of a linking verb. Recognize it by the fixed opening word how immediately followed by an adjective.',
    steps: [
      'Identify the pair: how plus an adjective (JJ).',
      'Right-click the canvas and add the WHADJP box; drag its connector dot onto how first, then the adjective.',
      'Check that the two leaves read in sentence order - the canvas checks the tree automatically.',
    ],
    examples: ['how old'],
  },
  {
    type: 'WHADVP', title: 'Wh-adverb phrase', group: 'Wh-phrases',
    rule: 'A wh-adverb phrase is a single wh-adverb standing in for when/where/how/why: WRB.',
    detail: 'A wh-adverb phrase (WHADVP) is a single wh-adverb (WRB) - where, when, how, or why - standing as a whole phrase. It asks for a place, time, manner, or reason, and either fronts a question ("Where is the cat?") or introduces a subordinate clause ("the town where I grew up"). Recognize it because the phrase is exactly one interrogative adverb.',
    steps: [
      'Find the single wh-adverb (WRB).',
      'Right-click the canvas and add the WHADVP box; drag its connector dot straight onto the adverb.',
      'Check that the leaf matches the example - the canvas checks the tree automatically.',
    ],
    examples: ['where', 'when', 'how'],
  },
  {
    type: 'WHPP', title: 'Wh-prepositional phrase', group: 'Wh-phrases',
    rule: 'A wh-prepositional phrase is a preposition with a wh-noun phrase: IN → WHNP.',
    detail: 'A wh-prepositional phrase (WHPP) is a prepositional phrase whose object is a wh-noun phrase: a preposition (IN) followed by WHNP ("to whom", "for what"). It questions the object of a preposition and is often fronted in a question. Recognize it by the preposition in first position and a wh-word in the object slot.',
    steps: [
      'Identify the preposition (IN) and the wh-object that follows (wh-word plus noun, if any).',
      'Right-click the canvas and add the WHPP box; connect the preposition first.',
      'Add the WHNP box and connect it after the preposition; attach the wh-word and noun beneath it.',
      'Check that the leaves match the example phrase - the canvas checks the tree automatically.',
    ],
    examples: ['to whom', 'for what'],
  },
  {
    type: 'CONJP', title: 'Conjunction phrase', group: 'Special phrases',
    rule: 'A conjunction phrase links two items using a multi-word conjunction: CC → X.',
    detail: 'A conjunction phrase (CONJP) links two parallel items with a multi-word conjunction - "as well as", "not to mention", "let alone". Its head is the conjunction (CC/IN), and whatever follows it forms the second half of the link; the first half sits outside the CONJP as a sibling. Recognize it by a multi-word connective joining two otherwise complete units of the same kind.',
    steps: [
      'Find the multi-word conjunction that links the two items.',
      'Right-click the canvas and add the CONJP box; drag its connector dot onto the connector words in order.',
      'If a word follows the conjunction as part of the link, give it its own box (e.g. a PP) and connect it to the CONJP.',
      'Check that the CONJP leaves match the example - the canvas checks the tree automatically.',
    ],
    examples: ['as well as'],
  },
  {
    type: 'UCP', title: 'Unlike-coordinated phrase', group: 'Special phrases',
    rule: 'An unlike-coordinated phrase coordinates two items of different categories: X → CC → Y.',
    detail: 'An unlike-coordinated phrase (UCP) coordinates two expressions of different grammatical categories - for example a noun phrase with an adjective phrase, or a clause with an adverb - joined by a coordinating conjunction (CC). Its head is the conjunction, and unlike ordinary coordination it does not require both conjuncts to match in category. Recognize it when "X and Y" combines items that play the same role but have different phrase types.',
    steps: [
      'Identify the two unlike conjuncts and the coordinating conjunction (CC) between them.',
      'Right-click the canvas and add the UCP box first.',
      'Connect the left conjunct, the conjunction, and the right conjunct to the UCP in reading order, building each conjunct subtree.',
      'Check that the leaves match the example - the canvas checks the tree automatically.',
    ],
    examples: ['first, second'],
  },
  {
    type: 'PRT', title: 'Particle', group: 'Special phrases',
    rule: 'A particle is a small adverb-like word that completes a phrasal verb. It hangs directly off the verb phrase: VB → PRT.',
    detail: 'A particle (PRT) is a small adverb-like word (RP) that belongs to a phrasal verb - away, up, off, out, down. It hangs directly off the verb phrase (VB → PRT) and changes the verb meaning ("throw away", "give up"). Unlike a preposition, a particle takes no object of its own, so it can appear before or after the object NP. Recognize it because it completes the verb rather than introducing a phrase.',
    steps: [
      'Find the phrasal verb and the particle (RP) that completes it.',
      'Right-click the canvas and add the PRT box; drag its connector dot onto the particle word.',
      'Build the VP (or S) around it: connect the VP to the verb and the PRT, plus any object NP.',
      'Check that the leaves reflect the sentence order - the canvas checks the tree automatically.',
    ],
    examples: ['Throw it away.', 'Give up the fight.'],
  },
  {
    type: 'FRAG', title: 'Fragment', group: 'Special phrases',
    rule: 'A fragment is a phrase standing alone as an utterance, without a subject and predicate.',
    detail: 'A fragment (FRAG) is a phrase used as a standalone utterance without a subject-predicate core - greetings, headlines, labels, answers ("Hello there."). It is headed by whatever word gives it its content (a noun, interjection, or adverb), and the parser marks it FRAG when no full clause can be built. Recognize it by the absence of a verb with a subject: the utterance works in context but not as a grammatical sentence.',
    steps: [
      'Identify the words of the utterance and what kind of phrase they form (NP, INTJ, ADVP ...).',
      'Right-click the canvas and add the FRAG box for the utterance as a whole.',
      'Build the inner phrase beneath it - for "Hello there." connect the FRAG to the interjection and its word.',
      'Check that the leaves match the example - the canvas checks the tree automatically.',
    ],
    examples: ['Hello there.'],
  },
  {
    type: 'INTJ', title: 'Interjection', group: 'Special phrases',
    rule: 'An interjection is a word that expresses emotion on its own: Wow! Hey!',
    detail: 'An interjection (INTJ) is a single emotive word - wow, hey, oh, alas - that expresses a reaction on its own. It stands outside the subject-predicate structure (it is not the head of any longer phrase) and adds affect rather than propositional meaning to the utterance. Recognize it by the exclamation word plus punctuation; nothing is attached beneath it.',
    steps: [
      'Find the single interjection word and its punctuation.',
      'Right-click the canvas and add the INTJ box above it.',
      'Drag the INTJ connector dot onto the interjection word.',
      'Check that the leaf matches the example - the canvas checks the tree automatically.',
    ],
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

// `view` may be 'quiz' (start a quiz now), 'lessons' (open the lesson-picker
// overlay), or 'leaderboard'/'achievements' (not built yet — show a placeholder).
export function openQuizView(view = 'quiz') {
  if (view === 'leaderboard' || view === 'achievements') {
    return showPlaceholder(view);
  }
  if (view === 'lessons') {
    openLessonsOverlay();
    return;
  }
  // 'quiz' (or default): start immediately — the learner doesn't pick a
  // sentence, the quiz serves them in order. A lesson opened in the right
  // panel must not bleed into a standalone quiz.
  clearActiveLesson();
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

export function closeQuizView() {
  closeLessonsOverlay();
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
  ensurePanelTabs();
}

// ---------------------------------------------------------------------------
// Right panel: lesson/quiz card vs. read-analysis panes
// ---------------------------------------------------------------------------
let panelTabsWired = false;

// Bookmark tab that flips the right panel between the lesson card and the
// read-analysis inspector while a lesson (or its quiz) is active.
function ensurePanelTabs() {
  if (panelTabsWired) return;
  panelTabsWired = true;
  $('#rightPanelBookmark')?.addEventListener('click', () => {
    const panel = $('.right-panel');
    if (!panel || !panel.classList.contains('lesson-on')) return;
    setRightPane(panel.classList.contains('read-on') ? 'lesson' : 'read');
  });
}

// `pane` is 'lesson' (full-height lesson/quiz card), 'read' (full-height read
// analysis), or null for standard SynTutor mode (analysis visible by default).
function setRightPane(pane) {
  const panel = $('.right-panel');
  const active = pane === 'lesson' || pane === 'read';
  if (panel) {
    panel.classList.toggle('lesson-on', active);
    panel.classList.toggle('read-on', pane === 'read');
  }
  const tabs = $('#rightPanelTabs');
  if (tabs) tabs.hidden = !active;
  const label = $('#rightPanelBookmarkLabel');
  if (label) label.textContent = pane === 'read' ? (state.session ? 'Quiz' : 'Lesson') : 'Read analysis';
  const btn = $('#rightPanelBookmark');
  if (btn) {
    btn.setAttribute('aria-pressed', String(pane === 'read'));
    btn.title = pane === 'read' ? 'Back to the lesson card' : 'Show the read analysis panel';
  }
}

// ---------------------------------------------------------------------------
// Lessons overlay: a frosted-glass module picker over the whole workspace
// ---------------------------------------------------------------------------
let lessonsOverlayWired = false;

function ensureLessonsOverlay() {
  if (lessonsOverlayWired) return;
  const overlay = $('#lessonsOverlay');
  if (!overlay) return;
  lessonsOverlayWired = true;
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) closeLessonsOverlay();
  });
  $('#lessonsCloseBtn', overlay)?.addEventListener('click', closeLessonsOverlay);
  $('#lessonsFreeBuilder', overlay)?.addEventListener('click', () => {
    closeLessonsOverlay();
    clearActiveLesson();
    closeQuizView();
    openBuilderView();
  });
}

// Esc closes the picker, but only after an open sidebar drawer has had its
// turn — the drawer sits above the overlay.
function onLessonsOverlayKeydown(e) {
  if (e.key !== 'Escape') return;
  if ($('#appSidebarBackdrop')?.classList.contains('active')) return;
  closeLessonsOverlay();
}

// Open the transparent lesson picker: dismiss the sidebar drawer, refresh the
// per-lesson progress grid, and mark the Lessons tab as current.
function openLessonsOverlay() {
  ensureLessonsOverlay();
  closeStepGuide();
  closeQuizView();
  $('#appSidebarBackdrop')?.classList.remove('active');
  $('#sidebarToggleBtn')?.setAttribute('aria-expanded', 'false');
  document.querySelectorAll('.sidebar-item').forEach((b) => {
    b.classList.toggle('active', b.dataset.view === 'lessons');
  });
  renderLessons();
  const overlay = $('#lessonsOverlay');
  if (!overlay) return;
  document.body.classList.add('lessons-overlay-open');
  overlay.classList.add('open');
  document.addEventListener('keydown', onLessonsOverlayKeydown);
  $('#lessonsCloseBtn', overlay)?.focus({ preventScroll: true });
}

function closeLessonsOverlay() {
  document.removeEventListener('keydown', onLessonsOverlayKeydown);
  document.body.classList.remove('lessons-overlay-open');
  $('#lessonsOverlay')?.classList.remove('open');
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

// ---------------------------------------------------------------------------
// Lessons: the module grid in the frosted overlay
// ---------------------------------------------------------------------------
function lessonProgress(lesson) {
  const done = lesson.examples.filter((e) => state.done.has(`${lesson.type}:${e}`)).length;
  const total = lesson.examples.length;
  return { done, total, pct: total ? Math.round((done / total) * 100) : 0 };
}

function renderLessonsSummary() {
  const summary = $('#lessonsSummary');
  if (!summary) return;
  let doneLessons = 0;
  let doneExamples = 0;
  let totalExamples = 0;
  for (const lesson of LESSONS) {
    const { done, total } = lessonProgress(lesson);
    doneExamples += done;
    totalExamples += total;
    if (done === total) doneLessons += 1;
  }
  summary.textContent =
    `${doneLessons} of ${LESSONS.length} lessons completed · ${doneExamples} of ${totalExamples} examples built`;
}

// The lessons split into their categories (Phrases, Clauses, Wh-phrases,
// Special phrases) — each small enough to show as one non-scrolling page.
function lessonsGroups() {
  const groups = [];
  for (const lesson of LESSONS) {
    let group = groups.find((g) => g.name === lesson.group);
    if (!group) {
      group = { name: lesson.group, lessons: [] };
      groups.push(group);
    }
    group.lessons.push(lesson);
  }
  return groups;
}

// One minimal module card: tag pill, title, and a thin progress line.
function lessonCard(lesson) {
  const { done, total, pct } = lessonProgress(lesson);
  const complete = done === total;
  const card = el('button', complete ? 'lesson-card is-complete' : 'lesson-card');
  card.type = 'button';
  card.title = `${lesson.title} — ${done}/${total} completed`;

  card.appendChild(el('span', 'lesson-badge', lesson.type));
  card.appendChild(el('span', 'lesson-card-title', lesson.title));
  card.appendChild(el('span', 'lesson-card-overview', lesson.rule));
  card.appendChild(el('span', 'lesson-card-count', complete ? `✓ ${done}/${total}` : `${done}/${total}`));

  const bar = el('span', 'lesson-bar');
  const fill = el('span', 'lesson-bar-fill');
  fill.style.width = `${pct}%`;
  bar.appendChild(fill);
  card.appendChild(bar);

  card.addEventListener('click', () => openLesson(lesson));
  return card;
}

// The catalog shows one category page at a time; the tabs switch pages and
// nothing ever scrolls.
function renderLessons() {
  ensureLessonsOverlay();
  renderLessonsSummary();
  const groups = lessonsGroups();
  state.lessonsTab = Math.max(0, Math.min(state.lessonsTab || 0, groups.length - 1));

  const tabs = $('#lessonsTabs');
  if (tabs) {
    tabs.innerHTML = '';
    groups.forEach((group, i) => {
      const tab = el('button', i === state.lessonsTab ? 'lessons-tab is-active' : 'lessons-tab', group.name);
      tab.type = 'button';
      tab.setAttribute('aria-pressed', String(i === state.lessonsTab));
      tab.addEventListener('click', () => {
        state.lessonsTab = i;
        renderLessons();
      });
      tabs.appendChild(tab);
    });
  }

  const grid = $('#lessonsGrid');
  if (!grid) return;
  grid.innerHTML = '';
  for (const lesson of groups[state.lessonsTab].lessons) {
    grid.appendChild(lessonCard(lesson));
  }
}

// Choosing a card loads the topic into the workspace: the picker fades away,
// the lesson card opens on its Concept page, and the first example opens on
// the builder canvas in place (no sidebar tab switch).
function openLesson(lesson) {
  closeLessonsOverlay();
  // Picking a lesson leaves any quiz session behind — the learner is now in
  // focused practice, not the session's in-order walk (this also re-enables
  // the practice affordance bar; see startChallenge).
  state.session = null;
  const gi = lessonsGroups().findIndex((g) => g.lessons.includes(lesson));
  if (gi >= 0) state.lessonsTab = gi;
  state.lessonPage = 1;
  state.lessonIndex = lesson.type;
  state.view = 'lesson';
  state.exampleIndex = 0;
  setRightPane('lesson');
  showExample(lesson, 0);
}

// ---------------------------------------------------------------------------
// Lesson: one construction + its examples + its quiz
// ---------------------------------------------------------------------------
// The active lesson is a four-page wizard in the right panel — Concept &
// Rule, Step-by-Step Tree Guide, Practice walkthroughs, and the module's
// comprehensive Lesson Quiz — switched by the page pills or the Back / Next
// buttons, so nothing ever scrolls. The quiz lives exclusively on the last
// page, after every step and example has been reviewed.
const LESSON_PAGES = ['Concept', 'Steps', 'Practice', 'Quiz'];

function renderLesson() {
  const lesson = LESSONS.find((l) => l.type === state.lessonIndex);
  if (!lesson) return;
  const host = $('#quizQuestHost');
  if (!host) return;
  ensurePanelTabs();
  const index = Math.max(0, Math.min(state.exampleIndex || 0, lesson.examples.length - 1));
  state.exampleIndex = index;
  state.lessonPage = Math.max(1, Math.min(state.lessonPage || 1, LESSON_PAGES.length));
  const page = state.lessonPage;
  const example = lesson.examples[index];

  // The spotlight guide only belongs on this lesson's Steps page, for the
  // example it was opened on; a page pill, example switch, or new lesson
  // dismisses it. Plain re-renders (a solved example refreshing the check-
  // marks) keep it alive — updateStepGuide() re-syncs the highlight below.
  if (guide.open && (page !== 2 || guide.lesson !== lesson.type || guide.example !== example)) {
    closeStepGuide();
  }

  host.innerHTML = '';
  const wrap = el('div', 'sq-lesson');

  const back = el('button', 'sq-lessons-back', '← All lessons');
  back.type = 'button';
  back.title = 'Show all lesson modules';
  back.addEventListener('click', () => openLessonsOverlay());
  wrap.appendChild(back);
  wrap.appendChild(el('h2', 'sq-title', `${lesson.type} · ${lesson.title}`));

  const pager = el('div', 'sq-pager');
  LESSON_PAGES.forEach((label, i) => {
    const pill = el('button', i + 1 === page ? 'sq-pager-pill is-active' : 'sq-pager-pill', `${i + 1} ${label}`);
    pill.type = 'button';
    pill.setAttribute('aria-pressed', String(i + 1 === page));
    pill.addEventListener('click', () => {
      state.lessonPage = i + 1;
      renderLesson();
    });
    pager.appendChild(pill);
  });
  wrap.appendChild(pager);

  const body = el('div', 'sq-lesson-body');
  if (page === 1) {
    const rule = el('div', 'sq-rule');
    rule.appendChild(el('span', 'sq-rule-tag', lesson.type));
    const ruleBody = el('div', 'sq-rule-body');
    ruleBody.appendChild(el('p', 'sq-rule-text', lesson.rule));
    ruleBody.appendChild(el('p', 'sq-rule-detail', lesson.detail));
    rule.appendChild(ruleBody);
    body.appendChild(rule);
  } else if (page === 2) {
    if (lesson.examples.length > 1) {
      const pills = el('div', 'sq-example-pills');
      lesson.examples.forEach((sentence, i) => {
        let cls = 'sq-example-pill';
        if (i === index) cls += ' is-active';
        else if (state.done.has(`${lesson.type}:${sentence}`)) cls += ' is-done';
        const pill = el('button', cls, String(i + 1));
        pill.type = 'button';
        pill.title = sentence;
        pill.setAttribute('aria-label', `Example ${i + 1}: ${sentence}`);
        pill.addEventListener('click', () => showExample(lesson, i));
        pills.appendChild(pill);
      });
      body.appendChild(pills);
    }
    const steps = el('div', 'sq-steps-box');
    const stepsHead = el('div', 'sq-steps-head');
    stepsHead.appendChild(el('span', 'sq-steps-label', 'Target sentence'));
    stepsHead.appendChild(el('span', 'sq-steps-sentence', example));
    const guideBtn = el('button', 'sq-steps-guide', guide.open ? '■ Stop guide' : '▶ Guide me');
    guideBtn.type = 'button';
    guideBtn.title = 'Point at each step on the canvas, one at a time';
    guideBtn.setAttribute('aria-pressed', String(guide.open));
    guideBtn.addEventListener('click', () => {
      if (guide.open) closeStepGuide();
      else openStepGuide(lesson, 0);
    });
    stepsHead.appendChild(guideBtn);
    steps.appendChild(stepsHead);
    const list = el('ol', 'sq-steps');
    lesson.steps.forEach((step, i) => {
      const li = el('li', guide.open && i === guide.step ? 'is-current' : null, step);
      li.title = 'Show this step on the canvas';
      li.addEventListener('click', () => openStepGuide(lesson, i));
      list.appendChild(li);
    });
    steps.appendChild(list);
    body.appendChild(steps);
  } else if (page === 3) {
    body.appendChild(el('div', 'sq-group', 'Practice walkthroughs'));
    lesson.examples.forEach((sentence, i) => {
      const row = el('button', 'sq-challenge');
      row.type = 'button';
      if (i === index) row.classList.add('is-active');
      const isDone = state.done.has(`${lesson.type}:${sentence}`);
      if (isDone) row.classList.add('is-done');
      row.appendChild(el('span', 'sq-challenge-mark', isDone ? '✓' : '▸'));
      row.appendChild(el('span', 'sq-challenge-sentence', sentence));
      // Pick an example and drop straight into its step-by-step walkthrough.
      row.addEventListener('click', () => {
        state.lessonPage = 2;
        showExample(lesson, i);
      });
      body.appendChild(row);
    });
  } else {
    // Page 4: the module's only quiz, at the very end of the lesson.
    body.appendChild(el('div', 'sq-group', 'Lesson quiz'));
    const summary = el('div', 'sq-quiz-summary');
    summary.appendChild(el('p', null,
      'You have read the concept, walked the build steps, and practiced the examples. '
      + 'The quiz rebuilds every example of this lesson in order — one tree each, checked live '
      + "against SynTutor's parse. Practiced examples are marked ✓."));
    body.appendChild(summary);
    const list = el('ul', 'sq-quiz-list');
    for (const sentence of lesson.examples) {
      const item = el('li', 'sq-quiz-item');
      const done = state.done.has(`${lesson.type}:${sentence}`);
      item.appendChild(el('span', done ? 'sq-quiz-mark is-done' : 'sq-quiz-mark', done ? '✓' : '○'));
      item.appendChild(el('span', 'sq-quiz-sent', sentence));
      list.appendChild(item);
    }
    body.appendChild(list);
  }
  wrap.appendChild(body);

  const nav = el('div', 'sq-lesson-nav');
  const prev = el('button', 'sq-ghost', '← Back');
  prev.type = 'button';
  prev.disabled = page === 1;
  prev.addEventListener('click', () => {
    state.lessonPage = Math.max(1, page - 1);
    renderLesson();
  });
  nav.appendChild(prev);
  if (page < LESSON_PAGES.length) {
    const next = el('button', 'sq-primary', 'Next →');
    next.type = 'button';
    next.addEventListener('click', () => {
      state.lessonPage = page + 1;
      renderLesson();
    });
    nav.appendChild(next);
  } else {
    const quiz = el('button', 'sq-primary', 'Start quiz');
    quiz.type = 'button';
    quiz.addEventListener('click', () => startLessonQuiz(lesson));
    nav.appendChild(quiz);
  }
  wrap.appendChild(nav);

  host.appendChild(wrap);

  // Keep an open spotlight guide in sync with the fresh DOM (the Steps list
  // and the guide button were just re-created).
  if (guide.open) updateStepGuide();
}

// Show one example of the open lesson: sync the top input, re-render the
// lesson panel (so its step-by-step guide matches), then load it on the canvas.
function showExample(lesson, index) {
  const last = lesson.examples.length - 1;
  const i = Math.max(0, Math.min(index, last));
  return startChallenge(lesson, lesson.examples[i]);
}

// The lesson's quiz: build every example of this lesson, in order. It is the
// lesson's final page — the spotlight guide has no place once the quiz starts.
function startLessonQuiz(lesson) {
  closeStepGuide();
  closeQuizView();
  $('#appSidebarBackdrop')?.classList.remove('active');
  startSession(lesson.examples.map((example) => ({ lesson, example })));
}

// ---------------------------------------------------------------------------
// Start an example: show the sentence, load gold, open the builder
// ---------------------------------------------------------------------------
// Show `text` in the top input bar. While locked, the textarea draws its text
// transparently and #inputHighlights overlays it, so the overlay must carry
// the sentence too; the synthetic input event also drops stale tutor spans.
function setInputSentence(text) {
  const input = $('#inputText');
  if (input) {
    input.value = text;
    input.dispatchEvent(new Event('input', { bubbles: true }));
  }
  const highlights = $('#inputHighlights');
  if (highlights) highlights.textContent = text;
}

async function startChallenge(lesson, example, onDone) {
  if (state.view === 'lesson') {
    const i = lesson.examples.indexOf(example);
    if (i >= 0) state.exampleIndex = i;
  }
  setInputSentence(example);
  refreshLessonPanel();

  closeQuizView();
  $('#appSidebarBackdrop')?.classList.remove('active');

  // Lessons and quizzes build in place: keep the sidebar highlight on the tab
  // the learner came from instead of switching to Syntax Builder.
  const sidebarView = state.view === 'lesson' ? 'lessons' : 'quiz';
  // Lesson practice (not the end-of-module quiz) keeps the affordance bar up
  // so learners can see they may connect boxes by hand on the canvas.
  const practice = state.view === 'lesson' && !state.session;
  let gold = state.cache.get(example);
  let reset = true;
  if (!gold) {
    openBuilderView({
      challenge: { kind: 'full', target: example, hint: lesson.rule, gold: [], goldTree: null },
      reset,
      sidebarView,
      practice,
    });
    reset = false;
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
    reset,
    sidebarView,
    practice,
    onComplete: (ok) => {
      record(lesson, example, ok);
      refreshLessonPanel();
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

// Clear the lesson view rendered in the right panel (#quizQuestHost) and
// return the panel to standard SynTutor mode. Called when leaving lesson mode:
// new session, standalone Syntax Builder, standalone quiz, or builder close.
export function clearActiveLesson() {
  closeStepGuide();
  closeLessonsOverlay();
  state.view = 'lessons';
  state.lessonIndex = null;
  state.exampleIndex = 0;
  state.lessonPage = 1;
  const host = $('#quizQuestHost');
  if (host) host.innerHTML = '';
  setRightPane(null);
}

// Re-render the active lesson panel so `state.done` checkmarks stay current
// as examples are solved.
function refreshLessonPanel() {
  if (state.view === 'lesson') renderLesson();
}

// ---------------------------------------------------------------------------
// Interactive step guide — a spotlight that points at what each step means
// ---------------------------------------------------------------------------
// Opened from the Steps page ("▶ Guide me", or any step row). A fixed ring
// highlights the canvas region, word row, phrase box, or connector dot the
// current step talks about, with a tooltip card carrying the step text and
// Prev / Next controls. The layer is pointer-events: none (only the card is
// interactive), so the learner can still right-click, drag, and re-route on
// the canvas while following along. A rAF loop keeps the ring glued to its
// target while the canvas pans, zooms, or the boxes move.
const guide = { open: false, step: 0, lesson: null, example: null, raf: 0 };

function ensureStepGuideDom() {
  if ($('#stepGuide')) return;
  const wrap = el('div', 'step-guide');
  wrap.id = 'stepGuide';
  wrap.hidden = true;
  wrap.innerHTML =
    '<div class="step-guide-ring" aria-hidden="true"></div>'
    + '<div class="step-guide-card" role="dialog" aria-label="Step-by-step guide">'
    + '<div class="step-guide-top"><span class="step-guide-kicker"></span>'
    + '<button type="button" class="step-guide-close" aria-label="Close guide">×</button></div>'
    + '<p class="step-guide-text"></p>'
    + '<div class="step-guide-nav">'
    + '<button type="button" class="sq-ghost step-guide-prev">← Previous</button>'
    + '<button type="button" class="sq-primary step-guide-next">Next →</button>'
    + '</div></div>';
  document.body.appendChild(wrap);
  wrap.querySelector('.step-guide-close').addEventListener('click', closeStepGuide);
  wrap.querySelector('.step-guide-prev').addEventListener('click', () => stepGuideMove(-1));
  wrap.querySelector('.step-guide-next').addEventListener('click', () => {
    // On the last step the primary button finishes the guide.
    const lesson = LESSONS.find((l) => l.type === guide.lesson);
    if (lesson && guide.step >= lesson.steps.length - 1) closeStepGuide();
    else stepGuideMove(1);
  });
}

function openStepGuide(lesson, step = 0) {
  ensureStepGuideDom();
  guide.open = true;
  guide.lesson = lesson.type;
  guide.example = lesson.examples[state.exampleIndex] ?? lesson.examples[0];
  guide.step = Math.max(0, Math.min(step, lesson.steps.length - 1));
  $('#stepGuide').hidden = false;
  document.addEventListener('keydown', onStepGuideKeydown);
  updateStepGuide();
  if (!guide.raf) guide.raf = requestAnimationFrame(guideLoopFrame);
}

function closeStepGuide() {
  if (!guide.open) return;
  guide.open = false;
  if (guide.raf) cancelAnimationFrame(guide.raf);
  guide.raf = 0;
  const wrap = $('#stepGuide');
  if (wrap) wrap.hidden = true;
  document.removeEventListener('keydown', onStepGuideKeydown);
  document.querySelectorAll('.sq-steps li.is-current').forEach((li) => li.classList.remove('is-current'));
  const btn = $('.sq-steps-guide');
  if (btn) {
    btn.textContent = '▶ Guide me';
    btn.setAttribute('aria-pressed', 'false');
  }
}

function stepGuideMove(d) {
  const lesson = LESSONS.find((l) => l.type === guide.lesson);
  if (!lesson) return closeStepGuide();
  guide.step = Math.max(0, Math.min(guide.step + d, lesson.steps.length - 1));
  updateStepGuide();
}

function onStepGuideKeydown(e) {
  if (e.key === 'Escape') {
    // The lessons overlay and the sidebar backdrop own their own Escape.
    if ($('#lessonsOverlay')?.classList.contains('open')) return;
    if ($('#appSidebarBackdrop')?.classList.contains('active')) return;
    closeStepGuide();
    return;
  }
  if (e.key === 'ArrowRight') stepGuideMove(1);
  else if (e.key === 'ArrowLeft') stepGuideMove(-1);
}

// Push the guide state into the tooltip card and the Steps list.
function updateStepGuide() {
  const lesson = LESSONS.find((l) => l.type === guide.lesson);
  if (!lesson) return closeStepGuide();
  const wrap = $('#stepGuide');
  if (!wrap) return;
  const last = lesson.steps.length - 1;
  wrap.querySelector('.step-guide-kicker').textContent =
    `Step ${guide.step + 1} of ${lesson.steps.length} · ${lesson.type}`;
  wrap.querySelector('.step-guide-text').textContent = lesson.steps[guide.step];
  wrap.querySelector('.step-guide-prev').disabled = guide.step === 0;
  wrap.querySelector('.step-guide-next').textContent = guide.step === last ? 'Done ✓' : 'Next →';
  // Highlight the matching row in the Steps list + flip the launch button.
  document.querySelectorAll('.sq-steps li').forEach((li, i) => {
    li.classList.toggle('is-current', i === guide.step);
  });
  const btn = $('.sq-steps-guide');
  if (btn) {
    btn.textContent = '■ Stop guide';
    btn.setAttribute('aria-pressed', 'true');
  }
}

// One frame of the spotlight: resolve the step's target, park the ring on it,
// seat the card beside it (clamped to the viewport), and schedule the next
// frame. No CSS transitions on position — the rAF loop is the interpolation.
function guideLoopFrame() {
  guide.raf = 0;
  if (!guide.open) return;
  const lesson = LESSONS.find((l) => l.type === guide.lesson);
  const wrap = $('#stepGuide');
  if (!lesson || !wrap) return closeStepGuide();
  const box = canvasGuideBox(guideTargetFor(lesson.steps[guide.step] || ''))
    || canvasGuideBox({ kind: 'canvas' });
  const ring = wrap.querySelector('.step-guide-ring');
  const card = wrap.querySelector('.step-guide-card');
  if (box) {
    ring.style.display = '';
    ring.style.left = `${Math.round(box.left - 6)}px`;
    ring.style.top = `${Math.round(box.top - 6)}px`;
    ring.style.width = `${Math.round(box.width + 12)}px`;
    ring.style.height = `${Math.round(box.height + 12)}px`;
    // Seat the card to the ring's right, then its left, then clamp inside.
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const cw = card.offsetWidth;
    const ch = card.offsetHeight;
    let left = box.left + box.width + 14;
    if (left + cw > vw - 10) left = box.left - cw - 14;
    if (left < 10) left = Math.max(10, Math.min(box.left, vw - cw - 10));
    const top = Math.max(10, Math.min(box.top, vh - ch - 10));
    card.style.left = `${Math.round(left)}px`;
    card.style.top = `${Math.round(top)}px`;
  } else {
    // No target (canvas hidden): dim nothing, but keep the card reachable.
    ring.style.display = 'none';
    card.style.left = `${Math.round(window.innerWidth - 340)}px`;
    card.style.top = '70px';
  }
  guide.raf = requestAnimationFrame(guideLoopFrame);
}

// Map a step's wording onto the canvas element the spotlight should point at.
// The steps follow a fixed phrasing — "Read/Find the leaves…", "Right-click …
// add an X box", "drag its connector dot…", "Check that …" — so: check/read/
// find steps target the word row; an "add an X box" step targets the empty
// region until X exists, then X (or its connector dot); anything else targets
// the first box it names, falling back to the words. Recomputed every frame,
// so the target tracks whatever the learner has built so far.
function guideTargetFor(step) {
  const model = builderModel();
  const hasPhrase = (type) =>
    Object.values(model.nodes).some((n) => n.kind === NODE.PHRASE && n.type === type);
  if (/^(Check|Read|Find|Identify|Spot|Pick out|Split)\b/i.test(step)) return { kind: 'words' };
  const labels = (step.match(/\b[A-Z]{1,6}\b/g) || []).filter((t) => PHRASE_NODE_TYPES.includes(t));
  const added = step.match(/\badd (?:an?|the) ([A-Z]{1,6}) box/i);
  if (added && labels.includes(added[1]) && !hasPhrase(added[1])) return { kind: 'spot' };
  const existing = labels.find(hasPhrase);
  if (existing) {
    return /\bconnector dot\b|\bconnect\b|\bdrag\b/i.test(step)
      ? { kind: 'dot', type: existing }
      : { kind: 'phrase', type: existing };
  }
  if (/\bleaves\b|\bwords?\b|\btags?\b/i.test(step)) return { kind: 'words' };
  if (labels.length) return { kind: 'spot' };
  return { kind: 'words' };
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

// Whenever the builder closes, drop any active lesson view so a stale lesson
// panel never survives a return to normal SynTutor or a standalone Syntax
// Builder session.
setBuilderCloseHandler(clearActiveLesson);
