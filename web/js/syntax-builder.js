// Syntax Builder core: a free-form node-graph model for building syntax trees
// by hand. Unlike SynTutor's read-only tree, here the learner arranges nodes on
// a canvas: word boxes they type, and phrase boxes (NP, VP, S, ...) they create
// from a right-click menu. Phrase nodes expose a small connector dot; dragging
// from a dot draws a link that attaches a word or another phrase as a child.
//
// The model is DOM-free so it can be unit-tested and reused by the Matrix Quiz
// (which asks the learner to rebuild SynTutor's tree for a target sentence and
// then compares the result against the gold parse).

// The visible palette comes from the approved canonical validator inventory.
import INVENTORY from './builder-inventory.js';
export function builderProfile(chapter=null,appendix=false){
 if(chapter===null)return {chapter:10,version:'FINAL',appendix_nom:true,profile_id:'FINAL-D1'};
 if(!Number.isInteger(chapter)||chapter<1||chapter>10)throw Error('Chapter must be 1–10');
 return chapter===7?{chapter,version:'V7',appendix_nom:appendix,profile_id:appendix?'V7-APPENDIX-D1':'V7-CORE'}:{chapter,version:`V${chapter}`,profile_id:`V${chapter}`};
}
export function paletteFor(profile=builderProfile()){
 const chapter=profile.chapter;
 const allowed=(label,intro)=>{
  if(intro>chapter)return false;
  // Chapter 1's pedagogical placeholders are not mature B-R syntax
  // categories; later profiles must not suggest them as ordinary nodes.
  if(chapter>1 && (label==='Sentence'||label==='Phrase'))return false;
  if(chapter>3 && label==='PHRASE')return false;
  return true;
 };
 return {labels:Object.entries(INVENTORY.labels).filter(([label,intro])=>allowed(label,intro)).map(([label])=>label),
  features:Object.entries(INVENTORY.features).filter(([,intro])=>intro<=chapter).map(([feature])=>feature)};
}
export const PHRASE_NODE_TYPES=Object.keys(INVENTORY.labels);
export const POS_TYPES=[]; // Penn POS tags are not canonical B-R categories.
export const NODE_TYPE_GROUPS=[{name:'B-R categories',types:PHRASE_NODE_TYPES}];

export const NODE = { WORD: 'word', PHRASE: 'phrase', SPECIAL: 'special' };

let counter = 0;
export function nextId() {
  counter += 1;
  return `n${counter}`;
}
export function resetIds() {
  counter = 0;
}

// Default box sizes; the UI overrides with real text measurement.
const WORD_W = 84;
const PHRASE_W = 58;
const NODE_H = 32;
const DOT_R = 5;

export function createModel() {
  return { nodes: {}, counter: 0 };
}

function put(model, node) {
  while(model.nodes[node.id])node.id=nextId();
  model.nodes[node.id] = node;
  return node;
}

export function addWord(model, text, x, y) {
  const t = String(text || '').trim();
  return put(model, {
    id: nextId(), kind: NODE.WORD, type: 'word', text: t,
    x, y, w: WORD_W, h: NODE_H, parent: null,
    valid: true, suggestion: null, tag: null,
  });
}

export function addPhrase(model, type, x, y) {
  return put(model, {
    id: nextId(), kind: NODE.PHRASE, type: type || 'NP', text: '',
    x, y, w: PHRASE_W, h: NODE_H, parent: null,
  });
}

// Split free text into tokens the way SynTutor's tokenizer would (words,
// numbers, and single punctuation marks kept separate).
export function tokenise(text) {
  return (String(text || '').match(/[\p{L}\p{N}_]+(?:['’][\p{L}\p{N}_]+)*|[^\p{L}\p{N}_\s]/gu)) || [];
}

// Create one word node per token, laid out in a row starting at (x, y).
export function addWordsFromText(model, text, x, y, gap = 12) {
  const toks = tokenise(text);
  const made = [];
  let cursor = x;
  for (const tok of toks) {
    const n = addWord(model, tok, cursor, y);
    made.push(n);
    cursor += n.w + gap;
  }
  return made;
}

export function moveNode(model, id, x, y) {
  const n = model.nodes[id];
  if (!n) return null;
  n.x = x;
  n.y = y;
  return n;
}

// The sentence the canvas currently spells out: every word node on it, read
// left to right by its X position and joined with single spaces. This is what
// the upper-right input panel mirrors while the learner builds, so the two
// surfaces never drift apart.
export function getSentenceFromLeaves(model) {
  const leaves = Object.values(model?.nodes || {})
    .filter((n) => n && (n.kind === NODE.WORD || n.type === 'word') && !n.canonicalData?.elided)
    .sort((a, b) => (a.x || 0) - (b.x || 0));
  return leaves
    .map((n) => String(n.text ?? n.word ?? '').trim())
    .filter(Boolean)
    .join(' ');
}

export function setType(model, id, type) {
  const n = model.nodes[id];
  if (!n) return null;
  n.type = type;
  return n;
}

export function removeNode(model, id) {
  const n = model.nodes[id];
  if (!n) return false;
  // Detach children (they become roots again).
  for (const other of Object.values(model.nodes)) {
    if (other.parent === id) other.parent = null;
  }
  delete model.nodes[id];
  return true;
}

export function childrenOf(model, id) {
  return Object.values(model.nodes)
    .filter((n) => n.parent === id)
    .sort((a, b) => a.x - b.x || (a.order??0)-(b.order??0));
}

export function roots(model) {
  return Object.values(model.nodes).filter((n) => !n.parent);
}

// Would attaching child under parent create a cycle? (parent is a descendant
// of child.) Also rejects self-links.
//
// The builder is intentionally permissive: any node may connect to any other
// node, even if the combination is not a valid constituency. A word like NNP
// can be a parent, and a word SynTutor doesn't recognise can be a child — the
// tree still gets built so the builder stays functional.
export function canConnect(model, parentId, childId) {
  if (parentId === childId) return false;
  const parent = model.nodes[parentId];
  const child = model.nodes[childId];
  if (!parent || !child || parent.kind!==NODE.PHRASE || parent.canonicalTriangle || parent.canonicalData?.empty) return false;
  let cur = parent;
  const visited=new Set();
  while (cur) {
    if(visited.has(cur.id))return false;visited.add(cur.id);
    if (cur.id === childId) return false;
    cur = cur.parent ? model.nodes[cur.parent] : null;
  }
  return true;
}

export function connect(model, parentId, childId) {
  if (!canConnect(model, parentId, childId)) return false;
  model.nodes[childId].parent = parentId;
  return true;
}

export function disconnect(model, childId) {
  const n = model.nodes[childId];
  if (!n || !n.parent) return false;
  n.parent = null;
  return true;
}

// Connector dot: bottom-centre of a phrase box (drag it to start a new link).
export function dotOf(node) {
  return { x: node.x + node.w / 2, y: node.y + node.h + DOT_R + 1, r: DOT_R };
}

export function dotHit(model, x, y) {
  for (const n of Object.values(model.nodes)) {
    if (n.kind !== NODE.PHRASE) continue;
    const d = dotOf(n);
    // Generous hit area so clicking just below a phrase box starts a link
    // instead of dragging the box.
    if (Math.hypot(x - d.x, y - d.y) <= d.r + 12) return n;
  }
  return null;
}

// Endpoint: top-centre of a box, where an existing parent edge meets it. Drag
// it to re-attach the connection to a different parent, or drop it on empty
// space (or click it) to remove the connection.
export function endpointOf(node) {
  return { x: node.x + node.w / 2, y: node.y, r: DOT_R };
}

export function endpointHit(model, x, y) {
  const list = Object.values(model.nodes);
  for (let i = list.length - 1; i >= 0; i -= 1) {
    const n = list[i];
    if (!n.parent) continue;
    const p = endpointOf(n);
    if (Math.hypot(x - p.x, y - p.y) <= p.r + 4) return n;
  }
  return null;
}

export function nodeHit(model, x, y) {
  const list = Object.values(model.nodes);
  for (let i = list.length - 1; i >= 0; i -= 1) {
    const n = list[i];
    if (x >= n.x && x <= n.x + n.w && y >= n.y && y <= n.y + n.h) return n;
  }
  return null;
}

// Flatten a nested tree into its leaves with their surface word and POS tag.
export function leavesWithTags(tree) {
  const out = [];
  const walk = (n) => {
    if (!n) return;
    if (n.leaf || !n.children || n.children.length === 0) {
      out.push({ surface: n.surface ?? '', tag: n.type });
      return;
    }
    n.children.forEach(walk);
  };
  walk(tree);
  return out;
}

// Seed the model with one word box per gold leaf, laid out in a row. When
// ``withTags`` is set the official POS tag is attached to each word (used by
// the phrase/full-tree lessons where tagging is already taught).
export function seedWords(model, leaves, x, y, withTags = false, gap = 12) {
  const made = [];
  let cursor = x;
  for (const leaf of leaves) {
    const node = addWord(model, leaf.surface, cursor, y);
    if (withTags && leaf.tag) node.tag = leaf.tag;
    node.valid = true;
    made.push(node);
    cursor += node.w + gap;
  }
  return made;
}

// Turn the graph into a nested tree rooted at `rootId` (or the best guess when
// omitted): leaves ordered left-to-right by x. Returns null when `rootId` is a
// word or missing.
export function toTree(model, rootId) {
  let root = rootId ? model.nodes[rootId] : guessRoot(model);
  if (!root || root.kind !== NODE.PHRASE) return null;
  const build = (node) => {
    const kids = childrenOf(model, node.id);
    if (node.kind === NODE.WORD || kids.length === 0) {
      return { type: node.kind === NODE.WORD ? node.type : node.type, surface: node.text, leaf: true, x: node.x };
    }
    const children = kids.map(build);
    const ordered = [...children].sort((a, b) => a.x - b.x || (a.order??0)-(b.order??0));
    return { type: node.type, children: ordered.map(clean), x: node.x };
  };
  const clean = (n) => {
    const out = { type: n.type };
    if (n.leaf) {
      out.surface = n.surface;
      out.leaf = true;
    } else {
      out.children = n.children;
    }
    return out;
  };
  return clean(build(root));
}

function guessRoot(model) {
  const rs = roots(model).filter((n) => n.kind === NODE.PHRASE);
  if (!rs.length) return null;
  const s = rs.find((n) => /^(S|SBAR|SQ|SINV|SBARQ)$/.test(n.type));
  return s || rs[0];
}

// Leaf text order for a tree, left-to-right.
export function leavesOf(tree) {
  if (!tree) return [];
  if (tree.leaf || !tree.children) return [tree.surface ?? ''];
  return tree.children.flatMap(leavesOf);
}

// Structural comparison against a gold tree (SynTutor's parse, already reduced
// to {type, children:[...]} / {type, leaf, surface} form). Returns matched /
// missing / extra phrase spans so the quiz can give precise feedback.
export function compareTrees(userTree, goldTree) {
  const gold = phraseSpans(goldTree);
  const user = phraseSpans(userTree);
  const key = (s) => `${s.type}[${s.start}-${s.end}]`;
  const gset = new Map(gold.map((s) => [key(s), s]));
  const uset = new Map(user.map((s) => [key(s), s]));
  const matched = [];
  const missing = [];
  const extra = [];
  for (const [k, s] of gset) (uset.has(k) ? matched : missing).push(s);
  for (const [k, s] of uset) if (!gset.has(k)) extra.push(s);
  return {
    correct: missing.length === 0 && extra.length === 0,
    matched, missing, extra,
  };
}

// Every phrase node's {type, start, end} span in leaf order. Leaf nodes are the
// unit of width; spans are computed in one recursive pass.
export function phraseSpans(tree) {
  const out = [];
  let cursor = 0;
  const walk = (node) => {
    if (!node || node.leaf || !node.children || node.children.length === 0) {
      const start = cursor;
      cursor += 1;
      return { start, end: cursor };
    }
    const start = cursor;
    for (const child of node.children) walk(child);
    out.push({ type: node.type, start, end: cursor });
    return { start, end: cursor };
  };
  if (tree) walk(tree);
  return out;
}

// Compare the leaf text sequence so the quiz can flag a wrong sentence.
export function leafText(tree) {
  return leavesOf(tree).join(' ');
}

// Canonical editing preserves every imported field, node identity and reference.
// A changed construction is learner work, never a newly source-approved tree.
const clone=value=>JSON.parse(JSON.stringify(value));
export function toCanonicalEnvelope(model, profile = null) {
 const all=Object.values(model?.nodes||{}),top=roots(model);
 if(!all.length||top.length!==1)throw Error('Connect every node under one root.');
 const words=all.filter(n=>n.kind===NODE.WORD&&!n.canonicalData?.elided).sort((a,b)=>a.x-b.x||(a.order??0)-(b.order??0));
 const texts=words.map(n=>String(n.text).trim());
 if(texts.some(t=>!t))throw Error('Words must not be empty.');
 const original=model.canonicalBase;
 const unchangedTokens=original && JSON.stringify(texts)===JSON.stringify(original.tokens.map(t=>t.text));
 let offset=0;
 const tokens=unchangedTokens?clone(original.tokens):texts.map((text,index)=>{const token={index,text,char_span:[offset,offset+Array.from(text).length]};offset+=Array.from(text).length+1;return token;});
 const sentence=unchangedTokens?original.sentence:texts.join(' '),seen=new Set();
 let cursor=0;
 function walk(n,depth=0){
  if(seen.has(n.id)||depth>80)throw Error('Tree contains a cycle or exceeds depth 80.');seen.add(n.id);
  const children=childrenOf(model,n.id),raw=clone(n.canonicalData||{}),hadSpan=Object.hasOwn(raw,'token_span');
  delete raw.children;delete raw.token_span;raw.id=n.id;
  if(n.kind===NODE.WORD){
   if(children.length)throw Error('A word cannot contain children.');
   const index=words.indexOf(n);raw.word=n.text.trim();
   if(!raw.elided){if(index!==cursor)throw Error('Branches cross or words are out of order.');raw.token_span=[cursor,cursor+1];cursor++;}
   return raw;
  }
  if(n.kind===NODE.SPECIAL){
   if(children.length)throw Error('A gap or empty position cannot contain children.');
   if(raw.empty||hadSpan)raw.token_span=[cursor,cursor];if(n.canonicalIndex!==undefined&&!raw.empty)raw.index=n.canonicalIndex;
   return raw;
  }
  if(!raw.unlabelled)raw.label=n.type;
  if(n.canonicalFeatures!==undefined)raw.features=clone(n.canonicalFeatures);
  if(n.canonicalIndex!==undefined)raw.index=n.canonicalIndex;
  if(n.canonicalTriangle){
   if(raw.features?.length)throw Error('Triangles cannot carry features; expand this node or remove its features first.');
   if(!children.length||children.some(c=>c.kind!==NODE.WORD||c.canonicalData?.elided))throw Error('A triangle contains overt words only.');
   const start=cursor;for(const c of children)walk(c,depth+1);
   delete raw.features;raw.triangle=true;raw.words=children.map(c=>c.text.trim());raw.token_span=[start,cursor];return raw;
  }
  delete raw.triangle;delete raw.words;
  if(!children.length)throw Error(`Connect a child to ${n.type}.`);
  const start=cursor;raw.children=children.map(c=>walk(c,depth+1));if(hadSpan)raw.token_span=[start,cursor];return raw;
 }
 const root=walk(top[0]);if(seen.size!==all.length)throw Error('There are disconnected nodes.');
 const chosen=profile||original?.convention_profile||builderProfile();
 return {...clone(original||{}),schema_version:'1.1.0',tree_id:original?.tree_id||'learner-builder',sentence,tokens,
  convention_profile:clone(chosen),source:{book:'Learner construction',chapter:chosen.chapter,evidence_status:'NEEDS_REVIEW',review_status:'NOT_REVIEWED'},
  root,movement:clone(model.movement||[]),accepted_alternatives:clone(model.acceptedAlternatives||[])};
}
export function fromCanonicalEnvelope(envelope){
 if(!envelope||!envelope.root||!Array.isArray(envelope.tokens)||!envelope.convention_profile||!Number.isInteger(envelope.convention_profile.chapter)||envelope.convention_profile.chapter<1||envelope.convention_profile.chapter>10||!Array.isArray(envelope.movement)||!Array.isArray(envelope.accepted_alternatives))throw Error('A canonical tree envelope is required.');
 const model=createModel();model.canonicalBase=clone(envelope);model.movement=clone(envelope.movement||[]);model.acceptedAlternatives=clone(envelope.accepted_alternatives||[]);
 let x=0,count=0;const ids=new Set();
 function walk(raw,parent=null,depth=0,order=0){
  if(!raw||typeof raw!=='object'||depth>80||++count>500)throw Error('Unsupported tree size or node shape.');
  const id=raw.id||`import-${count}`;if(ids.has(id)||typeof id!=='string'||['__proto__','constructor','prototype'].includes(id))throw Error('Invalid or duplicate node ID.');ids.add(id);
  const special=raw.gap||raw.empty;
  const n={id,kind:special?NODE.SPECIAL:('word' in raw)?NODE.WORD:NODE.PHRASE,
   type:raw.label||('word' in raw?'word':raw.gap?'GAP':'∅'),text:raw.word|| (special?(raw.gap?'gap':`${raw.label} ∅`):''),
   x:x*110,y:depth*70,w:84,h:32,parent,order,canonicalData:clone(raw),canonicalFeatures:raw.features,canonicalIndex:raw.index,canonicalTriangle:raw.triangle||false};
  delete n.canonicalData.children;model.nodes[id]=n;
  if(n.kind===NODE.WORD||special)x++;
  else if(raw.triangle){
   for(const [i,word] of raw.words.entries()){
    let wid=`${id}-word-${i}`;while(model.nodes[wid]||ids.has(wid))wid+='x';
    model.nodes[wid]={id:wid,kind:NODE.WORD,type:'word',text:word,x:x++*110,y:(depth+1)*70,w:84,h:32,parent:id,order:i};ids.add(wid);
   }
  }else for(const [i,c] of (raw.children||[]).entries())walk(c,id,depth+1,i);
  const kids=childrenOf(model,id);if(kids.length)n.x=kids[0].x;
  return n;
 }
 walk(envelope.root);return model;
}
export function addSpecial(model,kind,x=0,y=0){
 const raw=kind==='gap'?{gap:true,index:1}:{empty:true,label:kind,empty_role:{DET:'determiner',C1:'complementiser',E:'ellipsis'}[kind]};
 if(!raw.gap&&!raw.empty_role)throw Error('Unknown empty position');
 return put(model,{id:nextId(),kind:NODE.SPECIAL,type:raw.label||'GAP',text:raw.gap?'gap':`${kind} ∅`,x,y,w:84,h:32,parent:null,canonicalData:raw,canonicalIndex:raw.index});
}
