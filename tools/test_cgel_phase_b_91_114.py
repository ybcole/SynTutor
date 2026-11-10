"""Phase B Chapter 3, pp 91–114: schema, source provenance and safety gates."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
class CGELBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema=json.loads((ROOT/"grammar/schema.json").read_text(encoding="utf-8"))
        cls.rules=[r for f in sorted((ROOT/"grammar/rules").glob("*.json"))
            for r in json.loads(f.read_text(encoding="utf-8"))]
        cls.batch=[r for r in cls.rules if any(s.get("chapter")==3
            and "cambridge" in str(s.get("book","")).lower()
            and any(91<=p<=114 for p in s.get("pages",[]))
            for s in r.get("sources",[]))]
        cls.rows=json.loads((ROOT/"grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8"))["pages"]
    def test_batch_id_and_count(self):
        self.assertEqual(len(self.rules),301)
        self.assertEqual(len(self.batch),70)
        ids=[r["id"] for r in self.rules]
        self.assertEqual(len(ids),len(set(ids)))
    def test_schema_and_source_ranges(self):
        v=Draft202012Validator(self.schema)
        for r in self.batch:
            self.assertFalse(list(v.iter_errors(r)),r["id"])
            self.assertEqual(r["protocol_version"],"1.1")
            self.assertTrue(all(91<=p<=114 for s in r["sources"] if s["chapter"]==3 for p in s["pages"]))
    def test_constraints_have_gates(self):
        cs=[r for r in self.batch if r["rule_type"]=="constraint"]
        self.assertEqual(len(cs),19)
        for r in cs:
            d=r["diagnostic"]
            self.assertEqual(d["detector"],"spec_only",r["id"])
            self.assertGreaterEqual(len(r["examples"]["correct"]),2)
            self.assertGreaterEqual(len(r["examples"]["incorrect"]),2)
            self.assertGreaterEqual(len(d["minimal_pairs"]),2)
            self.assertGreaterEqual(len(d["false_positive_guards"]),2)
            for pair in d["minimal_pairs"]:
                self.assertEqual(len(pair.split("|||")),2,(r["id"],pair))
    def test_documented_coverage(self):
        for page in range(91,115):
            row=self.rows[page-1]
            self.assertEqual((row["page"],row["status"]),(page,"extracted"))
            self.assertTrue((ROOT/row["evidence"]).is_file(),page)
        self.assertEqual(self.rows[114]["status"],"unprocessed")
        self.assertEqual(sum(r["status"]=="extracted" for r in self.rows if r["chapter"]==3),41)
    def test_no_new_runtime_claims(self):
        self.assertFalse([r["id"] for r in self.batch if isinstance(r.get("diagnostic"),dict)
            and str(r["diagnostic"].get("detector","")).startswith("implemented:")])
