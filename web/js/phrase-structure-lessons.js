import { addIntroExample, lessonExample } from './lesson-presentation.js';
import { advancedFoundationsChapters } from './advanced-foundations-lessons.js';
import { addWorkedExample } from './foundations-lesson.js';
import { addVisibleContrast, chapterPolishing } from './foundations-polishing.js';
import { addCombinationPractice, addWordPractice } from './foundations-practice.js';
import { addEmbeddedTreeExercise } from './lesson-tree-exercise.js';
import { connect, disconnect, fromCanonicalEnvelope, toCanonicalEnvelope } from './syntax-builder.js';

const chapters = {
  'br-03': {
    topics: ['Adjective Phrases', 'Heads and Degree Words', 'Reading and Building an AP', 'Finding the Head in a New Phrase'],
    intro: 'Chapter 2 looked at the jobs that whole phrases do. This chapter looks inside one of those groups to see how its words work together.',
    exampleContext: 'In the example below, the brackets mark the description that follows “seemed”.',
    example: 'The children seemed [very cheerful].',
    introExample: 'The adjective “cheerful” describes the children, and “very” makes that description stronger. The whole group is an adjective phrase (AP) because it is built around the adjective.',
    preview: ['Use the contrast between “cheerful” and “very cheerful” to find the head.', 'Show the head and degree word on the tree.', 'Use the same reasoning to analyse a new description.'],
    concepts: [
      ['Find the head', 'Start with “The children seemed very cheerful” and remove “very”. In “The children seemed cheerful”, the adjective still supplies the description. The word that gives the phrase its grammatical character is its head. Here, “cheerful” is the head, so the group is an adjective phrase with or without “very”.'],
      ['Check what the degree word adds', 'Now try removing the head from the original sentence. “The children seemed very” leaves the description incomplete. In this example, “very” needs an adjective to modify. It is a degree word because it indicates how strongly the description applies. Replacing it with “quite” or “rather” changes the degree while keeping “cheerful” as the head.'],
      ['Read the labels', 'The tree shows both jobs. A labels the adjective “cheerful”, and DEG labels the degree word “very”. Both branches join under AP, the label for the whole phrase. Removing the degree word removes its branch, while A still heads the AP.'],
    ],
    contrast: ['Carry the comparison into the tree', ['In “very cheerful”, the AP covers the description and its degree word.', 'In “cheerful”, the AP covers just the adjective. The head stays the same in both trees.']],
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
    intro: 'In Chapter 2, you found the subject and predicate. Now look inside the predicate and see how the verb combines with a direct object. A verb used with one direct-object noun phrase follows the basic transitive pattern taught here.',
    exampleContext: 'In this statement about an inspection, the first bracket marks the subject. Look inside the second bracket for the verb and its direct object.',
    example: '[Nora] [inspected the bridge].',
    introExample: '“Nora” is the subject. Inside the predicate, “inspected” is the verb and “the bridge” is its direct object. The object names what Nora inspected.',
    preview: ['Separate the subject from the full predicate.', 'Identify the complete object and read the transitive feature on V.', 'Build the object branch and find the same pattern in a new sentence.'],
    concepts: [
      ['Start with the full predicate', 'In “Nora inspected the bridge”, the subject is “Nora”. Ask what the sentence says about Nora. “Inspected the bridge” is the whole predicate. You can then look inside that VP to find the verb and the words that go with it.'],
      ['Find the complete direct object', 'Ask “What did Nora inspect?” The answer is “the bridge”. Check the span with “Nora inspected it”. The pronoun replaces both words, which gives you evidence that the full NP belongs together.'],
      ['Show the transitive pattern', 'In this use, “inspected” takes one direct object. The feature [trans] belongs on V. Put the object NP beside V, directly under the same VP. That position and the feature show the object’s job.'],
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
    beforeTree: 'Trace “Nora” up to S through the subject NP. Then follow the other branch from S to VP. Inside VP, select V [trans] and the NP that covers “the bridge”. Notice which node both branches meet at.',
    treeTakeaway: 'The two NPs share a category and have different jobs. “Nora” meets VP at S. “The bridge” meets V inside VP.',
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
      ['Find the full object', 'First find the full predicate. Then ask what the children carried. Use “The children carried it” to check the full stretch of words you would put under the object NP.'],
      ['Compare a verb in two sentences', 'Read “Rina opened the window” and “The window opened”. The first has a direct object. In the second, “the window” is the subject, and “opened” has no direct object. Check the verb’s use in the sentence before assigning a feature.'],
    ],
    reveal: ['Check your analysis', '“The children” is the subject NP directly under S. “A heavy box” is the direct-object NP. Attach it beside V [trans] inside “carried a heavy box”.'],
    recapSummary: 'In “Nora inspected the bridge”, the subject NP and the object NP have the same category and different jobs. “Nora” joins the predicate under S. “The bridge” joins “inspected” inside VP. Replacing “the bridge” with “it” helps check that the whole object belongs on that branch.',
    recap: ['Find the subject and the full VP.', 'Within that VP, locate the verb and ask what or whom it takes as its object in this use.', 'Attach the direct-object NP and V [trans] to the same VP.'],
    selfCheck: ['In “Sam repaired the old lamp”, which words belong inside the object NP?', 'The whole NP is “the old lamp”. It attaches directly to VP beside V [trans].'],
    postTestIntro: 'Check the verb feature, the complete object span, and where the object attaches.',
  },
  'br-05': {
    topics: ['Adjuncts and Two Levels of VP', 'Complements and Time Adjuncts', 'Reading and Building the VP Layers', 'Finding an Adjunct in a New Sentence'],
    intro: 'Chapter 4 put the verb and its direct object together in one verb phrase. Now add a time phrase. A phrase that adds information about the event is called an adjunct in this pattern.',
    exampleContext: 'Read this statement about an inspection. The brackets separate what Nora did from the words that specify when she did it.',
    example: 'Nora [inspected the bridge] [in June].',
    introExample: 'The time phrase “in June” is an adjunct. In the tree, it joins the whole verb phrase “inspected the bridge” to form a larger VP.',
    preview: ['Find the verb and its object before adding the time phrase.', 'Trace and build the inner and outer VP.', 'Use omission and replacement to check the grouping in a new sentence.'],
    concepts: [
      ['Find the verb and its complement', 'Start with “Nora inspected the bridge”. The bridge is what Nora inspected. As the direct object, “the bridge” completes this use of the verb and sits beside V inside VP. Together they make “inspected the bridge”.'],
      ['Check what the time phrase adds', 'Add “in June”. This prepositional phrase (PP) tells when the inspection took place. Leave it out and “Nora inspected the bridge” still gives the same basic event. That is evidence that the time PP is an adjunct in this sentence.'],
      ['Use two levels of VP', 'The inner VP covers “inspected the bridge”. The outer VP covers that whole group plus “in June”. The time phrase adds information about the complete inspection, so it joins the inner VP under the outer VP.'],
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
    beforeTree: 'Trace the verb and object together in the inner VP. Select the time PP, then the outer VP to see both groups. Predict what will remain when you choose Without the time phrase.',
    treeTakeaway: 'Follow the PP upward. It meets the inner VP at the outer VP. The object NP meets V one level lower.',
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
      ['Find the two groups', 'Ask what they carried, then ask when they carried it. Keep both answers in mind. One belongs directly beside the verb, and the other describes the event made up of the verb and object together.'],
      ['Try leaving out the time phrase', 'Read the sentence without “before lunch”. Which words still make up the predicate? Say the full inner VP before you decide where to attach the time phrase.'],
      ['Check what “did so” can replace', 'In “The children carried a heavy box before lunch, and their neighbours did so after lunch”, what does “did so” stand for? Use the answer to check which words belong together.'],
    ],
    reveal: ['Check your analysis', '“Carried a heavy box” is the inner VP and is the group replaced by “did so”. “A heavy box” is the object NP beside V. The time PP “before lunch” sits beside the inner VP, and the outer VP covers both.'],
    recapSummary: 'In “Nora inspected the bridge in June”, the verb and object form an inner VP that describes the inspection. “In June” adds a time to that event, so it joins the inner VP under a larger VP. Removing the time phrase leaves the inner VP intact. A form of “do so” can also stand for that inner group in the examples you practised.',
    recap: ['Group V with its object NP to form the inner VP.', 'Find the final time PP that describes the event.', 'Put the PP beside the inner VP under the outer VP.'],
    selfCheck: ['In “Sam repaired the old lamp after school”, what belongs in each VP?', 'The inner VP is “repaired the old lamp”. The outer VP includes that group and the PP “after school”.'],
    postTestIntro: 'Trace both levels of VP and check which node is the adjunct’s sister.',
    references: ['Noel Burton-Roberts, Analysing Sentences, 3rd ed., printed p. 91 (the do so replacement test).'],
  },
  ...advancedFoundationsChapters,
};

// Compare the visible analysis independently of the IDs assigned to edits.
function shape(node) {
  return [node.label, node.word, node.words, node.features || [], node.gap, node.index, node.children?.map(shape)];
}

function addBranchExercise(body, ui, chapter) {
  const target = ui.lesson.worked_example.tree;
  const [parent, child] = chapter.build.branch(target.root);
  const profile = target.convention_profile;
  const expected = JSON.stringify(shape(target.root));
  function branchFeedback(model) {
    const current = model.nodes[child.id];
    const intended = model.nodes[parent.id];
    if (!current || !intended) return 'A starting node is missing. Choose Restart exercise to restore it, or recreate it on the canvas.';
    if (!current.parent) return `The target branch is still detached. ${chapter.build.hint}`;
    if (current.parent !== parent.id) {
      return `The target branch is attached to ${model.nodes[current.parent].type}. ${chapter.build.hint}`;
    }
    return null;
  }
  addEmbeddedTreeExercise(body, ui, {
    id: `${ui.lesson.lesson_id}-branch`,
    label: `${chapter.buildTitle} exercise`,
    profile,
    recovery: true,
    seed() {
      const model = fromCanonicalEnvelope(target);
      disconnect(model, child.id);
      return model;
    },
    check(model) {
      try {
        const built = toCanonicalEnvelope(model, profile);
        if (JSON.stringify(shape(built.root)) === expected) return chapter.build.success;
      } catch (error) {
        return branchFeedback(model) ?? `${error.message} ${chapter.build.hint}`;
      }
      return branchFeedback(model) ?? `The branch is attached. Check the rest of the tree against the worked example. ${chapter.build.hint}`;
    },
    guide: [{
      title: chapter.build.action,
      text: chapter.build.hint,
      apply(model) {
        if (!model.nodes[parent.id] || !model.nodes[child.id]) {
          return 'A starting node is missing. Choose Restart exercise to restore it, or recreate it on the canvas.';
        }
        return connect(model, parent.id, child.id) ? 'The branch is connected. Check the construction.' : chapter.build.hint;
      },
    }, {
      title: 'Check the branch',
      text: 'See whether the groups attach in the intended order.',
    }],
  });
}

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
        body.append(el('p', 'Drag a branch from the parent’s connection point to the detached node. Use Guide me for help, then select Check construction.'));
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
