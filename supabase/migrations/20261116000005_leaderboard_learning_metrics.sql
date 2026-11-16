-- Additive Leaderboard upgrade after 20261116000004_quiz_v2_contract_hardening:
-- Adds verified period completion metrics (lessons_completed, quizzes_completed)
-- to public.get_leaderboard(p_period) while preserving verified XP ranking,
-- opt-in/non-retroactive privacy rules, RLS isolation, and deterministic tie-breaking.
begin;

create or replace function public.get_leaderboard(p_period text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare
  uid text := nullif(auth.jwt()->>'sub', '');
  released boolean;
  period_start timestamptz;
  period_end timestamptz;
  as_of timestamptz := statement_timestamp();
  own public.leaderboard_preferences_v1%rowtype;
  board jsonb := '[]';
  own_rank bigint;
begin
  case p_period
    when 'weekly' then
      period_start := date_trunc('week', as_of at time zone 'UTC') at time zone 'UTC';
      period_end := period_start + interval '168 hours';
    when 'seasonal' then
      period_start := date_trunc('quarter', as_of at time zone 'UTC') at time zone 'UTC';
      period_end := ((period_start at time zone 'UTC') + interval '3 months') at time zone 'UTC';
    else raise exception 'Unknown leaderboard period' using errcode = '22023';
  end case;
  select enabled into released from public.leaderboard_release_v1 where singleton;
  select * into own from public.leaderboard_preferences_v1 where user_id = uid;

  if released then
    with participants as (
      select user_id, alias,
        greatest(period_start, opted_in_at) as since_at,
        least(period_end, as_of) as until_at
      from public.leaderboard_preferences_v1
      where opted_in_at is not null
    ), scores as (
      select p.user_id, p.alias,
        sum(e.xp)::integer as xp,
        max(e.created_at) as latest
      from participants p
      join public.xp_activity_ledger e on e.user_id = p.user_id
      where e.created_at >= p.since_at and e.created_at < p.until_at
      group by p.user_id, p.alias
    ), period_lessons as (
      select user_id, count(distinct lesson_id)::integer as lessons_completed
      from (
        select p.user_id, fp.lesson_id
        from participants p
        join public.foundation_progress fp on fp.user_id = p.user_id
        join public.foundation_active fa on fa.lesson_id = fp.lesson_id and fa.content_version = fp.content_version
        where fp.completed_at is not null and fp.completed_at >= p.since_at and fp.completed_at < p.until_at
        union all
        select p.user_id, lp.lesson_id
        from participants p
        join public.lesson_progress lp on lp.user_id = p.user_id
        where lp.completed_at is not null and lp.completed_at >= p.since_at and lp.completed_at < p.until_at
          and not exists (select 1 from public.foundation_active fa where fa.lesson_id = lp.lesson_id)
      ) l
      group by user_id
    ), period_quizzes as (
      select user_id, count(distinct assessment_id)::integer as quizzes_completed
      from (
        select p.user_id, q2.assessment_id
        from participants p
        join public.quiz_attempts_v2 q2 on q2.user_id = p.user_id
        where q2.submitted_at is not null and q2.submitted_at >= p.since_at and q2.submitted_at < p.until_at
        union all
        select p.user_id, q1.assessment_id
        from participants p
        join public.quiz_attempts_v1 q1 on q1.user_id = p.user_id
        where q1.submitted_at is not null and q1.correct between 0 and 5
          and q1.submitted_at >= p.since_at and q1.submitted_at < p.until_at
      ) q
      group by user_id
    ), ranked as (
      select s.user_id, s.alias, s.xp,
        coalesce(pl.lessons_completed, 0) as lessons_completed,
        coalesce(pq.quizzes_completed, 0) as quizzes_completed,
        row_number() over (order by s.xp desc, s.latest, lower(s.alias collate "C")) as rank
      from scores s
      left join period_lessons pl on pl.user_id = s.user_id
      left join period_quizzes pq on pq.user_id = s.user_id
    )
    select coalesce(jsonb_agg(jsonb_build_object(
        'alias', alias,
        'xp', xp,
        'rank', rank,
        'lessons_completed', lessons_completed,
        'quizzes_completed', quizzes_completed
      ) order by rank) filter (where rank <= 100), '[]'),
      max(rank) filter (where user_id = uid)
    into board, own_rank from ranked;
  end if;
  return jsonb_build_object('enabled', coalesce(released, false), 'period_start', period_start,
    'period_end', period_end, 'entries', board, 'my_rank', own_rank,
    'my_alias', own.alias, 'opted_in', own.opted_in_at is not null);
end;
$$;

revoke all on function public.get_leaderboard(text) from public, anon, authenticated;
grant execute on function public.get_leaderboard(text) to anon, authenticated;

commit;
