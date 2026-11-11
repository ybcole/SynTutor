// Presentation copy for the existing M4 lessons. The catalog owns the reviewed
// explanations, examples, worked steps, assessments and source references.
const chapterPages = {
  'br-03': {
    topics: ['Adjective Phrases', 'Heads and Degree Words', 'Reading an AP', 'Finding the Head'],
    steps: ['Adjective', 'Head A', 'Degree word'],
    context: 'Trace “cheerful” and “very” to their own labels. The head “cheerful” gives the whole phrase its category, AP.',
    recap: ['A labels the adjective head.', 'DEG labels the degree word.', 'The whole adjective phrase is AP.'],
  },
  'br-04': {
    topics: ['The Transitive VP', 'Verbs and Direct Objects', 'Reading a Transitive VP', 'Finding the Direct Object'],
    steps: ['Subject and predicate', 'Transitive verb', 'Object NP'],
    context: 'Start at “the bridge” and follow its NP branch upward. Its sister is V inside the VP. The subject NP “Nora” sits outside that VP.',
    recap: ['V carries [trans] in this pattern.', 'The direct-object NP is sister to V under VP.'],
  },
  'br-05': {
    topics: ['VP Adjuncts and Complements', 'Two Levels of VP', 'Reading the VP Layers', 'Finding the Adjunct'],
    steps: ['Inner VP', 'Adjunct PP', 'Outer VP'],
    context: 'Compare “the bridge” with “in June”. The object NP joins V, while the PP joins the inner VP to form a larger VP.',
    recap: ['A verb complement is sister to V.', 'An adjunct adverbial is sister to VP.'],
  },
  'br-06': {
    topics: ['Progressive Auxiliaries', 'Auxiliaries and VP Complements', 'Reading the Progressive VP', 'Finding the Lower VP'],
    steps: ['Lexical VP', 'Progressive auxiliary', 'Higher VP'],
    context: 'Follow “inspecting the bridge” to the lower VP. That whole VP is the complement of “is”, the progressive auxiliary.',
    recap: ['The higher VP contains PROG and its VP complement.', 'The lexical verb and its object form the lower VP.'],
  },
  'br-07': {
    topics: ['The Core Noun Phrase', 'DET, NOM and N', 'Reading the Noun Phrase', 'Following DET and NOM'],
    steps: ['Noun', 'NOM', 'DET and NOM'],
    context: 'Trace “lanterns” from N through NOM to NP. The demonstrative “those” reaches the same NP through DET.',
    recap: ['DET and NOM are sisters under NP in this pattern.', 'NOM is the intermediate level between NP and N.'],
  },
  'br-08': {
    topics: ['Overt That-clauses', 'Complementiser and Clause', 'Reading C and S', 'Sentence and Clause in Context'],
    steps: ['Clause boundary', 'Complementiser C', 'C and S under S′'],
    context: 'Trace “that” to C and the following clause to S. Both branches are directly under S′ in the display.',
    recap: ['C and S are sisters under S′ in the overt that-clause.', 'The tree stores S′ as S-bar.'],
  },
  'br-09': {
    topics: ['Wh-fronting and Gaps', 'C2, C1 and Typed Gaps', 'Reading an Object Wh-question', 'Following the Object Gap'],
    steps: ['Wh position', 'Auxiliary position', 'Typed gaps'],
    context: 'Compare the fronted “What” in C2 with the NP gap inside the lower VP. Locate “is” in C1 and the separate PROG gap.',
    recap: ['C2 is the wh position above C1 in this tree.', 'The NP object gap and the PROG gap stay in their respective positions.'],
  },
  'br-10': {
    topics: ['The To-infinitive VP', 'Untensed To and Its VP Complement', 'Reading the Infinitival VP', 'Locating the Tense Feature'],
    steps: ['Lower VP', 'Untensed auxiliary', 'Higher VP'],
    context: 'Find “to” under the [-tense] feature, then follow its sister branch down to the lexical VP. The example shows the non-finite VP fragment.',
    recap: ['Infinitival “to” carries [-tense] in this analysis.', 'The lexical VP is its complement.'],
  },
  'br-11': {
    topics: ['From Examples to Grammar Rules', 'Finite Rules and Open-ended Combinations', 'Reading the Sentence Examples', 'Applying the Rule Again'],
    context: 'Compare the two short sentences with the example joined by “and”. Consider what the same combination rule could take as input the next time.',
    recap: ['A finite rule can be applied repeatedly.', 'A grammar describes structure as well as which sentences its rules admit.'],
  },
};

export function foundationsArticle(lesson) {
  const chapter = chapterPages[lesson.lesson_id];
  if (!chapter) return null;
  return {
    headings: [`Introduction to ${chapter.topics[0]}`, ...chapter.topics.slice(1), 'Chapter Recap', 'Chapter Post-test'],
    teach(body, page, ui) {
      const { el } = ui;
      if (page === 0) body.append(el('p', lesson.outcomes[0].text));
      if (page === 1) {
        for (const block of lesson.teaching) body.append(el('p', block.text));
      }
      if (page === 2) addWorkedExample(body, ui, chapter.steps);
      if (page === 3) {
        body.append(el('p', chapter.context));
        for (const insight of lesson.cambridge_insights) {
          body.append(el('h3', 'Cambridge insight'), el('p', insight.text));
        }
      }
      if (page === 4) {
        const list = el('ul', undefined, 'constituent-recap');
        for (const text of chapter.recap) list.append(el('li', text));
        body.append(list);
      }
    },
    postTestIntro: 'Apply the chapter’s example and explanation to the questions below. Check each answer before continuing.',
  };
}

export function addWorkedExample(body, { el, button, lesson, showWorkedTree }, labels) {
  const worked = lesson.worked_example;
  body.append(el('p', worked.sentence, 'lesson-example-sentence'));
  if (!worked.tree) {
    const steps = el('ol');
    for (const step of worked.steps) steps.append(el('li', step.text));
    body.append(steps);
    return;
  }
  const controls = el('div', undefined, 'constituent-controls lesson-tree-steps');
  controls.setAttribute('role', 'group');
  controls.setAttribute('aria-label', 'Explore the worked tree');
  const diagram = el('div', undefined, 'constituent-diagram');
  const caption = el('p', undefined, 'constituent-caption');
  caption.setAttribute('aria-live', 'polite');
  const choices = worked.steps.map((step, index) => button(labels[index], () => select(index)));
  function select(index) {
    choices.forEach((choice, position) => choice.setAttribute('aria-pressed', String(position === index)));
    const step = worked.steps[index];
    caption.textContent = step.text;
    showWorkedTree(diagram, step.focus_node_id).after(caption);
  }
  controls.append(...choices);
  body.append(controls, diagram);
  select(0);
}
