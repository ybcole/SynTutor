/**
 * Map legacy matrix node records onto canonical B-R node IDs.
 *
 * The legacy detector runs on the Benepar tree and stores node ids such as
 * `n4`. The canonical tree uses ids such as `sg-root-1-0`. This bridge uses
 * token spans and remediation edit positions so the canonical view can show
 * the same diagnostic instead of silently losing it.
 */
export function mapLegacyDetailsToCanonical(root, details = {}) {
  const all = [];
  const parents = new Map();
  const walk = (node, parent = null) => {
    if (!node) return;
    if (parent) parents.set(node.id, parent);
    all.push(node);
    for (const child of node.children || []) walk(child, node);
  };
  walk(root);

  const spanLength = (node) => {
    const span = node?.token_span;
    return Array.isArray(span) && span.length === 2 ? span[1] - span[0] : Number.MAX_SAFE_INTEGER;
  };
  const smallestForSpan = (start, end) => all
    .filter((node) => Array.isArray(node.token_span)
      && node.token_span[0] <= start && end <= node.token_span[1])
    .sort((a, b) => spanLength(a) - spanLength(b))[0] || null;
  const smallestForToken = (index) => all
    .filter((node) => Array.isArray(node.token_span)
      && node.token_span[0] <= index && index < node.token_span[1])
    .sort((a, b) => {
      const aWord = a.children?.length ? 1 : 0;
      const bWord = b.children?.length ? 1 : 0;
      return aWord - bWord || spanLength(a) - spanLength(b);
    })[0] || null;

  const byNode = new Map();
  const assign = (nodeId, detail) => {
    if (nodeId && !byNode.has(nodeId)) byNode.set(nodeId, detail);
  };
  // Only the exact mapped node receives the legacy detail. Do not leak a
  // phrase-level finding onto every word in the phrase.
  const detailForNode = (nodeId) => byNode.get(nodeId) || null;

  let mapped = 0;
  let unmapped = 0;
  for (const detail of Object.values(details || {})) {
    if (!detail || detail.status !== 'error') continue;
    if (typeof detail.canonical_node_id === 'string' && detail.canonical_node_id) {
      mapped += 1;
      assign(detail.canonical_node_id, detail);
      continue;
    }
    const targets = [];
    const rows = [];
    if (detail.remediation?.edit) rows.push(detail.remediation);
    for (const row of detail.remediation?.edits || []) rows.push(row);
    for (const row of rows) {
      const edit = row?.edit || row;
      if (!Number.isInteger(edit?.start)) continue;
      const node = Number.isInteger(edit.end) && edit.end > edit.start + 1
        ? smallestForSpan(edit.start, edit.end)
        : smallestForToken(edit.start);
      if (node) targets.push(node.id);
    }
    if (!rows.length && Array.isArray(detail.span) && detail.span.length === 2) {
      const node = smallestForSpan(detail.span[0], detail.span[1]);
      if (node) targets.push(node.id);
    }
    if (!targets.length) {
      unmapped += 1;
      continue;
    }
    mapped += 1;
    for (const id of new Set(targets)) assign(id, detail);
  }
  return { byNode, detailForNode, mapped, unmapped };
}
