import { addIntroExample, addTreeTrace, lessonExample } from './lesson-presentation.js';
import { addBranchExercise } from './lesson-tree-exercise.js';

const node = (id, label, ...children) => ({ id, label, children });
const group = (id, label, text) => ({ id, label, triangle: true, words: text.split(' ') });
const verb = (word, ...features) => ({ ...node('verb', 'V', { word }), features });
const vp = (level, ...children) => ({ ...node(`vp${level}`, 'VP', ...children), ref: `VP${level}` });
const sentence = (text, subject, predicate) => ({
  sentence: text,
  root: node('sentence', 'S', group('subject', 'NP', subject), predicate),
});

const shed = group('shed', 'PP', 'in the shed');
const tools = group('object', 'NP', 'the tools');
const repaired = sentence('Mina repaired the tools in the shed', 'Mina', vp(2, vp(1, verb('repaired', 'trans'), tools), shed));
const put = sentence('Mina put the tools in the shed', 'Mina', vp(1, verb('put', 'complex'), tools, shed));

const checking = vp(1, verb('checked', 'trans'), group('object', 'NP', 'the latch'));
const quietly = group('quietly', 'AdvP', 'quietly');
const preceding = sentence('Mara quietly checked the latch', 'Mara', vp(2, quietly, checking));
const following = sentence('Mara checked the latch quietly', 'Mara', vp(2, checking, quietly));

const particle = sentence('Lea turned it off', 'Lea', node('predicate', 'VP',
  verb('turned', 'trans', 'phrasal'), group('object', 'NP', 'it'), node('particle', 'Prt', { word: 'off' })));
const bus = {
  sentence: 'off the bus',
  root: node('location', 'PP', node('preposition', 'P', { word: 'off' }), group('object', 'NP', 'the bus')),
};
const map = group('object', 'NP', 'a map');
const overt = sentence('Mina gave Ren a map', 'Mina', node('predicate', 'VP',
  verb('gave', 'ditrans'), group('recipient', 'NP', 'Ren'), map));
const elliptical = sentence('Mina gave a map', 'Mina', node('predicate', 'VP',
  verb('gave', 'ditrans'), node('recipient', 'NP', { id: 'understood', label: 'E' }), map));

const honestly = group('honestly', 'AdvP', 'honestly');
const answer = group('answer', 'VP', 'answered the question');
const manner = sentence('Lea answered the question honestly', 'Lea', node('scope', 'VP', answer, honestly));
const comment = {
  sentence: 'Honestly, Lea answered the question',
  root: node('scope', 'S', group('honestly', 'AdvP', 'Honestly'), node('sentence', 'S', group('subject', 'NP', 'Lea'), answer)),
};

const phraseLabels = ['S', 'NP', 'V', '△'];
const vpLevels = [...phraseLabels, 'VP1', 'VP2'];
const repair = {
  buildTitle: 'Attach the time adjunct',
  build: {
    branch: root => [root.children[1], root.children[1].children[1]],
    action: 'Connect the time PP under the outer VP',
    hint: 'Connect “in June” to the outer VP, beside the whole inner VP. Inside the inner VP, “the bridge” stays beside V.',
    success: 'The time PP and the inner VP are sisters under the outer VP. The verb and its object stay together.',
  },
};

function numberedInspection(tree) {
  const [subject, outer] = tree.root.children;
  const [inner, adjunct] = outer.children;
  return {
    ...tree,
    root: { ...tree.root, children: [subject, { ...outer, ref: 'VP2', children: [{ ...inner, ref: 'VP1' }, adjunct] }] },
  };
}

export const adverbialsPilot = {
  description: 'Compare what modifies a verb phrase and what comments on a whole sentence. Use the trees to distinguish adjuncts, complements, particles and ellipsis.',
  references: [
    'Chapter 5, printed pp. 87–92, figures [12], [15–16] and examples [17–25] · Adjuncts, VP layers and “do so”',
    'Printed pp. 92–95, figures [32], [35], [39] and examples [40a–b] · Mobility and particles',
    'Printed pp. 96–98, figure [46] · Ellipsis in a recipient context',
    'Printed pp. 98–101, figures [55a–b], [58] · VP and sentence adverbials',
  ],
  sections: [
    { id: 'introduction', title: 'What does the extra phrase modify?' },
    { id: 'concepts', title: 'Find the basic VP', notationLabels: [...vpLevels, 'PP'], notationFeatures: ['trans', 'complex'] },
    { id: 'worked-example', title: 'Trace and attach an adjunct', notationLabels: [...vpLevels, 'PP'], notationFeatures: ['trans'] },
    { id: 'mobility', title: 'Check what can move', notationLabels: [...vpLevels, 'AdvP'], notationFeatures: ['trans'] },
    { id: 'particles', title: 'Separate particles from prepositions', notationLabels: [...phraseLabels, 'VP', 'Prt', 'PP', 'P'], notationFeatures: ['trans', 'phrasal'] },
    { id: 'ellipsis', title: 'Read an understood complement', notationLabels: [...phraseLabels, 'VP', 'E'], notationFeatures: ['ditrans'] },
    { id: 'application', title: 'Choose the scope', notationLabels: ['S', 'NP', 'VP', 'AdvP', '△'] },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Adverbial', 'A grammatical function that adds information about an event or relates to a whole sentence. Several kinds of phrase can serve this function.'],
    ['Adjunct', 'An optional modifier that adds information such as when, where or how an event happened.'],
    ['Particle', 'A word that combines with a verb to form a phrasal verb, such as “off” in “turn off”.'],
    ['Ellipsis', 'The omission of material that can be understood from context.'],
    ['Disjunct adverbial', 'A comment by a speaker or writer on a whole statement or on how it is expressed.'],
    ['Conjunct adverbial', 'An expression that connects a statement to the surrounding discourse, such as “therefore”.'],
  ],
  teach(body, _page, ui) {
    const { el, lesson, section, button } = ui;
    const p = text => body.append(el('p', text));
    const example = text => body.append(lessonExample(el, text));
    const heading = text => body.append(el('h3', text));
    const trace = (label, steps) => addTreeTrace(body, ui, label, steps);

    switch (section.id) {
      case 'introduction': {
        p('Chapter 4 grouped “inspected” with its direct object. Adding a time leaves that event intact. A phrase that supplies a detail about an event or relates to a whole statement has an adverbial function. An adjunct is an optional modifier. It can add information such as time, place or manner to a verb phrase.');
        addIntroExample(body, el, 'The brackets separate the inspection from its time.',
          'Nora [inspected the bridge] [in June].',
          '“In June” is a prepositional phrase (PP). Its function here is to tell when the inspection happened. The entire inspection is what it modifies.');
        heading('What you’ll see in this chapter');
        const list = el('ul');
        for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
        body.append(list);
        break;
      }
      case 'concepts': {
        p('In “Nora inspected the bridge in June”, the verb and object describe the inspection. The time phrase can be left out while the event stays the same. Use the same question about the PP in the next two sentences.');
        example('Mina repaired the tools [in the shed].');
        example('Mina put the tools [in the shed].');
        p('With “repaired”, the shed is where the repair happened. With “put”, it is where the tools ended up. That resulting location completes the placement pattern. A phrase that gives the object’s resulting state or location can be an object predicative.');
        const feedback = el('p', undefined, 'lesson-feedback');
        feedback.setAttribute('role', 'status');
        body.append(ui.practiceQuestion('placement-pp', 'Where does “in the shed” attach in the placement example?', [
          'Beside V in the basic VP', 'Beside the basic VP in a higher VP',
        ], answer => {
          feedback.textContent = answer === '0'
            ? 'Yes. The resulting location is a complement of “put”, so it attaches beside V.'
            : 'That works for the optional repair location. With “put”, the location completes the placement pattern. Attach the PP beside V.';
        }), feedback);
        p('In the trees, VP₁ is the verb with its complements. VP₂ is the larger group that includes the adjunct.');
        trace('Compare two roles for the same PP', [
          ['Trace the repair location', repaired, 'shed', '“In the shed” is an adjunct here. The PP is a sister of VP₁ under VP₂.'],
          ['Trace the resulting location', put, 'shed', '“In the shed” is an object predicative here. It is a complement beside V and the object NP in the basic VP.'],
        ]);
        break;
      }
      case 'worked-example': {
        p('Return to the inspection. The inner VP, VP₁, contains the verb and its complement. The outer VP, VP₂, contains that whole phrase and the time adjunct.');
        example('Nora [inspected the bridge] [in June].');
        const inspection = numberedInspection(lesson.worked_example.tree);
        const [, outer] = inspection.root.children;
        const [inner, time] = outer.children;
        trace('Trace the layers of the inspection VP', [
          ['Find the basic VP', inspection, inner.id, '“Inspected the bridge” describes the inspection. The object NP joins V inside VP₁.'],
          ['Find the time adjunct', inspection, time.id, '“In June” attaches beside the whole basic VP.'],
          ['Find the full predicate', inspection, outer.id, 'VP₂ covers the inspection and its time. Another adjunct can add another VP layer.'],
        ]);
        heading(repair.buildTitle);
        p('Connect the detached PP “in June” to the same parent as the inner VP. Drag from the parent’s connection point or use Guide me. Then select Check my tree.');
        addBranchExercise(body, ui, repair);
        example('Nora inspected the bridge in June, and Mara did so in July.');
        p('The expression “did so” can stand for a verb phrase. Here it replaces “inspected the bridge”. The time changes from June to July while the activity stays the same.');
        break;
      }
      case 'mobility':
        p('The time adjunct followed the basic VP. Some adjuncts can also come before it. In these two examples, “quietly” is an adverb phrase (AdvP) that describes how Mara checked the latch.');
        example('Mara [quietly] checked the latch.');
        example('Mara checked the latch [quietly].');
        trace('Compare positions for the same manner adjunct', [
          ['Read the preceding adjunct', preceding, 'quietly', '“Quietly” precedes the basic VP. Both share VP₂.'],
          ['Read the following adjunct', following, 'quietly', '“Quietly” follows the basic VP. Both still share VP₂.'],
        ]);
        p('Some noun phrases can do the same job. In “Mara checked the latch last night”, the NP “last night” adds a time. Other adverbial positions can need a different analysis. The trees here cover clear cases where the adjunct sits beside the whole phrase it modifies.');
        break;
      case 'particles':
        p('When a short word like “off” follows a verb, check what it groups with. A particle combines with a verb to form a phrasal verb. In “turned off”, “off” helps express switching something off. In “off the bus”, the preposition begins a phrase that describes the path.');
        example('Lea [turned off] the lamp.');
        example('Lea stepped [off the bus].');
        p('Try replacing “the lamp” with “it”. The switching meaning survives in “Lea turned it off”. With the stepping meaning, “off” stays before its complement, as in “Lea stepped off it”.');
        trace('Compare a particle and a preposition', [
          ['Find the separated particle', particle, 'particle', '“Off” is Prt and follows the object pronoun. V carries [trans] and [phrasal].'],
          ['Find the preposition', bus, 'preposition', '“Off” heads the PP “off the bus”. It stays with “the bus” in this use.'],
        ]);
        break;
      case 'ellipsis':
        p('Leaving a phrase out can give two different results. An adjunct can be left out because it supplies extra detail. In ellipsis, a role is still understood even though the words that would fill it are absent.');
        p('Imagine that Mina is giving supplies to Ren and the conversation is about what Ren received.');
        example('Mina gave Ren a map.');
        example('Mina gave a map.');
        trace('Compare a spoken and an understood recipient', [
          ['Find the spoken recipient', overt, 'recipient', '“Ren” names the recipient. It is the indirect object in this ditransitive VP.'],
          ['Find the understood recipient', elliptical, 'understood', 'The context still identifies Ren. E marks the understood recipient under NP. E contributes no spoken word.'],
        ]);
        p('An extra phrase such as “after lunch” would tell when the gift was given. The recipient is a role in the giving event itself.');
        break;
      case 'application': {
        p('An adverbial can describe an event or relate to the whole statement. Compare the two readings of “honestly”.');
        example('Lea answered the question [honestly].');
        example('[Honestly], Lea answered the question.');
        trace('Compare event manner with a speaker comment', [
          ['Read the manner of answering', manner, 'honestly', '“Honestly” describes how Lea answered. The AdvP is beside VP within a higher VP.'],
          ['Read the speaker’s comment', comment, 'honestly', '“Honestly” marks how the speaker presents the statement. The AdvP is beside S within a higher S.'],
        ]);
        p('A sentence adverbial that expresses a speaker’s comment is a disjunct. A conjunct links the statement to nearby discourse. In “The latch broke. Therefore, the gate opened”, “therefore” connects the opening to the earlier event as its result.');
        example('[Unfortunately], the gate jammed.');
        const check = el('details', undefined, 'lesson-sources');
        check.append(el('summary', 'Check what “unfortunately” modifies'),
          el('p', 'It gives the speaker’s evaluation of the entire statement. Draw it beside S, under a higher S.'));
        body.append(check);
        break;
      }
      case 'recap':
        p('Start with the verb and its complements. In “Mina put the tools in the shed”, the PP gives the resulting location and attaches beside V. In “Nora inspected the bridge in June”, the PP supplies the time and attaches beside the basic VP.');
        p('Then check what the words group with. The object can come between “turned” and the particle “off”. In ellipsis, context can supply a complement such as the recipient even when no words name it.');
        p('For an adverbial, ask what it applies to. Manner can describe the event inside VP. A comment such as “unfortunately” applies to the whole statement and sits beside S in the tree.');
        break;
    }
  },
};
