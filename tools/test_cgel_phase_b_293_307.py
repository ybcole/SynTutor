import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
class Ch4FifthBatch(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=load('sources/cambridge/chapter_04/PP293_307_AUDIT.json');cls.ledger=load('grammar/coverage/cgel_ledger.json')['pages'];cls.rules={x['id']:x for x in load('grammar/rules/complementation.json')}
 def test_coverage(self):
  self.assertEqual([x['page'] for x in self.a['page_checks']],list(range(293,308)))
  for p in self.a['page_checks']:self.assertEqual(self.ledger[p['page']-1]['status'],'extracted')
 def test_nonlive_records(self):
  self.assertGreaterEqual(len(self.a['added_rule_ids']),30)
  for rid in self.a['added_rule_ids']:
   r=self.rules[rid];self.assertEqual(r['status'],'NEEDS_REVIEW')
   self.assertEqual(r['sources'][0]['pdf_pages'],[p+20 for p in r['sources'][0]['pages']])
   self.assertTrue(all(m['relation']=='unverified' for m in r['burton_roberts_mapping']))
   self.assertGreaterEqual(len(r['examples']['correct']),2)
   if r['rule_type']=='constraint':self.assertEqual(r['diagnostic']['detector'],'spec_only')
   else:self.assertIsNone(r['diagnostic'])
 def test_no_middle_voice_detector(self):
  r=next(x for x in self.rules.values() if x['concept']=='English middle is active syntax')
  self.assertEqual(r['rule_type'],'classification');self.assertIsNone(r['diagnostic'])
if __name__=='__main__':unittest.main()
