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

// `userSentences` are the learner's corrected sentences as segmented by the
// parser (payload.parse.sentences[i].text); the paragraph itself is a single
// flowing line, so sentence boundaries come from the server, not from newlines.
export function isParagraphQuizAnswerCorrect(userSentences, expectedSentences, payloads) {
  if (!Array.isArray(userSentences) || !Array.isArray(expectedSentences)) return false;
  if (userSentences.length !== expectedSentences.length
      || payloads.length !== userSentences.length
      || payloads.some((payload) => !payload)) {
    return false;
  }
  return userSentences.every((sentence, index) =>
    String(sentence).trim()
      && normalize(sentence) === normalize(expectedSentences[index])
      && !hasSyntaxError(payloads[index]));
}
