import { addEmbeddedTreeExercise } from './lesson-tree-exercise.js';
import { NODE, addPhrase, addWordsFromText, canConnect, childrenOf, connect, createModel, toCanonicalEnvelope } from './syntax-builder.js';

export function addSubjectPredicateBuilder(body, ui, {
  target = ui.lesson.worked_example.tree,
  id = ui.lesson.lesson_id,
  label = 'Build your first labelled tree exercise',
} = {}) {
  const { root, sentence, convention_profile: profile } = target;
  const branches = root.children;
  const labels = [root.label, ...branches.map(branch => branch.label)];
  const [subject, predicate] = branches.map(branch => branch.words.join(' '));
  const nodesFor = (model, kind, field, values) => values.map(value => {
    const matches = Object.values(model.nodes).filter(node => node.kind === kind && node[field] === value);
    return matches.length === 1 ? matches[0] : null;
  });
  const phrases = model => nodesFor(model, NODE.PHRASE, 'type', labels);

  function attach(model, links) {
    if (links.some(([parent, child]) => child.parent && child.parent !== parent.id)) {
      return 'One of these nodes already has a different parent. Move its branch before trying this step again.';
    }
    if (!links.every(([parent, child]) => child.parent === parent.id || canConnect(model, parent.id, child.id))) {
      return 'Expand any triangles or remove a conflicting branch before trying this step again.';
    }
    for (const [parent, child] of links) {
      if (child.parent !== parent.id) connect(model, parent.id, child.id);
    }
  }

  function check(model) {
    let tree;
    try {
      tree = toCanonicalEnvelope(model, profile);
    } catch (error) {
      return error.message;
    }
    if (tree.sentence !== sentence) return `Keep the words in this order: ${sentence}.`;
    const actual = tree.root.children || [];
    if (tree.root.label !== root.label || actual.length !== branches.length ||
        actual.some((branch, index) => branch.label !== branches[index].label)) {
      return 'Use S as the root, with NP on the left and VP on the right, both directly under S.';
    }
    for (const [index, branch] of branches.entries()) {
      const group = actual[index];
      const words = group.triangle ? group.words : group.children?.map(child => child.word);
      if (words?.join(' ') !== branch.words.join(' ')) {
        return `Connect exactly “${branch.words.join(' ')}” to ${branch.label}.`;
      }
      if (!group.triangle) return `Collapse ${branch.label} to a triangle to match the worked tree.`;
    }
    return `Your tree matches the target. NP covers “${subject}” and functions as the subject. VP covers “${predicate}” and functions as the predicate.`;
  }

  const guide = [
    {
      title: 'Add S, NP and VP',
      text: 'Put S at the top, with NP to the left and VP to the right.',
      apply(model) {
        const existing = Object.values(model.nodes).filter(node => node.kind === NODE.PHRASE);
        if (labels.some(label => existing.filter(node => node.type === label).length > 1)) {
          return 'Keep one of each label: S, NP and VP.';
        }
        const [left, right] = branches.map(branch => {
          const words = nodesFor(model, NODE.WORD, 'text', branch.words).filter(Boolean);
          return words.length ? (words[0].x + words.at(-1).x) / 2 : null;
        });
        const centers = [((left ?? 37) + (right ?? 214)) / 2, left ?? 37, right ?? 214];
        for (const [index, node] of phrases(model).entries()) {
          if (!node) addPhrase(model, labels[index], centers[index], index === 0 ? 20 : 100);
        }
        return 'S, NP and VP are on the canvas.';
      },
    },
    {
      title: 'Connect NP and VP to S',
      text: 'The two phrases share S as their parent.',
      apply(model) {
        const [top, np, vp] = phrases(model);
        if (!top || !np || !vp) return 'Put one S, one NP and one VP on the canvas first.';
        return attach(model, [[top, np], [top, vp]]) || 'NP and VP now sit directly under S. Keep NP to the left of VP.';
      },
    },
    {
      title: 'Connect the words to their phrases',
      text: `Attach “${subject}” to NP and “${predicate}” to VP.`,
      apply(model) {
        const [, ...groups] = phrases(model);
        const links = branches.flatMap((branch, index) =>
          nodesFor(model, NODE.WORD, 'text', branch.words).map(word => [groups[index], word]));
        if (links.some(([parent, word]) => !parent || !word)) {
          return `Use one NP, one VP and one copy of each word in “${sentence}”.`;
        }
        return attach(model, links) || `NP now covers “${subject}”. VP covers “${predicate}”.`;
      },
    },
    {
      title: 'Collapse both phrases and check',
      text: 'Use triangles to show which words belong to each phrase.',
      apply(model) {
        const [, ...groups] = phrases(model);
        if (groups.some(group => !group)) return 'Put one NP and one VP on the canvas first.';
        for (const [index, group] of groups.entries()) {
          const words = childrenOf(model, group.id).map(node => node.kind === NODE.WORD ? node.text : null);
          if (words.join(' ') !== branches[index].words.join(' ')) {
            return `Connect “${branches[index].words.join(' ')}” in order to ${group.type} first.`;
          }
        }
        for (const group of groups) group.canonicalTriangle = true;
        return check(model);
      },
    },
  ];

  addEmbeddedTreeExercise(body, ui, {
    id, label,
    profile, labels, guide, check,
    seed() {
      const model = createModel();
      addWordsFromText(model, sentence, 0, 190, 24);
      return model;
    },
  });
}
