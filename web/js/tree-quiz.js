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

import { openBuilderView, closeBuilderView, setBuilderCloseHandler, builderModel, canvasGuideBox } from './syntax-builder-ui.js';
import { leavesWithTags, NODE, PHRASE_NODE_TYPES } from './syntax-builder.js';

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
};

// The textbook, in order. `type` is the official parser label; `rule` is the
// one-line "how to build it" summary used as the in-canvas hint; `detail` is
// the in-depth explanation (role, head, modifiers/complements, recognition);
// `steps` is the numbered guide for assembling the example's tree on canvas.
const LESSONS = [
  {
    type: 'NP', title: 'Noun phrase', group: 'Phrases',
    summary: 'Names a person, thing, or idea. It is built around a noun or pronoun head, with words like determiners and adjectives describing it.',
    rule: 'A noun phrase keeps its modifiers flat around the noun head: determiner or possessive, then any adjectives, then the noun - all direct children of one NP. So "the big cat" is (NP (DT the) (JJ big) (NN cat)).',
    detail: 'A noun phrase names a person, thing, or idea. Its head is a noun (NN, NNS, NNP) or a pronoun (PRP), and the phrase serves as the subject or object of a clause. Determiners (DT), possessives (PRP$) and adjectives (JJ/JJR/JJS) sit in front of the head as plain sister leaves - SynTutor does not wrap them in an adjective box, so "the big cat" is a flat NP over DT + JJ + NN. A prepositional phrase completes the noun from behind, and when it brings its own object the parser nests a small inner NP: "a student of physics" is (NP (NP (DT a) (NN student)) (PP (IN of) (NP (NNS physics)))). To recognize an NP, ask "who or what?" about the clause verb - the answer is the NP.',
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
    summary: 'Describes a quality or attribute. It is built around an adjective head, often with a degree word in front or a phrase completing it.',
    rule: 'An adjective phrase heads on an adjective: an optional degree adverb in front and an optional PP after it - (RB) + JJ + (PP), all direct children of one ADJP.',
    detail: 'An adjective phrase describes a quality and is headed by an adjective (JJ, JJR, JJS). It works either attributively, inside a noun phrase ("the very happy child"), or predicatively, as the complement of a linking verb ("she is very happy"). A degree adverb (RB) modifies the head from in front and a prepositional phrase (PP) completes it from behind - both attach directly to the ADJP as sister leaves: "very happy" is (ADJP (RB very) (JJ happy)) and "fond of music" is (ADJP (JJ fond) (PP (IN of) (NP (NN music)))). Recognize it by asking "what kind?" or "how ...?" about a noun: the head is the last adjective of the phrase.',
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
    summary: 'Tells how, when, where, or to what degree. It is built around an adverb head, sometimes with a degree word in front.',
    rule: 'An adverb phrase heads on an adverb, with an optional degree adverb in front: (RB) + ADV, both direct children of one ADVP.',
    detail: 'An adverb phrase tells how, when, where, or to what degree, and its head is the last adverb of the phrase (RB, RBR, RBS). A degree adverb (RB) stands in front of the head as a sister leaf - "very quickly" is (ADVP (RB very) (RB quickly)) - and the pair modifies verbs, adjectives, or other adverbs ("runs very quickly"). Some adverb phrases act as clausal adjuncts ("rarely does he complain"). To recognize one, ask "how?", "when?", or "where?" about the verb or adjective it attaches to.',
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
    summary: 'Shows a relationship such as place, time, or manner. It is a preposition followed by the noun phrase it relates to.',
    rule: 'A prepositional phrase is a preposition followed by its noun-phrase object: IN → NP. So "in the garden" is (PP (IN in) (NP (DT the) (NN garden))).',
    detail: 'A prepositional phrase is headed by a preposition (IN) and always takes a noun-phrase object (NP). It usually expresses place, time, manner, or possession ("in the garden", "of physics") and attaches to the word it modifies - a noun, verb, or adjective. The preposition is the head and comes first; everything after it forms the object NP, which may be flat ("on the small table" keeps DT + JJ + NN directly under the NP) or a bare noun ("of physics" is an NP over NN alone). Recognize it by the leading preposition: a phrase that begins with in, on, of, to, or with is almost certainly a PP with the pattern IN → NP.',
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
    summary: 'Expresses an amount or quantity. It is built around a number head, such as "more than five".',
    rule: 'A quantifier phrase expresses an amount around a number head: (JJR) + (IN) + CD, sitting inside a noun phrase - "more than five" is (QP (JJR More) (IN than) (CD five)).',
    detail: 'A quantifier phrase expresses an amount or quantity. Its head is a cardinal number (CD), often modified by a comparative (JJR, e.g. "more") and linked by a comparative preposition (IN, e.g. "than"); all three words hang directly under the QP. Quantifier phrases sit inside noun phrases ("more than five people" puts the QP in front of the noun) or act as measure expressions in their own right. Recognize one when the phrase answers "how many?" or "how much?" and ends in a number.',
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
    summary: 'A complete sentence-level unit. It pairs a subject with a predicate and can stand alone as a grammatical sentence.',
    rule: 'A clause pairs a subject noun phrase with a predicate verb phrase under one S box, and keeps the sentence-final punctuation as its last child: NP → VP → (.).',
    detail: 'A clause (S) is the complete sentence-level unit: it pairs a subject noun phrase with a predicate verb phrase (NP → VP), and SynTutor keeps the sentence-final punctuation - (. .) or (. ?) - as a third child of the S. The subject is what the sentence is about; the VP says something about it, and the verb inside the VP determines which complements are needed. Recognize a full clause by that subject-predicate pairing - unlike a fragment, it can stand alone as a grammatical sentence.',
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
    summary: 'A question that expects a yes or no answer. Its auxiliary verb moves in front of the subject.',
    rule: 'A yes/no question inverts the auxiliary and the subject: fronted AUX, then the subject NP, then the VP - "Is it raining?" is (SQ (VBZ Is) (NP (PRP it)) (VP (VBG raining)) (. ?)).',
    detail: 'A yes/no question (SQ) is a clause whose auxiliary has moved in front of the subject ("Is it raining?", "Did she leave?"). It expects a yes or no answer, so no wh-phrase is involved; the pattern is AUX → NP → VP with the auxiliary or modal at the very front and the subject directly after it, plus the question mark on a standalone question. A copula may carry the whole predicate ("Where is the cat?" leaves SQ with just AUX + NP), and when the subject is the wh-word of a higher question it sits outside ("Who ate the cake?" keeps only the VP inside SQ). Inside a wh-question the same SQ nests under SBARQ and the question mark belongs to the SBARQ instead. Recognize one by that inverted order - verb before subject - usually ending in a question mark.',
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
    summary: 'A question that asks for missing information. It opens with a wh-word followed by an inverted clause.',
    rule: 'A wh-question stacks three pieces under one SBARQ box: the fronted wh-phrase, an inner SQ with the inverted clause, and the question mark.',
    detail: 'A wh-question (SBARQ) begins with a wh-phrase - a wh-noun phrase (WHNP), wh-adjective phrase, wh-adverb phrase (WHADVP), or wh-prepositional phrase (WHPP) - followed by an inverted clause (SQ) whose auxiliary has moved past the subject, then the question mark as the final child: "What did you say?" is (SBARQ (WHNP (WP What)) (SQ (VBD did) (NP (PRP you)) (VP (VB say))) (. ?)). Wh-questions ask for missing information, the wh-word is normally the first word, and the punctuation sits above the SQ, not inside it. Recognize one by the fronted wh-word plus subject-auxiliary inversion, with a question mark at the end.',
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
    summary: 'A clause introduced by a word like "because" or "that". It cannot stand alone and fills a role inside a larger sentence.',
    rule: 'A subordinate clause is a subordinator plus its own clause under one SBAR box: IN/WDT/WP → S - "because he left" is (SBAR (IN because) (S (NP (PRP he)) (VP (VBD left)))).',
    detail: 'A subordinate clause (SBAR) is a clause introduced by a complementizer or relative pronoun (IN/WDT/WP, e.g. "because", "that", "which") with a full clause (S) beneath it. It does not stand alone; it fills a role inside a larger sentence - the complement of a verb ("I think that she knows") or a modifier of a noun ("the book which I saw" opens its SBAR with a WHNP, as does "which I saw"). The introducer is the first child of the SBAR and the S box follows it. Recognize it by the leading subordinator followed by its own subject-predicate clause.',
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
    summary: 'A phrase that names the unknown person or thing a question asks about, built on a word like "which" or "who".',
    rule: 'A wh-noun phrase begins with a wh-word and carries its noun beside it: WDT/WP (+ N) under one WHNP - "which book" is (WHNP (WDT which) (NN book)).',
    detail: 'A wh-noun phrase (WHNP) is a noun phrase built on a wh-word: a wh-determiner (WDT, "which/what") or wh-pronoun (WP, "who/whom") plus the noun it determines when there is one. It names the unknown person or thing a question asks about ("which book", "what color") and usually serves as the fronted phrase of a wh-question, where it fills the subject role - "Who ate the cake?" then keeps the whole SQ down to its VP - or the object of a preposition. A lone wh-pronoun is a WHNP of its own. Recognize it by the wh-word at its left edge, with or without a following noun.',
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
    summary: 'A phrase that asks "how …?" about a quality, pairing the word "how" with an adjective, as in "how old".',
    rule: 'A wh-adjective phrase asks "how …?" about an adjective: WRB + ADJ under one WHADJP - "how old" is (WHADJP (WRB how) (JJ old)).',
    detail: 'A wh-adjective phrase (WHADJP) asks "how ...?" about a quality and pairs the adverb how (WRB) with an adjective (JJ) as its two direct children ("how old", "how tall"). It typically fronts a question or appears as the complement of a linking verb. Recognize it by the fixed opening word how immediately followed by an adjective.',
    steps: [
      'Identify the pair: how (WRB) plus an adjective (JJ).',
      'Right-click the canvas and add the WHADJP box; drag its connector dot onto how first, then the adjective.',
      'Check that the two leaves read in sentence order - the canvas checks the tree automatically.',
    ],
    examples: ['how old'],
  },
  {
    type: 'WHADVP', title: 'Wh-adverb phrase', group: 'Wh-phrases',
    summary: 'A single question word such as "where", "when", "how", or "why" that asks for a place, time, manner, or reason.',
    rule: 'A wh-adverb phrase is a single wh-adverb standing in for when/where/how/why: one WRB leaf under the WHADVP box - "where" is (WHADVP (WRB where)).',
    detail: 'A wh-adverb phrase (WHADVP) is a single wh-adverb (WRB) - where, when, how, or why - standing as a whole phrase, so the box wraps one leaf: (WHADVP (WRB where)). It asks for a place, time, manner, or reason, and either fronts a question ("Where is the cat?") or introduces a subordinate clause ("the town where I grew up"). Recognize it because the phrase is exactly one interrogative adverb.',
    steps: [
      'Find the single wh-adverb (WRB).',
      'Right-click the canvas and add the WHADVP box; drag its connector dot straight onto the adverb.',
      'Check that the leaf matches the example - the canvas checks the tree automatically.',
    ],
    examples: ['where', 'when', 'how'],
  },
  {
    type: 'WHPP', title: 'Wh-prepositional phrase', group: 'Wh-phrases',
    summary: 'A preposition paired with a question word, such as "to whom" or "for what", asking about the object of a preposition.',
    rule: 'A wh-prepositional phrase is a preposition with a wh-noun phrase: IN (or TO) → WHNP - "to whom" is (WHPP (TO to) (WHNP (WP whom))).',
    detail: 'A wh-prepositional phrase (WHPP) is a prepositional phrase whose object is a wh-noun phrase: a preposition followed by WHNP ("to whom", "for what"). SynTutor tags the preposition IN, except for the infinitive "to", which stays TO: (WHPP (TO to) (WHNP (WP whom))). It questions the object of a preposition and is often fronted in a question. Recognize it by the preposition in first position and a wh-word in the object slot.',
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
    summary: 'A multi-word linker that joins two parallel items, such as "as well as".',
    rule: 'A conjunction phrase is a multi-word linker whose parts hang directly under one CONJP box - "as well as" is (CONJP (RB as) (RB well) (IN as)).',
    detail: 'A conjunction phrase (CONJP) links two parallel items with a multi-word conjunction - "as well as", "not to mention", "let alone". SynTutor tags no CC head inside it: each linker word hangs directly under the CONJP as it falls ("as well as" reads RB + RB + IN), and the first conjunct sits outside the CONJP as a sibling. Recognize it by a multi-word connective joining two otherwise complete units of the same kind.',
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
    summary: 'Coordinates two items of different kinds without a conjunction word, typically joined by punctuation, as in "first, second".',
    rule: 'An unlike-coordinated phrase coordinates two items of different categories with no conjunction between them - "first, second" is (UCP (ADVP (JJ first)) (, ,) (JJ second)).',
    detail: 'An unlike-coordinated phrase (UCP) coordinates two expressions of different grammatical categories without a coordinating conjunction: SynTutor wraps the left item in its own phrase box (an ADVP around first), keeps the punctuation as a sibling leaf, and leaves the right item as a bare adjective: (UCP (ADVP (JJ first)) (, ,) (JJ second)). Unlike ordinary coordination it does not require both conjuncts to match in category. Recognize it when two differently-typed items play the same role side by side, typically joined by punctuation rather than and/or.',
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
    summary: 'The small word that completes a phrasal verb, such as "away" in "throw away" or "up" in "give up".',
    rule: 'A particle is the small word that completes a phrasal verb. It hangs under the verb phrase in its own PRT box, tagged RB or RP, wherever the sentence puts it.',
    detail: 'A particle (PRT) is a small adverb-like word that belongs to a phrasal verb - away, up, off, out, down - and changes the verb meaning ("throw away", "give up"). SynTutor tags it RB (away) or RP (up) and tucks the PRT box inside the VP: "Throw it away." puts the particle after the object (VP over VB + NP + PRT) while "Give up the fight." puts it before (VP over VB + PRT + NP). Unlike a preposition, a particle takes no object of its own. Recognize it because it completes the verb rather than introducing a phrase.',
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
    summary: 'A phrase used alone as an utterance without a subject and predicate, such as a greeting, headline, or label.',
    rule: 'A fragment is a phrase standing alone as an utterance, without a subject and predicate; its words hang directly under one FRAG box - "Hello there." is (FRAG (UH Hello) (RB there) (. .)).',
    detail: 'A fragment (FRAG) is a phrase used as a standalone utterance without a subject-predicate core - greetings, headlines, labels, answers. Its leaves hang directly under the FRAG box with no inner phrase: "Hello there." reads UH + RB + the final punctuation as three sister leaves. It is headed by whatever word gives it its content (an interjection, noun, or adverb), and the parser marks it FRAG when no full clause can be built. Recognize it by the absence of a verb with a subject: the utterance works in context but not as a grammatical sentence.',
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
    summary: 'A single word that expresses emotion on its own, such as "Wow!" or "Hey!".',
    rule: 'An interjection is a word that expresses emotion on its own: Wow! Hey! Its punctuation hangs beside it under one INTJ box.',
    detail: 'An interjection (INTJ) is a single emotive word - wow, hey, oh, alas - that expresses a reaction on its own, with the exclamation mark kept as a sibling leaf inside the same box: (INTJ (UH Wow) (. !)). It stands outside the subject-predicate structure (it is not the head of any longer phrase) and adds affect rather than propositional meaning to the utterance. Recognize it by the exclamation word plus its punctuation; nothing else is attached beneath it.',
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
  state.session = { seq, pos, quizLesson };
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
  chevron.innerHTML = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="9 6 15 12 9 18"></polyline></svg>';
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
  const isModule = Boolean(lesson.sections?.length);
  const expanded = isModule && state.openModule === lesson.type;

  const card = el('article', 'sq-card-cell');

  // A module tile reads like a course card: a header band carrying the module
  // name, then a body with the description and its sub-topic preview chips.
  const face = el('button', 'sq-card');
  face.type = 'button';
  face.title = isModule ? `${lesson.title} — pick a sub-topic` : lesson.title;

  const head = el('span', 'sq-card-head');
  if (!isModule) head.appendChild(el('span', 'sq-card-tag', lesson.type));
  head.appendChild(el('span', 'sq-card-title', lesson.title));
  if (isModule) {
    const chevron = el('span', expanded ? 'sq-card-expand is-open' : 'sq-card-expand');
    chevron.setAttribute('aria-hidden', 'true');
    chevron.innerHTML = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>';
    head.appendChild(chevron);
  }
  face.appendChild(head);

  const body = el('span', 'sq-card-body');
  body.appendChild(el('span', 'sq-card-overview', lesson.summary || lesson.rule));
  if (isModule) {
    const chips = el('span', 'sq-card-topics');
    for (const section of lesson.sections) {
      chips.appendChild(el('span', 'sq-card-topic-chip', section.name));
    }
    body.appendChild(chips);
  }
  face.appendChild(body);

  face.addEventListener('click', () => {
    if (isModule) toggleModule(lesson);
    else openLesson(lesson);
  });
  card.appendChild(face);
  if (expanded) card.appendChild(moduleSubtopics(lesson));
  return card;
}

// Open or collapse a module's sub-topic list in the catalog.
function toggleModule(lesson) {
  state.openModule = state.openModule === lesson.type ? null : lesson.type;
  renderLessons();
}

// The catalog: a toolbar with the category expander and the completion
// counter, and a grid of the module cards for the active category.
function renderLessons() {
  ensureLessonsOverlay();
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
  state.activeGroup = lesson.group;
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

// A node is "completed" once its activity is done: the concept has been seen,
// every example has been built, or the end-of-lesson quiz has been finished.
function lessonNodeDone(lesson, page, current) {
  if (page === 1) return page !== current && state.visitedPages.has(`${lesson.type}:1`);
  if (page === 2) {
    const p = lessonProgress(lesson);
    return p.total > 0 && p.done === p.total;
  }
  return state.quizDone.has(lesson.type);
}

// The node-and-branch progress: three compact nodes (1 → 2 → 3) joined by
// short branch lines. Each node is clickable, shows a ✓ once its stage is
// done, and marks the stage the learner is on.
function renderLessonNodes(lesson, current) {
  const wrap = el('div', 'sq-nodes');
  wrap.setAttribute('role', 'group');
  wrap.setAttribute('aria-label', 'Lesson stages');
  LESSON_NODES.forEach((node, i) => {
    const done = lessonNodeDone(lesson, node.page, current);
    let cls = 'sq-node';
    if (node.page === current) cls += ' is-active';
    if (done) cls += ' is-done';
    const btn = el('button', cls);
    btn.type = 'button';
    btn.title = `${node.label}${done ? ' — done' : ''}`;
    btn.setAttribute('aria-label', node.label);
    btn.setAttribute('aria-pressed', String(node.page === current));
    btn.appendChild(el('span', 'sq-node-badge', done ? '✓' : String(node.page)));
    btn.addEventListener('click', () => goLessonNode(lesson, node.page));
    wrap.appendChild(btn);
    if (i < LESSON_NODES.length - 1) wrap.appendChild(el('span', 'sq-node-branch'));
  });
  return wrap;
}

// The upper-right stage content. Every stage shows only what belongs to it:
// the Concept never lists the examples, the Practice stage never repeats the
// concept, and the Quiz stage is the only one that talks about the score.
// A module-style lesson (one with `sections`) swaps the numbered step pager
// on Practice for a section picker: one section per type of the construction.
function renderLessonStage(lesson, page, index, example) {
  const stage = el('div', 'sq-lesson-stage');

  if (page === 1) {
    // Concept: a short objective and the way forward. The example sentences
    // stay hidden until the learner starts practising.
    const summary = el('div', 'sq-lesson-summary');
    summary.appendChild(el('p', 'sq-lesson-objective', lesson.rule));
    stage.appendChild(summary);
    const cta = el('button', 'sq-primary sq-lesson-cta', 'Start Practice →');
    cta.type = 'button';
    cta.addEventListener('click', () => goLessonNode(lesson, 2));
    stage.appendChild(cta);
    return stage;
  }

  if (page === 2) {
    // Practice: the sentence on the canvas, a compact switcher for the other
    // examples, and the way into the quiz. Module-style lessons also get the
    // section picker; stepped lessons get the step pager instead.
    const active = el('div', 'sq-active-sentence');
    active.appendChild(el('span', 'sq-active-label', 'On the canvas'));
    active.appendChild(el('p', 'sq-active-text', example));
    stage.appendChild(active);

    if (lesson.sections) {
      const picker = el('div', 'sq-section-picker');
      picker.setAttribute('role', 'group');
      picker.setAttribute('aria-label', 'Lesson sections');
      lesson.sections.forEach((section, i) => {
        let cls = 'sq-section-pill';
        if (i === state.sectionIndex) cls += ' is-active';
        const sectionDone = section.examples.every((s) => state.done.has(`${lesson.type}:${s}`));
        if (sectionDone && i !== state.sectionIndex) cls += ' is-done';
        const pill = el('button', cls, section.name);
        pill.type = 'button';
        pill.title = `${section.title} — ${section.examples.filter((s) => state.done.has(`${lesson.type}:${s}`)).length}/${section.examples.length} built`;
        pill.setAttribute('aria-pressed', String(i === state.sectionIndex));
        pill.addEventListener('click', () => selectSection(lesson, i));
        picker.appendChild(pill);
      });
      stage.appendChild(picker);
    } else {
      const switcher = el('div', 'sq-example-switcher');
      switcher.setAttribute('role', 'group');
      switcher.setAttribute('aria-label', 'Lesson examples');
      lesson.examples.forEach((sentence, i) => {
        const done = state.done.has(`${lesson.type}:${sentence}`);
        let cls = 'sq-example-chip';
        if (i === index) cls += ' is-active';
        if (done) cls += ' is-done';
        const chip = el('button', cls, done ? '✓' : String(i + 1));
        chip.type = 'button';
        chip.title = sentence;
        chip.setAttribute('aria-label', `Example ${i + 1}: ${sentence}`);
        chip.addEventListener('click', () => showExample(lesson, i));
        switcher.appendChild(chip);
      });
      stage.appendChild(switcher);

      const pager = el('div', 'sq-step-pager');
      const prev = el('button', 'sq-ghost sq-step-btn', '←');
      prev.type = 'button';
      prev.title = 'Previous step';
      prev.disabled = guide.step <= 0;
      prev.addEventListener('click', () => openStepGuide(lesson, guide.step - 1));
      const label = el('span', 'sq-step-pager-label', `Step ${guide.step + 1} of ${lesson.steps.length}`);
      const next = el('button', 'sq-ghost sq-step-btn', '→');
      next.type = 'button';
      next.title = 'Next step';
      next.disabled = guide.step >= lesson.steps.length - 1;
      next.addEventListener('click', () => openStepGuide(lesson, guide.step + 1));
      pager.appendChild(prev);
      pager.appendChild(label);
      pager.appendChild(next);
      stage.appendChild(pager);
    }

    const quiz = el('button', 'sq-primary', 'Start Quiz →');
    quiz.type = 'button';
    quiz.addEventListener('click', () => startLessonQuiz(lesson));
    stage.appendChild(quiz);
    return stage;
  }

  // Quiz: the prompts (the examples the quiz walks through) and the score.
  if (state.session) {
    const live = el('div', 'sq-active-sentence');
    live.appendChild(el('span', 'sq-active-label', 'Build this tree'));
    live.appendChild(el('p', 'sq-active-text', state.session.seq[state.session.pos]?.example || ''));
    stage.appendChild(live);
  } else {
    const list = el('ul', 'sq-quiz-list');
    for (const sentence of lesson.examples) {
      const item = el('li', 'sq-quiz-item');
      const done = state.done.has(`${lesson.type}:${sentence}`);
      item.appendChild(el('span', done ? 'sq-quiz-mark is-done' : 'sq-quiz-mark', done ? '✓' : '○'));
      item.appendChild(el('span', 'sq-quiz-sent', sentence));
      list.appendChild(item);
    }
    stage.appendChild(list);
  }
  const progress = lessonProgress(lesson);
  const score = el('div', 'sq-quiz-score');
  score.appendChild(el('span', 'sq-quiz-score-value', state.session
    ? `${state.session.pos}/${state.session.seq.length}`
    : `${progress.done}/${progress.total}`));
  score.appendChild(el('span', 'sq-quiz-score-label', state.session ? 'trees built' : 'examples built'));
  stage.appendChild(score);
  if (!state.session) {
    const start = el('button', 'sq-primary', 'Start Quiz →');
    start.type = 'button';
    start.addEventListener('click', () => startLessonQuiz(lesson));
    stage.appendChild(start);
  }
  return stage;
}

// The bottom-right content: the current stage's explanation, rendered
// directly on the pane surface — no nested card, no clipped text. For a
// module-style lesson the Practice page shows the active section's content
// and directs the learner to build that section's trees on the canvas.
function renderLessonBody(lesson, page, example) {
  const body = el('div', 'sq-lesson-body');
  if (page === 1) {
    const rule = el('div', 'sq-rule');
    const concept = el('div', 'sq-concept');
    concept.appendChild(el('p', 'sq-rule-text', lesson.rule));
    concept.appendChild(el('p', 'sq-rule-detail', lesson.detail));
    if (lesson.components?.length) {
      const comps = el('div', 'sq-components');
      comps.appendChild(el('p', 'sq-group', 'Components'));
      const dl = el('dl', 'sq-component-list');
      for (const [term, text] of lesson.components) {
        dl.appendChild(el('dt', null, term));
        dl.appendChild(el('dd', null, text));
      }
      concept.appendChild(comps);
    }
    rule.appendChild(concept);
    body.appendChild(rule);
    return body;
  }
  if (page === 2) {
    if (state.session) {
      body.appendChild(el('p', 'sq-hint', 'Quiz in progress — build each tree on the canvas.'));
      return body;
    }
    if (lesson.sections) {
      const section = lesson.sections[state.sectionIndex] || lesson.sections[0];
      const built = section.examples.filter((s) => state.done.has(`${lesson.type}:${s}`)).length;
      body.appendChild(el('p', 'sq-hint',
        `Build the syntax tree for “${example}” on the canvas using the ${section.name.toLowerCase()} pattern below — `
        + 'the canvas checks your tree automatically. Pick another example once it matches.'));
      const panel = el('div', 'sq-section-panel');
      const head = el('div', 'sq-section-head');
      head.appendChild(el('h3', 'sq-section-title', section.title));
      head.appendChild(el('span', 'sq-section-count', `${built}/${section.examples.length} built`));
      panel.appendChild(head);
      panel.appendChild(el('p', 'sq-section-detail', section.detail));
      const list = el('ul', 'sq-quiz-list', null);
      section.examples.forEach((sentence) => {
        const item = el('li', 'sq-quiz-item');
        const done = state.done.has(`${lesson.type}:${sentence}`);
        item.appendChild(el('span', done ? 'sq-quiz-mark is-done' : 'sq-quiz-mark', done ? '✓' : '○'));
        const btn = el('button', 'sq-quiz-sent-btn', sentence);
        btn.type = 'button';
        btn.title = `${sentence} — load on the canvas`;
        btn.addEventListener('click', () => showExample(lesson, lesson.examples.indexOf(sentence)));
        item.appendChild(btn);
        list.appendChild(item);
      });
      panel.appendChild(list);
      body.appendChild(panel);
      return body;
    }
    body.appendChild(el('p', 'sq-hint',
      `Follow the step-by-step guide on the canvas for “${example}”. `
      + 'Press ▶ Play to animate through the steps as the ring points at each part of the tree.'));
    const steps = el('div', 'sq-steps-box');
    const list = el('ol', 'sq-steps');
    lesson.steps.forEach((step, i) => {
      const li = el('li', guide.open && i === guide.step ? 'is-current' : null, step);
      li.dataset.step = String(i);
      li.title = 'Show this step on the canvas';
      li.addEventListener('click', () => openStepGuide(lesson, i));
      list.appendChild(li);
    });
    steps.appendChild(list);
    body.appendChild(steps);
    return body;
  }
  const summary = el('div', 'sq-quiz-summary');
  summary.appendChild(el('p', null, lesson.sections
    ? 'You have explored every section and built its trees. '
      + "The quiz rebuilds every example of this lesson in order — one tree each, checked live against SynTutor's parse. Practiced examples are marked ✓."
    : 'You have read the concept, walked the build steps, and practiced the examples. '
      + 'The quiz rebuilds every example of this lesson in order — one tree each, checked live '
      + "against SynTutor's parse. Practiced examples are marked ✓."));
  body.appendChild(summary);
  return body;
}

// Pick a section of a module-style lesson: load its first sample and re-render
// the LMS lesson panel around it.
function selectSection(lesson, i) {
  state.sectionIndex = Math.max(0, Math.min(i, lesson.sections.length - 1));
  state.exampleIndex = defaultExampleIndex(lesson);
  state.goldError = null;
  state.goldLoading = null;
  renderLesson();
  const host = $('#quizQuestHost');
  if (host) host.scrollTop = 0;
  openModelExample(lesson, lesson.examples[state.exampleIndex]);
}

// The example a section should open on: its first sample.
function defaultExampleIndex(lesson) {
  const section = lesson.sections?.[state.sectionIndex] || lesson.sections?.[0];
  if (!section) return 0;
  const example = section.examples[0];
  const index = lesson.examples.indexOf(example);
  return index < 0 ? 0 : index;
}

// Move between nodes. Entering Practice loads the first not-yet-built
// example so the canvas and its guide card are ready to follow. A
// module-style lesson starts on its first not-yet-built section.
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

  // The spotlight guide only belongs to the example it was opened on; a node
  // switch, example switch, or new lesson dismisses it. Plain re-renders (a
  // solved example refreshing the checkmarks) keep it alive — syncGuideCard()
  // re-syncs the highlight below.
  if (guide.open
    && (guide.lesson !== lesson.type || guide.example !== example || page !== 2)) {
    closeStepGuide();
  }

  host.innerHTML = '';
  const wrap = el('div', 'sq-lesson');

  // One header row: the book button and the lesson title on the left, the
  // compact stage progress bar on the right.
  const head = el('header', 'sq-lesson-head');
  const headMain = el('div', 'sq-lesson-head-main');
  const book = el('button', 'sq-lesson-book');
  book.type = 'button';
  book.title = 'Show all lesson modules';
  book.setAttribute('aria-label', 'Show all lesson modules');
  book.innerHTML = '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>';
  book.addEventListener('click', () => openLessonsOverlay());
  headMain.appendChild(book);
  headMain.appendChild(el('h2', 'sq-lesson-title', lesson.title));
  head.appendChild(headMain);
  head.appendChild(renderLessonNodes(lesson, page));
  wrap.appendChild(head);

  // Only the current stage's controls live in the upper-right pane.
  wrap.appendChild(renderLessonStage(lesson, page, index, example));

  host.appendChild(wrap);

  // The stage content lives in the bottom pane, above the node inspector.
  guideHost.innerHTML = '';
  guideHost.appendChild(renderLessonBody(lesson, page, example));

  // Keep an open spotlight guide in sync with the fresh DOM.
  if (guide.open) updateStepGuide();
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
  const head = el('header', 'sq-lesson-head');
  const headMain = el('div', 'sq-lesson-head-main');
  const book = el('button', 'sq-lesson-book');
  book.type = 'button';
  book.title = 'Show all lesson modules';
  book.setAttribute('aria-label', 'Show all lesson modules');
  book.innerHTML = '<svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>';
  book.addEventListener('click', () => openLessonsOverlay());
  headMain.appendChild(book);
  headMain.appendChild(el('h2', 'sq-lesson-title', lesson.title));
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
  return startChallenge(lesson, lesson.examples[i]);
}

// The lesson's quiz: build every example of this lesson, in order. It is the
// lesson's final page — the spotlight guide has no place once the quiz starts.
function startLessonQuiz(lesson) {
  closeStepGuide();
  closeGuideCard();
  closeQuizView();
  $('#appSidebarBackdrop')?.classList.remove('active');
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
  // Module lessons are now read-only and single-unit lessons have no Model
  // state to return to, so the builder's "Show model tree" escape hatch is
  // never needed in a lesson practice session.
  const modelBtn = document.querySelector('#builderModel');
  if (modelBtn) modelBtn.hidden = true;
  // Lesson practice shows the step-by-step guide card docked at the canvas's
  // bottom-left when the lesson has numbered build steps; module-style
  // lessons (sections, no steps) teach by building, so they get no card.
  // Quiz sessions get no card either.
  if (practice && lesson.steps?.length) openGuideCard(lesson, example);
  else closeGuideCard();
}

function record(lesson, example, ok) {
  if (!ok) return;
  state.done.add(`${lesson.type}:${example}`);
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
  const host = $('#quizQuestHost');
  if (host) host.innerHTML = '';
  const guideHost = $('#lessonGuideHost');
  if (guideHost) guideHost.innerHTML = '';
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
// A step-by-step guide card is docked at the bottom-left of the canvas while a
// lesson example is loaded. Its step rows are clickable and its ▶ Play button
// animates through the steps. A fixed spotlight ring (pointer-events: none)
// highlights the canvas region, word row, phrase box, or connector dot the
// current step talks about; the learner can still right-click, drag, and
// re-route on the canvas while following along. A rAF loop keeps the ring
// glued to its target while the canvas pans, zooms, or the boxes move.
const guide = { open: false, step: 0, lesson: null, example: null, raf: 0, playing: false, timer: 0 };

function ensureStepGuideDom() {
  if ($('#stepGuide')) return;
  const wrap = el('div', 'step-guide');
  wrap.id = 'stepGuide';
  wrap.hidden = true;
  wrap.innerHTML = '<div class="step-guide-ring" aria-hidden="true"></div>';
  document.body.appendChild(wrap);
}

function ensureGuideCard() {
  const existing = $('#canvasGuideCard');
  if (existing) return existing;
  const stage = $('.canvas-stage');
  if (!stage) return null;
  const card = el('div', 'canvas-guide-card');
  card.id = 'canvasGuideCard';
  card.hidden = true;
  const head = el('div', 'canvas-guide-head');
  head.appendChild(el('span', 'canvas-guide-label', 'Step-by-step guide'));
  const play = el('button', 'canvas-guide-play', '▶ Play');
  play.type = 'button';
  play.title = 'Animate through the steps, pointing at the canvas';
  play.addEventListener('click', toggleGuidePlay);
  head.appendChild(play);
  card.appendChild(head);
  card.appendChild(el('p', 'canvas-guide-sentence'));
  card.appendChild(el('ol', 'canvas-guide-list'));
  stage.appendChild(card);
  return card;
}

function openGuideCard(lesson, example) {
  const card = ensureGuideCard();
  if (!card) return;
  card.querySelector('.canvas-guide-sentence').textContent = example;
  const list = card.querySelector('.canvas-guide-list');
  list.textContent = '';
  lesson.steps.forEach((step, i) => {
    const li = el('li', guide.open && guide.lesson === lesson.type && i === guide.step ? 'is-current' : null, step);
    li.dataset.step = String(i);
    li.title = 'Show this step on the canvas';
    li.addEventListener('click', () => openStepGuide(lesson, i));
    list.appendChild(li);
  });
  card.hidden = false;
  syncGuideCard();
}

function closeGuideCard() {
  stopGuidePlay();
  const card = $('#canvasGuideCard');
  if (card) card.hidden = true;
}

// Reflect the live guide state on the canvas card and both step lists: the
// Play/Stop button follows `guide.playing` and the highlighted row follows
// `guide.step`. Called whenever the guide opens, moves, plays, or stops, and on
// every lesson re-render so the checkmarks and highlight stay truthful.
function syncGuideCard() {
  const play = $('#canvasGuideCard')?.querySelector('.canvas-guide-play');
  if (play) {
    play.textContent = guide.playing ? '■ Stop' : '▶ Play';
    play.setAttribute('aria-pressed', String(guide.playing));
    play.classList.toggle('is-playing', guide.playing);
  }
  document.querySelectorAll('.canvas-guide-list li, .sq-steps li').forEach((li) => {
    li.classList.toggle('is-current', guide.open && li.dataset.step === String(guide.step));
  });
}

function toggleGuidePlay() {
  const lesson = LESSONS.find((l) => l.type === guide.lesson);
  if (!lesson) return;
  if (guide.playing) {
    stopGuidePlay();
    return;
  }
  if (!guide.open || guide.lesson !== lesson.type) openStepGuide(lesson, 0);
  startGuidePlay(lesson);
}

function startGuidePlay(lesson) {
  stopGuidePlay(false);
  guide.playing = true;
  syncGuideCard();
  const tick = () => {
    if (!guide.open || !guide.playing || guide.step >= lesson.steps.length - 1) {
      stopGuidePlay();
      return;
    }
    guide.step += 1;
    updateStepGuide();
    guide.timer = window.setTimeout(tick, 2600);
  };
  guide.timer = window.setTimeout(tick, 2600);
}

function stopGuidePlay(render = true) {
  guide.playing = false;
  if (guide.timer) { window.clearTimeout(guide.timer); guide.timer = 0; }
  if (render) syncGuideCard();
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
  stopGuidePlay(false);
  const wrap = $('#stepGuide');
  if (wrap) wrap.hidden = true;
  document.removeEventListener('keydown', onStepGuideKeydown);
  syncGuideCard();
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

// Push the guide state into the canvas card and both step lists. The ring's
// position is interpolated by the rAF loop, so this only syncs the chrome.
function updateStepGuide() {
  const lesson = LESSONS.find((l) => l.type === guide.lesson);
  if (!lesson) return closeStepGuide();
  syncGuideCard();
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
  // The hint floats on its own (outside the action cluster), so it has to be
  // unhidden explicitly for the message to be readable.
  if (hint) { hint.textContent = msg; hint.className = 'builder-hint builder-hint-no'; hint.hidden = false; }
}

// Whenever the builder closes, drop any active lesson view so a stale lesson
// panel never survives a return to normal SynTutor or a standalone Syntax
// Builder session.
setBuilderCloseHandler(clearActiveLesson);
