import unittest

from cgel_role_object_probe import probe_role_object
from parse_engine import NodeBuilder, parse_parse_string


class RoleObjectProbeTests(unittest.TestCase):
    def test_referential_object_and_controls(self):
        for phrase, tokens, vp, expected in [
            ("questioned treasurer", 4, "(VBD questioned) (NP (NN treasurer))", ["COMP-087"]),
            ("questioned the treasurer", 5, "(VBD questioned) (NP (DT the) (NN treasurer))", []),
            ("appointed her treasurer", 5, "(VBD appointed) (NP (PRP her)) (NP (NN treasurer))", []),
            ("contacted President Silva", 5, "(VBD contacted) (NP (NNP President) (NNP Silva))", []),
            ("interviewed directors", 4, "(VBD interviewed) (NP (NNS directors))", []),
        ]:
            with self.subTest(phrase=phrase):
                tree = NodeBuilder().build(parse_parse_string(f"(S (NP (PRP They)) (VP {vp}) (. .))"), tokens)
                result = probe_role_object(f"They {phrase}.", tree, variety="standard_english")
                self.assertEqual([row["rule_id"] for row in result["candidates"]], expected)
                for row in result["candidates"]:
                    self.assertIsNone(row["edit_hint"])
                    self.assertEqual(row["supporting_sources"][0]["rule_id"], "PHR-197")
