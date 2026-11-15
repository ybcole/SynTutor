import { addExplanationPractice, addIntroExample, lessonExample, addTreeTrace } from './lesson-presentation.js';
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

function trace(body, ui) {
  const steps = [
    ['Find the two sisters', topSplit, 'sentence', 'From S, one branch leads to the subject NP and one leads to the predicate VP. The triangles stand for the words inside each phrase.'],
    ['Trace the subject NP', twoNps, 'subject', 'In “Mira checked the lantern”, “Mira” is the NP directly under S. It is the subject.'],
    ['Trace the NP inside VP', twoNps, 'object', '“The lantern” is also an NP. Its parent is VP, so it belongs inside the predicate.'],
  ];
  addTreeTrace(body, ui, 'Trace the sentence groups', steps);
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
    { id: 'introduction', title: 'Introduction to grammatical functions' },
    { id: 'concepts', title: 'Subject, predicate, noun phrases and verb phrases' },
    { id: 'worked-example', title: 'Subject and predicate tree exercise' },
    { id: 'application', title: 'Dependency and function: heads, modifiers and complements' },
    { id: 'recap', title: 'Summary and exercises on grammatical functions', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Subject', 'The part paired with the predicate. It usually comes first in a simple English statement.'],
    ['Predicate', 'The part that tells what the subject does, what happens to it, or what it is like.'],
    ['Category', 'The kind of word or phrase, such as noun phrase or verb phrase.'],
    ['Function', 'The job a word or group does, such as subject or predicate.'],
    ['Sister nodes', 'Nodes that share the same parent.'],
    ['Head', 'The main word that gives a phrase its category.'],
    ['Modifier', 'A word or group that adds a detail about another word or group.'],
    ['Complement', 'A word or group that fills a role its head calls for in that use.'],
  ],
  teach(body, page, ui) {
    const { el, button, lesson } = ui;
    const p = text => body.append(el('p', text));
    const heading = text => body.append(el('h3', text));
    const example = text => body.append(lessonExample(el, text));

    if (page === 0) {
      p('In Chapter 1, you tested which words belong together. Now you’ll use those groups to take a sentence apart. A grammatical function is the job a word or group does in a sentence. First you’ll identify the subject and predicate. Then you’ll look inside phrases to find complements, the groups that fill roles made available by a head.');
      addIntroExample(body, el, 'In the example below, read each bracketed group on its own. See which one names the lantern and which one tells you what it is doing.',
        '[The lantern by the stairs] [is glowing].',
        '“The lantern by the stairs” is the subject. “Is glowing” is the predicate. Those names tell you each group’s function, or job. The category tells you what kind of phrase it is. You’ll use a yes/no question to check where the whole subject ends.');
      heading('What you’ll learn in this chapter');
      const list = el('ul');
      for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
      body.append(list);
    }
    if (page === 1) {
      p('The subject is the group a predicate says something about. In a basic statement tree, the subject and predicate share a parent, S. Compare the statement and yes/no question below to find where the whole subject ends.');
      p('In “The lantern by the stairs is glowing”, “lantern” alone names the object, but it does not include the words that identify which lantern. In the question, “the lantern by the stairs” moves as a group relative to “is”. Use the whole group when you mark the subject.');
      example(`${lantern}.`);
      example('Is the lantern by the stairs glowing?');
      p('In the question, “is” comes before the whole subject and “glowing” comes after it. In the statement, “is glowing” is the whole predicate.');
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
      const exercise = el('section', undefined, 'lesson-practice-panel');
      exercise.append(el('p', 'Pick the last word of the subject in the statement.'), words, feedback);
      body.append(exercise);
    }
    if (page === 2) {
      p('A noun phrase is built around a noun and is labelled NP. A verb phrase is built around a verb and is labelled VP. In the example “Mira checked the lantern”, “lantern” heads the NP “the lantern”, and “checked” heads the VP “checked the lantern”. In the short sentence tree below, the subject NP and predicate VP share S as their parent. Nodes that share a parent are sisters.');
      p('Next, look at a sentence with two NPs. Follow one branch up from each NP. Its parent helps show what job the NP does.');
      p('Think of category as the kind of group and function as its job here. In “Mira checked the lantern”, both “Mira” and “the lantern” are NPs. Switch them in “The lantern startled Mira” and both categories stay the same, while “Mira” is now the object. A tree shows the difference by placing the two NPs under different parents.');
      trace(body, ui);
      heading('Repair one branch');
      example(`${repairSentence}.`);
      p('Attach “the lantern” to VP. The NP and “checked” should share that parent. Choose Guide me if you need help.');
      repair(body, ui);
    }
    if (page === 3) {
      p('A head is the word that gives a phrase its category. A modifier adds information about the head or its group. A complement fills a role the head makes available in a particular use. A verb can take an object as its complement, and a preposition can take a group that names a landmark. In the examples below, try leaving out one part at a time to see how the roles differ.');
      example('Tessa repaired a loose hinge.');
      p('In “a loose hinge”, “hinge” is the head. “Loose” is a modifier because it adds a detail. “Tessa repaired a hinge” still makes sense without it. The whole NP “a loose hinge” is a complement of “repaired”. It tells what Tessa repaired.');
      example('Ava slipped beside the counter.');
      p('“Beside” and “the counter” share a parent. You can leave out the whole location. If you keep “beside” with this meaning, “the counter” fills the complement role. It tells what the location is beside.');
      p('Use the omission test at two levels. In the example about Ava, you can leave out the entire location and still have “Ava slipped”. Inside the location phrase, “the counter” is needed to say what the person was beside. A group can be optional as a whole while containing parts that depend on each other.');
      heading('Try a new sentence');
      example('Leo tightened a loose bolt.');
      p('Write the subject and predicate. Then say which word “loose” describes and which group tells what Leo tightened.');
      const hint = el('details', undefined, 'lesson-sources');
      hint.append(el('summary', 'Hint'), el('p', 'Compare “Leo tightened a bolt” with the original. Which word can disappear while the thing being tightened is still named?'));
      body.append(hint);
      const key = `syntutor:lesson-transfer:${ui.userId}:br-02@${lesson.content_version}:application`;
      addExplanationPractice(body, ui, {
        key, id: 'chapter-two-transfer',
        explanation: '“Leo” is the subject. “Tightened a loose bolt” is the predicate. “Loose” modifies “bolt”, and “a loose bolt” is the full complement of “tightened”.',
      });
    }
    if (page === 4) {
      p('Find the biggest groups first. Use a yes/no question to check where the subject ends. Then go back to the statement to find the whole predicate.');
      p('Name each group’s category, then find its parent. In these trees, the NP directly under S is the subject. The NP under VP has its own job.');
      p('Compare the sisters inside a phrase. A modifier adds a detail you can often leave out. A complement fills a role the head calls for. Keep the same meaning when you test what happens if you leave words out.');
    }
  },
};
