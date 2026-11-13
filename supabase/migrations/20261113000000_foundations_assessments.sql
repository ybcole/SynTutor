-- Phase 2: no active version is changed by applying this migration.
begin;

create table public.foundation_assessments (
  lesson_id text not null check (lesson_id ~ '^br-(0[1-9]|1[01])$'),
  content_version text not null check (content_version ~ '^[0-9]+\.[0-9]+\.[0-9]+$'),
  required_sections text[] not null check (cardinality(required_sections) > 0),
  opening jsonb not null check (jsonb_typeof(opening) = 'object'),
  closing jsonb not null check (jsonb_typeof(closing) = 'object'),
  primary key (lesson_id, content_version)
);
create table public.foundation_active (
  lesson_id text primary key,
  content_version text not null,
  foreign key (lesson_id, content_version) references public.foundation_assessments
);
create table public.foundation_progress (
  user_id text not null,
  lesson_id text not null,
  content_version text not null,
  visited text[] not null default '{}',
  opening_correct integer,
  opening_first_response text,
  last_correct integer,
  last_answers jsonb,
  best_correct integer,
  xp integer not null default 0 check (xp between 0 and 15),
  completed_at timestamptz,
  updated_at timestamptz not null default now(),
  primary key (user_id, lesson_id, content_version),
  foreign key (lesson_id, content_version) references public.foundation_assessments
);
create table public.foundation_attempts (
  user_id text not null,
  lesson_id text not null,
  content_version text not null,
  attempt_id uuid not null,
  kind text not null check (kind in ('opening','closing')),
  responses jsonb not null,
  correct integer not null check (correct >= 0),
  xp integer not null check (xp between 0 and 15 and (kind = 'closing' or xp = 0)),
  submitted_at timestamptz not null default now(),
  primary key (user_id, lesson_id, content_version, attempt_id),
  foreign key (user_id, lesson_id, content_version) references public.foundation_progress
);

alter table public.foundation_assessments enable row level security;
alter table public.foundation_active enable row level security;
alter table public.foundation_progress enable row level security;
alter table public.foundation_attempts enable row level security;
revoke all on public.foundation_assessments, public.foundation_active, public.foundation_progress,
  public.foundation_attempts from public, anon, authenticated;
grant select on public.foundation_progress, public.foundation_attempts to anon, authenticated;
create policy "Own foundations progress" on public.foundation_progress for select
  using ((select auth.jwt()->>'sub') = user_id);
create policy "Own foundations attempts" on public.foundation_attempts for select
  using ((select auth.jwt()->>'sub') = user_id);

-- The ledger needs only this boolean. Catalog contents and answer keys remain private.
create function public.foundation_award_active(p_key text, p_revised boolean)
returns boolean language sql stable security definer set search_path = '' as $$
  select case when p_revised then coalesce(a.content_version = split_part(p_key, ':', 3), false)
    else a.lesson_id is null end
  from (values (split_part(p_key, ':', 2))) as item(lesson_id)
  left join public.foundation_active a using (lesson_id);
$$;
revoke all on function public.foundation_award_active(text,boolean) from public, anon, authenticated;
grant execute on function public.foundation_award_active(text,boolean) to anon, authenticated;

create function public.save_foundation_event(
  p_lesson_id text, p_content_version text, p_event jsonb
) returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  uid text := nullif(auth.jwt()->>'sub', '');
  catalog public.foundation_assessments%rowtype;
  saved public.foundation_progress%rowtype;
  prior public.foundation_attempts%rowtype;
  kind text := p_event->>'kind';
  section_id text := p_event->>'section';
  attempt uuid;
  answers jsonb := p_event->'answers';
  questions jsonb;
  correct integer;
  eligible integer;
  earned integer := 0;
begin
  if uid is null or length(uid) > 255 then
    raise exception 'Sign in to save foundations progress' using errcode = '42501';
  end if;
  if jsonb_typeof(p_event) is distinct from 'object' or octet_length(p_event::text) > 10000
    or kind is null or kind not in ('visit','opening','closing') then
    raise exception 'Invalid foundations event' using errcode = '22023';
  end if;
  perform pg_catalog.pg_advisory_xact_lock_shared(44792011);
  select c.* into catalog from public.foundation_assessments c
    join public.foundation_active a using (lesson_id, content_version)
    where c.lesson_id=p_lesson_id and c.content_version=p_content_version;
  if not found then raise exception 'Unknown or inactive foundations version' using errcode = '22023'; end if;
  if kind = 'visit' then
    if section_id is null or not section_id = any(catalog.required_sections)
      or p_event - 'kind' - 'section' <> '{}'::jsonb then
      raise exception 'Invalid foundations visit' using errcode = '22023';
    end if;
  else
    if p_event - 'kind' - 'attempt_id' - 'answers' <> '{}'::jsonb
      or coalesce(p_event->>'attempt_id','') !~ '^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
      or jsonb_typeof(answers) is distinct from 'object' then
      raise exception 'Invalid foundations submission' using errcode = '22023';
    end if;
    attempt := (p_event->>'attempt_id')::uuid;
    questions := case when kind = 'opening' then catalog.opening else catalog.closing end;
    if (select count(*) from jsonb_object_keys(questions)) < 5
      or exists (select 1 from jsonb_each(questions) q where
        jsonb_typeof(answers->q.key) is distinct from 'string'
        or not ((q.value->'options') ? (answers->>q.key)))
      or exists (select 1 from jsonb_object_keys(answers) id where not questions ? id) then
      raise exception 'Invalid foundations answers' using errcode = '22023';
    end if;
    select count(*) filter (where q.value->>'answer' = answers->>q.key),
           15 * count(*) filter (where q.value->>'answer' = answers->>q.key) / count(*)
      into correct, eligible from jsonb_each(questions) q;
  end if;

  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(uid,0));
  insert into public.foundation_progress (user_id,lesson_id,content_version)
    values (uid,p_lesson_id,p_content_version) on conflict do nothing;
  select * into saved from public.foundation_progress
    where user_id=uid and lesson_id=p_lesson_id and content_version=p_content_version;
  if kind = 'visit' then
    if not section_id = any(saved.visited) then saved.visited := array_append(saved.visited, section_id); end if;
  else
    select * into prior from public.foundation_attempts
      where user_id=uid and lesson_id=p_lesson_id and content_version=p_content_version
        and attempt_id=attempt;
    if found then
      if prior.kind <> kind or prior.responses <> answers then
        raise exception 'Attempt ID already used for different answers' using errcode = '22023';
      end if;
      return to_jsonb(saved) || jsonb_build_object('earned', 0);
    end if;
    if kind = 'closing' then
      earned := greatest(0, eligible - saved.xp);
      saved.xp := saved.xp + earned;
      saved.last_correct := correct;
      saved.last_answers := answers;
      saved.best_correct := greatest(saved.best_correct, correct);
    elsif saved.opening_correct is null then
      saved.opening_correct := correct;
      select answers->>q.key into saved.opening_first_response
        from jsonb_each(questions) q order by (q.value->>'position')::integer limit 1;
    end if;
    insert into public.foundation_attempts (user_id, lesson_id, content_version, attempt_id, kind, responses, correct, xp)
      values (uid,p_lesson_id,p_content_version,attempt,kind,answers,correct,earned);
  end if;
  if saved.last_correct is not null and saved.visited @> catalog.required_sections then
    saved.completed_at := coalesce(saved.completed_at, now());
  end if;
  update public.foundation_progress p
    set visited=saved.visited, opening_correct=saved.opening_correct, opening_first_response=saved.opening_first_response,
        last_correct=saved.last_correct, last_answers=saved.last_answers, best_correct=saved.best_correct, xp=saved.xp,
        completed_at=saved.completed_at, updated_at=now()
    where p.user_id=uid and p.lesson_id=p_lesson_id and p.content_version=p_content_version returning p.* into saved;
  if earned > 0 then
    insert into public.player_stats as stats (user_id,display_name,xp,level)
      values (uid,'Learner',earned,public.lesson_level_for_xp(earned))
      on conflict (user_id) do update set xp=stats.xp+earned,
        level=public.lesson_level_for_xp(stats.xp+earned),updated_at=now();
  end if;
  return to_jsonb(saved) || jsonb_build_object('earned', earned);
end;
$$;
revoke all on function public.save_foundation_event(text,text,jsonb) from public, anon, authenticated;
grant execute on function public.save_foundation_event(text,text,jsonb) to anon, authenticated;

create or replace function public.save_lesson_progress(
  p_lesson_id text, p_content_version text, p_state jsonb
) returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  uid text := nullif(auth.jwt()->>'sub','');
  catalog public.lesson_catalog%rowtype;
  saved public.lesson_progress%rowtype;
  answers jsonb;
  stages jsonb;
  stage_index integer;
  good boolean;
  prereqs boolean;
  earned integer := 0;
  event_key text;
begin
  if uid is null or length(uid) > 255 then raise exception 'Sign in to save account lesson progress' using errcode = '42501'; end if;
  if jsonb_typeof(p_state) is distinct from 'object'
    or jsonb_typeof(p_state->'responses') is distinct from 'object'
    or jsonb_typeof(p_state->'visited') is distinct from 'array'
    or jsonb_typeof(p_state->'stage') is distinct from 'number'
    or (p_state->>'stage') !~ '^[0-5]$'
    or octet_length(p_state::text) > 10000
    or exists (select 1 from jsonb_object_keys(p_state) k where k not in ('responses','visited','stage'))
    then raise exception 'Invalid lesson progress payload' using errcode = '22023'; end if;
  if exists (select 1 from jsonb_object_keys(p_state->'responses') k where k not in ('predict','guided','transfer','exit'))
    or exists (select 1 from jsonb_each(p_state->'responses') v where jsonb_typeof(v.value) <> 'string' or (v.value #>> '{}') not in ('a','b','c'))
    or exists (select 1 from jsonb_array_elements(p_state->'visited') s where jsonb_typeof(s) <> 'string' or (s #>> '{}') not in ('predict','understand','worked','guided','transfer','exit'))
    then raise exception 'Invalid answer or stage' using errcode = '22023'; end if;
  perform pg_catalog.pg_advisory_xact_lock_shared(44792011);
  if not public.foundation_award_active('lesson:' || p_lesson_id || ':' || p_content_version, false) then
    raise exception 'Retired lesson version' using errcode = '22023';
  end if;
  select * into catalog from public.lesson_catalog where lesson_id=p_lesson_id and content_version=p_content_version and published;
  if not found then raise exception 'Unknown or unpublished lesson version' using errcode = '22023'; end if;
  -- Serialize this user's lesson writes and awards. No caller-supplied user/XP.
  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(uid,0));
  insert into public.lesson_progress (user_id,lesson_id,content_version) values (uid,p_lesson_id,p_content_version) on conflict do nothing;
  select * into saved from public.lesson_progress where user_id=uid and lesson_id=p_lesson_id and content_version=p_content_version for update;
  answers := saved.responses || (p_state->'responses');
  -- A stale tab cannot replace an already correct answer with an older failure.
  select answers || coalesce(jsonb_object_agg(k,v),'{}') into answers
    from jsonb_each(saved.responses) e(k,v) where (v #>> '{}') = catalog.answer_key->>k;
  select coalesce(jsonb_agg(distinct v),'[]') into stages from jsonb_array_elements(saved.visited || (p_state->'visited')) a(v);
  stage_index := (p_state->>'stage')::integer; -- Current reading location may move backwards.
  good := stages @> '["predict","understand","worked","guided","transfer","exit"]'::jsonb
    and answers ? 'predict'
    and answers->>'guided' = catalog.answer_key->>'guided'
    and answers->>'transfer' = catalog.answer_key->>'transfer'
    and answers->>'exit' = catalog.answer_key->>'exit';
  select not exists (
    select 1 from jsonb_array_elements(catalog.prerequisites) req
    where not exists (select 1 from public.lesson_progress p where p.user_id=uid
      and p.lesson_id=req->>'lesson_id' and p.content_version=req->>'content_version' and p.completed_at is not null)
    and not exists (select 1 from public.foundation_progress p
      join public.foundation_active a using (lesson_id, content_version)
      where p.user_id=uid and p.lesson_id=req->>'lesson_id' and p.completed_at is not null)
  ) into prereqs;
  if good and prereqs then
    event_key := 'lesson:' || p_lesson_id || ':' || p_content_version;
    insert into public.lesson_xp_events (user_id,activity_key,xp) values (uid,event_key,15) on conflict do nothing;
    if found then
      earned := 15;
      insert into public.player_stats as stats (user_id,display_name,xp,level)
      values (uid,'Learner',15,public.lesson_level_for_xp(15))
      on conflict (user_id) do update set xp=stats.xp+15,level=public.lesson_level_for_xp(stats.xp+15),updated_at=now();
    end if;
    saved.completed_at := coalesce(saved.completed_at,now());
  end if;
  update public.lesson_progress set responses=answers,visited=stages,stage=stage_index,
    completed_at=saved.completed_at,updated_at=now()
    where user_id=uid and lesson_id=p_lesson_id and content_version=p_content_version
    returning * into saved;
  return jsonb_build_object('responses',saved.responses,'visited',saved.visited,'stage',saved.stage,
    'completed_at',saved.completed_at,'earned',earned,'activity_key',event_key);
end;
$$;

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
  and public.foundation_award_active('lesson:' || a.lesson_id || ':' || a.content_version, true);

-- Private operator entry point. A null version restores legacy XP and progress.
-- Ledger and cache cut over atomically. Quiz awards acquire the quiz event lock
-- before writing stats; matching their lock order avoids a cutover deadlock.
create function public.set_foundation_active_version(p_lesson_id text, p_version text)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if p_lesson_id is null or p_lesson_id !~ '^br-(0[1-9]|1[01])$' then
    raise exception 'Only Foundations chapters 1–11 can be switched';
  end if;
  perform pg_catalog.pg_advisory_xact_lock(44792011);
  lock table public.quiz_xp_events_v1, public.player_stats in share row exclusive mode;
  if p_version is null then
    delete from public.foundation_active where lesson_id=p_lesson_id;
  else
    insert into public.foundation_active (lesson_id,content_version) values (p_lesson_id,p_version)
      on conflict (lesson_id) do update set content_version=excluded.content_version;
  end if;
  with totals as (
    select user_id, sum(xp)::integer as xp from public.xp_activity_ledger group by user_id
  ), accounts as (
    select user_id from public.player_stats union select user_id from totals
  )
  insert into public.player_stats (user_id,xp,level)
    select a.user_id, coalesce(t.xp,0), public.lesson_level_for_xp(coalesce(t.xp,0))
    from accounts a left join totals t using (user_id)
  on conflict (user_id) do update set xp=excluded.xp, level=excluded.level, updated_at=now()
    where public.player_stats.xp is distinct from excluded.xp
       or public.player_stats.level is distinct from excluded.level;
end;
$$;
revoke all on function public.set_foundation_active_version(text,text) from public, anon, authenticated;

commit;
