// Section 7 — Adjectives and adverbs. One builder per rule; 40 items per tier.
import {
  pick, mk, pool40, cartesian, cap, ADV, TAILS_SIMPLE, TAILS_COMPLEX, NAMES,
} from './core.js';

const art = (w) => (/^[aeiou]/i.test(w) ? 'an' : 'a');

const twoNames = (i) => {
  const a = pick(NAMES, i * 3 + 1);
  let b = pick(NAMES, i * 5 + 2);
  if (b === a) b = pick(NAMES, i * 5 + 3);
  return [a, b];
};

// ---- 7.1 Adjective vs adverb --------------------------------------------
const AV = [
  ['quick', 'quickly'], ['slow', 'slowly'], ['happy', 'happily'], ['easy', 'easily'],
  ['busy', 'busily'], ['heavy', 'heavily'], ['lazy', 'lazily'], ['angry', 'angrily'],
  ['gentle', 'gently'], ['simple', 'simply'], ['terrible', 'terribly'], ['careful', 'carefully'],
  ['quiet', 'quietly'], ['loud', 'loudly'], ['beautiful', 'beautifully'], ['sad', 'sadly'],
  ['bad', 'badly'], ['perfect', 'perfectly'], ['correct', 'correctly'], ['safe', 'safely'],
  ['brave', 'bravely'], ['polite', 'politely'], ['usual', 'usually'], ['real', 'really'],
  ['silent', 'silently'], ['sudden', 'suddenly'], ['good', 'well'],
];
const IVERB = ['runs', 'walks', 'speaks', 'works', 'sings', 'dances', 'studies', 'writes',
  'reads', 'cooks', 'paints', 'cleans', 'listens', 'waits', 'laughs', 'smiles'];
const TVERB = ['reads', 'writes', 'plays', 'paints', 'cleans', 'cooks', 'finishes', 'opens',
  'closes', 'carries', 'watches', 'drives', 'answers', 'builds', 'draws', 'repairs'];
const MOBJ = ['the letter', 'the report', 'the song', 'the piano', 'the essay', 'the test',
  'the room', 'the fence', 'the dishes', 'the problem', 'the garden', 'the road'];
const PSUBJ = ['She', 'He', 'Tom', 'Anna', 'The boy', 'The girl', 'My friend', 'The teacher',
  'The driver', 'The student'];

function adjectiveAdverb(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [adj, adv] = pick(AV, i * 3 + 1);
      const v = pick(IVERB, i * 7 + 2);
      const s = pick(PSUBJ, i * 5 + 3);
      return mk(`${s} ${v} ${adj}.`, `${s} ${v} ${adv}.`,
        `An action verb is modified by the adverb "${adv}", not the adjective "${adj}".`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [adj, adv] = pick(AV, i * 5 + 1);
      const v = pick(TVERB, i * 3 + 2);
      const o = pick(MOBJ, i * 7 + 3);
      const s = pick(PSUBJ, i * 4 + 1);
      return mk(`${s} ${v} ${o} ${adj}.`, `${s} ${v} ${o} ${adv}.`,
        `The adverb "${adv}" follows the object "${o}"; the adjective "${adj}" cannot modify "${v}".`);
    });
  }
  return pool40((i) => {
    const [adj, adv] = pick(AV, i * 7 + 1);
    const v = pick(TVERB, i * 5 + 2);
    const o = pick(MOBJ, i * 3 + 3);
    const s = pick(PSUBJ, i * 3 + 1);
    const t = pick(TAILS_COMPLEX, i * 5 + 4);
    return mk(`${s} ${v} ${o} ${adj} ${t}.`, `${s} ${v} ${o} ${adv} ${t}.`,
      `Even in this longer sentence the verb needs the adverb "${adv}", not "${adj}".`);
  });
}

// ---- 7.2 Adjective order -------------------------------------------------
const CAT = {
  opinion: ['beautiful', 'lovely', 'nice', 'ugly', 'wonderful', 'horrible', 'charming', 'silly'],
  size: ['big', 'small', 'huge', 'tiny', 'large', 'little', 'enormous'],
  age: ['old', 'new', 'young', 'ancient', 'modern', 'recent'],
  shape: ['round', 'square', 'flat', 'oval', 'narrow'],
  colour: ['red', 'blue', 'green', 'black', 'white', 'brown', 'yellow', 'grey'],
  origin: ['French', 'Italian', 'Chinese', 'Japanese', 'German', 'Spanish', 'Greek'],
  material: ['wooden', 'plastic', 'metal', 'silk', 'cotton', 'leather', 'glass'],
  purpose: ['sleeping', 'running', 'dining', 'gardening', 'swimming'],
};
const ORDER = ['opinion', 'size', 'age', 'shape', 'colour', 'origin', 'material', 'purpose'];
const PAIRS = [];
const TRIPLES = [];
const QUADS = [];
for (let i = 0; i < ORDER.length; i += 1) {
  for (let j = i + 1; j < ORDER.length; j += 1) {
    PAIRS.push([ORDER[i], ORDER[j]]);
    for (let k = j + 1; k < ORDER.length; k += 1) {
      TRIPLES.push([ORDER[i], ORDER[j], ORDER[k]]);
      for (let l = k + 1; l < ORDER.length; l += 1) {
        QUADS.push([ORDER[i], ORDER[j], ORDER[k], ORDER[l]]);
      }
    }
  }
}
const ADJ_NOUNS = ['car', 'house', 'dog', 'table', 'garden', 'boat', 'painting', 'jacket',
  'chair', 'bridge', 'clock', 'vase', 'lamp', 'bicycle', 'window', 'cup'];

function adjectiveOrder(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [c1, c2] = pick(PAIRS, i);
      const a = pick(CAT[c1], i * 3 + 1);
      const b = pick(CAT[c2], i * 5 + 2);
      const n = pick(ADJ_NOUNS, i * 7 + 3);
      return mk(cap(`${art(b)} ${b} ${a} ${n} stood in the corner.`),
        cap(`${art(a)} ${a} ${b} ${n} stood in the corner.`),
        `${c1} adjectives (${a}) come before ${c2} adjectives (${b}).`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const [c1, c2, c3] = pick(TRIPLES, i);
      const a = pick(CAT[c1], i * 3 + 1);
      const b = pick(CAT[c2], i * 5 + 2);
      const c = pick(CAT[c3], i * 7 + 3);
      const n = pick(ADJ_NOUNS, i * 3 + 4);
      return mk(cap(`${art(c)} ${c} ${a} ${b} ${n} caught my eye.`),
        cap(`${art(a)} ${a} ${b} ${c} ${n} caught my eye.`),
        `Adjective order is ${c1} \u2192 ${c2} \u2192 ${c3}: "${a} ${b} ${c} ${n}".`);
    });
  }
  return pool40((i) => {
    const [c1, c2, c3, c4] = pick(QUADS, i);
    const a = pick(CAT[c1], i * 3 + 1);
    const b = pick(CAT[c2], i * 5 + 2);
    const c = pick(CAT[c3], i * 7 + 3);
    const e = pick(CAT[c4], i * 3 + 4);
    const n = pick(ADJ_NOUNS, i * 5 + 5);
    const t = pick(TAILS_COMPLEX, i * 7 + 6);
    return mk(`I noticed ${art(e)} ${e} ${c} ${a} ${b} ${n} ${t}.`,
      `I noticed ${art(a)} ${a} ${b} ${c} ${e} ${n} ${t}.`,
      `The correct order is ${c1} \u2192 ${c2} \u2192 ${c3} \u2192 ${c4}: "${a} ${b} ${c} ${e} ${n}".`);
  });
}

// ---- 7.3 Adverb placement ------------------------------------------------
const LIKE_VERBS = ['like', 'love', 'enjoy', 'want', 'need', 'prefer'];
const LIKE_OBJ = ['it', 'them', 'the film', 'the book', 'the song', 'the idea', 'the plan',
  'the gift', 'the news', 'the show'];
const PSUBJ2 = ['I', 'You', 'We', 'They', 'My friends', 'The students', 'The children',
  'Tom and Anna', 'My parents', 'The teachers'];
const PVOICE = ['read', 'wrote', 'played', 'painted', 'cleaned', 'cooked', 'finished',
  'opened', 'closed', 'carried', 'watched', 'drove'];
const MOBJ2 = ['the letter', 'the report', 'the song', 'the piano', 'the essay', 'the room',
  'the fence', 'the dishes', 'the problem', 'the garden', 'the road', 'the cake'];

function adverbPlacement(d) {
  if (d === 'easy') {
    return cartesian([PSUBJ2, LIKE_OBJ, LIKE_VERBS, ['very much', 'a lot']],
      (s, o, v, dp) => mk(`${s} ${v} ${dp} ${o}.`, `${s} ${v} ${o} ${dp}.`,
        `The adverb phrase "${dp}" comes after the object "${o}".`));
  }
  if (d === 'medium') {
    return pool40((i) => {
      const s = pick(PSUBJ2, i);
      const v = pick(PVOICE, i * 5 + 1);
      const o = pick(MOBJ2, i * 3 + 2);
      const adv = pick(ADV, i * 7 + 3);
      return mk(`${s} ${v} ${adv} ${o}.`, `${s} ${v} ${o} ${adv}.`,
        `A manner adverb goes after the object: "${o} ${adv}".`);
    });
  }
  return pool40((i) => {
    const s = pick(PSUBJ2, i);
    const v = pick(PVOICE, i * 7 + 1);
    const o = pick(MOBJ2, i * 5 + 2);
    const adv = pick(ADV, i * 3 + 3);
    const t = pick(TAILS_COMPLEX, i * 5 + 4);
    return mk(`${s} ${v} ${adv} ${o} ${t}.`, `${s} ${v} ${o} ${adv} ${t}.`,
      `The adverb "${adv}" still follows the object "${o}" in a longer sentence.`);
  });
}

// ---- 7.4 Participial adjectives ------------------------------------------
const PA = [
  ['bored', 'boring'], ['interested', 'interesting'], ['excited', 'exciting'], ['tired', 'tiring'],
  ['surprised', 'surprising'], ['confused', 'confusing'], ['frightened', 'frightening'],
  ['amazed', 'amazing'], ['annoyed', 'annoying'], ['disappointed', 'disappointing'],
  ['embarrassed', 'embarrassing'], ['relaxed', 'relaxing'], ['satisfied', 'satisfying'],
  ['worried', 'worrying'], ['shocked', 'shocking'], ['pleased', 'pleasing'],
  ['fascinated', 'fascinating'], ['inspired', 'inspiring'], ['motivated', 'motivating'],
  ['depressed', 'depressing'],
];
const PEOPLE = [['I', 'am'], ['You', 'are'], ['He', 'is'], ['She', 'is'], ['We', 'are'],
  ['They', 'are'], ['Tom', 'is'], ['Anna', 'is'], ['The students', 'are'],
  ['The children', 'are'], ['My parents', 'are'], ['The audience', 'is']];
const THINGS = [['the film', 'is'], ['the book', 'is'], ['the lesson', 'is'], ['the news', 'is'],
  ['the story', 'is'], ['the game', 'is'], ['the result', 'is'], ['the journey', 'is'],
  ['the lecture', 'is'], ['the concert', 'is'], ['the party', 'is'], ['the meeting', 'is'],
  ['the weather', 'is'], ['the ending', 'is'], ['the project', 'is'], ['the match', 'is']];
const WHO_CLAUSE = ['worked all day', 'studied for hours', 'waited in the rain',
  'travelled for two days', 'listened to the whole lecture', 'watched the long film'];
const THAT_CLAUSE = ['everyone read', 'nobody liked', 'we watched last night',
  'the critics praised', 'the children loved'];

function participial(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [ed, ing] = pick(PA, i * 3 + 1);
      const [s, be] = pick(PEOPLE, i * 5 + 2);
      return mk(cap(`${s} ${be} ${ing}.`), cap(`${s} ${be} ${ed}.`),
        `A person who feels the effect uses the -ed form "${ed}", not "${ing}".`);
    });
  }
  if (d === 'medium') {
    return cartesian([THINGS, PA], ([t, be], [ed, ing]) => mk(cap(`${t} ${be} ${ed}.`),
      cap(`${t} ${be} ${ing}.`),
      `A thing that causes the feeling uses the -ing form "${ing}", not "${ed}".`));
  }
  return pool40((i) => {
    const [ed, ing] = pick(PA, i * 7 + 1);
    if (i % 2 === 0) {
      const [s, be] = pick(PEOPLE, i * 3 + 2);
      const wc = pick(WHO_CLAUSE, i * 5 + 3);
      return mk(cap(`${s} who ${wc} ${be} ${ing}.`), cap(`${s} who ${wc} ${be} ${ed}.`),
        `The people described are affected, so use the -ed form "${ed}".`);
    }
    const [t, be] = pick(THINGS, i * 3 + 4);
    const tc = pick(THAT_CLAUSE, i * 5 + 5);
    return mk(cap(`${t} that ${tc} ${be} ${ed}.`), cap(`${t} that ${tc} ${be} ${ing}.`),
      `The thing described causes the feeling, so use the -ing form "${ing}".`);
  });
}

// ---- 7.5 Intensifiers and degree -----------------------------------------
const THING_ADJ = [
  ['The box', 'heavy'], ['The room', 'big'], ['The bag', 'strong'], ['The coat', 'warm'],
  ['The table', 'wide'], ['The car', 'fast'], ['The house', 'tall'], ['The dog', 'gentle'],
  ['The bridge', 'narrow'], ['The river', 'deep'], ['The road', 'long'], ['The bottle', 'full'],
  ['The soup', 'hot'], ['The blanket', 'soft'], ['The rope', 'long'], ['The wall', 'high'],
];
const GOAL = ['to carry', 'to sleep in', 'to wear', 'to hold everything', 'to cross',
  'for two people', 'to reach the ceiling', 'to fill the tank', 'to survive the winter'];
const MTOO_ADJ = ['difficult', 'complicated', 'demanding', 'detailed', 'tiring', 'risky',
  'dangerous', 'noisy', 'crowded', 'heavy', 'dirty', 'confusing'];
const TSUBJ = ['The task', 'The exam', 'The road', 'The machine', 'The room', 'The job',
  'The journey', 'The question', 'The test', 'The project', 'The plan', 'The schedule'];
const FORWHO = ['for us', 'for beginners', 'for the team', 'for a first attempt',
  'for young children', 'for most people'];
const ENOUGH_NOUN = ['money', 'time', 'food', 'water', 'space', 'evidence', 'information',
  'help', 'patience', 'experience', 'courage', 'strength', 'fuel', 'paperwork', 'support',
  'preparation'];

function intensifiers(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [s, a] = pick(THING_ADJ, i * 3 + 1);
      const g = pick(GOAL, i * 5 + 2);
      return mk(`${s} is enough ${a} ${g}.`, `${s} is ${a} enough ${g}.`,
        `"Enough" goes after the adjective: "${a} enough".`);
    });
  }
  if (d === 'medium') {
    return cartesian([TSUBJ, MTOO_ADJ, FORWHO], (s, a, w) => mk(`${s} was too much ${a} ${w}.`,
      `${s} was much too ${a} ${w}.`,
      `Before an adjective use "much too", not "too much": "much too ${a}".`));
  }
  const enoughHalf = cartesian([['We', 'They', 'The team', 'The students', 'The workers',
    'The family', 'The company', 'The committee'], TAILS_COMPLEX, ENOUGH_NOUN,
  ['had', 'needed', 'found', 'saved', 'gathered', 'collected', 'produced', 'offered', 'required']],
  (s, t, n, v) => mk(`${s} ${v} ${n} enough to finish the project ${t}.`,
    `${s} ${v} enough ${n} to finish the project ${t}.`,
    `"Enough" goes before the noun: "enough ${n}".`));
  const tooMuchHalf = cartesian([TSUBJ, TAILS_COMPLEX, MTOO_ADJ], (s, t, a) => mk(
    `${s} was too much ${a} for everyone ${t}.`, `${s} was much too ${a} for everyone ${t}.`,
    `Use "much too" before the adjective "${a}".`,
  ));
  return enoughHalf.slice(0, 20).concat(tooMuchHalf.slice(0, 20));
}

// ---- 7.6 Comparative structures ------------------------------------------
const CMP = [
  ['tall', 'taller'], ['short', 'shorter'], ['old', 'older'], ['young', 'younger'],
  ['fast', 'faster'], ['slow', 'slower'], ['high', 'higher'], ['low', 'lower'],
  ['small', 'smaller'], ['strong', 'stronger'], ['weak', 'weaker'], ['cold', 'colder'],
  ['warm', 'warmer'], ['smart', 'smarter'], ['clean', 'cleaner'], ['dark', 'darker'],
  ['big', 'bigger'], ['hot', 'hotter'], ['thin', 'thinner'], ['happy', 'happier'],
  ['easy', 'easier'], ['busy', 'busier'], ['heavy', 'heavier'], ['safe', 'safer'],
  ['nice', 'nicer'], ['brave', 'braver'], ['polite', 'politer'], ['simple', 'simpler'],
];
const AS_ADJ = [...CMP.map((x) => x[0]), 'beautiful', 'expensive', 'interesting', 'difficult',
  'comfortable', 'popular', 'important', 'dangerous'];

function comparatives(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const [adj, comp] = pick(CMP, i * 3 + 1);
      const [a, b] = twoNames(i);
      return mk(`${a} is more ${comp} than ${b}.`, `${a} is ${comp} than ${b}.`,
        `"${comp}" is already comparative, so "more" is not added.`);
    });
  }
  if (d === 'medium') {
    return pool40((i) => {
      const adj = pick(AS_ADJ, i * 5 + 1);
      const [a, b] = twoNames(i * 7 + 2);
      return mk(`${a} is as ${adj} than ${b}.`, `${a} is as ${adj} as ${b}.`,
        `The "as ... as" structure uses "as", not "than".`);
    });
  }
  return pool40((i) => {
    const t = pick(TAILS_COMPLEX, i * 5 + 1);
    const [a, b] = twoNames(i * 3 + 2);
    if (i % 2 === 0) {
      const [, comp] = pick(CMP, i * 7 + 3);
      return mk(`${a} was far more ${comp} than ${b} ${t}.`, `${a} was far ${comp} than ${b} ${t}.`,
        `"${comp}" is already a comparative, so "far ${comp}" is enough.`);
    }
    const adj = pick(AS_ADJ, i * 3 + 4);
    return mk(`${a} was not as ${adj} than ${b} ${t}.`, `${a} was not as ${adj} as ${b} ${t}.`,
      `After "not as" use "as": "not as ${adj} as".`);
  });
}

// ---- 7.7 Modifier position ----------------------------------------------
const MODADJ = ['red', 'blue', 'green', 'old', 'new', 'small', 'big', 'young', 'tall', 'heavy',
  'bright', 'clean', 'dark', 'warm', 'cold', 'pretty'];
const MODNOUN = ['car', 'house', 'dog', 'table', 'garden', 'boat', 'chair', 'bridge', 'clock',
  'vase', 'lamp', 'window', 'door', 'book'];
const MODVERB = ['saw', 'bought', 'painted', 'cleaned', 'found', 'liked', 'wanted', 'repaired'];
const MODSUBJ = ['I', 'We', 'They', 'She', 'He', 'Tom', 'Anna', 'The neighbour'];
const RELCLAUSE = ['that was parked outside', 'that stood by the gate', 'that everyone admired',
  'which had just arrived', 'that belonged to my uncle', 'which nobody wanted',
  'that needed repair', 'which stood in the corner'];

function modifierPosition(d) {
  if (d === 'easy') {
    return pool40((i) => {
      const adj = pick(MODADJ, i);
      const n = pick(MODNOUN, i * 3 + 1);
      const v = pick(MODVERB, i * 5 + 2);
      const s = pick(MODSUBJ, i * 7 + 3);
      return mk(`${s} ${v} the ${n} ${adj}.`, `${s} ${v} the ${adj} ${n}.`,
        `An attributive adjective goes before the noun: "the ${adj} ${n}".`);
    });
  }
  if (d === 'medium') {
    return cartesian([MODSUBJ, MODNOUN, MODADJ, MODADJ, MODVERB],
      (s, n, adj1, adj2, v) => {
        if (adj1 === adj2) return null;
        return mk(`${s} ${v} the ${n} ${adj1} and ${adj2}.`,
          `${s} ${v} the ${adj1} and ${adj2} ${n}.`,
          `Both adjectives must precede the noun: "the ${adj1} and ${adj2} ${n}".`);
      });
  }
  return pool40((i) => {
    const adj = pick(MODADJ, i * 3 + 1);
    const n = pick(MODNOUN, i * 5 + 2);
    const rel = pick(RELCLAUSE, i * 7 + 3);
    const v = pick(MODVERB, i * 3 + 4);
    const s = pick(MODSUBJ, i * 5 + 5);
    return mk(`${s} ${v} the ${n} ${adj} ${rel}.`, `${s} ${v} the ${adj} ${n} ${rel}.`,
      `The adjective belongs directly before the noun, even with a relative clause: "the ${adj} ${n}".`);
  });
}

export default {
  '7.1': adjectiveAdverb,
  '7.2': adjectiveOrder,
  '7.3': adverbPlacement,
  '7.4': participial,
  '7.5': intensifiers,
  '7.6': comparatives,
  '7.7': modifierPosition,
};
