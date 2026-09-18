-- Migration: Create analysis_history table with Row Level Security (RLS).
-- Authentication is provided by Clerk as a third-party provider: Supabase
-- verifies Clerk-issued session tokens (native third-party auth). user_id thus
-- stores the Clerk user identifier (a string such as "user_2a1B..."), not a
-- Supabase auth UUID, so RLS keys off the Clerk `sub` claim via auth.jwt().

create table if not exists public.analysis_history (
  id uuid default gen_random_uuid() primary key,
  user_id text not null,
  sentence text not null,
  is_valid boolean not null,
  constraints_fired text[] default '{}',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Index user queries for drawer speed
create index if not exists idx_analysis_history_user_created
  on public.analysis_history(user_id, created_at desc);

-- Enable Row Level Security (RLS)
alter table public.analysis_history enable row level security;

-- Policies: Strictly isolate access to authenticated record owner
drop policy if exists "Users can view own history" on public.analysis_history;
create policy "Users can view own history"
  on public.analysis_history for select
  to authenticated
  using (auth.jwt()->>'sub' = user_id);

drop policy if exists "Users can insert own history" on public.analysis_history;
create policy "Users can insert own history"
  on public.analysis_history for insert
  to authenticated
  with check (auth.jwt()->>'sub' = user_id);

drop policy if exists "Users can delete own history" on public.analysis_history;
create policy "Users can delete own history"
  on public.analysis_history for delete
  to authenticated
  using (auth.jwt()->>'sub' = user_id);