"""Canonical evaluation, actual constructed graphs and shared transport parity."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from copy import deepcopy
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
from tree_evaluation import evaluate_request,evaluate_analysis,compare_target,signature
from explanations import explain_analysis
from burton_roberts import canonicalize_gold_record,validate_canonical_tree
COURSE=json.loads((ROOT/'web/content/lessons/course.json').read_text())
def tree(ident='br-02'):
 return deepcopy(next(l['worked_example']['tree'] for l in COURSE['lessons'] if l['lesson_id']==ident))

class BuilderEvaluationTests(unittest.TestCase):
 def test_reviewed_benchmarks_have_shared_generator_builder_results(self):
  for lesson in COURSE['lessons']:
   t=lesson['worked_example'].get('tree')
   if not t:continue
   with self.subTest(lesson=lesson['lesson_id']):
    actual=evaluate_request({'tree':t,'target_lesson_id':lesson['lesson_id']})
    shared=evaluate_analysis({'status':'normalized','tree':t})
    self.assertTrue(actual['structure']['valid']);self.assertEqual(actual['target_comparison']['status'],'matched')
    self.assertEqual(actual['explanation_evidence'],explain_analysis({'status':'normalized','tree':t}))
    for k in ['structure','grammaticality','node_details','cambridge_evaluation']:self.assertEqual(actual[k],shared[k])
    self.assertEqual(actual['grammaticality']['status'],'unresolved')
 def test_actual_construction_is_validated_instead_of_its_sentence(self):
  t=tree();t['root']['children'][0]['label']='NOM'
  r=evaluate_request({'tree':t,'target_lesson_id':'br-02'})
  self.assertFalse(r['structure']['valid']);self.assertEqual(r['target_comparison']['status'],'not_evaluated');self.assertEqual(r['grammaticality']['status'],'unresolved')
  t=tree();t['root']['children'][0]['label']='VP'
  r=evaluate_request({'tree':t,'target_lesson_id':'br-02'});self.assertTrue(r['structure']['valid']);self.assertEqual(r['target_comparison']['status'],'different_from_target')
 def test_identity_free_comparison_and_accepted_alternatives(self):
  target=tree();alternative=deepcopy(target['root']);alternative['children'][0]['label']='VP'
  target['accepted_alternatives']=[{'analysis_id':'contextual-alternative','root':alternative,'acceptance':'ACCEPTED','rationale':'Synthetic comparison fixture, not production linguistic approval'}]
  t=deepcopy(target);t['root']=alternative;t['accepted_alternatives']=[]
  self.assertEqual(compare_target(t,target)['analysis_id'],'contextual-alternative')
  target['accepted_alternatives'][0]['acceptance']='NEEDS_REVIEW';self.assertFalse(compare_target(t,target)['matched'])
  t=tree();t['root']['id']='different';self.assertTrue(compare_target(t,tree())['matched'])
  t['convention_profile']={'chapter':10,'version':'FINAL','appendix_nom':True,'profile_id':'FINAL-D1'};self.assertEqual(compare_target(t,tree())['status'],'profile_mismatch')
 def test_client_metadata_cannot_supply_authority_or_target_answers(self):
  for extra in [{'runtime_registry':{}},{'xp':100},{'target_tree':tree()}]:
   with self.assertRaises(ValueError):evaluate_request({'tree':tree(),**extra})
  with self.assertRaises(ValueError):evaluate_request({'tree':tree(),'target_lesson_id':'invented'})
  t=tree();t['source']['review_status']='HUMAN_APPROVED';r=evaluate_request({'tree':t});self.assertEqual(r['explanation_evidence'],evaluate_request({'tree':tree()})['explanation_evidence'])
 def test_bounds_and_unsupported_labels(self):
  t=tree();t['root']['label']='SBAR';r=evaluate_request({'tree':t});self.assertEqual(r['structure']['status'],'unsupported')
  with self.assertRaises(ValueError):evaluate_request({'tree':None})
  t=tree();n=t['root']
  for _ in range(82):n['children']=[{'label':'NP'}];n=n['children'][0]
  with self.assertRaisesRegex(ValueError,'depth'):evaluate_request({'tree':t})
 def test_full_valid_gold_corpus_survives_editor_roundtrip(self):
  corpus=[]
  for path in sorted((ROOT/'web/content/book').glob('ch*.trees.json')):
   data=json.loads(path.read_text())
   for record in data.get('trees',[]):
    result=canonicalize_gold_record(record,data)
    if result['status']=='normalized':corpus.append(result['tree'])
  code="""import fs from 'node:fs';import{fromCanonicalEnvelope,toCanonicalEnvelope}from './web/js/syntax-builder.js';const trees=JSON.parse(fs.readFileSync(0,'utf8'));console.log(JSON.stringify(trees.map(t=>toCanonicalEnvelope(fromCanonicalEnvelope(t),t.convention_profile))));"""
  actual=json.loads(subprocess.check_output(['node','--input-type=module','-e',code],input=json.dumps(corpus),text=True,cwd=ROOT))
  self.assertGreater(len(actual),240)
  for before,after in zip(corpus,actual):
   with self.subTest(tree=before['tree_id']):
    self.assertTrue(validate_canonical_tree(after)['valid'],validate_canonical_tree(after)['errors'])
    self.assertEqual(signature(before),signature(after));self.assertEqual(before['tokens'],after['tokens']);self.assertEqual(before['movement'],after['movement']);self.assertEqual(before['accepted_alternatives'],after['accepted_alternatives'])
 def test_all_three_transports(self):
  from test_explanation_transports import ExplanationTransportTests,app
  from urllib.request import Request,urlopen
  from fastapi import FastAPI,Request as ASGIRequest
  from fastapi.testclient import TestClient
  from explanation_transport import api_evaluate
  data={'tree':tree(),'target_lesson_id':'br-02'}
  flask=app.test_client().post('/api/evaluate',json=data);self.assertEqual(flask.status_code,200)
  preflight=app.test_client().options('/api/evaluate',headers={'Origin':'https://syntutor.vercel.app','Access-Control-Request-Headers':'content-type'})
  self.assertIn('Content-Type',preflight.headers['Access-Control-Allow-Headers'])
  self.assertIn('POST',preflight.headers['Access-Control-Allow-Methods'])
  ExplanationTransportTests.setUpClass()
  try:
   req=Request(f'http://127.0.0.1:{ExplanationTransportTests.server.server_port}/api/evaluate',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})
   with urlopen(req) as response:self.assertEqual(json.load(response),flask.get_json())
  finally:ExplanationTransportTests.tearDownClass()
  async def endpoint(request):return await api_evaluate(request)
  endpoint.__annotations__={'request':ASGIRequest};asgi=FastAPI();asgi.add_api_route('/api/evaluate',endpoint,methods=['POST'])
  with TestClient(asgi) as client:
   self.assertEqual(client.post('/api/evaluate',json=data).json(),flask.get_json())
   for bad in [[],{'tree':None},{'tree':tree(),'target_tree':tree()}]:
    self.assertEqual(client.post('/api/evaluate',json=bad).status_code,400);self.assertEqual(app.test_client().post('/api/evaluate',json=bad).status_code,400)
