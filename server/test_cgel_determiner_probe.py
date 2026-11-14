import glob
import json
import unittest
from pathlib import Path

from cgel_determiner_probe import probe_determiner
from parse_engine import analyze


ROOT = Path(__file__).resolve().parents[1]
RULE_IDS = [
    "PHR-028", "PHR-043", "PHR-044", "PHR-080", "PHR-084", "PHR-088",
    "PHR-126", "PHR-128", "PHR-133", "PHR-140", "PHR-157", "PHR-161",
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

    def evaluate(self, sentence):
        return probe_determiner(sentence, analyze(sentence)["root"])

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
        result = probe_determiner("Each furniture was packed.", variety="other")
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["candidates"], [])


class EditTests(unittest.TestCase):
    def row(self, sentence, rule_id):
        rows = [row for row in probe_determiner(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == rule_id]
        self.assertEqual(len(rows), 1)
        return rows[0]

    def test_much_replaced_by_indefinite_article(self):
        sentence = "They hired much assistant."
        row = self.row(sentence, "PHR-043")
        span = row["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "much")
        self.assertEqual(row["edit_hint"]["replacement"], "an")

    def test_each_mass_inserts_piece_of(self):
        sentence = "Each furniture was packed."
        row = self.row(sentence, "PHR-044")
        span = row["edit_hint"]["char_span"]
        self.assertEqual(span[0], sentence.index("furniture"))
        self.assertEqual(row["edit_hint"]["replacement"], "piece of ")

    def test_initial_a_deleted_after_determiner(self):
        sentence = "These a hundred bulbs came from a single supplier."
        row = self.row(sentence, "PHR-128")
        span = row["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "a ")
        self.assertEqual(row["edit_hint"]["replacement"], "")

    def test_all_a_replaced_by_a_whole(self):
        sentence = "We waited all a week for parts."
        row = self.row(sentence, "PHR-133")
        span = row["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "all a")
        self.assertEqual(row["edit_hint"]["replacement"], "a whole")

    def test_every_of_replaced_by_each(self):
        sentence = "Every of the lamps was inspected."
        row = self.row(sentence, "PHR-140")
        span = row["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "Every")
        self.assertEqual(row["edit_hint"]["replacement"], "Each")

    def test_no_of_replaced_by_none(self):
        sentence = "No of the bolts were missing."
        row = self.row(sentence, "PHR-161")
        self.assertEqual(row["edit_hint"]["replacement"], "None")

    def test_bare_subject_inserts_the(self):
        sentence = "Old technician arrived."
        row = self.row(sentence, "PHR-028")
        span = row["edit_hint"]["char_span"]
        self.assertEqual(span[0], 0)
        self.assertEqual(row["edit_hint"]["replacement"], "The ")


class HeldOutTests(unittest.TestCase):
    def flagged(self, sentence, rule_id):
        return [row for row in probe_determiner(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == rule_id]

    def test_bare_subject_variants(self):
        self.assertTrue(self.flagged("New engineer arrived.", "PHR-028"))
        self.assertFalse(self.flagged("Water arrived.", "PHR-028"))
        self.assertFalse(self.flagged("The workers arrived.", "PHR-028"))

    def test_much_variants(self):
        self.assertTrue(self.flagged("They hired much engineer.", "PHR-043"))
        self.assertFalse(self.flagged("She drank much water.", "PHR-043"))

    def test_each_variants(self):
        self.assertTrue(self.flagged("Every equipment was checked.", "PHR-044"))
        self.assertFalse(self.flagged("Each chocolate was wrapped.", "PHR-044"))

    def test_deal_variants(self):
        self.assertTrue(self.flagged("A great deal of chairs were sold.", "PHR-080"))
        self.assertFalse(self.flagged("A great deal of water was wasted.", "PHR-080"))
        self.assertFalse(self.flagged("A great deal of the equipment was damaged.", "PHR-080"))

    def test_approximate_number_variants(self):
        self.assertTrue(self.flagged("Hundreds of equipment were stored.", "PHR-084"))
        self.assertFalse(self.flagged("Hundreds of litres of milk were delivered.", "PHR-084"))
        self.assertFalse(self.flagged("Hundreds of condensation droplets covered the window.", "PHR-084"))

    def test_cardinal_variants(self):
        rows = self.flagged("One drivers stopped.", "PHR-088")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "driver")
        self.assertFalse(self.flagged("One in ten cyclists stopped.", "PHR-088"))
        self.assertFalse(self.flagged("One or more pumpkins were damaged.", "PHR-088"))

    def test_fused_the_variants(self):
        self.assertTrue(self.flagged("I kept the he repaired.", "PHR-126"))
        self.assertFalse(self.flagged("I kept the red one.", "PHR-126"))

    def test_initial_a_variants(self):
        self.assertTrue(self.flagged("Those a thousand bulbs filled three boxes.", "PHR-128"))
        self.assertFalse(self.flagged("Those one hundred bulbs filled three boxes.", "PHR-128"))

    def test_all_a_variants(self):
        self.assertTrue(self.flagged("They painted all a house before lunch.", "PHR-133"))
        self.assertFalse(self.flagged("They painted all the wall before lunch.", "PHR-133"))

    def test_every_of_variants(self):
        self.assertTrue(self.flagged("Every of the chairs was moved.", "PHR-140"))
        self.assertFalse(self.flagged("Every chair was moved.", "PHR-140"))
        self.assertFalse(self.flagged("Every one of the chairs was moved.", "PHR-140"))

    def test_either_variants(self):
        rows = self.flagged("You can take either roads.", "PHR-157")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "road")
        self.assertFalse(self.flagged("You can take either of the roads.", "PHR-157"))

    def test_no_none_variants(self):
        self.assertTrue(self.flagged("None chairs were missing.", "PHR-161"))
        self.assertFalse(self.flagged("None of the chairs were missing.", "PHR-161"))
        self.assertFalse(self.flagged("She felt none the worse afterward.", "PHR-161"))
        self.assertFalse(self.flagged("None other than the manager arrived.", "PHR-161"))

    def test_plural_looking_verbs_are_not_nominal_heads(self):
        self.assertFalse(self.flagged("This one costs more than that.", "PHR-088"))
        self.assertFalse(self.flagged("Either works for me.", "PHR-157"))
        self.assertFalse(self.flagged("None works without power.", "PHR-161"))


if __name__ == "__main__":
    unittest.main()
