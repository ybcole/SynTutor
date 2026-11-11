import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(x):return json.loads((ROOT/x).read_text(encoding='utf-8'))
class Ch5FirstBatch(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.audit=load('sources/cambridge/chapter_05/PP323_340_AUDIT.json');cls.ledger=load('grammar/coverage/cgel_ledger.json')['pages'];cls.rules={r['id']:r for r in load('grammar/rules/phrases.json')}
 def test_source_pages(self):
  self.assertEqual([p['page'] for p in self.audit['page_checks']],list(range(323,341)))
  for p in self.audit['page_checks']:self.assertEqual(p['status'],self.ledger[p['page']-1]['status'])
  self.assertTrue(all(p['status']=='skipped_with_reason' for p in self.audit['page_checks'][:3]))
 def test_nonactivated(self):
  self.assertGreaterEqual(len(self.audit['added_rule_ids']),25)
  for rid in self.audit['added_rule_ids']:
   r=self.rules[rid];self.assertEqual(r['status'],'NEEDS_REVIEW')
   self.assertEqual(r['sources'][0]['pdf_pages'],[p+20 for p in r['sources'][0]['pages']])
   self.assertTrue(all(x['relation']=='unverified' for x in r['burton_roberts_mapping']))
   self.assertGreaterEqual(len(r['examples']['correct']),2)
   if r['rule_type']=='constraint':self.assertEqual(r['diagnostic']['detector'],'spec_only')
   else:self.assertIsNone(r['diagnostic'])
 def test_sense_not_lemma(self):
  r=next(x for x in self.rules.values() if x['concept']=='Countability belongs to the lexical sense')
  self.assertIsNone(r['diagnostic'])
if __name__=='__main__':unittest.main()
