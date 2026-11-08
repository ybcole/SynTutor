-- M9: disabled until the database owner completes the release/privacy gate.
begin;
create table public.leaderboard_release_v1 (
  singleton boolean primary key default true check (singleton),
  enabled boolean not null default false
);
insert into public.leaderboard_release_v1 default values;

create table public.leaderboard_preferences_v1 (
  user_id text primary key,
  alias text not null check (alias collate "C" ~ '^[A-Za-z][A-Za-z0-9_-]{2,23}$'
    and lower(alias collate "C") !~ '^(user|sess|org|client|clerk)[_-]'),
  opted_in_at timestamptz
);
create unique index leaderboard_active_alias_v1
  on public.leaderboard_preferences_v1 (lower(alias collate "C"))
  where opted_in_at is not null;

alter table public.leaderboard_release_v1 enable row level security;
alter table public.leaderboard_preferences_v1 enable row level security;
revoke all on public.leaderboard_release_v1, public.leaderboard_preferences_v1 from public, anon, authenticated;

create function public.set_my_leaderboard_preference(p_alias text, p_opt_in boolean)
returns void language plpgsql security definer set search_path = '' as $$
declare
  uid text := nullif(auth.jwt()->>'sub', '');
  chosen text := btrim(p_alias);
begin
  if uid is null or length(uid) > 255 then
    raise exception 'Sign in to change leaderboard participation' using errcode = '42501';
  end if;
  if p_opt_in is false then
    update public.leaderboard_preferences_v1 set opted_in_at = null where user_id = uid;
    return;
  end if;
  if p_opt_in is null or chosen is null or chosen collate "C" !~ '^[A-Za-z][A-Za-z0-9_-]{2,23}$'
    or lower(chosen collate "C") ~ '^(user|sess|org|client|clerk)[_-]'
    or lower(chosen collate "C") = lower(uid collate "C") then
    raise exception 'Choose a 3–24 character alias starting with a letter' using errcode = '22023';
  end if;
  if (select enabled from public.leaderboard_release_v1 where singleton for share) is distinct from true then
    raise exception 'Public rankings are paused' using errcode = '55000';
  end if;
  insert into public.leaderboard_preferences_v1 as p (user_id,alias,opted_in_at)
  values (uid,chosen,clock_timestamp())
  on conflict (user_id) do update set alias=excluded.alias,
    opted_in_at=coalesce(p.opted_in_at,clock_timestamp());
exception when unique_violation then
  raise exception 'That alias is already in use' using errcode = '23505';
end;
$$;

create function public.get_leaderboard(p_period text)
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
    with scores as (
      select p.user_id, p.alias, sum(e.xp) as xp, max(e.created_at) as latest
      from public.leaderboard_preferences_v1 p
      join public.xp_activity_ledger e on e.user_id = p.user_id
      where p.opted_in_at is not null and e.created_at >= greatest(period_start,p.opted_in_at)
        and e.created_at < least(period_end,as_of)
      group by p.user_id,p.alias
    ), ranked as (
      select *, row_number() over (order by xp desc, latest, lower(alias collate "C")) as rank
      from scores
    )
    select coalesce(jsonb_agg(jsonb_build_object('alias',alias,'xp',xp,'rank',rank)
      order by rank) filter (where rank <= 100),'[]'),
      max(rank) filter (where user_id = uid)
    into board, own_rank from ranked;
  end if;
  return jsonb_build_object('enabled',coalesce(released,false),'period_start',period_start,
    'period_end',period_end,'entries',board,'my_rank',own_rank,
    'my_alias',own.alias,'opted_in',own.opted_in_at is not null);
end;
$$;
revoke all on function public.get_leaderboard(text), public.set_my_leaderboard_preference(text,boolean)
  from public, anon, authenticated;
grant execute on function public.get_leaderboard(text), public.set_my_leaderboard_preference(text,boolean)
  to anon, authenticated;
commit;
