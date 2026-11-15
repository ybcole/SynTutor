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
  hint.append(el('summary', 'Hint'), el('p', 'Find the direct object in each sentence. Does the other phrase tell who gets something? Or does it tell what the object is like?'));
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
    { id: 'introduction', title: 'Introduction to the basic verb phrase' },
    { id: 'concepts', title: 'Lexical verbs, complements, transitive and intransitive verbs', notationLabels: sentenceLabels, notationFeatures: ['trans', 'intrans'] },
    { id: 'worked-example', title: 'Ditransitive verbs', notationLabels: [...sentenceLabels, 'PP'], notationFeatures: ['ditrans'] },
    { id: 'predicatives', title: 'Intensive and complex transitive verbs', notationLabels: [...sentenceLabels, 'AP'], notationFeatures: ['intens', 'trans', 'complex'] },
    { id: 'prepositional-complements', title: 'Prepositional verbs and PP complements', notationLabels: [...sentenceLabels, 'PP'], notationFeatures: ['prep', 'intens'] },
    { id: 'application', title: 'Exercises on the six verb patterns' },
    { id: 'recap', title: 'Summary of the six verb patterns', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Lexical verb', 'The verb that gives the main action or state, or tells how things are related.'],
    ['Basic verb phrase (VP)', 'The group made up of a lexical verb and its complements.'],
    ['Complement', 'A word or group that fills a role its head calls for in that use.'],
    ['Direct object', 'A complement that often names who or what the verb acts on. It is usually an NP.'],
    ['Indirect object', 'A complement that often names who gets something or who benefits. It goes with a direct object.'],
    ['Predicative', 'A complement that tells who, what, or where the subject or direct object is, or what it is like.'],
    ['Prepositional complement', 'A PP that a verb calls for in a certain use. “Depend” takes “on the schedule” in “depend on the schedule”.'],
  ],
  teach(body, _page, ui) {
    const { el, lesson, section } = ui;
    const p = text => body.append(el('p', text));
    const heading = text => body.append(el('h3', text));
    const example = text => body.append(lessonExample(el, text));
    const trace = (label, steps) => addTreeTrace(body, ui, label, steps);

    if (section.id === 'introduction') {
      p('Chapter 3 showed how the head helps you name a phrase. Now look at the words that go with a verb. “Nora waited” makes sense with just the verb in its predicate. What goes with “inspected”? In this chapter, you’ll compare verbs by the groups they take and the jobs those groups do.');
      addIntroExample(body, el, 'The brackets mark the whole predicate. First find the word that gives the main action. Then look for what Nora inspected.',
        'Nora [inspected the bridge].',
        '“Inspected” gives the main action, so it is the lexical verb and the head of this VP. “The bridge” fills a role that “inspected” calls for here. That makes it a complement. Its job is direct object because it tells what Nora inspected.');
      heading('What you’ll see in this chapter');
      const list = el('ul');
      for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
      body.append(list);
    }
    if (section.id === 'concepts') {
      example('[Nora] [inspected the bridge].');
      p('Find “Nora” right under S. That NP is the subject. Inside VP, “the bridge” is the direct object. It tells what Nora inspected, and “it” can replace the whole NP. Here, “inspected” takes one direct object, so V has the transitive feature [trans].');
      p('In “Nora waited”, the verb alone makes the VP. “Waited” takes no object, so it is intransitive [intrans]. A verb can fit more than one pattern. Compare “The window opened” with “Rina opened the window”. Only the second has an object.');
      const inspection = lesson.worked_example.tree;
      const [subject, vp] = inspection.root.children;
      const object = vp.children[1];
      trace('Compare a basic VP with and without an object', [
        ['Find the subject', inspection, subject.id, '“Nora” is the subject NP directly under S.'],
        ['Trace the object', inspection, object.id, '“The bridge” and “inspected” share VP as their parent. The verb’s [trans] feature marks its use with one direct object.'],
        ['Compare the intransitive VP', waited, 'verb', 'In “Nora waited”, V [intrans] is the only immediate part of VP.'],
      ]);
      heading(repair.buildTitle);
      p('Attach “the bridge” so it shares a parent with “inspected”. Drag from that parent’s connection point or choose Guide me. Then select Check my tree.');
      addBranchExercise(body, ui, repair);
    }
    if (section.id === 'worked-example') {
      p('A transitive verb like “inspected” takes one direct object. A ditransitive verb takes two complements. The direct object can name the thing given. The indirect object can name the person who gets it or benefits from it.');
      example('Mara handed [Leo] [a map].');
      example('Mara handed [a map] [to Leo].');
      p('Mara hands over “a map” in both sentences. Leo is the recipient, the person who gets it. In the second sentence, the prepositional phrase (PP) “to Leo” names him.');
      p('Try naming the two roles before you look at their order. “A map” answers “What did Mara hand over?” and Leo answers “Who received it?” The construction can put the recipient before the map as an NP or after it as a “to” PP. This is why being first after the verb does not always make a group the direct object.');
      trace('Compare two ways to express the recipient', [
        ['Find the recipient NP', recipientNP, 'recipient', '“Leo” is the indirect object in NP form. It comes before the direct object.'],
        ['Find the direct object', recipientNP, 'object', '“A map” is the direct object. Both NPs are sisters of V [ditrans].'],
        ['Compare the recipient PP', recipientPP, 'recipient', '“To Leo” is the corresponding PP. It comes after “a map” and shares VP with the verb and the direct object. Some verbs allow a similar “for” phrase for a beneficiary.'],
      ]);
    }
    if (section.id === 'predicatives') {
      p('A complement can also tell what someone is like or where they are. A subject predicative gives information about the subject. A verb that takes a subject predicative has the intensive feature [intens].');
      example('Mina became [a coach].');
      example('Mina met [a coach].');
      p('Look at “a coach” in both sentences. In the first, it tells what Mina became. In the second, it is the direct object. It tells whom Mina met.');
      example('The rain left [the steps] [slippery].');
      p('What became slippery? The steps did. “Slippery” is an object predicative because it describes the direct object. When the verb has both of these complements, it is complex transitive [complex]. A subject or object predicative can be an NP, an adjective phrase (AP), or a PP.');
      p('Compare “The steps became slippery” with “The rain left the steps slippery”. The description is about the steps in both. In the first sentence, the steps are the subject, so “slippery” is a subject predicative. In the second, the steps are the direct object, so the same AP is an object predicative.');
      trace('Compare subject and object predicatives', [
        ['Identify the subject', became, 'description', '“A coach” identifies Mina. The NP is a subject predicative beside V [intens].'],
        ['Compare a direct object', met, 'object', '“A coach” refers to the person Mina met. The NP is a direct object beside V [trans].'],
        ['Describe the object', left, 'description', '“Slippery” describes “the steps”. The object NP and predicative AP each attach beside V [complex].'],
      ]);
    }
    if (section.id === 'prepositional-complements') {
      p('A PP can also fill a role that a verb calls for. In “relied on her notes”, the “on” phrase tells what Mina relied on. The verb “relied” calls for an “on” phrase here. We call it a prepositional complement and mark V with [prep].');
      example('Mina relied [on her notes].');
      example('Mina was [in the studio].');
      trace('Compare two PP complements', [
        ['Trace the selected PP', relied, 'complement', '“On her notes” names what Mina relied on. The PP is a prepositional complement beside V [prep].'],
        ['Trace the subject location', was, 'description', '“In the studio” locates Mina. The PP functions as a subject predicative beside V [intens].'],
      ]);
      example('Mina waited [in the studio].');
      p('Compare the last statement with “Mina waited”. “Waited” can be the whole predicate. The PP adds a place where she waited. Chapter 5 shows where to attach this kind of optional modifier.');
      p('One way to classify a PP after a verb is to ask what information it supplies. “On her notes” fills the slot selected by “relied”. “In the studio” after “was” describes the subject’s location. “In the studio” after “waited” adds the place where the waiting happened. These three PPs look similar but do different work.');
    }
    if (section.id === 'application') {
      p('Both sentences have two groups after the verb. Ask what job each group does to tell the patterns apart.');
      example('Ari showed [Ren] [the map].');
      example('Ari found [the map] [useful].');
      p('Name the direct object in each sentence. Then explain the role of the other group.');
      transfer(body, ui);
    }
    if (section.id === 'recap') {
      p('Split the sentence into subject and predicate. Find the lexical verb in the VP. Count its complements and name their jobs. Then choose the feature that shows the verb’s pattern.');
      const list = el('dl');
      for (const [feature, sample, analysis] of recap) list.append(el('dt', feature), el('dd', `${sample} ${analysis}.`));
      body.append(list);
      p('Phrase labels alone can look the same. Ask what each phrase does. “A coach” tells what Mina became in one sentence. In the other, it tells whom she met. The V features show those two patterns.');
    }
  },
};
