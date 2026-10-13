function normalize(text) {
  return (text || '')
    .toLowerCase()
    .replace(/[\u2018\u2019]/g, "'")
    .replace(/[\u201C\u201D]/g, '"')
    .replace(/[.!?]+$/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

export function hasSyntaxError(payload) {
  const summary = payload?.summary;
  return summary?.verdict === 'ungrammatical'
    || summary?.root_error === true
    || summary?.violated_edges > 0
    || summary?.valid === false
    || Object.values(payload?.node_details || {}).some((detail) => detail?.status === 'error');
}

export function isQuizAnswerCorrect(answer, expected, payload) {
  return normalize(answer) === normalize(expected) && !hasSyntaxError(payload);
}
