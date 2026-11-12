import test from 'node:test';
import assert from 'node:assert/strict';

import { loadHistoryRows } from
  '../../web/js/history-store.mjs';

import { forDisplay } from
  '../../web/js/history-status.mjs';

function mockClient(responses) {
  const calls = [];

  return {
    calls,

    from(table) {
      assert.equal(table, 'analysis_history');

      return {
        select(columns) {
          calls.push(columns);

          return {
            order(column, options) {
              assert.equal(column, 'created_at');
              assert.equal(options.ascending, false);

              return {
                async limit(count) {
                  assert.equal(count, 50);
                  return responses.shift();
                },
              };
            },
          };
        },
      };
    },
  };
}

test('extended schema preserves explicit status', async () => {
  const client = mockClient([{
    data: [{
      is_valid: false,
      analysis_status: 'reported_violation',
      diagnostic_authority: 'legacy_diagnostic',
    }],
    error: null,
  }]);

  const result = await loadHistoryRows(client);

  assert.equal(result.schema, 'extended');
  assert.equal(client.calls.length, 1);
  assert.equal(
    forDisplay(result.rows[0]).status,
    'reported_violation'
  );
});

test('missing new columns falls back to legacy loading', async () => {
  const client = mockClient([
    {
      data: null,
      error: {
        code: '42703',
        message:
          'column analysis_history.analysis_status does not exist',
      },
    },
    {
      data: [{ is_valid: false }],
      error: null,
    },
  ]);

  const result = await loadHistoryRows(client);

  assert.equal(result.schema, 'legacy');
  assert.equal(client.calls.length, 2);
  assert.equal(
    forDisplay(result.rows[0]).status,
    'legacy_unclassified'
  );
});

test('permission errors never trigger legacy fallback', async () => {
  const client = mockClient([{
    data: null,
    error: Object.assign(
      new Error('permission denied'),
      { code: '42501' }
    ),
  }]);

  await assert.rejects(
    () => loadHistoryRows(client),
    /permission denied/
  );

  assert.equal(client.calls.length, 1);
});

test('unrelated missing columns do not trigger fallback', async () => {
  const client = mockClient([{
    data: null,
    error: Object.assign(
      new Error('column other_field does not exist'),
      { code: '42703' }
    ),
  }]);

  await assert.rejects(
    () => loadHistoryRows(client),
    /other_field/
  );

  assert.equal(client.calls.length, 1);
});

test('errors during legacy fallback are not hidden', async () => {
  const client = mockClient([
    {
      data: null,
      error: {
        code: 'PGRST204',
        message:
          'Could not find the analysis_status column in schema cache',
      },
    },
    {
      data: null,
      error: new Error('legacy query failed'),
    },
  ]);

  await assert.rejects(
    () => loadHistoryRows(client),
    /legacy query failed/
  );
});

import { insertHistoryRow } from
  '../../web/js/history-store.mjs';

function mockInsertClient(response) {
  const calls = [];

  return {
    calls,
    from(table) {
      assert.equal(table, 'analysis_history');

      return {
        async insert(row) {
          calls.push(row);
          return response;
        },
      };
    },
  };
}

test('insertion preserves reported violation authority', async () => {
  const client = mockInsertClient({ error: null });

  const result = await insertHistoryRow(
    client,
    'test-user',
    'The boys runs.',
    {
      verdict: 'ungrammatical',
      verdict_authority: 'legacy_diagnostic',
      constraints_fired: ['C-SUBJECT-AGREEMENT'],
    }
  );

  assert.equal(result.saved, true);
  assert.equal(
    client.calls[0].analysis_status,
    'reported_violation'
  );
  assert.equal(
    client.calls[0].diagnostic_authority,
    'legacy_diagnostic'
  );
  assert.deepEqual(
    client.calls[0].constraints_fired,
    ['C-SUBJECT-AGREEMENT']
  );
});

test('unverified findings retain explicit uncertainty', async () => {
  const client = mockInsertClient({ error: null });

  await insertHistoryRow(
    client,
    'test-user',
    'An uncertain example.',
    {
      verdict: 'unverified',
      verdict_authority: 'legacy_diagnostic',
    }
  );

  assert.equal(client.calls[0].is_valid, false);
  assert.equal(
    client.calls[0].analysis_status,
    'unverified'
  );
});

test('legacy grammatical verdict is not certified', async () => {
  const client = mockInsertClient({ error: null });

  await insertHistoryRow(
    client,
    'test-user',
    'The boy runs.',
    {
      verdict: 'grammatical',
      verdict_authority: 'legacy_diagnostic',
    }
  );

  assert.equal(
    client.calls[0].analysis_status,
    'no_supported_error_detected'
  );
  assert.equal(
    client.calls[0].diagnostic_authority,
    'legacy_diagnostic'
  );
});

test('missing status columns block lossy insertion', async () => {
  const client = mockInsertClient({
    error: {
      code: 'PGRST204',
      message:
        'Could not find the analysis_status column in schema cache',
    },
  });

  const result = await insertHistoryRow(
    client,
    'test-user',
    'The boys runs.',
    { verdict: 'ungrammatical' }
  );

  assert.deepEqual(result, {
    saved: false,
    reason: 'migration_required',
  });

  // There must be no fallback Boolean-only insertion.
  assert.equal(client.calls.length, 1);
  assert.equal(
    client.calls[0].analysis_status,
    'reported_violation'
  );
});

test('permission errors are propagated during insertion', async () => {
  const client = mockInsertClient({
    error: Object.assign(
      new Error('permission denied'),
      { code: '42501' }
    ),
  });

  await assert.rejects(
    () => insertHistoryRow(
      client,
      'test-user',
      'The boys runs.',
      { verdict: 'ungrammatical' }
    ),
    /permission denied/
  );

  assert.equal(client.calls.length, 1);
});
