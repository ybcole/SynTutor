-- M11: preserve legacy progress and constrain the current account API.
begin;

-- Legacy parser-stage counters are historical after M8. The current
-- application does not write them. Retain owner reads and all existing rows.
drop policy if exists "Users can insert own quiz progress" on public.quiz_progress;
drop policy if exists "Users can update own quiz progress" on public.quiz_progress;
revoke all on public.quiz_progress from public, anon, authenticated;
grant select on public.quiz_progress to anon, authenticated;

-- Analysis history has a narrower surface than default Supabase grants.
-- Its existing owner-only Clerk policies still govern all three operations.
revoke all on public.analysis_history from public, anon, authenticated;
grant select, insert, delete on public.analysis_history to anon, authenticated;

commit;
