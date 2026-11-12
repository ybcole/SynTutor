export function addIntroExample(body, el, context, example, explanation) {
  const panel = el('div', undefined, 'lesson-intro-example');
  panel.append(
    el('p', context),
    el('p', example, 'lesson-example-sentence'),
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
