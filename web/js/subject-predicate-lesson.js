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

export function subjectPredicateOpeningCheck(lesson) {
  const { prompt, options } = lesson.predict;
  return [{ prompt, options }, {
    prompt: 'In “The robins sing”, which words form the whole group that names the birds?',
    options: [
      { id: 'a', text: 'The robins' },
      { id: 'b', text: 'robins sing' },
      { id: 'c', text: 'robins' },
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

function disclosure(el, label, ...content) {
  const details = el('details');
  details.append(el('summary', label), ...content);
  return details;
}

function addPractice(body, ui, { key, prompt, choices, correct, feedback, onAnswer }) {
  const { el, practiceQuestion } = ui;
  const response = el('p', undefined, 'lesson-feedback');
  response.setAttribute('role', 'status');
  body.append(practiceQuestion(key, prompt, choices, id => {
    const index = Number(id);
    const isCorrect = index === correct;
    response.className = `lesson-feedback ${isCorrect ? 'correct' : 'retry'}`;
    response.textContent = feedback[index];
    onAnswer?.();
  }), response);
}

// These supplemental diagrams are authored teaching views. The catalog's
// reviewed tree still drives construction, explanation and scored questions.
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
  const prompt = el('p', 'Which branch covers exactly “are singing softly”? Select a branch to check.');
  prompt.tabIndex = -1;
  const feedback = el('p', undefined, 'lesson-feedback');
  feedback.setAttribute('role', 'status');
  const branches = el('div', undefined, 'constituent-controls lesson-tree-steps');
  branches.setAttribute('role', 'group');
  branches.setAttribute('aria-label', 'Choose a tree branch');
  const diagram = el('div', undefined, 'constituent-diagram');
  const caption = el('p', undefined, 'constituent-caption');
  caption.setAttribute('role', 'status');
  const picker = ['Short sentence', 'Longer sentence'].map((label, index) =>
    button(label, () => chooseExample(index)));
  const branchButtons = ['Whole sentence', 'Subject', 'Predicate'].map((label, index) =>
    button(label, () => selectBranch(index, true)));
  const explanations = [
    'S covers the whole sentence. Its two direct branches divide the words into two groups.',
    'Category: NP · Function: subject. This NP is directly under S.',
    'Category: VP · Function: predicate. This VP is the other branch directly under S.',
  ];
  let current = 0;

  function describe(index, answer) {
    branchButtons.forEach((control, i) => control.setAttribute('aria-pressed', String(i === index)));
    caption.textContent = explanations[index];
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
    const focusId = nodes[index].id;
    const canvas = current === 0
      ? showWorkedTree(diagram, focusId, { highlightWords: true, onSelect })
      : showDiagram(diagram, tree, { focusId, highlightWords: true, onSelectNode: onSelect });
    canvas.after(caption);
    describe(index, answer);
  }
  function chooseExample(index) {
    current = index;
    picker.forEach((control, i) => control.setAttribute('aria-pressed', String(i === index)));
    sentence.textContent = examples[index].sentence;
    prompt.hidden = index === 0;
    feedback.textContent = '';
    selectBranch(0);
  }

  switches.append(...picker);
  branches.append(...branchButtons);
  body.append(switches, sentence, prompt, branches, diagram, feedback);
  chooseExample(0);
  return () => {
    chooseExample(1);
    prompt.focus();
  };
}

function addClosingWarmup(body, ui) {
  const { el } = ui;
  const exercise = el('div');
  const reasoning = el('div', undefined, 'lesson-warmup-reason');
  reasoning.hidden = true;
  addPractice(exercise, ui, {
    key: 'warmup-split',
    prompt: 'Where does the subject end?',
    choices: [
      'The children / by the window were reading quietly',
      'The children by the window / were reading quietly',
      'The children by the window were / reading quietly',
    ],
    correct: 1,
    feedback: [
      'Keep “by the window” with “the children”. It tells you which children.',
      'That’s the whole split. “The children by the window” is the subject, and “were reading quietly” is the predicate.',
      '“Were” belongs with “reading quietly” in the statement.',
    ],
    onAnswer: () => { reasoning.hidden = false; },
  });
  addPractice(reasoning, ui, {
    key: 'warmup-reason',
    prompt: 'What would show that “The children by the window” is the subject in a tree?',
    choices: [
      'It is an NP anywhere in the tree.',
      'It comes first in the sentence.',
      'It is the NP directly under S, next to the VP.',
    ],
    correct: 2,
    feedback: [
      'An NP can also be inside the VP. Look at which node the NP attaches to.',
      'In this example it comes first, but the tree shows its job through its position under S.',
      'Exactly. In this pattern, that NP and the predicate VP are the two direct branches under S.',
    ],
  });
  exercise.append(reasoning);
  body.append(disclosure(el, 'Try an unscored warm-up',
    el('p', 'The children by the window were reading quietly.', 'lesson-example-sentence'), exercise));
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
    paragraph('In Chapter 1, you found words that belong together. Now look at the two main parts of a simple sentence and ask what each part does.');
    section('What this chapter covers');
    body.append(el('p', sentence, 'lesson-example-sentence'));
    paragraph('Read the sentence. Where would you divide it into two parts? Find the whole group that names the birds, then the part that tells you what they do.');
    body.append(disclosure(el, 'See the two parts',
      el('p', `[${np}] [${vp}]`, 'lesson-example-sentence'),
      el('p', `“${np}” names the birds and works as the subject. “${vp}” says what they do and works as the predicate.`)));
    list([
      'Find the complete subject and predicate, even when they contain several words.',
      'Use a tree to see the difference between the kind of phrase and its job.',
      'Build a tree showing the two main parts of a sentence.',
    ]);
  }

  if (page === 1) {
    section('Find the two main groups');
    const examples = el('ul');
    examples.append(el('li', `[${np}] [${vp}]`), el('li', longSentence));
    body.append(examples);
    paragraph('The longer sentence has the same two-part pattern. Find all the words that tell you which birds, then all the words that say what those birds are doing.');
    addPractice(body, ui, {
      key: 'long-split',
      prompt: 'Where would you put the boundary in the longer sentence?',
      choices: [
        'The robins / near the gate are singing softly',
        `${longSubject} / ${longPredicate}`,
        `${longSubject} are / singing softly`,
      ],
      correct: 1,
      feedback: [
        'Keep “near the gate” with “The robins”. It tells you which robins.',
        'Yes. The whole subject is “The robins near the gate”. All three words in “are singing softly” form the predicate.',
        '“Are” goes with “singing softly” in the statement.',
      ],
    });
    section('Try a yes/no question',
      'In this example, the question starts with “Are”. Which words stay together right after it?');
    body.append(disclosure(el, 'Reveal the question',
      el('p', 'Are [the robins near the gate] singing softly?', 'lesson-example-sentence'),
      el('p', 'The whole subject stays together after “Are”. In the original statement, “are” belongs to the predicate. We’ll draw the tree for the statement.')));
    body.append(disclosure(el, 'Try replacing the subject',
      el('p', 'They are singing softly.', 'lesson-example-sentence'),
      el('p', '“They” can stand for the whole group “The robins near the gate”. The predicate stays the same. This is another way to check which words go together.')));
    section('What kind of group is it?',
      'A category tells you what kind of phrase you’re looking at. A function tells you the job it does in this sentence.',
      '“The robins” and “The robins near the gate” are noun phrases (NPs). “Sing” and “are singing softly” are verb phrases (VPs). A phrase can contain a single word, as “sing” does here.',
      'In these statements, the NP functions as the subject and the VP functions as the predicate. A predicate can also describe a state. In “The gate is open”, the whole predicate is “is open”.');
  }

  if (page === 2) {
    paragraph('Switch between the two sentences. Select Subject or Predicate, or select a label in the tree, to highlight the complete group. S labels the whole sentence.');
    const practiceLongTree = addTreeComparison(body, ui);
    section('Build your first labelled tree',
      'Start with the words of “The robins sing”. Add S, NP and VP and connect their branches. Use Guide me for help, or build directly on the canvas.',
      'A triangle shows the words that belong to a phrase. It leaves the branches inside the phrase out of the drawing. Right-click or press and hold to open a node menu. After connecting the words, use the menu to collapse each phrase.');
    addSubjectPredicateBuilder(body, ui);
    if (ui.openBuilderPractice) {
      body.append(ui.button('Try in Syntax Builder', () => ui.openBuilderPractice(lesson, [
        'Add S, NP and VP using New category.',
        'Connect NP and VP to S, with NP on the left.',
        'Connect The and robins to NP, and sing to VP. Then collapse each phrase to a triangle to match this chapter’s model.',
      ]), 'lesson-builder-link'));
    }
    section('Find the branch that covers the whole predicate',
      'Try the longer tree and check which branch includes all three predicate words.');
    body.append(ui.button('Practice on the longer tree', practiceLongTree, 'lesson-builder-link'));
  }

  if (page === 3) {
    section('Can the same phrase do a different job?');
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
    const overview = el('div', undefined, 'constituent-diagram');
    body.append(overview);
    ui.showDiagram(overview, contrast);
    const closeUp = el('div', undefined, 'constituent-diagram');
    const detail = disclosure(el, 'Look inside the predicate',
      el('p', 'Here the VP is opened up so you can see “the robins” inside it. Follow that NP upward. It connects to VP. The subject NP “Maya” connects directly to S.'),
      closeUp);
    body.append(detail);
    detail.addEventListener('toggle', () => {
      if (!detail.open || closeUp.childElementCount) return;
      const [subject, predicate] = contrast.root.children;
      ui.showDiagram(closeUp, {
        ...contrast,
        root: { ...contrast.root, children: [subject, {
          id: predicate.id, label: 'VP',
          children: [{ word: 'watched' }, triangle('br-02-contrast-inner', 'NP', 'the robins')],
        }] },
      }, { focusId: 'br-02-contrast-inner', highlightWords: true, wordBaseline: 3 });
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
    section('Cambridge insight: sentence and clause',
      'Cambridge uses sentence for a unit of text and clause for a unit of syntax. A typical clause has a subject and a predicate, and a clause can sit inside another clause. See Cambridge, printed pp. 44–45, in the chapter references.');
  }

  if (page === 5 && ui.showClosingWarmup) addClosingWarmup(body, ui);
}
