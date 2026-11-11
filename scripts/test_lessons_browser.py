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
  assert cards.nth(1).bounding_box()['y'] >= first.bounding_box()['y'] + first.bounding_box()['height']
  page.screenshot(path=str(OUT/'modules-desktop.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844})
  assert view.evaluate('(el) => el.scrollWidth <= el.clientWidth'), 'Module list has horizontal overflow'
  page.screenshot(path=str(OUT/'modules-mobile.png'),full_page=True)
  page.set_viewport_size({'width':1440,'height':1050})
  for ident in ['br-01','br-06','br-10']:
   page.evaluate("id=>import('/js/lessons-ui.js').then(m=>m.openLessons(id))",ident)
   view.get_by_role('button',name='6. Exit check',exact=True).wait_for()
   assert view.get_by_role('button',name='6. Exit check',exact=True).is_disabled()
   lesson=next(l for l in COURSE['lessons'] if l['lesson_id']==ident)
   prediction=view.locator('[data-question="predict"]')
   prediction.locator('input[value="'+lesson['predict']['answer']+'"]').check()
   expect(prediction.locator('.lesson-feedback.correct')).to_be_visible()
   view.get_by_role('button',name='Continue →',exact=True).click()
   expect(view.locator('.lesson-stepper [aria-current="step"]')).to_have_text('2. Understand')
   view.get_by_role('button',name='Continue →',exact=True).click()
   expect(view.locator('.lesson-stepper [aria-current="step"]')).to_have_text('3. See it')
   assert view.locator('svg[role="img"]').count()==1
   view.locator('.lesson-sources').last.locator('summary').click()
   page.screenshot(path=str(OUT/f'{ident}-desktop.png'),full_page=True)
   page.set_viewport_size({'width':390,'height':844})
   page.screenshot(path=str(OUT/f'{ident}-mobile.png'),full_page=True)
   view.locator('.lesson-evidence-card').scroll_into_view_if_needed()
   page.screenshot(path=str(OUT/f'{ident}-mobile-tree.png'),full_page=True)
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Page-level horizontal overflow'
   page.set_viewport_size({'width':1440,'height':1050})
  # Reload keeps an unfinished stage; identity and version handling are unit/RPC tested.
  page.reload(wait_until='domcontentloaded');page.locator('.sidebar-item[data-view="lessons"]').click()
  view.get_by_role('heading',name='Lesson modules',exact=True).wait_for()
  expect(meter).to_have_attribute('value','2')
  expect(first.get_by_text('2 of 6 stages completed',exact=True)).to_be_visible()
  first.get_by_role('button',name='Resume lesson',exact=True).click()
  assert view.get_by_role('button',name='3. See it',exact=True).get_attribute('aria-current')=='step'
  # Complete every published lesson, in prerequisite order, using rendered controls.
  for lesson in COURSE['lessons']:
   page.evaluate("id=>import('/js/lessons-ui.js').then(m=>m.openLessons(id))",lesson['lesson_id'])
   # Representative previews may already have advanced to the worked stage.
   current=0
   active=view.locator('.lesson-stepper [aria-current="step"]')
   current=int(active.inner_text().split('.')[0])-1
   for i in range(current,6):
    key=['predict','understand','worked','guided','transfer','exit'][i]
    title=['Predict','Understand','See it','Build it','Apply it','Exit check'][i]
    expect(view.locator('.lesson-stepper [aria-current="step"]')).to_have_text(f'{i+1}. {title}')
    print('Checking',lesson['lesson_id'],key,flush=True)
    if key=='worked':
     for _ in range(len(lesson['worked_example']['steps'])-1):view.get_by_role('button',name='Next step',exact=True).click()
    if lesson.get(key):
     question=view.locator(f'[data-question="{key}"]')
     expect(question).to_be_visible()
     if key=='exit':
      wrong=next(o['id'] for o in lesson[key]['options'] if o['id']!=lesson[key]['answer'])
      question.locator(f'input[value="{wrong}"]').check()
      expect(question.locator('.lesson-feedback.retry')).to_contain_text('Try again.')
      expect(view.get_by_role('button',name='Complete lesson · 15 XP once',exact=True)).to_be_disabled()
     question.locator(f'input[value="{lesson[key]["answer"]}"]').check()
     expect(question.locator('.lesson-feedback.correct')).to_be_visible()
    view.get_by_role('button',name='Complete lesson · 15 XP once' if key=='exit' else 'Continue →',exact=True).click()
   expect(view.locator('.lesson-save-status')).to_contain_text('15 lesson XP awarded',timeout=10000)
   if lesson['lesson_id']=='br-11':assert view.locator('svg').count()==0,'Chapter 11 must remain text-only'
  page.evaluate("()=>import('/js/lessons-ui.js').then(m=>m.openLessons('br-01'))")
  view.get_by_role('button',name='Finish review — no extra XP',exact=True).click()
  view.get_by_role('button',name='← All lessons',exact=True).click()
  assert '12 / 12 lessons completed · 180 lesson XP' in view.locator('.lesson-total').inner_text()
  expect(meter).to_have_attribute('value','6')
  expect(first.get_by_role('button',name='Review lesson',exact=True)).to_be_visible()
  expect(first).not_to_contain_text('XP')
  view.get_by_role('button',name='Grammar and Analysis',exact=True).click()
  assert view.locator('.curriculum-card').count()==1
  assert view.get_by_text('17 further topics planned — not published',exact=True).count()==1
  page.reload(wait_until='domcontentloaded');page.locator('.sidebar-item[data-view="lessons"]').click()
  view.locator('.lesson-total').wait_for();assert '180 lesson XP' in view.locator('.lesson-total').inner_text()
  view.get_by_role('button',name='Back to Syntax Generator',exact=True).click();assert view.is_hidden()
  page.goto(base+'/#lesson/NP',wait_until='domcontentloaded')
  view.get_by_role('heading',name='DET and NOM inside NP',exact=True).wait_for()
  view.get_by_role('button',name='Back to Syntax Generator',exact=True).click()
  assert view.is_hidden()
  assert not parses,parses
  assert not errors,errors
  browser.close()
  print('PASS: 12 lessons; representative desktop/mobile trees; no parser authority; stage gates, wrong-answer feedback, resume/reload, 180 XP once, planned modules and mode teardown.')
finally:server.shutdown();server.server_close();thread.join(2)
