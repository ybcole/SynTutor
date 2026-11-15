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
const twoAdjuncts = sentence('Mara checked the latch quietly after lunch', 'Mara',
  vp(3, following.root.children[1], group('time', 'PP', 'after lunch')));

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
    { id: 'introduction', title: 'Introduction to adverbials' },
    { id: 'concepts', title: 'Adjunct adverbials and levels of VP', notationLabels: [...vpLevels, 'PP'], notationFeatures: ['trans', 'complex'] },
    { id: 'worked-example', title: 'VP adjunct attachment exercise', notationLabels: [...vpLevels, 'VP3', 'AdvP', 'PP'], notationFeatures: ['trans'] },
    { id: 'mobility', title: 'Mobility of adverbials', notationLabels: [...vpLevels, 'AdvP'], notationFeatures: ['trans'] },
    { id: 'particles', title: 'Phrasal verbs and ellipsis', notationLabels: [...phraseLabels, 'VP', 'Prt', 'PP', 'P'], notationFeatures: ['trans', 'phrasal'] },
    { id: 'ellipsis', title: 'Ellipsis and understood complements', notationLabels: [...phraseLabels, 'VP', 'E'], notationFeatures: ['ditrans'] },
    { id: 'application', title: 'Sentence adverbials: disjuncts and conjuncts', notationLabels: ['S', 'NP', 'VP', 'AdvP', '△'] },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Adverbial', 'A job a phrase can do. It can tell when, where, or how an event happened, or apply to a whole statement.'],
    ['Adjunct', 'An optional modifier. It can tell when, where, or how something happened.'],
    ['Particle', 'A word like “off” that joins a verb to make a phrasal verb, such as “turn off”.'],
    ['Ellipsis', 'Leaving words out when their meaning is clear from the words or situation around them.'],
    ['Disjunct adverbial', 'A comment on a whole statement or on how someone says it.'],
    ['Conjunct adverbial', 'A word or phrase such as “therefore” that links a statement to the words around it.'],
  ],
  teach(body, _page, ui) {
    const { el, lesson, section, button } = ui;
    const p = text => body.append(el('p', text));
    const example = text => body.append(lessonExample(el, text));
    const heading = text => body.append(el('h3', text));
    const trace = (label, steps) => addTreeTrace(body, ui, label, steps);

    switch (section.id) {
      case 'introduction': {
        p('Chapter 4 looked at the groups a verb takes as complements. Now try adding a detail to an event you already know. If Nora inspected the bridge in June, would taking out the time change what she did? In this chapter, you’ll use questions like this to tell a complement from an extra detail and decide where each one goes in a tree.');
        addIntroExample(body, el, 'The first brackets mark the action. The second mark the group that says when it happened.',
          'Nora [inspected the bridge] [in June].',
          '“In June” is a prepositional phrase (PP). It does the job of an adverbial because it tells when the inspection happened. “Nora inspected the bridge” still works on its own. Here the PP is an adjunct, an optional detail that modifies the whole verb phrase.');
        heading('What you’ll see in this chapter');
        const list = el('ul');
        for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
        body.append(list);
        break;
      }
      case 'concepts': {
        p('In “Nora inspected the bridge in June”, you can leave out “in June” and still tell what Nora did. Try leaving out the PP in the next two sentences. What changes?');
        example('Mina repaired the tools [in the shed].');
        example('Mina put the tools [in the shed].');
        p('With “repaired”, the shed is where the work happened. With “put”, the shed is where the tools ended up. The place completes the meaning of “put” here. A phrase that tells where an object ends up or what it becomes can be an object predicative.');
        const feedback = el('p', undefined, 'lesson-feedback');
        feedback.setAttribute('role', 'status');
        body.append(ui.practiceQuestion('placement-pp', 'Where does “in the shed” attach in the placement example?', [
          'Beside V in the basic VP', 'Beside the basic VP in a higher VP',
        ], answer => {
          feedback.textContent = answer === '0'
            ? 'Yes. The resulting location is a complement of “put”, so it attaches beside V.'
            : 'That works for the optional repair location. With “put”, the location completes the placement pattern. Attach the PP beside V.';
        }), feedback);
        p('VP₁ holds the verb and its complements. VP₂ is the bigger group. It holds VP₁ and the adjunct.');
        trace('Compare two roles for the same PP', [
          ['Trace the repair location', repaired, 'shed', '“In the shed” is an adjunct here. The PP is a sister of VP₁ under VP₂.'],
          ['Trace the resulting location', put, 'shed', '“In the shed” is an object predicative here. It is a complement beside V and the object NP in the basic VP.'],
        ]);
        break;
      }
      case 'worked-example': {
        p('Look at the inspection again. Find the verb and its complement inside VP₁. Then find VP₂. It holds all of VP₁ plus the time adjunct.');
        example('Nora [inspected the bridge] [in June].');
        const inspection = numberedInspection(lesson.worked_example.tree);
        const [, outer] = inspection.root.children;
        const [inner, time] = outer.children;
        trace('Trace the layers of the inspection VP', [
          ['Find the basic VP', inspection, inner.id, '“Inspected the bridge” describes the inspection. The object NP joins V inside VP₁.'],
          ['Find the time adjunct', inspection, time.id, '“In June” attaches beside the whole basic VP.'],
          ['Find the full predicate', inspection, outer.id, 'VP₂ covers the inspection and its time. Another adjunct can add another VP layer.'],
          ['Read two adjunct layers', twoAdjuncts, 'vp3', 'Start with VP₁ “checked the latch”. “Quietly” adds VP₂. “After lunch” applies to that whole event and adds VP₃.'],
        ]);
        heading(repair.buildTitle);
        p('Attach “in June” so it shares a parent with the inner VP. Drag from that parent’s connection point or choose Guide me. Then select Check my tree.');
        addBranchExercise(body, ui, repair);
        example('Nora inspected the bridge in June, and Mara did so in July.');
        p('“Did so” can stand for a whole VP. Here it replaces “inspected the bridge”. The time changes from June to July. The action stays the same.');
        break;
      }
      case 'mobility':
        p('“In June” came after the basic VP. Some adjuncts can also go before it. In both examples below, “quietly” is an adverb phrase (AdvP). It tells how Mara checked the latch.');
        example('Mara [quietly] checked the latch.');
        example('Mara checked the latch [quietly].');
        trace('Compare positions for the same manner adjunct', [
          ['Read the preceding adjunct', preceding, 'quietly', '“Quietly” precedes the basic VP. Both share VP₂.'],
          ['Read the following adjunct', following, 'quietly', '“Quietly” follows the basic VP. Both still share VP₂.'],
        ]);
        p('An NP can add a time, too. In “Mara checked the latch last night”, “last night” is an NP. In these trees, the adjunct sits next to the whole phrase it modifies. Other positions can work differently.');
        break;
      case 'particles':
        p('When you see “off”, ask which words it goes with. In “turned off”, “off” is a particle. It joins a verb to make a phrasal verb meaning “switch off”. In “off the bus”, “off” is a preposition. It joins “the bus” to show the path.');
        example('Lea [turned off] the lamp.');
        example('Lea stepped [off the bus].');
        p('Replace “the lamp” with “it”. In “Lea turned it off”, “it” fits before the particle. In “Lea stepped off it”, “it” stays after the preposition.');
        trace('Compare a particle and a preposition', [
          ['Find the separated particle', particle, 'particle', '“Off” is Prt and follows the object pronoun. V carries [trans] and [phrasal].'],
          ['Find the preposition', bus, 'preposition', '“Off” heads the PP “off the bus”. It stays with “the bus” in this use.'],
        ]);
        break;
      case 'ellipsis':
        p('You can leave out an adjunct because it adds an extra detail. Ellipsis works differently. The words are missing, but the listener can still work out the role they would fill.');
        p('Suppose Mina gives supplies to Ren. The people talking already know that Ren gets the supplies.');
        example('Mina gave Ren a map.');
        example('Mina gave a map.');
        trace('Compare a spoken and an understood recipient', [
          ['Find the spoken recipient', overt, 'recipient', '“Ren” names the recipient. It is the indirect object in this ditransitive VP.'],
          ['Find the understood recipient', elliptical, 'understood', 'The listener can still work out that Ren gets the gift. E marks the understood recipient under NP. No word is spoken for E.'],
        ]);
        p('“After lunch” would add a time. The recipient has a role in the giving itself, even when no words name that person.');
        break;
      case 'application': {
        p('An adverbial can tell how something happened. It can also apply to the whole statement. See how “honestly” does both jobs.');
        example('Lea answered the question [honestly].');
        example('[Honestly], Lea answered the question.');
        trace('Compare event manner with a speaker comment', [
          ['Read the manner of answering', manner, 'honestly', '“Honestly” describes how Lea answered. The AdvP is beside VP within a higher VP.'],
          ['Read the speaker’s comment', comment, 'honestly', '“Honestly” marks how the speaker presents the statement. The AdvP is beside S within a higher S.'],
        ]);
        p('A disjunct adds the speaker’s comment to a statement. A conjunct links a statement to the words around it. In “The latch broke. Therefore, the gate opened”, “therefore” shows that the opening was a result of the break.');
        example('[Unfortunately], the gate jammed.');
        const check = el('details', undefined, 'lesson-sources');
        check.append(el('summary', 'Check what “unfortunately” modifies'),
          el('p', 'It gives the speaker’s evaluation of the entire statement. Draw it beside S, under a higher S.'));
        body.append(check);
        break;
      }
      case 'recap':
        p('Start with the verb and its complements. In “Mina put the tools in the shed”, the PP tells where the tools ended up and sits beside V. In “Nora inspected the bridge in June”, the PP adds a time and sits beside the basic VP.');
        p('Next, check which words go together. The object can go between “turned” and the particle “off”. With ellipsis, the missing words can still have a role, such as naming the recipient.');
        p('Ask what each adverbial goes with. A manner adverbial tells how the event happened and sits inside VP. “Unfortunately” can give the speaker’s view of the whole event. In that case, it sits beside S.');
        break;
    }
  },
};
