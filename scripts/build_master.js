// Masterfile generator.
//
// Combines the authoring sources into one table the whole SynTutor reads:
//   - rule catalog            (web/js/quiz/catalog.js)
//   - question generators     (web/js/quiz/s1.js .. s11.js, via ./quiz/index.js)
//   - rule concept "what" texts (web/js/quiz/concepts.js)
//
// Output: web/content/master.json  (generated — edit the sources, not this file)
//
//   npm run build:master
//
// The file keeps the catalog pretty-printed but writes each quiz item on its
// own line, so a human can add or tweak questions directly if they want.

import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { MATRIX_SECTIONS, ruleDifficulty } from '../web/js/quiz/catalog.js';
import { RULE_CONCEPTS } from '../web/js/quiz/concepts.js';
import { materializePool } from '../web/js/quiz/index.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const outFile = join(root, 'web', 'content', 'master.json');
const quizLength = 5;

const sections = [];
const questions = {};
const catalogIds = new Set();
let ruleCount = 0;
let questionCount = 0;
const missingConcept = [];
const missingQuestions = [];

for (const section of MATRIX_SECTIONS) {
  const rules = [];
  for (const rule of section.rules) {
    catalogIds.add(rule.id);
    ruleCount += 1;
    const concept = RULE_CONCEPTS[rule.id];
    if (!concept) missingConcept.push(rule.id);
    rules.push({
      id: rule.id,
      rule: rule.rule,
      example: rule.example,
      check: rule.check,
      difficulty: ruleDifficulty(rule),
      concept: concept || '',
    });
    const pool = materializePool(rule.id);
    if (pool.length) {
      questions[rule.id] = pool.map((item) => {
        const out = { bad: item.bad, good: item.good, explanation: item.explanation };
        if (Array.isArray(item.sentences)) {
          out.sentences = item.sentences.map(({ bad, good }) => ({ bad, good }));
        }
        return out;
      });
      questionCount += pool.length;
    } else {
      missingQuestions.push(rule.id);
    }
  }
  sections.push({ id: section.id, title: section.title, rules });
}

for (const id of Object.keys(RULE_CONCEPTS)) {
  if (!catalogIds.has(id)) {
    console.warn(`[build:master] concept ${id} has no catalog rule (typo?)`);
  }
}
if (missingConcept.length) {
  console.warn(`[build:master] rules without a concept: ${missingConcept.join(', ')}`);
}
if (missingQuestions.length) {
  console.warn(`[build:master] rules without questions: ${missingQuestions.join(', ')}`);
}

const master = {
  generatedAt: new Date().toISOString().slice(0, 10),
  quizLength,
  ruleCount,
  questionCount,
  sections,
  questions,
};

function indent(text, pad) {
  const prefix = ' '.repeat(pad);
  return text.split('\n').map((line, i) => (i ? prefix + line : line)).join('\n');
}

function serialize(data) {
  const lines = [];
  lines.push('{');
  lines.push(`  "generatedAt": ${JSON.stringify(data.generatedAt)},`);
  lines.push(`  "quizLength": ${data.quizLength},`);
  lines.push(`  "ruleCount": ${data.ruleCount},`);
  lines.push(`  "questionCount": ${data.questionCount},`);
  lines.push(`  "sections": ${indent(JSON.stringify(data.sections, null, 2), 2)},`);
  lines.push('  "questions": {');
  const ids = Object.keys(data.questions);
  ids.forEach((id, index) => {
    const items = data.questions[id];
    const comma = index < ids.length - 1 ? ',' : '';
    lines.push(`    ${JSON.stringify(id)}: [`);
    items.forEach((item, j) => {
      const itemComma = j < items.length - 1 ? ',' : '';
      lines.push(`      ${JSON.stringify(item)}${itemComma}`);
    });
    lines.push(`    ]${comma}`);
  });
  lines.push('  }');
  lines.push('}');
  return `${lines.join('\n')}\n`;
}

mkdirSync(dirname(outFile), { recursive: true });
writeFileSync(outFile, serialize(master));

console.log(`[build:master] ${ruleCount} rules, ${questionCount} questions -> web/content/master.json`);
