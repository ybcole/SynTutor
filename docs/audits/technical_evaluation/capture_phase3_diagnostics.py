"""Capture local review traces without changing the frozen Phase 2 scorer."""

import argparse
import json
from pathlib import Path

from run_real_world_reliability import write_json

from analysis_api import build_payload
from br_tree import load_reference_records
from burton_roberts import convention_profile, normalize_benepar_candidate
from parse_engine import analyze
from run_technical_evaluation import _extract_spans, score_parseval_pair


def app_record(row):
    text = row['sentence']
    view = build_payload(text)
    summary = view['summary']
    findings = view['learner_analysis']['findings']
    details = []
    for node in view['node_details'].values():
        stored = [f for f in node.get('findings', []) if f.get('status') in {'error', 'suggestion'}]
        if node.get('status') == 'error' or stored:
            details.append({**{k: node.get(k) for k in ('id', 'surface', 'span', 'status',
                                                       'constraint', 'text', 'evidence', 'remediation')},
                            'findings': stored})
    return {**row, 'parse': view['parse'], 'verdict': summary.get('verdict'), 'details': details,
            'constraints': summary.get('constraints_fired'), 'learner_findings': findings,
            'correction': summary.get('corrected_sentence'),
            'correction_edits': (summary.get('correction') or {}).get('edits'),
            'tree_status': view['br_analysis']['status'], 'tokens': [node for node in view['nodes'].values()
                                                                  if not node.get('children')]}


def tree_record(reference, profile):
    result = analyze(reference['sentence'])
    projection = normalize_benepar_candidate(result, profile)
    predicted = projection.get('tree')
    gold = reference['tree']
    return {'id': reference['id'], 'chapter': reference['_chapter'], 'sentence': reference['sentence'],
            'penn': result['parse_string'], 'tokens': result['tokens'], 'status': projection['status'],
            'reasons': projection.get('reasons'), 'gold': gold,
            'projection': predicted['root'] if predicted else None,
            'gold_words': _extract_spans(gold)[0],
            'pred_words': _extract_spans(predicted['root'])[0] if predicted else None,
            'triangle_aware': score_parseval_pair(gold, predicted['root'], True) if predicted else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('local_scores', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(args.manifest.read_text())
    census = json.loads(args.local_scores.read_text())['rows']
    refs = {row['id']: row for row in load_reference_records()}
    for name in ('expect', 'wi'):
        write_json(args.output / f'{name}-traces.json', [app_record(row) for row in manifest[name]])
    profile = convention_profile()
    write_json(args.output / 'br-traces.json', [tree_record(refs[row['id']], profile) for row in census])


if __name__ == '__main__':
    main()
