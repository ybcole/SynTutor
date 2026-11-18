import { lessonKey } from './lesson-core.js';

export function renderFoundationCheck({ lesson, progress, kind, el, button, submit, userId, account }) {
  const assessment = lesson.revised_assessment;
  const questions = assessment[kind];
  const opening = kind === 'opening';
  const score = opening ? progress.opening_correct : progress.last_correct;
  const key = `syntutor:foundation-draft:${userId}:${lessonKey(lesson)}:${kind}`;
  const section = el('section', undefined, opening ? 'lesson-assessment constituent-pre-test' : 'lesson-assessment');
  const title = opening ? 'Check what you know' : 'Check what you learned';
  section.setAttribute('aria-label', title);
  let draft;
  function saveDraft(value) {
    draft = value;
    try {
      if (draft) sessionStorage.setItem(key, JSON.stringify(draft));
      else sessionStorage.removeItem(key);
    } catch { /* The check still works without draft storage. */ }
  }
  try {
    const saved = JSON.parse(sessionStorage.getItem(key));
    if (Number.isInteger(saved?.index) && questions[saved.index] && saved.answers &&
        questions.slice(0, saved.index).every(q => q.options.some(o => o.id === saved.answers[q.id]))) {
      draft = saved;
    }
  } catch { /* No saved draft. */ }
  function render(focus = false) {
    section.replaceChildren();
    if (opening) section.append(el('h3', title));
    if (score != null && (opening || !draft)) {
      const summaryWrap = el('div', undefined, 'lesson-assessment-summary');
      const summary = el('p', opening ? `Opening check complete. ${score} / ${questions.length} correct.`
        : `Last attempt ${score} / ${questions.length} · Best ${progress.best_correct} / ${questions.length}`, 'lesson-assessment-score');
      summary.setAttribute('role', 'status');
      summary.tabIndex = -1;
      summaryWrap.append(summary);
      if (!opening) {
        summaryWrap.append(el('p', `${progress.verified_xp} / 15 lesson XP${account ? ' verified' : ' on this device'}`, 'lesson-assessment-xp'));
      }
      section.append(summaryWrap);
      if (!opening) {
        if (!progress.completed_at) section.append(el('p', 'Visit the remaining required sections to complete the chapter.', 'lesson-guide-note'));
        const overview = el('details', undefined, 'lesson-sources lesson-overview-details');
        overview.open = true;
        overview.append(el('summary', 'Answers overview'));
        const list = el('ol', undefined, 'lesson-answers-list');
        for (const q of questions) {
          const selected = q.options.find(o => o.id === progress.last_answers?.[q.id]);
          const correct = q.options.find(o => o.id === q.answer);
          const isCorrect = selected?.id === correct.id;
          const row = el('li', undefined, `lesson-answer-item ${isCorrect ? 'is-correct' : 'is-review'}`);
          row.append(el('strong', q.prompt));
          if (selected) row.append(el('p', `Your answer: ${selected.text}. ${selected.feedback}`, 'lesson-answer-yours'));
          row.append(el('p', `Correct answer: ${correct.text}. ${correct.feedback}`, 'lesson-answer-key'));
          list.append(row);
        }
        overview.append(list);
        section.append(overview, button('Retake closing check', () => {
          saveDraft({ index: 0, answers: {} });
          render(true);
        }, 'lesson-primary'));
      }
      if (progress.pending) section.append(el('p', 'Saved on this device. Account sync is pending.', 'lesson-guide-note'));
      return;
    }
    const index = draft?.index ?? 0;
    const answers = draft?.answers || {};
    const q = questions[index];
    const item = el('div', undefined, 'lesson-question');
    const field = el('fieldset');
    item.append(field);
    const legend = el('legend', q.prompt);
    legend.tabIndex = -1;
    field.append(legend);
    const last = index === questions.length - 1;
    const next = button(last ? (opening ? 'Finish opening check' : 'Submit closing check') : 'Next question →', async () => {
      if (!last) {
        saveDraft({ index: index + 1, answers });
        render(true);
        return;
      }
      const event = { kind, attempt_id: crypto.randomUUID(), answers: { ...answers } };
      field.disabled = true;
      actions.querySelectorAll('button').forEach(control => { control.disabled = true; });
      try {
        await submit(event, () => saveDraft(null));
      } catch (error) {
        render(true);
        const status = el('p', error.message);
        status.setAttribute('role', 'alert');
        section.append(status);
      }
    }, 'lesson-primary');
    next.disabled = !q.options.some(o => o.id === answers[q.id]);
    for (const option of q.options) {
      const label = el('label', undefined, 'lesson-option');
      const input = el('input');
      input.type = 'radio';
      input.name = `foundation-${kind}-${q.id}`;
      input.value = option.id;
      input.checked = option.id === answers[q.id];
      input.addEventListener('change', () => {
        answers[q.id] = option.id;
        saveDraft({ index, answers });
        next.disabled = false;
      });
      label.append(input, el('span', option.text));
      field.append(label);
    }
    const actions = el('div', undefined, 'lesson-assessment-actions');
    if (index > 0) actions.append(button('← Previous question', () => {
      saveDraft({ index: index - 1, answers });
      render(true);
    }));
    actions.append(next);
    section.append(el('p', opening ? 'This check shows your score and gives no XP.'
      : 'Submit all answers to see your score and feedback. A higher best score can earn additional XP.'),
      el('p', `Question ${index + 1} of ${questions.length}`, 'lesson-assessment-position'), item, actions);
    if (focus) legend.focus();
  }
  render();
  return section;
}
