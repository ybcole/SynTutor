import { connect, disconnect, fromCanonicalEnvelope, toCanonicalEnvelope } from './syntax-builder.js';

export function addEmbeddedTreeExercise(body, { el, button, mountBuilder }, { label, guide, ...exercise }) {
  const workspace = el('section', undefined, 'first-tree-builder');
  workspace.setAttribute('aria-label', label);
  const guidance = el('ol', undefined, 'first-tree-guide');
  guidance.id = `first-tree-guide-${exercise.id}`;
  guidance.setAttribute('role', 'list');
  guidance.hidden = true;
  const status = el('p', undefined, 'first-tree-feedback');
  status.setAttribute('role', 'status');
  const checkStatus = el('p', undefined, 'first-tree-feedback');
  checkStatus.setAttribute('role', 'status');
  function showFeedback(message, target = status) {
    (target === status ? checkStatus : status).textContent = '';
    target.textContent = message;
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
  const toolbar = el('div', undefined, 'first-tree-toolbar');
  const help = el('div', undefined, 'first-tree-help');
  help.append(toggle, button('Restart exercise', () => {
    editor.restart();
    showFeedback('Starting tree restored. Use Undo to return to your previous tree.');
  }));
  const undo = button('↶', () => {
    showFeedback(editor.undo() ? 'Last edit undone.' : 'There is no edit to undo in this visit.');
  }, 'first-tree-undo');
  undo.setAttribute('aria-label', 'Undo');
  undo.title = 'Undo';
  toolbar.append(help, undo);

  const footer = el('div', undefined, 'first-tree-footer');
  footer.append(checkStatus, button('Check my tree', () => showFeedback(editor.check(), checkStatus), 'lesson-primary'));
  workspace.append(toolbar, guidance, status, stage, footer);
  body.append(workspace);
  const editor = mountBuilder(stage, exercise);
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
