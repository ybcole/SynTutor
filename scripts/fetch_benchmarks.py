#!/usr/bin/env python3
"""Fetch external benchmark data for SynTutor evaluation.

Downloads minimal-pair / labeled acceptability data from the HuggingFace
datasets-server and writes normalised TSV files consumed by
``server/eval_minimal_pairs.py``.

Emitted TSV format (one record per line, '#' comments ignored)::

    category <TAB> label <TAB> sentence

where ``label`` is ``good`` (grammatical) or ``bad`` (ungrammatical).

Datasets
--------
* BLiMP  (nyu-mll/blimp)  -> syntactic minimal pairs, one config per phenomenon
* CoLA   (nyu-mll/glue, config=cola)  -> single-sentence acceptability labels
* JFLEG  (jhu-clsp/jfleg) -> L2 learner sentences + corrections

Usage::

    python scripts/fetch_benchmarks.py --out benchmarks --limit 100
    python scripts/fetch_benchmarks.py --only blimp --limit 500
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.parse

import requests

ROWS_API = 'https://datasets-server.huggingface.co/rows'
SPLITS_API = 'https://datasets-server.huggingface.co/splits'

BLIMP_DATASET = 'nyu-mll/blimp'
COLA_DATASET = 'nyu-mll/glue'
COLA_CONFIG = 'cola'
JFLEG_DATASET = 'jhu-clsp/jfleg'

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _get(url, params, retries=4):
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=60)
            if r.status_code == 200:
                return r.json()
            last = f'HTTP {r.status_code}'
        except Exception as exc:  # noqa: BLE001
            last = f'{type(exc).__name__}: {exc}'
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f'request failed for {url} {params}: {last}')


def _all_rows(dataset, config, split, limit=None, page=100):
    """Yield rows, paging through the datasets-server /rows endpoint."""
    seen = 0
    offset = 0
    while True:
        want = page if limit is None else min(page, limit - seen)
        if want <= 0:
            break
        data = _get(ROWS_API, {
            'dataset': dataset, 'config': config, 'split': split,
            'offset': offset, 'length': want,
        })
        rows = data.get('rows', [])
        if not rows:
            break
        for entry in rows:
            yield entry['row']
            seen += 1
            if limit is not None and seen >= limit:
                return
        offset += len(rows)
        if len(rows) < want:
            break


def _blimp_configs():
    data = _get(SPLITS_API, {'dataset': BLIMP_DATASET})
    return sorted({s['config'] for s in data['splits']})


def fetch_blimp(limit):
    records = []
    configs = _blimp_configs()
    for cfg in configs:
        try:
            for row in _all_rows(BLIMP_DATASET, cfg, 'train', limit=limit):
                cat = row.get('UID') or cfg
                records.append((cat, 'good', row['sentence_good']))
                records.append((cat, 'bad', row['sentence_bad']))
        except Exception as exc:  # noqa: BLE001
            print(f'  [blimp] {cfg}: skipped ({exc})', file=sys.stderr)
    return records


def fetch_cola(limit, split='validation'):
    records = []
    for row in _all_rows(COLA_DATASET, COLA_CONFIG, split, limit=limit):
        label = 'good' if int(row['label']) == 1 else 'bad'
        records.append(('cola', label, row['sentence'].strip()))
    return records


def fetch_jfleg(limit, split='validation'):
    records = []
    for row in _all_rows(JFLEG_DATASET, 'default', split, limit=limit):
        bad = (row.get('sentence') or '').strip()
        corrections = row.get('corrections') or []
        if not bad or not corrections:
            continue
        good = corrections[0].strip()
        records.append(('jfleg', 'bad', bad))
        records.append(('jfleg', 'good', good))
    return records


def write_tsv(path, records):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, delimiter='\t')
        w.writerow(['category', 'label', 'sentence'])
        for cat, label, sent in records:
            sent = ' '.join(sent.split())
            if sent:
                w.writerow([cat, label, sent])
    n_good = sum(1 for r in records if r[1] == 'good')
    n_bad = len(records) - n_good
    print(f'wrote {path}: {len(records)} records ({n_good} good / {n_bad} bad)')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default=os.path.join(_ROOT, 'benchmarks'),
                    help='output directory (default: <repo>/benchmarks)')
    ap.add_argument('--limit', type=int, default=100,
                    help='max records per dataset/config (default 100)')
    ap.add_argument('--only', choices=['blimp', 'cola', 'jfleg'],
                    help='fetch a single dataset only')
    args = ap.parse_args()

    targets = [args.only] if args.only else ['blimp', 'cola', 'jfleg']
    if 'blimp' in targets:
        print('fetching BLiMP ...')
        write_tsv(os.path.join(args.out, 'blimp.tsv'), fetch_blimp(args.limit))
    if 'cola' in targets:
        print('fetching CoLA ...')
        write_tsv(os.path.join(args.out, 'cola.tsv'), fetch_cola(args.limit))
    if 'jfleg' in targets:
        print('fetching JFLEG ...')
        write_tsv(os.path.join(args.out, 'jfleg.tsv'), fetch_jfleg(args.limit))


if __name__ == '__main__':
    main()
