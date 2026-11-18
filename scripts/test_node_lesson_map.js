import fs from 'node:fs';
import { SYNTAX_NODE_LESSONS, WORD_NODE_LESSONS } from '../web/js/node-lessons.js';
import INVENTORY from '../web/js/builder-inventory.js';
import { constituentsPilot } from '../web/js/constituents-pilot.js';
import { functionsPilot } from '../web/js/functions-pilot.js';
import { categoriesPilot } from '../web/js/categories-pilot.js';
import { basicVpPilot } from '../web/js/basic-vp-pilot.js';
import { adverbialsPilot } from '../web/js/adverbials-pilot.js';
import { auxiliariesPilot } from '../web/js/auxiliaries-pilot.js';
import { nounPhrasesPilot } from '../web/js/noun-phrases-pilot.js';
import { embeddedClausesPilot } from '../web/js/embedded-clauses-pilot.js';
import { whClausesPilot } from '../web/js/wh-clauses-pilot.js';
import { nonFinitePilot } from '../web/js/non-finite-pilot.js';
import { grammarPilot } from '../web/js/grammar-pilot.js';

const PILOTS = { 'br-01': constituentsPilot, 'br-02': functionsPilot, 'br-03': categoriesPilot, 'br-04': basicVpPilot, 'br-05': adverbialsPilot, 'br-06': auxiliariesPilot, 'br-07': nounPhrasesPilot, 'br-08': embeddedClausesPilot, 'br-09': whClausesPilot, 'br-10': nonFinitePilot, 'br-11': grammarPilot };

const course = JSON.parse(fs.readFileSync('web/content/lessons/course.json', 'utf8'));
const lessons = new Map(course.lessons.map((l) => [l.lesson_id, l]));
const cache = new Map();
const chapterFor = (lesson) => lesson === 'cgel-clauses' ? '02' : lesson.slice(-2);
const readChapter = (lesson) => {
  const ch = chapterFor(lesson);
  if (!cache.has(ch)) cache.set(ch, JSON.parse(fs.readFileSync(`web/content/lessons/cambridge-authored/ch${ch}.json`, 'utf8')));
  return cache.get(ch);
};

for (const [label, entry] of Object.entries(SYNTAX_NODE_LESSONS)) {
  if (!entry.route.startsWith('#lesson/')) throw new Error(`${label}: bad route`);
  if (!lessons.has(entry.lesson)) throw new Error(`${label}: missing lesson ${entry.lesson}`);
  if (entry.route.startsWith('#lesson/br-')) {
    const [, lesson, section] = entry.route.split('/');
    const pilot = PILOTS[lesson];
    if (!pilot?.sections?.some((row) => row.id === section)) throw new Error(`${label}: missing B-R section ${entry.route}`);
  } else if (entry.route.startsWith('#lesson/cgel-')) {
    const chapter = readChapter(entry.lesson);
    const section = entry.route.split('/').pop();
    if (!chapter.sections.some((s) => s.id === section)) throw new Error(`${label}: missing syntax section`);
  } else {
    throw new Error(`${label}: unrecognised syntax route`);
  }
}

for (const [label, entry] of Object.entries(WORD_NODE_LESSONS)) {
  if (!entry.route.startsWith('#lesson/cgel-')) throw new Error(`${label}: word route is not Cambridge`);
  const chapter = readChapter(entry.lesson);
  if (!chapter.sections.some((s) => s.id === entry.section)) throw new Error(`${label}: missing word section`);
}

const mapped = new Set([...Object.keys(SYNTAX_NODE_LESSONS), ...Object.keys(WORD_NODE_LESSONS)]);
const missing = [...Object.keys(INVENTORY.labels), ...Object.keys(INVENTORY.features)].filter((label) => !mapped.has(label));
if (missing.length) throw new Error(`Unmapped inventory labels: ${missing.join(', ')}`);

console.log(`PASS: ${Object.keys(SYNTAX_NODE_LESSONS).length} syntax routes and ${Object.keys(WORD_NODE_LESSONS).length} Cambridge word routes verified.`);
