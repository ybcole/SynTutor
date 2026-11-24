import assert from 'node:assert/strict';

const { chromium } = await import(process.env.QUIZ_V2_PLAYWRIGHT_MODULE || 'playwright');
const origin = process.env.SYNTUTOR_TEST_ORIGIN || 'http://127.0.0.1:8769';
const browser = await chromium.launch({ headless: true });

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.addInitScript(() => localStorage.setItem('syntutor_onboarding_seen', '1'));
  await page.route('**/*', route => {
    const url = new URL(route.request().url());
    if (url.origin === origin) return route.continue();
    if (url.host === 'esm.sh') {
      return route.fulfill({ contentType: 'application/javascript', body: 'export const createClient = () => null;' });
    }
    return route.abort();
  });
  await page.goto(origin, { waitUntil: 'domcontentloaded' });
  await page.evaluate(async () => import(document.querySelector('script[src*="js/main.js"]').src));
  const input = page.locator('#inputText');
  await input.click();
  await input.fill('Did she can swim?');
  await input.press('Enter');
  await page.locator('#canonicalTreeView svg').waitFor({ timeout: 60_000 });
  await page.locator('#treeAuthorityNotice').waitFor();
  await page.locator('#canvasTreeTextBody').waitFor();

  for (const [width, height] of [[1440, 900], [1024, 640], [390, 844]]) {
    await page.setViewportSize({ width, height });
    await page.getByRole('button', { name: 'Fit syntax tree' }).click();
    const result = await page.evaluate(async () => {
      const settle = () => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      const notice = document.querySelector('#treeAuthorityNotice');
      const hint = document.querySelector('#builderHint');
      const reader = document.querySelector('#canvasTreeTextBody');
      const zoom = document.querySelector('.canonical-viewport .canonical-zoom');
      const tree = document.querySelector('.canonical-layer svg');
      const modeButton = document.querySelector('#exploreBuilderBtn');
      const footerAligned = () => {
        const a = hint.getBoundingClientRect();
        const b = modeButton.getBoundingClientRect();
        return Math.abs((a.top + a.bottom - b.top - b.bottom) / 2) < 1 && a.right <= b.left;
      };
      const selectors = [
        '.canvas-stage', '.canonical-viewport', '.canonical-zoom',
        '#exploreBuilderBtn', '#canvasTreeText', '#tutorSurface',
      ];
      const layout = () => ({
        boxes: selectors.map(selector => document.querySelector(selector).getBoundingClientRect().toJSON()),
        camera: getComputedStyle(tree.parentElement).transform,
      });
      await settle();
      const fitted = tree.getBoundingClientRect();
      const clearsText = fitted.top >= notice.getBoundingClientRect().bottom
        && fitted.bottom <= hint.getBoundingClientRect().top;
      const footerAlignedBefore = footerAligned();
      const saved = [notice, hint, reader].map(el => el.innerHTML);
      zoom.querySelector('button').click();
      const before = layout();
      notice.textContent = 'Long provisional analysis notice. '.repeat(50);
      hint.textContent = 'Long generator hint. '.repeat(50);
      reader.textContent = 'Long textual representation of the tree. '.repeat(100);
      window.dispatchEvent(new Event('resize'));
      await settle();
      const long = layout();
      const scrolls = [notice, reader].every(el => el.scrollHeight > el.clientHeight);
      const clearsZoom = notice.getBoundingClientRect().right <= zoom.getBoundingClientRect().left;
      const footerAlignedAfter = footerAligned();
      notice.hidden = true;
      reader.textContent = 'Short tree.';
      await settle();
      const short = layout();
      notice.hidden = false;
      [notice, hint, reader].forEach((el, i) => { el.innerHTML = saved[i]; });
      return { before, long, short, scrolls, clearsZoom, clearsText, footerAlignedBefore, footerAlignedAfter };
    });
    assert.deepEqual(result.long, result.before, `Long text must not move or reset the canvas at ${width}px`);
    assert.deepEqual(result.short, result.before, `Short or hidden text must not move or reset the canvas at ${width}px`);
    assert.ok(result.scrolls, `Overflow must stay scrollable at ${width}px`);
    assert.ok(result.clearsZoom, `The notice must not overlap the zoom buttons at ${width}px`);
    assert.ok(result.clearsText, `The fitted tree must clear the notice and hint at ${width}px`);
    assert.ok(result.footerAlignedBefore && result.footerAlignedAfter,
      `The mode hint and button must share a centerline without overlapping at ${width}px`);
  }
  console.log('PASS: tree layout stays fixed when notice, hint and reader text change on desktop and mobile.');
} finally {
  await browser.close();
}
