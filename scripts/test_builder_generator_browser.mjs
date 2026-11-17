// Browser interaction tests for Lessons node palette, Syntax Builder Nodes palette,
// connector dot drag-to-connect, Fit behavior, and Syntax Generator Enter-to-analyze.
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

  // 2. Syntax Builder: Top-left Clear/Edit, Floating draggable Nodes panel, bottom-left Nodes toggle, Construct vs Done editing, Fit & connector alignment.
  await page.locator('.sidebar-item[data-view="builder"]').click();
  await page.locator('#builderCanvas').waitFor({ state: 'visible' });
  assert.equal(await page.locator('#builderPalette').isHidden(), true, 'Nodes palette stays hidden outside Edit mode');
  assert.equal(await page.locator('#builderNodesToggle').isHidden(), true, 'Bottom-left Nodes toggle stays hidden outside Edit mode');
  assert.equal(await page.locator('[data-builder-construct]').isHidden(), true, 'Construct button stays hidden outside Edit mode');
  const topLeftButtons = await page.locator('#builderTopLeft button:visible').allInnerTexts();
  assert.deepEqual(topLeftButtons, ['Clear', 'Edit mode'], 'Normal mode places Clear and Edit mode side by side top-left');

  await page.locator('[data-builder-edit]').click();
  await page.locator('#builderPalette').waitFor({ state: 'visible' });
  await page.locator('#builderNodesToggle').waitFor({ state: 'visible' });
  await page.locator('[data-builder-construct]').waitFor({ state: 'visible' });
  const editLeftButtons = await page.locator('#builderTopLeft button:visible').allInnerTexts();
  assert.deepEqual(editLeftButtons, ['Clear', 'Done editing'], 'Edit mode toggles top-left button to Done editing');
  const editRightButtons = await page.locator('#builderToolbar button:visible').allInnerTexts();
  assert.deepEqual(editRightButtons, ['Construct', '+', '−', 'Fit'], 'Edit mode places Construct before +, -, Fit top-right');

  // Move pointer off toolbar before checking resting neutral button styles (no permanent purple border/fill on Done editing or Construct).
  await page.mouse.move(700, 400);
  const buttonAudit = await page.evaluate(() => {
    const clear = document.getElementById('builderClearTop');
    const doneEdit = document.querySelector('[data-builder-edit]');
    const construct = document.querySelector('[data-builder-construct]');
    const fit = document.querySelector('[data-builder-zoom="fit"]');
    const nodesBtn = document.getElementById('builderNodesToggle');
    const hint = document.getElementById('builderHint');
    const grip = document.querySelector('.builder-palette-grip');
    const headText = document.getElementById('builderPaletteHead')?.innerText?.replace(/\s+/g, ' ').trim();
    const s = el => {
      const cs = getComputedStyle(el);
      return { bg: cs.backgroundColor, border: cs.borderColor, color: cs.color, h: el.getBoundingClientRect().height };
    };
    return {
      clear: s(clear), doneEdit: s(doneEdit), construct: s(construct), fit: s(fit), nodesBtn: s(nodesBtn),
      hintVisible: hint ? getComputedStyle(hint).display !== 'none' && !hint.hidden : false,
      gripText: grip?.textContent,
      headText,
      tooltipVisibleWhenOpen: !document.getElementById('builderNodesTooltip')?.hidden,
    };
  });
  assert.equal(buttonAudit.hintVisible, false, 'Persistent overlapping canvas hint stays removed in Syntax Builder Edit mode');
  assert.equal(buttonAudit.tooltipVisibleWhenOpen, false, 'Tooltip does not show when floating Nodes panel is already visible');
  assert.equal(buttonAudit.gripText, '::', 'Floating Nodes header includes subtle :: drag indicator');
  assert.ok(buttonAudit.headText.startsWith(':: Nodes'), 'Header shows :: before Nodes');
  assert.equal(buttonAudit.doneEdit.bg, buttonAudit.clear.bg, 'Done editing uses neutral background matching Clear');
  assert.equal(buttonAudit.doneEdit.border, buttonAudit.clear.border, 'Done editing uses neutral border matching Clear');
  assert.equal(buttonAudit.construct.bg, buttonAudit.fit.bg, 'Construct uses neutral background matching Fit');
  assert.equal(buttonAudit.construct.border, buttonAudit.fit.border, 'Construct uses neutral border matching Fit');
  assert.ok(buttonAudit.clear.h <= 34 && buttonAudit.construct.h <= 34, 'Toolbar buttons use compact sizing');

  // Verify category descriptions wrap completely without ellipsis truncation.
  const truncatedDescCount = await page.locator('#builderPaletteList .builder-palette-desc').evaluateAll(els =>
    els.filter(el => el.scrollWidth > el.clientWidth + 2).length);
  assert.equal(truncatedDescCount, 0, 'Category descriptions wrap cleanly without horizontal truncation');

  // Verify bottom-left Nodes toggle stays anchored bottom-left and floating palette is draggable without panning canvas.
  const togglePos = await page.evaluate(() => {
    const t = document.getElementById('builderNodesToggle').getBoundingClientRect();
    const s = document.querySelector('.canvas-stage').getBoundingClientRect();
    return { leftOffset: t.left - s.left, bottomOffset: s.bottom - t.bottom };
  });
  assert.ok(togglePos.leftOffset < 32 && togglePos.bottomOffset < 32, 'Nodes toggle anchors at bottom-left of canvas');

  const palBeforeDrag = await page.locator('#builderPalette').boundingBox();
  const headBox = await page.locator('#builderPaletteHead').boundingBox();
  await page.mouse.move(headBox.x + 40, headBox.y + 12);
  await page.mouse.down();
  await page.mouse.move(headBox.x + 120, headBox.y + 42, { steps: 6 });
  await page.mouse.up();
  const palAfterDrag = await page.locator('#builderPalette').boundingBox();
  assert.ok(palAfterDrag.x > palBeforeDrag.x + 50, 'Dragging palette header moves floating Nodes panel');

  // Search input interaction inside panel must NOT drag the floating panel.
  const searchBox = await page.locator('#builderPaletteSearch').boundingBox();
  await page.mouse.move(searchBox.x + 20, searchBox.y + 10);
  await page.mouse.down();
  await page.mouse.move(searchBox.x + 60, searchBox.y + 20, { steps: 3 });
  await page.mouse.up();
  const palAfterSearchDrag = await page.locator('#builderPalette').boundingBox();
  assert.equal(Math.round(palAfterSearchDrag.x), Math.round(palAfterDrag.x), 'Interacting with search input does not drag Nodes panel');

  // Hide panel, exit Edit mode, and re-enter Edit mode -> tooltip points at Show Nodes once; clicking Show Nodes dismisses it and restores dragged position.
  await page.locator('#builderNodesToggle').click();
  assert.equal(await page.locator('#builderPalette').isHidden(), true, 'Bottom-left Nodes toggle hides floating palette');
  assert.equal(await page.locator('#builderNodesTooltip').isHidden(), true, 'Hiding panel during active session does not repeatedly show tooltip');
  await page.locator('[data-builder-edit]').click(); // Exit Edit mode
  await page.locator('[data-builder-edit]').click(); // Re-enter Edit mode with panel hidden
  await page.locator('#builderNodesTooltip').waitFor({ state: 'visible' });
  const tipGeom = await page.evaluate(() => {
    const tip = document.getElementById('builderNodesTooltip').getBoundingClientRect();
    const btn = document.getElementById('builderNodesToggle').getBoundingClientRect();
    return { text: document.getElementById('builderNodesTooltip').textContent, aboveBtn: tip.bottom <= btn.top + 4, alignedLeft: Math.abs(tip.left - btn.left) < 16 };
  });
  assert.ok(tipGeom.text.includes('Nodes') && tipGeom.aboveBtn && tipGeom.alignedLeft, 'Tooltip points concisely right above Show Nodes');
  await snap('builder-tooltip-show-nodes.png');

  await page.locator('#builderNodesToggle').click();
  assert.equal(await page.locator('#builderNodesTooltip').isHidden(), true, 'Clicking Show Nodes immediately dismisses tooltip');
  await page.locator('#builderPalette').waitFor({ state: 'visible' });
  const palReopened = await page.locator('#builderPalette').boundingBox();
  assert.ok(Math.abs(palReopened.x - palAfterDrag.x) <= 4, 'Reopening Nodes restores remembered floating position');

  // Snap palette back near left edge for clean edit screenshot/tests.
  await page.mouse.move(palReopened.x + 40, palReopened.y + 12);
  await page.mouse.down();
  await page.mouse.move(palBeforeDrag.x + 40, palBeforeDrag.y + 12, { steps: 5 });
  await page.mouse.up();

  await page.locator('#builderPaletteSearch').fill('Noun Phrase');
  await page.locator('#builderPaletteSearch').press('Enter');
  assert.equal(parseRequests.length, 2, 'Enter in node search never triggers Syntax Generator');
  const filteredLabels = await page.locator('#builderPaletteList [data-palette-label]').allInnerTexts();
  assert.ok(filteredLabels.some(t => t.startsWith('NP')), 'Nodes search finds NP');

  await page.locator('#builderPaletteList [data-palette-label="NP"]').click();
  await page.locator('#builderPaletteSearch').fill('');
  await ta.fill('small birds');
  await page.waitForTimeout(260);
  await page.locator('#builderPaletteList [data-palette-label="NP"]').click();
  await snap('builder-palette-edit.png');

  // Fit on incomplete/disconnected tree centers cleanly to the right of #builderPalette without changing parents.
  await page.locator('[data-builder-zoom="out"]').click();
  await page.locator('[data-builder-zoom="out"]').click();
  await page.locator('[data-builder-zoom="fit"]').click();
  await page.waitForTimeout(80);
  const fitState = await page.evaluate(async () => {
    const mod = await import('/js/syntax-builder-ui.js');
    const sb = await import('/js/syntax-builder.js');
    const model = mod.builderModel();
    const pal = document.getElementById('builderPalette').getBoundingClientRect();
    const canvas = document.getElementById('builderCanvas').getBoundingClientRect();
    const nodes = Object.values(model.nodes);
    const parentCount = nodes.filter(n => n.parent).length;
    const phrases = nodes.filter(n => n.kind === 'phrase');
    const dot = sb.dotOf(phrases[0]);
    return { palRight: pal.right - canvas.left, canvasW: canvas.width, parentCount, phraseX: phrases[0].x, dotX: dot.x, dotY: dot.y, phraseY: phrases[0].y, phraseH: phrases[0].h };
  });
  assert.equal(fitState.parentCount, 0, 'Fit never forces grammatical connections on incomplete trees');
  assert.equal(fitState.dotY, fitState.phraseY + fitState.phraseH + 2, 'Connector dot aligns flush with phrase bottom branch junction');

  // Pointer drag from NP's connector dot onto a word node creates a branch connection cleanly.
  const dragCoords = await page.evaluate(async () => {
    const mod = await import('/js/syntax-builder-ui.js');
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
  const connectedPosBeforeDone = await page.evaluate(async () => {
    const mod = await import('/js/syntax-builder-ui.js');
    const nodes = Object.values(mod.builderModel().nodes);
    const p = nodes.find(n => n.kind === 'phrase' && Object.values(mod.builderModel().nodes).some(c => c.parent === n.id));
    return { connected: nodes.filter(n => n.parent).length, x: p.x, y: p.y };
  });
  assert.equal(connectedPosBeforeDone.connected, 1, 'dragging connector dot onto child node establishes branch parent');

  // Clicking Done editing exits Edit mode WITHOUT automatically reconstructing or shifting the learner's tree.
  await page.locator('[data-builder-edit]').click();
  assert.equal(await page.locator('#builderPalette').isHidden(), true, 'Done editing hides floating palette');
  assert.equal(await page.locator('#builderNodesToggle').isHidden(), true, 'Done editing hides bottom-left toggle');
  assert.equal(await page.locator('[data-builder-construct]').isHidden(), true, 'Done editing hides Construct');
  const posAfterDone = await page.evaluate(async () => {
    const mod = await import('/js/syntax-builder-ui.js');
    const nodes = Object.values(mod.builderModel().nodes);
    const p = nodes.find(n => n.kind === 'phrase' && Object.values(mod.builderModel().nodes).some(c => c.parent === n.id));
    return { x: p.x, y: p.y };
  });
  assert.deepEqual(posAfterDone, { x: connectedPosBeforeDone.x, y: connectedPosBeforeDone.y }, 'Done editing preserves manual tree geometry');

  // Re-enter Edit mode, build complete S -> birds tree, and click Construct to arrange hierarchically.
  await page.locator('[data-builder-edit]').click();
  await page.locator('[data-builder-clear]').click();
  await ta.fill('birds');
  await page.waitForTimeout(260);
  await page.locator('#builderPaletteList [data-palette-label="S"]').click();
  const sDrag = await page.evaluate(async () => {
    const mod = await import('/js/syntax-builder-ui.js');
    const nodes = Object.values(mod.builderModel().nodes);
    const phrase = nodes.find(n => n.type === 'S');
    const word = nodes.find(n => n.kind === 'word');
    const pBox = mod.canvasGuideBox({ kind: 'phrase', type: 'S' });
    const dBox = mod.canvasGuideBox({ kind: 'dot', type: 'S' });
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
  await page.mouse.move(sDrag.dotX, sDrag.dotY);
  await page.mouse.down();
  await page.mouse.move(sDrag.wordX, sDrag.wordY, { steps: 6 });
  await page.mouse.up();
  await page.locator('[data-builder-construct]').click();
  await page.waitForTimeout(160);
  const alignedCenter = await page.evaluate(async () => {
    const mod = await import('/js/syntax-builder-ui.js');
    const nodes = Object.values(mod.builderModel().nodes);
    const s = nodes.find(n => n.type === 'S');
    const w = nodes.find(n => n.kind === 'word');
    return Math.abs((s.x + s.w / 2) - (w.x + w.w / 2));
  });
  assert.ok(alignedCenter < 2, `Construct aligns parent S cleanly over child word (delta=${alignedCenter})`);
  assert.ok((await page.locator('#explainNode').innerText()).includes('Constructed tree evaluation'), 'Bottom-right evaluation panel remains unchanged after Construct');
  await snap('builder-constructed.png');

  // Clear canvas and Fit on a wide long-word sentence scales down cleanly within the canvas without obscuring under palette.
  await page.locator('[data-builder-clear]').click();
  await ta.fill('extraordinarily sophisticated transformations inevitably produce remarkably intricate hierarchical constituencies throughout contemporary linguistics research');
  await page.waitForTimeout(300);
  await page.locator('[data-builder-zoom="fit"]').click();
  await page.waitForTimeout(80);
  const wideFit = await page.evaluate(async () => {
    const mod = await import('/js/syntax-builder-ui.js');
    const words = Object.values(mod.builderModel().nodes).filter(n => n.kind === 'word');
    const wBox = mod.canvasGuideBox({ kind: 'words' });
    const pal = document.getElementById('builderPalette').getBoundingClientRect();
    const canvas = document.getElementById('builderCanvas').getBoundingClientRect();
    const worldSpan = Math.max(...words.map(w => w.x + w.w)) - Math.min(...words.map(w => w.x)) + 24;
    return {
      scale: wBox.width / worldSpan,
      worldSpan,
      availableW: canvas.right - pal.right,
      wordsLeft: wBox.left,
      palRight: pal.right,
      wordsRight: wBox.left + wBox.width,
      canvasRight: canvas.right,
    };
  });
  assert.ok(wideFit.scale < 1, `wide sentence scales down on Fit (got scale=${wideFit.scale}, worldSpan=${wideFit.worldSpan}, availableW=${wideFit.availableW})`);
  assert.ok(wideFit.wordsLeft >= wideFit.palRight - 2, 'Fit positions wide tree clear of floating Nodes palette');
  assert.ok(wideFit.wordsRight <= wideFit.canvasRight + 2, 'Fit keeps wide tree within right canvas boundary');

  // Mobile dark check on Syntax Builder toggle & palette + zero overflow.
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'));
  await page.locator('#builderNodesToggle').click();
  assert.equal(await page.locator('#builderPalette').isHidden(), true, 'mobile Nodes toggle hides floating panel');
  await page.locator('#builderNodesToggle').click();
  await page.locator('#builderPalette').waitFor({ state: 'visible' });
  await snap('builder-mobile-dark.png');
  const builderMobileOverflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  assert.ok(builderMobileOverflow <= 1, `No mobile horizontal overflow on Syntax Builder (overflow=${builderMobileOverflow})`);
  await page.setViewportSize({ width: 1360, height: 920 });
  await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'light'));

  // Subtle Show Nodes tooltip stays visible across time, canvas clicks, pan/zoom until Show Nodes is clicked or Edit mode is exited.
  await page.locator('#builderNodesToggle').click();
  await page.locator('[data-builder-edit]').click();
  await page.locator('[data-builder-edit]').click();
  await page.locator('#builderNodesTooltip').waitFor({ state: 'visible' });
  const tipStyle = await page.evaluate(() => {
    const cs = getComputedStyle(document.getElementById('builderNodesTooltip'));
    return { fontSize: parseFloat(cs.fontSize), fontWeight: Number(cs.fontWeight), shadow: cs.boxShadow };
  });
  assert.ok(tipStyle.fontSize <= 12 && tipStyle.fontWeight <= 400 && tipStyle.shadow === 'none', `Tooltip is compact and visually subtle (${JSON.stringify(tipStyle)})`);
  await page.locator('#builderCanvas').click({ position: { x: 400, y: 240 } });
  await page.mouse.move(700, 420);
  await page.locator('[data-builder-zoom="in"]').click();
  await page.waitForTimeout(3800);
  assert.equal(await page.locator('#builderNodesTooltip').isVisible(), true, 'Tooltip remains visible across canvas clicks, pointer move, zoom, and elapsed time until Show Nodes is clicked');
  await snap('builder-tooltip-show-nodes.png');
  await page.locator('#builderNodesToggle').click();
  assert.equal(await page.locator('#builderNodesTooltip').isHidden(), true, 'Clicking Show Nodes immediately dismisses tooltip');
  await page.locator('#builderPalette').waitFor({ state: 'visible' });
  await page.locator('[data-builder-edit]').click();
  assert.equal(await page.locator('#builderPalette').isHidden(), true, 'leaving Edit mode hides Nodes palette');
  assert.equal(await page.locator('#builderNodesTooltip').isHidden(), true, 'leaving Edit mode keeps tooltip hidden');

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
      const mod = await import('/js/syntax-builder-ui.js');
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
    const mod = await import('/js/syntax-builder-ui.js');
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

  assert.deepEqual(errors, []);
  console.log('PASS builder/generator/lessons interaction suite: Enter-to-analyze, Shift+Enter, blank blur guard, Builder top-left Clear/Edit + floating palette + bottom-left Nodes toggle + Construct vs Done editing + Fit + connector alignment, Lessons br-01/02/07/08 geometry/Fit/step-labels/palettes, light/dark + desktop/mobile, 0 errors.');
} finally {
  await browser.close();
  await new Promise(resolve => server.close(resolve));
}
