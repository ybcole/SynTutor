import { addIntroExample, addTreeTrace, lessonExample } from './lesson-presentation.js';
import { addBranchExercise } from './lesson-tree-exercise.js';

const node = (id, label, ...children) => ({ id, label, children });
const leaf = (id, label, word) => node(id, label, { word });
const triangle = (id, label, text) => ({ id, label, triangle: true, words: text.split(' ') });
const det = (category, word) => node('det', 'DET', leaf('determiner', category, word));
const noun = word => leaf('noun', 'N', word);
const ap = word => node(word, 'AP', leaf(`${word}-head`, 'A', word));
const phrase = (sentence, ...children) => ({ sentence, root: node('np', 'NP', ...children) });

const baskets = noun('baskets');
const simpleNom = node('nom', 'NOM', baskets);
const bare = phrase('baskets', { id: 'det', label: 'DET', empty: true }, simpleNom);
const article = phrase('the baskets', det('ART', 'the'), simpleNom);
const pronoun = phrase('they', leaf('pronoun', 'pronoun', 'they'));
const predet = phrase('all those baskets', leaf('all', 'PRE-DET', 'all'),
  node('inner-np', 'NP', det('DEM', 'those'), simpleNom));

const kite = phrase('a new red kite', det('ART', 'a'),
  node('outer', 'NOM', ap('new'), node('inner', 'NOM', ap('red'), noun('kite'))));
const crates = phrase('the wooden crates from Cebu', det('ART', 'the'),
  node('outer', 'NOM', node('inner', 'NOM', ap('wooden'), noun('crates')), triangle('origin', 'PP', 'from Cebu')));
const applicant = phrase('the eager applicant for the job', det('ART', 'the'),
  node('outer', 'NOM', ap('eager'), node('inner', 'NOM', noun('applicant'), triangle('job', 'PP', 'for the job'))));
const someone = phrase('someone from Vigan', leaf('pronoun', 'pronoun', 'someone'), triangle('origin', 'PP', 'from Vigan'));

const coreLabels = ['NP', 'DET', 'NOM', 'N'];
const repair = {
  buildTitle: 'Attach the nominal under NP',
  build: {
    branch: root => [root, root.children[1]],
    action: 'Connect NOM directly under NP',
    hint: 'Attach NOM to NP so it shares a parent with DET.',
    success: 'DET and NOM share NP as their parent. “Lanterns” stays under N within NOM.',
  },
};

export const nounPhrasesPilot = {
  description: 'Open up a noun phrase to find its determiner, noun and modifiers. Compare empty determiners and see how the meaning of a modifier guides its attachment.',
  references: [
    'Chapter 7, printed pp. 141–144, [1–7], [10], [12], [14] · Basic NP and determiner choices',
    'Printed pp. 145–149, [18], [25–28], [32], [36] · Pre-determiners and modifiers before the noun',
    'Printed pp. 150–155, [39a], [A–B], [65–67] · Modifiers after the noun and their scope',
    'Printed pp. 155–156, [72a–b] · Modified indefinite pronouns',
  ],
  sections: [
    { id: 'introduction', title: 'What is inside a noun phrase?' },
    { id: 'concepts', title: 'Find DET and NOM', notationLabels: [...coreLabels, 'ART', 'DEM', 'pronoun'] },
    { id: 'worked-example', title: 'Build the basic NP', notationLabels: [...coreLabels, 'DEM', 'PRE-DET'] },
    { id: 'pre-modifiers', title: 'Add modifiers inside NOM', notationLabels: [...coreLabels, 'ART', 'AP', 'A'] },
    { id: 'post-modifiers', title: 'Compare modifier attachments', notationLabels: [...coreLabels, 'ART', 'AP', 'A', 'PP', '△'] },
    { id: 'application', title: 'Apply the distinction', notationLabels: ['NP', 'pronoun', 'PP', '△'] },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Determiner (DET)', 'The position for words such as “the”, “those”, “some” and “my”. They help indicate which things or how many are meant.'],
    ['Nominal (NOM)', 'The layer within a noun phrase that contains the head noun and its modifiers.'],
    ['Pre-determiner (PRE-DET)', 'An element such as “all” or “both” that can come before a determiner and combines with a full NP.'],
    ['Pre-modifier', 'A modifier that comes before the head it modifies.'],
    ['Post-modifier', 'A modifier that comes after the head it modifies.'],
    ['Indefinite pronoun', 'A pronoun such as “someone” or “anyone” that refers without naming a specific person or thing.'],
  ],
  teach(body, _page, ui) {
    const { el, lesson, section } = ui;
    const p = text => body.append(el('p', text));
    const example = text => body.append(lessonExample(el, text));
    const trace = (label, steps) => addTreeTrace(body, ui, label, steps);

    switch (section.id) {
      case 'introduction': {
        p('Earlier trees used a triangle to show where a noun phrase (NP) fits. Now look inside the NP. The head noun names the kind of thing the phrase is about. The nominal (NOM) contains that noun and any modifiers of it. The determiner position (DET) can hold a word that helps specify which things or how many are meant.');
        addIntroExample(body, el, 'Imagine someone pointing to a group of baskets. The brackets mark the two parts of the NP.',
          '[Those] [baskets]',
          '“Those” fills DET and points out the baskets. “Baskets” is the head noun and fills NOM by itself.');
        body.append(el('h3', 'What you’ll see in this chapter'));
        const list = el('ul');
        for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
        body.append(list);
        break;
      }
      case 'concepts': {
        p('The determiner can change while the nominal stays the same. Compare the article “the”, the demonstrative “those”, the quantifier “some” and the possessive “my”. Each occupies the same DET position in these examples.');
        example('The baskets · those baskets · some baskets · my baskets');
        p('DET can also be empty. In “Baskets were stacked by the door”, the subject is a bare plural NP. It could take “the”, so the tree keeps a DET branch with no word. A mass noun such as “sand” can also occur with empty DET.');
        trace('Compare three ways to build an NP', [
          ['Find the article', article, 'determiner', '“The” is ART under DET. The noun remains under NOM.'],
          ['Find empty DET', bare, 'det', 'The DET branch ends without a word. NOM still contains “baskets”.'],
          ['Compare the pronoun', pronoun, 'pronoun', '“They” forms an NP on its own, as a name such as “Mina” can. Its tree has a single branch from NP.'],
        ]);
        p('A possessive can be longer than one word. In “the maker’s baskets”, the NP “the maker” and the possessive ending form the determiner of “baskets”.');
        break;
      }
      case 'worked-example': {
        p('Use the same split for another demonstrative phrase. “Those” is DEM under DET. Keep the noun “lanterns” under NOM.');
        example('[Those] [lanterns]');
        body.append(el('h3', repair.buildTitle));
        p('Attach the detached NOM to the whole NP. Drag from the parent’s connection point, or use Guide me. Then select Check my tree.');
        addBranchExercise(body, ui, repair);
        p('A pre-determiner can come before a determiner. In the example below, “all” combines with the whole NP “those baskets”. The demonstrative “those” still fills DET inside that group.');
        example('[All] [those baskets]');
        trace('Trace the pre-determiner and the NP it joins', [
          ['Find PRE-DET', predet, 'all', '“All” is the pre-determiner. It attaches at the level of the larger NP.'],
          ['Read the inner NP', predet, 'inner-np', '“Those baskets” is the sister of PRE-DET. Its DET and NOM stay together.'],
        ]);
        break;
      }
      case 'pre-modifiers':
        p('A pre-modifier comes before the head. In this example, start with “red kite”. The adjective phrase “red” and the noun form a nominal. Then “new” modifies that whole group, creating a larger NOM.');
        example('A [new [red kite]]');
        trace('Build the two nominal layers', [
          ['Read the smaller NOM', kite, 'inner', '“Red kite” is the smaller nominal. “Red” is an AP beside N.'],
          ['Read the larger NOM', kite, 'outer', '“New” is an AP beside the smaller NOM “red kite”. Both are under the larger NOM.'],
        ]);
        p('Other categories can occur before the noun. In “those two kites”, the numeral “two” is a quantifying adjective (QA). In “the sleeping child”, “sleeping” heads a participle phrase (PartP). In “the paper kite”, “paper” and “kite” form a compound under N.');
        break;
      case 'post-modifiers':
        p('A post-modifier follows the noun. To place it in a tree, ask which words it goes with. Suppose “wooden crates” names a kind of crate and Cebu is where those crates came from. The PP “from Cebu” joins the smaller nominal “wooden crates”.');
        example('The [[wooden crates] from Cebu]');
        p('Now suppose an applicant is eager and the application is for a particular job. “For the job” goes with “applicant”. The AP “eager” then modifies that smaller nominal.');
        example('The [eager [applicant for the job]]');
        trace('Compare the two modifier attachments', [
          ['Trace “wooden crates”', crates, 'inner', 'The smaller NOM includes the adjective and noun. The origin PP joins that whole NOM.'],
          ['Trace “applicant for the job”', applicant, 'inner', 'The smaller NOM includes the noun and PP. The AP “eager” joins that whole NOM.'],
        ]);
        p('An adjective phrase with its own complement can also follow the noun. In “the pilot ready for departure”, “ready for departure” is the whole AP.');
        break;
      case 'application': {
        p('Suppose “ceramic bowls” names a kind of bowl and Vigan is their place of origin. Which group does the origin PP join?');
        example('Those ceramic bowls from Vigan');
        const check = el('details', undefined, 'lesson-sources');
        check.append(el('summary', 'Check the attachment'),
          el('p', '“Ceramic bowls” forms the smaller NOM. The PP “from Vigan” joins that NOM under a larger one. “Those” stays in DET.'));
        body.append(check);
        p('Compare an indefinite pronoun, which refers without naming a particular person. “Someone” can form an NP on its own. If a PP modifies it in the next example, both the pronoun and the PP attach directly under NP.');
        example('Someone [from Vigan]');
        trace('Compare a plain and a modified pronoun', [
          ['Read the plain pronoun', pronoun, 'pronoun', 'The pronoun “they” forms a complete NP by itself.'],
          ['Read the modified pronoun', someone, 'origin', 'In “someone from Vigan”, the pronoun and PP are sisters under NP.'],
        ]);
        break;
      }
      case 'recap':
        p('Find the head noun, then split a basic NP into DET and NOM. A bare plural can have empty DET, as “baskets” does. In “all those baskets”, the pre-determiner “all” joins the full inner NP.');
        p('Inside NOM, use the intended meaning to find the smaller group first. “From Cebu” can join the whole nominal “wooden crates”. In “the eager applicant for the job”, the job phrase groups first with “applicant”.');
        p('If an indefinite pronoun has a modifier, check the NP directly. In “someone from Vigan”, the PP joins the pronoun under NP.');
        break;
    }
  },
};
