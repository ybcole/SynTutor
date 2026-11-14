import { addIntroExample, lessonExample, setTreeStepLabel } from './lesson-presentation.js';

function phrase(id, label, ...children) { return { id, label, children }; }
function word(text) { return { word: text }; }
function landmark(id, text) { return { id, label: 'NP', triangle: true, words: text.split(' ') }; }

const degree = phrase('degree', 'DEG', word('quite'));
const modifier = phrase('modifier', 'AdvP', degree, phrase('adverb', 'Adv', word('clearly')));
const adjective = phrase('adjective', 'A', word('visible'));
const description = { sentence: 'quite clearly visible', root: phrase('description', 'AP', modifier, adjective) };
const simpleDescription = { sentence: 'very visible', root: phrase('simple', 'AP',
  phrase('simple-degree', 'DEG', word('very')), adjective) };
const locations = {
  sentence: 'beside the bench and near the heater',
  root: phrase('locations', 'PP',
    phrase('first-location', 'PP', phrase('first-head', 'P', word('beside')), landmark('bench', 'the bench')),
    word('and'),
    phrase('second-location', 'PP', phrase('second-head', 'P', word('near')), landmark('heater', 'the heater'))),
};
const there = { sentence: 'there', root: phrase('there-phrase', 'PP', phrase('there-head', 'P', word('there'))) };

function trace(body, { el, button, showDiagram }, label, steps) {
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

export const categoriesPilot = {
  description: 'Distinguish words from the phrases they head, then trace noun, adjective, adverb and prepositional phrases. See how two prepositional phrases can join to form a larger one.',
  references: [
    'Chapter 3, printed pp. 47–53, figures [7], [14], [18] · Nouns and noun phrases',
    'Printed pp. 54–56 and p. 62, diagrams (a–b) · Adjectives, adverbs and degree',
    'Printed pp. 56–57, figures [19a–b] · Two prepositional phrase patterns',
    'Printed pp. 57–62, figure [41b] · Co-ordination of prepositional phrases',
  ],
  sections: [
    { id: 'introduction', title: 'Words and phrases have categories' },
    { id: 'concepts', title: 'Find the noun and the whole phrase', notationLabels: ['NP', 'name', 'pronoun'] },
    { id: 'worked-example', title: 'Read an AP and its adverb phrase', notationLabels: ['AP', 'A', 'AdvP', 'Adv', 'DEG'] },
    { id: 'prepositions-and-coordination', title: 'Join two prepositional phrases', notationLabels: ['PP', 'P', 'NP', '△'] },
    { id: 'application', title: 'Try a new coordination' },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Lexical category', 'The grammatical class of a word, such as noun, adjective, adverb or preposition.'],
    ['Phrasal category', 'The grammatical class of a whole group. In an ordinary headed phrase, the head determines the class.'],
    ['Degree word', 'A word such as “very” or “quite” that indicates how strongly a quality applies.'],
    ['Coordination', 'The joining of two or more units, often with a word such as “and” or “or”. Each joined unit is a conjunct.'],
  ],
  teach(body, _page, ui) {
    const { el, button, lesson, section } = ui;
    const p = text => body.append(el('p', text));
    const heading = text => body.append(el('h3', text));
    const example = text => body.append(lessonExample(el, text));

    if (section.id === 'introduction') {
      p('Chapter 2 used labels such as NP and VP for whole groups. A phrasal category is the class of a whole phrase. A lexical category is the class of an individual word, such as noun. One word can sometimes be enough to form a phrase.');
      addIntroExample(body, el, 'The brackets show the whole subject group.',
        '[The lamps] glowed.',
        '“Lamps” is a noun. “The lamps” is a noun phrase (NP) headed by that noun, and it functions as the subject.');
      heading('What you’ll see in this chapter');
      const list = el('ul');
      for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
      body.append(list);
    }
    if (section.id === 'concepts') {
      p('Nouns are a word class. The forms “lamp” and “lamps” show one clue: many nouns have a plural form. In the next statement, “lamps” is the head. It gives the whole group its category as an NP.');
      example('The paper lamps flickered.');
      p('Compare “They flickered”. Select the words that the pronoun replaces.');
      const choices = el('div', undefined, 'lesson-tree-steps');
      choices.setAttribute('role', 'group');
      choices.setAttribute('aria-label', 'Choose the replaced span');
      const feedback = el('div', undefined, 'lesson-tree-observation');
      const message = el('p');
      feedback.setAttribute('aria-live', 'polite');
      feedback.append(message);
      for (const [text, response] of [
        ['lamps', '“They” replaces the full subject group. Include “the paper”.'],
        ['The paper lamps', 'Exactly. “They” fills the same position as the whole NP.'],
        ['The paper lamps flickered', '“Flickered” stays in the new sentence. Replace only the subject.'],
      ]) {
        const choice = button(text, () => {
          Array.from(choices.children).forEach(control => control.setAttribute('aria-pressed', String(control === choice)));
          message.textContent = response;
        });
        choice.setAttribute('aria-pressed', 'false');
        choices.append(choice);
      }
      body.append(choices, feedback);
      example('Lamps flickered. Mina waited.');
      p('In the first statement, “lamps” is a noun that forms the whole subject NP. In the second, “Mina” is a name that forms an NP by itself. Compare the name with the pronoun in “They flickered”.');
      trace(body, ui, 'Compare two one-word noun phrases', [
        ['Trace the name', { sentence: 'Mina', root: phrase('name-np', 'NP', phrase('name', 'name', word('Mina'))) },
          'name-np', '“Mina” is a name. The NP above it represents the full phrase that functions as the subject.'],
        ['Trace the pronoun', { sentence: 'they', root: phrase('pronoun-np', 'NP', phrase('pronoun', 'pronoun', word('they'))) },
          'pronoun-np', 'The word is a pronoun. It also forms a whole NP and can take the place of “the paper lamps”.'],
      ]);
    }
    if (section.id === 'worked-example') {
      p('An adjective phrase (AP) is headed by an adjective. An adverb phrase (AdvP) is headed by an adverb. In the following example, “visible” supplies the description and “quite clearly” tells how clearly the sign could be seen.');
      example('The sign was [quite clearly visible].');
      p('“Quite” is a degree word. Follow its branch to see which word it modifies before comparing the shorter description.');
      trace(body, ui, 'Trace the adjective and adverb phrases', [
        ['Find the adjective', description, 'adjective', '“Visible” is the head of the whole AP.'],
        ['Read the adverb phrase', description, 'modifier', '“Clearly” heads “quite clearly”. The degree word “quite” modifies “clearly”. Together they form an AdvP that modifies “visible”.'],
        ['Compare a direct modifier', simpleDescription, 'simple-degree', 'In “very visible”, “very” modifies the adjective directly. The whole group is still an AP.'],
      ]);
      p('“The sign was visible” also works. Here the adjective alone is the whole AP.');
    }
    if (section.id === 'prepositions-and-coordination') {
      p('A prepositional phrase (PP) is headed by a preposition. In “beside the bench”, “beside” expresses the spatial relation and its NP complement supplies the landmark.');
      example('The puppy slept [beside the bench and near the heater].');
      p('Coordination joins two or more units. Here “and” joins two PPs, called conjuncts. Each has its own head and landmark. In this analysis the coordinate group is also a PP.');
      trace(body, ui, 'Trace the two locations and their replacement', [
        ['Trace the first PP', locations, 'first-location', '“Beside” heads the first PP. “The bench” is its NP complement.'],
        ['Trace the second PP', locations, 'second-location', '“Near” heads the second PP. “The heater” is its NP complement.'],
        ['Read the whole coordination', locations, 'locations', 'Both PPs and the word “and” sit directly under the outer PP.'],
        ['Compare “there”', there, 'there-phrase', '“The puppy slept there” uses “there” for the whole location. In this analysis, locative “there” is a preposition that forms a PP by itself.'],
      ]);
    }
    if (section.id === 'application') {
      example('The cat hid behind the chair and under the blanket.');
      p('Write the two groups joined by “and” and give the category of the whole location.');
      const hint = el('details', undefined, 'lesson-sources');
      hint.append(el('summary', 'Hint'), el('p', 'Find each preposition and include its landmark in the same group.'));
      body.append(hint);
      const key = `syntutor:lesson-transfer:${ui.userId}:br-03@${lesson.content_version}:application`;
      const label = el('label', 'Your explanation');
      label.htmlFor = 'chapter-three-transfer';
      const input = el('textarea');
      input.id = label.htmlFor;
      input.rows = 3;
      input.maxLength = 1200;
      try { input.value = localStorage.getItem(key) || ''; } catch { /* The exercise still works. */ }
      const feedback = el('div', undefined, 'lesson-tree-observation');
      const answer = el('p');
      feedback.setAttribute('aria-live', 'polite');
      feedback.append(answer);
      const reveal = button('Compare your explanation', () => {
        answer.textContent = '“Behind the chair” and “under the blanket” are the two PPs. Each includes a preposition and its landmark. Together with “and”, they form one coordinate PP.';
      });
      reveal.disabled = !input.value.trim();
      input.addEventListener('input', () => {
        reveal.disabled = !input.value.trim();
        try { localStorage.setItem(key, input.value); } catch { /* Keep the current response in the field. */ }
      });
      const practice = el('div', undefined, 'lesson-pilot-transfer');
      practice.append(label, input, reveal, feedback);
      body.append(practice);
    }
    if (section.id === 'recap') {
      p('Identify the complete phrase before naming its category. A pronoun can help find the span of an NP. A phrase can consist of just one word, as in “Mina waited”.');
      p('Find what each dependent goes with. In “quite clearly visible”, the AdvP goes with the adjective, and “quite” goes with the adverb inside that AdvP.');
      p('When you see “and”, find the full span of each conjunct. In the location examples, each PP has its own preposition and landmark. The whole coordinate group is also a PP.');
    }
  },
};
