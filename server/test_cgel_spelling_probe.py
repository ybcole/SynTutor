import glob
import json
import unittest
from pathlib import Path

from cgel_spelling_probe import probe_spelling


ROOT = Path(__file__).resolve().parents[1]
RULE_IDS = [
    "PHR-164", "MORPH-109", "MORPH-237", "MORPH-258", "MORPH-309",
    "MORPH-311", "MORPH-313", "MORPH-316", "MORPH-357", "MORPH-385",
    "MORPH-445", "MORPH-477", "MORPH-482", "MORPH-483",
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
        result = probe_spelling(sentence)
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
        result = probe_spelling("The guests paniced.", variety="other")
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["candidates"], [])


class EditSpanTests(unittest.TestCase):
    def rows(self, sentence, rule_id):
        return [row for row in probe_spelling(sentence)["candidates"]
                if row["rule_id"] == rule_id]

    def test_split_another_replaces_whole_phrase(self):
        sentence = "An other parcel arrived."
        rows = self.rows(sentence, "PHR-164")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "An other")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "Another")

    def test_final_c_inserts_k(self):
        sentence = "The guests paniced at the noise."
        rows = self.rows(sentence, "MORPH-109")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "k")
        self.assertEqual(span[0], sentence.index("paniced") + len("panic"))

    def test_measure_unit_becomes_singular(self):
        sentence = "We booked a four-nights stay."
        rows = self.rows(sentence, "MORPH-258")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "nights")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "night")

    def test_power_head_loses_plural(self):
        sentence = "The school ordered four hundreds desks."
        rows = self.rows(sentence, "MORPH-477")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "hundreds")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "hundred")

    def test_compound_ordinal_replaces_final_unit(self):
        sentence = "Their twenty-twoth entry won a prize."
        rows = self.rows(sentence, "MORPH-482")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "twenty-twoth")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "twenty-second")

    def test_fraction_denominator_plural(self):
        sentence = "The team completed two third of the route."
        rows = self.rows(sentence, "MORPH-483")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "third")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "thirds")


class HeldOutSpellingTests(unittest.TestCase):
    def rows(self, sentence, rule_id):
        return [row for row in probe_spelling(sentence)["candidates"]
                if row["rule_id"] == rule_id]

    def test_final_c_variants(self):
        self.assertTrue(self.rows("They were frolicing by the river.", "MORPH-109"))
        self.assertTrue(self.rows("The unit bivouaced near the ridge.", "MORPH-109"))
        self.assertFalse(self.rows("They picnic every summer.", "MORPH-109"))

    def test_er_preposition_variants(self):
        self.assertEqual(
            self.rows("The hanger-ons waited outside.", "MORPH-237")[0]["edit_hint"]["replacement"],
            "hangers-on",
        )
        self.assertFalse(self.rows("The take-offs were delayed.", "MORPH-237"))

    def test_measure_variants(self):
        self.assertTrue(self.rows("They planned a five-miles walk.", "MORPH-258"))
        self.assertTrue(self.rows("We took a ten-minutes break.", "MORPH-258"))
        self.assertFalse(self.rows("The trench was six feet deep.", "MORPH-258"))
        self.assertFalse(self.rows("They gave us three weeks' notice.", "MORPH-258"))

    def test_y_replacement_variants(self):
        self.assertTrue(self.rows("The happyness of the crowd was obvious.", "MORPH-316"))
        self.assertFalse(self.rows("The invoice is payable next week.", "MORPH-316"))

    def test_negative_prefix_variants(self):
        self.assertTrue(self.rows("They found an inlegal entry.", "MORPH-357"))
        self.assertFalse(self.rows("The route was unmarked.", "MORPH-357"))
        self.assertFalse(self.rows("The gymnast was in balance.", "MORPH-357"))

    def test_invariant_inhabitant_variants(self):
        self.assertTrue(self.rows("Two Japaneses joined the tour.", "MORPH-385"))
        self.assertFalse(self.rows("Two Taiwanese volunteers arrived early.", "MORPH-385"))
        self.assertFalse(self.rows("The Swiss committee submitted its report.", "MORPH-385"))

    def test_possessive_ed_variants(self):
        self.assertTrue(self.rows("They rented a four-bedroomsed house.", "MORPH-445"))
        self.assertFalse(self.rows("They rented a three-bedroom flat.", "MORPH-445"))
        self.assertFalse(self.rows("The flat has three bedrooms.", "MORPH-445"))

    def test_power_head_variants(self):
        self.assertTrue(self.rows("The charity raised three millions pounds.", "MORPH-477"))
        self.assertFalse(self.rows("Thousands of photographs survived.", "MORPH-477"))

    def test_ordinal_variants(self):
        self.assertEqual(
            self.rows("The thirty-threeth runner finished.", "MORPH-482")[0]["edit_hint"]["replacement"],
            "thirty-third",
        )
        self.assertFalse(self.rows("The twenty-fourth entry won.", "MORPH-482"))

    def test_fraction_variants(self):
        self.assertEqual(
            self.rows("They finished four fifth of the work.", "MORPH-483")[0]["edit_hint"]["replacement"],
            "fifths",
        )
        self.assertFalse(self.rows("They finished one third of the route.", "MORPH-483"))
        self.assertFalse(self.rows("They booked a three-quarter-hour lesson.", "MORPH-483"))


if __name__ == "__main__":
    unittest.main()
