import { addEmbeddedTreeExercise } from './lesson-tree-exercise.js';
import { NODE, addPhrase, addWordsFromText, canConnect, childrenOf, connect, createModel, roots } from './syntax-builder.js';

const sentence = 'beside the red gate';
const guide = [
  {
    title: 'Add PHRASE-b',
    text: 'Place an inner node above “the red gate”.',
    apply(model) {
      if (Object.values(model.nodes).some(node => node.kind === NODE.PHRASE && node.type === 'PHRASE-b')) {
        return 'PHRASE-b is already on the canvas.';
      }
      const words = gateWords(model);
      if (!words) return 'The canvas needs one copy each of “the”, “red”, and “gate”.';
      const x = words.reduce((sum, word) => sum + word.x, 0) / words.length;
      const y = Math.min(...words.map(word => word.y)) - 70;
      addPhrase(model, 'PHRASE-b', x, y);
      return 'PHRASE-b is ready for its branches.';
    },
  },
  {
    title: 'Connect PHRASE-b to PHRASE-a',
    text: 'Attach the smaller group to the outer phrase.',
    apply(model) {
      const outer = findPhrase(model, 'PHRASE-a');
      const inner = findPhrase(model, 'PHRASE-b');
      if (!outer || !inner) return 'Put one PHRASE-a and one PHRASE-b on the canvas first.';
      return connect(model, outer.id, inner.id)
        ? 'PHRASE-b now sits under PHRASE-a.'
        : 'Disconnect any branch from PHRASE-b to PHRASE-a first to avoid a loop.';
    },
  },
  {
    title: 'Connect “the red gate” to PHRASE-b',
    text: 'Attach the three words to the inner node. Leave “beside” under PHRASE-a.',
    apply(model) {
      const inner = findPhrase(model, 'PHRASE-b');
      const words = gateWords(model);
      if (!inner || !words) return 'Put one PHRASE-b and one copy of each gate word on the canvas first.';
      if (!words.every(word => canConnect(model, inner.id, word.id))) {
        return 'Expand PHRASE-b before attaching the words.';
      }
      for (const word of words) connect(model, inner.id, word.id);
      return 'PHRASE-b now covers “the red gate”.';
    },
  },
  {
    title: 'Check the tree',
    text: 'See whether the inner node covers exactly “the red gate”.',
  },
];

function findPhrase(model, label) {
  const matches = Object.values(model.nodes).filter(node => node.kind === NODE.PHRASE && node.type === label);
  return matches.length === 1 ? matches[0] : null;
}

function gateWords(model) {
  const nodes = Object.values(model.nodes);
  const matches = ['the', 'red', 'gate'].map(word => nodes.filter(node => node.kind === NODE.WORD && node.text === word));
  return matches.every(group => group.length === 1) ? matches.flat() : null;
}

function seed() {
  const model = createModel();
  const outer = addPhrase(model, 'PHRASE-a', 132, 20);
  const words = addWordsFromText(model, sentence, 0, 175, 24);
  for (const word of words) connect(model, outer.id, word.id);
  return model;
}

function check(model) {
  const top = roots(model);
  if (top.length !== 1 || top[0].kind !== NODE.PHRASE) {
    return 'Connect each word and phrase under a single outer node.';
  }
  const outer = top[0];
  const groupWords = node => node.kind === NODE.WORD
    ? [node.text]
    : childrenOf(model, node.id).flatMap(groupWords);
  const empty = Object.values(model.nodes).find(node => node.kind === NODE.PHRASE && !groupWords(node).length);
  if (empty) return `“${empty.type}” has no words under it yet. Connect a word or remove the empty phrase.`;
  if (groupWords(outer).join(' ') !== sentence) return 'Keep all four words in order: beside the red gate.';
  const immediate = childrenOf(model, outer.id);
  const group = immediate.find(node => node.kind === NODE.PHRASE && groupWords(node).join(' ') === 'the red gate');
  if (group && immediate.some(node => node.kind === NODE.WORD && node.text === 'beside')) {
    return `Exactly. “${group.type}” covers “the red gate”. “Beside” connects directly to the outer node.`;
  }
  return 'Look for a branch under the outer node that covers exactly “the red gate”.';
}

export function addConstituentTreeBuilder(body, ui) {
  addEmbeddedTreeExercise(body, ui, { id: 'br-01', label: 'Build your first tree exercise', guide, seed, check });
}
