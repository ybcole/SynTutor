import re
import unittest

from cgel_modal_parser_probe import probe_modal_parser
from parse_engine import NodeBuilder, parse_parse_string


def probe(sentence, parse, variety="standard_english"):
    leaf_count = len(re.findall(r"\([^()]+\)", parse))
    tree = NodeBuilder().build(parse_parse_string(parse), leaf_count)
    return probe_modal_parser(sentence, tree, variety=variety)


INFLECTED = "(S (NP (PRP She)) (VP (MD can) (VP (VBZ goes))) (. .))"
MARKED = "(S (NP (PRP She)) (VP (MD can) (S (VP (TO to) (VP (VB go))))) (. .))"


class ModalParserProbeTests(unittest.TestCase):
    def test_two_modal_errors_each_have_one_relation_and_exact_edit(self):
        for sentence, tree in [("She can goes.", INFLECTED), ("She can to go.", MARKED)]:
            with self.subTest(sentence=sentence):
                result = probe(sentence, tree)
                candidate, = result["candidates"]
                self.assertEqual(candidate["rule_id"], "COMP-034")
                self.assertFalse(result["production_enabled"])
                relation = candidate["relation"]
                self.assertEqual((relation["governor_token_index"], relation["dependent_token_index"]), (1, 2))
                edit = candidate["edit_hint"]
                start, end = edit["char_span"]
                self.assertEqual(sentence[:start] + edit["replacement"] + sentence[end:], "She can go.")

    def test_mistagged_third_person_forms_require_an_attested_paradigm(self):
        for surface, plain in [("arrives", "arrive"), ("brings", "bring")]:
            with self.subTest(surface=surface):
                tree = INFLECTED.replace("VBZ goes", f"VB {surface}")
                candidate, = probe(f"She can {surface}.", tree)["candidates"]
                self.assertEqual(candidate["edit_hint"]["replacement"], plain)

        for plain in ["pass", "focus", "bias", "gas", "axes", "blorps"]:
            with self.subTest(plain=plain):
                tree = INFLECTED.replace("VBZ goes", f"VB {plain}")
                self.assertEqual(probe(f"She can {plain}.", tree)["candidates"], [])

    def test_plain_lexical_noncentral_and_coordinated_cases_are_guarded(self):
        cases = [
            ("She can go.", "(S (NP (PRP She)) (VP (MD can) (VP (VB go))) (. .))"),
            ("She ought to go.", MARKED.replace("MD can", "MD ought")),
            ("They can tomatoes.", "(S (NP (PRP They)) (VP (VBP can) (NP (NNS tomatoes))) (. .))"),
            ("She may or may not go.", "(S (NP (PRP She)) (VP (MD may) (CC or) (MD may) (RB not) (VP (VB go))) (. .))"),
            ("She can go to work.", "(S (NP (PRP She)) (VP (MD can) (VP (VB go) (S (VP (TO to) (VP (VB work)))))) (. .))"),
        ]
        for sentence, tree in cases:
            with self.subTest(sentence=sentence):
                self.assertEqual(probe(sentence, tree)["candidates"], [])

    def test_alignment_and_variety_fail_closed(self):
        self.assertEqual(probe("She can walks.", INFLECTED)["blocked"], ["parser_token_alignment_unavailable"])
        self.assertEqual(probe("She can goes.", INFLECTED, variety=None)["candidates"], [])


if __name__ == "__main__":
    unittest.main()
