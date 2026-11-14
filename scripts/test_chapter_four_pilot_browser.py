"""Verify the Chapter 4 pilot through the static Lessons app."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads((ROOT / 'web/content/lessons/br-04-pilot.json').read_text())


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

        page.goto(f'{base}/?preview=br-04#lesson/catalog', wait_until='domcontentloaded')
        chapter = view.locator('.lesson-module').filter(has=page.get_by_role('heading', name=PILOT['title'], exact=True))
        expect(chapter.locator('.lesson-module-description')).to_contain_text('six patterns')
        chapter.get_by_role('button', name='Start lesson', exact=True).click()
        expect(view.get_by_role('heading', name='What belongs inside a verb phrase?')).to_be_visible()
        opening = submit('opening', 2)
        expect(opening.get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
        expect(opening.get_by_text('Correct answer:', exact=False)).to_have_count(0)
        expect(view.get_by_text('lesson XP', exact=False)).to_have_count(0)

        next_page = view.get_by_role('button', name='Next →', exact=True)
        next_page.click()
        note = view.locator('.constituent-diagram .lesson-tree-observation')
        outline = view.locator('.lesson-tree-outline')
        view.get_by_role('button', name='Compare the intransitive VP').press('Enter')
        expect(note).to_contain_text('only immediate part of VP')
        expect(outline).to_contain_text('V [intrans]')
        view.get_by_text('Tree notation', exact=True).click()
        features = view.locator('.lesson-notation > dl')
        expect(features.get_by_text('[trans]', exact=True)).to_be_visible()
        expect(features.get_by_text('[intrans]', exact=True)).to_be_visible()
        expect(features.get_by_text('[ditrans]', exact=True)).to_have_count(0)

        exercise = view.get_by_role('region', name='Attach the direct object exercise')
        check_tree = exercise.get_by_role('button', name='Check my tree')
        status = exercise.locator('.first-tree-footer [role=status]')
        check_tree.click()
        expect(status).to_contain_text('still detached')
        exercise.get_by_role('button', name='Guide me').click()
        exercise.get_by_role('button', name='Connect the object NP under VP', exact=False).click()
        check_tree.click()
        expect(status).to_contain_text('shares VP with V [trans]')
        exercise.get_by_role('button', name='Undo', exact=True).click()
        check_tree.click()
        expect(status).to_contain_text('still detached')
        exercise.get_by_role('button', name='Connect the object NP under VP', exact=False).click()
        page.reload(wait_until='domcontentloaded')
        check_tree.click()
        expect(status).to_contain_text('shares VP with V [trans]')

        next_page.click()
        view.get_by_role('button', name='Compare the recipient PP').click()
        expect(note).to_contain_text('“To Leo” is the corresponding PP')
        expect(outline.get_by_text('PP — to Leo', exact=True)).to_have_count(1)
        view.get_by_text('Tree notation', exact=True).click()
        expect(features.get_by_text('[ditrans]', exact=True)).to_be_visible()
        expect(features.get_by_text('[trans]', exact=True)).to_have_count(0)

        page.set_viewport_size({'width': 390, 'height': 844})
        page.evaluate("document.documentElement.dataset.theme = 'dark'")
        next_page.click()
        expect(page).to_have_url(f'{base}/?preview=br-04#lesson/br-04/predicatives')
        view.get_by_role('button', name='Describe the object').click()
        expect(note).to_contain_text('describes “the steps”')
        expect(outline.get_by_text('AP — slippery', exact=True)).to_have_count(1)
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')
        next_page.click()
        expect(page).to_have_url(f'{base}/?preview=br-04#lesson/br-04/prepositional-complements')
        view.get_by_role('button', name='Trace the subject location').click()
        expect(note).to_contain_text('subject predicative')
        expect(view.get_by_text('The PP adds an optional location', exact=False)).to_be_visible()
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')

        next_page.click()
        response = view.get_by_role('textbox', name='Your explanation')
        expect(view.get_by_role('button', name='Compare your explanation')).to_be_disabled()
        response.fill('The map is the direct object in both. Ren is a recipient. Useful describes the map.')
        view.get_by_role('button', name='← All lessons', exact=True).click()
        chapter.get_by_role('button', name='Resume lesson', exact=True).click()
        expect(page).to_have_url(f'{base}/?preview=br-04#lesson/br-04/application')
        page.reload(wait_until='domcontentloaded')
        expect(response).to_have_value('The map is the direct object in both. Ren is a recipient. Useful describes the map.')
        view.get_by_role('button', name='Compare your explanation').click()
        expect(view.locator('.lesson-tree-observation')).to_contain_text('“Useful” is an object predicative')
        next_page.click()
        view.get_by_text('References and source review', exact=True).click()
        expect(view.get_by_text('Chapter 4 · printed p. 78', exact=False)).to_be_visible()
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

        page.goto(f'{base}/#lesson/br-04/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name='The basic transitive VP', exact=True)).to_be_visible()
        # A numbered VP uses the same label in the tree, outline and notation guide.
        assert page.evaluate("""async () => {
            const { renderLessonTree } = await import('/js/lessons-ui.js');
            const { lessonNotation } = await import('/js/lesson-notation.js');
            const el = (tag, text) => {
                const element = document.createElement(tag);
                if (text !== undefined) element.textContent = text;
                return element;
            };
            const root = { id: 'outer', label: 'VP', ref: 'VP2', children: [
                { id: 'inner', label: 'VP', source_refs: ['VP1'], children: [{ word: 'waited' }] },
                { id: 'time', label: 'NP', triangle: true, words: ['last', 'night'] },
            ] };
            const tree = renderLessonTree({ root, sentence: 'waited last night' });
            const notation = lessonNotation({ worked_example: { tree: { root } } }, 2, el);
            const pageGuide = lessonNotation({}, 2, el, ['VP1', 'VP3']);
            const entries = [...notation.querySelectorAll(':scope > dl:first-of-type dt')].map(node => node.textContent);
            return entries.join(' ') === 'VP₂ VP₁ NP'
                && tree.querySelector('svg').textContent.includes('VP₁')
                && tree.querySelector('details').textContent.includes('VP₂')
                && pageGuide.textContent.includes('VP₃A higher verb phrase level');
        }""")
        assert not errors and not parses, (errors, parses)
        browser.close()
finally:
    server.shutdown()

print('PASS: Chapter 4 tree contrasts and repair, page features, mobile, draft/resume, assessment review and XP, and published isolation.')
