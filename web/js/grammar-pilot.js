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
    ['Grammar', 'Rules that tell which word sequences count as sentences and how they are built.'],
    ['Recursion', 'Using the result of a rule as a new input to the same rule.'],
    ['Derivation', 'The steps that show how rules build a structure.'],
    ['Phrase marker', 'A tree or set of labelled brackets that shows the groups in a sentence.'],
    ['Generative grammar', 'A grammar that tells which sentences its rules allow and shows the structure of each one.'],
  ],
  teach(body, _page, ui) {
    const { el, lesson, section } = ui;
    const p = text => body.append(el('p', text));
    const example = text => body.append(lessonExample(el, text));
    switch (section.id) {
      case 'introduction': {
        p('Trees show how words group together. A grammar gives rules for which groups can go together and in what order. See how a few rules can describe sentences you have never seen before.');
        addIntroExample(body, el, 'The brackets mark two complete sentences joined by “and”.',
          '[Iris rests] and [Leo waits].',
          'The rule joins the two sentences to make a new one. You can use that new sentence in the same rule again.');
        body.append(el('h3', 'What you’ll see in this chapter'));
        const list = el('ul');
        for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
        body.append(list);
        break;
      }
      case 'concepts':
        p('Ask which word orders make sentences in a language. English speakers use different patterns in different varieties. A grammar describes the patterns of the variety it is built for.');
        p('Imagine a made-up language with only three sentences. They are “Iris rests”, “Leo waits”, and “Mina waves”. Its list tells you exactly which sentences belong. “Iris rests and Leo waits” is missing from the list.');
        example('S → S and S');
        p('Keep the three sentences and add a rule. Join two sentences, each marked S, to make a new S. Then you can use that new S in the same rule again. This is recursion. Each sentence ends, but the rule gives no limit on how long a sentence can grow.');
        break;
      case 'worked-example':
        p('A derivation shows the steps that build a structure. Join the first two sentences. Then follow that whole group into the next step.');
        addTreeTrace(body, ui, 'Trace the two rule applications', [
          ['Join two starting sentences', first, 'first', 'The rule joins “Iris rests” and “Leo waits”. The result is an S.'],
          ['Reuse the first result', second, 'first', 'The earlier S stays together as the first input. “Mina waves” is the second input.'],
          ['Read the new sentence', second, 'second', 'The larger S joins the earlier group to “Mina waves”. You can use this new S in the rule again.'],
        ]);
        p('The tree shows one way to build the sentence. You can get the same words in the same order by joining “Leo waits” and “Mina waves” first.');
        break;
      case 'apply-the-rule':
        p('Pick two complete sentences. Join them, then use the result with a third sentence. Try the unfinished choice to see what the rule still needs.');
        addCombinationPractice(body, ui, base, 'Iris rests and', { showDerivation: true });
        break;
      case 'rule-and-structure':
        p('A phrase marker shows the groups in a string of words. A rule says which groups can go together and which goes first. Try this with a second small grammar.');
        example('S → NP VP · NP → DET N · VP → V');
        p('Here DET can be “the”, N can be “dog”, and V can be “waits”. The first rule places NP before VP.');
        example('[The dog] [waits].');
        example('[Waits] [the dog].');
        p('The first line follows the rule. “The dog” is NP and “waits” is VP, so NP comes first. The second line puts VP first, so this toy grammar has no derivation for it. You can still put brackets around both groups. The rule explains why their order matters.');
        break;
      case 'application': {
        p('The starting list has “Mina waves” and “Leo waits”. Can the rule build the sentence below? Say which two inputs it needs, then check.');
        example('Mina waves and Leo waits.');
        const answer = el('details', undefined, 'lesson-sources');
        answer.append(el('summary', 'Check the derivation'),
          lessonExample(el, '[S [S Mina waves] and [S Leo waits]]'),
          el('p', 'Both inputs are on the base list. One rule application builds the new S. Speakers can also recognize many unfamiliar sentences by applying grammatical patterns they know implicitly.'));
        body.append(answer);
        break;
      }
      case 'recap':
        p('A list can cover a small set of sentences. A recursive rule can describe an unbounded set, with no fixed size. Every new S can go back into the rule again.');
        p('A generative grammar does two things. It says which word sequences the rules allow and shows how each is built. The tree shows the groups. The derivation shows the steps that made them.');
        break;
    }
  },
};
