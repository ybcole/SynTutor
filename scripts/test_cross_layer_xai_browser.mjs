import assert from 'node:assert/strict';

const { chromium } = await import(process.env.QUIZ_V2_PLAYWRIGHT_MODULE || 'playwright');

const BASE_URL = process.env.SYNTUTOR_TEST_URL || 'http://127.0.0.1:8769';

const browser = await chromium.launch({
  headless: true,
  ...(process.env.QUIZ_V2_CHROMIUM_PATH ? { executablePath: process.env.QUIZ_V2_CHROMIUM_PATH } : {}),
});

async function submitAndInspect(page, sentence) {
  const responsePromise = page.waitForResponse(
    (res) => {
      if (!res.url().includes('/api/parse') || res.request().method() !== 'POST') return false;
      try { return res.request().postDataJSON()?.text?.trim() === sentence; } catch { return false; }
    },
    { timeout: 20000 },
  );
  const ta = page.locator('#inputText');
  await ta.click();
  await ta.fill(sentence);
  await ta.press('Enter');
  const res = await responsePromise;
  assert.equal(res.status(), 200, `Expected HTTP 200 for ${sentence}`);
  const payload = await res.json();
  await page.waitForFunction((expected) => {
    const el = document.querySelector('#inputText');
    const loading = document.querySelector('#loadingIndicator');
    const host = document.querySelector('#canonicalTreeView');
    return el?.value?.trim() === expected
      && !loading?.classList.contains('visible')
      && host && !host.hidden
      && host.querySelectorAll('svg [data-node-id]').length > 0;
  }, sentence, { timeout: 20000 });
  return payload;
}

try {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
  const skip = page.locator('.onboarding .onboarding-skip');
  await skip.waitFor({ state: 'visible', timeout: 5000 }).catch(() => {});
  if (await skip.isVisible().catch(() => false)) {
    await skip.click();
    await page.locator('#onboarding').waitFor({ state: 'hidden' });
  }

  // 1. Reported failure sentence: "I am scares tomorrow."
  const p1 = await submitAndInspect(page, 'I am scares tomorrow.');
  assert.equal(p1.learner_analysis.verdict, 'ungrammatical');
  assert(p1.learner_analysis.findings.some((f) => f.constraint === 'C-COPULA'));
  assert.equal(p1.learner_analysis.revision, undefined);

  // Tree has NO fabricated PP / empty P for 'tomorrow'
  const svgLabels = (await page.locator('#canonicalTreeView svg text').allTextContents()).map((s) => s.trim());
  assert(!svgLabels.includes('PP'), `Did not expect fabricated PP in tree: ${JSON.stringify(svgLabels)}`);
  assert(!svgLabels.includes('P'), `Did not expect fabricated P in tree: ${JSON.stringify(svgLabels)}`);

  // Interactive highlighting: 'scares' is error, 'I' & 'am' are related (not error)
  const errNodes = await page.locator('#canonicalTreeView svg g[data-legacy-issue="true"]').count();
  const relNodes = await page.locator('#canonicalTreeView svg g[data-learner-related="true"]').count();
  assert(errNodes >= 1, 'Expected error highlight on scares');
  assert(relNodes >= 2, 'Expected non-erroneous related highlights on I and am');

  // Click 'scares': qualified node text + C-COPULA finding + predicative lesson link
  const scaresGroup = page.locator('#canonicalTreeView svg g[data-legacy-issue="true"]').last();
  await scaresGroup.click();
  await page.waitForFunction(() => document.querySelector('#explainNode')?.innerText.includes('scares'));
  const scaresText = await page.locator('#explainNode').innerText();
  assert(!scaresText.includes('is a plural noun'), `Contradictory plural noun claim: ${scaresText}`);
  assert(!scaresText.includes('predicative adjective complement'), `Contradictory adj-comp claim: ${scaresText}`);
  const scaresHref = await page.locator('#explainNode .xai-lesson-link').getAttribute('href');
  assert.equal(scaresHref, '#lesson/br-04/predicatives', `Expected predicatives lesson, got ${scaresHref}`);

  // Click 'am': qualified local agreement that does NOT imply full sentence grammaticality
  const amGroup = page.locator('#canonicalTreeView svg g[data-node-id]:has-text("am")').last();
  await amGroup.click();
  await page.waitForFunction(() => document.querySelector('#explainNode')?.innerText.includes('am'));
  const amText = await page.locator('#explainNode').innerText();
  assert(amText.includes('does not establish that the rest of the sentence is grammatical'),
    `Expected qualified local agreement on 'am': ${amText}`);

  // Click 'tomorrow': temporal adjunct explanation + adjuncts lesson (NOT prepositions!)
  const tomGroup = page.locator('#canonicalTreeView svg g[data-node-id]:has-text("tomorrow")').last();
  await tomGroup.click();
  await page.waitForFunction(() => document.querySelector('#explainNode')?.innerText.includes('tomorrow'));
  const tomText = await page.locator('#explainNode').innerText();
  assert(tomText.includes('temporal adverbial modifier'), `Expected temporal modifier prose: ${tomText}`);
  const tomHref = await page.locator('#explainNode .xai-lesson-link').getAttribute('href');
  assert.equal(tomHref, '#lesson/br-05/concepts', `Expected adjuncts lesson for tomorrow, got ${tomHref}`);

  // 2. Positive control: "I am scared tomorrow."
  const p2 = await submitAndInspect(page, 'I am scared tomorrow.');
  assert.equal(p2.learner_analysis.verdict, 'grammatical');
  assert.equal(p2.learner_analysis.findings.length, 0);
  assert.equal(await page.locator('#canonicalTreeView svg g[data-legacy-issue="true"]').count(), 0);

  // 3. Auxiliary + finite verb: "She is sleeps today." -> C-AUX-FORM + clean revision
  const p3 = await submitAndInspect(page, 'She is sleeps today.');
  assert.equal(p3.learner_analysis.verdict, 'ungrammatical');
  assert(p3.learner_analysis.findings.some((f) => f.constraint === 'C-AUX-FORM'));
  assert.equal(p3.learner_analysis.revision?.text, 'She is sleeping today.');
  const revText = await page.locator('#explainNode').innerText();
  assert(revText.includes('She is sleeping today.'), `Expected validated revision in explain pane: ${revText}`);

  // 4. Positive plural nominal control + licensed ellipsis: "Those are scares."
  const p4 = await submitAndInspect(page, 'Those are scares.');
  assert.equal(p4.learner_analysis.verdict, 'grammatical');
  assert.equal(p4.learner_analysis.findings.length, 0);
  const scaresCtrl = page.locator('#canonicalTreeView svg g[data-node-id]:has-text("scares")').last();
  await scaresCtrl.click();
  await page.waitForFunction(() => document.querySelector('#explainNode')?.innerText.includes('predicative complement'));
  const scaresCtrlText = await page.locator('#explainNode').innerText();
  assert(scaresCtrlText.includes('plural noun'), scaresCtrlText);
  assert(!scaresCtrlText.includes('adjective'), scaresCtrlText);

  // 5. Lexical uncertainty vs canonical determiner/possessive controls ("Ths cat sleeps.", "Ths boys walk.", "His cat sleeps.", "Ana sleeps.")
  const pHis = await submitAndInspect(page, 'His cat sleeps.');
  assert.equal(pHis.br_analysis.status, 'normalized');
  const hisLabels = (await page.locator('#canonicalTreeView svg text').allTextContents()).map((s) => s.trim());
  assert(hisLabels.includes('POSS'), `Expected canonical POSS on 'His cat sleeps.': ${JSON.stringify(hisLabels)}`);

  const pThs = await submitAndInspect(page, 'Ths cat sleeps.');
  assert.equal(pThs.br_analysis.status, 'unresolved');
  assert.equal(pThs.learner_analysis.tree_status, 'provisional');
  const thsLabels = (await page.locator('#canonicalTreeView svg text').allTextContents()).map((s) => s.trim());
  assert(!thsLabels.includes('POSS'), `Must not display unverified POSS node for 'Ths': ${JSON.stringify(thsLabels)}`);
  assert(!thsLabels.includes('DET'), `Must not fabricate canonical DET node for 'Ths': ${JSON.stringify(thsLabels)}`);
  const noticeText = await page.locator('#treeAuthorityNotice').innerText();
  assert(noticeText.includes('Provisional B-R working tree'), `Expected provisional notice: ${noticeText}`);
  const thsFullExplain = await page.locator('#explainNode').innerText();
  assert(thsFullExplain.includes('Lexical uncertainty'), `Expected lexical uncertainty badge: ${thsFullExplain}`);
  assert(thsFullExplain.includes('“Ths”') && thsFullExplain.includes('uncertain'), `Expected uncertainty explanation for Ths: ${thsFullExplain}`);
  assert(thsFullExplain.includes('“The”') && thsFullExplain.includes('“This”'), `Expected plausible readings for Ths: ${thsFullExplain}`);
  assert(thsFullExplain.includes('agrees with its subject'), `Expected valid agreement between cat and sleeps preserved: ${thsFullExplain}`);
  assert(!thsFullExplain.includes('The checks found no clear grammatical issue.'), `Must not claim clean verification: ${thsFullExplain}`);
  assert(!thsFullExplain.toLowerCase().includes('possessive'), `Must not claim possessive for Ths: ${thsFullExplain}`);

  // Click 'Ths' node directly -> verify node-level uncertainty explanation & Determiners lesson
  const thsNode = page.locator('#canonicalTreeView svg g[data-node-id="sg-root-0-0"]');
  await thsNode.click();
  await page.waitForFunction(() => document.querySelector('#explainNode [data-learner-reset-selection]') !== null);
  const thsNodeText = await page.locator('#explainNode').innerText();
  assert(thsNodeText.includes('orthographically uncertain token'), `Expected node-level uncertainty on Ths: ${thsNodeText}`);
  assert(!thsNodeText.toLowerCase().includes('possessive'), `Must not call Ths a possessive word: ${thsNodeText}`);
  const thsLessonHref = await page.locator('#explainNode .xai-lesson-link').getAttribute('href');
  assert.equal(thsLessonHref, '#lesson/br-07/concepts');

  // Plural agreement preserved under lexical uncertainty ("Ths boys walk.")
  const pThsBoys = await submitAndInspect(page, 'Ths boys walk.');
  assert.equal(pThsBoys.br_analysis.status, 'unresolved');
  const thsBoysExplain = await page.locator('#explainNode').innerText();
  assert(thsBoysExplain.includes('“boys”') && thsBoysExplain.includes('“walk”') && thsBoysExplain.includes('agrees with its subject'),
    `Expected valid plural agreement on Ths boys walk.: ${thsBoysExplain}`);
  assert(thsBoysExplain.includes('“The”') && thsBoysExplain.includes('“These”') && thsBoysExplain.includes('“Those”'),
    `Expected plural-compatible determiner readings: ${thsBoysExplain}`);

  // Proper-name control ("Ana sleeps.") stays canonical & clean
  const pAna = await submitAndInspect(page, 'Ana sleeps.');
  assert.equal(pAna.br_analysis.status, 'normalized');
  const anaLabels = (await page.locator('#canonicalTreeView svg text').allTextContents()).map((s) => s.trim());
  assert(anaLabels.includes('name'), `Expected canonical name node for Ana: ${JSON.stringify(anaLabels)}`);

  await context.close();
  console.log('PASS: live Flask + Chromium cross-layer consistency, licensing, explanations, corrections, and lesson routing.');
} finally {
  await browser.close();
}
