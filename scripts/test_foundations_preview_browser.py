"""Exercise the combined Foundations candidate from the packaged static app."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
PILOTS = {path.name[:5]: json.loads(path.read_text())
          for path in sorted((DIST / 'content/lessons').glob('br-*-pilot.json'))}
assert len(PILOTS) == 11
COURSE = json.loads((DIST / 'content/lessons/course.json').read_text())


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=DIST))
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f'http://127.0.0.1:{server.server_port}'
preview = base + '/?preview=foundations#lesson/'

try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.add_init_script("localStorage.setItem('syntutor_onboarding_seen','1')")
        errors, parser_calls = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))

        def route(request):
            url = request.request.url
            if '/api/parse' in url:
                parser_calls.append(url)
            if url.startswith('https://esm.sh/'):
                request.fulfill(content_type='application/javascript', body='export const createClient = () => null;')
            elif url.startswith(base) and '/api/parse' not in url:
                request.continue_()
            else:
                request.abort()

        page.route('**/*', route)
        view = page.locator('#curriculumView')

        def open_lesson(url, heading=None):
            page.goto(url, wait_until='domcontentloaded')
            expect(view.locator('h1').first).to_be_visible()
            if heading:
                expect(view.locator('.lesson-stage-body > h2')).to_have_text(heading)

        def check_panel(kind):
            label = 'Check what you know' if kind == 'opening' else 'Check what you learned'
            return view.get_by_role('region', name=label, exact=True)

        def submit(id, kind, correct):
            panel = check_panel(kind)
            for index, question in enumerate(PILOTS[id]['revised_assessment'][kind]):
                answer = question['answer'] if index < correct else next(
                    option['id'] for option in question['options'] if option['id'] != question['answer'])
                panel.locator(f'input[value="{answer}"]').check()
                last = 'Finish opening check' if kind == 'opening' else 'Submit closing check'
                panel.get_by_role('button', name=last if index == 4 else 'Next question →', exact=True).click()
            return panel

        # Keep published progress on this device before opening either preview.
        open_lesson(base + '/#lesson/catalog')
        legacy = next(lesson for lesson in COURSE['lessons'] if lesson['lesson_id'] == 'br-02')
        published = {
            f"br-02@{legacy['content_version']}": {
                'completed_at': '2026-11-08T00:00:00Z', 'stage': 5,
                'visited': legacy['completion']['required_stages'],
                'responses': {key: legacy[key]['answer'] for key in ('predict', 'guided', 'transfer', 'exit')},
            },
        }
        page.evaluate("progress => localStorage.setItem('syntutor:lessons:v1:guest', JSON.stringify(progress))", published)
        page.reload(wait_until='domcontentloaded')
        expect(view.locator('.lesson-total')).to_have_text('1 / 12 lessons completed · 15 lesson XP')

        # Start an individual draft before loading the combined preview in this same browser.
        open_lesson(base + '/?preview=br-02#lesson/br-02/introduction')
        individual = check_panel('opening')
        individual.get_by_role('radio').first.check()
        individual.get_by_role('button', name='Next question →', exact=True).click()

        open_lesson(preview + 'catalog')
        expect(view.locator('.lesson-total')).to_have_text('0 / 12 lessons completed · 0 lesson XP')
        expect(view.get_by_role('button', name='Start lesson', exact=True)).to_have_count(11)
        assert view.locator('.lesson-module h2').all_text_contents() == [pilot['title'] for pilot in PILOTS.values()]

        # Load each authored section so a mismatch with an assessment's required IDs is visible.
        for id, pilot in PILOTS.items():
            for section in pilot['revised_assessment']['required_sections']:
                open_lesson(preview + f'{id}/{section}')
                expect(view).to_contain_text('Chapter pilot · progress saved on this device')
                assert page.url.endswith(f'#lesson/{id}/{section}')
            if id == 'br-02':
                open_lesson(preview + f'{id}/introduction')
                expect(check_panel('opening')).to_contain_text('Question 1 of 5')
                panel = submit(id, 'opening', 2)
                expect(panel.get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
                expect(panel.get_by_text('Correct answer:', exact=False)).to_have_count(0)
            if id in {'br-02', 'br-06', 'br-11'}:
                page.set_viewport_size({'width': 390 if id != 'br-02' else 1440, 'height': 844})
                open_lesson(preview + f'{id}/closing-check')
                panel = submit(id, 'closing', 3)
                expect(panel.get_by_role('status')).to_have_text('Last attempt 3 / 5 · Best 3 / 5')
                expect(panel.get_by_text('9 / 15 lesson XP on this device')).to_be_visible()
                assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')
                panel.get_by_role('button', name='Retake closing check').click()
                panel = submit(id, 'closing', 5)
                expect(panel.get_by_text('15 / 15 lesson XP on this device')).to_be_visible()

        open_lesson(preview + 'catalog')
        expect(view.locator('.lesson-total')).to_have_text('3 / 12 lessons completed · 45 lesson XP')
        view.get_by_role('button', name='Grammar and Analysis', exact=True).click()
        cambridge = view.locator('.lesson-module').first
        expect(cambridge.locator('.lesson-prerequisite')).to_have_count(0)
        cambridge.get_by_role('button', name='Start lesson', exact=True).click()
        expect(view.locator('.lesson-stage-body')).to_be_visible()
        expect(view.get_by_text('Chapter pilot · progress saved on this device')).to_have_count(0)

        open_lesson(base + '/?preview=br-02#lesson/br-02/introduction')
        expect(check_panel('opening')).to_contain_text('Question 2 of 5')
        open_lesson(base + '/#lesson/catalog')
        expect(view.locator('.lesson-total')).to_have_text('1 / 12 lessons completed · 15 lesson XP')
        assert view.locator('.lesson-module h2').all_text_contents() != [pilot['title'] for pilot in PILOTS.values()]
        assert not errors and not parser_calls, (errors, parser_calls)
        browser.close()
finally:
    server.shutdown()

print('PASS: eleven pilots, required section routes, isolated drafts and progress, scored checks, Cambridge navigation and packaged published isolation.')
