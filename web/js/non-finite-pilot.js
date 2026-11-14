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
    'Printed pp. 232–236, [40–65] and Discussion 2, p. 244 · Clause functions',
    'Printed pp. 239–243, [98–102] · Type I and Type II complements',
  ],
  sections: [
    { id: 'introduction', title: 'Where does tense belong?' },
    { id: 'concepts', title: 'Identify the four non-finite forms', notationLabels: ['S', 'NP', 'VP', 'V', '△', '•', 'Index'], notationFeatures: ['trans', '-tense'] },
    { id: 'worked-example', title: 'Trace and repair the infinitival VP', notationLabels: ['VP', 'V', 'NP', '△'], notationFeatures: ['-tense', 'trans'] },
    { id: 'subjects-and-control', title: 'Find the subject and its controller', notationLabels: [...labels, 'S-dbar', 'C2', 'PP'], notationFeatures: ['-tense', 'trans', 'pres', 'past', 'intrans'] },
    { id: 'clause-functions', title: 'Ask what job the clause does' },
    { id: 'verb-complements', title: 'Compare Type I and Type II', notationLabels: [...labels, 'V(I)', 'V(II)'], notationFeatures: ['-tense', 'past', 'intrans'] },
    { id: 'application', title: 'Apply the two analyses' },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Finite verb', 'A verb that carries tense in its clause.'],
    ['Non-finite clause', 'A clause whose verb sequence carries no tense of its own.'],
    ['Overt subject', 'A subject expressed in spoken or written words.'],
    ['Covert subject', 'A subject understood without an overt expression.'],
    ['Controller', 'An overt element that identifies an understood constituent in a lower clause.'],
    ['Index', 'A number that links positions in a tree. The same number shows that they refer to the same participant.'],
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
        p('Chapter 6 showed where tense sits in a sequence of verbs. A finite verb carries tense in its clause. A non-finite clause has no tense of its own. It can still contain a verb, complements and an understood or expressed subject.');
        addIntroExample(body, el, 'The brackets mark what Nora planned to do.',
          'Nora planned [to inspect the bridge].',
          '“Planned” carries past tense. Changing it to “plans” leaves “to inspect the bridge” unchanged.');
        body.append(el('h3', 'What you’ll see in this chapter'));
        const list = el('ul');
        for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
        body.append(list);
        break;
      }
      case 'concepts':
        p('The marker [-tense], read “minus tense”, identifies the untensed verb or auxiliary in these patterns. Compare where it belongs in each example.');
        example('The crew made Ivo [wait].');
        p('“Wait” is a bare infinitive. It has the stem form without “to”, so [-tense] goes on V.');
        example('Nora planned [to inspect the bridge].');
        p('In the to-infinitive, [-tense] goes on the branch above “to”. “Inspect” keeps its stem form.');
        example('With [the lamps packed], the crew left.');
        p('“Packed” is a passive participle and carries [-tense] on V. The lamps are what someone packed. In the passive clause, “the lamps” is the subject and the object position is empty.');
        trace('Trace the passive participle clause', [
          ['Find the passive subject', packed, 'lower-subject', '“The lamps” is the overt subject. It carries index 1.'],
          ['Find the object gap', packed, 'object-dot', 'The matching index shows that the lamps are what someone packed. The passive verb carries [-tense].'],
        ]);
        example('[Knowing the route] helps.');
        p('In an -ing participle clause, [-tense] goes on the first -ing verb. Here it goes on “knowing”. Compare “is checking”, where “is” carries tense in a finite progressive.');
        break;
      case 'worked-example': {
        p('Return to the inspection example and look inside the smaller VP. The branch above “to” shows [-tense]. Its sister is the lexical VP that contains “inspect” and the object “the bridge”.');
        example('Nora plans [to inspect the bridge].');
        const fragment = lesson.worked_example.tree;
        const [to, lexical] = fragment.root.children;
        trace('Read the two verb phrases', [
          ['Find [-tense] above “to”', fragment, to.id, 'The branch above infinitival “to” carries [-tense].'],
          ['Find the lexical VP', fragment, lexical.id, '“Inspect the bridge” is the entire complement of “to”.'],
        ]);
        body.append(el('h3', repair.buildTitle));
        p('Drag from the higher VP to the detached lexical VP, or use Guide me. Then select Check my tree.');
        addBranchExercise(body, ui, repair);
        p('Compare “Nora walked to the bridge”. Here “to” is a preposition and “the bridge” is its NP complement.');
        break;
      }
      case 'subjects-and-control':
        p('An overt subject is expressed in words. A covert subject is understood. When it refers to people in general, it is free. When an overt element in the larger clause identifies it, that element is its controller.');
        example('[Knowing the route] helps. · Nia enjoys [checking the maps]. · Nia enjoys [Ivo checking the maps].');
        trace('Compare free, controlled and overt subjects', [
          ['Find the free subject', free, 'lower-subject-dot', 'The dot marks a free subject. The example makes a general statement about knowing the route.'],
          ['Find the controlled subject', controlled, 'lower-subject-dot', 'The matching 1s on Nia’s NP and the dot show that Nia is understood to check the maps.'],
          ['Find the overt subject', overt, 'lower-subject', '“Ivo” is expressed inside the non-finite clause and names who checks the maps.'],
        ]);
        p('A complementiser can mark the start of the clause. “For” goes in C1 with an overt subject. In the embedded question with “whether”, C1 is filled and the subject is silent. With “what”, C2 is filled and C1 is empty.');
        example('[For Ivo to wait outside] seemed unfair. · Nia wondered [whether to wait]. · Nia knew [what to pack].');
        trace('Locate C1 and C2 in infinitival clauses', [
          ['Find “for” in C1', forClause, 'for', '“For” fills C1. “Ivo” is the overt subject inside S.'],
          ['Find “whether” in C1', whetherClause, 'whether', '“Whether” introduces the embedded question. The silent subject is understood as Nia in the full sentence.'],
          ['Find “what” in C2', whatClause, 'what', '“What” fills C2 and corresponds to the object gap after “pack”. C1 has no word.'],
        ]);
        break;
      case 'clause-functions':
        p('Once the subject and verb are clear, ask how the clause fits into the larger structure.');
        example('[Checking the ropes] takes time.');
        p('The bracketed clause identifies what takes time. It functions as subject.');
        example('Nia insisted on [checking the ropes].');
        p('The clause completes “on”, so it is a complement of P inside PP. In this pattern, P takes the S directly.');
        example('Nia paused [to check the ropes].');
        p('The clause explains the purpose of pausing, so it functions as an adverbial. Non-finite clauses can also complete an adjective or noun, as in “eager to help” and “a request to speak”. In “the crates stacked by the door”, the participle clause modifies “crates”.');
        break;
      case 'verb-complements':
        p('The words after the main verb can look identical and still group differently. A Type I verb such as “expect” can take one clausal complement with its own overt subject. A Type II verb such as “persuade” takes an object and a clause whose subject is understood.');
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
        p('Ren is understood to leave in both examples. Decide which clause contains the overt NP “Ren” before revealing the bracketed analyses.');
        example('Nia expected Ren to leave. · Nia advised Ren to leave.');
        const answer = el('details', undefined, 'lesson-sources');
        answer.append(el('summary', 'Check both analyses'),
          lessonExample(el, 'Nia expected [Ren to leave]. · Nia advised [Ren] [to leave].'),
          el('p', 'With “expected”, Ren is the overt lower subject. With “advised”, Ren is the higher object and controls the silent lower subject.'));
        body.append(answer);
        break;
      }
      case 'recap':
        p('Find the untensed form first. The marker sits above infinitival “to” or on the untensed verb in the bare infinitive, passive participle and -ing examples.');
        p('Then find the lower subject. It may be overt, free or controlled. Matching indices link the overt controller to the silent position.');
        p('Finally, ask what the clause does. “Checking the ropes” can be a subject or complete a preposition. After a verb, check whether the following NP belongs inside the lower clause, as with “expected”, or is an object of the higher verb, as with “persuaded”.');
        break;
    }
  },
};
