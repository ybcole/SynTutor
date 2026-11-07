"""Audit IMG-marked B-R sources without treating image evidence as automatic gold status.

The IMG flag means the tree was transcribed/checked against an image. It does
not by itself mean the record is a canonical, error-free, runtime-grade tree.
This audit checks that accepted records validate and that rejected records are
reported explicitly rather than silently converted.
"""
import unittest

from br_tree import _atoms, _source_yield, load_reference_records, normalize_candidate, validate_tree


class BurtonRobertsFixtureTests(unittest.TestCase):
    def test_sentence_aligned_img_records_are_validated_or_explicitly_rejected(self):
        records = load_reference_records()
        aligned = []
        accepted = []
        rejected = []
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
            aligned.append(record)
            result = normalize_candidate(
                {}, None, sentence, version, [record],
                appendix_nom=bool(record.get("appendix_nom", False)))
            if result.get("status") == "normalized":
                errors = validate_tree(result["tree"], version, _atoms(sentence))
                self.assertEqual(errors, [], f"{record.get('id')} returned an invalid normalized tree")
                accepted.append(record.get("id"))
            else:
                rejected.append({
                    "tree_id": record.get("id"),
                    "version": version,
                    "diagnostics": result.get("diagnostics"),
                })

        self.assertGreater(len(aligned), 0, "No sentence-aligned IMG records were found.")
        self.assertGreater(len(accepted), 0, "No IMG source fixtures passed canonical validation.")
        self.assertEqual(len(accepted) + len(rejected), len(aligned))
        self.assertTrue(
            all(row["diagnostics"] and row["diagnostics"][0].get("code")
                for row in rejected),
            "Every rejected source record must expose a diagnostic code.",
        )
        print(
            "B-R IMG source audit: "
            f"{len(aligned)} sentence-aligned records; "
            f"{len(accepted)} normalized and validated; "
            f"{len(rejected)} explicitly unresolved."
        )
        if rejected:
            print("Explicitly unresolved source records:")
            for row in rejected:
                diagnostic = row["diagnostics"][0]
                details = diagnostic.get("rejected_references") or []
                detail_text = "; ".join(
                    f"{item.get('tree_id')}: {item.get('message')}"
                    for item in details
                )
                print(f"  {row['tree_id']} ({row['version']}): "
                      f"{diagnostic.get('code')} — {diagnostic.get('message')} "
                      f"{detail_text}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
