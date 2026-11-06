"""Audit IMG-marked B-R source trees that have a transcribed sentence."""
import unittest
from br_tree import _atoms, _source_yield, load_reference_records, normalize_candidate


class BurtonRobertsFixtureTests(unittest.TestCase):
    def test_sentence_aligned_img_fixtures_normalize(self):
        records = load_reference_records()
        eligible = []
        failures = []
        for record in records:
            if record.get("status") != "IMG" or record.get("correct") is False:
                continue
            sentence = record.get("sentence")
            version = record.get("_convention_version")
            tree = record.get("tree")
            if not isinstance(sentence, str) or not version or not isinstance(tree, dict):
                continue
            if _source_yield(tree) != _atoms(sentence):
                continue
            eligible.append(record)
            result = normalize_candidate({}, None, sentence, version, [record])
            if result.get("status") != "normalized":
                failures.append({
                    "tree_id": record.get("id"),
                    "version": version,
                    "diagnostics": result.get("diagnostics"),
                })
        self.assertGreater(len(eligible), 0, "No eligible IMG fixtures were found.")
        self.assertEqual(failures, [], f"IMG fixtures failed canonical validation: {failures[:12]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
