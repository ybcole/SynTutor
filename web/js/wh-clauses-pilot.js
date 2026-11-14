import { addIntroExample, addTreeTrace, lessonExample } from './lesson-presentation.js';
import { addBranchExercise } from './lesson-tree-exercise.js';

const node = (id, label, ...children) => ({ id, label, children });
const word = (id, label, text) => node(id, label, { word: text });
const group = (id, label, text) => ({ id, label, triangle: true, words: text.split(' ') });
const tree = (sentence, root) => ({ sentence, root });
const empty = label => ({ id: label, label, empty: true });
const gap = (id, label) => node(id, label, { id: `${id}-dot`, gap: true });
const nora = group('subject', 'NP', 'Nora');
const bridge = group('object', 'NP', 'the bridge');
const inspecting = { ...word('inspect', 'V', 'inspecting'), features: ['trans'] };
const lexical = object => node('lexical', 'VP', inspecting, object);
const progressive = (head, complement) => node('progressive', 'VP', head, complement);
const wh = (front, lower, inner) => node('wh-clause', 'S-dbar', front, node('sbar', 'S-bar', lower, inner));
const vacatedAux = { ...gap('auxiliary-gap', 'PROG'), features: ['pres'] };
const companion = (sentence, front, adjunct) => tree(sentence,
  wh(front, word('C1', 'C1', 'is'), node('clause', 'S', nora,
    node('predicate', 'VP', progressive(vacatedAux, lexical(bridge)), adjunct))));
const stranded = companion('Who is Nora inspecting the bridge with',
  word('C2', 'C2', 'Who'), node('companion', 'PP', word('with', 'P', 'with'), gap('wh-gap', 'NP')));
const frontedPP = companion('With whom is Nora inspecting the bridge',
  group('C2', 'C2', 'With whom'), gap('wh-gap', 'PP'));
const subjectQuestion = tree('Who is inspecting the bridge', wh(word('C2', 'C2', 'Who'),
  word('C1', 'C1', 'is'), node('clause', 'S', gap('wh-gap', 'NP'), progressive(vacatedAux, lexical(bridge)))));
const embedded = tree('what Nora was inspecting', wh(word('C2', 'C2', 'what'), empty('C1'),
  node('clause', 'S', nora, progressive({ ...word('auxiliary', 'PROG', 'was'), features: ['past'] },
    lexical(gap('wh-gap', 'NP'))))));

const article = node('det', 'DET', word('article', 'ART', 'the'));
const claim = word('noun', 'N', 'claim');
const content = node('content', 'S-bar', word('C1', 'C1', 'that'), group('clause', 'S', 'the ferry was late'));
const nounComplement = tree('the claim that the ferry was late',
  node('np', 'NP', article, node('nom', 'NOM', claim, content)));
function claimRelative(intro) {
  const clause = wh(intro ? word('C2', 'C2', intro) : empty('C2'), empty('C1'),
    node('clause', 'S', group('subject', 'NP', 'Ria'),
      node('predicate', 'VP', { ...word('disputed', 'V', 'disputed'), features: ['trans', 'past'] }, gap('wh-gap', 'NP'))));
  return tree(['the claim', intro, 'Ria disputed'].filter(Boolean).join(' '),
    node('np', 'NP', article, node('nom', 'NOM', node('base', 'NOM', claim), clause)));
}
const lanterns = node('base', 'NOM', word('noun', 'N', 'lanterns'));
const cracked = wh(word('C2', 'C2', 'which'), empty('C1'),
  node('clause', 'S', gap('wh-gap', 'NP'), group('predicate', 'VP', 'had cracked')));
const restrictive = tree('the lanterns which had cracked',
  node('np', 'NP', article, node('nom', 'NOM', lanterns, cracked)));
const nonRestrictive = tree('the lanterns, which had cracked',
  node('np', 'NP', node('inner-np', 'NP', article, lanterns), cracked));

function objectPositions(root) {
  const [whFront, sBar] = root.children;
  const [auxFront, s] = sBar.children;
  const [, upperVP] = s.children;
  const [auxOrigin, lowerVP] = upperVP.children;
  return { whFront, auxFront, auxOrigin, lowerVP, objectNP: lowerVP.children[1] };
}

const repair = {
  buildTitle: 'Attach the NP that contains the object gap',
  build: {
    branch(root) {
      const { lowerVP, objectNP } = objectPositions(root);
      return [lowerVP, objectNP];
    },
    action: 'Connect the object-gap NP beside V',
    hint: 'Attach the detached NP to the lower VP, beside “inspecting”. The auxiliary gap stays under PROG.',
    success: 'The object-gap NP sits beside V in the lower VP. The separate auxiliary gap stays under PROG.',
  },
};

const clauseLabels = ['S-dbar', 'C2', 'S-bar', 'C1', 'S', 'NP', 'VP', '△', '•'];
const questionLabels = [...clauseLabels, 'PROG', 'V'];
const relativeLabels = [...clauseLabels, 'DET', 'ART', 'NOM', 'N'];

export const whClausesPilot = {
  description: 'Trace the gaps in main and embedded wh-questions. Then compare noun complements and the two kinds of relative clause.',
  references: [
    'Chapter 9, printed pp. 196–201, [11b], [13–14] and Discussion 2, p. 213 · Main questions and gap positions',
    'Printed pp. 201–203, [17–19], [26] · Deeper gaps and embedded questions',
    'Printed pp. 204–208, [38–39], [44–54] · Noun complements and relative variants',
    'Printed pp. 208–211, [59–60] · Restrictive and non-restrictive relatives',
  ],
  sections: [
    { id: 'introduction', title: 'What does a wh-clause ask or describe?' },
    { id: 'concepts', title: 'Find what the question asks for', notationLabels: [...questionLabels, 'PP', 'P'], notationFeatures: ['pres', 'trans'] },
    { id: 'worked-example', title: 'Trace and repair the object question', notationLabels: questionLabels, notationFeatures: ['pres', 'trans'] },
    { id: 'embedded-interrogatives', title: 'Read an embedded wh-question', notationLabels: questionLabels, notationFeatures: ['pres', 'past', 'trans'] },
    { id: 'relatives-and-complements', title: 'Compare a relative with a noun complement', notationLabels: [...relativeLabels, 'V'], notationFeatures: ['trans', 'past'] },
    { id: 'relative-scope', title: 'Check what the relative modifies', notationLabels: relativeLabels },
    { id: 'application', title: 'Explain a new relative clause' },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Wh-expression', 'A word or phrase such as “who”, “which books” or “with whom” that can introduce a wh-clause.'],
    ['Fronting', 'Placing a word or phrase at the front of a clause while it keeps a grammatical role inside that clause.'],
    ['Gap', 'A tree position with no spoken words that can correspond to a fronted element.'],
    ['Embedded interrogative', 'A question expressed as part of a larger clause, as in “asked what Ren saw”.'],
    ['Relative clause', 'A clause that modifies a nominal or noun phrase and contains a gap linked to the noun phrase it describes.'],
    ['Restrictive relative', 'A relative clause that helps identify which people or things are meant.'],
    ['Non-restrictive relative', 'A relative clause that adds information about an already identified person or group.'],
  ],
  teach(body, _page, ui) {
    const { el, lesson, section } = ui;
    const p = text => body.append(el('p', text));
    const example = text => body.append(lessonExample(el, text));
    const trace = (label, steps) => addTreeTrace(body, ui, label, steps);
    const main = lesson.worked_example.tree;
    const { whFront, auxFront, auxOrigin, objectNP } = objectPositions(main.root);

    switch (section.id) {
      case 'introduction': {
        p('Chapter 8 showed how a clause can report a question. This chapter starts with a question that asks for a particular part of an answer. A wh-expression is a word or phrase such as “what” or “which bridge”. In a wh-question it can appear at the front, a placement called fronting. The tree uses a dot to mark its gap, the position that supplies its grammatical role.');
        addIntroExample(body, el, 'In the statement, the brackets show the group the question asks for.',
          'Nora is inspecting [the bridge].',
          'In “What is Nora inspecting?”, “what” asks for the direct object. The object position after “inspecting” has no spoken words.');
        body.append(el('h3', 'What you’ll see in this chapter'));
        const list = el('ul');
        for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
        body.append(list);
        break;
      }
      case 'concepts':
        p('Start with a possible answer. Suppose Nora is inspecting the bridge with Ivo. The next two questions both ask about her companion. One keeps “with” inside the clause, and the other fronts the whole phrase.');
        example('[Who] is Nora inspecting the bridge with?');
        example('[With whom] is Nora inspecting the bridge?');
        trace('Compare three positions for a wh-gap', [
          ['Find the gap after “with”', stranded, 'wh-gap', '“With” stays inside S. The gap is an NP inside the PP headed by “with”.'],
          ['Find the whole PP gap', frontedPP, 'wh-gap', 'The whole PP “with whom” has moved. Its gap is a PP beside the VP it modifies.'],
          ['Find the subject gap', subjectQuestion, 'wh-gap', '“Who is inspecting the bridge?” asks for the inspector. The gap is in the subject NP. This analysis also shows “is” fronted, although the order of “who” and “is” stays the same.'],
        ]);
        p('A whole adjective phrase or adverb phrase can also be questioned, as in “How tall is the tower?” or “How quickly did the crew leave?”');
        break;
      case 'worked-example':
        p('Return to the object question. C2 is the higher front position for the wh-expression under S″. C1 is the lower position for the fronted auxiliary under S′. Each fronted item corresponds to a different gap inside S.');
        example('[What] [is] Nora inspecting?');
        trace('Match each front position to its gap', [
          ['Find “what” in C2', main, whFront.id, '“What” asks for the object and sits in C2 under S″.'],
          ['Find the object gap', main, objectNP.id, 'The object NP sits beside the lexical V. Its dot marks where “the bridge” would occur in an answer.'],
          ['Find “is” in C1', main, auxFront.id, '“Is” sits in C1 under S′, before the subject.'],
          ['Find the auxiliary gap', main, auxOrigin.id, 'The dot under PROG [pres] marks the original position of “is”.'],
        ]);
        body.append(el('h3', repair.buildTitle));
        p('Drag from the lower VP to the detached object NP, or use Guide me. Then select Check my tree.');
        addBranchExercise(body, ui, repair);
        break;
      case 'embedded-interrogatives':
        p('An embedded interrogative expresses a question inside a larger clause. Compare a question asked directly with one that reports what Mina asked.');
        example('What is Nora inspecting?');
        example('Mina asked [what Nora was inspecting].');
        trace('Compare the two front positions', [
          ['Read main C1', main, auxFront.id, 'The main question has “is” in C1.'],
          ['Read embedded C1', embedded, 'C1', '“What” is in C2. C1 has no word, and “was” stays after Nora under PROG.'],
          ['Read the embedded object gap', embedded, 'wh-gap', 'The missing object is beside “inspecting” inside the embedded S.'],
        ]);
        p('A main wh-question can ask about something inside a report. In the next example, “what” asks for the object inside the report. “Did” belongs to the main question and leaves its own gap under TENSE.');
        example('[What] did Mina say [Nora was inspecting •]?');
        break;
      case 'relatives-and-complements':
        p('A noun complement gives the content of a noun such as “claim”. A relative clause modifies a nominal or noun phrase. In these examples, check whether the clause gives what the claim says or helps identify which claim is meant.');
        example('The claim [that the ferry was late]');
        example('The claim [which Ria disputed]');
        trace('Compare the content clause and relative variants', [
          ['Find the noun complement', nounComplement, 'content', 'The complete clause “the ferry was late” gives the claim’s content. S′ attaches beside N.'],
          ['Find the relative with “which”', claimRelative('which'), 'wh-gap', 'Ria disputed something: the claim. “Which” sits in C2 and corresponds to the object gap. The relative joins NOM.'],
          ['Compare relative “that”', claimRelative('that'), 'C2', 'Relative “that” occupies C2 in this analysis. The object gap remains after “disputed”.'],
          ['Leave C2 unfilled', claimRelative(null), 'C2', '“The claim Ria disputed” also works. No word fills C2, and the object gap still identifies the claim.'],
        ]);
        p('Omission works in this object relative. In “The guide who waved wore a hat”, “who” corresponds to the subject of “waved”. Removing it would leave “The guide waved wore a hat”, which breaks that relative-clause reading.');
        break;
      case 'relative-scope': {
        p('A restrictive relative narrows the set being discussed. A non-restrictive relative adds information about a group already identified. Compare what each statement says was removed.');
        example('The lanterns [which had cracked] were removed.');
        example('The lanterns, [which had cracked], were removed.');
        const feedback = el('p', undefined, 'lesson-feedback');
        feedback.setAttribute('role', 'status');
        body.append(ui.practiceQuestion('relative-scope', 'Which sentence limits the removal statement to the cracked lanterns?', [
          'The first sentence', 'The second sentence',
        ], answer => {
          feedback.className = `lesson-feedback ${answer === '0' ? 'correct' : 'retry'}`;
          feedback.textContent = answer === '0'
            ? 'The first relative picks out the cracked lanterns from the larger set.'
            : 'The second sentence says the already identified lanterns were removed and adds that they had cracked.';
        }), feedback);
        trace('Compare NOM and NP attachment', [
          ['Read the restrictive relative', restrictive, 'wh-clause', 'The relative joins “lanterns” under a larger NOM. “The” determines the whole group “lanterns which had cracked”.'],
          ['Read the non-restrictive relative', nonRestrictive, 'inner-np', '“The lanterns” is a full NP. The relative joins that NP and adds a comment about it.'],
        ]);
        break;
      }
      case 'application': {
        p('Decide whether the bracketed relative gives content or helps identify the ropes. Then recover the missing object.');
        example('The ropes [which Ivo checked] were dry.');
        const feedback = el('p', undefined, 'lesson-feedback');
        feedback.setAttribute('role', 'status');
        body.append(ui.practiceQuestion('relative-transfer', 'What does “which Ivo checked” do?', [
          'Gives the content of the noun', 'Identifies which ropes were dry',
        ], answer => {
          feedback.className = `lesson-feedback ${answer === '1' ? 'correct' : 'retry'}`;
          feedback.textContent = answer === '1'
            ? 'The statement applies to the ropes Ivo checked.'
            : 'Try supplying what Ivo checked. The missing object links the clause to “ropes”.';
        }), feedback);
        const check = el('details', undefined, 'lesson-sources');
        check.append(el('summary', 'Check the relative’s job'),
          el('p', 'The relative picks out the ropes Ivo checked. The object gap is after “checked”, and the relative joins the NOM “ropes”.'));
        body.append(check);
        break;
      }
      case 'recap':
        p('Use a possible answer to recover the role of a wh-expression. In “What is Nora inspecting?”, the gap after “inspecting” corresponds to “what”. The separate gap under PROG corresponds to “is”.');
        p('Read C2 before C1. In “Mina asked what Nora was inspecting”, the embedded C2 holds “what”. C1 is unfilled, and “was” stays after the subject.');
        p('Inside an NP, a clause that gives the noun’s content joins N. A restrictive relative joins NOM and narrows the set. A non-restrictive relative joins the whole NP and adds information.');
        break;
    }
  },
};
