// Comprehensive live Chromium end-to-end verification of SynTutor interactive
// XAI, generalized evidence propagation, node selection, error/related
// highlighting, partial vs complete revisions, lesson links, and state reset.
import assert from 'node:assert/strict';

const { chromium } = await import(process.env.QUIZ_V2_PLAYWRIGHT_MODULE || 'playwright');
const origin = process.env.SYNTUTOR_TEST_ORIGIN || 'http://127.0.0.1:8769';
const browser = await chromium.launch({ headless: true });

try {
  const page = await browser.newPage();
  const pageErrors = [];
  page.on('pageerror', error => pageErrors.push(error.message));
  await page.addInitScript(() => localStorage.setItem('syntutor_onboarding_seen', '1'));
  await page.route('**/*', route => {
    const url = new URL(route.request().url());
    if (url.origin === origin) return route.continue();
    if (url.host === 'esm.sh') {
      return route.fulfill({ contentType: 'application/javascript', body: 'export const createClient = () => null;' });
    }
    return route.abort();
  });

  const health = await page.request.get(`${origin}/api/health`, { timeout: 120_000 });
  assert.equal(health.status(), 200, await health.text());

  await page.goto(origin, { waitUntil: 'domcontentloaded' });
  await page.evaluate(async () => {
    await import(document.querySelector('script[src*="js/main.js"]').src);
  });

  const input = page.locator('#inputText');
  const tree = page.locator('#canonicalTreeView');
  const explain = page.locator('#explainNode');

  async function submitSentence(sentence) {
    await input.click();
    await input.fill(sentence);
    const pending = page.waitForResponse(
      r => r.url() === `${origin}/api/parse` && r.request().method() === 'POST' && r.request().postDataJSON()?.text === sentence,
      { timeout: 60_000 },
    );
    await input.press('Enter');
    const resp = await pending;
    assert.equal(resp.status(), 200, await resp.text());
    const payload = await resp.json();
    await explain.locator('[data-xai-short]').waitFor({ timeout: 15_000 });
    return payload;
  }

  // 1. Relational agreement with distractor PP: error vs related evidence vs clean distractor
  const agrPayload = await submitSentence('The boy with the bags walk.');
  assert.equal(agrPayload.br_analysis.status, 'normalized');
  assert.equal(agrPayload.learner_analysis.findings.length, 1);

  const walkBtn = tree.locator('svg').getByRole('button', { name: 'Inspect Burton-Roberts word for walk', exact: true }).first();
  const boyBtn = tree.locator('svg').getByRole('button', { name: 'Inspect Burton-Roberts word for boy', exact: true }).first();
  const bagsBtn = tree.locator('svg').getByRole('button', { name: 'Inspect Burton-Roberts word for bags', exact: true }).first();
  assert.equal(await walkBtn.getAttribute('data-legacy-issue'), 'true', 'violating verb must be marked as error');
  assert.equal(await boyBtn.getAttribute('data-learner-related'), 'true', 'subject head must be marked as related evidence');
  assert.equal(await boyBtn.getAttribute('data-legacy-issue'), null, 'non-erroneous subject must NOT be marked as error');
  assert.equal(await bagsBtn.getAttribute('data-legacy-issue'), null, 'distractor PP noun must NOT be marked as error');
  assert.equal(await bagsBtn.getAttribute('data-learner-related'), null, 'distractor PP noun must NOT be marked related');

  // Click leaf node 'boy' -> verify context-specific explanation & non-destructive error highlight
  await boyBtn.press('Enter');
  await explain.locator('[data-xai-short]').waitFor();
  const boyText = await explain.innerText();
  assert.match(boyText, /singular noun/i);
  assert.match(boyText, /subject/i);
  assert.match(boyText, /walk/);
  assert.equal(await boyBtn.getAttribute('data-selected'), 'true');
  assert.equal(await walkBtn.getAttribute('data-legacy-issue'), 'true', 'selecting another node must NOT erase error highlight');
  const lessonLink = explain.locator('.xai-lesson-link');
  assert.equal(await lessonLink.count(), 1, 'lesson link should be present');
  assert.match(await lessonLink.getAttribute('href'), /^#lesson\//);

  // Click phrase node NP & clause node S -> verify distinct phrase/clause explanations
  const npBtn = tree.locator('svg').getByRole('button', { name: 'Inspect Burton-Roberts NP for The boy with the bags', exact: true }).first();
  await npBtn.press('Enter');
  const npText = await explain.innerText();
  assert.match(npText, /noun phrase/i);
  assert.match(npText, /subject/i);
  assert.notEqual(npText, boyText);

  const sBtn = tree.locator('svg').getByRole('button', { name: /^Inspect Burton-Roberts S for The boy with the bags walk/ }).first();
  await sBtn.press('Enter');
  const sText = await explain.innerText();
  assert.match(sText, /subject.*predicate/i);

  // Click "Show full sentence analysis" reset button -> verify selection clears cleanly
  const resetBtn = explain.locator('[data-learner-reset-selection]');
  assert.equal(await resetBtn.count(), 1, 'reset-selection button should restore sentence-level analysis');
  await resetBtn.click();
  assert.equal(await tree.locator('[data-selected="true"]').count(), 0, 'selection cleared');
  const fullText = await explain.innerText();
  assert.match(fullText, /Suggested revision.*The boy with the bags walks\./);

  // 2. Partial vs complete repair labeling
  const partialPayload = await submitSentence('Ths cat sleepps.');
  assert.equal(partialPayload.learner_analysis.revision.text, 'Ths cat sleeps.');
  assert.equal(partialPayload.learner_analysis.revision.impact.whole_sentence_clean, false);
  const partialText = await explain.innerText();
  assert.match(partialText, /Partial revision — “Ths cat sleeps\.”/);
  assert.match(partialText, /“Ths” remains uncertain/);

  // 3. Generalized evidence propagation on provisional working tree (2 independent errors)
  const provPayload = await submitSentence('If you dont know, the boys walks.');
  assert.equal(provPayload.learner_analysis.tree_status, 'provisional');
  assert.equal(provPayload.learner_analysis.findings.length, 2);
  const provText = await explain.innerText();
  assert.match(provText, /Partial grammatical analysis/);
  assert.match(provText, /walks/);
  assert.match(provText, /don't/);

  // 4. Newly propagated rule families (C-ARTICLE + irregular morphology C-VERB-FORM 'brang')
  await submitSentence('She bought apple.');
  const artText = await explain.innerText();
  assert.match(artText, /apple/i);
  assert.match(artText, /Suggested revision — “She bought an apple\.”/);

  await submitSentence('He always brang bad marks home.');
  const brangText = await explain.innerText();
  assert.match(brangText, /brang/i);
  assert.match(brangText, /Suggested revision — “He always brought bad marks home\.”/);

  // 5. Submit clean complex grammatical sentence -> verify ZERO stale state & rich node explanations
  const cleanPayload = await submitSentence('The careful student has read the book on the bus.');
  assert.equal(cleanPayload.br_analysis.status, 'normalized');
  assert.equal(cleanPayload.learner_analysis.findings.length, 0);
  assert.equal(await tree.locator('[data-legacy-issue="true"]').count(), 0, 'no stale error highlights');
  assert.equal(await tree.locator('[data-selected="true"]').count(), 0, 'no stale selection');
  const cleanOverview = await explain.innerText();
  assert.doesNotMatch(cleanOverview, /brang|walks|Ths|apple/);
  assert.match(cleanOverview, /no clear grammatical issue/i);

  // Inspect leaf (PERF 'has', N 'student'), phrase (PP 'on the bus', VP 'has read the book on the bus'), clause (S)
  for (const [label, pattern] of [
    ['Inspect Burton-Roberts word for has', /perfect auxiliary/i],
    ['Inspect Burton-Roberts word for student', /singular noun/i],
    ['Inspect Burton-Roberts PP for on the bus', /preposition.*complement/i],
    ['Inspect Burton-Roberts VP for has read the book on the bus', /verb phrase|combines/i],
    ['Inspect Burton-Roberts S for The careful student has read the book on the bus', /subject.*predicate/i],
  ]) {
    const btn = tree.locator('svg').getByRole('button', { name: label, exact: true }).first();
    await btn.press('Enter');
    const txt = await explain.innerText();
    assert.match(txt, pattern, `Expected ${pattern} for ${label}, got: ${txt}`);
    assert.doesNotMatch(txt, /position in |expresses what happens/i, `Shallow boilerplate on ${label}: ${txt}`);
  }

  assert.deepEqual(pageErrors, [], `Unexpected browser page errors: ${pageErrors}`);
  console.log('PASS: live Chromium interactive XAI, evidence propagation, highlighting, partial revisions, and state-reset suite.');
} finally {
  await browser.close();
}
