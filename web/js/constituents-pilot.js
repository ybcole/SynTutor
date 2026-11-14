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
    { id: 'concepts', title: 'Test a group in context' },
    { id: 'worked-example', title: 'Read and repair a phrase marker' },
    { id: 'application', title: 'Explain two readings' },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Constituent', 'A word or group of words that works as a unit in a particular expression.'],
    ['Phrase', 'A sequence of words that can function as a unit.'],
    ['Hierarchy', 'The arrangement of smaller units within larger ones.'],
    ['Phrase marker', 'A tree diagram that represents how an expression is grouped.'],
    ['Dominance', 'A node dominates the elements it reaches by following branches downward. Immediate dominance takes just one branch.'],
    ['Structural ambiguity', 'Two or more interpretations that arise from different groupings of the same words.'],
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
      paragraph('A constituent is a word or group of words that works as one unit in an expression. A phrase is a sequence of words that can work as a unit. A phrase can contain another phrase, and this arrangement of smaller groups inside larger ones is called hierarchy.');
      addIntroExample(body, el, 'The brackets mark where Mina paused and the landmark inside that location.',
        'Mina paused [near [the stone arch]].',
        'The inner group names the landmark. Adding “near” makes a larger group that specifies the location.');
      heading('What you’ll see in this chapter');
      const list = el('ul');
      for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
      body.append(list);
    }
    if (page === 1) {
      paragraph('The brackets in the introduction propose two groups. To see whether those boundaries fit the sentence, try changing one group at a time.');
      example(sentence);
      heading('Omit the location or replace it');
      paragraph('“Mina paused” is still a complete sentence. The location is optional here, and leaving it out as a whole supports the proposed boundary. “Mina paused there” gives another clue. One word, “there”, takes the place of “near the stone arch”.');
      heading('Find the smaller group');
      paragraph('Keep “near” and replace the landmark instead. In “Mina paused near it”, “it” stands for “the stone arch”. Ask what Mina paused near and the answer is “the stone arch”. Ask where Mina paused and the answer is “near the stone arch”. The answers have different boundaries.');
      heading('Check the same words in a longer sentence');
      example('Mina paused near the stone arch that spans the canal.');
      paragraph('Suppose the last words identify which arch Mina paused near. Then the answer to what Mina paused near is “the stone arch that spans the canal”. The shorter location phrase from the first sentence ends too early for this reading.');
      disclosure('Try the question test', 'Where did Mina pause? “Near the stone arch that spans the canal.” The longer landmark sits inside the longer location phrase.');
    }
    if (page === 2) {
      paragraph('A phrase marker is a tree diagram that shows how an expression is grouped. A node is a point in the tree where branches can meet and a label can appear. PHRASE-a names the outer group in this drawing. PHRASE-b names the group inside it.');
      example(sentence);
      paragraph('A node dominates the elements its branches reach below it. It immediately dominates the elements it reaches in one branch. Use both drawings to see whether the three landmark words have a node of their own.');
      const nested = locationTree(true);
      comparison(body, ui, 'Compare the phrase markers', [
        { label: 'Trace the flat drawing', step: 1, tree: locationTree(false), focusId: 'PHRASE-a',
          caption: 'All four words join PHRASE-a directly. The drawing gives the landmark words no node of their own.' },
        { label: 'Trace the landmark', step: 2, tree: nested, focusId: 'PHRASE-b',
          caption: 'PHRASE-b reaches all and only “the stone arch”. The replacement and question tests support that grouping.' },
        { label: 'Trace the outer phrase', step: 3, tree: nested, focusId: 'PHRASE-a',
          caption: 'PHRASE-a immediately dominates “near” and PHRASE-b. It reaches the landmark words indirectly through PHRASE-b.' },
      ]);
      paragraph('A triangle can stand for a whole group when its internal branches are left unexpanded. Here the landmark’s branches are open so each word can be traced.');
      heading('Repair a flat tree');
      paragraph('In “beside the red gate”, give the gate words a node of their own. Keep “beside” directly under the outer node. Use Guide me for help with the branches.');
      addConstituentTreeBuilder(body, ui);
    }
    if (page === 3) {
      paragraph('Structural ambiguity occurs when different groupings of the same words lead to different readings. Look at the phrase “with binoculars” and decide who might have them.');
      example('Nina spotted the climber with binoculars.');
      paragraph('The drawings show only the part of the sentence where the grouping changes. Follow “with binoculars” up one branch from PHRASE-c in each drawing.');
      comparison(body, ui, 'Compare the two readings', [
        { label: 'Nina used binoculars', tree: ambiguityTree(false), focusId: 'PHRASE-a',
          caption: 'The binoculars phrase joins the group that includes “spotted”. It describes how Nina spotted the climber.' },
        { label: 'The climber had binoculars', tree: ambiguityTree(true), focusId: 'PHRASE-b',
          caption: 'The binoculars phrase joins the climber group. It helps identify which climber Nina spotted.' },
      ]);
      heading('Try another sentence');
      example('Ivo sketched the guide with a pencil.');
      paragraph('Describe both readings. For each one, say which group “with a pencil” belongs to.');
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
      paragraph('Start with a proposed group in a specific sentence. Omit it if the rest can stand on its own, replace it with a suitable word, or check which question the group answers. Moving a whole group can provide another clue. A sequence that sounds like a unit still needs checking in context.');
      paragraph('Draw a boundary around the words that belong together. In a tree, trace a node down to all and only those words. One branch shows an immediate part. A route through another node shows a part inside a smaller group.');
      paragraph('When the same words allow two readings, explain what changes in the grouping. Ask what the disputed phrase tells the reader in each interpretation, then trace where its branch joins.');
    }
  },
};
