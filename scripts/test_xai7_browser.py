"""XAI-7 real Flask+Playwright all-mode parity: lessons, quizzes and trees.

Uses real server-side /api/explain, source gates and canonical tree records.
Auth/third-party requests are isolated, but no explanation endpoint is mocked.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import threading

from playwright.sync_api import sync_playwright, expect
from werkzeug.serving import make_server

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'server'))
from webapp import app
import api

api.classify=lambda text:None
BANK=json.loads((ROOT/'web/content/quizzes/bank.json').read_text())
server=make_server('127.0.0.1',0,app,threaded=True)
thread=threading.Thread(target=server.serve_forever,daemon=True)
thread.start()
base=f'http://127.0.0.1:{server.server_port}'

try:
  with sync_playwright() as playwright:
    browser=playwright.chromium.launch(headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':980})
    page.add_init_script("localStorage.setItem('syntutor_onboarding_seen','1')")
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    def route(r):
      if r.request.url.startswith('https://esm.sh/'):
        r.fulfill(status=200,content_type='application/javascript',
                  body='export const createClient = () => null;')
        return
      if not r.request.url.startswith(base):
        r.abort()
        return
      r.continue_()
    page.route('**/*',route)
    page.goto(base,wait_until='domcontentloaded')
    page.evaluate("async () => { await import('/js/main.js'); }")
    # LESSON — choose an actual B-R node, prove selected/tree parent and
    # navigate to another node without stale highlight.
    page.locator('.sidebar-item[data-view="lessons"]').click()
    page.evaluate("async () => {const m=await import('/js/lessons-ui.js');await m.openLessons('br-04')}")
    lesson=page.locator('#curriculumView')
    tree=lesson.locator('.lesson-evidence-card .lesson-tree-wrap').first
    tree.wait_for(timeout=30000)
    nodes=tree.locator('svg g[data-node-id][role="button"]')
    assert nodes.count()>=3
    nodes.first.press('Enter')
    area=lesson.locator('[data-xai7-lesson]')
    area.locator('[data-shared-evidence]').wait_for(timeout=30000)
    assert area.locator('[data-xai7-navigation]').count()==1
    assert tree.locator('svg g[data-xai7-focus="selected"]').count()==1
    old=tree.locator('svg g[data-xai7-focus="selected"]').get_attribute('data-node-id')
    nodes.last.press('Enter')
    expect(area.locator('[data-xai7-selected]')).to_contain_text(':')
    new=tree.locator('svg g[data-xai7-focus="selected"]').get_attribute('data-node-id')
    assert new!=old,(old,new)
    assert tree.locator('svg g[data-xai7-focus="selected"]').count()==1
    assert area.locator('[data-xai7-verbosity]').count()==1
    # A feature row is independently keyboard selectable, but is never
    # promoted into an inferred syntactic function.
    feature=tree.locator('svg [data-feature-label]').first
    assert feature.count()>=1,'br-04 must expose its recorded B-R V feature'
    feature.press('Enter')
    expect(area.locator('[data-xai7-feature-selected]')).to_contain_text('recorded feature',timeout=30000)
    current=tree.locator('svg').get_attribute('width')
    tree.get_by_role('button',name='Zoom in').click()
    enlarged=tree.locator('svg').get_attribute('width')
    assert float(enlarged)>float(current)
    tree.get_by_role('button',name='Reset zoom').click()
    assert tree.locator('svg').get_attribute('width')==current
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.set_viewport_size({'width':1440,'height':980})

    # QUIZ — grade an actual assessment before the quiz source channel is
    # available. Then select its authentic reviewed answer tree and confirm
    # a *separate* server evidence panel without replacing the quiz feedback.
    page.locator('.sidebar-item[data-view="quizzes"]').click()
    quiz=page.locator('#quizzesView')
    quiz.locator('[data-assessment="quiz-br-02"]').get_by_role(
      'button',name='Start assessment',exact=True).click()
    quiz.locator('[data-quiz-item]').wait_for()
    for n in range(5):
      question=quiz.locator('[data-quiz-item]')
      identifier=question.get_attribute('data-quiz-item')
      row=next(row for row in BANK['items'] if row['item_id']==identifier)
      question.locator('input[value="'+row['answer']+'"]').check()
      expect(quiz).to_have_attribute('aria-busy','false')
      if n<4:
        quiz.get_by_role('button',name='Next question',exact=True).click()
        expect(quiz).to_have_attribute('aria-busy','false')
    quiz.get_by_role('button',name='Submit assessment',exact=True).click()
    quiz.locator('.quiz-score').wait_for(timeout=30000)
    review=quiz.locator('[data-xai7-quiz-tree]').first
    review.wait_for(timeout=30000)
    review.locator('summary').first.click()
    review_tree=review.locator('.lesson-tree-wrap')
    review_tree.locator('svg g[data-node-id][role="button"]').first.press('Enter')
    inspector=review.locator('[data-xai7-quiz-inspector]')
    inspector.locator('[data-shared-evidence]').wait_for(timeout=30000)
    assert inspector.locator('[data-xai7-navigation]').count()==1
    assert review_tree.locator('[data-xai7-focus="selected"]').count()==1
    assert review.locator('xpath=ancestor::article[1]').locator('[data-shared-evidence]').count()>=2
    assert 'Benepar' not in inspector.inner_text()
    page.set_viewport_size({'width':390,'height':844})
    review_tree.get_by_role('button',name='Zoom in').click()
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    assert not errors,errors
    browser.close()
    print('PASS XAI-7: real lesson/quiz API parity, selected/relative tree focus, keyboard features, separate source feedback and mobile zoom.')
finally:
  server.shutdown()
  server.server_close()
  thread.join(2)
