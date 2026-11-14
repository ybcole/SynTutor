import glob
import json
import unittest
from pathlib import Path

from cgel_verb_form_probe import probe_verb_form
from parse_engine import analyze


ROOT = Path(__file__).resolve().parents[1]
RULE_IDS = ["MORPH-025", "MORPH-035", "COMP-042", "COMP-061", "COMP-116",
            "COMP-194", "WCAT-059"]


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
        return probe_verb_form(sentence, analyze(sentence)["root"])

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
        result = probe_verb_form("The door tends sticking.", variety="other")
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["candidates"], [])


class EditTests(unittest.TestCase):
    def rows(self, sentence, rule_id):
        return [row for row in probe_verb_form(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == rule_id]

    def test_had_better_deletes_to(self):
        sentence = "You had better to call the adviser."
        rows = self.rows(sentence, "COMP-042")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "to ")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "")

    def test_tend_gerund_becomes_to_infinitive(self):
        sentence = "The door tends sticking."
        rows = self.rows(sentence, "COMP-061")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "sticking")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "to stick")

    def test_do_pseudocleft_repairs_aspect(self):
        sentence = "What Leo did was repairing the radio."
        rows = self.rows(sentence, "COMP-116")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "repairing")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "repair")

    def test_bare_participle_becomes_preterite(self):
        sentence = "She broken the glass."
        rows = self.rows(sentence, "MORPH-025")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "broken")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "broke")

    def test_degree_adverb_repair(self):
        sentence = "They are very watering the seedlings."
        rows = self.rows(sentence, "MORPH-035")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "very")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "carefully")

    def test_too_participle_repair(self):
        sentence = "The seedlings were too watered by the gardener."
        rows = self.rows(sentence, "MORPH-035")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "too watered")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "watered thoroughly")

    def test_accustomed_to_gerund(self):
        sentence = "Jo is accustomed to work late."
        rows = self.rows(sentence, "WCAT-059")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "work")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "working")


class HeldOutTests(unittest.TestCase):
    def flagged(self, sentence, rule_id):
        return [row for row in probe_verb_form(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == rule_id]

    def test_had_better_variants(self):
        self.assertTrue(self.flagged("They had best to leave before sunset.", "COMP-042"))
        self.assertFalse(self.flagged("You better call the adviser.", "COMP-042"))
        self.assertFalse(self.flagged("The new method had better results.", "COMP-042"))

    def test_tend_variants(self):
        self.assertTrue(self.flagged("The students tend arriving early.", "COMP-061"))
        self.assertFalse(self.flagged("They tend to arrive late.", "COMP-061"))
        self.assertFalse(self.flagged("We tend the garden.", "COMP-061"))

    def test_pseudocleft_variants(self):
        rows = self.flagged("What Leo was doing was repair the radio.", "COMP-116")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "repairing")
        self.assertFalse(self.flagged("What he did was to rewrite the report.", "COMP-116"))

    def test_inchoative_variants(self):
        self.assertTrue(self.flagged("The shed constructed last week.", "COMP-194"))
        self.assertFalse(self.flagged("The window broke yesterday.", "COMP-194"))
        self.assertFalse(self.flagged("The warehouse was destroyed overnight.", "COMP-194"))
        self.assertFalse(self.flagged("The demolition team destroyed the warehouse.", "COMP-194"))

    def test_bare_participle_variants(self):
        rows = self.flagged("They chosen the last option.", "MORPH-025")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "chose")
        self.assertFalse(self.flagged("She has broken the glass.", "MORPH-025"))
        self.assertFalse(self.flagged("The last option was chosen.", "MORPH-025"))

    def test_degree_participle_variants(self):
        self.assertFalse(self.flagged(
            "The children were too frightened by the noise to speak.", "MORPH-035"))
        self.assertFalse(self.flagged("The movie was very entertaining.", "MORPH-035"))
        self.assertFalse(self.flagged("The gardener was very tired.", "MORPH-035"))

    def test_accustomed_variants(self):
        rows = self.flagged("Mina is accustomed to take the early train.", "WCAT-059")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "taking")
        self.assertFalse(self.flagged("She was accustomed to the noise.", "WCAT-059"))
        self.assertFalse(self.flagged("He is eager to work late.", "WCAT-059"))
        self.assertFalse(self.flagged(
            "They are accustomed to work that requires patience.", "WCAT-059"))


if __name__ == "__main__":
    unittest.main()
