"""Score source-specified B–R structure from saved zero-lookup projection traces."""

import argparse
from collections import Counter
import json
from pathlib import Path
from unittest.mock import patch

from run_technical_evaluation import _extract_spans


def inside_explicit_triangle(span, triangles):
    start, end, _ = span
    return next((bounds for bounds in triangles
                 if bounds[0] <= start and end <= bounds[1] and (start, end) != bounds), None)


def compare(gold, prediction):
    gw, gs, triangles = _extract_spans(gold)
    pw, ps, _ = _extract_spans(prediction) if prediction else ([], [], [])
    expected, actual = Counter(gs), Counter(ps)
    aligned = bool(prediction) and gw == pw
    matched = expected & actual if aligned else Counter()
    extra = actual - matched
    omitted = expected - matched
    ignored = []
    if aligned:
        for span, count in sorted(extra.items()):
            triangle = inside_explicit_triangle(span, triangles)
            if triangle is not None:
                ignored.append({'span': span, 'count': count, 'reference_triangle': triangle})
    masked = Counter({tuple(row['span']): row['count'] for row in ignored})
    return {
        'aligned': aligned,
        'matched': matched.total(),
        'gold': expected.total(),
        'predicted': actual.total(),
        'ignored': ignored,
        'gold_only': list(omitted.elements()),
        'predicted_only': list((extra - masked).elements()),
        'full_exact': aligned and not omitted and not extra,
        'specified_exact': aligned and not omitted and not extra - masked,
    }


def complexity(gold):
    if gold.get('label') not in {'S', 'Sentence'}:
        return 'phrase_or_fragment'
    children = [gold]
    count = 0
    while children:
        node = children.pop()
        label = node.get('label')
        if label in {'S-bar', 'S-dbar', 'S′', 'S″'}:
            return 'complex_or_embedded'
        count += label in {'S', 'Sentence'}
        children.extend(node.get('children', []))
    return 'complex_or_embedded' if count > 1 else 'simple'


def summarize(rows):
    predicted = sum(row['predicted'] for row in rows)
    gold = sum(row['gold'] for row in rows)
    matched = sum(row['matched'] for row in rows)
    ignored = sum(item['count'] for row in rows for item in row['ignored'])
    return {
        'items': len(rows), 'aligned': sum(row['aligned'] for row in rows),
        'gold': gold, 'predicted': predicted, 'matched': matched,
        'ignored': ignored, 'full_exact': sum(row['full_exact'] for row in rows),
        'specified_exact': sum(row['specified_exact'] for row in rows),
        'full_f1': 2 * matched / (gold + predicted) if gold + predicted else None,
        'reference_specified_f1': (2 * matched / (gold + predicted - ignored)
                                   if gold + predicted > ignored else None),
    }


def audit(traces):
    rows = [
        {'id': item['id'], 'chapter': item['chapter'], 'complexity': complexity(item['gold']),
         **compare(item['gold'], item['projection'])}
        for item in traces
    ]
    aligned = [row for row in rows if row['aligned']]
    return {'all_attempts': summarize(rows), 'aligned_only': summarize(aligned),
            'by_complexity': {
                group: summarize([row for row in rows if row['complexity'] == group])
                for group in sorted({row['complexity'] for row in rows})
            },
            'aligned_gold_placeholders': sum(
                label.lower() == 'phrase' for item in traces
                if item['projection'] and item['gold_words'] == item['pred_words']
                for _, _, label in _extract_spans(item['gold'])[1]
            ),
            'rows': rows}


def capture_traces(selection, output):
    from capture_phase3_diagnostics import tree_record
    from br_tree import load_reference_records
    import burton_roberts as br

    identifiers = [row['id'] for row in json.loads(selection.read_text(encoding='utf-8'))['rows']]
    references = {row['id']: row for row in load_reference_records()}
    if len(identifiers) != 216 or len(set(identifiers)) != 216:
        raise ValueError('Expected the 216 distinct published reference identifiers')
    profile = br.convention_profile()
    with patch.object(br, '_matching_gold_records',
                      side_effect=AssertionError('textbook lookup attempted')) as lookup:
        rows = [tree_record(references[identifier], profile) for identifier in identifiers]
        assert not lookup.called
    with output.open('x', encoding='utf-8') as stream:
        json.dump(rows, stream, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('traces', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--capture-from', type=Path,
                        help='Capture traces for the existing H01 result selection before scoring.')
    args = parser.parse_args()
    if args.capture_from:
        capture_traces(args.capture_from, args.traces)
    result = audit(json.loads(args.traces.read_text(encoding='utf-8')))
    with args.output.open('x', encoding='utf-8') as out:
        json.dump(result, out, indent=2)
    print({key: value for key, value in result.items() if key != 'rows'})


if __name__ == '__main__':
    main()
