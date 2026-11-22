"""Reproduce H01 and isolate the positive-evidence licensing component of H02."""

import argparse
from collections import Counter
from contextlib import ExitStack
from itertools import accumulate
import json
from pathlib import Path
from unittest.mock import patch

from run_real_world_reliability import (
    ROOT, Draft202012Validator, analyze, br, load_reference_records, textbook_parseval,
    write_json,
)
from run_technical_evaluation import _extract_spans, score_parseval_pair
import run_phase2_external as external


def schema():
    path = ROOT / 'docs/canonical-burton-roberts-tree.schema.json'
    return Draft202012Validator(json.loads(path.read_text()))


def explicit_clauses(node):
    return (int(node.get('label') in {'S', 'Sentence'})
            + sum(explicit_clauses(child) for child in node.get('children', [])))


def all_attempts(rows):
    aligned = [row for row in rows if row.get('yield_match')]
    # A mismatched yield contributes gold spans and all emitted span counts,
    # but no matches. A fallback has no comparable canonical prediction.
    gold = sum(row['gold_spans'] for row in rows)
    predicted = sum(row.get('pred_count', 0) for row in rows)
    matched = sum(row['labeled_match'] for row in aligned)
    return {
        'attempted': len(rows),
        'normalized': sum(row['normalized'] for row in rows),
        'aligned': len(aligned),
        'full_exact': sum(row['exact_match'] for row in aligned),
        'matched': matched, 'gold': gold, 'predicted': predicted,
        'f1': 2 * matched / (gold + predicted) if gold + predicted else None,
    }


def score_lexical_characters(gold, prediction):
    """Secondary alignment for equivalent splits of an identical lexical yield."""
    def source_ranges(tree):
        words, spans, _ = _extract_spans(tree)
        tokens = [word.replace('’', "'") for word in words]
        offsets = list(accumulate(map(len, tokens), initial=0))
        return ''.join(tokens), Counter((offsets[start], offsets[end], label)
                                        for start, end, label in spans)

    gold_yield, expected = source_ranges(gold)
    predicted_yield, actual = source_ranges(prediction)
    if gold_yield != predicted_yield:
        return {'yield_match': False, 'gold_yield': gold_yield, 'predicted_yield': predicted_yield}
    return {'yield_match': True, 'matches': (expected & actual).total(),
            'gold': expected.total(), 'predicted': actual.total(), 'exact': expected == actual,
            'gold_only': list((expected - actual).elements()),
            'predicted_only': list((actual - expected).elements())}


def check_figure_79b():
    # Visual transcription of the author's diagram, not a projected reference.
    # Keep the two printed NP triangles, unlabelled C1 value and control index.
    gold = {
        'label': 'S', 'children': [
            {'label': 'NP', 'index': '1', 'triangle': True, 'words': ['he']},
            {'label': 'VP', 'children': [
                {'label': 'TENSE', 'features': ['past'], 'children': [{'word': 'didn’t'}]},
                {'label': 'VP', 'children': [
                    {'label': 'V', 'children': [{'word': 'remember'}]},
                    {'label': 'S-bar', 'children': [
                        {'label': 'C1', 'empty': True},
                        {'label': 'S', 'children': [
                            {'label': 'NP', 'children': [{'label': 'E', 'index': '1', 'symbol': '•'}]},
                            {'label': 'VP', 'children': [
                                {'label': 'V', 'features': ['trans', '-tense'],
                                 'children': [{'word': 'kissing'}]},
                                {'label': 'NP', 'triangle': True, 'words': ['Millie']},
                            ]},
                        ]},
                    ]},
                ]},
            ]},
        ],
    }
    text = 'He didn’t remember kissing Millie.'
    candidate = analyze(text)
    result = br.normalize_benepar_candidate(candidate, br.convention_profile())
    prediction = result.get('tree')
    return {
        'reference': 'Noel Burton-Roberts, Analysing Sentences, 3rd ed., p. 239, [79a–b]',
        'text': text, 'gold_transcription': gold, 'penn': candidate['parse_string'],
        'status': result['status'], 'reasons': result.get('reasons'),
        'prediction': prediction, 'working_tree': result.get('working_tree'),
        'full': score_parseval_pair(gold, prediction['root']) if prediction else None,
        'lexical_character_comparison': score_lexical_characters(gold, prediction['root'])
        if prediction else None,
    }


def h01(output):
    references = {row['id']: row for row in load_reference_records()}
    with patch.object(br, '_matching_gold_records',
                      side_effect=AssertionError('textbook lookup attempted')) as lookup:
        report = textbook_parseval(schema())
        additional_case = check_figure_79b()
        if lookup.called:
            raise AssertionError('textbook retrieval was invoked')
    rows = report['rows']
    if len(rows) != 216:
        raise ValueError(f'Expected 216 reference records, got {len(rows)}')
    for row in rows:
        reference = references[row['id']]
        tree = reference['tree']
        words, spans, _ = _extract_spans(tree)
        row.update(reference_page=reference.get('page'), figure=reference.get('fig'),
                   reference_file=reference['_source_path'], gold_spans=len(spans),
                   reference_words=len(words), explicit_clauses=explicit_clauses(tree),
                   sentence_root=tree.get('label') in {'S', 'Sentence'})
    report['all_attempts'] = all_attempts(rows)
    report['by_clause_count'] = {
        key: all_attempts([row for row in rows
                           if min(row['explicit_clauses'], 2) == value])
        for value, key in enumerate(('zero', 'one', 'two_or_more'))
    }
    report['sentence_root_only'] = all_attempts([row for row in rows if row['sentence_root']])
    write_json(output / 'h01.json', report)
    write_json(output / 'h01-source-figure-79b.json', additional_case)
    print(json.dumps({key: report[key] for key in ('full', 'triangle_aware', 'all_attempts',
                                                    'by_clause_count', 'sentence_root_only')}, indent=2))
    print('Figure [79b]', additional_case['status'], additional_case['lexical_character_comparison'])


def disabled_lexicon(*_args, **_kwargs):
    return [], {'content': 0, 'licensed': 0, 'unverified': 0, 'malformed': 0}


def view_packet(view):
    return {
        'parse': view['parse'],
        'tree_status': view['br_analysis']['status'],
        'cambridge': view['cambridge_evaluation'],
        'verdict': view['summary']['verdict'],
        'detector': view['summary'].get('detector'),
        'rules': view['summary'].get('constraints_fired'),
        'matrix_correction': view['summary'].get('corrected_sentence'),
        'learner': view['learner_analysis'],
    }


def score_verdicts(blimp, views):
    labels = Counter()
    for row in blimp:
        view = views[row['sentence']]
        verdict = view['verdict'] if 'verdict' in view else 'processing_failure'
        labels[row['gold_label'], verdict] += 1
    return {gold: {verdict: n for (expected, verdict), n in labels.items() if expected == gold}
            for gold in ('grammatical', 'ungrammatical')}


def h02(sources, manifest, output):
    import analysis_api
    import licensing

    batch = json.loads(manifest.read_text())
    if batch['scorer_sha256'] != external.digest(Path(external.__file__)):
        raise ValueError('Frozen external scorer digest changed')
    for name in ('blimp.tar.gz', 'wi-locness-v2.1.tar.gz', 'expect-test.json'):
        if batch['source_sha256'][name] != external.digest(sources / name):
            raise ValueError(f'Frozen source digest changed for {name}')
    all_rows = [row for name in ('blimp', 'wi', 'expect') for row in batch[name]]
    sentences = list(dict.fromkeys(row['sentence'] for row in all_rows))
    if len(sentences) != len(all_rows):
        raise ValueError('Unexpected overlapping items in frozen diagnostic manifest')
    pairs = {}
    raw_app = analysis_api.build_payload
    for arm in ('on', 'off'):
        directory = output / arm
        directory.mkdir()
        views, packets = {}, {}
        with ExitStack() as stack:
            if arm == 'off':
                stack.enter_context(patch.object(licensing, 'check_lexicon', disabled_lexicon))
                stack.enter_context(patch.object(licensing, 'check_relatives', return_value=[]))
            for text in sentences:
                try:
                    view = raw_app(text)
                    views[text] = view
                    packets[text] = view_packet(view)
                except Exception as exc:
                    packets[text] = {'failure': f'{type(exc).__name__}: {exc}'}
        write_json(directory / 'packets.json', packets)
        pairs[arm] = packets

        def full_sentence(text):
            if text not in views:
                raise ValueError(packets[text]['failure'])
            view = views[text]
            if view['parse']['sentence_count'] != 1 or view['parse']['text'] != text.strip():
                raise ValueError('application did not analyze the entire scoring item as one sentence')
            return view

        def learner_revision(text):
            view = full_sentence(text)
            revision = (view['learner_analysis'].get('revision') or {}).get('text')
            return {**view, 'summary': {**view['summary'], 'corrected_sentence': revision}}

        learner_directory = directory / 'learner'
        learner_directory.mkdir()
        with patch.object(external, 'load_application_sentence', full_sentence):
            matrix_wi = external.score_wi(batch['wi'], directory)
            expect = external.score_expect(batch['expect'], directory)
        with patch.object(external, 'load_application_sentence', learner_revision):
            learner_wi = external.score_wi(batch['wi'], learner_directory)
        blimp = {row['sentence']: packets[row['sentence']] for row in batch['blimp']}
        blimp = {text: packet if text in views and views[text]['parse']['sentence_count'] == 1
                 and views[text]['parse']['text'] == text.strip() else {}
                 for text, packet in blimp.items()}
        summary = {
            'manifest_sha256': external.digest(manifest),
            'blimp': score_verdicts(batch['blimp'], blimp),
            'matrix_wi': matrix_wi, 'learner_wi': learner_wi, 'expect': expect,
            'packets_with_rule_findings': sum(bool(p.get('learner', {}).get('findings'))
                                              for p in packets.values()),
            'packets_with_sentence_prose': sum(bool(p.get('learner', {}).get('sentence_text'))
                                               for p in packets.values()),
            'packets_with_node_prose': sum(any(n.get('text') for n in p.get('learner', {}).get('nodes', {}).values())
                                           for p in packets.values()),
        }
        write_json(directory / 'summary.json', summary)
        print(arm, json.dumps(summary, indent=2), flush=True)
    different = [text for text in sentences if pairs['on'][text] != pairs['off'][text]]
    shared_fields = ('parse', 'tree_status', 'cambridge', 'detector')
    differences = [text for text in sentences
                   if any(pairs['on'][text].get(field) != pairs['off'][text].get(field)
                          for field in shared_fields)]
    if differences:
        raise AssertionError(f'Unexpected paired upstream differences on {len(differences)} inputs')
    write_json(output / 'paired.json', {'inputs': len(sentences), 'changed_packets': different,
                                        'common_channel_disagreements': differences})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='phase', required=True)
    parser_h01 = commands.add_parser('h01')
    parser_h01.add_argument('output', type=Path)
    parser_h02 = commands.add_parser('h02')
    parser_h02.add_argument('sources', type=Path)
    parser_h02.add_argument('manifest', type=Path)
    parser_h02.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    if args.phase == 'h01':
        h01(args.output)
    else:
        h02(args.sources, args.manifest, args.output)


if __name__ == '__main__':
    main()
