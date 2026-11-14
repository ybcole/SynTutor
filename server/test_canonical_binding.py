import unittest

from canonical_binding import bind_details_to_canonical


TREE = {
    "root": {
        "id": "s-root",
        "label": "S",
        "token_span": [0, 3],
        "children": [
            {
                "id": "np-subject",
                "label": "NP",
                "token_span": [0, 1],
                "children": [
                    {"id": "n-boys", "label": "N", "token_span": [0, 1],
                     "children": [{"id": "w-boys", "word": "boys", "token_span": [0, 1]}]},
                ],
            },
            {
                "id": "vp-predicate",
                "label": "VP",
                "token_span": [1, 3],
                "children": [
                    {"id": "v-reads", "label": "V", "token_span": [1, 2],
                     "children": [{"id": "w-reads", "word": "reads", "token_span": [1, 2]}]},
                    {"id": "np-object", "label": "NP", "token_span": [2, 3],
                     "children": [{"id": "w-book", "word": "book", "token_span": [2, 3]}]},
                ],
            },
        ],
    }
}


class CanonicalBindingTests(unittest.TestCase):
    def test_remediation_target_maps_to_exact_word(self):
        details = {
            "n4": {
                "status": "error",
                "span": [1, 3],
                "remediation": {
                    "edit": {"start": 1, "end": 2, "text": "read"},
                    "edits": [{"node": "n5", "replacement": "read"}],
                },
            }
        }
        summary = bind_details_to_canonical(TREE, details)
        self.assertEqual(summary["mapped"], 1)
        self.assertEqual(details["n4"]["canonical_node_id"], "w-reads")
        self.assertEqual(details["n4"]["canonical_binding"]["label"], "V")
        self.assertEqual(details["n4"]["canonical_node_ids"], ["w-reads"])

    def test_non_error_detail_maps_by_span(self):
        details = {"n1": {"status": "valid", "span": [2, 3]}}
        bind_details_to_canonical(TREE, details)
        self.assertIsNotNone(details["n1"]["canonical_node_id"])
        self.assertEqual(details["n1"]["canonical_binding"]["status"], "mapped")

    def test_missing_span_is_unmapped(self):
        details = {"n9": {"status": "error", "span": None}}
        summary = bind_details_to_canonical(TREE, details)
        self.assertEqual(summary["unmapped"], 1)
        self.assertIsNone(details["n9"]["canonical_node_id"])
        self.assertEqual(details["n9"]["canonical_binding"]["status"], "unmapped")

    def test_unavailable_tree(self):
        summary = bind_details_to_canonical(None, {"n1": {"status": "error"}})
        self.assertEqual(summary["status"], "unavailable")


if __name__ == "__main__":
    unittest.main()
