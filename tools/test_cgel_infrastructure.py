"""Phase A infrastructure and fail-closed coverage unit tests."""
import copy,unittest
from tools import ledger
from tools.migrate_diagnostics import run
from tools.validate_cgel_rules import validate
class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=ledger.load(ledger.LEDGER)
        cls.manifest=ledger.load(ledger.MANIFEST)
    def test_page_inventory(self):
        pages=self.data["pages"]
        self.assertEqual(len(pages),1764)
        self.assertEqual(pages[69]["status"],"absent_from_source")
        self.assertEqual(pages[523]["status"],"absent_from_source")
        self.assertEqual(sum(p["status"]=="skipped_with_reason" for p in pages),10)
        self.assertEqual(sum(p["status"]=="unprocessed" for p in pages),1752)
    def test_integrity_not_certification(self):
        self.assertEqual(ledger.check(self.data,self.manifest,allow_unprocessed=True),[])
        errors=ledger.check(self.data,self.manifest,chapter=3)
        self.assertTrue(any("unprocessed" in e for e in errors))
    def test_unverified_extraction_rejected(self):
        bad=copy.deepcopy(self.data)
        bad["pages"][70]["status"]="extracted"
        self.assertTrue(any("missing extraction evidence" in e for e in ledger.check(bad,self.manifest,allow_unprocessed=True)))
    def test_bad_chapter_rejected(self):
        bad=copy.deepcopy(self.data)
        bad["pages"][70]["chapter"]=2
        self.assertTrue(any("mismatch" in e for e in ledger.check(bad,self.manifest,allow_unprocessed=True)))
    def test_migration_completed(self):
        self.assertEqual(run(),(196,0))
    def test_schema_and_rule_citations(self):
        count,errors=validate()
        self.assertEqual(count,196)
        self.assertEqual(errors,[])
