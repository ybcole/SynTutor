"""Verify the Chapter 10 pilot through the static Lessons app."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads((ROOT / 'web/content/lessons/br-10-pilot.json').read_text())


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

        page.goto(f'{base}/?preview=br-10#lesson/catalog', wait_until='domcontentloaded')
        chapter = view.locator('.lesson-module').filter(has=page.get_by_role('heading', name=PILOT['title'], exact=True))
        chapter.get_by_role('button', name='Start lesson', exact=True).click()
        expect(view.get_by_role('heading', name='Where does tense belong?')).to_be_visible()
        opening = submit('opening', 2)
        expect(opening.get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
        expect(opening.get_by_text('Correct answer:', exact=False)).to_have_count(0)

        next_page = view.get_by_role('button', name='Next →', exact=True)
        next_page.click()
        view.get_by_role('button', name='Find the object gap').press('Enter')
        outline = view.locator('.lesson-tree-outline')
        expect(outline).to_contain_text('V [trans, -tense]')
        expect(outline.get_by_text('• (1)', exact=True)).to_have_count(1)

        next_page.click()
        aux = view.locator('svg [data-node-id="lesson-br-10-worked-root-0"]')
        expect(aux).to_have_text('[-tense]')
        exercise = view.get_by_role('region', name='Attach the lexical VP beside infinitival “to” exercise')
        check = exercise.get_by_role('button', name='Check my tree')
        status = exercise.locator('.first-tree-footer [role=status]')
        check.click()
        expect(status).to_contain_text('still detached')
        exercise.get_by_role('button', name='Guide me').click()
        guide = exercise.get_by_role('button', name='Connect the lexical VP beside “to”', exact=False)
        guide.click()
        check.click()
        expect(status).to_contain_text('shares the higher VP')
        exercise.get_by_role('button', name='Undo', exact=True).click()
        check.click()
        expect(status).to_contain_text('still detached')
        guide.click()
        page.reload(wait_until='domcontentloaded')
        check.click()
        expect(status).to_contain_text('shares the higher VP')

        next_page.click()
        expect(outline.first.get_by_text('•', exact=True)).to_have_count(1)
        view.get_by_role('button', name='Find the controlled subject').click()
        expect(outline.first.get_by_text('NP (1) — Nia', exact=True)).to_have_count(1)
        expect(outline.first.get_by_text('• (1)', exact=True)).to_have_count(1)
        view.get_by_role('button', name='Find the overt subject').click()
        expect(outline.first.get_by_text('NP — Ivo', exact=True)).to_have_count(1)
        view.get_by_role('button', name='Find “what” in C2').click()
        expect(outline.last.get_by_text('C1 (empty)', exact=True)).to_have_count(1)
        expect(outline.last.get_by_text('• (2)', exact=True)).to_have_count(1)
        next_page.click()
        expect(view.get_by_text('In this pattern, P takes the S directly.', exact=False)).to_be_visible()

        page.set_viewport_size({'width': 390, 'height': 844})
        page.evaluate("document.documentElement.dataset.theme = 'dark'")
        next_page.click()
        view.get_by_role('radio', name='The overt subject inside the lower clause').check()
        expect(view.get_by_role('status')).to_contain_text('Look for it in the higher VP')
        view.get_by_role('radio', name='The object of “persuaded”').check()
        expect(view.get_by_role('status')).to_contain_text('controls the silent subject')
        view.get_by_role('button', name='Trace the silent subject').click()
        expect(outline.get_by_text('NP (1) — Ivo', exact=True)).to_have_count(1)
        expect(outline.get_by_text('• (1)', exact=True)).to_have_count(1)
        expect(view.locator('svg [data-node-id="controller"]')).to_contain_text('NP (1)')
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')

        next_page.click()
        view.get_by_role('button', name='← All lessons', exact=True).click()
        chapter.get_by_role('button', name='Resume lesson', exact=True).click()
        expect(page).to_have_url(f'{base}/?preview=br-10#lesson/br-10/application')
        view.get_by_text('Check both analyses').click()
        expect(view.get_by_text('Ren is the higher object', exact=False)).to_be_visible()
        next_page.click()
        view.get_by_text('References and source review', exact=True).click()
        expect(view.get_by_text('Chapter 10 · printed p. 243', exact=False)).to_be_visible()
        view.get_by_role('button', name='Check what you learned', exact=True).click()
        closing = submit('closing', 3)
        expect(closing.get_by_role('status')).to_have_text('Last attempt 3 / 5 · Best 3 / 5')
        expect(closing.get_by_text('9 / 15 lesson XP on this device')).to_be_visible()
        closing.get_by_role('button', name='Retake closing check').click()
        closing = submit('closing', 5)
        expect(closing.get_by_text('15 / 15 lesson XP on this device')).to_be_visible()

        page.goto(f'{base}/#lesson/br-10/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name='The non-finite to-infinitive VP', exact=True)).to_be_visible()
        assert not errors and not parses, (errors, parses)
        browser.close()
finally:
    server.shutdown()

print('PASS: Chapter 10 forms, control indices, Type I and II, branch repair, mobile, resume, scores and XP, and published isolation.')
