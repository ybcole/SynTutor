import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createServer} from 'node:http';
import path from 'node:path';
const {chromium}=await import(process.env.QUIZ_V2_PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve('web');
const server=createServer(async(req,res)=>{
 try{const url=new URL(req.url,'http://localhost');const file=path.resolve(root,'.'+(url.pathname==='/'?'/index.html':url.pathname));if(!file.startsWith(root+'/'))throw Error();
 const body=await readFile(file);res.writeHead(200,{'Content-Type':{'.html':'text/html','.js':'application/javascript','.css':'text/css','.json':'application/json'}[path.extname(file)]||'text/plain'});res.end(body);
 }catch{res.writeHead(404);res.end();}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const base=`http://127.0.0.1:${server.address().port}`;
const browser=await chromium.launch({headless:true,...(process.env.QUIZ_V2_CHROMIUM_PATH?{executablePath:process.env.QUIZ_V2_CHROMIUM_PATH}:{})});
try{
 const page=await browser.newPage({viewport:{width:1360,height:920}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>{
  localStorage.setItem('syntutor_onboarding_seen','1');const now=Date.now();Date.now=()=>now;
  window.historyReadCount=0;
  window.historyFixtures=[0,1,1.0001,7,30].map((days,i)=>({id:String(i),user_id:'account-a',sentence:`History sentence ${i}.`,is_valid:i%2===0,created_at:new Date(now-days*86400000).toISOString()}));
  historyFixtures.push({id:'missing',user_id:'account-a',sentence:'Undated analysis.',is_valid:false,created_at:null},{id:'b',user_id:'account-b',sentence:'Private account B sentence.',created_at:new Date(now).toISOString()});
  window.Clerk={load:async()=>{},addListener(fn){window.accountListener=fn;}};
  window.switchAccount=id=>{window.currentAccount=id;Clerk.user=id?{id,firstName:id}:null;Clerk.session=id?{id:'session-'+id,getToken:async()=>id}:null;window.accountListener?.();};switchAccount('account-a');
 });
 await page.route('**/*',route=>{
  const url=route.request().url();
  if(url.startsWith(base+'/js/config.js'))return route.fulfill({contentType:'application/javascript',body:"export const CLERK_CONFIG={publishableKey:'pk_test_history'};export const SUPABASE_CONFIG={url:'https://fixture.test',anonKey:'fixture'};export const API_BASE='';"});
  if(url.startsWith('https://esm.sh/'))return route.fulfill({contentType:'application/javascript',body:`export const createClient=()=>{
   const owner=window.currentAccount;return {rpc:(name)=>{const result={data:name==='get_my_progression'?{xp:250}:[],error:null};return {then:r=>Promise.resolve(result).then(r),abortSignal:async()=>result};},from:table=>{
    const query={select(){return this},eq(){return this},order(){return this},limit(){return this},range:async(start,end)=>{if(table==='analysis_history')window.historyReadCount++;return {data:table==='analysis_history'?window.historyFixtures.filter(r=>r.user_id===owner).slice(start,end+1):[],error:null}},then:r=>Promise.resolve({data:[],error:null}).then(r)};return query;
   }};
  };`});
  return url.startsWith(base)?route.continue():route.abort();
 });
 await page.goto(base);const toggle=page.locator('#headerHistoryBtn');await toggle.waitFor();await toggle.click();
 const panel=page.locator('.pane-side #historyDrawerBackdrop');await panel.waitFor();
 const entries=page.locator('#historyList .history-item');await entries.first().waitFor();assert.equal(await entries.count(),6);
 const range=page.locator('#historyTimeFilter');await range.selectOption('day');assert.equal(await entries.count(),2);
 await range.selectOption('week');assert.equal(await entries.count(),4);
 await range.selectOption('month');assert.equal(await entries.count(),5);
 await range.selectOption('all');assert.equal(await entries.count(),6);
 assert.equal(await page.evaluate(()=>historyReadCount),1,'range filtering uses the account cache');
 assert.equal(await page.locator('.history-item.is-valid,.history-item.is-invalid,#historyFilters').count(),0);
 const listText=await page.locator('#historyList').innerText();assert.doesNotMatch(listText,/Errors|Valid/);assert.match(listText,/Date unavailable/);
 const border=await entries.first().evaluate(n=>{const s=getComputedStyle(n);return [s.borderLeftColor,s.borderRightColor,s.borderLeftWidth,s.borderRightWidth]});assert.equal(border[0],border[1]);assert.equal(border[2],border[3]);
 const icon=await toggle.boundingBox(),side=await page.locator('.pane-side').boundingBox();assert.ok(icon.x>=side.x&&icon.x<side.x+60&&icon.y<side.y+45,'History icon is at upper left of Generator side panel');
 await page.evaluate(()=>switchAccount('account-b'));await toggle.click();await entries.first().waitFor();assert.equal(await entries.count(),1);assert.match(await entries.innerText(),/Private account B/);assert.doesNotMatch(await entries.innerText(),/History sentence/);
 await range.selectOption('day');assert.equal(await entries.count(),1);
 // Empty filtered state without modifying records.
 await page.evaluate(()=>{historyFixtures.find(r=>r.user_id==='account-b').created_at='2000-01-01T00:00:00Z';switchAccount('account-a');switchAccount('account-b');});
 await toggle.click();
 await range.selectOption('day');await page.locator('.history-empty').filter({hasText:'No matching analyses'}).waitFor();
 await range.selectOption('all');await entries.first().waitFor();
 // Reopening uses the existing replay handler. Intercept parse to observe restoration.
 let reopened='';await page.route('**/api/parse',route=>{reopened=route.request().postDataJSON().text;return route.fulfill({status:503,contentType:'application/json',body:'{"error":"Fixture stops after observing replay"}'});});
 await entries.first().click();await page.waitForFunction(()=>document.getElementById('inputText').value==='Private account B sentence.');
 assert.equal(await panel.isVisible(),false);assert.equal(reopened,'Private account B sentence.');
 for(const width of [1360,390])for(const theme of ['light','dark']){
  await page.setViewportSize({width,height:920});await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);await page.waitForTimeout(250);
  await toggle.click();await panel.waitFor();
  const metrics=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,builder:document.getElementById('inlineBuilderArea').getBoundingClientRect().top,gen:document.querySelector('.canvas-wrap').getBoundingClientRect().bottom}));
  assert.equal(metrics.overflow,false);assert.ok(metrics.builder>metrics.gen,'Builder appears below Generator');
  if(process.env.QUIZ_V2_SCREENSHOT_DIR)await page.screenshot({path:path.join(process.env.QUIZ_V2_SCREENSHOT_DIR,`history-${width}-${theme}.png`),fullPage:width===390});
  await page.locator('#closeDrawerBtn').click();
 }
 await page.evaluate(()=>switchAccount(null));assert.equal(await toggle.isHidden(),true);assert.equal(await panel.isVisible(),false);
 assert.deepEqual(errors,[]);console.log('PASS History browser: side-panel placement, neutral entries, cache/time filters, account isolation, empty dates/ranges, replay, responsive light/dark layouts.');
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
