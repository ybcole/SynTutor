"""Temporal adverbials: temporal NPs stay NPs (Ch5 p.88, p.93).

Terminal punctuation and the VP-within-VP adjunct layer are unchanged; only
the category of the temporal adjunct is at issue here.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import build_payload, model_status


def _models_ready():
    return bool(model_status().get('ready'))


def walk(node):
    yield node
    for child in node.get('children', []):
        yield from walk(child)


def words(node):
    out = []
    for item in walk(node):
        if item.get('word'):
            out.append(item['word'])
    return out


@unittest.skipUnless(_models_ready(), 'parser models not installed')
class TemporalAdjunctTest(unittest.TestCase):
    def projected(self, text):
        payload = build_payload(text)
        self.assertEqual(payload['summary'].get('verdict'), 'grammatical', text)
        self.assertEqual(payload['br_analysis'].get('status'), 'normalized', text)
        return payload['br_analysis']['tree']['root']

    def adjunct_vp(self, root):
        for node in walk(root):
            if node.get('label') != 'VP':
                continue
            kids = node.get('children', [])
            if kids and kids[0].get('label') == 'VP' and len(kids) > 1:
                return node
        self.fail('no VP-within-VP adjunct layer')

    def test_last_night_is_an_np_adjunct(self):
        root = self.projected('Max slept last night.')
        vp = self.adjunct_vp(root)
        temporal = [c for c in vp['children'][1:] if c.get('label') == 'NP']
        self.assertEqual(len(temporal), 1)
        self.assertEqual(words(temporal[0]), ['last', 'night'])
        self.assertFalse(any(n.get('label') == 'PP' for n in walk(root)))

    def test_every_day_is_an_np_adjunct(self):
        root = self.projected('She runs every day.')
        vp = self.adjunct_vp(root)
        temporal = [c for c in vp['children'][1:] if c.get('label') == 'NP']
        self.assertEqual(words(temporal[0]), ['every', 'day'])
        self.assertFalse(any(n.get('label') == 'PP' for n in walk(root)))

    def test_coordinated_temporal_nps_stay_np(self):
        root = self.projected('She runs every day and every night.')
        vp = self.adjunct_vp(root)
        temporal = [c for c in vp['children'][1:] if c.get('label') == 'NP']
        self.assertEqual(words(temporal[0]), ['every', 'day', 'and', 'every', 'night'])
        self.assertFalse(any(n.get('label') == 'PP' for n in walk(root)))

    def test_overt_temporal_pp_stays_pp(self):
        root = self.projected('They met in the morning.')
        vp = self.adjunct_vp(root)
        temporal = [c for c in vp['children'][1:] if c.get('label') == 'PP']
        self.assertEqual(len(temporal), 1)
        self.assertEqual(words(temporal[0]), ['in', 'the', 'morning'])

    def test_time_np_subject_is_not_made_an_adjunct(self):
        root = self.projected('The morning was cold.')
        for node in walk(root):
            if node.get('label') == 'VP':
                self.assertFalse(any(c.get('label') == 'VP' for c in node.get('children', [])))


if __name__ == '__main__':
    unittest.main()
