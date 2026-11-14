import glob
import json
import unittest
from pathlib import Path

from cgel_usage_probe import probe_usage
from parse_engine import analyze


ROOT = Path(__file__).resolve().parents[1]
RULE_IDS = [
    "PHR-083", "PHR-110", "PHR-240", "OTH-615", "COMP-041", "MORPH-114",
    "MORPH-130", "MORPH-391", "MORPH-480", "MORPH-481", "CLS-120",
    "CLS-1159", "CLS-1188", "CLS-1239", "CLS-1415", "CLS-1425", "CLS-1325",
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
        return probe_usage(sentence, analyze(sentence)["root"])

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
        result = probe_usage("We perused.", variety="other")
        self.assertEqual(result["status"], "not_evaluated")
        self.assertEqual(result["candidates"], [])


class EditTests(unittest.TestCase):
    def rows(self, sentence, rule_id):
        return [row for row in probe_usage(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == rule_id]

    def test_of_inserted_after_approximate_number(self):
        sentence = "Dozens lanterns lit the route."
        rows = self.rows(sentence, "PHR-083")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(span[0], sentence.index("lanterns"))
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "of ")

    def test_more_than_one_singularizes_head(self):
        sentence = "More than one panels was damaged."
        rows = self.rows(sentence, "PHR-240")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "panels")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "panel")

    def test_coordinated_contraction_expands(self):
        sentence = "I wonder if she and we're ready."
        rows = self.rows(sentence, "OTH-615")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "we're")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "we are")

    def test_have_got_question_reorders(self):
        sentence = "Do they have got the documents?"
        rows = self.rows(sentence, "COMP-041")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "Do they have got")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "Have they got")

    def test_sung_becomes_sang(self):
        sentence = "She sung the opening verse."
        rows = self.rows(sentence, "MORPH-114")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "sung")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "sang")

    def test_i_arent_expands(self):
        sentence = "I aren't on the list."
        rows = self.rows(sentence, "MORPH-130")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "I aren't")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "I am not")

    def test_new_zealand_predicate(self):
        sentence = "Her cousins are New Zealand."
        rows = self.rows(sentence, "MORPH-391")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "New Zealand")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "New Zealanders")

    def test_ten_hundred_becomes_thousand(self):
        sentence = "The archive received ten hundred letters."
        rows = self.rows(sentence, "MORPH-480")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "ten hundred")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "one thousand")

    def test_a_in_composite_numeral(self):
        sentence = "They paid two thousand a hundred and fifteen pounds."
        rows = self.rows(sentence, "MORPH-481")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "a")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "one")

    def test_used_to_ellipsis(self):
        sentence = "Kai used to cycle, and Isla used too."
        rows = self.rows(sentence, "CLS-120")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "used too")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "did too")

    def test_fewer_mass_becomes_less(self):
        sentence = "We need fewer equipment than they do."
        rows = self.rows(sentence, "CLS-1159")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "fewer")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "less")

    def test_a_same_becomes_the_same(self):
        sentence = "They made a same mistake."
        rows = self.rows(sentence, "CLS-1188")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "a same")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "the same")

    def test_as_like_predicate(self):
        sentence = "Nina is as her aunt in temperament."
        rows = self.rows(sentence, "CLS-1239")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "as")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "like")

    def test_cleft_it_inserts_be(self):
        sentence = "I consider it Maya who should speak first."
        rows = self.rows(sentence, "CLS-1415")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(span[0], sentence.index("Maya"))
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "to be ")

    def test_bare_who_pseudocleft(self):
        sentence = "Who found the key was Lena."
        rows = self.rows(sentence, "CLS-1425")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "Who ")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "The one who ")

    def test_particle_pronoun_reorders(self):
        sentence = "She brought back them."
        rows = self.rows(sentence, "CLS-1325")
        self.assertEqual(len(rows), 1)
        span = rows[0]["edit_hint"]["char_span"]
        self.assertEqual(sentence[span[0]:span[1]], "brought back them")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "brought them back")


class HeldOutTests(unittest.TestCase):
    def flagged(self, sentence, rule_id):
        return [row for row in probe_usage(sentence, analyze(sentence)["root"])["candidates"]
                if row["rule_id"] == rule_id]

    def test_approximate_number_variants(self):
        self.assertTrue(self.flagged("Hundreds tickets were sold.", "PHR-083"))
        self.assertFalse(self.flagged("A dozen lanterns lit the route.", "PHR-083"))
        self.assertFalse(self.flagged("Four hundred tickets were sold.", "PHR-083"))

    def test_both_variants(self):
        self.assertTrue(self.flagged("Both Maren, Jo, and Sam signed.", "PHR-110"))
        self.assertFalse(self.flagged("Both Maren and the team of Jo and Sam signed.", "PHR-110"))

    def test_one_more_variants(self):
        rows = self.flagged("One more parcels has arrived.", "PHR-240")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "parcel")
        self.assertFalse(self.flagged("One or more parcels have arrived.", "PHR-240"))

    def test_have_got_variants(self):
        rows = self.flagged("She doesn't have got the right key.", "COMP-041")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "She hasn't got")
        self.assertFalse(self.flagged("Do they have the documents?", "COMP-041"))

    def test_sung_sang_variants(self):
        rows = self.flagged("She has sang that verse before.", "MORPH-114")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "sung")
        self.assertFalse(self.flagged("She has sung that verse before.", "MORPH-114"))

    def test_new_zealand_variants(self):
        rows = self.flagged("The new curator is New Zealand.", "MORPH-391")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "from New Zealand")
        self.assertFalse(self.flagged("The winning team is New Zealand.", "MORPH-391"))
        self.assertFalse(self.flagged("The curator is from New Zealand.", "MORPH-391"))
        self.assertFalse(self.flagged("Our next destination is New Zealand.", "MORPH-391"))

    def test_hundred_variants(self):
        self.assertTrue(self.flagged("The farmer sold sixty hundred and twelve seedlings.", "MORPH-480"))
        self.assertFalse(self.flagged("They saved nineteen hundred dollars.", "MORPH-480"))
        self.assertFalse(self.flagged("The shop sold sixty-one hundred tickets.", "MORPH-480"))

    def test_composite_numeral_variants(self):
        self.assertTrue(self.flagged("They saved three thousand a hundred pounds.", "MORPH-481"))
        self.assertFalse(self.flagged("They paid a hundred pounds.", "MORPH-481"))

    def test_used_ellipsis_variants(self):
        rows = self.flagged("Lena used to sing, and Omar used as well.", "CLS-120")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "used to as well")
        self.assertFalse(self.flagged("Kai used to cycle, and Isla did too.", "CLS-120"))
        self.assertFalse(self.flagged("Kai used a map, and Isla used one too.", "CLS-120"))

    def test_fewer_variants(self):
        self.assertTrue(self.flagged("The recipe uses fewer flour than mine.", "CLS-1159"))
        self.assertFalse(self.flagged("We need fewer tools than they do.", "CLS-1159"))
        self.assertFalse(self.flagged("She arrived less than ten minutes ago.", "CLS-1159"))

    def test_same_variants(self):
        self.assertTrue(self.flagged("They chose a same route.", "CLS-1188"))
        self.assertFalse(self.flagged("They chose this same route.", "CLS-1188"))
        self.assertFalse(self.flagged("They made an identical mistake.", "CLS-1188"))

    def test_as_like_variants(self):
        self.assertTrue(self.flagged("As Lena, I prefer the earlier train.", "CLS-1239"))
        self.assertFalse(self.flagged("I signed the form as the project manager.", "CLS-1239"))
        self.assertFalse(self.flagged("As our neighbors do, we support the proposal.", "CLS-1239"))

    def test_cleft_variants(self):
        self.assertTrue(self.flagged("I believe it the latch that is stuck.", "CLS-1415"))
        self.assertFalse(self.flagged("I find it surprising that Maya spoke first.", "CLS-1415"))
        self.assertFalse(self.flagged("It seems to be Maya who should speak first.", "CLS-1415"))

    def test_bare_who_variants(self):
        self.assertTrue(self.flagged("Who designed the bridge was Jo.", "CLS-1425"))
        self.assertFalse(self.flagged("Who found the key is still unclear.", "CLS-1425"))
        self.assertFalse(self.flagged("It was Jo who designed the bridge.", "CLS-1425"))

    def test_particle_variants(self):
        rows = self.flagged("He put away it.", "CLS-1325")
        self.assertEqual(rows[0]["edit_hint"]["replacement"], "put it away")
        self.assertFalse(self.flagged("She brought back the boxes.", "CLS-1325"))
        self.assertFalse(self.flagged("He looked after them.", "CLS-1325"))
        self.assertFalse(self.flagged("She stood with her hands in her pockets.", "CLS-1325"))


if __name__ == "__main__":
    unittest.main()
