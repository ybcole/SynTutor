import { approved, reviewed, rng, shuffled, randomSeed, MAX_QUIZ_ITEMS } from './quiz-core.js';
import {isRelevantAssessmentQuestion} from './quiz-scope.js';

export const GENERAL_POLICY = Object.freeze({ minimum: 5, perTopic: 1 });
export const MAX_MASTER_QUIZ_ITEMS = 50;
export const DEFAULT_MASTER_QUIZ_ITEMS = 25;
// An additive crosswalk: published content and answer keys remain unchanged.
// These narrow pools do NOT claim coverage of every topic in their chapter.
const legacyTopics = {
  'br-01': 'worked-example', 'br-02': 'concepts', 'br-03': 'worked-example',
  'br-04': 'concepts', 'br-05': 'concepts', 'br-06': 'chain',
  'br-07': 'worked-example', 'br-08': 'worked-example', 'br-09': 'worked-example',
  'br-10': 'worked-example', 'br-11': 'worked-example', 'cgel-clauses': 'sentence-clause',
};
export function questionMetadata(q, curriculum) {
  if (!q) return null;
  const track = curriculum.find(t => t.chapters.some(c => c.id === q.lesson_id));
  const chapter = track?.chapters.find(c => c.id === q.lesson_id);
  const topic = q.subtopic_id || (q.pool_id === 'br-11-p4' ? 'rule-and-structure'
    : q.pool_id === 'cgel-clauses-p3' ? 'subordinate-clauses' : legacyTopics[q.lesson_id]);
  if (!chapter?.topics.some(t => t.id === topic)) return null;
  // Explicit metadata must agree with the authoritative lesson.
  if ((q.track_id && q.track_id !== track.id) || (q.chapter_id && q.chapter_id !== chapter.id)) return null;
  return { track_id: track.id, chapter_id: chapter.id, subtopic_id: topic,
    concept_ids: q.concept_ids, outcome_ids: q.outcome_ids, lesson_id: q.lesson_id,
    lesson_reference: q.lesson_reference || `#lesson/${chapter.id}/${topic}`,
    content_version: q.content_version };
}
export function eligibleQuestions(bank, curriculum, trackId, tier = 'approved') {
  const sources = new Map(bank.sources.map(s => [s.id, s]));
  const published = bank.items.filter(q => {
    const meta = questionMetadata(q, curriculum);
    return meta?.track_id === trackId && isRelevantAssessmentQuestion(q) && reviewed(q) && q.publication_status === 'published'
      && q.source_ids?.length && q.source_ids.every(id => {
        const s = sources.get(id);
        return reviewed(s) && s.status === 'approved' && s.book === (trackId === 'syntax' ? 'B-R' : 'Cambridge')
          && ['resolved', 'compatible'].includes(s.crosswalk_status);
      });
  });
  if(tier==='approved'||tier==='lesson-assessment'){
    return [...published,...(bank.assessment_items||[]).filter(q=>{
      const meta=questionMetadata(q,curriculum);
      return meta?.track_id===trackId&&isRelevantAssessmentQuestion(q)&&q.publication_status==='published'
        &&q.assessment_format==='independent'&&approved(q);
    })];
  }
  if(tier!=='lesson-practice')return published;
  const practice=(bank.practice_items||[]).filter(q=>{
    const meta=questionMetadata(q,curriculum);
    return meta?.track_id===trackId&&q.publication_status==='practice'&&q.review_status==='UNREVIEWED'
      &&q.independent_review===false&&q.source_metadata?.kind==='syntutor_lesson_section'
      &&q.lesson_reference===`#lesson/${meta.chapter_id}/${meta.subtopic_id}`;
  });
  return [...published,...practice];
}
export function publishedBlueprint(bank, curriculum, spec) {
  if (spec.mode !== 'topic'||['lesson-practice','lesson-assessment'].includes(spec.content_tier)) return null;
  const eligible = new Set(eligibleQuestions(bank, curriculum, spec.track, 'reviewed').filter(q => {
    const m = questionMetadata(q, curriculum);
    return m.chapter_id === spec.chapter && m.subtopic_id === spec.topic;
  }).map(q => `${q.item_id}@${q.content_version}`));
  return bank.assessments.find(a => reviewed(a) && a.pool_ids.length === 5 && a.pool_ids.every(pool => {
    const variants = bank.items.filter(q => q.pool_id === pool && q.content_version === a.item_version);
    return variants.length >= 2 && variants.every(q => eligible.has(`${q.item_id}@${q.content_version}`));
  })) || null;
}
export function topicPerformance(bank, curriculum, attempts, trackId) {
  const topics = new Map(), missed = new Set(), seen = new Set(), concepts = new Map(), missedFamilies = new Set(), missedExamples = new Set();
  const questions=[...bank.items,...(bank.practice_items||[]),...(bank.assessment_items||[])];
  const rows = Object.values(attempts).filter(t => t.submitted_at && Array.isArray(t.presented) && t.responses)
    .sort((a,b) => a.submitted_at.localeCompare(b.submitted_at) || a.attempt_id.localeCompare(b.attempt_id));
  for (const t of rows) for (const r of t.presented) {
    const q = questions.find(q => q.item_id === r.item_id && q.content_version === r.content_version);
    const m = questionMetadata(q, curriculum);
    if (m?.track_id !== trackId) continue;
    const correct = t.responses[q.item_id] === q.answer;
    seen.add(q.item_id);
    if (!correct) missed.add(q.item_id); // Never remove historical misses after a later success.
    if(!correct&&q.practice_family)missedFamilies.add(q.practice_family);
    if(!correct)for(const example of q.practice_example_ids||[])missedExamples.add(example);
    const key = `${m.chapter_id}/${m.subtopic_id}`;
    const old = topics.get(key) || { answered: 0, correct: 0, incorrect: 0, recent: 0.5 };
    old.answered++; old.correct += Number(correct); old.incorrect += Number(!correct);
    old.recent = 0.65 * old.recent + 0.35 * Number(correct);
    // Beta prior + recent improvement; an unseen topic is never a confirmed weakness.
    old.accuracy = (old.correct + 2) / (old.answered + 4);
    old.weakness = (1 - (0.4 * old.accuracy + 0.6 * old.recent)) * old.answered / (old.answered + 2);
    topics.set(key, old);
    for (const id of q.concept_ids || []) {
      const prior = concepts.get(id) || { answered: 0, incorrect: 0 };
      prior.answered++; prior.incorrect += Number(!correct); concepts.set(id, prior);
    }
  }
  return { topics, concepts, missed, seen, missedFamilies, missedExamples };
}
// Water-fill allocation: shuffled ties fairly rotate extras, respecting capacity.
export function balancedSelection(groups, count, random, preference = () => 0) {
  if (!Number.isInteger(count) || count < groups.length) throw Error(`Choose at least ${groups.length} questions to cover every group.`);
  const pools = shuffled(groups, random).map(g => ({ ...g, items: shuffled(g.items, random).sort((a,b)=>preference(a)-preference(b)), selected: [] }));
  if (pools.some(g => !g.items.length)) throw Error('Insufficient approved questions: every required topic or chapter needs approved questions.');
  if (pools.reduce((n,g) => n + g.items.length, 0) < count) throw Error('Not enough distinct approved questions for this count.');
  for (let i = 0; i < count; i++) {
    const available = pools.filter(g => g.items.length).sort((a,b) => a.selected.length - b.selected.length);
    available[0].selected.push(available[0].items.pop());
  }
  return pools.flatMap(g => g.selected);
}
export const specKey = spec => `quiz-v2:${spec.track}:${spec.mode}:${spec.chapter || ''}:${spec.topic || ''}:${spec.count || ''}${['lesson-practice','lesson-assessment'].includes(spec.content_tier)?':'+spec.content_tier:''}${spec.format==='formal'?':formal-1':''}`;
export function selectQuestions(bank, curriculum, spec, attempts = {}, seed = randomSeed()) {
  const random = rng(seed), track = curriculum.find(t => t.id === spec.track);
  if (!track) throw Error('Unknown quiz track.');
  // Deduplicate stable IDs even if multiple content versions become available.
  const all = [...new Map(eligibleQuestions(bank, curriculum, spec.track, spec.content_tier).map(q => [q.item_id, q])).values()];
  const meta = q => questionMetadata(q, curriculum);
  const chapter = track.chapters.find(c => c.id === spec.chapter);
  let selection, diagnostic = false;
  if (spec.mode === 'personalized') {
    const performance = topicPerformance(bank, curriculum, attempts, spec.track);
    const eligible = shuffled(all.filter(q => !performance.missed.has(q.item_id)
      &&(!q.practice_family||!performance.missedFamilies.has(q.practice_family))
      &&!(q.practice_example_ids||[]).some(id=>performance.missedExamples.has(id))), random);
    if (eligible.length < 5) throw Error(`Only ${eligible.length} eligible questions remain after excluding every previously missed question. Five are required; try another available topic quiz.`);
    diagnostic = [...performance.topics.values()].reduce((n,t) => n + t.answered, 0) < 5;
    if (diagnostic) {
      const groups = track.chapters.map(c => ({ id: c.id, items: eligible.filter(q => meta(q).chapter_id === c.id) })).filter(g => g.items.length);
      // Diagnostic covers as many chapters as five questions permit.
      selection = balancedSelection(shuffled(groups, random).slice(0,5), 5, random, q => performance.seen.has(q.item_id) ? 0 : 1);
    } else {
      const rank = q => {
        const m = meta(q), topic = performance.topics.get(`${m.chapter_id}/${m.subtopic_id}`);
        const concept = Math.max(0, ...(q.concept_ids || []).map(id => {
          const p = performance.concepts.get(id);
          return p ? p.incorrect / (p.answered + 2) : 0;
        }));
        return (topic?.weakness || 0) * 10 + concept + (performance.seen.has(q.item_id) ? 0 : 0.5);
      };
      selection = eligible.sort((a,b) => rank(b) - rank(a)).slice(0,5);
    }
  } else if (spec.mode === 'master') {
    if(spec.count>MAX_MASTER_QUIZ_ITEMS)throw Error(`Choose no more than ${MAX_MASTER_QUIZ_ITEMS} questions per attempt.`);
    selection = balancedSelection(track.chapters.map(c => ({ id: c.id, items: all.filter(q => meta(q).chapter_id === c.id) })), spec.count, random);
  } else {
    if (!chapter) throw Error('Unknown chapter.');
    const items = all.filter(q => meta(q).chapter_id === chapter.id);
    if (spec.mode === 'topic') {
      if (!chapter.topics.some(t => t.id === spec.topic)) throw Error('Unknown instructional topic.');
      const pool = items.filter(q => meta(q).subtopic_id === spec.topic);
      if (pool.length < 5) throw Error(`Insufficient approved questions: ${pool.length}/5 distinct validated questions available.`);
      selection = shuffled(pool, random).slice(0,5);
    } else if (spec.mode === 'general') {
      selection = balancedSelection(chapter.topics.map(t => ({ id: t.id, items: items.filter(q => meta(q).subtopic_id === t.id) })),
        Math.max(GENERAL_POLICY.minimum, chapter.topics.length * GENERAL_POLICY.perTopic), random);
    } else throw Error('Unknown quiz mode.');
  }
  return { items: shuffled(selection, random), diagnostic, unreviewed:selection.some(q=>!approved(q)) };
}
export function makeV2Attempt(bank, curriculum, spec, attempts = {}, seed = randomSeed(), id = crypto.randomUUID()) {
  if (!Number.isInteger(seed) || seed < 0 || seed > 4294967295) throw Error('Invalid seed.');
  const isPractice = spec.content_tier === 'lesson-practice';
  const resolvedSpec = isPractice
    ? { ...spec, content_tier: 'lesson-practice' }
    : { ...spec, content_tier: 'lesson-assessment', format: 'formal' };
  const selected = selectQuestions(bank, curriculum, resolvedSpec, attempts, seed), random = rng(seed ^ 0xa5a5a5a5);
  const track = curriculum.find(t => t.id === resolvedSpec.track), chapter = track.chapters.find(c => c.id === resolvedSpec.chapter);
  const title = resolvedSpec.mode === 'topic' ? chapter.topics.find(t => t.id === resolvedSpec.topic).title
    : resolvedSpec.mode === 'general' ? `${chapter.title} — General Quiz`
    : resolvedSpec.mode === 'master' ? `${track.title || resolvedSpec.track} Master Quiz`
    : `Personalized ${track.title || resolvedSpec.track} Quiz${selected.diagnostic ? ' — diagnostic assessment' : ''}`;
  return { attempt_id: id, assessment_id: specKey(resolvedSpec), content_version: '2.0.0',
    quiz_v2: true, spec: resolvedSpec, title,
    diagnostic: selected.diagnostic, includes_unreviewed:selected.unreviewed, seed,
    practice: isPractice,
    xp_policy: isPractice ? 'unscored-v2' : 'verified-v2',
    ...(isPractice ? {} : { assessment_contract: 'quiz-v2-formal-1' }),
    presented: selected.items.map(q => ({ item_id: q.item_id, content_version: q.content_version, option_order: shuffled(q.options.map(o => o.id), random) })),
    responses: {}, position: 0, started_at: new Date().toISOString(), submitted_at: null };
}
