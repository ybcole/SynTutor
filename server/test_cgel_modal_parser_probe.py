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

    def test_modal_stack_requires_two_modal_tags_and_explicit_variety(self):
        tree = "(S (NP (PRP They)) (VP (MD might) (VP (MD can) (VP (VB fish)))) (. .))"
        sentence = "They might can fish."
        candidate, = probe(sentence, tree)["candidates"]
        self.assertEqual(candidate["rule_id"], "COMP-031")
        self.assertIsNone(candidate["edit_hint"])
        self.assertEqual(probe(sentence, tree, variety=None)["candidates"], [])
        lexical = tree.replace("(MD can) (VP (VB fish))", "(VB can) (NP (NN fish))")
        self.assertEqual(probe(sentence, lexical)["candidates"], [])
        mistagged = tree.replace("(MD can) (VP (VB fish))", "(MD can) (VP (NNS peaches))")
        self.assertEqual(probe("They might can peaches.", mistagged)["candidates"], [])

    def test_inverted_supportive_do_requires_an_auxiliary_complement(self):
        cases = [
            ("Did she have left?", "(VB have) (VP (VBN left))", ["CLS-100"]),
            ("Did she be working?", "(VB be) (VP (VBG working))", ["CLS-100"]),
            ("Did she be ready?", "(VB be) (ADJP (JJ ready))", ["CLS-100"]),
            ("Did she be ready today?", "(VB be) (ADJP (JJ ready)) (NP (NN today))", ["CLS-100"]),
            ("Did she be ready soon?", "(VB be) (ADJP (JJ ready)) (ADVP (RB soon))", ["CLS-100"]),
            ("Did she be ready or leave?", "(VB be) (ADJP (JJ ready)) (CC or) (VB leave)", []),
            ("Did she can leave?", "(MD can) (VP (VB leave))", ["CLS-100"]),
            ("Did she have time?", "(VB have) (NP (NN time))", []),
            ("Did she have it fixed?", "(VB have) (S (NP (PRP it)) (VP (VBN fixed)))", []),
        ]
        for sentence, predicate, expected in cases:
            with self.subTest(sentence=sentence):
                tree = f"(SQ (VBD Did) (NP (PRP she)) (VP {predicate}) (. ?))"
                candidates = probe(sentence, tree)["candidates"]
                self.assertEqual([c["rule_id"] for c in candidates], expected)
                for candidate in candidates:
                    self.assertEqual(candidate["supporting_rule_ids"], ["COMP-030"])
                    self.assertIsNone(candidate["edit_hint"])

    def test_closed_question_lexical_form(self):
        for surface, tag, replacement in [
            ("works", "VBZ", "work"), ("went", "VBD", "go"), ("works", "VB", "work"),
            ("went", "VBN", "go"), ("parked", "VBN", "park"), ("gone", "VBN", None),
            ("cut", "VBD", None), ("work", "VB", None),
        ]:
            with self.subTest(surface=surface, tag=tag):
                tree = f"(SQ (VBD Did) (NP (PRP she)) (VP ({tag} {surface})) (. ?))"
                candidates = probe(f"Did she {surface}?", tree)["candidates"]
                if replacement:
                    candidate, = candidates
                    self.assertEqual(candidate["rule_id"], "CLS-126")
                    self.assertEqual(candidate["source_pages"], [856])
                    self.assertEqual(candidate["edit_hint"]["replacement"], replacement)
                else:
                    self.assertEqual(candidates, [])

    def test_imperative_do_is_out_of_scope(self):
        tree = "(S (VP (VBP Do) (VP (VB be) (ADJP (JJ careful)))) (. !))"
        self.assertEqual(probe("Do be careful!", tree)["candidates"], [])

    def test_alignment_and_variety_fail_closed(self):
        self.assertEqual(probe("She can walks.", INFLECTED)["blocked"], ["parser_token_alignment_unavailable"])
        self.assertEqual(probe("She can goes.", INFLECTED, variety=None)["candidates"], [])


if __name__ == "__main__":
    unittest.main()
