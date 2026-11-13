import os
import unittest

from cgel_case_probe import probe_infinitival_case, probe_local_reflexive, probe_pride_reflexive, probe_pronoun_case
from parse_engine import NodeBuilder, analyze, parse_parse_string


CASES = [
    ("Him greeted us.", ["subject"]),
    ("They greeted she.", ["direct_object"]),
    ("Him thanked she.", ["subject", "direct_object"]),
    ("He greeted us.", []),
    ("They greeted her.", []),
]


class CaseProbeTests(unittest.TestCase):
    def test_simple_active_roles(self):
        for sentence, expected in CASES:
            with self.subTest(sentence=sentence):
                subject, verb, obj = sentence.rstrip(".").split()
                parse = f"(S (NP (PRP {subject})) (VP (VBD {verb}) (NP (PRP {obj}))) (. .))"
                tree = NodeBuilder().build(parse_parse_string(parse), 4)
                rows = probe_pronoun_case(sentence, tree, variety="standard_english")["candidates"]
                self.assertEqual([row["relation"]["kind"] for row in rows], expected)
                for row in rows:
                    support = row["supporting_sources"]
                    self.assertEqual(bool(support), row["relation"]["kind"] == "subject")

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_case_probe(self):
        for sentence, expected in CASES + [
            ("It was her.", []), ("They waved to her.", []), ("He and I greeted her.", []),
            ("They thanked him and me.", []),
        ]:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_pronoun_case(sentence, analysis["root"], variety="standard_english")["candidates"]
                found = [row["relation"]["kind"] for row in rows]
                print(f"Cambridge case {sentence!r}: {found}; expected={expected}; parse={analysis['parse_string']}")
                self.assertEqual(found, [role for role in expected if role in found])


class InfinitivalCaseTests(unittest.TestCase):
    def test_explicit_for_infinitival(self):
        for pronoun, expected in [("he", ["him"]), ("him", []), ("they", ["them"]), ("them", [])]:
            with self.subTest(pronoun=pronoun):
                sentence = f"We arranged for {pronoun} to speak."
                parse = f"(S (NP (PRP We)) (VP (VBD arranged) (SBAR (IN for) (S (NP (PRP {pronoun})) (VP (TO to) (VP (VB speak)))))) (. .))"
                tree = NodeBuilder().build(parse_parse_string(parse), 7)
                result = probe_infinitival_case(sentence, tree, variety="standard_english")
                self.assertEqual([row["expected_pronoun"] for row in result["candidates"]], expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_infinitival_case(self):
        for sentence, expected in [
            ("We arranged for he to speak first.", ["him"]),
            ("It was unusual for she to arrive late.", ["her"]),
            ("We arranged for him to speak first.", []),
            ("It was unusual for her to arrive late.", []),
            ("We waited for him.", []),
            ("We hoped that he would speak first.", []),
            ("It is time for there to be a change.", []),
            ("We arranged for her and me to speak.", []),
        ]:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_infinitival_case(sentence, analysis["root"], variety="standard_english")["candidates"]
                found = [row["expected_pronoun"] for row in rows]
                self.assertIn(found, (expected, []))
                print(f"Cambridge infinitival case {sentence!r}: {found}; expected={expected}; parse={analysis['parse_string']}")


class LocalReflexiveTests(unittest.TestCase):
    def test_local_controller(self):
        for pronoun, reflexive, expected in [
            ("he", "myself", ["CLS-1101"]), ("she", "herself", []),
            ("they", "themself", []), ("you", "yourselves", []),
        ]:
            with self.subTest(pronoun=pronoun, reflexive=reflexive):
                sentence = f"If {pronoun} hurt {reflexive}, I would leave."
                parse = (
                    f"(S (SBAR (IN If) (S (NP (PRP {pronoun})) "
                    f"(VP (VBD hurt) (NP (PRP {reflexive}))))) (, ,) "
                    "(NP (PRP I)) (VP (MD would) (VP (VB leave))) (. .))"
                )
                tree = NodeBuilder().build(parse_parse_string(parse), 9)
                rows = probe_local_reflexive(sentence, tree, variety="standard_english")["candidates"]
                self.assertEqual([row["rule_id"] for row in rows], expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_local_reflexive(self):
        for sentence, expected in [
            ("If she blames myself, I will apologize.", ["CLS-1101"]),
            ("If we injure himself, Kiran will seek treatment.", ["CLS-1101"]),
            ("If she blames herself, Mira will apologize.", []),
            ("If they injure themselves, Kiran will seek treatment.", []),
            ("If she admires a portrait of myself, I will thank her.", []),
            ("I blamed myself.", []),
        ]:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_local_reflexive(sentence, analysis["root"], variety="standard_english")["candidates"]
                found = [row["rule_id"] for row in rows]
                self.assertIn(found, (expected, []))
                print(f"Cambridge local reflexive {sentence!r}: {found}; expected={expected}")


PRIDE_CASES = [
    ("Nadia prides her on her patience.", True),
    ("They pride them on their teamwork.", True),
    ("Nadia prides herself on her patience.", False),
    ("They pride themselves on their teamwork.", False),
    ("Nadia takes pride in her patience.", False),
    ("They congratulated her on her patience.", False),
]


class PrideReflexiveTests(unittest.TestCase):
    def test_plain_object_and_reflexive_control(self):
        for word, expected in [("her", ["CLS-1103"]), ("herself", [])]:
            with self.subTest(word=word):
                sentence = f"Nadia prides {word} on her patience."
                parse = (
                    f"(S (NP (NNP Nadia)) (VP (VBZ prides) (NP (PRP {word})) "
                    "(PP (IN on) (NP (PRP$ her) (NN patience)))) (. .))"
                )
                tree = NodeBuilder().build(parse_parse_string(parse), 7)
                rows = probe_pride_reflexive(sentence, tree, variety="standard_english")["candidates"]
                self.assertEqual([row["rule_id"] for row in rows], expected)
                if rows:
                    self.assertEqual(rows[0]["relation"]["object_char_span"], [13, 16])
                    self.assertIsNone(rows[0]["edit_hint"])

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_pride_reflexive(self):
        for sentence, expected in PRIDE_CASES:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_pride_reflexive(sentence, analysis["root"], variety="standard_english")["candidates"]
                found = [row["rule_id"] for row in rows]
                self.assertIn(found, ([], ["CLS-1103"]) if expected else ([],))
                print(f"Cambridge pride reflexive {sentence!r}: {found}; expected={expected}")
