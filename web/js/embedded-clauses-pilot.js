import { addIntroExample, addTreeTrace, lessonExample } from './lesson-presentation.js';
import { addBranchExercise } from './lesson-tree-exercise.js';

const node = (id, label, ...children) => ({ id, label, children });
const word = (id, label, text) => node(id, label, { word: text });
const group = (id, label, text) => ({ id, label, triangle: true, words: text.split(' ') });
const clause = (intro, text) => node('embedded', 'S-bar',
  intro ? word('intro', 'C', intro) : { id: 'intro', label: 'C', empty: true },
  group('inner', 'S', text));
const tree = (sentence, root) => ({ sentence, root });

const implicit = tree('Nora is inspecting the bridge', clause(null, 'Nora is inspecting the bridge'));
const whether = tree('whether Nora was inspecting the bridge', clause('whether', 'Nora was inspecting the bridge'));
const latch = clause('that', 'the latch jammed');
const surprise = group('predicate', 'VP', 'surprised Mina');
const subject = tree('That the latch jammed surprised Mina',
  node('main', 'S', node('clausal-np', 'NP', clause('That', 'the latch jammed')), surprise));
const extraposed = tree('It surprised Mina that the latch jammed',
  node('main', 'S', group('subject', 'NP', 'It'), surprise, latch));
const object = tree('Mina noticed that the latch jammed',
  node('main', 'S', group('subject', 'NP', 'Mina'),
    node('predicate', 'VP', { ...word('head', 'V', 'noticed'), features: ['trans', 'past'] }, node('clausal-np', 'NP', latch))));

const adjective = tree('certain that the latch jammed', node('phrase', 'AP', word('head', 'A', 'certain'), latch));
const noun = tree('the claim that the latch jammed', node('phrase', 'NP',
  node('det', 'DET', word('article', 'ART', 'the')),
  node('nom', 'NOM', word('head', 'N', 'claim'), latch)));
const preposition = tree('about whether the latch jammed',
  node('phrase', 'PP', word('head', 'P', 'about'), clause('whether', 'the latch jammed')));
const waiting = group('activity', 'VP', 'waited');
const time = tree('Mina waited after the gate closed', node('main', 'S', group('subject', 'NP', 'Mina'),
  node('predicate', 'VP', waiting,
    node('added', 'PP', word('after', 'P', 'after'), group('inner', 'S', 'the gate closed')))));
const reason = tree('Mina waited because the gate jammed', node('main', 'S', group('subject', 'NP', 'Mina'),
  node('predicate', 'VP', waiting, clause('because', 'the gate jammed'))));

const labels = ['S-bar', 'C', 'S', '△'];
const repair = {
  buildTitle: 'Attach the complementiser branch',
  build: {
    branch: root => [root, root.children[0]],
    action: 'Connect C beside S',
    hint: 'Attach C directly under S′ beside the S triangle. The triangle starts at “Nora”.',
    success: 'C and S are sisters under S′. “That” stays outside the inner S.',
  },
};

export const embeddedClausesPilot = {
  description: 'Find a clause inside a larger clause. Compare what introduces it and where it attaches when it serves as a subject, complement or adverbial.',
  references: [
    'Chapter 8, printed pp. 171–176, [1–4], [11], [15–17] · Clause boundaries and complementisers',
    'Printed pp. 176–181, [23–24], [36], [40–41] · Subjects, objects and predicatives',
    'Printed pp. 181–185, [47], [54], [61], [67c] · Complements of adjectives, nouns and prepositions',
    'Printed pp. 186–187, [71], [82–84] and Discussion 7, p. 190 · Adverbial clauses',
  ],
  sections: [
    { id: 'introduction', title: 'How can one clause contain another?' },
    { id: 'concepts', title: 'Find the clause within the clause' },
    { id: 'worked-example', title: 'Read C and S', notationLabels: labels },
    { id: 'clausal-subjects-and-objects', title: 'Follow the clause as subject or object', notationLabels: [...labels, 'NP', 'VP', 'V'], notationFeatures: ['trans', 'past'] },
    { id: 'clausal-complements', title: 'Find the head the clause completes', notationLabels: [...labels, 'AP', 'A', 'NP', 'DET', 'ART', 'NOM', 'N', 'PP', 'P'] },
    { id: 'adverbial-clauses', title: 'Distinguish two ways to add a clause', notationLabels: [...labels, 'NP', 'VP', 'PP', 'P'] },
    { id: 'application', title: 'Trace two levels of embedding' },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Main clause', 'The highest clause in a sentence. It can contain smaller clauses.'],
    ['Embedded clause', 'A clause that forms part of a larger grammatical structure. It is also called a subordinate clause.'],
    ['Complementiser (C)', 'An introductory word such as “that” or “whether”, or the position that holds it in the tree.'],
    ['Extraposed subject', 'A clause that occurs at the end of a sentence while dummy “it” fills the subject position.'],
    ['Adverbial clause', 'A clause that adds a relation such as reason or condition to an event or whole statement.'],
  ],
  teach(body, _page, ui) {
    const { el, lesson, section } = ui;
    const p = text => body.append(el('p', text));
    const example = text => body.append(lessonExample(el, text));
    const trace = (label, steps) => addTreeTrace(body, ui, label, steps);

    switch (section.id) {
      case 'introduction': {
        p('Chapter 7 showed how one nominal can contain another. The same pattern can occur with clauses. An embedded clause forms part of a larger grammatical structure. The main clause is the highest clause. It includes the material embedded within it.');
        addIntroExample(body, el, 'The brackets mark the complete content of Leo’s report.',
          'Leo says [that Nora is inspecting the bridge].',
          'Inside the report, “Nora” is the subject and “is inspecting the bridge” is its predicate. The word “that” introduces this embedded clause.');
        body.append(el('h3', 'What you’ll see in this chapter'));
        const list = el('ul');
        for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
        body.append(list);
        break;
      }
      case 'concepts':
        p('In a report, the words reporting what happened sit inside the clause that contains the reporting verb.');
        example('Leo says [that Nora is inspecting the bridge].');
        p('Compare “Leo spoke and Nora inspected the bridge”. Here “and” joins two clauses at the same level. Each describes a separate event.');
        p('A clause can also contain another clause that has an embedded clause of its own. In this example, start at the deepest bracket and follow each report outward.');
        example('Maya thinks [Leo said [Nora closed the gate]].');
        p('“Closed” heads the clause reporting Nora’s action. That action is the content of what Leo “said”. The whole group starting at “Leo” supplies what Maya “thinks”. The main clause starts at “Maya” and includes both reports.');
        break;
      case 'worked-example': {
        p('A complementiser introduces a subordinate clause. C is its position in the tree. S contains the subject and predicate. The higher layer S′, read “S-bar”, groups C with S.');
        example('Leo says [that [Nora is inspecting the bridge]].');
        p('In this report, “that” fills C. In “that bridge”, it is a demonstrative inside the NP, as in Chapter 7.');
        const overt = lesson.worked_example.tree;
        trace('Compare three ways to introduce an embedded clause', [
          ['Find overt “that”', overt, overt.root.children[0].id, '“That” occupies C, beside S under S′.'],
          ['Find the unfilled C', implicit, 'intro', '“Leo says Nora is inspecting the bridge” keeps the same inner S. The C branch has no word.'],
          ['Find interrogative “whether”', whether, 'intro', 'In “Leo asked whether Nora was inspecting the bridge”, C contains “whether”. Inside S, the subject “Nora” comes before “was”.'],
        ]);
        p('A standalone question begins “Was Nora inspecting the bridge?” In the embedded question, “whether” already occupies C, so “was” stays after the subject.');
        body.append(el('h3', repair.buildTitle));
        p('Drag from S′ to the detached C branch, or use Guide me. Then select Check my tree.');
        addBranchExercise(body, ui, repair);
        break;
      }
      case 'clausal-subjects-and-objects':
        p('The completed S′ can fill different roles. In the first example, the bracketed clause identifies what surprised Mina. It is a clausal subject, shown inside the subject NP.');
        example('[That the latch jammed] surprised Mina.');
        p('A speaker can move the subject clause to the end and put dummy “it” in the subject slot. The relocated clause is called an extraposed subject.');
        example('It surprised Mina [that the latch jammed].');
        p('Compare a report of what Mina noticed. Here the clause fills the verb’s direct-object position.');
        example('Mina noticed [that the latch jammed].');
        trace('Compare three functions of the same clause', [
          ['Find the clausal subject', subject, 'clausal-np', 'The subject NP contains S′. It is a sister of the predicate VP under main S.'],
          ['Find the extraposed subject', extraposed, 'embedded', 'Dummy “it” fills the subject NP. The extraposed S′ attaches directly under the main S.'],
          ['Find the clausal object', object, 'clausal-np', 'The object NP contains S′ and attaches beside V inside the main VP.'],
        ]);
        break;
      case 'clausal-complements':
        p('A clause can complete an adjective, noun or preposition. Find the head that the clause supplies information for in each example.');
        example('Certain [that the latch jammed] · the claim [that the latch jammed] · about [whether the latch jammed]');
        trace('Find the host of each clausal complement', [
          ['Trace the adjective', adjective, 'embedded', 'S′ completes “certain”. A and S′ are sisters within AP.'],
          ['Trace the noun', noun, 'embedded', 'The clause gives the content of the claim. N and S′ are sisters within NOM.'],
          ['Trace the preposition', preposition, 'embedded', '“Whether the latch jammed” is the complement of “about”. P and S′ are sisters within PP.'],
        ]);
        p('A clause can also function as a subject predicative. In “The question is whether the latch jammed”, S′ attaches directly beside “is” within VP.');
        break;
      case 'adverbial-clauses': {
        p('A clause can be part of an optional time or reason expression. First check what introduces it.');
        example('Mina waited [after the gate closed].');
        example('Mina waited [because the gate jammed].');
        p('Temporal “after” is a preposition here. It takes S as its complement, and together they form a PP. “Because” is a subordinating conjunction. It fills C and makes an adverbial clause that supplies a reason.');
        const feedback = el('p', undefined, 'lesson-feedback');
        feedback.setAttribute('role', 'status');
        body.append(ui.practiceQuestion('reason-attachment', 'Which group attaches beside the basic VP in the reason example?', [
          'The S′ beginning with “because”', 'The inner S beginning with “the gate”',
        ], answer => {
          feedback.className = `lesson-feedback ${answer === '0' ? 'correct' : 'retry'}`;
          feedback.textContent = answer === '0'
            ? 'The whole S′ joins the basic VP. “Because” gives the relation that the added clause expresses.'
            : 'Include “because”. The inner S describes what happened to the gate, and C adds the reason relation.';
        }), feedback);
        trace('Compare the time PP and the reason clause', [
          ['Trace the time PP', time, 'added', 'The PP is a sister of the basic VP. Inside it, P “after” takes S directly.'],
          ['Trace the reason S′', reason, 'embedded', 'The whole S′ is a sister of the basic VP. Inside it, C “because” introduces S.'],
        ]);
        p('Some adverbial clauses apply to the whole statement. In “In case there is any doubt, the gate is locked”, the first clause explains why the speaker is making the statement.');
        break;
      }
      case 'application': {
        p('Find what Ria heard. Then find the embedded question inside what she heard. Choose the two words where the embedded clauses start.');
        example('Ria heard that Ivo wondered whether the hall was open.');
        const feedback = el('p', undefined, 'lesson-feedback');
        feedback.setAttribute('role', 'status');
        body.append(ui.practiceQuestion('embedded-spans', 'Where do the outer and inner embedded clauses start, in that order?', [
          '“Ivo” and “the hall”', '“that” and “whether”', '“Ria” and “whether”',
        ], answer => {
          feedback.className = `lesson-feedback ${answer === '1' ? 'correct' : 'retry'}`;
          feedback.textContent = [
            'Those are the subjects inside the two S nodes. Include the introductory word in each full S′.',
            'Both starts include the introductory word. The two embedded spans end at “open”.',
            '“Ria” starts the main clause. Start the outer embedded clause at the word that introduces what she heard.',
          ][Number(answer)];
        }), feedback);
        const check = el('details', undefined, 'lesson-sources');
        check.append(el('summary', 'Check both spans'),
          lessonExample(el, 'Ria heard [that Ivo wondered [whether the hall was open]].'),
          el('p', 'The outer report starts at “that”. The inner question starts at “whether”, and its S starts at “the hall”. Both embedded spans end at “open”.'));
        body.append(check);
        break;
      }
      case 'recap':
        p('Start with the main clause and locate the complete spans inside it. In a report, S′ covers C and S. C may contain “that” or “whether”, or be unfilled in a report such as “Leo says Nora is inspecting the bridge”.');
        p('Then ask which job the clause does. The clause about the latch can be the subject of “surprised Mina”, or the object of “noticed”. It can also complete a noun, as in “the claim that the latch jammed”.');
        p('For an optional time or reason expression, inspect the first word. Temporal “after” can head a PP containing S. “Because” introduces an adverbial S′.');
        break;
    }
  },
};
