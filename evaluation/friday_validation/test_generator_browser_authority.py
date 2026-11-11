"""Independent QA: learner-facing diagnostic authority boundary."""

import os
import socket
import subprocess
import time
from pathlib import Path
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PYTHON = ROOT.parent / "SynTutor/.venv/bin/python"
LOG = Path("/tmp/syntutor-qa-generator-browser.log")

with socket.socket() as sock:
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]

base = f"http://127.0.0.1:{port}"
env = os.environ.copy()
env.pop("PORT", None)
env.update(SYNTUTOR_PORT=str(port), SYNTUTOR_HOST="127.0.0.1")

with LOG.open("w") as log:
    server = subprocess.Popen(
        [str(PYTHON), "server/webapp.py"],
        cwd=ROOT,
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
    )

    try:
        for _ in range(100):
            if server.poll() is not None:
                raise RuntimeError(f"Flask exited; inspect {LOG}")
            try:
                with urlopen(base, timeout=1):
                    break
            except Exception:
                time.sleep(0.2)
        else:
            raise RuntimeError("Flask startup timed out")

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                errors = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.add_init_script(
                    "localStorage.setItem('syntutor_onboarding_seen','1')"
                )

                def route(r):
                    if r.request.url.startswith("https://esm.sh/"):
                        r.fulfill(
                            content_type="application/javascript",
                            body="export const createClient = () => null;",
                        )
                    elif r.request.url.startswith(base):
                        r.continue_()
                    else:
                        r.abort()

                page.route("**/*", route)
                page.goto(base, wait_until="domcontentloaded")
                page.evaluate(
                    "async () => { await import('/js/main.js'); }"
                )

                with page.expect_response(
                    lambda r: r.url.endswith("/api/parse"),
                    timeout=120000,
                ) as parsed:
                    page.locator("#inputText").evaluate("""el => {
                        el.removeAttribute('readonly');
                        el.value = 'Can she swims?';
                        el.dispatchEvent(new KeyboardEvent('keydown', {
                            key: 'Enter', ctrlKey: true, bubbles: true
                        }));
                    }""")

                assert parsed.value.status == 200
                page.locator("#canonicalTreeView").wait_for(
                    state="visible", timeout=30000
                )

                body = page.locator("body").inner_text().lower()
                assert "two full parts" not in body, (
                    "Legacy run-on advice leaked into initial UI"
                )

                node = page.locator(
                    '#canonicalTreeView '
                    '[aria-label="Inspect Burton-Roberts word for swims"]'
                ).first

                assert node.count() == 1

                with page.expect_response(
                    lambda r: r.url.endswith("/api/explain"),
                    timeout=30000,
                ) as explained:
                    node.press("Enter")

                assert explained.value.status == 200
                page.locator(
                    "#explainNode [data-shared-evidence]"
                ).wait_for(timeout=30000)

                shown = page.locator("#explainNode").inner_text()
                assert "swims" in shown.lower()
                assert "two full parts" not in shown.lower()
                assert "without punctuation or a conjunction" not in shown.lower()
                assert page.locator("#treeCanvas").is_hidden()
                assert not errors, errors

                print("PASS: legacy run-on diagnosis withheld from tested UI route.")
                print("Learner-facing explanation:", shown)
            finally:
                browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
