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
  part_heading=view.locator('.lesson-stage-body h2')
  part_titles=['Predict','Understand','See it','Build it','Apply it','Exit check']
  chapter_one_titles=['Introduction to Constituents and Hierarchy','Identifying Constituents in a Sentence',
                      'Comparing Flat and Nested Trees', 'Structural Ambiguity',
                      'Chapter Recap','Chapter Post-test']
  for ident in ['br-01','br-06','br-10']:
   titles=chapter_one_titles if ident=='br-01' else part_titles
   page.evaluate("id=>import('/js/lessons-ui.js').then(m=>m.openLessons(id))",ident)
   expect(part_heading).to_have_text(titles[0])
   if ident=='br-01':
    expect(view.locator('.lesson-tree-canvas')).to_have_count(0)
    expect(view.locator('article')).to_have_attribute('aria-labelledby','constituent-page-title')
    intro=view.get_by_role('heading',name='Pre-test',exact=True)
    expect(view.locator('[data-question="predict"] legend')).to_contain_text('Mara rested beside the river')
    expect(intro).to_be_visible()
    assert intro.bounding_box()['y'] < view.locator('[data-question="predict"]').bounding_box()['y']
    page.screenshot(path=str(OUT/'br-01-intro-desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Introduction has horizontal overflow'
    page.screenshot(path=str(OUT/'br-01-intro-mobile.png'),full_page=True)
    page.set_viewport_size({'width':1440,'height':1050})
   expect(view.get_by_text(re.compile(r'^Part \d+ of 6$'))).to_have_count(0)
   next_button=view.locator('.lesson-page-actions').get_by_role('button',name='Next →',exact=True)
   expect(next_button).to_be_disabled()
   columns=view.locator('.lesson-columns, .constituent-page article').bounding_box()
   action=next_button.bounding_box()
   assert action['y'] >= columns['y'] + columns['height']
   assert abs(action['x'] + action['width'] - columns['x'] - columns['width']) < 1
   expect(view.locator('.lesson-sources')).to_have_count(0)
   lesson=next(l for l in COURSE['lessons'] if l['lesson_id']==ident)
   prediction=view.locator('[data-question="predict"]')
   prediction_answer=lesson['predict']['answer']
   if ident=='br-01':
    prediction_answer=next(o['id'] for o in lesson['predict']['options'] if o['id']!=prediction_answer)
   prediction.locator(f'input[value="{prediction_answer}"]').click()
   if ident=='br-01':
    expect(view.locator('.constituent-pre-test-status')).to_have_text('Response recorded.')
    expect(prediction).to_have_count(0)
   else:
    expect(prediction.locator('.lesson-feedback')).to_be_visible()
   expect(next_button).to_be_enabled()
   view.get_by_role('button',name='Next →',exact=True).click()
   expect(part_heading).to_have_text(titles[1])
   if ident=='br-01':
    expect(view.get_by_role('heading',name='Test a group with replacement')).to_be_visible()
    view.get_by_role('button',name='near the quiet garden',exact=True).click()
    expect(view.locator('.lesson-tree-focus text')).to_have_text('PHRASE-a')
    view.get_by_role('button',name='← Previous',exact=True).click()
    expect(view.locator('.constituent-pre-test-status')).to_have_text('Response recorded.')
    expect(prediction).to_have_count(0)
    view.get_by_role('button',name='Next →',exact=True).click()
    expect(part_heading).to_have_text(titles[1])
   view.get_by_role('button',name='Next →',exact=True).click()
   expect(part_heading).to_have_text(titles[2])
   if ident=='br-01':
    expect(view.get_by_role('heading',name='Worked example',exact=True)).to_have_count(0)
    expect(view.get_by_role('button',name='Inspect highlighted tree position')).to_have_count(0)
    expect(view.locator('.constituent-selection mark')).to_have_text(['the','quiet','garden'])
    view.get_by_role('button',name='Flat drawing').click()
    expect(view.locator('.canonical-viewport')).to_be_hidden()
    view.get_by_role('button',name='Nested drawing').click()
    expect(view.locator('.canonical-viewport')).to_be_visible()
   else:
    assert view.locator('svg[role="img"]').count()==1
   canvas=view.locator('.canonical-viewport')
   viewport=canvas.bounding_box()
   drawing=canvas.locator('svg')
   initial_width=drawing.bounding_box()['width']
   canvas.get_by_role('button',name='Zoom in B-R tree').click()
   assert drawing.bounding_box()['width'] > initial_width
   assert canvas.bounding_box()==viewport
   canvas.get_by_role('button',name='Fit B-R tree').click()
   page.screenshot(path=str(OUT/f'{ident}-desktop.png'),full_page=True)
   page.set_viewport_size({'width':390,'height':844})
   page.screenshot(path=str(OUT/f'{ident}-mobile.png'),full_page=True)
   view.locator('.lesson-tree-canvas').scroll_into_view_if_needed()
   assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Lesson has horizontal overflow'
   page.screenshot(path=str(OUT/f'{ident}-mobile-tree.png'),full_page=True)
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Page-level horizontal overflow'
   page.set_viewport_size({'width':1440,'height':1050})
  # Reload keeps an unfinished stage; identity and version handling are unit/RPC tested.
  page.reload(wait_until='domcontentloaded');page.locator('.sidebar-item[data-view="lessons"]').click()
  view.get_by_role('heading',name='Lesson modules',exact=True).wait_for()
  expect(meter).to_have_attribute('value','2')
  expect(first.get_by_text('2 of 6 stages completed',exact=True)).to_be_visible()
  expect(summary.get_by_role('button',name='Constituents and hierarchy',exact=True)).to_be_visible()
  first.get_by_role('button',name='Resume lesson',exact=True).click()
  expect(part_heading).to_have_text(chapter_one_titles[2])
  # Finish the consolidated Chapter 1 teaching flow and test its saved assessment.
  for word in ['the','red','gate']:
   view.get_by_role('checkbox',name=word,exact=True).check()
  view.get_by_role('button',name='Check grouping').click()
  expect(view.get_by_role('status').filter(has_text='Exactly.')).to_be_visible()
  view.get_by_role('button',name='Next →',exact=True).click()
  expect(part_heading).to_have_text(chapter_one_titles[3])
  view.get_by_role('button',name='The hikers had the telescope').click()
  expect(view.locator('.constituent-caption')).to_contain_text('which hikers')
  view.get_by_role('button',name='Next →',exact=True).click()
  expect(part_heading).to_have_text(chapter_one_titles[4])
  expect(view.locator('.constituent-recap li')).to_have_count(4)
  references=view.locator('article .lesson-sources')
  references.locator('summary').click()
  expect(references.get_by_text('AI checked',exact=False)).to_be_visible()
  view.get_by_role('button',name='Start post-test').click()
  expect(part_heading).to_have_text(chapter_one_titles[5])
  expect(view.locator('.lesson-sources')).to_have_count(0)
  chapter_one=COURSE['lessons'][0]
  guided=view.locator('[data-question="guided"]')
  tree_text=view.get_by_text('Read the tree as text',exact=True)
  tree_text.click()
  expect(view.locator('.lesson-tree-text')).not_to_contain_text('PHRASE-b')
  guided.locator('input[value="'+chapter_one['guided']['answer']+'"]').check()
  view.get_by_role('button',name='Next question →',exact=True).click()
  view.get_by_role('button',name='← Previous',exact=True).click()
  expect(part_heading).to_have_text(chapter_one_titles[4])
  view.get_by_role('button',name='Start post-test').click()
  expect(view.locator('[data-question="transfer"]')).to_be_visible()
  page.reload(wait_until='domcontentloaded')
  page.locator('.sidebar-item[data-view="lessons"]').click()
  first.get_by_role('button',name='Resume lesson',exact=True).click()
  expect(view.locator('[data-question="transfer"]')).to_be_visible()
  for key, action in [('transfer','Next question →'),('exit','Complete lesson')]:
   question=view.locator(f'[data-question="{key}"]')
   wrong=next(o['id'] for o in chapter_one[key]['options'] if o['id']!=chapter_one[key]['answer'])
   question.locator(f'input[value="{wrong}"]').check()
   expect(view.get_by_role('button',name=action,exact=True)).to_be_disabled()
   question.locator(f'input[value="{chapter_one[key]["answer"]}"]').check()
   view.get_by_role('button',name=action,exact=True).click()
  expect(view.locator('.lesson-save-status')).to_contain_text('15 lesson XP awarded')
  expect(view.get_by_role('heading',name='Extra practice')).to_be_visible()
  expect(view.get_by_role('button',name='Retake post-test')).to_be_visible()
  view.get_by_role('button',name='Retake post-test').click()
  expect(view.locator('.lesson-question input:checked')).to_have_count(0)
  for key in ['guided','transfer','exit']:
   wrong=next(o['id'] for o in chapter_one[key]['options'] if o['id']!=chapter_one[key]['answer'])
   view.locator(f'[data-question="{key}"] input[value="{wrong}"]').check()
  view.get_by_role('button',name='Finish practice').click()
  for key in ['guided','transfer','exit']:
   original=view.locator(f'[data-question="{key}"] input:checked')
   expect(original).to_have_value(chapter_one[key]['answer'])
   expect(original).to_be_disabled()
  view.get_by_role('button',name='Finish review',exact=True).click()
  assert '1 / 12 lessons completed · 15 lesson XP' in view.locator('.lesson-total').inner_text()
  # Complete every other published lesson in prerequisite order.
  for lesson in COURSE['lessons'][1:]:
   page.evaluate("id=>import('/js/lessons-ui.js').then(m=>m.openLessons(id))",lesson['lesson_id'])
   current=part_titles.index(part_heading.inner_text())
   for i in range(current,6):
    key=['predict','understand','worked','guided','transfer','exit'][i]
    expect(part_heading).to_have_text(part_titles[i])
    print('Checking',lesson['lesson_id'],key,flush=True)
    if key=='worked':
     for _ in range(len(lesson['worked_example']['steps'])-1):
      view.get_by_role('button',name='Next →',exact=True).click()
    if lesson.get(key):
     question=view.locator(f'[data-question="{key}"]')
     expect(question).to_be_visible()
     if key=='exit':
      wrong=next(o['id'] for o in lesson[key]['options'] if o['id']!=lesson[key]['answer'])
      question.locator(f'input[value="{wrong}"]').check()
      expect(question.locator('.lesson-feedback.retry')).to_contain_text('Try again.')
      expect(view.get_by_role('button',name='Complete lesson',exact=True)).to_be_disabled()
      references=view.locator('.lesson-sources')
      expect(references).to_have_count(1)
      assert references.get_attribute('open') is None
      references.locator('summary').click()
      expect(references.locator('li').first).to_be_visible()
     question.locator(f'input[value="{lesson[key]["answer"]}"]').check()
     expect(question.locator('.lesson-feedback.correct')).to_be_visible()
    view.get_by_role('button',name='Complete lesson' if key=='exit' else 'Next →',exact=True).click()
   expect(view.locator('.lesson-save-status')).to_contain_text('15 lesson XP awarded',timeout=10000)
   if lesson['lesson_id']=='br-11':assert view.locator('svg').count()==0,'Chapter 11 must remain text-only'
  page.evaluate("()=>import('/js/lessons-ui.js').then(m=>m.openLessons('br-01'))")
  expect(part_heading).to_have_text(chapter_one_titles[0])
  expect(view.get_by_text('Completed for this content version. Reviewing cannot award another 15 XP.',exact=True)).to_have_count(0)
  expect(view.locator('.constituent-pre-test-status')).to_have_text('Response recorded.')
  expect(view.locator('[data-question="predict"]')).to_have_count(0)
  for _ in range(4):
   view.get_by_role('button',name='Next →',exact=True).click()
  view.get_by_role('button',name='Start post-test',exact=True).click()
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
  assert not parses,parses
  assert not errors,errors
  browser.close()
  print('PASS: 12 lessons; representative desktop/mobile trees; no parser authority; stage gates, wrong-answer feedback, resume/reload, 180 XP once, planned modules and mode teardown.')
finally:server.shutdown();server.server_close();thread.join(2)
