"""Standalone assessment browser flows; static app plus real shared composer."""
import functools,json,threading,sys
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'server'))
from explanations import explain_request
BANK=json.loads((ROOT/'web/content/quizzes/bank.json').read_text());OUT=Path('/tmp/syntutor-quizzes-browser');OUT.mkdir(exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  if self.path!='/api/explain':self.send_error(404);return
  try:body=explain_request(json.loads(self.rfile.read(int(self.headers.get('Content-Length','0')))));status=200
  except ValueError as e:body={'error':str(e)};status=400
  raw=json.dumps(body).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(raw)
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT/'web')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1440,'height':1050});errors=[];parses=[];evidence=[]
  page.add_init_script("localStorage.setItem('syntutor_onboarding_seen','1')");page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   if r.request.url.startswith('https://esm.sh/'):r.fulfill(status=200,content_type='application/javascript',body='export const createClient = () => null;');return
   if not r.request.url.startswith(base):r.abort();return
   if '/api/parse' in r.request.url:parses.append(r.request.url)
   if '/api/explain' in r.request.url:evidence.append(r.request.post_data_json)
   r.continue_()
  page.route('**/*',route);page.goto(base,wait_until='domcontentloaded');page.locator('.sidebar-item[data-view="quizzes"]').click();view=page.locator('#quizzesView')
  expect(view.get_by_role('heading',name='Test what you can apply.')).to_be_visible();assert view.locator('.curriculum-card').count()==16
  assert not page.evaluate("Object.keys(localStorage).some(k=>k.startsWith('syntutor:lessons:'))")
  card=view.locator('[data-assessment="quiz-br-02"]');card.get_by_role('button',name='Start assessment',exact=True).click();expect(view.locator('[data-quiz-item]')).to_be_visible()
  def answer_questions(score):
   answered=0
   for _ in range(5):
    panel=view.locator('[data-quiz-item]');expect(panel).to_be_visible();ident=panel.get_attribute('data-quiz-item');q=next(q for q in BANK['items'] if q['item_id']==ident)
    if answered<score:
     radio=panel.locator(f'input[value="{q["answer"]}"]');radio.check();expect(view).to_have_attribute('aria-busy','false');expect(radio).to_be_checked()
    assert view.locator('[data-shared-evidence]').count()==0,'feedback must wait for submission'
    answered+=1
    if answered<5:
     old=ident;view.get_by_role('button',name='Next question',exact=True).click();expect(view).to_have_attribute('aria-busy','false');expect(view.locator('[data-quiz-item]')).not_to_have_attribute('data-quiz-item',old)
  answer_questions(3)
  # An unfinished attempt resumes with choices, manifest/order and position intact.
  last=view.locator('[data-quiz-item]').get_attribute('data-quiz-item');page.reload(wait_until='domcontentloaded');page.locator('.sidebar-item[data-view="quizzes"]').click();view.locator('[data-assessment="quiz-br-02"]').get_by_role('button',name='Resume assessment',exact=True).click();expect(view.locator('[data-quiz-item]')).to_have_attribute('data-quiz-item',last)
  view.get_by_role('button',name='Submit assessment · 2 unanswered',exact=True).click();expect(view.locator('.quiz-score')).to_contain_text('3/5');expect(view.locator('.lesson-save-status')).to_contain_text('6 new quiz XP')
  expect(view.locator('[data-shared-evidence]')).to_have_count(5);page.screenshot(path=str(OUT/'review-desktop.png'),full_page=True)
  for expected in [4,0]:
   view.get_by_role('button',name='Try a new attempt',exact=True).click();expect(view.locator('[data-quiz-item]')).to_be_visible();answer_questions(5)
   view.get_by_role('button',name='Submit assessment',exact=True).click();expect(view.locator('.quiz-score')).to_contain_text('5/5');expect(view.locator('.lesson-save-status')).to_contain_text(f'{expected} new quiz XP')
  view.get_by_role('button',name='Practise missed concepts · no XP',exact=True).click();expect(view.get_by_text('Reinforcement · no XP · v1.0.0',exact=True)).to_be_visible();answer_questions(5);view.get_by_role('button',name='Submit assessment',exact=True).click();expect(view.get_by_text('UNSCORED REINFORCEMENT',exact=True)).to_be_visible()
  view.get_by_role('button',name='← All quizzes',exact=True).click();expect(view.locator('.lesson-total')).to_contain_text('10 quiz XP');view.get_by_role('button',name='Chapter',exact=True).click();assert view.locator('.curriculum-card').count()==11
  page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(OUT/'catalog-mobile.png'),full_page=True);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.set_viewport_size({'width':1440,'height':1050});page.evaluate("()=>import('/js/quizzes-ui.js').then(m=>m.openQuizzes('quiz-br-09'))")
  # Capture a genuine tree-selection item via deterministic authored manifest.
  for _ in range(5):
   ident=view.locator('[data-quiz-item]').get_attribute('data-quiz-item');q=next(q for q in BANK['items'] if q['item_id']==ident)
   if q['kind']=='tree_choice':break
   view.get_by_role('button',name='Next question',exact=True).click();expect(view).to_have_attribute('aria-busy','false');expect(view.locator('[data-quiz-item]')).not_to_have_attribute('data-quiz-item',ident)
  assert q['kind']=='tree_choice';assert view.locator('svg[role="img"]').count()==3;page.screenshot(path=str(OUT/'trees-desktop.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(OUT/'trees-mobile.png'),full_page=True);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not page.evaluate("Object.keys(localStorage).some(k=>k.startsWith('syntutor:lessons:'))"),'assessment state must not become lesson completion'
  view.get_by_role('button',name='Back to Syntax Generator',exact=True).click();expect(view).to_be_hidden();assert not parses;assert not errors,errors;assert evidence and all('quiz_item_id' in e for e in evidence)
  browser.close();print('PASS: independent quiz navigation, pre-submit feedback boundary, resume/order, 6→4→0 XP, unscored reinforcement, shared evidence, tree/mobile rendering and lesson-state isolation.')
finally:server.shutdown();server.server_close();thread.join(2)
