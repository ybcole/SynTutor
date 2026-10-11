// Section 5 — Pronouns. One builder per rule; each returns 40 items per tier.
import {
  OBJECTS, TAILS_SIMPLE, TAILS_COMPLEX,
  pick, mk, pool40, cap,
} from './core.js';

// mixed-radix index decomposition so a small number of pools still yields
// many distinct combinations (injective for i < product of the radices).
const mix = (i, lenses) => {
  const out = [];
  let n = i;
  for (const L of lenses) { out.push(((n % L) + L) % L); n = Math.floor(n / L); }
  return out;
};

const TIME_TAILS = ['yesterday', 'last week', 'this morning', 'after lunch', 'on Sunday'];

// ---- 5.1 Case, simple ----------------------------------------------------
const SUBJ_CASE = [
  ['I', 'me', 'am'], ['he', 'him', 'is'], ['she', 'her', 'is'],
  ['we', 'us', 'are'], ['they', 'them', 'are'],
];
const CASE_PREDS = [
  'ready', 'late', 'tired', 'hungry', 'happy', 'at school', 'at home',
  'in the park', 'very kind', 'quite busy', 'in a hurry', 'at work',
  'ready to leave', 'happy with the result', 'sure about the plan',
  'careful with money', 'proud of the team', 'always on time',
  'never afraid', 'quite serious', 'fond of music',
];
const PAIR_OBJ = [
  ['you and me', 'you and I'], ['Tom and me', 'Tom and I'],
  ['her and me', 'her and I'], ['him and me', 'him and I'],
  ['the boys and me', 'the boys and I'], ['my friends and me', 'my friends and I'],
  ['the teacher and me', 'the teacher and I'], ['Anna and me', 'Anna and I'],
  ['my parents and me', 'my parents and I'], ['the children and me', 'the children and I'],
];
const PREP_FRAMES = [
  'The secret stays between {P}.', 'This small gift is for {P}.',
  'She sat quietly next to {P}.', 'He walked home with {P}.',
  'The letter was addressed to {P}.', 'They stood together behind {P}.',
  'The good news came from {P}.', 'The dog ran towards {P}.',
];
const OBJ_CASE = [['me', 'I'], ['him', 'he'], ['her', 'she'], ['us', 'we'], ['them', 'they']];
const LONG_VP = [
  'quietly handed the keys to', 'finally sent the report to',
  'reluctantly gave the seat to', 'read the whole story to',
  'explained the new plan to', 'whispered the answer to',
  'passed the heavy box to', 'mailed the small parcel to',
];
const SUBJ_LONG = [
  'the guard', 'the driver', 'the teacher', 'the manager', 'my brother',
  'my sister', 'the neighbour', 'the shopkeeper', 'the receptionist',
  'the coach', 'the waiter', 'the nurse',
];

function caseSimple(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [si, pi] = mix(i, [SUBJ_CASE.length, CASE_PREDS.length]);
      const [subj, obj, be] = pick(SUBJ_CASE, si);
      const pred = pick(CASE_PREDS, pi);
      return mk(`${cap(obj)} ${be} ${pred}.`, `${cap(subj)} ${be} ${pred}.`,
        `A subject takes the subject pronoun "${subj}"; "${obj}" is the object form.`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [pip, fi] = mix(i, [PAIR_OBJ.length, PREP_FRAMES.length]);
      const [goodP, badP] = pick(PAIR_OBJ, pip);
      const frame = pick(PREP_FRAMES, fi);
      return mk(frame.replace('{P}', badP), frame.replace('{P}', goodP),
        `After a preposition use the object pronoun: "${goodP}", not "${badP}".`);
    });
  }
  return pool40((i) => {
    const [ti, oi, vi] = mix(i, [TAILS_COMPLEX.length, OBJ_CASE.length, LONG_VP.length]);
    const tail = pick(TAILS_COMPLEX, ti);
    const [obj, wrong] = pick(OBJ_CASE, oi);
    const vp = pick(LONG_VP, vi);
    const subj = pick(SUBJ_LONG, i * 2 + 1);
    return mk(`${cap(tail)}, ${subj} ${vp} ${wrong}.`, `${cap(tail)}, ${subj} ${vp} ${obj}.`,
      `The object of "${vp}" needs "${obj}"; "${wrong}" is the subject form.`);
  });
}

// ---- 5.2 Case in coordination and comparison -----------------------------
const COORD_SUBJ = [
  ['He and I', 'Me and him'], ['She and I', 'Her and me'],
  ['He and she', 'Him and her'], ['They and I', 'Them and me'],
  ['We and they', 'Us and them'], ['Tom and I', 'Tom and me'],
  ['Anna and I', 'Anna and me'], ['He and Tom', 'Him and Tom'],
  ['She and Anna', 'Her and Anna'], ['The teacher and I', 'The teacher and me'],
];
const COORD_VPS = [
  'went to the market', 'were late again', 'played football', 'finished the work',
  'arrived early', 'cleaned the room', 'watched a film', 'cooked dinner',
];
const COORD_OK = ['my brother and me', 'my sister and me', 'Tom and me', 'the boys and me',
  'my friends and me', 'her and me', 'him and me', 'my parents and me'];
const COORD_BAD = ['my brother and I', 'my sister and I', 'Tom and I', 'the boys and I',
  'my friends and I', 'her and I', 'him and I', 'my parents and I'];
const COORD_AGENTS = ['The teacher', 'The manager', 'Tom', 'Anna', 'The coach',
  'My neighbour', 'The doctor', 'The principal', 'The guide', 'Mr Lee'];
const COORD_VERBS = ['thanked', 'invited', 'met', 'helped', 'joined', 'visited', 'called', 'photographed'];
const HARD_COORD_OK = ['my colleagues and I', 'the other students and I', 'my parents and I',
  'the neighbours and I', 'my classmates and I', 'the volunteers and I', 'my cousins and I',
  'the committee and I', 'my teammates and I', 'the staff and I'];
const HARD_COORD_BAD = ['my colleagues and me', 'the other students and me', 'my parents and me',
  'the neighbours and me', 'my classmates and me', 'the volunteers and me', 'my cousins and me',
  'the committee and me', 'my teammates and me', 'the staff and me'];
const HARD_VPS = ['decided to continue', 'managed to finish', 'agreed to help', 'offered to wait',
  'volunteered to lead', 'promised to return', 'refused to leave', 'planned to object'];

function coordinated(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [ci, vi] = mix(i, [COORD_SUBJ.length, COORD_VPS.length]);
      const [goodS, badS] = pick(COORD_SUBJ, ci);
      const vp = pick(COORD_VPS, vi);
      const t = pick(TIME_TAILS, i);
      return mk(`${badS} ${vp} ${t}.`, `${goodS} ${vp} ${t}.`,
        `A compound subject takes subject pronouns: "${goodS}", not "${badS}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [oi, vi, ai] = mix(i, [COORD_OK.length, COORD_VERBS.length, COORD_AGENTS.length]);
      const goodO = pick(COORD_OK, oi);
      const badO = pick(COORD_BAD, oi);
      const verb = pick(COORD_VERBS, vi);
      const agent = pick(COORD_AGENTS, ai);
      return mk(`${agent} ${verb} ${badO}.`, `${agent} ${verb} ${goodO}.`,
        `As the object of a verb use "${goodO}"; "${badO}" wrongly uses the subject form.`);
    });
  }
  return pool40((i) => {
    const [ci, vi] = mix(i, [HARD_COORD_OK.length, HARD_VPS.length]);
    const goodS = pick(HARD_COORD_OK, ci);
    const badS = pick(HARD_COORD_BAD, ci);
    const vp = pick(HARD_VPS, vi);
    const tail = pick(TAILS_COMPLEX, i * 3 + 1);
    const obj = pick(OBJECTS, i);
    return mk(`${cap(tail)}, ${badS} ${vp} ${obj}.`, `${cap(tail)}, ${goodS} ${vp} ${obj}.`,
      `The compound subject needs "${goodS}", not the object form "${badS}".`);
  });
}

// ---- 5.3 Ambiguous reference ---------------------------------------------
const MALE = ['Tom', 'Sam', 'Ben', 'Jack', 'Leo', 'Omar', 'Paul', 'Kai', 'Raj', 'Ivan'];
const FEMALE = ['Anna', 'Lucy', 'Mia', 'Zoe', 'Emma', 'Sara', 'Nina', 'Rita', 'Dana', 'Lena'];
const AMB_PAIRS = [];
for (const a of MALE) for (const b of MALE) if (a !== b) AMB_PAIRS.push([a, b, 'he']);
for (const a of FEMALE) for (const b of FEMALE) if (a !== b) AMB_PAIRS.push([a, b, 'she']);

const AMB_EASY = [
  [(a, b, p) => `${a} told ${b} that ${p} had passed the exam.`, (a, b, r) => `${a} told ${b} that ${r} had passed the exam.`],
  [(a, b, p) => `${a} asked ${b} if ${p} could help.`, (a, b, r) => `${a} asked ${b} if ${r} could help.`],
  [(a, b, p) => `${a} reminded ${b} that ${p} was late.`, (a, b, r) => `${a} reminded ${b} that ${r} was late.`],
  [(a, b, p) => `${a} promised ${b} that ${p} would call.`, (a, b, r) => `${a} promised ${b} that ${r} would call.`],
  [(a, b, p) => `${a} told ${b} that ${p} felt tired.`, (a, b, r) => `${a} told ${b} that ${r} felt tired.`],
  [(a, b, p) => `${a} warned ${b} that ${p} was in danger.`, (a, b, r) => `${a} warned ${b} that ${r} was in danger.`],
];
const AMB_MED = [
  [(a, b, p) => `${a} told ${b} at the station that ${p} had taken the early train.`, (a, b, r) => `${a} told ${b} at the station that ${r} had taken the early train.`],
  [(a, b, p) => `${a} asked ${b} quietly whether ${p} had finished the report.`, (a, b, r) => `${a} asked ${b} quietly whether ${r} had finished the report.`],
  [(a, b, p) => `${a} reminded ${b} before the meeting that ${p} needed to sign the form.`, (a, b, r) => `${a} reminded ${b} before the meeting that ${r} needed to sign the form.`],
  [(a, b, p) => `${a} promised ${b} after lunch that ${p} would return the book.`, (a, b, r) => `${a} promised ${b} after lunch that ${r} would return the book.`],
  [(a, b, p) => `${a} wrote to ${b} saying that ${p} had found the missing key.`, (a, b, r) => `${a} wrote to ${b} saying that ${r} had found the missing key.`],
  [(a, b, p) => `${a} told ${b} in the office that ${p} had been promoted.`, (a, b, r) => `${a} told ${b} in the office that ${r} had been promoted.`],
];
const AMB_HARD = [
  [(a, b, p) => `Although the deadline was close, ${a} told ${b} that ${p} had already submitted the final draft.`, (a, b, r) => `Although the deadline was close, ${a} told ${b} that ${r} had already submitted the final draft.`],
  [(a, b, p) => `When the results were announced, ${a} asked ${b} whether ${p} had expected such a high mark.`, (a, b, r) => `When the results were announced, ${a} asked ${b} whether ${r} had expected such a high mark.`],
  [(a, b, p) => `${a} reminded ${b}, just as the guests were leaving, that ${p} still had the key.`, (a, b, r) => `${a} reminded ${b}, just as the guests were leaving, that ${r} still had the key.`],
  [(a, b, p) => `After the long argument, ${a} told ${b} that ${p} should apologise first.`, (a, b, r) => `After the long argument, ${a} told ${b} that ${r} should apologise first.`],
  [(a, b, p) => `${a} whispered to ${b}, while the music played, that ${p} had won the prize.`, (a, b, r) => `${a} whispered to ${b}, while the music played, that ${r} had won the prize.`],
  [(a, b, p) => `${a} wrote to ${b} after the conference that ${p} had impressed the committee.`, (a, b, r) => `${a} wrote to ${b} after the conference that ${r} had impressed the committee.`],
];
function ambiguous(d) {
  const frames = d === 'easy' ? AMB_EASY : d === 'medium' ? AMB_MED : AMB_HARD;
  return pool40((i) => {
    const [fi, pi] = mix(i, [frames.length, AMB_PAIRS.length]);
    const [badF, goodF] = pick(frames, fi);
    const [a, b, p] = pick(AMB_PAIRS, pi);
    const r = i % 2 === 0 ? a : b;
    return mk(badF(a, b, p), goodF(a, b, r),
      `"${p}" is ambiguous: it could refer to ${a} or to ${b}. Naming the intended person removes the ambiguity.`);
  });
}

// ---- 5.4 Relative pronoun choice -----------------------------------------
const REL_PERSON = ['man', 'woman', 'boy', 'girl', 'child', 'teacher', 'student', 'doctor',
  'driver', 'worker', 'farmer', 'nurse', 'player', 'friend', 'brother', 'sister', 'mother',
  'father', 'actor', 'actress'];
const REL_THING = ['book', 'car', 'house', 'tree', 'phone', 'table', 'chair', 'window', 'door',
  'garden', 'river', 'mountain', 'village', 'city', 'office', 'box', 'watch', 'letter',
  'picture', 'song'];
const PERSON_REL = [
  ['lives next door', 'is a doctor'], ['called you yesterday', 'is my aunt'],
  ['won the prize', 'is very happy'], ['teaches at our school', 'is quite strict'],
  ['works at the hospital', 'is always busy'], ['helped me yesterday', 'is a good friend'],
  ['drives a taxi', 'works at night'], ['sings beautifully', 'is from our village'],
  ['studies medicine', 'is very clever'], ['fixed the fence', 'lives across the road'],
];
const THING_REL = [
  ['stands on the hill', 'is very old'], ['broke yesterday', 'costs too much'],
  ['arrived this morning', 'came from overseas'], ['smells fresh', 'was baked today'],
  ['fell in the storm', 'belonged to my aunt'], ['has a red cover', 'is on the shelf'],
  ['runs very fast', 'belongs to my father'], ['faces the garden', 'gets a lot of sun'],
  ['needs repairing', 'is in the garage'], ['was written last year', 'won a prize'],
];
const OBJ_CLAUSES_P = ['I met yesterday', 'the teacher praised', 'we visited last week',
  'my father knows', 'she thanked at the party', 'the manager hired'];
const OBJ_MAINS_P = ['is very kind', 'won the prize', 'moved away last year',
  'works at the bank', 'is a close friend', 'was elected captain'];
const OBJ_CLAUSES_T = ['I bought last week', 'she found in the attic', 'my father repaired',
  'we saw at the market', 'the children broke', 'he mentioned yesterday'];
const OBJ_MAINS_T = ['is very useful', 'was rather expensive', 'belongs to the museum',
  'looks quite old', 'still works perfectly', 'needs a new part'];
const POSS_REL = [
  ['son', 'won the race'], ['daughter', 'studies abroad'], ['car', 'was stolen'],
  ['house', 'caught fire'], ['dog', 'ran away'], ['team', 'lost the final'],
  ['father', 'owns the shop'], ['brother', 'plays the guitar'], ['garden', 'needs water'],
  ['bicycle', 'has a flat tyre'],
];
const WHOSE_MAINS = ['is my neighbour', 'lives nearby', 'called the police',
  'was very upset', 'works with me', 'moved to the city'];
const P_AGENTS = ['I', 'we', 'they', 'she', 'he'];
const P_PREPS = ['spoke to', 'wrote to', 'complained about', 'argued with', 'referred to', 'voted for'];
const WHOSE_HARD_MAINS = ['was finally rewarded', 'was very proud', 'had to leave early',
  'thanked everyone', 'moved to another town'];

function relative(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [type, ni, ci] = mix(i, [2, REL_PERSON.length, PERSON_REL.length]);
      const isPerson = type === 0;
      const noun = pick(isPerson ? REL_PERSON : REL_THING, ni);
      const [clause, main] = pick(isPerson ? PERSON_REL : THING_REL, ci);
      const wrong = isPerson ? 'which' : 'who';
      const right = isPerson ? 'who' : 'which';
      return mk(`The ${noun} ${wrong} ${clause} ${main}.`, `The ${noun} ${right} ${clause} ${main}.`,
        `Use "${right}" for a ${isPerson ? 'person' : 'thing'}; "${wrong}" is the wrong relative pronoun.`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const kind = i % 3;
      const k = Math.floor(i / 3);
      if (kind === 0) {
        const noun = pick(REL_PERSON, k);
        const clause = pick(OBJ_CLAUSES_P, Math.floor(k / REL_PERSON.length));
        const main = pick(OBJ_MAINS_P, Math.floor(k / 5));
        return mk(`The ${noun} who ${clause} ${main}.`, `The ${noun} whom ${clause} ${main}.`,
          `As the object of the clause, a person takes "whom", not "who".`);
      }
      if (kind === 1) {
        const noun = pick(REL_THING, k);
        const clause = pick(OBJ_CLAUSES_T, Math.floor(k / REL_THING.length));
        const main = pick(OBJ_MAINS_T, Math.floor(k / 5));
        return mk(`The ${noun} who ${clause} ${main}.`, `The ${noun} which ${clause} ${main}.`,
          `For a thing use "which", not "who".`);
      }
      const isPerson = k % 2 === 0;
      const noun = pick(isPerson ? REL_PERSON : REL_THING, Math.floor(k / 2));
      const [possN, possVp] = pick(POSS_REL, Math.floor(k / 5));
      const main = pick(WHOSE_MAINS, Math.floor(k / 3));
      return mk(`The ${noun} which ${possN} ${possVp} ${main}.`, `The ${noun} whose ${possN} ${possVp} ${main}.`,
        `Possession requires "whose", not "which".`);
    });
  }
  return pool40((i) => {
    const kind = i % 4;
    const tail = pick(TAILS_COMPLEX, Math.floor(i / 4));
    if (kind === 0) {
      const noun = pick(REL_PERSON, i);
      const [clause, main] = pick(PERSON_REL, Math.floor(i / 2));
      return mk(`${cap(tail)}, the ${noun} which ${clause} ${main}.`, `${cap(tail)}, the ${noun} who ${clause} ${main}.`,
        `The relative pronoun for the person "${noun}" is "who".`);
    }
    if (kind === 1) {
      const noun = pick(REL_THING, i);
      const [clause, main] = pick(THING_REL, Math.floor(i / 3));
      return mk(`${cap(tail)}, the ${noun} who ${clause} ${main}.`, `${cap(tail)}, the ${noun} which ${clause} ${main}.`,
        `The relative pronoun for the thing "${noun}" is "which".`);
    }
    if (kind === 2) {
      const noun = pick(REL_PERSON, i * 2 + 1);
      const agent = pick(P_AGENTS, i);
      const prep = pick(P_PREPS, i * 2);
      return mk(`${cap(tail)}, the ${noun} who ${agent} ${prep} was very helpful.`,
        `${cap(tail)}, the ${noun} whom ${agent} ${prep} was very helpful.`,
        `As the object of the preposition, a person takes "whom", not "who".`);
    }
    const noun = pick(REL_PERSON, i * 3);
    const [possN, possVp] = pick(POSS_REL, i);
    const main = pick(WHOSE_HARD_MAINS, Math.floor(i / 3));
    return mk(`${cap(tail)}, the ${noun} which ${possN} ${possVp} ${main}.`,
      `${cap(tail)}, the ${noun} whose ${possN} ${possVp} ${main}.`,
      `Possession requires "whose", not "which".`);
  });
}

// ---- 5.5 Dummy it / there -------------------------------------------------
const IT_PREDS = ['raining outside', 'snowing heavily', 'very cold today', 'getting dark',
  'almost six in the evening', 'too late to leave', 'important to sleep well',
  'difficult to say', 'clear that he was wrong', 'a pity that she left', 'time to go',
  'no use complaining', 'easy to forget', 'hard to believe', 'wonderful to see you',
  'strange that nobody called', 'likely to rain tonight', 'worth trying again',
  'dangerous to swim here', 'a shame about the delay'];
const THERE_NP = [
  ['a book on the table', 'is'], ['many people waiting outside', 'are'],
  ['a cat in the garden', 'is'], ['two cars in the drive', 'are'],
  ['some milk in the fridge', 'is'], ['a problem with the plan', 'is'],
  ['plenty of time', 'is'], ['no reason to worry', 'is'], ['a letter for you', 'is'],
  ['several mistakes in the report', 'are'], ['a few chairs in the hall', 'are'],
  ['nobody at the door', 'is'], ['a lot of noise outside', 'is'],
  ['some children in the yard', 'are'], ['an old bridge over the river', 'is'],
  ['three tickets left', 'are'], ['a strange smell in the kitchen', 'is'],
  ['too many rules', 'are'], ['little hope of success', 'is'], ['enough food for everyone', 'is'],
];
const IT_CLAUSES = ['the train has already left', 'she had studied very hard',
  'the weather will improve', 'nobody knew the answer', 'the meeting was cancelled',
  'he had forgotten his keys', 'the road is closed today', 'they will arrive by noon',
  'the project needs more time', 'the prices have gone up'];
const IT_VERBS = ['seems', 'appears', 'is clear', 'was obvious', 'is likely', 'is fortunate',
  'is surprising', 'was unfortunate'];
const THERE_PLACES = ['in the kitchen', 'on the table', 'in the garden', 'near the door',
  'at the station', 'in the office', 'on the bus', 'in the report', 'by the river', 'in the box'];
const HARD_IT_PREDS = ['still dangerous to go outside', 'impossible to read the sign',
  'clear that something had gone wrong', 'obvious that the plan had failed',
  'too late to change the decision', 'essential to act quickly', 'hard to tell who was right',
  'surprising that nobody complained'];
const HARD_IT_PP = ['stated that costs had risen sharply', 'agreed that the deadline would move',
  'announced that the bridge would close', 'reported that the storm had passed',
  'decided that the rules would change', 'proved that the theory was wrong'];
const HARD_THERE_NP = ['a strange silence', 'no one in the room', 'a note on the desk',
  'nothing but dust', 'an unexpected visitor', 'a broken window'];

function dummy(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [type, idx] = mix(i, [2, IT_PREDS.length]);
      if (type === 0) {
        const pred = pick(IT_PREDS, idx);
        return mk(`Is ${pred}.`, `It is ${pred}.`,
          `Weather, time and general statements need the dummy subject "it".`);
      }
      const [np, be] = pick(THERE_NP, idx);
      return mk(`${cap(be)} ${np}.`, `There ${be} ${np}.`,
        `Introducing that something exists needs the dummy subject "there".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const type = i % 2;
      const k = Math.floor(i / 2);
      if (type === 0) {
        const verb = pick(IT_VERBS, k);
        const clause = pick(IT_CLAUSES, Math.floor(k / IT_VERBS.length));
        return mk(`${cap(verb)} that ${clause}.`, `It ${verb} that ${clause}.`,
          `The clause needs the dummy subject "it".`);
      }
      const [np, be] = pick(THERE_NP, k);
      const place = pick(THERE_PLACES, Math.floor(k / THERE_NP.length));
      return mk(`${cap(be)} ${np} ${place}.`, `There ${be} ${np} ${place}.`,
        `The existential sentence needs the dummy subject "there".`);
    });
  }
  return pool40((i) => {
    const kind = i % 3;
    const tail = pick(TAILS_COMPLEX, Math.floor(i / 3));
    if (kind === 0) {
      const pred = pick(HARD_IT_PREDS, i);
      return mk(`${cap(tail)}, was ${pred}.`, `${cap(tail)}, it was ${pred}.`,
        `Even in this long sentence the clause needs the dummy subject "it".`);
    }
    if (kind === 1) {
      const pp = pick(HARD_IT_PP, i);
      return mk(`${cap(tail)}, was ${pp}.`, `${cap(tail)}, it was ${pp}.`,
        `The passive structure needs the dummy subject "it".`);
    }
    const np = pick(HARD_THERE_NP, i);
    const place = pick(THERE_PLACES, i * 2);
    return mk(`${cap(tail)}, was ${np} ${place}.`, `${cap(tail)}, there was ${np} ${place}.`,
      `The existential clause needs the dummy subject "there".`);
  });
}

// ---- 5.6 Possessive pronoun vs determiner --------------------------------
const POSS = [['my', 'mine'], ['your', 'yours'], ['her', 'hers'], ['our', 'ours'], ['their', 'theirs']];
const POSS_THINGS = ['book', 'car', 'house', 'coat', 'bag', 'phone', 'bicycle', 'garden',
  'ticket', 'umbrella', 'camera', 'watch'];
const POSS_FRAMES = ['The {n} is {x}.', 'This {n} is {x}.', 'That {n} is {x}.',
  'Look, the {n} is {x}.', 'I think the {n} is {x}.'];
const POSS_VPS = ['is parked outside', 'was stolen yesterday', 'needs a service',
  'is in the garage', 'broke down again', 'looks brand new', 'belongs to my father',
  'is very old'];
const POSS_HARD_VPS = ['could not be found', 'was left behind', 'broke down again', 'needed a repair'];

function possessivePron(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [pi, ni, fi] = mix(i, [POSS.length, POSS_THINGS.length, POSS_FRAMES.length]);
      const [det, pron] = pick(POSS, pi);
      const noun = pick(POSS_THINGS, ni);
      const frame = pick(POSS_FRAMES, fi);
      return mk(frame.replace('{n}', noun).replace('{x}', det),
        frame.replace('{n}', noun).replace('{x}', pron),
        `Standing alone, the possessive is "${pron}", not "${det}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [pi, ni, vi] = mix(i, [POSS.length, POSS_THINGS.length, POSS_VPS.length]);
      const [det, pron] = pick(POSS, pi);
      const noun = pick(POSS_THINGS, ni);
      const vp = pick(POSS_VPS, vi);
      return mk(`${cap(pron)} ${noun} ${vp}.`, `${cap(det)} ${noun} ${vp}.`,
        `Before a noun use the determiner "${det}", not "${pron}".`);
    });
  }
  return pool40((i) => {
    const kind = i % 2;
    const tail = pick(TAILS_COMPLEX, Math.floor(i / 2));
    const [det, pron] = pick(POSS, i);
    const noun = pick(POSS_THINGS, i * 3 + 1);
    if (kind === 0) {
      return mk(`${cap(tail)}, the ${noun} was not really ${det}.`,
        `${cap(tail)}, the ${noun} was not really ${pron}.`,
        `Used as a predicate, the possessive is "${pron}", not "${det}".`);
    }
    const vp = pick(POSS_HARD_VPS, i * 2 + 1);
    return mk(`${cap(tail)}, ${pron} ${noun} ${vp}.`, `${cap(tail)}, ${det} ${noun} ${vp}.`,
      `Before the noun "${noun}" use the determiner "${det}", not "${pron}".`);
  });
}

// ---- 5.7 Reflexive vs ordinary pronoun ------------------------------------
const REFL_SUBJ = [
  ['I', 'myself', 'am'], ['he', 'himself', 'is'], ['she', 'herself', 'is'],
  ['they', 'themselves', 'are'], ['we', 'ourselves', 'are'], ['you', 'yourself', 'are'],
];
const REFL_PREDS = ['ready', 'late', 'tired', 'happy', 'in a hurry', 'at home',
  'very careful', 'quite sure', 'hungry', 'at school', 'on time', 'proud of the work'];
const COORD_REFLEX_OK = ['My friend and I', 'My sister and I', 'My brother and I',
  'Tom and I', 'Anna and I', 'The teacher and I', 'My parents and I',
  'My colleague and I', 'My neighbour and I', 'My cousin and I'];
const COORD_REFLEX_BAD = ['My friend and myself', 'My sister and myself', 'My brother and myself',
  'Tom and myself', 'Anna and myself', 'The teacher and myself', 'My parents and myself',
  'My colleague and myself', 'My neighbour and myself', 'My cousin and myself'];
const REFLEX_VPS = ['finished the work', 'cleaned the room', 'painted the fence',
  'repaired the roof', 'prepared dinner', 'organised the trip', 'planted the garden',
  'moved the furniture'];
const REFLEX_SUBJ3 = ['the director', 'the manager', 'the committee', 'the coach',
  'the principal', 'the judge', 'the editor', 'the professor'];
const REFLEX_THX = ['thanked', 'praised', 'invited', 'congratulated', 'credited', 'commended'];
const REFLEX_EXTRA = ['for the report', 'for the effort', 'for the success',
  'for the hard work', 'for the results', 'for the contribution'];
const PAIR_OBJ_REFLEX = [
  ['my assistant and me', 'my assistant and myself'],
  ['my brother and me', 'my brother and myself'],
  ['the other volunteers and me', 'the other volunteers and myself'],
  ['my colleagues and me', 'my colleagues and myself'],
  ['the whole team and me', 'the whole team and myself'],
];

function reflexives(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [ri, pi] = mix(i, [REFL_SUBJ.length, REFL_PREDS.length]);
      const [subj, refl, be] = pick(REFL_SUBJ, ri);
      const pred = pick(REFL_PREDS, pi);
      return mk(`${cap(refl)} ${be} ${pred}.`, `${cap(subj)} ${be} ${pred}.`,
        `A reflexive cannot be a subject; use the ordinary pronoun "${subj}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [ci, vi] = mix(i, [COORD_REFLEX_OK.length, REFLEX_VPS.length]);
      const goodS = pick(COORD_REFLEX_OK, ci);
      const badS = pick(COORD_REFLEX_BAD, ci);
      const vp = pick(REFLEX_VPS, vi);
      const tail = pick(TIME_TAILS, i);
      return mk(`${badS} ${vp} ${tail}.`, `${goodS} ${vp} ${tail}.`,
        `In a compound subject use the ordinary pronoun: "${goodS}", not "${badS}".`);
    });
  }
  return pool40((i) => {
    const kind = i % 2;
    const tail = pick(TAILS_COMPLEX, Math.floor(i / 2));
    const subj = pick(REFLEX_SUBJ3, i * 2 + 1);
    const verb = pick(REFLEX_THX, i * 3);
    const extra = pick(REFLEX_EXTRA, i);
    if (kind === 0) {
      return mk(`${cap(tail)}, ${subj} ${verb} myself ${extra}.`,
        `${cap(tail)}, ${subj} ${verb} me ${extra}.`,
        `The object of the verb is "me"; "myself" is only used when the subject is "I".`);
    }
    const goodPair = pick(PAIR_OBJ_REFLEX, i)[0];
    const badPair = pick(PAIR_OBJ_REFLEX, i)[1];
    return mk(`${cap(tail)}, ${subj} ${verb} ${badPair} ${extra}.`,
      `${cap(tail)}, ${subj} ${verb} ${goodPair} ${extra}.`,
      `The object of the verb is "${goodPair}"; "myself" is only used with the subject "I".`);
  });
}

export default {
  '5.1': caseSimple,
  '5.2': coordinated,
  '5.3': ambiguous,
  '5.4': relative,
  '5.5': dummy,
  '5.6': possessivePron,
  '5.7': reflexives,
};
