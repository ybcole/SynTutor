export function addEmbeddedTreeExercise(body, { el, button, mountBuilder }, { label, guide, ...exercise }) {
  const workspace = el('section', undefined, 'first-tree-builder');
  workspace.setAttribute('aria-label', label);
  const guidance = el('ol', undefined, 'first-tree-guide');
  guidance.id = `first-tree-guide-${exercise.id}`;
  guidance.setAttribute('role', 'list');
  guidance.hidden = true;
  const status = el('p', undefined, 'first-tree-feedback');
  status.setAttribute('role', 'status');
  function checkTree() {
    status.textContent = editor.check();
  }
  for (const [index, step] of guide.entries()) {
    const item = el('li');
    const action = button(undefined, () => {
      if (step.apply) status.textContent = editor.edit(step.apply);
      else checkTree();
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
  const checkButton = button('Check construction', checkTree);
  const toolbar = el('div', undefined, 'first-tree-toolbar');
  toolbar.append(toggle, checkButton);
  workspace.append(toolbar, guidance, status, stage);
  body.append(workspace);
  const editor = mountBuilder(stage, exercise);
}
