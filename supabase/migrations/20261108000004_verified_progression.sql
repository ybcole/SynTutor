-- M7: apply after the versioned lesson and quiz catalogs, before the M7 frontend.
begin;

-- Drain existing award transactions before taking the historical snapshot.
-- The two award RPCs lock progress first, then write their event and stats row.
lock table public.lesson_xp_events, public.quiz_xp_events_v1, public.player_stats
  in access exclusive mode;

-- Preserve pre-cutover values for an administrative audit. The previous
-- balance could be directly edited by the client, so it cannot establish XP.
create table public.legacy_player_stats_m7 as select * from public.player_stats;
alter table public.legacy_player_stats_m7 enable row level security;
revoke all on public.legacy_player_stats_m7 from public, anon, authenticated;

drop policy "Leaderboard is public" on public.player_stats;
drop policy "Users can insert own stats" on public.player_stats;
drop policy "Users can update own stats" on public.player_stats;
revoke all on public.player_stats from public, anon, authenticated;
grant select on public.player_stats to anon, authenticated;
create policy "Own player stats only" on public.player_stats for select to public
  using ((select auth.jwt()->>'sub') = user_id);

-- Preserve private legacy achievement history. M9 can supply a separate
-- opt-in ranking projection after the privacy review.
drop policy "Quiz progress is public" on public.quiz_progress;
create policy "Own legacy quiz progress only" on public.quiz_progress for select to public
  using ((select auth.jwt()->>'sub') = user_id);

-- Read-only unified ledger over the already protected M4/M5 event stores.
-- Event keys are unique per account. Quiz attempt deltas also share a
-- per-assessment/version ceiling, enforced by the existing award RPC.
create view public.xp_activity_ledger with (security_invoker = true) as
select e.user_id, 'lesson'::text as activity_type, p.lesson_id as activity_id,
       p.content_version, e.activity_key as event_key, e.xp, e.created_at,
       jsonb_build_object('completed_at', p.completed_at) as evidence
from public.lesson_xp_events e
left join public.lesson_progress p on p.user_id = e.user_id
  and e.activity_key = 'lesson:' || p.lesson_id || ':' || p.content_version
union all
select e.user_id, 'quiz', e.assessment_id, e.content_version,
       'quiz:' || e.assessment_id || ':' || e.content_version || ':' || e.attempt_id,
       e.xp, e.created_at,
       jsonb_build_object('attempt_id', e.attempt_id, 'correct', a.correct, 'submitted_at', a.submitted_at)
from public.quiz_xp_events_v1 e
join public.quiz_attempts_v1 a on a.user_id = e.user_id and a.attempt_id = e.attempt_id;

revoke all on public.xp_activity_ledger from public, anon, authenticated;
grant select on public.xp_activity_ledger to anon, authenticated;

-- Both trusted award functions already call this helper for their private
-- compatibility cache. Level L begins at 10*L*L + 90*L cumulative XP.
create or replace function public.lesson_level_for_xp(p_xp integer) returns integer
language sql immutable strict set search_path = '' as $$
  select floor((sqrt(8100::numeric + 40::numeric * greatest(0, p_xp)) - 90) / 20)::integer;
$$;

-- Reconcile the compatibility cache, including accounts with only legacy XP.
with totals as (
  select user_id, sum(xp)::integer as xp from public.xp_activity_ledger group by user_id
), accounts as (
  select user_id from public.player_stats union select user_id from totals
)
insert into public.player_stats (user_id, xp, level)
select a.user_id, coalesce(t.xp, 0), public.lesson_level_for_xp(coalesce(t.xp, 0))
from accounts a left join totals t using (user_id)
on conflict (user_id) do update set xp = excluded.xp, level = excluded.level;

create function public.get_my_progression() returns jsonb
language plpgsql stable security definer set search_path = '' as $$
declare
  uid text := nullif(auth.jwt()->>'sub', '');
  lesson_xp integer;
  quiz_xp integer;
  total integer;
begin
  if uid is null or length(uid) > 255 then
    raise exception 'Sign in to view account progression' using errcode = '42501';
  end if;
  select coalesce(sum(xp) filter (where activity_type = 'lesson'), 0),
         coalesce(sum(xp) filter (where activity_type = 'quiz'), 0)
    into lesson_xp, quiz_xp from public.xp_activity_ledger where user_id = uid;
  total := lesson_xp + quiz_xp;
  return jsonb_build_object('xp', total, 'lesson_xp', lesson_xp, 'quiz_xp', quiz_xp,
    'level', public.lesson_level_for_xp(total));
end;
$$;
revoke all on function public.get_my_progression() from public, anon, authenticated;
grant execute on function public.get_my_progression() to anon, authenticated;

commit;
