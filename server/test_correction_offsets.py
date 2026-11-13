"""Real-model regression for sentence-local repairs in document-offset parses."""
import unittest
from unittest.mock import patch

import api


class CorrectionOffsetTests(unittest.TestCase):
    def test_repairs_use_selected_sentence_offsets_without_changing_parser_tokens(self):
        cases = [
            ("She go home.", 0),
            ("The birds sing. She go home.", 1),
            ("The birds sing.\r\n\tShe  go home.", 1),
        ]
        with patch.object(api, "classify", return_value=None), \
             patch.object(api.corrections, "_from_text", return_value=[]):
            for text, index in cases:
                with self.subTest(text=text):
                    payload = api.build_payload(text, sentence_index=index)
                    correction = payload["summary"].get("correction")
                    self.assertIsNotNone(correction)
                    self.assertEqual(correction["corrected_sentence"], "She goes home.")
                    original = payload["parse"]["text"]
                    verb_edit = next(e for e in correction["edits"] if e["replacement"] == "goes")
                    self.assertEqual(original[verb_edit["start"]:verb_edit["end"]], "go")
                    self.assertEqual(verb_edit["original"], "go")
                    for token in payload["parse"]["tokens"]:
                        self.assertEqual(text[token["start"]:token["end"]], token["t"])
                    self.assertEqual(correction["corrected_br_analysis"]["status"], "normalized")
                    self.assertIn("goes", correction["corrected_candidate_parse"]["parse_string"])
                    self.assertTrue(correction["alignment"]["edits"])

    def test_clean_selected_sentence_has_no_correction(self):
        with patch.object(api, "classify", return_value=None):
            payload = api.build_payload("The birds sing. She goes home.", sentence_index=1)
        self.assertNotIn("correction", payload["summary"])


if __name__ == "__main__":
    unittest.main()
