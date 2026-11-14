"""Verify the Chapter 6 pilot through the static Lessons app."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads((ROOT / 'web/content/lessons/br-06-pilot.json').read_text())


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
                label = 'Next question →' if i < len(PILOT['revised_assessment'][kind]) - 1 else f'{"Finish" if kind == "opening" else "Submit"} {kind} check'
                panel.get_by_role('button', name=label, exact=True).click()
            return panel

        page.goto(f'{base}/?preview=br-06#lesson/catalog', wait_until='domcontentloaded')
        chapter = view.locator('.lesson-module').filter(has=page.get_by_role('heading', name=PILOT['title'], exact=True))
        expect(chapter.locator('.lesson-module-description')).to_contain_text('auxiliary is the head of its own verb phrase')
        chapter.get_by_role('button', name='Start lesson', exact=True).click()
        expect(view.get_by_role('heading', name='How do auxiliary verbs fit in?')).to_be_visible()
        opening = submit('opening', 2)
        expect(opening.get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
        expect(opening.get_by_text('Correct answer:', exact=False)).to_have_count(0)
        expect(view.get_by_text('lesson XP', exact=False)).to_have_count(0)

        next_page = view.get_by_role('button', name='Next →', exact=True)
        next_page.click()
        view.get_by_role('radio', name='written').check()
        expect(view.get_by_role('status')).to_contain_text('lexical verb “written” heads the lowest VP')
        view.get_by_role('radio', name='should').check()
        expect(view.get_by_role('status')).to_contain_text('heads the highest VP')
        note = view.locator('.constituent-diagram .lesson-tree-observation')
        view.get_by_role('button', name='Find the progressive auxiliary').press('Enter')
        expect(note).to_contain_text('PROG “is” heads the outer VP')
        expect(view.locator('svg[aria-label="Syntax tree for Monsieur Blanc is studying the menu"]')).to_be_visible()

        exercise = view.get_by_role('region', name='Nest the auxiliary VPs exercise')
        check = exercise.get_by_role('button', name='Check my tree')
        status = exercise.locator('.first-tree-footer [role=status]')
        check.click()
        expect(status).to_contain_text('still detached')
        exercise.get_by_role('button', name='Guide me').click()
        exercise.get_by_role('button', name='Connect the lower VP under the auxiliary VP', exact=False).click()
        check.click()
        expect(status).to_contain_text('MOD “should” heads its own VP')
        exercise.get_by_role('button', name='Undo', exact=True).click()
        check.click()
        expect(status).to_contain_text('still detached')
        exercise.get_by_role('button', name='Connect the lower VP under the auxiliary VP', exact=False).click()
        page.reload(wait_until='domcontentloaded')
        check = view.get_by_role('region', name='Nest the auxiliary VPs exercise').get_by_role('button', name='Check my tree')
        check.click()
        expect(view.get_by_role('region', name='Nest the auxiliary VPs exercise').locator('.first-tree-footer [role=status]')).to_contain_text('MOD “should” heads its own VP')

        page.set_viewport_size({'width': 390, 'height': 844})
        next_page.click()
        expect(page).to_have_url(f'{base}/?preview=br-06#lesson/br-06/chain')
        view.get_by_role('button', name='Find MOD').press('Enter')
        expect(note).to_contain_text('MOD “should” [past] is the highest verb')
        view.get_by_role('button', name='Read the whole chain').press('Enter')
        expect(note).to_contain_text('Only the highest VP is tensed')
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')

        next_page.click()
        view.get_by_role('button', name='Find the pre-verb adverbial').press('Enter')
        expect(note.first).to_contain_text('The AdvP “easily” comes before “have”')
        view.get_by_role('button', name='Attach the final PP').press('Enter')
        expect(note.last).to_contain_text('It modifies the lexical VP “complaining”')

        next_page.click()
        view.get_by_role('button', name='Mark the empty do').press('Enter')
        expect(note).to_contain_text('empty “do” under TENSE [past] carries the negation')

        next_page.click()
        view.get_by_role('button', name='Front the empty do').press('Enter')
        expect(note).to_contain_text('“Do” from the TENSE node moves to C')
        expect(view.locator('svg[aria-label="Syntax tree for Does Byron dance"]')).to_be_visible()
        view.get_by_role('button', name='Front as a copula').press('Enter')
        expect(note).to_contain_text('the lexical verb itself moves to C')

        next_page.click()
        view.get_by_text('References and source review', exact=True).click()
        expect(view.get_by_text('Chapter 6 · printed p. 121', exact=False)).to_be_visible()
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

        page.goto(f'{base}/#lesson/br-06/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name='Auxiliaries head their own VPs', exact=True)).to_be_visible()
        assert not errors and not parses, (errors, parses)
        browser.close()
finally:
    server.shutdown()

print('PASS: Chapter 6 auxiliary VP chain, branch repair, negation, do-support and question fronting, mobile, scores and XP, and published isolation.')
