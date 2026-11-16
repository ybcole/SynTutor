-- Verified Quiz V2 attempts, server-authoritative scoring, best-score XP deltas,
-- and ledger integration for project-approved SynTutor Quiz V2 assessments.
begin;

create table public.quiz_attempts_v2 (
  user_id text not null,
  attempt_id uuid not null,
  assessment_id text not null check (assessment_id ~ '^quiz-v2:.+:lesson-assessment:formal-1$'),
  content_version text not null check (content_version = '2.0.0'),
  spec jsonb not null,
  title text,
  diagnostic boolean not null default false,
  seed bigint not null check (seed between 0 and 4294967295),
  presented jsonb not null check (jsonb_typeof(presented) = 'array' and jsonb_array_length(presented) between 1 and 1000),
  responses jsonb not null check (jsonb_typeof(responses) = 'object'),
  position integer not null check (position >= 0 and position < jsonb_array_length(presented)),
  started_at timestamptz not null default now(),
  submitted_at timestamptz,
  correct integer check (correct >= 0 and correct <= jsonb_array_length(presented)),
  primary key (user_id, attempt_id)
);

create table public.quiz_best_scores_v2 (
  user_id text not null,
  assessment_id text not null,
  content_version text not null,
  best_score integer not null default 0 check (best_score >= 0),
  last_score integer check (last_score >= 0),
  attempt_count integer not null default 0,
  xp_awarded integer not null default 0 check (xp_awarded >= 0 and xp_awarded % 2 = 0),
  last_completed_at timestamptz,
  primary key (user_id, assessment_id, content_version)
);

create table public.quiz_xp_events_v2 (
  user_id text not null,
  attempt_id uuid not null,
  assessment_id text not null,
  content_version text not null,
  xp integer not null check (xp >= 2 and xp % 2 = 0),
  created_at timestamptz not null default now(),
  primary key (user_id, attempt_id),
  foreign key (user_id, attempt_id) references public.quiz_attempts_v2
);

alter table public.quiz_attempts_v2 enable row level security;
alter table public.quiz_best_scores_v2 enable row level security;
alter table public.quiz_xp_events_v2 enable row level security;

revoke all on public.quiz_attempts_v2, public.quiz_best_scores_v2, public.quiz_xp_events_v2 from public, anon, authenticated;
grant select on public.quiz_attempts_v2, public.quiz_best_scores_v2, public.quiz_xp_events_v2 to anon, authenticated;

create policy "Own quiz v2 attempts" on public.quiz_attempts_v2
  for select to public using ((select auth.jwt()->>'sub') = user_id);
create policy "Own quiz v2 best scores" on public.quiz_best_scores_v2
  for select to public using ((select auth.jwt()->>'sub') = user_id);
create policy "Own quiz v2 awards" on public.quiz_xp_events_v2
  for select to public using ((select auth.jwt()->>'sub') = user_id);

create function public.save_quiz_v2_attempt(p_attempt jsonb, p_submit boolean default false)
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

create or replace view public.xp_activity_ledger with (security_invoker = true) as
select e.user_id, 'lesson'::text as activity_type, p.lesson_id as activity_id,
       p.content_version, e.activity_key as event_key, e.xp, e.created_at,
       jsonb_build_object('completed_at', p.completed_at) as evidence
from public.lesson_xp_events e
left join public.lesson_progress p on p.user_id = e.user_id
  and e.activity_key = 'lesson:' || p.lesson_id || ':' || p.content_version
where public.foundation_award_active(e.activity_key, false)
union all
select e.user_id, 'quiz', e.assessment_id, e.content_version,
       'quiz:' || e.assessment_id || ':' || e.content_version || ':' || e.attempt_id,
       e.xp, e.created_at,
       jsonb_build_object('attempt_id', e.attempt_id, 'correct', a.correct, 'submitted_at', a.submitted_at)
from public.quiz_xp_events_v1 e
join public.quiz_attempts_v1 a on a.user_id = e.user_id and a.attempt_id = e.attempt_id
union all
select a.user_id, 'lesson', a.lesson_id, a.content_version,
       'foundation:' || a.lesson_id || ':' || a.content_version || ':' || a.attempt_id,
       a.xp, a.submitted_at,
       jsonb_build_object('attempt_id', a.attempt_id, 'correct', a.correct, 'submitted_at', a.submitted_at)
from public.foundation_attempts a
where a.kind = 'closing' and a.xp > 0
  and public.foundation_award_active('lesson:' || a.lesson_id || ':' || a.content_version, true)
union all
select e.user_id, 'quiz', e.assessment_id, e.content_version,
       'quiz-v2:' || e.assessment_id || ':' || e.content_version || ':' || e.attempt_id,
       e.xp, e.created_at,
       jsonb_build_object('attempt_id', e.attempt_id, 'correct', a.correct, 'submitted_at', a.submitted_at)
from public.quiz_xp_events_v2 e
join public.quiz_attempts_v2 a on a.user_id = e.user_id and a.attempt_id = e.attempt_id;

commit;
