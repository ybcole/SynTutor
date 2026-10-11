"""Thesis evaluation: does SynTutor accept ungrammatical input?

Input: a TSV with three columns  ``category <TAB> grammatical <TAB> ungrammatical``
(one minimal pair per line; '#' lines ignored).  Good sources for pairs:
BLiMP (Warstadt et al., 2020; already split by phenomenon: agreement, irregular
forms, island effects, ...), CoLA/JFLEG (learner-style errors), plus your own
hand-written pairs for the phenomena in docs/matrix.md.

Metrics per category, using the tri-state verdict from matrix.evaluate():

    miss rate        ungrammatical sentence got verdict 'grammatical'
                     (THE failure this work targets -- the false accept)
    flag rate        ungrammatical sentence got verdict 'ungrammatical'
    unverified rate  ungrammatical sentence got 'unverified' (not accepted, but
                     the system could not name the error)
    false reject     grammatical sentence got verdict 'ungrammatical'
    pair accuracy    good NOT rejected AND bad NOT accepted as grammatical

Usage:
    python eval_minimal_pairs.py pairs.tsv            # real pipeline (spaCy+benepar)
"""
import csv
import sys
from collections import defaultdict


def default_analyze(text):
    import parse_engine
    return parse_engine.analyze(text)['root']


def verdict_of(text, analyze_fn, use_detector=False):
    import matrix
    root = analyze_fn(text)
    summary = matrix.evaluate(root, text=text)['summary']
    if not use_detector:
        return summary['verdict'], None, None
    from detector import classify, combine
    det = classify(text)
    if det is None:
        return summary['verdict'], None, None
    final = combine(summary, det)
    return final['verdict'], summary['verdict'], det


def evaluate_pairs(pairs, analyze_fn=default_analyze, use_detector=False):
    """pairs: iterable of (category, good, bad).  Returns {category: metrics}."""
    stats = defaultdict(lambda: defaultdict(int))
    for cat, good, bad in pairs:
        gv, gr, gd = verdict_of(good, analyze_fn, use_detector)
        bv, br, bd = verdict_of(bad, analyze_fn, use_detector)
        for key in (cat, 'ALL'):
            s = stats[key]
            s['n'] += 1
            s['bad_missed'] += bv == 'grammatical'
            s['bad_flagged'] += bv == 'ungrammatical'
            s['bad_unverified'] += bv == 'unverified'
            s['good_rejected'] += gv == 'ungrammatical'
            s['pair_ok'] += (gv != 'ungrammatical') and (bv != 'grammatical')
            if use_detector:
                s['bad_rules_flagged'] += br == 'ungrammatical'
                s['bad_model_flagged'] += (bd is not None and not bd['acceptable'])
                s['good_model_accepted'] += (gd is not None and gd['acceptable'])
                # agreement: both channels decide the same way on a 'bad' input
                s['bad_both_flagged'] += (
                    br == 'ungrammatical' and bd is not None
                    and not bd['acceptable'])
    return stats


def report(stats, use_detector=False):
    print(f"{'category':<24}{'n':>5}{'miss%':>8}{'flag%':>8}{'unver%':>8}"
          f"{'falseRej%':>11}{'pairAcc%':>10}")
    for cat in sorted(stats, key=lambda c: (c == 'ALL', c)):
        s, n = stats[cat], stats[cat]['n']
        pct = lambda k: 100.0 * s[k] / n
        print(f"{cat:<24}{n:>5}{pct('bad_missed'):>8.1f}{pct('bad_flagged'):>8.1f}"
              f"{pct('bad_unverified'):>8.1f}{pct('good_rejected'):>11.1f}"
              f"{pct('pair_ok'):>10.1f}")
    if use_detector:
        s, n = stats['ALL'], stats['ALL']['n']
        rules = pct('bad_rules_flagged')
        model = pct('bad_model_flagged')
        both = pct('bad_both_flagged')
        model_only = model - both
        g_ok = pct('good_model_accepted')
        print(f"\n  hybrid channel breakdown (ALL, n={n}):")
        print(f"    bad flagged by RULES : {rules:.1f}%")
        print(f"    bad flagged by MODEL : {model:.1f}%   (rules+model: {both:.1f}%, "
              f"model-only: {model_only:.1f}%)")
        print(f"    good accepted by MODEL: {g_ok:.1f}%")


def read_pairs(path):
    with open(path, newline='', encoding='utf-8') as fh:
        for n, row in enumerate(csv.reader(fh, delimiter='\t')):
            if len(row) != 3 or row[0].startswith('#'):
                continue
            if n == 0 and row[0].strip().lower() in ('category', 'cat', 'phenomenon'):
                continue
            yield row[0], row[1].strip(), row[2].strip()


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--detector']
    if len(args) != 1 or sys.argv[1] in ('-h', '--help'):
        sys.exit(f"{__doc__}\n    python eval_minimal_pairs.py [--detector] pairs.tsv")
    use_detector = '--detector' in sys.argv[1:]
    report(evaluate_pairs(read_pairs(args[0]), use_detector=use_detector),
           use_detector=use_detector)
