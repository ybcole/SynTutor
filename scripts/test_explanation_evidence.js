import assert from 'node:assert/strict';
import { createModel, addWord, addPhrase, connect, toCanonicalEnvelope, fromCanonicalEnvelope } from '../web/js/syntax-builder.js';
import { requestEvidence, evidenceLines } from '../web/js/explanation-evidence.js';

const model = createModel();
const s = addPhrase(model, 'S', 0, 0);
const np = addPhrase(model, 'NP', 0, 70);
const vp = addPhrase(model, 'VP', 200, 70);
connect(model, s.id, np.id); connect(model, s.id, vp.id);
for (const [text, x, parent] of [['The', 0, np], ['birds', 100, np], ['sing', 200, vp]]) {
  const word = addWord(model, text, x, 140); connect(model, parent.id, word.id);
}
const tree = toCanonicalEnvelope(model, { chapter: 2, version: 'V2', profile_id: 'V2' });
assert.equal(tree.sentence, 'The birds sing');
assert.deepEqual(tree.tokens.map(token => token.char_span), [[0, 3], [4, 9], [10, 14]]);
assert.equal(tree.root.children[0].label, 'NP');
const imported = fromCanonicalEnvelope(tree);
assert.equal(toCanonicalEnvelope(imported, tree.convention_profile).sentence, tree.sentence);
const evidence = { status: 'NO_BOOK_BASIS', channels: {}, diagnostics: [] };
let request;
const fetch = async (url, options) => { request = { url, body: JSON.parse(options.body) }; return { ok: true, json: async () => evidence }; };
assert.deepEqual(await requestEvidence(tree, null, { fetch }), evidence);
assert.equal(request.url, '/api/explain');
assert.deepEqual(request.body, { tree });
assert.equal(evidenceLines(evidence)[0], 'No reviewed book evidence is available for this analysis.');
await assert.rejects(() => requestEvidence(tree, null, { fetch: async () => ({ ok: false, json: async () => ({ error: 'invalid tree' }) }) }), /invalid tree/);
assert.throws(() => toCanonicalEnvelope(createModel()), /one root/);
imported.nodes[Object.keys(imported.nodes)[0]].parent = 'missing';
assert.throws(() => toCanonicalEnvelope(imported), /one root/);
console.log('PASS: canonical Builder bridge and shared explanation request/state contract');
