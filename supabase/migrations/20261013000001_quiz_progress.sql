-- Migration: per-rule quiz completion history for achievements.
-- Clerk authentication (user_id = Clerk `sub`, same as player_stats /
-- analysis_history). Achievements are derived deterministically from these
-- rows by web/js/quiz/achievements.js, so no separate unlock table is needed.

create table if not exists public.quiz_progress (
  user_id text not null,
  rule_id text not null,
  completed_count integer not null default 0 check (completed_count >= 0),
  perfect_count integer not null default 0 check (perfect_count >= 0),
  last_completed_at timestamp with time zone default timezone('utc'::text, now()) not null,
  primary key (user_id, rule_id)
);

-- Achievements only need the user's own rows, but leaderboards may one day
-- surface global numbers, so reads stay public (same trade-off as
-- player_stats: Clerk session tokens carry no `role` claim, so write policies
-- enforce the sub match directly instead of role-based authentication).
alter table public.quiz_progress enable row level security;

drop policy if exists "Quiz progress is public" on public.quiz_progress;
create policy "Quiz progress is public"
  on public.quiz_progress for select
  to public
  using (true);

drop policy if exists "Users can insert own quiz progress" on public.quiz_progress;
create policy "Users can insert own quiz progress"
  on public.quiz_progress for insert
  to public
  with check (auth.jwt()->>'sub' = user_id);

drop policy if exists "Users can update own quiz progress" on public.quiz_progress;
create policy "Users can update own quiz progress"
  on public.quiz_progress for update
  to public
  using (auth.jwt()->>'sub' = user_id)
  with check (auth.jwt()->>'sub' = user_id);