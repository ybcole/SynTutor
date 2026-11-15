// Capture the actual rendered Syntax teaching, not source-code strings or an
// obsolete catalog. Playwright is build/test tooling only, not an app dependency.
import {createServer} from 'node:http';
import {readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {loadActiveCourse,quizCurriculum} from '../web/js/lesson-curriculum.js';
import {syntaxPracticeDigest} from '../web/js/quiz-lesson-practice.js';
const {chromium}=await import(process.env.QUIZ_V2_PLAYWRIGHT_MODULE || 'playwright');
const root=path.resolve('web');
const course=await loadActiveCourse(async p=>({ok:true,json:async()=>JSON.parse(await readFile(path.join(root,p),'utf8'))}));
const syntax=quizCurriculum(course).find(t=>t.id==='syntax');
const server=createServer(async(req,res)=>{
  try{
    const url=new URL(req.url,'http://localhost');
    const filename=path.resolve(root,'.'+(url.pathname==='/'?'/index.html':url.pathname));
    if(!filename.startsWith(root+path.sep))throw Error('Invalid path');
    const data=await readFile(filename);
    res.writeHead(200,{'Content-Type':{'.js':'application/javascript','.json':'application/json','.css':'text/css','.html':'text/html','.svg':'image/svg+xml'}[path.extname(filename)]||'application/octet-stream'});res.end(data);
  }catch{res.writeHead(404);res.end();}
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const base=`http://127.0.0.1:${server.address().port}`,browser=await chromium.launch();
try{
  const page=await browser.newPage();
  await page.addInitScript(()=>{localStorage.setItem('syntutor_onboarding_seen','1');window.Clerk={load:async()=>{},addListener(){}};});
  await page.route('**/*',route=>{
    const url=route.request().url();
    if(url.startsWith(base+'/js/config.js'))return route.fulfill({contentType:'application/javascript',body:"export const CLERK_CONFIG={publishableKey:'pk_test_fixture'};export const SUPABASE_CONFIG={url:'https://fixture.test',anonKey:'fixture'};export const API_BASE='';"});
    if(url.startsWith('https://esm.sh/'))return route.fulfill({contentType:'application/javascript',body:'export const createClient=()=>null;'});
    return url.startsWith(base)?route.continue():route.abort();
  });
  await page.goto(base);
  await page.locator('.sidebar-item[data-view="lessons"]').click();
  await page.locator('#curriculumView .curriculum-card').first().waitFor();
  const sections=[];
  for(const chapter of syntax.chapters)for(const topic of chapter.topics){
    await page.evaluate(async({id,section})=>{
      const lessons=await import('/js/lessons-ui.js?v=2026.11.16c');
      await lessons.openLessons(id,{section});
    },{id:chapter.id,section:topic.id});
    const texts=await page.locator('#curriculumView .lesson-stage-body').evaluate(body=>
      [...body.querySelectorAll('p,li,th,td')].filter(n=>
        !n.closest('.lesson-sources,.lesson-tree-wrap,.lesson-quick-check,.lesson-feedback,.lesson-page-actions,button')
      ).map(n=>n.textContent.replace(/\s+/g,' ').trim()).filter(t=>t.length>=45)
    );
    sections.push({lesson_id:chapter.id,subtopic_id:topic.id,title:topic.title,
      lesson_version:chapter.content_version,article_digest:syntaxPracticeDigest(chapter.id),texts:[...new Set(texts)]});
  }
  const output=process.env.QUIZ_PRACTICE_OUTPUT || 'web/content/quizzes/syntax-practice-source.json';
  await writeFile(output,JSON.stringify({schema_version:'1.0.0',source_kind:'rendered-active-syntutor-lessons',sections},null,2)+'\n');
  console.log(`Captured ${sections.length} actual Syntax sections to ${output}`);
}finally{await browser.close();await new Promise(r=>server.close(r));}
