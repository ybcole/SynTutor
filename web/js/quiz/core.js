// ---------------------------------------------------------------------------
// Shared building blocks for the Matrix Quiz question banks.
//
// Every rule builder has the shape   (difficulty) => item[]
// where difficulty is 'easy' | 'medium' | 'hard' and each item is
//   { bad, good, explanation }
// `bad` is the incorrect sentence the learner repairs, `good` is the expected
// correction, and `explanation` is the fallback text shown when the rule matrix
// cannot detect the error.
//
// `pool40(gen)` de-duplicates and caps at 40, so each rule always offers 40
// sentences per difficulty. Difficulty tiers should get progressively more
// complex: easy = short canonical case, medium = added modifiers/clauses or
// less common words, hard = long/compound/embedded sentences and edge cases.
// ---------------------------------------------------------------------------

export const pick = (arr, i) => arr[((i % arr.length) + arr.length) % arr.length];
export const mk = (bad, good, explanation) => ({ bad, good, explanation });
export const tier = (d, table) => table[d] || table.easy;

export function pool40(gen, n = 40) {
  const out = [];
  const seen = new Set();
  for (let i = 0; out.length < n && i < n * 12; i += 1) {
    const item = gen(i);
    if (!item || !item.bad || !item.good || item.bad === item.good) continue;
    const key = `${item.bad}||${item.good}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(item);
  }
  return out;
}

// Cartesian product of `dims` passed to make(...), de-duplicated, capped at n.
export function cartesian(dims, make, n = 40) {
  const out = [];
  const seen = new Set();
  const walk = (idx, chosen) => {
    if (out.length >= n) return;
    if (idx === dims.length) {
      const item = make(...chosen);
      if (item && item.bad && item.good && item.bad !== item.good) {
        const key = `${item.bad}||${item.good}`;
        if (!seen.has(key)) { seen.add(key); out.push(item); }
      }
      return;
    }
    for (const value of dims[idx]) {
      walk(idx + 1, [...chosen, value]);
      if (out.length >= n) return;
    }
  };
  walk(0, []);
  return out;
}

export const cap = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s);
export const withPeriod = (s) => (/[.!?]$/.test(s) ? s : `${s}.`);
export const withoutPeriod = (s) => s.replace(/[.!?]+$/, '');

// ---- Nouns ---------------------------------------------------------------
// [singular, plural]
export const NOUNS = [
  ['boy', 'boys'], ['girl', 'girls'], ['man', 'men'], ['woman', 'women'],
  ['child', 'children'], ['baby', 'babies'], ['teacher', 'teachers'],
  ['student', 'students'], ['doctor', 'doctors'], ['driver', 'drivers'],
  ['worker', 'workers'], ['farmer', 'farmers'], ['nurse', 'nurses'],
  ['player', 'players'], ['friend', 'friends'], ['brother', 'brothers'],
  ['sister', 'sisters'], ['mother', 'mothers'], ['father', 'fathers'],
  ['cat', 'cats'], ['dog', 'dogs'], ['bird', 'birds'], ['horse', 'horses'],
  ['tree', 'trees'], ['house', 'houses'], ['car', 'cars'], ['book', 'books'],
  ['phone', 'phones'], ['table', 'tables'], ['chair', 'chairs'],
  ['window', 'windows'], ['door', 'doors'], ['garden', 'gardens'],
  ['river', 'rivers'], ['mountain', 'mountains'], ['village', 'villages'],
  ['city', 'cities'], ['office', 'offices'], ['box', 'boxes'],
  ['watch', 'watches'], ['leaf', 'leaves'], ['knife', 'knives'],
  ['potato', 'potatoes'], ['hero', 'heroes'], ['photo', 'photos'],
  ['piano', 'pianos'], ['tooth', 'teeth'], ['foot', 'feet'], ['mouse', 'mice'],
  ['child', 'children'], ['crisis', 'crises'], ['criterion', 'criteria'],
  ['datum', 'data'], ['analysis', 'analyses'],
];

export const SG_SUBJ = NOUNS.map(([s]) => `the ${s}`);
export const PL_SUBJ = NOUNS.map(([, p]) => `the ${p}`);
export const NAMES = [
  'Tom', 'Anna', 'Sam', 'Lucy', 'Ben', 'Mia', 'Jack', 'Zoe', 'Leo', 'Emma',
  'Omar', 'Sara', 'Paul', 'Nina', 'Kai', 'Rita', 'Raj', 'Dana', 'Ivan', 'Lena',
];

// ---- Verbs ---------------------------------------------------------------
// [base, 3sg, past, pastParticiple, -ing]
export const VREG = [
  ['walk', 'walks', 'walked', 'walked', 'walking'], ['talk', 'talks', 'talked', 'talked', 'talking'],
  ['look', 'looks', 'looked', 'looked', 'looking'], ['help', 'helps', 'helped', 'helped', 'helping'],
  ['call', 'calls', 'called', 'called', 'calling'], ['open', 'opens', 'opened', 'opened', 'opening'],
  ['close', 'closes', 'closed', 'closed', 'closing'], ['clean', 'cleans', 'cleaned', 'cleaned', 'cleaning'],
  ['paint', 'paints', 'painted', 'painted', 'painting'], ['jump', 'jumps', 'jumped', 'jumped', 'jumping'],
  ['kick', 'kicks', 'kicked', 'kicked', 'kicking'], ['push', 'pushes', 'pushed', 'pushed', 'pushing'],
  ['pull', 'pulls', 'pulled', 'pulled', 'pulling'], ['cook', 'cooks', 'cooked', 'cooked', 'cooking'],
  ['bake', 'bakes', 'baked', 'baked', 'baking'], ['dance', 'dances', 'danced', 'danced', 'dancing'],
  ['live', 'lives', 'lived', 'lived', 'living'], ['love', 'loves', 'loved', 'loved', 'loving'],
  ['hope', 'hopes', 'hoped', 'hoped', 'hoping'], ['smile', 'smiles', 'smiled', 'smiled', 'smiling'],
  ['use', 'uses', 'used', 'used', 'using'], ['move', 'moves', 'moved', 'moved', 'moving'],
  ['arrive', 'arrives', 'arrived', 'arrived', 'arriving'], ['decide', 'decides', 'decided', 'decided', 'deciding'],
  ['watch', 'watches', 'watched', 'watched', 'watching'], ['fix', 'fixes', 'fixed', 'fixed', 'fixing'],
  ['study', 'studies', 'studied', 'studied', 'studying'], ['carry', 'carries', 'carried', 'carried', 'carrying'],
  ['stop', 'stops', 'stopped', 'stopped', 'stopping'], ['plan', 'plans', 'planned', 'planned', 'planning'],
];
export const VIRR = [
  ['go', 'goes', 'went', 'gone', 'going'], ['have', 'has', 'had', 'had', 'having'],
  ['do', 'does', 'did', 'done', 'doing'], ['say', 'says', 'said', 'said', 'saying'],
  ['get', 'gets', 'got', 'gotten', 'getting'], ['make', 'makes', 'made', 'made', 'making'],
  ['know', 'knows', 'knew', 'known', 'knowing'], ['think', 'thinks', 'thought', 'thought', 'thinking'],
  ['take', 'takes', 'took', 'taken', 'taking'], ['see', 'sees', 'saw', 'seen', 'seeing'],
  ['come', 'comes', 'came', 'come', 'coming'], ['give', 'gives', 'gave', 'given', 'giving'],
  ['find', 'finds', 'found', 'found', 'finding'], ['tell', 'tells', 'told', 'told', 'telling'],
  ['leave', 'leaves', 'left', 'left', 'leaving'], ['feel', 'feels', 'felt', 'felt', 'feeling'],
  ['bring', 'brings', 'brought', 'brought', 'bringing'], ['begin', 'begins', 'began', 'begun', 'beginning'],
  ['keep', 'keeps', 'kept', 'kept', 'keeping'], ['write', 'writes', 'wrote', 'written', 'writing'],
  ['speak', 'speaks', 'spoke', 'spoken', 'speaking'], ['break', 'breaks', 'broke', 'broken', 'breaking'],
  ['drive', 'drives', 'drove', 'driven', 'driving'], ['buy', 'buys', 'bought', 'bought', 'buying'],
  ['wear', 'wears', 'wore', 'worn', 'wearing'], ['choose', 'chooses', 'chose', 'chosen', 'choosing'],
  ['eat', 'eats', 'ate', 'eaten', 'eating'], ['drink', 'drinks', 'drank', 'drunk', 'drinking'],
  ['sing', 'sings', 'sang', 'sung', 'singing'], ['swim', 'swims', 'swam', 'swum', 'swimming'],
  ['fly', 'flies', 'flew', 'flown', 'flying'], ['throw', 'throws', 'threw', 'thrown', 'throwing'],
  ['catch', 'catches', 'caught', 'caught', 'catching'], ['teach', 'teaches', 'taught', 'taught', 'teaching'],
  ['sell', 'sells', 'sold', 'sold', 'selling'], ['sleep', 'sleeps', 'slept', 'slept', 'sleeping'],
  ['put', 'puts', 'put', 'put', 'putting'], ['run', 'runs', 'ran', 'run', 'running'],
];
export const VERBS = [...VREG, ...VIRR];

// ---- Phrase pools --------------------------------------------------------
export const OBJECTS = [
  'the letter', 'the book', 'the car', 'the door', 'the window', 'the garden',
  'the report', 'the message', 'the homework', 'the dishes', 'the floor',
  'the song', 'the piano', 'the picture', 'the story', 'the project',
  'the email', 'the bill', 'the cake', 'the room', 'the wall', 'the road',
  'the river', 'the mountain', 'the plan', 'the list', 'the test', 'the essay',
  'the novel', 'the bridge', 'the ticket', 'the parcel', 'the mirror',
  'the carpet', 'the fence', 'the clock', 'the kettle', 'the ladder',
  'the camera', 'the basket', 'the puzzle', 'the garden gate', 'the old house',
  'the small village', 'the heavy box',
];

export const TAILS_SIMPLE = [
  'at school', 'every morning', 'before dinner', 'in the park', 'after lunch',
  'on Mondays', 'at noon', 'near the river', 'every weekend', 'after work',
  'in the kitchen', 'on the bus', 'at the station', 'during the lesson',
  'before breakfast', 'in the office', 'on the farm', 'at the clinic',
  'after school', 'in the library',
];

export const TAILS_COMPLEX = [
  'while the baby was sleeping', 'although the weather was terrible',
  'because the train had been delayed', 'before the guests arrived',
  'when the lights suddenly went out', 'even though she had studied hard',
  'after the long meeting finally ended', 'as soon as the rain stopped',
  'unless the plan changes', 'since everyone had already left',
  'in case the power fails again', 'though nobody expected it',
  'once the paperwork is finished', 'whenever the phone rings',
  'while they were waiting outside', 'before the storm reached the coast',
  'after the committee reviewed the proposal', 'because the budget was cut',
  'as the audience grew impatient', 'until the replacement arrives',
];

export const ADJ = [
  'tall', 'short', 'old', 'young', 'fast', 'slow', 'high', 'low', 'small',
  'strong', 'weak', 'cold', 'warm', 'cool', 'smart', 'clean', 'dark', 'deep',
  'big', 'hot', 'thin', 'happy', 'easy', 'busy', 'heavy', 'pretty', 'gentle',
  'simple', 'careful', 'quiet', 'loud', 'beautiful', 'expensive',
  'interesting', 'difficult', 'popular', 'dangerous', 'comfortable', 'bright',
  'narrow',
];

export const ADV = [
  'quickly', 'slowly', 'happily', 'easily', 'busily', 'heavily', 'lazily',
  'angrily', 'gently', 'simply', 'terribly', 'carefully', 'quietly', 'loudly',
  'beautifully', 'sadly', 'badly', 'well', 'correctly', 'politely', 'bravely',
  'clearly', 'suddenly', 'silently', 'perfectly', 'safely', 'usually',
  'probably', 'really', 'fully',
];

export const PREPS = [
  'in', 'on', 'at', 'by', 'with', 'for', 'from', 'about', 'into', 'over',
  'under', 'between', 'through', 'during', 'after', 'before', 'against',
  'toward', 'across', 'without',
];

export const CONNECTORS = [
  'and', 'but', 'or', 'so', 'because', 'although', 'while', 'since', 'unless',
  'whereas', 'however', 'therefore', 'moreover', 'otherwise', 'nevertheless',
];

export const PRON_SG = ['he', 'she', 'it'];
export const PRON_PL = ['they', 'we', 'you'];
