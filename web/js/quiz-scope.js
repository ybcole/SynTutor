// Lessons determines what is taught; this policy determines what is assessed.
// These exclusions NEVER alter the Lessons catalog, content or progress.
const excludedChapters = new Set(['cgel-ch01']); // Preliminaries: orientation, not a Quiz chapter.
const excludedTopics = new Set(['br-11/concepts']); // Language varieties/description, not grammatical analysis.

export function applyQuizScope(curriculum) {
  return curriculum.map(track=>({...track,chapters:track.chapters
    .filter(chapter=>!excludedChapters.has(chapter.id))
    .map(chapter=>({...chapter,topics:chapter.topics.filter(topic=>!excludedTopics.has(`${chapter.id}/${topic.id}`))}))
    .filter(chapter=>chapter.topics.length)}));
}

export function isRelevantAssessmentQuestion(q) {
  if(excludedChapters.has(q.chapter_id||q.lesson_id)
    ||excludedTopics.has(`${q.chapter_id||q.lesson_id}/${q.subtopic_id}`))return false;
  if(/using the wording in the lesson|which explanation is paired with|the table “[^”]+” pairs/i.test(q.prompt))return false;
  if(/\b(?:which|what) (?:page|chapter|edition)\b|\bwho (?:wrote|authored)\b/i.test(q.prompt))return false;
  // Chapter/page identification and commentary about a book's presentation are
  // not grammar questions. Keep legitimate applied "Chapter 3 B-R diagram"
  // questions in the immutable published bank.
  if(q.kind==='concept_completion'&&/\b(chapter \d+|(?:this|the) (?:course|lesson|textbook)|the book (?:uses|treats|describes|introduces|covers|explains|presents)|the book[’']s example|printed page)\b/i.test(q.prompt))return false;
  return true;
}
