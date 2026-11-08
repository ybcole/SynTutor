import assert from 'node:assert/strict';
import { createLayout } from '../web/js/renderer.js';
import { correctionPreview, matchesPreviewTokens } from '../web/js/correction.js';

let id = 0;
const leaf = surface => ({ id: String(++id), surface, type: 'NN' });
const branch = (type, ...children) => ({ id: String(++id), type, children });
const measure = label => [...label].length * 10;
const wide = branch('S', ...Array.from({ length: 15 }, (_, i) =>
  branch(i === 3 ? 'Extended construction label' : 'NP', leaf(i === 4 ? 'disproportionately' : 'and'))));
let deep = leaf('word');
for (let n = 0; n < 20; n++) deep = branch('VP', leaf('then'), deep);

for (const root of [branch('S', leaf('birds'), leaf('sing')), wide, deep]) {
  for (const viewport of [360, 768, 1440]) {
    const result = createLayout(root, measure, viewport);
    const rows = new Map();
    for (const item of result.layout.values()) {
      if (!rows.has(item.y)) rows.set(item.y, []);
      rows.get(item.y).push(item);
    }
    for (const row of rows.values()) {
      row.sort((a, b) => a.x - b.x);
      for (const [i, node] of row.entries()) {
        assert(node.x - node.w / 2 >= 0 && node.x + node.w / 2 <= result.totalW);
        if (i) {
          const prev = row[i - 1];
          assert(node.x - node.w / 2 - (prev.x + prev.w / 2) >= 16);
        }
        for (const child of node.node.children || []) {
          const target = result.layout.get(child.id);
          const bounds = result.bounds.get(node.id);
          assert(target.x > bounds.left && target.x < bounds.right);
          assert(target.y - node.y >= 62);
        }
      }
    }
  }
}
assert(createLayout(wide, measure, 390).totalW < 15 * (measure('disproportionately') + 28 + 26));

function check(source, tokens, edit, expected) {
  const payload = { meta: { target_sentence: 1 },
    parse: { text: source, sentences: [{ start: 10 }],
      tokens: tokens.map(([start, end]) => ({ start: start + 10, end: end + 10 })) } };
  assert.deepEqual(correctionPreview(payload, edit), expected);
}
check('The birds sings.', [[0, 3], [4, 9], [10, 15], [15, 16]],
  { start: 2, end: 3, text: 'sing' }, { text: 'The birds sing.', removed: 'sings', added: 'sing' });
check('She bought book.', [[0, 3], [4, 10], [11, 15], [15, 16]],
  { start: 2, end: 2, text: 'a' }, { text: 'She bought a book.', removed: '', added: 'a' });
check('They left today.', [[0, 4], [5, 9], [10, 15], [15, 16]],
  { start: 2, end: 3, text: '' }, { text: 'They left.', removed: 'today', added: '' });
check('They left', [[0, 4], [5, 9]],
  { start: 2, end: 2, text: '?' }, { text: 'They left?', removed: '', added: '?' });
check('🦉 I do not sing.', [[0, 1], [2, 3], [4, 6], [7, 10], [11, 15], [15, 16]],
  { start: 2, end: 4, text: "don't" }, { text: "🦉 I don't sing.", removed: 'do not', added: "don't" });
console.log('PASS: shallow, deep and wide layouts at three widths and five correction shapes.');

const parsed = {
  parse: {
    text: 'Birds (sing).', sentences: [{ start: 0 }],
    tokens: [
      { t: 'Birds', start: 0, end: 5 }, { t: '(', start: 6, end: 7 },
      { t: 'sing', start: 7, end: 11 }, { t: ')', start: 11, end: 12 },
      { t: '.', start: 12, end: 13 },
    ],
  },
  tree: { children: ['Birds', '-LRB-', 'sing', '-RRB-', '.'].map((surface, i) =>
    ({ surface, span: [i, i + 1] })) },
};
assert(matchesPreviewTokens(parsed, parsed.parse.text));
assert(!matchesPreviewTokens(parsed, 'Birds (sing)!'));
const wrongWord = structuredClone(parsed);
wrongWord.tree.children[2].surface = 'sings';
assert(!matchesPreviewTokens(wrongWord, parsed.parse.text));
const wrongOrder = structuredClone(parsed);
wrongOrder.tree.children.reverse();
assert(!matchesPreviewTokens(wrongOrder, parsed.parse.text));
const missingWord = structuredClone(parsed);
missingWord.parse.tokens.pop();
missingWord.tree.children.pop();
assert(!matchesPreviewTokens(missingWord, parsed.parse.text));
console.log('PASS: corrected tree rejects stale leaf text, wrong order and uncovered punctuation.');
