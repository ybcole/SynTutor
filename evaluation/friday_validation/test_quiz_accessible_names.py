"""QA-012: Assessment actions need contextual accessible names."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


server = ThreadingHTTPServer(
    ("127.0.0.1", 0),
    partial(Quiet, directory=str(Path("web").resolve())),
)
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()

base = f"http://127.0.0.1:{server.server_port}"

try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)

        try:
            page = browser.new_page()
            page.add_init_script(
                "localStorage.setItem('syntutor_onboarding_seen','1')"
            )

            def route(request):
                if request.request.url.startswith("https://esm.sh/"):
                    request.fulfill(
                        content_type="application/javascript",
                        body="export const createClient = () => null;",
                    )
                elif request.request.url.startswith(base):
                    request.continue_()
                else:
                    request.abort()

            page.route("**/*", route)
            page.goto(base, wait_until="domcontentloaded")
            page.evaluate(
                "async () => { await import('/js/main.js'); }"
            )

            page.locator(
                '.sidebar-item[data-view="quizzes"]'
            ).click()

            cards = page.locator(
                "#quizzesView article.curriculum-card"
            )
            cards.first.wait_for(state="visible")

            failures = []

            for index in range(cards.count()):
                card = cards.nth(index)
                title = card.locator("h2").inner_text().strip()
                button = card.locator("button.lesson-primary")

                action = button.inner_text().strip()
                snapshot = button.aria_snapshot()

                if (
                    title.casefold() not in snapshot.casefold()
                    or action.casefold() not in snapshot.casefold()
                ):
                    failures.append((title, snapshot))

            print("Assessment cards checked:", cards.count())
            print("Buttons missing contextual names:", len(failures))

            for title, snapshot in failures:
                print(f"FAIL: {title}")
                print(f"  Accessible snapshot: {snapshot.strip()}")

            if failures:
                raise SystemExit(1)

            print("PASS: All assessment actions have contextual names.")

        finally:
            browser.close()

finally:
    server.shutdown()
    server.server_close()
    thread.join()
