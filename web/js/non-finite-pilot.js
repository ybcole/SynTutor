import { addIntroExample, addTreeTrace, lessonExample } from './lesson-presentation.js';
import { addBranchExercise } from './lesson-tree-exercise.js';

const node = (id, label, ...children) => ({ id, label, children });
const word = (id, label, text, ...features) => ({ ...node(id, label, { word: text }), features });
const np = (id, text, index) => ({ id, label: 'NP', triangle: true, words: text.split(' '), index });
const silent = (id, index) => node(id, 'NP', { id: `${id}-dot`, gap: true, index });
const tree = (sentence, root) => ({ sentence, root });
const emptyC1 = { id: 'c1', label: 'C1', empty: true };
const sbar = (subject, predicate, c1 = emptyC1) =>
  node('embedded', 'S-bar', c1, node('lower-clause', 'S', subject, predicate));
const infinitive = (verb, ...parts) =>
  node('infinitive', 'VP', word('to', 'AUX', 'to', '-tense'), node('lexical', 'VP', verb, ...parts));
const wait = infinitive(word('wait', 'V', 'wait', 'intrans'));
const knowing = node('knowing', 'VP', word('know', 'V', 'Knowing', 'trans', '-tense'), np('route', 'the route'));
const checking = node('checking', 'VP', word('check', 'V', 'checking', 'trans', '-tense'), np('maps', 'the maps'));
const free = tree('Knowing the route', sbar(silent('lower-subject'), knowing));
const packed = tree('the lamps packed', node('lower-clause', 'S', np('lower-subject', 'the lamps', 1),
  node('predicate', 'VP', word('pack', 'V', 'packed', 'trans', '-tense'), silent('object', 1))));
const enjoyment = (sentence, subject, lowerSubject) => tree(sentence,
  node('main', 'S', subject, node('predicate', 'VP', word('enjoy', 'V', 'enjoys', 'trans', 'pres'),
    sbar(lowerSubject, checking))));
const controlled = enjoyment('Nia enjoys checking the maps', np('controller', 'Nia', 1), silent('lower-subject', 1));
const overt = enjoyment('Nia enjoys Ivo checking the maps', np('subject', 'Nia'), np('lower-subject', 'Ivo'));
const forClause = tree('For Ivo to wait outside', sbar(np('lower-subject', 'Ivo'),
  node('modified', 'VP', wait, { id: 'outside', label: 'PP', triangle: true, words: ['outside'] }),
  word('for', 'C1', 'For')));
const embeddedQuestion = (sentence, verb, clause) => tree(sentence, node('main', 'S',
  np('controller', 'Nia', 1), node('predicate', 'VP', word('main-verb', 'V', verb, 'trans', 'past'), node('question-np', 'NP', clause))));
const whetherClause = embeddedQuestion('Nia wondered whether to wait', 'wondered',
  sbar(silent('lower-subject', 1), wait, word('whether', 'C1', 'whether')));
const whatClause = embeddedQuestion('Nia knew what to pack', 'knew',
  node('question', 'S-dbar', { ...word('what', 'C2', 'what'), index: 2 },
    sbar(silent('lower-subject', 1), infinitive(word('pack', 'V', 'pack', 'trans'), silent('object', 2)))));
const expected = tree('They expected Ivo to wait', node('main', 'S', np('subject', 'They'),
  node('predicate', 'VP', word('expect', 'V(I)', 'expected', 'past'), sbar(np('lower-subject', 'Ivo'), wait))));
const persuaded = tree('They persuaded Ivo to wait', node('main', 'S', np('subject', 'They'),
  node('predicate', 'VP', word('persuade', 'V(II)', 'persuaded', 'past'), np('controller', 'Ivo', 1),
    sbar(silent('lower-subject', 1), wait))));

const request = tree('a request to move the crates', node('np', 'NP',
  node('det', 'DET', word('article', 'ART', 'a')), node('nom', 'NOM', word('noun', 'N', 'request'),
    sbar(silent('lower-subject'),
      infinitive(word('move', 'V', 'move', 'trans'), np('object', 'the crates'))))));
const crates = tree('the crates to move', node('np', 'NP',
  node('det', 'DET', word('article', 'ART', 'the')), node('nom', 'NOM',
    { ...node('inner-nom', 'NOM', word('noun', 'N', 'crates')), index: 1 },
    node('relative', 'S-dbar', node('c2', 'C2', { id: 'wh-gap', gap: true, index: 1 }),
      sbar(silent('lower-subject'), infinitive(word('move', 'V', 'move', 'trans'), silent('object', 1)))))));

const labels = ['S-bar', 'C1', 'S', 'NP', 'VP', 'V', '△', '•', 'Index'];
const repair = {
  buildTitle: 'Attach the lexical VP beside infinitival “to”',
  build: {
    branch: root => [root, root.children[1]],
    action: 'Connect the lexical VP beside “to”',
    hint: 'Attach “inspect the bridge” directly under the higher VP, beside the branch above “to”.',
    success: 'The lexical VP shares the higher VP with the untensed auxiliary “to”.',
  },
};

export const nonFinitePilot = {
  description: 'Compare four non-finite forms, find their subjects, and see how two verb patterns change where an overt noun phrase belongs.',
  references: [
    'Chapter 10, printed pp. 224–229, [6], [11], [14a], [17], [21–22] · Non-finite forms and subjects',
    'Printed pp. 229–232, [26–33] and Discussion 1, p. 244 · Complementisers and wh-phrases',
    'Printed pp. 232–236, [38c], [40–65] and Discussion 2, p. 244 · Clause functions and non-finite NP modifiers',
    'Printed pp. 236–244, [66–102] · Verb selection and Type I and Type II complements',
  ],
  sections: [
    { id: 'introduction', title: 'Introduction to non-finite clauses and their subjects' },
    { id: 'concepts', title: 'Part I: Infinitives and participles', notationLabels: ['S', 'NP', 'VP', 'V', '△', '•', 'Index'], notationFeatures: ['trans', '-tense'] },
    { id: 'worked-example', title: 'To-infinitive verb phrase exercise', notationLabels: ['VP', 'V', 'NP', '△'], notationFeatures: ['-tense', 'trans'] },
    { id: 'subjects-and-control', title: 'Non-finite complementisers and fronted wh-phrases (C1 and C2)', notationLabels: [...labels, 'S-dbar', 'C2', 'PP'], notationFeatures: ['-tense', 'trans', 'pres', 'past', 'intrans'] },
    { id: 'clause-functions', title: 'Part II: Non-finite subjects, adjective and preposition complements, and adverbials' },
    { id: 'noun-clause-functions', title: 'Non-finite noun complements and NOM modifiers',
      notationLabels: [...labels, 'DET', 'ART', 'NOM', 'N', 'S-dbar', 'C2'], notationFeatures: ['-tense', 'trans'] },
    { id: 'verb-complements', title: 'Non-finite verb complements and Type I and Type II verbs', notationLabels: [...labels, 'V(I)', 'V(II)'], notationFeatures: ['-tense', 'past', 'intrans'] },
    { id: 'application', title: 'Exercises on non-finite clauses and control' },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Finite verb', 'A verb that carries tense in its clause.'],
    ['Non-finite clause', 'A clause whose verbs have no tense of their own.'],
    ['Overt subject', 'A subject with words you can point to.'],
    ['Covert subject', 'A subject you can work out even though no words name it.'],
    ['Controller', 'A word or group that shows who or what a silent part of a smaller clause refers to.'],
    ['Index', 'A number that links spots in a tree. The same number can show that two spots refer to the same person or thing.'],
  ],
  teach(body, _page, ui) {
    const { el, lesson, section } = ui;
    const p = text => body.append(el('p', text));
    const example = text => body.append(lessonExample(el, text));
    const trace = (label, steps) => addTreeTrace(body, ui, label, steps);
    const check = (key, prompt, choices, correct, messages) => {
      const feedback = el('p', undefined, 'lesson-feedback');
      feedback.setAttribute('role', 'status');
      body.append(ui.practiceQuestion(key, prompt, choices, answer => {
        feedback.className = `lesson-feedback ${Number(answer) === correct ? 'correct' : 'retry'}`;
        feedback.textContent = messages[Number(answer)];
      }), feedback);
    };

    switch (section.id) {
      case 'introduction': {
        p('Chapter 6 showed which verb carries tense in a verb chain. A non-finite clause has no tense of its own. It can still describe an action or state, and you can often work out its subject from the larger sentence. This chapter looks at clauses without tense of their own, and how to work out who does the action in them.');
        addIntroExample(body, el, 'In the example below, the brackets mark what Nora planned to do. Try changing “planned” to “plans” and see which words keep their form.',
          'Nora planned [to inspect the bridge].',
          '“Planned” carries past tense, so it is finite. The smaller clause, “to inspect the bridge”, stays the same. It is non-finite. In the tree, “to” carries the feature [-tense]. Nora is still the person who would do the inspecting, even though her name is outside the brackets.');
        body.append(el('h3', 'What you’ll learn in this chapter'));
        const list = el('ul');
        for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
        body.append(list);
        break;
      }
      case 'concepts':
        p('Infinitives and participles are forms that lack tense. Read [-tense] as “minus tense”. In the trees on this page, it marks the untensed verb or auxiliary. See which branch has that mark in each example.');
        example('The crew made Ivo [wait].');
        p('“Wait” is a bare infinitive. It uses the plain verb form without “to”. Put [-tense] on V.');
        example('Nora planned [to inspect the bridge].');
        p('In a to-infinitive, put [-tense] on the branch above “to”. The verb “inspect” stays in its plain form.');
        example('With [the lamps packed], the crew left.');
        p('“Packed” is a passive participle. Put [-tense] on V. “The lamps” is the subject of the passive clause, even though the lamps are what someone packed. The object spot is empty.');
        trace('Trace the passive participle clause', [
          ['Find the passive subject', packed, 'lower-subject', '“The lamps” is the overt subject. It carries index 1.'],
          ['Find the object gap', packed, 'object-dot', 'The matching index shows that the lamps are what someone packed. The passive verb carries [-tense].'],
        ]);
        example('[Knowing the route] helps.');
        p('In this -ing participle clause, put [-tense] on “knowing”. Compare “is checking”. There, “is” carries tense, so the progressive is finite.');
        break;
      case 'worked-example': {
        p('A to-infinitive uses “to” followed by a verb in its base form. In the inspection tree below, “to” bears [-tense] and sits beside the lexical VP “inspect the bridge”.');
        p('Say “Nora plans to inspect the bridge”, then change “plans” to “planned”. The time changes on the higher verb, but “to inspect the bridge” keeps its form. Inside the smaller VP, “to” bears [-tense] and takes “inspect the bridge” as its VP complement. In that lowest VP, “the bridge” belongs with “inspect”.');
        example('Nora plans [to inspect the bridge].');
        const fragment = lesson.worked_example.tree;
        const [to, lexical] = fragment.root.children;
        trace('Read the two verb phrases', [
          ['Find [-tense] above “to”', fragment, to.id, 'The branch above infinitival “to” carries [-tense].'],
          ['Find the lexical VP', fragment, lexical.id, '“Inspect the bridge” is the entire complement of “to”.'],
        ]);
        body.append(el('h3', repair.buildTitle));
        p('Drag a branch from the higher VP to the detached lexical VP, or choose Guide me. Then select Check my tree.');
        addBranchExercise(body, ui, repair);
        p('In “Nora walked to the bridge”, “to” is a preposition. Its NP complement is “the bridge”.');
        break;
      }
      case 'subjects-and-control':
        p('An overt subject has words you can point to. A covert subject is understood without words. It can mean people in general. Then it is free. If a word group in the larger clause tells who it is, that group is its controller.');
        example('[Knowing the route] helps. · Nia enjoys [checking the maps]. · Nia enjoys [Ivo checking the maps].');
        trace('Compare free, controlled and overt subjects', [
          ['Find the free subject', free, 'lower-subject-dot', 'The dot marks a free subject. The example makes a general statement about knowing the route.'],
          ['Find the controlled subject', controlled, 'lower-subject-dot', 'The matching 1s on Nia’s NP and the dot show that Nia is understood to check the maps.'],
          ['Find the overt subject', overt, 'lower-subject', '“Ivo” is expressed inside the non-finite clause and names who checks the maps.'],
        ]);
        p('A complementiser can start the clause. “For” fills C1 before a spoken subject. In the next example, “whether” fills C1 and the subject is silent. In the example with “what”, C2 is filled and C1 is empty.');
        p('Compare “for Ivo to wait” and “whether to wait”. In the first, C1 is “for” and “Ivo” is the spoken subject of “wait”. In the second, C1 is “whether”, and the subject may have to be inferred from the larger sentence. In “Nia knew what to pack”, “what” belongs in C2 and points to an object gap after “pack”. That object gap is separate from the understood subject, Nia.');
        example('[For Ivo to wait outside] seemed unfair. · Nia wondered [whether to wait]. · Nia knew [what to pack].');
        trace('Locate C1 and C2 in infinitival clauses', [
          ['Find “for” in C1', forClause, 'for', '“For” fills C1. “Ivo” is the overt subject inside S.'],
          ['Find “whether” in C1', whetherClause, 'whether', '“Whether” introduces the embedded question. The silent subject is understood as Nia in the full sentence.'],
          ['Find “what” in C2', whatClause, 'what', '“What” fills C2. The object gap after “pack” shows where it does its job. C1 is empty.'],
        ]);
        break;
      case 'clause-functions':
        p('Find the subject and verb first. Then ask what job the whole clause does in the sentence.');
        example('[Checking the ropes] takes time.');
        p('The bracketed clause tells what takes time. It is the subject.');
        example('Nia insisted on [checking the ropes].');
        p('The clause completes the preposition “on”. That makes it the complement of P inside the PP. Here, P takes S directly.');
        example('Nia paused [to check the ropes].');
        p('The clause tells why someone paused. It works as an adverbial of purpose. An adjective can also select a non-finite clause, as “eager” does in “eager to help”. Next, compare the two ways a non-finite clause can belong to an NP.');
        break;
      case 'noun-clause-functions':
        p('Ask what the clause tells you about the noun. In “a request to move the crates”, it gives the request’s content. In “the crates to move”, it tells which crates, and there is an object gap after “move”.');
        p('Try the question “What did the request ask for?” The answer is “to move the crates”, which gives the request’s content. For “the crates to move”, ask “Which crates?” The relative identifies them, and “move” leaves the object unspoken. The guide follows that gap back to the nominal “crates”.');
        trace('Compare a noun complement and a NOM modifier', [
          ['Read the complement of N', request, 'embedded', '“To move the crates” is the content of the request. It joins N within NOM.'],
          ['Read the relative beside NOM', crates, 'inner-nom', '“To move” helps identify the crates. The smaller NOM and the relative S″ join under a larger NOM.'],
          ['Follow the silent wh-expression', crates, 'object-dot', 'Index 1 connects the crates, the silent wh-expression in C2, and the object gap after “move”. The separate silent subject names no particular mover in this phrase.'],
        ]);
        break;
      case 'verb-complements':
        p('With a Type I verb, labelled V(I), the non-finite clause is one complement with its own subject. With a Type II verb, labelled V(II), the higher verb takes an object and a separate non-finite clause. In the examples below, “expect” is Type I. It takes one clause with its own overt subject. “Persuade” is Type II here. It takes an object and a clause with a covert subject.');
        example('They expected [Ivo to wait].');
        example('They persuaded [Ivo] [to wait].');
        check('type-two-object', 'What is “Ivo” in the sentence with “persuaded”?',
          ['The overt subject inside the lower clause', 'The object of “persuaded”'],
          1, ['Ivo does the waiting, and the overt NP is the person they persuaded. Look for it in the higher VP.',
            '“Ivo” is the higher object. It controls the silent subject of “to wait”.']);
        trace('Compare the two positions for the overt NP', [
          ['Read the Type I complement', expected, 'lower-subject', 'The clause is the single complement of V(I). Ivo is its overt subject.'],
          ['Find the Type II object', persuaded, 'controller', 'V(II) has two complements. The object NP “Ivo” sits beside the infinitival clause.'],
          ['Trace the silent subject', persuaded, 'lower-subject-dot', 'The dot and the object NP share index 1. Ivo is understood to wait.'],
        ]);
        const note = el('details', undefined, 'lesson-sources');
        note.append(el('summary', 'Try a check with “there”'),
          el('p', '“They expected there to be a delay” allows dummy “there” as the lower subject. “They persuaded there to be a delay” fails in that reading because “persuade” needs an object that can be persuaded. “Promise” has its own control pattern: in “Nia promised Ren to wait”, Nia is understood to wait.'));
        body.append(note);
        break;
      case 'application': {
        p('Ren is the one who would leave in both examples. Where does the spoken NP “Ren” belong in each sentence? Decide before you reveal the brackets.');
        example('Nia expected Ren to leave. · Nia advised Ren to leave.');
        const answer = el('details', undefined, 'lesson-sources');
        answer.append(el('summary', 'Check both analyses'),
          lessonExample(el, 'Nia expected [Ren to leave]. · Nia advised [Ren] [to leave].'),
          el('p', 'With “expected”, Ren is the overt lower subject. With “advised”, Ren is the higher object and controls the silent lower subject.'));
        body.append(answer);
        break;
      }
      case 'recap':
        p('First find the untensed form. Put [-tense] above infinitival “to” or on the untensed verb in the other three forms.');
        p('Now find the subject of the smaller clause. It can be overt, free, or controlled. Matching indices link a controller you can see to a subject you have to work out.');
        p('Last, ask what the clause does. “Checking the ropes” can be a subject or complete a preposition. After “expected”, the NP can be the subject inside the lower clause. After “persuaded”, the NP is the object of the higher verb.');
        break;
    }
  },
};
