// Section 10 — Punctuation and orthography. One builder per rule; 40 items/tier.
import {
  pick, mk, pool40, cartesian, cap, NOUNS, SG_SUBJ, PL_SUBJ, NAMES, VERBS,
  OBJECTS, TAILS_SIMPLE, TAILS_COMPLEX,
} from './core.js';

const lc = (s) => (s.charAt(0).toLowerCase() + s.slice(1));
const capWord = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s);

// Keep the first `n` de-duplicated, well-formed items.
function firstN(list, n = 40) {
  const out = [];
  const seen = new Set();
  for (const it of list) {
    if (!it || !it.bad || !it.good || it.bad === it.good) continue;
    const key = `${it.bad}||${it.good}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(it);
    if (out.length >= n) break;
  }
  return out;
}

const SUBJ = ['The boy', 'The girl', 'The man', 'The woman', 'The child',
  'The teacher', 'The student', 'The doctor', 'The driver', 'The farmer',
  'The nurse', 'The worker', 'The player', 'My brother', 'My sister',
  'My friend', 'Tom', 'Anna', 'Sam', 'Lucy', 'Ben', 'Mia', 'Jack', 'Zoe'];
const V3 = ['walks', 'runs', 'talks', 'smiles', 'works', 'waits', 'stands',
  'sits', 'plays', 'reads', 'writes', 'cooks', 'cleans', 'paints', 'sings',
  'dances', 'studies', 'listens', 'watches', 'opens'];
const VTR = ['reads', 'writes', 'opens', 'cleans', 'paints', 'cooks', 'watches',
  'carries', 'moves', 'uses', 'closes', 'fixes', 'picks'];
const ADV = ['quickly', 'slowly', 'quietly', 'carefully', 'happily', 'politely',
  'suddenly', 'gently', 'busily', 'loudly'];

// ===========================================================================
// 10.1 Sentence-initial capital (the boy runs)
// ===========================================================================
function capitalInitial(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(SUBJ, i);
      const v = pick(V3, i + 5);
      const t = pick(TAILS_SIMPLE, Math.floor(i / SUBJ.length));
      return mk(`${lc(s)} ${v} ${t}.`, `${s} ${v} ${t}.`,
        'Every sentence begins with a capital letter.');
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(SUBJ, i);
      const adv = pick(ADV, i + 3);
      const v = pick(VTR, i + 7);
      const o = pick(OBJECTS, Math.floor(i / SUBJ.length));
      const t = pick(TAILS_SIMPLE, i + 11);
      return mk(`${lc(s)} ${adv} ${v} ${o} ${t}.`, `${s} ${adv} ${v} ${o} ${t}.`,
        'Start the sentence with a capital letter.');
    });
  }
  return pool40((i) => {
    const s = pick(SUBJ, i);
    const v = pick(VTR, i + 1);
    const o = pick(OBJECTS, i + 6);
    const t = pick(TAILS_COMPLEX, i + 5);
    const s2 = pick(SUBJ, i + 4);
    const v2 = pick(VTR, i + 9);
    const o2 = pick(OBJECTS, i + 13);
    const body = `${s} ${v} ${o} ${t} and ${lc(s2)} ${v2} ${o2}.`;
    return mk(lc(body), body, 'The first word of the sentence must be capitalised.');
  });
}

// ===========================================================================
// 10.2 Proper nouns, "I", days, months
// ===========================================================================
const NAMES_LC = ['tom', 'anna', 'sam', 'lucy', 'ben', 'mia', 'jack', 'zoe',
  'omar', 'sara', 'paul', 'nina', 'kai', 'rita', 'raj', 'dana', 'ivan', 'lena'];
const DAYS_LC = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday',
  'saturday', 'sunday'];
const MONTHS_LC = ['january', 'february', 'march', 'april', 'may', 'june',
  'july', 'august', 'september', 'october', 'november', 'december'];
const PLACES_LC = ['london', 'paris', 'berlin', 'madrid', 'tokyo', 'cairo',
  'rome', 'venice'];
const LANGS_LC = ['english', 'spanish', 'french', 'german', 'italian', 'arabic'];

const NAME_FR = [
  (w) => `I met ${w} at the station.`,
  (w) => `She called ${w} this morning.`,
  (w) => `We visited ${w} last summer.`,
];
const DAY_FR = [
  (w) => `We have a meeting on ${w}.`,
  (w) => `The shop is closed on ${w}.`,
  (w) => `She arrived late on ${w}.`,
];
const MONTH_FR = [
  (w) => `Her birthday is in ${w}.`,
  (w) => `The course begins in ${w}.`,
  (w) => `It often snows here in ${w}.`,
];
const PLACE_FR = [
  (w) => `He moved to ${w} last year.`,
  (w) => `They travelled to ${w} by train.`,
  (w) => `The conference was held in ${w}.`,
];
const LANG_FR = [
  (w) => `She speaks ${w} fluently.`,
  (w) => `He is studying ${w} at school.`,
  (w) => `We listened to a talk in ${w}.`,
];
const I_FR = [
  (w) => `She told me that ${w} was right.`,
  (w) => `My friend said that ${w} should stay.`,
  (w) => `Nobody knew whether ${w} had finished.`,
];

function properGroup(words, frames) {
  return cartesian([frames, words], (f, w) => mk(f(w), f(capWord(w)),
    'Proper nouns, days, months, languages and the pronoun "I" take a capital.'));
}

function properNouns(d) {
  if (d === 'easy') {
    return firstN(properGroup(NAMES_LC, NAME_FR), 40);
  }
  if (d === 'medium') {
    return firstN([
      ...properGroup(DAYS_LC, DAY_FR.slice(0, 2)),
      ...properGroup(MONTHS_LC, MONTH_FR.slice(0, 2)),
      ...properGroup(LANGS_LC, LANG_FR.slice(0, 2)),
      ...properGroup(['i'], I_FR),
    ], 40);
  }
  const frameA = (n, p, m, dy) => mk(
    `${n} flew to ${p} in ${m} on ${dy}.`,
    `${capWord(n)} flew to ${capWord(p)} in ${capWord(m)} on ${capWord(dy)}.`,
    'Capitalise every proper noun, month and day.');
  const a = cartesian([MONTHS_LC, DAYS_LC, PLACES_LC, NAMES_LC], frameA, 30);
  const frameB = (n, p, lg) => mk(
    `${n} studied ${lg} in ${p} last year.`,
    `${capWord(n)} studied ${capWord(lg)} in ${capWord(p)} last year.`,
    'Names, languages and places are proper nouns and take capitals.');
  const b = cartesian([LANGS_LC, PLACES_LC, NAMES_LC], frameB, 20);
  return firstN([...a, ...b], 40);
}

// ===========================================================================
// 10.3 Terminal punctuation (missing full stop / question mark)
// ===========================================================================
const QUESTIONS = [
  'Where is the station', 'Where is the library', 'Where is the bank',
  'Where is the post office', 'What is your name', 'What time is it',
  'When does the film start', 'Why are you late', 'Is the door open',
  'Are the windows closed', 'Has the train left', 'Can you help me',
  'Did she call you', 'Will they arrive soon', 'Do you like tea',
  'Have you finished', 'Whose bag is this', 'How far is the village',
];
const QUESTIONS_M = [
  'Where can I find the nearest pharmacy', 'When will the new library open',
  'Why was the meeting postponed', 'How long does the journey take',
  'Do you know where the keys are', 'Have they finished the report yet',
  'Will the results be announced today', 'Is there a bus after midnight',
];
const QUESTIONS_H = [
  'Where exactly did you leave the documents before the meeting began',
  'Why had nobody warned the committee about the sudden change',
  'How many applications were actually reviewed before the deadline',
  'Do you honestly believe the story he told everyone at dinner',
  'When was the last time the whole team met face to face',
];

function terminal(d) {
  const qs = d === 'easy' ? QUESTIONS
    : d === 'medium' ? [...QUESTIONS, ...QUESTIONS_M]
      : [...QUESTIONS_M, ...QUESTIONS_H];
  const qItems = qs.map((q) => mk(q, `${q}?`,
    'A direct question ends with a question mark.'));
  if (d === 'easy') {
    const stmts = cartesian([TAILS_SIMPLE, V3, SUBJ], (t, vv, ss) => mk(
      `${ss} ${vv} ${t}`, `${ss} ${vv} ${t}.`, 'A statement ends with a full stop.'));
    return firstN([...qItems, ...stmts], 40);
  }
  if (d === 'medium') {
    const stmts = cartesian([TAILS_SIMPLE, VTR, SUBJ, OBJECTS], (t, vv, ss, o) => mk(
      `${ss} ${vv} ${o} ${t}`, `${ss} ${vv} ${o} ${t}.`,
      'A statement ends with a full stop.'));
    return firstN([...qItems, ...stmts], 40);
  }
  const stmts = cartesian([TAILS_COMPLEX, VTR, SUBJ, OBJECTS], (t, vv, ss, o) => mk(
    `${ss} ${vv} ${o} ${t}`, `${ss} ${vv} ${o} ${t}.`,
    'A statement ends with a full stop.'));
  return firstN([...qItems, ...stmts], 40);
}

// ===========================================================================
// 10.4 Commas (series, introductory, clauses)
// ===========================================================================
const SER_ITEMS = ['apples', 'oranges', 'pears', 'bananas', 'grapes', 'plums',
  'figs', 'dates', 'carrots', 'peas', 'beans', 'onions', 'tomatoes',
  'potatoes', 'rolls', 'buns', 'cakes', 'tarts', 'nuts', 'berries'];
const SER_WHO = ['She', 'He', 'Tom', 'Anna', 'We', 'They', 'My brother'];
const SER_VERB = ['bought', 'packed', 'chose', 'ordered', 'brought', 'collected'];

function seriesItems() {
  return pool40((i) => {
    const a = pick(SER_ITEMS, i);
    const b = pick(SER_ITEMS, i + 7);
    const c = pick(SER_ITEMS, i + 13);
    if (a === b || b === c || a === c) return null;
    const who = pick(SER_WHO, i + 3);
    const vb = pick(SER_VERB, i + 5);
    return mk(`${who} ${vb} ${a} ${b} and ${c}.`,
      `${who} ${vb} ${a}, ${b}, and ${c}.`,
      'Separate the items in a series with commas.');
  });
}

const INTRO_PH = ['After lunch', 'Before dinner', 'In the morning',
  'On Monday', 'Last night', 'During the lesson', 'After the meeting',
  'In the garden', 'Before the storm', 'At noon', 'Every weekend',
  'On Friday evening', 'Later that day', 'After the break', 'In the end'];
const MAIN_CLAUSES = ['we went home', 'she called her mother',
  'they finished the report', 'the rain stopped', 'the children played outside',
  'everyone left the office', 'I read the letter', 'the bus arrived',
  'we started cooking', 'he apologised', 'the guests sat down',
  'the lights came on', 'we packed the car', 'she paid the bill'];

function introItems() {
  return pool40((i) => {
    const ph = pick(INTRO_PH, i);
    const cl = pick(MAIN_CLAUSES, Math.floor(i / INTRO_PH.length));
    return mk(`${ph} ${cl}.`, `${ph}, ${cl}.`,
      'Use a comma after an introductory phrase.');
  });
}

const SUBORD = ['Although it was raining', 'When the bell rang',
  'Because the traffic was heavy', 'If you finish early',
  'While we were waiting', 'Since she had studied hard',
  'After the guests left', 'Before the meeting began',
  'Unless the plan changes', 'Though nobody expected it',
  'Once the work is done', 'Whenever the phone rings'];
const CLAUSE_MAIN = ['we decided to stay in', 'she hurried to class',
  'we arrived late', 'call me', 'we waited by the gate',
  'she passed the exam', 'we cleaned up', 'we reviewed the notes',
  'we will go ahead', 'everyone was surprised', 'you may leave',
  'I answer it'];

function clauseItems() {
  return pool40((i) => {
    const sub = pick(SUBORD, i);
    const cl = pick(CLAUSE_MAIN, Math.floor(i / SUBORD.length));
    return mk(`${sub} ${cl}.`, `${sub}, ${cl}.`,
      'Use a comma after a fronted dependent clause.');
  });
}

const APPOS = [
  ['My brother', 'a doctor', 'lives in London'],
  ['Anna', 'our new colleague', 'starts on Monday'],
  ['The old house', 'a former school', 'was finally sold'],
  ['Mr Reed', 'our English teacher', 'retired last year'],
  ['The bridge', 'an impressive structure', 'was closed for repairs'],
  ['Her car', 'a small red model', 'barely fits the garage'],
  ['The manager', 'a patient man', 'listened to everyone'],
  ['The novel', 'a bestseller', 'was translated into ten languages'],
];

function apposItems() {
  return firstN(APPOS.map(([s, ap, rest]) => mk(
    `${s} ${ap} ${rest}.`, `${s}, ${ap}, ${rest}.`,
    'Enclose a non-restrictive appositive in commas.')), 40);
}

function commas(d) {
  if (d === 'easy') {
    return firstN([...seriesItems().slice(0, 25), ...introItems().slice(0, 20)], 40);
  }
  if (d === 'medium') {
    return firstN([...introItems().slice(0, 16), ...clauseItems().slice(0, 16),
      ...seriesItems().slice(0, 16)], 40);
  }
  return firstN([...clauseItems().slice(0, 16), ...apposItems().slice(0, 16),
    ...seriesItems().slice(0, 16)], 40);
}

// ===========================================================================
// 10.5 Apostrophes (the 1990's)
// ===========================================================================
const DECADES = ['1910', '1920', '1930', '1940', '1950', '1960', '1970',
  '1980', '1990', '2000', '2010', '2020'];
const DEC_FR = [
  (w) => `Fashion changed a lot during the ${w}.`,
  (w) => `She was born in the ${w}.`,
  (w) => `The ${w} were a difficult decade.`,
  (w) => `Music from the ${w} still sounds good.`,
];

function decadeItems() {
  return cartesian([DEC_FR, DECADES], (f, x) => mk(f(`${x}'s`), f(`${x}s`),
    'Decades are written as plain plurals: 1990s, not 1990\'s.'));
}

const POSS_NAMES = ['tom', 'anna', 'sam', 'lucy', 'ben', 'mia', 'jack', 'zoe',
  'omar', 'sara', 'paul', 'nina', 'emma', 'noah', 'liam', 'ella', 'ava',
  'leo', 'max', 'ruby'];
const POSS_FR = [
  (w) => `I borrowed ${w} bicycle.`,
  (w) => `This is ${w} favourite book.`,
  (w) => `We admired ${w} new house.`,
  (w) => `Have you seen ${w} report?`,
];

function singularPoss() {
  return cartesian([POSS_FR, POSS_NAMES], (f, n) => mk(
    f(`${capWord(n)}s`), f(`${capWord(n)}'s`),
    `A singular possessive takes an apostrophe before the s: ${capWord(n)}'s.`));
}

const POSS_PL = ['students', 'teachers', 'workers', 'players', 'drivers',
  'farmers', 'nurses', 'doctors', 'friends', 'neighbours', 'owners',
  'members', 'parents', 'readers', 'writers', 'singers', 'dancers',
  'actors', 'builders', 'bakers'];
const POSS_PL_FR = [
  (w) => `The ${w}'s work was praised.`,
  (w) => `We enjoyed the ${w}'s performance.`,
  (w) => `All the ${w}'s tools were missing.`,
  (w) => `The ${w}'s union called a meeting.`,
];

function pluralPoss() {
  return cartesian([POSS_PL_FR, POSS_PL], (f, w) => mk(
    f(w), f(w).replace(`${w}'s`, `${w}'`),
    'A plural possessive ending in s takes the apostrophe after the s.'));
}

function apostrophes(d) {
  if (d === 'easy') {
    return firstN(decadeItems(), 40);
  }
  if (d === 'medium') {
    return firstN([...decadeItems().slice(0, 20), ...singularPoss().slice(0, 24)], 40);
  }
  return firstN([...pluralPoss().slice(0, 20), ...singularPoss().slice(0, 16),
    ...decadeItems().slice(0, 16)], 40);
}

// ===========================================================================
// 10.6 Quotation and dialogue (mismatched marks)
// ===========================================================================
const QUOTE_INNER = ['I am tired', 'The bus is late', 'We should go now',
  'It is raining hard', 'I will be there soon', 'She has already left',
  'The meeting starts at nine', 'I cannot find my keys', 'This is my seat',
  'You were right', 'I finished the report', 'The food was delicious',
  'He forgot the tickets', 'They arrived yesterday', 'The shop is closed'];

function quoteItems(d) {
  const inners = d === 'easy' ? QUOTE_INNER.slice(0, 9)
    : d === 'medium' ? QUOTE_INNER.slice(0, 13) : QUOTE_INNER;
  const subs = d === 'easy' ? ['He', 'She', 'Tom']
    : d === 'medium' ? ['He', 'She', 'Tom', 'Anna', 'My father']
      : ['He', 'She', 'Tom', 'Anna', 'My father', 'The teacher', 'The manager'];
  const items = [];
  for (const q of inners) {
    for (const s of subs) {
      items.push(mk(`${s} said, "${q}.`, `${s} said, "${q}."`,
        'A quotation needs a closing quotation mark.'));
      items.push(mk(`${s} said, ${q}."`, `${s} said, "${q}."`,
        'A quotation needs an opening quotation mark.'));
      items.push(mk(`${s} said, '${q}."`, `${s} said, "${q}."`,
        'Use matching quotation marks around a quotation.'));
      items.push(mk(`"${q}." ${s} said.`, `"${q}," ${s} said.`,
        'A comma separates a quotation from its reporting clause.'));
    }
  }
  return firstN(items, 40);
}

// ===========================================================================
// 10.7 Hyphens and dashes (a well known author)
// ===========================================================================
const HYPH = [
  ['well known', 'well-known', 'author'],
  ['five year old', 'five-year-old', 'child'],
  ['state of the art', 'state-of-the-art', 'equipment'],
  ['long term', 'long-term', 'plan'],
  ['high speed', 'high-speed', 'train'],
  ['full time', 'full-time', 'worker'],
  ['part time', 'part-time', 'student'],
  ['up to date', 'up-to-date', 'record'],
  ['out of date', 'out-of-date', 'map'],
  ['world famous', 'world-famous', 'singer'],
  ['award winning', 'award-winning', 'film'],
  ['record breaking', 'record-breaking', 'run'],
  ['self made', 'self-made', 'millionaire'],
  ['well behaved', 'well-behaved', 'dog'],
  ['ten minute', 'ten-minute', 'break'],
  ['two hour', 'two-hour', 'meeting'],
  ['three day', 'three-day', 'trip'],
  ['one way', 'one-way', 'street'],
  ['first class', 'first-class', 'ticket'],
  ['last minute', 'last-minute', 'change'],
  ['high quality', 'high-quality', 'product'],
  ['low cost', 'low-cost', 'option'],
  ['old fashioned', 'old-fashioned', 'house'],
  ['mouth watering', 'mouth-watering', 'dish'],
  ['fully furnished', 'fully-furnished', 'flat'],
];

function hyphens(d) {
  const frames = d === 'easy'
    ? [(m, n) => `She rented a ${m} ${n}.`, (m, n) => `It was a ${m} ${n}.`]
    : d === 'medium'
      ? [(m, n) => `They published a ${m} ${n} for the project.`,
        (m, n) => `He bought a ${m} ${n} at the fair.`]
      : [(m, n) => `Although critics disagreed at first, it remained a ${m} ${n} for years.`,
        (m, n) => `The committee finally approved the ${m} ${n} after a long debate.`];
  return cartesian([frames, HYPH], (f, [bad, good, noun]) => mk(
    f(bad, noun), f(good, noun),
    'A compound modifier before a noun is joined with hyphens.'));
}

// ===========================================================================
// 10.8 Colons and semicolons (misuse)
// ===========================================================================
const LIST_HEADS = [
  ['The recipe needs', ['flour', 'eggs', 'sugar']],
  ['The basket contained', ['sandwiches', 'fruit', 'juice']],
  ['She bought', ['bread', 'milk', 'cheese']],
  ['The team needed', ['a keeper', 'a defender', 'a striker']],
  ['He packed', ['a shirt', 'trousers', 'a jacket']],
  ['We ordered', ['soup', 'salad', 'pasta']],
  ['The kit includes', ['a brush', 'a roller', 'a tray']],
  ['The garden has', ['roses', 'tulips', 'daisies']],
  ['The bag held', ['keys', 'a wallet', 'a phone']],
  ['The shelf displayed', ['novels', 'poems', 'essays']],
];
const LIST_TAIL = ['', ' for the trip', ' for the party', ' this morning', ' last week'];

function colonListItems() {
  return pool40((i) => {
    const [head, items] = pick(LIST_HEADS, i);
    const tail = pick(LIST_TAIL, Math.floor(i / LIST_HEADS.length));
    const joined = `${items[0]}, ${items[1]} and ${items[2]}`;
    return mk(`${head}, ${joined}${tail}.`, `${head}: ${joined}${tail}.`,
      'Use a colon to introduce a list.');
  });
}

const IND_A = ['It was getting late', 'The traffic was heavy',
  'She had studied hard', 'The shop was closed', 'The storm grew worse',
  'He had forgotten his notes', 'The train was delayed', 'Everyone was tired'];
const IND_B = ['we decided to go home', 'we took a different route',
  'she passed the exam', 'we ordered online', 'we stayed indoors',
  'he borrowed mine', 'we missed the connection', 'we left early'];

function semiItems() {
  return cartesian([IND_B, IND_A], (b, a) => mk(
    `${a}, ${b}.`, `${a}; ${b}.`,
    'Join two independent clauses with a semicolon, not a comma.'));
}

const CONN = ['however', 'therefore', 'moreover', 'nevertheless',
  'consequently', 'otherwise'];

function connItems() {
  return cartesian([CONN, IND_B, IND_A], (c, b, a) => mk(
    `${a}, ${c}, ${b}.`, `${a}; ${c}, ${b}.`,
    'Use a semicolon before a conjunctive adverb joining two clauses.'));
}

function colonMisuseItems() {
  return cartesian([IND_B, IND_A], (b, a) => mk(
    `${a}: ${b}.`, `${a}; ${b}.`,
    'A colon does not join two independent clauses; use a semicolon.'));
}

function colons(d) {
  if (d === 'easy') {
    return firstN([...colonListItems().slice(0, 22), ...semiItems().slice(0, 20)], 40);
  }
  if (d === 'medium') {
    return firstN([...semiItems().slice(0, 18), ...colonListItems().slice(0, 16),
      ...connItems().slice(0, 12)], 40);
  }
  return firstN([...colonMisuseItems().slice(0, 14), ...connItems().slice(0, 14),
    ...semiItems().slice(0, 14)], 40);
}

// ===========================================================================
// 10.9 Spacing and repeats (the the, space before comma)
// ===========================================================================
const DUP_SENTENCES = [
  'She went to the market.', 'He put the book on the table.',
  'We saw the film and enjoyed the show.', 'The cat sat on the old mat.',
  'They walked to the park after lunch.', 'I think that the plan will work.',
  'He said that he was very tired.', 'We had had enough of the noise.',
  'She told me that that was wrong.', 'The teacher gave the class the test.',
  'We travelled to the coast in the summer.', 'He is the one that I trust.',
  'They arrived at the station on time.', 'She put the keys in the drawer.',
  'We need to buy a gift for the party.', 'The report is on the desk in the office.',
  'He asked whether the shop was open.', 'I believe that the story is true.',
];
const DUP_WORDS = ['the', 'to', 'and', 'that', 'had', 'is', 'a', 'of', 'in', 'on'];

function repeatItems() {
  return pool40((i) => {
    const s = pick(DUP_SENTENCES, i);
    const tokens = s.split(' ');
    const cands = tokens.map((w, idx) => ({ w, idx }))
      .filter((x) => DUP_WORDS.includes(x.w.toLowerCase().replace(/[.,?]/g, '')));
    if (!cands.length) return null;
    const { w, idx } = pick(cands, i + 2);
    const bad = `${tokens.slice(0, idx + 1).join(' ')} ${w} ${tokens.slice(idx + 1).join(' ')}`;
    return mk(bad, s, 'A word has been accidentally repeated; delete the extra copy.');
  });
}

const COMMA_SENTS = [
  'She bought bread, milk and eggs.', 'We visited Rome, Paris and Berlin.',
  'The meal was hot, fresh and tasty.', 'He packed shirts, socks and shoes.',
  'They planted roses, tulips and daisies.', 'I need paper, pens and ink.',
  'She invited Tom, Anna and Sam.', 'We saw lions, tigers and bears.',
  'The box held nails, screws and bolts.', 'He chose red, blue and green.',
  'The shop sells tea, coffee and cake.', 'We met Ben, Lucy and Mia.',
];
const PERIOD_SENTS = [
  'It is late.', 'The door is open.', 'She is ready.', 'The bus has left.',
  'He works here.', 'They arrived early.', 'The soup is hot.',
  'We are waiting.', 'The film was long.', 'She called again.',
  'The room is clean.', 'It will rain.',
];
const TWO_SENTS = [
  ['It was late.', 'We went home.'], ['The bell rang.', 'The children left.'],
  ['The sun set.', 'The air grew cold.'], ['She waved.', 'He drove away.'],
  ['The kettle boiled.', 'She made tea.'], ['The train stopped.', 'We got off.'],
  ['It started raining.', 'We ran inside.'], ['The lights failed.', 'The room went dark.'],
];

function spacingItems(d) {
  const before = COMMA_SENTS.map((s) => mk(s.replace(',', ' ,'), s,
    'Do not leave a space before a comma.'));
  const after = COMMA_SENTS.map((s) => mk(s.replace(', ', ','), s,
    'Leave a space after a comma.'));
  const per = PERIOD_SENTS.map((s) => mk(`${s.slice(0, -1)} .`, s,
    'Do not leave a space before a full stop.'));
  const double = PERIOD_SENTS.map((s) => mk(s.replace(' ', '  '), s,
    'Use a single space between words.'));
  const join = TWO_SENTS.map(([a, b]) => mk(`${a}${b}`, `${a} ${b}`,
    'Leave a space after a full stop before the next sentence.'));
  const reps = repeatItems();
  if (d === 'easy') {
    return firstN([...reps.slice(0, 12), ...before.slice(0, 10),
      ...per.slice(0, 10), ...double.slice(0, 8)], 40);
  }
  if (d === 'medium') {
    return firstN([...after.slice(0, 12), ...before.slice(0, 10),
      ...reps.slice(0, 10), ...per.slice(0, 8)], 40);
  }
  return firstN([...join.slice(0, 8), ...after.slice(0, 12),
    ...before.slice(0, 10), ...reps.slice(0, 10)], 40);
}

// ===========================================================================
// 10.10 Numbers, dates and abbreviations (inconsistent format)
// ===========================================================================
const TITLES = ['Mr', 'Mrs', 'Ms', 'Dr', 'Prof', 'Capt', 'Sgt'];
const SURNAMES = ['Smith', 'Jones', 'Brown', 'Taylor', 'Wilson', 'Clark',
  'Hall', 'Young', 'King', 'Wright'];
const TITLE_FR = [
  (t, s) => `I spoke to ${t} ${s} yesterday.`,
  (t, s) => `We invited ${t} ${s} to dinner.`,
  (t, s) => `Did you see ${t} ${s} at the office?`,
];

function titleItems() {
  return cartesian([TITLE_FR, TITLES, SURNAMES], (f, t, s) => mk(
    f(t, s), f(`${t}.`, s),
    'Abbreviated titles take a full stop: Mr., Dr., Prof.'));
}

const TIMES = [['7', 'am'], ['8', 'am'], ['9', 'am'], ['10', 'am'],
  ['6', 'pm'], ['7', 'pm'], ['8', 'pm'], ['9', 'pm']];
const TIME_FR = [
  (h, m) => `The train leaves at ${h} ${m}.`,
  (h, m) => `The film starts at ${h} ${m}.`,
];

function timeItems() {
  return cartesian([TIME_FR, TIMES], (f, [h, m]) => mk(
    f(h, m), f(h, `${m[0]}.${m[1]}.`),
    'Time expressions take full stops: a.m., p.m.'));
}

const NUMBERS = [1000, 2500, 5000, 10000, 15000, 25000, 50000, 75000,
  100000, 225000, 500000, 1000000];
const NUM_FR = [
  (n) => `The company earned ${n} dollars last year.`,
  (n) => `The city spent ${n} on repairs.`,
];

function numberItems() {
  return cartesian([NUM_FR, NUMBERS], (f, n) => mk(
    f(`${n}`), f(n.toLocaleString('en-US')),
    'Separate large numbers with commas in groups of three.'));
}

const DATES = [['January', '5'], ['March', '3'], ['June', '12'], ['August', '7'],
  ['October', '19'], ['December', '25'], ['February', '14'], ['April', '9']];
const DATE_FR = [
  (m, d) => `The appointment is on ${m} ${d} 2024.`,
  (m, d) => `She was born on ${m} ${d} 1990.`,
];

function dateItems() {
  return cartesian([DATE_FR, DATES], (f, [m, d]) => mk(
    f(m, d), f(m, `${d},`),
    'Use a comma between the day and the year in a date.'));
}

const ABBR_PAIRS = [
  ['We brought pencils and notebooks,@@', 'etc'],
  ['Many students, @@ the top ones, passed.', 'e.g'],
  ['The meeting, @@ it was urgent, began early.', 'i.e'],
  ['City A @@ City B held a debate.', 'vs'],
];
const ABBR_TAIL = ['', ' in the end', ' last week'];

function abbrItems() {
  return pool40((i) => {
    const [tmpl, word] = pick(ABBR_PAIRS, i);
    const tail = pick(ABBR_TAIL, Math.floor(i / ABBR_PAIRS.length));
    return mk(`${tmpl.replace('@@', word)}${tail}`,
      `${tmpl.replace('@@', `${word}.`)}${tail}`,
      `The abbreviation "${word}" takes a full stop: "${word}."`);
  });
}

function numbers(d) {
  if (d === 'easy') {
    return firstN([...titleItems().slice(0, 20), ...timeItems().slice(0, 10),
      ...numberItems().slice(0, 10)], 40);
  }
  if (d === 'medium') {
    return firstN([...numberItems().slice(0, 14), ...dateItems().slice(0, 12),
      ...timeItems().slice(0, 8), ...abbrItems().slice(0, 6)], 40);
  }
  return firstN([...dateItems().slice(0, 12), ...numberItems().slice(0, 10),
    ...abbrItems().slice(0, 8), ...titleItems().slice(0, 10)], 40);
}

export default {
  '10.1': capitalInitial,
  '10.2': properNouns,
  '10.3': terminal,
  '10.4': commas,
  '10.5': apostrophes,
  '10.6': quoteItems,
  '10.7': hyphens,
  '10.8': colons,
  '10.9': spacingItems,
  '10.10': numbers,
};
