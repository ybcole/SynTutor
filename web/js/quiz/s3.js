// Section 3 — Articles and determiners. One builder per rule; 40 items per tier.
import { pick, mk, pool40, NAMES } from './core.js';

// Cycle a pool against a frame list, re-using the index so long pools still
// yield 40 unique items. `make(item, frame, i)` returns a finished item.
const gen = (list, frames, make) => pool40((i) => {
  const item = pick(list, i);
  const f = pick(frames, Math.floor(i / list.length));
  return make(item, f, i);
});

// [noun, correct article] — 20 vowel-sound nouns then 20 consonant-sound nouns.
const A_POOL = [
  ['apple', 'an'], ['orange', 'an'], ['egg', 'an'], ['elephant', 'an'],
  ['umbrella', 'an'], ['hour', 'an'], ['idea', 'an'], ['owl', 'an'],
  ['ant', 'an'], ['artist', 'an'], ['engineer', 'an'], ['onion', 'an'],
  ['island', 'an'], ['eagle', 'an'], ['uncle', 'an'], ['old man', 'an'],
  ['honest boy', 'an'], ['expensive car', 'an'], ['interesting book', 'an'],
  ['easy test', 'an'],
  ['dog', 'a'], ['cat', 'a'], ['book', 'a'], ['car', 'a'],
  ['house', 'a'], ['table', 'a'], ['teacher', 'a'], ['doctor', 'a'],
  ['boy', 'a'], ['girl', 'a'], ['pen', 'a'], ['bag', 'a'],
  ['tree', 'a'], ['bike', 'a'], ['chair', 'a'], ['window', 'a'],
  ['door', 'a'], ['garden', 'a'], ['phone', 'a'], ['bird', 'a'],
];

// ---- 3.1 a / an choice ---------------------------------------------------
function aAn(d) {
  const nouns = d === 'easy' ? A_POOL : d === 'medium' ? A_POOL.slice(0, 20) : A_POOL.slice(20);
  const frames = {
    easy: [(p) => `She ate ${p}.`],
    medium: [
      (p) => `We noticed ${p} near the old gate.`,
      (p) => `He carried ${p} into the office.`,
    ],
    hard: [
      (p) => `Although it was getting late, we still managed to find ${p} beside the river.`,
      (p) => `The report claimed that she had bought ${p} just before the meeting began.`,
    ],
  }[d];
  return gen(nouns, frames, ([n, art], f) => mk(
    f(`${art === 'an' ? 'a' : 'an'} ${n}`),
    f(`${art} ${n}`),
    `"${n}" begins with a ${art === 'an' ? 'vowel' : 'consonant'} sound, so it takes "${art}".`,
  ));
}

// ---- 3.2 Missing article -------------------------------------------------
function missingArticle(d) {
  const nouns = d === 'easy' ? A_POOL : d === 'medium' ? A_POOL.slice(0, 20) : A_POOL.slice(20);
  const frames = {
    easy: [(p) => `I saw ${p}.`],
    medium: [
      (p) => `We found ${p} in the garden.`,
      (p) => `He bought ${p} yesterday.`,
    ],
    hard: [
      (p) => `Because the shop was closed, we could not buy ${p} on the way home.`,
      (p) => `She told me that she had seen ${p} near the station that morning.`,
    ],
  }[d];
  return gen(nouns, frames, ([n, art], f) => mk(
    f(n),
    f(`${art} ${n}`),
    `A singular countable noun needs an article: "${art} ${n}".`,
  ));
}

// ---- 3.3 Unnecessary article ---------------------------------------------
const SPORTS = ['football', 'tennis', 'basketball', 'chess', 'cricket', 'hockey',
  'badminton', 'baseball', 'volleyball', 'rugby', 'golf'];
const MEALS = ['breakfast', 'lunch', 'dinner', 'supper', 'brunch'];
const SUBJ3 = ['math', 'science', 'history', 'geography', 'chemistry', 'physics',
  'biology', 'music', 'art'];
const LANGS = ['English', 'French', 'Spanish', 'German'];
const VEHICLES = ['car', 'bus', 'train', 'bike', 'plane', 'boat', 'taxi', 'subway'];
const INSTS = ['bed', 'school', 'work', 'church', 'college', 'university'];
const UNNEC = [
  ...SPORTS.map((w) => ['play', `the ${w}`, w]),
  ...MEALS.map((w) => ['have', `the ${w}`, w]),
  ...SUBJ3.map((w) => ['study', `the ${w}`, w]),
  ...LANGS.map((w) => ['study', `the ${w}`, w]),
  ...VEHICLES.map((w) => ['by', `by the ${w}`, `by ${w}`]),
  ...INSTS.map((w) => ['go', `to the ${w}`, `to ${w}`]),
];
const UNNEC_FR = {
  play: {
    easy: { pre: (s) => `${s} plays `, post: ' every weekend.' },
    medium: { pre: (s) => `${s} plays `, post: ' with the local team after school.' },
    hard: {
      pre: (s) => `${s} has played `,
      post: [
        ' since childhood, despite several setbacks.',
        ' in the spring league for three consecutive years.',
        ' with the neighbourhood team since primary school.',
        ' at the local club whenever the season allows.',
        ' in several tournaments over the past decade.',
      ],
    },
  },
  have: {
    easy: { pre: (s) => `${s} has `, post: ' at seven.' },
    medium: { pre: (s) => `${s} has `, post: ' before the morning bus arrives.' },
    hard: { pre: (s) => `${s} has `, post: ' every morning before the long staff meeting begins.' },
  },
  study: {
    easy: { pre: (s) => `${s} studies `, post: ' at school.' },
    medium: { pre: (s) => `${s} studies `, post: ' with a private tutor after class.' },
    hard: { pre: (s) => `${s} has studied `, post: ' as part of a rather demanding university programme.' },
  },
  by: {
    easy: { pre: (s) => `${s} travels `, post: ' to work.' },
    medium: { pre: (s) => `${s} travels `, post: ' to the office every day.' },
    hard: { pre: (s) => `${s} travels `, post: ' to the distant office even when the roads are icy.' },
  },
  go: {
    easy: { pre: (s) => `${s} goes `, post: ' every morning.' },
    medium: { pre: (s) => `${s} goes `, post: ' before the sun rises.' },
    hard: { pre: (s) => `${s} goes `, post: ' whenever the old bell rings across the village.' },
  },
};
const UNNEC_WHY = {
  play: 'No article is used with games and sports.',
  have: 'No article is used with meals.',
  study: 'No article is used with school subjects and languages.',
  by: 'Means of transport with "by" take no article.',
  go: 'The institution noun takes no article in this idiom.',
};
function unnecessary(d) {
  const list = d === 'easy' ? UNNEC.slice(0, 40) : d === 'medium' ? UNNEC : UNNEC.slice(3, 43);
  const subjects = d === 'easy'
    ? ['She', 'He', 'Tom', 'Anna', 'My friend', 'The boy']
    : d === 'medium'
      ? ['Lucy', 'Ben', 'The teacher', 'My brother', 'The young doctor', ...NAMES.slice(0, 4)]
      : ['The new student', 'My older brother', 'The famous musician', 'The quiet librarian', 'The tired driver'];
  return pool40((i) => {
    const [kind, badObj, goodObj] = pick(list, i);
    const subj = pick(subjects, i);
    const fr = UNNEC_FR[kind][d];
    const post = Array.isArray(fr.post) ? pick(fr.post, i) : fr.post;
    return mk(fr.pre(subj) + badObj + post, fr.pre(subj) + goodObj + post, UNNEC_WHY[kind]);
  });
}

// ---- 3.4 Definite vs indefinite (first mention) --------------------------
function defIndef(d) {
  const nouns = d === 'easy' ? A_POOL : d === 'medium' ? A_POOL.slice(0, 20) : A_POOL.slice(20);
  const frames = {
    easy: [(p) => `I saw ${p} in the park.`],
    medium: [
      (p) => `We noticed ${p} near the old station.`,
      (p) => `He found ${p} behind the fence.`,
    ],
    hard: [
      (p) => `Because the streets were empty, she quickly noticed ${p} walking toward the river.`,
      (p) => `Although he had looked everywhere, he finally spotted ${p} waiting by the gate.`,
    ],
  }[d];
  return gen(nouns, frames, ([n, art], f) => mk(
    f(`the ${n}`),
    f(`${art} ${n}`),
    `On first mention, "${n}" is indefinite and takes "${art}", not "the".`,
  ));
}

// ---- 3.5 Stacked determiners ---------------------------------------------
const SG_N = ['book', 'letter', 'car', 'house', 'dog', 'table', 'phone', 'window',
  'garden', 'teacher', 'student', 'doctor', 'apple', 'orange', 'egg', 'umbrella',
  'island', 'engineer', 'painting', 'camera'];
const PL_N = ['books', 'letters', 'cars', 'houses', 'dogs', 'tables', 'phones',
  'windows', 'gardens', 'teachers', 'students', 'doctors', 'apples', 'oranges',
  'eggs', 'umbrellas', 'islands', 'engineers', 'paintings', 'cameras'];
const STACK = [
  ['sg', 'the my', 'my'], ['sg', 'a my', 'my'], ['sg', 'the your', 'your'], ['sg', 'a your', 'your'],
  ['sg', 'the his', 'his'], ['sg', 'the her', 'her'], ['sg', 'the our', 'our'], ['sg', 'the their', 'their'],
  ['sg', 'the its', 'its'], ['sg', 'a its', 'its'], ['sg', 'a this', 'this'], ['sg', 'the this', 'this'],
  ['sg', 'a that', 'that'], ['sg', 'the that', 'that'], ['sg', 'the each', 'each'], ['sg', 'a each', 'each'],
  ['sg', 'the every', 'every'], ['sg', 'a every', 'every'], ['sg', 'the no', 'no'], ['sg', 'a no', 'no'],
  ['pl', 'the these', 'these'], ['pl', 'the those', 'those'], ['pl', 'a these', 'these'], ['pl', 'a those', 'those'],
  ['pl', 'the some', 'some'], ['pl', 'my some', 'some'], ['pl', 'the any', 'any'], ['pl', 'their any', 'any'],
  ['pl', 'the many', 'many'], ['pl', 'the few', 'few'], ['pl', 'a many', 'many'], ['pl', 'the several', 'several'],
];
function stacked(d) {
  const frames = {
    easy: [(det, n) => `I read ${det} ${n} last night.`],
    medium: [
      (det, n) => `She put ${det} ${n} carefully on the desk.`,
      (det, n) => `We found ${det} ${n} behind the old door.`,
    ],
    hard: [
      (det, n) => `Although the room was tidy, someone had left ${det} ${n} lying on the floor.`,
      (det, n) => `The note explained that he had borrowed ${det} ${n} without asking anyone.`,
    ],
  }[d];
  return pool40((i) => {
    const [form, badDet, goodDet] = pick(STACK, i);
    const n = pick(form === 'sg' ? SG_N : PL_N, i * 3 + 1);
    const f = pick(frames, Math.floor(i / STACK.length));
    return mk(f(badDet, n), f(goodDet, n),
      `Only one central determiner is allowed; write "${goodDet} ${n}", not "${badDet} ${n}".`);
  });
}

// ---- 3.6 Determiner with no noun -----------------------------------------
const NOLESS = [
  ['poss', 'my', 'mine'], ['poss', 'your', 'yours'], ['poss', 'her', 'hers'],
  ['poss', 'our', 'ours'], ['poss', 'their', 'theirs'],
  ['art', 'a', 'one'], ['art', 'an', 'one'], ['art', 'the', 'it'],
];
const THINGS = ['This old book', 'That red car', 'The big house', 'This silver pen',
  'That warm coat', 'The small ticket', 'This blue umbrella', 'That wooden table',
  'The garden gate'];
const NOLESS_FR = {
  easy: [(x) => `I need ${x}.`, (x) => `She found ${x}.`, (x) => `They wanted ${x}.`],
  medium: [
    (x) => `Please bring ${x} to the office.`,
    (x) => `We ordered ${x} from the shop.`,
    (x) => `He packed ${x} for the journey.`,
  ],
  hard: [
    (x) => `Although nobody asked, he quietly took ${x} for himself.`,
    (x) => `The manager insisted that they should order ${x} before Friday.`,
    (x) => `Whenever the shop is busy, the assistant always recommends ${x}.`,
  ],
};
function determinerNoNoun(d) {
  const frames = NOLESS_FR[d];
  return pool40((i) => {
    const [kind, det, pron] = pick(NOLESS, i);
    const f = pick(frames, Math.floor(i / NOLESS.length));
    if (kind === 'poss') {
      const thing = pick(THINGS, i);
      return mk(`${thing} is ${det}.`, `${thing} is ${pron}.`,
        `"${det}" is a determiner and cannot stand alone; use the possessive pronoun "${pron}".`);
    }
    const phrase = pron === 'one' ? 'one' : 'it';
    return mk(f(`${det}.`), f(`${phrase}.`),
      `"${det}" cannot stand alone without a noun; use the pronoun "${phrase}".`);
  });
}

// ---- 3.7 some / any ------------------------------------------------------
const SOME_NOUNS = ['money', 'water', 'milk', 'bread', 'sugar', 'rice', 'time',
  'information', 'advice', 'homework', 'luck', 'patience', 'energy', 'food',
  'tea', 'coffee', 'cheese', 'paper', 'work', 'help', 'books', 'apples',
  'friends', 'tickets', 'letters', 'pens', 'eggs', 'chairs', 'oranges', 'biscuits'];
const SA_FRAMES = {
  easy: [
    (n) => mk(`I don't have some ${n}.`, `I don't have any ${n}.`, 'After a negative, use "any".'),
    (n) => mk(`We didn't buy some ${n}.`, `We didn't buy any ${n}.`, 'After a negative, use "any".'),
  ],
  medium: [
    (n) => mk(`Do you have some ${n}?`, `Do you have any ${n}?`, 'In questions, use "any".'),
    (n) => mk(`Did she need some ${n}?`, `Did she need any ${n}?`, 'In questions, use "any".'),
    (n) => mk(`He bought any ${n} yesterday.`, `He bought some ${n} yesterday.`, 'In an affirmative statement, use "some".'),
  ],
  hard: [
    (n) => mk(`She said that she didn't have some ${n} for the trip.`,
      `She said that she didn't have any ${n} for the trip.`, 'The negation still takes "any".'),
    (n) => mk(`Although he searched everywhere, he could not find some ${n}.`,
      `Although he searched everywhere, he could not find any ${n}.`, 'After "could not", use "any".'),
    (n) => mk(`We unexpectedly received any ${n} from the office.`,
      `We unexpectedly received some ${n} from the office.`, 'In an affirmative statement, use "some".'),
  ],
};
function someAny(d) {
  const nouns = d === 'easy' ? SOME_NOUNS.slice(0, 20)
    : d === 'medium' ? SOME_NOUNS.slice(0, 20) : SOME_NOUNS.slice(0, 14);
  const frames = SA_FRAMES[d];
  return pool40((i) => {
    const n = pick(nouns, i);
    const f = pick(frames, Math.floor(i / nouns.length));
    return f(n);
  });
}

// ---- 3.8 each / every / all / whole / other / another --------------------
const QUANT_FIX = [
  ['another books', 'another book'], ['another pens', 'another pen'],
  ['another cars', 'another car'], ['another apples', 'another apple'],
  ['another tickets', 'another ticket'], ['another chairs', 'another chair'],
  ['another phones', 'another phone'], ['another bags', 'another bag'],
  ['another eggs', 'another egg'], ['another oranges', 'another orange'],
  ['every books', 'every book'], ['every pens', 'every pen'],
  ['every cars', 'every car'], ['every apples', 'every apple'],
  ['every tickets', 'every ticket'], ['every chairs', 'every chair'],
  ['every phones', 'every phone'], ['every bags', 'every bag'],
  ['every eggs', 'every egg'], ['every oranges', 'every orange'],
  ['each books', 'each book'], ['each pens', 'each pen'],
  ['each cars', 'each car'], ['each apples', 'each apple'],
  ['each tickets', 'each ticket'], ['each chairs', 'each chair'],
  ['each phones', 'each phone'], ['each bags', 'each bag'],
  ['each eggs', 'each egg'], ['each oranges', 'each orange'],
  ['all book', 'all books'], ['all pen', 'all pens'], ['all car', 'all cars'],
  ['all apple', 'all apples'], ['all ticket', 'all tickets'],
  ['other book', 'other books'], ['other pen', 'other pens'],
  ['other car', 'other cars'], ['other apple', 'other apples'],
  ['the whole books', 'all the books'], ['the whole cars', 'all the cars'],
  ['the whole money', 'all the money'], ['the whole water', 'all the water'],
  ['the all books', 'all the books'], ['the all money', 'all the money'],
  ['every of the tickets', 'each of the tickets'], ['each of book', 'each of the books'],
  ['the others books', 'the other books'],
];
function quantReason(bad) {
  if (/^another/.test(bad)) return '"another" takes a singular noun.';
  if (/^every of/.test(bad)) return 'Use "each of the" before a plural noun.';
  if (/^every/.test(bad)) return '"every" takes a singular noun.';
  if (/^each of/.test(bad)) return '"each of" is followed by "the" and a plural noun.';
  if (/^each/.test(bad)) return '"each" takes a singular noun.';
  if (/^all/.test(bad)) return '"all" takes a plural noun.';
  if (/^other/.test(bad)) return '"other" before a plural noun stays "other".';
  if (/^the whole/.test(bad)) return '"whole" is not used with plurals or uncountables; use "all the".';
  if (/^the all/.test(bad)) return 'The quantifier "all" comes before "the".';
  if (/^the others/.test(bad)) return 'Write "the other" before a plural noun.';
  return 'Choose the correct quantifier.';
}
function quantifiers(d) {
  const list = d === 'easy' ? QUANT_FIX.slice(0, 40)
    : d === 'medium' ? QUANT_FIX.slice(4, 48) : QUANT_FIX.slice(8, 48);
  const frames = {
    easy: [(p) => `She bought ${p}.`, (p) => `He wanted ${p}.`],
    medium: [
      (p) => `The teacher asked for ${p} before the bell rang.`,
      (p) => `We noticed ${p} near the old gate.`,
    ],
    hard: [
      (p) => `Although the list was long, the clerk still needed ${p} before closing time.`,
      (p) => `The report explained why the manager had ordered ${p} at the last minute.`,
    ],
  }[d];
  return gen(list, frames, ([bad, good], f) => mk(f(bad), f(good), quantReason(bad)));
}

export default {
  '3.1': aAn,
  '3.2': missingArticle,
  '3.3': unnecessary,
  '3.4': defIndef,
  '3.5': stacked,
  '3.6': determinerNoNoun,
  '3.7': someAny,
  '3.8': quantifiers,
};
