"""Re-run the real-world diagnostics, V4 comparison and textbook PARSEVAL.

The cases and historical predictions informed development. Results are diagnostic.
Outputs go to the caller's directory. Earlier evaluation artifacts stay intact.
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
import statistics
import sys
import time

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'server'))

from analysis_api import ParseFailure, build_payload, health_payload
import burton_roberts as br
from br_tree import _atoms, _source_yield, load_reference_records
from cambridge_registry import load_runtime_registry
from matrix import evaluate
from parse_engine import analyze
from run_cycle7_evaluation import evaluate_corpus, independent_check_correction, summarize_tree_cov
from run_cycle8_evaluation import audit_correction_safety
from run_technical_evaluation import aggregate_parseval, compute_binary_metrics, score_parseval_pair


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def run_probes(cases, schema):
    rows = []
    for case in cases:
        start = time.perf_counter()
        row = {**case, 'execution_status': 'ok'}
        try:
            payload = build_payload(case['text'])
            elapsed = (time.perf_counter() - start) * 1000
            br_analysis = payload['br_analysis']
            tree = br_analysis.get('tree') or br_analysis.get('working_tree')
            row.update(parse=payload['parse'], status=br_analysis['status'],
                       working=bool(br_analysis.get('working_tree')),
                       reasons=br_analysis.get('reasons'),
                       schema_valid=schema.is_valid(tree) if tree else None,
                       token_alignment=all(case['text'][token['start']:token['end']] == token['t']
                                           for token in payload['parse']['tokens']),
                       hybrid_verdict=payload['summary']['verdict'],
                       rules_verdict=evaluate(payload['tree'], text=payload['parse']['text'])['summary']['verdict'],
                       findings=[(item['rule_id'], item['surface'], item['violation'])
                                 for item in payload['unified_findings']['findings']],
                       corrected=payload['summary'].get('corrected_sentence'),
                       explanation=payload['learner_explanation'])
        except ParseFailure as exc:
            row.update(execution_status='unsupported_input', error=str(exc))
            elapsed = (time.perf_counter() - start) * 1000
        except Exception as exc:
            row.update(execution_status='error', error=f'{type(exc).__name__}: {exc}')
            elapsed = (time.perf_counter() - start) * 1000
        row['elapsed_ms'] = round(elapsed, 2)
        rows.append(row)
    return rows


def textbook_parseval(schema):
    profile = br.convention_profile()
    full, triangle, errors = [], [], []
    for record in load_reference_records():
        chapter = record.get('_chapter', 0)
        text, gold = record.get('sentence'), record.get('tree')
        if (record.get('status') != 'IMG' or not isinstance(text, str) or not isinstance(gold, dict)
                or record.get('correct') is False or (chapter > 1 and gold.get('label') == 'Sentence')
                or _source_yield(gold) != _atoms(text)):
            continue
        try:
            result = br.normalize_benepar_candidate(analyze(text), profile)
        except Exception as exc:
            errors.append({'id': record['id'], 'error': f'{type(exc).__name__}: {exc}'})
            result = {}
        tree = result.get('tree')
        row = {'id': record['id'], 'chapter': chapter, 'normalized': bool(tree),
               'working_tree': bool(result.get('working_tree')),
               'schema_valid': schema.is_valid(tree) if tree else None}
        full.append({**row, **(score_parseval_pair(gold, tree['root']) if tree else {})})
        triangle.append({**row, **(score_parseval_pair(gold, tree['root'], True) if tree else {})})
    return {'full': aggregate_parseval(full), 'triangle_aware': aggregate_parseval(triangle),
            'errors': errors, 'rows': full}


def summarize(rows):
    results = {}
    for category in ['all', *sorted({row['category'] for row in rows})]:
        scoped = [row for row in rows if category == 'all' or row['category'] == category]
        labeled = [row for row in scoped if row.get('gold_label')]
        times = [row['elapsed_ms'] for row in scoped if row['execution_status'] == 'ok']
        results[category] = {
            'count': len(scoped),
            'rules_strict': compute_binary_metrics(labeled, 'rules_verdict', 'strict_ungrammatical'),
            'hybrid_decisive': compute_binary_metrics(labeled, 'hybrid_verdict', 'decisive_only'),
            'tree_status': dict(Counter(row.get('status', row['execution_status']) for row in scoped)),
            'working_trees': sum(bool(row.get('working')) for row in scoped),
            'misaligned_source_offsets': sum(row.get('token_alignment') is False for row in scoped),
            'schema_failures': sum(row.get('schema_valid') is False for row in scoped),
            'exposed_repairs': sum(bool(row.get('corrected')) for row in scoped),
            'repairs_on_labeled_controls': sum(bool(row.get('corrected')) and row.get('gold_label') == 'grammatical'
                                              for row in scoped),
            'warm_median_probe_ms': round(statistics.median(times), 2) if times else None,
            'warm_probe_p95_ms': round(statistics.quantiles(times, n=20, method='inclusive')[-1], 2)
            if len(times) > 1 else None,
        }
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    schema = Draft202012Validator(json.loads((ROOT / 'docs/canonical-burton-roberts-tree.schema.json').read_text()))
    cases = json.loads((HERE / 'real_world_reliability/diagnostic_cases.json').read_text())
    health = health_payload()
    if not health['ready']:
        raise SystemExit(health)
    build_payload('The students read books in the library.')
    rows = run_probes(cases, schema)
    write_json(args.output / 'after-probes.json', rows)
    stats = summarize(rows)
    write_json(args.output / 'probe-metrics.json', stats)
    repairs = [dict(text=row['text'], corrected=row['corrected'], **audit_correction_safety(
        row['text'], row['corrected'], [finding[0] for finding in row['findings']],
        independent_check_correction)) for row in rows if row.get('corrected')]
    write_json(args.output / 'correction-audit.json', repairs)

    with (HERE / 'FROZEN_INDEPENDENT_EVAL_V4.csv').open(encoding='utf-8') as source:
        measurements = evaluate_corpus(list(csv.DictReader(source)), schema, load_runtime_registry())
    with (args.output / 'v4-diagnostic-predictions.csv').open('w', encoding='utf-8', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=list(measurements[0]))
        writer.writeheader()
        writer.writerows(measurements)
    groups = defaultdict(list)
    for row in measurements:
        groups[row['dataset']].append(row)
        groups[f"family:{row['error_family']}"].append(row)
    groups['primary'] = [row for row in measurements if row['dataset'] != 'eval4_cola']
    write_json(args.output / 'v4-diagnostic-metrics.json', {
        source: {'rules': compute_binary_metrics(group, 'rules_verdict', 'strict_ungrammatical'),
                 'hybrid': compute_binary_metrics(group, 'hybrid_verdict', 'decisive_only'),
                 'tree_coverage': summarize_tree_cov(group)} for source, group in groups.items()
    })
    write_json(args.output / 'textbook-parseval.json', textbook_parseval(schema))


if __name__ == '__main__':
    main()
