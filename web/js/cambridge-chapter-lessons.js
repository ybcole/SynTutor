import { cambridgeChapterData } from './cambridge-chapter-data.js';

function articleForChapter(chapter) {
  return {
    headings: [
      `Introduction to ${chapter.topics[0]}`,
      ...chapter.topics.slice(1),
      'Chapter recap',
      'Check what you learned',
    ],
    openingCheck(lesson) {
      return [lesson.predict, ...chapter.opening.map(([prompt, choices, correct]) => ({
        prompt,
        answer: String(correct),
        options: choices.map((text, index) => ({ id: String(index), text })),
      }))];
    },
    postTestIntro: chapter.postTestIntro,
    references: [],
    teach(body, page, ui) {
      const { el } = ui;
      const sections = blocks => {
        for (const [title, text] of blocks) body.append(el('h3', title), el('p', text));
      };
      const list = items => {
        const container = el('ul');
        container.append(...items.map(item => el('li', item)));
        body.append(container);
      };
      const reveal = (label, text, example) => {
        const details = el('details');
        details.append(el('summary', label));
        if (example) details.append(el('p', example, 'lesson-example-sentence'));
        details.append(el('p', text));
        body.append(details);
      };
      if (page === 0) {
        body.append(el('h3', 'What this chapter covers'), el('p', chapter.intro));
        body.append(el('p', chapter.exampleContext));
        body.append(el('p', chapter.example, 'lesson-example-sentence'));
        body.append(el('p', chapter.introExample));
        body.append(el('h3', 'What you’ll see in this chapter'));
        list(chapter.preview);
      } else if (page === 1) {
        sections(chapter.concepts);
      } else if (page === 2) {
        sections([chapter.contrast]);
      } else if (page === 3) {
        body.append(el('p', chapter.applyExample, 'lesson-example-sentence'));
        sections(chapter.apply);
        reveal(chapter.reveal[0], chapter.reveal[1], chapter.example);
      } else if (page === 4) {
        body.append(el('p', chapter.recapSummary));
        list(chapter.recap);
        body.append(el('h3', 'Check yourself'));
        list(chapter.selfCheck);
      }
    },
  };
}

export const cambridgeChapterArticles = Object.fromEntries(
  Object.entries(cambridgeChapterData).map(([id, chapter]) => [id, articleForChapter(chapter)]),
);
