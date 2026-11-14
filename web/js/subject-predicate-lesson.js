import { addIntroExample, lessonExample, setTreeStepLabel } from './lesson-presentation.js';
import { addSubjectPredicateBuilder } from './subject-predicate-builder.js';

export const subjectPredicateHeadings = [
  'Introduction to Subject and Predicate',
  'Finding the Subject and Predicate',
  'Reading and Building the NP/VP Tree',
  'Applying the Split',
  'Chapter Recap',
  'Check what you learned',
];

export const subjectPredicateReferences = [
  'Noel Burton-Roberts, Analysing Sentences, 3rd ed., Chapter 2, printed pp. 24–28 (subject, predicate, and the yes/no question comparison).',
  'Noel Burton-Roberts, Analysing Sentences, 3rd ed., Chapter 2, printed pp. 29–31 (category, function, triangles, and an NP inside a VP).',
];

const longSubject = 'The robins near the gate';
const longPredicate = 'are singing softly';
const longSentence = `${longSubject} ${longPredicate}`;
const contrastSentence = 'Maya watched the robins';
const transferSubject = 'The gate by our house';
const transferPredicate = 'is open';
const transferSentence = `${transferSubject} ${transferPredicate}`;

export function subjectPredicateOpeningCheck(lesson) {
  return [lesson.predict, {
    prompt: 'In “The robins sing”, which words form the whole group that names the birds?',
    answer: 'a',
    options: [
      { id: 'a', text: 'The robins' },
      { id: 'b', text: 'robins sing' },
      { id: 'c', text: 'robins' },
    ],
  }, {
    prompt: 'In “The lanterns glow at night”, which words tell you what the lanterns do and when?',
    answer: 'c',
    options: [
      { id: 'a', text: 'The lanterns' },
      { id: 'b', text: 'glow' },
      { id: 'c', text: 'glow at night' },
    ],
  }];
}

function disclosure(el, label, ...content) {
  const details = el('details');
  details.append(el('summary', label), ...content);
  return details;
}

function addPractice(body, ui, { key, prompt, choices, correct, feedback }) {
  const { el, practiceQuestion } = ui;
  const response = el('p', undefined, 'lesson-feedback');
  response.setAttribute('role', 'status');
  body.append(practiceQuestion(key, prompt, choices, id => {
    const index = Number(id);
    const isCorrect = index === correct;
    response.className = `lesson-feedback ${isCorrect ? 'correct' : 'retry'}`;
    response.textContent = feedback[index];
  }), response);
}

// Supplemental trees use the same top-level pattern as the reviewed V2 example.
function triangle(id, label, text) {
  return { id, label, triangle: true, words: text.split(' ') };
}

function sentenceTree(id, sentence, subject, predicate) {
  return {
    sentence,
    root: {
      id, label: 'S',
      children: [
        triangle(`${id}-subject`, 'NP', subject),
        triangle(`${id}-predicate`, 'VP', predicate),
      ],
    },
  };
}

function addTreeComparison(body, ui) {
  const { el, button, lesson, showDiagram, showWorkedTree } = ui;
  const short = lesson.worked_example;
  const long = sentenceTree('br-02-long', longSentence, longSubject, longPredicate);
  const examples = [short.tree, long];
  const switches = el('div', undefined, 'constituent-controls');
  switches.setAttribute('role', 'group');
  switches.setAttribute('aria-label', 'Choose a worked sentence');
  const sentence = el('p', undefined, 'lesson-example-sentence');
  const prompt = el('div');
  prompt.append(
    el('h3', 'Find the full predicate'),
    el('p', 'The subject ends at “gate”. Find the node that covers the remaining words, “are singing softly”. Select its label in the tree or use the buttons below.'),
  );
  const feedback = el('p', undefined, 'lesson-feedback');
  feedback.setAttribute('role', 'status');
  const branches = el('div', undefined, 'constituent-controls lesson-tree-steps');
  branches.setAttribute('role', 'group');
  branches.setAttribute('aria-label', 'Choose a tree branch');
  const diagram = el('div', undefined, 'constituent-diagram');
  const observation = el('div', undefined, 'lesson-tree-observation');
  const caption = el('p', undefined, 'constituent-caption');
  caption.setAttribute('role', 'status');
  observation.append(caption, feedback);
  const picker = ['Short sentence', 'Try the longer sentence'].map((label, index) =>
    button(label, () => chooseExample(index)));
  const branchLabels = [['Whole sentence', 'Subject', 'Predicate'], ['S', 'NP', 'VP']];
  const branchButtons = branchLabels[0].map((label, index) =>
    button(label, () => selectBranch(index, true)));
  const explanations = [
    'S covers the whole sentence. Its two direct branches divide the words into two groups.',
    'Category: NP · Function: subject. This NP is directly under S.',
    'Category: VP · Function: predicate. This VP is the other branch directly under S.',
  ];
  let current = 0;

  function describe(index, answer) {
    branchButtons.forEach((control, i) => control.setAttribute('aria-pressed', String(i === index)));
    caption.textContent = explanations[index] ?? '';
    if (current === 0 || !answer) return;
    feedback.className = `lesson-feedback ${index === 2 ? 'correct' : 'retry'}`;
    feedback.textContent = [
      'S also covers the subject. Look for a branch that covers just the three predicate words.',
      'The NP covers “The robins near the gate”. Follow the other branch from S.',
      'The VP covers all three words and functions as the predicate.',
    ][index];
  }
  function selectBranch(index, answer = false) {
    const tree = examples[current];
    const nodes = [tree.root, ...tree.root.children];
    const onSelect = id => {
      const selected = nodes.findIndex(node => node.id === id);
      if (selected === -1) return;
      if (current === 1) {
        for (const item of diagram.querySelectorAll('svg [data-node-id]')) {
          item.classList.remove('lesson-tree-focus');
          item.toggleAttribute('data-constituent-selected', item.dataset.nodeId === id);
        }
      }
      describe(selected, true);
    };
    const focusId = nodes[index]?.id;
    if (current === 0) {
      showWorkedTree(diagram, focusId, { highlightWords: true, onSelect, observation });
    } else {
      observation.querySelector('.constituent-selection')?.remove();
      showDiagram(diagram, tree, { focusId, highlightWords: true, onSelectNode: onSelect }).after(observation);
    }
    describe(index, answer);
  }
  function chooseExample(index) {
    current = index;
    picker.forEach((control, i) => control.setAttribute('aria-pressed', String(i === index)));
    branchButtons.forEach((control, i) => {
      setTreeStepLabel(control, el, branchLabels[index][i], index === 0 ? i + 1 : undefined);
    });
    sentence.textContent = examples[index].sentence;
    prompt.hidden = index === 0;
    feedback.textContent = '';
    selectBranch(index === 0 ? 0 : null);
  }

  switches.append(...picker);
  branches.append(...branchButtons);
  body.append(switches, sentence, prompt, branches, diagram);
  chooseExample(0);
}

function addSubjectBoundary(body, { el, button }) {
  const prompt = 'Select the last word of the subject.';
  const words = longSentence.split(' ');
  const subjectEnd = longSubject.split(' ').length - 1;
  const choices = el('div', undefined, 'constituent-controls');
  choices.setAttribute('role', 'group');
  choices.setAttribute('aria-label', prompt);
  const response = el('p', undefined, 'lesson-feedback');
  response.setAttribute('role', 'status');
  const controls = words.map((word, index) => {
    const control = button(word, () => selectBoundary(index));
    control.setAttribute('aria-label', `End the subject after word ${index + 1}, ${word}`);
    control.setAttribute('aria-pressed', 'false');
    return control;
  });
  function selectBoundary(index) {
    controls.forEach((control, position) => control.setAttribute('aria-pressed', String(position === index)));
    const correct = index === subjectEnd;
    response.className = `lesson-feedback ${correct ? 'correct' : 'retry'}`;
    if (correct) {
      response.replaceChildren(el('strong', 'Subject '), longSubject, el('br'),
        el('strong', 'Predicate '), longPredicate);
    } else {
      response.textContent = index < subjectEnd
        ? 'Keep the words that tell you which robins together. Where does that group end?'
        : '“Are singing softly” says what the robins are doing. Move the boundary to the word before “are”.';
    }
  }
  choices.append(...controls);
  body.append(el('p', prompt), choices, response);
}

function addClosingWarmup(body, { el }) {
  body.append(el('h3', 'Unscored warm-up'),
    el('p', 'The children by the window were reading quietly.', 'lesson-example-sentence'),
    el('p', 'Find the full subject and predicate. Which branches go directly under S?'),
    disclosure(el, 'Reveal the analysis',
      lessonExample(el, '[The children by the window] [were reading quietly]'),
      el('p', '“By the window” identifies the children, so it belongs in the subject NP. The predicate VP covers “were reading quietly”.')));
}

export function addSubjectPredicateTeaching(body, page, ui) {
  const { el, lesson } = ui;
  const { sentence, tree } = lesson.worked_example;
  const [np, vp] = tree.root.children.map(branch => branch.words.join(' '));
  const paragraph = text => body.append(el('p', text));
  const section = (title, ...paragraphs) => body.append(el('h3', title), ...paragraphs.map(text => el('p', text)));
  const list = (items, tag = 'ul') => {
    const points = el(tag);
    for (const item of items) points.append(el('li', item));
    body.append(points);
  };

  if (page === 0) {
    section('What this chapter covers',
      'In Chapter 1, you learned how words form groups. Here you’ll see how two groups work together in a simple statement. In these simple statements, the subject is the group that the sentence says something about. The predicate tells what the subject does or what state it is in.');
    addIntroExample(body, el,
      'Read this statement about the robins. The brackets show its subject and predicate as two separate groups.',
      `[${np}] [${vp}].`,
      `“${np}” is a noun phrase that serves as the subject. “${vp}” is a verb phrase that serves as the predicate. Noun phrase and verb phrase name the kinds of groups. Subject and predicate name their jobs in this sentence.`);
    section('What you’ll see in this chapter');
    const preview = el('ol');
    for (const [topic, example] of [
      ['Find the complete subject and predicate.', 'Use a yes/no question and a replacement test to check the split.'],
      ['Read and build a tree.', 'Show the two groups with branches in the lesson canvas.'],
      ['Compare the jobs a phrase can do.', 'See how the same noun phrase works in two different sentences.'],
    ]) {
      const item = el('li');
      item.append(el('strong', topic), ` ${example}`);
      preview.append(item);
    }
    body.append(preview);
  }

  if (page === 1) {
    section('Ways to find the subject and predicate',
      'Start by finding the two main groups. Then check the subject with a yes/no question or by replacing the whole group. In the simple statements here, the rest of the sentence forms the predicate.');
    section('Try a first split',
      'In “The robins sing every morning”, “The robins” is still the subject. The predicate is “sing every morning”. In the sentence below, the subject also grows. Look for all the words that tell you which robins.');
    body.append(el('p', longSentence, 'lesson-example-sentence'));
    addSubjectBoundary(body, ui);
    section('Check the split');
    const checks = el('ul');
    for (const [method, explanation] of [
      ['Ask a yes/no question.', 'Move “are” to the front: “Are [the robins near the gate] singing softly?” The words in brackets stay together as the subject. For “The robins sing”, add “do”: “Do the robins sing?”'],
      ['Replace the whole group.', 'Try “They are singing softly.” The word “they” replaces all of “The robins near the gate”, giving you another clue that those five words form a group.'],
      ['Read the original statement.', 'Once you have the subject, read the remaining words together. The whole predicate is “are singing softly”, including “are”. Use this split when you draw the tree.'],
    ]) {
      const item = el('li');
      item.append(el('strong', method), ` ${explanation}`);
      checks.append(item);
    }
    body.append(checks);
    section('What kind of group is it?',
      'A category tells you what kind of phrase it is. A function tells you its job in the sentence.');
    list([
      'A noun phrase (NP) is built around a noun in these examples. Both subject groups are built around “robins”.',
      'A verb phrase (VP) is built around a verb. It can consist of one word, as in “sing”, or several, as in “are singing softly”.',
    ]);
    paragraph('A predicate can describe a state. In “The gate is open”, the subject is “The gate” and the whole predicate is “is open”.');
  }

  if (page === 2) {
    section('Read the tree from the top',
      'On the previous page, you split “The robins sing” into two groups. A tree shows that same split with two lines. It puts a label above each group so you can see what kind of phrase it is.',
      'The top label, S, covers the whole sentence. Its left branch leads to NP, the noun phrase “The robins”. Its right branch leads to VP, the verb phrase “sing”. These nodes are sisters because they share the same parent.');
    section('What the triangles show',
      'A triangle points to the words in a phrase. It leaves any smaller branches inside that phrase for another drawing. In the short tree, the NP triangle covers two words and the VP triangle covers just “sing”.',
      'Before you look at the longer tree, recall the question from the previous page. It showed that “The robins near the gate” stays together. Use the NP triangle to check whether the tree includes all five words in that group.');
    section('Compare the two trees',
      'Select Subject or Predicate to see which words each branch covers in the short tree. Then choose Try the longer sentence to check whether you can find the full predicate on your own.');
    addTreeComparison(body, ui);
    section('Build your first labelled tree',
      'Start with the words of “The robins sing”. Add S, NP and VP and connect their branches. Use Guide me for help, or build directly on the canvas.',
      'Right-click or press and hold to open a node menu. Connect the words to their phrases first, then use the menu to collapse NP and VP to triangles. Use Check my tree to see which part needs attention.');
    addSubjectPredicateBuilder(body, ui);
  }

  if (page === 3) {
    section('Can the same phrase do a different job?',
      'A label such as NP tells you the kind of group you are looking at. To work out what job it does, look at where it connects in the tree.');
    list([sentence, contrastSentence]);
    paragraph('Find “the robins” in each sentence. Is it still a noun phrase? Does it still do the subject’s job?');
    addPractice(body, ui, {
      key: 'np-function',
      prompt: 'What changes in “Maya watched the robins”?',
      choices: [
        '“The robins” is an NP and still functions as the subject.',
        '“The robins” is an NP inside the predicate. “Maya” is the subject.',
        '“The robins” becomes a VP because it is inside the predicate.',
      ],
      correct: 1,
      feedback: [
        'Look for the whole subject of the new sentence. The statement says what Maya did.',
        'The category stays NP. Its place and job change: it is now inside the predicate VP.',
        'The larger group “watched the robins” is a VP. The smaller group “the robins” is still an NP.',
      ],
    });
    const contrast = sentenceTree('br-02-contrast', contrastSentence, 'Maya', 'watched the robins');
    section('Follow the two NPs',
      'In “The robins sing”, “The robins” is the NP directly under S. In the tree below, “Maya” takes that position and is an NP on its own. The VP covers “watched the robins”.',
      'Follow the highlighted NP up to its parent. It sits inside the VP, just as smaller groups sat inside larger ones in Chapter 1.');
    const closeUp = el('div', undefined, 'constituent-diagram');
    body.append(closeUp);
    const [subject, predicate] = contrast.root.children;
    ui.showDiagram(closeUp, {
      ...contrast,
      root: { ...contrast.root, children: [subject, {
        id: predicate.id, label: 'VP',
        children: [{ word: 'watched' }, triangle('br-02-contrast-inner', 'NP', 'the robins')],
      }] },
    }, { focusId: 'br-02-contrast-inner', highlightWords: true, wordBaseline: 3 });
    section('Build a tree for a new sentence',
      'Find the words that identify the gate and the words that describe its state. Then build the split.');
    body.append(el('p', transferSentence, 'lesson-example-sentence'));
    paragraph('Use S, NP, and VP. Build on your own or use Guide me. Each exercise saves its own draft.');
    addSubjectPredicateBuilder(body, ui, {
      id: `${lesson.lesson_id}-transfer`,
      label: 'Build a tree for a new sentence exercise',
      target: {
        ...sentenceTree('br-02-transfer', transferSentence, transferSubject, transferPredicate),
        convention_profile: tree.convention_profile,
      },
    });
  }

  if (page === 4) {
    section('How to find the two groups');
    list([
      'Read the statement. Try dividing it into its two main groups.',
      'If the subject boundary is unclear, try a yes/no question. In “Are the robins near the gate singing softly?”, the subject stays together just after “Are”.',
      'Start at S in the tree for the statement. Follow the NP and VP directly under it down to all their words. The NP works as the subject and the VP works as the predicate in this pattern.',
    ], 'ol');
    section('Remember category and function',
      'NP and VP are categories. Subject and predicate are functions. An NP inside the VP still has the category NP. A triangle shows its words while leaving its internal branches out of view.');
    section('Put it into practice',
      'Read “The lights in the hall were bright”. Try finding the two groups before opening the answer. Check that every word belongs to one of them.');
    body.append(disclosure(el, 'Check your split',
      lessonExample(el, '[The lights in the hall] [were bright]'),
      el('p', 'Ask “Were the lights in the hall bright?” The entire subject stays together after “Were”. In the statement, the subject NP covers “The lights in the hall”, and the predicate VP covers “were bright”. Both phrases connect directly to S in this pattern.')));
  }

  if (page === 5 && ui.showClosingWarmup) addClosingWarmup(body, ui);
}
