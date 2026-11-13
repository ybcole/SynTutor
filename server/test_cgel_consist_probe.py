import os
import unittest

from cgel_consist_probe import probe_consist
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
