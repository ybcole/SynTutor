import os
import re
import unittest

from cgel_catenative_probe import probe_believe_object, probe_catenative_perfect
from cgel_catenative_probe import probe_determined_participle
from cgel_catenative_probe import probe_interrogative_infinitival_subject
from cgel_catenative_probe import probe_participial_relative_marker
from parse_engine import NodeBuilder, analyze, parse_parse_string


class CatenativePerfectTests(unittest.TestCase):
    def test_confirmed_bound_reading(self):
        sentence = "She began to have read it."
        tree = NodeBuilder().build(parse_parse_string(
            "(S (NP (PRP She)) (VP (VBD began) (S (VP (TO to) "
            "(VP (VB have) (VP (VBN read) (NP (PRP it))))))) (. .))"
        ), 7)
        for context, expected in [(True, ["OTH-182"]), (False, [])]:
            rows = probe_catenative_perfect(sentence, tree, variety="standard_english",
                                           bound_reading_confirmed=context)["candidates"]
            self.assertEqual([row["rule_id"] for row in rows], expected)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_catenatives(self):
        for sentence, context, target in [
            ("She began to have read the manuscript.", True, True),
            ("The tutor made the class have completed the exercise.", True, True),
            ("She began to have read the manuscript.", False, False),
            ("She seemed to have read the manuscript.", True, False),
            ("They expected her to have finished the exercise.", True, False),
            ("She began to have doubts.", True, False),
            ("The tutor made the class complete the exercise.", True, False),
        ]:
            with self.subTest(sentence=sentence, context=context):
                analysis = analyze(sentence)
                rows = probe_catenative_perfect(sentence, analysis["root"], variety="standard_english",
                                               bound_reading_confirmed=context)["candidates"]
                found = [row["rule_id"] for row in rows]
                print(f"Cambridge catenative perfect {sentence!r}: {found}; target={target}; parse={analysis['parse_string']}")
                self.assertIn(found, ([], ["OTH-182"]) if target else ([],))


class BelieveObjectTests(unittest.TestCase):
    def check_case(self, sentence, tree, context, expected):
        result = probe_believe_object(
            sentence, tree, variety="standard_english", complement_confirmed=context
        )
        self.assertFalse(result["production_enabled"])
        self.assertEqual([row["rule_id"] for row in result["candidates"]], expected)
        for row in result["candidates"]:
            self.assertIsNone(row["edit_hint"])

    def test_active_complement_requires_object(self):
        sentence = "Nina believed to be qualified."
        tree = NodeBuilder().build(parse_parse_string(
            "(S (NP (NNP Nina)) (VP (VBD believed) (S (VP (TO to) "
            "(VP (VB be) (ADJP (JJ qualified)))))) (. .))"
        ), 6)
        self.check_case(sentence, tree, True, ["CLS-320"])
        self.check_case(sentence, tree, False, [])

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_believe_objects(self):
        for sentence, context, expected in [
            ("Nina believed to be qualified.", True, ["CLS-320"]),
            ("I believed to be ready.", True, ["CLS-320"]),
            ("Nina believed to be qualified.", False, []),
            ("Nina believed herself to be qualified.", True, []),
            ("Nina believed him to be qualified.", True, []),
            ("Nina was believed to be qualified.", True, []),
            ("Nina believed that she was qualified.", True, []),
            ("Nina hoped to be qualified.", True, []),
        ]:
            with self.subTest(sentence=sentence, context=context):
                self.check_case(sentence, analyze(sentence)["root"], context, expected)


class InterrogativeInfinitivalSubjectTests(unittest.TestCase):
    def test_selected_wh_infinitival(self):
        sentence = "She explained how for us to start the pump."
        tree = NodeBuilder().build(parse_parse_string(
            "(S (NP (PRP She)) (VP (VBD explained) (SBAR (WHADVP (WRB how)) "
            "(SBAR (IN for) (S (NP (PRP us)) (VP (TO to) (VP (VB start) (NP (DT the) (NN pump)))))))) (. .))"
        ), 10)
        candidate, = probe_interrogative_infinitival_subject(
            sentence, tree, variety="standard_english"
        )["candidates"]
        self.assertEqual(candidate["rule_id"], "CLS-407")
        a, b = candidate["relation"]["subject_char_span"]
        self.assertEqual(sentence[a:b], "us")
        self.assertIsNone(candidate["edit_hint"])

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_interrogative_infinitivals(self):
        for sentence, target in [
            ("She explained how for us to start the pump.", True),
            ("They discussed which route for them to take.", True),
            ("She explained how to start the pump.", False),
            ("She explained how we should start the pump.", False),
            ("They arranged for us to start the pump.", False),
            ("They discussed a route for us to take.", False),
            ("They discussed which route we should take.", False),
        ]:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                result = probe_interrogative_infinitival_subject(
                    sentence, analysis["root"], variety="standard_english"
                )
                found = [row["rule_id"] for row in result["candidates"]]
                self.assertIn(found, ([], ["CLS-407"]) if target else ([],))
                print(f"Cambridge wh-infinitival {sentence!r}: {found}; target={target}; parse={analysis['parse_string']}")


class ParticipialRelativeMarkerTests(unittest.TestCase):
    def test_bare_participle_and_finite_relative(self):
        for auxiliary in (False, True):
            verb = "(VBG waiting) (ADVP (RB outside))"
            predicate = f"(VBP are) (VP {verb})" if auxiliary else verb
            sentence = "The people who " + ("are " if auxiliary else "") + "waiting outside need shelter."
            parse = (
                "(S (NP (NP (DT The) (NNS people)) "
                f"(SBAR (WHNP (WP who)) (S (VP {predicate})))) "
                "(VP (VBP need) (NP (NN shelter))) (. .))"
            )
            with self.subTest(auxiliary=auxiliary):
                tree = NodeBuilder().build(parse_parse_string(parse), 9 if auxiliary else 8)
                rows = probe_participial_relative_marker(sentence, tree, variety="standard_english")["candidates"]
                self.assertEqual([row["rule_id"] for row in rows], [] if auxiliary else ["CLS-408"])
                if rows:
                    start, end = rows[0]["relation"]["marker_char_span"]
                    self.assertEqual(sentence[start:end], "who")
                    self.assertIsNone(rows[0]["edit_hint"])

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_participial_modifiers(self):
        for sentence, target in [
            ("The people who waiting outside need shelter.", True),
            ("The workers who repairing the lift need more time.", True),
            ("The people waiting outside need shelter.", False),
            ("The people who are waiting outside need shelter.", False),
            ("The workers who repair the lift need more time.", False),
            ("I know who is repairing the lift.", False),
            ("The person to contact is here.", False),
        ]:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_participial_relative_marker(
                    sentence, analysis["root"], variety="standard_english"
                )["candidates"]
                found = [row["rule_id"] for row in rows]
                self.assertIn(found, ([], ["CLS-408"]) if target else ([],))
                print(f"Cambridge participial modifier {sentence!r}: {found}; target={target}; parse={analysis['parse_string']}")


class DeterminedParticipleTests(unittest.TestCase):
    def test_verbal_object_and_nominal_of_phrase(self):
        for phrase, text, expected in [
            ("(NP (DT The) (VP (VBG painting) (NP (DT the) (NN fence))))",
             "The painting the fence", ["MORPH-041"]),
            ("(NP (DT The) (NN painting) (PP (IN of) (NP (DT the) (NN fence))))",
             "The painting of the fence", []),
            ("(S (VP (VBG Painting) (NP (DT the) (NN fence))))",
             "Painting the fence", []),
        ]:
            with self.subTest(text=text):
                parse = f"(S {phrase} (VP (VBD took) (NP (NNS hours))) (. .))"
                tree = NodeBuilder().build(parse_parse_string(parse), len(re.findall(r"\([^()]+\)", parse)))
                rows = probe_determined_participle(f"{text} took hours.", tree,
                                                   variety="standard_english")["candidates"]
                self.assertEqual([row["rule_id"] for row in rows], expected)
                for row in rows:
                    self.assertIsNone(row["edit_hint"])

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_determined_participles(self):
        for sentence, target in [
            ("The painting the fence took hours.", True),
            ("The repairing the roof delayed the workers.", True),
            ("Painting the fence took hours.", False),
            ("The painting of the fence took hours.", False),
            ("The sleeping child woke up.", False),
            ("The painting the curator bought was expensive.", False),
            ("Their repairing the roof took hours.", False),
        ]:
            with self.subTest(sentence=sentence):
                analysis = analyze(sentence)
                rows = probe_determined_participle(sentence, analysis["root"],
                                                   variety="standard_english")["candidates"]
                found = [row["rule_id"] for row in rows]
                print(f"Cambridge determined participle {sentence!r}: {found}; target={target}; parse={analysis['parse_string']}")
                self.assertIn(found, ([], ["MORPH-041"]) if target else ([],))
