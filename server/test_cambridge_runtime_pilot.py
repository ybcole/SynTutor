import unittest

from burton_roberts import build_canonical_analysis
from cambridge_evaluator import evaluate_cambridge
from cambridge_registry import load_runtime_registry
from parse_engine import analyze


class CambridgeRuntimePilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_runtime_registry()

    def evaluate(self, sentence):
        analysis = build_canonical_analysis(analyze(sentence))
        analysis["sentence"] = sentence
        return evaluate_cambridge(analysis, self.registry, variety="standard_english")

    def test_all_implemented_pilots_are_enabled(self):
        self.assertEqual(len(self.registry["active_rule_ids"]), 193)

    def test_final_c_rule_produces_a_runtime_finding(self):
        result = self.evaluate("The guests paniced at the noise.")
        self.assertEqual(result["status"], "evaluated")
        self.assertIn("MORPH-109", result["evaluated_rule_ids"])
        finding = next(row for row in result["findings"] if row["rule_id"] == "MORPH-109")
        self.assertEqual(finding["candidate_matches"][0]["edit_hint"]["replacement"], "k")

    def test_i_arent_rule_produces_a_runtime_finding(self):
        result = self.evaluate("I aren't on the list.")
        finding = next(row for row in result["findings"] if row["rule_id"] == "MORPH-130")
        self.assertEqual(finding["candidate_matches"][0]["edit_hint"]["replacement"], "I am not")

    def test_no_of_rule_produces_a_runtime_finding(self):
        result = self.evaluate("No of the bolts were missing.")
        finding = next(row for row in result["findings"] if row["rule_id"] == "PHR-161")
        self.assertEqual(finding["candidate_matches"][0]["edit_hint"]["replacement"], "None")

    def test_clean_sentence_passes_the_pilot(self):
        result = self.evaluate("The guests arrived at dawn.")
        self.assertEqual(result["status"], "evaluated")
        self.assertEqual(result["findings"], [])


if __name__ == "__main__":
    unittest.main()
