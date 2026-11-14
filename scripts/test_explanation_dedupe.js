import assert from 'node:assert/strict';
import { hasOwnLexicalExplanation, shouldCollapseExplanation } from '../web/js/explanation-dedupe.js';

// Words always keep their own explanation. This is the reported regression:
// after selecting C2 "Who", selecting the word "Who" again must not become
// "Same explanation as the enclosing C2".
const whoWord = { id: 'w', word: 'Who' };
assert.equal(hasOwnLexicalExplanation(whoWord), true);
assert.equal(shouldCollapseExplanation(whoWord, 'Who is the wh-phrase.', 'Who is the wh-phrase.'), false);

// Lexical wrappers (C2, pronoun, DET, N, V, ...) are not collapsed onto their
// parent either.
const c2 = { id: 'c2', label: 'C2', children: [] };
const pronoun = { id: 'p', label: 'pronoun', children: [] };
const det = { id: 'd', label: 'DET', children: [] };
assert.equal(hasOwnLexicalExplanation(c2), true);
assert.equal(hasOwnLexicalExplanation(pronoun), true);
assert.equal(hasOwnLexicalExplanation(det), true);
assert.equal(shouldCollapseExplanation(c2, 'same', 'same'), false);
assert.equal(shouldCollapseExplanation(pronoun, 'same', 'same'), false);
assert.equal(shouldCollapseExplanation(det, 'same', 'same'), false);

// Structural layers still collapse when the paragraph is genuinely identical.
for (const label of ['S', 'NP', 'VP', 'NOM', 'PP', 'AP', 'AdvP', 'S-bar']) {
  assert.equal(hasOwnLexicalExplanation({ label }), false);
  assert.equal(shouldCollapseExplanation({ label }, 'same', 'same'), true);
}

// Empty and gap positions keep their own description.
assert.equal(hasOwnLexicalExplanation({ gap: true }), true);
assert.equal(hasOwnLexicalExplanation({ empty: true }), true);
assert.equal(hasOwnLexicalExplanation({ triangle: true, words: ['x'] }), true);
assert.equal(shouldCollapseExplanation({ gap: true }, 'same', 'same'), false);
assert.equal(shouldCollapseExplanation({ empty: true }, 'same', 'same'), false);

// Different text, missing parent text, or missing text never collapses.
assert.equal(shouldCollapseExplanation({ label: 'NP' }, 'child', 'parent'), false);
assert.equal(shouldCollapseExplanation({ label: 'NP' }, 'same', null), false);
assert.equal(shouldCollapseExplanation({ label: 'NP' }, '', ''), false);

console.log('explanation-dedupe tests passed');
