"""Exercise the combined Foundations candidate from the packaged static app."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import subprocess
import threading

from playwright.sync_api import expect, sync_playwright

from lesson_browser_steps import choose_tree_step

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
PILOTS = {path.name[:5]: json.loads(path.read_text())
          for path in sorted((DIST / 'content/lessons').glob('br-*-pilot.json'))}
assert len(PILOTS) == 11
COURSE = json.loads((DIST / 'content/lessons/course.json').read_text())
TOTAL_LESSONS = len(COURSE['lessons'])
assert TOTAL_LESSONS >= 12
BOOK_COVERAGE = json.loads(subprocess.check_output([
    'node', '--input-type=module', '-e',
    "import { foundationsBookContent } from './dist/js/foundations-book-content.js';"
    "console.log(JSON.stringify(foundationsBookContent));",
], cwd=ROOT))
PLAN = ROOT / 'docs/planning/syntax-foundations-book-coverage-plan.md'
planned_topics = re.findall(r'^\| (BR\d{2}-(?:\d{2}|P)) ·', PLAN.read_text(), re.M)
assert sorted(planned_topics) == sorted(
    row[0] for chapter in BOOK_COVERAGE.values() for sections in chapter.values() for row in sections)


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
                payload = request.request.post_data_json or {}
                if not (page.url.rstrip('/') == base and payload.get('text') == 'The clever boy reads a book.'):
                    parser_calls.append((page.url, payload))
            if url.startswith('https://esm.sh/'):
                request.fulfill(content_type='application/javascript', body='export const createClient = () => null;')
            elif url.startswith(base) and '/api/parse' not in url:
                request.continue_()
            else:
                request.abort()

        page.route('**/*', route)
        view = page.locator('#curriculumView')

        def open_lesson(url, heading=None):
            page.mouse.move(1, 1)
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
        open_lesson(base + '/?preview=legacy#lesson/catalog')
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
        expect(view.locator('.lesson-total')).to_have_text(f'1 / {TOTAL_LESSONS} lessons completed · 15 lesson XP')

        # Start an individual draft before loading the combined preview in this same browser.
        open_lesson(base + '/?preview=br-02#lesson/br-02/introduction')
        individual = check_panel('opening')
        individual.get_by_role('radio').first.check()
        individual.get_by_role('button', name='Next question →', exact=True).click()

        open_lesson(preview + 'catalog')
        expect(view.locator('.lesson-total')).to_have_text(f'0 / {TOTAL_LESSONS} lessons completed · 0 lesson XP')
        expect(view.get_by_role('button', name='Start lesson', exact=True)).to_have_count(11)
        assert view.locator('.lesson-module h2').all_text_contents() == [pilot['title'] for pilot in PILOTS.values()]

        # Load each authored section so a mismatch with an assessment's required IDs is visible.
        for id, pilot in PILOTS.items():
            tree_pages = 0
            topics = BOOK_COVERAGE[id]
            sections = dict.fromkeys([*pilot['revised_assessment']['required_sections'], *topics])
            for section in sections:
                open_lesson(preview + f'{id}/{section}')
                expect(view).to_contain_text('Chapter pilot · progress saved on this device')
                assert page.url.endswith(f'#lesson/{id}/{section}')
                if section == 'introduction':
                    expect(view.get_by_role('heading', name='What you’ll learn in this chapter')).to_be_visible()
                    expect(view.locator('.lesson-intro-example > p').first).to_contain_text('below')
                if section == 'recap':
                    expect(view.get_by_role('heading', name='Key takeaways')).to_be_visible()
                    assert view.locator('article > ul.constituent-recap > li').count() >= 3
                entries = topics.get(section, [])
                assert len(entries) <= 4, (id, section)
                expect(view.locator('article > h3[id^="br"]')).to_have_count(len(entries))
                if entries:
                    expect(view.locator('#lesson-reflections-title')).to_have_text('Practice and feedback')
                for topic_id, title, example, explanation, prompt, answer, *definition in entries:
                    selector = f'#{topic_id.lower()}'
                    heading = view.locator(selector)
                    expect(heading).to_have_text(title)
                    if definition:
                        expect(view.locator(f'{selector} + p')).to_have_text(definition[0])
                    expect(view.locator(selector + ' + p' * (1 + len(definition)))).to_have_text(example)
                    for index, paragraph in enumerate(explanation.split('\n\n'), start=2 + len(definition)):
                        expect(view.locator(selector + ' + p' * index)).to_have_text(paragraph)
                    exercise = view.locator(f'{selector}-practice')
                    expect(exercise.locator('.lesson-reflection-intro + .lesson-reflection-prompt')).to_be_visible()
                    assert exercise.locator('.lesson-reflection-intro').inner_text().strip()
                    expect(exercise.locator('.lesson-reflection-prompt')).to_have_text(prompt)
                    expect(exercise.locator(':scope > p').last).to_have_text(answer)
                    expect(exercise.locator(':scope > p').last).to_be_visible()
                    expect(exercise.locator('details')).to_have_count(0)
                    expect(exercise).to_have_css('border-inline-start-width', '0px')
                canvases = view.locator('.lesson-tree-canvas')
                if canvases.count():
                    tree_pages += 1
                    expect(canvases.locator('details.lesson-tree-text > summary')).to_have_count(canvases.count())
                    expect(view.locator('.lesson-notation').first).to_be_visible()
                    assert canvases.evaluate_all("""nodes => nodes.every(canvas => {
                      const outline = canvas.querySelector('.lesson-tree-text');
                      const observation = canvas.querySelector('.lesson-tree-observation');
                      const notation = canvas.closest('article').querySelector('.lesson-notation');
                      return !outline.open && (!observation || observation.nextElementSibling === outline)
                        && Boolean(outline.compareDocumentPosition(notation) & Node.DOCUMENT_POSITION_FOLLOWING);
                    })""")
                    disclosure = canvases.first.locator('details.lesson-tree-text')
                    disclosure.locator('summary').press('Enter')
                    expect(disclosure.locator('.lesson-tree-outline > ul > li').first).to_be_visible()
            assert tree_pages, id
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
        expect(view.locator('.lesson-total')).to_have_text(f'3 / {TOTAL_LESSONS} lessons completed · 45 lesson XP')
        view.get_by_role('button', name='Grammar and Analysis', exact=True).click()
        cambridge = view.locator('.lesson-module').first
        expect(cambridge.locator('.lesson-prerequisite')).to_have_count(0)
        cambridge.get_by_role('button', name='Start lesson', exact=True).click()
        expect(view.locator('.lesson-stage-body')).to_be_visible()
        first_grammar = next(l for l in COURSE['lessons'] if l.get('track') == 'grammar')
        has_pilot = (DIST / f"content/lessons/{first_grammar['lesson_id']}-pilot.json").exists()
        expect(view.get_by_text('Chapter pilot · progress saved on this device')).to_have_count(1 if has_pilot else 0)

        # Check keyboard navigation in the desktop sidebar and tap navigation in
        # the dark mobile reader using representative early, middle and late chapters.
        page.set_viewport_size({'width': 1440, 'height': 1000})
        mobile = browser.new_page(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True)
        mobile.add_init_script("""
          localStorage.setItem('syntutor_onboarding_seen', '1');
          localStorage.setItem('syntutor_theme', 'dark');
        """)
        mobile.on('pageerror', lambda error: errors.append(str(error)))
        mobile.route('**/*', route)
        for id, section in [('br-01', 'worked-example'), ('br-06', 'chain'), ('br-11', 'worked-example')]:
            open_lesson(preview + f'{id}/introduction')
            sidebar = view.locator('.lesson-section-sidebar')
            sidebar.locator(f'a[href$="/{section}"]').press('Enter')
            expect(page).to_have_url(preview + f'{id}/{section}')
            expect(view.locator('.lesson-stage-body > h2')).to_be_focused()
            expect(view.locator('svg[aria-label^="Syntax tree"]').first).to_be_visible()

            mobile.goto(preview + f'{id}/introduction', wait_until='domcontentloaded')
            expect(mobile.locator('html')).to_have_attribute('data-theme', 'dark')
            menu = mobile.locator('.lesson-section-mobile')
            menu.locator('summary').tap()
            menu.locator(f'a[href$="/{section}"]').tap()
            expect(mobile).to_have_url(preview + f'{id}/{section}')
            expect(mobile.locator('#curriculumView svg[aria-label^="Syntax tree"]').first).to_be_visible()
            disclosure = mobile.locator('.lesson-tree-text').first
            disclosure.locator('summary').tap()
            expect(disclosure.locator('.lesson-tree-outline > ul > li').first).to_be_visible()
            assert mobile.locator('#curriculumView').evaluate('(el) => el.scrollWidth <= el.clientWidth')
        open_lesson(preview + 'br-11/worked-example')
        disclosure = view.locator('.lesson-tree-text').first
        disclosure.locator('summary').press('Enter')
        choose_tree_step(view, 'Reuse the first result')
        expect(disclosure).to_have_attribute('open', '')
        expect(disclosure.locator('.lesson-tree-outline')).to_contain_text('Mina waves')

        open_lesson(preview + 'br-04/concepts')
        term = view.get_by_role('button', name='Define complement', exact=True).first
        dictionary = view.get_by_role('region', name='Dictionary definition')
        term.hover()
        expect(dictionary).to_contain_text('fills a role')
        expect(dictionary.get_by_role('link')).to_have_count(0)
        page.mouse.move(1, 1)
        term.focus()
        expect(dictionary).to_be_visible()
        page.keyboard.press('Escape')
        expect(dictionary).to_have_count(0)
        expect(term).to_be_focused()

        mobile.goto(preview + 'br-04/concepts', wait_until='domcontentloaded')
        mobile.get_by_role('button', name='Define [trans]', exact=True).first.tap()
        mobile_dictionary = mobile.get_by_role('region', name='Dictionary definition')
        expect(mobile_dictionary).to_contain_text('one direct object')
        assert mobile_dictionary.evaluate('(el) => el.getBoundingClientRect().right <= innerWidth')
        mobile.locator('.lesson-stage-body > h2').tap()
        expect(mobile_dictionary).to_have_count(0)
        mobile.close()

        open_lesson(base + '/?preview=br-02#lesson/br-02/introduction')
        expect(check_panel('opening')).to_contain_text('Question 2 of 5')
        open_lesson(base + '/?preview=legacy#lesson/catalog')
        expect(view.locator('.lesson-total')).to_have_text(f'1 / {TOTAL_LESSONS} lessons completed · 15 lesson XP')
        assert view.locator('.lesson-module h2').all_text_contents() != [pilot['title'] for pilot in PILOTS.values()]
        page.goto(base, wait_until='domcontentloaded')
        page.locator('.sidebar-item[data-view="lessons"]').click()
        expect(view.locator('.lesson-module')).to_have_count(11)
        assert view.locator('.lesson-module h2').all_text_contents() == [pilot['title'] for pilot in PILOTS.values()]
        expect(view.locator('.lesson-total')).to_have_text(f'0 / {TOTAL_LESSONS} lessons completed · 0 lesson XP in this view')
        open_lesson(base + '/#lesson/br-01/introduction')
        dictionary_example = view.get_by_role('button', name='Define constituent', exact=True).first
        dictionary_example.hover()
        chapter_one_dictionary = view.get_by_role('region', name='Dictionary definition')
        expect(chapter_one_dictionary).to_contain_text('works as a unit')
        expect(chapter_one_dictionary.get_by_role('link')).to_have_count(0)
        expect(page).to_have_url(base + '/#lesson/br-01/introduction')
        open_lesson(base + '/#lesson/br-01/recap')
        expect(view.locator('.lesson-sources').first).to_have_css('border-inline-start-width', '0px')
        open_lesson(base + '/#lesson/br-04/concepts')
        expect(view.locator('#br04-03')).to_be_visible()
        expect(view.locator('#br04-04')).to_be_visible()
        terms = view.locator('.lesson-dictionary-term')
        repeats = view.locator('.lesson-dictionary-term-repeat')
        assert repeats.count() > 0
        expect(terms.first).to_have_css('text-decoration-line', 'underline')
        expect(repeats.first).to_have_css('text-decoration-line', 'none')
        view.get_by_role('button', name='Define complement', exact=True).first.hover()
        expect(view.get_by_role('region', name='Dictionary definition')).to_contain_text('fills a role')
        open_lesson(base + '/#lesson/br-07/nom-appendix')
        expect(view.locator('#br07-11')).to_be_visible()
        open_lesson(base + '/#lesson/br-02/introduction')
        expect(check_panel('opening')).to_contain_text('Question 1 of 5')
        panel = submit('br-02', 'opening', 2)
        expect(panel.get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
        page.reload(wait_until='domcontentloaded')
        expect(check_panel('opening').get_by_role('status')).to_have_text('Opening check complete. 2 / 5 correct.')
        open_lesson(base + '/#lesson/br-02/closing-check')
        panel = submit('br-02', 'closing', 3)
        expect(panel.get_by_text('9 / 15 lesson XP on this device')).to_be_visible()
        assert not errors and not parser_calls, (errors, parser_calls)
        browser.close()
finally:
    server.shutdown()

print(f'PASS: {len(planned_topics)} book topics across eleven pilots, practice feedback, section routes, progress, Cambridge navigation and normal Lessons launch.')
