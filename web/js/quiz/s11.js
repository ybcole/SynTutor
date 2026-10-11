// Section 11 — Meaning and usage. One builder per rule; 40 items per difficulty.
import {
  pick, mk, pool40, cartesian, cap, NOUNS, SG_SUBJ, PL_SUBJ, NAMES, VERBS,
  OBJECTS, TAILS_SIMPLE, TAILS_COMPLEX, CONNECTORS,
} from './core.js';

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

// Lower-case the first letter of a sentence unless it begins with "I" or a name.
function lcSent(s) {
  const first = s.split(' ')[0];
  if (first === 'I' || NAMES.includes(first)) return s;
  return s.charAt(0).toLowerCase() + s.slice(1);
}

// ===========================================================================
// 11.1 Confusable words — affect/effect, lose/loose
// ===========================================================================
const CONF = [
  ['effect', 'affect', 'The heavy rain will ~ the outdoor game'],
  ['affect', 'effect', 'The storm had a huge ~ on the village'],
  ['effect', 'affect', 'Smoking can ~ your health'],
  ['effect', 'affect', 'The new law will ~ every driver'],
  ['effect', 'affect', 'The news did not ~ her mood'],
  ['affect', 'effect', 'The ~ of the medicine was immediate'],
  ['affect', 'effect', 'They studied the ~ of the drought'],
  ['affect', 'effect', 'His advice had no ~ on me'],
  ['effect', 'affect', 'The teacher will ~ our final grade'],
  ['affect', 'effect', 'We measured the ~ of the new method'],
  ['effect', 'affect', 'Too much sugar can ~ your sleep'],
  ['affect', 'effect', 'The ~ of the reform was felt quickly'],
  ['loose', 'lose', 'Be careful not to ~ the tickets'],
  ['lose', 'loose', 'This jacket is much too ~'],
  ['loose', 'lose', 'We do not want to ~ the match'],
  ['lose', 'loose', 'A ~ screw caused the whole problem'],
  ['loose', 'lose', 'She is afraid to ~ her job'],
  ['lose', 'loose', 'The dog got ~ in the park'],
  ['loose', 'lose', 'Do not ~ your passport'],
  ['lose', 'loose', 'He wore a ~ shirt to the party'],
  ['loose', 'lose', 'Many firms will ~ money this year'],
  ['lose', 'loose', 'The old gate hung ~ on its hinges'],
  ['loose', 'lose', 'Nobody wants to ~ such a good friend'],
  ['lose', 'loose', 'Her hair hung ~ around her shoulders'],
];
const CONF_TAIL = {
  easy: ['', ' today', ' again'],
  medium: ['', ' this year', ' in the end', ' lately'],
  hard: ['', ' sooner or later', ' throughout the region', ' no matter what happens', ' after all'],
};

function confusableWords(d) {
  const tails = CONF_TAIL[d];
  return pool40((i) => {
    const [wrong, right, tmpl] = pick(CONF, i);
    const tail = pick(tails, Math.floor(i / CONF.length));
    return mk(
      `${cap(tmpl.replace('~', wrong))}${tail}.`,
      `${cap(tmpl.replace('~', right))}${tail}.`,
      `Use "${right}", not "${wrong}", in this sentence.`,
    );
  });
}

// ===========================================================================
// 11.2 Collocations — do a decision
// ===========================================================================
const COLL = [
  ['do', 'make', 'a decision about the project'],
  ['do', 'make', 'a serious mistake'],
  ['do', 'take', 'a photograph of the building'],
  ['do', 'make', 'good progress on the task'],
  ['make', 'take', 'a short break'],
  ['make', 'do', 'the homework before dinner'],
  ['do', 'make', 'a real effort to help'],
  ['make', 'take', 'a quick shower'],
  ['do', 'make', 'a promise to his mother'],
  ['make', 'do', 'the dishes after the meal'],
  ['do', 'make', 'an important phone call'],
  ['make', 'take', 'part in the competition'],
  ['do', 'make', 'friends at the new school'],
  ['make', 'take', 'a seat near the window'],
  ['make', 'do', 'some research on the topic'],
  ['do', 'make', 'a terrible mess in the kitchen'],
  ['make', 'take', 'full responsibility for the error'],
  ['do', 'make', 'an appointment with the doctor'],
  ['make', 'take', 'careful notes during the lecture'],
  ['make', 'do', 'a favour for a neighbour'],
  ['do', 'make', 'a wise choice'],
  ['make', 'take', 'a big risk'],
  ['do', 'make', 'business with the company'],
  ['do', 'make', 'a short speech'],
  ['make', 'take', 'good care of the garden'],
  ['make', 'do', 'a test on the new material'],
];
const COLL_SUBJ = ['She', 'He', 'Tom', 'Anna', 'We', 'They', 'My brother',
  'The manager', 'The students', 'The team'];
const COLL_FRAME = {
  easy: [
    (s, v, p) => `${s} had to ${v} ${p}.`,
    (s, v, p) => `${s} wanted to ${v} ${p}.`,
  ],
  medium: [
    (s, v, p) => `${s} had to ${v} ${p} before the meeting.`,
    (s, v, p) => `${s} finally decided to ${v} ${p}.`,
    (s, v, p) => `${s} was asked to ${v} ${p} yesterday.`,
  ],
  hard: [
    (s, v, p) => `Although everyone was busy, ${s} still had to ${v} ${p} before the deadline.`,
    (s, v, p) => `Because the situation was urgent, ${s} agreed to ${v} ${p} without further delay.`,
  ],
};

function collocations(d) {
  const frames = COLL_FRAME[d];
  const subs = d === 'easy' ? COLL_SUBJ.slice(0, 6) : COLL_SUBJ;
  const entries = d === 'easy' ? COLL.slice(0, 16) : COLL;
  return cartesian([frames, entries, subs], (f, [wrong, right, p], s) => mk(
    f(s, wrong, p), f(s, right, p),
    `The correct collocation is "${right} ${p}".`,
  ));
}

// ===========================================================================
// 11.3 Tense-time agreement — Yesterday I go
// ===========================================================================
const TT_VERBS = [
  ['went', 'goes', 'go', 'to school'],
  ['drove', 'drives', 'drive', 'to work'],
  ['ate', 'eats', 'eat', 'breakfast'],
  ['wrote', 'writes', 'write', 'a letter'],
  ['bought', 'buys', 'buy', 'a new car'],
  ['made', 'makes', 'make', 'a cake'],
  ['took', 'takes', 'take', 'the bus'],
  ['saw', 'sees', 'see', 'the film'],
  ['began', 'begins', 'begin', 'the lesson'],
  ['left', 'leaves', 'leave', 'the office'],
  ['came', 'comes', 'come', 'home'],
  ['did', 'does', 'do', 'the shopping'],
  ['met', 'meets', 'meet', 'her friend'],
  ['spoke', 'speaks', 'speak', 'to the class'],
  ['ran', 'runs', 'run', 'in the park'],
  ['gave', 'gives', 'give', 'a short talk'],
  ['found', 'finds', 'find', 'the missing key'],
  ['kept', 'keeps', 'keep', 'a daily diary'],
  ['sang', 'sings', 'sing', 'a familiar song'],
  ['taught', 'teaches', 'teach', 'the first lesson'],
];
const TT_SUBJ = ['she', 'he', 'Tom', 'Anna', 'my brother', 'the teacher', 'the manager'];
const TT_PAST_T = ['Yesterday', 'Last night', 'Last week', 'Two days ago', 'Last summer', 'This morning'];
const TT_PRES_T = ['Every day', 'Usually', 'On Mondays', 'These days', 'Every weekend'];
const TT_FUT_T = ['Tomorrow', 'Next week', 'Soon', 'Later today', 'Next month'];

function tenseAgreement(d) {
  const wrap = {
    easy: (T, S, clause) => `${cap(T)} ${S} ${clause}.`,
    medium: (T, S, clause) => `${cap(T)} ${S} ${clause} before the others arrived.`,
    hard: (T, S, clause) => `Even though the day was long, ${lcSent(cap(T))} ${S} ${clause} as usual.`,
  }[d];
  const past = cartesian([TT_PAST_T, TT_SUBJ, TT_VERBS], (T, S, [p, p3, b, rest]) => mk(
    wrap(T, S, `${p3} ${rest}`), wrap(T, S, `${p} ${rest}`),
    `The past-time word "${T}" needs the past tense "${p}".`));
  const pres = cartesian([TT_PRES_T, TT_SUBJ, TT_VERBS], (T, S, [p, p3, b, rest]) => mk(
    wrap(T, S, `${p} ${rest}`), wrap(T, S, `${p3} ${rest}`),
    `The present-time word "${T}" needs the present tense "${p3}".`));
  const fut = cartesian([TT_FUT_T, TT_SUBJ, TT_VERBS], (T, S, [p, p3, b, rest]) => mk(
    wrap(T, S, `${p} ${rest}`), wrap(T, S, `will ${b} ${rest}`),
    `The future-time word "${T}" needs "will ${b}".`));
  return firstN([...past.slice(0, 15), ...pres.slice(0, 15), ...fut.slice(0, 15)], 40);
}

// ===========================================================================
// 11.4 Selectional restrictions — The book eats
// ===========================================================================
const SEL = [
  ['The book ate the sandwich', 'The boy ate the sandwich', 'A book cannot eat; the subject must be animate.'],
  ['The table cooked the meal', 'The chef cooked the meal', 'A table cannot cook; the subject must be a person.'],
  ['The rock threw the stone', 'The child threw the stone', 'A rock cannot throw; the subject must be animate.'],
  ['The tree watered the plants', 'The gardener watered the plants', 'A tree cannot water; the subject must be a person.'],
  ['The car parked near the gate', 'The driver parked near the gate', 'A car cannot park itself; the subject must be a driver.'],
  ['The lamp switched on the light', 'The reader switched on the light', 'A lamp cannot switch itself on; the subject must be a person.'],
  ['The boat steered the ship', 'The sailor steered the ship', 'A boat cannot steer; the subject must be animate.'],
  ['The piano played the tune', 'The musician played the tune', 'A piano cannot play itself; the subject must be a musician.'],
  ['The clock repaired the engine', 'The mechanic repaired the engine', 'A clock cannot repair; the subject must be a person.'],
  ['The wind wrote the letter', 'The writer wrote the letter', 'The wind cannot write; the subject must be a person.'],
  ['The kennel barked at the stranger', 'The dog barked at the stranger', 'A kennel cannot bark; the subject must be an animal.'],
  ['The classroom answered the question', 'The student answered the question', 'A classroom cannot answer; the subject must be a person.'],
  ['The hammer drove the nail', 'The carpenter drove the nail', 'A hammer cannot act on its own; the subject must be a person.'],
  ['The garden grew the flowers', 'The gardener grew the flowers', 'A garden cannot grow flowers on purpose; the subject must be a person.'],
  ['The novel read the reader', 'The reader read the novel', 'The subject must be the person doing the reading.'],
  ['The sandwich ate the boy', 'The boy ate the sandwich', 'The subject must be the eater, not the food.'],
  ['The idea listened to the teacher', 'The student listened to the teacher', 'An idea cannot listen; the subject must be a person.'],
  ['The bread drank the milk', 'The baby drank the milk', 'Bread cannot drink; the subject must be animate.'],
  ['The picture watched the film', 'The audience watched the film', 'A picture cannot watch; the subject must be people.'],
  ['The music heard the song', 'The audience heard the song', 'Music cannot hear; the subject must be a listener.'],
  ['The boy ate the rock', 'The boy ate the sandwich', 'The object of "eat" must be edible.'],
  ['The baby drank the bread', 'The baby drank the milk', 'The object of "drink" must be a liquid.'],
  ['She read the song', 'She read the letter', 'The object of "read" must be something written.'],
  ['He listened to the picture', 'He listened to the music', 'The object of "listen to" must be something audible.'],
  ['They watered the idea', 'They watered the plants', 'The object of "water" must be a plant.'],
  ['She folded the ocean', 'She folded the blanket', 'The object of "fold" must be something foldable.'],
  ['He switched on the wind', 'He switched on the fan', 'The object of "switch on" must be a device.'],
  ['She cut the melody', 'She cut the paper', 'The object of "cut" must be something physical.'],
];
const SEL_PREFIX = {
  easy: ['', 'Yesterday, '],
  medium: ['Later that day, ', 'In the end, '],
  hard: ['Although nobody expected it, ', 'Despite everything, '],
};
const selFrame = (pre, c) => (pre ? `${pre}${lcSent(c)}.` : `${cap(c)}.`);

function selectional(d) {
  const pres = SEL_PREFIX[d];
  return pool40((i) => {
    const [bad, good, why] = pick(SEL, i);
    const pre = pick(pres, Math.floor(i / SEL.length));
    return mk(selFrame(pre, bad), selFrame(pre, good), why);
  });
}

// ===========================================================================
// 11.5 Structural ambiguity — PP-attachment
// ===========================================================================
const PP_SUBJ = ['The teacher', 'The scientist', 'The guard', 'My friend',
  'Anna', 'The hiker', 'The detective', 'The nurse'];
const PP_VERB = ['saw', 'watched', 'photographed', 'observed', 'studied',
  'examined', 'spotted'];
const PP_OBJ_TOOL = ['the man', 'the bird', 'the ship', 'the mountain',
  'the building', 'the car', 'the statue', 'the valley'];
const PP_TOOL = ['telescope', 'microscope', 'camera', 'binoculars', 'lantern',
  'ladder', 'map', 'compass'];
const PP_OBJ_PERSON = ['the man', 'the boy', 'the stranger', 'the visitor',
  'the girl', 'the guard', 'the hiker', 'the child'];
const PP_ATTR = ['hat', 'coat', 'stick', 'umbrella', 'scarf', 'beard', 'cane',
  'backpack', 'badge', 'necklace'];

function ppAttachment(d) {
  const badFrame = {
    easy: (s, v, o, n) => `${s} ${v} ${o} with the ${n}.`,
    medium: (s, v, o, n) => `${s} ${v} ${o} with the ${n} near the old gate.`,
    hard: (s, v, o, n) => `Although the light was poor, ${lcSent(s)} ${v} ${o} with the ${n} near the old gate.`,
  }[d];
  const goodA = {
    easy: (s, v, o, n) => `Using the ${n}, ${lcSent(s)} ${v} ${o}.`,
    medium: (s, v, o, n) => `Using the ${n}, ${lcSent(s)} ${v} ${o} near the old gate.`,
    hard: (s, v, o, n) => `Using the ${n}, ${lcSent(s)} ${v} ${o} near the old gate, although the light was poor.`,
  }[d];
  const goodB = {
    easy: (s, v, o, n) => `${s} ${v} ${o} who had the ${n}.`,
    medium: (s, v, o, n) => `${s} ${v} ${o} who had the ${n} nearby.`,
    hard: (s, v, o, n) => `${s} ${v} ${o} who, as it happened, was carrying the ${n}.`,
  }[d];
  const a = cartesian([PP_SUBJ, PP_VERB, PP_OBJ_TOOL, PP_TOOL], (s, v, o, n) => mk(
    badFrame(s, v, o, n), goodA(s, v, o, n),
    `"with the ${n}" is attached to the verb "${v}" as the instrument, not to "${o}".`), 200);
  const b = cartesian([PP_SUBJ, PP_VERB, PP_OBJ_PERSON, PP_ATTR], (s, v, o, n) => mk(
    badFrame(s, v, o, n), goodB(s, v, o, n),
    `"with the ${n}" is attached to "${o}", identifying which one, not to the verb "${v}".`), 200);
  return firstN([...a.slice(0, 20), ...b.slice(0, 20)], 40);
}

// ===========================================================================
// 11.6 Register — slang in formal writing
// ===========================================================================
const REG = [
  ['The report is gonna be late.', 'The report is going to be late.', 'gonna', 'going to'],
  ['We wanna finish the project today.', 'We want to finish the project today.', 'wanna', 'want to'],
  ['You gotta submit the form by Friday.', 'You have to submit the form by Friday.', 'gotta', 'have to'],
  ['The kids enjoyed the museum.', 'The children enjoyed the museum.', 'kids', 'children'],
  ['We discussed a lot of stuff.', 'We discussed a great deal of material.', 'stuff', 'material'],
  ['The guy at the desk was helpful.', 'The man at the desk was helpful.', 'guy', 'man'],
  ['The results were awesome.', 'The results were excellent.', 'awesome', 'excellent'],
  ['The proposal sounds cool.', 'The proposal sounds suitable.', 'cool', 'suitable'],
  ['The committee said yeah to the plan.', 'The committee said yes to the plan.', 'yeah', 'yes'],
  ['The sample was kinda small.', 'The sample was somewhat small.', 'kinda', 'somewhat'],
  ['The task was sorta difficult.', 'The task was somewhat difficult.', 'sorta', 'somewhat'],
  ['The theory ain\'t proven yet.', 'The theory is not proven yet.', 'ain\'t', 'is not'],
  ['The manager said y\'all should wait.', 'The manager said you all should wait.', 'y\'all', 'you all'],
  ['The student flunked the exam.', 'The student failed the exam.', 'flunked', 'failed'],
  ['The shop ripped off the customers.', 'The shop overcharged the customers.', 'ripped off', 'overcharged'],
  ['We hung out after the lecture.', 'We spent time together after the lecture.', 'hung out', 'spent time'],
  ['She crammed for the test all night.', 'She studied intensively for the test all night.', 'crammed', 'studied intensively'],
  ['I asked the boss for a raise.', 'I asked the manager for a raise.', 'boss', 'manager'],
  ['My mom works at the clinic.', 'My mother works at the clinic.', 'mom', 'mother'],
  ['My dad is a researcher.', 'My father is a researcher.', 'dad', 'father'],
  ['The film was super long.', 'The film was extremely long.', 'super', 'extremely'],
  ['The results were pretty clear.', 'The results were quite clear.', 'pretty', 'quite'],
  ['We read loads of articles.', 'We read numerous articles.', 'loads of', 'numerous'],
  ['She brought a bunch of samples.', 'She brought several samples.', 'a bunch of', 'several'],
  ['We left cuz it was late.', 'We left because it was late.', 'cuz', 'because'],
  ['Wait til the results arrive.', 'Wait until the results arrive.', 'til', 'until'],
  ['Tho the sample was small, it was clear.', 'Although the sample was small, it was clear.', 'tho', 'although'],
  ['We walked thru the lab.', 'We walked through the lab.', 'thru', 'through'],
  ['The party lasted all nite.', 'The party lasted all night.', 'nite', 'night'],
  ['He is a big shot in the firm.', 'He is a senior figure in the firm.', 'big shot', 'senior figure'],
];
const REG_PREFIX = {
  easy: ['', 'In the memo, '],
  medium: ['In the official summary, ', 'According to the draft, '],
  hard: ['In the report submitted to the committee, ', 'As the senior analyst observed, '],
};

function register(d) {
  const pres = REG_PREFIX[d];
  return pool40((i) => {
    const [bad, good, slang, formal] = pick(REG, i);
    const pre = pick(pres, Math.floor(i / REG.length));
    return mk(
      pre ? `${pre}${lcSent(bad)}` : bad,
      pre ? `${pre}${lcSent(good)}` : good,
      `"${slang}" is informal; in formal writing use "${formal}".`,
    );
  });
}

// ===========================================================================
// 11.7 L1 interference / false friends — I am agree
// ===========================================================================
const L1 = [
  ['I am agree with you.', 'I agree with you.', 'A full verb such as "agree" cannot take the verb "am".'],
  ['She is agree with the teacher.', 'She agrees with the teacher.', 'Do not add "is" before the verb "agree".'],
  ['We are agree on the plan.', 'We agree on the plan.', 'Do not add "are" before the verb "agree".'],
  ['They are agree about the price.', 'They agree about the price.', 'Do not add "are" before the verb "agree".'],
  ['He is agree that it is fair.', 'He agrees that it is fair.', 'Do not add "is" before the verb "agree".'],
  ['Tom is agree to help us.', 'Tom agrees to help us.', 'Do not add "is" before the verb "agree".'],
  ['I have twenty years old.', 'I am twenty years old.', 'Age in English uses "be", not "have".'],
  ['She has eighteen years old.', 'She is eighteen years old.', 'Age in English uses "be", not "have".'],
  ['He has thirty years old.', 'He is thirty years old.', 'Age in English uses "be", not "have".'],
  ['My brother has twenty-five years old.', 'My brother is twenty-five years old.', 'Age in English uses "be", not "have".'],
  ['I have hungry.', 'I am hungry.', 'States and feelings use "be", not "have".'],
  ['She has afraid of dogs.', 'She is afraid of dogs.', 'States and feelings use "be", not "have".'],
  ['They have cold.', 'They are cold.', 'States and feelings use "be", not "have".'],
  ['He has thirsty.', 'He is thirsty.', 'States and feelings use "be", not "have".'],
  ['I am interesting in physics.', 'I am interested in physics.', 'People feel "interested"; things are "interesting".'],
  ['She is interesting in art.', 'She is interested in art.', 'People feel "interested"; things are "interesting".'],
  ['He explained me the rule.', 'He explained the rule to me.', '"Explain" needs "to" before the listener.'],
  ['She recommended me a book.', 'She recommended a book to me.', '"Recommend" needs "to" before the listener.'],
  ['We are agree with the decision.', 'We agree with the decision.', 'Do not add "are" before the verb "agree".'],
  ['He is agree with my opinion.', 'He agrees with my opinion.', 'Do not add "is" before the verb "agree".'],
  ['I am agree to the proposal.', 'I agree to the proposal.', 'Do not add "am" before the verb "agree".'],
  ['He is married with her.', 'He is married to her.', '"Married" takes "to", not "with".'],
  ['She is married with a doctor.', 'She is married to a doctor.', '"Married" takes "to", not "with".'],
  ['I am boring in this class.', 'I am bored in this class.', 'People feel "bored"; things are "boring".'],
  ['We are boring with the lecture.', 'We are bored with the lecture.', 'People feel "bored"; things are "boring".'],
  ['I very like this book.', 'I really like this book.', 'English does not put "very" before a verb; use "really".'],
  ['She very likes music.', 'She really likes music.', 'English does not put "very" before a verb; use "really".'],
  ['I have a hunger.', 'I am hungry.', 'English uses the adjective "hungry", not "have a hunger".'],
  ['Open the light, please.', 'Turn on the light, please.', 'A light is turned on, not opened.'],
  ['Close the light, please.', 'Turn off the light, please.', 'A light is turned off, not closed.'],
];
const L1_PREFIX = {
  easy: ['', 'Personally, '],
  medium: ['In my opinion, ', 'As far as I know, '],
  hard: ['Although the details were complicated, ', 'After the long discussion, '],
};

function l1Interference(d) {
  const pres = L1_PREFIX[d];
  return pool40((i) => {
    const [bad, good, why] = pick(L1, i);
    const pre = pick(pres, Math.floor(i / L1.length));
    return mk(
      pre ? `${pre}${lcSent(bad)}` : bad,
      pre ? `${pre}${lcSent(good)}` : good,
      why,
    );
  });
}

// ===========================================================================
// 11.8 Connector misuse — I was tired, however I slept
// ===========================================================================
const RES_A = ['I was tired', 'She studied hard', 'The road was flooded',
  'He trained every day', 'It was raining', 'The test was easy',
  'He missed the bus', 'The soup was cold'];
const RES_B = ['I went to bed', 'she passed the exam', 'the match was cancelled',
  'he won the race', 'we took an umbrella', 'everyone passed',
  'he was late for work', 'she sent it back'];
const CON_A = ['She was tired', 'He is rich', 'The plan was risky',
  'The task was simple', 'He was exhausted'];
const CON_B = ['she kept working', 'he is unhappy', 'they approved it',
  'nobody finished it', 'he continued working'];

function connectorMisuse(d) {
  const badR = {
    easy: (A, B) => `${A}, however ${B}.`,
    medium: (A, B) => `${A}, however ${B} in the end.`,
    hard: (A, B) => `${A}, however ${B}, although nobody expected that outcome.`,
  }[d];
  const goodR = {
    easy: (A, B) => `${A}, so ${B}.`,
    medium: (A, B) => `${A}, so ${B} in the end.`,
    hard: (A, B) => `${A}, so ${B}, although nobody expected that outcome.`,
  }[d];
  const badC = {
    easy: (A, B) => `${A}, so ${B}.`,
    medium: (A, B) => `${A}, so ${B} in the end.`,
    hard: (A, B) => `${A}, so ${B}, although everyone had hoped otherwise.`,
  }[d];
  const goodC = {
    easy: (A, B) => `${A}, but ${B}.`,
    medium: (A, B) => `${A}, but ${B} in the end.`,
    hard: (A, B) => `${A}, but ${B}, although everyone had hoped otherwise.`,
  }[d];
  const res = cartesian([RES_A, RES_B], (A, B) => mk(
    badR(A, B), goodR(A, B),
    'The second clause gives a result, so use "so", not the contrastive "however".'), 80);
  const con = cartesian([CON_A, CON_B], (A, B) => mk(
    badC(A, B), goodC(A, B),
    'The second clause contrasts with the first, so use "but", not the result connector "so".'), 40);
  return firstN([...res.slice(0, 24), ...con.slice(0, 16)], 40);
}

export default {
  '11.1': confusableWords,
  '11.2': collocations,
  '11.3': tenseAgreement,
  '11.4': selectional,
  '11.5': ppAttachment,
  '11.6': register,
  '11.7': l1Interference,
  '11.8': connectorMisuse,
};
