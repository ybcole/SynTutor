"""Reusable Cambridge batch QA: existing verified pages plus adversarial drift tests.

These tests do not assert that self-reported reading proves linguistic truth.
"""
import copy
import unittest

from tools import ledger
from tools.cgel_batch_gate import check_batch, scaffold


def completed_manifest(page, rule_id):
    row = ledger.load(ledger.LEDGER)["pages"][page - 1]
    return {
        "manifest_version": 1, "chapter": row["chapter"],
        "printed_start": page, "printed_end": page,
        "report": row["evidence"],
        "source_pdf_page_offset": 20,
        "source_anchor": {"printed_page": page, "pdf_page": page + 20},
        "added_rule_ids": [rule_id],
        "page_checks": [{
            "page": page, "status": "extracted",
            "section": "Source-cited Cambridge grammatical section",
            "summary": "All relevant printed page prose and its exceptions were checked.",
            "source_checked": True,
            "nonprose_present": True,
            "layout_checked": True,
            "exceptions_checked": True,
            "unresolved_items": [],
        }],
    }


class TestCambridgeBatchGate(unittest.TestCase):
    def test_existing_source_extracted_examples_meet_same_gates(self):
        for page, rid in [(211, "OTH-570"), (212, "OTH-587"),
                          (106, "COMP-034"), (105, "COMP-031")]:
            with self.subTest(page=page, rule=rid):
                self.assertEqual(check_batch(completed_manifest(page, rid)), [])

    def test_scaffold_cannot_fake_source_verification(self):
        draft = scaffold(3, 211, 212,
                         "sources/cambridge/chapter_03/PHASE_B_PP211_212_REPORT.md")
        errors = check_batch(draft)
        self.assertTrue(errors)
        self.assertTrue(any("source" in err.lower() or "status" in err.lower()
                            for err in errors))
        self.assertEqual(draft["page_checks"][0]["status"], "pending")
        self.assertEqual(draft["page_checks"][0]["unresolved_items"], ["NOT_YET_READ"])

    def test_exact_page_inventory_prevents_skip_or_duplication(self):
        good = completed_manifest(211, "OTH-570")
        wrong = copy.deepcopy(good)
        wrong["page_checks"].append(copy.deepcopy(wrong["page_checks"][0]))
        self.assertIn("Every printed page must have exactly one page_checks entry",
                      check_batch(wrong))
        wrong = copy.deepcopy(good)
        wrong["printed_end"] = 212
        self.assertTrue(any("Every printed page" in error
                            for error in check_batch(wrong)))
        wrong = copy.deepcopy(good)
        wrong["page_checks"][0]["status"] = "unprocessed"
        self.assertTrue(any("ledger" in error for error in check_batch(wrong)))

    def test_source_or_exceptions_not_checked_fails_closed(self):
        good = completed_manifest(211, "OTH-570")
        changes = [
            {"source_checked": False},
            {"summary": ""},
            {"section": ""},
            {"exceptions_checked": False},
            {"nonprose_present": True, "layout_checked": False},
            {"nonprose_present": None},
            {"unresolved_items": ["unreadable footnote"]},
        ]
        for fields in changes:
            with self.subTest(fields=fields):
                bad = copy.deepcopy(good)
                bad["page_checks"][0].update(fields)
                self.assertTrue(check_batch(bad))

    def test_pdf_anchor_and_page_offset_must_match_sources(self):
        good = completed_manifest(211, "OTH-570")
        bad = copy.deepcopy(good)
        bad["source_anchor"]["pdf_page"] += 1
        self.assertTrue(any("anchor" in error for error in check_batch(bad)))
        bad = copy.deepcopy(good)
        bad["source_pdf_page_offset"] = 19
        self.assertTrue(any("citations" in error for error in check_batch(bad)))
        bad = copy.deepcopy(good)
        bad["report"] = "../../../tmp/not-the-source.md"
        self.assertTrue(any("Report must" in error for error in check_batch(bad)))

    def test_added_rule_must_have_actual_overlapping_source(self):
        good = completed_manifest(211, "OTH-570")
        bad = copy.deepcopy(good)
        bad["added_rule_ids"] = ["COMP-034"]
        self.assertTrue(any("overlaps this batch" in e for e in check_batch(bad)))
        bad = copy.deepcopy(good)
        bad["added_rule_ids"] = ["OTH-570", "OTH-570"]
        self.assertTrue(any("Duplicate IDs" in e for e in check_batch(bad)))
        bad = copy.deepcopy(good)
        bad["added_rule_ids"] = ["OTH-99999"]
        self.assertTrue(any("not found" in e for e in check_batch(bad)))

    def test_contents_only_skip_requires_real_reason_and_source_check(self):
        row = ledger.load(ledger.LEDGER)["pages"][70]
        self.assertEqual(row["status"], "skipped_with_reason")
        good = {
            "manifest_version": 1, "chapter": 3,
            "printed_start": 71, "printed_end": 71,
            "report": row["evidence"],
            "source_pdf_page_offset": 20,
            "source_anchor": {"printed_page": 71, "pdf_page": 91},
            "added_rule_ids": [],
            "page_checks": [{
                "page": 71, "status": "skipped_with_reason",
                "section": "Chapter contents", "summary": "Chapter table of contents only.",
                "source_checked": True, "nonprose_present": False,
                "layout_checked": False, "exceptions_checked": True,
                "unresolved_items": [],
            }],
        }
        self.assertEqual(check_batch(good), [])
        bad = copy.deepcopy(good)
        bad["page_checks"][0]["source_checked"] = False
        self.assertTrue(any("not checked" in e for e in check_batch(bad)))


if __name__ == "__main__":
    unittest.main()
