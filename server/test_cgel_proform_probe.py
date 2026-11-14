import glob
import json
import unittest
from pathlib import Path

from cgel_proform_probe import probe_proform


ROOT = Path(__file__).resolve().parents[1]
RULE_IDS = ["PHR-629", "PHR-632", "PHR-644", "PHR-645", "PHR-654",
            "PHR-666", "PHR-684", "PHR-704", "PHR-705", "PHR-706", "PHR-737"]


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
        result = probe_proform(sentence)
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
        result = probe_proform("We only have two ones.", variety="other")
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["candidates"], [])


class EditTests(unittest.TestCase):
    def rows(self, sentence, rule_id):
        return [row for row in probe_proform(sentence)["candidates"]
                if row["rule_id"] == rule_id]

    def test_fused_that(self):
        sentence = "The width of the kitchen exceeds this of the hallway."
        rows = self.rows(sentence, "PHR-629")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "this")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "that")

    def test_mass_one_becomes_that(self):
        sentence = "The equipment in this lab is older than the one in the new wing."
        rows = self.rows(sentence, "PHR-632")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "the one")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "that")

    def test_two_ones_becomes_two(self):
        sentence = "I need four more clamps, but we only have two ones."
        rows = self.rows(sentence, "PHR-644")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "two")

    def test_no_ones_becomes_none(self):
        sentence = "We looked for pegs but found no ones."
        rows = self.rows(sentence, "PHR-644")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "none")

    def test_every_fused(self):
        sentence = "We checked the seals, and every was intact."
        rows = self.rows(sentence, "PHR-645")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "every")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "every one")

    def test_bare_ones_object(self):
        sentence = "We still need extension cords. Do you stock ones?"
        rows = self.rows(sentence, "PHR-654")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "them")

    def test_other_order(self):
        sentence = "We chose the blue others."
        rows = self.rows(sentence, "PHR-666")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "the other blue ones")

    def test_aux_reduction_do(self):
        sentence = "Ari will be outside soon, and Lee does too."
        rows = self.rows(sentence, "PHR-684")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "will too")

    def test_be_did_so(self):
        sentence = "They asked me to be discreet, and I did so."
        rows = self.rows(sentence, "PHR-704")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "was")

    def test_do_so_object(self):
        sentence = "I didn't invite Rae, but I did so Sol."
        rows = self.rows(sentence, "PHR-705")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], " so ")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], " ")

    def test_do_so_comparison(self):
        sentence = "She cycles farther than I do so."
        rows = self.rows(sentence, "PHR-706")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], " so")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "")

    def test_additive_so(self):
        sentence = "Nora can't hear the alarm, and so can't Lee."
        rows = self.rows(sentence, "PHR-737")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "and neither can Lee")


class HeldOutTests(unittest.TestCase):
    def flagged(self, sentence, rule_id):
        return [row for row in probe_proform(sentence)["candidates"]
                if row["rule_id"] == rule_id]

    def test_fused_that_variants(self):
        self.assertTrue(self.flagged(
            "The duties of the new staff resemble these of their predecessors.", "PHR-629"))
        self.assertFalse(self.flagged("This is wider than the doorway.", "PHR-629"))

    def test_mass_one_variants(self):
        self.assertTrue(self.flagged(
            "The furniture here is older than the one in the annex.", "PHR-632"))
        self.assertFalse(self.flagged(
            "I tried a chair here. The one in the annex was bigger.", "PHR-632"))

    def test_bare_ones_variants(self):
        self.assertTrue(self.flagged("We found no ones.", "PHR-644"))
        self.assertFalse(self.flagged("We found two wooden ones.", "PHR-644"))
        self.assertFalse(self.flagged("We found no loose ones.", "PHR-644"))

    def test_every_variants(self):
        self.assertTrue(self.flagged("I tested the bulbs, and every lit up.", "PHR-645"))
        self.assertFalse(self.flagged("Every bulb lit up.", "PHR-645"))

    def test_ones_object_variants(self):
        self.assertEqual(
            self.flagged("Rae had concerns, and Ben had ones too.", "PHR-654")[0]["edit_hint"]["replacement"],
            "some",
        )
        self.assertFalse(self.flagged("Do you stock longer ones?", "PHR-654"))
        self.assertFalse(self.flagged("Ones with rubber grips were available.", "PHR-654"))

    def test_other_order_variants(self):
        self.assertTrue(self.flagged("Please set aside the small others.", "PHR-666"))
        self.assertFalse(self.flagged("We chose the others.", "PHR-666"))
        self.assertFalse(self.flagged("We chose the other blue folders.", "PHR-666"))

    def test_aux_reduction_variants(self):
        self.assertEqual(
            self.flagged("Nina has been ill all week, and her brother does too.", "PHR-684")[0]["edit_hint"]["replacement"],
            "has too",
        )
        self.assertFalse(self.flagged("Nina should have called, but her brother did.", "PHR-684"))
        self.assertFalse(self.flagged("Ari will open the store, and Lee will too.", "PHR-684"))

    def test_be_did_so_variants(self):
        self.assertTrue(self.flagged("She tried to be patient, and eventually she did so.", "PHR-704"))
        self.assertFalse(self.flagged("They asked me to seal the box, and I did so.", "PHR-704"))

    def test_do_so_object_variants(self):
        self.assertTrue(self.flagged("I won't inspect the roof, but I will do so the cellar.", "PHR-705"))
        self.assertFalse(self.flagged("I checked the latch and did so carefully.", "PHR-705"))
        self.assertFalse(self.flagged("I hope they won't do that to me.", "PHR-705"))

    def test_do_so_comparison_variants(self):
        self.assertTrue(self.flagged("He judged it fair, as I did so.", "PHR-706"))
        self.assertFalse(self.flagged("I closed the hatch. As I did so, the warning light went out.", "PHR-706"))
        self.assertFalse(self.flagged("She cleaned the vent and did so more carefully than before.", "PHR-706"))

    def test_additive_so_variants(self):
        self.assertTrue(self.flagged("Mina won't attend, and so won't Theo.", "PHR-737"))
        self.assertFalse(self.flagged("The alarm was broken, so Lee couldn't hear it.", "PHR-737"))
        self.assertFalse(self.flagged("Nora can hear the alarm, and so too can Lee.", "PHR-737"))


if __name__ == "__main__":
    unittest.main()
