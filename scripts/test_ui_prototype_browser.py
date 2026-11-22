"""Exercise unified Generator/Builder flows, fail-closed B-R authority, outlines, zoom, and outage recovery."""
from copy import deepcopy
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
UNRESOLVED = "Unresolved fragment."
ORIGINAL = "The robins sings."
CORRECTED = "The robins sing."
OUT = Path(os.environ.get("SYNTUTOR_UI_SCREENSHOTS", "/tmp/syntutor-m10-browser"))
OUT.mkdir(parents=True, exist_ok=True)


def build_tree_envelope(sentence, verb_word):
    """Clone the reviewed br-02 canonical tree envelope with explicit word leaves for fixture sentences."""
    env = deepcopy(CANONICAL)
    env["sentence"] = sentence
    env["tokens"][2]["text"] = verb_word
    env["tokens"][2]["char_span"] = [11, 11 + len(verb_word)]
    env["root"] = {
        "id": "fixture-s",
        "label": "S",
        "token_span": [0, 3],
        "children": [
            {
                "id": "fixture-np",
                "label": "NP",
                "token_span": [0, 2],
                "children": [
                    {"id": "fixture-det", "label": "DET", "token_span": [0, 1], "children": [{"id": "fixture-w0", "word": "The", "token_span": [0, 1]}]},
                    {"id": "fixture-n", "label": "N", "token_span": [1, 2], "children": [{"id": "fixture-w1", "word": "robins", "token_span": [1, 2]}]},
                ],
            },
            {
                "id": "fixture-vp",
                "label": "VP",
                "token_span": [2, 3],
                "children": [
                    {"id": "fixture-v", "label": "V", "token_span": [2, 3], "children": [{"id": "fixture-w2", "word": verb_word, "token_span": [2, 3]}]},
                ],
            },
        ],
    }
    return env, "fixture-w1", "fixture-w2"


def parse(text):
    raw_tokens = list(re.finditer(r"\w+|[^\w\s]", text))
    tags = ("DT", "NNS", "VB", ".") if len(raw_tokens) >= 4 else ("NN", "NN", ".")
    tokens = [
        {"index": i, "t": m.group(), "start": m.start(), "end": m.end(), "pos": tags[min(i, len(tags) - 1)]}
        for i, m in enumerate(raw_tokens)
    ]
    leaves = [
        {"id": f"n{i+1}", "type": token["pos"], "surface": token["t"], "span": [i, i + 1]}
        for i, token in enumerate(tokens)
    ]
    tree = {"id": "n0", "type": "S", "surface": text, "span": [0, len(tokens)], "children": leaves}
    nodes = {n["id"]: n for n in [tree, *leaves]}
    details = {
        k: {**n, "parent": "n0" if k != "n0" else None, "status": "valid", "role": "fixture"}
        for k, n in nodes.items()
    }
    base_payload = {
        "tree": tree,
        "nodes": nodes,
        "node_details": details,
        "explainers": {},
        "meta": {"target_sentence": 1, "sentence_count": 1, "backend": "fixture"},
        "parse": {"text": text, "tokens": tokens, "sentences": [{"start": 0, "end": len(text), "ordinal": 1}]},
    }

    if text == UNRESOLVED:
        return {
            **base_payload,
            "summary": {"violations": [], "constraints_fired": [], "valid": True, "verdict": "grammatical"},
            "br_analysis": {"status": "unresolved"},
            "explanation_evidence": {"status": "UNRESOLVED", "channels": {}},
        }

    if text == ORIGINAL:
        working, subj_node_id, verb_node_id = build_tree_envelope(text, "sings")
        details["n3"].update(
            status="error",
            constraint="C-SUBJECT-AGREEMENT",
            remediation={"edit": {"start": 2, "end": 3, "text": "sing"}},
        )
        finding_text = "The plural subject 'The robins' does not agree with the singular verb 'sings'. Use 'sing' instead."
        return {
            **base_payload,
            "summary": {
                "violations": ["C-SUBJECT-AGREEMENT"],
                "constraints_fired": ["C-SUBJECT-AGREEMENT"],
                "valid": False,
                "verdict": "ungrammatical",
            },
            "br_analysis": {"status": "unresolved", "working_tree": working},
            "learner_analysis": {
                "verdict": "ungrammatical",
                "sentence_text": finding_text,
                "revision": {
                    "text": "The robins sing.",
                    "impact": {"whole_sentence_clean": True},
                },
                "findings": [
                    {
                        "id": "f-sva",
                        "rule": "C-SUBJECT-AGREEMENT",
                        "text": finding_text,
                        "node_ids": [verb_node_id],
                        "related_node_ids": [subj_node_id],
                    }
                ],
                "nodes": {
                    verb_node_id: {"error": True, "findings": ["f-sva"], "text": finding_text},
                    subj_node_id: {"related": True, "findings": ["f-sva"], "text": "Plural subject head governing verb agreement."},
                },
            },
            "explanation_evidence": {
                "status": "SUPPORTED",
                "channels": {},
                "supported_local_findings": [
                    {"id": "f-sva", "rule": "C-SUBJECT-AGREEMENT", "text": finding_text}
                ],
            },
        }

    canonical, _, _ = build_tree_envelope(text, "sing")
    return {
        **base_payload,
        "summary": {"violations": [], "constraints_fired": [], "valid": True, "verdict": "grammatical"},
        "br_analysis": {"status": "normalized", "tree": canonical},
        "learner_analysis": {
            "verdict": "grammatical",
            "sentence_text": "The plural subject 'The robins' agrees with the plural verb 'sing'.",
            "findings": [],
            "nodes": {},
        },
        "explanation_evidence": {"status": "SUPPORTED", "channels": {}},
    }


def dismiss_onboarding(page):
    skip = page.locator("#onboarding .onboarding-skip")
    try:
        skip.wait_for(state="visible", timeout=1500)
        skip.click()
    except Exception:
        pass


def submit_sentence(page, text):
    with page.expect_response(
        lambda r: r.url.endswith("/api/parse") and r.request.method == "POST",
        timeout=15000,
    ):
        page.locator("#inputText").evaluate(
            """(el, value) => {
              el.removeAttribute('readonly');
              el.value = value;
              el.dispatchEvent(new Event('input', { bubbles: true }));
              el.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', ctrlKey: true, bubbles: true }));
            }""",
            text,
        )


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
            page = browser.new_page(
                viewport={"width": width, "height": height},
                has_touch=name == "mobile",
                reduced_motion="reduce",
            )
            page.add_init_script("localStorage.setItem('syntutor_onboarding_seen', '1')")
            if name == "tablet":
                page.add_init_script("localStorage.setItem('syntutor_theme', 'dark')")
            fail_catalogs = {"/content/lessons/course.json", "/content/quizzes/bank.json"} if name == "desktop" else set()
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
                    request.fulfill(json=result)
                elif url.endswith("/api/explain"):
                    request.fulfill(json={"status": "UNRESOLVED", "channels": {}})
                elif (path := url.removeprefix(base)) in fail_catalogs:
                    fail_catalogs.remove(path)
                    request.fulfill(status=503, json={"error": "Test outage"})
                else:
                    request.continue_()

            page.route("**/*", route)
            page.goto(base, wait_until="domcontentloaded")
            page.evaluate("""async () => {
              const src = document.querySelector('script[type="module"][src*="main.js"]')?.src || '/js/main.js';
              await import(src);
            }""")
            dismiss_onboarding(page)

            # 1. Fail-closed B-R authority: unresolved construction never renders raw Benepar/Penn
            #    categories or the retired parser-diagnostic opt-in button.
            submit_sentence(page, UNRESOLVED)
            notice = page.locator("#treeAuthorityNotice")
            expect(notice).to_be_visible()
            expect(notice).to_contain_text("A Burton-Roberts tree is not available")
            expect(page.locator("#toggleParserDiagnostic")).to_have_count(0)
            expect(page.locator("#treeCanvas")).to_be_hidden()
            expect(page.locator("#canonicalTreeView")).to_be_hidden()

            # 2. Provisional B-R working tree with flagged node, accessible outline, zoom, and grounded explanation.
            submit_sentence(page, ORIGINAL)
            expect(notice).to_be_visible()
            expect(notice).to_contain_text("Provisional B-R working tree")
            canonical_view = page.locator("#canonicalTreeView")
            expect(canonical_view.locator("svg").first).to_be_visible()

            outline = page.locator("#canvasTreeText")
            expect(outline).to_be_visible()
            expect(page.locator("#canvasTreeTextBody")).to_contain_text("sings")

            zoom_in = canonical_view.get_by_role("button", name="Zoom in on syntax tree")
            fit_btn = canonical_view.get_by_role("button", name="Fit syntax tree")
            expect(zoom_in).to_be_visible()
            if name == "mobile":
                zoom_in.tap()
                fit_btn.tap()
            else:
                zoom_in.click()
                fit_btn.click()

            expect(page.locator("#explainNode [data-learner-revision]")).to_contain_text("The robins sing.")

            flagged = canonical_view.locator('svg [data-node-id][data-legacy-issue="true"]').first
            expect(flagged).to_be_visible()
            flagged.focus()
            flagged.press("Enter")
            expect(flagged).to_have_attribute("aria-pressed", "true")
            expect(page.locator("#explainNode")).to_contain_text("does not agree")
            show_full = page.locator("#explainNode [data-learner-reset-selection]")
            expect(show_full).to_be_visible()
            show_full.click()
            expect(flagged).to_have_attribute("aria-pressed", "false")
            expect(page.locator("#explainNode [data-learner-revision]")).to_contain_text("The robins sing.")
            expect(page.locator("#inputText")).to_have_value(ORIGINAL)

            # 3. Canonical B-R tree + unified Generator <-> Syntax Builder handoff.
            submit_sentence(page, CORRECTED)
            expect(notice).to_be_hidden()
            expect(canonical_view.locator("svg").first).to_be_visible()
            expect(page.locator("#inputText")).to_have_value(CORRECTED)
            page.screenshot(path=str(OUT / f"{name}.png"))
            if name == "mobile":
                canonical_view.locator("svg").first.scroll_into_view_if_needed()
                page.screenshot(path=str(OUT / "mobile-canonical.png"))

            explore = page.locator("#exploreBuilderBtn")
            expect(explore).to_be_visible()
            expect(explore).to_contain_text("Syntax builder")
            explore.click()
            expect(page.locator("#builderCanvas")).to_be_visible()
            expect(canonical_view).to_be_hidden()
            expect(explore).to_contain_text("Syntax generator")
            expect(page.locator("#inputText")).to_have_value(re.compile(r"^The robins sing\.?$"))
            explore.click()
            expect(canonical_view.locator("svg").first).to_be_visible()
            expect(page.locator("#builderCanvas")).to_be_hidden()

            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            assert page.evaluate("""async tree => {
                const modUrl = performance.getEntriesByType('resource')
                  .map(r => r.name)
                  .find(u => u.includes('/js/lessons-ui.js')) || '/js/lessons-ui.js';
                const {renderLessonTree} = await import(modUrl);
                const view = renderLessonTree(tree);
                document.body.append(view);
                const result = view.querySelector('svg polygon') !== null
                    && view.querySelector('details').textContent.includes('•')
                    && view.scrollWidth >= view.clientWidth;
                view.remove();
                return result;
            }""", ADVANCED)

            # 4. Desktop 503 outage recovery for Lessons and Quizzes catalogs.
            if name == "desktop":
                for view_name, container, title in (
                    ("lessons", "#curriculumView", "Lessons unavailable"),
                    ("quizzes", "#quizzesView", "Assessments unavailable"),
                ):
                    page.locator(f'.sidebar-item[data-view="{view_name}"]').click()
                    surface = page.locator(container)
                    heading = surface.get_by_role("heading", name=title)
                    expect(heading).to_be_focused()
                    expect(surface).to_have_attribute("aria-busy", "false")
                    expect(surface.get_by_role("button", name="Back to Syntax Studio")).to_be_visible()
                    surface.get_by_role("button", name="Try again").click()
                    expect(surface.get_by_role("heading", level=1)).not_to_have_text(title)
                    expect(surface).to_have_attribute("aria-busy", "false")
            assert not errors, errors
            page.close()
        browser.close()
finally:
    server.shutdown()
    server.server_close()

print("PASS: fail-closed B-R authority, provisional finding explanation, canonical tree & unified Builder handoff, outline, zoom, reduced-motion, outage recovery, and desktop/tablet/mobile layout.")
