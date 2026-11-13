import os
import unittest

from cgel_doubling_probe import _doubling_replacement, _mute_e_replacement, probe_consonant_doubling, probe_mute_e
from cgel_doubling_probe import _final_ie_replacement, _final_y_plural_replacement, probe_final_ie, probe_final_y_plural
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

class FinalIETests(unittest.TestCase):
    def test_closed_set_and_controls(self):
        for word, expected in [
            ("dieing", "dying"), ("lieing", "lying"), ("tieing", "tying"), ("vieing", "vying"),
            ("dyeing", None), ("skiing", None), ("singeing", None), ("tying", None),
        ]:
            with self.subTest(word=word):
                self.assertEqual(_final_ie_replacement(word, "VBG"), expected)
                self.assertIsNone(_final_ie_replacement(word, "NN"))

    def test_span_and_candidate(self):
        sentence = "She is tieing it."
        tree = NodeBuilder().build(parse_parse_string(
            "(S (NP (PRP She)) (VP (VBZ is) (VP (VBG tieing) (NP (PRP it)))) (. .))"
        ), 5)
        candidate, = probe_final_ie(sentence, tree, variety="standard_english")["candidates"]
        self.assertEqual(candidate["rule_id"], "MORPH-083")
        edit = candidate["edit_hint"]
        start, end = edit["char_span"]
        self.assertEqual(sentence[:start] + edit["replacement"] + sentence[end:], "She is tying it.")

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_final_ie(self):
        for sentence, expected in [
            ("She is tieing the parcel.", "She is tying the parcel."),
            ("The dog is lieing on the rug.", "The dog is lying on the rug."),
            ("She is dyeing cloth.", None),
            ("They are skiing today.", None),
            ("She is tying the parcel.", None),
        ]:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_final_ie(sentence, analysis["root"], variety="standard_english")["candidates"]
                repairs = []
                for row in rows:
                    edit = row["edit_hint"]
                    start, end = edit["char_span"]
                    repaired = sentence[:start] + edit["replacement"] + sentence[end:]
                    repairs.append(repaired)
                    recheck = probe_final_ie(repaired, analyze(repaired)["root"], variety="standard_english")
                    self.assertEqual(recheck["status"], "candidate_only")
                    self.assertEqual(recheck["candidates"], [])
                self.assertIn(repairs, ([], [expected]) if expected else ([],))
                print(f"Cambridge final ie {sentence!r}: {repairs}; expected={expected}; parse={analysis['parse_string']}")

class FinalYPluralTests(unittest.TestCase):
    def test_known_noun_paradigms(self):
        for word, expected in [
            ("citys", "cities"), ("donkeies", "donkeys"), ("babys", "babies"),
            ("toies", "toys"), ("cities", None), ("donkeys", None),
            ("trolleys", None), ("trollies", None), ("monies", None), ("moneys", None),
            ("bys", None),
        ]:
            with self.subTest(word=word):
                self.assertEqual(_final_y_plural_replacement(word, "NNS"), expected)
                self.assertIsNone(_final_y_plural_replacement(word, "NNP"))

    def test_common_noun_span(self):
        sentence = "Several citys joined."
        tree = NodeBuilder().build(parse_parse_string(
            "(S (NP (JJ Several) (NN citys)) (VP (VBD joined)) (. .))"
        ), 4)
        candidate, = probe_final_y_plural(sentence, tree, variety="standard_english")["candidates"]
        self.assertEqual(candidate["rule_id"], "MORPH-092")
        start, end = candidate["edit_hint"]["char_span"]
        self.assertEqual(sentence[start:end], "citys")

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_final_y_plurals(self):
        for sentence, expected in [
            ("Several citys joined the program.", "Several cities joined the program."),
            ("Two donkeies stood beside the gate.", "Two donkeys stood beside the gate."),
            ("Several cities joined the program.", None),
            ("Two donkeys stood beside the gate.", None),
            ("The Kennedys arrived early.", None),
            ("Several trolleys waited outside.", None),
        ]:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_final_y_plural(sentence, analysis["root"], variety="standard_english")["candidates"]
                repaired = []
                for row in rows:
                    edit = row["edit_hint"]
                    start, end = edit["char_span"]
                    corrected = sentence[:start] + edit["replacement"] + sentence[end:]
                    repaired.append(corrected)
                    recheck = probe_final_y_plural(corrected, analyze(corrected)["root"], variety="standard_english")
                    self.assertEqual(recheck["status"], "candidate_only")
                    self.assertEqual(recheck["candidates"], [])
                self.assertIn(repaired, ([], [expected]) if expected else ([],))
                print(f"Cambridge final y plural {sentence!r}: {repaired}; expected={expected}; parse={analysis['parse_string']}")
