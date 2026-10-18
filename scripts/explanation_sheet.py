"""SynTutor explanation sheet: review every *valid* (correct) explanation.

The detection master sheet (``scripts/master_sheet.py``) checks whether the
model finds the intended error. This sheet checks the other half: when the
model judges a node *correct*, the explanation it shows must make sense and
must refer to the actual sentence (like the explanations for errors do).

For every quiz sentence we run the real model (spaCy + benepar parse ->
deterministic constraint matrix), collect each ``valid`` node explanation,
and group them by constraint. Explanations are deduplicated by a normalised
template (quoted material replaced with ``{X}``) so the sheet stays compact:

    == C-INFINITIVAL-MARKER  (3 templates, 185 explanations)
        "'{X}' introduces the infinitive phrase '{X}'."   e.g. 'To eat is fun.'

An explanation is flagged when it does not quote any part of the sentence.

Usage:
    python3 scripts/explanation_sheet.py                 # full run, write sheet
    python3 scripts/explanation_sheet.py --rule 9.1      # one rule
    python3 scripts/explanation_sheet.py --no-write
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from server.parse_engine import analyze, ParseFailure  # noqa: E402
from server.matrix import evaluate  # noqa: E402

MASTER_PATH = os.path.join(ROOT, 'web', 'content', 'master.json')
OUT_MD = os.path.join(ROOT, 'docs', 'explanation_sheet.md')
OUT_JSON = os.path.join(ROOT, 'docs', 'explanation_sheet.json')

_QUOTED = re.compile(r"'[^']*'")


def load_questions():
    with open(MASTER_PATH, encoding='utf-8') as handle:
        return json.load(handle).get('questions', {})


def sentence_pairs(item):
    sents = item.get('sentences')
    if isinstance(sents, list) and sents:
        for s in sents:
            yield s.get('bad', ''), s.get('good', '')
    else:
        yield item.get('bad', ''), item.get('good', '')


def normalise(text):
    """Replace quoted material with a placeholder so like templates group."""
    return _QUOTED.sub("'{X}'", text)


def valid_explanations(text):
    """Return [(constraint, explanation)] for every correct node."""
    if not text:
        return []
    try:
        parsed = analyze(text, sentence_index=0)
    except ParseFailure:
        return []
    except Exception:  # noqa: BLE001
        return []
    result = evaluate(parsed['root'], text=parsed['sentence'])
    out = []
    for detail in result.get('details', {}).values():
        if detail.get('status') == 'valid' and detail.get('text'):
            out.append((detail.get('constraint', '?'), detail['text']))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rule', action='append', help='only this rule id (repeatable)')
    ap.add_argument('--no-write', action='store_true', help='do not write the sheet')
    args = ap.parse_args()

    questions = load_questions()
    rule_ids = sorted(questions.keys(), key=lambda s: [int(x) for x in s.split('.')])
    if args.rule:
        wanted = set(args.rule)
        rule_ids = [r for r in rule_ids if r in wanted]

    # constraint -> normalised template -> {'count', 'example', 'text'}
    groups = {}
    seen_sentences = set()
    total = 0
    for rid in rule_ids:
        for item in questions.get(rid, []):
            for bad, _good in sentence_pairs(item):
                if not bad or bad in seen_sentences:
                    continue
                seen_sentences.add(bad)
                for constraint, explanation in valid_explanations(bad):
                    total += 1
                    tmpl = normalise(explanation)
                    bucket = groups.setdefault(constraint, {})
                    entry = bucket.get(tmpl)
                    if entry is None:
                        bucket[tmpl] = {'count': 1, 'example': bad,
                                        'text': explanation}
                    else:
                        entry['count'] += 1

    # ---- console summary ----
    print(f"sentences {len(seen_sentences)}  constraints {len(groups)}  "
          f"explanations {total}")
    flagged = []
    for constraint, bucket in sorted(groups.items()):
        for tmpl, entry in bucket.items():
            if not _QUOTED.search(entry['text']):
                flagged.append((constraint, tmpl, entry['example']))
    print(f"templates: {sum(len(b) for b in groups.values())}  "
          f"without a quoted reference: {len(flagged)}")
    for constraint, tmpl, example in flagged[:20]:
        print(f"  [no-ref] {constraint}: {tmpl!r}  <= {example!r}")

    if args.no_write:
        return

    # ---- markdown sheet ----
    lines = ['# SynTutor explanation sheet — correct (valid) explanations', '',
             f"Sentences: {len(seen_sentences)} · Constraints: {len(groups)} · "
             f"Explanations: {total} · Templates: "
             f"{sum(len(b) for b in groups.values())} · Without a quoted reference: "
             f"{len(flagged)}", '',
             'Each explanation below is a template with quoted material replaced by '
             '`{X}`; one real example sentence is shown per template.', '']
    for constraint in sorted(groups):
        bucket = groups[constraint]
        n = sum(e['count'] for e in bucket.values())
        lines.append(f"## {constraint}  ({len(bucket)} templates, {n} explanations)")
        lines.append('')
        lines.append('| template | count | example |')
        lines.append('| --- | --- | --- |')
        for tmpl, entry in sorted(bucket.items(), key=lambda kv: -kv[1]['count']):
            t = (entry['text']).replace('|', '\\|')
            ex = entry['example'].replace('|', '\\|')
            lines.append(f"| {t} | {entry['count']} | {ex} |")
        lines.append('')
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(lines) + '\n')
    with open(OUT_JSON, 'w', encoding='utf-8') as handle:
        json.dump({'constraints': groups,
                   'summary': {'sentences': len(seen_sentences),
                               'constraints': len(groups),
                               'explanations': total,
                               'without_reference': len(flagged)}},
                  handle, indent=2)
    print(f"wrote {os.path.relpath(OUT_MD, ROOT)} and {os.path.relpath(OUT_JSON, ROOT)}")


if __name__ == '__main__':
    main()
