"""Real browser/API parity smoke; requires parser models and Playwright Chromium.

Only authentication/third-party requests and advisory CoLA are disabled. Parsing,
canonical serialization, HTTP evidence composition and DOM rendering are real.
The default test uses V2. The FINAL-D1 mode exercises the reported Generator case.
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
working_mode = '--working-tree' in sys.argv
final_mode = '--final-declarative' in sys.argv or working_mode
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
        if final_mode:
            page.add_init_script("localStorage.setItem('syntutor_onboarding_seen', '1')")
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        def route(request_route):
            request = request_route.request
            if request.url.startswith('https://esm.sh/'):
                request_route.fulfill(status=200, content_type='application/javascript', body='export const createClient = () => null;'); return
            if not request.url.startswith(base):
                request_route.abort(); return
            if '/api/parse' in request.url and not final_mode:
                body = request.post_data_json
                body['chapter'] = 2
                request_route.continue_(post_data=json.dumps(body)); return
            request_route.continue_()
        page.route('**/*', route)
        page.goto(base, wait_until='domcontentloaded')
        page.evaluate("async () => { await import('/js/main.js'); }")
        text = 'She is taller than he is.' if working_mode else 'The boy sleeps.' if final_mode else 'The birds sing.'
        with page.expect_response(lambda response: response.url.endswith('/api/parse')) as response:
            page.locator('#inputText').evaluate("""(el, text) => {
                el.removeAttribute('readonly');
                el.value = text;
                el.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', ctrlKey: true, bubbles: true }));
            }""", text)
        if working_mode:
            parsed = response.value.json()
            br = parsed['br_analysis']
            assert br['status'] == 'unresolved' and br['tree'] is None
            assert br['working_tree']['sentence'] == text
            canonical = page.locator('#canonicalTreeView')
            canonical.wait_for(state='visible', timeout=60000)
            assert not page.locator('#treeCanvas').is_visible()
            assert 'working tree' in page.locator('#treeAuthorityNotice').inner_text()
            assert page.locator('#openCanonicalBuilder').count() == 0
            button = canonical.get_by_role('button', name='Inspect Burton-Roberts AP for taller than he is', exact=True).first
            button.press('Enter')
            pane = page.locator('#explainNode')
            assert 'Unresolved internal analysis' in pane.inner_text()
            assert 'requires a resolved analysis' in pane.inner_text()
            assert not errors, errors
            print('PASS: unresolved span remains visible in a B-R working tree with explicit uncertainty.')
            browser.close()
            raise SystemExit(0)
        if final_mode:
            parsed = response.value.json()
            br = parsed.get('br_analysis', {})
            assert parsed['parse']['text'] == text
            assert br.get('status') == 'normalized', (parsed['parse']['parse_string'], br.get('reasons'))
            verb = br['tree']['root']['children'][1]['children'][0]
            assert br['display_labels'][verb['id']] == ['V', '[intrans]', '[pres]']
        page.wait_for_selector('#openCanonicalBuilder', timeout=60000)
        if final_mode:
            canonical = page.locator('#canonicalTreeView')
            canonical.wait_for(state='visible')
            assert not page.locator('#treeCanvas').is_visible()
            svg = canonical.locator('svg')
            # The pan/zoom module moves the SVG outside .lesson-tree-wrap.
            # Its branch strokes and text font must survive that move, or
            # the visible tree becomes disconnected and its labels overlap.
            assert page.evaluate("""() => {
              const svg = document.querySelector('#canonicalTreeView .canonical-layer svg');
              const edges = [...svg.querySelectorAll('.lesson-branch')];
              if (!edges.length || getComputedStyle(svg).fontSize !== '15px') return false;
              if (!edges.every(line => {
                const style = getComputedStyle(line);
                return style.stroke !== 'none' && Number.parseFloat(style.strokeWidth) > 0;
              })) return false;
              const nodes = [...svg.querySelectorAll('g[data-node-id]')];
              return nodes.some(g => g.querySelector('text') && getComputedStyle(g.querySelector('text')).fill !== 'none');
            }"""), 'Canonical B-R viewport lost SVG branch stroke or measured label typography'
            # Verify narrow layout and interactive zoom without changing tree
            # edge coordinates or original leaf order.
            page.set_viewport_size({'width': 390, 'height': 800})
            canonical.get_by_role('button', name='Fit B-R tree').click()
            geometry_before = page.evaluate("""() => {
              const svg = document.querySelector('#canonicalTreeView svg');
              return {
                paths: [...svg.querySelectorAll('.lesson-branch')].map(n => [
                  n.getAttribute('x1'), n.getAttribute('y1'), n.getAttribute('x2'), n.getAttribute('y2')]),
                positions: [...svg.querySelectorAll('g[data-node-id] text')]
                  .filter(t => !t.classList.contains('br-feature-row'))
                  .map(t => t.getAttribute('x')),
              };
            }""")
            # The SVG must preserve the canonical left-to-right word
            # sequence, not just keep connector coordinates nonzero.
            ordered_leaves = page.evaluate("""(root) => {
              const svg = document.querySelector('#canonicalTreeView svg');
              const nodes = [];
              function visit(node) {
                if ('word' in node) nodes.push(node.id);
                else for (const child of node.children || []) visit(child);
              }
              visit(root);
              return nodes.map(id => {
                const group = [...svg.querySelectorAll('g[data-node-id]')]
                  .find(g => g.getAttribute('data-node-id') === id);
                return group && Number(group.querySelector('text')?.getAttribute('x'));
              });
            }""", br['tree']['root'])
            assert all(isinstance(x, (int, float)) and x is not None for x in ordered_leaves), ordered_leaves
            assert all(a < b for a, b in zip(ordered_leaves, ordered_leaves[1:])), ordered_leaves
            canonical.get_by_role('button', name='Zoom in B-R tree').click()
            geometry_after = page.evaluate("""() => {
              const svg = document.querySelector('#canonicalTreeView svg');
              return [...svg.querySelectorAll('.lesson-branch')].map(n => [
                n.getAttribute('x1'), n.getAttribute('y1'), n.getAttribute('x2'), n.getAttribute('y2')]);
            }""")
            assert geometry_before['paths'] == geometry_after
            assert len(geometry_before['positions']) >= 5
            assert not page.locator('#treeCanvas').is_visible()
            page.set_viewport_size({'width': 1440, 'height': 1000})
            canonical.get_by_role('button', name='Fit B-R tree').click()
            assert svg.locator('.br-feature-row').all_text_contents() == ['[intrans]', '[pres]']
            labels = svg.locator('text').all_text_contents()
            assert all(label in labels for label in ('S', 'NP', 'DET', 'ART', 'NOM', 'N', 'VP', 'V', 'sleeps')), labels
            assert all(tag not in labels for tag in ('VBZ', 'DT', 'NN', '.')), labels
            svg.get_by_role('button', name='Inspect Burton-Roberts V for sleeps', exact=True).press('Enter')
            pane = page.locator('#explainNode')
            assert 'spans “sleeps”' in pane.inner_text()
            assert 'Ch5 p. 104' in pane.inner_text()
            canonical.get_by_text('Read the tree as text', exact=True).click()
            word = canonical.locator('details').get_by_role('button', name='Inspect Burton-Roberts word for sleeps')
            word.press('Enter')
            assert word.get_attribute('aria-pressed') == 'true'
            assert 'Ch5 p. 104' in pane.inner_text()
            page.locator('#newSessionBtn').click()
            assert not canonical.is_visible()
            assert not errors, errors
            print('PASS: FINAL-D1 renders the reported sentence and exposes its node evidence.')
            browser.close()
            raise SystemExit(0)
        page.wait_for_selector('[data-shared-evidence]')
        assert page.evaluate("""async () => {
          const { matchesPreviewTokens } = await import('/js/correction.js');
          for (const text of ["The birds sing.", "The birds don't sing.", "The birds (usually) sing."]) {
            const response = await fetch('/api/parse', {
              method: 'POST', headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({text}),
            });
            if (!response.ok || !matchesPreviewTokens(await response.json(), text)) {
              throw Error('Correction token contract failed for ' + text);
            }
          }
          return true;
        }""")
        generator = page.locator('[data-shared-evidence]').inner_text()
        assert ('Test structure' if fixture_mode else 'A sentence is the largest syntactic unit') in generator, generator
        page.evaluate("""async () => {
          const {renderNodeDetail, renderCorrection} = await import('/js/ui.js');
          renderNodeDetail({payload:{explanation_evidence:{}}}, {
            type:'NP',surface:'The birds',status:'valid',role:'diagnostic',
            text:'UNREVIEWED_LINGUISTIC_CLAIM'
          }, {});
          if (document.querySelector('#explainNode').textContent.includes('UNREVIEWED_LINGUISTIC_CLAIM'))
            throw new Error('Legacy prose escaped source gates');
          renderCorrection({book_verified:false,correction:{original_sentence:'She go',corrected_sentence:'She goes'}});
          if (document.querySelector('#explainNode').textContent.includes('Verified correction'))
            throw new Error('Legacy correction presented as verified');
        }""")
        page.click('#openCanonicalBuilder')
        page.click('#builderSnap')
        page.wait_for_selector('[data-shared-evidence]', timeout=30000)
        shared = page.evaluate("async()=>{const m=await import('/js/syntax-builder-ui.js');const b=await import('/js/syntax-builder.js');const tree=b.toCanonicalEnvelope(m.builderModel(),{chapter:2,version:'V2',profile_id:'V2'});const evaluated=await(await fetch('/api/evaluate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tree})})).json();const explained=await(await fetch('/api/explain',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tree})})).json();return {evaluated:evaluated.explanation_evidence,explained};}")
        assert shared['evaluated'] == shared['explained']
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
