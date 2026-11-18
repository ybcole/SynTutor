import assert from 'node:assert/strict';
import fs from 'node:fs';
import {loadActiveCourse, quizCurriculum} from '../web/js/lesson-curriculum.js';
import {
  findStaleSyntaxSources,
  makeLessonPractice,
  syntaxPracticeDigest,
  validateSyntaxPracticeSource,
} from '../web/js/quiz-lesson-practice.js';

const json = p => JSON.parse(fs.readFileSync(new URL('../' + p, import.meta.url), 'utf8'));
const course = await loadActiveCourse(async p => ({ok: true, json: async () => json('web' + p)}));
const curriculum = quizCurriculum(course);
const syntaxSource = json('web/content/quizzes/syntax-practice-source.json');

// 1. Committed source must match every active Syntax chapter digest & version.
assert.deepEqual(findStaleSyntaxSources(curriculum, syntaxSource), []);
assert.equal(validateSyntaxPracticeSource(curriculum, syntaxSource), syntaxSource);
for (const chapter of curriculum.find(t => t.id === 'syntax').chapters) {
  const expected = syntaxPracticeDigest(chapter.id);
  assert.ok(expected, `missing pilot digest for ${chapter.id}`);
  for (const topic of chapter.topics) {
    const entry = syntaxSource.sections.find(s => s.lesson_id === chapter.id && s.subtopic_id === topic.id);
    assert.ok(entry, `missing syntax source section for ${chapter.id}/${topic.id}`);
    assert.equal(entry.article_digest, expected, `stale digest for ${chapter.id}/${topic.id}`);
    assert.equal(entry.lesson_version, chapter.content_version, `version mismatch for ${chapter.id}/${topic.id}`);
  }
}

// 2. Simulating a lesson prose edit must fail loudly (never silently discard items).
const staleDigest = structuredClone(syntaxSource);
for (const sec of staleDigest.sections.filter(s => s.lesson_id === 'br-01')) sec.article_digest = '00000000';
assert.ok(findStaleSyntaxSources(curriculum, staleDigest).some(s => s.chapter_id === 'br-01' && s.reason === 'digest_mismatch'));
assert.throws(() => validateSyntaxPracticeSource(curriculum, staleDigest), /Stale syntax practice source for br-01/);
assert.throws(() => makeLessonPractice(curriculum, staleDigest), /Stale syntax practice source for br-01/);

const staleVersion = structuredClone(syntaxSource);
for (const sec of staleVersion.sections.filter(s => s.lesson_id === 'br-05')) sec.lesson_version = '0.0.1';
assert.ok(findStaleSyntaxSources(curriculum, staleVersion).some(s => s.chapter_id === 'br-05' && s.reason === 'version_mismatch'));
assert.throws(() => makeLessonPractice(curriculum, staleVersion), /Stale syntax practice source for br-05/);

const recorded = [];
makeLessonPractice(curriculum, staleDigest, {onStale: list => recorded.push(...list)});
assert.ok(recorded.some(s => s.chapter_id === 'br-01'));

console.log('PASS quiz digest freshness: all 11 Syntax chapters / 50 topics match active Lessons digests; stale digests and version mismatches fail loudly.');
