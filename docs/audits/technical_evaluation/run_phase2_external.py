"""Freeze and score the Phase 2 research samples. Keep corpora in an external directory."""

import argparse
from collections import Counter, defaultdict
import csv
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import unicodedata

from nltk import Tree
from nltk.tokenize.treebank import TreebankWordDetokenizer

from freeze_independent_eval_v4 import collect_prior_sentences, _toks
from run_cycle7_evaluation import compute_rich_metrics, evaluate_corpus
from run_real_world_reliability import ROOT, write_json


SALT = 'syntutor-phase2-v1'
SOURCES = ('blimp.tar.gz', 'wi-locness-v2.1.tar.gz', 'expect-test.json', 'gum-gold.tar.gz')
DETOKENIZER = TreebankWordDetokenizer()
PTB_WORDS = dict(zip(('-LRB-', '-RRB-', '-LSB-', '-RSB-', '-LCB-', '-RCB-', '``', "''"),
                     ('(', ')', '[', ']', '{', '}', '"', '"')))
PTB_PUNCT = {'.', ',', ':', '``', "''", '-LRB-', '-RRB-', '-LSB-', '-RSB-', '-LCB-', '-RCB-'}


def norm(text):
    return ''.join(re.findall(r'\w+', unicodedata.normalize('NFC', text).casefold()))


def rank(key):
    return sha256(f'{SALT}:{key}'.encode()).hexdigest()


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def prior_texts():
    prior, _ = collect_prior_sentences()
    paths = [*ROOT.glob('benchmarks/*.tsv'), *ROOT.glob('docs/audits/technical_evaluation/**/*.csv')]
    for path in sorted(paths):
        with path.open(encoding='utf-8', newline='') as f:
            for row in csv.DictReader(f, delimiter='\t' if path.suffix == '.tsv' else ','):
                prior.update(row[key] for key in ('sentence', 'reference_correction') if row.get(key))
    for path in ROOT.glob('web/content/book/ch*.trees.json'):
        prior.update(row['sentence'] for row in json.loads(path.read_text())['trees'] if row.get('sentence'))
    probes = ROOT / 'docs/audits/technical_evaluation/real_world_reliability/diagnostic_cases.json'
    prior.update(row['text'] for row in json.loads(probes.read_text()))
    return prior


def blimp_rows(archive_path, excluded, prior):
    # Look up token sets through their words to avoid comparing with unrelated records.
    inverted = defaultdict(list)
    prior_sets = {frozenset(_toks(text)) for text in prior}
    for words in prior_sets:
        for word in words:
            inverted[word].append(words)

    def near_prior(text):
        words = _toks(text)
        return any(len(words & other) / len(words | other) >= .85
                   for token in words for other in inverted[token]
                   if .85 * len(words) <= len(other) <= len(words) / .85)

    with tarfile.open(archive_path) as archive:
        for name in sorted(archive.getnames()):
            if '/data/' not in name or not name.endswith('.jsonl'):
                continue
            candidates = [json.loads(line) for line in archive.extractfile(name)]
            # BLiMP includes semantic contrasts normally outside a grammar checker.
            if candidates[0]['field'] == 'semantics':
                continue
            for pair in sorted(candidates, key=lambda row: rank(f"{row['UID']}:{row['pairID']}")):
                good, bad = pair['sentence_good'], pair['sentence_bad']
                keys = {norm(good), norm(bad)}
                if keys & excluded or near_prior(good) or near_prior(bad):
                    continue
                excluded.update(keys)
                for label, sentence in (('grammatical', good), ('ungrammatical', bad)):
                    yield {'item_id': f"{pair['UID']}:{pair['pairID']}:{label}", 'dataset': 'external_blimp',
                           'gold_label': label, 'sentence': sentence, 'field': pair['field'],
                           'source_category': pair['UID'], 'error_family': pair['linguistics_term']}
                break


def wi_rows(archive_path, excluded):
    from spacy import load

    spacy_tokenizer = load('en_core_web_md', enable=[]).tokenizer
    with tarfile.open(archive_path) as archive:
        # EXPECT below is restricted to the distinct LOCNESS/native portion.
        for level in 'ABC':
            path = f'wi+locness/m2/{level}.dev.gold.bea19.m2'
            blocks = archive.extractfile(path).read().decode().strip().split('\n\n')
            chosen = 0
            for index in sorted(range(len(blocks)), key=lambda index: rank(f'{level}.dev:{index}')):
                block = blocks[index]
                original = block.splitlines()[0].removeprefix('S ')
                text = DETOKENIZER.detokenize(original.split())
                key = norm(text)
                if not key or key in excluded or len(original.split()) > 80:
                    continue
                if [t.text for t in spacy_tokenizer(text)] != original.split():
                    continue
                excluded.add(key)
                yield {'id': f'{level}.dev:{index}', 'sentence': text, 'reference': block}
                chosen += 1
                if chosen == 40:
                    break


def expect_rows(path, excluded):
    groups = defaultdict(list)
    for index, line in enumerate(path.read_text(encoding='utf-8').splitlines()):
        row = json.loads(line)
        if row['origin'] != 'N':
            continue
        offset = len(row['target']) + 1
        positions = {}
        words = []
        for i, word in enumerate(row['source']):
            if word != '[NONE]':
                positions[i + offset] = len(words)
                words.append(word)
        edit = sorted({positions[i] for i in row['correction_index'] if i in positions})
        evidence = sorted({positions[i] for i in row['evidence_index'] if i in positions} - set(edit))
        if edit and len(words) <= 80:
            groups[' '.join(words)].append({'id': index, 'edit': edit, 'evidence': evidence,
                                           'category': row['error_type']})
    for text, rows in sorted(groups.items()):
        if norm(text) not in excluded:
            yield {'sentence': text, 'annotations': rows}


def gum_rows(archive_path, excluded):
    with tarfile.open(archive_path) as archive:
        for name in sorted(archive.getnames()):
            if '/const_gold/' not in name or not name.endswith('.ptb') or 'GUM_reddit_' in name:
                continue
            data = archive.extractfile(name).read().decode()
            for index, item in enumerate(penn_trees(data)):
                tree = Tree.fromstring(item)
                leaves = [PTB_WORDS.get(word, word) for word, tag in tree.pos() if tag != '-NONE-']
                text = DETOKENIZER.detokenize(leaves)
                if norm(text) and norm(text) not in excluded:
                    yield {'id': f'{Path(name).stem}:{index}', 'sentence': text, 'reference': item.strip()}


def penn_trees(data):
    depth = 0
    for index, char in enumerate(data):
        if char == '(':
            if depth == 0:
                start = index
            depth += 1
        elif char == ')':
            depth -= 1
            if depth == 0:
                yield data[start:index + 1]
            elif depth < 0:
                raise ValueError('unmatched closing bracket in the published Penn trees')
    if depth:
        raise ValueError('unclosed bracket in the published Penn trees')


def freeze(data, manifest):
    prior = prior_texts()
    excluded = {norm(text) for text in prior}
    samples = list(blimp_rows(data / SOURCES[0], excluded, prior))
    wi = list(wi_rows(data / SOURCES[1], excluded))
    expect = list(expect_rows(data / SOURCES[2], excluded))
    gum = list(gum_rows(data / SOURCES[3], excluded))
    payload = {'salt': SALT, 'scorer_sha256': digest(Path(__file__)), 'known_prior_texts': len(prior),
               'source_sha256': {name: digest(data / name) for name in SOURCES},
               'blimp': samples, 'wi': wi, 'expect': expect, 'gum': gum}
    if manifest.exists():
        raise FileExistsError(manifest)
    write_json(manifest, payload)
    print({key: len(payload[key]) for key in ('blimp', 'wi', 'expect', 'gum')})


def counts(tp, fp, fn, beta=1):
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    denom = (1 + beta**2) * tp + beta**2 * fn + fp
    return dict(tp=tp, fp=fp, fn=fn, precision=precision, recall=recall,
                f=(1 + beta**2) * tp / denom if denom else 0)


def load_application_sentence(text):
    from analysis_api import build_payload

    payload = build_payload(text)
    if payload['parse']['sentence_count'] != 1 or payload['parse']['text'] != text.strip():
        raise ValueError('application did not analyze the entire scoring item as one sentence')
    return payload


def score_wi(rows, output):
    import errant
    import spacy

    annotator = errant.load('en', spacy.load('en_core_web_md', disable=['ner']))
    hypotheses, predictions = [], []
    for row in rows:
        reference = row['reference'].splitlines()[0]
        result = {'id': row['id'], 'revision': None}
        try:
            result['revision'] = load_application_sentence(row['sentence'])['summary'].get('corrected_sentence')
        except Exception as exc:
            result['failure'] = f'{type(exc).__name__}: {exc}'
        edits = []
        if result['revision']:
            original = annotator.parse(reference.removeprefix('S '))
            revised = annotator.parse(result['revision'], tokenise=True)
            edits = [edit.to_m2(0) for edit in annotator.annotate(original, revised)]
        hypotheses.append('\n'.join([reference, *edits]))
        predictions.append(result)
    hypothesis, reference = output / 'wi-hyp.m2', output / 'wi-ref.m2'
    hypothesis.write_text('\n\n'.join(hypotheses) + '\n', encoding='utf-8')
    reference.write_text('\n\n'.join(row['reference'] for row in rows) + '\n', encoding='utf-8')
    scoring = subprocess.check_output([sys.executable, '-c', 'from errant.commands.compare_m2 import main; main()',
                                       '-hyp', str(hypothesis), '-ref', str(reference), '-cs'], text=True)
    (output / 'wi-errant.txt').write_text(scoring, encoding='utf-8')
    write_json(output / 'wi-predictions.json', predictions)
    return {'items': len(rows), 'api_revisions': sum(bool(r['revision']) for r in predictions),
            'failures': sum('failure' in r for r in predictions), 'errant': scoring.strip()}


def score_expect(rows, output):
    predictions = []
    for row in rows:
        text = row['sentence']
        offsets = [match.span() for match in re.finditer(r'\S+', text)]
        try:
            payload = load_application_sentence(text)
            tokens = payload['parse']['tokens']
            positions = {tok['i']: {i for i, (s, e) in enumerate(offsets) if tok['start'] < e and tok['end'] > s}
                         for tok in tokens}
            assert all(positions.values()) and all(text[t['start']:t['end']] == t['t'] for t in tokens)
            findings = payload['learner_analysis']['findings']
            failure = None
        except Exception as exc:
            failure = f'{type(exc).__name__}: {exc}'
            findings = []
        for annotation in row['annotations']:
            anchors, gold = set(annotation['edit']), set(annotation['evidence'])
            matched = [f for f in findings if anchors & set().union(
                *(positions.get(t, set()) for t in f['target_token_ids']))]
            related = set().union(*(positions.get(t, set()) for f in matched for t in f['related_token_ids'])) - anchors
            predictions.append({'id': annotation['id'], 'category': annotation['category'],
                                'target_detected': bool(matched), 'evidence': sorted(related),
                                'tp': len(gold & related), 'fp': len(related - gold), 'fn': len(gold - related),
                                'failure': failure})
    write_json(output / 'expect-predictions.json', predictions)
    return {**counts(*(sum(r[key] for r in predictions) for key in ('tp', 'fp', 'fn'))),
            'sentences': len(rows), 'annotations': len(predictions),
            'anchored': sum(r['target_detected'] for r in predictions),
            'failures': sum(bool(r['failure']) for r in predictions)}


def penn_brackets(tree):
    # Compare Penn phrase categories only, using lexical-character offsets to
    # permit equivalent splits. Function tags, punctuation and empty nodes go.
    brackets, pieces = Counter(), []
    cursor = 0

    def visit(node):
        nonlocal cursor
        category = node.label()
        if node.height() == 2:
            if category not in PTB_PUNCT | {'-NONE-'}:
                word = ''.join(PTB_WORDS.get(node[0], node[0]).split())
                pieces.append(word)
                cursor += len(word)
            return
        start = cursor
        for child in node:
            visit(child)
        category = re.split('[-=]', category, maxsplit=1)[0]
        if cursor > start and category not in {'ROOT', 'TOP'}:
            brackets[start, cursor, category] += 1

    visit(tree)
    return ''.join(pieces), brackets


def score_gum(rows, output):
    from parse_engine import analyze

    predictions = []
    for row in rows:
        scored = {'id': row['id']}
        try:
            analysis = analyze(row['sentence'])
            scored['candidate'] = analysis['parse_string']
            if analysis['sentence_count'] != 1:
                raise ValueError('different sentence segmentation')
            gold_yield, gold = penn_brackets(Tree.fromstring(row['reference']))
            system_yield, system = penn_brackets(Tree.fromstring(analysis['parse_string']))
            if gold_yield != system_yield:
                raise ValueError('different lexical yield after Penn punctuation normalization')
            scored.update(tp=(gold & system).total(), fp=(system - gold).total(), fn=(gold - system).total())
        except Exception as exc:
            scored['failure'] = f'{type(exc).__name__}: {exc}'
        predictions.append(scored)
    write_json(output / 'gum-predictions.json', predictions)
    return {**counts(*(sum(r.get(key, 0) for r in predictions) for key in ('tp', 'fp', 'fn'))),
            'items': len(rows), 'aligned': sum('failure' not in row for row in predictions)}


def run(data, manifest, output):
    from jsonschema import Draft202012Validator
    from cambridge_registry import load_runtime_registry

    batch = json.loads(manifest.read_text())
    assert batch['scorer_sha256'] == digest(Path(__file__)), 'scorer changed after sample lock'
    assert batch['source_sha256'] == {name: digest(data / name) for name in SOURCES}, 'source hash changed'
    output.mkdir(parents=True, exist_ok=False)
    schema = Draft202012Validator(json.loads((ROOT / 'docs/canonical-burton-roberts-tree.schema.json').read_text()))
    blimp = evaluate_corpus(batch['blimp'], schema, load_runtime_registry())
    write_json(output / 'blimp-predictions.json', blimp)
    scores = {'manifest_sha256': digest(manifest),
              'blimp': {'rules': compute_rich_metrics(blimp, 'rules_verdict', 'strict_ungrammatical'),
                        'hybrid': compute_rich_metrics(blimp, 'hybrid_verdict', 'decisive_only')},
              'wi': score_wi(batch['wi'], output),
              'expect': score_expect(batch['expect'], output),
              'gum': score_gum(batch['gum'], output)}
    write_json(output / 'metrics.json', scores)
    print(json.dumps(scores, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sources', type=Path)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--output', type=Path, help='Score a frozen sample instead of freezing it.')
    args = parser.parse_args()
    if args.output:
        run(args.sources, args.manifest, args.output)
    else:
        freeze(args.sources, args.manifest)
