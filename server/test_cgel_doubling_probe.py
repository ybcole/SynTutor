import os
import unittest

from cgel_doubling_probe import _doubling_replacement, _mute_e_replacement, probe_consonant_doubling, probe_mute_e
from parse_engine import NodeBuilder, analyze, parse_parse_string


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

class MuteETests(unittest.TestCase):
    def test_spelling_and_retention_controls(self):
        for word, expected in [
            ("hopeing", "hoping"), ("bakeing", "baking"), ("writeing", "writing"),
            ("hoping", None), ("seeing", None), ("dyeing", None), ("singeing", None),
            ("dye", None), ("dieing", None), ("ageing", None),
        ]:
            with self.subTest(word=word):
                self.assertEqual(_mute_e_replacement(word, "VBG"), expected)

    def test_edit_span(self):
        sentence = "They are bakeing bread."
        parse = "(S (NP (PRP They)) (VP (VBP are) (VP (VBG bakeing) (NP (NN bread)))) (. .))"
        tree = NodeBuilder().build(parse_parse_string(parse), 5)
        candidate, = probe_mute_e(sentence, tree, variety="standard_english")["candidates"]
        self.assertEqual(candidate["rule_id"], "MORPH-080")
        edit = candidate["edit_hint"]
        start, end = edit["char_span"]
        self.assertEqual(sentence[:start] + edit["replacement"] + sentence[end:], "They are baking bread.")

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_mute_e(self):
        for sentence, expected in [
            ("She is hopeing for a reply.", "She is hoping for a reply."),
            ("They are bakeing bread.", "They are baking bread."),
            ("She is dyeing cloth.", None),
            ("He is singeing the fabric.", None),
            ("They are seeing a play.", None),
            ("She is hoping for a reply.", None),
        ]:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_mute_e(sentence, analysis["root"], variety="standard_english")["candidates"]
                repaired = []
                for row in rows:
                    edit = row["edit_hint"]
                    start, end = edit["char_span"]
                    corrected = sentence[:start] + edit["replacement"] + sentence[end:]
                    repaired.append(corrected)
                    self.assertEqual(probe_mute_e(corrected, analyze(corrected)["root"],
                                                 variety="standard_english")["candidates"], [])
                self.assertIn(repaired, ([], [expected]) if expected else ([],))
                print(f"Cambridge mute e {sentence!r}: {repaired}; expected={expected}; parse={analysis['parse_string']}")
