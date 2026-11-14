"""Walk the actual localhost pilot and verify its published chapter remains available."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from time import monotonic

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads((ROOT / 'web/content/lessons/br-01-pilot.json').read_text())
OUT = Path('/tmp/syntutor-chapter-one-pilot')
OUT.mkdir(exist_ok=True)


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
        start = monotonic()

        def select(kind, score):
            title = 'Check what you know' if kind == 'opening' else 'Check what you learned'
            panel = view.get_by_role('region', name=title, exact=True)
            questions = PILOT['revised_assessment'][kind]
            for i, question in enumerate(questions):
                answer = question['answer'] if i < score else next(o['id'] for o in question['options'] if o['id'] != question['answer'])
                panel.locator(f'input[value="{answer}"]').check()
                label = 'Next question →'
                if i == len(questions) - 1:
                    label = 'Finish opening check' if kind == 'opening' else 'Submit closing check'
                panel.get_by_role('button', name=label, exact=True).click()
            return panel

        page.goto(f'{base}/?preview=br-01#lesson/br-01/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name='Words form groups')).to_be_visible()
        expect(view.get_by_text('Mina paused [near [the stone arch]].', exact=True)).to_be_visible()
        expect(view.locator('.lesson-key-terms dt')).to_have_count(6)
        opening = select('opening', 3)
        expect(opening.get_by_role('status')).to_have_text('Opening check complete. 3 / 5 correct.')
        expect(opening.get_by_text('Correct answer:', exact=False)).to_have_count(0)
        page.screenshot(path=OUT / 'intro-desktop.png', full_page=True)

        view.get_by_role('button', name='Next →', exact=True).click()
        expect(view.get_by_role('heading', name='Test a group in context')).to_be_visible()
        expect(view.get_by_text('Mina paused near the stone arch.', exact=True)).to_be_visible()
        view.get_by_role('button', name='Next →', exact=True).click()
        for label, caption in [('Trace the landmark', 'all and only'), ('Trace the outer phrase', 'indirectly')]:
            view.get_by_role('button', name=label, exact=True).press('Enter')
            expect(view.locator('.constituent-diagram .lesson-tree-observation')).to_contain_text(caption)
        assert 'undefined' not in view.locator('.constituent-diagram svg').get_attribute('aria-label')
        page.screenshot(path=OUT / 'tree-desktop.png', full_page=True)
        exercise = view.get_by_role('region', name='Build your first tree exercise')
        exercise.get_by_role('button', name='Check my tree').click()
        expect(exercise.locator('.first-tree-footer [role=status]')).to_contain_text('covers exactly')
        exercise.get_by_role('button', name='Guide me').click()
        for step in exercise.locator('.first-tree-guide button').all()[:3]:
            step.click()
        exercise.get_by_role('button', name='Check my tree').click()
        expect(exercise.locator('.first-tree-footer [role=status]')).to_contain_text('Exactly.')
        page.reload(wait_until='domcontentloaded')
        exercise.get_by_role('button', name='Check my tree').click()
        expect(exercise.locator('.first-tree-footer [role=status]')).to_contain_text('Exactly.')

        page.set_viewport_size({'width': 390, 'height': 844})
        view.get_by_role('button', name='Next →', exact=True).click()
        view.get_by_role('button', name='The climber had binoculars').click()
        expect(view.locator('.constituent-diagram .lesson-tree-observation')).to_contain_text('which climber')
        expect(view.get_by_role('button', name='Compare your explanation')).to_be_disabled()
        view.get_by_role('textbox', name='Your explanation').fill('Ivo used the pencil, or the guide had it.')
        page.reload(wait_until='domcontentloaded')
        expect(view.get_by_role('textbox', name='Your explanation')).to_have_value('Ivo used the pencil, or the guide had it.')
        view.get_by_role('button', name='Compare your explanation').click()
        expect(view.get_by_text('When “with a pencil” joins', exact=False)).to_be_visible()
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')
        page.screenshot(path=OUT / 'transfer-mobile.png', full_page=True)
        view.get_by_role('button', name='Next →', exact=True).click()
        view.get_by_text('References and source review', exact=True).click()
        expect(view.get_by_text('AI source check complete. Pilot acceptance is pending.')).to_be_visible()
        view.get_by_role('button', name='Check what you learned', exact=True).click()
        closing = select('closing', 3)
        expect(closing.get_by_role('status')).to_have_text('Last attempt 3 / 5 · Best 3 / 5')
        expect(closing.get_by_text('9 / 15 lesson XP on this device')).to_be_visible()
        expect(closing.get_by_text('Correct answer:', exact=False)).to_have_count(5)
        page.screenshot(path=OUT / 'review-mobile.png', full_page=True)
        closing.get_by_role('button', name='Retake closing check').click()
        closing = select('closing', 5)
        expect(closing.get_by_text('15 / 15 lesson XP on this device')).to_be_visible()
        view.get_by_role('button', name='← All lessons', exact=True).click()
        expect(view.locator('.lesson-total')).to_have_text('1 / 12 lessons completed · 15 lesson XP')
        print(f'Automated interaction time {monotonic() - start:.1f}s, excludes reading and reasoning.')
        page.goto(f'{base}/#lesson/br-01/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name='Introduction to Constituents and Hierarchy')).to_be_visible()
        expect(view.get_by_text('Opening check complete. 3 / 5 correct.')).to_have_count(0)
        assert not errors and not parses, (errors, parses)
        browser.close()
finally:
    server.shutdown()

print('PASS: Chapter 1 pilot, assessments and retakes, authored tree repair and reload, mobile transfer, source disclosure and published chapter isolation.')
