const $ = (sel) => document.querySelector(sel);

const PLAIN_NAME = {
  S: 'Sentence / Clause', NP: 'Noun Phrase', NML: 'Noun Phrase (compound)', NX: 'Noun Phrase',
  VP: 'Verb Phrase', PP: 'Prepositional Phrase', ADJP: 'Adjective Phrase', ADVP: 'Adverb Phrase',
  SBAR: 'Subordinate Clause', SQ: 'Inverted Question Clause', SBARQ: 'Wh-Question Clause',
  SINV: 'Inverted Declarative Clause', FRAG: 'Sentence Fragment', PRT: 'Verb-Particle Phrase',
  INTJ: 'Interjection', ROOT: 'Parse Root', CONJP: 'Conjunction Phrase', UCP: 'Coordination Phrase',
  DT: 'Determiner', NN: 'Singular noun', NNS: 'Plural noun', NNP: 'Proper noun (singular)',
  NNPS: 'Proper noun (plural)', PRP: 'Personal pronoun', PRP$: 'Possessive pronoun',
  WP: 'Wh-pronoun', WP$: 'Possessive wh-pronoun', WDT: 'Wh-determiner', WRB: 'Wh-adverb',
  JJ: 'Adjective', JJR: 'Comparative adjective', JJS: 'Superlative adjective',
  RB: 'Adverb', RBR: 'Comparative adverb', RBS: 'Superlative adverb',
  IN: 'Preposition', TO: 'Infinitive marker', MD: 'Modal auxiliary', AUX: 'Auxiliary verb',
  VB: 'Base verb', VBD: 'Past-tense verb', VBG: 'Present participle verb', VBN: 'Past participle verb',
  VBP: 'Non-third-person present verb', VBZ: 'Third-person singular present verb',
  CC: 'Coordinating conjunction', CD: 'Cardinal number', POS: 'Possessive ending', RP: 'Verb particle',
  '.': 'Sentence-final period', ',': 'Comma', ':': 'Colon', ';': 'Semicolon',
  '?': 'Question mark', '!': 'Exclamation mark',
  '``': 'Opening quotation mark', "''": 'Closing quotation mark',
};

export function plainName(type) {
  return PLAIN_NAME[type] || type;
}

// Semantic findings are classified with *qualitative* confidence labels — the
// backend never emits a numeric probability (there is no trained or
// probabilistic model in the feedback path):
//   * `Direct Rule Match`      — a definitive violation of a deterministic rule;
//   * `Advisory Suggestion`    — a hedged literal-interpretation warning;
//   * `Insufficient Evidence`  — the finding has no rule provenance the UI knows.
const SEM_CONFIDENCE_LABEL = {
  'S-SELECTIONAL': 'Direct Rule Match',
  'S-PREPOSITION': 'Direct Rule Match',
  'S-TENSE-TIME': 'Direct Rule Match',
  'S-COLLOCATION': 'Direct Rule Match',
  'S-PREDICATE-COMPAT': 'Advisory Suggestion',
};
const DEFAULT_CONFIDENCE_LABEL = 'Insufficient Evidence';

export function confidenceLabel(finding) {
  if (finding && typeof finding.confidence_label === 'string' && finding.confidence_label) {
    return finding.confidence_label;
  }
  const key = finding && (finding.constraint || finding.rule);
  return SEM_CONFIDENCE_LABEL[key] || DEFAULT_CONFIDENCE_LABEL;
}

export function log(entry) {
  const panel = $('#logPanel');
  if (!panel) return;
  if (!panel.dataset.autoscrollBound) {
    panel.dataset.autoscrollBound = '1';
    panel.addEventListener('scroll', () => {
      panel.dataset.stickToBottom = panel.scrollHeight - panel.scrollTop - panel.clientHeight < 24 ? '1' : '0';
    });
  }
  const div = document.createElement('div');
  div.className = 'log-entry';
  const time = new Date().toLocaleTimeString('en-GB', { hour12: false });
  const t = document.createElement('span');
  t.className = 'log-time';
  t.textContent = time;
  div.appendChild(t);
  const body = document.createElement('span');
  body.textContent = entry;
  div.appendChild(body);
  panel.appendChild(div);
  if (panel.dataset.stickToBottom !== '0') {
    panel.scrollTop = panel.scrollHeight;
  }
}

export function clearOverlay() {
  const overlay = $('#canvasOverlay');
  if (overlay) overlay.innerHTML = '';
}

export function showCanvasMessage(kind, title, lines) {
  const holder = $('#canvasOverlay');
  if (!holder) return;
  holder.innerHTML = '';
  const card = document.createElement('div');
  card.className = `overlay-card ${kind}`;
  const h = document.createElement('h3');
  h.textContent = title;
  card.appendChild(h);
  for (const line of lines) {
    const d = document.createElement('p');
    d.textContent = line;
    card.appendChild(d);
  }
  holder.appendChild(card);
}

export function renderNodeDetail(_session, detail, node) {
  const box = $('#explainNode');
  const emptyState = $('#emptyExplainState');
  if (!box) return;
  box.innerHTML = '';

  if (!detail || !node) {
    if (emptyState) emptyState.classList.remove('hidden');
    return;
  }

  if (emptyState) emptyState.classList.add('hidden');

  const card = document.createElement('div');
  card.className = 'node-card';

  const head = document.createElement('div');
  head.className = 'nc-head';
  const dot = document.createElement('span');
  dot.className = `nc-dot ${detail.status === 'error' ? 'err' : detail.status === 'unlisted' ? 'un' : 'ok'}`;
  const name = document.createElement('span');
  name.className = 'nc-name';
  name.textContent = plainName(detail.type);
  head.appendChild(dot);
  head.appendChild(name);
  if (detail.surface) {
    const surf = document.createElement('span');
    surf.className = 'nc-surface';
    surf.textContent = ` \u2014 "${detail.surface}"`;
    head.appendChild(surf);
  }
  card.appendChild(head);

  const chipRow = document.createElement('div');
  chipRow.className = 'nc-chiprow';
  const chip = document.createElement('span');
  chip.className = detail.status === 'error' ? 'nc-chip err' : 'nc-chip';
  chip.textContent = detail.role;
  chipRow.appendChild(chip);
  card.appendChild(chipRow);

  const ex = document.createElement('p');
  ex.className = 'ex-text';
  ex.textContent = detail.text;
  card.appendChild(ex);

  if (detail.status === 'error' && detail.remediation) {
    card.appendChild(renderRemediation(detail.remediation));
  }

  box.appendChild(card);
}

function label(body, text) {
  const lab = document.createElement('div');
  lab.className = 'nc-label';
  lab.textContent = text;
  body.appendChild(lab);
}

function renderRemediation(rm) {
  const wrap = document.createElement('div');
  wrap.className = 'nc-rem';

  label(wrap, 'What\u2019s wrong');
  const vb = document.createElement('p');
  vb.className = 'ex-text';
  vb.textContent = rm.violation;
  wrap.appendChild(vb);

  label(wrap, 'How to fix it');
  const fx = document.createElement('p');
  fx.className = 'ex-text nc-fix';
  fx.textContent = rm.suggested_fix || 'Fix the highlighted issue.';
  wrap.appendChild(fx);

  if (rm.alternative_fix) {
    label(wrap, 'Alternative fix');
    const al = document.createElement('p');
    al.className = 'ex-text';
    al.textContent = rm.alternative_fix;
    wrap.appendChild(al);
  }

  return wrap;
}

export function renderDiagnostic(title, lines) {
  const box = $('#explainNode');
  const emptyState = $('#emptyExplainState');
  if (emptyState) emptyState.classList.add('hidden');
  if (!box) return;
  box.innerHTML = '';
  const h = document.createElement('h4');
  h.textContent = title;
  box.appendChild(h);
  for (const line of lines) {
    const p = document.createElement('p');
    p.className = 'ex-text';
    p.textContent = line;
    box.appendChild(p);
  }
}

export function renderSentenceVerdict(markupLines, isError) {
  const box = $('#sentenceVerdict');
  if (!box) return;
  box.innerHTML = '';
  const h = document.createElement('h4');
  h.textContent = 'Sentence verdict';
  box.appendChild(h);
  for (const line of markupLines) {
    const d = document.createElement('p');
    d.textContent = line;
    box.appendChild(d);
  }
  box.dataset.verdict = isError ? 'error' : 'valid';
  box.classList.toggle('is-error', Boolean(isError));
}

function renderSemanticFinding(finding) {
  const advisory = finding.status === 'warning';
  const card = document.createElement('div');
  card.className = `sem-card ${advisory ? 'advisory' : 'error'}`;

  const head = document.createElement('div');
  head.className = 'sem-card-head';

  // Advisory literal-interpretation warnings and definitive semantic errors
  // are labelled and styled differently, and both stay visually distinct from
  // the red syntax-error treatment (--err). The badge shows a *qualitative*
  // confidence label, never a fabricated numeric probability.
  const badge = document.createElement('span');
  badge.className = `sem-badge ${advisory ? 'advisory' : ''}`.trim();
  const label = confidenceLabel(finding);
  badge.textContent = label;
  badge.title = finding.provenance
    ? `Confidence: ${label} · ${finding.provenance}`
    : `Confidence: ${label} (deterministic, non-probabilistic)`;
  head.appendChild(badge);

  const rule = finding.rule || finding.constraint;
  if (rule) {
    const ruleTag = document.createElement('span');
    ruleTag.className = 'sem-rule';
    ruleTag.textContent = rule;
    ruleTag.title = finding.constraint || '';
    head.appendChild(ruleTag);
  }
  card.appendChild(head);

  if (finding.category) {
    const category = document.createElement('p');
    category.className = 'sem-category';
    category.textContent = finding.category;
    card.appendChild(category);
  }

  const text = document.createElement('p');
  text.className = 'sem-card-text';
  text.textContent = finding.text || 'Semantic issue detected.';
  card.appendChild(text);

  if (finding.suggestion) {
    const fix = document.createElement('p');
    fix.className = 'sem-suggestion';
    fix.textContent = finding.suggestion;
    card.appendChild(fix);
  }
  return card;
}

// Render one reading's paraphrase and a structured list of its thematic roles
// (e.g. Agent / Action / Theme / Instrument).
function renderAmbiguityExplanation(box, reading) {
  box.textContent = '';
  if (!reading) return;

  const paraphrase = document.createElement('p');
  paraphrase.className = 'ambiguity-paraphrase';
  paraphrase.textContent = reading.paraphrase || '';
  box.appendChild(paraphrase);

  const roles = reading.thematic_roles;
  if (roles && typeof roles === 'object' && Object.keys(roles).length) {
    const grid = document.createElement('div');
    grid.className = 'thematic-grid';
    for (const [role, value] of Object.entries(roles)) {
      const roleEl = document.createElement('span');
      roleEl.className = 'thematic-role';
      roleEl.textContent = role;
      const valueEl = document.createElement('span');
      valueEl.className = 'thematic-value';
      valueEl.textContent = String(value);
      grid.appendChild(roleEl);
      grid.appendChild(valueEl);
    }
    box.appendChild(grid);
  }
}

// Render the semantic layer (spec R11). Findings are advisory "suggestions";
// when ``semantics.ambiguity.ambiguous`` is true, ``#ambiguityTabs`` holds one
// pill per reading and ``#ambiguityExplanation`` shows the active reading's
// paraphrase and thematic roles. ``onSelectReading`` receives the reading
// *index* so the caller can swap the canvas tree and node explanations.
export function renderSemantics(semantics, { onSelectReading, activeIndex = 0 } = {}) {
  const section = $('#semanticsSection');
  const findingsList = $('#semanticFindingsList');
  const emptyState = $('#emptySemanticsState');
  const unavailableState = $('#semanticsUnavailable');
  const ambiguityBox = $('#ambiguityContainer');
  const tabsBox = $('#ambiguityTabs');
  const explanationBox = $('#ambiguityExplanation');
  const scopeBox = $('#ambiguityScope');
  if (!section) return;

  if (findingsList) findingsList.textContent = '';
  if (tabsBox) tabsBox.textContent = '';
  if (explanationBox) explanationBox.textContent = '';
  if (scopeBox) scopeBox.textContent = '';
  if (ambiguityBox) ambiguityBox.hidden = true;
  if (unavailableState) unavailableState.hidden = true;

  if (!semantics) {
    section.hidden = true;
    return;
  }
  section.hidden = false;

  // A controlled failure of the semantic layer must not look like a clean
  // "no findings" run: show the explicit unavailable notice instead.
  const unavailable = semantics.status === 'unavailable'
    || semantics.available === false;
  if (unavailable) {
    if (emptyState) emptyState.hidden = true;
    if (unavailableState) unavailableState.hidden = false;
    return;
  }

  const findings = Array.isArray(semantics.findings) ? semantics.findings : [];
  if (findingsList) {
    for (const finding of findings) {
      findingsList.appendChild(renderSemanticFinding(finding));
    }
  }
  if (emptyState) emptyState.hidden = findings.length > 0;

  const ambiguity = (semantics.ambiguity
    && typeof semantics.ambiguity === 'object'
    && !Array.isArray(semantics.ambiguity))
    ? semantics.ambiguity
    : null;
  const readings = ambiguity && ambiguity.ambiguous && Array.isArray(ambiguity.readings)
    ? ambiguity.readings
    : [];
  if (!readings.length || !tabsBox || !explanationBox) return;

  if (ambiguityBox) ambiguityBox.hidden = false;
  if (scopeBox) scopeBox.textContent = ambiguity.scope || '';

  const active = Math.min(Math.max(activeIndex, 0), readings.length - 1);
  const pills = [];
  const activate = (index) => {
    pills.forEach((pill, i) => {
      const on = i === index;
      pill.classList.toggle('active', on);
      pill.setAttribute('aria-selected', String(on));
      pill.tabIndex = on ? 0 : -1;
    });
    renderAmbiguityExplanation(explanationBox, readings[index]);
  };

  readings.forEach((reading, index) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'ambiguity-pill';
    btn.setAttribute('role', 'tab');
    btn.textContent = reading.label || `Reading ${index + 1}`;
    btn.addEventListener('click', () => {
      activate(index);
      if (typeof onSelectReading === 'function') onSelectReading(index);
    });
    pills.push(btn);
    tabsBox.appendChild(btn);
  });

  activate(active);
}

export function fillDevPanel(payload) {
  const parseStr = $('#parseString');
  const tokStream = $('#tokenStream');
  if (parseStr) parseStr.textContent = payload.parse.parse_string;
  if (tokStream) {
    tokStream.textContent = payload.parse.tokens
      .map((t, i) => `${i + 1}\t${t.t}\t${t.pos}\t${t.tag}`)
      .join('\n');
  }
}

export function applySentenceSelection(payload) {
  const ta = $('#inputText');
  const sents = payload.parse.sentences || [];
  const idx = (payload.meta.target_sentence || 1) - 1;
  const s = sents[idx];
  if (!ta || !s || ta.readOnly !== true) return;
  const st = ta.scrollTop;
  ta.setSelectionRange(s.start, s.end);
  ta.scrollTop = st;
}

// Map the semantic analysis payload to one of the four documented states.
// Consumed by the Semantics tab dot so the semantic state can never be confused
// with the syntax verdict.
function semanticsStatus(semantics) {
  if (!semantics || semantics.status === 'unavailable' || semantics.available === false) {
    return { state: 'unavailable', label: 'Analysis Unavailable' };
  }
  const findings = Array.isArray(semantics.findings) ? semantics.findings : [];
  const errors = findings.filter((f) => f.status !== 'warning').length;
  const warnings = findings.length - errors;
  if (errors > 0) return { state: 'error', label: 'Issues Found' };
  if (warnings > 0) return { state: 'warn', label: 'Suggestions Available' };
  return { state: 'ok', label: 'No Findings' };
}

// ── Right-panel segmented tabs (Syntax vs. Semantics) ───────────────────────

const RIGHT_PANEL_TABS = {
  syntax: { btn: '#tabSyntaxBtn', view: '#syntaxTabView' },
  semantics: { btn: '#tabSemanticsBtn', view: '#semanticsTabView' },
};

// Switch the right panel between the 'syntax' and 'semantics' views. Sets
// `.active` + `aria-selected` on both buttons and toggles the `hidden`
// attribute between the two tab panels. Unknown names are ignored.
export function setActiveRightPanelTab(tabName) {
  if (!RIGHT_PANEL_TABS[tabName]) return;
  for (const [name, refs] of Object.entries(RIGHT_PANEL_TABS)) {
    const on = name === tabName;
    const btn = $(refs.btn);
    if (btn) {
      btn.classList.toggle('active', on);
      btn.setAttribute('aria-selected', String(on));
    }
    const view = $(refs.view);
    if (view) view.hidden = !on;
  }
}

// Wire the two tab buttons once and normalize the initial state (Syntax
// active). Safe no-op when the panel is absent (e.g. the dependency-free
// DOM-shim audit), so importing ui.js never throws.
export function initRightPanelTabs() {
  const syntaxBtn = $('#tabSyntaxBtn');
  const semanticsBtn = $('#tabSemanticsBtn');
  if (syntaxBtn) syntaxBtn.addEventListener('click', () => setActiveRightPanelTab('syntax'));
  if (semanticsBtn) semanticsBtn.addEventListener('click', () => setActiveRightPanelTab('semantics'));
  setActiveRightPanelTab('syntax');
}

// Paint the tab dots (Syntax validity + semantic status) and the Semantics
// finding count. Called with the payload states after an analysis, and with no
// argument to reset (both dots cleared, count hidden).
export function renderRightPanelTabs({ syntaxValid, semantics } = {}) {
  const syntaxDot = $('#syntaxTabDot');
  const semDot = $('#semanticsTabDot');
  const countBadge = $('#semanticsTabCount');

  if (syntaxDot) {
    syntaxDot.classList.remove('ok', 'warn', 'err');
    if (syntaxValid !== undefined) {
      syntaxDot.classList.add(syntaxValid === false ? 'err' : 'ok');
    }
  }

  const unavailable = !semantics
    || semantics.status === 'unavailable'
    || semantics.available === false;
  const findings = !unavailable && Array.isArray(semantics.findings)
    ? semantics.findings
    : [];
  const ambiguous = !unavailable
    && !!(semantics.ambiguity
      && semantics.ambiguity.ambiguous
      && Array.isArray(semantics.ambiguity.readings)
      && semantics.ambiguity.readings.length);

  if (semDot) {
    semDot.classList.remove('ok', 'warn', 'err');
    if (!unavailable) {
      const { state } = semanticsStatus(semantics);
      if (state === 'ok' || state === 'warn' || state === 'error') {
        semDot.classList.add(state === 'error' ? 'err' : state);
      }
    }
  }

  if (countBadge) {
    const count = unavailable ? 0 : findings.length + (ambiguous ? 1 : 0);
    countBadge.textContent = String(count);
    countBadge.hidden = count === 0;
  }
}