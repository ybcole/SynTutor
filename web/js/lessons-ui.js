import { showCurriculumState } from './curriculum-state.js';
import { STAGES, STAGE_TITLES, validateCourse, lessonKey, emptyProgress, canAdvance, lessonXp } from './lesson-core.js';
import { createLessonStore } from './lesson-progress.js';
import { requestEvidence, renderEvidence } from './explanation-evidence.js';
import { subscribeAuthState } from './auth.js';

let options = {}, course, store, host, active = null, step = 0, track = 'foundations', busy = false, notice = '', generation = 0, lastFocus = null;
const el = (tag, text, cls) => { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (cls) node.className = cls; return node; };
function button(text, run, cls = '') { const b = el('button',text,cls); b.type = 'button'; b.addEventListener('click',run); return b; }
function sourceList(ids, parent) {
  const details = el('details',undefined,'lesson-sources'); details.append(el('summary','Sources and review'));
  for (const id of [...new Set(ids)]) {
    const source = course.sources.find(s => s.id === id); if (!source) continue;
    details.append(el('p',`${source.book === 'B-R' ? 'Burton-Roberts' : 'Cambridge'} · ${source.title} · ${source.edition} · Ch ${source.chapter} · printed p. ${source.printed_page}`));
  }
  details.append(el('p','Source-checked by AI against the cited pages; no human instructor sign-off is claimed.'));
  parent.append(details);
}
const SVG_NS = 'http://www.w3.org/2000/svg';
function svgNode(name, attrs = {}) { const n = document.createElementNS(SVG_NS,name); for (const [k,v] of Object.entries(attrs)) n.setAttribute(k,v); return n; }
// Read-only canonical trees plus a constrained fill-in target for guided practice.
// Advanced structures never pass through the parser or the legacy Builder bridge.
export function renderLessonTree(envelope, {
  focusId = null, blank = null, stackFeatures = false, displayLabels = null,
  interactive = false, onSelectNode = null, zoomControls = false,
} = {}) {
  const wrap = el('div',undefined,'lesson-tree-wrap');
  const root = envelope.root;
  const hint=el('p','Scroll sideways to inspect the whole tree, or open its text view.','lesson-tree-hint');wrap.append(hint);wrap.tabIndex=0;wrap.setAttribute('aria-label','Scrollable B-R tree');
  function label(node, withFeatures = true) {
    const master = displayLabels?.[node.id];
    if (master) return withFeatures ? master.join(' ') : master[0] || '';
    if (node.gap) return node.index === undefined ? '•' : `• (${node.index})`;
    const vpSourceRef = node.label === 'VP' ? [node.ref, ...(node.source_refs || [])].find(ref => typeof ref === 'string' && /^VP[1-9][0-9]*$/.test(ref)) : null;
    const numberedVP = vpSourceRef ? 'VP' + vpSourceRef.slice(2).replace(/[0-9]/g, digit => '₀₁₂₃₄₅₆₇₈₉'[Number(digit)]) : null;
    const name=node.label === 'AUX' ? '' : node.label === 'S-bar' ? 'S′' : node.label === 'S-dbar' ? 'S″' : node.unlabelled ? '' : numberedVP || node.label || node.word;
    return `${name || ''}${withFeatures && node.features?.length ? ` [${node.features.join(', ')}]` : ''}${node.empty ? ' (empty)' : ''}`;
  }
  const featureRows = node => displayLabels?.[node.id]
    ? displayLabels[node.id].slice(1)
    : stackFeatures ? (node.features || []).map(feature => `[${feature}]`) : [];
  const measure = document.createElement('canvas').getContext('2d');
  measure.font = '15px system-ui, sans-serif';
  const gap = 18;
  const widths = new Map();
  function widthOf(node) {
    if (widths.has(node)) return widths.get(node);
    const children = node.children || [];
    const ownLabel = blank && blank.node_id === node.id && blank.field === 'feature'
      ? label(node) + ' [?]' : label(node, !stackFeatures && !displayLabels);
    const width = Math.max(node.id === focusId ? 122 : 56,
      measure.measureText(ownLabel).width + 28,
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
      const target = place(child, cursor, y + 72 + featureRows(node).length * 18);
      edges.push([position, target]);
      cursor += widthOf(child) + gap;
    }
    return position;
  }
  const width=widthOf(root); place(root,0,35);
  const height=Math.max(...positions.map(p=>p.y + featureRows(p.node).length * 18 + (p.node.triangle ? 80 : 35)));
  const svg=svgNode('svg',{viewBox:`0 0 ${width} ${height}`,width,height,role:'img','aria-label':`B-R tree for ${envelope.sentence}`});
  for (const [a,b] of edges) svg.append(svgNode('line',{x1:a.x,y1:a.y+12+featureRows(a.node).length*18,x2:b.x,y2:b.y-18,class:'lesson-branch'}));
  for (const {node,x,y} of positions) {
    const g=svgNode('g',{'data-node-id':node.id || '',class:node.id===focusId ? 'lesson-tree-focus' : ''});
    if (node.id===focusId) g.append(svgNode('rect',{x:x-55,y:y-20,width:110,height:40,rx:9}));
    const t=svgNode('text',{x,y,'text-anchor':'middle'});
    t.textContent=blank && blank.node_id===node.id ? (blank.field==='feature' ? `${node.label === 'AUX' ? '' : node.label} [?]` : '?') : label(node, !stackFeatures && !displayLabels);g.append(t);
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
      const choose = () => onSelectNode(node.id, null);
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
        row.addEventListener('click', event => {
          event.stopPropagation(); onSelectNode(node.id,row.textContent);
        });
        row.addEventListener('keydown', event => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.stopPropagation(); event.preventDefault();
            onSelectNode(node.id,row.textContent);
          }
        });
      }
    }
    svg.append(g);
  }
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
  const text=el('details',undefined,'lesson-tree-text');text.append(el('summary','Read the tree as text'));
  function list(node) {
    const item = el('li');
    const name = label(node) || '△';
    const description = node.words ? `${name} — ${node.words.join(' ')}` : name;
    if (interactive && node.id) {
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
function currentLesson() { return course.lessons.find(l => l.lesson_id===active); }
function progressFor(lesson) { return store.records[lessonKey(lesson)] || emptyProgress(); }
async function act(event) {
  if (busy) return;const token=generation;const focused=document.activeElement;const focusName=focused?.name,focusValue=focused?.value;busy=true;render();
  try { const result=await store.act(currentLesson(),event);if(token!==generation){busy=false;return;}notice=result.earned ? (store.status === 'Synced to your account'
      ? 'Lesson complete. 15 lesson XP awarded for this content version.'
      : 'Lesson complete. 15 lesson XP awarded on this device. Verified account XP requires account sync.') : ''; }
  catch(error) { if(token!==generation){busy=false;return;}notice=error.message; }
  busy=false;render();
  if(event.type==='answer' && focusName)host.querySelector(`input[name="${CSS.escape(focusName)}"][value="${focusValue}"]`)?.focus();
  else { const h=host.querySelector('.lesson-stage-body h2');if(h){h.tabIndex=-1;h.focus();} }
}
function openLesson(id) { active=id; step=0;notice='';render();host.querySelector('h1')?.focus(); }
function catalog() {
  const header=el('header',undefined,'curriculum-header');header.append(el('p','SOURCE-GROUNDED LEARNING','lesson-eyebrow'),el('h1','Learn the structure. See the reason.'));
  header.append(el('p','Follow the B-R chapter sequence, then explore selected Cambridge insights. Practice is part of each lesson; independent quizzes will arrive separately.','lesson-lead'));
  header.append(el('p',`${course.lessons.filter(l=>progressFor(l).completed_at).length} / ${course.lessons.length} lessons completed · ${lessonXp(store.records)} lesson XP in this course`,'lesson-total'));
  const continuing=course.lessons.find(l=>store.records[lessonKey(l)] && !progressFor(l).completed_at) || course.lessons.find(l=>!progressFor(l).completed_at);
  if (continuing) header.append(button(`Continue: ${continuing.title}`,()=>openLesson(continuing.lesson_id),'lesson-primary'));
  host.append(header);
  const tabs=el('div',undefined,'lesson-track-tabs');tabs.setAttribute('role','group');tabs.setAttribute('aria-label','Learning tracks');
  for (const t of course.tracks) { const b=button(t.title,()=>{track=t.id;render();});b.setAttribute('aria-pressed',String(track===t.id));tabs.append(b); }
  host.append(tabs,el('p',course.tracks.find(t=>t.id===track).description,'lesson-lead'));
  const grid=el('div',undefined,'curriculum-grid');
  for (const lesson of course.lessons.filter(l=>l.track===track)) {
    const card=el('article',undefined,'curriculum-card'),p=progressFor(lesson);
    card.append(el('p',`${lesson.track==='foundations' ? `Chapter ${lesson.chapter}` : 'Companion'} · ${lesson.difficulty} · ${lesson.estimated_minutes} min`,'lesson-eyebrow'),el('h2',lesson.title),el('p',lesson.outcomes[0].text));
    card.append(el('p',p.completed_at ? `Completed · v${lesson.content_version} · 15 XP earned` : `v${lesson.content_version} · ${p.stage ? `Resume ${STAGE_TITLES[p.stage]}` : 'Not started'}`,'lesson-status'));
    if (lesson.prerequisites.length) card.append(el('p',`Prerequisite: ${lesson.prerequisites.map(pr=>course.lessons.find(l=>l.lesson_id===pr.lesson_id)?.title).join(', ')}. Reading is always available.`,'lesson-prerequisite'));
    card.append(button(p.completed_at ? 'Review lesson' : p.stage ? 'Resume lesson' : 'Open lesson',()=>openLesson(lesson.lesson_id),'lesson-open'));
    grid.append(card);
  }
  host.append(grid);
  if (track==='grammar') {
    const planned=el('details',undefined,'lesson-planned');planned.append(el('summary',`${course.planned_modules.length} further topics planned — not published`));
    const list=el('ul');for(const p of course.planned_modules)list.append(el('li',`${p.title}: ${p.reason}`));planned.append(list);host.append(planned);
  }
}
function question(lesson,key,p) {
  const data=lesson[key], section=el('section',undefined,'lesson-question');section.dataset.question=key;
  const field=el('fieldset');field.disabled=busy;field.append(el('legend',data.prompt));
  for (const option of data.options) {
    const label=el('label',undefined,'lesson-option'),radio=el('input');radio.type='radio';radio.name=`${lesson.lesson_id}-${key}`;radio.value=option.id;radio.checked=p.responses[key]===option.id;
    radio.addEventListener('change',()=>act({type:'answer',answer:option.id}));label.append(radio,el('span',option.text));field.append(label);
  }
  section.append(field);
  if (p.responses[key]) { const chosen=data.options.find(o=>o.id===p.responses[key]);section.append(el('p',chosen.feedback,p.responses[key]===data.answer ? 'lesson-feedback correct' : 'lesson-feedback retry')); }
  const hint=el('details');hint.append(el('summary','Need a hint?'),el('p',data.hint));section.append(hint);sourceList(data.source_ids,section);return section;
}
function lessonScreen() {
  const lesson=currentLesson(),p=progressFor(lesson),key=STAGES[p.stage];
  const header=el('header',undefined,'lesson-header');header.append(button('← All lessons',()=>{active=null;notice='';render();}),el('p',`${lesson.track==='foundations' ? `B-R · Chapter ${lesson.chapter}` : 'Cambridge · Companion'} · ${lesson.convention_profile?.version || 'Text-only'} · version ${lesson.content_version}`,'lesson-eyebrow'));
  const h1=el('h1',lesson.title);h1.tabIndex=-1;header.append(h1,el('p',lesson.outcomes[0].text,'lesson-lead'));host.append(header);
  const nav=el('nav',undefined,'lesson-stepper');nav.setAttribute('aria-label','Lesson stages');
  const firstMissing=STAGES.findIndex(s=>!p.visited.includes(s));const max=firstMissing<0 ? 5 : firstMissing;
  STAGE_TITLES.forEach((title,i)=>{const b=button(`${i+1}. ${title}`,()=>act({type:'navigate',stage:i}));b.disabled=busy||i>max;if(i===p.stage)b.setAttribute('aria-current','step');nav.append(b);});host.append(nav);
  const columns=el('div',undefined,'lesson-columns'),body=el('section',undefined,'lesson-stage-body'),aside=el('aside',undefined,'lesson-evidence-card');
  body.append(el('p',`Stage ${p.stage+1} of 6`,'lesson-eyebrow'),el('h2',STAGE_TITLES[p.stage]));
  if (lesson[key]) body.append(question(lesson,key,p));
  if (key==='understand') {
    for (const block of lesson.teaching) { const card=el('section');card.append(el('p',block.text));sourceList(block.source_ids,card);body.append(card); }
    for (const insight of lesson.cambridge_insights) { const card=el('section',undefined,'lesson-insight');card.append(el('h3','Cambridge insight'),el('p',insight.text));sourceList(insight.source_ids,card);body.append(card); }
  }
  const worked=lesson.worked_example;
  aside.append(el('h2',worked.tree ? 'Worked B-R example' : 'Worked example'),el('p',worked.sentence,'lesson-example-sentence'));
  if (worked.tree) {
    const evidence=el('details',undefined,'lesson-shared-evidence');
    evidence.dataset.xai7Lesson = '';
    const title=el('summary','Explanation');
    const slot=el('div',undefined,'lesson-unified-evidence');
    evidence.append(title,slot);
    let requestVersion=0;
    let selected=key==='guided' ? lesson.guided.build_target?.node_id : worked.steps[step]?.focus_node_id;
    let treeView;
    const inspect=async (nodeId, feature=null) => {
      selected=nodeId;
      evidence.open=true;
      const version=++requestVersion;
      slot.replaceChildren(el('p','Explaining this word or phrase…'));
      try {
        const result=await requestEvidence(worked.tree,nodeId);
        if (version!==requestVersion||!slot.isConnected) return;
        renderEvidence(result,slot,{treeRoot:treeView,feature});
      } catch {
        if (version===requestVersion&&slot.isConnected) {
          slot.replaceChildren(el('p','An explanation is not available for this part of the sentence.'));
        }
      }
    };
    treeView=renderLessonTree(worked.tree,{
      focusId:selected,
      blank:key==='guided' && p.responses.guided!==lesson.guided.answer ? lesson.guided.build_target : null,
      interactive:true, onSelectNode:inspect, zoomControls:true, stackFeatures:true,
    });
    aside.append(treeView);
    if (selected) aside.append(button('Inspect highlighted tree position',()=>inspect(selected)));
    evidence.addEventListener('toggle',()=>{if(evidence.open&&!slot.childElementCount&&selected)inspect(selected);});
    aside.append(evidence);
  }
  else aside.append(el('p',lesson.chapter===11 && lesson.track==='foundations' ? 'This closing chapter is a text-only synthesis. No new tree convention or gradable tree is introduced.' : 'Use the text contrast without renaming B-R tree categories.'));
  aside.append(el('p',worked.origin,'lesson-origin'));sourceList(worked.source_ids,aside);
  if(key==='worked') {
    body.append(el('p',`Step ${step+1} of ${worked.steps.length}`),el('p',worked.steps[step].text));
    const steps=el('div',undefined,'lesson-step-controls');const prev=button('Previous step',()=>{step=Math.max(0,step-1);render();});prev.disabled=step===0;
    const next=button('Next step',()=>{step=Math.min(worked.steps.length-1,step+1);render();});next.disabled=step===worked.steps.length-1;steps.append(prev,next);body.append(steps);
  }
  if(key==='guided' && lesson.guided.build_target) body.append(el('p','Fill the highlighted missing label or feature in the worked tree. The complete original returns when your answer matches.','lesson-guide-note'));
  if(key==='predict') body.append(el('p','This is a prediction, not a scored assessment. A wrong first answer does not reduce XP.'));
  const next=button(busy ? 'Saving…' : key==='exit' ? (p.completed_at ? 'Finish review — no extra XP' : 'Complete lesson · 15 XP once') : 'Continue →',()=>act({type:'advance'}),'lesson-primary');
  next.disabled=busy||!canAdvance(lesson,p)||(key==='worked'&&step!==worked.steps.length-1);body.append(next);
  if(p.completed_at) body.append(el('p','Completed for this content version. Reviewing cannot award another 15 XP.','lesson-feedback correct'));
  if(key==='exit' && p.completed_at) {
    const following=course.lessons.find(l=>l.prerequisites.some(pr=>pr.lesson_id===lesson.lesson_id) && !progressFor(l).completed_at);
    if(following)body.append(button(`Next lesson: ${following.title}`,()=>openLesson(following.lesson_id)));
  }
  columns.append(body,aside);host.append(columns);

}
function render() {
  if (!host || host.hidden || !course || !store) return;
  const scroll=host.scrollTop;host.replaceChildren();
  host.append(button('Back to Syntax Generator',()=>options.onExit?.(),'lesson-return'));
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
export async function openLessons(id=null) {
  lastFocus=document.activeElement;host.hidden=false;document.body.classList.add('curriculum-open');
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
    active=course.lessons.some(l=>l.lesson_id===id) ? id : null;step=0;notice='';render();
    const heading=host.querySelector('h1');if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});host.scrollTop=0;}
    document.querySelector('#appSidebarBackdrop')?.classList.remove('active');
  } catch {
    if (token === generation) showCurriculumState(host, {
      title: 'Lessons unavailable',
      message: 'The lesson catalog could not be loaded or its source review is incomplete.',
      retry: () => openLessons(id), back: options.onExit,
    });
  }
}
export function closeLessons() { generation+=1;if(host){host.hidden=true;host.replaceChildren();}document.body.classList.remove('curriculum-open');active=null;notice='';if(lastFocus?.isConnected)lastFocus.focus(); }
