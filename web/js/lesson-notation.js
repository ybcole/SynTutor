import inventory from './builder-inventory.js';

const categories = {
  'PHRASE-a': 'Outer phrase in the Chapter 1 examples.',
  'PHRASE-b': 'A smaller phrase within the outer phrase in the Chapter 1 examples.',
  'PHRASE-c': 'Another phrase in the Chapter 1 ambiguity example.',
  'PHRASE-d': 'An inner phrase in the Chapter 1 ambiguity example.',
  Sentence: 'Top node in a Chapter 1 sentence diagram.',
  Phrase: 'Placeholder for a phrase before its category is specified.',
  PHRASE: 'Placeholder for a phrase before its category is specified.',
  S: 'Sentence or clause node.',
  NP: 'Noun phrase.',
  VP: 'Verb phrase.',
  VP1: 'The basic verb phrase, including the verb and any complements it takes.',
  VP2: 'The next verb phrase level, formed when an adjunct joins the basic verb phrase.',
  N: 'Noun.',
  A: 'Adjective.',
  AP: 'Adjective phrase.',
  DEG: 'Degree word, such as “very”.',
  Adv: 'Adverb.',
  AdvP: 'Adverb phrase.',
  P: 'Preposition.',
  PP: 'Prepositional phrase.',
  name: 'Name within an NP.',
  pronoun: 'Pronoun within an NP.',
  V: 'Lexical verb.',
  Prt: 'Particle in a phrasal verb.',
  E: 'Ellipted element understood from the context.',
  MOD: 'Modal auxiliary.',
  PERF: 'Perfect auxiliary.',
  PROG: 'Progressive auxiliary.',
  PASS: 'Passive auxiliary.',
  TENSE: 'Tense-carrying auxiliary “do”.',
  'S-bar': 'Clause layer above S, displayed as S′.',
  C: 'Complementiser or auxiliary position, depending on the chapter.',
  DET: 'Determiner position.',
  ART: 'Article.',
  DEM: 'Demonstrative.',
  Q: 'Quantifier in DET.',
  POSS: 'Possessive in DET.',
  'PRE-DET': 'Pre-determiner, such as “all” or “both”.',
  NOM: 'Nominal layer between NP and N.',
  PartP: 'Participle phrase.',
  'V-part': 'Participial verb.',
  QA: 'Quantifying adjective.',
  'S-dbar': 'Wh-clause layer above S′, displayed as S″.',
  C1: 'Lower position in the Chapter 9 wh-tree.',
  C2: 'Higher position for the fronted wh-expression in the Chapter 9 tree.',
  AUX: 'Stored auxiliary category. In the Chapter 10 “to” example, the tree displays only [-tense].',
  'V(I)': 'Type I verb with a clause complement and an overt subject in that clause.',
  'V(II)': 'Type II verb with an object NP and a clause complement with a covert subject.',
};

const features = {
  trans: 'Transitive.',
  intrans: 'Intransitive.',
  ditrans: 'Ditransitive.',
  intens: 'Intensive.',
  complex: 'Complex transitive.',
  prep: 'Prepositional verb pattern.',
  phrasal: 'Phrasal verb.',
  pres: 'Present tense.',
  past: 'Past tense.',
  '-tense': 'Non-finite, with no tense of its own.',
};

const symbols = {
  Node: 'A point in the tree that can branch or carry a label.',
  Branch: 'A line connecting a node to one of its immediate parts.',
  '△': 'A constituent whose internal structure is left unanalyzed.',
  '•': 'A gap with no overt word in that position.',
  Index: 'A number used to mark a structural relationship between positions.',
};

export function vpLevel(node) {
  if (node.label !== 'VP') return undefined;
  return [node.ref, ...(node.source_refs || [])].find(ref => typeof ref === 'string' && /^VP[1-9][0-9]*$/.test(ref));
}

function displayCategory(label) {
  if (/^VP[1-9][0-9]*$/.test(label)) return label.replace(/[0-9]/g, digit => '₀₁₂₃₄₅₆₇₈₉'[Number(digit)]);
  return ({ 'S-bar': 'S′', 'S-dbar': 'S″' })[label] || label;
}

function categoryDescription(label) {
  return categories[label] ?? (/^VP[1-9][0-9]*$/.test(label)
    ? 'A higher verb phrase level, formed when another adjunct joins the phrase below it.'
    : undefined);
}

export function displayVpLevel(node) {
  const level = vpLevel(node);
  return level && displayCategory(level);
}

export function lessonNotation(lesson, page, el, pageLabels, pageFeatures = []) {
  const guide = el('details', undefined, 'lesson-notation');
  guide.append(el('summary', 'Tree notation'));
  const labels = new Set();
  const marks = new Set(['Node', 'Branch']);
  const usedFeatures = new Set(pageFeatures);
  function collect(node) {
    if (node.label && node.label !== 'AUX') labels.add(vpLevel(node) || node.label);
    for (const feature of node.features || []) usedFeatures.add(feature);
    if (node.triangle) marks.add('△');
    if (node.gap) marks.add('•');
    if (node.index !== undefined) marks.add('Index');
    for (const child of node.children || []) collect(child);
  }
  if (pageLabels) {
    for (const label of pageLabels) {
      if (Object.hasOwn(symbols, label)) marks.add(label);
      else labels.add(label);
    }
  } else if (lesson.lesson_id === 'br-01') {
    const ambiguityLabels = lesson.revised_assessment
      ? ['PHRASE-a', 'PHRASE-b', 'PHRASE-c']
      : ['S', 'PHRASE-a', 'PHRASE-b', 'PHRASE-c', 'PHRASE-d'];
    for (const label of page === 3 ? ambiguityLabels : ['PHRASE-a', 'PHRASE-b']) {
      labels.add(label);
    }
  } else {
    collect(lesson.worked_example.tree.root);
  }
  function addGroup(parent, title, keys, describe, display) {
    if (!keys.length) return;
    const list = el('dl');
    for (const key of keys) list.append(el('dt', display(key)), el('dd', describe(key)));
    parent.append(el('h4', title), list);
  }
  function addEntries(parent, categoryKeys, featureKeys, symbolKeys) {
    addGroup(parent, 'Categories and labels', categoryKeys, categoryDescription, displayCategory);
    addGroup(parent, 'Features', featureKeys, key => features[key], key => `[${key}]`);
    addGroup(parent, 'Diagram symbols', symbolKeys, key => symbols[key], key => key);
  }
  addEntries(guide, [...labels], [...usedFeatures], [...marks]);
  const all = el('details');
  all.append(el('summary', 'View all notation'));
  addEntries(all, ['PHRASE-a', 'PHRASE-b', 'PHRASE-c', 'PHRASE-d', ...Object.keys(inventory.labels)], Object.keys(inventory.features), Object.keys(symbols));
  guide.append(all);
  return guide;
}
