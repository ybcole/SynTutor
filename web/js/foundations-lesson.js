import { setTreeStepLabel } from './lesson-presentation.js';

export function addWorkedExample(body, ui, labels, {
  highlightWords = false, captions, comparison, extraSteps = [], tracePath = false,
} = {}) {
  const { el, button, lesson, showWorkedTree, showDiagram } = ui;
  const worked = lesson.worked_example;
  const sentence = el('p', worked.sentence, 'lesson-example-sentence');
  if (!worked.tree) {
    const steps = el('ol');
    for (const step of worked.steps) steps.append(el('li', step.text));
    body.append(sentence, steps);
    return;
  }

  const controls = el('div', undefined, 'constituent-controls lesson-tree-steps');
  controls.setAttribute('role', 'group');
  controls.setAttribute('aria-label', 'Explore the worked tree');
  const diagram = el('div', undefined, 'constituent-diagram');
  const observation = el('div', undefined, 'lesson-tree-observation');
  const caption = el('p', undefined, 'constituent-caption');
  caption.setAttribute('aria-live', 'polite');
  observation.append(caption);
  const steps = worked.steps.map((step, index) => ({
    id: step.focus_node_id, label: labels[index], caption: captions?.[index] ?? step.text,
  })).filter(step => step.label).concat(extraSteps);
  const choices = steps.map((step, index) => {
    const control = button(step.label, () => select(index));
    setTreeStepLabel(control, el, step.label, index + 1);
    return control;
  });

  function describe(index, position) {
    choices.forEach((choice, i) => choice.setAttribute('aria-pressed', String(i === index)));
    if (index !== -1) {
      caption.textContent = steps[index].caption;
    } else if (position) {
      const { node, parent } = position;
      const label = name => ({ 'S-bar': 'S′', 'S-dbar': 'S″' })[name] ?? name;
      if (node.gap) {
        caption.textContent = `The dot under ${label(parent?.label)} marks a position with no spoken word.`;
      } else {
        const name = node.word ? `“${node.word}”` : label(node.label) || 'This node';
        caption.textContent = parent?.label
          ? `${name} is directly under ${label(parent.label)}.`
          : `${name} is at the top of this tree.`;
      }
    } else {
      caption.textContent = '';
    }
  }

  function select(index) {
    describe(index);
    showWorkedTree(diagram, steps[index].id, {
      highlightWords,
      tracePath,
      observation,
      onSelect: (nodeId, position) => describe(steps.findIndex(step => step.id === nodeId), position),
    });
  }

  if (comparison) {
    const switcher = el('div', undefined, 'constituent-controls');
    switcher.setAttribute('role', 'group');
    switcher.setAttribute('aria-label', 'Compare worked structures');
    const primary = button(comparison.original, () => show(false));
    const alternate = button(comparison.alternate, () => show(true));
    function show(compare) {
      primary.setAttribute('aria-pressed', String(!compare));
      alternate.setAttribute('aria-pressed', String(compare));
      controls.hidden = compare;
      sentence.textContent = compare ? comparison.tree.sentence : worked.sentence;
      if (compare) {
        observation.querySelector('.constituent-selection')?.remove();
        showDiagram(diagram, comparison.tree, {
          focusId: comparison.focusId, highlightWords: true, stackFeatures: true,
        }).after(observation);
        caption.textContent = comparison.caption;
      } else {
        select(0);
      }
    }
    primary.setAttribute('aria-pressed', 'true');
    alternate.setAttribute('aria-pressed', 'false');
    switcher.append(primary, alternate);
    body.append(switcher);
  }

  controls.append(...choices);
  body.append(sentence, controls, diagram);
  select(0);
}
