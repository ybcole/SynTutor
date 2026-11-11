import { addConstituentTreeBuilder } from './constituent-tree-builder.js';

// Original examples following Analysing Sentences, 3rd ed., Chapter 1.
export const constituentReferences = [
  'Noel Burton-Roberts, Analysing Sentences, 3rd ed. · Chapter 1, printed pp. 6–10 · Word order and hierarchical structure',
  'Noel Burton-Roberts, Analysing Sentences, 3rd ed. · Chapter 1, printed pp. 10–15 · Evidence for constituents',
  'Noel Burton-Roberts, Analysing Sentences, 3rd ed. · Chapter 1, printed pp. 15–18 · Constituents in context and structural ambiguity',
];

export const constituentHeadings = [
  'Introduction to Constituents and Hierarchy',
  'Identifying Constituents in a Sentence',
  'Comparing Flat and Nested Trees',
  'Structural Ambiguity',
  'Chapter Recap',
  'Chapter Post-test',
];

// The saved prediction is a completion marker. Any choice satisfies the pre-test.
export const constituentPreTest = {
  prompt: 'In “Mara rested beside the river”, which words could you replace with “there”?',
  options: [
    { id: 'a', text: 'the river' },
    { id: 'b', text: 'beside the river' },
    { id: 'c', text: 'rested beside' },
  ],
};

const word = (text, position) => ({ id: `word-${position}`, word: text });
const group = (name, ...children) => ({ id: name, label: name, children });

function drawings(words) {
  const [outside, ...inside] = words.map(word);
  return [
    { sentence: words.join(' '), root: group('PHRASE-a', outside, ...inside) },
    { sentence: words.join(' '), root: group('PHRASE-a', outside, group('PHRASE-b', ...inside)) },
  ];
}

function readings() {
  const sentence = 'I watched the hikers with a telescope';
  const [i, watched, the, hikers, withWord, a, telescope] = sentence.split(' ').map(word);
  const instrument = group('PHRASE-c', withWord, group('PHRASE-d', a, telescope));
  return [
    { sentence, root: group('S', i, group('PHRASE-a', watched, group('PHRASE-b', the, hikers), instrument)) },
    { sentence, root: group('S', i, group('PHRASE-a', watched, group('PHRASE-b', the, hikers, instrument))) },
  ];
}

export function addConstituentTeaching(body, page, { el, button, showDiagram, showComparisonTree, mountBuilder }) {
  const paragraph = text => body.append(el('p', text));
  const section = (title, ...paragraphs) => body.append(el('h3', title), ...paragraphs.map(text => el('p', text)));
  function figureControls(label, choices, target, select, initial = 0) {
    const controls = el('div', undefined, 'constituent-controls lesson-tree-steps');
    controls.setAttribute('role', 'group');
    controls.setAttribute('aria-label', label);
    const buttons = choices.map((choice, index) => button(choice, () => show(index)));
    function show(index) {
      buttons.forEach((item, position) => item.setAttribute('aria-pressed', String(position === index)));
      select(index);
    }
    controls.append(...buttons);
    target.before(controls);
    show(initial);
  }

  if (page === 0) {
    paragraph('Think about a bicycle. The spokes are part of a wheel, and the wheel is part of the bicycle. Words fit together in groups in a similar way.');
    paragraph('Syntax is the study of how words fit together in a sentence. In this chapter, you’ll look for small groups of words and see how they fit inside larger groups.');
    section('What this chapter covers',
      'Read “We met near the quiet garden”. Which words tell you where we met?',
      '“Near the quiet garden” tells us where we met. Inside that group, “the quiet garden” tells us what we were near.',
      'A word or group of words that works as one part of a sentence is called a constituent. The way smaller groups fit inside larger ones is called hierarchy.');
    const list = el('ul');
    for (const objective of [
      'Test whether words form a group by replacing them with one word or asking a question.',
      'Read brackets and tree branches to see which words go together.',
      'Compare two trees and draw a branch for a group of words.',
      'See how grouping the same words in two ways can change the meaning of a sentence.',
    ]) list.append(el('li', objective));
    body.append(list);
  }
  if (page === 1) {
    paragraph('Read “We met near the quiet garden”. Does “the quiet garden” work as a single unit in that sentence? Start by trying to replace it.');
    section('Test a group with replacement',
      'Say “We met near it”. Here, one word takes the place of “the quiet garden”, and the rest of the sentence stays in place. That is evidence that the three words form a constituent.',
      'Try the same thing with just “the quiet”. You get “We met near it garden”. The word “garden” is left behind, so this replacement gives us no evidence that “the quiet” forms a unit here.');
    section('Check what answers a question',
      'Ask “What did we meet near?” The answer is “the quiet garden”. Now ask “Where did we meet?” The answer is “near the quiet garden”. The two answers show how the smaller group fits inside the larger one.');
    section('Read the brackets and the branches',
      'Write the two groups as [near [the quiet garden]]. The inner brackets mark the garden group. The outer brackets mark the whole location phrase, including “near”. The tree shows each group with a node, a point from which you can follow branches down to the words.',
      'Select each group below and trace its branches. The inner node reaches exactly “the quiet garden”. The outer node reaches those words and “near”.');
    const diagram = el('div', undefined, 'constituent-diagram');
    const sentence = el('p', undefined, 'constituent-selection');
    sentence.setAttribute('aria-live', 'polite');
    const tree = el('div');
    diagram.append(sentence, tree);
    body.append(diagram);
    const nested = drawings(['near', 'the', 'quiet', 'garden'])[1];
    figureControls('Highlight a group', ['the quiet garden', 'near the quiet garden'], tree, index => {
      sentence.replaceChildren(...(index ? [el('mark', 'near the quiet garden')] : ['near ', el('mark', 'the quiet garden')]));
      sentence.append(index ? ' · The outer node includes every word.' : ' · The inner node covers just the garden group.');
      showDiagram(tree, nested, { focusId: index ? 'PHRASE-a' : 'PHRASE-b' });
    });
  }
  if (page === 2) {
    paragraph('You found evidence that “the quiet garden” is a group inside “near the quiet garden”. Now compare two ways of drawing those same four words. Where does each drawing put the boundary of the garden group?');
    section('Compare the two drawings',
      'Start with the flat drawing. Trace “the”, “quiet”, and “garden” upward to the first node they share. Does that node also reach “near”? Switch to the nested drawing and try again.');
    const [flat] = drawings(['near', 'the', 'quiet', 'garden']);
    const tree = el('div');
    const caption = el('p', undefined, 'constituent-caption');
    caption.setAttribute('aria-live', 'polite');
    const example = el('div', undefined, 'constituent-diagram');
    example.append(tree);
    body.append(example);
    figureControls('Compare drawings', ['Flat drawing', 'Nested drawing'], tree, index => {
      caption.textContent = index
        ? 'PHRASE-b reaches exactly “the quiet garden”. One level up, PHRASE-a contains that group and “near”. The nested tree shows both constituents.'
        : 'The three garden words first meet at PHRASE-a, which also reaches “near”. The flat tree shows the whole phrase as a group and gives the garden words no node of their own.';
      showComparisonTree(tree, index ? null : flat).after(caption);
    }, 1);
    section('Build your first tree',
      'Try the same idea with “beside the red gate”. Give the gate words a node of their own, then check which words it covers. Use Guide me if you want help with a step.');
    addConstituentTreeBuilder(body, { el, button, mountBuilder });
  }
  if (page === 3) {
    paragraph('Structural ambiguity occurs when the same sentence can be grouped in two ways and each grouping gives it a different meaning. In “I watched the hikers with a telescope”, the phrase “with a telescope” could tell us how I watched or describe the hikers.');
    section('Trace the telescope phrase',
      'Switch between the two readings below. In each tree, follow “with a telescope” up to the highlighted group. Look at what else sits under that same node.');
    const alternatives = readings();
    const caption = el('p', undefined, 'constituent-caption');
    caption.setAttribute('aria-live', 'polite');
    const tree = el('div');
    const diagram = el('div', undefined, 'constituent-diagram');
    diagram.append(tree);
    body.append(diagram);
    figureControls('Compare meanings', ['I used the telescope', 'The hikers had the telescope'], tree, index => {
      caption.textContent = index
        ? '“With a telescope” joins “the hikers”. It tells us which hikers I watched.'
        : '“With a telescope” joins the larger group that includes “watched”. It tells us how I watched.';
      showDiagram(tree, alternatives[index], { focusId: index ? 'PHRASE-b' : 'PHRASE-a' }).after(caption);
    });
    paragraph('To explain the difference in your own words, ask “Who had the telescope?” In one reading it was the person watching. In the other it was the hikers. The branch shows which reading the tree represents.');
  }
  if (page === 4) {
    paragraph('You’ve used evidence from a sentence to identify its groups, then shown how those groups fit together. Use this summary to review the steps before the post-test.');
    section('Key ideas');
    const list = el('ul', undefined, 'constituent-recap');
    for (const [term, explanation] of [
      ['Constituents', 'Words can function together as a unit, and one group can sit inside another.'],
      ['Brackets and branches', 'A pair of brackets encloses a group. In a tree, look for one node that covers all and only the words in that group.'],
      ['Evidence', 'Try replacing the whole group with one suitable word, or see if the group can answer a question about the sentence.'],
      ['Structural ambiguity', 'The same word order can allow two groupings. Each grouping can lead to a different interpretation.'],
    ]) {
      const item = el('li');
      item.append(el('strong', term), ` · ${explanation}`);
      list.append(item);
    }
    body.append(list);
    section('Before the post-test',
      'Look for the complete group. If you’re reading a tree, follow its branches to the words. If you’re testing a sentence, try a replacement or ask what the group answers.');
  }
}

export function addConstituentReview(body, { el }) {
  const section = el('section', undefined, 'constituent-review');
  section.append(el('h3', 'Extra practice'), el('p', 'Try each question before revealing its explanation.'));
  for (const [prompt, answer] of [
    ['In “Mia left her blue notebook on the desk”, what evidence supports grouping “her blue notebook”?',
      'Replace the group with “it” to get “Mia left it on the desk”. It also answers “What did Mia leave on the desk?” Both tests support treating the whole group as a unit.'],
    ['In “Lee photographed the artist with a camera”, how can “with a camera” change the meaning?',
      'If it joins the photographing, Lee used a camera. If it joins “the artist”, the artist had a camera. The second reading tells us which artist Lee photographed.'],
  ]) {
    const example = el('details');
    example.append(el('summary', prompt), el('p', answer));
    section.append(example);
  }
  body.append(section);
}
