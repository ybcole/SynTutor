import { addConstituentTreeBuilder } from './constituent-tree-builder.js';
import { addIntroExample, setTreeStepLabel } from './lesson-presentation.js';

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
  const buttons = views.map(({ label, step }, index) => {
    const control = button(label, () => select(index));
    if (step) setTreeStepLabel(control, el, label, step);
    return control;
  });
  function select(index) {
    const { tree, focusId, caption } = views[index];
    buttons.forEach((item, i) => item.setAttribute('aria-pressed', String(i === index)));
    showDiagram(canvas, tree, { focusId, highlightWords: true });
    captionText.textContent = caption;
  }
  controls.append(...buttons);
  figure.append(controls, canvas, observation);
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
    { id: 'introduction', title: 'Words form groups' },
    { id: 'concepts', title: 'Structure and constituent tests' },
    { id: 'worked-example', title: 'Read and repair a phrase marker' },
    { id: 'application', title: 'Explain two readings' },
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
    const disclosure = (title, explanation) => {
      const details = el('details', undefined, 'lesson-sources');
      details.append(el('summary', title), el('p', explanation));
      body.append(details);
    };

    if (page === 0) {
      paragraph('When you read a sentence, some words make sense as a group. How can you tell which words go together? In this chapter, you’ll test groups by leaving words out, swapping them for a single word, and asking what question they answer.');
      addIntroExample(body, el, 'Read the sentence below. The outer brackets mark where Mina paused. The inner brackets mark the landmark inside that location.',
        'Mina paused [near [the stone arch]].',
        '“The stone arch” names the landmark. Add “near” and the whole phrase tells where Mina paused. A constituent is a word or group that works as one unit. Both bracketed groups are constituents. The way one group fits inside the other is called hierarchy.');
      heading('What you’ll see in this chapter');
      const list = el('ul');
      for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
      body.append(list);
    }
    if (page === 1) {
      paragraph('The brackets suggest two groups. Try changing one group at a time to see which words belong together.');
      example(sentence);
      heading('Omit the location or replace it');
      paragraph('First, leave out “near the stone arch”. “Mina paused” is still a complete sentence. Now put “there” in its place. In “Mina paused there”, one word stands for the whole location.');
      heading('Find the smaller group');
      paragraph('This time, keep “near”. In “Mina paused near it”, “it” stands for “the stone arch”. Ask “What did Mina pause near?” The answer is “the stone arch”. Ask “Where did Mina pause?” The answer is “near the stone arch”. The second answer includes one more word.');
      heading('Check the same words in a longer sentence');
      example('Mina paused near the stone arch that spans the canal.');
      paragraph('Suppose “that spans the canal” tells which arch Mina paused near. Then the answer to “What did Mina pause near?” is “the stone arch that spans the canal”. The whole location now includes those extra words.');
      disclosure('Try the question test', 'Where did Mina pause? “Near the stone arch that spans the canal.” The longer landmark sits inside the longer location phrase.');
    }
    if (page === 2) {
      paragraph('A phrase marker is a tree that shows which words belong together. A node is a point on the tree. It can have a label and branches below it. Here, PHRASE-a labels the big group. PHRASE-b labels the smaller group inside it.');
      example(sentence);
      paragraph('A node dominates everything its branches reach below it. It immediately dominates anything it reaches in one branch. In each tree, look for a node that reaches just the three words naming the landmark.');
      const nested = locationTree(true);
      comparison(body, ui, 'Compare the phrase markers', [
        { label: 'Trace the flat drawing', step: 1, tree: locationTree(false), focusId: 'PHRASE-a',
          caption: 'All four words sit right under PHRASE-a. There is no smaller node for the landmark.' },
        { label: 'Trace the landmark', step: 2, tree: nested, focusId: 'PHRASE-b',
          caption: 'PHRASE-b reaches exactly three words, “the stone arch”. That is the group you found with the tests.' },
        { label: 'Trace the outer phrase', step: 3, tree: nested, focusId: 'PHRASE-a',
          caption: 'PHRASE-a immediately dominates “near” and PHRASE-b. To reach the landmark words, follow another branch down from PHRASE-b.' },
      ]);
      paragraph('A triangle stands for a whole group. It hides the branches inside that group. Here, the branches are drawn so you can follow them to each word.');
      heading('Repair a flat tree');
      paragraph('Put the words “the red gate” under their own node. Keep “beside” right under the outer node. Choose Guide me if you need help.');
      addConstituentTreeBuilder(body, ui);
    }
    if (page === 3) {
      paragraph('The same words can have two meanings when they group in two ways. This is structural ambiguity. In the next example, who might have the binoculars?');
      example('Nina spotted the climber with binoculars.');
      paragraph('The trees show the part where the grouping changes. In each tree, start at PHRASE-c and follow one branch up. See which group contains “with binoculars”.');
      comparison(body, ui, 'Compare the two readings', [
        { label: 'Nina used binoculars', tree: ambiguityTree(false), focusId: 'PHRASE-a',
          caption: 'The binoculars phrase joins the group that includes “spotted”. It describes how Nina spotted the climber.' },
        { label: 'The climber had binoculars', tree: ambiguityTree(true), focusId: 'PHRASE-b',
          caption: 'The binoculars phrase joins the climber group. It helps identify which climber Nina spotted.' },
      ]);
      heading('Try another sentence');
      example('Ivo sketched the guide with a pencil.');
      paragraph('Explain both meanings. In each one, which group does “with a pencil” belong to?');
      disclosure('Hint', 'Ask whether the pencil explains how the sketch was made or helps identify the guide.');
      const key = `syntutor:lesson-transfer:${ui.userId}:br-01@${lesson.content_version}:application`;
      const label = el('label', 'Your explanation');
      label.htmlFor = 'chapter-one-transfer';
      const response = el('textarea');
      response.id = label.htmlFor;
      response.rows = 3;
      response.maxLength = 1200;
      try { response.value = localStorage.getItem(key) || ''; }
      catch { /* The learner can still write an explanation. */ }
      response.addEventListener('input', () => {
        try { localStorage.setItem(key, response.value); }
        catch { /* Keep the current response in the field. */ }
      });
      const feedback = el('div', undefined, 'lesson-tree-observation');
      const answer = el('p');
      feedback.append(answer);
      answer.setAttribute('role', 'status');
      const reveal = ui.button('Compare your explanation', () => {
        answer.textContent = 'When “with a pencil” joins the sketching group, Ivo used it to draw. When it joins “the guide”, the guide is the person with the pencil.';
      });
      reveal.disabled = !response.value.trim();
      response.addEventListener('input', () => { reveal.disabled = !response.value.trim(); });
      const practice = el('div', undefined, 'lesson-pilot-transfer');
      practice.append(label, response, reveal, feedback);
      body.append(practice);
    }
    if (page === 4) {
      paragraph('Start with a group you think belongs together. Try leaving it out, replacing it, moving it, or asking a question it answers. Check what happens in that sentence.');
      paragraph('Mark the words in the group. In a tree, follow the branches down from its node. They should reach exactly those words. One branch leads to an immediate part. More branches lead to parts inside that part.');
      paragraph('If the same words have two meanings, show where the grouping changes. Ask what the phrase tells you each time. Then find where its branch joins the tree.');
    }
  },
};
