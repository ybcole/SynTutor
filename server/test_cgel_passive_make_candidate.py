import re
import unittest

from cgel_passive_make_candidate import probe_passive_make
from parse_engine import NodeBuilder, parse_parse_string


def probe(sentence, fixture, variety="standard_english"):
    leaves = re.findall(r"\([^()]+\)", fixture)
    tree = NodeBuilder().build(parse_parse_string(fixture), len(leaves))
    return probe_passive_make(sentence, tree, variety=variety)


PASSIVE = "(S (NP (PRP We)) (VP (VBD were) (VP (VBN made) (S (VP (VB wait) (ADVP (RB outside)))))) (. .))"
MARKED = "(S (NP (PRP We)) (VP (VBD were) (VP (VBN made) (S (VP (TO to) (VP (VB wait) (ADVP (RB outside))))))) (. .))"


class PassiveMakeCandidateTest(unittest.TestCase):
    def test_insert_to_once_with_both_source_citations(self):
        sentence = "We were made wait outside."
        result = probe(sentence, PASSIVE)
        self.assertEqual(result["status"], "candidate_only")
        self.assertFalse(result["production_enabled"])
        candidate, = result["candidates"]
        self.assertEqual(candidate["rule_id"], "CLS-357")
        self.assertEqual(candidate["supporting_rule_ids"], ["CLS-1451"])
        self.assertEqual([source["pages"] for source in candidate["sources"]], [[1234], [1432]])
        self.assertEqual(candidate["token_span"], [2, 4])
        self.assertEqual(candidate["relation"]["passive_auxiliary_token_index"], 1)
        edit = candidate["edit_hint"]
        start, end = edit["char_span"]
        corrected = sentence[:start] + edit["replacement"] + sentence[end:]
        self.assertEqual(corrected, "We were made to wait outside.")
        self.assertTrue(edit["requires_reparse"])
        self.assertFalse(edit["safe_to_apply_automatically"])
        self.assertEqual(probe(corrected, MARKED)["candidates"], [])

    def test_bare_vp_complement_under_higher_auxiliary(self):
        result = probe("They had been made repeat the exercise.", (
            "(S (NP (PRP They)) (VP (VBD had) (VP (VBN been) (VP (VBN made) "
            "(VP (VB repeat) (NP (DT the) (NN exercise)))))) (. .))"
        ))
        candidate, = result["candidates"]
        self.assertEqual(candidate["relation"]["governor_token_index"], 3)
        self.assertEqual(candidate["edit_hint"]["char_span"], [19, 19])

    def test_explicit_negation_and_by_phrase_preserve_their_spans(self):
        cases = [
            ("The witness was not made identify the suspect.",
             "(S (NP (DT The) (NN witness)) (VP (VBD was) (RB not) (VP (VBN made) "
             "(S (VP (VB identify) (NP (DT the) (NN suspect)))))) (. .))", "identify"),
            ("The crew was made unload the van by the supervisor.",
             "(S (NP (DT The) (NN crew)) (VP (VBD was) (VP (VBN made) "
             "(S (VP (VB unload) (NP (DT the) (NN van)))) "
             "(PP (IN by) (NP (DT the) (NN supervisor))))) (. .))", "unload"),
            ("The crew was not made unload the van by the supervisor.",
             "(S (NP (DT The) (NN crew)) (VP (VBD was) (ADVP (RB not)) (VP (VBN made) "
             "(S (VP (VB unload) (NP (DT the) (NN van)))) "
             "(PP (IN by) (NP (DT the) (NN supervisor))))) (. .))", "unload"),
        ]
        for sentence, fixture, verb in cases:
            with self.subTest(sentence=sentence):
                candidate, = probe(sentence, fixture)["candidates"]
                edit = candidate["edit_hint"]
                self.assertEqual(edit["char_span"], [sentence.index(verb)] * 2)
                self.assertEqual(edit["replacement"], "to ")

    def test_negation_and_by_phrase_do_not_license_other_tree_shapes(self):
        cases = [
            ("We were not made to wait.", "(S (NP (PRP We)) (VP (VBD were) (RB not) "
             "(VP (VBN made) (S (VP (TO to) (VP (VB wait)))))) (. .))"),
            ("The parts were not made by the vendor.", "(S (NP (DT The) (NNS parts)) "
             "(VP (VBD were) (RB not) (VP (VBN made) (PP (IN by) (NP (DT the) (NN vendor))))) (. .))"),
            ("We were made wait and watch by the guard.", "(S (NP (PRP We)) (VP (VBD were) "
             "(VP (VBN made) (S (VP (VB wait) (CC and) (VB watch))) "
             "(PP (IN by) (NP (DT the) (NN guard))))) (. .))"),
            ("We were often made wait.", "(S (NP (PRP We)) (VP (VBD were) (RB often) "
             "(VP (VBN made) (S (VP (VB wait))))) (. .))"),
        ]
        for sentence, fixture in cases:
            with self.subTest(sentence=sentence):
                self.assertEqual(probe(sentence, fixture)["candidates"], [])

    def test_licensed_and_unresolved_constructions(self):
        controls = [
            ("They made us wait.", "(S (NP (PRP They)) (VP (VBD made) (NP (PRP us)) (S (VP (VB wait)))) (. .))"),
            ("We were made to wait outside.", MARKED),
            ("We were allowed to wait.", "(S (NP (PRP We)) (VP (VBD were) (VP (VBN allowed) (S (VP (TO to) (VP (VB wait)))))) (. .))"),
            ("The sign was made to warn visitors.", "(S (NP (DT The) (NN sign)) (VP (VBD was) (VP (VBN made) (S (VP (TO to) (VP (VB warn) (NP (NNS visitors))))))) (. .))"),
            ("The doors were made flush.", "(S (NP (DT The) (NNS doors)) (VP (VBD were) (VP (VBN made) (ADJP (JJ flush)))) (. .))"),
            ("The bread was made yesterday.", "(S (NP (DT The) (NN bread)) (VP (VBD was) (VP (VBN made) (ADVP (RB yesterday)))) (. .))"),
            ("We were made wait and watch.", "(S (NP (PRP We)) (VP (VBD were) (VP (VBN made) (S (VP (VB wait) (CC and) (VB watch))))) (. .))"),
        ]
        for sentence, fixture in controls:
            with self.subTest(sentence=sentence):
                self.assertEqual(probe(sentence, fixture)["candidates"], [])

    def test_unselected_variety_and_mismatched_parse_abstain(self):
        self.assertEqual(probe("We were made wait outside.", PASSIVE, None)["status"], "not_evaluated")
        self.assertEqual(probe("We were made stay outside.", PASSIVE)["status"], "not_evaluated")


if __name__ == "__main__":
    unittest.main()
