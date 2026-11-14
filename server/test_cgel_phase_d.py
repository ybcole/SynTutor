import unittest

from cgel_phase_d import correct_selected_sentence


class PhaseDCorrectionTests(unittest.TestCase):
    def test_single_surface_error_is_corrected(self):
        result = correct_selected_sentence("The guests paniced at the noise.")
        self.assertFalse(result["production_enabled"])
        self.assertEqual(result["status"], "candidate_correction")
        self.assertEqual(result["correction"], "The guests panicked at the noise.")
        self.assertEqual(len(result["best_candidate"]["edits"]), 1)
        self.assertEqual(result["best_candidate"]["lineage"][0]["status"],
                         "targeted_cleared")
        self.assertTrue(result["original"]["findings"][0]["learner_explanation"])
        self.assertIn("not proof", result["caveat"])

    def test_independent_errors_are_combined(self):
        sentence = "The guests paniced and the room was enough warm."
        result = correct_selected_sentence(sentence)
        self.assertEqual(result["status"], "candidate_correction")
        self.assertEqual(result["correction"],
                         "The guests panicked and the room was warm enough.")
        edits = result["best_candidate"]["edits"]
        self.assertEqual(len(edits), 2)
        spans = sorted(edit["span"] for edit in edits)
        self.assertLessEqual(spans[0][1], spans[1][0])
        self.assertEqual(result["best_candidate"]["new_rule_ids"], [])

    def test_one_round_can_leave_a_persisting_finding(self):
        sentence = "The guests paniced and the room was enough warm."
        result = correct_selected_sentence(sentence, max_candidates=1)
        self.assertEqual(result["status"], "partial_candidate_correction")
        self.assertIsNotNone(result["correction"])
        statuses = {row["status"] for row in result["best_candidate"]["lineage"]}
        self.assertIn("persists", statuses)

    def test_finding_without_edit_is_unresolved(self):
        result = correct_selected_sentence("We perused.")
        self.assertEqual(result["status"], "no_safe_correction")
        self.assertIsNone(result["correction"])
        unresolved = {finding["rule_id"] for finding in result["unresolved_findings"]}
        self.assertIn("COMP-063", unresolved)
        self.assertIn("COMP-189", unresolved)

    def test_clean_sentence_has_no_correction(self):
        result = correct_selected_sentence("The guests arrived at dawn.")
        self.assertEqual(result["status"], "no_findings")
        self.assertIsNone(result["correction"])
        self.assertEqual(result["original"]["findings"], [])

    def test_candidate_limit_is_respected(self):
        result = correct_selected_sentence(
            "The guests paniced and the room was enough warm.", max_candidates=1)
        self.assertLessEqual(len(result["candidates"]), 1)

    def test_selection_bounds(self):
        self.assertEqual(correct_selected_sentence("")["status"], "not_evaluated")
        self.assertEqual(correct_selected_sentence("")["blocked"], ["empty_selection"])
        too_long = correct_selected_sentence("a" * 1201)
        self.assertEqual(too_long["status"], "not_evaluated")
        self.assertIn("selection_too_long", too_long["blocked"])

    def test_all_findings_remain_candidate_only(self):
        result = correct_selected_sentence("The guests paniced at the noise.")
        for finding in result["original"]["findings"]:
            self.assertFalse(finding["production_enabled"])
            self.assertEqual(finding["rule_type"], "constraint")
            self.assertTrue(finding["source_pages"])


if __name__ == "__main__":
    unittest.main()
