// Section 2 — Agreement. One builder per rule; each returns 40 items per tier.
import {
  VERBS, NOUNS, SG_SUBJ, PL_SUBJ, NAMES, OBJECTS, TAILS_SIMPLE, TAILS_COMPLEX,
  ADJ, ADV, pick, mk, pool40, cap,
} from './core.js';

const BARE_SG = NOUNS.map(([s]) => s);
const BARE_PL = NOUNS.map(([, p]) => p);

const INTRANS = new Set(['arrive', 'go', 'come', 'live', 'smile', 'hope',
  'decide', 'sleep', 'run', 'jump', 'dance', 'swim', 'fly', 'stand', 'sit']);
const TRANS = VERBS.filter(([b]) => !INTRANS.has(b));

const OBJ3 = ['the letter', 'the car', 'the door', 'the garden', 'the report',
  'the homework', 'the dishes', 'the song', 'the piano', 'the picture'];

const INTER_PL = ['with the bags', 'with the dogs', 'with the children', 'near the rivers',
  'in the gardens', 'by the windows', 'under the tables', 'among the trees',
  'of the cities', 'with the boxes', 'beside the cars', 'near the horses'];
const INTER_SG = ['with the bag', 'with the dog', 'with the child', 'near the river',
  'in the garden', 'by the window', 'under the table', 'beside the car',
  'of the city', 'with the box', 'behind the house', 'near the mountain'];

const COORD_SG = [...NAMES, 'the teacher', 'the boy', 'the girl', 'the dog', 'my friend', 'the child', 'the man'];
const COORD_PL = ['the boys', 'the girls', 'the students', 'the teachers', 'my friends',
  'the children', 'the dogs', 'the men', 'the women', 'the workers'];

const WH = ['Where', 'Why', 'When', 'How', 'What'];

const PLACE7 = ['at home', 'at school', 'in the car', 'on the bus', 'at the office', 'in the park', 'at the station'];

const HABITS = ['every morning', 'after lunch', 'on Mondays', 'at noon', 'before dinner',
  'after school', 'every weekend', 'in the evening'];

// ---- 2.1 Subject-verb, simple -------------------------------------------
function svSimple(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(SG_SUBJ, i);
      const [b, sg] = pick(VERBS, i * 3 + 1);
      const o = pick(OBJ3, i * 7 + 2);
      return mk(cap(`${s} ${b} ${o} every day.`), cap(`${s} ${sg} ${o} every day.`),
        `A singular subject takes "${sg}", not "${b}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(PL_SUBJ, i);
      const [b, sg] = pick(VERBS, i * 5 + 2);
      const o = pick(OBJ3, i * 3 + 1);
      const adv = pick(ADV, i);
      return mk(cap(`${s} ${sg} ${o} ${adv}.`), cap(`${s} ${b} ${o} ${adv}.`),
        `The plural subject "${s}" takes "${b}", not "${sg}".`);
    });
  }
  return pool40((i) => {
    const s = pick(SG_SUBJ, i);
    const [b, sg] = pick(VERBS, i * 7 + 3);
    const o = pick(OBJ3, i * 5 + 1);
    const t = pick(TAILS_COMPLEX, i);
    return mk(cap(`${s} ${b} ${o} ${t}.`), cap(`${s} ${sg} ${o} ${t}.`),
      `Even in this longer sentence the subject "${s}" takes "${sg}".`);
  });
}

// ---- 2.2 Subject-verb across an intervening phrase ----------------------
function svIntervening(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(SG_SUBJ, i);
      const inter = pick(INTER_PL, i * 3 + 1);
      const [b, sg] = pick(VERBS, i * 7 + 2);
      return mk(cap(`${s} ${inter} ${b} home.`), cap(`${s} ${inter} ${sg} home.`),
        `The verb agrees with "${s}", not with the plural noun in "${inter}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(PL_SUBJ, i);
      const inter = pick(INTER_SG, i * 3 + 1);
      const [b, sg] = pick(VERBS, i * 7 + 2);
      return mk(cap(`${s} ${inter} ${sg} home.`), cap(`${s} ${inter} ${b} home.`),
        `The head noun "${s}" is plural, so use "${b}" despite "${inter}".`);
    });
  }
  return pool40((i) => {
    const s = pick(SG_SUBJ, i);
    const inter = pick(INTER_PL, i * 3 + 1);
    const [b, sg] = pick(VERBS, i * 5 + 2);
    const t = pick(TAILS_COMPLEX, i);
    return mk(cap(`${s} ${inter} ${b} home ${t}.`), cap(`${s} ${inter} ${sg} home ${t}.`),
      `Only the head noun "${s}" controls the verb, so use "${sg}".`);
  });
}

// ---- 2.3 Coordinated subjects (and / or / nor) --------------------------
function coordinated(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const a = pick(COORD_SG, i);
      const b = pick(COORD_SG, i * 5 + 1);
      const t = pick(TAILS_SIMPLE, i);
      return mk(`${a} and ${b} is ${t}.`, `${a} and ${b} are ${t}.`,
        `Two subjects joined by "and" take the plural verb "are".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const a = pick(COORD_SG, i);
      const b = pick(COORD_SG, i * 3 + 1);
      const t = pick(TAILS_SIMPLE, i * 7 + 2);
      return mk(`${a} or ${b} are ${t}.`, `${a} or ${b} is ${t}.`,
        `With "or" the verb agrees with the nearer singular subject "${b}".`);
    });
  }
  return pool40((i) => {
    const a = pick(COORD_SG, i);
    const b = pick(COORD_PL, i * 3 + 1);
    const t = pick(TAILS_COMPLEX, i);
    return mk(`Neither ${a} nor ${b} was ready ${t}.`, `Neither ${a} nor ${b} were ready ${t}.`,
      `The verb agrees with the nearer plural subject "${b}", so use "were".`);
  });
}

// ---- 2.4 Existential there ----------------------------------------------
function existential(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const p = pick(BARE_PL, i);
      const t = pick(TAILS_SIMPLE, i * 3 + 1);
      return mk(`There is ${p} ${t}.`, `There are ${p} ${t}.`,
        `The plural noun "${p}" requires "There are".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(BARE_SG, i);
      const t = pick(TAILS_SIMPLE, i * 3 + 1);
      if (i % 2 === 0) {
        return mk(`There were one ${s} ${t}.`, `There was one ${s} ${t}.`,
          `"One ${s}" is singular, so use "There was".`);
      }
      return mk(`There are one ${s} ${t}.`, `There is one ${s} ${t}.`,
        `"One ${s}" is singular, so use "There is".`);
    });
  }
  return pool40((i) => {
    const p = pick(BARE_PL, i);
    const t = pick(TAILS_COMPLEX, i * 3 + 1);
    return mk(`${cap(t)}, there is ${p} on the list.`, `${cap(t)}, there are ${p} on the list.`,
      `The plural noun "${p}" still requires "There are".`);
  });
}

// ---- 2.5 Collective and notional nouns ----------------------------------
const COLLECTIVE = ['team', 'family', 'government', 'committee', 'audience', 'class',
  'group', 'crowd', 'jury', 'board', 'company', 'public', 'union', 'panel', 'army',
  'club', 'choir', 'band', 'firm', 'council', 'staff', 'crew', 'squad', 'orchestra',
  'delegation', 'assembly', 'senate', 'parliament', 'tribunal', 'corporation',
  'agency', 'department', 'faculty', 'gang', 'mob', 'flock', 'herd', 'swarm', 'fleet', 'colony'];
const NOTIONAL = ['police', 'people', 'cattle', 'clergy', 'livestock', 'vermin', 'gentry', 'folk', 'poultry', 'youth'];
const PLACE10 = ['in the city', 'in the village', 'around the station', 'near the river',
  'across the country', 'in the province', 'at the border', 'on the farm', 'in the valley', 'along the coast'];

function collectives(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const c = pick(COLLECTIVE, i);
      const t = pick(TAILS_SIMPLE, i * 3 + 1);
      return mk(`The ${c} are meeting ${t}.`, `The ${c} is meeting ${t}.`,
        `"${c}" is a collective noun and takes a singular verb.`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const c = pick(COLLECTIVE, i);
      const p = pick(BARE_PL, i * 3 + 1);
      const t = pick(TAILS_SIMPLE, i * 7 + 2);
      return mk(`The ${c} of ${p} are ${t}.`, `The ${c} of ${p} is ${t}.`,
        `The head noun "${c}" is a singular collective; "${p}" does not change the verb.`);
    });
  }
  return pool40((i) => {
    const n = pick(NOTIONAL, i);
    const pl = pick(PLACE10, i * 3 + 1);
    const adv = pick(ADV, i);
    const t = pick(TAILS_COMPLEX, i * 7 + 2);
    return mk(`${cap(t)}, the ${n} ${pl} is ${adv} on duty.`, `${cap(t)}, the ${n} ${pl} are ${adv} on duty.`,
      `"${n}" is a notional plural, so it takes "are".`);
  });
}

// ---- 2.6 Questions and inversion ----------------------------------------
function inversion(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const w = pick(WH, i);
      const p = pick(PL_SUBJ, i * 3 + 1);
      const t = pick(TAILS_SIMPLE, i * 7 + 2);
      return mk(`${w} is ${p} ${t}?`, `${w} are ${p} ${t}?`,
        `The plural subject "${p}" requires "are" in the question.`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const p = pick(PL_SUBJ, i);
      const [b] = pick(TRANS, i * 7 + 1);
      const o = pick(OBJ3, i * 3 + 2);
      return mk(`Does ${p} ${b} ${o}?`, `Do ${p} ${b} ${o}?`,
        `With the plural subject "${p}" the question uses "Do".`);
    });
  }
  return pool40((i) => {
    const w = pick(WH, i);
    const s = pick(SG_SUBJ, i * 5 + 1);
    const o = pick(OBJ3, i * 7 + 2);
    const t = pick(TAILS_COMPLEX, i);
    return mk(`${w} are ${s} ${o} ${t}?`, `${w} is ${s} ${o} ${t}?`,
      `The singular subject "${s}" requires "is" even in this long question.`);
  });
}

// ---- 2.7 Relative clauses -----------------------------------------------
function relatives(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(SG_SUBJ, i);
      const [b, sg] = pick(VERBS, i * 3 + 1);
      return mk(`I know ${s} who ${b} very well.`, `I know ${s} who ${sg} very well.`,
        `"Who" refers to the singular "${s}", so the verb is "${sg}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const p = pick(PL_SUBJ, i);
      const [b, sg] = pick(VERBS, i * 5 + 1);
      return mk(`I know ${p} who ${sg} very well.`, `I know ${p} who ${b} very well.`,
        `"Who" refers to the plural "${p}", so the verb is "${b}".`);
    });
  }
  return pool40((i) => {
    const s = pick(SG_SUBJ, i);
    const [b, sg] = pick(VERBS, i * 5 + 1);
    const o = pick(OBJ3, i * 7 + 2);
    const t = pick(TAILS_COMPLEX, i);
    return mk(`Yesterday I finally met ${s} who ${b} ${o} ${t}.`, `Yesterday I finally met ${s} who ${sg} ${o} ${t}.`,
      `The relative pronoun agrees with "${s}", so the verb is "${sg}".`);
  });
}

// ---- 2.8 Indefinite pronouns --------------------------------------------
const INDEF_SG = ['everyone', 'everybody', 'someone', 'somebody', 'anyone', 'anybody',
  'nobody', 'no one', 'each', 'either', 'neither', 'nothing', 'something', 'anything', 'everything', 'one'];
const INDEF_VERB = [['have', 'has'], ['want', 'wants'], ['need', 'needs'], ['like', 'likes'],
  ['know', 'knows'], ['go', 'goes'], ['do', 'does'], ['say', 'says']];
const INDEF_PLACE = ['in the room', 'in the class', 'at the party', 'on the team',
  'in the office', 'at the table', 'in the village', 'on the list'];

function indefinites(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const s = pick(INDEF_SG, i);
      const [b, sg] = pick(INDEF_VERB, i * 3 + 1);
      const o = pick(OBJ3, i * 7 + 2);
      return mk(`${cap(s)} ${b} ${o} already.`, `${cap(s)} ${sg} ${o} already.`,
        `"${s}" is singular and takes "${sg}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(INDEF_SG, i);
      const pl = pick(INDEF_PLACE, i * 3 + 1);
      const [b, sg] = pick(INDEF_VERB, i * 7 + 2);
      const t = pick(TAILS_SIMPLE, i);
      return mk(`${cap(s)} ${pl} ${b} ${t}.`, `${cap(s)} ${pl} ${sg} ${t}.`,
        `"${s}" stays singular even with "${pl}", so use "${sg}".`);
    });
  }
  return pool40((i) => {
    const s = pick(INDEF_SG, i);
    const [b, sg] = pick(INDEF_VERB, i * 3 + 1);
    const o = pick(OBJ3, i * 7 + 2);
    const t = pick(TAILS_COMPLEX, i);
    return mk(`${cap(t)}, ${s} in the group ${b} ${o}.`, `${cap(t)}, ${s} in the group ${sg} ${o}.`,
      `"${s}" is still singular, so the verb is "${sg}".`);
  });
}

// ---- 2.9 Quantified subjects --------------------------------------------
const QUANT = ['Each', 'Every one', 'Either', 'Neither', 'One', 'Each one'];
const PL_GROUP = ['the boys', 'the girls', 'the students', 'the teachers', 'the workers',
  'the children', 'the players', 'the drivers', 'the doctors', 'the farmers', 'my friends', 'the members'];

function quantified(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const q = pick(QUANT, i);
      const g = pick(PL_GROUP, i * 5 + 1);
      const t = pick(TAILS_SIMPLE, i * 7 + 2);
      return mk(`${q} of ${g} are ${t}.`, `${q} of ${g} is ${t}.`,
        `"${q} of ${g}" is singular and takes "is".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const q = pick(QUANT, i);
      const g = pick(PL_GROUP, i * 5 + 1);
      const t = pick(TAILS_SIMPLE, i * 3 + 2);
      return mk(`${q} of ${g} were ${t}.`, `${q} of ${g} was ${t}.`,
        `"${q} of ${g}" is singular, so the past verb is "was".`);
    });
  }
  return pool40((i) => {
    const q = pick(QUANT, i);
    const g = pick(PL_GROUP, i * 5 + 1);
    const o = pick(OBJ3, i * 7 + 3);
    const t = pick(TAILS_COMPLEX, i * 3 + 2);
    return mk(`${cap(t)}, ${q} of ${g} are responsible for ${o}.`, `${cap(t)}, ${q} of ${g} is responsible for ${o}.`,
      `The quantifier "${q}" is singular, so the verb is "is".`);
  });
}

// ---- 2.10 Determiner-noun number ----------------------------------------
function determinerNumber(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [sg, pl] = pick(NOUNS, Math.floor(i / 2));
      const t = pick(TAILS_SIMPLE, i);
      if (i % 2 === 0) {
        return mk(`Please bring these ${sg} ${t}.`, `Please bring this ${sg} ${t}.`,
          `"${sg}" is singular, so use "this".`);
      }
      return mk(`Please bring this ${pl} ${t}.`, `Please bring these ${pl} ${t}.`,
        `"${pl}" is plural, so use "these".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [sg, pl] = pick(NOUNS, Math.floor(i / 2));
      const t = pick(TAILS_SIMPLE, i);
      if (i % 2 === 0) {
        return mk(`Look at those ${sg} ${t}.`, `Look at that ${sg} ${t}.`,
          `"${sg}" is singular, so use "that".`);
      }
      return mk(`Look at that ${pl} ${t}.`, `Look at those ${pl} ${t}.`,
        `"${pl}" is plural, so use "those".`);
    });
  }
  return pool40((i) => {
    const [sg, pl] = pick(NOUNS, Math.floor(i / 2));
    const adj = pick(ADJ, i * 3 + 1);
    if (i % 2 === 0) {
      return mk(`These ${adj} ${sg} must be moved today.`, `This ${adj} ${sg} must be moved today.`,
        `The singular noun "${sg}" takes the singular determiner "this".`);
    }
    return mk(`This ${adj} ${pl} must be moved today.`, `These ${adj} ${pl} must be moved today.`,
      `The plural noun "${pl}" takes the plural determiner "these".`);
  });
}

// ---- 2.11 Quantifier-noun -----------------------------------------------
const NONCOUNT = ['money', 'water', 'time', 'information', 'advice', 'furniture', 'homework',
  'bread', 'milk', 'rice', 'sugar', 'salt', 'music', 'traffic', 'baggage', 'equipment',
  'knowledge', 'progress', 'weather', 'help'];

function quantifierNoun(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const p = pick(BARE_PL, Math.floor(i / 2));
      const t = pick(TAILS_SIMPLE, i);
      if (i % 2 === 0) {
        return mk(`There are less ${p} ${t}.`, `There are fewer ${p} ${t}.`,
          `"${p}" is countable, so use "fewer".`);
      }
      return mk(`There are much ${p} ${t}.`, `There are many ${p} ${t}.`,
        `"${p}" is countable, so use "many".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const n = pick(NONCOUNT, Math.floor(i / 2));
      const t = pick(TAILS_SIMPLE, i * 3 + 1);
      if (i % 2 === 0) {
        return mk(`We have fewer ${n} ${t}.`, `We have less ${n} ${t}.`,
          `"${n}" is uncountable, so use "less".`);
      }
      return mk(`We have many ${n} ${t}.`, `We have much ${n} ${t}.`,
        `"${n}" is uncountable, so use "much".`);
    });
  }
  return pool40((i) => {
    const t = pick(TAILS_COMPLEX, Math.floor(i / 2));
    if (i % 2 === 0) {
      const p = pick(BARE_PL, i);
      return mk(`A large amount of ${p} were sold ${t}.`, `A large number of ${p} were sold ${t}.`,
        `Countable "${p}" takes "a large number of".`);
    }
    const n = pick(NONCOUNT, i);
    return mk(`A large number of ${n} was wasted ${t}.`, `A large amount of ${n} was wasted ${t}.`,
      `Uncountable "${n}" takes "a large amount of".`);
  });
}

// ---- 2.12 Pronoun-antecedent --------------------------------------------
const ANTECEDENT_PL = ['The girls', 'The boys', 'The students', 'The teachers', 'My friends',
  'The children', 'The workers', 'The players', 'The doctors', 'The drivers', 'The women', 'The men'];
const POSS_THINGS = ['bag', 'coat', 'book', 'car', 'house', 'ticket', 'umbrella', 'phone', 'laptop', 'jacket'];
const BARE_OBJ = ['message', 'letter', 'report', 'picture', 'story', 'project', 'plan', 'essay',
  'novel', 'parcel', 'puzzle', 'basket', 'test', 'list', 'cake'];
const SG_ANT = [
  ['The boy', 'his'], ['The girl', 'her'], ['The man', 'his'], ['The woman', 'her'],
  ['My father', 'his'], ['My mother', 'her'], ['The actor', 'his'], ['The actress', 'her'],
  ['The king', 'his'], ['The queen', 'her'], ['The brother', 'his'], ['The sister', 'her'],
  ['Tom', 'his'], ['Anna', 'her'], ['The waiter', 'his'], ['The waitress', 'her'],
  ['The gentleman', 'his'], ['The lady', 'her'], ['The uncle', 'his'], ['The aunt', 'her'],
];

function pronouns(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const a = pick(ANTECEDENT_PL, i);
      const obj = pick(POSS_THINGS, i * 3 + 1);
      const wrong = pick(['her', 'his', 'its'], i * 7 + 2);
      return mk(`${a} lost ${wrong} ${obj} yesterday.`, `${a} lost their ${obj} yesterday.`,
        `The plural antecedent "${a}" takes the plural possessive "their".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [a, poss] = pick(SG_ANT, i);
      const obj = pick(POSS_THINGS, i * 3 + 1);
      const place = pick(PLACE7, i);
      return mk(`${a} forgot their ${obj} ${place}.`, `${a} forgot ${poss} ${obj} ${place}.`,
        `The singular antecedent "${a}" agrees with "${poss}".`);
    });
  }
  return pool40((i) => {
    const [a, poss] = pick(SG_ANT, i);
    const adv = pick(ADV, i);
    const obj = pick(BARE_OBJ, i * 3 + 1);
    const t = pick(TAILS_COMPLEX, i * 7 + 2);
    return mk(`${cap(t)}, ${a} ${adv} blamed their ${obj}.`, `${cap(t)}, ${a} ${adv} blamed ${poss} ${obj}.`,
      `The antecedent "${a}" controls the pronoun, which must be "${poss}".`);
  });
}

// ---- 2.13 Correlatives ---------------------------------------------------
function correlatives(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const a = pick(COORD_SG, i);
      const b = pick(COORD_PL, i * 3 + 1);
      return mk(`Either ${a} or ${b} is coming tonight.`, `Either ${a} or ${b} are coming tonight.`,
        `With "either...or" the verb agrees with the nearer plural "${b}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const a = pick(COORD_SG, i);
      const b = pick(COORD_PL, i * 3 + 1);
      const t = pick(TAILS_SIMPLE, i * 7 + 2);
      return mk(`Neither ${a} nor ${b} was ${t}.`, `Neither ${a} nor ${b} were ${t}.`,
        `The nearer subject "${b}" is plural, so use "were".`);
    });
  }
  return pool40((i) => {
    const a = pick(COORD_PL, i);
    const b = pick(COORD_SG, i * 3 + 1);
    const t = pick(TAILS_COMPLEX, i);
    return mk(`Not only ${a} but also ${b} are expected ${t}.`, `Not only ${a} but also ${b} is expected ${t}.`,
      `The verb agrees with the nearer singular subject "${b}", so use "is".`);
  });
}

// ---- 2.14 Reflexive-antecedent ------------------------------------------
const REFL = [
  ['She', 'herself', 'himself'], ['He', 'himself', 'herself'], ['The girl', 'herself', 'himself'],
  ['The boy', 'himself', 'herself'], ['The woman', 'herself', 'himself'], ['The man', 'himself', 'herself'],
  ['Anna', 'herself', 'himself'], ['Tom', 'himself', 'herself'], ['My mother', 'herself', 'himself'],
  ['My father', 'himself', 'herself'], ['The actress', 'herself', 'himself'], ['The actor', 'himself', 'herself'],
  ['The queen', 'herself', 'himself'], ['The king', 'himself', 'herself'], ['The sister', 'herself', 'himself'],
  ['The brother', 'himself', 'herself'], ['Lucy', 'herself', 'himself'], ['Ben', 'himself', 'herself'],
  ['The waitress', 'herself', 'himself'], ['The waiter', 'himself', 'herself'],
];
const REFL_PL = [
  ['The boys', 'themselves', 'himself'], ['The girls', 'themselves', 'herself'],
  ['The students', 'themselves', 'themself'], ['The teachers', 'themselves', 'himself'],
  ['My friends', 'themselves', 'themself'], ['The children', 'themselves', 'himself'],
  ['The workers', 'themselves', 'herself'], ['The players', 'themselves', 'themself'],
  ['The doctors', 'themselves', 'himself'], ['The women', 'themselves', 'herself'],
  ['The men', 'themselves', 'himself'], ['The drivers', 'themselves', 'themself'],
];

function reflexives(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [s, refl, wrong] = pick(REFL, i);
      const [, sg] = pick(VERBS, i * 3 + 1);
      return mk(`${s} ${sg} ${wrong} in the mirror.`, `${s} ${sg} ${refl} in the mirror.`,
        `The singular subject "${s}" takes the reflexive "${refl}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [s, refl, wrong] = pick(REFL_PL, i);
      const [b] = pick(VERBS, i * 5 + 1);
      const t = pick(TAILS_SIMPLE, i * 3 + 2);
      return mk(`${s} blamed ${wrong} ${t}.`, `${s} blamed ${refl} ${t}.`,
        `The plural antecedent "${s}" takes the reflexive "${refl}".`);
    });
  }
  return pool40((i) => {
    const [s, refl, wrong] = pick(REFL, i);
    const adv = pick(ADV, i);
    const obj = pick(OBJ3, i * 3 + 1);
    const t = pick(TAILS_COMPLEX, i);
    return mk(`${cap(t)}, ${s} ${adv} prepared ${obj} for ${wrong} alone.`,
      `${cap(t)}, ${s} ${adv} prepared ${obj} for ${refl} alone.`,
      `The reflexive must match the subject "${s}", so use "${refl}".`);
  });
}

export default {
  '2.1': svSimple,
  '2.2': svIntervening,
  '2.3': coordinated,
  '2.4': existential,
  '2.5': collectives,
  '2.6': inversion,
  '2.7': relatives,
  '2.8': indefinites,
  '2.9': quantified,
  '2.10': determinerNumber,
  '2.11': quantifierNoun,
  '2.12': pronouns,
  '2.13': correlatives,
  '2.14': reflexives,
};
