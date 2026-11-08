-- M8: durable account badges from trusted versioned learning records.
begin;

create table public.achievement_catalog_v1 (
  id text primary key,
  title text not null,
  description text not null,
  category text not null check (category in ('learning','assessment','syntax','consistency','cross-framework')),
  icon text not null,
  reward text not null default 'Badge',
  definition_version integer not null default 1 check (definition_version = 1),
  position integer not null unique
);

-- Criteria in the same option must all pass. Any complete option unlocks the badge.
create table public.achievement_criteria_v1 (
  achievement_id text not null references public.achievement_catalog_v1,
  option_no integer not null check (option_no > 0),
  criterion_no integer not null check (criterion_no > 0),
  metric text not null check (metric in ('lessons','quizzes','active_days','improvements')),
  activity_id text,
  content_version text not null,
  minimum_score integer check (minimum_score is null or (minimum_score between 1 and 5 and metric = 'quizzes')),
  target integer not null check (target > 0),
  label text not null,
  primary key (achievement_id, option_no, criterion_no)
);

create table public.achievement_unlocks_v1 (
  user_id text not null,
  achievement_id text not null references public.achievement_catalog_v1,
  unlocked_at timestamptz not null,
  primary key (user_id, achievement_id)
);

alter table public.achievement_catalog_v1 enable row level security;
alter table public.achievement_criteria_v1 enable row level security;
alter table public.achievement_unlocks_v1 enable row level security;
revoke all on public.achievement_catalog_v1, public.achievement_criteria_v1, public.achievement_unlocks_v1
  from public, anon, authenticated;

insert into public.achievement_catalog_v1 (id,title,description,category,icon,position) values
  ('first-lesson','First Lesson','Complete your first lesson.','learning','sprout',1),
  ('learning-path','Learning Path','Complete four different lessons.','learning','book',2),
  ('first-quiz','First Assessment','Submit your first scored assessment. Every score counts.','assessment','sprout',3),
  ('quiz-explorer','Quiz Explorer','Submit three different scored assessments.','assessment','stack',4),
  ('personal-best','Personal Best','Improve on an earlier score for the same assessment version.','assessment','target',5),
  ('perfect-five','Perfect Five','Score five out of five on a scored assessment.','assessment','trophy',6),
  ('gap-spotter','Gap Spotter','Complete the wh-fronting lesson or score at least 4/5 on its quiz.','syntax','tree',7),
  ('syntax-checkpoint','Syntax Checkpoint','Complete the complementisers lesson and score at least 4/5 on the advanced checkpoint.','syntax','medal',8),
  ('steady-practice','Steady Practice','Complete or submit a new learning activity on three different UTC dates. The dates can be nonconsecutive.','consistency','flame',9),
  ('framework-distinction','Framework Distinction','Complete the Cambridge companion lesson and score at least 4/5 on its clauses assessment.','cross-framework','gem',10);

insert into public.achievement_criteria_v1 values
  ('first-lesson',1,1,'lessons',null,'1.0.0',null,1,'lesson completed'),
  ('learning-path',1,1,'lessons',null,'1.0.0',null,4,'different lessons completed'),
  ('first-quiz',1,1,'quizzes',null,'1.0.0',null,1,'scored assessment submitted'),
  ('quiz-explorer',1,1,'quizzes',null,'1.0.0',null,3,'different scored assessments submitted'),
  ('personal-best',1,1,'improvements',null,'1.0.0',null,1,'assessment improved'),
  ('perfect-five',1,1,'quizzes',null,'1.0.0',5,1,'assessment scored 5/5'),
  ('gap-spotter',1,1,'lessons','br-09','1.0.0',null,1,'wh-fronting lesson completed'),
  ('gap-spotter',2,1,'quizzes','quiz-br-09','1.0.0',4,1,'wh-fronting assessment scored at least 4/5'),
  ('syntax-checkpoint',1,1,'lessons','br-08','1.0.0',null,1,'complementisers lesson completed'),
  ('syntax-checkpoint',1,2,'quizzes','quiz-advanced','1.0.0',4,1,'advanced checkpoint scored at least 4/5'),
  ('steady-practice',1,1,'active_days',null,'1.0.0',null,3,'distinct UTC practice dates'),
  ('framework-distinction',1,1,'lessons','cgel-clauses','1.0.0',null,1,'Cambridge companion lesson completed'),
  ('framework-distinction',1,2,'quizzes','quiz-cgel-clauses','1.0.0',4,1,'clauses assessment scored at least 4/5');

-- Opening Achievements reconciles the caller's durable unlocks. Guests can
-- read the catalog. Clients cannot supply identity, evidence, or unlocks.
create function public.get_my_achievements() returns jsonb
language plpgsql security definer set search_path = '' as $$
declare
  uid text := nullif(auth.jwt()->>'sub', '');
  snapshot jsonb;
  result jsonb;
begin
  if length(uid) > 255 then
    raise exception 'Invalid account identity' using errcode = '42501';
  end if;

  with lessons as (
    select lesson_id as activity_id, content_version, completed_at as at
    from public.lesson_progress
    where user_id = uid and completed_at is not null
  ), quizzes as (
    select assessment_id as activity_id, content_version, submitted_at as at, correct
    from public.quiz_attempts_v1
    where user_id = uid and submitted_at is not null and correct between 0 and 5
  ), first_activities as (
    select content_version, min(at) as at
    from quizzes group by activity_id, content_version
    union all
    select content_version, at from lessons
  ), practice_days as (
    select content_version, min(at) as at
    from first_activities
    group by content_version, (at at time zone 'UTC')::date
  ), scored_history as (
    select q.*, min(correct) over (
      partition by activity_id, content_version order by at
      groups between unbounded preceding and 1 preceding
    ) as earlier_low
    from quizzes q
  ), improvements as (
    select activity_id, content_version, min(at) as at
    from scored_history where correct > earlier_low
    group by activity_id, content_version
  ), progress as (
    select c.*, signals.done, signals.met_at
    from public.achievement_criteria_v1 c
    cross join lateral (
      select count(*)::integer as done, max(at) as met_at from (
        select at from (
          select l.at from lessons l
          where c.metric = 'lessons' and l.content_version = c.content_version
            and (c.activity_id is null or c.activity_id = l.activity_id)
          union all
          select min(q.at) from quizzes q
          where c.metric = 'quizzes' and q.content_version = c.content_version
            and (c.activity_id is null or c.activity_id = q.activity_id)
            and q.correct >= coalesce(c.minimum_score, 0)
          group by q.activity_id
          union all
          select i.at from improvements i
          where c.metric = 'improvements' and i.content_version = c.content_version
            and (c.activity_id is null or c.activity_id = i.activity_id)
          union all
          select d.at from practice_days d
          where c.metric = 'active_days' and d.content_version = c.content_version
        ) eligible order by at limit c.target
      ) counted
    ) signals
  ), options as (
    select achievement_id, option_no,
      case when bool_and(done >= target) then max(met_at) end as met_at,
      jsonb_agg(jsonb_build_object('label',label,'count',done,'target',target,'content_version',content_version)
        order by criterion_no) as criteria
    from progress group by achievement_id, option_no
  ), badges as (
    select achievement_id, min(met_at) as earned_at,
      jsonb_agg(criteria order by option_no) as options
    from options group by achievement_id
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
    'id',c.id,'title',c.title,'description',c.description,'category',c.category,
    'icon',c.icon,'reward',c.reward,'definition_version',c.definition_version,
    'visibility','visible','repeatable',false,
    'options',snapshot->c.id->'options','unlocked_at',u.unlocked_at) order by c.position), '[]')
  into result
  from public.achievement_catalog_v1 c
  left join public.achievement_unlocks_v1 u on u.user_id = uid and u.achievement_id = c.id;

  return result;
end;
$$;
revoke all on function public.get_my_achievements() from public, anon, authenticated;
grant execute on function public.get_my_achievements() to anon, authenticated;
commit;
