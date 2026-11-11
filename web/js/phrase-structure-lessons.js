import { addWorkedExample } from './foundations-lesson.js';
import { addEmbeddedTreeExercise } from './lesson-tree-exercise.js';
import { connect, disconnect, fromCanonicalEnvelope, toCanonicalEnvelope } from './syntax-builder.js';

const chapters = {
  'br-03': {
    topics: ['Adjective Phrases', 'Heads and Degree Words', 'Reading and Building an AP', 'Finding the Head in a New Phrase'],
    intro: 'In Chapter 2, you labelled whole phrases. Now look inside one. In “very cheerful”, the adjective “cheerful” is the head, the word that gives the phrase its category. “Very” tells you the degree of cheerfulness. Together they form an adjective phrase.',
    preview: ['Find the word that makes the group an adjective phrase.', 'Read and build an AP with an adjective and a degree word.', 'Apply the same pattern to a new phrase.'],
    concepts: [
      ['Find the head', 'Compare “cheerful” with “very cheerful”. In “The children seemed cheerful” and “The children seemed very cheerful”, both phrases describe the children. “Cheerful” supplies the description in both.'],
      ['Find the degree word', '“Very” tells you how cheerful the children seemed. It depends on the adjective here: “The children seemed very” leaves the description unfinished. Other degree words in this pattern include “quite” and “rather”.'],
      ['Read the labels', 'A labels the adjective word. DEG labels the degree word. AP labels the whole phrase. In this pattern, DEG and A are sisters directly under AP.'],
    ],
    opening: [
      ['In “quite bright”, which word tells you the degree of brightness?', ['quite', 'bright', 'both words']],
      ['In “very quiet”, which label stands for the whole adjective phrase?', ['A', 'AP', 'DEG']],
    ],
    steps: ['Find cheerful', 'Read the A label', 'Read the whole AP'],
    beforeTree: 'Find “cheerful” first and follow it up to A. Then look one level higher for AP. The other branch from AP leads to DEG and the word “very”.',
    buildTitle: 'Connect the adjective head',
    build: {
      branch: root => [root, root.children[1]],
      prompt: 'The DEG branch is in place. Connect the A branch for “cheerful” to the node that covers both words.',
      action: 'Connect A under AP',
      hint: 'A and DEG should share AP as their parent. Keep “cheerful” under A.',
      success: 'A and DEG are sisters under AP. “Cheerful” is the adjective head.',
    },
    apply: [
      ['Find the two roles in “quite bright”', 'Read “The room looked quite bright”. Which word supplies the description? Which word tells you its degree?'],
      ['Try a phrase with one word', 'Now read “The room looked bright”. The description still works. “Bright” can form an AP on its own.'],
    ],
    reveal: ['Check your analysis', 'In “quite bright”, A covers “bright” and DEG covers “quite”. Both branches sit directly under AP. In the one-word example, AP contains just the adjective branch.'],
    recap: ['Find the adjective that supplies the description.', 'If a word like “very” tells its degree, label that word DEG in this pattern.', 'Use A for the adjective and AP for the whole phrase.'],
    postTestIntro: 'Use the head and degree word to read each adjective phrase.',
  },
  'br-04': {
    topics: ['The Basic Transitive VP', 'Verbs and Direct Objects', 'Reading and Building a Transitive VP', 'Finding a New Direct Object'],
    intro: 'In Chapter 2, you found the subject and predicate. Now look inside the predicate of “Nora inspected the bridge”. “Inspected” is the verb. “The bridge” names what Nora inspected and works as the direct object.',
    preview: ['Separate the subject from the whole verb phrase.', 'Attach the direct-object noun phrase beside the verb.', 'Recognize the same structure in a new sentence.'],
    concepts: [
      ['Start with the full predicate', 'In “Nora inspected the bridge”, the subject is “Nora”. The predicate is “inspected the bridge”. Both the verb and the object belong inside that verb phrase.'],
      ['Find the direct object', 'Ask “What did Nora inspect?” The answer is “the bridge”. Keep the whole noun phrase together. It could be replaced by “it” in “Nora inspected it”.'],
      ['Show the transitive pattern', 'In this use, “inspected” takes one direct-object NP. Put [trans] on V to mark that pattern. The object NP is a sister of V, so both attach directly to VP. Compare “Nora slept”, where “slept” has no object.'],
    ],
    opening: [
      ['In “Rina opened the window”, which group names what Rina opened?', ['Rina', 'the window', 'opened the window']],
      ['In “Rina opened the window”, which words form the whole predicate?', ['opened', 'the window', 'opened the window']],
    ],
    steps: ['Find the subject', 'Read V [trans]', 'Trace the object NP'],
    beforeTree: 'Trace “Nora” up to S through the subject NP. Then follow the other branch from S to VP. Inside VP, look for V [trans] and the NP that covers “the bridge”.',
    buildTitle: 'Attach the direct object',
    build: {
      branch: root => [root.children[1], root.children[1].children[1]],
      prompt: 'The subject and verb are in place. Connect the NP “the bridge” so it shares a parent with V.',
      action: 'Connect the object NP under VP',
      hint: 'Attach “the bridge” to VP beside V [trans]. The subject NP “Nora” stays directly under S.',
      success: 'The object NP shares VP with V [trans]. The subject NP stays outside that VP.',
    },
    apply: [
      ['Find the object in “The children carried a heavy box”', 'First find the full subject and predicate. Then ask what the children carried. Include every word in the answer.'],
      ['Compare the two NPs', 'Both “the children” and “a heavy box” are noun phrases. In the tree, their different attachment points show their jobs.'],
    ],
    reveal: ['Check your analysis', '“The children” is the subject NP directly under S. “A heavy box” is the direct-object NP. Attach it beside V [trans] inside “carried a heavy box”.'],
    recap: ['Find the subject and the full VP.', 'Within that VP, locate the verb and ask what or whom it takes as its object in this use.', 'Attach the direct-object NP and V [trans] to the same VP.'],
    postTestIntro: 'Check the verb feature, the complete object span, and where the object attaches.',
  },
  'br-05': {
    topics: ['Adjuncts and Two Levels of VP', 'Complements and Time Adjuncts', 'Reading and Building the VP Layers', 'Finding an Adjunct in a New Sentence'],
    intro: '“Nora inspected the bridge in June” builds on the verb phrase from Chapter 4. “The bridge” tells us what Nora inspected. “In June” tells us when the inspection happened. Their different jobs show up at different levels of the tree.',
    preview: ['Find the verb and its object before looking at the time phrase.', 'Use two VP levels to show where the time phrase attaches.', 'Apply the same reasoning to a new sentence.'],
    concepts: [
      ['Find the verb and its complement', 'Start with “Nora inspected the bridge”. “The bridge” is the direct object and is a sister of V inside VP. Together, “inspected the bridge” forms a complete verb phrase in this example.'],
      ['Add information about the event', 'Add “in June” to tell when Nora inspected the bridge. The time phrase is a prepositional phrase (PP). Here it works as an adjunct, adding information about the whole inspection. Leaving it out still gives “Nora inspected the bridge”.'],
      ['Use two levels of VP', 'The inner VP covers “inspected the bridge”. The outer VP covers “inspected the bridge in June”. Attach the PP beside the inner VP under the outer VP. This is the pattern for the final time adjunct shown here.'],
    ],
    opening: [
      ['In “Nora inspected the bridge in June”, which words tell when the inspection happened?', ['the bridge', 'inspected the bridge', 'in June']],
      ['Which group can stand as the predicate after leaving out the time phrase?', ['inspected the bridge', 'the bridge in June', 'inspected in']],
    ],
    steps: ['Trace the inner VP', 'Trace the time PP', 'Read the outer VP'],
    beforeTree: 'Start at the inner VP and trace the verb and object together. Then find the PP “in June”. Follow both branches upward to see which node contains the full predicate.',
    buildTitle: 'Attach the time adjunct',
    build: {
      branch: root => [root.children[1], root.children[1].children[1]],
      prompt: 'The verb and object already form an inner VP. Connect the PP “in June” so it shares a parent with that whole phrase.',
      action: 'Connect the time PP under the outer VP',
      hint: 'Keep “in June” beside the inner VP. Inside the inner VP, “the bridge” stays beside V.',
      success: 'The PP and inner VP are sisters under the outer VP. The verb and object stay together.',
    },
    apply: [
      ['Find what happened in “The children carried a heavy box before lunch”', 'Ask what they carried, then ask when they carried it. The answers identify different groups.'],
      ['Try leaving out the time phrase', 'Read the sentence without “before lunch”. Which words still make up the predicate? Use that group as your inner VP.'],
      ['Check what “did so” can replace', 'In “The children carried a heavy box before lunch, and their neighbours did so after lunch”, “did so” stands for “carried a heavy box”. The two time phrases tell when each event happened. This is another clue that the verb and object form a VP together.'],
    ],
    reveal: ['Check your analysis', '“Carried a heavy box” is the inner VP. “A heavy box” is the object NP beside V. The time PP “before lunch” sits beside the inner VP, and the outer VP covers both.'],
    recap: ['Group V with its object NP to form the inner VP.', 'Find the final time PP that describes the event.', 'Put the PP beside the inner VP under the outer VP.'],
    postTestIntro: 'Trace both levels of VP and check which node is the adjunct’s sister.',
    references: ['Noel Burton-Roberts, Analysing Sentences, 3rd ed., printed p. 91 (the do so replacement test).'],
  },
};

// Compare the visible analysis independently of the IDs assigned to edits.
function shape(node) {
  return [node.label, node.word, node.words, node.features || [], node.children?.map(shape)];
}

function addBranchExercise(body, ui, chapter) {
  const target = ui.lesson.worked_example.tree;
  const [parent, child] = chapter.build.branch(target.root);
  const profile = target.convention_profile;
  const expected = JSON.stringify(shape(target.root));
  addEmbeddedTreeExercise(body, ui, {
    id: `${ui.lesson.lesson_id}-branch`,
    label: `${chapter.buildTitle} exercise`,
    profile,
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
        return `${error.message} ${chapter.build.hint}`;
      }
      return chapter.build.hint;
    },
    guide: [{
      title: chapter.build.action,
      text: chapter.build.hint,
      apply(model) {
        if (!model.nodes[parent.id] || !model.nodes[child.id]) {
          return 'A starting node is missing. Recreate and connect the branch on the canvas.';
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
  openingIntro: 'Try three short questions to see what you already know. This check is unscored.',
  openingCheck(lesson) {
    return [lesson.predict, ...chapter.opening.map(([prompt, choices]) => ({
      prompt, options: choices.map((text, index) => ({ id: String(index), text })),
    }))];
  },
  postTestIntro: chapter.postTestIntro,
  references: chapter.references,
  teach(body, page, ui) {
    const { el } = ui;
    function sections(blocks) {
      for (const [title, text] of blocks) body.append(el('h3', title), el('p', text));
    }
    function list(tag, items) {
      const container = el(tag);
      container.append(...items.map(item => el('li', item)));
      body.append(container);
    }
    if (page === 0) {
      sections([['What this chapter covers', chapter.intro]]);
      body.append(el('h3', 'What you’ll see in this chapter'));
      list('ul', chapter.preview);
    }
    if (page === 1) sections(chapter.concepts);
    if (page === 2) {
      body.append(el('p', chapter.beforeTree));
      addWorkedExample(body, ui, chapter.steps, { highlightWords: true });
      sections([[chapter.buildTitle, chapter.build.prompt]]);
      addBranchExercise(body, ui, chapter);
    }
    if (page === 3) {
      sections(chapter.apply);
      const answer = el('details');
      answer.append(el('summary', chapter.reveal[0]), el('p', chapter.reveal[1]));
      body.append(answer);
    }
    if (page === 4) {
      body.append(el('h3', 'Steps to use on a new example'));
      list('ol', chapter.recap);
    }
  },
}]));
