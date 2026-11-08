"""Verify M8 after test_progression_database.py on the same disposable database."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from uuid import uuid4

from test_progression_database import (
    connect, identity, lesson, quiz, quiz_payload, scalar, rejects, MIGRATIONS,
)
from psycopg.errors import InsufficientPrivilege, UndefinedFunction


def badges(db):
    return {badge["id"]: badge for badge in scalar(db, "select public.get_my_achievements()")}


def unlocked(items):
    return {ident for ident, item in items.items() if item["unlocked_at"]}


def stamp(day):
    return datetime(2026, 11, day, tzinfo=timezone.utc)


def record_lesson(db, user, ident, day, version="1.0.0"):
    db.execute("""
      insert into public.lesson_progress (user_id,lesson_id,content_version,completed_at)
      values (%s,%s,%s,%s)
    """, (user, ident, version, stamp(day) if day else None))


def record_quiz(db, user, ident, score, day, version="1.0.0"):
    db.execute("""
      insert into public.quiz_attempts_v1
        (user_id,attempt_id,assessment_id,content_version,seed,presented,responses,position,submitted_at,correct)
      values (%s,%s,%s,%s,0,'[]','{}',0,%s,%s)
    """, (user, uuid4(), ident, version, stamp(day) if day else None, score))


with connect() as admin, connect() as a, connect() as b:
    assert scalar(admin, "select current_database()") == "syntutor_progression_test"
    admin.execute((MIGRATIONS / "20261108000005_achievements.sql").read_text())
    assert scalar(admin, """
      select count(*) from public.achievement_criteria_v1 c where activity_id is not null
        and ((metric='lessons' and not exists(select from public.lesson_catalog l
               where l.lesson_id=c.activity_id and l.content_version=c.content_version and l.published))
          or (metric='quizzes' and not exists(select from public.quiz_catalog_v1 q
               where q.assessment_id=c.activity_id and q.content_version=c.content_version and q.published)))
    """) == 0
    # Existing M4/M5 awards written by the actual RPCs before applying M8 are backfilled.
    identity(a, "new-account")
    assert unlocked(badges(a)) == {"first-lesson", "first-quiz", "perfect-five"}
    # Exercise the normal write paths after M8 too, including a genuine 0/5 submission.
    identity(a, "rpc-achievements")
    assert lesson(a)["earned"] == 15
    assert quiz(a, quiz_payload(0))["earned"] == 0
    assert unlocked(badges(a)) == {"first-lesson", "first-quiz"}

    identity(a, "achievement-learner")
    empty = badges(a)
    assert len(empty) == 10 and not unlocked(empty)
    assert empty["gap-spotter"]["options"][0][0]["count"] == 0
    # Invalid evidence channels, drafts, and wrong content versions never qualify.
    admin.execute("""
      insert into public.quiz_progress (user_id,rule_id,completed_count,perfect_count)
      values ('achievement-learner','old-stage',999,999)
    """)
    record_lesson(admin, "achievement-learner", "br-01", 1, "2.0.0")
    record_lesson(admin, "achievement-learner", "br-09", None)
    record_quiz(admin, "achievement-learner", "quiz-br-02", None, None)
    assert not unlocked(badges(a))

    user = "achievement-learner"
    record_lesson(admin, user, "br-08", 2)
    record_quiz(admin, user, "quiz-advanced", 0, 2)
    record_quiz(admin, user, "quiz-advanced", 0, 3)
    record_quiz(admin, user, "quiz-br-09", 4, 4)
    partial = badges(a)
    assert unlocked(partial) == {"first-lesson", "first-quiz", "gap-spotter"}
    assert partial["syntax-checkpoint"]["options"][0][0]["count"] == 1
    assert partial["syntax-checkpoint"]["options"][0][1]["count"] == 0
    assert partial["steady-practice"]["options"][0][0]["count"] == 2
    assert partial["quiz-explorer"]["options"][0][0]["count"] == 2

    record_quiz(admin, user, "quiz-advanced", 5, 5)
    record_quiz(admin, user, "quiz-cgel-clauses", 4, 6)
    record_lesson(admin, user, "cgel-clauses", 7)
    record_lesson(admin, user, "br-07", 7)
    record_lesson(admin, user, "br-03", 7)
    identity(b, user, "authenticated")
    with ThreadPoolExecutor(max_workers=2) as pool:
        later, same = list(pool.map(badges, (a, b)))
    assert later == same
    assert len(unlocked(later)) == 10
    for ident, day in {
        "gap-spotter": 4, "personal-best": 5, "syntax-checkpoint": 5,
        "steady-practice": 6, "framework-distinction": 7, "learning-path": 7,
    }.items():
        assert datetime.fromisoformat(later[ident]["unlocked_at"]) == stamp(day)
    assert scalar(admin, "select count(*) from public.achievement_unlocks_v1 where user_id=%s", (user,)) == 10
    assert scalar(admin, "select count(*) from public.player_stats where user_id=%s", (user,)) == 0
    assert badges(a) == later

    identity(b, "or-other-path", "authenticated")
    record_lesson(admin, "or-other-path", "br-09", 3)
    assert unlocked(badges(b)) == {"first-lesson", "gap-spotter"}
    identity(b, None)
    assert len(badges(b)) == 10 and not unlocked(badges(b))
    for role in ("anon", "authenticated"):
        identity(b, user, role)
        rejects(lambda: b.execute("select * from public.achievement_unlocks_v1"), InsufficientPrivilege)
        rejects(lambda: b.execute("update public.achievement_catalog_v1 set title='fake'"), InsufficientPrivilege)
        rejects(lambda: b.execute("insert into public.achievement_unlocks_v1 values "
                                  "('fake','perfect-five',now())"), InsufficientPrivilege)
        rejects(lambda: b.execute("select public.get_my_achievements('another-user')"), UndefinedFunction)

print("PASS: all ten badges, AND/OR paths, partial progress, UTC consistency, retries, version isolation, durable timestamps, and account isolation.")
