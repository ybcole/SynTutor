import { addIntroExample, addTreeTrace, lessonExample, lessonReflection } from './lesson-presentation.js';
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
    { id: 'introduction', title: 'Introduction to wh-questions and relative clauses' },
    { id: 'concepts', title: 'Main wh-questions and fronting', notationLabels: [...questionLabels, 'PP', 'P'], notationFeatures: ['pres', 'trans'] },
    { id: 'worked-example', title: 'Wh-fronting and the object gap', notationLabels: questionLabels, notationFeatures: ['pres', 'trans'] },
    { id: 'embedded-interrogatives', title: 'Subordinate wh-clauses and embedded wh-interrogatives', notationLabels: questionLabels, notationFeatures: ['pres', 'past', 'trans'] },
    { id: 'relatives-and-complements', title: 'Relative clauses, wh-phrase omission and relative that', notationLabels: [...relativeLabels, 'V'], notationFeatures: ['trans', 'past'] },
    { id: 'relative-scope', title: 'Restrictive and non-restrictive relative clauses', notationLabels: relativeLabels },
    { id: 'application', title: 'Wh-question and relative clause exercises' },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Wh-expression', 'A word or phrase such as “who”, “which books”, or “with whom” that can start a wh-clause.'],
    ['Fronting', 'Moving a word or group to the front while it still has a job inside the clause.'],
    ['Gap', 'An empty spot in a tree. It can show where a group at the front does its job.'],
    ['Embedded interrogative', 'A question inside a larger clause, as in “Mina asked what Ren saw”.'],
    ['Relative clause', 'A clause that adds information about a nominal or NP. It can have a gap linked to the person or thing it describes.'],
    ['Restrictive relative', 'A relative clause that helps tell which people or things are meant.'],
    ['Non-restrictive relative', 'A relative clause that adds a detail about people or things you can already identify.'],
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
        p('Chapter 8 showed how to put a question inside a larger sentence. Now look at questions that ask for a missing piece of information. A wh-expression is a question word or group such as “what” or “which bridge”. You can use a possible answer to find the job of that expression. In this chapter, you’ll trace that link in questions and use it to read relative clauses.');
        addIntroExample(body, el, 'In the example below, the brackets mark the part of a possible answer that “What is Nora inspecting?” asks for.',
          'Nora is inspecting [the bridge].',
          'In “What is Nora inspecting?”, “what” asks for the direct object, “the bridge”. In the tree the wh-expression “what” appears in the front position labelled C2. A dot marks the gap after “inspecting”, where the direct object would go.');
        body.append(el('h3', 'What you’ll learn in this chapter'));
        const list = el('ul');
        for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
        body.append(list);
        break;
      }
      case 'concepts':
        p('Wh-fronting places the question word or phrase in C2 near the front of a clause. Imagine that Nora is inspecting the bridge with Ivo. Both examples below ask who is with her. In one, “with” stays inside the clause. In the other, the whole PP moves to the front.');
        example('[Who] is Nora inspecting the bridge with?');
        example('[With whom] is Nora inspecting the bridge?');
        trace('Compare three positions for a wh-gap', [
          ['Find the gap after “with”', stranded, 'wh-gap', '“With” stays inside S. The gap is an NP inside the PP headed by “with”.'],
          ['Find the whole PP gap', frontedPP, 'wh-gap', 'The whole PP “with whom” has moved. Its gap is a PP beside the VP it modifies.'],
          ['Find the subject gap', subjectQuestion, 'wh-gap', '“Who is inspecting the bridge?” asks for the inspector. The gap is in the subject NP. This analysis also shows “is” fronted, although the order of “who” and “is” stays the same.'],
        ]);
        p('A question can ask about a whole AP or AdvP. “How tall is the tower?” asks for an AP. “How quickly did the crew leave?” asks for an AdvP.');
        break;
      case 'worked-example':
        p('Find the two front positions in the object question. C2 is higher, under S″. It holds the wh-expression. C1 is lower, under S′. It holds the fronted auxiliary. Each has its own gap inside S.');
        p('Start with a possible answer: “Nora is inspecting the bridge.” The answer tells you which words “what” replaces. Mark an object gap after “inspecting”, then put “what” in the higher C2 position. The auxiliary “is” has a separate gap after the subject and moves to the lower C1 position.');
        example('[What] [is] Nora inspecting?');
        trace('Match each front position to its gap', [
          ['Find “what” in C2', main, whFront.id, '“What” asks for the object and sits in C2 under S″.'],
          ['Find the object gap', main, objectNP.id, 'The object NP sits beside the lexical V. Its dot marks where “the bridge” would occur in an answer.'],
          ['Find “is” in C1', main, auxFront.id, '“Is” sits in C1 under S′, before the subject.'],
          ['Find the auxiliary gap', main, auxOrigin.id, 'The dot under PROG [pres] marks the original position of “is”.'],
        ]);
        body.append(el('h3', repair.buildTitle));
        p('Drag a branch from the lower VP to the detached object NP, or choose Guide me. Then select Check my tree.');
        addBranchExercise(body, ui, repair);
        break;
      case 'embedded-interrogatives':
        p('An embedded interrogative is a question inside a larger clause. Compare the direct question with the sentence that tells what Mina asked.');
        p('Compare asking “What is Nora inspecting?” with reporting “Mina asked what Nora was inspecting”. The word “what” still corresponds to the object of “inspecting”. In the report, however, “was” stays after the subject, and C1 of the embedded clause is empty. Track the wh-expression and auxiliary separately.');
        example('What is Nora inspecting?');
        example('Mina asked [what Nora was inspecting].');
        trace('Compare the two front positions', [
          ['Read main C1', main, auxFront.id, 'The main question has “is” in C1.'],
          ['Read embedded C1', embedded, 'C1', '“What” is in C2. C1 has no word, and “was” stays after Nora under PROG.'],
          ['Read the embedded object gap', embedded, 'wh-gap', 'The missing object is beside “inspecting” inside the embedded S.'],
        ]);
        p('A main question can ask for a word group inside a report. Here, “what” asks for the object in the smaller clause. “Did” belongs to the main question. Its gap is under TENSE.');
        example('[What] did Mina say [Nora was inspecting •]?');
        break;
      case 'relatives-and-complements':
        p('A noun complement tells what a noun such as “claim” contains. A relative clause modifies a nominal or noun phrase. Ask whether the clause tells what the claim says or which claim the speaker means.');
        example('The claim [that the ferry was late]');
        example('The claim [which Ria disputed]');
        trace('Compare the content clause and relative variants', [
          ['Find the noun complement', nounComplement, 'content', 'The complete clause “the ferry was late” gives the claim’s content. S′ attaches beside N.'],
          ['Find the relative with “which”', claimRelative('which'), 'wh-gap', 'Ria disputed something: the claim. “Which” sits in C2. Its gap is in the object spot. The relative joins NOM.'],
          ['Compare relative “that”', claimRelative('that'), 'C2', 'Here, “that” sits in C2. The object gap is still after “disputed”.'],
          ['Leave C2 unfilled', claimRelative(null), 'C2', '“The claim Ria disputed” also works. No word fills C2, and the object gap still identifies the claim.'],
        ]);
        p('You can leave out the wh-word in this object relative. Compare the subject relative in “The guide who waved wore a hat”. “Who” is the subject of “waved”. Leaving it out gives “The guide waved wore a hat” and breaks the relative-clause reading.');
        break;
      case 'relative-scope': {
        p('A restrictive relative tells which members of a group are meant. A non-restrictive relative adds a detail about a group you can already identify. Check what each statement says was removed.');
        p('Picture two sets of lanterns, some cracked and some intact. A restrictive relative can identify the cracked ones. If everyone already knows which lanterns are meant, the clause can instead add that they had cracked. The tree places that second kind of comment beside the complete NP.');
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
        example('The ropes [which Ivo checked] were dry.');
        body.append(lessonReflection(el,
          'Which ropes does “which Ivo checked” pick out, and where would the missing object go inside the clause?',
          'The relative picks out the ropes Ivo checked. The object gap is after “checked”: Ivo checked something, and that missing object is linked to “ropes”. The relative joins the NOM “ropes” to show which ones were dry.'));
        break;
      }
      case 'recap':
        p('Try answering the question to find the job of the wh-expression. In “What is Nora inspecting?”, “what” stands for the object after “inspecting”. “Is” has its own gap under PROG.');
        p('Look at C2 first, then C1. In “Mina asked what Nora was inspecting”, “what” fills the embedded C2. C1 is empty. “Was” stays after the subject.');
        p('Inside an NP, a noun complement gives the noun’s content and joins N. A restrictive relative tells which ones and joins NOM. A non-restrictive relative adds a detail and joins the whole NP.');
        break;
    }
  },
};
