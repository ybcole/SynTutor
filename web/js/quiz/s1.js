// Section 1 — Word forms. Reference implementation for the other sections.
import {
  NOUNS, VERBS, VIRR, SG_SUBJ, NAMES, pool40, cartesian, pick, mk,
} from './core.js';

const wrongPlural = (sg, pl) => [`${sg}s`, `${sg}es`, `${sg}ies`, `${sg}en`]
  .find((c) => c !== pl) || `${sg}ss`;

// cycle a list against a frame list so long pools still yield 40 unique items
const cyc = (list, frames, make) => pool40((i) => make(pick(list, i), pick(frames, Math.floor(i / list.length))));

// ---- 1.1 Regular noun plurals -------------------------------------------
const PL_FRAMES = {
  easy: [(a, b) => `One ${a}, two ${b}.`, (a, b) => `I saw a ${a}, then I saw two ${b}.`],
  medium: [(a, b) => `The shop had one ${a} on display and two ${b} out back.`, (a, b) => `She carried one ${a} while her brother carried two ${b}.`],
  hard: [(a, b) => `Although she expected a single ${a}, the shelves were crowded with ${b}.`, (a, b) => `He ordered one ${a} at first, yet the final invoice listed dozens of ${b}.`],
};
function plurals(d) {
  const nouns = d === 'easy' ? NOUNS.slice(0, 26) : d === 'medium' ? NOUNS.slice(16, 42) : NOUNS.slice(30);
  return cyc(nouns, PL_FRAMES[d], (n, f) => {
    const [sg, pl] = n;
    return mk(f(sg, wrongPlural(sg, pl)), f(sg, pl), `The plural of "${sg}" is "${pl}".`);
  });
}

// ---- 1.2 Irregular noun plurals -----------------------------------------
const IRREGULAR = [
  ['man', 'men'], ['woman', 'women'], ['child', 'children'], ['person', 'people'],
  ['tooth', 'teeth'], ['foot', 'feet'], ['mouse', 'mice'], ['goose', 'geese'],
  ['ox', 'oxen'], ['louse', 'lice'], ['crisis', 'crises'], ['thesis', 'theses'],
  ['analysis', 'analyses'], ['basis', 'bases'], ['diagnosis', 'diagnoses'],
  ['criterion', 'criteria'], ['phenomenon', 'phenomena'], ['datum', 'data'],
  ['medium', 'media'], ['bacterium', 'bacteria'], ['cactus', 'cacti'],
  ['fungus', 'fungi'], ['nucleus', 'nuclei'], ['stimulus', 'stimuli'],
  ['alumnus', 'alumni'], ['index', 'indices'], ['appendix', 'appendices'],
  ['matrix', 'matrices'], ['vertex', 'vertices'], ['formula', 'formulae'],
  ['larva', 'larvae'], ['radius', 'radii'], ['axis', 'axes'], ['oasis', 'oases'],
  ['leaf', 'leaves'], ['knife', 'knives'], ['wife', 'wives'], ['wolf', 'wolves'],
  ['shelf', 'shelves'], ['half', 'halves'], ['loaf', 'loaves'], ['thief', 'thieves'],
];
const IR_FRAMES = {
  easy: [(a, b) => `One ${a}, two ${b}.`, (a, b) => `There was one ${a} and later two ${b}.`],
  medium: [(a, b) => `We counted one ${a}, and near the gate we spotted two ${b}.`, (a, b) => `A single ${a} appeared, followed by several ${b}.`],
  hard: [(a, b) => `A lone ${a} was recorded at dawn, but by evening the field was full of ${b}.`, (a, b) => `The report mentioned one ${a}, yet the raw data contained hundreds of ${b}.`],
};
function irregularPlurals(d) {
  const nouns = d === 'easy' ? IRREGULAR.slice(0, 20) : d === 'medium' ? IRREGULAR.slice(10, 34) : IRREGULAR.slice(22);
  return cyc(nouns, IR_FRAMES[d], (n, f) => {
    const [sg, pl] = n;
    const bad = [`${sg}s`, `${sg}es`, `${sg}en`].find((c) => c !== pl) || `${sg}s`;
    return mk(f(sg, bad), f(sg, pl), `"${sg}" has the irregular plural "${pl}".`);
  });
}

// ---- 1.3 Possessive 's / s' ---------------------------------------------
function possessives(d) {
  const nouns = d === 'easy' ? NOUNS.slice(0, 20) : d === 'medium' ? NOUNS.slice(6, 36) : NOUNS.slice(16);
  if (d === 'easy') {
    return cyc(nouns, [
      (n) => `The ${n} owns a new bicycle. It is the __ bicycle.`,
      (n) => `I met the ${n} earlier; this is the __ coat.`,
    ], (n, f) => mk(f(n).replace('__', `${n}s`), f(n).replace('__', `${n}'s`),
      `A singular noun takes 's: ${n} \u2192 ${n}'s.`));
  }
  if (d === 'medium') {
    return cyc(nouns.map(([s, p]) => p), [
      (p) => `The ${p} share a new bicycle. It is the __ bicycle.`,
      (p) => `We visited the ${p} house; the __ garden was lovely.`,
    ], (p, f) => mk(f(p).replace('__', `${p}'s`), f(p).replace('__', `${p}'`),
      `A plural noun ending in -s takes the apostrophe after the s: ${p} \u2192 ${p}'.`));
  }
  return cyc(nouns, [
    (n) => `The ${n[0]} shares the plot with the ${n[1]}, so it is the __ plot.`,
    (n) => `Both the ${n[0]} and the ${n[1]} use this gate; it is the __ gate.`,
  ], (n, f) => mk(f(n).replace('__', `${n[0]}'s`), f(n).replace('__', `${n[1]}'`),
    `The ${n[1]} take a plural possessive (${n[1]}'), not ${n[0]}'s.`));
}

// ---- 1.4 Verb endings (-s, -ed, -ing) -----------------------------------
const S_SUBJ = ['She', 'He', 'Tom', 'Anna', 'The boy', 'The girl', 'My friend', 'The teacher', 'The child', 'The dog'];
const P_SUBJ = ['They', 'We', 'You', 'The boys', 'The girls', 'My friends', 'The teachers', 'The children', 'The dogs', 'The students'];
function verbEndings(d) {
  if (d === 'easy') {
    return cartesian([VERBS, S_SUBJ, ['the car', 'the letter', 'the garden']],
      ([b, s], subj, obj) => mk(`${subj} ${b} ${obj} every day.`, `${subj} ${s} ${obj} every day.`, `A singular subject takes "${s}".`));
  }
  if (d === 'medium') {
    return cartesian([VERBS, P_SUBJ, ['the car', 'the letter', 'the garden', 'the door']],
      ([b, , ed], subj, obj) => mk(`${subj} ${b}ed ${obj} yesterday.`, `${subj} ${ed} ${obj} yesterday.`, `The past tense is "${ed}".`));
  }
  return cartesian([VERBS, S_SUBJ, ['the car', 'the book', 'the fence']],
    ([b, , , , ing], subj, obj) => mk(`${subj} is ${b}ing ${obj} right now.`, `${subj} is ${ing} ${obj} right now.`,
      `The -ing form of "${b}" is "${ing}" (watch the spelling).`));
}

// ---- 1.5 Irregular past tense -------------------------------------------
function irregularPast(d) {
  const verbs = d === 'easy' ? VIRR.slice(0, 18) : d === 'medium' ? VIRR.slice(10, 28) : VIRR.slice(20);
  const frame = {
    easy: (subj, v, obj) => `${subj} ${v} ${obj} yesterday.`,
    medium: (subj, v, obj) => `${subj} ${v} ${obj} before the meeting began.`,
    hard: (subj, v, obj) => `Although nobody noticed at first, ${subj} ${v} ${obj} long before the alarms rang.`,
  }[d];
  return cartesian([verbs, ['the letter', 'the door', 'the car', 'the parcel', 'the message'],
    ['She', 'He', 'Tom', 'Anna', 'The boy', 'The girl', 'We', 'They']],
  ([b, , past], obj, subj) => mk(frame(lc(subj), `${b}ed`, obj), frame(lc(subj), past, obj),
    `The simple past of "${b}" is "${past}", not "${b}ed".`));
}

// ---- 1.6 Irregular past participle --------------------------------------
function irregularParticiple(d) {
  const verbs = d === 'easy' ? VIRR.slice(0, 18) : d === 'medium' ? VIRR.slice(10, 28) : VIRR.slice(20);
  const frame = {
    easy: (subj, v, obj) => `${subj} ${v} ${obj}.`,
    medium: (subj, v, obj) => `By the time we arrived, ${subj} already ${v} ${obj}.`,
    hard: (subj, v, obj) => `No one could believe that ${subj} ${v} ${obj} so quickly before the deadline.`,
  }[d];
  return cartesian([verbs, [['She', 'has'], ['He', 'has'], ['Tom', 'has'], ['They', 'have'], ['We', 'have'], ['The boys', 'have']],
    ['the letter', 'the door', 'the car', 'the parcel', 'the message']],
  ([b, , past, part], [subj, aux], obj) => mk(frame(lc(subj), `${aux} ${past}`, obj), frame(lc(subj), `${aux} ${part}`, obj),
    `The past participle of "${b}" is "${part}", so it is "${aux} ${part}".`));
}

// ---- 1.7 Comparative / superlative --------------------------------------
const COMPARATIVES = [
  ['tall', 'taller', 'tallest'], ['short', 'shorter', 'shortest'], ['old', 'older', 'oldest'],
  ['young', 'younger', 'youngest'], ['fast', 'faster', 'fastest'], ['slow', 'slower', 'slowest'],
  ['high', 'higher', 'highest'], ['low', 'lower', 'lowest'], ['small', 'smaller', 'smallest'],
  ['strong', 'stronger', 'strongest'], ['weak', 'weaker', 'weakest'], ['cold', 'colder', 'coldest'],
  ['warm', 'warmer', 'warmest'], ['cool', 'cooler', 'coolest'], ['smart', 'smarter', 'smartest'],
  ['clean', 'cleaner', 'cleanest'], ['dark', 'darker', 'darkest'], ['deep', 'deeper', 'deepest'],
  ['big', 'bigger', 'biggest'], ['hot', 'hotter', 'hottest'], ['thin', 'thinner', 'thinnest'],
  ['sad', 'sadder', 'saddest'], ['happy', 'happier', 'happiest'], ['easy', 'easier', 'easiest'],
  ['busy', 'busier', 'busiest'], ['heavy', 'heavier', 'heaviest'], ['dry', 'drier', 'driest'],
  ['early', 'earlier', 'earliest'], ['good', 'better', 'best'], ['bad', 'worse', 'worst'],
  ['far', 'farther', 'farthest'], ['little', 'less', 'least'], ['many', 'more', 'most'],
  ['beautiful', 'more beautiful', 'most beautiful'], ['expensive', 'more expensive', 'most expensive'],
  ['interesting', 'more interesting', 'most interesting'], ['difficult', 'more difficult', 'most difficult'],
  ['popular', 'more popular', 'most popular'], ['dangerous', 'more dangerous', 'most dangerous'],
  ['comfortable', 'more comfortable', 'most comfortable'],
];
function comparatives(d) {
  const list = d === 'easy' ? COMPARATIVES.slice(0, 19)
    : d === 'medium' ? COMPARATIVES.slice(19, 30) : COMPARATIVES.slice(30);
  const letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];
  return cartesian([list, letters], ([adj, comp], x) => mk(
    `Option ${x} is more ${adj} than the others.`, `Option ${x} is ${comp} than the others.`,
    `The comparative of "${adj}" is "${comp}".`,
  )).concat(cartesian([list, letters], ([adj, , sup], x) => mk(
    `Option ${x} is the ${adj} of them all.`, `Option ${x} is the ${sup} of them all.`,
    `The superlative of "${adj}" is "${sup}".`,
  ))).slice(0, 40);
}

// ---- 1.8 Adverb formation ------------------------------------------------
const ADVERBS = [
  ['quick', 'quickly'], ['slow', 'slowly'], ['happy', 'happily'], ['easy', 'easily'],
  ['busy', 'busily'], ['heavy', 'heavily'], ['lazy', 'lazily'], ['angry', 'angrily'],
  ['gentle', 'gently'], ['simple', 'simply'], ['terrible', 'terribly'], ['possible', 'possibly'],
  ['comfortable', 'comfortably'], ['probable', 'probably'], ['true', 'truly'], ['whole', 'wholly'],
  ['full', 'fully'], ['real', 'really'], ['usual', 'usually'], ['awful', 'awfully'],
  ['careful', 'carefully'], ['quiet', 'quietly'], ['loud', 'loudly'], ['beautiful', 'beautifully'],
  ['sad', 'sadly'], ['bad', 'badly'], ['good', 'well'], ['silent', 'silently'],
  ['sudden', 'suddenly'], ['clear', 'clearly'], ['perfect', 'perfectly'], ['correct', 'correctly'],
  ['safe', 'safely'], ['brave', 'bravely'], ['polite', 'politely'],
];
function adverbFormation(d) {
  const list = d === 'easy' ? ADVERBS.slice(0, 12)
    : d === 'medium' ? ADVERBS.slice(12, 26) : ADVERBS.slice(24);
  const verbs = ['finished the task', 'answered the question', 'opened the door', 'painted the fence', 'read the letter'];
  return cartesian([list, verbs], ([adj, adv], vp) => mk(
    `She ${vp} ${adj}.`, `She ${vp} ${adv}.`, `The adverb of "${adj}" is "${adv}".`));
}

// ---- 1.9 Reflexive forms -------------------------------------------------
const REFLEXIVES = [
  ['I', 'myself'], ['you', 'yourself'], ['he', 'himself'], ['she', 'herself'],
  ['it', 'itself'], ['we', 'ourselves'], ['they', 'themselves'],
  ['the boy', 'himself'], ['the girl', 'herself'], ['the dog', 'itself'],
  ['the children', 'themselves'], ['my father', 'himself'], ['my mother', 'herself'],
  ['Tom', 'himself'], ['Anna', 'herself'], ['the students', 'themselves'],
  ['the cat', 'itself'], ['my friends', 'themselves'], ['the teacher', 'himself'],
  ['the workers', 'themselves'],
];
const REFLEXIVE_WRONGS = ['hisself', 'theirselves', 'themself', 'meself', 'ourselfs', 'youselves', 'himselves', 'herselves', 'itselves'];
function reflexives(d) {
  const list = d === 'easy' ? REFLEXIVES.slice(0, 8) : d === 'medium' ? REFLEXIVES.slice(7, 16) : REFLEXIVES;
  const frames = d === 'easy'
    ? ['looked at __', 'hurt __', 'blamed __', 'introduced __', 'taught __']
    : d === 'medium'
      ? ['prepared __', 'convinced __', 'reassured __', 'photographed __', 'described __']
      : ['was proud of __', 'took care of __', 'spoke about __', 'believed in __', 'relied on __'];
  return cartesian([list, frames], ([subj, refl], frame) => {
    const wrong = pick(REFLEXIVE_WRONGS, subj.length + frame.length);
    const cap = subj.charAt(0).toUpperCase() + subj.slice(1);
    return mk(`${cap} ${frame.replace('__', wrong)}.`, `${cap} ${frame.replace('__', refl)}.`,
      `"${subj}" takes the reflexive "${refl}".`);
  });
}

// ---- 1.10 Homophones -----------------------------------------------------
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
  ['She is taller ___ me.', 'than', ['then', 'that', 'thn']],
  ['We ate dinner, ___ we left.', 'then', ['than', 'them', 'thn']],
  ['The movie had no ___ on me.', 'effect', ['affect', 'affekt', 'efect']],
  ['The rain will ___ the game.', 'affect', ['effect', 'affekt', 'efect']],
  ['I might ___ my keys.', 'lose', ['loose', 'loes', 'loze']],
  ['This shirt is too ___.', 'loose', ['lose', 'luse', 'loze']],
  ['___ coming to the party?', "Who's", ['Whose', 'Whos', 'Whoes']],
  ['___ bag is this?', 'Whose', ["Who's", 'Whos', 'Whoes']],
  ['I do not know ___ it will rain.', 'whether', ['weather', 'wether', 'wheather']],
  ['The ___ is nice today.', 'weather', ['whether', 'wether', 'wheather']],
  ['Please ___ my apology.', 'accept', ['except', 'exept', 'accepte']],
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
  ['She was ___ in July.', 'born', ['borne', 'bored', 'borrne']],
  ['The ___ of the story is clear.', 'moral', ['morale', 'morral', 'morral']],
  ['Team spirit was high; ___ was good.', 'morale', ['moral', 'morral', 'morral']],
  ['He is a member of the ___ board.', 'school', ['schol', 'schole', 'skool']],
];
function homophones(d) {
  const list = d === 'easy' ? HOMOPHONES.slice(0, 20) : d === 'medium' ? HOMOPHONES.slice(10, 30) : HOMOPHONES.slice(22);
  const tails = d === 'easy' ? ['', ' every day'] : d === 'medium' ? ['', ' again'] : ['', ' once again', ' for everyone'];
  return pool40((i) => {
    const [tmpl, correct, wrongs] = pick(list, i);
    const tail = pick(tails, Math.floor(i / list.length));
    const good = (tmpl.replace('___', correct) + tail).trim();
    const bad = (tmpl.replace('___', wrongs[0]) + tail).trim();
    return mk(bad, good, `The correct word is "${correct}".`);
  });
}

// ---- 1.11 Contractions ---------------------------------------------------
const CONTRACTIONS = [
  ['do not', "don't"], ['does not', "doesn't"], ['did not', "didn't"], ['is not', "isn't"],
  ['are not', "aren't"], ['was not', "wasn't"], ['were not', "weren't"], ['have not', "haven't"],
  ['has not', "hasn't"], ['had not', "hadn't"], ['will not', "won't"], ['would not', "wouldn't"],
  ['can not', "can't"], ['could not', "couldn't"], ['should not', "shouldn't"], ['must not', "mustn't"],
  ['I am', "I'm"], ['you are', "you're"], ['he is', "he's"], ['she is', "she's"],
  ['it is', "it's"], ['we are', "we're"], ['they are', "they're"], ['I have', "I've"],
  ['I will', "I'll"], ['you will', "you'll"], ['they will', "they'll"], ['let us', "let's"],
  ['I would', "I'd"], ['they have', "they've"], ['we will', "we'll"], ['she will', "she'll"],
  ['he will', "he'll"], ['it will', "it'll"], ['who is', "who's"], ['there is', "there's"],
  ['what is', "what's"], ['here is', "here's"], ['you have', "you've"], ['we have', "we've"],
];
function contractions(d) {
  const list = d === 'easy' ? CONTRACTIONS.slice(0, 20) : d === 'medium' ? CONTRACTIONS.slice(10, 30) : CONTRACTIONS.slice(22);
  const frames = [(full) => `"${full}" contracts to ___.`, (full) => `In speech we shorten "${full}" to ___.`, (full) => `The short form of "${full}" is ___.`];
  return cyc(list, frames, ([full, contr], f) => mk(
    f(full).replace('___', contr.replace("'", '')),
    f(full).replace('___', contr),
    `"${full}" contracts to "${contr}" (keep the apostrophe).`));
}

// ---- 1.12 Spelling -------------------------------------------------------
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
function spellings(d) {
  const list = d === 'easy' ? SPELLINGS.slice(0, 18) : d === 'medium' ? SPELLINGS.slice(10, 30) : SPELLINGS.slice(22);
  const frames = ['The correct spelling is ___.', 'She wrote "___" on the board.', 'He asked how to spell "___".'];
  return cartesian([list, frames], ([good, wrong], frame) => mk(
    frame.replace('___', wrong), frame.replace('___', good), `The correct spelling is "${good}".`));
}

// ---- 1.13 Numerals and measures -----------------------------------------
const NUMERALS = [
  ['There were two ___ people at the party.', 'hundred', ['hundreds', 'hundredth']],
  ['She has three ___ books.', 'hundred', ['hundreds', 'hundredth']],
  ['The company hired two ___ workers.', 'thousand', ['thousands', 'thousandth']],
  ['Five ___ dollars is a lot.', 'thousand', ['thousands', 'thousandth']],
  ['A five-___-old child started school.', 'year', ['years', 'yeared']],
  ['They agreed to a ten-___ plan.', 'year', ['years', 'yeared']],
  ['It was a three-___ journey.', 'hour', ['hours', 'houred']],
  ['We waited for two ___.', 'hours', ['hour', 'hourss']],
  ['She is a two-___-old toddler.', 'year', ['years', 'yeared']],
  ['The table is two ___ long.', 'metres', ['metre', 'metress']],
  ['He weighs about sixty ___.', 'kilograms', ['kilogram', 'kilogrammes']],
  ['Half an ___ passed.', 'hour', ['hours', 'houred']],
  ['An ___ and a half is left.', 'hour', ['hours', 'houred']],
  ['There are twelve ___ in a dozen.', 'items', ['item', 'itemses']],
  ['The room is ten ___ wide.', 'feet', ['foot', 'feets']],
  ['The box is five ___ tall.', 'feet', ['foot', 'feets']],
  ['She is six ___ tall.', 'feet', ['foot', 'feets']],
  ['I need two ___ of milk.', 'litres', ['litre', 'litress']],
  ['We drove eighty ___.', 'kilometres', ['kilometre', 'kilometress']],
  ['The bill came to fifty ___.', 'dollars', ['dollar', 'dollares']],
  ['It costs twenty ___ pounds.', 'pounds', ['pound', 'poundses']],
  ['Give me a ___ of water.', 'glass', ['glasses', 'glassful']],
  ['She ate two ___ of bread.', 'slices', ['slice', 'slicess']],
  ['There are sixty ___ in an hour.', 'minutes', ['minute', 'minutess']],
  ['There are twenty-four ___ in a day.', 'hours', ['hour', 'hourss']],
  ['Only a ___ of the cake was left.', 'piece', ['pieces', 'pieced']],
  ['He is one hundred ___ old.', 'years', ['year', 'yearss']],
  ['It is two ___ since we met.', 'months', ['month', 'monthss']],
  ['The train leaves in ten ___.', 'minutes', ['minute', 'minutess']],
  ['A dozen ___ were on the shelf.', 'eggs', ['egg', 'eggss']],
  ['Two ___ of paper, please.', 'reams', ['ream', 'reamss']],
  ['The wall is three ___ high.', 'metres', ['metre', 'metress']],
  ['She ran five ___ today.', 'kilometres', ['kilometre', 'kilometress']],
  ['Add two ___ of sugar.', 'cups', ['cup', 'cupss']],
  ['There are thirty ___ in June.', 'days', ['day', 'dayss']],
];
function numerals(d) {
  const list = d === 'easy' ? NUMERALS.slice(0, 18) : d === 'medium' ? NUMERALS.slice(8, 30) : NUMERALS.slice(18);
  const tails = d === 'easy' ? ['', ' Please check it.', ' Thanks.'] : d === 'medium' ? ['', ' Read it aloud.'] : ['', ' Write it down.', ' Check the unit.'];
  return pool40((i) => {
    const [tmpl, correct, wrongs] = pick(list, i);
    const tail = pick(tails, Math.floor(i / list.length));
    return mk((tmpl.replace('___', wrongs[0]) + tail).trim(), (tmpl.replace('___', correct) + tail).trim(),
      `The correct form is "${correct}".`);
  });
}

function lc(s) { return /^[A-Z]/.test(s) && s.split(' ').length > 1 ? s.charAt(0).toLowerCase() + s.slice(1) : s; }

export default {
  '1.1': plurals,
  '1.2': irregularPlurals,
  '1.3': possessives,
  '1.4': verbEndings,
  '1.5': irregularPast,
  '1.6': irregularParticiple,
  '1.7': comparatives,
  '1.8': adverbFormation,
  '1.9': reflexives,
  '1.10': homophones,
  '1.11': contractions,
  '1.12': spellings,
  '1.13': numerals,
};
