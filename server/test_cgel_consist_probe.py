import os
import unittest

from cgel_consist_probe import probe_come_across, probe_consist
from parse_engine import NodeBuilder, analyze, parse_parse_string


class ConsistProbeTests(unittest.TestCase):
    def test_requires_confirmed_composition_and_selected_pp(self):
        for word, expected in [("with", 1), ("on", 1), ("in", 0), ("of", 0)]:
            sentence = f"The mixture consists {word} milk."
            parse = f"(S (NP (DT The) (NN mixture)) (VP (VBZ consists) (PP (IN {word}) (NP (NN milk)))) (. .))"
            tree = NodeBuilder().build(parse_parse_string(parse), 6)
            with self.subTest(word=word):
                self.assertEqual(probe_consist(sentence, tree, variety="standard_english")["candidates"], [])
                rows = probe_consist(sentence, tree, variety="standard_english", composition_confirmed=True)["candidates"]
                self.assertEqual(len(rows), expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_parser(self):
        for sentence, expected in [
            ("The mixture consists with milk and flour.", "The mixture consists of milk and flour."),
            ("The team consists on seven players.", "The team consists of seven players."),
            ("The team consists of seven players.", None),
            ("The work consists in careful observation.", None),
            ("The outcome depends on seven players.", None),
        ]:
            with self.subTest(sentence=sentence):
                tree = analyze(sentence)["root"]
                rows = probe_consist(sentence, tree, variety="standard_english", composition_confirmed=True)["candidates"]
                print(f"Cambridge consist {sentence!r}: {len(rows)} candidate(s)")
                if expected is None:
                    self.assertEqual(rows, [])
                elif rows:
                    candidate, = rows
                    edit = candidate["edit_hint"]
                    start, end = edit["char_span"]
                    repaired = sentence[:start] + edit["replacement"] + sentence[end:]
                    self.assertEqual(repaired, expected)
                    recheck = probe_consist(repaired, analyze(repaired)["root"],
                                            variety="standard_english", composition_confirmed=True)
                    self.assertEqual(recheck["status"], "candidate_only")
                    self.assertEqual(recheck["candidates"], [])


class ComeAcrossProbeTests(unittest.TestCase):
    def test_fronted_preposition_requires_encounter_reading(self):
        sentence = "Across which papers did she come?"
        tree = NodeBuilder().build(parse_parse_string(
            "(SBARQ (WHPP (IN Across) (WHNP (WDT which) (NNS papers))) "
            "(SQ (VBD did) (NP (PRP she)) (VP (VB come))) (. ?))"
        ), 7)
        for confirmed, expected in [(True, ["COMP-128"]), (False, [])]:
            with self.subTest(confirmed=confirmed):
                rows = probe_come_across(sentence, tree, variety="standard_english",
                                         encounter_confirmed=confirmed)["candidates"]
                self.assertEqual([row["rule_id"] for row in rows], expected)
                if rows:
                    self.assertEqual(rows[0]["relation"]["preposition_char_span"], [0, 6])
                    self.assertIsNone(rows[0]["edit_hint"])

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_come_across(self):
        for sentence, confirmed, expected in [
            ("Across which papers did she come?", True, ["COMP-128"]),
            ("Across which papers did she come?", False, []),
            ("Across which river did she come?", False, []),
            ("Which papers did she come across?", True, []),
            ("Across which river did she swim?", True, []),
            ("To which report did she refer?", True, []),
        ]:
            with self.subTest(sentence=sentence, confirmed=confirmed):
                analysis = analyze(sentence)
                rows = probe_come_across(sentence, analysis["root"], variety="standard_english",
                                         encounter_confirmed=confirmed)["candidates"]
                found = [row["rule_id"] for row in rows]
                print(f"Cambridge come across {sentence!r} sense={confirmed}: {found}; expected={expected}; parse={analysis['parse_string']}")
                self.assertEqual(found, expected)
