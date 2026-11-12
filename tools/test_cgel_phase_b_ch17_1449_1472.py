"""CGEL Chapter 17 source batch pp.1449–1472: audit, regressions and negative guards."""
import json
import unittest
from pathlib import Path
from tools.cgel_batch_gate import check_batch

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

class Chapter17FirstBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit=load("sources/cambridge/chapter_17/PP1449_1472_AUDIT.json")
        cls.ledger=load("grammar/coverage/cgel_ledger.json")["pages"]
        cls.rules={r["id"]:r for p in ("phrases.json","clauses.json") for r in load("grammar/rules/"+p)}

    def test_consecutive_page_audit_and_gate(self):
        self.assertEqual([x["page"] for x in self.audit["page_checks"]],list(range(1449,1473)))
        self.assertEqual(check_batch(self.audit),[])
        self.assertEqual([x["status"] for x in self.audit["page_checks"][:2]],["skipped_with_reason"]*2)
        self.assertTrue(all(x["status"]=="extracted" for x in self.audit["page_checks"][2:]))
        for x in self.audit["page_checks"]:
            self.assertEqual(self.ledger[x["page"]-1]["status"],x["status"])
            self.assertTrue(x["source_checked"])
            self.assertTrue(x["layout_checked"])
            self.assertTrue(x["exceptions_checked"])
            self.assertFalse(x["unresolved_items"])

    def test_grounded_examples_and_fail_closed_runtime(self):
        self.assertEqual(len(self.audit["added_rule_ids"]),62)
        for rid in self.audit["added_rule_ids"]:
            with self.subTest(id=rid):
                rule=self.rules[rid]
                self.assertEqual(rule["status"],"NEEDS_REVIEW")
                self.assertTrue(all(m["relation"]=="unverified" for m in rule["burton_roberts_mapping"]))
                self.assertGreaterEqual(len(rule["examples"]["correct"]),2)
                self.assertTrue(all(e["origin"]=="ai_authored" for e in rule["examples"]["correct"]))
                for src in rule["sources"]:
                    self.assertEqual(src["chapter"],17)
                    self.assertEqual(src["pdf_pages"],[p+20 for p in src["pages"]])
                if rule["rule_type"]=="constraint":
                    self.assertEqual(rule["diagnostic"]["detector"],"spec_only")
                    self.assertGreaterEqual(len(rule["examples"]["incorrect"]),2)
                    self.assertGreaterEqual(len(rule["diagnostic"]["minimal_pairs"]),2)
                    self.assertGreaterEqual(len(rule["diagnostic"]["false_positive_guards"]),2)
                else:
                    self.assertIsNone(rule["diagnostic"])
                    self.assertFalse(rule["examples"]["incorrect"])

    def test_semantic_and_register_cases_not_overflagged(self):
        by={self.rules[rid]["concept"]:self.rules[rid] for rid in self.audit["added_rule_ids"]}
        for concept in ("Bound-variable anaphora with quantifiers",
                        "Multiple antecedent candidates and grammatical ambiguity",
                        "Split antecedents for plural anaphors",
                        "Authorial we in single-author writing",
                        "Non-referential generic you",
                        "Contextually salient non-anaphoric third-person reference",
                        "Institutional they with unspecified authority",
                        "Hypothetical entities licensed by indefinite antecedents"):
            with self.subTest(concept=concept):
                self.assertNotEqual(by[concept]["rule_type"],"constraint")
                self.assertIsNone(by[concept]["diagnostic"])

    def test_specific_reflexive_constraint_only(self):
        c=[self.rules[rid] for rid in self.audit["added_rule_ids"] if self.rules[rid]["rule_type"]=="constraint"]
        self.assertEqual(len(c),1)
        self.assertEqual(c[0]["concept"],"Reflexive anaphor requires the appropriate local antecedent in a chain")
        for bad,pair in zip(c[0]["examples"]["incorrect"],c[0]["diagnostic"]["minimal_pairs"]):
            self.assertTrue(pair.startswith(bad["text"]+" ||| "))

if __name__=="__main__":
    unittest.main()
