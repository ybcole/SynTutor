// Matrix Quiz data: the rule catalog (docs/matrix.md) plus, for each rule that
// has quizzes, a builder that produces randomised multiple-choice questions.
//
// A question is: { sentence, prompt, options:[...], answer:<index>, explanation }
// Every rule builds three pools (easy / medium / hard) so a run feels fresh.

const shuffle = (arr) => {
  const out = [...arr];
  for (let i = out.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
};

const unique = (arr) => [...new Set(arr)];

const INDEX_OPTIONS = ['A', 'B', 'C', 'D'];

function makeQ(sentence, prompt, correct, wrongs, explanation) {
  const pool = unique((wrongs || []).filter((w) => w && w !== correct));
  const picks = shuffle(pool).slice(0, 3);
  const pads = [
    `${correct}s`, `${correct}es`, `${correct}ed`, `${correct}d`,
    `${correct}ing`, `more ${correct}`, `most ${correct}`,
  ];
  for (const pad of shuffle(pads)) {
    if (picks.length >= 3) break;
    if (pad !== correct && !picks.includes(pad)) picks.push(pad);
  }
  const options = shuffle([correct, ...picks]);
  return {
    sentence,
    prompt,
    options,
    answer: options.indexOf(correct),
    explanation,
  };
}

// --------------------------------------------------------------------------
// Catalog — every rule in the matrix, grouped by section.
// `cap` marks rules that currently have question banks.
// --------------------------------------------------------------------------
export const MATRIX_SECTIONS = [
  {
    id: 1,
    title: 'Word forms',
    rules: [
      { id: '1.1', rule: 'Regular noun plurals', example: 'boxs', check: 'L', cap: true },
      { id: '1.2', rule: 'Irregular noun plurals', example: 'childs', check: 'L', cap: true },
      { id: '1.3', rule: "Possessive 's / s'", example: 'the boys toy', check: 'T', cap: true },
      { id: '1.4', rule: 'Verb endings (-s, -ed, -ing)', example: 'runing', check: 'L', cap: true },
      { id: '1.5', rule: 'Irregular past tense', example: 'goed', check: 'L', cap: true },
      { id: '1.6', rule: 'Irregular past participle', example: 'had went', check: 'L', cap: true },
      { id: '1.7', rule: 'Comparative/superlative formation', example: 'gooder, more tall', check: 'L', cap: true },
      { id: '1.8', rule: 'Adverb formation', example: 'happyly', check: 'L', cap: true },
      { id: '1.9', rule: 'Reflexive forms', example: 'hisself', check: 'L', cap: true },
      { id: '1.10', rule: 'Homophones (its/it\u2019s, their/there)', example: 'Its raining', check: 'T+L', cap: true },
      { id: '1.11', rule: 'Contractions', example: 'dont', check: 'L', cap: true },
      { id: '1.12', rule: 'Spelling', example: 'recieve', check: 'L', cap: true },
      { id: '1.13', rule: 'Numerals and measures', example: 'two hundreds', check: 'L', cap: true },
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

// --------------------------------------------------------------------------
// Section 1 — Word forms. Each builder returns a full pool (>=40 items) and the
// runner samples from it, so repetition is rare.
// --------------------------------------------------------------------------

const REG_PLURALS = [
  ['cat', 'cats'], ['dog', 'dogs'], ['book', 'books'], ['car', 'cars'],
  ['tree', 'trees'], ['key', 'keys'], ['day', 'days'], ['boy', 'boys'],
  ['toy', 'toys'], ['pen', 'pens'], ['cup', 'cups'], ['chair', 'chairs'],
  ['table', 'tables'], ['door', 'doors'], ['window', 'windows'], ['bag', 'bags'],
  ['hat', 'hats'], ['shoe', 'shoes'], ['bike', 'bikes'], ['road', 'roads'],
  ['cloud', 'clouds'], ['star', 'stars'], ['flower', 'flowers'], ['bird', 'birds'],
  ['teacher', 'teachers'], ['student', 'students'], ['friend', 'friends'],
  ['room', 'rooms'], ['lamp', 'lamps'], ['spoon', 'spoons'], ['fork', 'forks'],
  ['plate', 'plates'], ['bus', 'buses'], ['box', 'boxes'], ['watch', 'watches'],
  ['brush', 'brushes'], ['dish', 'dishes'], ['church', 'churches'], ['class', 'classes'],
  ['fox', 'foxes'], ['city', 'cities'], ['baby', 'babies'], ['story', 'stories'],
  ['party', 'parties'], ['family', 'families'], ['country', 'countries'],
  ['lady', 'ladies'], ['puppy', 'puppies'], ['leaf', 'leaves'], ['wolf', 'wolves'],
  ['shelf', 'shelves'], ['knife', 'knives'], ['wife', 'wives'], ['life', 'lives'],
  ['loaf', 'loaves'], ['half', 'halves'], ['potato', 'potatoes'], ['tomato', 'tomatoes'],
  ['hero', 'heroes'], ['echo', 'echoes'], ['photo', 'photos'], ['piano', 'pianos'],
  ['roof', 'roofs'], ['chief', 'chiefs'],
];

function pluralWrongs(s, correct) {
  const c = new Set();
  c.add(`${s}s`);
  c.add(`${s}es`);
  c.add(`${s}ies`);
  c.add(`${s}en`);
  if (/[^aeiou]y$/.test(s)) c.add(`${s.slice(0, -1)}ies`);
  if (/fe$/.test(s)) c.add(`${s.slice(0, -2)}ves`);
  if (/f$/.test(s)) c.add(`${s.slice(0, -1)}ves`);
  if (/o$/.test(s)) c.add(`${s}es`);
  c.delete(correct);
  return [...c];
}

const IRREGULAR_PLURALS = [
  ['child', 'children'], ['man', 'men'], ['woman', 'women'], ['foot', 'feet'],
  ['tooth', 'teeth'], ['goose', 'geese'], ['mouse', 'mice'], ['louse', 'lice'],
  ['ox', 'oxen'], ['person', 'people'], ['cactus', 'cacti'], ['focus', 'foci'],
  ['fungus', 'fungi'], ['nucleus', 'nuclei'], ['syllabus', 'syllabi'],
  ['analysis', 'analyses'], ['crisis', 'crises'], ['thesis', 'theses'],
  ['phenomenon', 'phenomena'], ['criterion', 'criteria'], ['datum', 'data'],
  ['medium', 'media'], ['bacterium', 'bacteria'], ['alumnus', 'alumni'],
  ['index', 'indices'], ['appendix', 'appendices'], ['matrix', 'matrices'],
  ['vertex', 'vertices'], ['basis', 'bases'], ['diagnosis', 'diagnoses'],
  ['parenthesis', 'parentheses'], ['stimulus', 'stimuli'], ['curriculum', 'curricula'],
  ['formula', 'formulae'], ['larva', 'larvae'], ['alga', 'algae'],
];

function irregularPluralWrongs(s, correct) {
  const c = new Set([`${s}s`, `${s}es`, `${s}en`]);
  c.delete(correct);
  return [...c];
}

const POSSESSIVE_NOUNS = [
  'boy', 'girl', 'cat', 'dog', 'teacher', 'student', 'mother', 'father',
  'sister', 'brother', 'friend', 'baby', 'lady', 'man', 'woman', 'child',
  'doctor', 'driver', 'artist', 'singer', 'worker', 'farmer', 'nurse', 'player',
];

function possessiveWrongs(base, plural) {
  if (plural) {
    return [`${base}s`, `${base}'s`, `${base}s's`, `${base}s'`];
  }
  return [`${base}s`, `${base}s'`, `${base}'s'`, base];
}

const VERB_FORMS = [
  ['fix', 'fixes', 'fixed', 'fixing'],
  ['watch', 'watches', 'watched', 'watching'],
  ['play', 'plays', 'played', 'playing'],
  ['study', 'studies', 'studied', 'studying'],
  ['carry', 'carries', 'carried', 'carrying'],
  ['stop', 'stops', 'stopped', 'stopping'],
  ['plan', 'plans', 'planned', 'planning'],
  ['drop', 'drops', 'dropped', 'dropping'],
  ['walk', 'walks', 'walked', 'walking'],
  ['talk', 'talks', 'talked', 'talking'],
  ['look', 'looks', 'looked', 'looking'],
  ['help', 'helps', 'helped', 'helping'],
  ['call', 'calls', 'called', 'calling'],
  ['open', 'opens', 'opened', 'opening'],
  ['close', 'closes', 'closed', 'closing'],
  ['clean', 'cleans', 'cleaned', 'cleaning'],
  ['paint', 'paints', 'painted', 'painting'],
  ['jump', 'jumps', 'jumped', 'jumping'],
  ['kick', 'kicks', 'kicked', 'kicking'],
  ['push', 'pushes', 'pushed', 'pushing'],
  ['pull', 'pulls', 'pulled', 'pulling'],
  ['cook', 'cooks', 'cooked', 'cooking'],
  ['bake', 'bakes', 'baked', 'baking'],
  ['dance', 'dances', 'danced', 'dancing'],
  ['live', 'lives', 'lived', 'living'],
  ['love', 'loves', 'loved', 'loving'],
  ['hope', 'hopes', 'hoped', 'hoping'],
  ['smile', 'smiles', 'smiled', 'smiling'],
  ['use', 'uses', 'used', 'using'],
  ['move', 'moves', 'moved', 'moving'],
  ['arrive', 'arrives', 'arrived', 'arriving'],
  ['decide', 'decides', 'decided', 'deciding'],
  ['enjoy', 'enjoys', 'enjoyed', 'enjoying'],
  ['cry', 'cries', 'cried', 'crying'],
  ['try', 'tries', 'tried', 'trying'],
  ['marry', 'marries', 'married', 'marrying'],
  ['copy', 'copies', 'copied', 'copying'],
  ['hurry', 'hurries', 'hurried', 'hurrying'],
  ['tidy', 'tidies', 'tidied', 'tidying'],
  ['rub', 'rubs', 'rubbed', 'rubbing'],
];

const IRREGULAR_VERBS = [
  ['be', 'was', 'been'], ['have', 'had', 'had'], ['do', 'did', 'done'],
  ['say', 'said', 'said'], ['go', 'went', 'gone'], ['get', 'got', 'gotten'],
  ['make', 'made', 'made'], ['know', 'knew', 'known'], ['think', 'thought', 'thought'],
  ['take', 'took', 'taken'], ['see', 'saw', 'seen'], ['come', 'came', 'come'],
  ['give', 'gave', 'given'], ['find', 'found', 'found'], ['tell', 'told', 'told'],
  ['become', 'became', 'become'], ['leave', 'left', 'left'], ['feel', 'felt', 'felt'],
  ['bring', 'brought', 'brought'], ['begin', 'began', 'begun'], ['keep', 'kept', 'kept'],
  ['hold', 'held', 'held'], ['write', 'wrote', 'written'], ['stand', 'stood', 'stood'],
  ['hear', 'heard', 'heard'], ['mean', 'meant', 'meant'], ['meet', 'met', 'met'],
  ['run', 'ran', 'run'], ['pay', 'paid', 'paid'], ['sit', 'sat', 'sat'],
  ['speak', 'spoke', 'spoken'], ['read', 'read', 'read'], ['grow', 'grew', 'grown'],
  ['lose', 'lost', 'lost'], ['fall', 'fell', 'fallen'], ['send', 'sent', 'sent'],
  ['build', 'built', 'built'], ['draw', 'drew', 'drawn'], ['break', 'broke', 'broken'],
  ['spend', 'spent', 'spent'], ['cut', 'cut', 'cut'], ['drive', 'drove', 'driven'],
  ['buy', 'bought', 'bought'], ['wear', 'wore', 'worn'], ['choose', 'chose', 'chosen'],
  ['eat', 'ate', 'eaten'], ['drink', 'drank', 'drunk'], ['sing', 'sang', 'sung'],
  ['swim', 'swam', 'swum'], ['fly', 'flew', 'flown'], ['throw', 'threw', 'thrown'],
  ['catch', 'caught', 'caught'], ['teach', 'taught', 'taught'], ['sell', 'sold', 'sold'],
  ['fight', 'fought', 'fought'], ['sleep', 'slept', 'slept'], ['freeze', 'froze', 'frozen'],
  ['hide', 'hid', 'hidden'], ['shoot', 'shot', 'shot'], ['put', 'put', 'put'],
  ['hit', 'hit', 'hit'], ['wake', 'woke', 'woken'],
];

function pastWrongs(base, past) {
  return [base, `${base}ed`, `${base}d`, `${past}ed`, `${base}ded`];
}

function participleWrongs(base, past, part) {
  return [past, base, `${base}ed`, `${base}en`, `${part}ed`];
}

const COMPARATIVES = [
  ['tall', 'taller', 'tallest', false], ['short', 'shorter', 'shortest', false],
  ['old', 'older', 'oldest', false], ['young', 'younger', 'youngest', false],
  ['fast', 'faster', 'fastest', false], ['slow', 'slower', 'slowest', false],
  ['high', 'higher', 'highest', false], ['low', 'lower', 'lowest', false],
  ['small', 'smaller', 'smallest', false], ['strong', 'stronger', 'strongest', false],
  ['weak', 'weaker', 'weakest', false], ['cold', 'colder', 'coldest', false],
  ['warm', 'warmer', 'warmest', false], ['cool', 'cooler', 'coolest', false],
  ['smart', 'smarter', 'smartest', false], ['clean', 'cleaner', 'cleanest', false],
  ['dark', 'darker', 'darkest', false], ['deep', 'deeper', 'deepest', false],
  ['big', 'bigger', 'biggest', 'double'], ['hot', 'hotter', 'hottest', 'double'],
  ['thin', 'thinner', 'thinnest', 'double'], ['fat', 'fatter', 'fattest', 'double'],
  ['sad', 'sadder', 'saddest', 'double'], ['wet', 'wetter', 'wettest', 'double'],
  ['happy', 'happier', 'happiest', 'y2i'], ['easy', 'easier', 'easiest', 'y2i'],
  ['busy', 'busier', 'busiest', 'y2i'], ['heavy', 'heavier', 'heaviest', 'y2i'],
  ['dry', 'drier', 'driest', 'y2i'], ['early', 'earlier', 'earliest', 'y2i'],
  ['good', 'better', 'best', 'irr'], ['bad', 'worse', 'worst', 'irr'],
  ['far', 'farther', 'farthest', 'irr'], ['little', 'less', 'least', 'irr'],
  ['many', 'more', 'most', 'irr'], ['beautiful', 'more beautiful', 'most beautiful', 'long'],
  ['expensive', 'more expensive', 'most expensive', 'long'],
  ['interesting', 'more interesting', 'most interesting', 'long'],
  ['difficult', 'more difficult', 'most difficult', 'long'],
  ['popular', 'more popular', 'most popular', 'long'],
  ['dangerous', 'more dangerous', 'most dangerous', 'long'],
  ['comfortable', 'more comfortable', 'most comfortable', 'long'],
];

function comparativeWrongs(adj, correct, type) {
  const c = new Set([adj]);
  if (type === 'long') {
    c.add(`${adj}er`); c.add(`${adj}est`);
    c.add(`more ${adj}`); c.add(`most ${adj}`);
  } else {
    c.add(`more ${adj}`); c.add(`most ${adj}`);
    c.add(`${adj}er`); c.add(`${adj}est`);
    if (type === 'double') c.add(`${adj}er` === correct ? `${adj.slice(0, -1)}er` : `${adj}er`);
    if (type === 'y2i') { c.add(`${adj}er`); c.add(`${adj.slice(0, -1)}ier`); c.add(`more ${adj}`); }
  }
  c.delete(correct);
  return [...c];
}

const ADVERBS = [
  ['quick', 'quickly'], ['slow', 'slowly'], ['happy', 'happily'],
  ['easy', 'easily'], ['busy', 'busily'], ['heavy', 'heavily'],
  ['lazy', 'lazily'], ['angry', 'angrily'], ['gentle', 'gently'],
  ['simple', 'simply'], ['terrible', 'terribly'], ['possible', 'possibly'],
  ['comfortable', 'comfortably'], ['probable', 'probably'], ['true', 'truly'],
  ['whole', 'wholly'], ['full', 'fully'], ['real', 'really'],
  ['usual', 'usually'], ['awful', 'awfully'], ['careful', 'carefully'],
  ['quiet', 'quietly'], ['loud', 'loudly'], ['beautiful', 'beautifully'],
  ['sad', 'sadly'], ['bad', 'badly'], ['good', 'well'], ['fast', 'fast'],
  ['hard', 'hard'], ['late', 'late'], ['early', 'early'], ['near', 'near'],
  ['far', 'far'], ['silent', 'silently'], ['sudden', 'suddenly'],
  ['clear', 'clearly'], ['perfect', 'perfectly'], ['correct', 'correctly'],
  ['safe', 'safely'], ['brave', 'bravely'], ['polite', 'politely'],
];

function adverbWrongs(adj, adv) {
  const c = new Set([adj, `${adj}ly`, `${adj}ily`]);
  if (/y$/.test(adj)) c.add(`${adj.slice(0, -1)}ily`);
  if (/e$/.test(adj)) c.add(`${adj}ly`);
  c.delete(adv);
  return [...c];
}

const REFLEXIVES = [
  ['I', 'myself'], ['you', 'yourself'], ['he', 'himself'], ['she', 'herself'],
  ['it', 'itself'], ['we', 'ourselves'], ['they', 'themselves'],
  ['the boy', 'himself'], ['the girl', 'herself'], ['the dog', 'itself'],
  ['the children', 'themselves'], ['my father', 'himself'], ['my mother', 'herself'],
  ['Tom', 'himself'], ['Anna', 'herself'], ['the students', 'themselves'],
  ['the cat', 'itself'], ['my friends', 'themselves'], ['the teacher', 'himself'],
  ['the workers', 'themselves'],
];

const REFLEXIVE_WRONGS = [
  'hisself', 'theirselves', 'themself', 'meself', 'ourselfs', 'youselves',
  'himselves', 'herselves', 'itselves',
];

const HOMOPHONES = [
  ['___ raining outside.', "it's", ['its', "its'", 'is']],
  ['The dog wagged ___ tail.', 'its', ["it's", "its'", 'is']],
  ['___ going to the park.', "they're", ['their', 'there', 'theyre']],
  ['___ house is on the corner.', 'their', ["they're", 'there', 'thier']],
  ['Put the book over ___.', 'there', ["they're", 'their', 'thier']],
  ['Is this ___ book?', 'your', ["you're", 'yore', 'yourr']],
  ['___ very kind.', "you're", ['your', 'yore', 'youre']],
  ['I want ___ go home.', 'to', ['too', 'two', 'tu']],
  ['It is ___ cold today.', 'too', ['to', 'two', 'tou']],
  ['I have ___ brothers.', 'two', ['to', 'too', 'tu']],
  ['She is taller ___ me.', 'than', ['then', 'that', 'than']],
  ['We ate dinner, ___ we left.', 'then', ['than', 'them', 'than']],
  ['What is your name?', 'What', ['Wat', 'Watt', 'Whot']],
  ['The movie had no ___ on me.', 'effect', ['affect', 'affekt', 'efect']],
  ['The rain will ___ the game.', 'affect', ['effect', 'affekt', 'efect']],
  ['I might ___ my keys.', 'lose', ['loose', 'loose', 'loes']],
  ['This shirt is too ___.', 'loose', ['lose', 'loose', 'luse']],
  ['___ coming to the party?', "Who's", ['Whose', 'Whos', 'Whoes']],
  ['___ bag is this?', 'Whose', ["Who's", 'Whos', 'Whoes']],
  ['I do not know ___ it will rain.', 'whether', ['weather', 'wether', 'weatherr']],
  ['The ___ is nice today.', 'weather', ['whether', 'wether', 'wheather']],
  ['Please ___ my apology.', 'accept', ['except', 'accept', 'exept']],
  ['Everyone came ___ Tom.', 'except', ['accept', 'exept', 'expcept']],
  ['The school ___ spoke to us.', 'principal', ['principle', 'principel', 'princaple']],
  ['It is a matter of ___.', 'principle', ['principal', 'principel', 'princaple']],
  ['We must have ___ in the world.', 'peace', ['piece', 'peice', 'pease']],
  ['I ate a ___ of cake.', 'piece', ['peace', 'peice', 'pease']],
  ['Please hit the ___.', 'brake', ['break', 'braik', 'bracke']],
  ['Do not ___ the glass.', 'break', ['brake', 'braik', 'bracke']],
  ['We walked ___ the old school.', 'past', ['passed', 'pased', 'passd']],
  ['She ___ the exam.', 'passed', ['past', 'pased', 'passd']],
  ['Please read the letter ___.', 'aloud', ['allowed', 'alowd', 'alloud']],
  ['We are not ___ to swim here.', 'allowed', ['aloud', 'alowd', 'alloud']],
  ['The car is ___, not moving.', 'stationary', ['stationery', 'stationarry', 'stationairy']],
  ['I bought new ___ for school.', 'stationery', ['stationary', 'stationarry', 'stationairy']],
  ['We crossed the hot ___.', 'desert', ['dessert', 'desrt', 'dessart']],
  ['I would like ___ after dinner.', 'dessert', ['desert', 'desrt', 'dessart']],
  ['He was ___ away by the crowd.', 'borne', ['born', 'bored', 'borrne']],
  ['She was ___ in July.', 'born', ['borne', 'bored', 'borrne']],
  ['The ___ of the story is clear.', 'moral', ['morale', 'morral', 'morral']],
  ['The team spirit was high; ___ was good.', 'morale', ['moral', 'morral', 'morral']],
];

const CONTRACTIONS = [
  ['do not', "don't"], ['does not', "doesn't"], ['did not', "didn't"],
  ['is not', "isn't"], ['are not', "aren't"], ['was not', "wasn't"],
  ['were not', "weren't"], ['have not', "haven't"], ['has not', "hasn't"],
  ['had not', "hadn't"], ['will not', "won't"], ['would not', "wouldn't"],
  ['can not', "can't"], ['could not', "couldn't"], ['should not', "shouldn't"],
  ['must not', "mustn't"], ['I am', "I'm"], ['you are', "you're"],
  ['he is', "he's"], ['she is', "she's"], ['it is', "it's"],
  ['we are', "we're"], ['they are', "they're"], ['I have', "I've"],
  ['I will', "I'll"], ['you will', "you'll"], ['they will', "they'll"],
  ['let us', "let's"], ['I would', "I'd"], ['they have', "they've"],
  ['we will', "we'll"], ['she will', "she'll"], ['he will', "he'll"],
  ['it will', "it'll"], ['is that', "that's"], ['who is', "who's"],
  ['there is', "there's"], ['what is', "what's"], ['here is', "here's"],
  ['you have', "you've"], ['we have', "we've"], ['does that', "that's"],
];

function contractionWrongs(full, contraction) {
  const base = full.replace(/ /g, '');
  const c = new Set([base, base.replace("n't", 'nt'), base.replace("'", '')]);
  const wp = base.replace('not', 'nt');
  c.add(wp.replace('o nt', "on't"));
  c.add(contraction.replace("'", "' "));
  c.delete(contraction);
  return [...c];
}

const SPELLINGS = [
  ['receive', ['recieve', 'receeve', 'reccive']],
  ['separate', ['seperate', 'separrate', 'seperete']],
  ['definitely', ['definately', 'definitly', 'defenitely']],
  ['occurred', ['occured', 'ocurred', 'occurred']],
  ['accommodate', ['accomodate', 'acommodate', 'acommodate']],
  ['believe', ['beleive', 'beleeve', 'belive']],
  ['weird', ['wierd', 'weerd', 'weard']],
  ['necessary', ['neccessary', 'necesary', 'necessery']],
  ['embarrass', ['embarass', 'embarrass', 'embaras']],
  ['recommend', ['recomend', 'reccommend', 'recommand']],
  ['beginning', ['begining', 'beginning', 'beggining']],
  ['calendar', ['calender', 'calandar', 'calander']],
  ['government', ['goverment', 'governmant', 'govenment']],
  ['environment', ['enviroment', 'environmant', 'envirnment']],
  ['tomorrow', ['tommorow', 'tomorow', 'tommorrow']],
  ['until', ['untill', 'untl', 'untill']],
  ['which', ['wich', 'whitch', 'whch']],
  ['because', ['becuase', 'becasue', 'becaues']],
  ['argument', ['arguement', 'argumant', 'arguemant']],
  ['atheist', ['athiest', 'atheist', 'athiest']],
  ['cemetery', ['cemetary', 'semetery', 'cemetarry']],
  ['conscious', ['concious', 'consious', 'conscius']],
  ['existence', ['existance', 'existense', 'existanse']],
  ['foreign', ['foriegn', 'forien', 'forreign']],
  ['grammar', ['grammer', 'gramar', 'grammer']],
  ['independent', ['independant', 'independ ent', 'indipendent']],
  ['knowledge', ['knowlege', 'knowledge', 'knowladge']],
  ['leisure', ['liesure', 'leasure', 'leizure']],
  ['maintenance', ['maintainance', 'maintenence', 'maintainence']],
  ['millennium', ['millenium', 'milennium', 'millenium']],
  ['occurrence', ['occurance', 'occurence', 'occurrance']],
  ['persistent', ['persistant', 'persistant', 'persistend']],
  ['possession', ['posession', 'possesion', 'possesson']],
  ['privilege', ['priviledge', 'privilige', 'privilage']],
  ['publicly', ['publically', 'publically', 'publickly']],
  ['questionnaire', ['questionaire', 'questionnair', 'questionare']],
  ['rhythm', ['rythm', 'rhythem', 'rythym']],
  ['success', ['sucess', 'succes', 'sucsess']],
  ['truly', ['truely', 'truley', 'truely']],
  ['vacuum', ['vacumm', 'vaccuum', 'vaccum']],
];

const NUMERALS = [
  ['There were two ___ people at the party.', 'hundred', ['hundreds', 'hundreds', 'hundredth']],
  ['She has three ___ books.', 'hundred', ['hundreds', 'hundreds', 'hundredth']],
  ['The company hired two ___ workers.', 'thousand', ['thousands', 'thousands', 'thousandth']],
  ['Five ___ dollars is a lot.', 'thousand', ['thousands', 'thousands', 'thousandth']],
  ['A five-___-old child started school.', 'year', ['years', 'year old', 'yeared']],
  ['They agreed to a ten-___ plan.', 'year', ['years', 'year old', 'yeared']],
  ['It was a three-___ journey.', 'hour', ['hours', 'hours', 'houred']],
  ['We waited for two ___.', 'hours', ['hour', 'hour', 'hourss']],
  ['She is a two-___-old toddler.', 'year', ['years', 'year old', 'yeared']],
  ['The table is two ___ long.', 'metres', ['metre', 'meter', 'metress']],
  ['He weighs about sixty ___.', 'kilograms', ['kilogram', 'kilos', 'kilogrammes']],
  ['Half an ___ passed.', 'hour', ['hours', 'hour', 'houred']],
  ['An ___ and a half is left.', 'hour', ['hours', 'hours', 'houred']],
  ['There are twelve ___ in a dozen.', 'items', ['item', 'item', 'itemses']],
  ['The room is ten ___ wide.', 'feet', ['foot', 'feets', 'foots']],
  ['The box is five ___ tall.', 'feet', ['foot', 'feets', 'foots']],
  ['She is six ___ tall.', 'feet', ['foot', 'feets', 'foots']],
  ['I need two ___ of milk.', 'litres', ['litre', 'liter', 'litress']],
  ['We drove eighty ___.', 'kilometres', ['kilometre', 'kilometer', 'kilometress']],
  ['The bill came to fifty ___.', 'dollars', ['dollar', 'dollar', 'dollares']],
  ['It costs twenty ___ pounds.', 'pounds', ['pound', 'pound', 'poundses']],
  ['Give me a ___ of water.', 'glass', ['glasses', 'glass', 'glassful']],
  ['She ate two ___ of bread.', 'slices', ['slice', 'slice', 'slicess']],
  ['There are sixty ___ in an hour.', 'minutes', ['minute', 'minute', 'minutess']],
  ['There are twenty-four ___ in a day.', 'hours', ['hour', 'hour', 'hourss']],
  ['Only a ___ of the cake was left.', 'piece', ['pieces', 'peace', 'pieced']],
  ['He is one hundred ___ old.', 'years', ['year', 'year', 'yearss']],
  ['It is two ___ since we met.', 'months', ['month', 'month', 'monthss']],
  ['The train leaves in ten ___.', 'minutes', ['minute', 'minute', 'minutess']],
  ['A dozen ___ were on the shelf.', 'eggs', ['egg', 'egg', 'eggss']],
  ['Two ___ of paper, please.', 'reams', ['ream', 'ream', 'reamss']],
  ['The wall is three ___ high.', 'metres', ['metre', 'meter', 'metress']],
  ['She ran five ___ today.', 'kilometres', ['kilometre', 'kilometer', 'kilometress']],
  ['Add two ___ of sugar.', 'cups', ['cup', 'cup', 'cupss']],
  ['There are thirty ___ in June.', 'days', ['day', 'day', 'dayss']],
];

// --------------------------------------------------------------------------
// Builders
// --------------------------------------------------------------------------

function buildPlurals() {
  return REG_PLURALS.map(([s, p]) => makeQ(
    `One ${s}, two ___.`,
    `Choose the correct plural of \u201c${s}\u201d.`,
    p,
    pluralWrongs(s, p),
    `The plural of \u201c${s}\u201d is \u201c${p}\u201d.`,
  ));
}

function buildIrregularPlurals() {
  return IRREGULAR_PLURALS.map(([s, p]) => makeQ(
    `One ${s}, two ___.`,
    `Choose the correct plural of \u201c${s}\u201d.`,
    p,
    irregularPluralWrongs(s, p),
    `\u201c${s}\u201d has the irregular plural \u201c${p}\u201d.`,
  ));
}

function buildPossessives() {
  const qs = [];
  POSSESSIVE_NOUNS.forEach((n) => {
    const sing = `${n}'s`;
    qs.push(makeQ(
      `The toy belongs to the ${n}. It is the ___ toy.`,
      `Choose the correct possessive (one ${n}).`,
      sing,
      possessiveWrongs(n, false),
      `A singular noun takes an apostrophe before the s: ${n} \u2192 ${sing}.`,
    ));
    const plur = `${n}s'`;
    qs.push(makeQ(
      `The toys belong to the ${n}s. They are the ___ toys.`,
      `Choose the correct possessive (many ${n}s).`,
      plur,
      possessiveWrongs(n, true),
      `A plural noun ending in -s takes the apostrophe after the s: ${n}s \u2192 ${plur}.`,
    ));
  });
  return qs;
}

function buildVerbEndings() {
  const qs = [];
  VERB_FORMS.forEach(([b, s, ed, ing]) => {
    qs.push(makeQ(`She ___ her homework every day.`, `Third-person singular present of \u201c${b}\u201d:`, s, [b, `${b}ed`, `${b}ing`, `${b}s`], `He/She/It takes \u201c${s}\u201d.`));
    qs.push(makeQ(`Yesterday they ___ at noon.`, `Past tense (-ed) of \u201c${b}\u201d:`, ed, [b, `${b}ed`, `${b}d`, `${b}ded`], `The past tense is \u201c${ed}\u201d.`));
    qs.push(makeQ(`They are ___ right now.`, `Present participle (-ing) of \u201c${b}\u201d:`, ing, [b, `${b}ing`, `${b}eing`, `${b}ying`], `The -ing form is \u201c${ing}\u201d.`));
  });
  return qs;
}

function buildIrregularPast() {
  return IRREGULAR_VERBS.map(([b, past]) => makeQ(
    `Yesterday I ___ it.`,
    `Past tense of \u201c${b}\u201d:`,
    past,
    pastWrongs(b, past),
    `The simple past of \u201c${b}\u201d is \u201c${past}\u201d (not \u201c${b}ed\u201d).`,
  ));
}

function buildIrregularParticiple() {
  return IRREGULAR_VERBS.map(([b, past, part]) => makeQ(
    `I have ___ it.`,
    `Past participle of \u201c${b}\u201d (used with have/has):`,
    part,
    participleWrongs(b, past, part),
    `The past participle of \u201c${b}\u201d is \u201c${part}\u201d.`,
  ));
}

function buildComparatives() {
  const qs = [];
  COMPARATIVES.forEach(([adj, comp, sup, type]) => {
    qs.push(makeQ(
      `This one is ___ than that one.`,
      `Comparative form of \u201c${adj}\u201d:`,
      comp,
      comparativeWrongs(adj, comp, type).concat([sup]),
      `The comparative of \u201c${adj}\u201d is \u201c${comp}\u201d.`,
    ));
    qs.push(makeQ(
      `This is the ___ of them all.`,
      `Superlative form of \u201c${adj}\u201d:`,
      sup,
      comparativeWrongs(adj, sup, type).concat([comp]),
      `The superlative of \u201c${adj}\u201d is \u201c${sup}\u201d.`,
    ));
  });
  return qs;
}

function buildAdverbs() {
  return ADVERBS.map(([adj, adv]) => makeQ(
    `He did the job ___.`,
    `Adverb form of the adjective \u201c${adj}\u201d:`,
    adv,
    adverbWrongs(adj, adv),
    `The adverb is \u201c${adv}\u201d.`,
  ));
}

function buildReflexives() {
  const qs = [];
  REFLEXIVES.forEach(([subj, refl]) => {
    qs.push(makeQ(
      `${subj.charAt(0).toUpperCase() + subj.slice(1)} looked at ___.`,
      `Choose the reflexive that matches \u201c${subj}\u201d.`,
      refl,
      unique([...REFLEXIVE_WRONGS, `${subj}`]),
      `\u201c${subj}\u201d takes the reflexive \u201c${refl}\u201d.`,
    ));
  });
  return qs;
}

function buildHomophones() {
  return HOMOPHONES.map(([sent, correct, wrongs]) => makeQ(
    sent.replace('___', correct),
    `Fill the blank: \u201c${sent}\u201d`,
    correct,
    wrongs,
    `The correct word is \u201c${correct}\u201d.`,
  ));
}

function buildContractions() {
  return CONTRACTIONS.map(([full, contr]) => makeQ(
    `\u201c${full}\u201d contracts to ___.`,
    `Choose the correct contraction of \u201c${full}\u201d.`,
    contr,
    contractionWrongs(full, contr),
    `\u201c${full.replace(/ /g, ' ')}\u201d becomes \u201c${contr}\u201d.`,
  ));
}

function buildSpellings() {
  return SPELLINGS.map(([correct, wrongs]) => makeQ(
    `Choose the correct spelling.`,
    `Which spelling is correct?`,
    correct,
    wrongs,
    `The correct spelling is \u201c${correct}\u201d.`,
  ));
}

function buildNumerals() {
  return NUMERALS.map(([sent, correct, wrongs]) => makeQ(
    sent.replace('___', correct),
    `Fill the blank: \u201c${sent}\u201d`,
    correct,
    wrongs,
    `The correct form is \u201c${correct}\u201d.`,
  ));
}

const BUILDERS = {
  '1.1': buildPlurals,
  '1.2': buildIrregularPlurals,
  '1.3': buildPossessives,
  '1.4': buildVerbEndings,
  '1.5': buildIrregularPast,
  '1.6': buildIrregularParticiple,
  '1.7': buildComparatives,
  '1.8': buildAdverbs,
  '1.9': buildReflexives,
  '1.10': buildHomophones,
  '1.11': buildContractions,
  '1.12': buildSpellings,
  '1.13': buildNumerals,
};

export const DIFFICULTY = {
  easy: { label: 'Easy', count: 5 },
  medium: { label: 'Medium', count: 5 },
  hard: { label: 'Hard', count: 10 },
};

export function hasQuiz(ruleId) {
  return Boolean(BUILDERS[ruleId]);
}

// Returns a randomised question pool for a rule (cached per rule so a run does
// not rebuild everything, but re-shuffled on each request for variety).
const cache = new Map();

export function questionPool(ruleId) {
  const build = BUILDERS[ruleId];
  if (!build) return [];
  if (!cache.has(ruleId)) cache.set(ruleId, build());
  return shuffle(cache.get(ruleId));
}

export function ruleInfo(ruleId) {
  for (const section of MATRIX_SECTIONS) {
    const found = section.rules.find((r) => r.id === ruleId);
    if (found) return { ...found, section: section.title, sectionId: section.id };
  }
  return null;
}

export { INDEX_OPTIONS };
