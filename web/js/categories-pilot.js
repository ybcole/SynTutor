import { addIntroExample, lessonExample, addTreeTrace } from './lesson-presentation.js';

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
    ['Lexical category', 'The kind of word, such as noun, adjective, adverb, or preposition.'],
    ['Phrasal category', 'The kind of phrase. In a phrase with a head, the head gives the phrase its category.'],
    ['Degree word', 'A word like “very” or “quite” that tells how much a description applies.'],
    ['Coordination', 'Joining two or more parts, often with “and” or “or”. Each part that joins is a conjunct.'],
  ],
  teach(body, _page, ui) {
    const { el, button, lesson, section } = ui;
    const p = text => body.append(el('p', text));
    const heading = text => body.append(el('h3', text));
    const example = text => body.append(lessonExample(el, text));

    if (section.id === 'introduction') {
      p('Chapter 2 used NP and VP to name kinds of phrases. The kind of phrase is its phrasal category. The kind of word, such as noun, is its lexical category. Sometimes one word can form a whole phrase.');
      addIntroExample(body, el, 'The brackets show the whole subject group.',
        '[The lamps] glowed.',
        '“Lamps” is a noun. It heads the noun phrase (NP) “the lamps”. The whole NP does the job of subject.');
      heading('What you’ll see in this chapter');
      const list = el('ul');
      for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
      body.append(list);
    }
    if (section.id === 'concepts') {
      p('“Lamp” and “lamps” are both nouns. Many nouns have a plural form that means more than one. In the next example, “lamps” is the head. This noun makes the whole group a noun phrase (NP).');
      example('The paper lamps flickered.');
      p('In “They flickered”, the pronoun “they” stands in for a group. Select all the words it replaces.');
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
      p('A noun can make a whole NP. In the first tree, “lamps” does this by itself. The name “Mina” also makes a whole NP. A pronoun such as “they” can fill that same spot.');
      addTreeTrace(body, ui, 'Compare two one-word noun phrases', [
        ['Trace the name', { sentence: 'Mina', root: phrase('name-np', 'NP', phrase('name', 'name', word('Mina'))) },
          'name-np', '“Mina” is a name. The NP above it represents the full phrase that functions as the subject.'],
        ['Trace the pronoun', { sentence: 'they', root: phrase('pronoun-np', 'NP', phrase('pronoun', 'pronoun', word('they'))) },
          'pronoun-np', 'The word is a pronoun. It also forms a whole NP and can take the place of “the paper lamps”.'],
      ]);
    }
    if (section.id === 'worked-example') {
      p('An adjective phrase (AP) has an adjective as its head. An adverb phrase (AdvP) has an adverb as its head. In the next example, “visible” describes the sign. “Quite clearly” tells how clearly someone could see it.');
      example('The sign was [quite clearly visible].');
      p('“Quite” is a degree word. It tells how much. Follow its branch to find the word it modifies.');
      addTreeTrace(body, ui, 'Trace the adjective and adverb phrases', [
        ['Find the adjective', description, 'adjective', '“Visible” is the head of the whole AP.'],
        ['Read the adverb phrase', description, 'modifier', '“Clearly” heads “quite clearly”. The degree word “quite” modifies “clearly”. Together they form an AdvP that modifies “visible”.'],
        ['Compare a direct modifier', simpleDescription, 'simple-degree', 'In “very visible”, “very” modifies the adjective directly. The whole group is still an AP.'],
      ]);
      p('“The sign was visible” also works. Here the adjective alone is the whole AP.');
    }
    if (section.id === 'prepositions-and-coordination') {
      p('A prepositional phrase (PP) has a preposition as its head. In “beside the bench”, “beside” tells how the place relates to the bench. The NP “the bench” is its complement. It names the landmark.');
      example('The puppy slept [beside the bench and near the heater].');
      p('Joining parts with a word like “and” is called coordination. Each part joined is a conjunct. Here, both conjuncts are PPs with their own head and landmark. Together they form a larger PP.');
      addTreeTrace(body, ui, 'Trace the two locations and their replacement', [
        ['Trace the first PP', locations, 'first-location', '“Beside” heads the first PP. “The bench” is its NP complement.'],
        ['Trace the second PP', locations, 'second-location', '“Near” heads the second PP. “The heater” is its NP complement.'],
        ['Read the whole coordination', locations, 'locations', 'Both PPs and the word “and” sit directly under the outer PP.'],
        ['Compare “there”', there, 'there-phrase', '“The puppy slept there” uses “there” for the whole location. In this analysis, locative “there” is a preposition that forms a PP by itself.'],
      ]);
    }
    if (section.id === 'application') {
      example('The cat hid behind the chair and under the blanket.');
      p('Write the two groups that “and” joins. Then name the category of the whole location group.');
      const hint = el('details', undefined, 'lesson-sources');
      hint.append(el('summary', 'Hint'), el('p', 'Find each preposition. Put the words that name its landmark in the same group.'));
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
      p('Find all the words in a phrase before you name its category. Try a pronoun to check which words go together in an NP. An NP can also be one word, as “Mina” is in “Mina waited”.');
      p('Ask what each dependent goes with. In “quite clearly visible”, the AdvP “quite clearly” goes with “visible”. Inside the AdvP, “quite” goes with “clearly”.');
      p('When you see “and”, find the whole group on each side. Each group is a conjunct. Here, each PP has its own preposition and landmark. The joined group is also a PP.');
    }
  },
};
