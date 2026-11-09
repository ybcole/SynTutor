import assert from 'node:assert/strict';
import { findCanonicalNode, canonicalNodeFacts, canonicalObservation } from '../web/js/canonical-view.js';

const envelope = {
  sentence: 'The birds sing.', tokens: [
    {text:'The'}, {text:'birds'}, {text:'sing'},
  ],
  source: {book:'Burton-Roberts',printed_page:29},
  root: {id:'s',label:'S',token_span:[0,3],children:[
    {id:'np',label:'NP',token_span:[0,2],triangle:true,words:['The','birds']},
    {id:'vp',label:'VP',token_span:[2,3],triangle:true,words:['sing']},
  ]},
};
assert.equal(findCanonicalNode(envelope.root, 's')?.label,'S');
assert.equal(findCanonicalNode(envelope.root, 'np')?.label,'NP');
assert.equal(findCanonicalNode(envelope.root, 'unknown'),null);
const subject=canonicalNodeFacts(envelope,findCanonicalNode(envelope.root,'np'));
assert.equal(subject.label,'NP');
assert.equal(subject.surface,'The birds');
assert.deepEqual(subject.children,[]);
assert.match(canonicalObservation(subject),/triangle marks an unanalyzed phrase/);
assert(!canonicalObservation(subject).includes('DT'));
const rootFacts=canonicalNodeFacts(envelope,envelope.root);
assert.deepEqual(rootFacts.children,['NP','VP']);
assert.match(canonicalObservation(rootFacts),/direct branches are NP, VP/);
assert.equal(rootFacts.source.printed_page,29);
assert.equal(canonicalObservation(null),'No canonical structural details are available.');
console.log('PASS: canonical B-R facts preserve source labels and triangles without inventing Penn grammar.');
