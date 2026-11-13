import unittest

from cgel_article_parser_probe import probe_article_parser
from parse_engine import NodeBuilder, parse_parse_string


class ArticleParserProbeTests(unittest.TestCase):
    def test_known_onsets_and_parenthesised_modifier(self):
        for sentence, tree, size, expected, support in [
            ("An university", "(NP (DT An) (NN university))", 2, "A", False),
            ("a hour", "(NP (DT a) (NN hour))", 2, "an", False),
            ("a (old) book", "(NP (DT a) (-LRB- -LRB-) (JJ old) (-RRB- -RRB-) (NN book))", 5, "an", True),
            ("an (small) owl", "(NP (DT an) (-LRB- -LRB-) (JJ small) (-RRB- -RRB-) (NN owl))", 5, "a", True),
            ("an unusual book", "(NP (DT an) (JJ unusual) (NN book))", 3, None, False),
            ("a herb", "(NP (DT a) (NN herb))", 2, None, False),
            ("a UFO", "(NP (DT a) (NN UFO))", 2, None, False),
            ("a unicorn", "(NP (DT a) (NN unicorn))", 2, None, False),
        ]:
            with self.subTest(sentence=sentence):
                root = NodeBuilder().build(parse_parse_string(tree), size)
                result = probe_article_parser(sentence, root, variety="standard_english")
                if expected is None:
                    self.assertEqual(result["candidates"], [])
                else:
                    candidate, = result["candidates"]
                    self.assertEqual(candidate["edit_hint"]["replacement"], expected)
                    self.assertEqual(bool(candidate["supporting_sources"]), support)
                    self.assertFalse(result["production_enabled"])
