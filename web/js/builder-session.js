import {builderProfile} from './syntax-builder.js';
// Local draft recovery is separate from lessons, assessments and trusted XP.
const clone=x=>JSON.parse(JSON.stringify(x));
export function validateDraft(draft){
 if(draft?.version!==1||!draft.model||!draft.profile||!Number.isInteger(draft.profile.chapter)||draft.profile.chapter<1||draft.profile.chapter>10)throw Error('Invalid Builder draft');
 const expected=builderProfile(draft.profile.version==='FINAL'?null:draft.profile.chapter,draft.profile.appendix_nom===true);
 if(typeof draft.profile.version!=='string'||Object.keys(draft.profile).some(k=>!Object.hasOwn(expected,k))||Object.entries(draft.profile).some(([k,v])=>expected[k]!==v)||(draft.profile.version==='FINAL'&&draft.profile.appendix_nom!==true))throw Error('Invalid draft convention');
 const nodes=Object.values(draft.model.nodes||{});if(nodes.length>500)throw Error('Draft exceeds 500 nodes');
 for(const [id,n] of Object.entries(draft.model.nodes||{})){
  if(!n||id!==n.id||['__proto__','prototype','constructor'].includes(id)||!['word','phrase','special'].includes(n.kind)||!Number.isFinite(n.x)||!Number.isFinite(n.y)||typeof n.text!=='string'||typeof n.type!=='string'||n.text.length>10000)throw Error('Invalid draft node');
  if(n.parent&&!Object.hasOwn(draft.model.nodes,n.parent))throw Error('Draft contains a missing parent');
  const seen=new Set([id]);let cur=n;while(cur.parent){if(seen.has(cur.parent))throw Error('Draft contains a cycle');seen.add(cur.parent);cur=draft.model.nodes[cur.parent];}
 }
 return draft;
}
export function createBuilderSession({storage=null,identity='guest',initial}){
 const key=`syntutor:builder:v1:${identity}`;let history=[clone(initial)],position=0,status='Saved on this device';
 function save(){try{if(!storage)throw Error();storage.setItem(key,JSON.stringify(history[position]));status='Saved on this device';}catch{status='Draft storage unavailable; export your work before closing.';}}
 return {
  get status(){return status;},get current(){return clone(history[position]);},get canUndo(){return position>0;},get canRedo(){return position<history.length-1;},
  load(){try{const raw=storage?.getItem(key);if(raw){if(raw.length>2000000)throw Error();history=[validateDraft(JSON.parse(raw))];position=0;}}catch{status='Saved draft could not be recovered; your new work is unchanged.';}return this.current;},
  record(value){validateDraft(value);if(JSON.stringify(value)===JSON.stringify(history[position]))return;history=history.slice(0,position+1);history.push(clone(value));if(history.length>40)history.shift();position=history.length-1;save();},
  undo(){if(position>0){position--;save();}return this.current;},redo(){if(position<history.length-1){position++;save();}return this.current;},save,
 };
}
