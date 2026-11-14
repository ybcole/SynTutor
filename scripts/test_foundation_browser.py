"""Use the actual chapter player with an intercepted fixture course."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright
from test_foundation_fixture import fixture_course

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('/tmp/syntutor-foundation-browser')
OUT.mkdir(exist_ok=True)


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=ROOT / 'web'))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}'


def route(request):
    url = request.request.url
    if url.startswith('https://esm.sh/'):
        request.fulfill(content_type='application/javascript', body='export const createClient = () => null;')
    elif not url.startswith(base):
        request.abort()
    elif '/content/lessons/course.json' in url:
        request.fulfill(json=fixture_course())
    else:
        assert '/api/parse' not in url
        request.continue_()


try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.add_init_script("localStorage.setItem('syntutor_onboarding_seen', '1')")
        page.route('**/*', route)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        view = page.locator('#curriculumView')

        def open_section(section):
            page.goto(f'{base}/#lesson/br-02/{section}', wait_until='domcontentloaded')
            expect(view.locator('.lesson-stage-body > h2')).to_be_visible()

        def submit(kind, count, correct, *, start=0):
            heading = 'Check what you know' if kind == 'opening' else 'Check what you learned'
            panel = view.get_by_role('region', name=heading, exact=True)
            for i in range(start, count):
                expect(panel.get_by_text(f'Question {i + 1} of {count}', exact=True)).to_be_visible()
                button = 'Next question →'
                if i == count - 1:
                    button = 'Finish opening check' if kind == 'opening' else 'Submit closing check'
                panel.get_by_role('radio', name=f'Fixture option {"A" if i < correct else "B"}').check()
                panel.get_by_role('button', name=button, exact=True).click()
            return panel

        open_section('closing-check')
        expect(view.get_by_text('Answers overview')).to_have_count(0)
        panel = submit('closing', 6, 0)
        expect(panel.get_by_role('status')).to_have_text('Last attempt 0 / 6 · Best 0 / 6')
        expect(panel.get_by_text('Visit the remaining required sections')).to_be_visible()
        for section in ['concepts', 'worked-example', 'application', 'recap']:
            open_section(section)
        open_section('introduction')
        intro = view.get_by_role('region', name='Check what you know', exact=True)
        intro.get_by_role('radio', name='Fixture option A').check()
        intro.get_by_role('button', name='Next question →').click()
        page.reload(wait_until='domcontentloaded')
        intro = submit('opening', 5, 2, start=1)
        expect(intro.get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
        expect(intro.get_by_text('Correct answer', exact=False)).to_have_count(0)
        expect(intro.get_by_text('XP', exact=False)).to_have_count(0)

        open_section('closing-check')
        expect(view.get_by_text('Visit the remaining required sections')).to_have_count(0)
        panel.get_by_role('button', name='Retake closing check').click()
        panel = submit('closing', 6, 3)
        expect(panel.get_by_role('status')).to_have_text('Last attempt 3 / 6 · Best 3 / 6')
        expect(panel.get_by_text('7 / 15 lesson XP on this device')).to_be_visible()
        expect(panel.get_by_text('Correct answer: Fixture option A.', exact=False)).to_have_count(6)
        page.screenshot(path=OUT / 'closing-desktop.png', full_page=True)

        page.set_viewport_size({'width': 390, 'height': 844})
        panel.get_by_role('button', name='Retake closing check').click()
        panel = submit('closing', 6, 1)
        expect(panel.get_by_role('status')).to_have_text('Last attempt 1 / 6 · Best 3 / 6')
        expect(panel.get_by_text('7 / 15 lesson XP on this device')).to_be_visible()
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')
        page.screenshot(path=OUT / 'closing-mobile.png', full_page=True)
        view.get_by_role('button', name='← All lessons', exact=True).click()
        expect(view.locator('.lesson-total')).to_have_text('1 / 12 lessons completed · 7 lesson XP')
        assert not errors, errors
        browser.close()
finally:
    server.shutdown()

print('PASS: revised read-ahead, opening score without feedback, draft reload, zero-score completion, answer review and eligible retakes on desktop and mobile.')
