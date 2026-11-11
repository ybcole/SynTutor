
import json
import os
import unittest
from urllib.request import Request, urlopen

API_URL = os.environ.get(
    "SYNTUTOR_QA_API_URL",
    "http://127.0.0.1:8001/api/parse",
)

def analyze(sentence):
    request = Request(
        API_URL,
        data=json.dumps({"text": sentence}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=30) as response:
        return json.load(response)


def simplify_tree(node):
    """Keep linguistic structure, not generated IDs or citations."""
    if "word" in node:
        return node["word"]

    return {
        "label": node["label"],
        "features": node.get("features", []),
        "children": [
            simplify_tree(child)
            for child in node.get("children", [])
        ],
    }


EXPECTED_MODAL_TREE = {
    "label": "S",
    "features": [],
    "children": [
        {
            "label": "NP",
            "features": [],
            "children": [
                {
                    "label": "pronoun",
                    "features": [],
                    "children": ["She"],
                }
            ],
        },
        {
            "label": "VP",
            "features": [],
            "children": [
                {
                    "label": "MOD",
                    "features": ["pres"],
                    "children": ["can"],
                },
                {
                    "label": "VP",
                    "features": [],
                    "children": [
                        {
                            "label": "V",
                            "features": ["intrans"],
                            "children": ["sing"],
                        }
                    ],
                },
            ],
        },
    ],
}


class TestModalStructure(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = analyze("She can sing.")
        cls.br = cls.data["br_analysis"]

    def test_canonical_status(self):
        self.assertEqual(
            self.br["status"],
            "normalized",
        )

    def test_burton_roberts_hierarchy(self):
        actual = simplify_tree(self.br["tree"]["root"])

        self.assertEqual(
            actual,
            EXPECTED_MODAL_TREE,
        )

    def test_token_alignment(self):
        actual_tokens = [
            token["text"]
            for token in self.br["tree"]["tokens"]
        ]

        self.assertEqual(
            actual_tokens,
            ["She", "can", "sing"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
