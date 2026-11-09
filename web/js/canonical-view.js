// Structural facts for the *validated* B-R tree. This module never turns
// parser-only POS tags or a legacy matrix finding into book-backed evidence.
export function findCanonicalNode(root, nodeId) {
  if (!root || !nodeId) return null;
  if (root.id === nodeId) return root;
  for (const child of root.children || []) {
    const hit = findCanonicalNode(child, nodeId);
    if (hit) return hit;
  }
  return null;
}

export function canonicalNodeFacts(envelope, node) {
  if (!envelope || !node) return null;
  const label = node.label || (node.word ? 'Word' : node.gap ? 'Gap' : 'Unlabelled node');
  const span = node.token_span;
  let surface = '';
  if (Array.isArray(node.words)) {
    surface = node.words.join(' ');
  } else if (typeof node.word === 'string') {
    surface = node.word;
  } else if (Array.isArray(span) && span.length === 2
      && Number.isInteger(span[0]) && Number.isInteger(span[1])) {
    surface = (envelope.tokens || []).slice(span[0], span[1]).map(t => t.text).join(' ');
  }
  const children = node.children || [];
  const branchWords = child => {
    if (child.word) return child.word;
    if (Array.isArray(child.words)) return child.words.join(' ');
    if (!Array.isArray(child.token_span)) return '';
    const [start, end] = child.token_span;
    return (envelope.tokens || []).slice(start, end).map(token => token.text).join(' ');
  };
  return {
    label, surface,
    children: children.map(c => c.label || (c.word ? 'word' : c.gap ? 'gap' : 'unlabelled')),
    childSurfaces: children.map(branchWords),
    featureLabels: node.features || [],
    triangle: Boolean(node.triangle),
    gap: Boolean(node.gap),
    empty: Boolean(node.empty),
    source: envelope.source || null,
  };
}

export function canonicalObservation(facts) {
  if (!facts) return 'No canonical structural details are available.';
  let description = facts.label + (facts.surface ? ` spans “${facts.surface}”.` : ' is an empty or unspoken position.');
  if (facts.triangle) description += ' The triangle marks an unanalyzed phrase; no unverified internal branches are inserted.';
  else if (facts.children.length) {
    const branches = facts.children.map((label, i) => {
      const words = facts.childSurfaces?.[i];
      return words ? `${label} “${words}”` : label;
    });
    description += ` Its direct branches are ${branches.join(', ')}.`;
  }
  else if (facts.gap) description += ' This is a marked gap in the source tree.';
  const featureMeanings = {intrans: 'intransitive', trans: 'transitive',
    pres: 'present tense', past: 'past tense'};
  for (const feature of facts.featureLabels) {
    const meaning = featureMeanings[feature];
    description += meaning ? ` [${feature}] marks ${meaning}.` : ` Feature [${feature}].`;
  }
  return description;
}
