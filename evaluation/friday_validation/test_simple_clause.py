
import unittest
import test_tree_structure as helpers


EXPECTED_TREE = [
    "S",
    [
        "NP",
        ["DET", ["ART", "The"]],
        ["NOM", ["N", "boy"]],
    ],
    [
        "VP",
        ["V", "runs"],
    ],
]


def tree_shape(node):
    """Extract the ordered grammatical hierarchy."""
    if "word" in node:
        return node["word"]

    return [
        node["label"],
        *[tree_shape(child) for child in node.get("children", [])],
    ]


class TestSimpleClause(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = helpers.analyze("The boy runs.")
        cls.br = cls.data["br_analysis"]
        cls.root = cls.br["tree"]["root"]

    def test_normalization(self):
        self.assertEqual(self.br["status"], "normalized")

    def test_constituent_hierarchy(self):
        self.assertEqual(
            tree_shape(self.root),
            EXPECTED_TREE,
        )

    def test_verb_features(self):
        verb = self.root["children"][1]["children"][0]
        features = verb.get("features", [])

        self.assertIn("intrans", features)
        self.assertIn("pres", features)

    def test_token_alignment(self):
        tokens = [
            token["text"]
            for token in self.br["tree"]["tokens"]
        ]

        self.assertEqual(tokens, ["The", "boy", "runs"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
