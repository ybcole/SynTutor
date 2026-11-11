import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
class Ch4FourthBatch(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=load('sources/cambridge/chapter_04/PP273_292_AUDIT.json');cls.rows=load('grammar/coverage/cgel_ledger.json')['pages'];cls.rules={r['id']:r for r in load('grammar/rules/complementation.json')}
 def test_pages(self):
  self.assertEqual([x['page'] for x in self.a['page_checks']], list(range(273,293)))
  for x in self.a['page_checks']:self.assertEqual(self.rows[x['page']-1]['status'],'extracted')
 def test_rule_source_and_safety(self):
  self.assertGreaterEqual(len(self.a['added_rule_ids']),40)
  for rid in self.a['added_rule_ids']:
   r=self.rules[rid];self.assertEqual(r['status'],'NEEDS_REVIEW')
   self.assertEqual(r['sources'][0]['pdf_pages'],[p+20 for p in r['sources'][0]['pages']])
   self.assertGreaterEqual(len(r['examples']['correct']),2)
   self.assertTrue(all(x['relation']=='unverified' for x in r['burton_roberts_mapping']))
   if r['rule_type']=='constraint':self.assertEqual(r['diagnostic']['detector'],'spec_only')
   else:self.assertIsNone(r['diagnostic'])
 def test_dialect_not_error(self):
  a=next(x for x in self.rules.values() if x['concept']=='Transitive out is a regional variant')
  self.assertEqual(a['rule_type'],'variety_restricted');self.assertIsNone(a['diagnostic'])
if __name__=='__main__':unittest.main()
