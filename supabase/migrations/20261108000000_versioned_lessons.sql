-- M4: isolated versioned lesson progress and one lesson award per version.
-- No existing quiz/history/progress row is rewritten. Apply catalog seed after this.
begin;
create table if not exists public.lesson_catalog (
  lesson_id text not null,
  content_version text not null,
  prerequisites jsonb not null default '[]',
  answer_key jsonb not null,
  published boolean not null default false,
  primary key (lesson_id, content_version)
);
create table if not exists public.lesson_progress (
  user_id text not null,
  lesson_id text not null,
  content_version text not null,
  responses jsonb not null default '{}',
  visited jsonb not null default '[]',
  stage integer not null default 0 check (stage between 0 and 5),
  completed_at timestamptz,
  updated_at timestamptz not null default now(),
  primary key (user_id, lesson_id, content_version),
  foreign key (lesson_id, content_version) references public.lesson_catalog
);
create table if not exists public.lesson_xp_events (
  user_id text not null,
  activity_key text not null,
  xp integer not null check (xp = 15),
  created_at timestamptz not null default now(),
  primary key (user_id, activity_key)
);
alter table public.lesson_catalog enable row level security;
alter table public.lesson_progress enable row level security;
alter table public.lesson_xp_events enable row level security;
revoke all on public.lesson_catalog, public.lesson_progress, public.lesson_xp_events from public, anon, authenticated;
grant select on public.lesson_progress, public.lesson_xp_events to anon, authenticated;
create policy "Own lesson progress only" on public.lesson_progress for select to public
  using ((select auth.jwt()->>'sub') = user_id);
create policy "Own lesson XP events only" on public.lesson_xp_events for select to public
  using ((select auth.jwt()->>'sub') = user_id);

-- Preserve the existing level curve until M7 changes progression globally.
create or replace function public.lesson_level_for_xp(p_xp integer) returns integer
language plpgsql immutable set search_path = '' as $$
declare l integer := 0; floor_xp numeric := 0; span numeric := 50;
begin
  while p_xp >= floor_xp + span loop
    floor_xp := floor_xp + span;
    l := l + 1;
    span := round(50 * power(1.6::numeric, l));
  end loop;
  return l;
end;
$$;
revoke all on function public.lesson_level_for_xp(integer) from public, anon, authenticated;

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
revoke all on function public.save_lesson_progress(text,text,jsonb) from public, anon, authenticated;
-- Existing Clerk integration can use either API role; a verified JWT sub is
-- still mandatory inside the function. A genuine anonymous request is denied.
grant execute on function public.save_lesson_progress(text,text,jsonb) to anon, authenticated;
commit;
