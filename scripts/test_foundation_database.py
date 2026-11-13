"""Run the revised assessment migration and two-session races in disposable PostgreSQL."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
import sys
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg.types.json import Jsonb

from seed_foundations import render
from test_foundation_fixture import fixture_course
from test_progression_database import identity, quiz, quiz_payload, scalar, summary

ROOT = Path(__file__).resolve().parents[1]
DSN = os.environ['SYNTUTOR_PROGRESSION_TEST_DSN']
COURSE = fixture_course()
REVISED = next(l for l in COURSE['lessons'] if l.get('revised_assessment'))
IDENT = REVISED['lesson_id']
VERSION = REVISED['content_version']
ASSESSMENT = REVISED['revised_assessment']
SECTIONS = ASSESSMENT['required_sections']


def event(db, payload, version=VERSION):
    return scalar(db, 'select public.save_foundation_event(%s, %s, %s)', (IDENT, version, Jsonb(payload)))


def attempt(kind, correct):
    return {
        'kind': kind,
        'attempt_id': str(uuid4()),
        'answers': {q['id']: 'a' if i < correct else 'b' for i, q in enumerate(ASSESSMENT[kind])},
    }


def visit(db, section):
    return event(db, {'kind': 'visit', 'section': section})


def legacy(db, chapter):
    lesson = next(l for l in COURSE['lessons'] if l['lesson_id'] == chapter)
    return scalar(db, 'select public.save_lesson_progress(%s, %s, %s)', (chapter, '1.0.0', Jsonb({
        'responses': {key: lesson[key]['answer'] for key in ('predict', 'guided', 'transfer', 'exit')},
        'visited': ['predict', 'understand', 'worked', 'guided', 'transfer', 'exit'],
        'stage': 5,
    })))


def reject(call, match):
    try:
        call()
    except psycopg.Error as error:
        assert match in str(error), error
    else:
        raise AssertionError(f'Expected rejection containing {match}')


def connect():
    return psycopg.connect(DSN, autocommit=True)


if __name__ == '__main__':
    with connect() as admin, connect() as a, connect() as b:
        assert scalar(admin, 'select current_database()') == 'syntutor_progression_test'
        if '--after-account-tests' in sys.argv:
            for migration in sorted((ROOT / 'supabase/migrations').glob('20261113*foundations*.sql')):
                admin.execute(migration.read_text())
        else:
            admin.execute("""
              create role anon; create role authenticated; create schema auth;
              create function auth.jwt() returns jsonb language sql stable as $$
                select coalesce(nullif(current_setting('request.jwt.claims', true), '')::jsonb, '{}'::jsonb)
              $$;
              grant usage on schema auth to anon, authenticated;
              grant execute on function auth.jwt() to anon, authenticated;
            """)
            for migration in sorted((ROOT / 'supabase/migrations').glob('*.sql')):
                admin.execute(migration.read_text())
        admin.execute(render(COURSE))
        admin.execute(render(COURSE))
        identity(a, 'historical')
        assert legacy(a, 'br-01')['earned'] == 15
        assert legacy(a, 'br-02')['earned'] == 15
        assert quiz(a, quiz_payload(3))['earned'] == 6
        assert summary(a)['xp'] == 36
        reject(lambda: event(a, attempt('opening', 2)), 'inactive')
        reject(lambda: scalar(a, 'select public.set_foundation_active_version(%s,%s)', (IDENT, VERSION)), 'permission denied')

        def activate(version):
            scalar(admin, 'select public.set_foundation_active_version(%s,%s)', (IDENT, version))

        activate(VERSION)
        assert summary(a) == {'lesson_xp': 15, 'quiz_xp': 6, 'xp': 21, 'level': 0}
        assert scalar(a, 'select xp from public.player_stats') == 21
        assert scalar(a, "select count(*) from public.lesson_progress where lesson_id='br-02' and completed_at is not null") == 1
        assert scalar(a, 'select count(*) from public.foundation_progress') == 0
        reject(lambda: legacy(a, 'br-02'), 'Retired')
        assert legacy(a, 'cgel-clauses')['earned'] == 15

        identity(a, None)
        reject(lambda: event(a, attempt('closing', 6)), 'Sign in')
        identity(a, 'revised', 'authenticated')
        reject(lambda: event(a, {**attempt('closing', 6), 'xp': 15}), 'Invalid')
        reject(lambda: event(a, {**attempt('closing', 6), 'user_id': 'historical'}), 'Invalid')
        reject(lambda: event(a, {**attempt('closing', 6), 'answers': {'closing-0': 'a'}}), 'Invalid')
        reject(lambda: event(a, {**attempt('closing', 6), 'answers': {**attempt('closing', 6)['answers'], 'closing-0': 'x'}}), 'Invalid')
        reject(lambda: visit(a, 'made-up'), 'Invalid')
        reject(lambda: event(a, attempt('closing', 6), '2.0.1'), 'inactive')
        reject(lambda: a.execute('select * from public.foundation_assessments'), 'permission denied')
        reject(lambda: a.execute('update public.foundation_progress set xp=15'), 'permission denied')
        opened = event(a, attempt('opening', 2))
        assert (opened['opening_correct'], opened['opening_first_response'], opened['earned']) == (2, 'a', 0)
        assert event(a, attempt('opening', 5))['opening_correct'] == 2
        assert legacy(a, 'cgel-clauses')['completed_at'] is None
        zero = event(a, attempt('closing', 0))
        assert (zero['last_correct'], zero['best_correct'], zero['xp'], zero['completed_at']) == (0, 0, 0, None)
        for section in SECTIONS:
            completed = visit(a, section)
        assert completed['completed_at']
        assert legacy(a, 'cgel-clauses')['earned'] == 15
        assert scalar(a, "select count(*) from public.lesson_progress where lesson_id='br-02'") == 0

        prior = attempt('closing', 3)
        assert event(a, prior)['earned'] == 7
        assert event(a, prior)['earned'] == 0
        changed = {**prior, 'answers': attempt('closing', 4)['answers']}
        reject(lambda: event(a, changed), 'already used')
        assert event(a, attempt('closing', 3))['earned'] == 0
        lower = event(a, attempt('closing', 1))
        assert (lower['last_correct'], lower['best_correct'], lower['earned']) == (1, 3, 0)
        assert event(a, attempt('closing', 4))['earned'] == 3
        identity(b, 'revised')
        same = attempt('closing', 6)
        with ThreadPoolExecutor(2) as pool:
            jobs = [pool.submit(event, conn, same) for conn in (a, b)]
            assert sorted(job.result(timeout=10)['earned'] for job in jobs) == [0, 5]
        assert event(a, attempt('closing', 6))['earned'] == 0
        assert event(a, prior)['last_correct'] == 6, 'An old replay cannot replace the last result.'
        identity(b, 'racing')
        identity(a, 'racing')
        with ThreadPoolExecutor(2) as pool:
            jobs = [pool.submit(event, conn, attempt('closing', score)) for conn, score in ((a, 3), (b, 6))]
            assert sum(job.result(timeout=10)['earned'] for job in jobs) == 15
        assert summary(a)['lesson_xp'] == 15
        identity(a, 'revised', 'authenticated')
        assert summary(a)['lesson_xp'] == 30
        assert scalar(a, 'select xp from public.player_stats') == 30
        identity(b, 'different')
        assert scalar(b, 'select count(*) from public.foundation_attempts') == 0
        assert scalar(b, 'select count(*) from public.foundation_progress') == 0

        activate(None)
        assert summary(a)['lesson_xp'] == 15
        identity(b, 'historical')
        assert summary(b) == {'lesson_xp': 45, 'quiz_xp': 6, 'xp': 51, 'level': 0}
        assert scalar(b, 'select xp from public.player_stats') == 51
        reject(lambda: event(a, same), 'inactive')
        activate(VERSION)
        assert summary(a)['lesson_xp'] == 30
        assert summary(b)['xp'] == 36
    print('PASS: actual migrations, XP deltas and cap, score/replay race, RLS, Cambridge prerequisite, activation and rollback.')
