-- Private, explicitly UNVERIFIED practice manifests. Never read by XP/leaderboard RPCs.
create table public.quiz_practice_v2 (
  user_id text not null check (length(user_id) between 1 and 255),
  attempt_id uuid not null,
  payload jsonb not null,
  primary key (user_id, attempt_id),
  check (jsonb_typeof(payload) = 'object'),
  check ((payload->>'quiz_v2') is not distinct from 'true'),
  check ((payload->>'practice') is not distinct from 'true'),
  check ((payload->>'xp_policy') is not distinct from 'unscored-v2'),
  check ((payload->>'content_version') is not distinct from '2.0.0'),
  check ((payload->>'attempt_id') is not distinct from attempt_id::text),
  check (jsonb_typeof(payload->'presented') is not distinct from 'array'),
  check (jsonb_array_length(payload->'presented') between 1 and 1000),
  check (octet_length(payload::text) <= 500000)
);
alter table public.quiz_practice_v2 enable row level security;
create policy quiz_practice_v2_owner on public.quiz_practice_v2
  for all to anon, authenticated using (user_id = (select auth.jwt()->>'sub')) with check (user_id = (select auth.jwt()->>'sub'));
revoke all on public.quiz_practice_v2 from public, anon, authenticated;
grant select, insert, update on public.quiz_practice_v2 to anon, authenticated;
comment on table public.quiz_practice_v2 is
  'Unverified practice only: client manifests/responses are not proof of score, completion, or XP.';

create function public.freeze_quiz_practice_v2() returns trigger
language plpgsql set search_path = '' as $$
begin
  if (old.payload->'presented', old.payload->'seed', old.payload->'spec', old.payload->'started_at')
     is distinct from
     (new.payload->'presented', new.payload->'seed', new.payload->'spec', new.payload->'started_at')
     or (old.payload->>'submitted_at' is not null and old.payload is distinct from new.payload)
  then raise exception 'Practice manifest and completed attempts are immutable' using errcode = '22023';
  end if;
  return new;
end;
$$;
create trigger freeze_quiz_practice_v2 before update on public.quiz_practice_v2
  for each row execute function public.freeze_quiz_practice_v2();
