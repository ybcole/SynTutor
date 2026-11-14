import { addIntroExample, addTreeTrace, lessonExample } from './lesson-presentation.js';
import { addBranchExercise } from './lesson-tree-exercise.js';

const branch = (id, label, children) => ({ id, label, children });
const group = (id, label, text) => ({ id, label, triangle: true, words: text.split(' ') });

function sentence(subject, verb, feature, ...complements) {
  const v = { ...branch('verb', 'V', [{ word: verb }]), features: [feature] };
  return {
    sentence: [subject, verb, ...complements.flatMap(node => node.words)].join(' '),
    root: branch('sentence', 'S', [
      group('subject', 'NP', subject),
      branch('predicate', 'VP', [v, ...complements]),
    ]),
  };
}

const waited = sentence('Nora', 'waited', 'intrans');
const recipientNP = sentence('Mara', 'handed', 'ditrans', group('recipient', 'NP', 'Leo'), group('object', 'NP', 'a map'));
const recipientPP = sentence('Mara', 'handed', 'ditrans', group('object', 'NP', 'a map'), group('recipient', 'PP', 'to Leo'));
const became = sentence('Mina', 'became', 'intens', group('description', 'NP', 'a coach'));
const met = sentence('Mina', 'met', 'trans', group('object', 'NP', 'a coach'));
const left = sentence('The rain', 'left', 'complex', group('object', 'NP', 'the steps'), group('description', 'AP', 'slippery'));
const relied = sentence('Mina', 'relied', 'prep', group('complement', 'PP', 'on her notes'));
const was = sentence('Mina', 'was', 'intens', group('description', 'PP', 'in the studio'));
const sentenceLabels = ['S', 'NP', 'VP', 'V', '△'];

const repair = {
  buildTitle: 'Attach the direct object',
  build: {
    branch: root => [root.children[1], root.children[1].children[1]],
    action: 'Connect the object NP under VP',
    hint: 'Attach “the bridge” to VP beside V [trans]. “Nora” stays directly under S.',
    success: 'The object NP shares VP with V [trans]. The subject NP stays outside that VP.',
  },
};

const recap = [
  ['[trans]', 'Nora inspected the bridge.', 'One direct object'],
  ['[intrans]', 'Nora waited.', 'Zero complements'],
  ['[ditrans]', 'Mara handed Leo a map.', 'Indirect object and direct object'],
  ['[intens]', 'Mina became a coach.', 'One subject predicative'],
  ['[complex]', 'The rain left the steps slippery.', 'Direct object and object predicative'],
  ['[prep]', 'Mina relied on her notes.', 'One prepositional complement'],
];

function transfer(body, { el, button, userId, lesson }) {
  const hint = el('details', undefined, 'lesson-sources');
  hint.append(el('summary', 'Hint'), el('p', 'Find the direct object in each sentence. Then ask whether the other phrase names a recipient or describes the object.'));
  body.append(hint);

  const key = `syntutor:lesson-transfer:${userId}:${lesson.lesson_id}@${lesson.content_version}:application`;
  const label = el('label', 'Your explanation');
  label.htmlFor = 'chapter-four-transfer';
  const input = el('textarea');
  input.id = label.htmlFor;
  input.rows = 3;
  input.maxLength = 1200;
  try { input.value = localStorage.getItem(key) || ''; } catch { /* Practice remains available without storage. */ }
  const feedback = el('div', undefined, 'lesson-tree-observation');
  feedback.setAttribute('aria-live', 'polite');
  const answer = el('p');
  feedback.append(answer);
  const reveal = button('Compare your explanation', () => {
    answer.textContent = 'With “showed”, “Ren” is the recipient and indirect object, and “the map” is the direct object. With “found”, “the map” is still the direct object. “Useful” is an object predicative that describes it.';
  });
  reveal.disabled = !input.value.trim();
  input.addEventListener('input', () => {
    reveal.disabled = !input.value.trim();
    try { localStorage.setItem(key, input.value); } catch { /* Keep the current response in the field. */ }
  });
  const practice = el('div', undefined, 'lesson-pilot-transfer');
  practice.append(label, input, reveal, feedback);
  body.append(practice);
}

export const basicVpPilot = {
  description: 'Look inside a verb phrase. Compare six patterns to see which complements a verb takes and what each one does.',
  references: [
    'Chapter 4, printed pp. 67–72, figures [21–22] · Lexical verbs, direct objects and intransitive VPs',
    'Printed pp. 72–74, figures [26], [32] · Ditransitive VPs and the two recipient patterns',
    'Printed pp. 74–78, figures [46a–b], [51] · Subject and object predicatives',
    'Printed pp. 78–79, figure [56] and summary · Prepositional complements and the six patterns',
  ],
  sections: [
    { id: 'introduction', title: 'What belongs inside a verb phrase?' },
    { id: 'concepts', title: 'Find the verb and its complements', notationLabels: sentenceLabels, notationFeatures: ['trans', 'intrans'] },
    { id: 'worked-example', title: 'Follow both objects', notationLabels: [...sentenceLabels, 'PP'], notationFeatures: ['ditrans'] },
    { id: 'predicatives', title: 'Find what the phrase describes', notationLabels: [...sentenceLabels, 'AP'], notationFeatures: ['intens', 'trans', 'complex'] },
    { id: 'prepositional-complements', title: 'Compare three uses of PPs', notationLabels: [...sentenceLabels, 'PP'], notationFeatures: ['prep', 'intens'] },
    { id: 'application', title: 'Explain two verb patterns' },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Lexical verb', 'A verb that supplies the main action, event, state or relation in a clause.'],
    ['Basic verb phrase (VP)', 'A phrase centred on a lexical verb, considered together with the complements it takes.'],
    ['Complement', 'A word or group that fills a grammatical role licensed by its head in a particular use.'],
    ['Direct object', 'A complement typically expressed as a noun phrase that names the person or thing involved in the action or relation.'],
    ['Indirect object', 'A complement that typically expresses the recipient or beneficiary in a verb pattern with a direct object.'],
    ['Predicative', 'A complement that identifies, describes or locates the subject or the direct object.'],
    ['Prepositional complement', 'A prepositional phrase selected by a verb in a particular use, such as “on the schedule” in “depend on the schedule”.'],
  ],
  teach(body, _page, ui) {
    const { el, lesson, section } = ui;
    const p = text => body.append(el('p', text));
    const heading = text => body.append(el('h3', text));
    const example = text => body.append(lessonExample(el, text));
    const trace = (label, steps) => addTreeTrace(body, ui, label, steps);

    if (section.id === 'introduction') {
      p('Chapter 2 showed how a basic sentence divides into a subject and a predicate. The predicate is a verb phrase (VP). Here the focus is the basic VP, built around a lexical verb. A lexical verb supplies the main action, event, state or relation. Auxiliary verbs such as “might” can accompany a lexical verb, as in “might inspect”. Chapter 6 shows how auxiliaries fit into the tree.');
      addIntroExample(body, el, 'The brackets enclose the whole predicate in this inspection example.',
        'Nora [inspected the bridge].',
        '“Inspected” is the lexical head. It takes “the bridge” as a complement. A complement fills a role the head allows in a particular use. Here that role is the direct object, which names what Nora inspected.');
      heading('What you’ll see in this chapter');
      const list = el('ul');
      for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
      body.append(list);
    }
    if (section.id === 'concepts') {
      example('[Nora] [inspected the bridge].');
      p('The subject “Nora” is an NP directly under S, the sentence node. The direct object “the bridge” is the NP inside the VP. Replacing it with “it” leaves the rest of the sentence intact. In this use, “inspected” takes one direct object, so the verb carries the transitive feature [trans].');
      p('Compare “Nora waited”. The lexical verb alone can fill the VP. In this use, “waited” is intransitive [intrans]. A verb can appear in different patterns. “The window opened” has no object. “Rina opened the window” has one.');
      const inspection = lesson.worked_example.tree;
      const [subject, vp] = inspection.root.children;
      const object = vp.children[1];
      trace('Compare a basic VP with and without an object', [
        ['Find the subject', inspection, subject.id, '“Nora” is the subject NP directly under S.'],
        ['Trace the object', inspection, object.id, '“The bridge” and “inspected” share VP as their parent. The verb’s [trans] feature marks its use with one direct object.'],
        ['Compare the intransitive VP', waited, 'verb', 'In “Nora waited”, V [intrans] is the only immediate part of VP.'],
      ]);
      heading(repair.buildTitle);
      p('Connect the detached NP “the bridge” to the same parent as “inspected”. Drag from the parent’s connection point, or use Guide me. Then select Check my tree.');
      addBranchExercise(body, ui, repair);
    }
    if (section.id === 'worked-example') {
      p('A transitive verb has one direct object in the pattern just practised. A ditransitive verb has two complements. One is the direct object and the other is the indirect object, which typically names a recipient or beneficiary.');
      example('Mara handed [Leo] [a map].');
      example('Mara handed [a map] [to Leo].');
      p('Both sentences describe the same transfer. “A map” is what Mara handed over. “Leo” identifies the recipient. In the second version, the recipient is expressed by a prepositional phrase (PP) after the direct object.');
      trace('Compare two ways to express the recipient', [
        ['Find the recipient NP', recipientNP, 'recipient', '“Leo” is the indirect object in NP form. It comes before the direct object.'],
        ['Find the direct object', recipientNP, 'object', '“A map” is the direct object. Both NPs are sisters of V [ditrans].'],
        ['Compare the recipient PP', recipientPP, 'recipient', '“To Leo” is the corresponding PP. It comes after “a map” and shares VP with the verb and the direct object. Some verbs allow a similar “for” phrase for a beneficiary.'],
      ]);
    }
    if (section.id === 'predicatives') {
      p('The last page used two phrases for two roles in a transfer. A complement can also tell what a participant is like. A subject predicative identifies, describes or locates the subject. A verb that takes a subject predicative has the intensive feature [intens].');
      example('Mina became [a coach].');
      example('Mina met [a coach].');
      p('The same NP, “a coach”, has a different role in each statement. In the first it identifies Mina after a change. In the second it refers to the person Mina met and functions as direct object.');
      example('The rain left [the steps] [slippery].');
      p('Here “slippery” describes the steps. A complement that describes or identifies the direct object is an object predicative. The combination of a direct object and an object predicative gives the verb the complex transitive feature [complex]. In these two patterns, a predicative can be an NP, an adjective phrase (AP), or a PP.');
      trace('Compare subject and object predicatives', [
        ['Identify the subject', became, 'description', '“A coach” identifies Mina. The NP is a subject predicative beside V [intens].'],
        ['Compare a direct object', met, 'object', '“A coach” refers to the person Mina met. The NP is a direct object beside V [trans].'],
        ['Describe the object', left, 'description', '“Slippery” describes “the steps”. The object NP and predicative AP each attach beside V [complex].'],
      ]);
    }
    if (section.id === 'prepositional-complements') {
      p('The previous page showed how a phrase can describe a participant. A PP can do that too. A PP can also fill a role selected by a particular verb. In “relied on her notes”, “relied” selects an “on” phrase to name what Mina relied on. That PP is a prepositional complement, and V carries [prep].');
      example('Mina relied [on her notes].');
      example('Mina was [in the studio].');
      trace('Compare two PP complements', [
        ['Trace the selected PP', relied, 'complement', '“On her notes” names what Mina relied on. The PP is a prepositional complement beside V [prep].'],
        ['Trace the subject location', was, 'description', '“In the studio” locates Mina. The PP functions as a subject predicative beside V [intens].'],
      ]);
      example('Mina waited [in the studio].');
      p('Compare the last statement with “Mina waited”. The waiting already forms a complete predicate. The PP adds an optional location for the event. Chapter 5 shows where that kind of modifier attaches.');
    }
    if (section.id === 'application') {
      p('Both examples contain two groups after the verb. Use the jobs of those groups to tell the patterns apart.');
      example('Ari showed [Ren] [the map].');
      example('Ari found [the map] [useful].');
      p('Name the direct object in each sentence. Then explain the role of the other group.');
      transfer(body, ui);
    }
    if (section.id === 'recap') {
      p('Separate the subject from the predicate, then find the lexical verb inside the VP. Count the verb’s complements and identify what each does. Use the feature on V to record the pattern in that sentence.');
      const list = el('dl');
      for (const [feature, sample, analysis] of recap) list.append(el('dt', feature), el('dd', `${sample} ${analysis}.`));
      body.append(list);
      p('When two VPs have the same phrase labels, check the functions. “A coach” identifies Mina in “Mina became a coach”. In “Mina met a coach”, the same words name the person she met. The different functions explain the different features on V.');
    }
  },
};
