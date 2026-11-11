"""Regression: Chapter 4, printed 233–252, source and safe detector gate."""
import unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding="utf8"))
class Ch4SecondBatch(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.audit=read("sources/cambridge/chapter_04/PP233_252_AUDIT.json")
  cls.rules={x["id"]:x for x in read("grammar/rules/complementation.json")}
  cls.ledger=read("grammar/coverage/cgel_ledger.json")["pages"]
 def test_pages(self):
  self.assertEqual([r["page"] for r in self.audit["page_checks"]],list(range(233,253)))
  for r in self.audit["page_checks"]:self.assertEqual(self.ledger[r["page"]-1]["status"],"extracted")
 def test_gated_examples(self):
  self.assertEqual(len(self.audit["added_rule_ids"]),22)
  for rid in self.audit["added_rule_ids"]:
   r=self.rules[rid]
   self.assertEqual(r["status"],"NEEDS_REVIEW")
   self.assertEqual(r["sources"][0]["pdf_pages"],[p+20 for p in r["sources"][0]["pages"]])
   self.assertTrue(all(x["relation"]=="unverified" for x in r["burton_roberts_mapping"]))
   self.assertGreaterEqual(len(r["examples"]["correct"]),2)
   if r["rule_type"]=="constraint":
    self.assertEqual(r["diagnostic"]["detector"],"spec_only")
    self.assertGreaterEqual(len(r["diagnostic"]["false_positive_guards"]),2)
   else:self.assertIsNone(r["diagnostic"])
 def test_informal_plural_not_error(self):
  r=next(x for x in self.rules.values() if x["concept"]=="Existential agreement and informal contracted there's")
  self.assertEqual(r["rule_type"],"variety_restricted")
  self.assertIsNone(r["diagnostic"])
 def test_pp_is_not_indirect_object(self):
  r=next(x for x in self.rules.values() if x["concept"]=="Ditransitive PP alternant is not an indirect object")
  self.assertIn("not Oi",r["statement"]+" "+r["exceptions"][0]["description"])
if __name__=="__main__":unittest.main()
