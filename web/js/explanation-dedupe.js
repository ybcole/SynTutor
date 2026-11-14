const OWN_EXPLANATION_LABELS = new Set([
  'V', 'N', 'A', 'Adv', 'ART', 'DET', 'PRO', 'PRON', 'pronoun', 'AUX',
  'MOD', 'PERF', 'PROG', 'PASS', 'TENSE', 'P', 'DEG', 'NAME', 'name', 'Q',
  'QA', 'POSS', 'DEM', 'V-part', 'PRE-DET', 'PART', 'Prt', 'NEG', 'C', 'C1',
  'C2',
]);

// Words and lexical wrappers always keep their own explanation. Collapsing
// them onto an enclosing phrase is what made a second click on "Who" replace
// its lexical explanation with "Same explanation as the enclosing C2".
export function hasOwnLexicalExplanation(node) {
  if (!node) return false;
  if (node.word !== undefined || node.triangle || node.gap || node.empty
      || node.elided) return true;
  return OWN_EXPLANATION_LABELS.has(node.label);
}

export function shouldCollapseExplanation(node, text, parentText) {
  return Boolean(parentText) && Boolean(text) && text === parentText
    && !hasOwnLexicalExplanation(node);
}
