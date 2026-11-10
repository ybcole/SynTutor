// XAI-7: one evidence-focus contract for all tree-bearing modes.
//
// A B-R parent/sibling is an observed tree edge. An approved rule governor
// can only come from verified XAI-5 diagnoses. Raw-token candidates are NOT
// promoted into grammatical functions or error labels.
export function evidenceFocus(evidence) {
  const ui = evidence?.xai7_unified;
  if (!ui || ui.schema_version !== 'xai7-evidence-1.0.0'
      || ui.language_policy !== 'ENGLISH_ONLY') {
    return { selected: null, positions: [], issues: [], featureRows: [] };
  }
  const positions = Array.isArray(ui.focus) ? ui.focus.filter(row =>
    typeof row.node_id === 'string' &&
    ['selected','parent','sibling','approved_governor','approved_affected'].includes(row.reason) &&
    ['witnessed_tree_position','approved_rule'].includes(row.relation_authority)) : [];
  const issues = Array.isArray(ui.verified_issues)
    ? ui.verified_issues.filter(row => row.status === 'verified_local_violation') : [];
  return {
    selected: typeof ui.selected_node_id === 'string' ? ui.selected_node_id : null,
    positions, issues,
    featureRows: Array.isArray(ui.feature_rows) ? ui.feature_rows : [],
  };
}

// A canonical SVG's own data-node-id elements are the sole highlight targets.
// IDs are compared verbatim; never interpolate user-controlled text into CSS.
export function applyEvidenceFocus(treeRoot, evidence) {
  if (!treeRoot?.querySelectorAll) return [];
  const focus = evidenceFocus(evidence);
  const names = new Map();
  for (const row of focus.positions) {
    const existing = names.get(row.node_id) || [];
    existing.push(row.reason);
    names.set(row.node_id, existing);
  }
  const changed = [];
  for (const group of treeRoot.querySelectorAll('[data-node-id]')) {
    const id = group.getAttribute('data-node-id');
    const role = names.get(id) || [];
    group.removeAttribute('data-xai7-focus');
    group.removeAttribute('data-xai7-related');
    group.removeAttribute('data-xai7-issue');
    if (role.includes('selected')) group.dataset.xai7Focus = 'selected';
    else if (role.includes('parent')) group.dataset.xai7Focus = 'parent';
    else if (role.includes('sibling')) group.dataset.xai7Focus = 'sibling';
    if (role.includes('approved_governor') || role.includes('approved_affected'))
      group.dataset.xai7Issue = role.includes('approved_affected') ? 'affected' : 'governor';
    if (role.length) {
      group.dataset.xai7Related = role.join(' ');
      changed.push(id);
    }
  }
  return changed;
}

export function evidenceFocusText(evidence) {
  const focus = evidenceFocus(evidence);
  if (!focus.selected) return null;
  const graph = evidence?.fact_graph;
  const node = graph?.target;
  if (!node || node.node_id !== focus.selected) return null;
  const related = focus.positions.filter(x => x.node_id !== node.node_id);
  const lexical = node.kind === 'word' ? 'word' : node.label || 'constituent';
  const named = node.surface || 'silent position';
  const relations = related.filter(x => x.reason === 'parent' || x.reason === 'sibling');
  const issues = focus.issues.length;
  return {
    selected: lexical + ': ' + named,
    treeNote: relations.length
      ? relations.map(x => x.reason + ' ' + x.node_id).join(' · ')
      : 'Root position in the displayed tree',
    verifiedIssueCount: issues,
    featureLabels: focus.featureRows.map(x => x.feature),
  };
}
