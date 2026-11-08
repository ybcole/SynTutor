"""Run M7's migration and two-session races against an empty, disposable PostgreSQL database."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
from time import monotonic, sleep
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

ROOT = Path(__file__).resolve().parents[1]
DSN = os.environ["SYNTUTOR_PROGRESSION_TEST_DSN"]
MIGRATIONS = ROOT / "supabase/migrations"
COURSE = json.loads((ROOT / "web/content/lessons/course.json").read_text())
BANK = json.loads((ROOT / "web/content/quizzes/bank.json").read_text())
LESSON = COURSE["lessons"][0]
ASSESSMENT = BANK["assessments"][0]
STAGES = ["predict", "understand", "worked", "guided", "transfer", "exit"]


def scalar(db, sql, params=()):
    return db.execute(sql, params).fetchone()[0]


def connect():
    return psycopg.connect(DSN, autocommit=True)


def identity(db, user, role="anon"):
    db.execute("reset role")
    scalar(db, "select set_config('request.jwt.claims', %s, false)",
           (json.dumps({"sub": user} if user else {}),))
    db.execute("set role " + role)


def lesson(db, version=None, **extra):
    state = {"responses": {k: LESSON[k]["answer"] for k in ("predict", "guided", "transfer", "exit")},
             "visited": STAGES, "stage": 5, **extra}
    return scalar(db, "select public.save_lesson_progress(%s, %s, %s)",
                  (LESSON["lesson_id"], version or LESSON["content_version"], Jsonb(state)))


def quiz_payload(score, seed=310, version=None):
    items = []
    responses = {}
    random = seed
    for pool in ASSESSMENT["pool_ids"]:
        random = (1664525 * random + 1013904223) % 2**32
        variants = sorted((q for q in BANK["items"] if q["pool_id"] == pool), key=lambda q: q["item_id"])
        item = variants[random * len(variants) // 2**32]
        options = [o["id"] for o in item["options"]]
        responses[item["item_id"]] = item["answer"] if len(items) < score else next(
            o for o in options if o != item["answer"])
        items.append({"item_id": item["item_id"], "content_version": item["content_version"],
                      "option_order": options})
    return {"attempt_id": str(uuid4()), "assessment_id": ASSESSMENT["assessment_id"],
            "content_version": version or ASSESSMENT["content_version"], "seed": seed,
            "presented": items, "responses": responses, "position": 4}


def quiz(db, payload):
    return scalar(db, "select public.save_quiz_attempt(%s, true)", (Jsonb(payload),))


def summary(db):
    return scalar(db, "select public.get_my_progression()")


def rejects(action, error):
    try:
        action()
    except error:
        return
    raise AssertionError(f"Expected {error.__name__}")


def race(admin, a, b, first, second):
    """Require the second real backend to wait on the first transaction."""
    with ThreadPoolExecutor(max_workers=1) as pool:
        with a.transaction():
            first_award = first(a)["earned"]
            waiting = pool.submit(second, b)
            deadline = monotonic() + 5
            while not scalar(admin, "select %s = any(pg_blocking_pids(%s))",
                             (a.info.backend_pid, b.info.backend_pid)):
                assert not waiting.done(), "Second transaction did not wait for the first"
                assert monotonic() < deadline, "Timed out observing an actual PostgreSQL lock"
                sleep(0.02)
        return first_award, waiting.result(timeout=5)["earned"]


with connect() as admin, connect() as a, connect() as b:
    assert scalar(admin, "select current_database()") == "syntutor_progression_test", (
        "Use a disposable database named syntutor_progression_test")
    admin.execute("""
      create role anon;
      create role authenticated;
      create schema auth;
      create function auth.jwt() returns jsonb language sql stable as $$
        select coalesce(nullif(current_setting('request.jwt.claims', true), '')::jsonb, '{}'::jsonb)
      $$;
      grant usage on schema auth to anon, authenticated;
      alter default privileges in schema public grant all on tables to anon, authenticated;
    """)
    migrations = sorted(MIGRATIONS.glob("*.sql"))
    for migration in migrations:
        if migration.name.endswith("_verified_progression.sql"):
            cutover = migration
            break
        admin.execute(migration.read_text())

    identity(a, "learner")
    assert lesson(a)["earned"] == 15
    assert quiz(a, quiz_payload(3))["earned"] == 6
    admin.execute("""
      update public.player_stats set xp = 5000, level = 9 where user_id = 'learner';
      insert into public.player_stats (user_id, xp, level) values ('legacy-only', 400, 4);
      insert into public.quiz_progress (user_id, rule_id, completed_count)
        values ('learner', 'old-rule', 1);
    """)
    admin.execute(cutover.read_text())

    assert summary(a) == {"lesson_xp": 15, "quiz_xp": 6, "xp": 21, "level": 0}
    assert scalar(admin, "select xp from public.legacy_player_stats_m7 where user_id = 'learner'") == 5000
    assert scalar(admin, "select xp from public.player_stats where user_id = 'legacy-only'") == 0
    assert scalar(a, "select count(*) from public.quiz_progress") == 1
    assert scalar(a, "select count(*) from public.xp_activity_ledger where activity_id is not null "
                     "and content_version is not null and evidence is not null") == 2

    identity(b, None)
    rejects(lambda: summary(b), psycopg.errors.InsufficientPrivilege)
    for table in ("player_stats", "quiz_progress", "xp_activity_ledger"):
        assert scalar(b, f"select count(*) from public.{table}") == 0
    identity(b, "other", "authenticated")
    assert summary(b)["xp"] == 0
    for table in ("player_stats", "quiz_progress", "xp_activity_ledger"):
        assert scalar(b, f"select count(*) from public.{table}") == 0
    for role in ("anon", "authenticated"):
        identity(a, "learner", role)
        assert not scalar(a, "select has_table_privilege('public.xp_activity_ledger', 'UPDATE')")
        for statement in (
            "insert into public.player_stats (user_id, xp) values ('learner', 50000)",
            "update public.player_stats set xp=50000",
            "delete from public.player_stats",
            "select * from public.legacy_player_stats_m7",
        ):
            rejects(lambda: a.execute(statement), psycopg.errors.InsufficientPrivilege)
    rejects(lambda: lesson(a, xp=5000), psycopg.errors.InvalidParameterValue)
    rejects(lambda: lesson(a, "99.0.0"), psycopg.errors.InvalidParameterValue)
    rejects(lambda: quiz(a, {**quiz_payload(5), "xp": 5000}), psycopg.errors.InvalidParameterValue)

    admin.execute("insert into public.lesson_catalog select lesson_id,'2.0.0',prerequisites,answer_key,true "
                  "from public.lesson_catalog where lesson_id=%s and content_version=%s",
                  (LESSON["lesson_id"], LESSON["content_version"]))
    admin.execute("insert into public.quiz_catalog_v1 select assessment_id,'2.0.0',item_version,pool_ids,true "
                  "from public.quiz_catalog_v1 where assessment_id=%s", (ASSESSMENT["assessment_id"],))
    identity(b, "learner")
    perfect = quiz_payload(5, 311)
    assert race(admin, a, b, lambda db: lesson(db, "2.0.0"), lambda db: quiz(db, perfect)) == (15, 4)
    assert lesson(b, "2.0.0")["earned"] == 0
    assert quiz(b, perfect)["earned"] == 0
    assert quiz(a, quiz_payload(0, 312, "2.0.0"))["earned"] == 0
    partial = quiz_payload(3, 313, "2.0.0")
    improved = quiz_payload(5, 314, "2.0.0")
    assert race(admin, a, b, lambda db: quiz(db, partial), lambda db: quiz(db, improved)) == (6, 4)

    identity(a, "new-account")
    identity(b, "new-account", "authenticated")
    assert race(admin, a, b, lesson, lesson) == (15, 0)
    same_attempt = quiz_payload(5)
    assert race(admin, a, b, lambda db: quiz(db, same_attempt), lambda db: quiz(db, same_attempt)) == (10, 0)

    for score in range(6):
        identity(a, f"score-{score}")
        result = quiz(a, quiz_payload(score, 350 + score))
        assert result["correct"] == score and result["earned"] == 2 * score
        assert summary(a)["xp"] == 2 * score

    identity(a, "learner")
    assert summary(a) == {"lesson_xp": 30, "quiz_xp": 20, "xp": 50, "level": 0}
    assert scalar(a, "select sum(xp) from public.xp_activity_ledger") == 50
    assert scalar(a, "select count(distinct event_key) from public.xp_activity_ledger") == 6
    assert scalar(a, "select count(*) from public.xp_activity_ledger where activity_type = 'quiz' "
                     "and (evidence->>'correct')::int = 5") == 2
    for version in ("3.0.0", "4.0.0", "5.0.0", "6.0.0"):
        admin.execute("insert into public.lesson_catalog select lesson_id,%s,prerequisites,answer_key,true "
                      "from public.lesson_catalog where lesson_id=%s and content_version=%s",
                      (version, LESSON["lesson_id"], LESSON["content_version"]))
        assert lesson(a, version)["earned"] == 15
    assert summary(a) == {"lesson_xp": 90, "quiz_xp": 20, "xp": 110, "level": 1}
    assert admin.execute("""
      select user_id from public.player_stats
      left join (select user_id, sum(xp) as total from public.xp_activity_ledger group by user_id)
      using (user_id)
      where xp <> coalesce(total, 0) or level <> public.lesson_level_for_xp(xp)
    """).fetchall() == []
    for xp, expected in ((0, 0), (99, 0), (100, 1), (219, 1), (220, 2), (360, 3), (700, 5)):
        assert scalar(admin, "select public.lesson_level_for_xp(%s)", (xp,)) == expected

print("PASS: native PostgreSQL cutover, private ledger, score and version caps, four two-session races, and reconciliation.")
