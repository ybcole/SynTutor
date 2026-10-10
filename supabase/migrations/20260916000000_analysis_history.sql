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

-- Upgrade path for installs that already applied the earlier Supabase-native
-- schema (user_id uuid references auth.users(id), RLS via auth.uid()). Idempotent:
-- the block only rewrites the column when the legacy uuid type is detected, so it
-- is safe to rerun on fresh installs.
-- NOTE: existing rows keep their uuid-as-text user_id, so history recorded under
-- the old Supabase accounts becomes invisible to Clerk users — expected for an
-- auth-provider swap, and not migrated.
do $$
begin
  if exists (
    select 1
    from information_schema.columns
    where table_schema = 'public'
      and table_name = 'analysis_history'
      and column_name = 'user_id'
      and data_type = 'uuid'
  ) then
    alter table public.analysis_history
      drop constraint if exists analysis_history_user_id_fkey,
      alter column user_id type text;
  end if;
end
$$;

-- Index user queries for drawer speed
create index if not exists idx_analysis_history_user_created
  on public.analysis_history(user_id, created_at desc);

-- Enable Row Level Security (RLS)
alter table public.analysis_history enable row level security;

-- Policies: isolate access to the owning user, keyed on the Clerk `sub` claim.
-- Policy subjects are `to public` (not `to authenticated`) on purpose: Clerk's
-- default session token carries no `role` claim, so PostgREST treats such JWTs
-- as the anon role and `to authenticated` would deny every query. Isolation is
-- guaranteed by the sub match itself — anonymous requests have no JWT, so
-- auth.jwt()->>'sub' is null and matches nothing.
drop policy if exists "Users can view own history" on public.analysis_history;
create policy "Users can view own history"
  on public.analysis_history for select
  to public
  using (auth.jwt()->>'sub' = user_id);

drop policy if exists "Users can insert own history" on public.analysis_history;
create policy "Users can insert own history"
  on public.analysis_history for insert
  to public
  with check (auth.jwt()->>'sub' = user_id);

drop policy if exists "Users can delete own history" on public.analysis_history;
create policy "Users can delete own history"
  on public.analysis_history for delete
  to public
  using (auth.jwt()->>'sub' = user_id);