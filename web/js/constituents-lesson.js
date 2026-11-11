// Original examples following Analysing Sentences, 3rd ed., Chapter 1.
export const constituentReferences = [
  'Noel Burton-Roberts, Analysing Sentences, 3rd ed. · Chapter 1, printed pp. 6–10 · Word order and hierarchical structure',
  'Noel Burton-Roberts, Analysing Sentences, 3rd ed. · Chapter 1, printed pp. 10–15 · Evidence for constituents',
  'Noel Burton-Roberts, Analysing Sentences, 3rd ed. · Chapter 1, printed pp. 15–18 · Constituents in context and structural ambiguity',
];

export const constituentHeadings = [
  'Why words group together',
  'How to find a constituent',
  'What changes when we group words differently?',
  'One sentence, two meanings',
  'Chapter recap',
  'Chapter post-test',
];

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

export function addConstituentTeaching(body, page, { el, button, renderTree, workedCanvas }) {
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
    paragraph('When you read “near the quiet garden”, you probably picture the garden as one thing and “near” as locating something in relation to it. You made sense of the words by grouping them. In this chapter, you’ll make that grouping visible.');
    paragraph('By the end, you’ll be able to find a group inside a sentence, show it with brackets and branches, and explain how a different grouping can change the meaning.');
    section('Before you begin', 'Answer this quick pre-test to check what you already know. Choose the answer that makes the most sense to you. Any answer lets you continue.');
  }
  if (page === 1) {
    section('Start with a group that does a job',
      'Read “We visited the quiet garden”. The last three words name the place we visited. A group of words that functions as a unit within a larger structure is a constituent. A smaller constituent can sit inside a larger one. For instance, “the quiet garden” can also be part of “near the quiet garden”.');
    section('Look for evidence in the sentence',
      'Try “We visited it”. The single word “it” takes the place of “the quiet garden”, and the sentence keeps the same basic structure. Replacing only “the quiet” would leave “We visited it garden”, which breaks the structure. Successful replacement is evidence for the whole group. If one replacement fails, try another suitable replacement or check the group another way.',
      'You can also ask “What did we visit?” The whole group “the quiet garden” answers that question naturally. Ask the question in the original sentence so you can see what role the words play there.');
    section('Show the grouping',
      'In [near [the quiet garden]], the inner brackets enclose the garden group, and the outer brackets enclose the whole phrase. In a tree, the point where branches meet is a node. Follow its branches down to see which words it dominates, or contains in the drawing. A node representing the garden group must cover exactly those three words.');
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
    paragraph('Compare two drawings of “near the quiet garden”. The words appear in the same order in both. Look for a node that reaches all three garden words without also reaching “near”.');
    const flat = renderTree(drawings(['near', 'the', 'quiet', 'garden'])[0]);
    const nested = workedCanvas();
    const caption = el('p', undefined, 'constituent-caption');
    caption.setAttribute('aria-live', 'polite');
    const example = el('div', undefined, 'constituent-diagram');
    example.append(caption, flat, nested);
    body.append(example);
    figureControls('Compare drawings', ['Flat drawing', 'Nested drawing'], caption, index => {
      flat.hidden = Boolean(index);
      nested.hidden = !index;
      caption.textContent = index
        ? 'The inner node gives “the quiet garden” a branch of its own. The outer node still contains the whole phrase.'
        : 'All the words branch directly from the same node. There is no node for “the quiet garden” alone.';
    }, 1);
    section('Try giving a group its own branch',
      'Imagine a flat drawing of “beside the red gate”. Select the words that need their own node while keeping the rest under the outer node.');
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
    paragraph('“I watched the hikers with a telescope” can describe two situations. Read the sentence both ways, then follow the branch above “with a telescope” to see what it joins.');
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
    paragraph('The words stay in the same order, but their grouping changes what the sentence means. This is structural ambiguity.');
  }
  if (page === 4) {
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
    paragraph('The post-test checks how you read a tree and identify groups in new examples.');
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
