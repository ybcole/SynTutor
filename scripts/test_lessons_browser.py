"""Actual static app navigation/rendering/storage; no NLP or external auth required."""
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
COURSE=json.loads((ROOT/'web/content/lessons/course.json').read_text())
OUT=Path('/tmp/syntutor-lessons-browser');OUT.mkdir(exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'web')))
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
base=f'http://127.0.0.1:{server.server_port}'
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1440,'height':1050})
  errors=[];parses=[]
  page.add_init_script("localStorage.setItem('syntutor_onboarding_seen','1')")
  page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   if r.request.url.startswith('https://esm.sh/'):
    r.fulfill(status=200,content_type='application/javascript',body='export const createClient = () => null;');return
   if not r.request.url.startswith(base):r.abort();return
   if '/api/parse' in r.request.url:parses.append(r.request.url)
   r.continue_()
  page.route('**/*',route)
  page.goto(base,wait_until='domcontentloaded')
  page.locator('.sidebar-item[data-view="lessons"]').click()
  view=page.locator('#curriculumView')
  view.get_by_role('heading',name='Lesson modules',exact=True).wait_for()
  cards=view.locator('.lesson-module')
  assert cards.count()==11
  expect(cards.locator('.lesson-module-objective')).to_have_text([
   'Learning objective '+lesson['outcomes'][0]['text'] for lesson in COURSE['lessons'] if lesson['track']=='foundations'
  ])
  first=cards.first
  meter=first.get_by_role('progressbar',name='Constituents and hierarchy progress')
  expect(first.get_by_text('Chapter 1',exact=True)).to_be_visible()
  expect(first.locator('.lesson-module-description')).to_have_text(COURSE['module_descriptions']['br-01'])
  expect(meter).to_have_attribute('value','0')
  expect(meter).to_have_attribute('max','6')
  expect(first.get_by_role('button',name='Start lesson',exact=True)).to_be_visible()
  expect(view.get_by_role('button',name='Back to Syntax Generator',exact=True)).to_have_count(0)
  summary=view.get_by_role('complementary',name='Course progress')
  expect(summary.get_by_role('progressbar')).to_have_attribute('value','0')
  assert summary.bounding_box()['x'] >= first.bounding_box()['x'] + first.bounding_box()['width']
  assert cards.nth(1).bounding_box()['y'] >= first.bounding_box()['y'] + first.bounding_box()['height']
  page.screenshot(path=str(OUT/'modules-desktop.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844})
  assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Module list has horizontal overflow'
  page.screenshot(path=str(OUT/'modules-mobile.png'),full_page=True)
  page.set_viewport_size({'width':1440,'height':1050})
  part_heading=view.locator('.lesson-stage-body > h2')
  chapter_one_titles=['Introduction to Constituents and Hierarchy','Identifying Constituents in a Sentence',
                      'Comparing Flat and Nested Trees', 'Structural Ambiguity',
                      'Chapter Recap','Check what you learned']
  page.evaluate("()=>import('/js/lessons-ui.js').then(m=>m.openLessons('br-01'))")
  expect(part_heading).to_have_text(chapter_one_titles[0])
  expect(view.locator('.lesson-intro-example > p').first).to_contain_text('where the meeting took place')
  expect(view.locator('.lesson-key-terms dt')).to_have_text(['Constituent','Hierarchy','Replacement test','Structural ambiguity'])
  expect(view.locator('.lesson-tree-canvas')).to_have_count(0)
  expect(view.locator('article')).to_have_attribute('aria-labelledby','constituent-page-title')
  intro=view.get_by_role('heading',name='Check what you know',exact=True)
  opening=view.get_by_role('region',name='Check what you know')
  opening_rows=opening.locator('.lesson-option')
  expect(opening_rows.first.locator('input')).to_have_css('width','20px')
  assert opening_rows.evaluate_all("""rows => {
    const [first, second, third] = rows.map(row => getComputedStyle(row).backgroundColor);
    return first === third && first !== second;
  }"""), 'Answer rows should alternate in the opening check'
  expect(view.locator('[data-question="predict"] legend')).to_contain_text('Mara rested beside the river')
  expect(intro).to_be_visible()
  assert intro.bounding_box()['y'] < view.locator('[data-question="predict"]').bounding_box()['y']
  page.screenshot(path=str(OUT/'br-01-intro-desktop.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844})
  assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Introduction has horizontal overflow'
  page.screenshot(path=str(OUT/'br-01-intro-mobile.png'),full_page=True)
  page.set_viewport_size({'width':1440,'height':1050})
  next_button=view.get_by_role('button',name='Next →',exact=True)
  expect(next_button).to_be_disabled()
  columns=view.locator('.constituent-page article').bounding_box()
  action=next_button.bounding_box()
  assert action['y'] >= columns['y'] + columns['height']
  assert abs(action['x'] + action['width'] - columns['x'] - columns['width']) < 1
  expect(view.locator('.lesson-sources')).to_have_count(0)
  prediction=view.locator('[data-question="predict"]')
  page.set_viewport_size({'width':390,'height':844})
  for number, answer in enumerate(['a','c','a'],start=1):
   expect(opening.locator('.lesson-assessment-position')).to_have_text(f'Question {number} of 3')
   expect(opening.locator('.lesson-question')).to_have_count(1)
   assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')
   action=opening.get_by_role('button',name='Finish knowledge check' if number==3 else 'Next question →')
   expect(action).to_be_disabled()
   expect(next_button).to_be_disabled()
   prediction.locator(f'input[value="{answer}"]').check()
   action.click()
   expect(part_heading).to_have_text(chapter_one_titles[0])
   if number==1:
    page.reload(wait_until='domcontentloaded')
    page.evaluate("()=>import('/js/lessons-ui.js').then(m=>m.openLessons('br-01'))")
  expect(view.locator('.constituent-pre-test-status')).to_have_text('Knowledge check complete. 2 of 3 correct.')
  expect(prediction).to_have_count(0)
  expect(next_button).to_be_enabled()
  page.set_viewport_size({'width':1440,'height':1050})
  next_button.click()
  expect(part_heading).to_have_text(chapter_one_titles[1])
  expect(view.get_by_role('heading',name='Test a group with replacement')).to_be_visible()
  view.get_by_role('button',name='near the quiet garden',exact=True).click()
  expect(view.locator('.lesson-tree-focus text')).to_have_text('PHRASE-a')
  view.get_by_role('button',name='← Previous',exact=True).click()
  expect(view.locator('.constituent-pre-test-status')).to_have_text('Knowledge check complete. 2 of 3 correct.')
  expect(prediction).to_have_count(0)
  next_button.click()
  expect(part_heading).to_have_text(chapter_one_titles[1])
  next_button.click()
  expect(part_heading).to_have_text(chapter_one_titles[2])
  expect(view.get_by_role('heading',name='Worked example',exact=True)).to_have_count(0)
  expect(view.get_by_role('button',name='Inspect highlighted tree position')).to_have_count(0)
  expect(view.locator('.constituent-selection mark')).to_have_text(['the','quiet','garden'])
  comparison=view.locator('.canonical-viewport').first
  expect(comparison.locator('svg polygon')).to_have_count(0)
  nested_box=comparison.bounding_box()
  nested_viewbox=comparison.locator('svg').get_attribute('viewBox')
  def check_comparison_branches(color):
   assert comparison.locator('svg .lesson-branch').evaluate_all("""(branches, color) =>
     branches.every(branch => {
       const style = getComputedStyle(branch);
       return style.stroke === color && style.strokeWidth === '1.5px';
     })""",color), 'Comparison branches should have a uniform, neutral stroke'
  for drawing_name, branches in [('Flat drawing',4),('Nested drawing',5)]:
   view.get_by_role('button',name=drawing_name).click()
   expect(comparison.locator('svg .lesson-branch')).to_have_count(branches)
   traced_words = ['near','the','quiet','garden'] if drawing_name == 'Flat drawing' else ['the','quiet','garden']
   expect(comparison.locator('svg .lesson-word-traced')).to_have_text(traced_words)
   check_comparison_branches('rgb(100, 116, 139)')
   expect(comparison.locator('svg')).to_have_attribute('viewBox',nested_viewbox)
   expect(comparison.get_by_role('button',name='Zoom in B-R tree')).to_be_visible()
   assert comparison.bounding_box()['width']==nested_box['width']
   assert comparison.bounding_box()['height']==nested_box['height']
   expect(comparison.locator('svg text').filter(has_text=re.compile(r'^(near|the|quiet|garden)$'))).to_have_count(4)
  outer=comparison.get_by_role('button',name='Inspect B-R PHRASE-a for PHRASE-a',exact=True)
  inner=comparison.get_by_role('button',name=re.compile(r'^Inspect B-R PHRASE-b\b'))
  outer_box=outer.locator('.lesson-tree-focus-box')
  inner_box=inner.locator('.lesson-tree-focus-box')
  outer.press('Enter')
  check_comparison_branches('rgb(100, 116, 139)')
  expect(comparison.locator('svg .lesson-word-traced')).to_have_text(['near','the','quiet','garden'])
  expect(outer_box).to_have_css('display','inline')
  expect(inner_box).to_have_css('display','none')
  page.evaluate("document.documentElement.setAttribute('data-theme','dark')")
  inner.locator('text').first.click()
  expect(outer_box).to_have_css('display','none')
  expect(inner_box).to_have_css('display','inline')
  check_comparison_branches('rgb(148, 163, 184)')
  expect(comparison.locator('svg .lesson-word-traced')).to_have_text(['the','quiet','garden'])
  viewport=comparison.bounding_box()
  drawing=comparison.locator('svg')
  initial_width=drawing.bounding_box()['width']
  comparison.get_by_role('button',name='Zoom in B-R tree').click()
  assert drawing.bounding_box()['width'] > initial_width
  assert comparison.bounding_box()==viewport
  comparison.get_by_role('button',name='Fit B-R tree').click()
  page.evaluate("document.documentElement.setAttribute('data-theme','dark')")
  page.screenshot(path=str(OUT/'br-01-comparison-dark.png'),full_page=True)
  page.evaluate("document.documentElement.setAttribute('data-theme','light')")
  page.screenshot(path=str(OUT/'br-01-desktop.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844})
  comparison.scroll_into_view_if_needed()
  assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Chapter 1 has horizontal overflow'
  page.screenshot(path=str(OUT/'br-01-mobile-tree.png'),full_page=True)
  page.set_viewport_size({'width':1440,'height':1050})
  # Reload keeps an unfinished stage; identity and version handling are unit/RPC tested.
  page.reload(wait_until='domcontentloaded');page.locator('.sidebar-item[data-view="lessons"]').click()
  view.get_by_role('heading',name='Lesson modules',exact=True).wait_for()
  expect(meter).to_have_attribute('value','2')
  expect(first.get_by_text('2 of 6 stages completed',exact=True)).to_be_visible()
  expect(summary.get_by_role('button',name='Constituents and hierarchy',exact=True)).to_be_visible()
  resume=first.get_by_role('button',name='Resume lesson',exact=True)
  expect(resume).to_have_class(re.compile(r'\blesson-primary\b'))
  resume.click()
  expect(part_heading).to_have_text(chapter_one_titles[2])
  # Finish the consolidated Chapter 1 teaching flow and test its saved assessment.
  view.get_by_text('Tree notation',exact=True).click()
  expect(view.locator('.lesson-notation > dl').get_by_text('PHRASE-b',exact=True)).to_be_visible()
  view.get_by_text('View all notation',exact=True).click()
  expect(view.locator('.lesson-notation').get_by_text('[-tense]',exact=True)).to_be_visible()
  view.get_by_text('Tree notation',exact=True).click()
  exercise=view.get_by_role('region',name='Build your first tree exercise')
  expect(exercise.get_by_role('checkbox')).to_have_count(0)
  canvas=exercise.locator('#builderCanvas')
  expect(canvas).to_be_visible()
  expect(view.locator('.constituent-selection').first).to_be_visible()
  assert view.locator('.constituent-selection').first.bounding_box()['y'] < view.locator('.constituent-caption').first.bounding_box()['y']
  expect(exercise.locator('#builderTools')).to_have_count(0)
  canvas.click(button='right',position={'x':20,'y':25})
  page.locator('.builder-menu').get_by_role('button',name='PHRASE-c',exact=True).click()
  exercise.get_by_role('button',name='Check construction').click()
  expect(exercise.get_by_role('status')).to_contain_text('single outer node')
  canvas.press('Control+z')
  guide_toggle=exercise.get_by_role('button',name='Guide me')
  guide=exercise.locator('.first-tree-guide')
  expect(guide).to_be_hidden()
  guide_toggle.click()
  expect(guide_toggle).to_have_attribute('aria-expanded','true')
  expect(guide.get_by_role('button')).to_have_count(4)
  expect(guide.locator('.first-tree-guide-number')).to_have_text(['1.','2.','3.','4.'])
  expect(guide).to_have_css('background-color','rgba(0, 0, 0, 0)')
  add_node=guide.get_by_role('button',name='Add PHRASE-b',exact=False)
  expect(add_node.locator('strong')).to_have_css('color','rgb(30, 32, 41)')
  add_node.hover()
  assert add_node.evaluate("(row) => getComputedStyle(row).backgroundColor !== 'rgba(0, 0, 0, 0)'")
  expect(guide.get_by_role('button',name='Check the tree',exact=False)).to_be_visible()
  expect(exercise.get_by_role('button',name='Next hint')).to_have_count(0)
  guide.scroll_into_view_if_needed()
  page.screenshot(path=str(OUT/'br-01-tree-guide.png'),full_page=True)
  guide.get_by_role('button',name='Connect PHRASE-b to PHRASE-a',exact=False).press('Enter')
  expect(exercise.get_by_role('status')).to_contain_text('first')
  guide.get_by_role('button',name='Add PHRASE-b',exact=False).press('Enter')
  guide.get_by_role('button',name='Connect PHRASE-b to PHRASE-a',exact=False).press('Enter')
  guide.get_by_role('button',name='Connect “the red gate” to PHRASE-b',exact=False).press('Enter')
  guide.get_by_role('button',name='Check the tree',exact=False).press('Enter')
  expect(exercise.get_by_role('status')).to_contain_text('Exactly.')
  guide_toggle.click()
  expect(guide_toggle).to_have_attribute('aria-expanded','false')
  expect(guide).to_be_hidden()
  page.set_viewport_size({'width':390,'height':844})
  guide_toggle.click()
  expect(guide.get_by_role('button')).to_have_count(4)
  assert guide.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Open guide overflows its container'
  guide_toggle.click()
  assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Editable tree overflows the lesson'
  canvas.scroll_into_view_if_needed()
  page.wait_for_function("""canvas => {
    const pixels = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
    return pixels.some((value, index) => index % 4 === 3 && value > 0);
  }""",arg=canvas.element_handle(),timeout=5000)
  page.screenshot(path=str(OUT/'br-01-editable-tree-mobile.png'),full_page=True)
  page.set_viewport_size({'width':1440,'height':1050})
  view.get_by_role('button',name='Next →',exact=True).click()
  expect(part_heading).to_have_text(chapter_one_titles[3])
  expect(page.locator('.canvas-stage #builderCanvas')).to_be_hidden()
  view.get_by_role('button',name='The hikers had the telescope').click()
  expect(view.locator('.constituent-caption')).to_contain_text('which hikers')
  view.get_by_role('button',name='Next →',exact=True).click()
  expect(part_heading).to_have_text(chapter_one_titles[4])
  expect(view.locator('.constituent-recap li')).to_have_count(4)
  references=view.locator('article .lesson-sources')
  references.locator('summary').click()
  expect(references.get_by_text('AI checked',exact=False)).to_be_visible()
  view.get_by_role('button',name='Check what you learned').click()
  expect(part_heading).to_have_text(chapter_one_titles[5])
  expect(view.locator('.lesson-sources')).to_have_count(0)
  chapter_one=COURSE['lessons'][0]
  guided=view.locator('[data-question="guided"]')
  closing=view.get_by_role('region',name='Chapter knowledge check')
  expect(closing.locator('.lesson-assessment-position')).to_have_text('Question 1 of 3')
  expect(closing.locator('.lesson-question')).to_have_count(1)
  page.set_viewport_size({'width':390,'height':844})
  assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth')
  expect(view.get_by_text('Read the tree as text',exact=True)).to_have_count(0)
  outline=view.get_by_role('group',name='Tree structure')
  expect(outline).to_contain_text('?')
  expect(outline).not_to_contain_text('PHRASE-b')
  guided.locator('input[value="'+chapter_one['guided']['answer']+'"]').check()
  closing.get_by_role('button',name='Next question →',exact=True).click()
  expect(closing.locator('.lesson-assessment-position')).to_have_text('Question 2 of 3')
  expect(closing.locator('.lesson-question')).to_have_count(1)
  expect(part_heading).to_have_text(chapter_one_titles[5])
  page.set_viewport_size({'width':1440,'height':1050})
  view.get_by_role('button',name='← Previous',exact=True).click()
  expect(part_heading).to_have_text(chapter_one_titles[4])
  view.get_by_role('button',name='Check what you learned').click()
  expect(view.locator('[data-question="transfer"]')).to_be_visible()
  page.reload(wait_until='domcontentloaded')
  page.locator('.sidebar-item[data-view="lessons"]').click()
  first.get_by_role('button',name='Resume lesson',exact=True).click()
  expect(view.locator('[data-question="transfer"]')).to_be_visible()
  for key, action in [('transfer','Next question →'),('exit','Complete lesson')]:
   question=view.locator(f'[data-question="{key}"]')
   wrong=next(o['id'] for o in chapter_one[key]['options'] if o['id']!=chapter_one[key]['answer'])
   question.locator(f'input[value="{wrong}"]').check()
   expect(closing.get_by_role('button',name=action,exact=True)).to_be_disabled()
   question.locator(f'input[value="{chapter_one[key]["answer"]}"]').check()
   closing.get_by_role('button',name=action,exact=True).click()
  expect(view.locator('.lesson-save-status')).to_contain_text('15 lesson XP awarded')
  expect(view.get_by_role('heading',name='Extra practice')).to_be_visible()
  expect(closing.get_by_role('heading',name='Answers overview')).to_be_visible()
  expect(closing.locator('.lesson-question')).to_have_count(3)
  expect(closing.get_by_role('button',name='Next question →')).to_have_count(0)
  page.set_viewport_size({'width':390,'height':844})
  assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Answers overview has horizontal overflow'
  page.set_viewport_size({'width':1440,'height':1050})
  view.get_by_role('button',name='Try the questions again').click()
  expect(view.locator('.lesson-question input:checked')).to_have_count(0)
  for number,key in enumerate(['guided','transfer','exit'],start=1):
   expect(closing.locator('.lesson-question')).to_have_count(1)
   expect(closing.locator('.lesson-assessment-position')).to_have_text(f'Question {number} of 3')
   wrong=next(o['id'] for o in chapter_one[key]['options'] if o['id']!=chapter_one[key]['answer'])
   view.locator(f'[data-question="{key}"] input[value="{wrong}"]').check()
   closing.get_by_role('button',name='Finish practice' if number==3 else 'Next question →').click()
  expect(closing.get_by_role('heading',name='Answers overview')).to_be_focused()
  expect(closing.locator('.lesson-question')).to_have_count(3)
  expect(closing.get_by_role('button',name='Next question →')).to_have_count(0)
  for key in ['guided','transfer','exit']:
   original=view.locator(f'[data-question="{key}"] input:checked')
   expect(original).to_have_value(chapter_one[key]['answer'])
   expect(original).to_be_disabled()
  view.get_by_role('button',name='Finish review',exact=True).click()
  assert '1 / 12 lessons completed · 15 lesson XP' in view.locator('.lesson-total').inner_text()
  # Chapter 2 uses the same reading flow and keeps the reviewed assessment.
  chapter_two=next(lesson for lesson in COURSE['lessons'] if lesson['lesson_id']=='br-02')
  def open_chapter_two():
   page.evaluate("()=>import('/js/lessons-ui.js').then(m=>m.openLessons('br-02'))")
  view.locator('.lesson-module').nth(1).get_by_role('button',name='Start lesson',exact=True).click()
  expect(part_heading).to_have_text('Introduction to Subject and Predicate')
  expect(view.locator('.lesson-intro-example > p').first).to_contain_text('brackets')
  preview=view.get_by_role('heading',name='What you’ll see in this chapter')
  expect(preview).to_be_visible()
  expect(preview.locator('+ ol > li')).to_have_count(3)
  expect(preview.locator('+ ol + .lesson-key-terms dt')).to_have_text(['Subject','Predicate','Category','Function'])
  introductory_split=view.get_by_text('[The robins] [sing].',exact=True)
  expect(introductory_split).to_be_visible()
  expect(view.get_by_text('Subject and predicate name their jobs',exact=False)).to_be_visible()
  opening=view.get_by_role('region',name='Check what you know')
  expect(opening.locator('legend')).to_have_text(chapter_two['predict']['prompt'])
  opening.locator('input[value="a"]').click()
  opening.get_by_role('button',name='Next question →').click()
  page.reload(wait_until='domcontentloaded')
  page.locator('.sidebar-item[data-view="lessons"]').click()
  open_chapter_two()
  expect(opening.locator('.lesson-assessment-position')).to_have_text('Question 2 of 3')
  opening.locator('input[value="a"]').click()
  opening.get_by_role('button',name='Next question →').click()
  expect(opening.locator('.lesson-assessment-position')).to_have_text('Question 3 of 3')
  opening.locator('input[value="c"]').click()
  opening.get_by_role('button',name='Finish knowledge check').click()
  expect(view.locator('.constituent-pre-test-status')).to_have_text('Knowledge check complete. 2 of 3 correct.')
  view.get_by_role('button',name='Next →',exact=True).click()
  expect(part_heading).to_have_text('Finding the Subject and Predicate')
  expect(view.get_by_role('heading',name='What kind of group is it?')).to_be_visible()
  split=view.get_by_role('group',name='Select the last word of the subject.')
  split.get_by_role('button',name='End the subject after word 2, robins').press('Enter')
  expect(split.locator('+ .lesson-feedback')).to_contain_text('which robins')
  boundary=split.get_by_role('button',name='End the subject after word 5, gate')
  boundary.press('Space')
  expect(boundary).to_have_attribute('aria-pressed','true')
  expect(split.locator('+ .lesson-feedback')).to_contain_text('Subject The robins near the gate')
  expect(split.locator('+ .lesson-feedback')).to_contain_text('Predicate are singing softly')
  expect(view.locator('article input[type=radio]')).to_have_count(0)
  methods=view.get_by_role('heading',name='Check the split').locator('+ ul > li')
  expect(methods).to_have_count(3)
  expect(methods.nth(0)).to_contain_text('Are [the robins near the gate] singing softly?')
  expect(methods.nth(1)).to_contain_text('They are singing softly.')
  expect(methods.nth(2)).to_contain_text('including “are”')
  view.get_by_role('button',name='← Previous',exact=True).click()
  expect(view.locator('.constituent-pre-test-status')).to_have_text('Knowledge check complete. 2 of 3 correct.')
  view.get_by_role('button',name='Next →',exact=True).click()
  view.get_by_role('button',name='Next →',exact=True).click()
  expect(part_heading).to_have_text('Reading and Building the NP/VP Tree')
  assert view.get_by_role('heading',name='What the triangles show').bounding_box()['y'] < view.locator('.canonical-viewport').bounding_box()['y']
  expect(view.locator('.lesson-tree-step-number')).to_have_text(['1','2','3'])
  view.get_by_role('button',name='Subject',exact=True).click()
  expect(view.locator('.lesson-tree-observation > .constituent-selection')).to_be_visible()
  expect(view.locator('.lesson-word-traced')).to_have_text('The robins')
  expect(view.locator('.constituent-selection mark')).to_have_text(['The','robins'])
  view.get_by_role('button',name='Inspect B-R VP for sing',exact=True).press('Enter')
  expect(view.locator('.lesson-word-traced')).to_have_text('sing')
  expect(view.locator('.constituent-caption')).to_contain_text('Category: VP · Function: predicate')
  view.get_by_role('button',name='Predicate',exact=True).click()
  expect(view.locator('.lesson-tree-focus text').first).to_have_text('VP')
  view.get_by_text('Tree notation',exact=True).click()
  practice=view.get_by_role('heading',name='Find the full predicate',exact=True)
  expect(practice).to_be_hidden()
  longer=view.get_by_role('button',name='Try the longer sentence',exact=True)
  longer.press('Enter')
  expect(longer).to_be_focused()
  expect(practice).to_be_visible()
  expect(view.locator('.lesson-tree-step-number')).to_have_count(0)
  assert practice.bounding_box()['y'] < view.get_by_role('heading',name='Build your first labelled tree').bounding_box()['y']
  expect(view.locator('.lesson-word-traced')).to_have_count(0)
  view.get_by_role('button',name='Inspect B-R NP for The robins near the gate',exact=True).press('Enter')
  expect(view.locator('.lesson-word-traced')).to_have_text('The robins near the gate')
  expect(view.locator('.constituent-caption')).to_contain_text('Category: NP · Function: subject')
  expect(view.get_by_text('Follow the other branch from S.',exact=False)).to_be_visible()
  view.get_by_role('button',name='VP',exact=True).click()
  expect(view.locator('.lesson-word-traced')).to_have_text('are singing softly')
  expect(view.get_by_text('The VP covers all three words',exact=False)).to_be_visible()
  view.get_by_role('button',name='Short sentence',exact=True).click()
  expect(practice).to_be_hidden()
  expect(view.locator('.lesson-notation > dl').get_by_text('△',exact=True)).to_be_visible()
  view.get_by_text('Tree notation',exact=True).click()

  labelled=view.get_by_role('region',name='Build your first labelled tree exercise')
  canvas=labelled.locator('#builderCanvas')
  expect(canvas).to_be_visible()
  expect(labelled.locator('#builderTools')).to_have_count(0)
  page.evaluate("window.practiceProgress=localStorage.getItem('syntutor:lessons:v1:guest')")
  canvas.scroll_into_view_if_needed()
  def builder_point(kind, label):
   return page.evaluate("""async ([kind,label]) => {
    const {canvasGuideBox, builderModel}=await import('/js/syntax-builder-ui.js');
    const box=canvasGuideBox({kind:kind==='word'?'phrase':kind,type:kind==='word'?'NP':label});
    const center=[box.left+box.width/2,box.top+box.height/2];
    if(kind!=='word')return center;
    const nodes=Object.values(builderModel().nodes);
    const word=nodes.find(node=>node.text===label);
    const np=nodes.find(node=>node.type==='NP');
    const scale=box.width/(np.w+24);
    return [center[0]+(word.x+word.w/2-np.x-np.w/2)*scale,
            center[1]+(word.y+word.h/2-np.y-np.h/2)*scale];
   }""",[kind,label])
  def drag_branch(parent, kind, label):
   page.mouse.move(*builder_point('dot',parent))
   page.mouse.down()
   page.mouse.move(*builder_point(kind,label),steps=8)
   page.mouse.up()

  for label, x, y in [('S',300,55),('NP',250,115),('VP',400,115)]:
   canvas.click(button='right',position={'x':x,'y':y})
   menu=page.locator('.builder-menu')
   expect(menu.locator('.builder-menu-grid button')).to_have_text(['S','NP','VP'])
   menu.get_by_role('button',name=label,exact=True).click()
  drag_branch('S','phrase','NP')
  drag_branch('S','phrase','VP')
  drag_branch('NP','word','The')
  drag_branch('NP','word','robins')
  drag_branch('VP','word','sing')
  drag_branch('NP','phrase','VP')
  labelled.get_by_role('button',name='Check construction').click()
  expect(labelled.get_by_role('status')).to_contain_text('both directly under S')
  canvas.scroll_into_view_if_needed()
  drag_branch('S','phrase','VP')
  labelled.get_by_role('button',name='Check construction').click()
  expect(labelled.get_by_role('status')).to_contain_text('Collapse NP')
  for label in ['NP','VP']:
   canvas.scroll_into_view_if_needed()
   page.mouse.click(*builder_point('phrase',label),button='right')
   page.get_by_role('button',name='Collapse to triangle',exact=True).click()
  labelled.get_by_role('button',name='Check construction').click()
  expect(labelled.get_by_role('status')).to_contain_text('Your tree matches')
  page.screenshot(path=str(OUT/'br-02-builder-desktop.png'),full_page=True)

  expect(view.get_by_role('button',name='Try in Syntax Builder')).to_have_count(0)

  page.set_viewport_size({'width':390,'height':844})
  assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Chapter 2 article has horizontal overflow'
  view.locator('.canonical-viewport').scroll_into_view_if_needed()
  page.screenshot(path=str(OUT/'br-02-mobile-tree.png'),full_page=True)
  # Restart the exercise independently and build with the four guide actions.
  view.get_by_role('button',name='Next →',exact=True).click()
  expect(part_heading).to_have_text('Applying the Split')
  contrast=view.locator('[data-question="np-function"]')
  contrast.locator('input').nth(1).check()
  expect(contrast.locator('+ .lesson-feedback')).to_contain_text('now inside the predicate VP')
  highlighted=view.locator('.lesson-word-traced')
  expect(highlighted).to_be_visible()
  expect(highlighted).to_have_text('the robins')
  assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Chapter 2 contrast tree has horizontal overflow'
  transfer=view.get_by_role('region',name='Build a tree for a new sentence exercise')
  expect(transfer.locator('#builderCanvas')).to_be_visible()
  expect(transfer.locator('#builderTools')).to_have_count(0)
  transfer.get_by_role('button',name='Guide me').click()
  transfer_steps=transfer.locator('.first-tree-guide button')
  expect(transfer_steps).to_have_count(4)
  for row in transfer_steps.all():
   row.press('Enter')
  expect(transfer.get_by_role('status')).to_contain_text('NP covers “The gate by our house”')
  assert page.evaluate("localStorage.getItem('syntutor:lessons:v1:guest')===window.practiceProgress")
  view.get_by_role('button',name='← Previous',exact=True).click()
  labelled.get_by_role('button',name='Check construction').click()
  expect(labelled.get_by_role('status')).to_contain_text('NP covers “The robins”')
  view.get_by_role('button',name='Next →',exact=True).click()
  transfer.get_by_role('button',name='Check construction').click()
  expect(transfer.get_by_role('status')).to_contain_text('NP covers “The gate by our house”')
  page.evaluate("localStorage.removeItem('syntutor:builder:v1:guest:inline:br-02')")
  view.get_by_role('button',name='← Previous',exact=True).click()
  labelled.get_by_role('button',name='Guide me').click()
  guide=labelled.locator('.first-tree-guide')
  expect(guide.get_by_role('button')).to_have_count(4)
  guide.get_by_role('button').nth(1).press('Enter')
  expect(labelled.get_by_role('status')).to_contain_text('first')
  for row in guide.get_by_role('button').all():
   row.press('Enter')
  expect(labelled.get_by_role('status')).to_contain_text('Your tree matches')
  canvas.scroll_into_view_if_needed()
  cdp=page.context.new_cdp_session(page)
  x,y=builder_point('phrase','NP')
  cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
  expand=page.get_by_role('button',name='Expand triangle',exact=True)
  expect(expand).to_be_visible()
  cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
  expand.click()
  labelled.get_by_role('button',name='Check construction').click()
  expect(labelled.get_by_role('status')).to_contain_text('Collapse NP')
  guide.get_by_role('button').last.press('Enter')
  expect(labelled.get_by_role('status')).to_contain_text('Your tree matches')
  canvas.screenshot(path=str(OUT/'br-02-builder-mobile.png'))

  view.get_by_role('button',name='Next →',exact=True).click()
  view.get_by_role('button',name='Next →',exact=True).click()
  expect(part_heading).to_have_text('Chapter Recap')
  expect(view.get_by_role('heading',name='Put it into practice')).to_be_visible()
  expect(view.get_by_role('heading',name='Cambridge insight: sentence and clause')).to_have_count(0)
  expect(view.locator('article .lesson-sources')).to_have_count(1)
  view.get_by_role('button',name='Check what you learned',exact=True).click()
  expect(part_heading).to_have_text('Check what you learned')
  closing=view.get_by_role('region',name='Chapter knowledge check')
  page.evaluate("window.beforeWarmup=localStorage.getItem('syntutor:lessons:v1:guest')")
  expect(view.get_by_role('heading',name='Unscored warm-up')).to_be_visible()
  warmup_answer=view.get_by_text('[The children by the window] [were reading quietly]',exact=True)
  expect(warmup_answer).to_be_hidden()
  view.get_by_text('Reveal the analysis',exact=True).press('Enter')
  expect(warmup_answer).to_be_visible()
  assert page.evaluate("localStorage.getItem('syntutor:lessons:v1:guest')===window.beforeWarmup")
  expect(closing.locator('.lesson-tree-outline')).not_to_contain_text('NP')
  for number,(key,action) in enumerate([('guided','Next question →'),('transfer','Next question →'),('exit','Complete lesson')],1):
   expect(closing.locator('.lesson-assessment-position')).to_have_text(f'Question {number} of 3')
   expect(closing.locator('.lesson-question')).to_have_count(1)
   question=closing.locator(f'[data-question="{key}"]')
   expect(question.locator('legend')).to_have_text(chapter_two[key]['prompt'])
   question.locator(f'input[value="{chapter_two[key]["answer"]}"]').check()
   expect(question.locator('.lesson-feedback.correct')).to_be_visible()
   page.set_viewport_size({'width':1440,'height':1050})
   page.reload(wait_until='domcontentloaded')
   page.locator('.sidebar-item[data-view="lessons"]').click()
   open_chapter_two()
   page.set_viewport_size({'width':390,'height':844})
   expect(question.locator('input:checked')).to_have_value(chapter_two[key]['answer'])
   closing.get_by_role('button',name=action,exact=True).click()
  expect(view.locator('.lesson-save-status')).to_contain_text('15 lesson XP awarded')
  expect(closing.get_by_role('heading',name='Answers overview')).to_be_visible()
  expect(closing.locator('.lesson-question')).to_have_count(3)
  expect(closing.get_by_role('button',name='Next question →')).to_have_count(0)
  page.evaluate("window.chapterTwoComplete=localStorage.getItem('syntutor:lessons:v1:guest')")
  view.get_by_role('button',name='Try the questions again').click()
  for number in range(1,4):
   expect(closing.locator('.lesson-assessment-position')).to_have_text(f'Question {number} of 3')
   expect(closing.locator('input:checked')).to_have_count(0)
   closing.locator('input').last.check()
   closing.get_by_role('button',name='Finish practice' if number==3 else 'Next question →').click()
  expect(closing.get_by_role('heading',name='Answers overview')).to_be_focused()
  assert page.evaluate("localStorage.getItem('syntutor:lessons:v1:guest')===window.chapterTwoComplete")
  view.get_by_role('button',name='Finish review',exact=True).click()
  assert '2 / 12 lessons completed · 30 lesson XP' in view.locator('.lesson-total').inner_text()
  page.set_viewport_size({'width':1440,'height':1050})
  # Complete the rest of Syntax Foundations through the shared article flow.
  for lesson in COURSE['lessons'][2:]:
   ident=lesson['lesson_id']
   print('Checking',ident,flush=True)
   page.evaluate("id=>import('/js/lessons-ui.js').then(m=>m.openLessons(id))",ident)
   expect(part_heading).to_contain_text('Introduction to')
   if ident=='cgel-clauses':
    expect(view.locator('.constituent-chapter > p')).to_have_text('Cambridge · Chapter 2')
   expect(view.get_by_role('heading',name='What this chapter covers')).to_be_visible()
   expect(view.get_by_role('heading',name='What you’ll see in this chapter')).to_be_visible()
   key_terms=view.locator('article > ul + .lesson-key-terms')
   expect(key_terms.get_by_role('heading',name='Key terms')).to_be_visible()
   assert key_terms.locator('dt').count() in (3,4)
   expect(key_terms.get_by_text('In this chapter',exact=True)).to_have_count(key_terms.locator('dt').count())
   expect(key_terms.locator('dl')).to_have_css('background-color','rgba(0, 0, 0, 0)')
   expect(view.locator('.lesson-closing-result')).to_have_count(0)
   expect(view.locator('.lesson-intro-example > p')).to_have_count(3)
   expect(view.locator('.lesson-intro-example .lesson-example-sentence')).to_be_visible()
   expect(view.locator('.lesson-intro-example')).to_have_css('background-color','rgb(255, 255, 255)')
   expect(view.get_by_role('region',name='Check what you know')).to_be_visible()
   prediction=view.locator('[data-question="predict"]')
   expect(prediction.locator('legend')).to_have_text(lesson['predict']['prompt'])
   next_button=view.get_by_role('button',name='Next →',exact=True)
   expect(next_button).to_be_disabled()
   prediction.locator('input').first.click()
   for number in [2,3]:
    view.get_by_role('button',name='Next question →',exact=True).click()
    expect(view.locator('.lesson-assessment-position')).to_have_text(f'Question {number} of 3')
    prediction.locator('input').first.click()
   view.get_by_role('button',name='Finish knowledge check').click()
   extras_correct={'br-03':1,'br-04':0,'br-05':1,'br-06':1,'br-07':0,
                   'br-08':0,'br-09':1,'br-10':1,'br-11':0,'cgel-clauses':1}[ident]
   score=extras_correct + (lesson['predict']['options'][0]['id']==lesson['predict']['answer'])
   expect(view.locator('.constituent-pre-test-status')).to_have_text(f'Knowledge check complete. {score} of 3 correct.')
   next_button.click()
   expect(view.locator('article h3')).to_have_count(4)
   expect(view.locator('.lesson-key-terms')).to_have_count(0)
   expect(view.locator('article > ul:not(.lesson-transfer-context) > li')).to_have_count(2)
   next_button.click()
   worked=lesson['worked_example']
   expect(view.locator('article > .lesson-example-sentence')).to_have_text(worked['sentence'])
   if worked.get('tree'):
    step_controls=view.get_by_role('group',name='Explore the worked tree')
    viewport=view.locator('.canonical-viewport')
    captions=[]
    skipped={'br-03':1,'br-09':2}.get(ident)
    visible_steps=[step for i,step in enumerate(worked['steps']) if i!=skipped]
    step_count=len(visible_steps)+(2 if ident=='br-09' else 0)
    expect(step_controls.locator('.lesson-tree-step-number')).to_have_text([str(i+1) for i in range(step_count)])
    for i, step in enumerate(visible_steps):
     step_button=step_controls.get_by_role('button').nth(i)
     step_button.press('Enter')
     expect(step_button).to_have_attribute('aria-pressed','true')
     observation=view.locator('.lesson-tree-observation')
     expect(observation.locator('.constituent-selection')).to_be_visible()
     expect(observation).to_have_css('background-color','rgb(255, 255, 255)')
     captions.append(observation.locator('.constituent-caption').inner_text())
     expect(view.locator('svg .lesson-tree-focus')).to_have_attribute('data-node-id',step['focus_node_id'])
    assert all(captions) and len(set(captions)) == len(visible_steps)
    expect(viewport.get_by_role('button',name='Fit B-R tree')).to_be_visible()
    expect(view.get_by_text('Read the tree as text',exact=True)).to_have_count(0)
    outline=view.get_by_role('group',name='Tree structure')
    expect(outline.get_by_role('list')).not_to_have_count(0)
    expect(outline.get_by_role('button')).to_have_count(0)
    expect(view.locator('.lesson-shared-evidence summary')).to_have_text('Explanation')
    assert viewport.bounding_box()['y'] < view.locator('.lesson-shared-evidence').bounding_box()['y']
    if ident=='br-08':
     expect(viewport.locator('svg text').filter(has_text=re.compile(r'^S′$'))).to_have_count(1)
    if ident in {'br-03','br-05','br-06'}:
     comparison=view.get_by_role('group',name='Compare worked structures')
     alternative=comparison.get_by_role('button').nth(1)
     expect(comparison.locator('.lesson-tree-step-number')).to_have_count(0)
     alternative.press('Enter')
     expect(alternative).to_have_attribute('aria-pressed','true')
     expect(step_controls).to_be_hidden()
     expect(view.locator('.constituent-caption')).to_contain_text({
      'br-03':'DEG branch has disappeared','br-05':'whole predicate','br-06':'adds a time',
     }[ident])
     comparison.get_by_role('button').first.press('Enter')
     expect(step_controls).to_be_visible()
    if ident=='br-07':
     step_controls.get_by_role('button',name='Find the noun').press('Enter')
     expect(viewport.locator('.lesson-branch-traced')).to_have_count(2)
    if ident=='br-09':
     expect(viewport.locator('svg text').filter(has_text=re.compile(r'^•'))).to_have_count(2)
     for parent, control in [('PROG','Find the PROG gap'),('NP','Trace the NP gap')]:
      viewport.get_by_role('button',name=f'Inspect B-R gap under {parent}',exact=True).press('Enter')
      expect(step_controls.get_by_role('button',name=control)).to_have_attribute('aria-pressed','true')
      expect(view.locator('.constituent-selection')).to_contain_text(f'Gap under {parent}')
      expect(view.locator('.constituent-caption')).to_contain_text(f'The dot under {parent}')
     viewport.get_by_role('button',name='Inspect B-R NP for Nora',exact=True).press('Enter')
     expect(step_controls.locator('[aria-pressed=true]')).to_have_count(0)
     expect(view.locator('.constituent-caption')).to_have_text('NP is directly under S.')
    if ident=='br-10':
     expect(viewport.locator('svg text').filter(has_text=re.compile(r'^\[-tense\]$'))).to_have_count(1)
     expect(viewport.locator('svg text').filter(has_text=re.compile(r'^AUX$'))).to_have_count(0)
    page.screenshot(path=str(OUT/f'{ident}-desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    viewport.scroll_into_view_if_needed()
    steps_box=step_controls.bounding_box()
    assert 0 <= viewport.bounding_box()['y']-(steps_box['y']+steps_box['height']) <= 16
    assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), ident
    page.screenshot(path=str(OUT/f'{ident}-mobile-tree.png'),full_page=True)
    editor=view.locator('.first-tree-builder')
    expect(editor.locator('#builderCanvas')).to_be_visible()
    editor.get_by_role('button',name='Check construction').click()
    expect(editor.get_by_role('status')).to_contain_text('target branch is still detached')
    page.evaluate("window.beforeBranch=localStorage.getItem('syntutor:lessons:v1:guest')")
    success={
     'br-03':'sisters under AP', 'br-04':'shares VP with V',
     'br-05':'sisters under the outer VP', 'br-06':'share the higher VP',
     'br-07':'share NP as their parent', 'br-08':'sisters under S′',
     'br-09':'object-gap NP sits beside V', 'br-10':'shares the higher VP',
    }[ident]
    if ident in {'br-03','br-08'}:
     parent,child={'br-03':('AP','A'),'br-08':('S-bar','C')}[ident]
     editor.locator('#builderCanvas').scroll_into_view_if_needed()
     if ident=='br-03':
      drag_branch('DEG','phrase',child)
      editor.get_by_role('button',name='Check construction').click()
      expect(editor.get_by_role('status')).to_contain_text('attached to DEG')
      editor.get_by_role('button',name='Undo',exact=True).click()
      editor.get_by_role('button',name='Check construction').click()
      expect(editor.get_by_role('status')).to_contain_text('target branch is still detached')
     drag_branch(parent,'phrase',child)
     editor.get_by_role('button',name='Check construction').click()
     expect(editor.get_by_role('status')).to_contain_text(success)
    editor.get_by_role('button',name='Guide me').click()
    for step in editor.locator('.first-tree-guide button').all():
     step.press('Enter')
    expect(editor.get_by_role('status')).to_contain_text(success)
    editor.get_by_role('button',name='Restart exercise').click()
    expect(editor.get_by_role('status')).to_contain_text('Starting tree restored')
    editor.get_by_role('button',name='Check construction').click()
    expect(editor.get_by_role('status')).to_contain_text('target branch is still detached')
    editor.get_by_role('button',name='Undo',exact=True).click()
    editor.get_by_role('button',name='Check construction').click()
    expect(editor.get_by_role('status')).to_contain_text(success)
    assert page.evaluate("localStorage.getItem('syntutor:lessons:v1:guest')===window.beforeBranch")
    page.set_viewport_size({'width':1440,'height':1050})
   else:
    expect(view.locator('article ol li')).to_have_text([step['text'] for step in worked['steps']])
    expect(view.locator('svg')).to_have_count(0)
    worked_answer=view.get_by_text('Show the worked answer',exact=True)
    expect(worked_answer.locator('+ p')).to_be_hidden()
    worked_answer.press('Enter')
    expect(worked_answer.locator('+ p')).to_be_visible()
   next_button.click()
   expect(view.locator('article .lesson-example-sentence')).to_be_visible()
   page.set_viewport_size({'width':390,'height':844})
   transfer_practice=view.locator('.lesson-transfer')
   assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), ident
   page.evaluate("window.beforeTransfer=localStorage.getItem('syntutor:lessons:v1:guest')")
   if ident=='br-11':
    first_input=transfer_practice.get_by_label('First input')
    second_input=transfer_practice.get_by_label('Second input')
    apply_rule=transfer_practice.get_by_role('button',name='Apply the rule')
    first_input.select_option('Maya smiles')
    second_input.select_option('Maya smiles and')
    apply_rule.click()
    expect(transfer_practice.get_by_role('status')).to_contain_text('complete sentence after it')
    second_input.select_option('Leo waves')
    apply_rule.press('Enter')
    expect(transfer_practice.get_by_role('status')).to_contain_text('[Maya smiles] and [Leo waves]')
    transfer_practice.get_by_role('button',name='Use this result again').click()
    first_input.select_option('Maya smiles and Leo waves')
    second_input.select_option('Maya smiles')
    apply_rule.press('Enter')
    expect(transfer_practice.get_by_role('status')).to_contain_text('[Maya smiles and Leo waves] and [Maya smiles]')
    transfer_practice.get_by_role('button',name='Start again').click()
    expect(first_input).to_have_value('')
   else:
    answers={
     'br-03': [(4,), (3,4)], 'br-04': [(3,5)], 'br-05': [(2,5)],
     'br-06': [(3,5), (2,)], 'br-07': [(2,), (3,)], 'br-08': [(2,), (3,)],
     'br-09': [(0,), (1,), (2,), (3,)], 'br-10': [(3,5), (3,4)],
     'cgel-clauses': [(0,6), (3,4), (5,6)],
    }[ident]
    check_selection=transfer_practice.get_by_role('button',name='Check selection')
    choices=transfer_practice.get_by_role('group').get_by_role('button')
    for i, indices in enumerate(answers):
     expect(check_selection).to_be_disabled()
     if i==0:
      wrong=(indices[0]+1) % choices.count()
      choices.nth(wrong).press('Space')
      check_selection.click()
      expect(transfer_practice.locator('.retry')).to_be_visible()
     for index in indices:
      choices.nth(index).press('Enter')
     check_selection.click()
     expect(transfer_practice.locator('.correct')).to_be_visible()
     if i<len(answers)-1:
      transfer_practice.get_by_role('button',name='Next part').click()
   assert page.evaluate("localStorage.getItem('syntutor:lessons:v1:guest')===window.beforeTransfer")
   page.set_viewport_size({'width':1440,'height':1050})
   answer=view.get_by_text('Check your analysis',exact=True)
   expect(answer.locator('+ p')).to_be_hidden()
   answer.press('Enter')
   expect(answer.locator('+ p')).to_be_visible()
   if worked.get('tree'):
    view.get_by_role('button',name='← Previous',exact=True).click()
    editor.get_by_role('button',name='Check construction').click()
    expect(editor.get_by_role('status')).to_contain_text(success)
    next_button.click()
   next_button.click()
   expect(part_heading).to_have_text('Chapter Recap')
   if ident!='cgel-clauses':
    expect(view.get_by_role('heading',name='What this chapter showed').locator('+ p')).to_be_visible()
   expect(view.get_by_role('heading',name='Try a quick check')).to_be_visible()
   quick_answer=view.get_by_text('Show the answer',exact=True)
   expect(quick_answer.locator('+ p')).to_be_hidden()
   quick_answer.press('Enter')
   expect(quick_answer.locator('+ p')).to_be_visible()
   references=view.locator('article .lesson-sources')
   references.locator('summary').click()
   expect(references.locator('li').first).to_be_visible()
   view.get_by_role('button',name='Check what you learned').click()
   expect(part_heading).to_have_text('Check what you learned')
   expect(view.locator('.lesson-sources')).to_have_count(0)
   post_test=view.get_by_role('region',name='Chapter knowledge check')
   for key, action_name in [('guided','Next question →'),('transfer','Next question →'),('exit','Complete lesson')]:
    question=post_test.locator(f'[data-question="{key}"]')
    expect(question.locator('legend')).to_have_text(lesson[key]['prompt'])
    action=view.get_by_role('button',name=action_name,exact=True)
    if key=='guided' and ident in {'br-04','br-10'}:
     target=lesson[key]['build_target']
     masked=post_test.locator(f'svg [data-node-id="{target["node_id"]}"]')
     expect(masked.locator('.br-feature-row')).to_have_text('[?]')
     outline=post_test.get_by_role('group',name='Tree structure')
     expect(outline).to_contain_text('[?]')
     expect(outline).not_to_contain_text(f'[{target["expected"]}]')
    if key=='exit':
     wrong=next(o['id'] for o in lesson[key]['options'] if o['id']!=lesson[key]['answer'])
     question.locator(f'input[value="{wrong}"]').check()
     expect(question.locator('.lesson-feedback.retry')).to_contain_text('Try again.')
     expect(action).to_be_disabled()
    question.locator(f'input[value="{lesson[key]["answer"]}"]').check()
    expect(question.locator('.lesson-feedback.correct')).to_be_visible()
    if key=='guided' and ident in {'br-04','br-10'}:
     expect(masked.locator('.br-feature-row')).to_have_text(f'[{target["expected"]}]')
    action.click()
   expect(view.locator('.lesson-save-status')).to_contain_text('15 lesson XP awarded')
   expect(post_test.get_by_role('heading',name='Answers overview')).to_be_visible()
   expect(post_test.locator('.lesson-question')).to_have_count(3)
   if not worked.get('tree'):
    expect(view.locator('svg')).to_have_count(0)
   if ident in {'br-09','br-11','cgel-clauses'}:
    page.evaluate("window.beforeRetake=localStorage.getItem('syntutor:lessons:v1:guest')")
    view.get_by_role('button',name='Try the questions again').click()
    for number in range(1,4):
     expect(post_test.locator('.lesson-assessment-position')).to_have_text(f'Question {number} of 3')
     post_test.locator('input').first.check()
     post_test.get_by_role('button',name='Finish practice' if number==3 else 'Next question →').click()
    expect(post_test.get_by_role('heading',name='Answers overview')).to_be_visible()
    assert page.evaluate("localStorage.getItem('syntutor:lessons:v1:guest')===window.beforeRetake")
  page.evaluate("()=>import('/js/lessons-ui.js').then(m=>m.openLessons('br-01'))")
  expect(part_heading).to_have_text(chapter_one_titles[0])
  expect(view.get_by_text('Completed for this content version. Reviewing cannot award another 15 XP.',exact=True)).to_have_count(0)
  expect(view.locator('.lesson-closing-result')).to_have_text('Closing check complete. 3 of 3 correct.')
  expect(view.locator('.constituent-pre-test-status')).to_have_text('Knowledge check complete. 2 of 3 correct.')
  expect(view.locator('[data-question="predict"]')).to_have_count(0)
  for _ in range(4):
   view.get_by_role('button',name='Next →',exact=True).click()
  view.get_by_role('button',name='Check what you learned',exact=True).click()
  view.get_by_role('button',name='Finish review',exact=True).click()
  assert '12 / 12 lessons completed · 180 lesson XP' in view.locator('.lesson-total').inner_text()
  expect(meter).to_have_attribute('value','6')
  expect(summary.get_by_role('progressbar')).to_have_attribute('value','12')
  expect(first.get_by_role('button',name='Review lesson',exact=True)).to_be_visible()
  expect(first).not_to_contain_text('XP')
  view.get_by_role('button',name='Grammar and Analysis',exact=True).click()
  assert view.locator('.curriculum-card').count()==1
  assert view.get_by_text('17 further topics planned — not published',exact=True).count()==1
  page.reload(wait_until='domcontentloaded');page.locator('.sidebar-item[data-view="lessons"]').click()
  view.locator('.lesson-total').wait_for();assert '180 lesson XP' in view.locator('.lesson-total').inner_text()
  page.locator('.sidebar-item[data-view="tutor"]').click();assert view.is_hidden()
  page.goto(base+'/#lesson/NP',wait_until='domcontentloaded')
  view.get_by_role('heading',name='DET and NOM inside NP',exact=True).wait_for()
  page.locator('.sidebar-item[data-view="tutor"]').click()
  assert view.is_hidden()
  # Resume a progress record shaped like a pre-rollout Chapter 6 attempt.
  legacy=next(lesson for lesson in COURSE['lessons'] if lesson['lesson_id']=='br-06')
  saved={
   'stage':4,
   'visited':['predict','understand','worked','guided'],
   'responses':{
    'predict':legacy['predict']['answer'],
    'guided':legacy['guided']['answer'],
    'transfer':next(o['id'] for o in legacy['transfer']['options'] if o['id']!=legacy['transfer']['answer']),
   },
   'completed_at':None,
  }
  page.evaluate("""record => {
    const key = 'syntutor:lessons:v1:guest';
    const all = JSON.parse(localStorage.getItem(key));
    all['br-06@1.0.0'] = record;
    localStorage.setItem(key, JSON.stringify(all));
  }""",saved)
  page.goto(base+'/?lesson-progress-check',wait_until='domcontentloaded')
  page.locator('.sidebar-item[data-view="lessons"]').click()
  legacy_card=view.locator('.lesson-module').filter(has=page.get_by_role('heading',name=legacy['title'],exact=True))
  expect(legacy_card.get_by_role('progressbar')).to_have_attribute('value','4')
  legacy_card.get_by_role('button',name='Resume lesson',exact=True).click()
  expect(part_heading).to_have_text('Check what you learned')
  transfer=view.locator('[data-question="transfer"]')
  expect(transfer.locator('input:checked')).to_have_value(saved['responses']['transfer'])
  view.get_by_role('button',name='← Previous',exact=True).click()
  expect(part_heading).to_have_text('Chapter Recap')
  view.get_by_role('button',name='Check what you learned').click()
  expect(transfer.locator('input:checked')).to_have_value(saved['responses']['transfer'])
  assert not parses,parses
  assert not errors,errors
  browser.close()
  print('PASS: 12 lessons; representative desktop/mobile trees; no parser authority; stage gates, wrong-answer feedback, resume/reload, 180 XP once, planned modules and mode teardown.')
finally:server.shutdown();server.server_close();thread.join(2)
