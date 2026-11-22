"""Summarize frozen Phase 2 outputs and paired Phase 3 diagnostics."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from run_cycle7_evaluation import compute_rich_metrics
from run_phase2_external import counts
from run_real_world_reliability import write_json
from run_technical_evaluation import score_parseval_pair


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def m2_edits(block):
    from errant.commands.compare_m2 import simplify_edits

    edits = simplify_edits(block)
    if len({row[-1] for row in edits}) > 1:
        raise ValueError('This diagnostic requires a single annotator per scoring item')
    return {(start, end, correction): category
            for start, end, category, correction, _ in edits
            if start >= 0 and category != 'UNK'}


def wi_diagnostics(folder):
    predictions = read(folder / 'wi-predictions.json')
    ref = (folder / 'wi-ref.m2').read_text().strip().split('\n\n')
    hyp = (folder / 'wi-hyp.m2').read_text().strip().split('\n\n')
    assert len(predictions) == len(ref) == len(hyp)
    false_negatives, rows, by_type = Counter(), [], defaultdict(Counter)
    for row, gold_block, hyp_block in zip(predictions, ref, hyp):
        assert gold_block.splitlines()[0] == hyp_block.splitlines()[0]
        gold, system = m2_edits(gold_block), m2_edits(hyp_block)
        common, missed, extra = gold.keys() & system.keys(), gold.keys() - system.keys(), system.keys() - gold.keys()
        for key in common:
            by_type[gold[key]]['tp'] += 1
        for key in missed:
            by_type[gold[key]]['fn'] += 1
            false_negatives[(bool(row.get('failure')), gold[key])] += 1
        for key in extra:
            by_type[system[key]]['fp'] += 1
        rows.append({
            **row, 'matched': sorted(common), 'missing': [(*key, gold[key]) for key in sorted(missed)],
            'extra': [(*key, system[key]) for key in sorted(extra)],
            'clean_reference': not gold,
        })
    return {
        'items': len(rows),
        'scored_edits': {key: sum(len(r[field]) for r in rows)
                         for key, field in [('tp', 'matched'), ('fp', 'extra'), ('fn', 'missing')]},
        'edited_no_gold_edit': [r['id'] for r in rows if r['clean_reference'] and r['extra']],
        'adapter_misses': {key: value for (failed, key), value in false_negatives.items() if failed},
        'other_misses': {key: value for (failed, key), value in false_negatives.items() if not failed},
        'supported_agreement_tag': dict(by_type['R:VERB:SVA']),
        'rows': rows,
    }


def expect_diagnostics(folder):
    rows = read(folder / 'expect-predictions.json')
    by_cause, by_category = defaultdict(Counter), defaultdict(Counter)
    for row in rows:
        cause = 'adapter_split' if row['failure'] else 'anchored' if row['target_detected'] else 'unanchored'
        if row['tp'] + row['fn'] == 0:
            cause += '_no_source_evidence'
        stats = {k: row[k] for k in ('tp', 'fp', 'fn')}
        by_cause[cause].update(items=1, **stats)
        by_category[row['category']].update(items=1, anchors=int(row['target_detected']), **stats)
    return {'annotation_groups': by_cause, 'gold_categories': by_category}


def textbook_diagnostics(traces, common):
    rows = read(traces / 'br-traces.json')
    full = [score_parseval_pair(r['gold'], r['projection'], False) for r in rows if r['id'] in common]
    gold = sum(r['gold_count'] for r in full)
    pred = sum(r['pred_count'] for r in full)
    correct = sum(r['labeled_match'] for r in full)
    return {
        'unresolved': {r['id']: r['reasons'] for r in rows if r['status'] != 'normalized'},
        'yield_mismatches': [r['id'] for r in rows if r['projection'] and r['pred_words'] != r['gold_words']],
        'common_aligned': {'items': len(full), **counts(correct, pred - correct, gold - correct)},
        'recipient_wh_profile': next(r['triangle_aware'] for r in rows if r['id'] == 'ch9-d1bi'),
    }


def summarize(directory, common):
    blimp = read(directory / 'blimp-predictions.json')
    # Limit the secondary profile to implemented families and keep every case
    # in them regardless of verdict or whether its particular parse succeeded.
    prefixes = ('determiner_noun_agreement', 'irregular_past_participle',
                'regular_plural_subject_verb_agreement', 'irregular_plural_subject_verb_agreement')
    profile = [r for r in blimp if r['source_category'].startswith(prefixes)]
    return {
        'blimp_supported_families': compute_rich_metrics(profile, 'rules_verdict', 'strict_ungrammatical'),
        'wi': wi_diagnostics(directory),
        'expect': expect_diagnostics(directory),
        'textbook': textbook_diagnostics(directory.parent / directory.name.replace('-external', '-traces'), common),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='Workspace with baseline and final scoring/traces')
    args = parser.parse_args()
    before, after = (args.directory / f'{stage}-external' for stage in ('baseline', 'final'))
    aligned = []
    for directory in (before, after):
        rows = read(directory.parent / directory.name.replace('-external', '-traces') / 'br-traces.json')
        aligned.append({r['id'] for r in rows if r['projection'] and r['pred_words'] == r['gold_words']})
    common = aligned[0] & aligned[1]
    write_json(args.directory / 'diagnostic-breakdown.json', {
        'baseline': summarize(before, common), 'final': summarize(after, common)})


if __name__ == '__main__':
    main()
