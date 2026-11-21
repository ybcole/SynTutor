// Run against a live SynTutor Flask server with its normal NLP models.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const { chromium } = await import(process.env.QUIZ_V2_PLAYWRIGHT_MODULE || 'playwright');
const origin = process.env.SYNTUTOR_TEST_ORIGIN || 'http://127.0.0.1:8768';
const output = process.env.SYNTUTOR_TEST_ARTIFACTS;
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
  const manifest = { health: await health.json(), sha256: {}, cases: [] };
  for (const asset of ['index.html', 'js/main.js', 'js/config.js', 'js/explanation-evidence.js', 'js/ui.js', 'js/correction.js']) {
    const response = await page.request.get(`${origin}/${asset}`);
    assert.equal(response.headers()['cache-control'], 'no-store');
    const bytes = await response.body();
    assert.deepEqual(bytes, await readFile(join('web', asset)));
    manifest.sha256[asset] = createHash('sha256').update(bytes).digest('hex');
  }
  if (output) await mkdir(output, { recursive: true });

  async function submit(id, sentence) {
    await page.goto(origin, { waitUntil: 'domcontentloaded' });
    await page.evaluate(async () => {
      await import(document.querySelector('script[src*="js/main.js"]').src);
    });
    const input = page.locator('#inputText');
    await input.click();
    await input.fill(sentence);
    const pending = page.waitForResponse(response => response.url() === `${origin}/api/parse`
      && response.request().method() === 'POST' && response.request().postDataJSON()?.text === sentence);
    await input.press('Enter');
    const response = await pending;
    assert.equal(response.status(), 200, await response.text());
    const payload = await response.json();
    assert.equal(payload.parse.text, sentence);
    await page.locator('[data-xai-short]').waitFor();
    const tree = page.locator('#treeAuthorityNotice');
    const explanation = page.locator('#explainNode');
    const record = {id, sentence, tree: await tree.innerText(), explanation: await explanation.innerText()};
    manifest.cases.push(record);
    if (output) await writeFile(join(output, `${id}.json`), JSON.stringify(payload, null, 2) + '\n');
    return { payload, explanation, record };
  }

  const { payload: auxiliary, record: be } = await submit('auxiliary', 'I am ate an apple yesterday.');
  assert.equal(auxiliary.br_analysis.status, 'unresolved');
  assert.equal(auxiliary.summary.corrected_sentence, 'I ate an apple yesterday.');
  assert.match(be.tree, /Provisional B-R working tree/);
  assert.match(be.explanation, /Partial grammatical analysis/);
  assert.match(be.explanation, /simple past form.*-ing form.*past participle/s);
  assert.match(be.explanation, /possible revision is “I ate an apple yesterday\.”/);

  const { payload: contraction, explanation, record: conditional } = await submit('contraction', 'If you dont know.');
  assert.equal(contraction.br_analysis.status, 'unresolved');
  assert.equal(contraction.summary.corrected_sentence, undefined);
  assert.match(conditional.explanation, /conditional clause/);
  assert.match(conditional.explanation, /conversation.*formal writing/);
  assert.match(conditional.explanation, /don't.*negation.*know.*lexical verb/s);
  const tree = page.locator('#canonicalTreeView');
  assert.equal(await tree.getByRole('button', { name: /Inspect Burton-Roberts Adv for (do|nt)$/ }).count(), 0);
  await tree.locator('svg').getByRole('button', { name: 'Inspect Burton-Roberts word for know', exact: true }).press('Enter');
  await explanation.locator('[data-xai-short]').waitFor();
  conditional.selectedExplanation = await explanation.innerText();
  assert.match(conditional.selectedExplanation, /know.*lexical verb/);
  assert.doesNotMatch(conditional.selectedExplanation, /cannot be the main verb|is running|runs/);

  const { record: uncertain } = await submit('uncertain', 'They demolished.');
  assert.match(uncertain.explanation, /Analysis incomplete.*inconclusive/);
  const { payload: valid } = await submit('canonical', 'The apple was eaten yesterday.');
  assert.equal(valid.br_analysis.status, 'normalized');
  assert.equal(valid.summary.corrected_sentence, undefined);
  const { payload: homograph, record: cant } = await submit('homograph', 'A cant is a kind of slope.');
  assert.equal(homograph.br_analysis.status, 'unresolved');
  assert.equal(homograph.summary.corrected_sentence, undefined);
  assert.match(cant.explanation, /Analysis incomplete/);

  const unicode = 'Naomi 😊 will go later.';
  await submit('unicode', unicode);
  const selectedText = await page.locator('#inputText').evaluate(input =>
    input.value.slice(input.selectionStart, input.selectionEnd));
  assert.equal(selectedText, unicode);
  const input = page.locator('#inputText');
  await input.click();
  await input.fill('🙂?!');
  const rejected = page.waitForResponse(response => response.url() === `${origin}/api/parse`
    && response.request().postDataJSON()?.text === '🙂?!');
  await input.press('Enter');
  assert.equal((await rejected).status(), 422);
  await page.getByText('Unable to produce a parse', { exact: true }).first().waitFor();
  assert.equal(await page.locator('#canonicalTreeView').isVisible(), false);
  assert.equal(await page.locator('[data-xai-short]').count(), 0);

  const firstText = 'The boys walks.';
  const latestText = 'The children sang.';
  let reachedServer;
  let releaseFirst;
  const firstHeld = new Promise(resolve => { reachedServer = resolve; });
  const release = new Promise(resolve => { releaseFirst = resolve; });
  await page.route(`${origin}/api/parse`, async route => {
    if (route.request().postDataJSON()?.text !== firstText) return route.fallback();
    const response = await route.fetch();
    reachedServer();
    await release;
    await route.fulfill({ response });
  });
  const stale = page.waitForResponse(response => response.url() === `${origin}/api/parse`
    && response.request().postDataJSON()?.text === firstText).catch(() => null);
  await input.click();
  await input.fill(firstText);
  await input.press('Enter');
  await firstHeld;
  assert.equal(await page.locator('#loadingIndicator').getAttribute('aria-hidden'), 'false');
  const latest = page.waitForResponse(response => response.url() === `${origin}/api/parse`
    && response.request().postDataJSON()?.text === latestText, { timeout: 5_000 });
  await input.click();
  await input.fill(latestText);
  await input.press('Enter');
  try {
    assert.equal((await latest).status(), 200);
  } finally {
    releaseFirst();
  }
  const staleResponse = await stale;
  assert.equal(staleResponse?.status(), 200);
  await staleResponse.finished();
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  await page.locator('#canonicalTreeView').getByRole('button', { name: 'Inspect Burton-Roberts word for sang', exact: true }).first().waitFor();
  assert.equal(await input.inputValue(), latestText);
  assert.equal(await page.locator('#loadingIndicator').getAttribute('aria-hidden'), 'true');
  assert.doesNotMatch(await page.locator('#explainNode').innerText(), /walks/);
  manifest.rapidSubmissions = { firstText, latestText, renderedText: await input.inputValue() };
  assert.deepEqual(pageErrors, []);
  if (output) await writeFile(join(output, 'browser.json'), JSON.stringify(manifest, null, 2) + '\n');
  console.log('PASS: real Flask browser parity, Unicode selection, rejected input and rapid submissions.');
} finally {
  await browser.close();
}
