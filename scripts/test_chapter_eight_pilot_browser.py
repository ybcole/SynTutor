"""Verify the Chapter 8 pilot through the static Lessons app."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads((ROOT / 'web/content/lessons/br-08-pilot.json').read_text())


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

        page.goto(f'{base}/?preview=br-08#lesson/catalog', wait_until='domcontentloaded')
        chapter = view.locator('.lesson-module').filter(has=page.get_by_role('heading', name=PILOT['title'], exact=True))
        chapter.get_by_role('button', name='Start lesson', exact=True).click()
        expect(view.get_by_role('heading', name='How can one clause contain another?')).to_be_visible()
        opening = submit('opening', 2)
        expect(opening.get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
        expect(opening.get_by_text('Correct answer:', exact=False)).to_have_count(0)
        expect(view.get_by_text('lesson XP', exact=False)).to_have_count(0)

        next_page = view.get_by_role('button', name='Next →', exact=True)
        next_page.click()
        expect(view.get_by_text('Maya thinks [Leo said [Nora closed the gate]].', exact=True)).to_be_visible()
        next_page.click()
        note = view.locator('.constituent-diagram .lesson-tree-observation')
        outline = view.locator('.lesson-tree-outline')
        view.get_by_role('button', name='Find the unfilled C').press('Enter')
        expect(note).to_contain_text('C branch has no word')
        expect(view.locator('svg [data-node-id="intro"]')).to_have_text('C (empty)')
        expect(outline.get_by_text('C (empty)', exact=True)).to_have_count(1)
        expect(outline.get_by_text('•', exact=True)).to_have_count(0)
        view.get_by_role('button', name='Find interrogative “whether”').click()
        expect(note).to_contain_text('subject “Nora” comes before “was”')
        expect(outline.get_by_text('whether', exact=True)).to_have_count(1)

        exercise = view.get_by_role('region', name='Attach the complementiser branch exercise')
        check = exercise.get_by_role('button', name='Check my tree')
        status = exercise.locator('.first-tree-footer [role=status]')
        check.click()
        expect(status).to_contain_text('still detached')
        exercise.get_by_role('button', name='Guide me').click()
        exercise.get_by_role('button', name='Connect C beside S', exact=False).click()
        check.click()
        expect(status).to_contain_text('C and S are sisters under S′')
        exercise.get_by_role('button', name='Undo', exact=True).click()
        check.click()
        expect(status).to_contain_text('still detached')
        exercise.get_by_role('button', name='Connect C beside S', exact=False).click()
        page.reload(wait_until='domcontentloaded')
        check.click()
        expect(status).to_contain_text('C and S are sisters under S′')

        page.set_viewport_size({'width': 390, 'height': 844})
        page.evaluate("document.documentElement.dataset.theme = 'dark'")
        next_page.click()
        view.get_by_role('button', name='Find the extraposed subject').click()
        expect(note).to_contain_text('attaches directly under the main S')
        assert outline.locator(':scope > ul > li > ul > li').count() == 3
        view.get_by_role('button', name='Find the clausal object').click()
        expect(note).to_contain_text('object NP contains S′')
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')

        next_page.click()
        view.get_by_role('button', name='Trace the noun').click()
        expect(note).to_contain_text('sisters within NOM')
        view.get_by_role('button', name='Trace the preposition').click()
        expect(note).to_contain_text('sisters within PP')
        next_page.click()
        view.get_by_role('radio', name='The inner S beginning with “the gate”').check()
        expect(view.get_by_role('status')).to_contain_text('Include “because”')
        view.get_by_role('radio', name='The S′ beginning with “because”').check()
        expect(view.get_by_role('status')).to_contain_text('whole S′ joins the basic VP')
        expect(note).to_contain_text('P “after” takes S directly')
        view.get_by_role('button', name='Trace the reason S′').click()
        expect(note).to_contain_text('C “because” introduces S')
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')

        next_page.click()
        view.get_by_role('button', name='← All lessons', exact=True).click()
        chapter.get_by_role('button', name='Resume lesson', exact=True).click()
        expect(page).to_have_url(f'{base}/?preview=br-08#lesson/br-08/application')
        view.get_by_role('radio', name='“Ivo” and “the hall”').check()
        expect(view.get_by_role('status')).to_contain_text('subjects inside the two S nodes')
        view.get_by_role('radio', name='“that” and “whether”').check()
        expect(view.get_by_role('status')).to_contain_text('spans end at “open”')
        view.get_by_text('Check both spans').click()
        expect(view.get_by_text('Ria heard [that Ivo wondered [whether the hall was open]].', exact=True)).to_be_visible()

        next_page.click()
        view.get_by_text('References and source review', exact=True).click()
        expect(view.get_by_text('Chapter 8 · printed p. 185', exact=False)).to_be_visible()
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

        page.goto(f'{base}/#lesson/br-08/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name='Introduction to Overt That-clauses', exact=True)).to_be_visible()
        assert not errors and not parses, (errors, parses)
        browser.close()
finally:
    server.shutdown()

print('PASS: Chapter 8 unfilled C, attachments, branch repair, nested spans, mobile, resume, scores and XP, and published isolation.')
