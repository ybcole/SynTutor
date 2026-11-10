"""CGEL Chapter 3 pp. 115–122: page provenance and machine-readable rule contracts."""
import json,unittest
from pathlib import Path
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[1]
class PhaseB115122(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules=[r for f in sorted((ROOT/"grammar/rules").glob("*.json"))
                   for r in json.loads(f.read_text(encoding="utf-8"))]
        cls.schema=json.loads((ROOT/"grammar/schema.json").read_text(encoding="utf-8"))
        cls.batch=[r for r in cls.rules if any(s.get("chapter")==3
                   and "cambridge" in str(s.get("book","")).lower()
                   and any(115<=p<=122 for p in s.get("pages",[]))
                   for s in r.get("sources",[]))]
        cls.ledger=json.loads((ROOT/"grammar/coverage/cgel_ledger.json").read_text(encoding="utf-8"))["pages"]
    def test_source_records_stable(self):
        self.assertEqual(len(self.batch),31)
        self.assertGreaterEqual(len(self.rules),332)
        ids=[r["id"] for r in self.rules]
        self.assertEqual(len(ids),len(set(ids)))
    def test_schema_and_provenance(self):
        v=Draft202012Validator(self.schema)
        for rule in self.batch:
            self.assertFalse(list(v.iter_errors(rule)),rule["id"])
            self.assertEqual(rule["protocol_version"],"1.1")
            for src in rule["sources"]:
                if src["chapter"]==3:self.assertTrue(all(115<=p<=122 for p in src["pages"]))
    def test_error_safe_diagnostic(self):
        constraints=[r for r in self.batch if r["rule_type"]=="constraint"]
        self.assertEqual([r["id"] for r in constraints],["CLS-120"])
        for r in constraints:
            self.assertEqual(r["diagnostic"]["detector"],"spec_only")
            self.assertGreaterEqual(len(r["examples"]["correct"]),2)
            self.assertGreaterEqual(len(r["examples"]["incorrect"]),2)
            self.assertGreaterEqual(len(r["diagnostic"]["minimal_pairs"]),2)
            self.assertGreaterEqual(len(r["diagnostic"]["false_positive_guards"]),2)
    def test_source_evidence_files(self):
        for p in range(115,123):
            row=self.ledger[p-1]
            self.assertEqual(row["status"],"extracted")
            self.assertTrue((ROOT/row["evidence"]).is_file())
