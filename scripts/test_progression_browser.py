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
  rpc: (method, args) => {
    window.progressionCalls.push(method);
    return { abortSignal: async () => {
      if (window.progressionOffline) return { error: { message: 'Unavailable' } };
      if (method === 'get_my_progression') {
        return { data: { xp: 110, lesson_xp: 90, quiz_xp: 20, level: 1 }, error: null };
      }
      if (method === 'ensure_leaderboard_participation') {
        const enabled = Boolean(window.rankingsEnabled);
        return { data: { enabled, opted_in: enabled && Boolean(window.publicAlias),
          alias: enabled ? (window.publicAlias || null) : null, enrolled_now: false }, error: null };
      }
      if (method === 'get_leaderboard') {
        const enabled = Boolean(window.rankingsEnabled);
        return { data: { enabled, period_start: '2026-11-02T00:00:00Z',
          period_end: args.p_period === 'weekly' ? '2026-11-09T00:00:00Z' : '2027-01-01T00:00:00Z',
          entries: enabled && window.publicAlias
            ? [{ alias: window.publicAlias, xp: 10, rank: 1, lessons_completed: 1, quizzes_completed: 0 }]
            : [],
          opted_in: Boolean(window.publicAlias), my_alias: window.publicAlias || null,
          my_rank: window.publicAlias ? 1 : null }, error: null };
      }
      if (method === 'set_my_leaderboard_preference') {
        window.publicAlias = args.p_opt_in ? args.p_alias : null;
        return { data: null, error: null };
      }
      if (method !== 'get_my_achievements') throw Error('Unexpected RPC: ' + method);
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


def dismiss_onboarding(page):
    skip = page.locator("#onboarding .onboarding-skip")
    try:
        skip.wait_for(state="visible", timeout=1500)
        skip.click()
    except Exception:
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
        page.goto(base, wait_until="domcontentloaded")
        dismiss_onboarding(page)
        page.locator("#sidebarBrandBtn").click()
        achievements = page.locator('.sidebar-item[data-view="achievements"]')
        leaderboard = page.locator('.sidebar-item[data-view="leaderboard"]')
        progress_label = page.locator("#sidebarProgressLabel")
        progress_bar = page.locator("#sidebarProgressBar")

        # Verified XP and level progress are rendered on the sidebar progression meter.
        expect(progress_label).to_have_text("110/220 XP")
        expect(progress_label).to_have_attribute(
            "title",
            "110 total XP; 220 total XP reaches Level 2. 10/120 XP earned within this level.",
        )
        expect(progress_bar).to_be_visible()
        expect(progress_bar).to_have_attribute("max", "120")
        expect(progress_bar).to_have_attribute("value", "10")
        expect(page.locator("#identityLevelBadge")).to_have_text("1")
        expect(page.locator("#identityChip")).to_have_attribute("aria-label", "Test, Level 1, 110 verified XP")

        achievements.click()
        expect(page.locator("#achievementsStatsCounter")).to_have_text("1 of 2 achievements earned")
        first = page.locator('[data-achievement="first-lesson"]')
        gap = page.locator('[data-achievement="gap-spotter"]')
        expect(first.locator("time")).to_have_attribute("datetime", "2026-11-05T00:00:00Z")
        expect(first.locator(".achievement-reward")).to_have_text("Badge")
        expect(gap.get_by_text("Or: 0/1 assessment scored at least 4/5")).to_be_visible()

        calls = page.evaluate("window.progressionCalls.slice()")
        assert "get_my_progression" in calls and "get_my_achievements" in calls, calls

        leaderboard.click()
        expect(page.locator("#leaderboardStatus")).to_have_text("Public rankings are paused.")
        assert "get_leaderboard" in page.evaluate("window.progressionCalls")[len(calls):]

        page.evaluate("window.rankingsEnabled = true")
        page.get_by_label("Ranking period").select_option("seasonal")
        expect(page.locator("#leaderboardStatus")).to_have_text("No learners ranked yet.")

        # Customize alias & join rankings via Leaderboard Settings in the profile menu.
        page.locator("#identityChip").click()
        page.locator("#profileLeaderboardSettings").click()
        settings = page.locator("#leaderboardSettingsModal")
        expect(settings).to_be_visible()
        settings.locator("#leaderboardAlias").fill("TreeLearner")
        settings.locator("#leaderboardJoin").click()
        expect(settings.locator("#leaderboardPreferenceStatus")).to_have_text("Public participation and alias saved.")
        expect(page.locator("#leaderboardEntries")).to_contain_text("TreeLearner")
        expect(page.locator("#leaderboardPodium")).to_contain_text("Rank #1")

        # Opt out of public rankings while preserving private verified XP.
        settings.locator("#leaderboardLeave").click()
        expect(settings.locator("#leaderboardPreferenceStatus")).to_have_text("You opted out of public rankings.")
        settings.locator("#leaderboardSettingsCloseBtn").click()
        expect(settings).to_be_hidden()
        expect(page.locator("#leaderboardEntries").get_by_text("TreeLearner")).to_have_count(0)
        expect(progress_label).to_have_text("110/220 XP")

        # Offline error handling for achievements and sidebar progression.
        page.evaluate("window.progressionOffline = true")
        achievements.click()
        expect(page.locator("#achievementsStatsCounter")).to_contain_text("Achievements unavailable")
        page.evaluate("Clerk.user = { id: 'learner-offline', firstName: 'Test' }; window.changeIdentity()")
        expect(progress_label).to_have_text("Verified XP unavailable.")

        # Sign-out state clears private XP and badge unlock timestamps, while keeping category filtering.
        page.evaluate("window.progressionOffline = false; Clerk.session = null; Clerk.user = null; window.changeIdentity();")
        expect(progress_label).to_have_text("Sign in for verified XP.")
        expect(progress_bar).to_be_hidden()
        expect(page.locator("#achievementsStatsCounter")).to_contain_text("Sign in to track yours")
        expect(first.locator("time")).to_have_count(0)

        page.locator("#achievementsCatPills").get_by_role("button", name="Syntax Skill").click()
        expect(gap).to_be_visible()
        expect(first).to_have_count(0)
        assert not errors, errors
        browser.close()
finally:
    server.shutdown()
    server.server_close()

print("PASS: verified XP and next level, badge progress and timestamps, category filtering, offline and sign-out states, and paused, seasonal, join and leave ranking states.")
