"""Browser account journey against real disposable PostgreSQL policies and RPCs."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import re
from threading import Thread

from playwright.sync_api import expect, sync_playwright
from psycopg.errors import Error
from psycopg.types.json import Jsonb
from test_progression_database import BANK, ROOT, connect, identity, scalar

BR01_PILOT = json.loads((ROOT / "web/content/lessons/br-01-pilot.json").read_text())

BOOT = """
localStorage.setItem('syntutor_onboarding_seen','1');
window.Clerk = { load: async () => {}, addListener(fn) { window.accountChanged = fn; } };
window.switchAccount = id => {
  Clerk.user = id ? { id, firstName: id } : null;
  Clerk.session = id ? { id: 'session-' + id, getToken: async () => id } : null;
  window.accountChanged?.();
};
switchAccount('journey-a');
"""
TRANSPORT = """
export const createClient = (_url, _key, {accessToken}) => {
  const request = async (kind, name, args, signal) => {
    const token = await accessToken();
    const response = await fetch('/test-account-transport', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({kind, name, args, token}), signal,
    });
    return response.json();
  };
  const query = (kind, name, args = {}) => ({
    abortSignal: signal => request(kind, name, args, signal),
    then: (resolve, reject) => request(kind, name, args).then(resolve, reject),
    order() { return this; }, limit() { return this; },
  });
  return {
    rpc: (name, args) => query('rpc', name, args),
    from: name => ({
      select: () => query('select', name),
      insert: row => query('insert', name, { row }),
      upsert: (row, opts) => query('upsert', name, { row, opts }),
    }),
  };
};
"""
SELECTS = {
    "analysis_history": "select id,sentence,is_valid,constraints_fired,created_at from public.analysis_history",
    "lesson_progress": "select lesson_id,content_version,responses,visited,stage,completed_at,updated_at from public.lesson_progress",
    "foundation_progress": (
        "select user_id,lesson_id,content_version,visited,opening_correct,opening_first_response,"
        "last_correct,last_answers,best_correct,xp,completed_at,updated_at from public.foundation_progress"
    ),
    "quiz_attempts_v1": (
        "select attempt_id,assessment_id,content_version,seed,presented,responses,position,"
        "started_at,submitted_at,correct from public.quiz_attempts_v1"
    ),
    "quiz_attempts_v2": (
        "select attempt_id,assessment_id,content_version,spec,title,diagnostic,seed,presented,"
        "responses,position,started_at,submitted_at,correct from public.quiz_attempts_v2"
    ),
    "quiz_practice_v2": "select payload from public.quiz_practice_v2",
}


def ensure_latest_migrations(admin):
    """Apply post-Foundations 20261116 migrations when running right after test_foundation_database.py."""
    if scalar(admin, "select to_regclass('public.quiz_attempts_v2')") is not None:
        return
    for migration in sorted((ROOT / "supabase/migrations").glob("20261116*.sql")):
        admin.execute(migration.read_text())


def transport(body):
    # This fixture treats these two explicit tokens as already-verified Clerk
    # subjects. The real RLS and SQL functions handle all data/award checks.
    token = body["token"]
    assert token in (None, "journey-a", "journey-b")
    kind, name, args = body["kind"], body["name"], body.get("args") or {}
    with connect() as db:
        identity(db, token)
        if kind == "select":
            result = scalar(db, f"select coalesce(jsonb_agg(r), '[]') from ({SELECTS[name]}) r")
        elif kind == "insert" and name == "analysis_history":
            row = args["row"]
            db.execute(
                "insert into public.analysis_history (user_id,sentence,is_valid,constraints_fired) values (%s,%s,%s,%s)",
                (row["user_id"], row["sentence"], row["is_valid"], Jsonb(row.get("constraints_fired") or [])),
            )
            result = None
        elif kind == "upsert" and name == "quiz_practice_v2":
            row = args["row"]
            db.execute(
                """insert into public.quiz_practice_v2 (user_id,attempt_id,payload)
                   values (%s,%s,%s)
                   on conflict (user_id,attempt_id) do update set payload=excluded.payload, updated_at=now()""",
                (row["user_id"], row["attempt_id"], Jsonb(row["payload"])),
            )
            result = None
        elif name == "save_lesson_progress":
            result = scalar(db, "select public.save_lesson_progress(%s,%s,%s)", (
                args["p_lesson_id"], args["p_content_version"], Jsonb(args["p_state"])))
        elif name == "save_foundation_event":
            result = scalar(db, "select public.save_foundation_event(%s,%s,%s)", (
                args["p_lesson_id"], args["p_content_version"], Jsonb(args["p_event"])))
        elif name == "save_quiz_attempt":
            result = scalar(db, "select public.save_quiz_attempt(%s,%s)", (
                Jsonb(args["p_attempt"]), args["p_submit"]))
        elif name == "save_quiz_v2_attempt":
            result = scalar(db, "select public.save_quiz_v2_attempt(%s,%s)", (
                Jsonb(args["p_attempt"]), args["p_submit"]))
        elif name == "ensure_leaderboard_participation":
            result = scalar(db, "select public.ensure_leaderboard_participation(%s)", (
                args.get("p_preferred_alias"),))
        elif name == "get_leaderboard":
            result = scalar(db, "select public.get_leaderboard(%s)", (args["p_period"],))
        elif name == "set_my_leaderboard_preference":
            scalar(db, "select public.set_my_leaderboard_preference(%s,%s)",
                   (args["p_alias"], args["p_opt_in"]))
            result = None
        else:
            assert name in ("get_my_progression", "get_my_achievements"), f"Unexpected RPC: {name}"
            result = scalar(db, f"select public.{name}()")
        return {"data": result, "error": None}


def dismiss_onboarding(page):
    skip = page.locator("#onboarding .onboarding-skip")
    try:
        skip.wait_for(state="visible", timeout=1500)
        skip.click()
    except Exception:
        pass


BUILDER_NODES_JS = """async () => {
  const url = performance.getEntriesByType('resource')
    .map(r => r.name)
    .find(u => u.includes('/js/syntax-builder-ui.js')) || '/js/syntax-builder-ui.js';
  const mod = await import(url);
  return Object.values(mod.builderModel().nodes).map(n => n.text);
}"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=ROOT / "web"))
Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_port}"

try:
    with connect() as admin, sync_playwright() as playwright:
        assert scalar(admin, "select current_database()") == "syntutor_progression_test"
        ensure_latest_migrations(admin)
        admin.execute("update public.leaderboard_release_v1 set enabled=true")
        admin.execute("""insert into public.analysis_history (user_id,sentence,is_valid) values
                      ('journey-a','Only account A sees this.',true), ('journey-b','Only account B sees this.',true)""")
        browser = playwright.chromium.launch(executable_path=os.getenv("SYNTUTOR_CHROMIUM_BIN"))
        page = browser.new_page(viewport={"width": 1360, "height": 960})
        page.add_init_script(BOOT)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))

        def route(request):
            url = request.request.url
            if url.startswith("https://esm.sh/"):
                request.fulfill(content_type="application/javascript", body=TRANSPORT)
            elif url == base + "/test-account-transport":
                try:
                    request.fulfill(json=transport(request.request.post_data_json))
                except Error as error:
                    request.fulfill(json={"data": None, "error": {"code": error.sqlstate, "message": error.diag.message_primary}})
            elif url.startswith(base):
                request.continue_()
            else:
                request.abort()

        page.route("**/*", route)
        page.goto(base, wait_until="domcontentloaded")
        dismiss_onboarding(page)
        page.locator("#sidebarBrandBtn").click()

        def nav(view):
            page.locator(f'.sidebar-item[data-view="{view}"]').click()

        def open_leaderboard_settings():
            page.locator("#identityChip").click()
            page.locator("#profileLeaderboardSettings").click()
            modal = page.locator("#leaderboardSettingsModal")
            expect(modal).to_be_visible()
            return modal

        # 1. Customize public leaderboard alias via Leaderboard Settings.
        nav("leaderboard")
        settings = open_leaderboard_settings()
        settings.locator("#leaderboardAlias").fill("JourneyTree")
        settings.locator("#leaderboardJoin").click()
        expect(settings.locator("#leaderboardPreferenceStatus")).to_have_text("Public participation and alias saved.")
        settings.locator("#leaderboardSettingsCloseBtn").click()
        expect(settings).to_be_hidden()

        # 2. Complete active Foundations lesson br-01 (2.0.0) via save_foundation_event (15 verified XP).
        nav("lessons")
        lesson = page.locator("#curriculumView")
        lesson.locator('[data-lesson-card="br-01"]').get_by_role("button", name="Start lesson", exact=True).click()
        for sec in BR01_PILOT["revised_assessment"]["required_sections"]:
            lesson.locator(f'.lesson-section-sidebar a[href$="/{sec}"]').click()
            expect(page).to_have_url(re.compile(rf"#lesson/br-01/{re.escape(sec)}$"))
        lesson.locator('.lesson-section-sidebar a[href$="/closing-check"]').click()
        closing = lesson.get_by_role("region", name="Check what you learned", exact=True)
        questions = BR01_PILOT["revised_assessment"]["closing"]
        for idx, q in enumerate(questions):
            closing.locator(f'input[value="{q["answer"]}"]').check()
            btn_name = "Submit closing check" if idx == len(questions) - 1 else "Next question →"
            closing.get_by_role("button", name=btn_name, exact=True).click()
        expect(closing).to_contain_text("15 / 15 lesson XP verified")

        # 3. Complete published br-01 verified assessment (quiz-br-01) -> save_quiz_attempt (10 verified XP).
        quiz = page.locator("#quizzesView")
        page.evaluate("window.location.hash = '#quiz/quiz-br-01'")
        for i in range(5):
            question = quiz.locator("[data-quiz-item]")
            expect(question).to_be_visible()
            item_id = question.get_attribute("data-quiz-item")
            item = next(item for item in BANK["items"] if item["item_id"] == item_id)
            question.locator(f'input[value="{item["answer"]}"]').check()
            expect(quiz).to_have_attribute("aria-busy", "false")
            if i < 4:
                quiz.get_by_role("button", name="Next question").click()
                expect(question).not_to_have_attribute("data-quiz-item", item_id)
        quiz.get_by_role("button", name="Submit", exact=True).click()
        expect(quiz.locator(".quiz-score")).to_contain_text("5/5")

        # 4. Fresh tab state exercises the real PostgreSQL jsonb manifest ordering.
        page.evaluate("localStorage.removeItem('syntutor:assessments:v1:journey-a')")
        page.reload(wait_until="domcontentloaded")
        dismiss_onboarding(page)
        page.locator("#sidebarBrandBtn").click()
        nav("quizzes")
        quiz.locator("details.quiz-history > summary").click()
        expect(quiz.get_by_role("button", name="Constituents and hierarchy · 5/5 (100%)")).to_be_visible()

        # 5. Verified XP on sidebar meter + unlocked badges + public leaderboard rank & opt-out.
        progress_label = page.locator("#sidebarProgressLabel")
        expect(progress_label).to_have_text("25/100 XP")
        expect(page.locator("#identityChip")).to_have_attribute("aria-label", "journey-a, Level 0, 25 verified XP")

        nav("achievements")
        for badge in ("first-lesson", "first-quiz", "perfect-five"):
            expect(page.locator(f'[data-achievement="{badge}"] time')).to_be_visible()

        nav("leaderboard")
        expect(page.get_by_role("cell", name="JourneyTree")).to_be_visible()
        expect(page.locator("#leaderboardEntries")).to_contain_text("25")
        settings = open_leaderboard_settings()
        settings.locator("#leaderboardLeave").click()
        expect(settings.locator("#leaderboardPreferenceStatus")).to_have_text("You opted out of public rankings.")
        settings.locator("#leaderboardSettingsCloseBtn").click()
        expect(settings).to_be_hidden()
        expect(page.get_by_role("cell", name="JourneyTree")).to_have_count(0)
        expect(progress_label).to_have_text("25/100 XP")

        # 6. Private analysis history RLS isolation across journey-a and journey-b.
        open_history_js = """async () => {
          const url = performance.getEntriesByType('resource')
            .map(r => r.name)
            .find(u => u.includes('/js/history.js')) || '/js/history.js';
          const mod = await import(url);
          return mod.openHistoryDrawer();
        }"""
        assert page.evaluate(open_history_js) is True
        expect(page.get_by_text("Only account A sees this.", exact=True)).to_be_visible()
        page.evaluate("switchAccount('journey-b')")
        assert page.evaluate(open_history_js) is True
        expect(page.get_by_text("Only account B sees this.", exact=True)).to_be_visible()
        expect(page.get_by_text("Only account A sees this.", exact=True)).to_have_count(0)
        page.locator("#closeDrawerBtn").click()

        nav("achievements")
        expect(progress_label).to_have_text("0/100 XP")
        expect(page.locator('[data-achievement="first-lesson"] time')).to_have_count(0)

        def wait_builder_word(word, present=True):
            for _ in range(50):
                words = page.evaluate(BUILDER_NODES_JS)
                if (word in words) is present:
                    return words
                page.wait_for_timeout(100)
            raise AssertionError(f"Expected {word!r} present={present} in builderModel(), got {words!r}")

        # 7. Unified Syntax Builder draft isolation across accounts.
        page.locator("#newSessionBtn").click()
        page.locator("#exploreBuilderBtn").click()
        expect(page.locator("#builderCanvas")).to_be_visible()
        page.locator("#inputText").evaluate("""(el) => {
          el.removeAttribute('readonly');
          el.value = 'PrivateB';
          el.dispatchEvent(new Event('input', { bubbles: true }));
        }""")
        wait_builder_word("PrivateB", present=True)
        expect(page.locator("#inputText")).to_have_value("PrivateB", timeout=10000)

        # Repeated auth notifications for the same identity must not discard an edited Builder draft
        # while genuine account changes isolate and restore each account's draft.
        page.evaluate("window.accountChanged?.()")
        expect(page.locator("#inputText")).to_have_value("PrivateB", timeout=10000)
        assert "PrivateB" in page.evaluate(BUILDER_NODES_JS)
        page.evaluate("switchAccount('journey-a')")
        expect(page.locator("#inputText")).not_to_have_value("PrivateB", timeout=10000)
        wait_builder_word("PrivateB", present=False)
        page.evaluate("switchAccount('journey-b')")
        expect(page.locator("#inputText")).to_have_value("PrivateB", timeout=10000)
        wait_builder_word("PrivateB", present=True)

        # 8. Stale /api/parse response after leaving Generator and switching account must not repaint or lock.
        page.locator("#exploreBuilderBtn").click()
        expect(page.locator("#builderCanvas")).to_be_hidden()
        page.evaluate("""() => {
          const fetchActual = window.fetch;
          window.fetch = (url, options) => {
            if (!String(url).endsWith('/api/parse')) return fetchActual(url, options);
            return new Promise(resolve => {
              window.releaseOldAnalysis = () => resolve(new Response(JSON.stringify({error:'stale parse'}), {
                status: 503, headers: {'Content-Type':'application/json'}
              }));
            });
          };
          const input = document.querySelector('#inputText');
          input.readOnly = false;
          input.value = 'Only the previous analysis saw this.';
          input.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter',ctrlKey:true,bubbles:true}));
        }""")
        page.wait_for_function("typeof window.releaseOldAnalysis === 'function'")
        nav("achievements")
        page.evaluate("switchAccount('journey-a'); releaseOldAnalysis()")
        expect(progress_label).to_have_text("25/100 XP")
        page.locator("#newSessionBtn").click()
        expect(page.locator("#inputText")).to_have_value("")
        expect(page.get_by_text("stale parse", exact=True)).to_have_count(0)

        # 9. Sign-out blocks private history access and clears verified XP.
        nav("achievements")
        page.evaluate("switchAccount(null)")
        assert page.evaluate(open_history_js) is False
        expect(page.locator("#historyDrawerBackdrop")).not_to_have_class(re.compile(r"\bactive\b"))
        expect(progress_label).to_have_text("Sign in for verified XP.")
        expect(page.locator("#achievementsStatsCounter")).to_contain_text("Sign in to track yours")
        assert not errors, errors
        browser.close()
finally:
    with connect() as admin:
        admin.execute("update public.leaderboard_release_v1 set enabled=false")
    server.shutdown()
    server.server_close()

print("PASS: browser lesson + quiz → PostgreSQL XP and badges → opt-in board → private history, unified Builder draft isolation, and account switch.")
