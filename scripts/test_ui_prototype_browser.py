"""Exercise Generator correction and outline flows with a fixture API."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
from threading import Thread

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
COURSE = json.loads((ROOT / "web/content/lessons/course.json").read_text())
CANONICAL = next(x["worked_example"]["tree"] for x in COURSE["lessons"] if x["lesson_id"] == "br-02")
ADVANCED = next(x["worked_example"]["tree"] for x in COURSE["lessons"] if x["lesson_id"] == "br-09")
ORIGINAL = "The robins sings."
CORRECTED = "The robins sing."
OUT = Path(os.environ.get("SYNTUTOR_UI_SCREENSHOTS", "/tmp/syntutor-m10-browser"))
OUT.mkdir(parents=True, exist_ok=True)


def parse(text):
    tokens = [{"index": i, "t": m.group(), "start": m.start(), "end": m.end(), "pos": tag}
              for i, (m, tag) in enumerate(zip(re.finditer(r"\w+|[^\w\s]", text), ("DT", "NNS", "VB", ".")))]
    leaves = [{"id": f"n{i+1}", "type": token["pos"], "surface": token["t"], "span": [i, i+1]}
              for i, token in enumerate(tokens)]
    tree = {"id": "n0", "type": "S", "surface": text, "span": [0, len(tokens)], "children": leaves}
    nodes = {n["id"]: n for n in [tree, *leaves]}
    broken = text == ORIGINAL
    details = {k: {**n, "parent": "n0" if k != "n0" else None, "status": "valid", "role": "fixture"}
               for k, n in nodes.items()}
    if broken:
        details["n3"].update(status="error", constraint="C-SUBJECT-AGREEMENT",
                             remediation={"edit": {"start": 2, "end": 3, "text": "sing"}})
    canonical = {**CANONICAL, "sentence": text}
    return {"tree": tree, "nodes": nodes, "node_details": details, "explainers": {},
            "summary": {"violations": [], "constraints_fired": [], "valid": not broken,
                        "verdict": "ungrammatical" if broken else "grammatical"},
            "meta": {"target_sentence": 1, "sentence_count": 1, "backend": "fixture"},
            "br_analysis": {"status": "unresolved"} if broken else {"status": "normalized", "tree": canonical},
            "parse": {"text": text, "tokens": tokens, "sentences": [{"start": 0, "end": len(text), "ordinal": 1}]}}


class StaticHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), partial(StaticHandler, directory=ROOT / "web"))
Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{server.server_port}"
try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=os.getenv("SYNTUTOR_CHROMIUM_BIN"))
        for name, width, height in (("desktop", 1440, 1000), ("tablet", 800, 950), ("mobile", 390, 844)):
            page = browser.new_page(viewport={"width": width, "height": height},
                                    has_touch=name == "mobile", reduced_motion="reduce")
            page.add_init_script("localStorage.setItem('syntutor_onboarding_seen', '1')")
            if name == "tablet":
                page.add_init_script("localStorage.setItem('syntutor_theme', 'dark')")
            fail_catalogs = {"/content/lessons/course.json", "/content/quizzes/bank.json"} if name == "desktop" else set()
            fail_preview = name == "desktop"
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))

            def route(request):
                url = request.request.url
                if url.startswith("https://esm.sh/"):
                    request.fulfill(content_type="application/javascript", body="export const createClient = () => null;")
                elif not url.startswith(base):
                    request.abort()
                elif url.endswith("/api/parse"):
                    result = parse(request.request.post_data_json["text"])
                    if result["parse"]["text"] == CORRECTED and preview_failures:
                        preview_failures.pop()
                        result["tree"]["children"][2]["surface"] = "sings"
                    request.fulfill(json=result)
                elif url.endswith("/api/explain"):
                    request.fulfill(json={"status": "UNRESOLVED", "channels": {}})
                elif (path := url.removeprefix(base)) in fail_catalogs:
                    fail_catalogs.remove(path)
                    request.fulfill(status=503, json={"error": "Test outage"})
                else:
                    request.continue_()

            preview_failures = [True] if fail_preview else []
            page.route("**/*", route)
            page.goto(base, wait_until="domcontentloaded")
            page.evaluate("async () => { await import('/js/main.js'); }")
            page.locator("#inputText").evaluate("""(el, text) => {
              el.removeAttribute('readonly'); el.value = text;
              el.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter', ctrlKey: true, bubbles: true}));
            }""", ORIGINAL)
            outline = page.locator("#generatorTreeOutline")
            # With no canonical tree, the parser tree must still be on screen.
            expect(page.locator("#treeCanvas")).to_be_visible()
            expect(outline).to_be_visible()
            outline.locator("summary").click()
            expect(outline.get_by_role("button", name="Zoom in")).to_be_visible()
            zoom = outline.get_by_role("button", name="Zoom in")
            if name == "mobile":
                zoom.tap()
            else:
                zoom.click()
            flagged = outline.get_by_role("button", name="sings (VB) · flagged for review")
            flagged.focus()
            flagged.press("Enter")
            expect(flagged).to_have_attribute("aria-current", "true")
            outline.locator("summary").click()
            page.get_by_role("button", name="Preview suggested fix").click()
            panel = page.locator("#correctionPanel")
            if fail_preview:
                expect(panel.get_by_text("Could not verify a tree for the complete corrected sentence.")).to_be_visible()
                expect(panel.locator(".cp-sentence")).to_have_count(0)
                page.get_by_role("button", name="Preview suggested fix").click()
            expect(panel.locator(".cp-sentence")).to_have_text(CORRECTED)
            expect(panel.locator("del")).to_have_text("sings")
            expect(panel.locator("ins")).to_have_text("sing")
            page.get_by_role("button", name="Explore B-R tree in Builder").click(trial=True)
            panel.get_by_text("Corrected B-R tree", exact=True).click()
            expect(panel.get_by_role("img", name=f"B-R tree for {CORRECTED}")).to_be_visible()
            expect(page.locator("#inputText")).to_have_value(ORIGINAL)
            page.screenshot(path=str(OUT / f"{name}.png"))
            if name == "mobile":
                panel.locator("svg").scroll_into_view_if_needed()
                page.screenshot(path=str(OUT / "mobile-canonical.png"))
            if name == "mobile":
                panel.get_by_role("button", name="Close the correction").click()
                expect(panel).to_be_hidden()
                outline.locator("summary").click()
                expect(flagged).to_be_visible()
            else:
                panel.get_by_role("button", name="Return to original tree").click()
            expect(panel.locator(".cp-sentence")).to_have_count(0)
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            assert page.evaluate("""async tree => {
                const {renderLessonTree} = await import('/js/lessons-ui.js');
                const view = renderLessonTree(tree);
                document.body.append(view);
                const result = view.querySelector('svg polygon') !== null
                    && view.querySelector('details').textContent.includes('•')
                    && view.scrollWidth >= view.clientWidth;
                view.remove();
                return result;
            }""", ADVANCED)
            if name == "desktop":
                for view, container, title in (
                    ("lessons", "#curriculumView", "Lessons unavailable"),
                    ("quizzes", "#quizzesView", "Assessments unavailable"),
                ):
                    page.locator(f'.sidebar-item[data-view="{view}"]').click()
                    surface = page.locator(container)
                    heading = surface.get_by_role("heading", name=title)
                    expect(heading).to_be_focused()
                    expect(surface).to_have_attribute("aria-busy", "false")
                    expect(surface.get_by_role("button", name="Back to Syntax Generator")).to_be_visible()
                    surface.get_by_role("button", name="Try again").click()
                    expect(surface.get_by_role("heading", level=1)).not_to_have_text(title)
                    expect(surface).to_have_attribute("aria-busy", "false")
            assert not errors, errors
            page.close()
        browser.close()
finally:
    server.shutdown()
    server.server_close()

print("PASS: reversible corrected sentence and B-R tree, outline navigation, zoom, reduced-motion preference, and desktop/tablet/mobile layout.")
