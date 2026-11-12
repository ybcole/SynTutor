import { fromSummary } from './history-status.mjs';

const LEGACY_COLUMNS =
  'id, sentence, is_valid, constraints_fired, created_at';

const EXTENDED_COLUMNS =
  LEGACY_COLUMNS + ', analysis_status, diagnostic_authority';

function isMissingStatusColumn(error) {
  if (!error) return false;

  const supportedCode =
    error.code === '42703' ||
    error.code === 'PGRST204';

  const message = [
    error.message,
    error.details,
    error.hint,
  ].filter(Boolean).join(' ');

  return supportedCode &&
    /\b(analysis_status|diagnostic_authority)\b/.test(message);
}

function selectRows(client, columns, limit) {
  return client
    .from('analysis_history')
    .select(columns)
    .order('created_at', { ascending: false })
    .limit(limit);
}

export async function loadHistoryRows(client, limit = 50) {
  let result = await selectRows(
    client, EXTENDED_COLUMNS, limit
  );

  if (!result.error) {
    return {
      rows: result.data ?? [],
      schema: 'extended',
    };
  }

  if (!isMissingStatusColumn(result.error)) {
    throw result.error;
  }

  result = await selectRows(
    client, LEGACY_COLUMNS, limit
  );

  if (result.error) {
    throw result.error;
  }

  return {
    rows: result.data ?? [],
    schema: 'legacy',
  };
}


export async function insertHistoryRow(
  client, userId, sentence, summary
) {
  if (
    !client?.from ||
    typeof userId !== 'string' ||
    !userId ||
    typeof sentence !== 'string' ||
    !sentence.trim() ||
    !summary ||
    typeof summary !== 'object'
  ) {
    throw new TypeError('Invalid history insertion arguments');
  }

  const classification = fromSummary(summary);

  const row = {
    user_id: userId,
    sentence,
    is_valid: classification.is_valid,
    constraints_fired:
      Array.isArray(summary.constraints_fired)
        ? [...summary.constraints_fired]
        : [],
    analysis_status: classification.analysis_status,
    diagnostic_authority:
      classification.diagnostic_authority,
  };

  const { error } = await client
    .from('analysis_history')
    .insert(row);

  if (!error) {
    return {
      saved: true,
      status: classification.analysis_status,
    };
  }

  if (isMissingStatusColumn(error)) {
    return {
      saved: false,
      reason: 'migration_required',
    };
  }

  throw error;
}
