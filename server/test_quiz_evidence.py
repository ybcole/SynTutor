import copy,json,subprocess,unittest
from pathlib import Path
from jsonschema import Draft202012Validator
from explanations import explain_request,explain_quiz_response
from quiz_bank import load_quiz_bank
ROOT=Path(__file__).resolve().parents[1]
class QuizEvidenceTests(unittest.TestCase):
 def test_all_feedback_matches_the_m3_schema(self):
  bank=load_quiz_bank();schema=Draft202012Validator(json.loads((ROOT/'grammar/explanation_evidence.schema.json').read_text()))
  for q in bank['items']:
   for answer in [q['answer'],None]:
    result=explain_request({'quiz_item_id':q['item_id'],'quiz_item_version':q['content_version'],'answer_id':answer});schema.validate(result)
    self.assertEqual(result['status'],'EXPLAINED');self.assertFalse(result['channels']['remediation'])
    channel='structural' if q['claim_scope']=='br_structure' else 'grammatical';self.assertIn(q['rationale'],result['channels'][channel][0]['text'])
 def test_client_cannot_supply_claims_or_unknown_versions(self):
  base=dict(quiz_item_id='br-02-p1-1',quiz_item_version='1.0.0')
  for patch in [dict(quiz_item_id='missing'),dict(quiz_item_version='9.0.0'),dict(answer_id='forged'),dict(sources=[]),dict(tree=None)]:
   with self.subTest(patch=patch),self.assertRaises(ValueError):explain_request({**base,**patch})
 def test_source_and_scope_gates_are_shared(self):
  bank=load_quiz_bank();q=bank['items'][0]
  for field,value in [('independent_review',False),('edition',''),('crosswalk_status','unverified'),('printed_page',True)]:
   sources=copy.deepcopy(bank['sources'])
   for s in sources:
    if s['id'] in q['source_ids']:s[field]=value
   self.assertEqual(explain_quiz_response(q,q['answer'],sources)['status'],'NO_BOOK_BASIS')
  self.assertEqual(explain_quiz_response({**q,'claim_scope':'grammaticality_constraint'},q['answer'],bank['sources'])['status'],'NO_BOOK_BASIS')
 def test_javascript_and_python_feedback_are_identical(self):
  bank=load_quiz_bank();ids=['br-02-p1-1','br-06-p2-1','br-10-p2-2','cgel-clauses-p2-1'];items=[q for q in bank['items'] if q['item_id'] in ids]
  expected=[explain_quiz_response(q,a,bank['sources']) for q in items for a in [q['answer'],next(o['id'] for o in q['options'] if o['id']!=q['answer']),None]]
  code="""import fs from 'node:fs';import {composeQuizEvidence} from './web/js/explanation-evidence.js';const b=JSON.parse(fs.readFileSync('web/content/quizzes/bank.json'));const items=b.items.filter(q=>['br-02-p1-1','br-06-p2-1','br-10-p2-2','cgel-clauses-p2-1'].includes(q.item_id));console.log(JSON.stringify(items.flatMap(q=>[q.answer,q.options.find(o=>o.id!==q.answer).id,null].map(a=>composeQuizEvidence(q,a,b)))));"""
  self.assertEqual(json.loads(subprocess.check_output(['node','--input-type=module','-e',code],cwd=ROOT,text=True)),expected)
 def test_three_transports_share_quiz_feedback(self):
  from test_explanation_transports import ExplanationTransportTests,app
  from fastapi import FastAPI,Request
  from fastapi.testclient import TestClient
  from explanation_transport import api_explain
  data={'quiz_item_id':'br-02-p1-1','quiz_item_version':'1.0.0','answer_id':'b'}
  flask=app.test_client().post('/api/explain',json=data);self.assertEqual(flask.status_code,200)
  ExplanationTransportTests.setUpClass()
  try:
   code,stdlib=ExplanationTransportTests().stdlib_post(json.dumps(data).encode());self.assertEqual(code,200);self.assertEqual(stdlib,flask.get_json())
  finally:ExplanationTransportTests.tearDownClass()
  async def endpoint(request):return await api_explain(request)
  endpoint.__annotations__={'request':Request};asgi=FastAPI();asgi.add_api_route('/api/explain',endpoint,methods=['POST'])
  with TestClient(asgi) as client:self.assertEqual(client.post('/api/explain',json=data).json(),flask.get_json())
 def test_existing_tree_variety_contract(self):
  self.assertEqual(explain_request({'tree':None,'variety':'British'})['status'],'ANALYSIS_UNRESOLVED')
  with self.assertRaises(ValueError):explain_request({'tree':None,'rule_id':'forged'})
