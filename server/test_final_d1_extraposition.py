import unittest

try:
    from server.burton_roberts import build_canonical_analysis
    from server.parse_engine import analyze
except ImportError:
    from burton_roberts import build_canonical_analysis
    from parse_engine import analyze


class FinalD1ExtrapositionTests(unittest.TestCase):
    def test_passive_extraposition_normalizes_with_delayed_clause(self):
        sentence = "it was noticed by the critics that the book had a missing chapter."
        result = build_canonical_analysis(analyze(sentence))
        self.assertEqual(result["status"], "normalized", result.get("reasons"))
        root = result["tree"]["root"]
        self.assertEqual(root["label"], "S")
        labels = [child.get("label") or child.get("word") for child in root["children"]]
        self.assertIn("S-bar", labels)
        self.assertIn("VP", labels)


if __name__ == "__main__":
    unittest.main()
