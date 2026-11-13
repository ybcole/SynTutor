import os
import re
import unittest

from cgel_remote_conditional_probe import probe_remote_conditional
from parse_engine import NodeBuilder, analyze, parse_parse_string


class RemoteConditionalTests(unittest.TestCase):
    def check_case(self, sentence, tree, remote, expected):
        result = probe_remote_conditional(sentence, tree, variety="standard_english", remote_confirmed=remote)
        self.assertFalse(result["production_enabled"])
        self.assertEqual([row["rule_id"] for row in result["candidates"]], ["CLS-119"] if expected else [])
        for row in result["candidates"]:
            self.assertIsNone(row["edit_hint"])

    def test_remote_context_is_required(self):
        sentence = "If she arrived tomorrow, she joined us."
        parse = ("(S (SBAR (IN If) (S (NP (PRP she)) (VP (VBD arrived) (NP (NN tomorrow))))) "
                 "(, ,) (NP (PRP she)) (VP (VBD joined) (NP (PRP us))) (. .))")
        tree = NodeBuilder().build(parse_parse_string(parse), len(re.findall(r"\([^()]+\)", parse)))
        for remote in (True, False):
            with self.subTest(remote=remote):
                self.check_case(sentence, tree, remote, remote)

    @unittest.skipUnless(os.environ.get("CGEL_REQUIRE_PARSER") == "1", "configured parser required")
    def test_configured_remote_conditionals(self):
        for sentence, remote, expected in [
            ("If she arrived tomorrow, she joined us.", True, True),
            ("If we visited the archive tomorrow, we collected the copies.", True, True),
            ("If she arrived tomorrow, she joined us.", False, False),
            ("If she arrived tomorrow, she would join us.", True, False),
            ("If we visited the archive tomorrow, we could collect the copies.", True, False),
            ("If she arrived yesterday, she joined the morning group.", False, False),
            ("If she arrives tomorrow, she will join us.", False, False),
        ]:
            with self.subTest(sentence=sentence, remote=remote):
                self.check_case(sentence, analyze(sentence)["root"], remote, expected)
