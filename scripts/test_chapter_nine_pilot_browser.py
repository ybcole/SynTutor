"""Verify the Chapter 9 pilot through the static Lessons app."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PILOT = json.loads((ROOT / 'web/content/lessons/br-09-pilot.json').read_text())


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

        page.goto(f'{base}/?preview=br-09#lesson/catalog', wait_until='domcontentloaded')
        chapter = view.locator('.lesson-module').filter(has=page.get_by_role('heading', name=PILOT['title'], exact=True))
        chapter.get_by_role('button', name='Start lesson', exact=True).click()
        expect(view.get_by_role('heading', name='What does a wh-clause ask or describe?')).to_be_visible()
        opening = submit('opening', 2)
        expect(opening.get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
        expect(opening.get_by_text('Correct answer:', exact=False)).to_have_count(0)
        expect(view.get_by_text('lesson XP', exact=False)).to_have_count(0)

        next_page = view.get_by_role('button', name='Next →', exact=True)
        note = view.locator('.constituent-diagram .lesson-tree-observation')
        outline = view.locator('.lesson-tree-outline')
        next_page.click()
        expect(note).to_contain_text('an NP inside the PP')
        expect(view.locator('svg [data-node-id="wh-gap"]')).to_have_text('NP')
        view.get_by_role('button', name='Find the whole PP gap').press('Enter')
        expect(note).to_contain_text('Its gap is a PP')
        expect(view.locator('svg [data-node-id="wh-gap"]')).to_have_text('PP')
        view.get_by_role('button', name='Find the subject gap').click()
        expect(note).to_contain_text('subject NP')
        next_page.click()
        view.get_by_role('button', name='Find the auxiliary gap').click()
        expect(outline.get_by_text('•', exact=True)).to_have_count(2)
        exercise = view.get_by_role('region', name='Attach the NP that contains the object gap exercise')
        check = exercise.get_by_role('button', name='Check my tree')
        status = exercise.locator('.first-tree-footer [role=status]')
        check.click()
        expect(status).to_contain_text('still detached')
        exercise.get_by_role('button', name='Guide me').click()
        guide = exercise.get_by_role('button', name='Connect the object-gap NP beside V', exact=False)
        guide.click()
        check.click()
        expect(status).to_contain_text('object-gap NP sits beside V')
        exercise.get_by_role('button', name='Undo', exact=True).click()
        check.click()
        expect(status).to_contain_text('still detached')
        guide.click()
        page.reload(wait_until='domcontentloaded')
        check.click()
        expect(status).to_contain_text('object-gap NP sits beside V')

        page.set_viewport_size({'width': 390, 'height': 844})
        page.evaluate("document.documentElement.dataset.theme = 'dark'")
        next_page.click()
        view.get_by_role('button', name='Read embedded C1').click()
        expect(outline.get_by_text('C1 (empty)', exact=True)).to_have_count(1)
        expect(outline.get_by_text('was', exact=True)).to_have_count(1)
        expect(outline.get_by_text('•', exact=True)).to_have_count(1)
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')

        next_page.click()
        expect(outline.get_by_text('•', exact=True)).to_have_count(0)
        view.get_by_role('button', name='Compare relative “that”').click()
        expect(note).to_contain_text('occupies C2')
        expect(outline.get_by_text('•', exact=True)).to_have_count(1)
        view.get_by_role('button', name='Leave C2 unfilled').click()
        expect(outline.get_by_text('C2 (empty)', exact=True)).to_have_count(1)
        expect(outline.get_by_text('•', exact=True)).to_have_count(1)

        next_page.click()
        view.get_by_role('radio', name='The second sentence').check()
        expect(view.get_by_role('status')).to_contain_text('already identified lanterns')
        view.get_by_role('radio', name='The first sentence').check()
        expect(view.get_by_role('status')).to_contain_text('from the larger set')
        view.get_by_role('button', name='Read the non-restrictive relative').click()
        expect(note).to_contain_text('joins that NP')
        assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')

        next_page.click()
        view.get_by_role('button', name='← All lessons', exact=True).click()
        chapter.get_by_role('button', name='Resume lesson', exact=True).click()
        expect(page).to_have_url(f'{base}/?preview=br-09#lesson/br-09/application')
        view.get_by_role('radio', name='Identifies which ropes were dry').check()
        expect(view.get_by_role('status')).to_contain_text('applies to the ropes Ivo checked')
        view.get_by_text('Check the relative’s job').click()
        expect(view.get_by_text('The object gap is after “checked”', exact=False)).to_be_visible()
        next_page.click()
        view.get_by_text('References and source review', exact=True).click()
        expect(view.get_by_text('Chapter 9 · printed p. 210', exact=False)).to_be_visible()
        view.get_by_role('button', name='Check what you learned', exact=True).click()
        closing = submit('closing', 3)
        expect(closing.get_by_role('status')).to_have_text('Last attempt 3 / 5 · Best 3 / 5')
        expect(closing.get_by_text('9 / 15 lesson XP on this device')).to_be_visible()
        expect(closing.get_by_text('Correct answer:', exact=False)).to_have_count(5)
        closing.get_by_role('button', name='Retake closing check').click()
        closing = submit('closing', 5)
        expect(closing.get_by_text('15 / 15 lesson XP on this device')).to_be_visible()

        page.goto(f'{base}/#lesson/br-09/introduction', wait_until='domcontentloaded')
        expect(view.get_by_role('heading', name='Wh-fronting and typed gaps', exact=True)).to_be_visible()
        # A controlled gap and its overt controller expose the same index.
        labels = page.evaluate("""async () => {
            const { renderLessonTree } = await import('/js/lessons-ui.js');
            const root = { label: 'S', children: [
                { label: 'NP', index: 1, triangle: true, words: ['Nia'] },
                { label: 'VP', children: [
                    { word: 'tries' },
                    { label: 'S', children: [
                        { label: 'NP', children: [{ gap: true, index: 1 }] },
                        { label: 'VP', children: [{ word: 'to' }, { word: 'wait' }] },
                    ] },
                ] },
            ] };
            const tree = renderLessonTree({ root, sentence: 'Nia tries to wait' });
            return [
                [...tree.querySelectorAll('svg text')].map(label => label.textContent),
                tree.querySelector('.lesson-tree-text').textContent,
            ];
        }""")
        assert {'NP (1)', '• (1)'} <= set(labels[0])
        assert 'NP (1) — Nia' in labels[1] and '• (1)' in labels[1]
        assert not errors and not parses, (errors, parses)
        browser.close()
finally:
    server.shutdown()

print('PASS: Chapter 9 typed gaps, embedded C1, relative variants and scope, repair, mobile, resume, scores and XP, and published isolation.')
