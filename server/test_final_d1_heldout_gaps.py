import unittest

try:
    from server.burton_roberts import build_canonical_analysis
    from server.parse_engine import analyze
except ImportError:
    from burton_roberts import build_canonical_analysis
    from parse_engine import analyze

SENTENCES = [
    "He didn't read the report, not even the summary.",
    "They didn't visit the town, not even the museum.",
    "She never wrote, not even a postcard.",
    "We didn't ask anyone, not even Jon.",
    "It took longer than she thought.",
    "It is vital that he leave early.",
    "What is the matter, that you look so upset?",
    "She wrote more plays than he wrote novels.",
    "He's as old as I am.",
    "They have as many cats as we have dogs.",
    "She is taller than he is.",
    "She went to the same school as I did.",
    "Such cakes as she made were soon eaten.",
    "She'll be arriving tomorrow or on Friday.",
    "My aunt – she lives in Paris – is visiting.",
    "This book I gave to Mara.",
    "I find it odd that nobody called.",
    "She wrote more plays than he did.",
    "It was less painful than I'd expected.",
]


class FinalD1HeldoutGapTests(unittest.TestCase):
    def test_all_formerly_working_sentences_normalize(self):
        for sentence in SENTENCES:
            with self.subTest(sentence=sentence):
                result = build_canonical_analysis(analyze(sentence))
                self.assertEqual(result["status"], "normalized", result.get("reasons"))


if __name__ == "__main__":
    unittest.main()
