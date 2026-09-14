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
  panel.prepend(div);
}

export function clearOverlay() {
  $('#canvasOverlay').innerHTML = '';
}

export function showCanvasMessage(kind, title, lines) {
  const holder = $('#canvasOverlay');
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

/* ---------------- primary panel: node explanation ---------------- */

export function renderNodeDetail(_session, detail, node) {
  const box = $('#explainNode');
  box.innerHTML = '';
  if (!detail || !node) {
    return;
  }

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
    surf.textContent = `\u2014 "${detail.surface}"`;
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

/* ---------------- secondary (collapsible) dev panel ---------------- */

export function renderSentenceVerdict(markupLines, isError) {
  const box = $('#sentenceVerdict');
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

export function fillDevPanel(payload) {
  $('#parseString').textContent = payload.parse.parse_string;
  $('#tokenStream').textContent = payload.parse.tokens
    .map((t, i) => `${i + 1}\t${t.t}\t${t.pos}\t${t.tag}`)
    .join('\n');
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
