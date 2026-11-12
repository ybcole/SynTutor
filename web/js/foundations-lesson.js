export function addWorkedExample(body, { el, button, lesson, showWorkedTree }, labels, { highlightWords = false, captions } = {}) {
  const worked = lesson.worked_example;
  body.append(el('p', worked.sentence, 'lesson-example-sentence'));
  if (!worked.tree) {
    const steps = el('ol');
    for (const step of worked.steps) steps.append(el('li', step.text));
    body.append(steps);
    return;
  }
  const controls = el('div', undefined, 'constituent-controls lesson-tree-steps');
  controls.setAttribute('role', 'group');
  controls.setAttribute('aria-label', 'Explore the worked tree');
  const diagram = el('div', undefined, 'constituent-diagram');
  const caption = el('p', undefined, 'constituent-caption');
  caption.setAttribute('aria-live', 'polite');
  const choices = worked.steps.map((step, index) => button(labels[index], () => select(index)));
  function describe(index) {
    choices.forEach((choice, position) => choice.setAttribute('aria-pressed', String(position === index)));
    caption.textContent = captions?.[index] ?? worked.steps[index].text;
  }
  function select(index) {
    describe(index);
    showWorkedTree(diagram, worked.steps[index].focus_node_id, {
      highlightWords,
      onSelect: highlightWords ? nodeId => {
        const selected = worked.steps.findIndex(step => step.focus_node_id === nodeId);
        if (selected !== -1) describe(selected);
      } : null,
    }).after(caption);
  }
  controls.append(...choices);
  body.append(controls, diagram);
  select(0);
}
