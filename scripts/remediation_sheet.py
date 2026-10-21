"""SynTutor remediation sheet: review every *how to fix* / *alternative fix*.

The explanation sheet (``scripts/explanation_sheet.py``) reviews the wording of
correct explanations. This sheet reviews the other half of the feedback the
learner sees on an error node:

    What's wrong      -> ``violation``
    How to fix it     -> ``suggested_fix``
    Alternative fix   -> ``alternative_fix``

For every quiz sentence we run the real model (spaCy + benepar parse ->
deterministic constraint matrix), collect each error node's remediation card,
and group the cards by constraint. Cards are deduplicated by a normalised
template (quoted material replaced with ``{X}``) so the sheet stays compact:

    ## C-HEAD-VERB  (1 cards, 12 errors)
    | what's wrong | how to fix it | alternative fix | count | example |

A card is flagged when its *How to fix it* does not name a concrete corrected
form (no quoted replacement at all, or one of the known vague phrasings), so a
reviewer can see every place the fix is still indirect.

Usage:
    python3 scripts/remediation_sheet.py                # full run, write sheet
    python3 scripts/remediation_sheet.py --rule 6.4     # one rule
    python3 scripts/remediation_sheet.py --no-write
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
OUT_MD = os.path.join(ROOT, 'docs', 'remediation_sheet.md')
OUT_JSON = os.path.join(ROOT, 'docs', 'remediation_sheet.json')

_QUOTED = re.compile(r"'[^']*'")
_VAGUE = re.compile(
    r"(the word form the sentence needs|you really mean|this sentence really needs|"
    r"fix the highlighted issue|use the verb you|the action verb this sentence|"
    r"to the correct form|to the right form|the form the sentence needs)",
    re.I)


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
    return _QUOTED.sub("'{X}'", text or '')


def remediation_cards(text):
    """Return [(key, role, card)] for every error remediation in the sentence."""
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
        rem = detail.get('remediation')
        if detail.get('status') == 'error' and isinstance(rem, dict) and rem.get('violation'):
            out.append((detail.get('constraint', '?'), detail.get('role', ''), rem))
        for finding in detail.get('findings', []) or []:
            frem = finding.get('remediation')
            if isinstance(frem, dict) and frem.get('violation'):
                key = finding.get('constraint') or f"R{finding.get('rule_id', '?')}"
                out.append((key, finding.get('role', ''), frem))
    return out


def is_vague(fix):
    return bool(_VAGUE.search(fix)) or not _QUOTED.search(fix)


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

    # constraint -> (what, fix, alt) -> {'count', 'example', 'role'}
    groups = {}
    seen_sentences = set()
    total = 0
    for rid in rule_ids:
        for item in questions.get(rid, []):
            for bad, _good in sentence_pairs(item):
                if not bad or bad in seen_sentences:
                    continue
                seen_sentences.add(bad)
                for key, role, card in remediation_cards(bad):
                    total += 1
                    tmpl = (normalise(card.get('violation')),
                            normalise(card.get('suggested_fix')),
                            normalise(card.get('alternative_fix')))
                    bucket = groups.setdefault(key, {})
                    entry = bucket.get(tmpl)
                    if entry is None:
                        bucket[tmpl] = {'count': 1, 'example': bad, 'role': role,
                                        'fix': card.get('suggested_fix') or ''}
                    else:
                        entry['count'] += 1

    print(f"sentences {len(seen_sentences)}  constraints {len(groups)}  cards {total}")
    flagged = []
    for key, bucket in sorted(groups.items()):
        for tmpl, entry in bucket.items():
            if is_vague(tmpl[1] or ''):
                flagged.append((key, tmpl, entry['example']))
    print(f"templates: {sum(len(b) for b in groups.values())}  "
          f"vague fixes: {len(flagged)}")
    for key, tmpl, example in flagged:
        print(f"  [vague] {key}: {tmpl[1]!r}  <= {example!r}")

    if args.no_write:
        return

    lines = ['# SynTutor remediation sheet — how to fix / alternative fix', '',
             f"Sentences: {len(seen_sentences)} · Constraints: {len(groups)} · "
             f"Cards: {total} · Templates: {sum(len(b) for b in groups.values())} · "
             f"Vague fixes: {len(flagged)}", '',
             'Each row is a template with quoted material replaced by `{X}`; one real '
             'example sentence is shown per row. The **how to fix it** column must name '
             'the corrected form directly.', '']
    for key in sorted(groups):
        bucket = groups[key]
        n = sum(e['count'] for e in bucket.values())
        lines.append(f"## {key}  ({len(bucket)} templates, {n} cards)")
        lines.append('')
        lines.append("| what's wrong | how to fix it | alternative fix | count | example |")
        lines.append('| --- | --- | --- | --- | --- |')
        for tmpl, entry in sorted(bucket.items(), key=lambda kv: -kv[1]['count']):
            what = tmpl[0].replace('|', '\\|')
            fix = (tmpl[1] or '—').replace('|', '\\|')
            alt = (tmpl[2] or '—').replace('|', '\\|')
            ex = entry['example'].replace('|', '\\|')
            lines.append(f"| {what} | {fix} | {alt} | {entry['count']} | {ex} |")
        lines.append('')
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(lines) + '\n')
    with open(OUT_JSON, 'w', encoding='utf-8') as handle:
        plain = {key: {f"{t[0]} || {t[1]} || {t[2]}": e for t, e in bucket.items()}
                 for key, bucket in groups.items()}
        json.dump({'constraints': plain,
                   'summary': {'sentences': len(seen_sentences),
                               'constraints': len(groups),
                               'cards': total,
                               'vague_fixes': len(flagged)}},
                  handle, indent=2)
    print(f"wrote {os.path.relpath(OUT_MD, ROOT)} and "
          f"{os.path.relpath(OUT_JSON, ROOT)}")


if __name__ == '__main__':
    main()
