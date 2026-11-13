"""Real-model coverage for whitespace around learner submissions."""
import unittest

from parse_engine import ParseFailure, analyze


class ParserWhitespaceTests(unittest.TestCase):
    def test_boundary_whitespace_preserves_source_offsets_and_tree(self):
        sentence = "The birds sing."
        baseline = analyze(sentence)
        for prefix, suffix in [("  ", ""), ("\r\n\t", " \r\n"), ("\u2003", "\t"), ("", "  ")]:
            with self.subTest(prefix=prefix, suffix=suffix):
                text = prefix + sentence + suffix
                result = analyze(text)
                self.assertEqual(result["sentence"], sentence)
                self.assertEqual(result["sentence_count"], 1)
                self.assertEqual(result["parse_string"], baseline["parse_string"])
                self.assertEqual(result["sentences"][0]["start"], len(prefix))
                self.assertEqual(result["sentences"][0]["end"], len(prefix) + len(sentence))
                self.assertEqual(len(result["tokens"]), len(baseline["tokens"]))
                for token in result["tokens"]:
                    self.assertEqual(text[token["start"]:token["end"]], token["t"])

    def test_whitespace_only_input_is_a_parse_failure(self):
        for text in ("", " \t\r\n", "\u2003"):
            with self.subTest(text=text), self.assertRaises(ParseFailure):
                analyze(text)


if __name__ == "__main__":
    unittest.main()
