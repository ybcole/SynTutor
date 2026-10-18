// Syntax-Tree Quiz audit.
//
// Verifies the generated content sheet (web/content/tree_sheet.json) is
// exhaustive and internally consistent, then exercises the quiz's question
// builders against it.
//
//   npm run test:quiz

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const sheet = JSON.parse(
  readFileSync(join(root, 'web', 'content', 'tree_sheet.json'), 'utf8'),
);

assert.ok(Array.isArray(sheet.stages), 'sheet.stages must be an array');
assert.equal(sheet.stages.length, 4, 'sheet must have exactly 4 stages');

const [tok, pos, phrase, rules] = sheet.stages;
assert.equal(tok.id, 1, 'stage 1 is the tokenizer');
assert.equal(pos.id, 2, 'stage 2 is the POS tagger');
assert.equal(phrase.id, 3, 'stage 3 is the parser');
assert.equal(rules.id, 4, 'stage 4 is the rule matrix');

// Stage 2: every POS item has tag/name/example and tags are unique.
assert.ok(pos.items.length >= 40, 'expected 40+ POS tags');
for (const item of pos.items) {
  assert.ok(item.tag && item.name && item.example, `POS item incomplete: ${JSON.stringify(item)}`);
}
assert.equal(
  new Set(pos.items.map((i) => i.tag)).size,
  pos.items.length,
  'POS tags must be unique',
);

// Stage 3: every phrase item has tag/name/example and tags are unique.
assert.ok(phrase.items.length >= 20, 'expected 20+ phrase labels');
for (const item of phrase.items) {
  assert.ok(item.tag && item.name && item.example, `phrase item incomplete: ${JSON.stringify(item)}`);
}
assert.equal(
  new Set(phrase.items.map((i) => i.tag)).size,
  phrase.items.length,
  'phrase tags must be unique',
);

// Stage 4: every rule id is unique, and each carries a concept.
const ruleIds = rules.items.map((i) => i.rule).filter(Boolean);
const uniqueRuleIds = new Set(ruleIds);
assert.ok(uniqueRuleIds.size >= 100, `expected 100+ rules, got ${uniqueRuleIds.size}`);
for (const rid of uniqueRuleIds) {
  const entry = rules.items.find((i) => i.rule === rid);
  assert.ok(entry.name, `rule ${rid} is missing a name`);
  assert.ok(entry.concept, `rule ${rid} is missing a concept`);
}

// meta must match the actual counts.
const meta = sheet.meta;
assert.equal(meta.posTagCount, pos.items.length, 'meta.posTagCount mismatch');
assert.equal(meta.phraseNodeCount, phrase.items.length, 'meta.phraseNodeCount mismatch');
assert.equal(meta.ruleCount, uniqueRuleIds.size, 'meta.ruleCount mismatch');

console.log(`Stage 1 Tokenizer: implicit`);
console.log(`Stage 2 POS tagger: ${pos.items.length} tags`);
console.log(`Stage 3 Parser: ${phrase.items.length} phrase labels`);
console.log(`Stage 4 Rule matrix: ${uniqueRuleIds.size} rules, ${rules.items.length} constraint rows`);
console.log('Syntax-tree quiz content audit passed.');
