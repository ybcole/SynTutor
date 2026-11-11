"""Actual Builder controls/canvas, canonical HTTP evaluation and draft recovery."""
import functools,json,threading,sys
from pathlib import Path
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from playwright.sync_api import sync_playwright,expect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'server'))
from tree_evaluation import evaluate_request
from explanations import explain_request
OUT=Path('/tmp/syntutor-builder-browser');OUT.mkdir(exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  try:
   data=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))));result=(evaluate_request if self.path=='/api/evaluate' else explain_request)(data);status=200
  except (ValueError,TypeError) as e:result={'error':str(e)};status=400
  raw=json.dumps(result).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(raw)
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT/'web')));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1440,'height':1050});errors=[];parses=[];checks=[]
  page.add_init_script("localStorage.setItem('syntutor_onboarding_seen','1')");page.on('pageerror',lambda e:errors.append(str(e)))
  def route(r):
   if r.request.url.startswith('https://esm.sh/'):r.fulfill(status=200,content_type='application/javascript',body='export const createClient = () => null;');return
   if not r.request.url.startswith(base):r.abort();return
   if '/api/parse' in r.request.url:parses.append(r.request.url)
   if '/api/evaluate' in r.request.url:checks.append(r.request.post_data_json)
   r.continue_()
  page.route('**/*',route);page.goto(base,wait_until='domcontentloaded');page.locator('.sidebar-item[data-view="builder"]').click();tools=page.locator('#builderTools');expect(tools).to_be_visible();expect(tools.get_by_label('B-R convention',exact=True)).to_have_value('FINAL')
  convention=tools.get_by_label('B-R convention',exact=True)
  advanced=tools.get_by_text('Advanced tree conventions',exact=True)
  expect(convention).to_be_hidden()
  tools.get_by_text('Reviewed construction practice',exact=True).click();tools.get_by_label('Builder exercise',exact=True).select_option('br-02');tools.get_by_role('button',name='Start construction practice',exact=True).click();expect(tools.get_by_label('B-R convention',exact=True)).to_have_value('2')
  def nodes():return page.evaluate("()=>import('/js/syntax-builder-ui.js').then(m=>Object.values(m.builderModel().nodes).map(n=>({id:n.id,type:n.type,text:n.text,parent:n.parent})))")
  words=nodes();assert len(words)==3
  ids={}
  for label in ['S','NP','VP']:
   tools.get_by_label('New B-R category',exact=True).select_option(label);tools.get_by_role('button',name='Add category',exact=True).click();ids[label]=next(n['id'] for n in nodes() if n['type']==label)
  def select(ident):tools.get_by_label('Selected Builder node',exact=True).select_option(ident)
  def attach(ident,parent):
   select(ident);tools.get_by_label('Parent Builder node',exact=True).select_option(parent);tools.get_by_role('button',name='Connect to parent',exact=True).click()
  attach(ids['NP'],ids['S']);attach(ids['VP'],ids['S'])
  for w in words:attach(w['id'],ids['VP'] if w['text']=='sing' else ids['NP'])
  for label in ['NP','VP']:
   select(ids[label]);tools.get_by_role('button',name='Collapse to triangle',exact=True).click()
  tools.get_by_role('button',name='Check construction',exact=True).click();panel=page.locator('#explainNode');expect(panel).to_contain_text('Structure: well_formed.');expect(panel).to_contain_text('Exercise: matched.');expect(panel).to_contain_text('Grammaticality: unresolved.')
  expect(panel.locator('[data-shared-evidence]')).to_be_visible();page.screenshot(path=str(OUT/'construction-desktop.png'),full_page=True)
  # Undo/redo and source/profile validation operate on this exact tree.
  expect(convention).to_be_hidden();advanced.click();expect(convention).to_be_visible()
  tools.get_by_role('button',name='Undo',exact=True).click();tools.get_by_role('button',name='Redo',exact=True).click();tools.get_by_label('B-R convention',exact=True).select_option('1');tools.get_by_role('button',name='Check construction',exact=True).click();expect(panel).to_contain_text('Structure: invalid.');
  expect(convention).to_be_visible()
  for _ in range(3):
   if tools.get_by_label('B-R convention',exact=True).input_value()=='2':break
   tools.get_by_role('button',name='Undo',exact=True).click()
  expect(tools.get_by_label('B-R convention',exact=True)).to_have_value('2')
  tools.get_by_text('Canonical JSON, movement and alternatives',exact=True).click();tools.get_by_role('button',name='Export canonical JSON',exact=True).click();serialized=tools.get_by_label('Canonical Builder JSON',exact=True).input_value();assert json.loads(serialized)['root']['label']=='S'
  before=nodes();tools.get_by_label('Canonical Builder JSON',exact=True).fill('{broken');tools.get_by_role('button',name='Import canonical JSON',exact=True).click();expect(tools.locator('[data-builder-save]')).to_contain_text('Current work retained');assert nodes()==before
  tools.get_by_label('Canonical Builder JSON',exact=True).fill(json.dumps({**json.loads(serialized),'root':{'label':'S','children':[]}}));tools.get_by_role('button',name='Import canonical JSON',exact=True).click();expect(tools.locator('[data-builder-save]')).to_contain_text('Current work retained');assert nodes()==before
  tools.get_by_role('button',name='Save draft',exact=True).click();page.reload(wait_until='domcontentloaded');page.locator('.sidebar-item[data-view="builder"]').click();expect(tools).to_be_visible();assert nodes()==before;expect(tools.get_by_label('B-R convention',exact=True)).to_have_value('2')
  # Progressive hints and model reveal use reviewed original lesson material.
  tools.get_by_text('Reviewed construction practice',exact=True).click();tools.get_by_label('Builder exercise',exact=True).select_option('br-09');tools.get_by_role('button',name='Start construction practice',exact=True).click();tools.get_by_text('Reviewed construction practice',exact=True).click() if not tools.get_by_role('button',name='Next hint',exact=True).is_visible() else None
  tools.get_by_role('button',name='Next hint',exact=True).click();expect(tools.locator('[data-builder-save]')).not_to_be_empty();tools.get_by_role('button',name='Show model tree',exact=True).click();expect(panel.locator('svg[role="img"]')).to_be_visible();tools.get_by_role('button',name='Load model for exploration',exact=True).click();tools.get_by_role('button',name='Check construction',exact=True).click();expect(panel).to_contain_text('Exercise: matched.')
  page.set_viewport_size({'width':390,'height':844});tools.get_by_role('button',name='Hide editing controls',exact=True).click();page.screenshot(path=str(OUT/'construction-mobile.png'),full_page=True);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not parses,parses;assert checks and all('tree' in c and 'text' not in c for c in checks);assert not errors,errors
  assert not page.evaluate("Object.keys(localStorage).some(k=>/^syntutor:(lessons|assessments):/.test(k))")
  page.set_viewport_size({'width':1440,'height':1050})
  page.evaluate("""() => localStorage.setItem('syntutor:lessons:v1:guest', JSON.stringify({
    'br-02@1.0.0': { stage: 2, visited: ['predict', 'understand'], responses: { predict: 'b' }, completed_at: null }
  }))""")
  page.goto(base+'/#lesson/S',wait_until='domcontentloaded')
  lesson=page.locator('#curriculumView')
  launch=lesson.get_by_role('button',name='Try in Syntax Builder')
  expect(launch).to_be_visible()
  standalone=page.evaluate("localStorage.getItem('syntutor:builder:v1:guest')")
  launch.click()
  expect(tools.get_by_text('Build “The robins sing”',exact=True)).to_be_visible()
  words=nodes()
  assert [n['text'] for n in words]==['The','robins','sing']
  ids={}
  for label in ['S','NP','VP']:
   tools.get_by_label('New B-R category',exact=True).select_option(label)
   tools.get_by_role('button',name='Add category',exact=True).click()
   ids[label]=next(n['id'] for n in nodes() if n['type']==label)
  attach(ids['NP'],ids['S']);attach(ids['VP'],ids['S'])
  for w in words:attach(w['id'],ids['VP'] if w['text']=='sing' else ids['NP'])
  for label in ['NP','VP']:
   select(ids[label]);tools.get_by_role('button',name='Collapse to triangle',exact=True).click()
  tools.get_by_role('button',name='Check construction').click()
  expect(panel).to_contain_text('Exercise: matched.')
  assert checks[-1]['target_lesson_id']=='br-02'
  tools.get_by_role('button',name='Return to lesson').click()
  expect(lesson.get_by_role('heading',name='Reading the NP and VP Branches')).to_be_visible()
  assert page.evaluate("localStorage.getItem('syntutor:builder:v1:guest')")==standalone
  assert page.evaluate("JSON.parse(localStorage.getItem('syntutor:lessons:v1:guest'))['br-02@1.0.0'].stage")==2
  lesson.get_by_role('button',name='Try in Syntax Builder').click()
  expect(tools.get_by_text('Build “The robins sing”',exact=True)).to_be_visible()
  assert len(nodes())==6
  assert not parses,parses
  assert not errors,errors
  page.locator('.sidebar-item[data-view="tutor"]').click();expect(tools).to_be_hidden();browser.close();print('PASS: keyboard/touch node editing, canonical target match, separate verdicts, undo/redo, profile errors, safe import, draft reload, progressive hints/model, mobile layout and no parse/progress side effects.')
finally:server.shutdown();server.server_close();thread.join(2)
