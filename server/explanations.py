"""Deterministic, fail-closed evidence shared by Generator and Builder.

Only repository-owned templates and independently reviewed source records can
supply teaching claims. Client provenance, model verdicts and legacy matrix
prose are never promoted into source evidence.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from string import Formatter

from jsonschema import Draft202012Validator, ValidationError, SchemaError
from burton_roberts import validate_canonical_tree
from cambridge_registry import load_runtime_registry
from cambridge_evaluator import evaluate_cambridge

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / 'docs/canonical-burton-roberts-tree.schema.json').read_text())
VALIDATOR = Draft202012Validator(SCHEMA)
CHANNELS = ('structural', 'grammatical', 'remediation')
SLOTS = {'label', 'surface', 'sentence', 'node_id', 'rule_id'}


def load_registry():
    try:
        data = json.loads((ROOT / 'grammar/explanation_templates.json').read_text())
        schema = json.loads((ROOT / 'grammar/explanation_templates.schema.json').read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(data)
        return data
    except (OSError, ValueError, RecursionError, ValidationError, SchemaError):
        return {'version': '1.0.0', 'sources': [], 'templates': []}


def validate_envelope(tree):
    """Bound and validate untrusted trees before walking or formatting them."""
    try:
        if len(json.dumps(tree)) > 200_000:
            raise ValueError('canonical tree exceeds 200000 bytes')
        errors = list(VALIDATOR.iter_errors(tree))
        if errors:
            raise ValueError('canonical tree does not match the approved schema: ' + errors[0].message[:200])
        count = 0
        stack = [(tree['root'], 0)]
        while stack:
            node, depth = stack.pop()
            count += 1
            if depth > 80 or count > 1500:
                raise ValueError('canonical tree exceeds supported depth or node count')
            stack.extend((child, depth + 1) for child in node.get('children', []))
        result = validate_canonical_tree(tree)
        if not result['valid']:
            raise ValueError('invalid canonical structure: ' + '; '.join(result['errors'])[:500])
    except (TypeError, RecursionError) as exc:
        raise ValueError('invalid or excessively nested canonical tree') from exc
    return tree


def nodes_of(tree):
    def walk(node, path='root'):
        yield node.get('id') or path, node
        for index, child in enumerate(node.get('children', [])):
            yield from walk(child, f'{path}.{index}')
    return list(walk(tree['root']))


def _surface(node):
    if 'word' in node:
        return '' if node.get('elided') else node['word']
    if node.get('triangle'):
        return ' '.join(node['words'])
    return ' '.join(filter(None, (_surface(child) for child in node.get('children', []))))


def _reviewed(row):
    return (row.get('review_status') in {'INDEPENDENTLY_REVIEWED', 'HUMAN_APPROVED'}
            and row.get('independent_review') is True
            and bool(str(row.get('reviewed_by') or '').strip())
            and bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(row.get('reviewed_on', '')))))


def _eligible_source(source):
    return (_reviewed(source) and source.get('status') == 'approved'
            and source.get('book') in {'B-R', 'Cambridge'}
            and bool(source.get('title')) and bool(source.get('edition'))
            and isinstance(source.get('printed_page'), int)
            and not isinstance(source.get('printed_page'), bool)
            and source['printed_page'] > 0
            and source.get('evidence_status') in {'IMG', 'TXT'}
            and source.get('crosswalk_status') in {'compatible', 'resolved'})


def explain_analysis(analysis, node_id=None, *, registry=None, runtime_registry=None, variety=None):
    if node_id is not None and (not isinstance(node_id, str) or len(node_id) > 200):
        raise ValueError('node_id must be a string of at most 200 characters')
    if not isinstance(analysis, dict):
        raise ValueError('analysis must be an object')
    output = {'schema_version': '1.0.0', 'status': 'NO_BOOK_BASIS',
              'analysis_status': str(analysis.get('status', 'unresolved')),
              'channels': {key: [] for key in CHANNELS}, 'facts': [], 'diagnostics': []}
    if analysis.get('status') != 'normalized' or not isinstance(analysis.get('tree'), dict):
        output['status'] = 'ANALYSIS_UNRESOLVED'
        output['diagnostics'].append({'code': 'ANALYSIS_UNRESOLVED',
                                      'message': 'No resolved canonical analysis is available.'})
        return output
    tree = validate_envelope(analysis['tree'])
    nodes = nodes_of(tree)
    if node_id is not None:
        nodes = [(ident, node) for ident, node in nodes if ident == node_id]
        if not nodes:
            raise ValueError('node_id is not present in the canonical tree')
    registry = deepcopy(registry if registry is not None else load_registry())
    sources = {}
    duplicates = set()
    for row in registry.get('sources', []):
        if not isinstance(row, dict):
            continue
        ident = row.get('id')
        if ident in sources:
            duplicates.add(ident)
        sources[ident] = row
    evaluation = evaluate_cambridge(analysis, runtime_registry if runtime_registry is not None else load_runtime_registry(), variety=variety)
    evaluated_ids = set(evaluation.get('evaluated_rule_ids', []))
    violations = {row['rule_id'] for row in evaluation.get('findings', [])}
    outcomes = {row['rule_id']: row['status'] for row in evaluation.get('evaluations', [])}
    candidates = []
    template_ids = [row.get('id') for row in registry.get('templates', []) if isinstance(row, dict)]
    for template in registry.get('templates', []):
        if not isinstance(template, dict) or template_ids.count(template.get('id')) != 1:
            continue
        channel = template.get('channel')
        refs = template.get('source_ids') or []
        cited = [sources.get(ref, {}) for ref in refs]
        if (channel not in CHANNELS or not _reviewed(template) or not refs
                or any(ref in duplicates for ref in refs)
                or not all(_eligible_source(source) for source in cited)):
            continue
        # Structural conventions cannot be supplied by Cambridge; broader
        # grammatical claims cannot be inferred from B-R tree shape alone.
        required_book = 'B-R' if channel == 'structural' else 'Cambridge'
        if not all(source.get('book') == required_book for source in cited):
            continue
        # Grammar/remediation require an actual server-evaluated rule finding.
        # /api/explain constructs analysis from trees, so it cannot forge these.
        rule_id = template.get('rule_id')
        teaching_only = (channel == 'grammatical' and not rule_id
                         and template.get('claim_type') in {'classification', 'descriptive_generalization'})
        if channel != 'structural' and not teaching_only and rule_id not in evaluated_ids:
            continue
        if channel != 'structural' and not teaching_only and template.get('when') != outcomes.get(rule_id):
            continue
        if channel == 'remediation' and rule_id not in violations:
            continue
        if not isinstance(template.get('node_label'), str):
            continue
        for ident, node in nodes:
            if channel != 'structural' and not teaching_only and ident != (tree['root'].get('id') or 'root'):
                continue
            if node.get('label') != template['node_label']:
                continue
            expected_children = template.get('node_children_labels')
            if expected_children is not None and [child.get('label') for child in node.get('children', [])] != expected_children:
                continue
            facts = {'label': node.get('label', ''), 'surface': _surface(node),
                     'sentence': tree.get('sentence', ''), 'node_id': ident, 'rule_id': rule_id or ''}
            try:
                texts = [template.get('text', ''), template.get('deep_text', '')]
                if not texts[0] or any(field not in SLOTS for text in texts
                                      for _, field, _, _ in Formatter().parse(text) if field is not None):
                    continue
                rendered = [text.format(**facts) for text in texts]
            except (ValueError, KeyError, IndexError, AttributeError):
                continue
            candidates.append((channel, template.get('claim_key', template['id']), ident,
                               {'template_id': template['id'], 'node_id': ident,
                                'text': rendered[0], 'deep_text': rendered[1],
                                'sources': cited, 'facts': facts}))
    # Competing reviewed formulations of one claim do not become settled facts.
    for channel, claim, ident, item in candidates:
        competing = [row for ch, key, nid, row in candidates
                     if (ch, key, nid) == (channel, claim, ident)]
        if len({row['text'] for row in competing}) > 1:
            output['diagnostics'].append({'code': 'SOURCE_CONFLICT', 'message': f'Conflicting evidence for {claim} at {ident}.'})
            continue
        if item not in output['channels'][channel]:
            output['channels'][channel].append(item)
    output['facts'] = [{'node_id': ident, 'label': node.get('label'),
                        'surface': _surface(node)} for ident, node in nodes]
    if output['diagnostics']:
        output['status'] = 'SOURCE_CONFLICT'
    elif any(output['channels'].values()):
        output['status'] = 'EXPLAINED'
    else:
        output['diagnostics'].append({'code': 'NO_BOOK_BASIS',
                                      'message': 'No independently reviewed source/template supports an explanation for this analysis.'})
    return output


def explain_request(data):
    """Transport-neutral endpoint: client metadata is never source authority."""
    if not isinstance(data, dict):
        raise ValueError('request payload must be a JSON object')
    if set(data) - {'tree', 'node_id', 'rule_id'}:
        raise ValueError('only tree, node_id and variety are accepted; source registries cannot be supplied')
    variety = data.get('variety')
    if variety is not None and (not isinstance(variety, str) or not variety.strip()):
        raise ValueError('variety must be a non-empty string or null')
    tree = data.get('tree')
    if tree is None:
        return explain_analysis({'status': 'unresolved'}, data.get('node_id'), variety=variety)
    validate_envelope(tree)
    return explain_analysis({'status': 'normalized', 'tree': tree}, data.get('node_id'), variety=variety)
