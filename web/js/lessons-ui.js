import { showCurriculumState } from './curriculum-state.js';
import { STAGES, STAGE_TITLES, validateCourse, lessonKey, emptyProgress, canAdvance, lessonXp } from './lesson-core.js';
import { createLessonStore } from './lesson-progress.js';
import { requestEvidence, renderEvidence } from './explanation-evidence.js';
import { subscribeAuthState } from './auth.js';
import { enableCanvasView } from './canvas-view.js';
import { addConstituentReview, addConstituentTeaching, constituentHeadings, constituentPreTest, constituentReferences } from './constituents-lesson.js';
import { addSubjectPredicateTeaching, subjectPredicateHeadings } from './subject-predicate-lesson.js';
import { foundationsArticle } from './foundations-lesson.js';
import { lessonNotation } from './lesson-notation.js';

const articleLessons = {
  'br-01': {
    headings: constituentHeadings,
    preTest: constituentPreTest,
    teach: addConstituentTeaching,
    review: addConstituentReview,
    postTestIntro: 'Use what you learned about groups, brackets, and branches. Check each answer before continuing.',
  },
  'br-02': {
    headings: subjectPredicateHeadings,
    teach: addSubjectPredicateTeaching,
    postTestIntro: 'Use the NP and VP branches to identify the subject and predicate. Check each answer before continuing.',
  },
};

let options = {}, course, store, host, active = null, step = 0, track = 'foundations', busy = false, notice = '', generation = 0, lastFocus = null;
let reviewStage = null;
let articlePage = 0, practiceResponses = null;
const postTestKeys = ['guided', 'transfer', 'exit'];
const lessonCanvases = new Map();
let embeddedBuilderCleanup = null;
const el = (tag, text, cls) => { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (cls) node.className = cls; return node; };
function button(text, run, cls = '') { const b = el('button',text,cls); b.type = 'button'; b.addEventListener('click',run); return b; }
function lessonReferences(lesson) {
  const blocks = [lesson, ...lesson.teaching, ...lesson.cambridge_insights, lesson.worked_example,
    ...lesson.worked_example.steps, lesson.predict, lesson.guided, lesson.transfer, lesson.exit];
  const ids = new Set(blocks.flatMap(block => block.source_ids || []));
  const details = el('details', undefined, 'lesson-sources');
  details.append(el('summary', 'References and source review'));
  const list = el('ul');
  for (const source of course.sources.filter(source => ids.has(source.id))) {
    list.append(el('li', `${source.title} · ${source.edition} · Chapter ${source.chapter} · printed p. ${source.printed_page}`));
  }
  if (lesson.lesson_id === 'br-01') {
    for (const reference of constituentReferences) list.append(el('li', reference));
  }
  details.append(list, el('p', 'AI checked the cited pages. The lesson has no human instructor sign-off.'));
  return details;
}
const SVG_NS = 'http://www.w3.org/2000/svg';
function svgNode(name, attrs = {}) { const n = document.createElementNS(SVG_NS,name); for (const [k,v] of Object.entries(attrs)) n.setAttribute(k,v); return n; }
// Read-only canonical trees plus a constrained fill-in target for guided practice.
// Advanced structures never pass through the parser or the legacy Builder bridge.
export function renderLessonTree(envelope, {
  focusId = null, blank = null, stackFeatures = false, displayLabels = null,
  interactive = false, onSelectNode = null, zoomControls = false, wordBaseline = 0,
  textDisclosure = true, traceBranches = false,
} = {}) {
  const wrap = el('div',undefined,'lesson-tree-wrap');
  const root = envelope.root;
  const hint = el('p', textDisclosure
    ? 'Scroll sideways to inspect the whole tree, or open its text view.'
    : 'Scroll sideways to inspect the whole tree.', 'lesson-tree-hint');
  wrap.append(hint);wrap.tabIndex=0;wrap.setAttribute('aria-label','Scrollable B-R tree');
  function label(node, withFeatures = true) {
    const master = displayLabels?.[node.id];
    if (master) return withFeatures ? master.join(' ') : master[0] || '';
    if (node.gap) return node.index === undefined ? '•' : `• (${node.index})`;
    const vpSourceRef = node.label === 'VP' ? [node.ref, ...(node.source_refs || [])].find(ref => typeof ref === 'string' && /^VP[1-9][0-9]*$/.test(ref)) : null;
    const numberedVP = vpSourceRef ? 'VP' + vpSourceRef.slice(2).replace(/[0-9]/g, digit => '₀₁₂₃₄₅₆₇₈₉'[Number(digit)]) : null;
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
  const svg=svgNode('svg',{viewBox:`0 0 ${width} ${height}`,width,height,role,'aria-label':`B-R tree for ${envelope.sentence}`});
  const branchLines = edges.map(([a,b]) => {
    const line = svgNode('line',{x1:a.x,y1:a.y+12+featureRows(a.node).length*18,x2:b.x,y2:b.y-18,class:'lesson-branch'});
    svg.append(line);
    return line;
  });
  const wordLabels = new Map();
  function trace(nodeId) {
    const covered = new Set();
    function collect(node) {
      covered.add(node);
      for (const child of node.children || []) collect(child);
    }
    const selected = positions.find(({ node }) => node.id === nodeId);
    if (selected) collect(selected.node);
    edges.forEach(([parent], index) => {
      branchLines[index].classList.toggle('lesson-branch-traced', covered.has(parent.node));
    });
    for (const [node, label] of wordLabels) {
      label.classList.toggle('lesson-word-traced', covered.has(node));
    }
  }
  for (const {node,x,y} of positions) {
    const g=svgNode('g',{'data-node-id':node.id || '',class:node.id===focusId ? 'lesson-tree-focus' : ''});
    if (node.id===focusId) g.append(svgNode('rect',{x:x-55,y:y-20,width:110,height:40,rx:9}));
    const t=svgNode('text',{x,y,'text-anchor':'middle'});
    t.textContent=visibleLabel(node);g.append(t);
    if (traceBranches && node.word) wordLabels.set(node, t);
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
    }
    if (typeof onSelectNode === 'function' && node.id) {
      g.setAttribute('role','button');
      g.setAttribute('tabindex','0');
      g.setAttribute('aria-label','Inspect B-R ' + (node.label || 'tree position')
        + ' for ' + (node.word || node.words?.join(' ') || node.label || 'this position'));
      const choose = () => {
        if (traceBranches) trace(node.id);
        onSelectNode(node.id, null);
      };
      g.addEventListener('click', choose);
      g.addEventListener('keydown', event => {
        if (event.target !== g) return;
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); choose(); }
      });
      for (const row of g.querySelectorAll('.br-feature-row')) {
        row.setAttribute('role','button');
        row.setAttribute('tabindex','0');
        row.dataset.featureLabel = row.textContent;
        row.setAttribute('aria-label','Inspect recorded B-R feature ' + row.textContent
          + ' for ' + (node.word || node.label));
        const featureName=()=>{const text=row.textContent.trim();return text.startsWith('[') && text.endsWith(']') ? text.slice(1,-1) : text;};
        row.addEventListener('click', event => {
          event.stopPropagation(); onSelectNode(node.id,featureName());
        });
        row.addEventListener('keydown', event => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.stopPropagation(); event.preventDefault();
            onSelectNode(node.id,featureName());
          }
        });
      }
    }
    svg.append(g);
  }
  if (traceBranches) trace(focusId);
  if (zoomControls) {
    const toolbar=el('div',undefined,'xai7-tree-zoom');
    toolbar.dataset.xai7Zoom = '';
    toolbar.setAttribute('role','group');
    toolbar.setAttribute('aria-label','Zoom the B-R syntax tree');
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
function articleFor(lesson) { return articleLessons[lesson.lesson_id] ?? foundationsArticle(lesson); }
function currentLesson() { return course.lessons.find(l => l.lesson_id===active); }
function progressFor(lesson) { return store.records[lessonKey(lesson)] || emptyProgress(); }
async function act(event, afterSave) {
  if (busy) return;const token=generation;const focused=document.activeElement;const focusName=focused?.name,focusValue=focused?.value;let saved;busy=true;render();
  try { const result=await store.act(currentLesson(),event);if(token!==generation){busy=false;return;}saved=progressFor(currentLesson());notice=result.earned ? (store.status === 'Synced to your account'
      ? 'Lesson complete. 15 lesson XP awarded for this content version.'
      : 'Lesson complete. 15 lesson XP awarded on this device. Verified account XP requires account sync.') : ''; }
  catch(error) { if(token!==generation){busy=false;return;}notice=error.message; }
  busy=false;render();
  if (saved && afterSave) { afterSave(saved); return; }
  if(event.type==='answer' && focusName) {
    const response = host.querySelector(`input[name="${CSS.escape(focusName)}"][value="${focusValue}"]`);
    (response || host.querySelector('.constituent-pre-test-status'))?.focus();
  }
  else { const h=host.querySelector('.lesson-stage-body h2');if(h){h.tabIndex=-1;h.focus();} }
}
function selectLesson(id) {
  active = id;
  step = 0;
  notice = '';
  reviewStage = id && progressFor(currentLesson()).completed_at ? 0 : null;
  practiceResponses = null;
  if (id && articleFor(currentLesson())) {
    const progress = progressFor(currentLesson());
    articlePage = progress.completed_at ? 0 : progress.stage >= 3 ? 5 : progress.stage;
  }
}
function openLesson(id) {
  selectLesson(id);
  render();
  host.scrollTop = 0;
  host.querySelector('h1')?.focus({ preventScroll: true });
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
  overview.append(
    el('h2', 'Overall progress'),
    el('p', `${completed} / ${course.lessons.length} lessons completed · ${lessonXp(store.records)} lesson XP`, 'lesson-total'),
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
      const status = progress.completed_at ? 'Completed' : `Part ${progress.stage + 1} of ${STAGES.length}`;
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
    const completedStages = STAGES.filter(stage => progress.visited.includes(stage)).length;
    const started = completedStages > 0 || Object.keys(progress.responses).length > 0;
    const chapter = lesson.track === 'foundations' ? `Chapter ${lesson.chapter}` : `Cambridge · Chapter ${lesson.chapter}`;
    const card = el('article', undefined, 'curriculum-card lesson-module');
    card.append(
      el('p', chapter, 'lesson-eyebrow'),
      el('h2', lesson.title),
    );
    const description = course.module_descriptions?.[lesson.lesson_id];
    if (description) card.append(el('p', description, 'lesson-module-description'));
    const objective = el('p', undefined, 'lesson-module-objective');
    objective.append(el('strong', 'Learning objective'), ' ', lesson.outcomes[0].text);
    card.append(objective);
    const prerequisites = lesson.prerequisites.filter(pr => !store.records[lessonKey(pr)]?.completed_at);
    if (prerequisites.length) {
      const names = prerequisites.map(pr => course.lessons.find(l => l.lesson_id === pr.lesson_id).title);
      card.append(el('p', `Complete ${names.join(', ')} before finishing this lesson. You can start reading now.`, 'lesson-prerequisite'));
    }

    const footer = el('div', undefined, 'lesson-module-footer');
    const meter = el('div', undefined, 'lesson-module-progress');
    meter.append(el('p', `${completedStages} of ${STAGES.length} stages completed`),
      progressBar(completedStages, STAGES.length, `${lesson.title} progress`));
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

function appendWorkedTree(aside, worked, { focusId, blank = null, comparisonTree = null, inline = false }) {
  const evidence=el('details',undefined,'lesson-shared-evidence');
  evidence.dataset.xai7Lesson = '';
  const title=el('summary','Explanation');
  const slot=el('div',undefined,'lesson-unified-evidence');
  evidence.append(title,slot);
  let requestVersion=0;
  let selected = focusId;
  const selectedWords = el('p', undefined, 'constituent-selection');
  selectedWords.setAttribute('aria-live', 'polite');
  function describeSelection(node, id) {
    if (node.id === id) {
      const [start, end] = node.token_span || [];
      if (Number.isInteger(start) && Number.isInteger(end)) {
        selectedWords.replaceChildren('Selected words: ');
        worked.tree.tokens.forEach((token, index) => {
          if (index) selectedWords.append(' ');
          selectedWords.append(index >= start && index < end ? el('mark', token.text) : token.text);
        });
      }
    } else {
      for (const child of node.children || []) describeSelection(child, id);
    }
  }
  const inspect=async (nodeId, feature=null) => {
    selected=nodeId;
    if (inline) {
      selectedWords.replaceChildren();
      describeSelection(worked.tree.root, nodeId);
      for (const item of canvas.querySelectorAll('svg [data-node-id]')) {
        const isSelected = item.dataset.nodeId === nodeId;
        item.toggleAttribute('data-constituent-selected', isSelected);
        if (!isSelected) item.classList.remove('lesson-tree-focus');
      }
    }
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
    traceBranches: Boolean(comparisonTree),
  });
  if (inline) {
    if (selected) describeSelection(worked.tree.root, selected);
    canvas.append(selectedWords);
  } else {
    aside.append(el('p', worked.origin, 'lesson-origin'));
    if (selected) aside.append(button('Inspect highlighted tree position', () => inspect(selected)));
  }
  evidence.addEventListener('toggle',()=>{if(evidence.open&&!slot.childElementCount&&selected)inspect(selected);});
  aside.append(evidence);
  return canvas;
}

function showArticlePage(page) {
  articlePage = page;
  render();
  host.scrollTop = 0;
  host.querySelector('.lesson-stage-body h2')?.focus({ preventScroll: true });
}

function articleScreen(lesson, p, article) {
  const page = articlePage;
  const reviewing = Boolean(p.completed_at);
  const body = el('article', undefined, 'lesson-stage-body');
  const heading = el('h2', article.headings[page]);
  heading.id = 'constituent-page-title';
  body.setAttribute('aria-labelledby', heading.id);
  heading.tabIndex = -1;
  body.append(heading);
  const layout = el('div', undefined, 'constituent-page');
  layout.append(body);
  host.append(layout);

  article.teach(body, page, {
    el, button, lesson,
    openBuilderPractice: options.onBuilderPractice,
    mountBuilder: (stage, exercise) => {
      const editor = options.mountBuilder(stage, exercise);
      embeddedBuilderCleanup = editor.destroy;
      return editor;
    },
    showDiagram: (figure, tree, options) => {
      clearLessonDiagram(figure);
      return mountLessonCanvas(figure, tree, options);
    },
    showWorkedTree: (figure, focusId) => {
      clearLessonDiagram(figure);
      return appendWorkedTree(figure, lesson.worked_example, { focusId, inline: true });
    },
    showComparisonTree: (figure, flatTree) => {
      clearLessonDiagram(figure);
      if (flatTree) return mountLessonCanvas(figure, flatTree, {
        focusId: flatTree.root.id, wordBaseline: 2, traceBranches: true,
      });
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
      return appendWorkedTree(figure, worked, { focusId, comparisonTree: { ...worked.tree, root }, inline: true });
    },
  });

  const diagram = body.querySelector('.constituent-diagram');
  if (diagram) diagram.after(lessonNotation(lesson, page, el));

  if (page === 0) {
    const preTest = el('section', undefined, 'lesson-assessment constituent-pre-test');
    const title = el('h3', 'Pre-test');
    title.id = 'lesson-pre-test-title';
    preTest.setAttribute('aria-labelledby', title.id);
    preTest.append(title, el('p', 'Answer this short question before you begin. Your answer is unscored, and any choice lets you continue.'));
    if (p.responses.predict) {
      // Earlier versions used a different prompt with the same saved response key.
      // Acknowledge submission without applying an older choice to the new prompt.
      const recorded = el('p', 'Response recorded.', 'constituent-pre-test-status');
      recorded.setAttribute('role', 'status');
      recorded.tabIndex = -1;
      preTest.append(recorded);
    } else {
      const { prompt, options } = article.preTest ?? lesson.predict;
      preTest.append(question(lesson, 'predict', p, reviewing, undefined, { prompt, options }));
    }
    body.append(preTest);
  }

  if (page === 4) body.append(lessonReferences(lesson));

  const actions = el('div', undefined, 'lesson-page-actions constituent-actions');
  if (page > 0) {
    const previous = button('← Previous', () => showArticlePage(page - 1));
    previous.disabled = busy;
    actions.append(previous);
  }

  if (page < 5) {
    const next = button(page === 4 ? 'Start post-test' : 'Next →', () => {
      // The worked example and remaining reading pages share the existing worked stage.
      // The three saved answer stages begin together at the post-test.
      const checkpoint = page === 4 ? 2 : page < 2 ? page : null;
      const advancesProgress = !reviewing && p.stage === checkpoint;
      if (advancesProgress) {
        act({ type: 'advance' }, result => {
          if (result.stage !== p.stage) showArticlePage(page + 1);
        });
      } else {
        showArticlePage(page + 1);
      }
    }, 'lesson-primary');
    next.disabled = busy || (page === 0 && !p.responses.predict && !reviewing);
    actions.append(next);
  } else {
    const practice = practiceResponses !== null;
    const key = STAGES[p.stage];
    const keys = reviewing ? postTestKeys : [key];
    const postTest = el('section', undefined, 'lesson-assessment');
    postTest.setAttribute('aria-label', 'Post-test questions');
    postTest.append(el('p', practice ? 'Try the chapter questions again. This is a practice attempt.'
      : reviewing ? 'Review your answers and feedback from the completed chapter.'
        : article.postTestIntro));
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
    if (reviewing) {
      if (!practice) {
        actions.append(button('Retake post-test', () => {
          practiceResponses = {};
          showArticlePage(5);
        }));
      }
      actions.append(button(practice ? 'Finish practice' : 'Finish review', () => {
        if (!practice) { showCatalog(); return; }
        practiceResponses = null;
        showArticlePage(5);
      }, 'lesson-primary'));
      if (practice) {
        actions.lastElementChild.disabled = !postTestKeys.every(item => practiceResponses[item]);
      }
    } else {
      const next = button(busy ? 'Saving…' : key === 'exit' ? 'Complete lesson' : 'Next question →', () => {
        act({ type: 'advance' }, result => {
          if (result.completed_at) showArticlePage(5);
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
      actions.append(next);
    }
    if (key === 'exit' || reviewing) article.review?.(body, { el });
  }
  layout.append(actions);
}

function lessonScreen() {
  const lesson = currentLesson(), p = progressFor(lesson);
  const stage = reviewStage ?? p.stage, key = STAGES[stage];
  const reviewing = reviewStage !== null;
  const article = articleFor(lesson);
  const chapter = article ? `Chapter ${lesson.chapter}` : lesson.track === 'foundations' ? `B-R · Chapter ${lesson.chapter}` : `Cambridge · Chapter ${lesson.chapter}`;
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
  aside.append(el('h2', worked.tree ? 'Worked B-R example' : 'Worked example'),el('p',worked.sentence,'lesson-example-sentence'));
  if (worked.tree) appendWorkedTree(aside, worked, {
    focusId: key === 'guided' ? lesson.guided.build_target?.node_id : worked.steps[step]?.focus_node_id,
    blank: key === 'guided' && p.responses.guided !== lesson.guided.answer ? lesson.guided.build_target : null,
  });
  else aside.append(el('p',lesson.chapter===11 && lesson.track==='foundations' ? 'This closing chapter is a text-only synthesis. No new tree convention or gradable tree is introduced.' : 'Use the text contrast without renaming B-R tree categories.'), el('p', worked.origin, 'lesson-origin'));
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
  const footer=el('footer',undefined,'lesson-save-status');footer.setAttribute('aria-live','polite');if(notice)footer.append(el('p',notice));footer.append(el('p',store.status));
  if(options.userId?.()) footer.append(button('Retry account sync',async()=>{await store.retry();render();}));
  host.append(footer);host.scrollTop=scroll;
}
export function initLessons(config = {}) {
  options=config;
  host=document.getElementById('curriculumView');
  if(!host) {host=el('section',undefined,'curriculum-view');host.id='curriculumView';host.hidden=true;host.setAttribute('aria-label','Lessons and curriculum');document.body.append(host);}
  subscribeAuthState(()=>{generation+=1;store=null;active=null;busy=false;if(!host.hidden)openLessons();});
  const route = () => {
    const match=/^#lesson\/([A-Za-z0-9-]+)$/.exec(location.hash);
    const legacy={NP:'br-07',ADJP:'br-03',VP:'br-04',S:'br-02',SBAR:'br-08',SBARQ:'br-09'};
    if(match)options.onNavigate?.(legacy[match[1]] || match[1].toLowerCase());
  };
  window.addEventListener('hashchange',route);
  if(/^#lesson\//.test(location.hash))queueMicrotask(route);
}
export async function openLessons(id=null, { workedExample = false } = {}) {
  lastFocus=document.activeElement;host.hidden=false;document.body.classList.add('curriculum-open');
  clearLessonCanvases();
  showCurriculumState(host, { message: 'Loading reviewed lessons…' });
  const token=++generation;
  try {
    course ||= validateCourse(await (await fetch('/content/lessons/course.json',{cache:'no-cache'})).json());
    if(!store) {
      let storage;try{storage=localStorage;}catch{storage=null;}
      const next=createLessonStore(course,{storage,userId:options.userId?.() || 'guest',client:options.client?.()});
      await next.load();if(token!==generation)return;store=next;
    }
    if(token!==generation)return;
    host.setAttribute('aria-busy','false');
    selectLesson(course.lessons.some(l=>l.lesson_id===id) ? id : null);
    document.querySelector('#appSidebarBackdrop')?.classList.remove('active');
    if (workedExample && active && articleFor(currentLesson())) {
      const progress = progressFor(currentLesson());
      if (progress.completed_at || progress.stage >= 2) {
        showArticlePage(2);
        return;
      }
    }
    render();
    const heading=host.querySelector('h1');if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});host.scrollTop=0;}
  } catch {
    if (token === generation) showCurriculumState(host, {
      title: 'Lessons unavailable',
      message: 'The lesson catalog could not be loaded or its source review is incomplete.',
      retry: () => openLessons(id, { workedExample }), back: options.onExit,
    });
  }
}
export function closeLessons() { generation+=1;clearLessonCanvases();if(host){host.hidden=true;host.replaceChildren();}document.body.classList.remove('curriculum-open');active=null;notice='';if(lastFocus?.isConnected)lastFocus.focus(); }
