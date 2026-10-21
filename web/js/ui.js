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

// Tear down everything the Grammar Tutor may have left on the canvas or in
// the explain pane: the overlay message (errors, hints) and the node
// inspector. Used when the workspace switches modes, so a diagnostic from
// the previous mode never survives into the next one.
export function clearDiagnostics() {
  clearOverlay();
  renderNodeDetail(null, null, null);
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

  // Render the inspector's content directly into the explain pane: no inner
  // card wrapper, so the diagnostics/lesson explanation fill the whole panel.
  const head = document.createElement('div');
  head.className = 'nc-head';
  const status = detail.display_status || detail.status;
  const dot = document.createElement('span');
  dot.className = `nc-dot ${status === 'error' ? 'err' : status === 'neutral' || status === 'unlisted' ? 'nt' : 'ok'}`;
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
  box.appendChild(head);

  const chipRow = document.createElement('div');
  chipRow.className = 'nc-chiprow';
  const chip = document.createElement('span');
  chip.className = detail.status === 'error' ? 'nc-chip err' : 'nc-chip';
  chip.textContent = detail.role;
  chipRow.appendChild(chip);
  box.appendChild(chipRow);

  if (status === 'error' && detail.remediation) {
    box.appendChild(renderRemediation(detail.remediation));
  } else {
    const ex = document.createElement('p');
    ex.className = 'ex-text';
    ex.textContent = detail.text;
    box.appendChild(ex);
  }
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

export function renderCorrection(summary) {
  const box = $('#explainNode');
  const emptyState = $('#emptyExplainState');
  if (!box) return false;
  const correction = summary?.correction;
  if (!correction?.corrected_sentence) return false;
  if (emptyState) emptyState.classList.add('hidden');
  box.innerHTML = '';

  const head = document.createElement('div');
  head.className = 'nc-head';
  const dot = document.createElement('span');
  dot.className = 'nc-dot ok';
  const name = document.createElement('span');
  name.className = 'nc-name';
  name.textContent = 'Verified correction';
  head.appendChild(dot);
  head.appendChild(name);
  box.appendChild(head);

  const chipRow = document.createElement('div');
  chipRow.className = 'nc-chiprow';
  const chip = document.createElement('span');
  chip.className = 'nc-chip';
  chip.textContent = 'rule-checked';
  chipRow.appendChild(chip);
  box.appendChild(chipRow);

  label(box, 'Original');
  const original = document.createElement('p');
  original.className = 'ex-text nc-correction-original';
  original.textContent = correction.original_sentence || summary.sentence || '';
  box.appendChild(original);

  label(box, 'Corrected sentence');
  const fixed = document.createElement('p');
  fixed.className = 'ex-text nc-fix nc-correction-fixed';
  fixed.textContent = correction.corrected_sentence;
  box.appendChild(fixed);

  if (Array.isArray(correction.edits) && correction.edits.length) {
    label(box, 'Edits');
    const list = document.createElement('ul');
    list.className = 'nc-correction-edits';
    for (const edit of correction.edits) {
      const item = document.createElement('li');
      const from = edit.original || '(insert)';
      const to = edit.replacement || '(remove)';
      item.textContent = `${from} \u2192 ${to}`;
      list.appendChild(item);
    }
    box.appendChild(list);
  }

  if (summary.explanation) {
    label(box, 'Why');
    const why = document.createElement('p');
    why.className = 'ex-text';
    why.textContent = summary.explanation;
    box.appendChild(why);
  }

  return true;
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