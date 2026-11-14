"""Verify the Chapter 7 pilot through the static Lessons app."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads((ROOT / 'web/content/lessons/br-07-pilot.json').read_text())


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

        page.goto(f'{base}/?preview=br-07#lesson/catalog', wait_until='domcontentloaded')
        chapter = view.locator('.lesson-module').filter(has=page.get_by_role('heading', name=PILOT['title'], exact=True))
        expect(chapter.locator('.lesson-module-description')).to_contain_text('empty determiners')
        chapter.get_by_role('button', name='Start lesson', exact=True).click()
        expect(view.get_by_role('heading', name='What is inside a noun phrase?')).to_be_visible()
        opening = submit('opening', 2)
        expect(opening.get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
        expect(opening.get_by_text('Correct answer:', exact=False)).to_have_count(0)
        expect(view.get_by_text('lesson XP', exact=False)).to_have_count(0)

        next_page = view.get_by_role('button', name='Next →', exact=True)
        next_page.click()
        note = view.locator('.constituent-diagram .lesson-tree-observation')
        outline = view.locator('.lesson-tree-outline')
        view.get_by_role('button', name='Find empty DET').press('Enter')
        expect(note).to_contain_text('ends without a word')
        expect(view.locator('svg [data-node-id="det"]')).to_have_text('DET (empty)')
        expect(outline.get_by_text('DET (empty)', exact=True)).to_have_count(1)
        expect(outline.get_by_text('•', exact=True)).to_have_count(0)
        view.get_by_role('button', name='Compare the pronoun').click()
        expect(outline.get_by_text('DET', exact=True)).to_have_count(0)

        next_page.click()
        exercise = view.get_by_role('region', name='Attach the nominal under NP exercise')
        check = exercise.get_by_role('button', name='Check my tree')
        status = exercise.locator('.first-tree-footer [role=status]')
        check.click()
        expect(status).to_contain_text('still detached')
        exercise.locator('#builderCanvas').scroll_into_view_if_needed()
        start, end = page.evaluate("""async () => {
            const { canvasGuideBox } = await import('/js/syntax-builder-ui.js');
            return [{ kind: 'dot', type: 'DET' }, { kind: 'phrase', type: 'NOM' }].map(target => {
                const box = canvasGuideBox(target);
                return [box.left + box.width / 2, box.top + box.height / 2];
            });
        }""")
        page.mouse.move(*start)
        page.mouse.down()
        page.mouse.move(*end, steps=8)
        page.mouse.up()
        check.click()
        expect(status).to_contain_text('attached to DET')
        exercise.get_by_role('button', name='Guide me').click()
        exercise.get_by_role('button', name='Connect NOM directly under NP', exact=False).click()
        check.click()
        expect(status).to_contain_text('share NP as their parent')
        exercise.get_by_role('button', name='Undo', exact=True).click()
        check.click()
        expect(status).to_contain_text('attached to DET')
        exercise.get_by_role('button', name='Connect NOM directly under NP', exact=False).click()
        page.reload(wait_until='domcontentloaded')
        check.click()
        expect(status).to_contain_text('share NP as their parent')
        view.get_by_role('button', name='Read the inner NP').click()
        expect(note).to_contain_text('sister of PRE-DET')

        page.set_viewport_size({'width': 390, 'height': 844})
        page.evaluate("document.documentElement.dataset.theme = 'dark'")
        next_page.click()
        expect(page).to_have_url(f'{base}/?preview=br-07#lesson/br-07/pre-modifiers')
        view.get_by_role('button', name='Read the larger NOM').click()
        expect(note).to_contain_text('smaller NOM “red kite”')
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')
        next_page.click()
        view.get_by_role('button', name='Trace “applicant for the job”').click()
        expect(note).to_contain_text('smaller NOM includes the noun and PP')
        expect(view.locator('svg [data-node-id="inner"]')).to_have_class('lesson-tree-focus')
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')

        next_page.click()
        view.get_by_role('button', name='← All lessons', exact=True).click()
        chapter.get_by_role('button', name='Resume lesson', exact=True).click()
        expect(page).to_have_url(f'{base}/?preview=br-07#lesson/br-07/application')
        view.get_by_text('Check the attachment').click()
        expect(view.get_by_text('“Ceramic bowls” forms the smaller NOM.', exact=False)).to_be_visible()
        view.get_by_role('button', name='Read the modified pronoun').click()
        expect(note).to_contain_text('pronoun and PP are sisters under NP')
        expect(outline.get_by_text('PP — from Vigan', exact=True)).to_have_count(1)

        next_page.click()
        view.get_by_text('References and source review', exact=True).click()
        expect(view.get_by_text('Chapter 7 · printed p. 156', exact=False)).to_be_visible()
        view.get_by_role('button', name='Check what you learned', exact=True).click()
        closing = submit('closing', 3)
        expect(closing.get_by_role('status')).to_have_text('Last attempt 3 / 5 · Best 3 / 5')
        expect(closing.get_by_text('9 / 15 lesson XP on this device')).to_be_visible()
        expect(closing.get_by_text('Correct answer:', exact=False)).to_have_count(5)
        closing.get_by_role('button', name='Retake closing check').click()
        closing = submit('closing', 5)
        expect(closing.get_by_text('15 / 15 lesson XP on this device')).to_be_visible()
        view.get_by_role('button', name='← All lessons', exact=True).click()
        expect(view.locator('.lesson-total')).to_have_text('1 / 12 lessons completed · 15 lesson XP')

        page.goto(f'{base}/#lesson/br-07/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name='DET and NOM inside NP', exact=True)).to_be_visible()
        assert not errors and not parses, (errors, parses)
        browser.close()
finally:
    server.shutdown()

print('PASS: Chapter 7 empty DET, modifier scope, branch repair, mobile, resume, scores and XP, and published isolation.')
