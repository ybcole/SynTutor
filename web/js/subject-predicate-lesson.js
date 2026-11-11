import { addWorkedExample } from './foundations-lesson.js';
import { addSubjectPredicateBuilder } from './subject-predicate-builder.js';

export const subjectPredicateHeadings = [
  'Introduction to Subject and Predicate',
  'Finding the Subject and Predicate',
  'Reading and Building the NP/VP Tree',
  'Applying the Split',
  'Chapter Recap',
  'Check what you learned',
];

export function subjectPredicateOpeningCheck(lesson) {
  const { prompt, options } = lesson.predict;
  return [{ prompt, options }, {
    prompt: 'In “The robins sing”, which words belong together as the group that names the birds?',
    options: [
      { id: 'a', text: 'The robins' },
      { id: 'b', text: 'robins sing' },
      { id: 'c', text: 'The' },
    ],
  }, {
    prompt: 'In “The lanterns glow at night”, which words tell you what the lanterns do and when?',
    options: [
      { id: 'a', text: 'The lanterns' },
      { id: 'b', text: 'glow' },
      { id: 'c', text: 'glow at night' },
    ],
  }];
}

export function addSubjectPredicateTeaching(body, page, ui) {
  const { el, lesson } = ui;
  const { sentence, tree } = lesson.worked_example;
  const [np, vp] = tree.root.children.map(branch => branch.words.join(' '));
  const paragraph = text => body.append(el('p', text));
  const section = (title, ...paragraphs) => body.append(el('h3', title), ...paragraphs.map(text => el('p', text)));
  const list = items => {
    const points = el('ul');
    for (const item of items) points.append(el('li', item));
    body.append(points);
  };

  if (page === 0) {
    paragraph('In Chapter 1, you looked for words that belong together. Here, you’ll start with the two largest groups in a simple sentence and ask what job each group does.');
    section('What this chapter covers',
      `Read “${sentence}”. Which words name the birds? Which words tell you what they do?`,
      `“${np}” names the birds. “${vp}” tells us what they do. These two groups are the subject and predicate of this sentence.`);
    list([
      'Find the subject and predicate in a simple sentence.',
      'Tell the difference between a group’s category and its job in the sentence.',
      'Read and build a tree that shows the two groups.',
    ]);
  }
  if (page === 1) {
    paragraph(`Read the sentence in two groups: [${np}] [${vp}]. Each pair of brackets holds one of the largest parts of the sentence.`);
    section('What job does each group do?',
      `“${np}” is the subject in this sentence. “${vp}” is the predicate. Here, the predicate tells us what the robins do.`);
    section('What kind of group is it?',
      `“${np}” is a noun phrase (NP). “${vp}” is a verb phrase (VP), even though it contains one word.`,
      'NP and VP tell us the kind of phrase. Subject and predicate tell us the jobs those phrases do in this tree. To find the jobs in this pattern, look at the two branches directly under S, the sentence node.');
  }
  if (page === 2) {
    paragraph('Select the whole sentence, subject, or predicate. Follow each branch to see which words belong to it.');
    addWorkedExample(body, ui, ['Whole sentence', 'Subject', 'Predicate'], { highlightWords: true });
    section('Build your first labelled tree',
      'Start with the words. Add S, NP and VP and connect their branches. Use Guide me for help, or build directly on the canvas.',
      'A triangle keeps the phrase’s words visible and leaves its internal branches out of the drawing. Right-click or press and hold to open a node menu. After connecting the words, use the menu to collapse each phrase.');
    addSubjectPredicateBuilder(body, ui);
    if (ui.openBuilderPractice) {
      body.append(ui.button('Try in Syntax Builder', () => ui.openBuilderPractice(lesson, [
        'Add S, NP and VP using New category.',
        'Connect NP and VP to S, with NP on the left.',
        'Connect The and robins to NP, and sing to VP. Then collapse each phrase to a triangle to match this chapter’s model.',
      ]), 'lesson-builder-link'));
    }
  }
  if (page === 3) {
    section('Try another sentence',
      'Read “The lanterns glow at night”. Say which words go together as the subject and which words form the whole predicate. Then explain how you could spot the subject in the tree.');
    const answer = el('details');
    answer.append(el('summary', 'Check your explanation'),
      el('p', 'The NP “The lanterns” is the subject because it is directly under S. The VP “glow at night” is the predicate. The words “at night” belong to the predicate and tell us when the lanterns glow.'));
    body.append(answer);
    section('Cambridge insight: sentence and clause',
      'Cambridge uses sentence for a unit of text and clause for a unit of syntax. A clause can sit inside another clause. A typical clause has a subject and a predicate.',
      'The tree in this lesson uses Burton-Roberts’ labels. See Cambridge, pp. 44–45, in the chapter references.');
  }
  if (page === 4) {
    paragraph('You’ve identified the two largest groups in a simple sentence and used their positions to tell what each group does.');
    section('Key ideas');
    list([
      'In the basic pattern, S has two direct branches, NP and VP.',
      'NP and VP are categories. The NP directly under S functions as the subject. Its VP sister functions as the predicate.',
      'A triangle shows the words in a phrase and leaves its internal branches out of view.',
    ]);
    section('Put it into practice',
      'Start at S. Follow each direct branch down to all the words it covers. Then use the label and position of each branch to explain its job.');
  }
}
