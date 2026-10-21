// Regression test for the interactive corrective feedback (web/js/correction.js).
//
//   npm run test:correction
//
// The test runs against a hand-built parse payload, so it needs no backend:
// it checks the three things the feature depends on --
//   1. planFocus() finds the scope and the linked pair of an error,
//   2. applyEdit() rebuilds the sentence the way the server's edit describes,
//   3. findTargetError() re-identifies the error by constraint + context,
//      so the tutor can tell the learner that their own fix worked.

import assert from 'node:assert/strict';
import {
  planFocus, contextWords, applyEdit, expectedScopeWords, findScopeNode, findTargetError,
} from '../web/js/correction.js';

// A tiny parse of "She go to school" with a subject-verb agreement error.
function buildPayload(verb) {
  const tokens = [
    { t: 'She', start: 0, end: 3 },
    { t: verb, start: 4, end: 4 + verb.length },
    { t: 'to', start: 7, end: 9 },
    { t: 'school', start: 10, end: 16 },
  ];
  const nodes = {
    n0: { id: 'n0', type: 'S', surface: `She ${verb} to school`, span: [0, 4] },
    n1: { id: 'n1', type: 'NP', surface: 'She', span: [0, 1] },
    n2: { id: 'n2', type: 'VP', surface: `${verb} to school`, span: [1, 4] },
    n3: { id: 'n3', type: 'PRP', surface: 'She', span: [0, 1] },
    n4: { id: 'n4', type: 'VBP', surface: verb, span: [1, 2] },
    n5: { id: 'n5', type: 'PP', surface: 'to school', span: [2, 4] },
    n6: { id: 'n6', type: 'IN', surface: 'to', span: [2, 3] },
    n7: { id: 'n7', type: 'NP', surface: 'school', span: [3, 4] },
    n8: { id: 'n8', type: 'NN', surface: 'school', span: [3, 4] },
  };
  nodes.n0.children = [nodes.n1, nodes.n2];
  nodes.n1.children = [nodes.n3];
  nodes.n2.children = [nodes.n4, nodes.n5];
  nodes.n5.children = [nodes.n6, nodes.n7];
  nodes.n7.children = [nodes.n8];
  const tree = nodes.n0;
  const errored = verb === 'go';
  const node_details = {
    n2: {
      id: 'n2',
      type: 'VP',
      surface: `${verb} to school`,
      span: [1, 4],
      parent: 'n0',
      role: 'verb phrase',
      constraint: 'C-SUBJECT-AGREEMENT',
      status: errored ? 'error' : 'valid',
      text: errored
        ? "The subject 'She' is 3rd person singular, but the verb 'go' is not-third-person present."
        : "The subject 'She' and the verb 'goes' match.",
      remediation: errored
        ? {
          violation: "The subject 'She' is 3rd person singular, but the verb 'go' is not-third-person present.",
          suggested_fix: "Change 'go' to 'goes' so it matches the subject 'She'.",
          alternative_fix: null,
          targeted_outcome: 'Subject (3rd person singular) + verb VBZ',
          edit: { start: 1, end: 2, text: 'goes' },
          alternative_edit: null,
        }
        : undefined,
    },
  };
  return {
    meta: { target_sentence: 1 },
    parse: {
      text: `She ${verb} to school`,
      sentences: [{ ordinal: 1, start: 0, end: 16 }],
      tokens,
    },
    tree,
    nodes,
    node_details,
  };
}

const broken = buildPayload('go');
const fixed = buildPayload('goes');

// --- 1. the focus plan ----------------------------------------------------
const plan = planFocus(broken, 'n2');
assert.ok(plan, 'a focus plan is required for every error');
assert.equal(plan.nodeId, 'n2');
assert.equal(plan.scopeId, 'n0', 'the clause is the scope of the rule');
assert.equal(plan.scopeType, 'S');
assert.equal(plan.label, 'Subject\u2013verb agreement');
assert.deepEqual(plan.pair.sort(), ['n3', 'n4'],
  'the rule links the subject with the verb');

// --- 2. the edit rebuilds the sentence ------------------------------------
const edit = broken.node_details.n2.remediation.edit;
const corrected = applyEdit(broken, edit);
assert.equal(corrected, 'She goes to school');

// --- 3. the corrected scope is found in the re-parsed tree -----------------
const expected = expectedScopeWords(broken, plan.scopeId, edit);
assert.equal(expected, 'she goes to school');
assert.equal(findScopeNode(fixed, plan.scopeType, expected), 'n0',
  'the corrected subtree has to be locatable again');

// --- 4. the error is re-identified by constraint + context ----------------
const context = contextWords(broken, plan.scopeId);
assert.ok(context.length > 0, 'the scope needs surrounding words to match on');
const focus = { constraint: 'C-SUBJECT-AGREEMENT', context };

const hit = findTargetError(broken, focus);
assert.ok(hit, 'the error must be re-identifiable in the original parse');
assert.equal(hit.detail.id, 'n2');

assert.equal(findTargetError(fixed, focus), null,
  'a corrected sentence must not report the error again');

// --- 5. an unknown node never breaks the planner --------------------------
assert.equal(planFocus(broken, 'does-not-exist'), null);
assert.equal(planFocus(broken, 'n3'), null,
  'only a node with a detail (an error) can be focused');

console.log('PASS: the correction module plans, edits and re-checks correctly');
