import { addIntroExample, addTreeTrace, lessonExample } from './lesson-presentation.js';
import { addBranchExercise } from './lesson-tree-exercise.js';

const node = (id, label, ...children) => ({ id, label, children });
const group = (id, label, text) => ({ id, label, triangle: true, words: text.split(' ') });
const verb = (word, ...features) => ({ ...node('verb', 'V', { word }), features });
const aux = (id, label, word, ...features) => ({ ...node(id, label, { word }), features });
const vp = (level, ...children) => node(`vp${level}`, 'VP', ...children);
const gap = id => ({ id, gap: true });
const vacated = (id, label, ...features) => ({ ...node(id, label, gap(`${id}-gap`)), features });
const negative = (id, label, word) => ({ ...group(id, label, word), features: ['past'] });

// Each auxiliary heads its own VP and takes the next VP as its complement.
const studying = {
  sentence: 'Monsieur Blanc is studying the menu',
  root: node('sentence', 'S', group('subject', 'NP', 'Monsieur Blanc'),
    vp(1, aux('progressive', 'PROG', 'is', 'pres'), vp(2, verb('studying', 'trans'), group('object', 'NP', 'the menu')))),
};

const chain = {
  sentence: 'Mara should have packed the lantern',
  root: node('sentence', 'S', group('subject', 'NP', 'Mara'),
    vp(1, aux('modal', 'MOD', 'should', 'past'),
      vp(2, aux('perfect', 'PERF', 'have'),
        vp(3, verb('packed', 'trans'), group('object', 'NP', 'the lantern'))))),
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
    vp(1, negative('negation', 'MOD', 'would not'), vp(2, verb('dance', 'intrans')))),
};

const did = {
  sentence: 'Byron did not dance',
  root: node('sentence', 'S', group('subject', 'NP', 'Byron'),
    vp(1, negative('support', 'TENSE', 'did not'), vp(2, verb('dance', 'intrans')))),
};

const dancing = {
  sentence: 'Was Byron dancing',
  root: node('sentence', 'S-bar', node('complementiser', 'C', { word: 'was' }),
    node('clause', 'S', group('subject', 'NP', 'Byron'),
      vp(1, vacated('progressive', 'PROG', 'past'), vp(2, verb('dancing', 'intrans'))))),
};

const dances = {
  sentence: 'Does Byron dance',
  root: node('sentence', 'S-bar', node('complementiser', 'C', { word: 'does' }),
    node('clause', 'S', group('subject', 'NP', 'Byron'),
      vp(1, vacated('tense', 'TENSE', 'pres'), vp(2, verb('dance', 'intrans'))))),
};

const kubla = {
  sentence: 'Was Kubla extravagant',
  root: node('sentence', 'S-bar', node('complementiser', 'C', { word: 'was' }),
    node('clause', 'S', group('subject', 'NP', 'Kubla'),
      node('predicate', 'VP', vacated('verb', 'V', 'intens', 'past'), group('description', 'AP', 'extravagant')))),
};

const active = {
  sentence: 'The curator moved the statue',
  root: node('sentence', 'S', group('subject', 'NP', 'The curator'),
    vp(1, { ...verb('moved', 'trans'), features: ['trans', 'past'] }, group('object', 'NP', 'the statue'))),
};
const passive = {
  sentence: 'The statue was moved by the curator',
  root: node('sentence', 'S', group('subject', 'NP', 'The statue'),
    vp(1, aux('passive', 'PASS', 'was', 'past'),
      vp(2, vp(3, verb('moved', 'trans'), node('object', 'NP', gap('object-gap'))),
        group('agent', 'PP', 'by the curator')))),
};
const passiveQuestion = {
  sentence: 'Was the parcel delivered',
  root: node('sentence', 'S-bar', node('complementiser', 'C', { word: 'was' }),
    node('clause', 'S', group('subject', 'NP', 'the parcel'),
      vp(1, vacated('passive', 'PASS', 'past'),
        vp(2, verb('delivered', 'trans'), node('object', 'NP', gap('object-gap')))))),
};

const baseLabels = ['S', 'NP', 'VP', 'V', '△'];
const repair = {
  buildTitle: 'Nest the auxiliary VPs',
  build: {
    branch: root => [root.children[1], root.children[1].children[1]],
    action: 'Connect the lower VP under the auxiliary VP',
    hint: 'Attach “have packed the lantern” under the VP headed by MOD “should”. Only the first verb is tensed.',
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
    { id: 'concepts', title: 'Each auxiliary heads a VP', notationLabels: [...baseLabels, 'PROG', 'MOD', 'PERF'], notationFeatures: ['trans', 'pres', 'past'] },
    { id: 'chain', title: 'Follow the chain of VPs', notationLabels: [...baseLabels, 'MOD', 'PERF'], notationFeatures: ['past', 'trans'] },
    { id: 'adverbials', title: 'Place adverbials in the chain', notationLabels: [...baseLabels, 'MOD', 'PERF', 'PROG', 'AdvP', 'PP'], notationFeatures: ['past', 'pres', 'trans', 'intrans'] },
    { id: 'passive', title: 'Follow the object in a passive', notationLabels: [...baseLabels, 'PASS', 'PP', '•'], notationFeatures: ['past', 'trans'] },
    { id: 'negation', title: 'Negate with an auxiliary or with do', notationLabels: [...baseLabels, 'MOD', 'TENSE'], notationFeatures: ['past', 'intrans'] },
    { id: 'questions', title: 'Front the tense-carrying element', notationLabels: [...baseLabels, 'PROG', 'PASS', 'TENSE', 'C', 'S-bar', 'AP', '•'], notationFeatures: ['past', 'pres', 'intrans', 'intens', 'trans'] },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Auxiliary verb', 'A helping verb, such as a modal or a form of “be” or “have”. It heads its own VP. The next VP is its complement.'],
    ['Modal auxiliary (MOD)', 'A helping verb such as “can”, “could”, “might”, or “should”. It comes first in the chain and carries tense.'],
    ['Perfect auxiliary (PERF)', 'A form of “have” that comes before a past participle, as in “has studied”.'],
    ['Progressive auxiliary (PROG)', 'A form of “be” that comes before an -ing verb, as in “is studying”.'],
    ['Passive auxiliary (PASS)', 'A form of “be” that comes before a passive participle, as in “was moved”. The passive subject is often the object in the matching active sentence.'],
    ['Tense feature', 'A mark such as [pres] or [past]. In a verb chain, only the first verb carries tense.'],
    ['Do-support', 'Using “do” when a verb like “dance” needs help to form a question or a negative. In “did not dance”, “did” carries past tense under TENSE.'],
    ['Fronting', 'Moving a word or group to the front. In a yes/no question, the verb that carries tense moves to C and leaves a gap.'],
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
      p('A verb phrase can have more than one verb. Compare “studies” with “is studying”. Both describe studying, and “is” helps show that the action is in progress. This chapter looks at how helping verbs fit into a tree and how they help form questions and negative statements.');
      addIntroExample(body, el, 'In the sentence below, the first brackets mark the helping verb. The second mark the group that tells what Monsieur Blanc is doing.',
        'Monsieur Blanc [is] [studying the menu].',
        '“Is” is a helping verb called a progressive auxiliary. It heads its own VP. The lexical VP “studying the menu” is its complement. Only “is” carries tense here. You’ll follow the same pattern when there is more than one auxiliary.');
      heading('What you’ll see in this chapter');
      const list = el('ul');
      for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
      body.append(list);
    }
    if (section.id === 'concepts') {
      p('Find the lexical verb at the end of the chain. It heads the innermost VP, which holds any complements of that verb. Work back from there. Each auxiliary heads a bigger VP that holds the one you just found.');
      example('Mara [should] [have] [packed the lantern].');
      const feedback = status();
      body.append(practiceQuestion('chain-heads', 'In “should have packed the lantern”, which verb carries tense?', [
        'should', 'packed',
      ], answer => {
        feedback.className = `lesson-feedback ${answer === '0' ? 'correct' : 'retry'}`;
        feedback.textContent = answer === '0'
          ? '“Should” carries tense and heads the highest VP.'
          : '“Packed” heads the lowest VP. It is a participle here. The modal “should” carries tense.';
      }), feedback);
      trace('Separate the auxiliary from the verb group', [
        ['Find the progressive auxiliary', studying, 'progressive', 'PROG “is” heads the outer VP. It is tense-marked [pres] and takes a VP complement.'],
        ['Find the lexical VP', studying, 'vp2', 'The inner VP “studying the menu” is headed by V [trans] and holds the object NP.'],
      ]);
      heading(repair.buildTitle);
      p('One branch is missing from the tree. Connect “have packed the lantern” to the VP headed by “should”. Drag from that parent node or choose Guide me. Then select Check my tree.');
      addBranchExercise(body, ui, repair);
    }
    if (section.id === 'chain') {
      p('Count the auxiliaries in “should have packed”. “Should” and “have” each head a VP. “Packed” heads the lexical VP inside them. That makes three VPs. Only the first verb carries tense.');
      example('Mara [should] [have] [packed the lantern].');
      p('Follow the steps to see how each VP fits inside the one above it.');
      trace('Trace each auxiliary layer', [
        ['Find MOD', chain, 'modal', 'MOD “should” [past] is the highest verb. It is the only tensed verb in the sequence.'],
        ['Find PERF', chain, 'perfect', 'PERF “have” heads the next VP. It is untensed and takes the lexical VP as its complement.'],
        ['Find the lexical VP', chain, 'vp3', 'V [trans] “packed” heads the lowest VP with the object NP “the lantern”.'],
        ['Read the whole chain', chain, 'vp1', 'Each auxiliary heads a VP that holds the next one. Only the first verb, “should”, carries tense.'],
      ]);
      p('Read the possible slots in order. Modal (MOD) comes first, then perfect (PERF), progressive (PROG), and passive (PASS). The lexical verb comes last. A sentence can skip any auxiliary slot it does not need.');
      p('Look at the verb right after each auxiliary. A modal takes the plain verb form, as in “might write”. Perfect “have” takes a past participle, as in “has written”. Progressive “be” takes an -ing form, as in “is writing”. Passive “be” takes a passive participle, as in “was written”.');
    }
    if (section.id === 'adverbials') {
      p('Look for which VP an adverbial goes with. In these examples, an adverbial before a verb goes with the following VP. One at the end usually goes with the lexical VP. Some time phrases at the end go with a higher VP.');
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
      p('In “They were going to India next week last week”, start with “next week”. It tells when the trip was set to happen and goes with the lexical VP. “Last week” tells when that plan held. It goes with the higher past-tense PROG VP. What a time phrase means can help you find its scope.');
    }
    if (section.id === 'passive') {
      p('Passive “be” heads its own VP. It takes another VP as its complement. Look for “the statue” in both sentences.');
      example('The curator moved [the statue].');
      example('[The statue] was moved by the curator.');
      p('“The statue” is the object in the active sentence and the subject in the passive sentence. A dot marks the empty object position in the passive tree. “Moved” still has [trans]. The optional “by” phrase tells who moved the statue.');
      trace('Compare the active object and passive gap', [
        ['Find the active object', active, 'object', '“The statue” is the object NP beside V in the active VP.'],
        ['Find the passive subject', passive, 'subject', '“The statue” is the subject NP. “Was” heads the higher VP as PASS [past].'],
        ['Find the object gap', passive, 'object-gap', 'The gap is under the object NP beside V [trans]. The “by” phrase joins the lexical VP at the next level.'],
      ]);
    }
    if (section.id === 'negation') {
      p('To make a sentence negative, put “not” after the first auxiliary. “Not” can shorten to “n’t”. In the tree it goes with the auxiliary that carries tense.');
      example('Byron [would] [not] [dance].');
      p('With a lexical verb like “dance”, English uses do-support if there is no auxiliary. In the tree, the TENSE node holds “do”. “Do” carries tense and goes with “not”. The lexical verb stays untensed.');
      example('Byron [did] [not] [dance].');
      trace('Compare an auxiliary and an empty do', [
        ['Mark the tensed MOD', would, 'negation', 'MOD “would” [past] heads the highest VP. “Not” attaches to it, and “dance” is an untensed lexical verb.'],
        ['Mark the empty do', did, 'support', 'No auxiliary is available, so an empty “do” under TENSE [past] carries the negation. V “dance” stays untensed.'],
      ]);
      p('Lexical “be” behaves like an auxiliary here. Use “be” itself in a negative sentence or a question.');
    }
    if (section.id === 'questions') {
      p('To make a yes/no question, move the word that carries tense in front of the subject. This is fronting. Put it under C and mark its old spot with a gap. An auxiliary or “be” can move there. If there is neither, use “do”. The lexical verb stays untensed.');
      example('Was Byron dancing?');
      example('Does Byron dance?');
      trace('Front an auxiliary and front do-support', [
        ['Front the auxiliary', dancing, 'complementiser', 'The tensed PROG “was” moves to C. The subject stays in S, and a gap marks the empty PROG position.'],
        ['Front the empty do', dances, 'complementiser', '“Do” from the TENSE node moves to C. The gap is under TENSE [pres]. The lexical verb “dance” stays in place and is untensed.'],
        ['Front as a copula', kubla, 'complementiser', 'With “be” the lexical verb itself moves to C. It leaves a gap under V and keeps “extravagant” as a subject predicative.'],
        ['Find the auxiliary gap in a passive question', passiveQuestion, 'passive-gap', '“Was” is under C. The higher gap marks its original position under PASS.'],
        ['Find the object gap in a passive question', passiveQuestion, 'object-gap', '“The parcel” is the subject of the passive. Its original object position remains marked under the lower VP.'],
      ]);
      p('C is the complementiser position. It holds the verb that moves to the front in these questions. The S′ layer, read “S-bar”, groups C with S.');
    }
    if (section.id === 'recap') {
      p('Start with the lexical VP. Then work outward. Each auxiliary heads its own VP and takes the next VP as its complement. Only the first verb carries tense.');
      p('Remember the order MOD, PERF, PROG, PASS. Look at what each adverbial goes with. An adverbial before a verb can go with the next VP. One at the end often goes with the lexical VP. Some final time phrases go with a higher VP that carries tense.');
      p('“Not” goes after the first auxiliary. Use do-support under TENSE if a verb like “dance” has no auxiliary. In a yes/no question, move the word that carries tense to C and leave a gap.');
    }
  },
};
