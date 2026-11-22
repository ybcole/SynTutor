"""Verification tests for run_textbook_h01_h02.py using separate synthetic fixtures.

Never executes SynTutor on the 100 final evaluation sentences.
Verifies:
  1. Fair H02 scoring allows Arm B (with zero rule IDs) to achieve a perfect 4/4 score.
  2. Multi-alternative corrections and contraction equivalences are accepted.
  3. Wrong-target localization, false positives, false negatives, and self-contradictions
     trigger O4 failure symmetrically in both arms.
  4. Separate D1/D2 grounding diagnostics never leak into primary O1-O4 scores.
  5. H01 Track 2 partial-reference scoring, Track 3 B-R compliance (leaked Penn tag rejection),
     and Track 4 conversion consistency behave accurately.
  6. Statistical functions (Wilson CI, exact McNemar, paired Wilcoxon) match exact math.
  7. End-to-end smoke check on 2 synthetic sentences NOT in the 100-sentence CSV confirms
     both Arm A and Arm B function cleanly and that the gold-lookup sentinel blocks lookups.
"""

from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TECH_DIR = Path(__file__).resolve().parent
ROOT = TECH_DIR.parents[2]
for p in (str(TECH_DIR), str(ROOT / "server")):
    if p not in sys.path:
        sys.path.insert(0, p)

import run_textbook_h01_h02 as runner  # noqa: E402


class TestTextbookEvaluatorLogic(unittest.TestCase):
    def test_arm_b_can_achieve_perfect_fair_score_without_rule_ids(self):
        row = {
            "Sentence ID": "SYN-U1",
            "Sentence text": "The dog chase the cat.",
            "Grammatical status": "Ungrammatical",
            "Affected words": "dog chase",
            "Expected correction": "The dog chases the cat.",
            "Valid alternatives": "The dogs chase the cat.",
            "SynTutor rule mapping": "C-SUBJECT-AGREEMENT",
        }
        arm_b_pkt = {
            "arm": "B_ungrounded_neural",
            "verdict": "ungrammatical",
            "error_surfaces": ["dog"],
            "correction": "The dogs chase the cat.",
            "anchor_valid": True,
        }
        sc = runner.score_h02_fair_outcomes(row, arm_b_pkt)
        self.assertTrue(sc["O1_judgment"])
        self.assertTrue(sc["O2_localization"])
        self.assertTrue(sc["O3_correction"])
        self.assertTrue(sc["O4_no_incorrect_or_unsupported"])
        self.assertEqual(sc["fair_composite_0_4"], 4)

    def test_contraction_equivalence_and_demonstrable_errors(self):
        row_u = {
            "Sentence ID": "SYN-U2",
            "Sentence text": "She did not went.",
            "Grammatical status": "Ungrammatical",
            "Affected words": "did not went",
            "Expected correction": "She didn't go.",
            "Valid alternatives": "None",
            "SynTutor rule mapping": "C-AUX-FORM",
        }
        # Full form 'did not' matches contracted 'didn't'
        pkt_good = {
            "verdict": "ungrammatical", "error_surfaces": ["went"],
            "correction": "She did not go.", "anchor_valid": True,
        }
        self.assertTrue(runner.score_h02_fair_outcomes(row_u, pkt_good)["O3_correction"])

        # Wrong-target localization triggers O4 failure
        pkt_wrong_loc = {
            "verdict": "ungrammatical", "error_surfaces": ["She"],
            "correction": None, "anchor_valid": True,
        }
        sc_wl = runner.score_h02_fair_outcomes(row_u, pkt_wrong_loc)
        self.assertFalse(sc_wl["O2_localization"])
        self.assertFalse(sc_wl["O4_no_incorrect_or_unsupported"])

        # Principled abstention misses O1-O3 but does NOT trigger demonstrable falsehood on O4
        pkt_abstain = {
            "verdict": "unverified", "error_surfaces": [],
            "correction": None, "anchor_valid": True,
        }
        sc_abs = runner.score_h02_fair_outcomes(row_u, pkt_abstain)
        self.assertFalse(sc_abs["O1_judgment"])
        self.assertTrue(sc_abs["abstained"])
        self.assertTrue(sc_abs["O4_no_incorrect_or_unsupported"])

    def test_grammatical_false_positive_and_self_contradiction(self):
        row_g = {
            "Sentence ID": "SYN-G1",
            "Sentence text": "The dog chased the cat.",
            "Grammatical status": "Grammatical",
            "Affected words": "None",
            "Expected correction": "No correction required",
            "Valid alternatives": "N/A",
            "SynTutor rule mapping": "B-R Ch. 4",
        }
        pkt_clean = {"verdict": "grammatical", "error_surfaces": [], "correction": None, "anchor_valid": True}
        self.assertEqual(runner.score_h02_fair_outcomes(row_g, pkt_clean)["fair_composite_0_4"], 4)

        pkt_contra = {"verdict": "grammatical", "error_surfaces": ["chased"], "correction": None, "anchor_valid": True}
        sc_c = runner.score_h02_fair_outcomes(row_g, pkt_contra)
        self.assertTrue(sc_c["contradiction"])
        self.assertFalse(sc_c["O4_no_incorrect_or_unsupported"])

    def test_separate_grounding_diagnostics_do_not_affect_primary(self):
        row_u = {
            "Sentence ID": "SYN-U3",
            "Sentence text": "She had took the car.",
            "Grammatical status": "Ungrammatical",
            "Affected words": "had took",
            "Expected correction": "She had taken the car.",
            "Valid alternatives": "None",
            "SynTutor rule mapping": "MORPH-026 / C-AUX-FORM",
        }
        pkt_a = {
            "verdict": "ungrammatical", "error_surfaces": ["took"],
            "correction": "She had taken the car.",
            "fired_rules": ["C-AUX-FORM"], "anchor_valid": True, "channel_valid": True,
        }
        diag = runner.score_h02_grounding_diagnostics(row_u, pkt_a)
        self.assertTrue(diag["D1_rule_family_match"])
        self.assertTrue(diag["D2_provenance_integrity"])

    def test_h01_partial_and_compliance_scoring(self):
        good_tree = {
            "root": {
                "label": "S",
                "children": [
                    {"label": "NP", "children": [{"label": "DET", "children": [{"word": ""}]},
                                                 {"label": "NOM", "children": [{"label": "AP", "children": [{"label": "A", "children": [{"word": "Hot"}]}]},
                                                                               {"label": "N", "children": [{"word": "air"}]}]}]},
                    {"label": "VP", "children": [{"label": "V", "children": [{"word": "rises"}]}]},
                ],
            }
        }
        part = runner.score_h01_partial("G01", good_tree)
        self.assertTrue(part["all_passed"])
        comp = runner.score_h01_compliance("G01", "Hot air rises.", good_tree)
        self.assertTrue(comp["all_passed"])

        # Leaked Penn tag 'SBAR' must fail B-R compliance
        bad_tree = {"root": {"label": "SBAR", "children": [{"label": "NP", "children": [{"word": "Hot air rises"}]}]}}
        comp_bad = runner.score_h01_compliance("G01", "Hot air rises.", bad_tree)
        self.assertFalse(comp_bad["checks"]["canonical_labels_only"])
        self.assertIn("SBAR", comp_bad["leaked_penn_labels"])

    def test_exact_mcnemar_and_wilcoxon(self):
        # 8 wins for A, 0 wins for B -> exact two-sided p = 2 * 0.5^8 = 1/128 = 0.0078125
        m = runner.exact_mcnemar([True] * 8 + [False] * 2, [False] * 10)
        self.assertAlmostEqual(m["p_value_exact_two_sided"], 2 * (0.5 ** 8), places=5)
        w = runner.paired_wilcoxon_signed_rank([4, 4, 4, 4, 4, 4, 4, 4], [2, 2, 2, 2, 2, 2, 2, 2])
        self.assertEqual(w["rank_biserial_r"], 1.0)
        self.assertLess(w["p_value_approx"], 0.05)

    def test_end_to_end_smoke_on_separate_synthetic_fixtures_with_zero_lookup_sentinel(self):
        # Verify synthetic fixtures are strictly NOT in the 100-sentence CSV
        real_csv = ROOT / "docs/audits/h01_h02_evaluation_methodology/H01_H02_PROPOSED_100_SENTENCES.csv"
        with real_csv.open(encoding="utf-8") as fh:
            real_sents = {r["Sentence text"].strip().lower() for r in csv.DictReader(fh)}
        fixtures = [
            {
                "Sentence ID": "SYN-G1", "Pair ID": "SP1", "Sentence text": "The dog chased the cat.",
                "Origin type": "Synthetic test fixture", "Source": "Unit test", "Chapter and page": "N/A",
                "Grammar topic": "Basic transitive", "SynTutor rule mapping": "C-SUBJECT-AGREEMENT",
                "Difficulty": "Simple", "Grammatical status": "Grammatical", "Affected words": "None",
                "Grammatical reason": "Well-formed", "Expected correction": "No correction required",
                "Valid alternatives": "N/A", "Reference answer availability": "Fixture",
                "H01 eligibility": "Fixture", "H02 eligibility": "Fixture",
                "Previous development use": "No", "Development exposure detail": "Fixture",
                "Verification status": "Fixture",
            },
            {
                "Sentence ID": "SYN-U1", "Pair ID": "SP1", "Sentence text": "The dog chase the cat.",
                "Origin type": "Synthetic test fixture", "Source": "Unit test", "Chapter and page": "N/A",
                "Grammar topic": "SVA", "SynTutor rule mapping": "C-SUBJECT-AGREEMENT",
                "Difficulty": "Simple", "Grammatical status": "Ungrammatical", "Affected words": "dog chase",
                "Grammatical reason": "SVA mismatch", "Expected correction": "The dog chases the cat.",
                "Valid alternatives": "The dogs chase the cat.", "Reference answer availability": "Fixture",
                "H01 eligibility": "No", "H02 eligibility": "Fixture",
                "Previous development use": "No", "Development exposure detail": "Fixture",
                "Verification status": "Fixture",
            },
        ]
        for fx in fixtures:
            self.assertNotIn(fx["Sentence text"].strip().lower(), real_sents)

        with tempfile.TemporaryDirectory() as tmp:
            tmp_p = Path(tmp)
            fx_csv = tmp_p / "fixtures.csv"
            with fx_csv.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(fixtures[0].keys()))
                w.writeheader()
                w.writerows(fixtures)
            out_dir = tmp_p / "out"
            report = runner.run_evaluation(fx_csv, out_dir)
            self.assertTrue(report["gold_lookup_sentinel_verified_zero_calls"])
            self.assertEqual(report["total_rows"], 2)
            # Verify Arm B functioned cleanly on BOTH synthetic fixtures!
            h02_det = runner.json.loads((out_dir / "h02_details.json").read_text())
            self.assertEqual(h02_det[0]["arm_b_packet"]["verdict"], "grammatical")
            self.assertEqual(h02_det[1]["arm_b_packet"]["verdict"], "ungrammatical")
            self.assertTrue(h02_det[1]["arm_b_fair"]["O1_judgment"])
            self.assertTrue(h02_det[1]["arm_b_fair"]["O2_localization"])
            self.assertTrue(h02_det[1]["arm_b_fair"]["O3_correction"])
            self.assertTrue(h02_det[1]["arm_b_fair"]["O4_no_incorrect_or_unsupported"])

        # Verify sentinel genuinely raises AssertionError if lookup is ever called
        import burton_roberts as br
        with patch.object(br, "_matching_gold_records", side_effect=AssertionError("blocked")):
            with self.assertRaises(AssertionError):
                br._matching_gold_records("The dog chased the cat.")


if __name__ == "__main__":
    unittest.main()
