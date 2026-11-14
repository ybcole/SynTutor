// Compose local previews and release candidates from the same chapter overlays.
import { validateCourse } from './lesson-core.js';

export function composeLessonPreview(catalog, pilots) {
  const sources = new Map(catalog.sources.map(source => [source.id, source]));
  const lessonIds = new Set(catalog.lessons.map(lesson => lesson.lesson_id));
  const overlays = new Map();
  for (const [id, { preview_sources: previewSources = [], ...overlay }] of pilots) {
    if (!lessonIds.has(id) || overlays.has(id) || ('lesson_id' in overlay && overlay.lesson_id !== id)) {
      throw new Error(`Unexpected chapter pilot: ${id}`);
    }
    overlays.set(id, overlay);
    for (const source of previewSources) {
      const existing = sources.get(source.id);
      if (existing) {
        const fields = new Set([...Object.keys(existing), ...Object.keys(source)]);
        if ([...fields].some(field => existing[field] !== source[field])) {
          throw new Error(`Conflicting lesson source: ${source.id}`);
        }
      } else {
        sources.set(source.id, source);
      }
    }
  }
  return validateCourse({
    ...catalog,
    sources: [...sources.values()],
    lessons: catalog.lessons.map(lesson => overlays.has(lesson.lesson_id)
      ? { ...lesson, ...overlays.get(lesson.lesson_id) } : lesson),
  });
}
