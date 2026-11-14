// Print the validated local candidate. The published course remains the input.
import { readFileSync } from 'node:fs';
import { composeLessonPreview } from '../web/js/lesson-preview.js';

const read = name => JSON.parse(readFileSync(new URL(`../web/content/lessons/${name}.json`, import.meta.url), 'utf8'));
const catalog = read('course');
const pilots = catalog.lessons.filter(lesson => lesson.track === 'foundations')
  .map(({ lesson_id: id }) => [id, read(`${id}-pilot`)]);
if (pilots.length !== 11) throw new Error('Expected eleven Foundations pilots.');
console.log(JSON.stringify(composeLessonPreview(catalog, pilots), null, 2));
