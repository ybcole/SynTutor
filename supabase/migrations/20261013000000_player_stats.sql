-- Migration: permanent gamification stats (XP + level) and world-readable
-- leaderboard.
-- Authentication is provided by Clerk as a third-party provider, so user_id
-- stores the Clerk user identifier (e.g. "user_2a1B..."), the same string used
-- by analysis_history. XP/level derive from the exponential curve in
-- web/js/quiz/level.js (50, 80, 128, 205, ... XP per level lane).

create table if not exists public.player_stats (
  user_id text primary key,
  display_name text not null default 'Learner',
  xp integer not null default 0 check (xp >= 0),
  level integer not null default 0 check (level >= 0),
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Rank queries: level desc, then XP desc as the tie-break.
create index if not exists idx_player_stats_rank
  on public.player_stats(level desc, xp desc);

alter table public.player_stats enable row level security;

-- The leaderboard is read by every learner (public), but each row is only
-- written by the user whose Clerk `sub` claim matches its user_id. The policy
-- subjects are `to public` on purpose: Clerk's default session token carries no
-- `role` claim, so PostgREST sees it as the anon role and `to authenticated`
-- would deny every query. Isolation is guaranteed by the sub match itself.

drop policy if exists "Leaderboard is public" on public.player_stats;
create policy "Leaderboard is public"
  on public.player_stats for select
  to public
  using (true);

drop policy if exists "Users can insert own stats" on public.player_stats;
create policy "Users can insert own stats"
  on public.player_stats for insert
  to public
  with check (auth.jwt()->>'sub' = user_id);

drop policy if exists "Users can update own stats" on public.player_stats;
create policy "Users can update own stats"
  on public.player_stats for update
  to public
  using (auth.jwt()->>'sub' = user_id)
  with check (auth.jwt()->>'sub' = user_id);