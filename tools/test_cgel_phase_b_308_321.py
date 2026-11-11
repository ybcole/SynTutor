import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
class Ch4LastBatch(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=load('sources/cambridge/chapter_04/PP308_321_AUDIT.json');cls.ledger=load('grammar/coverage/cgel_ledger.json')['pages'];cls.rules={r['id']:r for r in load('grammar/rules/complementation.json')}
 def test_pages(self):
  self.assertEqual([x['page'] for x in self.a['page_checks']],list(range(308,322)))
  for p in self.a['page_checks']: self.assertEqual(self.ledger[p['page']-1]['status'],'extracted')
  self.assertEqual(self.ledger[321]['status'],'skipped_with_reason')
 def test_nonactivated(self):
  self.assertGreaterEqual(len(self.a['added_rule_ids']),35)
  for rid in self.a['added_rule_ids']:
   r=self.rules[rid];self.assertEqual(r['status'],'NEEDS_REVIEW')
   self.assertEqual(r['sources'][0]['pdf_pages'],[p+20 for p in r['sources'][0]['pages']])
   self.assertGreaterEqual(len(r['examples']['correct']),2)
   self.assertTrue(all(x['relation']=='unverified' for x in r['burton_roberts_mapping']))
   if r['rule_type']=='constraint':self.assertEqual(r['diagnostic']['detector'],'spec_only')
   else:self.assertIsNone(r['diagnostic'])
 def test_middle_and_goods_guard(self):
  for c in ['English middles are syntactically active','Goods beneficiaries versus service beneficiaries']:
   r=next(v for v in self.rules.values() if v['concept']==c)
   self.assertNotEqual(r['rule_type'],'constraint')
if __name__=='__main__':unittest.main()
