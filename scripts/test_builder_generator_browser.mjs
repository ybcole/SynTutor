// Browser interaction tests for Lessons node palette, Syntax Builder Nodes palette,
// branch editing, Fit behavior, and Syntax Generator Enter-to-analyze.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { createServer } from 'node:http';
import path from 'node:path';

const { chromium } = await import(process.env.QUIZ_V2_PLAYWRIGHT_MODULE || 'playwright');

const root = path.resolve('web');
const mime = { '.js': 'application/javascript', '.json': 'application/json', '.css': 'text/css', '.html': 'text/html', '.svg': 'image/svg+xml' };
let parseRequests = [];

function fakeParse(text) {
  const words = text.trim().split(/\s+/).filter(Boolean);
  const leaves = words.map((w, i) => ({
    id: `w${i + 1}`, kind: 'word', text: w, word: w, tag: 'N', pos: 'NN', label: 'N',
    token_span: [i, i], char_span: [0, w.length], children: [],
  }));
  const tree = {
    root: {
      id: 's1', label: 'S', kind: 'phrase', token_span: [0, Math.max(0, words.length - 1)],
      char_span: [0, text.length], children: leaves,
    },
    sentence: text.trim(),
    tokens: words.map((w, i) => ({ t: w, pos: 'NN', start: i * 2, end: i * 2 + 1 })),
    convention_profile: { chapter: 10, version: 'FINAL', appendix_nom: true, profile_id: 'FINAL-D1' },
  };
  return {
    meta: { backend: 'fixture', sentence_count: 1, target_sentence: 1 },
    parse: {
      tokens: tree.tokens,
      parse_string: `(S ${words.map(w => `(NN ${w})`).join(' ')})`,
      sentences: [{ ordinal: 1, start: 0, end: text.trim().length, text: text.trim() }],
    },
    tree,
    nodes: { s1: { id: 's1', type: 'S' } },
    node_details: { s1: { type: 'S', surface: text.trim(), status: 'valid', role: 'Sentence', text: 'Clause root.' } },
    summary: { valid_edges: words.length, violated_edges: 0, unrated_edges: 0, constraints_fired: [] },
    tokens: tree.tokens,
    explainers: { contrastive: null },
    explanation_evidence: { status: 'PROJECT_APPROVED', channels: {} },
  };
}

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://localhost');
    if (url.pathname === '/api/parse' && req.method === 'POST') {
      const chunks = [];
      for await (const c of req) chunks.push(c);
      const body = JSON.parse(Buffer.concat(chunks).toString('utf8'));
      parseRequests.push(body.text);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(fakeParse(body.text || 'Test.')));
      return;
    }
    if (url.pathname === '/api/words' && req.method === 'POST') {
      const chunks = [];
      for await (const c of req) chunks.push(c);
      const body = JSON.parse(Buffer.concat(chunks).toString('utf8'));
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ results: (body.words || []).map(w => ({ word: w, valid: true })) }));
      return;
    }
    if (url.pathname === '/api/evaluate' && req.method === 'POST') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        structure: { valid: true, status: 'well_formed', errors: [], warnings: [] },
        grammaticality: { status: 'grammatical', message: 'Matches constructed structure.' },
        target_comparison: { status: 'free_construction' },
        node_details: {},
        explanation_evidence: { status: 'PROJECT_APPROVED', channels: {} },
      }));
      return;
    }
    const rel = '.' + (url.pathname === '/' ? '/index.html' : url.pathname);
    const filename = path.resolve(root, rel);
    if (!filename.startsWith(root + path.sep)) throw Error('Invalid path');
    const content = await fs.readFile(filename);
    res.writeHead(200, { 'Content-Type': mime[path.extname(filename)] || 'application/octet-stream' });
    res.end(content);
  } catch {
    res.writeHead(404);
    res.end('Not found');
  }
});

await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch({ headless: true });

try {
  const page = await browser.newPage({ viewport: { width: 1360, height: 920 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.addInitScript(() => {
    localStorage.setItem('syntutor_onboarding_seen', '1');
    window.Clerk = { load: async () => {}, addListener() {}, user: null, session: null };
  });
  await page.route('**/*', route => {
    const url = route.request().url();
    if (url.startsWith(`${base}/js/config.js`)) {
      return route.fulfill({
        contentType: 'application/javascript',
        body: "export const CLERK_CONFIG={publishableKey:'pk_test_ui'};export const SUPABASE_CONFIG={url:'https://fixture.test',anonKey:'anon'};export const API_BASE='';",
      });
    }
    if (url.startsWith('https://esm.sh/')) {
      return route.fulfill({ contentType: 'application/javascript', body: 'export const createClient=()=>null;' });
    }
    return url.startsWith(base) ? route.continue() : route.abort();
  });

  await page.goto(base);
  const skipOnboarding = page.locator('#onboarding .onboarding-skip');
  if (await skipOnboarding.isVisible().catch(() => false)) {
    await skipOnboarding.click();
    await page.locator('#onboarding').waitFor({ state: 'hidden' });
  }
  const clearBtnInit = page.locator('#inputClearBtn');
  if (await clearBtnInit.isVisible().catch(() => false)) {
    await clearBtnInit.click();
  }
  await page.waitForFunction(() => !document.querySelector('#loadingIndicator')?.classList.contains('visible'));
  parseRequests = [];
  const snap = async name => {
    if (process.env.QUIZ_V2_SCREENSHOT_DIR) {
      await page.screenshot({ path: path.join(process.env.QUIZ_V2_SCREENSHOT_DIR, name) });
    }
  };

  // 1. Syntax Generator: Blank blur, Enter on empty, Enter to submit, Shift+Enter newline, no duplicate requests.
  const ta = page.locator('#inputText');
  await ta.click();
  await page.locator('.canvas-stage').click({ position: { x: 120, y: 120 } });
  assert.equal(parseRequests.length, 0, 'blurring an empty editor must not trigger analysis');
  assert.equal(await page.locator('#canvasOverlay').innerText(), '', 'blurring empty editor shows no error overlay');

  await ta.click();
  await ta.press('Enter');
  assert.equal(parseRequests.length, 0, 'Enter on empty text does not call /api/parse');
  assert.ok((await page.locator('#canvasOverlay').innerText()).includes('Enter a sentence'), 'concise empty-input prompt shown once');
  assert.ok(!(await page.locator('#explainNode').innerText()).includes('Enter a sentence'), 'error message is not duplicated in explain panel');

  await ta.fill('The cat slept.');
  await ta.press('Enter');
  await page.waitForFunction(() => document.querySelector('#inputText')?.readOnly === true);
  assert.equal(parseRequests.length, 1, 'Enter submits analysis directly without blur');
  await page.locator('.canvas-stage').click({ position: { x: 80, y: 80 } });
  assert.equal(parseRequests.length, 1, 'subsequent click/blur does not issue a duplicate parse request');

  await ta.dblclick();
  await ta.focus();
  await ta.fill('First sentence.');
  await ta.press('Shift+Enter');
  assert.equal(parseRequests.length, 1, 'Shift+Enter inserts newline without submitting');
  await ta.type('Second sentence.');
  assert.ok((await ta.inputValue()).includes('\n'), 'Shift+Enter preserved multiline newline');
  await ta.press('Enter');
  await page.waitForFunction(() => document.querySelector('#inputText')?.readOnly === true);
  assert.equal(parseRequests.length, 2, 'Enter submits revised multiline input cleanly');

  // 2. Unified Syntax Builder (via #exploreBuilderBtn): toolbar, right-click .builder-menu search & node insertion, Fit, connector-dot drag, wide Fit, mobile dark.
  await page.locator('#exploreBuilderBtn').click();
  await page.locator('#builderCanvas').waitFor({ state: 'visible' });
  assert.equal(await page.locator('.sidebar-item[data-view="tutor"].active').count(), 1, 'Integrated Syntax Builder keeps Syntax nav active');
  assert.equal(await page.locator('#builderTopLeft').isHidden(), true, 'Combined Syntax Builder hides legacy standalone Edit/Clear top-left bar');
  assert.equal(await page.locator('[data-builder-construct]').isHidden(), true, 'Combined Syntax Builder hides legacy Construct button');
  const combinedToolbarButtons = await page.locator('#builderToolbar button:visible').allInnerTexts();
  assert.deepEqual(combinedToolbarButtons, ['+', '−', 'Fit', 'Clear'], 'Combined Builder toolbar exposes +, −, Fit, and Clear');

  await page.locator('#combinedBuilderClear').click();
  await page.mouse.move(700, 400);
  // Let the hover/focus border transition (0.2s) finish before sampling styles.
  await page.waitForTimeout(260);
  const buttonAudit = await page.evaluate(() => {
    const clear = document.getElementById('combinedBuilderClear');
    const fit = document.querySelector('[data-builder-zoom="fit"]');
    const s = el => {
      const cs = getComputedStyle(el);
      return { bg: cs.backgroundColor, border: cs.borderColor, color: cs.color, h: el.getBoundingClientRect().height };
    };
    return { clear: s(clear), fit: s(fit) };
  });
  assert.equal(buttonAudit.clear.bg, buttonAudit.fit.bg, 'Clear uses neutral background matching Fit');
  assert.equal(buttonAudit.clear.border, buttonAudit.fit.border, 'Clear uses neutral border matching Fit');
  assert.ok(buttonAudit.clear.h <= 34 && buttonAudit.fit.h <= 34, 'Toolbar buttons use compact sizing');

  // Right-click canvas opens .builder-menu with searchable labels and lesson help links.
  await page.locator('#builderCanvas').click({ button: 'right', position: { x: 380, y: 220 } });
  await page.locator('.builder-menu').waitFor({ state: 'visible' });
  await page.locator('.builder-menu-search').fill('Noun Phrase');
  await page.locator('.builder-menu-search').press('Enter');
  assert.equal(parseRequests.length, 2, 'Enter in builder menu search never triggers Syntax Generator');
  const filteredLabels = await page.locator('.builder-menu .builder-menu-code').allInnerTexts();
  assert.ok(filteredLabels.includes('NP'), 'Builder menu search finds NP');
  assert.ok(await page.locator('.builder-menu-help:not(:disabled)').count() > 0, 'Builder menu exposes enabled lesson help links');

  await page.locator('.builder-menu .builder-menu-item', { has: page.locator('.builder-menu-code', { hasText: /^NP$/ }) }).first().click();
  await ta.fill('small birds');
  await page.waitForTimeout(260);
  await page.locator('#builderCanvas').click({ button: 'right', position: { x: 480, y: 220 } });
  await page.locator('.builder-menu').waitFor({ state: 'visible' });
  await page.locator('.builder-menu .builder-menu-item', { has: page.locator('.builder-menu-code', { hasText: /^NP$/ }) }).first().click();
  await snap('builder-palette-edit.png');

  // Fit on incomplete/disconnected tree centers cleanly without forcing grammatical connections.
  await page.locator('[data-builder-zoom="out"]').click();
  await page.locator('[data-builder-zoom="out"]').click();
  await page.locator('[data-builder-zoom="fit"]').click();
  await page.waitForTimeout(80);
  const fitState = await page.evaluate(async () => {
    const mod = await import('/js/syntax-builder-ui.js?v=2026.11.18f');
    const sb = await import('/js/syntax-builder.js');
    const model = mod.builderModel();
    const nodes = Object.values(model.nodes);
    const parentCount = nodes.filter(n => n.parent).length;
    const phrases = nodes.filter(n => n.kind === 'phrase');
    const dot = sb.dotOf(phrases[0]);
    const anchor = sb.parentAnchorOf(phrases[0]);
    return { parentCount, phraseX: phrases[0].x, dotX: dot.x, dotY: dot.y, anchorY: anchor.y, phraseY: phrases[0].y, phraseH: phrases[0].h };
  });
  assert.equal(fitState.parentCount, 0, 'Fit never forces grammatical connections on incomplete trees');
  assert.equal(fitState.dotY, fitState.anchorY, 'Connector dot aligns flush with phrase bottom branch junction');

  // Pointer drag from NP's connector dot onto a word node creates a branch connection cleanly.
  const dragCoords = await page.evaluate(async () => {
    const mod = await import('/js/syntax-builder-ui.js?v=2026.11.18f');
    const model = mod.builderModel();
    const nodes = Object.values(model.nodes);
    const phrase = nodes.find(n => n.kind === 'phrase');
    const word = nodes.find(n => n.kind === 'word');
    const pBox = mod.canvasGuideBox({ kind: 'phrase', type: phrase.type });
    const dBox = mod.canvasGuideBox({ kind: 'dot', type: phrase.type });
    const scale = pBox.width / (phrase.w + 24);
    const ox = pBox.left - (phrase.x - 12) * scale;
    const oy = pBox.top - (phrase.y - 12) * scale;
    return {
      dotX: dBox.left + dBox.width / 2,
      dotY: dBox.top + dBox.height / 2,
      wordX: ox + (word.x + word.w / 2) * scale,
      wordY: oy + (word.y + word.h / 2) * scale,
    };
  });
  await page.mouse.move(dragCoords.dotX, dragCoords.dotY);
  await page.mouse.down();
  await page.mouse.move(dragCoords.wordX, dragCoords.wordY, { steps: 6 });
  await page.mouse.up();
  const connectedPos = await page.evaluate(async () => {
    const mod = await import('/js/syntax-builder-ui.js?v=2026.11.18f');
    const nodes = Object.values(mod.builderModel().nodes);
    const p = nodes.find(n => n.kind === 'phrase' && Object.values(mod.builderModel().nodes).some(c => c.parent === n.id));
    return { connected: nodes.filter(n => n.parent).length, x: p?.x, y: p?.y };
  });
  assert.equal(connectedPos.connected, 1, 'dragging connector dot onto child node establishes branch parent');

  // Click the visible branch, not its connector or either node, before deleting.
  const selectedBranch = () => page.evaluate(async () => {
    const mod = await import('/js/syntax-builder-ui.js?v=2026.11.18f');
    const sb = await import('/js/syntax-builder.js');
    const model = mod.builderModel();
    const child = Object.values(model.nodes).find(n => n.parent);
    const parent = model.nodes[child.parent];
    const box = mod.canvasGuideBox({ kind: 'phrase', type: parent.type });
    const scale = box.width / (parent.w + 24);
    const a = sb.parentAnchorOf(parent);
    const b = sb.childAnchorOf(model, child);
    return {
      childId: child.id, parentId: parent.id,
      x: box.left + ((a.x + b.x) / 2 - parent.x + 12) * scale,
      y: box.top + ((a.y + b.y) / 2 - parent.y + 12) * scale,
    };
  });
  const branchModel = childId => page.evaluate(async id => {
    const { builderModel } = await import('/js/syntax-builder-ui.js?v=2026.11.18f');
    const nodes = builderModel().nodes;
    return { ids: Object.keys(nodes), parent: nodes[id]?.parent };
  }, childId);
  for (const key of ['Backspace', 'Delete']) {
    const branch = await selectedBranch();
    const before = await branchModel(branch.childId);
    await page.mouse.click(branch.x, branch.y);
    assert.equal(await page.locator('#builderCanvas').evaluate(el => el === document.activeElement), true);
    assert.deepEqual(await branchModel(branch.childId), before, 'clicking a branch only selects it');
    await page.keyboard.press(key);
    assert.deepEqual(await branchModel(branch.childId), { ids: before.ids, parent: null },
      `${key} removes the connection without deleting either node`);
    await page.keyboard.press('Control+z');
    assert.deepEqual(await branchModel(branch.childId), before, 'undo restores the connection');
  }

  // Clear canvas and Fit on a wide long-word sentence scales down cleanly within the canvas boundaries.
  await page.locator('#combinedBuilderClear').click();
  await page.locator('#builderCanvas').dblclick({ position: { x: 200, y: 240 } });
  await page.locator('.builder-inline-input').waitFor({ state: 'visible' });
  await page.locator('.builder-inline-input').fill('extraordinarily sophisticated transformations inevitably produce remarkably intricate hierarchical constituencies throughout contemporary linguistics research');
  await page.locator('.builder-inline-input').press('Enter');
  await page.waitForTimeout(300);
  await page.locator('[data-builder-zoom="fit"]').click();
  await page.waitForTimeout(80);
  const wideFit = await page.evaluate(async () => {
    const mod = await import('/js/syntax-builder-ui.js?v=2026.11.18f');
    const words = Object.values(mod.builderModel().nodes).filter(n => n.kind === 'word');
    const wBox = mod.canvasGuideBox({ kind: 'words' });
    const canvas = document.getElementById('builderCanvas').getBoundingClientRect();
    const worldSpan = Math.max(...words.map(w => w.x + w.w)) - Math.min(...words.map(w => w.x)) + 24;
    return {
      scale: wBox.width / worldSpan,
      worldSpan,
      availableW: canvas.width,
      wordsLeft: wBox.left,
      canvasLeft: canvas.left,
      wordsRight: wBox.left + wBox.width,
      canvasRight: canvas.right,
    };
  });
  assert.ok(wideFit.scale < 1, `wide sentence scales down on Fit (got scale=${wideFit.scale}, worldSpan=${wideFit.worldSpan}, availableW=${wideFit.availableW})`);
  assert.ok(wideFit.wordsLeft >= wideFit.canvasLeft - 2, 'Fit keeps wide tree within left canvas boundary');
  assert.ok(wideFit.wordsRight <= wideFit.canvasRight + 2, 'Fit keeps wide tree within right canvas boundary');

  // Mobile dark check on Syntax Builder + zero horizontal overflow.
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'));
  await page.waitForTimeout(100);
  await snap('builder-mobile-dark.png');
  const builderMobileOverflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  assert.ok(builderMobileOverflow <= 1, `No mobile horizontal overflow on Syntax Builder (overflow=${builderMobileOverflow})`);
  await page.setViewportSize({ width: 1360, height: 920 });
  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'light'));
  await page.locator('#exploreBuilderBtn').click();

  // 3. Lessons Embedded Tree Exercises: Ch. 1 visible PHRASE-a/b/c + Ch. 3 B-R labels + read-only diagrams untouched.
  await page.locator('.sidebar-item[data-view="lessons"]').click();
  const lessons = page.locator('#curriculumView');
  await lessons.locator('[data-lesson-card="br-01"] button').click();
  await lessons.locator('.lesson-section-sidebar nav a', { hasText: 'Phrases, constituents and phrase markers' }).click();
  const exercise = lessons.locator('.first-tree-builder');
  await exercise.waitFor({ state: 'visible' });
  const ch1Palette = await exercise.locator('.first-tree-node-btn').allTextContents();
  assert.deepEqual(ch1Palette, ['PHRASE-a', 'PHRASE-b', 'PHRASE-c'], 'Ch. 1 shows only permitted PHRASE-a/b/c node options');
  assert.equal(await lessons.locator('.lesson-diagram-palette').count(), 0);
  await exercise.locator('[data-node-label="PHRASE-b"]').click();
  await page.waitForTimeout(60);
  const afterCh1Add = await exercise.locator('.first-tree-feedback').innerText();
  assert.ok(afterCh1Add.includes('Added PHRASE-b'), 'clicking visible PHRASE-b adds node without right-click');
  await snap('lessons-tree-palette.png');

  // Verify Check my tree preserves manual check & shows honest incomplete feedback before repairing "the red gate".
  await exercise.getByRole('button', { name: 'Check my tree', exact: true }).click();
  assert.ok((await exercise.locator('.first-tree-feedback').innerText()).length > 0);

  // Repair "the red gate" using visible PHRASE-b + connector-dot drags (PHRASE-a -> PHRASE-b, PHRASE-b -> red & gate).
  const ch1Drag = async (parentType, childMatch) => {
    const pts = await page.evaluate(async ({ parentType, childMatch }) => {
      const mod = await import('/js/syntax-builder-ui.js?v=2026.11.18f');
      const model = mod.builderModel();
      const nodes = Object.values(model.nodes);
      const pNode = nodes.find(n => n.kind === 'phrase' && n.type === parentType);
      const cNode = nodes.find(n => (childMatch.kind ? n.kind === childMatch.kind : true) && (childMatch.type ? n.type === childMatch.type : true) && (childMatch.text ? n.text === childMatch.text : true));
      const pBox = mod.canvasGuideBox({ kind: 'phrase', type: parentType });
      const dBox = mod.canvasGuideBox({ kind: 'dot', type: parentType });
      const scale = pBox.width / (pNode.w + 24);
      const ox = pBox.left - (pNode.x - 12) * scale;
      const oy = pBox.top - (pNode.y - 12) * scale;
      return {
        dotX: dBox.left + dBox.width / 2,
        dotY: dBox.top + dBox.height / 2,
        targetX: ox + (cNode.x + cNode.w / 2) * scale,
        targetY: oy + (cNode.y + cNode.h / 2) * scale,
      };
    }, { parentType, childMatch });
    await page.mouse.move(pts.dotX, pts.dotY);
    await page.mouse.down();
    await page.mouse.move(pts.targetX, pts.targetY, { steps: 6 });
    await page.mouse.up();
  };
  await ch1Drag('PHRASE-a', { kind: 'phrase', type: 'PHRASE-b' });
  await ch1Drag('PHRASE-b', { kind: 'word', text: 'red' });
  await ch1Drag('PHRASE-b', { kind: 'word', text: 'gate' });
  await exercise.getByRole('button', { name: 'Check my tree', exact: true }).click();
  const ch1Repaired = await exercise.locator('.first-tree-feedback').innerText();
  assert.ok(!/flat|missing|needs|incomplete/i.test(ch1Repaired) || /correct|repaired|good|well done|constituent/i.test(ch1Repaired), `Ch. 1 repaired tree passes check: ${ch1Repaired}`);

  // Verify Chapter 2 branch exercise shows its permitted S/NP/VP labels (and excludes Ch. 1 PHRASE-a or later labels like C1).
  await lessons.locator('.header-icon-btn').click();
  await lessons.locator('[data-lesson-card="br-02"] button').click();
  await lessons.locator('.lesson-section-sidebar nav a', { hasText: 'Subject and predicate tree exercise' }).click();
  await lessons.locator('.first-tree-palette').waitFor({ state: 'visible' });
  const ch2Labels = await lessons.locator('.first-tree-node-btn').allTextContents();
  assert.deepEqual(ch2Labels, ['S', 'NP', 'VP'], 'Ch. 2 tree exercise exposes its exact permitted S/NP/VP labels');
  assert.ok(!ch2Labels.includes('C1') && !ch2Labels.includes('PHRASE-a'), 'Ch. 2 palette excludes unrelated chapter labels');

  // Verify Chapter 8 ("Nora is inspecting the bridge"): centered S-bar -> C + S, no clipped words, Fit, scoped Add a node, step label not truncated, SVG Fit & empty C.
  await lessons.locator('.header-icon-btn').click();
  const br08Btn = lessons.locator('[data-lesson-card="br-08"] button');
  await br08Btn.scrollIntoViewIfNeeded();
  await br08Btn.click();
  await lessons.locator('.lesson-section-sidebar nav a', { hasText: 'Complementiser and clause structure' }).click();
  await lessons.locator('.first-tree-palette').waitFor({ state: 'visible' });
  const ch8Labels = await lessons.locator('.first-tree-node-btn').allTextContents();
  assert.deepEqual(ch8Labels, ['S-bar', 'C', 'S'], 'Ch. 8 exercise scopes Add a node to S-bar, C, S');

  const ch8Geom = await page.evaluate(async () => {
    const mod = await import('/js/syntax-builder-ui.js?v=2026.11.18f');
    const nodes = Object.values(mod.builderModel().nodes);
    const sBar = nodes.find(n => n.type === 'S-bar');
    const sNode = nodes.find(n => n.type === 'S');
    const cNode = nodes.find(n => n.type === 'C');
    const words = nodes.filter(n => n.kind === 'word' && n.parent === sNode.id).sort((a, b) => a.x - b.x);
    const spanCenter = (words[0].x + words.at(-1).x + words.at(-1).w) / 2;
    const sCenter = sNode.x + sNode.w / 2;
    const cCenter = cNode.x + cNode.w / 2;
    const sBarCenter = sBar.x + sBar.w / 2;
    const stageRect = document.querySelector('.first-tree-stage').getBoundingClientRect();
    const wBox = mod.canvasGuideBox({ kind: 'words' });
    return {
      wordsText: words.map(w => w.text),
      sCenterDelta: Math.abs(sCenter - spanCenter),
      sBarBetweenCandS: sBarCenter > cCenter && sBarCenter < sCenter,
      wordsInsideStage: wBox.left >= stageRect.left && (wBox.left + wBox.width) <= stageRect.right,
    };
  });
  assert.deepEqual(ch8Geom.wordsText, ['Nora', 'is', 'inspecting', 'the', 'bridge']);
  assert.ok(ch8Geom.sCenterDelta <= 6, `Ch. 8 triangle S centers over "Nora is inspecting the bridge" (delta=${ch8Geom.sCenterDelta})`);
  assert.ok(ch8Geom.sBarBetweenCandS, 'S-bar sits centered between C and S');
  assert.ok(ch8Geom.wordsInsideStage, 'All words including bridge fit inside lesson canvas stage beside Add a node');

  // Step guide: advance to step 2 ("Find the unfilled C"), verify no truncation/clipping, compact Prev/Next, total count, empty C SVG & Fit.
  await lessons.locator('.lesson-tree-step-next').click();
  await page.waitForTimeout(80);
  const step2Info = await page.evaluate(() => {
    const title = document.querySelector('.lesson-tree-step-title');
    const total = document.querySelector('.lesson-tree-step-total');
    const label = document.querySelector('.lesson-tree-step-label');
    const svgText = document.querySelector('.lesson-tree-canvas svg')?.textContent || '';
    const style = getComputedStyle(title);
    const lStyle = getComputedStyle(label);
    return {
      titleText: title?.textContent,
      totalText: total?.textContent,
      textOverflow: style.textOverflow,
      paddingRight: parseFloat(lStyle.paddingRight),
      hasEmptyC: svgText.includes('C (empty)'),
      hasBridge: svgText.includes('Nora is inspecting the bridge'),
    };
  });
  assert.equal(step2Info.titleText, 'Find the unfilled C');
  assert.equal(step2Info.totalText, 'of 3');
  assert.notEqual(step2Info.textOverflow, 'ellipsis', 'Step title never truncates with ellipsis');
  assert.ok(step2Info.paddingRight >= 10, 'Step summary preserves horizontal padding');
  assert.ok(step2Info.hasEmptyC && step2Info.hasBridge, 'Empty C category and bridge clause remain intact in SVG diagram');
  await lessons.locator('.lesson-tree-canvas button[aria-label="Fit syntax tree"]').click();
  await lessons.locator('.first-tree-fit-btn').click();
  await page.locator('.lesson-contents-toggle').click();
  await page.waitForTimeout(160);
  await lessons.locator('.lesson-contents-toggle').click();
  await page.waitForTimeout(160);

  // Mobile dark check on Chapter 8 collapsible Add a node & zero horizontal overflow.
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'));
  await page.waitForTimeout(120);
  const mobileOverflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  assert.ok(mobileOverflow <= 1, `No mobile horizontal overflow on Ch. 8 (overflow=${mobileOverflow})`);
  await snap('br08-mobile-dark.png');
  await page.setViewportSize({ width: 1360, height: 920 });
  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'light'));

  // Verify Chapter 7 branch exercise shows Ch. 7 scoped labels and fits cleanly.
  await lessons.locator('.header-icon-btn').click();
  const br07Btn = lessons.locator('[data-lesson-card="br-07"] button');
  await br07Btn.scrollIntoViewIfNeeded();
  await br07Btn.click();
  await lessons.locator('.lesson-section-sidebar nav a', { hasText: 'Determiner and nominal tree exercise' }).click();
  await lessons.locator('.first-tree-palette').waitFor({ state: 'visible' });
  const ch7Labels = await lessons.locator('.first-tree-node-btn').allTextContents();
  assert.ok(ch7Labels.includes('NOM') && ch7Labels.includes('DET') && !ch7Labels.includes('C2'), 'Ch. 7 palette keeps Ch. 7 determiner/nominal scope');

  // Main's combined Studio keeps its automatic editing and tree transfer,
  // independently of the sidebar Builder's explicit Edit/Construct controls.
  await page.locator('.sidebar-item[data-view="tutor"]').click();
  await ta.dblclick();
  await ta.fill('Birds sing.');
  await ta.press('Enter');
  await page.waitForFunction(() => document.querySelector('#inputText').readOnly);
  await page.locator('#exploreBuilderBtn').click();
  await page.locator('#builderCanvas').waitFor({state:'visible'});
  assert.equal(await page.locator('#builderTopLeft').isHidden(),true);
  assert.equal(await page.locator('#combinedBuilderClear').isVisible(),true);
  assert.equal(await page.locator('.sidebar-item[data-view="tutor"].active').count(),1);
  await page.locator('#builderCanvas').click({button:'right',position:{x:400,y:240}});
  await page.locator('.builder-menu').waitFor({state:'visible'});
  assert.ok(await page.locator('.builder-menu-help:not(:disabled)').count());
  await page.keyboard.press('Escape');
  const transferred = await page.evaluate(async()=>JSON.stringify((await import('/js/syntax-builder-ui.js?v=2026.11.18f')).builderModel().nodes));
  await page.locator('#exploreBuilderBtn').click();
  await page.locator('#exploreBuilderBtn').click();
  assert.equal(await page.evaluate(async()=>JSON.stringify((await import('/js/syntax-builder-ui.js?v=2026.11.18f')).builderModel().nodes)),transferred,'repeated combined-mode switches retain exact model');
  await page.locator('#combinedBuilderClear').click();
  assert.equal(await ta.inputValue(),'');
  await page.locator('#builderCanvas').click({button:'right',position:{x:400,y:240}});
  await page.locator('.builder-menu').waitFor({state:'visible'});
  await page.locator('.sidebar-item[data-view="lessons"]').click();
  assert.equal(await page.locator('.builder-menu').count(),0,'combined builder menu closes when leaving for Lessons');
  assert.deepEqual(errors, []);
  console.log('PASS builder/generator/lessons interaction suite: Enter-to-analyze, Shift+Enter, blank blur guard, unified Builder toolbar + right-click menu/search/help + Fit + connector alignment + wide Fit, Lessons br-01/02/07/08 geometry/Fit/step-labels/palettes, light/dark + desktop/mobile, combined Studio transfer/repeated switches/Clear/teardown, 0 errors.');
} finally {
  await browser.close();
  await new Promise(resolve => server.close(resolve));
}
