import assert from 'node:assert/strict';
import { BUILDERS, questionPool } from '../web/js/quiz/index.js';
import { isParagraphQuizAnswerCorrect } from '../web/js/quiz/answer.js';

const hardPool = BUILDERS['1.1']('hard');
assert.equal(hardPool.length, 40, '1.1 Hard must retain its 40-question pool');
assert.equal(new Set(hardPool.map((item) => item.bad)).size, 40,
  '1.1 Hard must contain 40 distinct paragraphs');

const correctionCounts = new Set();
const correctedPositions = new Set();
for (const [index, item] of hardPool.entries()) {
  assert.equal(item.sentences.length, 4,
    `1.1 Hard paragraph ${index + 1} must contain four sentences`);
  assert.equal(item.bad, item.sentences.map((sentence) => sentence.bad).join(' '),
    '1.1 Hard paragraphs must render as a single flowing line (no newlines)');
  assert.equal(item.good, item.sentences.map((sentence) => sentence.good).join(' '),
    '1.1 Hard corrected paragraphs must render as a single flowing line');
  assert.ok(!/[\r\n]/.test(item.bad) && !/[\r\n]/.test(item.good),
    `1.1 Hard paragraph ${index + 1} must not contain newline characters`);
  const corrected = item.sentences
    .map((sentence, sentenceIndex) => sentence.bad !== sentence.good ? sentenceIndex + 1 : null)
    .filter(Boolean);
  assert.ok(corrected.length >= 2 && corrected.length <= 3,
    `1.1 Hard paragraph ${index + 1} must have two or three plural errors`);
  assert.ok(item.sentences.some((sentence) => sentence.bad === sentence.good),
    `1.1 Hard paragraph ${index + 1} must include an already-correct sentence`);
  for (const sentence of item.sentences.filter((entry) => entry.bad !== entry.good)) {
    const badWords = sentence.bad.match(/[A-Za-z]+(?:['’][A-Za-z]+)?/g);
    const goodWords = sentence.good.match(/[A-Za-z]+(?:['’][A-Za-z]+)?/g);
    assert.equal(badWords.length, goodWords.length,
      `1.1 Hard paragraph ${index + 1} changes unrelated sentence structure`);
    assert.equal(badWords.filter((word, wordIndex) => word !== goodWords[wordIndex]).length, 1,
      `1.1 Hard paragraph ${index + 1} must isolate one plural-form error per sentence`);
  }
  correctionCounts.add(corrected.length);
  correctedPositions.add(corrected.join(','));
}

assert.ok(correctionCounts.size > 1, 'The number of corrections should vary');
assert.ok(correctedPositions.size > 1, 'Correction locations should vary by paragraph');

const sample = questionPool('1.1', 5);
assert.equal(sample.length, 5, 'Each quiz session must still draw five questions');
assert.ok(sample.every((item) => item.sentences.length === 4),
  'Sampling must retain each complete paragraph');
assert.equal(BUILDERS['1.1']('easy').some((item) => item.sentences), false,
  'The easy question format must remain unchanged');
assert.equal(BUILDERS['1.1']('medium').some((item) => item.sentences), false,
  'The medium question format must remain unchanged');

const sampleParagraph = sample[0];
const validLinePayload = { summary: { verdict: 'grammatical', valid: true } };
const goodSentences = sampleParagraph.sentences.map((sentence) => sentence.good);
const paragraphPayloads = sampleParagraph.sentences.map(() => validLinePayload);
assert.equal(isParagraphQuizAnswerCorrect(
  goodSentences,
  goodSentences,
  paragraphPayloads,
), true, 'Paragraph grading should accept fully corrected sentence segmentation');
assert.equal(isParagraphQuizAnswerCorrect(
  goodSentences,
  goodSentences,
  paragraphPayloads.map((_, index) => index === 1
    ? { summary: { verdict: 'ungrammatical', valid: false } }
    : validLinePayload),
), false, 'An incorrect sentence verdict must fail the whole paragraph');
assert.equal(isParagraphQuizAnswerCorrect(
  goodSentences,
  goodSentences,
  paragraphPayloads.map((_, index) => index === 0 ? null : validLinePayload),
), false, 'An unavailable sentence parse must not count as a correct paragraph');
assert.equal(isParagraphQuizAnswerCorrect(
  goodSentences.slice(0, 3),
  goodSentences,
  paragraphPayloads,
), false, 'A paragraph missing a sentence must fail grading');

console.log('1.1 Hard paragraph-pool checks passed (40 single-line paragraphs; 5-question sample).');
