"""Synthetic regression tests for frozen run_textbook_h01_h02.py scoring logic.

Never runs SynTutor on any of the 100 final evaluation sentences.
"""

from __future__ import annotations

import csv
import json
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


class TestFrozenTextbookEvaluator(unittest.TestCase):
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
            "error_spans": [(4, 7)],  # exact char span of 'dog' inside 'dog chase'
            "error_surfaces": ["dog"],
            "correction": "The dogs chase the cat.",
            "anchor_valid": True,
        }
        sc = runner.score_h02_fair_outcomes(row, arm_b_pkt)
        self.assertTrue(sc["O1_judgment"])
        self.assertTrue(sc["O2_localization"])
        self.assertTrue(sc["O3_correction"])
        self.assertTrue(sc["O4_no_incorrect_or_unsupported"])
        self.assertTrue(sc["O4_decided_clean"])
        self.assertEqual(sc["fair_composite_0_4"], 4)

    def test_abstention_reported_separately_and_cannot_game_scores(self):
        row_u = {
            "Sentence ID": "SYN-U2",
            "Sentence text": "She did not went.",
            "Grammatical status": "Ungrammatical",
            "Affected words": "did not went",
            "Expected correction": "She didn't go.",
            "Valid alternatives": "None",
            "SynTutor rule mapping": "C-AUX-FORM",
        }
        pkt_abstain = {
            "verdict": "unverified", "error_spans": [], "error_surfaces": [],
            "correction": None, "anchor_valid": True,
        }
        sc = runner.score_h02_fair_outcomes(row_u, pkt_abstain)
        self.assertTrue(sc["abstained"])
        self.assertFalse(sc["detected_ungrammatical"])
        self.assertFalse(sc["O1_judgment"])
        self.assertFalse(sc["O2_localization"])
        self.assertFalse(sc["O3_correction"])
        # Principled abstention is NOT a demonstrable falsehood,
        # BUT O4_decided_clean and composite MUST stay 0 so abstaining cannot win!
        self.assertTrue(sc["O4_no_incorrect_or_unsupported"])
        self.assertFalse(sc["O4_decided_clean"])
        self.assertEqual(sc["fair_composite_0_4"], 0)

        # Verify _arm_breakdown separates abstention from detection & false positives
        rows_mock = [
            {"Grammatical status": "Ungrammatical", "arm_a_fair": sc},
            {"Grammatical status": "Grammatical", "arm_a_fair": runner.score_h02_fair_outcomes(
                {**row_u, "Grammatical status": "Grammatical", "Sentence text": "She did not go.", "Affected words": "None"},
                pkt_abstain,
            )},
        ]
        bd = runner._arm_breakdown(rows_mock, "arm_a_fair")
        self.assertEqual(bd["overall_abstention_rate"]["rate"], 1.0)
        self.assertEqual(bd["ungrammatical_error_detection_rate"]["rate"], 0.0)
        self.assertEqual(bd["grammatical_false_positive_rate"]["rate"], 0.0)
        self.assertEqual(bd["grammatical_abstention_rate"]["rate"], 1.0)

    def test_position_aware_localization_rejects_wrong_occurrence_of_repeated_word(self):
        row = {
            "Sentence ID": "SYN-REP",
            "Sentence text": "The wine from the shop is better than the from France.",
            "Grammatical status": "Ungrammatical",
            "Affected words": "the from France",
            "Expected correction": "The wine from the shop is better than that from France.",
            "Valid alternatives": "None",
            "SynTutor rule mapping": "PHR-126",
        }
        # Target span is 'the from France' at [38, 53)
        tspans = runner.resolve_target_char_spans(row["Sentence text"], row["Affected words"])
        self.assertEqual(tspans, [(38, 53)])

        # Flagging the EARLIER 'The' at [0, 3) shares the word 'the' but MUST FAIL!
        pkt_wrong_occ = {
            "verdict": "ungrammatical", "error_spans": [(0, 3)], "error_surfaces": ["The"],
            "correction": None, "anchor_valid": True,
        }
        sc_wrong = runner.score_h02_fair_outcomes(row, pkt_wrong_occ)
        self.assertFalse(sc_wrong["O2_localization"])
        self.assertTrue(sc_wrong["wrong_target"])
        self.assertFalse(sc_wrong["O4_no_incorrect_or_unsupported"])

        # Flagging the ACTUAL 'the' inside 'the from France' at [38, 41) MUST PASS!
        pkt_right_occ = {
            "verdict": "ungrammatical", "error_spans": [(38, 41)], "error_surfaces": ["the"],
            "correction": "The wine from the shop is better than that from France.",
            "anchor_valid": True,
        }
        sc_right = runner.score_h02_fair_outcomes(row, pkt_right_occ)
        self.assertTrue(sc_right["O2_localization"])
        self.assertFalse(sc_right["wrong_target"])
        self.assertTrue(sc_right["O4_decided_clean"])

    def test_position_aware_localization_rejects_overly_broad_whole_sentence_span(self):
        sent = "The wine from the shop is better than the from France."
        row = {
            "Sentence ID": "SYN-BROAD",
            "Sentence text": sent,
            "Grammatical status": "Ungrammatical",
            "Affected words": "the from France",
            "Expected correction": "The wine from the shop is better than that from France.",
            "Valid alternatives": "None",
            "SynTutor rule mapping": "PHR-126",
        }
        pkt_broad = {
            "verdict": "ungrammatical", "error_spans": [(0, len(sent))], "error_surfaces": [sent],
            "correction": None, "anchor_valid": True,
        }
        sc = runner.score_h02_fair_outcomes(row, pkt_broad)
        self.assertFalse(sc["O2_localization"])
        self.assertTrue(sc["overly_broad_span"])
        self.assertTrue(sc["wrong_target"])
        self.assertFalse(sc["O4_no_incorrect_or_unsupported"])

    def test_discontinuous_affected_words_resolution_across_all_100_csv_rows(self):
        # Static CSV schema verification ONLY (never runs SynTutor on CSV!)
        real_csv = ROOT / "docs/audits/h01_h02_evaluation_methodology/H01_H02_PROPOSED_100_SENTENCES.csv"
        with real_csv.open(encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        for r in rows:
            if r["Grammatical status"] == "Ungrammatical":
                spans = runner.resolve_target_char_spans(r["Sentence text"], r["Affected words"])
                self.assertTrue(len(spans) >= 1, f"Could not resolve target span for {r['Sentence ID']}: {r['Affected words']}")

    def test_h01_partial_checks_genuine_structural_attachment_and_limits_scope(self):
        # G17: 'Few students worry about exams until the end of term.'
        # Correct structure: outer VP -> [inner VP -> [V('worry'), PP('about exams')], PP('until the end of term')]
        good_g17 = {
            "root": {
                "label": "S",
                "children": [
                    {"label": "NP", "children": [{"word": "Few"}, {"word": "students"}]},
                    {"label": "VP", "children": [
                        {"label": "VP", "children": [
                            {"label": "V", "children": [{"word": "worry"}]},
                            {"label": "PP", "children": [{"word": "about"}, {"word": "exams"}]},
                        ]},
                        {"label": "PP", "children": [{"word": "until"}, {"word": "the"}, {"word": "end"}, {"word": "of"}, {"word": "term"}]},
                    ]},
                ],
            }
        }
        res_good = runner.score_h01_partial("G17", good_g17)
        self.assertTrue(res_good["all_passed"])
        self.assertTrue(len(res_good["checked_relations"]) >= 5)
        self.assertTrue(len(res_good["not_checked_relations"]) >= 1)

        # Flat bad VP attaching BOTH PPs as sisters of V MUST FAIL vp_adjunct_sister!
        flat_bad_g17 = {
            "root": {
                "label": "S",
                "children": [
                    {"label": "NP", "children": [{"word": "Few"}, {"word": "students"}]},
                    {"label": "VP", "children": [
                        {"label": "V", "children": [{"word": "worry"}]},
                        {"label": "PP", "children": [{"word": "about"}, {"word": "exams"}]},
                        {"label": "PP", "children": [{"word": "until"}, {"word": "the"}, {"word": "end"}, {"word": "of"}, {"word": "term"}]},
                    ]},
                ],
            }
        }
        res_bad = runner.score_h01_partial("G17", flat_bad_g17)
        self.assertFalse(res_bad["all_passed"])
        adj_chk = next(c for c in res_bad["checks"] if c["name"].startswith("vp_adjunct_sister"))
        self.assertFalse(adj_chk["passed"])

        # G16: S-adverbial 'in my opinion' inside VP instead of directly under S MUST FAIL parent check!
        bad_g16 = {
            "root": {
                "label": "S",
                "children": [
                    {"label": "NP", "children": [{"word": "Murdstone"}]},
                    {"label": "VP", "children": [
                        {"label": "V", "children": [{"word": "brought"}]},
                        {"label": "NP", "children": [{"word": "the"}, {"word": "child"}]},
                        {"label": "Prt", "children": [{"word": "up"}]},
                        {"label": "AdvP", "children": [{"word": "too"}, {"word": "strictly"}]},
                        {"label": "PP", "children": [{"word": "in"}, {"word": "my"}, {"word": "opinion"}]},
                    ]},
                ],
            }
        }
        res_g16 = runner.score_h01_partial("G16", bad_g16)
        self.assertFalse(res_g16["all_passed"])
        par_chk = next(c for c in res_g16["checks"] if c["name"].startswith("parent:"))
        self.assertFalse(par_chk["passed"])

    def test_exact_mcnemar_and_wilcoxon(self):
        m = runner.exact_mcnemar([True] * 8 + [False] * 2, [False] * 10)
        self.assertAlmostEqual(m["p_value_exact_two_sided"], 2 * (0.5 ** 8), places=5)
        w = runner.paired_wilcoxon_signed_rank([4, 4, 4, 4, 4, 4, 4, 4], [2, 2, 2, 2, 2, 2, 2, 2])
        self.assertEqual(w["rank_biserial_r"], 1.0)
        self.assertLess(w["p_value_approx"], 0.05)

    def test_end_to_end_smoke_on_synthetic_fixtures_verifies_both_arms_and_sentinel(self):
        real_csv = ROOT / "docs/audits/h01_h02_evaluation_methodology/H01_H02_PROPOSED_100_SENTENCES.csv"
        with real_csv.open(encoding="utf-8") as fh:
            real_sents = {r["Sentence text"].strip().lower() for r in csv.DictReader(fh)}
        fixtures = [
            {
                "Sentence ID": "SYN-G1", "Pair ID": "SP1", "Sentence text": "The dog chased the cat.",
                "Origin type": "Synthetic", "Source": "Unit test", "Chapter and page": "N/A",
                "Grammar topic": "Transitive", "SynTutor rule mapping": "C-SUBJECT-AGREEMENT",
                "Difficulty": "Simple", "Grammatical status": "Grammatical", "Affected words": "None",
                "Grammatical reason": "Well-formed", "Expected correction": "No correction required",
                "Valid alternatives": "N/A", "Reference answer availability": "Fixture",
                "H01 eligibility": "Fixture", "H02 eligibility": "Fixture",
                "Previous development use": "No", "Development exposure detail": "Fixture",
                "Verification status": "Fixture",
            },
            {
                "Sentence ID": "SYN-U1", "Pair ID": "SP1", "Sentence text": "The dog chase the cat.",
                "Origin type": "Synthetic", "Source": "Unit test", "Chapter and page": "N/A",
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
            h02_det = json.loads((out_dir / "h02_details.json").read_text())
            # Verify Arm A extracted real exact char spans & fired rules on SYN-U1!
            self.assertEqual(h02_det[1]["arm_a_packet"]["verdict"], "ungrammatical")
            self.assertTrue(len(h02_det[1]["arm_a_packet"]["error_spans"]) >= 1)
            self.assertTrue(h02_det[1]["arm_a_fair"]["O2_localization"])
            # Verify Arm B also functioned cleanly with exact char span localization!
            self.assertEqual(h02_det[0]["arm_b_packet"]["verdict"], "grammatical")
            self.assertEqual(h02_det[1]["arm_b_packet"]["verdict"], "ungrammatical")
            self.assertTrue(len(h02_det[1]["arm_b_packet"]["error_spans"]) == 1)
            self.assertTrue(h02_det[1]["arm_b_fair"]["O2_localization"])
            self.assertTrue(h02_det[1]["arm_b_fair"]["O3_correction"])
            self.assertTrue(h02_det[1]["arm_b_fair"]["O4_decided_clean"])
            # Verify separate abstention breakdown keys exist
            bd_a = report["h02"]["abstention_and_detection_breakdown"]["arm_a_rule_grounded"]
            self.assertIn("overall_abstention_rate", bd_a)
            self.assertIn("ungrammatical_error_detection_rate", bd_a)
            self.assertIn("grammatical_false_positive_rate", bd_a)


if __name__ == "__main__":
    unittest.main()
