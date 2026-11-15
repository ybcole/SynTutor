import { addExplanationPractice, addIntroExample, lessonExample, addTreeTrace } from './lesson-presentation.js';

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
    { id: 'introduction', title: 'Introduction to lexical and phrasal categories' },
    { id: 'concepts', title: 'Nouns, noun phrases and lexical categories', notationLabels: ['NP', 'name', 'pronoun'] },
    { id: 'worked-example', title: 'Adjectives, adverbs, APs and AdvPs', notationLabels: ['AP', 'A', 'AdvP', 'Adv', 'DEG'] },
    { id: 'prepositions-and-coordination', title: 'Prepositions, prepositional phrases and coordination', notationLabels: ['PP', 'P', 'NP', '△'] },
    { id: 'application', title: 'Category and coordination exercises' },
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
      p('Chapter 2 looked at the jobs phrases do in a sentence. Now look inside a phrase. A grammatical category tells you what kind of word or phrase something is. The head is the word that gives a phrase its category. In this chapter, you’ll find heads and use them to name whole phrases.');
      addIntroExample(body, el, 'In the example below, the brackets mark the whole subject. Look for the noun inside them that tells you what was glowing.',
        '[The lamps] glowed.',
        '“Lamps” is the main word, or head. Its lexical category, or word type, is noun (N). The phrasal category, or phrase type, of “the lamps” is noun phrase (NP). Its job in this sentence is subject.');
      heading('What you’ll learn in this chapter');
      const list = el('ul');
      for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
      body.append(list);
    }
    if (section.id === 'concepts') {
      p('A noun is a word that can head a noun phrase. Count nouns such as “lamp” often have a plural form that means more than one. In the next example, “lamps” is the head. This noun makes the whole group a noun phrase (NP).');
      example('The paper lamps flickered.');
      p('In “They flickered”, the pronoun “they” stands in for a group from the example.');
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
      const exercise = el('section', undefined, 'lesson-practice-panel');
      exercise.append(el('p', 'Pick the words that “they” replaces.'), choices, feedback);
      body.append(exercise);
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
      p('An adjective phrase (AP) has an adjective as its head. An adverb phrase (AdvP) has an adverb as its head. The tree uses A and Adv for the head words themselves. In the next example, “visible” describes the sign. “Quite clearly” tells how clearly someone could see it.');
      example('The sign was [quite clearly visible].');
      p('A degree word tells how much or how strongly a description applies. In this example, DEG labels “quite”. Follow its branch to find the word it modifies.');
      p('Read “quite clearly visible” in two passes. First, “quite” tells how clearly, so group it with “clearly” inside AdvP. Next, the whole AdvP modifies “visible”. “Visible” heads the AP, even though the AP contains an adverb phrase of its own.');
      addTreeTrace(body, ui, 'Trace the adjective and adverb phrases', [
        ['Find the adjective', description, 'adjective', '“Visible” is the head of the whole AP.'],
        ['Read the adverb phrase', description, 'modifier', '“Clearly” heads “quite clearly”. The degree word “quite” modifies “clearly”. Together they form an AdvP that modifies “visible”.'],
        ['Compare a direct modifier', simpleDescription, 'simple-degree', 'In “very visible”, “very” modifies the adjective directly. The whole group is still an AP.'],
      ]);
      p('“The sign was visible” also works. Here the adjective alone is the whole AP.');
    }
    if (section.id === 'prepositions-and-coordination') {
      p('A prepositional phrase (PP) has a preposition as its head. The tree labels the preposition P. In the first location of the example below, “beside” tells how the place relates to the bench. The NP “the bench” is its complement. It names the landmark.');
      example('The puppy slept [beside the bench and near the heater].');
      p('Joining parts with a word like “and” is called coordination. Each part joined is a conjunct. Here, both conjuncts are PPs with their own head and landmark. Together they form a larger PP.');
      p('Try covering the shared words in “above and beside the bench”. The coordinator joins the two prepositions, and “the bench” is their shared complement. Now read “above the table and beside the bench”. Each preposition has its own complement, so the coordinator joins two complete PPs.');
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
      body.append(el('p', 'Find each preposition. Put the words that name its landmark in the same group.'));
      const key = `syntutor:lesson-transfer:${ui.userId}:br-03@${lesson.content_version}:application`;
      addExplanationPractice(body, ui, {
        key, id: 'chapter-three-transfer',
        explanation: '“Behind the chair” and “under the blanket” are the two PPs. Each includes a preposition and its landmark. Together with “and”, they form one coordinate PP.',
      });
    }
    if (section.id === 'recap') {
      p('Find all the words in a phrase before you name its category. Try a pronoun to check which words go together in an NP. An NP can also be one word, as “Mina” is in “Mina waited”.');
      p('Ask what each dependent goes with. In “quite clearly visible”, the AdvP “quite clearly” goes with “visible”. Inside the AdvP, “quite” goes with “clearly”.');
      p('When you see “and”, find the whole group on each side. Each group is a conjunct. Here, each PP has its own preposition and landmark. The joined group is also a PP.');
    }
  },
};
