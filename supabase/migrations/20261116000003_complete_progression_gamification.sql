-- Complete progression cutover:
-- 1. Seed & activate all active Syntax Foundations (2.0.0) and Grammar (3.1.0) revised lessons
-- 2. Enforce Master Quiz max 50 questions on new attempts without breaking historical/existing rows
-- 3. Enable public opt-in leaderboard release flag
-- 4. Upgrade achievements to score active lessons, Quiz V2, mastery, and cross-track milestones
begin;

-- 1. Allow both Syntax Foundations (br-01..11) and Cambridge Grammar (cgel-*) in foundation_assessments.
alter table public.foundation_assessments
  drop constraint if exists foundation_assessments_lesson_id_check;
alter table public.foundation_assessments
  add constraint foundation_assessments_lesson_id_check
  check (lesson_id ~ '^(br-(0[1-9]|1[01])|cgel-(clauses|ch(0[1-9]|1[0-9]|20)))$');

create or replace function public.set_foundation_active_version(p_lesson_id text, p_version text)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if p_lesson_id is null or p_lesson_id !~ '^(br-(0[1-9]|1[01])|cgel-(clauses|ch(0[1-9]|1[0-9]|20)))$' then
    raise exception 'Unsupported active lesson identifier';
  end if;
  perform pg_catalog.pg_advisory_xact_lock(44792011);
  lock table public.quiz_xp_events_v1, public.quiz_xp_events_v2, public.player_stats in share row exclusive mode;
  if p_version is null then
    delete from public.foundation_active where lesson_id = p_lesson_id;
  else
    insert into public.foundation_active (lesson_id, content_version) values (p_lesson_id, p_version)
      on conflict (lesson_id) do update set content_version = excluded.content_version;
  end if;
  with totals as (
    select user_id, sum(xp)::integer as xp from public.xp_activity_ledger group by user_id
  ), accounts as (
    select user_id from public.player_stats union select user_id from totals
  )
  insert into public.player_stats (user_id, xp, level)
    select a.user_id, coalesce(t.xp, 0), public.lesson_level_for_xp(coalesce(t.xp, 0))
    from accounts a left join totals t using (user_id)
  on conflict (user_id) do update set xp = excluded.xp, level = excluded.level, updated_at = now()
    where public.player_stats.xp is distinct from excluded.xp
       or public.player_stats.level is distinct from excluded.level;
end;
$$;
revoke all on function public.set_foundation_active_version(text,text) from public, anon, authenticated;

insert into public.foundation_assessments (lesson_id, content_version, required_sections, opening, closing) values
('br-01', '2.0.0', array['introduction','concepts','worked-example','application','recap']::text[], '{"opening-replace":{"position":0,"options":["a","b","c"],"answer":"b"},"opening-where":{"position":1,"options":["a","b","c"],"answer":"c"},"opening-brackets":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-readings":{"position":3,"options":["a","b","c"],"answer":"c"},"opening-omit":{"position":4,"options":["a","b","c"],"answer":"b"}}'::jsonb, '{"closing-omit":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-brackets":{"position":1,"options":["a","b","c"],"answer":"b"},"closing-direct":{"position":2,"options":["a","b","c"],"answer":"c"},"closing-context":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-attachment":{"position":4,"options":["a","b","c"],"answer":"b"}}'::jsonb),
('br-02', '2.0.0', array['introduction','concepts','worked-example','application','recap']::text[], '{"opening-subject":{"position":0,"options":["a","b","c"],"answer":"b"},"opening-predicate":{"position":1,"options":["a","b","c"],"answer":"c"},"opening-position":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-omission":{"position":3,"options":["a","b","c"],"answer":"b"},"opening-question":{"position":4,"options":["a","b","c"],"answer":"c"}}'::jsonb, '{"closing-boundary":{"position":0,"options":["a","b","c"],"answer":"b"},"closing-category":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-sisters":{"position":2,"options":["a","b","c"],"answer":"c"},"closing-modifier":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-complement":{"position":4,"options":["a","b","c"],"answer":"b"}}'::jsonb),
('br-03', '2.0.0', array['introduction','concepts','worked-example','prepositions-and-coordination','application','recap']::text[], '{"opening-replacement":{"position":0,"options":["a","b","c"],"answer":"b"},"opening-description":{"position":1,"options":["a","b","c"],"answer":"c"},"opening-manner":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-location":{"position":3,"options":["a","b","c"],"answer":"b"},"opening-coordination":{"position":4,"options":["a","b","c"],"answer":"c"}}'::jsonb, '{"closing-name":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-ap":{"position":1,"options":["a","b","c"],"answer":"b"},"closing-advp":{"position":2,"options":["a","b","c"],"answer":"c"},"closing-pp":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-coordination":{"position":4,"options":["a","b","c"],"answer":"b"}}'::jsonb),
('br-04', '2.0.0', array['introduction','concepts','worked-example','predicatives','prepositional-complements','application','recap']::text[], '{"opening-verb":{"position":0,"options":["a","b","c"],"answer":"b"},"opening-object":{"position":1,"options":["a","b","c"],"answer":"c"},"opening-recipient":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-description":{"position":3,"options":["a","b","c"],"answer":"b"},"opening-location":{"position":4,"options":["a","b","c"],"answer":"c"}}'::jsonb, '{"closing-vp":{"position":0,"options":["a","b","c"],"answer":"b"},"closing-recipient":{"position":1,"options":["a","b","c"],"answer":"c"},"closing-subject-predicative":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-object-predicative":{"position":3,"options":["a","b","c"],"answer":"b"},"closing-pp-complement":{"position":4,"options":["a","b","c"],"answer":"c"}}'::jsonb),
('br-05', '2.0.0', array['introduction','concepts','worked-example','mobility','particles','ellipsis','application','recap']::text[], '{"opening-time":{"position":0,"options":["a","b","c"],"answer":"b"},"opening-placement":{"position":1,"options":["a","b","c"],"answer":"c"},"opening-particle":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-understood":{"position":3,"options":["a","b","c"],"answer":"b"},"opening-scope":{"position":4,"options":["a","b","c"],"answer":"c"}}'::jsonb, '{"closing-replacement":{"position":0,"options":["a","b","c"],"answer":"b"},"closing-complement":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-particle":{"position":2,"options":["a","b","c"],"answer":"c"},"closing-ellipsis":{"position":3,"options":["a","b","c"],"answer":"b"},"closing-scope":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('br-06', '2.0.0', array['introduction','concepts','chain','adverbials','passive','negation','questions','recap']::text[], '{"opening-tense":{"position":0,"options":["a","b","c"],"answer":"b"},"opening-vps":{"position":1,"options":["a","b","c"],"answer":"c"},"opening-negation":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-question":{"position":3,"options":["a","b","c"],"answer":"b"},"opening-passive":{"position":4,"options":["a","b","c"],"answer":"c"}}'::jsonb, '{"closing-chain":{"position":0,"options":["a","b","c"],"answer":"b"},"closing-tense":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-dosupport":{"position":2,"options":["a","b","c"],"answer":"c"},"closing-fronting":{"position":3,"options":["a","b","c"],"answer":"b"},"closing-copula":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('br-07', '2.0.0', array['introduction','concepts','worked-example','pre-modifiers','post-modifiers','application','recap']::text[], '{"opening-head":{"position":0,"options":["a","b","c"],"answer":"b"},"opening-before-det":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-colour":{"position":2,"options":["a","b","c"],"answer":"c"},"opening-origin":{"position":3,"options":["a","b","c"],"answer":"b"},"opening-pronoun":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-empty-det":{"position":0,"options":["a","b","c"],"answer":"c"},"closing-predet":{"position":1,"options":["a","b","c"],"answer":"b"},"closing-inner-nom":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-pp-scope":{"position":3,"options":["a","b","c"],"answer":"c"},"closing-modified-pronoun":{"position":4,"options":["a","b","c"],"answer":"b"}}'::jsonb),
('br-08', '2.0.0', array['introduction','concepts','worked-example','clausal-subjects-and-objects','clausal-complements','adverbial-clauses','application','recap']::text[], '{"opening-report":{"position":0,"options":["a","b","c"],"answer":"b"},"opening-question":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-subject":{"position":2,"options":["a","b","c"],"answer":"c"},"opening-claim":{"position":3,"options":["a","b","c"],"answer":"b"},"opening-reason":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-nesting":{"position":0,"options":["a","b","c"],"answer":"c"},"closing-empty-c":{"position":1,"options":["a","b","c"],"answer":"b"},"closing-question-order":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-extraposition":{"position":3,"options":["a","b","c"],"answer":"c"},"closing-after":{"position":4,"options":["a","b","c"],"answer":"b"}}'::jsonb),
('br-09', '2.0.0', array['introduction','concepts','worked-example','embedded-interrogatives','relatives-and-complements','relative-scope','application','recap']::text[], '{"opening-object":{"position":0,"options":["a","b","c"],"answer":"b"},"opening-subject":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-embedded":{"position":2,"options":["a","b","c"],"answer":"c"},"opening-content":{"position":3,"options":["a","b","c"],"answer":"b"},"opening-subset":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-stranded":{"position":0,"options":["a","b","c"],"answer":"c"},"closing-front-positions":{"position":1,"options":["a","b","c"],"answer":"b"},"closing-relative-that":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-restrictive":{"position":3,"options":["a","b","c"],"answer":"c"},"closing-non-restrictive":{"position":4,"options":["a","b","c"],"answer":"b"}}'::jsonb),
('br-10', '2.0.0', array['introduction','concepts','worked-example','subjects-and-control','clause-functions','verb-complements','application','recap']::text[], '{"opening-tense":{"position":0,"options":["a","b","c"],"answer":"b"},"opening-bare":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-controller":{"position":2,"options":["a","b","c"],"answer":"c"},"opening-for":{"position":3,"options":["a","b","c"],"answer":"b"},"opening-purpose":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-bare":{"position":0,"options":["a","b","c"],"answer":"c"},"closing-to":{"position":1,"options":["a","b","c"],"answer":"b"},"closing-free":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-types":{"position":3,"options":["a","b","c"],"answer":"c"},"closing-preposition":{"position":4,"options":["a","b","c"],"answer":"b"}}'::jsonb),
('br-11', '2.0.0', array['introduction','concepts','worked-example','apply-the-rule','rule-and-structure','application','recap']::text[], '{"opening-list":{"position":0,"options":["a","b","c"],"answer":"b"},"opening-input":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-reuse":{"position":2,"options":["a","b","c"],"answer":"c"},"opening-grouping":{"position":3,"options":["a","b","c"],"answer":"b"},"opening-tree":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-recursion":{"position":0,"options":["a","b","c"],"answer":"c"},"closing-incomplete":{"position":1,"options":["a","b","c"],"answer":"b"},"closing-brackets":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-order":{"position":3,"options":["a","b","c"],"answer":"c"},"closing-structure":{"position":4,"options":["a","b","c"],"answer":"b"}}'::jsonb),
('cgel-ch01', '3.1.0', array['what-this-course-covers','prescriptive-descriptive','disagreement','speech-writing','description-theory','constituent-structure','categories-functions','morphology','defining-concepts','truth-entailment','implicature-presupposition','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"b"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-clauses', '3.1.0', array['grammar-map','sentence-clause','canonical-clauses','counterparts-processes','verb-head','complements','nouns-noun-phrases','adjective-adverb-preposition','adjuncts','negation-polarity','clause-type-force','subordinate-clauses','nonfinite-catenative','coordination-supplementation','information-packaging','deixis-anaphora','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch03', '3.1.0', array['verb-phrase','verb-forms','auxiliaries','auxiliary-chain','tense-time','perfect','situations-aspect','progressive','mood-modality','modal-auxiliaries','modal-scope','future-time','verb-in-discourse','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch04', '3.1.0', array['clause-functions','core-noncore','clause-patterns','semantic-roles','subject','objects','predicative-complements','copular-clauses','prepositional-verbs','particles-idioms','light-verbs','multiple-patterns','complementation-in-use','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch05', '3.1.0', array['nouns-nps','noun-classes','number-countability','determiner','quantification','reference','fused-heads','pronouns','internal-dependents','np-order','case','genitives','gender-agreement','subject-verb-agreement','proper-names','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch06', '3.1.0', array['preliminaries','criterial-properties','category-boundaries','adjp-complementation','adjp-modification','restricted-adjectives','adverbs','advp-structure','adverb-position','focusing-adverbs','modifier-style','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch07', '3.1.0', array['prepositions-heads','category-membership','category-contrasts','pp-complementation','pp-modification','stranding-order','idiomatic-pps','pp-functions','grammaticised','space-time','preposition-style','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch08', '3.1.0', array['adjuncts-map','parameters','manner-means-instrument','act-related','space','time-duration','frequency-degree','cause-result','concession','conditionals-open','conditionals-remote','domain-modality','evaluation-speech-connective','position','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch09', '3.1.0', array['polarity-tests','negation-types','verbal-negation','nonverbal-negation','approximate-affixal','npis','ppis-nonaffirmative','scope-focus','specificity','multiple-negation','metalinguistic','responses','negation-style','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch10', '3.1.0', array['clause-type-system','form-force','declarative-interrogative','exclamative-imperative','indirect-speech-acts','kinds-questions','polar-alternative','variable-direction','biased-questions','echo-questions','tags-parentheticals','question-presuppositions','interrogative-words','exclamatives','imperatives-directives','minor-clause-types','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch11', '3.1.0', array['subordination','finite-classes','content-clause-type','that-declaratives','that-omission','functions-subject','functions-complements','interrogative-content','interrogative-constructions','exclamative-content','mood-factivity','reported-speech-indirect','reported-speech-direct','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch12', '3.1.0', array['relative-constructions','formal-types','relational-types','relativisation-gaps','relative-phrases','relativisation-range','integrated-relatives','supplementary-relatives','relative-position','infinitival-relatives','fused-relatives','unbounded-dependencies','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch13', '3.1.0', array['comparison-preliminaries','scalar-non-scalar','term-set','governors-phrases','comparative-clauses','than-as-single','likeness-contrast','scalar-inequality','scalar-equality','modification-correlative','non-scalar','as-like-unlike','set-comparison','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch14', '3.1.0', array['finite-nonfinite','form-types','infinitival-structure','auxiliaries-voice','subjectless-hollow','catenative-simple','catenative-complex','catenative-analysis','catenative-classes','hollow-clauses','control-raising','noncatenative','other-complements','modifiers-supplements','verbless-clauses','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch15', '3.1.0', array['coordination-overview','coordinate-structure','coordination-types','layered-scope','clausal-subclausal','order','and-or','both-either-neither','linkers','range','non-basic','supplementation','supplement-forms','constituency-scope','dislocation-parentheticals','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch16', '3.1.0', array['packaging-overview','reordering-realignment','information-concepts','preposing','postposing','inversion','existential','extraposition','dislocation','clefts','passive-syntax','passive-pragmatics','presentational','cleft-presupposition','combinations','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch17', '3.1.0', array['deixis','anaphora','personal-pronouns','third-person','anticipatory','special-it','reflexives','binding-domains','reciprocals','demonstratives','reduced-nps','reduced-vps','ellipsis','spatial-deixis','temporal-deixis','comparatives-reduced','discourse-location','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch18', '3.1.0', array['inflection-word-formation','lexical-base','inflectional-categories','alternation-syncretism','speech-writing','phonological-alternations','spelling-alternations','grade','noun-plurals','genitive','verb-forms','complex-bases','weak-forms','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch19', '3.1.0', array['established-potential','morphological-structure','constituent-structure','productivity','minor-processes','conversion','compound-nouns','compound-adjectives','compound-headedness','affixation','derivational-alternations','evaluative-gender','negatives','proper-name-derivatives','nominalisation','adjectivalisation-verbalisation','numerals','neologisms','borrowing-classical','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb),
('cgel-ch20', '3.1.0', array['domain','indicators-characters','rules-variation','orthographic-units','functions','primary-terminals','secondary-boundaries','comma-uses','parentheses-dash','quotation','capitalisation','word-level','apostrophe-slash','chapter-review']::text[], '{"opening-1":{"position":0,"options":["a","b","c"],"answer":"a"},"opening-2":{"position":1,"options":["a","b","c"],"answer":"a"},"opening-3":{"position":2,"options":["a","b","c"],"answer":"a"},"opening-4":{"position":3,"options":["a","b","c"],"answer":"a"},"opening-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb, '{"closing-1":{"position":0,"options":["a","b","c"],"answer":"a"},"closing-2":{"position":1,"options":["a","b","c"],"answer":"a"},"closing-3":{"position":2,"options":["a","b","c"],"answer":"a"},"closing-4":{"position":3,"options":["a","b","c"],"answer":"a"},"closing-5":{"position":4,"options":["a","b","c"],"answer":"a"}}'::jsonb)
on conflict (lesson_id, content_version) do nothing;

insert into public.foundation_active (lesson_id, content_version) values
('br-01', '2.0.0'),
('br-02', '2.0.0'),
('br-03', '2.0.0'),
('br-04', '2.0.0'),
('br-05', '2.0.0'),
('br-06', '2.0.0'),
('br-07', '2.0.0'),
('br-08', '2.0.0'),
('br-09', '2.0.0'),
('br-10', '2.0.0'),
('br-11', '2.0.0'),
('cgel-ch01', '3.1.0'),
('cgel-clauses', '3.1.0'),
('cgel-ch03', '3.1.0'),
('cgel-ch04', '3.1.0'),
('cgel-ch05', '3.1.0'),
('cgel-ch06', '3.1.0'),
('cgel-ch07', '3.1.0'),
('cgel-ch08', '3.1.0'),
('cgel-ch09', '3.1.0'),
('cgel-ch10', '3.1.0'),
('cgel-ch11', '3.1.0'),
('cgel-ch12', '3.1.0'),
('cgel-ch13', '3.1.0'),
('cgel-ch14', '3.1.0'),
('cgel-ch15', '3.1.0'),
('cgel-ch16', '3.1.0'),
('cgel-ch17', '3.1.0'),
('cgel-ch18', '3.1.0'),
('cgel-ch19', '3.1.0'),
('cgel-ch20', '3.1.0')
on conflict (lesson_id) do update set content_version = excluded.content_version;

with totals as (
  select user_id, sum(xp)::integer as xp from public.xp_activity_ledger group by user_id
), accounts as (
  select user_id from public.player_stats union select user_id from totals
)
insert into public.player_stats (user_id, xp, level)
  select a.user_id, coalesce(t.xp, 0), public.lesson_level_for_xp(coalesce(t.xp, 0))
  from accounts a left join totals t using (user_id)
on conflict (user_id) do update set xp = excluded.xp, level = excluded.level, updated_at = now()
  where public.player_stats.xp is distinct from excluded.xp
     or public.player_stats.level is distinct from excluded.level;

-- 2. Enforce Master Quiz 50-question cap for NEW attempts while keeping historical/unfinished attempts valid.
create or replace function public.save_quiz_v2_attempt(p_attempt jsonb, p_submit boolean default false)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  uid text := nullif(auth.jwt()->>'sub', '');
  aid uuid;
  spec_obj jsonb;
  mode_name text;
  pres_len integer;
  n bigint;
  pos integer;
  old public.quiz_attempts_v2%rowtype;
  best public.quiz_best_scores_v2%rowtype;
  ref jsonb;
  q public.quiz_items_v1%rowtype;
  response text;
  seen_ids jsonb := '[]';
  score integer := 0;
  earned integer := 0;
  completed timestamptz;
begin
  if uid is null or length(uid) > 255 then
    raise exception 'Sign in to save quiz attempts' using errcode = '42501';
  end if;
  if jsonb_typeof(p_attempt) is distinct from 'object'
    or octet_length(p_attempt::text) > 500000
    or exists (
      select 1 from jsonb_object_keys(p_attempt) k
      where k not in ('attempt_id', 'assessment_id', 'content_version', 'spec', 'title', 'diagnostic', 'seed', 'presented', 'responses', 'position')
    )
    or coalesce(p_attempt->>'content_version', '') <> '2.0.0'
    or coalesce(p_attempt->>'assessment_id', '') !~ '^quiz-v2:.+:lesson-assessment:formal-1$'
    or jsonb_typeof(p_attempt->'spec') is distinct from 'object'
    or jsonb_typeof(p_attempt->'seed') is distinct from 'number'
    or (p_attempt->>'seed') !~ '^[0-9]{1,10}$'
    or jsonb_typeof(p_attempt->'position') is distinct from 'number'
    or (p_attempt->>'position') !~ '^[0-9]{1,4}$'
    or jsonb_typeof(p_attempt->'presented') is distinct from 'array'
    or jsonb_typeof(p_attempt->'responses') is distinct from 'object'
  then
    raise exception 'Invalid quiz v2 assessment payload' using errcode = '22023';
  end if;

  aid := (p_attempt->>'attempt_id')::uuid;
  n := (p_attempt->>'seed')::bigint;
  pos := (p_attempt->>'position')::integer;
  pres_len := jsonb_array_length(p_attempt->'presented');
  spec_obj := p_attempt->'spec';
  mode_name := coalesce(spec_obj->>'mode', '');

  if aid is null or n < 0 or n > 4294967295
    or pres_len < 1 or pres_len > 1000
    or pos < 0 or pos >= pres_len
    or coalesce(spec_obj->>'content_tier', '') <> 'lesson-assessment'
    or coalesce(spec_obj->>'format', '') <> 'formal'
    or mode_name not in ('topic', 'general', 'master', 'personalized')
    or (mode_name in ('topic', 'personalized') and pres_len <> 5)
    or (mode_name = 'general' and pres_len < 5)
  then
    raise exception 'Invalid quiz v2 contract or bounds' using errcode = '22023';
  end if;

  for ref in select value from jsonb_array_elements(p_attempt->'presented') loop
    if jsonb_typeof(ref) is distinct from 'object'
      or exists (select 1 from jsonb_object_keys(ref) k where k not in ('item_id', 'content_version', 'option_order'))
    then
      raise exception 'Invalid question reference' using errcode = '22023';
    end if;
    if (seen_ids ? (ref->>'item_id')) then
      raise exception 'Duplicate question in attempt manifest' using errcode = '22023';
    end if;
    seen_ids := seen_ids || jsonb_build_array(ref->>'item_id');

    select * into q from public.quiz_items_v1
      where item_id = ref->>'item_id'
        and content_version = ref->>'content_version'
        and published = true
        and content_version in ('1.0.0', 'lesson-assessment-1.0.0');
    if not found
      or jsonb_typeof(ref->'option_order') is distinct from 'array'
      or jsonb_array_length(ref->'option_order') <> jsonb_array_length(q.option_ids)
      or not ((ref->'option_order') @> q.option_ids and q.option_ids @> (ref->'option_order'))
    then
      raise exception 'Unknown or unapproved quiz item or options' using errcode = '22023';
    end if;

    response := p_attempt->'responses'->>q.item_id;
    if response is not null and (jsonb_typeof(p_attempt->'responses'->q.item_id) <> 'string' or not (q.option_ids ? response)) then
      raise exception 'Unknown answer option' using errcode = '22023';
    end if;
    if response = q.answer then
      score := score + 1;
    end if;
  end loop;

  if exists (select 1 from jsonb_object_keys(p_attempt->'responses') k where not (seen_ids ? k)) then
    raise exception 'Unexpected answers in payload' using errcode = '22023';
  end if;

  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(uid, 0));
  select * into old from public.quiz_attempts_v2 where user_id = uid and attempt_id = aid for update;
  if found then
    if old.assessment_id <> (p_attempt->>'assessment_id')
      or old.content_version <> (p_attempt->>'content_version')
      or old.spec <> spec_obj
      or old.seed <> n
      or old.presented <> (p_attempt->'presented')
    then
      raise exception 'Attempt manifest is immutable';
    end if;
    if old.submitted_at is not null then
      if old.responses <> (p_attempt->'responses') then
        raise exception 'Submitted answers are immutable';
      end if;
      return jsonb_build_object('attempt_id', aid, 'submitted_at', old.submitted_at, 'correct', old.correct, 'earned', 0);
    end if;
  elsif mode_name = 'master' and pres_len > 50 then
    raise exception 'Master quiz permits at most 50 questions per attempt' using errcode = '22023';
  end if;

  completed := case when p_submit then now() else null end;
  insert into public.quiz_attempts_v2 (
    user_id, attempt_id, assessment_id, content_version, spec, title, diagnostic,
    seed, presented, responses, position, submitted_at, correct
  ) values (
    uid, aid, p_attempt->>'assessment_id', p_attempt->>'content_version', spec_obj,
    nullif(p_attempt->>'title', ''),
    coalesce((p_attempt->>'diagnostic')::boolean, false),
    n, p_attempt->'presented', p_attempt->'responses', pos,
    completed, case when p_submit then score else null end
  )
  on conflict (user_id, attempt_id) do update set
    responses = excluded.responses,
    position = excluded.position,
    submitted_at = excluded.submitted_at,
    correct = excluded.correct;

  if p_submit then
    insert into public.quiz_best_scores_v2 (user_id, assessment_id, content_version)
      values (uid, p_attempt->>'assessment_id', p_attempt->>'content_version')
      on conflict do nothing;
    select * into best from public.quiz_best_scores_v2
      where user_id = uid and assessment_id = (p_attempt->>'assessment_id') and content_version = (p_attempt->>'content_version')
      for update;

    earned := greatest(0, 2 * score - best.xp_awarded);
    update public.quiz_best_scores_v2
      set best_score = greatest(best.best_score, score),
          last_score = score,
          attempt_count = best.attempt_count + 1,
          xp_awarded = greatest(best.xp_awarded, 2 * score),
          last_completed_at = completed
      where user_id = uid and assessment_id = (p_attempt->>'assessment_id') and content_version = (p_attempt->>'content_version');

    if earned > 0 then
      insert into public.quiz_xp_events_v2 (user_id, attempt_id, assessment_id, content_version, xp)
        values (uid, aid, p_attempt->>'assessment_id', p_attempt->>'content_version', earned);
      insert into public.player_stats as stats (user_id, display_name, xp, level)
        values (uid, 'Learner', earned, public.lesson_level_for_xp(earned))
        on conflict (user_id) do update
          set xp = stats.xp + earned,
              level = public.lesson_level_for_xp(stats.xp + earned),
              updated_at = now();
    end if;
  end if;

  return jsonb_build_object(
    'attempt_id', aid,
    'submitted_at', completed,
    'correct', case when p_submit then score else null end,
    'earned', earned
  );
end;
$$;
revoke all on function public.save_quiz_v2_attempt(jsonb, boolean) from public, anon, authenticated;
grant execute on function public.save_quiz_v2_attempt(jsonb, boolean) to anon, authenticated;

-- 3. Enable public opt-in leaderboard rankings.
update public.leaderboard_release_v1 set enabled = true;

-- 4. Upgrade Achievements catalog & computation across active Lessons (foundation_progress) and Quiz V2 (quiz_attempts_v2) + legacy V1 records.
update public.achievement_catalog_v1 set position = position + 100;
insert into public.achievement_catalog_v1 (id, title, description, category, icon, position) values
  ('first-lesson', 'First Lesson', 'Complete your first lesson across Syntax Foundations or Grammar.', 'learning', 'sprout', 1),
  ('learning-path', 'Learning Path', 'Complete four different lessons.', 'learning', 'book', 2),
  ('foundations-graduate', 'Foundations Graduate', 'Complete all 11 Syntax Foundations chapters.', 'learning', 'medal', 3),
  ('first-quiz', 'First Assessment', 'Submit your first scored quiz attempt.', 'assessment', 'sprout', 4),
  ('quiz-explorer', 'Quiz Explorer', 'Submit three different scored quizzes.', 'assessment', 'stack', 5),
  ('personal-best', 'Personal Best', 'Improve on an earlier score for the same quiz or lesson closing check.', 'assessment', 'target', 6),
  ('perfect-five', 'Mastery Score', 'Score 100% on any scored quiz.', 'assessment', 'trophy', 7),
  ('master-challenger', 'Master Quiz Finisher', 'Score at least 80% on a Syntax or Grammar Master Quiz.', 'assessment', 'mountain', 8),
  ('gap-spotter', 'Wh-Movement Specialist', 'Complete Wh-Questions (Ch. 9) or score at least 80% on its quiz.', 'syntax', 'tree', 9),
  ('syntax-checkpoint', 'Clause Architect', 'Complete Embedded Clauses (Ch. 8) and score at least 80% on a Chapter 8 or Foundations Master Quiz.', 'syntax', 'bolt', 10),
  ('steady-practice', 'Steady Practice', 'Complete a lesson or submit a scored quiz on three different UTC dates.', 'consistency', 'flame', 11),
  ('framework-distinction', 'Cross-Track Scholar', 'Complete both a Syntax Foundations lesson and a Grammar lesson (or pass a scored quiz in each track).', 'cross-framework', 'gem', 12)
on conflict (id) do update set
  title = excluded.title,
  description = excluded.description,
  category = excluded.category,
  icon = excluded.icon,
  position = excluded.position;

create or replace function public.get_my_achievements() returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
  uid text := nullif(auth.jwt()->>'sub', '');
  snapshot jsonb;
  result jsonb;
begin
  if length(uid) > 255 then
    raise exception 'Invalid account identity' using errcode = '42501';
  end if;

  with raw_lessons as (
    select p.lesson_id, p.completed_at as at
    from public.foundation_progress p
    join public.foundation_active a using (lesson_id, content_version)
    where p.user_id = uid and p.completed_at is not null
    union all
    select lp.lesson_id, lp.completed_at as at
    from public.lesson_progress lp
    where lp.user_id = uid and lp.completed_at is not null
      and not exists (select 1 from public.foundation_active fa where fa.lesson_id = lp.lesson_id)
  ), lessons as (
    select lesson_id, min(at) as at from raw_lessons group by lesson_id
  ), quizzes as (
    select q.assessment_id, q.content_version, q.submitted_at as at, q.correct,
           jsonb_array_length(q.presented) as total,
           coalesce(q.spec->>'mode', '') as mode,
           coalesce(q.spec->>'track', '') as track,
           coalesce(q.spec->>'chapter', '') as chapter
    from public.quiz_attempts_v2 q
    where q.user_id = uid and q.submitted_at is not null
    union all
    select q1.assessment_id, q1.content_version, q1.submitted_at as at, q1.correct,
           5 as total,
           'legacy'::text as mode,
           case when q1.assessment_id like 'quiz-cgel%' then 'cambridge' else 'syntax' end as track,
           regexp_replace(q1.assessment_id, '^quiz-', '') as chapter
    from public.quiz_attempts_v1 q1
    where q1.user_id = uid and q1.submitted_at is not null and q1.correct between 0 and 5
  ), distinct_quizzes as (
    select assessment_id, min(at) as at from quizzes group by assessment_id
  ), first_activities as (
    select min(at) as at from quizzes group by assessment_id, content_version
    union all
    select at from raw_lessons
  ), practice_days as (
    select min(at) as at
    from first_activities
    group by (at at time zone 'UTC')::date
  ), quiz_scores as (
    select assessment_id, content_version, at, correct,
           min(correct) over (
             partition by assessment_id, content_version order by at
             rows between unbounded preceding and 1 preceding
           ) as earlier_low
    from quizzes
  ), lesson_scores as (
    select fa.lesson_id as assessment_id, fa.content_version, fa.submitted_at as at, fa.correct,
           min(fa.correct) over (
             partition by fa.lesson_id, fa.content_version order by fa.submitted_at
             rows between unbounded preceding and 1 preceding
           ) as earlier_low
    from public.foundation_attempts fa
    where fa.user_id = uid and fa.kind = 'closing'
  ), improvements as (
    select assessment_id, content_version, min(at) as at
    from (
      select assessment_id, content_version, at, correct, earlier_low from quiz_scores
      union all
      select assessment_id, content_version, at, correct, earlier_low from lesson_scores
    ) s
    where correct > earlier_low
    group by assessment_id, content_version
  ), criteria_eval as (
    -- Option criteria rows: (achievement_id, option_no, criterion_no, label, target, done, met_at)
    select 'first-lesson'::text as achievement_id, 1 as option_no, 1 as criterion_no,
      'lesson completed'::text as label, 1 as target,
      least(1, (select count(*)::integer from lessons)) as done,
      (select min(at) from lessons) as met_at
    union all
    select 'learning-path', 1, 1, 'different lessons completed', 4,
      least(4, (select count(*)::integer from lessons)),
      (select max(at) from (select at from lessons order by at limit 4) x)
    union all
    select 'foundations-graduate', 1, 1, 'Syntax Foundations chapters completed', 11,
      least(11, (select count(*)::integer from lessons where lesson_id ~ '^br-(0[1-9]|1[01])$')),
      (select max(at) from (select at from lessons where lesson_id ~ '^br-(0[1-9]|1[01])$' order by at limit 11) x)
    union all
    select 'first-quiz', 1, 1, 'scored quiz submitted', 1,
      least(1, (select count(*)::integer from distinct_quizzes)),
      (select min(at) from distinct_quizzes)
    union all
    select 'quiz-explorer', 1, 1, 'different scored quizzes submitted', 3,
      least(3, (select count(*)::integer from distinct_quizzes)),
      (select max(at) from (select at from distinct_quizzes order by at limit 3) x)
    union all
    select 'personal-best', 1, 1, 'score improved on retry', 1,
      least(1, (select count(*)::integer from improvements)),
      (select min(at) from improvements)
    union all
    select 'perfect-five', 1, 1, 'scored quiz at 100%', 1,
      least(1, (select count(*)::integer from quizzes where total > 0 and correct = total)),
      (select min(at) from quizzes where total > 0 and correct = total)
    union all
    select 'master-challenger', 1, 1, 'Master Quiz scored >= 80%', 1,
      least(1, (select count(*)::integer from quizzes where mode = 'master' and total > 0 and correct * 5 >= total * 4)),
      (select min(at) from quizzes where mode = 'master' and total > 0 and correct * 5 >= total * 4)
    union all
    select 'gap-spotter', 1, 1, 'wh-questions lesson completed', 1,
      least(1, (select count(*)::integer from lessons where lesson_id = 'br-09')),
      (select min(at) from lessons where lesson_id = 'br-09')
    union all
    select 'gap-spotter', 2, 1, 'wh-questions quiz scored >= 80%', 1,
      least(1, (select count(*)::integer from quizzes where chapter = 'br-09' and total > 0 and correct * 5 >= total * 4)),
      (select min(at) from quizzes where chapter = 'br-09' and total > 0 and correct * 5 >= total * 4)
    union all
    select 'syntax-checkpoint', 1, 1, 'embedded clauses lesson completed', 1,
      least(1, (select count(*)::integer from lessons where lesson_id = 'br-08')),
      (select min(at) from lessons where lesson_id = 'br-08')
    union all
    select 'syntax-checkpoint', 1, 2, 'Ch. 8 or Syntax Master quiz >= 80%', 1,
      least(1, (select count(*)::integer from quizzes where ((chapter = 'br-08') or (mode = 'master' and track = 'syntax') or assessment_id = 'quiz-advanced') and total > 0 and correct * 5 >= total * 4)),
      (select min(at) from quizzes where ((chapter = 'br-08') or (mode = 'master' and track = 'syntax') or assessment_id = 'quiz-advanced') and total > 0 and correct * 5 >= total * 4)
    union all
    select 'steady-practice', 1, 1, 'distinct UTC practice dates', 3,
      least(3, (select count(*)::integer from practice_days)),
      (select max(at) from (select at from practice_days order by at limit 3) x)
    union all
    select 'framework-distinction', 1, 1, 'Syntax Foundations lesson completed', 1,
      least(1, (select count(*)::integer from lessons where lesson_id like 'br-%')),
      (select min(at) from lessons where lesson_id like 'br-%')
    union all
    select 'framework-distinction', 1, 2, 'Cambridge Grammar lesson completed', 1,
      least(1, (select count(*)::integer from lessons where lesson_id like 'cgel-%')),
      (select min(at) from lessons where lesson_id like 'cgel-%')
    union all
    select 'framework-distinction', 2, 1, 'Syntax scored quiz >= 80%', 1,
      least(1, (select count(*)::integer from quizzes where track = 'syntax' and total > 0 and correct * 5 >= total * 4)),
      (select min(at) from quizzes where track = 'syntax' and total > 0 and correct * 5 >= total * 4)
    union all
    select 'framework-distinction', 2, 2, 'Grammar scored quiz >= 80%', 1,
      least(1, (select count(*)::integer from quizzes where track = 'cambridge' and total > 0 and correct * 5 >= total * 4)),
      (select min(at) from quizzes where track = 'cambridge' and total > 0 and correct * 5 >= total * 4)
  ), options as (
    select achievement_id, option_no,
      case when bool_and(done >= target) then max(met_at) end as met_at,
      jsonb_agg(jsonb_build_object('label', label, 'count', done, 'target', target) order by criterion_no) as criteria
    from criteria_eval
    group by achievement_id, option_no
  ), badges as (
    select achievement_id, min(met_at) as earned_at,
      jsonb_agg(criteria order by option_no) as options
    from options
    group by achievement_id
  )
  select coalesce(jsonb_object_agg(achievement_id, jsonb_build_object(
    'earned_at', earned_at, 'options', options)), '{}') into snapshot from badges;

  if uid is not null then
    insert into public.achievement_unlocks_v1 (user_id, achievement_id, unlocked_at)
    select uid, id, (badge->>'earned_at')::timestamptz
    from jsonb_each(snapshot) as s(id, badge)
    where badge->>'earned_at' is not null
    order by id
    on conflict do nothing;
  end if;

  select coalesce(jsonb_agg(jsonb_build_object(
    'id', c.id, 'title', c.title, 'description', c.description, 'category', c.category,
    'icon', c.icon, 'reward', c.reward, 'definition_version', c.definition_version,
    'visibility', 'visible', 'repeatable', false,
    'options', snapshot->c.id->'options', 'unlocked_at', u.unlocked_at) order by c.position), '[]')
  into result
  from public.achievement_catalog_v1 c
  left join public.achievement_unlocks_v1 u on u.user_id = uid and u.achievement_id = c.id;

  return result;
end;
$$;
revoke all on function public.get_my_achievements() from public, anon, authenticated;
grant execute on function public.get_my_achievements() to anon, authenticated;

commit;
