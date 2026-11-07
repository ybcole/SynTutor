"""Real browser/API parity smoke; requires parser models and Playwright Chromium.

Only authentication/third-party requests and advisory CoLA are disabled. Parsing,
canonical serialization, HTTP evidence composition and DOM rendering are real.
The test selects V2 to exercise the documented supported live transformation.
"""
import json
from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'server'))
import api
from webapp import app
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright

api.classify = lambda text: None
# Explicit fixture mode proves reviewed rendering without promoting synthetic
# records into the production registry.
fixture_mode = '--reviewed-fixture' in sys.argv
if fixture_mode:
    import explanations
    from test_explanations import registry
    fixture = registry()
    fixture['templates'][0]['deep_text'] = 'Synthetic test detail for {surface}.'
    explanations.load_registry = lambda: fixture

server = make_server('127.0.0.1', 0, app, threaded=True)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
base = f'http://127.0.0.1:{server.server_port}'
try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        def route(request_route):
            request = request_route.request
            if request.url.startswith('https://esm.sh/'):
                request_route.fulfill(status=200, content_type='application/javascript', body='export const createClient = () => null;'); return
            if not request.url.startswith(base):
                request_route.abort(); return
            if '/api/parse' in request.url:
                body = request.post_data_json
                body['chapter'] = 2
                request_route.continue_(post_data=json.dumps(body)); return
            request_route.continue_()
        page.route('**/*', route)
        page.goto(base, wait_until='domcontentloaded')
        page.evaluate("async () => { await import('/js/main.js'); }")
        page.locator('#inputText').evaluate("el => { el.removeAttribute('readonly'); el.value = 'The birds sing.'; el.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', ctrlKey: true, bubbles: true })); }")
        page.wait_for_selector('#openCanonicalBuilder', timeout=60000)
        page.wait_for_selector('[data-shared-evidence]')
        generator = page.locator('[data-shared-evidence]').inner_text()
        assert ('Test structure' if fixture_mode else 'A sentence is the largest syntactic unit') in generator, generator
        page.click('#openCanonicalBuilder')
        page.click('#builderSnap')
        page.wait_for_selector('[data-shared-evidence]', timeout=30000)
        builder = page.locator('[data-shared-evidence]').inner_text()
        assert builder == generator, (generator, builder)
        # A hostile explanation is displayed as text, never interpreted as HTML.
        page.evaluate("""async () => {
          const {renderEvidence} = await import('/js/explanation-evidence.js');
          renderEvidence({status:'EXPLAINED',channels:{structural:[{text:'<img src=x onerror=alert(1)>',sources:[],deep_text:'details'}]}});
        }""")
        assert page.locator('[data-shared-evidence] img').count() == 0
        assert page.locator('[data-shared-evidence] details').count() == 1
        assert not errors, errors
        print('PASS: Generator/Builder real HTTP evidence and rendered text match; HTML injection blocked. Fixture mode:', fixture_mode)
        browser.close()
finally:
    server.shutdown(); server.server_close(); thread.join(2)
