import { addIntroExample, addTreeTrace, lessonExample } from './lesson-presentation.js';
import { addCombinationPractice } from './foundations-practice.js';

const base = ['Iris rests', 'Leo waits', 'Mina waves'];
const sentence = (id, text) => ({ id, label: 'S', triangle: true, words: text.split(' ') });
const join = (id, first, second) => ({ id, label: 'S', children: [first, { word: 'and' }, second] });
const first = { sentence: 'Iris rests and Leo waits', root: join('first', sentence('iris', base[0]), sentence('leo', base[1])) };
const second = { sentence: 'Iris rests and Leo waits and Mina waves', root: join('second', first.root, sentence('mina', base[2])) };

export const grammarPilot = {
  description: 'Use a small grammar to form new sentences and explain how the same rules determine their structure.',
  references: [
    'Chapter 11, printed pp. 254–259 · Languages, variation and finite lists',
    'Printed pp. 259–262, coordination diagrams on p. 260 · Rules and repeated combination',
    'Printed pp. 262–265 · What a grammar describes and what speakers know',
    'Printed pp. 265–268, [11–12] · Phrase markers and generative grammar',
  ],
  sections: [
    { id: 'introduction', title: 'What does a grammar describe?' },
    { id: 'concepts', title: 'Compare a list with a rule' },
    { id: 'worked-example', title: 'Trace two applications', notationLabels: ['S', '△'] },
    { id: 'apply-the-rule', title: 'Apply the rule' },
    { id: 'rule-and-structure', title: 'Explain what the rules license' },
    { id: 'application', title: 'Derive a new sentence' },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Grammar', 'A system of rules that specifies which sequences are sentences and how those sentences are structured.'],
    ['Recursion', 'A pattern in which an output can serve as an input to the same rule.'],
    ['Derivation', 'The steps that show how a grammar builds a structure from its rules and starting elements.'],
    ['Phrase marker', 'A tree or labelled bracketing that represents a sentence’s structure.'],
    ['Generative grammar', 'A grammar that specifies permitted sentences and gives them structural descriptions.'],
  ],
  teach(body, _page, ui) {
    const { el, lesson, section } = ui;
    const p = text => body.append(el('p', text));
    const example = text => body.append(lessonExample(el, text));
    switch (section.id) {
      case 'introduction': {
        p('Earlier chapters used trees to show how words group together. A grammar states the rules that permit those groups and orders. This chapter asks how a small set of rules can describe sentences a learner has never encountered.');
        addIntroExample(body, el, 'The brackets mark two complete sentences joined by “and”.',
          '[Iris rests] and [Leo waits].',
          'The two inputs form a new sentence. If the new sentence can be an input to the same rule, the process can continue.');
        body.append(el('h3', 'What you’ll see in this chapter'));
        const list = el('ul');
        for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
        body.append(list);
        break;
      }
      case 'concepts':
        p('One way to study a language is to ask which sequences count as sentences in it. Speakers of different English varieties may have different patterns, so a grammar describes the variety it is intended to model.');
        p('Imagine a toy language whose entire list is “Iris rests”, “Leo waits” and “Mina waves”. The list answers whether any sequence belongs to that tiny language. “Iris rests and Leo waits” is absent from it.');
        example('S → S and S');
        p('Add this rule while keeping the three starting sentences. It combines two sentences, labelled S, into another S. Recursion means that this result can serve as an input again. Each step produces a finite sentence, and the rule sets no maximum length.');
        break;
      case 'worked-example':
        p('A derivation records how a rule builds a structure. Trace the first combination, then see where it goes in the next step.');
        addTreeTrace(body, ui, 'Trace the two rule applications', [
          ['Join two starting sentences', first, 'first', 'The rule joins “Iris rests” and “Leo waits”. The result is an S.'],
          ['Reuse the first result', second, 'first', 'The earlier S stays together as the first input. “Mina waves” is the second input.'],
          ['Read the new sentence', second, 'second', 'The larger S groups the earlier result with “Mina waves”. It can be used in another application.'],
        ]);
        p('The diagram records this particular derivation. The same words can also be grouped by joining “Leo waits” with “Mina waves” first.');
        break;
      case 'apply-the-rule':
        p('Choose two complete inputs, then reuse their result with a third sentence. Try the unfinished input and read which part the rule still requires.');
        addCombinationPractice(body, ui, base, 'Iris rests and', { showDerivation: true });
        break;
      case 'rule-and-structure':
        p('A phrase marker describes the groups in a sequence. A rule also specifies which groups can combine and in what order. Try a separate toy grammar for a simple statement.');
        example('S → NP VP · NP → DET N · VP → V');
        p('Here DET can be “the”, N can be “dog”, and V can be “waits”. The first rule places NP before VP.');
        example('[The dog] [waits].');
        example('[Waits] [the dog].');
        p('The first sequence can be derived: “the dog” is NP and “waits” is VP. The second reverses them, so this toy grammar has no derivation for it. Bracketing the reversed sequence still describes two groups. To explain which order is permitted, the grammar needs a rule.');
        break;
      case 'application': {
        p('The base list includes “Mina waves” and “Leo waits”. Can the rule derive the combined sentence below? Identify the inputs before checking.');
        example('Mina waves and Leo waits.');
        const answer = el('details', undefined, 'lesson-sources');
        answer.append(el('summary', 'Check the derivation'),
          lessonExample(el, '[S [S Mina waves] and [S Leo waits]]'),
          el('p', 'Both inputs are on the base list. One rule application builds the new S. Speakers can also recognize many unfamiliar sentences by applying grammatical patterns they know implicitly.'));
        body.append(answer);
        break;
      }
      case 'recap':
        p('A complete list can describe a small fixed set. A recursive rule can describe an unbounded set because each new S can become an input to the same rule.');
        p('A generative grammar does two jobs. It specifies which sequences its rules permit and gives those sequences a structural description. A tree records the grouping, while the derivation explains how the rules build it.');
        break;
    }
  },
};
