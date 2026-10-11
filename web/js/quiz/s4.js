// Section 4 — Nouns (3 rules). One builder per rule; each returns 40 items per
// difficulty tier ('easy' | 'medium' | 'hard').
import {
  pick, mk, pool40, cartesian,
} from './core.js';

// ---- 4.1 Countable vs uncountable ---------------------------------------
// [mass noun, wrong "plural"]
const UNCOUNT = [
  ['information', 'informations'], ['advice', 'advices'], ['furniture', 'furnitures'],
  ['homework', 'homeworks'], ['bread', 'breads'], ['milk', 'milks'],
  ['rice', 'rices'], ['sugar', 'sugars'], ['flour', 'flours'], ['soap', 'soaps'],
  ['shampoo', 'shampoos'], ['toothpaste', 'toothpastes'], ['honey', 'honeys'],
  ['jam', 'jams'], ['butter', 'butters'], ['cheese', 'cheeses'], ['cream', 'creams'],
  ['yoghurt', 'yoghurts'], ['juice', 'juices'], ['lemonade', 'lemonades'],
  ['petrol', 'petrols'], ['diesel', 'diesels'], ['coal', 'coals'], ['chalk', 'chalks'],
  ['ink', 'inks'], ['glue', 'glues'], ['wheat', 'wheats'], ['corn', 'corns'],
  ['hay', 'hays'], ['straw', 'straws'], ['gravel', 'gravels'], ['mud', 'muds'],
  ['sand', 'sands'], ['snow', 'snows'], ['oil', 'oils'], ['coffee', 'coffees'],
  ['tea', 'teas'], ['salt', 'salts'], ['pepper', 'peppers'], ['water', 'waters'],
];

const artOf = (u) => (/^[aeiou]/.test(u) ? 'an' : 'a');

const U_FRAMES = {
  easy: [
    (u, wp) => [`There are many ${wp} on the shelf.`, `There is much ${u} on the shelf.`,
      `"${u}" is uncountable, so it takes "much", not the plural "${wp}".`],
    (u, wp) => [`We do not have many ${wp} left.`, `We do not have much ${u} left.`,
      `Uncountable "${u}" has no plural "${wp}"; use "much ${u}".`],
  ],
  medium: [
    (u) => [`He asked for ${artOf(u)} ${u}.`, `He asked for some ${u}.`,
      `"${u}" is uncountable and takes "some", not the article "${artOf(u)}".`],
    (u) => [`The workers unloaded ${artOf(u)} ${u} from the truck.`, `The workers unloaded some ${u} from the truck.`,
      `Drop the article: uncountable "${u}" takes "some ${u}".`],
  ],
  hard: [
    (u, wp) => [`The manager insisted that the ${wp} sent by the supplier were unreliable.`,
      `The manager insisted that the ${u} sent by the supplier was unreliable.`,
      `"${u}" is uncountable, so use "${u} was", not "${wp} were".`],
    (u, wp) => [`Because the ${wp} stored in the cellar were ruined, we ordered replacements.`,
      `Because the ${u} stored in the cellar was ruined, we ordered replacements.`,
      `Uncountable "${u}" takes the singular verb: "${u} was".`],
    (u, wp) => [`The inspector noted that many ${wp} had been wasted during the project.`,
      `The inspector noted that much ${u} had been wasted during the project.`,
      `"${u}" is uncountable and takes "much", not the plural "${wp}".`],
  ],
};

function countableUncountable(d) {
  return cartesian([UNCOUNT, U_FRAMES[d]], ([u, wp], f) => {
    const [bad, good, explanation] = f(u, wp);
    return mk(bad, good, explanation);
  });
}

// ---- 4.2 Noun as modifier (number) ---------------------------------------
// [singular unit, plural unit, modified head noun]
const TRIPLES = [
  ['year', 'years', 'plan'], ['year', 'years', 'contract'], ['year', 'years', 'lease'],
  ['year', 'years', 'course'], ['year', 'years', 'warranty'], ['year', 'years', 'programme'],
  ['year', 'years', 'study'], ['week', 'weeks', 'holiday'], ['week', 'weeks', 'trip'],
  ['week', 'weeks', 'course'], ['week', 'weeks', 'strike'], ['week', 'weeks', 'delay'],
  ['week', 'weeks', 'placement'], ['month', 'months', 'project'], ['month', 'months', 'course'],
  ['month', 'months', 'lease'], ['month', 'months', 'tour'], ['month', 'months', 'trial'],
  ['day', 'days', 'journey'], ['day', 'days', 'trip'], ['day', 'days', 'visit'],
  ['day', 'days', 'trek'], ['day', 'days', 'course'], ['day', 'days', 'festival'],
  ['hour', 'hours', 'flight'], ['hour', 'hours', 'journey'], ['hour', 'hours', 'delay'],
  ['hour', 'hours', 'meeting'], ['hour', 'hours', 'shift'], ['hour', 'hours', 'drive'],
  ['hour', 'hours', 'wait'], ['hour', 'hours', 'seminar'], ['minute', 'minutes', 'walk'],
  ['minute', 'minutes', 'break'], ['minute', 'minutes', 'speech'], ['minute', 'minutes', 'delay'],
  ['minute', 'minutes', 'call'], ['minute', 'minutes', 'interview'], ['second', 'seconds', 'delay'],
  ['second', 'seconds', 'pause'], ['second', 'seconds', 'lead'], ['second', 'seconds', 'interval'],
  ['mile', 'miles', 'race'], ['mile', 'miles', 'walk'], ['mile', 'miles', 'drive'],
  ['mile', 'miles', 'hike'], ['mile', 'miles', 'detour'], ['kilometre', 'kilometres', 'race'],
  ['kilometre', 'kilometres', 'drive'], ['kilometre', 'kilometres', 'walk'],
  ['kilometre', 'kilometres', 'cycle'], ['metre', 'metres', 'wall'], ['metre', 'metres', 'bridge'],
  ['metre', 'metres', 'rope'], ['metre', 'metres', 'drop'], ['foot', 'feet', 'wall'],
  ['foot', 'feet', 'fence'], ['foot', 'feet', 'rope'], ['foot', 'feet', 'drop'],
  ['inch', 'inches', 'gap'], ['inch', 'inches', 'pipe'], ['pound', 'pounds', 'loan'],
  ['pound', 'pounds', 'bill'], ['pound', 'pounds', 'fine'], ['dollar', 'dollars', 'loan'],
  ['dollar', 'dollars', 'bill'], ['dollar', 'dollars', 'fine'], ['euro', 'euros', 'bill'],
  ['euro', 'euros', 'loan'], ['ton', 'tons', 'load'], ['litre', 'litres', 'bottle'],
  ['litre', 'litres', 'tank'], ['page', 'pages', 'report'], ['page', 'pages', 'essay'],
  ['page', 'pages', 'letter'], ['word', 'words', 'essay'], ['word', 'words', 'summary'],
  ['word', 'words', 'note'], ['chapter', 'chapters', 'book'], ['chapter', 'chapters', 'thesis'],
  ['star', 'stars', 'hotel'], ['star', 'stars', 'restaurant'], ['door', 'doors', 'car'],
  ['door', 'doors', 'cabinet'], ['bedroom', 'bedrooms', 'house'], ['bedroom', 'bedrooms', 'flat'],
  ['storey', 'storeys', 'building'], ['storey', 'storeys', 'house'], ['room', 'rooms', 'flat'],
  ['room', 'rooms', 'house'], ['course', 'courses', 'meal'], ['term', 'terms', 'plan'],
  ['term', 'terms', 'project'], ['stage', 'stages', 'process'], ['seat', 'seats', 'car'],
  ['seat', 'seats', 'table'], ['hole', 'holes', 'belt'], ['gram', 'grams', 'packet'],
];

const NUMBERS = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'nine',
  'ten', 'twelve', 'fifteen', 'twenty', 'twenty-five', 'thirty', 'forty',
  'fifty', 'sixty', 'hundred'];

const M_FRAMES = {
  easy: [
    (bad, good, n, us, up) => [`They finally agreed on ${bad}.`, `They finally agreed on ${good}.`,
      `A number-plus-noun modifier keeps the unit singular: "${n}-${us}", not "${n}-${up}".`],
    (bad, good, n, us, up) => [`She carefully planned ${bad}.`, `She carefully planned ${good}.`,
      `The modifier "${n}-${us}" uses the singular "${us}", not "${up}".`],
  ],
  medium: [
    (bad, good, n, us, up) => [`After a long debate, the board approved ${bad} for the whole region.`,
      `After a long debate, the board approved ${good} for the whole region.`,
      `In the compound modifier the unit stays singular: "${n}-${us}".`],
    (bad, good, n, us, up) => [`Everyone praised ${bad} that the mayor had proposed.`,
      `Everyone praised ${good} that the mayor had proposed.`,
      `Compare "a ${n}-${up}" with the correct "a ${n}-${us}".`],
  ],
  hard: [
    (bad, good, n, us, up) => [`Although the critics doubted it, the council still approved ${bad} covering the entire province.`,
      `Although the critics doubted it, the council still approved ${good} covering the entire province.`,
      `Even in this long sentence the modifier keeps the singular unit: "${n}-${us}".`],
    (bad, good, n, us, up) => [`It was only after months of negotiation that the two sides finally signed ${bad}.`,
      `It was only after months of negotiation that the two sides finally signed ${good}.`,
      `A number-plus-noun modifier never pluralises its unit, so use "${n}-${us}".`],
    (bad, good, n, us, up) => [`The report, which nobody had expected, recommended ${bad} for the coming decade.`,
      `The report, which nobody had expected, recommended ${good} for the coming decade.`,
      `The embedded modifier keeps the unit singular: "${n}-${us}", not "${n}-${up}".`],
  ],
};

function nounModifier(d) {
  const nums = d === 'easy' ? NUMBERS.slice(0, 10)
    : d === 'medium' ? NUMBERS.slice(5, 15) : NUMBERS.slice(10);
  const frames = M_FRAMES[d];
  return pool40((i) => {
    const [us, up, head] = pick(TRIPLES, i);
    const n = pick(nums, i * 3 + 1);
    const good = `a ${n}-${us} ${head}`;
    const bad = `a ${n}-${up} ${head}`;
    const [b, g, explanation] = pick(frames, i)(bad, good, n, us, up);
    return mk(b, g, explanation);
  });
}

// ---- 4.3 Plural-only / singular -s nouns ---------------------------------
const PAIR = ['scissors', 'trousers', 'glasses', 'jeans', 'pants', 'shorts',
  'tights', 'pyjamas', 'goggles', 'sunglasses', 'binoculars', 'spectacles',
  'tongs', 'pliers', 'tweezers', 'shears', 'clippers'];

const NONPAIR = ['clothes', 'goods', 'thanks', 'savings', 'belongings',
  'outskirts', 'premises', 'valuables', 'congratulations', 'proceeds', 'arrears',
  'regards', 'remains', 'surroundings', 'earnings', 'groceries', 'wages',
  'riches', 'lodgings', 'fireworks', 'customs'];

const SING_S = ['news', 'mathematics', 'physics', 'economics', 'politics',
  'athletics', 'gymnastics', 'linguistics', 'statistics', 'billiards', 'measles',
  'mumps', 'rabies', 'series', 'species', 'draughts', 'dominoes', 'aesthetics',
  'genetics', 'logistics', 'mechanics', 'optics', 'ethics', 'civics', 'phonetics',
  'acoustics', 'dynamics', 'robotics'];

const PAIR_FRAMES = {
  easy: [
    (n) => [`A ${n} is on the desk.`, `A pair of ${n} is on the desk.`,
      `"${n}" is plural-only, so say "a pair of ${n}", not "a ${n}".`],
    (n) => [`She lost a ${n} yesterday.`, `She lost a pair of ${n} yesterday.`,
      `"${n}" has no singular form; use "a pair of ${n}".`],
  ],
  medium: [
    (n) => [`He bought a ${n} at the market.`, `He bought a pair of ${n} at the market.`,
      `"${n}" is always plural, so the unit is "a pair of ${n}".`],
    (n) => [`A ${n} was left on the bench.`, `A pair of ${n} was left on the bench.`,
      `For plural-only "${n}" say "a pair of ${n}".`],
  ],
  hard: [
    (n) => [`It was only after the long journey that he realised a ${n} was missing from his bag.`,
      `It was only after the long journey that he realised a pair of ${n} was missing from his bag.`,
      `Even here "${n}" needs the singular unit "a pair of ${n}".`],
    (n) => [`Although the toolbox looked full, the ${n} was nowhere to be seen.`,
      `Although the toolbox looked full, the ${n} were nowhere to be seen.`,
      `Plural-only "${n}" takes the plural verb "were".`],
  ],
};

const NONPAIR_FRAMES = {
  easy: [
    (n) => [`The ${n} is very useful.`, `The ${n} are very useful.`,
      `"${n}" is plural-only and takes the plural verb "are".`],
    (n) => [`This ${n} looks expensive.`, `These ${n} look expensive.`,
      `Plural-only "${n}" pairs with "these ... look".`],
  ],
  medium: [
    (n) => [`The ${n} from the sale was impressive.`, `The ${n} from the sale were impressive.`,
      `Plural-only "${n}" requires the plural verb "were".`],
    (n) => [`All the ${n} in the store was fresh.`, `All the ${n} in the store were fresh.`,
      `"${n}" is plural, so use "were", not "was".`],
  ],
  hard: [
    (n) => [`Because the ${n} stored in the warehouse was damaged, the shop ordered more.`,
      `Because the ${n} stored in the warehouse were damaged, the shop ordered more.`,
      `Plural-only "${n}" takes "were" even in this clause.`],
    (n) => [`Everyone was surprised that the ${n} from the auction was sold so quickly.`,
      `Everyone was surprised that the ${n} from the auction were sold so quickly.`,
      `"${n}" is plural, so the verb must be "were".`],
  ],
};

const SING_FRAMES = {
  easy: [
    (n) => [`The ${n} are interesting.`, `The ${n} is interesting.`,
      `"${n}" ends in -s but is singular and takes "is".`],
    (n) => [`These ${n} are surprising.`, `This ${n} is surprising.`,
      `Singular "${n}" takes "this ... is", not "these ... are".`],
  ],
  medium: [
    (n) => [`The ${n} were explained by the teacher.`, `The ${n} was explained by the teacher.`,
      `Although it looks plural, "${n}" is singular and takes "was".`],
    (n) => [`The ${n} in this course are demanding.`, `The ${n} in this course is demanding.`,
      `"${n}" is a singular subject, so use "is".`],
  ],
  hard: [
    (n) => [`The professor insisted that the ${n} were more reliable than anyone expected.`,
      `The professor insisted that the ${n} was more reliable than anyone expected.`,
      `Singular "${n}" takes "was" even in the reported clause.`],
    (n) => [`Nobody could explain why the ${n} were so difficult this term.`,
      `Nobody could explain why the ${n} was so difficult this term.`,
      `"${n}" is singular, so the verb is "was".`],
  ],
};

function pluralOnly(d) {
  const TYPES = ['pair', 'nonpair', 'sing'];
  const entries = { pair: PAIR, nonpair: NONPAIR, sing: SING_S };
  const framesets = {
    pair: PAIR_FRAMES[d], nonpair: NONPAIR_FRAMES[d], sing: SING_FRAMES[d],
  };
  return pool40((i) => {
    const t = pick(TYPES, i);
    const k = Math.floor(i / TYPES.length);
    const n = pick(entries[t], k);
    const [bad, good, explanation] = pick(framesets[t], k)(n);
    return mk(bad, good, explanation);
  });
}

export default {
  '4.1': countableUncountable,
  '4.2': nounModifier,
  '4.3': pluralOnly,
};
