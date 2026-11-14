import glob
import json
import unittest
from pathlib import Path

from cgel_pronoun_case_probe import probe_pronoun_case


ROOT = Path(__file__).resolve().parents[1]
RULE_IDS = ["PHR-289", "PHR-290", "PHR-295", "PHR-305", "PHR-321",
            "PHR-580", "PHR-582"]


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
        result = probe_pronoun_case(sentence)
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
        result = probe_pronoun_case("They thanked he.", variety="other")
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["candidates"], [])


class EditTests(unittest.TestCase):
    def rows(self, sentence, rule_id):
        return [row for row in probe_pronoun_case(sentence)["candidates"]
                if row["rule_id"] == rule_id]

    def test_object_pronoun(self):
        sentence = "They thanked he after the meeting."
        rows = self.rows(sentence, "PHR-289")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "he")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "him")

    def test_for_infinitival_pronoun(self):
        sentence = "For she to leave now would be awkward."
        rows = self.rows(sentence, "PHR-290")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "she")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "her")

    def test_who_subject(self):
        sentence = "Whom opened the gate?"
        rows = self.rows(sentence, "PHR-295")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "Whom")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "Who")

    def test_dependent_genitive(self):
        sentence = "Mine bag stayed dry."
        rows = self.rows(sentence, "PHR-305")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "Mine")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "My")

    def test_own_genitive(self):
        sentence = "I brought mine own."
        rows = self.rows(sentence, "PHR-321")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "mine")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "my")

    def test_emphatic_adjunct_reorders(self):
        sentence = "They sent Ava the invoice herself."
        rows = self.rows(sentence, "PHR-580")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "sent Ava herself the invoice")

    def test_genitive_reflexive_removes_s(self):
        sentence = "We objected to Clara's herself directing the ceremony."
        rows = self.rows(sentence, "PHR-582")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "Clara herself")


class HeldOutTests(unittest.TestCase):
    def flagged(self, sentence, rule_id):
        return [row for row in probe_pronoun_case(sentence)["candidates"]
                if row["rule_id"] == rule_id]

    def test_object_variants(self):
        self.assertTrue(self.flagged("She handed I the spare key.", "PHR-289"))
        self.assertFalse(self.flagged("He thanked them after the meeting.", "PHR-289"))
        self.assertFalse(self.flagged("It was I who handed her the spare key.", "PHR-289"))

    def test_for_variants(self):
        self.assertTrue(self.flagged("For they to finish today would be unusual.", "PHR-290"))
        self.assertFalse(self.flagged("She can leave now.", "PHR-290"))

    def test_who_variants(self):
        self.assertTrue(self.flagged("The guide whom led the tour has returned.", "PHR-295"))
        self.assertFalse(self.flagged("Whom did you call?", "PHR-295"))
        self.assertFalse(self.flagged(
            "The guide whom we thought would lead the tour has returned.", "PHR-295"))

    def test_genitive_variants(self):
        self.assertTrue(self.flagged("The blue bag is my.", "PHR-305"))
        self.assertFalse(self.flagged("My first stayed dry but my second got wet.", "PHR-305"))
        self.assertFalse(self.flagged("I brought mine.", "PHR-321"))

    def test_emphatic_variants(self):
        self.assertTrue(self.flagged("We handed Leo the receipt himself.", "PHR-580"))
        self.assertFalse(self.flagged("We handed Leo himself the receipt.", "PHR-580"))
        self.assertFalse(self.flagged(
            "Having booked the venue herself, Ava sent us the address.", "PHR-580"))

    def test_genitive_reflexive_variants(self):
        self.assertTrue(self.flagged("The captain herself's niece called.", "PHR-582"))
        self.assertFalse(self.flagged(
            "We objected to Clara's directing the ceremony herself.", "PHR-582"))
        self.assertFalse(self.flagged("I spoke to the captain herself.", "PHR-582"))


if __name__ == "__main__":
    unittest.main()
