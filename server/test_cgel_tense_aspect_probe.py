import glob
import json
import unittest
from pathlib import Path

from cgel_tense_aspect_probe import probe_tense_aspect
from parse_engine import analyze


ROOT = Path(__file__).resolve().parents[1]
RULE_IDS = ["OTH-377", "OTH-439", "OTH-458"]


def source_rules():
    rows = {}
    for path in glob.glob(str(ROOT / "grammar/rules/*.json")):
        for row in json.loads(Path(path).read_text(encoding="utf-8")):
            if row.get("id") in RULE_IDS:
                rows[row["id"]] = row
    return rows


class SourceExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rules = source_rules()

    def evaluate(self, sentence):
        return probe_tense_aspect(sentence, analyze(sentence)["root"])

    def flagged(self, sentence, rule_id):
        result = self.evaluate(sentence)
        self.assertFalse(result["production_enabled"])
        return [row for row in result["candidates"] if row["rule_id"] == rule_id]

    def test_incorrect_examples_are_flagged(self):
        for rule_id in RULE_IDS:
            for example in self.rules[rule_id]["examples"]["incorrect"]:
                with self.subTest(rule=rule_id, sentence=example["text"]):
                    self.assertTrue(self.flagged(example["text"], rule_id))

    def test_correct_and_guard_examples_are_not_flagged(self):
        for rule_id in RULE_IDS:
            rule = self.rules[rule_id]
            texts = [example["text"] for example in rule["examples"]["correct"]]
            texts.extend(rule["diagnostic"]["false_positive_guards"])
            for sentence in texts:
                with self.subTest(rule=rule_id, sentence=sentence):
                    self.assertFalse(self.flagged(sentence, rule_id))

    def test_variety_is_not_evaluated(self):
        result = probe_tense_aspect("I wish I can attend.", variety="other")
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["candidates"], [])


class EditTests(unittest.TestCase):
    def rows(self, sentence, rule_id):
        return [row for row in probe_tense_aspect(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == rule_id]

    def test_temporal_will_replaced_by_present(self):
        sentence = "We will begin as soon as the room will be ready."
        rows = self.rows(sentence, "OTH-377")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "will be")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "is")

    def test_temporal_will_third_person_s(self):
        sentence = "I will send the parcel when the courier will arrive."
        rows = self.rows(sentence, "OTH-377")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "will arrive")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "arrives")

    def test_could_replaced_by_was_able_to(self):
        sentence = "She searched the cupboard and could find the spare key."
        rows = self.rows(sentence, "OTH-439")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "could")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "was able to")

    def test_wish_modal_replaced_by_remote(self):
        sentence = "I wish I can attend tomorrow."
        rows = self.rows(sentence, "OTH-458")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "can")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "could")


class HeldOutTests(unittest.TestCase):
    def rows(self, sentence, rule_id):
        return [row for row in probe_tense_aspect(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == rule_id]

    def test_temporal_will_variants(self):
        self.assertTrue(self.rows("I will call you after the meeting will end.", "OTH-377"))
        self.assertTrue(self.rows("We will leave before the train will depart.", "OTH-377"))
        self.assertFalse(self.rows("She asked when the train will arrive.", "OTH-377"))
        self.assertFalse(self.rows("I will explain it before you ask.", "OTH-377"))

    def test_could_variants(self):
        rows = self.rows("They tried the door twice and could unlock it.", "OTH-439")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "were able to")
        self.assertFalse(self.rows("When I was younger, I could open those cases easily.", "OTH-439"))
        self.assertFalse(self.rows("I could hear the birds singing.", "OTH-439"))
        self.assertFalse(self.rows("She said she could open the case.", "OTH-439"))

    def test_wish_variants(self):
        self.assertEqual(
            self.rows("I wish she is here.", "OTH-458")[0]["edit_hint"]["replacement"], "were")
        self.assertEqual(
            self.rows("I wish we can stay.", "OTH-458")[0]["edit_hint"]["replacement"], "could")
        self.assertEqual(
            self.rows("I wish he has more time.", "OTH-458")[0]["edit_hint"]["replacement"], "had")
        self.assertFalse(self.rows("I wish them all the best.", "OTH-458"))
        self.assertFalse(self.rows("I wish to attend tomorrow.", "OTH-458"))
        self.assertFalse(self.rows("I wished yesterday that she were here.", "OTH-458"))


if __name__ == "__main__":
    unittest.main()
