"""Browser account journey against real disposable PostgreSQL policies and RPCs."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from threading import Thread

from playwright.sync_api import expect, sync_playwright
from psycopg.errors import Error
from psycopg.types.json import Jsonb
from test_progression_database import BANK, LESSON, ROOT, STAGES, connect, identity, scalar

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
    from: name => ({select: () => query('select', name)}),
  };
};
"""
SELECTS = {
    "analysis_history": "select id,sentence,is_valid,constraints_fired,created_at from public.analysis_history",
    "lesson_progress": "select lesson_id,content_version,responses,visited,stage,completed_at from public.lesson_progress",
    "quiz_attempts_v1": "select attempt_id,assessment_id,content_version,seed,presented,responses,position,started_at,submitted_at,correct from public.quiz_attempts_v1",
}


def transport(body):
    # This fixture treats these two explicit tokens as already-verified Clerk
    # subjects. The real RLS and SQL functions handle all data/award checks.
    token = body["token"]
    assert token in (None, "journey-a", "journey-b")
    name, args = body["name"], body["args"]
    with connect() as db:
        identity(db, token)
        if body["kind"] == "select":
            result = scalar(db, f"select coalesce(jsonb_agg(r), '[]') from ({SELECTS[name]}) r")
        elif name == "save_lesson_progress":
            result = scalar(db, "select public.save_lesson_progress(%s,%s,%s)", (
                args["p_lesson_id"], args["p_content_version"], Jsonb(args["p_state"])))
        elif name == "save_quiz_attempt":
            result = scalar(db, "select public.save_quiz_attempt(%s,%s)", (
                Jsonb(args["p_attempt"]), args["p_submit"]))
        elif name == "get_leaderboard":
            result = scalar(db, "select public.get_leaderboard(%s)", (args["p_period"],))
        elif name == "set_my_leaderboard_preference":
            scalar(db, "select public.set_my_leaderboard_preference(%s,%s)",
                   (args["p_alias"], args["p_opt_in"]))
            result = None
        else:
            assert name in ("get_my_progression", "get_my_achievements")
            result = scalar(db, f"select public.{name}()")
        return {"data": result, "error": None}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=ROOT / "web"))
Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_port}"

try:
    with connect() as admin, sync_playwright() as playwright:
        assert scalar(admin, "select current_database()") == "syntutor_progression_test"
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
        page.goto(base)

        def nav(view):
            page.locator(f'.sidebar-item[data-view="{view}"]').click()

        nav("leaderboard")
        page.get_by_label("Public alias").fill("JourneyTree")
        page.get_by_role("button", name="Join public rankings").click()
        expect(page.get_by_text("Public participation saved.")).to_be_visible()

        nav("lessons")
        lesson = page.locator("#curriculumView")
        lesson.locator(".curriculum-card").filter(
            has=page.get_by_role("heading", name=LESSON["title"], exact=True)).get_by_role("button").click()
        for key in STAGES:
            if key == "worked":
                for _ in LESSON["worked_example"]["steps"][1:]:
                    lesson.get_by_role("button", name="Next step", exact=True).click()
            if LESSON.get(key):
                question = lesson.locator(f'[data-question="{key}"]')
                question.locator(f'input[value="{LESSON[key]["answer"]}"]').check()
                expect(question.locator(".lesson-feedback.correct")).to_be_visible()
            action = "Complete lesson · 15 XP once" if key == "exit" else "Continue →"
            lesson.get_by_role("button", name=action, exact=True).click()
        expect(lesson.locator(".lesson-save-status")).to_contain_text("Synced to your account")

        nav("quizzes")
        quiz = page.locator("#quizzesView")
        quiz.locator('[data-assessment="quiz-br-01"]').get_by_role("button", name="Start assessment").click()
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
        quiz.get_by_role("button", name="Submit assessment", exact=True).click()
        expect(quiz.locator(".quiz-score")).to_contain_text("5/5")

        # Fresh tab state exercises the real PostgreSQL jsonb manifest ordering.
        page.evaluate("localStorage.removeItem('syntutor:assessments:v1:journey-a')")
        page.reload()
        nav("quizzes")
        quiz.get_by_text("Your attempt history").click()
        expect(quiz.get_by_role("button", name="Constituents and hierarchy · 5/5 · v1.0.0")).to_be_visible()

        nav("achievements")
        expect(page.locator("#achievementsProgressLabel")).to_contain_text("25 verified XP")
        for badge in ("first-lesson", "first-quiz", "perfect-five"):
            expect(page.locator(f'[data-achievement="{badge}"] time')).to_be_visible()
        nav("leaderboard")
        expect(page.get_by_role("cell", name="JourneyTree")).to_be_visible()
        expect(page.locator("#leaderboardEntries")).to_contain_text("25")
        page.get_by_role("button", name="Leave public rankings").click()
        expect(page.get_by_role("cell", name="JourneyTree")).to_have_count(0)
        expect(page.locator("#leaderboardLifetime")).to_contain_text("25 verified XP")

        page.locator("#headerHistoryBtn").click()
        expect(page.get_by_text("Only account A sees this.", exact=True)).to_be_visible()
        page.evaluate("switchAccount('journey-b')")
        page.locator("#headerHistoryBtn").click()
        expect(page.get_by_text("Only account B sees this.", exact=True)).to_be_visible()
        expect(page.get_by_text("Only account A sees this.", exact=True)).to_have_count(0)
        page.locator("#closeDrawerBtn").click()
        nav("achievements")
        expect(page.locator("#achievementsProgressLabel")).to_contain_text("0 verified XP")
        expect(page.locator('[data-achievement="first-lesson"] time')).to_have_count(0)
        nav("builder")
        tools = page.locator("#builderTools")
        tools.get_by_label("New words", exact=True).fill("PrivateB")
        tools.get_by_role("button", name="Add words", exact=True).click()
        nodes = "() => import('/js/syntax-builder-ui.js').then(m => Object.values(m.builderModel().nodes).map(n => n.text))"
        if page.locator("#inputText").input_value() != "PrivateB":
            print("ACCOUNT BUILDER MIRROR DIAGNOSTIC", page.evaluate("""() => ({
              model: Object.values(window.__builderDebugNodes || []),
              input: document.querySelector('#inputText')?.value,
              textContent: document.querySelector('#builderTools')?.textContent?.slice(-600),
              saveStatus: document.querySelector('[data-builder-save]')?.textContent,
              editButtons: [...document.querySelectorAll('#builderTools button')].filter(b=>b.textContent==='Add words').length,
              editorVisible: !!document.querySelector('#builderTools details[open]'),
            })"""), errors, flush=True)
        expect(page.locator("#inputText")).to_have_value("PrivateB", timeout=10000)
        assert "PrivateB" in page.evaluate(nodes)
        # Repeated auth notifications for the same identity must not discard
        # an edited Builder draft while genuine account changes still isolate it.
        page.evaluate("window.accountChanged?.()")
        expect(page.locator("#inputText")).to_have_value("PrivateB", timeout=10000)
        assert "PrivateB" in page.evaluate(nodes)
        page.evaluate("switchAccount('journey-a')")
        expect(page.locator("#inputText")).not_to_have_value("PrivateB", timeout=10000)
        assert "PrivateB" not in page.evaluate(nodes)
        page.evaluate("switchAccount('journey-b')")
        expect(page.locator("#inputText")).to_have_value("PrivateB", timeout=10000)
        assert "PrivateB" in page.evaluate(nodes)
        nav("achievements")
        # Complete a stale parser request after leaving the Generator and
        # switching account. It must not repaint or lock the next workspace.
        page.locator("#newSessionBtn").click()
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
        expect(page.locator("#achievementsProgressLabel")).to_contain_text("25 verified XP")
        page.locator("#newSessionBtn").click()
        expect(page.locator("#inputText")).to_have_value("")
        expect(page.get_by_text("stale parse", exact=True)).to_have_count(0)
        nav("achievements")
        page.evaluate("switchAccount(null)")
        expect(page.locator("#headerHistoryBtn")).to_be_hidden()
        expect(page.locator("#achievementsProgressLabel")).to_have_text("Sign in to track your progress.")
        assert not errors, errors
        browser.close()
finally:
    with connect() as admin:
        admin.execute("update public.leaderboard_release_v1 set enabled=false")
    server.shutdown()
    server.server_close()

print("PASS: browser lesson + quiz → PostgreSQL XP and badges → opt-in board → private history and account switch.")
