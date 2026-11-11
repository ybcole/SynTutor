import { NODE, addPhrase, addWordsFromText, canConnect, childrenOf, connect, createModel, roots } from './syntax-builder.js';

const sentence = 'beside the red gate';
const guide = [
  {
    title: 'Make a place for the smaller group',
    text: 'Add PHRASE-b above “the red gate”. Right-click the canvas to add the node yourself, or use the button below.',
    action: 'Add PHRASE-b',
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
    title: 'Put the smaller group inside the larger one',
    text: 'Drag from the connector on PHRASE-a to PHRASE-b. This puts the smaller group inside the whole phrase.',
    action: 'Connect the phrase nodes',
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
    title: 'Connect the words that belong together',
    text: 'Connect “the”, “red”, and “gate” to PHRASE-b. Keep “beside” attached directly to PHRASE-a.',
    action: 'Connect the gate words',
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
    title: 'Read the tree you built',
    text: 'Follow the branches from PHRASE-b down to the words. Do they reach exactly “the red gate”? Use Check construction to see what the tree says.',
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

export function addConstituentTreeBuilder(body, { el, button, mountBuilder }) {
  const workspace = el('section', undefined, 'first-tree-builder');
  workspace.setAttribute('aria-label', 'Build your first tree exercise');
  const guidance = el('div', undefined, 'first-tree-guide');
  guidance.hidden = true;
  const instructions = el('div');
  instructions.setAttribute('aria-live', 'polite');
  const count = el('p', undefined, 'first-tree-guide-step');
  const title = el('h4');
  const instruction = el('p');
  instructions.append(count, title, instruction);
  const actions = el('div', undefined, 'first-tree-guide-actions');
  const status = el('p', undefined, 'first-tree-feedback');
  status.setAttribute('role', 'status');
  let index = 0;
  const previous = button('Previous hint', () => showHint(index - 1));
  const next = button('Next hint', () => showHint(index + 1));
  const apply = button('', () => { status.textContent = editor.edit(guide[index].apply); });
  function showHint(step) {
    index = step;
    count.textContent = `Step ${step + 1} of ${guide.length}`;
    title.textContent = guide[step].title;
    instruction.textContent = guide[step].text;
    apply.textContent = guide[step].action || '';
    apply.hidden = !guide[step].apply;
    previous.disabled = step === 0;
    next.disabled = step === guide.length - 1;
  }
  actions.append(previous, next, apply);
  guidance.append(instructions, actions);
  const toggle = button('Guide me', () => {
    guidance.hidden = !guidance.hidden;
    toggle.setAttribute('aria-expanded', String(!guidance.hidden));
    if (!guidance.hidden) showHint(index);
  });
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-controls', 'first-tree-guide');
  guidance.id = 'first-tree-guide';

  const stage = el('div', undefined, 'first-tree-stage');
  const checkButton = button('Check construction', () => { status.textContent = editor.check(); });
  const toolbar = el('div', undefined, 'first-tree-toolbar');
  toolbar.append(toggle, checkButton);
  workspace.append(toolbar, guidance, stage, status);
  body.append(workspace);
  const editor = mountBuilder(stage, { id: 'br-01', seed, check });
}
