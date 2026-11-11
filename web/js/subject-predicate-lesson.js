import { addWorkedExample } from './foundations-lesson.js';

export const subjectPredicateHeadings = [
  'Introduction to Subject and Predicate',
  'Categories and Functions',
  'Reading the NP and VP Branches',
  'Sentence and Clause',
  'Chapter Recap',
  'Chapter Post-test',
];

export function addSubjectPredicateTeaching(body, page, ui) {
  const { el, lesson } = ui;
  const paragraph = text => body.append(el('p', text));
  if (page === 0) {
    paragraph('This chapter looks at how a simple sentence divides into a subject and a predicate. In “The robins sing”, “the robins” is the subject and “sing” tells us what they do.');
    paragraph(lesson.outcomes[0].text);
  }
  if (page === 1) {
    for (const block of lesson.teaching) paragraph(block.text);
  }
  if (page === 2) {
    paragraph('Follow the tree from the sentence to its two immediate branches.');
    addWorkedExample(body, ui, ['Whole sentence', 'Subject', 'Predicate']);
    body.append(el('h3', 'Build your first labelled tree'));
    paragraph('Start with the words, then add S, NP and VP and connect their branches.');
    if (ui.openBuilderPractice) {
      body.append(ui.button('Try in Syntax Builder', () => ui.openBuilderPractice(lesson, [
        'Add S, NP and VP using New category.',
        'Connect NP and VP to S, with NP on the left.',
        'Connect The and robins to NP, and sing to VP. Then collapse each phrase to a triangle to match this chapter’s model.',
      ]), 'lesson-primary'));
    }
    paragraph('After building, explain why NP is the category of “The robins” and subject is its function in this tree.');
    const reflection = el('details');
    reflection.append(el('summary', 'Check your explanation'),
      el('p', 'NP names the kind of phrase. Its position as the NP directly under S gives it the subject function in this pattern.'));
    body.append(reflection);
  }
  if (page === 3) {
    body.append(el('h3', 'Cambridge insight'));
    for (const insight of lesson.cambridge_insights) paragraph(insight.text);
  }
  if (page === 4) {
    paragraph('Use the top split in the tree to tell the subject and predicate apart.');
    const list = el('ul', undefined, 'constituent-recap');
    for (const text of [
      'S has two immediate branches in the basic pattern: NP and VP.',
      'The NP functions as the subject. The VP functions as the predicate.',
      'NP and VP are category labels. Subject and predicate are functions in this structure.',
      'A triangle leaves the internal structure of a group unanalyzed.',
    ]) list.append(el('li', text));
    body.append(list);
  }
}
