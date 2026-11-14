import glob
import json
import unittest
from pathlib import Path

from cgel_final_surface_probe import probe_final_surface


ROOT = Path(__file__).resolve().parents[1]
RULE_IDS = [
    "PHR-220", "PHR-258", "PHR-590", "PHR-593", "PHR-600", "PHR-602",
    "PHR-653", "CLS-1222", "CLS-1259", "CLS-1274", "CLS-1276", "CLS-1329",
]


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

    def flagged(self, sentence, rule_id):
        result = probe_final_surface(sentence)
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
        result = probe_final_surface("Every chef greeted each other.", variety="other")
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["candidates"], [])


class EditTests(unittest.TestCase):
    def rows(self, sentence, rule_id):
        return [row for row in probe_final_surface(sentence)["candidates"]
                if row["rule_id"] == rule_id]

    def test_postmodifier_order(self):
        sentence = "Something for the hike waterproof was already packed."
        rows = self.rows(sentence, "PHR-220")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "Something waterproof for the hike")

    def test_prehead_complement(self):
        sentence = "We hired a tax experienced adviser."
        rows = self.rows(sentence, "PHR-258")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "an experienced tax adviser")

    def test_split_each(self):
        sentence = "The twins thanked each the other."
        rows = self.rows(sentence, "PHR-590")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "each other")

    def test_split_one(self):
        sentence = "The escorts followed one the other along the trail."
        rows = self.rows(sentence, "PHR-593")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "one another")

    def test_every_reciprocal(self):
        sentence = "Every chef greeted each other."
        rows = self.rows(sentence, "PHR-600")
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["edit_hint"]["replacement"].startswith("All the chefs"))

    def test_reciprocal_adjunct(self):
        sentence = "The climbers packed the equipment one another."
        rows = self.rows(sentence, "PHR-602")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "The climbers packed the equipment themselves")

    def test_mass_one(self):
        sentence = "Your feedback was more detailed than the one from the tutor."
        rows = self.rows(sentence, "PHR-653")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "that")

    def test_supplementary_as(self):
        sentence = "As you know it, the bridge is closed."
        rows = self.rows(sentence, "CLS-1222")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], " it")

    def test_comparative_grade(self):
        sentence = "This is the sturdier of the four frames."
        rows = self.rows(sentence, "CLS-1259")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "the sturdiest of the four")

    def test_superlative_definiteness(self):
        sentence = "We chose a quietest room in the hotel."
        rows = self.rows(sentence, "CLS-1274")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "the quietest room in the hotel")

    def test_free_superlative(self):
        sentence = "The river is lowest it has been all summer."
        rows = self.rows(sentence, "CLS-1276")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "the ")

    def test_double_object_order(self):
        sentence = "We sent a reminder everyone on the waiting list."
        rows = self.rows(sentence, "CLS-1329")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "sent everyone on the waiting list a reminder")


class HeldOutTests(unittest.TestCase):
    def flagged(self, sentence, rule_id):
        return [row for row in probe_final_surface(sentence)["candidates"]
                if row["rule_id"] == rule_id]

    def test_postmodifier_variants(self):
        self.assertTrue(self.flagged("Something for dinner spicy was on the menu.", "PHR-220"))
        self.assertFalse(self.flagged(
            "We packed something else waterproof for the hike.", "PHR-220"))
        self.assertFalse(self.flagged("I considered everything near the gate unusual.", "PHR-220"))

    def test_prehead_variants(self):
        self.assertTrue(self.flagged("She consulted a legal respected adviser.", "PHR-258"))
        self.assertFalse(self.flagged("We hired a highly experienced adviser.", "PHR-258"))
        self.assertFalse(self.flagged("She consulted an adviser on legal matters.", "PHR-258"))

    def test_split_variants(self):
        self.assertTrue(self.flagged("The runners nodded each to the others.", "PHR-590"))
        self.assertFalse(self.flagged("The twins each thanked the other.", "PHR-590"))
        self.assertTrue(self.flagged("The delegates questioned one the other.", "PHR-593"))
        self.assertFalse(self.flagged("One delay followed another.", "PHR-593"))

    def test_every_variants(self):
        self.assertTrue(self.flagged("Every dancer recognized one another.", "PHR-600"))
        self.assertFalse(self.flagged("Everyone recognized one another.", "PHR-600"))
        self.assertFalse(self.flagged("Every chef greeted the others.", "PHR-600"))

    def test_adjunct_variants(self):
        self.assertTrue(self.flagged("The swimmers each other improved their strokes.", "PHR-602"))
        self.assertFalse(self.flagged("The swimmers looked after each other's gear.", "PHR-602"))
        self.assertFalse(self.flagged("The climbers spoke to one another.", "PHR-602"))

    def test_mass_variants(self):
        self.assertTrue(self.flagged(
            "The equipment in the studio is older than the one in the hall.", "PHR-653"))
        self.assertFalse(self.flagged(
            "The studio has a new scanner. The one in the hall is older.", "PHR-653"))

    def test_supplementary_as_variants(self):
        self.assertTrue(self.flagged("As I mentioned it, the clinic is closed on Friday.", "CLS-1222"))
        self.assertFalse(self.flagged(
            "The neighborhood, as we know it, grew around the station.", "CLS-1222"))
        self.assertFalse(self.flagged("When I mentioned it, nobody objected.", "CLS-1222"))

    def test_comparative_variants(self):
        self.assertTrue(self.flagged("That is the warmer of the three rooms.", "CLS-1259"))
        self.assertFalse(self.flagged("This is the sturdier of the two frames.", "CLS-1259"))
        self.assertFalse(self.flagged("This is the best of the two options.", "CLS-1259"))

    def test_superlative_variants(self):
        self.assertTrue(self.flagged("They surveyed two tallest buildings in town.", "CLS-1274"))
        self.assertFalse(self.flagged("Several runners set personal best times.", "CLS-1274"))
        self.assertFalse(self.flagged("It was a most satisfying result.", "CLS-1274"))

    def test_free_superlative_variants(self):
        self.assertTrue(self.flagged(
            "The engine is running the most smoothly which it ever has.", "CLS-1276"))
        self.assertFalse(self.flagged("The river is lowest in late summer.", "CLS-1276"))
        self.assertFalse(self.flagged(
            "They inspected the bridge, which was the oldest in town.", "CLS-1276"))

    def test_double_object_variants(self):
        self.assertTrue(self.flagged("They gave a voucher each student who stayed late.", "CLS-1329"))
        self.assertFalse(self.flagged("We sent a reminder to everyone on the waiting list.", "CLS-1329"))
        self.assertFalse(self.flagged("They gave a voucher to each student who stayed late.", "CLS-1329"))


if __name__ == "__main__":
    unittest.main()
