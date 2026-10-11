// Section 9 — Sentence structure. One builder per rule; 40 items per tier.
import {
  pick, mk, pool40, cartesian, cap, withPeriod, NOUNS,
} from './core.js';

// Lowercase a leading word but never touch the pronoun "I".
const lc = (s) => (s === 'I' || s.startsWith('I ') ? s : s.charAt(0).toLowerCase() + s.slice(1));
const art = (w) => (/^[aeiou]/i.test(w) ? 'an' : 'a');

const S3 = ['She', 'He', 'Tom', 'Anna', 'The boy', 'The girl', 'My friend',
  'The teacher', 'The child', 'The dog'];

// ---- 9.1 Fragment (Because I was late.) ----------------------------------
const SUBS = ['Because', 'Although', 'When', 'If', 'While', 'Since', 'Before',
  'Until', 'Unless', 'After', 'Though', 'As', 'Whenever', 'Whereas', 'Once',
  'Even though', 'As soon as', 'In case', 'Now that', 'Provided that'];
const DCLAUSE_E = ['I was late', 'it was raining', 'the bell rang', 'you finish early',
  'we were waiting', 'she had left', 'the guests arrived', 'the work is done',
  'we hurry', 'the film ended', 'he apologized', 'she called', 'it snows', 'nobody noticed'];
const DCLAUSE_M = ['the meeting had already started', 'the shops were still closed',
  'the traffic was unusually heavy', 'she had studied for weeks', 'the weather suddenly changed',
  'everyone had gone home', 'the train was delayed again', 'he had forgotten his notes',
  'the lights went out briefly', 'the children were playing outside', 'the report needed more work',
  'the phone kept ringing'];
const DCLAUSE_H = ['the committee had finally approved the new proposal',
  'she had been waiting at the station for over an hour',
  'the storm that everyone had feared finally arrived',
  'the results were announced after a long and tense delay',
  'he had already made up his mind about the offer',
  'the building had stood empty for many years',
  'they had been arguing about the same problem all evening',
  'the manuscript had been rejected by three publishers'];
const MAIN_E = ['I went home', 'we stayed inside', 'she called me', 'they left early'];
const MAIN_M = ['I still managed to finish the report', 'we decided to wait by the gate',
  'the whole team kept working quietly', 'she never mentioned it again'];
const MAIN_H = ['I could not help thinking about what might have been',
  'we had no choice but to postpone the meeting until Monday',
  'the committee eventually agreed to review every application again',
  'she realised that nobody had warned her about the change'];

function fragment(d) {
  const clauses = d === 'easy' ? DCLAUSE_E : d === 'medium' ? DCLAUSE_M : DCLAUSE_H;
  const mains = d === 'easy' ? MAIN_E : d === 'medium' ? MAIN_M : MAIN_H;
  return cartesian([mains, clauses, SUBS], (main, cl, sub) => mk(
    withPeriod(`${sub} ${cl}`),
    withPeriod(`${sub} ${cl}, ${main}`),
    'A dependent clause cannot stand alone; attach it to an independent clause.'));
}

// ---- 9.2 Missing subject (Went to school.) -------------------------------
const PREDS_9_2 = ['went to school', 'visited the museum', 'finished the homework',
  'cleaned the kitchen', 'watered the garden', 'read the letter', 'bought a new car',
  'watched a film', 'cooked dinner', 'painted the fence', 'washed the dishes',
  'planted a tree', 'answered the phone', 'opened the window', 'locked the door',
  'walked to the station', 'borrowed a book', 'fixed the bicycle', 'sang a song',
  'wrote a report', 'packed the bags', 'checked the tickets', 'lost the keys', 'found the wallet'];
const SUBJ_9_2 = ['She', 'He', 'Tom', 'Anna', 'They', 'We', 'You', 'I', 'The boy',
  'The girl', 'My friend', 'The teacher', 'The students', 'The children', 'My parents',
  'The workers'];
const TAIL_9_2 = {
  easy: ['', ' again', ' yesterday'],
  medium: [' before the meeting', ' after lunch', ' on Saturday morning'],
  hard: [' just before the storm broke', ' while everyone else was still asleep',
    ' as soon as the results were announced', ' long before the deadline'],
};

function missingSubject(d) {
  return cartesian([TAIL_9_2[d], SUBJ_9_2, PREDS_9_2], (tail, subj, pred) => {
    const p = `${pred}${tail}`;
    return mk(withPeriod(cap(p)), withPeriod(`${subj} ${p}`),
      'Every sentence needs an explicit subject before the verb.');
  });
}

// ---- 9.3 Run-on / fused (I like tea she likes coffee) --------------------
const IND = ['I like tea', 'she likes coffee', 'it was raining', 'we stayed inside',
  'the dog barked', 'the baby cried', 'Tom plays football', 'Anna reads novels',
  'they arrived late', 'the train was crowded', 'I finished my work', 'he forgot his keys',
  'the sun was shining', 'the wind felt cold', 'my phone died', 'the meeting ended early',
  'she smiled warmly', 'the children were laughing', 'we missed the bus', 'the shop was closed',
  'he called his mother', 'the kettle boiled', 'I found my wallet', 'the lights went out',
  'the guests had arrived', 'the traffic was heavy', 'the band started playing',
  'the soup tasted good', 'our team won', 'the clock struck twelve'];
const JOIN = ['and', 'but', 'so'];
const TAIL_ON = {
  easy: [''],
  medium: [' that evening', ' before lunch'],
  hard: [' before the guests finally arrived', ' just as the storm was breaking'],
};

function runOn(d) {
  const pool = d === 'easy' ? IND.slice(0, 16) : d === 'medium' ? IND.slice(6, 24) : IND;
  return cartesian([TAIL_ON[d], JOIN, pool, pool], (tail, j, b, a) => {
    if (a === b) return null;
    return mk(
      withPeriod(`${cap(a)} ${lc(b)}${tail}`),
      withPeriod(`${cap(a)}, ${j} ${lc(b)}${tail}`),
      'Two independent clauses need a conjunction or a full stop, not just juxtaposition.');
  });
}

// ---- 9.4 Comma splice (I came, I saw.) -----------------------------------
function commaSplice(d) {
  const pool = d === 'easy' ? IND.slice(0, 16) : d === 'medium' ? IND.slice(6, 24) : IND;
  return cartesian([TAIL_ON[d], JOIN, pool, pool], (tail, j, b, a) => {
    if (a === b) return null;
    return mk(
      withPeriod(`${cap(a)}, ${lc(b)}${tail}`),
      `${cap(a)}. ${cap(b)}${tail}.`,
      'A comma alone cannot join two independent clauses; use a full stop or a conjunction.');
  });
}

// ---- 9.5 Double subject (My brother he...) -------------------------------
const DS_SUBJ = [['My brother', 'he'], ['My sister', 'she'], ['Tom', 'he'], ['Anna', 'she'],
  ['The boy', 'he'], ['The girl', 'she'], ['My father', 'he'], ['My mother', 'she'],
  ['The teacher', 'he'], ['The students', 'they'], ['My friends', 'they'],
  ['The children', 'they'], ['The dog', 'it'], ['The car', 'it'], ['The workers', 'they'],
  ['Mr Khan', 'he'], ['Mrs Lee', 'she'], ['The manager', 'he'], ['The neighbours', 'they'],
  ['My uncle', 'he'], ['My aunt', 'she'], ['The cat', 'it'], ['The players', 'they'],
  ['The driver', 'he']];
const DS_PRED = ['went home', 'finished the race', 'bought a new phone', 'arrived late',
  'cleaned the room', 'read the newspaper', 'won the prize', 'left early',
  'started the engine', 'answered the question', 'cooked dinner', 'repaired the fence'];
const TAIL_9_5 = {
  easy: [''],
  medium: [' quietly', ' yesterday afternoon', ' without a word'],
  hard: [' as soon as the bell rang', ' although nobody had asked them to',
    ' before the long meeting finally began'],
};

function doubleSubject(d) {
  return cartesian([TAIL_9_5[d], DS_PRED, DS_SUBJ], (tail, pred, [sub, pro]) => mk(
    withPeriod(`${sub} ${pro} ${pred}${tail}`),
    withPeriod(`${sub} ${pred}${tail}`),
    'The subject is stated twice; drop the extra pronoun.'));
}

// ---- 9.6 Word order in statements (Yesterday went I) ---------------------
const WO_ADV = ['Yesterday', 'Last week', 'This morning', 'After lunch', 'In the evening',
  'On Monday', 'Last night', 'In the afternoon'];
const WO_VERB = ['went', 'came', 'left', 'arrived', 'played', 'worked', 'studied', 'walked',
  'returned', 'ran'];
const WO_SUBJ = ['I', 'she', 'he', 'Tom', 'Anna', 'they', 'we', 'the boys', 'my friends',
  'the students'];
const WO_REST = ['to the market', 'home', 'to school', 'by the gate', 'to the office',
  'to the park', 'to the station', 'to the library'];

function wordOrder(d) {
  const adv = d === 'easy' ? WO_ADV.slice(0, 4) : WO_ADV;
  const rest = d === 'easy' ? WO_REST.slice(0, 4) : d === 'medium' ? WO_REST.slice(2, 7) : WO_REST;
  return cartesian([adv, rest, WO_SUBJ, WO_VERB], (a, r, s, v) => mk(
    withPeriod(`${a} ${v} ${s} ${r}`),
    withPeriod(`${a} ${s} ${v} ${r}`),
    'In a statement the subject comes before the verb, even after a fronted time phrase.'));
}

// ---- 9.7 Missing or extra word (She is very the happy) -------------------
const ME_ADV = ['very', 'really', 'quite', 'extremely'];
const ME_ADJ = ['happy', 'tall', 'smart', 'clean', 'bright', 'careful', 'quiet', 'strong',
  'gentle', 'patient', 'polite', 'honest'];
const ME_BIGADJ = ['expensive', 'beautiful', 'interesting', 'comfortable', 'modern',
  'important', 'popular', 'dangerous', 'delicious'];

function missingExtraWord(d) {
  const s3 = d === 'easy' ? S3.slice(0, 6) : S3;
  const extra = cartesian([s3, ME_ADV, ME_ADJ], (s, a, adj) => mk(
    withPeriod(`${s} is ${a} the ${adj}`),
    withPeriod(`${s} is ${a} ${adj}`),
    'The word "the" is extra here; a bare adjective takes no determiner.'), 20);
  const nouns = NOUNS.slice(0, d === 'easy' ? 12 : 24).map(([sg]) => sg);
  const missing = cartesian([s3, ME_BIGADJ, nouns], (s, adj, n) => mk(
    withPeriod(`${s} bought ${adj} ${n}`),
    withPeriod(`${s} bought ${art(adj)} ${adj} ${n}`),
    'The article "a" or "an" is missing before the singular count noun.'), 20);
  return [...extra, ...missing];
}

// ---- 9.8 Parallel structure (to run, swimming) ---------------------------
const GER = [['swim', 'swimming'], ['read', 'reading'], ['sing', 'singing'],
  ['dance', 'dancing'], ['cook', 'cooking'], ['paint', 'painting'], ['write', 'writing'],
  ['run', 'running'], ['draw', 'drawing'], ['travel', 'travelling'], ['hike', 'hiking'],
  ['cycle', 'cycling'], ['fish', 'fishing'], ['garden', 'gardening'], ['sketch', 'sketching'],
  ['jog', 'jogging'], ['drive', 'driving'], ['bake', 'baking'], ['climb', 'climbing'],
  ['photograph', 'photographing']];

function parallel(d) {
  const s3 = d === 'easy' ? S3.slice(0, 5) : S3;
  return cartesian([GER, GER, GER, s3], ([, g1], [b2, g2], [, g3], s) => {
    if (g1 === g2 || g2 === g3 || g1 === g3) return null;
    return mk(
      withPeriod(`${s} enjoys ${g1}, to ${b2} and ${g3}`),
      withPeriod(`${s} enjoys ${g1}, ${g2} and ${g3}`),
      'List items must be parallel; after "enjoys" use gerunds throughout, not a to-infinitive.');
  }, 40);
}

// ---- 9.9 Conjunction pairing (Although..., but...) -----------------------
const CNJ_SUBS = ['Although', 'Though', 'Because', 'Since', 'While', 'Even though', 'Whereas'];
const CNJ_C1 = ['it was raining hard', 'she had studied for weeks', 'the traffic was terrible',
  'he was very tired', 'the shop was closed', 'the exam was difficult', 'the weather turned cold',
  'they had little money', 'the train was late', 'she felt unwell', 'the road was icy',
  'the team played well', 'the price was high', 'the room was small', 'he spoke quietly',
  'the plan seemed risky'];
const CNJ_C2 = ['we decided to go out', 'she still felt nervous', 'we arrived on time',
  'he finished the report', 'we found another one', 'she passed with ease', 'we stayed indoors',
  'they helped each other', 'we missed the connection', 'she came anyway', 'he drove carefully',
  'they lost the match', 'we bought it anyway', 'we made it work', 'everyone listened',
  'we went ahead'];

function conjunctionPairing(d) {
  const c1 = d === 'easy' ? CNJ_C1.slice(0, 8) : CNJ_C1;
  const c2 = d === 'easy' ? CNJ_C2.slice(0, 8) : CNJ_C2;
  const subs = d === 'easy' ? CNJ_SUBS.slice(0, 4) : CNJ_SUBS;
  return cartesian([subs, c1, c2], (sub, a, b) => {
    const conj = sub === 'Because' || sub === 'Since' ? 'so' : 'but';
    return mk(
      withPeriod(`${sub} ${a}, ${conj} ${b}`),
      withPeriod(`${sub} ${a}, ${b}`),
      `"${sub} ... ${conj} ..." pairs two conjunctions; keep only one.`);
  });
}

// ---- 9.10 Relative clause formation (the man who I saw him) --------------
const RC_NOUNS = [['man', 'him'], ['woman', 'her'], ['boy', 'him'], ['girl', 'her'],
  ['teacher', 'him'], ['doctor', 'her'], ['students', 'them'], ['children', 'them'],
  ['friends', 'them'], ['dog', 'it'], ['house', 'it'], ['book', 'it'], ['car', 'it'],
  ['painting', 'it'], ['neighbours', 'them'], ['player', 'him'], ['singer', 'her'],
  ['workers', 'them'], ['cat', 'it'], ['village', 'it']];
const RC_VERBS = ['saw', 'met', 'called', 'visited', 'helped', 'photographed', 'interviewed',
  'thanked', 'recognised', 'greeted'];
const RC_TAIL = {
  easy: ['yesterday', 'last week'],
  medium: ['at the station', 'during the meeting', 'outside the office'],
  hard: ['while I was waiting for the delayed train', 'just before the results were announced'],
};
const RC_CLOSE = ['was very kind', 'worked in our office', 'lived next door',
  'seemed quite friendly', 'had moved away'];

function relativeClause(d) {
  return cartesian([RC_VERBS, RC_TAIL[d], RC_CLOSE, RC_NOUNS],
    (v, tail, cl, [noun, pro]) => mk(
      withPeriod(`The ${noun} that I ${v} ${pro} ${tail} ${cl}`),
      withPeriod(`The ${noun} that I ${v} ${tail} ${cl}`),
      'A relative clause must not repeat the object with a pronoun.'));
}

// ---- 9.11 Dangling / misplaced modifier (Walking home, ...) --------------
const DM_MOD = ['Walking home', 'Running to catch the bus', 'Reading the letter',
  'Opening the window', 'Climbing the steep hill', 'Waiting for the train',
  'Looking out of the window', 'Sitting in the garden', 'Driving to work', 'Finishing the report',
  'Climbing the ladder', 'Looking at the map', 'Cleaning the kitchen', 'Listening to the radio',
  'Standing at the door', 'Chopping the vegetables'];
const DM_CLAUSE = {
  easy: ['the rain started', 'the trees looked beautiful', 'the phone rang', 'the sky turned dark'],
  medium: ['the bus finally arrived', 'the wind grew stronger', 'the lights went out',
    'the door creaked open', 'dinner was ready'],
  hard: ['the fire alarms sounded across the whole building',
    'the music from the hall could be heard for miles',
    'the train was already pulling out of the station',
    'the guests began to arrive one after another'],
};

function danglingModifier(d) {
  const mods = DM_MOD;
  return cartesian([mods, DM_CLAUSE[d]], (m, cl) => mk(
    `${m}, ${cl}.`,
    `As I was ${lc(m)}, ${cl}.`,
    'The participial phrase describes the subject of the main clause; reword with "As I was ...".'));
}

// ---- 9.12 Redundancy (return back) ---------------------------------------
const RED = [
  ['returned back to the office', 'returned to the office'],
  ['repeated the point again', 'repeated the point'],
  ['introduced a new innovation', 'introduced an innovation'],
  ['moved forward ahead', 'moved ahead'],
  ['sat in close proximity', 'sat nearby'],
  ['discussed the end result', 'discussed the result'],
  ['reviewed the past history', 'reviewed the history'],
  ['gave a free gift', 'gave a gift'],
  ['had an unexpected surprise', 'had a surprise'],
  ['joined together the two parts', 'joined the two parts'],
  ['merged together the teams', 'merged the teams'],
  ['combined together the results', 'combined the results'],
  ['reverted back to the old plan', 'reverted to the old plan'],
  ['ascended up the stairs', 'ascended the stairs'],
  ['descended down the hill', 'descended the hill'],
  ['cooperated together on the task', 'cooperated on the task'],
  ['collaborated together on the project', 'collaborated on the project'],
  ['wrote a brief summary', 'wrote a summary'],
  ['announced the final outcome', 'announced the outcome'],
  ['received an added bonus', 'received a bonus'],
  ['explained the basic fundamentals', 'explained the fundamentals'],
  ['used the exact same method', 'used the same method'],
  ['planned ahead for the trip', 'planned for the trip'],
  ['postponed until later the meeting', 'postponed the meeting'],
  ['circulated around the room', 'circulated in the room'],
  ['showed mutual cooperation', 'showed cooperation'],
  ['examined it with close scrutiny', 'examined it'],
  ['filled it to capacity', 'filled it'],
  ['chose a tiny little house', 'chose a tiny house'],
  ['checked each and every item', 'checked every item'],
  ['asked first and foremost for help', 'asked for help'],
  ['declared the contract null and void', 'declared the contract void'],
  ['kept the money safe and sound', 'kept the money safe'],
  ['sang it over and over again', 'sang it again'],
  ['offered various different options', 'offered different options'],
  ['completely eliminated the error', 'eliminated the error'],
  ['completely destroyed the evidence', 'destroyed the evidence'],
  ['claimed it was totally unique', 'claimed it was unique'],
  ['said it still remains a mystery', 'said it remains a mystery'],
  ['rose up quickly', 'rose quickly'],
];
const RED_SUBJ = ['She', 'He', 'Tom', 'Anna', 'They', 'We', 'The team', 'My friend',
  'The manager', 'The workers'];
const TAIL_9_12 = {
  easy: [''],
  medium: [' before lunch', ' after the meeting', ' without any delay'],
  hard: [' just before the long meeting finally began',
    ' as soon as the results were announced', ' although nobody had expected it'],
};

function redundancy(d) {
  const subs = d === 'easy' ? RED_SUBJ.slice(0, 8) : RED_SUBJ;
  return pool40((i) => {
    const [b, g] = pick(RED, i);
    const s = pick(subs, i);
    const t = pick(TAIL_9_12[d], Math.floor(i / subs.length));
    return mk(withPeriod(`${s} ${b}${t}`), withPeriod(`${s} ${g}${t}`),
      'This phrase is redundant; one of the two words already carries the meaning.');
  });
}

// ---- 9.13 Indirect question word order (I wonder where is he) ------------
const IQ_INTRO = ['I wonder', 'She asked', 'Do you know', 'I do not know', 'Tell me',
  'We wondered', 'Nobody knows', 'Can you tell me'];
const IQ_WH = [['where', 'at home'], ['where', 'in the office'], ['where', 'at the station'],
  ['where', 'on holiday'], ['where', 'in the garden'], ['where', 'at work'],
  ['when', 'back'], ['when', 'ready'], ['when', 'free'], ['when', 'available'],
  ['why', 'so quiet'], ['why', 'so late'], ['why', 'so tired'], ['why', 'upset']];
const IQ_SUBJ = [['he', 'is'], ['she', 'is'], ['it', 'is'], ['Tom', 'is'], ['Anna', 'is'],
  ['they', 'are'], ['we', 'are'], ['you', 'are'], ['the boys', 'are'], ['the students', 'are'],
  ['the meeting', 'is'], ['the bus', 'is']];

function indirectQuestion(d) {
  const intros = d === 'easy' ? IQ_INTRO.slice(0, 6) : IQ_INTRO;
  const wh = d === 'easy' ? IQ_WH.slice(0, 8) : IQ_WH;
  return cartesian([intros, wh, IQ_SUBJ], (intro, [w, comp], [sub, be]) => mk(
    withPeriod(`${intro} ${w} ${be} ${sub} ${comp}`),
    withPeriod(`${intro} ${w} ${sub} ${be} ${comp}`),
    'In an indirect question the subject comes before the verb.'));
}

// ---- 9.14 Clause linking (because to see you) ----------------------------
const CL_SUBJ = ['She', 'He', 'Tom', 'Anna', 'They', 'We', 'The boy', 'My friend',
  'The students', 'The workers'];
const CL_PRE = ['came home', 'stayed late', 'waited outside', 'left early', 'woke up',
  'hurried over', 'returned', 'stood in line'];
const CL_INF = ['see you', 'help them', 'catch the train', 'finish the work', 'buy some milk',
  'meet his friend', 'learn Spanish', 'find the keys', 'answer the letter', 'visit the museum',
  'call his mother', 'repair the car', 'save money', 'read the report', 'take a rest',
  'join the team'];
const CL_LINK = ['because to', 'for to'];

function clauseLinking(d) {
  const links = d === 'easy' ? ['because to'] : CL_LINK;
  return cartesian([CL_SUBJ, CL_PRE, links, CL_INF], (s, pre, link, inf) => mk(
    withPeriod(`${s} ${pre} ${link} ${inf}`),
    withPeriod(`${s} ${pre} to ${inf}`),
    `Do not use "${link}" before a purpose infinitive; use "to" alone.`));
}

// ---- 9.15 Object order (gave to me a book) -------------------------------
const OO_SUBJ = ['She', 'He', 'Tom', 'Anna', 'They', 'We', 'The boy', 'My friend',
  'The teacher', 'The workers'];
const OO_VERB = [['gave', 'to'], ['sent', 'to'], ['showed', 'to'], ['told', 'to'], ['lent', 'to'],
  ['handed', 'to'], ['offered', 'to'], ['passed', 'to'], ['read', 'to'], ['brought', 'to'],
  ['bought', 'for'], ['made', 'for'], ['cooked', 'for'], ['wrote', 'to'], ['taught', 'to'],
  ['promised', 'to'], ['paid', 'to'], ['threw', 'to'], ['found', 'for'], ['got', 'for']];
const OO_RECIP = ['me', 'him', 'her', 'us', 'them', 'Tom', 'Anna', 'the teacher', 'my friend',
  'the children'];
const OO_OBJ = ['a book', 'the letter', 'a gift', 'the news', 'some money', 'a story', 'the keys',
  'a sandwich', 'the tickets', 'a ride', 'the message', 'a present', 'the bill', 'some advice',
  'a map', 'the ball'];

function objectOrder(d) {
  const recips = d === 'easy' ? OO_RECIP.slice(0, 6) : OO_RECIP;
  const objs = d === 'easy' ? OO_OBJ.slice(0, 6) : OO_OBJ;
  return cartesian([OO_SUBJ, OO_VERB, recips, objs], (s, [v, prep], r, o) => mk(
    withPeriod(`${s} ${v} ${prep} ${r} ${o}`),
    withPeriod(`${s} ${v} ${r} ${o}`),
    'With a double-object verb, the indirect object comes first and takes no preposition.'));
}

export default {
  '9.1': fragment,
  '9.2': missingSubject,
  '9.3': runOn,
  '9.4': commaSplice,
  '9.5': doubleSubject,
  '9.6': wordOrder,
  '9.7': missingExtraWord,
  '9.8': parallel,
  '9.9': conjunctionPairing,
  '9.10': relativeClause,
  '9.11': danglingModifier,
  '9.12': redundancy,
  '9.13': indirectQuestion,
  '9.14': clauseLinking,
  '9.15': objectOrder,
};
