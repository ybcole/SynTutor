// XAI-7 front-end focus, source-boundary and keyboard-contract regressions.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { evidenceFocus, applyEvidenceFocus, evidenceFocusText } from '../web/js/xai7-focus.js';

const mk=(id)=>({
  attrs:{"data-node-id":id}, dataset:{},
  getAttribute(k){return this.attrs[k]??null},
  removeAttribute(k){
    delete this.attrs[k];
    const ds=k.replace(/^data-/,'').replace(/-([a-z])/g,(_,x)=>x.toUpperCase());
    delete this.dataset[ds];
  },
});
const nodes=['s','np','vp','v','x'].map(mk);
const tree={querySelectorAll(query){assert.equal(query,'[data-node-id]');return nodes;}};
const original={
  xai7_unified:{
    schema_version:'xai7-evidence-1.0.0',language_policy:'ENGLISH_ONLY',
    selected_node_id:'v',focus:[
      {node_id:'v',reason:'selected',relation_authority:'witnessed_tree_position'},
      {node_id:'vp',reason:'parent',relation_authority:'witnessed_tree_position'},
      {node_id:'np',reason:'sibling',relation_authority:'witnessed_tree_position'},
    ],verified_issues:[],feature_rows:[{node_id:'v',feature:'pres'}],
  },
  fact_graph:{target:{node_id:'v',kind:'word',surface:'sings',label:'V'}},
};
assert.equal(evidenceFocus(original).selected,'v');
assert.deepEqual(applyEvidenceFocus(tree,original),['np','vp','v']);
assert.equal(nodes[3].dataset.xai7Focus,'selected');
assert.equal(nodes[2].dataset.xai7Focus,'parent');
assert.equal(nodes[1].dataset.xai7Focus,'sibling');
assert.equal(nodes[4].dataset.xai7Related,undefined);
assert.equal(evidenceFocusText(original).selected,'word: sings');
assert.deepEqual(evidenceFocusText(original).featureLabels,['pres']);
assert.equal(evidenceFocusText(original).verifiedIssueCount,0);

const next=structuredClone(original);
next.xai7_unified.selected_node_id='np';
next.xai7_unified.focus=[
  {node_id:'np',reason:'selected',relation_authority:'witnessed_tree_position'},
  {node_id:'s',reason:'parent',relation_authority:'witnessed_tree_position'},
];
next.fact_graph.target={node_id:'np',kind:'branch',label:'NP',surface:'The boy'};
assert.deepEqual(applyEvidenceFocus(tree,next),['s','np']);
assert.equal(nodes[3].dataset.xai7Focus,undefined);
assert.equal(nodes[1].dataset.xai7Focus,'selected');
assert.equal(nodes[0].dataset.xai7Focus,'parent');
assert.equal(evidenceFocusText(next).selected,'NP: The boy');
assert.equal(evidenceFocusText(next).treeNote,'parent s');

const permitted=structuredClone(original);
permitted.xai7_unified.verified_issues=[{
  finding_id:'fixture-only',status:'verified_local_violation'
}];
permitted.xai7_unified.focus.push(
  {node_id:'np',reason:'approved_governor',relation_authority:'approved_rule'}
);
applyEvidenceFocus(tree,permitted);
assert.equal(nodes[1].dataset.xai7Issue,'governor');
assert.equal(evidenceFocusText(permitted).verifiedIssueCount,1);
assert.equal(nodes[3].dataset.xai7Issue,undefined);

const unapproved=structuredClone(original);
unapproved.xai7_unified.verified_issues=[];
unapproved.xai4_partial_evaluation={evaluations:[{
  status:'BLOCKED',rule_id:'TEST-UNAPPROVED'
}]};
applyEvidenceFocus(tree,unapproved);
assert.equal(nodes[1].dataset.xai7Issue,undefined);
assert.equal(nodes[3].dataset.xai7Focus,'selected');
assert.equal(evidenceFocus({xai7_unified:{schema_version:'bad',focus:[]}}).selected,null);
assert.deepEqual(applyEvidenceFocus(null,original),[]);

// Guard against raw-Benepar category leakage via inferred linguistic roles.
// The shared view renders only verified position edges and approved findings.
const shared=readFileSync(new URL('../web/js/explanation-evidence.js',import.meta.url),'utf8');
const lessons=readFileSync(new URL('../web/js/lessons-ui.js',import.meta.url),'utf8');
const quiz=readFileSync(new URL('../web/js/quizzes-ui.js',import.meta.url),'utf8');
assert.match(shared,/renderFocusNavigation/);
assert.match(shared,/applyEvidenceFocus/);
assert.match(lessons,/onSelectNode/);
assert.match(lessons,/xai7Zoom/);
assert.match(quiz,/requestEvidence\(q.answer_tree,nodeId\)/);
console.log('PASS XAI-7: selected/parent/sibling focus, approved-only issues, safe clearing, English-only shared tree integration.');
