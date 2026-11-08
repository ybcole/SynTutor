"""Verify M9 after the M7 and M8 suites on the same disposable PostgreSQL database."""
from datetime import datetime, timedelta, timezone

from psycopg.errors import InsufficientPrivilege, InvalidParameterValue, ObjectNotInPrerequisiteState, UniqueViolation
from test_progression_database import connect, identity, lesson, quiz, quiz_payload, scalar, rejects, MIGRATIONS


def board(db, period="weekly"):
    return scalar(db, "select public.get_leaderboard(%s)", (period,))


def consent(db, alias=None, opt_in=True):
    db.execute("select public.set_my_leaderboard_preference(%s,%s)", (alias, opt_in))


with connect() as admin, connect() as a, connect() as b, connect() as guest:
    assert scalar(admin, "select current_database()") == "syntutor_progression_test"
    admin.execute((MIGRATIONS / "20261108000006_private_leaderboard.sql").read_text())
    identity(guest, None)
    identity(a, "user_leaderboard_a")
    identity(b, "user_leaderboard_b", "authenticated")
    assert board(guest)["enabled"] is False
    assert board(a)["entries"] == []
    rejects(lambda: consent(a, "TreeAlpha"), ObjectNotInPrerequisiteState)
    rejects(lambda: consent(guest, "GuestTree"), InsufficientPrivilege)
    rejects(lambda: board(guest, "all"), InvalidParameterValue)

    # Disposable test-only release flag. Migration leaves the flag false.
    admin.execute("update public.leaderboard_release_v1 set enabled=true")
    for invalid in (" user_leaderboard_a ", "user_other", "Sess_ABC", "person@example.com", "<b>X</b>", "ab", ""):
        rejects(lambda: consent(a, invalid), InvalidParameterValue)
    assert lesson(a)["earned"] == 15  # pre-consent, always private
    consent(a, "TreeAlpha")
    consent(b, "TreeBeta")
    rejects(lambda: consent(b, "treealpha"), UniqueViolation)
    assert board(guest)["entries"] == []
    assert board(guest)["my_alias"] is None
    assert board(a)["my_alias"] == "TreeAlpha"
    assert board(a)["my_rank"] is None
    for conn in (guest, a, b):
        for sql in ("select * from public.leaderboard_preferences_v1",
                    "update public.leaderboard_preferences_v1 set alias='stolen'",
                    "update public.leaderboard_release_v1 set enabled=true",
                    "update public.player_stats set xp=9999",
                    "insert into public.lesson_xp_events values ('fake','lesson:fake:1.0.0',15,now())"):
            rejects(lambda: conn.execute(sql), InsufficientPrivilege)
    assert quiz(a, quiz_payload(5))["earned"] == 10
    assert quiz(b, quiz_payload(5))["earned"] == 10
    assert quiz(a, quiz_payload(5))["earned"] == 0

    # Place known server events at deterministic boundaries. Do not rely on the
    # execution date or precision of consecutive requests for tie ordering.
    starts = scalar(admin, """select jsonb_build_array(
      date_trunc('week', now() at time zone 'UTC') at time zone 'UTC',
      date_trunc('quarter', now() at time zone 'UTC') at time zone 'UTC')""")
    week, quarter = (datetime.fromisoformat(item).astimezone(timezone.utc) for item in starts)
    assert week.weekday() == 0 and week.hour == 0
    assert quarter.month in (1, 4, 7, 10) and quarter.day == 1
    cutoff = max(week, quarter)
    consent_at = cutoff - timedelta(seconds=5)
    admin.execute("update public.leaderboard_preferences_v1 set opted_in_at=%s", (consent_at,))
    admin.execute("""update public.lesson_xp_events set created_at=%s where user_id='user_leaderboard_a'""",
                  (consent_at - timedelta(seconds=1),))
    admin.execute("""update public.quiz_xp_events_v1 set created_at=%s where user_id='user_leaderboard_b'""", (cutoff,))
    admin.execute("""update public.quiz_xp_events_v1 set created_at=%s where user_id='user_leaderboard_a'""",
                  (cutoff + timedelta(milliseconds=1),))
    if scalar(admin, "select now() > %s", (cutoff + timedelta(milliseconds=1),)) is False:
        admin.execute("select pg_sleep(0.01)")
    for period in ("weekly", "seasonal"):
        observed = board(guest, period)
        assert observed["entries"] == [
            {"alias": "TreeBeta", "xp": 10, "rank": 1},
            {"alias": "TreeAlpha", "xp": 10, "rank": 2},
        ]
        assert observed["my_rank"] is None and observed["my_alias"] is None
        assert board(a, period)["my_rank"] == 2
    assert datetime.fromisoformat(board(guest)["period_end"]) - week == timedelta(days=7)
    admin.execute("update public.quiz_xp_events_v1 set created_at=%s where user_id like 'user_leaderboard_%%'", (cutoff,))
    assert [row["alias"] for row in board(guest)["entries"]] == ["TreeAlpha", "TreeBeta"]
    if week > quarter:
        admin.execute("update public.leaderboard_preferences_v1 set opted_in_at=%s", (quarter,))
        admin.execute("update public.quiz_xp_events_v1 set created_at=%s where user_id='user_leaderboard_a'", (quarter,))
        assert [row["alias"] for row in board(guest)["entries"]] == ["TreeBeta"]
        assert len(board(guest, "seasonal")["entries"]) == 2

    consent(a, "TreeGamma")
    assert board(a)["my_alias"] == "TreeGamma"
    consent(a, opt_in=False)
    assert [row["alias"] for row in board(guest)["entries"]] == ["TreeBeta"]
    assert scalar(a, "select public.get_my_progression()")["xp"] == 25
    assert scalar(a, "select count(*) from jsonb_array_elements(public.get_my_achievements()) a "
                     "where a->>'unlocked_at' is not null") > 0
    consent(a, "TreeGamma")
    assert board(a)["my_rank"] is None
    # A participant outside the public top 100 still sees their own rank.
    admin.execute("""
      insert into public.leaderboard_preferences_v1 (user_id, alias, opted_in_at)
      select 'rank-fixture-' || i, 'RankFixture' || i, %s
      from generate_series(1, 101) i
    """, (consent_at,))
    admin.execute("""
      insert into public.lesson_xp_events (user_id, activity_key, xp, created_at)
      select 'rank-fixture-' || i, 'lesson:br-01:1.0.0', 15, %s
      from generate_series(1, 101) i
    """, (cutoff,))
    assert len(board(guest)["entries"]) == 100
    assert board(b)["my_rank"] == 102
    admin.execute("update public.leaderboard_release_v1 set enabled=false")
    assert board(guest)["entries"] == [] and board(b)["my_rank"] is None
    consent(b, opt_in=False)
    assert board(b)["opted_in"] is False

print("PASS: default pause, opt-in/out, no retroactive XP, alias privacy, scoped ranks, UTC boundaries, tie ordering, and write denial.")
