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
    { id: 'introduction', title: 'Introduction to clause embedding' },
    { id: 'concepts', title: 'Clause embedding and the complementisers that and whether' },
    { id: 'worked-example', title: 'Complementiser and clause structure (C and S)', notationLabels: labels },
    { id: 'clausal-subjects-and-objects', title: 'Clausal subjects, extraposition and verb complements', notationLabels: [...labels, 'NP', 'VP', 'V'], notationFeatures: ['trans', 'past'] },
    { id: 'clausal-complements', title: 'Clausal complements of adjectives, nouns and prepositions', notationLabels: [...labels, 'AP', 'A', 'NP', 'DET', 'ART', 'NOM', 'N', 'PP', 'P'] },
    { id: 'adverbial-clauses', title: 'Adverbial clauses and temporal prepositions', notationLabels: [...labels, 'NP', 'VP', 'PP', 'P'] },
    { id: 'application', title: 'Exercises on embedding and clause functions' },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Main clause', 'The highest clause in a sentence. It can hold smaller clauses.'],
    ['Embedded clause', 'A clause inside a larger structure. It is also called a subordinate clause.'],
    ['Complementiser (C)', 'A word such as “that” or “whether” that starts a subordinate clause. C is its spot in the tree.'],
    ['Extraposed subject', 'A subject clause that moves to the end. Dummy “it” fills the subject spot.'],
    ['Adverbial clause', 'A clause that can tell when or why something happens, or give a condition. It can apply to an event or a whole statement.'],
  ],
  teach(body, _page, ui) {
    const { el, lesson, section } = ui;
    const p = text => body.append(el('p', text));
    const example = text => body.append(lessonExample(el, text));
    const trace = (label, steps) => addTreeTrace(body, ui, label, steps);

    switch (section.id) {
      case 'introduction': {
        p('A clause is a grammatical unit built around a predicate. It often has a subject of its own. An embedded clause fits inside a larger phrase or clause. This chapter looks at how one clause fits inside another and what jobs the smaller clause can do.');
        addIntroExample(body, el, 'In the example below, the brackets mark what Leo reports. Look inside them for another subject and predicate.',
          'Leo says [that Nora is inspecting the bridge].',
          '“Nora” is the subject inside the brackets. “Is inspecting the bridge” is its predicate. The word “that” starts this embedded clause, a clause inside a larger structure. The main clause begins with “Leo” and includes the whole report.');
        body.append(el('h3', 'What you’ll learn in this chapter'));
        const list = el('ul');
        for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
        body.append(list);
        break;
      }
      case 'concepts':
        p('A complementiser is a word that introduces a subordinate clause. “That” can introduce a statement, and “whether” can introduce a yes/no question. In the report below, find the reporting verb and then the clause that tells what was reported.');
        example('Leo says [that Nora is inspecting the bridge].');
        p('Compare “Leo spoke and Nora inspected the bridge”. Here “and” joins two clauses at the same level. Each describes a separate event.');
        p('A clause inside a report can hold another clause. Start with the innermost brackets in this example. Work outward from one report to the next.');
        example('Maya thinks [Leo said [Nora closed the gate]].');
        p('Start with what Nora did. Leo “said” she closed something. The group starting at “Leo” tells what Maya “thinks”. The main clause begins at “Maya” and holds both smaller reports.');
        break;
      case 'worked-example': {
        p('C labels the position for the complementiser. S labels the part with the subject and predicate. S′, read “S-bar”, groups C and S as one clause. To see why the tree needs both layers, start with the complete statement “Nora is inspecting the bridge”. “Nora” is the subject, and “is inspecting the bridge” is the predicate. In a tree, S is the node that groups that subject and predicate.');
        example('Leo says [that [Nora is inspecting the bridge]].');
        p('Now Leo is reporting that statement. Ask “What does Leo say?” The answer is the whole outer bracket, “that Nora is inspecting the bridge”. The inner bracket still contains the same subject and predicate, so it remains S.');
        p('In the report, the complementiser “that” fills C. Follow the two branches down from S′. One reaches “that” through C. The other reaches “Nora is inspecting the bridge” through S. Together they make the full embedded clause, which is the complement of “says”.');
        p('Compare “Leo says that Nora is inspecting the bridge” with “Leo says Nora is inspecting the bridge”. Both reports contain the same inner S. In the second, C is still drawn but has no spoken word. In “Nora is inspecting that bridge”, “that” instead helps identify which bridge, so it belongs inside the NP “that bridge”.');
        const overt = lesson.worked_example.tree;
        trace('Compare three ways to introduce an embedded clause', [
          ['Find overt “that”', overt, overt.root.children[0].id, '“That” fills C. C and S sit side by side under S′.'],
          ['Find the unfilled C', implicit, 'intro', '“Leo says Nora is inspecting the bridge” keeps the same inner S. The C branch has no word.'],
          ['Find interrogative “whether”', whether, 'intro', 'In “Leo asked whether Nora was inspecting the bridge”, C contains “whether”. Inside S, the subject “Nora” comes before “was”.'],
        ]);
        example('Was Nora inspecting the bridge? · Leo asked [whether [Nora was inspecting the bridge]].');
        p('The first sentence asks a question directly, so “was” comes before “Nora”. The second tells what Leo asked. “Whether” introduces the yes/no question from C, and the inner S keeps “Nora” before “was”. When you compare the trees, locate the word in C first and then read the subject and predicate under S.');
        body.append(el('h3', repair.buildTitle));
        p('Drag a branch from S′ to C, or choose Guide me. Then select Check my tree.');
        addBranchExercise(body, ui, repair);
        break;
      }
      case 'clausal-subjects-and-objects':
        p('A clausal subject is a clause that fills the subject role. Extraposition places the clause later and uses “it” in the subject position. In the first example below, the bracketed S′ tells what surprised Mina. It is a clausal subject, so it sits inside the subject NP.');
        example('[That the latch jammed] surprised Mina.');
        p('You can move the subject clause to the end and fill the subject spot with dummy “it”. “It” fills the spot without naming anything. The clause at the end is an extraposed subject.');
        example('It surprised Mina [that the latch jammed].');
        p('Now look at what Mina noticed. The whole clause is the direct object of “noticed”.');
        example('Mina noticed [that the latch jammed].');
        trace('Compare three functions of the same clause', [
          ['Find the clausal subject', subject, 'clausal-np', 'The subject NP contains S′. It is a sister of the predicate VP under main S.'],
          ['Find the extraposed subject', extraposed, 'embedded', 'Dummy “it” fills the subject NP. The extraposed S′ attaches directly under the main S.'],
          ['Find the clausal object', object, 'clausal-np', 'The object NP contains S′ and attaches beside V inside the main VP.'],
        ]);
        break;
      case 'clausal-complements':
        p('A clausal complement fills a role made available by a head. That head can be a verb (V), an adjective (A), a noun (N), or a preposition (P). Keep the same event in mind: the latch jammed. Now change how the sentence presents the event. An adjective can describe someone’s reaction to it, a noun can name a claim about it, and a preposition can introduce a question about it. Find the head word in each example before you decide where the clause attaches.');
        example('Certain [that the latch jammed] · the claim [that the latch jammed] · about [whether the latch jammed]');
        p('Put the fragments back into sentences. “Mina was certain that the latch jammed” tells what she was certain about. “Mina checked the claim that the latch jammed” tells what the claim said. “Mina asked about whether the latch jammed” puts the question after the preposition “about”. The bracketed clause joins the head word whose meaning it completes in each construction.');
        trace('Find the host of each clausal complement', [
          ['Trace the adjective', adjective, 'embedded', 'S′ completes “certain”. A and S′ are sisters within AP.'],
          ['Trace the noun', noun, 'embedded', 'The clause gives the content of the claim. N and S′ are sisters within NOM.'],
          ['Trace the preposition', preposition, 'embedded', '“Whether the latch jammed” is the complement of “about”. P and S′ are sisters within PP.'],
        ]);
        p('A clause can also be a subject predicative. In “The question is whether the latch jammed”, the clause tells what the question is. S′ sits right beside “is” inside VP.');
        break;
      case 'adverbial-clauses': {
        p('An adverbial clause contributes information such as time or reason. In the first example, the time word “after” is a preposition, so its node is P. It takes a clause as its complement inside PP.');
        example('Mina waited [after the gate closed].');
        example('Mina waited [because the gate jammed].');
        p('Here, “after” tells when something happened. It is a preposition that takes S as its complement. Together they make a PP. “Because” is a subordinating conjunction. It fills C and introduces an adverbial clause that tells why something happened.');
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
        p('Some adverbial clauses go with the whole statement. In “In case there is any doubt, the gate is locked”, the first clause tells why the speaker says the gate is locked.');
        break;
      }
      case 'application': {
        p('Find what Ria heard. Then find the question inside that report. Choose the two words that start the embedded clauses.');
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
        p('Find the main clause, then mark every word in each embedded clause. In a report, S′ groups C and S. C can hold “that” or “whether”. It can also be empty, as in “Leo says Nora is inspecting the bridge”.');
        p('Ask what the clause does. The clause about the latch can tell what surprised Mina or what she noticed. It can also give the content of a noun, as in “the claim that the latch jammed”.');
        p('For a time or reason expression, start with the first word. “After” can head a PP that contains S. “Because” fills C in an adverbial S′.');
        break;
    }
  },
};
