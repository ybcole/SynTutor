import { addIntroExample, addTreeTrace, lessonExample } from './lesson-presentation.js';
import { addBranchExercise } from './lesson-tree-exercise.js';

const node = (id, label, ...children) => ({ id, label, children });
const group = (id, label, text) => ({ id, label, triangle: true, words: text.split(' ') });
const verb = (word, ...features) => ({ ...node('verb', 'V', { word }), features });
const aux = (id, label, word, ...features) => ({ ...node(id, label, { word }), features });
const vp = (level, ...children) => ({ ...node(`vp${level}`, 'VP', ...children), ref: `VP${level}` });
const gap = id => node(id, 'PERF', { gap: true, symbol: '•' });

// Each auxiliary heads its own VP and takes the next VP as its complement.
const studying = {
  sentence: 'Monsieur Blanc is studying the menu',
  root: node('sentence', 'S', group('subject', 'NP', 'Monsieur Blanc'),
    vp(1, aux('progressive', 'PROG', 'is', 'pres'), vp(2, verb('studying', 'trans'), group('object', 'NP', 'the menu')))),
};

const chain = {
  sentence: 'You should have written an essay',
  root: node('sentence', 'S', group('subject', 'NP', 'You'),
    vp(1, aux('modal', 'MOD', 'should', 'past'),
      vp(2, aux('perfect', 'PERF', 'have'),
        vp(3, verb('written', 'trans'), group('object', 'NP', 'an essay'))))),
};

const hippo = {
  sentence: 'That hippo could easily have killed me',
  root: node('sentence', 'S', group('subject', 'NP', 'That hippo'),
    vp(1, aux('modal', 'MOD', 'could', 'past'),
      vp(2, group('ease', 'AdvP', 'easily'), vp(3, aux('perfect', 'PERF', 'have'),
        vp(4, verb('killed', 'trans'), group('object', 'NP', 'me')))))),
};

const they = {
  sentence: 'They have been complaining',
  root: node('sentence', 'S', group('subject', 'NP', 'They'),
    vp(1, aux('perfect', 'PERF', 'have', 'pres'),
      vp(2, aux('progressive', 'PROG', 'been'),
        vp(3, verb('complaining', 'intrans'))))),
};
const theyFull = {
  sentence: 'They have been complaining for the fun of it',
  root: node('sentence', 'S', group('subject', 'NP', 'They'),
    vp(1, aux('perfect', 'PERF', 'have', 'pres'),
      vp(2, aux('progressive', 'PROG', 'been'),
        vp(3, vp(4, verb('complaining', 'intrans')), group('fun', 'PP', 'for the fun of it'))))),
};

const would = {
  sentence: 'Byron would not dance',
  root: node('sentence', 'S', group('subject', 'NP', 'Byron'),
    vp(1, node('negation', 'MOD', { word: 'would not' }), vp(2, verb('dance', 'intrans')))),
};

const did = {
  sentence: 'Byron did not dance',
  root: node('sentence', 'S', group('subject', 'NP', 'Byron'),
    vp(1, node('tense', 'VP', aux('support', 'TENSE', 'did not', 'past'), vp(2, verb('dance', 'intrans'))))),
};

const dancing = {
  sentence: 'Was Byron dancing',
  root: node('sentence', 'S-bar', node('complementiser', 'C', { word: 'was' }),
    node('clause', 'S', group('subject', 'NP', 'Byron'),
      vp(1, gap('progressive'), vp(2, verb('dancing', 'intrans'))))),
};

const dances = {
  sentence: 'Does Byron dance',
  root: node('sentence', 'S-bar', node('complementiser', 'C', { word: 'does' }),
    node('clause', 'S', group('subject', 'NP', 'Byron'),
      vp(1, gap('tense'), vp(2, verb('dance', 'intrans'))))),
};

const kubla = {
  sentence: 'Was Kubla extravagant',
  root: node('sentence', 'S-bar', node('complementiser', 'C', { word: 'was' }),
    node('clause', 'S', group('subject', 'NP', 'Kubla'),
      node('predicate', 'VP', verb('was', 'intens', 'past'), group('description', 'AP', 'extravagant')))),
};

const baseLabels = ['S', 'NP', 'VP', 'V', '△'];
const repair = {
  buildTitle: 'Nest the auxiliary VPs',
  build: {
    branch: root => [root.children[1], root.children[1].children[1]],
    action: 'Connect the lower VP under the auxiliary VP',
    hint: 'Attach the PERF VP “have written an essay” under the MOD VP “should”. Only the first verb is tensed.',
    success: 'The MOD “should” heads its own VP and takes the PERF VP as its complement. Only “should” is tensed.',
  },
};

export const auxiliariesPilot = {
  description: 'See why each auxiliary is the head of its own verb phrase. Follow a chain of VPs, then read negation, do-support and questions in the same framework.',
  references: [
    'Chapter 6, printed pp. 111–122, figures [8–9], [24–42], [52–53] · Auxiliaries as heads',
    'Printed pp. 123–125, figures [62], [66], [69] · Adverbials inside auxiliary VPs',
    'Printed p. 127, figure [78] · Passive VPs and the agent by-phrase',
    'Printed pp. 129–132, figures [86], [88], [91], [93], [103] · Negation, do-support and questions',
  ],
  sections: [
    { id: 'introduction', title: 'How do auxiliary verbs fit in?' },
    { id: 'concepts', title: 'Each auxiliary heads a VP', notationLabels: ['S', 'NP', 'VP', 'V'], notationFeatures: ['trans', 'pres'] },
    { id: 'chain', title: 'Follow the chain of VPs', notationLabels: [...baseLabels, 'MOD', 'PERF'], notationFeatures: ['past', 'trans'] },
    { id: 'adverbials', title: 'Place adverbials in the chain', notationLabels: [...baseLabels, 'MOD', 'PERF', 'PROG', 'AdvP', 'PP'], notationFeatures: ['past', 'pres', 'trans', 'intrans'] },
    { id: 'negation', title: 'Negate with an auxiliary or with do', notationLabels: [...baseLabels, 'MOD', 'TENSE'], notationFeatures: ['past', 'intrans'] },
    { id: 'questions', title: 'Front the tense-carrying element', notationLabels: [...baseLabels, 'MOD', 'PROG', 'TENSE', 'C', 'S-bar', '•'], notationFeatures: ['past', 'pres'] },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Auxiliary verb', 'A helping verb such as a modal, a form of “be” or a form of “have”. Each auxiliary heads its own verb phrase and takes the next verb phrase as its complement.'],
    ['Modal auxiliary (MOD)', 'A modal such as “can”, “could”, “might” or “should”. It is always the first verb and carries the tense.'],
    ['Perfect auxiliary (PERF)', 'A form of “have” followed by a past participle, as in “has studied”.'],
    ['Progressive auxiliary (PROG)', 'A form of “be” followed by an -ing verb, as in “is studying”.'],
    ['Passive auxiliary (PASS)', 'A form of “be” followed by a past participle whose object has become the subject, as in “was fired”.'],
    ['Tense feature', 'The pres/past marker on a verb. In a sequence of verbs only the first verb is tensed.'],
    ['Do-support', 'The use of “do” under the TENSE node to carry tense and negation when no other auxiliary is present, as in “did not dance”.'],
    ['Fronting', 'Moving the tense-carrying element to the front position C to form a question, leaving a gap where it was.'],
  ],
  teach(body, _page, ui) {
    const { el, lesson, section, practiceQuestion } = ui;
    const p = text => body.append(el('p', text));
    const example = text => body.append(lessonExample(el, text));
    const heading = text => body.append(el('h3', text));
    const trace = (label, steps) => addTreeTrace(body, ui, label, steps);
    const status = () => {
      const feedback = el('p', undefined, 'lesson-feedback');
      feedback.setAttribute('role', 'status');
      return feedback;
    };

    if (section.id === 'introduction') {
      p('Chapter 4 grouped the lexical verb with its complements inside one VP. Auxiliary verbs add information such as tense, possibility, aspect or voice. Each auxiliary heads its own verb phrase and takes the following verb phrase as its complement. Chapter 6 shows how these layers stack.');
      addIntroExample(body, el, 'The brackets separate the auxiliary from the verb group it helps.',
        'Monsieur Blanc [is] [studying the menu].',
        '“Is” is a progressive auxiliary. It heads one VP and takes the lexical VP “studying the menu” as its complement. Only the first verb carries the tense feature.');
      heading('What you’ll see in this chapter');
      const list = el('ul');
      for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
      body.append(list);
    }
    if (section.id === 'concepts') {
      p('When several verbs appear in a row, each one up to the last is an auxiliary. Each auxiliary is the head of its own VP, and its complement is the next VP. The last VP is the lexical one: the verb plus its own complements.');
      example('You [should] [have] [written an essay].');
      const feedback = status();
      body.append(practiceQuestion('chain-heads', 'In “should have written an essay”, which verb heads the lowest VP?', [
        'should', 'written',
      ], answer => {
        feedback.className = `lesson-feedback ${answer === '1' ? 'correct' : 'retry'}`;
        feedback.textContent = answer === '0'
          ? 'Not quite. “Should” is the modal and heads the highest VP. The lowest VP is headed by the lexical verb.'
          : 'Yes. The lexical verb “written” heads the lowest VP “written an essay”. “Should” and “have” each head a higher VP.';
      }), feedback);
      trace('Separate the auxiliary from the verb group', [
        ['Find the progressive auxiliary', studying, 'progressive', 'PROG “is” heads the outer VP. It is tense-marked [pres] and takes a VP complement.'],
        ['Find the lexical VP', studying, 'vp2', 'The inner VP “studying the menu” is headed by V [trans] and holds the object NP.'],
      ]);
      heading(repair.buildTitle);
      p('The worked sentence “You should have written an essay” is seeded below. Connect the lower VP under the MOD VP headed by “should”. Drag from the parent’s connection point or use Guide me. Then select Check my tree.');
      addBranchExercise(body, ui, repair);
    }
    if (section.id === 'chain') {
      p('Count the auxiliaries to find how many VPs stack. In “should have written”, two auxiliaries give two auxiliary VPs above the lexical VP, for three layers in all. The tense feature sits only on the first.');
      example('You [should] [have] [written an essay].');
      p('Only the first verb is tensed. If you place the tense on “have” or “written”, the tree no longer matches the book’s convention.');
      trace('Trace each auxiliary layer', [
        ['Find MOD', chain, 'modal', 'MOD “should” [past] is the highest verb. It is the only tensed verb in the sequence.'],
        ['Find PERF', chain, 'perfect', 'PERF “have” heads the next VP. It is untensed and takes the lexical VP as its complement.'],
        ['Find the lexical VP', chain, 'vp3', 'V [trans] “written” heads the lowest VP with the object NP “an essay”.'],
        ['Read the whole chain', chain, 'vp1', 'Each auxiliary VP sits directly above the next. Only the highest VP is tensed.'],
      ]);
      p('A useful check: the highest VP groups the whole layered sequence, and every lower VP is the complement of the auxiliary VP just above it.');
    }
    if (section.id === 'adverbials') {
      p('Adverbials can appear inside the chain too. The book follows two working rules. An adverbial that comes before a verb modifies the following VP, the one just below it. A sentence-final adverbial modifies the lexical VP, unless it is a time adverbial that modifies a higher, tensed auxiliary VP.');
      example('That hippo [could] [easily] [have] [killed me].');
      trace('Place an adjunct inside the auxiliary chain', [
        ['Find the pre-verb adverbial', hippo, 'ease', 'The AdvP “easily” comes before “have”, so it attaches beside the PERF VP — the next VP below it.'],
        ['Find the perfect auxiliary', hippo, 'perfect', 'PERF “have” heads the VP that “easily” modifies. It takes the lexical VP as its complement.'],
      ]);
      example('They [have] [been] [complaining] [for the fun of it].');
      trace('Attach a sentence-final adjunct', [
        ['Attach the final PP', theyFull, 'fun', '“For the fun of it” is a sentence-final adverbial. It modifies the lexical VP “complaining”.'],
        ['Compare a bare lexical VP', they, 'vp3', 'Without the adverbial the lexical VP is just “complaining”. The PP is an optional adjunct here.'],
      ]);
      p('A time adverbial can behave differently. In “They were going to India next week last week”, the final “last week” modifies the higher past-tense PROG VP, while “next week” stays with the lexical VP. That exception shows why position alone does not decide scope.');
    }
    if (section.id === 'negation') {
      p('To negate a sentence, put “not” (often contracted to “n’t”) after the first auxiliary. The auxiliary carries the tense, so “not” has a tensed head to attach to.');
      example('Byron [would] [not] [dance].');
      p('If there is no auxiliary, English supplies one: an empty “do” under a TENSE node. The “do” carries tense and negation, and the lexical verb stays untensed.');
      example('Byron [did] [not] [dance].');
      trace('Compare an auxiliary and an empty do', [
        ['Mark the tensed MOD', would, 'negation', 'MOD “would” [past] heads the highest VP. “Not” attaches to it, and “dance” is an untensed lexical verb.'],
        ['Mark the empty do', did, 'support', 'No auxiliary is available, so an empty “do” under TENSE [past] carries the negation. V “dance” stays untensed.'],
      ]);
      p('“Be” is special. As a lexical verb it still behaves like an auxiliary, so negation and questions use “be” itself rather than do-support.');
    }
    if (section.id === 'questions') {
      p('A yes/no question fronts the tense-carrying element to the front position C. Where the element came from, a gap remains. If the sentence has an auxiliary or “be”, that word moves. If not, empty “do” moves and the lexical verb stays untensed.');
      example('Was Byron dancing?');
      example('Does Byron dance?');
      trace('Front an auxiliary and front do-support', [
        ['Front the auxiliary', dancing, 'complementiser', 'The tensed PROG “was” moves to C. The subject stays in S, and a gap marks the empty PROG position.'],
        ['Front the empty do', dances, 'complementiser', '“Do” from the TENSE node moves to C. The lexical V “dance” stays untensed with its own gap below the auxiliary.'],
        ['Front as a copula', kubla, 'complementiser', 'With “be” the lexical verb itself moves to C. It leaves a gap under V and keeps “extravagant” as a subject predicative.'],
      ]);
      p('C stands for complementiser, the front position where the question word or auxiliary lands. S′ (printed “S-bar”) is the layer that groups C with the smaller S.');
    }
    if (section.id === 'recap') {
      p('Start by counting the verbs. Each auxiliary is the head of its own VP and takes the next VP as complement, so a chain of auxiliaries stacks one VP above the next. Only the first verb carries the tense feature.');
      p('MOD comes before PERF, which comes before PROG, which comes before PASS. Place adverbials by their position and role: a pre-verb adverbial modifies the next VP, and a sentence-final adverbial attaches to the lexical VP unless a time adverbial modifies a higher, tensed auxiliary VP.');
      p('Negate by putting “not” after the first auxiliary, or use empty “do” under TENSE when no auxiliary is present. Questions front that same tense-carrier to C, leaving a gap behind.');
    }
  },
};
