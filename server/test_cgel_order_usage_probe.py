import glob
import json
import unittest
from pathlib import Path

from cgel_order_usage_probe import probe_order_usage


ROOT = Path(__file__).resolve().parents[1]
RULE_IDS = [
    "CLS-1166", "CLS-1197", "CLS-1218", "CLS-1479", "CLS-1379",
    "CLS-108", "CLS-117", "CLS-156", "CLS-286", "PHR-748", "COMP-138",
    "COMP-033", "COMP-040",
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
        result = probe_order_usage(sentence)
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
        result = probe_order_usage("She had could be invited.", variety="other")
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["candidates"], [])


class EditTests(unittest.TestCase):
    def rows(self, sentence, rule_id):
        return [row for row in probe_order_usage(sentence)["candidates"]
                if row["rule_id"] == rule_id]

    def test_superior_than(self):
        sentence = "This fabric is superior than the original."
        rows = self.rows(sentence, "CLS-1166")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "superior than")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "superior to")

    def test_similar_as(self):
        sentence = "This fabric is similar as the green one."
        rows = self.rows(sentence, "CLS-1197")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "similar to")

    def test_other_than_inserts_what(self):
        sentence = "We received no payments other than the agency sent."
        rows = self.rows(sentence, "CLS-1218")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "what ")

    def test_got_seen(self):
        sentence = "Mina got seen to leave the hall."
        rows = self.rows(sentence, "CLS-1479")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "got")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "was")

    def test_infinitival_subject_inversion(self):
        sentence = "Would to close the valve help?"
        rows = self.rows(sentence, "CLS-1379")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "Would it help to close the valve?")

    def test_fronted_so(self):
        sentence = "So little time we had that we rushed."
        rows = self.rows(sentence, "CLS-108")
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["edit_hint"]["replacement"].startswith(
            "So little time did we have"))

    def test_adverb_placement(self):
        sentence = "She visits always the museum."
        rows = self.rows(sentence, "CLS-117")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "always visits")

    def test_single_fronting(self):
        sentence = "What to whom did she hand?"
        rows = self.rows(sentence, "CLS-156")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "What did she hand to whom?")

    def test_for_subject_order(self):
        sentence = "It is essential for the pressure you to check first."
        rows = self.rows(sentence, "CLS-286")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "for you to check the pressure")

    def test_fragment_stranding(self):
        sentence = "We're staying overnight. Which cabin in?"
        rows = self.rows(sentence, "PHR-748")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "In which cabin?")

    def test_direction_adverb(self):
        sentence = "The attendant brought downstairs the chair."
        rows = self.rows(sentence, "COMP-138")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "brought the chair downstairs")

    def test_aux_order(self):
        sentence = "She had could be invited."
        rows = self.rows(sentence, "COMP-033")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "could have been invited")

    def test_dynamic_have(self):
        sentence = "Had they a quiet lunch?"
        rows = self.rows(sentence, "COMP-040")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["edit_hint"]["replacement"],
                         "Did they have a quiet lunch?")


class HeldOutTests(unittest.TestCase):
    def flagged(self, sentence, rule_id):
        return [row for row in probe_order_usage(sentence)["candidates"]
                if row["rule_id"] == rule_id]

    def test_superior_variants(self):
        self.assertTrue(self.flagged("The older camera is inferior than this one.", "CLS-1166"))
        self.assertFalse(self.flagged("This fabric is better than the original.", "CLS-1166"))
        self.assertFalse(self.flagged("This is a very inferior design.", "CLS-1166"))

    def test_similar_variants(self):
        self.assertTrue(self.flagged("The two instruments are similar as those on the shelf.", "CLS-1197"))
        self.assertFalse(self.flagged("The two instruments are similar, as you can see.", "CLS-1197"))
        self.assertFalse(self.flagged("We chose the same fabric as the costume designer.", "CLS-1197"))

    def test_other_than_variants(self):
        self.assertTrue(self.flagged("He had no support other than his neighbors offered.", "CLS-1218"))
        self.assertFalse(self.flagged("The outcome was other than we expected.", "CLS-1218"))
        self.assertFalse(self.flagged("Nothing changed other than that the fee doubled.", "CLS-1218"))

    def test_got_seen_variants(self):
        self.assertTrue(self.flagged("Two visitors got seen to enter the garden.", "CLS-1479"))
        self.assertFalse(self.flagged("We saw Mina get knocked down.", "CLS-1479"))

    def test_inversion_variants(self):
        self.assertTrue(self.flagged("Is that the valve failed surprising?", "CLS-1379"))
        self.assertFalse(self.flagged("Would an inspection help?", "CLS-1379"))
        self.assertFalse(self.flagged("Will replacing the seal take all morning?", "CLS-1379"))

    def test_fronted_variants(self):
        self.assertTrue(self.flagged(
            "Such a commotion the crowd caused that traffic stopped.", "CLS-108"))
        self.assertFalse(self.flagged("So little time remained that we rushed.", "CLS-108"))
        self.assertFalse(self.flagged("So tired, he fell asleep at once.", "CLS-108"))

    def test_adverb_variants(self):
        self.assertTrue(self.flagged("They travel probably by rail.", "CLS-117"))
        self.assertFalse(self.flagged("She is always optimistic.", "CLS-117"))
        self.assertFalse(self.flagged("They have probably travelled by rail.", "CLS-117"))
        self.assertFalse(self.flagged("She visits, always, the same museum.", "CLS-117"))

    def test_fronting_variants(self):
        self.assertTrue(self.flagged("Where which boxes did they store?", "CLS-156"))
        self.assertFalse(self.flagged("When and where will they meet?", "CLS-156"))
        self.assertFalse(self.flagged("She handed what to whom?", "CLS-156"))

    def test_for_order_variants(self):
        self.assertTrue(self.flagged(
            "It is essential for the seal them to test next.", "CLS-286"))
        self.assertFalse(self.flagged(
            "It is essential for both of you to check the pressure.", "CLS-286"))
        self.assertFalse(self.flagged(
            "It is essential for you to first check the pressure.", "CLS-286"))

    def test_fragment_variants(self):
        self.assertTrue(self.flagged("I left it on a shelf. Which shelf on?", "PHR-748"))
        self.assertFalse(self.flagged("Which cabin are we staying in?", "PHR-748"))
        self.assertFalse(self.flagged("I spoke to someone. Who to?", "PHR-748"))

    def test_direction_variants(self):
        self.assertTrue(self.flagged("The driver carried downstairs the boxes.", "COMP-138"))
        self.assertFalse(self.flagged("She carried down the boxes.", "COMP-138"))
        self.assertFalse(self.flagged(
            "She brought downstairs the enormous chair that her relatives had sent.", "COMP-138"))

    def test_aux_variants(self):
        self.assertTrue(self.flagged("The street is having been repaired.", "COMP-033"))
        self.assertFalse(self.flagged("She is having lunch.", "COMP-033"))
        self.assertFalse(self.flagged("They have been eating dinner.", "COMP-033"))

    def test_dynamic_have_variants(self):
        self.assertTrue(self.flagged("She hadn't the curtains cleaned.", "COMP-040"))
        self.assertFalse(self.flagged("Have they already eaten?", "COMP-040"))
        self.assertFalse(self.flagged("She hasn't had lunch yet.", "COMP-040"))


if __name__ == "__main__":
    unittest.main()
