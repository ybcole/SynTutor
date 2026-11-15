import { cambridgeChapterData } from './cambridge-chapter-data.js?v=2026.11.16c';

function articleForChapter(chapter) {
  const dynamic = Array.isArray(chapter.sections) && chapter.sections.length > 0;
  const headings = dynamic
    ? [...chapter.sections.map(section => section.title), 'Check what you learned']
    : ['Introduction', 'Key ideas', 'Worked example', 'Application', 'Recap', 'Check what you learned'];
  const sections = dynamic
    ? [...chapter.sections.map(section => ({ id: section.id, title: section.title, advances: section.advances })),
       { id: 'closing-check', title: 'Check what you learned', assessment: true }]
    : undefined;
  return {
    headings,
    sections,
    openingCheck(lesson) {
      return [lesson.predict, ...(chapter.opening || []).map(([prompt, choices, correct]) => ({
        prompt,
        answer: String(correct),
        options: choices.map((text, index) => ({ id: String(index), text })),
      }))];
    },
    postTestIntro: chapter.postTestIntro,
    references: [],
    teach(body, page, ui) {
      const { el } = ui;
      const paragraphs = value => (Array.isArray(value) ? value : [value]).filter(Boolean);
      const rich = (parent, text, tag = 'p') => {
        const node = el(tag);
        const pattern = /(\*[^*]+\*|“[^”]+”)/g;
        let cursor = 0;
        for (const match of text.matchAll(pattern)) {
          if (match.index > cursor) node.append(document.createTextNode(text.slice(cursor, match.index)));
          const token = match[0];
          node.append(el('em', token.startsWith('*') ? token.slice(1, -1) : token, 'lesson-object-language'));
          cursor = match.index + token.length;
        }
        if (cursor < text.length) node.append(document.createTextNode(text.slice(cursor)));
        parent.append(node);
      };
      const renderCheck = check => {
        if (!check) return;
        const details = el('details');
        details.append(el('summary', 'Quick check'));
        details.append(el('p', check.prompt));
        const list = el('ul');
        for (const option of check.options || []) {
          list.append(el('li', option.text + (option.feedback ? ' — ' + option.feedback : '')));
        }
        details.append(list);
        body.append(details);
      };
      const renderConcept = (title, content) => {
        body.append(el('h3', title));
        if (content && typeof content === 'object' && !Array.isArray(content)) {
          for (const paragraph of paragraphs(content.paragraphs)) rich(body, paragraph);
          renderCheck(content.check);
          return;
        }
        for (const paragraph of paragraphs(content)) rich(body, paragraph);
      };
      const appendObjectLanguage = (parent, text) => {
        const label = text.match(/^([^:]{1,40}:)\s+/);
        if (label) parent.append(document.createTextNode(label[1] + ' '));
        const content = (label ? text.slice(label[0].length) : text).replace(/\*/g, '');
        for (const part of content.split(/(\[|\]|→)/)) {
          if (!part) continue;
          if (/^[\[\]→]$/.test(part)) parent.append(document.createTextNode(part));
          else parent.append(el('em', part, 'lesson-object-language'));
        }
      };
      const renderBlock = block => {
        if (!block || !block.type) return;
        if (block.type === 'subheading') {
          body.append(el('h4', block.text));
        } else if (block.type === 'paragraph') {
          rich(body, block.text);
        } else if (block.type === 'examples') {
          if (block.title) body.append(el('h4', block.title));
          const list = el('div', undefined, 'lesson-example-set');
          for (const example of block.items || []) {
            const item = el('div', undefined, 'lesson-example');
            const line = el('p', undefined, 'lesson-example-sentence');
            const mark = example.mark === 'bad' ? '*' : example.mark === 'ambiguous' ? '?' : '';
            if (mark) line.append(document.createTextNode(mark + ' '));
            appendObjectLanguage(line, example.text);
            item.append(line);
            if (example.note) item.append(el('p', example.note, 'lesson-example-note'));
            list.append(item);
          }
          body.append(list);
        } else if (block.type === 'table') {
          if (block.title) body.append(el('h4', block.title));
          const table = el('table', undefined, 'lesson-comparison-table');
          const head = el('tr');
          head.append(...(block.columns || []).map(column => el('th', column)));
          table.append(head);
          for (const row of block.rows || []) {
            const tr = el('tr');
            tr.append(...row.map(cell => el('td', cell)));
            table.append(tr);
          }
          body.append(table);
        } else if (block.type === 'diagnostic') {
          const aside = el('aside', undefined, 'lesson-diagnostic');
          aside.append(el('h4', block.title));
          const list = el('ol');
          for (const step of block.steps || []) list.append(el('li', step));
          aside.append(list);
          if (block.conclusion) aside.append(el('p', block.conclusion));
          body.append(aside);
        } else if (block.type === 'note') {
          const aside = el('aside', undefined, block.tone === 'watch' ? 'lesson-watch' : 'lesson-why');
          if (block.title) aside.append(el('h4', block.title));
          aside.append(el('p', block.text));
          body.append(aside);
        }
      };
      const sections = blocks => {
        for (const [title, content] of blocks) renderConcept(title, content);
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
      if (dynamic) {
        const section = chapter.sections[page];
        if (!section) return;
        if (Array.isArray(section.blocks)) {
          for (const block of section.blocks) renderBlock(block);
        } else {
          for (const paragraph of paragraphs(section.paragraphs)) rich(body, paragraph);
        }
        renderCheck(section.check);
        return;
      }
      if (page === 0) {
        for (const paragraph of paragraphs(chapter.intro)) body.append(el('p', paragraph));
      } else if (page === 1) {
        sections(chapter.concepts);
      } else if (page === 2) {
        const worked = lesson.worked_example || {};
        if (worked.sentence) body.append(el('p', worked.sentence, 'lesson-example-sentence'));
        for (const step of worked.steps || []) {
          if (step.text) body.append(el('p', step.text));
        }
        if (!worked.sentence && chapter.worked) {
          for (const paragraph of paragraphs(chapter.worked)) body.append(el('p', paragraph));
        }
      } else if (page === 3) {
        for (const paragraph of paragraphs(chapter.application || chapter.apply)) body.append(el('p', paragraph));
      } else if (page === 4) {
        for (const paragraph of paragraphs(chapter.recap || chapter.recapSummary)) body.append(el('p', paragraph));
        const selfChecks = chapter.selfCheck || [];
        for (const item of selfChecks) {
          if (item && typeof item === 'object') {
            const details = el('details');
            details.append(el('summary', item.question));
            details.append(el('p', item.answer));
            body.append(details);
          } else if (item) {
            body.append(el('p', item));
          }
        }
      }
    },
  };
}

export const cambridgeChapterArticles = Object.fromEntries(
  Object.entries(cambridgeChapterData).map(([id, chapter]) => [id, articleForChapter(chapter)]),
);
