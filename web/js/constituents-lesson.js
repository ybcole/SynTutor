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

export function addConstituentTeaching(body, page, { el, button, renderTree, showComparisonTree }) {
  const paragraph = text => body.append(el('p', text));
  const section = (title, ...paragraphs) => body.append(el('h3', title), ...paragraphs.map(text => el('p', text)));
  function figureControls(label, choices, target, select, initial = 0) {
    const controls = el('div', undefined, 'constituent-controls');
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
    paragraph('Syntax studies how words combine to form phrases and sentences. A constituent is a word or group of words that functions as a unit within a larger structure. Hierarchy describes how these units fit inside one another.');
    section('What this chapter covers',
      'Consider “We met near the quiet garden”. The words “the quiet garden” name a place, and “near the quiet garden” tells us where we met. The smaller group sits inside the larger one, and each group has a job in the sentence.');
    const list = el('ul');
    for (const objective of [
      'Use replacement and simple questions to test whether words act as a unit.',
      'Read brackets and branches to see which words a tree groups together.',
      'Explain how two groupings can give the same sentence different meanings.',
    ]) list.append(el('li', objective));
    body.append(list);
  }
  if (page === 1) {
    paragraph('To find a constituent, start with the sentence and ask what a group of words does there. Then use the brackets or tree to show the grouping your evidence supports.');
    section('Test a group with replacement',
      'In “We visited the quiet garden”, try replacing “the quiet garden” with “it”. The result, “We visited it”, still has the same basic pattern. One word has taken over the job of naming what we visited. That gives us evidence that the three words act as one unit.',
      'Now try replacing only “the quiet”. The result, “We visited it garden”, breaks that pattern. If a replacement fails, try a suitable substitute or check the group another way before deciding.');
    section('Check what answers a question',
      'Ask “What did we visit?” The natural answer “the quiet garden” gives the whole group. An answer such as “the quiet” leaves the name of the place unfinished. Both tests point to the same three words in this example.');
    section('Read the brackets and the branches',
      'In [near [the quiet garden]], the inner brackets enclose the garden group. The outer brackets enclose that group together with “near”. The tree draws those two groups as separate nodes. A node is a point in the tree from which you can trace branches down to the words it contains.',
      'Use the two choices below to highlight the inner and outer groups. Follow the branches from the highlighted node. Notice that the outer group reaches one more word, “near”.');
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
      tree.replaceChildren(renderTree(nested, { focusId: index ? 'PHRASE-a' : 'PHRASE-b' }));
    });
  }
  if (page === 2) {
    paragraph('A tree shows how an analysis groups words. Two trees can put the words in the same order while making different claims about which words belong together. Compare both drawings of “near the quiet garden” and trace the branches that lead to “the quiet garden”.');
    section('Compare the two drawings',
      'Switch between the flat and nested drawings below. In each drawing, start at the lowest node that contains all three garden words. Does that node also contain “near”?');
    const [flat] = drawings(['near', 'the', 'quiet', 'garden']);
    const tree = el('div');
    const caption = el('p', undefined, 'constituent-caption');
    caption.setAttribute('aria-live', 'polite');
    const example = el('div', undefined, 'constituent-diagram');
    example.append(tree);
    body.append(example);
    figureControls('Compare drawings', ['Flat drawing', 'Nested drawing'], tree, index => {
      showComparisonTree(tree, index ? null : flat);
      caption.textContent = index
        ? 'In the nested drawing, PHRASE-b covers just “the quiet garden”. PHRASE-a contains that whole group together with “near”.'
        : 'In the flat drawing, all four words connect directly to PHRASE-a. The only node covering the three garden words also covers “near”.';
      tree.querySelector('.lesson-tree-canvas').after(caption);
    }, 1);
    section('Try giving a group its own branch',
      'The drawing below puts all four words of “beside the red gate” under one node. Which words name what you are beside? Select that whole group, then check your answer to see where the new branch goes.');
    const [before, after] = drawings(['beside', 'the', 'red', 'gate']);
    const repairTree = el('div', undefined, 'constituent-diagram');
    repairTree.append(renderTree(before));
    const choices = el('fieldset', undefined, 'constituent-choices');
    choices.append(el('legend', 'Which words belong under the new node?'));
    const inputs = ['beside', 'the', 'red', 'gate'].map(text => {
      const label = el('label');
      const check = el('input');
      check.type = 'checkbox';
      label.append(check, text);
      choices.append(label);
      return check;
    });
    const feedback = el('p');
    feedback.setAttribute('role', 'status');
    const check = button('Check grouping', () => {
      const correct = inputs.every((input, index) => input.checked === (index > 0));
      feedback.textContent = correct
        ? 'Exactly. The new node covers “the red gate”. The outer node still covers the whole phrase.'
        : 'Try to include the whole gate group and leave “beside” outside it.';
      repairTree.replaceChildren(renderTree(correct ? after : before, { focusId: correct ? 'PHRASE-b' : null }));
    });
    body.append(repairTree, choices, check, feedback);
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
    diagram.append(caption, tree);
    body.append(diagram);
    figureControls('Compare meanings', ['I used the telescope', 'The hikers had the telescope'], caption, index => {
      caption.textContent = index
        ? '“With a telescope” joins “the hikers”. It tells us which hikers I watched.'
        : '“With a telescope” joins the larger group that includes “watched”. It tells us how I watched.';
      tree.replaceChildren(renderTree(alternatives[index], { focusId: index ? 'PHRASE-b' : 'PHRASE-a' }));
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
