// Original teaching examples based on Burton-Roberts, 3rd ed., Chapter 1.
export const constituentReferences = [
  'Noel Burton-Roberts, Analysing Sentences, 3rd ed. · Chapter 1, printed pp. 9, 12–13 · Flat structures and replacement',
  'Noel Burton-Roberts, Analysing Sentences, 3rd ed. · Chapter 1, printed pp. 17–18, 22–23 · Grouping, alternative trees, and ambiguity',
];

export const constituentHeadings = {
  predict: 'Which words belong together?',
  understand: 'Words form groups',
  worked: 'Trace a group through the tree',
  guided: 'Give a group its own branch',
  transfer: 'One sentence, two meanings',
  exit: 'Try a fresh example',
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
  const left = group('S', i, group('PHRASE-a', watched, group('PHRASE-b', the, hikers), instrument));
  const right = group('S', i, group('PHRASE-a', watched, group('PHRASE-b', the, hikers, instrument)));
  return [{ sentence, root: left }, { sentence, root: right }];
}

export function addConstituentTeaching(body, stage, { el, renderTree, worked, step }) {
  const paragraph = text => body.append(el('p', text));
  const section = (title, text) => body.append(el('h3', title), el('p', text));
  function comparison(examples) {
    const row = el('div', undefined, 'constituent-comparison');
    for (const [title, description, tree] of examples) {
      const figure = el('section');
      figure.append(el('h3', title), el('p', description), renderTree(tree));
      row.append(figure);
    }
    return row;
  }

  if (stage === 'predict') {
    paragraph('Read “near the quiet garden”. Say it once, then notice which words you would keep together if you were describing a place. Compare “the quiet garden” with “near the”.');
  }
  if (stage === 'understand') {
    paragraph('A constituent is a unit within a larger structure. In “near the quiet garden”, the words “the quiet garden” form a smaller group inside the larger phrase.');
    section('Read the brackets', 'In [near [the quiet garden]], the inner brackets show the garden group. The outer brackets include that whole group and “near”. Each pair of brackets shows the span of one group.');
    section('Read the branches', 'A node is a point in the tree. Follow its branches downward to see what it dominates, or contains in the drawing. To check a proposed group, look for one node that covers exactly those words.');
    body.append(renderTree(drawings(['near', 'the', 'quiet', 'garden'])[1]));
    section('Test a group in a sentence', 'Compare “We visited the quiet garden” with “We visited it”. Here “it” takes the place of the whole group in the same position. That is evidence that those words act as a unit in this sentence. A replacement has to fit the context and preserve the overall structure.');
    paragraph('Now try replacing just “the quiet”. The result, “We visited it garden”, breaks the original grouping. A single unsuccessful test is a reason to look for more evidence.');
  }
  if (stage === 'worked') {
    paragraph(worked.steps[step].text);
    paragraph('[near [the quiet garden]]');
    if (step === worked.steps.length - 1) {
      const [flat, nested] = drawings(['near', 'the', 'quiet', 'garden']);
      body.append(comparison([
        ['Flat drawing', 'Every word joins the same node. There is no node for just “the quiet garden”.', flat],
        ['Nested drawing', 'The inner node gives “the quiet garden” a branch of its own.', nested],
      ]));
    }
  }
  if (stage === 'guided') {
    paragraph('Start with this flat drawing of “beside the red gate”. Which words would you move under a new node while keeping “beside” outside it?');
    const [flat, nested] = drawings(['beside', 'the', 'red', 'gate']);
    body.append(renderTree(flat));
    const repair = el('details');
    repair.append(el('summary', 'Show the repaired tree'), el('p', 'The new branch groups “the red gate”. The outer node still covers the entire phrase.'), renderTree(nested));
    const choices = el('fieldset', undefined, 'constituent-choices');
    choices.append(el('legend', 'Select the words that need their own node'));
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
    const check = el('button', 'Check grouping');
    check.type = 'button';
    check.addEventListener('click', () => {
      const correct = inputs.every((input, index) => input.checked === (index > 0));
      feedback.textContent = correct ? 'Exactly. The three words share one node.' : 'Try to include the whole gate group and leave “beside” outside it.';
      if (correct) repair.open = true;
    });
    body.append(choices, check, feedback, repair, el('h3', 'Find the matching node in another example'));
  }
  if (stage === 'transfer') {
    paragraph('“I watched the hikers with a telescope” can describe two situations. Compare where the telescope phrase joins the tree in each reading.');
    const [watching, hikers] = readings();
    body.append(comparison([
      ['I used the telescope', 'The telescope phrase groups with the watching.', watching],
      ['The hikers had the telescope', 'The telescope phrase groups with “the hikers”.', hikers],
    ]));
    paragraph('The words stay in the same order. The change in grouping changes the meaning. This is structural ambiguity.');
  }
  if (stage === 'exit') {
    paragraph('Trace the whole group to one node. If the only node also covers extra words, the drawing represents a larger group. Apply that idea to the brackets below.');
  }
}
