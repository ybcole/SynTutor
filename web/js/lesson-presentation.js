import { foundationsBookContent, foundationsBookRecaps } from './foundations-book-content.js';

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

export function addFoundationsBookCoverage(body, el, lessonId, sectionId) {
  const entries = foundationsBookContent[lessonId]?.[sectionId] ?? [];
  const recap = sectionId === 'recap' && foundationsBookRecaps[lessonId];
  if (recap) body.append(el('p', recap));
  if (!entries.length) return;

  const practice = el('details', undefined, 'lesson-sources');
  practice.append(el('summary', 'Practice and feedback'));
  for (const [id, title, example, explanation, prompt, feedback] of entries) {
    const heading = el('h3', title);
    heading.id = id.toLowerCase();
    const paragraphs = explanation.split('\n\n').map(text => el('p', text));
    body.append(heading, lessonExample(el, example), ...paragraphs);

    const exercise = el('section');
    exercise.id = `${heading.id}-practice`;
    exercise.setAttribute('aria-label', title);
    const answer = el('details');
    answer.append(el('summary', 'Check your answer'), el('p', feedback));
    exercise.append(el('h4', title), el('p', prompt), answer);
    practice.append(exercise);
  }
  return practice;
}

export function treeStepGuide({ el, button }, label, labels, onSelect) {
  const controls = el('div', undefined, 'lesson-tree-steps lesson-tree-guide');
  controls.setAttribute('role', 'group');
  controls.setAttribute('aria-label', label);
  const title = el('p', undefined, 'lesson-tree-step-title');
  const picker = el('details', undefined, 'lesson-tree-step-picker');
  const number = el(labels.length > 1 ? 'summary' : 'span', undefined, 'lesson-tree-step-number');
  const choices = el('ol', undefined, 'lesson-tree-step-choices');
  let current = 0;

  function update(index) {
    current = index;
    const atEnd = index === labels.length - 1;
    number.textContent = String(index + 1);
    number.setAttribute('aria-label', `Step ${index + 1} of ${labels.length}${labels.length > 1 ? ' · Choose a step' : ''}`);
    title.textContent = labels[index];
    arrow.textContent = atEnd ? '←' : '→';
    arrow.setAttribute('aria-label', atEnd ? 'Previous step' : 'Next step');
    arrow.title = arrow.getAttribute('aria-label');
    for (const [i, choice] of Array.from(choices.children).entries()) {
      if (i === index) choice.firstElementChild.setAttribute('aria-current', 'step');
      else choice.firstElementChild.removeAttribute('aria-current');
    }
  }

  function select(index) {
    if (index < 0 || index >= labels.length) return;
    update(index);
    onSelect(index);
  }

  const arrow = button('', () => select(current + (current === labels.length - 1 ? -1 : 1)), 'lesson-tree-step-arrow');
  if (labels.length > 1) {
    for (const [index, text] of labels.entries()) {
      const item = el('li');
      item.append(button(text, () => {
        picker.open = false;
        select(index);
        number.focus();
      }));
      choices.append(item);
    }
    picker.append(number, choices);
    picker.addEventListener('focusout', event => {
      if (!picker.contains(event.relatedTarget)) picker.open = false;
    });
    controls.append(picker, arrow);
    controls.addEventListener('keydown', event => {
      if (event.key === 'Escape' && picker.open) {
        event.preventDefault();
        picker.open = false;
        number.focus();
      } else if (!picker.open && (event.key === 'ArrowLeft' || event.key === 'ArrowRight')) {
        event.preventDefault();
        select(current + (event.key === 'ArrowLeft' ? -1 : 1));
      }
    });
  } else {
    controls.append(number);
  }
  update(0);
  return { controls, title, update };
}

export function addTreeTrace(body, ui, label, steps, options = {}) {
  const { el, showDiagram } = ui;
  const figure = el('div', undefined, 'constituent-diagram');
  const canvas = el('div');
  const note = el('div', undefined, 'lesson-tree-observation');
  note.setAttribute('aria-live', 'polite');
  const caption = el('p');
  const guide = treeStepGuide(ui, label, steps.map(([text]) => text), show);
  note.append(guide.title, caption);
  function show(index) {
    const [, tree, focusId, explanation] = steps[index];
    showDiagram(canvas, tree, { focusId, highlightWords: true, wordBaseline: 3, ...options });
    caption.textContent = explanation;
  }
  figure.append(guide.controls, canvas, note);
  body.append(figure);
  show(0);
}
