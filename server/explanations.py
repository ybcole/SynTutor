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


def _finding_node_labels(evaluation, tree_nodes):
    """Collect only overt nodes explicitly tied to a server finding."""
    labels_by_rule = {}
    for finding in evaluation.get("findings", []):
        for match in finding.get("structural_matches", []):
            targets = labels_by_rule.setdefault(finding["rule_id"], {})
            for role in ("governor_node_id", "dependent_node_id"):
                node_id = match.get(role)
                node = tree_nodes.get(node_id)
                if not node:
                    continue
                label = node.get("label")
                targets[node_id] = label
                for child in node.get("children", []):
                    if child.get("id") and child.get("word") and not child.get("elided"):
                        targets[child["id"]] = label
    return labels_by_rule


def _attach_candidate_xai(output, analysis, source_text, node_id, include_candidate_xai):
    if not include_candidate_xai:
        return
    try:
        from cgel_candidate_xai import candidate_xai_for_sentence
        output['candidate_xai'] = candidate_xai_for_sentence(
            source_text, analysis=analysis, node_id=node_id)
    except Exception as exc:  # candidate diagnostics are never a production failure
        output['candidate_xai'] = {
            'status': 'unavailable', 'production_enabled': False,
            'items': [], 'blocked': [f'{type(exc).__name__}: {exc}'],
        }


def explain_analysis(analysis, node_id=None, *, registry=None, runtime_registry=None,
                     variety=None, include_candidate_xai=False):
    if node_id is not None and (not isinstance(node_id, str) or len(node_id) > 200):
        raise ValueError('node_id must be a string of at most 200 characters')
    if not isinstance(analysis, dict):
        raise ValueError('analysis must be an object')
    output = {'schema_version': '1.0.0', 'status': 'NO_BOOK_BASIS',
              'analysis_status': str(analysis.get('status', 'unresolved')),
              'channels': {key: [] for key in CHANNELS}, 'facts': [], 'diagnostics': [],
              'fact_graph': None, 'contextual_explanations': None,
              'xai4_partial_evaluation': None, 'xai5_localization': None,
              'xai6_naturalization': None, 'xai7_unified': None,
              'learner_explanation': None, 'candidate_xai': None}
    from xai4_partial import evaluate_xai4
    source_text = analysis.get('sentence')
    if source_text is None and isinstance(analysis.get('tree'), dict):
        source_text = analysis['tree'].get('sentence')
    output['xai4_partial_evaluation'] = evaluate_xai4(
        source_text, analysis_status=analysis.get('status', 'unresolved'), variety=variety)
    from xai5_repair import localize_xai4
    output['xai5_localization'] = localize_xai4(
        output['xai4_partial_evaluation'], analysis=analysis, sentence=source_text)
    if (analysis.get('status') in {'normalized', 'working', 'provisional'}
            and isinstance(analysis.get('tree'), dict)):
        from xai_facts import build_fact_graph
        output['fact_graph'] = build_fact_graph(analysis, node_id=node_id)
        from xai_composer import compose_explanations
        output['contextual_explanations'] = compose_explanations(output['fact_graph'], node_id=node_id)
        from learner_explanations import compose_learner_explanation
        output['learner_explanation'] = compose_learner_explanation(
            output['fact_graph'], node_id=node_id)
        from xai6_naturalizer import naturalize
        output['xai6_naturalization'] = naturalize(
            output['fact_graph'], output['contextual_explanations'], node_id=node_id,
            variety=variety)
    if output['learner_explanation'] is None:
        from learner_explanations import compose_learner_explanation
        output['learner_explanation'] = compose_learner_explanation(None, node_id=node_id)
    if (analysis.get('status') != 'normalized' or not isinstance(analysis.get('tree'), dict)
            or analysis['tree'].get('source', {}).get('evidence_status') == 'UNCERTAIN'):
        output['status'] = 'ANALYSIS_UNRESOLVED'
        output['diagnostics'].append({'code': 'ANALYSIS_UNRESOLVED',
                                      'message': 'No resolved canonical analysis is available.'})
        _attach_candidate_xai(output, analysis, source_text, node_id,
                              include_candidate_xai)
        from xai7_unified import assemble
        output['xai7_unified'] = assemble(output)
        return output
    tree = validate_envelope(analysis['tree'])
    nodes = nodes_of(tree)
    all_nodes = dict(nodes)
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
    finding_nodes = _finding_node_labels(evaluation, all_nodes)
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
        finding_target = template.get('target') == 'finding_nodes'
        if finding_target and (channel not in {'grammatical', 'remediation'} or rule_id not in violations):
            continue
        for ident, node in nodes:
            if finding_target:
                if finding_nodes.get(rule_id, {}).get(ident) != template['node_label']:
                    continue
            else:
                if channel != 'structural' and not teaching_only and ident != (tree['root'].get('id') or 'root'):
                    continue
                if node.get('label') != template['node_label']:
                    continue
            expected_children = template.get('node_children_labels')
            if expected_children is not None and [child.get('label') for child in node.get('children', [])] != expected_children:
                continue
            facts = {'label': node.get('label', ''), 'surface': _surface(node),
                     'sentence': tree.get('sentence', ''), 'node_id': ident, 'rule_id': rule_id or ''}
            if finding_target:
                facts['target'] = 'finding_nodes'
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
    _attach_candidate_xai(output, analysis, source_text, node_id,
                          include_candidate_xai)
    from xai7_unified import assemble
    output['xai7_unified'] = assemble(output)
    return output


def explain_quiz_response(item, answer, source_records):
    """Use the same review/source/channel gates for repository-owned quiz prose."""
    output={'schema_version':'1.0.0','status':'NO_BOOK_BASIS','analysis_status':'quiz_feedback',
            'channels':{key:[] for key in CHANNELS},'facts':[],'diagnostics':[]}
    from xai7_unified import assemble
    output['xai7_unified'] = assemble(output, mode='quiz')
    required={'br_structure':'B-R','cambridge_classification':'Cambridge'}.get(item.get('claim_scope'))
    lookup={s.get('id'):s for s in source_records}
    cited=[lookup.get(ident,{}) for ident in item.get('source_ids',[])]
    if (not required or not _reviewed(item) or not cited or len(lookup)!=len(source_records)
            or any(not _eligible_source(s) or s.get('book')!=required for s in cited)):
        output['diagnostics'].append({'code':'NO_BOOK_BASIS','message':'This question lacks eligible reviewed evidence.'})
        return output
    chosen=next((o for o in item['options'] if o['id']==answer),None)
    correct=next((o for o in item['options'] if o['id']==item['answer']),None)
    if answer is not None and chosen is None:raise ValueError('Unknown quiz answer')
    if not correct or not item.get('rationale') or not all(o.get('rationale') for o in item['options']):return output
    facts={'item_id':item['item_id'],'item_version':item['content_version'],'answer_id':answer,
           'correct_answer_id':item['answer'],'response_status':'correct' if answer==item['answer'] else 'incorrect' if chosen else 'unanswered','claim_scope':item['claim_scope']}
    fields={'id','book','title','edition','printed_page','evidence_status','status','crosswalk_status','review_status','independent_review','reviewed_by','reviewed_on'}
    channel='structural' if required=='B-R' else 'grammatical'
    output['channels'][channel].append({'template_id':f"quiz:{item['item_id']}@{item['content_version']}",'node_id':'quiz:'+item['item_id'],
        'text':f"Correct answer: {correct['text']}. {item['rationale']}",
        'deep_text':f"Your selected option: {chosen['rationale']}" if chosen else 'No answer was submitted; it counts as incorrect.',
        'sources':[{k:v for k,v in source.items() if k in fields} for source in cited],'facts':facts})
    output['facts']=[facts];output['status']='EXPLAINED'
    output['xai7_unified'] = assemble(output, mode='quiz')
    return output


def explain_request(data):
    """Transport-neutral endpoint: client metadata is never source authority."""
    if not isinstance(data, dict):
        raise ValueError('request payload must be a JSON object')
    if 'quiz_item_id' in data:
        from quiz_bank import explain_quiz_request
        return explain_quiz_request(data)
    if set(data) - {'tree', 'node_id', 'variety', 'include_candidate_xai'}:
        raise ValueError('only tree, node_id, variety and include_candidate_xai are accepted; source registries cannot be supplied')
    include_candidate_xai = data.get('include_candidate_xai') is True
    variety = data.get('variety')
    if variety is not None and (not isinstance(variety, str) or not variety.strip()):
        raise ValueError('variety must be a non-empty string or null')
    tree = data.get('tree')
    if tree is None:
        return explain_analysis({'status': 'unresolved'}, data.get('node_id'), variety=variety,
                                include_candidate_xai=include_candidate_xai)
    validate_envelope(tree)
    return explain_analysis({'status': 'normalized', 'tree': tree}, data.get('node_id'), variety=variety,
                            include_candidate_xai=include_candidate_xai)
