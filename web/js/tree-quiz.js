// Syntax-Tree Quiz — a textbook for building syntax trees.
//
// There are no "stages". The lesson list is the inventory of phrase
// constructions SynTutor's parser knows, ordered from simple building blocks
// (noun/adjective/adverb/prepositional/verb phrases) through wh-phrases and
// quantifiers to whole clauses, questions and special phrases. Each lesson
// gives an in-depth explanation, its own practice on the builder canvas, and
// its own quiz. Module-style lessons (like the verb phrase) split their
// content into sections - one per type - that the learner picks between;
// those lessons show read-only model trees with a live sentence breakdown
// instead of a canvas-building practice mode.
//
// Two entry points:
//   * Quiz (sidebar)    — starts a quiz straight away and walks every
//                         construction in order, advancing automatically each
//                         time the learner's tree matches SynTutor's parse.
//   * Lessons (sidebar) — a frosted-glass overlay of module cards with
//                         per-lesson progress: pick a category and a topic,
//                         then move through its Concept → Practice → Quiz
//                         pages; the module's comprehensive quiz appears
//                         exclusively at the very end, on page 3.
//
// Most examples are done *in the Syntax Builder*: the sentence is shown in the
// input box with its words already laid out, the learner builds the phrase
// structure by hand - right-clicking to add phrase boxes and dragging
// connector dots to connect them, re-route, or delete - and the tree is
// checked against SynTutor's own parse - fetched live from /api/parse, so the
// gold tree can never drift from the model. Lessons with numbered build steps
// can hand the learner an interactive spotlight guide that points at the exact
// canvas region, word row, or box each step talks about. Module lessons are
// the exception: their canvas is a read-only model tree, and selecting a sample
// sentence updates both that tree and the breakdown beside it.
//
// Exports the surface main.js imports:
//   openQuizView, closeQuizView, isQuizOpen, initQuiz, quizInputHint,
//   clearActiveLesson

import { openBuilderView, closeBuilderView, setBuilderCloseHandler, builderModel, canvasGuideBox, setCanvasHint, setHintBelowActions, setCheckResultHandler, setModelChangeHandler, checkBuilderTree } from './syntax-builder-ui.js';
import { leavesWithTags, childrenOf, NODE, PHRASE_NODE_TYPES } from './syntax-builder.js';
import { isGuestSession, subscribeAuthState, openAuthModal, recordGuestProgress } from './auth.js';
import { XP_PER_CORRECT } from './level.js';

const $ = (sel, root = document) => root.querySelector(sel);

const state = {
  view: 'lessons',    // lessons | lesson
  lessonIndex: null,
  exampleIndex: 0,    // active example inside the open lesson
  lessonPage: 1,      // lesson node: 1 concept | 2 practice | 3 quiz
  sectionIndex: 0,    // active section inside a module-style lesson
  activeGroup: 'All', // active category filter in the lessons catalog
  openModule: null,   // lesson.type whose sub-topics are expanded in the catalog
  controller: null,
  cache: new Map(),   // sentence -> gold
  pendingGold: new Map(), // sentence -> in-flight /api/parse promise
  done: new Set(),    // `${type}:${example}`
  goldLoading: null,    // sentence whose tree is being fetched
  goldError: null,      // message when the model tree could not be loaded
  visitedPages: new Set(), // `${type}:${page}` seen at least once
  quizDone: new Set(),     // lesson.type whose end-of-lesson quiz was finished
  session: null,      // { seq: [{lesson, example}], pos, quizLesson }
  // The examples whose walk-through the learner already saw: revisiting one
  // keeps the canvas clean instead of re-opening the tutorial overlay.
  seenExamples: new Set(),
  // The last live validation message from the builder (quiz stage).
  checkStatus: null,
};

// The textbook, in order. `type` is the official parser label; `rule` is the
// one-line "how to build it" summary used as the in-canvas hint; `detail` is
// the in-depth explanation (role, head, modifiers/complements, recognition);
// `steps` is the numbered guide for assembling the example's tree on canvas.
const LESSONS = [
  {
    type: 'NP', title: 'Noun phrase', group: 'Phrases',
    formula: 'NP → (DT) (JJ)* NN',
    goal: 'Recognise a noun phrase by asking "who or what?" about the clause verb.',
    summary: 'Names a person, thing, or idea. It is built around a noun or pronoun head, with words like determiners and adjectives describing it.',
    rule: 'A noun phrase keeps its modifiers flat around the noun head: determiner or possessive, then any adjectives, then the noun - all direct children of one NP. So "the big cat" is (NP (DT the) (JJ big) (NN cat)).',
    detail: 'A noun phrase names a person, thing, or idea. Its head is a noun (NN, NNS, NNP) or a pronoun (PRP), and the phrase serves as the subject or object of a clause. Determiners (DT), possessives (PRP$) and adjectives (JJ/JJR/JJS) sit in front of the head as plain sister leaves - SynTutor does not wrap them in an adjective box, so "the big cat" is a flat NP over DT + JJ + NN. A prepositional phrase completes the noun from behind, and when it brings its own object the parser nests a small inner NP: "a student of physics" is (NP (NP (DT a) (NN student)) (PP (IN of) (NP (NNS physics)))).',
    steps: [
      'Read the pre-placed leaves and their POS tags: the determiner (DT) or possessive (PRP$), any adjectives (JJ/JJR/JJS), the noun head (NN/NNS), and any prepositional words (IN ...) that follow.',
      'Right-click the canvas and add the NP box; drag its connector dot onto each leaf in reading order - determiner or possessive first, then the adjective(s), then the noun head.',
      'If a prepositional phrase completes the noun, first wrap the head and its determiner in an inner NP box, then add a PP box for the preposition and its object, and connect both boxes under the outer NP.',
      'Check that the NP leaves read left to right exactly like the example phrase - the canvas checks the tree automatically as you connect boxes.',
    ],
    examples: ['the big cat', 'a student of physics', 'my older sister'],
  },
  {
    type: 'ADJP', title: 'Adjective phrase', group: 'Phrases',
    formula: 'ADJP → (RB) JJ (PP)',
    goal: 'Recognise an adjective phrase by asking "what kind?" about a noun.',
    summary: 'Describes a quality or attribute. It is built around an adjective head, often with a degree word in front or a phrase completing it.',
    rule: 'An adjective phrase heads on an adjective: an optional degree adverb in front and an optional PP after it - (RB) + JJ + (PP), all direct children of one ADJP.',
    detail: 'An adjective phrase describes a quality and is headed by an adjective (JJ, JJR, JJS). It works either attributively, inside a noun phrase ("the very happy child"), or predicatively, as the complement of a linking verb ("she is very happy"). A degree adverb (RB) modifies the head from in front and a prepositional phrase (PP) completes it from behind - both attach directly to the ADJP as sister leaves: "very happy" is (ADJP (RB very) (JJ happy)) and "fond of music" is (ADJP (JJ fond) (PP (IN of) (NP (NN music)))).',
    steps: [
      'Find the head adjective (JJ) and everything attached to it: a degree adverb (RB) before the head and/or a prepositional phrase (PP) after it.',
      'Right-click the canvas and add the ADJP box; drag its connector dot onto the degree adverb (if any) and the adjective head, in reading order.',
      'If a prepositional phrase complements the adjective, add a PP box for the preposition and its object, and connect it to the ADJP after the head.',
      'Check that the leaves match the example phrase exactly - the canvas checks the tree automatically.',
    ],
    examples: ['very happy', 'fond of music', 'extremely proud of her'],
  },
  {
    type: 'ADVP', title: 'Adverb phrase', group: 'Phrases',
    formula: 'ADVP → (RB) ADV',
    goal: 'Spot an adverb phrase by asking "how?", "when?" or "where?" about the verb.',
    summary: 'Tells how, when, where, or to what degree. It is built around an adverb head, sometimes with a degree word in front.',
    rule: 'An adverb phrase heads on an adverb, with an optional degree adverb in front: (RB) + ADV, both direct children of one ADVP.',
    detail: 'An adverb phrase tells how, when, where, or to what degree, and its head is the last adverb of the phrase (RB, RBR, RBS). A degree adverb (RB) stands in front of the head as a sister leaf - "very quickly" is (ADVP (RB very) (RB quickly)) - and the pair modifies verbs, adjectives, or other adverbs ("runs very quickly"). Some adverb phrases act as clausal adjuncts ("rarely does he complain").',
    steps: [
      'Spot the adverb head (RB/RBR/RBS) and any degree adverb (RB) that modifies it.',
      'Right-click the canvas and add the ADVP box; drag its connector dot onto the degree adverb first, then the adverb head.',
      'If the adverb has no modifiers, connect the ADVP straight to the single adverb.',
      'Check that the leaves match the example phrase - the canvas checks the tree automatically.',
    ],
    examples: ['very quickly', 'quite well'],
  },
  {
    type: 'VP', title: 'Verb phrase', group: 'Phrases',
    summary: 'The predicate of a sentence: a main verb together with the auxiliary verbs, modifiers, objects, and complements that assist it.',
    rule: 'A verb phrase is a sentence\'s predicate: its main verb plus the words that assist it — auxiliary verbs, modifiers, objects, and complements. Auxiliaries stack into an outer verb phrase around an inner one, as in "has eaten the cake".',
    detail: 'A verb phrase, also known as a predicate, is a group of words composed of a sentence\'s main verb and any words that assist the main verb, including modifiers and auxiliary verbs, objects, and complements. Verb phrases express actions, occurrences, or states of being within a sentence.',
    components: [
      ['Main verb', 'The main verb indicating the primary action or state.'],
      ['Auxiliary (helping) verbs', 'Verbs like be, have, and do that assist the main verb in forming tenses, moods, or voices.'],
      ['Modifiers', 'Adverbs or adverbial phrases or clauses providing additional information about the action.'],
      ['Objects', 'Nouns or pronouns that receive the main action of the verb.'],
      ['Complements', 'Nouns, pronouns, or adjectives that provide more details about the subject or an object.'],
    ],
    sections: [
      {
        name: 'Intransitive',
        title: 'Intransitive verb phrases',
        detail: 'The verb of a verb phrase is intransitive when it does not contain objects or complements, but it can contain auxiliary verbs and/or modifiers.',
        formula: 'VP → V',
        examples: ['The server crashed.', 'The baby is crying.', 'The student studied in the library.'],
        hasObject: false,
      },
      {
        name: 'Linking / Copular',
        title: 'Linking verb phrases',
        detail: 'Linking verb phrases include the subject complements together with any auxiliary verbs and modifiers.',
        formula: 'VP → V + AP or V → NP',
        examples: ['We are ready for the test.', 'He is a researcher.', 'The system remained stable.'],
        hasObject: false,
      },
      {
        name: 'Transitive',
        title: 'Transitive verb phrases',
        detail: 'When the main verb phrase is transitive, the phrase must contain a direct object and may contain modifiers and auxiliary verbs.',
        formula: 'VP → V + NP',
        examples: ['The algorithm parsed the sentence.', 'She evaluated the results.'],
        hasObject: true,
      },
      {
        name: 'Ditransitive',
        title: 'Ditransitive verb phrases',
        detail: 'A ditransitive verb phrase is anchored by a main verb that takes two complements: an indirect object followed by a direct object, or a direct object followed by a prepositional phrase.',
        formula: 'VP → V + NP + NP or V → NP + PP',
        examples: ['The evaluator gave the student explicit feedback.', 'She handed the money to the cashier.'],
        hasObject: true,
      },
      {
        name: 'Complex Transitive',
        title: 'Complex transitive verb phrases',
        detail: 'The transitive verbs in complex transitive verb phrases are followed by both a direct object and an object complement.',
        formula: 'VP → V + NP + AP or V → NP + NP',
        examples: ['They considered the workflow inefficient.', 'They elected him president.'],
        hasObject: true,
      },
    ],
  },
  {
    type: 'PP', title: 'Prepositional phrase', group: 'Phrases',
    formula: 'PP → IN NP',
    goal: 'Recognise a prepositional phrase by its leading preposition.',
    summary: 'Shows a relationship such as place, time, or manner. It is a preposition followed by the noun phrase it relates to.',
    rule: 'A prepositional phrase is a preposition followed by its noun-phrase object: IN → NP. So "in the garden" is (PP (IN in) (NP (DT the) (NN garden))).',
    detail: 'A prepositional phrase is headed by a preposition (IN) and always takes a noun-phrase object (NP). It usually expresses place, time, manner, or possession ("in the garden", "of physics") and attaches to the word it modifies - a noun, verb, or adjective. The preposition is the head and comes first; everything after it forms the object NP, which may be flat ("on the small table" keeps DT + JJ + NN directly under the NP) or a bare noun ("of physics" is an NP over NN alone).',
    steps: [
      'Identify the preposition (IN) and the noun-phrase object that follows it (determiner + adjective(s) + noun, or a pronoun).',
      'Right-click the canvas and add the PP box; drag its connector dot onto the preposition.',
      'Add an NP box for the object and connect it to the PP after the preposition; attach the object words beneath the NP in reading order.',
      'Check that the PP leaves read like the example phrase - the canvas checks the tree automatically.',
    ],
    examples: ['in the garden', 'of physics', 'on the small table'],
  },
  {
    type: 'QP', title: 'Quantifier phrase', group: 'Phrases',
    formula: 'QP → (JJR) (IN) CD',
    goal: 'Recognise a quantifier phrase by the number it heads.',
    summary: 'Expresses an amount or quantity. It is built around a number head, such as "more than five".',
    rule: 'A quantifier phrase expresses an amount around a number head: (JJR) + (IN) + CD, sitting inside a noun phrase - "more than five" is (QP (JJR More) (IN than) (CD five)).',
    detail: 'A quantifier phrase expresses an amount or quantity. Its head is a cardinal number (CD), often modified by a comparative (JJR, e.g. "more") and linked by a comparative preposition (IN, e.g. "than"); all three words hang directly under the QP. Quantifier phrases sit inside noun phrases ("more than five people" puts the QP in front of the noun) or act as measure expressions in their own right.',
    steps: [
      'Pick out the quantity leaves: the comparative (JJR) if there is one, the linking word than (IN), and the cardinal number (CD) head.',
      'Right-click the canvas and add the QP box; drag its connector dot onto each leaf in reading order - comparative, than, number.',
      'Connect the QP inside the noun phrase, directly in front of the noun it quantifies (more than five + people).',
      'Check that the quantifier leaves match the example - the canvas checks the tree automatically.',
    ],
    examples: ['More than five people came.'],
  },
  {
    type: 'S', title: 'Clause (sentence)', group: 'Clauses',
    formula: 'S → NP VP (.?)',
    goal: 'Recognise a clause by its subject–predicate pairing.',
    summary: 'A complete sentence-level unit. It pairs a subject with a predicate and can stand alone as a grammatical sentence.',
    rule: 'A clause pairs a subject noun phrase with a predicate verb phrase under one S box, and keeps the sentence-final punctuation as its last child: NP → VP → (.).',
    detail: 'A clause (S) is the complete sentence-level unit: it pairs a subject noun phrase with a predicate verb phrase (NP → VP), and SynTutor keeps the sentence-final punctuation - (. .) or (. ?) - as a third child of the S. The subject is what the sentence is about; the VP says something about it, and the verb inside the VP determines which complements are needed.',
    steps: [
      'Split the sentence into its three biggest pieces: the subject NP (who or what the sentence is about), the predicate VP, and the final punctuation leaf (. or ?).',
      'Right-click the canvas and add the S box first; drag its connector dot onto the subject NP and the predicate VP in reading order.',
      'Build the subject NP beneath: determiner or possessive, any adjectives, then the noun head.',
      'Build the predicate VP: auxiliary or modal, the main verb, then any object NP or PP beneath it.',
      'Attach the sentence-final punctuation leaf as the last child of the S box - SynTutor keeps it inside the clause.',
      'Check that the S spans every word of the sentence - the canvas checks the tree automatically.',
    ],
    examples: ['The cat sat.', 'The dog chased the ball.', 'Birds sing.'],
  },
  {
    type: 'SQ', title: 'Yes/no question', group: 'Clauses',
    formula: 'SQ → AUX NP VP (.?)',
    goal: 'Recognise a yes/no question by the inverted auxiliary.',
    summary: 'A question that expects a yes or no answer. Its auxiliary verb moves in front of the subject.',
    rule: 'A yes/no question inverts the auxiliary and the subject: fronted AUX, then the subject NP, then the VP - "Is it raining?" is (SQ (VBZ Is) (NP (PRP it)) (VP (VBG raining)) (. ?)).',
    detail: 'A yes/no question (SQ) is a clause whose auxiliary has moved in front of the subject ("Is it raining?", "Did she leave?"). It expects a yes or no answer, so no wh-phrase is involved; the pattern is AUX → NP → VP with the auxiliary or modal at the very front and the subject directly after it, plus the question mark on a standalone question. A copula may carry the whole predicate ("Where is the cat?" leaves SQ with just AUX + NP), and when the subject is the wh-word of a higher question it sits outside ("Who ate the cake?" keeps only the VP inside SQ). Inside a wh-question the same SQ nests under SBARQ and the question mark belongs to the SBARQ instead.',
    steps: [
      'Find the fronted auxiliary or modal and the subject NP that follows it - a wh-word in front fills the subject role, so the SQ may start straight with its VP.',
      'Right-click the canvas and add the SQ box; drag its connector dot onto the auxiliary first, then the subject NP.',
      'Add the VP for the predicate and connect it to the SQ after the subject; attach the main verb and its complements beneath. If the fronted verb carries the whole predicate, add no separate VP.',
      'Check that the leaves read exactly like the question - a standalone yes/no question also keeps the question mark inside the SQ.',
    ],
    examples: ['Is it raining?', 'Did she leave?', 'Can you swim?'],
  },
  {
    type: 'SBARQ', title: 'Wh-question', group: 'Clauses',
    formula: 'SBARQ → WH* SQ (.?)',
    goal: 'Recognise a wh-question by the fronted wh-phrase plus subject–auxiliary inversion.',
    summary: 'A question that asks for missing information. It opens with a wh-word followed by an inverted clause.',
    rule: 'A wh-question stacks three pieces under one SBARQ box: the fronted wh-phrase, an inner SQ with the inverted clause, and the question mark.',
    detail: 'A wh-question (SBARQ) begins with a wh-phrase - a wh-noun phrase (WHNP), wh-adjective phrase, wh-adverb phrase (WHADVP), or wh-prepositional phrase (WHPP) - followed by an inverted clause (SQ) whose auxiliary has moved past the subject, then the question mark as the final child: "What did you say?" is (SBARQ (WHNP (WP What)) (SQ (VBD did) (NP (PRP you)) (VP (VB say))) (. ?)). Wh-questions ask for missing information, the wh-word is normally the first word, and the punctuation sits above the SQ, not inside it.',
    steps: [
      'Identify the wh-phrase at the front (what/which → WHNP, where/how → WHADVP, whom → WHPP) and the inverted clause that follows.',
      'Right-click the canvas and add the SBARQ box; drag its connector dot onto the wh-phrase first.',
      'Build the wh-phrase subtree beneath its own box (wh-word and noun, if present).',
      'Right-click again and add the SQ box for the inverted clause; connect the auxiliary, the subject NP, and the VP under it - whichever of them the question has.',
      'Attach the question mark as the last child of the SBARQ - in a wh-question it sits above the SQ.',
      'Check that the leaves match the question - the canvas checks the tree automatically.',
    ],
    examples: ['What did you say?', 'Who ate the cake?', 'Where is the cat?'],
  },
  {
    type: 'SBAR', title: 'Subordinate clause', group: 'Clauses',
    formula: 'SBAR → (IN|WDT|WP) S',
    goal: 'Recognise a subordinate clause by the complementizer that introduces it.',
    summary: 'A clause introduced by a word like "because" or "that". It cannot stand alone and fills a role inside a larger sentence.',
    rule: 'A subordinate clause is a subordinator plus its own clause under one SBAR box: IN/WDT/WP → S - "because he left" is (SBAR (IN because) (S (NP (PRP he)) (VP (VBD left)))).',
    detail: 'A subordinate clause (SBAR) is a clause introduced by a complementizer or relative pronoun (IN/WDT/WP, e.g. "because", "that", "which") with a full clause (S) beneath it. It does not stand alone; it fills a role inside a larger sentence - the complement of a verb ("I think that she knows") or a modifier of a noun ("the book which I saw" opens its SBAR with a WHNP, as does "which I saw"). The introducer is the first child of the SBAR and the S box follows it.',
    steps: [
      'Find the introducing complementizer or relative word (IN, WDT, WP) and the clause (S) that follows it.',
      'Right-click the canvas and add the SBAR box; connect it to the introducer first.',
      'Add an S box beneath for the embedded clause and build its subject NP and predicate VP.',
      'Check that the SBAR leaves match the example phrase - the canvas checks the tree automatically.',
    ],
    examples: ['because he left', 'that she knows', 'which I saw'],
  },
  {
    type: 'SINV', title: 'Inverted clause', group: 'Clauses',
    formula: 'SINV → ADVP AUX NP VP (.?)',
    goal: 'Recognise an inverted clause by the fronted negative adverb.',
    summary: 'A statement that fronts a negative or restrictive phrase, then puts the auxiliary before the subject, as in "Never have I seen".',
    rule: 'An inverted clause fronts a restrictive phrase, then inverts auxiliary and subject: ADVP → AUX → NP → VP → (.) - the fronted negative or restrictive adverb, then the auxiliary, then the subject NP and the rest of the predicate.',
    detail: 'An inverted declarative clause (SINV) fronts a negative or restrictive phrase ("never", "rarely", "only then") and then inverts the auxiliary with the subject ("Never have I seen such a thing." is (SINV (ADVP (RB Never)) (VBP have) (NP (PRP I)) (VP (VBN seen) (NP (PDT such) (DT a) (NN thing))) (. .))). It is a stylistic declarative, not a question, so no wh-word is involved; the giveaway is the fronted adverb before the inverted auxiliary. Object noun phrases may open with a predeterminer - such a thing is (NP (PDT such) (DT a) (NN thing)) - and the sentence-final punctuation closes the SINV. The pattern is ADVP → AUX → subject NP → VP → punctuation.',
    steps: [
      'Spot the fronted negative or restrictive phrase (an ADVP such as never or rarely) and the inverted auxiliary after it.',
      'Right-click the canvas and add the SINV box; drag its connector dot onto the fronted phrase first, then the auxiliary.',
      'Add the subject NP and the predicate VP, and connect both beneath; inside the object NP watch for a predeterminer (PDT) in front of the determiner.',
      'Attach the sentence-final punctuation leaf as the last child of the SINV box.',
      'Check that the leaves match the example sentence - the canvas checks the tree automatically.',
    ],
    examples: ['Never have I seen such a thing.', 'Rarely does he complain.'],
  },
  {
    type: 'WHNP', title: 'Wh-noun phrase', group: 'Wh-phrases',
    formula: 'WHNP → (WDT|WP) NN',
    goal: 'Recognise a wh-noun phrase by its leading wh-word.',
    summary: 'A phrase that names the unknown person or thing a question asks about, built on a word like "which" or "who".',
    rule: 'A wh-noun phrase begins with a wh-word and carries its noun beside it: WDT/WP (+ N) under one WHNP - "which book" is (WHNP (WDT which) (NN book)).',
    detail: 'A wh-noun phrase (WHNP) is a noun phrase built on a wh-word: a wh-determiner (WDT, "which/what") or wh-pronoun (WP, "who/whom") plus the noun it determines when there is one. It names the unknown person or thing a question asks about ("which book", "what color") and usually serves as the fronted phrase of a wh-question, where it fills the subject role - "Who ate the cake?" then keeps the whole SQ down to its VP - or the object of a preposition. A lone wh-pronoun is a WHNP of its own.',
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
    formula: 'WHADJP → WRB JJ',
    goal: 'Recognise a wh-adjective phrase by "how" plus an adjective.',
    summary: 'A phrase that asks "how …?" about a quality, pairing the word "how" with an adjective, as in "how old".',
    rule: 'A wh-adjective phrase asks "how …?" about an adjective: WRB + ADJ under one WHADJP - "how old" is (WHADJP (WRB how) (JJ old)).',
    detail: 'A wh-adjective phrase (WHADJP) asks "how ...?" about a quality and pairs the adverb how (WRB) with an adjective (JJ) as its two direct children ("how old", "how tall"). It typically fronts a question or appears as the complement of a linking verb.',
    steps: [
      'Identify the pair: how (WRB) plus an adjective (JJ).',
      'Right-click the canvas and add the WHADJP box; drag its connector dot onto how first, then the adjective.',
      'Check that the two leaves read in sentence order - the canvas checks the tree automatically.',
    ],
    examples: ['how old'],
  },
  {
    type: 'WHADVP', title: 'Wh-adverb phrase', group: 'Wh-phrases',
    formula: 'WHADVP → WRB',
    goal: 'Recognise a wh-adverb phrase by its single interrogative adverb.',
    summary: 'A single question word such as "where", "when", "how", or "why" that asks for a place, time, manner, or reason.',
    rule: 'A wh-adverb phrase is a single wh-adverb standing in for when/where/how/why: one WRB leaf under the WHADVP box - "where" is (WHADVP (WRB where)).',
    detail: 'A wh-adverb phrase (WHADVP) is a single wh-adverb (WRB) - where, when, how, or why - standing as a whole phrase, so the box wraps one leaf: (WHADVP (WRB where)). It asks for a place, time, manner, or reason, and either fronts a question ("Where is the cat?") or introduces a subordinate clause ("the town where I grew up").',
    steps: [
      'Find the single wh-adverb (WRB).',
      'Right-click the canvas and add the WHADVP box; drag its connector dot straight onto the adverb.',
      'Check that the leaf matches the example - the canvas checks the tree automatically.',
    ],
    examples: ['where', 'when', 'how'],
  },
  {
    type: 'WHPP', title: 'Wh-prepositional phrase', group: 'Wh-phrases',
    formula: 'WHPP → (IN|TO) WHNP',
    goal: 'Recognise a wh-prepositional phrase by the wh-word in the object slot.',
    summary: 'A preposition paired with a question word, such as "to whom" or "for what", asking about the object of a preposition.',
    rule: 'A wh-prepositional phrase is a preposition with a wh-noun phrase: IN (or TO) → WHNP - "to whom" is (WHPP (TO to) (WHNP (WP whom))).',
    detail: 'A wh-prepositional phrase (WHPP) is a prepositional phrase whose object is a wh-noun phrase: a preposition followed by WHNP ("to whom", "for what"). SynTutor tags the preposition IN, except for the infinitive "to", which stays TO: (WHPP (TO to) (WHNP (WP whom))). It questions the object of a preposition and is often fronted in a question.',
    steps: [
      'Identify the preposition - IN, or TO for "to" - and the wh-object that follows (wh-word plus noun, if any).',
      'Right-click the canvas and add the WHPP box; connect it to the preposition first.',
      'Add the WHNP box and connect it after the preposition; attach the wh-word and noun beneath it.',
      'Check that the leaves match the example phrase - the canvas checks the tree automatically.',
    ],
    examples: ['to whom', 'for what'],
  },
  {
    type: 'CONJP', title: 'Conjunction phrase', group: 'Special phrases',
    formula: 'CONJP → (RB|IN|CC)+',
    goal: 'Recognise a conjunction phrase by its multi-word connective.',
    summary: 'A multi-word linker that joins two parallel items, such as "as well as".',
    rule: 'A conjunction phrase is a multi-word linker whose parts hang directly under one CONJP box - "as well as" is (CONJP (RB as) (RB well) (IN as)).',
    detail: 'A conjunction phrase (CONJP) links two parallel items with a multi-word conjunction - "as well as", "not to mention", "let alone". SynTutor tags no CC head inside it: each linker word hangs directly under the CONJP as it falls ("as well as" reads RB + RB + IN), and the first conjunct sits outside the CONJP as a sibling.',
    steps: [
      'Find the multi-word conjunction that links the two items.',
      'Right-click the canvas and add the CONJP box; drag its connector dot onto each linker word in order - as, well, as.',
      'Keep the first conjunct outside the CONJP as its sibling - the box holds only the linker words.',
      'Check that the CONJP leaves match the example - the canvas checks the tree automatically.',
    ],
    examples: ['as well as'],
  },
  {
    type: 'UCP', title: 'Unlike-coordinated phrase', group: 'Special phrases',
    formula: 'UCP → X , X',
    goal: 'Recognise an unlike-coordinated phrase by two conjuncts of different categories.',
    summary: 'Coordinates two items of different kinds without a conjunction word, typically joined by punctuation, as in "first, second".',
    rule: 'An unlike-coordinated phrase coordinates two items of different categories with no conjunction between them - "first, second" is (UCP (ADVP (JJ first)) (, ,) (JJ second)).',
    detail: 'An unlike-coordinated phrase (UCP) coordinates two expressions of different grammatical categories without a coordinating conjunction: SynTutor wraps the left item in its own phrase box (an ADVP around first), keeps the punctuation as a sibling leaf, and leaves the right item as a bare adjective: (UCP (ADVP (JJ first)) (, ,) (JJ second)). Unlike ordinary coordination it does not require both conjuncts to match in category.',
    steps: [
      'Identify the two unlike conjuncts and the punctuation between them - there is no conjunction word inside the UCP.',
      'Right-click the canvas and add the UCP box first.',
      'Connect the left conjunct (wrapped in its own phrase box, here an ADVP), then the punctuation leaf, then the right conjunct - a bare adjective leaf.',
      'Check that the leaves match the example - the canvas checks the tree automatically.',
    ],
    examples: ['first, second'],
  },
  {
    type: 'PRT', title: 'Particle', group: 'Special phrases',
    formula: 'PRT → (RB|RP)',
    goal: 'Recognise a particle by the phrasal verb it completes.',
    summary: 'The small word that completes a phrasal verb, such as "away" in "throw away" or "up" in "give up".',
    rule: 'A particle is the small word that completes a phrasal verb. It hangs under the verb phrase in its own PRT box, tagged RB or RP, wherever the sentence puts it.',
    detail: 'A particle (PRT) is a small adverb-like word that belongs to a phrasal verb - away, up, off, out, down - and changes the verb meaning ("throw away", "give up"). SynTutor tags it RB (away) or RP (up) and tucks the PRT box inside the VP: "Throw it away." puts the particle after the object (VP over VB + NP + PRT) while "Give up the fight." puts it before (VP over VB + PRT + NP). Unlike a preposition, a particle takes no object of its own.',
    steps: [
      'Find the phrasal verb and the particle (RB/RP) that completes it.',
      'Right-click the canvas and add the PRT box; drag its connector dot onto the particle word.',
      'Build the VP around it: connect the verb, the object NP if there is one, and the PRT box in sentence order - the particle follows the object in "Throw it away" but precedes it in "Give up the fight."',
      'Wrap the VP in an S box with the sentence-final punctuation, then check that the leaves match - the canvas checks the tree automatically.',
    ],
    examples: ['Throw it away.', 'Give up the fight.'],
  },
  {
    type: 'FRAG', title: 'Fragment', group: 'Special phrases',
    formula: 'FRAG → (UH|RB|.)+',
    goal: 'Recognise a fragment by the missing subject and predicate.',
    summary: 'A phrase used alone as an utterance without a subject and predicate, such as a greeting, headline, or label.',
    rule: 'A fragment is a phrase standing alone as an utterance, without a subject and predicate; its words hang directly under one FRAG box - "Hello there." is (FRAG (UH Hello) (RB there) (. .)).',
    detail: 'A fragment (FRAG) is a phrase used as a standalone utterance without a subject-predicate core - greetings, headlines, labels, answers. Its leaves hang directly under the FRAG box with no inner phrase: "Hello there." reads UH + RB + the final punctuation as three sister leaves. It is headed by whatever word gives it its content (an interjection, noun, or adverb), and the parser marks it FRAG when no full clause can be built.',
    steps: [
      'Identify the words of the utterance and their POS tags - an interjection (UH), an adverb (RB), and the final punctuation.',
      'Right-click the canvas and add the FRAG box for the utterance as a whole.',
      'Drag the FRAG connector dot onto each leaf in reading order - greeting word, adverb, punctuation.',
      'Check that the leaves match the example - the canvas checks the tree automatically.',
    ],
    examples: ['Hello there.'],
  },
  {
    type: 'INTJ', title: 'Interjection', group: 'Special phrases',
    formula: 'INTJ → UH (.!)',
    goal: 'Recognise an interjection by the standalone emotive word and its punctuation.',
    summary: 'A single word that expresses emotion on its own, such as "Wow!" or "Hey!".',
    rule: 'An interjection is a word that expresses emotion on its own: Wow! Hey! Its punctuation hangs beside it under one INTJ box.',
    detail: 'An interjection (INTJ) is a single emotive word - wow, hey, oh, alas - that expresses a reaction on its own, with the exclamation mark kept as a sibling leaf inside the same box: (INTJ (UH Wow) (. !)). It stands outside the subject-predicate structure (it is not the head of any longer phrase) and adds affect rather than propositional meaning to the utterance.',
    steps: [
      'Find the single interjection word (UH) and its punctuation (!).',
      'Right-click the canvas and add the INTJ box above them.',
      'Drag the INTJ connector dot onto the interjection word first, then the punctuation leaf.',
      'Check that the leaves match the example - the canvas checks the tree automatically.',
    ],
    examples: ['Wow!', 'Hey!'],
  },
];

// A module-style lesson (one with `sections`, like the verb phrase) keeps its
// examples inside each section; flatten them into `examples` so progress
// counting, practice loading, and the end-of-module quiz all keep working on
// the flat list.
for (const lesson of LESSONS) {
  if (lesson.sections) lesson.examples = lesson.sections.flatMap((s) => s.examples);
}

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
}

// ---------------------------------------------------------------------------
// The lesson's canvas
// ---------------------------------------------------------------------------
// The Grammar Tutor's empty state ("No Syntax tree to generate yet!") belongs
// to the Grammar Tutor only. Inside a lesson the prompt must never appear —
// it would sit on top of the lesson's own canvas content — so it is hidden
// (class *and* attribute: the rule sets `display: flex`, which would defeat
// the bare `hidden` attribute on its own).
function setEmptyStateHidden(hidden) {
  const empty = document.getElementById('emptyTreeState');
  if (!empty) return;
  empty.classList.toggle('hidden', hidden);
  empty.hidden = hidden;
}

// Wipe the left canvas: the pixels of any tree left over from an earlier
// analysis (a squished, stale ghost tree) go, and so does the renderer's own
// copy of that tree — otherwise the next resize would paint it back.
function clearLessonCanvas() {
  const treeCanvas = document.getElementById('treeCanvas');
  if (treeCanvas) {
    const ctx = treeCanvas.getContext('2d');
    if (ctx) ctx.clearRect(0, 0, treeCanvas.width, treeCanvas.height);
  }
  state.controller?.clearCanvas?.();
}

// The lesson takes the canvas over: the Grammar Tutor's prompt disappears and
// every leftover tree is wiped.
function takeOverCanvas() {
  setEmptyStateHidden(true);
  clearLessonCanvas();
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
  // A lesson may be asked for by its id straight from the console. It goes
  // through the same funnel as a card click, so a guest never slips into a
  // gated lesson that way either.
  const lesson = LESSONS.find((l) => l.type === view);
  if (lesson) {
    openLesson(lesson);
    return;
  }
  if (view === 'lessons') {
    // The lesson picker takes the workspace: the Grammar Tutor's prompt has
    // no business on the canvas while the lessons own it.
    setEmptyStateHidden(true);
    openLessonsOverlay();
    // A deep link may name a lesson: #lesson/NP opens it — or asks for an
    // account, when the lesson is gated.
    handleHashRoute();
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
  closeBuilderView();
  $('#appSidebarBackdrop')?.classList.add('active');
  // The side panel takes the rail highlight while it is open.
  state.controller?.setOverlayView?.(view);
  const body = openSubpanel(view === 'leaderboard' ? 'Leaderboard' : 'Achievements');
  if (!body) return;
  body.appendChild(el('p', 'sq-intro', 'Coming soon.'));
}

export function closeQuizView() {
  closeLessonsOverlay();
  const panel = $('#quizPanel');
  if (panel) { panel.hidden = true; panel.innerHTML = ''; }
  $('#appSidebar')?.classList.remove('quiz-active');
  closeSubpanel();
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
// Left sub-panel: Achievements / Leaderboard / quiz finish (next to the rail)
// ---------------------------------------------------------------------------
// main.js owns #historyDrawerBackdrop (History); tree-quiz.js owns
// #subpanelPlaceholder. Both slide out in the same grid column, so only one
// is ever open — opening one closes the other. `openSubpanel` builds the
// shared chrome (title + close) and hands back the scrollable body.

// Closing the side panel also releases the rail highlight it was holding:
// main.js hands it back to the module underneath.
export function closeSubpanel() {
  $('#historyDrawerBackdrop')?.classList.remove('active');
  const host = $('#subpanelPlaceholder');
  state.controller?.setOverlayView?.(null);
  if (!host) return;
  host.classList.remove('active');
  host.innerHTML = '';
}

function openSubpanel(title) {
  const host = $('#subpanelPlaceholder');
  if (!host) return null;
  $('#historyDrawerBackdrop')?.classList.remove('active');
  host.innerHTML = '';
  const drawer = el('aside', 'history-drawer');
  drawer.setAttribute('aria-label', title);
  const head = el('div', 'drawer-header');
  head.appendChild(el('h2', null, title));
  const close = el('button', 'drawer-close');
  close.type = 'button';
  close.setAttribute('aria-label', 'Close panel');
  close.title = 'Close panel';
  close.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
  close.addEventListener('click', closeSubpanel);
  head.appendChild(close);
  drawer.appendChild(head);
  const body = el('div', 'sq-body subpanel-body');
  drawer.appendChild(body);
  host.appendChild(drawer);
  host.classList.add('active');
  return body;
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
  $('#lessonsCloseBtn')?.addEventListener('click', closeLessonsOverlay);
}

// Esc closes the picker, but only after an open sidebar drawer has had its
// turn — the drawer sits above the overlay. An open category expander closes
// first, so Esc never skips a step.
function onLessonsOverlayKeydown(e) {
  if (e.key !== 'Escape') return;
  if ($('#appSidebarBackdrop')?.classList.contains('active')) return;
  if (category.open) { setCategoryOpen(false); return; }
  closeLessonsOverlay();
}

// Open the lesson library: dismiss the sidebar drawer, refresh the
// per-lesson progress grid, and mark the Lessons tab as current.
function openLessonsOverlay() {
  ensureLessonsOverlay();
  closeStepGuide();
  closeGuideCard();
  closeQuizView();
  // The lesson picker owns the workspace: the Grammar Tutor's empty-canvas
  // prompt has no business on the canvas while the lessons are up.
  setEmptyStateHidden(true);
  $('#appSidebarBackdrop')?.classList.remove('active');
  $('#sidebarToggleBtn')?.setAttribute('aria-expanded', 'false');
  // The Lessons module owns the workspace (and the rail highlight) while it
  // is open.
  state.controller?.setWorkspaceView?.('lessons');
  renderLessons();
  const overlay = $('#lessonsOverlay');
  if (!overlay) return;
  document.body.classList.add('lessons-overlay-open');
  overlay.classList.add('open');
  document.addEventListener('keydown', onLessonsOverlayKeydown);
  $('.cat-trigger', overlay)?.focus({ preventScroll: true });
}

function closeLessonsOverlay() {
  setCategoryOpen(false);
  document.removeEventListener('keydown', onLessonsOverlayKeydown);
  document.body.classList.remove('lessons-overlay-open');
  $('#lessonsOverlay')?.classList.remove('open');
  // Leaving the picker without opening a lesson hands the Grammar Tutor its
  // canvas — and its empty-canvas prompt — back.
  if (state.view !== 'lesson') setEmptyStateHidden(false);
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

function startSession(seq, pos = 0, quizLesson = null) {
  state.session = { seq, pos, quizLesson, answered: false };
  advance();
}

async function advance() {
  const s = state.session;
  if (!s) return;
  // A fresh question: nothing answered yet, and the last check result
  // belonged to the previous tree.
  s.answered = false;
  state.checkStatus = null;
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
  const lessonType = state.session?.quizLesson || null;
  if (lessonType) state.quizDone.add(lessonType);
  state.session = null;
  closeBuilderView();
  closeGuideCard();
  $('#appSidebarBackdrop')?.classList.add('active');
  // The session belongs to the Lessons module.
  state.controller?.setWorkspaceView?.('lessons');
  const body = openSubpanel("You've built every tree!");
  if (!body) return;
  body.appendChild(el('p', 'sq-intro', 'Nice work — you constructed every phrase type SynTutor knows.'));
  const again = el('button', 'sq-stage sq-stage-alt');
  again.type = 'button';
  again.appendChild(el('span', 'sq-stage-title', 'Start again'));
  again.addEventListener('click', () => { closeQuizView(); startSession(flatExamples()); });
  body.appendChild(again);
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
// Special phrases) — the catalog groups the cards by them.
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

// ---------------------------------------------------------------------------
// Category selector: an inline expander in the catalog toolbar
// ---------------------------------------------------------------------------
// Collapsed it is a single trigger pill showing the active category; clicking
// it grows a horizontal row of category pills out of the toolbar, and picking
// one filters the cards and collapses the row again.
const category = { open: false, host: null, trigger: null, label: null };

const ALL_CATEGORIES = 'All';

function categoryNames(groups) {
  return [ALL_CATEGORIES, ...groups.map((g) => g.name)];
}

// The label on the trigger: the active category, or 'All' when the filter
// points at a category the catalog no longer has.
function activeCategoryLabel(groups) {
  if (state.activeGroup === ALL_CATEGORIES) return ALL_CATEGORIES;
  return groups.some((g) => g.name === state.activeGroup) ? state.activeGroup : ALL_CATEGORIES;
}

// Build (or rebuild) the trigger and the row of category pills.
function buildCategorySelector(groups) {
  const host = $('#lessonsCategory');
  if (!host) return;
  host.innerHTML = '';

  const trigger = el('button', 'cat-trigger');
  trigger.type = 'button';
  trigger.setAttribute('aria-haspopup', 'true');
  trigger.setAttribute('aria-expanded', 'false');
  trigger.setAttribute('aria-label', 'Choose a lesson category');
  const label = el('span', 'cat-trigger-label', activeCategoryLabel(groups));
  const chevron = el('span', 'cat-chevron');
  chevron.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 18 15 12 9 6"></polyline></svg>';
  trigger.appendChild(label);
  trigger.appendChild(chevron);
  trigger.addEventListener('click', () => setCategoryOpen(!category.open));
  host.appendChild(trigger);

  const options = el('div', 'cat-options');
  options.setAttribute('role', 'group');
  options.setAttribute('aria-label', 'Lesson categories');
  categoryNames(groups).forEach((name) => {
    const pill = el('button', name === state.activeGroup ? 'cat-pill is-active' : 'cat-pill', name);
    pill.type = 'button';
    pill.setAttribute('aria-pressed', String(name === state.activeGroup));
    pill.addEventListener('click', () => selectCategory(name));
    options.appendChild(pill);
  });
  host.appendChild(options);

  category.host = host;
  category.trigger = trigger;
  category.label = label;
  // The row is rebuilt on every render, so the open state is re-applied here.
  host.classList.toggle('is-open', category.open);
  trigger.setAttribute('aria-expanded', String(category.open));
}

// Open or close the expander. While it is open, a click outside collapses
// it again.
function setCategoryOpen(open) {
  const host = category.host;
  if (!host) return;
  category.open = Boolean(open);
  host.classList.toggle('is-open', category.open);
  category.trigger?.setAttribute('aria-expanded', String(category.open));
  if (category.open) {
    document.addEventListener('click', onClickOutsideCategory, true);
  } else {
    document.removeEventListener('click', onClickOutsideCategory, true);
  }
}

function onClickOutsideCategory(e) {
  const host = category.host;
  if (!host || host.contains(e.target)) return;
  setCategoryOpen(false);
}

// Pick a category: filter the cards, relabel the trigger, collapse the row.
function selectCategory(name) {
  state.activeGroup = name;
  setCategoryOpen(false);
  renderLessons();
}

// One module card in the e-learning catalog. A module-style lesson (one with
// `sections`, like the verb phrase) is a collapsible unit: clicking the card
// expands it in place to reveal a list of its sub-topics, and picking one
// opens the lesson focused on that sub-topic. Every other lesson is a single
// unit and opens directly.
function moduleSubtopics(lesson) {
  const list = el('ul', 'sq-module-topics');
  list.setAttribute('role', 'list');
  lesson.sections.forEach((section, i) => {
    const built = section.examples.filter((s) => state.done.has(`${lesson.type}:${s}`)).length;
    const sectionDone = built === section.examples.length;
    const item = el('li', 'sq-module-topic-item');
    const btn = el('button', sectionDone ? 'sq-module-topic is-done' : 'sq-module-topic');
    btn.type = 'button';
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      openLessonAtSection(lesson, i);
    });
    const head = el('span', 'sq-module-topic-head');
    head.appendChild(el('span', 'sq-module-topic-name', section.title));
    if (sectionDone) head.appendChild(el('span', 'sq-module-topic-count', '✓'));
    btn.appendChild(head);
    btn.appendChild(el('span', 'sq-module-topic-detail', section.detail));
    item.appendChild(btn);
    list.appendChild(item);
  });
  return list;
}

function lessonCard(lesson) {
  const { done, total, pct } = lessonProgress(lesson);
  const complete = done === total;
  // A gated lesson is locked for a guest: the card says so, and picking it
  // asks for an account instead of opening the lesson.
  const locked = isLessonGated(lesson) && isGuestSession();
  const isModule = Boolean(lesson.sections?.length);
  const expanded = isModule && state.openModule === lesson.type;
  const card = el('article', 'sq-card-cell');


  // A module tile reads like a course card: a header band carrying the module
  // name, then a body with the description and its sub-topic preview chips.
  const face = el('button', 'sq-card');
  face.type = 'button';
  face.title = isModule ? `${lesson.title} — pick a sub-topic` : lesson.title;

  if (locked) face.classList.add('is-locked');
  else if (complete) face.classList.add('is-complete');
  face.dataset.lessonId = lesson.type;
  if (locked) {
    face.title = `${lesson.title} — create a free account to open it`;
  }

  const head = el('span', 'sq-card-head');
  if (!isModule) head.appendChild(el('span', 'sq-card-tag', lesson.type));
  head.appendChild(el('span', 'sq-card-title', lesson.title));
  if (locked) {
    const badge = el('span', 'sq-card-lock-badge');
    badge.setAttribute('aria-label', 'Locked');
    badge.innerHTML = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>';
    head.appendChild(badge);
  }
  if (isModule) {
    const chevron = el('span', expanded ? 'sq-card-expand is-open' : 'sq-card-expand');
    chevron.setAttribute('aria-hidden', 'true');
    chevron.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>';
    head.appendChild(chevron);
  }
  face.appendChild(head);

  const body = el('span', 'sq-card-body');
  body.appendChild(el('span', 'sq-card-overview', lesson.summary || lesson.rule));
  body.appendChild(el('span', 'sq-card-count', complete ? `✓ ${done}/${total}` : `${done}/${total}`));
  if (isModule) {
    const chips = el('span', 'sq-card-topics');
    for (const section of lesson.sections) {
      chips.appendChild(el('span', 'sq-card-topic-chip', section.name));
    }
    body.appendChild(chips);
  }
  face.appendChild(body);

  face.addEventListener('click', () => {
    if (locked) {
      // A guest asking for a gated lesson: remember it, then ask for an
      // account. Signing up drops the learner straight into the lesson.
      window.pendingLessonUnlock = lesson.type;
      openAuthModal({ mode: 'register', reason: 'lessons_gate' });
      return;
    }
    if (isModule) toggleModule(lesson);
    else openLesson(lesson);
  });
  card.appendChild(face);
  if (expanded) card.appendChild(moduleSubtopics(lesson));
  return card;
}

// The catalog's page header: the same title, baseline and dividing line as
// the leaderboard and the achievements. It sits at the very top of the
// catalog, directly above the content body, so the catalog reads
// title → toolbar → cards.
function renderLessonsHeader() {
  const body = $('.sq-catalog-content');
  const container = body ? body.parentElement : null;
  if (!container) return;
  let header = $('.lessons-header');
  if (!header) {
    header = el('header', 'view-header lessons-header');
    header.appendChild(el('h2', null, 'Lessons'));
    container.insertBefore(header, body);
  }
}

// Open or collapse a module's sub-topic list in the catalog.
function toggleModule(lesson) {
  state.openModule = state.openModule === lesson.type ? null : lesson.type;
  renderLessons();
}
function renderLessons() {
  ensureLessonsOverlay();
  renderLessonsHeader();
  renderLessonsSummary();
  const groups = lessonsGroups();
  buildCategorySelector(groups);

  const grid = $('#lessonsGrid');
  if (!grid) return;
  grid.innerHTML = '';
  const visible = state.activeGroup === ALL_CATEGORIES
    ? LESSONS
    : groups.filter((g) => g.name === state.activeGroup).flatMap((g) => g.lessons);
  for (const lesson of visible) {
    grid.appendChild(lessonCard(lesson));
  }
}

// Choosing a card loads the topic into the workspace: the picker fades away,
// the lesson card opens on its Concept page, and the first example opens on
// the builder canvas in place (no sidebar tab switch).
function openLesson(lesson) {
  // The single funnel for opening a lesson: a guest asking for a gated one
  // never gets in, however the lesson was requested.
  if (isLessonGated(lesson) && isGuestSession()) {
    window.pendingLessonUnlock = lesson.type;
    // The learner is returned to the catalog: it is the backdrop of the
    // registration prompt.
    if (!$('#lessonsOverlay')?.classList.contains('open')) openLessonsOverlay();
    openAuthModal({ mode: 'register', reason: 'lessons_gate' });
    return;
  }
  closeLessonsOverlay();
  closeGuideCard();
  // Switching lessons invalidates any /api/parse response still in flight and
  // drops the previous lesson's tree; a non-module lesson starts with a clear
  // canvas, a module lesson immediately loads its own model below.
  goldRequest += 1;
  state.goldLoading = null;
  state.goldError = null;
  // A lesson owns the canvas, so clear whatever was on it (the tutor's tree or
  // the previous lesson's model) before painting the new one.
  state.controller?.clearModelTree?.({ force: true });
  if (!lesson.sections) document.querySelector('#emptyTreeState')?.classList.remove('hidden');
  // Picking a lesson leaves any quiz session behind. The learner is now in
  // focused study, not the session's in-order walk. Single-unit lessons open
  // on Node 1 (Concept); module lessons open directly on their first sample.
  state.session = null;
  state.openModule = null;
  // The catalog remembers the category it was left on. A guest keeps the
  // filter they had: the locked lessons are what they are being invited to.
  if (!isGuestSession()) state.activeGroup = lesson.group;
  state.lessonPage = 1;
  state.lessonIndex = lesson.type;
  state.view = 'lesson';
  state.exampleIndex = 0;
  state.sectionIndex = 0;
  if (lesson.sections) {
    state.exampleIndex = defaultExampleIndex(lesson);
    renderLesson();
    const host = $('#quizQuestHost');
    if (host) host.scrollTop = 0;
    openModelExample(lesson, lesson.examples[state.exampleIndex]);
    return;
  }
  renderLesson();
}

// Open a module straight onto one of its sub-topics: the section's first
// sample loads on the read-only canvas and the LMS panel follows it.
function openLessonAtSection(lesson, sectionIndex) {
  closeLessonsOverlay();
  closeGuideCard();
  // The catalog can be opened over the tutor, so the lesson must take the
  // canvas over explicitly instead of leaving the tutor's tree underneath.
  state.controller?.clearModelTree?.({ force: true });
  state.session = null;
  state.openModule = null;
  state.activeGroup = lesson.group;
  state.lessonPage = 1;
  state.lessonIndex = lesson.type;
  state.view = 'lesson';
  state.sectionIndex = Math.max(0, Math.min(sectionIndex, lesson.sections.length - 1));
  state.goldError = null;
  state.goldLoading = null;
  state.exampleIndex = defaultExampleIndex(lesson);
  renderLesson();
  const host = $('#quizQuestHost');
  if (host) host.scrollTop = 0;
  openModelExample(lesson, lesson.examples[state.exampleIndex]);
}

// ---------------------------------------------------------------------------
// Access tiers
// ---------------------------------------------------------------------------
// The introductory phrase lessons stay open for everybody: a guest can work
// through the whole "Phrases" category without an account. The deeper
// material — clauses, wh-phrases and the special phrases — needs one.
const FREE_LESSON_GROUPS = new Set(['Phrases']);

// Does this lesson need an account?
function isLessonGated(lesson) {
  return !FREE_LESSON_GROUPS.has(lesson.group);
}

// Does this category need an account?
function isGroupGated(group) {
  return !FREE_LESSON_GROUPS.has(group);
}

// A deep link may open a lesson directly: #lesson/NP. A guest asking for a
// gated lesson is sent back to the catalog with the registration prompt.
function handleHashRoute() {
  const match = /^#lesson\/([A-Za-z]+)$/.exec(window.location.hash || '');
  if (!match) return;
  const lesson = LESSONS.find((l) => l.type === match[1]);
  if (!lesson) return;
  // The link is handled once: the hash is cleared so the lesson does not
  // reopen behind the learner's back.
  if (window.history?.replaceState) {
    window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}`);
  }
  // The catalog is the backdrop of the prompt.
  if (!$('#lessonsOverlay')?.classList.contains('open')) openLessonsOverlay();
  // openLesson is the guarded funnel: a gated lesson asks for an account
  // instead of opening.
  openLesson(lesson);
}

// A deep link may also arrive while the app is running.
window.addEventListener('hashchange', handleHashRoute);

// The catalog follows the session: a guest sees the locks, an account sees
// every lesson open — and lands in the lesson they asked for before signing
// up.
subscribeAuthState((authState) => {
  // A guest who signs out lands on the free lessons again.
  if (isGuestSession() && state.activeGroup !== ALL_CATEGORIES && isGroupGated(state.activeGroup)) {
    state.activeGroup = ALL_CATEGORIES;
  }
  renderLessons();
  if (!authState.authenticated) return;
  // The lesson the guest picked before creating an account: open it now.
  const pending = window.pendingLessonUnlock;
  if (!pending) return;
  window.pendingLessonUnlock = null;
  const lesson = LESSONS.find((l) => l.type === pending);
  if (lesson) openLesson(lesson);
});

// ---------------------------------------------------------------------------
// Lesson: one construction + its examples + its quiz
// ---------------------------------------------------------------------------
// The active lesson is a three-stage branch across two panes: the upper-right
// #quizQuestHost holds the lesson header (the book button, the title, and the
// compact stage progress bar) plus the controls of the *current* stage only,
// while the bottom-right #lessonGuideHost shows that stage's explanation.
// Stage 1 is the Concept, Stage 2 is Practice (pick an example, it loads on
// the canvas; lessons with numbered build steps get a guide card whose Play
// button walks the steps, module-style lessons get a section picker instead),
// and Stage 3 is the module's comprehensive quiz.
const LESSON_NODES = [
  { page: 1, label: 'Concept' },
  { page: 2, label: 'Practice' },
  { page: 3, label: 'Quiz' },
];

// The canvas hint of each stage. Stage 1 is a demonstration: the reference
// tree is read-only, so its hint says so instead of inviting the learner to
// build something they cannot build yet.
const CONCEPT_HINT = 'Reference Tree · Observe the hierarchy and constituent branches';
const PRACTICE_HINT = 'Right-click to add a phrase · drag a dot to connect · grab a link end to re-route or delete';
const QUIZ_HINT = 'Build the tree, then check it against SynTutor’s parse';

// A short title for a step, derived from the step's own wording so every
// lesson reads the same way: leaf identification, adding the phrase box,
// connecting the branches, checking the result.
function stepTitle(lesson, index) {
  const step = lesson.steps[index] || '';
  const box = step.match(/\badd (?:an?|the) ([A-Z]{1,6}) box\b/i);
  if (box) return `Add the ${box[1].toUpperCase()} Box`;
  if (/^(Check|Verify)\b/i.test(step)) return 'Check the Tree';
  if (/\bconnect(?:or)?\b|\bconnector dot\b|\bdrag\b/i.test(step)) return 'Connect the Branches';
  if (/^(Read|Find|Identify|Spot|Pick out|Split)\b/i.test(step)) return 'Leaf Identification';
  return `Step ${index + 1}`;
}

// A node is "completed" once its activity is done: the concept has been seen,
// every example has been built, or the end-of-lesson quiz has been finished.
function lessonNodeDone(lesson, page, current) {
  if (page === 1) return page !== current && state.visitedPages.has(`${lesson.type}:1`);
  if (page === 2) {
    const p = lessonProgress(lesson);
    if (p.total > 0 && p.done === p.total) return true;
    // The learner worked through the practice and moved on to the quiz: the
    // stage keeps its checkmark instead of falling back to its number.
    return current > 2 && state.visitedPages.has(`${lesson.type}:2`);
  }
  return state.quizDone.has(lesson.type);
}

// The node-and-branch progress: three compact nodes (1 → 2 → 3) joined by
// short branch lines. Each node is clickable, shows a ✓ once its stage is
// done, and marks the stage the learner is on.
function renderLessonNodes(lesson, current) {
  const wrap = el('div', 'stage-stepper-tracker');
  wrap.setAttribute('role', 'group');
  wrap.setAttribute('aria-label', 'Lesson stages');
  LESSON_NODES.forEach((node, i) => {
    const done = lessonNodeDone(lesson, node.page, current);
    let cls = 'sq-progress-node';
    if (node.page === current) cls += ' active';
    if (done) cls += ' completed';
    const btn = el('button', cls);
    btn.type = 'button';
    btn.title = `${node.label}${done ? ' — done' : ''}`;
    btn.setAttribute('aria-label', node.label);
    btn.setAttribute('aria-pressed', String(node.page === current));
    btn.appendChild(el('span', 'sq-progress-node-badge', done ? '✓' : String(node.page)));
    btn.addEventListener('click', () => goLessonNode(lesson, node.page));
    wrap.appendChild(btn);
    if (i < LESSON_NODES.length - 1) wrap.appendChild(el('span', 'sq-progress-line'));
  });
  return wrap;
}

// The example switcher: labelled pills, so the learner knows which sentence
// each one opens. A built example carries a green ✓.
function renderExampleSwitcher(lesson, index) {
  const bar = el('div', 'example-pill-selector');
  bar.setAttribute('role', 'group');
  bar.setAttribute('aria-label', 'Lesson examples');
  lesson.examples.forEach((sentence, i) => {
    const done = state.done.has(`${lesson.type}:${sentence}`);
    const tab = el('button', done ? 'example-tab is-done' : 'example-tab');
    if (i === index) tab.classList.add('active');
    tab.type = 'button';
    tab.appendChild(document.createTextNode(`${i + 1}. `));
    tab.appendChild(el('span', 'example-tab-text', sentence));
    if (done) tab.appendChild(el('span', 'example-tab-check', '✓'));
    // The sentence is already on the tab: no tooltip on top of it.
    tab.setAttribute('aria-label', `Example ${i + 1}: ${sentence}`);
    tab.addEventListener('click', () => showExample(lesson, i));
    bar.appendChild(tab);
  });
  return bar;
}

// The primary action of the practice stage follows the learner through the
// practice: step by step, then example by example, and only once every
// example is built does it turn into the quiz.
function practiceCta(lesson) {
  const { done, total } = lessonProgress(lesson);
  if (total > 0 && done === total) return { label: 'Start Quiz →', kind: 'quiz' };
  if (guide.step >= lesson.steps.length - 1) return { label: 'Next Example →', kind: 'example' };
  return { label: 'Next Step →', kind: 'step' };
}

// Run the practice action: the next step, the next example, or the quiz.
function runPracticeCta(lesson) {
  const action = practiceCta(lesson);
  if (action.kind === 'quiz') {
    startLessonQuiz(lesson);
    return;
  }
  if (action.kind === 'step') {
    openStepGuide(lesson, guide.step + 1);
    return;
  }
  // Next example: the next one that is not built yet; if they are all built,
  // the quiz is what comes next.
  const total = lesson.examples.length;
  for (let i = 1; i <= total; i += 1) {
    const idx = (state.exampleIndex + i) % total;
    if (!state.done.has(`${lesson.type}:${lesson.examples[idx]}`)) {
      showExample(lesson, idx);
      return;
    }
  }
  startLessonQuiz(lesson);
}

// The upper-right stage content. Every stage shows only what belongs to it:
// the Concept never lists the examples, the Practice stage never repeats the
// concept, and the Quiz stage is the only one that talks about the score.
// A module-style lesson (one with `sections`) swaps the numbered step pager
// on Practice for a section picker: one section per type of the construction.
function renderLessonStage(lesson, page, index, example) {
  const stage = el('div', 'sq-lesson-stage');

  if (page === 1) {
    // Concept: a compact lesson overview — where the construction sits, the
    // target structure it follows, and the one thing to take away. The full
    // explanation lives in the bottom-right pane; nothing is repeated here.
    const overview = el('div', 'sq-lesson-overview');

    const tags = el('div', 'sq-overview-tags');
    tags.appendChild(el('span', 'sq-overview-tag', lesson.group));
    tags.appendChild(el('span', 'sq-overview-tag is-type', lesson.type));
    overview.appendChild(tags);

    const formula = el('div', 'sq-overview-structure');
    formula.appendChild(el('span', 'sq-overview-label', 'Target structure'));
    formula.appendChild(el('code', 'sq-overview-formula', lesson.formula));
    overview.appendChild(formula);

    overview.appendChild(el('p', 'sq-overview-goal', lesson.goal));

    stage.appendChild(overview);
    const cta = el('button', 'sq-primary quiz-primary-btn sq-lesson-cta', 'Start Steps & Practice →');
    cta.type = 'button';
    cta.addEventListener('click', () => goLessonNode(lesson, 2));
    stage.appendChild(cta);
    return stage;
  }

  if (page === 2) {
    // Practice: the example switcher, the step the learner is on, and the
    // action that walks them through it. The analysis of the example belongs
    // to the lower pane — nothing is printed twice.
    stage.appendChild(renderExampleSwitcher(lesson, index));

    // The step itself: what to do right now.
    const stepBox = el('div', 'sq-active-step');
    stepBox.id = 'sqActiveStep';
    fillActiveStep(stepBox, lesson);
    stage.appendChild(stepBox);

    // The step navigation: the learner moves through the steps themselves.
    const pager = el('div', 'sq-step-pager');
    const prev = el('button', 'sq-ghost sq-step-btn', '←');
    prev.type = 'button';
    prev.id = 'sqStepPrev';
    prev.title = 'Previous step';
    prev.disabled = guide.step <= 0;
    prev.addEventListener('click', () => openStepGuide(lesson, guide.step - 1));
    const label = el('span', 'sq-step-pager-label', `Step ${guide.step + 1} of ${lesson.steps.length}`);
    label.id = 'sqStepLabel';
    const next = el('button', 'sq-ghost sq-step-btn', '→');
    next.type = 'button';
    next.id = 'sqStepNext';
    next.title = 'Next step';
    next.disabled = guide.step >= lesson.steps.length - 1;
    next.addEventListener('click', () => openStepGuide(lesson, guide.step + 1));
    pager.appendChild(prev);
    pager.appendChild(label);
    pager.appendChild(next);
    stage.appendChild(pager);

    const cta = el('button', 'sq-primary quiz-primary-btn sq-stage-cta', practiceCta(lesson).label);
    cta.type = 'button';
    cta.id = 'sqStageCta';
    cta.addEventListener('click', () => runPracticeCta(lesson));
    stage.appendChild(cta);
    return stage;
  }

  // Quiz: the stage IS the quiz — it is already running, so the panel shows
  // the live question, the progress, and the way on. The diagnostics belong
  // to the lower pane.
  if (state.session) {
    const live = el('div', 'sq-active-sentence');
    live.appendChild(el('span', 'sq-active-label is-quiz',
      `QUESTION ${state.session.pos + 1} OF ${state.session.seq.length}`));
    live.appendChild(el('p', 'sq-active-text',
      `Build the syntax tree for “${state.session.seq[state.session.pos]?.example || ''}”`));
    stage.appendChild(live);

    const score = el('div', 'sq-quiz-score');
    score.appendChild(el('span', 'sq-quiz-score-value',
      `${state.session.pos}/${state.session.seq.length}`));
    score.appendChild(el('span', 'sq-quiz-score-label', 'trees built'));
    stage.appendChild(score);

    const cta = el('button', 'sq-primary quiz-primary-btn sq-stage-cta',
      state.session.answered ? 'Next Question →' : 'Check Tree →');
    cta.type = 'button';
    cta.id = 'sqStageCta';
    cta.addEventListener('click', () => {
      if (state.session?.answered) nextQuizQuestion();
      else checkBuilderTree();
    });
    stage.appendChild(cta);
    return stage;
  }

  // No run yet (the stage was opened without one): offer the launcher.
  const list = el('ul', 'sq-quiz-list');
  for (const sentence of lesson.examples) {
    const item = el('li', 'sq-quiz-item');
    const done = state.done.has(`${lesson.type}:${sentence}`);
    item.appendChild(el('span', done ? 'sq-quiz-mark is-done' : 'sq-quiz-mark', done ? '✓' : '○'));
    item.appendChild(el('span', 'sq-quiz-sent', sentence));
    list.appendChild(item);
  }
  stage.appendChild(list);
  const start = el('button', 'sq-primary quiz-primary-btn', 'Start Quiz →');
  start.type = 'button';
  start.addEventListener('click', () => startLessonQuiz(lesson));
  stage.appendChild(start);
  return stage;
}

// The active step, in full: what to do, and the grammar rule it applies.
// Only this one step is shown — the navigator lives in the upper-right pane
// and the canvas card carries the prompt, so the step text is never printed
// three times.
function fillActiveStep(box, lesson) {
  box.innerHTML = '';
  const index = Math.max(0, Math.min(guide.step, lesson.steps.length - 1));
  box.appendChild(el('h3', 'sq-active-step-title', stepTitle(lesson, index)));
  box.appendChild(el('p', 'sq-active-step-text', lesson.steps[index]));
}

// Keep the practice stage in step with the guide: the pager, the active step
// in the bottom-right pane, and the primary action all follow the current
// step, so they are updated in place instead of re-rendering the panel.
function updateStepUI(lesson) {
  if (!lesson) return;
  const label = $('#sqStepLabel');
  if (label) label.textContent = `Step ${guide.step + 1} of ${lesson.steps.length}`;
  const prev = $('#sqStepPrev');
  if (prev) prev.disabled = guide.step <= 0;
  const next = $('#sqStepNext');
  if (next) next.disabled = guide.step >= lesson.steps.length - 1;
  const box = $('#sqActiveStep');
  if (box) fillActiveStep(box, lesson);
  const cta = $('#sqStageCta');
  if (cta) {
    const action = practiceCta(lesson);
    cta.textContent = action.label;
    cta.dataset.kind = action.kind;
  }
}

// The live validation status of the quiz stage: what the last check said
// about the tree the learner is building.
function updateValidationStatus(target) {
  const box = target || $('#sqValidationResult');
  if (!box) return;
  box.innerHTML = '';
  const status = state.checkStatus;
  const lesson = activeLesson();

  // Nothing checked yet: the rule, the instructions, and no answer.
  if (!status) {
    if (lesson) box.appendChild(diagnosticIdleState(lesson));
    return;
  }

  const card = el('div', 'validation-result-card');
  card.classList.add(status.kind === 'ok' ? 'is-ok' : 'is-no');

  if (status.kind === 'ok') {
    card.appendChild(el('span', 'validation-card-title', '✓ Correct — the constituency is valid.'));
    card.appendChild(el('p', 'validation-card-body', constituencyExplanation(
      lesson, state.session?.seq[state.session.pos]?.example)));
    box.appendChild(card);
    return;
  }

  // Not quite: the check said what is wrong, and the tree says where.
  card.appendChild(el('span', 'validation-card-title', '✕ Not quite — the tree does not match SynTutor’s parse.'));
  card.appendChild(el('p', 'validation-card-body', status.message));
  box.appendChild(card);

  // The findings: what is valid, and what to fix.
  const findings = describeFindings();
  if (findings.length) {
    const list = el('div', 'validation-findings');
    for (const note of findings) {
      list.appendChild(el('p', 'validation-finding', note));
    }
    box.appendChild(list);
  }
}

// Move on to the next question of the running quiz.
function nextQuizQuestion() {
  const s = state.session;
  if (!s) return;
  s.pos += 1;
  s.answered = false;
  advance();
}

// The bottom-right content: the current stage's explanation, rendered
// directly on the pane surface — no nested card, no clipped text. It is the
// one place a stage's words live, so nothing here is repeated in the
// upper-right pane.
function renderLessonBody(lesson, page, example) {
  const body = el('div', 'sq-lesson-body');
  if (page === 1) {
    // Concept: the whole lower surface belongs to the theory — the
    // constituency rule, then how it works in detail. One section label, one
    // key-value grid: no stacked headers.
    body.appendChild(el('div', 'analysis-section-label', 'CONSTITUENCY ANALYSIS'));
    const grid = el('div', 'syntax-role-grid');
    grid.appendChild(el('span', 'syntax-role-label', 'Constituency rule'));
    grid.appendChild(el('span', 'syntax-role-value', lesson.rule));
    grid.appendChild(el('span', 'syntax-role-label', 'In depth'));
    grid.appendChild(el('span', 'syntax-role-value', lesson.detail));
    body.appendChild(grid);
    return body;
  }
  if (page === 2) {
    // Practice: the live breakdown of the example on the canvas — its leaves,
    // its head, and the modifiers hanging off that head.
    body.appendChild(el('div', 'analysis-section-label', 'SYNTAX BREAKDOWN'));
    body.appendChild(renderBreakdown(lesson, example));
    return body;
  }

  // Quiz: the diagnostics. The question itself lives in the upper pane; this
  // one says what to build and what SynTutor thinks of the result.
  body.appendChild(el('div', 'analysis-section-label', 'VALIDATION & SYNTACTIC DIAGNOSTICS'));
  body.appendChild(renderDiagnostics(lesson, example));
  return body;
}

// ---------------------------------------------------------------------------
// The lower panel: the grammar's side of the lesson
// ---------------------------------------------------------------------------
// The upper panel belongs to the learner (the controls, the active step, the
// question, the action); this one belongs to the grammar (the theory, the
// breakdown of the current example, the validation diagnostics). The two
// never print the same words twice.

// The cached parse of an example: its tree and its tagged leaves.
function goldFor(example) {
  return state.cache.get(example) || null;
}

// The words a node covers, in reading order.
function leafText(node) {
  if (!node) return '';
  if (node.leaf || !node.children) return node.surface ?? '';
  return node.children.map(leafText).join(' ');
}

// The head of a phrase is the child that carries its meaning: the noun in an
// NP, the verb in a VP, the adjective in an ADJP. Each phrase type puts its
// head in its own place, so each gets its own rule.
const HEAD_RULES = {
  NP: (kids) => {
    // A nested NP (a prepositional complement, as in "a student of physics")
    // keeps the head inside it.
    const inner = kids.find((k) => k.type === 'NP');
    if (inner) return phraseHead(inner);
    return [...kids].reverse().find((k) => /^NN/.test(k.type));
  },
  VP: (kids) => kids.find((k) => /^VB/.test(k.type)),
  ADJP: (kids) => [...kids].reverse().find((k) => /^JJ/.test(k.type)),
  ADVP: (kids) => [...kids].reverse().find((k) => /^RB/.test(k.type)),
  PP: (kids) => kids.find((k) => k.type === 'IN')
    || [...kids].reverse().find((k) => /^NN/.test(k.type)),
};

// The phrase types whose children are modifiers around a head. In a clause
// the children are constituents — the subject and the predicate — so the
// panel says "constituents" there instead of "modifiers".
const MODIFIER_PHRASES = new Set(['NP', 'ADJP', 'ADVP', 'PP', 'QP', 'NML', 'NX']);

// The head of a phrase: the child that carries its meaning.
function phraseHead(node) {
  if (!node) return null;
  const kids = node.children || [];
  const rule = HEAD_RULES[node.type];
  const head = (rule ? rule(kids) : null)
    || [...kids].reverse().find((k) => !k.leaf);
  return head || null;
}

// The head of a phrase, and the parts around it.
function phraseParts(node) {
  const kids = node && node.children ? node.children : [];
  const head = phraseHead(node);
  const modifierPhrase = node ? MODIFIER_PHRASES.has(node.type) : false;
  return {
    head: head || null,
    parts: kids.filter((k) => k !== head),
    label: modifierPhrase ? 'Direct modifiers' : 'Constituents',
    modifierPhrase,
  };
}

// What each modifier does to the phrase it hangs off.
const MODIFIER_ROLES = {
  DT: 'a determiner that selects the noun',
  JJ: 'an adjective that modifies the head',
  JJR: 'a comparative adjective that modifies the head',
  JJS: 'a superlative adjective that modifies the head',
  RB: 'an adverb that modifies the head',
  IN: 'a marker that introduces the phrase as its complement',
  TO: 'a marker that introduces the phrase as its complement',
  PP: 'a prepositional phrase that completes the phrase',
  CC: 'a coordinator that joins two constituents',
  PRP: 'a pronoun that stands for the phrase',
  'PRP$': 'a possessive pronoun that stands for the phrase',
  POS: 'a possessive marker that attaches to the head',
  CD: 'a numeral that quantifies the head',
  WDT: 'a wh-determiner that fills the phrase',
  WP: 'a wh-word that fills the phrase',
  'WP$': 'a possessive wh-word that fills the phrase',
};

// Why the modifiers attach to the phrase node rather than to one another.
function attachmentNote(tree, parts) {
  if (!parts.parts.length) {
    return `The ${tree.type} has no parts of its own: the head stands alone.`;
  }
  if (!parts.modifierPhrase) {
    return `The ${tree.type} is built from ${parts.parts
      .map((m) => `${m.type} (${leafText(m)})`).join(' and ')} — the constituents the phrase is made of.`;
  }
  const roles = parts.parts.map((m) => {
    const role = MODIFIER_ROLES[m.type] || 'a modifier of the phrase';
    return `${m.type} (${leafText(m)}) is ${role}`;
  });
  return `${roles.join('; ')}. They attach to the ${tree.type} node itself — the modifiers hang off the phrase, not off one another.`;
}

// The monospace rule badge that closes every analysis panel.
function ruleBadge(label, formula) {
  const badge = el('div', 'rule-chip');
  badge.appendChild(el('span', 'rule-chip-label', `${label}: `));
  badge.appendChild(el('code', 'rule-chip-code', formula));
  return badge;
}

// The live breakdown of the example on the canvas: the leaves with their POS
// tags, the head of the phrase, the modifiers around it, and why they attach
// where they do.
function renderBreakdown(lesson, example) {
  const box = el('div', 'sq-breakdown');
  const gold = goldFor(example);
  if (!gold?.tree) {
    box.appendChild(el('p', 'sq-panel-empty',
      'SynTutor is still reading this sentence — the breakdown follows in a moment.'));
    return box;
  }
  const tree = gold.tree;

  // The leaves, one by one, with the tag SynTutor gave them.
  const tokens = el('div', 'syntax-token-row');
  for (const leaf of leavesWithTags(tree)) {
    const token = el('span', 'syntax-token');
    token.appendChild(el('span', 'syntax-token-word', leaf.surface));
    token.appendChild(el('span', 'syntax-token-tag', `[${leaf.tag}]`));
    tokens.appendChild(token);
  }
  box.appendChild(tokens);

  // The head of the phrase and the parts around it.
  const parts = phraseParts(tree);
  const grid = el('div', 'syntax-role-grid');
  grid.appendChild(el('span', 'syntax-role-label', 'Head'));
  grid.appendChild(el('span', 'syntax-role-value',
    parts.head ? `${parts.head.type} (${leafText(parts.head)})` : '—'));
  grid.appendChild(el('span', 'syntax-role-label', parts.label));
  grid.appendChild(el('span', 'syntax-role-value', parts.parts.length
    ? parts.parts.map((m) => `${m.type} (${leafText(m)})`).join(', ')
    : 'none'));
  box.appendChild(grid);

  // Why the modifiers attach to this node.
  box.appendChild(el('p', 'syntax-explanation', attachmentNote(tree, parts)));

  // The rule the whole thing follows.
  box.appendChild(ruleBadge('RULE IN PLAY', lesson.formula));
  return box;
}

// The live diagnostic of the quiz stage. While the quiz is running the panel
// says nothing about the answer: the learner gets the rule, a nudge, and —
// once they press Check Tree — the verdict with the reasons behind it.
function renderDiagnostics(lesson, example) {
  const box = el('div', 'sq-diagnostics');
  const result = el('div', 'sq-diag-block');
  result.id = 'sqValidationResult';
  box.appendChild(result);
  // The block is not in the document yet: hand it over directly.
  updateValidationStatus(result);
  return box;
}

// The lesson the workspace is in right now.
function activeLesson() {
  return LESSONS.find((l) => l.type === state.lessonIndex) || null;
}

// Why the constituency is valid — the explanation that comes with a correct
// build, once the answer is no longer a spoiler.
function constituencyExplanation(lesson, example) {
  const gold = goldFor(example);
  if (!gold?.tree) {
    return 'Every word hangs under the right head, and the phrase spans them in the right order.';
  }
  const parts = phraseParts(gold.tree);
  const head = parts.head ? `${parts.head.type} (${leafText(parts.head)})` : 'its head';
  if (!parts.parts.length) {
    return `The ${gold.tree.type} is just ${head}: nothing else hangs off it.`;
  }
  const others = parts.parts.map((m) => `${m.type} (${leafText(m)})`).join(', ');
  return `The ${gold.tree.type} spans ${others} and the head ${head}. `
    + (parts.modifierPhrase
      ? 'The modifiers hang off the phrase itself, flat around the head — the constituency is valid.'
      : 'The constituents sit in the right order under their head — the constituency is valid.');
}

// Before the first check: the target rule and the instructions that get the
// learner to it. Nothing that gives the answer away.
function diagnosticIdleState(lesson) {
  const card = el('div', 'validation-guidelines-card');
  card.appendChild(el('span', 'validation-card-label', 'Target rule'));
  card.appendChild(el('code', 'validation-rule', lesson.formula));
  card.appendChild(el('p', 'validation-instructions',
    'Use right-click to spawn constituent phrase boxes, then drag from connector dots '
    + 'to attach leaves. Click Check Tree when ready.'));
  return card;
}

// What the learner's own tree says: the leaves that hang free, the phrases
// that dominate nothing, a second root, a circular reference, and the words
// whose tag no longer matches the one SynTutor gave them.
function describeFindings() {
  const model = builderModel();
  const nodes = Object.values(model?.nodes || {});
  if (!nodes.length) return [];
  const notes = [];
  const words = nodes.filter((n) => n.kind === NODE.WORD);
  const phrases = nodes.filter((n) => n.kind === NODE.PHRASE);
  const detached = words.filter((n) => !n.parent);
  const empty = phrases.filter((n) => childrenOf(model, n.id).length === 0);
  // A second phrase box with nothing above it is a second tree; the words
  // waiting to be attached are reported as detached leaves instead.
  const roots = phrases.filter((n) => !n.parent);
  if (detached.length) {
    notes.push(`Detached leaves: ${detached
      .map((n) => `${n.tag || 'word'} (${n.text})`).join(', ')} — every word must hang under a phrase.`);
  }
  if (empty.length) {
    notes.push(`Empty phrases: ${empty.map((n) => n.type).join(', ')} — a phrase box must dominate something.`);
  }
  if (roots.length > 1) {
    notes.push(`More than one root: ${roots
      .map((n) => n.type).join(', ')} — the tree must hang under a single root.`);
  }
  const cycle = findCycle(model, nodes);
  if (cycle) {
    notes.push(`Circular reference: ${cycle} — a node cannot be its own ancestor.`);
  }
  const wrong = mismatchedTags(words);
  if (wrong.length) {
    notes.push(`Mismatched tags: ${wrong.join('; ')} — right-click the word to give it the tag SynTutor reads.`);
  }
  return notes;
}

// A node that is its own ancestor: the builder refuses such a connection, but
// a broken model still has to be reported.
function findCycle(model, nodes) {
  for (const node of nodes) {
    const seen = new Set();
    let cur = node.parent;
    while (cur) {
      if (cur === node.id) return `${node.type || node.text} (${node.text || node.type})`;
      if (seen.has(cur)) break;
      seen.add(cur);
      cur = model.nodes[cur]?.parent ?? null;
    }
  }
  return null;
}

// The words whose tag no longer matches the one SynTutor gave them.
function mismatchedTags(words) {
  const example = state.session?.seq[state.session.pos]?.example;
  const gold = example ? goldFor(example) : null;
  if (!gold?.leaves?.length) return [];
  const ordered = [...words].sort((a, b) => (a.x || 0) - (b.x || 0));
  const wrong = [];
  gold.leaves.forEach((leaf, i) => {
    const node = ordered[i];
    if (!node || !leaf.tag) return;
    const tag = node.tag || leaf.tag;
    if (tag !== leaf.tag) wrong.push(`${node.text}: ${tag} (SynTutor reads ${leaf.tag})`);
  });
  return wrong;
}

// Move between nodes. Entering Steps & Practice loads the first not-yet-built
// example so the canvas and its guide card are ready to follow; entering the
// Quiz starts the run, because that stage IS the quiz.
// Pick a section of a module-style lesson: load its first sample and re-render
// the LMS lesson panel around it.
function selectSection(lesson, i) {
  state.sectionIndex = Math.max(0, Math.min(i, lesson.sections.length - 1));
  const section = lesson.sections[state.sectionIndex];
  const first = section.examples.findIndex((e) => !state.done.has(`${lesson.type}:${e}`));
  state.exampleIndex = first < 0 ? 0 : first;
  renderLesson();
}

// The example a module-style lesson opens on: the first of the active section
// that has not been built yet.
function defaultExampleIndex(lesson) {
  const section = lesson.sections?.[state.sectionIndex];
  const list = section?.examples || lesson.examples || [];
  const first = list.findIndex((e) => !state.done.has(`${lesson.type}:${e}`));
  return first < 0 ? 0 : first;
}
function goLessonNode(lesson, page) {
  const target = Math.max(1, Math.min(page, LESSON_NODES.length));
  if (target === 2) {
    state.lessonPage = 2;
    if (lesson.sections) {
      const sectionIdx = lesson.sections.findIndex((s) =>
        s.examples.some((e) => !state.done.has(`${lesson.type}:${e}`)));
      selectSection(lesson, sectionIdx < 0 ? 0 : sectionIdx);
      return;
    }
    const first = lesson.examples.findIndex((e) => !state.done.has(`${lesson.type}:${e}`));
    showExample(lesson, first < 0 ? 0 : first);
    return;
  }
  if (target === 3) {
    state.lessonPage = 3;
    // The quiz stage is the quiz: opening it starts the run, so the learner
    // never lands on a dead "Start Quiz" screen.
    if (!state.session || state.session.quizLesson !== lesson.type) {
      startLessonQuiz(lesson);
      return;
    }
    closeStepGuide();
    closeGuideCard();
    renderLesson();
    return;
  }
  state.lessonPage = target;
  // Leaving Practice takes the example spotlight and its canvas card
  // with it; re-entering Node 2 reloads the example and reopens both.
  closeStepGuide();
  closeGuideCard();
  renderLesson();
}

function renderLesson() {
  const lesson = LESSONS.find((l) => l.type === state.lessonIndex);
  if (!lesson) return;
  if (lesson.sections) {
    renderModuleLesson(lesson);
    return;
  }
  // Leaving a module lesson for a single-unit lesson must also leave its
  // single-column sidebar layout behind.
  document.body.classList.remove('module-lesson', 'lesson-model');
  const host = $('#quizQuestHost');
  const guideHost = $('#lessonGuideHost');
  if (!host || !guideHost) return;
  const index = Math.max(0, Math.min(state.exampleIndex || 0, lesson.examples.length - 1));
  state.exampleIndex = index;
  state.lessonPage = Math.max(1, Math.min(state.lessonPage || 1, LESSON_NODES.length));
  const page = state.lessonPage;
  const example = lesson.examples[index];
  state.visitedPages.add(`${lesson.type}:${page}`);

  // The lesson view owns the upper-right pane: the Grammar Tutor's input
  // surface steps aside so only the lesson controls are left there.
  document.body.classList.add('lesson-view');

  // …and the canvas panel wears the lesson's own surface, so the three
  // panels of the workspace share one radius, one border and one colour.
  $('.canvas-wrap')?.classList.add('lesson-canvas-panel');

  // …and it owns the left canvas too: the Grammar Tutor's empty state is
  // hidden and any tree left over from an earlier analysis is wiped, so no
  // squished ghost tree can sit behind the lesson.
  takeOverCanvas();

  // The spotlight guide only belongs to the example it was opened on; a node
  // switch, example switch, or new lesson dismisses it. Plain re-renders (a
  // solved example refreshing the checkmarks) keep it alive.
  if (guide.open
    && (guide.lesson !== lesson.type || guide.example !== example || page !== 2)) {
    closeStepGuide();
  }

  host.innerHTML = '';
  const wrap = el('div', 'sq-lesson');

  // One header row in every stage: the book button and the lesson title on
  // the left, the stage stepper on the right.
  const head = el('header', 'panel-header-row');
  const headMain = el('div', 'panel-title-group');
  const book = el('button', 'panel-book-btn');
  book.type = 'button';
  book.title = 'Show all lesson modules';
  book.setAttribute('aria-label', 'Show all lesson modules');
  book.innerHTML = '<svg class="panel-book-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"></path><path d="M6 2v20"></path></svg>';
  book.addEventListener('click', () => openLessonsOverlay());
  headMain.appendChild(book);
  headMain.appendChild(el('h2', 'lesson-panel-title', lesson.title));
  head.appendChild(headMain);
  head.appendChild(renderLessonNodes(lesson, page));
  wrap.appendChild(head);

  // Only the current stage's controls live in the upper-right pane.
  wrap.appendChild(renderLessonStage(lesson, page, index, example));

  host.appendChild(wrap);

  // The stage content lives in the bottom pane, above the node inspector.
  guideHost.innerHTML = '';
  guideHost.appendChild(renderLessonBody(lesson, page, example));

  // The Concept stage shows the primary example's parse on the canvas: one
  // clean, centred reference tree instead of an empty canvas.
  if (page === 1) renderConceptCanvas(lesson);
  else hideConceptCanvas();

  // Keep an open spotlight guide in sync with the fresh DOM.
  if (guide.open) updateStepGuide();
}

// ---------------------------------------------------------------------------
// The Concept stage's reference tree
// ---------------------------------------------------------------------------
// Stage 1 shows what the lesson is about before the learner builds anything:
// the primary example, parsed by SynTutor itself and drawn once, centred and
// scaled to fit the canvas. A late answer never overwrites a newer one.
let conceptToken = 0;

async function renderConceptCanvas(lesson) {
  const example = lesson.examples[0];
  const token = ++conceptToken;
  const note = ensureConceptNote();
  if (note) note.hidden = true;
  if (!example) return;
  // The Concept stage shows the reference tree, so the canvas belongs to the
  // tree renderer again: the builder's canvas and its floating controls step
  // aside (the builder itself stays loaded, so returning to Steps & Practice
  // costs nothing).
  showConceptCanvas();
  try {
    // The gold parse is cached, so the practice stage loads it instantly.
    let gold = state.cache.get(example);
    if (!gold) {
      gold = await loadGold(example);
      state.cache.set(example, gold);
    }
    if (token !== conceptToken) return;   // a newer stage took over
    if (!gold?.tree) throw new Error('no tree');
    // The renderer draws the tree with the same layout it uses everywhere
    // else — centred, fitted to the canvas, never squashed.
    state.controller?.renderTree?.(gold.tree);
  } catch {
    if (token !== conceptToken) return;
    // No model to draw: show a clean, centred card instead of a distorted
    // tree or an empty canvas.
    state.controller?.renderTree?.(null);
    if (note) {
      note.querySelector('.lesson-canvas-formula').textContent = lesson.formula;
      note.querySelector('.lesson-canvas-example').textContent = `“${example}”`;
      note.hidden = false;
    }
  }
}

// Hand the canvas back to the tree renderer: the reference tree needs the
// visible canvas, and a canvas that was hidden while the builder was open has
// a stale backing store — the resize event re-fits it. The stage is a
// demonstration: the tree is read-only and the hint says so.
function showConceptCanvas() {
  const tree = document.getElementById('treeCanvas');
  const builder = document.getElementById('builderCanvas');
  const controls = document.getElementById('canvasControls');
  if (tree) tree.hidden = false;
  if (builder) builder.hidden = true;
  if (controls) controls.hidden = true;
  // Read-only: the learner may pan and zoom, but cannot pick or drag nodes.
  state.controller?.setCanvasInteractive?.(false);
  setHintBelowActions(false);
  setCanvasHint(CONCEPT_HINT);
  window.dispatchEvent(new Event('resize'));
}

// The fallback card for the Concept stage: a centred, undistorted summary of
// the structure the learner is about to build.
function ensureConceptNote() {
  const existing = document.getElementById('lessonCanvasNote');
  if (existing) return existing;
  const stage = document.querySelector('.canvas-stage');
  if (!stage) return null;
  const note = el('div', 'lesson-canvas-note');
  note.id = 'lessonCanvasNote';
  note.hidden = true;
  note.appendChild(el('span', 'lesson-canvas-label', 'Reference structure'));
  note.appendChild(el('code', 'lesson-canvas-formula'));
  note.appendChild(el('span', 'lesson-canvas-example'));
  note.appendChild(el('span', 'lesson-canvas-hint', 'You build this tree yourself in Steps & Practice.'));
  stage.appendChild(note);
  return note;
}

function hideConceptCanvas() {
  conceptToken += 1;
  const note = document.getElementById('lessonCanvasNote');
  if (note) note.hidden = true;
}

// ---------------------------------------------------------------------------
// Module lessons (Verb phrase): read-only model trees + LMS lesson panel
// ---------------------------------------------------------------------------
// A module-style lesson presents one scrolling column: subtype pills, the
// active subtype's title and definition, a live sentence explanation, and the
// section's sample sentences. Selecting a sample paints its parsed tree on the
// read-only #treeCanvas and updates the explanation above; there is no builder,
// no task card, and no practice mode in this view.

// One monotonic token guards every /api/parse request made for the lesson
// canvas. A late response for a previous example must never overwrite the
// tree the learner is looking at now.
let goldRequest = 0;

function renderModuleLesson(lesson) {
  const host = $('#quizQuestHost');
  const guideHost = $('#lessonGuideHost');
  if (!host || !guideHost) return;
  // Re-rendering after a sample switch must not jump the lesson column back to
  // the top, and keyboard focus should stay on the control that caused it.
  const scrollTop = host.scrollTop;
  const active = document.activeElement;
  const focusWasPill = Boolean(active?.classList?.contains('sq-section-pill'));
  const focusExample = active?.dataset?.exampleIndex ?? null;

  // The module never uses the legacy spotlight guide or its docked card.
  closeStepGuide();
  closeGuideCard();
  document.body.classList.add('lesson-view', 'module-lesson', 'lesson-model');
  host.innerHTML = '';
  guideHost.innerHTML = '';
  syncChatTitle(lesson);

  state.sectionIndex = Math.max(0, Math.min(state.sectionIndex || 0, lesson.sections.length - 1));
  const section = lesson.sections[state.sectionIndex];
  state.exampleIndex = Math.max(0, Math.min(state.exampleIndex || 0, lesson.examples.length - 1));
  const example = lesson.examples[state.exampleIndex];

  const wrap = el('div', 'sq-lesson sq-module');

  // Header: the way back to the library and the module title. The old mode
  // pill is gone because a module lesson now only ever shows model trees.
  const head = el('header', 'panel-header-row');
  const headMain = el('div', 'panel-title-group');
  const book = el('button', 'panel-book-btn');
  book.type = 'button';
  book.title = 'Show all lesson modules';
  book.setAttribute('aria-label', 'Show all lesson modules');
  book.innerHTML = '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>';
  book.addEventListener('click', () => openLessonsOverlay());
  headMain.appendChild(book);
  headMain.appendChild(el('h2', 'lesson-panel-title', lesson.title));
  head.appendChild(headMain);
  wrap.appendChild(head);

  wrap.appendChild(renderSubtypeNav(lesson));
  wrap.appendChild(renderOverviewPanel(section, example));
  wrap.appendChild(renderSamplesCard(lesson, section));

  host.appendChild(wrap);
  host.scrollTop = scrollTop;
  if (focusWasPill) {
    wrap.querySelector('.sq-section-pill.is-active')?.focus({ preventScroll: true });
  } else if (focusExample !== null) {
    wrap.querySelector(`.sq-sample-button[data-example-index="${focusExample}"]`)?.focus({ preventScroll: true });
  }
}

function renderSubtypeNav(lesson) {
  const nav = el('nav', 'sq-module-nav');
  nav.setAttribute('aria-label', `${lesson.title} subtypes`);
  const pills = el('div', 'sq-module-pills');
  pills.setAttribute('role', 'group');
  pills.setAttribute('aria-label', 'Choose a subtype');
  lesson.sections.forEach((section, i) => {
    const pill = el('button', i === state.sectionIndex ? 'sq-section-pill is-active' : 'sq-section-pill', section.name);
    pill.type = 'button';
    pill.title = section.title;
    pill.setAttribute('aria-pressed', String(i === state.sectionIndex));
    pill.addEventListener('click', () => selectSection(lesson, i));
    pills.appendChild(pill);
  });
  nav.appendChild(pills);
  return nav;
}

function renderOverviewPanel(section, example) {
  const panel = el('section', 'sq-module-overview');
  panel.appendChild(el('p', 'sq-module-eyebrow', 'Subtype'));
  panel.appendChild(el('h3', 'sq-module-title', section.title));
  panel.appendChild(el('p', 'sq-module-definition', section.detail));
  if (section.formula) panel.appendChild(renderFormula(section.formula));
  panel.appendChild(renderSentenceExplanation(section, example));
  return panel;
}

// Structural formula for the active verb-phrase subtype, shown below the
// definition and above the live sentence explanation. Acronyms expose a hover
// tooltip spelling out what they stand for.
const FORMULA_TERMS = {
  VP: 'Verb phrase',
  V: 'Verb (the main verb)',
  NP: 'Noun phrase',
  AP: 'Adjective phrase',
  PP: 'Prepositional phrase',
};
function renderFormula(formula) {
  const container = el('div', 'sq-module-formula');
  container.appendChild(el('div', 'sq-module-formula-label', 'Structural Formula:'));
  const text = el('div', 'sq-module-formula-text');
  text.innerHTML = formula.replace(/\b(VPV|VP|V|NP|AP|PP)\b/g, (m) => {
    const term = FORMULA_TERMS[m] || m;
    return `<span class="sq-acronym" data-term="${term}">${m}</span>`;
  });
  container.appendChild(text);
  return container;
}

// Position the fixed-position hover tooltip over each acronym so it escapes
// the canvas stacking context and always renders on top.
function positionAcronymTooltip(el) {
  const rect = el.getBoundingClientRect();
  el.style.setProperty('--ac-tooltip-left', `${rect.left + rect.width / 2}px`);
  el.style.setProperty('--ac-tooltip-top', `${rect.top}px`);
}
document.addEventListener('mouseover', (ev) => {
  const ac = ev.target.closest('.sq-acronym');
  if (!ac) return;
  positionAcronymTooltip(ac);
});

function renderSentenceExplanation(section, example) {
  const gold = state.cache.get(example);
  let text;
  let tone = '';
  if (state.goldLoading === example) {
    text = `Reading the parsed tree for ${quoteSurface(example)}...`;
    tone = ' is-status';
  } else if (state.goldError) {
    text = state.goldError;
    tone = ' is-error';
  } else if (!gold) {
    text = `The parsed tree for ${quoteSurface(example)} is not available yet.`;
    tone = ' is-status';
  } else {
    text = describeSentence(gold, section, example);
  }
  const explanation = el('p', `sq-module-explanation${tone}`, text);
  explanation.setAttribute('aria-live', 'polite');
  return explanation;
}

function renderSamplesCard(lesson, section) {
  const card = el('section', 'sq-module-samples');
  const head = el('header', 'sq-module-section-head');
  head.appendChild(el('h3', 'sq-module-section-title', 'Sample sentences'));
  const count = section.examples.length;
  head.appendChild(el('span', 'sq-module-section-count', `${count} ${count === 1 ? 'example' : 'examples'}`));
  card.appendChild(head);

  const list = el('ul', 'sq-sample-list');
  section.examples.forEach((sentence) => {
    const index = lesson.examples.indexOf(sentence);
    const isActive = index === state.exampleIndex;
    const item = el('li', 'sq-sample-item');
    const button = el('button', isActive ? 'sq-sample-button is-active' : 'sq-sample-button');
    button.type = 'button';
    button.dataset.exampleIndex = String(index);
    button.setAttribute('aria-current', isActive ? 'true' : 'false');
    button.title = `Show the model tree for ${quoteSurface(sentence)}`;
    button.appendChild(el('span', 'sq-sample-text', sentence));
    const chevron = el('span', 'sq-sample-chevron');
    chevron.setAttribute('aria-hidden', 'true');
    chevron.innerHTML = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 6 15 12 9 18"></polyline></svg>';
    button.appendChild(chevron);
    button.addEventListener('click', () => openModelExample(lesson, sentence));
    item.appendChild(button);
    list.appendChild(item);
  });
  card.appendChild(list);
  return card;
}

async function openModelExample(lesson, example) {
  const token = ++goldRequest;
  state.goldError = null;
  state.goldLoading = null;
  const index = lesson.examples.indexOf(example);
  if (index >= 0) state.exampleIndex = index;
  setInputSentence(example);
  syncChatTitle(lesson);
  renderLesson();

  let gold = state.cache.get(example);
  if (!gold) {
    // Never leave the previous sample's tree on screen while this one loads.
    state.controller?.clearModelTree?.({ force: true });
    state.goldLoading = example;
    renderLesson();
    try {
      gold = await loadGold(example);
    } catch (err) {
      if (token !== goldRequest) return;
      state.goldLoading = null;
      state.goldError = `Could not load the parsed tree (${err.message}).`;
      renderLesson();
      return;
    }
    state.cache.set(example, gold);
  }
  if (token !== goldRequest) return;
  state.goldLoading = null;
  state.controller?.showModelTree?.(gold.payload, findVpId(gold.payload));
  renderLesson();
}

// Resolve the node whose edge is the clause predicate; selecting it gives the
// model view a visible VP band without turning the tree into an editor.
function findVpId(payload) {
  const details = Object.values(payload?.node_details || {});
  const predicate = details.find((d) => d.type === 'VP' && d.constraint === 'C-PREDICATE');
  const vp = predicate || details.find((d) => d.type === 'VP');
  return vp?.id || null;
}

// ---------------------------------------------------------------------------
// Sentence explanation: turn the parsed tree into a short plain-language lesson
// ---------------------------------------------------------------------------
const VERB_POS = new Set(['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD', 'AUX']);
const PUNCT_POS = new Set(['.', ',', ':', ';', '``', "''", '-LRB-', '-RRB-', 'HYPH', 'NFP', 'SYM']);
const AUX_SURFACES = new Set([
  'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
  'have', 'has', 'had', 'do', 'does', 'did',
  'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must', 'ought',
  "'m", "'s", "'re", "'ve", "'d",
]);
const PHRASE_LABELS = {
  NP: 'noun phrase',
  VP: 'verb phrase',
  PP: 'prepositional phrase',
  ADJP: 'adjective phrase',
  ADVP: 'adverb phrase',
  S: 'clause',
  SBAR: 'subordinate clause',
  SQ: 'question clause',
  SBARQ: 'wh-question clause',
  WHNP: 'wh-noun phrase',
  WHADVP: 'wh-adverb phrase',
  WHPP: 'wh-prepositional phrase',
  QP: 'quantifier phrase',
  PRT: 'particle',
  FRAG: 'fragment',
  INTJ: 'interjection',
};

function cleanSurface(value) {
  return String(value ?? '').replace(/\s+/g, ' ').trim();
}

function quoteSurface(value) {
  const text = cleanSurface(value);
  return text ? `\u201C${text}\u201D` : 'an empty phrase';
}

function listText(items) {
  const values = items.filter(Boolean);
  if (!values.length) return '';
  if (values.length === 1) return values[0];
  if (values.length === 2) return `${values[0]} and ${values[1]}`;
  return `${values.slice(0, -1).join(', ')}, and ${values[values.length - 1]}`;
}

function isLeafNode(node) {
  return Boolean(node) && !(node.children && node.children.length);
}

function nodePos(node) {
  return node?.pos || node?.type || '';
}

function isVerbLeaf(node) {
  return isLeafNode(node) && VERB_POS.has(nodePos(node));
}

function isPunctLeaf(node) {
  return isLeafNode(node) && PUNCT_POS.has(nodePos(node));
}

function isAuxForm(node) {
  const pos = nodePos(node);
  if (pos === 'MD' || pos === 'AUX') return true;
  return AUX_SURFACES.has(cleanSurface(node?.surface).toLowerCase());
}

// Follow the auxiliary VP chain down to the VP that owns the main verb. A
// nested VP is only treated as an auxiliary chain when the outer VP's direct
// verb leaves are all auxiliaries (has eaten, was being chased); an infinitival
// complement such as "wanted to leave" is therefore not mistaken for one.
function headVpNode(gold, vpId) {
  const nodes = gold?.payload?.nodes || {};
  let node = nodes[vpId];
  const seen = new Set();
  while (node && !seen.has(node.id)) {
    seen.add(node.id);
    const children = node.children || [];
    const directVerbs = children.filter(isVerbLeaf);
    const nestedVp = children.find((child) => child.type === 'VP' && !isLeafNode(child));
    if (nestedVp && directVerbs.length && directVerbs.every(isAuxForm)) {
      node = nestedVp;
      continue;
    }
    break;
  }
  return node;
}

function mainVerbLeaf(head) {
  if (!head) return null;
  const direct = (head.children || []).filter(isVerbLeaf);
  if (direct.length) return direct[direct.length - 1];
  let found = null;
  const walk = (node) => {
    for (const child of node.children || []) {
      if (isVerbLeaf(child)) found = child;
      else walk(child);
    }
  };
  walk(head);
  return found;
}

function verbLeavesUnder(gold, vpId) {
  const root = gold?.payload?.nodes?.[vpId];
  const out = [];
  const walk = (node) => {
    if (!node) return;
    if (isVerbLeaf(node)) {
      out.push(node);
      return;
    }
    for (const child of node.children || []) walk(child);
  };
  walk(root);
  return out.sort((a, b) => (a.span?.[0] ?? 0) - (b.span?.[0] ?? 0));
}

function auxiliaryLeaves(gold, vpId, main) {
  if (!main) return [];
  const mainStart = main.span?.[0] ?? 0;
  return verbLeavesUnder(gold, vpId)
    .filter((leaf) => leaf.id !== main.id && (leaf.span?.[0] ?? 0) < mainStart);
}

// The phrase-level children that follow the main verb: objects, complements,
// particles, and modifiers, in reading order.
function componentNodes(head, main) {
  if (!head) return [];
  const mainEnd = main?.span?.[1] ?? -1;
  return (head.children || [])
    .filter((child) => !isLeafNode(child) && !isPunctLeaf(child))
    .filter((child) => (child.span?.[0] ?? 0) >= mainEnd)
    .sort((a, b) => (a.span?.[0] ?? 0) - (b.span?.[0] ?? 0));
}

function describeNode(node) {
  const label = PHRASE_LABELS[node?.type] || 'phrase';
  return `the ${label} ${quoteSurface(node?.surface)}`;
}

function describeNodeList(nodes) {
  return listText(nodes.map(describeNode));
}

function describeSentence(gold, section, example) {
  const details = Object.values(gold?.payload?.node_details || {});
  const vpDetail = details.find((detail) => detail.type === 'VP' && detail.constraint === 'C-PREDICATE')
    || details.find((detail) => detail.type === 'VP');
  if (!vpDetail) {
    return `In ${quoteSurface(example)}, the model tree is ready, but no verb phrase was found to describe.`;
  }

  const vpSurface = cleanSurface(vpDetail.surface) || example;
  const head = headVpNode(gold, vpDetail.id);
  const main = mainVerbLeaf(head);
  const auxiliaries = auxiliaryLeaves(gold, vpDetail.id, main);
  const components = componentNodes(head, main);
  const linking = /linking|copular/i.test(section?.name || '');
  const hasObject = section?.hasObject !== false;
  const sentenceText = cleanSurface(example);
  const sentenceWithPunctuation = /[.!?]$/.test(sentenceText) ? sentenceText : `${sentenceText}.`;
  const parts = [
    `The sentence is ${quoteSurface(sentenceWithPunctuation)} The verb phrase is ${quoteSurface(vpSurface)} \u2014 the predicate of the clause.`,
  ];

  if (main) {
    if (auxiliaries.length) {
      const auxList = listText(auxiliaries.map((leaf) => quoteSurface(leaf.surface)));
      if (auxiliaries.length === 1) {
        parts.push(`The auxiliary verb is ${auxList}; it helps the main verb ${quoteSurface(main.surface)}.`);
      } else {
        parts.push(`The auxiliary verbs are ${auxList}; together they help the main verb ${quoteSurface(main.surface)}.`);
      }
    } else {
      parts.push(`The main verb is ${quoteSurface(main.surface)}.`);
    }
  } else {
    parts.push('The parse does not identify a main verb in this phrase.');
  }

  if (!hasObject && linking) {
    if (components.length) {
      const complement = cleanSurface(components.map((node) => node.surface).join(' '));
      parts.push(`The linking verb is followed by the subject complement ${quoteSurface(complement)}. No direct object follows; the complement describes the subject.`);
    } else {
      parts.push('No subject complement follows the linking verb in this parse.');
    }
  } else if (!hasObject) {
    if (components.length) {
      parts.push(`The supporting ${components.length === 1 ? 'component is' : 'components are'} ${describeNodeList(components)}. There is no object or complement, so the verb phrase is intransitive.`);
    } else {
      parts.push('There is no object, complement, or supporting component, so the verb phrase is intransitive.');
    }
    if (!auxiliaries.length) parts.push('No auxiliary verbs are present.');
  } else {
    const nounPhrases = components.filter((node) => node.type === 'NP');
    const prepositional = components.filter((node) => node.type === 'PP');
    const others = components.filter((node) => node.type !== 'NP' && node.type !== 'PP');
    const subtype = section?.name || '';

    if (/ditransitive/i.test(subtype)) {
      if (nounPhrases.length >= 2) {
        parts.push(`It takes two objects: the indirect object is ${describeNode(nounPhrases[0])}, and the direct object is ${describeNode(nounPhrases[1])}.`);
        const extras = [...nounPhrases.slice(2), ...prepositional, ...others];
        if (extras.length) {
          parts.push(`The supporting ${extras.length === 1 ? 'component is' : 'components are'} ${describeNodeList(extras)}.`);
        }
      } else if (nounPhrases.length === 1 && prepositional.length) {
        parts.push(`Its direct object is ${describeNode(nounPhrases[0])}, and the prepositional phrase ${quoteSurface(prepositional[0].surface)} names the recipient.`);
        const extras = [...prepositional.slice(1), ...others];
        if (extras.length) {
          parts.push(`The supporting ${extras.length === 1 ? 'component is' : 'components are'} ${describeNodeList(extras)}.`);
        }
      } else if (nounPhrases.length === 1) {
        parts.push(`Its direct object is ${describeNode(nounPhrases[0])}.`);
      } else {
        parts.push('This parse does not show a direct object after the verb.');
      }
    } else if (/complex transitive/i.test(subtype)) {
      // Benepar often wraps the object + object complement in a small-clause
      // S ("considered [the workflow inefficient]"). Unwrap that S so the
      // object and the complement can be named separately.
      const expanded = components.flatMap((node) => (
        node.type === 'S' ? (node.children || []).filter((child) => !isPunctLeaf(child)) : [node]
      ));
      const direct = expanded.find((node) => node.type === 'NP') || expanded[0] || null;
      const complement = direct
        ? expanded.find((node) => node !== direct
          && ['ADJP', 'ADVP', 'NP', 'PP'].includes(node.type)
          && (node.span?.[0] ?? 0) >= (direct.span?.[1] ?? 0))
        : null;
      if (direct) parts.push(`Its direct object is ${describeNode(direct)}.`);
      if (complement) {
        parts.push(`The object complement is ${describeNode(complement)}; it describes that object.`);
      } else {
        parts.push('This parse does not show a separate object complement.');
      }
      const extras = expanded.filter((node) => node !== direct && node !== complement);
      if (extras.length) {
        parts.push(`The supporting ${extras.length === 1 ? 'component is' : 'components are'} ${describeNodeList(extras)}.`);
      }
    } else {
      const direct = nounPhrases[0] || components[0] || null;
      if (direct) parts.push(`Its direct object is ${describeNode(direct)}.`);
      else parts.push('This parse does not show a direct object after the verb.');
      const extras = components.filter((node) => node !== direct);
      if (extras.length) {
        parts.push(`The supporting ${extras.length === 1 ? 'component is' : 'components are'} ${describeNodeList(extras)}.`);
      }
    }
    if (!auxiliaries.length) parts.push('No auxiliary verbs are present.');
  }

  return parts.join(' ');
}


// Show one example of the open lesson: sync the top input, re-render the
// lesson panel (so its step-by-step guide matches), then load it on the canvas.
function showExample(lesson, index) {
  const last = lesson.examples.length - 1;
  const i = Math.max(0, Math.min(index, last));
  // A new example starts at its first build step.
  guide.step = 0;
  const pending = startChallenge(lesson, lesson.examples[i]);
  // The spotlight opens on the first step, so the learner sees both what to
  // do and where on the canvas it happens.
  openStepGuide(lesson, 0);
  return pending;
}

// The lesson's quiz: build every example of this lesson, in order. It is the
// lesson's final page — the spotlight guide has no place once the quiz starts.
function startLessonQuiz(lesson) {
  closeStepGuide();
  closeGuideCard();
  closeQuizView();
  $('#appSidebarBackdrop')?.classList.remove('active');
  // The quiz stage is the quiz: the builder chrome and the hint follow it,
  // whichever way the learner got here.
  state.lessonPage = 3;
  startSession(lesson.examples.map((example) => ({ lesson, example })), 0, lesson.type);
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

// Keep the workspace controller informed of which lesson/quiz is active
// ("NP · Noun phrase" in a lesson, "Quiz · NP" during a session). main.js
// restores the last analysed sentence via clearActiveLesson().
function syncChatTitle(lesson) {
  const ctl = state.controller;
  if (!ctl || typeof ctl.setChatTitle !== 'function') return;
  // A module lesson labels itself by title alone, so no acronym ever surfaces
  // in the workspace title (e.g. "Verb phrase", never "VP · Verb phrase").
  const label = lesson.sections ? lesson.title : `${lesson.type} · ${lesson.title}`;
  ctl.setChatTitle(state.session ? `Quiz · ${label}` : label);
}

async function startChallenge(lesson, example, onDone) {
  if (state.view === 'lesson') {
    const i = lesson.examples.indexOf(example);
    if (i >= 0) state.exampleIndex = i;
  }
  setInputSentence(example);
  syncChatTitle(lesson);
  refreshLessonPanel();

  closeQuizView();
  $('#appSidebarBackdrop')?.classList.remove('active');

  // Lessons and quizzes build in place: keep the sidebar highlight on the tab
  // the learner came from instead of switching to Syntax Builder.
  const sidebarView = state.view === 'lesson' ? 'lessons' : 'quiz';
  // Inside a lesson there are two builder stages: the practice stage (Node 2)
  // and the quiz stage (Node 3). Both keep the canvas controls and the
  // affordance hint up; only the practice stage shows the step guide.
  const inLesson = state.view === 'lesson';
  const practice = inLesson && state.lessonPage === 2 && !state.session;
  const quiz = inLesson && state.lessonPage === 3;
  let gold = state.cache.get(example);
  let reset = true;
  if (!gold) {
    openBuilderView({
      challenge: { kind: 'full', target: example, hint: lesson.rule, gold: [], goldTree: null },
      reset,
      sidebarView,
      practice,
      quiz,
      hint: practice ? PRACTICE_HINT : QUIZ_HINT,
    });
    reset = false;
    try {
      gold = await loadGold(example);
    } catch (err) {
      setBuilderHint(`Could not reach SynTutor's model: ${err.message}`);
      return;
    }
    state.cache.set(example, gold);
    // The parse is here now: the analysis panel can show the breakdown of
    // this example (its leaves, its head, its modifiers).
    refreshLessonPanel();
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
    quiz,
    hint: practice ? PRACTICE_HINT : QUIZ_HINT,
    onComplete: (ok) => {
      record(lesson, example, ok);
      // The quiz stage knows whether the current question is answered, so it
      // can offer "Next Question" instead of "Check tree".
      if (state.session) state.session.answered = ok;
      refreshLessonPanel();
      onDone?.(ok);
    },
  });
  // The canvas belongs to the learner's tree: the step-by-step guide lives in
  // the upper panel now, so no pill floats over the bottom-left of the canvas.
  closeGuideCard();
}

function record(lesson, example, ok) {
  if (!ok) return;
  const key = `${lesson.type}:${example}`;
  const firstTime = !state.done.has(key);
  state.done.add(key);
  // A built example counts as seen: its tutorial overlay does not come back.
  state.seenExamples.add(key);
  if (isGuestSession()) {
    // A guest's progress waits in local storage; it follows them to their
    // account the moment they create one. An example is worth its XP once.
    if (firstTime) recordGuestProgress({ xp: XP_PER_CORRECT, lesson: lesson.type });
    return;
  }
  const progress = state.controller?.progress;
  if (progress && typeof progress.trackCompletion === 'function') {
    try { progress.trackCompletion({ ruleId: lesson.type, perfect: true }); } catch { /* ignore */ }
  }
}

// Clear the lesson view (controls in #quizQuestHost, page content in
// #lessonGuideHost) and return the workspace to standard SynTutor mode.
// Called when leaving lesson mode: new session, standalone Syntax Builder,
// standalone quiz, or builder close.
export function clearActiveLesson() {
  closeStepGuide();
  closeGuideCard();
  closeLessonsOverlay();
  closeSubpanel();
  // A module lesson may have left its read-only tree in the renderer even while
  // Practice hid the canvas. Drop it here as well as in teardown so closing the
  // builder cannot reveal a ghost tree; only show the empty state when a lesson
  // was actually open (opening a side panel must leave the tutor's tree alone).
  const wasLesson = document.body.classList.contains('lesson-view');
  const clearedModel = state.controller?.clearModelTree?.() === true;
  if (wasLesson || clearedModel) {
    document.querySelector('#emptyTreeState')?.classList.remove('hidden');
  }
  hideConceptCanvas();
  state.view = 'lessons';
  state.lessonIndex = null;
  state.exampleIndex = 0;
  state.lessonPage = 1;
  state.sectionIndex = 0;
  state.goldLoading = null;
  state.goldError = null;
  // Invalidate any in-flight gold request so it cannot paint a canvas after
  // the lesson has closed.
  goldRequest += 1;
  const modelBtn = $('#builderModel');
  if (modelBtn) modelBtn.hidden = true;
  document.body.classList.remove('lesson-model', 'lesson-practice', 'module-lesson');
  // Hand the upper-right pane back to the Grammar Tutor.
  document.body.classList.remove('lesson-view');
  // …and the canvas panel with it: it wears the lesson's surface only while
  // a lesson is open.
  $('.canvas-wrap')?.classList.remove('lesson-canvas-panel');
  const host = $('#quizQuestHost');
  if (host) host.innerHTML = '';
  const guideHost = $('#lessonGuideHost');
  if (guideHost) guideHost.innerHTML = '';
  // …and the canvas with it: the lesson's reference tree goes away and the
  // Grammar Tutor's empty-canvas prompt comes back.
  state.controller?.clearCanvas?.();
  setEmptyStateHidden(false);
  // Restore the chat title to whatever sentence the workspace last analysed.
  const ctl = state.controller;
  if (ctl && typeof ctl.setChatTitle === 'function') {
    ctl.setChatTitle(typeof ctl.lastChatTitle === 'function' ? ctl.lastChatTitle() : '');
  }
}

// Re-render the active lesson panel so `state.done` checkmarks stay current
// as examples are solved.
function refreshLessonPanel() {
  if (state.view === 'lesson') renderLesson();
}

// ---------------------------------------------------------------------------
// Interactive step guide — a spotlight that points at what each step means
// ---------------------------------------------------------------------------
// A fixed spotlight ring (pointer-events: none) highlights the canvas region,
// word row, phrase box, or connector dot the current step talks about; the
// learner can still right-click, drag, and re-route on the canvas while
// following along. A rAF loop keeps the ring glued to its target while the
// canvas pans, zooms, or the boxes move. The step itself is spelled out in
// the upper panel, so the canvas keeps nothing but the learner's tree.
const guide = { open: false, step: 0, lesson: null, example: null, raf: 0 };

function ensureStepGuideDom() {
  if ($('#stepGuide')) return;
  const wrap = el('div', 'step-guide');
  wrap.id = 'stepGuide';
  wrap.hidden = true;
  wrap.innerHTML = '<div class="step-guide-ring" aria-hidden="true"></div>';
  document.body.appendChild(wrap);
}

// The key of one example inside a lesson.
function exampleKey(lesson, example) {
  return `${lesson.type}:${example}`;
}

// Has the learner already walked through this example? A revisited example
// keeps the canvas clean: the walk-through is not replayed on a later visit.
function exampleSeen(lesson, example) {
  return state.seenExamples.has(exampleKey(lesson, example));
}

function markExampleSeen(lesson, example) {
  state.seenExamples.add(exampleKey(lesson, example));
}

// The canvas card is gone — the step guide lives in the upper panel now — but
// every caller that used to close it keeps working.
function closeGuideCard() {
  const card = $('#canvasGuideCard');
  if (card) card.hidden = true;
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

// Push the guide state into the canvas card and the stage's own views. The
// ring's position is interpolated by the rAF loop, so this only syncs the
// chrome: the card prompt, the step pager and the active step.
function updateStepGuide() {
  const lesson = LESSONS.find((l) => l.type === guide.lesson);
  if (!lesson) return closeStepGuide();
  // The walk-through is over on the final step: the canvas belongs to the
  // learner's tree again — and the example counts as seen, so it is not
  // replayed on a later visit.
  if (guide.step >= lesson.steps.length - 1) {
    markExampleSeen(lesson, guide.example ?? lesson.examples[0]);
  }
  updateStepUI(lesson);
}

// One frame of the spotlight: resolve the step's target and park the ring on
// it. No CSS transitions on position — the rAF loop is the interpolation, and
// it tracks the target as the canvas pans, zooms, or the boxes move.
function guideLoopFrame() {
  guide.raf = 0;
  if (!guide.open) return;
  const lesson = LESSONS.find((l) => l.type === guide.lesson);
  const wrap = $('#stepGuide');
  if (!lesson || !wrap) return closeStepGuide();
  const ring = wrap.querySelector('.step-guide-ring');
  const box = canvasGuideBox(guideTargetFor(lesson.steps[guide.step] || ''))
    || canvasGuideBox({ kind: 'canvas' });
  if (box) {
    ring.style.display = '';
    ring.style.left = `${Math.round(box.left - 6)}px`;
    ring.style.top = `${Math.round(box.top - 6)}px`;
    ring.style.width = `${Math.round(box.width + 12)}px`;
    ring.style.height = `${Math.round(box.height + 12)}px`;
  } else {
    // No target (canvas hidden): dim nothing and keep the learner's view clear.
    ring.style.display = 'none';
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
  // A rapid second click (or a task started while the model is loading) must
  // share the first request instead of firing another identical parse.
  const pending = state.pendingGold.get(sentence);
  if (pending) return pending;
  const request = (async () => {
    const res = await fetch('/api/parse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: sentence }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const payload = await res.json();
    const tree = apiTree(payload.tree);
    return { tree, leaves: leavesWithTags(tree), payload };
  })();
  state.pendingGold.set(sentence, request);
  try {
    return await request;
  } finally {
    state.pendingGold.delete(sentence);
  }
}

// Reduce /api/parse's node tree to the {type, children|leaf, surface} shape the
// comparison + leaf helpers expect. The node ids come along: the renderer
// needs them to lay a tree out.
function apiTree(node) {
  if (!node) return null;
  const kids = node.children;
  if (!kids || kids.length === 0) {
    return { type: node.type, id: node.id, leaf: true, surface: node.surface ?? '' };
  }
  return { type: node.type, id: node.id, children: kids.map(apiTree) };
}

function setBuilderHint(msg) {
  const hint = $('#builderHint');
  // The hint floats on its own (outside the action cluster), so it has to be
  // unhidden explicitly for the message to be readable.
  if (hint) { hint.textContent = msg; hint.className = 'builder-hint builder-hint-no'; hint.hidden = false; }
}

// Whenever the builder closes, drop any active lesson view so a stale lesson
// panel never survives a return to normal SynTutor or a standalone Syntax
// Builder session.
setBuilderCloseHandler(clearActiveLesson);

// The builder reports every live check; the lesson's diagnostics panel shows
// that verdict under the question.
setCheckResultHandler((message, kind) => {
  state.checkStatus = { message, kind };
  updateValidationStatus();
});

// …and every change to the tree itself, so the findings (detached leaves,
// empty phrases, a second root) follow the learner while they build.
setModelChangeHandler(() => {
  if (state.view === 'lesson' && state.lessonPage === 3) updateValidationStatus();
});
