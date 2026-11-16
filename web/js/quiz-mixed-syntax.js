import { builderProfile, paletteFor } from './syntax-builder.js';

const w = word => ({ word });
const p = (label, children, extra = {}) => ({ label, children, ...extra });
const g = (index = 1) => ({ gap: true, index });

function leavesOf(node, out = []) {
  if (!node) return out;
  if ('word' in node && node.word !== undefined) {
    out.push(node.word);
    return out;
  }
  for (const c of node.children || []) leavesOf(c, out);
  return out;
}

function tree(ch, root) {
  const profile = builderProfile(ch);
  const words = leavesOf(root);
  let offset = 0;
  const tokens = words.map((text, index) => {
    const start = offset;
    offset += text.length;
    const end = offset;
    offset += 1;
    return { index, text, char_span: [start, end] };
  });
  return {
    schema_version: '1.1.0',
    tree_id: `quiz-mixed-br-${String(ch).padStart(2, '0')}`,
    sentence: words.join(' '),
    tokens,
    convention_profile: profile,
    source: { book: 'Burton-Roberts', chapter: ch, evidence_status: 'PROJECT_APPROVED', review_status: 'PROJECT_APPROVED' },
    movement: [],
    accepted_alternatives: [],
    root,
  };
}

const syntaxDiff = (ch, kind) => {
  if (ch <= 4) return kind === 'tree_builder' || kind === 'syntax_correction' ? 'medium' : 'easy';
  if (ch <= 8) return kind === 'fill_blank' ? 'easy' : kind === 'sentence_reconstruction' ? 'medium' : 'hard';
  return kind === 'tree_builder' || kind === 'syntax_correction' ? 'hard' : 'medium';
};

function mkBlank(ch, id, topic, prompt, accepted, rationale, sentence = null) {
  return {
    item_id: `mixed:br-${String(ch).padStart(2, '0')}:${topic}:fill_blank:${id}`,
    pool_id: `mixed:br-${String(ch).padStart(2, '0')}:${topic}:fill_blank`,
    content_version: '2.0.0',
    track_id: 'syntax',
    chapter_id: `br-${String(ch).padStart(2, '0')}`,
    subtopic_id: topic,
    lesson_id: `br-${String(ch).padStart(2, '0')}`,
    concept_ids: [`br-${String(ch).padStart(2, '0')}:${topic}`],
    outcome_ids: ['o1'],
    lesson_reference: `#lesson/br-${String(ch).padStart(2, '0')}/${topic}`,
    kind: 'fill_blank',
    difficulty: syntaxDiff(ch, 'fill_blank'),
    prompt,
    ...(sentence ? { stimulus: { sentence } } : {}),
    accepted_answers: accepted,
    display_answer: accepted[0],
    rationale,
  };
}

function mkRecon(ch, id, topic, tokens, accepted, rationale, prompt = 'Arrange the supplied words/constituents into a well-formed expression matching this chapter.') {
  return {
    item_id: `mixed:br-${String(ch).padStart(2, '0')}:${topic}:sentence_reconstruction:${id}`,
    pool_id: `mixed:br-${String(ch).padStart(2, '0')}:${topic}:sentence_reconstruction`,
    content_version: '2.0.0',
    track_id: 'syntax',
    chapter_id: `br-${String(ch).padStart(2, '0')}`,
    subtopic_id: topic,
    lesson_id: `br-${String(ch).padStart(2, '0')}`,
    concept_ids: [`br-${String(ch).padStart(2, '0')}:${topic}`],
    outcome_ids: ['o1'],
    lesson_reference: `#lesson/br-${String(ch).padStart(2, '0')}/${topic}`,
    kind: 'sentence_reconstruction',
    difficulty: syntaxDiff(ch, 'sentence_reconstruction'),
    prompt,
    tokens,
    accepted_answers: accepted,
    display_answer: accepted[0],
    rationale,
  };
}

function mkTreeBuild(ch, id, topic, profileCh, prompt, root, rationale, summary, extras = []) {
  const profile = builderProfile(profileCh);
  const expected_tree = { ...tree(profileCh, root), convention_profile: profile };
  const accepted_trees = extras.map(r => ({ ...tree(profileCh, r), convention_profile: profile }));
  return {
    item_id: `mixed:br-${String(ch).padStart(2, '0')}:${topic}:tree_builder:${id}`,
    pool_id: `mixed:br-${String(ch).padStart(2, '0')}:${topic}:tree_builder`,
    content_version: '2.0.0',
    track_id: 'syntax',
    chapter_id: `br-${String(ch).padStart(2, '0')}`,
    subtopic_id: topic,
    lesson_id: `br-${String(ch).padStart(2, '0')}`,
    concept_ids: [`br-${String(ch).padStart(2, '0')}:${topic}`],
    outcome_ids: ['o1'],
    lesson_reference: `#lesson/br-${String(ch).padStart(2, '0')}/${topic}`,
    kind: 'tree_builder',
    difficulty: syntaxDiff(ch, 'tree_builder'),
    prompt,
    profile,
    labels: paletteFor(profile).labels,
    seed_tokens: expected_tree.sentence,
    expected_tree,
    accepted_trees,
    expected_summary: summary,
    rationale,
  };
}

function mkSyntaxFix(ch, id, topic, profileCh, prompt, seedRoot, expectedRoot, rationale, summary, extras = []) {
  const profile = builderProfile(profileCh);
  const seed_tree = { ...tree(profileCh, seedRoot), convention_profile: profile };
  const expected_tree = { ...tree(profileCh, expectedRoot), convention_profile: profile };
  const accepted_trees = extras.map(r => ({ ...tree(profileCh, r), convention_profile: profile }));
  return {
    item_id: `mixed:br-${String(ch).padStart(2, '0')}:${topic}:syntax_correction:${id}`,
    pool_id: `mixed:br-${String(ch).padStart(2, '0')}:${topic}:syntax_correction`,
    content_version: '2.0.0',
    track_id: 'syntax',
    chapter_id: `br-${String(ch).padStart(2, '0')}`,
    subtopic_id: topic,
    lesson_id: `br-${String(ch).padStart(2, '0')}`,
    concept_ids: [`br-${String(ch).padStart(2, '0')}:${topic}`],
    outcome_ids: ['o1'],
    lesson_reference: `#lesson/br-${String(ch).padStart(2, '0')}/${topic}`,
    kind: 'syntax_correction',
    difficulty: syntaxDiff(ch, 'syntax_correction'),
    prompt,
    stimulus: { sentence: expected_tree.sentence },
    profile,
    labels: paletteFor(profile).labels,
    seed_tree,
    expected_tree,
    accepted_trees,
    expected_summary: summary,
    rationale,
  };
}

export const syntaxMixedItems = [
  // Chapter 1: Sentence structure: constituents (V1: Sentence, Phrase, PHRASE)
  mkBlank(1, '1', 'concepts', 'A group of words that functions as a structural unit inside a larger expression is called a _____.', ['constituent'], 'Burton-Roberts Chapter 1 defines a constituent as a sequence of words forming a single structural unit.'),
  mkBlank(1, '2', 'concepts', 'The constituent test that drops an optional group such as “beside the old well” to see if the rest stays complete is the _____ test.', ['omission'], 'Omission drops a suspected optional constituent to check whether the remaining sequence stays well-formed.'),
  mkBlank(1, '3', 'worked-example', 'Substituting a single word like “there” for “beside the old well” applies the _____ test.', ['replacement', 'substitution'], 'Replacement (or substitution) replaces a whole constituent with a pro-form or shorter equivalent.'),
  mkBlank(1, '4', 'worked-example', 'On a phrase marker, a node dominates _____ and only the words belonging to its constituent.', ['all'], 'A single mother node in a tree reaches all and only the words inside that constituent.'),
  mkBlank(1, '5', 'application', 'One sequence of words with two distinct constituent groupings exhibits structural _____.', ['ambiguity'], 'Structural ambiguity arises when the same linear word order permits two hierarchical groupings.'),

  mkSyntaxFix(1, '1', 'worked-example', 1, 'Repair the flat structure below so “the old clock” forms a nested Phrase inside the outer Phrase “under the old clock”.',
    p('Phrase', [w('under'), w('the'), w('old'), w('clock')]),
    p('Phrase', [w('under'), p('Phrase', [w('the'), w('old'), w('clock')])]),
    '“the old clock” functions as a nested constituent inside “under the old clock”, not flat siblings alongside “under”.',
    '[Phrase under [Phrase the old clock]]'
  ),
  mkSyntaxFix(1, '2', 'concepts', 1, 'Repair the grouping below so “the gate” forms a Phrase inside “beside the gate”.',
    p('Phrase', [w('beside'), w('the'), w('gate')]),
    p('Phrase', [w('beside'), p('Phrase', [w('the'), w('gate')])]),
    '“beside” takes the entire landmark group “the gate” as its nested Phrase constituent.',
    '[Phrase beside [Phrase the gate]]'
  ),
  mkSyntaxFix(1, '3', 'application', 1, 'Repair the flat sentence below so “stopped” and nested “[Phrase by the river]” share an outer Phrase inside Sentence (“Inez [stopped [by the river]]”).',
    p('Sentence', [w('Inez'), w('stopped'), w('by'), w('the'), w('river')]),
    p('Sentence', [p('Phrase', [w('Inez')]), p('Phrase', [w('stopped'), p('Phrase', [w('by'), p('Phrase', [w('the'), w('river')])])])]),
    'Grouping “stopped” with its location constituent “[by [the river]]” captures the hierarchy inside Sentence.',
    '[Sentence [Phrase Inez] [Phrase stopped [Phrase by [Phrase the river]]]]',
    [p('Sentence', [w('Inez'), p('Phrase', [w('stopped'), p('Phrase', [w('by'), p('Phrase', [w('the'), w('river')])])])])]
  ),
  mkSyntaxFix(1, '4', 'worked-example', 1, 'Repair the bracketed hierarchy so “the bright lantern” sits inside a Phrase under “near”.',
    p('Phrase', [p('Phrase', [w('near'), w('the'), w('bright')]), w('lantern')]),
    p('Phrase', [w('near'), p('Phrase', [w('the'), w('bright'), w('lantern')])]),
    '“the bright lantern” is one constituent; detaching “lantern” outside the inner Phrase breaks the object grouping.',
    '[Phrase near [Phrase the bright lantern]]'
  ),
  mkSyntaxFix(1, '5', 'application', 1, 'Repair the tree to represent the reading where “the dog” has the collar (“the dog [with the red collar]”).',
    p('Phrase', [p('Phrase', [w('the'), w('dog')]), w('with'), w('the'), w('red'), w('collar')]),
    p('Phrase', [p('Phrase', [w('the'), w('dog')]), p('Phrase', [w('with'), p('Phrase', [w('the'), w('red'), w('collar')])])]),
    '“with the red collar” forms a nested Phrase combining with “the dog”.',
    '[Phrase [Phrase the dog] [Phrase with [Phrase the red collar]]]'
  ),

  mkRecon(1, '1', 'concepts', ['the', 'gate', 'beside'], ['beside the gate'], 'Order the preposition before its noun-group constituent to form the location phrase.'),
  mkRecon(1, '2', 'worked-example', ['clock', 'old', 'under', 'the'], ['under the old clock'], 'Place the location word “under” before its nested constituent “the old clock”.'),
  mkRecon(1, '3', 'application', ['with the binoculars', 'saw', 'the sailor', 'Inez'], ['Inez saw the sailor with the binoculars'], 'Arrange Subject, Verb, Object, and modifier into a complete sentence.'),
  mkRecon(1, '4', 'concepts', ['quietly', 'slept', 'the', 'cat'], ['the cat slept quietly'], 'Form a subject constituent followed by predicate verb and manner word.'),
  mkRecon(1, '5', 'application', ['by the door', 'waited', 'the', 'visitor'], ['the visitor waited by the door'], 'Group Subject followed by predicate and location phrase.'),

  mkTreeBuild(1, '1', 'worked-example', 1, 'Build a hierarchical Ch. 1 tree for “under the old clock” with “the old clock” grouped as an inner Phrase inside an outer Phrase.',
    p('Phrase', [w('under'), p('Phrase', [w('the'), w('old'), w('clock')])]),
    'Chapter 1 uses Phrase to show how “the old clock” nests inside “under the old clock”.',
    '[Phrase under [Phrase the old clock]]'
  ),
  mkTreeBuild(1, '2', 'concepts', 1, 'Build a nested Phrase tree for “near the dark well” with “the dark well” as an inner Phrase.',
    p('Phrase', [w('near'), p('Phrase', [w('the'), w('dark'), w('well')])]),
    'Nesting “the dark well” inside an inner Phrase shows constituent hierarchy.',
    '[Phrase near [Phrase the dark well]]'
  ),
  mkTreeBuild(1, '3', 'worked-example', 1, 'Build a Sentence tree for “Sam rested” using Phrase for “Sam” and Phrase for “rested” inside Sentence.',
    p('Sentence', [p('Phrase', [w('Sam')]), p('Phrase', [w('rested')])]),
    'Each immediate constituent of Sentence is grouped into its own Phrase.',
    '[Sentence [Phrase Sam] [Phrase rested]]'
  ),
  mkTreeBuild(1, '4', 'application', 1, 'Build a Sentence tree for “Leo waited inside” with “waited” and “[Phrase inside]” grouped inside a predicate Phrase.',
    p('Sentence', [p('Phrase', [w('Leo')]), p('Phrase', [w('waited'), p('Phrase', [w('inside')])])]),
    '“inside” nests inside the predicate Phrase under Sentence.',
    '[Sentence [Phrase Leo] [Phrase waited [Phrase inside]]]',
    [p('Sentence', [p('Phrase', [w('Leo')]), p('Phrase', [w('waited'), w('inside')])])]
  ),
  mkTreeBuild(1, '5', 'concepts', 1, 'Build a Phrase tree for “beside the quiet lake” nesting “the quiet lake” inside a child Phrase.',
    p('Phrase', [w('beside'), p('Phrase', [w('the'), w('quiet'), w('lake')])]),
    'The landmark “the quiet lake” forms a constituent inside “beside the quiet lake”.',
    '[Phrase beside [Phrase the quiet lake]]'
  ),

  // Chapter 2: Sentence structure: functions (V2: S, NP, VP)
  mkBlank(2, '1', 'concepts', 'A basic clause splits immediately under S into Subject and _____.', ['predicate'], 'Subject and predicate are the two immediate functions of a basic clause under S.'),
  mkBlank(2, '2', 'worked-example', 'Nodes that share the same immediate parent node are called _____.', ['sisters'], 'Nodes sharing a parent node in a tree are sisters.'),
  mkBlank(2, '3', 'concepts', 'In Burton-Roberts Chapter 2, the phrasal category filling the Subject function in “Mira checked the lantern” is _____.', ['NP'], 'Subject is a syntactic function normally filled by an NP (noun phrase).'),
  mkBlank(2, '4', 'concepts', 'The syntactic function of the VP in a basic declarative clause is _____.', ['predicate'], 'The predicate function is filled by a VP.'),
  mkBlank(2, '5', 'application', 'In “Mira checked the lantern”, “checked” is the _____ of the VP.', ['head'], 'The verb is the head of the VP.'),

  mkSyntaxFix(2, '1', 'concepts', 2, 'Repair the tree so S splits into Subject NP (“the dogs”) and Predicate VP (“barked”), rather than grouping all words flatly under S.',
    p('S', [w('the'), w('dogs'), w('barked')]),
    p('S', [p('NP', [w('the'), w('dogs')]), p('VP', [w('barked')])]),
    'Under S, the clause divides into two immediate constituents: Subject NP and Predicate VP.',
    '[S [NP the dogs] [VP barked]]'
  ),
  mkSyntaxFix(2, '2', 'worked-example', 2, 'Repair the tree so the object NP “the lantern” sits inside VP as sister to “checked”, rather than directly under S.',
    p('S', [p('NP', [w('Mira')]), p('VP', [w('checked')]), p('NP', [w('the'), w('lantern')])]),
    p('S', [p('NP', [w('Mira')]), p('VP', [w('checked'), p('NP', [w('the'), w('lantern')])])]),
    'A direct object NP belongs inside the predicate VP, not as a third sister directly under S.',
    '[S [NP Mira] [VP checked [NP the lantern]]]'
  ),
  mkSyntaxFix(2, '3', 'application', 2, 'Repair the label mismatch so “the warm soup” is an NP inside VP and “the guests” is the Subject NP.',
    p('S', [p('VP', [w('the'), w('guests')]), p('NP', [w('tasted'), p('VP', [w('the'), w('warm'), w('soup')])])]),
    p('S', [p('NP', [w('the'), w('guests')]), p('VP', [w('tasted'), p('NP', [w('the'), w('warm'), w('soup')])])]),
    'Subject and object arguments are NPs; the predicate headed by “tasted” is the VP.',
    '[S [NP the guests] [VP tasted [NP the warm soup]]]'
  ),
  mkSyntaxFix(2, '4', 'worked-example', 2, 'Repair the tree so “quickly” modifies inside VP alongside “moved” rather than sitting inside Subject NP.',
    p('S', [p('NP', [w('birds'), w('quickly')]), p('VP', [w('moved')])]),
    p('S', [p('NP', [w('birds')]), p('VP', [w('quickly'), w('moved')])]),
    '“quickly” modifies the predicate event inside VP, leaving “birds” as Subject NP.',
    '[S [NP birds] [VP quickly moved]]'
  ),
  mkSyntaxFix(2, '5', 'concepts', 2, 'Repair the tree so Subject NP and Predicate VP are sisters directly under S.',
    p('VP', [p('NP', [w('cats')]), w('sleep')]),
    p('S', [p('NP', [w('cats')]), p('VP', [w('sleep')])]),
    'The root node of a basic clause is S, dominating Subject NP and Predicate VP.',
    '[S [NP cats] [VP sleep]]'
  ),

  mkRecon(2, '1', 'worked-example', ['the lantern', 'checked', 'Mira'], ['Mira checked the lantern'], 'Place Subject NP before transitive Predicate VP containing its object NP.'),
  mkRecon(2, '2', 'concepts', ['the', 'children', 'laughed'], ['the children laughed'], 'Order Subject NP before intransitive VP.'),
  mkRecon(2, '3', 'application', ['folded', 'Nico', 'a', 'towel'], ['Nico folded a towel'], 'Arrange Subject NP, verb, and direct object NP.'),
  mkRecon(2, '4', 'worked-example', ['a', 'bell', 'the', 'clerk', 'rang'], ['the clerk rang a bell'], 'Order Subject NP before predicate verb + object NP.'),
  mkRecon(2, '5', 'application', ['guarded', 'dogs', 'the', 'two', 'gate'], ['two dogs guarded the gate'], 'Order Subject NP “two dogs” before VP “guarded the gate”.'),

  mkTreeBuild(2, '1', 'worked-example', 2, 'Build an S tree for “Mira checked the lantern” showing Subject NP, Predicate VP, and Object NP inside VP.',
    p('S', [p('NP', [w('Mira')]), p('VP', [w('checked'), p('NP', [w('the'), w('lantern')])])]),
    'Under S, “Mira” is Subject NP and “checked [NP the lantern]” is Predicate VP.',
    '[S [NP Mira] [VP checked [NP the lantern]]]'
  ),
  mkTreeBuild(2, '2', 'concepts', 2, 'Build an S tree for “Sam smiled” using Subject NP and Predicate VP.',
    p('S', [p('NP', [w('Sam')]), p('VP', [w('smiled')])]),
    'Intransitive clauses still split under S into Subject NP and Predicate VP.',
    '[S [NP Sam] [VP smiled]]'
  ),
  mkTreeBuild(2, '3', 'application', 2, 'Build an S tree for “Nico folded a towel” with “a towel” as Object NP inside VP.',
    p('S', [p('NP', [w('Nico')]), p('VP', [w('folded'), p('NP', [w('a'), w('towel')])])]),
    '“Nico” is Subject NP and “a towel” is Object NP inside VP.',
    '[S [NP Nico] [VP folded [NP a towel]]]'
  ),
  mkTreeBuild(2, '4', 'worked-example', 2, 'Build an S tree for “dogs chased cats” using S, NP, and VP.',
    p('S', [p('NP', [w('dogs')]), p('VP', [w('chased'), p('NP', [w('cats')])])]),
    'Subject NP and Predicate VP share S; object NP “cats” sits inside VP.',
    '[S [NP dogs] [VP chased [NP cats]]]'
  ),
  mkTreeBuild(2, '5', 'application', 2, 'Build an S tree for “water freezes” showing Subject NP and Predicate VP.',
    p('S', [p('NP', [w('water')]), p('VP', [w('freezes')])]),
    'Under S, “water” is Subject NP and “freezes” is Predicate VP.',
    '[S [NP water] [VP freezes]]'
  ),

  // Chapter 3: Sentence structure: categories (V3)
  mkBlank(3, '1', 'concepts', 'The word that determines the category of a phrase is its _____.', ['head'], 'The head gives a phrase its grammatical category (noun -> NP, adjective -> AP, etc.).'),
  mkBlank(3, '2', 'worked-example', 'In “very cold”, “very” belongs to the degree category abbreviated _____.', ['DEG', 'degree'], 'Burton-Roberts assigns words like “very”, “quite”, “rather” to DEG (degree adverb/modifier).'),
  mkBlank(3, '3', 'prepositions-and-coordination', 'In “beside the door”, the head word “beside” has lexical category _____.', ['P', 'preposition'], '“beside” is a preposition (P), heading a PP.'),
  mkBlank(3, '4', 'concepts', 'Proper names such as “Mira” or “Paris” form an NP without needing determiners and take lexical label _____.', ['name', 'proper name'], 'Chapter 3 introduces lexical label “name” (alongside “pronoun”) heading an NP.'),
  mkBlank(3, '5', 'worked-example', 'When two phrases of the same category join with “and”, the mother phrase keeps that _____ category.', ['same', 'shared'], 'Ordinary coordination joins two phrases of the same category to form a larger phrase of that category.'),

  mkSyntaxFix(3, '1', 'worked-example', 3, 'Repair the AP tree for “very cold” so “very” is labelled DEG (not A) and “cold” is labelled A.',
    p('AP', [p('A', [w('very')]), p('DEG', [w('cold')])]),
    p('AP', [p('DEG', [w('very')]), p('A', [w('cold')])]),
    '“very” is a degree word (DEG), while “cold” is the head adjective (A).',
    '[AP [DEG very] [A cold]]'
  ),
  mkSyntaxFix(3, '2', 'prepositions-and-coordination', 3, 'Repair the PP tree for “for Sam” so “Sam” is headed by name inside NP under PP, not P.',
    p('PP', [p('P', [w('for')]), p('P', [w('Sam')])]),
    p('PP', [p('P', [w('for')]), p('NP', [p('name', [w('Sam')])])]),
    'Preposition P “for” takes a complement NP “[NP [name Sam]]”.',
    '[PP [P for] [NP [name Sam]]]'
  ),
  mkSyntaxFix(3, '3', 'concepts', 3, 'Repair the AdvP tree for “quite slowly” so “quite” is DEG and “slowly” is Adv inside AdvP.',
    p('AdvP', [p('Adv', [w('quite')]), p('DEG', [w('slowly')])]),
    p('AdvP', [p('DEG', [w('quite')]), p('Adv', [w('slowly')])]),
    '“quite” is a degree word (DEG) modifying head adverb (Adv) “slowly”.',
    '[AdvP [DEG quite] [Adv slowly]]'
  ),
  mkSyntaxFix(3, '4', 'prepositions-and-coordination', 3, 'Repair the coordinated NP “Sam and Lena” so each name sits inside its own NP under the mother NP.',
    p('NP', [w('Sam'), w('and'), p('NP', [p('name', [w('Lena')])])]),
    p('NP', [p('NP', [p('name', [w('Sam')])]), w('and'), p('NP', [p('name', [w('Lena')])])]),
    'Two NPs “[NP [name Sam]]” and “[NP [name Lena]]” coordinate to form a larger NP.',
    '[NP [NP [name Sam]] and [NP [name Lena]]]'
  ),
  mkSyntaxFix(3, '5', 'concepts', 3, 'Repair the NP “warm tea” so “warm” is an AP ([AP [A warm]]) modifying head noun N “tea”.',
    p('NP', [p('N', [w('warm')]), p('A', [w('tea')])]),
    p('NP', [p('AP', [p('A', [w('warm')])]), p('N', [w('tea')])]),
    '“warm” is an adjective heading AP inside the NP whose head is noun N “tea”.',
    '[NP [AP [A warm]] [N tea]]',
    [p('NP', [p('A', [w('warm')]), p('N', [w('tea')])])]
  ),

  mkRecon(3, '1', 'worked-example', ['gentle', 'quite', 'rain'], ['quite gentle rain'], 'Place degree word DEG before head adjective A inside AP modifying noun “rain”.'),
  mkRecon(3, '2', 'prepositions-and-coordination', ['quietly', 'very', 'spoke', 'she'], ['she spoke very quietly'], 'Order Subject pronoun before verb and degree-modified AdvP.'),
  mkRecon(3, '3', 'concepts', ['Sam', 'and', 'Lena'], ['Sam and Lena', 'Lena and Sam'], 'Coordinate the two proper-name NPs with “and”.'),
  mkRecon(3, '4', 'prepositions-and-coordination', ['by', 'Mira', 'notes'], ['notes by Mira'], 'Order head noun “notes” before prepositional modifier “by Mira”.'),
  mkRecon(3, '5', 'worked-example', ['tea', 'fresh', 'hot'], ['fresh hot tea', 'hot fresh tea'], 'Place pre-modifying adjectives before head noun “tea”.'),

  mkTreeBuild(3, '1', 'worked-example', 3, 'Build a Ch. 3 AP tree for “quite gentle” using AP, DEG, and A.',
    p('AP', [p('DEG', [w('quite')]), p('A', [w('gentle')])]),
    'In “quite gentle”, “quite” is DEG and head “gentle” is A under AP.',
    '[AP [DEG quite] [A gentle]]'
  ),
  mkTreeBuild(3, '2', 'worked-example', 3, 'Build a Ch. 3 AdvP tree for “rather fast” using AdvP, DEG, and Adv.',
    p('AdvP', [p('DEG', [w('rather')]), p('Adv', [w('fast')])]),
    '“rather” is DEG modifying head adverb Adv “fast” inside AdvP.',
    '[AdvP [DEG rather] [Adv fast]]'
  ),
  mkTreeBuild(3, '3', 'prepositions-and-coordination', 3, 'Build a Ch. 3 PP tree for “with Lena” using PP, P, NP, and name.',
    p('PP', [p('P', [w('with')]), p('NP', [p('name', [w('Lena')])])]),
    'Preposition P “with” takes NP “[NP [name Lena]]” as its complement inside PP.',
    '[PP [P with] [NP [name Lena]]]'
  ),
  mkTreeBuild(3, '4', 'concepts', 3, 'Build a Ch. 3 NP tree for “cold milk” using NP, AP, A, and N.',
    p('NP', [p('AP', [p('A', [w('cold')])]), p('N', [w('milk')])]),
    'Adjective “cold” heads an AP modifying head noun N “milk” inside NP.',
    '[NP [AP [A cold]] [N milk]]'
  ),
  mkTreeBuild(3, '5', 'prepositions-and-coordination', 3, 'Build a coordinated AP tree for “warm and bright” joining two APs under a mother AP.',
    p('AP', [p('AP', [p('A', [w('warm')])]), w('and'), p('AP', [p('A', [w('bright')])])]),
    'Coordinated APs join two AP daughters with “and” under a mother AP.',
    '[AP [AP [A warm]] and [AP [A bright]]]'
  ),

  // Chapter 4: The basic Verb Phrase (V4)
  mkBlank(4, '1', 'concepts', 'A verb such as “slept” that takes no object or predicative complement is called _____.', ['intransitive'], 'Intransitive verbs take no complement in the basic VP.'),
  mkBlank(4, '2', 'worked-example', 'A verb such as “gave” taking both an indirect object and a direct object is _____.', ['ditransitive'], 'Ditransitive verbs take two object NPs (e.g. NP + NP or NP + PP).'),
  mkBlank(4, '3', 'predicatives', 'In “Kim became calm”, the AP “calm” functions as a _____ complement.', ['predicative', 'subject-predicative'], 'Intensive/copular verbs such as “become” or “be” take a predicative complement.'),
  mkBlank(4, '4', 'prepositional-complements', 'A verb like “put” requires both an object NP and a _____ phrase complement.', ['prepositional', 'PP', 'locational'], 'Complex-transitive / prepositional verbs like “put” take NP + PP complements.'),
  mkBlank(4, '5', 'concepts', 'Every lexical verb in Chapter 4 carries a verb feature (such as [trans]) on node _____.', ['V'], 'Subcategorisation features mark lexical verb category V.'),

  mkSyntaxFix(4, '1', 'worked-example', 4, 'Repair the VP tree for “Mira thanked Sam” so “thanked” is labelled V inside VP with object NP “[NP [name Sam]]”.',
    p('S', [p('NP', [p('name', [w('Mira')])]), p('VP', [p('N', [w('thanked')]), p('NP', [p('name', [w('Sam')])])])]),
    p('S', [p('NP', [p('name', [w('Mira')])]), p('VP', [p('V', [w('thanked')], { features: ['trans'] }), p('NP', [p('name', [w('Sam')])])])]),
    '“thanked” is a transitive verb (V [trans]), not a noun.',
    '[S [NP [name Mira]] [VP [V thanked [trans]] [NP [name Sam]]]]',
    [p('S', [p('NP', [p('name', [w('Mira')])]), p('VP', [p('V', [w('thanked')]), p('NP', [p('name', [w('Sam')])])])])]
  ),
  mkSyntaxFix(4, '2', 'predicatives', 4, 'Repair the tree for “Leo seemed happy” so “happy” is an AP complement inside VP rather than inside Subject NP.',
    p('S', [p('NP', [p('name', [w('Leo')]), p('AP', [p('A', [w('happy')])])]), p('VP', [p('V', [w('seemed')])])]),
    p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('seemed')], { features: ['intens'] }), p('AP', [p('A', [w('happy')])])])]),
    '“happy” is the predicative complement of intensive verb “seemed” inside VP.',
    '[S [NP [name Leo]] [VP [V seemed [intens]] [AP [A happy]]]]',
    [p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('seemed')]), p('AP', [p('A', [w('happy')])])])])]
  ),
  mkSyntaxFix(4, '3', 'prepositional-complements', 4, 'Repair the tree for “Ada went to York” so “[PP to York]” is a sister to V inside VP.',
    p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('went')])]), p('PP', [p('P', [w('to')]), p('NP', [p('name', [w('York')])])])]),
    p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('went')], { features: ['prep'] }), p('PP', [p('P', [w('to')]), p('NP', [p('name', [w('York')])])])])]),
    'Directional PP complement “to York” sits inside VP as sister to V.',
    '[S [NP [name Ada]] [VP [V went] [PP [P to] [NP [name York]]]]]',
    [p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('went')]), p('PP', [p('P', [w('to')]), p('NP', [p('name', [w('York')])])])])])]
  ),
  mkSyntaxFix(4, '4', 'worked-example', 4, 'Repair the ditransitive VP in “Kim gave Leo tea” so both object NPs are direct sisters of V inside VP.',
    p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('gave')]), p('NP', [p('name', [w('Leo')]), p('NP', [p('N', [w('tea')])])])])]),
    p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('gave')], { features: ['ditrans'] }), p('NP', [p('name', [w('Leo')])]), p('NP', [p('N', [w('tea')])])])]),
    'In a ditransitive VP, V takes two sister NP complements (“Leo” and “tea”) rather than nesting one inside the other.',
    '[S [NP [name Kim]] [VP [V gave] [NP [name Leo]] [NP [N tea]]]]',
    [p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('gave')]), p('NP', [p('name', [w('Leo')])]), p('NP', [p('N', [w('tea')])])])])]
  ),
  mkSyntaxFix(4, '5', 'concepts', 4, 'Repair the intransitive sentence “rain fell” so “fell” is V inside VP.',
    p('S', [p('NP', [p('N', [w('rain')])]), p('NP', [p('V', [w('fell')])])]),
    p('S', [p('NP', [p('N', [w('rain')])]), p('VP', [p('V', [w('fell')], { features: ['intrans'] })])]),
    'The predicate is headed by V inside VP, never NP.',
    '[S [NP [N rain]] [VP [V fell]]]',
    [p('S', [p('NP', [p('N', [w('rain')])]), p('VP', [p('V', [w('fell')])])])]
  ),

  mkRecon(4, '1', 'worked-example', ['books', 'sent', 'Kim', 'Lena'], ['Kim sent Lena books', 'Lena sent Kim books'], 'Order Subject, ditransitive verb, indirect object, and direct object.'),
  mkRecon(4, '2', 'predicatives', ['became', 'air', 'cool', 'fresh'], ['fresh air became cool'], 'Place Subject NP before intensive verb and predicative AP.'),
  mkRecon(4, '3', 'prepositional-complements', ['put', 'on', 'salt', 'bread', 'she'], ['she put salt on bread'], 'Complex-transitive verb “put” takes direct object NP before directional PP.'),
  mkRecon(4, '4', 'concepts', ['smiled', 'visitor', 'every'], ['every visitor smiled'], 'Subject NP precedes intransitive verb.'),
  mkRecon(4, '5', 'predicatives', ['quiet', 'remained', 'Paris'], ['Paris remained quiet'], 'Intensive verb “remained” links Subject NP to predicative AP.'),

  mkTreeBuild(4, '1', 'predicatives', 4, 'Build a Ch. 4 S tree for “Kim looked calm” using S, NP, name, VP, V, AP, and A.',
    p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('looked')]), p('AP', [p('A', [w('calm')])])])]),
    'Intensive verb V “looked” takes predicative AP “[AP [A calm]]” inside VP.',
    '[S [NP [name Kim]] [VP [V looked] [AP [A calm]]]]',
    [p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('looked')], { features: ['intens'] }), p('AP', [p('A', [w('calm')])])])])]
  ),
  mkTreeBuild(4, '2', 'concepts', 4, 'Build a Ch. 4 S tree for “dogs barked” using S, NP, N, VP, and V.',
    p('S', [p('NP', [p('N', [w('dogs')])]), p('VP', [p('V', [w('barked')])])]),
    '“dogs” is N inside Subject NP; “barked” is intransitive V inside VP.',
    '[S [NP [N dogs]] [VP [V barked]]]',
    [p('S', [p('NP', [p('N', [w('dogs')])]), p('VP', [p('V', [w('barked')], { features: ['intrans'] })])])]
  ),
  mkTreeBuild(4, '3', 'worked-example', 4, 'Build a Ch. 4 S tree for “she met Sam” using pronoun, V, and name.',
    p('S', [p('NP', [p('pronoun', [w('she')])]), p('VP', [p('V', [w('met')]), p('NP', [p('name', [w('Sam')])])])]),
    'Subject NP dominates pronoun “she”; VP dominates transitive V “met” and NP “[NP [name Sam]]”.',
    '[S [NP [pronoun she]] [VP [V met] [NP [name Sam]]]]',
    [p('S', [p('NP', [p('pronoun', [w('she')])]), p('VP', [p('V', [w('met')], { features: ['trans'] }), p('NP', [p('name', [w('Sam')])])])])]
  ),
  mkTreeBuild(4, '4', 'prepositional-complements', 4, 'Build a Ch. 4 S tree for “Inez leaned on Sam” with PP complement inside VP.',
    p('S', [p('NP', [p('name', [w('Inez')])]), p('VP', [p('V', [w('leaned')]), p('PP', [p('P', [w('on')]), p('NP', [p('name', [w('Sam')])])])])]),
    'Prepositional verb V “leaned” takes PP “[PP [P on] [NP [name Sam]]]” inside VP.',
    '[S [NP [name Inez]] [VP [V leaned] [PP [P on] [NP [name Sam]]]]]',
    [p('S', [p('NP', [p('name', [w('Inez')])]), p('VP', [p('V', [w('leaned')], { features: ['prep'] }), p('PP', [p('P', [w('on')]), p('NP', [p('name', [w('Sam')])])])])])]
  ),
  mkTreeBuild(4, '5', 'worked-example', 4, 'Build a Ch. 4 S tree for “Leo called Mira clever” with object NP + predicative AP inside VP.',
    p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('called')]), p('NP', [p('name', [w('Mira')])]), p('AP', [p('A', [w('clever')])])])]),
    'Complex-transitive verb “called” takes object NP and object-predicative AP inside VP.',
    '[S [NP [name Leo]] [VP [V called] [NP [name Mira]] [AP [A clever]]]]',
    [p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('called')], { features: ['complex'] }), p('NP', [p('name', [w('Mira')])]), p('AP', [p('A', [w('clever')])])])])]
  ),

  // Chapter 5: Adverbials and other matters (V5)
  mkBlank(5, '1', 'concepts', 'An optional VP modifier attached to a higher VP sister rather than required by the verb is a VP _____.', ['adjunct', 'adverbial'], 'Adjunct adverbials attach as sisters to a VP inside a higher VP.'),
  mkBlank(5, '2', 'particles', 'In “Kim turned the lamp off”, “off” is a phrasal verb _____ rather than a full PP head.', ['particle', 'Prt'], 'Phrasal verb particles (Prt) can move after the direct object NP, unlike prepositional complements.'),
  mkBlank(5, '3', 'worked-example', 'Sentence adverbials such as “frankly” modify the entire _____ rather than just the VP.', ['sentence', 'S', 'clause'], 'Sentence adverbials attach directly to S (or higher S) above Subject NP and Predicate VP.'),
  mkBlank(5, '4', 'ellipsis', 'Using “did so” to replace an inner VP leaves outer VP _____ unaffected outside it.', ['adjuncts', 'adverbials'], '“do so” replaces a VP level while leaving higher adjunct adverbials outside it.'),
  mkBlank(5, '5', 'mobility', 'Unlike verbal complements, most VP adjuncts exhibit positional _____ before or after the core VP.', ['mobility'], 'Adverbials can often appear before or after VP or sentence-initially.'),

  mkSyntaxFix(5, '1', 'worked-example', 5, 'Repair the VP hierarchy for “Mira read in Rome” so the location PP adjunct is sister to a lower VP “[VP [V read]]” inside an upper VP.',
    p('S', [p('NP', [p('name', [w('Mira')])]), p('VP', [p('V', [w('read')]), p('PP', [p('P', [w('in')]), p('NP', [p('name', [w('Rome')])])])])]),
    p('S', [p('NP', [p('name', [w('Mira')])]), p('VP', [p('VP', [p('V', [w('read')])]), p('PP', [p('P', [w('in')]), p('NP', [p('name', [w('Rome')])])])])]),
    'Adjunct PP attaches to an inner VP under a higher VP (VP -> VP + PP), distinguishing adjuncts from verb complements.',
    '[S [NP [name Mira]] [VP [VP [V read]] [PP [P in] [NP [name Rome]]]]]'
  ),
  mkSyntaxFix(5, '2', 'particles', 5, 'Repair “Sam looked up Leo” so “up” is a phrasal particle Prt alongside V inside VP (not P heading a PP).',
    p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('looked')]), p('PP', [p('P', [w('up')]), p('NP', [p('name', [w('Leo')])])])])]),
    p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('looked')]), p('Prt', [w('up')]), p('NP', [p('name', [w('Leo')])])])]),
    'In phrasal “look up”, “up” is a particle (Prt) sister to V and NP (“look Leo up”).',
    '[S [NP [name Sam]] [VP [V looked] [Prt up] [NP [name Leo]]]]',
    [p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('looked')], { features: ['phrasal'] }), p('Prt', [w('up')]), p('NP', [p('name', [w('Leo')])])])])]
  ),
  mkSyntaxFix(5, '3', 'concepts', 5, 'Repair the tree for “perhaps Kim slept” so sentence adverbial AdvP “perhaps” attaches directly under upper S.',
    p('S', [p('NP', [p('name', [w('Kim')]), p('AdvP', [p('Adv', [w('perhaps')])])]), p('VP', [p('V', [w('slept')])])]),
    p('S', [p('AdvP', [p('Adv', [w('perhaps')])]), p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('slept')])])])]),
    'Sentence adverbial AdvP “perhaps” attaches under an outer S dominating S (“S -> AdvP + S”), never inside Subject NP.',
    '[S [AdvP [Adv perhaps]] [S [NP [name Kim]] [VP [V slept]]]]',
    [p('S', [p('AdvP', [p('Adv', [w('perhaps')])]), p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('slept')])])])]
  ),
  mkSyntaxFix(5, '4', 'mobility', 5, 'Repair “Leo quickly walked” so AdvP “quickly” attaches as sister to inner VP “[VP [V walked]]”.',
    p('S', [p('NP', [p('name', [w('Leo')]), p('AdvP', [p('Adv', [w('quickly')])])]), p('VP', [p('V', [w('walked')])])]),
    p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('AdvP', [p('Adv', [w('quickly')])]), p('VP', [p('V', [w('walked')])])])]),
    'Manner AdvP “quickly” modifies the lower VP inside an upper VP.',
    '[S [NP [name Leo]] [VP [AdvP [Adv quickly]] [VP [V walked]]]]'
  ),
  mkSyntaxFix(5, '5', 'application', 5, 'Repair “she read quietly on Tuesday” so “quietly” attaches first to lower VP and “on Tuesday” attaches outside it.',
    p('S', [p('NP', [p('pronoun', [w('she')])]), p('VP', [p('V', [w('read')]), p('AdvP', [p('Adv', [w('quietly')])]), p('PP', [p('P', [w('on')]), p('NP', [p('name', [w('Tuesday')])])])])]),
    p('S', [p('NP', [p('pronoun', [w('she')])]), p('VP', [p('VP', [p('VP', [p('V', [w('read')])]), p('AdvP', [p('Adv', [w('quietly')])])]), p('PP', [p('P', [w('on')]), p('NP', [p('name', [w('Tuesday')])])])])]),
    'Each VP adjunct creates its own binary VP layer (VP -> VP + Adjunct).',
    '[S [NP [pronoun she]] [VP [VP [VP [V read]] [AdvP [Adv quietly]]] [PP [P on] [NP [name Tuesday]]]]]'
  ),

  mkRecon(5, '1', 'particles', ['off', 'Mira', 'switched', 'lamps'], ['Mira switched lamps off', 'Mira switched off lamps'], 'Phrasal particle “off” can follow either the verb or its direct object NP.'),
  mkRecon(5, '2', 'worked-example', ['quickly', 'departed', 'trains'], ['trains departed quickly', 'trains quickly departed'], 'Manner adverbial AdvP occurs comfortably before or after VP.'),
  mkRecon(5, '3', 'concepts', ['fortunately', 'survived', 'everyone'], ['fortunately everyone survived', 'everyone fortunately survived'], 'Sentence adverbial “fortunately” can sit sentence-initially or medially.'),
  mkRecon(5, '4', 'mobility', ['yesterday', 'arrived', 'Ada'], ['Ada arrived yesterday', 'yesterday Ada arrived'], 'Time adjunct PP/Adv appears in initial or final position.'),
  mkRecon(5, '5', 'particles', ['up', 'looked', 'it', 'Sam'], ['Sam looked it up'], 'With an unstressed pronoun object “it”, the particle “up” must follow the pronoun.'),

  mkTreeBuild(5, '1', 'worked-example', 5, 'Build a Ch. 5 tree for “Kim slept soundly” using two VP layers (VP -> VP + AdvP).',
    p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('VP', [p('V', [w('slept')])]), p('AdvP', [p('Adv', [w('soundly')])])])]),
    'Adjunct “soundly” attaches to a lower VP “[VP [V slept]]” inside an upper VP.',
    '[S [NP [name Kim]] [VP [VP [V slept]] [AdvP [Adv soundly]]]]'
  ),
  mkTreeBuild(5, '2', 'particles', 5, 'Build a Ch. 5 phrasal verb tree for “Sam woke Lena up” using Prt.',
    p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('woke')]), p('NP', [p('name', [w('Lena')])]), p('Prt', [w('up')])])]),
    'Verb V, object NP “Lena”, and particle Prt “up” share the VP.',
    '[S [NP [name Sam]] [VP [V woke] [NP [name Lena]] [Prt up]]]'
  ),
  mkTreeBuild(5, '3', 'concepts', 5, 'Build a Ch. 5 tree for “Inez waited outside” attaching “[PP [P outside]]” as adjunct to lower VP.',
    p('S', [p('NP', [p('name', [w('Inez')])]), p('VP', [p('VP', [p('V', [w('waited')])]), p('PP', [p('P', [w('outside')])])])]),
    'Optional location PP adjunct attaches at VP level above “[VP [V waited]]”.',
    '[S [NP [name Inez]] [VP [VP [V waited]] [PP [P outside]]]]'
  ),
  mkTreeBuild(5, '4', 'mobility', 5, 'Build a Ch. 5 tree for “slowly he turned” with AdvP modifying lower VP inside upper VP.',
    p('S', [p('AdvP', [p('Adv', [w('slowly')])]), p('S', [p('NP', [p('pronoun', [w('he')])]), p('VP', [p('V', [w('turned')])])])]),
    'Sentence-initial adverbial attaches under outer S (or VP fronting), dominating S.',
    '[S [AdvP [Adv slowly]] [S [NP [pronoun he]] [VP [V turned]]]]',
    [p('S', [p('AdvP', [p('Adv', [w('slowly')])]), p('NP', [p('pronoun', [w('he')])]), p('VP', [p('V', [w('turned')])])])]
  ),
  mkTreeBuild(5, '5', 'application', 5, 'Build a Ch. 5 tree for “Ada smiled on Monday” showing higher VP -> lower VP + PP.',
    p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('VP', [p('V', [w('smiled')])]), p('PP', [p('P', [w('on')]), p('NP', [p('name', [w('Monday')])])])])]),
    'Temporal adjunct PP “on Monday” sits outside lower VP “[VP [V smiled]]”.',
    '[S [NP [name Ada]] [VP [VP [V smiled]] [PP [P on] [NP [name Monday]]]]]'
  ),

  // Chapter 6: More on verbs: auxiliary VPs (V6)
  mkBlank(6, '1', 'chain', 'In the strict auxiliary order MOD – PERF – PROG – PASS, the progressive auxiliary is _____ followed by a -ing lexical verb.', ['be'], 'Progressive aspect combines auxiliary PROG (forms of “be”) with a progressive -ing verb.'),
  mkBlank(6, '2', 'negation', 'The negative particle “not” attaches immediately after the first _____ verb carrying tense.', ['auxiliary', 'tensed'], 'Sentential negation “not” follows the first tensed auxiliary.'),
  mkBlank(6, '3', 'concepts', 'In “Leo had slept”, “had” heads a higher VP under label _____.', ['PERF'], 'Perfect “have” sits under PERF heading its auxiliary VP.'),
  mkBlank(6, '4', 'questions', 'When no auxiliary is present in a yes/no question, English inserts dummy auxiliary _____.', ['do', 'did', 'does'], 'Do-support supplies a tensed auxiliary in questions/negation when no other auxiliary exists.'),
  mkBlank(6, '5', 'passive', 'In “Mira was thanked”, passive auxiliary “was” sits under _____ above the lexical VP.', ['PASS'], 'Passive auxiliary “be” is labelled PASS heading an auxiliary VP.'),

  mkSyntaxFix(6, '1', 'chain', 6, 'Repair “Sam may leave” so “may” is MOD (not V) heading an upper VP over lexical “[VP [V leave]]”.',
    p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('may')]), p('V', [w('leave')])])]),
    p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('MOD', [w('may')]), p('VP', [p('V', [w('leave')])])])]),
    'Modal auxiliaries carry label MOD and take a lexical VP complement.',
    '[S [NP [name Sam]] [VP [MOD may] [VP [V leave]]]]'
  ),
  mkSyntaxFix(6, '2', 'concepts', 6, 'Repair “Leo is smiling” so “is” sits under PROG heading an upper VP over “[VP [V smiling]]”.',
    p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('is')]), w('smiling')])]),
    p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('PROG', [w('is')]), p('VP', [p('V', [w('smiling')])])])]),
    'Progressive “be” is labelled PROG heading its own VP containing the main lexical VP.',
    '[S [NP [name Leo]] [VP [PROG is] [VP [V smiling]]]]'
  ),
  mkSyntaxFix(6, '3', 'passive', 6, 'Repair “glass was broken” so “was” is PASS heading an upper VP over “[VP [V broken]]”.',
    p('S', [p('NP', [p('N', [w('glass')])]), p('VP', [p('PROG', [w('was')]), p('VP', [p('V', [w('broken')])])])]),
    p('S', [p('NP', [p('N', [w('glass')])]), p('VP', [p('PASS', [w('was')]), p('VP', [p('V', [w('broken')])])])]),
    '“broken” is a passive participle, so auxiliary “was” is PASS rather than PROG.',
    '[S [NP [N glass]] [VP [PASS was] [VP [V broken]]]]'
  ),
  mkSyntaxFix(6, '4', 'chain', 6, 'Repair “Kim has been reading” so PERF “has” dominates the VP headed by PROG “been”.',
    p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('PROG', [w('has')]), p('VP', [p('PERF', [w('been')]), p('VP', [p('V', [w('reading')])])])])]),
    p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('PERF', [w('has')]), p('VP', [p('PROG', [w('been')]), p('VP', [p('V', [w('reading')])])])])]),
    'Perfect PERF precedes Progressive PROG in the English auxiliary chain.',
    '[S [NP [name Kim]] [VP [PERF has] [VP [PROG been] [VP [V reading]]]]]'
  ),
  mkSyntaxFix(6, '5', 'questions', 6, 'Repair “Will Ada rest?” so fronted auxiliary MOD “Will” attaches under C in S-bar above S.',
    p('S', [p('MOD', [w('Will')]), p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('rest')])])]),
    p('S-bar', [p('C', [w('Will')]), p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('rest')])])])]),
    'Subject-auxiliary inversion moves the first auxiliary into complementiser C under S-bar.',
    '[S-bar [C Will] [S [NP [name Ada]] [VP [V rest]]]]'
  ),

  mkRecon(6, '1', 'chain', ['reading', 'may', 'been', 'have', 'she'], ['she may have been reading'], 'Auxiliary verbs follow fixed order MOD -> PERF -> PROG -> V.'),
  mkRecon(6, '2', 'negation', ['arrived', 'not', 'Kim', 'has'], ['Kim has not arrived'], 'Sentential “not” follows the first tensed auxiliary “has”.'),
  mkRecon(6, '3', 'questions', ['leaving', 'Sam', 'now', 'is'], ['is Sam leaving now'], 'Auxiliary “is” precedes Subject in a yes/no question.'),
  mkRecon(6, '4', 'passive', ['painted', 'already', 'was', 'door', 'green'], ['green door was already painted', 'already green door was painted'], 'Passive auxiliary precedes adverbial and passive participle.'),
  mkRecon(6, '5', 'adverbials', ['never', 'have', 'seen', 'Rome', 'they'], ['they have never seen Rome'], 'Adverbial “never” sits comfortably after the first auxiliary.'),

  mkTreeBuild(6, '1', 'concepts', 6, 'Build a Ch. 6 tree for “Kim may leave” using S, NP, VP, MOD, and V.',
    p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('MOD', [w('may')]), p('VP', [p('V', [w('leave')])])])]),
    'MOD “may” heads a higher VP over the lexical VP “[VP [V leave]]”.',
    '[S [NP [name Kim]] [VP [MOD may] [VP [V leave]]]]'
  ),
  mkTreeBuild(6, '2', 'chain', 6, 'Build a Ch. 6 tree for “Ada has arrived” using PERF over the lexical VP.',
    p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('PERF', [w('has')]), p('VP', [p('V', [w('arrived')])])])]),
    'Perfect auxiliary PERF “has” heads an auxiliary VP containing “[VP [V arrived]]”.',
    '[S [NP [name Ada]] [VP [PERF has] [VP [V arrived]]]]'
  ),
  mkTreeBuild(6, '3', 'passive', 6, 'Build a Ch. 6 tree for “Leo was seen” using PASS over the lexical VP.',
    p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('PASS', [w('was')]), p('VP', [p('V', [w('seen')])])])]),
    'Passive auxiliary PASS “was” takes lexical passive “[VP [V seen]]”.',
    '[S [NP [name Leo]] [VP [PASS was] [VP [V seen]]]]'
  ),
  mkTreeBuild(6, '4', 'chain', 6, 'Build a Ch. 6 tree for “he has been singing” stacking PERF and PROG over VP.',
    p('S', [p('NP', [p('pronoun', [w('he')])]), p('VP', [p('PERF', [w('has')]), p('VP', [p('PROG', [w('been')]), p('VP', [p('V', [w('singing')])])])])]),
    'PERF dominates a VP headed by PROG, which in turn dominates lexical VP.',
    '[S [NP [pronoun he]] [VP [PERF has] [VP [PROG been] [VP [V singing]]]]]'
  ),
  mkTreeBuild(6, '5', 'questions', 6, 'Build a Ch. 6 tree for “Can Sam swim” using S-bar, C, S, NP, and VP.',
    p('S-bar', [p('C', [w('Can')]), p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('swim')])])])]),
    'Inverted auxiliary “Can” occupies C under S-bar above S.',
    '[S-bar [C Can] [S [NP [name Sam]] [VP [V swim]]]]'
  ),

  // Chapter 7: The structure of Noun Phrases (V7-CORE)
  mkBlank(7, '1', 'concepts', 'Inside a Burton-Roberts Chapter 7 NP, a determiner combines with an intermediate nominal constituent labelled _____.', ['NOM'], 'Chapter 7 splits NP into DET and NOM (with modifiers attaching to NOM).'),
  mkBlank(7, '2', 'worked-example', 'Articles such as “the” and “a” sit under category _____ inside DET.', ['ART'], 'Articles take category ART dominated by DET.'),
  mkBlank(7, '3', 'pre-modifiers', 'Demonstratives like “that” and “this” occupy category _____ inside DET.', ['DEM'], 'Demonstratives belong to DEM under DET.'),
  mkBlank(7, '4', 'application', 'An adjective modifying an indefinite pronoun like “something” must follow it, as in “something _____”.', ['fragile', 'new', 'cold', 'useful'], 'Unlike ordinary pre-nominal adjectives, APs modifying “something/anyone” follow the pronoun.'),
  mkBlank(7, '5', 'post-modifiers', 'Post-modifying PPs inside an NP attach as sisters to _____ inside a higher NOM.', ['NOM'], 'Both pre- and post-modifiers in an NP attach to a lower NOM inside a higher NOM.'),

  mkSyntaxFix(7, '1', 'worked-example', 7, 'Repair “the bird” so NP splits cleanly into “[DET [ART the]]” and “[NOM [N bird]]”.',
    p('NP', [p('ART', [w('the')]), p('N', [w('bird')])]),
    p('NP', [p('DET', [p('ART', [w('the')])]), p('NOM', [p('N', [w('bird')])])]),
    'In Ch. 7, NP immediately dominates DET and NOM; DET dominates ART and NOM dominates N.',
    '[NP [DET [ART the]] [NOM [N bird]]]'
  ),
  mkSyntaxFix(7, '2', 'pre-modifiers', 7, 'Repair “that old key” so “old” modifies NOM inside a higher NOM rather than sitting inside DET.',
    p('NP', [p('DET', [p('DEM', [w('that')]), p('AP', [p('A', [w('old')])])]), p('NOM', [p('N', [w('key')])])]),
    p('NP', [p('DET', [p('DEM', [w('that')])]), p('NOM', [p('AP', [p('A', [w('old')])]), p('NOM', [p('N', [w('key')])])])]),
    'Pre-modifying AP attaches inside NOM -> AP + NOM, leaving only DEM inside DET.',
    '[NP [DET [DEM that]] [NOM [AP [A old]] [NOM [N key]]]]'
  ),
  mkSyntaxFix(7, '3', 'post-modifiers', 7, 'Repair “the map of Rome” so PP post-modifier “of Rome” attaches to “[NOM [N map]]” under higher NOM.',
    p('NP', [p('DET', [p('ART', [w('the')])]), p('NOM', [p('N', [w('map')])]), p('PP', [p('P', [w('of')]), p('NP', [p('NOM', [p('name', [w('Rome')])])])])]),
    p('NP', [p('DET', [p('ART', [w('the')])]), p('NOM', [p('NOM', [p('N', [w('map')])]), p('PP', [p('P', [w('of')]), p('NP', [p('NOM', [p('name', [w('Rome')])])])])])]),
    'PP post-modifier attaches to lower NOM inside higher NOM, not directly under NP.',
    '[NP [DET [ART the]] [NOM [NOM [N map]] [PP [P of] [NP [NOM [name Rome]]]]]]',
    [p('NP', [p('DET', [p('ART', [w('the')])]), p('NOM', [p('NOM', [p('N', [w('map')])]), p('PP', [p('P', [w('of')]), p('NP', [p('name', [w('Rome')])])])])])]
  ),
  mkSyntaxFix(7, '4', 'pre-modifiers', 7, 'Repair “all the books” so “all” sits under PRE-DET before “[DET [ART the]]” inside NP.',
    p('NP', [p('DET', [p('Q', [w('all')]), p('ART', [w('the')])]), p('NOM', [p('N', [w('books')])])]),
    p('NP', [p('PRE-DET', [w('all')]), p('DET', [p('ART', [w('the')])]), p('NOM', [p('N', [w('books')])])]),
    'Pre-determiner “all” attaches directly under NP before DET + NOM.',
    '[NP [PRE-DET all] [DET [ART the]] [NOM [N books]]]'
  ),
  mkSyntaxFix(7, '5', 'concepts', 7, 'Repair “some fresh bread” so quantifier “some” is Q under DET and “fresh” modifies NOM.',
    p('NP', [p('DET', [p('ART', [w('some')])]), p('NOM', [p('AP', [p('A', [w('fresh')])]), p('N', [w('bread')])])]),
    p('NP', [p('DET', [p('Q', [w('some')])]), p('NOM', [p('AP', [p('A', [w('fresh')])]), p('NOM', [p('N', [w('bread')])])])]),
    '“some” is a quantifier Q (under DET), and “fresh” attaches to inner NOM “[NOM [N bread]]”.',
    '[NP [DET [Q some]] [NOM [AP [A fresh]] [NOM [N bread]]]]'
  ),

  mkRecon(7, '1', 'pre-modifiers', ['books', 'the', 'two', 'tall'], ['the two tall books'], 'Order determiner/article before numeral/QA and pre-modifying adjective before noun.'),
  mkRecon(7, '2', 'pre-modifiers', ['students', 'all', 'the', 'young'], ['all the young students'], 'Pre-determiner “all” precedes article “the”, adjective, and head noun.'),
  mkRecon(7, '3', 'application', ['fragile', 'carrying', 'was', 'Kim', 'something'], ['Kim was carrying something fragile'], 'Adjective modifying indefinite pronoun “something” follows it.'),
  mkRecon(7, '4', 'post-modifiers', ['the', 'table', 'vase', 'on', 'the'], ['the vase on the table'], 'Head nominal precedes post-modifying prepositional phrase.'),
  mkRecon(7, '5', 'concepts', ['every', 'quiet', 'garden', 'in', 'Rome'], ['every quiet garden in Rome'], 'Determiner precedes adjective + noun + post-modifying PP.'),

  mkTreeBuild(7, '1', 'worked-example', 7, 'Build a Ch. 7 NP tree for “the bird” using NP, DET, ART, NOM, and N.',
    p('NP', [p('DET', [p('ART', [w('the')])]), p('NOM', [p('N', [w('bird')])])]),
    'DET dominates ART “the”; NOM dominates head N “bird”.',
    '[NP [DET [ART the]] [NOM [N bird]]]'
  ),
  mkTreeBuild(7, '2', 'pre-modifiers', 7, 'Build a Ch. 7 NP tree for “that warm coat” using DEM, DET, NOM, AP, A, and N.',
    p('NP', [p('DET', [p('DEM', [w('that')])]), p('NOM', [p('AP', [p('A', [w('warm')])]), p('NOM', [p('N', [w('coat')])])])]),
    'DEM “that” sits in DET; AP “warm” attaches to “[NOM [N coat]]” inside NOM.',
    '[NP [DET [DEM that]] [NOM [AP [A warm]] [NOM [N coat]]]]'
  ),
  mkTreeBuild(7, '3', 'concepts', 7, 'Build a Ch. 7 NP tree for “every clock” using NP, DET, Q, NOM, and N.',
    p('NP', [p('DET', [p('Q', [w('every')])]), p('NOM', [p('N', [w('clock')])])]),
    'Quantifier “every” takes category Q under DET; “clock” sits in NOM.',
    '[NP [DET [Q every]] [NOM [N clock]]]'
  ),
  mkTreeBuild(7, '4', 'post-modifiers', 7, 'Build a Ch. 7 NP tree for “a house in York” attaching PP to inner NOM.',
    p('NP', [p('DET', [p('ART', [w('a')])]), p('NOM', [p('NOM', [p('N', [w('house')])]), p('PP', [p('P', [w('in')]), p('NP', [p('name', [w('York')])])])])]),
    'Post-modifier PP attaches to “[NOM [N house]]” inside higher NOM.',
    '[NP [DET [ART a]] [NOM [NOM [N house]] [PP [P in] [NP [name York]]]]]',
    [p('NP', [p('DET', [p('ART', [w('a')])]), p('NOM', [p('NOM', [p('N', [w('house')])]), p('PP', [p('P', [w('in')]), p('NP', [p('NOM', [p('name', [w('York')])])])])])])]
  ),
  mkTreeBuild(7, '5', 'pre-modifiers', 7, 'Build a Ch. 7 NP tree for “my friend” using POSS under DET and N under NOM.',
    p('NP', [p('DET', [p('POSS', [w('my')])]), p('NOM', [p('N', [w('friend')])])]),
    'Possessive determiner “my” is POSS inside DET; “friend” is N inside NOM.',
    '[NP [DET [POSS my]] [NOM [N friend]]]'
  ),

  // Chapter 8: Sentences within sentences (V8)
  mkBlank(8, '1', 'concepts', 'A subordinate clause introduced by “that” or “whether” sits directly under node _____.', ['S-bar'], 'Subordinate clauses with a complementiser position C project to S-bar (S-bar -> C + S).'),
  mkBlank(8, '2', 'worked-example', 'In “[S-bar [C that] [S ...]]”, “that” is a _____ introducing the embedded clause.', ['complementiser', 'complementizer', 'C'], 'Subordinators like “that”, “whether”, and “if” occupy complementiser C.'),
  mkBlank(8, '3', 'clausal-subjects-and-objects', 'When a clausal subject like “That Mira won” moves to the end leaving dummy “It” in front, the construction is called _____.', ['extraposition'], 'Extraposition places a clausal subject after the matrix VP with expletive “It” in Subject position.'),
  mkBlank(8, '4', 'clausal-complements', 'A that-clause completing a noun such as “the claim that Kim left” is a noun _____.', ['complement', 'NOM complement'], 'Unlike a relative clause modifier, “the claim that Kim left” has a complete embedded clause functioning as complement to the noun.'),
  mkBlank(8, '5', 'adverbial-clauses', 'An adverbial clause introduced by “because” or “although” is dominated by _____ functioning as adjunct.', ['S-bar'], 'Adverbial subordinate clauses are S-bars headed by subordinating complementisers C attaching as adjuncts.'),

  mkSyntaxFix(8, '1', 'worked-example', 8, 'Repair “Sam knew that Leo left” so “that Leo left” is wrapped under S-bar -> C + S inside matrix VP.',
    p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('knew')]), p('S', [p('C', [w('that')]), p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('left')])])])])]),
    p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('knew')]), p('S-bar', [p('C', [w('that')]), p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('left')])])])])])]),
    'A subordinate clause introduced by complementiser C dominates S inside S-bar.',
    '[S [NP [name Sam]] [VP [V knew] [S-bar [C that] [S [NP [name Leo]] [VP [V left]]]]]]'
  ),
  mkSyntaxFix(8, '2', 'clausal-subjects-and-objects', 8, 'Repair “That Ada won pleased Sam” so the clausal subject S-bar sits directly under matrix S before VP.',
    p('S', [p('NP', [p('S-bar', [p('C', [w('That')]), p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('won')])])])])]), p('VP', [p('V', [w('pleased')]), p('NP', [p('name', [w('Sam')])])])]),
    p('S', [p('S-bar', [p('C', [w('That')]), p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('won')])])])]), p('VP', [p('V', [w('pleased')]), p('NP', [p('name', [w('Sam')])])])]),
    'Wait — check whether subject clause is directly S-bar under S or NP: in Ch. 8 worked examples, a clausal subject S-bar replaces NP directly under S unless extraposed.',
    '[S [S-bar [C That] [S [NP [name Ada]] [VP [V won]]]] [VP [V pleased] [NP [name Sam]]]]'
  ),
  mkSyntaxFix(8, '3', 'adverbial-clauses', 8, 'Repair “Mira left because it rained” so the adverbial S-bar attaches to a lower VP inside upper VP.',
    p('S', [p('NP', [p('name', [w('Mira')])]), p('VP', [p('V', [w('left')]), p('S-bar', [p('C', [w('because')]), p('S', [p('NP', [p('pronoun', [w('it')])]), p('VP', [p('V', [w('rained')])])])])])]),
    p('S', [p('NP', [p('name', [w('Mira')])]), p('VP', [p('VP', [p('V', [w('left')])]), p('S-bar', [p('C', [w('because')]), p('S', [p('NP', [p('pronoun', [w('it')])]), p('VP', [p('V', [w('rained')])])])])])]),
    '“because it rained” is an optional adverbial clause attaching to lower VP -> [VP [VP ...] [S-bar ...]].',
    '[S [NP [name Mira]] [VP [VP [V left]] [S-bar [C because] [S [NP [pronoun it]] [VP [V rained]]]]]]'
  ),
  mkSyntaxFix(8, '4', 'clausal-complements', 8, 'Repair “Kim asked whether Sam arrived” so “whether” occupies C inside S-bar.',
    p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('asked')]), p('S-bar', [p('S', [p('P', [w('whether')]), p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('arrived')])])])])])]),
    p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('asked')]), p('S-bar', [p('C', [w('whether')]), p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('arrived')])])])])])]),
    'Subordinator “whether” sits under complementiser C inside S-bar.',
    '[S [NP [name Kim]] [VP [V asked] [S-bar [C whether] [S [NP [name Sam]] [VP [V arrived]]]]]]'
  ),
  mkSyntaxFix(8, '5', 'worked-example', 8, 'Repair “Inez hoped Leo smiled” so the embedded clause sits inside S-bar (even with overt C covert/absent) inside VP.',
    p('S', [p('NP', [p('name', [w('Inez')])]), p('VP', [p('V', [w('hoped')]), p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('smiled')])])])]),
    p('S', [p('NP', [p('name', [w('Inez')])]), p('VP', [p('V', [w('hoped')]), p('S-bar', [p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('smiled')])])])])])]),
    'Clausal complement “Leo smiled” forms an embedded clause inside S-bar under V “hoped”.',
    '[S [NP [name Inez]] [VP [V hoped] [S-bar [S [NP [name Leo]] [VP [V smiled]]]]]]',
    [p('S', [p('NP', [p('name', [w('Inez')])]), p('VP', [p('V', [w('hoped')]), p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('smiled')])])])])])]
  ),

  mkRecon(8, '1', 'worked-example', ['left', 'Sam', 'that', 'Kim', 'said'], ['Kim said that Sam left', 'Sam said that Kim left'], 'Matrix verb takes embedded S-bar headed by complementiser “that”.'),
  mkRecon(8, '2', 'clausal-subjects-and-objects', ['surprised', 'us', 'won', 'she', 'that'], ['that she won surprised us'], 'Place clausal subject before matrix VP.'),
  mkRecon(8, '3', 'clausal-subjects-and-objects', ['clear', 'it', 'rained', 'is', 'that', 'it'], ['it is clear that it rained'], 'Extraposed structure uses dummy subject “it” followed by predicate and clausal S-bar.'),
  mkRecon(8, '4', 'adverbial-clauses', ['rained', 'left', 'because', 'they', 'it'], ['they left because it rained', 'because it rained they left'], 'Adverbial S-bar attaches either after or before matrix clause.'),
  mkRecon(8, '5', 'clausal-complements', ['wondered', 'she', 'agreed', 'whether', 'Leo'], ['she wondered whether Leo agreed'], 'Embedded interrogative “whether Leo agreed” acts as complement of “wondered”.'),

  mkTreeBuild(8, '1', 'worked-example', 8, 'Build a Ch. 8 tree for “Sam knew that Leo slept” using S-bar -> C + S.',
    p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('knew')]), p('S-bar', [p('C', [w('that')]), p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('slept')])])])])])]),
    'Embedded clause “that Leo slept” is an S-bar complement of V “knew”.',
    '[S [NP [name Sam]] [VP [V knew] [S-bar [C that] [S [NP [name Leo]] [VP [V slept]]]]]]'
  ),
  mkTreeBuild(8, '2', 'clausal-complements', 8, 'Build a Ch. 8 tree for “Kim asked whether Ada left” using S-bar and C.',
    p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('asked')]), p('S-bar', [p('C', [w('whether')]), p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('left')])])])])])]),
    '“whether” fills C inside complement S-bar of “asked”.',
    '[S [NP [name Kim]] [VP [V asked] [S-bar [C whether] [S [NP [name Ada]] [VP [V left]]]]]]'
  ),
  mkTreeBuild(8, '3', 'adverbial-clauses', 8, 'Build a Ch. 8 tree for “Leo smiled because Mira arrived” attaching adverbial S-bar to lower VP.',
    p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('VP', [p('V', [w('smiled')])]), p('S-bar', [p('C', [w('because')]), p('S', [p('NP', [p('name', [w('Mira')])]), p('VP', [p('V', [w('arrived')])])])])])]),
    'Adverbial clause “because Mira arrived” is S-bar sister to inner VP “[VP [V smiled]]”.',
    '[S [NP [name Leo]] [VP [VP [V smiled]] [S-bar [C because] [S [NP [name Mira]] [VP [V arrived]]]]]]'
  ),
  mkTreeBuild(8, '4', 'worked-example', 8, 'Build a Ch. 8 tree for “they think that Sam stayed” using S-bar -> C + S.',
    p('S', [p('NP', [p('pronoun', [w('they')])]), p('VP', [p('V', [w('think')]), p('S-bar', [p('C', [w('that')]), p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('stayed')])])])])])]),
    'Embedded S-bar fills object complement of “think”.',
    '[S [NP [pronoun they]] [VP [V think] [S-bar [C that] [S [NP [name Sam]] [VP [V stayed]]]]]]'
  ),
  mkTreeBuild(8, '5', 'clausal-complements', 8, 'Build a Ch. 8 tree for “she knows if he fell” using C “if” under S-bar.',
    p('S', [p('NP', [p('pronoun', [w('she')])]), p('VP', [p('V', [w('knows')]), p('S-bar', [p('C', [w('if')]), p('S', [p('NP', [p('pronoun', [w('he')])]), p('VP', [p('V', [w('fell')])])])])])]),
    'Subordinator “if” sits in C heading S-bar.',
    '[S [NP [pronoun she]] [VP [V knows] [S-bar [C if] [S [NP [pronoun he]] [VP [V fell]]]]]]'
  ),

  // Chapter 9: Wh-clauses (V9)
  mkBlank(9, '1', 'concepts', 'In Burton-Roberts Chapter 9, a fronted wh-phrase moves to the higher _____ node above S-bar.', ['S-dbar', 'S double-bar', 'S″'], 'Fronted wh-expressions occupy specifier of S-dbar (sister to S-bar), while fronted auxiliaries occupy C2 under S-bar.'),
  mkBlank(9, '2', 'worked-example', 'The vacant object position left behind after wh-fronting is represented by a co-indexed _____.', ['gap', 'trace'], 'A co-indexed gap marks the canonical position from which the wh-constituent moved.'),
  mkBlank(9, '3', 'embedded-interrogatives', 'Unlike main wh-questions, embedded wh-interrogatives do NOT trigger subject-auxiliary _____.', ['inversion'], 'Embedded interrogatives (“I wonder what Kim bought”) lack C2 auxiliary inversion.'),
  mkBlank(9, '4', 'relatives-and-complements', 'A restrictive relative clause attaches inside an NP as a sister to _____ inside a higher NOM.', ['NOM'], 'Relative clauses modify NOM (NOM -> NOM + S-bar/S-dbar), whereas noun complements are sisters to N.'),
  mkBlank(9, '5', 'relative-scope', 'In “the friend who Kim saw”, the wh-pronoun “who” represents the _____ object of “saw”.', ['direct', 'direct object'], '“who” fronts from the object gap position inside “[VP [V saw] [NP gap]]”.'),

  mkSyntaxFix(9, '1', 'worked-example', 9, 'Repair the main wh-question “Who did Sam see?” so “Who” sits under S-dbar and inverted auxiliary “did” occupies C2 inside S-bar.',
    p('S-bar', [p('C2', [w('Who')]), p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('did')]), p('V', [w('see')])])])]),
    p('S-dbar', [p('NP', [p('pronoun', [w('Who')])]), p('S-bar', [p('C2', [w('did')]), p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('see')])])])])]),
    'Fronted wh-phrase NP occupies specifier of S-dbar; inverted auxiliary “did” occupies C2 under S-bar.',
    '[S-dbar [NP [pronoun Who]] [S-bar [C2 did] [S [NP [name Sam]] [VP [V see]]]]]'
  ),
  mkSyntaxFix(9, '2', 'embedded-interrogatives', 9, 'Repair “Mira asked what Kim saw” so the embedded wh-clause is an S-dbar without subject-auxiliary inversion.',
    p('S', [p('NP', [p('name', [w('Mira')])]), p('VP', [p('V', [w('asked')]), p('S-bar', [p('C2', [w('what')]), p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('saw')])])])])])]),
    p('S', [p('NP', [p('name', [w('Mira')])]), p('VP', [p('V', [w('asked')]), p('S-dbar', [p('NP', [p('pronoun', [w('what')])]), p('S-bar', [p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('saw')])])])])])])]),
    'Wh-word “what” moves to S-dbar (not C2); in embedded interrogatives C2 stays empty.',
    '[S [NP [name Mira]] [VP [V asked] [S-dbar [NP [pronoun what]] [S-bar [S [NP [name Kim]] [VP [V saw]]]]]]]',
    [p('S', [p('NP', [p('name', [w('Mira')])]), p('VP', [p('V', [w('asked')]), p('S-dbar', [p('NP', [p('pronoun', [w('what')])]), p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('saw')])])])])])])]
  ),
  mkSyntaxFix(9, '3', 'concepts', 9, 'Repair “What can Ada read?” so modal auxiliary “can” moves into C2 under S-bar rather than staying inside VP.',
    p('S-dbar', [p('NP', [p('pronoun', [w('What')])]), p('S-bar', [p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('MOD', [w('can')]), p('VP', [p('V', [w('read')])])])])])]),
    p('S-dbar', [p('NP', [p('pronoun', [w('What')])]), p('S-bar', [p('C2', [w('can')]), p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('read')])])])])]),
    'Main wh-questions undergo subject-auxiliary inversion placing auxiliary “can” in C2.',
    '[S-dbar [NP [pronoun What]] [S-bar [C2 can] [S [NP [name Ada]] [VP [V read]]]]]'
  ),
  mkSyntaxFix(9, '4', 'relatives-and-complements', 9, 'Repair “the man who smiled” so relative clause S-bar modifies NOM inside higher NOM.',
    p('NP', [p('DET', [p('ART', [w('the')])]), p('NOM', [p('N', [w('man')])]), p('S-bar', [p('NP', [p('pronoun', [w('who')])]), p('S', [p('VP', [p('V', [w('smiled')])])])])]),
    p('NP', [p('DET', [p('ART', [w('the')])]), p('NOM', [p('NOM', [p('N', [w('man')])]), p('S-dbar', [p('NP', [p('pronoun', [w('who')])]), p('S-bar', [p('S', [p('VP', [p('V', [w('smiled')])])])])])])]),
    'A relative clause modifies an inner NOM inside a higher NOM, never attaching directly to DET.',
    '[NP [DET [ART the]] [NOM [NOM [N man]] [S-dbar [NP [pronoun who]] [S-bar [S [VP [V smiled]]]]]]]',
    [p('NP', [p('DET', [p('ART', [w('the')])]), p('NOM', [p('NOM', [p('N', [w('man')])]), p('S-bar', [p('NP', [p('pronoun', [w('who')])]), p('S', [p('VP', [p('V', [w('smiled')])])])])])])]
  ),
  mkSyntaxFix(9, '5', 'worked-example', 9, 'Repair “Which song will Kim sing?” so “Which song” forms an NP under S-dbar above C2 “will”.',
    p('S-dbar', [p('DET', [p('Q', [w('Which')])]), p('S-bar', [p('C2', [w('will')]), p('S', [p('NP', [p('N', [w('song')]), p('NP', [p('name', [w('Kim')])])]), p('VP', [p('V', [w('sing')])])])])]),
    p('S-dbar', [p('NP', [p('DET', [p('Q', [w('Which')])]), p('NOM', [p('N', [w('song')])])]), p('S-bar', [p('C2', [w('will')]), p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('sing')])])])])]),
    'The entire wh-phrase “[NP [DET [Q Which]] [NOM [N song]]]” fronts together to S-dbar.',
    '[S-dbar [NP [DET [Q Which]] [NOM [N song]]] [S-bar [C2 will] [S [NP [name Kim]] [VP [V sing]]]]]'
  ),

  mkRecon(9, '1', 'worked-example', ['read', 'what', 'did', 'Leo'], ['what did Leo read'], 'Fronted wh-word precedes inverted auxiliary “did”, Subject, and main verb.'),
  mkRecon(9, '2', 'embedded-interrogatives', ['wondered', 'Sam', 'what', 'bought', 'Ada'], ['Sam wondered what Ada bought', 'Ada wondered what Sam bought'], 'Embedded wh-clauses keep Subject before verb without auxiliary inversion.'),
  mkRecon(9, '3', 'concepts', ['meet', 'will', 'who', 'Mira'], ['who will Mira meet'], 'Wh-word precedes inverted modal, Subject, and base verb.'),
  mkRecon(9, '4', 'relatives-and-complements', ['who', 'arrived', 'late', 'friend', 'the'], ['the friend who arrived late'], 'Relative clause follows head nominal inside NP.'),
  mkRecon(9, '5', 'embedded-interrogatives', ['knew', 'where', 'they', 'stopped', 'Kim'], ['Kim knew where they stopped'], 'Wh-adjunct “where” introduces embedded clause without inversion.'),

  mkTreeBuild(9, '1', 'worked-example', 9, 'Build a Ch. 9 main wh-question tree for “Who did Leo meet” using S-dbar, S-bar, C2, and S.',
    p('S-dbar', [p('NP', [p('pronoun', [w('Who')])]), p('S-bar', [p('C2', [w('did')]), p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('meet')])])])])]),
    '“Who” fronts to S-dbar while inverted “did” sits in C2 under S-bar.',
    '[S-dbar [NP [pronoun Who]] [S-bar [C2 did] [S [NP [name Leo]] [VP [V meet]]]]]'
  ),
  mkTreeBuild(9, '2', 'concepts', 9, 'Build a Ch. 9 tree for “What can Kim see” using S-dbar, NP, pronoun, S-bar, C2, S, VP, and V.',
    p('S-dbar', [p('NP', [p('pronoun', [w('What')])]), p('S-bar', [p('C2', [w('can')]), p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('see')])])])])]),
    '“What” sits under S-dbar and inverted modal “can” sits under C2 inside S-bar.',
    '[S-dbar [NP [pronoun What]] [S-bar [C2 can] [S [NP [name Kim]] [VP [V see]]]]]'
  ),
  mkTreeBuild(9, '3', 'embedded-interrogatives', 9, 'Build a Ch. 9 tree for “Sam asked what Ada found” using embedded S-dbar -> NP + S-bar.',
    p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('asked')]), p('S-dbar', [p('NP', [p('pronoun', [w('what')])]), p('S-bar', [p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('found')])])])])])])]),
    'Matrix verb “asked” takes an embedded S-dbar without C2 inversion.',
    '[S [NP [name Sam]] [VP [V asked] [S-dbar [NP [pronoun what]] [S-bar [S [NP [name Ada]] [VP [V found]]]]]]]',
    [p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('asked')]), p('S-dbar', [p('NP', [p('pronoun', [w('what')])]), p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('found')])])])])])])]
  ),
  mkTreeBuild(9, '4', 'worked-example', 9, 'Build a Ch. 9 tree for “When will Ada arrive” placing AdvP “When” in S-dbar and “will” in C2.',
    p('S-dbar', [p('AdvP', [p('Adv', [w('When')])]), p('S-bar', [p('C2', [w('will')]), p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('arrive')])])])])]),
    'Wh-adverbial “When” moves to S-dbar; “will” occupies C2.',
    '[S-dbar [AdvP [Adv When]] [S-bar [C2 will] [S [NP [name Ada]] [VP [V arrive]]]]]'
  ),
  mkTreeBuild(9, '5', 'relatives-and-complements', 9, 'Build a Ch. 9 tree for “Inez read the book that Mira wrote” or simpler NP “the book that Mira wrote” with relative S-dbar under NOM.',
    p('NP', [p('DET', [p('ART', [w('the')])]), p('NOM', [p('NOM', [p('N', [w('book')])]), p('S-dbar', [p('S-bar', [p('C1', [w('that')]), p('S', [p('NP', [p('name', [w('Mira')])]), p('VP', [p('V', [w('wrote')])])])])])])]),
    'Relative clause attaches inside NOM alongside lower NOM “[NOM [N book]]”.',
    '[NP [DET [ART the]] [NOM [NOM [N book]] [S-dbar [S-bar [C1 that] [S [NP [name Mira]] [VP [V wrote]]]]]]]',
    [p('NP', [p('DET', [p('ART', [w('the')])]), p('NOM', [p('NOM', [p('N', [w('book')])]), p('S-bar', [p('C1', [w('that')]), p('S', [p('NP', [p('name', [w('Mira')])]), p('VP', [p('V', [w('wrote')])])])])])])]
  ),

  // Chapter 10: Non-finite clauses (V10)
  mkBlank(10, '1', 'concepts', 'Non-finite verbs lack grammatical _____ (present or past).', ['tense'], 'Non-finite clauses are untensed ([-tense]), lacking finite tense distinctions.'),
  mkBlank(10, '2', 'worked-example', 'Infinitival marker “to” behaves like a [-tense] _____ heading a VP over a base verb rather than a preposition.', ['auxiliary', 'AUX'], 'Unlike preposition “to” (followed by NP), infinitival “to” sits under AUX [-tense] followed by VP.'),
  mkBlank(10, '3', 'subjects-and-control', 'In “Kim tried to leave”, the covert subject of “to leave” is _____ by “Kim”.', ['controlled'], 'In control constructions, an argument of the matrix clause determines the covert subject of the infinitival.'),
  mkBlank(10, '4', 'subjects-and-control', 'An overt subject inside a non-finite to-infinitival clause is introduced by complementiser _____.', ['for'], 'Complementiser “for” licenses an overt NP subject in a non-finite to-clause (“for Kim to leave”).'),
  mkBlank(10, '5', 'verb-complements', 'A non-finite verb ending in -ing or -en/-ed used without auxiliaries heads a _____ VP inside S-bar.', ['non-finite', 'participial'], 'Participial and bare infinitival clauses are non-finite clauses without tensed auxiliaries.'),

  mkSyntaxFix(10, '1', 'worked-example', 10, 'Repair “to rest” so “to” sits under AUX (not preposition P) heading a VP over “[VP [V rest]]”.',
    p('PP', [p('P', [w('to')]), p('NP', [p('NOM', [p('N', [w('rest')])])])]),
    p('VP', [p('AUX', [w('to')], { features: ['-tense'] }), p('VP', [p('V', [w('rest')])])]),
    'Infinitival “to” is [-tense] AUX taking a bare VP complement, not a PP.',
    '[VP [AUX to [-tense]] [VP [V rest]]]',
    [p('VP', [p('AUX', [w('to')]), p('VP', [p('V', [w('rest')])])])]
  ),
  mkSyntaxFix(10, '2', 'verb-complements', 10, 'Repair “Sam wants to leave” so “to leave” is a non-finite clause S-bar with VP -> AUX “to” + VP.',
    p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('wants')]), p('PP', [p('P', [w('to')]), p('VP', [p('V', [w('leave')])])])])]),
    p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('wants')]), p('S-bar', [p('S', [p('VP', [p('AUX', [w('to')]), p('VP', [p('V', [w('leave')])])])])])])]),
    'Embedded infinitival clause projects S-bar -> S -> VP [AUX to] + VP.',
    '[S [NP [name Sam]] [VP [V wants] [S-bar [S [VP [AUX to] [VP [V leave]]]]]]]',
    [p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('wants')]), p('S-bar', [p('S', [p('VP', [p('AUX', [w('to')], { features: ['-tense'] }), p('VP', [p('V', [w('leave')])])])])])])])]
  ),
  mkSyntaxFix(10, '3', 'subjects-and-control', 10, 'Repair “for Ada to win” so “for” is complementiser C inside S-bar over Subject NP “Ada” + VP.',
    p('PP', [p('P', [w('for')]), p('NP', [p('name', [w('Ada')])]), p('VP', [p('AUX', [w('to')]), p('VP', [p('V', [w('win')])])])]),
    p('S-bar', [p('C', [w('for')]), p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('AUX', [w('to')]), p('VP', [p('V', [w('win')])])])])]),
    '“for” introduces a non-finite subject inside S-bar -> C + S.',
    '[S-bar [C for] [S [NP [name Ada]] [VP [AUX to] [VP [V win]]]]]'
  ),
  mkSyntaxFix(10, '4', 'clause-functions', 10, 'Repair “Kim expects Leo to stay” so “Leo to stay” forms an embedded S-bar complement of “expects”.',
    p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('expects')]), p('NP', [p('name', [w('Leo')])]), p('PP', [p('P', [w('to')]), p('VP', [p('V', [w('stay')])])])])]),
    p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('expects')]), p('S-bar', [p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('AUX', [w('to')]), p('VP', [p('V', [w('stay')])])])])])])]),
    'Wait: verb “expects” takes the entire non-finite clause “Leo to stay” as S-bar (or NP + VP complement).',
    '[S [NP [name Kim]] [VP [V expects] [S-bar [S [NP [name Leo]] [VP [AUX to] [VP [V stay]]]]]]]',
    [p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('expects')]), p('NP', [p('name', [w('Leo')])]), p('S-bar', [p('S', [p('VP', [p('AUX', [w('to')]), p('VP', [p('V', [w('stay')])])])])])])])]
  ),
  mkSyntaxFix(10, '5', 'worked-example', 10, 'Repair “they refused to go” so “to” attaches under AUX above VP “[VP [V go]]”.',
    p('S', [p('NP', [p('pronoun', [w('they')])]), p('VP', [p('V', [w('refused')]), p('VP', [p('V', [w('to')]), p('V', [w('go')])])])]),
    p('S', [p('NP', [p('pronoun', [w('they')])]), p('VP', [p('V', [w('refused')]), p('S-bar', [p('S', [p('VP', [p('AUX', [w('to')]), p('VP', [p('V', [w('go')])])])])])])]),
    '“to” heads AUX [-tense] inside the non-finite clause S-bar.',
    '[S [NP [pronoun they]] [VP [V refused] [S-bar [S [VP [AUX to] [VP [V go]]]]]]]'
  ),

  mkRecon(10, '1', 'subjects-and-control', ['to', 'leave', 'for', 'best', 'Kim', 'is', 'it'], ['it is best for Kim to leave'], 'Complementiser “for” introduces overt subject “Kim” before “to leave”.'),
  mkRecon(10, '2', 'worked-example', ['hoped', 'stay', 'to', 'Ada'], ['Ada hoped to stay'], 'Subject precedes control verb and to-infinitival complement.'),
  mkRecon(10, '3', 'verb-complements', ['enjoyed', 'they', 'reading', 'quietly'], ['they enjoyed quietly reading', 'they enjoyed reading quietly'], 'Gerund-participial complement follows matrix verb “enjoyed”.'),
  mkRecon(10, '4', 'subjects-and-control', ['not', 'Kim', 'promised', 'to', 'leave'], ['Kim promised not to leave'], 'Negative “not” precedes infinitival “to” in non-finite clauses.'),
  mkRecon(10, '5', 'clause-functions', ['to', 'Mira', 'tried', 'solve', 'it'], ['Mira tried to solve it'], 'Subject precedes control verb “tried” and infinitival VP complement.'),

  mkTreeBuild(10, '1', 'worked-example', 10, 'Build a Ch. 10 tree for “to sleep” using VP -> AUX “to” + VP [V sleep].',
    p('VP', [p('AUX', [w('to')]), p('VP', [p('V', [w('sleep')])])]),
    'Infinitival “to” sits under AUX [-tense] dominating “[VP [V sleep]]”.',
    '[VP [AUX to] [VP [V sleep]]]',
    [p('VP', [p('AUX', [w('to')], { features: ['-tense'] }), p('VP', [p('V', [w('sleep')])])])]
  ),
  mkTreeBuild(10, '2', 'verb-complements', 10, 'Build a Ch. 10 tree for “Kim tried to rest” with S-bar -> S -> VP [AUX to] + VP.',
    p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('tried')]), p('S-bar', [p('S', [p('VP', [p('AUX', [w('to')]), p('VP', [p('V', [w('rest')])])])])])])]),
    'Control verb “tried” takes a non-finite S-bar containing “[VP [AUX to] [VP [V rest]]]”.',
    '[S [NP [name Kim]] [VP [V tried] [S-bar [S [VP [AUX to] [VP [V rest]]]]]]]',
    [p('S', [p('NP', [p('name', [w('Kim')])]), p('VP', [p('V', [w('tried')]), p('S-bar', [p('S', [p('VP', [p('AUX', [w('to')], { features: ['-tense'] }), p('VP', [p('V', [w('rest')])])])])])])])]
  ),
  mkTreeBuild(10, '3', 'subjects-and-control', 10, 'Build a Ch. 10 tree for “for Sam to read” using S-bar -> C “for” + S.',
    p('S-bar', [p('C', [w('for')]), p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('AUX', [w('to')]), p('VP', [p('V', [w('read')])])])])]),
    'Complementiser C “for” introduces overt subject NP “Sam” inside non-finite S.',
    '[S-bar [C for] [S [NP [name Sam]] [VP [AUX to] [VP [V read]]]]]',
    [p('S-bar', [p('C', [w('for')]), p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('AUX', [w('to')], { features: ['-tense'] }), p('VP', [p('V', [w('read')])])])])])]
  ),
  mkTreeBuild(10, '4', 'clause-functions', 10, 'Build a Ch. 10 tree for “she hopes to win” using S, NP, VP, S-bar, AUX, and V.',
    p('S', [p('NP', [p('pronoun', [w('she')])]), p('VP', [p('V', [w('hopes')]), p('S-bar', [p('S', [p('VP', [p('AUX', [w('to')]), p('VP', [p('V', [w('win')])])])])])])]),
    'Infinitival clause “to win” occupies S-bar complement of “hopes”.',
    '[S [NP [pronoun she]] [VP [V hopes] [S-bar [S [VP [AUX to] [VP [V win]]]]]]]',
    [p('S', [p('NP', [p('pronoun', [w('she')])]), p('VP', [p('V', [w('hopes')]), p('S-bar', [p('S', [p('VP', [p('AUX', [w('to')], { features: ['-tense'] }), p('VP', [p('V', [w('win')])])])])])])])]
  ),
  mkTreeBuild(10, '5', 'noun-clause-functions', 10, 'Build a Ch. 10 tree for “Ada needs to go” with non-finite S-bar complement.',
    p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('needs')]), p('S-bar', [p('S', [p('VP', [p('AUX', [w('to')]), p('VP', [p('V', [w('go')])])])])])])]),
    '“needs” selects an infinitival clause S-bar with AUX [-tense] “to”.',
    '[S [NP [name Ada]] [VP [V needs] [S-bar [S [VP [AUX to] [VP [V go]]]]]]]',
    [p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('needs')]), p('S-bar', [p('S', [p('VP', [p('AUX', [w('to')], { features: ['-tense'] }), p('VP', [p('V', [w('go')])])])])])])])]
  ),

  // Chapter 11: Languages, sentences and grammars (toy phrase-structure rules S -> NP VP, S -> S and S using V4 basic categories)
  mkBlank(11, '1', 'worked-example', 'A fixed _____ of sentences cannot capture every sentence speakers can form once coordination applies freely.', ['list'], 'Finite lists cannot enumerate an unbounded language generated by a recursive rule.'),
  mkBlank(11, '2', 'apply-the-rule', 'A rule such as S → S and S is called _____ because its output category S can serve again as its input.', ['recursive'], 'Recursion allows a rule to apply to its own output indefinitely.'),
  mkBlank(11, '3', 'rule-and-structure', 'Given the grammar S → NP VP, why is “Sings birds” rejected even though both words exist? Because the rule fixes linear _____.', ['order'], 'Phrase-structure rules specify both constituent categories and their required linear order.'),
  mkBlank(11, '4', 'apply-the-rule', 'Under S → S and S, each side of “and” must be a complete _____.', ['sentence', 'S', 'clause'], 'Joining an incomplete fragment (such as “Leo waits and”) fails the rule requirement.'),
  mkBlank(11, '5', 'rule-and-structure', 'Besides distinguishing grammatical from ungrammatical strings, a generative grammar assigns each sentence a structural _____.', ['description'], 'Rules derive both membership and the hierarchical tree description of a sentence.'),

  mkSyntaxFix(11, '1', 'rule-and-structure', 4, 'Repair the ill-formed structure for “birds sing” so rule S → NP VP expands cleanly under S.',
    p('S', [p('VP', [p('V', [w('birds')])]), p('NP', [p('N', [w('sing')])])]),
    p('S', [p('NP', [p('N', [w('birds')])]), p('VP', [p('V', [w('sing')])])]),
    'Rule S → NP VP places Subject NP “[NP [N birds]]” before Predicate VP “[VP [V sing]]”.',
    '[S [NP [N birds]] [VP [V sing]]]'
  ),
  mkSyntaxFix(11, '2', 'apply-the-rule', 4, 'Repair the coordinated tree for “Iris rests and Leo waits” so two complete clauses S join under an upper S.',
    p('S', [p('NP', [p('name', [w('Iris')]), w('rests'), w('and'), p('name', [w('Leo')])]), p('VP', [p('V', [w('waits')])])]),
    p('S', [p('S', [p('NP', [p('name', [w('Iris')])]), p('VP', [p('V', [w('rests')])])]), w('and'), p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('waits')])])])]),
    'Under recursive S → S and S, “and” joins two separate complete S nodes under a mother S.',
    '[S [S [NP [name Iris]] [VP [V rests]]] and [S [NP [name Leo]] [VP [V waits]]]]'
  ),
  mkSyntaxFix(11, '3', 'worked-example', 4, 'Repair “Mina waves and Sam reads” so each coordinated clause builds its own NP + VP inside S.',
    p('S', [p('NP', [p('name', [w('Mina')])]), p('VP', [p('V', [w('waves')]), w('and'), p('NP', [p('name', [w('Sam')])]), p('V', [w('reads')])])]),
    p('S', [p('S', [p('NP', [p('name', [w('Mina')])]), p('VP', [p('V', [w('waves')])])]), w('and'), p('S', [p('NP', [p('name', [w('Sam')])]), p('VP', [p('V', [w('reads')])])])]),
    'Coordinating two clauses puts “and” between two S daughters of the outer S.',
    '[S [S [NP [name Mina]] [VP [V waves]]] and [S [NP [name Sam]] [VP [V reads]]]]'
  ),
  mkSyntaxFix(11, '4', 'rule-and-structure', 4, 'Repair “Ada saw dogs” so “saw dogs” forms a single VP under S.',
    p('S', [p('NP', [p('name', [w('Ada')])]), p('V', [w('saw')]), p('NP', [p('N', [w('dogs')])])]),
    p('S', [p('NP', [p('name', [w('Ada')])]), p('VP', [p('V', [w('saw')]), p('NP', [p('N', [w('dogs')])])])]),
    'Under S → NP VP and VP → V NP, “saw dogs” must group into VP before combining with Subject NP.',
    '[S [NP [name Ada]] [VP [V saw] [NP [N dogs]]]]'
  ),
  mkSyntaxFix(11, '5', 'rule-and-structure', 4, 'Repair “rain falls” so N “rain” sits inside NP and V “falls” sits inside VP under S.',
    p('VP', [p('N', [w('rain')]), p('V', [w('falls')])]),
    p('S', [p('NP', [p('N', [w('rain')])]), p('VP', [p('V', [w('falls')])])]),
    'A complete sentence expands top-level S into NP + VP.',
    '[S [NP [N rain]] [VP [V falls]]]'
  ),

  mkRecon(11, '1', 'apply-the-rule', ['and', 'waits', 'Leo', 'rests', 'Iris'], ['Iris rests and Leo waits', 'Leo waits and Iris rests'], 'Rule S → S and S coordinates two complete NP + VP clauses.'),
  mkRecon(11, '2', 'rule-and-structure', ['sing', 'loudly', 'birds'], ['birds sing loudly'], 'Order Subject NP before VP (“sing loudly”).'),
  mkRecon(11, '3', 'worked-example', ['and', 'reads', 'Ren', 'sings', 'Ivo'], ['Ren reads and Ivo sings', 'Ivo sings and Ren reads'], 'Join two complete toy-grammar clauses with “and”.'),
  mkRecon(11, '4', 'apply-the-rule', ['and', 'Mina waves', 'Iris rests', 'Leo waits', 'and'], ['Iris rests and Leo waits and Mina waves', 'Leo waits and Iris rests and Mina waves', 'Mina waves and Iris rests and Leo waits'], 'Apply recursive coordination twice across three complete clauses.'),
  mkRecon(11, '5', 'rule-and-structure', ['cats', 'chased', 'dogs'], ['dogs chased cats', 'cats chased dogs'], 'Order NP + V + NP according to S → NP VP and VP → V NP.'),

  mkTreeBuild(11, '1', 'rule-and-structure', 4, 'Build a Ch. 11 derivation tree for “Iris rests” using S → NP VP (S, NP, name, VP, V).',
    p('S', [p('NP', [p('name', [w('Iris')])]), p('VP', [p('V', [w('rests')])])]),
    'Applies S → NP VP with NP → name and VP → V.',
    '[S [NP [name Iris]] [VP [V rests]]]'
  ),
  mkTreeBuild(11, '2', 'worked-example', 4, 'Build a Ch. 11 derivation tree for “Leo waits” using S → NP VP.',
    p('S', [p('NP', [p('name', [w('Leo')])]), p('VP', [p('V', [w('waits')])])]),
    'Generates “[S [NP [name Leo]] [VP [V waits]]]” via the phrase-structure rules.',
    '[S [NP [name Leo]] [VP [V waits]]]'
  ),
  mkTreeBuild(11, '3', 'rule-and-structure', 4, 'Build a Ch. 11 tree for “birds sing” using S, NP, N, VP, and V.',
    p('S', [p('NP', [p('N', [w('birds')])]), p('VP', [p('V', [w('sing')])])]),
    'Subject NP expands to N “birds” and Predicate VP expands to V “sing”.',
    '[S [NP [N birds]] [VP [V sing]]]'
  ),
  mkTreeBuild(11, '4', 'apply-the-rule', 4, 'Build a Ch. 11 tree for “Mina calls Sam” using S → NP VP and VP → V NP.',
    p('S', [p('NP', [p('name', [w('Mina')])]), p('VP', [p('V', [w('calls')]), p('NP', [p('name', [w('Sam')])])])]),
    'VP expands to V “calls” and Object NP “[NP [name Sam]]”.',
    '[S [NP [name Mina]] [VP [V calls] [NP [name Sam]]]]'
  ),
  mkTreeBuild(11, '5', 'worked-example', 4, 'Build a Ch. 11 tree for “water flows” using S → NP VP.',
    p('S', [p('NP', [p('N', [w('water')])]), p('VP', [p('V', [w('flows')])])]),
    'Applies S → NP VP to Noun + Verb.',
    '[S [NP [N water]] [VP [V flows]]]'
  ),

  // Additional reviewed items so all 50 Syntax subtopics support multi-format topic assessments.
  mkRecon(5, '6', 'ellipsis', ['the map', 'gave', 'Mina'], ['Mina gave the map'], 'Order Subject NP “Mina” before ditransitive V “gave” and retained direct object NP “the map” when indirect recipient E is elided.'),
  mkTreeBuild(5, '6', 'ellipsis', 5, 'Build a Ch. 5 ditransitive VP for “gave supplies” using VP, V, NP, and N.',
    p('VP', [p('V', [w('gave')]), p('NP', [p('N', [w('supplies')])])]),
    'Retained overt complement NP “[NP [N supplies]]” sits directly inside VP.',
    '[VP [V gave] [NP [N supplies]]]'
  ),
  mkBlank(6, '6', 'adverbials', 'In “Rae may quietly be reading”, placing “quietly” before “be” attaches the adverbial as a sister to a higher _____.', ['VP'], 'Each stacked auxiliary projects its own VP layer; an adverbial may adjoin higher or lower inside the VP chain.'),
  mkBlank(7, '6', 'nom-appendix', 'In Burton-Roberts Chapter 7 Appendix D1, the pro-form “one” replaces the intermediate nominal level called _____.', ['NOM'], '“one” substitutes for NOM (“map of the island”), leaving outside adjuncts attached to a higher NOM.'),
  mkRecon(7, '6', 'nom-appendix', ['a red border', 'with', 'one'], ['one with a red border'], 'Post-modifying PP adjunct “with a red border” follows pro-NOM “one”.'),
  mkTreeBuild(7, '6', 'nom-appendix', 7, 'Build a Ch. 7 NP for “a detailed map” using NP, DET, NOM, AP, A, and N.',
    p('NP', [p('DET', [w('a')]), p('NOM', [p('AP', [p('A', [w('detailed')])]), p('NOM', [p('N', [w('map')])])])]),
    'DET “a” sits in NP; AP “detailed” modifies inner “[NOM [N map]]” under outer NOM.',
    '[NP [DET a] [NOM [AP [A detailed]] [NOM [N map]]]]'
  ),
  mkRecon(8, '6', 'concepts', ['the door broke', 'said', 'that', 'Vic'], ['that Vic said the door broke'], 'Complementiser “that” precedes the embedded clause “Vic said the door broke”.'),
  mkSyntaxFix(8, '6', 'concepts', 8, 'Repair “whether it rained” so C “whether” and S “it rained” combine cleanly under S-bar.',
    p('S', [p('C', [w('whether')]), p('NP', [p('N', [w('it')])]), p('VP', [p('V', [w('rained')])])]),
    p('S-bar', [p('C', [w('whether')]), p('S', [p('NP', [p('N', [w('it')])]), p('VP', [p('V', [w('rained')])])])]),
    'C + S form a subordinate S-bar clause.',
    '[S-bar [C whether] [S [NP [N it]] [VP [V rained]]]]'
  ),
  mkRecon(9, '6', 'relative-scope', ['indoors', 'who trained', 'the runners'], ['the runners who trained indoors'], 'A restrictive relative clause follows NOM inside NP to narrow down the reference.'),
  mkBlank(10, '6', 'concepts', 'In “Rae made them open the gate”, “open” is a _____ infinitive without infinitival “to”.', ['bare'], 'A bare infinitive uses the base form of V without infinitival “to” ([–tense]).'),
  mkRecon(10, '6', 'concepts', ['open the gate', 'them', 'made', 'Rae'], ['Rae made them open the gate'], 'Matrix “made” takes bare infinitival subordinate clause “them open the gate”.'),
  mkBlank(10, '7', 'noun-clause-functions', 'In “the promise to check the lock”, the infinitival clause functions as a _____ of the noun “promise”.', ['complement'], 'Content-taking nouns like “promise” and “claim” take infinitival clauses as complements under NOM.'),
];

