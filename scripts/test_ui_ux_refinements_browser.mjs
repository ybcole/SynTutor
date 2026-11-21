import assert from 'node:assert/strict';

const { chromium } = await import(process.env.QUIZ_V2_PLAYWRIGHT_MODULE || 'playwright');

const BASE_URL = process.env.SYNTUTOR_TEST_URL || 'http://127.0.0.1:8769';

const browser = await chromium.launch({
  headless: true,
  ...(process.env.QUIZ_V2_CHROMIUM_PATH ? { executablePath: process.env.QUIZ_V2_CHROMIUM_PATH } : {}),
});

async function submitSentence(page, sentence) {
  const ta = page.locator('#inputText');
  await ta.click();
  await ta.fill(sentence);
  await page.locator('#inputText').press('Enter');
  await page.waitForFunction((expected) => {
    const el = document.querySelector('#inputText');
    const loading = document.querySelector('#loadingIndicator');
    const host = document.querySelector('#canonicalTreeView');
    return el?.value?.trim() === expected
      && !loading?.classList.contains('visible')
      && host && !host.hidden
      && host.querySelectorAll('svg [data-node-id]').length > 0;
  }, sentence, { timeout: 20000 });
}

async function dismissOnboardingIfOpen(page) {
  const skip = page.locator('.onboarding .onboarding-skip');
  if (await skip.isVisible().catch(() => false)) {
    await skip.click();
    await page.locator('#onboarding').waitFor({ state: 'hidden', timeout: 3000 });
  }
}

try {
  // =========================================================================
  // 1. Tutorial immediate appearance on fresh visit, reload, and non-reopen
  // =========================================================================
  {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    // Prove tutorial appears immediately on boot WITHOUT waiting for /api/parse or a 2s timer.
    let parseSettled = false;
    await page.route('**/api/parse', async (route) => {
      await new Promise((r) => setTimeout(r, 2500));
      parseSettled = true;
      await route.continue().catch(() => {});
    });
    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    const afterDcl = Date.now();
    await page.locator('#onboarding:not([hidden]) .onboarding-card').waitFor({ state: 'visible', timeout: 2500 });
    const deltaAfterDcl = Date.now() - afterDcl;
    assert.equal(parseSettled, false, 'Expected onboarding to display immediately before slow /api/parse settled');
    assert(deltaAfterDcl < 1800, `Expected immediate onboarding after DOM load; took ${deltaAfterDcl}ms`);
    await page.unroute('**/api/parse');
    await new Promise((r) => setTimeout(r, 50));

    const boxDesktop = await page.locator('.onboarding-card').boundingBox();
    assert(boxDesktop && boxDesktop.x >= 0 && boxDesktop.y >= 0
      && boxDesktop.x + boxDesktop.width <= 1440 && boxDesktop.y + boxDesktop.height <= 900,
      `Desktop onboarding card out of bounds: ${JSON.stringify(boxDesktop)}`);

    // Step through and dismiss onboarding
    await page.locator('.onboarding .onboarding-next').click();
    await page.locator('.onboarding .onboarding-skip').click();
    await page.locator('#onboarding').waitFor({ state: 'hidden' });

    // Confirm localStorage does NOT suppress tutorial on reload
    const storedSuppress = await page.evaluate(() => localStorage.getItem('syntutor_onboarding_seen'));
    assert.equal(storedSuppress, null, 'Expected no persistent onboarding suppression key');

    await page.reload({ waitUntil: 'domcontentloaded' });
    const reloadAfterDcl = Date.now();
    await page.locator('#onboarding:not([hidden]) .onboarding-card').waitFor({ state: 'visible', timeout: 3000 });
    assert(Date.now() - reloadAfterDcl < 1800, 'Expected immediate onboarding on reload');
    await dismissOnboardingIfOpen(page);

    // Navigating between Syntax Builder -> Lessons -> Syntax Generator must NOT reopen tutorial
    await page.locator('#exploreBuilderBtn').click();
    await page.waitForFunction(() => document.body.classList.contains('builder-active'));
    assert.equal(await page.locator('#onboarding').isVisible(), false, 'Tutorial must not reopen in Builder');

    await page.locator('.sidebar-item[data-view="lessons"]').click();
    await page.locator('.sq-catalog-grid, .lesson-card').first().waitFor({ state: 'visible', timeout: 8000 }).catch(() => {});
    assert.equal(await page.locator('#onboarding').isVisible(), false, 'Tutorial must not reopen in Lessons');

    await page.locator('#newSessionBtn').click();
    await page.waitForTimeout(150);
    assert.equal(await page.locator('#onboarding').isVisible(), false, 'Tutorial must not reopen on internal return');

    // Mobile tutorial layout check
    await page.setViewportSize({ width: 375, height: 812 });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.locator('#onboarding:not([hidden]) .onboarding-card').waitFor({ state: 'visible', timeout: 2500 });
    const boxMobile = await page.locator('.onboarding-card').boundingBox();
    assert(boxMobile && boxMobile.x >= 0 && boxMobile.y >= 0
      && boxMobile.x + boxMobile.width <= 375 && boxMobile.y + boxMobile.height <= 812,
      `Mobile onboarding card out of bounds: ${JSON.stringify(boxMobile)}`);

    await context.close();
  }

  // =========================================================================
  // 2 & 3. Node deselection (word/phrase/clause, empty canvas, pan safety,
  //        Escape, reset button, independent error highlights) + Lesson return
  // =========================================================================
  {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    let parseCount = 0;
    await page.route('**/api/parse', async (route) => {
      parseCount += 1;
      await route.continue();
    });

    await page.goto(BASE_URL, { waitUntil: 'domcontentloaded' });
    await page.locator('#onboarding:not([hidden]) .onboarding-card').waitFor({ state: 'visible', timeout: 2500 });
    await dismissOnboardingIfOpen(page);

    const badSentence = 'He always brang bad marks home.';
    await submitSentence(page, badSentence);
    const baselineParses = parseCount;

    // Verify error highlight exists cleanly in input & tree
    const errorCountBefore = await page.locator('#canonicalTreeView svg [data-legacy-issue="true"]').count();
    assert(errorCountBefore >= 1, 'Expected verified error node highlight on canonical tree');
    const invalidInputBefore = await page.locator('#inputHighlights .word-invalid').count();
    assert(invalidInputBefore >= 1, 'Expected word-invalid highlight in input highlights');

    // Click flagged word node ("brang")
    const brangWordNode = page.locator('#canonicalTreeView svg g[data-node-id][data-legacy-issue="true"]').last();
    const brangId = await brangWordNode.getAttribute('data-node-id');
    await brangWordNode.click();
    await page.waitForFunction((id) => {
      const el = document.querySelector(`#canonicalTreeView svg g[data-node-id="${id}"]`);
      return el?.dataset.selected === 'true' && el?.getAttribute('aria-pressed') === 'true';
    }, brangId);
    const wordExpText = await page.locator('#explainNode').innerText();
    assert(wordExpText.includes('Show full sentence analysis'), 'Expected reset button while node is selected');

    // Click the SAME word node again -> deselects cleanly!
    await brangWordNode.click();
    await page.waitForFunction(() => document.querySelectorAll('#canonicalTreeView [data-selected="true"]').length === 0);
    assert.equal(await page.locator('.xai-reset-selection-btn').count(), 0, 'Reset button disappears once deselected');
    assert.equal(await page.locator('#canonicalTreeView svg [data-legacy-issue="true"]').count(), errorCountBefore,
      'Error highlights must remain intact after deselecting');

    // Select a phrase node -> switch to clause node (root S) -> pan empty canvas must NOT deselect
    const phraseNode = page.locator('#canonicalTreeView svg g[data-node-id]:has-text("VP"), #canonicalTreeView svg g[data-node-id]:has-text("NP")').first();
    const phraseId = await phraseNode.getAttribute('data-node-id');
    await phraseNode.click();
    await page.waitForFunction((id) => document.querySelector(`#canonicalTreeView svg g[data-node-id="${id}"]`)?.dataset.selected === 'true', phraseId);

    const clauseNode = page.locator('#canonicalTreeView svg g[data-node-id]').first();
    const clauseId = await clauseNode.getAttribute('data-node-id');
    if (clauseId !== phraseId) {
      await clauseNode.click();
      await page.waitForFunction((id) => {
        const all = document.querySelectorAll('#canonicalTreeView [data-selected="true"]');
        return all.length === 1 && all[0].getAttribute('data-node-id') === id;
      }, clauseId);
    }

    // Pan empty area of .canonical-viewport -> must NOT deselect!
    const vpBox = await page.locator('#canonicalTreeView .canonical-viewport').boundingBox();
    assert(vpBox, 'Expected canonical-viewport bounding box');
    await page.mouse.move(vpBox.x + 24, vpBox.y + 80);
    await page.mouse.down();
    await page.mouse.move(vpBox.x + 70, vpBox.y + 110, { steps: 6 });
    await page.mouse.up();
    assert.equal(await page.locator('#canonicalTreeView [data-selected="true"]').count(), 1,
      'Panning/dragging canvas must not deselect the active node');

    // Click empty area of canvas (top-left clear margin inside canonical-viewport) -> deselects!
    await page.mouse.click(vpBox.x + 18, vpBox.y + 60);
    await page.waitForFunction(() => document.querySelectorAll('#canonicalTreeView [data-selected="true"]').length === 0);

    // Select node again, then press Escape -> deselects cleanly while preserving error highlights
    await brangWordNode.click();
    await page.waitForFunction((id) => document.querySelector(`#canonicalTreeView svg g[data-node-id="${id}"]`)?.dataset.selected === 'true', brangId);
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => document.querySelectorAll('#canonicalTreeView [data-selected="true"]').length === 0);
    assert.equal(await page.locator('#canonicalTreeView svg [data-legacy-issue="true"]').count(), errorCountBefore,
      'Error highlights must remain intact after Escape');
    assert.equal(await page.locator('#inputHighlights .word-invalid').count(), invalidInputBefore,
      'Input word-invalid highlights must remain intact after Escape');

    // Lesson navigation preservation: select brang, click related-lesson link, return via app nav AND browser Back
    await brangWordNode.click();
    const lessonLink = page.locator('#explainNode .xai-lesson-link').first();
    await lessonLink.waitFor({ state: 'visible', timeout: 5000 });
    const lessonHref = await lessonLink.getAttribute('href');
    assert(lessonHref?.startsWith('#lesson/'), `Expected #lesson/ href, got ${lessonHref}`);
    await lessonLink.click();
    await page.waitForFunction(() => location.hash.startsWith('#lesson/') && document.body.classList.contains('curriculum-open'));

    // Return via application navigation (Syntax Generator sidebar button) without re-running /api/parse
    await page.locator('#newSessionBtn').click();
    await page.waitForFunction((expected) => {
      return !document.body.classList.contains('curriculum-open')
        && document.querySelector('#inputText')?.value?.trim() === expected
        && !document.querySelector('#canonicalTreeView')?.hidden
        && document.querySelectorAll('#canonicalTreeView svg [data-node-id]').length > 0;
    }, badSentence, { timeout: 10000 });
    assert.equal(parseCount, baselineParses, 'App return from lesson must NOT rerun /api/parse');
    assert(await page.locator('#inputHighlights .word-invalid').count() >= 1, 'Input error highlights lost on return');
    assert((await page.locator('#explainNode').innerText()).includes('brang'), 'Explanation lost on app return');

    // Navigate to lesson a second time, then return via Browser Back
    const linkAgain = page.locator('#explainNode .xai-lesson-link').first();
    await linkAgain.click();
    await page.waitForFunction(() => location.hash.startsWith('#lesson/') && document.body.classList.contains('curriculum-open'));
    await page.goBack();
    await page.waitForFunction((expected) => {
      return !location.hash.startsWith('#lesson/')
        && !document.body.classList.contains('curriculum-open')
        && document.querySelector('#inputText')?.value?.trim() === expected
        && !document.querySelector('#canonicalTreeView')?.hidden;
    }, badSentence, { timeout: 10000 });
    assert.equal(parseCount, baselineParses, 'Browser Back return from lesson must NOT rerun /api/parse');
    assert(await page.locator('#inputHighlights .word-invalid').count() >= 1, 'Error highlights lost on browser Back');

    // Full page reload restores submitted sentence & analysis + shows tutorial immediately without overwriting input
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.locator('#onboarding:not([hidden]) .onboarding-card').waitFor({ state: 'visible', timeout: 2500 });
    await page.waitForFunction((expected) => {
      return document.querySelector('#inputText')?.value?.trim() === expected
        && !document.querySelector('#canonicalTreeView')?.hidden
        && document.querySelectorAll('#canonicalTreeView svg [data-node-id]').length > 0;
    }, badSentence, { timeout: 10000 });
    await dismissOnboardingIfOpen(page);
    assert(await page.locator('#inputHighlights .word-invalid').count() >= 1, 'Error highlights lost after reload restore');

    // Submit a brand-new grammatical sentence -> stale "brang" analysis must NOT remain associated
    const goodSentence = 'The girls read books.';
    await submitSentence(page, goodSentence);
    assert.equal(await page.locator('#canonicalTreeView svg [data-legacy-issue="true"]').count(), 0,
      'Stale error highlights appeared on grammatical sentence');
    assert.equal(await page.locator('#inputHighlights .word-invalid').count(), 0,
      'Stale word-invalid highlight appeared on grammatical sentence');

    // =========================================================================
    // 4. Button sizing consistency (Desktop 1440x900 & Mobile 375x812)
    // =========================================================================
    for (const vp of [{ width: 1440, height: 900 }, { width: 375, height: 812 }]) {
      await page.setViewportSize(vp);
      await page.waitForTimeout(120);

      // Measure Generator toolbar & mode buttons
      const genMetrics = await page.evaluate(() => {
        const readStyle = (el) => {
          if (!el) return null;
          const r = el.getBoundingClientRect();
          const cs = getComputedStyle(el);
          return {
            height: Math.round(r.height),
            width: Math.round(r.width),
            fontSize: cs.fontSize,
            fontWeight: cs.fontWeight,
            paddingTop: cs.paddingTop,
            paddingBottom: cs.paddingBottom,
            borderRadius: cs.borderRadius,
            clipped: el.scrollWidth > el.clientWidth + 1,
          };
        };
        return {
          zoomIn: readStyle(document.querySelector('#canonicalTreeView .canonical-zoom button:first-child')),
          zoomFit: readStyle(document.querySelector('#canonicalTreeView .canonical-zoom button:last-child')),
          modeBtn: readStyle(document.querySelector('#exploreBuilderBtn')),
          overflow: document.documentElement.scrollWidth > window.innerWidth,
        };
      });
      assert.equal(genMetrics.overflow, false, `Horizontal overflow in Generator at ${vp.width}x${vp.height}`);
      assert(genMetrics.zoomFit && !genMetrics.zoomFit.clipped, 'Generator Fit button clipped');
      assert(genMetrics.modeBtn && !genMetrics.modeBtn.clipped, 'Generator exploreBuilderBtn clipped');

      // Switch to Syntax Builder and compare equivalent controls
      await page.locator('#exploreBuilderBtn').click();
      await page.waitForFunction(() => document.body.classList.contains('builder-active'));
      await page.waitForTimeout(120);

      const bldMetrics = await page.evaluate(() => {
        const readStyle = (el) => {
          if (!el) return null;
          const r = el.getBoundingClientRect();
          const cs = getComputedStyle(el);
          return {
            height: Math.round(r.height),
            width: Math.round(r.width),
            fontSize: cs.fontSize,
            fontWeight: cs.fontWeight,
            paddingTop: cs.paddingTop,
            paddingBottom: cs.paddingBottom,
            borderRadius: cs.borderRadius,
            clipped: el.scrollWidth > el.clientWidth + 1,
          };
        };
        const modeBtn = document.querySelector('#exploreBuilderBtn');
        const clearBtn = document.querySelector('#combinedBuilderClear');
        const hint = document.querySelector('#builderHint');
        const modeRect = modeBtn?.getBoundingClientRect();
        const hintRect = hint && !hint.hidden ? hint.getBoundingClientRect() : null;
        const overlapsHintMode = Boolean(hintRect && modeRect && hintRect.height > 0
          && !(hintRect.right <= modeRect.left || hintRect.left >= modeRect.right
               || hintRect.bottom <= modeRect.top || hintRect.top >= modeRect.bottom));
        return {
          zoomIn: readStyle(document.querySelector('#builderToolbar.canonical-zoom [data-builder-zoom="in"]')),
          zoomFit: readStyle(document.querySelector('#builderToolbar.canonical-zoom [data-builder-zoom="fit"]')),
          clearBtn: readStyle(clearBtn),
          modeBtn: readStyle(modeBtn),
          overlapsHintMode,
          overflow: document.documentElement.scrollWidth > window.innerWidth,
        };
      });
      assert.equal(bldMetrics.overflow, false, `Horizontal overflow in Builder at ${vp.width}x${vp.height}`);
      assert.equal(bldMetrics.overlapsHintMode, false, `Builder hint & mode button overlap at ${vp.width}x${vp.height}`);
      assert(!bldMetrics.zoomFit?.clipped && !bldMetrics.clearBtn?.clipped && !bldMetrics.modeBtn?.clipped,
        `Clipped Builder button at ${vp.width}x${vp.height}`);

      // Equivalent zoom & toolbar controls must match identically across Generator and Builder
      assert.equal(genMetrics.zoomIn.height, bldMetrics.zoomIn.height, `Zoom + height mismatch at ${vp.width}`);
      assert.equal(genMetrics.zoomIn.width, bldMetrics.zoomIn.width, `Zoom + width mismatch at ${vp.width}`);
      assert.equal(genMetrics.zoomFit.height, bldMetrics.zoomFit.height,
        `Zoom Fit height mismatch at ${vp.width}: gen=${genMetrics.zoomFit.height}, bld=${bldMetrics.zoomFit.height}`);
      assert.equal(genMetrics.zoomFit.fontSize, bldMetrics.zoomFit.fontSize, 'Zoom Fit fontSize mismatch');
      assert.equal(genMetrics.zoomFit.fontWeight, bldMetrics.zoomFit.fontWeight, 'Zoom Fit fontWeight mismatch');
      assert.equal(genMetrics.zoomFit.borderRadius, bldMetrics.zoomFit.borderRadius, 'Zoom Fit borderRadius mismatch');
      assert.equal(genMetrics.zoomFit.paddingTop, bldMetrics.zoomFit.paddingTop, 'Zoom Fit paddingTop mismatch');

      // Toolbar/mode controls keep uniform dimensions across Generator and Builder
      assert.equal(genMetrics.modeBtn.height, bldMetrics.modeBtn.height, `Mode button height mismatch at ${vp.width}`);
      assert.equal(bldMetrics.modeBtn.height, bldMetrics.clearBtn.height,
        `Builder mode button vs Clear button height mismatch at ${vp.width}: ${bldMetrics.modeBtn.height} vs ${bldMetrics.clearBtn.height}`);
      assert.equal(bldMetrics.modeBtn.borderRadius, bldMetrics.clearBtn.borderRadius, 'Border radius mismatch');

      if (vp.width <= 760) {
        assert(bldMetrics.zoomFit.height >= 40, `Mobile touch target too small for zoom Fit: ${bldMetrics.zoomFit.height}`);
        assert(bldMetrics.clearBtn.height >= 40, `Mobile touch target too small for Clear btn: ${bldMetrics.clearBtn.height}`);
        assert(bldMetrics.modeBtn.height >= 40, `Mobile touch target too small for Mode btn: ${bldMetrics.modeBtn.height}`);
      }

      // Return to Generator for next viewport check
      await page.locator('#exploreBuilderBtn').click();
      await page.waitForFunction(() => !document.body.classList.contains('builder-active'));
    }

    await context.close();
  }

  console.log('PASS: UI/UX refinements (node deselection, lesson/reload state preservation, immediate tutorial, and button consistency at desktop + mobile).');
} finally {
  await browser.close();
}
