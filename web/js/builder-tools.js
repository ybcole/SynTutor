import {createBuilderSession} from './builder-session.js';
import {builderProfile,NODE,addPhrase,addWordsFromText,addSpecial,connect,disconnect,removeNode,toCanonicalEnvelope,fromCanonicalEnvelope,childrenOf} from './syntax-builder.js';
import {subscribeAuthState} from './auth.js';
const el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
export function createBuilderTools(config){
 let host,session,identity,selected='',course,active=false,message='',hintStep=0,collapsed=false,lessonPractice=null,previousDraft=null,inline=null;
 const snapshot=()=>({version:1,model:config.state.model,profile:config.state.canonicalProfile||builderProfile(),targetId:config.state.targetId||null,view:config.state.view});
 function restore(d){
  config.state.model=d.model;
  config.state.canonicalProfile=d.profile;
  config.state.targetId=d.targetId;
  config.state.view=d.view||{ox:60,oy:60,scale:1};
 }
 function apply(d){restore(d);config.reset();config.refresh();render();}
 function seedPractice(lesson) {
  const tree=lesson.worked_example.tree;
  config.state.model={nodes:{}};
  addWordsFromText(config.state.model,tree.tokens.map(token=>token.text).join(' '),0,240);
  config.state.canonicalProfile=tree.convention_profile;
  config.state.targetId=lesson.lesson_id;
  config.state.view={ox:60,oy:60,scale:1};
  config.reset();
  hintStep=0;
 }
 function initSession(recover){
  identity=config.userId?.()||'guest';
  let storage;try{storage=localStorage;}catch{}
  if(lessonPractice)seedPractice(lessonPractice.lesson);
  if(inline){
   config.state.model=inline.seed();
   config.state.canonicalProfile=builderProfile(1);
   config.state.targetId=null;
   config.state.view={ox:24,oy:20,scale:1};
   config.reset();
  }
  const lessonId=inline?.id||lessonPractice?.lesson.lesson_id;
  const draftIdentity=lessonId?`${identity}:lesson:${lessonId}`:identity;
  session=createBuilderSession({storage,identity:draftIdentity,initial:snapshot()});
  if(recover)apply(session.load());else session.save();
 }
 function mutate(fn){const before=JSON.parse(JSON.stringify(snapshot()));try{fn();config.refresh();record();message='';render();}catch(e){apply(before);message=e.message;updateStatus();}}
 function record(){if(!active||!session)return;if(identity!==(config.userId?.()||'guest'))return;session.record(snapshot());updateStatus();}
 function updateStatus(){const n=host?.querySelector('[data-builder-save]');if(n)n.textContent=message||session?.status||'';}
 function button(text,fn){const b=el('button',text);b.type='button';b.addEventListener('click',fn);return b;}
 function field(name,input){const label=el('label',name);label.append(input);return label;}
 function select(name,options,value){const n=el('select');n.setAttribute('aria-label',name);for(const [v,label] of options){const o=el('option',label);o.value=v;n.append(o);}n.value=value??'';return n;}
 function input(name,value=''){const n=el('input');n.setAttribute('aria-label',name);n.value=value;return n;}
 function render(){
  if(!active||inline)return;const open=host?.querySelector('details[data-edit]')?.open,io=host?.querySelector('[data-builder-json]')?.value||'';
  const practiceOpen=host.querySelector('details[data-practice]')?.open??Boolean(lessonPractice);
  const conventionsOpen=host.querySelector('details[data-conventions]')?.open??false;
  host.replaceChildren();const heading=el('h2','Build a B-R tree');host.append(heading,button(collapsed?'Show editing controls':'Hide editing controls',()=>{collapsed=!collapsed;render();config.fit();}));
  if(lessonPractice)host.append(button('Return to lesson',lessonPractice.onReturn));
  const view=el('div');view.className='builder-tool-actions';view.append(button('Zoom in',()=>config.zoom(1.25)),button('Zoom out',()=>config.zoom(.8)),button('Fit tree',()=>config.fit()),button('Pan left',()=>config.pan(-50,0)),button('Pan right',()=>config.pan(50,0)),button('Pan up',()=>config.pan(0,-50)),button('Pan down',()=>config.pan(0,50)));host.append(view);
  if(collapsed)return;
  if(lessonPractice) {
   const steps=el('ol');
   for(const text of lessonPractice.steps)steps.append(el('li',text));
   host.append(el('h3',`Build “${lessonPractice.lesson.worked_example.sentence}”`),steps);
  }
  const profile=config.state.canonicalProfile||builderProfile();
  host.append(el('p','Edit with the canvas or these keyboard and touch controls. Checking a tree does not establish sentence grammaticality.'));
  const actions=el('div');actions.className='builder-tool-actions';
  const undo=button('Undo',()=>apply(session.undo())),redo=button('Redo',()=>apply(session.redo()));undo.disabled=!session.canUndo;redo.disabled=!session.canRedo;
  actions.append(undo,redo,button('Save draft',()=>{session.save();updateStatus();}),button('Check construction',()=>config.evaluate()));host.append(actions);
  const editor=el('details');editor.dataset.edit='';editor.open=open??true;editor.append(el('summary','Nodes and connections'));
  const nodes=Object.values(config.state.model.nodes),palette=config.palette();
  if(!nodes.some(n=>n.id===selected))selected=nodes[0]?.id||'';
  const list=select('Selected Builder node',[['','Choose a node'],...nodes.map(n=>[n.id,`${n.id}: ${n.kind===NODE.WORD?n.text:n.type}${n.canonicalData?.empty?' ∅':''}`])],selected);
  list.addEventListener('change',()=>{selected=list.value;config.select(selected);render();});editor.append(field('Selected node',list));
  const node=config.state.model.nodes[selected];
  if(node){
   const text=input('Node label or word',node.kind===NODE.WORD?node.text:node.type);editor.append(field('Label or word',text));
   const features=input('Node features',(node.canonicalFeatures||[]).join(', ')),index=input('Node index',node.canonicalIndex??'');
   if(node.kind===NODE.PHRASE)editor.append(field(`Features (${palette.features.join(', ')||'none in this chapter'})`,features));
   if(node.kind!==NODE.WORD&&!node.canonicalData?.empty)editor.append(field('Index (optional)',index));
   editor.append(button('Apply node changes',()=>mutate(()=>{
    if(node.kind===NODE.WORD){if(!text.value.trim())throw Error('Enter a word.');node.text=text.value.trim();}
    else if(node.kind===NODE.PHRASE){if(!palette.labels.includes(text.value))throw Error('Choose a label in this convention.');node.type=text.value;node.canonicalFeatures=features.value.split(',').map(s=>s.trim()).filter(Boolean);if(node.canonicalFeatures.some(f=>!palette.features.includes(f)))throw Error('Feature is not in this convention.');if(node.canonicalTriangle&&node.canonicalFeatures.length)throw Error('Expand the triangle before adding features.');}
    if(node.kind!==NODE.WORD&&!node.canonicalData?.empty){if(index.value!==''&&!/^\d+$/.test(index.value))throw Error('Index must be a non-negative integer.');node.canonicalIndex=index.value===''?null:Number(index.value);}
   })));
   const parents=select('Parent Builder node',[['','No parent'],...nodes.filter(n=>n.kind===NODE.PHRASE&&n.id!==node.id).map(n=>[n.id,`${n.id}: ${n.type}`])],node.parent||'');editor.append(field('Parent',parents));
   editor.append(button('Connect to parent',()=>mutate(()=>{if(!parents.value)disconnect(config.state.model,node.id);else if(!connect(config.state.model,parents.value,node.id))throw Error('That connection would create a cycle or attach under a terminal/triangle.');})),button('Delete selected node',()=>mutate(()=>removeNode(config.state.model,node.id))));
   const position=input('Horizontal order',String(node.x));position.type='number';editor.append(field('Horizontal position / sibling order',position),button('Move node',()=>mutate(()=>{if(!Number.isFinite(Number(position.value)))throw Error('Enter a number');node.x=Number(position.value);})));
   if(node.kind===NODE.PHRASE&&!node.canonicalData?.unlabelled)editor.append(button(node.canonicalTriangle?'Expand triangle':'Collapse to triangle',()=>mutate(()=>{if(!node.canonicalTriangle&&node.canonicalFeatures?.length)throw Error('Remove features before collapsing this node.');if(!node.canonicalTriangle&&childrenOf(config.state.model,node.id).some(n=>n.kind!==NODE.WORD))throw Error('Connect only overt words before collapsing.');node.canonicalTriangle=!node.canonicalTriangle;})));
   editor.append(button('Explain selected node',()=>config.select(node.id,true)));
  }
  const phrase=select('New B-R category',palette.labels.map(l=>[l,l]),palette.labels.includes('NP')?'NP':palette.labels[0]);editor.append(field('New category',phrase),button('Add category',()=>mutate(()=>{selected=addPhrase(config.state.model,phrase.value,nodes.length*45,60).id;})));
  const words=input('New words');editor.append(field('New words',words),button('Add words',()=>mutate(()=>{const added=addWordsFromText(config.state.model,words.value,nodes.length*80,240);selected=added.at(-1)?.id||selected;})));
  const special=[...(profile.chapter>=9?[['gap','Indexed gap']]:[]),...(profile.chapter>=5?[['E','Elided E']]:[]),...(profile.chapter>=7?[['DET','Empty DET']]:[]),...(profile.chapter>=9?[['C1','Empty C1']]:[])];
  if(special.length){const empty=select('New empty position',special,special[0][0]);editor.append(field('Zero-word position',empty),button('Add empty position',()=>mutate(()=>{selected=addSpecial(config.state.model,empty.value,nodes.length*80,240).id;})));}
  host.append(editor);
  const exercises=el('details');exercises.append(el('summary','Reviewed construction practice'));
  exercises.dataset.practice='';
  exercises.open=practiceOpen;
  const units=lessonPractice?[lessonPractice.lesson]:course?.lessons.filter(l=>l.worked_example?.tree&&l.lesson_id!=='br-01');
  if(units){
   if(lessonPractice){
    exercises.append(button('Restart construction practice',()=>mutate(()=>seedPractice(lessonPractice.lesson))));
   }else{
    const choice=select('Builder exercise',[['','Choose an exercise'],...units.map(l=>[l.lesson_id,l.title])],config.state.targetId||'');
    exercises.append(choice,button('Start construction practice',()=>mutate(()=>{
     const lesson=units.find(l=>l.lesson_id===choice.value);
     if(!lesson)throw Error('Choose an exercise');
     seedPractice(lesson);
    })));
   }
   const target=units.find(l=>l.lesson_id===config.state.targetId);
   if(target)exercises.append(el('p',`Target: ${target.title} — ${target.worked_example.tree.sentence}`),button('Next hint',()=>{
    const steps=target.worked_example.steps;
    const step=steps[Math.min(hintStep++,steps.length-1)];
    message=step.instruction||step.text||step.explanation||step.caption||JSON.stringify(step);
    updateStatus();
   }),button('Show model tree',()=>config.showModel(target.worked_example.tree)),button('Load model for exploration',()=>mutate(()=>{
    config.state.model=fromCanonicalEnvelope(target.worked_example.tree);
    config.reset();
   })));
  }else exercises.append(el('p','Loading reviewed exercises…'));
  host.append(exercises);
  const conventions=el('details');
  conventions.dataset.conventions='';
  conventions.open=conventionsOpen;
  conventions.append(el('summary','Advanced tree conventions'));
  const profiles=[['FINAL','Free construction · FINAL-D1'],...Array.from({length:10},(_,i)=>[String(i+1),`Chapter ${i+1} · V${i+1}${i===6?' core':''}`]),['7D','Chapter 7 · Appendix D1']];
  const pick=select('B-R convention',profiles,profile.version==='FINAL'?'FINAL':profile.appendix_nom?'7D':String(profile.chapter));
  pick.addEventListener('change',()=>mutate(()=>{
   config.state.canonicalProfile=builderProfile(pick.value==='FINAL'?null:parseInt(pick.value),pick.value==='7D');
   config.state.targetId=null;
  }));
  conventions.append(field('Convention',pick));
  if(config.state.targetId)conventions.append(el('p','Changing conventions ends this exercise and keeps the tree on the canvas.'));
  host.append(conventions);
  const interchange=el('details');interchange.append(el('summary','Canonical JSON, movement and alternatives'));const json=el('textarea');json.dataset.builderJson='';json.setAttribute('aria-label','Canonical Builder JSON');json.value=io;json.rows=7;json.maxLength=240000;
  interchange.append(el('p','Export/import the shared canonical envelope. Advanced movement, indices, empty positions and accepted-alternative metadata are preserved; imported source claims do not become authority.'),json,
   button('Export canonical JSON',()=>{try{json.value=JSON.stringify(toCanonicalEnvelope(config.state.model,profile),null,2);}catch(e){message=e.message;updateStatus();}}),
   button('Import canonical JSON',async()=>{message='Checking import…';updateStatus();try{const tree=JSON.parse(json.value),before=JSON.stringify(snapshot()),account=identity;await config.validateImport(tree);if(!active||account!==identity||before!==JSON.stringify(snapshot()))throw Error('Construction changed during import; try again');const model=fromCanonicalEnvelope(tree);mutate(()=>{config.state.model=model;config.state.canonicalProfile=tree.convention_profile;config.state.targetId=null;config.reset();});}catch(e){message=`Import failed: ${e.message}. Current work retained.`;updateStatus();}}));host.append(interchange);
  appendStatus();
 }
 function appendStatus(){
  const status=el('p');status.dataset.builderSave='';status.setAttribute('role','status');host.append(status);updateStatus();
 }
 // Duplicate same-account auth notifications can arrive after a user edit.
 // Only a real identity transition may swap/restore the account draft.
 subscribeAuthState(()=>{
  if(!active)return;
  const nextIdentity=config.userId?.()||'guest';
  if(nextIdentity===identity)return;
  config.state.model={nodes:{}};
  config.state.canonicalProfile=builderProfile();
  config.state.targetId=null;
  if(lessonPractice||inline)previousDraft=snapshot();
  config.reset();initSession(true);render();
 });
 return {
 open({recover=true,practice=null,embedded=null}={}){
  active=true;lessonPractice=practice;inline=embedded;
  previousDraft=practice||inline?snapshot():null;
  if(practice||inline)collapsed=false;
  message='';hintStep=0;
  if(inline){
   if(host)host.hidden=true;
   initSession(recover);
   config.fit();
   return;
  }
  if(!host){
   host=el('section');host.id='builderTools';
   host.setAttribute('aria-label','Accessible Builder controls');
  }
  document.querySelector('.canvas-stage').append(host);
  host.hidden=false;host.replaceChildren();initSession(recover);render();config.fit();
  if(practice)return;
  fetch('/content/lessons/course.json').then(r=>r.json()).then(data=>{course=data;render();}).catch(()=>{
   message='Reviewed exercises unavailable; free construction remains available.';updateStatus();
  });
 },
 close(){
  record();active=false;if(previousDraft)restore(previousDraft);
  previousDraft=null;lessonPractice=null;inline=null;if(host)host.hidden=true;
 },
 record,render,select(id){selected=id;render();},
 undo(){if(session)apply(session.undo());},redo(){if(session)apply(session.redo());}};
}
