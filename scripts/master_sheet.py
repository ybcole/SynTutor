"""SynTutor master sheet: model-detection review over every quiz sentence.

For every quiz question in ``web/content/master.json`` we know which sentences
are meant to be WRONG (``bad != good``) and which are meant to be RIGHT
(``bad == good``). This harness drives the *real* SynTutor model (spaCy +
benepar parse -> deterministic constraint matrix) over each sentence and checks:

    expected error  + model flags   -> detected   (true positive)
    expected error  + model clean   -> MISS       (false negative)
    expected clean  + model flags   -> FALSE POS  (false positive)
    expected clean  + model clean   -> accepted   (true negative)

The goal is a single reviewable sheet (docs/master_sheet.md + .json) that stays
green until the model can identify the incorrect in every quiz.

Usage:
    python3 scripts/master_sheet.py                 # full run, write sheet
    python3 scripts/master_sheet.py --rule 9.1      # one rule
    python3 scripts/master_sheet.py --errors-only   # only print failures
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from server.parse_engine import analyze, ParseFailure  # noqa: E402
from server.matrix import evaluate  # noqa: E402

MASTER_PATH = os.path.join(ROOT, 'web', 'content', 'master.json')
OUT_MD = os.path.join(ROOT, 'docs', 'master_sheet.md')
OUT_JSON = os.path.join(ROOT, 'docs', 'master_sheet.json')


def load_questions():
    with open(MASTER_PATH, encoding='utf-8') as handle:
        return json.load(handle).get('questions', {})


def sentence_pairs(item):
    """Yield (bad, good) sentence pairs for one quiz item."""
    sents = item.get('sentences')
    if isinstance(sents, list) and sents:
        for s in sents:
            yield s.get('bad', ''), s.get('good', '')
    else:
        yield item.get('bad', ''), item.get('good', '')


def model_verdict(text):
    """Return (verdict, violations, checker_errors) for one sentence."""
    if not text:
        return ('empty', [], [])
    try:
        parsed = analyze(text, sentence_index=0)
    except ParseFailure as exc:
        return ('parse-failure', [str(exc)], [])
    except Exception as exc:  # noqa: BLE001
        return ('error', [], [f'{type(exc).__name__}: {exc}'])
    result = evaluate(parsed['root'], text=parsed['sentence'])
    summary = result['summary']
    return (summary.get('verdict'), summary.get('violations', []),
            summary.get('checker_errors', []))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rule', action='append', help='only this rule id (repeatable)')
    ap.add_argument('--errors-only', action='store_true', help='only print failures')
    ap.add_argument('--no-write', action='store_true', help='do not write the sheet')
    args = ap.parse_args()

    questions = load_questions()
    rule_ids = sorted(questions.keys(), key=lambda s: [int(x) for x in s.split('.')])
    if args.rule:
        wanted = set(args.rule)
        rule_ids = [r for r in rule_ids if r in wanted]

    cache = {}

    def check(text):
        if text not in cache:
            cache[text] = model_verdict(text)
        return cache[text]

    rows = []            # one dict per sentence
    rule_stats = {}      # rule_id -> counters
    for rid in rule_ids:
        stats = {'detected': 0, 'miss': 0, 'false_pos': 0, 'accepted': 0,
                 'items': 0, 'items_clean': 0}
        for qi, item in enumerate(questions.get(rid, [])):
            stats['items'] += 1
            item_ok = True
            for bad, good in sentence_pairs(item):
                if not bad and not good:
                    continue
                expected_error = bad != good
                verdict, violations, _errs = check(bad)
                flagged = verdict == 'ungrammatical'
                if expected_error and flagged:
                    status = 'detected'
                elif expected_error and not flagged:
                    status = 'miss'
                elif not expected_error and flagged:
                    status = 'false_pos'
                else:
                    status = 'accepted'
                stats[status] += 1
                if status in ('miss', 'false_pos'):
                    item_ok = False
                rows.append({
                    'rule': rid, 'item': qi, 'expected': 'error' if expected_error else 'correct',
                    'status': status, 'verdict': verdict, 'sentence': bad,
                    'good': good, 'violations': violations,
                })
            if item_ok:
                stats['items_clean'] += 1
        rule_stats[rid] = stats

    # ---- console summary ----
    tot = {'detected': 0, 'miss': 0, 'false_pos': 0, 'accepted': 0}
    for s in rule_stats.values():
        for k in tot:
            tot[k] += s[k]
    print(f"rules {len(rule_ids)}  sentences {sum(tot.values())}  "
          f"detected {tot['detected']}  MISS {tot['miss']}  "
          f"FALSE-POS {tot['false_pos']}  accepted {tot['accepted']}")

    bad_rules = [r for r, s in rule_stats.items() if s['miss'] or s['false_pos']]
    print(f"rules with gaps: {len(bad_rules)} -> {', '.join(bad_rules) if bad_rules else '(none)'}")
    for r in bad_rules:
        s = rule_stats[r]
        print(f"  {r}: miss {s['miss']}  false-pos {s['false_pos']}  "
              f"clean items {s['items_clean']}/{s['items']}")

    if args.errors_only:
        for row in rows:
            if row['status'] in ('miss', 'false_pos'):
                print(f"  [{row['status']}] {row['rule']}#{row['item']}  "
                      f"verdict={row['verdict']}  {row['sentence']!r}")

    if args.no_write:
        return

    # ---- markdown sheet ----
    lines = ['# SynTutor master sheet — model detection vs quiz', '',
             f"Rules: {len(rule_ids)} · Sentences: {sum(tot.values())} · "
             f"Detected: {tot['detected']} · Miss: {tot['miss']} · "
             f"False positives: {tot['false_pos']} · Accepted: {tot['accepted']}", '',
             '| status | rule | item | expected | verdict | sentence |',
             '| --- | --- | --- | --- | --- | --- |']
    order = {'miss': 0, 'false_pos': 1, 'detected': 2, 'accepted': 3}
    for row in sorted(rows, key=lambda r: (order[r['status']], r['rule'], r['item'])):
        if args.errors_only and row['status'] not in ('miss', 'false_pos'):
            continue
        sent = row['sentence'].replace('|', '\\|')
        lines.append(f"| {row['status']} | {row['rule']} | {row['item']} | "
                     f"{row['expected']} | {row['verdict']} | {sent} |")
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(lines) + '\n')
    with open(OUT_JSON, 'w', encoding='utf-8') as handle:
        json.dump({'summary': tot, 'rules': rule_stats, 'rows': rows},
                  handle, indent=2)
    print(f"wrote {os.path.relpath(OUT_MD, ROOT)} and {os.path.relpath(OUT_JSON, ROOT)}")


if __name__ == '__main__':
    main()
