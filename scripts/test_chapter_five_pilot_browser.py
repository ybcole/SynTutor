"""Verify the Chapter 5 pilot through the static Lessons app."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads((ROOT / 'web/content/lessons/br-05-pilot.json').read_text())


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

        page.goto(f'{base}/?preview=br-05#lesson/catalog', wait_until='domcontentloaded')
        chapter = view.locator('.lesson-module').filter(has=page.get_by_role('heading', name=PILOT['title'], exact=True))
        expect(chapter.locator('.lesson-module-description')).to_contain_text('particles and ellipsis')
        chapter.get_by_role('button', name='Start lesson', exact=True).click()
        expect(view.get_by_role('heading', name='What does the extra phrase modify?')).to_be_visible()
        opening = submit('opening', 2)
        expect(opening.get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
        expect(opening.get_by_text('Correct answer:', exact=False)).to_have_count(0)
        expect(view.get_by_text('lesson XP', exact=False)).to_have_count(0)

        next_page = view.get_by_role('button', name='Next →', exact=True)
        next_page.click()
        view.get_by_role('radio', name='Beside the basic VP in a higher VP').check()
        expect(view.get_by_role('status')).to_contain_text('That works for the optional repair location')
        view.get_by_role('radio', name='Beside V in the basic VP').check()
        expect(view.get_by_role('status')).to_contain_text('a complement of “put”')
        view.get_by_role('button', name='Trace the resulting location').press('Enter')
        note = view.locator('.constituent-diagram .lesson-tree-observation')
        expect(note).to_contain_text('object predicative')
        expect(view.locator('svg[aria-label="Syntax tree for Mina put the tools in the shed"]')).to_be_visible()

        next_page.click()
        view.get_by_role('button', name='Find the full predicate').click()
        expect(note).to_contain_text('VP₂ covers the inspection and its time')
        view.get_by_text('Tree notation', exact=True).click()
        notation = view.locator('.lesson-notation > dl')
        expect(notation.get_by_text('VP₁', exact=True)).to_be_visible()
        expect(notation.get_by_text('VP₂', exact=True)).to_be_visible()
        exercise = view.get_by_role('region', name='Attach the time adjunct exercise')
        check = exercise.get_by_role('button', name='Check my tree')
        status = exercise.locator('.first-tree-footer [role=status]')
        check.click()
        expect(status).to_contain_text('still detached')
        exercise.locator('#builderCanvas').scroll_into_view_if_needed()
        start, end = page.evaluate("""async () => {
            const { canvasGuideBox } = await import('/js/syntax-builder-ui.js');
            return [{ kind: 'dot', type: 'S' }, { kind: 'phrase', type: 'PP' }].map(target => {
                const box = canvasGuideBox(target);
                return [box.left + box.width / 2, box.top + box.height / 2];
            });
        }""")
        page.mouse.move(*start)
        page.mouse.down()
        page.mouse.move(*end, steps=8)
        page.mouse.up()
        check.click()
        expect(status).to_contain_text('attached to S')
        exercise.get_by_role('button', name='Guide me').click()
        exercise.get_by_role('button', name='Connect the time PP under the outer VP', exact=False).click()
        check.click()
        expect(status).to_contain_text('sisters under the outer VP')
        exercise.get_by_role('button', name='Undo', exact=True).click()
        check.click()
        expect(status).to_contain_text('attached to S')
        exercise.get_by_role('button', name='Connect the time PP under the outer VP', exact=False).click()
        page.reload(wait_until='domcontentloaded')
        check.click()
        expect(status).to_contain_text('sisters under the outer VP')

        page.set_viewport_size({'width': 390, 'height': 844})
        page.evaluate("document.documentElement.dataset.theme = 'dark'")
        next_page.click()
        expect(page).to_have_url(f'{base}/?preview=br-05#lesson/br-05/mobility')
        view.get_by_role('button', name='Read the following adjunct').click()
        expect(note).to_contain_text('follows the basic VP')
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')
        next_page.click()
        view.get_by_role('button', name='Find the preposition').click()
        expect(note).to_contain_text('heads the PP')
        view.get_by_role('button', name='Find the separated particle').click()
        expect(note).to_contain_text('follows the object pronoun')

        next_page.click()
        view.get_by_role('button', name='Find the understood recipient').click()
        expect(note).to_contain_text('E marks the understood recipient')
        expect(view.locator('.lesson-tree-outline').get_by_text('E', exact=True)).to_have_count(1)
        ellipsis = view.locator('svg[aria-label="Syntax tree for Mina gave a map"]')
        expect(ellipsis).to_be_visible()
        expect(ellipsis.locator('[data-node-id="understood"]')).to_have_text('E')
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')

        next_page.click()
        view.get_by_role('button', name='← All lessons', exact=True).click()
        chapter.get_by_role('button', name='Resume lesson', exact=True).click()
        expect(page).to_have_url(f'{base}/?preview=br-05#lesson/br-05/application')
        view.get_by_role('button', name='Read the speaker’s comment').click()
        expect(note).to_contain_text('beside S within a higher S')
        view.get_by_text('Check what “unfortunately” modifies').click()
        expect(view.get_by_text('Draw it beside S, under a higher S.', exact=False)).to_be_visible()

        next_page.click()
        view.get_by_text('References and source review', exact=True).click()
        expect(view.get_by_text('Chapter 5 · printed p. 97', exact=False)).to_be_visible()
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

        page.goto(f'{base}/#lesson/br-05/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name='Adjuncts and two levels of VP', exact=True)).to_be_visible()
        assert not errors and not parses, (errors, parses)
        browser.close()
finally:
    server.shutdown()

print('PASS: Chapter 5 scope and branch feedback, V5 trees and ellipsis, mobile, draft/resume, check scores and XP, and published isolation.')
