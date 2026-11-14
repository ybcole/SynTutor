import assert from 'node:assert/strict';
import { mapLegacyDetailsToCanonical } from '../web/js/legacy-node-map.js';

const tree = {
  id: 'sg-root',
  label: 'S',
  token_span: [0, 5],
  children: [
    {
      id: 'sg-root-0',
      label: 'NP',
      token_span: [0, 2],
      children: [
        { id: 'sg-root-0-0', label: 'DET', token_span: [0, 1], children: [] },
        { id: 'sg-root-0-1', label: 'NOM', token_span: [1, 2], children: [] },
      ],
    },
    {
      id: 'sg-root-1',
      label: 'VP',
      token_span: [2, 5],
      children: [
        {
          id: 'sg-root-1-0',
          label: 'V',
          token_span: [2, 3],
          children: [{ id: 'sg-root-1-0-0', word: 'reads', token_span: [2, 3] }],
        },
        {
          id: 'sg-root-1-1',
          label: 'NP',
          token_span: [3, 5],
          children: [{ id: 'sg-root-1-1-0', label: 'NOM', token_span: [3, 5], children: [] }],
        },
      ],
    },
  ],
};

const details = {
  n4: {
    status: 'error',
    span: [2, 5],
    constraint: 'C-SUBJECT-AGREEMENT',
    remediation: {
      edits: [{ node: 'n5', replacement: 'read', edit: { start: 2, end: 3, text: 'read' } }],
    },
  },
};

const mapped = mapLegacyDetailsToCanonical(tree, details);
assert.equal(mapped.mapped, 1);
assert.equal(mapped.unmapped, 0);
assert.equal(mapped.byNode.get('sg-root-1'), undefined);
assert.equal(mapped.byNode.get('sg-root-1-0-0')?.constraint, 'C-SUBJECT-AGREEMENT');
assert.equal(mapped.byNode.get('sg-root-1-0'), undefined);
assert.equal(mapped.byNode.get('sg-root'), undefined);
assert.equal(mapped.detailForNode('sg-root'), null);

const noEdit = mapLegacyDetailsToCanonical(tree, {
  n4: { status: 'error', span: [2, 5], constraint: 'C-SUBJECT-AGREEMENT' },
});
assert.equal(noEdit.byNode.get('sg-root-1')?.constraint, 'C-SUBJECT-AGREEMENT');
assert.equal(noEdit.detailForNode('sg-root-1-0-0'), null);

const unmapped = mapLegacyDetailsToCanonical(tree, {
  n9: { status: 'error', span: null, constraint: 'C-UNKNOWN' },
});
assert.equal(unmapped.mapped, 0);
assert.equal(unmapped.unmapped, 1);

const backendMapped = mapLegacyDetailsToCanonical(tree, {
  n4: {
    status: 'error',
    span: [2, 5],
    constraint: 'C-SUBJECT-AGREEMENT',
    canonical_node_id: 'sg-root-1-0-0',
  },
});
assert.equal(backendMapped.mapped, 1);
assert.equal(backendMapped.byNode.get('sg-root-1-0-0')?.constraint, 'C-SUBJECT-AGREEMENT');
assert.equal(backendMapped.byNode.get('sg-root-1'), undefined);

console.log('legacy-node-map tests passed');
