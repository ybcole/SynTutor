"""Source and safety regression for Cambridge Chapter 4 printed pp.213–232."""
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding="utf-8"))
class Ch4Batch(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.audit=read("sources/cambridge/chapter_04/PP213_232_AUDIT.json")
  cls.ledger=read("grammar/coverage/cgel_ledger.json")["pages"]
  cls.rules={r["id"]:r for r in read("grammar/rules/complementation.json")}
 def test_pages(self):
  self.assertEqual([p["page"] for p in self.audit["page_checks"]],list(range(213,233)))
  for p in self.audit["page_checks"]:self.assertEqual(self.ledger[p["page"]-1]["status"],p["status"])
 def test_inactive_and_sourced(self):
  self.assertEqual(len(self.audit["added_rule_ids"]),19)
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
 def test_anomaly_not_diagnostic(self):
  x=next(x for x in self.rules.values() if x["concept"]=="Semantic selection is not syntactic error")
  self.assertIsNone(x["diagnostic"])
if __name__=="__main__":unittest.main()
