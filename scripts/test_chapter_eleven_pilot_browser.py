"""Verify the Chapter 11 pilot through the static Lessons app."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads((ROOT / 'web/content/lessons/br-11-pilot.json').read_text())


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=ROOT / 'web'))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}'

try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.add_init_script("localStorage.setItem('syntutor_onboarding_seen','1')")
        errors, parses = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: parses.append(request.url) if '/api/parse' in request.url else None)

        def route(request):
            if request.request.url.startswith('https://esm.sh/'):
                request.fulfill(content_type='application/javascript', body='export const createClient = () => null;')
            elif request.request.url.startswith(base):
                request.continue_()
            else:
                request.abort()

        page.route('**/*', route)
        view = page.locator('#curriculumView')

        def submit(kind, score):
            name = 'Check what you know' if kind == 'opening' else 'Check what you learned'
            panel = view.get_by_role('region', name=name, exact=True)
            for i, question in enumerate(PILOT['revised_assessment'][kind]):
                answer = question['answer'] if i < score else next(o['id'] for o in question['options'] if o['id'] != question['answer'])
                panel.locator(f'input[value="{answer}"]').check()
                label = 'Next question →' if i < 4 else f'{"Finish" if kind == "opening" else "Submit"} {kind} check'
                panel.get_by_role('button', name=label, exact=True).click()
            return panel

        page.goto(f'{base}/?preview=br-11#lesson/catalog', wait_until='domcontentloaded')
        chapter = view.locator('.lesson-module').filter(has=page.get_by_role('heading', name=PILOT['title'], exact=True))
        chapter.get_by_role('button', name='Start lesson', exact=True).click()
        opening = submit('opening', 2)
        expect(opening.get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
        expect(opening.get_by_text('Correct answer:', exact=False)).to_have_count(0)
        expect(view.get_by_text('lesson XP', exact=False)).to_have_count(0)

        next_page = view.get_by_role('button', name='Next →', exact=True)
        next_page.click()
        expect(view.get_by_text('S → S and S', exact=True)).to_be_visible()
        next_page.click()
        view.get_by_role('button', name='Reuse the first result').press('Enter')
        expect(view.locator('.lesson-tree-observation')).to_contain_text('first input')
        expect(view.locator('.lesson-tree-outline')).to_contain_text('Mina waves')

        page.set_viewport_size({'width': 390, 'height': 844})
        next_page.click()
        apply = view.get_by_role('button', name='Apply the rule', exact=True)
        left = view.get_by_label('First input')
        right = view.get_by_label('Second input')
        feedback = view.get_by_role('status')
        apply.press('Enter')
        expect(feedback).to_contain_text('Choose both inputs first')
        left.select_option('Iris rests and')
        right.select_option('Leo waits')
        apply.click()
        expect(feedback).to_contain_text('needs a complete sentence')
        left.select_option('Iris rests')
        apply.click()
        expect(feedback).to_contain_text('[S [S Iris rests] and [S Leo waits]]')
        view.get_by_role('button', name='Use this result again').press('Enter')
        left.select_option('Iris rests and Leo waits')
        right.select_option('Mina waves')
        apply.click()
        expect(feedback).to_contain_text('[S [S [S Iris rests] and [S Leo waits]] and [S Mina waves]]')
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')

        next_page.click()
        expect(view.get_by_text('this toy grammar has no derivation', exact=False)).to_be_visible()
        next_page.click()
        view.get_by_role('button', name='← All lessons', exact=True).click()
        chapter.get_by_role('button', name='Resume lesson', exact=True).click()
        expect(page).to_have_url(f'{base}/?preview=br-11#lesson/br-11/application')
        view.get_by_text('Check the derivation').click()
        expect(view.get_by_text('[S [S Mina waves] and [S Leo waits]]', exact=True)).to_be_visible()
        next_page.click()
        view.get_by_text('References and source review', exact=True).click()
        expect(view.get_by_text('Chapter 11 · printed p. 266', exact=False)).to_be_visible()
        view.get_by_role('button', name='Check what you learned', exact=True).click()
        closing = submit('closing', 3)
        expect(closing.get_by_role('status')).to_have_text('Last attempt 3 / 5 · Best 3 / 5')
        expect(closing.get_by_text('9 / 15 lesson XP on this device')).to_be_visible()
        expect(closing.get_by_text('Correct answer:', exact=False)).to_have_count(5)
        closing.get_by_role('button', name='Retake closing check').click()
        closing = submit('closing', 5)
        expect(closing.get_by_text('15 / 15 lesson XP on this device')).to_be_visible()

        page.goto(f'{base}/#lesson/br-11/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name='From sentence lists to grammars', exact=True)).to_be_visible()
        assert not errors and not parses, (errors, parses)
        browser.close()
finally:
    server.shutdown()

print('PASS: Chapter 11 rule inputs, preserved recursive grouping, 390px layout, resume, scores and published isolation.')
