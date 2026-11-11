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
  part_titles=['Predict','Understand','See it','Build it','Apply it','Exit check']
  chapter_one_titles=['Introduction to Constituents and Hierarchy','Identifying Constituents in a Sentence',
                      'Comparing Flat and Nested Trees', 'Structural Ambiguity',
                      'Chapter Recap','Check what you learned']
  page.evaluate("()=>import('/js/lessons-ui.js').then(m=>m.openLessons('br-01'))")
  expect(part_heading).to_have_text(chapter_one_titles[0])
  expect(view.locator('.lesson-tree-canvas')).to_have_count(0)
  expect(view.locator('article')).to_have_attribute('aria-labelledby','constituent-page-title')
  intro=view.get_by_role('heading',name='Check what you know',exact=True)
  opening=view.get_by_role('region',name='Check what you know')
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
  expect(view.locator('.constituent-pre-test-status')).to_have_text('Knowledge check complete.')
  expect(prediction).to_have_count(0)
  expect(next_button).to_be_enabled()
  page.set_viewport_size({'width':1440,'height':1050})
  next_button.click()
  expect(part_heading).to_have_text(chapter_one_titles[1])
  expect(view.get_by_role('heading',name='Test a group with replacement')).to_be_visible()
  view.get_by_role('button',name='near the quiet garden',exact=True).click()
  expect(view.locator('.lesson-tree-focus text')).to_have_text('PHRASE-a')
  view.get_by_role('button',name='← Previous',exact=True).click()
  expect(view.locator('.constituent-pre-test-status')).to_have_text('Knowledge check complete.')
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
  for drawing_name, branches in [('Flat drawing',4),('Nested drawing',5)]:
   view.get_by_role('button',name=drawing_name).click()
   expect(comparison.locator('svg .lesson-branch')).to_have_count(branches)
   traced_words = ['near','the','quiet','garden'] if drawing_name == 'Flat drawing' else ['the','quiet','garden']
   expect(comparison.locator('svg .lesson-word-traced')).to_have_text(traced_words)
   expect(comparison.locator('svg .lesson-branch-traced')).to_have_count(len(traced_words))
   expect(comparison.locator('svg')).to_have_attribute('viewBox',nested_viewbox)
   expect(comparison.get_by_role('button',name='Zoom in B-R tree')).to_be_visible()
   assert comparison.bounding_box()['width']==nested_box['width']
   assert comparison.bounding_box()['height']==nested_box['height']
   expect(comparison.locator('svg text').filter(has_text=re.compile(r'^(near|the|quiet|garden)$'))).to_have_count(4)
  comparison.get_by_role('button',name='Inspect B-R PHRASE-a for PHRASE-a',exact=True).press('Enter')
  expect(comparison.locator('svg .lesson-branch-traced')).to_have_count(5)
  expect(comparison.locator('svg .lesson-word-traced')).to_have_text(['near','the','quiet','garden'])
  comparison.get_by_role('button',name=re.compile(r'^Inspect B-R PHRASE-b\b')).press('Enter')
  expect(comparison.locator('svg .lesson-branch-traced')).to_have_count(3)
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
  exercise.get_by_role('button',name='Guide me').click()
  guide=exercise.locator('.first-tree-guide')
  expect(guide.get_by_role('button')).to_have_count(4)
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
  exercise.get_by_role('button',name='Guide me').click()
  page.set_viewport_size({'width':390,'height':844})
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
  view.get_by_role('button',name='Try the questions again').click()
  expect(view.locator('.lesson-question input:checked')).to_have_count(0)
  for number,key in enumerate(['guided','transfer','exit'],start=1):
   expect(closing.locator('.lesson-question')).to_have_count(1)
   expect(closing.locator('.lesson-assessment-position')).to_have_text(f'Question {number} of 3')
   wrong=next(o['id'] for o in chapter_one[key]['options'] if o['id']!=chapter_one[key]['answer'])
   view.locator(f'[data-question="{key}"] input[value="{wrong}"]').check()
   closing.get_by_role('button',name='Finish practice' if number==3 else 'Next question →').click()
  for key in ['guided','transfer','exit']:
   original=view.locator(f'[data-question="{key}"] input:checked')
   expect(original).to_have_value(chapter_one[key]['answer'])
   expect(original).to_be_disabled()
   if key!='exit':
    closing.get_by_role('button',name='Next question →').click()
  view.get_by_role('button',name='Finish review',exact=True).click()
  assert '1 / 12 lessons completed · 15 lesson XP' in view.locator('.lesson-total').inner_text()
  # Chapter 2 shares the article flow and uses the reviewed M4 activities.
  chapter_two=next(lesson for lesson in COURSE['lessons'] if lesson['lesson_id']=='br-02')
  second=view.locator('.lesson-module').nth(1)
  second.get_by_role('button',name='Start lesson',exact=True).click()
  expect(part_heading).to_have_text('Introduction to Subject and Predicate')
  expect(view.locator('.constituent-pre-test legend')).to_have_text(chapter_two['predict']['prompt'])
  view.locator('[data-question="predict"] input[value="a"]').click()
  expect(view.locator('.constituent-pre-test-status')).to_have_text('Response recorded.')
  view.get_by_role('button',name='Next →',exact=True).click()
  expect(part_heading).to_have_text('Categories and Functions')
  expect(view.get_by_text(chapter_two['teaching'][0]['text'],exact=True)).to_be_visible()
  view.get_by_role('button',name='← Previous',exact=True).click()
  expect(view.locator('.constituent-pre-test-status')).to_have_text('Response recorded.')
  view.get_by_role('button',name='Next →',exact=True).click()
  view.get_by_role('button',name='Next →',exact=True).click()
  expect(part_heading).to_have_text('Reading the NP and VP Branches')
  view.get_by_role('button',name='Subject',exact=True).click()
  expect(view.locator('.lesson-tree-focus text').first).to_have_text('NP')
  view.get_by_role('button',name='Predicate',exact=True).click()
  expect(view.locator('.lesson-tree-focus text').first).to_have_text('VP')
  page.evaluate("window.practiceProgress=localStorage.getItem('syntutor:lessons:v1:guest')")
  view.get_by_role('button',name='Try in Syntax Builder').click()
  builder=page.locator('#builderTools')
  expect(builder.get_by_text('Build “The robins sing”',exact=True)).to_be_visible()
  expect(builder.get_by_label('B-R convention',exact=True)).to_have_value('2')
  expect(builder.get_by_text('Target: Subject, predicate and category — The robins sing',exact=True)).to_be_visible()
  assert page.evaluate("()=>import('/js/syntax-builder-ui.js').then(m=>Object.values(m.builderModel().nodes).map(n=>n.text))")==['The','robins','sing']
  builder.get_by_role('button',name='Return to lesson').click()
  expect(part_heading).to_have_text('Reading the NP and VP Branches')
  assert page.evaluate("localStorage.getItem('syntutor:lessons:v1:guest')===window.practiceProgress")
  page.set_viewport_size({'width':390,'height':844})
  assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Chapter 2 article has horizontal overflow'
  view.locator('.canonical-viewport').scroll_into_view_if_needed()
  page.screenshot(path=str(OUT/'br-02-mobile-tree.png'),full_page=True)
  page.set_viewport_size({'width':1440,'height':1050})
  view.get_by_role('button',name='Next →',exact=True).click()
  expect(part_heading).to_have_text('Sentence and Clause')
  expect(view.get_by_text(chapter_two['cambridge_insights'][0]['text'],exact=True)).to_be_visible()
  view.get_by_role('button',name='Next →',exact=True).click()
  expect(part_heading).to_have_text('Chapter Recap')
  expect(view.locator('article .lesson-sources')).to_have_count(1)
  view.get_by_role('button',name='Start post-test').click()
  expect(part_heading).to_have_text('Chapter Post-test')
  expect(view.locator('.lesson-sources')).to_have_count(0)
  for key, action in [('guided','Next question →'),('transfer','Next question →'),('exit','Complete lesson')]:
   question=view.locator(f'[data-question="{key}"]')
   expect(question.locator('legend')).to_have_text(chapter_two[key]['prompt'])
   question.locator(f'input[value="{chapter_two[key]["answer"]}"]').check()
   expect(question.locator('.lesson-feedback.correct')).to_be_visible()
   view.get_by_role('button',name=action,exact=True).click()
  expect(view.locator('.lesson-save-status')).to_contain_text('15 lesson XP awarded')
  view.get_by_role('button',name='Retake post-test').click()
  expect(view.locator('.lesson-question input:checked')).to_have_count(0)
  view.get_by_role('button',name='← All lessons',exact=True).click()
  assert '2 / 12 lessons completed · 30 lesson XP' in view.locator('.lesson-total').inner_text()
  # Complete the rest of Syntax Foundations through the shared article flow.
  for lesson in COURSE['lessons'][2:11]:
   ident=lesson['lesson_id']
   print('Checking',ident,flush=True)
   page.evaluate("id=>import('/js/lessons-ui.js').then(m=>m.openLessons(id))",ident)
   expect(part_heading).to_contain_text('Introduction to')
   expect(view.get_by_role('region',name='Pre-test')).to_be_visible()
   prediction=view.locator('[data-question="predict"]')
   expect(prediction.locator('legend')).to_have_text(lesson['predict']['prompt'])
   next_button=view.get_by_role('button',name='Next →',exact=True)
   expect(next_button).to_be_disabled()
   prediction.locator('input').first.click()
   expect(view.locator('.constituent-pre-test-status')).to_have_text('Response recorded.')
   next_button.click()
   for block in lesson['teaching']:
    expect(view.get_by_text(block['text'],exact=True)).to_be_visible()
   next_button.click()
   worked=lesson['worked_example']
   expect(view.get_by_text(worked['sentence'],exact=True)).to_be_visible()
   if worked.get('tree'):
    step_controls=view.get_by_role('group',name='Explore the worked tree')
    viewport=view.locator('.canonical-viewport')
    for i, step in enumerate(worked['steps']):
     step_button=step_controls.get_by_role('button').nth(i)
     step_button.press('Enter')
     expect(step_button).to_have_attribute('aria-pressed','true')
     expect(view.locator('.constituent-caption')).to_have_text(step['text'])
     expect(view.locator('svg .lesson-tree-focus')).to_have_attribute('data-node-id',step['focus_node_id'])
    expect(viewport.get_by_role('button',name='Fit B-R tree')).to_be_visible()
    expect(view.get_by_text('Read the tree as text',exact=True)).to_have_count(0)
    outline=view.get_by_role('group',name='Tree structure')
    expect(outline.get_by_role('list')).not_to_have_count(0)
    expect(outline.get_by_role('button')).to_have_count(0)
    expect(view.locator('.lesson-shared-evidence summary')).to_have_text('Explanation')
    assert viewport.bounding_box()['y'] < view.locator('.lesson-shared-evidence').bounding_box()['y']
    if ident=='br-08':
     expect(viewport.locator('svg text').filter(has_text=re.compile(r'^S′$'))).to_have_count(1)
    if ident=='br-09':
     expect(viewport.locator('svg text').filter(has_text=re.compile(r'^•'))).to_have_count(2)
    if ident=='br-10':
     expect(viewport.locator('svg text').filter(has_text=re.compile(r'^\[-tense\]$'))).to_have_count(1)
     expect(viewport.locator('svg text').filter(has_text=re.compile(r'^AUX$'))).to_have_count(0)
    if ident in {'br-03','br-06','br-09','br-10'}:
     page.screenshot(path=str(OUT/f'{ident}-desktop.png'),full_page=True)
     page.set_viewport_size({'width':390,'height':844})
     viewport.scroll_into_view_if_needed()
     steps_box=step_controls.bounding_box()
     assert 0 <= viewport.bounding_box()['y']-(steps_box['y']+steps_box['height']) <= 16
     assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), ident
     page.screenshot(path=str(OUT/f'{ident}-mobile-tree.png'),full_page=True)
     page.set_viewport_size({'width':1440,'height':1050})
   else:
    expect(view.locator('article ol li')).to_have_text([step['text'] for step in worked['steps']])
    expect(view.locator('svg')).to_have_count(0)
   next_button.click()
   for insight in lesson['cambridge_insights']:
    expect(view.get_by_text(insight['text'],exact=True)).to_be_visible()
   next_button.click()
   expect(part_heading).to_have_text('Chapter Recap')
   references=view.locator('article .lesson-sources')
   references.locator('summary').click()
   expect(references.locator('li').first).to_be_visible()
   view.get_by_role('button',name='Start post-test').click()
   expect(part_heading).to_have_text('Chapter Post-test')
   expect(view.locator('.lesson-sources')).to_have_count(0)
   post_test=view.get_by_role('region',name='Post-test questions')
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
   if ident=='br-11':
    expect(view.locator('svg')).to_have_count(0)
  # The Cambridge companion still follows its original sequence.
  companion=COURSE['lessons'][-1]
  page.evaluate("()=>import('/js/lessons-ui.js').then(m=>m.openLessons('cgel-clauses'))")
  for key, title in zip(['predict','understand','worked','guided','transfer','exit'],part_titles):
   expect(part_heading).to_have_text(title)
   if key=='worked':
    for _ in range(len(companion['worked_example']['steps'])-1):
     view.get_by_role('button',name='Next →',exact=True).click()
   if key in companion:
    view.locator(f'[data-question="{key}"] input[value="{companion[key]["answer"]}"]').check()
   view.get_by_role('button',name='Complete lesson' if key=='exit' else 'Next →',exact=True).click()
  expect(view.locator('.lesson-save-status')).to_contain_text('15 lesson XP awarded')
  page.evaluate("()=>import('/js/lessons-ui.js').then(m=>m.openLessons('br-01'))")
  expect(part_heading).to_have_text(chapter_one_titles[0])
  expect(view.get_by_text('Completed for this content version. Reviewing cannot award another 15 XP.',exact=True)).to_have_count(0)
  expect(view.locator('.constituent-pre-test-status')).to_have_text('Knowledge check complete.')
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
  expect(part_heading).to_have_text('Chapter Post-test')
  transfer=view.locator('[data-question="transfer"]')
  expect(transfer.locator('input:checked')).to_have_value(saved['responses']['transfer'])
  view.get_by_role('button',name='← Previous',exact=True).click()
  expect(part_heading).to_have_text('Chapter Recap')
  view.get_by_role('button',name='Start post-test').click()
  expect(transfer.locator('input:checked')).to_have_value(saved['responses']['transfer'])
  assert not parses,parses
  assert not errors,errors
  browser.close()
  print('PASS: 12 lessons; representative desktop/mobile trees; no parser authority; stage gates, wrong-answer feedback, resume/reload, 180 XP once, planned modules and mode teardown.')
finally:server.shutdown();server.server_close();thread.join(2)
