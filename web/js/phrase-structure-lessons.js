import { addIntroExample, lessonExample } from './lesson-presentation.js';
import { advancedFoundationsChapters } from './advanced-foundations-lessons.js';
import { addWorkedExample } from './foundations-lesson.js';
import { addVisibleContrast, chapterPolishing } from './foundations-polishing.js';
import { addCombinationPractice, addWordPractice } from './foundations-practice.js';
import { addBranchExercise } from './lesson-tree-exercise.js';

const chapters = {
  'br-03': {
    topics: ['Adjective Phrases', 'Heads and Degree Words', 'Reading and Building an AP', 'Finding the Head in a New Phrase'],
    intro: 'Chapter 2 looked at the jobs that whole phrases do. This chapter looks inside one of those groups to see how its words work together.',
    exampleContext: 'In the example below, the brackets mark the description that follows “seemed”.',
    example: 'The children seemed [very cheerful].',
    introExample: 'An adjective phrase (AP) is a phrase built around an adjective. In “very cheerful”, the adjective “cheerful” supplies the description and “very” makes it stronger. An AP can also consist of the adjective alone, as the next page shows.',
    preview: ['Use the contrast between “cheerful” and “very cheerful” to find the head.', 'Show the head and degree word on the tree.', 'Use the same reasoning to analyse a new description.'],
    conceptLead: 'Use the bracketed description as a reference. Compare what happens when each word is removed.',
    concepts: [
      ['Find the head', 'First remove “very”. In “The children seemed cheerful”, “cheerful” still describes the children. The head is the central word that determines the category of a phrase. Here “cheerful” is the head, so the group is an adjective phrase. That category stays the same when “very” is removed.'],
      ['Check what the degree word adds', 'Now remove “cheerful” from the reference sentence. “The children seemed very” leaves the description unfinished. In this use, “very” needs a description to modify. A degree word tells how strongly a quality applies, so “very” modifies the degree of cheerfulness. Switching to “quite cheerful” changes the degree while keeping the same head.'],
      ['Read the labels', 'The labels separate the two words from the phrase they form. A labels the adjective “cheerful”, DEG labels “very”, and AP labels the whole description. In the tree, A and DEG are both directly under AP.'],
    ],
    contrast: ['Carry the comparison into the tree', ['With “very”, AP covers both words and has an A and a DEG branch.', 'Without “very”, AP covers “cheerful” alone and keeps the A branch. Compare those two trees on the next page.']],
    opening: [
      ['In “quite bright”, which word tells you the degree of brightness?', ['quite', 'bright', 'both words'], 0],
      ['In “very quiet”, which label stands for the whole adjective phrase?', ['A', 'AP', 'DEG'], 1],
    ],
    steps: ['Find the adjective head', null, 'Read the whole AP'],
    captions: [
      'Start with A. It covers “cheerful”, the word that describes the children.',
      null,
      'Now follow both branches to AP. It covers “very cheerful”, including the DEG branch that adjusts the description.',
    ],
    beforeTree: 'Use the tree to check the contrast from the previous page. Trace “cheerful” to A, then select AP to see the full group. Predict which branch will disappear and switch to Adjective on its own to check.',
    treeTakeaway: 'Both trees keep A as the head of AP. The longer tree adds DEG alongside A. Next, use that relationship to complete the longer tree yourself.',
    buildTitle: 'Connect the adjective head',
    build: {
      branch: root => [root, root.children[1]],
      prompt: 'The DEG branch is already attached. Connect A, the branch for “cheerful”, to the AP node so that the phrase includes both words.',
      action: 'Connect A under AP',
      hint: 'A and DEG should share AP as their parent. Keep “cheerful” under A.',
      success: 'A and DEG are sisters under AP. “Cheerful” is the adjective head.',
    },
    applyExample: 'The room looked quite bright.',
    apply: [
      ['Find the two roles', 'Apply the same reasoning to “quite bright”. Replacing both words with “dull” gives “The room looked dull”. That substitution supports treating “quite bright” as one group. Which word inside that group gives the description?'],
      ['Try a phrase with one word', 'Now remove “quite” and read “The room looked bright”. Use the contrast to decide which branch disappears and what label still covers the description.'],
    ],
    reveal: ['Check your analysis', '“Bright” supplies the description in both versions, so it is the head under A. In “quite bright”, DEG also branches from AP. Removing “quite” removes DEG and leaves an AP headed by “bright”.'],
    recapSummary: 'The same contrast worked for “very cheerful” and “quite bright”. Removing the degree word leaves the adjective and its basic description in place. That is why A marks the head and AP marks the whole group, even when the group contains only that adjective.',
    recap: ['Find the whole description.', 'Remove the degree word to check which adjective still supplies the description.', 'Label the head A, any degree word DEG, and the whole group AP.'],
    selfCheck: ['Try “rather narrow”. Which label covers both words, and which labels cover each word?', 'AP covers “rather narrow”. DEG covers “rather” and A covers “narrow”.'],
    postTestIntro: 'Use the head and degree word to read each adjective phrase.',
  },
  'br-04': {
    topics: ['The Basic Transitive VP', 'Verbs and Direct Objects', 'Reading and Building a Transitive VP', 'Finding a New Direct Object'],
    intro: 'Chapter 2 separated a sentence into subject and predicate. This chapter takes the next step. It looks inside the predicate to see how a verb combines with its direct object.',
    exampleContext: 'In the inspection example, the first bracket marks the subject and the second marks the whole predicate.',
    example: '[Nora] [inspected the bridge].',
    introExample: 'A direct object is a verb complement that usually follows the verb in an active statement. Here “the bridge” is the direct object of “inspected”. A verb used with a direct object is transitive, so this example gives a transitive verb phrase.',
    preview: ['Separate the subject from the full predicate.', 'Identify the complete object and read the transitive feature on V.', 'Build the object branch and find the same pattern in a new sentence.'],
    concepts: [
      ['Start with the full predicate', 'First separate “Nora” from “inspected the bridge”. The second group is the full predicate because it says what Nora did. Keeping those words together gives you the VP to analyse next.'],
      ['Find the complete direct object', 'Inside that VP, “inspected” is the verb. Ask what Nora inspected to find the words that complete it. The answer is “the bridge”. In “Nora inspected it”, the pronoun replaces both words together, which helps confirm the span of the object NP.'],
      ['Show the transitive pattern', 'Once you have the whole object, you can show how it connects to the verb. “Inspected” takes a direct object in this sentence, so V carries [trans]. The object NP and V attach to the same VP. Nodes that share an immediate parent are called sisters.'],
    ],
    contrast: ['Compare the two jobs an NP can do', ['The subject NP “Nora” attaches directly to S.', 'The object NP “the bridge” attaches inside VP, beside V [trans].']],
    opening: [
      ['In “Rina opened the window”, which group names what Rina opened?', ['Rina', 'the window', 'opened the window'], 1],
      ['In “Rina opened the window”, which words form the whole predicate?', ['opened', 'the window', 'opened the window'], 2],
    ],
    steps: ['Find the subject', 'Read V [trans]', 'Trace the object NP'],
    captions: [
      'The subject NP “Nora” attaches directly to S. The other branch from S leads to the whole predicate.',
      'V covers “inspected”. Its [trans] feature marks its use with one direct object here.',
      'The NP “the bridge” is the direct object. It shares VP as a parent with V.',
    ],
    beforeTree: 'Use the split from the previous page to read the tree. Start at S and trace “Nora” to the subject NP. Follow the other branch to VP, then select V [trans] and the object NP to see where they meet.',
    treeTakeaway: 'Both “Nora” and “the bridge” are NPs. Their positions distinguish their jobs. “Nora” joins the predicate at S, while “the bridge” joins the verb inside VP. Use that second relationship to complete the tree.',
    buildTitle: 'Attach the direct object',
    build: {
      branch: root => [root.children[1], root.children[1].children[1]],
      prompt: 'The subject and verb are in place. Connect the NP “the bridge” so it shares a parent with V.',
      action: 'Connect the object NP under VP',
      hint: 'Attach “the bridge” to VP beside V [trans]. The subject NP “Nora” stays directly under S.',
      success: 'The object NP shares VP with V [trans]. The subject NP stays outside that VP.',
    },
    applyExample: 'The children carried a heavy box.',
    apply: [
      ['Find the full object', 'Use the same order in “The children carried a heavy box”. Find the whole predicate before asking what the children carried. Check your answer by seeing which words “it” replaces in “The children carried it”.'],
      ['Check the verb in context', 'Now try “Rina opened the window” and “The window opened”. In the first sentence, “the window” is the object. In the second, it is the subject. The same verb can appear in different patterns, so check for an object before choosing [trans].'],
    ],
    reveal: ['Check your analysis', '“The children” is the subject NP under S. “A heavy box” is the object NP because it names what they carried and can be replaced as a unit by “it”. That whole NP attaches beside V [trans] inside the predicate “carried a heavy box”.'],
    recapSummary: 'Start with the sentence split, then look inside the predicate. In “Nora inspected the bridge”, “Nora” is the subject NP under S. The object NP “the bridge” belongs with “inspected” under VP. The replacement “Nora inspected it” helps check exactly which words belong on the object branch.',
    recap: ['Find the subject and the full VP.', 'Within that VP, locate the verb and ask what or whom it takes as its object in this use.', 'Attach the direct-object NP and V [trans] to the same VP.'],
    selfCheck: ['In “Sam repaired the old lamp”, which words belong inside the object NP?', 'The whole NP is “the old lamp”. It attaches directly to VP beside V [trans].'],
    postTestIntro: 'Check the verb feature, the complete object span, and where the object attaches.',
  },
  'br-05': {
    topics: ['Adjuncts and Two Levels of VP', 'Complements and Time Adjuncts', 'Reading and Building the VP Layers', 'Finding an Adjunct in a New Sentence'],
    intro: 'Chapter 4 grouped a verb with its direct object. This chapter keeps that group intact and asks where a time phrase fits when it is added to the sentence.',
    exampleContext: 'The first bracket marks what Nora did. The second marks when the inspection happened.',
    example: 'Nora [inspected the bridge] [in June].',
    introExample: 'An adjunct adds information such as time, place, or manner to a group. “In June” adds the time of the inspection. The tree shows this by joining it to the whole group “inspected the bridge”.',
    preview: ['Find the verb and its object before adding the time phrase.', 'Trace and build the inner and outer VP.', 'Use omission and replacement to check the grouping in a new sentence.'],
    concepts: [
      ['Find the verb and its complement', 'Begin with the shorter sentence, “Nora inspected the bridge”. The question from Chapter 4 still works. What did Nora inspect? “The bridge” is the direct object. A complement fills a role in the pattern of its head, and here the object fills the role provided by “inspected”. The two form a VP.'],
      ['Check what the time phrase adds', 'Now add “in June” to that predicate. The prepositional phrase (PP) answers when the inspection happened. Leaving it out removes the time information while leaving the basic event intact. This is a clue that the PP is a time adjunct.'],
      ['Use two levels of VP', 'The omission test shows which words belong together without the adjunct. Keep “inspected the bridge” as the inner VP, the smaller phrase inside another VP. Attach “in June” beside it. The two branches share the outer VP, which covers both the event and its time.'],
    ],
    contrast: ['Compare the two attachment points', ['“The bridge” is the direct object. Its NP shares a parent with V.', '“In June” is a time adjunct here. Its PP shares a parent with the whole inner VP.']],
    opening: [
      ['In “Nora inspected the bridge in June”, which words tell when the inspection happened?', ['the bridge', 'inspected the bridge', 'in June'], 2],
      ['Which group can stand as the predicate after leaving out the time phrase?', ['inspected the bridge', 'the bridge in June', 'inspected in'], 0],
    ],
    steps: ['Trace the inner VP', 'Trace the time PP', 'Read the outer VP'],
    captions: [
      'The inner VP “inspected the bridge” groups the verb with its direct object. This group describes the event.',
      'The PP “in June” specifies when the inspection happened. It attaches beside the entire inner VP.',
      'The outer VP covers both groups. The inner VP and time PP share it as their parent.',
    ],
    beforeTree: 'Start by tracing “inspected the bridge”, the group that survived omission. Trace it to the inner VP, then select the time PP and the outer VP. Choose Without the time phrase to see the inner VP on its own.',
    treeTakeaway: 'The two attachment points reflect what each group goes with. The object joins V within the inner VP, while the time PP joins that entire VP. Keep this difference in mind as you attach the PP.',
    buildTitle: 'Attach the time adjunct',
    build: {
      branch: root => [root.children[1], root.children[1].children[1]],
      prompt: 'The verb and object already form an inner VP. Connect the PP “in June” so it shares a parent with that whole phrase.',
      action: 'Connect the time PP under the outer VP',
      hint: 'Keep “in June” beside the inner VP. Inside the inner VP, “the bridge” stays beside V.',
      success: 'The PP and inner VP are sisters under the outer VP. The verb and object stay together.',
    },
    applyExample: 'The children carried a heavy box before lunch.',
    apply: [
      ['Find the two groups', 'Apply the same distinction to the new event. Ask what the children carried to find the object, then ask when they carried it to find the time phrase.'],
      ['Try leaving out the time phrase', 'Check your grouping by reading the sentence without “before lunch”. What remains of the predicate? That group is the starting point for deciding where the time phrase attaches.'],
      ['Check what “did so” can replace', 'A replacement gives another check. In “The children carried a heavy box before lunch, and their neighbours did so after lunch”, what activity does “did so” stand for? Compare it with the group left by omission.'],
    ],
    reveal: ['Check your analysis', '“Carried a heavy box” survives when the time phrase is omitted, and “did so” can stand for that same group. This is the inner VP. Within it, “a heavy box” attaches beside V. “Before lunch” joins the inner VP at the next level.'],
    recapSummary: 'Start with the verb and its object to find the group that names the event. In the inspection sentence, that group is “inspected the bridge”. “In June” adds a time to the event, so the PP joins the whole inner VP to form a larger VP. Leaving out the PP or replacing the inner group with a form of “do so” helps make the two levels visible.',
    recap: ['Group V with its object NP to form the inner VP.', 'Find the final time PP that describes the event.', 'Put the PP beside the inner VP under the outer VP.'],
    selfCheck: ['In “Sam repaired the old lamp after school”, what belongs in each VP?', 'The inner VP is “repaired the old lamp”. The outer VP includes that group and the PP “after school”.'],
    postTestIntro: 'Trace both levels of VP and check which node is the adjunct’s sister.',
    references: ['Noel Burton-Roberts, Analysing Sentences, 3rd ed., printed p. 91 (the do so replacement test).'],
  },
  ...advancedFoundationsChapters,
};

export const phraseStructureArticles = Object.fromEntries(Object.entries(chapters).map(([id, chapter]) => [id, {
  headings: [`Introduction to ${chapter.topics[0]}`, ...chapter.topics.slice(1), 'Chapter Recap', 'Check what you learned'],
  openingCheck(lesson) {
    return [lesson.predict, ...chapter.opening.map(([prompt, choices, correct]) => ({
      prompt, answer: String(correct), options: choices.map((text, index) => ({ id: String(index), text })),
    }))];
  },
  postTestIntro: chapter.postTestIntro,
  references: chapter.references,
  teach(body, page, ui) {
    const { el, lesson } = ui;
    const polish = chapterPolishing[id];
    function sections(blocks) {
      for (const [title, text] of blocks) body.append(el('h3', title), el('p', text));
    }
    function list(tag, items) {
      const container = el(tag);
      container.append(...items.map(item => el('li', item)));
      body.append(container);
    }
    function reveal(label, text, example) {
      const answer = el('details');
      answer.append(el('summary', label));
      if (example) answer.append(lessonExample(el, example));
      answer.append(el('p', text));
      body.append(answer);
    }
    if (page === 0) {
      sections([['What this chapter covers', chapter.intro]]);
      addIntroExample(body, el, chapter.exampleContext, chapter.example, chapter.introExample);
      body.append(el('h3', 'What you’ll see in this chapter'));
      list('ul', chapter.preview);
    }
    if (page === 1) {
      if (id.startsWith('br-')) {
        body.append(el('p', chapter.conceptLead ?? 'Use the opening example as a reference for the explanation below.'));
        body.append(lessonExample(el, chapter.example));
      }
      sections(chapter.concepts);
      body.append(el('h3', chapter.contrast[0]));
      list('ul', chapter.contrast[1]);
      if (polish.examples) addVisibleContrast(body, ui, polish.examples);
    }
    if (page === 2) {
      sections([[chapter.build ? 'Read the branches' : 'Follow the worked example', chapter.beforeTree]]);
      addWorkedExample(body, ui, chapter.steps, {
        highlightWords: true,
        captions: chapter.captions,
        comparison: polish.comparison?.(ui),
        extraSteps: polish.extraSteps?.(lesson.worked_example.tree.root),
        tracePath: polish.tracePath,
      });
      if (chapter.build) {
        body.append(el('p', chapter.treeTakeaway));
        sections([[chapter.buildTitle, chapter.build.prompt]]);
        body.append(el('p', 'Drag a branch from the parent’s connection point to the detached node. Use Guide me for help, then select Check my tree.'));
        addBranchExercise(body, ui, chapter);
      } else {
        sections([chapter.workedPractice]);
        reveal('Show the worked answer', chapter.workedAnswer, chapter.workedAnswerExample);
      }
    }
    if (page === 3) {
      body.append(el('p', chapter.applyExample, 'lesson-example-sentence'));
      sections(chapter.apply);
      if (polish.combination) {
        addCombinationPractice(body, ui, polish.combination.basic, polish.combination.incomplete);
      } else {
        addWordPractice(body, ui, polish.practice);
      }
      reveal(...chapter.reveal);
    }
    if (page === 4) {
      if (chapter.recapSummary) sections([['What this chapter showed', chapter.recapSummary]]);
      body.append(el('h3', 'Steps to use on a new example'));
      list('ol', chapter.recap);
      sections([['Try a quick check', chapter.selfCheck[0]]]);
      reveal('Show the answer', chapter.selfCheck[1]);
    }
  },
}]));
