// Active release metadata shared by Lessons and Quiz; no browser dependencies.
import { constituentsPilot } from './constituents-pilot.js';
import { functionsPilot } from './functions-pilot.js';
import { categoriesPilot } from './categories-pilot.js';
import { basicVpPilot } from './basic-vp-pilot.js';
import { adverbialsPilot } from './adverbials-pilot.js';
import { auxiliariesPilot } from './auxiliaries-pilot.js';
import { nounPhrasesPilot } from './noun-phrases-pilot.js';
import { embeddedClausesPilot } from './embedded-clauses-pilot.js';
import { whClausesPilot } from './wh-clauses-pilot.js';
import { nonFinitePilot } from './non-finite-pilot.js';
import { grammarPilot } from './grammar-pilot.js';
import { cambridgeChapterData } from './cambridge-chapter-data.js?v=2026.11.16c';
import { composeLessonPreview } from './lesson-preview.js';

export const pilotArticles = {
  'br-01': constituentsPilot, 'br-02': functionsPilot, 'br-03': categoriesPilot,
  'br-04': basicVpPilot, 'br-05': adverbialsPilot, 'br-06': auxiliariesPilot,
  'br-07': nounPhrasesPilot, 'br-08': embeddedClausesPilot, 'br-09': whClausesPilot,
  'br-10': nonFinitePilot, 'br-11': grammarPilot,
};
export const cambridgePilotIds = Object.keys(cambridgeChapterData);
export const activeLessonIds = [...Object.keys(pilotArticles), ...cambridgePilotIds];
export async function loadActiveCourse(fetcher = fetch) {
  const json = async path => {
    const response = await fetcher(path, { cache: 'no-cache' });
    if (!response.ok) throw Error(`Lesson metadata unavailable: ${path}`);
    return response.json();
  };
  const [catalog, overlays] = await Promise.all([
    json('/content/lessons/course.json'),
    Promise.all(activeLessonIds.map(async id => [id, await json(`/content/lessons/${id}-pilot.json`)])),
  ]);
  return composeLessonPreview(catalog, overlays);
}
export function quizCurriculum(course) {
  return [
    { id: 'syntax', lessonTrack: 'foundations', title: 'Syntax', subtitle: 'Burton-Roberts' },
    { id: 'cambridge', lessonTrack: 'grammar', title: 'Cambridge', subtitle: 'Cambridge Grammar' },
  ].map(track => ({
    ...track,
    chapters: course.lessons.filter(l => l.track === track.lessonTrack).map(lesson => {
      const article = pilotArticles[lesson.lesson_id] || cambridgeChapterData[lesson.lesson_id];
      const topics = (article?.sections || []).filter(s =>
        !s.assessment && !['introduction', 'recap', 'chapter-review', 'closing-check'].includes(s.id)
        && !/^(exercises? on|category and coordination exercises|wh-question and relative clause exercises|grammar rules and sentence derivation exercise)/i.test(s.title));
      return { id: lesson.lesson_id, title: lesson.title, chapter: lesson.chapter,
        outcomes: lesson.outcomes, topics: topics.map(s => ({ id: s.id, title: s.title })) };
    }),
  }));
}
