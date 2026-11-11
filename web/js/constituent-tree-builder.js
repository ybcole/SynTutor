import {
  NODE, addPhrase, addWordsFromText, childrenOf, connect, createModel, disconnect, removeNode,
} from './syntax-builder.js';

const SVG_NS = 'http://www.w3.org/2000/svg';
const labelFor = node => node.kind === NODE.WORD ? node.text : node.type;

export function addConstituentTreeBuilder(body, { el, button }) {
  const model = createModel();
  const outer = addPhrase(model, 'PHRASE-a', 0, 0);
  const words = addWordsFromText(model, 'beside the red gate', 0, 0);
  const wordIndex = new Map(words.map(({ id }, index) => [id, index]));
  for (const word of words) connect(model, outer.id, word.id);

  let selected = outer.id;
  let choosingParent = false;
  let nextPhrase = 1;
  const workspace = el('section', undefined, 'first-tree-builder');
  workspace.setAttribute('aria-label', 'Build your first tree exercise');
  const status = el('p', 'Add a phrase node to get started.', 'first-tree-status');
  status.setAttribute('role', 'status');
  const canvas = el('div', undefined, 'first-tree-canvas');
  canvas.setAttribute('role', 'group');
  canvas.setAttribute('aria-label', 'Editable tree canvas');
  const surface = el('div', undefined, 'first-tree-surface');
  canvas.append(surface);

  const toolbar = el('div', undefined, 'first-tree-toolbar');
  const add = button('Add phrase node', () => {
    const parent = model.nodes[selected].kind === NODE.PHRASE ? selected : model.nodes[selected].parent;
    const suffix = nextPhrase < 26 ? String.fromCharCode(97 + nextPhrase) : String(nextPhrase + 1);
    nextPhrase++;
    const node = addPhrase(model, `PHRASE-${suffix}`, words.length * 70, 0);
    connect(model, parent || outer.id, node.id);
    choose(node.id);
    status.textContent = `Added ${node.type}. Select a word and connect it to this node.`;
  });
  const canvasLink = button('Connect on canvas', () => {
    choosingParent = !choosingParent;
    updateControls();
    status.textContent = choosingParent
      ? `Select a phrase node on the canvas to be the parent of “${labelFor(model.nodes[selected])}”.`
      : 'Canvas connection canceled.';
  });
  canvasLink.setAttribute('aria-pressed', 'false');
  toolbar.append(add, canvasLink);

  const controls = el('div', undefined, 'first-tree-controls');
  const selectedNode = el('select');
  const parentNode = el('select');
  const name = el('input');
  name.type = 'text';
  name.maxLength = 24;
  function field(title, input) {
    const label = el('label', title);
    label.append(input);
    return label;
  }
  selectedNode.addEventListener('change', () => choose(selectedNode.value));
  const connectButton = button('Connect to parent', () => attach(parentNode.value));
  const detach = button('Disconnect', () => {
    disconnect(model, selected);
    status.textContent = `Disconnected “${labelFor(model.nodes[selected])}” from its parent.`;
    update();
  });
  const rename = button('Rename phrase', () => {
    const label = name.value.trim();
    if (!label) {
      status.textContent = 'Enter a name for the phrase node.';
      return;
    }
    if (Object.values(model.nodes).some(node => node.id !== selected && labelFor(node) === label)) {
      status.textContent = 'Choose a different name so you can tell the nodes apart.';
      return;
    }
    model.nodes[selected].type = label;
    status.textContent = `Renamed the phrase to “${label}”.`;
    update();
  });
  const remove = button('Delete phrase', () => {
    const label = labelFor(model.nodes[selected]);
    removeNode(model, selected);
    choose(outer.id);
    status.textContent = `Deleted “${label}”. Any children are available to reconnect.`;
  });
  const parentControls = el('div', undefined, 'first-tree-field');
  parentControls.append(field('Parent phrase', parentNode), connectButton, detach);
  const phraseControls = el('div', undefined, 'first-tree-field');
  phraseControls.append(field('Phrase name', name), rename, remove);
  controls.append(field('Selected node', selectedNode), parentControls, phraseControls);

  const hint = el('details');
  hint.append(el('summary', 'Need a hint?'),
    el('p', 'Keep “beside” under the outer node. Add another phrase and connect “the”, “red”, and “gate” to it.'));
  const check = button('Check my tree', checkTree, 'lesson-primary');
  workspace.append(toolbar, canvas, controls, hint, check, status);
  body.append(workspace);
  update();

  function wordsUnder(node) {
    return node.kind === NODE.WORD ? [node] : childrenOf(model, node.id).flatMap(wordsUnder);
  }

  function checkTree() {
    const nodes = Object.values(model.nodes);
    if (nodes.some(node => node.id !== outer.id && !node.parent)) {
      status.textContent = 'Connect each node to the tree before checking.';
      return;
    }
    const groups = nodes.filter(node => node.kind === NODE.PHRASE);
    const empty = groups.find(node => !wordsUnder(node).length);
    if (empty) {
      status.textContent = `“${empty.type}” has no words under it yet. Connect a word or remove the empty phrase.`;
      return;
    }
    for (const node of groups) {
      const positions = wordsUnder(node).map(word => wordIndex.get(word.id)).sort((a, b) => a - b);
      if (positions.at(-1) - positions[0] + 1 !== positions.length) {
        status.textContent = `“${node.type}” skips words in the phrase. Give it a group of consecutive words.`;
        return;
      }
    }
    const gateGroup = groups.find(node => node.parent === outer.id
      && wordsUnder(node).map(word => wordIndex.get(word.id)).sort((a, b) => a - b).join(',') === '1,2,3');
    if (words[0].parent === outer.id && gateGroup) {
      status.textContent = `Exactly. “${gateGroup.type}” covers “the red gate”. “Beside” connects directly to the outer node.`;
      return;
    }
    const covered = wordsUnder(model.nodes[selected]).sort((a, b) => a.x - b.x).map(labelFor).join(' ');
    status.textContent = `“${labelFor(model.nodes[selected])}” covers “${covered}”. Look for a branch under the outer node that covers exactly “the red gate”.`;
  }

  function attach(parentId, restoreFocus = false) {
    if (!connect(model, parentId, selected)) {
      status.textContent = 'Choose a phrase that would keep the tree free of loops.';
      return;
    }
    choosingParent = false;
    status.textContent = `Connected “${labelFor(model.nodes[selected])}” to “${labelFor(model.nodes[parentId])}”.`;
    update(restoreFocus);
  }

  function choose(id, restoreFocus = false) {
    selected = id;
    choosingParent = false;
    update(restoreFocus);
  }

  function setOptions(select, nodes, value) {
    select.replaceChildren(...nodes.map(node => {
      const option = el('option', labelFor(node));
      option.value = node.id;
      return option;
    }));
    if ([...select.options].some(option => option.value === value)) select.value = value;
  }

  function updateControls() {
    const node = model.nodes[selected];
    const nodes = Object.values(model.nodes);
    setOptions(selectedNode, nodes, selected);
    setOptions(parentNode, nodes.filter(item => item.kind === NODE.PHRASE && item.id !== selected), node.parent);
    name.value = node.type;
    parentControls.hidden = selected === outer.id;
    phraseControls.hidden = selected === outer.id || node.kind !== NODE.PHRASE;
    detach.disabled = !node.parent;
    connectButton.disabled = parentNode.options.length === 0;
    canvasLink.disabled = selected === outer.id || connectButton.disabled;
    canvasLink.setAttribute('aria-pressed', String(choosingParent));
  }

  function update(restoreFocus = false) {
    updateControls();
    const nodes = Object.values(model.nodes);
    const phrases = nodes.filter(node => node.kind === NODE.PHRASE);
    const positions = new Map();
    const occupied = new Map();
    const spacing = Math.max(76, Math.min(116, Math.floor((canvas.clientWidth - 16) / words.length)));
    const inset = spacing / 2 + 8;
    surface.style.setProperty('--node-width', `${spacing - 8}px`);
    function depth(node) {
      return node.parent ? depth(model.nodes[node.parent]) + 1 : node.id === outer.id ? 0 : 1;
    }
    const wordY = Math.max(...phrases.map(depth)) * 68 + 96;
    words.forEach((word, index) => positions.set(word.id, { x: inset + index * spacing, y: wordY }));
    for (const node of phrases) {
      const row = depth(node);
      const covered = wordsUnder(node);
      const xs = covered.map(word => positions.get(word.id).x);
      let x = xs.length ? (Math.min(...xs) + Math.max(...xs)) / 2 : inset + (words.length - 1) * spacing / 2;
      const used = occupied.get(row) || [];
      while (used.some(position => Math.abs(position - x) < spacing)) x += spacing;
      used.push(x);
      occupied.set(row, used);
      positions.set(node.id, { x, y: 36 + row * 68 });
    }
    const width = Math.max(...[...positions.values()].map(point => point.x)) + inset;
    surface.style.width = `min(100%, ${width}px)`;
    surface.style.minWidth = `${Math.ceil(width / spacing * 72)}px`;
    surface.style.height = `${wordY + 38}px`;
    const branches = document.createElementNS(SVG_NS, 'svg');
    branches.setAttribute('aria-hidden', 'true');
    branches.setAttribute('preserveAspectRatio', 'none');
    branches.setAttribute('viewBox', `0 0 ${width} ${wordY + 38}`);
    for (const node of nodes) {
      if (!node.parent) continue;
      const from = positions.get(node.parent);
      const to = positions.get(node.id);
      const line = document.createElementNS(SVG_NS, 'line');
      for (const [key, value] of Object.entries({ x1: from.x, y1: from.y + 17, x2: to.x, y2: to.y - 17 })) {
        line.setAttribute(key, value);
      }
      branches.append(line);
    }
    let selectedButton;
    const nodeButtons = nodes.map(node => {
      const position = positions.get(node.id);
      const control = button(labelFor(node), () => {
        if (choosingParent) attach(node.id, true);
        else choose(node.id, true);
      }, 'first-tree-node');
      control.style.left = `${position.x / width * 100}%`;
      control.style.top = `${position.y}px`;
      control.dataset.kind = node.kind;
      control.title = labelFor(node);
      control.setAttribute('aria-pressed', String(node.id === selected));
      if (node.parent) control.setAttribute('aria-description', `Connected to ${labelFor(model.nodes[node.parent])}`);
      if (node.id === selected) selectedButton = control;
      return control;
    });
    surface.replaceChildren(branches, ...nodeButtons);
    if (restoreFocus) selectedButton?.focus({ preventScroll: true });
  }
}
