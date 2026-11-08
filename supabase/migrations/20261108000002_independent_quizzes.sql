-- M5, additive. Requires the M4 migrations/level helper. Legacy quizzes and
-- lesson completion are not rewritten. A verified request JWT sub is mandatory.
begin;
create table public.quiz_items_v1 (
 item_id text not null,content_version text not null,pool_id text not null,answer text not null,
 option_ids jsonb not null,published boolean not null default false,primary key(item_id,content_version)
);
create table public.quiz_catalog_v1 (
 assessment_id text not null,content_version text not null,item_version text not null,
 pool_ids jsonb not null,published boolean not null default false,primary key(assessment_id,content_version)
);
create table public.quiz_attempts_v1 (
 user_id text not null,attempt_id uuid not null,assessment_id text not null,content_version text not null,
 seed bigint not null check(seed between 0 and 4294967295),presented jsonb not null,responses jsonb not null,
 position integer not null check(position between 0 and 4),started_at timestamptz not null default now(),
 submitted_at timestamptz,correct integer check(correct between 0 and 5),
 primary key(user_id,attempt_id),foreign key(assessment_id,content_version) references public.quiz_catalog_v1
);
create table public.quiz_best_scores_v1 (
 user_id text not null,assessment_id text not null,content_version text not null,
 best_score integer not null default 0 check(best_score between 0 and 5),last_score integer check(last_score between 0 and 5),
 attempt_count integer not null default 0,xp_awarded integer not null default 0 check(xp_awarded between 0 and 10),last_completed_at timestamptz,
 primary key(user_id,assessment_id,content_version),foreign key(assessment_id,content_version) references public.quiz_catalog_v1
);
create table public.quiz_xp_events_v1 (
 user_id text not null,attempt_id uuid not null,assessment_id text not null,content_version text not null,
 xp integer not null check(xp between 2 and 10 and xp%2=0),created_at timestamptz not null default now(),
 primary key(user_id,attempt_id),foreign key(user_id,attempt_id) references public.quiz_attempts_v1
);
alter table public.quiz_items_v1 enable row level security;
alter table public.quiz_catalog_v1 enable row level security;
alter table public.quiz_attempts_v1 enable row level security;
alter table public.quiz_best_scores_v1 enable row level security;
alter table public.quiz_xp_events_v1 enable row level security;
revoke all on public.quiz_items_v1,public.quiz_catalog_v1,public.quiz_attempts_v1,public.quiz_best_scores_v1,public.quiz_xp_events_v1 from public,anon,authenticated;
grant select on public.quiz_attempts_v1,public.quiz_best_scores_v1,public.quiz_xp_events_v1 to anon,authenticated;
create policy "Own assessment attempts" on public.quiz_attempts_v1 for select to public using((select auth.jwt()->>'sub')=user_id);
create policy "Own assessment best scores" on public.quiz_best_scores_v1 for select to public using((select auth.jwt()->>'sub')=user_id);
create policy "Own assessment awards" on public.quiz_xp_events_v1 for select to public using((select auth.jwt()->>'sub')=user_id);

create function public.save_quiz_attempt(p_attempt jsonb,p_submit boolean default false)
returns jsonb language plpgsql security definer set search_path='' as $$
declare
 uid text:=nullif(auth.jwt()->>'sub',''); aid uuid; catalog public.quiz_catalog_v1%rowtype;
 old public.quiz_attempts_v1%rowtype; best public.quiz_best_scores_v1%rowtype;
 ref jsonb; pool text; expected text; n bigint; variants integer; response text; q public.quiz_items_v1%rowtype;
 score integer:=0; earned integer:=0; completed timestamptz; required_ids jsonb:='[]';
begin
 if uid is null or length(uid)>255 then raise exception 'Sign in to save quiz attempts' using errcode='42501';end if;
 if jsonb_typeof(p_attempt) is distinct from 'object' or octet_length(p_attempt::text)>20000
  or exists(select 1 from jsonb_object_keys(p_attempt) k where k not in ('attempt_id','assessment_id','content_version','seed','presented','responses','position'))
  or jsonb_typeof(p_attempt->'seed') is distinct from 'number' or (p_attempt->>'seed') !~ '^[0-9]{1,10}$'
  or jsonb_typeof(p_attempt->'position') is distinct from 'number' or (p_attempt->>'position') !~ '^[0-4]$'
  or jsonb_typeof(p_attempt->'presented') is distinct from 'array' or jsonb_array_length(p_attempt->'presented')<>5
  or jsonb_typeof(p_attempt->'responses') is distinct from 'object' then raise exception 'Invalid assessment payload' using errcode='22023';end if;
 aid:=(p_attempt->>'attempt_id')::uuid;n:=(p_attempt->>'seed')::bigint;
 if aid is null or n<0 or n>4294967295 then raise exception 'Invalid assessment identity or seed' using errcode='22023';end if;
 select * into catalog from public.quiz_catalog_v1 where assessment_id=p_attempt->>'assessment_id' and content_version=p_attempt->>'content_version' and published;
 if not found or jsonb_array_length(catalog.pool_ids)<>5 then raise exception 'Unknown published assessment version' using errcode='22023';end if;
 -- Reproduce the browser's unsigned 32-bit LCG variant selection. Display order
 -- may be permuted, but there must be one expected variant from each pool.
 for pool in select value from jsonb_array_elements_text(catalog.pool_ids) loop
  n:=(1664525*n+1013904223)%4294967296;
  select count(*) into variants from public.quiz_items_v1 where pool_id=pool and content_version=catalog.item_version and published;
  if variants<2 then raise exception 'Assessment variants unavailable';end if;
  select item_id into expected from public.quiz_items_v1 where pool_id=pool and content_version=catalog.item_version and published order by item_id offset ((n*variants)/4294967296)::integer limit 1;
  if (select count(*) from jsonb_array_elements(p_attempt->'presented') r where r->>'item_id'=expected and r->>'content_version'=catalog.item_version)<>1 then raise exception 'Seed or blueprint manifest mismatch' using errcode='22023';end if;
  required_ids:=required_ids||jsonb_build_array(expected);
 end loop;
 for ref in select value from jsonb_array_elements(p_attempt->'presented') loop
  if jsonb_typeof(ref) is distinct from 'object' or exists(select 1 from jsonb_object_keys(ref) k where k not in ('item_id','content_version','option_order')) then raise exception 'Invalid question reference';end if;
  select * into q from public.quiz_items_v1 where item_id=ref->>'item_id' and content_version=ref->>'content_version' and published;
  if not found or jsonb_typeof(ref->'option_order') is distinct from 'array'
   or jsonb_array_length(ref->'option_order')<>jsonb_array_length(q.option_ids)
   or not ((ref->'option_order') @> q.option_ids and q.option_ids @> (ref->'option_order')) then raise exception 'Invalid options';end if;
  response:=p_attempt->'responses'->>q.item_id;
  if response is not null and (jsonb_typeof(p_attempt->'responses'->q.item_id)<>'string' or not (q.option_ids ? response)) then raise exception 'Unknown answer';end if;
  if response=q.answer then score:=score+1;end if;
 end loop;
 if exists(select 1 from jsonb_object_keys(p_attempt->'responses') k where not (required_ids ? k)) then raise exception 'Unexpected answers';end if;
 -- Same user lock as M4; lesson and quiz awards cannot lose one another's totals.
 perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(uid,0));
 select * into old from public.quiz_attempts_v1 where user_id=uid and attempt_id=aid for update;
 if found then
  if old.assessment_id<>catalog.assessment_id or old.content_version<>catalog.content_version or old.seed<>(p_attempt->>'seed')::bigint or old.presented<>(p_attempt->'presented') then raise exception 'Attempt manifest is immutable';end if;
  if old.submitted_at is not null then
   if old.responses<>(p_attempt->'responses') then raise exception 'Submitted answers are immutable';end if;
   return jsonb_build_object('attempt_id',aid,'submitted_at',old.submitted_at,'correct',old.correct,'earned',0);
  end if;
 end if;
 completed:=case when p_submit then now() else null end;
 insert into public.quiz_attempts_v1 (user_id,attempt_id,assessment_id,content_version,seed,presented,responses,position,submitted_at,correct)
 values(uid,aid,catalog.assessment_id,catalog.content_version,(p_attempt->>'seed')::bigint,p_attempt->'presented',p_attempt->'responses',(p_attempt->>'position')::integer,completed,case when p_submit then score else null end)
 on conflict(user_id,attempt_id) do update set responses=excluded.responses,position=excluded.position,submitted_at=excluded.submitted_at,correct=excluded.correct;
 if p_submit then
  insert into public.quiz_best_scores_v1(user_id,assessment_id,content_version) values(uid,catalog.assessment_id,catalog.content_version) on conflict do nothing;
  select * into best from public.quiz_best_scores_v1 where user_id=uid and assessment_id=catalog.assessment_id and content_version=catalog.content_version for update;
  earned:=greatest(0,2*score-best.xp_awarded);
  update public.quiz_best_scores_v1 set best_score=greatest(best.best_score,score),last_score=score,attempt_count=best.attempt_count+1,
   xp_awarded=greatest(best.xp_awarded,2*score),last_completed_at=completed where user_id=uid and assessment_id=catalog.assessment_id and content_version=catalog.content_version;
  if earned>0 then
   insert into public.quiz_xp_events_v1(user_id,attempt_id,assessment_id,content_version,xp) values(uid,aid,catalog.assessment_id,catalog.content_version,earned);
   insert into public.player_stats as stats(user_id,display_name,xp,level) values(uid,'Learner',earned,public.lesson_level_for_xp(earned))
   on conflict(user_id) do update set xp=stats.xp+earned,level=public.lesson_level_for_xp(stats.xp+earned),updated_at=now();
  end if;
 end if;
 return jsonb_build_object('attempt_id',aid,'submitted_at',completed,'correct',case when p_submit then score else null end,'earned',earned);
end;
$$;
revoke all on function public.save_quiz_attempt(jsonb,boolean) from public,anon,authenticated;
grant execute on function public.save_quiz_attempt(jsonb,boolean) to anon,authenticated;
commit;
