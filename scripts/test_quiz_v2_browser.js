// Optional browser runner. Install Playwright outside the app or set
// QUIZ_V2_PLAYWRIGHT_MODULE to its index.mjs; no runtime dependency is added.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
const {chromium}=await import(process.env.QUIZ_V2_PLAYWRIGHT_MODULE || 'playwright');
const root=path.resolve('web');
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
        rpc:(name)=>{const result={data:name==='get_my_progression'?{xp:250,level:2,lesson_xp:250,quiz_xp:0}:[],error:null};
          return {then:(r,j)=>Promise.resolve(result).then(r,j),abortSignal:async()=>result};},
        from:()=>({select:()=>({order(){return this},limit(){return this},then:r=>Promise.resolve({data:[],error:null}).then(r)}),
          upsert:async()=>({error:null})})
      });`});
    if(url.startsWith(base))return route.continue();
    return route.abort();
  });
  await page.goto(base);
  const nav=async view=>page.locator(`.sidebar-item[data-view="${view}"]`).click();
  await nav('quizzes');
  const quiz=page.locator('#quizzesView');
  await quiz.getByRole('heading',{name:'Practise what you are learning.'}).waitFor();
  assert.equal(await quiz.locator('.quiz-chapter').count(),11);
  await quiz.getByRole('button',{name:'Cambridge — Cambridge Grammar',exact:true}).click();
  assert.equal(await quiz.locator('.quiz-chapter').count(),20);
  assert.ok(await quiz.getByText(/only 10 distinct reviewed questions/).isVisible());
  await quiz.getByRole('button',{name:'Syntax — Burton-Roberts',exact:true}).click();
  const chapter=quiz.locator('[data-chapter="br-03"]');
  await chapter.locator('summary').focus();await page.keyboard.press('Enter');
  assert.equal(await chapter.getAttribute('open'),'');
  const unavailable=chapter.locator('.quiz-topic-card').filter({has:page.getByRole('heading',{name:'Nouns, noun phrases and lexical categories',exact:true})});
  assert.ok(await unavailable.getByRole('button',{name:'Questions Under Review',exact:true}).isDisabled());
  const topic=chapter.locator('.quiz-topic-card').filter({has:page.getByRole('heading',{name:'Adjectives, adverbs, APs and AdvPs',exact:true})});
  await topic.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  await quiz.locator('input[type=radio]').first().check();
  await page.waitForFunction(()=>document.querySelector('#quizzesView').getAttribute('aria-busy')==='false');
  const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')));
  const draft=Object.values(saved.attempts).find(t=>!t.submitted_at);
  assert.equal(draft.assessment_id,'quiz-br-03','matching topic uses unchanged published XP blueprint');
  // The shell/assets still load normally; simulate unavailable content services.
  await page.route('**/content/**',route=>route.abort());
  await page.reload();await nav('quizzes');
  await quiz.getByText(/Offline content: using the last successfully downloaded/).waitFor();
  await page.unroute('**/content/**');
  await quiz.locator('[data-chapter="br-03"] > summary').click();
  await quiz.locator('[data-chapter="br-03"]').getByRole('button',{name:'Resume quiz',exact:true}).click();
  const restored=await page.evaluate(()=>JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')));
  assert.deepEqual(restored.attempts[draft.attempt_id].presented,draft.presented);
  assert.ok(await quiz.locator('input[type=radio]:checked').count());
  await quiz.getByRole('button',{name:'← All quizzes',exact:true}).click();
  const master=quiz.locator('.quiz-practice').filter({has:page.getByRole('heading',{name:'Syntax Master Quiz',exact:true})});
  await master.getByRole('spinbutton').fill('15');
  await master.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 15',exact:true}).waitFor();
  await quiz.getByRole('button',{name:'← All quizzes',exact:true}).click();
  await quiz.getByRole('button',{name:'Resume Syntax Master Quiz · 15 questions · at 1',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 15',exact:true}).waitFor();
  await quiz.getByRole('button',{name:'Submit assessment · 15 unanswered',exact:true}).click();
  await quiz.locator('.quiz-score').filter({hasText:'0/15'}).waitFor();
  assert.ok(await quiz.getByText('UNSCORED PRACTICE · NO XP',{exact:true}).isVisible());
  await quiz.getByRole('button',{name:'← All quizzes',exact:true}).click();
  const personalized=quiz.locator('.quiz-topic-card').filter({has:page.getByRole('heading',{name:'Personalized Syntax Quiz',exact:true})});
  await personalized.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  const personal=await page.evaluate(()=>Object.values(JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')).attempts).find(t=>t.spec?.mode==='personalized'));
  const missed=await page.evaluate(()=>Object.values(JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')).attempts).find(t=>t.spec?.mode==='master').presented.map(r=>r.item_id));
  assert.ok(personal.presented.every(r=>!missed.includes(r.item_id)));
  await page.evaluate(()=>switchQuizAccount('quiz-browser-a'));
  await page.waitForFunction(()=>document.querySelector('#sidebarProgressLabel').textContent.includes('250 verified XP'));
  assert.ok(await page.locator('#sidebarProgressRemaining').textContent().then(t=>t.includes('110 to next level')));
  assert.equal(await page.locator('#sidebarProgressBar').getAttribute('value'),'30');
  await page.evaluate(()=>switchQuizAccount(null));
  await page.waitForFunction(()=>document.querySelector('#sidebarProgressLabel').textContent.includes('Sign in'));
  // Both responsive sizes/themes use the actual app styles and native details.
  await quiz.getByRole('button',{name:'← All quizzes',exact:true}).click().catch(()=>{});
  for(const width of [390,1360])for(const theme of ['dark','light']){
    await page.setViewportSize({width,height:900});
    await page.evaluate(theme=>document.documentElement.setAttribute('data-theme',theme),theme);
    await quiz.getByRole('heading',{name:'Practise what you are learning.'}).waitFor();
    const overflow=await quiz.evaluate(n=>n.scrollWidth>n.clientWidth+2);
    assert.equal(overflow,false,`${width}px ${theme}: no horizontal page overflow`);
  }
  assert.deepEqual(errors,[]);
  console.log('PASS Quiz V2 browser: both tracks, native keyboard expansion, review shortages, published topic XP routing, offline-content draft reload, variable Master count/review, personalized exclusions, account XP/isolation, 390/1360px light/dark layouts; no page errors.');
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
