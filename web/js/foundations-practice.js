import { lessonExample } from './lesson-presentation.js';

export function addWordPractice(body, { el, button }, steps) {
  const section = el('section', undefined, 'lesson-transfer');
  const heading = el('h3', 'Try it yourself');
  const progress = el('p');
  const prompt = el('p');
  const instructions = el('p');
  const choices = el('div', undefined, 'constituent-controls lesson-transfer-choices');
  choices.setAttribute('role', 'group');
  const status = el('p', undefined, 'lesson-feedback');
  status.setAttribute('role', 'status');
  let index = 0;
  let start = null;
  let end = null;
  let checked = false;
  const check = button('Check selection', () => {
    const { expected, success, hint, gap } = steps[index];
    const selection = gap ? [start] : [Math.min(start, end ?? start), Math.max(start, end ?? start)];
    checked = true;
    const correct = selection.every((value, i) => value === expected[i]);
    status.className = `lesson-feedback ${correct ? 'correct' : 'retry'}`;
    status.textContent = correct ? success : hint;
    next.hidden = !correct || index === steps.length - 1;
  });
  const next = button('Next part', () => {
    index++;
    renderStep();
    prompt.focus();
  });
  prompt.tabIndex = -1;
  section.append(heading, progress, prompt, instructions, choices, check, next, status);
  body.append(section);

  function renderStep() {
    const { sentence, question, gap } = steps[index];
    const words = sentence.split(' ');
    start = end = null;
    checked = false;
    check.disabled = true;
    next.hidden = true;
    progress.textContent = steps.length > 1 ? `Part ${index + 1} of ${steps.length}` : '';
    progress.hidden = steps.length === 1;
    prompt.textContent = question;
    instructions.textContent = gap
      ? 'Select the position where the missing word or phrase belongs.'
      : 'Select the first and last words of the group. For one word, select it once.';
    choices.setAttribute('aria-label', question);
    status.textContent = '';
    const controls = [];
    function choose(position) {
      if (gap || checked || start === null || end !== null) {
        start = position;
        end = null;
      } else {
        end = position;
      }
      for (const [i, control] of controls.entries()) {
        const selected = i >= Math.min(start, end ?? start) && i <= Math.max(start, end ?? start);
        control.setAttribute('aria-pressed', String(selected));
      }
      checked = false;
      check.disabled = false;
      next.hidden = true;
      status.textContent = '';
    }
    if (gap) {
      const items = [];
      for (let i = 0; i <= words.length; i++) {
        const control = button('│', () => choose(i));
        const position = i === 0 ? `Before ${words[0]}`
          : i === words.length ? `After ${words.at(-1)}`
            : `Between ${words[i - 1]} and ${words[i]}`;
        control.setAttribute('aria-label', position);
        controls.push(control);
        items.push(control);
        if (i < words.length) items.push(el('span', words[i]));
      }
      choices.replaceChildren(...items);
    } else {
      controls.push(...words.map((word, i) => {
        const control = button(word, () => choose(i));
        control.setAttribute('aria-label', `${word}, word ${i + 1}`);
        return control;
      }));
      choices.replaceChildren(...controls);
    }
    for (const control of controls) control.setAttribute('aria-pressed', 'false');
  }
  renderStep();
}

export function addCombinationPractice(body, { el, button }, basic, incomplete, { showDerivation = false } = {}) {
  const section = el('section', undefined, 'lesson-transfer');
  const heading = el('h3', 'Try it yourself');
  const prompt = el('p', 'Join two complete sentences. Try the unfinished input to see why it fails.');
  const inputs = [el('select'), el('select')];
  const labels = inputs.map((input, i) => {
    const label = el('label', i === 0 ? 'First input' : 'Second input');
    label.append(input);
    return label;
  });
  const status = el('div', undefined, 'lesson-feedback');
  status.setAttribute('role', 'status');
  let result = '';
  let derivation = '';
  let reuse = false;
  const check = button('Apply the rule', () => {
    const parts = inputs.map(input => input.value);
    if (parts.some(part => !part)) {
      feedback('Choose both inputs first.', false);
      return;
    }
    if (parts.includes(incomplete)) {
      feedback('That input ends with “and”. It needs a complete sentence after it.', false);
      return;
    }
    if (reuse && parts.filter(part => part === result).length !== 1) {
      feedback('Use the earlier result on one side and a basic sentence on the other.', false);
      return;
    }
    const joined = parts.map(part => `[${part}]`).join(' and ');
    const structure = `[S ${parts.map(part => reuse && part === result ? derivation : `[S ${part}]`).join(' and ')}]`;
    if (reuse) {
      feedback('The same rule joined a complete earlier result with another sentence.', true, showDerivation ? structure : `${joined}.`);
    } else {
      result = parts.join(' and ');
      derivation = structure;
      feedback('Both inputs are complete, so their combination can serve as a new input.', true, showDerivation ? structure : `${joined}.`);
      next.hidden = false;
    }
  });
  const next = button('Use this result again', () => {
    reuse = true;
    prompt.textContent = 'Use the result you just made on one side and a basic sentence on the other.';
    const options = [...basic, incomplete, result];
    fillInputs(options);
    inputs[0].focus();
  });
  const restart = button('Start again', () => {
    reuse = false;
    result = '';
    derivation = '';
    prompt.textContent = 'Join two complete sentences. Try the unfinished input to see why it fails.';
    fillInputs([...basic, incomplete]);
    status.textContent = '';
    inputs[0].focus();
  });
  const actions = el('div', undefined, 'constituent-controls');
  actions.append(check, next, restart);
  const fields = el('div', undefined, 'lesson-combination-inputs');
  fields.append(...labels);
  section.append(heading, prompt, fields, actions, status);
  body.append(section);
  function feedback(message, correct, example) {
    status.className = `lesson-feedback ${correct ? 'correct' : 'retry'}`;
    status.replaceChildren();
    if (example) status.append(lessonExample(el, example));
    status.append(message);
    next.hidden = true;
  }
  function fillInputs(options) {
    for (const input of inputs) {
      const placeholder = el('option', 'Choose a sentence');
      placeholder.value = '';
      input.replaceChildren(placeholder, ...options.map(value => el('option', value)));
    }
    next.hidden = true;
    restart.hidden = !reuse;
  }
  inputs.forEach(input => input.addEventListener('change', () => {
    next.hidden = true;
    status.textContent = '';
  }));
  fillInputs([...basic, incomplete]);
}
