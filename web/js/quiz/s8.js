// Section 8 — Prepositions. One builder per rule; 40 items per tier.
import {
  pick, mk, pool40, cartesian, TAILS_SIMPLE, TAILS_COMPLEX,
} from './core.js';

const SING = ['She', 'He', 'Tom', 'Anna', 'The team', 'The company', 'My father',
  'The manager', 'The student', 'The government'];

// ---- 8.1 Wrong preposition ----------------------------------------------
const VP = [
  ['depends', 'on', 'in', 'the weather'],
  ['relies', 'on', 'at', 'public transport'],
  ['insists', 'on', 'for', 'a written apology'],
  ['concentrates', 'on', 'in', 'the main problem'],
  ['believes', 'in', 'on', 'honesty'],
  ['succeeds', 'in', 'at', 'difficult exams'],
  ['results', 'in', 'on', 'a serious delay'],
  ['approves', 'of', 'for', 'the new plan'],
  ['dreams', 'of', 'on', 'living abroad'],
  ['worries', 'about', 'on', 'the final exam'],
  ['talks', 'about', 'on', 'the new project'],
  ['cares', 'about', 'of', 'the environment'],
  ['apologizes', 'for', 'of', 'the mistake'],
  ['waits', 'for', 'on', 'the bus'],
  ['hopes', 'for', 'on', 'better weather'],
  ['looks', 'for', 'at', 'a new job'],
  ['listens', 'to', 'for', 'the radio'],
  ['belongs', 'to', 'in', 'a local club'],
  ['refers', 'to', 'at', 'the first chapter'],
  ['deals', 'with', 'to', 'difficult customers'],
  ['copes', 'with', 'to', 'the pressure'],
  ['suffers', 'from', 'of', 'bad headaches'],
  ['differs', 'from', 'than', 'the original'],
  ['arrives', 'at', 'in', 'the station'],
  ['laughs', 'at', 'on', 'the joke'],
  ['aims', 'at', 'to', 'the target'],
  ['objects', 'to', 'for', 'the decision'],
  ['adapts', 'to', 'for', 'the new rules'],
  ['complains', 'about', 'on', 'the noise'],
  ['participates', 'in', 'at', 'the race'],
];

function wrongPreposition(d) {
  if (d === 'easy') {
    return cartesian([VP, SING], ([v, good, bad, o], s) => mk(`${s} ${v} ${bad} ${o}.`,
      `${s} ${v} ${good} ${o}.`, `"${v}" is followed by "${good}", not "${bad}".`));
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [v, good, bad, o] = pick(VP, i * 5 + 1);
      const s = pick(SING, i * 3 + 2);
      const t = pick(TAILS_SIMPLE, i * 7 + 3);
      return mk(`${s} ${v} ${bad} ${o} ${t}.`, `${s} ${v} ${good} ${o} ${t}.`,
        `Even with "${t}", "${v}" still takes "${good}".`);
    });
  }
  return pool40((i) => {
    const [v, good, bad, o] = pick(VP, i * 7 + 1);
    const s = pick(SING, i * 3 + 2);
    const t = pick(TAILS_COMPLEX, i * 5 + 3);
    return mk(`${s} ${v} ${bad} ${o} ${t}.`, `${s} ${v} ${good} ${o} ${t}.`,
      `The fixed phrase is "${v} ${good}", not "${v} ${bad}".`);
  });
}

// ---- 8.2 Missing preposition --------------------------------------------
const MISS = [
  ['listens', 'to', 'music'],
  ['waits', 'for', 'the train'],
  ['looks', 'for', 'the keys'],
  ['depends', 'on', 'the weather'],
  ['arrives', 'at', 'the airport'],
  ['laughs', 'at', 'the joke'],
  ['asks', 'for', 'help'],
  ['cares', 'about', 'the environment'],
  ['thinks', 'about', 'the offer'],
  ['hopes', 'for', 'good news'],
  ['apologizes', 'for', 'the delay'],
  ['belongs', 'to', 'a chess club'],
  ['refers', 'to', 'the appendix'],
  ['agrees', 'with', 'the manager'],
  ['deals', 'with', 'angry customers'],
  ['suffers', 'from', 'allergies'],
  ['concentrates', 'on', 'the lesson'],
  ['relies', 'on', 'the schedule'],
  ['insists', 'on', 'a receipt'],
  ['believes', 'in', 'fair play'],
  ['succeeds', 'in', 'business'],
  ['participates', 'in', 'the race'],
  ['results', 'in', 'a warning'],
  ['comments', 'on', 'the article'],
  ['invests', 'in', 'new technology'],
  ['wonders', 'about', 'the outcome'],
  ['forgets', 'about', 'the meeting'],
  ['worries', 'about', 'the deadline'],
];

function missingPreposition(d) {
  if (d === 'easy') {
    return cartesian([MISS, SING], ([v, p, o], s) => mk(`${s} ${v} ${o}.`,
      `${s} ${v} ${p} ${o}.`, `"${v}" needs the preposition "${p}": "${v} ${p} ${o}".`));
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [v, p, o] = pick(MISS, i * 5 + 1);
      const s = pick(SING, i * 3 + 2);
      const t = pick(TAILS_SIMPLE, i * 7 + 3);
      return mk(`${s} ${v} ${o} ${t}.`, `${s} ${v} ${p} ${o} ${t}.`,
        `The preposition "${p}" is still required before "${o}".`);
    });
  }
  return cartesian([MISS, SING, TAILS_COMPLEX], ([v, p, o], s, t) => mk(
    `${s} ${v} ${o} ${t}.`, `${s} ${v} ${p} ${o} ${t}.`,
    `Do not drop "${p}" before "${o}", even in a longer sentence.`,
  ));
}

// ---- 8.3 Unnecessary preposition ----------------------------------------
const UNNEC = [
  ['discusses', 'about', 'the new plan'],
  ['mentions', 'about', 'the change'],
  ['emphasizes', 'on', 'the main point'],
  ['investigates', 'into', 'the accident'],
  ['approaches', 'to', 'the building'],
  ['enters', 'into', 'the room'],
  ['reaches', 'at', 'the summit'],
  ['marries', 'with', 'her colleague'],
  ['resembles', 'to', 'her mother'],
  ['lacks', 'of', 'experience'],
  ['attends', 'to', 'the meeting'],
  ['contacts', 'with', 'the office'],
  ['obeys', 'to', 'the rules'],
  ['requests', 'for', 'a loan'],
  ['orders', 'for', 'more supplies'],
  ['seeks', 'for', 'new opportunities'],
  ['awaits', 'for', 'the results'],
  ['comprises', 'of', 'three parts'],
  ['joins', 'with', 'the team'],
  ['affects', 'on', 'the outcome'],
  ['answers', 'to', 'the question'],
  ['reports', 'about', 'the incident'],
  ['considers', 'about', 'the proposal'],
  ['completes', 'of', 'the task'],
  ['enters', 'into', 'the competition'],
  ['discusses', 'on', 'the budget'],
  ['mentions', 'of', 'the delay'],
  ['emphasizes', 'about', 'the deadline'],
];

function unnecessaryPreposition(d) {
  if (d === 'easy') {
    return cartesian([UNNEC, SING], ([v, bad, o], s) => mk(`${s} ${v} ${bad} ${o}.`,
      `${s} ${v} ${o}.`,
      `"${v}" takes a direct object, so the preposition "${bad}" is unnecessary.`));
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [v, bad, o] = pick(UNNEC, i * 5 + 1);
      const s = pick(SING, i * 3 + 2);
      const t = pick(TAILS_SIMPLE, i * 7 + 3);
      return mk(`${s} ${v} ${bad} ${o} ${t}.`, `${s} ${v} ${o} ${t}.`,
        `Drop "${bad}": "${v}" is followed directly by "${o}".`);
    });
  }
  return cartesian([UNNEC, SING, TAILS_COMPLEX], ([v, bad, o], s, t) => mk(
    `${s} ${v} ${bad} ${o} ${t}.`, `${s} ${v} ${o} ${t}.`,
    `The extra "${bad}" is wrong; "${v}" needs no preposition.`,
  ));
}

// ---- 8.4 Adjective + preposition ----------------------------------------
const AP = [
  ['interested', 'in', 'on', 'art'],
  ['good', 'at', 'in', 'maths'],
  ['afraid', 'of', 'from', 'dogs'],
  ['proud', 'of', 'for', 'her work'],
  ['famous', 'for', 'of', 'its food'],
  ['married', 'to', 'with', 'a teacher'],
  ['similar', 'to', 'with', 'the original'],
  ['different', 'from', 'than', 'the others'],
  ['responsible', 'for', 'of', 'the report'],
  ['capable', 'of', 'in', 'great things'],
  ['fond', 'of', 'on', 'classical music'],
  ['keen', 'on', 'in', 'sports'],
  ['aware', 'of', 'from', 'the danger'],
  ['dependent', 'on', 'of', 'the weather'],
  ['worried', 'about', 'of', 'the deadline'],
  ['excited', 'about', 'for', 'the trip'],
  ['surprised', 'at', 'of', 'the news'],
  ['pleased', 'with', 'on', 'the result'],
  ['satisfied', 'with', 'on', 'the service'],
  ['angry', 'with', 'on', 'her friend'],
  ['ready', 'for', 'to', 'the exam'],
  ['suitable', 'for', 'to', 'the job'],
  ['accustomed', 'to', 'with', 'the noise'],
  ['allergic', 'to', 'with', 'cats'],
  ['guilty', 'of', 'for', 'the crime'],
  ['typical', 'of', 'for', 'his behaviour'],
  ['proud', 'of', 'from', 'his family'],
  ['good', 'at', 'of', 'football'],
  ['interested', 'in', 'at', 'history'],
  ['famous', 'for', 'as', 'its beaches'],
];
const DEGREE = ['very', 'really', 'quite', 'deeply'];

function adjectivePreposition(d) {
  if (d === 'easy') {
    return cartesian([AP, SING], ([adj, good, bad, o], s) => mk(`${s} is ${adj} ${bad} ${o}.`,
      `${s} is ${adj} ${good} ${o}.`,
      `The adjective "${adj}" goes with "${good}", not "${bad}".`));
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [adj, good, bad, o] = pick(AP, i * 5 + 1);
      const s = pick(SING, i * 3 + 2);
      const deg = pick(DEGREE, i * 7 + 3);
      return mk(`${s} is ${deg} ${adj} ${bad} ${o}.`, `${s} is ${deg} ${adj} ${good} ${o}.`,
        `"${adj}" still takes "${good}", regardless of "${deg}".`);
    });
  }
  return pool40((i) => {
    const [adj, good, bad, o] = pick(AP, i * 7 + 1);
    const s = pick(SING, i * 3 + 2);
    const t = pick(TAILS_COMPLEX, i * 5 + 3);
    return mk(`${s} is ${adj} ${bad} ${o} ${t}.`, `${s} is ${adj} ${good} ${o} ${t}.`,
      `The fixed pair is "${adj} ${good}", not "${adj} ${bad}".`);
  });
}

// ---- 8.5 Time and place (in / on / at) ----------------------------------
const TIME = [
  ['5 pm', 'at', 'on'], ['noon', 'at', 'in'], ['midnight', 'at', 'on'], ['night', 'at', 'in'],
  ['Monday', 'on', 'in'], ['Fridays', 'on', 'at'], ['1 May', 'on', 'in'],
  ['my birthday', 'on', 'in'], ['Christmas', 'at', 'on'], ['July', 'in', 'on'],
  ['2020', 'in', 'at'], ['winter', 'in', 'on'], ['the morning', 'in', 'at'],
  ['the afternoon', 'in', 'on'], ['the evening', 'in', 'at'], ["ten o'clock", 'at', 'on'],
  ['the weekend', 'at', 'in'], ['Tuesday morning', 'on', 'in'],
];
const PLACE = [
  ['the room', 'in', 'on'], ['the kitchen', 'in', 'at'], ['home', 'at', 'in'],
  ['the station', 'at', 'in'], ['the door', 'at', 'on'], ['the table', 'on', 'in'],
  ['the wall', 'on', 'at'], ['the floor', 'on', 'in'], ['the bus', 'on', 'at'],
  ['school', 'at', 'in'], ['the park', 'in', 'at'], ['London', 'in', 'at'],
  ['the airport', 'at', 'in'], ['the bus stop', 'at', 'on'], ['the beach', 'on', 'in'],
  ['the garden', 'in', 'on'], ['the mountains', 'in', 'on'], ['the car', 'in', 'on'],
  ['the farm', 'on', 'in'], ['the office', 'at', 'on'],
];
const MEET_WHO = ['We will meet', 'They will meet', 'She will arrive', 'He will arrive',
  'We will gather', 'They will gather', 'My friends will meet', 'The guests will arrive'];
const WERE_WHO = ['We were', 'They were', 'She was', 'He was', 'The children were',
  'My friends were', 'The visitors were', 'Our family was'];
const MIX_WHO = ['We finally met', 'They finally met', 'She waited', 'He waited',
  'The group gathered', 'My friends arrived', 'The students waited'];

function timePlace(d) {
  if (d === 'easy') {
    return cartesian([TIME, MEET_WHO], ([phrase, good, bad], w) => mk(
      `${w} ${bad} ${phrase}.`, `${w} ${good} ${phrase}.`,
      `Use "${good}" with "${phrase}": "${good} ${phrase}".`,
    ));
  }
  if (d === 'medium') {
    return cartesian([PLACE, WERE_WHO], ([phrase, good, bad], w) => mk(
      `${w} ${bad} ${phrase}.`, `${w} ${good} ${phrase}.`,
      `The place "${phrase}" takes "${good}", not "${bad}".`,
    ));
  }
  return pool40((i) => {
    const t = pick(TAILS_COMPLEX, i * 5 + 1);
    const w = pick(MIX_WHO, i * 3 + 2);
    if (i % 2 === 0) {
      const [phrase, good, bad] = pick(TIME, i * 7 + 3);
      return mk(`${w} ${bad} ${phrase} ${t}.`, `${w} ${good} ${phrase} ${t}.`,
        `Even in this sentence, "${phrase}" takes "${good}".`);
    }
    const [phrase, good, bad] = pick(PLACE, i * 7 + 4);
    return mk(`${w} ${bad} ${phrase} ${t}.`, `${w} ${good} ${phrase} ${t}.`,
      `The place "${phrase}" still takes "${good}".`);
  });
}

// ---- 8.6 Preposition + gerund -------------------------------------------
const PG = [
  ['looks forward to', 'see', 'seeing', 'you'],
  ['is interested in', 'learn', 'learning', 'Spanish'],
  ['is good at', 'swim', 'swimming', 'long distances'],
  ['is fond of', 'read', 'reading', 'old novels'],
  ['thinks about', 'move', 'moving', 'to Canada'],
  ['dreams of', 'travel', 'travelling', 'around the world'],
  ['insists on', 'pay', 'paying', 'in cash'],
  ['succeeds in', 'pass', 'passing', 'the final exam'],
  ['worries about', 'lose', 'losing', 'her keys'],
  ['apologizes for', 'arrive', 'arriving', 'so late'],
  ['is capable of', 'solve', 'solving', 'hard problems'],
  ['is tired of', 'wait', 'waiting', 'in queues'],
  ['is afraid of', 'fly', 'flying', 'at night'],
  ['is keen on', 'paint', 'painting', 'landscapes'],
  ['is used to', 'get up', 'getting up', 'early'],
  ['is excited about', 'start', 'starting', 'the new job'],
  ['is responsible for', 'manage', 'managing', 'the budget'],
  ['is proud of', 'represent', 'representing', 'her country'],
  ['believes in', 'tell', 'telling', 'the truth'],
  ['succeeds in', 'finish', 'finishing', 'on time'],
  ['is interested in', 'join', 'joining', 'the club'],
  ['is good at', 'organize', 'organizing', 'events'],
  ['dreams of', 'become', 'becoming', 'a pilot'],
  ['thinks about', 'study', 'studying', 'abroad'],
  ['apologizes for', 'break', 'breaking', 'the vase'],
  ['worries about', 'miss', 'missing', 'the train'],
  ['is fond of', 'collect', 'collecting', 'stamps'],
  ['is capable of', 'handle', 'handling', 'the pressure'],
  ['is tired of', 'do', 'doing', 'the same thing'],
  ['looks forward to', 'meet', 'meeting', 'the team'],
  ['insists on', 'do', 'doing', 'it himself'],
  ['is used to', 'work', 'working', 'night shifts'],
  ['is afraid of', 'make', 'making', 'mistakes'],
  ['is keen on', 'play', 'playing', 'chess'],
  ['is excited about', 'visit', 'visiting', 'the museum'],
  ['is responsible for', 'train', 'training', 'new staff'],
  ['is proud of', 'win', 'winning', 'the contest'],
  ['believes in', 'give', 'giving', 'second chances'],
];

function prepositionGerund(d) {
  if (d === 'easy') {
    return cartesian([PG, SING], ([ph, base, ing, o], s) => mk(`${s} ${ph} ${base} ${o}.`,
      `${s} ${ph} ${ing} ${o}.`,
      `After the preposition in "${ph}", use the gerund "${ing}".`));
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [ph, base, ing, o] = pick(PG, i * 5 + 1);
      const s = pick(SING, i * 3 + 2);
      const t = pick(TAILS_SIMPLE, i * 7 + 3);
      return mk(`${s} ${ph} ${base} ${o} ${t}.`, `${s} ${ph} ${ing} ${o} ${t}.`,
        `The gerund "${ing}" is required after "${ph}".`);
    });
  }
  return pool40((i) => {
    const [ph, base, ing, o] = pick(PG, i * 7 + 1);
    const s = pick(SING, i * 3 + 2);
    const t = pick(TAILS_COMPLEX, i * 5 + 3);
    return mk(`${s} ${ph} ${base} ${o} ${t}.`, `${s} ${ph} ${ing} ${o} ${t}.`,
      `After "${ph}" the verb must be the gerund "${ing}".`);
  });
}

export default {
  '8.1': wrongPreposition,
  '8.2': missingPreposition,
  '8.3': unnecessaryPreposition,
  '8.4': adjectivePreposition,
  '8.5': timePlace,
  '8.6': prepositionGerund,
};
