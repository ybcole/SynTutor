import { approved, reviewed, rng, shuffled, randomSeed, MAX_QUIZ_ITEMS } from './quiz-core.js';
import { isRelevantAssessmentQuestion } from './quiz-scope.js';
import { REQUIRED_CHAPTER_FORMATS, gradeQuestion, isMixedKind } from './quiz-mixed-eval.js';

export const GENERAL_POLICY = Object.freeze({ minimum: 5, perTopic: 1 });
export const MAX_MASTER_QUIZ_ITEMS = 50;
export const DEFAULT_MASTER_QUIZ_ITEMS = 25;
export const DIFFICULTIES = Object.freeze(['easy', 'medium', 'hard']);

export function chapterDifficulty(chapter) {
  const num = Number(chapter?.chapter || 0);
  const id = String(chapter?.id || '');
  if (id.startsWith('br-')) {
    if (num <= 4) return 'easy';
    if (num <= 8) return 'medium';
    return 'hard';
  }
  if (num <= 6) return 'easy';
  if (num <= 13) return 'medium';
  return 'hard';
}

export function questionDifficulty(q, curriculum) {
  if (DIFFICULTIES.includes(q?.difficulty)) return q.difficulty;
  const meta = questionMetadata(q, curriculum);
  const track = curriculum?.find(t => t.id === meta?.track_id);
  const chapter = track?.chapters.find(c => c.id === meta?.chapter_id);
  const base = chapterDifficulty(chapter);
  const complex = q?.kind === 'analysis' || Boolean(q?.answer_tree) || String(q?.prompt || '').length > 115;
  const foundational = q?.kind === 'rule_application' && String(q?.prompt || '').length <= 85;
  if (base === 'easy') return complex ? 'medium' : 'easy';
  if (base === 'hard') return foundational ? 'medium' : 'hard';
  return complex ? 'hard' : foundational ? 'easy' : 'medium';
}
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
  const questions=[...bank.items,...(bank.mixed_items||[]),...(bank.practice_items||[]),...(bank.assessment_items||[])];
  const rows = Object.values(attempts).filter(t => t.submitted_at && Array.isArray(t.presented) && t.responses)
    .sort((a,b) => a.submitted_at.localeCompare(b.submitted_at) || a.attempt_id.localeCompare(b.attempt_id));
  for (const t of rows) for (const r of t.presented) {
    const q = questions.find(q => q.item_id === r.item_id && q.content_version === r.content_version);
    const m = questionMetadata(q, curriculum);
    if (m?.track_id !== trackId) continue;
    const correct = gradeQuestion(q, t.responses[q.item_id]).correct;
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
  const pools = shuffled(groups, random).map(g => ({ ...g, items: shuffled(g.items, random), selected: [] }));
  if (pools.some(g => !g.items.length)) throw Error('Insufficient approved questions: every required topic or chapter needs approved questions.');
  if (pools.reduce((n,g) => n + g.items.length, 0) < count) throw Error('Not enough distinct approved questions for this count.');
  const kindCounts = new Map();
  const scoreItem = q => preference(q) * 1000 - (kindCounts.get(q?.kind || 'mcq') || 0);
  const bestIndex = items => {
    let best = 0, bestScore = scoreItem(items[0]);
    for (let j = 1; j < items.length; j++) {
      const s = scoreItem(items[j]);
      if (s > bestScore) { bestScore = s; best = j; }
    }
    return { index: best, score: bestScore };
  };
  for (let i = 0; i < count; i++) {
    let chosenPool = null, chosenIdx = 0, bestTier = -Infinity;
    for (const pool of pools) {
      if (!pool.items.length) continue;
      const cand = bestIndex(pool.items);
      if (!chosenPool
        || pool.selected.length < chosenPool.selected.length
        || (pool.selected.length === chosenPool.selected.length && cand.score > bestTier)) {
        chosenPool = pool;
        chosenIdx = cand.index;
        bestTier = cand.score;
      }
    }
    const [picked] = chosenPool.items.splice(chosenIdx, 1);
    chosenPool.selected.push(picked);
    const kind = picked?.kind || 'mcq';
    kindCounts.set(kind, (kindCounts.get(kind) || 0) + 1);
  }
  return pools.flatMap(g => g.selected);
}
export const specKey = spec => `quiz-v2:${spec.track}:${spec.mode}:${spec.chapter || ''}:${spec.topic || ''}:${spec.count || ''}${spec.mode === 'master' && DIFFICULTIES.includes(spec.difficulty) ? ':' + spec.difficulty : ''}${['lesson-practice','lesson-assessment'].includes(spec.content_tier)?':'+spec.content_tier:''}${spec.format==='formal'?':formal-1':spec.format==='mixed'?':mixed-1':''}`;

export function missedTopicsForTrack(bank, curriculum, attempts, trackId) {
  const perf = topicPerformance(bank, curriculum, attempts, trackId);
  const track = curriculum.find(t => t.id === trackId);
  if (!track || !perf.missed.size) return [];
  const entries = [];
  for (const [key, stats] of perf.topics.entries()) {
    if (!stats.incorrect) continue;
    const [chapterId, subtopicId] = key.split('/');
    const chapter = track.chapters.find(c => c.id === chapterId);
    const topic = chapter?.topics.find(t => t.id === subtopicId);
    if (!chapter || !topic) continue;
    entries.push({
      chapter_id: chapterId,
      subtopic_id: subtopicId,
      chapterTitle: chapter.title,
      title: topic.title,
      incorrect: stats.incorrect,
      weakness: stats.weakness,
    });
  }
  return entries.sort((a, b) => b.weakness - a.weakness || b.incorrect - a.incorrect);
}

const difficultyRank = { easy: 0, medium: 1, hard: 2 };

export function selectQuestions(bank, curriculum, spec, attempts = {}, seed = randomSeed()) {
  const random = rng(seed), track = curriculum.find(t => t.id === spec.track);
  if (!track) throw Error('Unknown quiz track.');
  // Deduplicate stable IDs even if multiple content versions become available.
  const all = [...new Map(eligibleQuestions(bank, curriculum, spec.track, spec.content_tier).map(q => [q.item_id, q])).values()];
  const meta = q => questionMetadata(q, curriculum);
  const chapter = track.chapters.find(c => c.id === spec.chapter);
  let selection;
  if (spec.format === 'mixed') {
    const mixedAll = [...new Map((bank.mixed_items || []).map(q => [q.item_id, q])).values()]
      .filter(q => !q.retired_from_selection && meta(q)?.track_id === spec.track);
    const formalAll = [...new Map(eligibleQuestions(bank, curriculum, spec.track, 'lesson-assessment').map(q => [q.item_id, q])).values()];
    const reqFormats = REQUIRED_CHAPTER_FORMATS[spec.track] || [];
    if (spec.mode === 'personalized') {
      const performance = topicPerformance(bank, curriculum, attempts, spec.track);
      if (!performance.missed.size) {
        throw Error('Complete a quiz with missed questions to unlock Review your errors.');
      }
      const keepEligible = q => !performance.missed.has(q.item_id)
        && (!q.practice_family || !performance.missedFamilies.has(q.practice_family))
        && !(q.practice_example_ids || []).some(id => performance.missedExamples.has(id));
      const eligibleMixed = shuffled(mixedAll.filter(keepEligible), random);
      const eligibleFormal = shuffled(formalAll.filter(keepEligible), random);
      const totalAvail = eligibleMixed.length + eligibleFormal.length;
      if (totalAvail < 5) {
        throw Error(`Only ${totalAvail} eligible questions remain after excluding every previously missed question. Five are required; try another available topic quiz.`);
      }
      if (!eligibleMixed.length) {
        throw Error('Missing non-MCQ review questions after excluding previously missed items.');
      }
      const rank = q => {
        const m = meta(q), topic = performance.topics.get(`${m.chapter_id}/${m.subtopic_id}`);
        const topicMissBonus = topic?.incorrect ? 20 + topic.weakness * 10 : 0;
        const concept = Math.max(0, ...(q.concept_ids || []).map(id => {
          const p = performance.concepts.get(id);
          return p && p.incorrect ? p.incorrect / (p.answered + 2) : 0;
        }));
        return topicMissBonus + concept * 5 + (performance.seen.has(q.item_id) ? 0 : 0.5);
      };
      eligibleMixed.sort((a, b) => rank(b) - rank(a));
      eligibleFormal.sort((a, b) => rank(b) - rank(a));
      const picks = [], seenIds = new Set();
      for (const fmt of shuffled(reqFormats, random)) {
        if (picks.length >= 5) break;
        const cand = eligibleMixed.find(q => q.kind === fmt && !seenIds.has(q.item_id));
        if (cand) { picks.push(cand); seenIds.add(cand.item_id); }
      }
      const kindCounts = new Map();
      for (const q of picks) kindCounts.set(q.kind, (kindCounts.get(q.kind) || 0) + 1);
      while (picks.length < 5) {
        const remMixed = eligibleMixed.filter(q => !seenIds.has(q.item_id))
          .sort((a, b) => (rank(b) - (kindCounts.get(b.kind) || 0) * 3) - (rank(a) - (kindCounts.get(a.kind) || 0) * 3));
        const nextQ = remMixed[0] || eligibleFormal.find(q => !seenIds.has(q.item_id));
        if (!nextQ) break;
        picks.push(nextQ);
        seenIds.add(nextQ.item_id);
        kindCounts.set(nextQ.kind, (kindCounts.get(nextQ.kind) || 0) + 1);
      }
      selection = picks;
    } else if (spec.mode === 'master') {
      if (spec.count > MAX_MASTER_QUIZ_ITEMS) throw Error(`Choose no more than ${MAX_MASTER_QUIZ_ITEMS} questions per attempt.`);
      if (!Number.isInteger(spec.count) || spec.count < track.chapters.length) {
        throw Error(`Choose at least ${track.chapters.length} questions to cover every group.`);
      }
      if (spec.difficulty !== undefined && !DIFFICULTIES.includes(spec.difficulty)) {
        throw Error('Invalid Master Quiz difficulty.');
      }
      for (const c of track.chapters) {
        if (!mixedAll.some(q => meta(q).chapter_id === c.id)) {
          throw Error(`Missing mixed-format questions for ${c.id}.`);
        }
      }
      const targetRank = spec.difficulty ? difficultyRank[spec.difficulty] : null;
      const diffScore = q => targetRank === null ? 0 : -Math.abs(difficultyRank[questionDifficulty(q, curriculum)] - targetRank);
      const chapterMap = new Map(track.chapters.map(c => [c.id, {
        id: c.id,
        mixed: shuffled(mixedAll.filter(q => meta(q).chapter_id === c.id), random),
        formal: shuffled(formalAll.filter(q => meta(q).chapter_id === c.id), random),
        selected: [],
      }]));
      const seenIds = new Set();
      const kindCounts = new Map();
      // Reserve at least one item of every mandatory format across distinct chapters first.
      for (const fmt of reqFormats) {
        const pools = shuffled([...chapterMap.values()].filter(g => !g.selected.length && g.mixed.some(q => q.kind === fmt && !seenIds.has(q.item_id))), random);
        const fallbackPools = pools.length ? pools : shuffled([...chapterMap.values()].filter(g => g.mixed.some(q => q.kind === fmt && !seenIds.has(q.item_id))), random);
        if (!fallbackPools.length) throw Error(`Missing required "${fmt}" questions for ${spec.track} Master Quiz.`);
        const chosenGroup = fallbackPools.sort((a, b) => a.selected.length - b.selected.length)[0];
        const cand = chosenGroup.mixed
          .filter(q => q.kind === fmt && !seenIds.has(q.item_id))
          .sort((a, b) => diffScore(b) - diffScore(a))[0];
        chosenGroup.selected.push(cand);
        seenIds.add(cand.item_id);
        kindCounts.set(cand.kind, (kindCounts.get(cand.kind) || 0) + 1);
      }
      const allGroups = shuffled([...chapterMap.values()], random);
      while ([...chapterMap.values()].reduce((n, g) => n + g.selected.length, 0) < spec.count) {
        let bestGroup = null, bestCand = null, bestScore = -Infinity, minSel = Infinity;
        for (const g of allGroups) {
          const avail = [...g.mixed, ...g.formal].filter(q => !seenIds.has(q.item_id));
          if (!avail.length) continue;
          const scoreQ = q => (isMixedKind(q.kind) ? 500 : 0) + diffScore(q) * 20 - (kindCounts.get(q.kind) || 0) * 4;
          avail.sort((a, b) => scoreQ(b) - scoreQ(a));
          const topScore = scoreQ(avail[0]);
          if (g.selected.length < minSel || (g.selected.length === minSel && topScore > bestScore)) {
            minSel = g.selected.length;
            bestGroup = g;
            bestCand = avail[0];
            bestScore = topScore;
          }
        }
        if (!bestGroup || !bestCand) throw Error('Not enough distinct questions for this Master Quiz count.');
        bestGroup.selected.push(bestCand);
        seenIds.add(bestCand.item_id);
        kindCounts.set(bestCand.kind, (kindCounts.get(bestCand.kind) || 0) + 1);
      }
      selection = [...chapterMap.values()].flatMap(g => g.selected);
    } else if (spec.mode === 'topic') {
      if (!chapter) throw Error('Unknown chapter.');
      if (!chapter.topics.some(t => t.id === spec.topic)) throw Error('Unknown instructional topic.');
      const mixedPool = shuffled(mixedAll.filter(q => meta(q).chapter_id === chapter.id && meta(q).subtopic_id === spec.topic), random);
      const suppPool = shuffled(formalAll.filter(q => meta(q).chapter_id === chapter.id && meta(q).subtopic_id === spec.topic), random);
      const distinctMixedKinds = new Set(mixedPool.map(q => q.kind));
      if (distinctMixedKinds.size < 2) {
        throw Error(`Insufficient multi-format questions for ${chapter.id}/${spec.topic} (found ${distinctMixedKinds.size} non-MCQ format).`);
      }
      const picks = [], seenIds = new Set();
      for (const fmt of shuffled([...distinctMixedKinds], random)) {
        const cand = mixedPool.find(q => q.kind === fmt && !seenIds.has(q.item_id));
        if (cand) { picks.push(cand); seenIds.add(cand.item_id); }
      }
      // Keep room for 1 supplementary reviewed MCQ when available while keeping >=2-4 non-MCQ questions.
      const mixedCap = suppPool.length >= 1 ? 4 : 5;
      for (const q of mixedPool) {
        if (picks.length >= mixedCap) break;
        if (!seenIds.has(q.item_id)) { picks.push(q); seenIds.add(q.item_id); }
      }
      for (const q of [...suppPool, ...mixedPool]) {
        if (picks.length >= 5) break;
        if (!seenIds.has(q.item_id)) { picks.push(q); seenIds.add(q.item_id); }
      }
      if (picks.length < 5) {
        throw Error(`Insufficient approved questions: ${picks.length}/5 distinct validated questions available.`);
      }
      selection = picks;
    } else if (spec.mode === 'general') {
      if (!chapter) throw Error('Unknown chapter.');
      const targetCount = Math.max(GENERAL_POLICY.minimum, chapter.topics.length * GENERAL_POLICY.perTopic);
      const mixedPool = mixedAll.filter(q => meta(q).chapter_id === chapter.id);
      const formalFallback = formalAll.filter(q => meta(q).chapter_id === chapter.id);
      const picks = [], seenIds = new Set(), coveredTopics = new Set();
      for (const fmt of reqFormats) {
        const candidates = shuffled(mixedPool.filter(q => q.kind === fmt && !seenIds.has(q.item_id)), random)
          .sort((a, b) => Number(coveredTopics.has(meta(a).subtopic_id)) - Number(coveredTopics.has(meta(b).subtopic_id)));
        if (!candidates.length) {
          throw Error(`Missing required "${fmt}" questions for ${chapter.id}.`);
        }
        picks.push(candidates[0]);
        seenIds.add(candidates[0].item_id);
        coveredTopics.add(meta(candidates[0]).subtopic_id);
      }
      const combinedPool = [...shuffled(mixedPool, random), ...shuffled(formalFallback, random)];
      for (const topic of shuffled(chapter.topics, random)) {
        if (picks.length >= targetCount) break;
        if (coveredTopics.has(topic.id)) continue;
        const cand = combinedPool.find(q => !seenIds.has(q.item_id) && meta(q).subtopic_id === topic.id);
        if (cand) {
          picks.push(cand);
          seenIds.add(cand.item_id);
          coveredTopics.add(topic.id);
        }
      }
      const kindCounts = new Map();
      for (const q of picks) kindCounts.set(q.kind, (kindCounts.get(q.kind) || 0) + 1);
      while (picks.length < targetCount) {
        const remaining = combinedPool
          .filter(q => !seenIds.has(q.item_id))
          .sort((a, b) => (isMixedKind(b.kind) ? 1 : 0) - (isMixedKind(a.kind) ? 1 : 0)
            || (kindCounts.get(a.kind) || 0) - (kindCounts.get(b.kind) || 0));
        if (!remaining.length) throw Error(`Not enough distinct questions for ${chapter.id}.`);
        picks.push(remaining[0]);
        seenIds.add(remaining[0].item_id);
        kindCounts.set(remaining[0].kind, (kindCounts.get(remaining[0].kind) || 0) + 1);
      }
      selection = picks;
    } else throw Error('Unknown quiz mode.');
  } else if (spec.mode === 'personalized') {
    const performance = topicPerformance(bank, curriculum, attempts, spec.track);
    if (!performance.missed.size) {
      throw Error('Complete a quiz with missed questions to unlock Review your errors.');
    }
    const eligible = shuffled(all.filter(q => !performance.missed.has(q.item_id)
      && (!q.practice_family || !performance.missedFamilies.has(q.practice_family))
      && !(q.practice_example_ids || []).some(id => performance.missedExamples.has(id))), random);
    if (eligible.length < 5) {
      throw Error(`Only ${eligible.length} eligible questions remain after excluding every previously missed question. Five are required; try another available topic quiz.`);
    }
    const rank = q => {
      const m = meta(q), topic = performance.topics.get(`${m.chapter_id}/${m.subtopic_id}`);
      const topicMissBonus = topic?.incorrect ? 20 + topic.weakness * 10 : 0;
      const concept = Math.max(0, ...(q.concept_ids || []).map(id => {
        const p = performance.concepts.get(id);
        return p && p.incorrect ? p.incorrect / (p.answered + 2) : 0;
      }));
      return topicMissBonus + concept * 5 + (performance.seen.has(q.item_id) ? 0 : 0.5);
    };
    selection = eligible.sort((a, b) => rank(b) - rank(a)).slice(0, 5);
  } else if (spec.mode === 'master') {
    if (spec.count > MAX_MASTER_QUIZ_ITEMS) throw Error(`Choose no more than ${MAX_MASTER_QUIZ_ITEMS} questions per attempt.`);
    if (spec.difficulty !== undefined && !DIFFICULTIES.includes(spec.difficulty)) {
      throw Error('Invalid Master Quiz difficulty.');
    }
    const targetRank = spec.difficulty ? difficultyRank[spec.difficulty] : null;
    const pref = targetRank === null
      ? () => 0
      : q => -Math.abs(difficultyRank[questionDifficulty(q, curriculum)] - targetRank);
    selection = balancedSelection(
      track.chapters.map(c => ({ id: c.id, items: all.filter(q => meta(q).chapter_id === c.id) })),
      spec.count,
      random,
      pref,
    );
  } else {
    if (!chapter) throw Error('Unknown chapter.');
    const items = all.filter(q => meta(q).chapter_id === chapter.id);
    if (spec.mode === 'topic') {
      if (!chapter.topics.some(t => t.id === spec.topic)) throw Error('Unknown instructional topic.');
      const pool = items.filter(q => meta(q).subtopic_id === spec.topic);
      if (pool.length < 5) throw Error(`Insufficient approved questions: ${pool.length}/5 distinct validated questions available.`);
      selection = balancedSelection([{ id: spec.topic, items: pool }], 5, random);
    } else if (spec.mode === 'general') {
      const groups = chapter.topics.map(t => ({ id: t.id, items: items.filter(q => meta(q).subtopic_id === t.id) }));
      selection = balancedSelection(
        groups,
        Math.max(GENERAL_POLICY.minimum, chapter.topics.length * GENERAL_POLICY.perTopic),
        random,
      );
    } else throw Error('Unknown quiz mode.');
  }
  const items = shuffled(selection, random);
  return { items, diagnostic: false, unreviewed: items.some(q => !approved(q) && !isMixedKind(q.kind)) };
}

function scrambledTokenOrder(tokens, random) {
  const order = shuffled(tokens.map((_, i) => i), random);
  if (order.length >= 2 && order.every((v, idx) => v === idx)) {
    [order[0], order[1]] = [order[1], order[0]];
  }
  return order;
}

export function makeV2Attempt(bank, curriculum, spec, attempts = {}, seed = randomSeed(), id = crypto.randomUUID()) {
  if (!Number.isInteger(seed) || seed < 0 || seed > 4294967295) throw Error('Invalid seed.');
  const isMixed = spec.format === 'mixed';
  const isPractice = spec.content_tier === 'lesson-practice' || isMixed;
  const resolvedSpec = isPractice
    ? { ...spec, content_tier: 'lesson-practice', ...(isMixed ? { format: 'mixed' } : {}) }
    : { ...spec, content_tier: 'lesson-assessment', format: 'formal' };
  const selected = selectQuestions(bank, curriculum, resolvedSpec, attempts, seed), random = rng(seed ^ 0xa5a5a5a5);
  const track = curriculum.find(t => t.id === resolvedSpec.track), chapter = track.chapters.find(c => c.id === resolvedSpec.chapter);
  const diffLabel = resolvedSpec.mode === 'master' && DIFFICULTIES.includes(resolvedSpec.difficulty)
    ? ` (${resolvedSpec.difficulty[0].toUpperCase() + resolvedSpec.difficulty.slice(1)})`
    : '';
  const title = resolvedSpec.mode === 'topic' ? chapter.topics.find(t => t.id === resolvedSpec.topic).title
    : resolvedSpec.mode === 'general' ? `${chapter.title} — General Quiz`
    : resolvedSpec.mode === 'master' ? `${track.title || resolvedSpec.track} Master Quiz${diffLabel}`
    : 'Review your Errors';
  return { attempt_id: id, assessment_id: specKey(resolvedSpec), content_version: '2.0.0',
    quiz_v2: true, spec: resolvedSpec, title,
    diagnostic: selected.diagnostic, includes_unreviewed: selected.unreviewed, seed,
    practice: isPractice,
    xp_policy: isPractice ? 'unscored-v2' : 'verified-v2',
    ...(isPractice ? {} : { assessment_contract: 'quiz-v2-formal-1' }),
    presented: selected.items.map(q => ({
      item_id: q.item_id,
      content_version: q.content_version,
      ...(Array.isArray(q.options) ? { option_order: shuffled(q.options.map(o => o.id), random) } : {}),
      ...(q.kind === 'sentence_reconstruction' && Array.isArray(q.tokens) ? { token_order: scrambledTokenOrder(q.tokens, random) } : {}),
    })),
    responses: {}, position: 0, started_at: new Date().toISOString(), submitted_at: null };
}
