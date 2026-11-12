// Supplemental, unscored practice for the reviewed launch outcomes.
function span(sentence, target, question, success, hint) {
  const words = sentence.split(' ');
  const group = target.split(' ');
  const start = words.findIndex((_, i) => group.every((word, j) => words[i + j] === word));
  if (start < 0) throw new Error(`The practice span “${target}” is missing from “${sentence}”.`);
  return { sentence, expected: [start, start + group.length - 1], question, success, hint };
}

function gap(sentence, position, question, success, hint) {
  return { sentence, expected: [position], question, success, hint, gap: true };
}

const ap = 'The room looked quite bright.';
const object = 'The children carried a heavy box.';
const adjunct = 'The children carried a heavy box before lunch.';
const progressive = 'The workers were painting the gate.';
const noun = 'Maya packed these baskets.';
const report = 'Maya noticed that those lanterns were flickering.';
const question = 'What were the workers painting?';
const infinitive = 'Maya hopes to visit the museum.';
const destination = 'Maya walks to the museum.';
const passage = `${report} She closed the door.`;

export const chapterPolishing = {
  'br-03': {
    practice: [
      span(ap, 'bright.', 'Which word is the adjective head?',
        '“Bright” supplies the description. It is the head (A).', 'Find the word that supplies the description when “quite” is left out.'),
      span(ap, 'quite bright.', 'Which words form the whole adjective phrase?',
        'AP covers “quite bright”. It includes DEG “quite” and A “bright”.', 'Include both the description and the word that tells its degree.'),
    ],
    comparison({ lesson }) {
      const tree = lesson.worked_example.tree;
      const root = { ...tree.root, children: [tree.root.children[1]] };
      return {
        original: 'With the degree word', alternate: 'Adjective on its own', focusId: root.id,
        tree: { sentence: 'cheerful', root },
        caption: 'AP and A now cover the same word. Only the DEG branch has disappeared.',
      };
    },
  },
  'br-04': {
    examples: [
      ['Subject NP under S', '', 'Nora', ' inspected the bridge.'],
      ['Object NP inside VP', 'Nora inspected ', 'the bridge', '.'],
    ],
    practice: [
      span(object, 'a heavy box.', 'Which words make up the complete direct object?',
        '“A heavy box” is the full object NP. All three words can be replaced by “it”.',
        'Ask what the children carried. Try replacing the whole answer with “it” after “carried”.'),
    ],
  },
  'br-05': {
    practice: [
      span(adjunct, 'carried a heavy box', 'Which words form the inner VP?',
        '“Carried a heavy box” is the inner VP. “Before lunch” joins that VP under the outer VP.',
        'Leave out the time phrase. Select the verb and the whole object that remain in the predicate.'),
    ],
    comparison({ lesson }) {
      const tree = lesson.worked_example.tree;
      const [subject, outerVP] = tree.root.children;
      const [innerVP] = outerVP.children;
      return {
        original: 'With the time phrase', alternate: 'Without the time phrase', focusId: innerVP.id,
        tree: { sentence: 'Nora inspected the bridge', root: { ...tree.root, children: [subject, innerVP] } },
        caption: 'The verb and object still form one VP. With the time PP gone, this VP is the whole predicate.',
      };
    },
  },
  'br-06': {
    practice: [
      span(progressive, 'painting the gate.', 'Which words form the lower VP?',
        '“Painting the gate” is the lexical VP. It is the complement of progressive “were”.',
        'Try replacing the activity with “doing so” while leaving “were” in place.'),
      span(progressive, 'were', 'Which word carries past tense?',
        '“Were” carries past tense. Changing it to “are” leaves the lower VP intact.',
        'Which word changes if you describe the same activity in the present tense?'),
    ],
    comparison({ getWorkedExample }) {
      const { tree } = getWorkedExample('br-05');
      return {
        original: 'Progressive auxiliary', alternate: 'Time adjunct', tree,
        focusId: tree.root.children[1].id,
        caption: '“In June” adds a time to the event described by the inner VP. In the progressive tree, “is” instead heads the higher VP and takes the lower VP as its complement.',
      };
    },
  },
  'br-07': {
    tracePath: true,
    practice: [
      span(noun, 'these', 'Which word is covered by the DET branch of the object NP?',
        '“These” sits under DEM, which reaches NP through DET.', 'Look for the demonstrative that could be replaced by “the”.'),
      span(noun, 'baskets.', 'Which word is covered by the NOM branch here?',
        'NOM covers “baskets”. The word is under N, and N reaches NP through NOM.',
        'Find the head noun. In this simple phrase, it is the only word in NOM.'),
    ],
  },
  'br-08': {
    examples: [
      ['The whole report', 'Leo says [', 'that Nora is inspecting the bridge', '].'],
      ['The inner S inside that report', 'Leo says [that [', 'Nora is inspecting the bridge', ']].'],
      ['Demonstrative inside an NP', 'Nora is inspecting [', 'that bridge', '].'],
    ],
    practice: [
      span(report, 'that', 'Select the first word in S′.',
        'S′ begins at “that”. It includes C and the clause that follows.', 'Look for the word that introduces the content of what Maya noticed.'),
      span(report, 'those', 'Select the first word in the inner S.',
        'S begins at “those”. “Those lanterns” is its complete subject NP.', 'Start with the first word of the embedded subject. The complementiser is on a separate branch.'),
    ],
  },
  'br-09': {
    examples: [
      ['Statement', 'Nora is inspecting ', 'the bridge', '.'],
      ['Yes/no question', '', 'Is', ' Nora inspecting the bridge?'],
      ['Object wh-question', '', 'What is', ' Nora inspecting?'],
    ],
    extraSteps(root) {
      const higherVP = root.children[1].children[1].children[1];
      return [{
        id: higherVP.children[0].children[0].id,
        label: 'Find the PROG gap',
        caption: 'The dot under PROG marks where “is” appears in the statement. In the question, the word is in C1.',
      }, {
        id: higherVP.children[1].children[1].children[0].id,
        label: 'Trace the NP gap',
        caption: 'The dot under NP marks the direct-object position beside V. “What” is in C2.',
      }];
    },
    practice: [
      span(question, 'What', 'Select the word that occupies C2.',
        '“What” occupies C2 and asks for the missing object.', 'Find the word that asks which thing the workers were painting.'),
      span(question, 'were', 'Select the word that occupies C1.',
        '“Were” is the auxiliary in C1.', 'Find the auxiliary that stands before the subject.'),
      gap('the workers painting', 2, 'Inside S, where is the PROG gap left by “were”?',
        'The PROG gap is between “workers” and “painting”, where “were” goes in the statement.',
        'Say “The workers were painting the gate”. Find the two words that surrounded “were”.'),
      gap('the workers painting', 3, 'Inside S, where is the NP object gap?',
        'The NP gap follows “painting”. The answer “the gate” would fill that position in the statement.',
        'Find the position where “the gate” would appear in the corresponding statement.'),
    ],
  },
  'br-10': {
    examples: [
      ['Present tense in the larger sentence', 'Nora plans [', 'to inspect the bridge', '].'],
      ['Past tense in the larger sentence', 'Nora planned [', 'to inspect the bridge', '].'],
    ],
    practice: [
      span(infinitive, 'visit the museum.', 'Select the complete group after infinitival “to”.',
        '“Visit the museum” is the lexical VP. The auxiliary “to” carries [-tense].',
        'Start with the verb “visit” and include what Maya hopes to visit.'),
      span(destination, 'the museum.', 'Select the complete group after prepositional “to”.',
        '“The museum” is an NP that names a destination. Here “to” is a preposition.',
        'Select the whole noun phrase naming where Maya walks.'),
    ],
  },
  'br-11': {
    examples: [
      ['First application', '', '[Iris rests] and [Leo waits]', '.'],
      ['Second application', '', '[[Iris rests] and [Leo waits]] and [Leo waits]', '.'],
    ],
    combination: { basic: ['Maya smiles', 'Leo waves'], incomplete: 'Maya smiles and' },
  },
  'cgel-clauses': {
    examples: [
      ['A sentence on its own', '', 'The robins sing', '.'],
      ['The same subject and predicate inside a report', 'Nora reports that ', 'the robins sing', '.'],
    ],
    practice: [
      span(passage, report, 'Mark the whole written sentence that contains Maya’s observation.',
        'The first sentence runs from “Maya” to “flickering”. “She closed the door” is a second text sentence.',
        'Start at “Maya” and stop at the full stop that ends her observation.'),
      span(passage, 'those lanterns', 'Inside that sentence, which words form the embedded subject?',
        '“Those lanterns” is the embedded subject. “Maya” is the subject of the larger clause.',
        'Ask what was flickering. Select the entire noun phrase naming it.'),
      span(passage, 'were flickering.', 'Which words form the embedded predicate?',
        '“Were flickering” says what the lanterns were doing. It is the embedded predicate.',
        'Find all the words that say what the lanterns were doing.'),
    ],
  },
};

export function addVisibleContrast(body, { el }, examples) {
  const list = el('ul', undefined, 'lesson-transfer-context');
  for (const [label, before, focus, after] of examples) {
    const item = el('li', undefined, 'lesson-transfer-example');
    item.append(el('strong', label), el('br'), before, el('mark', focus), after);
    list.append(item);
  }
  body.append(list);
}
