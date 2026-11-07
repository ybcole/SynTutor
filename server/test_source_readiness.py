"""Starter teaching evidence and executable constraint coverage are separate gates."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

path = Path(__file__).resolve().parents[1] / 'scripts/audit_source_readiness.py'
spec = importlib.util.spec_from_file_location('source_readiness_audit', path)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class SourceReadinessTests(unittest.TestCase):
    def test_real_sources_allow_m4_without_inventing_constraint_coverage(self):
        result = audit.readiness()
        self.assertTrue(result['milestone_04_content_ready'])
        self.assertEqual(result['reviewed_structural_template_count'], 1)
        self.assertEqual(result['reviewed_cambridge_template_count'], 1)
        self.assertFalse(result['runtime_constraint_coverage_ready'])
        self.assertEqual(result['runtime_enabled_rule_count'], 0)

    def test_missing_or_unreviewed_templates_block_content_readiness(self):
        original = audit.load_registry()
        for book in ['B-R', 'Cambridge']:
            data = {**original, 'sources': [dict(source) for source in original['sources']]}
            for source in data['sources']:
                if source['book'] == book: source['independent_review'] = False
            with patch.object(audit, 'load_registry', return_value=data):
                self.assertFalse(audit.readiness()['milestone_04_content_ready'])
        with patch.object(audit, 'load_registry', return_value={'sources': [], 'templates': []}):
            self.assertFalse(audit.readiness()['milestone_04_content_ready'])
