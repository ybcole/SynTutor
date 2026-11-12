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


def candidate(body):
    text = body["text"]
    selected = body.get("sentence_index", 0)
    offset = selected * (len(TEXT) + 1)
    rows = [
        {"index": i, "t": match.group(), "start": offset + match.start(),
         "end": offset + match.end(), "pos": tag}
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
        "meta": {"target_sentence": selected + 1, "sentence_count": text.count(TEXT),
                 "backend": "fixture", "cambridge_variety": body.get("variety")},
        "br_analysis": {"status": "unresolved", "reasons": [
            {"code": "PROFILE_MAPPING_NOT_APPROVED", "detail": "Source mapping not reviewed."}
        ]},
        "parse": {"text": TEXT, "tokens": rows, "sentences": [
            {"start": i * (len(TEXT) + 1), "end": i * (len(TEXT) + 1) + len(TEXT), "ordinal": i + 1}
            for i in range(text.count(TEXT))
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
        context = browser.new_context()
        for width, height in ((1280, 900), (390, 800)):
            page = context.new_page()
            page.set_viewport_size({"width": width, "height": height})
            page.add_init_script("localStorage.setItem('syntutor_onboarding_seen', '1')")

            parse_requests = []

            def route(request):
                url = request.request.url
                if url.startswith("https://esm.sh/"):
                    request.fulfill(content_type="application/javascript",
                                    body="export const createClient = () => null;")
                elif url.endswith("/api/parse"):
                    body = request.request.post_data_json
                    parse_requests.append(body)
                    request.fulfill(json=candidate(body))
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
            assert "variety" not in parse_requests[0]
            setting = page.get_by_label("English variety")
            expect(setting).to_be_visible()
            expect(setting).to_have_value("")
            page.locator("#inputText").evaluate("""(el, text) => {
                el.value = text;
                el.dispatchEvent(new KeyboardEvent('keydown', {
                  key:'Enter', ctrlKey:true, bubbles:true
                }));
            }""", f"{TEXT} {TEXT}")
            second = page.locator('.sentence-span[data-sent-idx="1"]')
            expect(second).to_be_visible()

            with page.expect_request(lambda r: r.url.endswith("/api/parse")) as changed:
                setting.select_option("standard_english")
            assert changed.value.post_data_json["variety"] == "standard_english"
            expect(page.locator("#loadingIndicator")).not_to_have_class(re.compile("visible"))
            expect(page.locator('.sentence-span[data-sent-idx="0"]')).to_have_class(re.compile("is-active"))
            with page.expect_request(lambda r: r.url.endswith("/api/parse")) as navigated:
                second.click()
            assert navigated.value.post_data_json["sentence_index"] == 1
            assert navigated.value.post_data_json["variety"] == "standard_english"
            expect(second).to_have_class(re.compile("is-active"))

            with page.expect_request(lambda r: r.url.endswith("/api/parse")) as cleared:
                setting.select_option("")
            assert cleared.value.post_data_json["sentence_index"] == 1
            assert "variety" not in cleared.value.post_data_json
            expect(page.locator("#loadingIndicator")).not_to_have_class(re.compile("visible"))
            expect(second).to_have_class(re.compile("is-active"))
            page.close()
        browser.close()
finally:
    server.shutdown()
    server.server_close()
print("PASS: raw diagnostics stay opt-in and English variety follows the selected sentence on desktop and mobile.")
