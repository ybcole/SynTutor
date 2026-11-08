"""Exercise progression presentation with a stubbed account and database transport."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CLERK = """
localStorage.setItem('syntutor_onboarding_seen', '1');
window.Clerk = {
  user: { id: 'learner', firstName: 'Test' },
  session: { id: 'session', getToken: async () => 'test' },
  load: async () => {},
  addListener: fn => { window.changeIdentity = fn; },
};
window.progressionCalls = [];
"""
CLIENT = """
export const createClient = () => ({
  from: table => {
    window.progressionCalls.push(table);
    return { select: () => ({ eq: () => ({
      abortSignal: async () => ({ data: [], error: null }),
    }) }) };
  },
  rpc: method => {
    window.progressionCalls.push(method);
    return { abortSignal: async () => window.progressionOffline
      ? { error: { message: 'Unavailable' } }
      : { data: { xp: 110, lesson_xp: 90, quiz_xp: 20, level: 1 }, error: null } };
  },
});
"""


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=ROOT / "web"))
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
base = f"http://127.0.0.1:{server.server_port}"
try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.getenv("SYNTUTOR_CHROMIUM_BIN"))
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.add_init_script(CLERK)

        def route(request):
            url = request.request.url
            if url.startswith("https://esm.sh/"):
                request.fulfill(content_type="application/javascript", body=CLIENT)
            elif url.startswith(base):
                request.continue_()
            else:
                request.abort()

        page.route("**/*", route)
        page.goto(base)
        achievements = page.locator('.sidebar-item[data-view="achievements"]')
        leaderboard = page.locator('.sidebar-item[data-view="leaderboard"]')
        label = page.locator("#achievementsProgressLabel")

        achievements.click()
        expect(label).to_have_text("Level 1 · 110 verified XP (90 lesson + 20 quiz) · 110 XP to Level 2")
        assert 8 < float(page.locator("#achievementsProgressFill").evaluate(
            "(element) => parseFloat(element.style.width)")) < 9
        assert page.locator(".achievement-reward").count() == 0

        calls = page.evaluate("window.progressionCalls.slice()")
        assert sorted(calls) == ["get_my_progression", "quiz_progress"]
        leaderboard.click()
        expect(page.get_by_text("Public rankings are paused.", exact=False)).to_be_visible()
        assert page.evaluate("window.progressionCalls") == calls

        page.evaluate("window.progressionOffline = true")
        achievements.click()
        expect(label).to_contain_text("Verified XP is unavailable")
        page.evaluate("Clerk.session = null; Clerk.user = null; window.changeIdentity();")
        expect(label).to_have_text("Sign in to track your progress.")
        assert not errors, errors
        browser.close()
finally:
    server.shutdown()
    server.server_close()

print("PASS: verified XP and next level, offline and sign-out states, and no public ranking requests.")
