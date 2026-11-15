import { addConstituentTreeBuilder } from './constituent-tree-builder.js';
import { addExplanationPractice, addIntroExample, addTreeTrace, lessonReflection } from './lesson-presentation.js';

const sentence = 'Mina paused near the stone arch.';
const word = (text, index) => ({ id: `word-${index}`, word: text });
const phrase = (label, ...children) => ({ id: label, label, children });

function locationTree(nested) {
  const [near, ...landmark] = ['near', 'the', 'stone', 'arch'].map(word);
  return { sentence: 'near the stone arch', root: phrase('PHRASE-a', near, ...(nested ? [phrase('PHRASE-b', ...landmark)] : landmark)) };
}

function ambiguityTree(climberHasBinoculars) {
  const [spotted, the, climber, withWord, binoculars] = 'spotted the climber with binoculars'.split(' ').map(word);
  const instrument = phrase('PHRASE-c', withWord, binoculars);
  const person = phrase('PHRASE-b', the, climber, ...(climberHasBinoculars ? [instrument] : []));
  return { sentence: 'spotted the climber with binoculars', root: phrase('PHRASE-a', spotted, person, ...(climberHasBinoculars ? [] : [instrument])) };
}

function comparison(body, { el, button, showDiagram }, name, views) {
  const figure = el('div', undefined, 'constituent-diagram');
  const controls = el('div', undefined, 'constituent-controls lesson-tree-steps');
  controls.setAttribute('role', 'group');
  controls.setAttribute('aria-label', name);
  const canvas = el('div');
  const observation = el('div', undefined, 'lesson-tree-observation');
  const captionText = el('p');
  observation.append(captionText);
  observation.setAttribute('aria-live', 'polite');
  const buttons = views.map(({ label }, index) => button(label, () => select(index)));
  function select(index) {
    const { tree, focusId, caption } = views[index];
    buttons.forEach((item, i) => item.setAttribute('aria-pressed', String(i === index)));
    showDiagram(canvas, tree, { focusId, highlightWords: true, observation });
    captionText.textContent = caption;
  }
  controls.append(...buttons);
  figure.append(controls, canvas);
  body.append(figure);
  select(0);
}

export const constituentsPilot = {
  references: [
    'Chapter 1, printed pp. 6–10 · Structure and immediate parts',
    'Printed pp. 10–15 · Omission, replacement, questions and candidate phrase markers [25a–c]',
    'Printed pp. 15–18 · Grouping in context, phrase markers [34–35] and ambiguity [36]',
  ],
  sections: [
    { id: 'introduction', title: 'Introduction to sentence structure and constituents' },
    { id: 'concepts', title: 'Structure and constituent tests' },
    { id: 'worked-example', title: 'Phrases, constituents and phrase markers' },
    { id: 'application', title: 'Structural ambiguity exercises' },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Constituent', 'A word or group of words that works as one unit.'],
    ['Phrase', 'A group of words that works as one unit. A phrase can also be just one word.'],
    ['Hierarchy', 'The way small groups fit inside bigger groups.'],
    ['Phrase marker', 'A tree that shows which words belong together.'],
    ['Dominance', 'A node dominates what its branches reach below it. It immediately dominates what it reaches in one branch.'],
    ['Structural ambiguity', 'When the same words can mean different things because they group in different ways.'],
  ],
  teach(body, page, ui) {
    const { el, lesson } = ui;
    const paragraph = text => body.append(el('p', text));
    const heading = title => body.append(el('h3', title));
    const example = text => body.append(el('p', text, 'lesson-example-sentence'));

    if (page === 0) {
      paragraph('When you read a sentence, some words work together as one unit. A word or group with that job is called a constituent. How can you tell which words go together? In this chapter, you’ll test groups by leaving words out, swapping them for a single word, and asking what question they answer.');
      addIntroExample(body, el, 'In the example below, the outer brackets mark where Mina paused. The inner brackets mark the landmark inside that location.',
        'Mina paused [near [the stone arch]].',
        '“The stone arch” names the landmark. Add “near” and the whole phrase tells where Mina paused. Both bracketed groups work as units, so both are constituents. The way one group fits inside the other is called hierarchy.');
      heading('What you’ll learn in this chapter');
      const list = el('ul');
      for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
      body.append(list);
    }
    if (page === 1) {
      paragraph('A constituency test checks whether a stretch of words works as a unit. The brackets in the example below suggest two groups. Try changing one group at a time to check them.');
      paragraph('A useful test changes one group while keeping the rest of the sentence steady. If one word such as “there” can stand for the whole location, that is evidence that those words work together. Try a second test when the first one is uncertain. A group can be a constituent even if the sentence needs it.');
      example(sentence);
      heading('Omit the location or replace it');
      paragraph('First, leave out “near the stone arch”. “Mina paused” is still a complete sentence. Now put “there” in its place. In “Mina paused there”, one word stands for the whole location.');
      heading('Find the smaller group');
      paragraph('This time, keep “near”. In “Mina paused near it”, “it” stands for “the stone arch”. Ask “What did Mina pause near?” The answer is “the stone arch”. Ask “Where did Mina pause?” The answer is “near the stone arch”. The second answer includes one more word.');
      heading('Check the same words in a longer sentence');
      example('Mina paused near the stone arch that spans the canal.');
      paragraph('Suppose “that spans the canal” tells which arch Mina paused near. Then the answer to “What did Mina pause near?” is “the stone arch that spans the canal”. The whole location now includes those extra words.');
      body.append(lessonReflection(el,
        'Mina paused at an arch. This longer sentence adds words to identify which arch it was.',
        'Where did Mina pause? Give the whole location, including the words that identify the arch.',
        '“Near the stone arch that spans the canal” answers where she paused. “The stone arch that spans the canal” answers what she paused near. The two answers show the smaller group inside the larger one.'));
    }
    if (page === 2) {
      paragraph('A phrase marker is a tree that shows which words belong together. A node is a point on the tree. It can have a label and branches below it. In the example below, PHRASE-a labels the whole location. In the nested tree, PHRASE-b labels the landmark inside it.');
      example(sentence);
      paragraph('A node dominates everything its branches reach below it. It immediately dominates anything it reaches in one branch. In each tree, look for a node that reaches just the three words naming the landmark.');
      paragraph('Start at PHRASE-a and follow just one branch. In the nested drawing, you can reach “near” or the PHRASE-b node in one move. You need another move to reach “arch”. That is why PHRASE-a dominates “arch” without immediately dominating it.');
      const nested = locationTree(true);
      addTreeTrace(body, ui, 'Compare the phrase markers', [
        ['Trace the flat drawing', locationTree(false), 'PHRASE-a',
          'All four words sit right under PHRASE-a. There is no smaller node for the landmark.'],
        ['Trace the landmark', nested, 'PHRASE-b',
          'PHRASE-b reaches exactly three words, “the stone arch”. That is the group you found with the tests.'],
        ['Trace the outer phrase', nested, 'PHRASE-a',
          'PHRASE-a immediately dominates “near” and PHRASE-b. To reach the landmark words, follow another branch down from PHRASE-b.'],
      ], { wordBaseline: 0 });
      paragraph('A triangle stands for a whole group. It hides the branches inside that group. Here, the branches are drawn so you can follow them to each word.');
      heading('Repair a flat tree');
      paragraph('Put the words “the red gate” under their own node. Keep “beside” right under the outer node. Choose Guide me if you need help.');
      addConstituentTreeBuilder(body, ui);
    }
    if (page === 3) {
      paragraph('The same words can have two meanings when they group in two ways. This is structural ambiguity. In the next example, who might have the binoculars?');
      example('Nina spotted the climber with binoculars.');
      paragraph('The trees show the part where the grouping changes. In each tree, start at PHRASE-c and follow one branch up. See which group contains “with binoculars”.');
      paragraph('In both readings, “with binoculars” is the same group. The question is what it joins. Picture Nina looking through binoculars, then picture a climber wearing them. Those two situations give you a reason to draw a different attachment.');
      comparison(body, ui, 'Compare the two readings', [
        { label: 'Nina used binoculars', tree: ambiguityTree(false), focusId: 'PHRASE-a',
          caption: 'The binoculars phrase joins the group that includes “spotted”. It describes how Nina spotted the climber.' },
        { label: 'The climber had binoculars', tree: ambiguityTree(true), focusId: 'PHRASE-b',
          caption: 'The binoculars phrase joins the climber group. It helps identify which climber Nina spotted.' },
      ]);
      heading('Try another sentence');
      example('Ivo sketched the guide with a pencil.');
      paragraph('Explain both meanings. In each one, which group does “with a pencil” belong to?');
      paragraph('Ask whether the pencil explains how the sketch was made or helps identify the guide.');
      const key = `syntutor:lesson-transfer:${ui.userId}:br-01@${lesson.content_version}:application`;
      addExplanationPractice(body, ui, {
        key, id: 'chapter-one-transfer',
        explanation: 'When “with a pencil” joins the sketching group, Ivo used it to draw. When it joins “the guide”, the guide is the person with the pencil.',
      });
    }
    if (page === 4) {
      paragraph('Start with a group you think belongs together. Try leaving it out, replacing it, moving it, or asking a question it answers. Check what happens in that sentence.');
      paragraph('Mark the words in the group. In a tree, follow the branches down from its node. They should reach exactly those words. One branch leads to an immediate part. More branches lead to parts inside that part.');
      paragraph('If the same words have two meanings, show where the grouping changes. Ask what the phrase tells you each time. Then find where its branch joins the tree.');
    }
  },
};
