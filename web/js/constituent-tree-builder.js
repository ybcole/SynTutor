import { NODE, addPhrase, addWordsFromText, childrenOf, connect, createModel, roots } from './syntax-builder.js';

const sentence = 'beside the red gate';
const guide = [
  'Add PHRASE-b above “the red gate”, to the right of “beside”.',
  'Connect PHRASE-b to PHRASE-a. On the canvas, drag from the outer node’s connector dot to the inner node.',
  'Connect “the”, “red”, and “gate” to the inner node. Leave “beside” connected directly to the outer node.',
  'Select Check construction. The inner node should cover exactly “the red gate”.',
];

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

export function addConstituentTreeBuilder(body, { el, button, mountBuilder }) {
  const workspace = el('section', undefined, 'first-tree-builder');
  workspace.setAttribute('aria-label', 'Build your first tree exercise');
  const guidance = el('div', undefined, 'first-tree-guide');
  guidance.hidden = true;
  const instruction = el('p');
  instruction.setAttribute('aria-live', 'polite');
  let index = 0;
  const previous = button('Previous hint', () => showHint(index - 1));
  const next = button('Next hint', () => showHint(index + 1));
  function showHint(step) {
    index = step;
    instruction.textContent = `Step ${step + 1} of ${guide.length}. ${guide[step]}`;
    previous.disabled = step === 0;
    next.disabled = step === guide.length - 1;
  }
  guidance.append(instruction, previous, next);
  const toggle = button('Guide me', () => {
    guidance.hidden = !guidance.hidden;
    toggle.setAttribute('aria-expanded', String(!guidance.hidden));
    if (!guidance.hidden) showHint(index);
  });
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-controls', 'first-tree-guide');
  guidance.id = 'first-tree-guide';

  const stage = el('div', undefined, 'first-tree-stage');
  workspace.append(toggle, guidance, stage);
  body.append(workspace);
  mountBuilder(stage, { id: 'br-01', seed, check });
}
