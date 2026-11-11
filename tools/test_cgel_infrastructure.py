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
        # Split-source gaps may later be resolved from the verified full PDF.
        # The current ledger, rather than a permanent absence assertion, is authoritative.
        for page in (70, 524):
            self.assertIn(pages[page-1]["status"],
                          {"absent_from_source", "extracted", "skipped_with_reason"})
        self.assertGreaterEqual(sum(p["status"]=="skipped_with_reason" for p in pages),10)
        self.assertEqual(sum(p["status"] in {
            "extracted", "unprocessed", "skipped_with_reason", "absent_from_source"
        } for p in pages), 1764)
        # A completed 20-chapter extraction must NOT cause this test to fail.
    def test_integrity_not_certification(self):
        self.assertEqual(ledger.check(self.data,self.manifest,allow_unprocessed=True),[])
        # Chapter 3 now has complete page-level source accounting; the book as a whole does not.
        self.assertEqual(ledger.check(self.data,self.manifest,chapter=3), [])
        # Test against whichever chapter still has work, instead of permanently
        # requiring Chapter 4 (or the whole book) to be incomplete.
        pending={row["chapter"] for row in self.data["pages"]
                 if row["status"]=="unprocessed"}
        if pending:
            next_ch=min(pending)
            errors=ledger.check(self.data,self.manifest,chapter=next_ch)
            self.assertTrue(any("unprocessed" in e for e in errors))
        else:
            self.assertEqual(ledger.check(self.data,self.manifest), [])
    def test_unverified_extraction_rejected(self):
        bad=copy.deepcopy(self.data)
        bad["pages"][70]["status"]="extracted"
        bad["pages"][70]["evidence"]=None
        self.assertTrue(any("missing extraction evidence" in e for e in ledger.check(bad,self.manifest,allow_unprocessed=True)))
    def test_bad_chapter_rejected(self):
        bad=copy.deepcopy(self.data)
        bad["pages"][70]["chapter"]=2
        self.assertTrue(any("mismatch" in e for e in ledger.check(bad,self.manifest,allow_unprocessed=True)))
    def test_migration_completed(self):
        self.assertGreaterEqual(run()[0],196)
        self.assertEqual(run()[1],0)
    def test_schema_and_rule_citations(self):
        count,errors=validate()
        self.assertGreaterEqual(count,196)
        self.assertEqual(errors,[])
