import { showCurriculumState } from './curriculum-state.js';
import { STAGES, STAGE_TITLES, validateCourse, lessonKey, emptyProgress, canAdvance, lessonXp } from './lesson-core.js';
import { createLessonStore } from './lesson-progress.js';
import { createFoundationStore } from './foundation-progress.js';
import { renderFoundationCheck } from './foundation-check.js';
import { constituentsPilot } from './constituents-pilot.js';
import { functionsPilot } from './functions-pilot.js';
import { categoriesPilot } from './categories-pilot.js';
import { basicVpPilot } from './basic-vp-pilot.js';
import { adverbialsPilot } from './adverbials-pilot.js';
import { requestEvidence, renderEvidence } from './explanation-evidence.js';
import { subscribeAuthState } from './auth.js';
import { enableCanvasView } from './canvas-view.js';
import { addConstituentReview, addConstituentTeaching, constituentHeadings, constituentOpeningCheck, constituentReferences } from './constituents-lesson.js';
import { addSubjectPredicateTeaching, subjectPredicateHeadings, subjectPredicateOpeningCheck, subjectPredicateReferences } from './subject-predicate-lesson.js';
import { phraseStructureArticles } from './phrase-structure-lessons.js';
import { displayVpLevel, lessonNotation } from './lesson-notation.js';
import { addLessonKeyTerms } from './lesson-key-terms.js';

const articleLessons = {
  'br-01': {
    headings: constituentHeadings,
    openingCheck: constituentOpeningCheck,
    teach: addConstituentTeaching,
    review: addConstituentReview,
    references: constituentReferences,
    postTestIntro: 'Use what you learned about groups, brackets, and branches. Check each answer before continuing.',
  },
  'br-02': {
    headings: subjectPredicateHeadings,
    openingCheck: subjectPredicateOpeningCheck,
    teach: addSubjectPredicateTeaching,
    references: subjectPredicateReferences,
    postTestIntro: 'Use the NP and VP branches to identify the subject and predicate. Check each answer before continuing.',
  },
  ...phraseStructureArticles,
};

let options = {}, course, store, foundations, host, active = null, step = 0, track = 'foundations', busy = false, notice = '', generation = 0, lastFocus = null;
let reviewStage = null;
let articlePage = 0, practiceResponses = null, assessmentIndex = 0;
const legacyArticleSections = [
  { id: 'introduction', advances: 'predict' },
  { id: 'concepts', advances: 'understand' },
  { id: 'worked-example' },
  { id: 'application' },
  { id: 'recap', advances: 'worked', references: true },
  { id: 'closing-check', assessment: true },
];
const pilotArticles = { 'br-01': constituentsPilot, 'br-02': functionsPilot, 'br-03': categoriesPilot, 'br-04': basicVpPilot, 'br-05': adverbialsPilot };
const pilotId = () => {
  if (!['localhost', '127.0.0.1', '[::1]'].includes(location.hostname)) return null;
  const id = new URLSearchParams(location.search).get('preview');
  return Object.hasOwn(pilotArticles, id) ? id : null;
};
const lessonUserId = () => pilotId() ? 'guest' : options.userId?.() || 'guest';
const readingScope = () => pilotId() ? `preview-${pilotId()}` : lessonUserId();
const legacyLessonLinks = { NP: 'br-07', ADJP: 'br-03', VP: 'br-04', S: 'br-02', SBAR: 'br-08', SBARQ: 'br-09' };
const postTestKeys = ['guided', 'transfer', 'exit'];
const lessonCanvases = new Map();
let embeddedBuilderCleanup = null;
const el = (tag, text, cls) => { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (cls) node.className = cls; return node; };
function button(text, run, cls = '') { const b = el('button',text,cls); b.type = 'button'; b.addEventListener('click',run); return b; }
function lessonReferences(lesson) {
  const blocks = [lesson, ...lesson.teaching, ...lesson.cambridge_insights, lesson.worked_example,
    ...lesson.worked_example.steps, lesson.predict, lesson.guided, lesson.transfer, lesson.exit,
    ...(lesson.revised_assessment?.opening ?? []), ...(lesson.revised_assessment?.closing ?? [])];
  const ids = new Set(blocks.flatMap(block => block.source_ids || []));
  const details = el('details', undefined, 'lesson-sources');
  details.append(el('summary', 'References and source review'));
  const list = el('ul');
  const sources = course.sources.filter(source => ids.has(source.id));
  if (sources.some(source => source.book === 'B-R')) {
    details.append(el('p', 'Book reference for the cited syntax trees and conventions: Noel Burton-Roberts, Analysing Sentences.'));
  }
  for (const source of sources) {
    list.append(el('li', `${source.title} · ${source.edition} · Chapter ${source.chapter} · printed p. ${source.printed_page}`));
  }
  for (const reference of articleFor(lesson)?.references || []) list.append(el('li', reference));
  details.append(list, el('p', lesson.lesson_id === pilotId()
    ? 'AI source check complete. Pilot acceptance is pending.'
    : 'AI checked the cited pages. The lesson has no human instructor sign-off.'));
  return details;
}
const SVG_NS = 'http://www.w3.org/2000/svg';
function svgNode(name, attrs = {}) { const n = document.createElementNS(SVG_NS,name); for (const [k,v] of Object.entries(attrs)) n.setAttribute(k,v); return n; }
// Read-only canonical trees plus a constrained fill-in target for guided practice.
// Advanced structures never pass through the parser or the legacy Builder bridge.
export function renderLessonTree(envelope, {
  focusId = null, blank = null, stackFeatures = false, displayLabels = null,
  interactive = false, onSelectNode = null, zoomControls = false, wordBaseline = 0,
  textDisclosure = true, highlightWords = false, tracePath = false,
} = {}) {
  const wrap = el('div',undefined,'lesson-tree-wrap');
  const root = envelope.root;
  const hint = el('p', textDisclosure
    ? 'Scroll sideways to inspect the whole tree, or open its text view.'
    : 'Scroll sideways to inspect the whole tree.', 'lesson-tree-hint');
  wrap.append(hint);wrap.tabIndex=0;wrap.setAttribute('aria-label','Scrollable syntax tree');
  function label(node, withFeatures = true) {
    const master = displayLabels?.[node.id];
    if (master) return withFeatures ? master.join(' ') : master[0] || '';
    if (node.gap) return node.index === undefined ? '•' : `• (${node.index})`;
    const numberedVP = displayVpLevel(node);
    const name=node.label === 'AUX' ? '' : node.label === 'S-bar' ? 'S′' : node.label === 'S-dbar' ? 'S″' : node.unlabelled ? '' : numberedVP || node.label || node.word;
    return `${name || ''}${withFeatures && node.features?.length ? ` [${node.features.join(', ')}]` : ''}${node.empty ? ' (empty)' : ''}`;
  }
  const blankFor = node => blank?.node_id && blank.node_id === node.id ? blank.field : null;
  const featureRows = node => {
    const stacked = displayLabels?.[node.id] || stackFeatures;
    if (blankFor(node) === 'feature') return stacked ? ['[?]'] : [];
    if (blankFor(node) === 'label') return [];
    return displayLabels?.[node.id]
      ? displayLabels[node.id].slice(1)
      : stackFeatures ? (node.features || []).map(feature => `[${feature}]`) : [];
  };
  function visibleLabel(node) {
    if (blankFor(node) === 'label') return '?';
    if (blankFor(node) === 'feature') {
      const name = label(node, false);
      return featureRows(node).length ? name : [name, '[?]'].filter(Boolean).join(' ');
    }
    return label(node, !stackFeatures && !displayLabels);
  }
  const measure = document.createElement('canvas').getContext('2d');
  measure.font = '15px system-ui, sans-serif';
  const gap = 18;
  const rowHeight = 72;
  const top = 35;
  const widths = new Map();
  function widthOf(node) {
    if (widths.has(node)) return widths.get(node);
    const children = node.children || [];
    const width = Math.max(node.id === focusId ? 122 : 56,
      measure.measureText(visibleLabel(node)).width + 28,
      ...featureRows(node).map(feature => measure.measureText(feature).width + 28),
      measure.measureText(node.words?.join(' ') || '').width + 28,
      children.reduce((total, child) => total + widthOf(child), 0)
        + Math.max(0, children.length - 1) * gap);
    widths.set(node, width);
    return width;
  }
  const positions = [], edges = [];
  function place(node, left, y) {
    const width=widthOf(node), position={node,x:left+width/2,y}; positions.push(position);
    const children = node.children || [];
    const childWidth = children.reduce((sum, child) => sum + widthOf(child), 0)
      + Math.max(0, children.length - 1) * gap;
    let cursor = left + (width - childWidth) / 2;
    for (const child of children) {
      const target = place(child, cursor, y + rowHeight + featureRows(node).length * 18);
      edges.push([position, target]);
      cursor += widthOf(child) + gap;
    }
    return position;
  }
  const width=widthOf(root); place(root,0,top);
  if (wordBaseline) {
    for (const position of positions) {
      if (position.node.word) position.y = Math.max(position.y, top + wordBaseline * rowHeight);
    }
  }
  const height=Math.max(...positions.map(p=>p.y + featureRows(p.node).length * 18 + (p.node.triangle ? 80 : 35)));
  const role = !textDisclosure && typeof onSelectNode === 'function' ? 'group' : 'img';
  const svg=svgNode('svg',{viewBox:`0 0 ${width} ${height}`,width,height,role,'aria-label':`Syntax tree for ${envelope.sentence}`});
  const branches = new Map();
  const parents = new Map();
  for (const [a,b] of edges) {
    const line = svgNode('line',{x1:a.x,y1:a.y+12+featureRows(a.node).length*18,x2:b.x,y2:b.y-18,class:'lesson-branch'});
    if (tracePath) branches.set(b.node.id, line);
    if (tracePath || b.node.gap) parents.set(b.node.id, a.node);
    svg.append(line);
  }
  function highlightPath(id) {
    if (!tracePath) return;
    for (const line of branches.values()) line.classList.remove('lesson-branch-traced');
    while (branches.has(id)) {
      branches.get(id).classList.add('lesson-branch-traced');
      id = parents.get(id)?.id;
    }
  }
  const wordLabels = new Map();
  function highlightCoveredWords(nodeId) {
    const covered = new Set();
    function collect(node) {
      covered.add(node);
      for (const child of node.children || []) collect(child);
    }
    const selected = positions.find(({ node }) => node.id === nodeId);
    if (selected) collect(selected.node);
    for (const [node, label] of wordLabels) {
      label.classList.toggle('lesson-word-traced', covered.has(node));
    }
  }
  for (const {node,x,y} of positions) {
    const g=svgNode('g',{'data-node-id':node.id || '',class:node.id===focusId ? 'lesson-tree-focus' : ''});
    if (node.id === focusId || (highlightWords && node.id && onSelectNode)) {
      g.append(svgNode('rect', {
        class: 'lesson-tree-focus-box', x: x - 55, y: y - 20,
        width: 110, height: highlightWords ? 30 : 40, rx: 9,
      }));
    }
    const t=svgNode('text',{x,y,'text-anchor':'middle'});
    t.textContent=visibleLabel(node);g.append(t);
    if (highlightWords && node.word) wordLabels.set(node, t);
    const rows = featureRows(node);
    rows.forEach((feature, index) => {
      const row = svgNode('text', {x, y: y + (index + 1) * 18, 'text-anchor': 'middle', class: 'br-feature-row'});
      row.textContent = feature;
      g.append(row);
    });
    if (node.triangle) {
      const half=Math.min(widthOf(node)/2-12,80);
      const bottom = y + rows.length * 18;
      g.append(svgNode('polygon',{points:`${x},${bottom+12} ${x-half},${bottom+45} ${x+half},${bottom+45}`}));
      const words=svgNode('text',{x,y:bottom+68,'text-anchor':'middle'});words.textContent=node.words.join(' ');g.append(words);
      if (highlightWords) wordLabels.set(node, words);
    }
    if (typeof onSelectNode === 'function' && node.id) {
      g.setAttribute('role','button');
      g.setAttribute('tabindex','0');
      g.setAttribute('aria-pressed', String(node.id === focusId));
      const parentLabel = parents.get(node.id)?.label;
      g.setAttribute('aria-label', node.gap && parentLabel ? `Inspect gap under ${parentLabel}`
        : 'Inspect ' + (node.label || 'tree position')
          + ' for ' + (node.word || node.words?.join(' ') || node.label || 'this position'));
      const choose = (feature = null) => {
        svg.querySelector('g[aria-pressed=true]')?.setAttribute('aria-pressed', 'false');
        g.setAttribute('aria-pressed', 'true');
        if (highlightWords) highlightCoveredWords(node.id);
        highlightPath(node.id);
        onSelectNode(node.id, feature);
      };
      g.addEventListener('click', () => choose());
      g.addEventListener('keydown', event => {
        if (event.target !== g) return;
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); choose(); }
      });
      for (const row of g.querySelectorAll('.br-feature-row')) {
        row.setAttribute('role','button');
        row.setAttribute('tabindex','0');
        row.dataset.featureLabel = row.textContent;
        row.setAttribute('aria-label','Inspect feature ' + row.textContent
          + ' for ' + (node.word || node.label));
        const featureName=()=>{const text=row.textContent.trim();return text.startsWith('[') && text.endsWith(']') ? text.slice(1,-1) : text;};
        row.addEventListener('click', event => {
          event.stopPropagation(); choose(featureName());
        });
        row.addEventListener('keydown', event => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.stopPropagation(); event.preventDefault();
            choose(featureName());
          }
        });
      }
    }
    svg.append(g);
  }
  if (highlightWords) highlightCoveredWords(focusId);
  highlightPath(focusId);
  if (zoomControls) {
    const toolbar=el('div',undefined,'xai7-tree-zoom');
    toolbar.dataset.xai7Zoom = '';
    toolbar.setAttribute('role','group');
    toolbar.setAttribute('aria-label','Zoom the syntax tree');
    let zoom=1;
    const originalWidth=svg.getAttribute('width');
    const originalHeight=svg.getAttribute('height');
    const status=el('span','100%');
    status.setAttribute('aria-live','polite');
    const apply=()=>{
      // Reset must restore exact B-R geometry, not a rounded approximation.
      svg.setAttribute('width',zoom===1?originalWidth:String(Math.round(width*zoom)));
      svg.setAttribute('height',zoom===1?originalHeight:String(Math.round(height*zoom)));
      status.textContent=Math.round(zoom*100)+'%';
    };
    toolbar.append(button('Zoom out',()=>{
      zoom=Math.max(.7,Math.round((zoom-.2)*10)/10);apply();
    }),button('Zoom in',()=>{
      zoom=Math.min(1.8,Math.round((zoom+.2)*10)/10);apply();
    }),button('Reset zoom',()=>{zoom=1;apply();}),status);
    wrap.append(toolbar);
  }
  wrap.append(svg);
  const text = textDisclosure
    ? el('details', undefined, 'lesson-tree-text')
    : el('div', undefined, 'lesson-tree-outline');
  if (textDisclosure) {
    text.append(el('summary', 'Read the tree as text'));
  } else {
    text.setAttribute('role', 'group');
    text.setAttribute('aria-label', 'Tree structure');
  }
  function list(node) {
    const item = el('li');
    const name = blankFor(node) ? [visibleLabel(node), ...featureRows(node)].filter(Boolean).join(' ')
      : label(node) || '△';
    const description = node.words ? `${name} — ${node.words.join(' ')}` : name;
    if (textDisclosure && interactive && node.id) {
      const button = el('button', description);
      button.type = 'button';
      button.dataset.nodeId = node.id;
      if (typeof onSelectNode === 'function') button.addEventListener('click', () => onSelectNode(node.id, null));
      item.append(button);
    } else {
      item.textContent = description;
    }
    if (node.children) {
      const nested = el('ul');
      node.children.forEach(child => nested.append(list(child)));
      item.append(nested);
    }
    return item;
  }
  const ul=el('ul');ul.append(list(root));text.append(ul);wrap.append(text);return wrap;
}
function articleFor(lesson) {
  return (lesson.revised_assessment && pilotArticles[lesson.lesson_id]) || articleLessons[lesson.lesson_id];
}
function articleSections(article) {
  return article.sections ?? article.headings.map((title, index) => ({ ...legacyArticleSections[index], title }));
}
function sectionRoute(lesson, section) {
  return `#lesson/${lesson.lesson_id}/${section.id}`;
}
function readLessonRoute() {
  const match = /^#lesson\/([a-z0-9-]+)(?:\/([a-z0-9-]+))?$/i.exec(location.hash);
  if (!match) return null;
  const [, id, section] = match;
  return { id: id === 'catalog' ? null : legacyLessonLinks[id] || id.toLowerCase(), section };
}
function updateLessonRoute(hash, replace = false) {
  if (location.hash === hash) return;
  if (replace) history.replaceState(history.state, '', hash);
  else history.pushState(null, '', hash);
}
function readingKey(lesson) {
  return `syntutor:lesson-reading:v1:${readingScope()}:${lessonKey(lesson)}`;
}
function readingState(lesson) {
  try {
    const saved = JSON.parse(localStorage.getItem(readingKey(lesson)));
    if (Array.isArray(saved?.visited)) return saved;
  } catch { /* Reading navigation works without device storage. */ }
  return { visited: [], last: null };
}
function rememberSection(lesson, section) {
  const state = readingState(lesson);
  state.last = section.id;
  if (!state.visited.includes(section.id)) state.visited.push(section.id);
  try { localStorage.setItem(readingKey(lesson), JSON.stringify(state)); }
  catch { /* The section remains in the current URL. */ }
}
function articlePageFor(lesson, progress, sections, requested, workedExample) {
  const available = section => lesson.revised_assessment || !section.assessment || progress.completed_at || progress.stage >= STAGES.indexOf('guided');
  const indexOf = id => sections.findIndex(section => section.id === id && available(section));
  const explicit = indexOf(requested ?? (workedExample ? 'worked-example' : null));
  if (explicit >= 0) return explicit;
  if (progress.completed_at && !lesson.revised_assessment) return 0;
  const last = indexOf(readingState(lesson).last);
  if (last >= 0) return last;
  if (lesson.revised_assessment) return 0;
  const checkpoint = sections.findIndex(section => available(section) &&
    (section.advances === STAGES[progress.stage] || section.assessment));
  if (STAGES[progress.stage] === 'worked') {
    const worked = indexOf('worked-example');
    if (worked >= 0) return worked;
  }
  return Math.max(0, checkpoint);
}
function articleSectionNav(lesson, progress, sections, mobile = false) {
  const nav = el('nav', undefined, 'lesson-section-nav');
  nav.setAttribute('aria-label', 'Chapter contents');
  const list = el('ol');
  const { visited } = readingState(lesson);
  const revised = lesson.revised_assessment && foundations.progress(lesson);
  for (const [index, section] of sections.entries()) {
    const locked = !revised && section.assessment && !progress.completed_at && progress.stage < STAGES.indexOf('guided');
    const done = revised ? (section.assessment ? revised.last_correct != null : revised.visited.includes(section.id)) :
      section.assessment ? Boolean(progress.completed_at) : Boolean(section.advances && progress.visited.includes(section.advances));
    const link = el(locked ? 'span' : 'a');
    link.className = 'lesson-section-link';
    link.append(el('span', section.title));
    if (locked) link.setAttribute('aria-disabled', 'true');
    else {
      link.href = sectionRoute(lesson, section);
      link.addEventListener('click', event => {
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        if (!busy && index !== articlePage) showArticlePage(index);
      });
    }
    if (index === articlePage) link.setAttribute('aria-current', 'location');
    const status = locked ? 'Finish earlier stages first'
      : done ? (revised && !section.assessment ? 'Visited' : 'Finished')
        : visited.includes(section.id) ? 'Visited' : '';
    if (status) link.append(el('small', status));
    const item = el('li');
    item.append(link);
    list.append(item);
  }
  nav.append(list);
  if (!mobile) {
    const sidebar = el('aside', undefined, 'lesson-section-sidebar');
    sidebar.append(el('p', 'Chapter contents'), nav);
    return sidebar;
  }
  const details = el('details', undefined, 'lesson-section-mobile');
  const summary = el('summary', 'Chapter contents');
  details.append(summary, nav);
  details.addEventListener('keydown', event => {
    if (event.key === 'Escape' && details.open) {
      details.open = false;
      summary.focus();
    }
  });
  return details;
}
function currentLesson() { return course.lessons.find(l => l.lesson_id===active); }
function progressFor(lesson) {
  const legacy = store.records[lessonKey(lesson)] || emptyProgress();
  return lesson.revised_assessment ? { ...legacy, ...foundations.progress(lesson) } : legacy;
}

function recordFoundationVisit(lesson, section) {
  if (!lesson.revised_assessment?.required_sections.includes(section.id)) return;
  const token = generation;
  const page = articlePage;
  foundations.act(lesson, { kind: 'visit', section: section.id }).then(() => {
    if (token !== generation || page !== articlePage || host.hidden) return;
    const article = articleFor(lesson);
    const progress = progressFor(lesson);
    const sections = articleSections(article);
    const sidebar = host.querySelector('.lesson-section-sidebar');
    const mobile = host.querySelector('.lesson-section-mobile');
    if (sidebar && !sidebar.contains(document.activeElement)) sidebar.replaceWith(articleSectionNav(lesson, progress, sections));
    if (mobile && !mobile.open) mobile.replaceWith(articleSectionNav(lesson, progress, sections, true));
  });
}
async function act(event, afterSave) {
  if (busy) return;const token=generation;const focused=document.activeElement;const focusName=focused?.name,focusValue=focused?.value;let saved;busy=true;render();
  try { const result=await store.act(currentLesson(),event);if(token!==generation)return;saved=progressFor(currentLesson());notice=result.earned ? (store.status === 'Synced to your account'
      ? 'Lesson complete. 15 lesson XP awarded for this content version.'
      : 'Lesson complete. 15 lesson XP awarded on this device. Verified account XP requires account sync.') : ''; }
  catch(error) { if(token!==generation)return;notice=error.message; }
  busy=false;render();
  if (saved && afterSave) { afterSave(saved); return; }
  if(event.type==='answer' && focusName) {
    const response = host.querySelector(`input[name="${CSS.escape(focusName)}"][value="${focusValue}"]`);
    (response || host.querySelector('.constituent-pre-test-status'))?.focus();
  }
  else { const h=host.querySelector('.lesson-stage-body h2');if(h){h.tabIndex=-1;h.focus();} }
}
function selectLesson(id, { section, workedExample } = {}) {
  active = id;
  step = 0;
  notice = '';
  reviewStage = id && progressFor(currentLesson()).completed_at ? 0 : null;
  practiceResponses = null;
  assessmentIndex = 0;
  const lesson = currentLesson();
  const article = lesson && articleFor(lesson);
  if (article) {
    const sections = articleSections(article);
    if (lesson.revised_assessment?.required_sections.some(id => !sections.some(section => section.id === id && !section.assessment))) {
      throw new Error('A required Foundations section is missing from the chapter.');
    }
    articlePage = articlePageFor(lesson, progressFor(lesson), sections, section, workedExample);
    rememberSection(lesson, sections[articlePage]);
    recordFoundationVisit(lesson, sections[articlePage]);
  }
}
function openLesson(id, routeOptions, replace = false) {
  generation++;
  busy = false;
  selectLesson(id, routeOptions);
  const lesson = currentLesson();
  const article = lesson && articleFor(lesson);
  if (article) updateLessonRoute(sectionRoute(lesson, articleSections(article)[articlePage]), replace);
  else updateLessonRoute(lesson ? `#lesson/${id}` : '#lesson/catalog', replace);
  render();
  host.scrollTop = 0;
  const heading = routeOptions?.section || routeOptions?.workedExample
    ? host.querySelector('.lesson-stage-body h2') : host.querySelector('h1');
  heading?.focus({ preventScroll: true });
}
function showCatalog() {
  openLesson(null);
}
function progressBar(value, max, label) {
  const bar = el('progress');
  bar.value = value;
  bar.max = max;
  bar.setAttribute('aria-label', label);
  return bar;
}
function progressSummary() {
  const summary = el('aside', undefined, 'lesson-catalog-summary');
  summary.setAttribute('aria-label', 'Course progress');
  const overview = el('section', undefined, 'lesson-summary-card');
  const completed = course.lessons.filter(lesson => progressFor(lesson).completed_at).length;
  const revised = course.lessons.filter(lesson => lesson.revised_assessment);
  const retired = new Set(revised.map(lesson => lesson.lesson_id));
  const legacy = Object.fromEntries(Object.entries(store.records).filter(([key]) => !retired.has(key.split('@')[0])));
  const xp = lessonXp(legacy) + revised.reduce((total, lesson) => total + foundations.progress(lesson).verified_xp, 0);
  overview.append(
    el('h2', 'Overall progress'),
    el('p', `${completed} / ${course.lessons.length} lessons completed · ${xp} lesson XP`, 'lesson-total'),
    progressBar(completed, course.lessons.length, 'Overall lesson progress'),
  );
  for (const group of course.tracks) {
    const lessons = course.lessons.filter(lesson => lesson.track === group.id);
    const count = lessons.filter(lesson => progressFor(lesson).completed_at).length;
    overview.append(el('p', `${group.title} · ${count} of ${lessons.length} completed`, 'lesson-track-progress'));
  }
  const activity = el('section', undefined, 'lesson-summary-card');
  activity.append(el('h2', 'Recent activity'));
  const recent = course.lessons.map(lesson => {
    const progress = progressFor(lesson);
    return { lesson, progress, date: progress.updated_at || progress.completed_at };
  }).filter(item => item.date)
    .sort((a, b) => Date.parse(b.date) - Date.parse(a.date)).slice(0, 3);
  if (!recent.length) activity.append(el('p', 'Your latest lesson activity will appear here.'));
  else {
    const list = el('ul', undefined, 'lesson-activity-list');
    const format = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' });
    for (const { lesson, progress, date } of recent) {
      const entry = el('li');
      const status = progress.completed_at ? 'Completed' :
        lesson.revised_assessment ? 'In progress' : `Part ${progress.stage + 1} of ${STAGES.length}`;
      const time = el('time', format.format(new Date(date)));
      time.dateTime = date;
      entry.append(button(lesson.title, () => openLesson(lesson.lesson_id), 'lesson-activity-link'), el('span', `${status} · `), time);
      list.append(entry);
    }
    activity.append(list);
  }
  summary.append(overview, activity);
  return summary;
}
function catalog() {
  const header = el('header', undefined, 'curriculum-header');
  const heading = el('h1', 'Lesson modules');
  heading.tabIndex = -1;
  header.append(heading);
  host.append(header);
  const layout = el('div', undefined, 'lesson-catalog-layout');
  const content = el('div', undefined, 'lesson-catalog-content');
  const tabs=el('div',undefined,'lesson-track-tabs');tabs.setAttribute('role','group');tabs.setAttribute('aria-label','Learning tracks');
  for (const t of course.tracks) { const b=button(t.title,()=>{track=t.id;render();});b.setAttribute('aria-pressed',String(track===t.id));tabs.append(b); }
  content.append(tabs);
  const modules = el('div', undefined, 'lesson-modules');
  for (const lesson of course.lessons.filter(l => l.track === track)) {
    const progress = progressFor(lesson);
    const revised = lesson.revised_assessment;
    const completedStages = revised ? progress.visited.length : STAGES.filter(stage => progress.visited.includes(stage)).length;
    const totalStages = revised?.required_sections.length ?? STAGES.length;
    const started = completedStages > 0 || Object.keys(progress.responses).length > 0 ||
      readingState(lesson).visited.some(id => id !== 'introduction');
    const chapter = lesson.track === 'foundations' ? `Chapter ${lesson.chapter}` : `Cambridge · Chapter ${lesson.chapter}`;
    const card = el('article', undefined, 'curriculum-card lesson-module');
    card.append(
      el('p', chapter, 'lesson-eyebrow'),
      el('h2', lesson.title),
    );
    const description = articleFor(lesson)?.description ?? course.module_descriptions?.[lesson.lesson_id];
    if (description) card.append(el('p', description, 'lesson-module-description'));
    const objective = el('p', undefined, 'lesson-module-objective');
    objective.append(el('strong', 'Learning objective'), ' ', lesson.outcomes[0].text);
    card.append(objective);
    const prerequisites = lesson.prerequisites.filter(pr => {
      const previous = course.lessons.find(candidate => candidate.lesson_id === pr.lesson_id);
      if (previous?.revised_assessment && revised) return !progressFor(previous).completed_at;
      return !store.records[lessonKey(pr)]?.completed_at &&
        !(previous?.revised_assessment && progressFor(previous).completed_at);
    });
    if (prerequisites.length) {
      const names = prerequisites.map(pr => course.lessons.find(l => l.lesson_id === pr.lesson_id).title);
      card.append(el('p', revised ? `Recommended first: ${names.join(', ')}. You can work through this chapter now.`
        : `Complete ${names.join(', ')} before finishing this lesson. You can start reading now.`, 'lesson-prerequisite'));
    }

    const footer = el('div', undefined, 'lesson-module-footer');
    const meter = el('div', undefined, 'lesson-module-progress');
    meter.append(el('p', `${completedStages} of ${totalStages} ${revised ? 'required sections visited' : 'stages completed'}`),
      progressBar(completedStages, totalStages, `${lesson.title} progress`));
    const action = progress.completed_at ? 'Review lesson' : started ? 'Resume lesson' : 'Start lesson';
    const actionStyle = action === 'Resume lesson' ? 'lesson-open lesson-resume lesson-primary' : 'lesson-open';
    footer.append(meter, button(action, () => openLesson(lesson.lesson_id), actionStyle));
    card.append(footer);
    modules.append(card);
  }
  content.append(modules);
  if (track==='grammar') {
    const planned=el('details',undefined,'lesson-planned');planned.append(el('summary',`${course.planned_modules.length} further topics planned — not published`));
    const list=el('ul');for(const p of course.planned_modules)list.append(el('li',`${p.title}: ${p.reason}`));planned.append(list);content.append(planned);
  }
  layout.append(content, progressSummary());
  host.append(layout);
}
function question(lesson,key,p,locked,onAnswer = answer => act({type:'answer',answer}), data = lesson[key]) {
  const section=el('section',undefined,'lesson-question');section.dataset.question=key;
  const field=el('fieldset');field.disabled=busy || locked;field.append(el('legend',data.prompt));
  for (const option of data.options) {
    const label=el('label',undefined,'lesson-option'),radio=el('input');radio.type='radio';radio.name=`${lesson.lesson_id}-${key}`;radio.value=option.id;radio.checked=p.responses[key]===option.id;
    radio.addEventListener('change',()=>onAnswer(option.id));label.append(radio,el('span',option.text));field.append(label);
  }
  section.append(field);
  if (p.responses[key]) {
    const chosen = data.options.find(option => option.id === p.responses[key]);
    const correct = chosen.id === data.answer;
    section.append(el('p', chosen.feedback, correct ? 'lesson-feedback correct' : 'lesson-feedback retry'));
  }
  if (data.hint) {
    const hint=el('details');
    hint.append(el('summary','Need a hint?'),el('p',data.hint));
    section.append(hint);
  }
  return section;
}

function mountLessonCanvas(host, tree, options) {
  const treeView = renderLessonTree(tree, { ...options, textDisclosure: false });
  const canvas = el('div', undefined, 'lesson-tree-canvas');
  canvas.append(treeView);
  host.append(canvas);
  lessonCanvases.set(host, enableCanvasView(canvas, treeView));
  return canvas;
}

function clearLessonDiagram(host) {
  lessonCanvases.get(host)?.destroy();
  lessonCanvases.delete(host);
  host.replaceChildren();
}

function clearLessonCanvases() {
  embeddedBuilderCleanup?.();
  embeddedBuilderCleanup = null;
  for (const view of lessonCanvases.values()) view.destroy();
  lessonCanvases.clear();
}

function appendWorkedTree(aside, worked, { focusId, blank = null, comparisonTree = null, inline = false, highlightWords = false, tracePath = false, observation = null, onSelect = null }) {
  const evidence=el('details',undefined,'lesson-shared-evidence');
  evidence.dataset.xai7Lesson = '';
  const title=el('summary','Explanation');
  const slot=el('div',undefined,'lesson-unified-evidence');
  evidence.append(title,slot);
  let requestVersion=0;
  let selected = focusId;
  const selectedWords = el('p', undefined, 'constituent-selection');
  selectedWords.setAttribute('aria-live', 'polite');
  const positions = new Map();
  function indexPositions(node, parent) {
    if (node.id) positions.set(node.id, { node, parent });
    for (const child of node.children || []) indexPositions(child, node);
  }
  indexPositions(worked.tree.root);
  function describeSelection(id) {
    const position = positions.get(id);
    if (!position) return;
    const { node, parent } = position;
    const [start, end] = node.token_span || [];
    if (node.gap || start === end && Number.isInteger(start)) {
      const label = parent?.label;
      selectedWords.textContent = node.gap
        ? `Gap under ${label || 'the parent node'}. No word is spoken here.`
        : 'This position has no spoken words.';
    } else if (Number.isInteger(start) && Number.isInteger(end)) {
      selectedWords.replaceChildren('Selected words: ');
      worked.tree.tokens.forEach((token, index) => {
        if (index) selectedWords.append(' ');
        selectedWords.append(index >= start && index < end ? el('mark', token.text) : token.text);
      });
    }
  }
  const inspect=async (nodeId, feature=null) => {
    selected=nodeId;
    if (inline) {
      selectedWords.replaceChildren();
      describeSelection(nodeId);
      for (const item of canvas.querySelectorAll('svg [data-node-id]')) {
        const isSelected = item.dataset.nodeId === nodeId;
        item.toggleAttribute('data-constituent-selected', isSelected);
        if (!isSelected) item.classList.remove('lesson-tree-focus');
      }
    }
    onSelect?.(nodeId, positions.get(nodeId));
    evidence.open=true;
    const version=++requestVersion;
    slot.replaceChildren(el('p','Explaining this word or phrase…'));
    try {
      const result=await requestEvidence(worked.tree,nodeId);
      if (version!==requestVersion||!slot.isConnected) return;
      renderEvidence(result,slot,{treeRoot:canvas,feature});
    } catch {
      if (version===requestVersion&&slot.isConnected) {
        slot.replaceChildren(el('p','An explanation is not available for this part of the sentence.'));
      }
    }
  };
  const canvas = mountLessonCanvas(aside, comparisonTree || worked.tree, {
    focusId: selected,
    blank,
    interactive: true,
    onSelectNode: inspect,
    stackFeatures: true,
    wordBaseline: comparisonTree ? 2 : 0,
    highlightWords: highlightWords || Boolean(comparisonTree),
    tracePath,
  });
  if (inline) {
    if (selected) describeSelection(selected);
    if (observation) {
      observation.querySelector('.constituent-selection')?.remove();
      observation.prepend(selectedWords);
      canvas.after(observation);
    } else {
      canvas.append(selectedWords);
    }
  } else {
    aside.append(el('p', worked.origin, 'lesson-origin'));
    if (selected) aside.append(button('Inspect highlighted tree position', () => inspect(selected)));
  }
  evidence.addEventListener('toggle',()=>{if(evidence.open&&!slot.childElementCount&&selected)inspect(selected);});
  aside.append(evidence);
  return canvas;
}

function showArticlePage(page, { fromHistory = false } = {}) {
  const lesson = currentLesson();
  const section = articleSections(articleFor(lesson))[page];
  articlePage = page;
  rememberSection(lesson, section);
  recordFoundationVisit(lesson, section);
  if (!fromHistory) updateLessonRoute(sectionRoute(lesson, section));
  render();
  host.scrollTop = 0;
  host.querySelector('.lesson-stage-body h2')?.focus({ preventScroll: true });
}

function assessmentPosition(index, total) {
  const position = el('p', `Question ${index + 1} of ${total}`, 'lesson-assessment-position');
  position.tabIndex = -1;
  return position;
}

function focusAssessmentPosition() {
  const position = host.querySelector('.lesson-assessment-position');
  position?.focus({ preventScroll: true });
  position?.scrollIntoView({ block: 'nearest' });
}

function openingResultKey(lesson) {
  return `syntutor:opening-result:v1:${readingScope()}:${lessonKey(lesson)}`;
}

function openingStatus(score, total) {
  return score === null ? 'Knowledge check complete.' : `Knowledge check complete. ${score} of ${total} correct.`;
}

function savedOpeningStatus(lesson, total) {
  let score = null;
  try {
    const saved = localStorage.getItem(openingResultKey(lesson));
    if (saved !== null && /^\d+$/.test(saved) && Number(saved) <= total) score = Number(saved);
  } catch { /* The score is optional when storage is unavailable. */ }
  return openingStatus(score, total);
}

function addOpeningQuestions(panel, lesson, prompts) {
  const draftKey = `syntutor:opening-check:${readingScope()}:${lessonKey(lesson)}`;
  let answers = [];
  let selected;
  try {
    const saved = JSON.parse(sessionStorage.getItem(draftKey));
    const submitted = Array.isArray(saved) ? saved : saved?.answers;
    if (Array.isArray(submitted) && submitted.length < prompts.length &&
        submitted.every((id, index) => prompts[index].options.some(option => option.id === id))) {
      answers = submitted;
      if (prompts[answers.length].options.some(option => option.id === saved.selected)) selected = saved.selected;
    }
  } catch {
    // The check can still be completed when session storage is unavailable.
  }
  const current = el('div');
  panel.append(current);
  function saveDraft() {
    try { sessionStorage.setItem(draftKey, JSON.stringify({ answers, selected })); }
    catch { /* The draft still works on this page. */ }
  }
  function showQuestion() {
    const index = answers.length;
    const last = index === prompts.length - 1;
    const next = button(last ? 'Finish knowledge check' : 'Next question →', () => {
      if (last) {
        // Keep the existing single prediction response as the synced completion marker.
        const submitted = [...answers, selected];
        const score = submitted.filter((id, i) => id === prompts[i].answer).length;
        const resultKey = openingResultKey(lesson);
        act({ type: 'answer', answer: submitted[0] }, saved => {
          if (!saved.responses.predict) return;
          try { localStorage.setItem(resultKey, String(score)); } catch { /* The result still appears for this visit. */ }
          try { sessionStorage.removeItem(draftKey); } catch { /* Optional draft storage. */ }
          const status = host.querySelector('.constituent-pre-test-status');
          if (status) {
            status.textContent = openingStatus(score, prompts.length);
            status.focus({ preventScroll: true });
          }
        });
        return;
      }
      answers.push(selected);
      selected = undefined;
      saveDraft();
      showQuestion();
      focusAssessmentPosition();
    }, 'lesson-primary');
    next.disabled = selected === undefined;
    const item = question(lesson, 'predict', { responses: { predict: selected } }, false, answer => {
      selected = answer;
      saveDraft();
      next.disabled = false;
    }, prompts[index]);
    const actions = el('div', undefined, 'lesson-assessment-actions');
    actions.append(next);
    current.replaceChildren(assessmentPosition(index, prompts.length), item, actions);
  }
  showQuestion();
}

function articleScreen(lesson, p, article) {
  const page = articlePage;
  const sections = articleSections(article);
  const section = sections[page];
  const reviewing = Boolean(p.completed_at);
  const revised = lesson.revised_assessment;
  const openingCheck = typeof article.openingCheck === 'function' ? article.openingCheck(lesson) : article.openingCheck;
  const body = el('article', undefined, 'lesson-stage-body');
  const heading = el('h2', section.title);
  heading.id = 'constituent-page-title';
  body.setAttribute('aria-labelledby', heading.id);
  heading.tabIndex = -1;
  body.append(heading);
  const layout = el('div', undefined, 'constituent-page');
  layout.append(articleSectionNav(lesson, p, sections, true), body);
  const frame = el('div', undefined, 'lesson-reader');
  frame.append(articleSectionNav(lesson, p, sections), layout);
  host.append(frame);

  article.teach(body, page, {
    el, button, lesson, section, userId: lessonUserId(),
    getWorkedExample: id => course.lessons.find(item => item.lesson_id === id).worked_example,
    showClosingWarmup: !revised && section.assessment && !reviewing && !p.responses.guided && STAGES[p.stage] === 'guided',
    practiceQuestion: (key, prompt, choices, onAnswer) => question(
      lesson, key, { responses: {} }, false, onAnswer,
      { prompt, options: choices.map((text, index) => ({ id: String(index), text })) },
    ),
    mountBuilder: (stage, exercise) => {
      const editor = options.mountBuilder(stage, {
        ...exercise,
        // Preserve existing 1.0.0 drafts. New content versions start in their own namespace.
        id: lesson.content_version === '1.0.0' ? exercise.id : `${lessonKey(lesson)}:${section.id}:${exercise.id}`,
      });
      embeddedBuilderCleanup = editor.destroy;
      return editor;
    },
    showDiagram: (figure, tree, options) => {
      clearLessonDiagram(figure);
      return mountLessonCanvas(figure, tree, options);
    },
    showWorkedTree: (figure, focusId, options) => {
      clearLessonDiagram(figure);
      return appendWorkedTree(figure, lesson.worked_example, { focusId, inline: true, ...options });
    },
    showComparisonTree: (figure, flatTree, observation) => {
      clearLessonDiagram(figure);
      if (flatTree) {
        const canvas = mountLessonCanvas(figure, flatTree, {
          focusId: flatTree.root.id, wordBaseline: 2, highlightWords: true,
        });
        observation.querySelector('.constituent-selection')?.remove();
        canvas.after(observation);
        return canvas;
      }
      const worked = lesson.worked_example;
      const focusId = worked.steps.at(-1).focus_node_id;
      // Expand the teaching diagram only. Explanations still use the canonical tree and node IDs.
      const root = {
        ...worked.tree.root,
        children: worked.tree.root.children.map(node => node.id === focusId ? {
          ...node,
          triangle: false,
          words: undefined,
          children: node.words.map(word => ({ word })),
        } : node),
      };
      return appendWorkedTree(figure, worked, { focusId, comparisonTree: { ...worked.tree, root }, inline: true, observation });
    },
  });

  const diagram = body.querySelector('.constituent-diagram');
  if (diagram) diagram.after(lessonNotation(lesson, page, el, section.notationLabels, section.notationFeatures));

  if (section.id === 'introduction') {
    addLessonKeyTerms(body, el, lesson.lesson_id, article.keyTerms);
  }

  if (revised) {
    if (section.references) body.append(lessonReferences(lesson));
    const userId = lessonUserId();
    const kind = section.assessment ? 'closing' : section.id === 'introduction' ? 'opening' : null;
    if (kind) body.append(renderFoundationCheck({
      lesson, progress: p, kind, el, button, userId, account: userId !== 'guest',
      async submit(event, clearDraft) {
        const token = generation;
        const result = await foundations.act(lesson, event);
        clearDraft();
        if (token !== generation || articlePage !== page || host.hidden) return;
        notice = result.earned > 0 ? `+${result.earned} lesson XP` : '';
        render();
        host.querySelector('.lesson-assessment [role="status"]')?.focus();
      },
    }));
    const actions = el('div', undefined, 'lesson-page-actions constituent-actions');
    if (page > 0) actions.append(button('← Previous', () => showArticlePage(page - 1)));
    const next = sections[page + 1];
    actions.append(next
      ? button(next.assessment ? 'Check what you learned' : 'Next →', () => showArticlePage(page + 1), 'lesson-primary')
      : button('All lessons', showCatalog, 'lesson-primary'));
    layout.append(actions);
    return;
  }

  if (section.id === 'introduction') {
    const preTest = el('section', undefined, 'lesson-assessment constituent-pre-test');
    const title = el('h3', openingCheck ? 'Check what you know' : 'Pre-test');
    title.id = 'lesson-pre-test-title';
    preTest.setAttribute('aria-labelledby', title.id);
    preTest.append(title, el('p', openingCheck
      ? 'Try three short questions to see what you already know. You’ll see how many you got right. Any result lets you continue and has no effect on XP.'
      : 'Answer this short question before you begin. Your answer is unscored, and any choice lets you continue.'));
    if (p.responses.predict) {
      // Earlier versions used a different prompt with the same saved response key.
      // Acknowledge submission without applying an older choice to the new prompt.
      const recorded = el('p', openingCheck ? savedOpeningStatus(lesson, openingCheck.length) : 'Response recorded.', 'constituent-pre-test-status');
      recorded.setAttribute('role', 'status');
      recorded.tabIndex = -1;
      preTest.append(recorded);
    } else if (openingCheck) {
      addOpeningQuestions(preTest, lesson, openingCheck);
    } else {
      const { prompt, options } = lesson.predict;
      preTest.append(question(lesson, 'predict', p, reviewing, undefined, { prompt, options }));
    }
    if (reviewing) {
      const correct = postTestKeys.filter(key => p.responses[key] === lesson[key].answer).length;
      preTest.append(el('p', `Closing check complete. ${correct} of ${postTestKeys.length} correct.`, 'lesson-closing-result'));
    }
    body.append(preTest);
  }

  if (section.references) body.append(lessonReferences(lesson));

  const actions = el('div', undefined, 'lesson-page-actions constituent-actions');
  if (page > 0) {
    const previous = button('← Previous', () => showArticlePage(page - 1));
    previous.disabled = busy;
    actions.append(previous);
  }

  if (!section.assessment) {
    const following = sections[page + 1];
    if (following) {
      const entersAssessment = Boolean(following.assessment);
      const advancesProgress = !reviewing && STAGES[p.stage] === section.advances;
      const next = button(entersAssessment ? (openingCheck ? 'Check what you learned' : 'Start post-test') : 'Next →', () => {
        if (advancesProgress) {
          act({ type: 'advance' }, result => {
            if (result.stage !== p.stage) showArticlePage(page + 1);
          });
        } else {
          showArticlePage(page + 1);
        }
      }, 'lesson-primary');
      const waitingForEarlierSections = entersAssessment && !reviewing &&
        p.stage < STAGES.indexOf('guided') && !advancesProgress;
      next.disabled = busy || waitingForEarlierSections || (advancesProgress && !canAdvance(lesson, p));
      if (waitingForEarlierSections) body.append(el('p',
        'Finish the opening check and continue through the concepts before starting the closing check.', 'lesson-guide-note'));
      actions.append(next);
    }
  } else {
    const practice = practiceResponses !== null;
    const key = STAGES[p.stage];
    const paged = openingCheck && (!reviewing || practice);
    const keys = !reviewing ? [key] : paged ? [postTestKeys[assessmentIndex]] : postTestKeys;
    const postTest = el('section', undefined, 'lesson-assessment');
    postTest.setAttribute('aria-label', openingCheck ? 'Chapter knowledge check' : 'Post-test questions');
    if (openingCheck && reviewing && !practice) {
      const overview = el('h3', 'Answers overview', 'lesson-answers-heading');
      overview.tabIndex = -1;
      postTest.append(overview);
    }
    postTest.append(el('p', practice ? 'Try the chapter questions again. This is a practice attempt.'
      : reviewing ? 'Review your answers and feedback from the completed chapter.'
        : article.postTestIntro));
    if (paged) postTest.append(assessmentPosition(postTestKeys.indexOf(keys[0]), postTestKeys.length));
    const questionActions = paged ? el('div', undefined, 'lesson-assessment-actions') : actions;
    for (const item of keys) {
      const response = practice ? { responses: practiceResponses } : p;
      if (item === 'guided' && lesson.guided.build_target && lesson.worked_example.tree) {
        const diagram = el('div', undefined, 'constituent-diagram');
        const target = lesson.guided.build_target;
        const blank = response.responses.guided === lesson.guided.answer ? null : target;
        diagram.append(el('p', lesson.worked_example.sentence, 'lesson-example-sentence'));
        if (blank) {
          mountLessonCanvas(diagram, lesson.worked_example.tree, {
            focusId: target.node_id, blank, stackFeatures: true,
          });
        } else {
          appendWorkedTree(diagram, lesson.worked_example, { focusId: target.node_id, inline: true });
        }
        postTest.append(diagram);
      }
      postTest.append(question(lesson, item, response, reviewing && !practice, answer => {
        if (!practice) {
          act({ type: 'answer', answer });
          return;
        }
        practiceResponses[item] = answer;
        render();
        host.querySelector(`[data-question="${item}"] input:checked`)?.focus();
      }));
    }
    body.append(postTest);
    if (practice && paged) {
      const item = keys[0];
      const last = assessmentIndex === postTestKeys.length - 1;
      const move = delta => {
        assessmentIndex += delta;
        render();
        focusAssessmentPosition();
      };
      if (assessmentIndex > 0) questionActions.append(button('← Previous question', () => move(-1)));
      if (!last) {
        const next = button('Next question →', () => move(1), 'lesson-primary');
        next.disabled = !practiceResponses[item];
        questionActions.append(next);
      } else {
        const finish = button('Finish practice', () => {
          practiceResponses = null;
          assessmentIndex = 0;
          render();
          host.querySelector('.lesson-answers-heading')?.focus();
        }, 'lesson-primary');
        finish.disabled = !practiceResponses[item];
        questionActions.append(finish);
      }
    } else if (reviewing && openingCheck) {
      actions.append(button('Try the questions again', () => {
        practiceResponses = {};
        assessmentIndex = 0;
        render();
        focusAssessmentPosition();
      }), button('Finish review', showCatalog, 'lesson-primary'));
    } else if (reviewing) {
      if (!practice) {
        actions.append(button('Retake post-test', () => {
          practiceResponses = {};
          showArticlePage(page);
        }));
      }
      actions.append(button(practice ? 'Finish practice' : 'Finish review', () => {
        if (!practice) { showCatalog(); return; }
        practiceResponses = null;
        showArticlePage(page);
      }, 'lesson-primary'));
      if (practice) {
        actions.lastElementChild.disabled = !postTestKeys.every(item => practiceResponses[item]);
      }
    } else {
      const next = button(busy ? 'Saving…' : key === 'exit' ? 'Complete lesson' : 'Next question →', () => {
        act({ type: 'advance' }, result => {
          if (result.completed_at) showArticlePage(page);
          else if (openingCheck) focusAssessmentPosition();
          else {
            const prompt = host.querySelector('.lesson-question legend');
            if (prompt) {
              prompt.tabIndex = -1;
              prompt.focus();
            }
          }
        });
      }, 'lesson-primary');
      next.disabled = busy || !canAdvance(lesson, p);
      questionActions.append(next);
    }
    if (paged && questionActions.childElementCount) postTest.append(questionActions);
    if (openingCheck ? reviewing && !practice : key === 'exit' || reviewing) article.review?.(body, { el });
  }
  layout.append(actions);
}

function lessonScreen() {
  const lesson = currentLesson(), p = progressFor(lesson);
  const stage = reviewStage ?? p.stage, key = STAGES[stage];
  const reviewing = reviewStage !== null;
  const article = articleFor(lesson);
  const chapter = lesson.track === 'grammar'
    ? `Cambridge · Chapter ${lesson.chapter}`
    : `Chapter ${lesson.chapter}`;
  const header = el('header', undefined, article ? 'lesson-header constituent-header' : 'lesson-header');
  header.append(button('← All lessons', showCatalog));
  const h1 = el('h1', lesson.title);
  h1.tabIndex = -1;
  if (article) {
    const chapterTitle = el('div', undefined, 'constituent-chapter');
    chapterTitle.append(el('p', chapter), h1);
    header.append(chapterTitle);
  } else {
    header.append(el('p', chapter, 'lesson-eyebrow'), h1, el('p', lesson.outcomes[0].text, 'lesson-lead'));
  }
  if (lesson.lesson_id === pilotId()) {
    header.append(el('p', 'Chapter pilot · progress saved on this device', 'lesson-guide-note'));
  }
  host.append(header);
  if (article) { articleScreen(lesson, p, article); return; }
  const columns=el('div',undefined,'lesson-columns'),body=el('section',undefined,'lesson-stage-body'),aside=el('aside',undefined,'lesson-evidence-card');
  const partHeading = el('h2', STAGE_TITLES[stage]);
  partHeading.tabIndex = -1;
  body.append(partHeading);
  const worked = lesson.worked_example;
  if (lesson[key]) body.append(question(lesson,key,p,reviewing));
  if (key==='understand') {
    for (const block of lesson.teaching) body.append(el('p', block.text));
    for (const insight of lesson.cambridge_insights) { const card=el('section',undefined,'lesson-insight');card.append(el('h3','Cambridge insight'),el('p',insight.text));body.append(card); }
  }
  aside.append(el('h2', 'Worked example'),el('p',worked.sentence,'lesson-example-sentence'));
  if (worked.tree) appendWorkedTree(aside, worked, {
    focusId: key === 'guided' ? lesson.guided.build_target?.node_id : worked.steps[step]?.focus_node_id,
    blank: key === 'guided' && p.responses.guided !== lesson.guided.answer ? lesson.guided.build_target : null,
  });
  else aside.append(el('p',lesson.chapter===11 && lesson.track==='foundations' ? 'This closing chapter is a text-only synthesis. No new tree convention or gradable tree is introduced.' : 'Compare the whole sentence with the clause inside it.'), el('p', worked.origin, 'lesson-origin'));
  if(key==='worked') {
    body.append(el('p',`Step ${step+1} of ${worked.steps.length}`),el('p',worked.steps[step].text));
  }
  if(key==='guided' && lesson.guided.build_target) body.append(el('p','Fill the highlighted missing label or feature in the worked tree. The complete original returns when your answer matches.','lesson-guide-note'));
  if(key==='predict') body.append(el('p','This is a prediction, not a scored assessment. A wrong first answer does not reduce XP.'));
  const actions = el('div', undefined, 'lesson-page-actions');
  const moreWorkedSteps = key === 'worked' && step < worked.steps.length - 1;
  const nextText = key === 'exit' ? (reviewing ? 'Finish review' : 'Complete lesson') : 'Next →';
  if (!p.completed_at || reviewing) {
    const next = button(busy ? 'Saving…' : nextText, () => {
      if (moreWorkedSteps) step++;
      else if (!reviewing) { act({type:'advance'}); return; }
      else if (key === 'exit') { showCatalog(); return; }
      else reviewStage++;
      render();
      host.querySelector('.lesson-stage-body h2')?.focus();
    }, 'lesson-primary');
    next.disabled = busy || (!reviewing && !canAdvance(lesson,p));
    actions.append(next);
  }
  if(key==='exit' && p.completed_at && !reviewing) {
    const following=course.lessons.find(l=>l.prerequisites.some(pr=>pr.lesson_id===lesson.lesson_id) && !progressFor(l).completed_at);
    if (following) actions.append(button(`Next lesson: ${following.title}`, () => openLesson(following.lesson_id), 'lesson-primary'));
  }
  columns.append(body);
  columns.append(aside);
  host.append(columns);
  if (key === 'exit') host.append(lessonReferences(lesson));
  if (actions.childElementCount) host.append(actions);
}
function render() {
  if (!host || host.hidden || !course || !store) return;
  clearLessonCanvases();
  const scroll=host.scrollTop;host.replaceChildren();
  if(active)lessonScreen();else catalog();
  const footer = el('footer', undefined, 'lesson-save-status');
  footer.setAttribute('aria-live', 'polite');
  if (notice) footer.append(el('p', notice));
  const syncStatus = foundations.pending ? 'Saved on this device. Account sync is pending.' : store.status;
  footer.append(el('p', syncStatus));
  if (lessonUserId() !== 'guest') footer.append(button('Retry account sync', async () => {
    const token = generation;
    const legacy = store;
    await foundations.load();
    await legacy.retry();
    if (token === generation) render();
  }));
  host.append(footer);host.scrollTop=scroll;
}
export function initLessons(config = {}) {
  options=config;
  host=document.getElementById('curriculumView');
  if(!host) {host=el('section',undefined,'curriculum-view');host.id='curriculumView';host.hidden=true;host.setAttribute('aria-label','Lessons and curriculum');document.body.append(host);}
  subscribeAuthState(() => {
    generation++;
    store = null;
    foundations = null;
    active = null;
    busy = false;
    if (!host.hidden) {
      const route = readLessonRoute();
      openLessons(route?.id ?? null, { section: route?.section, fromHistory: true });
    }
  });
  const route = event => {
    const target = readLessonRoute();
    if (!target) {
      if (!host.hidden && event && !location.hash) options.onExit?.();
      return;
    }
    if (!host.hidden && store) {
      const lesson = currentLesson();
      const article = lesson && articleFor(lesson);
      if (active === target.id && article) {
        const sections = articleSections(article);
        const page = articlePageFor(lesson, progressFor(lesson), sections, target.section);
        generation++;
        busy = false;
        showArticlePage(page, { fromHistory: true });
        updateLessonRoute(sectionRoute(lesson, sections[page]), true);
      } else {
        const id = course.lessons.some(item => item.lesson_id === target.id) ? target.id : null;
        openLesson(id, target, true);
      }
    } else {
      options.onNavigate?.(target.id, { section: target.section, fromHistory: true });
    }
  };
  window.addEventListener('hashchange', route);
  if (readLessonRoute()) queueMicrotask(() => route());
}
export async function openLessons(id = null, { workedExample = false, section, fromHistory = false } = {}) {
  lastFocus = document.activeElement;
  host.hidden = false;
  document.body.classList.add('curriculum-open');
  clearLessonCanvases();
  showCurriculumState(host, { message: 'Loading reviewed lessons…' });
  const token = ++generation;
  try {
    if (!course) {
      const catalog = await (await fetch('/content/lessons/course.json', { cache: 'no-cache' })).json();
      const preview = pilotId();
      if (preview) {
        const response = await fetch(`/content/lessons/${preview}-pilot.json`, { cache: 'no-cache' });
        if (!response.ok) throw new Error('Chapter pilot unavailable.');
        const { preview_sources: previewSources = [], ...pilot } = await response.json();
        catalog.sources.push(...previewSources);
        catalog.lessons = catalog.lessons.map(lesson => lesson.lesson_id === preview ? { ...lesson, ...pilot } : lesson);
      }
      course = validateCourse(catalog);
    }
    if (!store) {
      let storage;
      try { storage = localStorage; } catch { storage = null; }
      if (storage && pilotId()) {
        const device = storage;
        storage = {
          getItem: key => device.getItem(`syntutor:${readingScope()}:${key}`),
          setItem: (key, value) => device.setItem(`syntutor:${readingScope()}:${key}`, value),
        };
      }
      const config = { storage, userId: lessonUserId(), client: pilotId() ? null : options.client?.() };
      const revised = createFoundationStore(course, config);
      const next = createLessonStore(course, { ...config, revisedProgress: revised.progress });
      await revised.load();
      await next.load();
      if (token !== generation) return;
      store = next;
      foundations = revised;
    }
    if (token !== generation) return;
    host.setAttribute('aria-busy', 'false');
    document.querySelector('#appSidebarBackdrop')?.classList.remove('active');
    openLesson(course.lessons.some(lesson => lesson.lesson_id === id) ? id : null,
      { section, workedExample }, fromHistory);
  } catch {
    if (token === generation) showCurriculumState(host, {
      title: 'Lessons unavailable',
      message: 'The lesson catalog could not be loaded or its source review is incomplete.',
      retry: () => openLessons(id, { workedExample, section, fromHistory }), back: options.onExit,
    });
  }
}
export function closeLessons() { generation+=1;clearLessonCanvases();if(host){host.hidden=true;host.replaceChildren();}document.body.classList.remove('curriculum-open');active=null;notice='';if(lastFocus?.isConnected)lastFocus.focus(); }
