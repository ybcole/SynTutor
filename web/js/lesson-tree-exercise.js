import { connect, disconnect, fromCanonicalEnvelope, paletteFor, toCanonicalEnvelope } from './syntax-builder.js';

function rootLabelsOf(node, out = []) {
  if (!node) return out;
  if (node.label) out.push(node.label);
  for (const child of node.children || []) rootLabelsOf(child, out);
  return out;
}

function allowedLabelsForExercise(ui, target, profile) {
  const valid = paletteFor(profile).labels;
  const validSet = new Set(valid);
  const sectionLabels = ui.section?.notationLabels;
  if (!Array.isArray(sectionLabels) || !sectionLabels.length) return valid;
  const seen = new Set();
  const picked = [];
  for (const lbl of [...sectionLabels, ...rootLabelsOf(target?.root)]) {
    if (!validSet.has(lbl) || seen.has(lbl)) continue;
    seen.add(lbl);
    picked.push(lbl);
  }
  return picked.length ? picked : valid;
}

export function addEmbeddedTreeExercise(body, { el, button, mountBuilder }, { label, guide, ...exercise }) {
  const workspace = el('section', undefined, 'first-tree-builder');
  workspace.setAttribute('aria-label', label);
  const guidance = el('ol', undefined, 'first-tree-guide');
  guidance.id = `first-tree-guide-${exercise.id}`;
  guidance.setAttribute('role', 'list');
  guidance.hidden = true;
  const status = el('p', undefined, 'first-tree-feedback');
  status.setAttribute('role', 'status');
  function showFeedback(message) {
    status.textContent = message;
  }
  for (const [index, step] of guide.entries()) {
    const item = el('li');
    const action = button(undefined, () => {
      showFeedback(step.apply ? editor.edit(step.apply) : editor.check());
    }, 'first-tree-guide-action');
    const number = el('span', `${index + 1}.`, 'first-tree-guide-number');
    number.setAttribute('aria-hidden', 'true');
    action.append(number, el('strong', step.title), el('span', step.text, 'first-tree-guide-description'));
    item.append(action);
    guidance.append(item);
  }
  const toggle = button('Guide me', () => {
    guidance.hidden = !guidance.hidden;
    toggle.setAttribute('aria-expanded', String(!guidance.hidden));
  });
  toggle.setAttribute('aria-expanded', 'false');
  toggle.setAttribute('aria-controls', guidance.id);

  const stage = el('div', undefined, 'first-tree-stage');
  const workspaceRow = el('div', undefined, 'first-tree-workspace');
  const palette = el('aside', undefined, 'first-tree-palette');
  palette.setAttribute('aria-label', 'Add a node');
  const paletteHead = el('div', undefined, 'first-tree-palette-head');
  paletteHead.append(el('h4', 'Add a node'));
  const paletteList = el('div', undefined, 'first-tree-palette-list');
  const paletteToggle = button('Hide', () => {
    const collapsed = palette.classList.toggle('is-collapsed');
    paletteList.hidden = collapsed;
    paletteToggle.textContent = collapsed ? 'Show' : 'Hide';
    paletteToggle.setAttribute('aria-expanded', String(!collapsed));
    paletteToggle.setAttribute('aria-label', collapsed ? 'Show node buttons' : 'Hide node buttons');
    workspaceRow.classList.toggle('is-palette-collapsed', collapsed);
    editor?.fit?.();
  }, 'first-tree-palette-toggle');
  paletteToggle.setAttribute('aria-expanded', 'true');
  paletteToggle.setAttribute('aria-label', 'Hide node buttons');
  paletteHead.append(paletteToggle);
  palette.append(paletteHead, paletteList);
  workspaceRow.append(stage, palette);
  const toolbar = el('div', undefined, 'first-tree-toolbar');
  const help = el('div', undefined, 'first-tree-help');
  help.append(toggle, button('Restart exercise', () => {
    editor.restart();
    showFeedback('Starting tree restored. Use Undo to return to your previous tree.');
  }));
  const controls = el('div', undefined, 'first-tree-controls');
  const undo = button('↶', () => {
    showFeedback(editor.undo() ? 'Last edit undone.' : 'There is no edit to undo in this visit.');
  }, 'first-tree-undo');
  undo.setAttribute('aria-label', 'Undo');
  undo.title = 'Undo';
  const zoomIn = button('+', () => editor.zoom?.(1.25), 'first-tree-zoom-btn');
  zoomIn.dataset.embeddedZoom = 'in';
  zoomIn.setAttribute('aria-label', 'Zoom in on syntax tree');
  const zoomOut = button('−', () => editor.zoom?.(0.8), 'first-tree-zoom-btn');
  zoomOut.dataset.embeddedZoom = 'out';
  zoomOut.setAttribute('aria-label', 'Zoom out of syntax tree');
  const fitBtn = button('Fit', () => editor.fit?.(), 'first-tree-fit-btn');
  fitBtn.dataset.embeddedFit = 'true';
  fitBtn.setAttribute('aria-label', 'Fit syntax tree');
  controls.append(undo, zoomOut, zoomIn, fitBtn);
  toolbar.append(help, controls);

  const footer = el('div', undefined, 'first-tree-footer');
  footer.append(status, button('Check my tree', () => showFeedback(editor.check()), 'lesson-primary'));
  workspace.append(toolbar, guidance, workspaceRow, footer);
  body.append(workspace);
  const editor = mountBuilder(stage, exercise);
  const nodeLabels = editor.labels?.() || [];
  if (nodeLabels.length) {
    for (const nodeLabel of nodeLabels) {
      const addBtn = button(nodeLabel, () => {
        editor.addNode?.(nodeLabel);
        showFeedback(`Added ${nodeLabel}. Drag its purple dot to connect a child, or drag another dot onto it.`);
      }, 'first-tree-node-btn');
      addBtn.dataset.nodeLabel = nodeLabel;
      addBtn.setAttribute('aria-label', `Add ${nodeLabel} node`);
      paletteList.append(addBtn);
    }
    if (typeof window !== 'undefined' && window.innerWidth <= 760) {
      palette.classList.add('is-collapsed');
      paletteList.hidden = true;
      paletteToggle.textContent = 'Show';
      paletteToggle.setAttribute('aria-expanded', 'false');
      paletteToggle.setAttribute('aria-label', 'Show node buttons');
      workspaceRow.classList.add('is-palette-collapsed');
    }
  } else {
    palette.hidden = true;
    workspaceRow.classList.add('is-no-palette');
  }
  editor?.fit?.();
}

// Compare the visible analysis independently of the IDs assigned to edits.
function shape(node) {
  return [node.label, node.word, node.words, node.features || [], node.gap, node.index, node.children?.map(shape)];
}

export function addBranchExercise(body, ui, chapter) {
  const target = ui.lesson.worked_example.tree;
  const [parent, child] = chapter.build.branch(target.root);
  const profile = target.convention_profile;
  const expected = JSON.stringify(shape(target.root));
  function branchFeedback(model) {
    const current = model.nodes[child.id];
    const intended = model.nodes[parent.id];
    if (!current || !intended) return 'A starting node is missing. Choose Restart exercise to restore it, or recreate it on the canvas.';
    if (!current.parent) return `The target branch is still detached. ${chapter.build.hint}`;
    if (current.parent !== parent.id) {
      return `The target branch is attached to ${model.nodes[current.parent].type}. ${chapter.build.hint}`;
    }
    return null;
  }
  addEmbeddedTreeExercise(body, ui, {
    id: `${ui.lesson.lesson_id}-branch`,
    label: `${chapter.buildTitle} exercise`,
    profile,
    labels: allowedLabelsForExercise(ui, target, profile),
    seed() {
      const model = fromCanonicalEnvelope(target);
      disconnect(model, child.id);
      return model;
    },
    check(model) {
      try {
        const built = toCanonicalEnvelope(model, profile);
        if (JSON.stringify(shape(built.root)) === expected) return chapter.build.success;
      } catch (error) {
        return branchFeedback(model) ?? `${error.message} ${chapter.build.hint}`;
      }
      return branchFeedback(model) ?? `The branch is attached. Check the rest of the tree against the worked example. ${chapter.build.hint}`;
    },
    guide: [{
      title: chapter.build.action,
      text: chapter.build.hint,
      apply(model) {
        if (!model.nodes[parent.id] || !model.nodes[child.id]) {
          return 'A starting node is missing. Choose Restart exercise to restore it, or recreate it on the canvas.';
        }
        return connect(model, parent.id, child.id) ? 'The branch is connected. Check how it fits into the whole tree.' : chapter.build.hint;
      },
    }, {
      title: 'Check the branch',
      text: 'See whether the groups attach in the intended order.',
    }],
  });
}
