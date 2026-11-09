"""Browser regression: unresolved B-R must NOT silently expose Penn tree.

Runs against a fixture API without model downloads. A raw diagnostic is
available only after an explicit user action.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import os
import re

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TEXT = "The robins sings."


def candidate():
    rows = [
        {"index": i, "t": match.group(), "start": match.start(),
         "end": match.end(), "pos": tag}
        for i, (match, tag) in enumerate(zip(
            re.finditer(r"\w+|[^\w\s]", TEXT), ("DT", "NNS", "VBZ", ".")
        ))
    ]
    leaves = [
        {"id": f"n{i+1}", "type": t["pos"], "span": [i, i+1], "surface": t["t"]}
        for i, t in enumerate(rows)
    ]
    tree = {"id": "n0", "type": "S", "span": [0, len(leaves)],
            "surface": TEXT, "children": leaves}
    nodes = [tree, *leaves]
    return {
        "tree": tree,
        "nodes": {n["id"]: n for n in nodes},
        "node_details": {n["id"]: {"status": "valid", "role": "fixture", **n} for n in nodes},
        "summary": {"valid": False, "violations": [], "constraints_fired": [],
                    "verdict": "unverified"},
        "meta": {"target_sentence": 1, "sentence_count": 1, "backend": "fixture"},
        "br_analysis": {"status": "unresolved", "reasons": [
            {"code": "PROFILE_MAPPING_NOT_APPROVED", "detail": "Source mapping not reviewed."}
        ]},
        "parse": {"text": TEXT, "tokens": rows, "sentences": [
            {"start": 0, "end": len(TEXT), "ordinal": 1}
        ]},
        "explainers": {},
    }


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


server = ThreadingHTTPServer(
    ("127.0.0.1", 0), partial(QuietHandler, directory=ROOT / "web")
)
Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_port}"

try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=os.getenv("SYNTUTOR_CHROMIUM_BIN")
        )
        for width, height in ((1280, 900), (390, 800)):
            page = browser.new_page(viewport={"width": width, "height": height})
            page.add_init_script("localStorage.setItem('syntutor_onboarding_seen', '1')")

            def route(request):
                url = request.request.url
                if url.startswith("https://esm.sh/"):
                    request.fulfill(content_type="application/javascript",
                                    body="export const createClient = () => null;")
                elif url.endswith("/api/parse"):
                    request.fulfill(json=candidate())
                elif url.endswith("/api/explain"):
                    request.fulfill(json={"status": "UNRESOLVED", "channels": {}})
                elif url.startswith(base):
                    request.continue_()
                else:
                    request.abort()

            page.route("**/*", route)
            page.goto(base, wait_until="domcontentloaded")
            page.evaluate("async () => { await import('/js/main.js'); }")
            page.locator("#inputText").evaluate("""(el, text) => {
                el.readOnly = false;
                el.value = text;
                el.dispatchEvent(new KeyboardEvent('keydown', {
                  key:'Enter', ctrlKey:true, bubbles:true
                }));
            }""", TEXT)
            toggle = page.locator("#toggleParserDiagnostic")
            expect(toggle).to_be_visible()
            expect(toggle).to_have_attribute("aria-expanded", "false")
            expect(page.locator("#treeCanvas")).to_be_hidden()
            expect(page.locator("#canonicalTreeView")).to_be_hidden()
            toggle.click()
            expect(toggle).to_have_attribute("aria-expanded", "true")
            expect(page.locator("#treeCanvas")).to_be_visible()
            toggle.click()
            expect(page.locator("#treeCanvas")).to_be_hidden()
            page.close()
        browser.close()
finally:
    server.shutdown()
    server.server_close()
print("PASS: unresolved B-R never defaults to raw Benepar labels; diagnostics are opt-in.")
