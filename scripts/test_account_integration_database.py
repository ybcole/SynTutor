"""Apply M11 to representative pre-existing account state after the M7–M9 suites."""
from psycopg.errors import InsufficientPrivilege
from test_progression_database import connect, identity, rejects, scalar, MIGRATIONS


with connect() as admin, connect() as a, connect() as b:
    assert scalar(admin, "select current_database()") == "syntutor_progression_test"
    admin.execute("""
      insert into public.analysis_history (user_id, sentence, is_valid) values
        ('learner', 'Private previous analysis.', true),
        ('1ad93bfd-f4e1-467e-b5b0-39c3eced67a0', 'Legacy UUID history.', true);
      insert into public.quiz_progress (user_id, rule_id, completed_count, perfect_count)
        values ('learner', 'legacy-parser-stage', 3, 2);
    """)
    identity(a, "learner")
    before = scalar(a, "select public.get_my_progression()")
    badges_before = scalar(a, "select public.get_my_achievements()")
    admin.execute((MIGRATIONS / "20261108000007_account_integration.sql").read_text())
    assert scalar(a, "select count(*) from public.analysis_history") == 1
    assert scalar(a, "select completed_count from public.quiz_progress where rule_id='legacy-parser-stage'") == 3
    assert scalar(a, "select public.get_my_progression()") == before
    assert scalar(a, "select public.get_my_achievements()") == badges_before
    assert scalar(admin, "select count(*) from public.analysis_history") == 2
    for role in ("anon", "authenticated"):
        identity(b, "other-account", role)
        assert scalar(b, "select count(*) from public.analysis_history") == 0
        assert scalar(b, "select count(*) from public.quiz_progress") == 0
        rejects(lambda: b.execute("update public.quiz_progress set perfect_count=999"), InsufficientPrivilege)
        rejects(lambda: b.execute("insert into public.quiz_progress (user_id,rule_id) values ('other-account','fake')"),
                InsufficientPrivilege)
        rejects(lambda: b.execute("insert into public.analysis_history (user_id,sentence,is_valid) "
                                  "values ('learner','Forged',false)"), InsufficientPrivilege)
        assert b.execute("delete from public.analysis_history").rowcount == 0
    assert a.execute("insert into public.analysis_history (user_id,sentence,is_valid) "
                     "values ('learner','New private analysis.',true)").rowcount == 1
    assert a.execute("delete from public.analysis_history where sentence='New private analysis.'").rowcount == 1
    rejects(lambda: a.execute("update public.analysis_history set sentence='Unexpected'"), InsufficientPrivilege)
    identity(b, None)
    assert scalar(b, "select count(*) from public.analysis_history") == 0
    assert scalar(b, "select public.get_leaderboard('weekly')->>'enabled'") == "false"

print("PASS: additive account migration, retained legacy rows, history CRUD isolation, stable badges/XP, and paused rankings.")
