import { linguisticDictionary } from './linguistic-dictionary.js';

// docs/LINGUISTIC_DICTIONARY.md is the single definition source for both
// lesson books. Its generated entries also drive term matching here.
const terms = new Map();
const notation = new Map();
const pluralAliases = (term) => {
  if (/s$/i.test(term)) return [];
  if (/[^aeiou]y$/i.test(term)) return [`${term.slice(0, -1)}ies`];
  if (/(x|z|ch|sh)$/i.test(term)) return [`${term}es`];
  return [`${term}s`];
};
const headwords = new Set(linguisticDictionary.map((entry) => entry.term.toLowerCase()));
for (const source of linguisticDictionary) {
  const entry = { title: source.term, definition: source.definition };
  const aliases = [...(source.aliases || [])];
  for (const plural of pluralAliases(source.term)) {
    if (!headwords.has(plural.toLowerCase()) && !aliases.includes(plural)) aliases.push(plural);
  }
  for (const alias of [source.term, ...aliases]) {
    if (!alias) continue;
    const key = alias.toLowerCase();
    // Uppercase notation such as PASS should match only its written form.
    const exact = /[A-Z]/.test(alias) && !/[a-z]/.test(alias) ? alias : null;
    (exact ? notation : terms).set(exact || key, entry);
  }
}

const escapePattern = value => value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const baseSpellings = [...new Set([...terms.keys(), ...Array.from(notation.keys(), key => key.toLowerCase())])];
const excluded = [
  'a', 'button', 'summary', 'label', 'textarea', 'select', 'svg',
  '.lesson-example-sentence', '.lesson-notation', '.lesson-tree-canvas',
  '.lesson-practice-panel', '.first-tree-builder', '.lesson-assessment',
  '.lesson-sources', '.lesson-pilot-transfer', '[role="status"]',
].join(',');

function customLookup(entries = [], includeFoundations = true) {
  const customTerms = new Map();
  const customNotation = new Map();
  for (const entry of entries) {
    const aliases = Array.isArray(entry.aliases) ? entry.aliases : entry.aliases?.split('|') ?? [];
    for (const alias of [entry.title, ...aliases]) {
      if (!alias) continue;
      const key = alias.toLowerCase();
      // Uppercase notation such as PASS should match only its written form.
      const exact = /[A-Z]/.test(alias) && !/[a-z]/.test(alias) ? alias : null;
      (exact ? customNotation : customTerms).set(exact || key, entry);
    }
  }
  const raw = [...new Set([...customTerms.keys(), ...Array.from(customNotation.keys(), key => key.toLowerCase())])];
  const all = includeFoundations ? [...new Set([...raw, ...baseSpellings])] : raw;
  return {
    customTerms,
    customNotation,
    pattern: all.length
      ? new RegExp(`(?<![\\p{L}\\p{N}_-])(?:${all.sort((a, b) => b.length - a.length).map(escapePattern).join('|')})(?![\\p{L}\\p{N}_-])`, 'giu')
      : /(?!)/gu,
  };
}

function annotate(body, resolve, entries = [], includeFoundations = true) {
  const matches = new WeakMap();
  const seen = new Set();
  const { customTerms, customNotation, pattern } = customLookup(entries, includeFoundations);
  const walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      const parent = node.parentElement;
      return parent?.closest('p, li, dd') && !parent.closest(excluded)
        ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
    },
  });
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    const fragment = document.createDocumentFragment();
    let cursor = 0;
    for (const match of node.textContent.matchAll(pattern)) {
      const [spelling] = match;
      const entry = customNotation.get(spelling) ?? customTerms.get(spelling.toLowerCase())
        ?? (includeFoundations ? notation.get(spelling) ?? terms.get(spelling.toLowerCase()) : undefined);
      if (!entry) continue;
      const trigger = document.createElement('button');
      trigger.type = 'button';
      trigger.className = seen.has(entry)
        ? 'lesson-dictionary-term lesson-dictionary-term-repeat'
        : 'lesson-dictionary-term';
      seen.add(entry);
      trigger.textContent = spelling;
      trigger.setAttribute('aria-label', `Define ${spelling}`);
      trigger.setAttribute('aria-expanded', 'false');
      fragment.append(node.textContent.slice(cursor, match.index), trigger);
      matches.set(trigger, { entry });
      cursor = match.index + spelling.length;
    }
    if (cursor) {
      fragment.append(node.textContent.slice(cursor));
      node.replaceWith(fragment);
    }
  }
  return matches;
}

export function addLessonDictionary(body, {
  resolve, navigate, scrollHost, terms: customTerms = [], includeFoundations = true,
}) {
  const matches = annotate(body, resolve, customTerms, includeFoundations);
  const controller = new AbortController();
  const { signal } = controller;
  const panel = document.createElement('span');
  panel.id = 'lesson-dictionary-definition';
  panel.className = 'lesson-dictionary-panel';
  panel.setAttribute('role', 'region');
  panel.setAttribute('aria-label', 'Dictionary definition');
  const title = document.createElement('strong');
  const definition = document.createElement('span');
  definition.id = 'lesson-dictionary-text';
  panel.append(title, definition);

  let active = null;
  let closeTimer;
  let restoringFocus = false;

  function close() {
    clearTimeout(closeTimer);
    active?.setAttribute('aria-expanded', 'false');
    active?.removeAttribute('aria-controls');
    active?.removeAttribute('aria-describedby');
    panel.remove();
    active = null;
  }

  function locate() {
    if (!active) return;
    const anchor = active.getBoundingClientRect();
    const viewport = scrollHost.getBoundingClientRect();
    const edge = 12;
    if (anchor.bottom < viewport.top || anchor.top > viewport.bottom) {
      close();
      return;
    }
    const topSpace = anchor.top - viewport.top - edge;
    const bottomSpace = viewport.bottom - anchor.bottom - edge;
    panel.style.maxHeight = `${Math.max(64, Math.max(topSpace, bottomSpace))}px`;
    const box = panel.getBoundingClientRect();
    panel.style.left = `${Math.max(viewport.left + edge, Math.min(anchor.left, viewport.right - box.width - edge))}px`;
    const top = box.height + 6 <= bottomSpace || bottomSpace >= topSpace
      ? anchor.bottom + 6 : anchor.top - box.height - 6;
    panel.style.top = `${Math.max(viewport.top + edge, top)}px`;
  }

  function open(trigger) {
    clearTimeout(closeTimer);
    if (active === trigger) return;
    close();
    active = trigger;
    const { entry } = matches.get(trigger);
    title.textContent = entry.title;
    definition.textContent = entry.definition;
    trigger.setAttribute('aria-expanded', 'true');
    trigger.setAttribute('aria-controls', panel.id);
    trigger.setAttribute('aria-describedby', definition.id);
    trigger.after(panel);
    locate();
  }

  function scheduleClose() {
    clearTimeout(closeTimer);
    closeTimer = setTimeout(() => {
      if (!panel.matches(':hover, :focus-within') && !active?.matches(':hover, :focus')) close();
    }, 180);
  }

  body.addEventListener('pointerover', event => {
    if (event.pointerType === 'touch') return;
    if (panel.contains(event.target)) {
      clearTimeout(closeTimer);
    } else if (matches.has(event.target) && !panel.contains(document.activeElement)) {
      open(event.target);
    }
  }, { signal });
  body.addEventListener('pointerout', event => {
    if (event.pointerType !== 'touch' && (event.target === active || panel.contains(event.target))) scheduleClose();
  }, { signal });
  body.addEventListener('focusin', event => {
    if (!restoringFocus && matches.has(event.target)) open(event.target);
  }, { signal });
  body.addEventListener('focusout', event => {
    if (event.target === active || panel.contains(event.target)) scheduleClose();
  }, { signal });
  body.addEventListener('click', event => {
    if (matches.has(event.target)) open(event.target);
  }, { signal });
  document.addEventListener('pointerdown', event => {
    if (active && !active.contains(event.target) && !panel.contains(event.target)) close();
  }, { signal });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || !active || event.defaultPrevented) return;
    const trigger = active;
    const focusInPanel = panel.contains(document.activeElement);
    event.preventDefault();
    close();
    if (focusInPanel) {
      restoringFocus = true;
      trigger.focus({ preventScroll: true });
      restoringFocus = false;
    }
  }, { signal });
  scrollHost.addEventListener('scroll', locate, { signal, passive: true });
  window.addEventListener('resize', locate, { signal });
  return () => {
    controller.abort();
    close();
  };
}
