// Section 6 — Verbs (20 rules). One builder per rule; each returns 40 items
// per difficulty tier ('easy' | 'medium' | 'hard').
import {
  SG_SUBJ, PL_SUBJ, VERBS, OBJECTS, TAILS_SIMPLE, TAILS_COMPLEX,
  ADJ, ADV, pick, mk, pool40, cap,
} from './core.js';

// ---- local pools ---------------------------------------------------------
const SING_SUBJ = ['She', 'He', 'Tom', 'Anna', 'The boy', 'The girl', 'The child',
  'The teacher', 'My friend', 'The man'];
const PLUR_SUBJ = ['They', 'We', 'You', 'The boys', 'The girls', 'The students',
  'My friends', 'The children', 'The workers'];
const PLACES = ['at school', 'in the garden', 'to the office', 'near the river',
  'at the station', 'in the park', 'by the window', 'on the bus', 'at home',
  'in the kitchen'];
const MODALS = ['can', 'could', 'may', 'might', 'must', 'shall', 'should', 'will', 'would'];
const WH = ['Where', 'Why', 'When', 'How', 'What'];
const TIME11 = ['today', 'right now', 'at the moment', 'these days', 'every day',
  'this week', 'all the time', 'at present', 'nowadays', 'currently', 'lately'];
const TIME_PAST = ['last week', 'yesterday', 'this morning', 'the day before',
  'last month', 'that afternoon', 'the previous night', 'earlier', 'at the time',
  'back then', 'recently'];
const PASS_TIME = ['last week', 'yesterday', 'last month', 'this morning',
  'in 2019', 'before the storm', 'during the night', 'on Monday', 'long ago', 'recently'];
const AGENTS = ['the teacher', 'the workers', 'the boy', 'my father', 'the committee',
  'the team', 'the driver', 'the artist', 'the cleaner', 'the manager'];
const NEG_NOUNS = ['money', 'time', 'friends', 'food', 'water', 'ideas', 'questions',
  'plans', 'help', 'tickets', 'letters', 'reasons', 'answers', 'news', 'hope', 'homework'];
const NEG_MASS = ['money', 'time', 'food', 'water', 'help', 'news', 'hope', 'homework'];

const INTRANS6 = new Set(['arrive', 'go', 'come', 'live', 'smile', 'hope',
  'decide', 'sleep', 'run', 'jump', 'dance', 'swim', 'fly', 'stand', 'sit']);
const TRANS6 = VERBS.filter(([b]) => !INTRANS6.has(b));

// ---- 6.1 Auxiliary + verb form -------------------------------------------
function auxVerbForm(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(SG_SUBJ, i);
      const m = pick(MODALS, i * 3 + 1);
      const [b, sg] = pick(VERBS, i * 7 + 2);
      const adv = pick(ADV, i * 5 + 3);
      return mk(`${cap(s)} ${m} ${sg} ${adv}.`, `${cap(s)} ${m} ${b} ${adv}.`,
        `After the modal "${m}" use the base verb "${b}", not "${sg}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(SG_SUBJ, i);
      const m = pick(MODALS, i * 5 + 1);
      const [b, , past] = pick(VERBS, i * 3 + 2);
      const adv = pick(ADV, i * 7 + 3);
      const t = pick(TAILS_SIMPLE, i);
      return mk(`${cap(s)} ${m} ${past} ${adv} ${t}.`, `${cap(s)} ${m} ${b} ${adv} ${t}.`,
        `Modals like "${m}" take the base form "${b}", not the past "${past}".`);
    });
  }
  return pool40((i) => {
    const s = pick(SG_SUBJ, i);
    const m = pick(MODALS, i * 7 + 1);
    const [b, , , part] = pick(VERBS, i * 3 + 2);
    const adv = pick(ADV, i * 5 + 3);
    const t = pick(TAILS_COMPLEX, i * 7 + 2);
    return mk(`${cap(t)}, ${cap(s)} ${m} ${part} ${adv}.`, `${cap(t)}, ${cap(s)} ${m} ${b} ${adv}.`,
      `Even in this long sentence "${m}" must be followed by the base verb "${b}".`);
  });
}

// ---- 6.2 Finite main verb / copula ---------------------------------------
function finiteMainVerb(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(SG_SUBJ, i);
      const [, , , , ing] = pick(VERBS, i * 3 + 1);
      const p = pick(PLACES, i * 7 + 2);
      return mk(`${cap(s)} ${ing} ${p}.`, `${cap(s)} is ${ing} ${p}.`,
        `The clause needs the finite auxiliary "is": ${cap(s)} is ${ing}.`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(PL_SUBJ, i);
      const [, , , , ing] = pick(VERBS, i * 5 + 1);
      const adv = pick(ADV, i * 7 + 2);
      const p = pick(PLACES, i * 3 + 1);
      return mk(`${cap(s)} ${ing} ${adv} ${p}.`, `${cap(s)} are ${ing} ${adv} ${p}.`,
        `The plural subject "${s}" needs the finite verb "are": ${s} are ${ing}.`);
    });
  }
  return pool40((i) => {
    const s = pick(SG_SUBJ, i);
    const [, , , , ing] = pick(VERBS, i * 7 + 1);
    const t = pick(TAILS_COMPLEX, i * 5 + 2);
    return mk(`${cap(t)}, ${cap(s)} ${ing} home.`, `${cap(t)}, ${cap(s)} is ${ing} home.`,
      `Every clause needs a finite verb, so add "is" before "${ing}".`);
  });
}

// ---- 6.3 Missing verb / copula -------------------------------------------
function missingCopula(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(SG_SUBJ, i);
      const a = pick(ADJ, i * 3 + 1);
      return mk(`${cap(s)} very ${a}.`, `${cap(s)} is very ${a}.`,
        `A subject needs the copula "is" before the adjective "${a}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(PL_SUBJ, i);
      const a = pick(ADJ, i * 5 + 1);
      const adv = pick(ADV, i * 7 + 2);
      return mk(`${cap(s)} very ${a} ${adv}.`, `${cap(s)} are very ${a} ${adv}.`,
        `The plural subject "${s}" needs "are" before the adjective.`);
    });
  }
  return pool40((i) => {
    const s = pick(SG_SUBJ, i);
    const a = pick(ADJ, i * 5 + 1);
    const t = pick(TAILS_COMPLEX, i * 7 + 2);
    return mk(`${cap(t)}, ${cap(s)} still very ${a}.`, `${cap(t)}, ${cap(s)} is still very ${a}.`,
      `The copula "is" is still required in the main clause.`);
  });
}

// ---- 6.4 Passive formation -----------------------------------------------
const PASS_PAIRS = [
  ['the letter', 'write', 'written'], ['the book', 'read', 'read'],
  ['the song', 'sing', 'sung'], ['the car', 'drive', 'driven'],
  ['the house', 'build', 'built'], ['the window', 'break', 'broken'],
  ['the meal', 'cook', 'cooked'], ['the story', 'tell', 'told'],
  ['the report', 'write', 'written'], ['the bridge', 'destroy', 'destroyed'],
  ['the money', 'steal', 'stolen'], ['the cake', 'eat', 'eaten'],
  ['the milk', 'drink', 'drunk'], ['the photo', 'take', 'taken'],
  ['the ball', 'throw', 'thrown'], ['the fish', 'catch', 'caught'],
  ['the dress', 'wear', 'worn'], ['the door', 'close', 'closed'],
  ['the tree', 'cut', 'cut'], ['the floor', 'clean', 'cleaned'],
  ['the table', 'move', 'moved'], ['the picture', 'paint', 'painted'],
  ['the parcel', 'send', 'sent'], ['the bill', 'pay', 'paid'],
  ['the problem', 'solve', 'solved'], ['the gate', 'lock', 'locked'],
  ['the homework', 'finish', 'finished'], ['the garden', 'water', 'watered'],
  ['the wall', 'repaint', 'repainted'], ['the test', 'mark', 'marked'],
  ['the email', 'send', 'sent'], ['the room', 'clean', 'cleaned'],
  ['the car', 'wash', 'washed'], ['the fence', 'paint', 'painted'],
  ['the chair', 'repair', 'repaired'], ['the road', 'close', 'closed'],
  ['the candle', 'light', 'lit'], ['the plant', 'water', 'watered'],
  ['the coat', 'wash', 'washed'], ['the key', 'lose', 'lost'],
  ['the flag', 'raise', 'raised'], ['the contract', 'sign', 'signed'],
  ['the letter', 'type', 'typed'], ['the floor', 'sweep', 'swept'],
];
function passiveFormation(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [obj, b, part] = pick(PASS_PAIRS, i);
      return mk(`${cap(obj)} ${b} last week.`, `${cap(obj)} was ${part} last week.`,
        `A passive needs "was" plus the participle "${part}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [obj, b, part] = pick(PASS_PAIRS, i);
      const tm = pick(PASS_TIME, i * 3 + 1);
      const ag = pick(AGENTS, i * 7 + 2);
      return mk(`${cap(obj)} ${b} by ${ag} ${tm}.`, `${cap(obj)} was ${part} by ${ag} ${tm}.`,
        `Form the passive with "was ${part}" before the agent.`);
    });
  }
  return pool40((i) => {
    const [obj, b, part] = pick(PASS_PAIRS, i);
    const ag = pick(AGENTS, i * 5 + 1);
    const t = pick(TAILS_COMPLEX, i * 7 + 2);
    return mk(`${cap(t)}, ${obj} ${b} by ${ag}.`, `${cap(t)}, ${obj} was ${part} by ${ag}.`,
      `The passive "was ${part}" is required in the main clause.`);
  });
}

// ---- 6.5 Intransitive passive --------------------------------------------
const INTRANS = [
  ['happen', 'happened', 'happened'], ['occur', 'occurred', 'occurred'],
  ['arrive', 'arrived', 'arrived'], ['come', 'came', 'come'],
  ['go', 'went', 'gone'], ['die', 'died', 'died'],
  ['fall', 'fell', 'fallen'], ['rise', 'rose', 'risen'],
  ['appear', 'appeared', 'appeared'], ['disappear', 'disappeared', 'disappeared'],
  ['stay', 'stayed', 'stayed'], ['wait', 'waited', 'waited'],
  ['work', 'worked', 'worked'], ['live', 'lived', 'lived'],
  ['laugh', 'laughed', 'laughed'], ['cry', 'cried', 'cried'],
  ['smile', 'smiled', 'smiled'], ['swim', 'swam', 'swum'],
  ['run', 'ran', 'run'], ['walk', 'walked', 'walked'],
  ['sit', 'sat', 'sat'], ['stand', 'stood', 'stood'],
  ['remain', 'remained', 'remained'], ['exist', 'existed', 'existed'],
  ['emerge', 'emerged', 'emerged'], ['vanish', 'vanished', 'vanished'],
  ['collapse', 'collapsed', 'collapsed'], ['sneeze', 'sneezed', 'sneezed'],
  ['sleep', 'slept', 'slept'], ['depart', 'departed', 'departed'],
  ['travel', 'travelled', 'travelled'], ['rest', 'rested', 'rested'],
  ['faint', 'fainted', 'fainted'], ['yawn', 'yawned', 'yawned'],
  ['relax', 'relaxed', 'relaxed'], ['listen', 'listened', 'listened'],
  ['look', 'looked', 'looked'], ['seem', 'seemed', 'seemed'],
  ['become', 'became', 'become'], ['begin', 'began', 'begun'],
];
const INT_SUBJ = [
  ['It', 'was'], ['She', 'was'], ['He', 'was'], ['The train', 'was'],
  ['The boy', 'was'], ['They', 'were'], ['We', 'were'],
  ['The children', 'were'], ['The girls', 'were'], ['The guests', 'were'],
];
function intransitivePassive(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [s, aux] = pick(INT_SUBJ, i);
      const [b, past, part] = pick(INTRANS, i * 3 + 1);
      const tm = pick(TIME11, i * 7 + 2);
      return mk(`${s} ${aux} ${part} ${tm}.`, `${s} ${past} ${tm}.`,
        `"${b}" is intransitive, so it cannot be passive: use "${past}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [s, aux] = pick(INT_SUBJ, i);
      const [b, past, part] = pick(INTRANS, i * 5 + 1);
      const adv = pick(ADV, i * 7 + 2);
      const tm = pick(TIME_PAST, i * 3 + 1);
      return mk(`${s} ${aux} ${part} ${adv} ${tm}.`, `${s} ${past} ${adv} ${tm}.`,
        `"${b}" takes no passive; the active past is "${past}".`);
    });
  }
  return pool40((i) => {
    const [s, aux] = pick(INT_SUBJ, i);
    const [b, past, part] = pick(INTRANS, i * 7 + 1);
    const adv = pick(ADV, i * 5 + 2);
    const t = pick(TAILS_COMPLEX, i * 3 + 1);
    return mk(`${cap(t)}, ${s} ${aux} ${part} ${adv}.`, `${cap(t)}, ${s} ${past} ${adv}.`,
      `Even here "${b}" is intransitive and cannot be passive.`);
  });
}

// ---- 6.6 Stative verbs in progressive ------------------------------------
const STAT = [
  ['know', 'knows', 'knowing', 'the answer'],
  ['understand', 'understands', 'understanding', 'the question'],
  ['believe', 'believes', 'believing', 'the story'],
  ['like', 'likes', 'liking', 'the song'],
  ['love', 'loves', 'loving', 'the city'],
  ['hate', 'hates', 'hating', 'the noise'],
  ['want', 'wants', 'wanting', 'a new car'],
  ['need', 'needs', 'needing', 'some help'],
  ['remember', 'remembers', 'remembering', 'the name'],
  ['mean', 'means', 'meaning', 'the word'],
  ['recognize', 'recognizes', 'recognizing', 'the face'],
  ['deserve', 'deserves', 'deserving', 'the prize'],
  ['doubt', 'doubts', 'doubting', 'the excuse'],
  ['own', 'owns', 'owning', 'the house'],
  ['prefer', 'prefers', 'preferring', 'the tea'],
  ['see', 'sees', 'seeing', 'the problem'],
  ['hear', 'hears', 'hearing', 'the music'],
  ['taste', 'tastes', 'tasting', 'the soup'],
  ['imagine', 'imagines', 'imagining', 'the result'],
  ['realize', 'realizes', 'realizing', 'the truth'],
];
const STAT_PL = [['I', 'am'], ['We', 'are'], ['You', 'are'], ['They', 'are'],
  ['The students', 'are'], ['My friends', 'are'], ['The children', 'are'], ['The boys', 'are']];
function stativeProgressive(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [s, aux] = pick(STAT_PL, i);
      const [b, , ing, obj] = pick(STAT, i * 3 + 1);
      const tm = pick(TIME11, i * 7 + 2);
      return mk(`${s} ${aux} ${ing} ${obj} ${tm}.`, `${s} ${b} ${obj} ${tm}.`,
        `"${b}" is a stative verb and is not used in the progressive.`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(SING_SUBJ, i);
      const [b, sg, ing, obj] = pick(STAT, i * 5 + 1);
      const tm = pick(TIME11, i * 7 + 2);
      return mk(`${s} is ${ing} ${obj} ${tm}.`, `${s} ${sg} ${obj} ${tm}.`,
        `Stative "${b}" takes the simple present "${sg}", not "${ing}".`);
    });
  }
  return pool40((i) => {
    const s = pick(SING_SUBJ, i);
    const [b, sg, ing, obj] = pick(STAT, i * 7 + 1);
    const t = pick(TAILS_COMPLEX, i * 3 + 2);
    const adv = pick(ADV, i * 5 + 3);
    return mk(`${cap(t)}, ${s} is ${ing} ${obj} ${adv}.`, `${cap(t)}, ${s} ${sg} ${obj} ${adv}.`,
      `Even in this clause the stative "${b}" stays simple: use "${sg}".`);
  });
}

// ---- 6.7 Tense consistency / backshift -----------------------------------
const BACK_PAIRS = [
  ['is tired', 'was tired'], ['has finished', 'had finished'],
  ['wants to go', 'wanted to go'], ['needs help', 'needed help'],
  ['can swim', 'could swim'], ['will wait', 'would wait'],
  ['knows the answer', 'knew the answer'], ['works here', 'worked here'],
  ['is working', 'was working'], ['has been ill', 'had been ill'],
  ['will help', 'would help'], ['may come', 'might come'],
  ['is going to leave', 'was going to leave'], ['does not know', 'did not know'],
  ['is ready', 'was ready'], ['sees the doctor', 'saw the doctor'],
];
const REPORTS = ['He said', 'She said', 'Tom said', 'Anna said', 'They said',
  'He told me', 'She told me', 'They told me'];
function tenseConsistency(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const rep = pick(REPORTS, i);
      const [bad, good] = pick(BACK_PAIRS, i * 3 + 1);
      const tm = pick(TIME_PAST, i * 7 + 2);
      return mk(`${rep} that he ${bad} ${tm}.`, `${rep} that he ${good} ${tm}.`,
        `After a past reporting verb, backshift to "${good}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const rep = pick(REPORTS, i * 5 + 1);
      const [bad, good] = pick(BACK_PAIRS, i * 3 + 2);
      const tm = pick(TIME_PAST, i * 7 + 1);
      return mk(`Although it surprised us, ${cap(rep)} that he ${bad} ${tm}.`,
        `Although it surprised us, ${cap(rep)} that he ${good} ${tm}.`,
        `Tense consistency requires the backshifted "${good}".`);
    });
  }
  return pool40((i) => {
    const rep = pick(REPORTS, i * 7 + 1);
    const [bad, good] = pick(BACK_PAIRS, i * 5 + 2);
    const t = pick(TAILS_COMPLEX, i * 3 + 1);
    return mk(`${cap(t)}, ${rep} that he ${bad}.`, `${cap(t)}, ${rep} that he ${good}.`,
      `The reported clause must backshift to "${good}".`);
  });
}

// ---- 6.8 Transitivity -----------------------------------------------------
const TRANS_VERBS = ['discussed', 'mentioned', 'described', 'explained', 'announced',
  'reported', 'confirmed', 'denied', 'rejected', 'analyzed', 'summarized', 'outlined',
  'presented', 'covered', 'addressed', 'examined', 'considered', 'reviewed',
  'approved', 'proposed'];
const TR_SUBJ = ['We', 'They', 'The committee', 'The students', 'The managers',
  'The team', 'My colleagues', 'The researchers'];
function transitivity(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(TR_SUBJ, i);
      const v = pick(TRANS_VERBS, i * 3 + 1);
      const o = pick(OBJECTS, i * 7 + 2);
      const t = pick(TAILS_SIMPLE, i * 5 + 3);
      return mk(`${s} ${v} about ${o} ${t}.`, `${s} ${v} ${o} ${t}.`,
        `"${v}" is transitive and takes no "about" before ${o}.`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(TR_SUBJ, i * 3 + 1);
      const v = pick(TRANS_VERBS, i * 7 + 2);
      const o = pick(OBJECTS, i * 5 + 3);
      const adv = pick(ADV, i * 3 + 1);
      return mk(`${s} ${v} about ${o} ${adv}.`, `${s} ${v} ${o} ${adv}.`,
        `Drop "about": "${v}" is directly transitive.`);
    });
  }
  return pool40((i) => {
    const s = pick(TR_SUBJ, i * 5 + 1);
    const v = pick(TRANS_VERBS, i * 3 + 2);
    const o = pick(OBJECTS, i * 7 + 1);
    const t = pick(TAILS_COMPLEX, i * 5 + 2);
    return mk(`${cap(t)}, ${s} ${v} about ${o}.`, `${cap(t)}, ${s} ${v} ${o}.`,
      `"${v}" still takes a direct object without "about".`);
  });
}

// ---- 6.9 Gerund vs infinitive --------------------------------------------
const GERUND_V = ['enjoy', 'finish', 'avoid', 'mind', 'suggest', 'recommend',
  'consider', 'keep', 'practice', 'admit', 'deny', 'postpone', 'risk', 'imagine',
  'dislike', 'quit', 'tolerate', 'resist', 'celebrate', 'delay'];
const GER_SUBJ = ['I', 'We', 'You', 'They', 'My friends', 'The students',
  'The boys', 'The girls', 'Most people', 'The children'];
const INF_V = [['want', 'wants'], ['decide', 'decides'], ['hope', 'hopes'],
  ['plan', 'plans'], ['agree', 'agrees'], ['refuse', 'refuses'], ['offer', 'offers'],
  ['promise', 'promises'], ['learn', 'learns'], ['manage', 'manages'],
  ['afford', 'affords'], ['choose', 'chooses'], ['fail', 'fails'],
  ['pretend', 'pretends'], ['expect', 'expects'], ['intend', 'intends']];
function gerundInfinitive(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(GER_SUBJ, i);
      const gv = pick(GERUND_V, i * 3 + 1);
      const [b, , , , ing] = pick(VERBS, i * 7 + 2);
      return mk(`${s} ${gv} to ${b}.`, `${s} ${gv} ${ing}.`,
        `"${gv}" is followed by the gerund "${ing}", not "to ${b}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(GER_SUBJ, i * 5 + 1);
      const gv = pick(GERUND_V, i * 3 + 2);
      const [b, , , , ing] = pick(VERBS, i * 7 + 1);
      const adv = pick(ADV, i * 5 + 3);
      return mk(`${s} ${gv} to ${b} ${adv}.`, `${s} ${gv} ${ing} ${adv}.`,
        `"${gv}" takes the gerund "${ing}", so never "to ${b}".`);
    });
  }
  return pool40((i) => {
    const s = pick(SING_SUBJ, i);
    const [ib, isg] = pick(INF_V, i * 3 + 1);
    const [b, , , , ing] = pick(VERBS, i * 7 + 2);
    const t = pick(PLACES, i * 5 + 3);
    return mk(`${s} ${isg} ${ing} ${t}.`, `${s} ${isg} to ${b} ${t}.`,
      `"${ib}" takes the infinitive, so use "to ${b}", not "${ing}".`);
  });
}

// ---- 6.10 to + base form --------------------------------------------------
const TO_VERBS = [['want', 'wants'], ['need', 'needs'], ['hope', 'hopes'],
  ['try', 'tries'], ['plan', 'plans'], ['decide', 'decides'], ['expect', 'expects'],
  ['promise', 'promises'], ['agree', 'agrees'], ['refuse', 'refuses'],
  ['offer', 'offers'], ['learn', 'learns'], ['manage', 'manages'],
  ['forget', 'forgets'], ['remember', 'remembers'], ['begin', 'begins'],
  ['start', 'starts'], ['continue', 'continues'], ['like', 'likes'], ['love', 'loves']];
function toBaseForm(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(GER_SUBJ, i);
      const [b2] = pick(TO_VERBS, i * 3 + 1);
      const [b, sg] = pick(VERBS, i * 7 + 2);
      const t = pick(PLACES, i * 5 + 3);
      return mk(`${s} ${b2} to ${sg} ${t}.`, `${s} ${b2} to ${b} ${t}.`,
        `After "to" always use the base form "${b}", not "${sg}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(SING_SUBJ, i);
      const [, sg2] = pick(TO_VERBS, i * 5 + 1);
      const [b, , past] = pick(VERBS, i * 7 + 2);
      const t = pick(PLACES, i * 3 + 1);
      return mk(`${s} ${sg2} to ${past} ${t}.`, `${s} ${sg2} to ${b} ${t}.`,
        `The infinitive after "to" must be the base form "${b}", not "${past}".`);
    });
  }
  return pool40((i) => {
    const s = pick(SING_SUBJ, i);
    const [, sg2] = pick(TO_VERBS, i * 3 + 1);
    const [b, , , part] = pick(VERBS, i * 7 + 2);
    const t = pick(TAILS_COMPLEX, i * 5 + 3);
    return mk(`${cap(t)}, ${s} ${sg2} to ${part}.`, `${cap(t)}, ${s} ${sg2} to ${b}.`,
      `Even far from "to", the verb stays base: "${b}", not "${part}".`);
  });
}

// ---- 6.11 Phrasal verbs ---------------------------------------------------
const PH = [['pick', 'picked', 'up'], ['turn', 'turned', 'on'],
  ['turn', 'turned', 'off'], ['put', 'put', 'on'], ['take', 'took', 'off'],
  ['give', 'gave', 'back'], ['write', 'wrote', 'down'], ['throw', 'threw', 'away'],
  ['look', 'looked', 'up'], ['hand', 'handed', 'in'], ['fill', 'filled', 'in'],
  ['point', 'pointed', 'out'], ['figure', 'figured', 'out'], ['carry', 'carried', 'out'],
  ['bring', 'brought', 'up'], ['call', 'called', 'off'], ['put', 'put', 'off'],
  ['set', 'set', 'up'], ['wake', 'woke', 'up'], ['switch', 'switched', 'on']];
const PH_TAILS = ['right now', 'at once', 'before dinner', 'this morning',
  'for me', 'again', 'straight away'];
function phrasalVerbs(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [b, , part] = pick(PH, i * 3);
      const pron = pick(['it', 'them'], i * 7 + 1);
      const tail = pick(PH_TAILS, i * 5 + 2);
      return mk(`${cap(b)} ${part} ${pron} ${tail}.`, `${cap(b)} ${pron} ${part} ${tail}.`,
        `With a pronoun object, keep the particle after it: "${b} ${pron} ${part}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(SING_SUBJ, i);
      const [, past, part] = pick(PH, i * 3 + 1);
      const pron = pick(['it', 'them', 'me', 'him', 'her', 'us'], i * 7 + 2);
      const tail = pick(PH_TAILS, i * 5 + 3);
      return mk(`${s} ${past} ${part} ${pron} ${tail}.`, `${s} ${past} ${pron} ${part} ${tail}.`,
        `The pronoun must fall between the verb and the particle: "${past} ${pron} ${part}".`);
    });
  }
  return pool40((i) => {
    const s = pick(SING_SUBJ, i);
    const [, past, part] = pick(PH, i * 3 + 1);
    const pron = pick(['it', 'them', 'me', 'us'], i * 7 + 2);
    const t = pick(TAILS_COMPLEX, i * 5 + 3);
    const adv = pick(ADV, i * 7 + 1);
    return mk(`${cap(t)}, ${s} ${past} ${part} ${pron} ${adv}.`, `${cap(t)}, ${s} ${past} ${pron} ${part} ${adv}.`,
      `The pronoun stays between the verb and particle even in a long sentence.`);
  });
}

// ---- 6.12 Modals and semi-modals -----------------------------------------
function modalsSemi(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(SG_SUBJ, i);
      const m = pick(MODALS, i * 3 + 1);
      const [b] = pick(VERBS, i * 7 + 2);
      const t = pick(PLACES, i * 5 + 3);
      return mk(`${cap(s)} ${m} to ${b} ${t}.`, `${cap(s)} ${m} ${b} ${t}.`,
        `Pure modals like "${m}" are followed by the base verb without "to".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(SG_SUBJ, i);
      const m = pick(MODALS, i * 5 + 1);
      const [b] = pick(VERBS, i * 3 + 2);
      const adv = pick(ADV, i * 7 + 3);
      const t = pick(TAILS_SIMPLE, i);
      return mk(`${cap(s)} ${m} to ${b} ${adv} ${t}.`, `${cap(s)} ${m} ${b} ${adv} ${t}.`,
        `"${m}" never takes "to"; use the bare base "${b}".`);
    });
  }
  return pool40((i) => {
    const s = pick(SG_SUBJ, i);
    const [b] = pick(VERBS, i * 7 + 1);
    const t = pick(TAILS_COMPLEX, i * 3 + 2);
    if (i % 2 === 0) {
      const m = pick(MODALS, i * 5 + 3);
      return mk(`${cap(t)}, ${cap(s)} ${m} to ${b}.`, `${cap(t)}, ${cap(s)} ${m} ${b}.`,
        `"${m}" is a pure modal and takes no "to".`);
    }
    return mk(`${cap(t)}, ${cap(s)} ought ${b}.`, `${cap(t)}, ${cap(s)} ought to ${b}.`,
      `The semi-modal "ought" always keeps "to": "ought to ${b}".`);
  });
}

// ---- 6.13 Question formation ---------------------------------------------
function questionFormation(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const w = pick(WH, i);
      const s = pick(SG_SUBJ, i * 3 + 1);
      const [, , , , ing] = pick(VERBS, i * 7 + 2);
      return mk(`${w} ${s} is ${ing}?`, `${w} is ${s} ${ing}?`,
        `In a wh-question the auxiliary comes before the subject: "${w} is ${s} ${ing}?".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const w = pick(WH, i);
      const p = pick(PL_SUBJ, i * 3 + 1);
      const [b] = pick(VERBS, i * 7 + 2);
      const tm = pick(TIME_PAST, i * 5 + 3);
      return mk(`${w} ${p} did ${b} ${tm}?`, `${w} did ${p} ${b} ${tm}?`,
        `The auxiliary "did" moves before the subject: "${w} did ${p} ${b}?".`);
    });
  }
  return pool40((i) => {
    const w = pick(WH, i);
    const p = pick(PL_SUBJ, i * 7 + 1);
    const [, , , , ing] = pick(VERBS, i * 3 + 2);
    const tm = pick(TIME11, i * 5 + 3);
    return mk(`${w} ${p} have been ${ing} ${tm}?`, `${w} have ${p} been ${ing} ${tm}?`,
      `With a perfect progressive question the "have" precedes the subject.`);
  });
}

// ---- 6.14 Negation / double negatives ------------------------------------
function negation(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [s, aux] = pick([['I', "don't"], ['We', "don't"], ['You', "don't"],
        ['They', "don't"], ['She', "doesn't"], ['He', "doesn't"], ['Tom', "doesn't"],
        ['Anna', "doesn't"], ['The boys', "don't"], ['The girl', "doesn't"]], i);
      const n = pick(NEG_NOUNS, i * 3 + 1);
      return mk(`${s} ${aux} have no ${n}.`, `${s} ${aux} have any ${n}.`,
        `In a negative sentence use "any ${n}", not "no ${n}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [s] = pick([['I'], ['We'], ['You'], ['They'], ['She'], ['He'],
        ['Tom'], ['Anna'], ['The boys'], ['The girl']], i);
      const v = pick(['see', 'say', 'know', 'find', 'tell', 'hear'], i * 3 + 1);
      const pair = pick([['nobody', 'anybody'], ['nothing', 'anything']], i * 7 + 2);
      const tm = pick(TIME_PAST, i * 5 + 3);
      return mk(`${s} didn't ${v} ${pair[0]} ${tm}.`, `${s} didn't ${v} ${pair[1]} ${tm}.`,
        `Avoid the double negative: use "${pair[1]}", not "${pair[0]}".`);
    });
  }
  return pool40((i) => {
    const t = pick(TAILS_COMPLEX, i * 7 + 2);
    if (i % 2 === 0) {
      const n = pick(NEG_MASS, i * 3 + 1);
      return mk(`${cap(t)}, there wasn't no ${n} left.`, `${cap(t)}, there wasn't any ${n} left.`,
        `"wasn't ... no" is a double negative; use "any ${n}".`);
    }
    const n = pick(NEG_NOUNS, i * 3 + 1);
    return mk(`${cap(t)}, we never found no ${n}.`, `${cap(t)}, we never found any ${n}.`,
      `"never ... no" is a double negative; use "any ${n}".`);
  });
}

// ---- 6.15 Imperatives -----------------------------------------------------
function imperatives(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [b, sg] = pick(VERBS, i);
      const p = pick(PLACES, i * 3 + 1);
      return mk(`Don't ${sg} ${p}.`, `Don't ${b} ${p}.`,
        `The negative imperative uses the base verb "${b}", not "${sg}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [b, , past] = pick(VERBS, i * 3 + 1);
      const t = pick(TAILS_SIMPLE, i * 5 + 2);
      return mk(`Please don't ${past} ${t}.`, `Please don't ${b} ${t}.`,
        `After "don't" use the base form "${b}", not the past "${past}".`);
    });
  }
  return pool40((i) => {
    const [b, sg] = pick(TRANS6, i * 7 + 1);
    const o = pick(OBJECTS, i * 3 + 2);
    const t = pick(TAILS_COMPLEX, i * 5 + 3);
    return mk(`${cap(t)}, don't ${sg} ${o}.`, `${cap(t)}, don't ${b} ${o}.`,
      `The imperative stays base: "don't ${b}", not "don't ${sg}".`);
  });
}

// ---- 6.16 Conditionals ----------------------------------------------------
const WX = [
  ['rain', 'rains', 'rained', 'rained'], ['snow', 'snows', 'snowed', 'snowed'],
  ['stop', 'stops', 'stopped', 'stopped'], ['start', 'starts', 'started', 'started'],
  ['come', 'comes', 'came', 'come'], ['wait', 'waits', 'waited', 'waited'],
  ['help', 'helps', 'helped', 'helped'], ['work', 'works', 'worked', 'worked'],
  ['change', 'changes', 'changed', 'changed'], ['matter', 'matters', 'mattered', 'mattered'],
  ['clear', 'clears', 'cleared', 'cleared'], ['improve', 'improves', 'improved', 'improved'],
];
function conditionals(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [b, sg] = pick(WX, i);
      const when = pick(['tomorrow', 'tonight', 'later today', 'next week', 'this weekend'], i * 3 + 1);
      return mk(`If it will ${b} ${when}, we will stay inside.`,
        `If it ${sg} ${when}, we will stay inside.`,
        `The if-clause of a first conditional takes the present "${sg}", not "will ${b}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const p = pick(PLUR_SUBJ, i);
      const [b] = pick(WX, i * 5 + 1);
      const t = pick(TAILS_SIMPLE, i * 3 + 2);
      return mk(`If ${p} will ${b} ${t}, everything will be fine.`,
        `If ${p} ${b} ${t}, everything will be fine.`,
        `Never use "will" in the if-clause; use the present base "${b}".`);
    });
  }
  return pool40((i) => {
    const s = pick(SING_SUBJ, i);
    const [b, , past] = pick(WX, i * 5 + 1);
    const t = pick(TAILS_SIMPLE, i * 7 + 3);
    return mk(`If ${s} would ${b} ${t}, ${s} would succeed.`,
      `If ${s} ${past} ${t}, ${s} would succeed.`,
      `A second conditional uses the past "${past}" in the if-clause, not "would ${b}".`);
  });
}

// ---- 6.17 Subjunctive and wish -------------------------------------------
const MANDATE_ROLES = ['teacher', 'manager', 'judge', 'chairman', 'editor',
  'captain', 'director', 'officer'];
function subjunctiveWish(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const a = pick(ADJ, i);
      return mk(`I wish I was ${a}.`, `I wish I were ${a}.`,
        `After "wish" use the subjunctive "were", not "was".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(SING_SUBJ, i);
      const pred = pick(['here', 'taller', 'richer', 'stronger', 'younger',
        'a doctor', 'the manager', 'in charge'], i * 3 + 1);
      const [b] = pick(VERBS, i * 7 + 2);
      return mk(`If ${s} was ${pred}, ${s} would ${b} with us.`,
        `If ${s} were ${pred}, ${s} would ${b} with us.`,
        `The hypothetical "if" also takes "were", not "was".`);
    });
  }
  return pool40((i) => {
    const role = pick(MANDATE_ROLES, i);
    const s = pick(SING_SUBJ, i * 3 + 1);
    const [b, sg] = pick(VERBS, i * 7 + 2);
    const t = pick(TAILS_SIMPLE, i * 5 + 3);
    return mk(`The ${role} insisted that ${s} ${sg} ${t}.`,
      `The ${role} insisted that ${s} ${b} ${t}.`,
      `A mandative clause uses the base subjunctive "${b}", not "${sg}".`);
  });
}

// ---- 6.18 Reported speech -------------------------------------------------
const RS_VERBS = ['She', 'He', 'Tom', 'Anna', 'The teacher', 'My friend',
  'The manager', 'The guide'];
const RS_OBJ = ['the truth', 'the news', 'the story', 'a secret', 'the answer',
  'the time', 'the way', 'a lie', 'the details', 'the reason', 'everything',
  'the plan', 'the joke', 'the rules', 'the results'];
function reportedSpeech(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(RS_VERBS, i);
      const o = pick(RS_OBJ, i * 3 + 1);
      return mk(`${s} said me ${o}.`, `${s} told me ${o}.`,
        `"Say" cannot take a person object; use "told me ${o}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(RS_VERBS, i * 3 + 1);
      const clause = pick(['the meeting was cancelled', 'she would come later',
        'the train had left', 'it was too late', 'they were waiting',
        'the plan had changed'], i * 7 + 2);
      const tm = pick(TIME_PAST, i * 5 + 3);
      return mk(`${s} said me that ${clause} ${tm}.`, `${s} told me that ${clause} ${tm}.`,
        `Use "told me that ..." rather than "said me that ...".`);
    });
  }
  return pool40((i) => {
    const s = pick(RS_VERBS, i * 7 + 1);
    const [bad, good] = pick([['where was I', 'where I was'],
      ['what did I want', 'what I wanted'], ['when would I leave', 'when I would leave'],
      ['why was I late', 'why I was late'], ['how did I know', 'how I knew']], i * 3 + 2);
    return mk(`${s} asked me ${bad}.`, `${s} asked me ${good}.`,
      `A reported question keeps statement order: "${good}".`);
  });
}

// ---- 6.19 Causatives and perception verbs --------------------------------
const CAUS_SUBJ = ['She', 'He', 'Tom', 'Anna', 'The teacher', 'My father',
  'The manager', 'The coach'];
const CAUS_OBJ = ['me', 'him', 'her', 'us', 'them', 'you'];
const CAUS_V = ['cry', 'laugh', 'wait', 'leave', 'stay', 'work', 'run',
  'smile', 'sit', 'stand', 'try', 'come', 'stop', 'dance', 'sing', 'sleep'];
function causatives(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(CAUS_SUBJ, i * 3);
      const o = pick(CAUS_OBJ, i);
      const b = pick(CAUS_V, i * 5 + 2);
      return mk(`${s} made ${o} to ${b}.`, `${s} made ${o} ${b}.`,
        `After the causative "make" use the bare infinitive "${b}", not "to ${b}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(CAUS_SUBJ, i * 3 + 1);
      const o = pick(CAUS_OBJ, i * 7 + 2);
      const b = pick(CAUS_V, i * 5 + 3);
      const t = pick(PLACES, i);
      if (i % 2 === 0) {
        return mk(`${s} let ${o} to ${b} ${t}.`, `${s} let ${o} ${b} ${t}.`,
          `"let" takes the bare infinitive "${b}", not "to ${b}".`);
      }
      return mk(`${s} had ${o} to ${b} ${t}.`, `${s} had ${o} ${b} ${t}.`,
        `The causative "have" takes the bare infinitive "${b}".`);
    });
  }
  return pool40((i) => {
    const o = pick(CAUS_OBJ, i * 7 + 1);
    const b = pick(CAUS_V, i * 3 + 2);
    const pv = pick(['saw', 'heard', 'watched', 'felt'], i * 5 + 3);
    const t = pick(TAILS_COMPLEX, i);
    return mk(`${cap(t)}, she ${pv} ${o} to ${b}.`, `${cap(t)}, she ${pv} ${o} ${b}.`,
      `Perception verbs like "${pv}" take the bare infinitive "${b}", not "to ${b}".`);
  });
}

// ---- 6.20 Verb + clause patterns -----------------------------------------
const CLAUSE_VERBS = ['suggest', 'recommend', 'propose', 'demand', 'insist',
  'request', 'argue', 'maintain'];
const CLAUSE_VERBS_PAST = ['suggested', 'recommended', 'proposed', 'demanded',
  'insisted', 'requested', 'argued', 'maintained'];
const CLAUSE_SUBJ = [['I', false], ['We', false], ['They', false],
  ['The committee', true], ['The board', true], ['The teacher', true],
  ['The manager', true], ['The council', true]];
function verbClause(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [s, sgSubject] = pick(CLAUSE_SUBJ, i);
      const v = pick(CLAUSE_VERBS, i * 3 + 1);
      const vv = sgSubject ? `${v}s` : v;
      const [b] = pick(VERBS, i * 7 + 2);
      const t = pick(PLACES, i * 5 + 3);
      return mk(`${s} ${vv} him to ${b} ${t}.`, `${s} ${vv} that he ${b} ${t}.`,
        `"${v}" takes a that-clause, not an object plus infinitive.`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [s] = pick(CLAUSE_SUBJ, i * 3 + 1);
      const v = pick(CLAUSE_VERBS_PAST, i * 7 + 2);
      const [b] = pick(VERBS, i * 5 + 3);
      const t = pick(PLACES, i);
      return mk(`${s} ${v} him to ${b} ${t}.`, `${s} ${v} that he ${b} ${t}.`,
        `With "${v}" use "that he ${b}", not "him to ${b}".`);
    });
  }
  return pool40((i) => {
    const [s] = pick(CLAUSE_SUBJ, i * 5 + 1);
    const v = pick(CLAUSE_VERBS_PAST, i * 3 + 2);
    const [b] = pick(VERBS, i * 7 + 1);
    const t = pick(TAILS_COMPLEX, i);
    return mk(`${cap(t)}, ${s} ${v} him to ${b}.`, `${cap(t)}, ${s} ${v} that he ${b}.`,
      `"${v}" still requires a that-clause, not an object plus infinitive.`);
  });
}

export default {
  '6.1': auxVerbForm,
  '6.2': finiteMainVerb,
  '6.3': missingCopula,
  '6.4': passiveFormation,
  '6.5': intransitivePassive,
  '6.6': stativeProgressive,
  '6.7': tenseConsistency,
  '6.8': transitivity,
  '6.9': gerundInfinitive,
  '6.10': toBaseForm,
  '6.11': phrasalVerbs,
  '6.12': modalsSemi,
  '6.13': questionFormation,
  '6.14': negation,
  '6.15': imperatives,
  '6.16': conditionals,
  '6.17': subjunctiveWish,
  '6.18': reportedSpeech,
  '6.19': causatives,
  '6.20': verbClause,
};
