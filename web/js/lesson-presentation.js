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
