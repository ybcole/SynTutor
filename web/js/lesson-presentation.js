import { foundationsBookContent, foundationsBookRecaps, foundationsRecapPoints } from './foundations-book-content.js';

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

export function addExplanationPractice(body, { el, button }, { key, id, explanation }) {
  const practice = el('div', undefined, 'lesson-pilot-transfer');
  const label = el('label', 'Your explanation');
  label.htmlFor = id;
  const editor = el('div', undefined, 'lesson-explanation-editor');
  const input = el('textarea');
  input.id = id;
  input.rows = 3;
  input.maxLength = 1200;
  try { input.value = localStorage.getItem(key) || ''; } catch { /* Practice remains available without storage. */ }

  const feedback = el('div', undefined, 'lesson-tree-observation lesson-explanation-result');
  feedback.id = `${id}-answer`;
  feedback.setAttribute('aria-live', 'polite');
  const reveal = button('Compare your explanation', () => {
    feedback.replaceChildren(el('h4', 'Explanation'), el('p', explanation));
    reveal.setAttribute('aria-expanded', 'true');
  });
  reveal.setAttribute('aria-controls', feedback.id);
  reveal.setAttribute('aria-expanded', 'false');
  reveal.disabled = !input.value.trim();
  input.addEventListener('input', () => {
    reveal.disabled = !input.value.trim();
    try { localStorage.setItem(key, input.value); } catch { /* Keep the current response in the field. */ }
  });
  const actions = el('div', undefined, 'lesson-explanation-actions');
  actions.append(reveal);
  editor.append(input, actions);
  practice.append(label, editor, feedback);
  body.append(practice);
}

export function addFoundationsBookCoverage(body, el, lessonId, sectionId) {
  const entries = foundationsBookContent[lessonId]?.[sectionId] ?? [];
  const recap = sectionId === 'recap' && foundationsBookRecaps[lessonId];
  if (recap) {
    const list = el('ul', undefined, 'constituent-recap');
    for (const point of foundationsRecapPoints[lessonId]) list.append(el('li', point));
    body.append(el('p', recap), el('h3', 'Key takeaways'), list);
  }
  if (!entries.length) return;

  const practice = el('section', undefined, 'lesson-sources lesson-practice-prose');
  practice.append(el('h3', 'Practice and feedback'));
  for (const [id, title, example, explanation, prompt, feedback, definition] of entries) {
    const heading = el('h3', title);
    heading.id = id.toLowerCase();
    const paragraphs = explanation.split('\n\n').map(text => el('p', text));
    body.append(heading);
    if (definition) body.append(el('p', definition));
    body.append(lessonExample(el, example), ...paragraphs);

    const exercise = el('div', undefined, 'lesson-practice-item');
    exercise.id = `${heading.id}-practice`;
    exercise.setAttribute('aria-label', title);
    exercise.append(
      el('h4', title),
      el('p', prompt, 'lesson-practice-prompt'),
      el('p', feedback, 'lesson-practice-feedback'),
    );
    practice.append(exercise);
  }
  return practice;
}

export function treeStepGuide({ el, button }, label, labels, onSelect) {
  const navigation = el('div', undefined, 'lesson-tree-navigation');
  const guide = el('div', undefined, 'lesson-tree-steps lesson-tree-guide');
  guide.setAttribute('role', 'group');
  guide.setAttribute('aria-label', label);
  const title = el('span', undefined, 'lesson-tree-step-title');
  const picker = el('details', undefined, 'lesson-tree-step-picker');
  const step = el(labels.length > 1 ? 'summary' : 'div', undefined, 'lesson-tree-step-label');
  const number = el('span', undefined, 'lesson-tree-step-number');
  number.setAttribute('aria-hidden', 'true');
  step.append(number, title);
  const choices = el('ol', undefined, 'lesson-tree-step-choices');
  let current = 0;

  function update(index) {
    current = index;
    const atEnd = index === labels.length - 1;
    number.textContent = String(index + 1);
    step.setAttribute('aria-label', `Step ${index + 1} of ${labels.length}: ${labels[index]}${labels.length > 1 ? ' · Choose a step' : ''}`);
    title.textContent = labels[index];
    arrow.textContent = atEnd ? '←' : '→';
    arrow.dataset.direction = atEnd ? 'previous' : 'next';
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
        step.focus();
      }));
      choices.append(item);
    }
    picker.append(step, choices);
    picker.addEventListener('focusout', event => {
      if (!picker.contains(event.relatedTarget)) picker.open = false;
    });
    guide.append(picker);
    navigation.append(guide, arrow);
    navigation.addEventListener('keydown', event => {
      if (event.key === 'Escape' && picker.open) {
        event.preventDefault();
        picker.open = false;
        step.focus();
      } else if (!picker.open && (event.key === 'ArrowLeft' || event.key === 'ArrowRight')) {
        event.preventDefault();
        select(current + (event.key === 'ArrowLeft' ? -1 : 1));
      }
    });
  } else {
    guide.append(step);
    navigation.append(guide);
  }
  update(0);
  return { controls: navigation, guide, arrow, update };
}

export function addTreeTrace(body, ui, label, steps, options = {}) {
  const { el, showDiagram } = ui;
  const figure = el('div', undefined, 'constituent-diagram');
  const canvas = el('div');
  const note = el('div', undefined, 'lesson-tree-observation');
  note.setAttribute('aria-live', 'polite');
  const caption = el('p');
  const guide = treeStepGuide(ui, label, steps.map(([text]) => text), show);
  note.append(caption);
  function show(index) {
    const [, tree, focusId, explanation] = steps[index];
    showDiagram(canvas, tree, { focusId, highlightWords: true, wordBaseline: 3, ...options, observation: note });
    caption.textContent = explanation;
  }
  figure.append(guide.controls, canvas);
  body.append(figure);
  show(0);
}
