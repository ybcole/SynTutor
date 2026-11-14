"""Verify the Chapter 2 pilot through the static Lessons app."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads((ROOT / 'web/content/lessons/br-02-pilot.json').read_text())


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

        page.goto(f'{base}/?preview=br-02#lesson/br-02/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name=PILOT['title'], exact=True)).to_be_visible()
        expect(view.get_by_role('heading', name='Two groups, two functions')).to_be_visible()
        opening = submit('opening', 2)
        expect(opening.get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
        expect(opening.get_by_text('Correct answer:', exact=False)).to_have_count(0)
        view.get_by_role('button', name='Next →', exact=True).click()
        view.get_by_role('button', name='lantern', exact=True).click()
        expect(view.get_by_role('status')).to_contain_text('Continue through')
        view.get_by_role('button', name='stairs', exact=True).press('Enter')
        expect(view.get_by_role('status')).to_contain_text('completes the subject')
        view.get_by_role('button', name='Next →', exact=True).click()
        view.get_by_role('button', name='Trace the NP inside VP').click()
        expect(view.locator('.constituent-diagram .lesson-tree-observation')).to_contain_text('Its parent is VP')
        exercise = view.get_by_role('region', name='Attach the NP inside the predicate')
        exercise.get_by_role('button', name='Check my tree').click()
        expect(exercise.locator('.first-tree-footer [role=status]')).to_contain_text('still detached')
        exercise.get_by_role('button', name='Guide me').click()
        exercise.get_by_role('button', name='Attach the lantern group to VP', exact=False).click()
        exercise.get_by_role('button', name='Check my tree').click()
        expect(exercise.locator('.first-tree-footer [role=status]')).to_contain_text('share VP')
        page.reload(wait_until='domcontentloaded')
        exercise.get_by_role('button', name='Check my tree').click()
        expect(exercise.locator('.first-tree-footer [role=status]')).to_contain_text('share VP')
        page.set_viewport_size({'width': 390, 'height': 844})
        view.get_by_role('button', name='Next →', exact=True).click()
        response = view.get_by_role('textbox', name='Your explanation')
        response.fill('Leo is the subject. Loose modifies bolt.')
        page.reload(wait_until='domcontentloaded')
        expect(response).to_have_value('Leo is the subject. Loose modifies bolt.')
        view.get_by_role('button', name='Compare your explanation').click()
        expect(view.get_by_role('status')).to_contain_text('the full complement')
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')
        view.get_by_role('button', name='Next →', exact=True).click()
        view.get_by_text('References and source review', exact=True).click()
        expect(view.get_by_text('AI source check complete. Pilot acceptance is pending.')).to_be_visible()
        view.get_by_role('button', name='Check what you learned', exact=True).click()
        closing = submit('closing', 0)
        expect(closing.get_by_role('status')).to_have_text('Last attempt 0 / 5 · Best 0 / 5')
        expect(closing.get_by_text('0 / 15 lesson XP on this device')).to_be_visible()
        expect(closing.get_by_text('Correct answer:', exact=False)).to_have_count(5)
        closing.get_by_role('button', name='Retake closing check').click()
        closing = submit('closing', 5)
        expect(closing.get_by_text('15 / 15 lesson XP on this device')).to_be_visible()
        view.get_by_role('button', name='← All lessons', exact=True).click()
        expect(view.locator('.lesson-total')).to_have_text('1 / 12 lessons completed · 15 lesson XP')
        expect(view.locator('.lesson-module').get_by_role('heading', name=PILOT['title'], exact=True)).to_have_count(1)
        page.goto(f'{base}/?preview=br-01#lesson/br-01/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name='Sentence structure: constituents', exact=True)).to_be_visible()
        view.get_by_role('button', name='← All lessons', exact=True).click()
        expect(view.locator('.lesson-module').get_by_role('heading', name='Sentence structure: constituents', exact=True)).to_have_count(1)
        page.goto(f'{base}/#lesson/br-02/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name='Introduction to Subject and Predicate')).to_be_visible()
        expect(view.get_by_role('heading', name=PILOT['title'], exact=True)).to_have_count(0)
        assert not errors and not parses, (errors, parses)
        browser.close()
finally:
    server.shutdown()

print('PASS: book titles, Chapter 2 scope and feedback, saved V2 repair, mobile transfer, 0/5 completion, eligible retake, and published isolation.')
