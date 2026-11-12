"""Source gates and sentence/node evidence tests; all sources here are synthetic."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator
from burton_roberts import normalize_benepar_candidate, convention_profile
from explanations import explain_analysis, explain_request, load_registry
import test_cambridge_evaluator

ROOT = Path(__file__).resolve().parents[1]


def analysis():
    sentence = 'The birds sing'
    words = sentence.split()
    offset = 0
    tokens = []
    for index, word in enumerate(words):
        tokens.append({'i': index, 't': word, 'start': offset, 'end': offset + len(word), 'pos': 'NOUN', 'tag': 'NN'})
        offset += len(word) + 1
    return normalize_benepar_candidate({
        'sentence': sentence, 'tokens': tokens,
        'root': {'type': 'S', 'children': [
            {'type': 'NP', 'children': [{'type': 'DT', 'surface': 'The'}, {'type': 'NNS', 'surface': 'birds'}]},
            {'type': 'VP', 'children': [{'type': 'VBP', 'surface': 'sing'}]},
        ]}}, convention_profile(2))


def registry():
    review = {'review_status': 'INDEPENDENTLY_REVIEWED', 'independent_review': True,
              'reviewed_by': 'synthetic-test-reviewer', 'reviewed_on': '2026-11-07'}
    source = {'id': 'test-br', 'book': 'B-R', 'title': 'Synthetic test source',
              'edition': 'test-only', 'printed_page': 1, 'evidence_status': 'IMG',
              'status': 'approved', 'crosswalk_status': 'compatible', **review}
    template = {'id': 'test-s', 'channel': 'structural', 'node_label': 'S',
                'source_ids': ['test-br'], 'text': 'Test structure: {label} spans {surface}.',
                'deep_text': 'Test node {node_id} in {sentence}.', **review}
    return {'version': '1.0.0', 'sources': [source], 'templates': [template]}


class ExplanationEvidenceTests(unittest.TestCase):
    def test_structural_template_requires_its_specific_child_shape(self):
        data = registry()
        data['templates'][0]['node_children_labels'] = ['NP', 'VP']
        self.assertEqual(explain_analysis(analysis(), registry=data)['status'], 'EXPLAINED')
        data['templates'][0]['node_children_labels'] = ['VP', 'NP']
        self.assertEqual(explain_analysis(analysis(), registry=data)['status'], 'NO_BOOK_BASIS')

    def test_reviewed_structural_template_is_node_specific_and_cited(self):
        result = explain_analysis(analysis(), registry=registry())
        self.assertEqual(result['status'], 'EXPLAINED')
        item = result['channels']['structural'][0]
        self.assertIn('The birds sing', item['text'])
        self.assertEqual(item['sources'][0]['printed_page'], 1)
        self.assertEqual(result['channels']['grammatical'], [])
        self.assertEqual(result['channels']['remediation'], [])

    def test_evidence_and_registry_schema(self):
        for name in ['explanation_templates', 'explanation_evidence']:
            schema = json.loads((ROOT / f'grammar/{name}.schema.json').read_text())
            Draft202012Validator.check_schema(schema)
            document = registry() if name.endswith('templates') else explain_analysis(analysis(), registry=registry())
            Draft202012Validator(schema).validate(document)

    def test_missing_sources_fail_closed(self):
        data = registry(); data['sources'] = []
        self.assertEqual(explain_analysis(analysis(), registry=data)['status'], 'NO_BOOK_BASIS')

    def test_source_review_edition_page_crosswalk_gates_are_independent(self):
        for field, value in [('review_status', 'NOT_REVIEWED'), ('independent_review', False),
                             ('reviewed_by', ''), ('reviewed_on', ''), ('edition', ''),
                             ('printed_page', 0), ('printed_page', True),
                             ('crosswalk_status', 'unverified'), ('status', 'pending')]:
            with self.subTest(field=field, value=value):
                data = registry(); data['sources'][0][field] = value
                self.assertEqual(explain_analysis(analysis(), registry=data)['status'], 'NO_BOOK_BASIS')

    def test_unreviewed_template_is_not_published(self):
        data = registry(); data['templates'][0]['independent_review'] = False
        self.assertEqual(explain_analysis(analysis(), registry=data)['status'], 'NO_BOOK_BASIS')

    def test_unresolved_parse_never_fabricates_claims(self):
        result = explain_analysis({'status': 'unresolved', 'tree': None}, registry=registry())
        self.assertEqual(result['status'], 'ANALYSIS_UNRESOLVED')
        self.assertFalse(any(result['channels'].values()))

    def test_conflicting_claims_withheld(self):
        data = registry(); other = copy.deepcopy(data['templates'][0])
        data['templates'][0]['claim_key'] = 'same-claim'
        other.update(id='other', claim_key='same-claim', text='Incompatible test claim.')
        data['templates'].append(other)
        result = explain_analysis(analysis(), registry=data)
        self.assertEqual(result['status'], 'SOURCE_CONFLICT')
        self.assertEqual(result['channels']['structural'], [])

    def test_duplicate_source_or_template_ids_are_not_trusted(self):
        for key in ['sources', 'templates']:
            data = registry(); data[key].append(copy.deepcopy(data[key][0]))
            self.assertEqual(explain_analysis(analysis(), registry=data)['status'], 'NO_BOOK_BASIS')

    def test_cambridge_cannot_determine_br_structure(self):
        data = registry(); data['sources'][0]['book'] = 'Cambridge'
        self.assertEqual(explain_analysis(analysis(), registry=data)['status'], 'NO_BOOK_BASIS')

    def test_grammar_requires_server_rule_evidence(self):
        data = registry(); data['templates'][0]['channel'] = 'grammatical'
        data['templates'][0]['rule_id'] = 'forged'; data['sources'][0]['book'] = 'Cambridge'
        result = explain_analysis(analysis(), registry=data)
        self.assertEqual(result['status'], 'NO_BOOK_BASIS')

    def test_unknown_slots_and_attribute_access_are_rejected(self):
        for text in ['{made_up}', '{sentence.__class__}', '{surface[0]}']:
            data = registry(); data['templates'][0]['text'] = text
            self.assertEqual(explain_analysis(analysis(), registry=data)['status'], 'NO_BOOK_BASIS')

    def test_invalid_tree_and_unknown_node_are_rejected(self):
        data = analysis(); data['tree']['tokens'][0]['index'] = 99
        with self.assertRaises(ValueError): explain_analysis(data, registry=registry())
        with self.assertRaises(ValueError): explain_analysis(analysis(), 'absent', registry=registry())

    def test_client_cannot_supply_source_registry(self):
        with self.assertRaises(ValueError): explain_request({'tree': analysis()['tree'], 'registry': registry()})

    def test_provenance_forgery_does_not_enable_teaching_claims(self):
        tree = analysis()['tree']
        tree['source'].update(review_status='HUMAN_APPROVED', edition='forged', printed_page=12)
        with patch('explanations.load_registry', return_value={'sources': [], 'templates': []}):
            result = explain_request({'tree': tree})
        self.assertEqual(result['status'], 'NO_BOOK_BASIS')

    def test_generator_and_builder_same_tree_same_evidence(self):
        data = analysis()
        with patch('explanations.load_registry', return_value=registry()):
            self.assertEqual(explain_analysis(data), explain_request({'tree': data['tree']}))

    def test_real_evaluator_controls_grammar_and_remediation_channels(self):
        data = registry()
        source = copy.deepcopy(data['sources'][0]); source.update(id='test-cam', book='Cambridge')
        data['sources'].append(source)
        for channel in ['grammatical', 'remediation']:
            template = copy.deepcopy(data['templates'][0])
            template.update(id='test-'+channel, channel=channel, source_ids=['test-cam'],
                            rule_id='TEST-ONLY', when='violation')
            data['templates'].append(template)
        rule = {'rule_id': 'TEST-ONLY', 'rule_type': 'constraint', 'scope': 'sentence',
                'runtime_check': {'kind': 'forbidden_token_sequences',
                                  'forbidden_sequences': [['birds', 'sing']],
                                  'exception_sequences': []}}
        runtime = {'active_rules': [rule]}
        result = explain_analysis(analysis(), registry=data, runtime_registry=runtime)
        self.assertTrue(all(result['channels'].values()))
        rule['runtime_check']['exception_sequences'] = [['the', 'birds', 'sing']]
        result = explain_analysis(analysis(), registry=data, runtime_registry=runtime)
        self.assertEqual(result['channels']['remediation'], [])
        self.assertEqual(result['channels']['grammatical'], [])

    def test_reviewed_descriptive_teaching_is_not_a_runtime_verdict(self):
        data = registry(); data['sources'][0]['book'] = 'Cambridge'
        template = data['templates'][0]
        template.update(channel='grammatical', claim_type='classification')
        result = explain_analysis(analysis(), registry=data)
        self.assertEqual(result['status'], 'EXPLAINED')
        self.assertTrue(result['channels']['grammatical'])
        self.assertEqual(result['channels']['remediation'], [])
        template.update(channel='remediation')
        self.assertEqual(explain_analysis(analysis(), registry=data)['status'], 'NO_BOOK_BASIS')

    def test_passive_make_explanation_uses_only_the_finding_nodes(self):
        parsed = test_cambridge_evaluator.CambridgeEvaluatorTests.passive_analysis()
        runtime = {"active_rules": [{
            "rule_id": "CLS-357", "rule_type": "constraint", "scope": "clause",
            "runtime_check": {"kind": "passive_make_missing_to"},
        }]}
        review = {
            "review_status": "INDEPENDENTLY_REVIEWED", "independent_review": True,
            "reviewed_by": "synthetic-test-reviewer", "reviewed_on": "2026-11-07",
        }
        data = load_registry()
        pending = explain_analysis(parsed, registry=data, runtime_registry=runtime, variety="standard_english")
        self.assertEqual(pending["channels"]["remediation"], [])
        for source in data["sources"]:
            if source["id"] in {"CGEL-2002-CH14-P1234", "CGEL-2002-CH16-P1432"}:
                source.update(status="approved", crosswalk_status="compatible", **review)
        template = next(t for t in data["templates"] if t.get("rule_id") == "CLS-357")
        template.update(review)
        kwargs = dict(registry=data, runtime_registry=runtime, variety="standard_english")
        result = explain_analysis(parsed, **kwargs)
        findings = result["channels"]["remediation"]
        self.assertEqual({item["facts"]["surface"] for item in findings}, {"made", "wait"})
        self.assertEqual(len(findings), 4)  # Two verb nodes and their overt word nodes.
        self.assertTrue(all([source["printed_page"] for source in item["sources"]] == [1234, 1432]
                            for item in findings))
        self.assertTrue(all(item["facts"]["target"] == "finding_nodes" for item in findings))
        target_id = findings[0]["node_id"]
        self.assertEqual(len(explain_analysis(parsed, target_id, **kwargs)["channels"]["remediation"]), 1)
        subject_id = parsed["tree"]["root"]["children"][0]["id"]
        self.assertEqual(explain_analysis(parsed, subject_id, **kwargs)["channels"]["remediation"], [])
        self.assertEqual(explain_analysis({"status": "normalized", "tree": parsed["tree"]},
                                          **kwargs)["channels"]["remediation"], [])
        self.assertEqual(explain_analysis(parsed, registry=data, variety="standard_english")
                         ["channels"]["remediation"], [])

    def test_production_has_no_synthetic_reviewed_sources(self):
        production = load_registry()
        self.assertTrue(production['sources'])
        self.assertEqual({row['id'] for row in production['templates'] if row['independent_review']},
                         {'CGEL-CLS001-TEACHING-V1', 'BR-V2-S-NP-VP-V1'})
        draft, = [row for row in production['templates'] if not row['independent_review']]
        self.assertEqual(draft['id'], 'CGEL-CLS357-PASSIVE-MAKE-V1')
        self.assertEqual(draft['review_status'], 'NOT_REVIEWED')
        for source in production['sources']:
            self.assertTrue(source['id'].startswith(('CGEL-2002-', 'BR-3E-')))
            self.assertNotIn('synthetic', source['title'].casefold())
            if source['status'] == 'approved':
                self.assertTrue(source['independent_review'])
            else:
                self.assertFalse(source['independent_review'])
        receipt = json.loads((ROOT / 'sources/cambridge/reviews/2026-11-08-cls-001.json').read_text())
        self.assertEqual(receipt['template_id'], production['templates'][0]['id'])
        self.assertFalse(receipt['crosswalk_resolution']['br_book_comparison_performed'])
        rules = json.loads((ROOT / 'grammar/rules/clauses.json').read_text())
        rows = rules if isinstance(rules, list) else rules['rules']
        original = next(row for row in rows if row['id'] == 'CLS-001')
        self.assertEqual(production['templates'][0]['text'], original['statement'])
        self.assertEqual({source['printed_page'] for source in production['sources'] if source['book'] == 'Cambridge' and source['status'] == 'approved'}, {44, 45})
        br_receipt = json.loads((ROOT / 'sources/burton_roberts/reviews/2026-11-08-conventions.json').read_text())
        self.assertEqual(br_receipt['content_decision']['template_id'], production['templates'][1]['id'])
        self.assertEqual({source['printed_page'] for source in production['sources'] if source['book'] == 'B-R'}, {29, 30})
        result = explain_analysis(analysis())
        self.assertEqual(result['status'], 'EXPLAINED')
        self.assertTrue(result['channels']['grammatical'])
        self.assertTrue(result['channels']['structural'])
        self.assertEqual(result['channels']['remediation'], [])


if __name__ == '__main__': unittest.main()
