import json
import unittest
from pathlib import Path

from cgel_punctuation_probe import probe_all
from parse_engine import analyze


ROOT = Path(__file__).resolve().parents[1]
RULE_IDS = [
    "OTH-671", "OTH-688", "OTH-698", "OTH-699", "OTH-701", "OTH-708",
    "OTH-712", "OTH-715", "OTH-717", "OTH-726", "OTH-730", "OTH-737",
    "OTH-740", "OTH-743", "OTH-756", "OTH-764",
]


def source_rules():
    rows = json.loads((ROOT / "grammar/rules/other.json").read_text(encoding="utf-8"))
    return {row["id"]: row for row in rows if row["id"] in RULE_IDS}


class SourceExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = source_rules()

    def evaluate(self, sentence):
        return probe_all(sentence, analyze(sentence)["root"])

    def test_incorrect_examples_are_flagged(self):
        for rule_id in RULE_IDS:
            rule = self.rules[rule_id]
            for example in rule["examples"]["incorrect"]:
                with self.subTest(rule=rule_id, sentence=example["text"]):
                    result = self.evaluate(example["text"])
                    self.assertFalse(result["production_enabled"])
                    self.assertIn(rule_id, [row["rule_id"] for row in result["candidates"]])

    def test_correct_and_guard_examples_are_not_flagged(self):
        for rule_id in RULE_IDS:
            rule = self.rules[rule_id]
            texts = [example["text"] for example in rule["examples"]["correct"]]
            texts.extend(rule["diagnostic"]["false_positive_guards"])
            for sentence in texts:
                with self.subTest(rule=rule_id, sentence=sentence):
                    result = self.evaluate(sentence)
                    self.assertNotIn(rule_id, [row["rule_id"] for row in result["candidates"]])

    def test_variety_is_not_evaluated(self):
        result = probe_all("The repair crew, arrived at dawn.", analyze(
            "The repair crew, arrived at dawn.")["root"], variety="other")
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["candidates"], [])


class EditSpanTests(unittest.TestCase):
    def test_abbreviation_stop_deletes_second_dot(self):
        sentence = "The letter came from Washington, D.C.."
        rows = [row for row in probe_all(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == "OTH-764"]
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], ".")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "")

    def test_apostrophe_shape_replaces_opening_mark(self):
        sentence = "They danced to rock ‘n’ roll after dinner."
        rows = [row for row in probe_all(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == "OTH-671"]
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "‘")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "’")

    def test_compound_numeral_inserts_hyphen(self):
        sentence = "Twenty seven people signed the letter."
        rows = [row for row in probe_all(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == "OTH-756"]
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], " ")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "-")

    def test_parenthetical_article_replaces_article(self):
        sentence = "We saw a (unexpectedly large) owl."
        rows = [row for row in probe_all(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == "OTH-726"]
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "a")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "an")

    def test_direct_speech_boundary_inserts_comma(self):
        sentence = "Mara asked “When will the gates open?”"
        rows = [row for row in probe_all(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == "OTH-712"]
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], " ")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], ", ")

    def test_quoted_terminal_suppression_deletes_competing_stop(self):
        sentence = "Mara asked, “Where are the keys?”."
        rows = [row for row in probe_all(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == "OTH-743"]
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], ".")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "")

    def test_nested_quotes_replaces_both_inner_marks(self):
        sentence = "“The sign said “Closed”,” she explained."
        rows = [row for row in probe_all(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == "OTH-737"]
        self.assertEqual(len(rows), 2)
        replacements = {row["edit_hint"]["replacement"] for row in rows}
        self.assertEqual(replacements, {"‘", "’"})

    def test_subject_verb_comma_deletes_comma(self):
        sentence = "The repair crew, arrived at dawn."
        rows = [row for row in probe_all(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == "OTH-715"]
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], ",")

    def test_vocative_boundaries_insert_two_commas(self):
        sentence = "Could you Lina check the latch?"
        rows = [row for row in probe_all(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == "OTH-717"]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["edit_hint"]["replacement"] == "," for row in rows))

    def test_colon_series_replaces_each_colon(self):
        sentence = "The school opened at eight: the clinic opened at nine: the shop opened at ten."
        rows = [row for row in probe_all(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == "OTH-699"]
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["edit_hint"]["replacement"] == ";" for row in rows))

    def test_nested_colon_replaces_inner_colon(self):
        sentence = "One problem remained: the lift was broken, leaving only one option: the stairs."
        rows = [row for row in probe_all(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == "OTH-698"]
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], ":")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], ",")


class HeldOutPunctuationTests(unittest.TestCase):
    def flags(self, sentence, rule_id):
        result = probe_all(sentence, analyze(sentence)["root"])
        return [row for row in result["candidates"] if row["rule_id"] == rule_id]

    def test_abbreviation_variants(self):
        for sentence in (
            "The report cited Smith et al..",
            "The meeting is at 5 p.m..",
            "She lives in the U.S.A..",
            "He works at Acme Inc..",
        ):
            with self.subTest(sentence=sentence):
                self.assertTrue(self.flags(sentence, "OTH-764"))
        for sentence in ("Wait..", "Did it end at 5 p.m.?", "The value was 3.14."):
            with self.subTest(sentence=sentence):
                self.assertFalse(self.flags(sentence, "OTH-764"))

    def test_quotation_suppression_leaves_abbreviations(self):
        self.assertFalse(self.flags("“I live in D.C.”?", "OTH-743"))

    def test_medial_quote_does_not_cross_a_sentence_boundary(self):
        self.assertFalse(self.flags("She said, “I will wait.” Then she left.", "OTH-740"))

    def test_parallel_semicolon_series_is_not_nested(self):
        sentence = "The office opened at eight; Sue arrived; she opened the mail."
        self.assertFalse(self.flags(sentence, "OTH-698"))

    def test_parenthetical_agreement_ignores_plural_heads(self):
        self.assertFalse(self.flags("Students (and teachers) have arrived.", "OTH-730"))

    def test_article_sound_exceptions(self):
        self.assertTrue(self.flags("a (hour-long) delay", "OTH-726"))
        self.assertTrue(self.flags("an (university) student", "OTH-726"))
        self.assertFalse(self.flags("a (rather unusual) omelette", "OTH-726"))
        self.assertFalse(self.flags("an (unusually small) bird", "OTH-726"))

    def test_vocative_partial_comma(self):
        rows = self.flags("Could you, Lina check the latch?", "OTH-717")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], ",")
        self.assertFalse(self.flags("Could you, Lina, check the latch?", "OTH-717"))

    def test_subordinate_question_guards(self):
        self.assertTrue(self.flags("She asked where he went?", "OTH-688"))
        self.assertFalse(self.flags("Do you know where he went?", "OTH-688"))
        self.assertFalse(self.flags("She asked, “Where did he go?”", "OTH-688"))


if __name__ == "__main__":
    unittest.main()
