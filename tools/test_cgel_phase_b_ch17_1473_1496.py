"""Regressions for Chapter 17 pp.1473–1496; source inventory and fail-closed metadata."""
import json
import unittest
from pathlib import Path
from tools.cgel_batch_gate import check_batch

ROOT=Path(__file__).resolve().parents[1]
def load(p):
    return json.loads((ROOT/p).read_text(encoding="utf-8"))

class Ch17SecondBatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=load("sources/cambridge/chapter_17/PP1473_1496_AUDIT.json")
        cls.ledger=load("grammar/coverage/cgel_ledger.json")["pages"]
        cls.by_id={r["id"]:r for p in ("phrases.json","clauses.json") for r in load("grammar/rules/"+p)}

    def test_consecutive_source_checks_and_batch_gate(self):
        self.assertEqual([v["page"] for v in self.manifest["page_checks"]],list(range(1473,1497)))
        self.assertEqual(check_batch(self.manifest),[])
        for entry in self.manifest["page_checks"]:
            page=entry["page"]
            self.assertEqual(entry["status"],"extracted")
            self.assertEqual(self.ledger[page-1]["status"],"extracted")
            self.assertTrue(entry["source_checked"])
            self.assertTrue(entry["layout_checked"])
            self.assertTrue(entry["exceptions_checked"])
            self.assertFalse(entry["unresolved_items"])

    def test_source_provenance_and_no_enablement(self):
        ids=self.manifest["added_rule_ids"]
        self.assertEqual(len(ids),67)
        self.assertEqual(len(ids),len(set(ids)))
        for rid in ids:
            with self.subTest(rid=rid):
                r=self.by_id[rid]
                self.assertEqual(r["status"],"NEEDS_REVIEW")
                self.assertTrue(all(m["relation"]=="unverified" for m in r["burton_roberts_mapping"]))
                self.assertGreaterEqual(len(r["examples"]["correct"]),2)
                self.assertTrue(all(e["origin"]=="ai_authored" for e in r["examples"]["correct"]))
                for s in r["sources"]:
                    self.assertEqual(s["chapter"],17)
                    self.assertEqual(s["pdf_pages"],[p+20 for p in s["pages"]])
                if r["rule_type"]=="constraint":
                    self.assertEqual(r["diagnostic"]["detector"],"spec_only")
                    self.assertGreaterEqual(len(r["examples"]["incorrect"]),2)
                    self.assertGreaterEqual(len(r["diagnostic"]["minimal_pairs"]),2)
                    self.assertGreaterEqual(len(r["diagnostic"]["false_positive_guards"]),2)
                else:
                    self.assertIsNone(r["diagnostic"])
                    self.assertFalse(r["examples"]["incorrect"])

    def test_valid_variation_and_noncanonical_forms_not_false_errors(self):
        by={self.by_id[rid]["concept"]:self.by_id[rid] for rid in self.manifest["added_rule_ids"]}
        for concept in (
            "Sex-neutral bound-variable singular they",
            "Donkey anaphora under quantified conditions",
            "Rhetorical cataphora across multiple sentences",
            "Reflexive pronoun morphology",
            "Optional locative PP reflexives",
            "Preposed reflexives remain structurally bound",
            "Coreference without anaphoric linking",
            "Override reflexives in coordination",
            "Emphatic reflexives in four syntactic positions",
        ):
            with self.subTest(concept=concept):
                self.assertNotEqual(by[concept]["rule_type"],"constraint")
                self.assertIsNone(by[concept]["diagnostic"])

    def test_lexical_constraint_is_explicit_and_safely_scoped(self):
        constraints=[self.by_id[rid] for rid in self.manifest["added_rule_ids"] if self.by_id[rid]["rule_type"]=="constraint"]
        self.assertEqual(len(constraints),1)
        r=constraints[0]
        self.assertEqual(r["concept"],"Pride lexically requires the subject-bound reflexive object")
        self.assertEqual(r["diagnostic"]["detector"],"spec_only")
        self.assertEqual(len(r["diagnostic"]["minimal_pairs"]),2)
        for incorrect,pair in zip(r["examples"]["incorrect"],r["diagnostic"]["minimal_pairs"]):
            self.assertTrue(pair.startswith(incorrect["text"]+" ||| "))

if __name__=="__main__":
    unittest.main()
