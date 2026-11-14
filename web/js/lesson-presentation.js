export function hasExampleBrackets(text) {
  return /\[[^\]]+\]/.test(text);
}

export function lessonExample(el, text) {
  const style = hasExampleBrackets(text)
    ? 'lesson-example-sentence lesson-bracketed-example'
    : 'lesson-example-sentence';
  return el('p', text, style);
}

export function addIntroExample(body, el, context, example, explanation) {
  const panel = el('div', undefined, 'lesson-intro-example');
  panel.append(
    el('p', context),
    lessonExample(el, example),
    el('p', explanation),
  );
  body.append(panel);
}

export function setTreeStepLabel(control, el, label, number) {
  if (number === undefined) {
    control.textContent = label;
    control.removeAttribute('aria-description');
    return;
  }
  const badge = el('span', String(number), 'lesson-tree-step-number');
  badge.setAttribute('aria-hidden', 'true');
  control.replaceChildren(badge, label);
  control.setAttribute('aria-description', `Step ${number}`);
}

export function addTreeTrace(body, { el, button, showDiagram }, label, steps) {
  const figure = el('div', undefined, 'constituent-diagram');
  const controls = el('div', undefined, 'lesson-tree-steps');
  controls.setAttribute('role', 'group');
  controls.setAttribute('aria-label', label);
  const canvas = el('div');
  const note = el('div', undefined, 'lesson-tree-observation');
  note.setAttribute('aria-live', 'polite');
  const caption = el('p');
  note.append(caption);
  const buttons = steps.map(([text], i) => {
    const control = button(text, () => show(i));
    setTreeStepLabel(control, el, text, i + 1);
    return control;
  });
  function show(index) {
    const [, tree, focusId, explanation] = steps[index];
    buttons.forEach((control, i) => control.setAttribute('aria-pressed', String(i === index)));
    showDiagram(canvas, tree, { focusId, highlightWords: true, wordBaseline: 3 });
    caption.textContent = explanation;
  }
  controls.append(...buttons);
  figure.append(controls, canvas, note);
  body.append(figure);
  show(0);
}
