// Matrix Quiz data: the rule catalog (docs/matrix.md) plus a thin adapter over
// the generated question banks in ./quiz/.
//
// A quiz item is { bad, good, explanation }: `bad` is the incorrect sentence
// the learner must repair in the text box and `good` is the expected
// correction. Every rule has 40 items per difficulty tier; a run samples 5.

import {
  questionPool, hasQuiz, QUESTION_COUNT,
} from './quiz/index.js';

export { questionPool, hasQuiz };

// --------------------------------------------------------------------------
// Catalog — every rule in the matrix, grouped by section.
// --------------------------------------------------------------------------
export const MATRIX_SECTIONS = [
  {
    id: 1,
    title: 'Word forms',
    rules: [
      { id: '1.1', rule: 'Regular noun plurals', example: 'boxs', check: 'L' },
      { id: '1.2', rule: 'Irregular noun plurals', example: 'childs', check: 'L' },
      { id: '1.3', rule: "Possessive 's / s'", example: 'the boys toy', check: 'T' },
      { id: '1.4', rule: 'Verb endings (-s, -ed, -ing)', example: 'runing', check: 'L' },
      { id: '1.5', rule: 'Irregular past tense', example: 'goed', check: 'L' },
      { id: '1.6', rule: 'Irregular past participle', example: 'had went', check: 'L' },
      { id: '1.7', rule: 'Comparative/superlative formation', example: 'gooder, more tall', check: 'L' },
      { id: '1.8', rule: 'Adverb formation', example: 'happyly', check: 'L' },
      { id: '1.9', rule: 'Reflexive forms', example: 'hisself', check: 'L' },
      { id: '1.10', rule: 'Homophones (its/it\u2019s, their/there)', example: 'Its raining', check: 'T+L' },
      { id: '1.11', rule: 'Contractions', example: 'dont', check: 'L' },
      { id: '1.12', rule: 'Spelling', example: 'recieve', check: 'L' },
      { id: '1.13', rule: 'Numerals and measures', example: 'two hundreds', check: 'L' },
    ],
  },
  {
    id: 2,
    title: 'Agreement',
    rules: [
      { id: '2.1', rule: 'Subject-verb, simple', example: 'The boy go', check: 'T' },
      { id: '2.2', rule: 'Subject-verb across intervening phrase', example: 'The boy with the bags go', check: 'T' },
      { id: '2.3', rule: 'Coordinated subjects (and / or / nor)', example: 'Tom or Ann are', check: 'T' },
      { id: '2.4', rule: 'Existential there', example: 'There is books', check: 'T' },
      { id: '2.5', rule: 'Collective and notional nouns', example: 'The team are', check: 'C' },
      { id: '2.6', rule: 'Questions and inversion', example: 'Where is the books?', check: 'T' },
      { id: '2.7', rule: 'Relative clauses', example: 'the boys who plays', check: 'T' },
      { id: '2.8', rule: 'Indefinite pronouns', example: 'Everyone have', check: 'T+L' },
      { id: '2.9', rule: 'Quantified subjects', example: 'Each of the boys are', check: 'T+L' },
      { id: '2.10', rule: 'Determiner-noun number', example: 'these book', check: 'T' },
      { id: '2.11', rule: 'Quantifier-noun', example: 'less books, much books', check: 'T+L' },
      { id: '2.12', rule: 'Pronoun-antecedent', example: 'The girls lost her bag', check: 'C' },
      { id: '2.13', rule: 'Correlatives', example: 'Either he or I am', check: 'T' },
      { id: '2.14', rule: 'Reflexive-antecedent', example: 'She hurt himself', check: 'T' },
    ],
  },
  {
    id: 3,
    title: 'Articles and determiners',
    rules: [
      { id: '3.1', rule: 'a/an choice', example: 'a apple', check: 'L' },
      { id: '3.2', rule: 'Missing article', example: 'I saw dog', check: 'T+L' },
      { id: '3.3', rule: 'Unnecessary article', example: 'She plays the football', check: 'C' },
      { id: '3.4', rule: 'Definite vs indefinite', example: 'I saw the dog (first mention)', check: 'C' },
      { id: '3.5', rule: 'Stacked determiners', example: 'the my book', check: 'T' },
      { id: '3.6', rule: 'Determiner with no noun', example: 'the my', check: 'T' },
      { id: '3.7', rule: 'some/any', example: 'I don\u2019t have some money', check: 'T+L' },
      { id: '3.8', rule: 'each/every/all/whole/other/another', example: 'another books', check: 'T+L' },
    ],
  },
  {
    id: 4,
    title: 'Nouns',
    rules: [
      { id: '4.1', rule: 'Countable vs uncountable', example: 'informations, an advice', check: 'L' },
      { id: '4.2', rule: 'Noun as modifier (number)', example: 'a ten-years plan', check: 'T+L' },
      { id: '4.3', rule: 'Plural-only / singular -s nouns', example: 'a scissors, the news are', check: 'L' },
    ],
  },
  {
    id: 5,
    title: 'Pronouns',
    rules: [
      { id: '5.1', rule: 'Case, simple', example: 'Me go, between you and I', check: 'T' },
      { id: '5.2', rule: 'Case in coordination and comparison', example: 'Me and him went', check: 'T' },
      { id: '5.3', rule: 'Ambiguous reference', example: 'Tom told Jim he...', check: 'C' },
      { id: '5.4', rule: 'Relative pronoun choice', example: 'the man which', check: 'T+L' },
      { id: '5.5', rule: 'Dummy it/there', example: 'Is raining', check: 'T' },
      { id: '5.6', rule: 'Possessive pronoun vs determiner', example: 'This is my', check: 'T+L' },
      { id: '5.7', rule: 'Reflexive vs ordinary pronoun', example: 'Myself am happy', check: 'T' },
    ],
  },
  {
    id: 6,
    title: 'Verbs',
    rules: [
      { id: '6.1', rule: 'Auxiliary + verb form', example: 'She can goes', check: 'T' },
      { id: '6.2', rule: 'Finite main verb', example: 'She going to school', check: 'T' },
      { id: '6.3', rule: 'Missing verb / copula', example: 'She very happy', check: 'T' },
      { id: '6.4', rule: 'Passive formation', example: 'The house build', check: 'T' },
      { id: '6.5', rule: 'Intransitive passive', example: 'It was happened', check: 'L' },
      { id: '6.6', rule: 'Stative verbs in progressive', example: 'I am knowing', check: 'L' },
      { id: '6.7', rule: 'Tense consistency', example: 'He said he will come', check: 'C' },
      { id: '6.8', rule: 'Transitivity', example: 'discuss about', check: 'L' },
      { id: '6.9', rule: 'Gerund vs infinitive', example: 'enjoy to swim', check: 'L' },
      { id: '6.10', rule: 'to + base form', example: 'to goes', check: 'T' },
      { id: '6.11', rule: 'Phrasal verbs', example: 'pick up it', check: 'L' },
      { id: '6.12', rule: 'Modals and semi-modals', example: 'must to go', check: 'T+L' },
      { id: '6.13', rule: 'Question formation', example: 'Where you are going?', check: 'T' },
      { id: '6.14', rule: 'Negation', example: 'I don\u2019t have no money', check: 'T+L' },
      { id: '6.15', rule: 'Imperatives', example: 'Don\u2019t goes', check: 'T' },
      { id: '6.16', rule: 'Conditionals', example: 'If I will go', check: 'T' },
      { id: '6.17', rule: 'Subjunctive and wish', example: 'I wish I was', check: 'C' },
      { id: '6.18', rule: 'Reported speech', example: 'She said me', check: 'T+C' },
      { id: '6.19', rule: 'Causatives and perception verbs', example: 'made me to cry', check: 'T+L' },
      { id: '6.20', rule: 'Verb + clause patterns', example: 'suggest him to go', check: 'L' },
    ],
  },
  {
    id: 7,
    title: 'Adjectives and adverbs',
    rules: [
      { id: '7.1', rule: 'Adjective vs adverb', example: 'runs quick', check: 'T+L' },
      { id: '7.2', rule: 'Adjective order', example: 'red big car', check: 'L' },
      { id: '7.3', rule: 'Adverb placement', example: 'I like very much it', check: 'T+L' },
      { id: '7.4', rule: 'Participial adjectives', example: 'I am boring', check: 'L' },
      { id: '7.5', rule: 'Intensifiers and degree', example: 'enough big', check: 'T+L' },
      { id: '7.6', rule: 'Comparative structures', example: 'more taller', check: 'T+L' },
      { id: '7.7', rule: 'Modifier position', example: 'the car red', check: 'T' },
    ],
  },
  {
    id: 8,
    title: 'Prepositions',
    rules: [
      { id: '8.1', rule: 'Wrong preposition', example: 'depends in', check: 'C' },
      { id: '8.2', rule: 'Missing preposition', example: 'listen music', check: 'C' },
      { id: '8.3', rule: 'Unnecessary preposition', example: 'discuss about', check: 'L' },
      { id: '8.4', rule: 'Adjective + preposition', example: 'interested on', check: 'L' },
      { id: '8.5', rule: 'Time and place (in/on/at)', example: 'on 5 pm', check: 'L+C' },
      { id: '8.6', rule: 'Preposition + gerund', example: 'look forward to see', check: 'T+L' },
    ],
  },
  {
    id: 9,
    title: 'Sentence structure',
    rules: [
      { id: '9.1', rule: 'Fragment', example: 'Because I was late.', check: 'T' },
      { id: '9.2', rule: 'Missing subject', example: 'Went to school.', check: 'T' },
      { id: '9.3', rule: 'Run-on / fused sentence', example: 'I like tea she likes coffee', check: 'T+C' },
      { id: '9.4', rule: 'Comma splice', example: 'I came, I saw.', check: 'T' },
      { id: '9.5', rule: 'Double subject', example: 'My brother he...', check: 'T' },
      { id: '9.6', rule: 'Word order in statements', example: 'Yesterday went I', check: 'T' },
      { id: '9.7', rule: 'Missing or extra word', example: 'She is very the happy', check: 'C' },
      { id: '9.8', rule: 'Parallel structure', example: 'to run, swimming', check: 'T' },
      { id: '9.9', rule: 'Conjunction pairing', example: 'Although..., but...', check: 'L' },
      { id: '9.10', rule: 'Relative clause formation', example: 'the man who I saw him', check: 'T' },
      { id: '9.11', rule: 'Dangling / misplaced modifier', example: 'Walking home, the rain started', check: 'C' },
      { id: '9.12', rule: 'Redundancy', example: 'return back', check: 'L' },
      { id: '9.13', rule: 'Indirect question word order', example: 'I wonder where is he', check: 'T' },
      { id: '9.14', rule: 'Clause linking', example: 'because to see you', check: 'T' },
      { id: '9.15', rule: 'Object order', example: 'gave to me a book', check: 'T+L' },
    ],
  },
  {
    id: 10,
    title: 'Punctuation and orthography',
    rules: [
      { id: '10.1', rule: 'Sentence-initial capital', example: 'the boy runs', check: 'T' },
      { id: '10.2', rule: 'Proper nouns, "I", days, months', example: 'i am, monday', check: 'L' },
      { id: '10.3', rule: 'Terminal punctuation', example: 'missing period', check: 'T' },
      { id: '10.4', rule: 'Commas', example: 'series, introductory, clauses', check: 'T+C' },
      { id: '10.5', rule: 'Apostrophes', example: 'the 1990\u2019s', check: 'T' },
      { id: '10.6', rule: 'Quotation and dialogue', example: 'mismatched marks', check: 'T' },
      { id: '10.7', rule: 'Hyphens and dashes', example: 'a well known author', check: 'C' },
      { id: '10.8', rule: 'Colons and semicolons', example: 'misuse', check: 'T+C' },
      { id: '10.9', rule: 'Spacing and repeats', example: 'the the', check: 'T' },
      { id: '10.10', rule: 'Numbers, dates, abbreviations', example: 'inconsistent format', check: 'L' },
    ],
  },
  {
    id: 11,
    title: 'Meaning and usage',
    rules: [
      { id: '11.1', rule: 'Confusable words', example: 'affect/effect', check: 'C' },
      { id: '11.2', rule: 'Collocations', example: 'do a decision', check: 'C' },
      { id: '11.3', rule: 'Tense-time agreement', example: 'Yesterday I go', check: 'C' },
      { id: '11.4', rule: 'Selectional restrictions', example: 'The book eats', check: 'C' },
      { id: '11.5', rule: 'Structural ambiguity', example: 'PP-attachment', check: 'C' },
      { id: '11.6', rule: 'Register', example: 'slang in formal writing', check: 'C' },
      { id: '11.7', rule: 'L1 interference / false friends', example: 'I am agree', check: 'C' },
      { id: '11.8', rule: 'Connector misuse', example: 'I was tired, however I slept', check: 'C' },
    ],
  },
];

export const DIFFICULTY = {
  easy: { label: 'Easy', count: 5, total: QUESTION_COUNT },
  medium: { label: 'Medium', count: 5, total: QUESTION_COUNT },
  hard: { label: 'Hard', count: 5, total: QUESTION_COUNT },
};

export function ruleInfo(ruleId) {
  for (const section of MATRIX_SECTIONS) {
    const found = section.rules.find((r) => r.id === ruleId);
    if (found) return { ...found, section: section.title, sectionId: section.id };
  }
  return null;
}
