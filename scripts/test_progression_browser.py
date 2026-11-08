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
  rpc: method => {
    window.progressionCalls.push(method);
    return { abortSignal: async () => {
      if (window.progressionOffline) return { error: { message: 'Unavailable' } };
      if (method === 'get_my_progression') {
        return { data: { xp: 110, lesson_xp: 90, quiz_xp: 20, level: 1 }, error: null };
      }
      if (method !== 'get_my_achievements') throw Error('Unexpected RPC');
      const signedIn = Boolean(Clerk.session);
      return { data: [
        { id: 'first-lesson', title: 'First Lesson', description: 'Complete your first lesson.',
          category: 'learning', reward: 'Badge', icon: 'book',
          unlocked_at: signedIn ? '2026-11-05T00:00:00Z' : null,
          options: [[{ label: 'lesson completed', count: signedIn ? 1 : 0, target: 1 }]] },
        { id: 'gap-spotter', title: 'Gap Spotter', description: 'Recognize a typed gap.',
          category: 'syntax', reward: 'Badge', icon: 'tree', unlocked_at: null,
          options: [[{ label: 'lesson completed', count: 0, target: 1 }],
                    [{ label: 'assessment scored at least 4/5', count: 0, target: 1 }]] },
      ], error: null };
    } };
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
        first = page.locator('[data-achievement="first-lesson"]')
        gap = page.locator('[data-achievement="gap-spotter"]')
        expect(first.locator("time")).to_have_attribute("datetime", "2026-11-05T00:00:00Z")
        expect(first.locator(".achievement-reward")).to_have_text("Badge")
        expect(gap.get_by_text("Or: 0/1 assessment scored at least 4/5")).to_be_visible()

        calls = page.evaluate("window.progressionCalls.slice()")
        assert sorted(calls) == ["get_my_achievements", "get_my_progression"]
        leaderboard.click()
        expect(page.get_by_text("Public rankings are paused.", exact=False)).to_be_visible()
        assert page.evaluate("window.progressionCalls") == calls

        page.evaluate("window.progressionOffline = true")
        achievements.click()
        expect(label).to_contain_text("Verified XP is unavailable")
        expect(page.locator("#achievementsStatsCounter")).to_contain_text("Achievements unavailable")
        page.evaluate("window.progressionOffline = false; Clerk.session = null; Clerk.user = null; window.changeIdentity();")
        expect(label).to_have_text("Sign in to track your progress.")
        expect(page.get_by_text("Sign in to earn these badges.")).to_be_visible()
        expect(first.locator("time")).to_have_count(0)
        page.locator("#achievementsCatTrigger").click()
        page.get_by_role("button", name="Syntax Skill").click()
        expect(gap).to_be_visible()
        expect(first).to_have_count(0)
        assert not errors, errors
        browser.close()
finally:
    server.shutdown()
    server.server_close()

print("PASS: verified XP and next level, badge progress and timestamps, category filtering, offline and sign-out states, and no public ranking requests.")
