import assert from 'node:assert/strict';
import { BUILDERS, questionPool } from '../web/js/quiz/index.js';
import { isQuizAnswerCorrect } from '../web/js/quiz/answer.js';
import { MATRIX_SECTIONS } from '../web/js/quiz-data.js';

function contextKey(question) {
  const comma = question.bad.search(/[,;]/);
  const context = comma < 0 ? question.bad : question.bad.slice(comma + 1);
  return context.toLowerCase().replace(/[^a-z0-9']+/g, ' ').trim();
}

const batches = [[1, 4], [5, 8], [9, 11]];
for (const [first, last] of batches) {
  let reviewed = 0;
  for (const section of MATRIX_SECTIONS.filter((item) => item.id >= first && item.id <= last)) {
    for (const rule of section.rules) {
      const build = BUILDERS[rule.id];
      assert.equal(typeof build, 'function', `Missing builder for ${rule.id}`);
      const mergedTiers = [];
      for (const difficulty of ['easy', 'medium', 'hard']) {
        const fullPool = build(difficulty) || [];
        assert.ok(fullPool.every((item) => item.bad && item.good && item.bad !== item.good),
          `${rule.id} ${difficulty} contains an invalid correction pair`);
        mergedTiers.push(...fullPool);
      }

      const sample = questionPool(rule.id, 5);
      assert.equal(sample.length, 5, `${rule.id} must supply five questions`);
      assert.equal(new Set(sample.map((item) => item.bad)).size, 5,
        `${rule.id} contains duplicate questions in the sample`);
      assert.ok(sample.every((item) => item.bad && item.good && item.bad !== item.good),
        `${rule.id} contains an invalid correction pair`);

      const distinctContexts = new Set(mergedTiers.map(contextKey)).size;
      if (distinctContexts >= 5) {
        assert.equal(new Set(sample.map(contextKey)).size, 5,
          `${rule.id} repeats a sentence context in the sample`);
      }
      reviewed += 1;
    }
  }
  console.log(`Sections ${first}-${last}: reviewed ${reviewed} rule pools.`);
}

for (const difficulty of ['easy', 'medium', 'hard']) {
  const items = BUILDERS['6.16'](difficulty);
  assert.ok(items.length >= 5, `6.16 ${difficulty} has too few conditional scenarios`);
  assert.ok(items.every(({ bad, good }) => !/^If (?:The|My|He|She|Tom|Anna)\b/.test(bad)
    && !/^If (?:The|My|He|She|Tom|Anna)\b/.test(good)),
  `6.16 ${difficulty} has incorrect conditional capitalization`);
  if (difficulty === 'hard') {
    assert.ok(items.every(({ bad }) => !bad.includes('would succeed')),
      '6.16 hard repeats its fixed consequence');
  }
}

const danglingSubjects = [
  'the rain', 'the weather', 'the phone', 'the sky', 'the bus', 'the house',
  'the car', 'the stone', 'the table', 'the book', 'the chair', 'the plan',
];
for (const difficulty of ['easy', 'medium', 'hard']) {
  const questions = BUILDERS['9.11'](difficulty);
  assert.ok(questions.length >= 5, `9.11 ${difficulty} has too few dangling-modifier questions`);
  assert.ok(questions.every(({ bad }) =>
    danglingSubjects.some((subject) => bad.toLowerCase().includes(`, ${subject} `))),
  `9.11 ${difficulty} includes a subject that may not make the modifier dangling`);
}

console.log('Quiz question-bank audit passed.');

BUILDERS.__broken_test__ = () => {
  throw new Error('test builder failure');
};
try {
  assert.throws(() => questionPool('__broken_test__'), /test builder failure/,
    'Question-generation errors must not be converted into empty pools');
} finally {
  delete BUILDERS.__broken_test__;
}

const expected = 'The students finished the repairs.';
assert.equal(isQuizAnswerCorrect('the students finished the repairs!', expected, {
  summary: { verdict: 'grammatical', valid: true },
}), true, 'Answer comparison should ignore case and terminal punctuation');
assert.equal(isQuizAnswerCorrect(expected, expected, {
  summary: { verdict: 'ungrammatical', valid: false, violated_edges: 1 },
}), false, 'A keyed answer rejected by syntax analysis must not be scored correct');
assert.equal(isQuizAnswerCorrect(expected, expected, {
  summary: { verdict: 'grammatical', valid: true },
  node_details: { token: { status: 'error' } },
}), false, 'An error-marked tree node must prevent a success verdict');
assert.equal(isQuizAnswerCorrect('A different grammatical sentence.', expected, {
  summary: { verdict: 'grammatical', valid: true },
}), false, 'A grammatical alternative must not masquerade as the keyed answer');
console.log('Quiz answer-verdict checks passed.');
