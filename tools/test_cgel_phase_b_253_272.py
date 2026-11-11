import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
class Ch4ThirdBatch(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=read('sources/cambridge/chapter_04/PP253_272_AUDIT.json');cls.pages=read('grammar/coverage/cgel_ledger.json')['pages'];cls.rules={r['id']:r for r in read('grammar/rules/complementation.json')}
 def test_page_audit(self):
  self.assertEqual([x['page'] for x in self.a['page_checks']],list(range(253,273)))
  for x in self.a['page_checks']: self.assertEqual(self.pages[x['page']-1]['status'],'extracted')
 def test_examples_nonactivation(self):
  self.assertGreaterEqual(len(self.a['added_rule_ids']),35)
  for rid in self.a['added_rule_ids']:
   r=self.rules[rid];self.assertEqual(r['status'],'NEEDS_REVIEW');self.assertEqual(r['sources'][0]['pdf_pages'],[p+20 for p in r['sources'][0]['pages']])
   self.assertTrue(all(m['relation']=='unverified' for m in r['burton_roberts_mapping']))
   self.assertGreaterEqual(len(r['examples']['correct']),2)
   if r['rule_type']=='constraint':self.assertEqual(r['diagnostic']['detector'],'spec_only')
   else:self.assertIsNone(r['diagnostic'])
 def test_pronoun_case_is_variety(self):
  r=next(x for x in self.rules.values() if x['concept']=='Pronoun case with specifying be')
  self.assertEqual(r['rule_type'],'variety_restricted');self.assertIsNone(r['diagnostic'])
if __name__=='__main__':unittest.main()
