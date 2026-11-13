import os
import unittest

from cgel_doubling_probe import _doubling_replacement, probe_consonant_doubling
from parse_engine import analyze


class DoublingProbeTests(unittest.TestCase):
    def test_attested_forms_and_homographs(self):
        for word, tag, expected in [
            ("fited", "VBD", "fitted"), ("stoping", "VBG", None),
            ("planed", "VBD", None), ("hoping", "VBG", None),
            ("admiting", "VBG", "admitting"), ("opened", "VBD", None),
            ("traveling", "VBG", None), ("travelling", "VBG", None),
            ("combated", "VBD", None), ("combatted", "VBD", None),
            ("fixed", "VBD", None),
        ]:
            with self.subTest(word=word):
                self.assertEqual(_doubling_replacement(word, tag), expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_doubling(self):
        for sentence, expected in [
            ("The mechanic fited a latch.", "fitted"),
            ("They are admiting new members.", "admitting"),
            ("The runner is hoping for rain.", None),
            ("The mechanic fitted a latch.", None),
            ("They are traveling together.", None),
            ("They are travelling together.", None),
        ]:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_consonant_doubling(sentence, analysis["root"],
                                               variety="standard_english")["candidates"]
                replacements = [row["edit_hint"]["replacement"] for row in rows]
                print(f"Cambridge doubling {sentence!r}: {replacements}; expected={expected}; parse={analysis['parse_string']}")
                self.assertIn(replacements, ([], [expected]) if expected else ([],))
                for row in rows:
                    edit = row["edit_hint"]
                    start, end = edit["char_span"]
                    repaired = sentence[:start] + edit["replacement"] + sentence[end:]
                    recheck = probe_consonant_doubling(repaired, analyze(repaired)["root"],
                                                      variety="standard_english")
                    self.assertEqual(recheck["status"], "candidate_only")
                    self.assertEqual(recheck["candidates"], [])
