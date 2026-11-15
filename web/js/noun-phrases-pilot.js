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
const map = phrase('a map of the island with a red border', det('ART', 'a'),
  node('outer', 'NOM',
    node('inner', 'NOM', noun('map'), triangle('content', 'PP', 'of the island')),
    triangle('border', 'PP', 'with a red border')));
const one = phrase('one with a red border', { id: 'det', label: 'DET', empty: true },
  node('nom', 'NOM', { word: 'one' }, triangle('border', 'PP', 'with a red border')));

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
    'Printed pp. 165–170, appendix [14–20] · One as a pro-form for NOM and the complement–adjunct distinction',
  ],
  sections: [
    { id: 'introduction', title: 'What is inside a noun phrase?' },
    { id: 'concepts', title: 'Determiners and pre-determiners', notationLabels: [...coreLabels, 'ART', 'DEM', 'pronoun'] },
    { id: 'worked-example', title: 'Build the basic NP', notationLabels: [...coreLabels, 'DEM', 'PRE-DET'] },
    { id: 'pre-modifiers', title: 'Add modifiers inside NOM', notationLabels: [...coreLabels, 'ART', 'AP', 'A'] },
    { id: 'post-modifiers', title: 'NOM layers and post-modifiers', notationLabels: [...coreLabels, 'ART', 'AP', 'A', 'PP', '△'] },
    { id: 'application', title: 'Apply the distinction', notationLabels: ['NP', 'pronoun', 'PP', '△'] },
    { id: 'nom-appendix', title: 'Appendix: Test NOM with one', notationLabels: [...coreLabels, 'ART', 'PP', '△'] },
    { id: 'recap', title: 'Chapter recap', references: true },
    { id: 'closing-check', title: 'Check what you learned', assessment: true },
  ],
  keyTerms: [
    ['Determiner (DET)', 'The place for words like “the”, “those”, “some”, and “my”. These words help tell which things or how many.'],
    ['Nominal (NOM)', 'The part of an NP that holds the head noun and its modifiers.'],
    ['Pre-determiner (PRE-DET)', 'A word such as “all” or “both” that can come before a determiner. It goes with the whole NP.'],
    ['Pre-modifier', 'A modifier that comes before the head it describes.'],
    ['Post-modifier', 'A modifier that comes after the head it describes.'],
    ['Indefinite pronoun', 'A pronoun such as “someone” that refers to a person or thing without saying exactly who or what.'],
  ],
  teach(body, _page, ui) {
    const { el, lesson, section } = ui;
    const p = text => body.append(el('p', text));
    const example = text => body.append(lessonExample(el, text));
    const trace = (label, steps) => addTreeTrace(body, ui, label, steps);

    switch (section.id) {
      case 'introduction': {
        p('Earlier trees often used a triangle to stand for a whole noun phrase (NP). Now open up that triangle. Think about “those baskets” and “my baskets”. Both are about baskets, but the first word helps you work out which ones. In this chapter, you’ll see where that word goes and how other words add detail to the noun.');
        addIntroExample(body, el, 'Imagine someone pointing at baskets. The brackets mark the two parts of the phrase they use.',
          '[Those] [baskets]',
          '“Those” tells which baskets. It fills the determiner position (DET). “Baskets” is the head noun. It fills the nominal (NOM) on its own here. If you add a word like “woven”, it goes with “baskets” inside NOM.');
        body.append(el('h3', 'What you’ll see in this chapter'));
        const list = el('ul');
        for (const outcome of lesson.outcomes) list.append(el('li', outcome.text));
        body.append(list);
        break;
      }
      case 'concepts': {
        p('Keep “baskets” and change the first word. “The” is an article, “those” is a demonstrative, “some” is a quantifier, and “my” is a possessive. Each fills DET here. The nominal stays the same.');
        example('The baskets · those baskets · some baskets · my baskets');
        p('Sometimes no word fills DET. “Baskets” is a bare plural NP in “Baskets were stacked by the door”. You could say “the baskets”. The tree shows an empty DET in the bare plural. A mass noun like “sand” can also have empty DET.');
        trace('Compare three ways to build an NP', [
          ['Find the article', article, 'determiner', '“The” is ART under DET. The noun remains under NOM.'],
          ['Find empty DET', bare, 'det', 'The DET branch ends without a word. NOM still contains “baskets”.'],
          ['Compare the pronoun', pronoun, 'pronoun', '“They” forms an NP on its own, as a name such as “Mina” can. Its tree has a single branch from NP.'],
        ]);
        p('A possessive can have several words. In “the maker’s baskets”, start with the NP “the maker”. It joins the possessive ending to make the determiner for “baskets”.');
        break;
      }
      case 'worked-example': {
        p('Try the same split with “those lanterns”. “Those” is a demonstrative (DEM) under DET. “Lanterns” goes under NOM.');
        example('[Those] [lanterns]');
        body.append(el('h3', repair.buildTitle));
        p('Attach NOM to the whole NP. Drag from the NP’s connection point or choose Guide me. Then select Check my tree.');
        addBranchExercise(body, ui, repair);
        p('A pre-determiner can come before a determiner. Here, “all” goes with the whole NP “those baskets”. Inside that NP, “those” still fills DET.');
        example('[All] [those baskets]');
        trace('Trace the pre-determiner and the NP it joins', [
          ['Find PRE-DET', predet, 'all', '“All” is the pre-determiner. It attaches at the level of the larger NP.'],
          ['Read the inner NP', predet, 'inner-np', '“Those baskets” is the sister of PRE-DET. Its DET and NOM stay together.'],
        ]);
        break;
      }
      case 'pre-modifiers':
        p('A pre-modifier goes before the head. Group “red” and “kite” first. The AP “red” and the noun “kite” make a NOM. Then “new” goes with all of “red kite”. Now you have a larger NOM.');
        example('A [new [red kite]]');
        trace('Build the two nominal layers', [
          ['Read the smaller NOM', kite, 'inner', '“Red kite” is the smaller nominal. “Red” is an AP beside N.'],
          ['Read the larger NOM', kite, 'outer', '“New” is an AP beside the smaller NOM “red kite”. Both are under the larger NOM.'],
        ]);
        p('Look at three other words that come before a noun. In “those two kites”, “two” is a quantifying adjective (QA). In “the sleeping child”, “sleeping” heads a participle phrase (PartP). In “the paper kite”, “paper” and “kite” make a compound under N.');
        break;
      case 'post-modifiers':
        p('A post-modifier goes after the noun. Ask what it describes. Suppose the crates are made of wood and came from Cebu. The PP “from Cebu” goes with the whole nominal “wooden crates”.');
        example('The [[wooden crates] from Cebu]');
        p('Now picture an eager person applying for a job. “For the job” goes with “applicant”. The AP “eager” goes with that whole smaller group.');
        example('The [eager [applicant for the job]]');
        trace('Compare the two modifier attachments', [
          ['Trace “wooden crates”', crates, 'inner', 'The smaller NOM includes the adjective and noun. The origin PP joins that whole NOM.'],
          ['Trace “applicant for the job”', applicant, 'inner', 'The smaller NOM includes the noun and PP. The AP “eager” joins that whole NOM.'],
        ]);
        p('An AP can follow a noun when it has a complement of its own. In “the pilot ready for departure”, the whole AP is “ready for departure”.');
        break;
      case 'application': {
        p('The bowls are ceramic and they came from Vigan. Which group does the PP “from Vigan” go with?');
        example('Those ceramic bowls from Vigan');
        const check = el('details', undefined, 'lesson-sources');
        check.append(el('summary', 'Check the attachment'),
          el('p', '“Ceramic bowls” forms the smaller NOM. The PP “from Vigan” joins that NOM under a larger one. “Those” stays in DET.'));
        body.append(check);
        p('An indefinite pronoun can refer to a person without saying who it is. “Someone” can be a whole NP on its own. When you add the PP in the next example, the pronoun and PP both sit right under NP.');
        example('Someone [from Vigan]');
        trace('Compare a plain and a modified pronoun', [
          ['Read the plain pronoun', pronoun, 'pronoun', 'The pronoun “they” forms a complete NP by itself.'],
          ['Read the modified pronoun', someone, 'origin', 'In “someone from Vigan”, the pronoun and PP are sisters under NP.'],
        ]);
        break;
      }
      case 'recap':
        p('Find the head noun. Then look for DET and NOM. In the bare plural “baskets”, DET is empty. In “all those baskets”, the pre-determiner “all” goes with the whole NP “those baskets”.');
        p('Use the meaning to decide which words group first. “From Cebu” can go with “wooden crates”. In “the eager applicant for the job”, “for the job” goes with “applicant” first.');
        p('An indefinite pronoun can have a modifier. In “someone from Vigan”, “someone” and the PP “from Vigan” both sit right under NP.');
        p('Try one or ones to see which words form a NOM. A noun complement stays inside the NOM that the pro-form replaces. An adjunct can stay outside and describe the pro-form.');
        break;
      case 'nom-appendix':
        p('Suppose two maps show the same island. If one map has a red border, you can ask for “one with a red border”. Follow which words one replaces and which remain.');
        trace('Compare a noun complement and a NOM modifier', [
          ['Find the noun complement', map, 'content', '“Of the island” tells what the map depicts. It attaches beside N inside the smaller NOM.'],
          ['Find the modifier', map, 'border', '“With a red border” describes the map as an added detail. It attaches beside the smaller NOM.'],
          ['Replace the smaller NOM', one, 'nom', '“One” stands for “map of the island”, including the complement. Under the appendix convention, the pro-form is written directly under NOM and the border PP stays next to it.'],
        ]);
        break;
    }
  },
};
