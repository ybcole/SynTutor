import {gradeQuestion,normalizeResponseText} from '../web/js/quiz-mixed-eval.js';
import {makeV2Attempt,personalizedReviewSummary} from '../web/js/quiz-v2.js';
import {topicDescriptions} from '../web/js/quiz-catalog-copy.js';
// Optional browser runner. Install Playwright outside the app or set
// QUIZ_V2_PLAYWRIGHT_MODULE to its index.mjs; no runtime dependency is added.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import path from 'node:path';
import {loadActiveCourse,quizCurriculum} from '../web/js/lesson-curriculum.js';
import {makeLessonPractice} from '../web/js/quiz-lesson-practice.js';
import {makeAssessmentItems} from '../web/js/quiz-assessment-items.js';
import {syntaxMixedItems} from '../web/js/quiz-mixed-syntax.js';
import {cambridgeMixedItems} from '../web/js/quiz-mixed-cambridge.js';
const {chromium}=await import(process.env.QUIZ_V2_PLAYWRIGHT_MODULE || 'playwright');
const root=path.resolve('web');
const readJson=async p=>JSON.parse(await readFile(path.join(root,p),'utf8'));
const actualCourse=await loadActiveCourse(async p=>({ok:true,json:()=>readJson(p)}));
const actualCurriculum=quizCurriculum(actualCourse);
const fixtureBank=await readJson('/content/quizzes/bank.json');
const fixturePractice=makeLessonPractice(actualCurriculum,await readJson('/content/quizzes/syntax-practice-source.json'));
const fixtureQuestions=[...fixtureBank.items,...fixturePractice,...makeAssessmentItems(fixturePractice,actualCurriculum),...syntaxMixedItems,...cambridgeMixedItems];
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
const browser=await chromium.launch({headless:true,...(process.env.QUIZ_V2_CHROMIUM_PATH?{executablePath:process.env.QUIZ_V2_CHROMIUM_PATH}:{})});
try{
  const page=await browser.newPage({viewport:{width:1360,height:960}});
  page.setDefaultTimeout(15000);
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
  const sidebarViews=await page.locator('.app-sidebar-nav > .sidebar-item').evaluateAll(nodes=>nodes.map(n=>n.dataset.view));
  assert.equal(sidebarViews[sidebarViews.indexOf('tutor')+1],'builder');
  assert.equal(sidebarViews.filter(v=>v==='builder').length,1);
  assert.deepEqual(sidebarViews,['tutor','builder','history','lessons','quizzes','leaderboard','achievements'],'other sidebar destinations retain their relative order');
  for(const view of ['builder','tutor']){
    await nav(view);
    assert.equal(await page.locator(`.sidebar-item[data-view="${view}"].active`).count(),1,'destination keeps its active navigation style');
  }
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
  const snap=async name=>{if(process.env.QUIZ_V2_SCREENSHOT_DIR)await page.screenshot({path:path.join(process.env.QUIZ_V2_SCREENSHOT_DIR,name)});};
  await quiz.getByRole('heading',{name:'Quizzes',exact:true}).waitFor();
  assert.equal(await quiz.locator('.lesson-save-status').count(),0,'no XP footer on quiz selection');
  assert.ok(!(await quiz.innerText()).includes('Scores and explanations unlock after submission.'),'redundant intro text removed');
  assert.equal(await quiz.locator('.quiz-chapter').count(),11);
  assert.equal(await quiz.locator('.quiz-topic-card .quiz-card-count').count(),0,'redundant card question counts removed');
  assert.equal(await quiz.locator('.quiz-chapter-footer > button').count(),11,'every chapter has a direct General Chapter Quiz action');
  assert.equal(await quiz.locator('.quiz-topic-card.is-general').count(),0,'General quiz is accessed through the chapter action');
  assert.deepEqual((await quiz.locator('.quiz-chapter .quiz-chapter-title').allTextContents()).map(t=>t.replace(/^Chapter \d+: /,'')),syntaxLessons);
  const sectionOrder=await quiz.evaluate(()=>['.quiz-special-section.is-review','.quiz-folder-panel','.lesson-track-tabs','.quiz-special-section.is-master','.quiz-chapters-section'].map(s=>document.querySelector(s).getBoundingClientRect().top));
  assert.ok(sectionOrder[0]<sectionOrder[1]&&sectionOrder[1]<=sectionOrder[2]&&sectionOrder[2]<sectionOrder[3]&&sectionOrder[3]<sectionOrder[4],'Review your Errors sits above Syntax/Grammar folder tabs, followed by Master Quizzes and Chapter Quizzes');
  assert.equal(await quiz.locator('.quiz-folder-panel .quiz-special-section.is-review').count(),0,'Review your Errors is isolated outside the track folder and chapter containers');
  const initialSyntaxReview=quiz.locator('.quiz-special-section.is-review');
  assert.equal(await initialSyntaxReview.locator('.quiz-card-title-wrap > span').count(),0,'review heading contains no category or difficulty pill');
  assert.match(await initialSyntaxReview.locator('.quiz-card-desc').innerText(),/^Complete Syntax chapter or subtopic quizzes/);
  assert.equal(await initialSyntaxReview.getByRole('button').isDisabled(),true,'Review your errors is disabled when track has no errors');
  const assertSelectionPresentation=async()=>{
    assert.equal(await quiz.locator('.quiz-difficulty-tag').count(),0,'ordinary cards have no difficulty pills');
    assert.ok((await quiz.locator('.quiz-chapter-footer > button').allTextContents()).every(t=>t==='General Quiz'),'chapter action always reads General Quiz');
    assert.ok(!/In progress|\d+\/\d+ answered/.test(await quiz.innerText()),'selection panels have no draft answer counts');
    assert.ok((await quiz.locator('.quiz-card-status').allTextContents()).every(t=>t.trim()),'no empty status wrappers');
  };
  await assertSelectionPresentation();
  await snap('quiz-selection-desktop.png');
  await quiz.getByRole('button',{name:'Grammar',exact:true}).click();
  assert.equal(await quiz.locator('.quiz-chapter').count(),20);
  assert.deepEqual((await quiz.locator('.quiz-chapter .quiz-chapter-title').allTextContents()).map(t=>t.replace(/^Chapter \d+: /,'')),cambridgeLessons);
  await quiz.locator('[data-chapter="cgel-ch01"] .quiz-subtopics > summary').click();
  assert.equal(await quiz.locator('[data-chapter="cgel-ch01"]').getByText('What this course covers').count(),0,'non-assessable Chapter 1 overview remains excluded');
  assert.ok(await quiz.locator('[data-chapter="cgel-ch01"]').getByText('Prescriptive and descriptive approaches').isVisible(),'assessable Chapter 1 topics appear in Quiz');
  const stackMetrics=await quiz.locator('[data-chapter="cgel-ch01"] .quiz-topic-list .quiz-topic-card').evaluateAll(cards=>cards.map(c=>({
    top:c.getBoundingClientRect().top,
    bottom:c.getBoundingClientRect().bottom,
    desc:(c.querySelector('.quiz-card-desc')?.textContent||'').trim(),
  })));
  assert.ok(stackMetrics.length===10&&stackMetrics.every(m=>m.desc.length>0),'all subtopic quizzes have descriptions');
  for(let i=1;i<stackMetrics.length;i++){
    assert.ok(stackMetrics[i].top>=stackMetrics[i-1].bottom-1,'subtopic quizzes stack vertically one per row');
  }
  await quiz.locator('[data-chapter="cgel-ch01"]').scrollIntoViewIfNeeded();
  const assertChapterFooter=async card=>{
    const geometry=await card.evaluate(n=>{
      const footer=n.querySelector('.quiz-chapter-footer');
      const summary=n.querySelector('.quiz-subtopics > summary').getBoundingClientRect();
      const action=footer.querySelector(':scope > button').getBoundingClientRect();
      const list=n.querySelector('.quiz-topic-list');
      return {box:n.getBoundingClientRect(),footer:footer.getBoundingClientRect(),summary,action,
        open:n.querySelector('details').open,topics:list.getBoundingClientRect(),
        overflow:n.scrollWidth>n.clientWidth+2};
    });
    assert.equal(geometry.overflow,false,'chapter never overflows horizontally');
    assert.ok(Math.abs(geometry.summary.left-geometry.footer.left)<2,'disclosure aligns to footer left');
    const inset=await card.evaluate(n=>parseFloat(getComputedStyle(n).getPropertyValue('--quiz-row-inset')));
    assert.ok(Math.abs(geometry.footer.right-geometry.action.right-inset)<2,'chapter action uses the same right inset as subtopic rows');
    if(page.viewportSize().width>640){
      assert.ok(Math.abs((geometry.summary.top+geometry.summary.bottom)/2-(geometry.action.top+geometry.action.bottom)/2)<12,'desktop/tablet controls share a footer row');
      if(geometry.open)assert.ok(geometry.topics.top>=geometry.action.bottom,'expanded subtopics sit below the chapter action');
    }else{
      assert.ok(geometry.action.top>=geometry.summary.bottom,'mobile actions stack in reading order');
      if(geometry.open)assert.ok(geometry.action.top>=geometry.topics.bottom,'expanded mobile subtopics do not overlap the action');
    }
    if(!geometry.open)assert.ok(geometry.box.bottom-geometry.action.bottom<30,'closed footer is anchored to card bottom');
    assert.equal(await card.locator('.quiz-chapter-footer > button').innerText(),'General Quiz');
    if(geometry.open){
      const rows=await card.locator('.quiz-topic-card').evaluateAll(nodes=>nodes.map(n=>({
        row:n.getBoundingClientRect(),main:n.querySelector('.quiz-row-main').getBoundingClientRect(),
        button:n.querySelector('button').getBoundingClientRect(),
      })));
      for(const item of rows){
        assert.ok(Math.abs(item.button.right-geometry.action.right)<=2,'every subtopic action aligns with General Quiz within 2 CSS pixels');
        assert.ok(Math.abs(item.row.right-geometry.footer.right)<1,'subtopic cards fill the usable chapter width');
        assert.ok(Math.abs(item.button.right-rows[0].button.right)<1,'all subtopic actions share a right edge');
        assert.ok(Math.abs(item.button.width-rows[0].button.width)<1&&Math.abs(item.button.height-rows[0].button.height)<1,'Start/Resume actions have consistent dimensions');
        assert.ok(item.button.right<=item.row.right&&item.main.right<=item.row.right,'row content stays inside its card');
        if(page.viewportSize().width>900){
          assert.ok(item.main.right<item.button.left,'wrapping text never overlaps the action');
          assert.ok(Math.abs((item.main.top+item.main.bottom)/2-(item.button.top+item.button.bottom)/2)<2,'content and action center vertically');
        }else assert.ok(item.button.top>=item.main.bottom,'narrow rows stack text and action');
      }
    }
  };
  await assertChapterFooter(quiz.locator('[data-chapter="cgel-ch01"]'));
  // Check every chapter and every action against General Quiz, including rows
  // with long copy, using real expanded/collapsed geometry in both themes.
  for(const width of [390,768,1360])for(const theme of ['light','dark']){
    await page.setViewportSize({width,height:900});
    await page.evaluate(theme=>document.documentElement.setAttribute('data-theme',theme),theme);
    for(const track of ['Syntax','Grammar']){
      await quiz.getByRole('button',{name:track,exact:true}).click();
      const chapters=await quiz.evaluate(async n=>{
        const cards=[...n.querySelectorAll('.quiz-chapter')];
        const previous=cards.map(c=>c.querySelector('details').open);
        cards.forEach(c=>{c.querySelector('details').open=true;});
        await new Promise(requestAnimationFrame);
        const metrics=cards.map(c=>{
          const general=c.querySelector('.quiz-chapter-footer > button').getBoundingClientRect();
          const footer=c.querySelector('.quiz-chapter-footer').getBoundingClientRect();
          return {chapter:c.dataset.chapter,generalRight:general.right,footerRight:footer.right,
            overflow:c.scrollWidth>c.clientWidth+1,
            rows:[...c.querySelectorAll('.quiz-topic-card')].map(row=>{
              const b=row.querySelector('button').getBoundingClientRect();
              const main=row.querySelector('.quiz-row-main');
              return {right:b.right,width:b.width,height:b.height,cardRight:row.getBoundingClientRect().right,
                overflow:main.scrollWidth>main.clientWidth+1};
            })};
        });
        cards.forEach(c=>{c.querySelector('details').open=false;});
        await new Promise(requestAnimationFrame);
        cards.forEach((c,i)=>{
          const b=c.querySelector('.quiz-chapter-footer > button').getBoundingClientRect();
          metrics[i].collapsedRight=b.right;
          c.querySelector('details').open=previous[i];
        });
        await new Promise(requestAnimationFrame);
        return metrics;
      });
      assert.equal(chapters.length,track==='Syntax'?11:20);
      for(const c of chapters){
        assert.equal(c.overflow,false,`${width}px ${theme} ${c.chapter}: no overflow`);
        assert.ok(Math.abs(c.collapsedRight-c.generalRight)<=1,`${c.chapter}: collapsing preserves action alignment`);
        for(const row of c.rows){
          assert.ok(Math.abs(row.right-c.generalRight)<=2,`${width}px ${theme} ${c.chapter}: subtopic ${row.right} aligns with General Quiz ${c.generalRight}`);
          assert.ok(Math.abs(row.cardRight-c.footerRight)<=1,`${c.chapter}: expanded rows use the full footer width`);
          assert.ok(Math.abs(row.width-128)<=1&&Math.abs(row.height-40)<=1,`${c.chapter}: uniform action dimensions`);
          assert.equal(row.overflow,false,`${c.chapter}: long copy wraps without clipping`);
        }
      }
      if(width===1360&&theme==='light')console.log('PASS alignment coordinates:',JSON.stringify(chapters.map(c=>({chapter:c.chapter,general:c.generalRight,firstThree:c.rows.slice(0,3).map(r=>r.right)}))));
    }
  }
  await page.setViewportSize({width:1360,height:960});
  await quiz.locator('[data-chapter="cgel-ch01"] .quiz-chapter-footer').scrollIntoViewIfNeeded();
  await snap('quiz-chapter-footer-desktop.png');
  await snap('quiz-chapter-stacked.png');
  assert.equal(await quiz.locator('[data-assessment^="quiz-br-"]').count(),0,'Syntax assessments do not leak into Cambridge');
  const cambridgeMaster=quiz.locator('.quiz-practice').filter({has:page.getByRole('heading',{name:'Cambridge Master Quiz',exact:true})});
  assert.equal(await cambridgeMaster.locator('.quiz-diff-btn[aria-pressed="true"]').innerText(),'Medium');
  await cambridgeMaster.getByRole('button',{name:'Hard',exact:true}).click();
  assert.equal(await cambridgeMaster.locator('.quiz-diff-btn[aria-pressed="true"]').innerText(),'Hard');
  await cambridgeMaster.getByRole('button',{name:'Medium',exact:true}).click();
  assert.equal(await cambridgeMaster.getByRole('spinbutton').getAttribute('min'),'20');
  assert.equal(await cambridgeMaster.getByRole('spinbutton').getAttribute('max'),'50');
  assert.equal(await cambridgeMaster.getByRole('spinbutton').inputValue(),'25');
  await cambridgeMaster.getByRole('spinbutton').fill('25');
  await cambridgeMaster.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 25',exact:true}).waitFor();
  await assertNoResults();
  assert.equal(await quiz.locator('.lesson-save-status').count(),0,'no XP footer while taking quiz');
  assert.equal(await quiz.locator('.quiz-flag-btn, .quiz-nav-legend').count(),0,'flagging UI and navigator legend are removed');
  assert.equal(await quiz.locator('.quiz-question .quiz-attempt-controls .quiz-step-btn').count(),2,'Previous/Next sit inside the question panel');
  const qHeaderText=await quiz.locator('header h1').innerText();
  assert.ok(!/Question \d+ of \d+/.test(qHeaderText),'outer page header focuses on quiz title without duplicating question number');
  const backBtnStyle=await quiz.locator('.header-icon-btn').evaluate(n=>{const s=getComputedStyle(n);return {border:s.borderTopWidth,bg:s.backgroundColor};});
  assert.equal(backBtnStyle.border,'0px','back button has no permanent border box');
  assert.equal(backBtnStyle.bg,'rgba(0, 0, 0, 0)','back button has transparent idle background');
  const numBox=await quiz.locator('.quiz-question .quiz-question-number').boundingBox();
  assert.ok(numBox&&numBox.height>0,'Question X of Y indicator renders cleanly inside question panel');
  const assertTrackerLayout=async()=>{
    const m=await quiz.evaluate(n=>{
      const main=n.querySelector('.quiz-question').getBoundingClientRect();
      const side=n.querySelector('.quiz-navigator').getBoundingClientRect();
      const list=n.querySelector('.quiz-nav-list');
      return {main,side,list:{height:list.clientHeight,scrollHeight:list.scrollHeight},
        rows:[...list.querySelectorAll('button')].map(b=>({box:b.getBoundingClientRect(),border:getComputedStyle(b).borderTopWidth,radius:getComputedStyle(b).borderRadius})),
        overflow:n.scrollWidth>n.clientWidth+2};
    });
    assert.equal(m.overflow,false,'attempt has no horizontal overflow');
    assert.equal(await quiz.locator('.quiz-nav-summary').count(),0,'tracker has no answered-count header');
    assert.ok(!/\d+\/\d+ answered/.test(await quiz.locator('.quiz-navigator').innerText()));
    assert.equal(await quiz.locator('.quiz-nav-row[aria-current="step"]').count(),1);
    for(let i=0;i<m.rows.length;i++){
      assert.equal(m.rows[i].border,'0px','question rows have no surrounding border');
      assert.equal(m.rows[i].radius,'0px','question rows have no pill/square rounding');
      if(i)assert.ok(m.rows[i].box.top>=m.rows[i-1].box.bottom,'one question per vertical row');
    }
    if(page.viewportSize().width>900){
      assert.ok(Math.abs(m.main.top-m.side.top)<1&&Math.abs(m.main.bottom-m.side.bottom)<1,'desktop panel top and bottom boundaries match');
      assert.ok(m.side.width<m.main.width,'sidebar remains narrower');
      if(m.rows.length>=20)assert.ok(m.list.scrollHeight>m.list.height,'long question lists scroll within the panel');
    }else assert.ok(m.side.top>=m.main.bottom,'mobile/tablet navigator stacks below assessment');
  };
  for(const width of [390,768,1360])for(const theme of ['light','dark']){
    await page.setViewportSize({width,height:900});
    await page.evaluate(theme=>document.documentElement.setAttribute('data-theme',theme),theme);
    await assertTrackerLayout();
    const last=quiz.locator('.quiz-nav-row').last();
    await last.focus();await page.keyboard.press('Enter');
    await quiz.getByRole('heading',{name:'Question 25 of 25',exact:true}).waitFor();
    assert.equal(await quiz.locator('.quiz-nav-row[aria-current="step"]').evaluate(n=>n===document.activeElement),true,'keyboard navigation retains focus after rendering');
    const visible=await quiz.locator('.quiz-nav-row').last().evaluate(n=>{
      const row=n.getBoundingClientRect(),list=n.closest('ol').getBoundingClientRect();
      return row.top>=list.top&&row.bottom<=list.bottom;
    });
    assert.equal(visible,true,'last question is reachable and visible inside the scrollable list');
    await quiz.locator('.quiz-nav-row').first().focus();await page.keyboard.press('Enter');
    await page.waitForFunction(()=>document.querySelector('.quiz-nav-row[aria-current="step"]')===document.activeElement&&document.activeElement.textContent.startsWith('1Current'));
    await page.keyboard.press('Tab');
    assert.equal(await quiz.locator('.quiz-nav-row').nth(1).evaluate(n=>n===document.activeElement),true,'Tab reaches the next question');
    await page.keyboard.press(' ');
    await quiz.getByRole('heading',{name:'Question 2 of 25',exact:true}).waitFor();
    await last.click();
    await quiz.getByRole('heading',{name:'Question 25 of 25',exact:true}).waitFor();
    await quiz.getByRole('button',{name:'Previous question',exact:true}).click();
    await quiz.getByRole('heading',{name:'Question 24 of 25',exact:true}).waitFor();
    assert.equal(await quiz.locator('.quiz-nav-row[aria-current="step"]').evaluate(n=>{
      const row=n.getBoundingClientRect(),list=n.closest('ol').getBoundingClientRect();
      return row.top>=list.top&&row.bottom<=list.bottom;
    }),true,'Previous/Next keeps the active question visible in a long list');
    await quiz.locator('.quiz-nav-row').first().click();
    await quiz.getByRole('heading',{name:'Question 1 of 25',exact:true}).waitFor();
    await quiz.evaluate(n=>{n.scrollTop=0;});
    await snap(`quiz-tracker-${width}-${theme}.png`);
  }
  await page.setViewportSize({width:1360,height:960});
  const answerCurrentQuestion=async(wantCorrect=false,recordKinds=null)=>{
    const id=await quiz.locator('[data-quiz-item]').getAttribute('data-quiz-item');
    const kind=await quiz.locator('[data-quiz-item]').getAttribute('data-quiz-kind');
    if(recordKinds)recordKinds.add(kind);
    const q=fixtureQuestions.find(item=>item.item_id===id);
    if(kind==='fill_blank'){
      await quiz.locator('.quiz-text-input').fill(wantCorrect?q.accepted_answers[0]:'wrongblank');
      await quiz.locator('.quiz-text-input').blur();
    }else if(kind==='grammar_correction'){
      await quiz.locator('.quiz-textarea').fill(wantCorrect?q.accepted_answers[0]:q.stimulus.sentence);
      await quiz.locator('.quiz-textarea').blur();
    }else if(kind==='sentence_reconstruction'){
      while(await quiz.locator('.quiz-recon-remove').count())await quiz.locator('.quiz-recon-remove').first().click();
      let rest=normalizeResponseText(q.accepted_answers[0]),remaining=q.tokens.map((t,i)=>({t:normalizeResponseText(t),i}));
      const correct=[];
      while(rest){
        const token=remaining.find(x=>rest===x.t||rest.startsWith(x.t+' '));
        assert.ok(token,`reconstruction accepted answer must be buildable: ${id}`);
        correct.push(token.i);rest=rest.slice(token.t.length).trim();remaining=remaining.filter(x=>x!==token);
      }
      let order=correct;
      if(!wantCorrect){
        order=null;
        for(let i=0;i<correct.length&&!order;i++)for(let j=i+1;j<correct.length&&!order;j++){
          const candidate=[...correct];[candidate[i],candidate[j]]=[candidate[j],candidate[i]];
          if(!gradeQuestion(q,candidate).correct)order=candidate;
        }
        assert.ok(order,'fixture must have a complete incorrect ordering');
      }
      for(const idx of order)await quiz.locator(`.quiz-recon-avail[data-token-idx="${idx}"]`).click();
    }else if(kind==='tree_builder'||kind==='syntax_correction'){
      await quiz.locator('.quiz-builder-workspace .first-tree-stage canvas').waitFor();
      assert.equal(await quiz.locator('.first-tree-guide, [data-builder-construct]').count(),0,'no hint or reveal controls during formal syntax-tree quiz');
      await quiz.locator('.first-tree-palette-list button').first().click();
    }else{
      const choice=wantCorrect?q.answer:q.options.find(o=>o.id!==q.answer).id;
      await quiz.locator(`input[value="${choice}"]`).check();
    }
    await page.waitForFunction(()=>document.querySelector('#quizzesView').getAttribute('aria-busy')==='false');
    if(kind==='sentence_reconstruction')await page.waitForFunction(id=>{
      const saved=Object.keys(localStorage).filter(k=>k.startsWith('syntutor:assessments:v1:')).flatMap(k=>Object.values(JSON.parse(localStorage.getItem(k)).attempts)).find(t=>!t.submitted_at&&t.responses[id])?.responses[id];
      return saved?.length===document.querySelectorAll('.quiz-recon-chip').length;
    },id);
    return {id,kind,q};
  };
  const camMasterKinds=new Set();
  await answerCurrentQuestion(true,camMasterKinds);
  assert.match(await quiz.locator('.quiz-nav-row').first().getAttribute('aria-label'),/current, answered$/);
  assert.equal(await quiz.locator('.quiz-nav-row .quiz-nav-state').first().innerText(),'Current · Answered');
  assert.equal(await quiz.locator('.quiz-nav-row .quiz-nav-state').nth(1).innerText(),'Unanswered');
  const initialResponses=await page.evaluate(()=>Object.values(JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')).attempts).find(t=>!t.submitted_at).responses);
  await assertNoResults();
  await quiz.getByRole('button',{name:'Next question',exact:true}).click();await assertNoResults();
  await quiz.getByRole('button',{name:'Previous question',exact:true}).click();
  await quiz.locator('.quiz-navigator').getByRole('button',{name:/^Question 1,.*answered/}).waitFor();
  assert.deepEqual(await page.evaluate(()=>Object.values(JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')).attempts).find(t=>!t.submitted_at).responses),initialResponses,'question navigation preserves responses');
  await assertNoResults();
  // Question navigator direct jump
  await quiz.locator('.quiz-navigator').getByRole('button',{name:/^Question 4,/}).click();
  await quiz.getByRole('heading',{name:'Question 4 of 25',exact:true}).waitFor();
  assert.equal(await quiz.getByRole('button',{name:'Submit',exact:true}).count(),0,'Submit must stay hidden while questions are unanswered');
  const answerAllAndSubmit=async(count,{correctCount=0,testClear=false,recordKinds=null}={})=>{
    for(let i=1;i<=count;i++){
      assert.equal(await quiz.getByRole('button',{name:'Submit',exact:true}).count(),0,`Submit hidden before question ${i}/${count} is answered`);
      await quiz.locator('.quiz-navigator').getByRole('button',{name:new RegExp(`^Question ${i},`)}).click();
      await quiz.getByRole('heading',{name:`Question ${i} of ${count}`,exact:true}).waitFor();
      await answerCurrentQuestion(i<=correctCount,recordKinds);
      await quiz.locator('.quiz-navigator').getByRole('button',{name:new RegExp(`^Question ${i},.*answered`)}).waitFor();
    }
    await quiz.getByRole('button',{name:'Submit',exact:true}).waitFor();
    if(testClear){
      const clearBtn=quiz.getByRole('button',{name:/^Clear (answer|choice)$/});
      await clearBtn.click();
      await page.waitForFunction(()=>document.querySelector('#quizzesView').getAttribute('aria-busy')==='false');
      assert.equal(await quiz.getByRole('button',{name:'Submit',exact:true}).count(),0,'Submit hides immediately when an answer is cleared');
      await answerCurrentQuestion(false);
      await quiz.getByRole('button',{name:'Submit',exact:true}).waitFor();
    }
    await quiz.getByRole('button',{name:'Submit',exact:true}).click();
  };
  // Answer remaining 24 questions on Cambridge Master Quiz and submit
  for(let i=2;i<=25;i++){
    assert.equal(await quiz.getByRole('button',{name:'Submit',exact:true}).count(),0,'Submit hidden while Master Quiz is incomplete');
    await quiz.locator('.quiz-navigator').getByRole('button',{name:new RegExp(`^Question ${i},`)}).click();
    await quiz.getByRole('heading',{name:`Question ${i} of 25`,exact:true}).waitFor();
    await answerCurrentQuestion(false,camMasterKinds);
  }
  assert.ok(camMasterKinds.has('fill_blank')&&camMasterKinds.has('grammar_correction')&&camMasterKinds.has('sentence_reconstruction'),'Cambridge Master Quiz renders all 3 mandatory Grammar non-MCQ formats');
  await quiz.getByRole('button',{name:'Submit',exact:true}).click();
  await quiz.locator('.quiz-score').filter({hasText:'1/25 correct (4%)'}).waitFor();
  assert.equal(await quiz.locator('.lesson-save-status').count(),0,'no XP footer on quiz results');
  assert.equal(await quiz.getByText('QUIZ RESULTS',{exact:true}).count(),0,'redundant eyebrow removed');
  assert.equal(await quiz.getByText(/Verified account totals appear in the sidebar/).count(),0,'redundant sidebar note removed');
  assert.ok(await quiz.locator('.quiz-results-summary').innerText().then(t=>t.includes('Interactive mixed-format')));
  const summaryStyle=await quiz.locator('.quiz-results-summary').evaluate(n=>{
    const s=getComputedStyle(n);
    const sc=n.querySelector('.quiz-score')?.getBoundingClientRect();
    const st=n.querySelector('.quiz-results-stats')?.getBoundingClientRect();
    return {border:s.borderTopWidth,bg:s.backgroundColor,shadow:s.boxShadow,scoreLeft:sc?.left,statsLeft:st?.left};
  });
  assert.equal(summaryStyle.border,'0px','Results summary has no border container');
  assert.equal(summaryStyle.bg,'rgba(0, 0, 0, 0)','Results summary has transparent background');
  assert.equal(summaryStyle.shadow,'none','Results summary has no card shadow');
  assert.ok(summaryStyle.scoreLeft<summaryStyle.statsLeft,'Score sits left and stats sit right on the same row');
  const reviewWidths=await quiz.evaluate(()=>{
    const body=document.querySelector('.quiz-review-body'),shell=document.querySelector('.quiz-review-shell');
    const bs=getComputedStyle(body),avail=body.clientWidth-parseFloat(bs.paddingLeft)-parseFloat(bs.paddingRight);
    return {avail,shell:shell.getBoundingClientRect().width};
  });
  assert.ok(reviewWidths.shell>=reviewWidths.avail-2,`Results shell fills full workspace width (${reviewWidths.shell} >= ${reviewWidths.avail - 2})`);
  const firstReviewText=await quiz.locator('[data-review-item]').first().innerText();
  assert.ok(/Your (answer|correction):/.test(firstReviewText)&&!/Accepted (answer|correction):/.test(firstReviewText)&&!firstReviewText.includes('Needs review'),'correct answer shows answer once without repeating accepted answer');
  const secondReviewText=await quiz.locator('[data-review-item]').nth(1).innerText();
  assert.ok(/Your (answer|correction):/.test(secondReviewText)&&/Accepted (answer|correction):|Correct answer:/.test(secondReviewText)&&!secondReviewText.includes('Needs review'),'incorrect item shows submitted and accepted answers cleanly without repetitive Needs review text');
  assert.ok(await quiz.locator('.quiz-next').innerText().then(t=>t.includes('Review lessons')),'multi-lesson Master Quiz shows consolidated Review lessons bar');
  await snap('quiz-results-desktop.png');
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  await quiz.getByRole('button',{name:'Syntax',exact:true}).click();
  const chapter=quiz.locator('[data-chapter="br-03"]');
  await chapter.locator('summary').focus();await page.keyboard.press('Enter');
  assert.equal(await chapter.locator('.quiz-subtopics').getAttribute('open'),'');
  const approvedTopic=chapter.locator('.quiz-topic-card').filter({has:page.getByRole('heading',{name:/^Quiz \d+: Nouns, noun phrases and lexical categories$/})});
  assert.ok(await approvedTopic.getByRole('button',{name:'Start quiz',exact:true}).isEnabled());
  assert.equal(await quiz.getByRole('button',{name:'Questions Under Review',exact:true}).count(),0);
  await quiz.getByRole('button',{name:'Grammar',exact:true}).click();
  await quiz.locator('[data-chapter="cgel-ch04"] .quiz-subtopics > summary').click();
  await quiz.locator('[data-chapter="cgel-ch04"] .quiz-chapter-footer').getByRole('button',{name:/General Quiz:.*Start General Chapter Quiz/}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 13',exact:true}).waitFor();
  await assertNoResults();
  const camKinds=new Set();
  await answerAllAndSubmit(13,{recordKinds:camKinds});
  assert.ok(camKinds.has('fill_blank')&&camKinds.has('grammar_correction')&&camKinds.has('sentence_reconstruction'),'Grammar General Quiz renders all 3 mandatory non-MCQ formats in a single attempt');
  await quiz.locator('.quiz-score').filter({hasText:'0/13'}).waitFor();
  assert.ok(await quiz.locator('.quiz-results-stats').innerText().then(t=>t.includes('0 verified XP')));
  assert.ok(await quiz.locator('.quiz-next').innerText().then(t=>t.includes('Review:')),'single-chapter General quiz shows consolidated Review: chapter');
  assert.ok(await quiz.locator('.quiz-lesson-link').count()>=1,'multi-topic General quiz retains distinct per-subtopic lesson links');
  assert.equal(await quiz.locator('.quiz-lesson-link').count(),new Set(await quiz.locator('.quiz-lesson-link').evaluateAll(els=>els.map(a=>a.getAttribute('href')))).size,'per-card subtopic links are never duplicated');
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  await quiz.getByRole('button',{name:'Syntax',exact:true}).click();
  const synCh3=quiz.locator('[data-chapter="br-03"]');
  if((await synCh3.locator('.quiz-subtopics').getAttribute('open'))===null)await synCh3.locator('.quiz-subtopics > summary').click();
  await synCh3.locator('.quiz-chapter-footer').getByRole('button',{name:/General Quiz:.*Start General Chapter Quiz/}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  const synKinds=new Set();
  for(let qIdx=1;qIdx<=5;qIdx++){
    await quiz.locator('.quiz-navigator').getByRole('button',{name:new RegExp(`^Question ${qIdx},`)}).click();
    await assertTrackerLayout();
    await quiz.getByRole('heading',{name:`Question ${qIdx} of 5`,exact:true}).waitFor();
    const k=await quiz.locator('[data-quiz-item]').getAttribute('data-quiz-kind');
    synKinds.add(k);
    if(k==='fill_blank')await snap('quiz-mixed-fill-blank.png');
    if(k==='sentence_reconstruction')await snap('quiz-mixed-reconstruction.png');
    if(k==='tree_builder'||k==='syntax_correction'){
     await page.waitForFunction(()=>{
      const c=document.querySelector('.quiz-builder-workspace .first-tree-stage #builderCanvas');
      if(!c||c.width<=0||c.height<=0)return false;
      const d=c.getContext('2d')?.getImageData(0,0,c.width,c.height).data;
      if(!d)return false;
      for(let i=3;i<d.length;i+=4)if(d[i]>0)return true;
      return false;
     });
     await snap('quiz-mixed-tree-builder.png');
    }
  }
  assert.ok(synKinds.has('fill_blank')&&synKinds.has('syntax_correction')&&synKinds.has('sentence_reconstruction')&&synKinds.has('tree_builder'),'Syntax General Quiz renders all 4 mandatory non-MCQ formats including embedded Syntax Builder within a single attempt');
  await answerAllAndSubmit(5,{correctCount:1});
  await quiz.locator('.quiz-review-card').first().waitFor();
  assert.ok((await quiz.locator('.quiz-review-trees svg').count())>=2,'Tree builder & syntax correction results render learner and expected trees');
  await snap('quiz-mixed-results.png');
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  await quiz.getByRole('button',{name:'Grammar',exact:true}).click();
  const cambridgePers=quiz.locator('.quiz-topic-card.is-review').filter({has:page.getByRole('heading',{name:'Review your Errors',exact:true})});
  const submittedHistory=await page.evaluate(()=>JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')).attempts);
  assert.equal(await cambridgePers.locator('.quiz-card-desc').innerText(),personalizedReviewSummary({...fixtureBank,mixed_items:[...syntaxMixedItems,...cambridgeMixedItems],practice_items:fixturePractice,assessment_items:makeAssessmentItems(fixturePractice,actualCurriculum)},actualCurriculum,submittedHistory,'cambridge'),'guidance matches actual submitted incorrect answers');
  await cambridgePers.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  const camPersKinds=new Set();
  await answerAllAndSubmit(5,{testClear:true,recordKinds:camPersKinds});
  assert.ok(camPersKinds.size>=2&&['fill_blank','grammar_correction','sentence_reconstruction'].some(k=>camPersKinds.has(k)),'Cambridge Review your Errors uses multiple non-MCQ formats');
  await quiz.locator('.quiz-score').filter({hasText:'0/5'}).waitFor();
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  await quiz.getByRole('button',{name:'Syntax',exact:true}).click();
  await quiz.locator('[data-chapter="br-02"] .quiz-subtopics > summary').click();
  const nonBlueprint=quiz.locator('[data-chapter="br-02"] .quiz-topic-card').filter({has:page.getByRole('heading',{name:/^Quiz \d+: Subject and predicate tree exercise$/})});
  assert.ok(await nonBlueprint.getByRole('button',{name:'Start quiz',exact:true}).isEnabled());
  await nonBlueprint.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  await assertNoResults();
  await answerAllAndSubmit(5);
  await quiz.locator('.quiz-score').filter({hasText:'0/5'}).waitFor();
  assert.ok(await quiz.locator('.quiz-next').innerText().then(t=>t.includes('Review:')&&t.includes('Open lesson')),'single-lesson tree quiz consolidates recommendation into one Open lesson control');
  assert.equal(await quiz.locator('.quiz-lesson-link').count(),0,'consolidated single-lesson quiz does not repeat Read the lesson section under every card');
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  await quiz.getByRole('button',{name:'Grammar',exact:true}).click();
  if((await quiz.locator('[data-chapter="cgel-ch01"] .quiz-subtopics').getAttribute('open'))===null){
   await quiz.locator('[data-chapter="cgel-ch01"] .quiz-subtopics > summary').click();
  }
  await quiz.locator('[data-chapter="cgel-ch01"] .quiz-topic-card').filter({has:page.getByRole('heading',{name:/^Quiz \d+: Prescriptive and descriptive approaches$/})}).getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  const stdHeights=[],navYs=[];
  for(let step=0;step<5;step++){
   await quiz.getByRole('heading',{name:`Question ${step+1} of 5`,exact:true}).waitFor();
   await page.waitForFunction(()=>document.querySelector('#quizzesView')?.getAttribute('aria-busy')==='false');
   stdHeights.push((await quiz.locator('.quiz-question').boundingBox()).height);
   navYs.push((await quiz.locator('.quiz-attempt-controls .quiz-step-btn').first().boundingBox()).y);
   if(step===0)await snap('quiz-attempt-standard.png');
   if(step<4)await quiz.getByRole('button',{name:'Next question',exact:true}).click();
  }
  const minH=Math.min(...stdHeights),maxH=Math.max(...stdHeights);
  assert.ok(minH>=440,`question panel maintains consistent minimum height (${minH}px)`);
  assert.ok(maxH-minH<=1,`standard question panel keeps identical outer height across all 5 questions (${stdHeights.join(', ')})`);
  assert.ok(Math.max(...navYs)-Math.min(...navYs)<=1,`bottom Previous/Next arrows stay at fixed Y position (${navYs.join(', ')})`);
  const camTopKinds=new Set();
  await answerAllAndSubmit(5,{correctCount:2,recordKinds:camTopKinds});
  assert.ok(camTopKinds.size>=2&&['fill_blank','grammar_correction','sentence_reconstruction'].some(k=>camTopKinds.has(k)),'Grammar subtopic quiz uses multiple non-MCQ formats');
  await quiz.locator('.quiz-score').filter({hasText:'2/5 correct (40%)'}).waitFor();
  assert.ok(await quiz.locator('.quiz-next').innerText().then(t=>t.includes('Review: Preliminaries')&&t.includes('Open lesson')));
  assert.equal(await quiz.locator('.quiz-lesson-link').count(),0,'single-topic Cambridge quiz avoids repeating identical Read the lesson section links');
  assert.equal(await quiz.locator('.quiz-revisit-row button').innerText(),'Open lesson');
  await snap('quiz-results-compact.png');

  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  await quiz.getByRole('button',{name:'Syntax',exact:true}).click();
  const topic=chapter.locator('.quiz-topic-card').filter({has:page.getByRole('heading',{name:/^Quiz \d+: Adjectives, adverbs, APs and AdvPs$/})});
  await topic.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  const synTopicKinds=new Set();
  for(let step=0;step<5;step++){
   await quiz.getByRole('heading',{name:`Question ${step+1} of 5`,exact:true}).waitFor();
   await page.waitForFunction(()=>document.querySelector('#quizzesView')?.getAttribute('aria-busy')==='false');
   synTopicKinds.add(await quiz.locator('[data-quiz-item]').getAttribute('data-quiz-kind'));
   if(step<4)await quiz.getByRole('button',{name:'Next question',exact:true}).click();
  }
  assert.ok(synTopicKinds.size>=2&&['fill_blank','syntax_correction','sentence_reconstruction','tree_builder'].some(k=>synTopicKinds.has(k)),'Syntax subtopic quiz uses genuine mixed formats');
  await quiz.locator('.quiz-navigator').getByRole('button',{name:/^Question 1,/}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  await answerCurrentQuestion(true);
  await assertNoResults();
  // Builder changes use the same debounced auto-save as text inputs. Capture
  // the expected draft only after that response has actually reached storage.
  await page.waitForFunction(itemId=>Object.values(JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')).attempts)
    .some(t=>!t.submitted_at&&Object.hasOwn(t.responses||{},itemId)),await quiz.locator('[data-quiz-item]').getAttribute('data-quiz-item'));
  const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')));
  const draft=Object.values(saved.attempts).find(t=>!t.submitted_at);
  assert.equal(draft.spec?.format,'mixed','subtopic draft uses unified mixed-format engine');
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
  await quiz.locator('[data-chapter="cgel-ch01"] .quiz-subtopics > summary').click();
  assert.equal(await quiz.locator('[data-chapter="cgel-ch01"]').getByText('What this course covers').count(),0,'an old offline catalog cannot reintroduce excluded non-assessable topic');
  await quiz.getByRole('button',{name:'Syntax',exact:true}).click();
  await quiz.locator('[data-chapter="br-03"] .quiz-subtopics > summary').click();
  await quiz.locator('[data-chapter="br-03"] .quiz-topic-list').getByRole('button',{name:'Resume quiz',exact:true}).click();
  const restored=await page.evaluate(()=>JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')));
  assert.deepEqual(restored.attempts[draft.attempt_id].presented,draft.presented);
  assert.deepEqual(restored.attempts[draft.attempt_id].responses,draft.responses,'offline draft restoration keeps all responses');
  await quiz.locator('.quiz-navigator').getByRole('button',{name:/Question 1,.*answered/}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  await assertNoResults();
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  const master=quiz.locator('.quiz-practice').filter({has:page.getByRole('heading',{name:'Syntax Master Quiz',exact:true})});
  await master.getByRole('spinbutton').fill('15');
  await master.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 15',exact:true}).waitFor();
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  assert.equal(await quiz.locator('.quiz-unfinished-details').count(),0,'unfinished section is removed');
  await master.getByRole('button',{name:'Resume quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 15',exact:true}).waitFor();
  assert.equal(await quiz.getByRole('button',{name:'Submit',exact:true}).count(),0,'resumed unfinished Master Quiz hides Submit');
  const synMasterKinds=new Set();
  await answerAllAndSubmit(15,{recordKinds:synMasterKinds});
  assert.ok(synMasterKinds.has('fill_blank')&&synMasterKinds.has('syntax_correction')&&synMasterKinds.has('sentence_reconstruction')&&synMasterKinds.has('tree_builder'),'Syntax Master Quiz renders all 4 mandatory non-MCQ formats');
  await quiz.locator('.quiz-score').filter({hasText:'0/15'}).waitFor();
  assert.ok(await quiz.locator('.quiz-next').innerText().then(t=>t.includes('Review lessons')));
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  const personalized=quiz.locator('.quiz-topic-card.is-review').filter({has:page.getByRole('heading',{name:'Review your Errors',exact:true})});
  await personalized.getByRole('button',{name:'Start quiz',exact:true}).click();
  await quiz.getByRole('heading',{name:'Question 1 of 5',exact:true}).waitFor();
  const persKinds=new Set();
  for(let qIdx=1;qIdx<=5;qIdx++){
    await quiz.locator('.quiz-navigator').getByRole('button',{name:new RegExp(`^Question ${qIdx},`)}).click();
    persKinds.add(await quiz.locator('[data-quiz-item]').getAttribute('data-quiz-kind'));
  }
  assert.ok(persKinds.size>=2&&['fill_blank','syntax_correction','sentence_reconstruction','tree_builder'].some(k=>persKinds.has(k)),'Review your Errors uses multiple non-MCQ formats');
  await assertNoResults();
  const personal=await page.evaluate(()=>Object.values(JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')).attempts).find(t=>t.spec?.mode==='personalized'));
  const missed=await page.evaluate(()=>Object.values(JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')).attempts).find(t=>t.spec?.mode==='master'&&t.spec?.track==='syntax').presented.map(r=>r.item_id));
  assert.ok(personal.presented.every(r=>!missed.includes(r.item_id)));
  assert.equal(personal.spec?.format,'mixed');
  await page.evaluate(()=>switchQuizAccount('quiz-browser-a'));
  await page.waitForFunction(()=>document.querySelector('#sidebarProgressLabel').textContent.includes('250/360 XP'));
  assert.equal(await page.locator('#sidebarProgressLabel').innerText(),'250/360 XP');
  assert.equal(await page.locator('#sidebarProgressBar').getAttribute('max'),'140');
  assert.equal(await page.locator('#sidebarProgressBar').getAttribute('value'),'30');
  assert.match(await page.locator('#sidebarProgressLabel').getAttribute('title'),/30\/140 XP earned within this level/);
  assert.equal(await page.locator('#sidebarProgressRemaining').count(),0,'standalone remaining-XP card element removed');
  assert.equal(await page.locator('#identityChip #sidebarProgress').count(),1,'XP progress is integrated inside identityChip');
  assert.equal(await page.locator('#identityLevelBadge').isVisible(),true,'sidebar avatar displays level badge');
  assert.equal(await page.locator('#identityLevelBadge').innerText(),'2');
  const badgeGeo=await page.evaluate(()=>{
    const a=document.getElementById('identityAvatar').getBoundingClientRect();
    const b=document.getElementById('identityLevelBadge').getBoundingClientRect();
    return {aRight:a.right,aBottom:a.bottom,bLeft:b.left,bTop:b.top,bRight:b.right,bBottom:b.bottom};
  });
  assert.ok(badgeGeo.bRight>=badgeGeo.aRight-6&&badgeGeo.bBottom>=badgeGeo.aBottom-6,'level badge sits at bottom-right corner of avatar');
  assert.equal(await page.locator('#sidebarProgressBar').getAttribute('value'),'30');
  assert.equal(await page.locator('#sidebarProgress').evaluate(el=>getComputedStyle(el).display),'none','collapsed sidebar hides XP/level section');
  await page.evaluate(()=>document.getElementById('appSidebar').classList.add('expanded'));
  assert.notEqual(await page.locator('#sidebarProgress').evaluate(el=>getComputedStyle(el).display),'none','expanded sidebar shows XP/level section');
  await page.waitForTimeout(260);
  const profileGeo=await page.evaluate(()=>{
    const box=document.getElementById('sidebarProgress');
    const s=getComputedStyle(box);
    const chip=document.getElementById('identityChip').getBoundingClientRect();
    const av=document.getElementById('identityAvatar').getBoundingClientRect();
    const name=document.getElementById('identityLabel').getBoundingClientRect();
    const xp=document.getElementById('sidebarProgressLabel').getBoundingClientRect();
    const bar=document.getElementById('sidebarProgressBar').getBoundingClientRect();
    const ns=getComputedStyle(document.getElementById('identityLabel'));
    return {
      border:s.borderTopWidth,bg:s.backgroundColor,
      avRight:av.right,nameLeft:name.left,nameTop:name.top,xpTop:xp.top,xpLeft:xp.left,xpRight:xp.right,barTop:bar.top,
      barLeft:bar.left,barRight:bar.right,chipRight:chip.right,barHeight:bar.height,
      overflow:ns.textOverflow,nowrap:ns.whiteSpace,
      nameFont:parseFloat(getComputedStyle(document.getElementById('identityLabel')).fontSize),
      xpFont:parseFloat(getComputedStyle(document.getElementById('sidebarProgressLabel')).fontSize),
    };
  });
  assert.equal(profileGeo.border,'0px','integrated profile XP has no standalone border');
  assert.equal(profileGeo.bg,'rgba(0, 0, 0, 0)','integrated profile XP has transparent background');
  assert.ok(profileGeo.nameLeft>=profileGeo.avRight-2&&profileGeo.barLeft>=profileGeo.avRight-2,'username and progress bar sit in column right of avatar');
  assert.ok(profileGeo.nameTop<profileGeo.barTop&&profileGeo.barTop<profileGeo.xpTop,'hierarchy orders username -> progress bar -> verified XP vertically');
  assert.ok(Math.abs(profileGeo.xpLeft-profileGeo.barLeft)<=2,'XP fraction aligns to left edge of progress bar');
  assert.ok(profileGeo.xpFont<profileGeo.nameFont,'verified XP label uses slightly smaller font than username');
  assert.ok(profileGeo.barRight<=profileGeo.chipRight,'progress bar fits proportionally inside profile chip');
  assert.ok(profileGeo.barHeight<=5,'progress bar is thin and understated');
  assert.equal(profileGeo.overflow,'ellipsis','long usernames truncate cleanly with ellipsis');
  assert.equal(profileGeo.nowrap,'nowrap');
  await snap('sidebar-profile-expanded.png');
  await page.evaluate(()=>switchQuizAccount(null));
  await page.waitForFunction(()=>document.querySelector('#sidebarProgressLabel').textContent.includes('Sign in'));
  assert.equal(await page.locator('#sidebarProgressBar').isHidden(),true,'guest mode hides progress bar');
  assert.equal(await page.locator('#identityLevelBadge').isHidden(),true,'guest mode hides avatar level badge');
  await page.evaluate(()=>document.getElementById('appSidebar').classList.remove('expanded'));
  // Both responsive sizes/themes use the actual app styles and native details.
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click().catch(()=>{});
  for(const width of [390,768,1360])for(const theme of ['dark','light']){
    await page.setViewportSize({width,height:900});
    await page.evaluate(theme=>document.documentElement.setAttribute('data-theme',theme),theme);
    await quiz.getByRole('heading',{name:'Quizzes',exact:true}).waitFor();
    await assertSelectionPresentation();
    await quiz.getByRole('button',{name:'Grammar',exact:true}).click();
    assert.equal(await quiz.locator('.quiz-chapter').count(),20,`${width}px ${theme}: all 20 Grammar chapters rendered`);
    const overflow=await quiz.evaluate(n=>n.scrollWidth>n.clientWidth+2);
    assert.equal(overflow,false,`${width}px ${theme}: no horizontal page overflow`);
    const firstChapter=quiz.locator('.quiz-chapter').first();
    if(await firstChapter.locator('.quiz-subtopics').getAttribute('open')!==null)await firstChapter.locator('.quiz-subtopics > summary').click();
    await assertChapterFooter(firstChapter);
    await firstChapter.scrollIntoViewIfNeeded();
    await snap(`quiz-selection-${width}-${theme}.png`);
    const disclosure=firstChapter.locator('.quiz-subtopics');
    if(await disclosure.getAttribute('open')===null)await disclosure.locator('> summary').click();
    await assertChapterFooter(firstChapter);
    if(width===390&&theme==='dark'){
      await firstChapter.locator('.quiz-chapter-footer').scrollIntoViewIfNeeded();
      await snap('quiz-mobile-dark.png');
    }
  }
  // The chapter action keeps its visible name while resuming the exact saved manifest.
  await page.setViewportSize({width:1360,height:960});
  const generalAction=()=>quiz.locator('[data-chapter="cgel-ch01"] .quiz-chapter-footer > button');
  await generalAction().click();
  await answerCurrentQuestion(true);
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  const generalDraft=await page.evaluate(()=>Object.values(JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')).attempts).find(t=>!t.submitted_at&&t.spec?.mode==='general'&&t.spec.chapter==='cgel-ch01'));
  assert.ok(generalDraft&&Object.keys(generalDraft.responses).length,'General Quiz auto-saves responses');
  await assertSelectionPresentation();
  assert.equal(await generalAction().innerText(),'General Quiz');
  assert.match(await generalAction().getAttribute('aria-label'),/Resume General Chapter Quiz/);
  await page.reload();await nav('quizzes');
  await quiz.getByRole('button',{name:'Grammar',exact:true}).click();
  await assertSelectionPresentation();
  await generalAction().click();
  const resumedGeneral=await page.evaluate(id=>JSON.parse(localStorage.getItem('syntutor:assessments:v1:guest')).attempts[id],generalDraft.attempt_id);
  assert.deepEqual(resumedGeneral.presented,generalDraft.presented);
  assert.deepEqual(resumedGeneral.responses,generalDraft.responses);
  await quiz.locator('.quiz-nav-row[aria-current="step"].is-answered').waitFor();
  await assertNoResults();
  await quiz.getByRole('button',{name:'All quizzes',exact:true}).click();
  // Seed only local fixture-account attempts; never write a real learner record.
  const seeded=makeV2Attempt({...fixtureBank,mixed_items:[...syntaxMixedItems,...cambridgeMixedItems]},actualCurriculum,
    {track:'syntax',mode:'topic',chapter:'br-01',topic:'concepts',format:'mixed'}, {},123,'seeded-review');
  seeded.submitted_at='2026-11-17T00:00:00Z';seeded.synced=true;
  seeded.responses=Object.fromEntries(seeded.presented.map(r=>[r.item_id,'incorrect']));
  await page.evaluate(attempt=>localStorage.setItem('syntutor:assessments:v1:quiz-review-seed',JSON.stringify({attempts:{[attempt.attempt_id]:attempt},drafts:{}})),seeded);
  await page.evaluate(()=>switchQuizAccount('quiz-review-seed'));
  await quiz.getByRole('button',{name:'Syntax',exact:true}).click();
  const seededReview=quiz.locator('.quiz-special-section.is-review');
  await seededReview.getByText(new RegExp('Test phrase boundaries')).waitFor();
  assert.ok((await seededReview.locator('.quiz-card-desc').innerText()).endsWith(topicDescriptions['br-01/concepts']));
  for(const width of [390,768,1360])for(const theme of ['light','dark']){
    await page.setViewportSize({width,height:900});
    await page.evaluate(theme=>document.documentElement.setAttribute('data-theme',theme),theme);
    const metrics=await seededReview.locator('.quiz-card-desc').evaluate(n=>({overflow:n.scrollWidth>n.clientWidth,clamp:getComputedStyle(n).webkitLineClamp,whiteSpace:getComputedStyle(n).whiteSpace}));
    assert.equal(metrics.overflow,false);assert.equal(metrics.clamp,'none');assert.equal(metrics.whiteSpace,'normal');
    assert.equal(await seededReview.locator('.quiz-card-title-wrap > span').count(),0);
    await seededReview.scrollIntoViewIfNeeded();await snap(`quiz-review-${width}-${theme}.png`);
  }
  for(const view of ['leaderboard','achievements','history']){
    await nav(view);
    assert.equal(await page.locator(`.sidebar-item[data-view="${view}"].active`).count(),1,`${view} route keeps active highlighting`);
    if(view==='history')await page.keyboard.press('Escape');
  }
  await nav('quizzes');
  await page.evaluate(()=>switchQuizAccount('quiz-review-empty'));
  await seededReview.getByText(/^Complete Syntax chapter or subtopic quizzes/).waitFor();
  assert.equal(await seededReview.getByRole('button').isDisabled(),true,'another account never inherits seeded errors');
  await page.evaluate(()=>switchQuizAccount(null));
  // The same sidebar order and active destinations survive the mobile drawer.
  await page.setViewportSize({width:390,height:900});
  const openMobileNav=async()=>{if(await page.locator('#mobileNavBtn').getAttribute('aria-expanded')!=='true')await page.locator('#mobileNavBtn').click();};
  await openMobileNav();await nav('builder');
  assert.equal(await page.locator('.sidebar-item[data-view="builder"].active').count(),1);
  await openMobileNav();await nav('tutor');
  assert.equal(await page.locator('.sidebar-item[data-view="tutor"].active').count(),1);
  await openMobileNav();await nav('quizzes');
  const history=quiz.locator('.quiz-history');
  const historySummary=history.locator('> summary');
  assert.equal(await historySummary.evaluate(n=>getComputedStyle(n).fontWeight),'700');
  assert.equal(await historySummary.evaluate(n=>getComputedStyle(n).cursor),'pointer');
  await historySummary.click();
  assert.equal(await history.getAttribute('open'),'');
  assert.equal(await historySummary.evaluate(n=>getComputedStyle(n).marginBottom),'12px');
  await historySummary.click();
  assert.equal(await history.getAttribute('open'),null);
  await historySummary.click();
  const historicalScore=(await history.locator('.quiz-history-row button').first().innerText()).match(/(\d+\/\d+) \((\d+)%\)$/);
  assert.ok(historicalScore,'completed attempts remain available in history');
  await history.locator('.quiz-history-row button').first().click();
  await quiz.locator('.quiz-score').filter({hasText:`${historicalScore[1]} correct (${historicalScore[2]}%)`}).waitFor();
  assert.ok(await quiz.locator('.quiz-review-card').count()>0,'historical responses and explanations remain readable after reload');
  assert.deepEqual(errors,[]);
  console.log('PASS Quiz V2 browser: General Quiz start/resume labels and saved responses; aligned chapter/subtopic actions; no difficulty pills or draft counts; vertical, keyboard-accessible question states and scrolling; equal-height desktop panels including tree builder; 390/768/1360px light/dark layouts; mixed formats, gated results/scoring, offline drafts, history and account/XP isolation; no page errors.');
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
