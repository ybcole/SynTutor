import glob
import json
import unittest
from pathlib import Path

from cgel_word_order_probe import probe_word_order
from parse_engine import analyze


ROOT = Path(__file__).resolve().parents[1]
RULE_IDS = [
    "PHR-247", "PHR-381", "PHR-420", "PHR-769", "COMP-085", "COMP-202",
    "MORPH-056", "WCAT-046", "CLS-114", "CLS-128", "CLS-213", "CLS-217",
    "CLS-333", "COMP-063", "COMP-189",
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
        return probe_word_order(sentence, analyze(sentence)["root"])

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
        result = probe_word_order("We perused.", variety="other")
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["candidates"], [])


class EditTests(unittest.TestCase):
    def rows(self, sentence, rule_id):
        return [row for row in probe_word_order(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == rule_id]

    def test_such_a_reorders(self):
        sentence = "It was a such relief."
        rows = self.rows(sentence, "PHR-247")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "a such")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "such a")

    def test_before_that_deletes_that(self):
        sentence = "We packed before that the rain started."
        rows = self.rows(sentence, "PHR-381")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], " that")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "")

    def test_ago_reorders(self):
        sentence = "They left ago three weeks."
        rows = self.rows(sentence, "PHR-420")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "three weeks ago")

    def test_else_reorders(self):
        sentence = "If Rae can't help, ask else someone."
        rows = self.rows(sentence, "PHR-769")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "someone else")

    def test_particle_pronoun_reorders(self):
        sentence = "He brought in it."
        rows = self.rows(sentence, "COMP-085")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "brought it in")

    def test_explain_reorders(self):
        sentence = "I explained Mara the schedule."
        rows = self.rows(sentence, "COMP-202")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "explained the schedule to Mara")

    def test_infinitival_negative_reorders(self):
        sentence = "She asked me to don't leave."
        rows = self.rows(sentence, "MORPH-056")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "not to leave")

    def test_enough_reorders(self):
        sentence = "The room was enough warm."
        rows = self.rows(sentence, "WCAT-046")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "warm enough")

    def test_aux_inversion_reorders(self):
        sentence = "Where had been the documents kept?"
        rows = self.rows(sentence, "CLS-114")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "Where had the documents been kept")

    def test_fronted_question_reorders(self):
        sentence = "Where Mina did park?"
        rows = self.rows(sentence, "CLS-128")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "Where did Mina park")

    def test_how_come_reorders(self):
        sentence = "How come did Maya leave early?"
        rows = self.rows(sentence, "CLS-213")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "How come Maya left early?")

    def test_maximal_interrogative_reorders(self):
        sentence = "What size did you order boots?"
        rows = self.rows(sentence, "CLS-217")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "What size boots did you order?")

    def test_perfect_progressive_reorders(self):
        sentence = "She is having checked the seals."
        rows = self.rows(sentence, "CLS-333")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "She is having checked")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "She has been checking")

    def test_peruse_object(self):
        sentence = "Lena perused yesterday."
        rows = self.rows(sentence, "COMP-063")
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]["edit_hint"])
        self.assertTrue(self.rows(sentence, "COMP-189"))


class HeldOutTests(unittest.TestCase):
    def flagged(self, sentence, rule_id):
        return [row for row in probe_word_order(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == rule_id]

    def test_such_variants(self):
        self.assertTrue(self.flagged("A what mess that was!", "PHR-247"))
        self.assertFalse(self.flagged("It was such welcome news.", "PHR-247"))
        self.assertFalse(self.flagged("It was a further such delay.", "PHR-247"))

    def test_before_that_variants(self):
        self.assertTrue(self.flagged("We ate before that the guests arrived.", "PHR-381"))
        self.assertFalse(self.flagged("Before that, the guests had already eaten.", "PHR-381"))
        self.assertFalse(self.flagged("They can stay provided that the room is free.", "PHR-381"))

    def test_ago_variants(self):
        self.assertTrue(self.flagged("They moved ago two days.", "PHR-420"))
        self.assertFalse(self.flagged("They moved before the holidays.", "PHR-420"))

    def test_else_variants(self):
        self.assertTrue(self.flagged("Did you buy else anything?", "PHR-769"))
        self.assertFalse(self.flagged("Who else can help?", "PHR-769"))
        self.assertFalse(self.flagged("Ask for another key, or else call the caretaker.", "PHR-769"))

    def test_particle_variants(self):
        self.assertTrue(self.flagged("She picked up them.", "COMP-085"))
        self.assertFalse(self.flagged("She picked up the bags.", "COMP-085"))

    def test_explain_variants(self):
        self.assertTrue(self.flagged("They explained the visitors the policy.", "COMP-202"))
        self.assertFalse(self.flagged("She told Mara the schedule.", "COMP-202"))
        self.assertFalse(self.flagged("They gave the visitors a printed policy.", "COMP-202"))

    def test_infinitival_negative_variants(self):
        self.assertTrue(self.flagged("He wanted to do not interrupt the meeting.", "MORPH-056"))
        self.assertFalse(self.flagged("She asked me not to leave.", "MORPH-056"))
        self.assertFalse(self.flagged("Don't leave before dinner.", "MORPH-056"))

    def test_enough_variants(self):
        self.assertTrue(self.flagged("Jo spoke enough clearly.", "WCAT-046"))
        self.assertFalse(self.flagged("We brought enough blankets.", "WCAT-046"))
        self.assertFalse(self.flagged("There was time enough to finish.", "WCAT-046"))

    def test_aux_inversion_variants(self):
        self.assertTrue(self.flagged("Has been the parcel delivered?", "CLS-114"))
        self.assertFalse(self.flagged("Where had the documents been kept?", "CLS-114"))
        self.assertFalse(self.flagged("More important had been the remaining objections.", "CLS-114"))

    def test_fronted_question_variants(self):
        self.assertTrue(self.flagged("What Leon is carrying?", "CLS-128"))
        self.assertFalse(self.flagged("Who is carrying the bag?", "CLS-128"))
        self.assertFalse(self.flagged("I know where Mina parked.", "CLS-128"))

    def test_how_come_variants(self):
        self.assertTrue(self.flagged("How come is the gate locked?", "CLS-213"))
        self.assertFalse(self.flagged("How did it come to be locked?", "CLS-213"))
        self.assertFalse(self.flagged("How come Maya did leave early after all?", "CLS-213"))

    def test_maximal_interrogative_variants(self):
        self.assertTrue(self.flagged("How large did they build a crate?", "CLS-217"))
        self.assertFalse(self.flagged("What size did you order?", "CLS-217"))
        self.assertFalse(self.flagged("How large did they build it?", "CLS-217"))

    def test_perfect_progressive_variants(self):
        self.assertTrue(self.flagged("They are having inspected the roof.", "CLS-333"))
        self.assertFalse(self.flagged("They have inspected the roof.", "CLS-333"))
        self.assertFalse(self.flagged("She is having the seals checked.", "CLS-333"))

    def test_peruse_variants(self):
        self.assertTrue(self.flagged("She perused all afternoon.", "COMP-063"))
        self.assertFalse(self.flagged("She perused the papers carefully.", "COMP-063"))
        self.assertFalse(self.flagged("She read all afternoon.", "COMP-189"))


if __name__ == "__main__":
    unittest.main()
