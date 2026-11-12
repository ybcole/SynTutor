// Learner-facing renderer must show exactly one plain-English paragraph,
// never the source registry, implementation status or traceability sidecars.
import assert from 'node:assert/strict';
import { learnerParagraph, learnerFeatureParagraph, learnerFindingParagraph, renderEvidence } from '../web/js/explanation-evidence.js';

const original = {
  learner_explanation: {
    schema_version:'learner-explanation-1.0.0',language_policy:'ENGLISH_ONLY',
    text:'“are” is a present-tense form of the verb “be.” Here it combines with “working” to describe an activity in progress.',
  },
  status:'NO_BOOK_BASIS',
  diagnostics:[{message:'No independently reviewed source/template supports this.'}],
  xai4_partial_evaluation:{enabled_rule_ids:[],evaluations:[{status:'BLOCKED',rule_id:'FAKE'}]},
  xai6_naturalization:{status:'disabled'},
  xai5_localization:{original_sentence:'They are working.',diagnoses:[]},
  xai7_unified:{feature_rows:[]},
};
assert.match(learnerParagraph(original),/“are”.*“working”/);
assert.doesNotMatch(learnerParagraph(original),/book|page|XAI-|approved|source|rule|review/i);

const finding = {
  ...original, status:'EXPLAINED',
  channels:{remediation:[{node_id:'wait', text:'Add “to” before “wait”.',
                          facts:{target:'finding_nodes'}}]},
};
assert.equal(learnerFindingParagraph(finding, 'wait'), 'Add “to” before “wait”.');
assert.equal(learnerFindingParagraph(finding, 'subject'), null);
assert.equal(learnerFindingParagraph(finding), null);
assert.equal(learnerFindingParagraph({...finding, status:'SOURCE_CONFLICT'}, 'wait'), null);
assert.equal(learnerParagraph(finding), original.learner_explanation.text);
assert.doesNotMatch(learnerParagraph({status:'EXPLAINED', channels:finding.channels}), /Add “to”/);

const quiz = {
  status:'EXPLAINED', analysis_status:'quiz_feedback',
  channels:{
    grammatical:[{text:'Correct answer: an adjective phrase. “very” increases the degree of “cheerful”.',
                   sources:[{book:'Cambridge',printed_page:113}]}],
    structural:[],remediation:[],
  },
};
assert.match(learnerParagraph(quiz),/“very” increases/);
assert.doesNotMatch(learnerParagraph(quiz),/Cambridge|113|book|page/);
assert.equal(learnerParagraph({analysis_status:'quiz_feedback'}),
             "I can't explain this answer confidently yet.");

const featureEvidence = {
  ...original,
  xai7_unified:{feature_rows:[{node_id:'v',feature:'trans'}]},
  fact_graph:{target:{surface:'inspected'}},
};
assert.match(learnerFeatureParagraph(featureEvidence,'trans'),/marked as transitive/);
assert.doesNotMatch(learnerFeatureParagraph(featureEvidence,'past'),/marked as past tense/);

const elements = [];
const host = {
  children:[],
  querySelector(selector){return null},
  append(element){this.children.push(element);},
};
const originalDocument = globalThis.document;
globalThis.document = {
  createElement(tag) {
    const elt={tag,dataset:{},className:'',children:[],textContent:'',
      setAttribute(k,v){this[k]=v},
      append(child){this.children.push(child)},
      querySelector(){return null},
    };
    elements.push(elt);
    return elt;
  },
};
try {
  renderEvidence(original,host);
  assert.equal(host.children.length,1);
  assert.equal(host.children[0].children.length,1);
  assert.equal(host.children[0].children[0].tag,'p');
  assert.equal(host.children[0].children[0].textContent,original.learner_explanation.text);
  assert.equal(host.children[0].children[0].dataset.xaiShort,'');
  assert.equal(elements.some(elt => elt.tag==='details'||elt.tag==='button'||elt.tag==='h3'),false);
  host.children.length=0; elements.length=0;
  renderEvidence(quiz,host);
  assert.equal(host.children[0].children.length,1);
  assert.doesNotMatch(host.children[0].children[0].textContent,/Cambridge|printed_page/);
  host.children.length=0; elements.length=0;
  renderEvidence(finding,host,{nodeId:'wait'});
  assert.equal(host.children[0].children[0].textContent,'Add “to” before “wait”.');
  host.children.length=0; elements.length=0;
  renderEvidence(finding,host,{nodeId:'subject'});
  assert.equal(host.children[0].children[0].textContent,original.learner_explanation.text);
  // Hostile user text remains plain text. There is never an innerHTML call.
  host.children.length=0; elements.length=0;
  renderEvidence({status:'EXPLAINED',channels:{
    structural:[{text:'<img src=x onerror=alert(1)>',sources:[]}]}},host);
  assert.equal(host.children[0].children[0].textContent,'<img src=x onerror=alert(1)>');
  assert.equal(elements.some(elt => elt.tag==='img'),false);
} finally {
  globalThis.document = originalDocument;
}
console.log('PASS: one concise English paragraph, no book/debug panels, safe quote/HTML handling, per-feature sentence.');
