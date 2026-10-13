// Section 1 — Word forms.
//
// Each rule builds its 40 items with a *content generator*: slot i composes a
// distinct scenario (its own subject, verb, object and modifiers) and frames.js
// wraps that scenario in the i-th structurally distinct sentence shape. So no
// two questions in a rule/difficulty pool repeat the same context, and no two
// share a tree shape.
import { OBJECTS } from './core.js';
import { ruleItems } from './frames.js';

const at = (arr, i) => arr[((i % arr.length) + arr.length) % arr.length];
const step = (arr, i, k) => arr[(((i * k) % arr.length) + arr.length) % arr.length];
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

const WHO = [
  'The teacher', 'My friend', 'The farmer', 'The driver', 'The shopkeeper',
  'The cleaner', 'Her brother', 'The student', 'The nurse', 'The worker',
  'The gardener', 'The chef', 'His cousin', 'The guard', 'The baker',
  'The pilot', 'The painter', 'The author', 'The singer', 'The tailor',
  'The postman', 'The captain', 'The coach', 'The clerk', 'The plumber',
];

// Regular plural nouns: [singular, plural]
const REG = [
  ['book', 'books'], ['chair', 'chairs'], ['table', 'tables'], ['door', 'doors'],
  ['window', 'windows'], ['box', 'boxes'], ['watch', 'watches'], ['brush', 'brushes'],
  ['bench', 'benches'], ['city', 'cities'], ['baby', 'babies'], ['lady', 'ladies'],
  ['country', 'countries'], ['army', 'armies'], ['party', 'parties'], ['kiss', 'kisses'],
  ['dish', 'dishes'], ['class', 'classes'], ['glass', 'glasses'], ['church', 'churches'],
  ['branch', 'branches'], ['beach', 'beaches'], ['peach', 'peaches'], ['berry', 'berries'],
  ['cherry', 'cherries'], ['story', 'stories'], ['library', 'libraries'], ['family', 'families'],
  ['company', 'companies'], ['copy', 'copies'], ['key', 'keys'], ['boy', 'boys'],
  ['toy', 'toys'], ['day', 'days'], ['road', 'roads'], ['house', 'houses'],
  ['horse', 'horses'], ['nurse', 'nurses'], ['apple', 'apples'], ['shelf', 'shelves'],
];
const wrongPlural = (sg, pl) => [`${sg}s`, `${sg}es`, `${sg}ies`, `${sg}en`]
  .find((c) => c !== pl) || `${sg}ss`;

// Irregular plural nouns: [singular, plural]
const IRREG = [
  ['man', 'men'], ['woman', 'women'], ['child', 'children'], ['person', 'people'],
  ['tooth', 'teeth'], ['foot', 'feet'], ['mouse', 'mice'], ['goose', 'geese'],
  ['ox', 'oxen'], ['crisis', 'crises'], ['thesis', 'theses'], ['analysis', 'analyses'],
  ['basis', 'bases'], ['diagnosis', 'diagnoses'], ['criterion', 'criteria'],
  ['phenomenon', 'phenomena'], ['datum', 'data'], ['medium', 'media'],
  ['bacterium', 'bacteria'], ['cactus', 'cacti'], ['fungus', 'fungi'],
  ['nucleus', 'nuclei'], ['stimulus', 'stimuli'], ['alumnus', 'alumni'],
  ['index', 'indices'], ['appendix', 'appendices'], ['matrix', 'matrices'],
  ['vertex', 'vertices'], ['formula', 'formulae'], ['larva', 'larvae'],
  ['radius', 'radii'], ['axis', 'axes'], ['oasis', 'oases'], ['knife', 'knives'],
  ['wife', 'wives'], ['wolf', 'wolves'], ['half', 'halves'], ['loaf', 'loaves'],
  ['thief', 'thieves'], ['life', 'lives'],
];
const wrongIrregular = (sg, pl) => [`${sg}s`, `${sg}es`, `${sg}en`]
  .find((c) => c !== pl) || `${sg}s`;

const COUNT = ['counted', 'packed', 'moved', 'cleaned', 'painted', 'carried',
  'sorted', 'washed', 'lifted', 'loaded', 'checked', 'labelled', 'wrapped',
  'weighed', 'collected'];
const NUMWORD = ['two', 'three', 'four', 'five', 'six', 'several', 'many', 'a few'];

const PLACE = ['in the kitchen', 'near the river', 'at the office', 'in the garden',
  'on the farm', 'by the window', 'at the station', 'in the library'];

// Possessive owners
const OWNER_SG = ['boy', 'girl', 'teacher', 'doctor', 'driver', 'farmer',
  'student', 'nurse', 'worker', 'player', 'brother', 'sister', 'mother',
  'father', 'friend', 'pilot', 'baker', 'guard', 'author', 'painter'];

// Comparative adjectives: [base, comparative, superlative]
const COMP = [
  ['tall', 'taller', 'tallest'], ['short', 'shorter', 'shortest'], ['old', 'older', 'oldest'],
  ['young', 'younger', 'youngest'], ['fast', 'faster', 'fastest'], ['slow', 'slower', 'slowest'],
  ['high', 'higher', 'highest'], ['low', 'lower', 'lowest'], ['small', 'smaller', 'smallest'],
  ['strong', 'stronger', 'strongest'], ['weak', 'weaker', 'weakest'], ['cold', 'colder', 'coldest'],
  ['warm', 'warmer', 'warmest'], ['cool', 'cooler', 'coolest'], ['smart', 'smarter', 'smartest'],
  ['clean', 'cleaner', 'cleanest'], ['dark', 'darker', 'darkest'], ['deep', 'deeper', 'deepest'],
  ['big', 'bigger', 'biggest'], ['hot', 'hotter', 'hottest'], ['thin', 'thinner', 'thinnest'],
  ['sad', 'sadder', 'saddest'], ['happy', 'happier', 'happiest'], ['easy', 'easier', 'easiest'],
  ['busy', 'busier', 'busiest'], ['heavy', 'heavier', 'heaviest'], ['early', 'earlier', 'earliest'],
  ['good', 'better', 'best'], ['bad', 'worse', 'worst'], ['far', 'farther', 'farthest'],
  ['little', 'less', 'least'], ['many', 'more', 'most'], ['bright', 'brighter', 'brightest'],
  ['calm', 'calmer', 'calmest'], ['brave', 'braver', 'bravest'], ['fair', 'fairer', 'fairest'],
  ['kind', 'kinder', 'kindest'], ['rich', 'richer', 'richest'], ['safe', 'safer', 'safest'],
  ['wide', 'wider', 'widest'],
];

// Singular count nouns used as the compared subject in 1.7, so the subject is
// always a single thing ("the box is taller than ...") and never a plural that
// would break subject-verb agreement.
const COMP_SUBJ = ['the box', 'the room', 'the road', 'the plan', 'the test',
  'the essay', 'the wall', 'the chart', 'the garden', 'the chair', 'the tower',
  'the bridge', 'the lake', 'the hill', 'the shelf', 'the fence', 'the clock',
  'the desk', 'the map', 'the kite', 'the truck', 'the train', 'the pond',
  'the gate', 'the lamp', 'the park', 'the house', 'the tree', 'the nest',
  'the pool', 'the farm', 'the roof', 'the path', 'the barn',
  'the drum', 'the flag', 'the rope', 'the coin', 'the jar'];

// [adjective, adverb]
const ADV_FORMS = [
  ['quick', 'quickly'], ['slow', 'slowly'], ['happy', 'happily'], ['easy', 'easily'],
  ['busy', 'busily'], ['heavy', 'heavily'], ['lazy', 'lazily'], ['angry', 'angrily'],
  ['gentle', 'gently'], ['simple', 'simply'], ['terrible', 'terribly'], ['possible', 'possibly'],
  ['comfortable', 'comfortably'], ['probable', 'probably'], ['true', 'truly'], ['whole', 'wholly'],
  ['full', 'fully'], ['real', 'really'], ['usual', 'usually'], ['awful', 'awfully'],
  ['careful', 'carefully'], ['quiet', 'quietly'], ['loud', 'loudly'], ['beautiful', 'beautifully'],
  ['sad', 'sadly'], ['bad', 'badly'], ['good', 'well'], ['silent', 'silently'],
  ['sudden', 'suddenly'], ['clear', 'clearly'], ['perfect', 'perfectly'], ['correct', 'correctly'],
  ['safe', 'safely'], ['brave', 'bravely'], ['polite', 'politely'], ['calm', 'calmly'],
  ['bright', 'brightly'], ['warm', 'warmly'], ['soft', 'softly'], ['firm', 'firmly'],
];
const ACTION = ['sang the song', 'opened the door', 'answered the question',
  'painted the fence', 'read the letter', 'cleaned the room', 'closed the gate',
  'wrote the story', 'fixed the clock', 'carried the box', 'drove the car',
  'cooked the meal'];

// [subject, reflexive]
const REFLEX = [
  ['I', 'myself'], ['you', 'yourself'], ['he', 'himself'], ['she', 'herself'],
  ['it', 'itself'], ['we', 'ourselves'], ['they', 'themselves'], ['the boy', 'himself'],
  ['the girl', 'herself'], ['the dog', 'itself'], ['the puppy', 'itself'],
  ['my father', 'himself'], ['my mother', 'herself'], ['Tom', 'himself'],
  ['Anna', 'herself'], ['the kitten', 'itself'], ['the cat', 'itself'],
  ['the team', 'itself'], ['the teacher', 'himself'], ['the nurse', 'herself'],
  ['the driver', 'himself'], ['the doctor', 'herself'], ['the baby', 'itself'],
  ['the chef', 'himself'], ['my brother', 'himself'],
];
const REFLEXIVE_VERBS = ['prepared', 'introduced', 'taught', 'blamed', 'hurt',
  'convinced', 'reassured', 'described', 'photographed', 'protected'];
const REFLEXIVE_WRONG = ['hisself', 'theirselves', 'themself', 'meself',
  'ourselfs', 'youselves', 'himselves', 'herselves', 'itselves'];

// [template with ___, correct, wrong]
const HOMOPHONES = [
  ['___ raining outside.', "it's", 'its'],
  ['The dog wagged ___ tail.', 'its', "it's"],
  ['___ going to the park.', "they're", 'their'],
  ['___ house is on the corner.', 'their', "they're"],
  ['Put the book over ___.', 'there', 'their'],
  ['___ very kind.', "you're", 'your'],
  ['I want ___ go home.', 'to', 'too'],
  ['It is ___ cold today.', 'too', 'to'],
  ['I have ___ brothers.', 'two', 'to'],
  ['She is taller ___ me.', 'than', 'then'],
  ['The film ended and ___ we left.', 'then', 'than'],
  ['The movie had no ___ on me.', 'effect', 'affect'],
  ['The rain will ___ the game.', 'affect', 'effect'],
  ['I might ___ my keys.', 'lose', 'loose'],
  ['This shirt is too ___.', 'loose', 'lose'],
  ['I do not know ___ it will rain.', 'whether', 'weather'],
  ['The ___ is nice today.', 'weather', 'whether'],
  ['Please ___ my apology.', 'accept', 'except'],
  ['Everyone came ___ Tom.', 'except', 'accept'],
  ['The school ___ spoke to us.', 'principal', 'principle'],
  ['It is a matter of ___.', 'principle', 'principal'],
  ['We must have ___ in the world.', 'peace', 'piece'],
  ['I ate a ___ of cake.', 'piece', 'peace'],
  ['Please hit the ___.', 'brake', 'break'],
  ['Do not ___ the glass.', 'break', 'brake'],
  ['We walked ___ the old school.', 'past', 'passed'],
  ['She ___ the exam.', 'passed', 'past'],
  ['Please read the letter ___.', 'aloud', 'allowed'],
  ['We are not ___ to swim here.', 'allowed', 'aloud'],
  ['The car remained ___ for a week.', 'stationary', 'stationery'],
  ['I bought new ___ for school.', 'stationery', 'stationary'],
  ['We crossed the hot ___.', 'desert', 'dessert'],
  ['I would like ___ after dinner.', 'dessert', 'desert'],
  ['She was ___ in July.', 'born', 'borne'],
  ['The ___ of the story is clear.', 'moral', 'morale'],
  ['Team spirit was high; ___ was good.', 'morale', 'moral'],
  ['He is a member of the ___ board.', 'school', 'schol'],
  ['I wonder whether this is ___ book.', 'your', "you're"],
  ['I wonder ___ bag this is.', 'whose', "who's"],
  ['I wonder ___ coming to the party.', "who's", 'whose'],
];

// [bad (apostrophe dropped), good, full form, contraction]
const CONTRACTIONS = [
  ["They dont like the rain.", "They don't like the rain.", 'do not', "don't"],
  ["He doesnt like the rain.", "He doesn't like the rain.", 'does not', "doesn't"],
  ["She didnt finish her homework.", "She didn't finish her homework.", 'did not', "didn't"],
  ["He isnt very tired.", "He isn't very tired.", 'is not', "isn't"],
  ["They arent ready yet.", "They aren't ready yet.", 'are not', "aren't"],
  ["It wasnt my fault.", "It wasn't my fault.", 'was not', "wasn't"],
  ["They werent late today.", "They weren't late today.", 'were not', "weren't"],
  ["We havent seen that film.", "We haven't seen that film.", 'have not', "haven't"],
  ["He hasnt brushed his teeth.", "He hasn't brushed his teeth.", 'has not', "hasn't"],
  ["She hadnt called her mother.", "She hadn't called her mother.", 'had not', "hadn't"],
  ["He wont come to class.", "He won't come to class.", 'will not', "won't"],
  ["She wouldnt mind that.", "She wouldn't mind that.", 'would not', "wouldn't"],
  ["I cant swim very fast.", "I can't swim very fast.", 'can not', "can't"],
  ["He couldnt sleep last night.", "He couldn't sleep last night.", 'could not', "couldn't"],
  ["We shouldnt worry about it.", "We shouldn't worry about it.", 'should not', "shouldn't"],
  ["You mustnt run in the hall.", "You mustn't run in the hall.", 'must not', "mustn't"],
  ["Im tired now.", "I'm tired now.", 'I am', "I'm"],
  ["Youre late for dinner.", "You're late for dinner.", 'you are', "you're"],
  ["Hes at the office.", "He's at the office.", 'he is', "he's"],
  ["Shes busy this week.", "She's busy this week.", 'she is', "she's"],
  ["Its cold outside.", "It's cold outside.", 'it is', "it's"],
  ["Were ready to leave.", "We're ready to leave.", 'we are', "we're"],
  ["Theyre still at home.", "They're still at home.", 'they are', "they're"],
  ["Ive got a plan.", "I've got a plan.", 'I have', "I've"],
  ["Ill call you later.", "I'll call you later.", 'I will', "I'll"],
  ["Youll like this town.", "You'll like this town.", 'you will', "you'll"],
  ["Theyll wait for us.", "They'll wait for us.", 'they will', "they'll"],
  ["Youd enjoy this book.", "You'd enjoy this book.", 'you would', "you'd"],
  ["Id like that.", "I'd like that.", 'I would', "I'd"],
  ["Theyve already won.", "They've already won.", 'they have', "they've"],
  ["Well meet at noon.", "We'll meet at noon.", 'we will', "we'll"],
  ["Shell bring the book.", "She'll bring the book.", 'she will', "she'll"],
  ["Hell help us later.", "He'll help us later.", 'he will', "he'll"],
  ["Itll rain tonight.", "It'll rain tonight.", 'it will', "it'll"],
  ["The girl whos at the door is my cousin.", "The girl who's at the door is my cousin.", 'who is', "who's"],
  ["They wouldve told you.", "They would've told you.", 'would have', "would've"],
  ["Wed love that.", "We'd love that.", 'we would', "we'd"],
  ["Theyd say yes.", "They'd say yes.", 'they would', "they'd"],
  ["Youve been very kind.", "You've been very kind.", 'you have', "you've"],
  ["Weve already finished.", "We've already finished.", 'we have', "we've"],
];

// [correct, common misspelling]
const SPELLINGS = [
  ['receive', 'recieve'], ['separate', 'seperate'], ['definitely', 'definately'],
  ['occurred', 'occured'], ['accommodate', 'accomodate'], ['believe', 'beleive'],
  ['weird', 'wierd'], ['necessary', 'neccessary'], ['embarrass', 'embarass'],
  ['recommend', 'recomend'], ['beginning', 'begining'], ['calendar', 'calender'],
  ['government', 'goverment'], ['environment', 'enviroment'], ['tomorrow', 'tommorow'],
  ['until', 'untill'], ['which', 'wich'], ['because', 'becuase'], ['argument', 'arguement'],
  ['atheist', 'athiest'], ['cemetery', 'cemetary'], ['conscious', 'concious'],
  ['existence', 'existance'], ['foreign', 'foriegn'], ['grammar', 'grammer'],
  ['independent', 'independant'], ['knowledge', 'knowlege'], ['leisure', 'liesure'],
  ['maintenance', 'maintainance'], ['millennium', 'millenium'], ['occurrence', 'occurance'],
  ['persistent', 'persistant'], ['possession', 'posession'], ['privilege', 'priviledge'],
  ['publicly', 'publically'], ['questionnaire', 'questionaire'], ['rhythm', 'rythm'],
  ['success', 'sucess'], ['truly', 'truely'], ['vacuum', 'vacumm'],
];

const WHO_PL = [
  'The teachers', 'My friends', 'The students', 'The workers', 'The children',
  'The guests', 'The players', 'The farmers', 'The nurses', 'The painters',
];

const bare = (s) => s.replace(/^the\s+/, '');

// Intransitive regular verbs, [base, 3sg, past, prog], used so a core clause
// stays naturally complete ("The student walks") before a wrapper adds context.
const INTR_REG = [
  ['walk', 'walks', 'walked', 'walking'], ['talk', 'talks', 'talked', 'talking'],
  ['look', 'looks', 'looked', 'looking'], ['jump', 'jumps', 'jumped', 'jumping'],
  ['dance', 'dances', 'danced', 'dancing'], ['smile', 'smiles', 'smiled', 'smiling'],
  ['wait', 'waits', 'waited', 'waiting'], ['rest', 'rests', 'rested', 'resting'],
  ['play', 'plays', 'played', 'playing'], ['listen', 'listens', 'listened', 'listening'],
  ['arrive', 'arrives', 'arrived', 'arriving'], ['remember', 'remembers', 'remembered', 'remembering'],
  ['continue', 'continues', 'continued', 'continuing'], ['clap', 'claps', 'clapped', 'clapping'],
  ['camp', 'camps', 'camped', 'camping'], ['start', 'starts', 'started', 'starting'],
  ['finish', 'finishes', 'finished', 'finishing'], ['hurry', 'hurries', 'hurried', 'hurrying'],
  ['shout', 'shouts', 'shouted', 'shouting'], ['laugh', 'laughs', 'laughed', 'laughing'],
];

// Regular verbs whose -ed / -ing form is NOT base+-ed/-ing, so the wrong form
// "danced \u2192 danceed" is a real mistake for bases ending in -e or doubled
// consonants.
const INTR_TRIX = [
  ['dance', 'dances', 'danced', 'dancing'], ['smile', 'smiles', 'smiled', 'smiling'],
  ['arrive', 'arrives', 'arrived', 'arriving'], ['continue', 'continues', 'continued', 'continuing'],
  ['clap', 'claps', 'clapped', 'clapping'], ['stop', 'stops', 'stopped', 'stopping'],
  ['plan', 'plans', 'planned', 'planning'], ['rub', 'rubs', 'rubbed', 'rubbing'],
  ['nod', 'nods', 'nodded', 'nodding'], ['beg', 'begs', 'begged', 'begging'],
  ['shop', 'shops', 'shopped', 'shopping'], ['jog', 'jogs', 'jogged', 'jogging'],
  ['tag', 'tags', 'tagged', 'tagging'], ['hurry', 'hurries', 'hurried', 'hurrying'],
  ['carry', 'carries', 'carried', 'carrying'], ['worry', 'worries', 'worried', 'worrying'],
];
const INTR_HARD = [
  ['dance', 'dances', 'danced', 'dancing'], ['smile', 'smiles', 'smiled', 'smiling'],
  ['arrive', 'arrives', 'arrived', 'arriving'], ['continue', 'continues', 'continued', 'continuing'],
  ['clap', 'claps', 'clapped', 'clapping'], ['stop', 'stops', 'stopped', 'stopping'],
  ['plan', 'plans', 'planned', 'planning'], ['rub', 'rubs', 'rubbed', 'rubbing'],
  ['nod', 'nods', 'nodded', 'nodding'], ['beg', 'begs', 'begged', 'begging'],
  ['shop', 'shops', 'shopped', 'shopping'], ['jog', 'jogs', 'jogged', 'jogging'],
  ['drop', 'drops', 'dropped', 'dropping'], ['tap', 'taps', 'tapped', 'tapping'],
  ['tie', 'ties', 'tied', 'tying'], ['die', 'dies', 'died', 'dying'],
];

// Intransitive irregular verbs, [base, past, participle].
const IRRP = [
  ['go', 'went', 'gone'], ['come', 'came', 'come'], ['run', 'ran', 'run'],
  ['swim', 'swam', 'swum'], ['fly', 'flew', 'flown'], ['sing', 'sang', 'sung'],
  ['speak', 'spoke', 'spoken'], ['drive', 'drove', 'driven'], ['sleep', 'slept', 'slept'],
  ['sit', 'sat', 'sat'], ['stand', 'stood', 'stood'], ['wake', 'woke', 'woken'],
  ['fall', 'fell', 'fallen'], ['rise', 'rose', 'risen'], ['leave', 'left', 'left'],
  ['write', 'wrote', 'written'], ['eat', 'ate', 'eaten'], ['drink', 'drank', 'drunk'],
  ['begin', 'began', 'begun'],
];

const spellFrame = (word, i) => cap(at([
  `the teacher asked us to write "${word}" on the board`,
  `he always writes "${word}" in his essays`,
  `we practised the spelling of "${word}" in class`,
  `they asked him to spell "${word}" aloud`,
  `she read the word "${word}" off the page`,
], i));

export default {
  // 1.1 Regular noun plurals
  '1.1': (d) => ruleItems(d, (i) => {
    const [sg, pl] = at(REG, i);
    const num = at(NUMWORD, i * 3);
    const wrong = wrongPlural(sg, pl);
    // Vary syntactic structure
    const variants = [
      () => `${at(WHO, i)} ${step(COUNT, i, 5)} ${num} ${wrong}`,
      () => `${at(WHO, i)} found ${num} ${wrong} ${at(PLACE, i)}`,
      () => `We saw ${num} ${wrong} ${at(PLACE, i * 2)}`,
      () => `The shelf held ${num} ${wrong}`,
      () => `${num} ${wrong} were left ${at(PLACE, i * 3)}`,
      () => `${at(WHO, i)} sorted ${num} ${wrong} into piles`,
      () => `She packed ${num} ${wrong} for the trip`,
      () => `They donated ${num} ${wrong} to charity`,
    ];
    const g_variants = [
      () => `${at(WHO, i)} ${step(COUNT, i, 5)} ${num} ${pl}`,
      () => `${at(WHO, i)} found ${num} ${pl} ${at(PLACE, i)}`,
      () => `We saw ${num} ${pl} ${at(PLACE, i * 2)}`,
      () => `The shelf held ${num} ${pl}`,
      () => `${num} ${pl} were left ${at(PLACE, i * 3)}`,
      () => `${at(WHO, i)} sorted ${num} ${pl} into piles`,
      () => `She packed ${num} ${pl} for the trip`,
      () => `They donated ${num} ${pl} to charity`,
    ];
    const v = i % variants.length;
    return {
      bad: variants[v](),
      good: g_variants[v](),
      explanation: `The plural of "${sg}" is "${pl}".`
    };
  }),

  // 1.2 Irregular noun plurals
  '1.2': (d) => ruleItems(d, (i) => {
    const [sg, pl] = at(IRREG, i);
    const num = at(NUMWORD, i * 3);
    const wrong = wrongIrregular(sg, pl);
    const variants = [
      () => `${at(WHO, i)} ${step(COUNT, i, 3)} ${num} ${wrong}`,
      () => `${at(WHO, i)} saw ${num} ${wrong} ${at(PLACE, i)}`,
      () => `The barn held ${num} ${wrong}`,
      () => `${num} ${wrong} were grazing ${at(PLACE, i * 2)}`,
      () => `${at(WHO, i)} fed ${num} ${wrong} this morning`,
      () => `We observed ${num} ${wrong} in the field`,
      () => `${num} ${wrong} approached the gate`,
      () => `${at(WHO, i)} rescued ${num} ${wrong} from danger`,
    ];
    const g_variants = variants.map((fn) => {
      // Replace wrong with pl in the constructed string - easier to just reconstruct
      return () => {
        const vlist = [
          `${at(WHO, i)} ${step(COUNT, i, 3)} ${num} ${pl}`,
          `${at(WHO, i)} saw ${num} ${pl} ${at(PLACE, i)}`,
          `The barn held ${num} ${pl}`,
          `${num} ${pl} were grazing ${at(PLACE, i * 2)}`,
          `${at(WHO, i)} fed ${num} ${pl} this morning`,
          `We observed ${num} ${pl} in the field`,
          `${num} ${pl} approached the gate`,
          `${at(WHO, i)} rescued ${num} ${pl} from danger`,
        ];
        return vlist[i % vlist.length];
      };
    });
    const v = i % variants.length;
    // Simpler: just build both directly
    const builds = [
      [`${at(WHO, i)} ${step(COUNT, i, 3)} ${num} ${wrong}`, `${at(WHO, i)} ${step(COUNT, i, 3)} ${num} ${pl}`],
      [`${at(WHO, i)} saw ${num} ${wrong} ${at(PLACE, i)}`, `${at(WHO, i)} saw ${num} ${pl} ${at(PLACE, i)}`],
      [`The barn held ${num} ${wrong}`, `The barn held ${num} ${pl}`],
      [`${num} ${wrong} were grazing ${at(PLACE, i * 2)}`, `${num} ${pl} were grazing ${at(PLACE, i * 2)}`],
      [`${at(WHO, i)} fed ${num} ${wrong} this morning`, `${at(WHO, i)} fed ${num} ${pl} this morning`],
      [`We observed ${num} ${wrong} in the field`, `We observed ${num} ${pl} in the field`],
      [`${num} ${wrong} approached the gate`, `${num} ${pl} approached the gate`],
      [`${at(WHO, i)} rescued ${num} ${wrong} from danger`, `${at(WHO, i)} rescued ${num} ${pl} from danger`],
    ];
    const b = builds[v];
    return { bad: b[0], good: b[1], explanation: `"${sg}" has the irregular plural "${pl}".` };
  }),

  // 1.3 Possessive 's / s'
  '1.3': (d) => ruleItems(d, (i) => {
    if (i % 2 === 0) {
      const owner = at(OWNER_SG, i);
      const thing = bare(at(OBJECTS, i * 5));
      return {
        bad: `${at(WHO, i)} found the ${owner}s ${thing}`,
        good: `${at(WHO, i)} found the ${owner}'s ${thing}`,
        explanation: `A singular noun takes 's: ${owner} \u2192 ${owner}'s.`,
      };
    }
    const [, pl] = at(REG, i);
    const thing = bare(at(OBJECTS, i * 5 + 1));
    return {
      bad: `${at(WHO, i)} cleaned the ${pl}'s ${thing}`,
      good: `${at(WHO, i)} cleaned the ${pl}' ${thing}`,
      explanation: `A plural noun ending in -s takes the apostrophe after the s: ${pl} \u2192 ${pl}'.`,
    };
  }),

  // 1.4 Verb endings (-s, -ed, -ing)
  '1.4': (d) => ruleItems(d, (i) => {
    const who = step(WHO, i, 3);
    if (d === 'medium') {
      const [b, , ed] = at(INTR_TRIX, i);
      const builds = [
        [`${who} ${b}ed`, `${who} ${ed}`],
        [`${who} has ${b}ed`, `${who} has ${ed}`],
        [`Yesterday ${who} ${b}ed`, `Yesterday ${who} ${ed}`],
        [`${who} ${b}ed very well`, `${who} ${ed} very well`],
        [`By noon, ${who} had ${b}ed`, `By noon, ${who} had ${ed}`],
        [`The crowd saw that ${who} ${b}ed`, `The crowd saw that ${who} ${ed}`],
      ];
      const bb = builds[i % builds.length];
      return {
        bad: bb[0],
        good: bb[1],
        explanation: `The past tense is "${ed}", not "${b}ed".`,
      };
    }
    if (d === 'hard') {
      const [b, , , ing] = at(INTR_HARD, i);
      const builds = [
        [`${who} is ${b}ing`, `${who} is ${ing}`],
        [`${who} was ${b}ing`, `${who} was ${ing}`],
        [`Look, ${who} is ${b}ing`, `Look, ${who} is ${ing}`],
        [`${who} has been ${b}ing`, `${who} has been ${ing}`],
        [`I noticed ${who} was ${b}ing`, `I noticed ${who} was ${ing}`],
        [`While working, ${who} was ${b}ing`, `While working, ${who} was ${ing}`],
      ];
      const bb = builds[i % builds.length];
      return {
        bad: bb[0],
        good: bb[1],
        explanation: `The -ing form of "${b}" is "${ing}".`,
      };
    }
    const [b, s] = at(INTR_REG, i);
    const builds = [
      [`${who} ${b}`, `${who} ${s}`],
      [`Every day ${who} ${b}`, `Every day ${who} ${s}`],
      [`${who} usually ${b}`, `${who} usually ${s}`],
      [`In the morning, ${who} ${b}`, `In the morning, ${who} ${s}`],
      [`${who} never ${b} alone`, `${who} never ${s} alone`],
      [`It seems ${who} ${b} often`, `It seems ${who} ${s} often`],
    ];
    const bb = builds[i % builds.length];
    return {
      bad: bb[0],
      good: bb[1],
      explanation: `A singular subject takes "${s}".`,
    };
  }),

  // 1.5 Irregular past tense
  '1.5': (d) => ruleItems(d, (i) => {
    const [b, past] = at(IRRP, i);
    const who = step(WHO, i, 7);
    const builds = [
      [`${who} ${b}ed`, `${who} ${past}`],
      [`Yesterday ${who} ${b}ed`, `Yesterday ${who} ${past}`],
      [`Last week ${who} ${b}ed`, `Last week ${who} ${past}`],
      [`${who} ${b}ed early`, `${who} ${past} early`],
      [`We saw that ${who} ${b}ed`, `We saw that ${who} ${past}`],
      [`Earlier today, ${who} ${b}ed`, `Earlier today, ${who} ${past}`],
      [`${who} ${b}ed very quickly`, `${who} ${past} very quickly`],
      [`That morning, ${who} ${b}ed`, `That morning, ${who} ${past}`],
    ];
    const bb = builds[i % builds.length];
    return {
      bad: bb[0],
      good: bb[1],
      explanation: `The simple past of "${b}" is "${past}", not "${b}ed".`,
    };
  }),

  // 1.6 Irregular past participle
  '1.6': (d) => ruleItems(d, (i) => {
    const [b, , part] = at(IRRP, i);
    const who = i % 4 === 0 ? at(WHO_PL, i) : step(WHO, i, 7);
    const aux = i % 4 === 0 ? 'have' : 'has';
    const builds = [
      [`${who} ${aux} ${b}ed`, `${who} ${aux} ${part}`],
      [`${who} ${aux} never ${b}ed`, `${who} ${aux} never ${part}`],
      [`${who} ${aux} already ${b}ed`, `${who} ${aux} already ${part}`],
      [`${who} ${aux} just ${b}ed`, `${who} ${aux} just ${part}`],
      [`By now, ${who} ${aux} ${b}ed`, `By now, ${who} ${aux} ${part}`],
      [`It seems ${who} ${aux} ${b}ed`, `It seems ${who} ${aux} ${part}`],
      [`${who} ${aux} ${b}ed twice`, `${who} ${aux} ${part} twice`],
      [`Recently, ${who} ${aux} ${b}ed`, `Recently, ${who} ${aux} ${part}`],
    ];
    const bb = builds[i % builds.length];
    return {
      bad: bb[0],
      good: bb[1],
      explanation: `The past participle of "${b}" is "${part}", so it is "${aux} ${part}".`,
    };
  }),

  // 1.7 Comparative / superlative
  '1.7': (d) => ruleItems(d, (i) => {
    const [adj, comp, sup] = at(COMP, i);
    const a = at(COMP_SUBJ, i * 3);
    const b = at(COMP_SUBJ, i * 3 + 1);
    if (i % 2 === 0) {
      const builds = [
        [`${cap(a)} is more ${adj} than ${b}`, `${cap(a)} is ${comp} than ${b}`],
        [`${cap(a)} seems more ${adj} than ${b}`, `${cap(a)} seems ${comp} than ${b}`],
        [`Compared to ${b}, ${a} is more ${adj}`, `Compared to ${b}, ${a} is ${comp}`],
        [`${cap(a)} looks more ${adj} than ${b}`, `${cap(a)} looks ${comp} than ${b}`],
        [`This year, ${a} is more ${adj} than before`, `This year, ${a} is ${comp} than before`],
        [`Most agree ${a} is more ${adj} than ${b}`, `Most agree ${a} is ${comp} than ${b}`],
        [`${cap(a)} proved more ${adj} than ${b}`, `${cap(a)} proved ${comp} than ${b}`],
        [`In tests, ${a} is more ${adj} than ${b}`, `In tests, ${a} is ${comp} than ${b}`],
      ];
      const bb = builds[i % builds.length];
      return {
        bad: bb[0],
        good: bb[1],
        explanation: `The comparative of "${adj}" is "${comp}".`,
      };
    }
    const group = at(['boxes', 'rooms', 'roads', 'plans', 'tests', 'essays',
      'walls', 'charts', 'trees', 'trucks', 'lakes', 'farms', 'parks',
      'floors', 'rooms', 'boxes'], i);
    const builds = [
      [`Of all the ${group}, ${a} is the most ${adj} one`, `Of all the ${group}, ${a} is the ${sup} one`],
      [`Among the ${group}, ${a} is the most ${adj}`, `Among the ${group}, ${a} is the ${sup}`],
      [`Judged against other ${group}, ${a} is most ${adj}`, `Judged against other ${group}, ${a} is ${sup}`],
      [`Of these ${group}, ${a} stands out as most ${adj}`, `Of these ${group}, ${a} stands out as ${sup}`],
      [`After reviewing ${group}, we saw ${a} is most ${adj}`, `After reviewing ${group}, we saw ${a} is ${sup}`],
      [`In the set of ${group}, ${a} proved most ${adj}`, `In the set of ${group}, ${a} proved ${sup}`],
    ];
    const bb = builds[i % builds.length];
    return {
      bad: bb[0],
      good: bb[1],
      explanation: `The superlative of "${adj}" is "${sup}".`,
    };
  }),

  // 1.8 Adverb formation
  '1.8': (d) => ruleItems(d, (i) => {
    const [adj, adv] = at(ADV_FORMS, i);
    const action = at(ACTION, i * 3);
    const who = at(WHO, i);
    const builds = [
      [`${who} ${action} ${adj}`, `${who} ${action} ${adv}`],
      [`${who} completed the task ${adj}`, `${who} completed the task ${adv}`],
      [`${who} handled the situation ${adj}`, `${who} handled the situation ${adv}`],
      [`${who} spoke ${adj} to the audience`, `${who} spoke ${adv} to the audience`],
      [`Despite pressure, ${who} worked ${adj}`, `Despite pressure, ${who} worked ${adv}`],
      [`We noticed ${who} moved ${adj}`, `We noticed ${who} moved ${adv}`],
      [`${who} reacted ${adj} to the news`, `${who} reacted ${adv} to the news`],
      [`The team saw ${who} perform ${adj}`, `The team saw ${who} perform ${adv}`],
    ];
    const bb = builds[i % builds.length];
    return {
      bad: bb[0],
      good: bb[1],
      explanation: `The adverb of "${adj}" is "${adv}".`,
    };
  }),

  // 1.9 Reflexive forms
  '1.9': (d) => ruleItems(d, (i) => {
    const [subj, refl] = at(REFLEX, i);
    const verb = at(REFLEXIVE_VERBS, i * 3);
    const wrong = at(REFLEXIVE_WRONG, i);
    const builds = [
      [`${cap(subj)} ${verb} ${wrong}`, `${cap(subj)} ${verb} ${refl}`],
      [`${cap(subj)} tried to ${verb} ${wrong}`, `${cap(subj)} tried to ${verb} ${refl}`],
      [`Before leaving, ${subj} ${verb} ${wrong}`, `Before leaving, ${subj} ${verb} ${refl}`],
      [`${cap(subj)} ${verb} ${wrong} in the mirror`, `${cap(subj)} ${verb} ${refl} in the mirror`],
      [`After the fall, ${subj} ${verb} ${wrong}`, `After the fall, ${subj} ${verb} ${refl}`],
      [`${cap(subj)} quietly ${verb} ${wrong}`, `${cap(subj)} quietly ${verb} ${refl}`],
      [`In private, ${subj} ${verb} ${wrong}`, `In private, ${subj} ${verb} ${refl}`],
      [`${cap(subj)} took a moment to ${verb} ${wrong}`, `${cap(subj)} took a moment to ${verb} ${refl}`],
    ];
    const bb = builds[i % builds.length];
    return {
      bad: bb[0],
      good: bb[1],
      explanation: `"${subj}" takes the reflexive "${refl}".`,
    };
  }),

  // 1.10 Homophones
  '1.10': (d) => ruleItems(d, (i) => {
    const [tmpl, correct, wrong] = at(HOMOPHONES, i);
    const nice = (s) => s.replace(/\s+([.!?,])/g, '$1').replace(/[.]+$/, '').trim();
    const good = cap(nice(tmpl.replace('___', correct)));
    const bad = cap(nice(tmpl.replace('___', wrong)));
    // Add contextual variation around homophone templates
    const prefixes = [
      '', 'Yesterday I noticed: ', 'The teacher said, ', 'My friend asked, ',
      'I realised that ', 'She pointed out that ', 'It occurred to me that ',
      'During class we learned that ', 'He whispered that ',
    ];
    const suffixes = [
      '', ' earlier today', ' just now', ' last week',
    ];
    const p = prefixes[i % prefixes.length];
    const sfx = suffixes[(i * 3) % suffixes.length];
    // Only add prefix/suffix if not too awkward - but templates are full sentences mostly
    if (p && !p.endsWith(' ')) {
      // handle
    }
    const make = (txt) => {
      let out = txt;
      if (p.startsWith('Yesterday') || p.startsWith('The teacher') || p.startsWith('My friend') || p.startsWith('During') || p.startsWith('He')) {
        // prefix might need sentence structure
        out = p + out.charAt(0).toLowerCase() + out.slice(1) + sfx;
        if (out.endsWith(' ') || !out.match(/[.!?]$/)) out = out + '.';
      } else if (p) {
        out = p + out + sfx;
        if (!out.match(/[.!?]$/)) out = out + '.';
      }
      return out;
    };
    return { bad: make(bad), good: make(good), explanation: `The correct word is "${correct}".` };
  }),

  // 1.11 Contractions
  '1.11': (d) => ruleItems(d, (i) => {
    const [bad, good, full, contr] = at(CONTRACTIONS, i);
    const context = [
      '',
      'At this time, ',
      'Right now, ',
      'After all, ',
      'To be honest, ',
      'As it happens, ',
      'In fact, ',
      'Clearly, ',
    ];
    const ctxt = context[i % context.length];
    const wrap = (s) => {
      if (!ctxt) return s;
      let lower = s.charAt(0).toLowerCase() + s.slice(1);
      return ctxt + lower;
    };
    return {
      bad: wrap(bad),
      good: wrap(good),
      explanation: `"${full}" contracts to "${contr}" (keep the apostrophe).`,
    };
  }),

  // 1.12 Spelling
  '1.12': (d) => ruleItems(d, (i) => {
    const [good, wrong] = at(SPELLINGS, i);
    const extra = [
      (w) => `I made sure to use the word "${w}" correctly`,
      (w) => `The answer required the word "${w}"`,
      (w) => `We practised writing "${w}" in our notes`,
      (w) => `Her essay contained the word "${w}" twice`,
      (w) => `He carefully wrote "${w}" in the margin`,
      (w) => `The test asked for "${w}" in context`,
      (w) => `She misspelt nothing when using "${w}"`, // placeholder
      (w) => `Careful writers always get "${w}" right`,
    ];
    // easier: alternate between spellFrame and extra forms
    const useExtra = (i % 2 === 1);
    if (useExtra) {
      const ex = extra[i % extra.length];
      const bad = ex(wrong);
      const good = ex(good);
      // fix the "misspelt nothing" case for bad
      return {
        bad: bad.replace('misspelt nothing when using', 'used the incorrect form of'),
        good: good.replace('misspelt nothing when using', 'correctly used'),
        explanation: `The correct spelling is "${good}".`,
      };
    }
    return {
      bad: spellFrame(wrong, i),
      good: spellFrame(good, i),
      explanation: `The correct spelling is "${good}".`,
    };
  }),

  // 1.13 Numerals and measures
  '1.13': (d) => ruleItems(d, (i) => {
    const groups = [
      'two hundred', 'three hundred', 'four thousand', 'five thousand',
      'a five-year-old', 'a ten-year', 'a three-hour', 'two hours',
      'a two-year-old', 'two metres', 'sixty kilograms', 'half an hour',
      'an hour', 'twelve items', 'ten feet', 'five feet', 'six feet',
      'two litres', 'eighty kilometres', 'fifty dollars', 'twenty pounds',
      'a glass', 'two slices', 'sixty minutes', 'twenty-four hours',
      'a piece', 'one hundred years', 'two months', 'ten minutes', 'a dozen eggs',
      'two reams', 'three metres', 'five kilometres', 'two cups', 'thirty days',
      'three weeks', 'four days', 'ten dollars', 'two sets', 'four bowls',
    ];
    const wrongs = {
      'two hundred': 'two hundreds', 'three hundred': 'three hundreds',
      'four thousand': 'four thousands', 'five thousand': 'five thousands',
      'a five-year-old': 'a five-years-old', 'a ten-year': 'a ten-years',
      'a three-hour': 'a three-hours', 'two hours': 'two hour',
      'a two-year-old': 'a two-years-old', 'two metres': 'two metre',
      'sixty kilograms': 'sixty kilogram', 'half an hour': 'half an hours',
      'an hour': 'an hours', 'twelve items': 'twelve item', 'ten feet': 'ten foot',
      'five feet': 'five foot', 'six feet': 'six foot', 'two litres': 'two litre',
      'eighty kilometres': 'eighty kilometre', 'fifty dollars': 'fifty dollar',
      'twenty pounds': 'twenty pound', 'a glass': 'a glasses',
      'two slices': 'two slice', 'sixty minutes': 'sixty minute',
      'twenty-four hours': 'twenty-four hour', 'a piece': 'a pieces',
      'one hundred years': 'one hundred year', 'two months': 'two month',
      'ten minutes': 'ten minute', 'a dozen eggs': 'a dozen egg',
      'two reams': 'two ream', 'three metres': 'three metre',
      'five kilometres': 'five kilometre', 'two cups': 'two cup',
      'thirty days': 'thirty day', 'three weeks': 'three week',
      'four days': 'four day', 'ten dollars': 'ten dollar',
      'two sets': 'two set', 'four bowls': 'four bowl',
    };
    const good = at(groups, i);
    const builds = [
      [`${at(WHO, i)} needed ${wrongs[good]}`, `${at(WHO, i)} needed ${good}`],
      [`${at(WHO, i)} ordered ${wrongs[good]}`, `${at(WHO, i)} ordered ${good}`],
      [`${at(WHO, i)} bought ${wrongs[good]}`, `${at(WHO, i)} bought ${good}`],
      [`We measured ${wrongs[good]} for the job`, `We measured ${good} for the job`],
      [`The list included ${wrongs[good]}`, `The list included ${good}`],
      [`${at(WHO, i)} estimated ${wrongs[good]}`, `${at(WHO, i)} estimated ${good}`],
      [`They requested ${wrongs[good]}`, `They requested ${good}`],
      [`${at(WHO, i)} counted ${wrongs[good]}`, `${at(WHO, i)} counted ${good}`],
      [`The recipe called for ${wrongs[good]}`, `The recipe called for ${good}`],
      [`For the project, ${at(WHO, i)} required ${wrongs[good]}`, `For the project, ${at(WHO, i)} required ${good}`],
    ];
    const bb = builds[i % builds.length];
    return {
      bad: bb[0],
      good: bb[1],
      explanation: `The correct form is "${good}".`,
    };
  }),
};
