import os
import unittest

from cgel_lexical_number_probe import probe_demonstrative_number, probe_lexical_number, probe_total_number
from cgel_lexical_number_probe import probe_singular_they_agreement
from cgel_lexical_number_probe import probe_spatial_demonstrative
from parse_engine import NodeBuilder, analyze, parse_parse_string


CASES = [
    ("Cattle is outside.", "(NNS Cattle)", "VBZ is", "outside", False, [("PHR-062", "are")]),
    ("The police was outside.", "(DT The) (NNS police)", "VBD was", "outside", False, [("PHR-062", "were")]),
    ("The news are encouraging.", "(DT The) (NN news)", "VBP are", "encouraging", False, [("PHR-065", "is")]),
    ("Shingles are painful.", "(NNS Shingles)", "VBP are", "painful", True, [("PHR-065", "is")]),
    ("Shingles are painful.", "(NNS Shingles)", "VBP are", "painful", False, []),
    ("The police officer is outside.", "(DT The) (NN police) (NN officer)", "VBZ is", "outside", False, []),
    ("The news is encouraging.", "(DT The) (NN news)", "VBZ is", "encouraging", False, []),
    ("The shingles are loose.", "(DT The) (NNS shingles)", "VBP are", "loose", False, []),
]

CASES += [
    ("The furniture have arrived.", "(DT The) (NN furniture)", "VBP have", "arrived", False, [("PHR-347", "has")]),
    ("The luggage were outside.", "(DT The) (NN luggage)", "VBD were", "outside", False, [("PHR-347", "was")]),
    ("The crockery are fragile.", "(DT The) (NN crockery)", "VBP are", "fragile", False, [("PHR-347", "is")]),
    ("The equipment is ready.", "(DT The) (NN equipment)", "VBZ is", "ready", False, []),
    ("The luggage racks are empty.", "(DT The) (NN luggage) (NNS racks)", "VBP are", "empty", False, []),
    ("The staff are ready.", "(DT The) (NN staff)", "VBP are", "ready", False, []),
    ("Two pieces of furniture are missing.", "(CD Two) (NNS pieces) (PP (IN of) (NP (NN furniture)))",
     "VBP are", "missing", False, []),
]


class LexicalNumberTests(unittest.TestCase):
    def check_case(self, sentence, tree, disease, expected):
        result = probe_lexical_number(sentence, tree, variety="standard_english", disease_confirmed=disease)
        found = [(row["rule_id"], row["expected_verb"]) for row in result["candidates"]]
        self.assertEqual(found, expected)
        self.assertFalse(result["production_enabled"])

    def test_lexical_number_fixtures(self):
        for sentence, np, verb, adjective, disease, expected in CASES:
            with self.subTest(sentence=sentence, disease=disease):
                parse = f"(S (NP {np}) (VP ({verb}) (ADJP (JJ {adjective}))) (. .))"
                tree = NodeBuilder().build(parse_parse_string(parse), len(sentence.split()) + 1)
                self.check_case(sentence, tree, disease, expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_lexical_number(self):
        for sentence, _, _, _, disease, expected in CASES:
            with self.subTest(sentence=sentence, disease=disease):
                self.check_case(sentence, analyze(sentence)["root"], disease, expected)


class DemonstrativeNumberTests(unittest.TestCase):
    def check_case(self, sentence, tree, expected):
        result = probe_demonstrative_number(sentence, tree, variety="standard_english")
        self.assertEqual([row["rule_id"] for row in result["candidates"]], expected)
        for row in result["candidates"]:
            self.assertIsNone(row["edit_hint"])

    def test_number_mismatch_in_both_directions(self):
        for phrase, expected in [
            ("These book", ["PHR-087"]), ("This books", ["PHR-087"]),
            ("Those children", []), ("That child", []), ("These sheep", []),
        ]:
            det, noun = phrase.split()
            # The noun's lexical form matters even when the parser mistags its number.
            tree = NodeBuilder().build(parse_parse_string(f"(NP (DT {det}) (NN {noun}))"), 2)
            self.check_case(phrase, tree, expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_demonstratives(self):
        for sentence, expected in [
            ("I borrowed these book yesterday.", ["PHR-087"]),
            ("She packed that folders first.", ["PHR-087"]),
            ("I borrowed these books yesterday.", []),
            ("She packed that folder first.", []),
            ("These sheep are grazing.", []),
            ("These kind of books are expensive.", []),
            ("This ten miles is the hardest stretch.", []),
            ("These are books.", []),
            ("This book and that folder are mine.", []),
        ]:
            with self.subTest(sentence=sentence):
                self.check_case(sentence, analyze(sentence)["root"], expected)


class TotalNumberTests(unittest.TestCase):
    def check_case(self, sentence, tree, expected):
        rows = probe_total_number(sentence, tree, variety="standard_english")["candidates"]
        self.assertEqual([row["expected_verb"] for row in rows], expected)
        for row in rows:
            self.assertEqual(row["rule_id"], "PHR-079")
            self.assertIsNone(row["edit_hint"])

    def test_total_subject_shape(self):
        for det, expected in [("The", ["has"]), ("A", [])]:
            sentence = f"{det} number of deliveries have doubled."
            parse = (
                f"(S (NP (NP (DT {det}) (NN number)) (PP (IN of) (NP (NNS deliveries)))) "
                "(VP (VBP have) (VP (VBN doubled))) (. .))"
            )
            self.check_case(sentence, NodeBuilder().build(parse_parse_string(parse), 7), expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_total_number(self):
        for sentence, expected in [
            ("The number of deliveries have doubled.", ["has"]),
            ("The number of available seats are uncertain.", ["is"]),
            ("The number of deliveries has doubled.", []),
            ("A number of deliveries have arrived.", []),
            ("The numbers of arrivals and departures are similar.", []),
            ("The estimates of the number of deliveries are uncertain.", []),
            ("The number of deliveries and the number of returns are equal.", []),
        ]:
            with self.subTest(sentence=sentence):
                self.check_case(sentence, analyze(sentence)["root"], expected)


THEY_CASES = [
    ("They is ready.", "VBZ is", "ready", True, ["are"]),
    ("They was ready.", "VBD was", "ready", True, ["were"]),
    ("They are ready.", "VBP are", "ready", True, []),
    ("They were ready.", "VBD were", "ready", True, []),
    ("They is ready.", "VBZ is", "ready", False, []),
]


class SingularTheyTests(unittest.TestCase):
    def check_case(self, sentence, tree, context, expected):
        result = probe_singular_they_agreement(
            sentence, tree, variety="standard_english", singular_reference_confirmed=context
        )
        self.assertFalse(result["production_enabled"])
        rows = result["candidates"]
        self.assertEqual([row["expected_verb"] for row in rows], expected)
        for row in rows:
            self.assertEqual(row["rule_id"], "PHR-334")
            self.assertIsNone(row["edit_hint"])

    def test_confirmed_singular_reference(self):
        for sentence, verb, complement, context, expected in THEY_CASES:
            with self.subTest(sentence=sentence, context=context):
                parse = f"(S (NP (PRP They)) (VP ({verb}) (ADJP (JJ {complement}))) (. .))"
                self.check_case(sentence, NodeBuilder().build(parse_parse_string(parse), 4), context, expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_singular_they(self):
        for sentence, context, expected in [
            *((sentence, context, expected) for sentence, _, _, context, expected in THEY_CASES),
            ("They has finished.", True, ["have"]),
            ("They have finished.", True, []),
            ("She is ready.", False, []),
            ("They themselves are ready.", True, []),
        ]:
            with self.subTest(sentence=sentence, context=context):
                self.check_case(sentence, analyze(sentence)["root"], context, expected)


class SpatialDemonstrativeTests(unittest.TestCase):
    def test_np_attachment_and_context(self):
        for det, place, context, expected in [
            ("This", "there", True, ["PHR-620"]),
            ("That", "here", True, ["PHR-620"]),
            ("That", "there", True, []),
            ("This", "there", False, []),
        ]:
            with self.subTest(det=det, place=place, context=context):
                tree = NodeBuilder().build(parse_parse_string(
                    f"(S (NP (NP (DT {det}) (NN book)) (ADVP (RB {place}))) "
                    "(VP (VBZ belongs) (ADVP (RB upstairs))) (. .))"
                ), 6)
                self.check_case(f"{det} book {place} belongs upstairs.", tree, context, expected)

    def check_case(self, sentence, tree, context, expected):
        result = probe_spatial_demonstrative(
            sentence, tree, variety="standard_english", shared_deictic_context=context
        )
        self.assertEqual([row["rule_id"] for row in result["candidates"]], expected)
        for row in result["candidates"]:
            self.assertIsNone(row["edit_hint"])

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_spatial_demonstratives(self):
        for sentence, context, target in [
            ("This envelope over there is for Lee.", True, True),
            ("Those crates here belong to us.", True, True),
            ("This envelope over there is for Lee.", False, False),
            ("That envelope over there is for Lee.", True, False),
            ("These crates here belong to us.", True, False),
            ("Put this envelope over there.", True, False),
            ("We placed those crates here.", True, False),
        ]:
            with self.subTest(sentence=sentence, context=context):
                analysis = analyze(sentence)
                result = probe_spatial_demonstrative(
                    sentence, analysis["root"], variety="standard_english", shared_deictic_context=context
                )
                ids = [row["rule_id"] for row in result["candidates"]]
                self.assertIn(ids, ([], ["PHR-620"]) if target else ([],))
                print(f"Cambridge spatial demonstrative {sentence!r}: {ids}; target={target}; parse={analysis['parse_string']}")
