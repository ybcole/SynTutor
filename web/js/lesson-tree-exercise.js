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
