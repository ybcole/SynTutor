"""Verify the Chapter 3 pilot through the static Lessons app."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads((ROOT / 'web/content/lessons/br-03-pilot.json').read_text())


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

        page.goto(f'{base}/?preview=br-03#lesson/catalog', wait_until='domcontentloaded')
        chapter = view.locator('.lesson-module').filter(has=page.get_by_role('heading', name=PILOT['title'], exact=True))
        expect(chapter.locator('.lesson-module-description')).to_contain_text('prepositional phrases can join')
        chapter.get_by_role('button', name='Start lesson', exact=True).click()
        expect(view.get_by_role('heading', name=PILOT['title'], exact=True)).to_be_visible()
        expect(view.get_by_role('heading', name='Words and phrases have categories')).to_be_visible()
        opening = submit('opening', 2)
        expect(opening.get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
        expect(opening.get_by_text('Correct answer:', exact=False)).to_have_count(0)

        next_page = view.get_by_role('button', name='Next →', exact=True)
        next_page.click()
        view.get_by_role('button', name='lamps', exact=True).click()
        expect(view.locator('.lesson-tree-observation').first).to_contain_text('full subject group')
        view.get_by_role('button', name='The paper lamps', exact=True).press('Enter')
        expect(view.locator('.lesson-tree-observation').first).to_contain_text('whole NP')
        view.get_by_role('button', name='Trace the pronoun', exact=True).click()
        expect(view.locator('.constituent-diagram .lesson-tree-observation')).to_contain_text('forms a whole NP')
        next_page.click()
        view.get_by_role('button', name='Read the adverb phrase', exact=True).click()
        expect(view.locator('.lesson-tree-observation')).to_contain_text('modifies “clearly”')
        view.get_by_text('Tree notation', exact=True).click()
        expect(view.locator('.lesson-notation > dl').get_by_text('AdvP', exact=True)).to_be_visible()

        page.set_viewport_size({'width': 390, 'height': 844})
        next_page.click()
        expect(page).to_have_url(f'{base}/?preview=br-03#lesson/br-03/prepositions-and-coordination')
        view.get_by_role('button', name='Read the whole coordination', exact=True).click()
        expect(view.locator('.lesson-tree-observation')).to_contain_text('outer PP')
        view.get_by_role('button', name='Compare “there”', exact=True).click()
        expect(view.locator('.lesson-tree-observation')).to_contain_text('forms a PP by itself')
        view.get_by_text('Tree notation', exact=True).click()
        expect(view.locator('.lesson-notation > dl').get_by_text('PP', exact=True)).to_be_visible()
        expect(view.locator('.lesson-notation > dl').get_by_text('AP', exact=True)).to_have_count(0)
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')

        next_page.click()
        response = view.get_by_role('textbox', name='Your explanation')
        response.fill('Behind the chair and under the blanket are PPs.')
        page.reload(wait_until='domcontentloaded')
        expect(response).to_have_value('Behind the chair and under the blanket are PPs.')
        view.get_by_role('button', name='Compare your explanation').click()
        expect(view.locator('.lesson-tree-observation')).to_contain_text('coordinate PP')
        next_page.click()
        view.get_by_text('References and source review', exact=True).click()
        expect(view.get_by_text('AI source check complete. Pilot acceptance is pending.')).to_be_visible()
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
        page.goto(f'{base}/#lesson/br-03/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name='Introduction to Adjective Phrases')).to_be_visible()
        view.get_by_role('button', name='← All lessons', exact=True).click()
        published = view.locator('.lesson-module').filter(has=page.get_by_role('heading', name='Heads and adjective phrases', exact=True))
        expect(published.locator('.lesson-module-description')).to_contain_text('Using adjective phrases')
        assert not errors and not parses, (errors, parses)
        browser.close()
finally:
    server.shutdown()

print('PASS: Chapter 3 title, V3 traces, seven-page navigation, notation, transfer reload, review and XP.')
