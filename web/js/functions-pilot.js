import { addIntroExample, lessonExample, setTreeStepLabel } from './lesson-presentation.js';
import { addEmbeddedTreeExercise } from './lesson-tree-exercise.js';
import { addPhrase, addWordsFromText, childrenOf, connect, createModel, roots } from './syntax-builder.js';

const subject = 'The lantern by the stairs';
const predicate = 'is glowing';
const lantern = `${subject} ${predicate}`;
const repairSentence = 'Mira checked the lantern';
const profile = { chapter: 2, version: 'V2', profile_id: 'V2' };
const triangle = (id, label, text) => ({ id, label, triangle: true, words: text.split(' ') });
const topSplit = {
  sentence: lantern,
  root: { id: 'sentence', label: 'S', children: [
    triangle('subject', 'NP', subject), triangle('predicate', 'VP', predicate),
  ] },
};
const twoNps = {
  sentence: repairSentence,
  root: { id: 'sentence', label: 'S', children: [
    triangle('subject', 'NP', 'Mira'),
    { id: 'predicate', label: 'VP', children: [
      { id: 'verb', word: 'checked' }, triangle('object', 'NP', 'the lantern'),
    ] },
  ] },
};

function trace(body, { el, button, showDiagram }) {
  const figure = el('div', undefined, 'constituent-diagram');
  const controls = el('div', undefined, 'lesson-tree-steps');
  controls.setAttribute('role', 'group');
  controls.setAttribute('aria-label', 'Trace the sentence groups');
  const canvas = el('div');
  const note = el('div', undefined, 'lesson-tree-observation');
  note.setAttribute('aria-live', 'polite');
  const caption = el('p');
  note.append(caption);
  const steps = [
    ['Find the two sisters', topSplit, 'sentence', 'S branches directly to the subject NP and predicate VP. The triangles leave their internal branches hidden.'],
    ['Trace the subject NP', twoNps, 'subject', 'In “Mira checked the lantern”, “Mira” is the NP directly under S. It is the subject.'],
    ['Trace the NP inside VP', twoNps, 'object', '“The lantern” is also an NP. Its parent is VP, so it belongs inside the predicate.'],
  ];
  const buttons = steps.map(([label], index) => {
    const control = button(label, () => select(index));
    setTreeStepLabel(control, el, label, index + 1);
    return control;
  });
  function select(index) {
    const [, tree, focusId, explanation] = steps[index];
    buttons.forEach((control, i) => control.setAttribute('aria-pressed', String(i === index)));
    showDiagram(canvas, tree, { focusId, highlightWords: true, wordBaseline: 3 });
    caption.textContent = explanation;
  }
  controls.append(...buttons);
  figure.append(controls, canvas, note);
  body.append(figure);
  select(0);
}

function repair(body, ui) {
  function seed() {
    const model = createModel();
    const top = addPhrase(model, 'S', 112, 22);
    const subjectNode = addPhrase(model, 'NP', 24, 95);
    const vp = addPhrase(model, 'VP', 92, 95);
    const object = addPhrase(model, 'NP', 171, 155);
    const [mira, checked, the, lamp] = addWordsFromText(model, repairSentence, 0, 225, 24);
    for (const [parent, child] of [[top, subjectNode], [top, vp], [subjectNode, mira], [vp, checked], [object, the], [object, lamp]]) {
      connect(model, parent.id, child.id);
    }
    subjectNode.canonicalTriangle = object.canonicalTriangle = true;
    return model;
  }

  function objectBranch(model) {
    return Object.values(model.nodes).find(node => node.type === 'NP' &&
      childrenOf(model, node.id).map(child => child.text).join(' ') === 'the lantern');
  }

  addEmbeddedTreeExercise(body, ui, {
    id: 'attach-predicate-np', label: 'Attach the NP inside the predicate', profile, labels: ['S', 'NP', 'VP'], seed,
    guide: [{
      title: 'Attach the lantern group to VP',
      text: 'Connect VP to the detached NP. The NP and “checked” should share a parent.',
      apply(model) {
        const vp = Object.values(model.nodes).find(node => node.type === 'VP');
        const object = objectBranch(model);
        if (!vp || !object || !connect(model, vp.id, object.id)) {
          return 'Use one VP and an NP that covers exactly “the lantern”.';
        }
        return 'The lantern group now joins “checked” under VP.';
      },
    }],
    check(model) {
      const [top, extra] = roots(model);
      const object = objectBranch(model);
      if (!object?.parent) return 'The lantern group is still detached. Connect it to VP.';
      if (model.nodes[object.parent]?.type !== 'VP') return 'Connect the lantern group to VP. An NP directly under S would occupy the subject level.';
      const branches = top && childrenOf(model, top.id);
      const [first, second] = branches || [];
      const vpParts = second && childrenOf(model, second.id);
      if (extra || top?.type !== 'S' || branches?.length !== 2 || first?.type !== 'NP' ||
          childrenOf(model, first.id).map(child => child.text).join(' ') !== 'Mira' ||
          second?.type !== 'VP' || vpParts?.length !== 2 || vpParts[0].text !== 'checked' || vpParts[1].id !== object.id) {
        return 'Keep S over the subject NP and VP. Under VP, keep “checked” before “the lantern”.';
      }
      return 'The NP “the lantern” and “checked” share VP as their parent. “Mira” remains the subject NP directly under S.';
    },
  });
}

export const functionsPilot = {
  references: [
    'Chapter 2, printed pp. 24–28 · Subject–predicate division and the yes/no question test',
    'Printed pp. 29–32, figures [33–35] · Category, function, and sister nodes',
    'Printed pp. 32–38, figures [36], [43], [46], [48] · Heads, modifiers, and complements',
  ],
  sections: [
    { id: 'introduction', title: 'Two groups, two functions' },
    { id: 'concepts', title: 'Find the complete subject' },
    { id: 'worked-example', title: 'Read and repair the top split' },
    { id: 'application', title: 'Read relations between sisters' },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Subject', 'The group that a predicate is paired with. In a simple English statement, it typically comes before the predicate.'],
    ['Predicate', 'The part of a clause that says what the subject does, what happens to it, or what state it is in.'],
    ['Category', 'The grammatical kind of a word or phrase, such as noun phrase or verb phrase.'],
    ['Function', 'The grammatical role a group has in its structure, such as subject or predicate.'],
    ['Sister nodes', 'Nodes that share the same immediate parent.'],
    ['Head', 'The central element that determines a phrase’s category.'],
    ['Modifier', 'An element that adds information about another element.'],
    ['Complement', 'An element that fills a role required or licensed by a head in a particular construction.'],
  ],
  teach(body, page, ui) {
    const { el, button, lesson } = ui;
    const p = text => body.append(el('p', text));
    const heading = text => body.append(el('h3', text));
    const example = text => body.append(lessonExample(el, text));

    if (page === 0) {
      p('Chapter 1 showed how smaller groups fit inside larger ones. To analyse a whole statement, start at the top. The subject is the part paired with the predicate. The predicate tells what the subject does, what happens to it, or what state it is in. In “The lantern glows”, “the lantern” is the subject and “glows” is the predicate.');
      addIntroExample(body, el, 'Adding words to each group keeps the same two-part pattern.',
        '[The lantern by the stairs] [is glowing].',
        'The first group identifies the lantern. The second says what it is doing. Subject and predicate are functions, the jobs these groups do. The category of each group tells what kind of phrase it is.');
      heading('What you’ll see in this chapter');
      const list = el('ul');
      for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
      body.append(list);
    }
    if (page === 1) {
      p('Where does the subject end when it contains more than a noun? Compare the statement with its yes/no question.');
      example(`${lantern}.`);
      example('Is the lantern by the stairs glowing?');
      p('In the question, “is” comes before the complete subject. “Glowing” follows the subject in the question. In the statement, “is glowing” is the complete predicate. Select the last word of the subject in the statement.');
      const words = el('div', undefined, 'lesson-tree-steps');
      const feedback = el('div', undefined, 'lesson-tree-observation');
      feedback.setAttribute('role', 'status');
      const message = el('p');
      feedback.append(message);
      words.setAttribute('role', 'group');
      words.setAttribute('aria-label', 'Choose the last word of the subject');
      for (const [i, token] of lantern.split(' ').entries()) {
        const choice = button(token, () => {
          for (const [j, control] of Array.from(words.children).entries()) control.setAttribute('aria-pressed', String(i === j));
          message.textContent = i === 4 ? '“Stairs” completes the subject. The predicate is “is glowing”.' :
            i < 4 ? 'Continue through the words that identify the lantern. Those words stay together after “is” in the question.' :
              '“Is glowing” belongs to the predicate in the statement. End the subject just before it.';
        });
        choice.setAttribute('aria-pressed', 'false');
        words.append(choice);
      }
      body.append(words, feedback);
    }
    if (page === 2) {
      p('A noun phrase (NP) is centred on a noun, such as “lantern”. A verb phrase (VP) is centred on a verb. In the first tree, the NP and VP share S, the sentence node, as their immediate parent. Nodes with the same immediate parent are sisters.');
      p('Now compare a statement with two NPs. Follow each NP up one branch to see which function its position supports.');
      trace(body, ui);
      heading('Repair one branch');
      example(`${repairSentence}.`);
      p('Attach the detached NP “the lantern” to VP so it shares a parent with “checked”. Use Guide me for help with the branch.');
      repair(body, ui);
    }
    if (page === 3) {
      p('The subject NP and predicate VP work together in the statements above. Inside a phrase, a head is the central element that gives the phrase its category. Compare what happens when two different parts are left out.');
      example('Tessa repaired a loose hinge.');
      p('Within the group “a loose hinge”, “hinge” is the head. “Loose” is a modifier because it adds a description, and “Tessa repaired a hinge” still describes a repair. The whole group “a loose hinge” is a complement of “repaired” because it fills the role of the thing repaired in this sentence.');
      example('Ava slipped beside the counter.');
      p('Inside the location phrase, “beside” and “the counter” are sisters. The location can be omitted as a whole. The landmark “the counter” is still a complement of “beside” in this reading. It supplies what the location is beside.');
      heading('Try a new sentence');
      example('Leo tightened a loose bolt.');
      p('Write the subject and predicate. Then identify what “loose” modifies and which group completes “tightened”.');
      const hint = el('details', undefined, 'lesson-sources');
      hint.append(el('summary', 'Hint'), el('p', 'Compare “Leo tightened a bolt” with the original. Which word can disappear while the thing being tightened is still named?'));
      body.append(hint);
      const key = `syntutor:lesson-transfer:${ui.userId}:br-02@${lesson.content_version}:application`;
      const label = el('label', 'Your explanation');
      label.htmlFor = 'chapter-two-transfer';
      const input = el('textarea');
      input.id = label.htmlFor;
      input.rows = 3;
      input.maxLength = 1200;
      try { input.value = localStorage.getItem(key) || ''; } catch { /* The exercise still works. */ }
      const feedback = el('div', undefined, 'lesson-tree-observation');
      feedback.setAttribute('role', 'status');
      const answer = el('p');
      feedback.append(answer);
      const reveal = button('Compare your explanation', () => {
        answer.textContent = '“Leo” is the subject. “Tightened a loose bolt” is the predicate. “Loose” modifies “bolt”, and “a loose bolt” is the full complement of “tightened”.';
      });
      reveal.disabled = !input.value.trim();
      input.addEventListener('input', () => {
        reveal.disabled = !input.value.trim();
        try { localStorage.setItem(key, input.value); } catch { /* Keep the current response in the field. */ }
      });
      const practice = el('div', undefined, 'lesson-pilot-transfer');
      practice.append(label, input, reveal, feedback);
      body.append(practice);
    }
    if (page === 4) {
      p('Start with the largest groups. Use the yes/no question to check the full subject boundary, then read the predicate in the original statement.');
      p('Identify each group’s category and follow its branch to its parent. The NP directly under S is the subject in the trees here. An NP under VP has a different job.');
      p('Within a phrase, compare sisters. A modifier adds information that can often be omitted. A complement fills a role licensed by the head in that construction. Check the same reading each time you change the example.');
    }
  },
};
