// Optional browser runner. Install Playwright outside the app or set
// QUIZ_V2_PLAYWRIGHT_MODULE to its index.mjs; no runtime dependency is added.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
import {loadActiveCourse,quizCurriculum} from '../web/js/lesson-curriculum.js';
import {makeLessonPractice} from '../web/js/quiz-lesson-practice.js';
import {makeAssessmentItems} from '../web/js/quiz-assessment-items.js';
const {chromium}=await import(process.env.QUIZ_V2_PLAYWRIGHT_MODULE || 'playwright');
const root=path.resolve('web');
const readJson=async p=>JSON.parse(await readFile(path.join(root,p),'utf8'));
const actualCourse=await loadActiveCourse(async p=>({ok:true,json:()=>readJson(p)}));
const actualCurriculum=quizCurriculum(actualCourse);
const fixtureBank=await readJson('/content/quizzes/bank.json');
const fixtureQuestions=[...fixtureBank.items,...makeAssessmentItems(makeLessonPractice(actualCurriculum,await readJson('/content/quizzes/syntax-practice-source.json')))];
const server=createServer(async(req,res)=>{
  try{
    const pathname=new URL(req.url,'http://localhost').pathname;
    const filename=path.resolve(root,'.'+(pathname==='/'?'/index.html':pathname));
    if(!filename.startsWith(root+path.sep))throw Error('Invalid path');
    const content=await readFile(filename);
    const type={'.js':'application/javascript','.json':'application/json','.css':'text/css','.html':'text/html','.svg':'image/svg+xml'}[path.extname(filename)]||'application/octet-stream';
    res.writeHead(200,{'Content-Type':type});res.end(content);
  }catch{res.writeHead(404);res.end('Not found');}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true});
try{
  const page=await browser.newPage({viewport:{width:1360,height:960}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.addInitScript(()=>{
    localStorage.setItem('syntutor_onboarding_seen','1');
    window.Clerk={load:async()=>{},addListener(fn){window.accountChanged=fn;}};
    window.switchQuizAccount=id=>{
      Clerk.user=id?{id,firstName:id}:null;
      Clerk.session=id?{id:'session-'+id,getToken:async()=>id}:null;
      window.accountChanged?.();
    };
    switchQuizAccount(null);
  });
  await page.route('**/*',async route=>{
    const url=route.request().url();
    if(url.startsWith(base+'/js/config.js'))return route.fulfill({contentType:'application/javascript',body:`
      export const CLERK_CONFIG={publishableKey:'pk_test_fixture'};
      export const SUPABASE_CONFIG={url:'https://fixture.test',anonKey:'fixture'};
      export const API_BASE='';`});
    if(url.startsWith('https://esm.sh/'))return route.fulfill({contentType:'application/javascript',body:`
      export const createClient=()=>({
        rpc:(name,args)=>{
          const total=args?.p_attempt?.presented?.length||5;
          const result={data:name==='get_my_progression'?{xp:250,level:2,lesson_xp:250,quiz_xp:0}:name==='save_quiz_v2_attempt'?{attempt_id:args?.p_attempt?.attempt_id,submitted_at:args?.p_submit?'2026-11-16T00:00:00Z':null,correct:args?.p_submit?total:null,earned:args?.p_submit?total*2:0}:[],error:null};
          return {then:(r,j)=>Promise.resolve(result).then(r,j),abortSignal:async()=>result};
        },
        from:()=>({select:()=>({order(){return this},limit(){return this},then:r=>Promise.resolve({data:[],error:null}).then(r)}),
          upsert:async()=>({error:null})})
      });`});
    if(url.startsWith(base))return route.continue();
    return route.abort();
  });
  await page.goto(base);
  const nav=async view=>page.locator(`.sidebar-item[data-view="${view}"]`).click();
  await nav('lessons');
  const lessons=page.locator('#curriculumView');
  await lessons.locator('.lesson-module h2').first().waitFor();
  const syntaxLessons=await lessons.locator('.lesson-module h2').allTextContents();
  await lessons.getByRole('button',{name:'Grammar and Analysis',exact:true}).click();
  const cambridgeLessons=await lessons.locator('.lesson-module h2').allTextContents();
  assert.ok(cambridgeLessons.includes('Preliminaries'),'Preliminaries is an actual implemented lesson, not a book-only chapter');
  await lessons.locator('.lesson-module').filter({has:page.getByRole('heading',{name:'Preliminaries',exact:true})}).getByRole('button',{name:'Start lesson',exact:true}).click();
  await lessons.getByText('Prescriptive and descriptive approaches',{exact:true}).first().waitFor();
  await nav('quizzes');
  const quiz=page.locator('#quizzesView');
  const assertNoResults=async()=>{
    assert.equal(await quiz.locator('.quiz-score,.quiz-review-card,.lesson-feedback,.quiz-tree-inspector').count(),0,'no scores, correctness feedback or explanations before submission');
    assert.equal(await quiz.locator('a[href^="#lesson/"]').count(),0,'no lesson-answer links during an attempt');
    assert.ok(!/Correct answer:|Your answer:/.test(await quiz.innerText()));
  };
  await quiz.getByRole('heading',{name:'Assess your understanding.'}).waitFor();
  assert.equal(await quiz.locator('.quiz-chapter').count(),11);
  assert.deepEqual((await quiz.locator('.quiz-chapter > summary').allTextContents()).map(t=>t.replace(/^Chapter \d+: /,'')),syntaxLessons);
  await quiz.getByRole('button',{name:'Grammar',exact:true}).click();
  assert.equal(await quiz.locator('.quiz-chapter').count(),20);
  assert.deepEqual((await quiz.locator('.quiz-chapter > summary').allTextContents()).map(t=>t.replace(/^Chapter \d+: /,'')),cambridgeLessons);
  await quiz.locator('[data-chapter="cgel-ch01"] > summary').click();
  assert.equal(await quiz.locator('[data-chapter="cgel-ch01"]').getByText('What this course covers').count(),0,'non-assessable Chapter 1 overview remains excluded');
  assert.ok(await quiz.locator('[data-chapter="cgel-ch01"]').getByText('Prescriptive and descriptive approaches').isVisible(),'assessable Chapter 1 topics appear in Quiz');
  assert.equal(await quiz.locator('[data-assessment^="quiz-br-"]').count(),0,'Syntax assessments do not leak into Cambridge');
  const cambridgeMaster=quiz.locator('.quiz-practice').filter({has:page.getByRole('heading',{name:'Cambridge Master Quiz',exact:true})});
  assert.equal(await cambridgeMaster.getByRole('spinbutton').getAttribute('min'),'20');
  assert.equal(await cambridgeMaster.getByRole('spinbutton').getAttribute('max'),'50');
  assert.equal(await cambridgeMaster.getByRole('spinbutton').inputValue(),'25');
  await cambridgeMaster.getByRole('spinbutton').fill('25');
  await cambridgeMaster.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 25',exact:true}).waitFor();
  await assertNoResults();
  const firstMasterId=await quiz.locator('[data-quiz-item]').getAttribute('data-quiz-item');
  const firstMasterQuestion=fixtureQuestions.find(q=>q.item_id===firstMasterId);
  await quiz.locator(`input[value="${firstMasterQuestion.answer}"]`).check();
  await page.waitForFunction(()=>document.querySelector('#quizzesView').getAttribute('aria-busy')==='false');
  await assertNoResults();
  await quiz.getByRole('button',{name:'Next question',exact:true}).click();await assertNoResults();
  await quiz.getByRole('button',{name:'Previous question',exact:true}).click();
  assert.equal(await quiz.locator('input:checked').inputValue(),firstMasterQuestion.answer);await assertNoResults();
  // Question navigator direct jump & flagging (independent of answered state)
  await quiz.locator('.quiz-navigator').getByRole('button',{name:/^Question 4,/}).click();
  await quiz.getByRole('heading',{name:'Question 4 of 25',exact:true}).waitFor();
  await quiz.getByRole('button',{name:'Flag this question for review',exact:true}).click();
  await quiz.locator('.quiz-navigator').getByRole('button',{name:/Question 4,.*unanswered, flagged for review/}).waitFor();
  assert.equal(await quiz.getByRole('button',{name:'Submit',exact:true}).count(),0,'Submit must stay hidden while questions are unanswered (even when flagged)');
  const answerAllAndSubmit=async(count,{correctCount=0,testClear=false}={})=>{
    for(let i=1;i<=count;i++){
      assert.equal(await quiz.getByRole('button',{name:'Submit',exact:true}).count(),0,`Submit hidden before question ${i}/${count} is answered`);
      await quiz.locator('.quiz-navigator').getByRole('button',{name:new RegExp(`^Question ${i},`)}).click();
      await quiz.getByRole('heading',{name:`Question ${i} of ${count}`,exact:true}).waitFor();
      const id=await quiz.locator('[data-quiz-item]').getAttribute('data-quiz-item');
      const q=fixtureQuestions.find(item=>item.item_id===id);
      const choice=i<=correctCount?q.answer:q.options.find(o=>o.id!==q.answer).id;
      await quiz.locator(`input[value="${choice}"]`).check();
      await page.waitForFunction(()=>document.querySelector('#quizzesView').getAttribute('aria-busy')==='false');
    }
    await quiz.getByRole('button',{name:'Submit',exact:true}).waitFor();
    if(testClear){
      const id=await quiz.locator('[data-quiz-item]').getAttribute('data-quiz-item');
      const q=fixtureQuestions.find(item=>item.item_id===id);
      const wrong=q.options.find(o=>o.id!==q.answer).id;
      await quiz.getByRole('button',{name:'Clear choice',exact:true}).click();
      await page.waitForFunction(()=>document.querySelector('#quizzesView').getAttribute('aria-busy')==='false');
      assert.equal(await quiz.getByRole('button',{name:'Submit',exact:true}).count(),0,'Submit hides immediately when an answer is cleared');
      await quiz.locator(`input[value="${wrong}"]`).check();
      await page.waitForFunction(()=>document.querySelector('#quizzesView').getAttribute('aria-busy')==='false');
      await quiz.getByRole('button',{name:'Submit',exact:true}).waitFor();
    }
    await quiz.getByRole('button',{name:'Submit',exact:true}).click();
  };
  // Answer remaining 24 questions on Cambridge Master Quiz and submit
  for(let i=2;i<=25;i++){
    assert.equal(await quiz.getByRole('button',{name:'Submit',exact:true}).count(),0,'Submit hidden while Master Quiz is incomplete');
    await quiz.locator('.quiz-navigator').getByRole('button',{name:new RegExp(`^Question ${i},`)}).click();
    await quiz.getByRole('heading',{name:`Question ${i} of 25`,exact:true}).waitFor();
    const id=await quiz.locator('[data-quiz-item]').getAttribute('data-quiz-item');
    const q=fixtureQuestions.find(item=>item.item_id===id);
    const wrong=q.options.find(o=>o.id!==q.answer).id;
    await quiz.locator(`input[value="${wrong}"]`).check();
    await page.waitForFunction(()=>document.querySelector('#quizzesView').getAttribute('aria-busy')==='false');
  }
  await quiz.getByRole('button',{name:'Submit',exact:true}).click();
  await quiz.locator('.quiz-score').filter({hasText:'1/25 correct (4%)'}).waitFor();
  assert.ok(await quiz.getByText(/Verified account totals appear in the sidebar/).first().isVisible());
  assert.ok(await quiz.getByText(/Correct answer:/).first().isVisible());
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  await quiz.getByRole('button',{name:'Syntax',exact:true}).click();
  const chapter=quiz.locator('[data-chapter="br-03"]');
  await chapter.locator('summary').focus();await page.keyboard.press('Enter');
  assert.equal(await chapter.getAttribute('open'),'');
  const approvedTopic=chapter.locator('.quiz-topic-card').filter({has:page.getByRole('heading',{name:'Nouns, noun phrases and lexical categories',exact:true})});
  assert.ok(await approvedTopic.getByRole('button',{name:'Start quiz',exact:true}).isEnabled());
  assert.equal(await quiz.getByRole('button',{name:'Questions Under Review',exact:true}).count(),0);
  await quiz.getByRole('button',{name:'Grammar',exact:true}).click();
  await quiz.locator('[data-chapter="cgel-ch04"] > summary').click();
  const cambridgeGeneral=quiz.locator('[data-chapter="cgel-ch04"] .quiz-topic-card').filter({has:page.getByRole('heading',{name:'General Quiz',exact:true})});
  await cambridgeGeneral.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 13',exact:true}).waitFor();
  await assertNoResults();
  await answerAllAndSubmit(13);
  await quiz.locator('.quiz-score').filter({hasText:'0/13'}).waitFor();
  assert.ok(await quiz.getByText(/Read the lesson section/).first().isVisible());
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  const cambridgePers=quiz.locator('.quiz-topic-card').filter({has:page.getByRole('heading',{name:'Personalized Cambridge Quiz',exact:true})});
  await cambridgePers.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  await answerAllAndSubmit(5,{testClear:true});
  await quiz.locator('.quiz-score').filter({hasText:'0/5'}).waitFor();
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  await quiz.getByRole('button',{name:'Syntax',exact:true}).click();
  await quiz.locator('[data-chapter="br-02"] > summary').click();
  const nonBlueprint=quiz.locator('[data-chapter="br-02"] .quiz-topic-card').filter({has:page.getByRole('heading',{name:'Subject and predicate tree exercise',exact:true})});
  assert.ok(await nonBlueprint.getByRole('button',{name:'Start quiz',exact:true}).isEnabled());
  await nonBlueprint.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  await assertNoResults();
  await answerAllAndSubmit(5);
  await quiz.locator('.quiz-score').filter({hasText:'0/5'}).waitFor();
  assert.ok(await quiz.getByText(/Read the lesson section/).first().isVisible());
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  const topic=chapter.locator('.quiz-topic-card').filter({has:page.getByRole('heading',{name:'Adjectives, adverbs, APs and AdvPs',exact:true})});
  await topic.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  await quiz.locator('input[type=radio]').first().check();
  await page.waitForFunction(()=>document.querySelector('#quizzesView').getAttribute('aria-busy')==='false');
  // Flag question 2 and verify persistence across reload
  await quiz.locator('.quiz-navigator').getByRole('button',{name:/^Question 2,/}).click();
  await quiz.getByRole('heading',{name:'Question 2 of 5',exact:true}).waitFor();
  await quiz.getByRole('button',{name:'Flag this question for review',exact:true}).click();
  await quiz.locator('.quiz-navigator').getByRole('button',{name:/Question 2,.*unanswered, flagged for review/}).waitFor();
  await assertNoResults();
  const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')));
  const draft=Object.values(saved.attempts).find(t=>!t.submitted_at);
  assert.equal(draft.assessment_id,'quiz-br-03','matching topic uses unchanged published XP blueprint');
  // The shell/assets still load normally; simulate unavailable content services.
  await page.evaluate(()=>{
    const key='syntutor:quiz-v2:public-content:2',cache=JSON.parse(localStorage.getItem(key));
    cache.curriculum.find(t=>t.id==='cambridge').chapters[0].topics.unshift({id:'what-this-course-covers',title:'What this course covers'});
    localStorage.setItem(key,JSON.stringify(cache));
  });
  await page.route('**/content/**',route=>route.abort());
  await page.reload();await nav('quizzes');
  await quiz.getByText(/Offline content: using the last successfully downloaded/).waitFor();
  await page.unroute('**/content/**');
  await quiz.getByRole('button',{name:'Grammar',exact:true}).click();
  assert.equal(await quiz.locator('.quiz-chapter').count(),20);
  await quiz.locator('[data-chapter="cgel-ch01"] > summary').click();
  assert.equal(await quiz.locator('[data-chapter="cgel-ch01"]').getByText('What this course covers').count(),0,'an old offline catalog cannot reintroduce excluded non-assessable topic');
  await quiz.getByRole('button',{name:'Syntax',exact:true}).click();
  await quiz.locator('[data-chapter="br-03"] > summary').click();
  await quiz.locator('[data-chapter="br-03"]').getByRole('button',{name:'Resume quiz',exact:true}).click();
  const restored=await page.evaluate(()=>JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')));
  assert.deepEqual(restored.attempts[draft.attempt_id].presented,draft.presented);
  assert.deepEqual(restored.attempts[draft.attempt_id].flagged,draft.flagged,'flagged questions persist across reload');
  await quiz.locator('.quiz-navigator').getByRole('button',{name:/Question 1,.*answered/}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  assert.ok(await quiz.locator('input[type=radio]:checked').count());
  await quiz.locator('.quiz-navigator').getByRole('button',{name:/Question 2,.*unanswered, flagged for review/}).waitFor();
  await assertNoResults();
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  const master=quiz.locator('.quiz-practice').filter({has:page.getByRole('heading',{name:'Syntax Master Quiz',exact:true})});
  await master.getByRole('spinbutton').fill('15');
  await master.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 15',exact:true}).waitFor();
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  const masterUnfinished=quiz.locator('.quiz-unfinished-row').filter({hasText:'Syntax Master Quiz'}).filter({hasText:'0 of 15 answered'});
  assert.ok(!/#/.test(await masterUnfinished.innerText()),'no visible attempt ID hash in unfinished row');
  await masterUnfinished.getByRole('button',{name:/Resume/}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 15',exact:true}).waitFor();
  assert.equal(await quiz.getByRole('button',{name:'Submit',exact:true}).count(),0,'resumed unfinished Master Quiz hides Submit');
  await answerAllAndSubmit(15);
  await quiz.locator('.quiz-score').filter({hasText:'0/15'}).waitFor();
  assert.ok(await quiz.getByText('QUIZ RESULTS',{exact:true}).isVisible());
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  const personalized=quiz.locator('.quiz-topic-card').filter({has:page.getByRole('heading',{name:'Personalized Syntax Quiz',exact:true})});
  await personalized.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  await assertNoResults();
  const personal=await page.evaluate(()=>Object.values(JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')).attempts).find(t=>t.spec?.mode==='personalized'));
  const missed=await page.evaluate(()=>Object.values(JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')).attempts).find(t=>t.spec?.mode==='master'&&t.spec?.track==='syntax').presented.map(r=>r.item_id));
  assert.ok(personal.presented.every(r=>!missed.includes(r.item_id)));
  assert.equal(personal.assessment_contract,'quiz-v2-formal-1');
  await page.evaluate(()=>switchQuizAccount('quiz-browser-a'));
  await page.waitForFunction(()=>document.querySelector('#sidebarProgressLabel').textContent.includes('250 verified XP'));
  assert.ok(await page.locator('#sidebarProgressRemaining').textContent().then(t=>t.includes('110 to next level')));
  assert.equal(await page.locator('#sidebarProgressBar').getAttribute('value'),'30');
  assert.equal(await page.locator('#sidebarProgress').evaluate(el=>getComputedStyle(el).display),'none','collapsed sidebar hides XP/level section');
  await page.evaluate(()=>document.getElementById('appSidebar').classList.add('expanded'));
  assert.notEqual(await page.locator('#sidebarProgress').evaluate(el=>getComputedStyle(el).display),'none','expanded sidebar shows XP/level section');
  await page.evaluate(()=>switchQuizAccount(null));
  await page.waitForFunction(()=>document.querySelector('#sidebarProgressLabel').textContent.includes('Sign in'));
  assert.equal(await page.locator('#sidebarProgressBar').isHidden(),true,'guest mode hides progress bar');
  await page.evaluate(()=>document.getElementById('appSidebar').classList.remove('expanded'));
  // Both responsive sizes/themes use the actual app styles and native details.
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click().catch(()=>{});
  for(const width of [390,1360])for(const theme of ['dark','light']){
    await page.setViewportSize({width,height:900});
    await page.evaluate(theme=>document.documentElement.setAttribute('data-theme',theme),theme);
    await quiz.getByRole('heading',{name:'Assess your understanding.'}).waitFor();
    await quiz.getByRole('button',{name:'Grammar',exact:true}).click();
    assert.equal(await quiz.locator('.quiz-chapter').count(),20,`${width}px ${theme}: all 20 Grammar chapters rendered`);
    const overflow=await quiz.evaluate(n=>n.scrollWidth>n.clientWidth+2);
    assert.equal(overflow,false,`${width}px ${theme}: no horizontal page overflow`);
  }
  assert.deepEqual(errors,[]);
  console.log('PASS formal quiz browser: Preliminaries assessable topics available cleanly in Grammar Quiz (with orientation excluded even on offline cache and mobile/desktop themes), 20-chapter Master minimum & 25 default / 50 max, no cross-track published cards, no pre-submit feedback/keys, post-submit scores/explanations, topic/Master/personalized modes, offline replay and XP isolation; no page errors.');
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
