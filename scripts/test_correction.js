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
  computePreviewImpact, formatImpactSummary, formatRecheckOutcome,
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

// --- 6. correction-preview completeness & honest uncertainty reporting -----
const completeOrig = {
  parse: { text: 'The cat sleepps.' },
  node_details: {
    n4: { id: 'n4', status: 'error', constraint: 'C-LEXICON-MALFORMED', type: 'VBZ', surface: 'sleepps' },
  },
  summary: {
    verdict: 'ungrammatical',
    correction: { corrected_sentence: 'The cat sleeps.', impact: { whole_sentence_clean: true, completeness: 'complete' } },
  },
};
const completePreview = {
  parse: { text: 'The cat sleeps.' },
  node_details: {},
  br_analysis: { status: 'normalized' },
  summary: { verdict: 'grammatical', violations: [] },
};
const completeImpact = computePreviewImpact(completeOrig, completePreview);
assert.equal(completeImpact.whole_sentence_clean, true);
assert.equal(completeImpact.completeness, 'complete');
assert.match(formatImpactSummary(completeImpact, { panel: true }), /whole sentence is clean/i);
assert.equal(formatRecheckOutcome(completePreview).complete, true);
assert.match(formatRecheckOutcome(completePreview).message, /clean now/i);

// Partial repair: "Ths cat sleepps." -> "Ths cat sleeps." must NEVER claim clean
const partialOrig = {
  parse: { text: 'Ths cat sleepps.' },
  node_details: {
    n4: { id: 'n4', status: 'error', constraint: 'C-LEXICON-MALFORMED', type: 'VBZ', surface: 'sleepps' },
  },
  summary: {
    verdict: 'ungrammatical',
    correction: {
      corrected_sentence: 'Ths cat sleeps.',
      impact: { whole_sentence_clean: false, completeness: 'partial', unresolved_tokens: [{ token_id: 0, surface: 'Ths' }] },
    },
  },
};
const partialPreviewFromPayload = {
  parse: { text: 'Ths cat sleeps.' },
  node_details: {},
  br_analysis: { status: 'normalized' },
  summary: { verdict: 'grammatical', violations: [], unresolved_tokens: [{ token_id: 0, surface: 'Ths' }] },
};
const partialPreviewServerImpactOnly = {
  parse: { text: 'Ths cat sleeps.' },
  node_details: {},
  br_analysis: { status: 'normalized' },
  summary: { verdict: 'grammatical', violations: [] },
};
for (const preview of [partialPreviewFromPayload, partialPreviewServerImpactOnly]) {
  const imp = computePreviewImpact(partialOrig, preview);
  assert.equal(imp.whole_sentence_clean, false, 'partial preview must never report whole_sentence_clean=true');
  assert.equal(imp.completeness, 'partial');
  assert.deepEqual(imp.unresolved_tokens, [{ token_id: 0, surface: 'Ths' }]);
  const panelText = formatImpactSummary(imp, { panel: true });
  assert.doesNotMatch(panelText, /whole sentence is clean/i);
  assert.match(panelText, /“Ths” remains uncertain/);
}
const partialRecheck = formatRecheckOutcome(partialPreviewFromPayload);
assert.equal(partialRecheck.complete, false);
assert.doesNotMatch(partialRecheck.message, /clean now/i);
assert.match(partialRecheck.message, /“Ths” remains uncertain/);

// Unresolved syntax tree or unverified verdict must never claim clean
const unverifiedPreview = {
  parse: { text: 'I am scares tomorrow.' },
  node_details: {},
  br_analysis: { status: 'unresolved' },
  summary: { verdict: 'unverified', violations: [] },
};
const unverImpact = computePreviewImpact(completeOrig, unverifiedPreview);
assert.equal(unverImpact.whole_sentence_clean, false);
assert.equal(unverImpact.completeness, 'partial');
assert.doesNotMatch(formatImpactSummary(unverImpact, { panel: true }), /whole sentence is clean/i);
assert.match(formatImpactSummary(unverImpact, { panel: true }), /could not be verified/i);
assert.equal(formatRecheckOutcome(unverifiedPreview).complete, false);
assert.doesNotMatch(formatRecheckOutcome(unverifiedPreview).message, /clean now/i);

// Multi-error sentence where one error remains
const multiPreview = {
  parse: { text: 'The boys walks.' },
  node_details: {
    n4: { id: 'n4', status: 'error', constraint: 'C-SUBJECT-AGREEMENT', type: 'VBZ', surface: 'walks' },
  },
  br_analysis: { status: 'normalized' },
  summary: { verdict: 'ungrammatical', violations: ['C-SUBJECT-AGREEMENT'] },
};
const multiRecheck = formatRecheckOutcome(multiPreview);
assert.equal(multiRecheck.complete, false);
assert.match(multiRecheck.message, /1 other issue\(s\) remain/);

console.log('PASS: the correction module plans, edits and re-checks correctly');
