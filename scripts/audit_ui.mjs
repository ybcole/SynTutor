// SynTutor UI regression audit (semantic panel + ambiguity view).
//
// Runs js/ui.js under a tiny hand-written DOM shim so the deterministic
// rendering contract of the semantic panel is checked without a browser or any
// dependency (no jsdom/Playwright).  It guards the behaviour the backend audit
// cannot see:
//   * semantic findings carry *qualitative* confidence labels and never a
//     fabricated numeric probability;
//   * an advisory (status 'warning') finding is visibly distinct from a
//     definitive semantic error;
//   * a controlled semantic failure ('unavailable') is NEVER rendered as the
//     ordinary "no findings" state;
//   * the right-panel tab dots stay independent: the Syntax dot reflects rule
//     validity while the Semantics dot reflects the semantic state;
//   * R11.5 ambiguity pills render, state the two-reading scope, and dispatch
//     the selection callback.
//
// Exit code is non-zero if any check fails (CI-safe).  Run with:
//     node scripts/audit_ui.mjs        (or: npm run audit:ui)

import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

// ── minimal DOM shim ────────────────────────────────────────────────────────

class ClassList {
  constructor(el) { this.el = el; this.set = new Set(); }
  add(...cs) { cs.forEach((c) => this.set.add(c)); this._sync(); }
  remove(...cs) { cs.forEach((c) => this.set.delete(c)); this._sync(); }
  toggle(c, force) {
    const on = force === undefined ? !this.set.has(c) : force;
    on ? this.set.add(c) : this.set.delete(c);
    this._sync();
    return on;
  }
  contains(c) { return this.set.has(c); }
  _sync() { this.el._className = [...this.set].join(' '); }
}

class El {
  constructor(tag) {
    this.tag = tag;
    this.children = [];
    this.attributes = {};
    this.dataset = {};
    this._text = '';
    this.hidden = false;
    this.classList = new ClassList(this);
    this._className = '';
    this._listeners = {};
  }
  set className(v) {
    this._className = String(v);
    this.classList.set = new Set(String(v).split(/\s+/).filter(Boolean));
  }
  get className() { return this._className; }
  set textContent(v) { this._text = String(v); this.children = []; }
  get textContent() {
    return this._text + this.children.map((c) => c.textContent).join('');
  }
  appendChild(c) { this.children.push(c); return c; }
  setAttribute(k, v) { this.attributes[k] = String(v); }
  addEventListener(ev, fn) { (this._listeners[ev] = this._listeners[ev] || []).push(fn); }
  click() { (this._listeners.click || []).forEach((fn) => fn()); }
}

const IDS = [
  'semanticsSection', 'semanticFindingsList', 'emptySemanticsState',
  'semanticsUnavailable', 'ambiguityContainer', 'ambiguityTabs',
  'ambiguityExplanation', 'ambiguityScope',
  'syntaxTabDot', 'semanticsTabDot', 'semanticsTabCount',
];
const byId = {};
IDS.forEach((id) => { byId[`#${id}`] = new El('div'); });
globalThis.document = {
  querySelector: (sel) => byId[sel] || null,
  createElement: (t) => new El(t),
};

// ── load the module under test ──────────────────────────────────────────────

const here = dirname(fileURLToPath(import.meta.url));
const { renderSemantics, renderRightPanelTabs, confidenceLabel } =
  await import(`file://${join(here, '..', 'js', 'ui.js')}`);

let failures = 0;
const check = (label, cond) => {
  if (cond) { console.log(`  ok  : ${label}`); } else { failures += 1; console.log(`  FAIL: ${label}`); }
};

// 1. completed, no findings -> empty state (NOT the unavailable notice).
renderSemantics({ status: 'ok', available: true, findings: [], ambiguity: { ambiguous: false, readings: [] } });
check('section visible', byId['#semanticsSection'].hidden === false);
check('empty state shown', byId['#emptySemanticsState'].hidden === false);
check('unavailable notice hidden', byId['#semanticsUnavailable'].hidden === true);
check('no finding cards', byId['#semanticFindingsList'].children.length === 0);

// 2. definitive error vs advisory warning are visually distinct, and both use
//    *qualitative* confidence labels (never a fabricated numeric probability).
renderSemantics({
  status: 'ok', available: true,
  findings: [
    { rule: 'R11.4', constraint: 'S-SELECTIONAL', status: 'error', category: 'selectional restriction', text: 'x', suggestion: 'y', confidence_label: 'Direct Rule Match', provenance: 'deterministic rule R11.4 (S-SELECTIONAL)' },
    { rule: 'R11.6', constraint: 'S-PREDICATE-COMPAT', status: 'warning', category: 'subject-predicate compatibility', text: 'Anomalous under a literal interpretation: ...', suggestion: 'consider a figurative reading', confidence_label: 'Advisory Suggestion', provenance: 'deterministic rule R11.6 (S-PREDICATE-COMPAT)' },
  ],
  ambiguity: { ambiguous: false, readings: [] },
});
const cards = byId['#semanticFindingsList'].children;
const badgeText = (card) => card.children[0].children[0].textContent;
check('two cards rendered', cards.length === 2);
check('error card not advisory', !cards[0].classList.contains('advisory'));
check('advisory card marked advisory', cards[1].classList.contains('advisory'));
check('error badge is the Direct Rule Match label', badgeText(cards[0]) === 'Direct Rule Match');
check('advisory badge is the Advisory Suggestion label', badgeText(cards[1]) === 'Advisory Suggestion');
check('no fabricated numeric confidence in any card',
  !/\b\d\.\d\d\b/.test(cards[0].textContent + cards[1].textContent));
check('empty hidden with findings', byId['#emptySemanticsState'].hidden === true);

// 2b. qualitative label contract (incl. the Insufficient Evidence fallback).
check('confidenceLabel maps a known constraint',
  confidenceLabel({ constraint: 'S-TENSE-TIME' }) === 'Direct Rule Match');
check('confidenceLabel falls back to Insufficient Evidence',
  confidenceLabel({ constraint: 'S-UNKNOWN' }) === 'Insufficient Evidence');
check('confidenceLabel prefers the backend label',
  confidenceLabel({ constraint: 'S-SELECTIONAL', confidence_label: 'Advisory Suggestion' }) === 'Advisory Suggestion');

// 3. controlled failure -> explicit unavailable notice, never "no findings".
renderSemantics({ status: 'unavailable', available: false, findings: [], ambiguity: null });
check('unavailable notice shown', byId['#semanticsUnavailable'].hidden === false);
check('empty state hidden on failure', byId['#emptySemanticsState'].hidden === true);
check('no cards on failure', byId['#semanticFindingsList'].children.length === 0);

// 4. null payload hides the panel.
renderSemantics(null, {});
check('null hides section', byId['#semanticsSection'].hidden === true);

// 5. R11.5 ambiguity pills render, state the two-reading scope, and dispatch
//    selection.
const selected = [];
renderSemantics({
  status: 'ok', available: true, findings: [],
  ambiguity: {
    ambiguous: true,
    scope: 'Two primary readings are compared — this is not an exhaustive list.',
    readings: [
      { label: 'Verb-phrase reading — instrument / accompaniment', paraphrase: 'One candidate reading: P1', thematic_roles: { Agent: 'the boy' } },
      { label: 'Noun-phrase reading — possession / attribute', paraphrase: 'Another candidate reading: P2', thematic_roles: { Agent: 'the boy' } },
    ],
  },
}, { onSelectReading: (i) => selected.push(i) });
const pills = byId['#ambiguityTabs'].children;
check('ambiguity block visible', byId['#ambiguityContainer'].hidden === false);
check('two reading pills', pills.length === 2);
check('ambiguity scope note rendered',
  byId['#ambiguityScope'].textContent.toLowerCase().includes('two'));
check('first pill active', pills[0].classList.contains('active'));
pills[1].click();
check('pill click dispatches index 1', selected.length === 1 && selected[0] === 1);
check('second pill active after click', pills[1].classList.contains('active') && !pills[0].classList.contains('active'));

// 6. The right-panel tab dots are independent (syntax validity vs. semantic
//    state) and the Semantics badge counts findings + ambiguity.
renderRightPanelTabs({ syntaxValid: true, semantics: { status: 'ok', available: true, findings: [], ambiguity: { ambiguous: false } } });
check('syntax dot ok', byId['#syntaxTabDot'].classList.contains('ok'));
check('semantics dot ok', byId['#semanticsTabDot'].classList.contains('ok'));
check('no count badge when clean', byId['#semanticsTabCount'].hidden === true);

renderRightPanelTabs({ syntaxValid: false, semantics: { status: 'ok', available: true, findings: [
  { rule: 'R11.6', constraint: 'S-PREDICATE-COMPAT', status: 'warning', confidence_label: 'Advisory Suggestion', text: 'x', suggestion: 'y' },
], ambiguity: { ambiguous: false } } });
check('syntax dot err on invalid', byId['#syntaxTabDot'].classList.contains('err'));
check('semantics dot warn on advisory', byId['#semanticsTabDot'].classList.contains('warn'));
check('count badge shows 1', byId['#semanticsTabCount'].hidden === false && byId['#semanticsTabCount'].textContent === '1');

renderRightPanelTabs({ syntaxValid: true, semantics: { status: 'ok', available: true, findings: [
  { rule: 'R11.4', constraint: 'S-SELECTIONAL', status: 'error', confidence_label: 'Direct Rule Match', text: 'x', suggestion: 'y' },
], ambiguity: { ambiguous: false } } });
check('semantics dot err on definitive finding', byId['#semanticsTabDot'].classList.contains('err'));

renderRightPanelTabs({ syntaxValid: true, semantics: { status: 'unavailable', available: false, findings: [] } });
check('syntax dot stays ok while semantics unavailable', byId['#syntaxTabDot'].classList.contains('ok'));
check('semantics dot neutral on unavailable', !byId['#semanticsTabDot'].classList.contains('ok')
  && !byId['#semanticsTabDot'].classList.contains('warn')
  && !byId['#semanticsTabDot'].classList.contains('err'));

renderRightPanelTabs();
check('reset clears the status dots and count', !byId['#syntaxTabDot'].classList.contains('ok')
  && !byId['#syntaxTabDot'].classList.contains('err')
  && byId['#semanticsTabCount'].hidden === true);

console.log(failures === 0 ? '\nUI AUDIT: ALL CHECKS PASSED' : `\nUI AUDIT: ${failures} CHECK(S) FAILED`);
process.exit(failures === 0 ? 0 : 1);
