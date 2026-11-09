"""Parser-backed smoke tests; run only in the configured model CI workflow."""
import unittest
from pathlib import Path
from unittest.mock import patch

from jsonschema import Draft202012Validator

import api
import parse_engine


ROOT = Path(__file__).resolve().parents[1]
M1_SCHEMA = __import__("json").loads(
    (ROOT / "docs" / "canonical-burton-roberts-tree.schema.json").read_text(encoding="utf-8")
)
M1_VALIDATOR = Draft202012Validator(M1_SCHEMA)


class ParserBackedRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Force this test process to prove that the configured models can load.
        parse_engine._nlp = None
        parse_engine._load_error = None

    def test_real_spacy_benepar_single_sentence_parse(self):
        analysis = parse_engine.analyze("The students laugh.")
        self.assertEqual(analysis["sentence"], "The students laugh.")
        self.assertEqual(analysis["sentence_count"], 1)
        self.assertTrue(analysis["parse_string"])
        self.assertIsInstance(analysis["root"], dict)
        self.assertEqual([row["t"] for row in analysis["tokens"]],
                         ["The", "students", "laugh", "."])

    def test_final_d1_projects_different_constructions_with_original_words(self):
        cases = [
            ("The dog barked.", "S", {"V [intrans] [past]"}),
            ("She  read the book.", "S", {"V [trans] [past]", "DET", "NOM"}),
            ("The nurse have arrived.", "S", {"PERF [pres]", "V [intrans]"}),
            ("The letter was read by Mara.", "S", {"PASS [past]", "V [trans]", "•₁"}),
            ("What did Jon buy?", "S-dbar", {"S″", "C2₁", "C1₂", "TENSE [past]", "•₁", "•₂"}),
            ("Where did Lisa put it?", "S-dbar", {"V [complex]", "PP", "•₁"}),
            ("She persuaded Mara to leave.", "S", {"V(II) [past]", "[-tense]", "•₁"}),
        ]
        with patch.object(api, "classify", return_value=None):
            for sentence, root_label, expected in cases:
                with self.subTest(sentence=sentence):
                    result = api.build_payload(sentence)
                    analysis = result["br_analysis"]
                    self.assertEqual(analysis["status"], "normalized", analysis["reasons"])
                    tree = analysis["tree"]
                    self.assertEqual(tree["sentence"], sentence)
                    self.assertEqual(tree["root"]["label"], root_label)
                    self.assertFalse(list(M1_VALIDATOR.iter_errors(tree)))
                    labels = {" ".join(lines) for lines in analysis["display_labels"].values()}
                    self.assertTrue(expected <= labels, (expected, labels))

    def test_real_parser_selects_second_sentence_without_clamping(self):
        text = "The students laugh. The birds sing."
        analysis = parse_engine.analyze(text, sentence_index=1)
        self.assertEqual(analysis["sentence_count"], 2)
        self.assertEqual(analysis["sentence_index"], 1)
        self.assertEqual(analysis["sentence"], "The birds sing.")
        self.assertEqual([row["t"] for row in analysis["tokens"]],
                         ["The", "birds", "sing", "."])

    def test_out_of_range_sentence_index_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "out of range"):
            parse_engine.analyze("The students laugh.", sentence_index=1)

    def test_real_generator_api_returns_m1_envelope_for_supported_v2_parse(self):
        with patch.object(api, "classify", return_value=None):
            payload = api.build_payload("The students laugh.", chapter=2)

        self.assertEqual(payload["br_analysis"]["status"], "normalized",
                         payload["br_analysis"])
        envelope = payload["br_analysis"]["tree"]
        self.assertEqual(envelope["convention_profile"]["version"], "V2")
        self.assertEqual(envelope["root"]["label"], "S")
        self.assertEqual([node["label"] for node in envelope["root"]["children"]],
                         ["NP", "VP"])
        self.assertEqual(list(M1_VALIDATOR.iter_errors(envelope)), [])
        self.assertEqual(payload["tree"], payload["candidate_tree"])
        self.assertEqual(payload["meta"]["tree_authority"].split(";")[0],
                         "B-R canonical analysis is in br_analysis")

    def test_real_generator_api_handles_second_sentence_in_a_passage(self):
        passage = "The students laugh. The birds sing."
        with patch.object(api, "classify", return_value=None):
            payload = api.build_payload(passage, chapter=2, sentence_index=1)

        self.assertEqual(payload["meta"]["sentence_count"], 2)
        self.assertEqual(payload["meta"]["target_sentence"], 2)
        self.assertEqual(payload["parse"]["text"], "The birds sing.")
        self.assertEqual(payload["br_analysis"]["status"], "normalized",
                         payload["br_analysis"])
        self.assertEqual(list(M1_VALIDATOR.iter_errors(payload["br_analysis"]["tree"])), [])

    def test_real_generator_api_projects_the_first_final_d1_construction(self):
        with patch.object(api, "classify", return_value=None):
            payload = api.build_payload("The tired students sighed quietly.")

        analysis = payload["br_analysis"]
        self.assertEqual(analysis["status"], "normalized", analysis["reasons"])
        envelope = analysis["tree"]
        self.assertEqual(envelope["convention_profile"]["profile_id"], "FINAL-D1")
        self.assertEqual(list(M1_VALIDATOR.iter_errors(envelope)), [])
        vp, adjunct = envelope["root"]["children"][1]["children"]
        self.assertEqual(adjunct["label"], "AdvP")
        self.assertEqual(vp["children"][0]["features"], ["intrans", "past"])
        self.assertEqual(payload["tree"], payload["candidate_tree"])

    def test_corrected_sentence_is_independently_parsed_and_normalized(self):
        original = "The students laughs."
        corrected = "The students laugh."
        synthetic_summary = {
            "verdict": "ungrammatical", "valid": False,
            "valid_edges": 1, "violated_edges": 1, "unrated_edges": 0,
            "explanation": "Synthetic correction-path trigger.",
            "constraints_fired": ["TEST-TRIGGER"], "checker_errors": [],
            "suggested": True,
        }
        correction = {
            "corrected_sentence": corrected,
            "edits": [{
                "kind": "replacement",
                "original": "laughs",
                "corrected": "laugh",
            }],
        }
        with patch.object(api, "classify", return_value=None), \
             patch.object(api, "evaluate", return_value={
                 "details": {}, "summary": synthetic_summary,
             }), \
             patch.object(api.corrections, "has_actionable", return_value=True), \
             patch.object(api.corrections, "assemble", return_value=correction), \
             patch.object(api.corrections, "describe", return_value="Synthetic correction."), \
             patch.object(api, "apply_plain_language"), \
             patch.object(api, "plain_text", side_effect=lambda value: value), \
             patch.object(api, "_contrastive", return_value=""), \
             patch.object(api, "_pipeline_narration", return_value={"stages": []}), \
             patch.object(api, "_rule_concepts", return_value=[]):
            payload = api.build_payload(original, chapter=2)

        corrected_result = payload["summary"]["correction"]["corrected_br_analysis"]
        self.assertEqual(payload["parse"]["text"], original)
        self.assertEqual(payload["br_analysis"]["status"], "normalized")
        self.assertEqual(corrected_result["status"], "normalized", corrected_result)
        self.assertEqual(corrected_result["tree"]["sentence"], corrected)
        self.assertEqual(list(M1_VALIDATOR.iter_errors(corrected_result["tree"])), [])
        self.assertTrue(payload["summary"]["correction"]["alignment"]["edits"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
